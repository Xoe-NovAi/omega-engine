# 🔱 Infra — SQLite Policy & Subagent Pool
**AP Token**: `AP-INFRA-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Reference documentation for the Infra package — SQLite connection policy (profiled PRAGMAs) and subagent pool infrastructure.
**Tags**: infra, sqlite, policy, subagent, pool, tmux, profile
**Cross-references**: src/omega/infra/sqlite_policy.py, src/omega/infra/subagent_pool/, SOVEREIGN_MANDATES.md

---

## Overview

The `infra` package provides **infrastructure-level utilities** for the Omega Engine:

1. **SQLite Policy** — Profiled connection configuration (D-282, FS-Β4)
2. **Subagent Pool** — TMux-based subagent orchestration infrastructure

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Infra Package                           │
├─────────────────────────────────────────────────────────────┤
│  sqlite_policy.py    │  Profiled SQLite connections         │
│  subagent_pool/      │  TMux-based subagent orchestration   │
│    orchestrator.py   │    Pool orchestrator                 │
│    mcp_coordinator.py│    MCP coordination                  │
│    tmux_manager.py   │    TMux session management           │
│    profile_manager.py│    Profile management                │
│    models.py         │    Data models                       │
│    account_registry.py│   Account registry                 │
└─────────────────────────────────────────────────────────────┘
```

---

## SQLite Policy (sqlite_policy.py)

**Sovereign SQLite Policy** — Profiled connection configuration. **D-282 PRAGMA stack is law** for memory fabric. Profiles not one stack — separate profiles: memory / search / metrics / reader.

### Profiles

| Profile | Use Case | Key PRAGMAs |
|---------|----------|-------------|
| `memory` | Memory fabric (A10) | WAL, cache=32MB, mmap=256MB, wal_autocheckpoint=10000 |
| `search` | Search persistence | WAL, cache=64MB, mmap=256MB, wal_autocheckpoint=10000 |
| `metrics` | Metrics DB | WAL, cache=32MB, mmap=128MB, wal_autocheckpoint=10000 |
| `reader` | Read-only access | WAL, cache=32MB, **wal_autocheckpoint=0** (never checkpoint) |

### SQLCipher Integration (AP-SQLCIPHER-ENCRYPTION-v1.0.0)

- **2026 SOTA**: `sqlcipher3` (coleifer) — maintained binding
- **DO NOT USE**: `pysqlcipher3` (rigglemania) — archived 2023-01
- **SQLCipher 4.x defaults**: AES-256, PBKDF2-HMAC-SHA512, 256,000 KDF iterations

**Activation** (signal-driven):
1. `OMEGA_SQLCIPHER_KEY` environment variable
2. OS keyring (service=`omega-engine-sqlcipher`)
3. 0600-perm key file

If none resolve → falls back to plaintext sqlite3 **UNLESS** `OMEGA_SQLCIPHER_REQUIRED=1` (then hard-stop M23).

---

### Core Functions

#### `get_sqlite_connection(path, profile="memory", readonly=False, timeout=30.0) -> sqlite3.Connection`
Get standardized SQLite connection with profiled PRAGMAs.

```python
from omega.infra.sqlite_policy import get_sqlite_connection, Profile
from pathlib import Path

# Writer connection (memory profile)
conn = get_sqlite_connection(Path("data/memory.db"), profile="memory")

# Reader connection (reader profile, read-only via URI)
conn = get_sqlite_connection(Path("data/search.db"), profile="reader", readonly=True)
```

**Connection Flavor Decision**:
1. If `sqlcipher3` available + key resolvable → encrypted connection
2. Else if `readonly=True` → `sqlite3.connect("file:path?mode=ro", uri=True)`
3. Else → standard `sqlite3.connect()`

**PRAGMA key** (SQLCipher) set **before any other PRAGMA** via parameter binding (not f-string) to avoid key logging.

#### `sqlite_transaction(path, profile="memory", readonly=False, timeout=30.0) -> ContextManager`
Context manager for atomic transactions.

```python
from omega.infra.sqlite_policy import sqlite_transaction

with sqlite_transaction(Path("data/memory.db"), profile="memory") as conn:
    conn.execute("INSERT INTO ...")
    # Auto-commits on success, rolls back on exception
```

#### `init_database(path, schema_sql, profile="memory") -> None`
Initialize database with schema (idempotent).

#### `verify_pragmas(conn, profile="memory") -> Dict[str, Any]`
Verify connection has expected PRAGMAs (for contract tests).

```python
results = verify_pragmas(conn, profile="search")
# {"journal_mode": {"expected": "WAL", "actual": "WAL", "match": True}, ...}
```

#### `optimize_connection(conn) -> None`
Run `PRAGMA optimize=0x10002` (call before close for query planner stats).

