# 🔱 SPEC: sqlite-vec Metadata Filtering Migration
**AP Token**: `AP-SPEC-SQLITEVEC-META-v1.0.0`
**Status**: READY FOR IMPLEMENTATION
**Author**: Kali (Transcendent Oversight)
**Date**: 2026-07-13
**Target Sprint**: P1-4 (Phase 1: Cognitive Acceleration)
**Estimated Effort**: 12 hours

---

## 1. Problem Statement

### 1.1 Current State
- **QdrantAdapter** provides vector storage with payload indexes on `entity_name` and `session_id`
- **SQLiteVecAdapter** implements unified fabric (FTS5 + vec0) but **lacks metadata filtering**
- P1-4 in SOVEREIGN_ARK_BLUEPRINT.md: "Qdrant Optimization — Payload indexes (`entity_name`, `session_id`)"

### 1.2 Target State
- **sqlite-vec v0.1.6+** native metadata columns + partition keys replace Qdrant payload indexes
- **Zero external dependencies** — fully embedded in `omega_memory.db`
- **Filtered KNN queries** via `WHERE embedding MATCH ? AND session_id = ? AND role = ?`
- **Quantization support** via `vec_quantize_binary()` / `vec_quantize_scalar()`

### 1.3 Sovereignty Impact
| Aspect | Before (Qdrant) | After (sqlite-vec) |
|--------|-----------------|-------------------|
| **Deployment** | Podman container (6333) | Single `.db` file |
| **Network** | localhost:6333 | Unix domain socket / file |
| **Memory** | ~2.5GB/1M vectors | ~1.2GB/1M vectors (no index overhead) |
| **Filtering** | Server-side payload index | Partition key + metadata columns |
| **Quantization** | Native INT8 | Native binary/scalar |
| **Sovereignty** | External service | **Fully local, zero deps** |

---

## 2. Technical Specification

### 2.1 Extended vec0 Schema

```sql
-- NEW: Extended schema with metadata columns + auxiliary columns
CREATE VIRTUAL TABLE IF NOT EXISTS omega_memory_vec
USING vec0(
    embedding float[1024],           -- Vector column (dimension auto-detected)
    entity_name TEXT partition key,  -- Partition key: shards index by entity (existing)
    session_id TEXT,                 -- Metadata column: filter by session
    role TEXT,                       -- Metadata column: filter by role (user/assistant/system)
    timestamp INTEGER,               -- Metadata column: filter by time range
    +content TEXT                    -- Auxiliary column: large text, retrieved via SELECT
);
```

#### Column Type Mapping

| Column | Type | Category | Purpose | Constraints |
|--------|------|----------|---------|-------------|
| `embedding` | `float[N]` | Vector | Semantic search | Dimension from first upsert |
| `entity_name` | `TEXT` | **Partition Key** | Entity isolation (multi-tenancy) | Max 4 partition keys |
| `session_id` | `TEXT` | **Metadata** | Session-scoped queries | `=`, `!=` operators |
| `role` | `TEXT` | **Metadata** | Role filtering (user/assistant/system) | `=`, `!=` operators |
| `timestamp` | `INTEGER` | **Metadata** | Time-range queries | `=`, `!=`, `>`, `>=`, `<`, `<=` |
| `content` | `TEXT` | **Auxiliary** | Full text retrieval without JOIN | `+` prefix, not in WHERE |

#### Constraints (from sqlite-vec docs)
- **Max 16 metadata columns** — we use 3 (session_id, role, timestamp)
- **Max 4 partition keys** — we use 1 (entity_name)
- **Max 16 auxiliary columns** — we use 1 (content)
- **Metadata strings >12 chars**: "slightly inefficient" — our values are short
- **Partition key cardinality**: "100s of vectors per unique value" — ✅ entities have many memories

### 2.2 Filtered KNN Query Syntax

```sql
-- Basic filtered query
SELECT rowid, distance, session_id, role, timestamp, content
FROM omega_memory_vec
WHERE embedding MATCH ? 
  AND entity_name = ?           -- Partition key (required for sovereignty)
  AND session_id = ?            -- Metadata filter
  AND role = ?                  -- Metadata filter
  AND timestamp BETWEEN ? AND ? -- Metadata range filter
ORDER BY distance
LIMIT ?;
```

