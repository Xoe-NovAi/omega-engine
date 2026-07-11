"""Tests for PerspectiveProvider."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import httpx
import pytest

from omega_vetala.providers.perspective import PerspectiveProvider


@pytest.fixture
def provider() -> PerspectiveProvider:
    """Provider with a dummy API key (not real)."""
    return PerspectiveProvider(api_key="test-key")


class TestPerspectiveProvider:
    """Perspective API provider behaviour."""

    def test_init_no_key_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should read PERSPECTIVE_API_KEY from env."""
        monkeypatch.setenv("PERSPECTIVE_API_KEY", "env-key")
        p = PerspectiveProvider()
        assert p._api_key == "env-key"

    def test_init_explicit_key(self) -> None:
        """Explicit key should override env."""
        p = PerspectiveProvider(api_key="explicit")
        assert p._api_key == "explicit"

    def test_supports_offline(self) -> None:
        """Perspective requires network."""
        p = PerspectiveProvider(api_key="x")
        assert p.supports_offline is False

    async def test_empty_text(self, provider: PerspectiveProvider) -> None:
        """Empty text should return fast with no flag."""
        result = await provider.analyze("")
        assert result.is_flagged is False
        assert result.provider_name == "perspective"

    async def test_whitespace_text(self, provider: PerspectiveProvider) -> None:
        """Whitespace-only text should return fast with no flag."""
        result = await provider.analyze("   ")
        assert result.is_flagged is False

    async def test_no_api_key(self) -> None:
        """Without API key, should return error category."""
        p = PerspectiveProvider(api_key="")
        result = await p.analyze("some text")
        assert "__no_key__" in result.categories

    async def test_timeout_handling(self, provider: PerspectiveProvider) -> None:
        """On timeout, should return gracefully with __timeout__ category."""

        def _slow(*args: Any, **kwargs: Any) -> httpx.Response:
            raise httpx.TimeoutException("timed out")

        async with provider:
            with patch.object(provider._client, "post", _slow):  # type: ignore[arg-type]
                result = await provider.analyze("test text")
                assert "__timeout__" in result.categories
                assert result.is_flagged is False

    async def test_http_error(self, provider: PerspectiveProvider) -> None:
        """On HTTP error, should return gracefully."""

        def _fail(*args: Any, **kwargs: Any) -> httpx.Response:
            resp = httpx.Response(429, request=httpx.Request("POST", "http://x"))
            raise httpx.HTTPStatusError("rate limit", request=resp.request, response=resp)

        async with provider:
            with patch.object(provider._client, "post", _fail):  # type: ignore[arg-type]
                result = await provider.analyze("test text")
                assert "__http_error__" in result.categories
                assert result.is_flagged is False

    def test_rate_limit(self, provider: PerspectiveProvider) -> None:
        """Rate-limit should enforce 1 QPS (test synchronously)."""
        import time

        t0 = time.monotonic()
        # simulate two rapid calls via _rate_limit
        async def run() -> None:
            await provider._rate_limit()
            await provider._rate_limit()

        import anyio
        anyio.run(run)

        elapsed = time.monotonic() - t0
        assert elapsed >= 1.0  # at least 1 second for two calls

    async def test_context_manager(self) -> None:
        """Provider should create and clean up HTTP client."""
        p = PerspectiveProvider(api_key="test")
        assert p._client is None
        async with p:
            assert p._client is not None
        assert p._client is None  # closed on exit
