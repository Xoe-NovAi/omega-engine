"""omega-sieve — Sovereign-Sieve: T1→T2→T3 tiered web research & extraction.

One command to research anything. Your computer. Your data. No cloud required.
Falls back gracefully when you DO have API keys (Exa, Firecrawl).

Core pipeline:
    T1 (Fast/Trafilatura) → T2 (Surgical/Domain-specific) → T3 (Deep/Crawl4AI)
    ↕ TriangulationVerifier (hallucination guard)

Usage:
    from omega_sieve import research, scrape

    results = research("latest LLM quantization methods")
    text = scrape("https://example.com/article")
"""

__version__ = "0.1.0"

from .scraper import SovereignScraper, ScrapeResult, T1Scraper, T2Scraper, T3Scraper
from .verifier import TriangulationVerifier, VerificationResult
from .guards import SovereignSentry, BudgetGuard
from .proxy import SovereignProxyPool, ProxyConfig
from .youtube import YouTubeSieve, YouTubeResult
from .config import SieveConfig, load_config

__all__ = [
    # Core scraper
    "SovereignScraper",
    "ScrapeResult",
    "T1Scraper",
    "T2Scraper",
    "T3Scraper",
    # Verification
    "TriangulationVerifier",
    "VerificationResult",
    # Guards
    "SovereignSentry",
    "BudgetGuard",
    # Proxy
    "SovereignProxyPool",
    "ProxyConfig",
    # YouTube
    "YouTubeSieve",
    "YouTubeResult",
    # Config
    "SieveConfig",
    "load_config",
    # Convenience functions
    "research",
    "scrape",
]

# Convenience: single-function API
_default_scraper: SovereignScraper | None = None


def _get_scraper() -> SovereignScraper:
    global _default_scraper
    if _default_scraper is None:
        _default_scraper = SovereignScraper()
    return _default_scraper


async def scrape(url: str, tier: str = "auto") -> ScrapeResult:
    """Scrape a URL with auto tier-selection.

    Args:
        url: The URL to scrape.
        tier: Extraction tier — "auto", "fast", "surgical", or "deep".
              "auto" starts at T1 and escalates if content is insufficient.

    Returns:
        ScrapeResult with content and metadata.
    """
    scraper = _get_scraper()
    if tier == "auto":
        return await scraper.scrape_auto(url)
    return await scraper.scrape(url, tier=tier)


async def research(
    query: str,
    max_sources: int = 5,
    depth: str = "balanced",
) -> list[ScrapeResult]:
    """Run a full research pipeline: search → scrape → verify.

    Args:
        query: Research query.
        max_sources: Maximum number of sources to scrape.
        depth: Research depth — "quick" (T1 only), "balanced" (T1+T2), "deep" (T1+T2+T3).

    Returns:
        List of scraped and verified results.
    """
    from .research import Researcher

    researcher = Researcher(scraper=_get_scraper())
    return await researcher.research(query, max_sources=max_sources, depth=depth)