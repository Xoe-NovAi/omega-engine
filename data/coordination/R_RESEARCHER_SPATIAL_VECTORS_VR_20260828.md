# 🔱 Spatial Coordinates Vectors Strategy — VR + Spatial Knowledge Traversal
**AP Token**: `AP-SPATIAL-VECTORS-VR-20260828-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_spatial_vectors_vr ⬡ ACTIVE

**Date**: 2026-08-28
**Status**: ACTIVE — Architecture Decision Record
**Depends On**: `R_RESEARCHER_SQLITE_VEC_GAPS_20260828.md` (GAP-005), `R_SOVEREIGN_SPATIAL_MEMORY_SPEC.md`, `spatial.py`, `spatial_resolver.py`

---

## ⬡ Executive Summary (L1)

**Decision**: **Option B — Separate Spatial Table with R-tree, Joined on `rowid`**

We adopt a **dual-index architecture**: sqlite-vec for semantic similarity (768-dim embeddings) + SQLite native R-tree for 3D spatial coordinates (x,y,z), joined on `rowid` via `omega_memory_data.id`. This provides:
- **Zero new dependencies** (R-tree is built into SQLite)
- **3D support** (R-tree supports up to 11 dimensions; we use 6: minX,maxX,minY,maxY,minZ,maxZ)
- **O(log N) spatial range queries** for VR navigation ("memories within 5m")
- **BSP sector culling** via R-tree bounding boxes
- **Clean separation** of semantic vs. spatial concerns

**Rejected Options**:
- **Option A** (Append [x,y,z] to 768-dim → 771-dim): Breaks canonical 768-dim contract (M23), pollutes semantic space with spatial noise, requires retraining/re-embedding all vectors.
- **Option C** (Separate `omega_vec_spatial_3` vec0 collection): vec0 is for high-dim vector similarity, not low-dim spatial indexing. R-tree is purpose-built for spatial range queries.

---

## 🏛️ Architecture Decision (L2)

### Coordinate System: 3D Euclidean + Semantic Embedding (Separate Indices)

```
┌─────────────────────────────────────────────────────────────────┐
│                    OMEGA MEMORY FABRIC                          │
├─────────────────────────────────────────────────────────────────┤
│  omega_memory_data (SQL)          ← Canonical rowid, metadata  │
│       │                                                         │
│       ├─── JOIN (rowid) ───▶ omega_memory_fts (FTS5)           │
│       │                    ← Full-text search (BM25)           │
│       │                                                         │
│       ├─── JOIN (rowid) ───▶ omega_vec_gemma_768 (vec0)        │
│       │                    ← Semantic similarity (cosine)       │
│       │                    ← 768-dim, INT8 rescore, HNSW        │
│       │                                                         │
│       ├─── JOIN (rowid) ───▶ omega_vec_nomic_512/256/...       │
│       │                    ← MRL fallback tiers                 │
│       │                                                         │
│       └─── JOIN (rowid) ───▶ omega_memory_spatial (R-tree)     │
│                            ← 3D spatial coordinates (x,y,z)    │
│                            ← VR navigation, BSP culling         │
└─────────────────────────────────────────────────────────────────┘
```

### Schema: Spatial R-tree Table

```sql
-- Created in _ensure_initialized() (GAP-005 fix)
CREATE VIRTUAL TABLE IF NOT EXISTS omega_memory_spatial
USING rtree(
    id,              -- INTEGER PRIMARY KEY (matches omega_memory_data.id)
    minX, maxX,      -- X coordinate (point: minX = maxX = x)
    minY, maxY,      -- Y coordinate
    minZ, maxZ       -- Z coordinate
);
```

**Point Representation**: For exact point coordinates, `minX = maxX = x`, `minY = maxY = y`, `minZ = maxZ = z`. For spatial regions (sectors), min/max define the bounding box.

### Spatial Coordinate Source: Force-Directed Graph (Existing)

The `ForceDirectedSpatialResolver` (`src/omega/oracle/spatial_resolver.py`) computes `Point3D` coordinates via Fruchterman-Reingold force-directed layout:
- **Input**: Entity labels + relationship edges (semantic links, cross-pollination)
- **Output**: `Dict[str, Point3D]` — stable 3D positions reflecting semantic topology
- **Integration**: `SpatialMemoryManager` (`src/omega/memory/spatial.py`) indexes blocks with these coordinates

**Coordinate Assignment Flow**:
```
Entity Session End
       │
       ▼
