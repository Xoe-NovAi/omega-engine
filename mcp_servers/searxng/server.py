#!/usr/bin/env python3
"""
🔱 SearXNG MCP Server — Streamable HTTP Transport
AP: AP-SEARXNG-MCP-STREAMABLE-v1.1.0
⬡ OMEGA ⬡ SEARXNG-MCP ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_searxng_mcp ⬡ STREAMABLE-HTTP

Sovereign metasearch via self-hosted SearXNG.
Migrated from SSE to Streamable HTTP (MCP SDK v2, spec 2025-03-26).
v1.1.0: Fixed OpenCode config (type=remote, URL=/mcp), SearXNG settings.yml hardened
"""

import os
import httpx
from fastmcp.server.server import FastMCP
from starlette.middleware.cors import CORSMiddleware

# Configuration - MUST be set BEFORE FastMCP instantiation
MCP_PORT = int(os.getenv("MCP_PORT", "8018"))
os.environ.setdefault("FASTMCP_PORT", str(MCP_PORT))
os.environ.setdefault("FASTMCP_HOST", "127.0.0.1")

SEARXNG_URL = os.getenv("SEARXNG_BASE_URL", "http://localhost:8017")

# Initialize FastMCP server — port 8018 (Streamable HTTP transport)
mcp = FastMCP("Sovereign SearXNG")

# CORS for OpenCode/Claude Code - add middleware to Starlette app
app = mcp.http_app()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Port/host via environment (FastMCP 3.4+)
os.environ.setdefault("FASTMCP_PORT", str(MCP_PORT))
os.environ.setdefault("FASTMCP_HOST", "127.0.0.1")


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

    For YouTube research: categories="videos", engines="youtube,invidious,invidious2,duckduckgo,brave"
    For general: categories="general", engines="duckduckgo,google,brave,wikipedia"
    For code: categories="it", engines="github,duckduckgo,google"
    For science: categories="science", engines="arxiv,semantic_scholar,google"
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
        try:
            resp = await client.post(f"{SEARXNG_URL}/search", data=form_data)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as e:
            return f"SearXNG HTTP error: {e.response.status_code} - {e}"
        except httpx.RequestError as e:
            return f"SearXNG request failed: {e}"

    # Format results for LLM consumption
    results = data.get("results", [])
    if not results:
        return f"No results for query: {query}"

    lines = [f"Search: {query} | Categories: {categories} | Engines: {engines or 'default'}"]
    for i, r in enumerate(results[:limit], 1):
        title = r.get("title", "No title")
        url = r.get("url", "No URL")
        content = r.get("content", "No snippet")
        engine = r.get("engine", "unknown")
        lines.append(f"\n[{i}] {title} ({engine})")
        lines.append(f"    URL: {url}")
        lines.append(f"    Snippet: {content[:300]}...")

    return "\n".join(lines)


@mcp.tool()
async def searxng_health() -> str:
    """Check SearXNG instance health."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(f"{SEARXNG_URL}/healthz")
            return f"SearXNG healthy: {resp.status_code}"
        except Exception as e:
            return f"SearXNG unhealthy: {e}"


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8018)