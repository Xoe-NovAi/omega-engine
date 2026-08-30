# Session Lifecycle API Reference

**Module**: `src/omega/oracle/session_lifecycle.py`
**Status**: Production (Session 51)
**Tests**: `tests/test_session_lifecycle.py` (24 tests)

## Overview

The `SessionLifecycleManager` provides a bidirectional session lifecycle with state detection, archival, and recall capabilities. It wraps existing `MemoryStore` methods and adds a unified state machine for session management.

## Lifecycle States

```
ACTIVE (0-7d) → ARCHIVED (7-30d, gzip) → EXTERNAL (90d+, 8TB) → DELETED (optional)
```

- **ACTIVE**: Active session, full read/write access
- **ARCHIVED**: Compressed on local disk (gzip), still readable
- **EXTERNAL**: Moved to external storage (8TB drive), requires recall
- **DELETED**: Hard-deleted (disabled by default for data preservation)

## Classes

### SessionState (Enum)

```python
class SessionState(Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    EXTERNAL = "external"
    DELETED = "deleted"
```

### SessionLifecycleConfig

```python
@dataclass
class SessionLifecycleConfig:
    archive_after_days: int = 7      # Days before archival
    external_after_days: int = 90    # Days before external move
    delete_after_days: Optional[int] = None  # Disabled by default
    compression_enabled: bool = True  # Gzip archived sessions
```

### SessionInfo

```python
@dataclass
class SessionInfo:
    entity: str
    path: Path
    state: SessionState
    modified_time: float
    size_bytes: int
```

### LifecycleStats

```python
@dataclass
class LifecycleStats:
    total_sessions: int
    by_state: Dict[SessionState, int]
    total_size_bytes: int
    archived_size_bytes: int
```

### SessionLifecycleManager

```python
class SessionLifecycleManager:
    def __init__(self, config: SessionLifecycleConfig, memory_store: MemoryStore)
    async def run_lifecycle(self) -> int  # Returns count of sessions processed
    async def recall_from_external(self, entity: str, session_id: str) -> Optional[Path]
    async def get_session_state(self, entity: str, session_id: str) -> SessionState
    async def list_sessions(self, entity: str, state: Optional[SessionState] = None) -> List[SessionInfo]
    async def get_stats(self, entity: Optional[str] = None) -> LifecycleStats
```

## Key Methods

### run_lifecycle()

Performs the full lifecycle sweep: archive old sessions, move to external storage, clean up.

```python
lifecycle = SessionLifecycleManager(config, memory_store)
count = await lifecycle.run_lifecycle()
# Returns: Number of sessions processed
```

### recall_from_external()

Recalls a session from external storage to local disk (D189 gap resolution).

```python
path = await lifecycle.recall_from_external("kali", "ses_20260601_kali_1")
# Returns: Path to recalled session, or None if not found
```

### list_sessions()

Lists sessions by entity and optional state filter.

```python
active_sessions = await lifecycle.list_sessions("kali", state=SessionState.ACTIVE)
all_sessions = await lifecycle.list_sessions("verity")  # All states
```

## Integration Points

- **Oracle.__init__**: Creates `SessionLifecycleManager` instance
- **Oracle.bootstrap**: Calls `lifecycle.run_lifecycle()` to sweep old sessions
- **MemoryStore**: Provides `_get_entity_dir()` and `_get_archive_dir()` accessors

## Heritage

`[Lifecycle Bidirectionality: Omega Engine 2026-07-05]`

Write-only archival was a sovereignty violation. `recall_from_external()` resolves D189.
