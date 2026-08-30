# 🔱 SQLite-Vec Implementation Gaps — Audit & Fix Spec
**AP Token**: `AP-SQLITEVEC-GAPS-20260828-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_sqlite_vec_gaps ⬡ ACTIVE

**Date**: 2026-08-28
**Status**: ACTIVE — Ready for Implementation
**Source**: Audit of `src/omega/memory/sqlite_vec_adapter_optimized.py` (v3.0) + `sqlite_vec_adapter.py` (v2.0) + `INGESTION_PIPELINE_SPEC.md`

---

## ⬡ Executive Summary (L1)

The optimized sqlite-vec adapter (`sqlite_vec_adapter_optimized.py`) delivers **6,559 batch vec/sec, 121 q/sec, 9.6ms hybrid search** — but **9 critical gaps** remain that violate M23 (Failure Integrity), M11 (Soul Integrity), and the Ingestion Pipeline Spec. These gaps block alpha launch and VR preparation.

| Gap | Severity | Mandate Violation | Effort |
|-----|----------|-------------------|--------|
| Missing 5/7 collection creation | **P0** | M23, Ingestion Spec §5 | 2h |
| No MRL truncation pipeline | **P0** | M23, Ingestion Spec §5 | 4h |
| INT8 rescore never implemented | **P1** | COLLECTIONS declaration | 3h |
| Hardcoded RRF weights (0.5/0.5) | **P1** | Ingestion Spec §5 | 1h |
| No spatial index (R-tree) | **P1** | VR prep, SSM Spec | 6h |
| O(N) delete across all collections | **P1** | Performance | 2h |
| WAL checkpoint never started | **P1** | M23, Reliability | 1h |
| Metrics in-memory only | **P2** | Observability | 1h |
| No INT8 quantization code path | **P1** | COLLECTIONS declaration | 3h |

---

## 🔍 Detailed Gap Audit (L2)

### GAP-001: Missing Collection Creation (5/7 Collections Never Created)

**File**: `src/omega/memory/sqlite_vec_adapter_optimized.py:266-307`  
**Root Cause**: `_ensure_collection_vec_table()` is only called lazily on first `upsert()`/`batch_upsert()`/`query()` for a specific collection. The ingestion pipeline (§5 Collection Mapping) expects all 7 collections to exist, but only `omega_vec_gemma_768` and `omega_vec_nomic_768` are ever created because:
- Default `collection` param = `"omega_vec_gemma_768"`
- No code path calls `_ensure_collection_vec_table()` for MRL/fallback collections
- `get_status()` only reports `collections_created` from `_vec_tables_created` dict (empty for unused collections)

**Affected Collections** (never created):
- `omega_vec_nomic_512` (MRL 512-dim)
- `omega_vec_nomic_256` (MRL 256-dim)
- `omega_vec_minilm_384` (Speed tier)
- `omega_vec_static_64` (Zero-cost tier)
- `omega_vec_library_256` (Library feature-hashing)

**Fix Spec**:
```python
# File: src/omega/memory/sqlite_vec_adapter_optimized.py
# Add after line 161 (after _checkpoint_task = None)

async def _ensure_all_collections(self) -> None:
    """Eagerly create all declared vec0 collections at initialization.
    
    Called from _ensure_initialized() to guarantee all 7 collections exist
    before any ingestion occurs. Required by Ingestion Pipeline Spec §5.
    """
    for collection_name, config in self._collections.items():
        if not self._vec_tables_created.get(collection_name, False):
            # Use a dummy vector of correct dimension to trigger creation
            dummy_vector = [0.0] * config["dimension"]
            await self._ensure_collection_vec_table(collection_name, len(dummy_vector))

# In _ensure_initialized() (line 207), after conn.commit() at line 249:
await self._ensure_all_collections()
```

**Verification**: `get_status()["collections_created"]` must return all 7 collection names.

---

### GAP-002: No MRL Truncation Pipeline (768→512→256→128→64)

**File**: `src/omega/memory/sqlite_vec_adapter_optimized.py:49-50` (MRL_DIMENSIONS declared but unused)  
**Root Cause**: `MRL_DIMENSIONS = [768, 512, 256, 128, 64]` is declared as a constant but **no code path** truncates embeddings. The Ingestion Pipeline Spec §5 maps sources to MRL fallback collections (`omega_vec_nomic_512`, `omega_vec_nomic_256`), but:
- Embedding providers (Gemma, Nomic) always output 768-dim
- No truncation logic in `batch_upsert()`, `upsert()`, or provider layer
- Collections for 512/256/128/64 exist in COLLECTIONS but receive zero vectors

**Fix Spec**:
```python
# File: src/omega/memory/sqlite_vec_adapter_optimized.py
# Add after line 95 (after DEFAULT_EMBEDDING_DIM)

