# 🔱 omega-vetala — OpenAI Moderation API Provider
# ⬡ OMEGA ⬡ P6-MODELGATE ⬡ OPENAI-PROVIDER
#
# Wraps OpenAI's /v1/moderations endpoint with category mapping,
# rate limiting, and graceful fallback.

from __future__ import annotations

import logging
import os
import time
from typing import Any

import anyio
import httpx

from omega_vetala.providers.base import (
    ModerationResult,
    ModelProvider,
)

logger = logging.getLogger(__name__)

_OPENAI_MODERATION_URL = "https://api.openai.com/v1/moderations"
_REQUEST_TIMEOUT = 10.0
_RATE_LIMIT_INTERVAL = 0.5  # 2 req/s for the free/standard tier

# Maps OpenAI API category keys to our internal standard categories.
# The OpenAI Moderation API returns a flat dict of boolean + score pairs.
_CATEGORY_MAP: dict[str, str] = {
    "sexual": "sexual",
    "hate": "hate",
    "harassment": "harassment",
    "self-harm": "self_harm",
    "sexual/minors": "sexual_minors",
    "hate/threatening": "hate_threatening",
    "violence/graphic": "violence_graphic",
    "self-harm/intent": "self_harm_intent",
    "self-harm/instructions": "self_harm_instructions",
    "harassment/threatening": "harassment_threatening",
    "violence": "violence",
}


class OpenAIModerationProvider(ModelProvider):
    """Content moderation via OpenAI's Moderation API.

    Requires the ``OPENAI_API_KEY`` environment variable.

    Maps OpenAI's native categories to a consistent internal set so that
    results are comparable with other providers in the chain.

    Attributes:
        supports_offline: False — requires network access.
    """

    supports_offline: bool = False

    def __init__(self, api_key: str | None = None) -> None:
        """Initialise provider.

        Args:
            api_key: OpenAI API key.  Falls back to VaultCore.
        """
        if api_key is None:
            try:
                from omega.vault import VaultCore
                vault = VaultCore()
                vault._load_sync()
                cred = vault._credentials.get("openai:api_key")
                api_key = cred.encrypted_blob if cred else ""
            except Exception:
                api_key = ""
        self._api_key = api_key
        self._last_request: float = 0.0
        self._client: httpx.Client | None = None

    # ------------------------------------------------------------------
    # Resource lifecycle
    # ------------------------------------------------------------------

    async def __aenter__(self) -> "OpenAIModerationProvider":
        """Create shared HTTP client."""
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        self._client = httpx.Client(
            timeout=_REQUEST_TIMEOUT, headers=headers
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Close HTTP client."""
        if self._client is not None:
            self._client.close()
            self._client = None

    # ------------------------------------------------------------------
    # Rate limiting
    # ------------------------------------------------------------------

    async def _rate_limit(self) -> None:
        """Enforce a maximum request rate."""
        now = time.monotonic()
        since_last = now - self._last_request
        if since_last < _RATE_LIMIT_INTERVAL:
            await anyio.sleep(_RATE_LIMIT_INTERVAL - since_last)
        self._last_request = time.monotonic()

    # ------------------------------------------------------------------
    # Core logic
    # ------------------------------------------------------------------

    async def analyze(self, text: str) -> ModerationResult:
        """Analyse *text* via OpenAI Moderation API.

        Args:
            text: Content to moderate.

        Returns:
            :class:`ModerationResult` with mapped categories,
            or a low-confidence result on failure.
        """
        if not self._api_key:
            logger.warning("OPENAI_API_KEY not set — returning empty result")
            return ModerationResult(
                provider_name="openai_moderation",
                categories={"__no_key__": 1.0},
            )

        if not text.strip():
            return ModerationResult(provider_name="openai_moderation")

        await self._rate_limit()

        payload = {"input": text}

        def _do_request() -> httpx.Response:
            assert self._client is not None
            return self._client.post(_OPENAI_MODERATION_URL, json=payload)

        try:
            response: httpx.Response = await anyio.to_thread.run_sync(
                _do_request, abandon_on_cancel=True,
            )
            response.raise_for_status()
            data = response.json()
        except httpx.TimeoutException:
            logger.warning("OpenAI Moderation API timed out")
            return ModerationResult(
                provider_name="openai_moderation",
                categories={"__timeout__": 1.0},
            )
        except httpx.HTTPStatusError as exc:
            logger.warning("OpenAI Moderation HTTP error: %s", exc)
            return ModerationResult(
                provider_name="openai_moderation",
                categories={"__http_error__": 1.0},
            )
        except Exception as exc:
            logger.exception("OpenAI Moderation unexpected error: %s", exc)
            return ModerationResult(
                provider_name="openai_moderation",
                categories={"__error__": 1.0},
            )

        # Parse the first (and only) result
        results = data.get("results", [])
        if not results:
            return ModerationResult(
                provider_name="openai_moderation",
                categories={"__no_results__": 1.0},
            )

        raw = results[0]
        flagged: bool = raw.get("flagged", False)
        raw_categories: dict[str, float] = raw.get("category_scores", {})

        # Map to our standard category names
        mapped: dict[str, float] = {}
        for openai_key, score in raw_categories.items():
            std_key = _CATEGORY_MAP.get(openai_key, openai_key.replace("/", "_"))
            mapped[std_key] = score

        confidence = max(mapped.values()) if mapped else 0.0

        return ModerationResult(
            is_flagged=flagged,
            confidence=confidence,
            categories=mapped,
            provider_name="openai_moderation",
        )
