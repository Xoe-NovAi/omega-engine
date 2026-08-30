<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Pillar Leak Audit — M2 Engine-Stack Firewall Boundary Violation Inventory
**AP Token**: `AP-ROC_RACOON-PILLAR-AUDIT-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_mining ⬡ ACTIVE

**Date**: 2026-08-22
**Mission**: Complete codebase audit of pillar/WAD concept leaks into Engine core
**Canonical Ruling**: D180 / PIVOT_LOG_CANONICAL.md §1200-1210

---

## 📋 Executive Summary

| Category | Violations Found | Status |
|----------|------------------|--------|
| **Core Engine (src/omega/)** | 0 | ✅ CLEAN — Already migrated to `slots`/`metadata` |
| **MCP Hub/Tools** | 12 | ❌ CRITICAL — `oracle_list_pillar_keepers`, `pillar` field in responses |
| **Config/WADs** | 1 (entities.yaml) | ⚠️ WAD CONTENT — Correctly in WAD, but uses legacy `pillars:` field |
| **Tests** | 8 | ❌ NEEDS UPDATE — Tests assert `pillar`/`pillars` fields |
| **Docs** | 15+ | ⚠️ HISTORICAL — Mostly in decisions/archive, some active docs reference |
| **Scripts** | 3 | ❌ CRITICAL — `setup.sh` calls `list_pillar_keepers()`, accesses `result.pillar` |
| **Entity Soul Files** | 3 | ⚠️ WAD METADATA — `pillars:` in soul.yaml (entity workspace, not engine) |

**Total Active Violations (Engine + Hub + Scripts + Tests)**: **23 locations requiring refactor**

---

## 🔴 CORE ENGINE (src/omega/) — ✅ CLEAN

The Engine core has **already been migrated** per D180. No active violations found.

| File | Line | Finding | M2 Violation? | Status |
|------|------|---------|---------------|--------|
| `src/omega/oracle/entity_registry.py` | 160 | `slots: List[str]` — Engine field (replaces `pillars`) | N | ✅ Migrated |
| `src/omega/oracle/entity_registry.py` | 167 | `metadata: Dict[str, Any]` — Opaque WAD bag (replaces `traits`) | N | ✅ Migrated |
| `src/omega/oracle/entity_registry.py` | 395 | `metadata` in `core_fields` — prevents recursive nesting | N | ✅ Migrated |
| `src/omega/oracle/entity_registry.py` | 399 | `wad_metadata = {k: v for k, v in raw.items() if k not in core_fields}` | N | ✅ Migrated |
| `src/omega/oracle/entity_registry.py` | 404-419 | Auto-migration: `nodes:` → `slots:` on load | N | ✅ Migrated |
| `src/omega/oracle/entity_registry.py` | 598-606 | `list_node_keepers()` — forward-compat alias (not `list_pillar_keepers`) | N | ✅ Migrated |
| `src/omega/oracle/entity_registry.py` | 800-840 | `find_by_domain()` — no pillar gate (D179 removed) | N | ✅ Migrated |
| `src/omega/oracle/oracle.py` | 129 | `OracleResponse.slots: Optional[List[str]]` — not `pillars` | N | ✅ Migrated |
| `src/omega/oracle/oracle.py` | 119-122 | Docstring: "WAD-specific display fields in Entity.metadata" | N | ✅ Migrated |
| `src/omega/oracle/subagent_dispatcher.py` | 194, 224 | Comments: "WADs provide ENTITIES that fill those slots" | N | ✅ Migrated |
| `src/omega/iris/server.py` | 47, 85, 112, 133 | `ChatResponse.slots: list[str]` — not `pillars` | N | ✅ Migrated |

**Note**: The `__getattr__` proxy at line 237-246 in `entity_registry.py` provides backward compatibility for legacy code accessing `entity.element`, `entity.chakra`, etc. via `entity.metadata`. This is intentional for migration compatibility.

---

## 🔴 MCP HUB / TOOLS (mcp_servers/omega_hub/) — ❌ CRITICAL VIOLATIONS

| File | Line | Finding | M2 Violation? | Refactor Action |
|------|------|---------|---------------|-----------------|
| `mcp_servers/omega_hub/server.py` | 142 | Tool registration: `"oracle_list_pillar_keepers"` | **Y** | Rename tool to `oracle_list_node_keepers` |
| `mcp_servers/omega_hub/server.py` | 298 | `"pillar_slot": desc.get("pillar_slot")` in entity description | **Y** | Change to `slot` or remove |
| `mcp_servers/omega_hub/hub_tools/tools.py` | 529 | `@m9_safe("oracle_list_pillar_keepers")` decorator | **Y** | Rename to `oracle_list_node_keepers` |
| `mcp_servers/omega_hub/hub_tools/tools.py` | 531 | `async def oracle_list_pillar_keepers()` function name | **Y** | Rename to `oracle_list_node_keepers` |
| `mcp_servers/omega_hub/hub_tools/tools.py` | 542 | `entities = await anyio.to_thread.run_sync((await registry).list_pillar_keepers)` | **Y** | Call `list_node_keepers()` instead |
| `mcp_servers/omega_hub/hub_tools/tools.py` | 546 | Returns `"metadata": e.metadata` with comment "WAD content: element, chakra, planet, sigil" | **Y** | Keep metadata pass-through; update comment |
| `mcp_servers/omega_hub/hub_tools/tools.py` | 1288 | `"pillar": None` in entity_identity dict | **Y** | Remove or change to `slot` |
| `mcp_servers/omega_hub/hub_tools/tools.py` | 1293 | `entity_identity["type"] = "pillar_keeper" if entity_reg.slots else "entity"` | **Y** | Change `"pillar_keeper"` → `"node_keeper"` |
| `mcp_servers/omega_hub/hub_tools/tools.py` | 1297 | `entity_identity["pillar"] = entity_reg.slots[0]` | **Y** | Change key to `"slot"` |
| `mcp_servers/omega_hub/hub_tools/tools.py` | 3343 | Docstring: `"list_pillar_keepers: List entities with slot assignments"` | **Y** | Update docstring |
| `mcp_servers/omega_hub/hub_tools/tools.py` | 3346 | `action: "assess_intent|discover_entity|list_pillar_keepers"` | **Y** | Update action name |
| `mcp_servers/omega_hub/hub_tools/tools.py` | 3354 | `valid_actions = {"assess_intent", "discover_entity", "list_pillar_keepers"}` | **Y** | Update set |
| `mcp_servers/omega_hub/hub_tools/tools.py` | 3394 | `elif action == "list_pillar_keepers":` | **Y** | Update condition |

**Archive copies (already superseded, but present in repo):**
- `docs/hardening/omega-hub/claude-project/outbox/server-snapshot.py` — lines 721, 723, 730, 733, 761, 823, 1462, 1467, 1470, 1471, 3001
- `docs/hardening/omega-hub/server_monolith_snapshot_20260613.py` — same lines
- `data/entities/roc_racoon/workspace/hlmc_ore/gap4_mcp_auth/hub_server.py` — lines 142, 143

---

## 🟡 CONFIG / WADS — ⚠️ WAD CONTENT (Correct Location, Legacy Format)

| File | Line | Finding | M2 Violation? | Refactor Action |
|------|------|---------|---------------|-----------------|
| `config/wads/arcana_novai/entities.yaml` | 26, 58, 91, 129, 162, 199, 232, 272, 306, 343, 376, 416, 449, 489, 523, 564, 598, 637, 670, 712, 748, 799, 822, 909, 984, 1009, 1112, 1180, 1217, 1273, 1307, 1329, 1362, 1384, 1417, 1439, 1473, 1495, 1529, 1551, 1585, 1607, 1640, 1662, 1696, 1718, 1752, 1774, 1805, 1824, 1859, 1881, 1926, 1948, 2003, 2025, 2078, 2100, 2159, 2183 | **~70 entities** use `pillars:` field (e.g., `pillars: ['P1: Flesh']`) | **N** (WAD content) | **Migration needed**: Change `pillars:` → `slots:` in YAML; engine auto-migrates on load (line 404-419) |
| `config/wads/arcana_novai/hierarchy.yaml` | 55, 68 | `governs_pillars: [P1, P2, P3, P4, P5]` / `[P6, P7, P8, P9, P10]` | **N** (WAD content) | Keep — this is WAD governance metadata |
| `config/wads/omega_research/sandboxes/ml_training.yaml` | 7 | `pillar: "P6"` | **N** (WAD content) | Keep — WAD-specific |

**Note**: The `entities.yaml` in the WAD is the **correct place** for pillar definitions. The engine auto-migrates `pillars:` → `slots:` on load (see `entity_registry.py:404-419`). However, for cleanliness and to avoid confusion, the WAD should be updated to use `slots:` directly.

---

## 🔴 TESTS — ❌ NEEDS UPDATE

| File | Line | Finding | M2 Violation? | Refactor Action |
|------|------|---------|---------------|-----------------|
| `tests/test_hivemind.py` | 315 | `assert payload["entity"]["pillar"] == "P7"` | **Y** | Change to `slots` or `slot` |
| `tests/test_rag_router.py` | 25 | Query: "Compare the 23 Sovereign Mandates across all pillars" | **N** (test data) | Update query text |
| `tests/contracts/test_mandate_auditor.py` | 271 | `test_m3_detects_iris_in_pillar` — test name | **Y** | Rename test to `test_m3_detects_iris_in_slot` |
| `tests/contracts/test_mandate_auditor.py` | 277 | Comment: "Violation: MESSENGER_BRIDGE role with a pillar_slot" | **Y** | Update comment |
| `tests/contracts/test_mandate_auditor.py` | 283 | Test data: `"purpose: Test messenger in pillar"` | **Y** | Update test data |
| `tests/contracts/test_mandate_auditor.py` | 294 | `test_m3_passes_when_iris_not_in_pillar` — test name | **Y** | Rename test |
| `tests/contracts/test_mandate_auditor.py` | 300 | Comment: "iris is a messenger, not a pillar keeper" | **Y** | Update comment |
| `tests/contracts/test_dispatch_registry.py` | 49 | `test_dispatch_registry_get_entity_by_role_pillar` — test name | **Y** | Rename to `..._by_role_slot` |
| `tests/contracts/test_dispatch_registry.py` | 52 | `pillar = get_entity_by_role("N1")` — variable name | **Y** | Rename variable |
| `tests/contracts/test_dispatch_registry.py` | 55 | Comment: "Multiple entities have P1 role; verify pillar is among them" | **Y** | Update comment |
| `tests/test_a2a_bridge.py` | 603 | `sid = SPIFFEID.parse("spiffe://omega.local/entity/pillar/p6")` | **Y** | Change path to `entity/slot/p6` |
| `tests/test_a2a_bridge.py` | 605 | `assert sid.path == "entity/pillar/p6"` | **Y** | Update assertion |

---

## 🟡 DOCS — ⚠️ MOSTLY HISTORICAL / ARCHIVE

| File | Line | Finding | M2 Violation? | Refactor Action |
|------|------|---------|---------------|-----------------|
| `docs/team/STATUS_OPUS.md` | 78 | `pillars: []` in entities.yaml reference | **N** (historical) | Update to `slots: []` |
| `docs/team/STATUS_OPUS.md` | 81 | `pillar→pillars` bug fix reference | **N** (historical) | Keep as historical record |
| `docs/team/STATUS_OPUS.md` | 120 | `pillars: []` reference | **N** (historical) | Update to `slots: []` |
| `docs/team/COMMUNICATION_HUB.md` | 96 | "10/10 pillar subagents" | **N** (historical) | Keep as historical record |
| `docs/team/COMMUNICATION_HUB.md` | 224 | `pillar: personal` entity definition | **N** (historical) | Keep as historical record |
| `docs/team/COMMUNICATION_HUB.md` | 238 | `pillar → pillars` fix reference | **N** (historical) | Keep as historical record |
| `docs/team/COMMUNICATION_HUB.md` | 253 | `pillar: personal` reference | **N** (historical) | Keep as historical record |
| `docs/team/COMMUNICATION_HUB.md` | 259 | `pillar → pillars` fix reference | **N** (historical) | Keep as historical record |
| `docs/DOC_CLEANUP_AUDIT.md` | 142 | "verify pillar slots" | **N** (audit doc) | Update to "verify slot assignments" |
| `docs/positioning/FOR_TECHNICAL.md` | 28 | "four fundamental pillars" (architectural metaphor) | **N** (metaphor) | Keep — not engine concept |
| `docs/decisions/PIVOT_LOG_CANONICAL.md` | 130-1231 | Multiple references to pillar decoupling | **N** (decision log) | **DO NOT MODIFY** — immutable decision record |
| `docs/decisions/PIVOT_LOG_ARCHIVE_*.md` | Various | Historical pillar references | **N** (archive) | **DO NOT MODIFY** |
| `docs/intake/13x-low-level-council-review-*.md` | Many | `pillar_gate` references | **N** (intake/archive) | Keep — intake is historical |

**Active docs needing update**: `docs/team/STATUS_OPUS.md`, `docs/DOC_CLEANUP_AUDIT.md`

---

## 🔴 SCRIPTS — ❌ CRITICAL VIOLATIONS

| File | Line | Finding | M2 Violation? | Refactor Action |
|------|------|---------|---------------|-----------------|
| `scripts/setup.sh` | 107 | `print(f'  Pillar Keepers: {len(registry.list_pillar_keepers())}')` | **Y** | Change to `registry.list_node_keepers()` |
| `scripts/setup.sh` | 111 | `print(f'  Oracle test: {result.entity} — {result.pillar}')` | **Y** | Change to `result.slots` |
| `scripts/seed_knowledge.py` | 100 | `f"This is the primary knowledge repository for the {entity.title()} pillar."` | **Y** | Change to "slot" or "domain" |
| `scripts/mandate_gates.py` | 62, 71, 77, 79 | `iris_in_pillar` variable, "Pillar slots" in M3 check | **Y** | Rename to `iris_in_slot`, update messages |
| `scripts/validate_docs.py` | 68 | `"trc_pillar"` in trace ID list | **N** (trace ID) | Keep — trace IDs are immutable |

---

## 🟡 ENTITY SOUL FILES — ⚠️ WAD METADATA (Entity Workspace)

| File | Line | Finding | M2 Violation? | Refactor Action |
|------|------|---------|---------------|-----------------|
| `data/entities/researcher/soul.yaml` | 4-5 | `pillars: [Researcher]` | **N** (entity workspace) | Update to `slots: [Researcher]` or move to `metadata` |
| `data/entities/sophia/soul.yaml` | 4-5 | `pillars: [Unknown]` | **N** (entity workspace) | Update to `slots: []` or remove |
| `data/entities/movie-expert/soul.yaml` | 4-5 | `pillars: [Unknown]` | **N** (entity workspace) | Update to `slots: []` or remove |

**Note**: These are in `data/entities/<name>/soul.yaml` — entity-owned workspace files, NOT engine core. They are user/WAD metadata. However, for consistency with the new `slots` terminology, they should be updated.

---

## 📊 VIOLATION SUMMARY BY SEVERITY

| Severity | Count | Locations |
|----------|-------|-----------|
| **CRITICAL (Engine/Hub/Scripts runtime)** | 17 | MCP Hub tools (13), setup.sh (2), mandate_gates.py (4) |
| **HIGH (Tests)** | 12 | test_hivemind, test_mandate_auditor, test_dispatch_registry, test_a2a_bridge |
| **MEDIUM (WAD Config)** | 70+ | entities.yaml pillar fields (auto-migrated but should be cleaned) |
| **LOW (Docs/Archive)** | 20+ | Historical references, decision logs (immutable) |

---

## 🎯 REFACTOR PRIORITY ORDER

1. **P0 — Runtime Blockers** (must fix before any test passes):
   - `scripts/setup.sh` lines 107, 111 — breaks setup verification
   - `mcp_servers/omega_hub/hub_tools/tools.py` — `oracle_list_pillar_keepers` crashes (AttributeError)

2. **P1 — Test Suite** (must fix for `make test` to pass):
   - All test files listed above

3. **P2 — MCP Hub Tool Contract** (external API):
   - Rename `oracle_list_pillar_keepers` → `oracle_list_node_keepers`
   - Update all response fields (`pillar` → `slot`, `pillar_keeper` → `node_keeper`)

4. **P3 — WAD Cleanup** (cosmetic but important):
   - `config/wads/arcana_novai/entities.yaml` — change `pillars:` to `slots:`
   - `data/entities/*/soul.yaml` — update `pillars:` to `slots:`

5. **P4 — Docs** (non-blocking):
   - Active docs: `STATUS_OPUS.md`, `DOC_CLEANUP_AUDIT.md`
   - Archive/Decision logs: **DO NOT MODIFY**

---

## ✅ VERIFICATION CHECKLIST (Post-Refactor)

- [ ] `make test` passes (all 276+ tests)
- [ ] `scripts/setup.sh` runs without AttributeError
- [ ] `oracle_list_node_keepers` MCP tool works
- [ ] `OracleResponse.slots` populated correctly
- [ ] `EntityRegistry.list_node_keepers()` returns slot-holding entities
- [ ] `find_by_domain()` works for entities without slots
- [ ] `make temple-grade` passes (T1-T11)
- [ ] No `pillar` references in `src/omega/`, `mcp_servers/omega_hub/` (except comments)

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_mining ⬡ COMPLETE*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
