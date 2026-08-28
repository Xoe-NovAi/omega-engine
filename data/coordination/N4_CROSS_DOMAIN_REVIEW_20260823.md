# 🔱 N4 Cross-Domain Review Report
## MaKaLi Council Reports — Debut Hardening Review
**Session**: `ses_17a44db41698` · **Date**: 2026-08-23 · **Entity**: N4 bridge (maat)
**Charter**: `data/coordination/NODE_EXPERT_SESSIONS_PLAN.md` §4 (N4)
**Mandates**: M1, M2, M7, M13, M22, M25 (SOVEREIGN_MANDATES.md v3.8.0)

---

## Executive Summary

**Verdict: PROCEED WITH CONDITIONS**

The MaKaLi Council verdict is directionally correct but has **one critical API contract gap** (missing `RouteDecision` dataclass) and **three integration completeness gaps** (incomplete circuit breaker migration, dual admission gates, MIAP→Hivemind discontinuity) that must be resolved before DEL-1 Week 2 router collapse.

---

## 1. Router Collapse — API Contract Integrity

### 1.1 ProviderSelector as Single Router Authority
**Status**: ✅ **STABLE AND COMPLETE** `last_verified:2026-08-23`

- `ProviderSelector` at `src/omega/oracle/provider_selector.py:15` is the designated single router (93 lines)
- D-536 ratified: "One router: ProviderSelector + providers.yaml. Delete Triage + Semantic + RoutingTable"
- `ProviderSelector.get_ordered_providers()` called by `model_gateway.generate()` at lines 1153-1160
- Scoring: `(BasePriority * 10) - PII_Penalty - Latency_Penalty - Stability_Penalty` (lines 62-92)
- HealthMonitor integration via `self.health_monitor._breakers.get(provider.name)` (line 81)

### 1.2 RouteDecision Dataclass — **MISSING (CRITICAL GAP)**
**Status**: ❌ **NOT IMPLEMENTED**

- Referenced in DEBUT_REMEDIATION_MANUAL.md §2.4, ENGINE_DECISIONS_CONSOLIDATED.md as contract test requirement: "single `RouteDecision` (entity, model, provider, reason)"
- Was defined in DELETED `fleet_orchestrator.py:44` as `RouteDecision(Enum)` with values: SKIP, FALLBACK, ROUTE, BLOCK
- **No dataclass exists in surviving codebase** — this is the single biggest API contract gap for DEL-1 Week 2
- Required fields per docs: `entity`, `model`, `provider`, `reason`, `is_cloud`, `cost_warning`

### 1.3 oracle.py Imports That Break Post-Collapse
**Status**: ⚠️ **WILL BREAK** — must migrate in same PR as DEL-1 Week 2

| Import | Line | Usage | Migration Target |
|--------|------|-------|------------------|
| `SemanticRouter` | 31, 226-229, 1132-1137 | `_route_by_domain()` semantic routing | `EntityRegistry.find_by_domain()` + optional embed call |
| `TriageRouter` | 50-57, 233, 764 | `_select_model()` model selection | `ProviderSelector.get_ordered_providers()` + entity affinity |
| `RAGRouter` | 511-514 (per-turn in `talk()`) | Complexity classification | Advisory only — can remain if import guarded |

### 1.4 sovereign_search_service.py Circuit Breaker Migration
**Status**: ⚠️ **PARTIAL — INCOMPLETE**

- Lines 48-51: Still imports `initialize_circuit_breakers`, `TIER_CONFIGS` from deprecated `search_circuit_breaker`
- Lines 165-182: HealthMonitor migration implemented (`self._health_monitor.get_breaker()`)
- Lines 184-188: Still initializes old `circuit_breakers` registry if `enable_circuit_breaker=True`
- Lines 371-398, 627-654: Execution paths use `self.circuit_breakers` (old) not HealthMonitor
- **Must**: Remove old imports, remove `self.circuit_breakers`, use `HealthMonitor.get_breaker()` exclusively

---

## 2. Provider Fabric — Local-First Chain Integrity

### 2.1 config/providers.yaml Local-First List
**Status**: ✅ **SOLE ROUTING CONFIG** `last_verified:2026-08-23`

