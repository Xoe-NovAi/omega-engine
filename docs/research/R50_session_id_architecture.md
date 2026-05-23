# 🔱 Session ID Architecture — ContextBuilder Integration Design
# ⬡ OMEGA ⬡ SOPHIA ⬡ qwen3.6-plus-free ⬡ opencode ⬡ trc_design ⬡ SESSION-ARCH

**AP Token**: `AP-SESSION-DESIGN-v1.0.0`
**Date**: 2026-05-16
**Status**: Design — Ready for Implementation Review

---

## §1 Current State Analysis

### What Exists

| Component | ID Concept | Scope | Persistence |
|-----------|-----------|-------|-------------|
| `TraceSession` (observability.py:218) | `trace_id` = `trc_{uuid[:12]}` | Per-request | JSONL events, trace files |
| `ObservabilityEngine` (observability.py:60) | `_session_id` = `uuid[:8]` | Process-lifetime | In-memory only |
| `MemoryStore` (memory_store.py:46) | `session_id` parameter | Per-file | `data/memory/entities/{entity}/{session_id}.json` |
| `ContextBuilder` (context_builder.py:30) | `session_id` parameter | Per-build | Reads from MemoryStore |
| Hivemind MCP | `ses_{uuid[:12]}` | Per-post | `HALL_OF_RECORDS/<cli>/<session_id>.json` |
| CLI (`oracle_cli.py`) | **None** | N/A | Each `omega talk` = new Oracle = new trace |

### The Gap

`oracle.py` **never passes a `session_id`** to `ContextBuilder` or `MemoryStore`. Every request:
1. Creates a new `TraceSession` with a unique `trace_id`
2. Routes to an entity
3. Calls `model_gateway.generate()` with **no conversation history**
4. Returns response
5. `_track_soul_evolution()` updates soul.yaml — but **no `add_exchange()` is called**

Result: **Every request is stateless.** ContextBuilder exists but is never wired. MemoryStore exists but never receives exchanges.

---

## §2 Design Options Evaluated

### Option A: trace_id as session_id

```python
# Every request uses its trace_id as the session_id
session_id = trace.trace_id  # "trc_a1b2c3d4e5f6"
```

**Pros**: Zero new code, backward compatible
**Cons**: **No multi-turn continuity** — every request creates a new memory file. This defeats the entire purpose of ContextBuilder. MemoryStore would have one exchange per file forever.
**Verdict**: ❌ **Rejected** — makes ContextBuilder useless

### Option B: Persistent session IDs with full session management

```python
# Full session lifecycle: create, list, switch, expire, archive
session = SessionManager.create(entity="SOPHIA", user="arch")
session_id = session.id  # "ses_20260516_sophia_a1b2c3"
```

**Pros**: Full multi-turn continuity, session listing, expiry, archival
**Cons**: Requires a new `SessionManager` class, CLI commands (`/session new`, `/session list`, `/session switch`), expiry logic, database or file index
**Verdict**: ⚠️ **Deferred to Phase 1** — too heavy for Phase 0

### Option C: Hybrid — entity-scoped rolling session with trace fallback

```python
# One active session per entity per process lifetime
# Falls back to trace_id when no session exists
session_id = session_manager.get_or_create(entity_name) or trace.trace_id
```

**Pros**: Minimal code, enables ContextBuilder immediately, backward compatible
**Cons**: Session only lasts for process lifetime (CLI invocation or server uptime)
**Verdict**: ✅ **Recommended for Phase 0**

---

## §3 Recommended Approach: Entity-Scoped Rolling Sessions (Phase 0 Minimal)

### Core Concept

**One session_id per entity, persisted on disk, reused across CLI invocations.**

When the user talks to SOPHIA, they always continue the same SOPHIA session until they explicitly start a new one. The session_id is stored in a simple file: `data/sessions/{entity_name.lower()}.active`.

This requires **no new CLI commands**, **no session management UI**, and **no database**. It's a single file read/write per entity.

