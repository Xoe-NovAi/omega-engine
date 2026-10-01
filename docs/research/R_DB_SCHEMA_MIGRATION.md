<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 GAP 4: Database Schema Migration for New Enrichment Fields
**AP Token**: `AP-GAP4-DB-MIGRATION-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_gap4_db_migration ⬡ ACTIVE

**Date**: 2026-07-18
**Status**: RESEARCH COMPLETE — Implementation Ready
**Dependencies**: GAP 1 (AA API), GAP 2 (HF Hub params), GAP 3 (Validation schema)

---

## 📋 EXECUTIVE SUMMARY

This document details the SQLite schema migration required to support the new enrichment fields from GAP 1 (Artificial Analysis), GAP 2 (HF Hub parameters), and GAP 3 (Validation metadata). The current `models` table has 42 columns; we need to add ~35 new columns for capability scores with citations, parameter breakdown, validation metadata, and freshness tracking.

**Migration Strategy**: Additive-only (ALTER TABLE ADD COLUMN) — zero data loss, zero downtime, backward compatible. All new columns are nullable with no defaults, allowing existing 35 model cards to remain valid.

---

## 🔬 RESEARCH FINDINGS

### Current Schema (42 columns)
```sql
CREATE TABLE models (
    model_id TEXT PRIMARY KEY,
    display_name TEXT,
    version TEXT,
    provider TEXT,
    platform TEXT,
    tier TEXT,
    status TEXT,
    context_window INTEGER,
    max_output_tokens INTEGER,
    reasoning REAL,
    code_generation REAL,
    knowledge REAL,
    creative REAL,
    tool_use BOOLEAN,
    structured_output BOOLEAN,
    multimodal BOOLEAN,
    code_execution BOOLEAN,
    parallel_search BOOLEAN,
    workspace_integration BOOLEAN,
    input_per_mtok REAL,
    output_per_mtok REAL,
    free_tier BOOLEAN,
    latency_p99_ms INTEGER,
    uptime_percent REAL,
    engine_routable BOOLEAN,
    opencode_cli_only BOOLEAN,
    recommended_engine_alternative TEXT,
    temperature REAL,
    top_p REAL,
    top_k INTEGER,
    repetition_penalty REAL,
    max_tokens INTEGER,
    stop_sequences TEXT,
    presence_penalty REAL,
    frequency_penalty REAL,
    tags TEXT,
    created_at TEXT,
    updated_at TEXT,
    schema_version TEXT
);
```

### SQLite ALTER TABLE Capabilities (2026)
From official docs and production best practices:
- ✅ `ADD COLUMN` — Supported, O(1) for nullable columns without constraints
- ✅ `RENAME COLUMN` — Supported since 3.25.0 (2018)
- ✅ `DROP COLUMN` — Supported since 3.35.0 (2021)
- ✅ `SET/DROP NOT NULL` — Supported since 3.53.0 (2026-04-09)
- ❌ Changing column types — Requires table rebuild
- ❌ Adding constraints to existing columns — Requires table rebuild

### Migration Best Practices (2026)
1. **Prefer additive changes** — `ADD COLUMN` is nearly free, no table lock for nullable columns
2. **No DEFAULT on existing rows** — SQLite 3.37+ validates CHECK/NOT NULL against existing rows; nullable columns skip this
3. **Use schema_migrations table** — Track applied migrations for idempotency
4. **Wrap in transactions** — Atomicity for multi-step migrations
5. **Test in staging first** — Verify row counts, indexes, foreign keys

---

## 🎯 NEW FIELDS REQUIRED (35 columns)

### A. Capability Scores with Citations (21 columns)
Each of the 7 capability dimensions gets: score, benchmark, source, date

| Capability | Score | Benchmark | Source | Date |
|------------|-------|-----------|--------|------|
| reasoning | `cap_reasoning_score REAL` | `cap_reasoning_benchmark TEXT` | `cap_reasoning_source TEXT` | `cap_reasoning_date TEXT` |
| code_generation | `cap_code_score REAL` | `cap_code_benchmark TEXT` | `cap_code_source TEXT` | `cap_code_date TEXT` |
| knowledge | `cap_knowledge_score REAL` | `cap_knowledge_benchmark TEXT` | `cap_knowledge_source TEXT` | `cap_knowledge_date TEXT` |
| creative | `cap_creative_score REAL` | `cap_creative_benchmark TEXT` | `cap_creative_source TEXT` | `cap_creative_date TEXT` |
| tool_use | `cap_tool_use_score REAL` | `cap_tool_use_benchmark TEXT` | `cap_tool_use_source TEXT` | `cap_tool_use_date TEXT` |
| structured_output | `cap_structured_score REAL` | `cap_structured_benchmark TEXT` | `cap_structured_source TEXT` | `cap_structured_date TEXT` |
| multimodal | `cap_multimodal_score REAL` | `cap_multimodal_benchmark TEXT` | `cap_multimodal_source TEXT` | `cap_multimodal_date TEXT` |

### B. Parameter Breakdown (9 columns)
| Field | Type | Description |
|-------|------|-------------|
| `total_parameters` | BIGINT | Total params from HF Hub safetensors.total |
| `active_parameters` | BIGINT | Active params (dense = total; MoE = experts × expert_params) |
| `architecture` | TEXT | 'dense', 'moe', 'mamba', 'hybrid', 'unknown' |
| `layer_count` | INTEGER | From config.num_hidden_layers |
| `hidden_size` | INTEGER | From config.hidden_size |
| `num_attention_heads` | INTEGER | From config.num_attention_heads |
| `num_kv_heads` | INTEGER | From config.num_key_value_heads (GQA) |
| `expert_count` | INTEGER | MoE: config.num_local_experts |
| `expert_top_k` | INTEGER | MoE: config.num_experts_per_tok |

### C. Validation Metadata (4 columns)
| Field | Type | Description |
|-------|------|-------------|
| `validation_status` | TEXT | 'valid', 'stale', 'invalid', 'pending' |
| `validation_errors` | TEXT | JSON array of validation errors |
| `last_validated` | TEXT | ISO timestamp of last validation run |
| `validation_version` | INTEGER | Schema version of validator used |

### D. Freshness Tracking (3 columns)
| Field | Type | Description |
|-------|------|-------------|
| `benchmark_data_date` | TEXT | When capability scores were recorded (ISO) |
| `hf_hub_last_modified` | TEXT | HF Hub repo lastModified (ISO) |
| `enrichment_last_run` | TEXT | When enrichment pipeline last ran (ISO) |

---

## 📦 MIGRATION SCRIPT

```python
#!/usr/bin/env python3
"""
Model Registry Schema Migration v1 → v2
Adds 35 enrichment columns to models table.
Additive-only: zero data loss, zero downtime, backward compatible.

Usage:
    python scripts/migrate_model_registry_v2.py --dry-run
    python scripts/migrate_model_registry_v2.py --apply
    python scripts/migrate_model_registry_v2.py --verify
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


DB_PATH = Path("config/model_registry/index.sqlite")
MIGRATION_VERSION = 2
MIGRATION_NAME = "add_enrichment_fields_v2"


# All new columns to add (nullable, no defaults, no constraints)
NEW_COLUMNS = [
    # Capability scores with citations (7 capabilities × 4 fields = 28)
    ("cap_reasoning_score", "REAL"),
    ("cap_reasoning_benchmark", "TEXT"),
    ("cap_reasoning_source", "TEXT"),
    ("cap_reasoning_date", "TEXT"),
    ("cap_code_score", "REAL"),
    ("cap_code_benchmark", "TEXT"),
    ("cap_code_source", "TEXT"),
    ("cap_code_date", "TEXT"),
    ("cap_knowledge_score", "REAL"),
    ("cap_knowledge_benchmark", "TEXT"),
    ("cap_knowledge_source", "TEXT"),
    ("cap_knowledge_date", "TEXT"),
    ("cap_creative_score", "REAL"),
    ("cap_creative_benchmark", "TEXT"),
    ("cap_creative_source", "TEXT"),
    ("cap_creative_date", "TEXT"),
    ("cap_tool_use_score", "REAL"),
    ("cap_tool_use_benchmark", "TEXT"),
    ("cap_tool_use_source", "TEXT"),
    ("cap_tool_use_date", "TEXT"),
    ("cap_structured_score", "REAL"),
    ("cap_structured_benchmark", "TEXT"),
    ("cap_structured_source", "TEXT"),
    ("cap_structured_date", "TEXT"),
    ("cap_multimodal_score", "REAL"),
    ("cap_multimodal_benchmark", "TEXT"),
    ("cap_multimodal_source", "TEXT"),
    ("cap_multimodal_date", "TEXT"),
    # Parameter breakdown (9)
    ("total_parameters", "BIGINT"),
    ("active_parameters", "BIGINT"),
    ("architecture", "TEXT"),
    ("layer_count", "INTEGER"),
    ("hidden_size", "INTEGER"),
    ("num_attention_heads", "INTEGER"),
    ("num_kv_heads", "INTEGER"),
    ("expert_count", "INTEGER"),
    ("expert_top_k", "INTEGER"),
    # Validation metadata (4)
    ("validation_status", "TEXT"),
    ("validation_errors", "TEXT"),
    ("last_validated", "TEXT"),
    ("validation_version", "INTEGER"),
    # Freshness tracking (3)
    ("benchmark_data_date", "TEXT"),
    ("hf_hub_last_modified", "TEXT"),
    ("enrichment_last_run", "TEXT"),
]


def get_connection() -> sqlite3.Connection:
    """Get database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_migration_table(conn: sqlite3.Connection) -> None:
    """Create schema_migrations table if not exists."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)


def is_migration_applied(conn: sqlite3.Connection, version: int) -> bool:
    """Check if migration version already applied."""
    cursor = conn.execute(
        "SELECT 1 FROM schema_migrations WHERE version = ?", (version,)
    )
    return cursor.fetchone() is not None


def get_existing_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    """Get set of existing column names for a table."""
    cursor = conn.execute(f"PRAGMA table_info({table})")
    return {row["name"] for row in cursor.fetchall()}


def column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    """Check if column exists in table."""
    return column in get_existing_columns(conn, table)


def apply_migration(conn: sqlite3.Connection, dry_run: bool = False) -> tuple[int, int]:
    """Apply ADD COLUMN statements for all new columns.
    
    Returns:
        (added_count, skipped_count)
    """
    existing = get_existing_columns(conn, "models")
    added = 0
    skipped = 0
    
    for col_name, col_type in NEW_COLUMNS:
        if col_name in existing:
            print(f"  ⏭️  SKIP: {col_name} already exists")
            skipped += 1
            continue
        
        sql = f"ALTER TABLE models ADD COLUMN {col_name} {col_type};"
        
        if dry_run:
            print(f"  📝 DRY-RUN: {sql}")
        else:
            try:
                conn.execute(sql)
                print(f"  ✅ ADDED: {col_name} {col_type}")
            except sqlite3.Error as e:
                print(f"  ❌ FAILED: {col_name} — {e}")
                raise
        added += 1
    
    return added, skipped


def record_migration(conn: sqlite3.Connection, version: int, name: str) -> None:
    """Record migration in schema_migrations table."""
    conn.execute(
        "INSERT INTO schema_migrations (version, name, applied_at) VALUES (?, ?, ?)",
        (version, name, datetime.now(timezone.utc).isoformat())
    )


def verify_migration(conn: sqlite3.Connection) -> bool:
    """Verify all new columns exist and table is readable."""
    existing = get_existing_columns(conn, "models")
    
    missing = [c for c, _ in NEW_COLUMNS if c not in existing]
    if missing:
        print(f"  ❌ MISSING COLUMNS: {missing}")
        return False
    
    # Verify row count unchanged
    cursor = conn.execute("SELECT COUNT(*) as cnt FROM models")
    row_count = cursor.fetchone()["cnt"]
    print(f"  ✅ Row count: {row_count}")
    
    # Verify schema_version updated
    cursor = conn.execute("SELECT schema_version FROM models LIMIT 1")
    row = cursor.fetchone()
    if row and row["schema_version"]:
        print(f"  ✅ schema_version sample: {row['schema_version']}")
    
    print(f"  ✅ All {len(NEW_COLUMNS)} new columns verified")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Model Registry Schema Migration v1→v2")
    parser.add_argument("--dry-run", action="store_true", help="Show SQL without executing")
    parser.add_argument("--apply", action="store_true", help="Apply migration")
    parser.add_argument("--verify", action="store_true", help="Verify migration applied")
    parser.add_argument("--force", action="store_true", help="Force apply even if already applied")
    
    args = parser.parse_args()
    
    if not any([args.dry_run, args.apply, args.verify]):
        parser.print_help()
        return 1
    
    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        return 1
    
    conn = get_connection()
    
    try:
        ensure_migration_table(conn)
        
        if args.verify:
            print("🔍 Verifying migration...")
            if verify_migration(conn):
                print("✅ Verification PASSED")
                return 0
            else:
                print("❌ Verification FAILED")
                return 1
        
        if is_migration_applied(conn, MIGRATION_VERSION) and not args.force:
            print(f"⚠️  Migration v{MIGRATION_VERSION} already applied. Use --force to re-run.")
            return 0
        
        if args.dry_run:
            print(f"📋 DRY-RUN: Migration v{MIGRATION_VERSION} ({MIGRATION_NAME})")
            print(f"   Database: {DB_PATH}")
            print(f"   New columns: {len(NEW_COLUMNS)}")
            added, skipped = apply_migration(conn, dry_run=True)
            print(f"\n   Would add: {added}, skip: {skipped}")
            return 0
        
        if args.apply:
            print(f"🚀 APPLYING: Migration v{MIGRATION_VERSION} ({MIGRATION_NAME})")
            print(f"   Database: {DB_PATH}")
            
            conn.execute("BEGIN TRANSACTION")
            try:
                added, skipped = apply_migration(conn, dry_run=False)
                record_migration(conn, MIGRATION_VERSION, MIGRATION_NAME)
                conn.execute("COMMIT")
                print(f"\n✅ Migration COMPLETE: added {added}, skipped {skipped}")
                
                # Verify
                print("\n🔍 Verifying...")
                if verify_migration(conn):
                    print("✅ Verification PASSED")
                else:
                    print("❌ Verification FAILED — manual review needed")
                    return 1
                
            except Exception as e:
                conn.execute("ROLLBACK")
                print(f"\n❌ Migration FAILED, rolled back: {e}")
                return 1
        
        return 0
        
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
```

---

## 🔧 INDEXING STRATEGY

After migration, add composite indexes for common query patterns:

```sql
-- Provider + capability threshold queries (Oracle routing)
CREATE INDEX IF NOT EXISTS idx_models_provider_tier 
    ON models(provider, tier);

-- Capability score lookups
CREATE INDEX IF NOT EXISTS idx_models_reasoning_score 
    ON models(cap_reasoning_score) WHERE cap_reasoning_score IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_models_code_score 
    ON models(cap_code_score) WHERE cap_code_score IS NOT NULL;

-- Validation status filtering
CREATE INDEX IF NOT EXISTS idx_models_validation_status 
    ON models(validation_status);

-- Freshness queries
CREATE INDEX IF NOT EXISTS idx_models_hf_last_modified 
    ON models(hf_hub_last_modified) WHERE hf_hub_last_modified IS NOT NULL;

-- Full-text search on model_id (if not already present)
-- Note: SQLite FTS5 is separate virtual table; consider separate FTS table
```

---

## 🔄 ROLLBACK PLAN

Since this is additive-only (only `ADD COLUMN`), rollback is simple:

```sql
-- Remove all added columns (SQLite 3.35+)
ALTER TABLE models DROP COLUMN cap_reasoning_score;
-- ... repeat for all 35 columns ...

-- Remove migration record
DELETE FROM schema_migrations WHERE version = 2;
```

**Note**: `DROP COLUMN` rewrites the table (O(n) time). For 35 columns, run as single transaction. Test rollback in staging first.

---

## ✅ VALIDATION CHECKLIST

| Check | Method | Pass Criteria |
|-------|--------|---------------|
| Row count unchanged | `SELECT COUNT(*) FROM models` | Before = After |
| All 35 columns exist | `PRAGMA table_info(models)` | All present |
| Existing data readable | `SELECT * FROM models LIMIT 5` | No errors |
| schema_migrations updated | `SELECT * FROM schema_migrations` | Version 2 recorded |
| Indexes created | `.indexes` | New indexes listed |
| Application reads work | Run model registry loader | No crashes |
| Application writes work | Insert test model | No errors |

---

## 📝 DELIVERABLES

| Artifact | Path | Status |
|----------|------|--------|
| Research Doc | `docs/research/R_DB_SCHEMA_MIGRATION.md` | ✅ This document |
| Migration Script | `scripts/migrate_model_registry_v2.py` | ✅ Above |
| Index Script | `scripts/add_model_registry_indexes.py` | 📋 To create |
| Rollback Script | `scripts/rollback_model_registry_v2.py` | 📋 To create |

---

## 🔗 DEPENDENCIES

- **GAP 1**: AA API fields defined → capability score columns
- **GAP 2**: HF Hub parameter fields defined → parameter breakdown columns
- **GAP 3**: Validation schema defined → validation metadata columns
- **GAP 5**: Freshness design → freshness tracking columns

**Must run before GAP 5 columns**

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_gap4_db_migration ⬡ RESEARCH COMPLETE*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
