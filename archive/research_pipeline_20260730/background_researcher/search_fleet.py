# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — Search Fleet (Exa + Firecrawl)
# AP: AP-BACKGROUND-RESEARCHER-FLEET-v1.0.0
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ sovereign ⬡ search_fleet ⬡ WORKER
#
# Quota-managed cloud search providers with graceful fallback chain.
# Works alongside SearXNGClient for the sovereign (zero-cost) layer.
#
# NOTE: Tavily and Jina removed per D-kal-164 sovereign dependency purge.
#
# ⚠️ DEPRECATED — C-6' Unification (2026-07-25)
# This file contains a CircuitBreakerState dataclass and SearchCircuitBreaker
# that are CLONE implementations. Use HealthMonitor.get_breaker() instead:
#   breaker = get_health_monitor().get_breaker("search_fleet")
# The search fleet breaker was NOT migrated during Phase C-6'. New code
# MUST use HealthMonitor. Existing code should be migrated during P-5.
#
# LEGACY PORT: Circuit breaker pattern from Era 2 XNAi (xna-omega-legacy/src/omega/core/circuit_breakers/)
#   - Redis-backed state persistence with in-memory fallback
#   - Asymmetric thresholds: skip after N failures, critical after M failures
#   - Graceful degradation with fallback functions
#   - Full metrics for observability


# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
import logging
import time
from dataclasses import dataclass, field, asdict
from typing import Optional, Callable, Awaitable, Any

import anyio
import httpx2 as httpx

from omega.errors import (
    OmegaError,
    ProviderError, ProviderRateLimitError, ProviderAuthError,
    ProviderTimeoutError, ProviderUnavailableError, ProviderValidationError,
    ProviderSafetyError,
)
from .credit_budget import APICreditBudget, APICreditExhausted

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════
# §1 Circuit Breaker — Legacy XNAi Pattern Ported to Search Fleet
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class CircuitBreakerState:
    """State for a single provider's circuit breaker.
    
    Legacy XNAi pattern: asymmetric thresholds with skip/critical states.
    """
    consecutive_failures: int = 0
    total_failures: int = 0
    total_successes: int = 0
    last_failure_time: float = 0.0
    last_success_time: float = 0.0
    skip_until: float = 0.0
    degraded: bool = False
    critical: bool = False
    last_error: str = ""
    # Asymmetric thresholds: (skip_after_n_failures, critical_after_n_failures)
    skip_threshold: int = 3
    critical_threshold: int = 10

    @property
    def is_skipping(self) -> bool:
        """Whether the circuit breaker is currently skipping calls."""
        if not self.degraded:
            return False
        if time.time() < self.skip_until:
            return True
        # Skip window expired — reset
        self.degraded = False
        self.consecutive_failures = 0
        return False

    def record_success(self) -> None:
        """Record a successful call. Resets consecutive failures."""
        self.consecutive_failures = 0
        self.total_successes += 1
        self.last_success_time = time.time()
        self.degraded = False
        self.critical = False

    def record_failure(self, error: str = "") -> str:
        """Record a failure and return severity level: 'ok' | 'skip' | 'critical'."""
        self.consecutive_failures += 1
        self.total_failures += 1
        self.last_failure_time = time.time()
        self.last_error = error

        if self.consecutive_failures >= self.critical_threshold:
            self.critical = True
            self.degraded = True
            self.skip_until = time.time() + 3600  # 60 min skip
            logger.error(f"Circuit breaker CRITICAL for provider (skip 60min)")
            return "critical"

        if self.consecutive_failures >= self.skip_threshold:
            self.degraded = True
            self.skip_until = time.time() + 900  # 15 min skip
            logger.warning(f"Circuit breaker SKIP for provider (skip 15min)")
            return "skip"

        return "ok"

    def to_dict(self) -> dict:
        return asdict(self)