### Why This Works for Phase 0

1. **CLI use case**: User runs `omega talk "hello"` then `omega talk "what did I just say?"` — both go to the same SOPHIA session, ContextBuilder finds the previous exchange
2. **Server use case** (future): When oracle runs as a long-lived process, the session persists in memory
3. **Headless agents**: Orchestrator creates a session per dispatch with entity name
4. **Backward compatible**: If the active session file doesn't exist, falls back to trace_id

---

## §4 Session ID Format Specification

### Format

```
ses_{YYYYMMDD}_{entity_slug}_{counter}
```

| Component | Example | Source |
|-----------|---------|--------|
| Prefix | `ses_` | Constant |
| Date | `20260516` | UTC date of session creation |
| Entity slug | `sophia` | `entity_name.lower().replace(" ", "_")` |
| Counter | `001` | Auto-incremented per entity per day |

### Examples

```
ses_20260516_sophia_001    # First SOPHIA session on May 16
ses_20260516_sekhmet_003   # Third SEKHMET session on May 16
ses_20260517_sophia_001    # New day → counter resets
```

### Why This Format

- **Human-readable**: You can tell the entity, date, and sequence at a glance
- **Sortable**: Lexicographic sort = chronological order
- **Entity-scoped**: Each entity has independent sessions
- **Daily rotation**: Counter resets daily, preventing unbounded growth
- **No UUID dependency**: Deterministic, reproducible, debuggable

---

## §5 Session Lifecycle State Machine

### States

```
[CREATED] ──→ [ACTIVE] ──→ [ROLLOVER] ──→ [ARCHIVED]
     ↑            │                          │
     └────────────┘                          │
                  └──────────────────────────┘
```

| State | Trigger | Action |
|-------|---------|--------|
| **CREATED** | First query to entity | Write active session file, create MemoryStore entry |
| **ACTIVE** | Subsequent queries | Read active session file, append to MemoryStore |
| **ROLLOVER** | New day detected OR explicit `/session new` | Archive current, create new session with incremented counter |
| **ARCHIVED** | MemoryStore `archive_old_sessions()` cron | Move warm → cold storage |

### Phase 0 Simplification

For Phase 0, we only implement **CREATED → ACTIVE**. Rollover and archival are handled by existing MemoryStore methods (`archive_old_sessions()`). The rollover logic is:

```python
# On each query, check if the active session is from today
active_session = _read_active_session(entity_name)
if active_session and not _is_today(active_session):
    _rollover_session(entity_name)  # Increment counter, write new active
```

---

## §6 Code Changes — Phase 0 Minimal

### 6.1 New File: `src/omega/oracle/session_manager.py`

