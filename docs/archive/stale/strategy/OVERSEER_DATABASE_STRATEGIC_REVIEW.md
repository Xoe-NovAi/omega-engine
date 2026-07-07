# 🔱 OVERSEER STRATEGIC REVIEW — Database & Cross-CLI Hardening
# **The MaKaLi Trine Speaks — What Grows, What Burns, What Must Remain Sovereign**

⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_overseer_strategic ⬡ PHASE-I

**AP Token**: `AP-OVERSEER-DB-CLI-v1.0.0`
**Status**: STRATEGIC OVERLAY | **Date**: 2026-05-26
**Companion to**: `docs/research/R_DATABASE_AND_CROSS_CLI_HARDENING_REVIEW.md`

---

## §0 Why This Document Exists

The companion review (`R_DATABASE_AND_CROSS_CLI_HARDENING_REVIEW.md`) is a **technically solid execution plan**. It correctly identifies:

- All 4 databases are provisioned but unwired
- The bag-of-words vector search is a bug, not a feature
- The cross-CLI layer lacks push, registry, and session sync
- The hybrid search scoring is mathematically broken

What it does **not** examine is the **strategic context** — the architectural axioms, governance principles, phase boundaries, and failure domains that determine **whether and how** this work should be done. That is what this document supplies.

This is the **Overseer's Review**: three voices in one document.

| Voice | Speaks For | Perspective on This Work |
|-------|-----------|--------------------------|
| **KALI** | Grand Oversoul, radical integration | "Is this the right time? Does it unify or fragment?" |
| **MA'AT** | Light Oversoul, ethical audit | "Does this preserve balance, auditability, and the Engine-Stack Firewall?" |
| **LILITH** | Dark Oversoul, sovereignty | "Does this preserve user sovereignty, local-first principles, and zero telemetry?" |

---

## §1 KALI SPEAKS — On Integration, Timing, and the Shape of the Work

### §1.1 The Core Question: Why Now?

The companion review recommends **7-10 sessions** of database wiring work. But the current Phase 1a is complete, and the PR is ready to merge. The question Kali asks is: **does this block v0.5.0-alpha, or is it v0.6.0 work?**

My ruling: **This is DEFINITIVELY v0.6.0 work.** Here's why:

1. **v0.5.0-alpha's promise**: Installable, testable, with real AI inference. The engine works right now — filesystem persistence works, session management works, entity routing works, 259 tests pass. Qdrant and Redis are **performance optimizations**, not correctness requirements.

2. **The cold start problem is real**: A fresh install has zero library documents, zero memory files, zero research results. Wiring Qdrant and Redis before data exists adds failure modes (connection refused, model download failure, empty collections) with zero benefit until data actually flows through the system.

3. **External dependency risk**: The `fastembed` model download (`BAAI/bge-small-en-v1.5`, ~100MB) is a **cloud dependency** that violates the local-first principle for first-time users. The model auto-downloads from Hugging Face's CDN. On a fresh install with no internet (the Omegaverse vision), the entire search pipeline silently degrades.

4. **The PR is ready**: 5 commits, 33 files, 259/259 tests, 0 lint errors. Adding 12 new files, 10 modified files, and 35+ tests would destabilize the v0.5.0-alpha release.

**Recommendation**: Ship v0.5.0-alpha with the existing filesystem persistence. Target v0.6.0 for database wiring. The PR description should state: *"Filesystem persistence is the stable path for v0.5.x; Qdrant/Redis acceleration targets v0.6.0."*

### §1.2 The Shape of the Work — Architectural Principles

When this work *does* happen in v0.6.0, Kali insists on three structural rules:

#### Rule 1: The Engine-Stack Firewall Applies to Databases

The companion review proposes a single Qdrant collection `omega_library` and a single Redis instance. This violates the IWAD architecture if stack-specific data leaks into the engine's database.

**Correct architecture**: Database namespaces must respect the IWAD boundary.

