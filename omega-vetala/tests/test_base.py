"""Tests for base module: ModerationResult and ModelProvider."""

from __future__ import annotations

import pytest

from omega_vetala.providers.base import (
    ModerationResult,
    ModelProvider,
    ProviderError,
)


class TestModerationResult:
    """ModerationResult dataclass behaviour."""

    def test_default_values(self) -> None:
        """Defaults should produce a non-flagged result."""
        result = ModerationResult()
        assert result.is_flagged is False
        assert result.confidence == 0.0
        assert result.categories == {}
        assert result.provider_name == ""
        assert result.trace_id != ""  # auto-generated

    def test_auto_trace_id(self) -> None:
        """trace_id should be auto-generated when not provided."""
        result = ModerationResult()
        assert len(result.trace_id) == 16  # uuid hex[:16]

    def test_custom_trace_id_preserved(self) -> None:
        """Explicit trace_id should NOT be overwritten."""
        result = ModerationResult(trace_id="my-custom-id")
        assert result.trace_id == "my-custom-id"

    def test_flagged_result(self) -> None:
        """A flagged result with categories."""
        result = ModerationResult(
            is_flagged=True,
            confidence=0.95,
            categories={"toxicity": 0.95, "insult": 0.80},
            provider_name="test",
            latency_ms=42.0,
        )
        assert result.is_flagged is True
        assert result.confidence == 0.95
        assert result.categories["toxicity"] == 0.95
        assert result.provider_name == "test"
        assert result.latency_ms == 42.0

    def test_trace_id_is_string(self) -> None:
        """trace_id must always be a string."""
        result = ModerationResult()
        assert isinstance(result.trace_id, str)


class TestModelProvider:
    """Abstract base class contract."""

    def test_cannot_instantiate_abstract(self) -> None:
        """ModelProvider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ModelProvider()  # type: ignore[abstract]

    def test_concrete_provider(self) -> None:
        """A concrete subclass must implement analyze."""

        class GoodProvider(ModelProvider):
            async def analyze(self, text: str) -> ModerationResult:
                return ModerationResult(provider_name="good")

        provider = GoodProvider()
        assert provider.supports_offline is False  # default

    def test_context_manager(self) -> None:
        """Context manager should enter and exit cleanly."""

        class CtxProvider(ModelProvider):
            entered = False
            exited = False

            async def __aenter__(self) -> CtxProvider:
                self.entered = True
                return self

            async def __aexit__(self, *args: object) -> None:
                self.exited = True

            async def analyze(self, text: str) -> ModerationResult:
                return ModerationResult(provider_name="ctx")

        async def run() -> None:
            async with CtxProvider() as p:
                result = await p.analyze("test")
                assert result.provider_name == "ctx"
                assert p.entered is True
            assert p.exited is True

        import anyio
        anyio.run(run)

    def test_supports_offline_override(self) -> None:
        """Subclass can override supports_offline."""

        class OfflineProvider(ModelProvider):
            supports_offline = True

            async def analyze(self, text: str) -> ModerationResult:
                return ModerationResult(provider_name="offline")

        p = OfflineProvider()
        assert p.supports_offline is True


class TestProviderError:
    """ProviderError exception."""

    def test_is_exception(self) -> None:
        """ProviderError is a proper exception."""
        err = ProviderError("something broke")
        assert isinstance(err, Exception)
        assert str(err) == "something broke"

    def test_raise_and_catch(self) -> None:
        """ProviderError can be raised and caught."""
        with pytest.raises(ProviderError):
            raise ProviderError("fail")
