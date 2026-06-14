# AP Token: AP-ORACLE-RESTORE-v2.3.0
"""Search Indexing — Full-text and vector search indexing for the library.

AP: AP-OMEGA-INDEXER-v1.0.0
ICS: [NODE: KNOWLEDGE | ARCHETYPE: APOLLO | CONTEXT: INDEXER]

Provides:
  - Full-text search via SQLite FTS5 (aiosqlite, AnyIO-compatible)
  - Optional vector search via numpy cosine similarity (lightweight)
  - Incremental index updates (no full rebuild needed)

AnyIO compliance: yes (uses aiosqlite, no blocking calls).
"""

import json
import logging
import math
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import anyio
from omega.errors import (
    OmegaError, ProviderError, ProviderRateLimitError, ProviderAuthError,
    ProviderTimeoutError, ProviderUnavailableError, ProviderValidationError,
    ProviderSafetyError, InferenceError, InferenceOOMError, InferenceLoadError,
    InferenceRuntimeError, OmegaPersistenceError, SoulCorruptionError,
    SessionPersistenceError, StateIntegrityError, SovereignDiskFullError,
    ConfigError, WADError, BoundaryViolationError, InvariantViolationError,
    EntityTombstonedError, ModelNotFoundError,
)

from .curator import CuratedDocument
from omega.memory.vector_adapters import IVectorStoreAdapter, QdrantAdapter, MemoryVectorAdapter

logger = logging.getLogger(__name__)

def _get_db_path() -> Path:
    data_dir = Path(os.environ.get("OMEGA_DATA_DIR", str(Path(__file__).resolve().parent.parent.parent / "data")))
    index_dir = data_dir / "library" / "index"
    index_dir.mkdir(parents=True, exist_ok=True)
    return index_dir / "fts_index.db"

def _get_vector_path() -> Path:
    data_dir = Path(os.environ.get("OMEGA_DATA_DIR", str(Path(__file__).resolve().parent.parent.parent / "data")))
    return data_dir / "library" / "index" / "vectors.json"


_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "need", "dare",
    "this", "that", "these", "those", "i", "me", "my", "we", "our", "you",
    "your", "he", "him", "his", "she", "her", "it", "its", "they", "them",
    "their", "what", "which", "who", "whom", "when", "where", "why", "how",
    "all", "each", "every", "both", "few", "more", "most", "other", "some",
    "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too",
    "very", "just", "because", "as", "until", "while", "about", "between",
    "through", "during", "before", "after", "above", "below", "up", "down",
}


