#!/bin/bash
# apply_node0_fix.sh v2 — remediate Node 0 OpenCode provider issues (run ON Node 0).
#
# EVIDENCE (not theory — every claim below was reproduced or disproven live):
#  - Built-in providers need ZERO config. Node 1 runs Spark 1.2/1.3, big-pickle
#    (1M window) and OpenRouter (`openrouter/~…` IDs) with NO provider.opencode
#    block anywhere and NO openrouter block. The big-pickle-override lore in
#    AGENTS.md/HARDWARE.md is stale: the entry is built-in (models.dev).
#  - Official docs: config files "merged together, not replaced"; custom models
#    are "additional" (additive). Proven live on 1.18.31: a project-level
#    provider.opencode.models map with 3 entries leaves all 7 built-ins listed
#    AND Spark PONGs at request time. The override is innocent — closed-world
#    theory DEAD. Do NOT enumerate models to fix things (v1 did this; wrong).
#  - Error string "invalid openai provider options" is AI SDK
#    (AI_InvalidArgumentError) client-construction validation, NOT auth.
#    A bogus OPENCODE_API_KEY instead yields "Invalid API key." (different).
#  - Node 0's distinctive unknowns: opencode 1.18.23 (vs 1.18.31), an EMPTY
#    provider.opencode `options: {}` in global config, a 862B auth.json
#    (vs 236B healthy), OPENCODE_API_KEY env (absent on Node 1).
#  Hence v2 is SUBTRACTIVE + parity-seeking: strip the empty options object
#  (pure risk, zero function), upgrade to 1.18.31, retest. No model lists.
#
# Usage (on Node 0):
#   bash apply_node0_fix.sh                                   # DRY-RUN: show plan
#   bash apply_node0_fix.sh --apply                           # backup + apply
#   bash apply_node0_fix.sh --apply --patch-awareness         # + awareness.ts fix
#   bash apply_node0_fix.sh --apply --upgrade-opencode        # + pin 1.18.31
# Options: --project DIR (default ~/Documents/Xoe-NovAi/omega-engine)
#          --global DIR  (default $XDG_CONFIG_HOME or ~/.config/opencode)
#
# AFTER applying: QUIT the TUI completely + open a FRESH shell (startup env
# substitution + stale-process rules, gaps guide §11.2), then verify:
#   opencode models | grep -i spark ; opencode models openrouter | head -3
set -u
PROJECT="$HOME/Documents/Xoe-NovAi/omega-engine"
GLOBAL="${XDG_CONFIG_HOME:-$HOME/.config}/opencode"
APPLY=0; AWARE=0; UPGRADE=0
while [[ $# -gt 0 ]]; do case "$1" in
  --apply) APPLY=1; shift ;;
  --patch-awareness) AWARE=1; shift ;;
  --upgrade-opencode) UPGRADE=1; shift ;;
  --project) PROJECT="$2"; shift 2 ;;
  --global) GLOBAL="$2"; shift 2 ;;
  *) echo "unknown arg: $1" >&2; exit 1 ;;
esac; done
command -v python3 > /dev/null || { echo "python3 required" >&2; exit 1; }

export APPLY
for F in "$GLOBAL/opencode.json" "$GLOBAL/opencode.jsonc" "$PROJECT/opencode.json"; do
  [[ -f "$F" ]] || { echo "SKIP (absent): $F"; continue; }
  [[ "$APPLY" == "1" ]] && cp "$F" "$F.bak.$(date +%Y%m%dT%H%M%S)"
  export FIX_FILE="$F"
  python3 - <<'PYEOF'
import json, os
f = os.environ["FIX_FILE"]
try:
    cfg = json.load(open(f))
except Exception as e:
    print(f"SKIP (unparsable): {f}: {e}"); raise SystemExit
oc = (cfg.get("provider") or {}).get("opencode")
if not isinstance(oc, dict):
    print(f"OK (no provider.opencode block): {f}"); raise SystemExit
if oc.get("options") == {}:
    print(f"PLAN: strip empty provider.opencode.options: {f}")
    if os.environ["APPLY"] == "1":
        del oc["options"]
        json.dump(cfg, open(f, "w"), indent=2)
        print(f"WROTE {f}")
else:
    print(f"OK (options not empty-absent): {f} -> {json.dumps(oc.get('options', '<ABSENT>'))[:120]}")
PYEOF
  python3 -m json.tool "$F" > /dev/null && echo "JSON valid: $F"
done

# ── OpenRouter: NO config (built-in). Verify auth path instead ─────────
echo; echo "OpenRouter check (built-in provider — auth only, never config):"
if command -v opencode > /dev/null; then
  timeout 60 opencode models openrouter 2>/dev/null | head -3 || echo "catalog unreachable"
  echo "If empty: run 'opencode auth login', pick OpenRouter, register ONE key from ~/Desktop/API-keys.md"
  echo "(all 9 keys returned HTTP 200 against https://openrouter.ai/api/v1 — any one works;"
  echo " api.openrouter.ai is NXDOMAIN globally, never use it as baseURL)"
else echo "<no opencode>"; fi

# ── awareness.ts guard (opt-in) ───────────────────────────────────────
AW="$PROJECT/.opencode/plugins/awareness.ts"
if [[ "$AWARE" == "1" ]]; then
  if grep -q 'error?.slice(0, *80)' "$AW" 2>/dev/null; then
    [[ "$APPLY" == "1" ]] && cp "$AW" "$AW.bak.$(date +%Y%m%dT%H%M%S)"
    sed -i 's/error?\.slice(0, *80)/String(error?.message ?? error ?? "").slice(0, 80)/' "$AW"
    echo "patched awareness.ts error guard"
  else echo "awareness.ts pattern absent (already fixed?) — skipped"; fi
fi

# ── opencode pin (opt-in — last unverified variable besides auth.json) ─
if [[ "$UPGRADE" == "1" ]]; then
  echo "upgrading opencode to 1.18.31 (Node 1 parity)…"
  opencode upgrade 1.18.31 && opencode --version
fi

if [[ "$APPLY" == "1" ]]; then
  echo; echo "NEXT (Node 0): quit TUI FULLY + fresh shell, then:"
  echo "  opencode run -m opencode/muse-spark-1.2-contributor-free 'reply with exactly: PONG'"
  echo "If it still fails: rerun collect_node0.sh (v1.1+: correct auth.json path) and ferry back."
else
  echo; echo "DRY-RUN only — rerun with --apply to write (backups automatic)."
fi
