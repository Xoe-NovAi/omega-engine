# SPDX-FileCopyrightText: 2026 Xoe-NovAi

# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

"""
Provider Quota Pollers for Omega Engine

Implements quota monitoring for external API providers:
- Grok (xAI) gRPC-web quota
- OpenRouter credits/limits
- Google Cloud Monitoring quotas
- Exa Search rate limits
- Firecrawl credits

Each poller follows the Sovereign Search Protocol (SSP) and integrates
with the VaultCore credential system.

M13 Temple-Grade: All implementations include error handling,
retry logic, and structured logging.
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import anyio
import httpx


class QuotaStatusLevel(Enum):
    """Quota status levels."""

    HEALTHY = "healthy"  # >50% remaining
    MODERATE = "moderate"  # 20-50% remaining
    LOW = "low"  # 5-20% remaining
    CRITICAL = "critical"  # 1-5% remaining
    EXHAUSTED = "exhausted"  # 0% remaining
    UNKNOWN = "unknown"  # Cannot determine status


@dataclass
class QuotaSnapshot:
    """Standardized quota information across all providers."""

    provider: str
    status: QuotaStatusLevel
    remaining: float
    total: float
    used: float
    percent_remaining: float
    reset_time: Optional[datetime] = None
    reset_seconds: Optional[int] = None
    is_free_tier: bool = False
    rate_limit_rpm: Optional[int] = None
    rate_limit_rpd: Optional[int] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "provider": self.provider,
            "status": self.status.value,
            "remaining": self.remaining,
            "total": self.total,
            "used": self.used,
            "percent_remaining": self.percent_remaining,
            "reset_time": self.reset_time.isoformat() if self.reset_time else None,
            "reset_seconds": self.reset_seconds,
            "is_free_tier": self.is_free_tier,
            "rate_limit_rpm": self.rate_limit_rpm,
            "rate_limit_rpd": self.rate_limit_rpd,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "error": self.error,
        }


class QuotaPoller(ABC):
    """Abstract base class for provider quota pollers."""

    def __init__(
        self,
        provider_name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_seconds: float = 10.0,
        max_retries: int = 3,
    ):
        self.provider_name = provider_name
        self.api_key = api_key
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self._last_snapshot: Optional[QuotaSnapshot] = None
        self._last_poll_time: float = 0
        self._min_poll_interval: float = 60.0  # Minimum 60 seconds between polls

    @abstractmethod
    async def _fetch_quota(self) -> QuotaSnapshot:
        """Fetch quota from provider API. Implement in subclasses."""
        ...

    def _calculate_status(self, remaining: float, total: float) -> QuotaStatusLevel:
        """Calculate quota status based on remaining percentage."""
        if total <= 0:
            return QuotaStatusLevel.UNKNOWN

        percent = (remaining / total) * 100

        if percent <= 0:
            return QuotaStatusLevel.EXHAUSTED
        elif percent < 5:
            return QuotaStatusLevel.CRITICAL
        elif percent < 20:
            return QuotaStatusLevel.LOW
        elif percent < 50:
            return QuotaStatusLevel.MODERATE
        else:
            return QuotaStatusLevel.HEALTHY

    async def poll(self, force: bool = False) -> QuotaSnapshot:
        """
        Poll quota with rate limiting and caching.

        Args:
            force: Force immediate poll, bypassing rate limit

        Returns:
            QuotaSnapshot with current quota information
        """
        now = time.time()

        # Rate limit check
        if not force and (now - self._last_poll_time) < self._min_poll_interval:
            if self._last_snapshot:
                return self._last_snapshot

        # Attempt with retries
        last_error = None
        for attempt in range(self.max_retries):
            try:
                snapshot = await self._fetch_quota()
                self._last_snapshot = snapshot
                self._last_poll_time = time.time()
                return snapshot
            except Exception as e:
                last_error = str(e)
                if attempt < self.max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    await anyio.sleep(2**attempt)

        # All retries failed
        error_snapshot = QuotaSnapshot(
            provider=self.provider_name,
            status=QuotaStatusLevel.UNKNOWN,
            remaining=0,
            total=0,
            used=0,
            percent_remaining=0,
            error=f"Failed after {self.max_retries} attempts: {last_error}",
        )
        self._last_snapshot = error_snapshot
        self._last_poll_time = time.time()
        return error_snapshot

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        pass


class GrokQuotaPoller(QuotaPoller):
    """
    Grok (xAI) quota poller via gRPC-web GetGrokCreditsConfig.

    Endpoint: POST https://grok.com/grok_api_v2.GrokBuildBilling/GetGrokCreditsConfig
    Content-Type: application/grpc-web+proto
    Auth: Bearer token (xAI OAuth from Hermes, NOT xAI API key)

    Rate limit: 1 request per 30 seconds
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://grok.com",
        **kwargs,
    ):
        super().__init__(
            provider_name="grok",
            api_key=api_key,
            base_url=base_url,
            **kwargs,
        )
        self._min_poll_interval = 30.0  # 30 seconds minimum

    async def _fetch_quota(self) -> QuotaSnapshot:
        """Fetch Grok quota via gRPC-web endpoint."""
        url = f"{self.base_url}/grok_api_v2.GrokBuildBilling/GetGrokCreditsConfig"

        headers = {
            "Content-Type": "application/grpc-web+proto",
            "Authorization": f"Bearer {self.api_key}",
        }

        # Empty body for proto3 request
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                content=b"",
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()

        # Parse gRPC-web response (simplified - real impl needs proto parsing)
        # For now, assume JSON response from mock or test endpoint
        try:
            data = response.json()
        except Exception as e:
            logger.warning("gRPC-web JSON parse failed, using fallback: %s", e, exc_info=True)
            # For now, assume JSON response from mock or test endpoint
            # For production, use grpcio-tools or protobuf library
            return QuotaSnapshot(
                provider="grok",
                status=QuotaStatusLevel.UNKNOWN,
                remaining=0,
                total=0,
                used=0,
                percent_remaining=0,
                error="gRPC-web proto parsing not implemented",
            )

        # Extract fields from response
        credit_usage_percent = data.get("credit_usage_percent", 0)
        billing_period_start = data.get("billing_period_start")
        billing_period_end = data.get("billing_period_end")
        on_demand_cap = data.get("on_demand_cap", 0)
        on_demand_used = data.get("on_demand_used", 0)

        # Calculate remaining
        remaining = on_demand_cap - on_demand_used
        percent_remaining = (remaining / on_demand_cap * 100) if on_demand_cap > 0 else 0

        # Parse reset time
        reset_time = None
        reset_seconds = None
        if billing_period_end:
            try:
                reset_time = datetime.fromisoformat(billing_period_end.replace("Z", "+00:00"))
                reset_seconds = int((reset_time - datetime.now(timezone.utc)).total_seconds())
            except Exception as e:
                logger.warning("Failed to parse reset time from billing period end: %s", e, exc_info=True)
                reset_time = None
                reset_seconds = None

        return QuotaSnapshot(
            provider="grok",
            status=self._calculate_status(remaining, on_demand_cap),
            remaining=remaining,
            total=on_demand_cap,
            used=on_demand_used,
            percent_remaining=percent_remaining,
            reset_time=reset_time,
            reset_seconds=reset_seconds,
            metadata={
                "credit_usage_percent": credit_usage_percent,
                "billing_period_start": billing_period_start,
            },
        )