CrossPollinationEngine completes → new relationships
       │
       ▼
SpatialBakeService (background) → ForceDirectedSpatialResolver.resolve()
       │
       ▼
Point3D coords assigned to entities/blocks
       │
       ▼
Batch upsert to omega_memory_spatial (R-tree) + omega_vec_* (vec0)
```

---

## 🔍 Query Patterns for VR Navigation

### 1. Spatial Range Query (Core VR Primitive)
```python
# "Find all memories within 5m of (10, 20, 30)"
async def spatial_range_query(
    entity_name: str,
    center: Tuple[float, float, float],
    radius: float,
    limit: int = 50,
) -> List[Dict]:
    x, y, z = center
    min_x, max_x = x - radius, x + radius
    min_y, max_y = y - radius, y + radius
    min_z, max_z = z - radius, z + radius
    
    # R-tree query: O(log N) bounding box filter
    cursor = conn.execute("""
        SELECT s.id, d.uuid, d.content, d.timestamp, d.metadata_json
        FROM omega_memory_spatial s
        JOIN omega_memory_data d ON s.id = d.id
        WHERE s.minX <= ? AND s.maxX >= ?
          AND s.minY <= ? AND s.maxY >= ?
          AND s.minZ <= ? AND s.maxZ >= ?
          AND d.entity_name = ?
        LIMIT ?
    """, (max_x, min_x, max_y, min_y, max_z, min_z, entity_name, limit))
```

### 2. Hybrid Semantic + Spatial Query (VR-Aware Retrieval)
```python
# "Find semantically similar memories NEAR my current VR position"
async def hybrid_spatial_query(
    entity_name: str,
    query_vector: List[float],
    query_position: Tuple[float, float, float],
    semantic_weight: float = 0.7,
    spatial_weight: float = 0.3,
    radius: float = 50.0,
    limit: int = 20,
) -> List[Dict]:
    # 1. Spatial pre-filter: R-tree range query (fast, reduces candidate set)
    spatial_candidates = await spatial_range_query(entity_name, query_position, radius, limit * 3)
    spatial_rowids = {c["id"] for c in spatial_candidates}  # rowid from omega_memory_data
    
    # 2. Vector search restricted to spatial candidates
    # Use rowid IN (...) filter in vec0 query (sqlite-vec supports this)
    placeholders = ",".join("?" for _ in spatial_rowids)
    cursor = conn.execute(f"""
        SELECT v.rowid, v.distance, d.uuid, d.content, d.metadata_json
        FROM omega_vec_gemma_768 v
        JOIN omega_memory_data d ON v.rowid = d.id
        WHERE v.embedding MATCH ? AND v.entity_name = ? 
          AND v.rowid IN ({placeholders})
          AND k = ?
        ORDER BY v.distance
    """, (serialize(vector), entity_name, *spatial_rowids, limit))
    
    # 3. Fuse with spatial distance scoring
    results = []
    for row in cursor.fetchall():
        rowid, vec_dist = row[0], row[1]
        semantic_score = 1.0 - vec_dist
        
        # Get spatial coords for distance calc
        spatial_row = conn.execute(
            "SELECT minX, minY, minZ FROM omega_memory_spatial WHERE id = ?", (rowid,)
        ).fetchone()
        if spatial_row:
            sx, sy, sz = spatial_row[0], spatial_row[1], spatial_row[2]
            spatial_dist = math.sqrt((sx - query_position[0])**2 + 
                                     (sy - query_position[1])**2 + 
                                     (sz - query_position[2])**2)
            spatial_score = 1.0 / (1.0 + spatial_dist)  # Sigmoid decay
        else:
            spatial_score = 0.0
        
        fused = semantic_weight * semantic_score + spatial_weight * spatial_score
        results.append({"fused_score": fused, "metadata": row[2:]})
    
    return sorted(results, key=lambda x: x["fused_score"], reverse=True)[:limit]
