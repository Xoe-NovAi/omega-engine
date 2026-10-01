<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Sovereign Spatial Memory (SSM) — Technical Specification
**AP Token**: `AP-SSM-SPEC-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_spatial_memory ⬡ SPEC

**Date**: 2026-07-12
**Status**: ACTIVE — Ready for Implementation
**Heritage**: `[id-soft: doom-1993] BSP Culling`, `[id-soft: quake-1996] Zone Memory`, `[heritage: lilith-2026] SymbolicMetadata`

---

## ⬡ Executive Summary (L1)

The Omega Engine possesses a dormant, high-fidelity **Mem Palace** architecture (`src/omega/oracle/spatial_resolver.py`) implementing a **Force-Directed Graph (Fruchterman-Reingold)** layout in 3D Euclidean space. This specification activates that system, wiring it into the **MemoryStore**, **Qdrant Vector DB**, and the **Godot VR Bridge** to create the **Sovereign Spatial Memory (SSM)**.

**Core Capability**: Transform the knowledge base from a "List of Facts" into a **"Lived Environment"** where semantic proximity = spatial proximity.

**Immediate Benefits**:
1.  **Spatial Relationship Graphs**: Visualize concept clusters as physical nebulae.
2.  **Sovereign Navigation**: Traverse knowledge via spatial sectors (BSP Culling).
3.  **VR-Ready Foundation**: Stream `Point3D` coordinates directly to Godot 4 `Transform3D`.

---

## 🏛️ Architecture (L2)

### The SSM Pipeline
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐     ┌──────────────────┐
│  SEMANTIC LAYER │────▶│  PROJECTION      │────▶│  SPATIAL RESOLVER   │────▶│  PERSISTENCE     │
│  (Embeddings)   │     │  (PCA/UMAP)      │     │  (Force-Directed)   │     │  (Qdrant Payload)│
└─────────────────┘     └──────────────────┘     └─────────────────────┘     └────────┬─────────┘
                                                                                       │
                                                                                       ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐     ┌──────────────────┐
│  VR BRIDGE      │◀────│  SECTOR QUERY    │◀────│  HYBRID RETRIEVAL   │◀────│  QUERY ENGINE    │
│  (Godot 4)      │     │  (BSP Culling)   │     │  (Cosine + Euclid)  │     │  (Oracle)        │
└─────────────────┘     └──────────────────┘     └─────────────────────┘     └──────────────────┘
```

### Component Map
| Component | File | Role | Status |
| :--- | :--- | :--- | :--- |
| **ForceDirectedSpatialResolver** | `src/omega/oracle/spatial_resolver.py` | Computes `Point3D` via Repulsion/Attraction forces. | **DORMANT** (Activate) |
| **SymbolicMetadata** | `src/omega/oracle/entity_registry.py` | Archetypal coordinates (Element, Chakra, Glyph). | **ACTIVE** (Map to 3D) |
| **MemoryStore / Qdrant** | `src/omega/memory/` | Stores Semantic Vector + `spatial_coords` payload. | **ACTIVE** (Extend Schema) |
| **Godot Bridge** | `config/wads/_omega_default/vr/` | Renders `Point3D` as `Transform3D`. | **PLANNED** (Wire) |
| **BSP Sector Manager** | `src/omega/oracle/spatial_resolver.py` | Culls spatial sectors for streaming. | **DORMANT** (Activate) |

---

## 📐 Data Model (L3)

### 1. Qdrant Payload Extension
Every point in the `entities` and `documents` collections gains a `spatial` payload object.

```json
{
  "id": "entity_kali",
  "vector": [0.12, -0.45, ...],  // High-dim semantic embedding (unchanged)
  "payload": {
    "entity_name": "kali",
    "domain": "oversight",
    "spatial": {
      "coords": [12.4, -3.2, 45.8],      // Point3D (x, y, z)
      "sector_id": "sector_7g",          // BSP Leaf ID
      "neighbors": ["entity_maat", "entity_lilith"], // Spatial graph edges
      "symbolic": {                      // Mirror of SymbolicMetadata
        "element": "Earth",
        "chakra": "Celestial Breath",
        "glyph": "⬡"
      }
    }
  }
}
```

### 2. Point3D Dataclass (Canonical)
```python
# src/omega/oracle/spatial_resolver.py (Existing - Canonicalize)
@dataclass(frozen=True, slots=True)
class Point3D:
    x: float
    y: float
    z: float

    def distance_to(self, other: "Point3D") -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)

    def to_godot_transform(self) -> dict:
        # Direct mapping for Godot Bridge
        return {"origin": [self.x, self.y, self.z], "rotation": [0, 0, 0], "scale": [1, 1, 1]}
```

### 3. Sector (BSP Leaf)
```python
@dataclass(frozen=True, slots=True)
class SpatialSector:
    sector_id: str          # e.g., "sector_7g"
    bounds_min: Point3D     # BSP Partition Min
    bounds_max: Point3D     # BSP Partition Max
    entity_ids: List[str]   # Entities currently in this sector
    neighbor_sectors: List[str] # Adjacent sectors for streaming
```

