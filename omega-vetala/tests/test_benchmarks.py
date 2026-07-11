"""Performance benchmarks for the moderation system.

Uses deterministic mock providers to measure throughput, latency
percentiles, memory stability, and timeout behaviour.

⚠️  These are functional benchmarks — they verify performance
    characteristics under controlled conditions.  Results are
    environment-dependent (CPU speed, memory pressure, etc.).

All benchmarks use mock providers — NO API keys or ML models needed.
"""

from __future__ import annotations

import gc
import math
import time
from typing import Any

import pytest

from omega_vetala.providers.base import ModerationResult, ModelProvider
from omega_vetala.providers.chain import ProviderChain

from tests.conftest import (
    AlwaysFlagMockProvider,
    AlwaysPassMockProvider,
    FailingMockProvider,
    SlowMockProvider,
)


# ---------------------------------------------------------------------------
# Helper: a mock provider with configurable latency
# ---------------------------------------------------------------------------


class LatencySimProvider(ModelProvider):
    """Mock provider that simulates configurable processing delay."""

    supports_offline = True

    def __init__(self, latency_ms: float = 10.0, name: str = "latency_sim") -> None:
        self._latency_ms = latency_ms
        self._name = name

    async def analyze(self, text: str) -> ModerationResult:
        import anyio
        await anyio.sleep(self._latency_ms / 1000.0)
        return ModerationResult(
            is_flagged=False,
            confidence=0.1,
            provider_name=self._name,
            latency_ms=self._latency_ms,
        )


# ---------------------------------------------------------------------------
# Latency percentiles helper
# ---------------------------------------------------------------------------


def _compute_percentiles(
    latencies: list[float],
) -> dict[str, float]:
    """Compute P50, P95, P99 from a sorted list of latencies.

    Args:
        latencies: List of latency values in ms.

    Returns:
        Dict with p50, p95, p99 keys.
    """
    sorted_lats = sorted(latencies)
    n = len(sorted_lats)
    if n == 0:
        return {"p50": 0.0, "p95": 0.0, "p99": 0.0}

    def percentile(p: int) -> float:
        idx = max(0, min(n - 1, int(math.ceil(p / 100.0 * n) - 1)))
        return sorted_lats[idx]

    return {
        "p50": percentile(50),
        "p95": percentile(95),
        "p99": percentile(99),
    }


# ═══════════════════════════════════════════════════════════════════════
# Benchmark tests
# ═══════════════════════════════════════════════════════════════════════


class TestThroughput:
    """Requests per second measurement."""

    @pytest.mark.benchmark
    @pytest.mark.anyio
    async def test_mock_provider_throughput(self) -> None:
        """Measure requests per second for mock provider."""
        provider = AlwaysPassMockProvider(latency_ms=1.0)
        iterations = 100
        start = time.monotonic()

        for _ in range(iterations):
            result = await provider.analyze("benchmark test text")
            assert isinstance(result, ModerationResult)

        elapsed = time.monotonic() - start
        rps = iterations / elapsed if elapsed > 0 else float("inf")
        print(f"\n  Mock provider throughput: {rps:.1f} req/s ({elapsed:.2f}s for {iterations})")
        # Should comfortably exceed 10 req/s even on slow hardware
        assert rps > 10, f"Throughput too low: {rps:.1f} req/s"

    @pytest.mark.benchmark
    @pytest.mark.anyio
    async def test_chain_throughput(self) -> None:
        """Measure requests per second for a 2-provider chain."""
        chain = ProviderChain([
            AlwaysPassMockProvider(latency_ms=1.0),
            AlwaysFlagMockProvider(latency_ms=1.0),
        ])
        iterations = 50
        start = time.monotonic()

        for _ in range(iterations):
            result = await chain.analyze("benchmark chain test")
            assert isinstance(result, ModerationResult)

        elapsed = time.monotonic() - start
        rps = iterations / elapsed if elapsed > 0 else float("inf")
        print(f"\n  Chain throughput: {rps:.1f} req/s ({elapsed:.2f}s for {iterations})")
        assert rps > 5, f"Chain throughput too low: {rps:.1f} req/s"


