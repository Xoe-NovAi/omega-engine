# 🔱 Omega Firecrawl MCP Server
# AP: AP-FIRECRAWL-MCP-v1.0.0
# ⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_firecrawl_mcp
#
# Runs as SSE MCP server on port 8015 (configurable via MCP_PORT env var).
# Wraps the Firecrawl v2 API via firecrawl-py SDK.
# API key resolved from Sovereign Key Vault, with env fallback.
#
# Tools: search, scrape, crawl, map, extract, credit_usage

import os
import sys
import json
import logging

_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from mcp.server.fastmcp import FastMCP
from mcp_servers.omega_hub.middleware import m9_safe

FIRECRAWL_PORT = int(os.environ.get("MCP_PORT", "8015"))

# Resolve API key — vault first, then env fallback
FIRECRAWL_API_KEY: str | None = None
try:
    from omega.vault.key_vault import KeyVault
    vault = KeyVault()
    FIRECRAWL_API_KEY = vault.resolve("firecrawl")
    if FIRECRAWL_API_KEY:
        logging.info("Firecrawl API key resolved from Sovereign Key Vault")
except Exception:
    pass

if not FIRECRAWL_API_KEY:
    FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY")
    if FIRECRAWL_API_KEY:
        logging.info("Firecrawl API key resolved from environment fallback")
    else:
        logging.error("No FIRECRAWL_API_KEY found — Firecrawl MCP will fail on calls")

mcp = FastMCP("Sovereign Firecrawl", port=FIRECRAWL_PORT, host="127.0.0.1", log_level="WARNING")


def _make_client():
    from firecrawl import AsyncFirecrawl
    return AsyncFirecrawl(api_key=FIRECRAWL_API_KEY)


def _format_results(results: list, label: str = "results") -> str:
    if not results:
        return f"0 {label} returned."
    lines = [f"{len(results)} {label}:"]
    for i, r in enumerate(results[:20], 1):
        title = r.get("title") or r.get("name") or "Untitled"
        url = r.get("url") or ""
        desc = (r.get("description") or r.get("snippet") or "")[:120]
        lines.append(f"\n[{i}] {title}")
        if url:
            lines.append(f"     URL: {url}")
        if desc:
            lines.append(f"     {desc}")
    return "\n".join(lines)


@m9_safe("firecrawl_search")
@mcp.tool()
async def firecrawl_search(
    query: str,
    limit: int = 10,
    lang: str = "en",
    tbs: str = "",
    origin: str = "web",
) -> str:
    """Search the web using Firecrawl.

    Args:
        query: Search query string.
        limit: Maximum results (default 10, max 50).
        lang: Language code (default 'en').
        tbs: Time-based search filter (e.g. 'qdr:d' for past day, 'qdr:w' for week).
        origin: Result type — 'web', 'news', or 'images'.
    """
    client = _make_client()
    kwargs: dict = {"limit": min(limit, 50), "lang": lang}
    if tbs:
        kwargs["tbs"] = tbs
    if origin and origin != "web":
        kwargs["sources"] = [origin]

    data = await client.search(query, **kwargs)
    results = []
    if origin == "news":
        results = [r.model_dump() for r in (data.news or [])]
    elif origin == "images":
        results = [r.model_dump() for r in (data.images or [])]
    else:
        results = [r.model_dump() for r in (data.web or [])]
    return _format_results(results[:limit], f"search {origin} results")


@m9_safe("firecrawl_scrape")
@mcp.tool()
async def firecrawl_scrape(
    url: str,
    only_main: bool = False,
    formats: str = "markdown",
    include_tags: str = "",
    exclude_tags: str = "",
    wait_for: int = 0,
    timeout: int = 30,
) -> str:
    """Scrape a single URL using Firecrawl.

    Args:
        url: The URL to scrape.
        only_main: Extract only the main content (no sidebars/ads).
        formats: Comma-separated output formats (markdown, html, rawHtml, links, screenshot).
        include_tags: Comma-separated CSS selectors to include.
        exclude_tags: Comma-separated CSS selectors to exclude.
        wait_for: Milliseconds to wait for page load before extraction.
        timeout: Request timeout in seconds.
    """
    client = _make_client()
    options: dict = {"formats": formats.split(",") if formats else ["markdown"]}
    if only_main:
        options["only_main_content"] = True
    if include_tags:
        options["include_tags"] = include_tags.split(",")
    if exclude_tags:
        options["exclude_tags"] = exclude_tags.split(",")
    if wait_for:
        options["wait_for"] = wait_for

    data = await client.scrape(url, timeout=timeout, scrape_options=options)
    md = (getattr(data, "markdown", None) or "")[:4000]
    links = getattr(data, "links", None) or []
    meta = getattr(data, "metadata", None)
    meta_str = ""
    if meta:
        meta_dict = meta.model_dump() if hasattr(meta, "model_dump") else {}
        meta_parts = []
        for k in ["title", "description", "language", "sourceURL"]:
            v = meta_dict.get(k, "")
            if v:
                meta_parts.append(f"{k}: {v}")
        meta_str = "\n".join(meta_parts) + "\n\n"

    result = f"URL: {url}\n\n"
    if meta_str:
        result += meta_str
    result += md
    if links:
        result += f"\n\n[{len(links)} links extracted]"
    return result


