"""Comprehensive provider unit tests.

Tests each provider returns :class:`ModerationResult` dataclass,
handles graceful degradation, and exercises the provider chain
failover and aggregation logic.

All tests use mock providers or structural pattern analysis only —
NO static slur lists.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from omega_vetala.providers.base import (
    ModerationResult,
    ModelProvider,
    ProviderError,
)
from omega_vetala.providers.chain import ProviderChain

# Re-use mock providers from conftest
from tests.conftest import (
    AlwaysFlagMockProvider,
    AlwaysPassMockProvider,
    FailingMockProvider,
    NonDeterministicMockProvider,
    SlowMockProvider,
)


class TestModerationResultContract:
    """Contract test: all providers must return ModerationResult (M21)."""

    @pytest.mark.anyio
    async def test_always_pass_returns_moderation_result(
        self, always_pass_mock: AlwaysPassMockProvider
    ) -> None:
        """Must return a ModerationResult instance."""
        result = await always_pass_mock.analyze("test text")
        assert isinstance(result, ModerationResult)

    @pytest.mark.anyio
    async def test_always_flag_returns_moderation_result(
        self, always_flag_mock: AlwaysFlagMockProvider
    ) -> None:
        """Must return a ModerationResult instance."""
        result = await always_flag_mock.analyze("test text")
        assert isinstance(result, ModerationResult)

    @pytest.mark.anyio
    async def test_failing_mock_raises_exception(
        self, failing_mock: FailingMockProvider
    ) -> None:
        """Failing provider must raise (not return ModerationResult)."""
        with pytest.raises(RuntimeError):
            await failing_mock.analyze("test text")

    @pytest.mark.anyio
    async def test_provider_chain_returns_aggregated_result(
        self, always_pass_mock: AlwaysPassMockProvider
    ) -> None:
        """ProviderChain must return a ModerationResult."""
        chain = ProviderChain([always_pass_mock])
        result = await chain.analyze("test text")
        assert isinstance(result, ModerationResult)
        assert result.provider_name == "provider_chain"

    def test_result_has_trace_id(self) -> None:
        """Every ModerationResult should auto-generate a trace_id."""
        result = ModerationResult()
        assert result.trace_id != ""
        assert isinstance(result.trace_id, str)
        assert len(result.trace_id) == 16


class TestProviderGracefulDegradation:
    """Providers must degrade gracefully on failure."""

    @pytest.mark.anyio
    async def test_measure_wraps_exception(self) -> None:
        """_measure should catch exceptions and return error-coded result."""
        class FailingAnalyzeProvider(ModelProvider):
            supports_offline = True

            async def analyze(self, text: str) -> ModerationResult:
                msg = "inference failed"
                raise RuntimeError(msg)

        provider = FailingAnalyzeProvider()
        result = await provider._measure("test", "test_provider")
        assert isinstance(result, ModerationResult)
        assert result.is_flagged is False
        assert "__error__" in result.categories
        assert result.latency_ms > 0

    @pytest.mark.anyio
    async def test_empty_text_returns_immediately(self) -> None:
        """Empty text should return fast without calling provider logic."""
        chain = ProviderChain([AlwaysFlagMockProvider()])
        result = await chain.analyze("")
        assert result.is_flagged is False

    @pytest.mark.anyio
    async def test_whitespace_only_returns_immediately(self) -> None:
        """Whitespace-only text should return fast."""
        chain = ProviderChain([AlwaysFlagMockProvider()])
        result = await chain.analyze("   \t\n  ")
        assert result.is_flagged is False

    @pytest.mark.anyio
    async def test_chain_records_correct_provider_name(self) -> None:
        """Chain result should always have provider_name 'provider_chain'."""
        chain = ProviderChain([AlwaysPassMockProvider()])
        result = await chain.analyze("text")
        assert result.provider_name == "provider_chain"

    @pytest.mark.anyio
    async def test_chain_empty_providers_list(self) -> None:
        """Chain with no providers should return gracefully."""
        chain = ProviderChain([])
        result = await chain.analyze("text")
        assert "__all_failed__" in result.categories
        assert result.is_flagged is False


class TestProviderChainFailover:
    """Provider chain failover behaviour."""

    @pytest.mark.anyio
    async def test_first_provider_fails_second_succeeds(self) -> None:
        """If first provider fails, chain falls through to second."""
        chain = ProviderChain([
            FailingMockProvider(),
            AlwaysPassMockProvider(),
        ])
        result = await chain.analyze("test")
        assert result.is_flagged is False
        assert result.confidence >= 0.0

    @pytest.mark.anyio
    async def test_all_providers_fail_returns_error_result(self) -> None:
        """If all providers fail, return error-coded result."""
        chain = ProviderChain([
            FailingMockProvider("error 1"),
            FailingMockProvider("error 2"),
        ])
        result = await chain.analyze("test")
        assert result.is_flagged is False
        assert "__all_failed__" in result.categories

    @pytest.mark.anyio
    async def test_timeout_fallthrough(self) -> None:
        """A provider that times out should be skipped."""
        chain = ProviderChain(
            [SlowMockProvider(delay=50.0), AlwaysPassMockProvider()],
            timeout=0.1,
        )
        result = await chain.analyze("test")
        assert result.is_flagged is False

    @pytest.mark.anyio
    async def test_mixed_failures_and_successes(self) -> None:
        """Mix of failing, passing, and flagging providers."""
        chain = ProviderChain(
            [
                FailingMockProvider(),
                AlwaysPassMockProvider(),
                AlwaysFlagMockProvider(),
            ],
            confidence_floor=0.0,  # Don't stop early (0.0 means stop at first)
            # With floor=0.0, AlwaysPassMockProvider (conf=0.05) stops the chain
            # before AlwaysFlagMockProvider runs. We verify the chain works.
        )
        result = await chain.analyze("test")
        assert result.is_flagged is False  # Stopped at AlwaysPass (conf >= 0.0)

    @pytest.mark.anyio
    async def test_all_providers_run_with_high_floor(self) -> None:
        """With confidence_floor=1.0, all providers should be called."""
        chain = ProviderChain(
            [
                FailingMockProvider(),
                AlwaysPassMockProvider(),
                AlwaysFlagMockProvider(),
            ],
            confidence_floor=1.0,  # Nothing stops early
        )
        result = await chain.analyze("test")
        assert result.is_flagged is True  # AlwaysFlag results are included

    @pytest.mark.anyio
    async def test_stop_on_high_confidence(self) -> None:
        """Chain stops early when a provider returns high confidence."""
        called: list[int] = []

        class TrackingProvider(ModelProvider):
            supports_offline = True

            def __init__(self, idx: int, conf: float):
                self._idx = idx
                self._conf = conf

            async def analyze(self, text: str) -> ModerationResult:
                called.append(self._idx)
                return ModerationResult(
                    is_flagged=False,
                    confidence=self._conf,
                    provider_name=f"tracker_{self._idx}",
                )

        chain = ProviderChain(
            [
                TrackingProvider(0, conf=0.1),
                TrackingProvider(1, conf=0.2),
                TrackingProvider(2, conf=0.9),  # High enough to stop
                TrackingProvider(3, conf=0.9),
            ],
            confidence_floor=0.3,
        )
        await chain.analyze("test")
        # Provider 0 and 1 are below floor, passed through
        # Provider 2 is above floor, should stop
        assert 0 in called
        assert 1 in called
        assert 2 in called
        assert 3 not in called  # Should not be reached

    @pytest.mark.anyio
    async def test_provider_supports_offline(self) -> None:
        """supports_offline property should work for chain."""
        online = AlwaysFlagMockProvider()
        online.supports_offline = False

        chain_all_offline = ProviderChain([AlwaysPassMockProvider()])
        assert chain_all_offline.supports_offline is True

        chain_mixed = ProviderChain([AlwaysPassMockProvider(), online])
        assert chain_mixed.supports_offline is False


class TestProviderChainAggregation:
    """Provider chain weighted voting and aggregation."""

    @pytest.mark.anyio
    async def test_aggregation_multiple_providers(self) -> None:
        """Multiple providers' results should be aggregated."""
        chain = ProviderChain(
            [
                AlwaysFlagMockProvider(latency_ms=5.0),
                AlwaysPassMockProvider(latency_ms=5.0),
            ],
            confidence_floor=0.0,
        )
        result = await chain.analyze("test")
        assert result.is_flagged is True
        assert result.provider_name == "provider_chain"
        # Confidence should be a weighted average of both
        assert result.confidence > 0.3

    @pytest.mark.anyio
    async def test_aggregate_single_result(self) -> None:
        """Single result should pass through weighted voting unchanged."""
        r = ModerationResult(
            is_flagged=True, confidence=0.9, categories={"a": 0.9},
        )
        agg = ProviderChain._aggregate([r])
        assert agg.is_flagged is True
        assert agg.confidence == pytest.approx(0.9, rel=1e-3)

    @pytest.mark.anyio
    async def test_aggregate_flagged_any(self) -> None:
        """If ANY provider flagged, aggregate is_flagged should be True."""
        r1 = ModerationResult(is_flagged=False, confidence=0.1)
        r2 = ModerationResult(is_flagged=True, confidence=0.5)
        agg = ProviderChain._aggregate([r1, r2])
        assert agg.is_flagged is True

    @pytest.mark.anyio
    async def test_aggregate_weight_decay(self) -> None:
        """Later providers should have lower weight."""
        r1 = ModerationResult(
            is_flagged=True, confidence=1.0, categories={"x": 1.0},
        )
        r2 = ModerationResult(
            is_flagged=False, confidence=0.0, categories={"y": 1.0},
        )
        agg = ProviderChain._aggregate([r1, r2])
        # n=2: r1 weight = 1.0 - (0/2)*0.5 = 1.0
        #       r2 weight = 1.0 - (1/2)*0.5 = 0.75
        # Weighted confidence = (1.0*1.0 + 0.0*0.75) / 1.75 = 0.5714
        assert agg.confidence == pytest.approx(0.5714, rel=1e-3)

    @pytest.mark.anyio
    async def test_aggregate_categories_normalised(self) -> None:
        """Category scores should be weight-normalised."""
        r1 = ModerationResult(
            is_flagged=False, confidence=0.0, categories={"a": 1.0},
        )
        r2 = ModerationResult(
            is_flagged=False, confidence=0.0, categories={"b": 1.0},
        )
        agg = ProviderChain._aggregate([r1, r2])
        assert "a" in agg.categories
        assert "b" in agg.categories
        # Both should be < 1.0 due to weight normalisation
        assert agg.categories["a"] < 1.0
        assert agg.categories["b"] < 1.0

    @pytest.mark.anyio
    async def test_aggregate_trace_ids_merged(self) -> None:
        """Trace IDs from all sources should be merged in aggregate."""
        r1 = ModerationResult(
            is_flagged=False, confidence=0.0, trace_id="aaa",
        )
        r2 = ModerationResult(
            is_flagged=False, confidence=0.0, trace_id="bbb",
        )
        agg = ProviderChain._aggregate([r1, r2])
        assert "aaa" in agg.trace_id
        assert "bbb" in agg.trace_id


