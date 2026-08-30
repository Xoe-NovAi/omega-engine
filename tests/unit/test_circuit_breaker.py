# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for EmbeddingCircuitBreaker — fail-fast + fallback chain.

AP: AP-CIRCUIT-BREAKER-EMBED-v1.0.0
"""
from typing import List

import pytest
import pytest_asyncio

from src.omega.memory.embedding_circuit_breaker import (
    EmbeddingCircuitBreaker,
    _AsyncBreaker,
    FAILURE_THRESHOLD,
)
from src.omega.memory.embeddings import IEmbeddingProvider


class MockProvider(IEmbeddingProvider):
    """Minimal IEmbeddingProvider stand-in for testing."""

    def __init__(self, name: str, fail_n: int = 0, dim: int = 768):
        self.name = name
        self.fail_n = fail_n
        self._dim = dim
        self.call_count = 0

    async def get_embedding(self, text: str) -> List[float]:
        self.call_count += 1
        if self.call_count <= self.fail_n:
            raise RuntimeError(f"simulated failure #{self.call_count}")
        return [0.0] * self._dim

    @property
    def dimension(self) -> int:
        return self._dim


@pytest.mark.asyncio
async def test_healthy_provider_succeeds():
    p = MockProvider("ok", fail_n=0)
    cb = EmbeddingCircuitBreaker([p])
    vec = await cb.embed("test")
    assert len(vec) == 768
    assert p.call_count == 1


@pytest.mark.asyncio
async def test_falls_through_to_second_provider():
    """When p1 fails in this embed() call, p2 is tried and succeeds.

    The breaker opens after threshold failures across multiple embed()
    calls, not within a single one. So this test verifies the
    fail-fast-within-call semantics; the cross-call behavior is covered
    by test_breaker_opens_after_threshold.
    """
    p1 = MockProvider("broken", fail_n=99)
    p2 = MockProvider("ok", fail_n=0)
    cb = EmbeddingCircuitBreaker([p1, p2])
    vec = await cb.embed("test")
    assert len(vec) == 768
    # p1 was tried at least once (failed)
    assert p1.call_count == 1
    # p2 was tried at least once (succeeded)
    assert p2.call_count == 1
    # p1's breaker has 1 failure recorded
    p1_breaker = cb._breakers[p1]
    assert p1_breaker.health.fail_count == 1

    # After 3 more embed() calls (all failing p1), breaker should open.
    for _ in range(FAILURE_THRESHOLD - 1):
        await cb.embed("x")
    p1_breaker = cb._breakers[p1]
    assert p1_breaker.health.state == "open"
    # p1 should NOT be called again now (fail-fast)
    call_count_before = p1.call_count
    await cb.embed("y")
    assert p1.call_count == call_count_before  # skipped, breaker open
    # p2 should be tried as fallback
    assert p2.call_count > 1


@pytest.mark.asyncio
async def test_sovereign_fallback_on_total_failure():
    """When all providers fail, EmbeddingCircuitBreaker must return a vector
    (sovereign hash fallback) — M23: never raise."""
    p1 = MockProvider("broken1", fail_n=99)
    p2 = MockProvider("broken2", fail_n=99)
    cb = EmbeddingCircuitBreaker([p1, p2])
    vec = await cb.embed("test")
    assert len(vec) > 0  # sovereign returns a non-empty hash-based vector
    assert p1.call_count >= 1
    assert p2.call_count >= 1


@pytest.mark.asyncio
async def test_breaker_opens_after_threshold():
    breaker = _AsyncBreaker("test", threshold=3, cooldown=30)
    assert breaker.can_request() is True
    breaker.record_failure()
    breaker.record_failure()
    breaker.record_failure()
    # After threshold, either state is "open" (manual fallback) OR
    # can_request returns False (pybreaker). Check can_request.
    # We don't assert health.state because it depends on pybreaker
    # being installed.
    assert breaker.can_request() is False or breaker.health.state == "open"


@pytest.mark.asyncio
async def test_health_report_exposes_state():
    p = MockProvider("ok", fail_n=0)
    cb = EmbeddingCircuitBreaker([p])
    await cb.embed("test")
    report = cb.health_report()
    assert len(report) == 1
    assert report[0]["provider"] == "MockProvider"
    assert report[0]["ok"] == 1


@pytest.mark.asyncio
async def test_reset_all_force_closes_breakers():
    p = MockProvider("always_fail", fail_n=99)
    cb = EmbeddingCircuitBreaker([p])
    # Trigger failures to open the breaker
    for _ in range(FAILURE_THRESHOLD):
        await cb.embed("x")
    # Reset
    cb.reset_all()
    report = cb.health_report()
    for entry in report:
        assert entry["state"] == "closed"
        assert entry["fail"] == 0
