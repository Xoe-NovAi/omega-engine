# 🔱 Omega Engine — Search Fleet (Exa + Tavily + Jina + Firecrawl)
# AP: AP-BACKGROUND-RESEARCHER-FLEET-v1.0.0
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ sovereign ⬡ search_fleet ⬡ WORKER
#
# Quota-managed cloud search providers with graceful fallback chain.
# Works alongside SearXNGClient for the sovereign (zero-cost) layer.

import logging
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
        except Exception as e:
            logger.warning(f"Exa search failed: {e}")
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
        except Exception as e:
            logger.warning(f"Exa fetch failed for {url}: {e}")
            return None

    # ── Tavily ──────────────────────────────────────────────────────────────

    async def search_tavily(self, query: str, max_results: int = 8) -> list[str]:
        """RAG-optimized search via Tavily. ~1 credit per call."""
        self.budget.consume("search")
        self.budget.increment_daily("search_ops")

        api_key = os.getenv("TAVILY_API_KEY", "")
        if not api_key:
            logger.warning("TAVILY_API_KEY not set")
            return []

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    "https://api.tavily.com/search",
                    headers={
                        "Content-Type": "application/json",
                    },
                    json={
                        "api_key": api_key,
                        "query": query,
                        "max_results": max_results,
                        "search_depth": "advanced",
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                return [r["url"] for r in data.get("results", [])]
        except Exception as e:
            logger.warning(f"Tavily search failed: {e}")
            return []

    # ── Jina ────────────────────────────────────────────────────────────────

    async def search_jina(self, query: str, max_results: int = 10) -> list[str]:
        """Web search via Jina Reader API."""
        self.budget.consume("jina")
        self.budget.increment_daily("search_ops")

        api_key = os.getenv("JINA_API_KEY", "")
        if not api_key:
            logger.warning("JINA_API_KEY not set")
            return []

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    f"https://s.jina.ai/{query}",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "X-Retain-Images": "none",
                    },
                )
                resp.raise_for_status()
                text = resp.text
                # Parse URLs from the Jina Reader markdown response
                import re
                urls = re.findall(r"\[.*?\]\((https?://[^\s)]+)\)", text)
                return urls[:max_results]
        except Exception as e:
            logger.warning(f"Jina search failed: {e}")
            return []

    async def read_url_jina(self, url: str) -> Optional[str]:
        """Read URL content via Jina Reader API."""
        api_key = os.getenv("JINA_API_KEY", "")
        if not api_key:
            return None
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(
                    f"https://r.jina.ai/{url}",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "X-Retain-Images": "none",
                        "X-With-Links-Summary": "false",
                    },
                )
                resp.raise_for_status()
                return resp.text
        except Exception as e:
            logger.warning(f"Jina read failed for {url}: {e}")
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
        except Exception as e:
            logger.warning(f"Firecrawl failed for {url}: {e}")
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

        # Cloud providers based on depth
        if depth >= 2:
            # Try one provider at a time
            for provider in ("tavily", "jina", "exa"):
                if self.budget.has_quota("search"):
                    try:
                        if provider == "tavily":
                            urls = await self.search_tavily(query)
                        elif provider == "jina":
                            urls = await self.search_jina(query)
                        else:
                            urls = await self.search_exa(query)
                        if urls:
                            results[provider] = urls
                            break  # One cloud provider is enough for depth=2
                    except APICreditExhausted:
                        continue

        if depth >= 3:
            # Deep: try all remaining providers
            for provider in ("exa", "jina", "tavily"):
                if provider not in results and self.budget.has_quota("search"):
                    try:
                        if provider == "exa":
                            urls = await self.search_exa(query, num_results=15)
                        elif provider == "jina":
                            urls = await self.search_jina(query, max_results=15)
                        else:
                            urls = await self.search_tavily(query, max_results=12)
                        if urls:
                            results[provider] = urls
                    except APICreditExhausted:
                        continue

        return results
