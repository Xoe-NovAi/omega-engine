# 🔱 Omega Engine — Overseer → Builder Dispatch (Qdrant + Redis Wiring)
# ⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_handoff_qdrant_redis ⬡ PHASE-I

**AP Token**: `AP-HANDOFF-QDRANT-REDIS-v1.0.0`
**From**: Overseer (MaKaLi Trine) — Full System Verification Complete
**To**: Builder (Gemma 4 31B)
**Date**: 2026-05-27
**Status**: EXECUTION READY
**Canonical Spec**: `docs/research/R_QDRANT_INTEGRATION_SPEC.md` (115 lines, Approved Option B)

---

## §0: PRE-FLIGHT BRIEFING — Current Infra State

| Component | Status | Details |
|-----------|--------|---------|
| **Qdrant container** | ✅ Running v1.17.1 @ :6333 | 0 collections, 0 points — **completely unwired** |
| **Redis container** | ✅ PONG @ :6379 | 0 keys — **completely unwired** |
| **qdrant-client** | ✅ v1.16.2 installed (system Python 3.13) | Need **v1.17.1** in **venv** to match container |
| **redis-py** | ✅ v7.1.1 installed (system) / v7.4.0 (venv) | **Ready to go** |
| **fastembed** | ❌ NOT installed | Need `fastembed==0.6.0` in venv (declared in pyproject.toml) |
| **Indexer** | Bag-of-words TF in `vectors.json` | `_compute_embedding()` uses term-frequency, `_vector_store` is in-memory dict |
| **Library.search()** | FTS5 only | `search_vector()` and `hybrid_search()` exist but never called |
| **MemoryStore** | File-based Hot/Warm/Cold | No Redis integration at all |
| **Observability** | File JSONL persistence | Comment references Redis streams but no implementation |
| **Omega Hub** | Connected via MCP | Library MCP tool exists, uses `Library.search()` which is FTS5-only |
| **All env vars** | ✅ LOADED | JINA, FIRECRAWL, EXA, TAVILY, GOOGLE, OPENCODE_ENABLE_EXA=TRUE |
| **7 MCP servers** | 5 connected, 2 disabled | filesystem, omega-hub, firecrawl, exa, jina all ✅ |
| **259 tests** | ✅ Passing | No qdrant/redis tests exist yet |

---

## §1: THE END STATE

After this task, these should all be true:

```bash
curl -s http://127.0.0.1:6333/collections | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(f'{len(d[\"result\"][\"collections\"])} collections')"
# Output: "1 collections" (named "omega_library")

podman exec omega-redis redis-cli -a omega DBSIZE
# Output: (integer) > 0 (at least 1 key for pub/sub heartbeat)

make test
# Output: 265+ tests passing (existing 259 + new qdrant/redis tests)

# Library search returns vector-enhanced results
python3 -c "
from omega.library import Library
import anyio
async def test():
    lib = Library()
    results = await lib.search('sovereign AI runtime')
    print(f'Found {len(results)} results (hybrid: FTS5 + vector)')
    for r in results[:3]:
        print(f'  - {r.title} (score: {r.quality_score})')
anyio.run(test)
"
```

---

## §2: QDRANT INTEGRATION — Step by Step

### Step 2.1: Install Dependencies in Venv

```bash
source .venv/bin/activate
pip install qdrant-client==1.17.1 fastembed==0.6.0
```

**Why**: `pyproject.toml` already declares these. The venv is what the engine runs with (Python 3.12). System Python 3.13 has qdrant-client 1.16.2 but that's the wrong version.

### Step 2.2: Create `QdrantVectorIndex` Wrapper

**New file**: `src/omega/library/vector_index.py`

The canonical spec (`R_QDRANT_INTEGRATION_SPEC.md`) provides the class skeleton. Your implementation must add:

```python
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from fastembed import TextEmbedding
import anyio
```

