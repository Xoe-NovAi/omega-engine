#!/usr/bin/env bash
# 🔱 PRE-T+0 Sprint Bootstrap — Run at session start to ensure fleet readiness
# AP: AP-SPRINT-BOOTSTRAP-v1.0.0
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "═══════════════════════════════════════════════════════════"
echo " PRE-T+0 SPRINT BOOTSTRAP"
echo "═══════════════════════════════════════════════════════════"

# 1. Verify SoulDistiller export
echo "[1/8] Verifying SoulDistiller export..."
source .venv/bin/activate
python -c "from omega.scribe import SoulDistiller, LessonProposal; print('  ✅ SoulDistiller exported')"

# 2. Verify session_end hook uses anyio
echo "[2/8] Verifying session_end hook..."
if grep -q "anyio.run" .opencode/hooks/session_end.py; then
    echo "  ✅ Hook uses anyio.run()"
else
    echo "  ❌ Hook still uses asyncio.run() — fixing..."
    sed -i 's/asyncio.run/anyio.run/' .opencode/hooks/session_end.py
    sed -i 's/import asyncio/import anyio/' .opencode/hooks/session_end.py
fi

# 3. Verify integrations directory
echo "[3/8] Verifying integrations directory..."
if [[ -d src/omega/integrations && -f src/omega/integrations/__init__.py ]]; then
    echo "  ✅ Integrations directory exists"
else
    echo "  ❌ Creating integrations directory..."
    mkdir -p src/omega/integrations
    touch src/omega/integrations/__init__.py
fi

# 4. Verify Four-File Model dirs for all entities
echo "[4/8] Verifying Four-File Model directories..."
for entity in kali maat lilith researcher grokster roc_racoon jem verity doom_guy john_carmack scribe; do
    if [[ -d "data/entities/$entity/memory" && -f "data/entities/$entity/memory/approved_lessons.yaml" && -d "data/entities/$entity/memory/archive" ]]; then
        echo "  ✅ $entity"
    else
        echo "  ❌ Creating for $entity..."
        mkdir -p "data/entities/$entity/memory"
        touch "data/entities/$entity/memory/approved_lessons.yaml"
        mkdir -p "data/entities/$entity/memory/archive"
    fi
done

# 5. Verify MemoryStore API
echo "[5/8] Verifying MemoryStore API..."
python -c "
from omega.memory_store import get_memory_store
m = get_memory_store()
if m:
    import inspect
    sig = inspect.signature(m.get_history)
    params = list(sig.parameters.keys())
    print(f'  ✅ get_history({params})')
else:
    print('  ⚠️ MemoryStore not initialized')
"

# 6. Verify PolicyKit rule
echo "[6/8] Verifying PolicyKit rule for pkexec..."
if [[ -f /etc/polkit-1/rules.d/99-omega-warp.rules ]]; then
    echo "  ✅ PolicyKit rule installed"
else
    echo "  ⚠️ PolicyKit rule NOT installed (requires sudo)"
    echo "     Run: sudo cp /tmp/99-omega-warp.rules /etc/polkit-1/rules.d/99-omega-warp.rules"
fi

# 7. Verify C-0.5 hook registered
echo "[7/8] Verifying C-0.5 hook in opencode.json..."
if grep -q '"session_end"' .opencode/opencode.json; then
    echo "  ✅ Hook registered"
else
    echo "  ❌ Hook NOT registered — add to .opencode/opencode.json:"
    echo '     "hooks": { "session_end": ".opencode/hooks/session_end.py" }'
fi

# 8. Run temple-grade check
echo "[8/8] Running temple-grade check..."
if make temple-grade 2>&1 | tail -5 | grep -q "PASS\|pass"; then
    echo "  ✅ Temple-grade passing"
else
    echo "  ⚠️ Temple-grade check needed — run 'make temple-grade'"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo " BOOTSTRAP COMPLETE"
echo "═══════════════════════════════════════════════════════════"
