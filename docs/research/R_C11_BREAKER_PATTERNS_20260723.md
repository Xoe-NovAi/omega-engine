# 🔱 C-11 Property Test Patterns — Domain 4: CircuitBreaker (7→1 Unification)
**AP Token**: `AP-C11-BREAKER-PATTERNS-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_c11_breaker ⬡ 2026-07-23

---

## §1 Local Implementation Analysis

### 1.1 Canonical Implementation: `AsyncCircuitBreaker` (`src/omega/oracle/health_monitor.py:126-522`)
**C-6' Mandate**: Single canonical circuit breaker. All clones deprecated.

```python
class AsyncCircuitBreaker:
    """5-State FSM: CLOSED → DEGRADED → OPEN → HALF_OPEN → CLOSED
    
    Two detection modes:
    - 'cusum': CUSUM drift detection (default) — gradual degradation
    - 'sliding_window': Rate-based — burst failures
    
    Key features:
    - EMA latency smoothing (alpha=0.2)
    - EMA quality tracking (alpha=0.3)
    - CUSUM anomaly detection (drift=0.5, threshold=4.0)
    - Half-open probe pattern (max 1 request)
    - AnyIO-native async lock
    - ZONEID pattern for state integrity
    - 429 Classification: rate-limit vs quota-exhausted
    """
```

### 1.2 Deprecated: `SearchCircuitBreaker` (`src/omega/oracle/search_circuit_breaker.py`)
**Status**: DEPRECATED per C-6'. 3-state FSM (CLOSED/OPEN/HALF_OPEN), thread-based lock.

### 1.3 Deprecated: `CircuitBreaker` (`src/omega/council/failure_layer.py:48-87`)
**Status**: DEPRECATED per C-6'. Quality-aware for council operations only.

---

## §2 Property-Based Testing Patterns

### 2.1 Pattern 1: State Machine Transitions (5-State FSM)
**Property**: All valid state transitions occur; invalid transitions never occur.

```python
from hypothesis import given, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant
import pytest

class CircuitBreakerStateMachine(RuleBasedStateMachine):
    """Stateful testing of 5-state FSM transitions."""
    
    def __init__(self):
        super().__init__()
        self.breaker = AsyncCircuitBreaker(
            name="test",
            failure_threshold=3,
            recovery_timeout=1.0,  # Fast for testing
            mode="sliding_window",
            window_seconds=1.0,
            max_failures_per_window=3,
        )
        self.state_history = []
    
    @rule()
    async def record_success(self):
        await self.breaker._on_success(latency=100.0, quality=1.0)
        self.state_history.append(self.breaker.state)
    
    @rule()
    async def record_failure(self):
        await self.breaker._on_failure()
        self.state_history.append(self.breaker.state)
    
    @rule()
    async def wait_recovery(self):
        await asyncio.sleep(1.5)  # Exceed recovery_timeout
        # Trigger state check
        await self.breaker._on_success(latency=100.0, quality=1.0)
        self.state_history.append(self.breaker.state)
    
    @invariant()
    def valid_state_transitions(self):
        """Only valid FSM transitions occur."""
        valid_transitions = {
            CircuitState.CLOSED: {CircuitState.CLOSED, CircuitState.DEGRADED, CircuitState.OPEN},
            CircuitState.DEGRADED: {CircuitState.CLOSED, CircuitState.DEGRADED, CircuitState.OPEN},
            CircuitState.OPEN: {CircuitState.OPEN, CircuitState.HALF_OPEN},
            CircuitState.HALF_OPEN: {CircuitState.OPEN, CircuitState.CLOSED},
            CircuitState.UNKNOWN: {CircuitState.CLOSED, CircuitState.OPEN},
        }
        
        for i in range(1, len(self.state_history)):
            prev, curr = self.state_history[i-1], self.state_history[i]
            assert curr in valid_transitions.get(prev, set()), \
                f"Invalid transition: {prev} -> {curr}"

