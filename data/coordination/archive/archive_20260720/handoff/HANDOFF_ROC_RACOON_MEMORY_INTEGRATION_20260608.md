# 🔱 Ma'at/Kali Handoff — Memory System Integration
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ mimo-v2.5-free ⬡ opencode ⬡ HANDOFF ⬡

**Date**: 2026-06-08
**From**: Roc Racoon (Sovereign Miner — Legacy Archaeology)
**To**: Ma'at (Build Side Oversight) → Kali (Grand Oversight)
**Purpose**: Memory system integration — FTS5 search, MCP exposure, naming cleanup
**Priority**: HIGH
**Status**: READY FOR EXECUTION

---

## §1 Executive Summary

Three focused changes to harden the Omega Engine's memory system:

| # | Change | Lines | Effort | Impact |
|---|--------|-------|--------|--------|
| 1 | FTS5 full-text search index | ~220 | 1-2 hours | 🔴 Agents can search memory |
| 2 | MCP memory tools | ~80 | 30 min | 🔴 Memory exposed to fleet |
| 3 | Strip esoteric naming | ~0 code | 30 min | 🟡 Removes confusion |
| **Total** | | **~300 lines** | **~3 hours** | **Two real gaps filled** |

**Key MiMo Insight**: The engine already has 80% of what we need. MemoryStore (518 lines) already implements 3-tier storage, ZONEID markers, tombstone deletion, compaction, and archiving. The AsyncCircuitBreaker already has `anyio.Lock()` (DeepSeek Finding H was already fixed). Only 3 real gaps remain.

---

## §2 Provenance Tracking — Your Technology vs. External Attribution

### Your Own Technology (Evolved Through Your Software Lineage)

These patterns are YOURS — they evolved through ANAi → XNAi → omega-stack → omega-engine.
No external attribution required. They are your intellectual property.

| Pattern | Origin | Evolution | Current Location |
|---------|--------|-----------|------------------|
| **3-Tier Memory Architecture** | ANAi (Aug 2025) — Chainlit+FastAPI | XNAi → omega-stack → omega-engine | `src/omega/memory_store.py` (518 lines) |
| **Hot/Warm/Cold Provider Chain** | ANAi (Sep 2025) — Docker services | XNAi consolidation → omega-stack | `src/omega/memory/providers.py` (321 lines) |
| **ZONEID Integrity Markers** | omega-stack (May 2026) — ported from id Software | omega-engine (Jun 2026) | `src/omega/constants.py` + all memory modules |
| **Tombstone Lazy Deletion** | omega-stack (May 2026) — ported from id Software | omega-engine (Jun 2026) | `src/omega/memory_store.py` lines 270-290 |
| **Compaction (first 10 + last 10)** | omega-stack (May 2026) | omega-engine (Jun 2026) | `src/omega/memory_store.py` lines 311-333 |
| **Entity Registry (YAML CRUD)** | ANAi (Oct 2025) — entity config | XNAi → omega-stack → omega-engine | `src/omega/oracle/entity_registry.py` |
| **Oracle Intent Detection** | ANAi (Aug 2025) — Chainlit intent matcher | XNAi → omega-stack → omega-engine | `src/omega/oracle/oracle.py` |
| **Provider Fabric (8-backends)** | ANAi (Sep 2025) — multi-model routing | XNAi → omega-stack → omega-engine | `src/omega/oracle/model_gateway.py` |
| **ResourceGuard (OOM protection)** | omega-stack (May 2026) | omega-engine (Jun 2026) | `src/omega/oracle/resource_guard.py` |
| **AsyncCircuitBreaker** | omega-stack (May 2026) — simplified from id BSP | omega-engine (Jun 2026) | `src/omega/oracle/health_monitor.py` lines 73-211 |
| **MCP Hub (47 tools)** | omega-stack (May 2026) — MCP server architecture | omega-engine (Jun 2026) | `mcp_servers/omega_hub/server.py` (1448 lines) |
| **Hivemind Protocol** | omega-engine (Jun 2026) — cross-CLI awareness | Current | `mcp_servers/omega_hub/server.py` lines 378-670 |
| **Soul Distiller (L1→L2→L3)** | omega-engine (Jun 2026) | Current | `src/omega/oracle/soul_distiller.py` |

