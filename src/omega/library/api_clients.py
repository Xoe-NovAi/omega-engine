# AP: AP-LIBRARY-API-v2.0.0
# 🔱 Omega Engine — Sovereign Library API Integrations
#
# ⬡ OMEGA ⬡ KALI ⬡ api_clients ⬡ trc_canonical
#
# [id-soft: vet-025] Hard-Boundary Struct — each client is a sealed
#   interface with search() + get_by_identifier() as the contract.
# Heritage: WAD System — orchestrator treats clients like WAD entries: swapable, discoverable, hot-pluggable (Doom 1993)
#
# Canonical source for all library API client implementations.
# enrichment.py is the thin orchestration wrapper.
#
# Supported APIs:
# - Open Library (no key required)
# - Internet Archive (no key required)
# - Library of Congress (no key required)
# - Project Gutenberg via Gutendex (no key required)

import logging
import time
from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, TypeVar
from abc import ABC, abstractmethod

import anyio
import httpx2 as httpx
from omega.errors import OmegaError

logger = logging.getLogger(__name__)

# ============================================================================
# ENUMS
# ============================================================================


class DomainCategory(str, Enum):
    """Content domain categories for curation routing."""

    CODE = "code"
    SCIENCE = "science"
    DATA = "data"
    GENERAL = "general"
    BOOKS = "books"
    MUSIC = "music"
    ARCHIVES = "archives"
    FICTION = "fiction"
    REFERENCE = "reference"


class DeweyDecimalClass(str, Enum):
    """Dewey Decimal Classification for library cataloging."""

    COMPUTER_SCIENCE = "000"
    PHILOSOPHY = "100"
    RELIGION = "200"
    SOCIAL_SCIENCES = "300"
    LANGUAGE = "400"
    SCIENCE = "500"
    TECHNOLOGY = "600"
    ARTS = "700"
    LITERATURE = "800"
    HISTORY = "900"


DEWEY_TO_DOMAIN = {
    "000": DomainCategory.CODE,
    "500": DomainCategory.SCIENCE,
    "600": DomainCategory.ARCHIVES,
    "800": DomainCategory.BOOKS,
    "900": DomainCategory.REFERENCE,
}

# ============================================================================
# DATA MODELS
# ============================================================================


@dataclass
class LibraryAPIConfig:
    """Configuration for library API integrations. Zero required keys."""

    loc_api_base_url: str = "https://www.loc.gov/books/services/web/search.json"
    openlibrary_api_base_url: str = "https://openlibrary.org"
    archive_api_base_url: str = "https://archive.org/advancedsearch.php"
    gutenberg_api_base_url: str = "https://gutendex.com"

    rate_limit_calls: int = 10
    rate_limit_period: int = 60
    request_timeout: int = 10
    cache_ttl: int = 3600

    enable_cache: bool = True
    user_agent: str = (
        "OmegaEngine/1.0.0 (Sovereign Library Client; +https://github.com/Xoe-NovAi/omega-engine)"
    )


@dataclass
class LibraryMetadata:
    """Enriched metadata from library API responses."""

    isbn: Optional[str] = None
    title: Optional[str] = None
    authors: List[str] = field(default_factory=list)
    publication_date: Optional[str] = None
    publisher: Optional[str] = None
    description: Optional[str] = None
    subjects: List[str] = field(default_factory=list)
    dewey_decimal: Optional[str] = None
    lcc: Optional[str] = None
    language: Optional[str] = None
    page_count: Optional[int] = None
    cover_url: Optional[str] = None
    source_apis: List[str] = field(default_factory=list)
    enrichment_confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================================
# TYPED ERRORS [id-soft: vet-026] Hard-Boundary — typed error hierarchy as boundary layer
# ============================================================================


class LibraryAPIError(OmegaError):
    """Base error for library API operations."""


class ClientNotFoundError(LibraryAPIError):
    """Requested library client is not registered."""


# ============================================================================
# BASE CLIENT [id-soft: vet-027] WAD System — swapable, hot-pluggable data sources
# ============================================================================

T = TypeVar("T")


