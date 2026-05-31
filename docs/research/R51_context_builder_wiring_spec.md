# 🔱 ContextBuilder Wiring — Implementation Specification

**AP Token**: `AP-CTX-WIRE-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ qwen3.6-plus-free ⬡ opencode ⬡ trc_research ⬡ SPEC

**Date**: 2026-05-16
**Author**: Sovereign Master Researcher (aggregated from 4 subagent audits)
**Urgency**: 🔴 Critical — Blocks all Phase 1 soul architecture work
**Status**: Design complete — ready for implementation

---

## §1 Executive Summary

The ContextBuilder class (`src/omega/oracle/context_builder.py`, 168 lines) and MemoryStore class (`src/omega/memory_store.py`, 320 lines) are fully implemented but **never wired into the Oracle**. Every request to the Oracle is completely stateless — no conversation history, no soul context injection, no cross-pollination.

This spec defines the minimal wiring to enable persistent multi-turn conversations. The design follows the R50 session architecture (entity-scoped rolling sessions with daily counter) and reclaims proven patterns from the legacy codebase.

**Estimated effort**: ~8 hours
**Risk**: Low — all components exist, this is purely wiring + test coverage

---

## §2 Current State Assessment

### What Exists (Working)
| Component | File | Status |
|-----------|------|--------|
| ContextBuilder class | `src/omega/oracle/context_builder.py` | ✅ Complete, 0 tests |
| MemoryStore class | `src/omega/memory_store.py` | ✅ Complete, 0 tests |
| SessionManager design | `docs/research/R50_session_id_architecture.md` | ✅ Designed, not implemented |
| Oracle talk/summon | `src/omega/oracle/oracle.py` | ✅ Working, no memory |
| EntityRegistry | `src/omega/oracle/entity_registry.py` | ✅ Working |
| ModelGateway | `src/omega/oracle/model_gateway.py` | ✅ Working |
| Test suite | `tests/` | 123 tests passing, 0 memory tests |

### What's Missing (Blocking)
| Gap | Severity | Fix |
|-----|----------|-----|
| DATA_DIR path mismatch | BLOCKING | Standardize memory_store.py to oracle.py path pattern |
| No ContextBuilder in Oracle | BLOCKING | Wire into `__init__`, `_summon()`, `_route_by_domain()`, `_respond_as_iris()` |
| No MemoryStore.add_exchange() calls | BLOCKING | Call after every response in all 3 response paths |
| No session_id generation | BLOCKING | Implement SessionManager per R50 design |
| Singleton state leakage in tests | MAJOR | Add `reset_memory_store()` + OMEGA_ENV=test guard |
| Zero MemoryStore/ContextBuilder tests | MAJOR | 37 new tests needed |
| Module-level side effects in MemoryStore | MINOR | Defer mkdir to first use |

---

## §3 Architecture Design

### 3.1 Session ID Format

Per R50 design: `ses_{YYYYMMDD}_{entity_slug}_{counter}`

Examples:
- `ses_20260516_sophia_001`
- `ses_20260516_sekhmet_003`
- `ses_20260517_sophia_001` (new day → counter resets)

### 3.2 Session Lifecycle

```
CLI invocation → SessionManager.get_session_id(entity)
  → Read data/sessions/{entity}.active
  → If file exists AND same date → return existing session_id
  → If file missing OR different date → create new session (counter=1)
  → Write updated .active file
  → Return session_id

Transient mode → skip SessionManager, use trace.trace_id as session_id
```

### 3.3 Data Flow (After Wiring)

```
User query → Oracle.talk()
  → trace_id generated (observability)
  → session_id resolved (SessionManager or trace_id for transient)
  → context_block = ContextBuilder.build_context(entity_name, session_id)
  → system_prompt = ContextBuilder.prepend_to_prompt(context_block, entity.personality)
  → response = ModelGateway.generate(system_prompt, query)
  → MemoryStore.add_exchange(entity_name, session_id, query, response, metadata)
  → _track_soul_evolution(entity_name, trace_id)
  → return OracleResponse