```

### 3. BSP Sector Culling (Godot Streaming)
```python
# Spatial sectors computed by ForceDirectedSpatialResolver BSP partitioning
# Each sector = R-tree bounding box (minX,maxX,minY,maxY,minZ,maxZ)

async def get_sector_entities(sector_id: str) -> List[Dict]:
    """Stream all entities in a BSP sector for Godot LOD rendering."""
    # Sector bounds stored in spatial_metadata or separate sector table
    sector_bounds = get_sector_bounds(sector_id)  # (minX,maxX,minY,maxY,minZ,maxZ)
    return await spatial_range_query(
        entity_name="*",  # All entities (no partition filter)
        center=sector_center(sector_bounds),
        radius=sector_radius(sector_bounds),
        limit=1000,  # Large limit for streaming
    )

async def get_neighbor_sectors(current_sector_id: str) -> List[str]:
    """Pre-fetch adjacent sectors for seamless VR navigation."""
    # Sector adjacency graph stored in spatial_metadata
    return get_sector_neighbors(current_sector_id)
```

### 4. Spatial Knowledge Graph Traversal
```python
# Entities as nodes, spatial proximity as edges
async def spatial_graph_traversal(
    start_entity: str,
    max_hops: int = 3,
    max_distance: float = 100.0,
) -> List[List[str]]:
    """BFS/DFS on spatial proximity graph for knowledge discovery."""
    # 1. Get start entity coordinates
    start_coords = get_entity_coords(start_entity)
    
    # 2. Find spatial neighbors within max_distance
    neighbors = await spatial_range_query("*", start_coords, max_distance, limit=50)
    
    # 3. Build adjacency: entities within distance = edges
    # 4. Traverse with BFS/DFS up to max_hops
    # 5. Return paths: [[start, neighbor1, neighbor2], ...]