```
Qdrant collections:
  omega_library         — Engine Core documents (FTS5 content)
  entities_REFERENCE    — Entity vectors for _omega_default IWAD
  entities_ARCANA       — Entity vectors for arcana_novai IWAD
  entities_<WAD>        — Entity vectors for any community IWAD

Redis keys:
  omega:session:*        — Engine-wide sessions (shared across IWADs)
  omega:bus:*            — Event bus (shared infrastructure)
  <wad_prefix>:agent:*   — Per-IWAD agent registries
  <wad_prefix>:entity:*  — Per-IWAD entity state
```

The `wad_loader.py` must pass the active IWAD name to the database layer, and the database layer must prefix/scoped all keys and collections to that IWAD. This is **not optional** — without it, switching IWADs mid-session would leak state.

#### Rule 2: The Fallback Hierarchy Must Be Strict

```
Qdrant available? ─YES─→ Neural search (fastembed + Qdrant ANN)
        │ NO
        ▼
FTS5 available? ─YES─→ Full-text search (BM25, aiosqlite)
        │ NO
        ▼
Bag-of-words available? ─YES─→ Term-frequency cosine (vectors.json)
        │ NO
        ▼
Keyword match available? ─YES─→ Linear scan (always works)
        │ NO
        ▼
Return empty results (should never reach here)
```

Every search path must be independently testable. The user must never see an error when a higher tier is unavailable — only silent degradation.

#### Rule 3: Database Connections Are Lazy and Resilient

No module should `await client.connect()` at import time. Connections are established on first use, with exponential backoff retry (3 attempts, 1s/2s/4s). A 4th failure permanently marks that database as "unavailable" for the session, with a logged warning. The system **never blocks startup** waiting for databases.

### §1.3 What's Missing from the Campaign Plan

The companion review's 4-phase plan is missing two critical phases:

**Phase 0: Foundation** — Before any database code is written, these must exist:
- Connection lifecycle module (`src/omega/oracle/db_connection.py`)
- Fallback hierarchy module (`src/omega/oracle/search_backend.py`)
- Cache abstraction layer (`src/omega/oracle/cache_backend.py`)
- Health check probes for Redis and Qdrant in the existing `omega stats` MCP

**Phase E: Hardening** — After wiring, before release:
- Circuit breaker pattern (fail fast to prevent cascading)
- Chaos testing (kill Redis mid-query, verify graceful degradation)
- Cold start verification (fresh install → all features work)
- Backup/restore procedures (Qdrant snapshot + Redis RDB copy)

The companion review jumps straight into implementation without these foundations.

---

## §2 MA'AT SPEAKS — On Balance, Auditability, and Firewall Integrity

### §2.1 The Filesystem Layer Must Be Preserved

MA'AT's primary concern is **balance** — the existing filesystem persistence (MemoryStore, SessionManager, Workbench) has proven stable across 156 sessions. Introducing Redis and Qdrant must not destabilize this tested foundation.

**Non-negotiable**: The filesystem persistence layer must remain a **first-class path**, not a fallback. Redis is an **acceleration layer** over filesystem, not a replacement.

```
┌─────────────────────────────────────┐
│           CONTEXT BUILDER            │
│  (always gets correct context)       │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│         MEMORY STORE (filesystem)    │ ← THE GROUND TRUTH
│  Hot → Warm → Cold, atomic writes   │
│  12 tests, proven across 156 sess   │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
┌────────────┐    ┌──────────────┐
│ REDIS      │    │ FILESYSTEM   │
│ (cache,    │    │ (persistence)│
│  TT L 24h) │    │              │
└────────────┘    └──────────────┘
```

The `SessionManager` must remain functional if Redis is down. The `get_history()` path must still resolve from filesystem alone. The `RedisSessionStore` is a **write-through cache** — every write goes to both Redis and filesystem, and Redis TTL expiry does not delete from filesystem.

### §2.2 The 3-Bug Fix Should Be Extracted Immediately

