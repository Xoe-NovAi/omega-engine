# 🔱 ADR-001: Memory Layer Architecture
**Status**: Ratified (2026-07-20)
**Decision Makers**: Kali (Oversoul), P2 (Persistence), P8 (Observability)
**Campaign**: Foundation Stabilization Campaign — Gate Γ criterion

---

## Context

The Omega Engine's memory layer had three systemic issues:

1. **PRAGMA fragmentation** — Each memory module (archival, block_store, recall) configured SQLite connections independently, with inconsistent cache sizes (512MB vs 32MB), missing WAL autocheckpoint tuning, and no journal size limits.

2. **BEGIN semantics** — Write transactions used implicit BEGIN, which in WAL mode can silently upgrade from read to write, causing lock starvation under concurrent access.

3. **Connection lifecycle** — No centralized connection management; modules opened/closed connections ad-hoc, with no periodic PRAGMA optimize for long-running sessions.

## Decision

Establish `src/omega/infra/sqlite_policy.py` as the **single source of truth** for all SQLite connection configuration in the Omega Engine.

### Architecture

```
src/omega/infra/sqlite_policy.py    ← SSOT for PRAGMA stacks, profiles, connection factory
    │
    ├── src/omega/memory/archival.py     ← get_sqlite_connection(path, profile="memory")
    ├── src/omega/memory/block_store.py  ← get_sqlite_connection(path, profile="memory")
    ├── src/omega/memory/recall.py       ← get_sqlite_connection(path, profile="memory")
    └── src/omega/memory/sqlite_vec_adapter.py  ← (inherits via get_sqlite_connection)
```

### PRAGMA Profiles

| Profile | cache_size | wal_autocheckpoint | journal_size_limit | busy_timeout | Use Case |
|---------|-----------|-------------------|-------------------|-------------|----------|
| `memory` | 32MB | 10000 | 64MB | 30s | archival, block_store, recall (writers) |
| `search` | 64MB | 10000 | 64MB | 30s | search_persistence (high-concurrency) |
| `metrics` | 32MB | 10000 | 64MB | 10s | telemetry, lightweight writes |
| `reader` | 32MB | 0 | 64MB | 30s | read-only queries (never triggers checkpoint) |

### Key Decisions

| Decision | Rationale | Evidence |
|----------|-----------|----------|
| **journal_mode=WAL** | Concurrent readers + single writer; no read-lock blocking | SQLite WAL mode (2026 production standard) |
| **synchronous=NORMAL** | WAL guarantees durability on crash; NORMAL skips fsync on checkpoint | D-282 PRAGMA stack law |
| **cache_size=32MB** | Was 512MB (8× over-provisioned); 32MB matches 2026 production profiles | D-282, sqlite-vec-hnsw recommendations |
| **busy_timeout=30000** | 30s timeout prevents SQLITE_BUSY under write contention | D-282 |
| **wal_autocheckpoint=10000** | 10K pages (~40MB) before auto-checkpoint; prevents WAL file bloat | 2026 production hardening |
| **journal_size_limit=64MB** | Caps WAL file at 64MB (3× autocheckpoint threshold) | D-282 |
| **BEGIN IMMEDIATE** | Acquires write lock at transaction start; prevents silent read→write upgrade | SQLite WAL starvation prevention (2026) |
| **reader profile wal_autocheckpoint=0** | Readers never trigger checkpoints; prevents checkpoint contention | SQLite WAL architecture note (2026) |
| **PRAGMA optimize=0x10002** | Updates sqlite_stat1/stat4 for query planner; run before close or on timer | SQLite docs |

### Connection Factory

```python
# Single entry point for all SQLite connections
conn = get_sqlite_connection(
    path=Path("data/memory/omega_memory.db"),
    profile="memory",      # or "search", "metrics", "reader"
    readonly=False,
    timeout=30.0
)

# Convenience functions for common patterns
writer = get_writer_connection(path)    # profile="memory", readonly=False
reader = get_reader_connection(path)    # profile="reader", readonly=True

# Context manager for atomic transactions
with sqlite_transaction(path, profile="memory") as conn:
    conn.execute("INSERT INTO ...")
    # Auto-commits on success, rolls back on exception
```

## Consequences

### Positive
- **Single source of truth**: All PRAGMA decisions in one file; no more scattered `PRAGMA` statements
- **Profile-based tuning**: Different workloads get appropriate settings without code duplication
- **Contract tests**: `verify_pragmas()` enables CI validation of PRAGMA compliance
- **Checkpoint starvation prevention**: Reader profile (wal_autocheckpoint=0) + writer profile (10000) = predictable checkpoint behavior
- **Periodic optimize**: Background timer updates query planner stats for long-running sessions

### Negative
- **Migration cost**: 3 modules (archival, block_store, recall) needed updates to use `get_sqlite_connection()`
- **Profile selection**: Developers must choose correct profile; wrong profile = suboptimal performance

### Risks Mitigated
| Risk | Mitigation |
|------|------------|
| PRAGMA drift across modules | SSOT in sqlite_policy.py; contract tests verify |
| WAL checkpoint starvation | Reader profile wal_autocheckpoint=0; writer profile 10000 |
| Write lock starvation | BEGIN IMMEDIATE on all write transactions |
| Cache over-provisioning | 32MB (was 512MB); matches 2026 production standards |
| Connection leaks | Context manager pattern; optimize timer for long sessions |

---

## Future Considerations

| Item | Status | Notes |
|------|--------|-------|
| **page_size=16384** | Planned (post-Gate-Β) | ~1.7× faster vector lookups for 768D; requires VACUUM INTO migration |
| **WAL2** | Deferred | Not in stock SQLite; requires custom build |
| **Connection pooling** | Deferred | Single-writer model; pool only helps reads |
| **BEGIN CONCURRENT** | Deferred | SQLite 4.0 feature; not production-ready |

---

*⬡ OMEGA ⬡ P2 ⬡ memory ⬡ ADR-001 ⬡ Gate-Γ-criterion*
