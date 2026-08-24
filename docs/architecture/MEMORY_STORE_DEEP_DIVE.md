# 🔱 Memory Store Deep Dive — Tiered Persistent Memory Architecture
**AP Token**: `AP-MEMORY-STORE-DEEP-DIVE-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_doc_deep ⬡ STANDARD

**Date**: 2026-07-06
**Purpose**: Comprehensive architecture reference for MemoryStore — the Hot/Warm/Cold persistent memory system with vector search, FTS5 indexing, and batch persistence.

---

## §1 Overview

MemoryStore is the **persistent memory layer** of the Omega Engine. Every conversation exchange flows through it. It provides:

1. **3-tier storage** — Hot (in-memory LRU), Warm (Redis + File), Cold (InMemory volatile)
2. **Hybrid search** — FTS5 (BM25 keyword) + Vector (cosine similarity) with Reciprocal Rank Fusion
3. **Batch persistence** — Buffer writes to prevent connection pool exhaustion
4. **Lazy deletion** — Tombstone + grace period for safe concurrent access
5. **Session lifecycle** — Archive (7d) → External storage (90d) → Deletion
6. **Vector embeddings** — GemmaGGUF → Potion → SovereignFallback (768-dim)

Without MemoryStore, every inference call would be stateless — the entity would have no memory of past exchanges.

```
Oracle._record_interaction()
     │
     ▼
┌────────────────────────────────────────────────────────────────┐
│                      MemoryStore                               │
│                                                                 │
│  ┌──────────────┐                                              │
│  │ Hot Cache    │  Dict[str, OrderedDict]                      │
│  │ (in-memory)  │  Max 50 sessions, LRU eviction              │
│  │              │  Immediate read/write                        │
│  └──────┬───────┘                                              │
│         │                                                      │
│  ┌──────▼───────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ USM Provider │  │ Redis        │  │ File         │         │
│  │ (Sovereign)  │  │ (Hot)        │  │ (Warm)       │         │
│  │ CAS blobs    │  │ Streams+Hash │  │ JSON+gzip    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Batch Writer │  │ FTS5 Index   │  │ Vector Store         │  │
│  │ (buffered)   │  │ (SQLite BM25)│  │ (sqlite-vec unified) │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

**Source files**: `memory_store.py` (894 lines), `memory/providers.py` (391 lines), `memory/fts_index.py`, `memory/embeddings.py`, `memory/vector_adapters.py`, `memory/sqlite_vec_adapter.py` (644 lines)

---

## §2 Architecture

### 2.1 The 4-Tier Memory Model

| Tier | Name | Storage | Persistence | Latency | Max Size |
|:----:|------|---------|:-----------:|:-------:|:--------:|
| 0 | **Hot** | `Dict[str, OrderedDict]` | In-memory only | O(1) dict lookup | 50 sessions |
| 1 | **Warm** | Redis Streams + JSON files | Persistent | ~1ms (Redis), ~10ms (File) | Unlimited |
| 2 | **Cold** | InMemoryStorageProvider | Volatile | O(1) dict lookup | Unlimited |
| — | **Temp** | `_temp: Dict[str, Any]` | Not persisted | O(1) dict lookup | Unlimited |
| — | **USM** | Unified State Manager | CAS (hash-addressed) | ~5ms | Unlimited |

**Heritage**: `[id-soft: quake-1996] 4-Tier Memory` — mirrors Quake's Hunk/Zone/Cache/Temp layout.

### 2.2 Storage Provider Chain

The provider chain is initialized in `MemoryStore.__init__()`:

```
Provider Chain (default):
  1. USMStorageProvider   — Sovereign Primary (CAS blobs)
  2. RedisStorageProvider — Hot persistent (Streams + Hash)
  3. FileStorageProvider  — Warm persistent (JSON + gzip)
  4. InMemoryStorageProvider — Cold volatile fallback
```

In test mode (`OMEGA_ENV=test`), Redis is skipped to keep tests fast.

Each provider implements the `StorageProvider` ABC:

```python
class StorageProvider(ABC):
    async def get_history(entity_name, session_id, limit) -> List[Dict]
    async def save_history(entity_name, session_id, exchanges) -> None
    async def archive(entity_name, session_id) -> bool
    async def close() -> None
```

