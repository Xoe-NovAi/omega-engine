"""Direct Firecrawl API Tools — Bypass MCP for Reliability.
AP: AP-FIRECRAWL-DIRECT-v1.0.0
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_firecrawl_direct ⬡ ACTIVE

Direct HTTP API wrappers for Firecrawl v2. No MCP dependency.
Use these for all technical research queries.
"""

import os
import httpx
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

FIRECRAWL_API_KEY: Optional[str] = None
BASE_URL = "https://api.firecrawl.dev/v1"


def _resolve_api_key() -> str:
    """Resolve Firecrawl API key from vault."""
    global FIRECRAWL_API_KEY
    if FIRECRAWL_API_KEY:
        return FIRECRAWL_API_KEY
    
    # Try VaultCore first
    try:
        from omega.vault import VaultCore
        vault = VaultCore()
        vault._load_sync()
        cred = vault._credentials.get("firecrawl:api_key")
        FIRECRAWL_API_KEY = cred.encrypted_blob if cred else ""
        if FIRECRAWL_API_KEY:
            logger.info("Firecrawl API key resolved from Sovereign VaultCore")
            return FIRECRAWL_API_KEY
    except Exception as e:
        logger.debug(f"VaultCore resolution failed: {e}")
    
    # No fallback to environment - VaultCore is the single source of truth
    logger.error("No FIRECRAWL_API_KEY found in VaultCore — direct tools will fail")
    return ""


async def firecrawl_search_direct(
    query: str,
    limit: int = 10,
    lang: str = "en",
    tbs: str = "",
    origin: str = "web",
) -> str:
    """Direct Firecrawl search — no MCP dependency.
    
    Args:
        query: Search query string.
        limit: Maximum results (default 10, max 50).
        lang: Language code (default 'en').
        tbs: Time-based search filter (e.g. 'qdr:d' for past day, 'qdr:w' for week).
        origin: Result type — 'web', 'news', or 'images'.
    
    Returns:
        Formatted search results string.
    """
    api_key = _resolve_api_key()
    if not api_key:
        return "ERROR: No Firecrawl API key available"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            kwargs: Dict[str, Any] = {"limit": min(limit, 50), "lang": lang}
            if tbs:
                kwargs["tbs"] = tbs
            if origin and origin != "web":
                kwargs["sources"] = [origin]
            
            response = await client.post(
                f"{BASE_URL}/search",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"query": query, **kwargs}
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            if origin == "news":
                results = [r.model_dump() if hasattr(r, 'model_dump') else r for r in (data.news or [])]
            elif origin == "images":
                results = [r.model_dump() if hasattr(r, 'model_dump') else r for r in (data.images or [])]
            else:
                results = [r.model_dump() if hasattr(r, 'model_dump') else r for r in (data.web or [])]
            
            return _format_results(results[:limit], f"search {origin} results")
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Firecrawl search HTTP error: {e}")
            return f"Firecrawl search failed: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            logger.error(f"Firecrawl search unexpected error: {e}")
            return f"Firecrawl search failed: {e}"


