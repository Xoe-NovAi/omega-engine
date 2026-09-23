#!/bin/bash
# opencode_provider_doctor.sh — diagnose + safely repair OpenCode provider setups.
# SPDX-License-Identifier: MIT (see repo LICENSE)
#
# Doctrine (every rule below was paid for in production — see
# docs/research/KNOWLEDGE_GAPS_IMPLEMENTATION_GUIDE.md §11):
#  1. Built-in providers need ZERO config. Zen (opencode), OpenRouter and the
#     models.dev registry ship 100+ models with correct wiring. If you are
#     enumerating models in config, you are fighting the registry — and Zen
#     ROTATES free models/limits without notice (Big Pickle 1M→200K, Sept 2026).
#  2. Config layers MERGE (global < OPENCODE_CONFIG < project), custom models
#     are ADDITIVE. A partial `models` map does not drop built-ins (proven live).
#  3. Check every sibling file: opencode.json AND opencode.jsonc, global AND
#     project (project root = cwd up to git dir). Phantoms live in siblings.
#  4. Auth lives at $XDG_DATA_HOME/opencode/auth.json (NOT ~/.config).
#     Prefer `opencode auth login`; never paste keys into config files.
#  5. Dead hostnames kill providers before keys matter: api.openrouter.ai is
#     NXDOMAIN globally (apex openrouter.ai/api/v1 is correct); the common
#     mistake https://api.opencode.ai/v1 is wrong (Zen uses /zen/v1 paths).
#  6. Subtractive repair only: the tool strips provably-dead weight (empty
#     `options: {}`) with backups. It NEVER inscribes model lists or limits.
#
# Usage: bash opencode_provider_doctor.sh [--apply] [--project DIR] [--home DIR]
#        [--report FILE]
#   Default is DRY-RUN (report only). --apply writes backups (*.bak.TIMESTAMP)
#   then strips empty options objects. Exit: 0 clean, 1 warnings, 2 failures.
#   Secrets are never printed or written: shapes only (len + head4).
set -u
HOME_DIR="$HOME"; PROJECT=""; APPLY=0; REPORT=""; SANDBOX=0
while [[ $# -gt 0 ]]; do case "$1" in
  --apply) APPLY=1; shift ;;
  --project) PROJECT="$2"; shift 2 ;;
  --home) HOME_DIR="$2"; SANDBOX=1; shift 2 ;;
  --report) REPORT="$2"; shift 2 ;;
  *) echo "unknown arg: $1" >&2; exit 2 ;;
esac; done

CONF_DIR="${XDG_CONFIG_HOME:-$HOME_DIR/.config}/opencode"
DATA_DIR="${XDG_DATA_HOME:-$HOME_DIR/.local/share}/opencode"
# --home means sandbox: pin XDG so child processes (opencode, python) agree.
if [[ "$SANDBOX" == "1" ]]; then
  export XDG_CONFIG_HOME="$HOME_DIR/.config" XDG_DATA_HOME="$HOME_DIR/.local/share"
  CONF_DIR="$HOME_DIR/.config/opencode"; DATA_DIR="$HOME_DIR/.local/share/opencode"
fi
export NO_COLOR=1
LOG="$(mktemp)"
exec > >(tee "$LOG") 2>&1
if [[ -z "$PROJECT" ]]; then
  d="$PWD"; while [[ "$d" != "/" && ! -d "$d/.git" ]]; do d="$(dirname "$d")"; done
  [[ -d "$d/.git" ]] && PROJECT="$d"
fi
have() { command -v "$1" > /dev/null 2>&1; }
PASS=0; WARN=0; FAIL=0
say()  { printf "[%s] %s\n" "$1" "$2"; }
ok()   { PASS=$((PASS+1)); say "PASS" "$1"; }
warn() { WARN=$((WARN+1)); say "WARN" "$1"; }
fail() { FAIL=$((FAIL+1)); say "FAIL" "$1"; }
[[ -n "$REPORT" ]] && exec > >(tee "$REPORT") 2>&1

echo "=== opencode provider doctor — $(date -u +%FT%TZ) ==="
echo "home=$HOME_DIR project=${PROJECT:-<none>} apply=$APPLY"

# ── C1 version ───────────────────────────────────────────────────────
if have opencode; then
  if [[ "$SANDBOX" == "1" ]]; then
    echo "[PASS] sandbox version probe skipped (fixture is hermetic)"
  else
    VER="$(opencode --version 2>/dev/null | head -1)"
    echo "opencode: $VER"
    if [[ "$VER" =~ 1\.18\.([0-9]+) ]] && [[ "${BASH_REMATCH[1]}" -lt 30 ]]; then
      warn "opencode < 1.18.30: OpenAI provider SDK compatibility fixes landed in .30 — consider 'opencode upgrade' for parity (not a diagnosis)"
    else ok "opencode version recorded ($VER)"; fi
  fi
