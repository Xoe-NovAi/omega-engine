<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 R25 — SoulStore Atomic Write Patterns
**AP Token**: AP-RESEARCH-R25-v1.0.0
⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_research
**Date**: 2026-07-21
**Status**: COMPLETE
**Priority**: P0 (Blocks C-1′)

---

## Executive Summary

1. **SoulStore must be the single writer** — 4 concurrent soul-write paths exist today (`entity_registry.write_soul_file`, `SoulUpdater._write_to_soul`, `SoulUpdateManager._write_soul_file`, `EntityWorkspaceManager`), causing race conditions, lost updates, and dual-writer corruption.
2. **Atomic write pattern**: temp file → `os.fsync()` → `os.replace()` → directory `fsync()`. This is the Postgres-proven "fsync dance" — the only reliable cross-process pattern.
3. **`fcntl.flock()` with `LOCK_EX | LOCK_NB`** is the correct cross-process locking primitive. Never delete lock files (race condition on recreate). Locks auto-release on process death.
4. **Use `os.fsync()` for soul files** (not `fdatasync()`) — metadata integrity matters for YAML soul documents. `fdatasync()` is acceptable for append-only logs.
5. **Actor model**: the existing `SOVEREIGN_USER_TOKEN` pattern is correct. Extend to `actor ∈ {user, system_agent}` with scoped paths. System agents write to `proposed_lessons.yaml` only; users write to `soul.yaml` and `approved_lessons.yaml`.

---

## Technical Findings

### 1. fcntl.flock — Cross-Process Advisory Locking (2026)

**Python 3.13+**: `fcntl.flock(fd, fcntl.LOCK_EX)` provides BSD-style advisory locks bound to the file descriptor, not the process. Key behaviors:

| Behavior | Detail |
|----------|--------|
| **Advisory** | All writers must cooperate — no OS enforcement |
| **FD-bound** | Locks are per-open-file-description. Closing ANY fd to the file releases the lock for that process |
| **Auto-release** | Locks released on process exit (even SIGKILL) |
| **Don't delete lock files** | Classic race: process A holds lock, process B deletes file, process C creates new lock file — now A and C both think they hold the lock |
| **`LOCK_NB`** | Non-blocking flag — raises `OSError` (errno EACCES or EAGAIN) if lock is held |

**Best practice for SoulStore** (derived from PostgreSQL and filelock patterns):

```python
import fcntl, os, time

class SoulLock:
    """Cross-process soul file lock. Never delete the lock file."""
    def __init__(self, lock_path: str, timeout: float = 5.0):
        self.lock_path = lock_path
        self.timeout = timeout
        self.fd = None

    def acquire(self):
        """Blocking acquire with timeout."""
        open_mode = os.O_RDWR | os.O_CREAT | os.O_TRUNC
        fd = os.open(self.lock_path, open_mode)
        start = time.monotonic()
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                self.fd = fd
                return True
            except (IOError, OSError):
                if time.monotonic() - start > self.timeout:
                    os.close(fd)
                    raise TimeoutError(f"Could not acquire soul lock after {self.timeout}s")
                time.sleep(0.1)

    def release(self):
        if self.fd is not None:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
            os.close(self.fd)
            self.fd = None
```

