<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 MiMo Integration Spec — Memory System Hardening
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ mimo-v2.5-free ⬡ opencode ⬡ MIMO-INTEGRATION ⬡

**Date**: 2026-06-08
**Lens**: MiMo V2.5 (production pragmatism, code-first, delete before you add)
**Target**: Strip esoteric naming, port best patterns, harden MemoryStore
**Scope**: 3 focused changes — FTS5 search, MCP exposure, naming cleanup

---

## §0 MiMo Principle: The Engine Already Has 80% of What We Need

### Provenance: What's YOUR Technology vs. What's External

**YOUR Technology** (evolved through ANAi → XNAi → omega-stack → omega-engine):
- MemoryStore 3-tier architecture (518 lines) — yours since ANAi (Aug 2025)
- Hot/Warm/Cold provider chain (321 lines) — yours since XNAi consolidation
- AsyncCircuitBreaker with anyio.Lock (211 lines) — yours since omega-stack
- Entity Registry YAML CRUD — yours since ANAi (Oct 2025)
- Oracle intent detection — yours since ANAi (Aug 2025)
- Provider fabric 8-backends — yours since ANAi (Sep 2025)
- MCP Hub 47 tools — yours since omega-stack
- Hivemind protocol — yours since omega-engine (Jun 2026)

**External Attribution Required** (ported patterns):
- ZONEID markers — `[ZONEID Pattern: id Software 1993]` (in CREDITS.md §1.9)
- Tombstone deletion — `[Lazy Deletion: id Software 1993]` (in CREDITS.md §1.10)
- Grace period — `[Grace Period: id Software 1996]` (in CREDITS.md §1.10)
- BSP culling — `[BSP Culling: id Software 1993]` (in CREDITS.md §1.2)
- FTS5 search — SQLite public domain, no attribution needed
- MCP protocol — Anthropic open standard, no attribution needed

The MiMo lens reveals something the DeepSeek and first-pass analyses missed:

**The Omega Engine's MemoryStore (518 lines) already implements:**
- ✅ 3-tier storage (Hot=Redis+dict, Warm=JSON files, Cold=InMemory)
- ✅ ZONEID integrity markers (id-soft heritage)
- ✅ Tombstone-based lazy deletion with grace period
- ✅ Compaction (first 10 + last 10 + summary)
- ✅ Auto-archiving (7-day threshold)
- ✅ File locking (fcntl.flock)
- ✅ Disk space guard (10% threshold)
- ✅ Qdrant vector search adapter
- ✅ Singleton access pattern
- ✅ 12 passing tests

**The AsyncCircuitBreaker (211 lines) already implements:**
- ✅ `anyio.Lock()` for task safety (Finding H already fixed!)
- ✅ CLOSED → OPEN → HALF_OPEN state machine
- ✅ ZONEID integrity markers
- ✅ Probe limiting (half_open_max_requests=1)
- ✅ Observability integration

**What's actually MISSING (the real gaps):**
1. **FTS5 full-text search** — warm tier uses JSON files, no search capability
2. **MCP tool exposure** — MemoryStore has no MCP tools, agents can't search memory
3. **Esoteric naming** — entity names reference mythological figures

The legacy analysis over-counted complexity. The MiMo approach: **add what's missing, don't rebuild what works.**

---

## §1 Change 1: Add FTS5 Full-Text Search to Warm Tier

### What We're Porting
From `omega-stack-legacy/mcp-servers/memory-bank-mcp/memory_bank_store.py`:
- SQLite FTS5 virtual table with Porter stemmer (FTS5 is built into SQLite 3.46.1 — no extension needed)
- `search_context(query, limit)` method with BM25 ranking
- Dual-write pattern (source table + FTS index)

### DEEPSEEK FINAL PASS CORRECTIONS (Applied)
| Issue | Severity | Fix |
|-------|----------|-----|
| FTS index not cleaned on archive | 🔴 CRITICAL | Add `remove_session()` method + call from `archive_session()` |
| FTS write failure breaks add_exchange | 🔴 CRITICAL | Wrap FTS indexing in try/except in `add_exchange()` |
| No sovereign isolation on memory_search | 🔴 CRITICAL | Make `entity_name` REQUIRED, not optional |
| Vector store orphaned on archive | 🔴 CRITICAL | Add `vector_store.delete()` call in `archive_session()` |
| Tombstone state lost on restart | 🟡 HIGH | Deferred — document for future |
| No rate limiting on MCP tools | 🟡 HIGH | Not needed for MVP (single-user laptop) |