class BaseLibraryClient(ABC):
    """Abstract base for sovereign library API clients.

    Each client wraps a single external data source with:
      - search(query) -> List[LibraryMetadata]
      - get_by_identifier(id, id_type) -> Optional[LibraryMetadata]
      - In-memory cache with configurable TTL
      - Rate limiting via anyio.sleep
      - Reusable httpx client (one per instance lifetime)
    """

    def __init__(self, config: LibraryAPIConfig):
        self.config = config
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._last_request_time = 0.0
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Lazy-init and return the shared httpx client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.config.request_timeout,
                headers={"User-Agent": self.config.user_agent},
            )
        return self._client

    async def _rate_limit(self) -> None:
        """Enforce per-instance rate limiting."""
        elapsed = time.time() - self._last_request_time
        min_interval = self.config.rate_limit_period / self.config.rate_limit_calls
        if elapsed < min_interval:
            await anyio.sleep(min_interval - elapsed)
        self._last_request_time = time.time()

    def _get_cached(self, key: str) -> Optional[T]:
        if not self.config.enable_cache or key not in self._cache:
            return None
        value, timestamp = self._cache[key]
        if time.time() - timestamp > self.config.cache_ttl:
            del self._cache[key]
            return None
        return value  # type: ignore[return-value]

    def _set_cache(self, key: str, value: Any) -> None:
        if self.config.enable_cache:
            self._cache[key] = (value, time.time())

    async def close(self) -> None:
        """Explicitly close the shared httpx client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @abstractmethod
    async def search(self, query: str, **kwargs: Any) -> List[LibraryMetadata]: ...

    @abstractmethod
    async def get_by_identifier(
        self, identifier: str, id_type: str
    ) -> Optional[LibraryMetadata]: ...


# ============================================================================
# IMPLEMENTATIONS
# ============================================================================

# ── Open Library (openlibrary.org) ──────────────────────────────────


class OpenLibraryClient(BaseLibraryClient):
    """Open Library search and ISBN lookup. No API key required."""

    async def search(self, query: str, **kwargs: Any) -> List[LibraryMetadata]:
        cache_key = f"ol:search:{query}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        try:
            await self._rate_limit()
            client = await self._get_client()
            params = {"title": query, "limit": kwargs.get("limit", 5)}
            resp = await client.get(
                f"{self.config.openlibrary_api_base_url}/search.json",
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()

            results = []
            for doc in data.get("docs", [])[:5]:
                isbns = doc.get("isbn")
                results.append(
                    LibraryMetadata(
                        isbn=isbns[0] if isinstance(isbns, list) and isbns else None,
                        title=doc.get("title"),
                        authors=doc.get("author_name", []),
                        publication_date=str(doc.get("first_publish_year", "")),
                        subjects=doc.get("subject", [])[:5],
                        source_apis=["openlibrary"],
                        enrichment_confidence=0.7,
                    )
                )
            self._set_cache(cache_key, results)
            return results
        except (httpx.HTTPError, RuntimeError) as exc:
            logger.error("OpenLibrary search failed: %s", exc)
            return []

    async def get_by_identifier(
        self, identifier: str, id_type: str = "isbn"
    ) -> Optional[LibraryMetadata]:
        if id_type != "isbn":
            return None
        cache_key = f"ol:isbn:{identifier}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        try:
            await self._rate_limit()
            client = await self._get_client()
            params = {"bibkeys": f"ISBN:{identifier}", "jscmd": "details", "format": "json"}
            resp = await client.get(
                f"{self.config.openlibrary_api_base_url}/api/books",
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()
            if data:
                key = list(data.keys())[0]
                details = data[key].get("details", {})
                authors_raw = details.get("authors", [])
                publishers_raw = details.get("publishers", [])

                meta = LibraryMetadata(
                    isbn=identifier,
                    title=details.get("title"),
                    authors=[a.get("name", "") for a in authors_raw if isinstance(a, dict)],
                    publication_date=str(details.get("publish_date", "")),
                    publisher=publishers_raw[0]
                    if isinstance(publishers_raw, list) and publishers_raw
                    else None,
                    subjects=details.get("subjects", [])[:5],
                    source_apis=["openlibrary"],
                    enrichment_confidence=0.85,
                )
                self._set_cache(cache_key, meta)
                return meta
        except (httpx.HTTPError, RuntimeError) as exc:
            logger.error("OpenLibrary ISBN lookup failed: %s", exc)
        return None


# ── Internet Archive (archive.org) ──────────────────────────────────


class InternetArchiveClient(BaseLibraryClient):
    """Internet Archive text search and metadata lookup. No API key required."""

    async def search(self, query: str, **kwargs: Any) -> List[LibraryMetadata]:
        cache_key = f"ia:search:{query}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        try:
            await self._rate_limit()
            client = await self._get_client()
            params: Dict[str, Any] = {
                "q": f"(title:{query} OR description:{query}) AND mediatype:texts",
                "output": "json",
                "rows": kwargs.get("limit", 5),
                "fl[]": ["identifier", "title", "creator", "date", "description", "subject"],
            }
            resp = await client.get(self.config.archive_api_base_url, params=params)
            resp.raise_for_status()
            data = resp.json()

            results = []
            for doc in data.get("response", {}).get("docs", [])[:5]:
                creators = doc.get("creator", [])
                if isinstance(creators, str):
                    creators = [creators]
                results.append(
                    LibraryMetadata(
                        title=doc.get("title"),
                        authors=creators,
                        publication_date=doc.get("date"),
                        description=(
                            doc.get("description", "")[:500] if doc.get("description") else None
                        ),
                        subjects=doc.get("subject", [])[:5] if doc.get("subject") else [],
                        source_apis=["internetarchive"],
                        enrichment_confidence=0.65,
                    )
                )
            self._set_cache(cache_key, results)
            return results
        except (httpx.HTTPError, RuntimeError) as exc:
            logger.error("InternetArchive search failed: %s", exc)
            return []

    async def get_by_identifier(
        self, identifier: str, id_type: str = "archive_id"
    ) -> Optional[LibraryMetadata]:
        try:
            await self._rate_limit()
            client = await self._get_client()
            resp = await client.get(f"https://archive.org/metadata/{identifier}")
            resp.raise_for_status()
            data = resp.json()
            meta_dict = data.get("metadata", {})

            creators = meta_dict.get("creator", [])
            if isinstance(creators, str):
                creators = [creators]

            subjects_raw = meta_dict.get("subject", [])
            if isinstance(subjects_raw, str):
                subjects_raw = [subjects_raw]

            return LibraryMetadata(
                title=meta_dict.get("title"),
                authors=creators,
                publication_date=meta_dict.get("date"),
                description=(
                    meta_dict.get("description", "")[:500] if meta_dict.get("description") else None
                ),
                subjects=subjects_raw[:5],
                source_apis=["internetarchive"],
                enrichment_confidence=0.70,
            )
        except (httpx.HTTPError, RuntimeError) as exc:
            logger.error("InternetArchive lookup failed: %s", exc)
        return None


# ── Library of Congress (loc.gov) ───────────────────────────────────


class LibraryOfCongressClient(BaseLibraryClient):
    """Library of Congress catalog search. No API key required."""

    async def search(self, query: str, **kwargs: Any) -> List[LibraryMetadata]:
        cache_key = f"loc:search:{query}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        try:
            await self._rate_limit()
            client = await self._get_client()
            params = {"q": query, "fo": "json", "pagesize": kwargs.get("limit", 5)}
            resp = await client.get(self.config.loc_api_base_url, params=params)
            resp.raise_for_status()
            data = resp.json()

            results = []
            for record in data.get("results", [])[:5]:
                results.append(
                    LibraryMetadata(
                        title=record.get("title"),
                        authors=record.get("creators", []),
                        publication_date=record.get("date"),
                        description=(
                            record.get("description", "")[:500]
                            if record.get("description")
                            else None
                        ),
                        subjects=record.get("subjects", [])[:5],
                        lcc=record.get("classification"),
                        source_apis=["loc"],
                        enrichment_confidence=0.80,
                    )
                )
            self._set_cache(cache_key, results)
            return results
        except (httpx.HTTPError, RuntimeError) as exc:
            logger.error("LOC search failed: %s", exc)
            return []

    async def get_by_identifier(
        self, identifier: str, id_type: str = "lccn"
    ) -> Optional[LibraryMetadata]:
        if id_type == "lccn":
            res = await self.search(identifier, limit=1)
            return res[0] if res else None
        return None


# ── Project Gutenberg via Gutendex ──────────────────────────────────


class ProjectGutenbergClient(BaseLibraryClient):
    """Project Gutenberg search via Gutendex API. No API key required.

    Gutendex: https://gutendex.com
    Search: GET /books?search={query}
    Detail: GET /books/{id}
    """

    async def search(self, query: str, **kwargs: Any) -> List[LibraryMetadata]:
        cache_key = f"gut:search:{query}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        try:
            await self._rate_limit()
            client = await self._get_client()
            params: Dict[str, Any] = {"search": query}
            resp = await client.get(
                f"{self.config.gutenberg_api_base_url}/books",
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()

            results = []
            for book in data.get("results", [])[:5]:
                authors = [
                    a.get("name", "") for a in book.get("authors", []) if isinstance(a, dict)
                ]
                subjects = book.get("subjects", [])[:5]
                languages = book.get("languages", [])

                results.append(
                    LibraryMetadata(
                        title=book.get("title"),
                        authors=authors,
                        subjects=subjects if subjects else languages,
                        cover_url=book.get("formats", {}).get("image/jpeg"),
                        source_apis=["gutenberg"],
                        enrichment_confidence=0.60,
                    )
                )
            self._set_cache(cache_key, results)
            return results
        except (httpx.HTTPError, RuntimeError) as exc:
            logger.error("Gutenberg search failed: %s", exc)
            return []

    async def get_by_identifier(
        self, identifier: str, id_type: str = "gutenberg_id"
    ) -> Optional[LibraryMetadata]:
        try:
            await self._rate_limit()
            client = await self._get_client()
            resp = await client.get(f"{self.config.gutenberg_api_base_url}/books/{identifier}")
            resp.raise_for_status()
            data = resp.json()
            authors = [a.get("name", "") for a in data.get("authors", []) if isinstance(a, dict)]

            return LibraryMetadata(
                title=data.get("title"),
                authors=authors,
                cover_url=data.get("formats", {}).get("image/jpeg"),
                source_apis=["gutenberg"],
                enrichment_confidence=0.65,
            )
        except (httpx.HTTPError, RuntimeError) as exc:
            logger.error("Gutenberg lookup failed: %s", exc)
        return None


# ============================================================================
# ORCHESTRATOR [id-soft: vet-028] WAD System — swapable, hot-pluggable data sources
# ============================================================================


class LibraryAPIOrchestrator:
    """Coordinates multiple library clients to provide enriched metadata.

    Each client is a data source "WAD" — swapable, hot-pluggable.
    Clients can be added/removed at runtime.
    """

    def __init__(self, config: Optional[LibraryAPIConfig] = None):
        self.config = config or LibraryAPIConfig()
        self.clients: Dict[str, BaseLibraryClient] = {
            "openlibrary": OpenLibraryClient(self.config),
            "internetarchive": InternetArchiveClient(self.config),
            "loc": LibraryOfCongressClient(self.config),
            "gutenberg": ProjectGutenbergClient(self.config),
        }

    def add_client(self, name: str, client: BaseLibraryClient) -> None:
        """Register a custom client."""
        self.clients[name] = client

    def remove_client(self, name: str) -> None:
        """Unregister a client."""
        self.clients.pop(name, None)

    async def enrich_metadata(self, query: str) -> List[LibraryMetadata]:
        """Search across all clients in parallel, deduplicate by title.

        Aggregates results from every registered client into a flat,
        deduplicated list. This is the primary entry point for enrichment.
        """
        results_map: Dict[str, List[LibraryMetadata]] = {}

        async with anyio.create_task_group() as tg:
            for name, client in self.clients.items():
                tg.start_soon(self._search_client, name, client, query, results_map)

        # Flatten and deduplicate by title
        seen_titles: set = set()
        unique: List[LibraryMetadata] = []
        for results in results_map.values():
            for item in results:
                title_key = (item.title or "").lower().strip()
                if title_key and title_key not in seen_titles:
                    unique.append(item)
                    seen_titles.add(title_key)

        return unique

    async def _search_client(
        self,
        name: str,
        client: BaseLibraryClient,
        query: str,
        results_map: Dict[str, List[LibraryMetadata]],
    ) -> None:
        """Wrapper around client.search() to capture results by client name."""
        try:
            results = await client.search(query)
            results_map[name] = results
        except LibraryAPIError as exc:
            logger.warning("Client '%s' search error: %s", name, exc)
            results_map[name] = []

    async def close_all(self) -> None:
        """Clean up all client connections."""
        for name, client in self.clients.items():
            try:
                await client.close()
            except Exception as e:
                logger.debug("Error closing client '%s': %s", name, e)
