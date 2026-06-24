# 🔱 Omega SearXNG MCP Server
# AP: AP-SEARXNG-MCP-v1.1.0
# ⬡ OMEGA ⬡ SOPHIA ⬡ la-llama ⬡ opencode ⬡ trc_searxng_mcp
#
# Runs as SSE MCP server on port 8018 (configurable via MCP_PORT env var).
# Proxies queries to the SearXNG container on port 8017.
#
# Changes from v1.0.0:
#   - Removed inner try/except to let @m9_safe handle errors uniformly (M9 compliance)
#   - Wired 'limit' parameter to slice results
#   - Added categories, engines, language, time_range, pageno parameters for parity with client
#   - Preserved @m9_safe decorator for trace_id generation and error boundary
#
import os
import sys
import httpx
from mcp.server.fastmcp import FastMCP

# Ensure project root is in path for mcp_servers imports
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from mcp_servers.omega_hub.middleware import m9_safe

SEARXNG_URL = os.environ.get("SEARXNG_BASE_URL", "http://localhost:8017")
MCP_PORT = int(os.environ.get("MCP_PORT", "8018"))

# Initialize FastMCP server — port 8018 (SSE transport)
mcp = FastMCP("Sovereign SearXNG", port=MCP_PORT, host="127.0.0.1")


@m9_safe("searxng_search")
@mcp.tool()
async def searxng_search(
    query: str,
    categories: str = "general",
    engines: str = "",
    language: str = "auto",
    time_range: str = "",
    pageno: int = 1,
    limit: int = 10,
) -> str:
    """Sovereign metasearch via self-hosted SearXNG.

    Categories: general, images, videos, news, music, files, it, science, social media
    Engines: comma-separated (e.g., "google,bing,duckduckgo"). Empty = all enabled.
    Time range: day, week, month, year (empty = all time)
    Language: auto, en, en-US, de, fr, etc.
    Pagination: pageno starts at 1
    Limit: Maximum number of results to return.
    """
    form_data = {
        "q": query,
        "format": "json",
        "language": language,
        "categories": categories,
        "pageno": str(pageno),
    }
    if engines:
        form_data["engines"] = engines
    if time_range:
        form_data["time_range"] = time_range

    async with httpx.AsyncClient(timeout=15.0) as client:
        # POST is more private than GET (no query in URL/access logs)
        # SearXNG requires form-encoded data, NOT JSON body
        resp = await client.post(
            f"{SEARXNG_URL}/search",
            data=form_data,
        )
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results", [])
        if not results:
            suggestions = data.get("suggestions", [])
            unresponsive = data.get("unresponsive_engines", [])
            parts = ["No results found."]
            if suggestions:
                parts.append(f"Suggestions: {', '.join(suggestions)}")
            if unresponsive:
                failed = [e[0] for e in unresponsive]
                parts.append(f"Unresponsive engines: {', '.join(failed)}")
            return "\n".join(parts)

        # Apply the limit parameter to the results
        sliced_results = results[:limit]
        
        formatted_results = []
        for i, res in enumerate(sliced_results, 1):
            title = res.get("title", "No Title")
            url = res.get("url", "No URL")
            content = res.get("content", "No snippet available")
            engine = res.get("engine", "unknown")
            score = res.get("score", 0)
            formatted_results.append(
                f"[{i}] {title}\n"
                f"    URL: {url}\n"
                f"    Engine: {engine} (score: {score:.1f})\n"
                f"    {content}\n"
            )

        header = f"Found {len(results)} results (page {pageno}), returning top {len(sliced_results)}:\n\n"
        return header + "\n".join(formatted_results)


if __name__ == "__main__":
    # [id-soft: quake3-1999] netchan — Auto-reconnect on transport crash
    # FastMCP SSE transport has a known ASGI race on client disconnect.
    # Instead of crashing permanently, retry with exponential backoff.
    import time as _time
    max_retries = 5
    for attempt in range(max_retries):
        try:
            mcp.run(transport="sse")
            break  # clean exit
        except RuntimeError as e:
            if "http.response" in str(e):
                logger.warning("MCP SSE transport crashed (ASGI race), restarting (attempt %d/%d): %s",
                               attempt + 1, max_retries, e)
                if attempt < max_retries - 1:
                    _time.sleep(2 ** attempt)  # exponential backoff: 1s, 2s, 4s, 8s
                else:
                    logger.error("MCP SSE transport exhausted %d retries — giving up", max_retries)
                    raise
            else:
                raise  # non-transport errors propagate immediately
