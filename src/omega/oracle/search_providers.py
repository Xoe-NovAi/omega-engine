"""Sovereign Search Providers — Direct API implementations for T2 and T4.
# [id-soft: quake3-1999] Right Approximation — optimized search provider chain
AP: AP-SEARCH-PROVIDERS-v1.0.0
ICS: [NODE: ARCHON | ARCHETYPE: HERMES | CONTEXT: SEARCH-HARDENING]
"""

import logging
import anyio
import httpx
from typing import Any, Dict, List, Optional
from omega.errors import ProviderError, ProviderAuthError, ProviderRateLimitError
import json

logger = logging.getLogger(__name__)

class SearchProvider:
    """Base class for all sovereign search providers."""
    async def search(self, query: str, limit: int = 10) -> Optional[str]:
        raise NotImplementedError

class FirecrawlProvider(SearchProvider):
    """T2: Firecrawl Deep Extraction Provider."""
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or self._resolve_from_vault()
        self.base_url = "https://api.firecrawl.dev/v1"
    
    @staticmethod
    def _resolve_from_vault() -> str:
        """Fallback to vault if no key passed explicitly."""
        try:
            from omega.vault import KeyVault
            return KeyVault().resolve("firecrawl")
        except Exception:
            return os.environ.get("FIRECRAWL_API_KEY", "")

    async def search(self, query: str, limit: int = 10) -> Optional[str]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # 1. Search for relevant URLs
                response = await client.post(
                    f"{self.base_url}/search",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={"query": query, "limit": limit}
                )
                if response.status_code == 401:
                    raise ProviderAuthError("Firecrawl API key invalid")
                if response.status_code == 429:
                    raise ProviderRateLimitError("Firecrawl rate limit exceeded")
                response.raise_for_status()
                
                search_data = response.json()
                results = search_data.get("data", [])
                if not results:
                    return None
                
                # 2. Scrape the top results for actual content (Deep Extraction)
                content_snippets = []
                for res in results[:3]: # Scrape top 3 for efficiency
                    url = res.get("url")
                    if not url:
                        continue
                    try:
                        scrape_res = await client.post(
                            f"{self.base_url}/scrape",
                            headers={"Authorization": f"Bearer {self.api_key}"},
                            json={"url": url, "formats": ["markdown"]}
                        )
                        if scrape_res.status_code == 200:
                            scrape_data = scrape_res.json()
                            markdown = scrape_data.get("data", {}).get("markdown", "")
                            if markdown:
                                content_snippets.append(f"Source [{url}]:\n{markdown[:1000]}")
                    except Exception as e:
                        logger.warning(f"Failed to scrape {url}: {e}")
                
                if not content_snippets:
                    # Fallback to descriptions if scraping fails
                    snippets = [r.get("description", "")[:500] for r in results]
                    return f"Firecrawl Search (Snippets): {'\n\n'.join(snippets[:3])}"
                
                return f"Firecrawl Deep Extraction:\n\n" + "\n\n---\n\n".join(content_snippets)
            except httpx.HTTPStatusError as e:

                logger.error(f"Firecrawl HTTP error: {e}")
                raise ProviderError(f"Firecrawl API failure: {e}")
            except Exception as e:
                logger.error(f"Firecrawl unexpected error: {e}")
                raise ProviderError(f"Firecrawl system failure: {e}")

class ExaProvider(SearchProvider):
    """T4: Neural Search (Exa) Provider."""
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or self._resolve_from_vault()
        self.base_url = "https://api.exa.ai/search"
    
    @staticmethod
    def _resolve_from_vault() -> str:
        """Fallback to vault if no key passed explicitly."""
        try:
            from omega.vault import KeyVault
            return KeyVault().resolve("exa")
        except Exception:
            return os.environ.get("EXA_API_KEY", "")

    async def search(self, query: str, limit: int = 10) -> Optional[str]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    self.base_url,
                    headers={"x-api-key": self.api_key},
                    json={"query": query, "numResults": limit, "useAutoprompt": True}
                )
                if response.status_code == 401:
                    raise ProviderAuthError("Exa API key invalid")
                if response.status_code == 429:
                    raise ProviderRateLimitError("Exa rate limit exceeded")
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"Exa raw response: {json.dumps(data)}")
                results = data.get("results", [])
                if not results:
                    return None
                
                snippets = [r.get("text", r.get("highlights", ""))[:500] for r in results]
                return f"Exa Neural Search: {'\\n\\n'.join(snippets[:3])}"
            except httpx.HTTPStatusError as e:
                logger.error(f"Exa HTTP error: {e}")
                raise ProviderError(f"Exa API failure: {e}")
            except Exception as e:
                logger.error(f"Exa unexpected error: {e}")
                raise ProviderError(f"Exa system failure: {e}")
