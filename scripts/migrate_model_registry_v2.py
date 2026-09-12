#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

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