# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

import pytest
import anyio
import os
from unittest.mock import AsyncMock, MagicMock
from omega.memory_store import MemoryStore, reset_memory_store
from omega.memory.vector_adapters import IVectorStoreAdapter

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

@pytest.fixture
def store(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    monkeypatch.setenv("OMEGA_DATA_DIR", str(data_dir))
    monkeypatch.setenv("OMEGA_ENV", "test")
    reset_memory_store()
    from omega.memory_store import get_memory_store
    store = get_memory_store()
    yield store
    # cleanup
    try:
        anyio.run(store.close)
    except Exception as e:
        print(f"Warning: cleanup failed: {e}")
    import shutil
    shutil.rmtree(data_dir)


@pytest.mark.anyio
async def test_hybrid_search_rrf_logic(store):
    # 1. Add some data
    # We'll use specific timestamps to distinguish entries
    ts1 = "2026-06-09T12:00:00Z"
    ts2 = "2026-06-09T13:00:00Z"
    ts3 = "2026-06-09T14:00:00Z"
    
    # Manually index in FTS to control ranks
    store.fts.index_exchange("sess_a", "kali", "user", "Alpha keyword")
    store.fts.index_exchange("sess_b", "kali", "user", "Beta keyword")
    store.fts.index_exchange("sess_c", "kali", "user", "Gamma keyword")
    
    # Mock vector results
    # Doc C: Vector rank 1 (highest)
    # Doc A: Vector rank 2
    # Doc B: Vector rank 3
    mock_vec_results = [
        (0.9, {"session_id": "sess_c", "timestamp": ts3}),
        (0.8, {"session_id": "sess_a", "timestamp": ts1}),
        (0.7, {"session_id": "sess_b", "timestamp": ts2}),
    ]
    store.vector_store = MockVectorAdapter(mock_results=mock_vec_results)
    
    # Mock FTS results (returning them in specific order to define ranks)
    # Doc A: FTS rank 1
    # Doc B: FTS rank 2
    # Doc C: FTS rank 3
    store.search_fts = AsyncMock(return_value=[
        {"session_id": "sess_a", "timestamp": ts1, "content": "Alpha keyword"},
        {"session_id": "sess_b", "timestamp": ts2, "content": "Beta keyword"},
        {"session_id": "sess_c", "timestamp": ts3, "content": "Gamma keyword"},
    ])
    
    # 2. Run hybrid search
    results = await store.search("keyword", "kali", limit=3)
    
    # 3. Verify RRF
    # FTS ranks: A=1, B=2, C=3
    # Vec ranks: C=1, A=2, B=3
    # RRF(A) = 1/(60+1) + 1/(60+2) = 0.01639 + 0.01612 = 0.03251
    # RRF(C) = 1/(60+3) + 1/(60+1) = 0.01587 + 0.01639 = 0.03226
    # RRF(B) = 1/(60+2) + 1/(60+3) = 0.01612 + 0.01587 = 0.03199
    # Winner should be A!
    
    assert len(results) == 3
    assert results[0]["session_id"] == "sess_a"
    assert results[1]["session_id"] == "sess_c"
    assert results[2]["session_id"] == "sess_b"
    assert "_rrf_score" in results[0]