### What We're NOT Porting
- The `MemoryBankStore` class itself (our `FileStorageProvider` is better)
- The `FallbackCircuitBreaker` (our `AsyncCircuitBreaker` is already hardened)
- The `MemoryBankFallbackWrapper` (unnecessary abstraction)

### Implementation

**File**: `src/omega/memory/fts_index.py` (NEW, ~180 lines)

```python
"""Full-text search index for MemoryStore warm tier.

Uses SQLite FTS5 for high-performance keyword search over conversation history.
This is the one pattern worth porting from the legacy Memory Bank MCP.

DEEPSEEK V3 CORRECTIONS:
- remove_session() added for archive cleanup (C1)
- try/except wrapper required in caller (C2)
- entity_name is REQUIRED in search() for sovereign isolation (C3)
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
import anyio
from omega.errors import OmegaError
from omega.constants import ZONEID_MEMORY

logger = logging.getLogger(__name__)

class ConversationFTSIndex:
    """FTS5 index for conversation search. Runs alongside the JSON file store."""
    
    def __init__(self, db_path: Path):
        self._db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._lock = anyio.Lock()
        self._fts_available: bool = False
        self._entry_count: int = 0
    
    async def initialize(self) -> bool:
        """Create the FTS5 virtual table if it doesn't exist.
        
        Returns True if FTS5 is available and initialized, False if not.
        FTS5 is a compile-time option for SQLite — some builds don't include it.
        Confirmed available on this system (SQLite 3.46.1).
        """
        try:
            await anyio.to_thread.run_sync(self._initialize_sync)
            self._fts_available = True
            return True
        except Exception as e:
            logger.warning("FTS5 not available: %s. Search disabled.", e)
            self._fts_available = False
            return False
    
    def _initialize_sync(self) -> None:
        self._conn = sqlite3.connect(str(self._db_path))
        self._conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS conversation_fts 
            USING fts5(
                entity_name UNINDEXED,
                session_id UNINDEXED,
                role UNINDEXED,
                content,
                timestamp UNINDEXED,
                tokenize='porter'
            )
        """)
        # Count existing entries
        cursor = self._conn.execute("SELECT COUNT(*) FROM conversation_fts")
        self._entry_count = cursor.fetchone()[0]
        self._conn.commit()
    
    async def index_exchange(
        self, 
        entity_name: str, 
        session_id: str, 
        role: str, 
        content: str, 
        timestamp: str
    ) -> None:
        """Index a single exchange. Safe to call even if FTS unavailable."""
        if not self._fts_available:
            return
        async with self._lock:
            await anyio.to_thread.run_sync(
                self._index_exchange_sync,
                entity_name, session_id, role, content, timestamp
            )
        self._entry_count += 1
    
    def _index_exchange_sync(
        self, entity_name: str, session_id: str, 
        role: str, content: str, timestamp: str
    ) -> None:
        assert self._conn is not None
        self._conn.execute(
            "INSERT INTO conversation_fts VALUES (?, ?, ?, ?, ?)",
            (entity_name, session_id, role, content, timestamp)
        )
        self._conn.commit()
    
    async def remove_session(
        self, entity_name: str, session_id: str
    ) -> None:
        """Remove all FTS entries for a session. Called by archive_session().
        
        CRITICAL: Without this, archived session entries accumulate forever (C1).
        """
        if not self._fts_available:
            return
        async with self._lock:
            deleted = await anyio.to_thread.run_sync(
                self._remove_session_sync, entity_name, session_id
            )
        self._entry_count -= deleted
    
    def _remove_session_sync(
        self, entity_name: str, session_id: str
    ) -> int:
        assert self._conn is not None
        cursor = self._conn.execute(
            "DELETE FROM conversation_fts WHERE entity_name = ? AND session_id = ?",
            (entity_name, session_id)
        )
        self._conn.commit()
        return cursor.rowcount  # Return number of deleted rows
    
    async def search(
        self, 
        query: str, 
        entity_name: str,  # REQUIRED — sovereign isolation (C3)
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search conversations for a specific entity.
        
        entity_name is REQUIRED for sovereign isolation — agents can only
        search their own entity's conversations. Cross-entity search is a
        future feature.
        """
        if not self._fts_available:
            return []
        async with self._lock:
            return await anyio.to_thread.run_sync(
                self._search_sync, query, entity_name, limit
            )
    
    def _search_sync(
        self, query: str, entity_name: str, limit: int
    ) -> List[Dict[str, Any]]:
        assert self._conn is not None
        
        sql = """
            SELECT entity_name, session_id, role, content, timestamp,
                   rank
            FROM conversation_fts 
            WHERE conversation_fts MATCH ? AND entity_name = ?
            ORDER BY rank
            LIMIT ?
        """
        cursor = self._conn.execute(sql, (query, entity_name, limit))
        return [
            {
                "entity_name": row[0],
                "session_id": row[1],
                "role": row[2],
                "content": row[3],
                "timestamp": row[4],
                "relevance": abs(row[5]),  # FTS5 rank is negative (0 = perfect match)
            }
            for row in cursor.fetchall()
        ]
    
    async def entry_count(self) -> int:
        """Return the number of indexed entries."""
        return self._entry_count
    
    async def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            await anyio.to_thread.run_sync(self._conn.close)
            self._conn = None
```