async def firecrawl_scrape_direct(
    url: str,
    only_main: bool = False,
    formats: str = "markdown",
    include_tags: str = "",
    exclude_tags: str = "",
    wait_for: int = 0,
    timeout: int = 60,
    max_chars: int = 0,
) -> str:
    """Direct Firecrawl scrape with configurable content length.
    
    Args:
        url: The URL to scrape.
        only_main: Extract only the main content (no sidebars/ads).
        formats: Comma-separated output formats (markdown, html, rawHtml, links, screenshot).
        include_tags: Comma-separated CSS selectors to include.
        exclude_tags: Comma-separated CSS selectors to exclude.
        wait_for: Milliseconds to wait for page load before extraction.
        timeout: Request timeout in seconds.
        max_chars: Maximum characters to return (0 = no limit).
    
    Returns:
        Full scraped content as markdown.
    """
    api_key = _resolve_api_key()
    if not api_key:
        return "ERROR: No Firecrawl API key available"
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            options: Dict[str, Any] = {"formats": formats.split(",") if formats else ["markdown"]}
            if only_main:
                options["only_main_content"] = True
            if include_tags:
                options["include_tags"] = include_tags.split(",")
            if exclude_tags:
                options["exclude_tags"] = exclude_tags.split(",")
            if wait_for:
                options["wait_for"] = wait_for
            
            response = await client.post(
                f"{BASE_URL}/scrape",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"url": url, "scrape_options": options}
            )
            response.raise_for_status()
            data = response.json()
            
            scrape_data = data.get("data", {})
            md = scrape_data.get("markdown", "")
            
            if max_chars and max_chars > 0:
                md = md[:max_chars]
            
            # Include metadata
            meta = scrape_data.get("metadata", {})
            meta_parts = []
            for k in ["title", "description", "language", "sourceURL"]:
                v = meta.get(k, "")
                if v:
                    meta_parts.append(f"{k}: {v}")
            meta_str = "\n".join(meta_parts) + "\n\n" if meta_parts else ""
            
            links = scrape_data.get("links", [])
            links_str = f"\n\n[{len(links)} links extracted]" if links else ""
            
            return f"URL: {url}\n\n{meta_str}{md}{links_str}"
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Firecrawl scrape HTTP error: {e}")
            return f"Firecrawl scrape failed: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            logger.error(f"Firecrawl scrape unexpected error: {e}")
            return f"Firecrawl scrape failed: {e}"


async def firecrawl_map_direct(
    url: str,
    search: str = "",
    include_subdomains: bool = False,
    limit: int = 50,
) -> str:
    """Direct Firecrawl map — discover URLs on a website.
    
    Args:
        url: The root URL to map.
        search: Optional search query to filter mapped URLs.
        include_subdomains: Include subdomains in mapping.
        limit: Maximum number of URLs (default 50, max 500).
    
    Returns:
        List of discovered URLs.
    """
    api_key = _resolve_api_key()
    if not api_key:
        return "ERROR: No Firecrawl API key available"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            options: Dict[str, Any] = {
                "limit": min(limit, 500),
                "include_subdomains": include_subdomains,
            }
            if search:
                options["search"] = search
            
            response = await client.post(
                f"{BASE_URL}/map",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"url": url, **options}
            )
            response.raise_for_status()
            data = response.json()
            
            links = data.get("links", [])
            if not links:
                return "No URLs found."
            
            lines = [f"{len(links)} URLs mapped from {url}:"]
            for i, link in enumerate(links[:limit], 1):
                href = link.get("url", str(link)) if isinstance(link, dict) else str(link)
                lines.append(f"  [{i}] {href}")
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Firecrawl map error: {e}")
            return f"Firecrawl map failed: {e}"


async def firecrawl_crawl_direct(
    url: str,
    max_depth: int = 2,
    limit: int = 50,
    max_pages: int = 100,
    scrape_options: str = "",
) -> str:
    """Direct Firecrawl crawl — full website crawl (synchronous).
    
    Args:
        url: The starting URL.
        max_depth: Maximum crawl depth (default 2).
        limit: Maximum URLs to return in results (default 50).
        max_pages: Maximum pages to crawl (default 100).
        scrape_options: JSON string of scrape options (e.g. '{"formats":["markdown"]}').
    
    Returns:
        Crawl summary with page details.
    """
    api_key = _resolve_api_key()
    if not api_key:
        return "ERROR: No Firecrawl API key available"
    
    import json
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            opts: Dict[str, Any] = {
                "max_discovery_depth": max_depth,
                "limit": max_pages if max_pages else None,
            }
            if scrape_options:
                try:
                    opts["scrape_options"] = json.loads(scrape_options)
                except json.JSONDecodeError:
                    return f"Invalid JSON in scrape_options: {scrape_options}"
            
            response = await client.post(
                f"{BASE_URL}/crawl",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"url": url, **opts}
            )
            response.raise_for_status()
            data = response.json()
            
            job_data = data.get("data", [])
            if not job_data:
                return f"Crawl of {url} returned no data."
            
            lines = [f"Crawl of {url} completed: {len(job_data)} pages fetched."]
            for doc in job_data[:limit]:
                meta = doc.get("metadata", {})
                title = meta.get("title", "Untitled")
                source = meta.get("sourceURL", "")
                md_len = len(doc.get("markdown", "") or "")
                lines.append(f"\n  [{source}]")
                lines.append(f"  Title: {title}")
                lines.append(f"  Content: {md_len} chars")
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Firecrawl crawl error: {e}")
            return f"Firecrawl crawl failed: {e}"


