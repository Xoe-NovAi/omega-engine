<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Documentation Hardening — Audit & Exact Edits
**AP Token**: `AP-DOC-HARDENING-20260828-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_doc_hardening ⬡ ACTIVE

**Date**: 2026-08-28
**Status**: ACTIVE — Ready for Implementation
**Scope**: 7 documents audited against current mandates (v3.8.0), sprint (PUBLIC-DEBUT-01), and architecture

---

## ⬡ Executive Summary (L1)

| Document | Status | Critical Issues | Edit Effort |
|----------|--------|-----------------|-------------|
| `OMEGA_ENGINE.md` | **STALE** | Mandates v3.5→3.8, 25→27 mandates, date 2026-07-07 | 30min |
| `AGENTS.md` | **CURRENT** | Missing spatial vectors agent role; 9 decisions need spatial/VR additions | 15min |
| `SOVEREIGN_MANDATES.md` | **CURRENT** | v3.8.0, 27 mandates, all present | — |
| `MANDATES_CONDENSED.md` | **CURRENT** | Synced with v3.8.0 | — |
| `DEBUT_REMEDIATION_MANUAL_20260817.md` | **PARTIAL** | Missing spatial/VR workstreams (ZS, HR, KD, GN, DS, LI) | 20min |
| `SPATIAL_VECTORS_ARCHITECTURE.md` | **MISSING** | New document required | 1h |
| `SQLITE_VEC_OPTIMIZATION_GUIDE.md` | **MISSING** | New document required | 1h |

---

## 📋 Document-by-Document Audit (L2)

### 1. `OMEGA_ENGINE.md` — **STALE (Critical)**

**File**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/OMEGA_ENGINE.md`  
**Current State**: References 25 mandates, v3.5, date 2026-07-07  
**Required State**: 27 mandates, v3.8.0, date 2026-08-28

**Exact Edits**:

```markdown
# Line 1-5 (Header)
---
schema_version: "1.0"
document_type: "reference"
document_id: "OMEGA_ENGINE-REF-v3.8.0"
title: "Omega Engine — Reference Architecture"
status: "ACTIVE"
date: "2026-08-28"          # CHANGED: was 2026-07-07
version: "3.8.0"            # CHANGED: was 3.5.0
---

# Line 12 (Mandate count)
**27 Sovereign Mandates** (v3.8.0) — CHANGED: was "25 Sovereign Mandates (v3.5)"

# Line 45 (Mandate list) — ADD M26, M27
| M26 | Doc Standards | Reference docs pass `make doc-llm-validate` |
| M27 | Tracking Integrity | Execution state follows 5-Tier Tracking Architecture |

# Line 89 (Sprint reference)
**Current Sprint**: PUBLIC-DEBUT-01 (SSOT: `DEBUT_REMEDIATION_MANUAL_20260817.md`)
# CHANGED: was "DEBUT-01 (SSOT: ARK §4)"

# Line 156 (Architecture rules reference)
The 4 Architecture Rules (`.opencode/rules/`) — ADD: "See `MANDATES_CONDENSED.md` for Tier-0 injection"
```

---

### 2. `AGENTS.md` — **CURRENT (Minor Additions)**

**File**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/AGENTS.md`  
**Current State**: v1.0.0, date 2026-08-27, 9 decisions  
**Required Additions**: Spatial vectors agent role, 2 new decisions (D-578..D-584 from DEBUT_REMEDIATION §9)

**Exact Edits**:

```markdown
# Line 7 (Date)
date: "2026-08-28"          # CHANGED: was 2026-08-27

# Line 56-69 (9 Decisions) — ADD D-578..D-584
| **D-578** | GEMINI-NOTEBOOK workstream (GN) — free-tier research pipeline |
| **D-579** | DOCUMENTATION-SYSTEM workstream (DS) — modular domain docs |
| **D-580** | LOCAL-INFERENCE-OPT workstream (LI) — sequential loading, adaptive context |
| **D-581** | KNOWLEDGE-DOMAINS workstream (KD) — runtime modules + curator model |
| **D-582** | HEADROOM-INTEGRATION workstream (HR) — semantic compression for tools/RAG |
| **D-583** | ZSWAP-SUBSYSTEM workstream (ZS) — 16GB NVMe swap, zswap enabled |
| **D-584** | Post-debut execution order: GN → DS → LI → KD → HR → ZS |

# Line 113 (Architecture rules summary) — ADD 5th rule
5. **Spatial** — R-tree + vec0 dual-index for VR navigation (Option B)
```

---

### 3. `DEBUT_REMEDIATION_MANUAL_20260817.md` — **PARTIAL (Missing Workstreams)**

**File**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md`  
**Current State**: §9 lists 6 workstreams (GN, DS, LI, KD, HR, ZS) but §5 ticket sequence only covers P0-1 through DEL-1/DOC-1  
**Required**: Mark spatial/VR items as post-debut workstreams with dependencies

