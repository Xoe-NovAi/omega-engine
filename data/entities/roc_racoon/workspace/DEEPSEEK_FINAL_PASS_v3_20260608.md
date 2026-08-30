# 🔱 DeepSeek Final Pass v3 — Pre-Execution Audit
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash ⬡ opencode ⬡ DEEPSEEK-FINAL ⬡

**Date**: 2026-06-08
**Lens**: DeepSeek V4 Flash (final review — structural audit of MiMo Integration Spec)
**Status**: 4 CRITICAL corrections, 2 HIGH planning additions, 9 INFO observations

---

## §0 The MiMo Spec Was Good. These Are the Missing Edges.

The MiMo Integration Spec correctly identified the 3 real gaps (FTS5, MCP tools, naming cleanup)
and saved ~1,100 lines of unnecessary code. However, DeepSeek's structural audit found:

**4 CRITICAL issues** that must be fixed before any code is written.
**2 HIGH issues** that need execution planning.
**9 INFO observations** — document for future reference.

---

## §1 CRITICAL Corrections (Blocking — Must Fix in Spec)

### C1: FTS Index Orphaned on Session Archive

**Finding**: `MemoryStore.archive_session()` (line 350) does NOT clean the FTS index.
When a session is archived, its FTS entries remain in the `conversation_fts` table forever.
After enough archiving, the FTS index is dominated by dead entries.

**Fix**: Add `remove_session()` method to `ConversationFTSIndex`.

**File**: `src/omega/memory/fts_index.py`
```python
async def remove_session(self, entity_name: str, session_id: str) -> None:
    """Remove all FTS entries for a session. Called by archive_session()."""
    async with self._lock:
        await anyio.to_thread.run_sync(
            self._remove_session_sync, entity_name, session_id
        )

def _remove_session_sync(self, entity_name: str, session_id: str) -> None:
    assert self._conn is not None
    self._conn.execute(
        "DELETE FROM conversation_fts WHERE entity_name = ? AND session_id = ?",
        (entity_name, session_id)
    )
    self._conn.commit()
```

**Integration**: In `MemoryStore.archive_session()`, after providers succeed:
```python
await self._fts_index.remove_session(entity_name, session_id)
```

---

### C2: FTS Write Failure Would Break `add_exchange()`

**Finding**: The spec shows FTS indexing INSIDE `add_exchange()` without error handling:
```python
await self._fts_index.index_exchange(...)  # If this fails, the exchange is lost
```

**Fix**: Wrap in try/except. FTS indexing is secondary — if it fails, the exchange
still saved to providers. Log warning, continue.

```python
# In add_exchange(), after exchange is saved to providers:
try:
    await self._fts_index.index_exchange(
        entity_name=entity_name,
        session_id=session_id,
        role="user",
        content=user_message,
        timestamp=datetime.now(timezone.utc).isoformat()
    )
    await self._fts_index.index_exchange(
        entity_name=entity_name, role="assistant",
        content=response, timestamp=...
    )
except Exception:
    logger.warning("FTS indexing failed for %s/%s", entity_name, session_id, exc_info=True)
```

---

### C3: No Sovereign Isolation on MCP Memory Tools

**Finding**: The proposed `memory_search` tool has `entity_name` as OPTIONAL:
```python
async def memory_search(query: str, entity_name: str = "", limit: int = 20) -> str:
```
This violates sovereign isolation — any agent could search ALL entities' conversations.
The engine's existing sovereign architecture requires entity boundaries.

**Fix**: Make `entity_name` REQUIRED. Cross-entity search is a future feature.

```python
async def memory_search(
    query: str, 
    entity_name: str,  # REQUIRED — sovereign isolation
    limit: int = 20
) -> str:
```

Similarly for `memory_get_history` — entity_name is already required, good.

**Why this matters**: The 10 Pillar Keepers are separate sovereign entities.
Entity A should NOT be able to search Entity B's conversations.
This is the MemoryStore equivalent of `SovereignSearcher`'s entity filter.

---

### C4: Vector Store Orphaned on Session Archive

**Finding**: `MemoryStore.archive_session()` does NOT call `self.vector_store.delete()`.
When a session is archived, its vector embeddings remain in Qdrant indefinitely.
After enough archiving, Qdrant is dominated by dead vectors.

**Fix**: In `MemoryStore.archive_session()`, after providers succeed:
```python
if self.vector_store:
    try:
        await self.vector_store.delete(
            filter_by={"entity_name": entity_name, "session_id": session_id}
        )
    except Exception:
        logger.warning("Vector store cleanup failed for %s/%s", entity_name, session_id)
```

**Note**: Check `QdrantAdapter` for a `delete()` method. From the audit:
`QdrantAdapter` (vector_adapters.py:53-196) has `upsert()`, `query()`,
`get_status()`, and `delete()`. The `delete()` method accepts kwargs including
`entity_name` parameter for sovereign isolation. We need to verify it also
supports `session_id` filtering — if not, this requires a Qdrant `must` filter
with both fields.

---

## §2 HIGH Issues (Must Plan For Execution)

### H1: Tombstone State Lost on Restart

