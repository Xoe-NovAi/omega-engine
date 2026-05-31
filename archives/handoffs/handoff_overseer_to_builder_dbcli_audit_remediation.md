# 🔱 Omega Engine — Database & Cross-CLI Audit Remediation Build Brief
# Overseer → Gemma 4 31B (Builder Mode)

**AP Token**: `AP-BUILDER-BRIEF-DBCLI-REMEDIATION-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_builder_handoff ⬡ DBCLI-FIXES
**Recommended Model**: `gemma-4-31b-it` (Google AI Studio — unlimited usage, 262K context)
**Recommended Mode**: `builder` (`.opencode/agents/builder.md`)
**Vision**: NOT required for these tasks (all file-based code changes)

---

## §0 How to Use This Brief

This brief contains the prioritized action plan to remediate **13 bugs** found during the Firsthand Code Audit (2026-05-26). These bugs were discovered by reading every line of critical source files — they exist in code that *appears* to work but produces wrong results or crashes on edge cases.

### Reference Documents

Read these BEFORE starting any task:
- `docs/research/R_DATABASE_AND_CROSS_CLI_FIRSTHAND_FINDINGS.md` — Full audit report with all 13 bugs
- `docs/research/R_DATABASE_AND_CROSS_CLI_HARDENING_REVIEW.md` — Architectural review (earlier)
- `docs/strategy/OVERSEER_DATABASE_STRATEGIC_REVIEW.md` — Strategic timing assessment (earlier)

### Your Operating Rules

1. **READ before EDIT** — Every `edit()` call must be preceded by a `read()` of the target file. Line numbers in this brief are current as of May 26, 2026 — verify them.
2. **`make test` after every task** — Run `make test` after each commit-worthy change. If tests break, fix before moving on.
3. **Commit after every task** — `git add -A && git commit -m "Audit Remediation: <task description>"`. This creates a clean checkpoint trail.
4. **Ask about ANY ambiguity** — If a file path is wrong, a line number shifted, or a fix seems wrong, stop and ask. Do NOT guess.
5. **Tasks within a section can be parallelized** — P0 tasks are independent of each other. P1 tasks are independent of each other. Only P0→P1→P2 dependency is the ordering.
6. **Run `make lint` at the end** — Ensure no whitespace or formatting regressions.

---

## §1 Priority Queue

| Priority | # | Task | Severity | Files | Est. |
|----------|---|------|----------|-------|------|
| **P0** | 1 | Fix hivemind port from 8102 → 8016 | 🔴 CRITICAL | `src/omega/oracle/oracle.py`, `config/omega.yaml` | 5 min |
| **P0** | 2 | Fix hybrid search sort inversion | 🔴 CRITICAL | `src/omega/library/indexer.py` | 10 min |
| **P1** | 3 | Fix HALL_OF_RECORDS path consistency | 🟠 HIGH | `mcp/omega_hub/server.py`, `src/omega/workers/background_researcher/loop.py` | 10 min |
| **P1** | 4 | Add corrupted file handling in MemoryStore | 🟠 HIGH | `src/omega/memory_store.py` | 15 min |
| **P1** | 5 | Close file descriptor in SessionManager lock | 🟠 HIGH | `src/omega/oracle/session_manager.py` | 5 min |
| **P1** | 6 | Make session active file write atomic | 🟠 HIGH | `src/omega/oracle/session_manager.py` | 10 min |
| **P1** | 7 | Fix Indexer.close() never called | 🟠 HIGH | `src/omega/library/indexer.py`, `src/omega/library/library.py` | 10 min |
| **P1** | 8 | Fix stale lock detection time source | 🟡 MEDIUM | `src/omega/oracle/session_manager.py` | 5 min |
| **P2** | 9 | Remove duplicated method definitions in orchestrator | 🟡 MEDIUM | `src/omega/oracle/orchestrator.py` | 5 min |
| **P2** | 10 | Fix title=item.tags type bug | 🟡 LOW | `src/omega/library/library.py` | 5 min |
| **P2** | 11 | Remove dead database dependencies from pyproject.toml | 🟡 LOW | `pyproject.toml` | 5 min |
| **P2** | 12 | Fix Entity wad_source YAML deserialization | 🟡 LOW | `src/omega/oracle/entity_registry.py` | 5 min |
| **Final** | 13 | `make test` + `make lint` + `git commit` | — | — | 10 min |

**Total estimated time**: ~95 minutes (1.5 hours)

---

## §2 P0 Tasks — 🔴 Critical (Fix Immediately)

### TASK 1: Fix Hivemind Port from 8102 → 8016 (5 min)

**Bug C-7**: `_post_to_hivemind()` in `oracle.py` posts to port 8102, but the Hub MCP server runs on port 8016. All cross-CLI awareness from the Oracle is silently lost.

**Verification**: `ss -tlnp | grep 8016` shows the Hub running. `ss -tlnp | grep 8102` shows nothing.

#### File 1: `src/omega/oracle/oracle.py`
**Line**: ~216 (search for `8102`)
**Current code**:
```python
url = f"{hivemind_cfg.get('url', 'http://127.0.0.1:8102')}/tools/post_context"
```
**Fix**: Change `8102` to `8016` in the default URL:
```python
url = f"{hivemind_cfg.get('url', 'http://127.0.0.1:8016')}/tools/post_context"
```
**Also**: The payload construction sends `decisions: []` and `focus_chain: []` (lines 220-223). While this isn't a blocker, consider whether to populate these with real data. For now, just fix the port.

#### File 2: `config/omega.yaml`
**Line**: ~25 (search for `8102`)
**Current code**:
```yaml
hivemind:
  url: "http://127.0.0.1:8102"
