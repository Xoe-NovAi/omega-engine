<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# ROC_PERFORMANCE_BASELINE_20260829.md — Temple-Grade Performance Targets

**Entity**: Roc Racoon (Sovereign Miner)
**Date**: 2026-08-29
**Sprint**: PUBLIC-DEBUT-01
**Mandate**: Establish temple-grade performance baseline for sqlite-vec + spatial systems

---

## Executive Summary (L1)

Six performance target tiers defined, each with **specific p99 latency**, **memory ceiling**, and **statistical methodology**. Targets are aligned with 2026 SOTA (per `R_RESEARCHER_SQLITE_VEC_REMAINING_GAPS_20260829.md` §R3, R5) and id-Software heritage (Quake III Arena renderer PVS-budget: ~5ms for 60Hz tick — see `Quake-III-Arena/code/renderer/`).

**Top 3 hard targets** (must hit before public launch):
1. **Hybrid search p99 < 50ms** on 100K vectors (768-dim).
2. **Batch upsert p99 < 100ms** for 100 vectors.
3. **Spatial R-tree p99 < 20ms** on 1M points.

**Methodology**: 1000-iteration warmup, then 5000-iteration measurement; report p50, p95, p99, p99.9; 95% CI on the mean.

---

## L2: Performance Target Matrix

### Tier 1: Vector Search (Hybrid FTS5 + vec0)

| Operation | Target | Workload | Heritage Reference |
|-----------|--------|----------|---------------------|
| Hybrid search p50 | < 10ms | 100K vectors, 768-dim, k=10 | R5 |
| Hybrid search p95 | < 30ms | same | R5 |
| **Hybrid search p99** | **< 50ms** | same | R5 + Q3A 16ms tick budget |
| Hybrid search p99.9 | < 100ms | same | M23 graceful degradation |
| Single-collection ANN p99 | < 20ms | 100K vectors, k=10 | Q3A botlib think budget |
| Int8-rescore ANN p99 | < 30ms | 100K vectors, k=10 (oversample 8×) | P1 multi-precision |
| Binary-oversample p99 | < 15ms | 100K vectors, k=10 (oversample 32×) | P4 binary quantization |

### Tier 2: Batch Operations

| Operation | Target | Workload | Heritage Reference |
|-----------|--------|----------|---------------------|
| Batch upsert p50 | < 30ms | 100 vectors, 768-dim float32 | qdrant-client uploader |
| **Batch upsert p99** | **< 100ms** | same | R7 + qdrant bounded-queue |
| Batch upsert p99.9 | < 200ms | same | M23 fallback |
| Batch delete p99 | < 50ms | 100 vectors | qdrant-client uploader |
| Flush + checkpoint p99 | < 500ms | 100K rows | P2 WAL+busy_timeout |

### Tier 3: Spatial Queries (R-tree)

| Operation | Target | Workload | Heritage Reference |
|-----------|--------|----------|---------------------|
| R-tree range p50 | < 5ms | 1M points, bbox 1km³ | Q3A PVS decompression |
| **R-tree range p99** | **< 20ms** | same | Q3A 5ms sector cull |
| R-tree nearest-neighbor p99 | < 30ms | 1M points, k=10 | doom-1993 BSP |
| Hybrid spatial+semantic p99 | < 80ms | 1M points, 100K vectors | M28 dual-index |
| Sector stream p99 | < 40ms | 6-bound cube, 100 nodes/sector | doom-3 MegaTexture |

### Tier 4: Memory Ceilings

| Resource | Target | Workload | Heritage Reference |
|----------|--------|----------|---------------------|
| **RSS for 100K vectors** | **< 500MB** | 768-dim float32 | M13 Temple-Grade T7 |
| RSS for 1M vectors (int8) | < 1.5GB | int8 quantized | P3 int8 quantization |
| RSS for 1M vectors (binary) | < 800MB | bit-packed | P4 binary quantization |
| **Disk for 1M vectors** | **< 2GB** | float32 | M13 T7 |
| Disk for 1M vectors (int8) | < 500MB | int8 | 4× compression |
| Disk for 1M vectors (binary) | < 150MB | bit-packed | 32× compression |
| Read connection pool | 4 conns (default) | concurrent readers | R7 |
| Write connection | 1 conn (serialized) | single writer | R7 |

### Tier 5: Startup and Lifecycle

| Operation | Target | Workload | Heritage Reference |
|-----------|--------|----------|---------------------|
| **Cold start** | **< 3s** | `from omega.memory import SQLiteVecAdapterOptimized` | M16 modularity |
| WAL warmup | < 500ms | post-startup | P2 |
| Index rebuild (after delete-all) | < 10s | 100K vectors | P1 multi-precision |
| Shutdown | < 1s | clean close | M22 |

