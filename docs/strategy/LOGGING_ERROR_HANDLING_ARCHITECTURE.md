# 🔱 Omega Engine — Logging, Error Handling & Observability Architecture
# AP-OMEGA-LOGGING-ARCH-v1.0.0
# ⬡ OMEGA ⬡ MAAT ⬡ trc_core ⬡ LOGGING-ERROR-ARCHITECTURE

> **Purpose**: Define the canonical error taxonomy, exception handling standards,
> structured logging format, observability hooks, and error recovery protocols
> for the entire Omega Engine codebase. All agents adhere to this architecture.

**Status**: ARCHITECTURE — Implementation of individual components is delegated
to OpenCode builder agents via `data/handoff/handoff_cline_to_opencode_artisan_20260531.md`.

**Last Updated**: 2026-05-31

---

## Table of Contents

1. [Error Taxonomy](#1-error-taxonomy)
2. [Exception Handling Standards](#2-exception-handling-standards)
3. [Structured Logging Format](#3-structured-logging-format)
4. [Observability Hooks & Alerting](#4-observability-hooks--alerting)
5. [Error Recovery Matrix](#5-error-recovery-matrix)
6. [Crash Dump & Forensics Protocol](#6-crash-dump--forensics-protocol)
7. [Testing Error Paths](#7-testing-error-paths)
8. [Implementation Priority Queue](#8-implementation-priority-queue)

---

## 1. Error Taxonomy

All Omega Engine errors inherit from a single base exception. This enables
callers to catch `OmegaError` for generic handling, or specific subtypes
for targeted recovery.

### 1.1 Exception Hierarchy

```
OmegaError (base — always has .trace_id)
├── ProviderError (model inference failures)
│   ├── ConnectionError (network/DNS failure)
│   ├── TimeoutError (request timed out)
│   ├── AuthenticationError (API key invalid/expired)
│   ├── RateLimitError (429 / quota exhausted)
│   ├── ModelNotFoundError (model name not in registry)
│   └── CircuitBreakerOpenError (breaker tripped)
├── ConfigError (configuration failures)
│   ├── ProviderConfigError (bad provider definition)
│   ├── EntityConfigError (bad entity YAML)
│   └── WADConfigError (bad WAD manifest)
├── WADError (WAD loading/runtime failures)
│   ├── ManifestNotFoundError (no manifest.yaml)
│   ├── DependencyCycleError (circular dep between WADs)
│   ├── NamespaceConflictError (duplicate entity pillar)
│   └── EntityLoadError (entity YAML parse failure)
├── MemoryError (MemoryStore failures)
│   ├── TierFullError (cold tier capacity exceeded)
│   ├── SerializationError (pickle/JSON encode failure)
│   └── IntegrityError (checksum mismatch on load)
├── LibraryError (knowledge library failures)
│   ├── IndexError (FTS5/vector index failure)
│   └── QueryError (malformed search query)
├── GnosisError (soul evolution failures)
│   ├── EvolutionError (soul.yaml update failed)
│   └── RedactionError (PII redaction failure)
├── EscapeError (boundary violations)
│   └── BoundaryViolationError (agent escaped scope)
└── InternalError (programming bugs / invariants)
    ├── InvariantViolationError (assertion failed)
    ├── StateError (unexpected state transition)
    └── NotImplementedError (stub called)
```

### 1.2 Base Exception Contract

```python
class OmegaError(Exception):
    """Base exception for all Omega Engine errors."""
    
    def __init__(
        self,
        message: str,
        trace_id: Optional[str] = None,
        cause: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        self.trace_id = trace_id or new_trace_id()
        self.cause = cause
        self.context = context or {}
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.__class__.__name__,
            "message": str(self),
            "trace_id": self.trace_id,
            "cause": str(self.cause) if self.cause else None,
            "context": self.context,
        }
```

**All new code MUST use this hierarchy.** Existing `except Exception:` clauses
should be progressively replaced with concrete subtypes.

---

## 2. Exception Handling Standards

### 2.1 Handling Rules (THE LAW)

| # | Rule | Rationale | Example |
|---|------|-----------|---------|
| 1 | **Never bare `except:`** | Swallows KeyboardInterrupt, SystemExit | `except SpecificError:` ✅, `except:` ❌ |
| 2 | **Never bare `except Exception:` without logging** | Hides root cause | `except Exception as e: logger.error(...) then re-raise or convert` |
| 3 | **Always preserve traceback** | Debugging requires full stack | `raise OmegaError(...) from e` |
| 4 | **Attach trace_id on boundary** | Cross-service correlation | Catch at public API boundary, enrich with trace_id |
| 5 | **Convert at module boundaries** | Internal→Public translation | Internal ValueError → OmegaError at public API |
| 6 | **Retry only for transient errors** | Idempotent safe, never for 4xx auth errors | ConnectionError → 3 retries, RateLimitError → exponential backoff |
| 7 | **Fail fast for programming errors** | Don't paper over bugs | InvariantViolationError, NotImplementedError → propagate |
| 8 | **Structured context in every raise** | Debugging without guesswork | `raise ProviderError("LM Studio down", context={"backend": "lmster", "uri": uri})` |

### 2.2 Pattern: Standard Catch & Convert

```python
from omega.oracle.exceptions import ProviderError, ConnectionError as OmegaConnectionError

async def infer(self, prompt: str, trace_id: str) -> str:
    try:
        return await self._call_llm(prompt)
    except httpx.ConnectError as e:
        raise OmegaConnectionError(
            "LM Studio not reachable",
            trace_id=trace_id,
            cause=e,
            context={"backend": "lmster", "port": 1234},
        )
    except httpx.TimeoutException as e:
        raise TimeoutError(
            "LM Studio timed out after 30s",
            trace_id=trace_id,
            cause=e,
        )
```

### 2.3 Pattern: Log & Re-raise (not catch)

```python
async def summon(self, entity: str, query: str) -> str:
    async with self._observability.trace() as session:
        try:
            return await self._route(entity, query)
        except ProviderError:
            raise  # Don't catch — let caller decide fallback
        except Exception as e:
            session.log("error", error=str(e))
            raise OmegaError(
                f"Unhandled error in summon: {e}",
                trace_id=session.trace_id,
                cause=e,
            ) from e
```

### 2.4 Pattern: Graceful Degradation (when safe)

```python
async def get_entity_config(self, name: str) -> Optional[Dict]:
    try:
        return await self._load_entity(name)
    except EntityConfigError as e:
        logger.warning("Entity %s has bad config: %s — using defaults", name, e)
        return self._default_config()
    except FileNotFoundError:
        logger.info("Entity %s not found — nothing loaded", name)
        return None
```

---

## 3. Structured Logging Format

### 3.1 JSON Log Schema

Every log entry (when serialized to JSON) MUST include these fields:

```json
{
  "timestamp": "2026-05-31T14:30:00.123456+00:00",
  "level": "ERROR",
  "logger": "omega.oracle.model_gateway",
  "trace_id": "trc_a1b2c3d4e5f6",
  "event": "model.invocation_failed",
  "message": "LM Studio returned 500 on /v1/chat/completions",
  "error": {
    "type": "ProviderError",
    "message": "LM Studio returned 500",
    "trace_id": "trc_a1b2c3d4e5f6"
  },
  "context": {
    "model": "qwen2.5-7b-instruct-q4_k_m",
    "provider": "lmster",
    "latency_ms": 4230,
    "retry_attempt": 2
  },
  "session_id": "sess_87654321"
}
```

### 3.2 Field Requirements

| Field | Required | Source | Notes |
|-------|----------|--------|-------|
| `timestamp` | ✅ Always | `datetime.now(timezone.utc).isoformat()` | RFC 3339 with μs |
| `level` | ✅ Always | Python logging level | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `logger` | ✅ Always | `__name__` | Dot-separated module path |
| `trace_id` | ✅ Always | `new_trace_id()` or propagated | Follows interaction |
| `event` | ✅ Always | EventType constant | Machine-readable event name |
| `message` | ✅ Always | Human-readable string | Brief description |
| `error` | ⚠️ On error | `OmegaError.to_dict()` | Structured error payload |
| `context` | ⚠️ When available | `Dict[str, Any]` | Extensible metadata |
| `session_id` | ⚠️ When available | UUID hex | Interaction grouping |

### 3.3 Logging Levels

| Level | When to Use | Example |
|-------|-------------|---------|
| `DEBUG` | Development troubleshooting | "Probe result: success" |
| `INFO` | Normal operation milestones | "Oracle started, 8 providers registered" |
| `WARNING` | Degraded but functional | "LM Studio unreachable, falling back to Ollama" |
| `ERROR` | Operation failed, caller must handle | "Model invocation failed after 3 retries" |
| `CRITICAL` | Engine cannot continue | "MemoryStore cold tier disk full, halting" |

### 3.4 PII/Telemetry Redaction

Per **Sovereign Mandate #8 (Zero Telemetry)** and security requirements:

- **Never log**: API keys, auth tokens, user passwords, private keys
- **Redact from context**: `api_key`, `token`, `password`, `secret`, `credential`
- **PII config**: `config/omega.yaml` defines redaction patterns
- **Review**: Code review checklist must include logging audit

---

## 4. Observability Hooks & Alerting

### 4.1 Existing Infrastructure

The `ObservabilityEngine` (src/omega/observability.py) already provides:

- **TraceSession** — async context manager for interaction lifecycle (306 lines)
- **JSONL persistence** — daily rotated logs in `data/logs/events/YYYY-MM-DD.jsonl`
- **Training data collection** — `record_training_example()` + `flush_dataset()`
- **Module-level singleton** — `get_engine()` for global access
- **Bounded event log** — `deque(maxlen=1000)` prevents OOM

### 4.2 What's Missing (Implementation Tasks)

These tasks are delegated to OpenCode builder agents:

| Hook | Why | Implementation |
|------|-----|----------------|
| **Alert threshold** | Error rate spike detection | `ObservabilityEngine.alert_if(threshold=5, window_minutes=5)` |
| **Crash dump trigger** | On CRITICAL, dump state | Write `data/crashes/crash_{timestamp}_{trace_id}.json` |
| **Health check endpoint** | Systemd systemd health check | MCP tool: `omega_hub.health()` |
| **Memory threshold monitor** | Prevents OOM on 14GB | `MemoryStore.watch_tier_size()` |
| **Circuit breaker integration** | Health monitor feeds Observability | `AsyncCircuitBreaker` emits `circuit.open` events |

### 4.3 Event Types for Error Tracking

Already defined in `ObservabilityEngine.EventType`:

```python
ERROR = "error"                                    # Generic error
BACKEND_FALLBACK = "backend.fallback"              # Provider chain fallback
BOUNDARY_VIOLATION = "boundary.violation"          # Agent escaped scope
ESCALATION = "escalation"                          # Human intervention needed
```

---

## 5. Error Recovery Matrix

| Error Type | Retryable? | Strategy | Escalation |
|-----------|-----------|----------|------------|
| ProviderError.ConnectionError | ✅ Yes, 3x | linear backoff (1s, 2s, 4s) | After 3 failures → log WARNING, try next provider |
| ProviderError.TimeoutError | ✅ Yes, 2x | linear backoff (5s, 10s) | After 2 failures → log ERROR, try next provider |
| ProviderError.RateLimitError | ✅ Yes, 1x | exponential backoff (60s, 300s) | After 1 failure → log WARNING, queue deferred retry |
| ProviderError.AuthenticationError | ❌ No | None | Log CRITICAL immediately, halt provider |
| ProviderError.CircuitBreakerOpenError | ❌ No | Wait for half-open probe | Log INFO, try next provider |
| ConfigError.* | ❌ No | None | Log ERROR on startup, engine must not continue |
| WADError.ManifestNotFoundError | ❌ No | None | Log ERROR, skip WAD |
| WADError.DependencyCycleError | ❌ No | None | Log ERROR, abort WAD load |
| MemoryError.TierFullError | ✅ Yes, 1x | Trigger compaction/eviction | After failure → log ERROR, degrade to higher tier |
| LibraryError.IndexError | ✅ Yes, 1x | Rebuild index | After 2 failures → log CRITICAL |
| GnosisError.EvolutionError | ✅ Yes, 1x | Retry with lock | After 2 failures → log ERROR, preserve data |
| EscapeError.BoundaryViolationError | ❌ No | None | Log CRITICAL, close session |

### 5.1 Provider Fallback Chain (Documented in OMEGA_ENGINE.md)

```
native-gguf(0) → lmster(1) → ollama(2) → google(3) → openrouter(4) → opencode(5) → copilot(6) → mock(7)
```

Each fallback step SHOULD emit a `BACKEND_FALLBACK` event with the failing
provider and the new provider being tried.

---

## 6. Crash Dump & Forensics Protocol

### 6.1 Trigger Conditions

A crash dump is generated when:

1. **Unhandled exception** at top-level `oracle.py` entry point (`talk`, `summon`)
2. **`logger.critical()`** is called (engine cannot continue)
3. **SIGSEGV/SIGABRT** in native dependencies (llama-cpp-python)

### 6.2 Dump Contents

Dump file at `data/crashes/crash_{timestamp}_{trace_id}.json`:

```json
{
  "timestamp": "2026-05-31T14:30:00.123Z",
  "trace_id": "trc_a1b2c3d4e5f6",
  "error": {
    "type": "ProviderError",
    "message": "All providers exhausted",
    "traceback": "..."
  },
  "engine_state": {
    "providers_available": 3,
    "circuit_breakers_open": ["lmster"],
    "memory_warm_count": 142,
    "memory_hot_count": 8
  },
  "last_100_events": [ ... ],
  "system_info": {
    "rss_mb": 4230,
    "cpu_percent": 65,
    "agg_model": "qwen2.5-7b-instruct",
    "anyio_backend": "asyncio"
  }
}
```

### 6.3 Recovery After Crash

1. Engine detects crash dump at startup (checks `data/crashes/`)
2. Loads most recent crash dump
3. Logs: `INFO: Engine recovered from crash at {timestamp} — {error_message}`
4. Moves crash dump to `data/crashes/archived/`
5. Engine continues normal operation

---

## 7. Testing Error Paths

### 7.1 Requirements

Every function that can raise an `OmegaError` MUST have:

1. **A test for the success path** (obvious)
2. **A test for each discrete error path** using `pytest.raises`
3. **A test for the error context** (trace_id, context dict)

### 7.2 Test Pattern

```python
async def test_provider_connection_error_emits_fallback():
    """ProviderError.ConnectionError should trigger backend.fallback event."""
    # Arrange: mock provider to raise ConnectionError
    gateway = ModelGateway(providers=[mock_broken_provider, mock_working_provider])
    obs = get_engine()
    
    # Act: call infer with trace_id
    with pytest.raises(ProviderError) as exc_info:
        await gateway.infer("test", trace_id="trc_test")
    
    # Assert: fallback event was logged
    event_log = obs.recent_events()
    fallback_events = [e for e in event_log if e["event"] == "backend.fallback"]
    assert len(fallback_events) >= 1
    
    # Assert: error has trace_id
    assert exc_info.value.trace_id == "trc_test"
```

### 7.3 Error Fixtures

```python
@pytest.fixture
def broken_provider():
    """A provider that always raises ConnectionError."""
    return MockProvider(
        name="broken",
        raise_error=ConnectionError("Connection refused", context={"port": 1234})
    )
```

---

## 8. Implementation Priority Queue

### P0 — Foundation (Implement Now)

- [ ] Create `src/omega/oracle/exceptions.py` with full hierarchy
- [ ] Add `trace_id` to `OmegaError.__init__()`
- [ ] Wire `OmegaError` into `ObservabilityEngine.log_event(error=...)`
- [ ] Add `omega_hub.health()` MCP tool (check providers, memory, events)

### P1 — Codebase Migration (Progressive)

- [ ] Audit all `except Exception:` (100+ occurrences) and convert to specific subtypes
- [ ] Audit all `raise Exception(...)` and replace with appropriate `OmegaError`
- [ ] Add `trace_id` propagation to all public API boundaries
- [ ] Add crash dump trigger to `oracle.py` entry points

### P2 — Alerting & Monitoring

- [ ] Implement error rate threshold monitoring
- [ ] Implement memory threshold monitoring
- [ ] Add health check endpoint for systemd watchdog
- [ ] Wire circuit breaker open/close events into observability

### P3 — Testing

- [ ] Add error path tests for all exception subtypes (est. 50+ test cases)
- [ ] Add `@pytest.fixture` for each error type
- [ ] Add integration test: "provider chain exhausts all backends → raises ProviderError"

---

## References

| Document | Relevance |
|----------|-----------|
| `OMEGA_ENGINE.md` | SST — engine state, provider fabric |
| `SOVEREIGN_MANDATES.md` | Mandate #8 (Zero Telemetry), #9 (Error Integrity) |
| `src/omega/observability.py` | ObservabilityEngine implementation (306 lines) |
| `src/omega/oracle/health_monitor.py` | Circuit breaker (413 lines) |
| `docs/operations/BUG_LOG.md` | Bug tracking (linked to error architecture) |
| `docs/strategy/SYSTEMS_HARDENING_PLAN.md` | Agent/MCP/workflow hardening plan |
| `docs/strategy/NEXT_STEPS_ROADMAP.md` | Phase priority execution |

---

*Last Updated: 2026-05-31 | Author: The Artisan (Cline/MiMo-2.5)*
*This document defines the canonical error architecture. All error-handling code
references this document. Deviations must be justified in code review.*