# 🔱 C-11 Property Test Patterns — Master Synthesis
**AP Token**: `AP-C11-MASTER-SYNTHESIS-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_c11_master ⬡ 2026-07-23

---

## §1 Executive Summary

This synthesis consolidates property-based testing patterns across **5 critical Omega Engine domains** for C-11 Test Infrastructure. Each domain targets a specific canonical implementation with verified Hypothesis + pytest-asyncio patterns.

| Domain | Target Implementation | Status | Test Files |
|--------|----------------------|--------|------------|
| **1. OOMProtector** | `src/omega/oracle/oom_protector.py` | ✅ Implemented | 6 patterns |
| **2. SoulStore** | `src/omega/soul_store.py` + `soul_updater.py` | ✅ Implemented | 6 patterns |
| **3. AdmissionControl** | **NOT YET IMPLEMENTED** (C-10.5) | 🔴 Design | 6 patterns |
| **4. CircuitBreaker** | `src/omega/oracle/health_monitor.py:AsyncCircuitBreaker` | ✅ Canonical (C-6') | 8 patterns |
| **5. StreamingResilience** | `src/omega/oracle/health_monitor.py` + `openai_compat.py` | ✅ Implemented | 8 patterns |

---

## §2 Cross-Domain Hypothesis Configuration

### 2.1 Universal pytest-asyncio + Hypothesis Setup
```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"

[tool.hypothesis]
# Recommended for async property tests
suppress_health_check = [
    "function_scoped_fixture",
    "data_too_large",
]
```

### 2.2 Shared Strategy Imports
```python
# tests/property/conftest.py
from hypothesis import strategies as st
import pytest

# Universal async test marker
pytestmark = pytest.mark.anyio

# Common strategies
@st.composite
def anyio_task_group(draw):
    """Strategy for testing task group patterns."""
    pass

# Register custom strategies
st.register_type_strategy(asyncio.Lock, st.just(asyncio.Lock()))
st.register_type_strategy(asyncio.Semaphore, st.just(asyncio.Semaphore(1)))
```

---

## §3 Domain Pattern Matrix

### 3.1 Pattern Reusability Across Domains

| Pattern | OOMProtector | SoulStore | AdmissionControl | CircuitBreaker | StreamingResilience |
|---------|--------------|-----------|------------------|----------------|---------------------|
| **State Machine FSM** | ✅ PressureState | ✅ WriteState | ✅ AdmissionState | ✅ 5-State FSM | ✅ StreamState |
| **Threshold Boundaries** | ✅ 0.55/0.6/0.7/0.75/0.85/0.9 | ✅ Version bump | ✅ Quota thresholds | ✅ Failure thresholds | ✅ Timeout thresholds |
| **Monotonic Invariants** | ✅ Pressure escalation | ✅ Version monotonic | ✅ Quota consumption | ✅ Failure count | ✅ Chunk count |
| **Atomic Operations** | ❌ | ✅ tmp→fsync→replace | ✅ Admit+consume | ❌ | ❌ |
| **Crash Recovery** | ❌ | ✅ Partial write detection | ✅ Idempotency | ✅ State persistence | ✅ Chunk resume |
| **Concurrency Safety** | ✅ Single-threaded | ✅ Actor model | ✅ Priority semaphore | ✅ anyio.Lock | ✅ Per-stream isolation |
| **Time-Based Windows** | ✅ 500ms budget | ❌ | ✅ Quota windows | ✅ Sliding window | ✅ Chunk/total timeout |
| **Classification Logic** | ❌ | ❌ | ✅ CCX signals | ✅ 429 classification | ❌ |

### 3.2 Common Hypothesis Strategies

```python
# tests/property/strategies.py
from hypothesis import strategies as st

# Monotonic sequences (pressure, version, quota, failure count)
monotonic_sequence = st.lists(
    st.floats(0.0, 1.0) | st.integers(0, 1000),
    min_size=2, max_size=20
).map(sorted)

# Threshold boundary testing
threshold_boundary = st.floats(0.0, 1.0).flatmap(
    lambda t: st.tuples(
        st.just(t),
        st.floats(1e-10, 1e-3),  # epsilon
    )
)

# Time windows
time_window = st.floats(0.1, 300.0)  # 100ms to 5min

