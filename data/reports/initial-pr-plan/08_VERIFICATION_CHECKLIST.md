# 🔱 Omega Engine Initial PR Plan — Verification Checklist
## Complete Verification Steps for Each Commit and Final PR

**AP Token**: `AP-INITIAL-PR-PLAN-20260814-v1.0.0`  
**Part**: 08 of 09  
**Date**: 2026-08-14  

---

## ✅ COMMIT 1 VERIFICATION: NUCLEAR CLEANUP

### Pre-Commit Checks
```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine

# 1. Verify files to be deleted exist
ls session-ses_07ee.md P1.md P2.md P3.md P4.md P5.md P6.md P7.md P8.md P9.md 2>/dev/null | wc -l
# Should show: 10

ls data/realms/ 2>/dev/null | wc -l
# Should show: 7 directories

ls src/omega/state_manager.py src/omega/pool_tracker.py src/omega/mandate_enforcer.py \
   src/omega/oracle/link_p9_runtime.py src/omega/oracle/lifecycle_harvester.py 2>/dev/null | wc -l
# Should show: 5

ls src/omega/vault/ 2>/dev/null && echo "EXISTS" || echo "NOT FOUND"
# Should show: EXISTS

ls tests/unit/test_vault_core.py 2>/dev/null && echo "EXISTS" || echo "NOT FOUND"
# Should show: EXISTS
```

### Post-Commit Verification
```bash
# 1. Git status shows deletions
git status --short | grep -E "^ D" | wc -l
# Should show: ~35+ deletions

# 2. Core imports still work
.venv/bin/python -c "
from omega.oracle.oracle import Oracle
from omega.oracle.model_gateway import ModelGateway
from omega.oracle.entity_registry import EntityRegistry
from omega.oracle.wad_loader import WADLoader  # Still exists at this point
from omega.memory_store import get_memory_store
print('All core imports OK')
"

# 3. Core tests still pass (before M2 fix)
.venv/bin/python -m pytest tests/test_oracle.py tests/test_entity_registry.py \
  tests/test_model_gateway.py tests/test_wad_loader.py tests/test_memory_store.py -q
# Should show: 92 passed, 2 failed (memory store FTS)

# 4. Verify dead modules are gone
ls src/omega/state_manager.py src/omega/pool_tracker.py src/omega/mandate_enforcer.py \
   src/omega/oracle/link_p9_runtime.py src/omega/oracle/lifecycle_harvester.py 2>/dev/null
# Should show: No such file or directory

# 5. Verify vault is gone
ls src/omega/vault/ 2>/dev/null && echo "VAULT STILL EXISTS" || echo "VAULT DELETED"
# Must show: VAULT DELETED

ls tests/unit/test_vault_core.py 2>/dev/null && echo "TEST EXISTS" || echo "TEST DELETED"
# Must show: TEST DELETED

# 6. Verify VOS theater gone
ls data/realms/ 2>/dev/null && echo "REALMS EXIST" || echo "REALMS DELETED"
# Must show: REALMS DELETED

ls src/omega/cli/realm_cli.py 2>/dev/null && echo "REALM_CLI EXISTS" || echo "REALM_CLI DELETED"
# Must show: REALM_CLI DELETED
```

### Commit 1 Success Criteria
- [ ] ~35+ files deleted
- [ ] Core imports work
- [ ] 92 core tests pass (2 memory store failures OK for now)
- [ ] 5 dead modules deleted
- [ ] Vault deleted (17 failing tests gone)
- [ ] VOS theater deleted (realms, realm_cli.py)
- [ ] Root theater deleted

---

## ✅ COMMIT 2 VERIFICATION: M2 FIREWALL FIX

### Pre-Commit Checks
```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine

# 1. Verify WAD refs exist before fix
grep -rn "WAD" src/omega/ --include="*.py" | \
  grep -v "__pycache__" | \
  grep -v "\[id-soft:" | \
  grep -v "doom-1993" | wc -l
# Should show: 344

# 2. Verify wad_loader.py exists
ls src/omega/oracle/wad_loader.py 2>/dev/null && echo "EXISTS" || echo "NOT FOUND"
# Should show: EXISTS

# 3. Verify config/wads/ exists
ls config/wads/ 2>/dev/null && echo "EXISTS" || echo "NOT FOUND"
# Should show: EXISTS
```