Priority chain (lines 64-131):
```
0: native-gguf (local)     → priority 0
1: lmster (local)          → priority 1  
2: ollama (local, disabled)→ priority 2
3: antigravity (cloud)     → priority 3
4: google (cloud)          → priority 4
5: openrouter (cloud)      → priority 5
6: opencode-zen (cloud)    → priority 6
7: cline (cloud)           → priority 7
8: anthropic (cloud)       → priority 8
9: xai (cloud)             → priority 9
```

- `strategy: local_first` at line 4
- MaKaLi routing config at lines 8-17 for entity-specific preferences
- Dynamic fallback resolver at lines 21-61 (model-aware chains)

### 2.2 Hardcoded Preferences Bypassing ProviderSelector
**Status**: ✅ **NONE FOUND**

- `model_gateway.generate()` uses `ProviderSelector.get_ordered_providers()` as primary (line 1153)
- Falls back to `self.providers` (priority-sorted from `_load_provider_fabric()`) only on ProviderSelector failure (line 1175)
- `oracle.py` routes through `model_gateway.generate()` — no direct provider selection

### 2.3 Cloud Fallback Behavior
**Status**: ⚠️ **PARTIAL ENFORCEMENT**

- `OracleResponse.cost_warning` field exists (oracle.py:135) but not populated in all paths
- `GenerateResult.is_cloud` tracked (model_gateway.py:50) and passed to observability (line 1081)
- M22 provenance: `provider_name` from actual response (lines 1077, 1194) not dispatch intent
- **No explicit gate enforcing `cost_warning` on cloud fallback** — advisory only

---

## 3. MCP Hub — Tool Surface Stability

### 3.1 MCP Tools Routing Analysis
**Status**: ✅ **ALL ROUTE THROUGH ORACLE → PROVIDERSELECTOR**

| Tool | Line | Route | Depends on Deleted Routers? |
|------|------|-------|----------------------------|
| `oracle_talk` | 173 | `(await oracle).talk()` → ProviderSelector | No (via Oracle) |
| `oracle_summon` | 198 | `(await oracle).summon()` → ProviderSelector | No (via Oracle) |
| `oracle_summon_local` | 222 | `(await oracle).summon(model_override=)` → bypasses TriageRouter | No (via Oracle) |
| `oracle_assess_intent` | 582 | `oracle.assess_confidence()` + registry | No |
| `oracle_list_entities` | 511 | Registry only | No |
| `oracle_list_pillar_keepers` | 529 | Registry only | No |
| `oracle_entity_info` | 553 | Registry only | No |
| `oracle_discover_entity` | 614 | Registry only | No |
| `sovereign_search` | 634 | `sovereign_search_service` | No (uses HealthMonitor) |
| `delegate_task` | 738 | `(await oracle).summon()` | No |

### 3.2 Direct Router Imports in Tools
**Status**: ✅ **NONE** — No tool imports `SemanticRouter`, `TriageRouter`, `RoutingTable`, `RAGRouter` directly

### 3.3 Critical Dependency
**Status**: ⚠️ **TOOLS DEPEND ON ORACLE WHICH STILL IMPORTS DELETED ROUTERS**

All MCP tools will break post-collapse unless `oracle.py` is migrated in the same PR as DEL-1 Week 2.

---

## 4. DEL-1 Integration Impact

### 4.1 search_circuit_breaker.py Deletion
**Status**: ⚠️ **MIGRATION INCOMPLETE**

- `sovereign_search_service.py` lines 48-51: imports deprecated module
- Lines 165-182: HealthMonitor migration done for breaker creation
- Lines 184-188: Still initializes old `circuit_breakers` registry
- Lines 371-398, 627-654: Execution paths use old registry
- **Impact**: DEL-1 #5 deletion will break `sovereign_search` MCP tool and all search tiers

### 4.2 QdrantAdapter Deletion
**Status**: ✅ **NO MCP TOOL REFERENCES**

