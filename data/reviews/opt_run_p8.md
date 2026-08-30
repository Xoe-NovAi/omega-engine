<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 P8 Observability — Tracking & Data Lifecycle Optimization

**Pillar**: P8 (Observability — WatchTower)
**Reporting to**: Lilith (Dark Oversoul)
**Date**: 2026-06-27
**Status**: 🔴 CRITICAL GAPS — Remediation Required
**Session**: DISCOVERY-ONLY PASS — No refactoring

---

## Executive Summary

The Omega Engine's observability infrastructure has strong *code architecture* (ObservabilityEngine with 7 subsystems, ForensicsManager with signal handlers, TraceSession, JsonFormatter, TokenLedger) but **critical gaps in trace_id propagation**, **overwhelmingly noisy event data** (98.9% token.consumption), and **missing retention policies** on unbounded files.

**Key Metric**: 1,535 of 1,561 total events (98.4%) have `trace_id: "unknown"` — meaning the observability system cannot link 98% of its data to any specific user interaction. The trace chain is broken.

**Prior reviews** (P8_SPRINT_REPORT_20260624.md, P8_OBSERVABILITY_FINAL_REVIEW_20260625.md, run_P8.md) flagged the propagation gap. **No fix has been applied.** This report provides a fresh audit of the actual on-disk state.

---

## §1 Log Volume Analysis

### 1.1 Total Footprint

| Location | Size | Files | Description |
|----------|------|-------|-------------|
| `data/logs/events/` | 580 KB | 14 daily `.jsonl` | Event log (2026-06-13 to 2026-06-26) |
| `data/logs/token_ledger.jsonl` | **1.6 MB** | 1 file | Token transaction ledger (8,862 lines) |
| `data/logs/metrics.json` | <1 KB | 1 | Boundary violation log |
| `data/datasets/` | **800 KB** | **196 files** | Fine-tuning dataset exports |
| `data/traces/` | **0 bytes** | EMPTY | Trace storage directory — **nothing written** |
| `data/crashes/` | 48 bytes | 1 | `death_marker.txt` (SIGTERM, 2026-06-26) |
| **Total** | **~3.0 MB** | **213 files** | |

### 1.2 Per-Session Volume

| Metric | Value |
|--------|-------|
| Avg events/day | 111 (range: 5 - 298) |
| Peak day | 2026-06-23: 298 events, 103 KB |
| Lowest day | 2026-06-16: 5 events, 1.7 KB |
| Token ledger growth | ~633 lines/day avg (8,862 lines over 14 days) |
| Dataset growth | ~14 files/day on active days |

### 1.3 Signal-to-Noise Ratio

| Event Type | Count | Percentage |
|------------|-------|------------|
| `token.consumption` | 1,536 | **98.4%** |
| `query.received` | 4 | 0.26% |
| `session.active` | 4 | 0.26% |
| `summon.detected` | 4 | 0.26% |
| `model.completed` | 3 | 0.19% |
| `iris.speculative` | 3 | 0.19% |
| `summon.direct` | 2 | 0.13% |
| `escalation` | 2 | 0.13% |
| `domain.routed` | 2 | 0.13% |
| `provider_failed` | 1 | 0.06% |
| `backend.fallback` | 1 | 0.06% |
| **Total** | **1,561** | **100%** |

**Critical finding**: 98.4% of all persisted events are `token.consumption` from background model inference. Only **25 events (1.6%)** represent actual user interactions. The event log is drowning in noise.

---

## §2 Event Type Taxonomy

### 2.1 Defined Event Types (in EventType class, 19 types)