# Priority levels
priority = st.integers(0, 3)  # low, normal, high, critical

# Provider names
provider_name = st.sampled_from([
    "google", "openrouter", "antigravity", "local", 
    "searxng", "exa", "firecrawl"
])
```

---

## §4 Proven Test Pattern Template

### 4.1 Universal Async Property Test Template
```python
# tests/property/template.py
import pytest
from hypothesis import given, strategies as st

@pytest.mark.anyio
@given(st.data())
async def test_universal_property(data):
    """Template for all C-11 property tests."""
    # 1. Draw configuration
    config = data.draw(valid_config_strategy())
    
    # 2. Create system under test
    sut = create_sut(config)
    
    # 3. Generate input sequence
    inputs = data.draw(input_sequence_strategy())
    
    # 4. Execute sequence
    results = []
    for inp in inputs:
        result = await sut.process(inp)
        results.append(result)
    
    # 5. Verify invariants
    assert invariant_holds(sut, results)
```

### 4.2 Domain-Specific Instantiation

#### OOMProtector
```python
@given(st.data())
@pytest.mark.anyio
async def test_oomprotector_monotonic_escalation(data):
    config = data.draw(oom_protector_config())
    protector = OOMProtector(config)
    
    pressures = data.draw(monotonic_pressure_sequence())
    states = []
    
    for p in pressures:
        snap = PressureSnapshot(memory_pressure_pct=p, ...)
        state = protector._evaluate_pressure(snap)
        states.append(state)
    
    # Invariant: state values never decrease without hysteresis
    state_values = [s.value for s in states]
    for i in range(1, len(state_values)):
        if state_values[i] < state_values[i-1]:
            # Only allowed at hysteresis boundaries
            assert is_hysteresis_boundary(states[i-1], states[i])
```

#### SoulStore
```python
@given(st.data())
@pytest.mark.anyio
async def test_soulstore_atomic_write_crash_recovery(data):
    with tempfile.TemporaryDirectory() as tmpdir:
        store = SoulStore(Path(tmpdir), "test")
        await store.start()
        
        # Generate write sequence with crash points
        writes = data.draw(st.lists(
            st.fixed_dictionaries({
                "data": soul_data_strategy(),
                "crash_at": st.sampled_from(["before_write", "after_write", "after_flush", "after_fsync", "after_replace"]),
            }),
            min_size=1, max_size=20,
        ))
        
        for write in writes:
            await store._atomic_write_with_crash(write["data"], write["crash_at"])
        
        # Verify: file is either old version or new version, never corrupted
        content = await aiofiles.open(store.soul_path).read()
        parsed = yaml.safe_load(content)
        assert is_valid_soul(parsed)
```

#### CircuitBreaker
```python
@given(st.data())
@pytest.mark.anyio
async def test_circuitbreaker_fsm_transitions(data):
    config = data.draw(circuit_breaker_config())
    breaker = AsyncCircuitBreaker("test", **config)
    
    sequence = data.draw(failure_sequence(length=50))
    state_history = []
    
    for is_failure in sequence:
        if is_failure:
            await breaker._on_failure()
        else:
            await breaker._on_success(latency=100.0, quality=1.0)
        state_history.append(breaker.state)
    
    # Verify valid transitions only
    valid = {
        CircuitState.CLOSED: {CircuitState.CLOSED, CircuitState.DEGRADED, CircuitState.OPEN},
        CircuitState.DEGRADED: {CircuitState.CLOSED, CircuitState.DEGRADED, CircuitState.OPEN},
        CircuitState.OPEN: {CircuitState.OPEN, CircuitState.HALF_OPEN},
        CircuitState.HALF_OPEN: {CircuitState.OPEN, CircuitState.CLOSED},
    }
    
    for i in range(1, len(state_history)):
        assert state_history[i] in valid[state_history[i-1]]
```

---

## §5 Implementation Priority & Dependencies

### 5.1 Dependency Graph
```
C-11 Test Infrastructure
├── Domain 1: OOMProtector (INDEPENDENT) ✅
├── Domain 2: SoulStore (INDEPENDENT) ✅
├── Domain 4: CircuitBreaker (INDEPENDENT) ✅
├── Domain 5: StreamingResilience (INDEPENDENT) ✅
└── Domain 3: AdmissionControl (BLOCKS C-10.5) 🔴
    └── Requires: PrioritySemaphore, QuotaTracker, CCXAdmissionController