async def firecrawl_credit_usage_direct() -> str:
    """Check current Firecrawl credit usage and remaining credits."""
    api_key = _resolve_api_key()
    if not api_key:
        return "ERROR: No Firecrawl API key available"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{BASE_URL}/credit-usage",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            response.raise_for_status()
            import json
            return json.dumps(response.json(), indent=2)
        except Exception as e:
            logger.error(f"Firecrawl credit usage error: {e}")
            return f"Firecrawl credit usage failed: {e}"


def _format_results(results: List[Dict[str, Any]], label: str) -> str:
    """Format search results for LLM consumption."""
    if not results:
        return f"0 {label} returned."
    
    lines = [f"{len(results)} {label}:"]
    for i, r in enumerate(results[:20], 1):
        title = r.get("title") or r.get("name") or "Untitled"
        url = r.get("url") or ""
        desc = (r.get("description") or r.get("snippet") or "")[:300]
        lines.append(f"\n[{i}] {title}")
        if url:
            lines.append(f"     URL: {url}")
        if desc:
            lines.append(f"     {desc}")
    return "\n".join(lines)


# Synchronous wrappers for OpenCode tool registration
import anyio

def firecrawl_search(query: str, limit: int = 10, lang: str = "en", tbs: str = "", origin: str = "web") -> str:
    """Synchronous wrapper for OpenCode tool registration."""
    return anyio.run(firecrawl_search_direct, query, limit, lang, tbs, origin)

def firecrawl_scrape(
    url: str,
    only_main: bool = False,
    formats: str = "markdown",
    include_tags: str = "",
    exclude_tags: str = "",
    wait_for: int = 0,
    timeout: int = 60,
    max_chars: int = 0,
) -> str:
    """Synchronous wrapper for OpenCode tool registration."""
    return anyio.run(firecrawl_scrape_direct, url, only_main, formats, include_tags, exclude_tags, wait_for, timeout, max_chars)

def firecrawl_map(url: str, search: str = "", include_subdomains: bool = False, limit: int = 50) -> str:
    """Synchronous wrapper for OpenCode tool registration."""
    return anyio.run(firecrawl_map_direct, url, search, include_subdomains, limit)

def firecrawl_crawl(
    url: str,
    max_depth: int = 2,
    limit: int = 50,
    max_pages: int = 100,
    scrape_options: str = "",
) -> str:
    """Synchronous wrapper for OpenCode tool registration."""
    return anyio.run(firecrawl_crawl_direct, url, max_depth, limit, max_pages, scrape_options)

def firecrawl_credit_usage() -> str:
    """Synchronous wrapper for OpenCode tool registration."""
    return anyio.run(firecrawl_credit_usage_direct)


if __name__ == "__main__":
    # Quick test
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "search":
            print(anyio.run(firecrawl_search_direct, " ".join(sys.argv[2:]), 5))
        elif sys.argv[1] == "scrape":
            print(anyio.run(firecrawl_scrape_direct, sys.argv[2], max_chars=0))
        elif sys.argv[1] == "credits":
            print(anyio.run(firecrawl_credit_usage_direct))