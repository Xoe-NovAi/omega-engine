from unittest.mock import patch
import pytest
import os
import json
from pathlib import Path
from omega.memory_store import MemoryStore, get_memory_store, reset_memory_store

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
    
    # Clear hot cache by creating a new store instance or resetting
    reset_memory_store()
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
