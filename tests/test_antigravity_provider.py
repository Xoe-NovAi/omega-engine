# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Contract Tests — S7.5 Antigravity Provider
# AP: AP-ANTIGRAVITY-PROVIDER-TESTS-v1.0.0
# ⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_S7_5 ⬡ M21-CONTRACT-TESTS
#
# [M21 Gate Integrity] AntigravityProvider must subclass RemoteProvider and
# fail gracefully when the google.genai SDK is absent (import guard).
# Uses MagicMock to avoid real network calls (sovereign-local, no telemetry).
#
# The provider uses `google.genai.Client` (NOT the full google.antigravity
# Agent harness) with a custom HttpOptions base_url pointing at the
# Antigravity API endpoint.
#
# [S3 B4 Integration] AntigravityProvider inherits the Repetition Loop Detector
# from RemoteProvider base class (moved from OpenAICompatProvider in S3).

import builtins
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from omega.oracle.backends.remote_provider import RemoteProvider, ProviderConfig
from omega.oracle.backends.antigravity_provider import AntigravityProvider
from omega.errors import ProviderUnavailableError, ProviderAuthError


def test_s75_subclasses_remote_provider():
    """[S7.5] AntigravityProvider must inherit the hardened retry/breaker fabric."""
    cfg = ProviderConfig(name="antigravity", priority=0)
    provider = AntigravityProvider(cfg)
    assert isinstance(provider, RemoteProvider)


def test_s75_sdk_import_guard_no_leak():
    """[S7.5] When google.genai SDK is missing, _get_sdk_client must raise
    ProviderUnavailableError (NOT a bare ImportError leaking to the caller)."""
    cfg = ProviderConfig(name="antigravity", priority=0)
    provider = AntigravityProvider(cfg)

    # Simulate missing google.genai by patching __import__
    original_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name.startswith("google.genai"):
            raise ImportError(f"No module named '{name}'")
        return original_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=mock_import):
        with pytest.raises(ProviderUnavailableError):
            provider._get_sdk_client()


def test_s75_auth_error_without_key():
    """[S7.5] With SDK present but no resolved key, raise ProviderAuthError."""
    cfg = ProviderConfig(name="antigravity", priority=0)
    provider = AntigravityProvider(cfg)
    with patch.object(provider, "resolve_current_api_key", return_value=None):
        with pytest.raises(ProviderAuthError):
            provider._get_sdk_client()


@pytest.mark.asyncio
async def test_s75_send_request_returns_str_contract():
    """[S7.5 / M21] _send_request must return a str (typed result contract)."""
    cfg = ProviderConfig(name="antigravity", priority=0)
    provider = AntigravityProvider(cfg)

    fake_response = MagicMock()
    fake_response.text = "sovereign response"

    # Mock client with aio.models.generate_content path
    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=fake_response)

    with patch.object(
        provider, "_get_sdk_client", return_value=mock_client
    ), patch.object(provider, "resolve_current_api_key", return_value="dummy-key"):
        result = await provider._send_request(
            model_name="gemma-4-31b-it",
            system_prompt="sys",
            user_query="query",
            temperature=0.7,
            max_tokens=1024,
        )
        assert isinstance(result, str)
        assert result == "sovereign response"
        # Verify the SDK was called with the right arguments
        mock_client.aio.models.generate_content.assert_awaited_once_with(
            model="gemma-4-31b-it",
            contents="sys\n\nquery",
        )


# ── S3 B4 Integration: Loop Detector Inheritance ──────────────────────────
def test_s75_inherits_loop_detector():
    """[S7.5 / S3 B4] AntigravityProvider inherits _detect_repetition_loop from RemoteProvider."""
    cfg = ProviderConfig(name="antigravity", priority=0)
    provider = AntigravityProvider(cfg)
    # Prove the static method exists and is callable
    assert hasattr(provider, "_detect_repetition_loop")
    # Short content (< 60 chars) must not raise
    provider._detect_repetition_loop("short", "antigravity")
    # Repetitive content must raise
    with pytest.raises(RuntimeError, match="repetitive loop"):
        provider._detect_repetition_loop("A" * 100 + "X" * 80, "antigravity")
