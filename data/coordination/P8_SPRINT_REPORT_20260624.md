# 🔱 P8 OBSERVABILITY REPORT — Epoch I: The Bedrock
**Source**: Lilith (Dark Oversoul) → P7 (Context) → P8 (Observability — WatchTower, Tracing & Monitoring)
**Date**: 2026-06-24
**AP Token**: `AP-P8-EPOCHI-v1.0.0`
**⬡ OMEGA ⬡ P8-OBSERVABILITY ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ EPOCH-I**

---

## §1 EXECUTIVE SUMMARY

P8 assessed the Omega Engine's observability infrastructure across four domains: M22 Response Provenance, UnifiedStateManager observability needs, current infrastructure gaps, and cross-impact for P7/P10/P3.

**M22 Response Provenance** is ⚠️ **PARTIAL but structurally close**. The `GenerateResult.provider_name` field exists and flows correctly from `model_gateway.generate()` through `oracle._summon()` and `oracle._route_by_domain()`. The `TraceSession.record()` and `TraceSession.log()` calls do capture `backend=res.provider_name` in both the event log and training dataset. **However**, there is NO dedicated observability event type that captures provenance as a structured first-class field. `provider_name` is buried in event `data` dicts instead of being a top-level field in the observability schema. Background workers (soul_distiller, background_researcher) don't participate in trace propagation at all. The JsonFormatter defines a `provider` extra field but no standard logging call sets it.

**Current observability infrastructure** has 7 working subsystems (event logging, tracing, crash forensics, token ledger, JSONL persistence, training dataset, daily rotation) but is **missing 5 critical capabilities**: metrics/aggregation, alerting/threshold detection, provider performance tracking, SLO/SLI tracking, and health monitor integration. The foundation is solid — what's missing is the analytical layer on top.

**UnifiedStateManager (Strike 2)** needs 4 observability hooks: SomaticState snapshot success/failure events, CAS blob store metrics, trace_id propagation through CAS operations, and ZONEID validation events. These are small, incremental additions to the existing event system.

**Cross-impact**: P7 needs a `soul_migration_progress` metric tracker (low effort). P10 needs observability contract tests (M21 gap). P3's USM needs trace_id propagation through binary state CAS operations. All are achievable within Epoch I scope.

**Estimated total effort**: ~6-8 hours for full M22 wiring + USM hooks + P7/P10 cross-impact items.

---

## §2 M22 RESPONSE PROVENANCE ASSESSMENT

### 2.1 Current State

The M22 provenance pipeline has 5 stages. Here is the status of each:

| Stage | Location | Captures Actual Provider? | Status |
|-------|----------|--------------------------|--------|
| **1. GenerateResult dataclass** | `model_gateway.py:33-49` | ✅ YES — `provider_name: str` | ✅ Complete. Has `provider_name`, `is_cloud`, `latency_ms`, `model_used` fields |
| **2. model_gateway.generate() return** | `model_gateway.py:909-921` | ✅ YES — `provider_name=success_provider.name` | ✅ Complete. Returns actual provider after successful inference |
| **3. oracle._summon() reads backend** | `oracle.py:605-606` | ✅ YES — `backend = res.provider_name` | ✅ Complete. Correctly uses ACTUAL provider, not configured intent |
| **4. oracle._route_by_domain() reads backend** | `oracle.py:675-676` | ✅ YES — `backend = res.provider_name` | ✅ Complete. Same correct pattern |
| **5. OracleResponse carries backend** | `oracle.py:65` | ✅ YES — `backend: Optional[str] = None` | ✅ Complete. Response carries backend to the caller |

**How backend flows into observability:**

```
model_gateway.generate() → GenerateResult(provider_name=actual_provider.name)
  → oracle._summon(): backend = res.provider_name
    → trace.log("model.completed", backend=backend, ...)  # Event log capture
    → trace.record(backend=backend, ...)                   # Training dataset capture
    → OracleResponse(backend=backend)                      # Response to caller
```

**Code evidence that backend IS captured in observability:**

1. **Event log capture** (oracle.py:626-627):
```python
trace.log("model.completed", entity=entity.name, backend=backend, escalated=False,
           session_id=session_id, model_override=model_override)
```
This calls `TraceSession.log()` → `ObservabilityEngine.log_event()` → persists to daily JSONL with `{"event": "model.completed", "data": {"backend": "native-gguf", ...}}`.