**Issue**: `_tombstoned` dict is purely in-memory (memory_store.py:89).
After a process restart, the tombstone registry is empty. The warm files
are gone (deleted by FileStorageProvider.archive()), so archived sessions
are correctly invisible. However, there is no record that they WERE archived
and no way to restore from cold storage.

**Risk**: LOW for current use case (single user, laptop).
**Plan**: Add tombstone persistence to the FTS index or a separate
tombstone_store table. Not needed for MVP.

**Deferred**: Add to `docs/future/ARCHIVE_RESTORE.md` if archive restore is ever needed.

### H2: No Rate Limiting on MCP Tools

**Issue**: The 47 MCP tools have zero rate limiting. The only protection is
`ResourceGuard` (Semaphore(1)) on model inference. The new `memory_search`
tools access SQLite directly and could be hammered.

**Risk**: LOW for single-user (laptop, Hivemind limits concurrent agents).
**Plan for MVP**: No rate limiting needed. Add if multi-agent concurrency becomes a concern.
**Document**: Note in MCP tool docstrings that heavy usage (>100 calls/turn) may impact performance.

---

## §3 INFO Observations (Document for Future)

| # | Observation | Impact | Why It Matters |
|---|-------------|--------|----------------|
| I1 | `InMemoryStorageProvider` is misnamed "Cold/Volatile" — it's transient, lost on restart | LOW | Confusing for new developers. Rename to `TransientStorageProvider` in next cleanup pass. |
| I2 | `stats()` blind to FTS, vector store, archives | LOW | No observability into secondary storage. Add FTS entry count to stats() in post-MVP. |
| I3 | `archive_old_sessions()` no batch limit | LOW | Can attempt 10K+ files. Add `batch_size=100` default with anyio.Semaphore. |
| I4 | `FileStorageProvider.archive()` leaves orphan .lock files on failure | LOW | Lock removal failure returns True anyway. Minor disk clutter. |
| I5 | `close()` does not close vector_store | LOW | `QdrantAdapter` has no close(). Minor resource leak on shutdown. |
| I6 | `archive_session()` returns True if ANY provider succeeded | INFO | Partial archive success masked. Add per-provider status reporting. |
| I7 | `_reap_tombstoned()` only called from `_cache_hot()` | INFO | If no new sessions, tombstoned entries stay in dict forever. Minor memory leak. |
| I8 | FTS5 is built into SQLite 3.46.1 — no extension needed | INFO | Confirmed available. No fallback needed. |
| I9 | No "mnemosyne"/"memory_bank" references in active config | INFO | Naming: all clean. The session recordings in HALL_OF_RECORDS reference "mnemosyne" as a mining target (legacy), not an active system. |

---

## §4 Updated Architecture

```
MemoryStore (src/omega/memory_store.py)
├── Hot Tier (dict + Redis)
│   ├── LRU cache (50 entries max)
│   ├── Tombstone deletion (0.5s grace)
│   └── Auto-eviction via TTL
├── Warm Tier (JSON files + FTS5 index) ← NEW
│   ├── FileStorageProvider (atomic writes)
│   ├── ConversationFTSIndex (SQLite FTS5) ← NEW
│   ├── remove_session() on archive ← CRITICAL FIX C1
│   ├── try/except in add_exchange() ← CRITICAL FIX C2
│   └── fcntl.flock() locking
├── Cold Tier (InMemory fallback)
│   └── Volatile, no persistence
├── Vector Store (Qdrant adapter)
│   └── delete() on archive ← CRITICAL FIX C4
└── MCP Tools ← NEW
    ├── memory_search(query, entity_name REQUIRED, limit) ← CRITICAL FIX C3
    ├── memory_get_history(entity_name, session_id, limit)
    └── memory_list_sessions(entity_name)
```

---

## §5 Updated Execution Order

1. **Step 1**: Create `src/omega/memory/fts_index.py` with:
   - `initialize()` with FTS5 CREATE VIRTUAL TABLE
   - `index_exchange()` with try/except wrapper in caller
   - `remove_session()` for archive cleanup
   - `search()` with sovereign entity filter
   - `close()` for graceful shutdown

2. **Step 2**: Integrate into `MemoryStore`:
   - `__init__()` — create FTS index
   - `add_exchange()` — wrap FTS write in try/except
   - `archive_session()` — add FTS cleanup + vector store cleanup
   - `close()` — close FTS index
   - `stats()` — add FTS entry count

3. **Step 3**: Add MCP tools to `server.py`:
   - `memory_search(query, entity_name REQUIRED, limit)` — with sovereign isolation
   - `memory_get_history(entity_name, session_id, limit)` — already isolated
   - `memory_list_sessions(entity_name)` — already isolated

4. **Step 4**: Add tests (~80 lines):
   - FTS index: `test_fts_search`, `test_fts_index_exchange`, `test_fts_remove_session`
   - Integration: `test_fts_archive_cleanup`
   - MCP tools: `test_memory_search_isolation` (verify entity_name required)

5. **Step 5**: Run `make test` — all 320+ tests must pass

6. **Step 6**: Strip esoteric naming from documentation

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash ⬡ opencode ⬡ DEEPSEEK-FINAL ⬡*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
