"""Search Indexing — Full-text and vector search indexing for the library.

AP: AP-OMEGA-INDEXER-v1.0.0
ICS: [NODE: THOTH | ARCHETYPE: APOLLO | CONTEXT: INDEXER]

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

from .curator import CuratedDocument

logger = logging.getLogger(__name__)

DATA_DIR = Path(os.environ.get("OMEGA_DATA_DIR", str(Path.home() / "omega" / "data")))
INDEX_DIR = DATA_DIR / "library" / "index"
INDEX_DIR.mkdir(parents=True, exist_ok=True)

FTS_DB_PATH = INDEX_DIR / "fts_index.db"
VECTOR_INDEX_PATH = INDEX_DIR / "vectors.json"

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

    def __init__(self):
        self._fts: Optional[Any] = None
        self._vector_store: Dict[str, List[float]] = {}
        self._load_vectors()

    async def _get_fts(self) -> Any:
        if self._fts is None:
            import aiosqlite
            self._fts = await aiosqlite.connect(str(FTS_DB_PATH))
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

    def _load_vectors(self) -> None:
        if VECTOR_INDEX_PATH.exists():
            try:
                with open(VECTOR_INDEX_PATH) as f:
                    self._vector_store = json.load(f)
                logger.info(f"Loaded {len(self._vector_store)} vector embeddings")
            except Exception as e:
                logger.warning(f"Failed to load vector index: {e}")

    async def index_document(self, doc: CuratedDocument) -> None:
        """Add a document to the search index."""
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
            self._vector_store[doc.doc_id] = embedding

        logger.debug(f"Indexed: {doc.doc_id} [{doc.domain}] {doc.title}")

    async def remove_document(self, doc_id: str) -> None:
        """Remove a document from the search index."""
        conn = await self._get_fts()
        await conn.execute("DELETE FROM documents_fts WHERE doc_id = ?", (doc_id,))
        await conn.execute("DELETE FROM doc_metadata WHERE doc_id = ?", (doc_id,))
        await conn.commit()
        self._vector_store.pop(doc_id, None)

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
        """Vector similarity search (lightweight, in-memory)."""
        if not self._vector_store:
            return []

        query_embedding = self._compute_embedding(query)
        if not query_embedding:
            return []

        scores: List[Tuple[str, float]] = []
        for doc_id, vec in self._vector_store.items():
            sim = self._cosine_similarity(query_embedding, vec)
            scores.append((doc_id, sim))

        scores.sort(key=lambda x: x[1], reverse=True)
        conn = await self._get_fts()
        results = []
        for doc_id, sim in scores[:limit]:
            cursor = await conn.execute(
                "SELECT d.doc_id, d.title, d.summary, d.domain, m.quality_score, "
                "m.source, m.author, m.word_count, m.curated_at "
                "FROM documents_fts d JOIN doc_metadata m ON d.doc_id = m.doc_id "
                "WHERE d.doc_id = ?",
                (doc_id,),
            )
            row = await cursor.fetchone()
            if row:
                results.append({
                    "doc_id": row[0],
                    "title": row[1],
                    "summary": row[2],
                    "domain": row[3],
                    "quality_score": row[4],
                    "source": row[5],
                    "author": row[6],
                    "word_count": row[7],
                    "curated_at": row[8],
                    "_score": round(sim, 4),
                })
        return results

    async def hybrid_search(
        self,
        query: str,
        domain: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Hybrid search: FTS + vector, deduplicated and re-ranked."""
        fts_results = await self.search_fts(query, domain, limit)
        vec_results = await self.search_vector(query, limit)

        seen: set = set()
        combined = []
        for r in fts_results:
            if r["doc_id"] not in seen:
                seen.add(r["doc_id"])
                r["_fts_score"] = r.pop("_rank", 0)
                r["_vec_score"] = 0.0
                combined.append(r)

        for r in vec_results:
            if r["doc_id"] not in seen:
                seen.add(r["doc_id"])
                r["_fts_score"] = 0.0
                r["_vec_score"] = r.pop("_score", 0.0)
                combined.insert(0, r)
            else:
                for existing in combined:
                    if existing["doc_id"] == r["doc_id"]:
                        existing["_vec_score"] = r.pop("_score", 0.0)
                        break

        def _rrf_score(item, k=60):
            """Reciprocal Rank Fusion score — higher is better.
            
            Converts FTS5 rank (negative BM25, closer to 0 = better) and
            vector score (0 to 1, higher = better) into combined RRF score.
            k=60 is the standard RRF parameter.
            """
            # FTS5 rank: negate to make positive (higher rank value = worse match)
            # Convert to RRF: 1 / (k + rank_position)
            fts_raw = -item.get("_fts_score", 0)  # negate to make positive
            if fts_raw < 0:
                fts_raw = 0  # shouldn't happen, but guard
            fts_rrf = 1.0 / (k + fts_raw)
            
            # Vector score: already positive 0-1, invert so 1.0 = rank 0
            vec_raw = 1.0 - item.get("_vec_score", 0.0)
            vec_rrf = 1.0 / (k + vec_raw * 100)
            
            return fts_rrf + vec_rrf

        def _rrf_score(item, k=60):
            """Reciprocal Rank Fusion score — higher is better.
            
            Converts FTS5 rank (negative BM25, closer to 0 = better) and
            vector score (0 to 1, higher = better) into combined RRF score.
            k=60 is the standard RRF parameter.
            """
            # FTS5 rank: negate to make positive (higher rank value = worse match)
            # Convert to RRF: 1 / (k + rank_position)
            fts_raw = -item.get("_fts_score", 0)  # negate to make positive
            if fts_raw < 0:
                fts_raw = 0  # shouldn't happen, but guard
            fts_rrf = 1.0 / (k + fts_raw)
            
            # Vector score: already positive 0-1, invert so 1.0 = rank 0
            vec_raw = 1.0 - item.get("_vec_score", 0.0)
            vec_rrf = 1.0 / (k + vec_raw * 100)
            
            return fts_rrf + vec_rrf

        combined.sort(
            key=_rrf_score,
            reverse=False,
        )
        return combined[:limit]

    async def close(self) -> None:
        """Close the FTS database and save vectors."""
        if self._fts:
            await self._fts.close()
            self._fts = None
        await self.save_vectors()

    async def save_vectors(self) -> None:
        """Persist vector embeddings to disk."""
        if self._vector_store:
            async with await anyio.open_file(str(VECTOR_INDEX_PATH), "w") as f:
                await f.write(json.dumps(self._vector_store))
            logger.info(f"Saved {len(self._vector_store)} vector embeddings")

    async def flush(self) -> None:
        """Flush all indices to disk."""
        await self.save_vectors()
        if self._fts:
            await self._fts.commit()

    async def close(self) -> None:
        """Close the SQLite connection."""
        if self._fts:
            await self._fts.close()
            self._fts = None
            logger.info("FTS index connection closed")

    async def stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        vector_count = len(self._vector_store)
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

        This is a lightweight alternative to neural embeddings.
        For production, swap in fastembed or sentence-transformers.
        """
        tokens = self._tokenize(text)
        if not tokens:
            return None
        unique = list(dict.fromkeys(tokens))
        freq = {t: tokens.count(t) / len(tokens) for t in unique}
        return list(freq.values())[:256]

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        min_len = min(len(a), len(b))
        a, b = a[:min_len], b[:min_len]
        dot = sum(av * bv for av, bv in zip(a, b))
        na = math.sqrt(sum(av * av for av in a))
        nb = math.sqrt(sum(bv * bv for bv in b))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)