```python
"""Session Manager — Entity-scoped rolling sessions for Phase 0."""

import anyio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"
SESSION_DIR = DATA_DIR / "sessions"

class SessionManager:
    """Manages one active session per entity."""

    def __init__(self, session_dir: Optional[Path] = None):
        self._session_dir = session_dir or SESSION_DIR
        self._session_dir.mkdir(parents=True, exist_ok=True)
        self._active: dict[str, str] = {}  # in-memory cache

    def _session_file(self, entity_name: str) -> Path:
        return self._session_dir / f"{entity_name.lower()}.active"

    def _counter_file(self, entity_name: str) -> Path:
        return self._session_dir / f"{entity_name.lower()}.counter"

    async def get_session_id(self, entity_name: str) -> str:
        """Get or create the active session ID for an entity."""
        # Check in-memory cache first
        if entity_name in self._active:
            sid = self._active[entity_name]
            if self._is_current_session(sid, entity_name):
                return sid

        # Read from disk
        session_file = self._session_file(entity_name)
        if session_file.exists():
            async with await anyio.open_file(session_file) as f:
                data = json.loads(await f.read())
            sid = data.get("session_id", "")
            if self._is_current_session(sid, entity_name):
                self._active[entity_name] = sid
                return sid

        # Create new session
        return await self._create_session(entity_name)

    async def new_session(self, entity_name: str) -> str:
        """Force create a new session (for /session new command)."""
        return await self._create_session(entity_name)

    async def _create_session(self, entity_name: str) -> str:
        """Create a new session with daily counter."""
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        counter = await self._get_and_increment_counter(entity_name)
        slug = entity_name.lower().replace(" ", "_")
        session_id = f"ses_{today}_{slug}_{counter:03d}"

        data = {
            "session_id": session_id,
            "entity": entity_name,
            "created": datetime.now(timezone.utc).isoformat(),
            "date": today,
        }

        session_file = self._session_file(entity_name)
        async with await anyio.open_file(session_file, "w") as f:
            await f.write(json.dumps(data, indent=2))

        self._active[entity_name] = session_id
        return session_id

    async def _get_and_increment_counter(self, entity_name: str) -> int:
        """Get current counter and increment it."""
        counter_file = self._counter_file(entity_name)
        counter = 1
        if counter_file.exists():
            async with await anyio.open_file(counter_file) as f:
                data = json.loads(await f.read())
            last_date = data.get("date", "")
            today = datetime.now(timezone.utc).strftime("%Y%m%d")
            if last_date == today:
                counter = data.get("counter", 0) + 1
            # else: new day, reset to 1

        async with await anyio.open_file(counter_file, "w") as f:
            await f.write(json.dumps({
                "date": datetime.now(timezone.utc).strftime("%Y%m%d"),
                "counter": counter,
            }))
        return counter

    def _is_current_session(self, session_id: str, entity_name: str) -> bool:
        """Check if a session ID belongs to today."""
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        return f"ses_{today}_" in session_id

    async def list_sessions(self, entity_name: Optional[str] = None) -> list[dict]:
        """List active sessions."""
        sessions = []
        pattern = "*.active"
        for path in sorted(self._session_dir.glob(pattern)):
            if entity_name and entity_name.lower() not in path.stem:
                continue
            async with await anyio.open_file(path) as f:
                data = json.loads(await f.read())
            sessions.append(data)
        return sessions
```

### 6.2 Modified: `src/omega/oracle/oracle.py`

**Changes needed**:

1. Import `SessionManager`
2. Initialize in `__init__`
3. In `talk()` and `summon()`, get session_id before calling `_summon`/`_respond_as_iris`
4. Wire `ContextBuilder.build_context()` into the system prompt
5. Call `MemoryStore.add_exchange()` after each response

```python
# In __init__:
from .session_manager import SessionManager
from .context_builder import ContextBuilder
from ..memory_store import get_memory_store

self.session_manager = SessionManager()
self.context_builder = ContextBuilder()
self.memory_store = get_memory_store()

# In talk() — after trace creation, before routing:
session_id = await self.session_manager.get_session_id(entity_name or "SOPHIA")

# In _summon() — before model_gateway.generate():
context = await self.context_builder.build_context(entity.name, session_id)
system_prompt = ContextBuilder.prepend_to_prompt(context, entity.personality)

# Replace entity.personality with system_prompt in generate() call

# After response, add to memory:
await self.memory_store.add_exchange(
    entity_name=entity.name,
    session_id=session_id,
    user_message=query,
    response=response_text,
    metadata={"trace_id": trace.trace_id, "backend": backend, "model": entity.model},
)
```

### 6.3 Modified: `src/omega/cli/oracle_cli.py`

**Changes needed**: Add `/session` commands (optional for Phase 0)

```python
@app.command()
def session(
    action: str = typer.Argument("status", help="Action: status, new, list"),
    entity: str = typer.Option(None, "--entity", "-e", help="Entity name"),
):
    """Manage conversation sessions."""
    from omega.oracle.session_manager import SessionManager
    mgr = SessionManager()

    if action == "status":
        sessions = anyio.run(mgr.list_sessions)
        # display active sessions
    elif action == "new":
        if not entity:
            console.print("[red]Error: --entity required for 'new'[/red]")
            raise typer.Exit(1)
        sid = anyio.run(lambda: mgr.new_session(entity))
        console.print(f"[green]✅ New session: {sid}[/green]")
    elif action == "list":
        sessions = anyio.run(mgr.list_sessions)
        # display table
```