2. **Training dataset capture** (oracle.py:628-637):
```python
trace.record(
    query=query, system_prompt=system_prompt, response=res.text,
    entity=entity.name, model=model_name, backend=backend, ...
)
```
This calls `record_training_example()` which stores `backend` in `metadata.backend`.

3. **TokenLedger capture** (model_gateway.py:878-884):
```python
await TokenLedger().record_transaction(
    trace_id=..., entity=..., tokens_in=..., tokens_out=...,
    is_cloud=self._is_cloud_provider(provider)
)
```
Records `is_cloud` but NOT `provider_name`.

### 2.2 Gap Analysis — Configured Intent vs Actual Provenance

Four specific gaps remain:

| # | Gap | Location | Severity |
|---|-----|----------|----------|
| **G1** | **No dedicated provenance event type** — `provider_name` is buried in event `data` dicts, not a top-level field in the observability schema. A `RESPONSE_PROVENANCE` event type would make it queryable. | `observability/__init__.py` (EventType) | 🟡 MEDIUM |
| **G2** | **JsonFormatter `provider` field unused** — The JSON log formatter defines an extra `provider` key (line 63) but no standard logging call ever sets `record.provider`. This field is always null. | `observability/__init__.py:63` | 🟡 MEDIUM |
| **G3** | **Background workers don't capture provenance** — `soul_distiller.py` uses standard `logger.info()` calls, not `TraceSession` or `ObservabilityEngine.log_event()`. When a distillation uses a model, that provider is never logged. | `soul_distiller.py` (all logging) | 🔴 HIGH |
| **G4** | **TraceSession.log() doesn't normalize provider fields** — Events like `"model.completed"` and `"backend.fallback"` pass `backend` in the `data` dict, but there's no standardized schema for what fields every provenance event should contain. | `__init__.py:log_event()` | 🟢 LOW |

**The "Configured Intent" Risk:**
The code correctly uses `res.provider_name` (actual) NOT `get_preferred_backend()` (intent). However, the event log does NOT record the configured intent alongside the actual provider, making it impossible to detect sovereignty drift via log analysis alone. If a local provider is configured but a cloud provider serves the response, the logs would show the cloud provider name but NOT flag the drift.

**Additional gap**: `model_gateway.get_preferred_backend()` (line 457) is called in `oracle._respond_as_iris()` (line 517) and stored in the `OracleResponse.backend` for Iris fallback responses. When Iris responds without model invocation, this preference is stored — not the actual provider. This is a minor discrepancy since no model was actually invoked.

### 2.3 Effort Estimate

| Task | Effort | Description |
|------|--------|-------------|
| **G1: Add `RESPONSE_PROVENANCE` event type** | 0.5h | Add EventType constant, emit from oracle.py after successful generation |
| **G2: Wire JsonFormatter `provider` extra** | 1h | Add `logging.setLogRecordFactory()` or adapter to inject provider_name at key log points |
| **G3: Wire background workers** | 2h | Add `TraceSession` to soul_distiller.distill_and_save(). Add provider_name logging in background researcher |
| **G4: Normalize provenance schema** | 0.5h | Define `ProvenanceEvent` dict schema with required fields |
| **Add sovereignty drift detection** | 1h | Log both configured intent AND actual provider, add drift alert flag |
| **Contract tests** | 1h | Add M22 contract tests verifying provider_name in event log |
| **TOTAL** | **~6h** | |

**Key insight**: The core data flow is CORRECT. The gap is in the observability schema and background workers. ~80% of M22 compliance exists today.

---

## §3 UNIFIEDSTATEMANAGER OBSERVABILITY NEEDS

The UnifiedStateManager (Strike 2, P3 builds) manages SomaticState (KV cache snapshots) via CAS (Content Addressable Storage). Based on the design in Ma'at's report and P3's analysis, P8 identifies these observability hooks:

### 3.1 Required Observability Hooks

