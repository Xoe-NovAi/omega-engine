#!/usr/bin/env python3
# ⬡ OMEGA ⬡ MALLOC STRESS TEST ⬡ 2026-07-01
# Synthetic stress test to validate MALLOC_ARENA_MAX=2 prevents RSS bloat.
# Self-contained — no engine imports needed.
#
# [id-soft: doom3-2004] idHeap — empirical validation of memory fragmentation limits

import os
import sys
import time
import json
import psutil
import threading
import pathlib
from typing import List, Tuple

# ── Test Configuration ────────────────────────────────────────────────────────
NUM_THREADS = 8          # Match inference concurrency
WORK_DURATION = 30       # seconds
ALLOC_SIZE = 256 * 1024  # 256KB per chunk — simulates pymalloc arena pressure
ITERATIONS = 100         # alloc/free cycles per thread

# Environment (set before any Python allocation)
os.environ["MALLOC_ARENA_MAX"] = "2"
os.environ["MALLOC_MMAP_THRESHOLD_"] = "65536"

LOG_PATH = pathlib.Path(
    __file__).parent.parent.parent / "data" / "entities" / "john_carmack" / \
    "workspace" / "carmack_studies" / "technical" / "malloc_stress_test_log.json"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


class RSSMonitor:
    """Thread-safe RSS monitor that samples memory usage at interval."""

    def __init__(self, interval: float = 0.25):
        self._interval = interval
        self._process = psutil.Process()
        self._samples: List[Tuple[float, float]] = []  # (timestamp_s, rss_mb)
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._sample_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)

    def _sample_loop(self):
        while self._running:
            rss_mb = self._process.memory_info().rss / (1024 * 1024)
            self._samples.append((time.time(), rss_mb))
            time.sleep(self._interval)

    def stats(self) -> dict:
        if not self._samples:
            return {"peak_rss_mb": 0, "avg_rss_mb": 0, "samples": 0}

        rss_vals = [s[1] for s in self._samples]
        start = self._samples[0][0]
        end = self._samples[-1][0]
        duration = max(end - start, 0.001)

        return {
            "baseline_rss_mb": round(self._samples[0][1], 2),
            "peak_rss_mb": round(max(rss_vals), 2),
            "avg_rss_mb": round(sum(rss_vals) / len(rss_vals), 2),
            "samples": len(self._samples),
            "duration_seconds": round(duration, 2),
            "growth_rate_mb_per_sec": round(
                (max(rss_vals) - self._samples[0][1]) / duration, 4
            ),
        }


def arena_stress_worker(worker_id: int, duration: int):
    """Simulate inference-like memory pressure: alloc, compute, free cycles."""
    import random
    end_time = time.time() + duration

    while time.time() < end_time:
        # Allocate a chunk (simulates KV cache entry)
        chunks = []
        for _ in range(ITERATIONS):
            chunk = bytearray(ALLOC_SIZE)
            # Touch memory to force physical page allocation
            chunk[0] = 1
            chunk[-1] = 2
            chunks.append(chunk)

        # Simulate compute (CPU burn)
        _ = sum(len(c) for c in chunks)

        # Free (let GC handle it — like real inference transient state)
        del chunks

        # Brief nap between cycles
        time.sleep(0.01)