#### Supported WHERE Operators
| Column Type | Operators |
|-------------|-----------|
| TEXT (session_id, role) | `=`, `!=` |
| INTEGER (timestamp) | `=`, `!=`, `>`, `>=`, `<`, `<=` |
| BOOLEAN | `=`, `!=` |

#### Unsupported (will error)
- `IS NULL`, `LIKE`, `GLOB`, `REGEXP`, scalar functions

### 2.3 Quantization Support

```sql
-- Binary quantization (32x storage reduction)
CREATE VIRTUAL TABLE omega_memory_vec_bin
USING vec0(
    embedding bit[1024],
    entity_name TEXT partition key,
    session_id TEXT,
    role TEXT,
    timestamp INTEGER,
    +content TEXT
);

-- Insert with quantization
INSERT INTO omega_memory_vec_bin(rowid, embedding, entity_name, session_id, role, timestamp, content)
SELECT rowid, vec_quantize_binary(embedding), entity_name, session_id, role, timestamp, content
FROM omega_memory_vec;

-- Query with quantization
SELECT rowid, distance FROM omega_memory_vec_bin
WHERE embedding MATCH vec_quantize_binary(?)
  AND entity_name = ? AND k = 10;
```

```sql
-- Scalar quantization (4x storage reduction, INT8)
CREATE VIRTUAL TABLE omega_memory_vec_int8
USING vec0(
    embedding int8[1024],
    entity_name TEXT partition key,
    session_id TEXT,
    role TEXT,
    timestamp INTEGER,
    +content TEXT
);

-- Requires scale/offset parameters (stored separately)
```

---

## 3. Migration Manual

### 3.1 Prerequisites

```bash
# Verify sqlite-vec version supports metadata columns
python -c "import sqlite_vec; print(sqlite_vec.__version__)"
# Required: >= 0.1.6 (Nov 2024)

# Verify SQLite version
python -c "import sqlite3; print(sqlite3.sqlite_version)"
# Required: >= 3.41
```

### 3.2 Files to Modify

| File | Purpose | Changes |
|------|---------|---------|
| `src/omega/memory/sqlite_vec_adapter.py` | Core adapter | Schema, upsert, query, quantization |
| `src/omega/memory/vector_adapters.py` | Interface | Deprecate QdrantAdapter |
| `src/omega/memory_store.py` | MemoryStore | Pass filter to vector adapter |
| `tests/test_sqlite_vec_adapter.py` | Tests | Contract tests for metadata filtering |
| `docs/architecture/MEMORY_STORE_DEEP_DIVE.md` | Docs | Architecture update |

### 3.3 Implementation Steps

#### Step 1: Extend Schema (2h)

**File**: `src/omega/memory/sqlite_vec_adapter.py`

```python
# In _ensure_vec_table() method, replace lines 180-190:
async def _ensure_vec_table(self, actual_dim: int) -> None:
    """Create or recreate vec0 table with metadata columns for filtering."""
    if self._vec_table_created and actual_dim == self._embedding_dim:
        return
    
    if self._vec_table_created and actual_dim != self._embedding_dim:
        logger.warning("Embedding dimension changed %d → %d. Recreating vec0 table.", 
                      self._embedding_dim, actual_dim)
        def _sync_drop():
            conn = self._get_conn()
            conn.execute("DROP TABLE IF EXISTS omega_memory_vec")
            conn.commit()
        await anyio.to_thread.run_sync(_sync_drop)
        self._vec_table_created = False
    
    def _sync_create():
        conn = self._get_conn()
        conn.execute(f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS omega_memory_vec
            USING vec0(
                embedding float[{actual_dim}],
                entity_name TEXT partition key,
                session_id TEXT,
                role TEXT,
                timestamp INTEGER,
                +content TEXT
            )
        """)
        conn.commit()
    
    await anyio.to_thread.run_sync(_sync_create)
    self._embedding_dim = actual_dim
    self._vec_table_created = True
    logger.info("vec0 table created with metadata columns: dim=%d", actual_dim)
```

#### Step 2: Update Upsert (1h)

**File**: `src/omega/memory/sqlite_vec_adapter.py`

