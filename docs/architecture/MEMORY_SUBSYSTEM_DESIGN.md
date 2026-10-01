---
schema_version: "1.0"
document_type: architecture
document_id: memory-subsystem-design
title: Memory Subsystem Design
status: ACTIVE
version: "1.1.0"
date: "2026-08-16"
owner: kali
tags: [memory, sqlite-vec, qdrant, graphrag, architecture, spatial, adapter-pattern]
priority: P1
depends_on: []
blocks: []
acceptance_gates:
  - "sqlite-vec documented as the SINGLE core vector store"
  - "Qdrant documented as optional WAD adapter only"
  - "IVectorStoreAdapter pattern documented with 3 implementations"
  - "7 per-model collections architecture documented"
  - "Spatial coordinates (pos_x/pos_y/pos_z) required for all vector records"
  - "GraphRAG documented as native on SQLite"
cross_references:
  - src/omega/memory/sqlite_vec_adapter.py
  - src/omega/memory/vector_adapters.py
  - src/omega/memory/hybrid_search.py
  - src/omega/memory_store.py
  - OMEGA_ENGINE.md
llm_metadata:
  token_budget: 3000
  chunk_strategy: section_per_topic
  answer_first_sections: true
  self_contained_code: false
---

# 🔱 Memory Subsystem Design

**AP Token**: `AP-MEMORY-SUBSYSTEM-DESIGN-v1.1.0`
⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ 2026-08-16

---

## §1 The Store Hierarchy (UO-4 Decision)

> **`sqlite-vec` is the SINGLE Core vector store.** Qdrant is an **optional WAD adapter only.**

| Layer | Store | Role | Scope |
|-------|-------|------|-------|
| **Core Vector** | **sqlite-vec** | FTS5 + 7 per-model vec0 + SQL edges | Engine-native, always present |
| **Core Graph** | **SQLite (GraphRAG)** | Entity-relation edges on SQL | Engine-native |
| **Optional External** | **Qdrant** (Scalar int8 quant) | Stack opt-in external vector infra | WAD adapter ONLY |
| **Legacy (deprecated)** | FAISS, PostgreSQL | Not permitted in core | Purged |

No new core dependency on Qdrant/FAISS/PostgreSQL is permitted. GraphRAG is native on SQLite.

---

## §2 Vector Store Adapter Pattern (M2 Engine-Stack Firewall)

**Module**: `src/omega/memory/vector_adapters.py`
**Interface**: `IVectorStoreAdapter` (ABC)

The Omega Engine maintains **DB-agnostic semantic memory** through the adapter pattern. This ensures the Engine-Stack Firewall (M2) — the core engine never depends on a specific vector database.

### Implementations

| Adapter | Status | Purpose |
|---------|--------|---------|
| `SQLiteVecAdapter` | ✅ **Core Unified Fabric** | Primary production backend. 7 per-model vec0 collections + FTS5 BM25 + RRF fusion. |
| `MemoryVectorAdapter` | ✅ **Sovereign Fallback** | In-memory cosine similarity. Zero dependencies. Used when external stores unavailable. |
| `QdrantAdapter` | ⚠️ **Deprecated Heritage Ref** | Retained for reference only. Implements `IVectorStoreAdapter` for future WAD adapter use. |

### IVectorStoreAdapter Contract

```python
class IVectorStoreAdapter(ABC):
    @abstractmethod
    async def upsert(self, entity_name: str, vector: List[float], metadata: Dict, id: Optional[str]) -> str
    
    @abstractmethod
    async def query(self, entity_name: str, vector: List[float], limit: int, filter: Optional[Dict]) -> List[Tuple[float, Dict]]
    
    @abstractmethod
    async def delete(self, entity_name: str, ids: List[str]) -> bool
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]
```

**Entity isolation is mandatory** — every query MUST filter by `entity_name` to ensure sovereign memory separation.

---

## §3 sqlite-vec Adapter (Core Unified Fabric)

**Module**: `src/omega/memory/sqlite_vec_adapter.py`
**Implements**: `IVectorStoreAdapter`

### PRAGMA SSOT (Converged)
```
cache_size = 32MB
wal_autocheckpoint = 500
journal_mode = WAL
synchronous = NORMAL
```

### 7 Per-Model Collections Architecture

The unified fabric uses **one vec0 collection per embedding model/dimension** — not a single collection. This preserves embedding fidelity and enables MRL (Matryoshka) truncation fallbacks.