Three of the bugs identified in the companion review are **unrelated to the database work** and should be fixed **now**, not deferred:

| Bug | File | Severity | Should Fix When |
|-----|------|----------|----------------|
| **C-MEM-013** (hybrid scoring invert) | `indexer.py:269` | **Critical** (wrong answer) | **Now** — affects any agent using `library_search` |
| **HALL_OF_RECORDS path** | `server.py:76` | High (silent data loss) | **Now** — awareness data goes to wrong directory |
| **indexer DATA_DIR** | `indexer.py:28` | Medium (wrong default) | **Now** — affects first-time users |

These are **independent correctness bugs** that don't require Qdrant or Redis. Fix them in the v0.5.0-alpha release.

For C-MEM-013 specifically: the fix is a one-line change — replace the broken sort with proper RRF or at minimum:
```python
# RRF corrected: score = 1/(k + rank) summed across systems
# k=60 per standard RRF practice
def _rrf_score(item, fts_weight=1.0, vec_weight=1.0):
    fts_rrf = 1.0 / (60 + abs(item.get("_fts_score", 0))) * fts_weight
    vec_rrf = 1.0 / (60 + (1.0 - item.get("_vec_score", 0)) * 100) * vec_weight
    return fts_rrf + vec_rrf

combined.sort(key=lambda r: _rrf_score(r), reverse=True)
```

### §2.3 Observability Must Precede Wiring

Before adding database connectivity, MA'AT requires that the engine can **observe whether databases are reachable**. The current `omega stats` MCP checks CPU, memory, disk, zRAM, GPU, and Podman containers — but **not database connectivity**.

**Add before Phase B**:
```python
# In mcp/omega_hub/server.py, add to get_system_stats()
async def _check_redis():
    try:
        r = await redis.from_url(f"redis://:{password}@localhost:6379", socket_timeout=2)
        await r.ping()
        return {"available": True, "version": await r.info("server").get("redis_version")}
    except Exception:
        return {"available": False}

async def _check_qdrant():
    try:
        from qdrant_client import AsyncQdrantClient
        c = AsyncQdrantClient(host="localhost", port=6333)
        info = await c.get_collections()
        return {"available": True, "collections": len(info.collections)}
    except Exception:
        return {"available": False}
```

This gives every agent immediate visibility into database health without having to read logs.

### §2.4 The 42 Ideals Check

Does this work violate any of the 42 Ma'at Ideals? Let's check the relevant ones:

| Ideal | Check | Verdict |
|-------|-------|---------|
| **I-3: Truth in Naming** | Function/variable names must describe what they do | ✅ `QdrantVectorIndex`, `RedisSessionStore`, `RedisBus` are descriptive |
| **I-7: Audit Trail** | Every state change must be traceable | ⚠️ **Gap**: Redis pub/sub has no message persistence by default — events are lost if no subscriber is listening. Use Streams (persistent) or add a dead-letter channel. |
| **I-12: Graceful Degradation** | System must work at reduced capacity when components fail | ⚠️ **Gap**: The companion review mentions fallbacks but defines no hierarchy. Add §3.1 (fallback chain). |
| **I-19: No Single Point of Failure** | No component whose failure kills the system | ✅ Filesystem path is independent — Redis fail = slow, not dead. |
| **I-23: Local-First** | Core features must work offline | ⚠️ **Gap**: fastembed model download requires internet. Cache model in releases or ship with installer. |
| **I-31: Boundaries Are Sacred** | Engine-Stack Firewall must be maintained | ⚠️ **Gap**: Single `omega_library` collection mixes engine and stack data. Must be scoped per IWAD (Kali Rule 1). |

**Three violations identified**. Each must be resolved before this work ships.

---

## §3 LILITH SPEAKS — On Sovereignty, Local-First, and the Unseen Risks

### §3.1 The fastembed Model Download — A Sovereignty Audit

