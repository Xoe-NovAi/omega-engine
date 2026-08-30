# 🔱 Pillar Decoupling Refactor Plan — Temple-Grade Execution
**AP Token**: `AP-ROC_RACOON-PILLAR-REFACTOR-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_mining ⬡ ACTIVE

**Date**: 2026-08-22
**Source**: `PILLAR_LEAK_AUDIT_20260822.md`
**Canonical Ruling**: D180 / PIVOT_LOG_CANONICAL.md §1200-1210
**Temple-Grade Gates**: T1-T11 (must pass `make temple-grade` after each phase)

---

## 🎯 Objective

Complete the M2 Engine-Stack Firewall decoupling by removing all pillar/WAD concept leaks from Engine core and MCP Hub boundary layer. The Engine must be a universal runtime — no WAD-specific concepts (pillars, elements, chakras, sigils) in core code.

**End State**:
- Engine core: `slots` (abstract IDs N1-N10), `metadata` (opaque WAD bag)
- MCP Hub: `oracle_list_node_keepers`, `slot` field in responses
- WADs: `config/wads/arcana_novai/entities.yaml` uses `slots:` not `pillars:`
- Tests: All assert `slots`/`metadata`, not `pillars`/`traits`
- Setup: `scripts/setup.sh` uses `list_node_keepers()` and `result.slots`

---

## 📦 Phase 0: Pre-Flight (30 min)

### 0.1 Baseline Verification
```bash
# Capture current test state
make test 2>&1 | tail -20
# Capture current setup.sh state
bash scripts/setup.sh 2>&1 | grep -E "(Pillar|pillar|Error|AttributeError)"
```

### 0.2 Create Workspace Lock
```bash
cat > data/coordination/ROC_RACOON_WORKSPACE_LOCK_20260822.md << 'EOF'
# Workspace Lock: Pillar Decoupling Refactor
**Agent**: roc_racoon
**Started**: 2026-08-22
**Phase**: 0
**Scope**: M2 Firewall - Pillar → Slot migration
**Lock File**: This file
EOF
```

### 0.3 Hivemind Awareness
```bash
# Post context to Hivemind
omega-hub_hivemind_post_context \
  --intent="refactor" \
  --status="starting" \
  --continuation="Phase 0 pre-flight for Pillar Decoupling Refactor (D180)"
```

---

## 📦 Phase 1: Runtime Blockers — Scripts & MCP Hub (2-3 hours)

### 1.1 Fix `scripts/setup.sh` (P0 — Blocks Setup Verification)

**File**: `scripts/setup.sh`
**Lines**: 107, 111

```bash
# BEFORE (line 107):
print(f'  Pillar Keepers: {len(registry.list_pillar_keepers())}')

# AFTER:
print(f'  Node Keepers: {len(registry.list_node_keepers())}')

# BEFORE (line 111):
print(f'  Oracle test: {result.entity} — {result.pillar}')

# AFTER:
slots_str = ", ".join(result.slots) if result.slots else "—"
print(f'  Oracle test: {result.entity} — slots: {slots_str}')
```

**Verification**: `bash scripts/setup.sh` — must print "Node Keepers" and "slots:" without AttributeError.

### 1.2 Fix `scripts/mandate_gates.py` (P0 — M3 Gate)

**File**: `scripts/mandate_gates.py`
**Lines**: 62, 71, 77, 79

```python
# BEFORE:
iris_in_pillar = False
# Check if iris appears on a line with a pillar slot assignment
iris_in_pillar = True
check("M3: Iris Constant", not iris_in_pillar)

# AFTER:
iris_in_slot = False
# Check if iris appears on a line with a slot assignment
iris_in_slot = True
check("M3: Iris Constant", not iris_in_slot)
```

**Verification**: `python scripts/mandate_gates.py` — M3 check passes.

### 1.3 Fix `scripts/seed_knowledge.py` (P1 — Cosmetic)

**File**: `scripts/seed_knowledge.py`
**Line**: 100

```python
# BEFORE:
f"This is the primary knowledge repository for the {entity.title()} pillar.\n\n"

# AFTER:
f"This is the primary knowledge repository for the {entity.title()} slot.\n\n"
```

### 1.4 Rename MCP Tool: `oracle_list_pillar_keepers` → `oracle_list_node_keepers`

**Files**: 
- `mcp_servers/omega_hub/server.py` (line 142)
- `mcp_servers/omega_hub/hub_tools/tools.py` (lines 529, 531, 542, 3343, 3346, 3354, 3394)

**Changes**:

```python
# server.py line 142:
"oracle_list_node_keepers", "oracle_entity_info", "oracle_assess_intent",