#### `get_writer_connection(path, timeout=30.0) -> sqlite3.Connection`
Convenience: writer connection with writer profile.

#### `get_reader_connection(path, timeout=30.0) -> sqlite3.Connection`
Convenience: reader connection with reader profile (read-only).

---

### Periodic Optimize Timer

```python
start_optimize_timer(interval_seconds=3600)  # 1 hour
stop_optimize_timer()
```

Background thread running `PRAGMA optimize` on open connections periodically.

---

### Usage Example

```python
from omega.infra.sqlite_policy import (
    get_sqlite_connection, sqlite_transaction, 
    init_database, verify_pragmas
)
from pathlib import Path

DB_PATH = Path("data/my_db.sqlite")

# Initialize
SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    value REAL
);
"""
init_database(DB_PATH, SCHEMA, profile="memory")

# Write with transaction
with sqlite_transaction(DB_PATH, profile="memory") as conn:
    conn.execute("INSERT INTO items (name, value) VALUES (?, ?)", ("item1", 1.5))
    conn.execute("INSERT INTO items (name, value) VALUES (?, ?)", ("item2", 2.5))

# Read with reader profile
with sqlite_transaction(DB_PATH, profile="reader", readonly=True) as conn:
    rows = conn.execute("SELECT * FROM items").fetchall()
    for row in rows:
        print(dict(row))

# Verify PRAGMAs in tests
conn = get_sqlite_connection(DB_PATH, profile="memory")
results = verify_pragmas(conn, profile="memory")
assert all(r["match"] for r in results.values())
```

---

## Subagent Pool (subagent_pool/)

TMux-based subagent orchestration infrastructure for managing persistent agent sessions.

### Components

| Module | Purpose |
|--------|---------|
| `orchestrator.py` | Pool orchestration — lifecycle, scaling, health |
| `mcp_coordinator.py` | MCP server coordination for subagents |
| `tmux_manager.py` | TMux session/window/pane management |
| `profile_manager.py` | Agent profile management (models, configs) |
| `models.py` | Data models (AgentProfile, SessionState, etc.) |
| `account_registry.py` | Account credentials registry |

### Key Classes

#### SubagentOrchestrator
```python
from omega.infra.subagent_pool import SubagentOrchestrator

orchestrator = SubagentOrchestrator(
    pool_size=8,
    default_profile="researcher"
)

# Start pool
await orchestrator.start()

# Spawn subagent
session_id = await orchestrator.spawn(
    agent_type="researcher",
    task="Analyze the trade-offs between local-first and cloud fallback"
)

# Get status
status = await orchestrator.get_status(session_id)

# Scale pool
await orchestrator.scale(12)

# Shutdown
await orchestrator.shutdown()
```

#### TmuxManager
```python
from omega.infra.subagent_pool import TmuxManager

tmux = TmuxManager(socket_name="omega-pool")

# Create session
session = tmux.create_session("researcher-001", "bash")

# Send command
tmux.send_keys(session, "python -m omega.workers.youtube_worker --daemon")

# Capture output
output = tmux.capture_pane(session, pane_index=0)
```

#### ProfileManager
```python
from omega.infra.subagent_pool import ProfileManager

profiles = ProfileManager()

# Get agent profile
profile = profiles.get("researcher")
# AgentProfile(model="qwen3-1.7b", temperature=0.7, max_tokens=4096, ...)

# Register custom profile
profiles.register("custom-agent", AgentProfile(
    model="gemma-4b-local",
    temperature=0.5,
    system_prompt="You are a custom agent..."
))
```

---

## Mandate Compliance

| Mandate | SQLite Policy | Subagent Pool |
|---------|---------------|---------------|
| **M1 AnyIO** | Sync; async via `anyio.to_thread` | TMux via `anyio.open_process` |
| **M2 Firewall** | Pure infra; no engine logic | Pool manages agents; no engine deps |
| **M7 Local-First** | Local SQLite; SQLCipher local | TMux local; no cloud deps |
| **M13 Temple-Grade** | Profiled PRAGMAs; verification | Health checks; structured lifecycle |
| **M23 Failure Integrity** | Hard-stop if SQLCipher required | Explicit error propagation |
| **M24 Venv Sovereignty** | `sqlcipher3` in `.venv` | TMux system dependency |

---

## Testing

```bash
pytest tests/test_sqlite_policy.py tests/test_subagent_pool.py -v
```

Key test scenarios:
- Profile PRAGMA verification
- SQLCipher key resolution
- Transaction rollback on error
- Read-only URI connection
- TMux session creation/capture
- Profile registration/lookup
- Orchestrator spawn/scale/shutdown

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ INFRA-v1.0.0 ⬡ 2026-10-02 ⬡*
<!-- PROVENANCE-CORRECTED 2026-10-03T06:22:36Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

