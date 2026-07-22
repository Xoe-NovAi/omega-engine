"""Chaos test: SoulStore lockfile under contention."""
import pytest
import asyncio
from pathlib import Path
import tempfile
import os

@pytest.mark.chaos
@pytest.mark.anyio
async def test_concurrent_soul_writes(soul_store):
    """Test multiple concurrent soul writes don't corrupt data."""
    import anyio
    
    async def write_soul(entity, value):
        data = {"entity": {"name": entity, "lessons_learned": [value]}}
        await soul_store.write_soul(entity, data, actor="user", trace_id=f"concurrent-{value}")
    
    # Launch multiple concurrent writes to different entities
    async with anyio.create_task_group() as tg:
        for i in range(5):
            entity = f"entity_{i}"
            # Create entity directory
            entity_dir = soul_store._get_entity_dir(entity)
            entity_dir.mkdir(exist_ok=True)
            # Write minimal soul
            import yaml
            (entity_dir / "soul.yaml").write_text(
                yaml.dump({"entity": {"name": entity, "lessons_learned": []}})
            )
            tg.start_soon(write_soul, entity, f"value_{i}")
    
    # Verify all writes succeeded and data is consistent
    for i in range(5):
        entity = f"entity_{i}"
        soul = await soul_store.read_soul(entity)
        assert soul is not None
        assert soul["entity"]["lessons_learned"] == [f"value_{i}"]

@pytest.mark.chaos
@pytest.mark.anyio
async def test_concurrent_writes_same_entity(soul_store):
    """Test multiple concurrent writes to the same entity."""
    import anyio
    
    # Create entity
    entity = "shared_entity"
    entity_dir = soul_store._get_entity_dir(entity)
    entity_dir.mkdir(exist_ok=True)
    import yaml
    (entity_dir / "soul.yaml").write_text(
        yaml.dump({"entity": {"name": entity, "lessons_learned": []}})
    )
    
    results = []
    
    async def write_and_record(value):
        data = {"entity": {"name": entity, "lessons_learned": [value]}}
        await soul_store.write_soul(entity, data, actor="user", trace_id=f"shared-{value}")
        results.append(value)
    
    # Launch concurrent writes to same entity
    # The lock should serialize them
    async with anyio.create_task_group() as tg:
        for i in range(3):
            tg.start_soon(write_and_record, f"conflict_{i}")
    
    # All writes should succeed (lock serializes them)
    assert len(results) == 3
    
    # Final state should be one of the values (last writer wins)
    soul = await soul_store.read_soul(entity)
    assert soul is not None
    assert len(soul["entity"]["lessons_learned"]) == 1
    assert soul["entity"]["lessons_learned"][0] in [f"conflict_{i}" for i in range(3)]

import yaml