class OpenRouterQuotaPoller(QuotaPoller):
    """
    OpenRouter credits/limits poller.

    Endpoints:
    - GET /api/v1/credits → {data: {total_credits, total_usage}}
    - GET /api/v1/key → {data: {limit, limit_remaining, limit_reset, usage, ...}}

    Error codes:
    - 402: insufficient credits
    - 429: rate limit + X-RateLimit-* headers
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://openrouter.ai",
        **kwargs,
    ):
        super().__init__(
            provider_name="openrouter",
            api_key=api_key,
            base_url=base_url,
            **kwargs,
        )

    async def _fetch_quota(self) -> QuotaSnapshot:
        """Fetch OpenRouter quota via credits and key endpoints."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            # Fetch credits
            credits_response = await client.get(
                f"{self.base_url}/api/v1/credits",
                headers=headers,
                timeout=self.timeout_seconds,
            )
            credits_response.raise_for_status()
            credits_data = credits_response.json().get("data", {})

            # Fetch key info
            key_response = await client.get(
                f"{self.base_url}/api/v1/key",
                headers=headers,
                timeout=self.timeout_seconds,
            )
            key_response.raise_for_status()
            key_data = key_response.json().get("data", {})

        # Extract fields
        total_credits = credits_data.get("total_credits", 0)
        total_usage = credits_data.get("total_usage", 0)
        remaining = total_credits - total_usage

        limit = key_data.get("limit", 0)
        limit_remaining = key_data.get("limit_remaining", 0)
        limit_reset = key_data.get("limit_reset")
        usage = key_data.get("usage", 0)
        is_free_tier = key_data.get("is_free_tier", False)

        # Parse reset time
        reset_time = None
        reset_seconds = None
        if limit_reset:
            try:
                reset_time = datetime.fromisoformat(limit_reset.replace("Z", "+00:00"))
                reset_seconds = int((reset_time - datetime.now(timezone.utc)).total_seconds())
            except Exception as e:
                logger.warning("Failed to parse reset time from billing period end: %s", e, exc_info=True)
                reset_time = None
                reset_seconds = None

        # Determine rate limits based on free tier status
        rate_limit_rpm = 20  # Default
        rate_limit_rpd = 50 if is_free_tier else 1000

        return QuotaSnapshot(
            provider="openrouter",
            status=self._calculate_status(remaining, total_credits),
            remaining=remaining,
            total=total_credits,
            used=total_usage,
            percent_remaining=(remaining / total_credits * 100) if total_credits > 0 else 0,
            reset_time=reset_time,
            reset_seconds=reset_seconds,
            is_free_tier=is_free_tier,
            rate_limit_rpm=rate_limit_rpm,
            rate_limit_rpd=rate_limit_rpd,
            metadata={
                "limit": limit,
                "limit_remaining": limit_remaining,
                "usage_daily": key_data.get("usage_daily", 0),
                "usage_weekly": key_data.get("usage_weekly", 0),
                "usage_monthly": key_data.get("usage_monthly", 0),
                "byok_usage": key_data.get("byok_usage", 0),
            },
        )


