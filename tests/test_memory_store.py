from unittest.mock import patch
import pytest
import os
import json
from pathlib import Path
from omega.memory_store import MemoryStore, get_memory_store, reset_memory_store, async_reset_memory_store

@pytest.mark.anyio
async def test_get_history_empty_returns_list(temp_data_dir):
    reset_memory_store()
    store = get_memory_store()
    history = await store.get_history("Sophia", "ses_123")
    assert history == []

@pytest.mark.anyio
async def test_add_exchange_stores_in_hot_cache(temp_data_dir):
    reset_memory_store()
    store = get_memory_store()
    await store.add_exchange("Sophia", "ses_123", "Hello", "Hi there!")
    history = await store.get_history("Sophia", "ses_123")
    assert len(history) == 1
    assert history[0]["user"] == "Hello"
    assert history[0]["assistant"] == "Hi there!"

@pytest.mark.anyio
async def test_add_exchange_persists_to_warm_file(temp_data_dir):
    reset_memory_store()
    store = get_memory_store()
    await store.add_exchange("Sophia", "ses_123", "Hello", "Hi there!")
    
    # Async reset: flushes batch buffer to providers before abandoning
    await async_reset_memory_store()
    store_new = get_memory_store()
    
    history = await store_new.get_history("Sophia", "ses_123")
    assert len(history) == 1
    assert history[0]["user"] == "Hello"

@pytest.mark.anyio
async def test_get_history_reads_from_hot_cache(temp_data_dir, monkeypatch):
    reset_memory_store()
    store = get_memory_store()
    await store.add_exchange("Sophia", "ses_123", "Hello", "Hi there!")
    
    # Mock the file read to ensure it's using the cache
    with patch("anyio.open_file", side_effect=Exception("Should not be called")) as mock_open:
        history = await store.get_history("Sophia", "ses_123")
        assert len(history) == 1
        mock_open.assert_not_called()

@pytest.mark.anyio
async def test_get_history_respects_limit(temp_data_dir):
    reset_memory_store()
    store = get_memory_store()
    for i in range(10):
        await store.add_exchange("Sophia", "ses_123", f"User {i}", f"Assistant {i}")
    
    history = await store.get_history("Sophia", "ses_123", limit=3)
    assert len(history) == 3
    assert history[-1]["user"] == "User 9"

@pytest.mark.anyio
async def test_get_history_from_warm_file(temp_data_dir):
    reset_memory_store()
    store = get_memory_store()
    await store.add_exchange("Sophia", "ses_123", "Hello", "Hi there!")
    
    # Flush batch buffer to providers before checking file
    await store.flush()
    
    # Manually verify file exists
    safe_name = "sophia"
    path = Path(os.environ["OMEGA_DATA_DIR"]) / "memory" / "entities" / safe_name / "ses_123.json"
    assert path.exists()

@pytest.mark.anyio
async def test_compact_keeps_first_and_last(temp_data_dir):
    reset_memory_store()
    store = get_memory_store()
    # MAX_HISTORY is 20. Add 25.
    for i in range(25):
        await store.add_exchange("Sophia", "ses_123", f"User {i}", f"Assistant {i}")
    
    history = await store.get_history("Sophia", "ses_123", limit=100)
    # Compacted: keep = 20 // 2 = 10. First 10 + Last 10 + 1 summary = 21.
    assert len(history) == 21
    assert "compacted" in history[10]["assistant"]

@pytest.mark.anyio
async def test_archive_session_moves_to_cold(temp_data_dir):
    reset_memory_store()
    store = get_memory_store()
    await store.add_exchange("Sophia", "ses_123", "Hello", "Hi there!")
    
    # Flush batch buffer to providers before archive (providers need the data)
    await store.flush()
    
    success = await store.archive_session("Sophia", "ses_123")
    assert success is True
    
    # Warm file should be gone, cold file should exist
    warm_path = Path(os.environ["OMEGA_DATA_DIR"]) / "memory" / "entities" / "sophia" / "ses_123.json"
    cold_path = Path(os.environ["OMEGA_DATA_DIR"]) / "memory" / "archive" / "sophia" / "ses_123.json.gz"
    assert not warm_path.exists()
    assert cold_path.exists()

@pytest.mark.anyio
async def test_trace_exchange_creates_file(temp_data_dir):
    reset_memory_store()
    store = get_memory_store()
    await store.trace_exchange("trc_123", "Sophia", "ses_123", "Hello", "Hi")
    
    path = Path(os.environ["OMEGA_DATA_DIR"]) / "memory" / "trace" / "trc_123.json"
    assert path.exists()

@pytest.mark.anyio
async def test_stats_returns_dict(temp_data_dir):
    reset_memory_store()
    store = get_memory_store()
    await store.add_exchange("Sophia", "ses_123", "Hello", "Hi")
    stats = store.stats()
    assert isinstance(stats, dict)
    assert stats["saves"] >= 1