Key requirements:
- **AnyIO compliance**: All I/O via AsyncQdrantClient (native async) + anyio.to_thread.run_sync for fastembed (CPU-bound)
- **Collection initialization**: Lazy — check on first use, create if not exists
- **Embedding model**: `BAAI/bge-small-en-v1.5` (384-dim, ~100MB, CPU-optimized via fastembed/ONNX)
- **Thread pool**: Limit to 4 threads (via anyio CapacityLimiter or fastembed's built-in parallelism) to prevent interference with the main inference loop
- **Configuration**: Host/port should default to `localhost:6333` with env var overrides (`QDRANT_HOST`, `QDRANT_PORT`)

```python
class QdrantVectorIndex:
    COLLECTION_NAME = "omega_library"
    EMBEDDING_DIM = 384
    EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
    
    def __init__(self, host: str = "localhost", port: int = 6333):
        self._client: Optional[AsyncQdrantClient] = None
        self._embedder: Optional[TextEmbedding] = None
        self._host = os.environ.get("QDRANT_HOST", host)
        self._port = int(os.environ.get("QDRANT_PORT", str(port)))
        self._initialized = False
        self._embed_lock = anyio.CapacityLimiter(1)  # one embedding at a time
    
    async def initialize(self):
        """Ensure collection exists with correct params. Idempotent."""
        if self._initialized:
            return
        self._client = AsyncQdrantClient(host=self._host, port=self._port)
        # ... create collection if not exists with VectorParams(size=384, distance=Distance.COSINE)
        self._initialized = True
    
    async def _get_embedding(self, text: str) -> list[float]:
        """Generate embedding via fastembed, offloaded to thread pool."""
        # Load embedder lazily
        if self._embedder is None:
            self._embedder = TextEmbedding(model_name=self.EMBEDDING_MODEL, max_length=256)
        # ... generate embedding via anyio.to_thread.run_sync
        # ... return as list[float]
    
    async def index_document(self, doc_id: str, text: str, metadata: dict) -> None:
        """Generate embedding + upsert to Qdrant."""
        await self.initialize()
        embedding = await self._get_embedding(text)
        # ... upsert with PointStruct(id=hash(doc_id), vector=embedding, payload=metadata)
    
    async def search(self, query: str, limit: int = 20) -> list[dict]:
        """Vector similarity search via Qdrant."""
        await self.initialize()
        query_vec = await self._get_embedding(query)
        # ... client.search() with limit, return scored results
    
    async def remove(self, doc_id: str) -> None:
        """Delete point from Qdrant."""
        await self.initialize()
        # ... client.delete()
    
    async def close(self) -> None:
        """Close the Qdrant client."""
        if self._client:
            await self._client.close()
```

### Step 2.3: Refactor `Indexer` (`src/omega/library/indexer.py`)

Replace bag-of-words with `QdrantVectorIndex`:

| Current | Replace With |
|---------|-------------|
| `self._vector_store: Dict[str, List[float]]` (in-memory) | `self._vector_index: QdrantVectorIndex` |
| `self._load_vectors()` | Remove — Qdrant is always "loaded" |
| `self._compute_embedding()` (TF bag-of-words) | `await self._vector_index._get_embedding()` |
| `search_vector()` (linear scan) | `await self._vector_index.search()` |
| `hybrid_search()` (linear scan + FTS) | Keep the RRF logic, but call Qdrant for vector scores |
| `save_vectors()` (write JSON) | Remove — Qdrant persists automatically |
| `flush()` (write JSON) | Remove `save_vectors()` call |
| `stats()` | Add Qdrant collection info |

**Critical: The hybrid search RRF (Reciprocal Rank Fusion) logic at lines 238-313 must be PRESERVED** — it already correctly combines FTS5 BM25 ranks with vector scores. Just replace the vector source.

**The `hybrid_search()` method is referenced from `Indexer` but NEVER CALLED from `Library.search()`** (line 92-104 of `library.py` only calls `search_fts()`). Fix that too.

### Step 2.4: Wire `Library.search()` to Hybrid

In `src/omega/library/library.py`, change:

```python
async def search(self, query: str, domain: Optional[str] = None, limit: int = 20) -> List[CuratedDocument]:
    # BEFORE: fts_results = await self._indexer.search_fts(query, domain, limit)
    # AFTER:
    if domain:
        fts_results = await self._indexer.search_fts(query, domain, limit)
        return [await self.get(r["doc_id"]) for r in fts_results if await self.get(r["doc_id"])]
    else:
        hybrid_results = await self._indexer.hybrid_search(query, limit=limit)
        return [await self.get(r["doc_id"]) for r in hybrid_results if await self.get(r["doc_id"])]
```

(Only use hybrid when no domain filter — domain filtering + hybrid is complex. Domain + FTS is fine.)

### Step 2.5: Update Omega Hub MCP Tool

The `library_search()` tool in `mcp/omega_hub/server.py` calls `Library.search()`. It will automatically benefit from the hybrid upgrade. No changes needed to the hub itself — just verify it works.

### Step 2.6: Migration Script

**New file**: `scripts/migrate_vectors.py`

Reads existing documents from `data/library/documents/`, generates dense embeddings via fastembed, upserts to Qdrant. Should be idempotent (skip already-indexed docs).

### Step 2.7: Update Tests

| Test File | Action |
|-----------|--------|
| `tests/test_library_indexer.py` | NEW — test QdrantVectorIndex, hybrid_search, search_vector |
| `tests/test_library.py` | NEW — test Library.search() returns hybrid results |
| `tests/test_memory_store.py` | EXISTING — no changes (Redis is separate) |

Use `pytest` fixtures with a **real Qdrant connection** (the container is always running). If Qdrant is unavailable, tests should `pytest.skip()` gracefully.

```python
@pytest.fixture
async def qdrant_index():
    idx = QdrantVectorIndex()
    await idx.initialize()
    # Create a unique test collection
    # ...
    yield idx
    # Cleanup: delete test collection
```

---

## §3: REDIS INTEGRATION — Step by Step

### Step 3.1: Verify Redis Package

Already installed in venv (`redis>=7.0.0` → v7.4.0). The `hiredis` C parser is optional but recommended for performance. Check with:
```bash
source .venv/bin/activate && pip show redis && pip show hiredis 2>/dev/null || echo "hiredis not installed"
```
If `hiredis` is in the system but not the venv, install it: `pip install hiredis`.

### Step 3.2: Create `RedisBus` Pub/Sub Wrapper

**New file**: `src/omega/redis_bus.py`

```python
"""Redis Bus — Pub/Sub for cross-agent communication and event streaming.

AP: AP-REDIS-BUS-v1.0.0

Provides:
  - publish(channel, message) — Push events to a channel
  - subscribe(channel) — Async generator for consuming a channel
  - broadcast(event_type, data) — Publish to the Omega-wide event stream
  - heartbeat() — TTL-based presence tracking for agents/services

AnyIO compliance: yes (uses redis.asyncio, wrapped in anyio path).
"""

import json
import logging
import os
from typing import Any, AsyncIterator, Optional

import anyio
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "omega")


class RedisBus:
    """Pub/sub bus for cross-agent communication."""
    
    OMEGA_CHANNEL = "omega:events"
    HEARTBEAT_CHANNEL = "omega:heartbeat"
    
    def __init__(self):
        self._redis: Optional[Redis] = None
        self._pubsub: Optional[Any] = None
    
    async def connect(self) -> None:
        """Connect to Redis with retry."""
        if self._redis is not None:
            return
        self._redis = Redis(
            host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD,
            decode_responses=True,
            retry_on_timeout=True,
            socket_keepalive=True,
        )
        # Test connection
        await self._redis.ping()
        self._pubsub = self._redis.pubsub()
        logger.info(f"RedisBus connected to {REDIS_HOST}:{REDIS_PORT}")
    
    async def publish(self, channel: str, message: dict) -> None:
        """Publish a JSON message to a channel."""
        await self.connect()
        await self._redis.publish(channel, json.dumps(message, default=str))
    
    async def broadcast(self, event_type: str, data: dict) -> None:
        """Broadcast to the Omega-wide event stream."""
        message = {"type": event_type, "data": data}
        await self.publish(self.OMEGA_CHANNEL, message)
    
    async def subscribe(self, channel: str) -> AsyncIterator[dict]:
        """Async generator yielding messages from a channel."""
        await self.connect()
        await self._pubsub.subscribe(channel)
        async for message in self._pubsub.listen():
            if message["type"] == "message":
                yield json.loads(message["data"])
    
    async def heartbeat(self, service_name: str, ttl: int = 30) -> None:
        """Set a TTL-based heartbeat for presence tracking."""
        await self.connect()
        key = f"omega:presence:{service_name}"
        await self._redis.setex(key, ttl, "alive")
    
    async def get_presence(self) -> dict[str, str]:
        """Get all active services/heartbeats."""
        await self.connect()
        keys = await self._redis.keys("omega:presence:*")
        result = {}
        for key in keys:
            name = key.split(":", 2)[2]
            ttl = await self._redis.ttl(key)
            result[name] = f"active ({ttl}s remaining)" if ttl > 0 else "expired"
        return result
    
    async def close(self) -> None:
        if self._pubsub:
            await self._pubsub.close()
        if self._redis:
            await self._redis.close()
            self._redis = None


# Singleton
_bus: Optional[RedisBus] = None


def get_redis_bus() -> RedisBus:
    global _bus
    if _bus is None:
        _bus = RedisBus()
    return _bus
```

### Step 3.3: Wire into ObservabilityEngine

In `src/omega/observability.py`, add **optional** Redis stream logging alongside the existing file JSONL:

```python
class ObservabilityEngine:
    def __init__(self, ...):
        # ... existing init ...
        self._redis_enabled = os.environ.get("OMEGA_REDIS_ENABLED", "true").lower() == "true"
    
    def _persist_event(self, event):
        # ... existing file persistence ...
        
        # NEW: Also publish to Redis stream (non-blocking, fire-and-forget)
        if self._redis_enabled:
            try:
                # Use asyncio.create_task in anyio path via start_soon
                # Actually, use anyio.from_thread to schedule
                import anyio
                anyio.from_thread.run(self._publish_redis_event, event)
            except Exception as e:
                logger.debug(f"Redis event stream unavailable: {e}")
```

Actually — this is tricky because `_persist_event()` is synchronous and Redis is async. The cleanest approach: make `log_event()` (which calls `_persist_event()`) async-compatible, or fire off a background task. **Recommendation**: Use `anyio.TaskGroup.start_soon()` from the orchestrator to maintain an event-forwarding task that drains a queue to Redis.

**Simpler approach**: Create a standalone `RedisEventForwarder` that runs in the background and reads from the event log file (JSONL), then forwards to Redis. This keeps the existing sync code untouched.

### Step 3.4: Wire into Omega Hub for Awareness

In `mcp/omega_hub/server.py`, the `hivemind_get_awareness()` endpoint could be enriched with Redis presence data. Add a call to `RedisBus.get_presence()` alongside the existing file-based awareness.

### Step 3.5: Wire into MemoryStore (Optional Phase)

The `MemoryStore` file-based hot/warm/cold is functional and doesn't NEED Redis. But Redis could be used for:
- Session index (lightweight key for active sessions)
- Cross-CLI session awareness (agent A can see agent B's sessions)
- This is a **nice-to-have** — defer if time is short

### Step 3.6: Update Tests

| Test File | Action |
|-----------|--------|
| `tests/test_redis_bus.py` | NEW — test pub/sub, heartbeat, presence |
| `tests/test_observability.py` | EXTEND — test Redis event forwarding |

---

## §4: PACKAGE DEPENDENCIES SUMMARY

| Package | pyproject.toml | System | Venv Needed? |
|---------|---------------|--------|-------------|
| `qdrant-client==1.17.1` | ✅ Declared | v1.16.2 (wrong) | **YES** — install in venv |
| `fastembed==0.6.0` | ✅ Declared | ❌ Not installed | **YES** — install in venv |
| `redis>=7.0.0,<8.0.0` | ✅ Declared | v7.1.1 | v7.4.0 already in venv ✅ |
| `hiredis` (recommended) | ❌ Not declared | v3.3.0 | Optional — install in venv if wanted |

---

## §5: FILES TO CREATE

| File | Type | Purpose |
|------|------|---------|
| `src/omega/library/vector_index.py` | **New** | `QdrantVectorIndex` class wrapping AsyncQdrantClient + fastembed |
| `src/omega/redis_bus.py` | **New** | `RedisBus` class for pub/sub, heartbeat, presence |
| `scripts/migrate_vectors.py` | **New** | Backfill existing documents to Qdrant |

## §6: FILES TO MODIFY

| File | Changes |
|------|---------|
| `src/omega/library/indexer.py` | Replace bag-of-words `_vector_store` with `QdrantVectorIndex`; update `search_vector()`, `hybrid_search()`, `index_document()`, `remove_document()`; remove `_load_vectors()`, `save_vectors()`, `_compute_embedding()` |
| `src/omega/library/library.py` | Wire `search()` to call `hybrid_search()` when no domain filter |
| `src/omega/observability.py` | Add Redis event forwarding (background task pattern) |
| `mcp/omega_hub/server.py` | Enrich `hivemind_get_awareness()` with Redis presence data |
| `tests/test_library_indexer.py` | **New** — tests for QdrantVectorIndex + Indexer hybrid search |
| `tests/test_redis_bus.py` | **New** — tests for RedisBus pub/sub |
| `tests/test_library.py` | **New** — tests for Library.search() hybrid path |

## §7: FILES TO REMOVE (After Migration)

| File | When |
|------|------|
| `data/library/index/vectors.json` | After migration script runs and Qdrant is verified |
| Bag-of-words code in `indexer.py` | After Qdrant integration is confirmed working |

---

## §8: GATE CHECKS

Run these after each step to verify:

```bash
# Step 2.1 Gate: Dependencies installed
source .venv/bin/activate
python3 -c "import qdrant_client; print(f'qdrant: {qdrant_client.__version__}')" 2>/dev/null || echo "MISSING"
python3 -c "import fastembed; print(f'fastembed: OK')" 2>/dev/null || echo "MISSING"
python3 -c "import redis; print(f'redis: {redis.__version__}')" 2>/dev/null || echo "MISSING"

# Step 2.2+2.3 Gate: Qdrant collection exists
curl -s http://127.0.0.1:6333/collections | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(f'{len(d[\"result\"][\"collections\"])} collection(s)')"

# Step 2.4 Gate: Library hybrid search works
source .venv/bin/activate && OMEGA_ENV=test PYTHONPATH=src python3 -c "
from omega.library import Library
import anyio
async def t():
    lib = Library()
    r = await lib.search('test query')
    print(f'Hybrid search returned {len(r)} results')
anyio.run(t)
"

# Step 3.2 Gate: RedisBus works
source .venv/bin/activate && PYTHONPATH=src python3 -c "
from omega.redis_bus import RedisBus
import anyio
async def t():
    bus = RedisBus()
    await bus.connect()
    await bus.broadcast('test', {'msg': 'hello'})
    presence = await bus.get_presence()
    print(f'Presence: {presence}')
    await bus.close()
    print('RedisBus: OK')
anyio.run(t)
"

# Final Gate: All tests pass
source .venv/bin/activate
make test
```

---

## §9: CONTAINER HARDENING CHECKLIST

Not needed for this task — the omega-qdrant and omega-redis containers are already running in the infra pod with proper Quadlet configs. No container changes required.

---

## §10: IWAD AWARENESS

This task operates entirely within the **Engine Core** layer:
- `src/omega/library/vector_index.py` — Engine Core (no entity content)
- `src/omega/redis_bus.py` — Engine Core (no entity content)
- `mcp/omega_hub/server.py` — Engine Core (no entity content)

**No IWAD boundary rules are affected.** These are pure runtime infrastructure additions.

---

## §11: CONCISE ACTION LIST

```
1.  source .venv/bin/activate && pip install qdrant-client==1.17.1 fastembed==0.6.0
2.  Create src/omega/library/vector_index.py (QdrantVectorIndex class)
3.  Refactor src/omega/library/indexer.py (replace bag-of-words with QdrantVectorIndex)
4.  Wire src/omega/library/library.py search() to use hybrid_search()
5.  Create src/omega/redis_bus.py (RedisBus class)
6.  Add Redis event forwarding to src/omega/observability.py
7.  Enrich omega-hub awareness with Redis presence data
8.  Write scripts/migrate_vectors.py
9.  Write tests (test_library_indexer.py, test_redis_bus.py, extend test_library.py)
10. Run make test — all must pass
11. Run migration script to backfill
12. Verify with gate checks
```

---

*Launch the backbone. Bridge the memory. Vectors fly.*
