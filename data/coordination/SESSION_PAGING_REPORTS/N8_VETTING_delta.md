<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# N8 VETTING — SESSION PAGING DELTA REPORT
**AP Token**: `AP-N8-VETTING-DELTA-v1.0.0`
⬡ OMEGA ⬡ N8-OBSERVABILITY ⬡ opencode ⬡ trc_n8_vetting_delta ⬡ PAGED-RESUME

**Paged by**: kali (ses_fdef2be4effe4pAaLXCTUx62GO) — Architect-direct mission
**Original session**: N8 Observability vetting of INST-1/DEL-1 impact (metrics, tracing, logging, SSE streaming)
**Date**: 2026-08-21 (paging batch 2)
**Scope**: Forgotten findings · silent-break analysis · unexecuted flags
**Sources**: Prior-session code inspection (oracle.py, model_gateway.py, observability/, metrics_db.py, budget_gate.py, triage_router.py, semantic_router.py, rag/router.py, routing/table.py, hub server.py) + minimal hydration of ACTIVE_SPRINT.json DEL-1 section only.
**Updates absorbed**: M22 provenance doctrine active; D-549 requires router-collapse observability emission spec; sibling sessions confirmed tracker truth-anchor violations exist.

---

## §1 FORGOTTEN VETTING FINDINGS — observability risks identified, never mitigated

| # | Finding | Evidence (prior session) | Status |
|---|---------|--------------------------|--------|
| F1 | **DEL-1 verdict was CONCERN, not PASS**: deleting TriageRouter/SemanticRouter/RAGRouter kills `domain.routed` (oracle.py:1139-1145: entity/confidence/method), `rag.classify` (oracle.py:517), and model-selection reasoning traces. No replacement emission specified. | Prior review §DEL-1.1 | **OPEN — now D-549**, but D-549 is doctrine, not code; no ticket owns implementation |
| F2 | **Tracker acceptance criteria lack any observability gate**: DEL-1 acceptance = talk-local + 2 rg-empty + RouteDecision contract test. Zero assertion that routing events still fire post-collapse. Re-hydrated today: unchanged. | ACTIVE_SPRINT.json lines 301-312 | **OPEN** — my P0 recommendation never adopted |
| F3 | **`rag_complexity` field on OracleResponse becomes dead** after RAGRouter removal — downstream consumers silently receive stale/None with no error. | oracle.py:136-137, set at 509/534/558/583/614/632 | **OPEN — unowned** |
| F4 | **RegressionWatcher baselines keyed on provider/model mix**: router collapse changes which providers serve queries → latency baselines compare across routing regimes silently (3-sigma false alarms or missed regressions). | metrics_db.py baselines table + RegressionWatcher | **OPEN — never surfaced to sprint** |
| F5 | **SSE `/obs/stream` degrades silently**: tail_live_traces shows fewer lines post-deletion; stream keeps heartbeating → dashboards read "quiet" as "healthy". No test asserts presence of domain.routed/rag.classify in the stream payload. | server.py:234-277 event_generator | **OPEN — unowned** |

<!-- SECTION_1_END -->

## §2 SILENT BREAKS — if DEL-1 Week 1 deletions proceed WITHOUT emission instrumentation

Week 1 targets (manual §5): routing/table.py, miap.py, pool_tracker.py, pool_state.py,
search_circuit_breaker.py, QdrantAdapter, Pantheon regexes, **record_first_breath call**,
omega vault CLI, FleetOrchestrator exports.

