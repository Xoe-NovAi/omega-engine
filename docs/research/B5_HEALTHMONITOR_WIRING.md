# 🔱 B5: HealthMonitor Wiring into ModelGateway.generate()

**AP Token**: `AP-B5-HEALTHMONITOR-WIRING-v1.0.0`
**Status**: ✅ Complete — Implementation Spec
**Entity**: SOPHIA
**Model**: deepseek-v4-flash
**Channel**: opencode
**Created**: 2026-05-18

---

## §1 Executive Summary

This document specifies how to wire `HealthMonitor` into `ModelGateway.generate()` to enable B5 (Soul Update after Inference). The wiring requires:

1. **Pass HealthMonitor to ModelGateway** — via constructor
2. **Record latency** — around provider.generate() calls (lines 316, 383-385)
3. **Record success/failure** — after response or exception (lines 326-327, 328-343)
4. **Error handling** — graceful degradation if HealthMonitor fails

---

## §2 Architecture Overview

### Current State
```
Oracle
  └── health_monitor: HealthMonitor (line 123)
  └── triage_router: TriageRouter (line 124)
  └── model_gateway: ModelGateway (line 94) ← NO health_monitor
```

### Target State
```
Oracle
  └── health_monitor: HealthMonitor
  └── model_gateway: ModelGateway(health_monitor=health_monitor)
        └── generate() → _execute_with_retry() → record_latency/success/failure
```

---

## §3 Implementation Spec

### Step 1: Add `health_monitor` Parameter to ModelGateway.__init__

**File**: `src/omega/oracle/model_gateway.py`
**Line**: 80-96

```python
def __init__(self, config_path: Optional[str] = None, health_monitor: Optional[Any] = None):
    # ... existing code ...
    self._health_monitor = health_monitor  # NEW LINE
```

### Step 2: Pass HealthMonitor from Oracle to ModelGateway

**File**: `src/omega/oracle/oracle.py`
**Line**: 94

```python
self.model_gateway = model_gateway or ModelGateway(health_monitor=self.health_monitor)
```

### Step 3: Record Latency in _execute_with_retry()

**File**: `src/omega/oracle/model_gateway.py`
**Line**: 311-348

Wrap the provider.generate() call with timing:

```python
async def _execute_with_retry(self, provider: Any, model_name: str, system_prompt: str, user_query: str, temperature: float, max_tokens: int) -> Optional[str]:
    """Execute request with retry logic and background metrics tracking."""
    max_retries = 3
    for attempt in range(max_retries):
        start_time = time.monotonic()  # NEW: start timing
        try:
            response = await provider.generate(model_name, system_prompt, user_query, temperature, max_tokens)
            
            # NEW: Record latency + success
            if self._health_monitor:
                latency_ms = (time.monotonic() - start_time) * 1000
                try:
                    self._health_monitor.record_latency(model_name, latency_ms)
                    self._health_monitor.record_success(model_name)
                except Exception as e:
                    logger.debug(f"HealthMonitor recording failed: {e}")
            
            if response:
                return response
        except Exception as e:
            # NEW: Record failure
            if self._health_monitor:
                try:
                    self._health_monitor.record_failure(model_name)
                except Exception as hm_err:
                    logger.debug(f"HealthMonitor failure recording failed: {hm_err}")
            
            err_msg = str(e).lower()
            # ... rest of existing code ...
    
    return None
```

### Step 4: Set Model-Provider Mapping

For HealthMonitor to work correctly, the model-to-provider mapping must be set. This happens in Oracle initialization:

**File**: `src/omega/oracle/oracle.py`
**Add after line 124**:

```python
# Wire model→provider mapping into HealthMonitor
for provider in self.model_gateway.providers:
    for model in getattr(provider, 'models', [provider.name]):
        self.health_monitor.set_model_provider(model, provider.name)
```

---

## §4 Error Handling

| Scenario | Handling |
|----------|----------|
| HealthMonitor is None | Skip recording, log debug |
| record_latency() raises | Catch, log debug, continue |
| record_success() raises | Catch, log debug, continue |
| record_failure() raises | Catch, log debug, continue |
| Provider name unknown | Use "unknown" as fallback |

**Rationale**: HealthMonitor failures should NEVER block inference. The inference is primary; metrics are secondary.

---

## §5 AnyIO Compliance

All HealthMonitor methods (`record_latency`, `record_success`, `record_failure`) are **synchronous**:
- No `await` needed
- Safe to call from async context
- No blocking I/O inside HealthMonitor methods

The timing measurement uses `time.monotonic()` which is also synchronous and safe.

---

## §6 Testing Requirements

### Unit Tests (test_model_gateway.py)
1. Test `generate()` calls `record_latency` on success
2. Test `generate()` calls `record_success` on success
3. Test `generate()` calls `record_failure` on exception
4. Test graceful degradation when health_monitor is None

### Integration Tests (test_oracle.py)
1. Test full flow: talk → model_gateway.generate → health_monitor updated
2. Test soul update (B5.1): After inference, entity's soul.yaml has new entry

---

## §7 Code Locations Summary

| Location | Action | Line |
|----------|--------|------|
| `model_gateway.py:80` | Add `health_monitor` param to `__init__` | 80 |
| `model_gateway.py:311-348` | Wrap generate with timing + record calls | 311-348 |
| `oracle.py:94` | Pass `health_monitor` to ModelGateway | 94 |
| `oracle.py:126` | Set model→provider mapping | ~126 |

---

## §8 Alternative Approach (If ModelGateway Cannot Be Modified)

If modifying ModelGateway is not desired, the Oracle can wrap the call:

**In `oracle.py` around line 369** (where generate is called):

```python
# Before
response_text = await self.model_gateway.generate(...)

# After (timing wrapper)
import time
start = time.monotonic()
response_text = await self.model_gateway.generate(...)
latency_ms = (time.monotonic() - start) * 1000

# Record metrics
if self.health_monitor:
    try:
        self.health_monitor.record_latency(model_name, latency_ms)
        self.health_monitor.record_success(model_name)
    except Exception as e:
        logger.debug(f"HealthMonitor recording failed: {e}")
```

**However**, this approach has a downside: it cannot record failures because the exception propagates up. The _execute_with_retry approach is preferred.

---

## §9 Recommendation

Use **Step 1-4** (the integrated approach). It provides:
- Complete coverage (success + failure)
- Proper timing per attempt
- Error isolation per call
- Cleaner separation of concerns