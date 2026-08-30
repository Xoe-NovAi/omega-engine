# 🔱 C-11 Property Test Patterns — Domain 3: AdmissionControl & CCX-Aware Semaphore
**AP Token**: `AP-C11-ADMISSION-PATTERNS-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_c11_admission ⬡ 2026-07-23

---

## §1 Local Implementation Analysis

### 1.1 AdmissionController — NOT YET IMPLEMENTED
Per `tests/conftest.py:147-152`:
```python
"""Fresh AdmissionController per test."""
pytest.skip("AdmissionController not yet implemented")
```

### 1.2 Design Spec from C-10.5 Research Guide
The AdmissionController must implement:
- **CCX-Aware Semaphore**: Semaphore that understands provider quotas (requests/minute, tokens/minute)
- **Priority Inversion Prevention**: High-priority requests don't starve behind low-priority
- **Quota Management**: Tracks per-provider daily/monthly limits
- **Admission Decision**: Accept/reject/defer based on current load + quota

### 1.3 ProviderFabric Integration (`src/omega/oracle/provider_fabric.py`)
```python
class ProviderFabric:
    def __init__(self, providers: dict):
        self.providers = providers
        self._semaphores: dict[str, asyncio.Semaphore] = {}
    
    async def acquire(self, provider: str, priority: int = 0) -> bool:
        """Acquire admission slot for provider."""
        # TODO: CCX-aware semaphore
        pass
```

---

## §2 Property-Based Testing Patterns

### 2.1 Pattern 1: Semaphore Fairness Under Contention
**Property**: Under high contention, all waiters eventually acquire (no starvation).

```python
from hypothesis import given, strategies as st
import pytest
import asyncio

@given(
    num_requesters=st.integers(5, 50),
    max_concurrent=st.integers(1, 10),
    request_duration_ms=st.integers(10, 100),
)
@pytest.mark.anyio
async def test_semaphore_no_starvation(num_requesters, max_concurrent, request_duration_ms):
    """All requesters eventually acquire semaphore - no starvation."""
    semaphore = asyncio.Semaphore(max_concurrent)
    acquired = []
    completed = []
    
    async def requester(requester_id):
        async with semaphore:
            acquired.append(requester_id)
            await asyncio.sleep(request_duration_ms / 1000)
            completed.append(requester_id)
    
    # Launch all requesters concurrently
    await asyncio.gather(*[requester(i) for i in range(num_requesters)])
    
    # All should have acquired and completed
    assert set(acquired) == set(range(num_requesters))
    assert set(completed) == set(range(num_requesters))
```

### 2.2 Pattern 2: Priority Inversion Prevention
**Property**: High-priority requests don't wait behind low-priority when capacity exists.

```python
@given(
    high_priority_count=st.integers(1, 5),
    low_priority_count=st.integers(5, 20),
    capacity=st.integers(2, 10),
)
@pytest.mark.anyio
async def test_priority_preemption(high_priority_count, low_priority_count, capacity):
    """High-priority requests acquire before low-priority when capacity available."""
    from omega.admission import PrioritySemaphore  # Hypothetical
    
    sem = PrioritySemaphore(capacity)
    acquisition_order = []
    
    async def low_priority_worker(worker_id):
        await sem.acquire(priority=0)
        acquisition_order.append(("low", worker_id))
        await asyncio.sleep(0.01)
        sem.release()
    
    async def high_priority_worker(worker_id):
        await sem.acquire(priority=1)
        acquisition_order.append(("high", worker_id))
        await asyncio.sleep(0.01)
        sem.release()
    
    # Start low-priority workers first
    low_tasks = [low_priority_worker(i) for i in range(low_priority_count)]
    await asyncio.gather(*low_tasks)
    
    # Then start high-priority workers
    high_tasks = [high_priority_worker(i) for i in range(high_priority_count)]
    await asyncio.gather(*high_tasks)
    
    # High-priority should have acquired before low-priority released
    # (Implementation detail: priority queue in semaphore)
    high_acquisitions = [i for i, (p, _) in enumerate(acquisition_order) if p == "high"]
    low_acquisitions = [i for i, (p, _) in enumerate(acquisition_order) if p == "low"]
    
    # At least some high-priority should have acquired before low-priority finished
    assert min(high_acquisitions) < max(low_acquisitions) if low_acquisitions else True