else fail "opencode binary not found on PATH"; fi

# ── C2 config layers ─────────────────────────────────────────────────
echo "--- layers ---"
FILES=()
for f in "$CONF_DIR/opencode.json" "$CONF_DIR/opencode.jsonc" \
         "${OPENCODE_CONFIG:-/nonexistent-openconfig}" \
         ${PROJECT:+"$PROJECT/opencode.json" "$PROJECT/opencode.jsonc"}; do
  if [[ -f "$f" ]]; then echo "present: $f"; FILES+=("$f"); else echo "absent:  $f"; fi
done
[[ -f "$CONF_DIR/opencode.jsonc" ]] && warn "opencode.jsonc present — check it for stale entries shadowing opencode.json (merge order bites)"
[[ -n "${OPENCODE_CONFIG:-}" ]] && warn "OPENCODE_CONFIG override active: $OPENCODE_CONFIG (invisible to naive inspection)"
[[ -d "$CONF_DIR/plugins" ]] && { echo "global plugins: $(ls "$CONF_DIR/plugins" | tr '\n' ' ')"; }
[[ -n "$PROJECT" && -d "$PROJECT/.opencode/plugins" ]] && { echo "project plugins: $(ls "$PROJECT/.opencode/plugins" | tr '\n' ' ')"; warn "project plugins load — a provider-hooking plugin (e.g. *-auth) can rewrite requests"; }

# ── C3 provider audit per file ───────────────────────────────────────
export APPLY
for F in "${FILES[@]}"; do
  [[ "$F" == *.jsonc ]] && { warn "skipping deep audit of jsonc (comments break strict parsers): $F"; continue; }
  export AUDIT_FILE="$F"
  python3 - "$F" <<'PYEOF'
import json, os, re, socket
f = os.environ["AUDIT_FILE"]
try: cfg = json.load(open(f))
except Exception as e: print(f"[FAIL] strict-JSON parse: {f}: {e}"); raise SystemExit(2)
prov = cfg.get("provider", {}) or {}
if not prov: print(f"[PASS] no provider blocks: {f} (built-ins rule)"); raise SystemExit
for pid, pdef in prov.items():
    if not isinstance(pdef, dict): print(f"[WARN] {f} provider.{pid} not an object"); continue
    opts = pdef.get("options", "<ABSENT>")
    if opts == {}:
        print(f"[FAIL] {f} provider.{pid}.options is empty object (pure risk, zero function)")
        if os.environ["APPLY"] == "1":
            bak = f + ".bak." + __import__("datetime").datetime.now().strftime("%Y%m%dT%H%M%S")
            open(bak, "w").write(open(f).read())
            del pdef["options"]
            json.dump(cfg, open(f, "w"), indent=2)
            print(f"[PASS] REPAIRED {f} (backup {bak})")
    # baseURL liveness (DNS only — cheap, no quota)
    bu = (pdef.get("options") or {}).get("baseURL", "")
    if bu:
        host = re.sub(r"^https?://", "", bu).split("/")[0].split(":")[0]
        try: socket.getaddrinfo(host, 443); print(f"[PASS] {f} {pid}.baseURL resolves: {host}")
        except Exception:
            print(f"[FAIL] {f} {pid}.baseURL NXDOMAIN/unresolvable: {host}")
            if host == "api.openrouter.ai": print("  NOTE api.openrouter.ai is dead globally — use https://openrouter.ai/api/v1")
            if host == "api.opencode.ai": print("  NOTE api.opencode.ai/v1 is a documented mistake — Zen uses https://opencode.ai/zen/v1 paths")
    # embedded secrets + placeholders (patterns only, values never printed)
    blob = json.dumps(pdef)
    if re.search(r"sk-(or|ant)-[A-Za-z0-9_.\-]{20,}|ctx7sk-\S{20,}|fc-[a-f0-9]{30,}|ghp_\S{20,}", blob):
        print(f"[FAIL] {f} provider.{pid} embeds a full-length secret — move to {{env:VAR}} + auth login")
    if re.search(r"pk_(asus|hp)_|\$\(date|xxxx|sk-test|example|changeme", blob, re.I):
        print(f"[FAIL] {f} provider.{pid} contains placeholder-shaped credential")
    models = pdef.get("models", {})
    if isinstance(models, dict) and models:
        print(f"[WARN] {f} provider.{pid} enumerates {len(models)} model(s): {', '.join(list(models)[:6])}{'...' if len(models)>6 else ''} — Zen rotates; each entry is future rot (keep only limit-corrections you can justify)")
    elif isinstance(models, dict):
        print(f"[PASS] {f} provider.{pid} defines no model enumeration")
