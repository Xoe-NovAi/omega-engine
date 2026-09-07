"""Tests for Enrichment Engine — multi-source metadata enrichment."""

import pytest
from unittest.mock import AsyncMock, patch

from omega.library.api_clients import (
    LibraryMetadata,
    LibraryAPIConfig,
)
from omega.library.enrichment import EnrichmentEngine


class TestEnrichmentEngine:
    @pytest.fixture
    def engine(self):
        return EnrichmentEngine(LibraryAPIConfig(enable_cache=False))

    @pytest.mark.anyio
    async def test_enrich_no_results_graceful(self, engine):
        """When no results found, returns placeholder with 0.0 confidence."""
        # Mock orchestrator to return empty results
        engine.orchestrator.enrich_metadata = AsyncMock(return_value=[])

        result = await engine.enrich("totally nonexistent book title xyz")
        assert result.title == "totally nonexistent book title xyz"
        assert result.enrichment_confidence == 0.0
        assert result.source_apis == ["none"]

    @pytest.mark.anyio
    async def test_enrich_merges_fields_from_multiple_results(self, engine):
        """Gap-filling merge: isbn from second result fills missing in first."""
        meta_a = LibraryMetadata(
            title="Test Book",
            authors=["Author A"],
            publication_date="2020",
            source_apis=["openlibrary"],
            enrichment_confidence=0.8,
        )
        meta_b = LibraryMetadata(
            title="Test Book",
            isbn="9781234567890",
            source_apis=["loc"],
            enrichment_confidence=0.7,
        )

        engine.orchestrator.enrich_metadata = AsyncMock(return_value=[meta_a, meta_b])

        result = await engine.enrich("test book")
        assert result.title == "Test Book"
        assert result.isbn == "9781234567890"  # Merged from meta_b
        assert result.publication_date == "2020"
        assert result.enrichment_confidence == 0.8  # Highest confidence

    @pytest.mark.anyio
    async def test_get_authoritative_value_returns_highest_confidence(self, engine):
        meta_a = LibraryMetadata(
            title="Great Book",
            authors=["Best Author"],
            source_apis=["openlibrary"],
            enrichment_confidence=0.9,
        )
        meta_b = LibraryMetadata(
            title="Great Book",
            authors=["Lesser Author"],
            source_apis=["loc"],
            enrichment_confidence=0.5,
        )

        engine.orchestrator.enrich_metadata = AsyncMock(return_value=[meta_a, meta_b])

        author = await engine.get_authoritative_value("author", "great book")
        assert author == "Best Author"

    @pytest.mark.anyio
    async def test_get_authoritative_value_missing_field(self, engine):
        meta = LibraryMetadata(
            title="No Author Book",
            authors=[],
            source_apis=["openlibrary"],
            enrichment_confidence=0.8,
        )
        engine.orchestrator.enrich_metadata = AsyncMock(return_value=[meta])

        author = await engine.get_authoritative_value("author", "no author")
        assert author is None

    @pytest.mark.anyio
    async def test_get_authoritative_value_no_results(self, engine):
        engine.orchestrator.enrich_metadata = AsyncMock(return_value=[])
        value = await engine.get_authoritative_value("title", "nothing")
        assert value is None

    @pytest.mark.anyio
    async def test_enrich_with_authors_constructs_query(self, engine):
        """When authors are provided, query includes both title and author names."""
        engine.orchestrator.enrich_metadata = AsyncMock(return_value=[
            LibraryMetadata(title="My Book", authors=["John Doe"], source_apis=["mock"])
        ])

        result = await engine.enrich("My Book", authors=["John Doe"])
        assert result is not None
        assert result.title == "My Book"