@pytest.mark.anyio
async def test_close_flushes_hot_cache(temp_data_dir):
    reset_memory_store()
    store = get_memory_store()
    # Add exchange but don't let it save naturally (mocking a failure or just checking flush)
    await store.add_exchange("Sophia", "ses_123", "Hello", "Hi")
    await store.close()
    
    # Check if file exists
    path = Path(os.environ["OMEGA_DATA_DIR"]) / "memory" / "entities" / "sophia" / "ses_123.json"
    assert path.exists()

@pytest.mark.anyio
async def test_get_memory_store_returns_singleton(temp_data_dir):
    reset_memory_store()
    s1 = get_memory_store()
    s2 = get_memory_store()
    assert s1 is s2

@pytest.mark.anyio
async def test_add_exchange_none_session_id(temp_data_dir):
    """add_exchange with session_id=None must not create None.json."""
    reset_memory_store()
    store = get_memory_store()
    await store.add_exchange("Sophia", None, "Hello", "Hi there!")

    # No file should be created
    none_json = Path(os.environ["OMEGA_DATA_DIR"]) / "memory" / "entities" / "sophia" / "None.json"
    assert not none_json.exists()

    # Hot cache should not contain a None entry
    assert "sophia:None" not in store._hot

    # get_history with None should return empty
    history = await store.get_history("Sophia", None)
    assert history == []

@pytest.mark.anyio
async def test_add_exchange_empty_session_id(temp_data_dir):
    """add_exchange with session_id='' must be skipped."""
    reset_memory_store()
    store = get_memory_store()
    await store.add_exchange("Sophia", "", "Hello", "Hi there!")

    # Hot cache should not contain an empty string entry
    assert "sophia:" not in store._hot

    # get_history with empty string should return empty
    history = await store.get_history("Sophia", "")
    assert history == []

@pytest.mark.anyio
async def test_get_history_none_session_id_returns_empty(temp_data_dir):
    """get_history with session_id=None must return empty list."""
    reset_memory_store()
    store = get_memory_store()
    history = await store.get_history("Sophia", None)
    assert history == []


# ═══════════════════════════════════════════════════════════════════════════
# HYBRID SEARCH (RRF) TESTS
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.anyio
async def test_search_empty_query_returns_empty(temp_data_dir):
    """search() with empty query returns empty list."""
    reset_memory_store()
    store = get_memory_store()
    results = await store.search("", "Sophia")
    assert results == []


@pytest.mark.anyio
async def test_search_whitespace_query_returns_empty(temp_data_dir):
    """search() with whitespace-only query returns empty list."""
    reset_memory_store()
    store = get_memory_store()
    results = await store.search("   ", "Sophia")
    assert results == []


@pytest.mark.anyio
async def test_search_fts_results_have_rrf_score(temp_data_dir):
    """search() results include _rrf_score field from RRF fusion."""
    reset_memory_store()
    store = get_memory_store()
    # Add exchanges with searchable content
    await store.add_exchange("Sophia", "ses_search_001", "What is sovereignty?", "Sovereignty means self-governance.")
    await store.add_exchange("Sophia", "ses_search_002", "Tell me about courage.", "Courage is strength in the face of fear.")
    await store.flush()

    results = await store.search("sovereignty", "Sophia", limit=10)
    # At least the FTS result should be present
    assert len(results) >= 1
    # Results should have _rrf_score from RRF fusion
    for r in results:
        assert "_rrf_score" in r
        assert r["_rrf_score"] > 0


@pytest.mark.anyio
async def test_search_fts_only_when_vector_unavailable(temp_data_dir):
    """search() gracefully degrades to FTS-only when vector store is unavailable."""
    reset_memory_store()
    store = get_memory_store()
    # Force vector store to MemoryVectorAdapter (always available, no Qdrant needed)
    from omega.memory.vector_adapters import MemoryVectorAdapter
    store.vector_store = MemoryVectorAdapter()

    await store.add_exchange("Sophia", "ses_hybrid_001", "What is sovereignty?", "Sovereignty means self-governance.")
    await store.flush()

    results = await store.search("sovereignty", "Sophia", limit=10)
    assert len(results) >= 1
    # FTS results have 'content' field (not 'user'/'assistant')
    # Check that at least one result has relevant content
    all_text = " ".join(r.get("content", "").lower() for r in results)
    assert "sovereignt" in all_text  # stemmer may strip suffix


@pytest.mark.anyio
async def test_search_respects_limit(temp_data_dir):
    """search() respects the limit parameter."""
    reset_memory_store()
    store = get_memory_store()
    # Add multiple exchanges
    for i in range(5):
        await store.add_exchange("Sophia", f"ses_limit_{i:03d}", f"Query about topic {i}", f"Response about topic {i}")
    await store.flush()

    results = await store.search("topic", "Sophia", limit=2)
    assert len(results) <= 2
