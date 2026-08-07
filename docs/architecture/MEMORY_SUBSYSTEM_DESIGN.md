---
schema_version: "1.0"
document_type: architecture
document_id: memory-subsystem-design
title: Memory Subsystem Design
status: ACTIVE
version: "1.0.0"
date: "2026-08-07"
owner: kali
tags: [memory, sqlite-vec, graphrag, architecture, spatial]
priority: P1
depends_on: []
blocks: []
acceptance_gates:
  - "sqlite-vec documented as the SINGLE core vector store"
  - "Qdrant documented as optional WAD adapter only"
  - "Spatial coordinates (pos_x/pos_y/pos_z) required for all vector records"
  - "GraphRAG documented as native on SQLite"
cross_references:
  - src/omega/memory/sqlite_vec_adapter.py
  - src/omega/memory/hybrid_search.py
  - src/omega/memory_store.py
  - OMEGA_ENGINE.md
llm_metadata:
  token_budget: 2000
  chunk_strategy: section_per_topic
  answer_first_sections: true
  self_contained_code: false
---

# 🔱 Memory Subsystem Design

**AP Token**: `AP-MEMORY-SUBSYSTEM-DESIGN-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ 2026-08-07

---

## §1 The Store Hierarchy (UO-4 Decision)

> **`sqlite-vec` is the SINGLE Core vector store.** Qdrant is an **optional WAD adapter only.**

| Layer | Store | Role | Scope |
|-------|-------|------|-------|
| **Core Vector** | **sqlite-vec** | FTS5 + vec0 + SQL edges | Engine-native, always present |
| **Core Graph** | **SQLite (GraphRAG)** | Entity-relation edges on SQL | Engine-native |
| **Optional External** | **Qdrant** (TurboQuant BITS4) | Stack opt-in external vector infra | WAD adapter ONLY |
| **Legacy (deprecated)** | FAISS, PostgreSQL | Not permitted in core | Purged |

No new core dependency on Qdrant/FAISS/PostgreSQL is permitted. GraphRAG is native on SQLite.

---

## §2 sqlite-vec Adapter (Core)

**Module**: `src/omega/memory/sqlite_vec_adapter.py`
**Interface**: `IVectorStoreAdapter`

PRAGMA SSOT (converged):
```
cache_size = 32MB
wal_autocheckpoint = 500
journal_mode = WAL
synchronous = NORMAL
```

Backing tables:
- FTS5 table for BM25 keyword search
- `vec0` virtual table for vector cosine search
- Standard SQL tables for edge/relation data

---

## §3 Hybrid Search (RRF Fusion)

**Module**: `src/omega/memory/hybrid_search.py`

- FTS5 (BM25) + vector (cosine) results fused via **Reciprocal Rank Fusion, k=60**.
- 20 contract tests + 8 RRF math vectors.

---

## §4 GraphRAG (Native on SQLite)

GraphRAG is implemented **natively on SQLite** — entity nodes and relation edges
are SQL rows. No external graph database. This keeps the entire memory subsystem
within a single portable file, aligned with the local-first, zero-telemetry mandates.

---

## §5 Redis Task Canvas (Optional Hot Tier)

A Redis-backed task canvas MAY be used for the hot in-memory tier (fast ephemeral
task state). Redis is **optional** — the engine degrades to file-backed queues per
M12 (Queue Integrity, advisory). Never a hard dependency.

---

## §6 Mandatory Spatial Coordinates (Godot 4 OpenXR Readiness)

Every vector record in the Core store **MUST** carry spatial coordinates so the
memory can be rendered in a 3D space (Godot 4 / OpenXR) as a spatial memory palace:

```python
pos_x: float = 0.0
pos_y: float = 0.0
pos_z: float = 0.0
```

These coordinates map to the **Spatial Memory (Wings/Rooms/Drawers)** heritage
pattern (`[heritage: mempalace 2025]`) and enable:
- Physical anchoring of memories in a navigable space
- Proximity-based recall (nearby memories retrieved together)
- Immersive review via VR/OpenXR

---

*⬡ OMEGA ⬡ KALI ⬡ 2026-08-07*
