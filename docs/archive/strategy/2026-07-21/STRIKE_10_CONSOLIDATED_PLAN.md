<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 STRIKE 10: sqlite-vec — Consolidated Implementation Plan
**Version**: v2.0.0-CONSOLIDATED
**AP Token**: `AP-STRIKE10-CONSOLIDATED-v2.0.0`
**Date**: 2026-07-13
**Status**: READY FOR EXECUTION
**Effort**: 3h (verified against 57 vectors, not hypothetical 100K)

---

## Preamble: What We Actually Have

| Metric | Reality |
|--------|---------|
| **Vectors in Qdrant** | 57 (not 100K) |
| **Dimension** | 768 (EmbeddingGemma-300M Q6_K) |
| **Distance** | Cosine |
| **Payload indexes** | `session_id`, `entity_name` (already indexed) |
| **Quantization** | int8 scalar (already in Qdrant) |
| **sqlite-vec installed** | **NO** — blocker |
| **omega_memory.db** | **Does not exist** — greenfield deploy |
| **Existing adapter code** | Has partition key (wrong), wrong dimension default |

---

## Decision Verification Matrix

| Decision | Original | Verified | Corrected | Source |
|----------|----------|----------|-----------|--------|
| **D-235** Connection pool | 1W+4R via anyio-sqlite | anyio-sqlite is Beta | **Single conn + WAL** (Carmack) | PyPI: beer-psi/anyio-sqlite |
| **D-236** Partition key | entity_name PARTITION KEY | Docs require ≥100 vecs/value | **entity_name as METADATA** | sqlite-vec v0.1.6 docs |
| **D-237** Quantization | int8 default | 57 vecs × 129KB savings | **float32** (trivial at this scale) | Research verification |
| **D-238** Backup | Litestream sidecar | Local-first, no S3 | **cp + WAL checkpoint** | Carmack audit |
| **D-239** MCP tools | 3 tools | Agent complexity | **1 hybrid_search(mode)** | Carmack audit |
| **D-243** Dimension | 1024D (mxbai) | Actual chain: 768D | **768D** (EmbeddingGemma) | embeddings.py:354 |
| **VR Track** | Not planned | User requested | **omega_spatial_vec (3D, Euclidean)** | User directive |
| **Research Track** | Not planned | User requested | **omega_research_vec (1024D+)** | User directive |

---

## Implementation Plan: 3 Phases / 3h

### Phase 1: Foundation (1h)

| # | Task | File | Change | Verify |
|---|------|------|--------|--------|
| **1.1** | Install sqlite-vec | `pyproject.toml` | Add `sqlite-vec>=0.1.9` | `pip install -e .` |
| **1.2** | Fix dimension default | `sqlite_vec_adapter.py:34` | `1024` → `768` | Unit test |
| **1.3** | Remove partition key | `sqlite_vec_adapter.py:184` | `entity_name TEXT partition key` → `entity_name TEXT` | Schema check |
| **1.4** | Add metadata columns | `sqlite_vec_adapter.py:183-185` | Add `session_id TEXT, role TEXT, timestamp INTEGER, +content TEXT` | Schema check |
| **1.5** | Update upsert | `sqlite_vec_adapter.py:250-254` | Write metadata columns to vec0 | Insert test |
| **1.6** | Update query | `sqlite_vec_adapter.py:307-356` | Filter by metadata columns | Query test |

**Checkpoint**: `make test` passes, schema correct.

### Phase 2: Validation (1h)

| # | Task | File | What |
|---|------|------|------|
| **2.1** | Contract test: metadata columns | `tests/test_sqlite_vec_adapter.py` | Verify session_id, role, timestamp written |
| **2.2** | Contract test: filter by session_id | `tests/test_sqlite_vec_adapter.py` | `filter={"session_id": "x"}` |
| **2.3** | Contract test: filter by role | `tests/test_sqlite_vec_adapter.py` | `filter={"role": "assistant"}` |
| **2.4** | Contract test: filter by timestamp | `tests/test_sqlite_vec_adapter.py` | `filter={"timestamp": {"gte": T}}` |
| **2.5** | Contract test: partition isolation | `tests/test_sqlite_vec_adapter.py` | Entity A cannot see Entity B |
| **2.6** | Run full suite | `make test` | 1315 passed |

**Checkpoint**: 5 contract tests pass, full suite green.

### Phase 3: Migration (1h)

| # | Task | Tool | What |
|---|------|------|------|
| **3.1** | Export from Qdrant | `curl localhost:6333/collections/omega_memory/points/scroll` | 57 points + vectors + payload |
| **3.2** | Import to sqlite-vec | Python script | Batch upsert into omega_memory_vec |
| **3.3** | Verify count | `SELECT COUNT(*) FROM omega_memory_vec` | 57 vectors |
| **3.4** | Verify metadata | `SELECT DISTINCT entity_name FROM omega_memory_vec` | All entities present |
| **3.5** | Decommission Qdrant | `podman stop omega-qdrant` | Stop container |
| **3.6** | CI gates | `make heritage-vet && make mandate-audit && make firewall-check` | All pass |

