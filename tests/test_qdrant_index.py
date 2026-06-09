import pytest
import anyio
from unittest.mock import AsyncMock, MagicMock
from omega.library.indexer import Indexer
from omega.memory.vector_adapters import IVectorStoreAdapter, MemoryVectorAdapter

class MockVectorAdapter(IVectorStoreAdapter):
    def __init__(self, mock_results=None):
        self.mock_results = mock_results or []
    
    async def upsert(self, entity_name, vector, metadata, id=None):
        return "mock_id"
    
    async def query(self, entity_name, vector, limit=10, filter=None):
        return self.mock_results
    
    async def delete(self, entity_name, ids):
        return True
    
    async def get_status(self):
        return {"status": "healthy"}

@pytest.mark.anyio
async def test_hybrid_search_rrf_merging():
    # Setup: Mock adapter that returns a specific set of results
    # Doc A: High vector score, low FTS rank
    # Doc B: Low vector score, high FTS rank
    # Doc C: Medium both
    mock_results = [
        (0.9, {"doc_id": "doc_a", "title": "A"}),
        (0.1, {"doc_id": "doc_b", "title": "B"}),
        (0.5, {"doc_id": "doc_c", "title": "C"}),
    ]
    adapter = MockVectorAdapter(mock_results=mock_results)
    indexer = Indexer(vector_adapter=adapter)
    
    # We need to mock FTS results since we don't want to create a real DB
    # We'll patch the search_fts method
    indexer.search_fts = AsyncMock(return_value=[
        {"doc_id": "doc_b", "title": "B", "_rank": -10.0}, # Best FTS
        {"doc_id": "doc_c", "title": "C", "_rank": -5.0},  # Mid FTS
        {"doc_id": "doc_a", "title": "A", "_rank": -1.0},  # Worst FTS
    ])
    
    results = await indexer.hybrid_search("test query", limit=10)
    
    # Verify RRF merging:
    # Doc B: FTS rank 1, Vec rank 3
    # Doc A: FTS rank 3, Vec rank 1
    # Doc C: FTS rank 2, Vec rank 2
    # RRF should balance these.
    assert len(results) > 0
    assert results[0]["doc_id"] in ["doc_a", "doc_b", "doc_c"]
    assert "_rrf_score" in results[0]
    
    await indexer.close()


@pytest.mark.anyio
async def test_vector_fallback_to_memory():
    # Test that Indexer defaults to MemoryVectorAdapter if none provided
    indexer = Indexer()
    assert isinstance(indexer._vector_adapter, MemoryVectorAdapter)
    
    # Test basic upsert/query in memory
    await indexer._vector_adapter.upsert("test_ent", [0.1, 0.2], {"title": "test"})
    res = await indexer._vector_adapter.query("test_ent", [0.1, 0.2])
    assert len(res) == 1
    assert res[0][1]["title"] == "test"
    
    await indexer.close()

