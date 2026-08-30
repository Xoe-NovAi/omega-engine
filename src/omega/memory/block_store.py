# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-D283-MNEMOSYNE-v1.0.0
# 🔱 SQLite Block Store — Persistent Memory Blocks
# ⬡ OMEGA ⬡ MEMORY ⬡ block_store.py
#
# SQLite-backed MemoryBlock storage using the same omega_memory.db
# as the vector adapter. Ensures ACID transactions and WAL concurrency.

import json
import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import anyio

from .blocks import MemoryBlock, BlockCategory, GovernanceLevel
from omega.infra.sqlite_policy import get_sqlite_connection

logger = logging.getLogger(__name__)


class SQLiteBlockStore:
    """
    SQLite-backed MemoryBlock store.

    Uses the same omega_memory.db as SQLiteVecAdapter for unified storage.
    Table: memory_blocks (owner_entity, label, value, limit, description, read_only,
    category, governance_level, shared_with, taint_policy, metadata_json,
    created_at, updated_at, created_by_id, last_updated_by_id)
    """

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            from omega.memory_store import _get_memory_dir

            db_path = _get_memory_dir() / "omega_memory.db"
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._lock = anyio.Lock()
        self._initialized = False

    def _get_conn(self) -> sqlite3.Connection:
        """Get or create SQLite connection with profiled PRAGMA stack (FS-B4)."""
        if self._conn is None:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            # FS-B4: Use sqlite_policy memory profile (32MB cache, D-282)
            self._conn = get_sqlite_connection(self.db_path, profile="memory")

            # Operational PRAGMA (per A13 — not connection setup)
            self._conn.execute("PRAGMA optimize=0x10002")
        return self._conn

    async def _ensure_initialized(self) -> None:
        """Create memory_blocks table if not exists."""
        if self._initialized:
            return

        def _sync_init():
            conn = self._get_conn()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_blocks (
                    owner_entity TEXT NOT NULL,
                    label TEXT NOT NULL,
                    value TEXT NOT NULL DEFAULT '',
                    block_limit INTEGER NOT NULL DEFAULT 2000,
                    description TEXT NOT NULL DEFAULT '',
                    read_only INTEGER NOT NULL DEFAULT 0,
                    category TEXT NOT NULL DEFAULT 'context',
                    governance_level TEXT NOT NULL DEFAULT 'private',
                    shared_with TEXT NOT NULL DEFAULT '[]',
                    taint_policy TEXT NOT NULL DEFAULT 'strict',
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    created_by_id TEXT NOT NULL DEFAULT '',
                    last_updated_by_id TEXT NOT NULL DEFAULT '',
                    PRIMARY KEY (owner_entity, label)
                )
            """)
            # Index for faster lookups by owner
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_blocks_owner
                ON memory_blocks(owner_entity)
            """)
            conn.commit()

        await anyio.to_thread.run_sync(_sync_init)
        self._initialized = True
        logger.info("SQLiteBlockStore initialized at %s", self.db_path)

    def _row_to_block(self, row: sqlite3.Row) -> MemoryBlock:
        """Convert database row to MemoryBlock."""
        return MemoryBlock(
            id=str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{row['owner_entity']}:{row['label']}")),
            label=row["label"],
            value=row["value"],
            limit=row["block_limit"],
            description=row["description"],
            read_only=bool(row["read_only"]),
            metadata=json.loads(row["metadata_json"]) if row["metadata_json"] else {},
            category=BlockCategory(row["category"]),
            governance_level=GovernanceLevel(row["governance_level"]),
            shared_with=json.loads(row["shared_with"]) if row["shared_with"] else [],
            taint_policy=row["taint_policy"],
            owner_entity=row["owner_entity"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            created_by_id=row["created_by_id"],
            last_updated_by_id=row["last_updated_by_id"],
        )

    async def get_block(self, owner_entity: str, label: str) -> Optional[MemoryBlock]:
        """Get a block by owner and label."""
        await self._ensure_initialized()

        def _sync_get():
            conn = self._get_conn()
            row = conn.execute(
                "SELECT * FROM memory_blocks WHERE owner_entity = ? AND label = ?",
                (owner_entity, label),
            ).fetchone()
            return row

        row = await anyio.to_thread.run_sync(_sync_get)
        if row:
            return self._row_to_block(row)
        return None

    async def get_blocks_for_entity(self, owner_entity: str) -> List[MemoryBlock]:
        """Get all blocks for an entity."""
        await self._ensure_initialized()

        def _sync_get_all():
            conn = self._get_conn()
            rows = conn.execute(
                "SELECT * FROM memory_blocks WHERE owner_entity = ?", (owner_entity,)
            ).fetchall()
            return rows

        rows = await anyio.to_thread.run_sync(_sync_get_all)
        return [self._row_to_block(row) for row in rows]

    async def upsert_block(self, block: MemoryBlock) -> MemoryBlock:
        """Insert or update a block."""
        await self._ensure_initialized()

        block.updated_at = datetime.now(timezone.utc).isoformat()

        def _sync_upsert():
            conn = self._get_conn()
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                """
                INSERT INTO memory_blocks (
                    owner_entity, label, value, block_limit, description, read_only,
                    category, governance_level, shared_with, taint_policy,
                    metadata_json, created_at, updated_at, created_by_id, last_updated_by_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(owner_entity, label) DO UPDATE SET
                    value = excluded.value,
                    block_limit = excluded.block_limit,
                    description = excluded.description,
                    read_only = excluded.read_only,
                    category = excluded.category,
                    governance_level = excluded.governance_level,
                    shared_with = excluded.shared_with,
                    taint_policy = excluded.taint_policy,
                    metadata_json = excluded.metadata_json,
                    updated_at = excluded.updated_at,
                    last_updated_by_id = excluded.last_updated_by_id
            """,
                (
                    block.owner_entity,
                    block.label,
                    block.value,
                    block.limit,
                    block.description,
                    int(block.read_only),
                    block.category.value,
                    block.governance_level.value,
                    json.dumps(block.shared_with),
                    block.taint_policy,
                    json.dumps(block.metadata),
                    block.created_at,
                    block.updated_at,
                    block.created_by_id,
                    block.last_updated_by_id,
                ),
            )
            conn.commit()

        await anyio.to_thread.run_sync(_sync_upsert)
        return block

    async def delete_block(self, owner_entity: str, label: str) -> bool:
        """Delete a block."""
        await self._ensure_initialized()

        def _sync_delete():
            conn = self._get_conn()
            conn.execute("BEGIN IMMEDIATE")
            cursor = conn.execute(
                "DELETE FROM memory_blocks WHERE owner_entity = ? AND label = ?",
                (owner_entity, label),
            )
            conn.commit()
            return cursor.rowcount > 0

        return await anyio.to_thread.run_sync(_sync_delete)

    async def list_all(self) -> List[MemoryBlock]:
        """List all blocks."""
        await self._ensure_initialized()

        def _sync_list():
            conn = self._get_conn()
            rows = conn.execute("SELECT * FROM memory_blocks").fetchall()
            return rows

        rows = await anyio.to_thread.run_sync(_sync_list)
        return [self._row_to_block(row) for row in rows]


# Global block store instance
_sqlite_block_store: Optional[SQLiteBlockStore] = None


def get_sqlite_block_store() -> SQLiteBlockStore:
    """Get or create the global SQLite block store."""
    global _sqlite_block_store
    if _sqlite_block_store is None:
        _sqlite_block_store = SQLiteBlockStore()
    return _sqlite_block_store
