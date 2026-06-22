# 🔱 Omega Engine — SearXNG Sovereign Search Client
# AP: AP-BACKGROUND-RESEARCHER-SEARXNG-v1.0.0
# ⬡ OMEGA ⬡ BELIAL ⬡ sovereign ⬡ searxng ⬡ WORKER
#
# Zero-cost, always-on search via the local SearXNG instance (port 8017).

import logging
from omega.errors import (
    OmegaError,
)
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

SEARXNG_URL = "http://localhost:8017"
DEFAULT_ENGINES = ["google", "duckduckgo", "brave", "wikipedia", "arxiv", "semantic scholar"]
MAX_RESULTS = 10
TIMEOUT = 10.0


class SearXNGClient:
    """Client for the sovereign SearXNG search layer.

    This is the zero-cost, always-on search layer. No API key required.
    Connects to the Podman container on port 8017.
    """

    def __init__(self, base_url: str = SEARXNG_URL, timeout: float = TIMEOUT):
        self.base_url = base_url
        self.timeout = timeout

    async def search(
        self,
        query: str,
        engines: Optional[list[str]] = None,
        max_results: int = MAX_RESULTS,
        safesearch: int = 0,
        pageno: int = 1,
    ) -> list[dict]:
        """Execute a search via SearXNG. Returns list of result dicts.

        Each result has keys: url, title, content, engine, publishedDate, thumbnail

        IMPORTANT: SearXNG does NOT accept JSON body. Send form-encoded data.
        Uses POST with form data (application/x-www-form-urlencoded).
        """
        if engines is None:
            engines = DEFAULT_ENGINES

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Build form data — SearXNG expects form-encoded, not JSON
                form_data = {
                    "q": query,
                    "format": "json",
                    "safesearch": str(safesearch),
                    "pageno": str(pageno),
                    "language": "auto",
                    "categories": "general",
                }
                if engines:
                    form_data["engines"] = ",".join(engines)
                resp = await client.post(
                    f"{self.base_url}/search",
                    data=form_data,  # form-encoded, NOT json!
                )
                resp.raise_for_status()
                data = resp.json()
                results = data.get("results", [])
                return results[:max_results]

        except httpx.RequestError as e:
            logger.warning(f"SearXNG request failed: {e}")
            return []
        except OmegaError as e:
            logger.warning(f"SearXNG OmegaError: {e}")
            return []
        except Exception as e:
            logger.error(f"SearXNG search error: {e}", exc_info=True)
            return []

    async def search_text(
        self,
        query: str,
        engines: Optional[list[str]] = None,
        max_results: int = MAX_RESULTS,
    ) -> list[str]:
        """Convenience method: returns just the URL strings."""
        results = await self.search(query, engines, max_results)
        return [r.get("url", "") for r in results if r.get("url")]

    async def health(self) -> bool:
        """Check if SearXNG is available."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/healthz")
                return resp.status_code == 200
        except Exception as e:
            # M9 carve-out: health probe may catch all to prevent crash loops
            # [id-soft: doom-1993] WAD System — graceful degradation on search failure
            logger.warning("SearXNG health check failed: %s", e)
            return False
