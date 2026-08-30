#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 PRE-T+0 Sprint Bootstrap — Run at session start to ensure fleet readiness
# AP: AP-SPRINT-BOOTSTRAP-v1.0.0
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "═══════════════════════════════════════════════════════════"
echo " PRE-T+0 SPRINT BOOTSTRAP"
echo "═══════════════════════════════════════════════════════════"

# 1. Verify session_end hook uses anyio
echo "[1/7] Verifying session_end hook..."
if grep -q "anyio.run" .opencode/hooks/session_end.py; then
    echo "  ✅ Hook uses anyio.run()"
else
    echo "  ❌ Hook still uses asyncio.run() — fixing..."
    sed -i 's/asyncio.run/anyio.run/' .opencode/hooks/session_end.py
    sed -i 's/import asyncio/import anyio/' .opencode/hooks/session_end.py
fi

# 2. Verify integrations directory
echo "[2/7] Verifying integrations directory..."
if [[ -d src/omega/integrations && -f src/omega/integrations/__init__.py ]]; then
    echo "  ✅ Integrations directory exists"
else
    echo "  ❌ Creating integrations directory..."
    mkdir -p src/omega/integrations
    touch src/omega/integrations/__init__.py
fi

# 3. Verify Four-File Model dirs for all entities
echo "[3/7] Verifying Four-File Model directories..."
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

# 4. Verify MemoryStore API
echo "[4/7] Verifying MemoryStore API..."
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

# 5. Verify PolicyKit rule
echo "[5/7] Verifying PolicyKit rule for pkexec..."
if [[ -f /etc/polkit-1/rules.d/99-omega-warp.rules ]]; then
    echo "  ✅ PolicyKit rule installed"
else
    echo "  ⚠️ PolicyKit rule NOT installed (requires sudo)"
    echo "     Run: sudo cp /tmp/99-omega-warp.rules /etc/polkit-1/rules.d/99-omega-warp.rules"
fi

# 6. Verify hook registered
echo "[6/7] Verifying hook in opencode.json..."
if grep -q '"session_end"' .opencode/opencode.json; then
    echo "  ✅ Hook registered"
else
    echo "  ❌ Hook NOT registered — add to .opencode/opencode.json:"
    echo '     "hooks": { "session_end": ".opencode/hooks/session_end.py" }'
fi

# 7. Run temple-grade check
echo "[7/7] Running temple-grade check..."
if make temple-grade 2>&1 | tail -5 | grep -q "PASS\|pass"; then
    echo "  ✅ Temple-grade passing"
else
    echo "  ⚠️ Temple-grade check needed — run 'make temple-grade'"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo " BOOTSTRAP COMPLETE"
echo "═══════════════════════════════════════════════════════════"
