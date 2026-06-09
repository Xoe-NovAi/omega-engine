# AP Token: AP-ORACLE-RESTORE-v2.3.0
"""Vector-based Cross-Reference Engine for the Omega Library.

AP: AP-LIBRARY-CROSSREF-v1.0.0
ICS: [NODE: THOTH | ARCHETYPE: SOPHIA | CONTEXT: LIBRARY-CROSSREF]

Provides dual-path cross-referencing between library documents:
  - PATH A (keyword): FTS5 BM25 tag/title match (existing, preserved)
  - PATH B (vector):  Cosine similarity via IVectorStoreAdapter (new, S2-C)

Both paths are run in parallel. Results are deduplicated and merged via RRF.
No breaking changes to the existing FTS index or library.py interface.

[id-soft: quake-1996] Zone memory zone_t linked-list — cross-reference chaining
  QuakeC's zone allocator chains allocations in a doubly-linked list.
  CrossRefEngine chains related documents via similarity — the same
  structural pattern: each node points to its neighbors.

AnyIO compliance: yes. All async ops use aiosqlite/anyio.to_thread.run_sync.
"""

import hashlib
import logging
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import anyio

from omega.errors import OmegaError, OmegaPersistenceError

logger = logging.getLogger(__name__)

# RRF constant — empirically optimal for most IR fusion tasks
_RRF_K = 60


def _get_fts_path() -> Path:
    """Resolve the library FTS index database path."""
    data_dir = Path(os.environ.get(
        "OMEGA_DATA_DIR",
        str(Path(__file__).resolve().parent.parent.parent.parent / "data"),
    ))
    return data_dir / "library" / "index" / "fts_index.db"


# ── Lightweight embedding (stable, no ML deps) ─────────────────────────────

_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "this", "that", "these", "those",
}


def _tokenize(text: str) -> List[str]:
    """Tokenize text: lowercase, strip stopwords, min length 3."""
    import re
    tokens = re.findall(r"[a-zA-Z]\w+", text.lower())
    return [t for t in tokens if t not in _STOPWORDS and len(t) > 2]


