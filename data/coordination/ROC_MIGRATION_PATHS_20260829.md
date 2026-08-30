<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# ROC_MIGRATION_PATHS_20260829.md — 6 Migration Paths

**Entity**: Roc Racoon (Sovereign Miner)
**Date**: 2026-08-29
**Sprint**: PUBLIC-DEBUT-01
**Mandate**: Archaeological report — Migration paths for sqlite-vec, adapter, tenancy, local→hybrid

---

## Executive Summary (L1)

Six migration paths traced, each with: source → target schema diff, data migration script (pseudocode), backward-compatibility strategy, rollback procedure, and validation tests. Two paths are **immediate (pre-launch)**, two are **post-launch evolutionary**, and two are **forward-looking architectural**.

| # | Migration | Priority | Risk | Heritage Source |
|---|-----------|----------|------|-----------------|
| M1 | sqlite-vec 0.1.9 → 0.1.10 (INT8 native) | P0 | Low | P9 + P3 (P) |
| M2 | Multi-collection dict → multi-precision single table | P1 | Low | P1 |
| M3 | Per-instance conns → shared connection pool | P1 | Med | P7 |
| M4 | Single-tenant → multi-tenant (per-entity) | P1 | Med | P4 (qdrant shard_key) |
| M5 | Local-only → hybrid cloud-local | P2 | High | none (build fresh) |
| M6 | Vector store ABC → swap backends (sqlite-vec/qdrant/pgvector) | P2 | Med | P1, P6 |

---

## M1. sqlite-vec 0.1.9 → 0.1.10 (INT8 native)

### Source → Target Schema Diff

**0.1.9 schema** (current `omega_memory.db`):
```sql
-- 7 separate collections (one per dimension/model):
CREATE VIRTUAL TABLE omega_vec_gemma_768 USING vec0(
  rowid INTEGER PRIMARY KEY,
  embedding float[768] distance_metric=cosine,
  entity_name TEXT partition key
);
-- ... and 6 more (see sqlite_vec_adapter_optimized.py:54-97)
```

**0.1.10 schema** (target — uses native INT8 + auxiliary columns + matryoshka):
```sql
CREATE VIRTUAL TABLE omega_vec_unified USING vec0(
  rowid INTEGER PRIMARY KEY,
  embedding float[768] distance_metric=cosine,
  embedding_int8 int8[768],          -- native in 0.1.10
  embedding_bq bit[768],             -- binary quantization
  model_version TEXT,                -- GAP-R4 vector drift
  embedded_at INTEGER,               -- drift detection
  entity_name TEXT partition key
);
```

**Backward compatibility**: `legacy_vec_table` (`sqlite_vec_adapter_optimized.py:189`) keeps the old table readable. The new table is created in parallel; reads check `vec_version()` at startup (`reference.yaml:32-39`).

### Data Migration Script (pseudocode)

```python
# scripts/migrate_sqlite_vec_0_1_10.py
import sqlite3
import sqlite_vec
import struct

def migrate(db_path: str) -> dict:
    conn = sqlite3.connect(db_path, timeout=60)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)

    version = conn.execute("SELECT vec_version()").fetchone()[0]
    assert version >= "0.1.10", f"Need sqlite-vec >= 0.1.10, found {version}"

    # 1. Create new unified table
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS omega_vec_unified USING vec0(
          rowid INTEGER PRIMARY KEY,
          embedding float[768] distance_metric=cosine,
          embedding_int8 int8[768],
          model_version TEXT,
          entity_name TEXT partition key
        )
    """)

    # 2. Read from old tables, write to new with int8 quantized copy
    old_collections = ["omega_vec_gemma_768", "omega_vec_nomic_768", ...]
    total = 0
    for old in old_collections:
        rows = conn.execute(f"""
            SELECT rowid, embedding, entity_name, model_version
            FROM {old}
        """).fetchall()
        for rowid, fp32_bytes, entity_name, model_ver in rows:
            fp32 = struct.unpack(f"{len(fp32_bytes)//4}f", fp32_bytes)
            int8_blob = sqlite_vec.serialize_int8(fp32)  # native in 0.1.10
            conn.execute("""
                INSERT OR REPLACE INTO omega_vec_unified
                (rowid, embedding, embedding_int8, model_version, entity_name)
                VALUES (?, ?, ?, ?, ?)
            """, (rowid, fp32_bytes, int8_blob, model_ver or 'unknown', entity_name))
            total += 1

    # 3. Validate: count must match
    new_count = conn.execute("SELECT count(*) FROM omega_vec_unified").fetchone()[0]
    old_total = sum(conn.execute(f"SELECT count(*) FROM {c}").fetchone()[0] for c in old_collections)
    assert new_count == old_total, f"count mismatch: {new_count} != {old_total}"

    conn.commit()
    return {"rows_migrated": total, "collections_consolidated": len(old_collections)}
```