@m9_safe("firecrawl_map")
@mcp.tool()
async def firecrawl_map(
    url: str,
    search: str = "",
    include_subdomains: bool = False,
    limit: int = 50,
) -> str:
    """Map URLs on a website using Firecrawl.

    Args:
        url: The root URL to map.
        search: Optional search query to filter mapped URLs.
        include_subdomains: Include subdomains in mapping.
        limit: Maximum number of URLs (default 50, max 500).
    """
    client = _make_client()
    options: dict = {
        "limit": min(limit, 500),
        "include_subdomains": include_subdomains,
    }
    if search:
        options["search"] = search

    data = await client.map(url, **options)
    links = data.links or []
    if not links:
        return "No URLs found."
    lines = [f"{len(links)} URLs mapped from {url}:"]
    for i, link in enumerate(links[:limit], 1):
        href = link.url if hasattr(link, "url") else str(link)
        lines.append(f"  [{i}] {href}")
    return "\n".join(lines)


@m9_safe("firecrawl_crawl")
@mcp.tool()
async def firecrawl_crawl(
    url: str,
    max_depth: int = 2,
    limit: int = 50,
    max_pages: int = 100,
    scrape_options: str = "",
) -> str:
    """Crawl a website using Firecrawl (synchronous — waits for completion).

    Args:
        url: The starting URL.
        max_depth: Maximum crawl depth (default 2).
        limit: Maximum URLs to return in results (default 50).
        max_pages: Maximum pages to crawl (default 100).
        scrape_options: JSON string of scrape options (e.g. '{"formats":["markdown"]}').
    """
    client = _make_client()
    opts: dict = {
        "max_discovery_depth": max_depth,
        "limit": max_pages if max_pages else None,
    }
    if scrape_options:
        try:
            opts["scrape_options"] = json.loads(scrape_options)
        except json.JSONDecodeError:
            return f"Invalid JSON in scrape_options: {scrape_options}"

    job = await client.crawl(url, **opts)
    if not job.data:
        return f"Crawl of {url} returned no data."

    lines = [f"Crawl of {url} completed: {len(job.data)} pages fetched."]
    for doc in job.data[:limit]:
        meta = doc.metadata
        title = meta.title if meta and hasattr(meta, "title") else "Untitled"
        source = meta.source_url if meta and hasattr(meta, "source_url") else ""
        md_len = len(doc.markdown or "")
        lines.append(f"\n  [{source}]")
        lines.append(f"  Title: {title}")
        lines.append(f"  Content: {md_len} chars")
    return "\n".join(lines)


@m9_safe("firecrawl_credit_usage")
@mcp.tool()
async def firecrawl_credit_usage() -> str:
    """Check current Firecrawl credit usage and remaining credits."""
    client = _make_client()
    usage = await client.get_credit_usage()
    return json.dumps(usage, indent=2, default=str)


if __name__ == "__main__":
    import time as _time
    max_retries = 5
    for attempt in range(max_retries):
        try:
            mcp.run(transport="sse")
            break
        except RuntimeError as e:
            if "http.response" in str(e):
                logging.warning(
                    "MCP SSE transport crashed (ASGI race), restarting (attempt %d/%d): %s",
                    attempt + 1, max_retries, e,
                )
                if attempt < max_retries - 1:
                    _time.sleep(2 ** attempt)
                else:
                    logging.error("MCP SSE transport exhausted %d retries — giving up", max_retries)
                    raise
            else:
                raise