| # | Event Type | Used in Logs? | Purpose |
|---|------------|--------------|---------|
| 1 | `query.received` | ✅ (4) | User query entry point |
| 2 | `summon.detected` | ✅ (4) | @entity summon detected |
| 3 | `domain.routed` | ✅ (2) | Entity routing decision |
| 4 | `entity.matched` | ❌ | Entity match from intent engine |
| 5 | `model.invoked` | ❌ | Model inference start |
| 6 | `model.completed` | ✅ (3) | Model inference complete |
| 7 | `backend.fallback` | ✅ (1) | Provider fallback occurred |
| 8 | `response.delivered` | ❌ | Response returned to user |
| 9 | `escalation` | ✅ (2) | Iris confidence < threshold |
| 10 | `iris.speculative` | ✅ (3) | Iris speculative decode result |
| 11 | `boundary.violation` | ❌ | Tool boundary violation |
| 12 | `gnosis.redaction` | ❌ | Knowledge update/redaction |
| 13 | `error` | ❌ | Error event type |
| 14 | `worker.start` | ❌ | Background worker start |
| 15 | `worker.complete` | ❌ | Background worker complete |
| 16 | `worker.update` | ❌ | Background worker update |
| 17 | `worker.report` | ❌ | Background worker report |
| 18 | `tier.invoked` | ❌ | Research tier invoked |
| 19 | `mode.switched` | ❌ | Inference mode switched |
| 20 | `agent.dispatched` | ❌ | Agent dispatched |
| 21 | `research.complete` | ❌ | Research complete |
| 22 | `token.consumption` | ✅ (1,536) | Token usage event |
| 23 | `entity.interaction` | ❌ | Entity interaction recorded |

### 2.2 Redundancy Analysis

- **`summon.direct` vs `summon.detected`**: Both track entity summoning. `summon.direct` appears to be a different code path from `summon.detected`. Potential redundancy — oracle.py uses `summon.detected` for both `_detect_summon` and `_detect_consult` paths.
- **`model.invoked` and `model.completed`**: `model.invoked` is never emitted despite being defined. Only `model.completed` fires.
- **`worker.*` events**: 4 worker event types defined but **none are ever emitted**. Background workers (soul_distiller, background_researcher) use raw `logger.info()` calls instead of structured events.

### 2.3 Missing Event Types (Critical Gaps)

| Missing Event | Why Needed | Impact |
|---------------|-----------|--------|
| `RESPONSE_PROVENANCE` | M22 requires actual provider as first-class field, not buried in `data` dict | Cannot query "which provider served which response?" efficiently |
| `USM.SNAPSHOT_*` | SomaticState lifecycle tracking (P3 USM) | No crash forensics for KV cache snapshots |
| `GNOSIS_DISTILLATION` | L1→L2→L3 pipeline events (M11) | Cannot track soul evolution timing |
| `migration.*` | P7 soul migration progress | Cannot detect rollbacks or YAML errors |
| `latency` | Per-provider performance | No P95 response time tracking |
| `budget.alert` | BudgetGate threshold events | Cloud spend violations invisible in logs |

---

## §3 Trace & Span Audit

### 3.1 trace_id Propagation Health

| Source of Event | Valid trace_id? | Count | % of Total |
|----------------|----------------|-------|------------|
| From `oracle.talk()` → direct user interactions | ✅ Valid `trc_*` IDs | 26 | 1.7% |
| From `model_gateway.generate()` → TokenLedger | ❌ `"unknown"` | 1,535 | **98.3%** |

**Root cause**: Two `oracle.py` call sites do NOT pass `trace_id` to `model_gateway.generate()`:

1. **`_summon_direct()` (line 599-604)** — The primary summon path:
```python
res = await self.model_gateway.generate(
    model_name=model_name,
    system_prompt=effective_system_prompt,
    user_query=query,
    temperature=effective_temperature,
    max_tokens=effective_max_tokens,
    # ← trace_id MISSING, entity_name MISSING
)
```

2. **`_route_by_domain()` (line 671-677)** — The domain-routed path:
```python
res = await self.model_gateway.generate(
    model_name=model_name,
    system_prompt=system_prompt,
    user_query=text,
    temperature=entity.temperature,
    max_tokens=1024,
    # ← trace_id MISSING, entity_name MISSING
)
```

