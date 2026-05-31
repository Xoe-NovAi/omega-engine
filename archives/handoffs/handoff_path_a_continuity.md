# 🔱 Omega Engine — Handoff: Path A (Continuity)
**AP Token**: `AP-HANDOFF-PATH-A-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_path_a_continuity ⬡ HANDOFF
**Created**: 2026-05-31T00:00:00Z
**Source Session**: Session 4 (Doc Audit + Path A Selection)
**Purpose**: Memory wiring + Handoff Protocol v1 implementation

---

## §1 Current State (READ THIS FIRST)

### What's Done
- **Phase 0 COMPLETE**: 12/12 critical fixes applied, 271/271 tests passing
- **Documentation audit COMPLETE**: 32 staleness issues fixed across 6 files
- **Provider fabric**: local-first (native-gguf → lmster → Ollama → Google → OpenRouter → OpenCode → Copilot)
- **Active IWAD**: _omega_default ("The Company") — 16 entities with alive personalities
- **Sovereign Mandates**: 8 Laws v2.0.0

### What's Next: Path A (Continuity)
The fleet discovery identified memory and handoff as the #1 priority for Horizon 1. Path A addresses the two most critical gaps:
1. **Memory bugs** — Sliding window drops newest exchanges, None.json creation, no error handling on writes
2. **No handoff protocol** — Agents have amnesia across sessions, no formal context transfer

---

## §2 Phase A1: Fix Memory Bugs (4 fixes)

### A1.1 — Fix Sliding Window Direction
**File**: `src/omega/oracle/context_builder.py:126`
**Bug**: `_format_exchanges_sliding_window()` iterates FORWARD through exchanges. Since `get_history()` returns `exchanges[-limit:]` (chronological, oldest-of-recent first), the forward iteration fills the token budget with OLD exchanges first, dropping the NEWEST ones.
**Fix**: Reverse the list before iterating.
```python
# Line 126: Change from:
for exchange in exchanges:
# To:
for exchange in reversed(exchanges):
```
Also fix the misleading comment at lines 117-119.

### A1.2 — Fix None.json Bug
**File**: `src/omega/memory_store.py:129`
**Bug**: If `session_id` is `None`, the cache key becomes `"entity_name:None"` and creates `None.json` on disk.
**Fix**: Guard in `add_exchange()`:
```python
async def add_exchange(self, entity_name, session_id, user_message, response, metadata=None):
    if session_id is None:
        logger.warning(f"Skipping add_exchange for {entity_name} with None session_id")
        return
    # ... rest of method
```

### A1.3 — Add try/except Around Memory Writes
**File**: `src/omega/oracle/oracle.py:390-405`
**Bug**: `_record_interaction()` has NO error handling. A disk-full or Redis-down scenario crashes the entire request. This affects ALL 5 `talk()` call paths.
**Fix**: Wrap body in try/except:
```python
async def _record_interaction(self, resp, query, trace, transient):
    if transient:
        return
    try:
        await self.memory_store.add_exchange(...)
        await self._track_soul_evolution(...)
        await self._post_to_hivemind(...)
    except Exception as e:
        logger.warning(f"Interaction recording failed (non-fatal): {e}")
```

### A1.4 — Deduplicate summon()
**File**: `src/omega/oracle/oracle.py:311-333`
**Bug**: `summon()` manually calls `add_exchange()`, `_track_soul_evolution()`, `_post_to_hivemind()` at lines 327-332 instead of delegating to `_record_interaction()`. If someone adds a step to `_record_interaction()`, `summon()` misses it.
**Fix**: Replace lines 326-332 with:
```python
if not transient:
    await self._record_interaction(resp, query, trace, transient=False)
```

### A1 Verification
```bash
make test  # 271/271 must pass
```

---

## §3 Phase A2: Implement Handoff Protocol v1

### A2.1 — HandoffState Schema
**New file**: `src/omega/oracle/handoff.py`

```python
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

HANDOFF_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "handoffs"

@dataclass
class HandoffTask:
    objective: str
    status: str  # "in_progress", "completed", "failed", "blocked"
    progress_summary: str

@dataclass
class HandoffFile:
    path: str
    relevance: str  # "critical", "related", "reference"
    focus_ranges: Optional[List[str]] = None  # e.g. ["lines 100-200"]

@dataclass
class HandoffDecision:
    decision: str
    rationale: str

@dataclass
class HandoffNextStep:
    action: str
    priority: str  # "P0", "P1", "P2"