### Integration Points

**File**: `src/omega/memory_store.py` — modify `MemoryStore.__init__()`:

```python
# After line ~120 (provider chain construction):
from .memory.fts_index import ConversationFTSIndex
self._fts_index = ConversationFTSIndex(
    _get_memory_dir() / "conversation_index.db"
)
fts_ok = await self._fts_index.initialize()
if fts_ok:
    logger.info("FTS5 search index initialized at %s", self._fts_index._db_path)
else:
    logger.warning("FTS5 not available — search disabled")
```

**File**: `src/omega/memory_store.py` — modify `add_exchange()` (AFTER save to providers):

```python
# C2 FIX: Wrap FTS indexing in try/except — secondary concern
if hasattr(self, '_fts_index'):
    try:
        await self._fts_index.index_exchange(
            entity_name=entity_name,
            session_id=session_id,
            role="user",
            content=user_message,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        await self._fts_index.index_exchange(
            entity_name=entity_name,
            session_id=session_id,
            role="assistant",
            content=response,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    except Exception:
        logger.warning(
            "FTS indexing failed for %s/%s",
            entity_name, session_id, exc_info=True
        )
```

**File**: `src/omega/memory_store.py` — modify `archive_session()` (after providers succeed):

```python
# C1 FIX: Clean up FTS index on archive
if hasattr(self, '_fts_index'):
    try:
        await self._fts_index.remove_session(entity_name, session_id)
    except Exception:
        logger.warning(
            "FTS cleanup failed for %s/%s",
            entity_name, session_id, exc_info=True
        )

# C4 FIX: Clean up vector store on archive
if self.vector_store:
    try:
        await self.vector_store.delete(
            filter_by={"entity_name": entity_name, "session_id": session_id}
        )
    except Exception:
        logger.warning(
            "Vector store cleanup failed for %s/%s",
            entity_name, session_id, exc_info=True
        )
```

### Effort
- New file: ~150 lines
- Modifications to memory_store.py: ~20 lines
- Tests: ~50 lines
- **Total: ~220 lines, 1-2 hours**

---

## §2 Change 2: Expose MemoryStore as MCP Tools

### What We're Adding
Three new MCP tools on the Omega Hub, giving agents direct memory access:

| Tool | Purpose | Signature |
|------|---------|-----------|
| `memory_search` | FTS5 search across all conversations | `(query: str, entity_name?: str, limit?: int) -> str` |
| `memory_get_history` | Get conversation history for an entity+session | `(entity_name: str, session_id: str, limit?: int) -> str` |
| `memory_list_sessions` | List all sessions for an entity | `(entity_name: str) -> str` |

### Implementation

**File**: `mcp_servers/omega_hub/server.py` — add after line ~1190 (after observability tools):