**Impact cascade**:
1. oracle.py doesn't pass trace_id → model_gateway.generate() receives `trace_id=None`
2. model_gateway.generate() passes `trace_id or "unknown"` to `TokenLedger.record_transaction()`
3. TokenLedger logs `trace_id: "unknown"` in both the event log AND the JSONL ledger
4. ALL 1,536 `token.consumption` events and ALL 8862 token ledger entries have `trace_id: "unknown"`
5. `provider_failed` and `backend.fallback` events also have `trace_id: "unknown"`

**Status**: This was flagged as 🔴 CRITICAL in P8_OBSERVABILITY_FINAL_REVIEW (2026-06-25). **No fix has been applied in 2 days.**

### 3.2 Additional Propagation Gaps

| Call Site | File:Line | trace_id? | entity_name? |
|-----------|-----------|-----------|-------------|
| IterativeResearch._gap_analysis | iterative_research.py:64 | ❌ NO | ❌ NO |
| IterativeResearch._synthesize | iterative_research.py:143 | ❌ NO | ❌ NO |
| IterativeResearch._extract_claims | iterative_research.py:159 | ❌ NO | ❌ NO |
| SkepticalVerifier._nli_check | skeptical_verifier.py:130 | ❌ NO | ❌ NO |
| SkepticalVerifier._resolve | skeptical_verifier.py:171 | ❌ NO | ❌ NO |
| Orchestrator.sensing | orchestrator.py:94 | ✅ YES (`task_id`) | ❌ NO |

**Score**: 1/8 pass both trace_id AND entity_name (12.5%).

### 3.3 Storage Format

- **In-memory**: `deque` (maxlen=1000) — rolling buffer, survives within session
- **Persisted**: Daily JSONL files at `data/logs/events/{YYYY-MM-DD}.jsonl`
- **Traces**: `data/traces/` directory exists but is **empty** — no trace data is ever written
- **Token ledger**: `data/logs/token_ledger.jsonl` — append-only, unbounded

### 3.4 Pruning

- **Event log**: `_load_persisted_events(max_days=7)` loads only 7 days of history at startup
- **BUT**: All JSONL files are **never deleted** — they accumulate indefinitely
- **No retention policy**: 14 days of data exists, no archival or compaction
- **Token ledger**: **No pruning whatsoever** — 8,862 lines and growing

---

## §4 Fine-Tuning Data Retention

### 4.1 Inventory

| Metric | Value |
|--------|-------|
| Total files | **196** JSONL files |
| Total size | **800 KB** |
| Per-file size | Exactly **350 bytes** each |
| Per-file content | Exactly **1 training example** each |
| Date range | 2026-06-13 to 2026-06-26 (14 days) |
| Peak day | 2026-06-23: 39 files |
| Growth rate | ~14 files/day on active days |

### 4.2 Anomaly: 1 Example Per File

Every finetune file contains exactly 1 training example (350 bytes). This strongly suggests:
- **Auto-flush is NOT working as designed**: The `TraceSession.__aexit__` flushes when `len(engine._dataset) >= 100`, but files are being created for every single query
- OR: **Another code path calls `flush_dataset()` per-query** instead of batching
- OR: **The engine is restarted between each query**, resetting the in-memory buffer before it reaches 100

### 4.3 Collection Status

- `config/omega.yaml §observability`: `enable_dataset_collection: true`
- `ObservabilityEngine.__init__` default: `enable_dataset_collection: bool = False`
- `get_engine()` creates: `ObservabilityEngine()` — **no config overrides**
- **Actual status**: Likely **DISABLED** — the config value is never loaded and passed to the constructor

### 4.4 Retention Policy

**None**. Files accumulate indefinitely with no archival, compaction, or deletion.

---

## §5 Forensic Readiness

### 5.1 What Works

- ✅ **Signal handlers installed**: SIGSEGV, SIGABRT, SIGILL, SIGFPE, SIGTERM all caught
- ✅ **Death marker**: Written on signal (evidence: `death_marker.txt` from SIGTERM on 2026-06-26)
- ✅ **ForensicsManager**: Full `snapshot()` method with deep state capture (thread dumps, memory maps, FD audit)
- ✅ **Replay()**: Can reconstruct event timeline from persisted JSONL
- ✅ **Persistent writes**: `os.fsync()` on crash dump writes