class TestLatencyPercentiles:
    """P50, P95, P99 latency for provider chain."""

    @pytest.mark.benchmark
    @pytest.mark.anyio
    async def test_chain_latency_percentiles(self) -> None:
        """Measure latency percentiles for chain with mock providers."""
        chain = ProviderChain([
            LatencySimProvider(latency_ms=5.0, name="fast"),
            LatencySimProvider(latency_ms=15.0, name="slow"),
        ])
        iterations = 30
        latencies: list[float] = []

        for _ in range(iterations):
            result = await chain.analyze("latency test")
            latencies.append(result.latency_ms)

        percentiles = _compute_percentiles(latencies)
        print(f"\n  Chain latency percentiles (ms): P50={percentiles['p50']:.1f}, "
              f"P95={percentiles['p95']:.1f}, P99={percentiles['p99']:.1f}")

        # Fast provider returns immediately, so latency should be low
        assert percentiles["p50"] < 100, f"P50 latency too high: {percentiles['p50']:.1f}ms"

    @pytest.mark.benchmark
    @pytest.mark.anyio
    async def test_chain_aggregation_overhead(self) -> None:
        """Measure overhead of chain aggregation vs single provider."""
        single_provider = LatencySimProvider(latency_ms=5.0, name="single")
        chain = ProviderChain([
            LatencySimProvider(latency_ms=5.0, name="first"),
            LatencySimProvider(latency_ms=5.0, name="second"),
        ])
        iterations = 20

        # Single provider
        start = time.monotonic()
        for _ in range(iterations):
            await single_provider.analyze("overhead test")
        single_time = time.monotonic() - start

        # Chain (stops at first provider)
        start = time.monotonic()
        for _ in range(iterations):
            await chain.analyze("overhead test")
        chain_time = time.monotonic() - start

        print(f"\n  Single: {single_time:.3f}s, Chain: {chain_time:.3f}s "
              f"for {iterations} iterations")
        # Chain should not be significantly slower than single
        # (both stop at the first provider)
        overhead_ratio = chain_time / single_time if single_time > 0 else 0
        assert overhead_ratio < 5.0, (
            f"Chain overhead ratio too high: {overhead_ratio:.1f}x"
        )


class TestMemoryUsage:
    """Memory leak detection and tracking."""

    @pytest.mark.benchmark
    @pytest.mark.anyio
    async def test_no_memory_leak_over_1000_iterations(self) -> None:
        """Memory should not grow significantly over 1000 iterations."""
        import tracemalloc

        tracemalloc.start()
        gc.collect()

        # Take baseline
        baseline = tracemalloc.get_traced_memory()

        provider = AlwaysPassMockProvider(latency_ms=0.1)

        for i in range(1000):
            result = await provider.analyze(f"iteration {i} test text")
            assert isinstance(result, ModerationResult)

        gc.collect()
        current = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Current memory should not exceed baseline by more than 500KB
        # (tracemalloc overhead + natural Python object churn)
        memory_growth = current[0] - baseline[0]
        print(f"\n  Memory growth over 1000 iterations: {memory_growth / 1024:.1f} KB")
        assert memory_growth < 500 * 1024, (
            f"Potential memory leak: {memory_growth / 1024:.1f} KB growth"
        )

    @pytest.mark.benchmark
    @pytest.mark.anyio
    async def test_chain_no_memory_leak(self) -> None:
        """Provider chain should not leak memory over repeated calls."""
        import tracemalloc

        chain = ProviderChain([
            AlwaysPassMockProvider(latency_ms=0.1),
            AlwaysFlagMockProvider(latency_ms=0.1),
        ])

        tracemalloc.start()
        gc.collect()
        baseline = tracemalloc.get_traced_memory()

        for i in range(500):
            result = await chain.analyze(f"chain iteration {i}")
            assert isinstance(result, ModerationResult)

        gc.collect()
        current = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        memory_growth = current[0] - baseline[0]
        print(f"\n  Chain memory growth over 500 iterations: {memory_growth / 1024:.1f} KB")
        assert memory_growth < 500 * 1024, (
            f"Chain potential memory leak: {memory_growth / 1024:.1f} KB growth"
        )

    @pytest.mark.benchmark
    @pytest.mark.anyio
    async def test_moderation_result_not_leaking(self) -> None:
        """ModerationResult objects should be garbage collected."""
        import weakref

        provider = AlwaysFlagMockProvider(latency_ms=0.1)
        result = await provider.analyze("leak check")
        weak = weakref.ref(result)

        del result
        gc.collect()

        # The weak reference should be dead
        assert weak() is None, "ModerationResult leaked after deletion"