@staticmethod
def truncate_mrl(vector: List[float], target_dim: int) -> List[float]:
    """Truncate vector to target dimension using Matryoshka Representation Learning.
    
    MRL property: First N dimensions preserve most semantic information.
    Valid target_dims: 512, 256, 128, 64 (must be in MRL_DIMENSIONS).
    """
    if target_dim not in MRL_DIMENSIONS:
        raise ValueError(f"Invalid MRL target dimension: {target_dim}. Valid: {MRL_DIMENSIONS}")
    if target_dim >= len(vector):
        return vector[:target_dim]  # No-op or pad if needed
    return vector[:target_dim]

@staticmethod
def generate_mrl_variants(vector: List[float]) -> Dict[int, List[float]]:
    """Generate all MRL variants from a 768-dim canonical vector.
    
    Returns: {512: [...], 256: [...], 128: [...], 64: [...]}
    """
    if len(vector) != CANONICAL_DIMENSION:
        raise ValueError(f"Input must be {CANONICAL_DIMENSION}-dim, got {len(vector)}")
    return {
        dim: SQLiteVecAdapterOptimized.truncate_mrl(vector, dim)
        for dim in MRL_DIMENSIONS
        if dim < CANONICAL_DIMENSION
    }

# In batch_upsert() (line 341), after validating first_vec dimension (line 368):
# Generate MRL variants for fallback collections
mrl_variants = self.generate_mrl_variants(first_vec) if len(first_vec) == CANONICAL_DIMENSION else {}

# Then upsert to each MRL collection (after primary collection upsert at line 444):
for mrl_dim, mrl_vector in mrl_variants.items():
    mrl_collection = f"omega_vec_nomic_{mrl_dim}"
    if mrl_collection in self._collections:
        # Reuse same rowids, metadata; only vector changes
        mrl_embeddings = self.serialize_batch_float32([mrl_vector] * len(items))
        mrl_vec_data = [(rowids[i], mrl_embeddings[i], entity_names[i]) for i in range(len(items))]
        conn.executemany(
            f"INSERT INTO {mrl_collection}(rowid, embedding, entity_name) VALUES (?, ?, ?)",
            mrl_vec_data,
        )
```

**Verification**: Ingest a 768-dim vector → verify rows exist in `omega_vec_nomic_512`, `omega_vec_nomic_256`, `omega_vec_static_64`.

---

### GAP-003: INT8 Rescore Quantization Declared But Never Implemented

**File**: `src/omega/memory/sqlite_vec_adapter_optimized.py:53, 59, 65, 71` (COLLECTIONS declares `"quantization": "int8_rescore"`)  
**Root Cause**: The COLLECTIONS dict declares `"quantization": "int8_rescore"` for 768-dim and 512/256 collections, but:
- `CREATE VIRTUAL TABLE` at line 296-302 uses `float[dim]` — no quantization
- No `sqlite-vec` quantization API usage (requires v0.1.10-alpha+ rescore extension)
- No int8 vector storage or rescore logic in query path

**sqlite-vec Rescore Status** (per PIVOT_LOG D224): v0.1.10-alpha ships rescore/DiskANN/IVF ANN indexes. Binary quantization guide exists at `alexgarcia.xyz/sqlite-vec/guides/binary-quant.html`.

**Fix Spec**:
```python
# File: src/omega/memory/sqlite_vec_adapter_optimized.py
# Add after line 336 (after serialize_float32)

@staticmethod
def quantize_int8(vector: List[float]) -> bytes:
    """Quantize float32 vector to int8 for rescore index.
    
    Uses symmetric quantization: scale = 127 / max(abs(vector))
    Returns int8 bytes + scale factor for dequantization.
    """
    import numpy as np
    arr = np.array(vector, dtype=np.float32)
    max_abs = np.max(np.abs(arr))
    if max_abs == 0:
        return np.zeros(len(vector), dtype=np.int8).tobytes(), 1.0
    scale = 127.0 / max_abs
    quantized = np.round(arr * scale).astype(np.int8)
    return quantized.tobytes(), float(scale)