### 5.2 What's Missing

- ❌ **No crash dump JSON files ever created**: `ForensicsManager.snapshot()` has never been called in production. Only `write_death_marker()` fires (synchronous signal handler).
- ❌ **Broken trace_id prevents timeline reconstruction**: Even if crash dumps existed, 98.4% of events have `trace_id: "unknown"`, making `replay()` useless.
- ❌ **No provider performance history**: Circuit breaker state is in-memory only. A crash resets all performance history.
- ❌ **No SomaticState snapshots**: USM not yet integrated, so no KV cache state to recover.
- ❌ **No periodic health snapshots**: `snapshot()` is manual-only — no scheduled dumps.

### 5.3 Production Debugging Assessment

> **Can we debug a production issue?** — 🔴 **NO, with caveats**

| Scenario | Debuggable? | Reason |
|----------|------------|--------|
| "Why did the model return gibberish?" | ❌ No | No trace_id linking query to response. Token ledger has "unknown" for everything. |
| "Why did the engine crash?" | 🟡 Partial | Death marker says SIGTERM but no crash dump context. No provider state, no event timeline. |
| "When did we hit budget limit?" | ❌ No | Token ledger tracks tokens but with 0 prompt_tokens for most entries (estimation issue) and no entity attribution. |
| "Why did a query take 30 seconds?" | ❌ No | `latency_ms` is always 0.0 in GenerateResult. |
| "Which provider served most queries?" | ❌ No | Provider name recorded in events but 98.4% of events are token.consumption (which records `is_cloud` but NOT `provider_name` in its data dict). |

---

## §6 Observability Debt Inventory

### 6.1 Dead Code

| Location | Issue | Impact |
|----------|-------|--------|
| `observability/__init__.py:15-23` | **17 of 22 imported error types unused** — OmegaError is the only one referenced in catch blocks | Dead import bloat |
| `observability/__init__.py:63` | JsonFormatter `provider` extra field — **defined but NEVER set** by any logging call | Dead code |
| `data/traces/` | Directory exists but **nothing writes to it** | Orphan directory |
| `EventType` | 13 of 23 event types **never emitted** (entity.matched, model.invoked, response.delivered, error, all worker.*, tier.invoked, mode.switched, agent.dispatched, research.complete, entity.interaction) | Dead enum values |

### 6.2 Incomplete Implementations

| Location | Issue | Since |
|----------|-------|-------|
| `model_gateway.py:886-891` | `GenerateResult.latency_ms` defaults to `0.0` — **never populated** | Engine inception |
| `oracle.py:599-604, 671-677` | **trace_id not passed** to `model_gateway.generate()` | Engine inception |
| `TokenLedger.record_transaction()` | Records `is_cloud` but NOT `provider_name` | TokenLedger inception |
| `observability/__init__.py:570-577` | `get_engine()` creates with `enable_dataset_collection=False` — config value `true` never loaded | D118 override (2026-06-01) |

### 6.3 Orphan Metrics

| Metric | Source | Status |
|--------|--------|--------|
| `data/logs/metrics.json` | Boundary violations counter | **Last entry**: 2026-06-05 — likely abandoned |
| `ObservabilityEngine.stats()` | Returns in-memory event counts only (deque max 1000) | Survives restart? **NO** — only persists on crash |

---

## §7 Log vs Monitor Gap Analysis

### 7.1 Things Being Logged That Should Be Metrics

| Log Data | Suggested Metric | Reason |
|----------|-----------------|--------|
| `token.consumption` events (98.4% of volume) | Counter: `tokens_total`, Gauge: `tokens_per_minute` | Don't need 1,536 events — need aggregate counters |
| Every provider attempt in loop | Counter: `provider.attempts{provider,model}`, `provider.errors{provider}` | Store aggregated, not per-attempt |
| Circuit breaker transitions | Gauge: `breaker.state{provider}`, Counter: `breaker.open_count` | State is more useful than transition events |

### 7.2 Things Being Monitored That Should Be Logs