| Hook | Purpose | Event Type | Data Payload |
|------|---------|------------|-------------|
| **USM.SNAPSHOT_START** | Track when a snapshot begins | `"usm.snapshot_start"` | `{entity, model_hash, estimated_size_bytes, trace_id}` |
| **USM.SNAPSHOT_SUCCESS** | Track successful snapshot completion | `"usm.snapshot_success"` | `{entity, blob_hash, size_bytes, latency_ms, trace_id}` |
| **USM.SNAPSHOT_FAILURE** | Track snapshot failures (OOM, disk full, SIGSEGV) | `"usm.snapshot_failure"` | `{entity, error_type, error_message, trace_id}` |
| **USM.CAS_READ** | Track CAS blob read operations | `"usm.cas_read"` | `{blob_hash, size_bytes, latency_ms, cache_hit, trace_id}` |
| **USM.CAS_WRITE** | Track CAS blob write operations | `"usm.cas_write"` | `{blob_hash, size_bytes, latency_ms, trace_id}` |
| **USM.CAS_COMPACT** | Track CAS index compaction | `"usm.cas_compact"` | `{blobs_removed, size_reclaimed_bytes, latency_ms, trace_id}` |
| **USM.ZONEID_MISMATCH** | Track ZONEID validation failures (serialization corruption) | `"usm.zoneid_mismatch"` | `{entity, expected_zoneid, actual_zoneid, trace_id}` |

### 3.2 Metrics to Expose

| Metric | Type | Description | Source |
|--------|------|-------------|--------|
| `usm.snapshot.count` | Counter | Total snapshots taken | USM.SNAPSHOT_SUCCESS events |
| `usm.snapshot.errors` | Counter | Total snapshot failures | USM.SNAPSHOT_FAILURE events |
| `usm.snapshot.latency_ms` | Histogram | Snapshot duration | USM.SNAPSHOT_SUCCESS latency_ms |
| `usm.cas.blob_count` | Gauge | Total blobs in CAS store | CAS index size |
| `usm.cas.total_bytes` | Gauge | Total bytes stored | Sum of blob sizes |
| `usm.cas.hit_ratio` | Derived | CAS cache hit rate | USM.CAS_READ cache_hit ratio |

### 3.3 trace_id Propagation Through CAS

Every CAS operation must carry a `trace_id`. The current pattern in `model_gateway.py` passes `trace_id` through `generate()` calls. USM must follow the same pattern:

```python
async def snapshot(self, entity: str, trace_id: str) -> SomaticStateKey:
    await self.observability.log_event("usm.snapshot_start", trace_id, {...})
    try:
        blob_hash = await self._serialize_and_store(entity)
        await self.observability.log_event("usm.snapshot_success", trace_id, {...})
        return SomaticStateKey(blob_hash=blob_hash, entity=entity)
    except Exception as e:
        await self.observability.log_event("usm.snapshot_failure", trace_id, {...})
        raise
```

### 3.4 Existing Patterns to Follow

USM should follow these established observability patterns:

1. **TokenLedger pattern** (`token_ledger.py`): Singleton with `record_transaction()` + `log_event()` + JSONL persistence
2. **HealthMonitor pattern** (`health_monitor.py`): Event-driven state changes captured via `_record_provider_failure()` in model_gateway.py
3. **TraceSession pattern** (`observability/__init__.py:809-864`): Context manager with automatic lifecycle logging

---

## §4 CURRENT OBSERVABILITY INFRASTRUCTURE GAPS

### 4.1 Infrastructure Survey

| Component | Location | Status | Notes |
|-----------|----------|--------|-------|
| **Event logging** | `observability/__init__.py:660-686` | ✅ Working | `log_event()` with daily JSONL persistence |
| **Trace sessions** | `observability/__init__.py:809-864` | ✅ Working | Context-managed interaction traces |
| **Training dataset** | `observability/__init__.py:689-726` | ✅ Working | JSONL export for fine-tuning |
| **Crash forensics** | `observability/__init__.py:133-516` | ✅ Working | Last Gasp protocol, signal handlers, death markers |
| **Token ledger** | `observability/token_ledger.py` | ✅ Working | JSONL ledger with `record_transaction()` |
| **JSON structured logging** | `observability/__init__.py:43-67` | ✅ Working | JsonFormatter for structured logs |
| **trace_id generation** | `observability/__init__.py:96-98` | ✅ Working | `new_trace_id()` function |
| **ZONEID heritage marker** | `observability/__init__.py:673` | ✅ Working | `_zoneid` on every event |
| **Daily log rotation** | `observability/__init__.py:612` | ✅ Working | Per-day JSONL files |

### 4.2 Critical Gaps