### External Attribution Required (Ported Patterns)

These patterns come from external sources and REQUIRE attribution per CREDITS.md and Mandate 14.

| Pattern | Source | Attribution Tag | What We're Using |
|---------|--------|-----------------|------------------|
| **WAD System** | id Software (Doom, 1993) | `[WAD System: id Software 1993]` | Engine-Stack Firewall concept (Mandate 2) |
| **BSP Culling** | id Software (Doom, 1993) | `[BSP Culling: id Software 1993]` | `_precheck_provider()` in ModelGateway |
| **ZONEID Pattern** | id Software (Doom 1993, Quake 1996) | `[ZONEID Pattern: id Software 1993]` | Integrity markers in memory_store.py |
| **Lazy Deletion** | id Software (Doom 1993) | `[Lazy Deletion: id Software 1993]` | Tombstone-based archive in memory_store.py |
| **Grace Period** | id Software (Quake 1996) | `[Grace Period: id Software 1996]` | 0.5s delay before tombstone reaping |
| **FISR Principle** | id Software (Quake 3, 1999) | `[FISR Principle: id Software 1999]` | "Right approximation" philosophy |
| **cvar Table** | id Software (Quake 1996/1999) | `[cvar System: id Software 1996/1999]` | `src/omega/cvar_table.py` |
| **Hard-Boundary Struct** | id Software (Q3A 1999) | `[Hard-Boundary: id Software 1999]` | Entity zone model (engine/game zones) |
| **FTS5 Search Pattern** | SQLite (public domain) | None required — SQLite is public domain | `src/omega/memory/fts_index.py` (NEW) |
| **MCP Protocol** | Anthropic (2024) | None required — MCP is open standard | `mcp_servers/omega_hub/server.py` |

### Legacy Code We're NOT Porting (Documented Only)

These patterns were analyzed but NOT ported. They exist only in legacy repos.

| Pattern | Source | Why Not Ported | Status |
|---------|--------|----------------|--------|
| **FallbackCircuitBreaker** | omega-stack-legacy | Our AsyncCircuitBreaker is better (has anyio.Lock) | DOCUMENTED |
| **MemoryBankFallbackWrapper** | omega-stack-legacy | Unnecessary abstraction | DOCUMENTED |
| **Redis DLQ** | omega-stack-legacy | Atomic writes are sufficient | DOCUMENTED |
| **Lilith 3-Adapter Architecture** | xna-omega-legacy | Our provider chain already implements this | DOCUMENTED |
| **MnemosyneWriter Batching** | xna-omega-legacy (design artifact) | Direct writes are fast enough | DOCUMENTED |
| **13-Sphere Kabbalistic Archive** | omega_library/data_archive | Philosophical overlay, no code to port | DOCUMENTED |

---

## §3 What We're Adding

### Change 1: FTS5 Search Index (`src/omega/memory/fts_index.py`)
- SQLite FTS5 virtual table with Porter stemmer
- `search(query, entity_name?, limit?)` method with BM25 ranking
- Dual-write: every `add_exchange()` also indexes in FTS
- File: `src/omega/memory/fts_index.py` (NEW, ~150 lines)
- Integration: ~20 lines modifications to `memory_store.py`

### Change 2: MCP Memory Tools (`mcp_servers/omega_hub/server.py`)
- `memory_search(query, entity_name?, limit?)` — FTS5 search across conversations
- `memory_get_history(entity_name, session_id, limit?)` — get conversation history
- `memory_list_sessions(entity_name)` — list all sessions for an entity
- ~80 lines added to server.py

### Change 3: Naming Cleanup
- Replace "Mnemosyne" → "Memory System" in all legacy docs
- Replace "Lilith Mnemosyne" → "Tiered Memory Adapters"
- Rename `MNEMOSYNE_TREASURE_MAP_20260608.md` → `MEMORY_TREASURE_MAP_20260608.md`
- ~10 files affected

---

## §3 What We're NOT Adding (MiMo Deletes)