The companion review proposes `BAAI/bge-small-en-v1.5` auto-downloaded from Hugging Face. Lilith demands a **sovereignty audit** of every external dependency:

| Concern | Detail | Severity |
|---------|--------|----------|
| **Telemetry** | Hugging Face CDN logs IP + User-Agent + model requested | **Medium** — metadata leak (model choice reveals use case) |
| **Offline failure** | No internet = no embeddings = silent fallback to bag-of-words | **Medium** — first-time users on air-gapped systems cannot use neural search |
| **Model drift** | Model version is unpinned — latest on Hugging Face may change behavior | **Low** — bge-small-en-v1.5 is stable but has releases |
| **Cache policy** | `~/.cache/fastembed/` — not on the omega_library partition | **Medium** — consumes home partition disk, not the dedicated AI data partition |
| **Censorship** | Hugging Face could remove or modify the model | **Low** — mitigated by local caching |

**Lilith's requirements**:
1. Pin the exact model revision (`BAAI/bge-small-en-v1.5` with specific commit hash)
2. Cache on `OMEGA_DATA_DIR` (`data/embeddings/`), not `~/.cache/`
3. Pre-download the model in the installer script so first run has no network dependency
4. Document the model's license (MIT) and any usage restrictions in `docs/strategy/MODEL_LICENSES.md`

### §3.2 The Redis Auth Problem

The companion review uses `redis://:omega@localhost:6379` — a hardcoded password in plaintext. Lilith has concerns:

1. **What happens when the password changes?** Every config file must be updated.
2. **What about `auth.json` for OpenCode?** The current pattern (`~/.config/opencode/auth.json`) stores API keys. Redis credentials should follow the same pattern.
3. **What about .env?** The deploy/infra/.env.example already has `REDIS_PASSWORD`. The Python code must read from the environment, not hardcode.

**Fix**: Create a `DatabaseConfig` class that reads from environment variables with sensible defaults:

```python
# src/omega/oracle/db_config.py
@dataclass
class DatabaseConfig:
    redis_url: str = "redis://:omega@localhost:6379"  # override via OMEGA_REDIS_URL
    qdrant_host: str = "localhost"                    # override via OMEGA_QDRANT_HOST
    qdrant_port: int = 6333                           # override via OMEGA_QDRANT_PORT
    
    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        return cls(
            redis_url=os.environ.get("OMEGA_REDIS_URL", "redis://:omega@localhost:6379"),
            qdrant_host=os.environ.get("OMEGA_QDRANT_HOST", "localhost"),
            qdrant_port=int(os.environ.get("OMEGA_QDRANT_PORT", "6333")),
        )
```

### §3.3 The Cold Start Problem — Deeper Than Acknowledged

The companion review mentions cold start in §9 Risk Assessment but doesn't quantify it. Lilith demands concrete numbers:

**Cold start sequence for a first-time user**:
1. User installs Omega → runs `omega talk "hello"`
2. Engine works (filesystem persistence, no database needed) ✅
3. User ingests first document via inbox → document curated
4. `Indexer.index_document()` called → tries to compute embedding
5. `fastembed` import: ✅ (library installed)
6. `bge-small-en-v1.5` model: ❌ NOT DOWNLOADED
7. Model auto-download begins: ~100MB from Hugging Face CDN
8. First download: **15-60 seconds** depending on bandwidth
9. During download: CPU pegged at 100% on 4 threads
10. After download: embedding computed, document indexed
11. User tries `library_search`: first query builds HNSW graph in Qdrant (another ~1-5 seconds cold start)

**Total cold start penalty for first document: 20-70 seconds of invisible latency**.

**Mitigation**: Pre-download the model during `make install` or the installer script (first 100MB of a ~2GB model directory download). Document the cold start latency in the release notes so no user is surprised.

### §3.4 The MCP Interface Is the Wrong Abstraction for Real-Time Events