# hub_tools/tools.py line 529:
@m9_safe("oracle_list_node_keepers")

# hub_tools/tools.py line 531:
async def oracle_list_node_keepers() -> str:

# hub_tools/tools.py line 542:
entities = await anyio.to_thread.run_sync((await registry).list_node_keepers)

# hub_tools/tools.py line 3343:
list_node_keepers: List entities with slot assignments (no args)

# hub_tools/tools.py line 3346:
action: The operation to perform (assess_intent|discover_entity|list_node_keepers)

# hub_tools/tools.py line 3354:
valid_actions = {"assess_intent", "discover_entity", "list_node_keepers"}

# hub_tools/tools.py line 3394:
elif action == "list_node_keepers":
```

### 1.5 Fix MCP Tool Response Fields

**File**: `mcp_servers/omega_hub/hub_tools/tools.py`

```python
# Line 1288: Remove "pillar" field from entity_identity
# BEFORE:
"pillar": None,

# AFTER: (remove line entirely)

# Line 1293: Change "pillar_keeper" → "node_keeper"
# BEFORE:
entity_identity["type"] = "pillar_keeper" if entity_reg.slots else "entity"

# AFTER:
entity_identity["type"] = "node_keeper" if entity_reg.slots else "entity"

# Line 1297: Change "pillar" key → "slot"
# BEFORE:
entity_identity["pillar"] = entity_reg.slots[0]

# AFTER:
entity_identity["slot"] = entity_reg.slots[0]
```

**Verification**: Restart MCP Hub, call `oracle_list_node_keepers` — must return valid JSON with `slot` field.

---

## 📦 Phase 2: Test Suite Updates (1-2 hours)

### 2.1 Fix `tests/test_hivemind.py`

**Line 315**: 
```python
# BEFORE:
assert payload["entity"]["pillar"] == "P7"

# AFTER:
assert "P7" in payload["entity"]["slots"]
```

### 2.2 Fix `tests/test_rag_router.py`

**Line 25**: Update query text (cosmetic)
```python
# BEFORE:
"Compare the 23 Sovereign Mandates across all pillars and identify contradictions"

# AFTER:
"Compare the 23 Sovereign Mandates across all slots and identify contradictions"
```

### 2.3 Fix `tests/contracts/test_mandate_auditor.py`

**Lines 271, 277, 283, 294, 300**: Rename tests and update comments
```python
# BEFORE:
def test_m3_detects_iris_in_pillar(self):
    # Violation: MESSENGER_BRIDGE role with a pillar_slot
    "    purpose: Test messenger in pillar\n"

def test_m3_passes_when_iris_not_in_pillar(self):
    # Non-violation: iris is a messenger, not a pillar keeper

# AFTER:
def test_m3_detects_iris_in_slot(self):
    # Violation: MESSENGER_BRIDGE role with a slot assignment
    "    purpose: Test messenger in slot\n"

def test_m3_passes_when_iris_not_in_slot(self):
    # Non-violation: iris is a messenger, not a node keeper
```

### 2.4 Fix `tests/contracts/test_dispatch_registry.py`

**Lines 49, 52, 55**: Rename test and variable
```python
# BEFORE:
def test_dispatch_registry_get_entity_by_role_pillar(self):
    pillar = get_entity_by_role("N1")
    # Multiple entities have P1 role; verify pillar is among them

# AFTER:
def test_dispatch_registry_get_entity_by_role_slot(self):
    slot_entity = get_entity_by_role("N1")
    # Multiple entities have N1 role; verify slot entity is among them
```

### 2.5 Fix `tests/test_a2a_bridge.py`

**Lines 603, 605**: Update SPIFFE ID path
```python
# BEFORE:
sid = SPIFFEID.parse("spiffe://omega.local/entity/pillar/p6")
assert sid.path == "entity/pillar/p6"

# AFTER:
sid = SPIFFEID.parse("spiffe://omega.local/entity/slot/p6")
assert sid.path == "entity/slot/p6"
```

**Verification**: `make test` — all tests must pass (276+ tests).

---

## 📦 Phase 3: WAD Cleanup (1 hour)

### 3.1 Update `config/wads/arcana_novai/entities.yaml`

**Action**: Replace all `pillars:` keys with `slots:` (extract slot ID from "P1: Flesh" → "P1")

```bash
# Automated migration (dry-run first):
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
python3 -c "
import yaml
with open('config/wads/arcana_novai/entities.yaml') as f:
    data = yaml.safe_load(f)