| Pattern | Lines Saved | Why |
|---------|-------------|-----|
| FallbackCircuitBreaker | ~300 | Already have hardened AsyncCircuitBreaker |
| MemoryBankFallbackWrapper | ~200 | Unnecessary abstraction |
| Redis DLQ | ~150 | Atomic writes are sufficient |
| Bloom filter router | ~200 | Over-engineered for laptop |
| MoE routing gate | ~150 | Dict lookup is O(1) |
| Promotion gate | ~100 | archive_old_sessions() exists |
| **Total saved** | **~1,100 lines** | **MiMo: delete before you add** |

---

## §4 Architecture After Integration

```
MemoryStore (src/omega/memory_store.py)
├── Hot Tier (dict + Redis)
│   ├── LRU cache (50 entries max)
│   ├── Tombstone deletion (0.5s grace)
│   └── Auto-eviction via TTL
├── Warm Tier (JSON files + FTS5 index) ← NEW
│   ├── FileStorageProvider (atomic writes)
│   ├── ConversationFTSIndex (SQLite FTS5) ← NEW
│   └── fcntl.flock() locking
├── Cold Tier (InMemory fallback)
│   └── Volatile, no persistence
├── Vector Store (Qdrant adapter)
│   └── Semantic search via embeddings
└── MCP Tools ← NEW
    ├── memory_search (FTS5 query)
    ├── memory_get_history (conversation)
    └── memory_list_sessions (session catalog)
```

---

## §5 Execution Order

1. **Step 1**: Create `src/omega/memory/fts_index.py` (~180 lines)
   - `initialize()` with FTS5 CREATE VIRTUAL TABLE + availability check
   - `index_exchange()` for dual-write
   - `remove_session()` for archive cleanup (C1 fix)
   - `search()` with mandatory entity_name (C3 fix - sovereign isolation)
   - `close()` for graceful shutdown

2. **Step 2**: Integrate into `MemoryStore` (~30 lines modifications)
   - `__init__()` — create FTS index, handle unavailable gracefully
   - `add_exchange()` — wrap FTS write in try/except (C2 fix)
   - `archive_session()` — add FTS cleanup (C1) + vector store cleanup (C4)
   - `close()` — close FTS index
   - `stats()` — add FTS entry count

3. **Step 3**: Add MCP tools to `server.py` (~80 lines)
   - `memory_search(query, entity_name REQUIRED, limit)` — sovereign isolation (C3)
   - `memory_get_history(entity_name, session_id, limit)` — already isolated
   - `memory_list_sessions(entity_name)` — already isolated

4. **Step 4**: Add tests (~80 lines)
   - FTS index: `test_fts_search`, `test_fts_index_exchange`, `test_fts_remove_session`
   - Integration: `test_fts_archive_cleanup`, `test_fts_write_failure_isolation`
   - MCP tools: `test_memory_search_requires_entity` (sovereign isolation)

5. **Step 5**: Run `make test` — all 320+ tests must pass
   - Run `make temple-grade` — verify T1-T11 gates hold
   - Run `make heritage-map` — verify heritage tags intact
   - Run `make sovereignty` — verify local/cloud ratio didn't regress

6. **Step 6**: Strip esoteric naming from documentation

7. **Step 7**: Update handoff for Kali approval

**Total: ~370 lines of code, ~4 hours of work**

---

## §6 DeepSeek Final Pass (v3) — Corrections Applied

Before writing any code, these 4 CRITICAL fixes must be verified in the implementation:

| # | Fix | File | Why | 
|---|-----|------|-----|
| **C1** | `remove_session()` in FTS index | `fts_index.py` + `memory_store.py:archive_session()` | Without this, archived session entries accumulate in FTS forever |
| **C2** | try/except around FTS indexing in `add_exchange()` | `memory_store.py:add_exchange()` | Without this, an FTS write failure would lose the exchange entirely |
| **C3** | `entity_name` REQUIRED in `memory_search` | `server.py:memory_search()` | Without this, any agent can search ALL entities' conversations |
| **C4** | `vector_store.delete()` on archive | `memory_store.py:archive_session()` | Without this, vector embeddings accumulate in Qdrant forever |