### Post-Commit Verification
```bash
# 1. Verify 0 WAD refs in engine core (except heritage)
grep -rn "WAD" src/omega/ --include="*.py" | \
  grep -v "__pycache__" | \
  grep -v "\[id-soft:" | \
  grep -v "doom-1993" | wc -l
# Must show: 0

# 2. Verify heritage tags preserved on StackLoader
grep -A 10 "class StackLoader" src/omega/oracle/stack_loader.py | grep "id-soft"
# Must show: [id-soft: doom-1993] tags

# 3. Verify StackLoader loads WAD format
grep -A 20 "class StackLoader" src/omega/oracle/stack_loader.py | grep -i "wad"
# Should show: references to WAD format loading

# 4. Verify config updated
grep "active_stack" config/omega.yaml
# Must show: active_stack: "_omega_default"

# 5. Verify directory renamed
ls config/stacks/
# Must show: stack directories

# 6. Verify stack_loader.py exists
ls src/omega/oracle/stack_loader.py 2>/dev/null && echo "EXISTS" || echo "NOT FOUND"
# Must show: EXISTS

# 6. Verify wad_loader.py is gone
ls src/omega/oracle/wad_loader.py 2>/dev/null && echo "STILL EXISTS" || echo "RENAMED"
# Must show: RENAMED

# 7. Core tests pass
.venv/bin/python -m pytest tests/test_stack_loader.py -q
# Must show: all passed

# 8. All core tests pass
.venv/bin/python -m pytest tests/test_oracle.py tests/test_entity_registry.py \
  tests/test_model_gateway.py tests/test_stack_loader.py tests/test_memory_store.py -q
# Should show: 92 passed, 2 failed (memory store FTS)

# 9. Temple-grade M2 gate passes
make temple-grade 2>&1 | grep -i "m2\|firewall"
# Must show: M2 PASS
```

### Commit 2 Success Criteria
- [ ] 0 WAD refs in engine core (except heritage)
- [ ] Heritage tags preserved on StackLoader
- [ ] StackLoader loads WAD format
- [ ] config/omega.yaml has active_stack
- [ ] config/stacks/ directory exists
- [ ] stack_loader.py exists, wad_loader.py gone
- [ ] All core tests pass
- [ ] Temple-grade M2 gate PASS

---

## ✅ COMMIT 3 VERIFICATION: HONEST README + VERIFICATION

### Post-Commit Verification
```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine

# 1. Verify README rewritten
grep -c "What Works (v0.1)" README.md
# Must show: 1

grep -c "Local inference (GGUF)" README.md
# Must show: 1

grep -c "Entity routing" README.md
# Must show: 1

# 2. Verify test count badge updated
TEST_COUNT=$(.venv/bin/python -m pytest --collect-only -q 2>/dev/null | tail -1 | grep -oE '[0-9]+')
grep "${TEST_COUNT}_passing" README.md
# Must show: 1

# 3. Verify no theater promises in README
grep -i "vr\|p2p\|godot\|omegaverse\|soul evolution" README.md
# Must show: 0 (no matches)

# 4. Full test suite passes
make test
# Must show: XXX passed, 0 failed, 0 quarantined

# 5. Temple-grade all gates pass
make temple-grade
# Must show: All 11 gates green

# 6. Core flow works
.venv/bin/python -c "
from omega.oracle.oracle import Oracle
from omega.oracle.model_gateway import ModelGateway
from omega.oracle.entity_registry import EntityRegistry
from omega.oracle.stack_loader import StackLoader
from omega.memory_store import get_memory_store
print('All core imports OK')
"

# 7. CLI works
.venv/bin/python -m omega.cli.oracle_cli --help
.venv/bin/python -m omega.cli.oracle_cli list-entities

# 8. No WAD refs in engine core
grep -rn "WAD" src/omega/ --exclude-dir=__pycache__ | \
  grep -v "\[id-soft:" | grep -v "doom-1993" | wc -l
# Must show: 0

# 9. Clean git status
git status --short
# Only: modified README.md, modified config/omega.yaml, new/renamed source files
```

### Commit 3 Success Criteria
- [ ] README rewritten with honest content
- [ ] Test count badge shows actual count
- [ ] No theater promises in README
- [ ] `make test`: all passing, 0 failed, 0 quarantined
- [ ] `make temple-grade`: all 11 gates green
- [ ] Core imports work
- [ ] CLI works
- [ ] 0 WAD refs in engine core
- [ ] Clean git status

---

## ✅ COMMIT 4 VERIFICATION: COORDINATION CLEANUP