class TestProviderChainTimeout:
    """Timeout behaviour in provider chain."""

    @pytest.mark.benchmark
    @pytest.mark.anyio
    async def test_timeout_fires_correctly(self) -> None:
        """Chain timeout should fire within expected bounds."""
        chain = ProviderChain(
            [SlowMockProvider(delay=10.0), AlwaysPassMockProvider()],
            timeout=0.05,  # 50ms timeout
        )

        start = time.monotonic()
        result = await chain.analyze("timeout test")
        elapsed = time.monotonic() - start

        # Should fall through to AlwaysPassMockProvider quickly
        assert result.is_flagged is False
        # Should complete well before the slow provider's 10s delay
        assert elapsed < 5.0, f"Timeout didn't trigger fast enough: {elapsed:.2f}s"

    @pytest.mark.benchmark
    @pytest.mark.anyio
    async def test_all_providers_timeout(self) -> None:
        """When all providers time out, chain should return gracefully."""
        chain = ProviderChain(
            [SlowMockProvider(delay=10.0), SlowMockProvider(delay=10.0)],
            timeout=0.01,  # 10ms timeout
        )

        start = time.monotonic()
        result = await chain.analyze("all timeout")
        elapsed = time.monotonic() - start

        assert "__all_failed__" in result.categories
        assert elapsed < 5.0, f"All-timeout didn't complete fast enough: {elapsed:.2f}s"

    @pytest.mark.benchmark
    @pytest.mark.anyio
    async def test_timeout_not_triggered_when_provider_is_fast(self) -> None:
        """Timeout should not fire when provider is fast enough."""
        chain = ProviderChain(
            [AlwaysPassMockProvider(latency_ms=1.0)],
            timeout=30.0,  # Very generous timeout
        )

        start = time.monotonic()
        result = await chain.analyze("no timeout")
        elapsed = time.monotonic() - start

        assert result.is_flagged is False
        assert elapsed < 5.0, f"Fast provider took too long: {elapsed:.2f}s"


class TestProviderChainProductionLoad:
    """Simulated production load patterns."""

    @pytest.mark.benchmark
    @pytest.mark.anyio
    async def test_mixed_load_pattern(self) -> None:
        """Simulate mixed traffic pattern (mostly clean, some flagged)."""
        # Use content-based mock providers
        class ContentBasedProvider(ModelProvider):
            """Mock that flags only specific content."""

            supports_offline = True

            def __init__(self, latency_ms: float = 2.0) -> None:
                self._latency_ms = latency_ms

            async def analyze(self, text: str) -> ModerationResult:
                is_flagged = "flag" in text.lower()
                return ModerationResult(
                    is_flagged=is_flagged,
                    confidence=0.95 if is_flagged else 0.05,
                    categories={"toxicity": 0.95} if is_flagged else {"clean": 0.95},
                    provider_name="content_based",
                    latency_ms=self._latency_ms,
                )

        provider = ContentBasedProvider(latency_ms=2.0)
        chain = ProviderChain([provider], confidence_floor=0.1)

        # Simulate 80% clean, 20% flagged
        texts = ["clean text"] * 80 + ["flag this content"] * 20

        start = time.monotonic()
        results: list[ModerationResult] = []
        for text in texts:
            result = await chain.analyze(text)
            results.append(result)

        elapsed = time.monotonic() - start
        flagged_count = sum(1 for r in results if r.is_flagged)
        clean_count = sum(1 for r in results if not r.is_flagged)

        print(f"\n  Mixed load: {len(results)} requests in {elapsed:.2f}s "
              f"({len(results)/elapsed:.1f} req/s)")
        print(f"  Clean: {clean_count}, Flagged: {flagged_count}")

        assert clean_count >= 70, f"Expected ~80 clean, got {clean_count}"
        assert flagged_count >= 15, f"Expected ~20 flagged, got {flagged_count}"
