#!/usr/bin/env bash
# 🔱 Omega Engine — Free Tier Model Validator
# ⬡ OMEGA ⬡ SOPHIA ⬡ opencode ⬡ trc_model_check ⬡ PHASE-0
#
# Queries all provider APIs for current available free models.
# Usage:
#   ./scripts/check_free_models.sh              # Quick summary
#   ./scripts/check_free_models.sh --report     # Full markdown report
#   ./scripts/check_free_models.sh --diff       # Diff against last known

set -euo pipefail

OMEGA_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MODEL_DB="${OMEGA_ROOT}/docs/research/model_db"
LAST_STATE="${MODEL_DB}/.last_state.json"
REPORT_FILE="${MODEL_DB}/CURRENT_MODELS.md"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

mkdir -p "$MODEL_DB"

echo "🔱 Omega Model Validator — ${TIMESTAMP}"
echo ""

# ── 1. OpenRouter (public API, no key needed) ─────────────────────
echo "📡 Querying OpenRouter..."
OR_RAW=$(curl -s "https://openrouter.ai/api/v1/models" 2>/dev/null)

OR_FREE=$(echo "${OR_RAW}" | python3 -c '
import json, sys
data = json.load(sys.stdin)
free = []
for m in data.get("data", []):
    p = m.get("pricing", {})
    try:
        if float(p.get("prompt", 1)) == 0 and float(p.get("completion", 1)) == 0:
            free.append({
                "id": m["id"],
                "context": m.get("context_length", 0),
                "name": m.get("name", m["id"])
            })
    except (ValueError, TypeError):
        pass
json.dump(free, sys.stdout, indent=2)
' 2>/dev/null || echo "[]")

OR_COUNT=$(echo "${OR_FREE}" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(len(d))' 2>/dev/null || echo "0")
echo "   → ${OR_COUNT} free models"

# ── 2. Google AI Studio (needs .env key) ──────────────────────────
echo "📡 Querying Google AI Studio..."
GOOGLE_KEY=""
if [ -f "${OMEGA_ROOT}/.env" ]; then
    GOOGLE_KEY=$(grep "^GOOGLE_API_KEY=" "${OMEGA_ROOT}/.env" | head -1 | cut -d= -f2- | tr -d '"' || echo "")
fi

GOOGLE_GEMMA="[]"
GOOGLE_COUNT="0"
if [ -n "${GOOGLE_KEY}" ]; then
    GOOGLE_RAW=$(curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=${GOOGLE_KEY}" 2>/dev/null)
    GOOGLE_GEMMA=$(echo "${GOOGLE_RAW}" | python3 -c '
import json, sys
data = json.load(sys.stdin)
gemma = []
for m in data.get("models", []):
    name = m["name"].replace("models/", "")
    if "gemma" in name:
        gemma.append({"id": name, "methods": m.get("supportedGenerationMethods", [])})
json.dump(gemma, sys.stdout, indent=2)
' 2>/dev/null || echo "[]")
    GOOGLE_COUNT=$(echo "${GOOGLE_GEMMA}" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(len(d))' 2>/dev/null || echo "0")
    echo "   → ${GOOGLE_COUNT} Gemma models"
else
    echo "   ⚠️  No GOOGLE_API_KEY in .env — Google provider will never activate!"
fi

# ── 3. OpenCode Zen (public, limited info) ────────────────────────
echo "📡 Querying OpenCode Zen..."
ZEN_RAW=$(curl -s "https://opencode.ai/zen/v1/models" 2>/dev/null)

ZEN_PARSE=$(echo "${ZEN_RAW}" | python3 -c '
import json, sys
data = json.load(sys.stdin)
models = data.get("models", data.get("data", []))
free_ids = [m["id"] for m in models if "free" in m.get("id", "").lower()]
all_ids = [m["id"] for m in models]
print(json.dumps({"total": len(all_ids), "free": len(free_ids), "all": all_ids, "free_ids": free_ids}))
' 2>/dev/null || echo '{"total":0,"free":0,"all":[],"free_ids":[]}')

ZEN_TOTAL=$(echo "${ZEN_PARSE}" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["total"])' 2>/dev/null || echo "0")
ZEN_FREE=$(echo "${ZEN_PARSE}" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["free"])' 2>/dev/null || echo "0")
echo "   → ${ZEN_TOTAL} total, ${ZEN_FREE} free models"

# ── Build snapshot ─────────────────────────────────────────────────
SNAPSHOT_JSON=$(python3 -c "
import json, sys
snap = {
    'timestamp': '${TIMESTAMP}',
    'openrouter': {'free_count': ${OR_COUNT}, 'free': json.loads('''${OR_FREE}''')},
    'google': {'gemma_count': ${GOOGLE_COUNT}, 'gemma': json.loads('''${GOOGLE_GEMMA}''')},
    'opencode_zen': json.loads('''${ZEN_PARSE}''')
}
json.dump(snap, sys.stdout, indent=2)
")
echo "${SNAPSHOT_JSON}" > /tmp/omega_model_snapshot.json

# ── Diff against last state ────────────────────────────────────────
echo ""
if [ -f "${LAST_STATE}" ]; then
    echo "🔍 Checking for changes..."
    DIFF_RESULT=$(python3 -c "
import json
old = json.load(open('${LAST_STATE}'))
new = json.load(open('/tmp/omega_model_snapshot.json'))
old_ids = set(m['id'] for m in old.get('openrouter', {}).get('free', []))
new_ids = set(m['id'] for m in new.get('openrouter', {}).get('free', []))
added = new_ids - old_ids
removed = old_ids - new_ids
old_zen = set(old.get('opencode_zen', {}).get('all', []))
new_zen = set(new.get('opencode_zen', {}).get('all', []))
zen_added = new_zen - old_zen
zen_removed = old_zen - new_zen
changes = []
if added: changes.append(f'OR_ADDED:{sorted(added)}')
if removed: changes.append(f'OR_REMOVED:{sorted(removed)}')
if zen_added: changes.append(f'ZEN_ADDED:{sorted(zen_added)}')
if zen_removed: changes.append(f'ZEN_REMOVED:{sorted(zen_removed)}')
if changes:
    print('CHANGED')
    for c in changes: print(c)
else:
    print('NO_CHANGE')
" 2>/dev/null || echo "UNKNOWN")
    echo "   ${DIFF_RESULT}"
else
    echo "📝 No previous state — saving initial snapshot"
fi

mv /tmp/omega_model_snapshot.json "${LAST_STATE}"

# ── Full report (--report or --update-docs) ────────────────────────
if [[ "${1:-}" == "--report" || "${1:-}" == "--update-docs" ]]; then
    python3 "${OMEGA_ROOT}/scripts/generate_model_report.py"
fi

echo ""
echo "✅ Complete"
echo "   Last state: ${LAST_STATE}"
echo "   OpenRouter: ${OR_COUNT} free | Google: ${GOOGLE_COUNT} Gemma | Zen: ${ZEN_TOTAL} total (${ZEN_FREE} free)"