@staticmethod
def dequantize_int8(quantized_bytes: bytes, scale: float, dim: int) -> List[float]:
    """Dequantize int8 back to float32 for exact rescore."""
    import numpy as np
    quantized = np.frombuffer(quantized_bytes, dtype=np.int8, count=dim)
    return (quantized.astype(np.float32) / scale).tolist()

# In _ensure_collection_vec_table() (line 266), modify CREATE TABLE for quantized collections:
def _sync_create_vec():
    conn = self._get_write_conn()
    coll_config = self._collections[collection_name]
    declared_dim = coll_config["dimension"]
    quantization = coll_config.get("quantization", "none")
    
    if quantization == "int8_rescore":
        # Use int8 vector column + auxiliary float column for rescore
        # Note: sqlite-vec v0.1.10+ supports int8 vectors with rescore
        conn.execute(f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS {table_name}
            USING vec0(
                embedding int8[{declared_dim}] distance_metric=cosine,
                embedding_fp32 float[{declared_dim}] auxiliary,
                entity_name TEXT partition key
            )
        """)
    else:
        conn.execute(f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS {table_name}
            USING vec0(
                embedding float[{declared_dim}] distance_metric=cosine,
                entity_name TEXT partition key
            )
        """)
    conn.commit()

# In batch_upsert() (line 341), serialize both float32 and int8 for quantized collections:
quantization = self._collections[collection].get("quantization", "none")
if quantization == "int8_rescore":
    int8_embeddings = []
    scales = []
    for v in vectors:
        q_bytes, scale = self.quantize_int8(v)
        int8_embeddings.append(q_bytes)
        scales.append(scale)
    # Store scale in metadata_json or auxiliary column
```

**Verification**: Query `omega_vec_gemma_768` → verify int8 vectors stored, rescore produces identical ranking to float32.

---

### GAP-004: Hardcoded Hybrid Search RRF Weights (0.5/0.5)

**File**: `src/omega/memory/sqlite_vec_adapter_optimized.py:708-778` (`hybrid_search` method)  
**Root Cause**: `fts_weight: float = 0.5, vec_weight: float = 0.5` hardcoded as defaults. Ingestion Pipeline Spec §5 maps different source types to different collections, but weights are not configurable per collection. Code collections (MiniLM 384) need different weighting than semantic collections (Gemma 768).

**Fix Spec**:
```python
# File: src/omega/memory/sqlite_vec_adapter_optimized.py
# Add after line 92 (after COLLECTIONS dict)

# Per-collection RRF weights (configurable)
COLLECTION_RRF_WEIGHTS = {
    "omega_vec_gemma_768": {"fts": 0.5, "vec": 0.5},
    "omega_vec_nomic_768": {"fts": 0.5, "vec": 0.5},
    "omega_vec_nomic_512": {"fts": 0.4, "vec": 0.6},   # MRL: trust vector more
    "omega_vec_nomic_256": {"fts": 0.3, "vec": 0.7},   # MRL: trust vector more
    "omega_vec_minilm_384": {"fts": 0.6, "vec": 0.4},  # Code: FTS more reliable
    "omega_vec_static_64": {"fts": 0.7, "vec": 0.3},   # Zero-cost: FTS primary
    "omega_vec_library_256": {"fts": 0.8, "vec": 0.2}, # Feature-hash: FTS primary
}

# In hybrid_search() (line 708), replace hardcoded defaults:
async def hybrid_search(
    self,
    query: str,
    entity_name: str,
    vector: List[float],
    limit: int = 20,
    fts_weight: Optional[float] = None,
    vec_weight: Optional[float] = None,
    collection: str = "omega_vec_gemma_768",
) -> List[Dict[str, Any]]:
    # Use collection-specific weights if not explicitly provided
    if fts_weight is None or vec_weight is None:
        weights = self.COLLECTION_RRF_WEIGHTS.get(collection, {"fts": 0.5, "vec": 0.5})
        fts_weight = fts_weight or weights["fts"]
        vec_weight = vec_weight or weights["vec"]
    # ... rest unchanged