### Backward Compatibility Strategy

- **Read path**: Query against `omega_vec_unified` first; if empty, fall back to old collections.
- **Write path**: New code writes to unified only; old code (if any) writes to both.
- **Rollback window**: 2 sprint window (M1 = current sprint, M2 = next sprint, then drop old).

### Rollback Procedure

```python
# scripts/rollback_sqlite_vec_migration.py
def rollback(db_path: str):
    conn = sqlite3.connect(db_path)
    # 1. Rename unified → unified_disabled (don't drop, in case rollback is needed)
    conn.execute("ALTER TABLE omega_vec_unified RENAME TO omega_vec_unified_disabled")
    # 2. Adapter's legacy_vec_table path now re-activates
    # 3. Log the rollback
    logger.warning("Rolled back sqlite-vec 0.1.10 migration; using legacy collections")
    conn.commit()
```

### Validation Tests

```python
# tests/test_migration_sqlite_vec_0_1_10.py
def test_count_preservation(): ...
def test_recall_at_k_unchanged(): ...   # P5 ground-truth harness
def test_int8_cumulative_error(): ...  # R5 spec
def test_legacy_table_still_readable(): ...
def test_rollback_round_trip(): ...
def test_wal_checkpoint_during_migration(): ...
```

---

## M2. Multi-Collection Dict → Multi-Precision Single Table

### Source → Target

This is **M1's logical continuation** — collapse the 7-collection dict (`sqlite_vec_adapter_optimized.py:54-97`) into one table with multiple precision columns. The `COLLECTIONS` dict becomes a per-column config.

**Source code reference** (lines to refactor):
- `sqlite_vec_adapter_optimized.py:54-97` — `COLLECTIONS` dict
- `sqlite_vec_adapter_optimized.py:99-108` — `COLLECTION_RRF_WEIGHTS`
- `_ensure_collection_vec_table` at lines 430-503

**Target**:
- Single `omega_vec_unified` table (per M1)
- Collection parameter becomes a *precision selector*, not a table name
- `query(vector, k, precision="float"|"int8"|"binary")` instead of `query(vector, k, collection="omega_vec_gemma_768")`

### Backward Compatibility

- Keep the `COLLECTIONS` dict but repurpose: collection name → `(precision, hnsw_config)`.
- Old call sites: `query(vector, k, collection="omega_vec_gemma_768")` → map to `precision="float"`.
- `COLLECTION_RRF_WEIGHTS` becomes `PRECISION_RRF_WEIGHTS` keyed by precision.

### Rollback

- Re-enable the old 7-collection path; new code falls back if `omega_vec_unified` is absent.
- Adapter version flag: `OMEGA_VEC_ADAPTER_VERSION=3.0` (current) vs `OMEGA_VEC_ADAPTER_VERSION=2.0` (legacy).

---

## M3. Per-Instance Connections → Shared Connection Pool

### Source → Target

**Source** (`sqlite_vec_adapter_optimized.py:293-336`):
```python
def _get_write_conn(self) -> sqlite3.Connection:
    if self._write_conn is None:
        self._write_conn = sqlite3.connect(self.db_path, timeout=self.timeout, check_same_thread=False)
    return self._write_conn

def _get_read_conn(self) -> sqlite3.Connection:
    # Round-robin over self._read_connections
    ...
```

