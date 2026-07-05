# AP: AP-OMEGA-ENRICHMENT-v1.0.0
"""Sovereign Library Enrichment — Authoritative metadata augmentation.

AP: AP-OMEGA-ENRICHMENT-v1.0.0
ICS: [NODE: KNOWLEDGE | ARCHETYPE: HERMES | CONTEXT: ENRICHMENT-PIPELINE]

This module provides the Enrichment Layer of the Sovereign Extraction Loop.
It leverages a suite of free, no-key-required library APIs to transform 
raw extracted content into scholarly-grade curated assets.

Sovereign Mandate M7 (Local-First) is respected by using public, 
non-telemetry APIs and local caching.
"""

import anyio
import logging
import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Type
from enum import Enum
from abc import ABC, abstractmethod
from pathlib import Path

import httpx
from omega.errors import OmegaError

logger = logging.getLogger(__name__)

# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class DomainCategory(str, Enum):
    """Enhanced domain categorization for multi-source curation."""
    CODE = "code"
    SCIENCE = "science"
    DATA = "data"
    GENERAL = "general"
    BOOKS = "books"
    MUSIC = "music"
    ARCHIVES = "archives"
    MANUSCRIPTS = "manuscripts"
    PHOTOGRAPHS = "photographs"
    AUDIO = "audio"
    FICTION = "fiction"
    REFERENCE = "reference"
    PODCAST = "podcast"
    AUDIOBOOK = "audiobook"

class DeweyDecimalClass(str, Enum):
    """Dewey Decimal Classification system mapping for libraries."""
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
# CONFIGURATION & MODELS
# ============================================================================

@dataclass
class LibraryAPIConfig:
    """Configuration for library API integrations."""
    google_books_api_key: Optional[str] = None
    isbndb_api_key: Optional[str] = None
    loc_api_base_url: str = "https://www.loc.gov/books/services/web/search.json"
    openlibrary_api_base_url: str = "https://openlibrary.org"
    archive_api_base_url: str = "https://archive.org/advancedsearch.php"
    worldcat_api_base_url: str = "https://www.worldcat.org/cgi-bin/json_webservice"
    gutenberg_api_base_url: str = "https://gutendex.com"
    podcastindex_api_base_url: str = "https://api.podcastindex.org/api/1.0"
    lastfm_api_base_url: str = "https://www.last.fm/api/0.2"
    
    rate_limit_calls: int = 10
    rate_limit_period: int = 60
    request_timeout: int = 10
    cache_ttl: int = 3600
    enable_cache: bool = True
    user_agent: str = "OmegaEngine/1.0 (Sovereign Research Bot; +https://github.com/Xoe-NovAi/omega-engine)"

@dataclass
class LibraryMetadata:
    """Enriched metadata from library APIs."""
    isbn: Optional[str] = None
    title: Optional[str] = None
    authors: List[str] = field(default_factory=list)
    publication_date: Optional[str] = None
    publisher: Optional[str] = None
    description: Optional[str] = None
    subjects: List[str] = field(default_factory=list)
    dewey_decimal: Optional[str] = None
    oclc_number: Optional[str] = None
    lcc: Optional[str] = None
    language: Optional[str] = None
    page_count: Optional[int] = None
    cover_url: Optional[str] = None
    source_apis: List[str] = field(default_factory=list)
    enrichment_confidence: float = 0.0
    
    # Audio-specific
    is_audio: bool = False
    audio_type: Optional[str] = None
    podcast_id: Optional[str] = None
    podcast_url: Optional[str] = None
    duration: Optional[int] = None
    format: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

# ============================================================================
# BASE CLIENT
# ============================================================================

class BaseLibraryClient(ABC):
    """Abstract base for AnyIO-native library API clients."""
    
    def __init__(self, config: LibraryAPIConfig):
        self.config = config
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.last_request_time = 0.0

    async def _rate_limit(self):
        """Enforce rate limiting using AnyIO sleep."""
        elapsed = datetime.now().timestamp() - self.last_request_time
        min_interval = self.config.rate_limit_period / self.config.rate_limit_calls
        if elapsed < min_interval:
            await anyio.sleep(min_interval - elapsed)
        self.last_request_time = datetime.now().timestamp()

    def _get_cached(self, key: str) -> Optional[Any]:
        if not self.config.enable_cache or key not in self.cache:
            return None
        value, timestamp = self.cache[key]
        if datetime.now().timestamp() - timestamp > self.config.cache_ttl:
            del self.cache[key]
            return None
        return value

    def _set_cache(self, key: str, value: Any):
        if self.config.enable_cache:
            self.cache[key] = (value, datetime.now().timestamp())

    @abstractmethod
    async def search(self, query: str, **kwargs) -> List[LibraryMetadata]:
        pass

    @abstractmethod
    async def get_by_identifier(self, identifier: str, id_type: str) -> Optional[LibraryMetadata]:
        pass

