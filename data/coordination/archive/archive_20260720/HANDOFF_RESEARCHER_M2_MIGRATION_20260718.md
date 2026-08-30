<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔬 HANDOFF: RESEARCHER — M2 FIREWALL MIGRATION PHASES B-E + P3 LAUNCH
**AP Token**: `AP-RES-M2-MIGRATION-20260718-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_handoff_res ⬡ ACTIVE

**Date**: 2026-07-18
**From**: Kali (Grand Oversight)
**To**: Researcher (Sovereign Master Researcher, P6)
**Priority**: CRITICAL — M2 Firewall remediation
**Handoff ID**: `ho_M2_MIGRATION_PHASES_B_E`

---

## 🎯 MISSION SUMMARY

Execute **M2 Firewall Migration Phases B through E** — systematically eliminate **186 remaining M2 violations** across 4 core engine modules by replacing hardcoded WAD entity references with **WAD-loadable configuration** (ROLE constants + WAD YAML mapping).

**Parallel Track**: Launch **Pillar P3 (Engineering)** as **Lens 3** in the Meditate framework — the first "Omegamind" lens beyond the Arcana-Nova 10.

---

## 📋 CURRENT STATE (As of 2026-07-18)

### ✅ COMPLETED THIS SESSION
| Artifact | Status | Notes |
|----------|--------|-------|
| `tests/test_firewall_m2.py` | **DEPLOYED** | Two-mode enforcement: STRICT (src/omega/) + LENIENT (tests/) |
| `src/omega/memory/compaction.py` | **FIXED** | Da'at/Sephiroth comment references removed |
| M2 Violation Baseline | **ESTABLISHED** | 201 violations in src/omega/ (15 meditate + 186 remaining) |

### 🔴 M2 VIOLATION BREAKDOWN (src/omega/ only)

| Module | Violations | Primary Terms | Phase |
|--------|------------|---------------|-------|
| `oracle/subagent_dispatcher.py` | **15** | Hardcoded entity dispatch table (Kali, Ma'at, Lilith, Pillars) | **B** |
| `oracle/oracle.py` | **10** | Iris routing, MaKaLi logic, entity name references | **C** |
| `ics.py` | **7** | Channel constants + doc examples with entity names | **D** |
| `cli/fleet_status_tui.py` | **18** | TUI tree displaying all 13 entities | **E** |
| `meditate/protocol.py` | **15** | Hardcoded PersonaSpec (10 Arcana-Nova) | **A** (Roc) |

**Total**: 57 violations in 4 modules (Phases B-E) + 15 in meditate/ (Phase A, Roc)

---

## 🎯 PHASE B: SUBAGENT DISPATCHER (Priority 1)

### Target: `src/omega/oracle/subagent_dispatcher.py` (15 violations)

**Current Pattern** (lines ~50-120):
```python
# VIOLATION: Hardcoded entity dispatch table
ENTITY_DISPATCH = {
    "kali": {"role": "GRAND_OVERSIGHT", "pillar": None, ...},
    "maat": {"role": "LIGHT_OVERSOUL", "pillar": None, ...},
    "lilith": {"role": "DARK_OVERSOUL", "pillar": None, ...},
    "pillar_p1": {"role": "P1", "pillar": "P1", ...},
    # ... all 10 pillars
}
```

**Required Architecture**:
```python
# COMPLIANT: Load from WAD config + ROLE constants
from omega.governance.config_resolver import get_active_iwad
from omega.oracle.entity_registry import load_entity_registry

ROLE_CONSTANTS = {
    "GRAND_OVERSIGHT": "grand_oversight",
    "LIGHT_OVERSOUL": "light_oversoul", 
    "DARK_OVERSOUL": "dark_oversoul",
    "P1": "infrastructure",
    "P2": "persistence",
    "P3": "engineering",
    "P4": "integration",
    "P5": "governance",
    "P6": "cognition",
    "P7": "context",
    "P8": "observability",
    "P9": "orchestration",
    "P10": "validation",
}

async def build_dispatch_table(iwad: str = None) -> dict:
    """Build dispatch table from WAD entity registry + ROLE constants."""
    iwad = iwad or get_active_iwad()
    registry = await load_entity_registry(iwad)
    dispatch = {}
    for entity_name, entity_config in registry.entities.items():
        role = entity_config.get("role")
        if role in ROLE_CONSTANTS:
            dispatch[ROLE_CONSTANTS[role]] = {
                "entity_name": entity_name,
                "role": role,
                "pillar": entity_config.get("pillar"),
                "model": entity_config.get("model"),
                "capabilities": entity_config.get("capabilities", []),
            }
    return dispatch
