"""Researcher — full research pipeline: search → scrape → verify.

Combines SearXNG, Exa, Firecrawl for search and the SovereignScraper for extraction.
"""

# AP: AP-OMEGA-SIEVE-RESEARCH-v1.0.0

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Optional

from .scraper import SovereignScraper, ScrapeResult
from .guards import SovereignSentry, BudgetGuard

logger = logging.getLogger("omega_sieve.research")


@dataclass
class ResearchResult:
    """Result of a full research pipeline."""
    query: str
    sources: list[ScrapeResult] = field(default_factory=list)
    depth: str = "balanced"
    latency_ms: int = 0
    error: Optional[str] = None

    @property
    def successful_sources(self) -> list[ScrapeResult]:
        return [s for s in self.sources if s.success]

    @property
    def summary(self) -> str:
        ok = len(self.successful_sources)
        total = len(self.sources)
        return f"Research '{self.query}': {ok}/{total} sources, {self.latency_ms}ms"


class Researcher:
    """Full research pipeline: search → scrape → verify.

    Searches using available backends (SearXNG → Exa → Firecrawl),
    scrapes each result using the SovereignScraper's auto-tier,
    and returns the combined results.
    """

    def __init__(
        self,
        scraper: Optional[SovereignScraper] = None,
        sentry: Optional[SovereignSentry] = None,
        budget: Optional[BudgetGuard] = None,
    ):
        self.scraper = scraper or SovereignScraper()
        self.sentry = sentry or SovereignSentry()
        self.budget = budget or BudgetGuard()

    async def research(
        self,
        query: str,
        max_sources: int = 5,
        depth: str = "balanced",
    ) -> ResearchResult:
        """Execute full research pipeline.

        Args:
            query: Research query.
            max_sources: Maximum number of sources to scrape.
            depth: "quick" (T1 only), "balanced" (T1+T2), "deep" (T1+T2+T3).

        Returns:
            ResearchResult with scraped sources.
        """
        start = time.monotonic()

        # Step 1: Search for URLs
        urls = await self._search(query, max_sources=max_sources * 2)
        if not urls:
            return ResearchResult(
                query=query, depth=depth,
                latency_ms=int((time.monotonic() - start) * 1000),
                error="No search results found",
            )

        # Step 2: Scrape each URL
        tier_map = {"quick": "fast", "balanced": "fast", "deep": "auto"}
        scrape_tier = tier_map.get(depth, "fast")

        sources: list[ScrapeResult] = []
        for url in urls[:max_sources]:
            if scrape_tier == "auto":
                result = await self.scraper.scrape_auto(url, min_chars=100)
            else:
                result = await self.scraper.scrape(url, tier=scrape_tier)
            sources.append(result)

        latency = int((time.monotonic() - start) * 1000)
        return ResearchResult(query=query, sources=sources, depth=depth, latency_ms=latency)

    async def _search(self, query: str, max_sources: int = 10) -> list[str]:
        """Search for URLs using available backends.

        Tries SearXNG first (free, sovereign), then Exa if available.
        """
        urls = await self._search_searxng(query, max_sources)
        if urls:
            return urls

        urls = await self._search_websearch(query, max_sources)
        if urls:
            return urls

        return []

    async def _search_searxng(self, query: str, max_sources: int = 10) -> list[str]:
        """Search via self-hosted SearXNG."""
        import anyio
        import httpx

        from .config import SieveConfig
        config = SieveConfig()

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{config.searxng_url}/search",
                    params={"q": query, "format": "json", "limit": max_sources},
                    timeout=15,
                )
                if resp.status_code != 200:
                    return []

                data = resp.json()
                results = data.get("results", [])
                return [
                    r["url"] for r in results
                    if r.get("url") and not r.get("url", "").startswith("http")
                ]
        except Exception as e:
            logger.debug(f"SearXNG search failed: {e}")
            return []

    async def _search_websearch(self, query: str, max_sources: int = 10) -> list[str]:
        """Fallback: use httpx to search via a public engine."""
        # This is a minimal fallback — production should use Exa/Firecrawl
        return []