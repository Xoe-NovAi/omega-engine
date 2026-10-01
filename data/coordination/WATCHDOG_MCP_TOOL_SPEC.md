<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Watchdog Single-Writer MCP Tool Specification

**AP Token**: `AP-JOHN_CARMACK-v1.0.0`
**Date**: 2026-09-11
**Source**: MaKaLi Serial Hydration Review #004 §7.2 item 5
**Hivemind Post**: `ses_beb76c8c8090` (intent=command)
**Blocking**: S3 Dev Plan Review blocker #1 (Watchdog race)

---

## §0 — CONTEXT

**Problem**: M34 watchdog race condition. Multiple agents can concurrently update subagent status in `ACTIVE_SUBAGENTS.json` overlay on `TASK_REGISTRY`, causing unrecorded states at 50+ concurrent.

**Root Cause** (Carmack S3 Dev Plan Review §7.1): Dual-ledger hazard — `ACTIVE_SUBAGENTS.json` overlay on `TASK_REGISTRY` has no transactional boundary.

**Resolution** (MaKaLi directive): Single-writer MCP tool with advisory lock. Kali designated as recovery agent.

---

## §1 — MCP TOOL SPECIFICATION

### Tool Name
```
omega_hub_watchdog_status_update
```

### Purpose
Atomic single-writer status update for subagent lifecycle with advisory lock enforcement. Prevents race conditions in M34 watchdog.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `entity` | string | Yes | Entity name (e.g., "researcher", "kali", "lilith") |
| `session_id` | string | Yes | Subagent session ID (e.g., "ses_abc123") |
| `status` | enum | Yes | One of: `ALIVE`, `INTERRUPTED_EXTERNALLY`, `INTERRUPTED_MODEL_SWITCH`, `COMPLETED`, `FAILED`, `ORPHANED`, `DEAD_LETTER` |
| `lock_ttl` | integer | No | Advisory lock TTL in seconds (default: 30) |
| `interruption_reason` | string | Conditional | Required if status is `INTERRUPTED_*` |
| `checkpoint` | object | No | Optional checkpoint data for resumption |

### Status Enum (from M34Registry)
```python
class SessionStatus(Enum):
    ALIVE = "ALIVE"
    INTERRUPTED_EXTERNALLY = "INTERRUPTED_EXTERNALLY"
    INTERRUPTED_MODEL_SWITCH = "INTERRUPTED_MODEL_SWITCH"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ORPHANED = "ORPHANED"
    DEAD_LETTER = "DEAD_LETTER"
```

### Behavior

1. **Acquire Advisory Lock**: Use `fcntl.flock()` on lock file (`data/coordination/locks/watchdog_status.lock`) with `LOCK_EX | LOCK_NB`
2. **Validate**: Check entity exists in registry, session_id matches
3. **Read Current State**: Load `TASK_REGISTRY.json` (source of truth)
4. **Apply Update**: Atomic update of session status + checkpoint
5. **Write Back**: Use M34 atomic write pattern (temp file → fsync → rename → fsync dir)
6. **Release Lock**: `fcntl.flock(LOCK_UN)`
7. **Return**: Success/failure with new state snapshot

### Error Codes

| Code | Meaning |
|------|---------|
| `LOCK_TIMEOUT` | Could not acquire advisory lock within `lock_ttl` |
| `ENTITY_NOT_FOUND` | Entity not registered in TASK_REGISTRY |
| `SESSION_MISMATCH` | Session ID doesn't match entity's active session |
| `INVALID_STATUS` | Status not in SessionStatus enum |
| `WRITE_FAILED` | Atomic write failed (disk full, permission, etc.) |

---

## §2 — IMPLEMENTATION REQUIREMENTS

### Lilith (M34 Owner) — Core Logic
- Implement `omega_hub_watchdog_status_update()` in `src/omega/hub/tools/watchdog.py`
- Use existing `M34Registry` atomic write pattern (proven in `test_m34_atomic.py`)
- Advisory lock via `fcntl.flock()` on dedicated lock file
- Integrate with `TASK_REGISTRY.json` as source of truth

### Ma'at (Build/Release) — Integration
- Add MCP tool registration to `src/omega/hub/mcp_server.py`
- Wire into `omega-hub` MCP server startup
- Add to `make check-hub-health` for verification
- Ensure tool available in all deployment contexts