```

### 2.3 Pattern 3: Quota Enforcement Accuracy
**Property**: Quota tracking never allows over-consumption.

```python
@given(
    daily_limit=st.integers(100, 10000),
    num_requests=st.integers(1, 200),
    tokens_per_request=st.integers(1, 500),
)
@pytest.mark.anyio
async def test_quota_never_exceeded(daily_limit, num_requests, tokens_per_request):
    """Quota tracker never allows consumption beyond limit."""
    from omega.admission import QuotaTracker  # Hypothetical
    
    tracker = QuotaTracker(daily_limit=daily_limit)
    granted = 0
    denied = 0
    
    for _ in range(num_requests):
        if await tracker.try_consume(tokens_per_request):
            granted += 1
        else:
            denied += 1
    
    # Total granted tokens must not exceed limit
    assert granted * tokens_per_request <= daily_limit
    
    # If all requests would exceed, some must be denied
    if num_requests * tokens_per_request > daily_limit:
        assert denied > 0
```

### 2.4 Pattern 4: CCX (Concurrency Control) Signal Fusion
**Property**: Admission decision correctly fuses multiple signals (latency, error rate, quota).

```python
@given(
    current_latency_p99=st.floats(100, 10000),
    error_rate=st.floats(0.0, 1.0),
    quota_usage=st.floats(0.0, 1.0),
    capacity=st.integers(1, 100),
)
@pytest.mark.anyio
async def test_ccx_decision_logic(current_latency_p99, error_rate, quota_usage, capacity):
    """CCX admission decision correctly weighs all signals."""
    from omega.admission import CCXAdmissionController  # Hypothetical
    
    controller = CCXAdmissionController(
        capacity=capacity,
        latency_threshold_p99=5000,
        error_rate_threshold=0.1,
        quota_threshold=0.9,
    )
    
    decision = await controller.decide(
        latency_p99=current_latency_p99,
        error_rate=error_rate,
        quota_usage=quota_usage,
    )
    
    # Decision logic invariants
    if quota_usage >= 0.95:
        assert decision == "REJECT"  # Hard quota limit
    elif error_rate > 0.5:
        assert decision in ("REJECT", "DEFER")  # High error rate
    elif current_latency_p99 > 10000:
        assert decision in ("REJECT", "DEFER")  # Extreme latency
    elif quota_usage < 0.5 and error_rate < 0.05 and current_latency_p99 < 2000:
        assert decision == "ACCEPT"  # Healthy
```

### 2.5 Pattern 5: Admission Controller Idempotency
**Property**: Duplicate admission requests for same operation don't double-count.

```python
@given(
    request_id=st.uuids(),
    num_duplicates=st.integers(1, 10),
)
@pytest.mark.anyio
async def test_admission_idempotency(request_id, num_duplicates):
    """Duplicate admission requests don't double-count against quota."""
    from omega.admission import AdmissionController  # Hypothetical
    
    controller = AdmissionController(capacity=100)
    
    # Submit same request multiple times
    results = []
    for _ in range(num_duplicates):
        result = await controller.request_admission(
            request_id=request_id,
            estimated_tokens=10,
        )
        results.append(result)
    
    # All should return same decision
    assert all(r == results[0] for r in results)
    
    # Quota should only be consumed once
    assert controller.quota_consumed == 10
```

### 2.6 Pattern 6: Graceful Degradation Under Load
**Property**: System degrades gracefully - rejects excess load rather than crashing.

```python
@given(
    burst_size=st.integers(100, 10000),
    capacity=st.integers(10, 100),
    processing_time_ms=st.integers(1, 50),
)
@pytest.mark.anyio
async def test_graceful_degradation(burst_size, capacity, processing_time_ms):
    """Under burst load, controller rejects excess rather than queueing indefinitely."""
    from omega.admission import AdmissionController  # Hypothetical
    
    controller = AdmissionController(capacity=capacity)
    admitted = 0
    rejected = 0
    
    async def burst_request():
        nonlocal admitted, rejected
        decision = await controller.request_admission("burst", estimated_tokens=1)
        if decision == "ACCEPT":
            admitted += 1
            await asyncio.sleep(processing_time_ms / 1000)
            controller.release()
        else:
            rejected += 1
    
    # Fire all requests simultaneously
    await asyncio.gather(*[burst_request() for _ in range(burst_size)])
    
    # Should not exceed capacity at any point
    # (Implementation would need to track concurrent admissions)
    assert admitted <= capacity + 1  # Allow small race window
    assert rejected >= burst_size - capacity - 1