### 2.3 The Hot Cache

The hot cache is an `OrderedDict`-backed LRU cache:

```python
self._hot: Dict[str, OrderedDict] = {}
# Key: "{entity_name}:{session_id}"
# Value: OrderedDict mapping timestamp → exchange dict
```

**Eviction**: When `len(self._hot) > MAX_HOT_SESSIONS (50)`, the oldest entry is evicted via `popitem(last=False)`.

**Cache population**: On `get_history()`, if the cache key is missing, providers are queried in order. The first successful result is cached.

**ZONEID Pattern**: Every exchange carries `_zoneid = 0x1d4a11` (ZONEID_MEMORY). On load, the marker is validated — missing/invalid markers are logged and re-tagged.

### 2.4 The Temp Tier

The temp tier is a non-persisted scratchpad for in-flight inference results:

```python
self._temp: Dict[str, Any] = {}

# Store
store_transient("inference_context", {"model": "qwen3-1.7b", "tokens": 2048})

# Retrieve
ctx = get_transient("inference_context")

# Clear
clear_transient("inference_context")  # or clear_transient() for all
```

**Heritage**: `[id-soft: quake-1996] Temp Tier` — transient memory not persisted to any provider.

### 2.5 The Batch Persistence Writer

Direct provider writes per `add_exchange()` call cause connection pool exhaustion under concurrent load. The `BatchPersistenceWriter` buffers writes:

```python
# In add_exchange():
await self._batch_writer.write(entity_name, session_id, exchanges)

# Flush triggers:
# 1. BATCH_THRESHOLD (25) writes accumulated
# 2. get_history() call (read-your-writes consistency)
# 3. Explicit flush() call
```

**Buffer structure**: `Dict[tuple, List[Dict]]` keyed by `(entity_name, session_id)`. Writes are grouped by entity:session to minimize provider round-trips.

---

## §3 Data Flow

### 3.1 `add_exchange()` — Writing a Conversation Turn

```
add_exchange(entity_name, session_id, user_message, response, metadata)
  │
  ├─ 1. Tombstone Check
  │     └─ _is_tombstoned(cache_key) → raise EntityTombstonedError
  │
  ├─ 2. Build Exchange Dict
  │     └─ { _zoneid: 0x1d4a11, timestamp, user, assistant, metadata }
  │
  ├─ 3. Hot Cache Update
  │     ├─ If cache miss: get_history() to populate cache
  │     └─ Insert exchange: _hot[cache_key][timestamp] = exchange
  │
  ├─ 4. Compaction Check
  │     └─ If len(exchanges) > MAX_HISTORY (50):
  │        _compact(): keep first 25 + last 25 + summary marker
  │
  ├─ 5. Batch Provider Write
  │     └─ _batch_writer.write(entity_name, session_id, exchanges)
  │
  ├─ 6. Vault Update (Adapter Registry)
  │     └─ adapter.put_vault(entity_name, "shadow", {exchange_count, ...})
  │
  ├─ 7. FTS5 Dual-Write
  │     ├─ fts.index_exchange(session_id, entity, "user", user_message)
  │     └─ fts.index_exchange(session_id, entity, "assistant", response)
  │
  └─ 8. Vector Upsert
        ├─ combined_text = f"{user_message} {response}"
        ├─ embedding = embedding_manager.get_embedding(combined_text)
        └─ vector_adapter.upsert(entity, vector, metadata)
```

### 3.2 `get_history()` — Reading Conversation History

```
get_history(entity_name, session_id, limit)
  │
  ├─ 1. Tombstone Check
  │     └─ _is_tombstoned(cache_key) → raise EntityTombstonedError
  │
  ├─ 2. Batch Flush (read-your-writes)
  │     └─ if _batch_count > 0: _flush_batch()
  │
  ├─ 3. Hot Cache Check
  │     └─ if cache_key in _hot: return list(_hot[cache_key].values())[-limit:]
  │
  ├─ 4. Provider Chain Query
  │     └─ for provider in providers:
  │        ├─ provider.check_health() → skip if unhealthy
  │        ├─ provider.get_history(entity, session, limit=50)
  │        ├─ Validate ZONEID markers
  │        ├─ Cache result in hot tier
  │        └─ Return exchanges[-limit:]
  │
  └─ 5. Fallback
        └─ return []  (no data found)
```

