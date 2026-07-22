"""Tests for 429 classification hardening (C-10.5 / hardening P0).

[HARDENING-2026-07-22] These tests verify the bug class where circuit breakers
conflate rate-limit 429s with quota-exhausted 429s.

References:
    - resilient-llm-router: 3-state model (rate-limit/quota/circuit)
    - SmarterRouter issue #7: 429 with 1-hour cooldown = quota
    - OmniRoute issue #1767: 429 with no headers = 1s retry
"""
import time
import pytest
import anyio
from omega.oracle.health_monitor import AsyncCircuitBreaker


@pytest.fixture
def breaker():
    return AsyncCircuitBreaker("test-429", failure_threshold=5, recovery_timeout=60.0)


class Test429Classification:
    """429 classification — rate-limit vs quota-exhausted."""

    def test_rate_limit_detection_retry_after_short(self, breaker):
        """Retry-After < 1 hour = rate-limit (transient)."""
        breaker.record_429(retry_after=30.0)
        assert breaker.is_429_blocked() is True
        assert breaker.quota_until is None
        assert breaker.rate_limit_until is not None

    def test_quota_detection_retry_after_long(self, breaker):
        """Retry-After >= 1 hour = quota-exhausted (period-based)."""
        breaker.record_429(retry_after=7200.0)  # 2 hours
        assert breaker.is_429_blocked() is True
        assert breaker.quota_until is not None
        assert breaker.rate_limit_until is None

    def test_quota_detection_body_keywords(self, breaker):
        """Body containing 'monthly quota' = quota-exhausted."""
        breaker.record_429(response_body="Error: monthly quota exceeded for this account")
        assert breaker.quota_until is not None
        assert breaker.rate_limit_until is None

    def test_quota_detection_out_of_credits(self, breaker):
        """Body containing 'out of credits' = quota-exhausted."""
        breaker.record_429(response_body="out of credits, please upgrade")
        assert breaker.quota_until is not None

    def test_rate_limit_detection_no_indicators(self, breaker):
        """No Retry-After, no quota keywords = rate-limit (default)."""
        breaker.record_429()
        assert breaker.rate_limit_until is not None
        assert breaker.quota_until is None

    def test_explicit_quota_override(self, breaker):
        """is_quota=True forces quota classification."""
        breaker.record_429(retry_after=10.0, is_quota=True)
        assert breaker.quota_until is not None
        assert breaker.rate_limit_until is None

    def test_explicit_rate_limit_override(self, breaker):
        """is_quota=False forces rate-limit classification."""
        breaker.record_429(retry_after=7200.0, is_quota=False)
        assert breaker.rate_limit_until is not None
        assert breaker.quota_until is None

    def test_429_blocked_returns_false_after_cooldown(self, breaker):
        """is_429_blocked() returns False after cooldown expires."""
        breaker.record_429(retry_after=0.1)  # 100ms cooldown
        assert breaker.is_429_blocked() is True
        time.sleep(0.15)
        assert breaker.is_429_blocked() is False

    def test_429_status_report(self, breaker):
        """get_429_status() returns correct structure."""
        breaker.record_429(retry_after=60.0)
        status = breaker.get_429_status()
        assert "rate_limit_until" in status
        assert "quota_until" in status
        assert "rate_limit_remaining" in status
        assert "quota_remaining" in status
        assert "is_blocked" in status
        assert status["is_blocked"] is True

    def test_quota_does_not_affect_rate_limit(self, breaker):
        """Quota and rate_limit are independent fields."""
        breaker.record_429(retry_after=7200.0)  # quota
        assert breaker.quota_until is not None
        assert breaker.rate_limit_until is None
        
        # A separate rate-limit call doesn't clear quota
        breaker2 = AsyncCircuitBreaker("test-429-b", failure_threshold=5)
        breaker2.record_429(retry_after=30.0)  # rate limit
        assert breaker2.rate_limit_until is not None
        assert breaker2.quota_until is None

    def test_429_classification_does_not_trip_circuit(self, breaker):
        """429 classification is independent of circuit breaker state."""
        breaker.record_429(retry_after=60.0)
        # Circuit should still be CLOSED (not affected by 429)
        from omega.oracle.health_monitor import CircuitState
        assert breaker.state == CircuitState.CLOSED
