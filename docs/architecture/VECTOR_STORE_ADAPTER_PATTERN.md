---
schema_version: "1.0"
document_type: architecture
document_id: vector-store-adapter-pattern
title: Vector Store Adapter Pattern
status: ACTIVE
version: "1.0.0"
date: "2026-08-16"
owner: kali
tags: [vector-store, adapter-pattern, sqlite-vec, qdrant, m2-firewall, ivectorstoreadapter]
priority: P1
depends_on: []
blocks: []
acceptance_gates:
  - "IVectorStoreAdapter ABC documented with all methods"
  - "3 implementations documented (SQLiteVecAdapter, MemoryVectorAdapter, QdrantAdapter)"
  - "Engine-Stack Firewall (M2) compliance explained"
  - "Migration strategy: adapter swap with config toggle"
cross_references:
  - src/omega/memory/vector_adapters.py
  - src/omega/memory/sqlite_vec_adapter.py
  - docs/architecture/MEMORY_SUBSYSTEM_DESIGN.md
  - OMEGA_ENGINE.md
llm_metadata:
  token_budget: 2500
  chunk_strategy: section_per_topic
  answer_first_sections: true
  self_contained_code: true
---

# 🔱 Vector Store Adapter Pattern

**AP Token**: `AP-VECTOR-ADAPTER-PATTERN-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ 2026-08-16

---

## §1 Purpose

The **Vector Store Adapter Pattern** ensures the Omega Engine remains **DB-agnostic for semantic memory** — a direct enforcement of **Mandate 2 (Engine-Stack Firewall)**. The core engine must never depend on a specific vector database (Qdrant, FAISS, PostgreSQL, etc.). Instead, vector stores are swappable backends implementing a common interface.

---

## §2 The Interface: IVectorStoreAdapter

**Module**: `src/omega/memory/vector_adapters.py`

```python
class IVectorStoreAdapter(ABC):
    """Abstract base class for vector store adapters.
    
    Ensures the Omega Engine remains DB-agnostic for semantic memory.
    """
    
    @abstractmethod
    async def upsert(
        self, 
        entity_name: str, 
        vector: List[float], 
        metadata: Dict[str, Any], 
        id: Optional[str] = None
    ) -> str:
        """Insert or update a vector and its metadata."""
        pass
    
    @abstractmethod
    async def query(
        self, 
        entity_name: str, 
        vector: List[float], 
        limit: int = 10, 
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[float, Dict[str, Any]]]:
        """Query the vector store for the most similar entries."""
        pass
    
    @abstractmethod
    async def delete(self, entity_name: str, ids: List[str]) -> bool:
        """Delete specific vectors by ID."""
        pass
    
    async def delete_session(self, entity_name: str, session_id: str) -> bool:
        """Delete all vectors associated with a specific session.
        
        Default implementation returns False. Subclasses should override.
        """
        return False
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Get the current health and status of the vector store."""
        pass
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **`entity_name` as first param** | Mandatory sovereign isolation — every operation scoped to entity |
| **`metadata` dict** | Flexible payload for directives, tags, timestamps, spatial coords |
| **`filter` dict** | Additional query-time filters (session_id, type, tags) |
| **Returns `Tuple[float, Dict]`** | Score + payload — simple, no vendor-specific types |
| **Async throughout** | M1 AnyIO compliance — no blocking I/O |

---

## §3 Implementations

### 3.1 SQLiteVecAdapter — Core Unified Fabric ✅

**Module**: `src/omega/memory/sqlite_vec_adapter.py`
**Status**: Primary production backend

**Architecture**: 7 per-model vec0 collections + FTS5 BM25 + RRF fusion (k=60)

| Collection | Dimension | Model | Purpose |
|------------|-----------|-------|---------|
| `omega_vec_gemma_768` | 768 | EmbeddingGemma 300M | Primary canonical |
| `omega_vec_nomic_768` | 768 | Nomic Embed Text v1.5 | Cloud fallback |
| `omega_vec_nomic_512` | 512 | Nomic MRL truncation | Reduced dim |
| `omega_vec_nomic_256` | 256 | Nomic MRL truncation | Reduced dim |
| `omega_vec_minilm_384` | 384 | MiniLM L6 v2 | Fast local |
| `omega_vec_static_64` | 64 | Potion Base 2M | Ultra-fast |
| `omega_vec_library_256` | 256 | Library/discovery | Specialized |

**Hybrid Search**: `HybridSearchEngine` fuses FTS5 (BM25) + vec0 (cosine) via RRF k=60. Single source of truth in `hybrid_search.py`.

**PRAGMA SSOT**: cache_size=32MB, wal_autocheckpoint=500, journal_mode=WAL, synchronous=NORMAL

---

### 3.2 MemoryVectorAdapter — Sovereign Fallback ✅

**Module**: `src/omega/memory/vector_adapters.py` (lines 60-150)
**Status**: Zero-dependency fallback

**Implementation**: In-memory cosine similarity. Used when:
- External vector stores unavailable
- Testing (`OMEGA_ENV=test`)
- Bootstrapping before external store ready

**Guarantees**: Zero external dependencies. Pure Python. Sovereign fallback per M23 (Failure Integrity).

---

### 3.3 QdrantAdapter — Optional WAD Adapter ⚠️

**Module**: `src/omega/memory/vector_adapters.py` (lines 155-350)
**Status**: **Deprecated heritage reference only**

**Current State**: Retained for reference. Marked with:
```python
# DEPRECATED: QdrantAdapter retained for heritage reference only.
# [heritage: qdrant-2021] Vector database — Qdrant implementation.
# Use SQLiteVecAdapter for unified fabric (D225).
```

**Revival Required For Production Use**:
1. Update to modern `qdrant-client` async API (gRPC preferred)
2. Implement scalar int8 quantization config
3. Add payload indexes for entity_name, session_id, type, timestamp, tags, source
4. Implement hybrid search via Qdrant native RRF (prefetch + FusionQuery)
5. Add connection pooling (pool_size=20) and retry policy
6. Remove `DEPRECATED` marker and heritage comment

---

## §4 Configuration: The Adapter Toggle

**File**: `config/jit_rag.yaml` (to be created)

```yaml
vector_store:
  type: sqlite_vec | qdrant
  # SQLite-vec config (when type: sqlite_vec)
  sqlite_vec:
    db_path: "data/knowledge/vec.db"
    pragma:
      cache_size: 32768
      wal_autocheckpoint: 500
  
  # Qdrant config (when type: qdrant)
  qdrant:
    host: "127.0.0.1"
    port: 6333
    grpc_port: 6334
    api_key_env: "QDRANT_API_KEY"
    prefer_grpc: true
    pool_size: 20
    timeout: 30.0
    collections:
      entities: "omega_entities"
      sessions: "omega_sessions"
      knowledge: "omega_knowledge"
      code: "omega_code"
    quantization:
      enabled: true
      type: "int8"
      quantile: 0.99
      always_ram: true
```

**Runtime Resolution** (in `MemoryStore` or `EmbeddingManager`):
```python
def get_vector_adapter(config: JitRagConfig) -> IVectorStoreAdapter:
    if config.vector_store.type == "qdrant":
        return QdrantAdapter(config.vector_store.qdrant)
    return SQLiteVecAdapter(config.vector_store.sqlite_vec)
```

---

## §5 Migration Strategy: Adapter Swap (Not Replacement)

### Current Reality
- **SQLiteVecAdapter IS the unified fabric** — working in production
- **QdrantAdapter is DEPRECATED** — heritage reference only
- **Engine-Stack Firewall (M2)** demands swappable adapters

### Correct Migration Path

```
Phase 0: Fix L3 query bug + create config/jit_rag.yaml + vectorize DPO pairs
    ↓
Phase 1: Implement QdrantAdapter as full IVectorStoreAdapter
    ↓
Phase 2: Deploy Qdrant via Podman quadlet (6GB limit, 80% CPU)
    ↓
Phase 3: Add config toggle (vector_store.type: qdrant|sqlite_vec)
    ↓
Phase 4: Migrate primary collection (omega_vec_gemma_768) first
    ↓
Phase 5: Parity test per collection (≥95% recall)
    ↓
Phase 6: Keep SQLite-vec as hot standby for 30 days
```

### What NOT To Do
- ❌ Wholesale replacement of sqlite-vec with Qdrant
- ❌ Remove SQLiteVecAdapter
- ❌ Hard-code Qdrant in core engine paths
- ❌ Create 5-collection schema that doesn't match per-model architecture

---

## §6 Omega-Specific Payload Conventions

All adapters MUST include these payload fields for sovereign operations:

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `entity_name` | str | ✅ | Sovereign isolation filter |
| `session_id` | str | ✅ | Session-scoped retrieval |
| `type` | str | ✅ | knowledge\|session\|code\|directive\|dpo_pair |
| `timestamp` | datetime | ✅ | Temporal ordering |
| `tags` | List[str] | ⭕ | Categorical filtering |
| `source` | str | ⭕ | web\|local\|generated\|legacy |
| `pos_x/y/z` | float | ✅ | Spatial memory (Godot 4) |
| `_type` | str | ⭕ | soul_directive\|l3_gnosis\|dpo_pair\|memory_block |

### Special Payload Types

**Soul Directives**:
```python
{
    "_type": "soul_directive",
    "entity_name": "kali",
    "directive_id": "d-kal-001",
    "priority": "CRITICAL",
    "mandate_binding": ["M5", "M11"],
    "content": "No session may close without distillation..."
}
```

**L3 Gnosis Principles**:
```python
{
    "_type": "l3_gnosis",
    "entity_name": "kali",
    "principle_id": "L3-Principle-001",
    "confidence": 0.98,
    "content": "Anticipatory Forensics: The most valuable output..."
}
```

**DPO Pairs**:
```python
{
    "_type": "dpo_pair",
    "failure_mode_tag": "instructional_comment_contamination",
    "lineage_id": "f821-remediation-001",
    "reward_source": "opus_hybrid_synthesis",
    "prompt": "Fix this situation: ...",
    "chosen": "Correct response...",
    "rejected": "Naive response..."
}
```

---

## §7 Testing Requirements

Every `IVectorStoreAdapter` implementation MUST pass:

| Test | Description |
|------|-------------|
| `test_upsert_retrieval` | Upsert → query returns same vector |
| `test_entity_isolation` | Entity A cannot see Entity B's vectors |
| `test_filter_by_session` | Session filter works |
| `test_delete_by_id` | Delete removes specific vectors |
| `test_delete_session` | Delete removes all session vectors |
| `test_hybrid_search` | FTS5 + vector fusion works (if supported) |
| `test_parity_vs_sqlite_vec` | ≥95% recall parity (for Qdrant) |
| `test_concurrent_upsert` | Thread-safe under load |

---

## §8 Quick Reference

| Question | Answer |
|----------|--------|
| **Core vector store?** | sqlite-vec (7 per-model collections + FTS5 + RRF) |
| **Qdrant status?** | Optional WAD adapter — implements `IVectorStoreAdapter` |
| **Adapter interface?** | `IVectorStoreAdapter` in `vector_adapters.py` |
| **Config toggle?** | `config/jit_rag.yaml` → `vector_store.type` |
| **Entity isolation?** | Mandatory — `entity_name` filter on every query |
| **Migration strategy?** | Adapter swap with config toggle, not replacement |
| **Fallback?** | `MemoryVectorAdapter` — zero dependencies |

---

*⬡ OMEGA ⬡ KALI ⬡ 2026-08-16*