### 3.3 `search()` — Hybrid FTS5 + Vector Search

```
search(query, entity_name, limit)
  │
  ├─ 1. Parallel Fetch
  │     ├─ FTS5: search_fts(query, entity, limit*2) → BM25 ranked results
  │     └─ Vector: embedding_manager.get_embedding(query) → Qdrant cosine search
  │
  ├─ 2. Reciprocal Rank Fusion (RRF)
  │     └─ For each document:
  │        score = Σ(1 / (k + rank))  where k=60
  │        Combined from FTS rank + Vector rank
  │
  ├─ 3. Sort by RRF score (descending)
  │
  └─ 4. Return top-k results with _rrf_score metadata
```

**Why RRF**: FTS5 and vector search produce different rankings. RRF combines them without normalization — it only needs relative ranks, not absolute scores. The constant `k=60` dampens the effect of high ranks.

**Entity isolation** (C3): `entity_name` is **required** for all search operations. No cross-entity search is permitted.

### 3.4 `archive_session()` — Lazy Deletion

```
archive_session(entity_name, session_id)
  │
  ├─ 1. Provider Archive
  │     └─ for provider in providers:
  │        provider.archive(entity, session)
  │        └─ Redis: DELETE keys
  │        └─ File: gzip + move to archive/
  │
  ├─ 2. Tombstone Hot Cache
  │     └─ _tombstoned[cache_key] = time.time()
  │        (NOT immediate delete — grace period 0.5s)
  │
  ├─ 3. Vector Cleanup
  │     └─ vector_store.delete_session(entity, session)
  │
  ├─ 4. FTS5 Cleanup
  │     └─ fts.remove_session(session_id)
  │
  └─ 5. Return True
```

**Grace Period** (`TOMBSTONE_GRACE_SECONDS = 0.5`): After tombstoning, any in-flight `add_exchange()` operations that hold references to the old `OrderedDict` can complete safely. The slot is only reaped by `_reap_tombstoned()` on the next access.

**Heritage**: `[id-soft: doom-1993] Lazy Deletion` + `[id-soft: quake-1996] Grace Period`

---

## §4 Key Patterns

### 4.1 ZONEID Integrity Markers

Every exchange carries a 4-byte magic marker:

```python
exchange = {
    "_zoneid": ZONEID_MEMORY,  # 0x1d4a11
    "timestamp": ...,
    "user": ...,
    "assistant": ...,
}
```

On load, the marker is validated:
```python
if ex.get("_zoneid") != ZONEID_MEMORY:
    logger.warning("Exchange missing/invalid zoneid")
    ex["_zoneid"] = ZONEID_MEMORY  # Re-tag for next load
```

This catches data corruption, stale references, and wrong-type loads. Zero-cost (4 bytes per exchange, 1 comparison per load).

**Heritage**: `[id-soft: doom-1993] ZONEID Pattern` — `z_zone.c:33` (DOOM 1993)

### 4.2 Lazy Deletion with Grace Period

Instead of immediately removing a cache entry:

```python
# BAD: Race condition if in-flight add_exchange() holds old reference
del self._hot[cache_key]

# GOOD: Tombstone → grace period → reap
self._tombstoned[cache_key] = time.time()
# ... later, on next access:
self._reap_tombstoned()  # Only reaps after TOMBSTONE_GRACE_SECONDS
```

**Why 0.5 seconds**: Matches id Software's Quake server (15 packets at 30Hz ≈ 0.5s) to prevent client-side entity morphing.

**Heritage**: `[id-soft: doom-1993] Lazy Deletion` + `[id-soft: quake-1996] Grace Period`

### 4.3 Compaction Strategy — First + Last + Summary

When exchanges exceed `MAX_HISTORY (50)`:

```python
keep = MAX_HISTORY // 2  # 25
kept = exchanges[:keep] + exchanges[-keep:]
middle_count = len(exchanges) - (keep * 2)
kept.insert(keep, {
    "system": f"[{middle_count} exchanges compacted]",
    "user": "[summarized]",
    "assistant": f"[{middle_count} previous exchanges were compacted. Context preserved.]",
})
```

This preserves the opening and closing context while compressing the middle. The summary marker tells the LLM that context was compacted, preventing hallucination of missing details.