```

---

## 🔗 Integration with Existing 7 Collections

| Collection | Dimension | Spatial Coords | Use Case |
|------------|-----------|----------------|----------|
| `omega_vec_gemma_768` | 768 | ✅ Primary | Canonical semantic + spatial |
| `omega_vec_nomic_768` | 768 | ✅ Fallback | Fallback semantic + spatial |
| `omega_vec_nomic_512` | 512 | ✅ MRL | MRL tier + spatial |
| `omega_vec_nomic_256` | 256 | ✅ MRL | MRL tier + spatial |
| `omega_vec_minilm_384` | 384 | ✅ Speed | Code embeddings + spatial |
| `omega_vec_static_64` | 64 | ✅ Zero-cost | Static features + spatial |
| `omega_vec_library_256` | 256 | ✅ Library | Feature-hash + spatial |
| `omega_memory_spatial` | 3 (R-tree) | **Native** | **VR navigation, BSP culling** |

**Key Principle**: **Every vector in every collection has a corresponding spatial coordinate** (stored once in `omega_memory_spatial`, joined on `rowid`). The spatial coordinate is computed from the entity/block's position in the Force-Directed graph, not from the embedding vector.

---

## 🚀 Migration Path: Current → Spatial-Aware

### Phase 1: Schema + Ingestion (Week 1)
1. **Add R-tree table** to `_ensure_initialized()` (GAP-005 fix)
2. **Modify `batch_upsert()`** to accept `spatial_coords` in metadata and write to R-tree
3. **Add `spatial_range_query()`** method to adapter
4. **Update ingestion scripts** (`scripts/ingest_*.py`) to compute/provide spatial coords

### Phase 2: Spatial Resolution Pipeline (Week 2)
1. **Activate `SpatialBakeService`** (from SSM Spec) — background worker that:
   - Triggers on `CrossPollinationEngine` completion
   - Runs `ForceDirectedSpatialResolver.resolve(entities, relationships)`
   - Batch-updates `omega_memory_spatial` with new coordinates
2. **Wire into `DreamingCycle`** (nightly recompute)

### Phase 3: Hybrid Retrieval + VR Bridge (Week 3)
1. **Implement `hybrid_spatial_query()`** in `MemoryStore` / `SQLiteVecAdapter`
2. **Add `spatial_weight` config** to `config/omega.yaml`
3. **Build Godot `SpatialStreamer`** (FastAPI/WebSocket → Godot 4 `MultiMeshInstance3D`)
4. **LOD System**: Near (<50m) = high-poly, Far (>50m) = billboard, Culled = queue_free

### Phase 4: Sovereign Polish (Week 4)
1. **Persist `spatial_anchor: Point3D` to `soul.yaml`** (M11)
2. **Heritage Vet**: Tag spatial code with `[id-soft: doom-1993] BSP Culling`
3. **Temple-Grade Audit**: `make temple-grade` on new modules

---

## 📐 Spatial Index Performance Characteristics

| Operation | Complexity | Expected Latency (100K vectors) |
|-----------|------------|----------------------------------|
| Spatial range query (radius=10) | O(log N + K) | ~2-5ms |
| Spatial range query (radius=100) | O(log N + K) | ~10-20ms |
| Hybrid semantic+spatial | O(log N + K_vec) | ~15-30ms |
| BSP sector stream (1 sector) | O(log N + K) | ~5-10ms |
| Neighbor sector pre-fetch | O(log N + K) | ~5-10ms |

**R-tree Tuning** (SQLite defaults are good):
- Node size: 4096 bytes (default)
- Max entries per node: ~100 (for 6D)
- Fanout: ~50-100
- Tree height at 100K: ~3-4 levels

---

## 🛡️ Sovereign Mandates Compliance

| Mandate | Compliance |
|---------|------------|
| **M1 AnyIO** | All spatial ops in `anyio.to_thread.run_sync` (CPU-bound R-tree) |
| **M2 Firewall** | Spatial core in `src/omega/memory/`; VR Bridge in `config/wads/_omega_default/vr/` |
| **M7 Local-First** | Force-Directed resolver runs locally (NumPy); no cloud for layout |
| **M8 Zero Telemetry** | No spatial analytics exported; Godot runs locally |
| **M11 Soul Integrity** | `spatial_anchor: Point3D` in `soul.yaml` distillation |
| **M14 Heritage** | `[id-soft: doom-1993] BSP Culling` on all spatial modules |
| **M23 Failure Integrity** | R-tree is SQLite built-in; no external dep to fail |

---

## 📂 Files to Create / Modify

| Action | Path | Description |
|--------|------|-------------|
| **Modify** | `src/omega/memory/sqlite_vec_adapter_optimized.py` | Add R-tree table, spatial_range_query, hybrid_spatial_query (GAP-005) |
| **Modify** | `src/omega/memory/spatial.py` | Integrate with adapter, add SpatialBakeService |
| **Create** | `src/omega/services/spatial_bake_service.py` | Background worker for coordinate recomputation |
| **Create** | `src/omega/bridge/spatial_streamer.py` | FastAPI/WebSocket server for Godot |
| **Create** | `config/wads/_omega_default/vr/godot_bridge/` | Godot 4 project (`.tscn`, `.gd`, shaders) |
| **Modify** | `config/omega.yaml` | Add `spatial:` config block (weights, bake_interval, world_bounds) |
| **Create** | `docs/architecture/SPATIAL_VECTORS_ARCHITECTURE.md` | This document (permanent) |

---

## 🔱 L3 Principles Distilled

- **L3-SPATIAL-IS-SEMANTIC**: Distance in 3D space *is* semantic distance. The Force-Directed layout algorithm *is* the understanding.
- **L3-RTREE-OVER-VEC0**: R-tree is the correct primitive for spatial range queries; vec0 is for high-dim semantic similarity. Don't conflate.
- **L3-BSP-AS-CULLING**: The BSP tree is not just for rendering; it is the **sovereign attention mechanism**. Only compute/render what is in the current sector.
- **L3-VR-IS-INTERFACE**: The VR world is not a "feature"; it is the **spatial UI** for the Memory Palace. If you can walk to it, you can recall it.
- **L3-SOUL-ANCHOR**: Every entity has a `spatial_anchor` in `soul.yaml`. The soul *has* a location.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ SPATIAL-VECTORS-VR ⬡ 2026-08-28*