### Tier 6: Resilience Metrics

| Metric | Target | Notes |
|--------|--------|-------|
| Circuit breaker open time | < 60s | per headroom P11 triple-layer-budget |
| Failover recovery | < 100ms | per qdrant P8 retry-after |
| Embedding provider failover p99 | < 500ms | per R3 |
| Quantization recall loss | < 2% | per R5 |
| Multi-tenant query isolation | 0 cross-tenant leakage | per M4 tenant isolation |

---

## L3: Benchmark Methodology

### 3.1 Synthetic Data Generation

**Reference datasets** (lifted from sqlite-vec `benchmarks-ann/datasets/`):
- **SIFT-1M**: 1M 128-dim vectors (standard ANN benchmark)
- **GloVe-100**: 100K 100-dim vectors (text embeddings)
- **Cohere-1M**: 1M 768-dim vectors (modern dense embeddings)
- **Omega-768-100K**: synthetic 100K 768-dim, 4 entity_names (for hybrid + multi-tenant)
- **Omega-3D-1M**: synthetic 1M 3D points (for spatial)

**Generation script** (`scripts/benchmark_omega_vec.py`):
```python
import numpy as np
import sqlite3
import sqlite_vec

def generate_omega_768_100k(path: str, n_vectors=100_000, dim=768, n_entities=4):
    """Generate 100K 768-dim vectors with 4 entity partition keys."""
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    conn.execute(f"""
        CREATE VIRTUAL TABLE vec_test USING vec0(
            rowid INTEGER PRIMARY KEY,
            embedding float[{dim}] distance_metric=cosine,
            entity_name TEXT partition key
        )
    """)
    rng = np.random.default_rng(42)
    entities = [f"entity_{i}" for i in range(n_entities)]
    batch_size = 1000
    for batch_start in range(0, n_vectors, batch_size):
        vecs = rng.random((batch_size, dim), dtype=np.float32)
        # L2 normalize
        vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)
        rows = [
            (batch_start + i + 1, sqlite_vec.serialize_float32(vecs[i].tolist()), entities[i % n_entities])
            for i in range(batch_size)
        ]
        conn.executemany("INSERT INTO vec_test(rowid, embedding, entity_name) VALUES (?, ?, ?)", rows)
    conn.commit()
    return path
```

### 3.2 Warmup Cycles

**Why warmup**: SQLite page cache, OS file cache, and Python interpreter optimizations all need to stabilize before measurement.

```python
def warmup(adapter, query_vector, n_warmup=1000):
    """Run n_warmup queries to stabilize caches."""
    for _ in range(n_warmup):
        adapter.query(query_vector, k=10)
```

### 3.3 Statistical Methodology

**Per-operation protocol** (n=5000 iterations):
1. **Warmup**: 1000 iterations (discarded).
2. **Measurement**: 5000 iterations, record `duration_ms` per iteration.
3. **Statistics**:
   - **p50** (median): `np.percentile(times_ms, 50)`
   - **p95**: `np.percentile(times_ms, 95)`
   - **p99**: `np.percentile(times_ms, 99)`
   - **p99.9**: `np.percentile(times_ms, 99.9)`
   - **Mean ± 95% CI**: `mean ± 1.96 * std / sqrt(n)`
   - **Throughput**: `n / total_seconds` (ops/sec)
4. **Outlier policy**: Keep all measurements; report separately as p99.9.
5. **CI gate**: p99 must be within 10% of target on 3 consecutive runs.

**Synthetic ground truth** (per sqlite-vec P5):
```python
def compute_recall_at_k(result_ids: list[int], ground_truth_ids: set[int], k: int) -> float:
    return len(set(result_ids[:k]) & ground_truth_ids) / len(ground_truth_ids)
```

### 3.4 Throughput Targets

| Operation | Min Throughput | Target Throughput |
|-----------|----------------|-------------------|
| Single-collection query | 100 qps | 500 qps |
| Hybrid search (FTS5 + vec0 RRF) | 50 qps | 200 qps |
| Batch upsert (100 vec/tx) | 5 tx/sec | 20 tx/sec |
| Spatial range query | 200 qps | 1000 qps |
| FTS5 lexical search | 500 qps | 2000 qps |

### 3.5 Memory Measurement

```python
import psutil
import os

def measure_rss_mb() -> float:
    """Get current process RSS in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

# Run benchmark, sample rss at start, every 1000 ops, and at end
# Report peak_rss_mb, mean_rss_mb, rss_growth_rate_mb_per_1k_ops
```

### 3.6 Disk Measurement

