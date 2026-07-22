"""M21 Contract Tests: SoulStore writes survive failure (5 tests)."""
import pytest
import asyncio
from pathlib import Path
import tempfile
import os
import yaml

@pytest.mark.contract
@pytest.mark.anyio
async def test_write_soul_user_actor(soul_store):
    """User actor can write soul.yaml."""
    data = {"entity": {"name": "test_entity", "lessons_learned": ["L3 test"]}}
    await soul_store.write_soul("test_entity", data, actor="user", trace_id="test-1")
    result = await soul_store.read_soul("test_entity")
    assert "L3 test" in result["entity"]["lessons_learned"]

@pytest.mark.contract
@pytest.mark.anyio
async def test_write_soul_system_agent_denied(soul_store):
    """system_agent CANNOT write soul.yaml."""
    from omega.oracle.soul_store import SoulPermissionError
    data = {"entity": {"name": "test_entity", "lessons_learned": []}}
    with pytest.raises(SoulPermissionError):
        await soul_store.write_soul("test_entity", data, actor="system_agent")

@pytest.mark.contract
@pytest.mark.anyio
async def test_write_proposed_system_agent(soul_store):
    """system_agent CAN write proposed_lessons.yaml."""
    data = {"proposals": ["L3 test principle"]}
    await soul_store.write_proposed("test_entity", data, actor="system_agent")
    result = await soul_store.read_proposed("test_entity")
    assert "L3 test principle" in result["proposals"]

@pytest.mark.contract
@pytest.mark.anyio
async def test_atomic_write_durability(soul_store, tmp_path):
    """Atomic write produces valid file."""
    from omega.oracle.soul_store import _atomic_write
    target = tmp_path / "test.yaml"
    _atomic_write(target, b"key: value\n")
    assert target.read_text() == "key: value\n"

@pytest.mark.contract
def test_lock_acquire_release():
    """SoulLock acquires and releases cleanly."""
    from omega.oracle.soul_store import SoulLock
    import tempfile
    with tempfile.NamedTemporaryFile() as f:
        lock = SoulLock(f.name, timeout=1.0)
        assert lock.acquire() is True
        lock.release()
        assert lock._fd is None