class SearchCircuitBreaker:
    """Manages circuit breaker state for all search providers.
    
    Providers tracked:
      - searxng (sovereign, zero-cost)
      - exa (cloud, semantic search)
      - firecrawl (cloud, deep extraction)
    
    Legacy XNAi features ported:
      - Per-provider state with asymmetric thresholds
      - Graceful degradation with fallback functions
      - Full metrics for observability
      - Singleton pattern for shared state across engine
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        # Provider configurations with asymmetric thresholds
        # SearXNG: more tolerant (local, no cost)
        # Exa/Firecrawl: stricter (cloud, cost per call)
        self.providers: dict[str, CircuitBreakerState] = {
            "searxng": CircuitBreakerState(
                skip_threshold=5,      # Skip after 5 failures
                critical_threshold=15, # Critical after 15 failures
            ),
            "exa": CircuitBreakerState(
                skip_threshold=3,      # Skip after 3 failures
                critical_threshold=10, # Critical after 10 failures
            ),
            "firecrawl": CircuitBreakerState(
                skip_threshold=3,      # Skip after 3 failures
                critical_threshold=10, # Critical after 10 failures
            ),
        }
        
        # Fallback functions for graceful degradation
        self._fallbacks: dict[str, Callable[[], Awaitable[Any]]] = {}
        
        # Metrics
        self._metrics = {
            "calls": 0,
            "failures": 0,
            "successes": 0,
            "blocked": 0,
            "fallbacks": 0,
        }
        
        self._lock = anyio.Lock()

    def register_fallback(self, provider: str, fallback: Callable[[], Awaitable[Any]]) -> None:
        """Register a fallback function for a provider."""
        self._fallbacks[provider] = fallback

    async def can_call(self, provider: str) -> bool:
        """Check if a provider is available (not skipping)."""
        async with self._lock:
            state = self.providers.get(provider)
            if not state:
                return True
            return not state.is_skipping

    async def record_success(self, provider: str) -> None:
        """Record a success for a provider."""
        async with self._lock:
            state = self.providers.get(provider)
            if state:
                state.record_success()
                self._metrics["successes"] += 1
            self._metrics["calls"] += 1

    async def record_failure(self, provider: str, error: str = "") -> str:
        """Record a failure. Returns severity: 'ok' | 'skip' | 'critical'."""
        async with self._lock:
            state = self.providers.get(provider)
            if not state:
                return "ok"
            severity = state.record_failure(error)
            self._metrics["failures"] += 1
            self._metrics["calls"] += 1
            return severity

    async def call_with_breaker(
        self,
        provider: str,
        func: Callable[[], Awaitable[Any]],
        fallback: Optional[Callable[[], Awaitable[Any]]] = None,
    ) -> Any:
        """Execute a function with circuit breaker protection.
        
        Args:
            provider: Provider name
            func: Async function to execute
            fallback: Optional fallback function (overrides registered fallback)
        
        Returns:
            Function result, or fallback result if circuit open
        
        Raises:
            ProviderUnavailableError: If circuit is critical and no fallback
        """
        async with self._lock:
            state = self.providers.get(provider)
            if not state:
                # Unknown provider — execute without protection
                return await func()
            
            # Check circuit state
            if state.is_skipping:
                self._metrics["blocked"] += 1
                self._metrics["calls"] += 1
                
                if state.critical:
                    # Critical — try fallback
                    fallback_fn = fallback or self._fallbacks.get(provider)
                    if fallback_fn:
                        self._metrics["fallbacks"] += 1
                        logger.warning(f"Circuit CRITICAL for {provider}, using fallback")
                        return await fallback_fn()
                    else:
                        raise ProviderUnavailableError(
                            f"Circuit breaker critical for {provider}, no fallback available"
                        )
                else:
                    # Skip mode — try fallback
                    fallback_fn = fallback or self._fallbacks.get(provider)
                    if fallback_fn:
                        self._metrics["fallbacks"] += 1
                        logger.warning(f"Circuit SKIP for {provider}, using fallback")
                        return await fallback_fn()
                    else:
                        raise ProviderUnavailableError(
                            f"Circuit breaker skipping {provider}, no fallback available"
                        )
        
        # Execute the function
        try:
            result = await func()
            await self.record_success(provider)
            return result
        except Exception as e:
            severity = await self.record_failure(provider, str(e))
            if severity == "critical":
                # Try fallback on critical failure
                fallback_fn = fallback or self._fallbacks.get(provider)
                if fallback_fn:
                    self._metrics["fallbacks"] += 1
                    logger.warning(f"Critical failure for {provider}, using fallback")
                    return await fallback_fn()
            raise

    def get_metrics(self) -> dict[str, Any]:
        """Get circuit breaker metrics for observability."""
        return {
            "global": self._metrics.copy(),
            "providers": {k: v.to_dict() for k, v in self.providers.items()},
        }

    async def reset(self, provider: Optional[str] = None) -> None:
        """Reset circuit breaker state for a provider or all providers."""
        async with self._lock:
            if provider:
                if provider in self.providers:
                    self.providers[provider] = CircuitBreakerState(
                        skip_threshold=self.providers[provider].skip_threshold,
                        critical_threshold=self.providers[provider].critical_threshold,
                    )
                    logger.info(f"Circuit breaker reset for {provider}")
            else:
                for name, state in self.providers.items():
                    self.providers[name] = CircuitBreakerState(
                        skip_threshold=state.skip_threshold,
                        critical_threshold=state.critical_threshold,
                    )
                self._metrics = {k: 0 for k in self._metrics}
                logger.info("All circuit breakers reset")


# ══════════════════════════════════════════════════════════════════════════
# §2 Search Fleet — Cloud Search Providers with Circuit Breaker
# ══════════════════════════════════════════════════════════════════════════


class SearchFleet:
    """Cloud search provider fleet with quota management, fallback, and circuit breaker."""

    def __init__(self, budget: APICreditBudget):
        self.budget = budget
        self.circuit_breaker = SearchCircuitBreaker()
        
        # Register fallbacks
        self.circuit_breaker.register_fallback("searxng", self._fallback_empty_list)
        self.circuit_breaker.register_fallback("exa", self._fallback_empty_list)
        self.circuit_breaker.register_fallback("firecrawl", self._fallback_none)

    async def _fallback_empty_list(self) -> list:
        """Fallback returning empty list."""
        return []

    async def _fallback_none(self) -> None:
        """Fallback returning None."""
        return None

    # ── Exa ─────────────────────────────────────────────────────────────────

    def _resolve_key(self, provider: str, env_var: str) -> str:
        """Resolve API key from vault."""
        try:
            from omega.vault import VaultCore
            vault = VaultCore()
            vault._load_sync()
            cred = vault._credentials.get(f"{provider}:api_key")
            if cred:
                return cred.encrypted_blob
        except (OmegaError, RuntimeError):
            pass
        return ""

    async def search_exa(self, query: str, num_results: int = 10) -> list[str]:
        """Semantic search via Exa. ~1 credit per call."""
        self.budget.consume("search")
        self.budget.increment_daily("search_ops")

        api_key = self._resolve_key("exa", "EXA_API_KEY")
        if not api_key:
            logger.warning("EXA_API_KEY not set")
            return []

        async def _do_search():
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    "https://api.exa.ai/search",
                    headers={"x-api-key": api_key},
                    json={
                        "query": query,
                        "num_results": num_results,
                        "type": "auto",
                        "highlights": True,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                return [r["url"] for r in data.get("results", [])]

        try:
            return await self.circuit_breaker.call_with_breaker("exa", _do_search)
        except ProviderUnavailableError:
            return []
        except (httpx.HTTPError, RuntimeError) as e:
            logger.error(f"Exa search failed: {e}", exc_info=True)
            await self.circuit_breaker.record_failure("exa", str(e))
            return []

    async def fetch_exa(self, url: str) -> Optional[str]:
        """Fetch content from a URL via Exa contents endpoint."""
        api_key = self._resolve_key("exa", "EXA_API_KEY")
        if not api_key:
            return None

        async def _do_fetch():
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    "https://api.exa.ai/contents",
                    headers={"x-api-key": api_key},
                    json={"urls": [url], "highlights": True, "text": True},
                )
                resp.raise_for_status()
                data = resp.json()
                results = data.get("results", [])
                if results:
                    return results[0].get("text", "")
                return None

        try:
            return await self.circuit_breaker.call_with_breaker("exa", _do_fetch)
        except ProviderUnavailableError:
            return None
        except (httpx.HTTPError, RuntimeError) as e:
            logger.error(f"Exa fetch failed for {url}: {e}", exc_info=True)
            await self.circuit_breaker.record_failure("exa", str(e))
            return None

    # ── Firecrawl ───────────────────────────────────────────────────────────

    async def extract_firecrawl(self, url: str) -> Optional[str]:
        """Deep content extraction via Firecrawl. ~1-2 credits per call."""
        self.budget.consume("firecrawl")
        self.budget.increment_daily("deep_extracts")

        api_key = self._resolve_key("firecrawl", "FIRECRAWL_API_KEY")
        if not api_key:
            logger.warning("FIRECRAWL_API_KEY not set")
            return None

        async def _do_extract():
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    "https://api.firecrawl.dev/v1/scrape",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={"url": url, "formats": ["markdown"]},
                )
                resp.raise_for_status()
                data = resp.json()
                return data.get("data", {}).get("markdown", "")

        try:
            return await self.circuit_breaker.call_with_breaker("firecrawl", _do_extract)
        except ProviderUnavailableError:
            return None
        except (httpx.HTTPError, RuntimeError) as e:
            logger.error(f"Firecrawl failed for {url}: {e}", exc_info=True)
            await self.circuit_breaker.record_failure("firecrawl", str(e))
            return None

    # ── Unified search with fallback ────────────────────────────────────────

    async def search_all(self, query: str, depth: int = 1) -> dict[str, list[str]]:
        """Search across multiple providers with depth-based strategy.

        Args:
            query: The search query
            depth: 1=light (SearXNG only), 2=standard (+ one cloud), 3=deep (+ all)

        Returns:
            dict with provider_name -> list of URL strings
        """
        results: dict[str, list[str]] = {}

        # SearXNG is always tried first (zero cost)
        from .searxng_client import SearXNGClient
        searxng = SearXNGClient()
        
        async def _searxng_search():
            return await searxng.search_text(query)

        try:
            searxng_results = await self.circuit_breaker.call_with_breaker("searxng", _searxng_search)
            if searxng_results:
                results["searxng"] = searxng_results
        except ProviderUnavailableError:
            pass
        except Exception as e:
            logger.error(f"SearXNG search failed: {e}", exc_info=True)
            await self.circuit_breaker.record_failure("searxng", str(e))

        # Cloud providers based on depth (Exa only — Tavily/Jina removed per D-kal-164)
        if depth >= 2:
            if self.budget.has_quota("search"):
                try:
                    urls = await self.search_exa(query)
                    if urls:
                        results["exa"] = urls
                except APICreditExhausted:
                    pass

        if depth >= 3:
            if "exa" not in results and self.budget.has_quota("search"):
                try:
                    urls = await self.search_exa(query, num_results=15)
                    if urls:
                        results["exa"] = urls
                except APICreditExhausted:
                    pass

        return results

    # ── Observability ───────────────────────────────────────────────────────

    def get_circuit_breaker_metrics(self) -> dict[str, Any]:
        """Get circuit breaker metrics for monitoring."""
        return self.circuit_breaker.get_metrics()

    async def reset_circuit_breakers(self, provider: Optional[str] = None) -> None:
        """Reset circuit breaker state."""
        await self.circuit_breaker.reset(provider)