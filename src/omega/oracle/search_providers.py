"""Sovereign Search Providers — Direct API implementations for T2 and T4.
AP: AP-SEARCH-PROVIDERS-v1.0.0
ICS: [NODE: ARCHON | ARCHETYPE: HERMES | CONTEXT: SEARCH-HARDENING]
"""

import logging
import anyio
import httpx
from typing import Any, Dict, List, Optional
from omega.errors import ProviderError, ProviderAuthError, ProviderRateLimitError

logger = logging.getLogger(__name__)

class SearchProvider:
    """Base class for all sovereign search providers."""
    async def search(self, query: str, limit: int = 10) -> Optional[str]:
        raise NotImplementedError

class FirecrawlProvider(SearchProvider):
    """T2: Firecrawl Deep Extraction Provider."""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.firecrawl.dev/v1"

    async def search(self, query: str, limit: int = 10) -> Optional[str]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
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
                
                data = response.json()
                results = data.get("data", [])
                if not results:
                    return None
                
                # Synthesize results into a finding
                snippets = [r.get("markdown", r.get("content", ""))[:500] for r in results]
                return f"Firecrawl Deep Extraction: {'\\n\\n'.join(snippets[:3])}"
            except httpx.HTTPStatusError as e:
                logger.error(f"Firecrawl HTTP error: {e}")
                raise ProviderError(f"Firecrawl API failure: {e}")
            except Exception as e:
                logger.error(f"Firecrawl unexpected error: {e}")
                raise ProviderError(f"Firecrawl system failure: {e}")

class ExaProvider(SearchProvider):
    """T4: Neural Search (Exa) Provider."""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.exa.ai/search"

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
