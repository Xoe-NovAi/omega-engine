# 🔱 Metrics Pipeline Architecture
**AP Token**: `AP-METRICS_PIPELINE-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_doc_deep ⬡ STANDARD

**Date**: 2026-07-06
**Purpose**: Metrics Pipeline Architecture.

---

# Metrics Pipeline Architecture

**Module**: `src/omega/observability/metrics_db.py`
**Status**: Production (T3-2)
**Tests**: 30 existing + 12 integration = 42 tests

## Overview

The Metrics Pipeline provides WAL-mode SQLite storage for high-speed, zero-wear performance logging. It records inference metrics, circuit breaker transitions, and regression detection data.

## Architecture

```
Oracle.talk()
    ↓
ObservabilityEngine.record_performance()
    ↓
MetricsDB (SQLite WAL)
    ├── performance table (latency, tokens, provider)
    ├── baselines table (EWMA regression detection)
    ├── regressions table (detected anomalies)
    ├── breaker_transitions table (state changes)
    └── events table (general observability)
```

## Design Decisions

### WAL-Mode

Write-Ahead Logging (WAL) ensures:
1. **Crash safety**: Writes are logged before being applied
2. **Concurrent reads**: Readers don't block writers
3. **Zero-wear logging**: Sequential writes minimize SSD wear

### Lazy Initialization

`MetricsDB` is created on first access, not at import time. This prevents filesystem side effects in tests and allows the engine to start even if the database directory doesn't exist yet.

```python
def _ensure_metrics_db(self) -> None:
    if self._metrics_db is not None:
        return
    if os.environ.get("OMEGA_ENV") == "test":
        return  # Skip in test mode
    self._metrics_db = MetricsDB()
```

### Test-Mode Override

When `OMEGA_ENV=test`, `_ensure_metrics_db()` is a no-op unless an instance is injected. This allows tests to inject a mock or in-memory database:

```python
metrics_db = MetricsDB(":memory:")
observability = ObservabilityEngine(metrics_db=metrics_db)
# Now observability.metrics_db returns the injected instance
```

### Non-Fatal Recording

MetricsDB recording failures are logged at DEBUG level, never raised. This ensures that observability failures never crash the inference pipeline:

```python
try:
    await self._metrics_db.record_performance(...)
except Exception as e:
    logger.debug("MetricsDB recording failed: %s", e)
```

## Regression Detection

The MetricsDB uses EWMA (Exponentially Weighted Moving Average) baselines to detect performance regressions:

1. **Baseline update**: On each recording, the EWMA baseline is updated
2. **Regression check**: If latency exceeds baseline by >2σ, a regression is flagged
3. **Alert**: Regressions are logged and can be queried via `detect_regressions()`

```python
regressions = await metrics_db.detect_regressions("kali")
# Returns: [{"metric": "latency_ms", "expected": 150.0, "actual": 350.0, ...}]
```

## Integration Points

- **ObservabilityEngine**: Main entry point for recording
- **HealthMonitor**: Records breaker transitions
- **Oracle**: Records inference performance after each call

## Performance

- **Write latency**: ~0.1ms per record (WAL-mode)
- **Read latency**: ~1ms for aggregations
- **Database size**: ~100KB per 10,000 records

## Heritage

`[id-soft: doom3-2004] Event System — structured event logging for observability`

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