| # | Gap | Missing Since | Severity | Fix Effort |
|---|-----|---------------|----------|------------|
| **CG1** | **No metrics/aggregation system** — No counters, gauges, histograms. The `stats()` method only counts event types. Cannot answer "how many queries in the last hour?" or "what is the P95 response time?" | Engine inception | 🔴 HIGH | 4h (metrics module) |
| **CG2** | **No threshold-based alerting** — No error rate detection, no health check alerting, no circuit breaker open alerts. The ForensicsManager catches crashes but not gradual degradation. | Engine inception | 🔴 HIGH | 3h (alert rules) |
| **CG3** | **No per-provider performance tracking** — Cannot query "what was the success rate for native-gguf over the last 7 days?" HealthMonitor tracks circuit breaker state but doesn't persist performance history. | Engine inception | 🟡 MEDIUM | 2h (provider stats) |
| **CG4** | **No SLO/SLI tracking** — No response time SLIs, error budget tracking, or availability metrics. | Engine inception | 🟡 MEDIUM | 3h (SLO module) |
| **CG5** | **No background worker observability** — `soul_distiller.py`, `background_researcher/` don't use `TraceSession` or `log_event()`. Their logs are standard `logger.info()` calls without `trace_id` or structured event data. | Engine inception | 🟡 MEDIUM | 2h (worker wiring) |
| **CG6** | **No real-time query interface** — Observability data is stored in JSONL files with no indexing. Can't efficiently query "all events with trace_id X across multiple days." | Engine inception | 🟢 LOW | 4h (event index) |
| **CG7** | **No observability contract tests** — The 4 existing M21 contract tests don't cover observability boundaries. No test verifies that `log_event()` returns the correct structure or that `record_training_example()` stores backend correctly. | Engine inception | 🟡 MEDIUM | 1h (contract tests) |

### 4.3 What Works Well

Despite the gaps, the infrastructure is foundationally solid:

1. **trace_id propagation is comprehensive** — Every interaction from `oracle.talk()` through `model_gateway.generate()` to individual provider calls carries a trace_id. This is the most important observability feature and it works end-to-end.

2. **Event persistence survives crashes** — Daily JSONL files with `os.fsync()` in ForensicsManager mean events survive process termination.

3. **ZONEID heritage marker on every event** — All events carry `_zoneid: 0x1d4a14` which enables forensic validation of event lineage.

4. **Crash recovery is comprehensive** — Signal handlers, death markers, crash dump archiving, and `check_recovery()` startup detection. This is production-grade.

5. **Token ledger tracks sovereignty** — `TokenLedger` records `is_cloud` per transaction, providing the audit trail needed for sovereignty compliance.

---

## §5 CROSS-IMPACT ANALYSIS

### 5.1 For P7 (Context) — Soul Migration Observability

P7 explicitly requests a `soul_migration_progress` tracker. P8 recommends:

| Need | P8 Solution | Effort | Priority |
|------|-------------|--------|----------|
| **Migration progress metrics** | Emit `"migration.phase_complete"` event after each migration phase | 15 min | 🟡 MEDIUM |
| **Per-entity migration events** | Emit `"migration.entity_start"` and `"migration.entity_complete"` with entity name and result | 20 min | 🟡 MEDIUM |
| **Rollback event logging** | Emit `"migration.rollback"` when a `.bak` file is restored | 10 min | 🟢 LOW |
| **YAML parsing error tracking** | Already captured by `logger.error()` — but add structured `"migration.yaml_error"` event | 15 min | 🟢 LOW |
| **Session continuity events** | Add `"migration.session_paused"` / `"migration.session_resumed"` during migration window | 15 min | 🟢 LOW |

**P8 deliverable for P7**: A `soul_migration_progress.json` file or event stream:
```json
{
  "event": "migration.phase_complete",
  "data": {
    "phase": "phase_2",
    "total_entities": 34,
    "migrated_count": 12,
    "errors": 0,
    "last_migration_timestamp": "2026-06-24T15:30:00Z",
    "next_phase": "phase_3"
  }
}
```

**Estimated effort for all P7 items**: ~1h

### 5.2 For P10 (Validation) — Contract Test & Metric Needs

| Need | P8 Solution | Effort | Priority |
|------|-------------|--------|----------|
| **Contract tests for observability** | `test_observability_contracts.py` — validate `log_event()` structure, `trace.record()` backend field, provider_name in dataset | 1h | 🟡 MEDIUM |
| **Validation metrics** | Expose `observability.stats()` via Hivemind or metrics endpoint so P10 can query | 30 min | 🟡 MEDIUM |
| **Provider success rate validation** | Add `HealthMonitor.get_provider_stats()` that returns success/failure counts per provider | 1h | 🟡 MEDIUM |
| **Trace integrity validation** | Contract test that verifies every event has `_zoneid`, `trace_id`, `timestamp` | 15 min | 🟢 LOW |