### Post-Commit Verification
```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine

# 1. Verify M27-mandatory files exist
for f in ACTIVE_SPRINT.json HMC_COLLABORATION_HUB.md GAP_REGISTRY.json \
         RESEARCH_PLAN_PHASE1_4_20260813.md TASK_REGISTRY.json \
         SESSION_ANCHOR.md DECISION_LEDGER.md; do
  if [ -f "data/coordination/$f" ]; then
    echo "KEEP: $f ($(wc -c < data/coordination/$f) bytes)"
  else
    echo "MISSING: $f — PROBLEM"
  fi
done

# 2. Verify orphaned files deleted
for f in KALI_DEV_ROADMAP_20260811.md KALI_OVERSIGHT_PORTFOLIO_20260811.md \
         KNOWLEDGE_GAPS_RESEARCH_20260811.md RESEARCH_JOB_BOARD.yaml \
         SONNET_4_6_REVIEW_20260814.md; do
  if [ -f "data/coordination/$f" ]; then
    echo "STILL EXISTS: $f — PROBLEM"
  else
    echo "DELETED: $f ✓"
  fi
done

# 3. Count remaining coordination files
ls data/coordination/ | grep -v "^\." | wc -l
# Should show: 7 M27 files + maybe 1-2 others

# 4. Verify tests still pass
make test
# Must show: all passing

# 5. Verify temple-grade still passes
make temple-grade
# Must show: all 11 gates green
```

### Commit 4 Success Criteria
- [ ] 7 M27-mandatory files exist
- [ ] 5 orphaned files deleted
- [ ] Coordination directory clean
- [ ] Tests still pass
- [ ] Temple-grade still passes

---

## ✅ FINAL PR VERIFICATION (All Commits Complete)

### Complete Verification Suite
```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine

echo "=== FINAL VERIFICATION SUITE ==="
echo ""

# 1. Test suite
echo "1. Test suite..."
make test
echo ""

# 2. Temple-grade
echo "2. Temple-grade gates..."
make temple-grade
echo ""

# 3. Core imports
echo "3. Core imports..."
.venv/bin/python -c "
from omega.oracle.oracle import Oracle
from omega.oracle.model_gateway import ModelGateway
from omega.oracle.entity_registry import EntityRegistry
from omega.oracle.stack_loader import StackLoader
from omega.memory_store import get_memory_store
print('All core imports OK')
"
echo ""

# 4. CLI works
echo "4. CLI works..."
.venv/bin/python -m omega.cli.oracle_cli --help > /dev/null && echo "Help OK"
.venv/bin/python -m omega.cli.oracle_cli list-entities > /dev/null && echo "List entities OK"
echo ""

# 5. No WAD refs in engine core
echo "5. M2 firewall (0 WAD refs)..."
COUNT=$(grep -rn "WAD" src/omega/ --exclude-dir=__pycache__ | grep -v "\[id-soft:" | grep -v "doom-1993" | wc -l)
echo "WAD refs in engine core: $COUNT"
if [ "$COUNT" -eq 0 ]; then
  echo "M2: PASS"
else
  echo "M2: FAIL"
fi
echo ""

# 6. Heritage tags on StackLoader
echo "6. Heritage tags on StackLoader..."
grep -A 10 "class StackLoader" src/omega/oracle/stack_loader.py | grep "id-soft" && echo "Heritage: PASS" || echo "Heritage: FAIL"
echo ""

# 7. Config updated
echo "7. Config updated..."
grep "active_stack" config/omega.yaml && echo "Config: PASS" || echo "Config: FAIL"
echo ""

# 8. Directory renamed
echo "8. Directory renamed..."
ls config/stacks/ > /dev/null && echo "Directory: PASS" || echo "Directory: FAIL"
echo ""

# 9. Git status clean
echo "9. Git status..."
git status --short
echo ""

# 10. README honest
echo "10. README honest..."
grep -i "vr\|p2p\|godot\|omegaverse\|soul evolution" README.md > /dev/null && echo "README: FAIL (theater promises found)" || echo "README: PASS (no theater promises)"
echo ""

echo "=== VERIFICATION COMPLETE ==="
```

### Final Success Criteria (ALL MUST PASS)

| Check | Must Pass |
|-------|-----------|
| `make test` | ✅ All passing, 0 failed, 0 quarantined |
| `make temple-grade` | ✅ All 11 gates green |
| Core imports | ✅ Oracle, ModelGateway, EntityRegistry, StackLoader, MemoryStore |
| CLI works | ✅ `omega talk`, `omega summon`, `omega list-entities` |
| M2 firewall | ✅ 0 WAD refs in engine core (except heritage) |
| Heritage tags | ✅ `[id-soft: doom-1993]` on StackLoader |
| Config | ✅ `active_stack` in config/omega.yaml |
| Directory | ✅ `config/stacks/` exists |
| Git status | ✅ Clean (only expected modifications) |
| README | ✅ Honest, no theater promises, actual test count |

---

## 🚀 PR READY CHECKLIST

- [ ] All verification checks pass
- [ ] Branch pushed to origin
- [ ] PR created with honest description
- [ ] PR description includes:
  - What works (v0.1 features)
  - What was cleaned (theater, dead code, vault)
  - M2 firewall fix details
  - Verification results
  - Sovereignty claims verified

---

**Next**: See `09_HANDOFF_TO_GROK_CLI.md` for the complete handoff packet details.
