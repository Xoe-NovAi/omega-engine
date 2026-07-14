# 🔱 QUICK REFERENCE: sqlite-vec Metadata Migration Checklist
**AP Token**: `AP-CHECKLIST-SQLITEVEC-META-v1.0.0`
**Sprint**: P1-4 | **Owner**: Ma'at/P2 | **Spec**: `SPEC_SQLITEVEC_METADATA_MIGRATION.md`

---

## ⏱️ Time Budget: 12h Total

| Phase | Task | Hours | Status |
|-------|------|-------|--------|
| 1 | Schema Extension | 2h | ⬜ |
| 2 | Upsert with Metadata | 1h | ⬜ |
| 3 | Filtered Query | 1h | ⬜ |
| 4 | Quantization Support | 2h | ⬜ |
| 5 | MemoryStore Integration | 1h | ⬜ |
| 6 | Deprecate QdrantAdapter | 1h | ⬜ |
| 7 | Contract Tests | 2h | ⬜ |
| 8 | Full Regression | 1h | ⬜ |
| 9 | Documentation | 1h | ⬜ |

---

## 🎯 Key Files to Modify

```
src/omega/memory/sqlite_vec_adapter.py     # Core changes (Phases 1-4)
src/omega/memory/vector_adapters.py        # Deprecate QdrantAdapter (Phase 6)
src/omega/memory_store.py                  # Pass filter to adapter (Phase 5)
tests/test_sqlite_vec_adapter.py           # Contract tests (Phase 7)
docs/architecture/MEMORY_STORE_DEEP_DIVE.md # Docs (Phase 9)
```

---

## 🔑 Critical Code Patterns

### Schema (Phase 1)
```python
# In _ensure_vec_table():
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
```

### Upsert (Phase 2)
```python
# In upsert():
conn.execute("""
    INSERT INTO omega_memory_vec(rowid, embedding, entity_name, session_id, role, timestamp, content)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", (rowid, embedding_blob, entity_name, session_id, role, int(float(timestamp)), content))
```

### Filtered Query (Phase 3)
```python
# In query():
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

cursor = conn.execute(f"""
    SELECT rowid, distance, session_id, role, timestamp, content
    FROM omega_memory_vec
    WHERE {where_sql}
    ORDER BY distance
    LIMIT ?
""", params)
```

---

## ✅ Acceptance Tests (Phase 7)

```bash
# Run specific contract tests
python -m pytest tests/test_sqlite_vec_adapter.py::TestSQLiteVecMetadataFiltering -v

# Expected: 5 tests pass
# test_upsert_includes_metadata_columns
# test_filter_by_session_id
# test_filter_by_role
# test_filter_by_timestamp_range
# test_combined_filters
# test_partition_key_isolation
```

---

## 🚀 Full Regression (Phase 8)

```bash
# All must pass
make test                    # 1315 passed
make heritage-vet            # 0 unvetted
make mandate-audit           # 9/9 PASS
make firewall-check          # 0 violations
make sovereignty             # ≥80% local
```

---

## 📋 Quick Verification Commands

```bash
# Verify schema
sqlite3 data/memory/omega_memory.db ".schema omega_memory_vec"

# Should show:
# CREATE VIRTUAL TABLE omega_memory_vec USING vec0(
#   embedding float[1024],
#   entity_name TEXT partition key,
#   session_id TEXT,
#   role TEXT,
#   timestamp INTEGER,
#   +content TEXT
# )

# Test filtered query manually
sqlite3 data/memory/omega_memory.db "
SELECT rowid, distance FROM omega_memory_vec
WHERE embedding MATCH ? AND entity_name = 'test_entity' AND session_id = 'sess-1'
ORDER BY distance LIMIT 5;
"
```

---

## 🔄 Rollback (if needed)

```bash
# 1. Revert code
git checkout HEAD -- src/omega/memory/sqlite_vec_adapter.py
git checkout HEAD -- src/omega/memory/vector_adapters.py
git checkout HEAD -- src/omega/memory_store.py

# 2. Drop new vec0 table (data preserved in omega_memory_data + FTS)
sqlite3 data/memory/omega_memory.db "DROP TABLE IF EXISTS omega_memory_vec;"

# 3. Recreate old schema
sqlite3 data/memory/omega_memory.db "
CREATE VIRTUAL TABLE omega_memory_vec 
USING vec0(embedding float[1024], entity_name TEXT partition key);
"

# 4. Verify
make test
```

---

## 📚 Key References

| Doc | Purpose |
|-----|---------|
| `SPEC_SQLITEVEC_METADATA_MIGRATION.md` | Full spec |
| `SOVEREIGN_ARK_BLUEPRINT.md` | P1-4 context |
| `sqlite-vec v0.1.6 release` | Metadata columns, partition keys |
| `alexgarcia.xyz/sqlite-vec/features/vec0.html` | Official docs |

---

*⬡ OMEGA ⬡ MA'AT ⬡ P2 ⬡ trc_build ⬡ CHECKLIST_READY*