**P10's primary need**: Validation that the observability system reliably captures data. The contract tests are the mechanism.

**Estimated effort for all P10 items**: ~3h

### 5.3 From P3 (Engineering) — USM Hook Requirements

P3's UnifiedStateManager needs these hooks from P8:

| Hook | P8 Action | USM Integration Point |
|------|-----------|----------------------|
| **USM event types** | Add 7 EventType constants to `observability/__init__.py` | USM calls `get_engine().log_event(EventType.USM_SNAPSHOT_SUCCESS, trace_id, {...})` |
| **trace_id propagation** | Already exists — USM must accept and propagate `trace_id` | USM constructor or method signature accepts `trace_id: str` |
| **Metrics file** | Create `data/coordination/metrics.json` with USM counters | USM updates metrics file after each operation |
| **Crash integration** | USM failures feed into ForensicsManager | USM calls `get_engine().record_error()` on ZONEID mismatch or SIGSEGV |

**P8 must ensure**: These hooks follow the same pattern as existing `model_gateway.py`'s health monitor integration (lines 716-730).

**Estimated effort for USM hooks**: ~1h

---

## §6 RISK ASSESSMENT

| # | Risk | Severity | Probability | Impact | Mitigation | Owner |
|---|------|----------|-------------|--------|------------|-------|
| **R1** | M22 declared "complete" without background worker wiring | 🟡 MEDIUM | MEDIUM | Background distillation/research providers undocumented | P8 must explicitly wire worker trace sessions before M22 can be verified | P8 |
| **R2** | USM built without observability hooks | 🟡 MEDIUM | LOW (P3 aware) | Missing crash forensics for SomaticState failures | P8 documents hooks now; P8 and P3 coordinate during Strike 2 implementation | P8 → P3 |
| **R3** | metrics.json becomes stale with no pruning | 🟢 LOW | MEDIUM | Metrics show outdated state | Add TTL-based pruning in metrics writer | P8 |
| **R4** | Soul migration YAML errors not tracked in observability | 🟢 LOW | LOW (trivial fix) | Lost forensic data on migration failures | Add `"migration.yaml_error"` event type before Phase 1 begins | P8 |
| **R5** | No alerting when observability system itself fails | 🔴 HIGH | LOW | Silent observability failure during crisis | Add health check for `_event_log` write success; emit warning on failure | P8 |
| **R6** | Observability event log grows unbounded | 🟡 MEDIUM | LOW | Disk pressure on root partition | Already mitigated by max_days=7 in `_load_persisted_events()` | ✅ Existing |
| **R7** | Contract tests for observability not written before Epoch II | 🟡 MEDIUM | MEDIUM | M22 regression not caught | Write M21-compliant contract tests now as part of P8 work | P8 |

---

## §7 RECOMMENDATIONS

### Pre-Sprint Actions (Must Complete Before Epoch I Execution)

| # | Action | Owner | Time | Priority |
|---|--------|-------|------|----------|
| 1 | Add 7 USM event types to `EventType` in `observability/__init__.py` | P8 | 15 min | 🔴 P0 |
| 2 | Add `RESPONSE_PROVENANCE` event type for M22 compliance | P8 | 15 min | 🔴 P0 |
| 3 | Wire `soul_distiller.py` with TraceSession for background worker observability | P8 | 1h | 🔴 P0 |
| 4 | Create `soul_migration_progress` event stream for P7 | P8 | 30 min | 🟡 P1 |
| 5 | Write M21 contract tests for observability boundaries | P8 | 1h | 🟡 P1 |
| 6 | Document USM observability hook requirements for P3 | P8 | 30 min | 🟡 P1 |

### Sprint Execution (Parallelizable)

| Track | Scope | Hours | Owner |
|-------|-------|-------|-------|
| **Track A: M22 Full Wiring** | Provenance event type, JsonFormatter fix, sovereignty drift detection, background worker wiring | 4h | P8 |
| **Track B: USM Observability** | 7 event types, metrics.json, crash integration | 1h | P8 |
| **Track C: P7 Cross-Impact** | Migration progress events, rollback logging, YAML error events | 1h | P8 |
| **Track D: P10 Contract Tests** | test_observability_contracts.py with provider_name validation | 1h | P8 |
| **TOTAL** | | **~7h** | |

