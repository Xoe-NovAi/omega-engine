"""Tests for ProviderChain failover and aggregation."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest

from omega_vetala.providers.base import ModerationResult, ModelProvider
from omega_vetala.providers.chain import ProviderChain


class AlwaysPassProvider(ModelProvider):
    """Provider that always returns a clean result."""

    supports_offline = True

    async def analyze(self, text: str) -> ModerationResult:
        return ModerationResult(
            is_flagged=False,
            confidence=0.05,
            categories={"clean": 0.95},
            provider_name="always_pass",
        )


class AlwaysFlagProvider(ModelProvider):
    """Provider that always flags."""

    supports_offline = True

    async def analyze(self, text: str) -> ModerationResult:
        return ModerationResult(
            is_flagged=True,
            confidence=0.95,
            categories={"toxicity": 0.95},
            provider_name="always_flag",
        )


class FailingProvider(ModelProvider):
    """Provider that always raises an exception."""

    supports_offline = True

    async def analyze(self, text: str) -> ModerationResult:
        msg = "provider crashed"
        raise RuntimeError(msg)


class SlowProvider(ModelProvider):
    """Provider that never returns (simulates timeout)."""

    supports_offline = True

    def __init__(self, delay: float = 999.0) -> None:
        self._delay = delay

    async def analyze(self, text: str) -> ModerationResult:
        import anyio
        await anyio.sleep(self._delay)
        return ModerationResult(provider_name="slow")


class LowConfidenceProvider(ModelProvider):
    """Provider that returns below-confidence result."""

    supports_offline = True

    async def analyze(self, text: str) -> ModerationResult:
        return ModerationResult(
            is_flagged=False,
            confidence=0.05,
            categories={"irrelevant": 0.05},
            provider_name="low_conf",
        )


class TestProviderChain:
    """Provider chain failover and aggregation."""

    async def test_empty_text(self) -> None:
        """Empty text returns fast without calling providers."""
        p1 = AlwaysPassProvider()
        chain = ProviderChain([p1])
        result = await chain.analyze("")
        assert result.is_flagged is False
        assert result.provider_name == "provider_chain"

    async def test_single_provider(self) -> None:
        """Single provider result should pass through directly."""
        chain = ProviderChain([AlwaysFlagProvider()])
        result = await chain.analyze("bad text")
        assert result.is_flagged is True
        assert result.confidence >= 0.9

    async def test_failover_on_exception(self) -> None:
        """If first provider fails, second should be tried."""
        chain = ProviderChain([FailingProvider(), AlwaysPassProvider()])
        result = await chain.analyze("test")
        assert result.is_flagged is False
        # The chain should have succeeded via the second provider

    async def test_failover_on_low_confidence(self) -> None:
        """If first provider returns low confidence, fall through."""
        chain = ProviderChain(
            [LowConfidenceProvider(), AlwaysFlagProvider()],
            confidence_floor=0.1,
        )
        result = await chain.analyze("test")
        assert result.is_flagged is True  # Second provider flagged it

    async def test_all_providers_fail(self) -> None:
        """If all providers fail, return aggregated error."""
        chain = ProviderChain([FailingProvider(), FailingProvider()])
        result = await chain.analyze("test")
        assert result.is_flagged is False
        assert "__all_failed__" in result.categories

    async def test_aggregation_multiple_results(self) -> None:
        """Multiple results should be aggregated via weighted voting."""
        chain = ProviderChain(
            [AlwaysFlagProvider(), AlwaysPassProvider()],
            confidence_floor=0.0,  # Don't stop early
        )
        result = await chain.analyze("test")
        # At least one provider flagged it
        assert result.is_flagged is True
        # provider_name should be chain
        assert result.provider_name == "provider_chain"

    async def test_stop_on_high_confidence(self) -> None:
        """Chain should stop after first high-confidence result."""
        called: list[str] = []

        class TrackingProvider(ModelProvider):
            supports_offline = True

            def __init__(self, name: str, flagged: bool = False, conf: float = 0.9):
                self._name = name
                self._flagged = flagged
                self._conf = conf

            async def analyze(self, text: str) -> ModerationResult:
                called.append(self._name)
                return ModerationResult(
                    is_flagged=self._flagged,
                    confidence=self._conf,
                    provider_name=self._name,
                )

        chain = ProviderChain(
            [
                TrackingProvider("first", conf=0.8),
                TrackingProvider("second", conf=0.9),
                TrackingProvider("third", conf=0.9),
            ],
            confidence_floor=0.85,
        )
        result = await chain.analyze("test")
        assert "first" in called
        assert "second" in called
        assert "third" not in called  # Stopped after second

    async def test_supports_offline_mixed(self) -> None:
        """Chain supports_offline is True only if ALL providers support it."""
        online_provider = AlwaysFlagProvider()
        online_provider.supports_offline = False

        chain1 = ProviderChain([AlwaysPassProvider()])
        assert chain1.supports_offline is True

        chain2 = ProviderChain([online_provider])
        assert chain2.supports_offline is False

        chain3 = ProviderChain([AlwaysPassProvider(), online_provider])
        assert chain3.supports_offline is False

    async def test_timeout_provider(self) -> None:
        """A provider that times out should be skipped."""
        chain = ProviderChain(
            [SlowProvider(delay=50.0), AlwaysPassProvider()],
            timeout=0.1,  # Very short timeout
        )
        result = await chain.analyze("test")
        assert result.is_flagged is False
        # Should have fallen through to AlwaysPassProvider

    async def test_context_manager(self) -> None:
        """Chain context manager should propagate to all providers."""
        p1 = AlwaysPassProvider()
        p2 = AlwaysFlagProvider()
        chain = ProviderChain([p1, p2])
        async with chain:
            result = await chain.analyze("test")
            assert isinstance(result, ModerationResult)

    async def test_yaml_config_not_found(self) -> None:
        """from_yaml should raise on missing file."""
        with pytest.raises(FileNotFoundError):
            ProviderChain.from_yaml("/nonexistent/path.yaml")

    # ------------------------------------------------------------------
    # _aggregate unit tests
    # ------------------------------------------------------------------

    def test_aggregate_single(self) -> None:
        """Single result aggregation."""
        r = ModerationResult(is_flagged=True, confidence=0.9, categories={"a": 0.9})
        agg = ProviderChain._aggregate([r])
        assert agg.is_flagged is True
        assert agg.confidence == pytest.approx(0.9, rel=1e-3)

    def test_aggregate_multiple(self) -> None:
        """Multi-result aggregation with weighted voting."""
        r1 = ModerationResult(
            is_flagged=True, confidence=0.9, categories={"toxicity": 0.9}
        )
        r2 = ModerationResult(
            is_flagged=False, confidence=0.1, categories={"clean": 0.9}
        )
        agg = ProviderChain._aggregate([r1, r2])
        # r1 gets weight 1.0, r2 gets 0.5
        assert agg.is_flagged is True  # at least one flagged
        assert agg.confidence > 0.5  # weighted average

    def test_aggregate_categories_normalised(self) -> None:
        """Categories should be weight-normalised."""
        r1 = ModerationResult(is_flagged=False, confidence=0.0, categories={"a": 1.0})
        r2 = ModerationResult(is_flagged=False, confidence=0.0, categories={"b": 1.0})
        agg = ProviderChain._aggregate([r1, r2])
        assert "a" in agg.categories
        assert "b" in agg.categories
        # Both should be < 1.0 due to normalisation
        assert agg.categories["a"] < 1.0
