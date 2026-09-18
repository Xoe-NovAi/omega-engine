#!/bin/bash
# apply_node0_fix.sh — remediate Node 0 OpenCode provider issues (run ON Node 0).
#
# Root causes (from USB collector bundles node0-collect-20260918T135439Z/135710Z):
#  1. Muse Spark "invalid openai provider options": the PROJECT opencode.json
#     (highest precedence) defines provider.opencode.models with ONLY 3 entries
#     (nemotron/mimo/big-pickle). Spark 1.2/1.3 fall off the override map and the
#     client builds with invalid options. Fix: add both Spark entries (Node 1's
#     Big-Pickle 1M-window limits). Test BEFORE upgrading opencode (isolates var).
#  2. OpenRouter dead everywhere: no provider block on either node, no key in
#     Node 1 .env, and the `api.openrouter.ai` hostname is NXDOMAIN globally.
#     Correct base is https://openrouter.ai/api/v1 (probed HTTP 200). All 9
#     Node 0 keys return HTTP 200 against it. Fix: add provider block + live
#     catalog model registration. OPENROUTER_API_KEY already exported (len 73).
#  3. awareness.ts:137 `error?.slice` crashes on non-string errors, masking the
#     real message. Fix: String()-guard (opt-in --patch-awareness).
#
# Usage (on Node 0):
#   bash apply_node0_fix.sh                                   # DRY-RUN: show plan
#   bash apply_node0_fix.sh --apply                           # backup + apply
#   bash apply_node0_fix.sh --apply --patch-awareness         # + awareness.ts fix
#   bash apply_node0_fix.sh --apply --upgrade-opencode        # + pin 1.18.31
# Options: --project DIR (default ~/Documents/Xoe-NovAi/omega-engine)
#
# AFTER applying: QUIT the TUI completely + open a FRESH shell (startup env
# substitution + stale-process rules, gaps guide §11.2), then verify:
#   opencode models | grep -i spark ; opencode models openrouter | head
set -u
PROJECT="$HOME/Documents/Xoe-NovAi/omega-engine"
APPLY=0; AWARE=0; UPGRADE=0
while [[ $# -gt 0 ]]; do case "$1" in
  --apply) APPLY=1; shift ;;
  --patch-awareness) AWARE=1; shift ;;
  --upgrade-opencode) UPGRADE=1; shift ;;
  --project) PROJECT="$2"; shift 2 ;;
  *) echo "unknown arg: $1" >&2; exit 1 ;;
esac; done

F="$PROJECT/opencode.json"
[[ -f "$F" ]] || { echo "MISSING project config: $F (use --project)" >&2; exit 1; }
command -v python3 > /dev/null || { echo "python3 required" >&2; exit 1; }
[[ "$APPLY" == "1" ]] && cp "$F" "$F.bak.$(date +%Y%m%dT%H%M%S)" && echo "backup written"

# ── live OpenRouter catalog (no auth needed) ─────────────────────────
CATALOG="$(mktemp)"
if command -v curl > /dev/null; then
  timeout 25 curl -sS -m 20 https://openrouter.ai/api/v1/models -o "$CATALOG" 2>/dev/null \
    && python3 -c "import json;json.load(open('$CATALOG'))" 2>/dev/null \
    && echo "live catalog: $(python3 -c "import json;print(len(json.load(open('$CATALOG'))['data']))") models" \
    || { echo "catalog fetch failed — static fallback"; echo '{"data":[]}' > "$CATALOG"; }
else echo "no curl — static fallback"; echo '{"data":[]}' > "$CATALOG"; fi

export PROJ_FILE="$F" CATALOG APPLY
python3 - <<'PYEOF'
import json, os, re
f = os.environ["PROJ_FILE"]
cfg = json.load(open(f))
prov = cfg.setdefault("provider", {})