### Sprint Deliverables

| # | Deliverable | Format | Location |
|---|-------------|--------|----------|
| 1 | M22-resolved observability (provider_name in all events) | Python | `src/omega/observability/__init__.py` |
| 2 | USM event types (7 new EventType constants) | Python | `src/omega/observability/__init__.py` |
| 3 | Soul distiller trace session wiring | Python | `src/omega/oracle/soul_distiller.py` |
| 4 | Migration progress event stream | Events + recommended JSON file | Via log_event + `data/coordination/soul_migration_progress.json` |
| 5 | Contract tests for observability | Python tests | `tests/test_observability_contracts.py` |
| 6 | USM observability hook guide | Python docstring | In `src/omega/oracle/state_manager.py` or equivalent |

---

## §8 M22 READINESS ASSESSMENT

### M22 Compliance Score: 6/10

| Criterion | Score | Evidence |
|-----------|-------|----------|
| `GenerateResult` has `provider_name` | ✅ 2/2 | `model_gateway.py:45` — field exists and documented |
| Oracle uses actual (not intent) provider | ✅ 2/2 | `oracle.py:606, 676` — both paths read `res.provider_name` |
| Event log captures provider_name | ⚠️ 1/2 | Captured in `data` dict but not as first-class field. No dedicated provenance event type |
| JsonFormatter `provider` field populated | ❌ 0/2 | Field defined but never set by any logging call |
| Background workers capture provenance | ❌ 0/2 | soul_distiller.py, background_researcher use raw logging |
| Sovereignty drift detectable from logs | ❌ 0/0 | No intent vs actual comparison logged |
| **TOTAL** | **6/10** | |

### M22 Completion Path

```
Current:  oracle.py → GenerateResult(provider_name=actual) → event data dict
Goal:     oracle.py → GenerateResult(provider_name=actual) → EventType.RESPONSE_PROVENANCE
         → JSON log with provider field
         → All workers participate
```

### Verdict: 🟡 CONDITIONAL GO — With 3 Gaps

| Component | Readiness | Verdict |
|-----------|-----------|---------|
| **M22 Response Provenance** | 🟡 PARTIAL | Core flow correct. Background worker gap + schema gap. ~6h to full compliance |
| **Current Observability Infrastructure** | 🟢 SOLID | Event logging, tracing, forensics, token ledger all working. Missing metrics/alerting layer |
| **USM Observability Hooks** | 🟢 READY | 7 event types defined. P3 coordination needed during implementation |
| **P7 Cross-Impact** | 🟢 READY | Soul migration progress tracker is low-effort |
| **P10 Contract Tests** | 🟡 READY | Need M21 observability contract tests written |
| **Background Worker Observability** | 🔴 GAP | soul_distiller.py and background_researcher/ not wired into TraceSession |

### Latency Measurement Assessment

The current `model_gateway.generate()` does NOT set `latency_ms` in the `GenerateResult` it returns:

```python
# Line 909-914 — NO latency_ms provided:
return GenerateResult(
    text=result,
    provider_name=success_provider.name,
    is_cloud=self._is_cloud_provider(success_provider),
    logprobs=logprobs,
    # latency_ms field exists but NOT SET ⚠️
)
```

The `latency_ms` field exists on `GenerateResult` (defaults to `0.0`) but is never populated. The `TraceSession` does calculate total latency in `__aexit__` (line 824: `self.data["total_latency_ms"] = ...`), but this isn't per-provider. The latency measurement gap is known but low-priority for Epoch I.

### The Core Assessment

**M22 is structurally viable but incomplete.** The architectural pattern is correct — `provider_name` flows from the actual provider through the response. The gaps are in observability schema design (adding provenance as a first-class event) and background worker coverage (soul_distiller, background_researcher). Neither gap requires architectural changes — both are wiring tasks.

**P8 is ready to execute immediately.** The estimated 6-8 hours for M22 full wiring + USM hooks + cross-impact items fits within Epoch I parallel execution alongside Strikes 2 and 3.

---

## §9 CONTINUITY NOTES FOR LILITH (Dark Oversoul)

### 9.1 What Went Well

