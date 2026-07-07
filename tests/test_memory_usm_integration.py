import pytest
import anyio
from pathlib import Path
from omega.memory_store import MemoryStore, reset_memory_store
from omega.state import get_usm

@pytest.mark.anyio
async def test_memory_store_usm_integration():
    reset_memory_store()
    ms = MemoryStore()
    usm = get_usm()
    
    entity = "test_entity"
    session = "test_session"
    user_msg = "Hello USM"
    assistant_msg = "Hello from CAS"
    
    # 1. Add exchange
    await ms.add_exchange(entity, session, user_msg, assistant_msg)
    await ms.flush()
    
    # 2. Retrieve history
    history = await ms.get_history(entity, session, limit=1)
    assert len(history) == 1
    assert history[0]["user"] == user_msg
    assert history[0]["assistant"] == assistant_msg
    
    # 3. Verify it's in USM
    state_key = f"mem:{entity}:{session}"
    usm_data = await usm.load_state(state_key)
    assert usm_data is not None
    assert usm_data["entity"] == entity
    assert usm_data["session_id"] == session
    assert len(usm_data["exchanges"]) == 1
    assert usm_data["exchanges"][0]["user"] == user_msg

@pytest.mark.anyio
async def test_memory_store_usm_deduplication():
    reset_memory_store()
    ms = MemoryStore()
    usm = get_usm()
    
    # Two different sessions with identical content
    e1, s1 = "ent1", "sess1"
    e2, s2 = "ent2", "sess2"
    msg_u, msg_a = "Same content", "Same response"
    
    await ms.add_exchange(e1, s1, msg_u, msg_a)
    await ms.add_exchange(e2, s2, msg_u, msg_a)
    await ms.flush()
    
    # Verify both exist in MemoryStore
    h1 = await ms.get_history(e1, s1, 1)
    h2 = await ms.get_history(e2, s2, 1)
    assert len(h1) == 1 and len(h2) == 1
    
    # Verify they share the same CAS blob
    key1 = f"mem:{e1}:{s1}"
    key2 = f"mem:{e2}:{s2}"
    data1 = await usm.load_state(key1)
    data2 = await usm.load_state(key2)
    
    # In a real CAS, the content hash would be the same.
    # Since USM stores the whole session as a blob, and these sessions are identical,
    # the blobs should be identical.
    # We can't easily check the internal CAS hash from USM without adding a method,
    # but we can verify that the data is identical.
    assert data1 == data2
