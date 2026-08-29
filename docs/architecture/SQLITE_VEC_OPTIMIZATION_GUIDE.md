---
schema_version: "1.0"
document_type: "architecture"
document_id: "SQLITE_VEC_OPTIMIZATION_GUIDE-20260828"
title: "Omega Engine — SQLite-Vec Optimization Guide"
status: "ACTIVE"
date: "2026-08-28"
owner: "Researcher"
tags: ["sqlite-vec", "optimization", "vec0", "hnsw", "wal", "mrl"]
---

# 🔱 SQLite-Vec Optimization Guide

**AP Token**: `AP-SQLITEVEC-OPT-GUIDE-20260828-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ trc_sqlite_vec_opt ⬡ ACTIVE

## Current Performance Baseline (v3.0 Optimized)

| Metric | Value | Method |
|--------|-------|--------|
| Batch upsert throughput | 6,559 vec/sec | `batch_upsert()` single transaction |
| Query throughput | 121 q/sec | JOIN-based metadata fetch |
| Hybrid search latency | 9.6ms p50 | RRF fusion (FTS5 + vec0) |
| WAL checkpoint | Manual | `checkpoint_wal("RESTART")` |

## Architecture Overview

```
┌────────────────────────────────────────────────────────────┐
│                    SQLITE-VEC ADAPTER v3.0                 │
├────────────────────────────────────────────────────────────┤
│  Write Path (serialized)          Read Path (pooled)       │
│  ┌─────────────────────┐          ┌─────────────────────┐  │
│  │ _write_conn         │          │ _read_connections[] │  │
│  │ anyio.Lock          │          │ pool_size=4         │  │
│  │ BEGIN IMMEDIATE     │          │ Shared read access  │  │
│  └──────────┬──────────┘          └──────────┬──────────┘  │
│             │                                │             │
│             ▼                                ▼             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              omega_memory.db (WAL mode)             │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐  │   │
│  │  │omega_mem │ │omega_mem │ │omega_vec │ │omega_  │  │   │
│  │  │_data     │ │_fts (FTS5)│ │_gemma_768│ │memory_ │  │   │
│  │  │(metadata)│ │(BM25)    │ │(vec0)    │ │spatial │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ │(R-tree)│  │   │
│  │  ... 6 more vec0 collections ...         └────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

## Key Optimizations (Implemented)

### 1. Batch Upsert (Single Transaction)
```python
# Before: N transactions for N vectors
# After: 1 transaction, batch serialization, executemany
async def batch_upsert(self, items: List[Dict], collection: str) -> List[str]:
    async with self._write_lock:
        conn.execute("BEGIN IMMEDIATE")
        # 1. Insert metadata (executemany)
        # 2. Insert FTS5 (executemany)
        # 3. Insert vec0 (executemany)
        conn.commit()
```

### 2. JOIN-Based Query (Eliminates N+1)
```python
# Before: vec0 query → N metadata SELECTs
# After: Single JOIN query
SELECT v.rowid, v.distance, d.uuid, d.entity_name, d.content...
FROM omega_vec_gemma_768 v
JOIN omega_memory_data d ON v.rowid = d.id
WHERE v.embedding MATCH ? AND v.entity_name = ? AND k = ?
```

### 3. Batch Serialization (NumPy Vectorized)
```python
@staticmethod
def serialize_batch_float32(vectors: List[List[float]]) -> List[bytes]:
    import numpy as np
    arr = np.array(vectors, dtype=np.float32)
    return [row.tobytes() for row in arr]  # Vectorized, ~10x faster
```

### 4. Read Connection Pool
```python
# 4 concurrent read connections for parallel queries
self._read_pool_size = 4
# _get_read_conn() / _return_read_conn() manage pool
```

### 5. Configurable HNSW per Collection
```python
COLLECTIONS = {
    "omega_vec_gemma_768": {
        "hnsw": {"m": 16, "ef_construction": 200, "ef_search": 64},
    },
    # ... per-collection tuning
}
```

### 6. WAL Optimization
```python
# Smart checkpoint scheduling
async def start_periodic_checkpoint(self, interval_seconds: int = 300):
    # Background task: RESTART checkpoint every 5min
```

## Canonical Embedding Strategy (Hardcoded)