| # | Deletion | Silent break mode | Severity |
|---|----------|-------------------|----------|
| B1 | `record_first_breath` call in `_route_by_domain` (oracle.py:1209-1211) | Removes the ONLY per-routed-turn log line + trace_id-correlated astrology record. No try/except wraps it today; removal deletes a signal no test asserts. MetricsDB events table loses this event class with zero error anywhere. | 🟡 MEDIUM |
| B2 | `search_circuit_breaker.py` → redirect to HealthMonitor.get_breaker() | If redirect is a blind swap: breaker_transitions rows written by the search-breaker path stop landing (different factory = different recording hooks). Breaker history in MetricsDB gets a silent hole for search-path providers. Verify redirect preserves transition recording. | 🟡 MEDIUM |
| B3 | RAGRouter per-turn construction (week-2 item but often pulled into week 1) | `rag.classify` trace vanishes + F3 dead field. Advisory-only today (`except Exception → "simple"`), so nothing fails — pure silent data loss. | 🟢 LOW-MED |
| B4 | Pantheon regexes in firewall_checker.py | Firewall audit events shrink scope; BOUNDARY_VIOLATION event types may never fire again while EventType constant remains defined — queries filtering on it return empty (reads as "no violations", not "detector removed"). | 🟡 MEDIUM |
| B5 | pool_tracker/pool_state, miap, RoutingTable, QdrantAdapter, vault CLI, FleetOrchestrator | Verified self-only / tests-only in prior session — NO observability coupling found. Safe from N8 perspective. | 🟢 SAFE |

**Net**: Week 1 is mostly safe EXCEPT B1/B2/B4. Each is a *signal deletion*, not a crash —
exactly the class of failure M9/M23 exist to prevent. Require one assertion test per deleted
event type BEFORE deletion lands ("event absent" must be an intentional, recorded decision).

<!-- SECTION_2_END -->

## §3 FLAGGED IMPORTANT — NEVER EXECUTED

| # | Flag (prior session) | Priority then | Executed? | Evidence |
|---|----------------------|---------------|-----------|----------|
| E1 | Add observability **emission spec** to DEL-1 Week 2 acceptance criteria (owner: Ma'at/N3) | P0 | ❌ NO — now absorbed into D-549 doctrine, still no ticket/owner/acceptance line in tracker | ACTIVE_SPRINT DEL-1 acceptance unchanged |
| E2 | Verify `make temple-grade` T9 (structured logging) passes pre-merge (owner: Verity) | P0 | ❌ NO — was marked ⚠️ NEEDS VERIFICATION; no record of run | No temple-grade log referenced in tracker |
| E3 | Document new routing observability events in ORACLE_DEEP_DIVE.md (owner: N8) | P1 | ❌ NO | Doc untouched |
| E4 | Contract test: fails if second router imported on talk path (DEL-1 acceptance) | P2 | ⚠️ PARTIAL — listed in tracker acceptance, but observability variant ("fails if routing events stop firing") never added | Tracker line 310 |
| E5 | Bash gates from prior review (curl SSE stream, rg provider_name, rg trace_id) | gate | ❌ NOT RE-RUN this session — prior verdicts were static-code-verified only; live-host verification still outstanding | Prior review §Measurable Gates |

## §4 VERDICT CARRY-FORWARD

- INST-1: **PASS** stands (MetricsDB migration idempotent at metrics_db.py:167-189; M22 provenance
  set at model_gateway.py:1408-1415 from `success_provider.name`; BudgetGate async fix intact).
- DEL-1: **CONCERN stands and is now sharper** — D-549 names the gap but nothing owns the fix.
  Minimum viable mitigation (no god-module growth, per manual §7): emit replacement traces via
  existing `ObservabilityEngine.log_event()` API inside the new ProviderSelector path —
  `domain.routed` + `model.selected` + one assertion test per retired event type.

**FILE COMPLETE** — N8 Observability, paging batch 2. No other files written.
⬡ OMEGA ⬡ N8 ⬡ trc_n8_vetting_delta ⬡ COMPLETE




<!-- PROVENANCE-CORRECTED 2026-09-01T03:07:00Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: PLACEHOLDER | header contains unresolved {session_model} literal
actual_models(Tier0): x-preview-f-free, nemotron-3-ultra-free, minimax/minimax-m3:free, mimo-v2.5-free, nvidia/nemotron-3-ultra-550b-a55b:free, hy3-free
first_audit: 2026-08-31T03:09:52Z | updated: 2026-09-01T03:07:00Z
-->