# ============================================================================
# IMPLEMENTATIONS
# ============================================================================

class OpenLibraryClient(BaseLibraryClient):
    async def search(self, query: str, **kwargs) -> List[LibraryMetadata]:
        cache_key = f"ol:search:{query}"
        cached = self._get_cached(cache_key)
        if cached: return cached

        try:
            await self._rate_limit()
            async with httpx.AsyncClient(timeout=self.config.request_timeout) as client:
                params = {"title": query, "limit": kwargs.get("limit", 5)}
                headers = {"User-Agent": self.config.user_agent}
                resp = await client.get(f"{self.config.openlibrary_api_base_url}/search.json", params=params, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                
                results = []
                for doc in data.get("docs", [])[:5]:
                    results.append(LibraryMetadata(
                        isbn=doc.get("isbn")[0] if doc.get("isbn") else None,
                        title=doc.get("title"),
                        authors=doc.get("author_name", []),
                        publication_date=str(doc.get("first_publish_year", "")),
                        subjects=doc.get("subject", [])[:5],
                        source_apis=["openlibrary"],
                        enrichment_confidence=0.7
                    ))
                self._set_cache(cache_key, results)
                return results
        except (httpx.HTTPError, RuntimeError) as e:
            logger.error(f"OpenLibrary search failed: {e}")
            return []

    async def get_by_identifier(self, identifier: str, id_type: str = "isbn") -> Optional[LibraryMetadata]:
        if id_type != "isbn": return None
        cache_key = f"ol:isbn:{identifier}"
        cached = self._get_cached(cache_key)
        if cached: return cached

        try:
            await self._rate_limit()
            async with httpx.AsyncClient(timeout=self.config.request_timeout) as client:
                params = {"bibkeys": f"ISBN:{identifier}", "jscmd": "details", "format": "json"}
                headers = {"User-Agent": self.config.user_agent}
                resp = await client.get(f"{self.config.openlibrary_api_base_url}/api/books", params=params, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                if data:
                    key = list(data.keys())[0]
                    details = data[key].get("details", {})
                    meta = LibraryMetadata(
                        isbn=identifier,
                        title=details.get("title"),
                        authors=[a.get("name") for a in details.get("authors", [])],
                        publication_date=str(details.get("publish_date", "")),
                        publisher=details.get("publishers", [None])[0] if details.get("publishers") else None,
                        subjects=details.get("subjects", [])[:5],
                        source_apis=["openlibrary"],
                        enrichment_confidence=0.85
                    )
                    self._set_cache(cache_key, meta)
                    return meta
        except (httpx.HTTPError, RuntimeError) as e:
            logger.error(f"OpenLibrary lookup failed: {e}")
        return None

class InternetArchiveClient(BaseLibraryClient):
    async def search(self, query: str, **kwargs) -> List[LibraryMetadata]:
        cache_key = f"ia:search:{query}"
        cached = self._get_cached(cache_key)
        if cached: return cached

        try:
            await self._rate_limit()
            async with httpx.AsyncClient(timeout=self.config.request_timeout) as client:
                params = {
                    "q": f"(title:{query} OR description:{query}) AND mediatype:texts",
                    "output": "json",
                    "rows": kwargs.get("limit", 5),
                    "fl": ["identifier", "title", "creator", "date", "description", "subject"]
                }
                resp = await client.get(self.config.archive_api_base_url, params=params)
                resp.raise_for_status()
                data = resp.json()
                
                results = []
                for doc in data.get("response", {}).get("docs", [])[:5]:
                    creators = doc.get("creator", [])
                    if isinstance(creators, str): creators = [creators]
                    results.append(LibraryMetadata(
                        title=doc.get("title"),
                        authors=creators,
                        publication_date=doc.get("date"),
                        description=doc.get("description", "")[:500] if doc.get("description") else None,
                        subjects=doc.get("subject", [])[:5] if doc.get("subject") else [],
                        source_apis=["internetarchive"],
                        enrichment_confidence=0.65
                    ))
                self._set_cache(cache_key, results)
                return results
        except (httpx.HTTPError, RuntimeError) as e:
            logger.error(f"InternetArchive search failed: {e}")
            return []

    async def get_by_identifier(self, identifier: str, id_type: str = "archive_id") -> Optional[LibraryMetadata]:
        try:
            await self._rate_limit()
            async with httpx.AsyncClient(timeout=self.config.request_timeout) as client:
                resp = await client.get(f"https://archive.org/metadata/{identifier}")
                resp.raise_for_status()
                data = resp.json()
                meta_dict = data.get("metadata", {})
                creators = meta_dict.get("creator", [])
                if isinstance(creators, str): creators = [creators]
                
                return LibraryMetadata(
                    title=meta_dict.get("title"),
                    authors=creators,
                    publication_date=meta_dict.get("date"),
                    description=meta_dict.get("description", "")[:500] if meta_dict.get("description") else None,
                    subjects=meta_dict.get("subject", [])[:5] if isinstance(meta_dict.get("subject"), list) else [],
                    source_apis=["internetarchive"],
                    enrichment_confidence=0.70
                )
        except (httpx.HTTPError, RuntimeError) as e:
            logger.error(f"InternetArchive lookup failed: {e}")
        return None

class LibraryOfCongressClient(BaseLibraryClient):
    async def search(self, query: str, **kwargs) -> List[LibraryMetadata]:
        cache_key = f"loc:search:{query}"
        cached = self._get_cached(cache_key)
        if cached: return cached

        try:
            await self._rate_limit()
            async with httpx.AsyncClient(timeout=self.config.request_timeout) as client:
                params = {"q": query, "fo": "json", "pagesize": kwargs.get("limit", 5)}
                resp = await client.get(self.config.loc_api_base_url, params=params)
                resp.raise_for_status()
                data = resp.json()
                
                results = []
                for record in data.get("results", [])[:5]:
                    results.append(LibraryMetadata(
                        title=record.get("title"),
                        authors=record.get("creators", []),
                        publication_date=record.get("date"),
                        description=record.get("description", "")[:500] if record.get("description") else None,
                        subjects=record.get("subjects", [])[:5],
                        lcc=record.get("classification"),
                        source_apis=["loc"],
                        enrichment_confidence=0.80
                    ))
                self._set_cache(cache_key, results)
                return results
        except (httpx.HTTPError, RuntimeError) as e:
            logger.error(f"LOC search failed: {e}")
            return []

    async def get_by_identifier(self, identifier: str, id_type: str = "lccn") -> Optional[LibraryMetadata]:
        if id_type == "lccn":
            res = await self.search(identifier, limit=1)
            return res[0] if res else None
        return None

class ProjectGutenbergClient(BaseLibraryClient):
    async def search(self, query: str, **kwargs) -> List[LibraryMetadata]:
        cache_key = f"gutenberg:search:{query}"
        cached = self._get_cached(cache_key)
        if cached: return cached

        try:
            await self._rate_limit()
            async with httpx.AsyncClient(timeout=self.config.request_timeout) as client:
                params = {"query": query, "topic": "all"}
                resp = await client.get(f"{self.config.gutenberg_api_base_url}/books/search", params=params)
                resp.raise_for_status()
                data = resp.json()
                
                results = []
                for book in data.get("results", [])[:5]:
                    results.append(LibraryMetadata(
                        title=book.get("title"),
                        authors=book.get("authors", []),
                        publication_date=book.get("publication_date"),
                        subjects=book.get("languages", []),
                        source_apis=["gutenberg"],
                        enrichment_confidence=0.60
                    ))
                self._set_cache(cache_key, results)
                return results
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Gutenberg search failed: {e}")
            return []

    async def get_by_identifier(self, identifier: str, id_type: str = "gutenberg_id") -> Optional[LibraryMetadata]:
        try:
            await self._rate_limit()
            async with httpx.AsyncClient(timeout=self.config.request_timeout) as client:
                resp = await client.get(f"{self.config.gutenberg_api_base_url}/books/{identifier}")
                resp.raise_for_status()
                data = resp.json()
                return LibraryMetadata(
                    title=data.get("title"),
                    authors=[a.get("name") for a in data.get("authors", [])],
                    publication_date=data.get("publication_date"),
                    cover_url=data.get("cover_image"),
                    source_apis=["gutenberg"],
                    enrichment_confidence=0.65
                )
        except (httpx.HTTPError, RuntimeError) as e:
            logger.error(f"Gutenberg lookup failed: {e}")
        return None

# ============================================================================
# ENRICHMENT ENGINE
# ============================================================================

class EnrichmentEngine:
    """Coordinates multiple library clients to enrich a curated document."""
    
    def __init__(self, config: Optional[LibraryAPIConfig] = None):
        self.config = config or LibraryAPIConfig()
        self.clients: Dict[str, BaseLibraryClient] = {
            "openlibrary": OpenLibraryClient(self.config),
            "internetarchive": InternetArchiveClient(self.config),
            "loc": LibraryOfCongressClient(self.config),
            "gutenberg": ProjectGutenbergClient(self.config),
        }

    async def enrich(self, title: str, authors: List[str] = None) -> LibraryMetadata:
        """
        Perform a multi-API search to find the best metadata match.
        Returns a merged LibraryMetadata object.
        """
        query = title
        if authors:
            query = f"{title} {', '.join(authors)}"
        
        # Parallel search across all clients
        async with anyio.create_task_group() as tg:
            results_map = {}
            for name, client in self.clients.items():
                tg.start_soon(self._search_and_store, name, client, query, results_map)
        
        # Merge results based on confidence
        all_results = []
        for results in results_map.values():
            all_results.extend(results)
        
        if not all_results:
            return LibraryMetadata(title=title, authors=authors or [], source_apis=["none"], enrichment_confidence=0.0)
        
        # Sort by confidence and merge
        all_results.sort(key=lambda x: x.enrichment_confidence, reverse=True)
        best_match = all_results[0]
        
        # Simple merge: fill gaps in best_match with other results
        for other in all_results[1:]:
            if not best_match.isbn and other.isbn: best_match.isbn = other.isbn
            if not best_match.publication_date and other.publication_date: best_match.publication_date = other.publication_date
            if not best_match.publisher and other.publisher: best_match.publisher = other.publisher
            if not best_match.subjects and other.subjects: best_match.subjects = other.subjects
            
        return best_match

    async def _search_and_store(self, name: str, client: BaseLibraryClient, query: str, results_map: Dict):
        results = await client.search(query)
        results_map[name] = results

    async def get_authoritative_value(self, field: str, query: str) -> Optional[str]:
        """
        Get an authoritative value for a specific metadata field.
        Used by TriangulationVerifier for Sovereign-Sieve.
        
        Args:
            field: The metadata field (author, date, doi, title)
            query: The search query (title, DOI, etc.)
            
        Returns:
            Authoritative value if found, None otherwise.
        """
        try:
            # Search across all clients for this specific field
            async with anyio.create_task_group() as tg:
                results_map = {}
                for name, client in self.clients.items():
                    tg.start_soon(self._search_and_store, name, client, query, results_map)
            
            # Extract the field from the best match
            all_results = []
            for results in results_map.values():
                all_results.extend(results)
            
            if not all_results:
                return None
            
            # Sort by confidence
            all_results.sort(key=lambda x: x.enrichment_confidence, reverse=True)
            best_match = all_results[0]
            
            # Extract the requested field
            field_map = {
                "author": lambda m: m.authors[0] if m.authors else None,
                "date": lambda m: m.publication_date,
                "doi": lambda m: m.doi,
                "title": lambda m: m.title,
                "isbn": lambda m: m.isbn,
                "publisher": lambda m: m.publisher,
            }
            
            extractor = field_map.get(field)
            if extractor:
                value = extractor(best_match)
                if value:
                    logger.debug(f"Authoritative value for '{field}': {value} (from {best_match.source_apis})")
                    return str(value)
            
            return None
            
        except (OmegaError, RuntimeError, OSError) as e:
            logger.warning(f"Failed to get authoritative value for '{field}': {e}")
            return None

# ============================================================================
# INTEGRATION WRAPPER
# ============================================================================

async def enrich_document(doc_body: str, doc_title: str, authors: List[str] = None) -> Dict[str, Any]:
    """High-level entry point for document enrichment."""
    engine = EnrichmentEngine()
    metadata = await engine.enrich(doc_title, authors)
    return metadata.to_dict()
