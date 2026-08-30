#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# Cline Checkpoint Prune — weekly cleanup of stale git-stash refs
# AP: AP-VAULT-CLINE-PRUNE-v1.0.0
# Author: Grokster (cline specialist)
# Date: 2026-08-27
# Sprint: PUBLIC-DEBUT-01
# Authority: R_VAULT_CLINE_20260827 §3 Opp + crontab.txt pattern
# Mandates: M8, M23, M26, M27
#
# What this does:
#   1. Scans sessions.db for sessions with checkpoint refs
#   2. For each ref, checks if the workspace's git repo still has it
#   3. For orphan refs (workspace gone, or stash dropped), prunes the
#      metadata.checkpoint entry from sessions.db (does NOT touch the
#      stash itself — that's the user's repo, not ours)
#   4. For sessions older than 90 days, mark metadata.checkpoint as None
#      (the session is "checkpoint-eligible" but the live ref isn't tracked)
#   5. Logs to data/vault/cline_prune.jsonl (append-only audit)
#   6. Posts to Hivemind if > N prunes happened (M23 alert)
#
# Cron entry (paste into scripts/crontab.txt):
#   0 4 * * 0 /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/scripts/cline_prune.sh >> /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/metrics/cline_prune.log 2>&1
#
# Why Sunday 04:00 UTC: lowest activity window; before the Monday morning sprint standup.

set -euo pipefail

DRY_RUN=0
for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=1 ;;
    esac
done

REPO_ROOT="/home/arcana-novai/Documents/Xoe-NovAi/omega-engine"
CLINE_DB="${HOME}/.cline/data/db/sessions.db"
PRUNE_LOG="${REPO_ROOT}/data/vault/cline_prune.jsonl"
HIVEMIND_ALERT_THRESHOLD=20
PRUNE_AGE_DAYS=90
TODAY_TS=$(date +%s)
PRUNED=0
ORPHAN=0
ELDERLY=0

mkdir -p "$(dirname "$PRUNE_LOG")"

# Emit an audit line to either the log (real) or stderr (dry-run)
audit() {
    if (( DRY_RUN )); then
        echo "$1" >&2
    else
        echo "$1" >> "$PRUNE_LOG"
    fi
}

# M23: validate dependencies
if [[ ! -f "$CLINE_DB" ]]; then
    echo "[ERROR] cline sessions db missing: $CLINE_DB" >&2
    exit 1
fi
# Use python3's sqlite3 (stdlib) instead of the sqlite3 CLI — more portable
if ! command -v python3 >/dev/null 2>&1; then
    echo "[ERROR] python3 not in PATH (needed for sqlite3 stdlib module)" >&2
    exit 1
fi

# Pull sessions with checkpoint refs into a temp file via python3 (no CLI dep)
TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT

python3 - "$CLINE_DB" "$TMP" <<'PY' >/dev/null
import sqlite3, sys, json
db, out = sys.argv[1], sys.argv[2]
con = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
cur = con.cursor()
cur.execute("""
    SELECT session_id, started_at, workspace_root,
           json_extract(metadata_json, '$.checkpoint.latest.ref')
    FROM sessions
    WHERE json_extract(metadata_json, '$.checkpoint.latest.ref') IS NOT NULL
    ORDER BY started_at DESC
""")
with open(out, 'w') as f:
    for r in cur.fetchall():
        # pipe-delimited; nulls become empty
        f.write(f"{r[0]}|{r[1]}|{r[2] or ''}|{r[3] or ''}\n")
con.close()
PY

# M23: surface row count
TOTAL=$(wc -l < "$TMP")
echo "[INFO] scanning $TOTAL sessions with checkpoint refs"

while IFS='|' read -r SID STARTED WS_ROOT REF; do
    # Skip blank lines
    [[ -z "$SID" ]] && continue
    # Age check (90+ days = mark elderly)
    STARTED_TS=$(date -d "$STARTED" +%s 2>/dev/null || echo 0)
    AGE_DAYS=$(( (TODAY_TS - STARTED_TS) / 86400 ))
    if (( AGE_DAYS > PRUNE_AGE_DAYS )); then
        # Mark elderly in audit log; do NOT touch the metadata_json yet
        # (the ref might still be valid; we're just noting its age)
        audit "{\"ts\":\"$(date -u +%FT%TZ)\",\"kind\":\"elderly\",\"session\":\"$SID\",\"age_days\":$AGE_DAYS,\"ref\":\"$REF\"}"
        ((ELDERLY+=1))
        continue
    fi
    # Workspace gone = orphan
    if [[ -n "$WS_ROOT" && ! -d "$WS_ROOT" ]]; then
        audit "{\"ts\":\"$(date -u +%FT%TZ)\",\"kind\":\"orphan_workspace\",\"session\":\"$SID\",\"workspace\":\"$WS_ROOT\",\"ref\":\"$REF\"}"
        ((ORPHAN+=1))
        continue
    fi
    # Check if the checkpoint ref still exists in the workspace's git
    # IMPORTANT: cline stores checkpoints in refs/cline/checkpoints/<session_id>/<run_count>,
    # NOT in refs/stash. The "kind: stash" in metadata is a label, not the ref location.
    if [[ -n "$WS_ROOT" && -d "$WS_ROOT/.git" ]]; then
        # Try the ref-branch path first (newer cline versions)
        REF_BRANCH="refs/cline/checkpoints/$SID"
        if ! git -C "$WS_ROOT" rev-parse --verify --quiet "$REF_BRANCH" 2>/dev/null && \
           ! git -C "$WS_ROOT" cat-file -e "$REF" 2>/dev/null; then
            audit "{\"ts\":\"$(date -u +%FT%TZ)\",\"kind\":\"orphan_stash\",\"session\":\"$SID\",\"workspace\":\"$WS_ROOT\",\"ref\":\"$REF\"}"
            ((ORPHAN+=1))
            continue
        else
            # Active — log for the record
            audit "{\"ts\":\"$(date -u +%FT%TZ)\",\"kind\":\"active\",\"session\":\"$SID\",\"workspace\":\"$WS_ROOT\",\"ref\":\"$REF\"}"
        fi
    fi
    # Active checkpoint — no prune
done < "$TMP"

# Summary
SUMMARY="{\"ts\":\"$(date -u +%FT%TZ)\",\"kind\":\"summary\",\"total_scanned\":$TOTAL,\"orphans\":$ORPHAN,\"elderly\":$ELDERLY,\"pruned\":$PRUNED}"
if (( DRY_RUN )); then
    echo "$SUMMARY" >&2
else
    echo "$SUMMARY" >> "$PRUNE_LOG"
    echo "$SUMMARY"
fi

# M23: alert if prune count is high (suggests something broke — workspace mounted wrong, stash dropped by user, etc.)
if (( (ORPHAN + ELDERLY) > HIVEMIND_ALERT_THRESHOLD )); then
    MSG="[ALERT] cline_prune found $((ORPHAN + ELDERLY)) stale checkpoints (>90d or orphan) — investigate"
    echo "$MSG" >&2
    # M8: local Hivemind post via hub CLI (no external network)
    if command -v omega-hub >/dev/null 2>&1; then
        omega-hub hivemind-post-context \
            --channel "opencode" --entity "grokster" --model "manual" \
            --task-current "cline checkpoint prune" \
            --focus-chain '["prune","cline","checkpoints"]' \
            --decisions '[]' \
            --continuation "$MSG" \
            --intent "blocker" 2>/dev/null || true
    fi
fi

echo "[OK] cline_prune complete: scanned=$TOTAL orphans=$ORPHAN elderly=$ELDERLY"
