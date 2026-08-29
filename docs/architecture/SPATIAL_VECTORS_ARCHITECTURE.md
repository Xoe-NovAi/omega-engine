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