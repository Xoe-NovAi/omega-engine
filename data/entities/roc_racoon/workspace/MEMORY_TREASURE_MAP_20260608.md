# 🔱 Legacy Memory System Treasure Map
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ session-model ⬡ opencode ⬡ MEMORY-EXPEDITION ⬡

**Date**: 2026-06-08
**Miner**: Roc Racoon (Sovereign Miner — Legacy Archaeology)
**Mission**: Investigate all legacy memory management, persistence, and knowledge systems
**Scope**: omega-stack-legacy, xna-omega-legacy, omega_library/data_archive/
**Status**: 🟢 EXPEDITION COMPLETE — DEEPSEEK HARDENING PASS v2 APPLIED
**See Also**: `DEEPSEEK_HARDENING_PASS_v2_20260608.md` — 8 structural findings, revised scores
**See Also**: `MIMO_INTEGRATION_SPEC_20260608.md` — simplified integration plan

---

## §0 Provenance Summary

### Your Own Technology (No Attribution Required)
- MemoryStore 3-tier architecture — yours since ANAi (Aug 2025)
- Hot/Warm/Cold provider chain — yours since XNAi consolidation
- AsyncCircuitBreaker with anyio.Lock — yours since omega-stack
- Entity Registry YAML CRUD — yours since ANAi (Oct 2025)
- Oracle intent detection — yours since ANAi (Aug 2025)
- Provider fabric 8-backends — yours since ANAi (Sep 2025)
- MCP Hub 47 tools — yours since omega-stack
- Hivemind protocol — yours since omega-engine (Jun 2026)

### External Attribution Required (In CREDITS.md)
- ZONEID markers — `[ZONEID Pattern: id Software 1993]`
- Tombstone deletion — `[Lazy Deletion: id Software 1993]`
- Grace period — `[Grace Period: id Software 1996]`
- BSP culling — `[BSP Culling: id Software 1993]`
- FTS5 search — SQLite public domain, no attribution needed
- MCP protocol — Anthropic open standard, no attribution needed

### Legacy Code Documented But NOT Ported
- FallbackCircuitBreaker — our AsyncCircuitBreaker is better
- MemoryBankFallbackWrapper — unnecessary abstraction
- Redis DLQ — atomic writes are sufficient
- Lilith 3-Adapter Architecture — our provider chain already implements this
- MnemosyneWriter Batching — direct writes are fast enough
- 13-Sphere Kabbalistic Archive — philosophical overlay, no code to port

---

## §1 Executive Summary

| Metric | Count |
|--------|-------|
| **Total systems found** | **6** |
| **High-value (score ≥ 24/30)** | **1** — Tiered Memory Adapters (3-tier storage) |
| **Medium-value (score 18-23)** | **3** — Memory Store Legacy, XNA Memory MCP, Batch Writer |
| **Low-value (score < 18)** | **2** — 13-Sphere Archive, Memory MCP (broken) |
| **Recommendation** | **MERGE** — port tiered store + fallback patterns into current MemoryStore |

