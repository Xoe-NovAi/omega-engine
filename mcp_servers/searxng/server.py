# 🔱 Omega SearXNG MCP Server
# AP: AP-SEARXNG-MCP-v1.0.0
# ⬡ OMEGA ⬡ SOPHIA ⬡ la-llama ⬡ opencode ⬡ trc_searxng_mcp
#
# Runs as SSE MCP server on port 8018 (configurable via MCP_PORT env var).
# Proxies queries to the SearXNG container on port 8017.

import os
import httpx
from mcp.server.fastmcp import FastMCP
from mcp_servers.omega_hub.middleware import m9_safe

SEARXNG_URL = os.environ.get("SEARXNG_BASE_URL", "http://localhost:8017")
MCP_PORT = int(os.environ.get("MCP_PORT", "8018"))

# Initialize FastMCP server — port 8018 (SSE transport)
mcp = FastMCP("Sovereign SearXNG", port=MCP_PORT, host="127.0.0.1")


@m9_safe("searxng_search")
@mcp.tool()
async def searxng_search(query: str, limit: int = 10) -> str:
    """Performs a sovereign metasearch using the self-hosted SearXNG instance.

    Returns a formatted list of results with titles, URLs, and snippets.
    """
    params = {
        "q": query,
        "format": "json",
        "limit": limit,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{SEARXNG_URL}/search", params=params, timeout=10.0
            )
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            if not results:
                return "No results found for the query."

            formatted_results = []
            for i, res in enumerate(results, 1):
                title = res.get("title", "No Title")
                url = res.get("url", "No URL")
                content = res.get("content", "No snippet available")
                formatted_results.append(
                    f"[{i}] {title}\nURL: {url}\nSnippet: {content}\n"
                )

            return "\n".join(formatted_results)
        except Exception as e:
            return f"Error connecting to SearXNG: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="sse")
