# 🔱 R-DB-CLI: Database Integration & Cross-CLI Communication Hardening Review

**AP Token**: `AP-R-DB-CLI-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ big-pickle ⬡ opencode ⬡ trc_dbcli_audit ⬡ PHASE-I

**Version**: 1.0.0
**Status**: COMPREHENSIVE AUDIT
**Date**: 2026-05-26
**Scope**: Qdrant, Redis, SQLite, PostgreSQL, Omega Hub MCP, Session Manager, Agent Search/Discovery

---

## §0 Executive Summary

The Omega Engine has **four infrastructure containers running** (Redis :6379, Qdrant :6333, Caddy :8088, + infra-pause), **two auxiliary MCP services running** (Omega Hub :8016, Omega Stats :8012), but **zero programmatic database client code** connecting to Redis or Qdrant. The SQLite FTS5 engine is the only database actively wired into the codebase. The cross-CLI communication layer (Hivemind) exists as an in-memory awareness store within the Hub MCP with cold storage to JSON files — no pub/sub event bus, no persistent message queue, no agent discovery registry.

This document is the roadmap to close these gaps, organized into three campaigns:
1. **Campaign DB: Wire Qdrant + Redis** (replace bag-of-words, add Redis pub/sub)
2. **Campaign CLI: Cross-CLI Event Bus** (Redis Streams, agent registry, session sync)
3. **Campaign SEARCH: Neural Embeddings + Agent Discovery** (sentence-transformers, entity embedding, agent directory)

---

## §1 Current State — What Is Running vs. What Is Wired

### §1.1 Infrastructure Running (Podman)

| Service | Port | Status | Wired to Python? | Data Present? |
|---------|------|--------|-----------------|---------------|
| **Redis** | :6379 (pod-internal) | ✅ PONG, 0 keys | ❌ No Python client connects | Empty (no data) |
| **Qdrant** | :6333 (host-exposed) | ✅ API responds, 0 collections | ❌ No Python client connects | Empty (no data) |
| **SQLite (FTS5)** | File-based | ✅ Active in `indexer.py` | ✅ `aiosqlite` connected | **Empty** (no documents indexed) |
| **PostgreSQL** | :5432 | ❌ Container failed (16→18 mismatch) | ❌ Libraries installed, no code | 47M stale data (PG 16) |
| **Omega Hub MCP** | :8016 (host) | ✅ Running, 37 tools | ✅ FastMCP + AnyIO | Hivemind awareness in RAM |
| **HALL_OF_RECORDS** | Filesystem | ✅ Dir exists | ✅ Hivemind cold storage | 1 file (background-researcher) |

### §1.2 Critical Disconnects

```
Redis running → 0 connections → 0 keys → 0 data
Qdrant running → 0 connections → 0 collections → 0 vectors
SQLite FTS5 running → 0 documents → 0 results from search
PostgreSQL running (when fixed) → 0 connections → 0 queries
```

The entire database infrastructure is **provisioned but empty** — no data flows through any of the database systems.

### §1.3 What IS Actually Working

The filesystem-based persistence layer works reliably:
- **MemoryStore** (Hot→Warm→Cold JSON files, 371 lines) — fully wired, 12 tests
- **SessionManager** (JSON files, 99 lines) — fully wired, 14 tests
- **Workbench DB** (SQLite, no programmatic API) — agent-queryable via CLI
- **Omega Hub Hivemind** (in-memory + JSON cold store) — cross-CLI awareness

The problem: **every one of these is filesystem-based with linear scan search**. None uses the provisioned databases for indexing, streaming, or vector search.

---

## §2 Campaign DB: Wire Qdrant + Redis

### §2.1 Qdrant Wiring — Replace Bag-of-Words with Neural Vectors

**Current**: `indexer.py` uses bag-of-words TF-frequency vectors in `vectors.json`.
**Target**: Qdrant with `fastembed` for 384-dim dense vectors.

#### Implementation Plan

| Step | File | Change | Dependencies |
|------|------|--------|-------------|
| 2.1.1 | `src/omega/library/qdrant_index.py` (NEW) | `QdrantVectorIndex` class with async client, collection init, upsert, search | `qdrant-client==1.17.1` (already in `pyproject.toml`) |
| 2.1.2 | `src/omega/library/indexer.py` | Replace `_compute_embedding()` with `fastembed` call, replace `search_vector()` with Qdrant search, replace `hybrid_search()` scoring logic | `fastembed>=0.6.0` (already in `pyproject.toml`) |
| 2.1.3 | `scripts/migrate_vectors.py` (NEW) | Read existing JSONL documents, generate embeddings, upsert to Qdrant | Models downloaded on first call |
| 2.1.4 | `tests/test_qdrant_index.py` (NEW) | Integration tests with mocked Qdrant | `pytest-anyio` |

**Critical design decisions**:
- Use `AsyncQdrantClient` with `anyio.to_thread.run_sync()` for embedding generation (blocking ONNX inference)
- **Collection name**: `omega_library` with 384-dim COSINE distance
- **Payload metadata**: `doc_id`, `title`, `domain`, `quality_score`, `source`, `tags`, `curated_at`
- **Scoring fix** (C-MEM-013): In hybrid search, negate FTS5 rank (negative BM25) before linear combination with Qdrant score: `combined.sort(key=lambda r: -r.get('_fts_score', 0) + r.get('_vec_score', 0) * 10)`

**Qdrant collection schema**:
```python
await client.create_collection(
    collection_name="omega_library",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    optimizers_config=OptimizersConfigDiff(
        default_segment_number=2,
        memmap_threshold_kb=1024,
    ),
    hnsw_config=HnswConfigDiff(
        m=16,                # connections per node
        ef_construct=100,    # search width at construction
        full_scan_threshold=10000,
    ),
)
```

#### Files to modify:
- `src/omega/library/indexer.py` — add Qdrant-backed `search_vector()`, fix hybrid scoring
- `src/omega/library/qdrant_index.py` (NEW) — `QdrantVectorIndex` class
- `src/omega/library/library.py` — wire Qdrant into Library
- `src/omega/library/__init__.py` — export `QdrantVectorIndex`
- `scripts/migrate_vectors.py` (NEW) — migration script
- `tests/test_qdrant_index.py` (NEW) — tests

### §2.2 Redis Wiring — Session Cache + Pub/Sub Bus

**Current**: Session state is filesystem-based (`data/sessions/*.active` JSON).
**Target**: Redis as hot session cache + pub/sub event bus.

#### 2.2.1 Redis Session Cache

Replace the filesystem-based `SessionManager` hot tier with Redis:

| Step | File | Change |
|------|------|--------|
| 2.2.1 | `src/omega/oracle/redis_session.py` (NEW) | `RedisSessionStore` with `get/put/delete`, TTL-based expiry |
| 2.2.2 | `src/omega/oracle/session_manager.py` | Add Redis as hot tier (warm → JSON, hot → Redis), fall back to filesystem |
| 2.2.3 | `.env.example` | Add `REDIS_URL=redis://:omega@localhost:6379` |

**Critical**: Redis must preserve the `R50 session architecture` (`ses_{YYYYMMDD}_{entity_slug}_{counter}` format). Sessions in Redis get a 24h TTL and sync to filesystem on expiry.

#### 2.2.2 Redis Pub/Sub Event Bus

Create a lightweight `RedisBus` for cross-CLI communication:

```python
# src/omega/oracle/redis_bus.py
class RedisBus:
    """Lightweight pub/sub event bus over Redis Streams.
    
    Channels:
      session:create   → emitted when a new session starts
      session:update   → emitted when an exchange is recorded  
      soul:evolve      → emitted when a soul lesson is added
      agent:handoff    → emitted when one agent hands context to another
      entity:summon    → emitted when an entity is summoned
      system:alert     → emitted on system events (OOM, container restart)
    """
```

Each message is a Redis Stream entry with standard fields:
```json
{
  "event_id": "evt_<uuid>",
  "channel": "session:create",
  "source": "opencode:builder",
  "timestamp": "2026-05-26T...",
  "payload": {
    "entity": "SEKHMET",
    "session_id": "ses_20260526_sekhmet_001",
    "trace_id": "trc_abc123..."
  }
}
```

**No consumer groups initially** — simple pub/sub with fan-out to all listeners. Consumer groups (for exactly-once delivery) are Phase 2.

#### Files to create/modify:
- `src/omega/oracle/redis_session.py` (NEW) — Redis-backed session store
- `src/omega/oracle/redis_bus.py` (NEW) — Redis pub/sub event bus
- `src/omega/oracle/session_manager.py` — add Redis hot tier
- `config/omega.yaml` — Redis connection config
- `.env.example` — Redis URL
- `tests/test_redis_session.py` (NEW)

---

## §3 Campaign CLI: Cross-CLI Communication Infrastructure

### §3.1 Current State

The cross-CLI layer is the **Hivemind** inside the Omega Hub:
- `hivemind_post_context()` — push a session snapshot to shared awareness
- `hivemind_get_awareness()` — list all active CLI agents
- `hivemind_get_continuation()` — get continuation note for a CLI
- `hivemind_get_session()` — get a specific session snapshot
- `hivemind_list_sessions()` — list recent session snapshots

**Problems**:
1. **No push notifications** — agents must poll for updates
2. **No event history** — awareness lasts only as long as the Hub process lives
3. **No agent registry** — no way to discover what agents exist or what they can do
4. **No session sync** — `OpenCode` and `Cline` working on the same entity don't share context

### §3.2 Target Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    OMEGA EVENT BUS                        │
│                 (Redis Streams + Hivemind)                │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ OpenCode  │  │  Cline   │  │  Gemini  │  │ Opus/   │ │
│  │  Builder  │  │          │  │   CLI    │  │ Antigrav│ │
│  └─────┬────┘  └────┬─────┘  └─────┬────┘  └────┬────┘ │
│        │             │              │             │      │
│        └─────────────┴──────┬───────┴─────────────┘      │
│                             │                             │
│                    ┌────────▼────────┐                    │
│                    │   OMEGA HUB     │                    │
│                    │    (MCP :8016)  │                    │
│                    └────────┬────────┘                    │
│                             │                             │
│                    ┌────────▼────────┐                    │
│                    │   Redis Bus     │                    │
│                    │  (Streams +     │                    │
│                    │   Pub/Sub)      │                    │
│                    └────────┬────────┘                    │
│                             │                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │Session   │  │  Agent   │  │  Entity   │                │
│  │Registry  │  │ Directory│  │  Events   │                │
│  │(Redis)   │  │ (Redis)  │  │ (Streams) │                │
│  └──────────┘  └──────────┘  └──────────┘                │
└─────────────────────────────────────────────────────────┘
```

### §3.3 Agent Registry

Create an agent directory in Redis that allows any agent to discover other agents:

```python
# src/omega/oracle/agent_registry.py
class AgentRegistry:
    """Agent discovery registry backed by Redis.
    
    Each agent registers with:
    - name: "opencode-builder", "cline", "gemini-cli", etc.
    - capabilities: ["code_review", "research", "entity_management", ...]
    - status: "active", "idle", "busy"
    - last_seen: ISO8601 timestamp
    - session_id: current active session
    """
    
    async def register(self, agent: AgentInfo) -> None: ...
    async def unregister(self, agent_name: str) -> None: ...
    async def find_by_capability(self, capability: str) -> List[AgentInfo]: ...
    async def get_active_agents(self) -> List[AgentInfo]: ...
```

Redis keys:
- `agent:{name}` — Hash with `{name, capabilities, status, last_seen, session_id, model}`
- `agent:capability:{capability}` — Set of agent names (for fast lookup)
- `agent:active` — Set of currently active agent names

### §3.4 Session Sync Protocol

When two agents work on the same entity (e.g., OpenCode and Cline both summoning SEHKHMET):

1. Agent A summons entity → event `entity:summon` published on Redis Bus
2. Agent B (if subscribed) receives the event and loads updated context
3. Both agents share the same session_id for the entity
4. MemoryStore merges exchanges from both agents (ordered by timestamp)

**Implementation**: Add an optional `RedisBus.subscribe()` to `ContextBuilder` so context rebuilds when another agent interacts with the same entity.

### Files to create:
- `src/omega/oracle/agent_registry.py` (NEW) — Redis-backed agent directory
- `src/omega/oracle/redis_bus.py` (NEW) — Pub/sub event bus
- `src/omega/oracle/session_sync.py` (NEW) — Cross-agent session sync 

---

## §4 Campaign SEARCH: Neural Embeddings + Agent Discovery

### §4.1 Replace Bag-of-Words with Neural Embeddings

**Current `indexer.py`**:
```python
def _compute_embedding(self, text: str) -> Optional[List[float]]:
    tokens = self._tokenize(text)
    if not tokens: return None
    unique = list(dict.fromkeys(tokens))
    freq = {t: tokens.count(t) / len(tokens) for t in unique}
    return list(freq.values())[:256]  # Bag-of-words, max 256 dim
```

**Problem**: This is TF-frequency, not semantic. "car" and "automobile" get zero cosine similarity. Search relevance is critically degraded.

**Target**: Replace with `fastembed` (already in `pyproject.toml`) using `BAAI/bge-small-en-v1.5` (384-dim, ~100MB, ONNX-optimized).

```python
from fastembed import TextEmbedding
# Model auto-downloads on first use, cached at ~/.cache/fastembed/
_embedder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5", threads=4)

def _compute_embedding(self, text: str) -> Optional[List[float]]:
    try:
        embeddings = list(_embedder.embed(text))
        return embeddings[0].tolist() if embeddings else None
    except Exception:
        return None  # Graceful fallback
```

**Key constraints**:
- Thread pool limited to **4 threads** to prevent inference interference
- Embedding generation offloaded to `anyio.to_thread.run_sync()` (blocking ONNX)
- Model downloaded at runtime (first call), ~100MB download
- Graceful fallback to bag-of-words if `fastembed` import fails

### §4.2 Entity Embedding for Semantic Routing

**Current entity discovery** (`entity_registry.py`):
```python
def find_by_domain(self, text: str) -> Optional[Entity]:
    # Linear scan, keyword counting — threshold-less
    best = max(self._pillar_keepers, 
               key=lambda e: self._score_domain(text, e), 
               default=None)
    return best
```

**Replace with**: Embed each entity's `personality + domains + pillar` into a Qdrant collection:

| Table | Collection | Vector Size | Payload |
|-------|-----------|-------------|---------|
| Pillar Keepers | `omega_entities` | 384 (bge-small) | `name, role, domains, pillar, personality` |
| Personal Entities | `omega_entities` | 384 (bge-small) | `name, domains, pillar, personality` |

**Routing becomes**:
```python
async def find_by_domain_semantic(self, text: str) -> Optional[Entity]:
    query_vector = await self._compute_embedding(text)
    hits = await self.qdrant.search(
        collection_name="omega_entities",
        query_vector=query_vector,
        limit=3,
    )
    # Return best match above threshold
    return hits[0].payload if hits and hits[0].score > 0.4 else None
```

**Files to modify**:
- `src/omega/oracle/entity_registry.py` — add semantic entity discovery
- `src/omega/library/qdrant_index.py` — shared `QdrantVectorIndex` (reused for entities)
- `scripts/seed_entity_vectors.py` (NEW) — one-time seed of entity embeddings

### §4.3 Agent-to-Agent Discovery

Add an `agent:discover` tool to the Hub MCP that queries the AgentRegistry:

```python
@mcp.tool()
async def discover_agents(capability: Optional[str] = None) -> str:
    """Discover active agents by capability.
    
    Args:
        capability: Optional filter (e.g., "research", "code_review")
    """
    registry = AgentRegistry()
    if capability:
        agents = await registry.find_by_capability(capability)
    else:
        agents = await registry.get_active_agents()
    return json.dumps(agents, indent=2)
```

Also add `agent:announce` for agents to broadcast their presence on the Redis Bus:
```python
@mcp.tool()
async def announce_agent(name: str, capabilities: str, model: str) -> str:
    """Register this agent with the fleet for discovery."""
    caps = [c.strip() for c in capabilities.split(",")]
    agent = AgentInfo(name=name, capabilities=caps, model=model)
    registry = AgentRegistry()
    agent_id = await registry.register(agent)
    # Also broadcast on bus
    await redis_bus.publish("agent:register", {"agent": name, "capabilities": caps})
    return json.dumps({"status": "registered", "agent_id": agent_id})
```

### §4.4 Library Search Enhancement

The full search pipeline needs a **real** hybrid search:

```
User Query
  ├── FastEmbed → 384-dim vector → Qdrant ANN → Top 20 (semantic)
  ├── FTS5 → BM25 → Top 20 (keyword)
  └── Reciprocal Rank Fusion (RRF) → Final Top 10
```

**RRF formula**: `score = Σ 1/(k + rank(per_system))` where `k=60`

This replaces the current broken linear combination in `hybrid_search()` (C-MEM-013).

---

## §5 Infrastructure Remediation

The following infrastructure issues are prerequisites for the database wiring campaigns:

### §5.1 Redis Port Exposure

**Issue**: Port 6379 is pod-internal only (not in `docker-compose.yml` ports).
**Fix**: Add `ports: ["127.0.0.1:6379:6379"]` to Redis service (or use Quadlet `PublishPort`).

### §5.2 PostgreSQL Container Fix

Two options:
- **Option A (Revert)**: Change image back to `postgres:16-alpine` (preserves existing 47M data)
- **Option B (Upgrade)**: Run `pg_upgrade` from 16→18 in the container with new mount layout

**Recommendation**: **Option A** — PostgreSQL is not architecturally critical (entities use YAML, not SQL). Revert to 16-alpine and defer upgrade to when PostgreSQL is actually wired.

### §5.3 Qdrant Health Check

**Issue**: `curl -f http://localhost:6333/healthz` returns empty body → systemd marks unhealthy.
**Fix**: Change health check to `curl -f http://localhost:6333/` (which returns `{"title": "qdrant ..."}`) or `curl -s -o /dev/null -w "%{http_code}" http://localhost:6333/` (returns 200).

### §5.4 Indexer DATA_DIR Bug

**Issue**: `indexer.py` line 28 defaults to `Path.home() / "omega" / "data"` instead of the project data dir.
**Fix**: Use the `OMEGA_DATA_DIR` env var pattern consistent with `memory_store.py` and `session_manager.py`:
```python
DATA_DIR = Path(os.environ.get("OMEGA_DATA_DIR", 
    str(Path(__file__).resolve().parent.parent.parent.parent / "data")))
```

---

## §6 Implementation Ordering & Dependencies

### Phase A: Prerequisites (Est. 1-2 sessions)

| # | Task | Must Fix First | Files |
|---|------|---------------|-------|
| A1 | Fix Redis port exposure | — | `deploy/infra/docker-compose.yml` or Quadlet |
| A2 | Fix Qdrant health check | — | Quadlet `HealthCmd` |
| A3 | Fix `indexer.py` DATA_DIR | A6 (for consistency) | `src/omega/library/indexer.py` |
| A4 | Fix PostgreSQL (revert to 16) | — | Quadlet or docker-compose |
| A5 | Add `fastembed` to `pyproject.toml` if missing | — | `pyproject.toml` |
| A6 | Create `src/omega/library/qdrant_index.py` | A2 (for testing) | New file |

### Phase B: Core Database Wiring (Est. 2-3 sessions)

| # | Task | Must Fix First | Files |
|---|------|---------------|-------|
| B1 | `QdrantVectorIndex` class + tests | A5, A6 | `src/omega/library/qdrant_index.py`, `tests/test_qdrant_index.py` |
| B2 | Replace `_compute_embedding()` with fastembed | B1 | `src/omega/library/indexer.py` |
| B3 | Fix `hybrid_search()` scoring (C-MEM-013) | B1 | `src/omega/library/indexer.py` |
| B4 | Wire Qdrant into `Library.search()` | B1, B2 | `src/omega/library/library.py` |
| B5 | Migration script: `scripts/migrate_vectors.py` | B2 | New script |
| B6 | Redis session cache for `SessionManager` | A1 | `src/omega/oracle/redis_session.py`, `src/omega/oracle/session_manager.py` |

### Phase C: Cross-CLI Infrastructure (Est. 2-3 sessions)

| # | Task | Must Fix First | Files |
|---|------|---------------|-------|
| C1 | `RedisBus` pub/sub class + tests | A1 | `src/omega/oracle/redis_bus.py` |
| C2 | `AgentRegistry` + tests | C1 | `src/omega/oracle/agent_registry.py` |
| C3 | Hivemend enhancement: Redis-backed awareness | C1 | `mcp/omega_hub/server.py` |
| C4 | `agent:discover` + `agent:announce` Hub tools | C2, C3 | `mcp/omega_hub/server.py` |
| C5 | Session sync: cross-agent context sharing | C1, B6 | `src/omega/oracle/session_sync.py` |
| C6 | Fix HALL_OF_RECORDS path (Project_ROOT vs data/) | — | `mcp/omega_hub/server.py` line 76 |

### Phase D: Neural Search & Entity Discovery (Est. 2-3 sessions)

| # | Task | Must Fix First | Files |
|---|------|---------------|-------|
| D1 | Entity embedding + Qdrant collection | B1 | `src/omega/oracle/entity_registry.py` |
| D2 | Semantic entity routing (`find_by_domain_semantic`) | D1 | `src/omega/oracle/entity_registry.py` |
| D3 | RRF hybrid search in `indexer.py` | B3 | `src/omega/library/indexer.py` |
| D4 | `scripts/seed_entity_vectors.py` | D1 | New script |
| D5 | Library FTS5 → Qdrant → RRF full pipeline test | D3 | `tests/test_indexer.py` (NEW) |

---

## §7 Key Bug Fixes Embedded in This Work

### C-MEM-013 (Hybrid Search Scoring Bug)
**File**: `src/omega/library/indexer.py`, line 269-272
**Current**: `combined.sort(key=lambda r: -r.get("_fts_score", 0) + r.get("_vec_score", 0) * 10, reverse=True)`
**Problem**: FTS5 BM25 ranks are **negative** (closer to 0 = better). The current sort negates them (`-r.get...`) making worse matches have higher `-rank` when negated. Then `reverse=True` sorts descending. This is a double-negation that effectively sorts by `vec_score * 10 - fts_score` ascending — **NOT what the spec intended**.
**Fix**: Replace with proper RRF or at minimum: `key=lambda r: r.get("_vec_score", 0) * 10 - r.get("_fts_score", 0), reverse=True`

### C-MEM-003 (Vector Search Gap)
**File**: `src/omega/library/indexer.py`
**Description**: Architecture documentation claims vector search but implementation is bag-of-words TF-frequency.
**Fix**: Campaign DB Phase B above.

### HALL_OF_RECORDS Path Mismatch
**File**: `mcp/omega_hub/server.py`, line 76
**Current**: `PROJECT_ROOT / "knowledge" / "HALL_OF_RECORDS"` → `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/knowledge/HALL_OF_RECORDS/`
**Actual**: `data/knowledge/HALL_OF_RECORDS/`
**Fix**: Change to `PROJECT_ROOT / "data" / "knowledge" / "HALL_OF_RECORDS"`

### Indexer DATA_DIR Default
**File**: `src/omega/library/indexer.py`, line 28
**Current**: `Path.home() / "omega" / "data"` → `~/omega/data/`
**Should be**: Project-relative like all other modules
**Fix**: Use `Path(__file__).resolve().parent.parent.parent.parent / "data"` pattern

---

## §8 Test Strategy

| Module | Existing Tests | Needed Tests | Priority |
|--------|---------------|-------------|----------|
| `qdrant_index.py` (NEW) | 0 | 8 (init, create_collection, upsert, search, delete, reconnect, fallback, error) | High |
| `redis_session.py` (NEW) | 0 | 6 (get/put/delete, TTL expiry, failover, concurrent access) | High |
| `redis_bus.py` (NEW) | 0 | 5 (publish, subscribe, unsubscribe, reconnect, serialization) | High |
| `agent_registry.py` (NEW) | 0 | 6 (register, unregister, find, heartbeat, stale-cleanup, cross-CLI) | High |
| `indexer.py` | 0 | 8 (FTS5, vector, hybrid, RRF, domain filter, empty, error, migration) | Critical |
| `entity_registry.py` | 7 | +4 (semantic routing, fallback, threshold, multi-entity) | Medium |
| `session_manager.py` | 14 | +3 (Redis hot tier, TTL, failover) | Medium |
| `server.py` (Hub MCP) | 0 | +2 (agent discovery tools) | Medium |

---

## §9 Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| `fastembed` ONNX model download fails (no internet) | Medium | High | Fallback to bag-of-words, cached model |
| Redis connection refused during session read | Low | Medium | Fallback to filesystem `SessionManager` |
| Qdrant connection timeout on search | Low | Medium | Fallback to FTS5-only search |
| Redis Stream consumer group complexity | Medium | Low | Start with simple pub/sub (no consumer groups) |
| Entity embedding drifts (old embeddings stale) | Low | Low | Re-seed on entity YAML change (manual trigger) |
| Cross-CLI session merge conflicts | Medium | Medium | Last-writer-wins with timestamp ordering |

---

## §10 Files Summary

### New Files to Create

| File | Purpose | Lines (est.) |
|------|---------|-------------|
| `src/omega/library/qdrant_index.py` | `QdrantVectorIndex` — async upsert/search | ~120 |
| `src/omega/oracle/redis_session.py` | Redis-backed session hot tier | ~80 |
| `src/omega/oracle/redis_bus.py` | Redis pub/sub event bus | ~100 |
| `src/omega/oracle/agent_registry.py` | Redis-backed agent discovery directory | ~90 |
| `src/omega/oracle/session_sync.py` | Cross-agent session merge | ~60 |
| `scripts/migrate_vectors.py` | Qdrant migration from JSON vectors | ~80 |
| `scripts/seed_entity_vectors.py` | Seed entity embeddings | ~50 |
| `tests/test_qdrant_index.py` | Qdrant integration tests | ~150 |
| `tests/test_redis_session.py` | Redis session tests | ~100 |
| `tests/test_redis_bus.py` | Redis pub/sub tests | ~80 |
| `tests/test_agent_registry.py` | Agent registry tests | ~80 |
| `tests/test_indexer.py` | Library indexer tests | ~120 |

### Existing Files to Modify

| File | Changes |
|------|---------|
| `src/omega/library/indexer.py` | Replace bag-of-words with fastembed, fix hybrid scoring, fix DATA_DIR |
| `src/omega/library/library.py` | Wire Qdrant into `search()` |
| `src/omega/oracle/session_manager.py` | Add Redis hot tier |
| `src/omega/oracle/entity_registry.py` | Add semantic routing |
| `mcp/omega_hub/server.py` | Fix HALL_OF_RECORDS path, add agent discovery tools |
| `deploy/infra/docker-compose.yml` | Expose Redis port :6379 (or Quadlet) |
| `config/omega.yaml` | Redis connection config |
| `.env.example` | `REDIS_URL`, `QDRANT_URL` |

---

## §11 Total Effort Estimate

| Campaign | Files to Create | Files to Modify | Est. Sessions | Test Count |
|----------|----------------|----------------|---------------|------------|
| **Phase A**: Prerequisites | 0 | 4 | 0.5-1 session | 0 |
| **Phase B**: Database Wiring | 2 | 3 | 2-3 sessions | 18+ |
| **Phase C**: Cross-CLI Bus | 3 | 1 | 2-3 sessions | 12+ |
| **Phase D**: Neural Search | 2 | 2 | 2-3 sessions | 5+ |
| **Total** | **~12 new files** | **~10 modified files** | **~7-10 sessions** | **35+ new tests** |

---

*The containers are running, the libraries are installed, the architecture is planned. What remains is the wiring — the pipeline from data → database → discovery. This review is the blueprint for that wiring.*
