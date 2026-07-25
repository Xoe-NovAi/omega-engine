# 🔱 omega-vetala — Perspective API Provider
# ⬡ OMEGA ⬡ P6-MODELGATE ⬡ PERSPECTIVE-PROVIDER
#
# Google Perspective API wrapper with rate limiting and graceful degradation.
# Free tier: 1 query per second.

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
    ProviderError,
)

logger = logging.getLogger(__name__)

# Default categories requested from Perspective API
_DEFAULT_ATTRIBUTES: dict[str, dict[str, float]] = {
    "TOXICITY": {},
    "INSULT": {},
    "PROFANITY": {},
    "THREAT": {},
    "IDENTITY_ATTACK": {},
}

# Minimum free-tier interval between requests (seconds)
_RATE_LIMIT_INTERVAL = 1.0

# HTTP request timeout
_REQUEST_TIMEOUT = 5.0

# Endpoint
_PERSPECTIVE_API_URL = (
    "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze"
)


class PerspectiveProvider(ModelProvider):
    """Content moderation via Google's Perspective API.

    Requires the ``PERSPECTIVE_API_KEY`` environment variable.

    Free-tier rate limit is 1 request per second.  If the API is
    unreachable or returns an error a low-confidence (non-flagged)
    result is returned — the caller (e.g. :class:`ProviderChain`)
    can fall through to the next provider.

    Attributes:
        supports_offline: False — requires network access.
    """

    supports_offline: bool = False

    def __init__(self, api_key: str | None = None) -> None:
        """Initialise provider.

        Args:
            api_key: Perspective API key.  Falls back to VaultCore.
        """
        if api_key is None:
            try:
                from omega.vault import VaultCore
                vault = VaultCore()
                vault._load_sync()
                cred = vault._credentials.get("perspective:api_key")
                api_key = cred.encrypted_blob if cred else ""
            except Exception:
                api_key = ""
        self._api_key = api_key
        self._last_request: float = 0.0
        self._client: httpx.Client | None = None

    # ------------------------------------------------------------------
    # Resource lifecycle
    # ------------------------------------------------------------------

    async def __aenter__(self) -> "PerspectiveProvider":
        """Create shared HTTP client on context entry."""
        self._client = httpx.Client(timeout=_REQUEST_TIMEOUT)
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Close HTTP client on context exit."""
        if self._client is not None:
            self._client.close()
            self._client = None

    # ------------------------------------------------------------------
    # Core logic
    # ------------------------------------------------------------------

    async def _rate_limit(self) -> None:
        """Enforce 1 request per second (free-tier)."""
        now = time.monotonic()
        since_last = now - self._last_request
        if since_last < _RATE_LIMIT_INTERVAL:
            await anyio.sleep(_RATE_LIMIT_INTERVAL - since_last)
        self._last_request = time.monotonic()

    async def analyze(self, text: str) -> ModerationResult:
        """Analyse *text* via Perspective API.

        Args:
            text: Content to moderate.

        Returns:
            :class:`ModerationResult` with Perspective category scores,
            or a low-confidence result on failure.
        """
        if not self._api_key:
            logger.warning("PERSPECTIVE_API_KEY not set — returning empty result")
            return ModerationResult(
                provider_name="perspective",
                categories={"__no_key__": 1.0},
            )

        if not text.strip():
            return ModerationResult(provider_name="perspective")

        # Rate-limit BEFORE sending
        await self._rate_limit()

        # Build payload
        payload: dict[str, Any] = {
            "comment": {"text": text},
            "languages": ["en"],
            "requestedAttributes": _DEFAULT_ATTRIBUTES,
        }

        # Wrap the synchronous HTTP call in anyio thread
        def _do_request() -> httpx.Response:
            assert self._client is not None  # guaranteed by __aenter__
            url = f"{_PERSPECTIVE_API_URL}?key={self._api_key}"
            return self._client.post(url, json=payload)

        try:
            response: httpx.Response = await anyio.to_thread.run_sync(
                _do_request,
                abandon_on_cancel=True,
            )
            response.raise_for_status()
            data = response.json()
        except httpx.TimeoutException:
            logger.warning("Perspective API timed out")
            return ModerationResult(
                provider_name="perspective",
                categories={"__timeout__": 1.0},
            )
        except httpx.HTTPStatusError as exc:
            logger.warning("Perspective API HTTP error: %s", exc)
            return ModerationResult(
                provider_name="perspective",
                categories={"__http_error__": 1.0},
            )
        except Exception as exc:
            logger.exception("Perspective API unexpected error: %s", exc)
            return ModerationResult(
                provider_name="perspective",
                categories={"__error__": 1.0},
            )

        # Parse response
        categories: dict[str, float] = {}
        scores = data.get("attributeScores", {})
        for cat_name, cat_data in scores.items():
            summary = cat_data.get("summaryScore", {})
            categories[cat_name.lower()] = summary.get("value", 0.0)

        # Determine overall flag
        is_flagged = any(v >= 0.7 for v in categories.values())
        confidence = max(categories.values()) if categories else 0.0

        return ModerationResult(
            is_flagged=is_flagged,
            confidence=confidence,
            categories=categories,
            provider_name="perspective",
        )
