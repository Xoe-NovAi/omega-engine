# 🔱 Omega Engine — Hybrid Search Engine
# AP: AP-D283-MNEMOSYNE-v1.0.0
# ⬡ OMEGA ⬡ MEMORY ⬡ hybrid_search.py
#
# Single source of truth for Reciprocal Rank Fusion (RRF).
# Unifies RRF logic from:
#   - memory_store.py:search() (lines 286-364)
#   - sqlite_vec_adapter.py:hybrid_search() (lines 543-649)
#   - block_tools.py:block_rethink/block_summarize (future)
#
# RRF Formula: score = sum( weight / (k + rank) ) where k=60 (Cormack et al. 2009)

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Sequence
import logging

logger = logging.getLogger(__name__)


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
    Unified Reciprocal Rank Fusion engine.
    
    Single source of truth for hybrid search fusion across:
    - MemoryStore.search()
    - SQLiteVecAdapter.hybrid_search()
    - BlockTools.block_rethink/block_summarize
    
    RRF Formula: score = sum( weight / (k + rank) )
    Default k=60 per Cormack et al. 2009 and sqlite-vec NBC Headlines benchmark.
    """
    
    DEFAULT_K = 60
    
    def __init__(self, k: int = DEFAULT_K):
        """
        Initialize HybridSearchEngine.
        
        Args:
            k: RRF constant (default 60). Lower k = more weight to top ranks.
        """
        self.k = k
    
    def fuse(
        self,
        fts_results: Sequence[FTSResult],
        vec_results: Sequence[VecResult],
        fts_weight: float = 1.0,
        vec_weight: float = 1.0,
        limit: int = 20,
    ) -> List[HybridSearchResult]:
        """
        Fuse FTS and vector results using Reciprocal Rank Fusion.
        
        Args:
            fts_results: Sequence of FTSResult (ranked by BM25 score, best first)
            vec_results: Sequence of VecResult (ranked by vector distance, best first)
            fts_weight: Weight for FTS results (default 1.0)
            vec_weight: Weight for vector results (default 1.0)
            limit: Maximum number of fused results to return
            
        Returns:
            List of HybridSearchResult sorted by fused_score descending
        """
        if not fts_results and not vec_results:
            return []
        
        # Build rank maps: doc_id -> (rank, metadata)
        fts_ranks = {r.doc_id: (r.rank, r.metadata) for r in fts_results}
        vec_ranks = {r.doc_id: (r.rank, r.metadata) for r in vec_results}
        
        # Union of all doc_ids
        all_doc_ids = set(fts_ranks.keys()) | set(vec_ranks.keys())
        
        # Compute fused scores
        scored_docs = []
        for doc_id in all_doc_ids:
            score = 0.0
            source_rank_fts = None
            source_rank_vec = None
            
            if doc_id in fts_ranks:
                rank, metadata = fts_ranks[doc_id]
                score += fts_weight / (self.k + rank)
                source_rank_fts = rank
            else:
                metadata = {}
            
            if doc_id in vec_ranks:
                rank, vec_metadata = vec_ranks[doc_id]
                score += vec_weight / (self.k + rank)
                source_rank_vec = rank
                # Merge metadata (prefer FTS, fallback to vec)
                if not metadata:
                    metadata = vec_metadata
                else:
                    metadata = {**vec_metadata, **metadata}  # FTS overrides
            
            scored_docs.append(HybridSearchResult(
                doc_id=doc_id,
                fused_score=round(score, 6),
                source_rank_fts=source_rank_fts,
                source_rank_vec=source_rank_vec,
                metadata=metadata,
            ))
        
        # Sort by fused_score descending
        scored_docs.sort(key=lambda x: x.fused_score, reverse=True)
        
        return scored_docs[:limit]
    
    def fuse_from_dicts(
        self,
        fts_results: List[Dict[str, Any]],
        vec_results: List[tuple],  # List of (score, metadata)
        fts_weight: float = 1.0,
        vec_weight: float = 1.0,
        limit: int = 20,
        fts_doc_id_key: str = "doc_id",
        vec_doc_id_key: str = "doc_id",
    ) -> List[HybridSearchResult]:
        """
        Convenience method for dict/tuple inputs (legacy compatibility).
        
        Args:
            fts_results: List of dicts with doc_id_key and metadata
            vec_results: List of (score, metadata_dict) tuples
            fts_weight: Weight for FTS results
            vec_weight: Weight for vector results
            limit: Maximum results
            fts_doc_id_key: Key for doc_id in FTS dicts
            vec_doc_id_key: Key for doc_id in vec metadata dicts
            
        Returns:
            List of HybridSearchResult
        """
        # Convert FTS dicts to FTSResult
        fts_objects = []
        for i, r in enumerate(fts_results):
            doc_id = r.get(fts_doc_id_key)
            if doc_id is None:
                # Generate from session_id:timestamp if available
                doc_id = f"{r.get('session_id', '')}:{r.get('timestamp', '')}"
            fts_objects.append(FTSResult(
                doc_id=doc_id,
                rank=i + 1,
                metadata=r,
            ))
        
        # Convert vec tuples to VecResult
        vec_objects = []
        for i, (score, metadata) in enumerate(vec_results):
            doc_id = metadata.get(vec_doc_id_key)
            if doc_id is None:
                doc_id = f"{metadata.get('session_id', '')}:{metadata.get('timestamp', '')}"
            vec_objects.append(VecResult(
                doc_id=doc_id,
                rank=i + 1,
                score=score,
                metadata=metadata,
            ))
        
        return self.fuse(fts_objects, vec_objects, fts_weight, vec_weight, limit)


# Singleton instance for convenience
_default_engine: Optional[HybridSearchEngine] = None


def get_hybrid_search_engine(k: int = HybridSearchEngine.DEFAULT_K) -> HybridSearchEngine:
    """Get or create the default HybridSearchEngine instance."""
    global _default_engine
    if _default_engine is None or _default_engine.k != k:
        _default_engine = HybridSearchEngine(k=k)
    return _default_engine