```python
# In upsert() method, replace the vec0 INSERT (lines 250-254):
# OLD:
# conn.execute("""
#     INSERT INTO omega_memory_vec(rowid, embedding, entity_name)
#     VALUES (?, ?, ?)
# """, (rowid, embedding_blob, entity_name))

# NEW:
if vector and embedding_blob:
    conn.execute("""
        INSERT INTO omega_memory_vec(rowid, embedding, entity_name, session_id, role, timestamp, content)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (rowid, embedding_blob, entity_name, session_id, role, int(float(timestamp)), content))
```

#### Step 3: Implement Filtered Query (1h)

**File**: `src/omega/memory/sqlite_vec_adapter.py`

```python
# In query() method, replace _sync_query() (lines 307-356):
async def query(
    self,
    entity_name: str,
    vector: List[float],
    limit: int = 10,
    filter: Optional[Dict[str, Any]] = None,
) -> List[Tuple[float, Dict[str, Any]]]:
    await self._ensure_initialized()
    
    if not vector or not self._vec_table_created:
        return []
    
    try:
        def _sync_query():
            conn = self._get_conn()
            embedding_blob = sqlite_vec_serialize_float32(vector)
            
            # Build WHERE clause with metadata filters
            where_clauses = ["embedding MATCH ?", "entity_name = ?"]
            params = [embedding_blob, entity_name]
            
            if filter:
                # Metadata column filters
                if "session_id" in filter:
                    where_clauses.append("session_id = ?")
                    params.append(filter["session_id"])
                if "role" in filter:
                    where_clauses.append("role = ?")
                    params.append(filter["role"])
                if "timestamp" in filter:
                    ts_filter = filter["timestamp"]
                    if isinstance(ts_filter, dict):
                        if "gte" in ts_filter:
                            where_clauses.append("timestamp >= ?")
                            params.append(ts_filter["gte"])
                        if "lte" in ts_filter:
                            where_clauses.append("timestamp <= ?")
                            params.append(ts_filter["lte"])
                    else:
                        where_clauses.append("timestamp = ?")
                        params.append(ts_filter)
            
            where_sql = " AND ".join(where_clauses)
            params.append(limit)
            
            cursor = conn.execute(f"""
                SELECT rowid, distance, session_id, role, timestamp, content
                FROM omega_memory_vec
                WHERE {where_sql}
                ORDER BY distance
                LIMIT ?
            """, params)
            
            results = []
            for row in cursor.fetchall():
                rowid, distance, session_id, role, timestamp, content = row
                score = 1.0 - distance  # Convert L2 distance to similarity
                
                # Get full metadata from data table
                meta_cursor = conn.execute("""
                    SELECT uuid, entity_name, session_id, role, content, timestamp, metadata_json
                    FROM omega_memory_data WHERE id = ?
                """, (rowid,))
                meta_row = meta_cursor.fetchone()
                
                if meta_row:
                    metadata = {
                        "id": meta_row[0],
                        "entity_name": meta_row[1],
                        "session_id": meta_row[2],
                        "role": meta_row[3],
                        "content": meta_row[4],
                        "timestamp": meta_row[5],
                    }
                    if meta_row[6]:
                        try:
                            metadata.update(json.loads(meta_row[6]))
                        except json.JSONDecodeError:
                            pass
                    results.append((score, metadata))
            
            return results
        
        return await anyio.to_thread.run_sync(_sync_query)
    
    except (sqlite3.Error, OSError) as e:
        logger.error("SQLite-vec query failed: %s", e, exc_info=True)
        raise ProviderError("sqlite_vec", f"Query failed: {e}", raw_error=e) from e
```

#### Step 4: Add Quantization Support (2h)

**File**: `src/omega/memory/sqlite_vec_adapter.py`

