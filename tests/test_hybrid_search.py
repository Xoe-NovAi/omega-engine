# 🔱 Omega Engine — Hybrid Search Engine Contract Tests
# AP: AP-D283-MNEMOSYNE-v1.0.0
# ⬡ OMEGA ⬡ MEMORY ⬡ test_hybrid_search.py
#
# CONTRACT TESTS FIRST (TDD) — These define the expected behavior
# of HybridSearchEngine before implementation.

import pytest
from typing import List, Dict, Any

from src.omega.memory.hybrid_search import (
    HybridSearchEngine,
    FTSResult,
    VecResult,
    HybridSearchResult,
    get_hybrid_search_engine,
)


class TestHybridSearchEngineContract:
    """Contract tests for HybridSearchEngine — MUST pass before implementation."""

    def test_rrf_basic_fusion(self):
        """Test basic RRF fusion with known inputs."""
        engine = HybridSearchEngine(k=60)
        
        fts = [
            FTSResult(doc_id="doc1", rank=1, metadata={"content": "A"}),
            FTSResult(doc_id="doc2", rank=2, metadata={"content": "B"}),
        ]
        vec = [
            VecResult(doc_id="doc1", rank=1, score=0.9, metadata={"content": "A"}),
            VecResult(doc_id="doc3", rank=2, score=0.8, metadata={"content": "C"}),
        ]
        
        results = engine.fuse(fts, vec, limit=10)
        
        # doc1 appears in both: score = 1/(60+1) + 1/(60+1) = 2/61 ≈ 0.032787 (rounded to 6 decimals)
        doc1 = next(r for r in results if r.doc_id == "doc1")
        assert abs(doc1.fused_score - round(2.0/61, 6)) < 1e-10
        assert doc1.source_rank_fts == 1
        assert doc1.source_rank_vec == 1
        
        # doc2 only in FTS: score = 1/(60+2)
        doc2 = next(r for r in results if r.doc_id == "doc2")
        assert abs(doc2.fused_score - round(1.0/62, 6)) < 1e-10
        assert doc2.source_rank_fts == 2
        assert doc2.source_rank_vec is None
        
        # doc3 only in vec: score = 1/(60+2)
        doc3 = next(r for r in results if r.doc_id == "doc3")
        assert abs(doc3.fused_score - round(1.0/62, 6)) < 1e-10
        assert doc3.source_rank_fts is None
        assert doc3.source_rank_vec == 2

    def test_rrf_fts_only(self):
        """Test RRF with FTS results only."""
        engine = HybridSearchEngine(k=60)
        
        fts = [
            FTSResult(doc_id="doc1", rank=1, metadata={"content": "A"}),
            FTSResult(doc_id="doc2", rank=2, metadata={"content": "B"}),
        ]
        vec = []
        
        results = engine.fuse(fts, vec, limit=10)
        
        assert len(results) == 2
        assert results[0].doc_id == "doc1"
        assert abs(results[0].fused_score - round(1.0/61, 6)) < 1e-10
        assert results[1].doc_id == "doc2"
        assert abs(results[1].fused_score - round(1.0/62, 6)) < 1e-10

    def test_rrf_vec_only(self):
        """Test RRF with vector results only."""
        engine = HybridSearchEngine(k=60)
        
        fts = []
        vec = [
            VecResult(doc_id="doc1", rank=1, score=0.9, metadata={"content": "A"}),
            VecResult(doc_id="doc2", rank=2, score=0.8, metadata={"content": "B"}),
        ]
        
        results = engine.fuse(fts, vec, limit=10)
        
        assert len(results) == 2
        assert results[0].doc_id == "doc1"
        assert abs(results[0].fused_score - round(1.0/61, 6)) < 1e-10
        assert results[1].doc_id == "doc2"
        assert abs(results[1].fused_score - round(1.0/62, 6)) < 1e-10

    def test_rrf_empty_results(self):
        """Test RRF with empty results from both sources."""
        engine = HybridSearchEngine(k=60)
        
        results = engine.fuse([], [], limit=10)
        
        assert results == []

    def test_rrf_k_parameter(self):
        """Test k parameter behavior (default 60)."""
        engine_default = HybridSearchEngine()  # k=60
        engine_custom = HybridSearchEngine(k=10)
        
        fts = [FTSResult(doc_id="doc1", rank=1, metadata={})]
        vec = [VecResult(doc_id="doc1", rank=1, score=0.9, metadata={})]
        
        results_default = engine_default.fuse(fts, vec)
        results_custom = engine_custom.fuse(fts, vec)
        
        # k=10 gives higher scores than k=60 for same ranks
        assert results_custom[0].fused_score > results_default[0].fused_score

    def test_result_type(self):
        """Test that results are HybridSearchResult instances."""
        engine = HybridSearchEngine(k=60)
        
        fts = [FTSResult(doc_id="doc1", rank=1, metadata={})]
        vec = [VecResult(doc_id="doc1", rank=1, score=0.9, metadata={})]
        
        results = engine.fuse(fts, vec)
        
        assert len(results) == 1
        assert isinstance(results[0], HybridSearchResult)

    def test_fused_score_precision(self):
        """Test fused_score is rounded to 6 decimal places."""
        engine = HybridSearchEngine(k=60)
        
        fts = [FTSResult(doc_id="doc1", rank=1, metadata={})]
        vec = [VecResult(doc_id="doc1", rank=1, score=0.9, metadata={})]
        
        results = engine.fuse(fts, vec)
        
        # 2/61 = 0.032786885... rounded to 6 decimals = 0.032787
        assert results[0].fused_score == round(2.0/61, 6)

    def test_metadata_preservation(self):
        """Test that metadata from both sources is preserved."""
        engine = HybridSearchEngine(k=60)
        
        fts = [FTSResult(doc_id="doc1", rank=1, metadata={"source": "fts", "content": "A"})]
        vec = [VecResult(doc_id="doc1", rank=1, score=0.9, metadata={"source": "vec", "embedding": [1,2,3]})]
        
        results = engine.fuse(fts, vec)
        
        assert results[0].metadata["source"] == "fts"  # FTS overrides
        assert "embedding" in results[0].metadata  # Vec metadata merged
        assert results[0].metadata["content"] == "A"

    def test_rank_tracking(self):
        """Test that source_rank_fts and source_rank_vec are tracked."""
        engine = HybridSearchEngine(k=60)
        
        fts = [FTSResult(doc_id="doc1", rank=3, metadata={})]
        vec = [VecResult(doc_id="doc1", rank=5, score=0.9, metadata={})]
        
        results = engine.fuse(fts, vec)
        
        assert results[0].source_rank_fts == 3
        assert results[0].source_rank_vec == 5

    def test_weighted_fusion(self):
        """Test weighted fusion (fts_weight, vec_weight)."""
        engine = HybridSearchEngine(k=60)
        
        fts = [FTSResult(doc_id="doc1", rank=1, metadata={})]
        vec = [VecResult(doc_id="doc1", rank=1, score=0.9, metadata={})]
        
        # Double weight on FTS
        results = engine.fuse(fts, vec, fts_weight=2.0, vec_weight=1.0)
        
        # Score = 2/(60+1) + 1/(60+1) = 3/61
        expected = round(3.0 / 61, 6)
        assert abs(results[0].fused_score - expected) < 1e-10

    def test_limit_parameter(self):
        """Test limit parameter truncates results."""
        engine = HybridSearchEngine(k=60)
        
        fts = [FTSResult(doc_id=f"doc{i}", rank=i, metadata={}) for i in range(1, 6)]
        vec = [VecResult(doc_id=f"doc{i}", rank=i, score=0.9, metadata={}) for i in range(1, 6)]
        
        results = engine.fuse(fts, vec, limit=3)
        
        assert len(results) == 3

    def test_fuse_from_dicts(self):
        """Test convenience method for dict/tuple inputs."""
        engine = HybridSearchEngine(k=60)
        
        fts_results = [
            {"doc_id": "doc1", "session_id": "s1", "timestamp": "t1", "content": "A"},
            {"doc_id": "doc2", "session_id": "s2", "timestamp": "t2", "content": "B"},
        ]
        vec_results = [
            (0.9, {"doc_id": "doc1", "session_id": "s1", "timestamp": "t1", "embedding": [1,2,3]}),
            (0.8, {"doc_id": "doc3", "session_id": "s3", "timestamp": "t3", "embedding": [4,5,6]}),
        ]
        
        results = engine.fuse_from_dicts(fts_results, vec_results, limit=10)
        
        assert len(results) == 3
        doc1 = next(r for r in results if r.doc_id == "doc1")
        assert doc1.source_rank_fts == 1
        assert doc1.source_rank_vec == 1
        assert "embedding" in doc1.metadata

    def test_singleton_get_hybrid_search_engine(self):
        """Test get_hybrid_search_engine returns singleton."""
        engine1 = get_hybrid_search_engine(k=60)
        engine2 = get_hybrid_search_engine(k=60)
        
        assert engine1 is engine2
        
        # Different k should create new instance
        engine3 = get_hybrid_search_engine(k=10)
        assert engine3 is not engine1