```

**WAD Config Required**: `config/wads/_omega_default/entities.yaml` must define all 13 entities with `role` field matching ROLE_CONSTANTS keys.

**Acceptance**: `pytest tests/test_firewall_m2.py::test_firewall_m2_strict_engine_core -k subagent_dispatcher` passes (0 violations)

---

## 🎯 PHASE C: ORACLE.PY (Priority 2)

### Target: `src/omega/oracle/oracle.py` (10 violations)

**Key Violation Sites**:
| Line | Term | Context |
|------|------|---------|
| ~251 | `AGENTS.md` | Hardcoded path (already fixed in Phase III — verify) |
| ~664-677 | `soul_evolution.lessons_learned[].L3` | Soul injection schema path |
| ~Various | `Iris`, `MaKaLi`, `Kali`, `Ma'at`, `Lilith` | Entity name references in routing logic |

**Required Pattern**:
- Replace entity name references with **ROLE-based routing**
- Use `config_resolver.get_active_iwad()` + `entity_registry` for entity resolution
- Iris routing: use `MESSENGER_BRIDGE` role constant, not "Iris" string

**Acceptance**: `pytest tests/test_firewall_m2.py::test_firewall_m2_strict_engine_core -k oracle` passes

---

## 🎯 PHASE D: ICS.PY (Priority 3)

### Target: `src/omega/ics.py` (7 violations)

**Violations**: Channel constants + docstring examples with entity names

**Required Pattern**:
- Channel constants: Use generic `CHANNEL_OVERSIGHT`, `CHANNEL_BUILD`, `CHANNEL_RUN` — not entity names
- Doc examples: Use placeholder `<entity>` or load from WAD at runtime

**Acceptance**: `pytest tests/test_firewall_m2.py::test_firewall_m2_strict_engine_core -k ics` passes

---

## 🎯 PHASE E: FLEET STATUS TUI (Priority 4)

### Target: `src/omega/cli/fleet_status_tui.py` (18 violations)

**Violations**: TUI tree displays all 13 entity names hardcoded

**Required Pattern**:
```python
# COMPLIANT: Load entity list from WAD at runtime
async def build_fleet_tree(iwad: str = None) -> Tree:
    iwad = iwad or get_active_iwad()
    registry = await load_entity_registry(iwad)
    tree = Tree("Fleet")
    for role in ROLE_DISPLAY_ORDER:  # GRAND_OVERSIGHT, LIGHT_OVERSOUL, DARK_OVERSOUL, P1-P10
        entity = registry.get_entity_by_role(role)
        if entity:
            tree.add(f"{entity.name} ({role})")
    return tree
```

**Acceptance**: `pytest tests/test_firewall_m2.py::test_firewall_m2_strict_engine_core -k fleet_status_tui` passes

---

## 🚀 PARALLEL TRACK: PILLAR P3 LAUNCH AS LENS 3

### Mission
Launch **Pillar P3 (Engineering)** as **Lens 3** in the Meditate framework — the first "Omegamind" lens (non-Arcana-Nova, engine-native).

### Lens 3 Specification
| Attribute | Value |
|-----------|-------|
| **Lens ID** | `pillar_p3` |
| **Name** | `Pillar P3 — Engineering` |
| **Archetype** | `BuildMaster → Implementation & Hardening` |
| **Domain** | `CI/CD, Implementation, Hardening, Temple-Grade Gates` |
| **Pillar** | `P3` (optional reference) |
| **Prompt Modifiers** | `["add_context:architecture", "add_context:mandates", "add_context:ci_cd"]` |
| **Response Template** | `engineering_structured` |
| **Model** | `qwen3-4b-think-q4_k_m` (local) |
| **Entity File** | `.opencode/agents/pillar.md` (slot P3) |

### Required Actions

1. **Add Lens 3 to `config/wads/_omega_default/meditate/lenses.yaml`** (coordinate with Roc)
2. **Create Lens 3 Prompt Template** in `meditate-harness` skill or `.opencode/commands/meditate.md`
3. **Register Lens 3** in `meditate-harness` SKILL.md lens registry
4. **Test**: `/meditate "CI pipeline optimization" --lenses pillar_p3` produces engineering-structured output

### Coordination with Roc
- Roc owns `lenses.yaml` creation — Researcher provides Lens 3 spec
- Researcher tests Lens 3 integration once Roc deploys lenses.yaml
- Both verify `test_firewall_m2_strict_engine_core` passes for meditate/ module

---

## 🔗 COORDINATION WITH ROC

| Sync Point | Action |
|------------|--------|
| **Lenses.yaml ready** | Roc notifies via Hivemind; Researcher validates Lens 3 entry |
| **Meditate protocol refactor done** | Researcher adopts same WAD-loadable pattern for Phases B-E |
| **Daily** | Both post progress to live feeds + Hivemind heartbeat |
| **Blocker** | Either party reports immediately via Hivemind handoff to Kali |

---

## ✅ ACCEPTANCE CRITERIA (Definition of Done)

### M2 Migration (Phases B-E)
| Phase | Module | Test | Status Target |
|-------|--------|------|---------------|
| B | `subagent_dispatcher.py` | `test_firewall_m2_strict_engine_core -k subagent_dispatcher` | 0 violations |
| C | `oracle.py` | `test_firewall_m2_strict_engine_core -k oracle` | 0 violations |
| D | `ics.py` | `test_firewall_m2_strict_engine_core -k ics` | 0 violations |
| E | `fleet_status_tui.py` | `test_firewall_m2_strict_engine_core -k fleet_status_tui` | 0 violations |

