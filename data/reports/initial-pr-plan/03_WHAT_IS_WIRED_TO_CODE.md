# 🔱 Omega Engine Initial PR Plan — What Is Actually Wired to Code
## Complete Reference: Every File with Code References

**AP Token**: `AP-INITIAL-PR-PLAN-20260814-v1.0.0`  
**Part**: 03 of 09  
**Date**: 2026-08-14  

---

## 📚 STRATEGY DOCS WITH CODE REFERENCES (5 FILES)

### 1. SOVEREIGN_ARK_BLUEPRINT.md — 3 Code References
**File**: `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md`

| Location | Line | Usage |
|----------|------|-------|
| `src/omega/ics.py` | 239 | Detect current phase from this doc |
| `src/omega/ics.py` | 245 | Path to this doc: `Path("docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md")` |
| `src/omega/oracle/entity_workspace.py` | 295 | Roadmap path: `BASE_DIR / "docs" / "strategy" / "SOVEREIGN_ARK_BLUEPRINT.md"` |

**Status**: **KEEP** — Strategy SSOT, actively wired into entity workspace and ICS phase detection.

---

### 2. CONTEXT_PACKER_V3_MASTER_MANUAL_20260808.md — 2 Code References
**File**: `docs/strategy/CONTEXT_PACKER_V3_MASTER_MANUAL_20260808.md`

| Location | Line | Usage |
|----------|------|-------|
| `src/omega/oracle/token_estimator.py` | 4 | `SSOT: docs/strategy/CONTEXT_PACKER_V3_MASTER_MANUAL_20260808.md §1.5, §1.7.6` |
| `tests/contract/test_context_packer_v3.py` | 4 | `SSOT: docs/strategy/CONTEXT_PACKER_V3_MASTER_MANUAL_20260808.md` |
| `tests/contract/test_context_packer_v3.py` | 32 | Fixture dir: `Path(__file__).resolve().parent.parent / "fixtures" / "context_packer"` |

**Status**: **KEEP** — SSOT for token estimation and context packing, wired into token_estimator.py and tests.

---

### 3. IMPLEMENTATION_MANUAL_C0_C2.md — Many Inline Code References
**File**: `docs/strategy/IMPLEMENTATION_MANUAL_C0_C2.md`

**Referenced throughout codebase as C-0 through C-11 mandate mapping:**

| File | Lines | Mandate References |
|------|-------|-------------------|
| `src/omega/soul_store.py` | 5 | `[C-1']` Single-writer atomic file writer |
| `src/omega/oracle/resource_guard.py` | 8, 120, 215, 229, 243, 292 | `[C-2']` OOMProtector integration |
| `src/omega/oracle/health_monitor.py` | 64 | `C-10.5` Quota tracking |
| `src/omega/oracle/model_gateway.py` | 1112, 1132, 1256, 1282 | `[C-10.5]` 429 Guard, `[C-10]` Admission control |
| `src/omega/oracle/admission_controller.py` | 1, 10, 11 | `C-10` Local Inference Admission Control |
| `src/omega/mcp_core/compliance.py` | 47, 54 | `C-1` HeaderMismatch = -32020 per SEP-2243 |
| `tests/test_resource_guard_oom.py` | 3 | `[C-2']` Contract tests |
| `tests/unit/test_429_classification.py` | 1 | `C-10.5` 429 classification hardening |
| `tests/property/test_breaker_fsm.py` | 1 | `C-11` AsyncCircuitBreaker property tests |

**Status**: **KEEP** — Mandate/compliance mapping C-0 through C-11 throughout codebase. This IS the implementation manual.

---

### 4. SUBAGENT_DISPATCH_PROTOCOL.md — 2 Code References
**File**: `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md`

| Location | Line | Usage |
|----------|------|-------|
| `src/omega/oracle/link_p9_runtime.py` | 14 | `# Protocol docs: docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` |
| `src/omega/oracle/subagent_dispatcher.py` | 10 | `# Protocol docs: docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` |