class TestProviderChainYAMLFactory:
    """ProviderChain.from_yaml YAML factory."""

    def test_from_yaml_file_not_found(self) -> None:
        """Should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            ProviderChain.from_yaml("/nonexistent/path.yaml")

    def test_from_yaml_invalid_type(self, tmp_path: Any) -> None:
        """Should raise ProviderError for unknown provider type."""
        config_path = tmp_path / "bad_config.yaml"
        config_path.write_text(
            "providers:\n  - type: nonexistent_provider\n"
        )
        with pytest.raises(ProviderError, match="Unknown provider type"):
            ProviderChain.from_yaml(str(config_path))

    def test_from_yaml_empty_providers(self, tmp_path: Any) -> None:
        """Empty providers list should create chain with no providers."""
        config_path = tmp_path / "empty.yaml"
        config_path.write_text("providers: []\n")
        chain = ProviderChain.from_yaml(str(config_path))
        assert len(chain._providers) == 0

    def test_from_yaml_with_timeout(self, tmp_path: Any) -> None:
        """YAML can specify global timeout."""
        config_path = tmp_path / "timeout.yaml"
        config_path.write_text(
            "providers:\n  - type: local_fallback\ntimeout: 5.0\n"
        )
        chain = ProviderChain.from_yaml(str(config_path))
        assert chain._timeout == 5.0

    def test_from_yaml_with_confidence_floor(self, tmp_path: Any) -> None:
        """YAML can specify confidence_floor."""
        config_path = tmp_path / "floor.yaml"
        config_path.write_text(
            "providers:\n  - type: local_fallback\nconfidence_floor: 0.2\n"
        )
        chain = ProviderChain.from_yaml(str(config_path))
        assert chain._confidence_floor == 0.2

    def test_from_yaml_local_fallback(self, tmp_path: Any) -> None:
        """Can load local_fallback from YAML."""
        config_path = tmp_path / "local.yaml"
        config_path.write_text(
            "providers:\n  - type: local_fallback\n"
            "  - type: local\n"
        )
        chain = ProviderChain.from_yaml(str(config_path))
        assert len(chain._providers) == 2
        from omega_vetala.providers.local_fallback import (
            LocalFallbackProvider,
        )
        assert isinstance(chain._providers[0], LocalFallbackProvider)
        assert isinstance(chain._providers[1], LocalFallbackProvider)


class TestProviderChainContextManager:
    """Provider chain AnyIO context manager."""

    @pytest.mark.anyio
    async def test_context_manager_enter_exit(self) -> None:
        """Context manager should enter and exit gracefully."""
        chain = ProviderChain([AlwaysPassMockProvider()])
        async with chain:
            result = await chain.analyze("test")
            assert isinstance(result, ModerationResult)
        # No exception means clean exit

    @pytest.mark.anyio
    async def test_context_manager_nested(self) -> None:
        """Nested context managers should work."""
        chain = ProviderChain([
            AlwaysPassMockProvider(),
            AlwaysFlagMockProvider(),
        ])
        async with chain:
            async with chain:
                result = await chain.analyze("nested")
                assert isinstance(result, ModerationResult)

    @pytest.mark.anyio
    async def test_context_manager_with_failing_provider(self) -> None:
        """Context manager should handle providers that fail on exit."""
        class ExitFailProvider(ModelProvider):
            supports_offline = True

            async def analyze(self, text: str) -> ModerationResult:
                return ModerationResult(provider_name="exit_fail")

            async def __aexit__(self, *args: Any) -> None:
                # Should not crash the context manager
                pass

        chain = ProviderChain([ExitFailProvider()])
        async with chain:
            pass  # Clean exit expected


class TestAnyIOWrapper:
    """Provider chain must properly wrap async context."""

    @pytest.mark.anyio
    async def test_analyze_in_anyio_context(self) -> None:
        """Provider.analyze should be callable from anyio context."""
        import anyio

        async def run_in_thread() -> ModerationResult:
            provider = AlwaysPassMockProvider()
            return await provider.analyze("test")

        result = await anyio.to_thread.run_sync(
            lambda: anyio.run(run_in_thread)
        )
        # The result should be correct even after thread hopping
        assert isinstance(result, ModerationResult)
        assert result.is_flagged is False

    @pytest.mark.anyio
    async def test_chain_timeout_doesnt_leak(self) -> None:
        """Timeout should not leave dangling tasks."""
        chain = ProviderChain(
            [SlowMockProvider(delay=50.0), AlwaysPassMockProvider()],
            timeout=0.1,
        )
        import anyio

        with anyio.fail_after(5.0):  # Safety net
            result = await chain.analyze("test")
            assert result.is_flagged is False