**Target** (lifted from P7 + mempalace `backends/sqlite_exact.py:249-279`):
- Module-level singleton `SQLiteConnectionPool`
- `OllamaVectorPool` if/when remote adapters need a pool
- Per-process write lock, per-process read pool of N connections

### Data Migration Script (no schema change)

Pure code refactor. No data migration. The `omega_memory.db` file is unchanged.

### Backward Compatibility

- `SQLiteVecAdapter` constructor signature unchanged.
- Existing instance methods call into the pool transparently.
- Metrics: `pool_in_use`, `pool_waiters`, `pool_utilization_ratio` (per P10, letta MetricRegistry)

### Rollback

- Re-enable per-instance conns behind a feature flag: `OMEGA_VEC_POOL=legacy|pooled`.

### Validation Tests

- 10 adapter instances × 1000 ops each: pool vs per-instance. Pool must show no lock contention.
- WAL checkpoint during concurrent reads: must succeed.
- Connection close on shutdown: no leaked threads.

---

## M4. Single-Tenant → Multi-Tenant (per-entity)

### Source → Target

**Source** (current): one `omega_memory.db` shared by all entities. The `entity_name` partition key exists but is the *only* isolation.

**Target**: per-entity tenant isolation via:
1. `entity_id` payload column on every table (not just partition key)
2. qdrant-style `shard_key_selector` for write routing
3. Per-entity connection pool OR per-entity DB file