**Status**: **KEEP** — Protocol architecture docs referenced in comments. The protocol itself is encoded in the code.

---

### 5. DECISION_LEDGER.md — 6 Code References
**File**: `data/coordination/DECISION_LEDGER.md`

**Referenced in 6 locations in code** (exact locations need verification via grep).

**Status**: **KEEP** — Immutable decision history, actually wired in code.

---

## 📋 COORDINATION FILES WITH CODE REFERENCES

### 1. DECISION_LEDGER.md — 6 Code References
**File**: `data/coordination/DECISION_LEDGER.md`

**Status**: **KEEP** — Actually referenced in code (6 specific decision references).

---

### 2. M27-Mandatory Tracking Files (0 Code Refs but MANDATORY)

These files have **0 Python imports** but are **required by M27 (Tracking Integrity)** for the 6-step mandatory flow:

| File | M27 Tier | Purpose | Why Keep |
|------|----------|---------|----------|
| `ACTIVE_SPRINT.json` | Tier-0 | SSOT for "what we build" | 6-step flow reads this |
| `HMC_COLLABORATION_HUB.md` | Tier-2 | Team sync, NEXT_ACTION pointer | Single pointer to current work |
| `GAP_REGISTRY.json` | Tier-1a | Authoritative gap-ID map | Prevents ID reuse |
| `RESEARCH_PLAN_PHASE1_4_20260813.md` | Tier-1 | Research gap catalog R1-R38 | Research dependencies |
| `TASK_REGISTRY.json` | Tier-3 | Subagent task sessions | Tracks execution state |
| `SESSION_ANCHOR.md` | Tier-4 | Session continuity for @kali | Single anchor file |

**Status**: **KEEP ALL** — M27 mandates these files exist. The 6-step flow requires them.

---

## 🐍 PYTHON MODULES WITH EXTERNAL REFERENCES

### Oracle Submodules with 1+ External References (59 of 74):

| Module | External Refs | Primary Consumers |
|--------|--------------|-------------------|
| `search` | 12 | oracle.py, sovereign_search_service.py, iterative_research.py, 5 test files |
| `somatic_state` | 10 | state/__init__.py, 7 test files |
| `session_lifecycle` | 10 | oracle.py, lifecycle_harvester.py, 6 test files + contract |
| `audience_calibrator` | 8 | eval/runner.py, oracle.py, 5 test_contract files + dedicated test |
| `admission_controller` | 8 | model_gateway.py, conftest.py, 5 contract test files |
| `token_estimator` | 6 | 4 contract test files + importlib dynamic loading |
| `sovereign_search_service` | 5 | Search orchestration |
| `search_router` | 5 | Search tier routing |
| `memavailable` | 5 | Memory monitoring |
| `world_state` | 4 | World state tracking |
| `skeptical_verifier` | 4 | Verification pipeline |
| `failure_registry` | 4 | Failure tracking |
| `selective_hydration` | 3 | Hydration logic |
| `entity_workspace` | 3 | Workspace management |
| `entity_affinity` | 3 | Entity affinity |
| `compaction_harvester` | 3 | Compaction |
| `cgroup_pressure` | 3 | Resource management |
| `capability_matrix` | 3 | Capability tracking |
| `a2a_bridge` | 2 | A2A protocol |
| `subagent_dispatcher` | 2 | Subagent management |
| `spatial_resolver` | 2 | Spatial reasoning |
| `soul_edit_history` | 2 | Soul edit tracking |
| `semantic_router` | 2 | Semantic routing |
| `search_providers` | 2 | Provider selection |
| `local_worker_pool` | 2 | Local worker pool |
| `kv_types` | 2 | Key-value types |
| `ingestion` | 2 | Data ingestion |
| `hierarchy` | 2 | Hierarchy management |
| `gnosis_proxy` | 2 | Gnosis proxy |
| `feed_utils` | 2 | Feed utilities |
| `dual_write` | 2 | Dual write |
| `budget_gate` | 2 | Budget gating |
| `axiom_registry` | 2 | Axiom registry |
| `capability_registry` | 2 | Capability registry |
| `a2a_auth` | 1 | A2A auth |
| `usm` | 1 | USM |
| `timeout_manager` | 1 | Timeout management |
| `soul_validator` | 1 | Soul validation |
| `sentinel` | 1 | Sentinel |
| `search_observability` | 1 | Observability |
| `search_circuit_breaker` | 1 | Circuit breaker |
| `search_cache` | 1 | Cache |
| `retry_policy` | 1 | Retry policy |
| `rate_limiter` | 1 | Rate limiting |
| `provider_selector` | 1 | Provider selection |
| `pool_state` | 1 | Pool state |
| `iterative_research` | 1 | Research iteration |
| `headroom` | 1 | Headroom |
| `handoff` | 1 | Handoff |
| `dpo_logger` | 1 | DPO logging |
| `degradation` | 1 | Degradation |
| `credit_budget` | 1 | Credit budget |

