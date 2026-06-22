# AP: AP-PR-READINESS-v1.0.0
# ── Antigravity OAuth Client ──
# Handles OAuth token refresh and API calls to Google's internal Unified Gateway.
# [id-soft: doom-1993] Sovereign-Siloing — this module is self-contained, no cross-stack imports.

"""OAuth client for Google's undocumented Antigravity API.

The Antigravity API (`cloudcode-pa.googleapis.com`) uses OAuth Bearer tokens
for authentication, NOT API keys. Each account has a refresh token that must
be exchanged for an access token before making API calls.

Endpoint: POST https://cloudcode-pa.googleapis.com/v1internal:generateContent
Auth: Authorization: Bearer {access_token}
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import httpx

from .config import AntigravityConfig

logger = logging.getLogger(__name__)

# Token expiry buffer (60 seconds before actual expiry)
_TOKEN_EXPIRY_BUFFER_S = 60

# OAuth token endpoint
_TOKEN_URL = "https://oauth2.googleapis.com/token"

# Error classification
_QUOTA_KEYWORDS = {"exhausted", "quota", "rate limit", "too many requests", "presque"}
_CAPACITY_KEYWORDS = {"capacity", "overloaded", "resource exhausted"}


@dataclass
class AntigravityResponse:
    """Response from the Antigravity API."""

    text: str
    model: str
    account_email: Optional[str] = None
    tokens_in: int = 0
    tokens_out: int = 0
    provider_name: str = "antigravity"
    raw: Optional[Dict[str, Any]] = None


@dataclass
class OAuthToken:
    """Cached OAuth access token."""

    access_token: str
    expires_at: float  # Unix timestamp

    @property
    def is_expired(self) -> bool:
        return time.time() >= (self.expires_at - _TOKEN_EXPIRY_BUFFER_S)


class AntigravityClient:
    """OAuth client for Google's Antigravity API.

    Handles token refresh, API calls, and error classification.
    Does NOT handle account rotation — that's AccountManager's job.

    This client is stateless with respect to accounts. Each generate() call
    receives an account with its refresh token, and the client handles the
    rest.
    """

    def __init__(self, config: Optional[AntigravityConfig] = None) -> None:
        self._config = config or AntigravityConfig()
        self._token_cache: Dict[str, OAuthToken] = {}  # refresh_token -> OAuthToken
        self._http_client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Lazy-initialize shared HTTP client."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=60.0)
        return self._http_client

    async def refresh_access_token(self, refresh_token: str) -> OAuthToken:
        """Exchange a refresh token for an access token.

        Caches the result to avoid redundant refreshes within the token lifetime.
        """
        cached = self._token_cache.get(refresh_token)
        if cached and not cached.is_expired:
            return cached

        client = await self._get_client()
        try:
            response = await client.post(
                _TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "client_id": self._config.client_id,
                    "client_secret": self._config.client_secret,
                    "refresh_token": refresh_token,
                },
            )
            response.raise_for_status()
            data = response.json()

            access_token = data["access_token"]
            expires_in = data.get("expires_in", 3600)
            expires_at = time.time() + expires_in

            token = OAuthToken(access_token=access_token, expires_at=expires_at)
            self._token_cache[refresh_token] = token
            logger.debug("Refreshed access token for %s (expires in %ds)", refresh_token[:8], expires_in)
            return token

        except httpx.HTTPStatusError as e:
            logger.error("Token refresh failed: %s", e.response.status_code)
            raise
        except Exception as e:
            logger.error("Token refresh error: %s", e)
            raise

    async def generate(
        self,
        model: str,
        system_prompt: str,
        user_query: str,
        refresh_token: str,
        project_id: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        trace_id: Optional[str] = None,
    ) -> AntigravityResponse:
        """Generate content via the Antigravity API.

        Args:
            model: Model name (e.g., "claude-sonnet-4.6", "gemini-3.5-flash").
            system_prompt: System prompt.
            user_query: User query.
            refresh_token: OAuth refresh token for the account.
            project_id: Optional project ID for loadCodeAssist.
            temperature: Generation temperature.
            max_tokens: Maximum output tokens.
            trace_id: Optional trace ID for observability.

        Returns:
            AntigravityResponse with generated text and metadata.

        Raises:
            httpx.HTTPStatusError: On API errors (429, 401, 500, etc.).
        """
        token = await self.refresh_access_token(refresh_token)
        client = await self._get_client()

        url = f"{self._config.base_url}/v1internal:generateContent"
        payload = {
            "contents": [{"parts": [{"text": f"{system_prompt}\n\nUser: {user_query}"}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        headers = {
            "Authorization": f"Bearer {token.access_token}",
            "Content-Type": "application/json",
            "User-Agent": "antigravity/python/1.0",
        }

        # Add project metadata if available
        if project_id:
            headers["X-Goog-Api-Project"] = project_id

        response = await client.post(url, json=payload, headers=headers)

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise AntigravityRateLimitError(
                status_code=429,
                retry_after_ms=int(retry_after) * 1000 if retry_after else None,
                model=model,
                trace_id=trace_id,
            )

        if response.status_code in (401, 403):
            # Token may be revoked — clear cache
            self._token_cache.pop(refresh_token, None)
            raise AntigravityAuthError(
                status_code=response.status_code,
                model=model,
                trace_id=trace_id,
            )

        response.raise_for_status()
        data = response.json()

        # Extract text from response
        candidates = data.get("candidates", [])
        if not candidates:
            return AntigravityResponse(
                text="",
                model=model,
                raw=data,
            )

        text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()

        # Extract token usage
        usage = data.get("usageMetadata", {})

        return AntigravityResponse(
            text=text,
            model=model,
            tokens_in=usage.get("promptTokenCount", 0),
            tokens_out=usage.get("candidatesTokenCount", 0),
            raw=data,
        )

    async def check_available_models(self, refresh_token: str) -> Dict[str, Any]:
        """Query available models and quota via fetchAvailableModels.

        Returns the raw API response with model quota information.
        """
        token = await self.refresh_access_token(refresh_token)
        client = await self._get_client()

        url = f"{self._config.base_url}/v1internal:fetchAvailableModels"
        payload = {"project": "bamboo-precept-lgxtn"}

        headers = {
            "Authorization": f"Bearer {token.access_token}",
            "Content-Type": "application/json",
            "User-Agent": "antigravity/python/1.0",
        }

        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()
            self._http_client = None


# ── Typed Errors ──


class AntigravityError(Exception):
    """Base error for Antigravity API calls."""

    def __init__(self, message: str, model: str = "", trace_id: Optional[str] = None) -> None:
        self.model = model
        self.trace_id = trace_id
        super().__init__(message)


class AntigravityRateLimitError(AntigravityError):
    """Rate limit (429) from the Antigravity API."""

    def __init__(
        self,
        status_code: int = 429,
        retry_after_ms: Optional[int] = None,
        model: str = "",
        trace_id: Optional[str] = None,
    ) -> None:
        self.status_code = status_code
        self.retry_after_ms = retry_after_ms
        msg = f"Antigravity rate limit (429) for {model}"
        if retry_after_ms:
            msg += f" — retry after {retry_after_ms}ms"
        super().__init__(msg, model=model, trace_id=trace_id)


class AntigravityAuthError(AntigravityError):
    """Authentication error (401/403) from the Antigravity API."""

    def __init__(self, status_code: int = 401, model: str = "", trace_id: Optional[str] = None) -> None:
        self.status_code = status_code
        super().__init__(
            f"Antigravity auth error ({status_code}) for {model} — token may be revoked",
            model=model,
            trace_id=trace_id,
        )


def classify_rate_limit_reason(status_code: int, message: Optional[str] = None) -> str:
    """Classify the rate limit reason from status code and error message.

    Returns one of: "quota_exhausted", "rate_limit_exceeded",
    "model_capacity_exhausted", "server_error", "unknown".
    """
    if status_code in (529, 503):
        return "model_capacity_exhausted"
    if status_code == 500:
        return "server_error"

    if message:
        lower = message.lower()
        if any(kw in lower for kw in _CAPACITY_KEYWORDS):
            return "model_capacity_exhausted"
        if any(kw in lower for kw in _QUOTA_KEYWORDS):
            return "quota_exhausted"

    if status_code == 429:
        return "unknown"

    return "unknown"


def calculate_backoff_ms(reason: str, consecutive_failures: int, retry_after_ms: Optional[int] = None) -> int:
    """Calculate backoff duration in milliseconds based on rate limit reason.

    Matches the plugin's backoff strategy:
    - QUOTA_EXHAUSTED: 60s, 300s, 1800s, 7200s (escalating)
    - RATE_LIMIT_EXCEEDED: 30s
    - MODEL_CAPACITY_EXHAUSTED: 45s ± 15s jitter
    - SERVER_ERROR: 20s
    - UNKNOWN: 60s
    """
    import random

    if retry_after_ms and retry_after_ms > 0:
        return max(retry_after_ms, 2000)

    quota_backoffs = [60_000, 300_000, 1_800_000, 7_200_000]

    if reason == "quota_exhausted":
        idx = min(consecutive_failures, len(quota_backoffs) - 1)
        return quota_backoffs[idx]
    elif reason == "rate_limit_exceeded":
        return 30_000
    elif reason == "model_capacity_exhausted":
        return 45_000 + random.randint(-15_000, 15_000)
    elif reason == "server_error":
        return 20_000
    else:
        return 60_000
