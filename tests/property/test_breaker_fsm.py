"""Hypothesis property-based tests for AsyncCircuitBreaker (C-11).

[PHASE-C-HARDENING] Two layers:
1. Synchronous RuleBasedStateMachine for 429 classification (no async needed)
2. Async @given tests for FSM state transitions

Key properties tested:
    - 429 classification is independent of circuit state
    - record_429 with arbitrary text never crashes
    - Circuit state transitions correctly (CLOSED→DEGRADED→OPEN)
    - Circuit heals with enough successes
"""
import time
from functools import partial

import anyio
import pytest
from hypothesis import HealthCheck, given, settings, strategies as st
from hypothesis.stateful import (
    RuleBasedStateMachine,
    invariant,
    precondition,
    rule,
    run_state_machine_as_test,
)

from omega.oracle.health_monitor import (
    AsyncCircuitBreaker,
    CircuitOpenError,
    CircuitState,
)

# ── Synchronous: 429 Classification Properties ────────────────────────────────


class Breaker429Machine(RuleBasedStateMachine):
    """Sync-only state machine for 429 classification.
    
    Tests that 429 recording is independent of circuit state.
    No async calls needed — record_429 and is_429_blocked are sync.
    """
    
    def __init__(self):
        super().__init__()
        self.breaker = AsyncCircuitBreaker(
            "test-429-sync",
            failure_threshold=3,
            recovery_timeout=0.01,
        )
        self.history: list[tuple[str, CircuitState, bool]] = []
    
    @rule()
    def record_429_rate_limit(self):
        """Record a rate-limit 429 — must NOT change circuit state."""
        state_before = self.breaker.state
        self.breaker.record_429(retry_after=30.0, response_body="rate limit")
        assert self.breaker.state == state_before, "429 changed circuit state!"
        assert self.breaker.is_429_blocked() is True
        self.history.append(("429_rate", self.breaker.state, True))
    
    @rule()
    def record_429_quota(self):
        """Record a quota 429 — must NOT change circuit state."""
        state_before = self.breaker.state
        self.breaker.record_429(
            retry_after=7200.0,
            response_body="monthly quota exceeded",
        )
        assert self.breaker.state == state_before, "429 quota changed circuit state!"
        assert self.breaker.quota_until is not None
        self.history.append(("429_quota", self.breaker.state, True))
    
    @rule(body=st.text(max_size=500))
    def record_429_arbitrary_body(self, body: str):
        """Record 429 with arbitrary body — must never crash."""
        state_before = self.breaker.state
        try:
            self.breaker.record_429(retry_after=60.0, response_body=body)
        except Exception as e:
            raise AssertionError(f"record_429 crashed: body={body!r}: {e}")
        assert self.breaker.state == state_before
    
    @rule()
    def wait_cooldown(self):
        """Wait for a 429 cooldown to expire (clear both rate-limit and quota)."""
        self.breaker.rate_limit_until = time.monotonic() - 0.01
        self.breaker.quota_until = time.monotonic() - 0.01
        assert self.breaker.is_429_blocked() is False
    
    @invariant()
    def blocked_means_timestamps_set(self):
        """If blocked, cooldown timestamps must be set."""
        if self.breaker.is_429_blocked():
            assert (
                self.breaker.rate_limit_until is not None
                or self.breaker.quota_until is not None
            ), "Blocked but no cooldown"
    
    @invariant()
    def valid_state(self):
        """Breaker must always be in a known state."""
        assert self.breaker.state in CircuitState
    
    @invariant()
    def no_negative_count(self):
        """Failure count must never be negative."""
        assert self.breaker.failure_count >= 0


class TestBreaker429Properties:
    """Property-based tests for 429 classification (sync)."""
    
    def test_429_independence(self):
        """429 classification must never affect circuit state."""
        run_state_machine_as_test(
            Breaker429Machine,
            settings=settings(
                max_examples=20,
                stateful_step_count=25,
                suppress_health_check=[HealthCheck.too_slow],
            ),
        )
    
    def test_429_rate_limit_cooldown(self):
        """Rate-limit cooldown expires and blocks clear."""
        run_state_machine_as_test(
            Breaker429Machine,
            settings=settings(
                max_examples=10,
                stateful_step_count=20,
                suppress_health_check=[HealthCheck.too_slow],
            ),
        )