# Run stateful tests
TestCircuitBreakerFSM = CircuitBreakerStateMachine.TestCase
```

### 2.2 Pattern 2: CUSUM Drift Detection Accuracy
**Property**: CUSUM correctly detects sustained failure rate increase.

```python
@given(
    baseline_failure_rate=st.floats(0.01, 0.1),
    drift_magnitude=st.floats(0.1, 0.5),
    num_samples=st.integers(10, 100),
)
@pytest.mark.anyio
async def test_cusum_detects_drift(baseline_failure_rate, drift_magnitude, num_samples):
    """CUSUM detects sustained failure rate drift."""
    breaker = AsyncCircuitBreaker(
        name="cusum_test",
        mode="cusum",
        cusum_drift=0.5,
        cusum_threshold=4.0,
    )
    
    # Phase 1: Baseline failures
    for _ in range(num_samples // 2):
        if random.random() < baseline_failure_rate:
            await breaker._on_failure()
        else:
            await breaker._on_success(latency=100.0, quality=1.0)
    
    cusum_baseline = breaker.cusum_g
    
    # Phase 2: Drifted failure rate
    drifted_rate = min(1.0, baseline_failure_rate + drift_magnitude)
    for _ in range(num_samples // 2):
        if random.random() < drifted_rate:
            await breaker._on_failure()
        else:
            await breaker._on_success(latency=100.0, quality=1.0)
    
    cusum_drifted = breaker.cusum_g
    
    # CUSUM should increase significantly
    assert cusum_drifted > cusum_baseline + 1.0
    
    # If drift is large enough, should trip to OPEN
    if drift_magnitude > 0.3 and num_samples > 30:
        assert breaker.state in (CircuitState.OPEN, CircuitState.DEGRADED)
```

### 2.3 Pattern 3: Sliding Window Rate Detection
**Property**: Sliding window correctly counts failures within time window.

```python
@given(
    failure_times=st.lists(st.floats(0, 10), min_size=1, max_size=20),
    window_seconds=st.floats(1.0, 5.0),
    max_failures=st.integers(2, 10),
)
@pytest.mark.anyio
async def test_sliding_window_accuracy(failure_times, window_seconds, max_failures):
    """Sliding window counts only failures within window."""
    breaker = AsyncCircuitBreaker(
        name="window_test",
        mode="sliding_window",
        window_seconds=window_seconds,
        max_failures_per_window=max_failures,
    )
    
    # Simulate failures at specific times
    start_time = time.monotonic()
    for t in sorted(failure_times):
        # Advance time
        await asyncio.sleep(max(0, t - (time.monotonic() - start_time)))
        await breaker._on_failure()
    
    # Count failures in window
    now = time.monotonic()
    cutoff = now - window_seconds
    expected_failures = sum(1 for t in failure_times if (start_time + t) > cutoff)
    
    # Breaker should have same count
    assert len(breaker._window_failures) == expected_failures
    
    # State should match threshold
    if expected_failures >= max_failures:
        assert breaker.state == CircuitState.OPEN
    elif expected_failures >= max_failures // 2:
        assert breaker.state in (CircuitState.DEGRADED, CircuitState.OPEN)
    else:
        assert breaker.state == CircuitState.CLOSED
```

### 2.4 Pattern 4: Half-Open Probe Correctness
**Property**: Half-open allows exactly one probe; success closes, failure reopens.

```python
@given(
    probe_succeeds=st.booleans(),
    num_probes=st.integers(1, 5),
)
@pytest.mark.anyio
async def test_half_open_probe_limit(probe_succeeds, num_probes):
    """Half-open state allows exactly max_probes before decision."""
    breaker = AsyncCircuitBreaker(
        name="half_open_test",
        failure_threshold=1,
        recovery_timeout=0.1,
        half_open_max_requests=1,
        mode="sliding_window",
        window_seconds=1.0,
        max_failures_per_window=1,
    )
    
    # Force OPEN state
    await breaker._on_failure()
    assert breaker.state == CircuitState.OPEN
    
    # Wait for recovery timeout
    await asyncio.sleep(0.2)
    
    # Trigger half-open transition
    await breaker._on_success(latency=100.0, quality=1.0)
    assert breaker.state == CircuitState.HALF_OPEN
    
    # Try multiple probes
    results = []
    for _ in range(num_probes):
        try:
            if probe_succeeds:
                await breaker._on_success(latency=100.0, quality=1.0)
                results.append("success")
            else:
                await breaker._on_failure()
                results.append("failure")
        except CircuitOpenError:
            results.append("rejected")
    
    if probe_succeeds:
        # First success should close circuit
        assert "success" in results
        assert breaker.state == CircuitState.CLOSED
        # Subsequent probes should be rejected (circuit closed, but we're testing half-open limit)
    else:
        # First failure should reopen
        assert "failure" in results
        assert breaker.state == CircuitState.OPEN
```

### 2.5 Pattern 5: 429 Classification Correctness
**Property**: Rate-limit 429s get short cooldown; quota 429s get long cooldown.

```python
@given(
    retry_after=st.one_of(
        st.floats(1, 60),      # Rate limit: seconds
        st.floats(3600, 86400), # Quota: hours/days
        st.none(),
    ),
    response_body=st.text(max_size=500),
    explicit_quota=st.one_of(st.booleans(), st.none()),
)
@pytest.mark.anyio
async def test_429_classification(retry_after, response_body, explicit_quota):
    """429 responses correctly classified as rate-limit vs quota."""
    breaker = AsyncCircuitBreaker(name="429_test")
    
    await breaker.record_429(
        retry_after=retry_after,
        response_body=response_body,
        is_quota=explicit_quota,
    )
    
    # Check classification
    status = breaker.get_429_status()
    
    if explicit_quota is True:
        assert status["quota_remaining"] > 0
        assert status["rate_limit_remaining"] == 0
    elif explicit_quota is False:
        assert status["rate_limit_remaining"] > 0
        assert status["quota_remaining"] == 0
    else:
        # Auto-detect
        has_quota_keywords = bool(breaker.quota_keywords.search(response_body))
        is_long_cooldown = retry_after is not None and retry_after >= 3600
        
        if has_quota_keywords or is_long_cooldown:
            assert status["quota_remaining"] > 0
        else:
            assert status["rate_limit_remaining"] > 0
```

### 2.6 Pattern 6: ZONEID State Integrity
**Property**: ZONEID magic constant validates state integrity on every transition.

```python
@given(
    num_operations=st.integers(10, 100),
)
@pytest.mark.anyio
async def test_zoneid_integrity(num_operations):
    """ZONEID magic constant validated on every state change."""
    breaker = AsyncCircuitBreaker(name="zoneid_test")
    
    for i in range(num_operations):
        if i % 2 == 0:
            await breaker._on_success(latency=100.0, quality=1.0)
        else:
            await breaker._on_failure()
        
        # ZONEID should be validated internally
        # (Implementation validates in _on_success/_on_failure)
        assert breaker.magic == ZONEID_BREAKER
    
    # Corrupt magic and verify detection
    breaker.magic = 0xDEADBEEF
    try:
        await breaker._on_success(latency=100.0, quality=1.0)
        assert False, "Should have raised validation error"
    except Exception as e:
        assert "ZONEID" in str(e) or "magic" in str(e).lower()
```

### 2.7 Pattern 7: EMA Latency Smoothing
**Property**: EMA latency converges to true mean; doesn't spike on outliers.

```python
@given(
    latencies=st.lists(st.floats(50, 5000), min_size=10, max_size=100),
    outlier=st.floats(10000, 100000),
)
@pytest.mark.anyio
async def test_ema_latency_smoothing(latencies, outlier):
    """EMA latency smooths outliers; converges to mean."""
    breaker = AsyncCircuitBreaker(name="ema_test")
    
    # Feed normal latencies
    for lat in latencies:
        await breaker._on_success(latency=lat, quality=1.0)
    
    ema_normal = breaker.ema_latency
    expected_mean = sum(latencies) / len(latencies)
    
    # EMA should be close to mean (within 20%)
    assert abs(ema_normal - expected_mean) / expected_mean < 0.2
    
    # Feed outlier
    await breaker._on_success(latency=outlier, quality=1.0)
    ema_with_outlier = breaker.ema_latency
    
    # EMA should not jump to outlier (alpha=0.2 means 20% weight)
    max_expected = ema_normal * 0.8 + outlier * 0.2
    assert ema_with_outlier <= max_expected * 1.1  # Allow small margin
```

### 2.8 Pattern 8: Concurrent Access Safety
**Property**: Thread-safe under concurrent success/failure recording.

```python
@given(
    num_tasks=st.integers(10, 100),
    operations_per_task=st.integers(10, 50),
)
@pytest.mark.anyio
async def test_concurrent_access_safety(num_tasks, operations_per_task):
    """Concurrent success/failure recording doesn't corrupt state."""
    breaker = AsyncCircuitBreaker(name="concurrent_test")
    
    async def worker(worker_id):
        for i in range(operations_per_task):
            if (worker_id + i) % 3 == 0:
                await breaker._on_failure()
            else:
                await breaker._on_success(latency=100.0, quality=1.0)
    
    await asyncio.gather(*[worker(i) for i in range(num_tasks)])
    
    # State should be consistent
    assert breaker.state in CircuitState
    assert breaker.failure_count >= 0
    assert breaker.ema_latency >= 0
    assert 0 <= breaker.ema_quality <= 1
    assert breaker.cusum_g >= 0
```

---

## §3 Hypothesis Strategy Composites

### 3.1 CircuitBreakerConfig Strategy
```python
from hypothesis import strategies as st

@st.composite
def circuit_breaker_config(draw):
    """Generate valid circuit breaker configurations."""
    return {
        "failure_threshold": draw(st.integers(1, 20)),
        "recovery_timeout": draw(st.floats(1.0, 300.0)),
        "half_open_max_requests": draw(st.integers(1, 5)),
        "mode": draw(st.sampled_from(["cusum", "sliding_window"])),
        "window_seconds": draw(st.floats(1.0, 60.0)),
        "max_failures_per_window": draw(st.integers(1, 50)),
    }
```

### 3.2 Failure Sequence Strategy
```python
@st.composite
def failure_sequence(draw, length=20):
    """Generate realistic failure/success sequences."""
    # Burst pattern: periods of failures followed by recovery
    pattern = draw(st.sampled_from(["steady", "burst", "gradual", "oscillating"]))
    
    if pattern == "steady":
        failure_rate = draw(st.floats(0.0, 0.5))
        return [draw(st.booleans().map(lambda x: x if random.random() < failure_rate else not x)) 
                for _ in range(length)]
    
    elif pattern == "burst":
        # Normal then burst then recovery
        normal_len = draw(st.integers(3, length//3))
        burst_len = draw(st.integers(3, length//2))
        recovery_len = length - normal_len - burst_len
        
        seq = [False] * normal_len  # Normal
        seq += [True] * burst_len   # Burst
        seq += [False] * recovery_len  # Recovery
        return seq
    
    elif pattern == "gradual":
        # Gradually increasing failure rate
        return [random.random() < (i / length * 0.8) for i in range(length)]
    
    else:  # oscillating
        return [i % 4 < 2 for i in range(length)]  # 2 fail, 2 succeed
```

---

## §4 Integration with Existing Test Pattern

### 4.1 Proven Pattern Adaptation
```python
# From tests/property/test_breaker_fsm.py
@pytest.mark.anyio
@given(st.data())
async def test_circuit_breaker_property(data):
    config = data.draw(circuit_breaker_config())
    breaker = AsyncCircuitBreaker(name="prop_test", **config)
    
    # Generate failure sequence
    seq = data.draw(failure_sequence(length=50))
    
    for is_failure in seq:
        if is_failure:
            await breaker._on_failure()
        else:
            await breaker._on_success(latency=100.0, quality=1.0)
    
    # Verify invariants
    assert breaker.state in CircuitState
    assert breaker.failure_count >= 0
    assert breaker.cusum_g >= 0
```

---

## §5 Extraction Targets for Omega Engine

| Pattern | Omega Type | Test File | Status |
|---------|------------|-----------|--------|
| 5-State FSM transitions | `AsyncCircuitBreaker` | `test_breaker_fsm.py` | ✅ Exists |
| CUSUM drift detection | `AsyncCircuitBreaker.cusum_g` | `test_breaker_cusum.py` | Ready |
| Sliding window rate | `AsyncCircuitBreaker._window_failures` | `test_breaker_window.py` | Ready |
| Half-open probe | `AsyncCircuitBreaker.half_open_max_requests` | `test_breaker_halfopen.py` | Ready |
| 429 classification | `AsyncCircuitBreaker.record_429` | `test_breaker_429.py` | Ready |
| ZONEID integrity | `AsyncCircuitBreaker.magic` | `test_breaker_zoneid.py` | Ready |
| EMA latency smoothing | `AsyncCircuitBreaker.ema_latency` | `test_breaker_ema.py` | Ready |
| Concurrent safety | `AsyncCircuitBreaker._lock` | `test_breaker_concurrent.py` | Ready |

---

## §6 Key Findings Summary

1. **Canonical Implementation Exists**: `AsyncCircuitBreaker` in `health_monitor.py` is the single source of truth (C-6')
2. **5-State FSM**: CLOSED → DEGRADED → OPEN → HALF_OPEN → CLOSED (more nuanced than 3-state)
3. **Dual Detection Modes**: CUSUM (gradual) + Sliding Window (burst) - configurable
4. **429 Classification**: Critical hardening - separates rate-limit (seconds) from quota (hours/days)
5. **ZONEID Pattern**: Magic constant validates state integrity on every transition
6. **EMA Metrics**: Latency and quality tracked with exponential moving averages
6. **AnyIO Native**: Uses `anyio.Lock`, not `threading.RLock` or `asyncio.Lock`
7. **Observability Integration**: Breaker transitions logged to MetricsDB/Engine

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ C-11 Domain 4 Complete ⬡ 2026-07-23*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