| Collection | Dimension | Model | Metric | Quantization | HNSW Params |
|------------|-----------|-------|--------|--------------|-------------|
| `omega_vec_gemma_768` | 768 | EmbeddingGemma 300M (primary) | cosine | int8_rescore | m=16, ef_construct=200, ef_search=64 |
| `omega_vec_nomic_768` | 768 | Nomic Embed Text v1.5 (Ollama) | cosine | int8_rescore | m=16, ef_construct=200, ef_search=64 |
| `omega_vec_nomic_512` | 512 | Nomic MRL truncation | cosine | int8_rescore | m=16, ef_construct=200, ef_search=64 |
| `omega_vec_nomic_256` | 256 | Nomic MRL truncation | cosine | int8_rescore | m=16, ef_construct=200, ef_search=64 |
| `omega_vec_minilm_384` | 384 | MiniLM L6 v2 (native) | cosine | none | m=16, ef_construct=200, ef_search=64 |
| `omega_vec_static_64` | 64 | Potion Base 2M (model2vec) | cosine | none | m=16, ef_construct=200, ef_search=64 |
| `omega_vec_library_256` | 256 | Library/discovery embeddings | cosine | none | m=16, ef_construct=200, ef_search=64 |

**Canonical Dimension Lock**: 768-dim enforced at vec0 table creation (M23 Failure Integrity) — `sqlite_vec_adapter.py:280-288`

**Embedding Fallback Chain** (EmbeddingManager):
1. `GemmaGGUFEmbeddingProvider` (768-dim, primary) — `embeddings.py:400`
2. `OllamaEmbeddingProvider` (nomic-embed-text:v1.5, 768-dim) — `embeddings.py:401`
3. `LocalGGUFEmbeddingProvider` (MiniLM, 384-dim native → MRL to 768) — `embeddings.py:402`
4. `StaticEmbeddingProvider` (potion-base-2M, 64-dim native → MRL to 768) — `embeddings.py:403`

---

## §4 Hybrid Search (RRF Fusion)

**Module**: `src/omega/memory/hybrid_search.py`

- FTS5 (BM25) + vector (cosine) results fused via **Reciprocal Rank Fusion, k=60**.
- Single source of truth: `HybridSearchEngine` class.
- Used by both `MemoryStore.search()` and `SQLiteVecAdapter.hybrid_search()` via `fetch_and_fuse()`.
- 20 contract tests + 8 RRF math vectors.

---

## §5 GraphRAG (Native on SQLite)

GraphRAG is implemented **natively on SQLite** — entity nodes and relation edges
are SQL rows. No external graph database. This keeps the entire memory subsystem
within a single portable file, aligned with the local-first, zero-telemetry mandates.

---

## §6 Redis Task Canvas (Optional Hot Tier)

A Redis-backed task canvas MAY be used for the hot in-memory tier (fast ephemeral
task state). Redis is **optional** — the engine degrades to file-backed queues per
M12 (Queue Integrity, advisory). Never a hard dependency.

---

## §7 Qdrant as Optional WAD Adapter

**Qdrant is NOT a core dependency.** It implements `IVectorStoreAdapter` for stacks
that opt into external vector infrastructure (e.g., multi-node clusters, >100M vectors).

### Migration Strategy: Adapter Swap (Not Replacement)

1. **Implement `QdrantAdapter`** as a full `IVectorStoreAdapter` implementation (revive from heritage ref)
2. **Add config toggle** in `config/jit_rag.yaml`:
   ```yaml
   vector_store:
     type: qdrant | sqlite_vec
   ```
3. **Migrate primary collection first** (`omega_vec_gemma_768` — canonical 768-dim)
4. **Parity test per collection** (≥95% recall vs sqlite-vec)
5. **Keep SQLite-vec as hot standby** for 30-day rollback window

### Qdrant Collection Schema (When Enabled)

| Collection | Dimensions | Purpose | Quantization |
|------------|------------|---------|--------------|
| `omega_entities` | 768 | Entity embeddings | Scalar int8 |
| `omega_sessions` | 768 | Session/context embeddings | Scalar int8 |
| `omega_knowledge` | 768 | Research/knowledge base | Scalar int8 |
| `omega_code` | 768 | Code embeddings | Scalar int8 |

**HNSW Config**: m=16, ef_construct=256, ef_search=128, max_indexing_threads=4
**Quantization**: Scalar int8, quantile=0.99, always_ram=true (4x memory savings, <1% recall loss)
**Payload Indexes**: entity_name, session_id, type, timestamp, tags, source (KEYWORD)

### Multi-Entity Isolation

Single collection + payload partitioning (not per-entity collections). Payload filtering integrates with HNSW traversal (pre-filtering). Every query includes entity filter:

```python
query_filter = models.Filter(
    must=[
        models.FieldCondition(key="entity_name", match=models.MatchValue(value="researcher")),
        models.FieldCondition(key="type", match=models.MatchValue(value="knowledge")),
    ]
)
```

---

## §8 Mandatory Spatial Coordinates (Godot 4 OpenXR Readiness)

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

*⬡ OMEGA ⬡ KALI ⬡ 2026-08-16*
