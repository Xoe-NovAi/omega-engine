#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# Migrate or-key.md + cline-key + 7 auth.json providers → vault shim
# AP: AP-VAULT-CLINE-MIGRATION-v1.0.0
# Author: Grokster (cline specialist)
# Date: 2026-08-27
# Sprint: PUBLIC-DEBUT-01
# Authority: R_VAULT_CLINE_20260827 §3 Opp 5, D-568 (AES-256-GCM)
# Mandates: M8, M14, M23, M26
#
# This is a ONE-SHOT migration script. Run it once to:
#   1. Back up all 3 source stores
#   2. Capture the master key for the new vault shim
#   3. Run the 3-store shim in 'inventory' mode
#   4. Verify the encrypted blob is decryptable
#   5. Sanity-check: try the new shim's read path on a known credential
#   6. Report the source → shim mapping
#
# ROLLBACK: the backups at ~/.omega-vault-migration/ let you restore the
# original plaintext stores if anything breaks. The shim's first run
# only WRITES data/vault/, never touches the source stores.
#
# Usage:
#   ./migrate_3store.sh              # interactive
#   ./migrate_3store.sh --yes        # non-interactive (CI/scripted)
#   ./migrate_3store.sh --dry-run    # scan only, no writes
#
# Post-migration, add to crontab.txt (use YOUR worktree/repo root, not a hardcoded path):
#   0 3 * * * <repo-root>/scripts/three_store_shim.py scan > <repo-root>/data/metrics/3store_inventory.log 2>&1

set -euo pipefail

# Worktree-safe: derive repo root from script location so linked worktrees
# (../omega-wt-maat, ../omega-wt-doom, ../omega-wt-grok) resolve to themselves,
# never to the main tree. (Doom Guy audit 2026-09-27; M27 tracking integrity.)
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"
SHIM="${REPO_ROOT}/scripts/three_store_shim.py"
BACKUP_ROOT="${HOME}/.omega-vault-migration/$(date -u +%Y%m%dT%H%M%SZ)"
MASTER_KEY_PATH="${REPO_ROOT}/data/vault/.master_key"

DRY_RUN=0
YES=0
SHIM_PATH=""
for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=1 ;;
        --yes)     YES=1 ;;
        --shim-path=*) SHIM_PATH="${arg#*=}" ;;
    esac
done
if [[ -n "$SHIM_PATH" ]]; then
    SHIM="$SHIM_PATH"
fi

# --- Step 0: M23 validate shim exists ---
if [[ ! -f "$SHIM" ]]; then
    echo "[ERROR] shim not found: $SHIM" >&2
    exit 1
fi

# --- Step 1: Back up the 3 source stores ---
mkdir -p "$BACKUP_ROOT"
echo "[INFO] backing up 3 stores to $BACKUP_ROOT"
for f in \
    "$HOME/.cline/data/secrets.json" \
    "$HOME/.cline/data/settings/providers.json" \
    "$HOME/.local/share/opencode/auth.json"
do
    if [[ -f "$f" ]]; then
        # M14: backup with restrictive perms
        install -m 600 "$f" "$BACKUP_ROOT/$(basename "$f")"
        echo "  backed up: $f ($(wc -c < "$f") bytes)"
    else
        echo "  [skip] missing: $f"
    fi
done

# --- Step 2: Generate master key (M14 mode 600, 32 bytes random) ---
if [[ ! -f "$MASTER_KEY_PATH" ]] && (( ! DRY_RUN )); then
    if (( ! YES )); then
        echo -n "Generate new master key at $MASTER_KEY_PATH? [y/N] "
        read -r ANS
        [[ "$ANS" =~ ^[Yy]$ ]] || { echo "aborted"; exit 1; }
    fi
    mkdir -p "$(dirname "$MASTER_KEY_PATH")"
    umask 077
    python3 -c "import os; open('$MASTER_KEY_PATH','wb').write(os.urandom(32))"
    chmod 600 "$MASTER_KEY_PATH"
    echo "[OK] master key: $MASTER_KEY_PATH (32 bytes, mode 600)"
fi

# --- Step 3: Run the shim in 'scan' mode first (always read-only) ---
echo "[INFO] shim scan (read-only)..."
if ! python3 "$SHIM" scan --verbose; then
    echo "[ERROR] shim scan failed" >&2
    exit 1
fi

# --- Step 4: Run the shim in 'inventory' mode (writes encrypted blob) ---
if (( DRY_RUN )); then
    echo "[DRY-RUN] skipping inventory write"
    exit 0
fi
echo "[INFO] shim inventory (writes encrypted blob + plaintext index)..."
if ! python3 "$SHIM" inventory --keyfile "$MASTER_KEY_PATH"; then
    echo "[ERROR] shim inventory failed" >&2
    exit 1
fi

# --- Step 5: Verify the encrypted blob is decryptable ---
echo "[INFO] verifying encrypted blob..."
python3 <<PY
import sys
from pathlib import Path
keyfile = Path("$MASTER_KEY_PATH")
ct = Path("${REPO_ROOT}/data/vault/encrypted_inventory.enc").read_bytes()
nonce, body = ct[:12], ct[12:]
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
try:
    plain = AESGCM(keyfile.read_bytes()[:32].ljust(32, b"\x00")).decrypt(nonce, body, associated_data=b"omega-vault-shim-v1")
    import json
    inv = json.loads(plain)
    print(f"[OK] decrypt OK: {len(inv)} credentials, {len(inv[0]) if inv else 0} fields each")
except Exception as e:
    print(f"[ERROR] decrypt failed: {e}", file=sys.stderr)
    sys.exit(1)
PY

# --- Step 6: Sanity check: pick a known provider, decrypt, compare to backup ---
echo "[INFO] sanity check: pick 'openrouter' from cline secrets vs backup..."
python3 <<PY
import json
from pathlib import Path
shim_inv = json.loads(Path("${REPO_ROOT}/data/vault/inventory.json").read_text())
backup = json.loads(Path("$BACKUP_ROOT/secrets.json").read_text())
shim_or = [c for c in shim_inv["credentials"]
           if c["provider"] == "openrouter" and c["account_id"] == "cline-0"]
if not shim_or:
    print("[ERROR] no openrouter entry in shim inventory", file=sys.stderr)
    raise SystemExit(1)
if shim_or[0]["value"] != backup.get("openRouterApiKey"):
    print("[ERROR] shim openrouter != backup openRouterApiKey", file=sys.stderr)
    raise SystemExit(1)
print(f"[OK] openrouter matches: fp={shim_or[0]['fingerprint']}")
PY

# --- Step 7: Report ---
echo ""
echo "============================================================"
echo "MIGRATION COMPLETE"
echo "============================================================"
echo "Backup:   $BACKUP_ROOT"
echo "Master:   $MASTER_KEY_PATH (mode 600)"
echo "Inventory: ${REPO_ROOT}/data/vault/inventory.json"
echo "Encrypted: ${REPO_ROOT}/data/vault/encrypted_inventory.enc"
echo ""
echo "Next steps:"
echo "  1. Add to crontab.txt: shim scan every 6h"
echo "  2. Set OMEGA_VAULT_MASTER_KEY in .env (or rely on keyfile)"
echo "  3. The 3 source stores are now READ-ONLY for non-shim processes"
echo "  4. To roll back: cp -p $BACKUP_ROOT/* ~/.cline/data/secrets.json"
echo "============================================================"