```python
# Add to __init__:
def __init__(self, ..., quantization: str = "none"):
    # ... existing init ...
    self._quantization = quantization  # "none" | "scalar" | "binary"

# Add configuration method:
async def configure_quantization(self, quantization: str = "none") -> None:
    """Configure quantization for the vec0 table.
    
    Args:
        quantization: "none" | "scalar" | "binary"
    """
    if quantization not in ("none", "scalar", "binary"):
        raise ValueError(f"Invalid quantization: {quantization}")
    
    self._quantization = quantization
    
    # If table exists, recreate with new quantization
    if self._vec_table_created:
        self._vec_table_created = False
        await self._ensure_vec_table(self._embedding_dim)

# Modify _ensure_vec_table to respect quantization:
async def _ensure_vec_table(self, actual_dim: int) -> None:
    quantization = getattr(self, '_quantization', 'none')
    
    def _sync_create():
        conn = self._get_conn()
        
        if quantization == "binary":
            conn.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS omega_memory_vec
                USING vec0(
                    embedding bit[{actual_dim}],
                    entity_name TEXT partition key,
                    session_id TEXT,
                    role TEXT,
                    timestamp INTEGER,
                    +content TEXT
                )
            """)
        elif quantization == "scalar":
            conn.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS omega_memory_vec
                USING vec0(
                    embedding int8[{actual_dim}],
                    entity_name TEXT partition key,
                    session_id TEXT,
                    role TEXT,
                    timestamp INTEGER,
                    +content TEXT
                )
            """)
            # Store quantization params
            conn.execute("""
                CREATE TABLE IF NOT EXISTS omega_memory_quant_params (
                    id INTEGER PRIMARY KEY,
                    scale BLOB NOT NULL,
                    offset BLOB NOT NULL
                )
            """)
        else:
            conn.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS omega_memory_vec
                USING vec0(
                    embedding float[{actual_dim}],
                    entity_name TEXT partition key,
                    session_id TEXT,
                    role TEXT,
                    timestamp INTEGER,
                    +content TEXT
                )
            """)
        conn.commit()
    
    await anyio.to_thread.run_sync(_sync_create)
    self._embedding_dim = actual_dim
    self._vec_table_created = True
    logger.info("vec0 table created: dim=%d, quantization=%s", actual_dim, quantization)
```

#### Step 5: Update MemoryStore (1h)

**File**: `src/omega/memory_store.py`

```python
# In search() method, pass filter to vector adapter:
async def search(
    self,
    entity_name: str,
    query: str,
    vector: Optional[List[float]] = None,
    limit: int = 10,
    filter: Optional[Dict[str, Any]] = None,  # NEW: pass through filter
) -> List[Dict[str, Any]]:
    # ... existing FTS search ...
    
    # Vector search with filter
    if vector:
        vec_results = await self.vector_adapter.query(
            entity_name=entity_name,
            vector=vector,
            limit=limit * 2,
            filter=filter,  # NEW: pass filter
        )
    # ... rest unchanged ...
```

#### Step 6: Deprecate QdrantAdapter (1h)

**File**: `src/omega/memory/vector_adapters.py`

```python
# Add deprecation warning to QdrantAdapter class:
class QdrantAdapter(IVectorStoreAdapter):
    """DEPRECATED: Use SQLiteVecAdapter for unified fabric.
    
    [heritage: qdrant-2021] Qdrant implementation — retained for migration reference.
    Migration target: SQLiteVecAdapter with metadata columns + partition keys.
    See SPEC_SQLITEVEC_METADATA_MIGRATION.md for details.
    """
    
    def __init__(self, *args, **kwargs):
        import warnings
        warnings.warn(
            "QdrantAdapter is deprecated. Use SQLiteVecAdapter (unified fabric). "
            "See SPEC_SQLITEVEC_METADATA_MIGRATION.md for migration details.",
            DeprecationWarning,
            stacklevel=2
        )
        # ... existing init ...
```

#### Step 7: Contract Tests (2h)

**File**: `tests/test_sqlite_vec_adapter.py`