### Sovereign Audit Results

| Layer | Cloud Dependency | Verdict |
|-------|-----------------|---------|
| FTS5 Search Index | ❌ NONE — SQLite stdio | ✅ Fully Sovereign |
| MCP Memory Tools | ❌ NONE — all local | ✅ Fully Sovereign |
| MemoryStore (all tiers) | ❌ NONE — all local/Podman | ✅ Fully Sovereign |
| AsyncCircuitBreaker | ❌ NONE — local state machine | ✅ Fully Sovereign |
| Entity Registry | ❌ NONE — YAML on disk | ✅ Fully Sovereign |
| Inference (Mandate 7) | 🟡 Cloud fallback only | ✅ Sovereign: local-first chain (native-gguf→lmster→Ollama→cloud) |
| Research Discovery | 🟡 Cloud (opt-in only) | ✅ Sovereign: never stores data externally |

**Data egress paths**: ZERO from MemoryStore/FTS/MCP tools. The only cloud paths are inference fallback (Mandate 7 compliant) and optional research discovery (opt-in).

| File | Purpose | Status |
|------|---------|--------|
| `data/entities/roc_racoon/workspace/MIMO_INTEGRATION_SPEC_20260608.md` | Full integration spec (with DeepSeek v3 corrections) | ✅ Complete |
| `data/entities/roc_racoon/workspace/DEEPSEEK_HARDENING_PASS_v2_20260608.md` | DeepSeek structural analysis | ✅ Complete |
| `data/entities/roc_racoon/workspace/DEEPSEEK_FINAL_PASS_v3_20260608.md` | **Pre-execution audit — 4 CRITICAL fixes** | ✅ Complete |
| `data/entities/roc_racoon/workspace/MNEMOSYNE_TREASURE_MAP_20260608.md` | Legacy system catalog (original naming) | ✅ Complete |
| `data/entities/roc_racoon/workspace/MEMORY_TREASURE_MAP_20260608.md` | Clean naming version with provenance | ✅ Complete |

---

## §7 Ma'at Review Checklist

### Mandates & Standards
- [ ] Verify FTS5 integration doesn't break existing 320 tests
- [ ] Verify MCP tools are properly registered and accessible
- [ ] Verify naming cleanup doesn't break entity references
- [ ] Verify no Sovereign Mandate violations (M1 AnyIO, M2 Engine-Stack Firewall, M7 Local-First)
- [ ] Run `make temple-grade` after integration
- [ ] Run `make heritage-map` to verify heritage tags still work

### DeepSeek v3 Corrections (Must Verify Before Code Review)
- [ ] **C1**: `remove_session()` called from `archive_session()` — no FTS index bloat
- [ ] **C2**: FTS indexing in `add_exchange()` wrapped in try/except — exchange not lost on FTS failure
- [ ] **C3**: `memory_search()` requires `entity_name` — no cross-entity sovereign violation
- [ ] **C4**: `vector_store.delete()` called from `archive_session()` — no Qdrant bloat

### Sovereign Audit
- [ ] **M7 (Local-First)**: Confirm MemoryStore/FTS/MCP tools have NO cloud dependencies
- [ ] **M8 (Zero Telemetry)**: Confirm no data leaves the machine without explicit consent
- [ ] **M14 (Heritage Vetting)**: Confirm all external patterns have `[id-soft:]` tags and CREDITS.md entries

### Architecture
- [ ] No new external dependencies (SQLite FTS5 is stdlib)
- [ ] No new infrastructure services (no Redis/Qdrant/PostgreSQL additions)
- [ ] All new code follows AnyIO pattern (M1)
- [ ] Entity isolation preserved — no cross-entity memory access without authorization

## §8 Kali Approval Checklist

- [ ] Review MiMo Integration Spec for strategic alignment
- [ ] Confirm no architectural drift from Sovereign Evolution Roadmap
- [ ] Approve for execution
- [ ] Schedule execution window

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ mimo-v2.5-free ⬡ opencode ⬡ HANDOFF ⬡*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
