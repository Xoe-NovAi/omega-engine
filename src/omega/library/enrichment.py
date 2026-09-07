# AP: AP-OMEGA-ENRICHMENT-v1.1.0
"""Sovereign Library Enrichment — Thin wrapper over canonical API clients.

AP: AP-OMEGA-ENRICHMENT-v1.1.0
[carmack-law: id-software] Consolidated from duplicated implementation.
Canonical source: api_clients.py. This file re-exports and adds higher-level
orchestration only — no duplicated client code.

The Enrichment Layer of the Sovereign Extraction Loop transforms raw extracted
content into curated assets using free, no-key-required library APIs.
"""

# DocRef: docs/architecture/KNOWLEDGE_LIBRARY.md

import logging
from typing import Any, Dict, List, Optional


# ── Canonical source for all client implementations ─────────────────────
from omega.library.api_clients import (
    LibraryAPIConfig,
    LibraryMetadata,
    LibraryAPIOrchestrator,  # coordinates all 4 clients
)

logger = logging.getLogger(__name__)

# ============================================================================
# ENRICHMENT ENGINE — Thin orchestration layer
# ============================================================================


class EnrichmentEngine:
    """Coordinates multiple library clients to enrich a curated document.

    This is a thin wrapper around LibraryAPIOrchestrator that adds
    result merging and authoritative value extraction. All real client
    logic lives in api_clients.py.
    """

    def __init__(self, config: Optional[LibraryAPIConfig] = None):
        self.config = config or LibraryAPIConfig()
        self.orchestrator = LibraryAPIOrchestrator(self.config)

    async def enrich(self, title: str, authors: Optional[List[str]] = None) -> LibraryMetadata:
        """Multi-API search merging best metadata into a single result.

        Searches all clients in parallel via the orchestrator, then
        merges results by filling gaps from lower-confidence matches.

        Returns:
            LibraryMetadata with best available fields merged.
        """
        query = title
        if authors:
            query = f"{title} {', '.join(authors)}"

        results = await self.orchestrator.enrich_metadata(query)
        if not results:
            return LibraryMetadata(
                title=title,
                authors=authors or [],
                source_apis=["none"],
                enrichment_confidence=0.0,
            )

        # Sort by confidence and merge: fill gaps from best match
        results.sort(key=lambda x: x.enrichment_confidence, reverse=True)
        best = results[0]
        for other in results[1:]:
            if not best.isbn and other.isbn:
                best.isbn = other.isbn
            if not best.publication_date and other.publication_date:
                best.publication_date = other.publication_date
            if not best.publisher and other.publisher:
                best.publisher = other.publisher
            if not best.subjects and other.subjects:
                best.subjects = other.subjects

        return best

    async def get_authoritative_value(self, field: str, query: str) -> Optional[str]:
        """Get an authoritative value for a specific metadata field.

        Used by TriangulationVerifier for Sovereign verification.
        Searches all clients, returns the field from the highest-confidence match.

        Supported fields: author, date, doi, title, isbn, publisher
        """
        results = await self.orchestrator.enrich_metadata(query)
        if not results:
            return None

        results.sort(key=lambda x: x.enrichment_confidence, reverse=True)
        best = results[0]

        extractors = {
            "author": lambda m: m.authors[0] if m.authors else None,
            "date": lambda m: m.publication_date,
            "title": lambda m: m.title,
            "isbn": lambda m: m.isbn,
            "publisher": lambda m: m.publisher,
        }
        extractor = extractors.get(field)
        if extractor:
            value = extractor(best)
            if value:
                logger.debug("Authoritative '%s' = %s (from %s)", field, value, best.source_apis)
                return str(value)

        return None


# ============================================================================
# HIGH-LEVEL WRAPPER
# ============================================================================


async def enrich_document(
    doc_body: str,
    doc_title: str,
    authors: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Quick-entry enrichment for a document body + title.

    Args:
        doc_body: The full document text (used for future extraction).
        doc_title: Title to search for metadata enrichment.
        authors: Optional list of authors to narrow the search.

    Returns:
        Dict of enriched LibraryMetadata fields.
    """
    engine = EnrichmentEngine()
    metadata = await engine.enrich(doc_title, authors)
    return metadata.to_dict()