class GCPQuotaPoller(QuotaPoller):
    """
    Google Cloud Monitoring quota poller.

    Uses Service Usage API to query quota information.
    Requires monitoring.read scope.

    Endpoint: GET https://serviceusage.googleapis.com/v1beta1/projects/{project}/services/{service}
    """

    def __init__(
        self,
        project_id: str,
        service_name: str = "monitoring.googleapis.com",
        credentials_json: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(
            provider_name="gcp",
            base_url="https://serviceusage.googleapis.com",
            **kwargs,
        )
        self.project_id = project_id
        self.service_name = service_name
        self.credentials_json = credentials_json
        self._access_token: Optional[str] = None
        self._token_expiry: float = 0

    async def _get_access_token(self) -> str:
        """Get or refresh OAuth2 access token."""
        now = time.time()

        # Return cached token if valid
        if self._access_token and now < self._token_expiry - 60:
            return self._access_token

        # For production, use google-auth library
        # For now, assume token is provided or use service account
        if self.credentials_json:
            # TODO: Implement proper OAuth2 token exchange
            # This is a placeholder for the actual implementation
            raise NotImplementedError("OAuth2 token exchange not implemented")

        # Use application default credentials
        # In production, this would use google.auth.default()
        raise NotImplementedError("GCP authentication not configured")

    async def _fetch_quota(self) -> QuotaSnapshot:
        """Fetch GCP quota via Service Usage API."""
        token = await self._get_access_token()

        url = f"{self.base_url}/v1beta1/projects/{self.project_id}/services/{self.service_name}"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=headers,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()

        # Extract quota information
        quotas = data.get("quotas", [])

        # Find the relevant quota (e.g., request_count)
        quota_info = None
        for quota in quotas:
            if quota.get("metric") == "serviceruntime.googleapis.com/api/consumer/request_count":
                quota_info = quota
                break

        if not quota_info:
            return QuotaSnapshot(
                provider="gcp",
                status=QuotaStatusLevel.UNKNOWN,
                remaining=0,
                total=0,
                used=0,
                percent_remaining=0,
                error="No quota information found",
            )

        # Extract values
        limit = quota_info.get("limit", 0)
        usage = quota_info.get("usage", 0)
        remaining = limit - usage

        return QuotaSnapshot(
            provider="gcp",
            status=self._calculate_status(remaining, limit),
            remaining=remaining,
            total=limit,
            used=usage,
            percent_remaining=(remaining / limit * 100) if limit > 0 else 0,
            metadata={
                "service": self.service_name,
                "metric": quota_info.get("metric"),
                "unit": quota_info.get("unit"),
            },
        )


class ExaQuotaPoller(QuotaPoller):
    """
    Exa Search API rate limit poller.

    Rate limits:
    - /search: 10 QPS
    - /contents: 100 QPS
    - /answer: 10 QPS

    Note: Exa doesn't provide a dedicated quota endpoint.
    We track usage locally and infer rate limits.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.exa.ai",
        **kwargs,
    ):
        super().__init__(
            provider_name="exa",
            api_key=api_key,
            base_url=base_url,
            **kwargs,
        )
        self._request_times: list[float] = []
        self._min_poll_interval = 10.0  # 10 seconds minimum

    async def _fetch_quota(self) -> QuotaSnapshot:
        """
        Check Exa API health and rate limits.

        Since Exa doesn't have a quota endpoint, we:
        1. Make a lightweight search request
        2. Track response headers for rate limit info
        3. Calculate remaining capacity
        """
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }

        # Minimal search request to check API health
        payload = {
            "query": "test",
            "type": "instant",
            "numResults": 1,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/search",
                headers=headers,
                json=payload,
                timeout=self.timeout_seconds,
            )

            # Track request time
            now = time.time()
            self._request_times.append(now)

            # Clean old request times (keep last 60 seconds)
            self._request_times = [t for t in self._request_times if now - t < 60]

        # Calculate QPS from recent requests
        recent_requests = len([t for t in self._request_times if now - t < 1])

        # Exa rate limits (from documentation)
        search_limit = 10  # QPS
        contents_limit = 100  # QPS
        answer_limit = 10  # QPS

        # Calculate remaining capacity
        search_remaining = max(0, search_limit - recent_requests)

        return QuotaSnapshot(
            provider="exa",
            status=self._calculate_status(search_remaining, search_limit),
            remaining=search_remaining,
            total=search_limit,
            used=recent_requests,
            percent_remaining=(search_remaining / search_limit * 100) if search_limit > 0 else 0,
            rate_limit_rpm=search_limit * 60,  # Convert QPS to RPM
            metadata={
                "search_qps_limit": search_limit,
                "contents_qps_limit": contents_limit,
                "answer_qps_limit": answer_limit,
                "recent_requests_1s": recent_requests,
                "requests_last_60s": len(self._request_times),
            },
        )


class FirecrawlQuotaPoller(QuotaPoller):
    """
    Firecrawl credits poller.

    Endpoint: GET /v2/team/credit-usage
    Response: {success: true, data: {remainingCredits, planCredits, billingPeriodStart, billingPeriodEnd}}

    Credit costs:
    - Scrape: 1 credit/page
    - Crawl: 1 credit/page
    - Map: 1 credit/call
    - Search: 2 credits/10 results
    - Interact: 2 credits/browser minute
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.firecrawl.dev",
        **kwargs,
    ):
        super().__init__(
            provider_name="firecrawl",
            api_key=api_key,
            base_url=base_url,
            **kwargs,
        )

    async def _fetch_quota(self) -> QuotaSnapshot:
        """Fetch Firecrawl credits via credit-usage endpoint."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v2/team/credit-usage",
                headers=headers,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()

        if not data.get("success"):
            return QuotaSnapshot(
                provider="firecrawl",
                status=QuotaStatusLevel.UNKNOWN,
                remaining=0,
                total=0,
                used=0,
                percent_remaining=0,
                error=data.get("error", "Unknown error"),
            )

        # Extract fields
        remaining_credits = data.get("data", {}).get("remainingCredits", 0)
        plan_credits = data.get("data", {}).get("planCredits", 0)
        billing_period_start = data.get("data", {}).get("billingPeriodStart")
        billing_period_end = data.get("data", {}).get("billingPeriodEnd")

        # Calculate used
        used = plan_credits - remaining_credits if plan_credits > 0 else 0

        # Parse reset time
        reset_time = None
        reset_seconds = None
        if billing_period_end:
            try:
                reset_time = datetime.fromisoformat(billing_period_end.replace("Z", "+00:00"))
                reset_seconds = int((reset_time - datetime.now(timezone.utc)).total_seconds())
            except Exception as e:
                logger.warning("Failed to parse reset time from billing period end: %s", e, exc_info=True)
                reset_time = None
                reset_seconds = None

        return QuotaSnapshot(
            provider="firecrawl",
            status=self._calculate_status(remaining_credits, plan_credits),
            remaining=remaining_credits,
            total=plan_credits,
            used=used,
            percent_remaining=(remaining_credits / plan_credits * 100) if plan_credits > 0 else 0,
            reset_time=reset_time,
            reset_seconds=reset_seconds,
            metadata={
                "billing_period_start": billing_period_start,
                "credit_costs": {
                    "scrape": "1 credit/page",
                    "crawl": "1 credit/page",
                    "map": "1 credit/call",
                    "search": "2 credits/10 results",
                    "interact": "2 credits/browser minute",
                },
            },
        )


# Factory function for creating pollers
def create_quota_poller(
    provider: str,
    **kwargs,
) -> QuotaPoller:
    """
    Factory function to create appropriate quota poller.

    Args:
        provider: Provider name (grok, openrouter, gcp, exa, firecrawl)
        **kwargs: Provider-specific configuration

    Returns:
        QuotaPoller instance

    Raises:
        ValueError: If provider is not supported
    """
    pollers = {
        "grok": GrokQuotaPoller,
        "openrouter": OpenRouterQuotaPoller,
        "gcp": GCPQuotaPoller,
        "exa": ExaQuotaPoller,
        "firecrawl": FirecrawlQuotaPoller,
    }

    if provider not in pollers:
        raise ValueError(f"Unsupported provider: {provider}. Supported: {list(pollers.keys())}")

    return pollers[provider](**kwargs)


# Module exports
__all__ = [
    "QuotaStatusLevel",
    "QuotaSnapshot",
    "QuotaPoller",
    "GrokQuotaPoller",
    "OpenRouterQuotaPoller",
    "GCPQuotaPoller",
    "ExaQuotaPoller",
    "FirecrawlQuotaPoller",
    "create_quota_poller",
]