**Exact Edits**:

```markdown
# Line 436-455 (§9 Post-Debut Phase) — ADD spatial/VR dependencies

**Dependencies**: DEL-1 Week 2 (router collapse) → QDRANT-MIGRATION (H2) → COGNITIVE-ARCH (H3) → VAULT-SPRINT → P2/P3/P4
# ADD:
**Spatial/VR Dependencies**: DEL-1 Week 2 → GAP-005 (R-tree) → SPATIAL-BAKE (Sprint 1) → HYBRID-SPATIAL (Sprint 2) → GODOT-BRIDGE (Sprint 3) → SOUL-ANCHOR (Sprint 4)

# Line 438-445 (Workstream table) — ADD Spatial/VR row
| **SPATIAL-VECTORS** | SV | researcher | R-tree + vec0 dual-index, Force-Directed bake, Godot bridge, VR navigation | Depends: DEL-1 Week 2, GAP-005 |

# Line 447-453 (Execution Order) — ADD Spatial/VR phase
**Execution Order** (after PUB-1 allowlist + INST-1 + DEL-1 Week 1):
1. **GN-1..GN-5**: Deploy notebooklm-py[mcp]...
...
6. **ZS-1..ZS-3**: zswap sysctl + kernel cmdline...
7. **SV-1..SV-4**: R-tree schema → SpatialBakeService → HybridSpatialQuery → GodotBridge (Post-debut, Horizon 1)
```

---

### 4. `docs/architecture/SPATIAL_VECTORS_ARCHITECTURE.md` — **NEW (Create)**

**File**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/architecture/SPATIAL_VECTORS_ARCHITECTURE.md`  
**Source**: `R_RESEARCHER_SPATIAL_VECTORS_VR_20260828.md` (this research)  
**Status**: Create as permanent architecture document

**Content Template**:
```markdown
---
schema_version: "1.0"
document_type: "architecture"
document_id: "SPATIAL_VECTORS_ARCHITECTURE-20260828"
title: "Omega Engine — Spatial Vectors Architecture (R-tree + vec0 Dual-Index)"
status: "ACTIVE"
date: "2026-08-28"
owner: "Researcher"
tags: ["spatial", "vr", "r-tree", "sqlite-vec", "dual-index"]
---

# 🔱 Spatial Vectors Architecture

**AP Token**: `AP-SPATIAL-ARCH-20260828-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ trc_spatial_arch ⬡ ACTIVE

## Decision Record: Option B — Separate R-tree Table Joined on rowid

### Context
- sqlite-vec provides `vec0` for high-dim semantic similarity (768-dim)
- VR navigation requires 3D spatial range queries ("within 5m of x,y,z")
- BSP sector culling requires bounding-box spatial index
- sqlite-vec does NOT support spatial/R-tree natively

### Decision
Use **SQLite native R-tree virtual table** (`omega_memory_spatial`) for 3D coordinates, joined on `rowid` with `omega_memory_data`. Keep `vec0` collections pure for semantic embeddings.

### Consequences
- ✅ Zero new dependencies (R-tree built into SQLite)
- ✅ 3D support (6D R-tree: minX,maxX,minY,maxY,minZ,maxZ)
- ✅ O(log N) spatial range queries for VR
- ✅ Clean separation: semantic (vec0) vs spatial (R-tree)
- ⚠️ Two indexes to maintain (vec0 + R-tree) on upsert/delete
- ⚠️ Hybrid queries require application-level fusion

## Schema

```sql
-- Semantic embeddings (7 collections, vec0)
CREATE VIRTUAL TABLE omega_vec_gemma_768 USING vec0(embedding float[768], entity_name TEXT partition key);
-- ... 6 more vec0 collections ...

-- Full-text search (FTS5)
CREATE VIRTUAL TABLE omega_memory_fts USING fts5(content, entity_name, session_id, role, timestamp);

-- Metadata (SQL)
CREATE TABLE omega_memory_data (id INTEGER PRIMARY KEY, uuid TEXT, entity_name TEXT, ...);

-- Spatial coordinates (R-tree) — NEW
CREATE VIRTUAL TABLE omega_memory_spatial USING rtree(id, minX, maxX, minY, maxY, minZ, maxZ);
```

## Query Patterns

### Spatial Range Query (VR Primitive)
```sql
SELECT s.id, d.uuid, d.content
FROM omega_memory_spatial s
JOIN omega_memory_data d ON s.id = d.id
WHERE s.minX <= ? AND s.maxX >= ?
  AND s.minY <= ? AND s.maxY >= ?
  AND s.minZ <= ? AND s.maxZ >= ?
  AND d.entity_name = ?
