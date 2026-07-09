# 🔱 Contract Tests — S3 OpenRouter Provider Hardening (B1/B2/B5/B6)
# AP: AP-REMOTE-PROVIDER-S3-TESTS-v1.0.0
# ⬡ OMEGA ⬡ JOHN_CARMACK ⬡ opencode ⬡ trc_S3_S4 ⬡ M21-CONTRACT-TESTS
#
# [M21 Gate Integrity] Every runtime change in S3 is exercised by a contract
# test validating the typed result / behavior. These tests use MagicMock to
# avoid real network calls (sovereign-local, no telemetry).

import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch

from omega.oracle.backends.remote_provider import (
    ProviderConfig,
    RemoteProvider,
    ProviderRateLimitError,
)
from omega.oracle.backends.openai_compat import OpenAICompatProvider


# ── B1: Timeout floor (30s → 120s) ────────────────────────────────────────
def test_b1_timeout_default_is_120s():
    """[S3 B1] ProviderConfig.timeout_seconds must default to 120.0."""
    cfg = ProviderConfig(name="test", priority=0)
    assert cfg.timeout_seconds == 120.0


# ── B2: httpx.HTTPError caught and retried ────────────────────────────────
@pytest.mark.asyncio
async def test_b2_httpx_error_triggers_retry_then_none():
    """[S3 B2] httpx.HTTPError must be caught by the retry loop.

    After max_retries attempts, generate() returns None (not raise).
    """
    cfg = ProviderConfig(name="test", priority=0, max_retries=2, timeout_seconds=1.0)
    provider = OpenAICompatProvider(cfg)

    # Force _send_request to always raise httpx.ConnectError
    async def _raise(*args, **kwargs):
        raise httpx.ConnectError("simulated connection failure")

    provider._send_request = _raise

    result = await provider.generate("model", "sys", "query")
    assert result is None
    assert provider.metrics.failed_requests == 2
    assert provider.metrics.consecutive_failures == 2


# ── B5: 8-account Active-Passive Sharding (D205) ──────────────────────────
@pytest.mark.asyncio
async def test_b5_key_rotation_on_429():
    """[S3 B5 / D205] On 429, rotate to next key in the pool."""
    cfg = ProviderConfig(
        name="openrouter",
        priority=0,
        api_keys=["key-0", "key-1", "key-2"],
        max_retries=1,
        timeout_seconds=1.0,
    )
    provider = OpenAICompatProvider(cfg)
    assert provider._active_key_index == 0

    # Simulate 429 via httpx.HTTPStatusError
    mock_response = MagicMock()
    mock_response.status_code = 429
    http_error = httpx.HTTPStatusError("rate limited", request=MagicMock(), response=mock_response)

    async def _raise_429(*args, **kwargs):
        raise http_error

    provider._send_request = _raise_429

    result = await provider.generate("model", "sys", "query")
    assert result is None
    # After first failure (429), index should rotate to 1
    assert provider._active_key_index == 1


@pytest.mark.asyncio
async def test_b5_no_rotation_with_single_key():
    """[S3 B5] Single-key config must NOT rotate (no failover target)."""
    cfg = ProviderConfig(
        name="openrouter",
        priority=0,
        api_keys=["only-key"],
        max_retries=2,
        timeout_seconds=1.0,
    )
    provider = OpenAICompatProvider(cfg)

    mock_response = MagicMock()
    mock_response.status_code = 429
    http_error = httpx.HTTPStatusError("rate limited", request=MagicMock(), response=mock_response)

    async def _raise_429(*args, **kwargs):
        raise http_error

    provider._send_request = _raise_429
    await provider.generate("model", "sys", "query")
    assert provider._active_key_index == 0  # unchanged


# ── B3: Streaming completion (happy path + mid-stream error) ─────────────
class _FakeStreamResponse:
    """Simulates httpx streaming response with SSE lines."""

    def __init__(self, sse_lines, raise_on_status=True):
        self._lines = sse_lines
        self._raise_on_status = raise_on_status

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    def raise_for_status(self):
        if self._raise_on_status:
            pass  # 200 OK

    async def aiter_lines(self):
        for line in self._lines:
            yield line