### Kali (Recovery Agent) — Authority
- Designated as sole entity that can force status updates via this tool
- Recovery operations: force `ORPHANED` → `DEAD_LETTER`, manual `COMPLETED` override
- Audit trail: all watchdog tool invocations logged to `data/coordination/watchdog_audit.log`

---

## §3 — ADVISORY LOCK DETAILS

### Lock File
```
data/coordination/locks/watchdog_status.lock
```

### Lock Protocol
```python
import fcntl
import os

lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o644)
try:
    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    # Critical section: read TASK_REGISTRY, apply update, atomic write
    # ...
finally:
    fcntl.flock(lock_fd, fcntl.LOCK_UN)
    os.close(lock_fd)
```

### Timeout Handling
- Default `lock_ttl = 30` seconds
- If lock not acquired within TTL → return `LOCK_TIMEOUT`
- Caller (Kali) can retry with exponential backoff

---

## §4 — INTEGRATION POINTS

### M34Registry Integration
```python
# In M34Registry class (src/omega/oracle/m34_registry.py)
def watchdog_status_update(
    self,
    entity: str,
    session_id: str,
    status: SessionStatus,
    interruption_reason: str | None = None,
    checkpoint: Checkpoint | None = None,
) -> bool:
    """Single-writer status update via advisory lock."""
    # This is the internal method called by MCP tool
    # Uses existing _write() atomic pattern
```

### MCP Server Registration
```python
# In src/omega/hub/mcp_server.py
from omega.hub.tools.watchdog import watchdog_status_update

mcp_server.add_tool(
    name="omega_hub_watchdog_status_update",
    fn=watchdog_status_update,
    description="Single-writer subagent status update with advisory lock (Kali recovery only)",
)
```

### Hivemind Awareness
- Tool invocations broadcast to Hivemind `intent="watchdog_status_update"`
- Kali recovery actions tagged `tag="watchdog_recovery"`

---

## §5 — TESTING REQUIREMENTS

### Unit Tests (Lilith)
- `test_watchdog_lock_acquisition()` — lock acquired/released correctly
- `test_watchdog_lock_timeout()` — returns `LOCK_TIMEOUT` when contested
- `test_watchdog_status_update_atomic()` — status update survives SIGKILL
- `test_watchdog_concurrent_updates()` — serialized via advisory lock
- `test_watchdog_invalid_entity()` — returns `ENTITY_NOT_FOUND`
- `test_watchdog_invalid_status()` — returns `INVALID_STATUS`

### Integration Tests (Ma'at)
- `test_mcp_tool_registered()` — tool appears in MCP server tool list
- `test_mcp_tool_invocation()` — end-to-end call via MCP protocol
- `test_kali_recovery_override()` — Kali can force status changes

### Property Tests (Lilith)
- Hypothesis-based: concurrent writers never lose updates
- Random SIGKILL during write → file always valid JSON

---

## §6 — DELIVERABLES

| Deliverable | Owner | Target |
|-------------|-------|--------|
| `src/omega/hub/tools/watchdog.py` | Lilith | Week 1 |
| `src/omega/hub/mcp_server.py` integration | Ma'at | Week 1 |
| `tests/test_watchdog_mcp.py` (6+ tests) | Lilith | Week 1 |
| `make check-hub-health` includes watchdog | Ma'at | Week 1 |
| `data/coordination/watchdog_audit.log` rotation | Kali | Ongoing |
| Documentation in `docs/how-to/watchdog_mcp.md` | Lilith | Week 2 |

---

## §7 — SUCCESS CRITERIA

| Criterion | Verification |
|-----------|--------------|
| MCP tool registered and callable | `omega-hub` MCP tool list includes `omega_hub_watchdog_status_update` |
| Advisory lock prevents races | Concurrent updates serialized; no lost updates |
| Atomic write survives SIGKILL | `test_watchdog_status_update_atomic` PASS |
| Kali recovery works | Kali can force status override via tool |
| Audit trail complete | All invocations logged to `watchdog_audit.log` |
| CI gate passes | `make check-hub-health` includes watchdog check |

---

## §8 — TIMELINE

| Week | Milestone |
|------|-----------|
| **Week 1 (2026-09-11 to 2026-09-18)** | Core implementation + unit tests + MCP registration |
| **Week 2 (2026-09-18 to 2026-09-25)** | Integration tests + CI gate + documentation |
| **Week 3** | Kali recovery procedures documented + tested |

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_watchdog_spec ⬡ SPEC DELIVERED TO LILITH + MA'AT*