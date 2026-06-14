# 🔱 Omega SearXNG MCP Server
# AP: AP-SEARXNG-MCP-v1.0.0
# ⬡ OMEGA ⬡ SOPHIA ⬡ la-llama ⬡ opencode ⬡ trc_searxng_mcp

import os
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Sovereign SearXNG")

SEARXNG_URL = os.environ.get("SEARXNG_BASE_URL", "http://localhost:8017")

@mcp.tool()
async def searxng_search(query: str, limit: int = 10) -> str:
    \"\"\"
    Performs a sovereign metasearch using the self-hosted SearXNG instance.
    Returns a formatted list of results with titles, URLs, and snippets.
    \"\"\"
    params = {
        "q": query,
        "format": "json",
        "limit": limit
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SEARXNG_URL}/search", params=params, timeout=10.0)
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
                formatted_results.append(f"[{i}] {title}\\nURL: {url}\\nSnippet: {content}\\n")
            
            return "\\n".join(formatted_results)
        except Exception as e:
            return f"Error connecting to SearXNG: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="sse")