| Monitor Data | Should Be Log | Reason |
|-------------|--------------|--------|
| Missing — no SLO/SLI tracking | Histograms for P50/P95/P99 latency | Need actual latency distributions, not just total_ms |
| Missing — no provider health over time | Time-series of `provider.available` | Need to know WHEN providers were unhealthy |

### 7.3 Missing Altogether

| Capability | Current State |
|-----------|--------------|
| **Counters** (total queries, total errors) | ❌ Not implemented |
| **Gauges** (active sessions, memory usage) | ❌ Not implemented |
| **Histograms** (latency P50/P95/P99) | ❌ Not implemented |
| **Alerting** (error rate thresholds) | ❌ Not implemented |
| **SLO/SLI tracking** | ❌ Not implemented |
| **Per-provider performance history** | ❌ Not persisted |
| **Health check integration** | ❌ Not linked to observability |

---

## §8 Recommendations

### 🔴 P0 — Fix trace_id Propagation (Effort: 30 min)

**Action**: Add `trace_id=trace.trace_id` and `entity_name=entity.name` to 7 call sites.

| File | Line | Current | Fix |
|------|------|---------|-----|
| `oracle.py` | 599 | `model_gateway.generate(..., trace_id=MISSING)` | Add `trace_id=trace.trace_id, entity_name=entity.name` |
| `oracle.py` | 671 | `model_gateway.generate(..., trace_id=MISSING)` | Add `trace_id=trace.trace_id, entity_name=entity.name` |
| `iterative_research.py` | 64 | `model_gateway.generate(..., trace_id=MISSING)` | Thread trace_id through IterativeResearcher |
| `iterative_research.py` | 143 | Same | Same |
| `iterative_research.py` | 159 | Same | Same |
| `skeptical_verifier.py` | 130 | `model_gateway.generate(..., trace_id=MISSING)` | Thread trace_id through SkepticalVerifier |
| `skeptical_verifier.py` | 171 | Same | Same |

**Impact**: Fixing this single issue will turn 1,535 orphan events into traceable interactions.

### 🟡 P1 — Add Token Ledger Retention Policy (Effort: 1 hr)

**Action**: Add compaction to `token_ledger.jsonl`:
- Archive entries older than 30 days to `data/logs/archive/`
- Add TTL-based pruning (cvar: `ledger.retention_days` default 30)
- Add `provider_name` field to token ledger transactions

**Impact**: Prevent unbounded disk growth (1.6 MB in 14 days = ~34 MB/year).

### 🟡 P1 — Suppress `token.consumption` Event Noise (Effort: 2 hr)

**Action**: Two options:
- **Option A (recommended)**: Convert `token.consumption` from per-call events to **aggregated counters** stored in a separate `data/logs/token_stats.jsonl` with hourly rollups
- **Option B**: Add cvar to control sampling rate (e.g., `log 1 in N token events`)

**Impact**: Reduce event log volume by 98%, making monitoring dashboards actually useful.

### 🟡 P1 — Fix Dataset Collection Bootstrap (Effort: 30 min)

**Action**: Verify and fix the bootstrap path:
1. Ensure `OmegaConfigReader` loads `observability.enable_dataset_collection`
2. Pass it to `ObservabilityEngine(enable_dataset_collection=config_value)`
3. Add startup log: `observability.dataset_collection = true|false`
4. Batch flush to 1 file per N examples instead of 1 file per example

**Impact**: If users want fine-tuning data, the pipeline actually works.

### 🟢 P2 — Add RESPONSE_PROVENANCE Event Type (Effort: 30 min)

**Action**: Add `EventType.RESPONSE_PROVENANCE` and emit from `oracle.py` after successful generation, with `provider_name` as a top-level field (not buried in `data` dict).

**Impact**: M22 compliance becomes queryable — "which provider served this response?" becomes a first-class field.

### 🟢 P2 — Close the JsonFormatter `provider` Gap (Effort: 1 hr)

**Action**: Either wire `logging.setLogRecordFactory()` to inject `provider_name` at log points, or remove the unused `provider` key from JsonFormatter.

**Impact**: Fix dead code and enable structured provider logging.

