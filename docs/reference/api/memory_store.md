# API Reference: Memory Store

> MemoryStore — Hot/Warm/Cold entity memory with LRU caching and 3-tier provider fallback.

---

## MemoryStore

**File**: `src/omega/memory_store.py`

The central persistence layer for all entity interactions. It manages the lifecycle of session history, from high-speed volatile cache (Hot) to persistent disk storage (Warm) and long-term vector embeddings (Cold).

### Constructor

```python
MemoryStore(
    providers: Optional[List[StorageProvider]] = None, 
    vector_store: Optional[IVectorStoreAdapter] = None, 
    embedding_manager: Optional[EmbeddingManager] = None, 
    adapter_registry: Optional[MemoryAdapterRegistry] = None
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `providers` | `Optional[List[StorageProvider]]` | `None` | List of storage providers. If `None`, initializes default chain: Redis (Hot) $\rightarrow$ File (Warm) $\rightarrow$ InMemory (Cold). |
| `vector_store` | `Optional[IVectorStoreAdapter]` | `None` | Adapter for vector database (e.g., Qdrant). |
| `embedding_manager` | `Optional[EmbeddingManager]` | `None` | Manager for generating and caching embeddings. |
| `adapter_registry` | `Optional[MemoryAdapterRegistry]` | `None` | Registry for memory adapters. |

---

### Methods

#### `await add_exchange(entity_name: str, session_id: str, user_query: str, response_text: str, metadata: Dict[str, Any] = None) -> None`

Persists a single interaction exchange. Uses **Batch Persistence** to buffer writes and prevent connection pool exhaustion.

```python
await memory_store.add_exchange(
    entity_name="Prometheus",
    session_id="ses_123",
    user_query="What is sovereignty?",
    response_text="Sovereignty is the ability to...",
    metadata={"tokens": 450, "latency": 1.2}
)
```

#### `await get_history(entity_name: str, session_id: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]`

Retrieves the conversation history for a specific session. Triggers a `_flush_batch()` call to ensure "read-your-writes" consistency.

**Returns**: `List[Dict[str, Any]]` — a list of interaction exchanges.

#### `await search(query: str, entity_name: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]`

Performs a hybrid search across both Full-Text Search (FTS) and Vector embeddings.

```python
results = await memory_store.search("How do I harden containers?", entity_name="Prometheus")
```

**Returns**: `List[Dict[str, Any]]` — ranked search results.

#### `await archive_session(entity_name: str, session_id: str) -> bool`

Tombstones a session in the hot cache and flushes it to the warm/cold providers. Implements a `0.5s` grace period before full removal.

**Returns**: `bool`

#### `await archive_old_sessions(older_than_days: int = 7) -> int`

Scans all sessions and archives those older than the threshold.

**Returns**: `int` — number of sessions archived.

#### `await move_to_external_storage(older_than_days: int = 30) -> int`

Moves extremely old sessions from the local warm store to external long-term storage.

**Returns**: `int` — number of sessions moved.

#### `store_transient(key: str, value: Any) -> None`

Stores data in the **Temp Tier** (volatile scratchpad). Data is not persisted to disk and is cleared on restart.

#### `get_transient(key: str) -> Optional[Any]`

Retrieves data from the Temp Tier.

---

## Memory Architecture

### 3-Tier Storage Hierarchy
The `MemoryStore` uses a fallback chain to balance latency and durability:

1. **Hot Tier (Redis/InMemory)**: Low-latency access to active session history.
2. **Warm Tier (File/JSON)**: Durable, local storage for recent history.
3. **Cold Tier (Qdrant/Vector)**: Long-term semantic memory for cross-session retrieval.

### Batch Persistence Mechanism
To prevent I/O bottlenecks, writes are buffered in `_batch_buffer`. A flush is triggered when:
- `BATCH_THRESHOLD` (default 25) writes are accumulated.
- `get_history()` is called.
- `flush()` is explicitly invoked.

---

## id Software Heritage Patterns

### 1. ZONEID Pattern `[id-soft: doom-1993]`
Every persisted exchange entry includes a `ZONEID_MEMORY` marker. This is verified on load to detect data corruption or stale references.

### 2. Lazy Deletion & Grace Period `[id-soft: doom-1993 / quake-1996]`
Sessions are not deleted immediately. They are marked as tombstoned and reaped after `TOMBSTONE_GRACE_SECONDS` (0.5s), ensuring that in-flight `add_exchange` operations can complete safely without crashing.

### 3. Temp Tier `[id-soft: quake-1996]`
Implements a transient scratchpad for in-flight inference results that should not be persisted to the permanent record, mirroring Quake's transient memory allocations.
