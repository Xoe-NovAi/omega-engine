"""Tests for OpenAIModerationProvider."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import httpx
import pytest

from omega_vetala.providers.openai_moderation import (
    OpenAIModerationProvider,
)


@pytest.fixture
def provider() -> OpenAIModerationProvider:
    """Provider with a dummy API key."""
    return OpenAIModerationProvider(api_key="sk-test-key")


class TestOpenAIModerationProvider:
    """OpenAI Moderation API provider behaviour."""

    def test_init_no_key_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should read OPENAI_API_KEY from env."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-env-key")
        p = OpenAIModerationProvider()
        assert p._api_key == "sk-env-key"

    def test_supports_offline(self) -> None:
        """OpenAI Moderation requires network."""
        p = OpenAIModerationProvider(api_key="x")
        assert p.supports_offline is False

    async def test_empty_text(self, provider: OpenAIModerationProvider) -> None:
        """Empty text returns fast with no flag."""
        result = await provider.analyze("")
        assert result.is_flagged is False
        assert result.provider_name == "openai_moderation"

    async def test_no_api_key(self) -> None:
        """Without API key, returns error category."""
        p = OpenAIModerationProvider(api_key="")
        result = await p.analyze("some text")
        assert "__no_key__" in result.categories

    async def test_timeout_handling(self, provider: OpenAIModerationProvider) -> None:
        """On timeout, returns gracefully."""

        def _slow(*args: Any, **kwargs: Any) -> httpx.Response:
            raise httpx.TimeoutException("timed out")

        async with provider:
            with patch.object(provider._client, "post", _slow):  # type: ignore[arg-type]
                result = await provider.analyze("test")
                assert "__timeout__" in result.categories
                assert result.is_flagged is False

    async def test_http_error(self, provider: OpenAIModerationProvider) -> None:
        """On HTTP error, returns gracefully."""

        def _fail(*args: Any, **kwargs: Any) -> httpx.Response:
            resp = httpx.Response(401, request=httpx.Request("POST", "http://x"))
            raise httpx.HTTPStatusError(
                "auth fail", request=resp.request, response=resp
            )

        async with provider:
            with patch.object(provider._client, "post", _fail):  # type: ignore[arg-type]
                result = await provider.analyze("test")
                assert "__http_error__" in result.categories

    async def test_context_manager(self) -> None:
        """Provider should create and clean up HTTP client."""
        p = OpenAIModerationProvider(api_key="sk-test")
        assert p._client is None
        async with p:
            assert p._client is not None
            assert "Authorization" in p._client.headers
        assert p._client is None

    def test_category_mapping(self) -> None:
        """OpenAI category keys map to standard names."""
        from omega_vetala.providers.openai_moderation import _CATEGORY_MAP

        assert _CATEGORY_MAP["hate"] == "hate"
        assert _CATEGORY_MAP["self-harm"] == "self_harm"
        assert _CATEGORY_MAP["violence/graphic"] == "violence_graphic"