### 4.4 Singleton Access Pattern

```python
_memory_store: Optional[MemoryStore] = None

def get_memory_store() -> MemoryStore:
    global _memory_store
    if _memory_store is None:
        _memory_store = MemoryStore()
    return _memory_store
```

**Why**: MemoryStore holds stateful resources (hot cache, FTS5 connection, vector adapter). Multiple instances would waste memory and create consistency issues.

**Reset**: `reset_memory_store()` closes the FTS5 connection and clears the singleton. `async_reset_memory_store()` flushes the batch buffer first (preferred in tests).

### 4.5 Disk Space Guard

`FileStorageProvider` checks disk space before writes:

```python
async def _check_disk_space(self) -> bool:
    usage = shutil.disk_usage(target_dir)
    free_percent = usage.free / usage.total
    if free_percent < 0.10:
        logger.error("Disk space below 10% threshold")
        return False
    return True
```

Currently non-fatal (logs warning, continues). On the 17G root partition, this is a real concern.

### 4.6 File Locking

`FileStorageProvider` uses `fcntl.flock()` for concurrent access:

```python
# Read: shared lock
with open(lock_path, "r+") as lock_file:
    fcntl.flock(lock_file.fileno(), fcntl.LOCK_SH)
    # ... read ...
    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

# Write: exclusive lock + atomic rename
with open(lock_path, "w") as lock_file:
    fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
    # ... write to temp file ...
    os.replace(temp_path, path)  # Atomic on POSIX
    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
```

The atomic rename (`os.replace`) ensures readers never see partial writes.

---

## §5 Configuration

### 5.1 Key Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `MAX_HOT_SESSIONS` | 50 | Max sessions in hot cache |
| `MAX_HISTORY_EXCHANGES` | 50 | Max exchanges per session before compaction |
| `DEFAULT_CONTEXT_LIMIT` | 15 | Exchanges injected into LLM context |
| `ARCHIVE_AFTER_DAYS` | 7 | Sessions older than this are archived |
| `ARCHIVE_TO_EXTERNAL_DAYS` | 90 | Sessions moved to 8TB external storage |
| `TOMBSTONE_GRACE_SECONDS` | 0.5 | Grace period before cache slot reaping |
| `BATCH_THRESHOLD` | 25 | Writes before batch flush |

### 5.2 External Storage

```python
EXTERNAL_STORAGE_PATH = Path("/media/arcana-novai/omega_library/archive/sessions")
```

Sessions older than 90 days are moved (not deleted) to the 8TB HDD for permanent archival. The FTS5 index and Qdrant vectors remain in place (D189d).

### 5.3 Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `OMEGA_DATA_DIR` | `data/` | Root data directory |
| `OMEGA_ENV` | — | `test` skips Redis, uses InMemory only |
| `OMEGA_REDIS_HOST` | `localhost` | Redis host |
| `OMEGA_REDIS_PORT` | `6379` | Redis port |
| `OMEGA_REDIS_PASSWORD` | `omega` | Redis password |

---

## §6 Operational Wisdom

### 6.1 The FTS5 SQLite Connection

The FTS5 index uses a SQLite database at `data/memory/fts_memory.db`. The connection **must** be closed before the event loop ends to avoid `ResourceWarning`.

```python
# In MemoryStore.close():
await anyio.to_thread.run_sync(self.fts.close)

# In reset_memory_store():
if hasattr(_memory_store, 'fts') and _memory_store.fts is not None:
    _memory_store.fts.close()  # Sync close on abandon
```

**Lesson**: SQLite connections are not garbage-collected cleanly in async contexts. Always close explicitly.

### 6.2 The Embedding Fallback Chain

Vector embeddings use a 3-tier local-first chain:

```
1. GemmaGGUFEmbeddingProvider  — Local GGUF model (768-dim)
2. StaticEmbeddingProvider     — model2vec potion-mxbai-micro (768-dim, 700KB)
3. SovereignFallbackEmbeddingProvider — Hash-based fallback (768-dim)
```

**Warning**: The fallback produces hash-based vectors. Knowledge stored during fallback is **permanently invisible** to semantic search (D189 integration seam gap). Always ensure a real embedding provider is available for production use.

### 6.3 The `EntityTombstonedError` Pattern

