"""SovereignScraper — T1→T2→T3 tiered web extraction.

Tiers:
    T1 (Fast): Trafilatura for clean article extraction — ~2s, no JS.
    T2 (Surgical): Domain-specific extraction with boundary markers — ~3s.
    T3 (Deep): Crawl4AI with Playwright JS rendering — ~10-30s.

All tiers are optional. The scraper degrades gracefully if a dependency is missing.
"""

# AP: AP-OMEGA-SIEVE-SCRAPER-v1.0.0

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .errors import ScrapeError
from .config import SieveConfig

logger = logging.getLogger("omega_sieve.scraper")


@dataclass
class ScrapeResult:
    """Result of a scrape operation."""
    url: str
    content: str
    tier: str  # "fast" | "surgical" | "deep"
    success: bool
    error: Optional[str] = None
    provider_name: str = ""
    latency_ms: int = 0
    metadata: dict = field(default_factory=dict)

    @property
    def is_empty(self) -> bool:
        return not self.content.strip()

    def __bool__(self) -> bool:
        return self.success and not self.is_empty


class T1Scraper:
    """T1: Fast extraction using Trafilatura."""

    def __init__(self):
        self._available: Optional[bool] = None

    @property
    def available(self) -> bool:
        if self._available is None:
            try:
                import trafilatura  # noqa: F401
                self._available = True
            except ImportError:
                self._available = False
        return self._available

    async def scrape(self, url: str) -> ScrapeResult:
        """Extract clean text using Trafilatura."""
        import anyio

        start = time.monotonic()
        try:
            import trafilatura

            downloaded = await anyio.to_thread.run_sync(trafilatura.fetch_url, url)
            if not downloaded:
                return ScrapeResult(
                    url=url, content="", tier="fast", success=False,
                    error="Trafilatura failed to fetch URL",
                    provider_name="trafilatura",
                    latency_ms=int((time.monotonic() - start) * 1000),
                )

            result = await anyio.to_thread.run_sync(trafilatura.extract, downloaded)
            if not result:
                return ScrapeResult(
                    url=url, content="", tier="fast", success=False,
                    error="Trafilatura extracted no content",
                    provider_name="trafilatura",
                    latency_ms=int((time.monotonic() - start) * 1000),
                )

            latency = int((time.monotonic() - start) * 1000)
            return ScrapeResult(
                url=url, content=result, tier="fast", success=True,
                provider_name="trafilatura", latency_ms=latency,
                metadata={"method": "trafilatura"},
            )

        except ImportError:
            return ScrapeResult(
                url=url, content="", tier="fast", success=False,
                error="trafilatura not installed (pip install omega-sieve[fast])",
                provider_name="trafilatura",
                latency_ms=int((time.monotonic() - start) * 1000),
            )
        except Exception as e:
            return ScrapeResult(
                url=url, content="", tier="fast", success=False,
                error=str(e), provider_name="trafilatura",
                latency_ms=int((time.monotonic() - start) * 1000),
            )


class T2Scraper:
    """T2: Surgical extraction using domain-specific markers."""

    def __init__(self, domain_rules: Optional[dict[str, str]] = None):
        self._t1 = T1Scraper()
        self.domain_rules = domain_rules or {
            "gutenberg": {
                "start": r"\*\*\* START OF (?:THIS )?PROJECT GUTENBERG EBOOK.*?\*\*\*",
                "end": r"\*\*\* END OF (?:THIS )?PROJECT GUTENBERG EBOOK.*?\*\*\*",
            },
        }

    @property
    def available(self) -> bool:
        return self._t1.available

    def _identify_domain(self, url: str) -> Optional[str]:
        """Identify domain key from URL."""
        for key, pattern in {
            "gutenberg": r"gutenberg\.org",
            "arxiv": r"arxiv\.org",
            "pubmed": r"pubmed\.ncbi\.nlm\.nih\.gov",
            "wikipedia": r"wikipedia\.org",
            "github": r"github\.com",
        }.items():
            if re.search(pattern, url, re.IGNORECASE):
                return key
        return None

    def _surgical_strip(self, content: str, domain_key: str) -> str:
        """Apply domain-specific boundary stripping."""
        rules = self.domain_rules.get(domain_key)
        if not rules:
            return content.strip()

        if "start" in rules:
            content = re.sub(f"^.*?{rules['start']}", "", content, flags=re.DOTALL | re.IGNORECASE)
        if "end" in rules:
            content = re.sub(f"{rules['end']}.*$", "", content, flags=re.DOTALL | re.IGNORECASE)

        if domain_key == "arxiv":
            content = re.sub(r"^.*?Abstract\s*:\s*", "", content, count=1, flags=re.DOTALL | re.IGNORECASE)

        return content.strip()

    async def scrape(self, url: str) -> ScrapeResult:
        """Extract with domain-specific surgical stripping."""
        import anyio

        start = time.monotonic()

        # Start with T1
        t1_result = await self._t1.scrape(url)
        if not t1_result.success:
            return t1_result

        domain_key = self._identify_domain(url)
        if not domain_key:
            # No specific domain rules — return T1 result as-is
            return t1_result

        cleaned = self._surgical_strip(t1_result.content, domain_key)
        latency = int((time.monotonic() - start) * 1000)

        return ScrapeResult(
            url=url, content=cleaned, tier="surgical", success=True,
            provider_name="trafilatura_surgical", latency_ms=latency,
            metadata={**t1_result.metadata, "domain_key": domain_key},
        )