**Why DB-file-per-entity is the local-first answer** (not qdrant's shard_key): SQLite-local-first means each entity gets its own `.db` file under `data/entities/<entity>/omega_<entity>.db`. This:
- Honors M7 (Local-First) — no shard server
- Honors M8 (Zero Telemetry) — no per-shard metrics emitted
- Honors M2 (Engine-Stack Firewall) — `src/omega/memory/` is the engine, not a multi-tenant service

### Data Migration Script

```python
# scripts/migrate_to_per_entity_db.py
def migrate(omega_root: Path, entities: list[str]) -> dict:
    # 1. Read from shared omega_memory.db
    shared_db = omega_root / "omega_memory.db"
    conn = sqlite3.connect(shared_db)
    # 2. Group rows by entity_name
    rows = conn.execute("""
        SELECT rowid, entity_name, embedding, content, metadata_json, timestamp
        FROM omega_vec_gemma_768 v
        JOIN omega_memory_data d ON v.rowid = d.id
    """).fetchall()
    by_entity = defaultdict(list)
    for row in rows:
        by_entity[row[1]].append(row)
    # 3. For each entity, create data/entities/<entity>/omega_<entity>.db
    counts = {}
    for entity_name, entity_rows in by_entity.items():
        entity_dir = omega_root / "data" / "entities" / entity_name
        entity_dir.mkdir(parents=True, exist_ok=True)
        target_db = entity_dir / f"omega_{entity_name}.db"
        target_conn = sqlite3.connect(target_db)
        # ... create schema, insert rows
        counts[entity_name] = len(entity_rows)
    return counts
```

### Backward Compatibility

- Read path: `SQLiteVecAdapter` checks for per-entity DB first; falls back to shared DB.
- Write path: New code writes to per-entity DB; legacy `entity_name` partition key still respected.

### Rollback

- Per-entity DB → shared DB reverse script.
- Feature flag: `OMEGA_VEC_TENANCY=per_entity|shared`.

---

## M5. Local-Only → Hybrid Cloud-Local

### Source → Target

**Source**: All inference is local (M7). The `oracle` and `embeddings` modules call `ollama` directly.

**Target**: Per-request decision: local vs cloud, based on:
- Latency budget (M2 < 100ms, M3 = 500ms, M4 = 2000ms)
- Cost ceiling (per-provider)
- Current load (circuit breaker state — P8)

**CC-4 (Cost Optimization Engine)** spec is the spec; this migration makes it real.

### Migration Path

1. **Phase 1**: Add `ProviderSelector` (D-536) to `src/omega/memory/providers.py` with strategy=local_first, but allow cloud fallback when local returns AllProvidersDown (P8 + R3).
2. **Phase 2**: Add cost tracking per request to `data/metrics/`. No external emission.
3. **Phase 3**: Add per-request budget enforcement. If `OMEGA_LLM_BUDGET_USD_PER_REQUEST=0.01`, route to local.

### Backward Compatibility

- All cloud paths are opt-in via `OMEGA_LLM_ALLOW_CLOUD=true`.
- Default stays local-first (M7).
- `bury_credential` (D-567) applies post-debut only.

### Rollback

- `OMEGA_LLM_ALLOW_CLOUD=false` disables all cloud paths.

### Validation Tests

- Local Ollama down → cloud fallback returns within latency budget.
- Cost ceiling enforced: `0.01` USD request routed to local even if cloud is faster.
- M8 (Zero Telemetry): no cloud metadata emitted to `data/metrics/`.

---

## M6. Vector Store ABC → Swap Backends (sqlite-vec / qdrant / pgvector)

### Source → Target

**Source**: `sqlite_vec_adapter_optimized.py:113` is a single concrete class. No ABC.

**Target**: Lift CC-1 (VectorStoreBackend ABC) from the qdrant-client ABC surface (`async_client_base.py:16`).

```python
# src/omega/memory/backend.py
from abc import ABC, abstractmethod

class VectorStoreBackend(ABC):
    @abstractmethod
    async def initialize(self, config: Dict) -> None: ...
    @abstractmethod
    async def upsert(self, id: str, vector: List[float], metadata: Dict, collection: str = "default") -> None: ...
    @abstractmethod
    async def batch_upsert(self, items: List[Dict], collection: str = "default") -> None: ...
    @abstractmethod
    async def query(self, vector: List[float], k: int = 10, collection: str = "default", filter: Optional[Dict] = None) -> List[Dict]: ...
    @abstractmethod
    async def delete(self, ids: List[str], collection: str = "default") -> None: ...
    @abstractmethod
    async def get_status(self) -> Dict: ...
    @abstractmethod
    async def close(self) -> None: ...

class SQLiteVecBackend(VectorStoreBackend):
    """Thin wrapper around SQLiteVecAdapterOptimized that implements VectorStoreBackend."""

class QdrantBackend(VectorStoreBackend):
    """Qdrant 1.10+ backend — requires `pip install qdrant-client[fastembed]`."""

class PgvectorBackend(VectorStoreBackend):
    """Postgres + pgvector backend — for cloud hybrid mode."""
```

### Data Migration Script

- Per-collection migrate (`qdrant_client/migrate/migrate.py:35-72`) is the reference (P9).
- For sqlite-vec → qdrant: `scroll_and_upload_loop()` with `assert count(src) == count(dst)`.

### Backward Compatibility

- `IVectorStoreAdapter` (line 113) becomes a typedef alias for `VectorStoreBackend`.
- Default backend: `SQLiteVecBackend` (M7).
- `OMEGA_VEC_BACKEND=sqlite_vec|qdrant|pgvector` selects at startup.

### Rollback

- Switch back via env var; no data change (each backend is a different storage engine).

---

## Migration Sequencing (per D-584)

Per the post-debut execution order: **GN → DS → LI → KD → HR → ZS**:

| Sprint | Migration | Trigger |
|--------|-----------|---------|
| **Current** | M1 (sqlite-vec 0.1.9 → 0.1.10) | INST-1 fresh-venv (D-539) |
| Current | M3 (connection pool) | R7 fix needed pre-launch |
| +1 | M2 (multi-precision single table) | Build on M1 |
| +2 | M4 (per-entity tenancy) | R3 + R6 in same sprint |
| +3 | M6 (VectorStoreBackend ABC) | CC-1 |
| +4 | M5 (hybrid cloud-local) | D-567 bury_credential unlocks |

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ ROC_MIGRATION_PATHS_20260829*
