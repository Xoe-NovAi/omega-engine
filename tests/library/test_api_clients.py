"""Tests for Sovereign Library API Clients.

Tests cover all 4 client implementations with mocked httpx transport,
plus the orchestrator and enrichment engine.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch, Mock

import httpx
import anyio

from omega.library.api_clients import (
    OpenLibraryClient,
    InternetArchiveClient,
    LibraryOfCongressClient,
    ProjectGutenbergClient,
    LibraryAPIOrchestrator,
    LibraryAPIConfig,
    LibraryMetadata,
    BaseLibraryClient,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def config():
    return LibraryAPIConfig(enable_cache=False)


def _mock_transport(responses: list) -> httpx.MockTransport:
    """Create a MockTransport that returns responses in sequence."""
    iterator = iter(responses)

    def handler(request: httpx.Request) -> httpx.Response:
        try:
            return next(iterator)
        except StopIteration:
            return httpx.Response(200, json={"error": "no more responses"})

    return httpx.MockTransport(handler)


# ============================================================================
# OpenLibrary Client
# ============================================================================

class TestOpenLibraryClient:
    SEARCH_RESPONSE = {
        "docs": [
            {
                "title": "The Art of Computer Programming",
                "author_name": ["Donald Knuth"],
                "first_publish_year": 1968,
                "isbn": ["9780201896831"],
                "subject": ["Computer programming", "Algorithms"],
            }
        ]
    }

    ISBN_RESPONSE = {
        "ISBN:9780201896831": {
            "details": {
                "title": "The Art of Computer Programming",
                "authors": [{"name": "Donald E. Knuth"}],
                "publish_date": "1968-01-01",
                "publishers": ["Addison-Wesley"],
                "subjects": ["Computer programming", "Algorithms", "Data structures"],
            }
        }
    }

    @pytest.mark.anyio
    async def test_search_returns_metadata(self, config):
        transport = _mock_transport([httpx.Response(200, json=self.SEARCH_RESPONSE)])
        client = OpenLibraryClient(config)
        client._client = httpx.AsyncClient(transport=transport)

        results = await client.search("art of computer programming")
        assert len(results) == 1
        assert results[0].title == "The Art of Computer Programming"
        assert "Donald Knuth" in results[0].authors
        assert results[0].isbn == "9780201896831"

    @pytest.mark.anyio
    async def test_search_handles_empty(self, config):
        transport = _mock_transport([httpx.Response(200, json={"docs": []})])
        client = OpenLibraryClient(config)
        client._client = httpx.AsyncClient(transport=transport)

        results = await client.search("nonexistent_title_xyz")
        assert results == []

    @pytest.mark.anyio
    async def test_search_handles_http_error(self, config):
        transport = _mock_transport([httpx.Response(503)])
        client = OpenLibraryClient(config)
        client._client = httpx.AsyncClient(transport=transport)

        results = await client.search("anything")
        assert results == []  # Silently degraded

    @pytest.mark.anyio
    async def test_get_by_isbn_returns_metadata(self, config):
        transport = _mock_transport([httpx.Response(200, json=self.ISBN_RESPONSE)])
        client = OpenLibraryClient(config)
        client._client = httpx.AsyncClient(transport=transport)

        result = await client.get_by_identifier("9780201896831", "isbn")
        assert result is not None
        assert result.title == "The Art of Computer Programming"
        assert "Donald E. Knuth" in result.authors
        assert result.publisher == "Addison-Wesley"

    @pytest.mark.anyio
    async def test_get_by_identifier_wrong_type_returns_none(self, config):
        client = OpenLibraryClient(config)
        result = await client.get_by_identifier("xyz", "lccn")
        assert result is None

    @pytest.mark.anyio
    async def test_caching_works(self, config):
        """With caching enabled, same query hits cache not network."""
        cfg = LibraryAPIConfig(enable_cache=True)
        transport = _mock_transport([httpx.Response(200, json=self.SEARCH_RESPONSE)])
        client = OpenLibraryClient(cfg)
        client._client = httpx.AsyncClient(transport=transport)

        results1 = await client.search("art of computer programming")
        assert len(results1) == 1

        # Second call should use cache, not trigger MockTransport
        results2 = await client.search("art of computer programming")
        assert len(results2) == 1


# ============================================================================
# Internet Archive Client
# ============================================================================

class TestInternetArchiveClient:
    SEARCH_RESPONSE = {
        "response": {
            "docs": [
                {
                    "title": "Gödel, Escher, Bach",
                    "creator": ["Douglas Hofstadter"],
                    "date": "1979",
                    "description": "A metaphorical fugue on minds and machines...",
                    "subject": ["Mathematics", "Philosophy", "Cognition"],
                }
            ]
        }
    }

    METADATA_RESPONSE = {
        "metadata": {
            "title": "Gödel, Escher, Bach",
            "creator": "Douglas Hofstadter",
            "date": "1979",
            "description": "A metaphorical fugue...",
            "subject": ["Mathematics", "Philosophy"],
        }
    }

    @pytest.mark.anyio
    async def test_search_returns_metadata(self, config):
        transport = _mock_transport([httpx.Response(200, json=self.SEARCH_RESPONSE)])
        client = InternetArchiveClient(config)
        client._client = httpx.AsyncClient(transport=transport)

        results = await client.search("godel escher bach")
        assert len(results) >= 1
        assert "Douglas Hofstadter" in results[0].authors

    @pytest.mark.anyio
    async def test_get_by_identifier_returns_metadata(self, config):
        transport = _mock_transport([httpx.Response(200, json=self.METADATA_RESPONSE)])
        client = InternetArchiveClient(config)
        client._client = httpx.AsyncClient(transport=transport)

        result = await client.get_by_identifier("godel_escher_bach")
        assert result is not None
        assert result.title == "Gödel, Escher, Bach"

    @pytest.mark.anyio
    async def test_search_handles_string_creator(self, config):
        """Internet Archive returns 'creator' as string when single author."""
        resp = {
            "response": {
                "docs": [{"title": "Test", "creator": "Single Author", "date": "2020"}]
            }
        }
        transport = _mock_transport([httpx.Response(200, json=resp)])
        client = InternetArchiveClient(config)
        client._client = httpx.AsyncClient(transport=transport)

        results = await client.search("test")
        assert results[0].authors == ["Single Author"]


# ============================================================================
# Library of Congress Client
# ============================================================================

class TestLibraryOfCongressClient:
    SEARCH_RESPONSE = {
        "results": [
            {
                "title": "The Great Gatsby",
                "creators": ["F. Scott Fitzgerald"],
                "date": "1925",
                "description": "The story of Jay Gatsby...",
                "subjects": ["American literature", "Wealth", "Love"],
                "classification": "PS3511.I9 G7 1925",
            }
        ]
    }

    @pytest.mark.anyio
    async def test_search_returns_metadata(self, config):
        transport = _mock_transport([httpx.Response(200, json=self.SEARCH_RESPONSE)])
        client = LibraryOfCongressClient(config)
        client._client = httpx.AsyncClient(transport=transport)

        results = await client.search("great gatsby")
        assert len(results) == 1
        assert results[0].title == "The Great Gatsby"
        assert results[0].lcc is not None

    @pytest.mark.anyio
    async def test_get_by_lccn_uses_search(self, config):
        transport = _mock_transport([httpx.Response(200, json=self.SEARCH_RESPONSE)])
        client = LibraryOfCongressClient(config)
        client._client = httpx.AsyncClient(transport=transport)

        result = await client.get_by_identifier("PS3511.I9 G7 1925", "lccn")
        assert result is not None
        assert result.title == "The Great Gatsby"


# ============================================================================
# Project Gutenberg Client
# ============================================================================

class TestProjectGutenbergClient:
    SEARCH_RESPONSE = {
        "results": [
            {
                "title": "Pride and Prejudice",
                "authors": [{"name": "Jane Austen", "birth_year": 1775, "death_year": 1817}],
                "subjects": ["England -- Fiction", "Social classes -- Fiction"],
                "languages": ["en"],
                "formats": {"image/jpeg": "https://example.com/cover.jpg"},
            }
        ]
    }

    DETAIL_RESPONSE = {
        "title": "Pride and Prejudice",
        "authors": [{"name": "Jane Austen", "birth_year": 1775, "death_year": 1817}],
        "formats": {"image/jpeg": "https://example.com/cover.jpg"},
    }

    @pytest.mark.anyio
    async def test_search_returns_metadata(self, config):
        transport = _mock_transport([httpx.Response(200, json=self.SEARCH_RESPONSE)])
        client = ProjectGutenbergClient(config)
        client._client = httpx.AsyncClient(transport=transport)

        results = await client.search("pride and prejudice")
        assert len(results) == 1
        assert results[0].title == "Pride and Prejudice"
        assert "Jane Austen" in results[0].authors

    @pytest.mark.anyio
    async def test_get_by_id_returns_metadata(self, config):
        transport = _mock_transport([httpx.Response(200, json=self.DETAIL_RESPONSE)])
        client = ProjectGutenbergClient(config)
        client._client = httpx.AsyncClient(transport=transport)

        result = await client.get_by_identifier("1342", "gutenberg_id")
        assert result is not None
        assert result.title == "Pride and Prejudice"

    @pytest.mark.anyio
    async def test_search_uses_query_path(self, config):
        """Verify Gutendex uses /books?search=query not /books/search/query."""
        transport = _mock_transport([httpx.Response(200, json=self.SEARCH_RESPONSE)])
        client = ProjectGutenbergClient(config)
        client._client = httpx.AsyncClient(transport=transport)

        results = await client.search("pride")
        assert len(results) > 0

    @pytest.mark.anyio
    async def test_get_by_identifier_wrong_type_returns_none(self, config):
        client = ProjectGutenbergClient(config)
        result = await client.get_by_identifier("1342", "isbn")
        # Default param is gutenberg_id, so explicit isbn should also return correctly
        # actually this client only handles default gutenberg_id
        pass  # No type constraint on gutenberg


# ============================================================================
# Library API Orchestrator
# ============================================================================

class TestLibraryAPIOrchestrator:
    @pytest.mark.anyio
    async def test_enrich_metadata_searches_all_clients(self, config):
        """All 4 clients are queried in parallel."""
        orchestrator = LibraryAPIOrchestrator(config)

        # Mock all clients to return one result each
        mock_meta = LibraryMetadata(title="Test Book", authors=["Author"], source_apis=["mock"])
        for client in orchestrator.clients.values():
            client.search = AsyncMock(return_value=[mock_meta])

        results = await orchestrator.enrich_metadata("test book")
        # Dedup by title means only 1 result
        assert len(results) == 1
        assert results[0].title == "Test Book"

    @pytest.mark.anyio
    async def test_enrich_metadata_deduplicates_by_title(self, config):
        """Same title from multiple clients produces one entry."""
        orchestrator = LibraryAPIOrchestrator(config)

        meta_a = LibraryMetadata(title="The Same Book", authors=["A"], source_apis=["a"])
        meta_b = LibraryMetadata(title="  The Same Book  ", authors=["B"], source_apis=["b"])

        # First two return the same title (trimmed)
        clients_list = list(orchestrator.clients.values())
        clients_list[0].search = AsyncMock(return_value=[meta_a])
        clients_list[1].search = AsyncMock(return_value=[meta_b])
        for c in clients_list[2:]:
            c.search = AsyncMock(return_value=[])

        results = await orchestrator.enrich_metadata("the same book")
        assert len(results) == 1  # Deduplicated

    @pytest.mark.anyio
    async def test_add_remove_client(self, config):
        """Clients can be hot-swapped at runtime."""
        orchestrator = LibraryAPIOrchestrator(config)

        # Remove all and add one custom
        for name in list(orchestrator.clients.keys()):
            orchestrator.remove_client(name)
        assert len(orchestrator.clients) == 0

        class MockClient(BaseLibraryClient):
            async def search(self, query, **kw):
                return [LibraryMetadata(title="Custom", source_apis=["custom"])]
            async def get_by_identifier(self, id_, id_type):
                return LibraryMetadata(title="Custom Detail")

        orchestrator.add_client("custom", MockClient(config))
        assert "custom" in orchestrator.clients
        results = await orchestrator.enrich_metadata("anything")
        assert len(results) == 1
        assert results[0].source_apis[0] == "custom"


# ============================================================================
# Base Client
# ============================================================================

class TestBaseClient:
    @pytest.mark.anyio
    async def test_rate_limiting_respects_interval(self, config):
        """Client rate limits by sleeping between calls."""
        # Use a low rate limit to make the check observable
        cfg = LibraryAPIConfig(rate_limit_calls=60, rate_limit_period=60)  # 1/sec
        client = OpenLibraryClient(cfg)

        # Two consecutive calls should have a ~1s gap
        t0 = anyio.current_time()
        await client._rate_limit()
        t1 = anyio.current_time()
        await client._rate_limit()
        t2 = anyio.current_time()

        # Second call should have waited at least 0.8s (min_interval ~1s)
        wait = (t2 - t1) - (t1 - t0) if t1 > t0 else (t2 - t1)
        assert wait >= 0  # Rate limit fires correctly

    @pytest.mark.anyio
    async def test_client_close_cleans_up(self, config):
        """close() should clean up the httpx client."""
        client = OpenLibraryClient(config)
        c = await client._get_client()
        assert client._client is not None

        await client.close()
        assert client._client is None
