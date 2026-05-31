"""Tests for HealthMonitor — provider health & circuit breaking.

AP: AP-HEALTH-MONITOR-TESTS-v1.0.0
Covers: Circuit breaker states, latency tracking, quota management, success rates.
"""

import anyio
import pytest

from omega.oracle.health_monitor import (
    AsyncCircuitBreaker,
    CircuitOpenError,
    CircuitState,
    HealthMonitor,
    ProviderStatus,
    QuotaStatus,
)


class TestCircuitBreaker:
    """Test AsyncCircuitBreaker state machine."""

    @pytest.mark.anyio
    async def test_starts_closed(self):
        cb = AsyncCircuitBreaker(name="test")
        assert cb.state == CircuitState.CLOSED
        assert cb.is_available is True

    @pytest.mark.anyio
    async def test_opens_after_threshold(self):
        cb = AsyncCircuitBreaker(name="test", failure_threshold=3)
        for _ in range(3):
            try:
                await cb.call(lambda: (_ for _ in ()).throw(ConnectionError("fail")))
            except ConnectionError:
                pass
        assert cb.state == CircuitState.OPEN
        assert cb.is_available is False

    @pytest.mark.anyio
    async def test_raises_when_open(self):
        cb = AsyncCircuitBreaker(name="test", failure_threshold=1)
        try:
            await cb.call(lambda: (_ for _ in ()).throw(ConnectionError("fail")))
        except ConnectionError:
            pass
        assert cb.state == CircuitState.OPEN
        with pytest.raises(CircuitOpenError):
            await cb.call(lambda: "success")

    @pytest.mark.anyio
    async def test_half_open_after_recovery(self):
        cb = AsyncCircuitBreaker(
            name="test",
            failure_threshold=1,
            recovery_timeout=0.05,  # 50ms for fast tests
        )
        try:
            await cb.call(lambda: (_ for _ in ()).throw(ConnectionError("fail")))
        except ConnectionError:
            pass
        assert cb.state == CircuitState.OPEN

        # Wait for recovery
        await anyio.sleep(0.06)

        # Next call should transition to half-open
        result = await cb.call(lambda: "ok")
        assert result == "ok"
        assert cb.state == CircuitState.CLOSED

    @pytest.mark.anyio
    async def test_reopens_on_half_open_failure(self):
        cb = AsyncCircuitBreaker(
            name="test",
            failure_threshold=1,
            recovery_timeout=0.05,
        )
        try:
            await cb.call(lambda: (_ for _ in ()).throw(ConnectionError("fail")))
        except ConnectionError:
            pass
        await anyio.sleep(0.06)

        # Failure in half-open should reopen
        try:
            await cb.call(lambda: (_ for _ in ()).throw(ConnectionError("fail2")))
        except ConnectionError:
            pass
        assert cb.state == CircuitState.OPEN

    @pytest.mark.anyio
    async def test_success_resets_failure_count(self):
        cb = AsyncCircuitBreaker(name="test", failure_threshold=3)
        # 2 failures with network errors
        for _ in range(2):
            try:
                await cb.call(lambda: (_ for _ in ()).throw(ConnectionError("connection refused")))
            except ConnectionError:
                pass
        assert cb.failure_count == 2

        # 1 success resets
        result = await cb.call(lambda: "ok")
        assert result == "ok"
        assert cb.failure_count == 0

    @pytest.mark.anyio
    async def test_non_circuit_breaking_error_does_not_trip(self):
        cb = AsyncCircuitBreaker(name="test", failure_threshold=1)
        # 400-style error should not trip circuit
        for _ in range(5):
            try:
                await cb.call(lambda: (_ for _ in ()).throw(ValueError("bad request")))
            except ValueError:
                pass
        # Circuit should still be closed (ValueError doesn't match circuit-breaking keywords)
        # Actually ValueError doesn't contain any circuit-breaking keywords, so it won't trip
        assert cb.state == CircuitState.CLOSED


class TestLatencyTracking:
    """Test per-model latency sliding window."""

    def test_record_and_get_p99(self):
        hm = HealthMonitor()
        for i in range(100):
            hm.record_latency("gemma-4-31b", 100 + i)
        p99 = hm.get_latency_p99("gemma-4-31b")
        assert p99 >= 190  # p99 of 100-199 range

    def test_default_when_no_data(self):
        hm = HealthMonitor()
        assert hm.get_latency_p99("unknown") == 1000

    def test_sliding_window_bounded(self):
        hm = HealthMonitor(latency_window_size=10)
        for i in range(50):
            hm.record_latency("test", float(i))
        assert len(hm._latency_windows["test"]) == 10

    def test_latency_snapshot(self):
        hm = HealthMonitor()
        for i in range(100):
            hm.record_latency("test", float(i))
        snap = hm.get_latency_snapshot("test")
        assert snap.count == 100
        assert snap.min_ms == 0.0
        assert snap.max_ms == 99.0
        assert snap.p50_ms >= 45.0


class TestSuccessRate:
    """Test success/failure rate tracking."""

    def test_default_is_healthy(self):
        hm = HealthMonitor()
        assert hm.get_success_rate("unknown") == 1.0

    def test_all_success(self):
        hm = HealthMonitor()
        for _ in range(10):
            hm.record_success("model")
        assert hm.get_success_rate("model") == 1.0

    def test_mixed(self):
        hm = HealthMonitor()
        for _ in range(8):
            hm.record_success("model")
        for _ in range(2):
            hm.record_failure("model")
        assert hm.get_success_rate("model") == 0.8

    def test_all_failure(self):
        hm = HealthMonitor()
        for _ in range(10):
            hm.record_failure("model")
        assert hm.get_success_rate("model") == 0.0


class TestQuotaTracking:
    """Test per-provider quota management."""

    def test_default_unlimited(self):
        hm = HealthMonitor()
        assert hm.get_quota_usage("google") == 0.0

    def test_quota_usage(self):
        hm = HealthMonitor()
        hm._quotas["google"] = QuotaStatus(daily_limit=1000)
        hm.record_token_usage("google", 500)
        assert hm.get_quota_usage("google") == 0.5

    def test_quota_exhausted(self):
        hm = HealthMonitor()
        hm._quotas["google"] = QuotaStatus(daily_limit=100)
        hm.record_token_usage("google", 150)
        assert hm.get_quota_usage("google") == 1.0


class TestProviderStatus:
    """Test provider status reporting."""

    def test_healthy_by_default(self):
        hm = HealthMonitor(providers={"google": {}, "lmster": {}})
        assert hm.get_provider_status("google") == ProviderStatus.HEALTHY

    def test_unknown_provider_offline(self):
        hm = HealthMonitor()
        assert hm.get_provider_status("unknown") == ProviderStatus.OFFLINE

    def test_is_available_with_mapping(self):
        hm = HealthMonitor(providers={"google": {}})
        hm.set_model_provider("gemma-4-31b", "google")
        assert hm.is_available("gemma-4-31b") is True

    def test_is_available_without_mapping(self):
        hm = HealthMonitor()
        assert hm.is_available("unknown-model") is True  # Assume available


class TestStatusReport:
    """Test full status report generation."""

    def test_report_structure(self):
        hm = HealthMonitor(providers={"google": {}})
        hm.record_latency("gemma-4-31b", 150.0)
        hm.record_success("gemma-4-31b")

        report = hm.get_status_report()
        assert "providers" in report
        assert "models" in report
        assert "timestamp" in report
        assert "google" in report["providers"]
        assert "gemma-4-31b" in report["models"]
