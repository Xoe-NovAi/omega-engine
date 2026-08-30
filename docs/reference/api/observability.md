# Observability Engine API Reference

**Module**: `src/omega/observability/__init__.py`
**Status**: Production (T3-2 wired)
**Tests**: `tests/test_observability.py` (15 existing) + `tests/test_metrics_db_integration.py` (12 integration)

## Overview

`ObservabilityEngine` provides trace-level event logging, performance metrics, and regression detection. It integrates with `MetricsDB` for persistent storage and `TokenLedger` for token accounting.

## Architecture

```
Oracle.talk() → ObservabilityEngine.record_*() → MetricsDB (SQLite WAL)
                                                → Event Log (JSON)
                                                → TokenLedger
```

## Classes

### ObservabilityEngine

```python
class ObservabilityEngine:
    def __init__(self, data_dir: str = "data", 
                 metrics_db: Optional[MetricsDB] = None)
    
    # Core recording
    async def log_event(self, event_type: str, entity: str, 
                        payload: Dict, trace_id: Optional[str] = None) -> str
    async def record_performance(self, entity: str, latency_ms: float,
                                  tokens: int, provider: str,
                                  trace_id: str) -> None
    async def record_metrics_error(self, entity: str, error: str,
                                    trace_id: str) -> None
    async def record_breaker_transition(self, provider: str,
                                         old_state: str, new_state: str) -> None
    
    # Queries
    async def get_events(self, entity: Optional[str] = None,
                         event_type: Optional[str] = None,
                         limit: int = 100) -> List[Dict]
    async def stats(self, entity: Optional[str] = None) -> Dict[str, Any]
    
    # Properties
    @property
    def metrics_db(self) -> MetricsDB:  # Lazy-loaded
        ...
```

## Key Methods

### log_event()

Records a structured event with trace ID propagation.

```python
trace_id = await engine.log_event(
    event_type="inference_complete",
    entity="kali",
    payload={"latency_ms": 150, "tokens": 500},
    trace_id="trc_abc123"
)
```

### record_performance()

Records inference performance to MetricsDB with regression detection.

```python
await engine.record_performance(
    entity="kali",
    latency_ms=150.5,
    tokens=500,
    provider="native-gguf",
    trace_id="trc_abc123"
)
```

### record_breaker_transition()

Records circuit breaker state changes.

```python
await engine.record_breaker_transition(
    provider="google",
    old_state="CLOSED",
    new_state="OPEN"
)
```

### stats()

Returns aggregated statistics.

```python
stats = await engine.stats("kali")
# Returns: {"total_events": 150, "avg_latency_ms": 120.5, "total_tokens": 75000, ...}
```

## Integration Points

- **Oracle**: Main consumer — records every inference
- **Health Monitor**: Records breaker transitions
- **MetricsDB**: Persistent storage backend (lazy-loaded)

## Performance

- **Write latency**: ~0.2ms per event (async, non-blocking)
- **Read latency**: ~5ms for aggregations
- **Storage**: WAL-mode SQLite, ~100KB per 10,000 events

## Heritage

`[id-soft: doom3-2004] Event System — structured event logging for observability`