class Indexer:
    """Full-text and vector search indexer for library documents.
    
    Uses aiosqlite for AnyIO-compatible async SQLite access.
    """
    
    def __init__(self, vector_adapter: Optional[IVectorStoreAdapter] = None):
        self._fts: Optional[Any] = None
        self._vector_adapter = vector_adapter or MemoryVectorAdapter()
        self._write_lock = anyio.Lock()

    async def _get_fts(self) -> Any:
        if self._fts is None:
            import aiosqlite
            self._fts = await aiosqlite.connect(str(_get_db_path()), timeout=20)
            await self._fts.execute(
                "CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5("
                "doc_id, title, body, summary, domain, tags, tokenize='unicode61 remove_diacritics 2'"
                ")"
            )
            await self._fts.execute(
                "CREATE TABLE IF NOT EXISTS doc_metadata ("
                "doc_id TEXT PRIMARY KEY, source TEXT, source_type TEXT, "
                "author TEXT, published_date TEXT, quality_score REAL, "
                "word_count INTEGER, curated_at TEXT"
                ")"
            )
            await self._fts.commit()
        return self._fts

    async def index_document(self, doc: CuratedDocument) -> None:
        """Add a document to the search index."""
        async with self._write_lock:
            conn = await self._get_fts()

            await conn.execute(
                "INSERT OR REPLACE INTO documents_fts (doc_id, title, body, summary, domain, tags) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    doc.doc_id,
                    doc.title,
                    doc.body[:100000] if doc.body else "",
                    doc.summary,
                    doc.domain or "general",
                    " ".join(doc.tags),
                ),
            )
            await conn.execute(
                "INSERT OR REPLACE INTO doc_metadata (doc_id, source, source_type, author, "
                "published_date, quality_score, word_count, curated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    doc.doc_id,
                    doc.source,
                    doc.source_type,
                    doc.author,
                    doc.published_date,
                    doc.quality_score,
                    doc.word_count,
                    doc.curated_at,
                ),
            )
            await conn.commit()

        embedding = self._compute_embedding(doc.title + " " + doc.summary)
        if embedding:
            await self._vector_adapter.upsert(
                entity_name=doc.domain or "general",
                vector=embedding,
                metadata={"title": doc.title, "doc_id": doc.doc_id}
            )

        logger.debug(f"Indexed: {doc.doc_id} [{doc.domain}] {doc.title}")

    async def remove_document(self, doc_id: str) -> None:
        """Remove a document from the search index."""
        async with self._write_lock:
            conn = await self._get_fts()
            await conn.execute("DELETE FROM documents_fts WHERE doc_id = ?", (doc_id,))
            await conn.execute("DELETE FROM doc_metadata WHERE doc_id = ?", (doc_id,))
            await conn.commit()
        await self._vector_adapter.delete(
            entity_name="general", # Simplification: search all for deletion
            ids=[doc_id]
        )

    async def search_fts(
        self,
        query: str,
        domain: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Full-text search using SQLite FTS5."""
        conn = await self._get_fts()
        terms = self._tokenize(query)
        if not terms:
            return []

        fts_query = " AND ".join(f'"{t}"' for t in terms[:10])

        if domain:
            cursor = await conn.execute(
                "SELECT d.doc_id, d.title, d.summary, d.domain, m.quality_score, "
                "m.source, m.author, m.published_date, m.word_count, m.curated_at, "
                "rank "
                "FROM documents_fts d "
                "JOIN doc_metadata m ON d.doc_id = m.doc_id "
                "WHERE documents_fts MATCH ? AND d.domain = ? "
                "ORDER BY rank "
                "LIMIT ?",
                (fts_query, domain, limit),
            )
        else:
            cursor = await conn.execute(
                "SELECT d.doc_id, d.title, d.summary, d.domain, m.quality_score, "
                "m.source, m.author, m.published_date, m.word_count, m.curated_at, "
                "rank "
                "FROM documents_fts d "
                "JOIN doc_metadata m ON d.doc_id = m.doc_id "
                "WHERE documents_fts MATCH ? "
                "ORDER BY rank "
                "LIMIT ?",
                (fts_query, limit),
            )

        rows = await cursor.fetchall()
        results = []
        for row in rows:
            results.append({
                "doc_id": row[0],
                "title": row[1],
                "summary": row[2],
                "domain": row[3],
                "quality_score": row[4],
                "source": row[5],
                "author": row[6],
                "published_date": row[7],
                "word_count": row[8],
                "curated_at": row[9],
                "_rank": row[10],
            })
        return results

    async def search_vector(
        self,
        query: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Vector similarity search using the configured adapter."""
        query_embedding = self._compute_embedding(query)
        if not query_embedding:
            return []
        
        # Use the adapter for the actual search
        # We use "general" as the entity_name for library-wide search
        results = await self._vector_adapter.query(
            entity_name="general",
            vector=query_embedding,
            limit=limit
        )
        
        conn = await self._get_fts()
        final_results = []
        for score, meta in results:
            doc_id = meta.get("doc_id")
            if not doc_id:
                continue
            cursor = await conn.execute(
                "SELECT d.doc_id, d.title, d.summary, d.domain, m.quality_score, "
                "m.source, m.author, m.word_count, m.curated_at "
                "FROM documents_fts d JOIN doc_metadata m ON d.doc_id = m.doc_id "
                "WHERE d.doc_id = ?",
                (doc_id,),
            )
            row = await cursor.fetchone()
            if row:
                final_results.append({
                    "doc_id": row[0],
                    "title": row[1],
                    "summary": row[2],
                    "domain": row[3],
                    "quality_score": row[4],
                    "source": row[5],
                    "author": row[6],
                    "word_count": row[7],
                    "curated_at": row[8],
                    "_score": round(score, 4),
                })
        return final_results

    async def hybrid_search(
        self,
        query: str,
        domain: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Hybrid search: FTS + vector, deduplicated and re-ranked via RRF.
        
        Reciprocal Rank Fusion (RRF) merges results from different scoring
        systems by focusing on the rank rather than the raw score.
        """
        fts_results = await self.search_fts(query, domain, limit * 2)
        vec_results = await self.search_vector(query, limit * 2)
        
        # Map doc_id -> rank (1-indexed)
        fts_ranks = {r["doc_id"]: i + 1 for i, r in enumerate(fts_results)}
        vec_ranks = {r["doc_id"]: i + 1 for i, r in enumerate(vec_results)}
        
        all_doc_ids = set(fts_ranks.keys()) | set(vec_ranks.keys())
        
        # RRF Scoring: score = sum( 1 / (k + rank) )
        k = 60
        scored_docs = []
        for doc_id in all_doc_ids:
            score = 0.0
            if doc_id in fts_ranks:
                score += 1.0 / (k + fts_ranks[doc_id])
            if doc_id in vec_ranks:
                score += 1.0 / (k + vec_ranks[doc_id])
            scored_docs.append((doc_id, score))
        
        # Sort by RRF score descending
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        # Hydrate results from FTS (since it has the full metadata)
        final_results = []
        for doc_id, score in scored_docs[:limit]:
            # Try to find metadata in FTS results first
            doc = next((r for r in fts_results if r["doc_id"] == doc_id), None)
            if not doc:
                # If not in FTS, we need to fetch it from DB
                conn = await self._get_fts()
                cursor = await conn.execute(
                    "SELECT d.doc_id, d.title, d.summary, d.domain, m.quality_score, "
                    "m.source, m.author, m.word_count, m.curated_at "
                    "FROM documents_fts d JOIN doc_metadata m ON d.doc_id = m.doc_id "
                    "WHERE d.doc_id = ?",
                    (doc_id,),
                )
                row = await cursor.fetchone()
                if row:
                    doc = {
                        "doc_id": row[0], "title": row[1], "summary": row[2],
                        "domain": row[3], "quality_score": row[4], "source": row[5],
                        "author": row[6], "word_count": row[7], "curated_at": row[8],
                    }
            
            if doc:
                doc["_rrf_score"] = round(score, 6)
                final_results.append(doc)
                
        return final_results

    async def close(self) -> None:
        """Close the FTS database."""
        if self._fts:
            await self._fts.close()
            self._fts = None
            logger.info("FTS index connection closed")

    async def flush(self) -> None:
        """Flush all indices to disk."""
        async with self._write_lock:
            if self._fts:
                await self._fts.commit()

    async def stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        vector_count = len(self._vector_adapter) if hasattr(self._vector_adapter, "__len__") else 0
        if self._fts:
            cursor = await self._fts.execute("SELECT COUNT(*) FROM doc_metadata")
            row = await cursor.fetchone()
            count = row[0] if row else 0
        else:
            count = 0
        return {"fts_documents": count, "vector_embeddings": vector_count}

    def _tokenize(self, text: str) -> List[str]:
        tokens = re.findall(r"[a-zA-Z]\w+", text.lower())
        return [t for t in tokens if t not in _STOPWORDS and len(t) > 2]

    def _compute_embedding(self, text: str) -> Optional[List[float]]:
        """Compute a simple bag-of-words embedding.

        Uses stable MD5-based Feature Hashing (hashing trick) to map
        tokens deterministically to a fixed 256-dimensional space.
        """
        import hashlib
        
        vec = [0.0] * 256
        tokens = self._tokenize(text)
        if not tokens:
            return None
            
        for token in tokens:
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            dim = h % 256
            vec[dim] += 1.0
            
        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
            
        return vec

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        min_len = min(len(a), len(b))
        a, b = a[:min_len], b[:min_len]
        dot = sum(av * bv for av, bv in zip(a, b))
        na = math.sqrt(sum(av * av for av in a))
        nb = math.sqrt(sum(bv * bv for bv in b))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)
