# How to Manage Sessions

**Module**: `src/omega/oracle/session_lifecycle.py`
**Status**: Production (T3-1)

## Overview

The Session Lifecycle Manager provides tools to list, inspect, and recall sessions. This guide covers common operations.

## List Active Sessions

```python
from src.omega.oracle.session_lifecycle import SessionLifecycleManager, SessionState

lifecycle = SessionLifecycleManager(config, memory_store)

# List all active sessions for an entity
active_sessions = await lifecycle.list_sessions("kali", state=SessionState.ACTIVE)
for session in active_sessions:
    print(f"{session.session_id}: {session.size_bytes} bytes, modified {session.modified_at}")
```

## Recall from External Storage

If a session was moved to external storage (90+ days old), you can recall it:

```python
# Recall a specific session
path = await lifecycle.recall_from_external("kali", "ses_20260601_kali_1")
if path:
    print(f"Session recalled to: {path}")
else:
    print("Session not found in external storage")
```

## Check Session State

```python
state = await lifecycle.get_session_state("kali", "ses_20260601_kali_1")
print(f"Session state: {state.value}")  # "active", "archived", or "external"
```

## Get Lifecycle Statistics

```python
stats = await lifecycle.get_stats()
print(f"Total sessions: {stats.total_sessions}")
print(f"Active: {stats.by_state.get(SessionState.ACTIVE, 0)}")
print(f"Archived: {stats.by_state.get(SessionState.ARCHIVED, 0)}")
print(f"External: {stats.by_state.get(SessionState.EXTERNAL, 0)}")
```

## Configure Lifecycle Policies

```python
from src.omega.oracle.session_lifecycle import SessionLifecycleConfig

config = SessionLifecycleConfig(
    archive_after_days=7,      # Archive after 7 days
    external_after_days=90,    # Move to external after 90 days
    delete_after_days=None,    # Never hard-delete (default)
    compression_enabled=True   # Gzip archived sessions
)

lifecycle = SessionLifecycleManager(config, memory_store)
```

## Manual Lifecycle Sweep

The lifecycle runs automatically during `Oracle.bootstrap()`, but you can trigger it manually:

```python
count = await lifecycle.run_lifecycle()
print(f"Processed {count} sessions")
```

## Troubleshooting

### Sessions not archiving

Check that `archive_after_days` is set and sessions are older than the threshold:

```python
stats = await lifecycle.get_stats()
print(f"Active sessions: {stats.by_state.get(SessionState.ACTIVE, 0)}")
```

### Recall fails

Ensure the external storage directory exists and is accessible:

```python
import os
external_dir = memory_store._get_archive_dir("kali")
print(f"External dir: {external_dir}")
print(f"Exists: {os.path.exists(external_dir)}")
```

### Database locked

If you see "database is locked" errors, ensure only one lifecycle sweep is running at a time. The lifecycle uses WAL-mode which allows concurrent reads, but writes are serialized.