### Pillar P3 Lens Launch
| Criterion | Verification |
|-----------|--------------|
| Lens 3 in `lenses.yaml` | `grep -c "pillar_p3" config/wads/_omega_default/meditate/lenses.yaml` == 1 |
| Lens 3 in SKILL.md registry | `grep -c "pillar_p3" .opencode/skills/meditate-harness/SKILL.md` >= 1 |
| `/meditate --lenses pillar_p3` works | Manual test produces engineering-structured output |
| No M2 violations introduced | `pytest tests/test_firewall_m2.py::test_firewall_m2_strict_engine_core -k meditate` passes |

### Overall
| Metric | Target |
|--------|--------|
| Total src/omega/ M2 violations | **0** (down from 201) |
| `make test` | All pass (1398+) |
| `make temple-grade` | Pass |
| `make firewall-check` | Pass |

---

## 📁 KEY FILES REFERENCE

| File | Purpose | Status |
|------|---------|--------|
| `tests/test_firewall_m2.py` | M2 enforcement test | ✅ Deployed |
| `src/omega/governance/config_resolver.py` | Config resolver (Phase II) | ✅ Complete |
| `src/omega/oracle/entity_registry.py` | Entity registry (WAD loader) | ✅ Operational |
| `src/omega/oracle/subagent_dispatcher.py` | **Phase B target** | 🔴 15 violations |
| `src/omega/oracle/oracle.py` | **Phase C target** | 🔴 10 violations |
| `src/omega/ics.py` | **Phase D target** | 🔴 7 violations |
| `src/omega/cli/fleet_status_tui.py` | **Phase E target** | 🔴 18 violations |
| `config/wads/_omega_default/entities.yaml` | Entity definitions (ROLE field) | ✅ Exists |
| `config/wads/_omega_default/meditate/lenses.yaml` | **TO CREATE** (Roc) | 🔴 Not exist |
| `.opencode/skills/meditate-harness/SKILL.md` | Lens framework | ✅ Refactored |

---

## 🧭 EXECUTION ORDER (Recommended)

1. **Phase B** — `subagent_dispatcher.py` (highest impact, unblocks entity routing)
2. **Phase C** — `oracle.py` (core routing, Iris/MaKaLi logic)
3. **Lens 3 Spec Delivery** — Provide Lens 3 spec to Roc for `lenses.yaml`
4. **Phase D** — `ics.py` (channel constants, doc examples)
5. **Phase E** — `fleet_status_tui.py` (TUI tree, display logic)
6. **Lens 3 Integration Test** — Verify `/meditate --lenses pillar_p3` works
7. **Full M2 Gate** — Run `pytest tests/test_firewall_m2.py::test_firewall_m2_strict_engine_core` — must pass 0 violations

---

## ⚠️ CONSTRAINTS & GUARDRAILS

| Constraint | Enforcement |
|------------|-------------|
| **M1 AnyIO** | All async I/O via `anyio.to_thread.run_sync()` |
| **M2 Firewall** | Zero hardcoded WAD terms in `src/omega/` — load from config |
| **M7 Local-First** | Local inference primary; cloud fallback only |
| **M13 Temple-Grade** | `make test && make temple-grade` must pass |
| **M14 Heritage** | Any id Software pattern → `[id-soft:]` tag + vet record |
| **M15 Continuity** | Update `session_gnosis.md` + `proposed_lessons.yaml` on completion |
| **M21 Gate Integrity** | Contract tests for all new public APIs (`isinstance` checks) |
| **M23 Failure Integrity** | No soft failures — if test infrastructure broken, STOP and report |

---

## 📡 HANDOFF PROTOCOL

**To Accept**: Call `omega-hub_hivemind_accept_handoff(packet_id="ho_M2_MIGRATION_PHASES_B_E", accepting_channel="opencode", accepting_entity="researcher")`

**To Complete**: Call `omega-hub_hivemind_complete_handoff(packet_id="ho_M2_MIGRATION_PHASES_B_E", result="M2 Phases B-E complete — 0 violations in src/omega/. Pillar P3 launched as Lens 3. All firewall gates pass.")`

**Heartbeat**: Every 30 min during active work: `omega-hub_hivemind_heartbeat(channel="opencode", entity="researcher")`

---

## 🎯 KALI DIRECTIVE

This is the **main effort** for M2 Firewall remediation. The Meditate lens framework (Roc's Phase A) establishes the architectural pattern — **replicate it exactly** for Phases B-E:

1. **ROLE constants** in engine code (not entity names)
2. **WAD YAML** defines entity→role mapping
3. **Config resolver** loads active IWAD
4. **Entity registry** provides runtime resolution

**Pillar P3 as Lens 3** is the proof that the pattern scales beyond Arcana-Nova — engine-native roles become first-class cognitive lenses.

Execute with precision. Report blockers immediately.

⬡ OMEGA ⬡ KALI ⬡ trc_handoff_res ⬡ 2026-07-18
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