LIMIT ?;
```

### Hybrid Semantic + Spatial
1. R-tree range query → candidate rowids
2. vec0 KNN with `rowid IN (...)` filter
3. Fuse: `α * semantic_score + β * spatial_score`

### BSP Sector Streaming (Godot)
- Sector = R-tree bounding box
- `current_sector + neighbors` streamed to Godot
- LOD: Near=high-poly, Far=billboard, Culled=queue_free

## Integration with 7 Collections

All 7 `omega_vec_*` collections share the **same** `omega_memory_spatial` R-tree via `rowid` join. Spatial coordinates computed once by `ForceDirectedSpatialResolver`, stored once, joined everywhere.

## Migration Path

1. **Phase 1**: Add R-tree table + `spatial_coords` in `batch_upsert` (GAP-005)
2. **Phase 2**: `SpatialBakeService` — background Force-Directed recompute
3. **Phase 3**: `hybrid_spatial_query()` + Godot `SpatialStreamer`
4. **Phase 4**: `spatial_anchor` in `soul.yaml`, Heritage Vet, Temple-Grade

## Mandate Compliance

| Mandate | Compliance |
|---------|------------|
| M1 AnyIO | All ops in `anyio.to_thread.run_sync` |
| M2 Firewall | Core in `src/omega/memory/`, VR in `config/wads/_omega_default/vr/` |
| M7 Local-First | Force-Directed runs locally (NumPy) |
| M8 Zero Telemetry | No spatial analytics exported |
| M11 Soul Integrity | `spatial_anchor: Point3D` in `soul.yaml` |
| M14 Heritage | `[id-soft: doom-1993] BSP Culling` on spatial modules |
| M23 Failure Integrity | R-tree is SQLite built-in |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ SPATIAL-VECTORS-ARCH ⬡ 2026-08-28*
```

---

### 5. `docs/architecture/SQLITE_VEC_OPTIMIZATION_GUIDE.md` — **NEW (Create)**

**File**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/architecture/SQLITE_VEC_OPTIMIZATION_GUIDE.md`  
**Source**: `sqlite_vec_adapter_optimized.py` + `R_RESEARCHER_SQLITE_VEC_GAPS_20260828.md`  
**Status**: Create as permanent architecture document

**Content Template**:
```markdown
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
```

---

### 6. `docs/specs/debut_remediation/DEBUT_REMEDIATION_MANUAL_20260817.md` — **SYNC**

**File**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/specs/debut_remediation/DEBUT_REMEDIATION_MANUAL_20260817.md`  
**Note**: This appears to be a duplicate/symlink of the main DEBUT_REMEDIATION_MANUAL. Apply same edits as Document 3.

---

## 📋 Implementation Checklist

| Task | File | Status |
|------|------|--------|
| Update mandate count to 27, version to 3.8.0, date to 2026-08-28 | `OMEGA_ENGINE.md` | ☐ |
| Add M26, M27 to mandate table | `OMEGA_ENGINE.md` | ☐ |
| Update sprint reference to DEBUT_REMEDIATION_MANUAL | `OMEGA_ENGINE.md` | ☐ |
| Update date to 2026-08-28 | `AGENTS.md` | ☐ |
| Add D-578 through D-584 to decisions table | `AGENTS.md` | ☐ |
| Add 5th architecture rule (Spatial) | `AGENTS.md` | ☐ |
| Add Spatial/VR workstream + dependencies | `DEBUT_REMEDIATION_MANUAL_20260817.md` | ☐ |
| Add SV execution order phase | `DEBUT_REMEDIATION_MANUAL_20260817.md` | ☐ |
| Create `SPATIAL_VECTORS_ARCHITECTURE.md` | `docs/architecture/` | ☐ |
| Create `SQLITE_VEC_OPTIMIZATION_GUIDE.md` | `docs/architecture/` | ☐ |
| Sync duplicate in `docs/specs/debut_remediation/` | `docs/specs/debut_remediation/` | ☐ |

---

## 🧪 Validation Commands

```bash
# Verify mandate count
grep -c "^### [0-9]\+" SOVEREIGN_MANDATES.md  # Should be 27

# Verify OMEGA_ENGINE.md mandate count
grep "Sovereign Mandates" OMEGA_ENGINE.md    # Should say "27"

# Verify AGENTS.md decisions
grep "D-57[89]\|D-58[0-4]" AGENTS.md         # Should show 7 new decisions

# Verify new architecture docs exist
ls -la docs/architecture/SPATIAL_VECTORS_ARCHITECTURE.md
ls -la docs/architecture/SQLITE_VEC_OPTIMIZATION_GUIDE.md

# Run doc validation
make doc-llm-validate
```

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ DOC-HARDENING ⬡ 2026-08-28*
<!-- PROVENANCE-CORRECTED 2026-08-30T03:06:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