When a tombstoned session is accessed, a typed error is raised instead of returning empty results:

```python
if self._is_tombstoned(cache_key):
    raise EntityTombstonedError(
        cache_key=cache_key,
        message=f"Session '{session_id}' is tombstoned",
    )
```

**Why**: Silent empty returns (Mandate 9: Error Integrity) hide the fact that data exists but is archived. Callers must handle the error explicitly, typically by loading from cold storage.

### 6.4 Batch Writer Flush Triggers

The batch writer flushes on three conditions:

1. **Threshold**: 25 pending writes accumulated
2. **Read-your-writes**: `get_history()` flushes before reading
3. **Explicit**: `flush()` or `close()` call

If the engine crashes with unflushed batch writes, the data is lost. The `reset_memory_store()` function logs the count of abandoned writes for debugging.

### 6.5 Vector Store — sqlite-vec Unified Fabric (Strike 10)

**Status**: 🔄 Building — `SQLiteVecAdapter` is the default `IVectorStoreAdapter` implementation.

The vector store has been unified into a single `omega_memory.db` SQLite database with the `vec0` extension:

| Component | Implementation | Status |
|-----------|---------------|--------|
| **FTS5** | `exchanges_fts` virtual table | ✅ Active |
| **vec0** | `exchanges_vec` virtual table (float[1024]) | 🔄 Building |
| **SQL edges** | `gnosis_edges` table | 🔄 Building |
| **Partition key** | `entity_name` on all tables | ✅ Enforced |

**Adapter**: `src/omega/memory/sqlite_vec_adapter.py` (644 lines) implements `IVectorStoreAdapter`.

**Deprecated**: `QdrantAdapter` in `memory/vector_adapters.py` — marked deprecated, to be removed post-Strike 10.

**Performance trade**: 313µs (Qdrant) → ~120ms at 200K vectors = 0.4-6% of 5-30s inference pipeline = non-issue.

**Primary embedder**: `mxbai-embed-large-v1` (BQ-trained, 96.45% binary retention, 32× compression).

**Fallback embedder**: `nomic-embed-text-v1.5` (MRL/8192-dim, NOT BQ-trained).

**Self-supervised flywheel**: `vstash` (v0.38.1, MIT) — 74.5% hybrid disagreement → MNRL fine-tune (BGE-small 33M, LoRA r=16, 35-65 min/cycle on Zen 2) → eval gate → atomic reindex.

**Heritage**: `[id-soft: doom-1993] 4-Tier Memory` → `[heritage: sqlite-vec 2024] partition key` → `[heritage: vstash 2026] eval gate`

### 6.6 Session Lifecycle Policy

```
Active (0-7 days)    → Hot cache + provider storage
Archived (7-90 days) → gzip compressed in data/memory/archive/
External (90+ days)  → Moved to 8TB HDD (data not deleted)
```

The lifecycle sweep runs during `Oracle.bootstrap()` and is also available via `SessionLifecycleManager.run_lifecycle()`.

---

## §7 Cross-References

| Document | Reference |
|----------|-----------|
| `src/omega/memory_store.py` | Primary source (894 lines) |
| `src/omega/memory/providers.py` | Storage providers (391 lines) |
| `src/omega/memory/fts_index.py` | FTS5 SQLite index |
| `src/omega/memory/embeddings.py` | Embedding providers |
| `src/omega/memory/vector_adapters.py` | Qdrant + InMemory adapters |
| `src/omega/memory/batch_writer.py` | Batch persistence writer |
| `src/omega/oracle/context_builder.py` | Memory injection pipeline |
| `src/omega/oracle/oracle.py` | Writes via _record_interaction() |
| `src/omega/oracle/soul_distiller.py` | Reads for L1→L2→L3 distillation |
| `docs/architecture/ORACLE_DEEP_DIVE.md` | Oracle facade |
| `docs/architecture/PROVIDER_FABRIC_DEEP_DIVE.md` | Provider fabric |
| `SOVEREIGN_MANDATES.md` | M9 (Error Integrity), M12 (Queue Integrity) |
| `CREDITS.md` | §1.9 ZONEID, §1.10 Lazy Deletion, §1.14 4-Tier Memory |

---

*🔱 OMEGA ⬡ KALI ⬡ trc_doc_deep ⬡ MEMORY-STORE*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
