---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "session-paging-report"
document_id: "n8-vetting-early-delta"
title: "N8 Observability — EARLY Pass Delta Report (vs later N8_VETTING_delta.md)"
status: "COMPLETE"
date: "2026-08-21"
owner: "node (N8 Observability)"
session_model: "x-preview-f-free"
paged_by: "kali (ses_fdef2be4effe4pAaLXCTUx62GO)"
scope: "Unique findings from EARLIER N8 INST-1/DEL-1 vetting only"
---

# N8 VETTING — EARLY PASS DELTA

**Context**: Original session performed N8 observability vetting of INST-1/DEL-1
(Debut Hardening Plan). Session paged out mid-verification before final verdict
was delivered. A later N8 pass produced `N8_VETTING_delta.md`. This file reports
ONLY what the early pass uniquely found.

## §1 Unique Findings

**F1 — Measurable gate spec bug (HIGH, likely absent from later pass).**
The review task's gate `rg -n "provider_name" src/omega/oracle/providers.py`
returns EMPTY. M22 provenance is actually satisfied in
`src/omega/oracle/model_gateway.py` (GenerateResult dataclass line 37,
field line 49; set from `success_provider.name` at line 1410; fallback path
line 1427 sets `provider_name="fallback"` with is_cloud derived per M22).
Gate as written fails against a compliant codebase — wrong target file.

**F2 — Duplicate method in god-module (MEDIUM).**
`ObservabilityEngine.record_vault_audit` is defined TWICE in
`src/omega/observability/__init__.py` (~lines 1225 and ~1291); second def
silently shadows the first. Also duplicate `OmegaError` import (lines 16-18).
God-module freeze (manual §7) means this dead duplicate persists through
debut. Pre-existing defect, NOT introduced by INST-1/DEL-1.

**F3 — Router collapse loses routing-decision trace events (CONCERN).**
Current talk path emits: `trace.log("rag.classify", complexity=...)`
(oracle.py:517), `trace.log("domain.routed", entity/confidence/method)`
(oracle.py:1139), TriageResponse.reasoning[] + fallback_chain
(triage_router.py:73-82), escalation event (oracle.py:625).
DEL-1 week2 deletes RAGRouter/TriageRouter/SemanticRouter → these events
vanish unless the single RouteDecision contract test preserves a minimal
routing-reason event. SSE `/obs/stream` consumers lose routing visibility.

**F4 — search_circuit_breaker redirect must keep trace_id (LOW).**
DEL-1 week1 deletes it; leftover caller redirects to
`HealthMonitor.get_breaker()` whose `_on_success/_on_failure` record
trace_id into MetricsDB breaker_transitions — preserve that arg on redirect.

## §2 Concerns: Resolved vs Silently Dropped

**Verified GREEN during early pass (evidence-backed):**
- SSE `/obs/stream` LIVE: curl returned `event: observability_update`
  payloads (breaker_states, global_error_rate, 10-trace tail, 2s cadence).
  server.py:234 handler + route :324 + hub_tools/tools.py:3530 tool intact.
- `make temple-grade` PASSES: M1 AnyIO, M9 no-bare-except, M8 zero-telemetry,
  M7 local-first SSOT, **M22 is_cloud-SSOT check**, M23 soft-failure scan
  (296 vs baseline 298) all green.
- MetricsDB migration GOOD: `data/observability/metrics.db` performance table
  has cache_read_tokens/provider_prompt_tokens/provider_completion_tokens
  (verified via sqlite PRAGMA). Schema v3 live.
- trace_id propagation rich: ~30 call sites through oracle talk path.

**Premise correction (INST-1 Q1):** `config/model_registry/index.sqlite` has
NO performance table at all — the sprint-note claim "Metrics DB migration
fixed" refers to `data/observability/metrics.db`. INST-1 does not touch either;
unaffected. But ACTIVE_SPRINT gate note cites the wrong path.

**Data-quality concern (LOW):** live stream showed global_error_rate=0.859
with contract-test pollution (`failing_provider`, `contract-test-trace-*`
events in production feed). Cosmetic; not an INST/DEL impact.

**Silently dropped:** session paged out before final verdict message and
before Hivemind completion post — findings were orphaned, neither ratified
nor rejected by Kali.

## §3 Flagged But Never Executed

1. **Gate-spec fix** — correct the measurable gate to
   `rg -n "provider_name" src/omega/oracle/model_gateway.py` (F1).
   Never filed as a ticket; review-task text still wrong.
2. **RouteDecision trace-preservation requirement** — add explicit acceptance
   line to DEL-1 week2: collapsed path MUST emit one routing-reason event
   (entity, model, provider, reason) or observability loses routing traces (F3).
   Not present in manual §5 week-2 acceptance list.
3. **Duplicate record_vault_audit cleanup** — deferred under god-module freeze;
   recommend post-debut split ticket (F2). No owner assigned.
4. **Full pytest verification** — early pass attempted
   `pytest tests/test_metrics_db.py::test_performance_cache_read_tokens_tracked`
   but hit plugin arg error (`-n --timeout=60` unrecognized in system python;
   venv not activated per M24). Test-level confirmation of migration was done
   via direct sqlite PRAGMA instead — adequate evidence, but the formal
   contract-test run was never completed in-session.

## Verdict (early pass, reconstructed)

INST-1: **PASS** for observability (no obs-surface files touched; MetricsDB
unaffected; Redis opt-in change does not alter event persistence path).
DEL-1: **PASS with CONCERN** — router collapse is safe for M22 provenance
(provider_name survives; ProviderSelector retained) and BudgetGate async fix
(P1-1 completed 2026-08-17, ACTIVE_SPRINT) survives; but routing-decision
trace events are lost unless F3 mitigation is added to week-2 acceptance.

---
*⬡ OMEGA ⬡ N8-OBSERVABILITY ⬡ EARLY-PASS-DELTA ⬡ 2026-08-21*
