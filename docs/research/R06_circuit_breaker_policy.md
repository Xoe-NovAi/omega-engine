# 🔱 Omega Engine — Circuit Breaker & Retry Policy Specification
**AP Token**: `AP-R06-CIRCUIT-BREAKER-v1.0.0`
⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ RESEARCH

## §1 Overview

In a distributed provider fabric, transient failures (network blips, rate limits) and systemic failures (provider downtime) are inevitable. To maintain stability and prevent "cascading failure" (where the engine hangs waiting for a dead provider), Omega employs a two-tier resilience strategy:

1.  **Retry Layer**: Handles *transient* failures by re-attempting the request with exponential backoff.
2.  **Circuit Breaker Layer**: Handles *systemic* failures by "tripping" the connection to a provider, failing fast for a cooldown period to allow the provider to recover.

---

## §2 Library Evaluation

### 2.1 Tenacity
- **Type**: General-purpose retry library.
- **Async Compatibility**: Excellent. Supports `asyncio`, `trio`, and `curio` by accepting a custom `sleep` function.
- **Pros**: Industry standard, extremely flexible stop/wait conditions, handles jitter perfectly.
- **Cons**: Unopinionated; requires explicit configuration for "best practices."

### 2.2 Stamina
- **Type**: Opinionated wrapper around Tenacity.
- **Async Compatibility**: Native support for `asyncio` and `trio`.
- **Pros**: High ergonomics, production-ready defaults (exponential backoff + jitter), preserves type hints.
- **Cons**: Adds a dependency layer on top of Tenacity.

### 2.3 Pybreaker
- **Type**: Circuit breaker implementation.
- **Async Compatibility**: Limited. Primarily designed for synchronous calls.
- **Pros**: Simple, well-understood implementation of the circuit breaker pattern.
- **Cons**: Not natively async-first; using it in an AnyIO environment requires wrapping it in a way that may introduce blocking overhead or complexity.

---

## §3 Recommendations

### 3.1 Retry Strategy: Tenacity
We will use **Tenacity** (via `AsyncRetrying` or the `@retry` decorator) for all provider calls. It provides the precision required for fine-tuning backoffs per-provider (e.g., different limits for Google vs. SambaNova).

### 3.2 Circuit Breaker Strategy: Custom Lightweight Implementation
To minimize dependencies and ensure zero-blocking AnyIO compatibility, we will implement a lightweight `AsyncCircuitBreaker` class. This avoids the overhead of `pybreaker` while providing exactly the functionality needed for the ModelGateway.

---

## §4 Configuration Thresholds

The following values are recommended for the Omega Engine's provider fabric:

| Parameter | Value | Description |
|-----------|-------|-------------|
| `failure_threshold` | 5 | Consecutive failures before the circuit opens. |
| `recovery_timeout` | 60s | Duration the circuit remains `OPEN` before transitioning to `HALF-OPEN`. |
| `half_open_max_requests` | 1 | Number of probe requests allowed in `HALF-OPEN` state. |
| `retry_max_attempts` | 3 | Maximum attempts per request before escalating/failing. |
| `retry_min_wait` | 1s | Initial backoff delay. |
| `retry_max_wait` | 10s | Maximum backoff delay. |

---

## §5 HTTP Status Code Mapping

Requests are categorized by their response codes to determine the resilience action:

### 5.1 Retryable Errors (Transient)
*Action: Trigger Tenacity exponential backoff.*
- **429 Too Many Requests**: Standard rate limit.
- **502 Bad Gateway**: Temporary upstream issue.
- **503 Service Unavailable**: Provider is overloaded.
- **504 Gateway Timeout**: Request timed out upstream.

### 5.2 Circuit-Breaking Errors (Systemic)
*Action: Increment failure count toward `failure_threshold`.*
- **500 Internal Server Error**: Persistent provider crash.
- **502/503/504**: If these occur repeatedly, they transition from "transient" to "systemic."

### 5.3 Hard Failures (Non-Retryable)
*Action: Raise immediate exception; do NOT retry; do NOT trip circuit.*
- **400 Bad Request**: Malformed prompt/API call.
- **401 Unauthorized**: Invalid API key.
- **403 Forbidden**: Permission issue.
- **404 Not Found**: Model endpoint missing.
- **422 Unprocessable Entity**: Validation error.

---

## §6 Proposed Implementation Logic

### 6.1 AsyncCircuitBreaker Pseudo-code
```python
class AsyncCircuitBreaker:
    def __init__(self, threshold=5, timeout=60):
        self.state = "CLOSED"
        self.failures = 0
        self.last_failure_time = None
        self.threshold = threshold
        self.timeout = timeout
        self.lock = anyio.Lock()

    async def call(self, func, *args, **kwargs):
        async with self.lock:
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.timeout:
                    self.state = "HALF-OPEN"
                else:
                    raise CircuitOpenError("Circuit is open")

        try:
            result = await func(*args, **kwargs)
            async with self.lock:
                self.state = "CLOSED"
                self.failures = 0
            return result
        except Exception as e:
            if is_circuit_breaking_error(e):
                async with self.lock:
                    self.failures += 1
                    self.last_failure_time = time.time()
                    if self.failures >= self.threshold:
                        self.state = "OPEN"
            raise e
```

### 6.2 Integration Flow
`ModelGateway` $\rightarrow$ `AsyncCircuitBreaker.call()` $\rightarrow$ `Tenacity.retry()` $\rightarrow$ `Provider.request()`