class T3Scraper:
    """T3: Deep extraction using Crawl4AI with Playwright JS rendering."""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self._available: Optional[bool] = None

    @property
    def available(self) -> bool:
        if self._available is None:
            try:
                from crawl4ai import AsyncWebCrawler  # noqa: F401
                self._available = True
            except ImportError:
                self._available = False
        return self._available

    async def scrape(self, url: str) -> ScrapeResult:
        """Extract with Crawl4AI in an isolated subprocess."""
        import anyio
        import multiprocessing
        from multiprocessing import Queue

        start = time.monotonic()

        if not self.available:
            return ScrapeResult(
                url=url, content="", tier="deep", success=False,
                error="crawl4ai not installed (pip install omega-sieve[full])",
                provider_name="crawl4ai",
                latency_ms=int((time.monotonic() - start) * 1000),
            )

        result_queue: Queue = Queue()

        def _run_crawler(q: Queue, target_url: str, timeout_s: int):
            """Run crawler in isolated process to protect event loop."""
            try:
                import anyio as _anyio
                from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode

                async def _execute():
                    async with AsyncWebCrawler() as crawler:
                        config = CrawlerRunConfig(
                            cache_mode=CacheMode.BYPASS,
                        )
                        result = await crawler.arun(url=target_url, config=config)
                        md = str(result.markdown) if result.markdown else ""
                        meta = dict(result.metadata) if result.metadata else {}
                        return {"content": md, "metadata": meta, "error": None}

                res = _anyio.run(_execute)
                q.put(res)

            except Exception as e:
                q.put({"content": "", "metadata": {}, "error": str(e)})

        try:
            process = multiprocessing.Process(
                target=_run_crawler, args=(result_queue, url, self.timeout)
            )
            process.start()
            process.join(timeout=self.timeout)

            if process.is_alive():
                process.terminate()
                process.join(timeout=5)
                raise TimeoutError(f"Deep scrape exceeded {self.timeout}s timeout")

            if result_queue.empty():
                raise RuntimeError("Crawler process returned no result")

            res = result_queue.get_nowait()
            if res.get("error"):
                raise RuntimeError(f"Crawler error: {res['error']}")

            latency = int((time.monotonic() - start) * 1000)
            return ScrapeResult(
                url=url, content=res["content"], tier="deep", success=True,
                provider_name="crawl4ai", latency_ms=latency,
                metadata=res.get("metadata", {}),
            )

        except Exception as e:
            latency = int((time.monotonic() - start) * 1000)
            return ScrapeResult(
                url=url, content="", tier="deep", success=False,
                error=str(e), provider_name="crawl4ai", latency_ms=latency,
            )


class SovereignScraper:
    """Unified scraper with automatic tier selection.

    Usage:
        scraper = SovereignScraper()
        result = await scraper.scrape_auto("https://example.com")
        if result:
            print(result.content)
    """

    def __init__(self, config: Optional[SieveConfig] = None):
        self.config = config or SieveConfig()
        self.t1 = T1Scraper()
        self.t2 = T2Scraper()
        self.t3 = T3Scraper()

    async def scrape(self, url: str, tier: str = "fast") -> ScrapeResult:
        """Scrape with a specific tier.

        Args:
            url: Target URL.
            tier: One of "fast" (T1), "surgical" (T2), "deep" (T3).

        Returns:
            ScrapeResult.
        """
        if tier == "fast":
            return await self.t1.scrape(url)
        elif tier == "surgical":
            return await self.t2.scrape(url)
        elif tier == "deep":
            return await self.t3.scrape(url)
        else:
            raise ScrapeError(f"Unknown tier: {tier}. Use: fast, surgical, deep")

    async def scrape_auto(self, url: str, min_chars: int = 200) -> ScrapeResult:
        """Auto-tier: start at T1, escalate if content is insufficient.

        Strategy:
            T1 (Trafilatura) → if empty, try T2 (Surgical) → if still empty, T3 (Crawl4AI)

        Args:
            url: Target URL.
            min_chars: Minimum content length to consider successful.

        Returns:
            Best ScrapeResult from the attempted tiers.
        """
        # T1: Fast
        result = await self.t1.scrape(url)
        if result and len(result.content) >= min_chars:
            return result

        # T2: Surgical
        result = await self.t2.scrape(url)
        if result and len(result.content) >= min_chars:
            return result

        # T3: Deep (JS rendering)
        result = await self.t3.scrape(url)
        return result

    async def scrape_all(self, url: str) -> dict[str, ScrapeResult]:
        """Run all tiers and return results as a dict keyed by tier name."""
        return {
            "fast": await self.t1.scrape(url),
            "surgical": await self.t2.scrape(url),
            "deep": await self.t3.scrape(url),
        }

    @property
    def available_tiers(self) -> list[str]:
        """List available tiers based on installed dependencies."""
        tiers = []
        if self.t1.available:
            tiers.append("fast")
        if self.t2.available:
            tiers.append("surgical")
        if self.t3.available:
            tiers.append("deep")
        return tiers