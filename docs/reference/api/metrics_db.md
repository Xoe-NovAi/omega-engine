# Metrics DB API Reference

**Module**: `src/omega/observability/metrics_db.py`
**Status**: Production (T3-2)
**Tests**: `tests/test_metrics_db.py` (30 existing) + `tests/test_metrics_db_integration.py` (12 integration)

## Overview

`MetricsDB` provides WAL-mode SQLite storage for high-speed, zero-wear performance logging. It's wired into `ObservabilityEngine` and records inference metrics, breaker transitions, and regression detection data.

## Architecture

```
Oracle.talk() → ObservabilityEngine.record_performance() → MetricsDB.record()
                                                           ↓
                                                    metrics SQLite DB
                                                    (WAL-mode, 5 tables)
```

## Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `performance` | Inference latency, tokens, provider | trace_id, entity, latency_ms, tokens, provider |
| `regressions` | Detected regressions | entity, metric, expected, actual, timestamp |
| `baselines` | EWMA baselines per entity | entity, metric, baseline, alpha |
| `breaker_transitions` | Circuit breaker state changes | provider, old_state, new_state, timestamp |
| `events` | General observability events | event_type, entity, payload, trace_id |

## Classes

### MetricsDB

```python
class MetricsDB:
    def __init__(self, db_path: str = "data/observability/metrics.db")
    async def initialize(self) -> None  # Creates tables if needed
    async def record_performance(self, entity: str, latency_ms: float, 
                                  tokens: int, provider: str, 
                                  trace_id: str) -> None
    async def record_metrics_error(self, entity: str, error: str,
                                    trace_id: str) -> None
    async def record_breaker_transition(self, provider: str, 
                                         old_state: str, new_state: str) -> None
    async def get_entity_stats(self, entity: str, 
                                hours: int = 24) -> Dict[str, Any]
    async def detect_regressions(self, entity: str) -> List[Dict]
```

## Integration Points

### ObservabilityEngine

```python
# src/omega/observability/__init__.py
class ObservabilityEngine:
    @property
    def metrics_db(self) -> MetricsDB:  # Lazy-loaded
        ...
    
    async def record_performance(self, entity, latency_ms, tokens, provider, trace_id):
        """Records to both event log and MetricsDB."""
        ...
```

### Oracle

```python
# src/omega/oracle/oracle.py
# After successful inference:
await self.observability.record_performance(
    entity=entity_name,
    latency_ms=latency_ms,
    tokens=result.usage.get("total_tokens", 0),
    provider=result.provider_name,
    trace_id=trace_id
)
```

### Health Monitor

```python
# src/omega/oracle/health_monitor.py
# On breaker state change:
await engine.record_breaker_transition(provider, old_state, new_state)
```

## Key Features

### WAL-Mode

Write-Ahead Logging ensures crash safety and concurrent reads during writes.

### Lazy Initialization

`MetricsDB` is created on first access, not at import time. This prevents filesystem side effects in tests.

### Test-Mode Override

When `OMEGA_ENV=test`, `_ensure_metrics_db()` is a no-op unless an instance is injected:

```python
# Test code:
metrics_db = MetricsDB(":memory:")
observability = ObservabilityEngine(metrics_db=metrics_db)
# Now observability.metrics_db returns the injected instance
```

### Regression Detection

EWMA baselines are updated on each recording. Regressions are detected when latency exceeds baseline by >2σ:

```python
regressions = await metrics_db.detect_regressions("kali")
# Returns: [{"metric": "latency_ms", "expected": 150.0, "actual": 350.0, ...}]
```

## Performance

- **Write latency**: ~0.1ms per record (WAL-mode)
- **Read latency**: ~1ms for aggregations
- **Database size**: ~100KB per 10,000 records

## Heritage

`[id-soft: doom3-2004] Event System — structured event logging for observability`
