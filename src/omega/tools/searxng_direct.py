# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Direct SearXNG API Tools — Bypass MCP for Reliability.
AP: AP-SEARXNG-DIRECT-v1.0.0
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_searxng_direct ⬡ ACTIVE

Direct HTTP API wrappers for self-hosted SearXNG. No MCP dependency.
Use these for all technical research queries when SearXNG instance is healthy.
"""

import os
import httpx
import logging
from typing import Dict

logger = logging.getLogger(__name__)

SEARXNG_BASE_URL: str = os.environ.get("SEARXNG_BASE_URL", "http://127.0.0.1:8017")


async def searxng_search_direct(
    query: str,
    limit: int = 10,
    categories: str = "general",
    engines: str = "",
    language: str = "auto",
    time_range: str = "",
    pageno: int = 1,
) -> str:
    """Direct SearXNG search — no MCP dependency.

    Args:
        query: Search query string.
        limit: Maximum results (default 10).
        categories: Search categories (general, science, it, videos, etc.)
        engines: Specific engines to use (comma-separated).
        language: Language code (default 'auto').
        time_range: Time filter (day, week, month, year).
        pageno: Page number (default 1).

    Returns:
        Formatted search results string.
    """
    form_data: Dict[str, str] = {
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
            resp = await client.post(f"{SEARXNG_BASE_URL}/search", data=form_data)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"SearXNG HTTP error: {e}")
            return f"SearXNG search failed: {e.response.status_code} - {e.response.text}"
        except httpx.RequestError as e:
            logger.error(f"SearXNG request failed: {e}")
            return f"SearXNG request failed: {e}"
        except Exception as e:
            logger.error(f"SearXNG unexpected error: {e}")
            return f"SearXNG search failed: {e}"

    results = data.get("results", [])
    if not results:
        suggestions = data.get("suggestions", [])
        if suggestions:
            return f"SearXNG suggestions: {', '.join(suggestions)}"
        return f"No results for query: {query}"

    lines = [f"Search: {query} | Categories: {categories} | Engines: {engines or 'default'}"]
    for i, r in enumerate(results[:limit], 1):
        title = r.get("title", "No title")
        url = r.get("url", "No URL")
        content = r.get("content", "No snippet")
        engine = r.get("engine", "unknown")
        lines.append(f"\n[{i}] {title} ({engine})")
        lines.append(f"    URL: {url}")
        lines.append(f"    Snippet: {content[:500]}")

    return "\n".join(lines)


async def searxng_health_direct() -> str:
    """Check SearXNG instance health directly."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(f"{SEARXNG_BASE_URL}/healthz")
            return f"SearXNG healthy: {resp.status_code}"
        except Exception as e:
            logger.error(f"SearXNG health check failed: {e}")
            return f"SearXNG unhealthy: {e}"


async def searxng_preferences_direct() -> str:
    """Get SearXNG instance preferences/capabilities."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(f"{SEARXNG_BASE_URL}/preferences")
            resp.raise_for_status()
            data = resp.json()
            import json

            return json.dumps(data, indent=2)
        except Exception as e:
            logger.error(f"SearXNG preferences failed: {e}")
            return f"SearXNG preferences failed: {e}"


# Synchronous wrappers for OpenCode tool registration
import anyio


def searxng_search(
    query: str,
    limit: int = 10,
    categories: str = "general",
    engines: str = "",
    language: str = "auto",
    time_range: str = "",
    pageno: int = 1,
) -> str:
    """Synchronous wrapper for OpenCode tool registration."""
    return anyio.run(
        searxng_search_direct, query, limit, categories, engines, language, time_range, pageno
    )


def searxng_health() -> str:
    """Synchronous wrapper for OpenCode tool registration."""
    return anyio.run(searxng_health_direct)


def searxng_preferences() -> str:
    """Synchronous wrapper for OpenCode tool registration."""
    return anyio.run(searxng_preferences_direct)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "search":
            print(anyio.run(searxng_search_direct, " ".join(sys.argv[2:]), 5))
        elif sys.argv[1] == "health":
            print(anyio.run(searxng_health_direct))
        elif sys.argv[1] == "prefs":
            print(anyio.run(searxng_preferences_direct))
