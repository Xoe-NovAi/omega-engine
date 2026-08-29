#!/usr/bin/env python3
"""Benchmark script for SQLite-vec adapter optimizations.

Tests:
1. Single upsert latency
2. Batch upsert throughput
3. Query latency (with JOIN optimization)
4. Hybrid search latency
5. Memory usage

Run: python3 scripts/benchmark_sqlite_vec.py
"""

import asyncio
import random
import time
import uuid
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from omega.memory.sqlite_vec_adapter_optimized import SQLiteVecAdapterOptimized


async def generate_test_vector(dim: int = 768) -> list:
    """Generate a random test vector."""
    return [random.uniform(-1, 1) for _ in range(dim)]


async def benchmark_single_upsert(adapter, num_ops: int = 100):
    """Benchmark single upsert operations."""
    print(f"\n=== Single Upsert Benchmark ({num_ops} ops) ===")
    latencies = []
    
    for i in range(num_ops):
        vector = await generate_test_vector(768)
        start = time.perf_counter()
        await adapter.upsert(
            entity_name="benchmark",
            vector=vector,
            metadata={"content": f"Test content {i}", "session_id": "bench", "role": "user"},
            collection="omega_vec_gemma_768",
        )
        latency = (time.perf_counter() - start) * 1000
        latencies.append(latency)
    
    avg_latency = sum(latencies) / len(latencies)
    p99_latency = sorted(latencies)[int(len(latencies) * 0.99)]
    print(f"  Avg latency: {avg_latency:.2f} ms")
    print(f"  P99 latency: {p99_latency:.2f} ms")
    print(f"  Throughput: {1000 / avg_latency:.1f} ops/sec")
    return latencies


async def benchmark_batch_upsert(adapter, batch_size: int = 100, num_batches: int = 10):
    """Benchmark batch upsert operations."""
    print(f"\n=== Batch Upsert Benchmark ({num_batches} batches of {batch_size}) ===")
    latencies = []
    total_vectors = 0
    
    for batch in range(num_batches):
        items = []
        for i in range(batch_size):
            vector = await generate_test_vector(768)
            items.append({
                "entity_name": "benchmark",
                "vector": await generate_test_vector(768),
                "metadata": {"content": f"Batch {batch} item {i}", "session_id": "bench", "role": "user"},
            })
        
        start = time.perf_counter()
        await adapter.batch_upsert(items, collection="omega_vec_gemma_768")
        latency = (time.perf_counter() - start) * 1000
        latencies.append(latency)
        total_vectors += batch_size
    
    avg_latency = sum(latencies) / len(latencies)
    total_time = sum(latencies) / 1000
    throughput = total_vectors / total_time
    print(f"  Avg batch latency: {sum(latencies) / len(latencies):.2f} ms")
    print(f"  Total vectors: {total_vectors}")
    print(f"  Total time: {total_time:.2f} s")
    print(f"  Throughput: {throughput:.1f} vectors/sec")
    return latencies


async def benchmark_query(adapter, num_queries: int = 100):
    """Benchmark query operations (with JOIN optimization)."""
    print(f"\n=== Query Benchmark ({num_queries} queries) ===")
    latencies = []
    
    for i in range(num_queries):
        vector = await generate_test_vector(768)
        start = time.perf_counter()
        results = await adapter.query(
            entity_name="benchmark",
            vector=vector,
            limit=10,
            collection="omega_vec_gemma_768",
        )
        latency = (time.perf_counter() - start) * 1000
        latencies.append(latency)
    
    avg_latency = sum(latencies) / len(latencies)
    p99_latency = sorted(latencies)[int(len(latencies) * 0.99)]
    print(f"  Avg latency: {avg_latency:.2f} ms")
    print(f"  P99 latency: {p99_latency:.2f} ms")
    print(f"  Throughput: {1000 / avg_latency:.1f} queries/sec")
    return latencies


async def benchmark_hybrid_search(adapter, num_searches: int = 50):
    """Benchmark hybrid search operations."""
    print(f"\n=== Hybrid Search Benchmark ({num_searches} searches) ===")
    latencies = []
    
    for i in range(num_searches):
        vector = await generate_test_vector(768)
        start = time.perf_counter()
        results = await adapter.hybrid_search(
            query=f"test query {i}",
            entity_name="benchmark",
            vector=vector,
            limit=20,
        )
        latency = (time.perf_counter() - start) * 1000
        latencies.append(latency)
    
    avg_latency = sum(latencies) / len(latencies)
    p99_latency = sorted(latencies)[int(len(latencies) * 0.99)]
    print(f"  Avg latency: {avg_latency:.2f} ms")
    print(f"  P99 latency: {p99_latency:.2f} ms")
    return latencies


async def main():
    print("=" * 60)
    print("SQLite-vec Adapter Optimization Benchmark")
    print("=" * 60)
    
    # Initialize adapter
    adapter = SQLiteVecAdapterOptimized(
        db_path="/tmp/benchmark_omega_memory.db",
        embedding_dim=768,
        read_pool_size=4,
        batch_size=100,
        enable_metrics=True,
    )
    
    try:
        # Run benchmarks
        await benchmark_single_upsert(adapter, num_ops=50)
        await benchmark_batch_upsert(adapter, batch_size=50, num_batches=5)
        await benchmark_query(adapter, num_queries=50)
        await benchmark_hybrid_search(adapter, num_searches=20)
        
        # Print metrics
        print("\n=== Adapter Metrics ===")
        metrics = adapter.get_metrics()
        for key, value in metrics.items():
            if isinstance(value, list):
                print(f"  {key}: {len(value)} samples")
            else:
                print(f"  {key}: {value}")
        
        print("\n=== Benchmark Complete ===")
        
    finally:
        await adapter.close()
        # Clean up
        import os
        for suffix in ["", "-wal", "-shm"]:
            path = f"/tmp/benchmark_omega_memory.db{suffix}"
            if os.path.exists(path):
                os.remove(path)


if __name__ == "__main__":
    asyncio.run(main())