```

### 3.4 Reclaimed Legacy Patterns

From the legacy mining audit, these patterns are proven and should be adopted:

| Pattern | Source | Application |
|---------|--------|-------------|
| Bounded deque for session history | `omega-stack-legacy/.../session_manager.py` | MemoryStore already uses list slicing — equivalent behavior |
| Dual-limit truncation (per-doc + total) | `omega-stack-legacy/rag_service.py` | Add `max_total_chars` parameter to ContextBuilder |
| Holographic scoring formula | `xna-omega-legacy/.../hologram.py` | Phase 2 enhancement — not needed for Phase 0 |
| Entity-aware prompt building | `omega-stack-legacy/.../chainlit_app_unified.py` | Exactly what ContextBuilder.prepend_to_prompt does |

---

## §4 Implementation Plan

### Phase 0a: Infrastructure Fixes (Blocking, ~1 hour)

#### Fix 1: Standardize DATA_DIR in memory_store.py

```python
# BEFORE (memory_store.py:31):
DATA_DIR = Path(os.environ.get(
    "OMEGA_DATA_DIR",
    str(Path.home() / "omega" / "data")
))

# AFTER:
DATA_DIR = Path(os.environ.get(
    "OMEGA_DATA_DIR",
    str(Path(__file__).resolve().parent.parent.parent.parent / "data")
))
```

#### Fix 2: Add OMEGA_ENV=test guard around mkdir

```python
# BEFORE (memory_store.py:37-38):
for d in [MEMORY_DIR, TRACE_DIR, ENTITY_DIR, ARCHIVE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# AFTER:
if os.environ.get("OMEGA_ENV") != "test":
    for d in [MEMORY_DIR, TRACE_DIR, ENTITY_DIR, ARCHIVE_DIR]:
        d.mkdir(parents=True, exist_ok=True)
```

#### Fix 3: Add reset_memory_store() function

```python
# Add at end of memory_store.py (after get_memory_store):
def reset_memory_store() -> None:
    """Reset the singleton instance. Used for testing."""
    global _memory_store
    _memory_store = None
```

#### Fix 4: De-duplicate MAX_CONTEXT_EXCHANGES constant

Create `src/omega/oracle/constants.py`:
```python
"""Shared constants for Oracle subsystem."""
DEFAULT_CONTEXT_LIMIT = 6
MAX_HISTORY_EXCHANGES = 20
```

Update both `memory_store.py` and `context_builder.py` to import from this file.

### Phase 0b: SessionManager Implementation (~2 hours)

New file: `src/omega/oracle/session_manager.py` (~150 lines)

```python
"""Session Manager — Entity-scoped rolling sessions with daily counter.

Implements the R50 session architecture. Each entity has one active session
per day, persisted to data/sessions/{entity}.active. Transient mode falls
back to trace_id with no persistence.
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

SESSION_DIR = Path(os.environ.get(
    "OMEGA_DATA_DIR",
    str(Path(__file__).resolve().parent.parent.parent.parent / "data")
)) / "sessions"


class SessionManager:
    """Manages entity-scoped rolling sessions."""

    def __init__(self, session_dir: Optional[Path] = None):
        self.session_dir = session_dir or SESSION_DIR
        if os.environ.get("OMEGA_ENV") != "test":
            self.session_dir.mkdir(parents=True, exist_ok=True)

    def get_session_id(self, entity_name: str) -> str:
        """Get or create the active session ID for an entity.

        Returns existing session if same day, otherwise creates new one.
        Session ID format: ses_{YYYYMMDD}_{entity_slug}_{counter}
        """
        entity_slug = entity_name.lower().replace(" ", "_")
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        active_file = self.session_dir / f"{entity_slug}.active"

        counter = 1
        if active_file.exists():
            try:
                data = json.loads(active_file.read_text())
                stored_date = data.get("date", "")
                stored_counter = data.get("counter", 0)
                if stored_date == today:
                    counter = stored_counter + 1
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to read session file {active_file}: {e}")

        session_id = f"ses_{today}_{entity_slug}_{counter:03d}"

        # Persist active session
        try:
            active_file.write_text(json.dumps({
                "date": today,
                "counter": counter,
                "session_id": session_id,
                "entity": entity_name,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }, indent=2))
        except OSError as e:
            logger.warning(f"Failed to write session file {active_file}: {e}")

        return session_id

    def get_session_id_transient(self, trace_id: str) -> str:
        """Return trace_id as session_id for transient mode.

        Transient sessions are not persisted — each request is unique.
        """
        return trace_id
```

### Phase 0c: Wire ContextBuilder into Oracle (~3 hours)

#### Changes to `src/omega/oracle/oracle.py`

**1. Add imports:**
```python
from .context_builder import ContextBuilder
from .session_manager import SessionManager
from ..memory_store import get_memory_store
```

**2. Update `__init__`:**
```python
def __init__(
    self,
    registry: Optional[EntityRegistry] = None,
    model_gateway: Optional[ModelGateway] = None,
    session_manager: Optional[SessionManager] = None,
    context_builder: Optional[ContextBuilder] = None,
):
    self.registry = registry or EntityRegistry()
    self.model_gateway = model_gateway or ModelGateway()
    self.session_manager = session_manager or SessionManager()
    self.context_builder = context_builder or ContextBuilder()
    self.memory_store = get_memory_store()
    # ... rest of existing init code ...
```

**3. Update `_summon()` method (around line 247):**
```python
async def _summon(self, entity_name: str, query: str, trace: TraceSession, transient: bool = False) -> OracleResponse:
    """Summon a specific entity and generate a response."""
    entity = self.registry.get(entity_name)
    if not entity:
        entity = self.registry.find_by_name_fragment(entity_name)

    if not entity:
        trace.log("entity.not_found", entity=entity_name)
        return await self._route_by_domain(query or entity_name, trace, transient=transient)

    trace.log("entity.matched", entity=entity.name, pillars=entity.pillars)

    # Resolve session_id
    if transient:
        session_id = self.session_manager.get_session_id_transient(trace.trace_id)
    else:
        session_id = self.session_manager.get_session_id(entity.name)

    # Build context from memory
    context_block = await self.context_builder.build_context(entity.name, session_id)
    system_prompt = ContextBuilder.prepend_to_prompt(context_block, entity.personality)

    # Generate response
    response_text = await self.model_gateway.generate(
        model_name=entity.model,
        system_prompt=system_prompt,
        user_query=query,
        temperature=entity.temperature,
        max_tokens=1024,
    )

    backend = await self.model_gateway.get_preferred_backend()
    sigil_str = f" {entity.sigil}" if entity.sigil else ""

    result = OracleResponse(
        text=f"{entity.name} says: {response_text}{sigil_str}",
        entity=entity.name,
        pillars=entity.pillars,
        sigil=entity.sigil,
        glyph=entity.glyph,
        pantheon=entity.pantheon,
        domains=entity.domains,
        confidence=1.0,
        trace_id=trace.trace_id,
        backend=backend,
        model=entity.model,
        session_id=session_id,  # NEW FIELD
    )

    # Persist exchange to memory (skip for transient)
    if not transient:
        try:
            await self.memory_store.add_exchange(
                entity_name=entity.name,
                session_id=session_id,
                user_message=query,
                response=response_text,
                metadata={
                    "trace_id": trace.trace_id,
                    "backend": backend,
                    "model": entity.model,
                    "context_exchanges": len(context_block.split("---")) if context_block else 0,
                },
            )
        except Exception as e:
            logger.warning(f"Failed to persist exchange to memory: {e}")

    trace.log("model.completed", entity=entity.name, backend=backend, session_id=session_id)
    trace.record(
        query=query,
        system_prompt=system_prompt,
        response=response_text,
        entity=entity.name,
        model=entity.model,
        backend=backend,
        confidence=1.0,
        session_id=session_id,
    )
    return result
```

**4. Update `_route_by_domain()` method (around line 297):**
Same pattern as `_summon()` — add session_id resolution, context building, and memory persistence.

**5. Update `_respond_as_iris()` method (around line 213):**
Same pattern — add session_id resolution, context building, and memory persistence.

**6. Add `session_id` field to `OracleResponse` dataclass:**
```python
@dataclass
class OracleResponse:
    text: str
    entity: str
    pillars: List[str] = field(default_factory=list)
    role: Optional[str] = None
    sigil: Optional[str] = None
    glyph: Optional[str] = None
    pantheon: Optional[str] = None
    domains: List[str] = field(default_factory=list)
    confidence: float = 0.0
    trace_id: Optional[str] = None
    session_id: Optional[str] = None  # NEW
    backend: Optional[str] = None
    model: Optional[str] = None
    phase: str = "Phase-0"
    escalated: bool = False
```

**7. Update `talk()` method to pass `transient` flag to `_summon()` and `_route_by_domain()`:**
The `transient` parameter already exists on `talk()` but is not forwarded to internal methods. Add it.

### Phase 0d: Test Suite (~2 hours)

#### New file: `tests/conftest.py`
```python
import os
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from omega.memory_store import MemoryStore, reset_memory_store
from omega.oracle.context_builder import ContextBuilder


@pytest.fixture
def temp_data_dir(tmp_path, monkeypatch):
    """Create isolated temp data directory for tests."""
    monkeypatch.setenv("OMEGA_DATA_DIR", str(tmp_path))
    reset_memory_store()
    yield tmp_path
    reset_memory_store()


@pytest.fixture
def mock_memory_store():
    """Mock MemoryStore with configurable get_history return value."""
    store = MagicMock(spec=MemoryStore)
    store.get_history = AsyncMock(return_value=[])
    store.add_exchange = AsyncMock()
    return store


@pytest.fixture
def context_builder(mock_memory_store):
    """ContextBuilder with injected mock MemoryStore."""
    return ContextBuilder(memory_store=mock_memory_store)


@pytest.fixture
def sample_exchanges():
    """Standard test fixture: 2 conversation exchanges."""
    return [
        {
            "timestamp": "2026-05-16T10:00:00+00:00",
            "user": "What is strength?",
            "assistant": "Strength is the will to endure.",
            "metadata": {},
        },
        {
            "timestamp": "2026-05-16T10:01:00+00:00",
            "user": "And what is courage?",
            "assistant": "Courage is strength in the face of fear.",
            "metadata": {},
        },
    ]
```

#### New file: `tests/test_memory_store.py` — 12 tests
- `test_get_history_empty_returns_list`
- `test_add_exchange_stores_in_hot_cache`
- `test_add_exchange_persists_to_warm_file`
- `test_get_history_reads_from_hot_cache`
- `test_get_history_respects_limit`
- `test_get_history_from_warm_file`
- `test_compact_keeps_first_and_last`
- `test_archive_session_moves_to_cold`
- `test_trace_exchange_creates_file`
- `test_stats_returns_dict`
- `test_close_flushes_hot_cache`
- `test_get_memory_store_returns_singleton`

#### New file: `tests/test_context_builder.py` — 22 tests
- Constructor tests (2)
- build_context happy path (4)
- build_context edge cases (4)
- build_context_for_user (3)
- _format_exchanges (2)
- _format_timestamp (3)
- prepend_to_prompt (4)

#### Update: `tests/test_oracle.py` — add 3 integration tests
- `test_oracle_talk_injects_context_into_prompt`
- `test_oracle_talk_with_no_memory_still_works`
- `test_oracle_talk_context_builder_exception_does_not_crash`

---

## §5 Edge Cases

| Edge Case | Handling |
|-----------|----------|
| MemoryStore.get_history() raises exception | ContextBuilder catches and returns `""` — graceful degradation |
| Session file corrupted | SessionManager logs warning, creates new session (counter=1) |
| Disk full during add_exchange | Oracle logs warning, continues — response still returned |
| Concurrent requests same entity | SessionManager uses file locking via atomic write — counter increments safely |
| Transient mode | SessionManager returns trace_id, MemoryStore.add_exchange skipped |
| Entity not found | Falls back to domain routing, still gets session_id and memory |
| Empty query | Returns early — no session_id resolution, no memory operations |
| OMEGA_ENV=test | MemoryStore skips mkdir, SessionManager uses temp dir |

---

## §6 Migration Path

### From Current State (trace_id only)
1. Deploy Phase 0a fixes — no behavior change, just infrastructure
2. Deploy SessionManager — new sessions start using `.active` files
3. Deploy ContextBuilder wiring — new requests get memory context
4. Existing trace_ids continue to work (transient mode fallback)
5. Old conversation files (if any) in `~/omega/data/memory/` are orphaned — no migration needed

### Backward Compatibility
- `OracleResponse` gains optional `session_id` field — existing consumers ignore it
- `talk()` and `summon()` signatures unchanged — `transient` parameter already exists
- `ContextBuilder` and `SessionManager` are injectable — tests can mock them
- MemoryStore singleton is preserved — existing code that calls `get_memory_store()` still works

---

## §7 Verification Checklist

After implementation, verify:

- [ ] `make test` — 160 tests passing (123 existing + 37 new)
- [ ] `make lint` — no new warnings
- [ ] `omega talk "hello"` — works, creates session file
- [ ] `omega talk "what did I just say?"` — references previous exchange
- [ ] `omega talk "hello" --transient` — works, no session file created
- [ ] `data/sessions/sophia.active` — exists after non-transient talk
- [ ] `data/memory/entities/sophia/ses_*.json` — exists with exchanges
- [ ] `OMEGA_ENV=test make test` — no disk writes outside temp dirs
- [ ] Multiple CLI invocations same day → same session_id
- [ ] Next day → new session_id, counter resets to 001

---

## §8 Known Unknowns

| Unknown | Impact | Resolution |
|---------|--------|------------|
| MemoryStore.get_history() return format | May not match ContextBuilder expectations | Verify during Phase 0a — both use `List[Dict[str, str]]` with `user`/`assistant`/`timestamp` keys |
| Session file locking on Windows | Atomic write may behave differently | Test on Windows if cross-platform support needed |
| Context window overflow with large memory | System prompt may exceed model limits | Add `max_total_chars` parameter (Phase 1) |
| MemoryStore singleton in production | Multiple Oracle instances share state | Acceptable for CLI — one process. For server mode (future), use dependency injection |

---

## §9 Implementation Note

**To the Builder**: This is a straightforward wiring task. The hard architectural decisions are already made (R50 design, legacy patterns reclaimed). The implementation is mechanical:

1. Fix the 4 infrastructure items (DATA_DIR, OMEGA_ENV guard, reset function, constants)
2. Create SessionManager (~150 lines, copy from spec)
3. Wire ContextBuilder into Oracle's 3 response methods (~50 lines of changes)
4. Write 37 tests (~300 lines)

The biggest risk is test infrastructure — the singleton pattern in MemoryStore and the lack of `conftest.py` will cause flaky tests if not addressed first. Do Phase 0a and 0d before Phase 0c.

**Estimated total effort**: 8 hours
**Risk level**: Low — all components exist, this is integration work
**Dependencies**: None — can be done in parallel with other Phase 0 tasks