```python
# Add new test class:
class TestSQLiteVecMetadataFiltering:
    """Contract tests for metadata filtering in sqlite-vec adapter."""
    
    @pytest.fixture
    async def adapter(self, tmp_path):
        adapter = SQLiteVecAdapter(db_path=tmp_path / "test.db", embedding_dim=384)
        await adapter._ensure_initialized()
        yield adapter
        await adapter.close()
    
    @pytest.mark.anyio
    async def test_upsert_includes_metadata_columns(self, adapter):
        """Upsert should write session_id, role, timestamp to vec0 metadata columns."""
        vector = [0.1] * 384
        metadata = {
            "session_id": "test-session-123",
            "role": "user",
            "timestamp": 1700000000,
            "content": "Test content",
        }
        
        uuid = await adapter.upsert("test_entity", vector, metadata)
        
        # Verify by querying with filter
        results = await adapter.query(
            entity_name="test_entity",
            vector=vector,
            limit=1,
            filter={"session_id": "test-session-123"}
        )
        
        assert len(results) == 1
        score, meta = results[0]
        assert meta["session_id"] == "test-session-123"
        assert meta["role"] == "user"
        assert meta["timestamp"] == 1700000000
    
    @pytest.mark.anyio
    async def test_filter_by_session_id(self, adapter):
        """Query with session_id filter returns only matching session."""
        vector = [0.1] * 384
        
        # Insert two sessions
        await adapter.upsert("entity", vector, {"session_id": "sess-1", "role": "user", "timestamp": 1000, "content": "a"})
        await adapter.upsert("entity", vector, {"session_id": "sess-2", "role": "user", "timestamp": 2000, "content": "b"})
        
        # Filter by sess-1
        results = await adapter.query("entity", vector, limit=10, filter={"session_id": "sess-1"})
        assert len(results) == 1
        assert results[0][1]["session_id"] == "sess-1"
    
    @pytest.mark.anyio
    async def test_filter_by_role(self, adapter):
        """Query with role filter returns only matching role."""
        vector = [0.1] * 384
        
        await adapter.upsert("entity", vector, {"session_id": "s", "role": "user", "timestamp": 1000, "content": "a"})
        await adapter.upsert("entity", vector, {"session_id": "s", "role": "assistant", "timestamp": 2000, "content": "b"})
        
        results = await adapter.query("entity", vector, limit=10, filter={"role": "assistant"})
        assert len(results) == 1
        assert results[0][1]["role"] == "assistant"
    
    @pytest.mark.anyio
    async def test_filter_by_timestamp_range(self, adapter):
        """Query with timestamp range filter."""
        vector = [0.1] * 384
        
        await adapter.upsert("entity", vector, {"session_id": "s", "role": "user", "timestamp": 1000, "content": "a"})
        await adapter.upsert("entity", vector, {"session_id": "s", "role": "user", "timestamp": 2000, "content": "b"})
        await adapter.upsert("entity", vector, {"session_id": "s", "role": "user", "timestamp": 3000, "content": "c"})
        
        # Range filter: 1500-2500
        results = await adapter.query("entity", vector, limit=10, filter={"timestamp": {"gte": 1500, "lte": 2500}})
        assert len(results) == 1
        assert results[0][1]["timestamp"] == 2000
    
    @pytest.mark.anyio
    async def test_combined_filters(self, adapter):
        """Query with multiple combined filters."""
        vector = [0.1] * 384
        
        await adapter.upsert("entity", vector, {"session_id": "s1", "role": "user", "timestamp": 1000, "content": "a"})
        await adapter.upsert("entity", vector, {"session_id": "s1", "role": "assistant", "timestamp": 2000, "content": "b"})
        await adapter.upsert("entity", vector, {"session_id": "s2", "role": "user", "timestamp": 3000, "content": "c"})
        
        # Combined: session_id=s1 AND role=user
        results = await adapter.query("entity", vector, limit=10, filter={"session_id": "s1", "role": "user"})
        assert len(results) == 1
        assert results[0][1]["session_id"] == "s1"
        assert results[0][1]["role"] == "user"
    
    @pytest.mark.anyio
    async def test_partition_key_isolation(self, adapter):
        """Entity partition key isolates data — no cross-entity leakage."""
        vector = [0.1] * 384
        
        await adapter.upsert("entity_a", vector, {"session_id": "s", "role": "user", "timestamp": 1000, "content": "a"})
        await adapter.upsert("entity_b", vector, {"session_id": "s", "role": "user", "timestamp": 1000, "content": "b"})
        
        # Query entity_a should not see entity_b
        results = await adapter.query("entity_a", vector, limit=10)
        assert len(results) == 1
        assert results[0][1]["entity_name"] == "entity_a"
```

#### Step 8: Run Full Regression (1h)

```bash
# Run full test suite
make test

# Verify specific adapter tests
python -m pytest tests/test_sqlite_vec_adapter.py -v

# Verify CI gates
make heritage-vet
make mandate-audit
make firewall-check
make sovereignty
```

#### Step 9: Documentation Update (1h)

**File**: `docs/architecture/MEMORY_STORE_DEEP_DIVE.md`