# Known test vectors for RRF math verification (k=60)
# Source: Cormack et al. 2009, sqlite-vec NBC Headlines example
RRF_TEST_VECTORS = [
    # (fts_rank, vec_rank, expected_fused_score)
    (1, 1, 1.0/(60+1) + 1.0/(60+1)),  # Both rank 1
    (1, 2, 1.0/(60+1) + 1.0/(60+2)),  # FTS rank 1, vec rank 2
    (2, 1, 1.0/(60+2) + 1.0/(60+1)),  # FTS rank 2, vec rank 1
    (10, 10, 1.0/(60+10) + 1.0/(60+10)),  # Both rank 10
    (1, None, 1.0/(60+1)),  # FTS only
    (None, 1, 1.0/(60+1)),  # Vec only
    (100, 100, 1.0/(60+100) + 1.0/(60+100)),  # Both rank 100
]


class TestRRFMathVerification:
    """Verify RRF math against known test vectors."""

    @pytest.mark.parametrize("fts_rank,vec_rank,expected", RRF_TEST_VECTORS)
    def test_rrf_formula(self, fts_rank, vec_rank, expected):
        """Verify RRF formula: score = sum(1/(k + rank)) for k=60."""
        k = 60
        score = 0.0
        if fts_rank is not None:
            score += 1.0 / (k + fts_rank)
        if vec_rank is not None:
            score += 1.0 / (k + vec_rank)
        assert abs(score - expected) < 1e-10, f"RRF math mismatch: {score} != {expected}"