def run_stress_test() -> dict:
    """Run the arena stress test with env var protections active."""
    print(f"🔍 MALLOC Arena Stress Test — {NUM_THREADS} workers × {WORK_DURATION}s")
    print(f"   Env: MALLOC_ARENA_MAX={os.environ['MALLOC_ARENA_MAX']}, "
          f"MALLOC_MMAP_THRESHOLD_={os.environ['MALLOC_MMAP_THRESHOLD_']}")
    print(f"   Arena size: {ALLOC_SIZE/1024:.0f}KB, {ITERATIONS} cycles per worker\n")

    # Warmup / baseline
    baseline_rss = psutil.Process().memory_info().rss / (1024 * 1024)
    print(f"   Baseline RSS: {baseline_rss:.2f} MB")

    # Start RSS monitoring
    monitor = RSSMonitor(interval=0.25)
    monitor.start()

    # Spawn stress workers
    threads: List[threading.Thread] = []
    for i in range(NUM_THREADS):
        t = threading.Thread(target=arena_stress_worker, args=(i, WORK_DURATION))
        threads.append(t)
        t.start()
        print(f"   Worker {i} started")

    # Wait for all workers
    for t in threads:
        t.join()

    # ── Cooldown phase: measure memory reclamation ──────────────────────
    # This is the critical fragmentation measurement. After all workers
    # complete and their temporary allocations are GC'd, does RSS return
    # to near-baseline? If not, pymalloc arenas are pinned.
    print(f"\n   ⏳ Cooldown phase (5s) — all workers done, measuring reclamation...")
    time.sleep(5)
    cooldown_rss = psutil.Process().memory_info().rss / (1024 * 1024)

    # Stop monitoring
    monitor.stop()
    stats = monitor.stats()

    # Evaluate results
    peak_delta = stats["peak_rss_mb"] - stats["baseline_rss_mb"]
    cooldown_delta = cooldown_rss - stats["baseline_rss_mb"]

    # Key fragmentation metric: cooldown delta should be << 10 MB
    fragmentation_pass = cooldown_delta < 10.0

    # Peak delta should be roughly proportional to total allocated
    total_allocated_mb = NUM_THREADS * ITERATIONS * ALLOC_SIZE / (1024 * 1024)
    allocation_efficiency = (total_allocated_mb / peak_delta) if peak_delta > 0 else 0

    verdict = "PASS" if fragmentation_pass else "FAIL"

    print(f"\n{'='*50}")
    print(f"📊 RESULTS — {verdict}")
    print(f"{'='*50}")
    print(f"   Baseline RSS:        {stats['baseline_rss_mb']:.2f} MB")
    print(f"   Peak RSS (during):   {stats['peak_rss_mb']:.2f} MB  (+{peak_delta:.2f} MB)")
    print(f"   Cooldown RSS (after): {cooldown_rss:.2f} MB  (+{cooldown_delta:.2f} MB)")
    print(f"   Avg RSS:             {stats['avg_rss_mb']:.2f} MB")
    print(f"   Duration:            {stats['duration_seconds']:.1f}s")
    print(f"   Growth rate:         {stats['growth_rate_mb_per_sec']:.4f} MB/s")
    print(f"   Samples:             {stats['samples']}")
    print(f"   ─────────────────────────────────────")
    print(f"   Total allocated:     ~{total_allocated_mb:.0f} MB (8×{ITERATIONS}×{ALLOC_SIZE//1024}KB)")
    print(f"   Allocation efficiency: {allocation_efficiency:.1f}x (peak / allocated)")
    print(f"   Fragmentation score:  {cooldown_delta:.2f} MB retained after cooldown")
    if not fragmentation_pass:
        print(f"   ❌ Fragmentation detected: {cooldown_delta:.2f} MB retained (>10 MB threshold)")
    else:
        print(f"   ✅ Memory reclaimed cleanly: {cooldown_delta:.2f} MB retained")
    print(f"{'='*50}\n")

    result = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "test_type": "MALLOC_arena_stress",
        "environment": {
            "MALLOC_ARENA_MAX": os.environ.get("MALLOC_ARENA_MAX"),
            "MALLOC_MMAP_THRESHOLD_": os.environ.get("MALLOC_MMAP_THRESHOLD_"),
        },
        "configuration": {
            "num_threads": NUM_THREADS,
            "duration_seconds": WORK_DURATION,
            "alloc_size_bytes": ALLOC_SIZE,
            "iterations_per_cycle": ITERATIONS,
        },
        "results": {
            **stats,
            "cooldown_rss_mb": round(cooldown_rss, 2),
            "cooldown_delta_mb": round(cooldown_delta, 2),
            "total_allocated_mb": round(total_allocated_mb, 0),
            "allocation_efficiency": round(allocation_efficiency, 1),
        },
        "verdict": verdict,
        "pass": fragmentation_pass,
    }

    # Append to log
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(result) + "\n")

    print(f"📝 Results logged to: {LOG_PATH}")
    return result


if __name__ == "__main__":
    result = run_stress_test()
    sys.exit(0 if result["pass"] else 1)