```

**Verification**: `hybrid_search(collection="omega_vec_minilm_384")` uses 0.6/0.4 weights without explicit params.

---

### GAP-005: No Spatial Index (R-tree) for VR Spatial Queries

**File**: `src/omega/memory/sqlite_vec_adapter_optimized.py` — **No R-tree tables exist**  
**Root Cause**: The adapter only creates `vec0` (vector) and `fts5` (text) virtual tables. No `rtree` virtual table for 3D spatial coordinates. The SSM Spec (`R_SOVEREIGN_SPATIAL_MEMORY_SPEC.md`) requires BSP sector culling and "Find all memories within 5m of (x,y,z)" queries.

**sqlite-vec + R-tree Architecture**: sqlite-vec does NOT support spatial/R-tree natively. Options:
- **Option A**: Separate `rtree` virtual table (SQLite built-in) joined on `rowid`
- **Option B**: SpatiaLite extension (heavy, GIS-focused, 2D only per StackOverflow)
- **Option C**: Separate spatial collection `omega_vec_spatial_3` with R-tree

**Decision**: **Option A** — Native SQLite R-tree is zero-dependency, supports 3D (minX,maxX,minY,maxY,minZ,maxZ), joins on `rowid` with existing `omega_memory_data`.

**Fix Spec**:
```python
# File: src/omega/memory/sqlite_vec_adapter_optimized.py
# Add after line 246 (after FTS5 table creation in _ensure_initialized)

# Spatial R-tree table for 3D coordinates (VR navigation)
conn.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS omega_memory_spatial
    USING rtree(
        id,              -- Integer primary key (matches omega_memory_data.id)
        minX, maxX,      -- X coordinate bounds (point: minX=maxX=x)
        minY, maxY,      -- Y coordinate bounds
        minZ, maxZ       -- Z coordinate bounds
    )