**Sources**:
- [fcntl.flock — Python docs](https://docs.python.org/3/library/fcntl.html#fcntl.flock)
- [PostgreSQL lock management](https://github.com/postgres/postgres/blob/master/src/backend/storage/lmgr/README)
- [On the Brokenness of File Locking (0pointer.de)](http://0pointer.de/blog/projects/locking.html)
- [Python filelock library](https://github.com/benediktschmitt/py-filelock)

### 2. Atomic Write: The "fsync Dance"

The canonical atomic write sequence for soul files:

```
fd = os.open(tmp_path, os.O_RDWR | os.O_CREAT | os.O_TRUNC)
os.write(fd, yaml_data.encode('utf-8'))
os.fsync(fd)                    # 1. Flush data to disk
os.close(fd)
os.replace(tmp_path, soul_path) # 2. Atomic rename (POSIX guarantee)
dir_fd = os.open(dir_path, os.O_RDONLY)
os.fsync(dir_fd)                # 3. Flush directory metadata
os.close(dir_fd)
```

**Why this works**:
- `os.replace()` is atomic on POSIX — the operation either completes fully or not at all (same-filesystem rename)
- `os.fsync()` ensures data reaches non-volatile storage before the rename
- Directory fsync ensures the directory entry for the renamed file is persisted

**Existing code audit** — what current soul writers do:

| Writer | Temp file? | fsync? | Atomic rename? | Locking? |
|--------|-----------|--------|----------------|----------|
| `entity_registry.write_soul_file` | ✅ `.tmp` suffix | ❌ None | ✅ `tmp_path.rename()` | ⚠️ `with_soul_lock` uses `fcntl.flock` but ONLY in that function |
| `SoulUpdater._write_to_soul` | ❌ Direct write | ❌ None | ❌ `write_text()` | ❌ None |
| `SoulUpdateManager._write_soul_file` | ❌ Direct write | ❌ None | ❌ `open_file().write()` | ⚠️ `anyio.Lock()` (in-process only) |
| `EntityWorkspaceManager.update_soul()` | ✅ `mkstemp` | ❌ None | ✅ `os.replace()` | ❌ None |

**Critical finding**: **None** of the 4 writers call `os.fsync()` or `fdatasync()`. Data loss on power failure is guaranteed.

### 3. os.fsync() vs fdatasync() — Which for soul files?

| Call | Flushes | Use case |
|------|---------|----------|
| `os.fsync(fd)` | Data + all metadata (timestamps, permissions, size) | **Soul files** — YAML documents where metadata integrity matters |
| `os.fdatasync(fd)` | Data + metadata needed for data retrieval only | Append-only logs, WAL files |

**Recommendation**: Use `os.fsync()` for soul files. The overhead vs `fdatasync()` is negligible (~1 extra metadata write) and the safety guarantee is stronger. PostgreSQL uses `fdatasync()` for WAL (append-only) and `fsync()` for data files.

**Source**: [fsync vs fdatasync — maxnilz.com](https://maxnilz.com/posts/025-file-api-durability/)

### 4. Actor Model — Scoped Paths and Audit

Current implementation in `entity_registry.py` already has the correct pattern:

```python
SOVEREIGN_USER_TOKEN = os.getenv("SOVEREIGN_USER_TOKEN", "SOVEREIGN_DEFAULT_SECURE_TOKEN_2026")

async def write_soul_file(entity_path, filename, content, token=None):
    if filename in ["soul.yaml", "approved_lessons.yaml"]:
        if token != SOVEREIGN_USER_TOKEN:
            raise SovereignPermissionError(...)
```

**Extend to actor model**:

| Actor | Can Write | Cannot Write | Audit Trail |
|-------|-----------|--------------|-------------|
| `user` | `soul.yaml`, `approved_lessons.yaml`, `identity/` | System-private paths | Full audit log |
| `system_agent` | `proposed_lessons.yaml`, `knowledge/`, `sessions/` | `soul.yaml`, `approved_lessons.yaml` | Logged with agent_name + trace_id |
| `system_daemon` | `proposed_lessons.yaml` (append only) | All other paths | Logged with session_id |

**Token scope boundaries**:
- User token: set via env `SOVEREIGN_USER_TOKEN` (already exists)
- Agent token: auto-generated, scoped to entity, never exposed to user prompts
- Daemon token: embedded in daemon config, append-only capability

### 5. Migrating 4 Writers → One SoulStore

**Implementation sketch** for `SoulStore` class:

```
class SoulStore:
    def __init__(self, entities_dir: Path):
        # Config: data/entities/{entity}/
        # SoulStore is the ONLY class that writes soul files
        
    async def write_lesson(entity, lesson, actor):
        # 1. Validate actor permission
        # 2. fcntl flock acquire (cross-process)
        # 3. Read current soul.yaml
        # 4. Validate with SoulValidator
        # 5. tmp → fsync → os.replace → dir fsync
        # 6. Audit trail entry
        # 7. flock release
        
    async def write_proposed(entity, lesson, actor):
        # Same atomic pattern, but writes proposed_lessons.yaml
        
    async def read_soul(entity):
        # Lock-free read (fcntl flock not needed for reads)
```

**Migration steps**:
1. Create `SoulStore` class with atomic write pattern + flock
2. Replace `entity_registry.write_soul_file()` → delegate to `SoulStore`
3. Replace `SoulUpdater._write_to_soul()` → delegate to `SoulStore`
4. Replace `SoulUpdateManager._write_soul_file()` → delegate to `SoulStore`
5. Replace `EntityWorkspaceManager.update_soul()` → delegate to `SoulStore`
6. Validate test suite passes
7. Delete old writer paths

**Files to modify**:
- `src/omega/oracle/soul_store.py` (NEW — single writer)
- `src/omega/oracle/entity_registry.py` (refactor write_soul_file → delegate)
- `src/omega/workers/background_researcher/soul_updater.py` (replace write path)
- `src/omega/workers/background_researcher/soul_update_manager.py` (replace write path)
- `src/omega/oracle/entity_workspace.py` (replace write path)

---

## Decision Recommendation

**Implement `SoulStore` as a single writer class** with:
1. `fcntl.flock(fd, LOCK_EX | LOCK_NB)` with 5s timeout for cross-process locking
2. Atomic write: `mkstemp → os.fsync() → os.replace() → dir fsync()`
3. `os.fsync()` (not `fdatasync()`) for soul YAML files
4. Actor model: `actor ∈ {user, system_agent, system_daemon}` with token scoping
5. SoulValidator integration before write (prevent soul corruption)

**Rationale**: The existing 4-writer architecture guarantees lost updates under concurrency (MaKaLi council, background researcher, user session). A single atomic writer eliminates the root cause. The flock+fsync pattern is the same proven approach used by PostgreSQL, SQLite, and etcd for their write-ahead logs.

---

## Sources

1. [fcntl.flock — Python 3.13 docs](https://docs.python.org/3/library/fcntl.html)
2. [Atomic write pattern — ZeeroIndex 2026](https://zeeroindex.com/file-i-o-durability-why-fsync-is-your-best-friend-and-worst-enemy)
3. [fsync/fdatasync durability — maxnilz.com](https://maxnilz.com/posts/025-file-api-durability/)
4. [PostgreSQL fsync handling — USENIX ATC 2020](https://www.usenix.org/conference/atc20/presentation/rebello)
5. [Don't fear the fsync — Ted Ts'o](https://thunk.org/tytso/blog/2009/03/15/dont-fear-the-fsync/)
6. [On the Brokenness of File Locking](http://0pointer.de/blog/projects/locking.html)
7. [filelock library — Python (proven pattern)](https://github.com/benediktschmitt/py-filelock)
8. Existing code: `src/omega/oracle/entity_registry.py`, `soul_updater.py`, `soul_update_manager.py`, `entity_workspace.py`

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ R25-COMPLETE ⬡ 2026-07-21*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