```
**Fix**:
```yaml
hivemind:
  url: "http://127.0.0.1:8016"
```

**Verification**:
- After fix, `grep -rn "8102" src/omega/ config/` should return **zero matches** in active code paths (comments referencing historical port 8102 are acceptable).
- Run `make test` — all 259 tests must pass.

---

### TASK 2: Fix Hybrid Search Sort Inversion (10 min)

**Bug C-13**: `hybrid_search()` sort key in `indexer.py:269-272` is mathematically inverted. The negation of FTS5's already-negative BM25 rank combined with `reverse=True` produces `vec_score*10 - fts_score` descending, which **penalizes good FTS matches** instead of boosting them.

**File**: `src/omega/library/indexer.py`
**Lines**: ~269-272

**Current code**:
```python
        combined.sort(
            key=lambda r: -r.get("_fts_score", 0) + r.get("_vec_score", 0) * 10,
            reverse=True,
        )
```

**Bug analysis**:
- FTS5 BM25 ranks are negative (closer to 0 = better match)
- `-r.get("_fts_score", 0)` negates the negative, making worse FTS matches produce HIGHER positive values
- `reverse=True` sorts descending, so worse FTS matches rank higher
- Vector score is multiplied by 10, then added — so vector-dominant results always push FTS-good results down

**Fix**: Replace with Reciprocal Rank Fusion (RRF), the standard approach for hybrid search:

```python
        def _rrf_score(item, k=60):
            """Reciprocal Rank Fusion score — higher is better.
            
            Converts FTS5 rank (negative BM25, closer to 0 = better) and
            vector score (0 to 1, higher = better) into combined RRF score.
            k=60 is the standard RRF parameter.
            """
            # FTS5 rank: negate to make positive (higher rank value = worse match)
            # Convert to RRF: 1 / (k + rank_position)
            fts_raw = -item.get("_fts_score", 0)  # negate to make positive
            if fts_raw < 0:
                fts_raw = 0  # shouldn't happen, but guard
            fts_rrf = 1.0 / (k + fts_raw)
            
            # Vector score: already positive 0-1, invert so 1.0 = rank 0
            vec_raw = 1.0 - item.get("_vec_score", 0.0)
            vec_rrf = 1.0 / (k + vec_raw * 100)
            
            return fts_rrf + vec_rrf

        combined.sort(
            key=_rrf_score,
            reverse=True,
        )