def _compute_embedding(text: str) -> Optional[List[float]]:
    """Compute a stable 256-dim MD5 feature-hash embedding.

    Uses the same algorithm as Indexer._compute_embedding() to ensure
    cross-reference vectors are compatible with library index vectors.
    """
    vec = [0.0] * 256
    tokens = _tokenize(text)
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


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two L2-normalized vectors."""
    min_len = min(len(a), len(b))
    a, b = a[:min_len], b[:min_len]
    dot = sum(av * bv for av, bv in zip(a, b))
    na = math.sqrt(sum(av * av for av in a))
    nb = math.sqrt(sum(bv * bv for bv in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


# ── CrossRefEngine ─────────────────────────────────────────────────────────

class CrossRefEngine:
    """Dual-path cross-reference engine for library documents.

    PATH A (keyword): FTS5 BM25 search on tags + title.
    PATH B (vector):  Cosine similarity via in-memory vector store.

    Results from both paths are merged via Reciprocal Rank Fusion (RRF, k=60)
    to produce a stable, re-ranked list of related documents.

    Usage::

        engine = CrossRefEngine()
        refs = await engine.find_related(doc_id="doc_security_R_tainted_data_protocol", limit=5)
        # refs: List[Dict] — each has doc_id, title, domain, _rrf_score, _path
    """

    def __init__(self) -> None:
        self._fts: Optional[Any] = None
        # In-memory vector store: doc_id -> (vector, metadata)
        self._vectors: Dict[str, Tuple[List[float], Dict[str, str]]] = {}
        self._loaded = False

    # ── Lifecycle ──────────────────────────────────────────────────────────

    async def _ensure_fts(self) -> Any:
        """Lazy-open the FTS database (read-only path)."""
        if self._fts is None:
            import aiosqlite
            db_path = _get_fts_path()
            if not db_path.exists():
                raise OmegaPersistenceError(
                    f"FTS index not found at {db_path}. Run ingest_seeded_knowledge.py first."
                )
            self._fts = await aiosqlite.connect(str(db_path), timeout=20)
        return self._fts

    async def load_vectors(self) -> int:
        """Build the in-memory vector store from all indexed documents.

        Reads doc_id + body from FTS, computes embeddings, stores them.
        Returns the number of documents vectorized.
        """
        if self._loaded:
            return len(self._vectors)

        conn = await self._ensure_fts()
        cursor = await conn.execute(
            "SELECT d.doc_id, d.title, d.body, d.domain, d.tags "
            "FROM documents_fts d"
        )
        rows = await cursor.fetchall()

        loaded = 0
        for row in rows:
            doc_id, title, body, domain, tags = row
            # Embed concatenated title + tags + body[:2000] for efficiency
            text = f"{title} {tags} {(body or '')[:2000]}"
            vec = _compute_embedding(text)
            if vec:
                self._vectors[doc_id] = (vec, {
                    "title": title or "",
                    "domain": domain or "",
                    "tags": tags or "",
                })
                loaded += 1

        self._loaded = True
        logger.info(f"CrossRefEngine: loaded {loaded} document vectors")
        return loaded

    async def close(self) -> None:
        """Release the FTS connection."""
        if self._fts:
            await self._fts.close()
            self._fts = None
            self._loaded = False
            logger.info("CrossRefEngine: FTS connection closed")

    # ── PATH A: Keyword cross-reference ────────────────────────────────────

    async def _keyword_related(
        self,
        doc_id: str,
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Find related documents via FTS5 tag + title keyword match.

        Strategy: extract tags and title words from the source document,
        then query FTS for documents sharing those tokens (excluding self).
        """
        conn = await self._ensure_fts()

        # Fetch source doc metadata
        cursor = await conn.execute(
            "SELECT title, domain, tags FROM documents_fts WHERE doc_id = ?",
            (doc_id,),
        )
        row = await cursor.fetchone()
        if not row:
            return []

        title, domain, tags = row
        # Build a keyword query from tags + title tokens
        keyword_tokens = _tokenize(f"{title} {tags}")
        if not keyword_tokens:
            return []

        # FTS5 MATCH query — OR semantics across tokens
        fts_query = " OR ".join(keyword_tokens[:10])  # cap to avoid over-broad match

        try:
            cursor = await conn.execute(
                "SELECT d.doc_id, d.title, d.domain, d.tags, rank "
                "FROM documents_fts d "
                "WHERE documents_fts MATCH ? AND d.doc_id != ? "
                "ORDER BY rank "
                "LIMIT ?",
                (fts_query, doc_id, limit),
            )
            rows = await cursor.fetchall()
        except Exception as e:
            logger.warning(f"CrossRef keyword search failed: {e}")
            return []

        return [
            {
                "doc_id": r[0],
                "title": r[1],
                "domain": r[2],
                "tags": r[3],
                "_path": "keyword",
                "_raw_rank": r[4],
            }
            for r in rows
        ]

    # ── PATH B: Vector cross-reference ─────────────────────────────────────

    async def _vector_related(
        self,
        doc_id: str,
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Find related documents via cosine similarity on MD5 feature vectors.

        Loads all document vectors (lazy, cached), computes similarity against
        the source document's vector, returns top-k excluding self.
        """
        await self.load_vectors()

        if doc_id not in self._vectors:
            logger.warning(f"CrossRef: doc_id '{doc_id}' not in vector store")
            return []

        query_vec, _ = self._vectors[doc_id]

        # Score all documents against query vector
        scored: List[Tuple[str, float]] = []
        for other_id, (other_vec, meta) in self._vectors.items():
            if other_id == doc_id:
                continue
            sim = _cosine_similarity(query_vec, other_vec)
            scored.append((other_id, sim))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[1], reverse=True)

        results = []
        for other_id, sim in scored[:limit]:
            _, meta = self._vectors[other_id]
            results.append({
                "doc_id": other_id,
                "title": meta.get("title", ""),
                "domain": meta.get("domain", ""),
                "tags": meta.get("tags", ""),
                "_path": "vector",
                "_cosine": round(sim, 4),
            })
        return results

    # ── MERGE: RRF Fusion ──────────────────────────────────────────────────

    async def find_related(
        self,
        doc_id: str,
        limit: int = 5,
        domain_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Find documents related to doc_id via dual-path RRF fusion.

        Runs PATH A (keyword) and PATH B (vector) in parallel via AnyIO.
        Merges results with RRF (k=60). Deduplicates by doc_id.

        Args:
            doc_id: The source document's ID.
            limit: Maximum number of related documents to return.
            domain_filter: If set, only return docs from this domain.

        Returns:
            List of dicts with keys: doc_id, title, domain, tags,
            _rrf_score, _paths (list of which paths found this doc).
        """
        # Run both paths concurrently
        keyword_results: List[Dict[str, Any]] = []
        vector_results: List[Dict[str, Any]] = []

        async def _kw():
            nonlocal keyword_results
            try:
                keyword_results = await self._keyword_related(doc_id, limit * 2)
            except OmegaError:
                raise
            except Exception as e:
                logger.warning(f"CrossRef keyword path failed: {e}")

        async def _vec():
            nonlocal vector_results
            try:
                vector_results = await self._vector_related(doc_id, limit * 2)
            except OmegaError:
                raise
            except Exception as e:
                logger.warning(f"CrossRef vector path failed: {e}")

        async with anyio.create_task_group() as tg:
            tg.start_soon(_kw)
            tg.start_soon(_vec)

        # Build rank maps
        kw_ranks = {r["doc_id"]: i + 1 for i, r in enumerate(keyword_results)}
        vec_ranks = {r["doc_id"]: i + 1 for i, r in enumerate(vector_results)}

        all_doc_ids = set(kw_ranks.keys()) | set(vec_ranks.keys())

        # RRF scoring
        scored: List[Tuple[str, float]] = []
        for did in all_doc_ids:
            score = 0.0
            paths = []
            if did in kw_ranks:
                score += 1.0 / (_RRF_K + kw_ranks[did])
                paths.append("keyword")
            if did in vec_ranks:
                score += 1.0 / (_RRF_K + vec_ranks[did])
                paths.append("vector")
            scored.append((did, score, paths))

        # Sort by RRF score descending
        scored.sort(key=lambda x: x[1], reverse=True)

        # Hydrate results — prefer keyword metadata (has full data from FTS)
        kw_meta = {r["doc_id"]: r for r in keyword_results}
        vec_meta = {r["doc_id"]: r for r in vector_results}

        final: List[Dict[str, Any]] = []
        for did, rrf_score, paths in scored[:limit * 2]:
            meta = kw_meta.get(did) or vec_meta.get(did) or {"doc_id": did}

            # Apply domain filter
            if domain_filter and meta.get("domain") != domain_filter:
                continue

            final.append({
                "doc_id": did,
                "title": meta.get("title", ""),
                "domain": meta.get("domain", ""),
                "tags": meta.get("tags", ""),
                "_rrf_score": round(rrf_score, 6),
                "_paths": paths,
            })

            if len(final) >= limit:
                break

        return final

    # ── Cross-entity topic discovery ───────────────────────────────────────

    async def find_cross_entity_refs(
        self,
        entity_name: str,
        topic: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Find library documents related to a topic from another entity's perspective.

        Useful for the Knowledge Discovery Layer: when entity A promotes a
        topic, find which other entity domains have related knowledge.

        Args:
            entity_name: The entity doing the lookup (used for exclusion).
            topic: Free-form topic description.
            limit: Max results.

        Returns:
            List of related docs from any domain except entity_name.
        """
        await self.load_vectors()

        query_vec = _compute_embedding(topic)
        if not query_vec:
            return []

        scored: List[Tuple[str, float, Dict]] = []
        for other_id, (other_vec, meta) in self._vectors.items():
            # Exclude the requesting entity's own documents
            if meta.get("domain") == entity_name:
                continue
            sim = _cosine_similarity(query_vec, other_vec)
            scored.append((other_id, sim, meta))

        scored.sort(key=lambda x: x[1], reverse=True)

        return [
            {
                "doc_id": did,
                "title": meta.get("title", ""),
                "domain": meta.get("domain", ""),
                "_cosine": round(sim, 4),
                "_path": "vector",
            }
            for did, sim, meta in scored[:limit]
        ]
