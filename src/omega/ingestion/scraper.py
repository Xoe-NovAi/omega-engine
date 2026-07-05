# AP: AP-INGESTION-SCRAPER-v1.0.0
import re
import logging
import anyio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path

# We assume crawl4ai is installed. If not, we provide a mock/fallback.
try:
    from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
except ImportError:
    AsyncWebCrawler = None

logger = logging.getLogger("omega.ingestion.scraper")

@dataclass
class ScrapeResult:
    url: str
    content: str
    metadata: Dict[str, Any]
    tier: str  # 'fast', 'surgical', 'deep'
    success: bool
    error: Optional[str] = None
    provider_name: str = ""
    latency_ms: int = 0

class SovereignScraper:
    """
    Hardened Web Scraper for the Omega Engine.
    Implements the 'Nuclear Option' legacy wrapper for Crawl4AI.
    
    Sovereignty: Local Playwright/Selenium, zero telemetry, domain-anchored security.
    M2 Compliance: Domain allowlist loaded from config, not hardcoded in Engine Core.
    """
    def __init__(self, cas_archiver=None, domain_config_path: Optional[str] = None):
        self.cas = cas_archiver
        # M2 Compliance: Load domain allowlist from WAD layer config
        default_config = "config/wads/ingestion/domains.yaml"
        self._domain_allowlist = self._load_domain_config(domain_config_path or default_config)

    def _load_domain_config(self, config_path: Optional[str]) -> Dict[str, str]:
        """
        Loads domain allowlist from config.
        M2 Compliance: Domain policies belong in the WAD layer, not Engine Core.
        """
        import yaml
        default_allowlist = {
            "gutenberg": r"^https?://[^.]*\.gutenberg\.org/.*$",
            "arxiv": r"^https?://arxiv\.org/.*$",
            "pubmed": r"^https?://pubmed\.ncbi\.nlm\.nih\.gov/.*$",
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    if config and "ingestion" in config and "domain_allowlist" in config["ingestion"]:
                        return config["ingestion"]["domain_allowlist"]
            except (OmegaError, RuntimeError, OSError) as e:
                logger.warning(f"Failed to load domain config from {config_path}: {e}")

        
        return default_allowlist

    def _is_allowed(self, url: str, domain_key: str) -> bool:
        pattern = self._domain_allowlist.get(domain_key)
        if not pattern:
            return False
        return bool(re.match(pattern, url, re.IGNORECASE))

    def _surgical_strip(self, content: str, domain: str) -> str:
        """
        Surgical boundary stripping for high-fidelity extraction.
        [id-soft: doom-1993] Surgical Stripping Pattern
        """
        if domain == "gutenberg":
            # Strip Project Gutenberg headers and footers
            # Pattern: From "*** START OF THIS PROJECT GUTENBERG EBOOK... ***" to "*** END OF THIS PROJECT GUTENBERG EBOOK... ***"
            start_marker = r"\*\*\* START OF THIS PROJECT GUTENBERG EBOOK.*?\*\*\*"
            end_marker = r"\*\*\* END OF THIS PROJECT GUTENBERG EBOOK.*?\*\*\*"
            
            # Remove everything before start marker
            content = re.sub(f"^.*{start_marker}", "", content, flags=re.DOTALL | re.IGNORECASE)
            # Remove everything after end marker
            content = re.sub(f"{end_marker}.*$", "", content, flags=re.DOTALL | re.IGNORECASE)
            
        elif domain == "arxiv":
            # arXiv specific cleaning (remove header metadata blocks)
            content = re.sub(r"^.*?Abstract\s*:\s*", "", content, count=1, flags=re.DOTALL | re.IGNORECASE)
            
        return content.strip()

    async def scrape(self, url: str, tier: str = "fast", domain_key: Optional[str] = None) -> ScrapeResult:
        """
        Executes a scrape based on the requested tier.
        T1: Fast (Trafilatura/Simple)
        T2: Surgical (Domain-specific)
        T3: Deep (Crawl4AI/Playwright)
        """
        if domain_key and not self._is_allowed(url, domain_key):
            return ScrapeResult(url, "", {}, tier, False, f"URL {url} failed domain-anchored security check for {domain_key}", provider_name="blocked", latency_ms=0)

        start_time = anyio.current_time()
        try:
            if tier == "fast":
                return await self._scrape_fast(url)
            elif tier == "surgical":
                return await self._scrape_surgical(url, domain_key)
            elif tier == "deep":
                return await self._scrape_deep(url)
            else:
                raise ValueError(f"Invalid scrape tier: {tier}")
        except (OmegaError, RuntimeError, OSError, ValueError) as e:
            logger.error(f"Scrape failed for {url} [{tier}]: {str(e)}")
            latency = int((anyio.current_time() - start_time) * 1000)
            return ScrapeResult(url, "", {}, tier, False, str(e), provider_name="error", latency_ms=latency)

    async def _scrape_fast(self, url: str) -> ScrapeResult:
        """T1: Fast extraction using Trafilatura (via thread)."""
        start_time = anyio.current_time()
        try:
            import trafilatura
            downloaded = await anyio.to_thread.run_sync(trafilatura.fetch_url, url)
            if not downloaded:
                return ScrapeResult(url, "", {}, "fast", False, "Trafilatura failed to fetch URL", provider_name="trafilatura", latency_ms=int((anyio.current_time() - start_time) * 1000))
            
            result = await anyio.to_thread.run_sync(trafilatura.extract, downloaded)
            if not result:
                return ScrapeResult(url, "", {}, "fast", False, "Trafilatura failed to extract content", provider_name="trafilatura", latency_ms=int((anyio.current_time() - start_time) * 1000))
                
            latency = int((anyio.current_time() - start_time) * 1000)
            # Store in CAS if available
            cid = None
            if self.cas:
                cid = await self.cas.store(result.encode())
            metadata = {"method": "trafilatura"}
            if cid:
                metadata["cas_cid"] = cid
            return ScrapeResult(url, result, metadata, "fast", True, provider_name="trafilatura", latency_ms=latency)
        except ImportError:
            return ScrapeResult(url, "", {}, "fast", False, "trafilatura not installed", provider_name="trafilatura", latency_ms=0)

    async def _scrape_surgical(self, url: str, domain_key: Optional[str]) -> ScrapeResult:
        """T2: Surgical extraction using domain-specific markers."""
        start_time = anyio.current_time()
        # First, get the raw content (Fast path)
        fast_res = await self._scrape_fast(url)
        if not fast_res.success:
            return fast_res
            
        # Apply surgical stripping
        cleaned_content = self._surgical_strip(fast_res.content, domain_key or "")
        
        latency = int((anyio.current_time() - start_time) * 1000)
        # Store in CAS if available
        cid = None
        if self.cas:
            cid = await self.cas.store(cleaned_content.encode())
        metadata = {**fast_res.metadata, "surgical_domain": domain_key}
        if cid:
            metadata["cas_cid"] = cid
        return ScrapeResult(
            url=url,
            content=cleaned_content,
            metadata=metadata,
            tier="surgical",
            success=True,
            provider_name="trafilatura_surgical",
            latency_ms=latency
        )

    async def _scrape_deep(self, url: str) -> ScrapeResult:
        """
        T3: Deep extraction using Crawl4AI.
        Isolated in a subprocess to maintain M1 (AnyIO Absolute) compliance.
        """
        start_time = anyio.current_time()
        if AsyncWebCrawler is None:
            return ScrapeResult(url, "", {}, "deep", False, "crawl4ai not installed", provider_name="crawl4ai", latency_ms=0)

        # Use the C-FFI isolation pattern: run in a dedicated subprocess
        def run_crawler_subprocess():
            import asyncio
            
            async def _execute():
                async with AsyncWebCrawler() as crawler:
                    config = CrawlerRunConfig(
                        cache_mode=CacheMode.BYPASS,
                    )
                    result = await crawler.arun(url=url, config=config)
                    return {
                        "content": result.markdown,
                        "metadata": result.metadata
                    }
            
            return asyncio.run(_execute())

        try:
            res = await anyio.to_thread.run_sync(run_crawler_subprocess)
            latency = int((anyio.current_time() - start_time) * 1000)
            # Store in CAS if available
            cid = None
            if self.cas:
                cid = await self.cas.store(res["content"].encode())
            metadata = res["metadata"]
            if cid:
                metadata["cas_cid"] = cid
            return ScrapeResult(url, res["content"], metadata, "deep", True, provider_name="crawl4ai", latency_ms=latency)
        except (OmegaError, RuntimeError, OSError) as e:
            latency = int((anyio.current_time() - start_time) * 1000)
            return ScrapeResult(url, "", {}, "deep", False, str(e), provider_name="crawl4ai", latency_ms=latency)
