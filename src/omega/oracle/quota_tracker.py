# AP: AP-ORACLE-QUOTA-TRACKER-v1.0.0
# 🔱 Oracle Quota Tracker — Provider Quota Management
# Tracks quota usage per provider from response headers and enables quota-aware routing

"""
Quota Tracker for Oracle Provider Fabric

Monitors provider quota consumption from HTTP response headers and enables
quota-aware routing to prevent rate-limit loops and quota exhaustion.

Supports 6 major providers:
- OpenRouter: x-ratelimit-remaining-requests (errors only), 402 vs 429 distinction
- Anthropic: anthropic-ratelimit-requests-remaining, anthropic-ratelimit-tokens-remaining
- Google/Gemini: x-ratelimit-remaining-requests, x-ratelimit-remaining-tokens
- SambaNova: x-ratelimit-remaining-requests, x-ratelimit-remaining-requests-day
- Cerebras: x-ratelimit-remaining-requests-day, x-ratelimit-remaining-tokens-minute
- DigitalOcean: x-ratelimit-remaining-requests, x-ratelimit-remaining-tokens-per-day/minute

Implements IETF RateLimit Headers draft (draft-ietf-httpapi-ratelimit-headers-11)
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Dict, Optional
from omega.errors import OmegaError

logger = __import__("logging").getLogger("omega.quota_tracker")


@dataclass
class QuotaSnapshot:
    """Immutable snapshot of quota status at a point in time."""
    provider: str
    timestamp: float
    requests_remaining: int
    tokens_remaining: int
    requests_limit: int
    tokens_limit: int
    requests_reset: float  # Unix timestamp
    tokens_reset: float    # Unix timestamp
    exhausted: bool = False

    @property
    def requests_reset_in(self) -> float:
        """Seconds until request quota resets."""
        return max(0, self.requests_reset - time.time())

    @property
    def tokens_reset_in(self) -> float:
        """Seconds until token quota resets."""
        return max(0, self.tokens_reset - time.time())


@dataclass
class QuotaUsage:
    """Tracks quota consumption for a provider."""
    provider: str
    requests_used: int = 0
    tokens_used: int = 0
    last_updated: float = field(default_factory=time.time)
    request_reset: float = 0.0
    token_reset: float = 0.0
    request_limit: int = 0
    token_limit: int = 0

    @property
    def requests_remaining(self) -> int:
        if self.request_limit == 0:
            return 2**31 - 1  # Effectively unlimited
        return max(0, self.request_limit - self.requests_used)

    @property
    def tokens_remaining(self) -> int:
        if self.token_limit == 0:
            return 2**31 - 1  # Effectively unlimited
        return max(0, self.token_limit - self.tokens_used)

    @property
    def is_exhausted(self) -> bool:
        """Check if either requests or tokens are exhausted."""
        return self.requests_remaining <= 0 or self.tokens_remaining <= 0

    def to_snapshot(self) -> QuotaSnapshot:
        """Create an immutable snapshot of current quota state."""
        return QuotaSnapshot(
            provider=self.provider,
            timestamp=self.last_updated,
            requests_remaining=self.requests_remaining,
            tokens_remaining=self.tokens_remaining,
            requests_limit=self.request_limit,
            tokens_limit=self.token_limit,
            requests_reset=self.request_reset,
            tokens_reset=self.token_reset,
            exhausted=self.is_exhausted,
        )


class QuotaTracker:
    """
    Tracks quota usage for all providers in the fabric.
    
    Parses provider-specific quota headers and maintains rolling windows
    of quota consumption to enable proactive throttling.
    """

    def __init__(self):
        self._quotas: dict[str, QuotaUsage] = {}
        self._history: dict[str, list[QuotaSnapshot]] = {}
        self._lock = __import__("anyio").Lock()

        # Provider-specific header mappings
        self._header_map = {
            "openrouter": {
                "requests": "x-ratelimit-remaining-requests",
                "tokens": None,  # OpenRouter doesn't provide token headers on success
                "requests_reset": "x-ratelimit-reset-requests",
                "tokens_reset": None,
                "quota_exceeded_status": 402,  # Distinct from rate limit 429
            },
            "anthropic": {
                "requests": "anthropic-ratelimit-requests-remaining",
                "tokens": "anthropic-ratelimit-tokens-remaining",
                "requests_reset": "anthropic-ratelimit-requests-reset",
                "tokens_reset": "anthropic-ratelimit-tokens-reset",
                "quota_exceeded_status": 429,
            },
            "google": {
                "requests": "x-ratelimit-remaining-requests",
                "tokens": "x-ratelimit-remaining-tokens",
                "requests_reset": "x-ratelimit-reset-requests",
                "tokens_reset": "x-ratelimit-reset-tokens",
                "quota_exceeded_status": 429,
            },
            "sambanova": {
                "requests": "x-ratelimit-remaining-requests-day",
                "tokens": None,  # SambaNova doesn't provide token limits in headers
                "requests_reset": "x-ratelimit-reset-requests-day",
                "tokens_reset": None,
                "quota_exceeded_status": 429,
            },
            "cerebras": {
                "requests": "x-ratelimit-remaining-requests-day",
                "tokens": "x-ratelimit-remaining-tokens-minute",
                "requests_reset": "x-ratelimit-reset-requests-day",
                "tokens_reset": "x-ratelimit-reset-tokens-minute",
                "quota_exceeded_status": 429,
            },
            "digitalocean": {
                "requests": "x-ratelimit-remaining-requests",
                "tokens": "x-ratelimit-remaining-tokens-per-day",
                "requests_reset": "x-ratelimit-reset-requests",
                "tokens_reset": "x-ratelimit-reset-tokens-per-day",
                "quota_exceeded_status": 429,
            },
        }

        # Compile regex for quota-exceeded error detection
        self._quota_error_pattern = re.compile(
            r"monthly\.quota|daily\.limit|out\.of\.credits|quota\.exceeded|"
            r"insufficient\.credit|billing|payment|plan\.limit",
            re.IGNORECASE,
        )

    async def update_from_response(
        self,
        provider_name: str,
        headers: dict[str, str],
        status_code: int,
        response_body: str = "",
    ) -> None:
        """
        Update quota tracking from provider response headers.
        
        Called after each provider response to track quota consumption.
        """
        async with self._lock:
            if provider_name not in self._quotas:
                self._quotas[provider_name] = QuotaUsage(provider=provider_name)
                self._history[provider_name] = []

            quota = self._quotas[provider_name]
            quota.last_updated = time.time()

            # Get provider-specific header mapping
            headers_map = self._header_map.get(provider_name.lower(), {})
            if not headers_map:
                # Unknown provider - skip quota tracking
                return

            # Update request quota
            req_header = headers_map.get("requests")
            if req_header and req_header in headers:
                try:
                    quota.requests_used = int(headers[req_header])
                    reset_header = headers_map.get("requests_reset")
                    if reset_header and reset_header in headers:
                        quota.request_reset = float(headers[reset_header])
                    else:
                        # Default to 1 hour if no reset header
                        quota.request_reset = time.time() + 3600
                except (ValueError, TypeError):
                    pass

            # Update token quota
            token_header = headers_map.get("tokens")
            if token_header and token_header in headers:
                try:
                    quota.tokens_used = int(headers[token_header])
                    reset_header = headers_map.get("tokens_reset")
                    if reset_header and reset_header in headers:
                        quota.token_reset = float(headers[reset_header])
                    else:
                        # Default to 1 hour if no reset header
                        quota.token_reset = time.time() + 3600
                except (ValueError, TypeError):
                    pass

            # Handle special case: OpenRouter only provides quota headers on errors
            if provider_name.lower() == "openrouter" and status_code in (402, 429):
                # Try to get quota from the specific endpoint or error response
                if "x-ratelimit-remaining-requests" in headers:
                    try:
                        quota.requests_used = int(headers["x-ratelimit-remaining-requests"])
                        quota.request_limit = int(headers.get("x-ratelimit-limit-requests", quota.requests_used + 100))
                        reset_header = headers.get("x-ratelimit-reset-requests")
                        if reset_header:
                            quota.request_reset = float(reset_header)
                    except (ValueError, TypeError):
                        pass

            # Check for quota exhaustion via response body (for providers that don't header it)
            if status_code in (402, 429) and self._quota_error_pattern.search(response_body):
                # Mark as exhausted - will be reset when quota headers are next seen
                quota.requests_used = quota.request_limit or 1
                quota.tokens_used = quota.token_limit or 1

            # Store snapshot for historical analysis
            self._history[provider_name].append(quota.to_snapshot())
            # Keep only last 100 snapshots per provider
            if len(self._history[provider_name]) > 100:
                self._history[provider_name] = self._history[provider_name][-100:]

            logger.debug(
                f"Updated quota for {provider_name}: "
                f"{quota.requests_remaining} req, {quota.tokens_remaining} tok remaining"
            )

    def get_quota(self, provider_name: str) -> Optional[QuotaUsage]:
        """Get current quota usage for a provider."""
        return self._quotas.get(provider_name)

    def get_quota_snapshot(self, provider_name: str) -> Optional[QuotaSnapshot]:
        """Get immutable quota snapshot for a provider."""
        quota = self._quotas.get(provider_name)
        return quota.to_snapshot() if quota else None

    def is_quota_exhausted(self, provider_name: str) -> bool:
        """Check if a provider's quota is exhausted."""
        quota = self._quotas.get(provider_name)
        return quota.is_exhausted if quota else False

    def get_time_to_reset(self, provider_name: str) -> float:
        """
        Get seconds until quota resets for a provider.
        
        Returns the minimum of request and token reset times.
        """
        quota = self._quotas.get(provider_name)
        if not quota:
            return 0.0
        
        reset_times = []
        if quota.request_reset > 0:
            reset_times.append(quota.request_reset - time.time())
        if quota.token_reset > 0:
            reset_times.append(quota.token_reset - time.time())
        
        return max(0, min(reset_times) if reset_times else 0)

    def get_available_providers(self, providers: list[str]) -> list[str]:
        """
        Filter providers to only those with available quota.
        
        Returns list of provider names that are not quota-exhausted.
        """
        available = []
        for provider in providers:
            if not self.is_quota_exhausted(provider):
                available.append(provider)
        return available

    def estimate_reset_time(self, provider_name: str) -> float:
        """
        Estimate when quota will be available again.
        
        Returns Unix timestamp of when quota should refresh.
        """
        quota = self._quotas.get(provider_name)
        if not quota:
            return time.time()
        
        # Return the sooner of request or token reset
        resets = []
        if quota.request_reset > 0:
            resets.append(quota.request_reset)
        if quota.token_reset > 0:
            resets.append(quota.token_reset)
        
        return min(resets) if resets else time.time()


# Global quota tracker instance
_quota_tracker: Optional[QuotaTracker] = None


def get_quota_tracker() -> QuotaTracker:
    """Get or create the global quota tracker instance."""
    global _quota_tracker
    if _quota_tracker is None:
        _quota_tracker = QuotaTracker()
    return _quota_tracker