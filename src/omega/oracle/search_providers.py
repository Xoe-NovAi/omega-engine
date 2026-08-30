# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Sovereign Search Providers — Direct API implementations for T2 and T4.
# [id-soft: vet-002] Right Approximation — fast heuristic search provider chain
# [heritage: searxng 2023] SearXNG — self-hosted metasearch (Tier 1 privacy-first search)
# [heritage: cloudflare-warp 2021] WARP proxy pool — multi-namespace privacy proxy
AP: AP-SEARCH-PROVIDERS-v1.0.0
ICS: [NODE: ARCHON | ARCHETYPE: HERMES | CONTEXT: SEARCH-HARDENING]
"""
# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md

import logging
import anyio
import httpx2 as httpx
import os
from typing import Dict, List, Optional
from omega.errors import OmegaError, ProviderError, ProviderAuthError, ProviderRateLimitError
from omega.observability.bleg import BLEGMiddleware

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
            from omega.vault import VaultCore

            vault = VaultCore()
            vault._load_sync()
            cred = vault._credentials.get("firecrawl:api_key")
            return cred.encrypted_blob if cred else ""
        except (OmegaError, RuntimeError, OSError) as e:
            logger.debug(f"Firecrawl key fallback failed: {e}")
            return ""

    async def search(self, query: str, limit: int = 10) -> Optional[str]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # 1. Search for relevant URLs
                response = await client.post(
                    f"{self.base_url}/search",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={"query": query, "limit": limit},
                )
                if response.status_code == 401:
                    raise ProviderAuthError("firecrawl", "Firecrawl API key invalid")
                if response.status_code == 429:
                    raise ProviderRateLimitError("firecrawl", "Firecrawl rate limit exceeded")
                response.raise_for_status()
                # [IW-3] BLEG: inspect 200 OK bodies for error signatures
                BLEGMiddleware().inspect(
                    status_code=response.status_code,
                    body=response.text,
                    provider="firecrawl",
                    trace_id="unknown",
                    url=str(response.url),
                )

                search_data = response.json()
                results = search_data.get("data", [])
                if not results:
                    return None

                # 2. Scrape the top results for actual content (Deep Extraction)
                content_snippets = []
                for res in results[:3]:  # Scrape top 3 for efficiency
                    url = res.get("url")
                    if not url:
                        continue
                    try:
                        scrape_res = await client.post(
                            f"{self.base_url}/scrape",
                            headers={"Authorization": f"Bearer {self.api_key}"},
                            json={"url": url, "formats": ["markdown"]},
                        )
                        if scrape_res.status_code == 200:
                            scrape_data = scrape_res.json()
                            markdown = scrape_data.get("data", {}).get("markdown", "")
                            if markdown:
                                content_snippets.append(f"Source [{url}]:\n{markdown[:1000]}")
                    except (OmegaError, RuntimeError, OSError) as e:
                        logger.warning(f"Failed to scrape {url}: {e}")

                if not content_snippets:
                    # Fallback to descriptions if scraping fails
                    snippets = [r.get("description", "")[:500] for r in results]
                    return f"Firecrawl Search (Snippets): {'\n\n'.join(snippets[:3])}"

                return f"Firecrawl Deep Extraction:\n\n" + "\n\n---\n\n".join(content_snippets)
            except ProviderError:
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"Firecrawl HTTP error: {e}")
                raise ProviderError("firecrawl", f"Firecrawl API failure: {e}")
            except (OmegaError, RuntimeError, OSError) as e:
                logger.error(f"Firecrawl unexpected error: {e}")
                raise ProviderError("firecrawl", f"Firecrawl system failure: {e}")


class SearXNGProvider(SearchProvider):
    """T1: SearXNG Broad Discovery Provider — privacy-first metasearch."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: float = 15.0,
        retries: int = 2,
        retry_delays: Optional[List[float]] = None,
    ):
        self.base_url = (
            base_url or os.environ.get("SEARXNG_BASE_URL", "http://127.0.0.1:8017")
        ).rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.retry_delays = retry_delays or [5.0, 10.0]

    async def search(
        self,
        query: str,
        limit: int = 10,
        categories: str = "general",
        engines: str = "",
        language: str = "auto",
    ) -> Optional[str]:
        form_data: Dict[str, str] = {
            "q": query,
            "format": "json",
            "language": language,
            "categories": categories,
            "pageno": "1",
        }
        if engines:
            form_data["engines"] = engines

        last_error: Optional[Exception] = None
        for attempt in range(self.retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(
                        f"{self.base_url}/search",
                        data=form_data,
                    )
                    resp.raise_for_status()
                    data = resp.json()

                    results = data.get("results", [])
                    if not results:
                        suggestions = data.get("suggestions", [])
                        if suggestions:
                            return f"SearXNG suggestions: {', '.join(suggestions)}"
                        return None

                    snippets = []
                    for r in results[:limit]:
                        title = r.get("title", "")
                        url = r.get("url", "")
                        content = r.get("content", "")
                        engine = r.get("engine", "unknown")
                        if content:
                            snippets.append(f"Source [{url}] ({engine}):\n{content[:500]}")

                    if not snippets:
                        return None

                    return f"SearXNG Search ({len(results)} results):\n\n" + "\n\n---\n\n".join(
                        snippets[:5]
                    )

            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code in (429, 502, 503, 504):
                    delay = (
                        self.retry_delays[attempt]
                        if attempt < len(self.retry_delays)
                        else self.retry_delays[-1]
                    )
                    logger.info(
                        f"SearXNG attempt {attempt + 1}/{self.retries + 1} failed ({e.response.status_code}), retrying in {delay}s"
                    )
                    await anyio.sleep(delay)
                else:
                    logger.error(f"SearXNG HTTP error: {e}")
                    raise ProviderError("searxng", f"SearXNG API failure: {e}")
            except httpx.TimeoutException as e:
                last_error = e
                delay = (
                    self.retry_delays[attempt]
                    if attempt < len(self.retry_delays)
                    else self.retry_delays[-1]
                )
                logger.info(
                    f"SearXNG attempt {attempt + 1}/{self.retries + 1} timed out, retrying in {delay}s"
                )
                await anyio.sleep(delay)
            except (OmegaError, RuntimeError, OSError) as e:
                last_error = e
                logger.error(f"SearXNG unexpected error: {e}")
                raise ProviderError("searxng", f"SearXNG system failure: {e}")

        logger.error(f"SearXNG exhausted {self.retries + 1} attempts: {last_error}")
        return None


class ExaProvider(SearchProvider):
    """T2: Neural Search (Exa) Provider."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or self._resolve_from_vault()
        self.base_url = "https://api.exa.ai/search"

    @staticmethod
    def _resolve_from_vault() -> str:
        """Fallback to vault if no key passed explicitly."""
        try:
            from omega.vault import VaultCore

            vault = VaultCore()
            vault._load_sync()
            cred = vault._credentials.get("exa:api_key")
            return cred.encrypted_blob if cred else ""
        except (OmegaError, RuntimeError, OSError) as e:
            logger.debug(f"Exa key fallback failed: {e}")
            return ""

    async def search(self, query: str, limit: int = 10) -> Optional[str]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # [id-soft: vet-002] Right Approximation — fast heuristic search provider chain
                # We default to 'auto' type and 'highlights' for token efficiency.
                payload = {
                    "query": query,
                    "numResults": limit,
                    "type": "auto",
                    "contents": {"highlights": True},
                }
                response = await client.post(
                    self.base_url, headers={"x-api-key": self.api_key}, json=payload
                )
                if response.status_code == 401:
                    raise ProviderAuthError("exa", "Exa API key invalid")
                if response.status_code == 429:
                    raise ProviderRateLimitError("exa", "Exa rate limit exceeded")
                response.raise_for_status()
                # [IW-3] BLEG: inspect 200 OK bodies for error signatures
                BLEGMiddleware().inspect(
                    status_code=response.status_code,
                    body=response.text,
                    provider="exa",
                    trace_id="unknown",
                    url=str(response.url),
                )

                data = response.json()
                results = data.get("results", [])
                if not results:
                    return None

                # Extract highlights as the primary signal for the triage phase
                snippets = []
                for r in results:
                    content = r.get("highlights", r.get("text", ""))
                    if content:
                        snippets.append(f"Source [{r.get('url')}]:\n{content[:500]}")

                if not snippets:
                    return None

                return f"Exa Neural Search (Highlights):\n\n" + "\n\n---\n\n".join(snippets[:3])
            except ProviderError:
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"Exa HTTP error: {e}")
                raise ProviderError("exa", f"Exa API failure: {e}")
            except (OmegaError, RuntimeError, OSError) as e:
                logger.error(f"Exa unexpected error: {e}")
                raise ProviderError("exa", f"Exa system failure: {e}")
