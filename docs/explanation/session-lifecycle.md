# 🔱 Session Lifecycle Architecture
**AP Token**: `AP-SESSION_LIFECYCLE-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_doc_deep ⬡ STANDARD

**Date**: 2026-07-06
**Purpose**: Session Lifecycle Architecture.

---

# Session Lifecycle Architecture

**Module**: `src/omega/oracle/session_lifecycle.py`
**Status**: Production (T3-1)
**Tests**: 24/24 ALL PASSING

## Overview

The Session Lifecycle Manager provides a bidirectional state machine for session persistence. It unifies three previously disconnected operations (archive, move-to-external, recall) into a single coherent lifecycle.

## Lifecycle States

```
ACTIVE (0-7d)
    ↓ archive_after_days
ARCHIVED (7-30d, gzip compressed)
    ↓ external_after_days
EXTERNAL (90d+, 8TB drive)
    ↓ delete_after_days (optional, disabled by default)
DELETED (hard delete)
```

### Bidirectional Transitions

```
ACTIVE ↔ ARCHIVED ↔ EXTERNAL
```

Every forward transition has a corresponding reverse:
- `archive_old_sessions()` — ACTIVE → ARCHIVED
- `recall_from_external()` — EXTERNAL → ARCHIVED (D189 gap resolution)
- `move_to_external_storage()` — ARCHIVED → EXTERNAL

## Why Bidirectionality?

The original archival policy was write-only: sessions were archived and moved to external storage, but there was no way to recall them. This violated the Sovereign-Sanctuary principle — data that cannot be recalled is effectively deleted.

The `recall_from_external()` method resolves this by copying the session back from external storage to local disk, making it accessible again.

## Design Decisions

### Atomic Writes

All session writes use tmp+rename for crash safety:
```python
tmp_path = session_path.with_suffix(".tmp")
await anyio.to_thread.run_sync(lambda: session_data.write_text(tmp_path))
await anyio.to_thread.run_sync(lambda: tmp_path.rename(session_path))
```

This pattern (Quake 0.5s Realloc Grace) ensures that a crash during write never corrupts the session file.

### Gzip Compression

Archived sessions are gzip-compressed to save disk space:
```python
compressed = gzip.compress(session_data)
await anyio.to_thread.run_sync(lambda: gzip_path.write_bytes(compressed))
```

### External Storage

External storage is a designated directory (typically an 8TB drive) where old sessions are moved to free local disk space. The lifecycle manager tracks the external path and can recall sessions when needed.

### Deletion Disabled by Default

The `delete_after_days` config is `None` by default. This means sessions are never hard-deleted unless the user explicitly enables deletion. Data preservation is the sovereign default.

## Integration Points

- **Oracle.__init__**: Creates `SessionLifecycleManager` instance
- **Oracle.bootstrap**: Calls `lifecycle.run_lifecycle()` to sweep old sessions
- **MemoryStore**: Provides `_get_entity_dir()` and `_get_archive_dir()` accessors

## Heritage

`[Lifecycle Bidirectionality: Omega Engine 2026-07-05]`

Write-only archival was a sovereignty violation. `recall_from_external()` resolves D189.