| Collection | Dimension | Quantization | HNSW | Use Case |
|------------|-----------|--------------|------|----------|
| `omega_vec_gemma_768` | 768 | int8_rescore | m=16, ef_c=200, ef_s=64 | Primary (Gemma 300M) |
| `omega_vec_nomic_768` | 768 | int8_rescore | m=16, ef_c=200, ef_s=64 | Fallback (Nomic v1.5) |
| `omega_vec_nomic_512` | 512 | int8_rescore | m=16, ef_c=200, ef_s=64 | MRL Tier 1 |
| `omega_vec_nomic_256` | 256 | int8_rescore | m=16, ef_c=200, ef_s=64 | MRL Tier 2 |
| `omega_vec_minilm_384` | 384 | none | m=16, ef_c=200, ef_s=64 | Speed (MiniLM) |
| `omega_vec_static_64` | 64 | none | m=16, ef_c=200, ef_s=64 | Zero-cost |
| `omega_vec_library_256` | 256 | none | m=16, ef_c=200, ef_s=64 | Feature-hash |

**MRL Pipeline**: 768 → 512 → 256 → 128 → 64 via truncation (first N dims preserve semantics)

## Known Gaps (See `R_RESEARCHER_SQLITE_VEC_GAPS_20260828.md`)

| Gap | Fix | Priority |
|-----|-----|----------|
| Missing 5/7 collection creation | Eager init in `_ensure_initialized()` | P0 |
| No MRL truncation pipeline | `truncate_mrl()` + batch upsert to MRL collections | P0 |
| INT8 rescore not implemented | int8 vec0 column + auxiliary float32 | P1 |
| Hardcoded RRF weights | Per-collection `COLLECTION_RRF_WEIGHTS` | P1 |
| No spatial R-tree | `omega_memory_spatial` R-tree table | P1 (VR) |
| O(N) delete cascade | `rowid → collection` mapping | P1 |
| WAL checkpoint not auto-started | `auto_checkpoint=True` in `__init__` | P1 |
| Metrics in-memory only | Persist to `data/metrics/sqlite_vec_metrics.json` | P2 |

## Tuning Guide

### PRAGMA Stack (Memory Profile)
```python
# From sqlite_policy.py "memory" profile
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = -32768;        # 32MB
PRAGMA wal_autocheckpoint = 500;   # Checkpoint every 500 pages
PRAGMA busy_timeout = 5000;        # 5s
PRAGMA temp_store = MEMORY;
PRAGMA mmap_size = 268435456;      # 256MB
```

### HNSW Parameters
| Parameter | Gemma 768 | Nomic 768 | MRL 512/256 | MiniLM 384 |
|-----------|-----------|-----------|-------------|------------|
| `m` | 16 | 16 | 16 | 16 |
| `ef_construction` | 200 | 200 | 200 | 200 |
| `ef_search` | 64 | 64 | 64 | 64 |

**Tuning**: Increase `ef_search` for higher recall (cost: latency). Increase `m` for better connectivity (cost: memory).

### Batch Size
```python
# Default: 100 vectors per batch
# Tune based on vector dimension:
# 768-dim: batch_size=100 (optimal)
# 384-dim: batch_size=200
# 64-dim: batch_size=500
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `SQLITE_BUSY` on upsert | Concurrent writers | Exponential backoff (50/100/200ms) implemented |
| WAL file > 50MB | Checkpoint starvation | `start_periodic_checkpoint(300)` + `checkpoint_wal("RESTART")` |
| Dimension mismatch error | Provider outputs wrong dim | Provider MUST output collection's declared dim (M23) |
| Slow queries (>50ms) | No HNSW / wrong ef_search | Verify vec0 table created with HNSW params |
| Hybrid search poor recall | RRF weights wrong | Use per-collection `COLLECTION_RRF_WEIGHTS` |

## Monitoring

```python
# Get real-time metrics
metrics = adapter.get_metrics()
# {
#   "upsert_count": 15000,
#   "batch_upsert_count": 150,
#   "avg_batch_upsert_latency_ms": 15.2,
#   "p99_batch_upsert_latency_ms": 45.0,
#   "query_count": 8500,
#   "avg_query_latency_ms": 8.9,
#   "p99_query_latency_ms": 22.1,
#   "wal_checkpoint_count": 12,
# }

# WAL health
health = await adapter.check_wal_health()
# {
#   "wal_size_mb": 12.3,
#   "checkpoint_busy": 0,
#   "healthy": true
# }
```

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ SQLITE-VEC-OPT-GUIDE ⬡ 2026-08-28*