```python
# ── Memory Search Tools ──────────────────────────────────────────────

from omega.memory_store import get_memory_store

@mcp.tool()
async def memory_search(
    query: str, 
    entity_name: str,  # REQUIRED — sovereign isolation (C3)
    limit: int = 20
) -> str:
    """Search conversation memory using full-text search.
    
    Uses SQLite FTS5 with Porter stemmer for high-performance keyword search.
    
    SOVEREIGN ISOLATION: entity_name is REQUIRED. Cross-entity search is
    not available — each entity's memory is private.
    
    Args:
        query: Search query (supports FTS5 syntax: AND, OR, NOT, "exact phrase")
        entity_name: Entity to search (e.g., "sophia", "roc_racoon") — REQUIRED
        limit: Maximum results (default 20, max 100)
    """
    store = get_memory_store()
    results = await store._fts_index.search(query, entity_name, limit)
    
    if not results:
        return json.dumps({"results": [], "total": 0, "query": query, "entity": entity_name})
    
    return json.dumps({
        "results": results,
        "total": len(results),
        "query": query,
        "entity": entity_name,
    }, indent=2)


@mcp.tool()
async def memory_get_history(entity_name: str, session_id: str, limit: int = 50) -> str:
    """Get conversation history for a specific entity and session.
    
    Returns the last N exchanges from the conversation history.
    Uses hot cache for fast access, falls back to warm/cold storage.
    
    Args:
        entity_name: The entity name (e.g., "sophia", "roc_racoon")
        session_id: The session ID (e.g., "ses_20260608_roc_001")
        limit: Maximum exchanges to return (default 50)
    """
    store = get_memory_store()
    history = await store.get_history(entity_name, session_id, limit)
    
    if not history:
        return json.dumps({
            "entity": entity_name,
            "session": session_id,
            "exchanges": [],
            "total": 0,
        })
    
    return json.dumps({
        "entity": entity_name,
        "session": session_id,
        "exchanges": history,
        "total": len(history),
    }, indent=2)


@mcp.tool()
async def memory_list_sessions(entity_name: str) -> str:
    """List all sessions for an entity.
    
    Returns session IDs with metadata (first/last exchange, exchange count).
    Useful for finding relevant conversation context.
    
    Args:
        entity_name: The entity name (e.g., "sophia", "roc_racoon")
    """
    store = get_memory_store()
    sessions = await store.list_sessions(entity_name)
    
    return json.dumps({
        "entity": entity_name,
        "sessions": sessions,
        "total": len(sessions),
    }, indent=2)
```

### Effort
- ~80 lines added to server.py
- **Total: ~80 lines, 30 minutes**

---

## §3 Change 3: Strip Esoteric Terminology

### What We're Changing
All documentation and code comments that reference mythological/esoteric names get replaced with clean, engineering-first terminology.

### Naming Mapping