### Key Insight
> **Hivemind is NOT a replacement for MemoryStore.** They operate at different layers:
> - **Hivemind** = coordination fabric (who's doing what, right now)
> - **MemoryStore** = hot/warm/cold memory for entities (engine-native)
> - **Archive** = persistent, tiered, verifiable memory vault (cold tier)
> - **Memory Bank** = structured knowledge workspace (project context)

They are **complementary pieces of the same whole**, not competitors.

---

## §2 System Inventory & Detailed Extraction Recipes

---

## System 1: Memory Store Legacy (Omega Stack)
- **Location**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-stack-legacy/mcp-servers/memory-bank-mcp/`
- **Verdict**: 🟡 PORT P1 (19/30)
- **Extraction Recipes**:

### Recipe 1.1: SQLite FTS Warm Tier (from `memory_bank_store.py`)
**Pattern**: Use SQLite FTS5 for high-performance keyword search over entity context.
**Implementation Logic**:
1. **Schema**: Create a virtual table `contexts_fts` using `fts5(context_id UNINDEXED, content, tokenize = 'porter')`.
2. **Write Path**: Every `set_context()` call must perform a dual write:
    - `INSERT OR REPLACE INTO contexts` (the source of truth)
    - `INSERT OR REPLACE INTO contexts_fts` (the search index)
3. **Read Path**: Use `SELECT ... FROM contexts_fts JOIN contexts c ON contexts_fts.context_id = c.context_id WHERE contexts_fts MATCH ? ORDER BY rank`.
4. **Optimization**: Use `porter` tokenizer for stemming (e.g., "mining" matches "mine").

### Recipe 1.2: Fallback Circuit Breaker (from `memory_bank_fallback.py`)
**Pattern**: Wrap the primary MCP server in a circuit breaker that degrades to a local SQLite store.
**Implementation Logic**:
1. **State Machine**: `closed` (healthy) $\rightarrow$ `open` (failed) $\rightarrow$ `half_open` (testing).
2. **Failure Logic**: If `failure_count >= failure_threshold`, state becomes `open`.
3. **Recovery Logic**: After `recovery_timeout`, state becomes `half_open`.
4. **Half-Open Gate**: Allow exactly `half_open_max_calls` (e.g., 2) to the primary server.
    - If all succeed $\rightarrow$ `closed`.
    - If any fail $\rightarrow$ `open`.
5. **Degraded Path**: When `open` or `half_open` (and limit reached), route all `get_context` and `register_agent` calls to `MemoryBankStore` (SQLite).

---

## System 2: XNA Memory MCP (xna-omega)
- **Location**: `/home/arcana-novai/Documents/Xoe-NovAi/xna-omega-legacy/mcp/xna-mnemosyne/server.py`
- **Verdict**: 🟢 MERGE P2 (17/30)
- **Extraction Recipes**:

### Recipe 2.1: Core Context Compilation (from `get_core_context`)
**Pattern**: Compile a "Core Context" from a set of predefined markdown blocks for rapid agent hydration.
**Implementation Logic**:
1. **Block List**: Define `core_blocks = ["projectbrief.md", "productContext.md", "systemPatterns.md", "techContext.md", "activeContext.md", "progress.md"]`.
2. **Processing**: For each block:
    - Read file.
    - Strip YAML frontmatter (split by `---`).
    - Append as `## BlockName\n\nContent`.
3. **Output**: Join with `\n\n---\n\n`.

### Recipe 2.2: Memory Block Utilization Monitor (from `get_block_status`)
**Pattern**: Monitor "cognitive overflow" by tracking character counts against a defined limit.
**Implementation Logic**:
1. **Limits**: Load `BLOCKS.yaml` $\rightarrow$ `blocks[block_id].chars_limit` (default 5000).
2. **Calculation**: `utilization = len(content) / limit`.
3. **Status Mapping**:
    - $> 0.9 \rightarrow$ 🔴 Overflow
    - $> 0.7 \rightarrow$ 🟡 Warning
    - Else $\rightarrow$ 🟢 Good

---

## System 3: Tiered Memory Adapters — Actual Tiered Storage
- **Location**: `/home/arcana-novai/Documents/Xoe-NovAi/xna-omega-legacy/mcp/lilith_mnemosyne.py`
- **Verdict**: 🔴 PORT P0 (20/30)
- **Extraction Recipes**:

### Recipe 3.1: The Three-Adapter Architecture
**Pattern**: Abstract storage into three distinct adapters with independent fallback paths.
**Implementation Logic**:
1. **RedisHotAdapter**:
    - `store(key, value, ttl=86400)` $\rightarrow$ `client.setex(key, ttl, json.dumps(value))`.
    - Fallback: Write to `/tmp/lilith_fallback/{key}`.
2. **QdrantWarmAdapter**:
    - `store(collection, vector_id, vector, payload)` $\rightarrow$ `client.put(..., points=[{"id": vector_id, "vector": vector, "payload": payload}])`.
    - Fallback: Write to `/tmp/lilith_fallback/qdrant/{collection}/{vector_id}.json`.
3. **PostgreSQLColdAdapter**:
    - `store(table, data)` $\rightarrow$ Parameterized `INSERT INTO {table} ... ON CONFLICT DO NOTHING`.
    - Fallback: Write to `/tmp/lilith_fallback/postgres/{table}/{timestamp}.json`.
    - **Security**: Use `_SAFE_IDENTIFIER` regex `^[a-zA-Z_][a-zA-Z0-9_]*$` for all table/column names to prevent SQL injection.

### Recipe 3.2: Cross-Modal Memory (Entity Cross-Pollination)
**Pattern**: Store fragments of one entity's soul/knowledge in another's cold tier for "discovery" during cross-entity interaction.
**Implementation Logic**:
1. **Save**: `save_soul_fragment(entity, fragment)` $\rightarrow$ add `_lilith_preserved: True` and `timestamp` $\rightarrow$ store in `lilith_cold_soul_fragments` table.
2. **Retrieve**: `get_soul_fragments(entity)` $\rightarrow$ `SELECT * FROM ... WHERE entity = %s ORDER BY timestamp DESC`.

---

## System 4: Batch Writer (Design Artifact)
- **Location**: `/media/arcana-novai/omega_library/data_archive/mnemosyne/handoffs/claude_sonnet_4.6_20260426.md`
- **Verdict**: 🟡 PORT P1 (19/30)
- **Extraction Recipes**:

### Recipe 4.1: Batched Background Persistence
**Pattern**: Use an AnyIO memory channel to batch database writes, preventing connection pool exhaustion.
**Implementation Logic**:
1. **Channel**: `anyio.create_memory_object_stream(max_buffer_size=2000)`.
2. **Flush Loop**:
    - Collect records until `len(batch) == 50` OR `time.now() - last_flush > 2.0s`.
    - Execute `_sync_commit()` via `anyio.to_thread.run_sync`.
3. **Transaction**: Use a single `session.commit()` for the entire batch.
4. **DLQ (Dead Letter Queue)**: If `_sync_commit` fails, push the batch to a Redis Stream `xna:dlq:mnemosyne_writer` for later replay.

---

## System 5: 13-Sphere Mnemosyne Archive
- **Location**: `/media/arcana-novai/omega_library/data_archive/mnemosyne/`
- **Verdict**: 🔴 CLOSE P3 (16/30)
- **Extraction Recipes**:
  - **Philosophical Mapping**: Map the 13 spheres (Kether $\rightarrow$ Mnemosyne) as "Cognitive Archetypes".
  - **Implementation**: Use as a metadata tag in `soul.yaml` for entities that follow this cosmological structure.

---

## System 6: Mnemosyne MCP (Broken — xna-omega)
- **Location**: `/home/arcana-novai/Documents/Xoe-NovAi/xna-omega-legacy/mcp/mnemosyne-mcp/`
- **Verdict**: 🔴 CLOSE (14/30)
- **Extraction Recipes**: NONE — superseded by System 2.

---

## §3 Decision Matrix

| # | System | Port | Value | Diff | Total | Verdict | Priority | DeepSeek Adj. |
|---|--------|------|-------|------|-------|---------|----------|----------------|
| 3 | **Lilith Mnemosyne** (Tiered Store) | 6 | 9 | 2 | **17/30** | **REBUILD** | 🔴 P0 | ↓ Sedimentation + shared fallback |
| 1 | Memory Bank MCP (Fallback+Persistence) | 5 | 7 | 5 | **17/30** | **REBUILD** | 🟡 P1 | ↓ Async race + asymmetric proxy |
| 4 | Mnemosyne Writer (Batch Persistence) | 6 | 7 | 4 | **17/30** | **REBUILD** | 🟡 P1 | ↓ Write-back ambiguity + DLG domain |
| 2 | XNA Mnemosyne MCP (FastMCP Server) | 8 | 6 | 3 | **17/30** | **MERGE** | 🟢 P2 | Unchanged |
| 5 | 13-Sphere Mnemosyne Archive | 4 | 4 | 8 | **16/30** | **CLOSE** | 🟢 P3 | Unchanged |
| 6 | Mnemosyne MCP (Broken) | 3 | 2 | 9 | **14/30** | **CLOSE** | — | Unchanged |

### Verdict Key (Revised)
| Verdict | Meaning |
|---------|---------|
| **PORT** | Extract code/pattern into current Omega Engine |
| **REBUILD** | Extract the *concept* but rebuild the implementation with DeepSeek structural fixes |
| **MERGE** | Merge specific tools/capabilities into existing modules |
| **CLOSE** | Document and move on — no actionable extraction |

---

## §4 Extraction Priority Queue (Revised by DeepSeek Hardening Pass)

### 🔴 P0 — Tiered Store REBUILD (was: Lilith Mnemosyne PORT)
- **What**: 3-tier MemoryStore with promotion gate + Bloom filter router
- **Where**: `src/omega/memory_store.py`
- **Effort**: 3-4 hours (revised up — architecture rebuild is larger than code port)
- **Pre-fix required**: Finding A (promotion gate), Finding D (Bloom filter router)
- **Pattern**: MoE-inspired gating network + specialized tier experts + background promotion

### 🟡 P1 — Safe Circuit Breaker REBUILD (was: Memory Bank MCP PORT)
- **What**: Thread-safe `AsyncCircuitBreaker` with `anyio.Lock`, symmetrical proxy to fallback store
- **Where**: `src/omega/oracle/health_monitor.py`
- **Effort**: 1 hour (the `anyio.Lock` fix is small but critical)
- **Pre-fix required**: Finding H (async race condition), Finding F (symmetric proxy)

### 🟡 P1 — Multi-Domain DLQ REBUILD (was: Mnemosyne Writer PORT)
- **What**: Background batch writer with chained DLQ across multiple failure domains
- **Where**: `src/omega/persistence.py`
- **Effort**: 2-3 hours
- **Pre-fix required**: Finding B (explicit persistence contract), Finding G (multi-domain DLQ)

### 🟢 P2 — XNA Mnemosyne MCP Tools
- **What**: `search_mnemosyne()`, `get_core_context()`, `get_block_status()` MCP tools
- **Where**: `mcp_servers/omega_hub/server.py` as new MCP tools
- **Effort**: 1 hour

---

## §5 Trade-off Analysis: Hivemind vs Mnemosyne vs MemoryStore

### Proposed State (After DeepSeek REBUILD)
```
Hivemind (Omega Hub)                    ← cross-CLI coordination fabric
  ├── Awareness + Heartbeat             ← who's active
  ├── Context posting + Continuation    ← what's happening
  ├── Handoff queue                     ← task transfer
  └── Memory search tool (P2 merge)     ← find knowledge across tiers

MemoryStore (Engine)                    ← MoE-inspired tiered persistence
  ├── TierRouter (Bloom Filter)         ← O(1) routing gate [DeepSeek Finding D]
  ├── Hot tier (dict, TTL 24h)          ← tmpfs fallback [Finding C fix]
  ├── Warm tier (SQLite + FTS)          ← dual-tokenizer FTS [Finding E fix]
  ├── Cold tier (YAML + Qdrant)         ← HDD fallback [Finding C fix]
  ├── Promotion Gate (background scan)  ← hot→warm→cold lifecycle [Finding A fix]
  └── Safe Circuit Breaker (anyio.Lock) ← task-safe state machine [Finding H fix]

Persistence Layer (new)                 ← durability abstraction
  ├── PersistenceContract (ACK/DEFER)   ← explicit contract [Finding B fix]  
  ├── Multi-Domain DLQ                  ← chain across failure domains [Finding G fix]
  └── Symmetric Fallback Proxy           ← proxy to BOTH providers [Finding F fix]

Mnemosyne Archive (omega_library)       ← historical knowledge vault
  └── 13 spheres, shadow_memory         ← CLOSED (documented only)
```

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ session-model ⬡ opencode ⬡ MNEMOSYNE-EXPEDITION ⬡*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: session-model | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