""")

# In batch_upsert() (line 341), after FTS insert (line 428), add spatial insert:
# Requires spatial coordinates in metadata: metadata.get("spatial_coords", {"x":0,"y":0,"z":0})
spatial_data = []
for i in range(len(items)):
    coords = items[i].get("metadata", {}).get("spatial_coords", {"x": 0.0, "y": 0.0, "z": 0.0})
    x, y, z = coords.get("x", 0.0), coords.get("y", 0.0), coords.get("z", 0.0)
    spatial_data.append((rowids[i], x, x, y, y, z, z))  # Point: min=max

if spatial_data:
    conn.executemany(
        "INSERT INTO omega_memory_spatial(id, minX, maxX, minY, maxY, minZ, maxZ) VALUES (?, ?, ?, ?, ?, ?, ?)",
        spatial_data,
    )

# New method: Spatial range query for VR
async def spatial_range_query(
    self,
    entity_name: str,
    center_x: float, center_y: float, center_z: float,
    radius: float,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """Find all memories within radius of (x,y,z) — VR navigation query."""
    await self._ensure_initialized()
    
    min_x, max_x = center_x - radius, center_x + radius
    min_y, max_y = center_y - radius, center_y + radius
    min_z, max_z = center_z - radius, center_z + radius
    
    def _sync_spatial_query():
        conn = self._get_read_conn()
        cursor = conn.execute("""
            SELECT s.id, d.uuid, d.entity_name, d.session_id, d.role, d.content, d.timestamp, d.metadata_json
            FROM omega_memory_spatial s
            JOIN omega_memory_data d ON s.id = d.id
            WHERE s.minX <= ? AND s.maxX >= ?
              AND s.minY <= ? AND s.maxY >= ?
              AND s.minZ <= ? AND s.maxZ >= ?
              AND d.entity_name = ?
            LIMIT ?
        """, (max_x, min_x, max_y, min_y, max_z, min_z, entity_name, limit))
        
        results = []
        for row in cursor.fetchall():
            metadata = {
                "id": row[1], "entity_name": row[2], "session_id": row[3],
                "role": row[4], "content": row[5], "timestamp": row[6],
            }
            if row[7]:
                try:
                    metadata.update(json.loads(row[7]))
                except json.JSONDecodeError:
                    pass
            results.append(metadata)
        return results
    
    return await anyio.to_thread.run_sync(_sync_spatial_query)
```

**Verification**: Insert vectors with `spatial_coords` → `spatial_range_query(x=10,y=10,z=10,radius=5)` returns correct subset.

---

### GAP-006: Vector Deletion Cascade — O(N) Across All Collections

**File**: `src/omega/memory/sqlite_vec_adapter_optimized.py:589-626` (`delete` method)  
**Root Cause**: Lines 617-618 iterate `for collection_name in self._vec_tables_created:` and execute DELETE on each. With 7 collections, this is 7 DELETE statements per UUID. No `rowid → collection` mapping exists.

**Fix Spec**:
```python
# File: src/omega/memory/sqlite_vec_adapter_optimized.py
# Add after line 159 (after _legacy_vec_created = False)

# rowid -> collection mapping for O(1) delete
self._rowid_to_collection: Dict[int, str] = {}

# In batch_upsert() (line 341), after vec0 insert (line 444), record mapping:
for i in range(len(items)):
    self._rowid_to_collection[rowids[i]] = collection

# In delete() (line 589), replace lines 617-618:
# OLD: for collection_name in self._vec_tables_created:
#          conn.execute(f"DELETE FROM {collection_name} WHERE rowid = ?", (rowid,))
# NEW: O(1) delete using mapping
target_collection = self._rowid_to_collection.get(rowid)
if target_collection:
    conn.execute(f"DELETE FROM {target_collection} WHERE rowid = ?", (rowid,))
    del self._rowid_to_collection[rowid]
else:
    # Fallback: collection not in mapping (legacy data) — scan created tables
    for collection_name in self._vec_tables_created:
        conn.execute(f"DELETE FROM {collection_name} WHERE rowid = ?", (rowid,))

# In delete_session() (line 628), similar optimization:
# Build rowid->collection mapping for the session's rowids
rowid_to_coll = {rid: self._rowid_to_collection.get(rid) for rid in rowids}
for rowid, coll in rowid_to_coll.items():
    if coll:
        conn.execute(f"DELETE FROM {coll} WHERE rowid = ?", (rowid,))
    else:
        for collection_name in self._vec_tables_created:
            conn.execute(f"DELETE FROM {collection_name} WHERE rowid = ?", (rowid,))
```

**Verification**: Delete 1000 vectors → measure DELETE latency (should drop from ~7x to ~1x).

---

### GAP-007: WAL Checkpoint Automation Never Started

**File**: `src/omega/memory/sqlite_vec_adapter_optimized.py:816-833` (`start_periodic_checkpoint` exists but never called)  
**Root Cause**: `start_periodic_checkpoint()` method exists (line 816) but **no code calls it at startup**. The adapter initializes without starting the background checkpoint task. WAL file grows unbounded until manual `checkpoint_wal()` call.

**Fix Spec**:
```python
# File: src/omega/memory/sqlite_vec_adapter_optimized.py
# In __init__ (line 109), add auto-start parameter:
def __init__(
    self,
    db_path: Optional[str] = None,
    embedding_dim: int = DEFAULT_EMBEDDING_DIM,
    collections: Optional[Dict[str, Dict]] = None,
    timeout: float = 5.0,
    read_pool_size: int = 4,
    batch_size: int = 100,
    enable_metrics: bool = True,
    auto_checkpoint: bool = True,           # NEW: default True
    checkpoint_interval: int = 300,         # NEW: 5 minutes default
):

# Store params
self.auto_checkpoint = auto_checkpoint
self.checkpoint_interval = checkpoint_interval

# In _ensure_initialized() (line 207), after self._initialized = True (line 253):
if self.auto_checkpoint:
    await self.start_periodic_checkpoint(self.checkpoint_interval)
    logger.info("Auto WAL checkpoint enabled (interval=%ds)", self.checkpoint_interval)

# In close() (line 846), ensure cleanup:
async def close(self) -> None:
    if self._checkpoint_task:
        await self.stop_periodic_checkpoint()
    # ... rest unchanged
```

**Verification**: Start adapter → wait 300s → verify `wal_checkpoint_count` > 0 in `get_metrics()`.

---

### GAP-008: Metrics Persistence — In-Memory Only

**File**: `src/omega/memory/sqlite_vec_adapter_optimized.py:148-155` (`_metrics` dict) + `get_metrics()` (line 697)  
**Root Cause**: Metrics stored in `self._metrics` dict, lost on adapter restart. No persistence to `data/metrics/sqlite_vec_metrics.json`. Ingestion pipeline and observability require historical metrics.

**Fix Spec**:
```python
# File: src/omega/memory/sqlite_vec_adapter_optimized.py
# Add after line 155 (after _metrics dict)

# Metrics persistence path
self._metrics_path = self.db_path.parent / "metrics" / "sqlite_vec_metrics.json"
self._metrics_path.parent.mkdir(parents=True, exist_ok=True)

# Load persisted metrics on init
def _load_metrics(self) -> None:
    if self._metrics_path.exists():
        try:
            with open(self._metrics_path) as f:
                persisted = json.load(f)
                # Merge with defaults (preserve counters)
                self._metrics.update(persisted)
        except (json.JSONDecodeError, OSError):
            pass

# In __init__ (after line 155):
self._load_metrics()

# In get_metrics() (line 697), add persistence:
def get_metrics(self) -> Dict[str, Any]:
    metrics = self._metrics.copy()
    # ... compute averages ...
    # Persist atomically
    try:
        tmp_path = self._metrics_path.with_suffix(".tmp")
        with open(tmp_path, "w") as f:
            json.dump(metrics, f, indent=2)
        tmp_path.replace(self._metrics_path)
    except OSError:
        pass
    return metrics
```

**Verification**: Restart adapter → `get_metrics()` shows historical `upsert_count`, `query_count`.

---

### GAP-009: No INT8 Quantization Code Path (Duplicate of GAP-003 but distinct)

**File**: `src/omega/memory/sqlite_vec_adapter_optimized.py` — No quantization in upsert/query  
**Root Cause**: Even if tables created with int8 (GAP-003 fix), the `upsert()`/`batch_upsert()`/`query()` methods serialize only float32. Need quantization at write and dequantization at read for rescore.

**Fix Spec**: Combined with GAP-003 fix above. Key addition in `query()`:
```python
# In query() (line 477), for quantized collections:
coll_config = self._collections[collection]
quantization = coll_config.get("quantization", "none")

if quantization == "int8_rescore":
    # Query uses int8 index for fast ANN, then rescore with float32 auxiliary
    cursor = conn.execute(f"""
        SELECT v.rowid, v.distance,
               d.uuid, d.entity_name, d.session_id, d.role, d.content, d.timestamp, d.metadata_json
        FROM {collection} v
        JOIN omega_memory_data d ON v.rowid = d.id
        WHERE v.embedding MATCH ? AND v.entity_name = ? AND k = ?
        ORDER BY v.distance
    """, (sqlite_vec_serialize_int8(vector), entity_name, limit))
    # Note: sqlite-vec v0.1.10+ handles int8 MATCH + float32 rescore automatically
else:
    # Existing float32 path
    ...
```

---

## 📋 Implementation Priority Order

| Phase | Gaps | Dependencies | Est. Time |
|-------|------|--------------|-----------|
| **Phase 1 (P0 - Alpha Blocker)** | GAP-001, GAP-002, GAP-006 | None | 8h |
| **Phase 2 (P1 - Reliability)** | GAP-003, GAP-004, GAP-007, GAP-008 | Phase 1 | 8h |
| **Phase 3 (P1 - VR Prep)** | GAP-005 | Phase 1 | 6h |
| **Phase 4 (P1 - Quantization)** | GAP-009 | GAP-003 | 3h |

**Total**: ~25h engineering effort

---

## 🧪 Test Plan (Per Gap)

| Gap | Test Case |
|-----|-----------|
| GAP-001 | `adapter.get_status()["collections_created"] == 7 collections` |
| GAP-002 | Ingest 768-dim → verify 512/256/64 variants in respective collections |
| GAP-003 | `PRAGMA table_info(omega_vec_gemma_768)` shows `embedding int8[768]` + `embedding_fp32` |
| GAP-004 | `hybrid_search(collection="omega_vec_minilm_384")` uses 0.6/0.4 without explicit weights |
| GAP-005 | `spatial_range_query(center=(0,0,0), radius=10)` returns correct spatial subset |
| GAP-006 | Delete 1000 vectors → latency < 100ms (vs 700ms before) |
| GAP-007 | After 5min uptime → `get_metrics()["wal_checkpoint_count"] > 0` |
| GAP-008 | Restart adapter → `get_metrics()["upsert_count"]` persists |
| GAP-009 | Query quantized collection → ranking matches float32 baseline (recall@10 ≥ 0.98) |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ SQLITE-VEC-GAPS ⬡ 2026-08-28*
<!-- PROVENANCE-CORRECTED 2026-08-30T03:06:40Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

