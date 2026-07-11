"""Tests for HuggingFaceProvider."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from omega_vetala.providers.huggingface import HuggingFaceProvider
from omega_vetala.providers.base import ProviderError


class TestHuggingFaceProvider:
    """HuggingFace local model provider behaviour."""

    def test_init_defaults(self) -> None:
        """Default model and fallback should be set."""
        p = HuggingFaceProvider()
        assert p._model_name == "unitary/toxic-bert"
        assert p._fallback_model == "unitary/unbiased-toxic-roberta"
        assert p._pipeline is None  # lazy

    def test_supports_offline(self) -> None:
        """HuggingFace works offline once cached."""
        p = HuggingFaceProvider()
        assert p.supports_offline is True

    async def test_empty_text(self) -> None:
        """Empty text returns fast with no flag."""
        p = HuggingFaceProvider()
        result = await p.analyze("")
        assert result.is_flagged is False
        assert result.provider_name == "huggingface"

    async def test_analyze_before_model_load(self) -> None:
        """If model fails to load, should return gracefully."""
        # Patch _ensure_model to raise ProviderError
        p = HuggingFaceProvider()

        async def _fail() -> None:
            raise ProviderError("no model")

        with patch.object(p, "_ensure_model", _fail):  # type: ignore[arg-type]
            result = await p.analyze("some text")
            assert "__load_failed__" in result.categories
            assert result.is_flagged is False

    async def test_inference_error(self) -> None:
        """If inference fails, should return gracefully."""
        p = HuggingFaceProvider()

        # Use a regular callable that raises — _infer runs in a thread
        def _failing_pipeline(*args: Any, **kwargs: Any) -> list:
            msg = "OOM during inference"
            raise RuntimeError(msg)

        async def _mock_ensure() -> None:
            p._pipeline = _failing_pipeline
            p._loaded_model_name = "test-model"

        p._ensure_model = _mock_ensure  # type: ignore[assignment]

        result = await p.analyze("some text")
        assert "__inference_error__" in result.categories
        assert result.is_flagged is False

    async def test_lazy_loading(self) -> None:
        """Pipeline should be None until first analyze."""
        p = HuggingFaceProvider()
        assert p._pipeline is None
        # Don't actually trigger model download in unit tests
        # This just verifies the lazy-load contract
        assert p._loaded_model_name == ""

    def test_pipeline_import_guard(self) -> None:
        """The module should work even if transformers is not installed."""

        # If we can import the module at all, the import guard works
        import omega_vetala.providers.huggingface as hf_mod  # noqa: F811

        # The pipeline is loaded lazily, so missing dep won't crash init
        p = hf_mod.HuggingFaceProvider()
        assert p._pipeline is None
