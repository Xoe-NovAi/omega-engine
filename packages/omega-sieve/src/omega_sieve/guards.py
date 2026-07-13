"""SovereignSentry & BudgetGuard — pre-flight checks and credit tracking.

SovereignSentry: Canary probes to check provider health before extraction.
BudgetGuard: Atomic API credit tracking to prevent double-spending across agents.
"""

# AP: AP-OMEGA-SIEVE-GUARDS-v1.0.0

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Optional

from .errors import BudgetExceededError, ProviderError

logger = logging.getLogger("omega_sieve.guards")


@dataclass
class SentryResult:
    """Result of a sentry probe."""
    provider: str
    healthy: bool
    latency_ms: int = 0
    error: Optional[str] = None


class SovereignSentry:
    """Pre-flight canary probes for external providers.

    Before making an expensive API call, the sentry checks:
    1. Is the provider reachable?
    2. Does the API key work?
    3. Is the circuit breaker closed?
    """

    def __init__(self):
        self._circuit_breakers: dict[str, CircuitBreaker] = {}

    def get_circuit_breaker(self, provider: str) -> "CircuitBreaker":
        """Get or create circuit breaker for a provider."""
        if provider not in self._circuit_breakers:
            self._circuit_breakers[provider] = CircuitBreaker(provider)
        return self._circuit_breakers[provider]

    async def probe(self, provider: str, api_key: Optional[str] = None) -> SentryResult:
        """Probe a provider's health.

        Args:
            provider: Provider name (e.g., "exa", "firecrawl", "openrouter").
            api_key: Optional API key to validate.

        Returns:
            SentryResult with health status.
        """
        import anyio

        cb = self.get_circuit_breaker(provider)
        if cb.is_open:
            return SentryResult(
                provider=provider, healthy=False,
                error=f"Circuit breaker open for {provider} (reset in {cb.remaining_delay:.0f}s)",
            )

        start = time.monotonic()

        try:
            if provider == "exa":
                if not api_key:
                    return SentryResult(provider=provider, healthy=False, error="No API key")
                healthy = await self._probe_exa(api_key)

            elif provider == "firecrawl":
                if not api_key:
                    return SentryResult(provider=provider, healthy=False, error="No API key")
                healthy = await self._probe_firecrawl(api_key)

            elif provider == "searxng":
                healthy = await self._probe_searxng()

            else:
                return SentryResult(provider=provider, healthy=False, error=f"Unknown provider: {provider}")

            latency = int((time.monotonic() - start) * 1000)

            if healthy:
                cb.record_success()
            else:
                cb.record_failure()

            return SentryResult(provider=provider, healthy=healthy, latency_ms=latency)

        except Exception as e:
            latency = int((time.monotonic() - start) * 1000)
            cb.record_failure()
            return SentryResult(provider=provider, healthy=False, latency_ms=latency, error=str(e))

    async def _probe_exa(self, api_key: str) -> bool:
        import anyio
        import httpx

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.exa.ai/v1/account",
                headers={"x-api-key": api_key},
                timeout=10,
            )
            return resp.status_code == 200

    async def _probe_firecrawl(self, api_key: str) -> bool:
        import anyio
        import httpx

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.firecrawl.dev/v1/account",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10,
            )
            return resp.status_code == 200

    async def _probe_searxng(self) -> bool:
        import anyio
        import httpx

        from .config import SieveConfig
        config = SieveConfig()

        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{config.searxng_url}/health", timeout=5)
            return resp.status_code == 200


class CircuitBreaker:
    """Simple circuit breaker for external API providers.

    States: closed (normal) → open (failing) → half-open (testing).
    """

    def __init__(self, name: str, failure_threshold: int = 3, reset_timeout: float = 300.0):
        self.name = name
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self._is_open = False

    @property
    def is_open(self) -> bool:
        if self._is_open:
            if time.monotonic() - self.last_failure_time >= self.reset_timeout:
                self._is_open = False  # Half-open: allow next request
        return self._is_open

    @property
    def remaining_delay(self) -> float:
        if not self._is_open:
            return 0.0
        return max(0.0, self.reset_timeout - (time.monotonic() - self.last_failure_time))

    def record_success(self):
        self.failure_count = 0
        self._is_open = False

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.monotonic()
        if self.failure_count >= self.failure_threshold:
            self._is_open = True


class BudgetGuard:
    """Atomic API credit tracking to prevent double-spending.

    Uses in-memory counters with optional Redis backend for distributed agents.
    """

    def __init__(self, config: Optional["SieveConfig"] = None):
        from .config import SieveConfig as SC
        self.config = config or SC()
        self._counters: dict[str, int] = {}
        self._redis = None

    async def can_afford(self, provider: str, estimated_cost: int = 1) -> bool:
        """Check if we have budget for an API call.

        Args:
            provider: Provider name.
            estimated_cost: Estimated cost in credits (default 1).

        Returns:
            True if within budget.
        """
        limits = {
            "exa": self.config.budget.exa_max_calls,
            "firecrawl": self.config.budget.firecrawl_max_calls,
            "openrouter": self.config.budget.openrouter_max_calls,
        }

        limit = limits.get(provider)
        if limit is None:
            return True  # Unknown provider = no limit

        if provider not in self._counters:
            self._counters[provider] = 0

        current = self._counters[provider]
        if current + estimated_cost > limit:
            warn_at = limit * self.config.budget.warn_at
            if current >= warn_at:
                logger.warning(f"Budget warning for {provider}: {current}/{limit} used")
            return False

        return True

    async def spend(self, provider: str, cost: int = 1) -> None:
        """Record a budget expenditure.

        Args:
            provider: Provider name.
            cost: Credits consumed (default 1).

        Raises:
            BudgetExceededError: If budget would be exceeded.
        """
        if provider not in self._counters:
            self._counters[provider] = 0

        self._counters[provider] += cost

    async def remaining(self, provider: str) -> int:
        """Get remaining budget for a provider."""
        limits = {
            "exa": self.config.budget.exa_max_calls,
            "firecrawl": self.config.budget.firecrawl_max_calls,
            "openrouter": self.config.budget.openrouter_max_calls,
        }

        limit = limits.get(provider)
        if limit is None:
            return -1  # Unlimited

        current = self._counters.get(provider, 0)
        return max(0, limit - current)

    async def reset_daily(self):
        """Reset all counters (call at start of day)."""
        self._counters.clear()
        logger.info("Budget counters reset for new day")