PYEOF
done

# ── C4 registry drift (live models.dev vs custom limits) ─────────────
echo "--- registry drift (custom limits vs live models.dev) ---"
export CONF_FILES="${FILES[*]}"
if [[ "$SANDBOX" == "1" ]]; then
  echo "[PASS] sandbox registry drift skipped (fixture is hermetic)"
else
python3 - <<'PYEOF'
import json, os, urllib.request
files = os.environ["CONF_FILES"].split()
custom = {}
for f in files:
    if f.endswith(".jsonc"): continue
    try: cfg = json.load(open(f))
    except Exception: continue
    for pid, pdef in (cfg.get("provider") or {}).items():
        for mid, mdef in ((pdef or {}).get("models") or {}).items():
            if isinstance(mdef, dict) and "limit" in mdef:
                custom[(pid, mid)] = mdef["limit"]
if not custom:
    print("[PASS] no custom limit overrides anywhere — nothing to drift"); raise SystemExit
req = urllib.request.Request("https://models.dev/api.json",
    headers={"User-Agent": "opencode-provider-doctor/1.0"})
try:
    reg = json.load(urllib.request.urlopen(req, timeout=20))
except Exception as e:
    print(f"[WARN] registry unreachable ({e}) — drift unchecked"); raise SystemExit
checked = drifted = 0
for (pid, mid), lim in custom.items():
    entry = ((reg.get(pid) or {}).get("models") or {}).get(mid)
    if not entry or not isinstance(entry, dict): print(f"[WARN] {pid}/{mid}: absent from live registry (removed upstream?)"); continue
    checked += 1
    rlim = entry.get("limit") or {}
    if rlim and lim != rlim:
        drifted += 1
        print(f"[WARN] {pid}/{mid}: custom {json.dumps(lim)} != registry {json.dumps(rlim)} (Zen moved — drop or re-justify the override)")
print(f"[{'WARN' if drifted else 'PASS'}] drift: {drifted}/{checked} custom limits disagree with registry" if checked else "[PASS] no comparable entries")
PYEOF
fi

# ── C5 auth ──────────────────────────────────────────────────────────
echo "--- auth ---"
if [[ -f "$DATA_DIR/auth.json" ]]; then
  python3 - "$DATA_DIR/auth.json" <<'PYEOF'
import json,sys
a=json.load(open(sys.argv[1]))
print("auth providers (names only): " + ", ".join(a.keys()))
PYEOF
else fail "no auth.json at $DATA_DIR/auth.json — run 'opencode auth login'"; fi
[[ -f "$CONF_DIR/auth.json" ]] && warn "$CONF_DIR/auth.json exists — dead path (live store is \$DATA_DIR); delete to avoid confusion"
if have opencode; then
  if [[ "$SANDBOX" == "1" ]]; then
    echo "[PASS] sandbox auth listing skipped (fixture is hermetic)"
  else
    timeout 60 opencode auth ls 2>&1 | head -8 || warn "'opencode auth ls' unavailable"
  fi
fi

# ── C6 env ───────────────────────────────────────────────────────────
echo "--- env (names only, values never shown) ---"
env | grep -iE "^(OPENCODE_|OPENAI_|ANTHROPIC_|XDG_)" | sed -E 's/=.*/=<set>/' | head -10
env | grep -iE "proxy" | sed -E 's/=.*/=<set>/' | head -5 || true
nkeys=$(env | grep -ciE "_API_KEY=" || true); echo "env API keys present: $nkeys (values never shown)"

# ── summary (counted from the log — single source of truth) ──────────
sleep 1  # let the tee drain before counting
PASSES=$(grep -c "^\[PASS\]" "$LOG"); WARNS=$(grep -c "^\[WARN\]" "$LOG"); FAILS=$(grep -c "^\[FAIL\]" "$LOG")
echo "=== $PASSES pass, $WARNS warnings, $FAILS failures ==="
echo "Guidance: fix FAILs first; WARNs are hygiene/rot-risk. After ANY config change: quit TUI fully + fresh shell, then 'opencode models' to verify."
if [[ "$APPLY" == "0" ]]; then echo "(dry-run: rerun with --apply to strip empty options objects w/ backups)"; fi
[[ -n "$REPORT" ]] && cp "$LOG" "$REPORT" && echo "report: $REPORT"
rm -f "$LOG"
[[ "$FAILS" -gt 0 ]] && exit 2 || [[ "$WARNS" -gt 0 ]] && exit 1 || exit 0