### 🟢 P2 — Add Periodic Forensics Snapshots (Effort: 2 hr)

**Action**: Schedule `ForensicsManager.snapshot()` on:
1. Engine startup (baseline)
2. Every 1000 interactions (rolling health check)
3. Circuit breaker open events
4. Engine shutdown (clean state)

**Impact**: When a crash happens, you have recent state to compare against.

---

## §9 Retention Policy Draft

### 9.1 Proposed Rules

| Data Class | Location | Retention | Action | Implementation |
|------------|----------|-----------|--------|---------------|
| **Event logs** | `data/logs/events/*.jsonl` | 30 days | Archive then delete | Add pruning loop in `ObservabilityEngine.__init__` or startup |
| **Token ledger** | `data/logs/token_ledger.jsonl` | 90 days | Compact then archive | Add `TokenLedger.compact()` with cvar `ledger.retention_days` |
| **Fine-tuning datasets** | `data/datasets/*.jsonl` | Indefinite (user opt-in) | Archive flagged | Move to `data/datasets/archive/` after 90 days; never auto-delete |
| **Crash dumps** | `data/crashes/crash_*.json` | 180 days | Archive | Move to `data/crashes/archived/` after 30 days |
| **Traces (future)** | `data/traces/*.json` | 7 days | Delete | Trace data is ephemeral; only useful for active debugging |

### 9.2 Implementation Strategy

```python
# Proposed cvar_table entries
# config.observability.retention_days = 30
# config.observability.ledger_retention_days = 90
# config.observability.crash_retention_days = 180

async def enforce_retention_policy():
    """Run at startup and periodically."""
    retention_days = cvar_get("config.observability.retention_days", 30)
    cutoff = datetime.now() - timedelta(days=retention_days)
    
    # Archive old event logs
    for path in Path("data/logs/events").glob("*.jsonl"):
        date_str = path.stem  # YYYY-MM-DD
        file_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if file_date < cutoff.date():
            # Archive then delete
            archive_dir = Path("data/logs/archive")
            archive_dir.mkdir(parents=True, exist_ok=True)
            path.rename(archive_dir / f"{path.stem}.jsonl.archive")
    
    # Compact token ledger
    ledger_cutoff = datetime.now() - timedelta(
        days=cvar_get("config.observability.ledger_retention_days", 90)
    )
    await TokenLedger().compact(older_than=ledger_cutoff)
```

---

## §10 L1→L2→L3 Distillation

### L1 (Narrative)
Audited 213 observability files across 5 data directories (~3.0 MB total). Found that the ObservabilityEngine has 7 well-structured subsystems (event logging, trace sessions, training datasets, crash forensics, token ledger, JSON formatting, ZONEID marking) but **98.4% of persisted events have `trace_id: "unknown"`** because 2 oracle.py call sites don't propagate the trace_id. The token ledger grows unbounded at ~633 lines/day. Fine-tuning dataset collection is likely disabled due to a bootstrap gap. Data/traces directory sits empty.

### L2 (Insight)
The observability system has a **structural asymmetry**: it's excellent at crash survival (signals, fsync, death markers) but fundamentally broken at data linking (trace_id propagation). The engine was built to survive crashes before it was built to deliver queryable, structured evidence. The 98.4% orphan rate means the entire observability investment is wasted on noise — you can't answer "which query caused this error?" because the trace chain doesn't connect.

The token ledger is the biggest growth vector: 1.6 MB in 14 days from ~8K transactions. Without retention policies, this grows ~34 MB/year — manageable but symptomatic of a "never delete" philosophy that will accumulate across all observability data classes.

### L3 (Universal Principle)
**Observability without traceability is storage, not insight.** A system that logs 1,500 events but cannot answer "what happened during this interaction?" has built a noise archive, not an observability system. The trace_id is the primary key of observability — when 98% of rows have NULL for the primary key, the entire schema is degraded. Fix the key first, then fix the schema, then fix the retention.

---

*⬡ OMEGA ⬡ P8 ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_observability_audit ⬡ DISCOVERY-COMPLETE*