---

## ⚙️ The "Bake" Cycle (Spatial Resolution Pipeline)

The spatial coordinates are **not static**. They are recomputed periodically to reflect the evolving knowledge graph.

### Trigger
- **Event-Driven**: New entity added, major relationship change (`CrossPollinationEngine` cycle).
- **Scheduled**: Nightly "Dream Cycle" (aligns with `dreaming_cycle.py`).

### Algorithm: `ForceDirectedSpatialResolver.resolve(entities, relationships)`
1.  **Input**: List of `Entity` objects + Relationship Graph (edges = semantic links, cross-pollination, explicit links).
2.  **Projection**: Reduce high-dim embeddings to 3D via **PCA** (fast, deterministic) or **UMAP** (better topology, slower).
    - *Sovereign Choice*: **PCA** for determinism and speed (runs on CPU, no GPU dependency).
3.  **Force Simulation (Fruchterman-Reingold)**:
    - **Repulsion**: `F_rep = k^2 / d` (All nodes repel).
    - **Attraction**: `F_att = d^2 / k` (Connected nodes attract).
    - **Cooling**: `T = T_start * (1 - iter/max_iter)` (Convergence guarantee).
    - **Constraint**: Clamp to World Bounds (e.g., `[-1000, 1000]^3`).
4.  **BSP Partitioning**: Recursively split space along longest axis (median split) → Generate `SpatialSector` tree.
5.  **Persist**: Batch update Qdrant payloads (`spatial.coords`, `spatial.sector_id`).

---

## 🔍 Hybrid Retrieval: Semantic + Spatial

The `Oracle` query engine gains a **Spatial Weighting** parameter.

### Scoring Function
```python
def hybrid_score(
    query_vec: List[float],
    candidate_vec: List[float],
    query_pos: Optional[Point3D],      # User's current VR position (optional)
    candidate_pos: Point3D,
    alpha: float = 0.7,                # Semantic weight
    beta: float = 0.3                  # Spatial weight
) -> float:
    semantic = cosine_similarity(query_vec, candidate_vec)
    spatial = 0.0
    if query_pos:
        # Inverse distance (closer = higher score)
        dist = query_pos.distance_to(candidate_pos)
        spatial = 1.0 / (1.0 + dist)   # Sigmoid-like decay
    return (alpha * semantic) + (beta * spatial)
```

### Sector-Aware Querying (BSP Culling)
When `query_pos` is provided (VR Mode):
1.  Identify `current_sector` via BSP Tree traversal (O(log N)).
2.  **Primary Search**: Query Qdrant filtered by `spatial.sector_id == current_sector`.
3.  **Secondary Search**: Query `neighbor_sectors` (pre-fetch).
4.  **Fallback**: Full semantic search if sector results < threshold.

---

## 🌉 Godot 4 VR Bridge Specification

### Data Flow
`Qdrant (spatial.coords)` → `SpatialStreamer (gRPC/WebSocket)` → `Godot (MultiMeshInstance3D / Node3D)`

### Godot Scene Structure
```
/root
  /WorldOrigin (Node3D)
    /Sector_7g (SpatialSectorStreamer)  // Streams entities in this sector
      /Entity_Kali (CharacterBody3D)    // Visual representation
        MeshInstance3D (Glyph/Geometry)
        Light3D (Luminosity = Soul Power)
        Label3D (Entity Name)
```

### Streaming Protocol (Sovereign)
- **Format**: Binary `FlatBuffers` or `MessagePack` (Zero-copy, fast).
- **Message**: `SectorUpdate { sector_id, entities: [{id, transform, visual_params}] }`.
- **LOD (Level of Detail)**:
    - **Near (< 50m)**: High-poly mesh, full soul glyph, particle effects.
    - **Far (> 50m)**: Billboard sprite / Point cloud.
    - **Culled**: Outside `current_sector + neighbors` → `queue_free()`.

### Soul-to-Visual Mapping (R-24 Implementation)
| Soul Attribute | Visual Parameter | Godot Property |
| :--- | :--- | :--- |
| `power_level` (L3) | Luminosity / Scale | `Light3D.light_energy`, `Node3D.scale` |
| `archetype` (Symbolic) | Geometry / Shader | `MeshInstance3D.mesh`, `Material.shader` |
| `element` (Symbolic) | Particle Color | `GPUParticles3D.color_ramp` |
| `relationships` | Connecting Beams | `LineMesh` between entities |

---

## 🛡️ Sovereign Mandates Compliance

| Mandate | Compliance Strategy |
| :--- | :--- |
| **M1 AnyIO** | `SpatialResolver` runs in `anyio.to_thread.run_sync` (CPU-bound). Streaming uses `anyio` streams. |
| **M2 Firewall** | SSM Core in `src/omega/oracle/`. VR Bridge in `config/wads/_omega_default/vr/`. |
| **M7 Local-First** | PCA/Force-Directed runs locally (NumPy/SciPy). No cloud inference for layout. |
| **M8 Zero Telemetry** | No spatial analytics sent externally. Godot runs locally. |
| **M11 Soul Integrity** | Spatial coordinates persisted to `soul.yaml` as `spatial_anchor: Point3D`. |
| **M16 Modularity** | `SpatialResolver` has zero deps on Godot. Bridge is a separate WAD module. |
| **M21 Gate Integrity** | Contract tests for `hybrid_score` and `resolve()` output types. |