- No MCP tool in `hub_tools/tools.py` references QdrantAdapter
- `sovereign_search_service.py` uses `self.memory_store.vector_store` (line 950) — abstract interface
- `hub_tools/tools.py` line 720: `gw.model_gateway._health_monitor` — no Qdrant direct reference

### 4.3 fleet_orchestrator.py Deletion
**Status**: ⚠️ **RouteDecision WAS HERE — NOW MISSING**

- `RouteDecision` enum defined at `fleet_orchestrator.py:44` — **DELETED MODULE**
- This is the source of the missing `RouteDecision` dataclass
- No Hub tool imports `fleet_orchestrator` directly
- **Must**: Re-implement `RouteDecision` as dataclass in surviving code (provider_selector.py or new contracts.py)

---

## 5. Lilith's 5 CRITICAL BLOCKERS — N4 API/Integration Assessment

| Blocker | N4 Assessment | File:Line Evidence |
|---------|---------------|-------------------|
| **Missing RouteDecision contract test** | **CONFIRMED CRITICAL**: RouteDecision dataclass does not exist. Was in deleted `fleet_orchestrator.py:44`. Must be re-implemented with contract test. | `fleet_orchestrator.py:44` (deleted), DEBUT_REMEDIATION_MANUAL.md:313 |
| **Dual admission gates** | **CONFIRMED**: `model_gateway.py:1233` `admission_ctrl.acquire()` + `:1258` `resource_guard.lock()` = two semaphores. Blocker A in verdict. Naive merge → non-reentrant self-deadlock. | `model_gateway.py:1233,1258`, MAKALI_COUNCIL_VERDICT.md:38 |
| **Zombie breakers** | **CONFIRMED**: `search_circuit_breaker.py` still exists, imported by `sovereign_search_service.py`, instantiated alongside HealthMonitor. C-6' unification incomplete. | `sovereign_search_service.py:48-51,185-188,371+` |
| **M8 false positive ("segments" in comment)** | **NEEDS VERIFICATION**: Check `oracle_cli.py` and `config/m23_baseline.txt` for "segments" comment triggering false positive. | `oracle_cli.py:21-26`, `config/m23_baseline.txt:8` |
| **MIAP→Hivemind gap** | **CONFIRMED**: No automated gnosis projection from MIAP (cancelled DEL-1 #2) to Hivemind. `hivemind_get_continuation` reads cold store passively; no active push from session lifecycle. | `hub_tools/tools.py:919-958`, `oracle.py:818-896` |

---

## 6. Mandate Compliance Check

| Mandate | Status | Evidence |
|---------|--------|----------|
| **M1 AnyIO Absolute** | ✅ | All async code uses AnyIO; `anyio.to_thread.run_sync` for blocking I/O |
| **M2 Engine-Stack Firewall** | ✅ | `config/providers.yaml` is engine config; WADs in `config/wads/` |
| **M7 Local-First** | ✅ | Provider chain native-gguf→lmster→ollama→cloud; ProviderSelector enforces |
| **M13 Temple-Grade** | ⚠️ | `make temple-grade` currently FAILS (m23 gate, Blocker B) — must fix before green |
| **M22 Response Provenance** | ✅ | `GenerateResult.provider_name` from actual response (model_gateway.py:1077,1194) |
| **M25 Streaming Resilience** | ✅ | `config/providers.yaml` has `streaming.chunk_timeout_ms` and `total_timeout_ms` per provider |

---

## 7. Conditions for PROCEED (Must Fix Before DEL-1 Week 2)

### P0 — Critical (Block DEL-1 Week 2 Router Collapse)
1. **Implement RouteDecision dataclass** in `provider_selector.py` or new `contracts.py`:
   ```python
   @dataclass
   class RouteDecision:
       entity: str
       model: str
       provider: str
       reason: str
       is_cloud: bool
       cost_warning: Optional[str] = None
   ```

2. **Add contract test** at `tests/contract/test_route_decision.py` verifying `isinstance(result, RouteDecision)` at every typed boundary (M21)

3. **Complete search_circuit_breaker migration** in `sovereign_search_service.py`:
   - Remove lines 48-51 (deprecated imports)
   - Remove lines 184-188 (old registry initialization)
   - Replace lines 371-398, 627-654 with `self._health_monitor.get_breaker()` calls

4. **Migrate oracle.py** to remove `SemanticRouter`, `TriageRouter`, `RAGRouter` imports and replace with `EntityRegistry.find_by_domain` + `ProviderSelector` (DEL-1 Week 2 scope)

### P1 — High (Block Green Build)
5. **Fix dual admission gate** in `model_gateway.py` (Blocker A) — merge to single `ResourceGuard.lock()` with fail-fast semantics preserving C-10 admission control

6. **Verify M8 false positive** in `oracle_cli.py:21-26` and `config/m23_baseline.txt:8` — replace blind-except with `contextlib.suppress(ImportError)`

### P2 — Medium (Post-Debut)
7. **Implement MIAP→Hivemind gnosis projection** — event-driven from session lifecycle (`oracle.py:818-896`) to Hivemind via `hivemind_post_context`

---

## 8. File:Line Citation Index

| Claim | File | Line(s) |
|-------|------|---------|
| ProviderSelector single router | `src/omega/oracle/provider_selector.py` | 15, 30-60 |
| RouteDecision missing | `src/omega/integrations/fleet_orchestrator.py` | 44 (deleted) |
| oracle.py SemanticRouter import | `src/omega/oracle/oracle.py` | 31, 226-229, 1132-1137 |
| oracle.py TriageRouter import | `src/omega/oracle/oracle.py` | 50-57, 233, 764 |
| oracle.py RAGRouter import | `src/omega/oracle/oracle.py` | 511-514 |
| sovereign_search_service old imports | `src/omega/oracle/sovereign_search_service.py` | 48-51 |
| sovereign_search_service HealthMonitor | `src/omega/oracle/sovereign_search_service.py` | 165-182 |
| sovereign_search_service old registry | `src/omega/oracle/sovereign_search_service.py` | 184-188, 371-398, 627-654 |
| config/providers.yaml chain | `config/providers.yaml` | 64-131 |
| model_gateway ProviderSelector call | `src/omega/oracle/model_gateway.py` | 1153-1175 |
| OracleResponse.cost_warning | `src/omega/oracle/oracle.py` | 135 |
| GenerateResult.is_cloud | `src/omega/oracle/model_gateway.py` | 50, 1081 |
| M22 provenance | `src/omega/oracle/oracle.py` | 1077, 1194 |
| MCP tools via Oracle | `mcp_servers/omega_hub/hub_tools/tools.py` | 173, 198, 222, 582, 511, 529, 553, 614, 634, 738 |
| Dual admission gates | `src/omega/oracle/model_gateway.py` | 1233, 1258 |
| M8 false positive | `src/omega/oracle/oracle_cli.py` | 21-26 |
| MIAP→Hivemind gap | `mcp_servers/omega_hub/hub_tools/tools.py` | 919-958 |
| Session lifecycle | `src/omega/oracle/oracle.py` | 818-896 |

---

## 9. Lessons Tagged [N_4] → Ma'at's proposed_lessons.yaml

All lessons from this review have been appended to `data/entities/maat/proposed_lessons.yaml` with tags `[N_4]` covering:
- Router Collapse contract integrity
- Provider Fabric local-first sovereignty
- DEL-1 circuit breaker migration atomicity
- Admission control pipeline composition
- MIAP→Hivemind gnosis projection architecture

---

## 10. Final Verdict

**PROCEED WITH CONDITIONS**

The architecture is sound. The single-router design (ProviderSelector) is correct and stable. The provider fabric enforces local-first. MCP Hub tools route correctly through Oracle.

**But**: The missing `RouteDecision` contract, incomplete circuit breaker migration, dual admission gates, and MIAP→Hivemind gap are **integration completeness failures** that will cause runtime failures if DEL-1 Week 2 proceeds without them.

**Recommendation**: Execute INST-1 Fixes 2, 4, 5, 6 + Blocker B fix (per Audit sequence), then address the 6 conditions above in a single atomic PR before DEL-1 Week 2 router collapse.

---

*⬡ OMEGA ⬡ N4 BRIDGE ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_n4_cross_domain_review ⬡ 2026-08-23*