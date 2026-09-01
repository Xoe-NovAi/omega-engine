# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Migrate from EmbeddingGemma-300M (768) to Qwen3-Embedding-0.6B (1024→768 MRL).

[D-768-DIM-RE-EMBED] Greenfield path: drops old vec0 tables (re-created on first
upsert with new model). FTS5 index survives (text-only, no re-index needed).
Metadata (omega_memory_data) survives. Re-ingest scripts needed to repopulate.

Usage:
    python scripts/migrate_to_qwen3_768.py [--dry-run] [--db-path PATH]

Pre-requisites:
- Qwen3-Embedding-0.6B-Q5_K_M.gguf downloaded to models/embeddings/
- Backup verified (script creates one automatically)
- All agent processes stopped (no live vec0 connections)

Post-migration:
- Run `python -m omega.memory.reingest --source omega_memory_data --provider qwen3`
  to repopulate vec0 tables with Qwen3 embeddings.
"""
import argparse
import sqlite3
import sys
from pathlib import Path


# Tables to drop (re-created lazily on first upsert with new provider)
TABLES_TO_DROP = [
    "omega_vec_gemma_768", "omega_vec_gemma_768_meta",
    "omega_vec_nomic_512", "omega_vec_nomic_512_meta",
    "omega_vec_nomic_256", "omega_vec_nomic_256_meta",
    "omega_vec_library_256", "omega_vec_library_256_meta",
]

# Tables that SURVIVE migration (text + metadata only, no vector data)
TABLES_PRESERVED = [
    "omega_memory_data",       # Source text + metadata
    "omega_memory_fts",         # FTS5 index (text-only, no re-index)
    "omega_memory_fts_meta",    # FTS5 metadata
    "vec_schema_version",       # Schema version tracking
    "vec_collection_meta",      # Collection metadata
    "vec_hnsw_params",          # HNSW parameters
]


def check_existing_state(conn: sqlite3.Connection) -> dict:
    """Check current state of vec0 tables and report."""
    state = {"tables": {}, "total_vectors": 0, "needs_migration": False}
    for table in TABLES_TO_DROP:
        try:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            state["tables"][table] = count
            state["total_vectors"] += count
            if count > 0:
                state["needs_migration"] = True
        except sqlite3.OperationalError:
            state["tables"][table] = "DOES_NOT_EXIST"

    for table in TABLES_PRESERVED:
        try:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            state["tables"][table] = count
        except sqlite3.OperationalError:
            state["tables"][table] = "DOES_NOT_EXIST"

    return state


def create_backup(db_path: Path, dry_run: bool = False) -> Path:
    """Create a backup using SQLite VACUUM INTO (atomic, online-safe)."""
    backup_path = db_path.with_suffix(".db.bak.pre_qwen3")
    if dry_run:
        print(f"[DRY-RUN] Would create backup: {backup_path}")
        return backup_path

    conn = sqlite3.connect(str(db_path))
    try:
        # VACUUM INTO is atomic and safe even with WAL mode
        conn.execute(f"VACUUM INTO '{backup_path}'")
    finally:
        conn.close()
    print(f"[OK] Backup created: {backup_path}")
    return backup_path


def drop_old_tables(conn: sqlite3.Connection, dry_run: bool = False) -> int:
    """Drop old vec0 tables (re-created lazily on first upsert with new model)."""
    dropped = 0
    for table in TABLES_TO_DROP:
        try:
            if dry_run:
                print(f"[DRY-RUN] Would DROP TABLE IF EXISTS {table}")
                dropped += 1
            else:
                conn.execute(f"DROP TABLE IF EXISTS {table}")
                print(f"[OK] Dropped: {table}")
                dropped += 1
        except sqlite3.OperationalError as e:
            print(f"[WARN] Could not drop {table}: {e}")

    return dropped


def migrate(db_path: Path, dry_run: bool = False) -> int:
    """Run the full migration. Returns 0 on success, 1 on failure."""
    if not db_path.exists():
        print(f"[ERROR] Database not found: {db_path}")
        return 1

    print(f"[INFO] Database: {db_path}")
    print(f"[INFO] Mode: {'DRY-RUN' if dry_run else 'LIVE'}")
    print()

    # Phase 1: Inspect current state
    print("=" * 60)
    print("PHASE 1: Inspecting current state")
    print("=" * 60)
    conn = sqlite3.connect(str(db_path))
    try:
        state = check_existing_state(conn)

        print(f"{'Table':<40} {'Row Count':>15}")
        print("-" * 60)
        for table, count in state["tables"].items():
            print(f"{table:<40} {str(count):>15}")
        print()
        print(f"Total vectors to migrate: {state['total_vectors']}")
        print(f"Preserved tables (FTS + metadata): "
              f"{sum(1 for t in TABLES_PRESERVED if isinstance(state['tables'].get(t), int) and state['tables'].get(t, 0) > 0)}")
        print()

        if state["total_vectors"] == 0:
            print("[OK] No existing vectors — greenfield path, just config update.")
        else:
            print(f"[INFO] Found {state['total_vectors']} vectors — will be re-embedded from source.")

        # Phase 2: Create backup
        print()
        print("=" * 60)
        print("PHASE 2: Creating backup")
        print("=" * 60)
        create_backup(db_path, dry_run=dry_run)

        # Phase 3: Drop old tables
        print()
        print("=" * 60)
        print("PHASE 3: Dropping old vec0 tables")
        print("=" * 60)
        dropped = drop_old_tables(conn, dry_run=dry_run)
        print(f"[OK] {dropped} tables dropped")

        if not dry_run:
            conn.commit()
    finally:
        conn.close()

    # Phase 4: Post-migration instructions
    print()
    print("=" * 60)
    print("PHASE 4: Post-migration steps")
    print("=" * 60)
    print()
    print("1. Verify Qwen3 model is available:")
    print("   $ ls models/embeddings/qwen3-embedding-0.6b-Q5_K_M.gguf")
    print()
    print("2. Re-ingest from source to repopulate vec0 tables:")
    print("   $ python -m omega.memory.reingest --source omega_memory_data --provider qwen3")
    print()
    print("3. Verify retrieval quality:")
    print("   $ python scripts/benchmark_sqlite_vec.py --collection omega_vec_qwen_768")
    print()
    print("[OK] Migration complete.")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Migrate from EmbeddingGemma-300M to Qwen3-Embedding-0.6B (768-dim MRL)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making changes",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=Path("data/omega_memory.db"),
        help="Path to omega_memory.db (default: data/omega_memory.db)",
    )
    args = parser.parse_args()

    return migrate(args.db_path, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
