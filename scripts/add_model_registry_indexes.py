#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
Add composite indexes for Model Registry v2 schema.
Optimizes common query patterns for Oracle routing, validation, freshness.

Usage:
    python scripts/add_model_registry_indexes.py --apply
    python scripts/add_model_registry_indexes.py --verify
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path


DB_PATH = Path("config/model_registry/index.sqlite")


INDEXES = [
    # Provider + tier queries (Oracle routing)
    ("idx_models_provider_tier", "models", "provider, tier"),
    
    # Capability score lookups (partial indexes for non-null values)
    ("idx_models_reasoning_score", "models", "cap_reasoning_score", "cap_reasoning_score IS NOT NULL"),
    ("idx_models_code_score", "models", "cap_code_score", "cap_code_score IS NOT NULL"),
    ("idx_models_knowledge_score", "models", "cap_knowledge_score", "cap_knowledge_score IS NOT NULL"),
    ("idx_models_creative_score", "models", "cap_creative_score", "cap_creative_score IS NOT NULL"),
    ("idx_models_tool_use_score", "models", "cap_tool_use_score", "cap_tool_use_score IS NOT NULL"),
    ("idx_models_structured_score", "models", "cap_structured_score", "cap_structured_score IS NOT NULL"),
    ("idx_models_multimodal_score", "models", "cap_multimodal_score", "cap_multimodal_score IS NOT NULL"),
    
    # Validation status filtering
    ("idx_models_validation_status", "models", "validation_status"),
    
    # Freshness queries
    ("idx_models_hf_last_modified", "models", "hf_hub_last_modified", "hf_hub_last_modified IS NOT NULL"),
    ("idx_models_enrichment_last_run", "models", "enrichment_last_run", "enrichment_last_run IS NOT NULL"),
    ("idx_models_benchmark_data_date", "models", "benchmark_data_date", "benchmark_data_date IS NOT NULL"),
    
    # Architecture filtering (for MoE vs dense queries)
    ("idx_models_architecture", "models", "architecture"),
    
    # Status + platform (common filter combo)
    ("idx_models_status_platform", "models", "status, platform"),
    
    # Free tier filtering
    ("idx_models_free_tier", "models", "free_tier"),
]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_existing_indexes(conn: sqlite3.Connection) -> set[str]:
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
    return {row["name"] for row in cursor.fetchall()}


def apply_indexes(conn: sqlite3.Connection, dry_run: bool = False) -> tuple[int, int]:
    existing = get_existing_indexes(conn)
    added = 0
    skipped = 0
    
    for idx_name, table, columns, *where_clause in INDEXES:
        if idx_name in existing:
            print(f"  ⏭️  SKIP: {idx_name} already exists")
            skipped += 1
            continue
        
        where = f" WHERE {where_clause[0]}" if where_clause else ""
        sql = f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({columns}){where};"
        
        if dry_run:
            print(f"  📝 DRY-RUN: {sql}")
        else:
            try:
                conn.execute(sql)
                print(f"  ✅ CREATED: {idx_name} ON {table}({columns}){where}")
            except sqlite3.Error as e:
                print(f"  ❌ FAILED: {idx_name} — {e}")
                raise
        added += 1
    
    return added, skipped


def verify_indexes(conn: sqlite3.Connection) -> bool:
    existing = get_existing_indexes(conn)
    expected = {idx[0] for idx in INDEXES}
    missing = expected - existing
    
    if missing:
        print(f"  ❌ MISSING INDEXES: {missing}")
        return False
    
    print(f"  ✅ All {len(expected)} indexes verified")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Add Model Registry v2 indexes")
    parser.add_argument("--dry-run", action="store_true", help="Show SQL without executing")
    parser.add_argument("--apply", action="store_true", help="Apply indexes")
    parser.add_argument("--verify", action="store_true", help="Verify indexes exist")
    
    args = parser.parse_args()
    
    if not any([args.dry_run, args.apply, args.verify]):
        parser.print_help()
        return 1
    
    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        return 1
    
    conn = get_connection()
    
    try:
        if args.verify:
            print("🔍 Verifying indexes...")
            if verify_indexes(conn):
                print("✅ Verification PASSED")
                return 0
            else:
                print("❌ Verification FAILED")
                return 1
        
        if args.dry_run:
            print(f"📋 DRY-RUN: Adding {len(INDEXES)} indexes")
            added, skipped = apply_indexes(conn, dry_run=True)
            print(f"\n   Would add: {added}, skip: {skipped}")
            return 0
        
        if args.apply:
            print(f"🚀 APPLYING: {len(INDEXES)} indexes")
            conn.execute("BEGIN TRANSACTION")
            try:
                added, skipped = apply_indexes(conn, dry_run=False)
                conn.execute("COMMIT")
                print(f"\n✅ Indexes COMPLETE: added {added}, skipped {skipped}")
                
                print("\n🔍 Verifying...")
                if verify_indexes(conn):
                    print("✅ Verification PASSED")
                else:
                    print("❌ Verification FAILED")
                    return 1
            except Exception as e:
                conn.execute("ROLLBACK")
                print(f"\n❌ Index creation FAILED, rolled back: {e}")
                return 1
        
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())