```

**Verification**:
- Read the file to confirm the exact current code (line numbers may have shifted)
- After fix, `make test` must pass all 259 tests
- The `test_bug_001_fix.py` test (the only test touching indexer) must still pass

---

## §3 P1 Tasks — 🟠 High (Fix Before Release)

### TASK 3: Fix HALL_OF_RECORDS Path Consistency (10 min)

**Bug C-10**: The Hub MCP writes awareness data to `knowledge/HALL_OF_RECORDS/` (line 76), while the background researcher writes to `data/knowledge/HALL_OF_RECORDS/` (line 427 in loop.py). These are **different physical directories**. Data stored by one system is invisible to the other.

**Fix**: Both must use the same canonical path. The standard across the project is `data/knowledge/HALL_OF_RECORDS/` (consistent with `data/memory/`, `data/sessions/`, `data/library/`).

#### File 1: `mcp/omega_hub/server.py`
**Line**: ~76
**Current code**:
```python
HALL_OF_RECORDS = PROJECT_ROOT / "knowledge" / "HALL_OF_RECORDS"
```
**Fix**:
```python
HALL_OF_RECORDS = PROJECT_ROOT / "data" / "knowledge" / "HALL_OF_RECORDS"
```

#### File 2: `src/omega/workers/background_researcher/loop.py`
**Line**: ~427 (search for `HALL_OF_RECORDS`)
**Current code** (likely):
```python
base_dir = Path(__file__).resolve().parent.parent.parent.parent
records_dir = base_dir / "data" / "knowledge" / "HALL_OF_RECORDS" / "background-researcher"
```
**This path may already be correct** — verify by reading the file. The researcher writes to the `data/knowledge/` variant, so it may already be right. Only `server.py` needs fixing if loop.py uses the correct path.

**Also**: After fixing the Hub path, move any existing files from `knowledge/HALL_OF_RECORDS/` to `data/knowledge/HALL_OF_RECORDS/`:
```bash
mkdir -p data/knowledge/HALL_OF_RECORDS
cp -r knowledge/HALL_OF_RECORDS/* data/knowledge/HALL_OF_RECORDS/ 2>/dev/null || true
```

**Verification**:
- `grep -rn "knowledge.*HALL_OF_RECORDS" src/omega/ mcp/` should show a single consistent path
- `make test` — all tests pass

---

### TASK 4: Add Corrupted File Handling in MemoryStore (15 min)

**Bug C-MEM-002**: Every `json.loads()` call in `memory_store.py` lacks `try/except`. A single corrupted memory file (truncated write, disk error, manual edit) will crash the engine with an unhandled `json.JSONDecodeError`.

**File**: `src/omega/memory_store.py`
**Affected call sites** (read the file to verify exact lines):

#### Site 1: Warm read (~line 119-120)
**Current code** (approximate):
```python
        async with await anyio.open_file(str(warm_path)) as f:
            data = json.loads(await f.read())
        exchanges = data.get("exchanges", [])
```
**Fix**:
```python
        async with await anyio.open_file(str(warm_path)) as f:
            raw = await f.read()
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            logger.warning(f"Corrupted warm memory file: {warm_path}. Starting fresh.")
            data = {}
        exchanges = data.get("exchanges", [])
```

#### Site 2: Cold read (~line 128-130)
**Current code** (approximate):
```python
        async with await anyio.open_file(str(cold_path), "rb") as f:
            data = json.loads(gzip.decompress(await f.read()))
        exchanges = data.get("exchanges", [])
```
**Fix**:
```python
        async with await anyio.open_file(str(cold_path), "rb") as f:
            raw = gzip.decompress(await f.read())
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            logger.warning(f"Corrupted cold memory file: {cold_path}. Starting fresh.")
            data = {}
        exchanges = data.get("exchanges", [])
```

#### Site 3: Archive read (~line 240-241)
**Current code** (approximate):
```python
        async with await anyio.open_file(str(warm_path)) as f:
            data = json.loads(await f.read())
```
**Fix**:
```python
        async with await anyio.open_file(str(warm_path)) as f:
            raw = await f.read()
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            logger.warning(f"Corrupted archive source file: {warm_path}. Cannot archive.")
            return False
```

**Verification**:
- After fix, `make test` passes all 259 tests
- The test suite includes `test_memory_store.py` (12 tests) — verify they all pass

---

### TASK 5: Close File Descriptor in SessionManager Lock (5 min)

**Bug C-MEM-003**: `os.open()` in `session_manager.py` returns a file descriptor that is **never stored or closed**. Every `get_session_id()` call leaks an FD.

**File**: `src/omega/oracle/session_manager.py`
**Line**: ~50

**Current code**:
```python
def _create_lock():
    try:
        os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        return True
    except FileExistsError:
        ...
```

**Fix option A** (store and close the FD):
```python
def _create_lock():
    try:
        fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
        return True
    except FileExistsError:
        ...
```

**Fix option B** (use `Path.touch()` instead — cleaner, no FD):
```python
def _create_lock():
    try:
        lock_file.touch(exist_ok=False)
        return True
    except FileExistsError:
        ...
```

**Recommendation**: Option B is cleaner. `Path.touch(exist_ok=False)` creates the file atomically and raises `FileExistsError` if it already exists. No file descriptor is involved.

BUT — there's a subtlety. `Path.touch()` is not atomic in the same sense as `os.open(O_CREAT | O_EXCL)` — it's a TOCTOU race. `os.open(O_CREAT | O_EXCL)` is the correct atomic primitive. So Option A is the safer choice for correctness, even though Option B is cleaner.

**Stick with Option A** (close the FD explicitly):

```python
def _create_lock():
    try:
        fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
        return True
    except FileExistsError:
        ...
```

**Verification**:
- After fix, `make test` passes
- `test_session_manager.py` (14 tests) covers lock behavior

---

### TASK 6: Make Session Active File Write Atomic (10 min)

**Bug C-MEM-005**: The session active file is written with `anyio.open_file(..., "w")` — a truncating write. Crash between `open` and `write` = empty active file. SessionManager catches this, but it loses the counter.

**File**: `src/omega/oracle/session_manager.py`
**Lines**: ~83-90

**Current code**:
```python
        async with await anyio.open_file(str(active_file), "w") as f:
            await f.write(json.dumps({
                "date": today,
                "counter": counter,
                "session_id": session_id,
                "entity": entity_name,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }, indent=2))
```

**Fix**: Use the `_atomic_write` pattern established in `memory_store.py` — write to temp, then rename:

```python
        # Atomic write: temp file + os.replace to prevent crash corruption
        temp_file = active_file.with_suffix(f".{os.getpid()}.tmp")
        async with await anyio.open_file(str(temp_file), "w") as f:
            await f.write(json.dumps({
                "date": today,
                "counter": counter,
                "session_id": session_id,
                "entity": entity_name,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }, indent=2))
        await anyio.to_thread.run_sync(os.replace, str(temp_file), str(active_file))
```

**Also**: Add `import os` at the top if not already present (it IS present — line 11 has `import os`).

**Verification**:
- After fix, `make test` passes (14 session_manager tests)
- The atomic write guarantees the active file is never partially written

---

### TASK 7: Fix Indexer.close() Never Called (10 min)

**Bug C-15**: `Indexer.close()` exists at `indexer.py:288-293` but is **never called** by any code. The FTS5 aiosqlite connection is never explicitly closed.

**File 1**: `src/omega/library/indexer.py`
**Lines**: ~288-293
**Current code (already exists, just never called)**:
```python
    async def close(self) -> None:
        """Close the SQLite connection."""
        if self._fts:
            await self._fts.close()
            self._fts = None
            logger.info("FTS index connection closed")
```
**No change needed here** — the `close()` method is correctly implemented. The bug is that it's never invoked.

**File 2**: `src/omega/library/library.py`
**The fix**: Add a `close()` method to `Library` that delegates to `Indexer.close()`, and ensure it's called on shutdown.

**Read `library.py`** first to understand the class structure. Then add:

```python
    async def close(self) -> None:
        """Close the search index and flush any pending data."""
        await self._indexer.close()
```

**Then**: Wire this into the Hub MCP server's shutdown lifecycle. Read `mcp/omega_hub/server.py` — look for how the Library is instantiated and if there's any cleanup path. The simplest fix is to call `library.close()` at the end of the Hub's main block or via an `atexit` handler.

Since the Hub runs as a long-lived server, the connection leak is low-impact in practice (the FTS DB is closed when the process exits). The primary fix is making `Library.close()` exist and be callable. If there's no shutdown hook, add:

In `mcp/omega_hub/server.py`, at the end of `if __name__ == "__main__":` block (around line 812-813):

```python
    try:
        run_mcp(mcp, modify_app=_add_hub_endpoints)
    finally:
        # Ensure index connections are closed on shutdown
        import anyio
        anyio.run(library.close)
```

**But**: `anyio.run()` inside a `finally` block may cause issues with the event loop lifecycle. A cleaner approach:

```python
    # Register cleanup
    import atexit
    atexit.register(lambda: anyio.run(library.close) if 'library' in dir() else None)
```

Actually, the cleanest approach depends on how `run_mcp` works. If it blocks until shutdown, we can use a try/finally:

In `server.py`, modify the `__main__` block:
```python
if __name__ == "__main__":
    try:
        run_mcp(mcp, modify_app=_add_hub_endpoints)
    finally:
        # Close library connections
        import anyio
        try:
            anyio.run(library.close)
        except Exception:
            pass
```

**Verification**:
- After fix, `make test` passes
- The `Indexer` connection is now properly closable

---

### TASK 8: Fix Stale Lock Detection Time Source (5 min)

**Bug C-MEM-004**: `session_manager.py:55` mixes `time.monotonic()` (boot-relative clock) with `st_mtime` (epoch-based wall clock). The expression `time.monotonic() - st_mtime` is **always negative** on a running system, making the `age > 30` stale lock check **never trigger**.

**File**: `src/omega/oracle/session_manager.py`
**Lines**: ~54-56

**Current code**:
```python
                    try:
                        age = time.monotonic() - lock_file.stat().st_mtime
                        if age > 30:
```

**Fix**: Use `time.time()` (epoch-based wall clock, matching `st_mtime`):

```python
                    try:
                        age = time.time() - lock_file.stat().st_mtime
                        if age > 30:
```

**Also**: Add `import time` at the top if not already present (it IS present — line 11 has `import time`).

**Verification**:
- After fix, `make test` passes
- The stale lock detection now correctly compares wall-clock times

---

## §4 P2 Tasks — 🟡 Medium/Low (Fix After P0+P1)

### TASK 9: Remove Duplicated Method Definitions in Orchestrator (5 min)

**Bug**: `trigger_model_update()` and `get_model_updater_status()` are each defined **twice** in `orchestrator.py`. The second definition shadows the first.

**File**: `src/omega/oracle/orchestrator.py`
**Lines**: ~250-264 (first definition) and ~276-290 (second definition — identical)

**Fix**: Remove the first pair of definitions (lines ~250-264). Keep only the second pair (~276-290) since Python uses the last definition.

```python
# Lines ~250-264: DELETE these lines entirely
# Lines ~276-290: KEEP these (they are the effective definition)
```

**Steps**:
1. Read `orchestrator.py` around lines 240-300 to verify the actual code
2. Delete the first occurrence of `trigger_model_update()` and `get_model_updater_status()` (lines 250-264 approximately)
3. Verify the second occurrence at lines 276-290 remains

**Verification**:
- `grep -c "async def trigger_model_update" src/omega/oracle/orchestrator.py` should return `1`
- `grep -c "async def get_model_updater_status" src/omega/oracle/orchestrator.py` should return `1`
- `make test` passes

---

### TASK 10: Fix title=item.tags Type Bug (5 min)

**Bug C-17**: `library.py:177` passes `title=item.tags` instead of `title=item.title` to `curation_pipeline.process()`. `item.tags` is a `List[str]`, producing `"['tag1', 'tag2']"` as the document title.

**File**: `src/omega/library/library.py`
**Line**: ~177

**Current code**:
```python
        doc = await curation_pipeline.process(
            source=item.source,
            source_type=item.source_type,
            title=item.tags,  # ← BUG: should be item.title
            ...
```

**Fix**:
```python
            title=item.title,
```

**Verification**:
- `make test` passes
- No regression in document ingestion

---

### TASK 11: Remove Dead Database Dependencies from pyproject.toml (5 min)

**Bug**: 5 database dependencies are declared in `pyproject.toml` but never imported in any source code.

**File**: `pyproject.toml`
**Dependencies to remove**:
- `asyncpg==0.31.0` — Zero imports, not installed, not needed (entities are YAML-only)
- `sqlalchemy[asyncio]==2.0.49` — Zero imports, no use case

**Dependencies to KEEP** (needed for future wiring):
- `redis>=7.0.0,<8.0.0` — Planned for v0.6.0 wiring
- `qdrant-client==1.17.1` — Planned for v0.6.0 wiring
- `fastembed==0.6.0` — Planned for v0.6.0 wiring

**Also**: Fix the `aiosqlite` version mismatch — `pyproject.toml` pins `==0.20.0` but the installed version is `0.22.1`. Update to match:
```
aiosqlite==0.22.1
```

**Verification**:
- `grep -rn "import asyncpg\|from asyncpg" src/omega/ mcp/` — should be zero (confirming the dep was never needed)
- `grep -rn "import sqlalchemy\|from sqlalchemy" src/omega/ mcp/` — should be zero
- `pip install -e .` works without errors
- `make test` passes

---

### TASK 12: Fix Entity wad_source YAML Deserialization (5 min)

**Bug**: `Entity` constructed from `config/entities.yaml` never receives `wad_source` — the constructor at `entity_registry.py:99-118` doesn't read it from `raw`.

**File**: `src/omega/oracle/entity_registry.py`
**Lines**: ~99-118 (the Entity constructor call inside `_load()`)

**Current code** (approximate — read the file to verify):
```python
                    self._entities[name] = Entity(
                        name=raw.get("name", name),
                        ...
                        # wad_source is NOT passed
                    )
```

**Fix**: Add `wad_source=raw.get("wad_source")` to the Entity constructor call:

```python
                    self._entities[name] = Entity(
                        name=raw.get("name", name),
                        ...
                        wad_source=raw.get("wad_source"),  # ← ADD THIS
                    )
```

**Verification**:
- `make test` passes (7 entity_registry tests)
- `test_entity_registry.py` should cover `wad_source` — verify existing tests still pass

---

## §5 File-by-File Summary

| # | File | Change | P-Level | Lines Changed |
|---|------|--------|---------|-------------|
| 1 | `src/omega/oracle/oracle.py:216` | Fix hivemind port 8102→8016 | P0 | 1 |
| 1 | `config/omega.yaml:25` | Fix hivemind URL port | P0 | 1 |
| 2 | `src/omega/library/indexer.py:269-272` | Replace inverted sort with RRF | P0 | ~12 |
| 3 | `mcp/omega_hub/server.py:76` | Fix HALL_OF_RECORDS path | P1 | 1 |
| 3 | `src/omega/workers/background_researcher/loop.py:427` | Verify path (likely correct) | P1 | 0-1 |
| 4 | `src/omega/memory_store.py:119,129,240` | Add try/except to 3 json.loads() | P1 | ~18 |
| 5 | `src/omega/oracle/session_manager.py:50` | Close leaked FD | P1 | 2 |
| 6 | `src/omega/oracle/session_manager.py:83-90` | Atomic write for active file | P1 | ~8 |
| 7 | `src/omega/library/library.py` | Add close() method | P1 | 4 |
| 7 | `mcp/omega_hub/server.py` | Wire library.close() on shutdown | P1 | ~6 |
| 8 | `src/omega/oracle/session_manager.py:55` | Fix monotonic→time.time() | P1 | 1 |
| 9 | `src/omega/oracle/orchestrator.py:250-264` | Remove duplicated methods | P2 | ~14 |
| 10 | `src/omega/library/library.py:177` | Fix title=item.tags | P2 | 1 |
| 11 | `pyproject.toml` | Remove asyncpg+sqlalchemy, fix aiosqlite version | P2 | 3 |
| 12 | `src/omega/oracle/entity_registry.py` | Add wad_source to Entity constructor | P2 | 1 |

**Total files modified**: ~10 (some files appear in multiple tasks)
**Total lines changed**: ~75 (excluding deletions of duplicated code)

---

## §6 Verification Gate

After ALL tasks are complete, run this verification sequence:

```bash
# 1. Confirm no stale 8102 references
echo "=== Port 8102 references (should be 0) ==="
grep -rn "8102" src/omega/ config/omega.yaml mcp/ --include="*.py" --include="*.yaml" --include="*.yml" || echo "CLEAN"

# 2. Confirm single HALL_OF_RECORDS path
echo "=== HALL_OF_RECORDS paths ==="
grep -rn "HALL_OF_RECORDS" src/omega/ mcp/ --include="*.py" || echo "CHECK"

# 3. Confirm no duplicate method definitions
echo "=== Duplicate method count ==="
grep -c "async def trigger_model_update" src/omega/oracle/orchestrator.py
grep -c "async def get_model_updater_status" src/omega/oracle/orchestrator.py

# 4. Confirm no leaked asyncpg/sqlalchemy
echo "=== Dead dependency check ==="
grep -rn "import asyncpg\|from asyncpg\|import sqlalchemy\|from sqlalchemy" src/omega/ mcp/ --include="*.py" || echo "CLEAN: No dead imports"

# 5. Confirm entity wad_source handling
echo "=== wad_source in Entity constructor ==="
grep -n "wad_source" src/omega/oracle/entity_registry.py

# 6. Run tests
echo "=== Test suite ==="
make test

# 7. Lint
echo "=== Lint ==="
make lint
```

---

## §7 Commit Sequence

```bash
# After P0 Tasks 1-2
git add -A && git commit -m "Audit Remediation: Fix hivemind port (8102→8016) and hybrid search sort inversion"

# After P1 Tasks 3-8
git add -A && git commit -m "Audit Remediation: Fix HALL_OF_RECORDS path, MemoryStore error handling, SessionManager FD leak, atomic session writes, Indexer cleanup, stale lock detection"

# After P2 Tasks 9-12
git add -A && git commit -m "Audit Remediation: Remove duplicated methods, fix title type bug, clean dead deps, fix wad_source deserialization"

# After Final Task 13
git add -A && git commit -m "Audit Remediation: Final verification — all tests pass"
```

---

*Nineteen eyes read the code. Thirteen bugs surfaced. Seven files, seventy-five lines, one release saved.*