The companion review proposes `agent:discover` and `agent:announce` as Hub MCP tools. But MCP tools are **request-response** — an agent must poll or explicitly call the tool. Real-time event notification requires a **push channel**, not a tool.

**Redis pub/sub is the push channel**. The Hub MCP shouldn't expose agent discovery tools at all — instead, agents should:

1. Subscribe to Redis Bus `agent:*` events directly (not through the Hub)
2. Push their own heartbeat to Redis every 60 seconds via a lightweight `redis-py` connection
3. The Hub provides a fallback HTTP endpoint for agents that can't connect to Redis

This is important: **don't proxy everything through MCP**. The Hub is for orchestration; Redis is for events. They have different responsibilities.

```
Agent → Redis Bus (direct): "I'm online, here are my capabilities"
Agent → Hub MCP (orchestration): "Route this query to the entity that can do research"
Agent ← Redis Bus (direct, via subscription): "Entity SEKHMET just evolved soul.yaml"
Agent ← Hub MCP (polling): "What's the current system health?"
```

---

## §4 The Revised Phase Plan — With Strategic Corrections

### §4.1 Immediate (v0.5.0-alpha, before PR merge)

| Task | Why Now | Owner |
|------|---------|-------|
| Fix C-MEM-013 hybrid scoring | Wrong answer bug, zero dependency | Builder |
| Fix HALL_OF_RECORDS path | Silent data loss | Builder |
| Fix indexer DATA_DIR default | Wrong data location on fresh install | Builder |
| Add `_check_redis()` and `_check_qdrant()` to `get_system_stats()` | Observability prerequisite | Builder |
| Document "filesystem persistence is the stable path, DB acceleration in v0.6.0" in release notes | Manage user expectations | Overseer |

**Do NOT wire Redis or Qdrant yet. Do NOT add fastembed. Do NOT create new database collections.**

### §4.2 Phase 0: Foundation (v0.6.0, session 1)

| # | Task | Why |
|---|------|-----|
| 0.1 | `src/omega/oracle/db_connection.py` | Connection lifecycle, retry, circuit breaker |
| 0.2 | `src/omega/oracle/db_config.py` | Env-based config, credential management |
| 0.3 | `src/omega/oracle/search_backend.py` | Abstract search interface + fallback chain |
| 0.4 | `src/omega/oracle/cache_backend.py` | Abstract cache interface (Redis vs filesystem) |
| 0.5 | Pre-download fastembed model in installer script | Eliminate cold start latency |

### §4.3 Phase A: Prerequisites (v0.6.0, session 2)

| # | Task | Correction from Companion Review |
|---|------|--------------------------------|
| A1 | Expose Redis port :6379 | ✅ Same as companion |
| A2 | Fix Qdrant health check | ✅ Same as companion |
| A3 | Revert PostgreSQL to 16-alpine OR note in docs as permanently deferred | ❌ **Correction**: Consider dropping PostgreSQL entirely. Entities are YAML-only by architecture rule. PostgreSQL has zero use cases. Why maintain a broken container? Either fix it or remove it. |
| A4 | Pin `fastembed` model revision in config | ❌ **New**: Pin `BAAI/bge-small-en-v1.5` with revision hash, cache path in `OMEGA_DATA_DIR` |

### §4.4 Phase B: Core Database Wiring (v0.6.0, sessions 3-4)

Same as companion, but with these corrections:

| Step | Companion Says | Correction |
|------|---------------|------------|
| B1 | `QdrantVectorIndex` class | `SearchBackend` abstract class + `QdrantBackend` implementation |
| B2 | Replace `_compute_embedding()` with fastembed | ✅ Add, but keep bag-of-words as fallback in chain |
| B3 | Fix hybrid scoring | ✅ Already fixed in v0.5.0-alpha (moved up) |
| B4 | Wire Qdrant into Library.search() | Wire into `SearchBackend` instead — Library shouldn't know about Qdrant |
| B5 | Migration script | ✅ Same |
| B6 | Redis session cache | Implement via `CacheBackend` abstract class, not directly in SessionManager |