@pytest.mark.asyncio
async def test_b3_streaming_accumulates_content():
    """[S3 B3] _stream_completion accumulates SSE delta chunks into a string."""
    cfg = ProviderConfig(
        name="openrouter", priority=0, api_keys=["key-0"],
        base_url="https://openrouter.ai/api",
    )
    provider = OpenAICompatProvider(cfg)

    sse_lines = [
        'data: {"choices":[{"delta":{"content":"Hello"},"finish_reason":null}]}',
        'data: {"choices":[{"delta":{"content":" world"},"finish_reason":null}]}',
        "data: [DONE]",
    ]
    fake_resp = _FakeStreamResponse(sse_lines)

    class FakeClient:
        def stream(self, method, url, json=None, headers=None):
            return fake_resp

    provider._client = FakeClient()
    result = await provider._stream_completion(FakeClient(), "url", {}, {})
    assert result == "Hello world"


@pytest.mark.asyncio
async def test_b3_streaming_mid_stream_error_raises():
    """[S3 B3] finish_reason='error' mid-stream raises RuntimeError for retry."""
    cfg = ProviderConfig(
        name="openrouter", priority=0, api_keys=["key-0"],
        base_url="https://openrouter.ai/api",
    )
    provider = OpenAICompatProvider(cfg)

    sse_lines = [
        'data: {"choices":[{"delta":{"content":"Partial"},"finish_reason":null}]}',
        'data: {"choices":[{"delta":{},"finish_reason":"error"}]}',
    ]
    fake_resp = _FakeStreamResponse(sse_lines)

    class FakeClient:
        def stream(self, method, url, json=None, headers=None):
            return fake_resp

    with pytest.raises(RuntimeError, match="finish_reason"):
        await provider._stream_completion(FakeClient(), "url", {}, {})


# ── B4: Repetition Loop Detector (base class guard) ─────────────────────
# All tests use RemoteProvider._detect_repetition_loop since it now lives
# in the base class and is inherited by ALL provider subclasses.

def test_b4_short_content_no_error():
    """[S3 B4] Content < 60 chars must NOT trigger the loop detector."""
    RemoteProvider._detect_repetition_loop("short", "model")
    # No exception = pass


def test_b4_normal_content_no_error():
    """[S3 B4] Non-repetitive content must NOT trigger the loop detector."""
    content = "The quick brown fox jumps over the lazy dog. " * 5
    RemoteProvider._detect_repetition_loop(content, "model")
    # No exception = pass


def test_b4_repetitive_content_raises():
    """[S3 B4] 3+ identical 20-char tail windows must raise RuntimeError."""
    filler = "A" * 100
    repeat = "X" * 20
    content = filler + repeat * 4  # last 80 chars = 4x "XXXXXXXXXXXXXXXXXXXX"
    with pytest.raises(RuntimeError, match="repetitive loop"):
        RemoteProvider._detect_repetition_loop(content, "test-model")


def test_b4_threshold_respected():
    """[S3 B4] Only 2 identical windows (below threshold=3) must NOT raise."""
    filler = "B" * 100
    repeat = "Y" * 20
    content = filler + repeat * 2  # only 2 identical windows, threshold=3
    RemoteProvider._detect_repetition_loop(content, "model")
    # No exception = pass


# ── B6: In-gateway fallback (allow_fallbacks: true) ───────────────────────
@pytest.mark.asyncio
async def test_b6_allow_fallbacks_in_payload():
    """[S3 B6] When extra.allow_fallbacks=True, payload includes the flag."""
    cfg = ProviderConfig(
        name="openrouter",
        priority=0,
        api_keys=["key-0"],
        base_url="https://openrouter.ai/api",
        extra={"allow_fallbacks": True},
    )
    provider = OpenAICompatProvider(cfg)

    captured = {}

    async def _fake_post(url, json=None, headers=None):
        captured["payload"] = json
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"choices": [{"message": {"content": "ok"}}]}
        mock_resp.raise_for_status.return_value = None
        return mock_resp

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post = _fake_post
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = False
        mock_client_cls.return_value = mock_client

        result = await provider.generate("model", "sys", "query")

    assert result == "ok"
    assert captured["payload"].get("allow_fallbacks") is True


@pytest.mark.asyncio
async def test_b6_no_fallback_flag_when_disabled():
    """[S3 B6] Default (no flag) must NOT inject allow_fallbacks."""
    cfg = ProviderConfig(
        name="openrouter",
        priority=0,
        api_keys=["key-0"],
        base_url="https://openrouter.ai/api",
    )
    provider = OpenAICompatProvider(cfg)

    captured = {}

    async def _fake_post(url, json=None, headers=None):
        captured["payload"] = json
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"choices": [{"message": {"content": "ok"}}]}
        mock_resp.raise_for_status.return_value = None
        return mock_resp

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post = _fake_post
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = False
        mock_client_cls.return_value = mock_client

        await provider.generate("model", "sys", "query")

    assert "allow_fallbacks" not in captured["payload"]