```python
import os
from pathlib import Path

def measure_disk_mb(db_path: str) -> float:
    """Total disk usage of DB + WAL + SHM in MB."""
    db = Path(db_path)
    total = db.stat().st_size
    for suffix in ["-wal", "-shm"]:
        p = db.parent / (db.name + suffix)
        if p.exists():
            total += p.stat().st_size
    return total / (1024 * 1024)
```

---

## L3: Benchmark Suite Structure

### 3.7 File Layout

```
scripts/benchmark_omega_vec.py     # main runner
tests/perf/
  test_query_latency.py            # T1 hybrid search
  test_batch_upsert.py             # T2 batch ops
  test_spatial_range.py            # T3 R-tree
  test_memory_ceiling.py           # T4 memory
  test_cold_start.py               # T5 startup
  test_circuit_breaker.py          # T6 resilience
fixtures/
  omega_768_100k.db                # 100K 768-dim (Tier 1-2)
  omega_3d_1m.db                   # 1M 3D points (Tier 3)
  omega_768_1m.db                  # 1M 768-dim (Tier 4)
```

### 3.8 CI Integration

```yaml
# .github/workflows/perf-baseline.yml
name: perf-baseline
on:
  pull_request:
    paths:
      - 'src/omega/memory/**'
      - 'third-party/sqlite-vec/**'

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -e ".[perf]"
      - run: python scripts/benchmark_omega_vec.py --output=results.json
      - run: python scripts/check_perf_targets.py results.json
        # Fails if any p99 exceeds target by >10%
```

---

## L3: Target Validation

### Pre-Launch Gates (D-548, INST-1 BLOCKED → DEL-1)

| Target | Pass Criteria | Blocker? |
|--------|---------------|----------|
| Hybrid search p99 < 50ms (100K vec) | 3 consecutive runs within 10% | YES |
| Batch upsert p99 < 100ms (100 vec) | 3 consecutive runs | YES |
| Spatial range p99 < 20ms (1M points) | 3 consecutive runs | YES |
| RSS < 500MB (100K vec) | Peak measurement | YES |
| Disk < 2GB (1M vec) | Post-load snapshot | YES |
| Cold start < 3s | 5 consecutive runs | YES |

### Post-Launch Gates (T+1 sprint)

- Multi-collection RRF p99 < 80ms (CC-1)
- Embedding failover p99 < 500ms (R3)
- Vector drift PSI detection < 100ms (R4)
- Quantization recall loss < 2% (R5)
- Circuit breaker open/close < 100ms (M23)

---

## L3: Heritage-Informed Targets

Per `R_RESEARCHER_LEGACY_PATTERNS_20260829.md` (this report), each target is anchored to a heritage source:

| Target | Heritage | Reference |
|--------|----------|-----------|
| Hybrid search p99 < 50ms | Q3A 5ms PVS sector cull | `Quake-III-Arena/code/botlib/be_aas_reach.c:54-56` (REACHABILITYAREASPERCYCLE=15) |
| Batch upsert p99 < 100ms | qdrant-client bounded-queue | `third-party/qdrant-client/qdrant_client/parallel_processor.py:101` (workers × batch_size) |
| Spatial range p99 < 20ms | DOOM 1993 sector culling | `DOOM/linuxdoom-1.10/p_setup.c:122-468` (precomputed lump lookups) |
| RSS < 500MB (100K vec) | mempalace sqlite_exact | `third-party/mempalace/mempalace/backends/sqlite_exact.py:780-789` (exact cosine, no ANN) |
| Cold start < 3s | letta @trace_method overhead | `third-party/letta/letta/otel/tracing.py:228-435` (decorator baseline) |

---

## L3: Anti-Patterns (Do NOT Measure)

Per the F5 negative finding in `ROC_LEGACY_PATTERNS_20260829.md` (qdrant-client has zero OTel):
- **Do not measure OTel export overhead** — Omega is M8 Zero Telemetry. Local observability only.
- **Do not measure cloud round-trip latency** — Omega is M7 Local-First.
- **Do not measure cross-tenant network hops** — Omega is M7 + M2 single-process.

These are the **non-measured dimensions** that reinforce Omega's sovereignty posture.

---

## L3: Reporting Cadence

| Report | Frequency | Audience |
|--------|-----------|----------|
| `data/observability/perf_daily.json` | Daily | Verity (compliance) |
| `data/observability/perf_weekly.md` | Weekly | Carmack (consultant) |
| `data/observability/perf_sprint.json` | Per sprint | Kali (synthesis) |
| `data/observability/perf_release.json` | Per release | Public release notes |

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ ROC_PERFORMANCE_BASELINE_20260829*