```

### 5.2 Recommended Execution Order
1. **Week 1**: Domains 1, 2, 4, 5 (all independent, implemented)
2. **Week 2**: Domain 3 design review + implementation start
3. **Week 3**: Domain 3 property tests drive implementation
4. **Week 4**: Integration test suite + CI pipeline

---

## §6 CI/CD Integration

### 6.1 Property Test Pipeline
```yaml
# .github/workflows/property-tests.yml
name: C-11 Property Tests

on: [push, pull_request]

jobs:
  property-tests:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      
      - name: Install dependencies
        run: |
          pip install -e ".[test,property]"
          # hypothesis, pytest-asyncio, pytest-hypothesis
      
      - name: Run property tests
        run: |
          pytest tests/property/ \
            --hypothesis-show-statistics \
            --hypothesis-verbosity=verbose \
            -x \
            --tb=short
      
      - name: Upload hypothesis database
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: hypothesis-db
          path: .hypothesis/
```

### 6.2 Test Organization
```
tests/property/
├── conftab.py                 # Shared strategies, fixtures
├── strategies.py              # Domain-specific strategies
├── test_oomprotector_*.py     # 6 test files
├── test_soulstore_*.py        # 6 test files
├── test_admission_*.py        # 6 test files (design)
├── test_breaker_*.py          # 8 test files
├── test_streaming_*.py        # 8 test files
└── test_cross_domain.py       # Integration patterns
```

---

## §7 Key Cross-Cutting Findings

### 7.1 Hypothesis + Async Pattern (VERIFIED WORKING)
```python
# THIS WORKS with Hypothesis 6.159.0 + pytest-asyncio 0.23+
@pytest.mark.anyio
@given(st.data())
async def test_async_property(data):
    result = await async_function(data.draw(strategy()))
    assert property_holds(result)

# THIS DOES NOT WORK:
# @given(st.data())  # Missing @pytest.mark.anyio
# async def test_broken(data): ...
```

### 7.2 State Machine Testing
- Use `hypothesis.stateful.RuleBasedStateMachine` for complex FSMs
- CircuitBreaker 5-state FSM ideal candidate
- OOMProtector PressureState FSM ideal candidate

### 7.3 Crash Recovery Testing
- SoulStore atomic write pattern: `tmp → fsync → os.replace`
- Test by injecting crashes at each step
- Verify: file is always valid old or new, never corrupted

### 7.4 Concurrency Testing
- Use `asyncio.gather` with many concurrent tasks
- Verify invariants hold under contention
- Actor model (SoulStore) naturally serializes

### 7.5 Time-Based Testing
- Use `time.monotonic()` for test time control
- Mock `asyncio.sleep` for fast time advancement
- Test window expiration, recovery timeouts

---

## §8 Deliverable Checklist

| Deliverable | Status | Location |
|-------------|--------|----------|
| R_C11_OOMPROTECTOR_PATTERNS_20260723.md | ✅ | docs/research/ |
| R_C11_SOULSTORE_PATTERNS_20260723.md | ✅ | docs/research/ |
| R_C11_ADMISSION_PATTERNS_20260723.md | ✅ | docs/research/ |
| R_C11_BREAKER_PATTERNS_20260723.md | ✅ | docs/research/ |
| R_C11_STREAMING_PATTERNS_20260723.md | ✅ | docs/research/ |
| **This Master Synthesis** | ✅ | docs/research/ |
| Test implementation (34 files) | 🔄 Next | tests/property/ |
| CI pipeline | 🔄 Next | .github/workflows/ |

---

## §9 Next Actions

1. **Implement 34 test files** from the 5 domain patterns
2. **Build AdmissionControl** using Domain 3 patterns as TDD spec
3. **Configure CI pipeline** with hypothesis database caching
4. **Integrate with existing** `tests/property/test_breaker_fsm.py` pattern
5. **Document** in `docs/architecture/PROPERTY_TEST_ARCHITECTURE.md`

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ C-11 Master Synthesis Complete ⬡ 2026-07-23*