# 🔱 Omega Engine — Search Fleet (Exa + Firecrawl)
# AP: AP-BACKGROUND-RESEARCHER-FLEET-v1.0.0
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ sovereign ⬡ search_fleet ⬡ WORKER
#
# Quota-managed cloud search providers with graceful fallback chain.
# Works alongside SearXNGClient for the sovereign (zero-cost) layer.
#
# NOTE: Tavily and Jina removed per D-kal-164 sovereign dependency purge.

import logging
from omega.errors import (
    OmegaError, ProviderError, ProviderRateLimitError, ProviderAuthError,
    ProviderTimeoutError, ProviderUnavailableError, ProviderValidationError,
    ProviderSafetyError, InferenceError, InferenceOOMError, InferenceLoadError,
    InferenceRuntimeError, OmegaPersistenceError, SoulCorruptionError,
    SessionPersistenceError, StateIntegrityError, SovereignDiskFullError,
    ConfigError, WADError, BoundaryViolationError, InvariantViolationError,
    EntityTombstonedError, ModelNotFoundError,
)
import os
from typing import Optional

import httpx

from .credit_budget import APICreditBudget, APICreditExhausted

logger = logging.getLogger(__name__)


class SearchFleet:
    """Cloud search provider fleet with quota management and fallback."""

    def __init__(self, budget: APICreditBudget):
        self.budget = budget

    # ── Exa ─────────────────────────────────────────────────────────────────

    async def search_exa(self, query: str, num_results: int = 10) -> list[str]:
        """Semantic search via Exa. ~1 credit per call."""
        self.budget.consume("search")
        self.budget.increment_daily("search_ops")

        api_key = os.getenv("EXA_API_KEY", "")
        if not api_key:
            logger.warning("EXA_API_KEY not set")
            return []

        try:
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
        except OmegaError:
            return []
        except Exception as e:
            logger.error(f"Exa search failed: {e}", exc_info=True)
            return []

    async def fetch_exa(self, url: str) -> Optional[str]:
        """Fetch content from a URL via Exa contents endpoint."""
        api_key = os.getenv("EXA_API_KEY", "")
        if not api_key:
            return None
        try:
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
        except OmegaError:
            return None
        except Exception as e:
            logger.error(f"Exa fetch failed for {url}: {e}", exc_info=True)
            return None

    # ── Firecrawl ───────────────────────────────────────────────────────────

    async def extract_firecrawl(self, url: str) -> Optional[str]:
        """Deep content extraction via Firecrawl. ~1-2 credits per call."""
        self.budget.consume("firecrawl")
        self.budget.increment_daily("deep_extracts")

        api_key = os.getenv("FIRECRAWL_API_KEY", "")
        if not api_key:
            logger.warning("FIRECRAWL_API_KEY not set")
            return None

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    "https://api.firecrawl.dev/v1/scrape",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={"url": url, "formats": ["markdown"]},
                )
                resp.raise_for_status()
                data = resp.json()
                return data.get("data", {}).get("markdown", "")
        except OmegaError:
            return None
        except Exception as e:
            logger.error(f"Firecrawl failed for {url}: {e}", exc_info=True)
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
        searxng_results = await searxng.search_text(query)
        if searxng_results:
            results["searxng"] = searxng_results

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