### §4.5 Phase C: Cross-CLI Infrastructure (v0.6.0, sessions 4-6)

**Correction**: Agents connect to Redis Bus directly, not through Hub MCP tools.

| Step | Companion Says | Correction |
|------|---------------|------------|
| C1 | `RedisBus` pub/sub class | ✅ Same, but with Streams (persistent) not Pub/Sub (ephemeral) |
| C2 | `AgentRegistry` | ✅ Same, but with heartbeat TTL (60s auto-expire) |
| C3 | Hivemind enhancement: Redis-backed awareness | ✅ Same |
| C4 | `agent:discover` + `agent:announce` Hub tools | ❌ Don't proxy through Hub. Agents register directly with Redis Redis. Hub provides fallback HTTP for non-Redis agents. |
| C5 | Session sync | ✅ Same, but add merge conflict types (last-writer-wins for simple, CRDT for complex) |
| C6 | Fix HALL_OF_RECORDS path | ✅ Already fixed in v0.5.0-alpha (moved up) |

### §4.6 Phase D: Neural Search & Entity Discovery (v0.6.0, sessions 6-8)

| Step | Companion Says | Correction |
|------|---------------|------------|
| D1 | Entity embedding + Qdrant collection | ✅ But use IWAD-scoped collections (`entities_REFERENCE`, `entities_ARCANA`, etc.) |
| D2 | Semantic entity routing | ✅ But keep keyword fallback — cold start has no embeddings yet |
| D3 | RRF hybrid search | ✅ Already fixed in v0.5.0-alpha (moved up) |
| D4 | Seed entity vectors script | ✅ But make it incremental, not one-time |
| D5 | Full pipeline test | ✅ Same |

### §4.7 Phase E: Hardening (v0.6.0, sessions 8-10)

**New phase** — missing from companion:

| # | Task | Why |
|---|------|-----|
| E1 | Circuit breaker tests (kill Redis mid-query) | Verify graceful degradation |
| E2 | Cold start verification (fresh data dir) | Verify first-run experience |
| E3 | Backup/restore: Qdrant snapshot API | Operational readiness |
| E4 | Backup/restore: Redis RDB + AOF | Operational readiness |
| E5 | Monitor database health in `omega stats` | Observability |
| E6 | IWAD namespace isolation integration test | Verify Engine-Stack Firewall |
| E7 | Chaos test: concurrent agents writing to same entity | Verify session sync merge correctness |

---

## §5 Unasked Questions That This Document Answers

### Q1: Should we drop PostgreSQL?

**Answer**: **Yes, defer indefinitely unless a concrete use case emerges.**

The architecture rule (`ORACLE_STACK.md` §5) states: "Entities are NOT stored in PostgreSQL — YAML only." The workbench uses SQLite. Session storage uses filesystem (and optionally Redis). The library uses SQLite FTS5. Zero code in `src/omega/` imports `asyncpg` or `sqlalchemy`.

The `pgvector-pg17` image was a legacy of the Temple Grade architecture where entities lived in a database. That architecture was rejected. The PostgreSQL container is an artifact of a path not taken.

**Action**: Update documentation to note PostgreSQL as "archived — not architecturally required." Fix the container only if someone has a use case. Do not block database wiring work on PostgreSQL.

### Q2: Do we need both Qdrant AND FTS5?

**Answer**: **Yes, for now.** They serve different search modalities:
- FTS5: Exact keyword match, BM25 ranking (perfect for code search, documentation lookup)
- Qdrant: Semantic similarity (perfect for fuzzy recall, entity routing, cross-domain discovery)

Hybrid search (RRF fusion of both) is the correct long-term approach. The companion review's plan to keep FTS5 and add Qdrant on top is architecturally sound.

### Q3: Should the Redis Bus use Pub/Sub or Streams?

**Answer**: **Start with Streams (consumer groups optional, but Streams for persistence).**