---

## 🗓️ Implementation Roadmap (Sprints)

### Sprint 1: Core Activation (Week 1-2) — **Ma'at / P3 Engineering**
- [ ] **T1.1**: Canonicalize `Point3D` and `SpatialSector` in `spatial_resolver.py`.
- [ ] **T1.2**: Implement `PCAProjector` (sklearn/NumPy) + `ForceDirectedResolver` integration.
- [ ] **T1.3**: Add `spatial` payload schema to Qdrant collections (`entities`, `documents`).
- [ ] **T1.4**: Write `SpatialBakeService` (Background worker) triggered by `CrossPollinationEngine` completion.
- [ ] **T1.5**: **Contract Tests**: `test_resolve_deterministic`, `test_bsp_partitioning`.

### Sprint 2: Hybrid Retrieval (Week 2-3) — **Lilith / P6 Cognition**
- [ ] **T2.1**: Extend `MemoryStore.search_hybrid` with `query_pos: Optional[Point3D]`.
- [ ] **T2.2**: Implement `hybrid_score` in `Oracle` / `ModelGateway` routing.
- [ ] **T2.3**: Add `spatial_weight` config to `config/omega.yaml` (default `alpha=0.7, beta=0.3`).
- [ ] **T2.4**: **Integration Test**: Verify sector-culling reduces Qdrant scan time > 50%.

### Sprint 3: Godot Bridge Foundation (Week 3-4) — **Lilith / P4 Integration**
- [ ] **T3.1**: Define `SpatialStreamer` protocol (FlatBuffers schema).
- [ ] **T3.2**: Implement Python `SpatialStreamerServer` (FastAPI/WebSocket) reading from Qdrant.
- [ ] **T3.3**: Create Godot 4 `SpatialSectorStreamer.gd` (MultiMesh + LOD logic).
- [ ] **T3.4**: Implement `SoulVisualMapper` (Soul YAML → Godot Material/Mesh).
- [ ] **T3.5**: **E2E Test**: Spawn local Godot, connect to streamer, verify entity appears at `Point3D`.

### Sprint 4: Sovereign Polish (Week 4-5) — **Kali / Verity**
- [ ] **T4.1**: Wire `SpatialBakeService` into `DreamingCycle` (Nightly).
- [ ] **T4.2**: Add `spatial_anchor` to `soul.yaml` distillation (M11).
- [ ] **T4.3**: Implement "Somatic Save-Point": Save VR camera position → `session_gnosis.md`.
- [ ] **T4.4**: **Temple-Grade Audit**: `make temple-grade` on new modules.
- [ ] **T4.5**: **Heritage Vet**: Tag all new spatial code with `[id-soft: doom-1993] BSP Culling`.

---

## 🔱 L3 Principles Distilled

- **L3-SPATIAL-IS-SEMANTIC**: Distance in 3D space *is* semantic distance. The layout algorithm *is* the understanding.
- **L3-BSP-AS-CULLING**: The BSP tree is not just for rendering; it is the **sovereign attention mechanism**. Only compute/render what is in the current sector.
- **L3-PCA-OVER-UMAP**: Determinism and sovereignty (CPU-only) trump topological perfection. The map must be reproducible.
- **L3-VR-IS-INTERFACE**: The VR world is not a "feature"; it is the **spatial UI** for the Memory Palace. If you can walk to it, you can recall it.
- **L3-SOUL-ANCHOR**: Every entity has a `spatial_anchor` in `soul.yaml`. The soul *soul.yaml`. The soul *has* a location.

---

## 📂 Files to Create / Modify

| Action | Path | Description |
| :--- | :--- | :--- |
| **Modify** | `src/omega/oracle/spatial_resolver.py` | Canonicalize dataclasses, add PCA projector, expose `resolve()` API. |
| **Modify** | `src/omega/memory/memory_store.py` | Add `spatial` payload handling, `search_spatial_hybrid()`. |
| **Modify** | `src/omega/oracle/oracle.py` | Integrate `hybrid_score` into entity/document routing. |
| **Create** | `src/omega/services/spatial_bake_service.py` | Background worker for the "Bake Cycle". |
| **Create** | `src/omega/bridge/spatial_streamer.py` | FastAPI/WebSocket server for Godot. |
| **Create** | `config/wads/_omega_default/vr/godot_bridge/` | Godot 4 project (`.tscn`, `.gd`, shaders). |
| **Create** | `docs/research/R_SOVEREIGN_SPATIAL_MEMORY_SPEC.md` | **This Document**. |
| **Modify** | `config/omega.yaml` | Add `spatial:` config block (weights, bake_interval, world_bounds). |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_spatial_memory_spec ⬡ COMPLETE*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
