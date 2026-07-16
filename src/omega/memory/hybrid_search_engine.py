# 🔱 Omega Engine — Hybrid Search Engine
# AP: AP-D283-MNEMOSYNE-v1.0.0
# ⬡ OMEGA ⬡ MEMORY ⬡ hybrid_search_engine.py
#
# Single RRF fusion source (k=60) — extracted from:
#   - memory_store.py:search() (lines 286-364)
#   - sqlite_vec_adapter.py:hybrid_search() (lines 543-649)
#   - block_tools.py:block_rethink/block_summarize (to be implemented)
#
# All hybrid search in Omega Engine MUST use this engine.
# No inline RRF implementations permitted.

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


# Default RRF constant per Cormack et al. 2009 and sqlite-vec NBC Headlines
DEFAULT_RRF_K = 60


@dataclass
class FTSResult:
    """FTS search result with rank."""
    doc_id: str
    rank: int
    metadata: Dict[str, Any]


@dataclass
class VecResult:
    """Vector search result with rank."""
    doc_id: str
    rank: int
    score: float
    metadata: Dict[str, Any]


@dataclass
class HybridSearchResult:
    """Fused hybrid search result."""
    doc_id: str
    fused_score: float
    source_rank_fts: Optional[int] = None
    source_rank_vec: Optional[int] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class HybridSearchEngine:
    """
    Single RRF fusion source for Omega Engine.
    
    Implements Reciprocal Rank Fusion (RRF) per Cormack et al. 2009:
        score = sum(1 / (k + rank)) for each source
    
    Default k=60 per sqlite-vec NBC Headlines and Cormack et al. 2009.
    
    Usage:
        engine = HybridSearchEngine(k=60)
        results = engine.fuse(fts_results, vec_results, limit=20)
    """
    
    def __init__(self, k: int = DEFAULT_RRF_K):
        """
        Initialize HybridSearchEngine.
        
        Args:
            k: RRF constant (default 60). Higher k = more weight to lower ranks.
        """
        self.k = k
        logger.debug("HybridSearchEngine initialized with k=%d", k)
    
    def fuse(
        self,
        fts_results: List[FTSResult],
        vec_results: List[VecResult],
        limit: int = 20,
        fts_weight: float = 1.0,
        vec_weight: float = 1.0,
    ) -> List[HybridSearchResult]:
        """
        Fuse FTS and vector results using RRF.
        
        Args:
            fts_results: List of FTSResult (ranked by BM25/score)
            vec_results: List of VecResult (ranked by distance/similarity)
            limit: Maximum number of fused results to return
            fts_weight: Weight for FTS source (default 1.0)
            vec_weight: Weight for vector source (default 1.0)
        
        Returns:
            List of HybridSearchResult sorted by fused_score descending
        """
        if not fts_results and not vec_results:
            return []
        
        # Build rank maps
        fts_ranks = {r.doc_id: r.rank for r in fts_results}
        vec_ranks = {r.doc_id: r.rank for r in vec_results}
        
        # All unique doc_ids
        all_doc_ids = set(fts_ranks.keys()) | set(vec_ranks.keys())
        
        # Compute RRF scores
        scored_docs = []
        for doc_id in all_doc_ids:
            score = 0.0
            fts_rank = fts_ranks.get(doc_id)
            vec_rank = vec_ranks.get(doc_id)
            
            if fts_rank is not None:
                score += fts_weight / (self.k + fts_rank)
            if vec_rank is not None:
                score += vec_weight / (self.k + vec_rank)
            
            scored_docs.append((doc_id, score, fts_rank, vec_rank))
        
        # Sort by fused score descending
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        # Build results with metadata
        results = []
        fts_meta = {r.doc_id: r.metadata for r in fts_results}
        vec_meta = {r.doc_id: r.metadata for r in vec_results}
        
        for doc_id, fused_score, fts_rank, vec_rank in scored_docs[:limit]:
            # Prefer FTS metadata (typically richer: content, role, etc.)
            metadata = fts_meta.get(doc_id, {}).copy()
            if not metadata:
                metadata = vec_meta.get(doc_id, {}).copy()
            
            result = HybridSearchResult(
                doc_id=doc_id,
                fused_score=round(fused_score, 6),
                source_rank_fts=fts_rank,
                source_rank_vec=vec_rank,
                metadata=metadata,
            )
            results.append(result)
        
        return results
    
    def fuse_from_dicts(
        self,
        fts_results: List[Dict[str, Any]],
        vec_results: List[Dict[str, Any]],
        limit: int = 20,
        fts_weight: float = 1.0,
        vec_weight: float = 1.0,
        doc_id_key: str = "doc_id",
    ) -> List[HybridSearchResult]:
        """
        Fuse results from plain dicts (convenience method).
        
        Args:
            fts_results: List of dicts with doc_id_key and metadata
            vec_results: List of dicts with doc_id_key and metadata
            limit: Maximum results
            fts_weight: FTS weight
            vec_weight: Vector weight
            doc_id_key: Key for document ID in dicts
        
        Returns:
            List of HybridSearchResult
        """
        fts_parsed = []
        for i, r in enumerate(fts_results):
            doc_id = r.get(doc_id_key) or r.get("doc_id") or r.get("rowid") or r.get("id")
            if doc_id is None:
                continue
            metadata = {k: v for k, v in r.items() if k != doc_id_key}
            fts_parsed.append(FTSResult(
                doc_id=str(doc_id),
                rank=i + 1,
                metadata=metadata,
            ))
        
        vec_parsed = []
        for i, r in enumerate(vec_results):
            doc_id = r.get(doc_id_key) or r.get("doc_id") or r.get("rowid") or r.get("id")
            if doc_id is None:
                continue
            score = r.get("score") or r.get("distance") or 0.0
            metadata = {k: v for k, v in r.items() if k != doc_id_key}
            vec_parsed.append(VecResult(
                doc_id=str(doc_id),
                rank=i + 1,
                score=float(score),
                metadata=metadata,
            ))
        
        return self.fuse(fts_parsed, vec_parsed, limit, fts_weight, vec_weight)


# Module-level singleton for convenience
_hybrid_search_engine: Optional[HybridSearchEngine] = None


def get_hybrid_search_engine(k: int = DEFAULT_RRF_K) -> HybridSearchEngine:
    """
    Get or create the singleton HybridSearchEngine.
    
    Args:
        k: RRF constant (default 60)
    
    Returns:
        HybridSearchEngine instance
    """
    global _hybrid_search_engine
    if _hybrid_search_engine is None or _hybrid_search_engine.k != k:
        _hybrid_search_engine = HybridSearchEngine(k=k)
    return _hybrid_search_engine


def fuse(
    fts_results: List[FTSResult],
    vec_results: List[VecResult],
    limit: int = 20,
    fts_weight: float = 1.0,
    vec_weight: float = 1.0,
    k: int = DEFAULT_RRF_K,
) -> List[HybridSearchResult]:
    """
    Convenience function for one-off fusion.
    
    Args:
        fts_results: List of FTSResult
        vec_results: List of VecResult
        limit: Maximum results
        fts_weight: FTS weight
        vec_weight: Vector weight
        k: RRF constant
    
    Returns:
        List of HybridSearchResult
    """
    engine = get_hybrid_search_engine(k)
    return engine.fuse(fts_results, vec_results, limit, fts_weight, vec_weight)