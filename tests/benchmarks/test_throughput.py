"""Performance benchmark: Requests per second under load."""
import pytest
import asyncio
import time
from pathlib import Path
import tempfile
import os

@pytest.mark.benchmark
@pytest.mark.anyio
async def test_soulstore_write_throughput(soul_store):
    """Measure SoulStore writes per second."""
    iterations = 100
    start = time.perf_counter()
    for i in range(iterations):
        data = {"entity": {"name": f"throughput_{i}", "lessons_learned": [f"lesson_{i}"]}}
        await soul_store.write_soul(f"throughput_{i}", data, actor="system_agent", trace_id=f"throughput-{i}")
    elapsed = time.perf_counter() - start
    writes_per_second = iterations / elapsed
    print(f"SoulStore throughput: {writes_per_second:.2f} writes/sec")
    assert writes_per_second > 10, f"Throughput too low: {writes_per_second:.2f} writes/sec"

@pytest.mark.benchmark
@pytest.mark.anyio
async def test_concurrent_read_throughput(soul_store):
    """Measure concurrent read throughput."""
    import anyio
    
    # Create some entities first
    for i in range(10):
        entity = f"read_entity_{i}"
        entity_dir = soul_store._get_entity_dir(entity)
        entity_dir.mkdir(exist_ok=True)
        import yaml
        (entity_dir / "soul.yaml").write_text(
            yaml.dump({"entity": {"name": entity, "lessons_learned": [f"lesson_{i}"]}})
        )
    
    async def read_soul(entity):
        return await soul_store.read_soul(entity)
    
    # Concurrent reads
    start = time.perf_counter()
    async with anyio.create_task_group() as tg:
        for i in range(10):
            tg.start_soon(read_soul, f"read_entity_{i}")
    elapsed = time.perf_counter() - start
    
    reads_per_second = 10 / elapsed
    print(f"Concurrent read throughput: {reads_per_second:.2f} reads/sec")
    assert reads_per_second > 50, f"Read throughput too low: {reads_per_second:.2f} reads/sec"