# ── Async: FSM Transition Tests (using anyio) ────────────────────────────────


class TestBreakerFSMAsync:
    """Async FSM transition tests using Hypothesis @given + anyio."""
    
    @pytest.mark.anyio
    @given(
        mode=st.sampled_from(["cusum", "sliding_window"]),
        failures=st.integers(min_value=1, max_value=15),
    )
    @settings(max_examples=30)
    async def test_failures_trip_circuit(self, mode: str, failures: int):
        """Enough failures must trip the circuit OPEN."""
        breaker = AsyncCircuitBreaker(
            "async-fsm",
            failure_threshold=5,
            recovery_timeout=0.01,
            mode=mode,
            max_failures_per_window=5,
        )
        for _ in range(failures):
            async def _fail():
                raise ConnectionError("connection refused — simulated provider failure")
            try:
                await breaker.call(_fail)
            except (ConnectionError, CircuitOpenError):
                pass
        
        state = breaker.state
        if failures >= 5:
            assert state == CircuitState.OPEN, (
                f"{failures} failures with threshold=5 should OPEN, got {state}"
            )
        else:
            assert state in (
                CircuitState.CLOSED, CircuitState.DEGRADED
            ), f"{failures} failures should not OPEN, got {state}"
    
    @pytest.mark.anyio
    @given(
        mode=st.sampled_from(["cusum", "sliding_window"]),
        initial_failures=st.integers(min_value=5, max_value=10),
    )
    @settings(max_examples=20)
    async def test_circuit_heals_with_success(self, mode: str, initial_failures: int):
        """After enough successes, circuit returns to CLOSED or DEGRADED."""
        breaker = AsyncCircuitBreaker(
            "async-heal",
            failure_threshold=5,
            recovery_timeout=0.01,
            mode=mode,
            max_failures_per_window=5,
        )
        # Trip the circuit
        for _ in range(initial_failures):
            async def _fail():
                raise ConnectionError("connection refused — simulated provider failure")
            try:
                await breaker.call(_fail)
            except (ConnectionError, CircuitOpenError):
                pass
        
        # Wait for recovery_timeout to elapse so circuit transitions to HALF_OPEN
        await anyio.sleep(0.02)
        
        # Heal with successes
        for _ in range(initial_failures * 3):
            async def _succeed():
                return "ok"
            try:
                await breaker.call(_succeed)
            except CircuitOpenError:
                pass
        
        assert breaker.state in (
            CircuitState.CLOSED, CircuitState.DEGRADED
        ), f"Failed to heal: {breaker.state}"
    
    @pytest.mark.anyio
    @given(
        mode=st.sampled_from(["cusum", "sliding_window"]),
    )
    @settings(max_examples=20)
    async def test_429_does_not_affect_circuit(self, mode: str):
        """429 classification async: must not change circuit state."""
        breaker = AsyncCircuitBreaker(
            "async-429",
            failure_threshold=3,
            mode=mode,
        )
        state_before = breaker.state
        breaker.record_429(retry_after=30.0)
        assert breaker.state == state_before
        assert breaker.is_429_blocked() is True
    
    @pytest.mark.anyio
    @given(
        retry_after=st.floats(
            min_value=0, max_value=86400,
            allow_nan=False, allow_infinity=False,
        ),
        body=st.text(max_size=500),
    )
    @settings(max_examples=50)
    async def test_429_orthogonal_all_inputs(self, retry_after: float, body: str):
        """429 with any retry-after and body must not crash or change state."""
        breaker = AsyncCircuitBreaker("async-429-all", mode="cusum")
        state_before = breaker.state
        breaker.record_429(retry_after=retry_after, response_body=body)
        assert breaker.state == state_before
