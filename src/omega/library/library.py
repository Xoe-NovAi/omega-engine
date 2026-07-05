# AP: AP-ORACLE-RESTORE-v2.3.0
"""Offline Library — Persistent storage, search, and retrieval of curated content.

AP: AP-OMEGA-LIBRARY-STORE-v1.0.0
ICS: [NODE: KNOWLEDGE | ARCHETYPE: MNEMOSYNE | CONTEXT: LIBRARY-STORE]

The library is the canonical knowledge repository. All curated documents
are stored as JSON files with full-text search support via indexed metadata.
Vector search is handled by the Indexer module (separate concern).

Storage layout:
  data/library/
    documents/{doc_id}.json   — Full curated document
    sources/{domain}/         — Organized by domain for browsing
    index/                    — Search indices
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import anyio

from .curator import CuratedDocument
from .indexer import Indexer

logger = logging.getLogger(__name__)

DATA_DIR = Path(os.environ.get("OMEGA_DATA_DIR", str(Path.home() / "omega" / "data")))
LIBRARY_DIR = DATA_DIR / "library"
DOCUMENTS_DIR = LIBRARY_DIR / "documents"
SOURCES_DIR = LIBRARY_DIR / "sources"

for d in [DOCUMENTS_DIR, SOURCES_DIR]:
    d.mkdir(parents=True, exist_ok=True)


class Library:
    """Offline content library with storage, search, and retrieval."""

    def __init__(self):
        self._documents: Dict[str, CuratedDocument] = {}
        self._index_ensured: bool = False
        # Use QdrantAdapter with sovereign fallback to MemoryVectorAdapter
        from omega.memory.vector_adapters import QdrantAdapter
        self._indexer = Indexer(vector_adapter=QdrantAdapter())
        self._load()

    def _load(self) -> None:
        for path in DOCUMENTS_DIR.glob("*.json"):
            try:
                with open(path) as f:
                    data = json.load(f)
                    doc = CuratedDocument(**data)
                    self._documents[doc.doc_id] = doc
            except (json.JSONDecodeError, TypeError, OSError) as e:
                logger.warning(f"Failed to load document {path}: {e}")
        logger.info(f"Library loaded: {len(self._documents)} documents")

    async def _ensure_index(self) -> None:
        """Auto-rebuild the FTS5 index if it's empty but documents exist.

        [id-soft: doom-1993] FTS5 Index Rebuild — WAD directory rebuild pattern.
        Called once at startup to ensure search is functional immediately.
        """
        stats = await self._indexer.stats()
        if stats.get("fts_documents", 0) == 0 and self._documents:
            logger.info(
                "FTS index empty (%d docs stored). Auto-rebuilding...",
                len(self._documents),
            )
            count = 0
            for doc in self._documents.values():
                await self._indexer.index_document(doc)
                count += 1
            await self._indexer.flush()
            stats = await self._indexer.stats()
            logger.info("FTS index rebuilt: %s", stats)

    async def _ensure_index_lazy(self) -> None:
        """Lazily rebuild the FTS5 index on the first async call, if needed."""
        if not self._index_ensured:
            self._index_ensured = True
            await self._ensure_index()

    async def store(self, document: CuratedDocument) -> None:
        """Store a curated document in the library."""
        await self._ensure_index_lazy()
        path = DOCUMENTS_DIR / f"{document.doc_id}.json"
        async with await anyio.open_file(str(path), "w") as f:
            await f.write(json.dumps(document.to_dict(), indent=2, default=str))

        domain_dir = SOURCES_DIR / (document.domain or "general")
        domain_dir.mkdir(parents=True, exist_ok=True)
        link_path = domain_dir / f"{document.doc_id}.json"
        if not link_path.exists():
            async with await anyio.open_file(str(link_path), "w") as f:
                await f.write(json.dumps({"doc_id": document.doc_id, "title": document.title, "domain": document.domain}, indent=2))

        self._documents[document.doc_id] = document
        await self._indexer.index_document(document)
        # Notify Hivemind about new knowledge (Phase 4 H2-N)
        try:
            from .hivemind_bridge import BRIDGE
            await BRIDGE.publish_new_document(document)
        except ImportError:
            pass  # hivemind_bridge not yet created
        logger.info(f"Library stored: {document.title} [{document.domain}]")

    async def get(self, doc_id: str) -> Optional[CuratedDocument]:
        """Retrieve a document by ID."""
        await self._ensure_index_lazy()
        if doc_id in self._documents:
            return self._documents[doc_id]
        path = DOCUMENTS_DIR / f"{doc_id}.json"
        if path.exists():
            try:
                async with await anyio.open_file(str(path)) as f:
                    data = json.loads(await f.read())
                doc = CuratedDocument(**data)
                self._documents[doc.doc_id] = doc
                return doc
            except (json.JSONDecodeError, TypeError, OSError) as e:
                logger.warning(f"Failed to load {doc_id}: {e}")
        return None

    async def search(self, query: str, domain: Optional[str] = None, limit: int = 20) -> List[CuratedDocument]:
        """Hybrid search across all documents using FTS5 + vector RRF.

        Uses Reciprocal Rank Fusion to merge BM25 keyword scores with
        Qdrant vector cosine similarity. Falls back to FTS5-only if
        Qdrant is unavailable (handled by vector adapter).
        """
        await self._ensure_index_lazy()
        # Call hybrid_search which uses RRF to merge FTS + vector results
        results = await self._indexer.hybrid_search(query, domain, limit)
        
        # Look up full CuratedDocument for each result
        docs = []
        for res in results:
            doc = await self.get(res["doc_id"])
            if doc:
                docs.append(doc)
        
        return docs

    async def search_by_domain(self, domain: str, limit: int = 50) -> List[CuratedDocument]:
        """List all documents in a domain."""
        docs = [d for d in self._documents.values() if d.domain == domain]
        docs.sort(key=lambda d: d.quality_score, reverse=True)
        return docs[:limit]

    async def search_by_tag(self, tag: str, limit: int = 50) -> List[CuratedDocument]:
        """List documents with a specific tag."""
        tag_lower = tag.lower()
        docs = [d for d in self._documents.values() if any(tag_lower in t.lower() for t in d.tags)]
        docs.sort(key=lambda d: d.quality_score, reverse=True)
        return docs[:limit]

    async def recent(self, limit: int = 20) -> List[CuratedDocument]:
        """Get most recently curated documents."""
        docs = sorted(self._documents.values(), key=lambda d: d.curated_at, reverse=True)
        return docs[:limit]

    async def domains(self) -> Dict[str, int]:
        """Get document counts by domain."""
        counts: Dict[str, int] = {}
        for doc in self._documents.values():
            d = doc.domain or "general"
            counts[d] = counts.get(d, 0) + 1
        return counts

    async def count(self) -> int:
        return len(self._documents)

    async def close(self) -> None:
        """Close the search index and flush any pending data."""
        await self._indexer.close()

    async def stats(self) -> Dict[str, Any]:
        await self._ensure_index_lazy()
        domains = await self.domains()
        total = await self.count()
        avg_score = sum(d.quality_score for d in self._documents.values()) / max(total, 1)
        return {
            "total_documents": total,
            "domains": domains,
            "average_quality_score": round(avg_score, 2),
            "total_words": sum(d.word_count for d in self._documents.values()),
        }

    async def delete(self, doc_id: str) -> bool:
        """Delete a document from the library."""
        await self._ensure_index_lazy()
        if doc_id not in self._documents:
            return False
        doc = self._documents[doc_id]
        path = DOCUMENTS_DIR / f"{doc_id}.json"
        if path.exists():
            path.unlink()
        await self._indexer.remove_document(doc_id)
        domain_dir = SOURCES_DIR / (doc.domain or "general")
        link_path = domain_dir / f"{doc_id}.json"
        if link_path.exists():
            link_path.unlink()
        del self._documents[doc_id]
        logger.info(f"Library deleted: {doc.title}")
        return True

    async def ingest_from_inbox(
        self,
        inbox_manager: Any,
        curation_pipeline: Any,
        limit: int = 5,
    ) -> List[CuratedDocument]:
        """Process pending inbox items through curation into the library."""
        from .inbox import InboxItem
        pending = await inbox_manager.list_pending(limit=limit)
        ingested = []
        for item in pending:
            await inbox_manager.mark_processing(item.item_id)
            try:
                doc = await curation_pipeline.process(
                    source=item.source,
                    source_type=item.source_type,
                    title=item.title,
                    tags=item.tags,
                    metadata=item.metadata,
                )
                if curation_pipeline.is_above_threshold(doc):
                    await self.store(doc)
                    ingested.append(doc)
                    await inbox_manager.mark_completed(item.item_id)
                else:
                    logger.info(f"Below threshold, skipping: {doc.title} (score={doc.quality_score:.2f})")
                    await inbox_manager.mark_completed(item.item_id)
            except (OmegaError, RuntimeError, OSError) as e:
                logger.error(f"Failed to ingest {item.source}: {e}")
                await inbox_manager.mark_failed(item.item_id, str(e))
        return ingested

    def _relevance(self, doc: CuratedDocument, query_lower: str) -> float:
        score = 0.0
        if query_lower in doc.title.lower():
            score += 0.4
        if query_lower in doc.summary.lower():
            score += 0.3
        count = doc.body.lower().count(query_lower)
        score += min(count * 0.01, 0.3)
        score += doc.quality_score * 0.2
        return score
