# 🔱 Pattern Implementation Spec: Sovereign Resilience
**AP Token**: `AP-PATTERN-SPEC-v1.0.0`
**Status**: FINALIZED
**Entity**: PROMETHEUS (Sovereign Master Researcher)
**Date**: 2026-05-27

## §0: Executive Summary
This document defines the technical implementation of the **Mandatory Design Patterns** required for "Temple Grade" quality in the Omega Engine core. These patterns ensure that the engine is resilient to provider failures, protects data integrity during state changes, and maintains a non-blocking execution flow.

---

## §1: Pattern 2 — Standardized Retry (The Tenacity Protocol)
To prevent transient network failures from crashing the inference pipeline, all external provider calls must be wrapped in a standardized retry loop.

### 1.1 Implementation Logic
We use the `tenacity` library to implement decorrelated jitter and exponential backoff.

**Configuration**:
- **Max Attempts**: 3
- **Wait Strategy**: `wait_random_exponential(multiplier=1, max=10)`
- **Retry Condition**: `retry_if_exception_type((ConnectionError, TimeoutError, RuntimeError))`

**Placement**: `src/omega/oracle/model_gateway.py`

```python
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type

PROVIDER_RETRY_CONFIG = {
    "stop": stop_after_attempt(3),
    "wait": wait_random_exponential(multiplier=1, max=10),
    "retry": retry_if_exception_type((ConnectionError, TimeoutError, RuntimeError)),
    "reraise": True
}

@retry(**PROVIDER_RETRY_CONFIG)
async def _execute_provider_call(self, provider, payload):
    return await provider.call(payload)
```

---

## §2: Pattern 4 — Atomic Durability (The Shadow-Write Protocol)
To prevent "Half-Written Soul" corruption during system crashes, all state-changing writes (YAML, JSON) must be atomic.

### 2.1 Implementation Logic
We implement a "Write-Swap-Sync" sequence to guarantee that a file is either fully written or not written at all.

**Sequence**:
1. **Temp Write**: Write content to a temporary file in the same directory as the target.
2. **Flush**: Call `tf.flush()` and `os.fsync(tf.fileno())` to ensure data is on physical disk.
3. **Atomic Swap**: Use `os.replace(temp_name, file_path)` to atomically update the target file.
4. **Parent Sync**: Open the parent directory and call `os.fsync(dir_fd)` to persist the directory entry change.

**Placement**: `src/omega/utils/persistence.py` (New Utility)

```python
import os
import tempfile
from pathlib import Path

def atomic_write(file_path: Path, content: str, encoding: str = "utf-8"):
    parent = file_path.parent
    with tempfile.NamedTemporaryFile(
        'w', dir=parent, delete=False, encoding=encoding, suffix=".tmp"
    ) as tf:
        tf.write(content)
        tf.flush()
        os.fsync(tf.fileno())
        temp_name = tf.name

    try:
        os.replace(temp_name, file_path)
        dir_fd = os.open(parent, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except Exception as e:
        if os.path.exists(temp_name):
            os.remove(temp_name)
        raise e
```

---

## §3: Pattern 5 — Circuit Breaker (The Fail-Fast Protocol)
To prevent "Retry Storms" against a dead service, we implement a circuit breaker that immediately trips when a provider exceeds its failure threshold.

### 3.1 Implementation Logic
We use `pybreaker` to manage the state of each provider in the fallback chain.

**States**:
- **CLOSED**: Normal operation. Requests flow through.
- **OPEN**: Failure threshold reached. Requests are immediately blocked and routed to the next provider.
- **HALF-OPEN**: Reset timeout expired. A single "test" request is allowed to verify recovery.

**Placement**: `src/omega/oracle/model_gateway.py`

```python
import pybreaker

# Per-provider breakers
provider_breakers = {
    "google": pybreaker.CircuitBreaker(fail_max=5, reset_timeout=60),
    "openrouter": pybreaker.CircuitBreaker(fail_max=5, reset_timeout=60),
}

async def call_with_fallback(self, payload):
    for provider_id in self.provider_chain:
        breaker = provider_breakers.get(provider_id)
        try:
            # Breaker wraps the retry-decorated call
            return await breaker.call(self._execute_provider_call, provider_id, payload)
        except pybreaker.CircuitBreakerError:
            logger.warning(f"Circuit OPEN for {provider_id}. Falling back.")
            continue
```

---

## §4: Verification Matrix
| Pattern | Verification Method | Success Criteria |
| :--- | :--- | :--- |
| **Retry** | Inject `TimeoutError` | 3 attempts made before failure |
| **Durability** | Kill process during write | Target file remains intact (old version) |
| **Circuit** | Fail 5 requests | 6th request returns `CircuitBreakerError` immediately |