# 1. Spark entries under provider.opencode.models (mirror Big-Pickle 1M window)
oc = prov.setdefault("opencode", {}).setdefault("models", {})
spark_limit = {"context": 1000000, "input": 950000, "output": 64000}
plan = []
for mid, disp in [("muse-spark-1.2-contributor-free", "Muse Spark 1.2 Free (Zen)"),
                  ("muse-spark-1.3-contributor-free", "Muse Spark 1.3 Free (Zen)")]:
    if mid in oc:
        plan.append(f"spark {mid}: ALREADY PRESENT — left untouched")
    else:
        plan.append(f"spark {mid}: ADD name={disp!r} limit=1M/950k/64k")
        if os.environ["APPLY"] == "1":
            oc[mid] = {"name": disp, "limit": dict(spark_limit)}

# 2. OpenRouter provider (apex baseURL — api. subdomain is NXDOMAIN)
fam = re.compile(r"^(anthropic|openai|google|deepseek|qwen|meta-llama|mistralai|x-ai)/")
defs = {}
try:
    data = json.load(open(os.environ["CATALOG"]))["data"]
    for m in data:
        mid = m.get("id", "")
        if fam.match(mid):
            ctx = int(m.get("context_length") or 200000)
            defs[mid] = {"name": mid.split("/", 1)[1],
                         "limit": {"context": ctx,
                                   "output": min(32000, max(4096, ctx // 10))}}
    defs = dict(sorted(defs.items())[:80])
except Exception as e:
    plan.append(f"catalog parse failed ({e}) — static fallback trio")
if not defs:
    for mid in ["anthropic/claude-sonnet-4", "openai/gpt-5-mini", "deepseek/deepseek-chat"]:
        defs[mid] = {"name": mid.split("/")[1],
                     "limit": {"context": 200000, "output": 32000}}
or_block = {"npm": "@ai-sdk/openai-compatible", "name": "OpenRouter",
            "options": {"baseURL": "https://openrouter.ai/api/v1",
                        "apiKey": "{env:OPENROUTER_API_KEY}"},
            "models": defs}
if "openrouter" in prov:
    plan.append("openrouter: ALREADY PRESENT — left untouched")
else:
    plan.append(f"openrouter: ADD baseURL=apex, apiKey={{env:…}}, {len(defs)} catalog models")
    if os.environ["APPLY"] == "1":
        prov["openrouter"] = or_block

print("\n".join("  PLAN: " + p for p in plan))
if os.environ["APPLY"] == "1":
    json.dump(cfg, open(f, "w"), indent=2)
    print("  WROTE " + f)
PYEOF
rm -f "$CATALOG"
python3 -m json.tool "$F" > /dev/null && echo "JSON valid: $F"

# ── 3. awareness.ts guard (opt-in) ───────────────────────────────────
AW="$PROJECT/.opencode/plugins/awareness.ts"
if [[ "$AWARE" == "1" ]]; then
  if grep -q 'error?.slice(0, *80)' "$AW" 2>/dev/null; then
    [[ "$APPLY" == "1" ]] && cp "$AW" "$AW.bak.$(date +%Y%m%dT%H%M%S)"
    sed -i 's/error?\.slice(0, *80)/String(error?.message ?? error ?? "").slice(0, 80)/' "$AW"
    echo "patched awareness.ts error guard"
  else echo "awareness.ts pattern absent (already fixed?) — skipped"; fi
fi

# ── 4. opencode pin (opt-in) ─────────────────────────────────────────
if [[ "$UPGRADE" == "1" ]]; then
  echo "upgrading opencode to 1.18.31 (Node 1 parity)…"
  opencode upgrade 1.18.31 && opencode --version
fi

# ── verification guidance ────────────────────────────────────────────
if [[ "$APPLY" == "1" ]]; then
  echo; echo "NEXT (Node 0): quit TUI FULLY + fresh shell, then:"
  echo "  opencode models | grep -i spark"
  echo "  opencode models openrouter | head -5"
  echo "  opencode run -m opencode/muse-spark-1.2-contributor-free 'reply with exactly: PONG'"
  echo "Test Spark BEFORE any upgrade (isolates config-fix vs version)."
else
  echo; echo "DRY-RUN only — rerun with --apply to write (backups automatic)."
fi