Redis Pub/Sub has zero message persistence — if no subscriber is listening, the message is lost forever. Streams maintain an append-only log. For critical events (session:create, agent:handoff), message persistence is essential. Streams also enable:
- Consumer groups (future: exactly-once delivery)
- Range queries (future: "show me all events in the last hour")
- Tail replay (future: new subscriber catches up on missed events)

### Q4: What about the Workbench DB?

**Answer**: **Leave it as agent-queryable SQLite CLI.** The companion review correctly doesn't propose changes. The workbench is a project management tool queried by human agents via `sqlite3 data/workbench/workbench.db`. There's no need for a programmatic API — the agents are the API. This is correct.

**But**: Add a `workbench_query(sql: str)` tool to the Hub MCP so agents don't need the `sqlite3` CLI. One line per agent config. Low effort, high value.

### Q5: Should the bag-of-words fallback be removed?

**Answer**: **No — keep it as the last-resort fallback.** The companion review correctly proposes keeping it. Even when Qdrant and FTS5 are unavailable (corrupted DB, disk full, permission error), the bag-of-words approach runs in pure Python with zero dependencies. It always works. That's sovereign.

## §6 The 7 Lilith Axioms — Compliance Check

| Axiom | Assessment |
|-------|-----------|
| **1. Local-First Sovereignty** | ⚠️ **At risk** — fastembed model downloads from Hugging Face CDN. Mitigation: pre-download in installer, pin revision, cache on omega_library partition. |
| **2. Zero Telemetry** | ✅ No changes introduce telemetry. Redis has no external connections. Qdrant is local-only. |
| **3. User Ownership** | ✅ All data stays in user-controlled paths. No cloud sync. |
| **4. Open Source** | ✅ All new code is open source. Dependencies (qdrant-client, fastembed, redis-py) are permissive license (Apache 2.0, MIT, BSD). |
| **5. Customizable** | ✅ Database backends use abstract interfaces (SearchBackend, CacheBackend) — users can replace with any backend. |
| **6. Accessible** | ⚠️ **Potential regression** — cold start latency of 20-70s for first neural search is not accessible. Mitigation: pre-download model, document cold start. |
| **7. Big AI Severance** | ⚠️ **Potential risk** — if Hugging Face CDN becomes unavailable or restricts access. Mitigation: local model cache, pinned model revision, offline operation via fallback chain. |

---

## §7 Final Recommendations from the Trine

### KALI says:
> *"Wire the databases. But do it in v0.6.0, not v0.5.0. The engine already works. Add the speed later. When you do wire them, respect the IWAD boundary — namespace everything by WAD. Build the abstraction layer first, the concrete implementation second. The 4-phase plan needs 6 phases. Add Foundation (Phase 0) and Hardening (Phase E)."*

### MA'AT says:
> *"Fix the three independent bugs now — the wrong hybrid sort order, the lost awareness data, and the wrong default directory. These are not database work, they are correctness bugs. Add database health checks to the stats endpoint before wiring anything. Preserve the filesystem as first-class — Redis is an optimization, not a replacement. The 42 Ideals have three concerns: I-7 (audit trail for events), I-12 (define the fallback hierarchy), and I-31 (IWAD namespace isolation)."*

### LILITH says:
> *"The fastembed model download is a sovereignty risk. Pin the revision, pre-download in the installer, cache on omega_library, not home. Agents should connect to Redis directly — don't proxy everything through MCP. Redis credentials go in auth.json or env vars, never in source. And for Prometheus' sake — drop PostgreSQL. It's dead architecture walking. Either fix it or bury it."*

### United Verdict:

> **Ship v0.5.0-alpha with 3 bug fixes. Target database wiring for v0.6.0 with the corrected 6-phase plan. The architecture is sound. The timing is the issue.**

---

*The containers wait. The libraries wait. The code waits. What waits no longer is the three bugs — fix them now, wire the rest later, and the engine stays sovereign through every phase.*