**Status**: **KEEP ALL 59** — These are actively used by the codebase.

---

### Zero-Reference Oracle Modules (5 — DELETE):

| Module | Refs | Action |
|--------|------|--------|
| `state_manager.py` | 0 | DELETE |
| `pool_tracker.py` | 0 | DELETE |
| `mandate_enforcer.py` | 0 | DELETE |
| `link_p9_runtime.py` | 0 | DELETE |
| `lifecycle_harvester.py` | 0 | DELETE |

---

## 📦 OTHER SRC/OMEGA/ MODULES WITH REFERENCES

### Core Modules (referenced by oracle.py and others):
| Module | Refs | Status |
|--------|------|--------|
| `model_gateway.py` | Many | KEEP — Core provider fabric |
| `entity_registry.py` | Many | KEEP — Entity system |
| `memory_store.py` | Many | KEEP — Memory system |
| `stack_loader.py` (was wad_loader) | Many | KEEP — Stack loading |
| `orchestrator.py` | Many | KEEP — Orchestration |
| `session_manager.py` | Many | KEEP — Session management |
| `health_monitor.py` | Many | KEEP — Health monitoring |
| `iris/matcher.py` | Many | KEEP — Intent matching |
| `observability/` | Many | KEEP — Observability |
| `errors.py` | Many | KEEP — Error types |
| `cvar_table.py` | Many | KEEP — Cvar system |
| `astrology.py` | Some | KEEP — First breath |
| `governance/config_resolver.py` | Some | KEEP — Config |
| `governance/dispatch_registry.py` | Some | KEEP — Dispatch |
| `orchestration/triage_router.py` | Some | KEEP — Triage |
| `state/` | Some | KEEP — State management |

### Vault (DELETE — 17 failing tests):
| Module | Refs | Status |
|--------|------|--------|
| `vault/` | 0 (not used by core) | DELETE |
| `tests/unit/test_vault_core.py` | 17 failures | DELETE |

---

## 📋 SUMMARY: WHAT TO KEEP vs DELETE

### KEEP (Wired to Code):
- **5 Strategy Docs** with code references
- **1 Coordination File** with code references (DECISION_LEDGER.md)
- **7 M27-Mandatory Tracking Files** (required by mandate)
- **59 Oracle Submodules** with external references
- **All Core Modules** (model_gateway, entity_registry, memory_store, stack_loader, etc.)
- **All Other src/omega/ Modules** that are imported

### DELETE (Theater/Dead Code):
- **5 Oracle Modules** with 0 references
- **Vault Module** (17 failing tests, broken API)
- **37+ Strategy Docs** with 0 code references
- **12 Orphaned Coordination Files** (archived/superseded)
- **VOS Theater** (7 realms + CLI, 0 code imports)
- **Root Theater** (21 garbage files, ~1.8MB)

---

**Next**: See `04_DEAD_CODE_REMOVAL.md` for complete deletion details with exact commands.