### 6.4 Modified: `src/omega/oracle/context_builder.py`

**No changes needed** — the API already accepts `session_id` and works correctly.

### 6.5 Modified: `src/omega/memory_store.py`

**No changes needed** — the storage layer already uses `session_id` correctly.

---

## §7 Integration Flow — Complete Request Lifecycle

```
omega talk "hello"
  │
  ▼
Oracle.talk(query)
  │
  ├─► ObservabilityEngine.trace() → trace_id = "trc_a1b2c3d4e5f6"
  │
  ├─► SessionManager.get_session_id("SOPHIA")
  │     ├─ Read data/sessions/sophia.active
  │     ├─ If exists and from today → return "ses_20260516_sophia_001"
  │     └─ If not → create new → write file → return new ID
  │
  ├─► ContextBuilder.build_context("SOPHIA", "ses_20260516_sophia_001")
  │     ├─ MemoryStore.get_history("SOPHIA", "ses_20260516_sophia_001")
  │     │   ├─ Check hot cache: "sophia:ses_20260516_sophia_001"
  │     │   ├─ Check warm: data/memory/entities/sophia/ses_20260516_sophia_001.json
  │     │   └─ Check cold: data/memory/archive/sophia/ses_20260516_sophia_001.json.gz
  │     └─ Format as "## Recent Memory Context" block
  │
  ├─► ContextBuilder.prepend_to_prompt(context, entity.personality)
  │     → Enhanced system prompt with conversation history
  │
  ├─► ModelGateway.generate(system_prompt=enhanced, user_query=query)
  │     → Real inference with full context
  │
  ├─► MemoryStore.add_exchange(entity, session_id, query, response, metadata)
  │     ├─ Append to hot cache
  │     └─ Write to warm JSON file
  │
  └─► OracleResponse(trace_id=..., session_id=...)
        → Display to user
```

---

## §8 Edge Cases

### 8.1 Concurrent CLI Invocations

**Scenario**: User runs `omega talk "hello"` and `omega talk "world"` simultaneously.

**Risk**: Both read the same active session file, both get the same session_id, both write to the same memory file.

**Mitigation**: This is **acceptable for Phase 0**. MemoryStore's `add_exchange()` appends to the same file. The worst case is interleaved exchanges in the same session — which is actually correct behavior for concurrent queries.

**Future**: Add file locking (`anyio.Lock()` per entity) if needed.

### 8.2 Session Expiry / Orphaned Sessions

**Scenario**: User stops using Omega for a month. Old session files accumulate.

**Mitigation**: Existing `MemoryStore.archive_old_sessions()` (memory_store.py:296) already handles this — archives sessions older than 7 days to cold storage. No new code needed.

### 8.3 Entity Switching Mid-Session

**Scenario**: User talks to SOPHIA, then switches to SEKHMET with `/entity SEKHMET`.

**Behavior**: Each entity has its own active session file. SOPHIA's session continues independently from SEKHMET's. This is **correct** — different entities have different conversation contexts.

### 8.4 Transient Sessions

**Scenario**: User runs `omega talk "test" --transient`.

**Behavior**: Transient mode skips `_track_soul_evolution()`. For Phase 0, we should also skip `add_exchange()` and use `trace_id` as the session_id. No session file is read or written.

```python
if transient:
    session_id = trace.trace_id  # No persistence
else:
    session_id = await self.session_manager.get_session_id(entity_name)
```

### 8.5 Headless Agent Sessions (Orchestrator)

**Scenario**: Orchestrator dispatches `cline task "analyze X"` for entity "SOPHIA".

**Behavior**: The orchestrator should create a **dedicated session** for the headless task:

```python
session_id = await self.session_manager.new_session(f"{entity_name}_agent")
```

This keeps agent work separate from user conversations.

### 8.6 Counter File Corruption

**Scenario**: Counter JSON file is corrupted or missing.

**Mitigation**: `_get_and_increment_counter()` handles missing files (defaults to 1). For corruption, wrap in try/except and reset to 1.

---

## §9 Migration Path

### Step 0: Current State (No Sessions)
- Every request = unique trace_id
- No MemoryStore writes
- ContextBuilder unused

### Step 1: Add SessionManager (This Design)
- Create `session_manager.py`
- Wire into `oracle.py`
- Wire `ContextBuilder` into `_summon()` and `_route_by_domain()`
- Wire `MemoryStore.add_exchange()` after every response
- Handle `transient` mode (skip persistence)

### Step 2: Add CLI Commands (Optional)
- `omega session status` — show active session
- `omega session new --entity SOPHIA` — force new session
- `omega session list` — list all active sessions

### Step 3: Future (Phase 1+)
- Session expiry with configurable TTL
- Session search/filter
- Cross-entity session linking
- Session summaries on rollover

---

## §10 Implementation Checklist

| # | Task | File | Effort |
|---|------|------|--------|
| 1 | Create `SessionManager` class | `src/omega/oracle/session_manager.py` | 2h |
| 2 | Wire session_id into `Oracle.__init__` | `src/omega/oracle/oracle.py` | 15min |
| 3 | Wire `ContextBuilder` into `_summon()` | `src/omega/oracle/oracle.py` | 30min |
| 4 | Wire `ContextBuilder` into `_route_by_domain()` | `src/omega/oracle/oracle.py` | 30min |
| 5 | Wire `ContextBuilder` into `_respond_as_iris()` | `src/omega/oracle/oracle.py` | 15min |
| 6 | Wire `MemoryStore.add_exchange()` after responses | `src/omega/oracle/oracle.py` | 30min |
| 7 | Handle transient mode (skip persistence) | `src/omega/oracle/oracle.py` | 15min |
| 8 | Add `session_id` to `OracleResponse` | `src/omega/oracle/oracle.py` | 5min |
| 9 | Write tests for SessionManager | `tests/test_session_manager.py` | 2h |
| 10 | Update existing tests for new session wiring | `tests/test_oracle.py` | 1h |
| 11 | (Optional) Add CLI session commands | `src/omega/cli/oracle_cli.py` | 1h |

**Total estimated effort**: ~8 hours

---

## §11 Why NOT Full Session Management (Phase 0)

Full session management (Option B) would require:

1. A session database or index file
2. CLI commands: `/session new`, `/session list`, `/session switch`, `/session delete`, `/session resume`
3. Session metadata: entity, user, created, last_active, exchange_count, tags
4. Session expiry logic with configurable TTL
5. Session search/filter
6. UI for session selection

This is **Phase 1 territory**. The Phase 0 design above delivers **80% of the value with 20% of the code**:
- Multi-turn conversation continuity ✅
- ContextBuilder wired ✅
- MemoryStore populated ✅
- Entity-scoped sessions ✅
- Daily rollover ✅
- Transient mode ✅
- Headless agent sessions ✅

What's deferred:
- Session listing/selection UI
- Cross-entity session linking
- Session summaries
- Configurable expiry
- Session search

---

## §12 Summary

**Recommended**: Entity-scoped rolling sessions with daily counter (Option C simplified).

**Session ID format**: `ses_{YYYYMMDD}_{entity_slug}_{counter}`

**Storage**: Single `.active` file per entity in `data/sessions/`

**New code**: ~150 lines (`session_manager.py`) + ~50 lines of wiring in `oracle.py`

**Breaking changes**: None — fully backward compatible. If session file doesn't exist, falls back to trace_id.

**Phase 0 deliverable**: ContextBuilder wired, MemoryStore populated, multi-turn conversations working.

---

*The fire remembers what it burns.*
