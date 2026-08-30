# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

import pytest
import anyio
import os
from pathlib import Path
from omega.memory.fts_index import ConversationFTSIndex
from omega.memory_store import MemoryStore, reset_memory_store

@pytest.fixture
def fts_db(tmp_path):
    db_path = tmp_path / "test_fts.db"
    fts = ConversationFTSIndex(db_path)
    fts.initialize()
    yield fts
    fts.close()

@pytest.mark.anyio
async def test_fts_basic_search(fts_db):
    await fts_db.index_exchange("sess_1", "kali", "user", "How do I build a house?")
    await fts_db.index_exchange("sess_1", "kali", "assistant", "Use bricks and mortar.")
    
    # Search for "build"
    results = await fts_db.search("build", "kali")
    assert len(results) == 1
    assert "build a house" in results[0]["content"]
    
    # Search for "mortar"
    results = await fts_db.search("mortar", "kali")
    assert len(results) == 1
    assert "bricks and mortar" in results[0]["content"]

@pytest.mark.anyio
async def test_fts_sovereign_isolation(fts_db):
    await fts_db.index_exchange("sess_1", "kali", "user", "Secret code is 1234")
    await fts_db.index_exchange("sess_2", "maat", "user", "Secret code is 5678")
    
    # Kali searches for "Secret"
    results = await fts_db.search("Secret", "kali")
    assert len(results) == 1
    assert "1234" in results[0]["content"]
    
    # Maat searches for "Secret"
    results = await fts_db.search("Secret", "maat")
    assert len(results) == 1
    assert "5678" in results[0]["content"]

@pytest.mark.anyio
async def test_fts_cleanup(fts_db):
    await fts_db.index_exchange("sess_1", "kali", "user", "Hello world")
    assert await fts_db.count() == 1
    
    await fts_db.remove_session("sess_1")
    assert await fts_db.count() == 0
    
    results = await fts_db.search("Hello", "kali")
    assert len(results) == 0

@pytest.mark.anyio
async def test_memorystore_integration(tmp_path, monkeypatch):
    # Mock data dir
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    monkeypatch.setenv("OMEGA_DATA_DIR", str(data_dir))
    monkeypatch.setenv("OMEGA_ENV", "test")
    
    reset_memory_store()
    from omega.memory_store import get_memory_store
    store = get_memory_store()
    
    await store.add_exchange("kali", "sess_1", "What is the meaning of life?", "42")
    
    # Search via MemoryStore
    results = await store.search_fts("meaning", "kali")
    assert len(results) >= 1
    assert "meaning of life" in results[0]["content"]
    
    await store.close()
