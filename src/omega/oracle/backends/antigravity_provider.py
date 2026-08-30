# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Antigravity Provider — Sovereign Cloud Backend (S7.5)
# AP: AP-ANTIGRAVITY-PROVIDER-v1.0.0
# ⬡ OMEGA ⬡ RESEARCHER ⬡ antigravity ⬡ trc_core ⬡ PROVIDER-FABRIC
#
# First-class Antigravity provider using the official google-antigravity SDK.
# Bypasses the banned opencode-antigravity-auth plugin (IW-2 / M4 / M8 compliant).
# Sticky account routing only — NO round-robin (D205 ratified 2026-07-08).
#
# Heritage: This is a NEW sovereign module. It does NOT use the deleted
# src/omega/oracle/antigravity/ legacy code (purged in T1-8). It subclasses
# RemoteProvider to inherit the hardened retry + circuit-breaker fabric.

import logging
from typing import Optional

from omega.oracle.backends.remote_provider import RemoteProvider, ProviderConfig
from omega.errors import ProviderAuthError, ProviderUnavailableError

logger = logging.getLogger(__name__)

# ── Antigravity API base URL ──────────────────────────────────────────────
DEFAULT_BASE_URL = "https://api.antigravity.ai/v1"


class AntigravityProvider(RemoteProvider):
    """Sovereign Antigravity backend.

    Uses `google.genai.Client` with a custom HttpOptions base_url pointing to
    the Antigravity API.  This is LEANER than the full google.antigravity
    Agent harness (which spawns a local Go binary) and integrates directly
    with the provider fabric's retry + circuit-breaker.

    Auth: ANTIGRAVITY_API_KEY env var (headless) or OS keyring (ChainedAuth).
    Routing: sticky per-account — one account used sequentially until a hard
    429, then failover to next (D205). Never round-robin.

    Heritage: [id-soft: vet-025] Hard-Boundary — SDK calls are gated by
    a single guarded import, preventing cascading failures from a missing
    dependency.
    """

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self._sdk_client = None
        self._account_index = 0  # sticky until failover (D205)

    def _get_sdk_client(self):
        """Lazily import and instantiate the google.genai Client.

        Uses `HttpOptions(base_url=...)` to point at the Antigravity API
        instead of the default Google AI / Vertex endpoint.
        """
        if self._sdk_client is not None:
            return self._sdk_client

        # ── Import guard (M9 typed error) ──────────────────────────────
        try:
            from google.genai import Client as GenaiClient
            from google.genai.types import HttpOptions
        except ImportError as e:
            raise ProviderUnavailableError(
                "antigravity",
                "google-genai SDK not installed. Run: pip install google-genai",
            ) from e

        # ── Auth — vault-first chain ───────────────────────────────────
        api_key = self.resolve_current_api_key()
        if not api_key:
            raise ProviderAuthError(
                "antigravity",
                "No ANTIGRAVITY_API_KEY / vault key resolved for AntigravityProvider",
            )

        # ── Instantiate with Antigravity base URL ─────────────────────
        self._sdk_client = GenaiClient(
            api_key=api_key,
            http_options=HttpOptions(
                base_url=DEFAULT_BASE_URL,
                timeout=self.config.timeout or 120000,
            ),
        )
        return self._sdk_client

    async def _send_request(
        self,
        model_name: str,
        system_prompt: str,
        user_query: str,
        temperature: float,
        max_tokens: int,
        trace_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> str:
        """Send a text generation request via google.genai.aio.

        Inherits retry/breaker from RemoteProvider.  Uses the native asyncio
        interface (google.genai.aio) which is compatible with AnyIO's asyncio
        backend — no thread-pool overhead required.

        Args:
            model_name: Model ID recognised by the Antigravity API.
            system_prompt: System-level instructions (prepended as context).
            user_query: The user's message / prompt body.
            temperature: Sampling temperature.
            max_tokens: Maximum output tokens.
            trace_id: Optional observability trace identifier.

        Returns:
            The response text as a plain string.

        Raises:
            ProviderUnavailableError: The SDK is missing or the API returned
                an empty/failed response.
            ProviderAuthError: Authentication key could not be resolved.
        """
        client = self._get_sdk_client()

        # ── Build combined prompt ──────────────────────────────────────
        contents = f"{system_prompt}\n\n{user_query}" if system_prompt else user_query

        try:
            response = await client.aio.models.generate_content(
                model=model_name,
                contents=contents,
            )
        except ProviderAuthError:
            raise
        except ProviderUnavailableError:
            raise
        except Exception as exc:
            # Wrap unknown errors in OmegaError for M9 (Gate Integrity)
            raise ProviderUnavailableError(
                "antigravity",
                f"Antigravity API call failed: {exc}",
            ) from exc

        # ── Extract text from response ─────────────────────────────────
        if response is None:
            raise ProviderUnavailableError(
                "antigravity",
                "Empty response from google.genai (None)",
            )

        text = getattr(response, "text", None) or ""
        if not text.strip():
            raise ProviderUnavailableError(
                "antigravity",
                "Empty response text from Antigravity API",
            )

        return text.strip()
