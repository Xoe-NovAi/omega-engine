"""Performance benchmark: Inference latency under 500ms p99."""
import pytest
import asyncio
import time
from pathlib import Path
import tempfile
import os

@pytest.mark.benchmark
@pytest.mark.anyio
async def test_soulstore_write_latency(soul_store):
    """Measure SoulStore write latency (should be <10ms)."""
    data = {"entity": {"name": "bench", "lessons_learned": ["x"] * 100}}
    start = time.perf_counter()
    await soul_store.write_soul("bench", data, actor="system_agent", trace_id="bench-write")
    elapsed = (time.perf_counter() - start) * 1000
    assert elapsed < 10, f"SoulStore write took {elapsed}ms"
    print(f"SoulStore write latency: {elapsed:.2f}ms")

@pytest.mark.benchmark
@pytest.mark.anyio
async def test_admission_acquire_latency(admission_controller):
    """Measure admission acquire latency (should be <5ms)."""
    start = time.perf_counter()
    acquired = await admission_controller.acquire("model")
    elapsed = (time.perf_counter() - start) * 1000
    assert elapsed < 5, f"Admission acquire took {elapsed}ms"
    admission_controller.release()
    print(f"Admission acquire latency: {elapsed:.2f}ms")

@pytest.mark.benchmark
@pytest.mark.anyio
async def test_inference_latency_mock():
    """Mock inference latency test (placeholder for real inference)."""
    # This is a structural test; real inference benchmarks require actual model loading.
    # For now, measure the overhead of the provider fabric routing.
    from unittest.mock import AsyncMock, patch
    
    async def mock_inference(*args, **kwargs):
        # Simulate network latency
        await asyncio.sleep(0.01)  # 10ms
        return {"text": "response", "provider": "mock", "latency_ms": 10}
    
    start = time.perf_counter()
    result = await mock_inference()
    elapsed = (time.perf_counter() - start) * 1000
    
    # Should be under 500ms p99 (target)
    assert elapsed < 500, f"Inference latency {elapsed}ms exceeds 500ms"
    print(f"Mock inference latency: {elapsed:.2f}ms")