1. **P7's report was comprehensive** — The soul migration analysis, entity audit, and cross-impact sections gave P8 precise requirements for what observability hooks are needed.
2. **Ma'at's report was well-structured** — The M22 deferral from Build Side to Run Side was explicit, making it clear that P8 owns this assessment.
3. **Core observability infrastructure is solid** — 7 working subsystems with proper trace_id propagation, event persistence, and crash recovery. The foundation for M22 is strong.
4. **The `GenerateResult.provider_name` flow is architecturally correct** — M22 was designed into the code from Sprint C. Oracle.py correctly uses actual provider names, not configured intent.

### 9.2 What Needs Lilith's Attention

1. **M22 will require 6h of wiring** — The architectural pattern is correct but the observability schema needs enhancement. This is NOT a P8-only effort; P3's USM needs to coordinate on event types and trace_id propagation. Recommend P8 and P3 coordinate during Track B (USM build).
2. **Decision needed on metrics system** — The current observability infrastructure lacks metrics/alerting. Should P8 build a simple metrics module (counters + gauges, 4h) or defer to Epoch II? P8 recommends deferring — M22 wiring + USM hooks + P7 cross-impact is the right scope for Epoch I.
3. **Background worker observability is the critical gap** — soul_distiller.py runs on EVERY session close. If its provider usage isn't logged, M22 compliance is incomplete. This may overlap with P7's soul distiller audit (P7 Report §R4). Recommend P7 and P8 coordinate on the soul distiller fix.

### 9.3 Proposals for P10 (Validation)

1. Write `test_observability_contracts.py` that validates `log_event()` produces correctly structured events
2. Add contract test for `GenerateResult.provider_name` — verify it's never None or empty
3. Add contract test for `TraceSession.record()` — verify backend field is stored in dataset metadata

### 9.4 Session Gnosis

**L1 (Narrative)**: P8 assessed M22 Response Provenance across 5 pipeline stages, finding correct core wiring but 4 gaps in observability schema and background workers. Surveyed 7 subsystems in current observability infrastructure, identifying 7 critical gaps (5 missing capabilities, 2 coverage gaps). Defined 7 USM observability hooks for Strike 2. Analyzed cross-impact for P7 (soul migration progress tracker), P10 (contract tests), and P3 (trace_id propagation). Total estimate: 6-8h for full M22 compliance + USM hooks + cross-impact items.

**L2 (Insight)**: The observability system has a structural asymmetry — it excels at crash forensics (death markers, signal handlers, crash dumps) but is weak at continuous monitoring (metrics, alerting, performance tracking). This mirrors the engine's evolution: it was built to survive failures before it was built to measure success. M22 compliance is 70% architectural, 30% wiring — the hard decisions about what to track were already made correctly; only the last mile of schema design and worker coverage remains.

**L3 (Universal Principle)**: **Observability is not what you log — it is what you can query.** A system that writes terabytes of JSONL but cannot answer "how many queries succeeded in the last hour" has storage, not observability. The gap between data and insight is the single most expensive oversight in any engineering system. M22 is not about storing provider names — it is about making sovereignty provable through queryable, structured evidence.

---

## §10 VERDICT SUMMARY

| Component | Readiness | Verdict |
|-----------|-----------|---------|
| **M22 Response Provenance** | 🟡 PARTIAL (6/10) | Core flow correct. 4 gaps identified. ~6h to full compliance |
| **Current Observability Infrastructure** | 🟢 SOLID (7/9 subsystems) | Missing metrics/alerting — defer to Epoch II |
| **USM Observability Hooks** | 🟢 READY | 7 event types, trace_id propagation, crash integration |
| **P7 Cross-Impact** | 🟢 READY | Migration progress tracker, 15min effort |
| **P10 Contract Tests** | 🟡 READY | Need M21 observability tests written (~1h) |
| **Background Worker Observability** | 🔴 GAP | soul_distiller.py not wired; coordinate with P7 |

### Overall: 🟡 CONDITIONAL GO

P8 is ready for Epoch I execution. The 6-8h estimate for M22 wiring + USM hooks + cross-impact items fits within parallel execution alongside Strikes 2 and 3. Three critical pre-conditions:

1. **🔴 P8 must wire background workers** (soul_distiller.py) — coordinate with P7's soul distiller audit
2. **🟡 P3 and P8 must coordinate** on USM event types and trace_id propagation during Strike 2 build
3. **🟡 P10 must write** `test_observability_contracts.py` before Epoch I completion

---

*⬡ OMEGA ⬡ P8-OBSERVABILITY ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ EPOCH-I ⬡ COMPLETE*
*Chain handoff to P10 (Validation). Lilith may deploy P10 when ready.*