| Esoteric Name | Clean Name | Where Used |
|---------------|------------|------------|
| Lilith Mnemosyne | Memory System | Legacy analysis docs |
| Mnemosyne Writer | Batch Writer | Legacy analysis docs |
| Memory Bank MCP | Memory Store Legacy | Legacy analysis docs |
| Kether, Chokmah... | (removed) | 13-sphere archive |
| Lilith (entity) | (keep — it's a user-defined entity) | entities.yaml |
| Mnemosyne (entity) | (keep — it's a user-defined entity) | entities.yaml |
| Soul (concept) | State / Knowledge Base | soul.yaml references |
| Gnosis | Knowledge / Insights | soul.yaml lessons |
| Oracle (entity) | (keep — it's the routing engine) | oracle.py |

### Files to Update

| File | Change |
|------|--------|
| `docs/legacy/LEGACY_MASTER_SYNTHESIS.md` | Replace "Mnemosyne" → "Memory System", "Lilith Mnemosyne" → "Tiered Memory Adapters" |
| `docs/legacy/LEGACY_ASSET_CATALOG.md` | Same replacements |
| `docs/legacy/LEGACY_INDEX.md` | Same replacements |
| `MNEMOSYNE_TREASURE_MAP_20260608.md` | Rename to `MEMORY_TREASURE_MAP_20260608.md`, replace all esoteric refs |
| `DEEPSEEK_HARDENING_PASS_v2_20260608.md` | Replace "Mnemosyne" → "Memory System" in all findings |
| `docs/strategy/MASTER_SYNTHESIS_AND_ROADMAP.md` | Replace "Mnemosyne" → "Memory System" in §15 |
| `SOVEREIGN_MANDATES.md` | No changes needed (already clean) |
| `AGENTS.md` | No changes needed (already clean) |

### Effort
- Search-and-replace across ~10 files
- **Total: 30 minutes**

---

## §4 What We're NOT Doing (MiMo Deletes)

The MiMo lens says: **if it's not broken, don't fix it.** These legacy patterns are NOT being ported:

| Legacy Pattern | Why NOT Porting |
|----------------|-----------------|
| **FallbackCircuitBreaker** | Our `AsyncCircuitBreaker` already has `anyio.Lock()`, proper state machine, ZONEID markers. It's BETTER. |
| **MemoryBankFallbackWrapper** | The proxy pattern is unnecessary. Our circuit breaker already handles fallback at the provider level. |
| **Redis DLQ** | Our `FileStorageProvider` uses atomic writes (`.tmp` + `os.replace()`) + `fcntl.flock()`. No need for Redis. |
| **Qdrant adapter** | Already exists in `vector_adapters.py` (196 lines). No changes needed. |
| **Bloom filter router** | Over-engineered. The hot cache + provider chain is sufficient for 3 tiers on a laptop. |
| **MoE routing gate** | Over-engineered. Simple dict lookup is O(1) and fast enough. |
| **Promotion gate** | Over-engineered. The existing `archive_old_sessions()` handles hot→cold. Warm→cold is handled by `FileStorageProvider.archive()`. |
| **3-adapter Lilith architecture** | Our provider chain (Redis → File → InMemory) already implements the same pattern with less code. |
| **MnemosyneWriter batching** | Our `MemoryStore.add_exchange()` writes directly to providers. No batching needed — the writes are fast (dict + JSON file). |

**Total lines NOT written: ~1,500**

---

## §5 Summary: The MiMo Integration

### What's Being Added

| Change | Lines | Effort | Impact |
|--------|-------|--------|--------|
| FTS5 search index (with archive cleanup) | ~180 | 1.5 hours | 🔴 HIGH — agents can search memory |
| MemoryStore integration (try/except, archive) | ~30 | 30 min | 🔴 HIGH — FTS index lifecycle |
| MCP memory tools (sovereign isolated) | ~80 | 30 min | 🔴 HIGH — memory exposed to fleet |
| Tests (FTS + MCP + isolation) | ~80 | 1 hour | 🔴 HIGH — must verify corrections |
| Naming cleanup | ~0 code | 30 min | 🟡 MED — removes confusion |
| **Total** | **~370 lines** | **~4 hours** | **3 CRITICAL fixes applied** |

### What's NOT Being Added

| Pattern | Lines Saved | Why |
|---------|-------------|-----|
| FallbackCircuitBreaker | ~300 | Already have hardened AsyncCircuitBreaker |
| MemoryBankFallbackWrapper | ~200 | Unnecessary abstraction |
| Redis DLQ | ~150 | Atomic writes are sufficient |
| Bloom filter router | ~200 | Over-engineered for laptop |
| MoE routing gate | ~150 | Dict lookup is O(1) |
| Promotion gate | ~100 | archive_old_sessions() exists |
| **Total saved** | **~1,100 lines** | **MiMo principle: delete before you add** |

### Architecture After Integration (With DeepSeek Corrections)

```
MemoryStore (src/omega/memory_store.py)
├── Hot Tier (dict + Redis)
│   ├── LRU cache (50 entries max)
│   ├── Tombstone deletion (0.5s grace)
│   └── Auto-eviction via TTL
├── Warm Tier (JSON files + FTS5 index) ← NEW
│   ├── FileStorageProvider (atomic writes)
│   ├── ConversationFTSIndex (SQLite FTS5) ← NEW
│   │   ├── remove_session() on archive ← C1 FIX
│   │   └── try/except in add_exchange() ← C2 FIX
│   └── fcntl.flock() locking
├── Cold Tier (InMemory fallback)
│   └── Volatile, no persistence
├── Vector Store (Qdrant adapter)
│   └── delete() on archive ← C4 FIX
└── MCP Tools ← NEW
    ├── memory_search(query, entity_name REQUIRED) ← C3 FIX
    ├── memory_get_history(entity_name, session_id, limit)
    └── memory_list_sessions(entity_name)
```

### No External Dependencies Added
- SQLite FTS5 is built into Python's `sqlite3` module
- No new Python packages required
- No new infrastructure services required
- No Redis/Qdrant/PostgreSQL additions

---

## §6 Execution Order

1. **Step 1**: Create `src/omega/memory/fts_index.py` (~180 lines)
   - `initialize()` with FTS5 CREATE VIRTUAL TABLE + availability check
   - `index_exchange()` for dual-write
   - `remove_session()` for archive cleanup (C1 fix)
   - `search()` with mandatory entity_name (C3 fix)
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

*⬡ OMEGA ⬡ ROC_RACOON ⬡ mimo-v2.5-free ⬡ opencode ⬡ MIMO-INTEGRATION ⬡*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