for key, entity in data.get('entities', {}).items():
    if 'pillars' in entity:
        slots = []
        for p in entity['pillars']:
            if ':' in p:
                slots.append(p.split(':')[0].strip())
            else:
                slots.append(p)
        entity['slots'] = slots
        del entity['pillars']

with open('config/wads/arcana_novai/entities.yaml.migrated', 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
print('Migrated file written to entities.yaml.migrated')
"
```

**Then**: Review `entities.yaml.migrated`, replace original.

**Verification**: `python3 -c "from omega.oracle import EntityRegistry; r=EntityRegistry(); print(r.list_node_keepers()[0].slots)"`

### 3.2 Update Entity Soul Files

**Files**: 
- `data/entities/researcher/soul.yaml`
- `data/entities/sophia/soul.yaml`
- `data/entities/movie-expert/soul.yaml`

```yaml
# BEFORE:
pillars:
  - Researcher

# AFTER:
slots:
  - Researcher
```

For Sophia and movie-expert (Unknown):
```yaml
# BEFORE:
pillars:
  - Unknown

# AFTER:
slots: []
```

---

## 📦 Phase 4: Active Docs Update (30 min)

### 4.1 Update `docs/team/STATUS_OPUS.md`

**Lines 78, 81, 120**: Change `pillars: []` → `slots: []`

### 4.2 Update `docs/DOC_CLEANUP_AUDIT.md`

**Line 142**: Change "verify pillar slots" → "verify slot assignments"

**Note**: DO NOT modify:
- `docs/decisions/PIVOT_LOG_CANONICAL.md` — immutable decision record
- `docs/decisions/PIVOT_LOG_ARCHIVE_*.md` — archives
- `docs/intake/*` — intake/historical

---

## 📦 Phase 5: Temple-Grade Verification (30 min)

### 5.1 Run Full Test Suite
```bash
make test
# Must show: 276+ passed, 0 failed
```

### 5.2 Run Temple-Grade Gates
```bash
make temple-grade
# Must pass T1-T11 (T11 exempt per M13)
```

### 5.3 Verify Setup Script
```bash
bash scripts/setup.sh
# Must complete without AttributeError
# Must show "Node Keepers: X" and "slots: ..."
```

### 5.4 Verify MCP Hub Tool
```bash
# Start hub (if not running)
# Call oracle_list_node_keepers via MCP client
# Verify response has "slot" field, not "pillar"
```

### 5.5 Verify Entity Registry
```bash
python3 -c "
from omega.oracle import EntityRegistry
r = EntityRegistry()
print(f'Entities: {r.count()}')
print(f'Node Keepers: {len(r.list_node_keepers())}')
for e in r.list_node_keepers()[:3]:
    print(f'  {e.name}: slots={e.slots}')
"
```

---

## 🚨 ROLLBACK PLAN

If any phase breaks `make test` or `make temple-grade`:

1. **Git stash** changes: `git stash`
2. **Verify baseline**: `make test` passes
3. **Re-apply incrementally**: Apply one file at a time, run tests after each
4. **Escalate**: Page Kali if blocked > 30 min

---

## 📋 SIGN-OFF CRITERIA

| Gate | Criteria | Verification |
|------|----------|--------------|
| **Phase 1** | `scripts/setup.sh` runs clean | Manual run |
| **Phase 2** | `make test` 100% pass | CI / local |
| **Phase 3** | WAD entities load with `slots` | Registry inspection |
| **Phase 4** | Active docs updated | Grep for "pillar" in active docs |
| **Phase 5** | `make temple-grade` passes | CI gate |

**Final Sign-Off**: Kali approval via Hivemind post with `intent="approval"`

---

## 📝 DECISION LOG (This Refactor)

| Decision | Description | Trace |
|----------|-------------|-------|
| D-XXX | Rename `oracle_list_pillar_keepers` → `oracle_list_node_keepers` | trc_pillar_refactor_001 |
| D-XXX | Change MCP response `pillar` → `slot`, `pillar_keeper` → `node_keeper` | trc_pillar_refactor_002 |
| D-XXX | Update `scripts/setup.sh` to use `list_node_keepers()` and `result.slots` | trc_pillar_refactor_003 |
| D-XXX | Migrate WAD `entities.yaml` from `pillars:` to `slots:` | trc_pillar_refactor_004 |
| D-XXX | Update all test assertions from `pillar`/`pillars` to `slots` | trc_pillar_refactor_005 |

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_mining ⬡ PLAN READY*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
