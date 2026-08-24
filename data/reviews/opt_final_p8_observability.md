# 🔱 P8 Observability — Final Cross-Domain Review
## Trace Quality, Event Classification, Retention & Consolidation

**Pillar**: P8 (Observability — WatchTower)
**Date**: 2026-06-28
**Status**: 🔴 CRITICAL — Systemic trace_id gap renders 98.4% of observability investment wasted
**Inputs**: `MAAT_BUILD_OPT_CONSOLIDATED.md` + `LILITH_RUN_OPT_CONSOLIDATED.md` + `opt_run_p8.md`

⬡ OMEGA ⬡ P8 ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_p8_final_review ⬡ SYNTHESIS

---

## Executive Summary

The build-side (Ma'at) and run-side (Lilith) optimization passes identified **49 actionable findings** across 8 pillars (P1-P9). Of these, **5 are directly in P8's domain**, but **2 more are cross-pillar issues that require P8 intervention** (the trace_id propagation gap affects M9 Error Integrity, and the token ledger noise affects forensic readiness).

The single most impactful fix — across the entire engine — is wiring `trace_id` at 2 call sites in `oracle.py`. This restores traceability to 98.4% of all observability data. Everything else is secondary.

Below is my consolidated analysis across the 4 requested dimensions.

---

## §1 Trace Quality Improvement Plan

### 1.1 Root Cause Analysis

The trace_id chain is broken at precisely 2 points in `oracle.py`, with 5 additional propagation gaps in sub-systems:

| # | Call Site | File:Line | trace_id Passed? | entity_name Passed? | Impact |
|---|-----------|-----------|-----------------|-------------------|--------|
| **P0** | `_summon_direct()` | `oracle.py:599` | ❌ | ❌ | 98.4% of events orphaned |
| **P0** | `_route_by_domain()` | `oracle.py:671` | ❌ | ❌ | 98.4% of events orphaned |
| P1 | `IterativeResearch._gap_analysis` | `iterative_research.py:64` | ❌ | ❌ | Research events untraceable |
| P1 | `IterativeResearch._synthesize` | `iterative_research.py:143` | ❌ | ❌ | Research events untraceable |
| P1 | `IterativeResearch._extract_claims` | `iterative_research.py:159` | ❌ | ❌ | Research events untraceable |
| P1 | `SkepticalVerifier._nli_check` | `skeptical_verifier.py:130` | ❌ | ❌ | Verification events untraceable |
| P1 | `SkepticalVerifier._resolve` | `skeptical_verifier.py:171` | ❌ | ❌ | Verification events untraceable |
| P2 | `Orchestrator.sensing` | `orchestrator.py:94` | ✅ (task_id) | ❌ | Partial — wrong key format |

**Propagation chain**:
```
oracle.talk() → trace = self.observability.trace()  # ✅ trace_id created
  ├→ _summon_direct()                               # ❌ does NOT pass trace_id
  │   └→ model_gateway.generate(…, trace_id=None)    # receives None
  │       └→ TokenLedger.record_transaction(trace_id or "unknown")
  │           └→ event["trace_id"] = "unknown"       # 💥 BREAKS HERE
  │           └→ token_ledger.jsonl writes "unknown"
  └→ _route_by_domain()                              # ❌ does NOT pass trace_id
      └→ model_gateway.generate(…, trace_id=None)    # same cascade
```

### 1.2 Fix Strategy (3 Phases)

#### Phase 0 — Emergency Patch (< 30 min, single file)

**Action**: Add 2 parameters to 2 `generate()` call sites in `oracle.py`:

```python
# oracle.py:599 — _summon_direct()
res = await self.model_gateway.generate(
    model_name=model_name,
    system_prompt=effective_system_prompt,
    user_query=query,
    temperature=effective_temperature,
    max_tokens=effective_max_tokens,
    trace_id=trace.trace_id,         # ← ADD
    entity_name=entity.name,          # ← ADD
)

# oracle.py:671 — _route_by_domain()
res = await self.model_gateway.generate(
    model_name=model_name,
    system_prompt=system_prompt,
    user_query=text,
    temperature=entity.temperature,
    max_tokens=1024,
    trace_id=trace.trace_id,         # ← ADD
    entity_name=entity.name,          # ← ADD
)
```

**Impact**: Restores traceability to **1,535/1,561 events** (98.4%). The remaining 26 events (from `oracle.talk()` direct path) already have valid trace_ids, so this closes the gap entirely for the primary inference path.

**Verification**: After fix, grep the event log for `"trace_id": "unknown"` — should drop to ~0 for new events.

#### Phase 1 — Sub-System Wiring (< 2 hr, 5 files)

**Action**: Thread `trace_id` and `entity_name` through:
1. `IterativeResearcher` constructor — accept and store `trace_id` + `entity_name`
2. `SkepticalVerifier` constructor — accept and store `trace_id` + `entity_name`
3. Both pass to `model_gateway.generate()` on internal calls

**Design pattern**: Add optional `trace_id: Optional[str] = None` and `entity_name: Optional[str] = None` to the constructor of both classes. The caller (`oracle.py`'s talk/summon methods) passes them when creating instances. Default `None` preserves backward compatibility.

```python
class IterativeResearcher:
    def __init__(self, ..., trace_id: Optional[str] = None, entity_name: Optional[str] = None):
        self._trace_id = trace_id
        self._entity_name = entity_name
```

#### Phase 2 — Contract Enforcement (< 4 hr)

**Action**: Add a `@validated_generate` wrapper to `model_gateway.generate()` that:
1. **Logs a warning** when `trace_id` is None (catches new propagation gaps)
2. **Injects a fresh trace_id** when None instead of `"unknown"` (degraded but functional)

```python
async def generate(self, ..., trace_id: Optional[str] = None, ...):
    if trace_id is None:
        logger.warning(
            f"generate() called without trace_id from {inspect.stack()[1].function} "
            f"in {inspect.stack()[1].filename}"
        )
        trace_id = new_trace_id()
    ...
```

This creates a self-healing system: even if new call sites forget trace_id, the contract degrades gracefully and logs a warning that makes the gap visible.

### 1.3 Monitoring & Verification

| Metric | Current | Target | How to Measure |
|--------|---------|--------|----------------|
| Events with `trace_id: "unknown"` | 98.4% | < 5% | `grep -c '"trace_id": "unknown"' data/logs/events/*.jsonl` |
| `generate()` calls with None trace_id | ~100% | 0% | Add runtime counter in model_gateway |
| Event correlation rate | 1.6% (26/1,561) | > 95% | Events per distinct trace_id |

---

## §2 Event Classification System — Signal vs. Noise

### 2.1 Current State

From 1,561 persisted events across 14 days:

| Classification | Event Types | Count | % of Total | Definition |
|---------------|------------|-------|------------|------------|
| **Noise** | `token.consumption` | 1,536 | 98.4% | Generated by background inference; no actionable information per-event |
| **Signal** | `query.received`, `session.active`, `summon.detected`, `model.completed`, `iris.speculative`, `summon.direct`, `domain.routed`, `provider_failed`, `backend.fallback` | 25 | 1.6% | Direct user interactions or critical infrastructure events |

### 2.2 Proposed 3-Tier Classification

```yaml
event_classes:
  critical:   # Retained 100% — forensic necessity
    - provider_failed
    - backend.fallback
    - error
    - boundary.violation
    - budget.alert             # NEW — M22 budget compliance
    
  signal:     # Retained 100% — user interaction + routing decisions
    - query.received
    - summon.detected
    - domain.routed
    - response.delivered       # REACTIVATE — currently dead enum
    - escalation
    - iris.speculative
    - gnosis.redaction
    - entity.interaction
    - response.provenance      # NEW — M22 compliance
    
  metric:     # Sampled/aggregated — not stored as per-event rows
    - token.consumption        # → hourly aggregated counters
    - model.invoked            # → REACTIVATE as sampled (1:100)
    - model.completed          # → REACTIVATE as sampled (1:100)
    - worker.*                 # → REACTIVATE as aggregated
```

### 2.3 Token Consumption — Aggregation Strategy

Instead of 1,536 per-call events, implement **hourly token stats**:

```python
@dataclass
class TokenStats:
    hour: str                    # "2026-06-28T14:00:00Z"
    entity: str
    provider: str
    total_prompt_tokens: int
    total_completion_tokens: int
    cloud_cost: float
    call_count: int
    trace_sample: List[str]      # last 3 trace_ids for audit trail
```

**Storage**: Single `data/logs/token_stats.jsonl` — 1 row per entity per provider per hour.
**Estimated reduction**: 1,536 events/day → ~24-48 rows/day (1-2 per entity per hour). **~97% reduction** in event volume.

**Implementation**: `TokenLedger` accumulates in-memory counters and flushes hourly (or on `flush_dataset()`). Only writes to the event log on:
- First token usage of the hour (creates the row)
- Every N calls as a heartbeat (configurable via cvar)
- Manual flush on graceful shutdown

### 2.4 Signal-to-Noise Ratio Target

| Metric | Current | Target | Method |
|--------|---------|--------|--------|
| Event log SNR | 1.6% | > 50% | Aggregate token stats + suppress per-call events |
| Storage SNR | 98.4% noise | < 30% noise | Same + retention policies |
| Actionable events per day | ~2 | > 15 | Add RESPONSE_PROVENANCE + latency histograms |

---

## §3 Retention Policy Framework

### 3.1 Current State (No Retention)

| Data Class | Location | Size | Growth Rate | Retention |
|------------|----------|------|-------------|-----------|
| Event logs | `data/logs/events/*.jsonl` | 580 KB | ~40 KB/day | Forever |
| Token ledger | `data/logs/token_ledger.jsonl` | 1.6 MB | ~114 KB/day | Forever |
| Finetune datasets | `data/datasets/*.jsonl` | 800 KB | ~57 KB/day (active) | Forever |
| Traces | `data/traces/` | 0 bytes | N/A | N/A (empty) |
| Crash dumps | `data/crashes/` | 48 bytes | Rare | Forever |

### 3.2 Proposed Per-Event-Class Retention

```yaml
retention_policy:
  default_ttl_days: 30
  enforcement_hook: startup + daily heartbeat
  
  event_log:
    retention_days: 30
    post_expiry: archive to data/logs/archive/{YYYY-MM}.jsonl
    compaction: keep 1 sample per hour after 7 days
    per_class_overrides:
      critical: 365     # provider_failed, error — keep for legal/audit
      signal: 90         # user interactions — keep for UX analysis
      metric: 7          # aggregated token stats — ephemeral
    
  token_ledger:
    retention_days: 90
    post_expiry: compact to monthly summary
    compaction:
      older_than_days: 30
      aggregate_by: [entity, provider, month]
      fields: [total_prompt, total_completion, total_cost, call_count]
    
  finetune_datasets:
    retention: indefinite  # user opt-in data
    post_expiry: move to data/datasets/archive/
    never_auto_delete: true  # user-generated training data
    
  traces:
    retention_days: 7
    post_expiry: delete  # traces are ephemeral debugging tools
    
  crash_dumps:
    retention_days: 180
    post_expiry: archive to data/crashes/archived/
    keep_last: 5  # keep the 5 most recent even if over 180 days
```

### 3.3 Implementation: `enforce_retention_policy()`

```python
async def enforce_retention_policy(engine: ObservabilityEngine) -> int:
    """Enforce retention policy across all observability data stores.
    
    Called at startup and on daily heartbeat.
    Returns number of files archived/deleted.
    """
    now = datetime.now(timezone.utc)
    archived = 0
    
    # 1. Event log retention
    retention_days = cvar_get("config.observability.retention_days", 30)
    cutoff = now - timedelta(days=retention_days)
    
    events_dir = DATA_DIR / "logs" / "events"
    if events_dir.exists():
        archive_dir = DATA_DIR / "logs" / "archive"
        for path in sorted(events_dir.glob("*.jsonl")):
            date_str = path.stem  # "2026-06-01"
            try:
                file_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if file_date < cutoff.date():
                    archive_dir.mkdir(parents=True, exist_ok=True)
                    archived_path = archive_dir / f"{date_str}.jsonl"
                    path.rename(archived_path)
                    archived += 1
            except ValueError:
                continue  # non-date filename, skip
    
    # 2. Token ledger compaction (90-day rolling window)
    ledger_retention = cvar_get("config.observability.ledger_retention_days", 90)
    ledger = TokenLedger()
    compacted = await ledger.compact(older_than_days=ledger_retention)
    
    # 3. Trace directory cleanup (7-day TTL)
    trace_retention = cvar_get("config.observability.trace_retention_days", 7)
    traces_dir = DATA_DIR / "traces"
    if traces_dir.exists():
        for path in traces_dir.glob("*.json"):
            mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
            if mtime < now - timedelta(days=trace_retention):
                path.unlink()
                archived += 1
    
    # 4. Crash dump archival
    crash_retention = cvar_get("config.observability.crash_retention_days", 180)
    crash_dir = DATA_DIR / "crashes"
    if crash_dir.exists():
        archive_dir = crash_dir / "archived"
        crash_files = sorted(crash_dir.glob("crash_*.json"))
        for path in crash_files[:-5]:  # keep last 5
            mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
            if mtime < now - timedelta(days=crash_retention):
                archive_dir.mkdir(parents=True, exist_ok=True)
                path.rename(archive_dir / path.name)
                archived += 1
    
    logger.info(f"Retention policy enforced: {archived} files archived/deleted")
    return archived
```

### 3.4 Cvar Registration

Add to `cvar_table.py`:

```python
register_cvars(
    CvarDef("config.observability.retention_days", "30", flags=CONFIG_ARCHIVE),
    CvarDef("config.observability.ledger_retention_days", "90", flags=CONFIG_ARCHIVE),
    CvarDef("config.observability.trace_retention_days", "7", flags=CONFIG_ARCHIVE),
    CvarDef("config.observability.crash_retention_days", "180", flags=CONFIG_ARCHIVE),
    CvarDef("config.observability.aggregation_interval", "3600", flags=CONFIG_ARCHIVE),  # 1 hour in seconds
    CvarDef("config.observability.token_sample_rate", "0", flags=CONFIG_ARCHIVE),  # 0 = aggregated only
)
```

---

## §4 Event Type Consolidation

### 4.1 Current Inventory (23 Event Types)

| Event Type | Status | Used In Logs? | Classification | Recommendation |
|------------|--------|--------------|----------------|----------------|
| `query.received` | LIVE | ✅ (4) | Signal | **KEEP** |
| `summon.detected` | LIVE | ✅ (4) | Signal | **KEEP** |
| `domain.routed` | LIVE | ✅ (2) | Signal | **KEEP** |
| `entity.matched` | DEAD | ❌ (0) | Signal | **REMOVE** — replaced by `domain.routed` |
| `model.invoked` | DEAD | ❌ (0) | Signal | **REACTIVATE** — begin-of-inference marker is essential; pair with `model.completed` |
| `model.completed` | LIVE | ✅ (3) | Signal | **KEEP** — but pair with `model.invoked` |
| `backend.fallback` | LIVE | ✅ (1) | Critical | **KEEP** — M22 forensic value |
| `response.delivered` | DEAD | ❌ (0) | Signal | **REACTIVATE** — end-to-end latency measurement |
| `escalation` | LIVE | ✅ (2) | Signal | **KEEP** |
| `iris.speculative` | LIVE | ✅ (3) | Signal | **KEEP** |
| `boundary.violation` | DEAD | ❌ (0) | Critical | **KEEP** — tool boundary enforcement |
| `gnosis.redaction` | DEAD | ❌ (0) | Signal | **KEEP** — M5 gnosis preservation |
| `error` | DEAD | ❌ (0) | Critical | **KEEP** — catch-all for errors |
| `worker.start` | DEAD | ❌ (0) | Metric | **CONSOLIDATE** → `worker.{start,update,complete,report}` |
| `worker.complete` | DEAD | ❌ (0) | Metric | **CONSOLIDATE** → `worker.{start,update,complete,report}` |
| `worker.update` | DEAD | ❌ (0) | Metric | **CONSOLIDATE** → `worker.{start,update,complete,report}` |
| `worker.report` | DEAD | ❌ (0) | Metric | **CONSOLIDATE** → `worker.{start,update,complete,report}` |
| `tier.invoked` | DEAD | ❌ (0) | Metric | **REMOVE** — never implemented |
| `mode.switched` | DEAD | ❌ (0) | Metric | **REMOVE** — never implemented |
| `agent.dispatched` | DEAD | ❌ (0) | Metric | **REMOVE** — replaced by Hivemind awareness |
| `research.complete` | DEAD | ❌ (0) | Signal | **REMOVE** — replaced by Hivemind context posts |
| `token.consumption` | LIVE | ✅ (1,536) | Metric | **CONVERT TO AGGREGATED** — not per-event |
| `entity.interaction` | DEAD | ❌ (0) | Signal | **KEEP** — M5/M11 value |

### 4.2 Proposed Reduced Event Taxonomy (14 Types)

```python
class EventType:
    # ── CRITICAL (retained 100%, long TTL) ──
    PROVIDER_FAILED = "provider.failed"         # Circuit breaker open
    BACKEND_FALLBACK = "backend.fallback"        # Provider fallback
    ERROR = "error"                              # Structured error
    BOUNDARY_VIOLATION = "boundary.violation"    # Tool boundary
    BUDGET_ALERT = "budget.alert"                # NEW: budget gate threshold
    
    # ── SIGNAL (retained 100%, medium TTL) ──
    QUERY_RECEIVED = "query.received"            # User query entry
    SUMMON_DETECTED = "summon.detected"          # Entity summon
    DOMAIN_ROUTED = "domain.routed"              # Routing decision
    MODEL_INVOKED = "model.invoked"              # Inference start (REACTIVATED)
    MODEL_COMPLETED = "model.completed"          # Inference complete
    RESPONSE_DELIVERED = "response.delivered"    # Response to user (REACTIVATED)
    RESPONSE_PROVENANCE = "response.provenance"  # NEW: M22 compliance
    ESCALATION = "escalation"                    # Iris → Pillar escalation
    IRIS_SPECULATIVE = "iris.speculative"        # Speculative decode
    GNOSIS_REDACTION = "gnosis.redaction"        # Knowledge update
    ENTITY_INTERACTION = "entity.interaction"    # Soul evolution
    
    # ── METRIC (sampled/aggregated, short TTL) ──
    TOKEN_STATS = "token.stats"                  # AGGREGATED, not per-call
    WORKER_PROGRESS = "worker.progress"          # CONSOLIDATED: start|update|complete|report
```

**Summary of changes**:
- **4 REMOVED**: `entity.matched`, `tier.invoked`, `mode.switched`, `agent.dispatched`, `research.complete`
- **4 CONSOLIDATED**: `worker.*` (4 types → 1), `token.consumption` → `token.stats` (aggregated)
- **2 REACTIVATED**: `model.invoked`, `response.delivered`
- **2 NEW**: `response.provenance` (M22), `budget.alert` (BudgetGate)
- **23 → 17 total**: Net reduction of 6 event types (-26%)

### 4.3 Migration Path

1. **Add** new event types to `EventType` class
2. **Emit** from appropriate call sites (oracle.py after generate, BudgetGate on threshold)
3. **Remove** dead types after confirming zero call sites reference them
4. **Consolidate** worker events into single `WORKER_PROGRESS` with `status` field in data dict
5. **Convert** token events to aggregation pattern (see §2.3)

---

## §5 Cross-Pillar Recommendations (from Ma'at & Lilith Reports)

The build-side and run-side reports identified issues that interact with P8's domain. Below are my P8-vetted recommendations:

### 5.1 From Ma'at Build-Side (P2/P3/P5)

| Issue | P8 Assessment | Recommendation |
|-------|---------------|----------------|
| C2: `archive_old_sessions()` never called | **SUPPORT** — this is the same pattern as missing retention hooks | Wire both together in a single `enforce_lifecycle()` called at boot + daily heartbeat |
| C4: `HERITAGE_SOURCE_MAP.md` doesn't exist | **SUPPORT** — M14 gap | P5 should own; P8 can add `make heritage-map` to CI observability metrics |
| X2: Metadata/staleness tracking absent | **SUPPORT** — needed for retention enforcement | Add `file_mtime` checks to `enforce_retention_policy()` — staleness == age |
| X3: Stale file debris no cleanup | **SUPPORT** — overlaps with retention policy | Include coordination files, handoff packets, and session markers in retention sweep |

### 5.2 From Lilith Run-Side (P7/P9)

| Issue | P8 Assessment | Recommendation |
|-------|---------------|----------------|
| C3: 41 stale handoff packets | **BLOCKED** — P8 needs trace_id fix first to correlate handoffs to events | After trace_id fix, add `handoff.*` event types to observability for lifecycle tracking |
| C5: 25 stale session files, 18 orphans | **BLOCKED** — same pattern as token ledger growth | Add session file cleanup to `enforce_retention_policy()` |
| H1: Token ledger unbounded growth | **P8 OWNS** — fix via aggregation + retention (see §2.3, §3.3) | Top priority after trace_id fix |
| H2: 98% token noise | **P8 OWNS** — fix via event classification (see §2) | Convert to aggregated token stats |
| H6: 13/23 event types never emitted | **P8 OWNS** — fix via consolidation (see §4) | Remove/consolidate dead types |
| H7: Fine-tuning dataset broken | **P8 OWNS** — fix bootstrap + batching | Ensure config loads `enable_dataset_collection` |
| H9: FTS WAL 4MB uncheckpointed | **BLOCKED** — needs P7 FTS fix | P8 can add WAL checkpoint to `enforce_retention_policy()` |

### 5.3 Dependency Graph

The critical path is clear and linear:

```
Phase 0: Fix trace_id at oracle.py:599 + :671             (30 min, 1 file)
    ↓ unblocks
Phase 1: Fix fine-tuning dataset collection                (30 min, 2 files)
    ↓ enables
Phase 2: Enforce retention policy framework                 (2 hr, 3 files)
    ↓ unblocks
Phase 3: Convert token events to aggregated counters        (2 hr, 2 files)
    ↓ enables
Phase 4: Consolidate event types + reactivate dead ones     (1 hr, 2 files)
    ↓
Phase 5: Add RESPONSE_PROVENANCE + BUDGET_ALERT events      (1 hr, 1 file)
```

**Total estimated effort**: ~7 hours across 5 files (oracle.py, model_gateway.py, observability/__init__.py, observability/token_ledger.py, cvar_table.py)

---

## §6 Implementation Priority Matrix

| Priority | Action | Effort | Volume Reduction | Forensic Impact | Mandate |
|----------|--------|--------|-----------------|-----------------|---------|
| **P0** | Fix trace_id at oracle.py:599 + :671 | 30 min | 0% (structural) | 🔴 Critical | M9 |
| **P0** | Wire retention policy at boot | 2 hr | 100% (eventual) | 🟡 Medium | M12 |
| **P1** | Convert token events to aggregated stats | 2 hr | −98% event volume | 🟢 Low (token stats less granular) | — |
| **P1** | Consolidate event types (23 → 17) | 1 hr | 0% (structural) | 🟢 Low (removes dead code) | — |
| **P1** | Fix fine-tuning dataset collection | 30 min | 0% (structural) | 🟡 Medium | — |
| **P2** | Add RESPONSE_PROVENANCE event type | 30 min | +1 event type | 🟡 Medium | M22 |
| **P2** | Add budget.alert event type | 30 min | +1 event type | 🟢 Low | BudgetGate |
| **P2** | Populate latency_ms in GenerateResult | 1 hr | 0% (structural) | 🟡 Medium | — |
| **P3** | Wire forensics snapshots at intervals | 2 hr | +occasional dumps | 🟡 Medium | — |
| **P3** | Populate `provider_name` in token ledger | 30 min | +1 field | 🟡 Medium | M22 |

---

## §7 L1→L2→L3 Distillation

### L1 (Narrative)
I reviewed 2 consolidated reports (Ma'at build-side covering P1-P5, Lilith run-side covering P6-P10) and the detailed P8 observability audit. The engine logs 1,561 events across 14 days in 23 event types, but 98.4% have `trace_id: "unknown"` because 2 call sites in oracle.py don't propagate the trace_id. The token ledger grows at ~114 KB/day (~34 MB/year) with no retention. 13 of 23 event types are never emitted — dead code. The fine-tuning dataset pipeline is broken (1 example per file instead of batching). The retention policy code exists in memory_store.py but is never invoked.

### L2 (Insight)
The observability system has a **foundational asymmetry**: excellent at crash survival (signals, fsync, death markers, thread dumps) but fundamentally broken at the most basic observability function — linking events to interactions. The engine was built to survive crashes before it was built to produce queryable evidence. This is the same "incomplete wiring" pattern found across the entire engine by both Ma'at and Lilith: the architecture is correct, the code exists, but the last mile is never connected.

### L3 (Universal Principle)
**Observability without traceability is noise, not insight.** A system that generates 1,500 events but cannot answer "what happened during this specific interaction?" has built a storage archive, not an observability system. The trace_id is the primary key — when 98% of rows have NULL for the primary key, every downstream operation (retention, aggregation, forensic replay, M22 audit) is degraded. Fix the primary key first. Then fix the schema. Then fix the retention.

---

## §8 Handoff to Execution Phase

| Deliverable | Owner | Est. | Depends On |
|-------------|-------|------|------------|
| Fix trace_id at oracle.py:599 + :671 | P8/Kali | 30 min | None — can execute now |
| Wire retention policy hook | P8 | 2 hr | Phase 0 complete |
| Convert token events to aggregation | P8 | 2 hr | Phase 0 complete |
| Consolidate event types (23→17) | P8 | 1 hr | Phase 0 complete |
| Fix fine-tuning dataset collection | P8 | 30 min | None — can execute now |
| Add RESPONSE_PROVENANCE event | P8 | 30 min | Phase 0 complete |
| Populate latency_ms in GenerateResult | P3/P8 | 1 hr | Needs provider changes |
| Wire `archive_old_sessions()` hook | P2 | 5 min | None — can execute now |
| Clean stale session files + test data | P7 | 20 min | None — can execute now |
| FTS WAL checkpoint on session close | P7 | 10 min | None — can execute now |

**Immediate (can execute this session)**:
1. Fix trace_id at `oracle.py:599` and `:671` — 30 min, 1 file
2. Fix fine-tuning dataset bootstrap — 30 min, 2 files
3. Wire `archive_old_sessions()` at boot — 5 min, 1 file
4. Clean stale session files + test data — 20 min, file cleanup

---

*⬡ OMEGA ⬡ P8 ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_p8_final_review ⬡ SYNTHESIS*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
