# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Performance benchmark: RAM usage under concurrent inference."""
import pytest
import asyncio
import time
from pathlib import Path
import tempfile
import os

@pytest.mark.benchmark
@pytest.mark.anyio
async def test_memory_usage_during_writes(soul_store):
    """Measure memory usage during multiple soul writes."""
    try:
        import psutil
        import os
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform many writes
        for i in range(50):
            data = {"entity": {"name": f"memory_{i}", "lessons_learned": [f"lesson_{i}"] * 10}}
            await soul_store.write_soul(f"memory_{i}", data, actor="system_agent", trace_id=f"memory-{i}")
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        print(f"Memory usage: initial={initial_memory:.2f}MB, final={final_memory:.2f}MB, growth={memory_growth:.2f}MB")
        # Memory growth should be reasonable (less than 100MB for 50 writes)
        assert memory_growth < 100, f"Memory growth too high: {memory_growth:.2f}MB"
    except ImportError:
        pytest.skip("psutil not installed")

@pytest.mark.benchmark
@pytest.mark.anyio
async def test_concurrent_inference_memory():
    """Measure memory usage under concurrent inference (mock)."""
    try:
        import psutil
        import os
        import anyio
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        async def mock_inference(task_id):
            # Simulate inference workload
            await asyncio.sleep(0.01)
            return {"task": task_id, "result": "x" * 1000}
        
        # Launch concurrent inferences
        async with anyio.create_task_group() as tg:
            for i in range(10):
                tg.start_soon(mock_inference, i)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        print(f"Concurrent inference memory: initial={initial_memory:.2f}MB, final={final_memory:.2f}MB, growth={memory_growth:.2f}MB")
        # Memory growth should be reasonable
        assert memory_growth < 50, f"Memory growth too high: {memory_growth:.2f}MB"
    except ImportError:
        pytest.skip("psutil not installed")

@pytest.mark.benchmark
@pytest.mark.anyio
async def test_memory_leak_detection():
    """Detect memory leaks by performing repeated operations."""
    try:
        import psutil
        import os
        process = psutil.Process(os.getpid())
        
        # Baseline memory
        baseline_memory = process.memory_info().rss / 1024 / 1024
        
        # Perform operations that might leak
        for cycle in range(5):
            # Create and destroy temporary objects
            temp_dir = tempfile.mkdtemp()
            for i in range(10):
                path = Path(temp_dir) / f"test_{i}.txt"
                path.write_text("x" * 10000)
                path.unlink()
            os.rmdir(temp_dir)
        
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_growth = final_memory - baseline_memory
        
        print(f"Memory leak test: baseline={baseline_memory:.2f}MB, final={final_memory:.2f}MB, growth={memory_growth:.2f}MB")
        # Memory should not grow significantly after cleanup
        assert memory_growth < 5, f"Possible memory leak: growth {memory_growth:.2f}MB"
    except ImportError:
        pytest.skip("psutil not installed")