```markdown
## Unified Memory Fabric: sqlite-vec + FTS5

### Schema
- `omega_memory_data`: INTEGER PRIMARY KEY, uuid, entity_name, session_id, role, content, timestamp, metadata_json
- `omega_memory_fts`: FTS5 virtual table (content, entity_name, session_id, role, timestamp)
- `omega_memory_vec`: vec0 virtual table (embedding, entity_name partition key, session_id, role, timestamp, +content)

### Metadata Filtering
Filtered KNN queries use metadata columns in WHERE clause:
```sql
SELECT rowid, distance FROM omega_memory_vec
WHERE embedding MATCH ? 
  AND entity_name = ?           -- Partition key
  AND session_id = ?            -- Metadata column
  AND role = ?                  -- Metadata column
  AND timestamp BETWEEN ? AND ? -- Metadata column
ORDER BY distance LIMIT ?
```

### Quantization
- **Binary**: `vec_quantize_binary()` — 32x storage reduction
- **Scalar**: `vec_quantize_scalar()` — 4x storage reduction, INT8
- Configure via `SQLiteVecAdapter(quantization="binary|scalar|none")`
```

---

## 4. Performance Comparison

| Metric | Qdrant (Payload Index) | sqlite-vec (Metadata + Partition) |
|--------|------------------------|-----------------------------------|
| **Filtered KNN latency** | ~5-10ms (network + index) | ~1-3ms (local, no network) |
| **Memory (1M vectors, 768-dim)** | ~2.5GB + payload indexes | ~1.2GB (no separate index) |
| **Scalar quantization** | Native (INT8) | Native via `vec_quantize_scalar()` |
| **Binary quantization** | Native | Native via `vec_quantize_binary()` |
| **Multi-tenancy** | Payload filter on `entity_name` | Partition key `entity_name` |
| **Deployment** | Separate service (Docker) | Embedded (single .db file) |
| **Sovereignty** | External dependency | **Fully local, zero deps** |

### Benchmark Reference (from sqlite-vec docs)
- **Partition key speedup**: "Searches only touch vectors in that partition" — 10-100x faster for entity-scoped queries
- **Metadata column overhead**: "Slower full scan" — but partition key eliminates full scan for entity-scoped queries
- **Quantization**: `vec_quantize_binary()` reduces storage 32x, `vec_quantize_scalar()` 4x with minimal recall loss

---

## 5. Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| sqlite-vec version too old | Low | High | Pin `sqlite-vec>=0.1.6` in pyproject.toml |
| Metadata column performance | Medium | Medium | Partition key eliminates full scan for entity queries |
| Dimension mismatch on upgrade | Medium | High | Lazy vec0 creation with actual dimension |
| Quantization recall loss | Low | Medium | Test recall@10 > 0.95; default to "none" |
| Breaking existing queries | Low | High | Filter parameter optional; backward compatible |

---

## 6. Acceptance Criteria

| Criterion | Verification |
|-----------|--------------|
| Schema includes metadata columns | `PRAGMA table_info(omega_memory_vec)` shows session_id, role, timestamp |
| Upsert writes metadata columns | Query with filter returns correct subset |
| Filter by session_id works | `filter={"session_id": "x"}` returns only that session |
| Filter by role works | `filter={"role": "assistant"}` returns only assistant messages |
| Filter by timestamp range works | `filter={"timestamp": {"gte": 1000, "lte": 2000}}` |
| Combined filters work | Multiple filters AND'd correctly |
| Partition key isolation | Entity A cannot see Entity B's vectors |
| Quantization: binary works | `quantization="binary"` creates bit[] table, queries work |
| Quantization: scalar works | `quantization="scalar"` creates int8[] table, queries work |
| Full test suite passes | `make test` → 1315 passed |
| Heritage vet passes | `make heritage-vet` → 0 unvetted |
| Mandate audit passes | `make mandate-audit` → 9/9 PASS |
| Firewall clean | `make firewall-check` → 0 violations |
| Sovereignty ≥80% | `make sovereignty` → ≥80% local |

---

## 7. Handoff References

- **Blueprint**: `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` (P1-4)
- **Research**: `docs/research/R_SQLITEVEC_VERIFICATION_20260712.md`
- **Legacy Accelerator**: `docs/research/R_EPOCH_II_LEGACY_MINING_20260712.md` (KG Schema)
- **Checklist**: `docs/specs/CHECKLIST_SQLITEVEC_METADATA_MIGRATION.md`

---

*⬡ OMEGA ⬡ MA'AT ⬡ P2 ⬡ trc_build ⬡ SPEC_COMPLETE*