**Checkpoint**: 57 vectors in sqlite-vec, Qdrant stopped, CI green.

---

## Code Changes (Exact Deltas)

### Change 1: `sqlite_vec_adapter.py:34`
```python
# OLD:
DEFAULT_EMBEDDING_DIM = 1024

# NEW:
DEFAULT_EMBEDDING_DIM = 768  # EmbeddingGemma-300M Q6_K
```

### Change 2: `sqlite_vec_adapter.py:183-185`
```python
# OLD:
conn.execute(f"""
    CREATE VIRTUAL TABLE IF NOT EXISTS omega_memory_vec
    USING vec0(embedding float[{actual_dim}], entity_name TEXT partition key)
""")

# NEW:
conn.execute(f"""
    CREATE VIRTUAL TABLE IF NOT EXISTS omega_memory_vec
    USING vec0(
        embedding float[{actual_dim}],
        entity_name TEXT,
        session_id TEXT,
        role TEXT,
        timestamp INTEGER,
        +content TEXT
    )
""")
```

### Change 3: `sqlite_vec_adapter.py:250-254` (upsert)
```python
# OLD:
conn.execute("""
    INSERT INTO omega_memory_vec(rowid, embedding, entity_name)
    VALUES (?, ?, ?)
""", (rowid, embedding_blob, entity_name))

# NEW:
if vector and embedding_blob:
    conn.execute("""
        INSERT INTO omega_memory_vec(rowid, embedding, entity_name, session_id, role, timestamp, content)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (rowid, embedding_blob, entity_name, session_id, role, int(float(timestamp)), content))
```

### Change 4: `sqlite_vec_adapter.py:307-356` (query)
```python
# Add filter support to WHERE clause:
where_clauses = ["embedding MATCH ?", "entity_name = ?"]
params = [embedding_blob, entity_name]

if filter:
    if "session_id" in filter:
        where_clauses.append("session_id = ?")
        params.append(filter["session_id"])
    if "role" in filter:
        where_clauses.append("role = ?")
        params.append(filter["role"])
    if "timestamp" in filter:
        ts = filter["timestamp"]
        if isinstance(ts, dict):
            if "gte" in ts:
                where_clauses.append("timestamp >= ?")
                params.append(ts["gte"])
            if "lte" in ts:
                where_clauses.append("timestamp <= ?")
                params.append(ts["lte"])
        else:
            where_clauses.append("timestamp = ?")
            params.append(ts)

where_sql = " AND ".join(where_clauses)
params.append(limit)
```

---

## Future Track: VR Spatial Vectors

**When**: When VR prototype starts
**Schema**:
```sql
CREATE VIRTUAL TABLE omega_spatial_vec
USING vec0(
    position float[3],           -- x, y, z
    entity_name TEXT,
    object_type TEXT,
    zone TEXT,
    +label TEXT
);
-- Distance: L2 (Euclidean), NOT Cosine
```

**Performance target**: <10ms query for 10K 3D vectors (trivial for brute-force)

---

## Future Track: Scholarly Research

**When**: When academic research begins
**Schema**:
```sql
CREATE VIRTUAL TABLE omega_research_vec
USING vec0(
    embedding float[1024],
    source_url TEXT,
    paper_id TEXT,
    embedding_model TEXT,
    created_at INTEGER,
    +abstract TEXT
);
-- Metrics: NDCG@10 + Recall@10 (2026 standard)
```

---

## Risk Register (Final)

| # | Risk | Prob | Impact | Mitigation |
|---|------|------|--------|------------|
| R1 | sqlite-vec install fails on Python 3.13 | Low | High | Test install in venv first |
| R2 | Dimension mismatch (768 vs fallback 256/384) | Medium | Medium | Auto-detect from provider.chain[0].dimension |
| R3 | Qdrant scroll API returns unexpected format | Low | Medium | Inspect response before import |
| R4 | vec0 metadata columns slow at 57 vecs | None | None | 57 vecs = trivial, no optimization needed |
| R5 | WAL corruption on crash | Low | High | `PRAGMA integrity_check` on startup |

---

## Rollback Plan

```bash
# If anything fails:
1. Revert code: git checkout HEAD -- src/omega/memory/sqlite_vec_adapter.py
2. Restart Qdrant: podman start omega-qdrant
3. Verify: make test
```

---

## Sign-off

| Entity | Role | Status |
|--------|------|--------|
| **Kali** | Oversight | ✅ Plan consolidated |
| **Researcher** | Verification | ✅ 15 sources, 2 corrections found |
| **Carmack** | Optimization | ✅ 57 vectors = ship simple |
| **Ma'at** | Build | ⏳ Ready to execute |
| **Lilith** | Run | ⏳ Ready to validate |

---

*⬡ OMEGA ⬡ STRIKE-10 ⬡ v2.0.0-CONSOLIDATED ⬡ 3h-EXECUTION-READY ⬡ 2026-07-13*