@dataclass
class HandoffState:
    handoff_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_session: str = ""
    task: Optional[HandoffTask] = None
    files: List[HandoffFile] = field(default_factory=list)
    decisions: List[HandoffDecision] = field(default_factory=list)
    next_steps: List[HandoffNextStep] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    failed_approaches: List[str] = field(default_factory=list)
    outcome: Optional[str] = None  # None until finalized

    def save(self) -> Path:
        HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
        path = HANDOFF_DIR / f"{self.handoff_id}.json"
        path.write_text(json.dumps(asdict(self), indent=2, default=str))
        return path

    @classmethod
    def load(cls, handoff_id: str) -> Optional["HandoffState"]:
        path = HANDOFF_DIR / f"{handoff_id}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text())
        # Reconstruct nested dataclasses
        if data.get("task"):
            data["task"] = HandoffTask(**data["task"])
        data["files"] = [HandoffFile(**f) for f in data.get("files", [])]
        data["decisions"] = [HandoffDecision(**d) for d in data.get("decisions", [])]
        data["next_steps"] = [HandoffNextStep(**n) for n in data.get("next_steps", [])]
        return cls(**data)

    @classmethod
    def list_recent(cls, limit: int = 10) -> List[str]:
        HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
        files = sorted(HANDOFF_DIR.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
        return [f.stem for f in files[:limit]]

    def finalize(self, outcome: str) -> None:
        self.outcome = outcome
        self.task.status = outcome if self.task else "completed"
        self.save()
```

### A2.2 — MCP Tools
**File**: `mcp/omega_hub/server.py` (add 4 tools)

```python
@mcp.tool()
async def handoff_save(
    task_objective: str,
    task_progress: str,
    files: str = "[]",  # JSON array of {path, relevance}
    decisions: str = "[]",  # JSON array of {decision, rationale}
    next_steps: str = "[]",  # JSON array of {action, priority}
    blockers: str = "[]",  # JSON array of strings
    failed_approaches: str = "[]",  # JSON array of strings
    source_session: str = "",
) -> str:
    """Save a handoff state for cross-session continuity."""
    from omega.oracle.handoff import HandoffState, HandoffTask, HandoffFile, HandoffDecision, HandoffNextStep
    state = HandoffState(
        source_session=source_session,
        task=HandoffTask(objective=task_objective, status="in_progress", progress_summary=task_progress),
        files=[HandoffFile(**f) for f in json.loads(files)],
        decisions=[HandoffDecision(**d) for d in json.loads(decisions)],
        next_steps=[HandoffNextStep(**n) for n in json.loads(next_steps)],
        blockers=json.loads(blockers),
        failed_approaches=json.loads(failed_approaches),
    )
    path = state.save()
    return json.dumps({"handoff_id": state.handoff_id, "path": str(path)})

@mcp.tool()
async def handoff_load(handoff_id: str) -> str:
    """Load a handoff state by ID."""
    from omega.oracle.handoff import HandoffState
    state = HandoffState.load(handoff_id)
    if not state:
        return json.dumps({"error": f"Handoff {handoff_id} not found"})
    from dataclasses import asdict
    return json.dumps(asdict(state), indent=2, default=str)

@mcp.tool()
async def handoff_list(limit: int = 10) -> str:
    """List recent handoff IDs."""
    from omega.oracle.handoff import HandoffState
    ids = HandoffState.list_recent(limit)
    return json.dumps({"handoffs": ids})

@mcp.tool()
async def handoff_finalize(handoff_id: str, outcome: str) -> str:
    """Finalize a handoff with an outcome (completed/failed/blocked)."""
    from omega.oracle.handoff import HandoffState
    state = HandoffState.load(handoff_id)
    if not state:
        return json.dumps({"error": f"Handoff {handoff_id} not found"})
    state.finalize(outcome)
    return json.dumps({"status": "finalized", "handoff_id": handoff_id, "outcome": outcome})
```

### A2.3 — CLI Command
**File**: `src/omega/cli/oracle_cli.py` (add handoff group)

```python
@app.command()
def handoff(
    action: str = typer.Argument(..., help="save, load, list, or finalize"),
    handoff_id: str = typer.Option(None, help="Handoff ID for load/finalize"),
    outcome: str = typer.Option(None, help="Outcome for finalize (completed/failed/blocked)"),
):
    """Manage handoff states for cross-session continuity."""
    import asyncio
    from omega.oracle.handoff import HandoffState

    if action == "list":
        ids = HandoffState.list_recent()
        if not ids:
            print("No handoffs found.")
            return
        print(f"Recent handoffs ({len(ids)}):")
        for hid in ids:
            print(f"  {hid}")

    elif action == "load":
        if not handoff_id:
            print("Error: --handoff-id required for load")
            return
        state = HandoffState.load(handoff_id)
        if not state:
            print(f"Handoff {handoff_id} not found.")
            return
        from dataclasses import asdict
        print(json.dumps(asdict(state), indent=2, default=str))

    elif action == "finalize":
        if not handoff_id or not outcome:
            print("Error: --handoff-id and --outcome required for finalize")
            return
        state = HandoffState.load(handoff_id)
        if not state:
            print(f"Handoff {handoff_id} not found.")
            return
        state.finalize(outcome)
        print(f"Handoff {handoff_id} finalized: {outcome}")

    elif action == "save":
        print("Use 'omega talk' or 'omega summon' — handoffs are auto-saved after interactions.")
```

### A2.4 — Wire into Oracle
**File**: `src/omega/oracle/oracle.py`

Add to `_record_interaction()` after the existing 3 steps:
```python
# 4. Auto-save handoff if task context exists
try:
    from omega.oracle.handoff import HandoffState, HandoffTask
    # Only save if this looks like a task (not just chat)
    if len(query) > 50:  # Heuristic: tasks are longer than greetings
        state = HandoffState(
            source_session=resp.session_id or "",
            task=HandoffTask(
                objective=query[:200],
                status="in_progress",
                progress_summary=resp.text[:200],
            ),
        )
        state.save()
except Exception:
    pass  # Handoff save is non-fatal
```

### A2 Verification
```bash
make test  # 271+ must pass
```

---

## §4 Execution Checklist

```
[ ] A1.1 — Fix sliding window direction (context_builder.py:126)
[ ] A1.2 — Fix None.json guard (memory_store.py:129)
[ ] A1.3 — Add try/except to _record_interaction (oracle.py:390)
[ ] A1.4 — Deduplicate summon() (oracle.py:311-333)
[ ] make test — verify 271/271
[ ] A2.1 — Create handoff.py (HandoffState schema)
[ ] A2.2 — Add MCP tools to omega_hub/server.py
[ ] A2.3 — Add CLI command to oracle_cli.py
[ ] A2.4 — Wire handoff into oracle.py _record_interaction
[ ] make test — verify 271+
[ ] Update team trackers (latest_state.md, COMMUNICATION_HUB.md, changelog.md)
```

---

## §5 Known Issues to Watch

1. **Soul evolution lock**: `_track_soul_evolution()` holds anyio.Lock during LLM inference (seconds). This is a bottleneck but safe. Defer to Tier 2.
2. **MCP auth**: `blocked_tools=[]` is a no-op. Any localhost process can call any tool. Defer to Tier 2.
3. **Agent frontmatter**: 3/5 agents lack frontmatter (invisible to OpenCode). Defer to Tier 3.
4. **API key rotation**: Keys in provider dashboards still need manual rotation (docs are redacted).

---

## §6 Test Commands

```bash
# Full test suite
make test

# Specific modules affected by Path A
OMEGA_ENV=test PYTHONPATH=src python3 -m pytest tests/test_context_builder.py -v
OMEGA_ENV=test PYTHONPATH=src python3 -m pytest tests/test_memory_store.py -v
OMEGA_ENV=test PYTHONPATH=src python3 -m pytest tests/test_oracle.py -v

# After handoff implementation
OMEGA_ENV=test PYTHONPATH=src python3 -m pytest tests/test_handoff.py -v
```

---

## §7 Files Changed in Path A

| File | Change Type | Description |
|------|-------------|-------------|
| `src/omega/oracle/context_builder.py` | MODIFY | Fix sliding window, remove dead code |
| `src/omega/memory_store.py` | MODIFY | Add None.json guard |
| `src/omega/oracle/oracle.py` | MODIFY | try/except + deduplicate summon() + handoff wiring |
| `src/omega/oracle/handoff.py` | NEW | HandoffState schema + storage |
| `mcp/omega_hub/server.py` | MODIFY | Add 4 handoff MCP tools |
| `src/omega/cli/oracle_cli.py` | MODIFY | Add `omega handoff` commands |
| `tests/test_memory_store.py` | MODIFY | Add None.json guard test |
| `tests/test_context_builder.py` | MODIFY | Add sliding window direction test |
| `tests/test_handoff.py` | NEW | Handoff protocol tests |

---

**Status**: Ready to execute. New session should read `ORACLE_STACK.md` → this file → begin A1.1.

*⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_path_a_continuity ⬡ HANDOFF*