```

---

## §3 Hypothesis Strategy Composites

### 3.1 CCX Signal Strategy
```python
from hypothesis import strategies as st

@st.composite
def ccx_signals(draw):
    """Generate realistic CCX signal combinations."""
    # Correlated signals: high latency often correlates with high error rate
    base_load = draw(st.floats(0.0, 1.0))
    
    latency_p99 = draw(st.floats(
        min_value=100 + base_load * 5000,
        max_value=100 + base_load * 15000,
    ))
    
    error_rate = draw(st.floats(
        min_value=base_load * 0.01,
        max_value=min(1.0, base_load * 0.5),
    ))
    
    quota_usage = draw(st.floats(
        min_value=base_load * 0.2,
        max_value=min(1.0, base_load * 1.2),
    ))
    
    return {
        "latency_p99": latency_p99,
        "error_rate": error_rate,
        "quota_usage": quota_usage,
    }
```

### 3.2 Admission Request Strategy
```python
@st.composite
def admission_request(draw):
    """Generate admission request with realistic parameters."""
    return {
        "request_id": draw(st.uuids()),
        "priority": draw(st.integers(0, 3)),  # 0=low, 1=normal, 2=high, 3=critical
        "estimated_tokens": draw(st.integers(10, 8000)),
        "estimated_latency_ms": draw(st.integers(100, 5000)),
        "provider": draw(st.sampled_from(["google", "openrouter", "antigravity", "local"])),
        "trace_id": draw(st.uuids()),
    }
```

---

## §4 Integration with Existing Test Pattern

### 4.1 Proven Pattern Adaptation
```python
# From tests/property/test_breaker_fsm.py pattern
@pytest.mark.anyio
@given(st.data())
async def test_admission_controller_property(data):
    controller = AdmissionController(capacity=100)
    
    # Generate concurrent admission requests
    num_requests = data.draw(st.integers(10, 200))
    requests = data.draw(st.lists(admission_request(), min_size=num_requests, max_size=num_requests))
    
    async def request_admission(req):
        return await controller.request_admission(**req)
    
    results = await asyncio.gather(*[request_admission(r) for r in requests])
    
    # Verify invariants
    accepted = sum(1 for r in results if r == "ACCEPT")
    assert accepted <= 100  # Never exceed capacity
```

---

## §5 Extraction Targets for Omega Engine

| Pattern | Omega Type | Test File | Status |
|---------|------------|-----------|--------|
| Semaphore fairness | `asyncio.Semaphore` wrapper | `test_admission_fairness.py` | Design |
| Priority inversion prevention | `PrioritySemaphore` | `test_admission_priority.py` | Design |
| Quota enforcement | `QuotaTracker` | `test_admission_quota.py` | Design |
| CCX signal fusion | `CCXAdmissionController` | `test_admission_ccx.py` | Design |
| Idempotency | `AdmissionController` | `test_admission_idempotent.py` | Design |
| Graceful degradation | `AdmissionController` | `test_admission_degradation.py` | Design |

---

## §6 Key Findings Summary

1. **AdmissionController Not Implemented**: This is a greenfield design - property tests will drive implementation
2. **CCX-Aware Semaphore**: Must fuse latency, error rate, quota into single admission decision
3. **Priority Semaphore**: Standard `asyncio.Semaphore` doesn't support priority - needs custom implementation
4. **Quota Tracking**: Must be atomic with admission decision to prevent race conditions
5. **Hypothesis + Async**: Use `@pytest.mark.anyio` + `@given` with `asyncio_mode=auto` in pyproject.toml

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ C-11 Domain 3 Complete ⬡ 2026-07-23*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
