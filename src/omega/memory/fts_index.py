# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-PR-READINESS-v1.0.0
"""SQLite FTS5 Full-Text Search Index for Omega Memory.

# [heritage: sqlite-fts5 2015] SQLite FTS5 — BM25 full-text search with Porter stemmer
Provides BM25-ranked search across conversation history with sovereign isolation.
"""
# DocRef: docs/architecture/MEMORY_STORE_DEEP_DIVE.md

import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

import anyio

logger = logging.getLogger("omega.memory.fts")


def escape_fts_query(query: str) -> str:
    """Escape a user search string for the FTS5 MATCH operand.

    FTS5 has its own query grammar (``AND``/``OR``/``NOT``/``NEAR``,
    ``"phrase"``, ``-exclude``, ``*``). An unescaped user string containing
    these tokens triggers ``sqlite3.OperationalError: fts5: syntax error`` —
    a denial-of-service-by-error rather than data exposure.

    Mitigation: wrap each whitespace-token in double quotes (phrase match)
    and escape any embedded double quotes. This neutralizes FTS5 special
    syntax while preserving the user's search intent.

    [P2-6 / §4 audit] FTS5 MATCH syntax injection.
    """
    if not query:
        return ""
    tokens = query.split()
    escaped = []
    for tok in tokens:
        safe = tok.replace('"', '\\"')
        escaped.append(f'"{safe}"')
    return " ".join(escaped)


class ConversationFTSIndex:
    """SQLite FTS5 index for conversation exchanges."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._conn = None
        self._initialized = False
        # [M1 AnyIO] Same rationale as MetricsDB — check_same_thread=False
        # (set in initialize()) permits cross-thread use but does not
        # serialize it. Lazy-init: constructing anyio.Lock() outside a
        # running event loop is backend-dependent, so defer to first use.
        self._write_lock: Optional[anyio.Lock] = None

    def _get_write_lock(self) -> "anyio.Lock":
        if self._write_lock is None:
            self._write_lock = anyio.Lock()
        return self._write_lock

    def initialize(self):
        """Initialize the FTS5 virtual table."""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            # [id-soft: quake-1996] WAL journal mode — allows concurrent reads
            # from foreground + background (Dreaming Cycle) without contention.
            self._conn.execute("PRAGMA journal_mode=WAL")

            # Create FTS5 virtual table with Porter stemmer
            # session_id: unique session UUID
            # entity_name: sovereign owner of the memory
            # role: 'user' or 'assistant'
            # content: the text content
            # timestamp: unindexed ISO string
            self._conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS exchanges USING fts5(
                    session_id,
                    entity_name,
                    role,
                    content,
                    timestamp UNINDEXED,
                    tokenize='porter'
                )
            """)
            self._conn.commit()
            self._initialized = True
            logger.info("FTS5 index initialized at %s", self.db_path)
        except (sqlite3.Error, OSError) as e:
            logger.error("Failed to initialize FTS5 index: %s", e)
            self._initialized = False

    async def index_exchange(
        self, session_id: str, entity_name: str, role: str, content: str
    ) -> None:
        """Index a single exchange. [M1 AnyIO] Offloaded + lock-serialized.

        [C2: caller wraps this in try/except in MemoryStore] — this method
        still swallows sqlite3.Error/RuntimeError internally for backward
        compatibility with that call-site contract; it does not raise.
        """
        if not self._initialized:
            return

        timestamp = datetime.now(timezone.utc).isoformat()

        def _sync_index() -> None:
            self._conn.execute(
                "INSERT INTO exchanges (session_id, entity_name, role, content, timestamp) VALUES (?, ?, ?, ?, ?)",
                (session_id, entity_name, role, content, timestamp),
            )
            self._conn.commit()

        try:
            async with self._get_write_lock():
                await anyio.to_thread.run_sync(_sync_index)
        except (sqlite3.Error, RuntimeError) as e:
            logger.warning("FTS index write failed for session %s: %s", session_id, e)

    async def search(self, query: str, entity_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search across exchanges for a specific entity. [C3: entity_name REQUIRED] [M1 AnyIO]"""
        if not self._initialized:
            return []

        def _sync_search():
            # BM25 ranking via FTS5 'rank'
            # [P2-6] Escape user query to prevent FTS5 MATCH syntax injection.
            fts_query = escape_fts_query(query)
            cursor = self._conn.execute(
                """
                SELECT session_id, role, content, timestamp, rank
                FROM exchanges
                WHERE exchanges MATCH ? AND entity_name = ?
                ORDER BY rank
                LIMIT ?
            """,
                (fts_query, entity_name, limit),
            )
            return [dict(row) for row in cursor.fetchall()]

        try:
            return await anyio.to_thread.run_sync(_sync_search)
        except sqlite3.OperationalError as e:
            # FTS5 syntax error from a malformed query — degrade gracefully.
            logger.warning("FTS5 query syntax error (degraded): %s", e)
            return []
        except (sqlite3.Error, RuntimeError) as e:
            logger.error("FTS search failed: %s", e)
            return []

    async def remove_session(self, session_id: str) -> None:
        """Remove all exchanges for a session (C1 fix). [M1 AnyIO]"""
        if not self._initialized:
            return

        def _sync_remove() -> None:
            self._conn.execute("DELETE FROM exchanges WHERE session_id = ?", (session_id,))
            self._conn.commit()

        try:
            async with self._get_write_lock():
                await anyio.to_thread.run_sync(_sync_remove)
            logger.info("Removed session %s from FTS index", session_id)
        except (sqlite3.Error, RuntimeError) as e:
            logger.error("Failed to remove session %s from FTS: %s", session_id, e)

    def __del__(self):
        """Best-effort safety net: close the connection on garbage collection."""
        if self._conn is not None:
            try:
                self._conn.close()
            except (sqlite3.Error, RuntimeError):
                pass

    def close(self):
        """Close the database connection."""
        if self._conn:
            try:
                # [G-12] Optimize FTS index before closing
                self._conn.execute("PRAGMA optimize")
                logger.debug("FTS5 index optimized")
            except (sqlite3.Error, RuntimeError) as e:
                logger.warning("FTS index optimize failed: %s", e)

            self._conn.close()
            self._conn = None
            self._initialized = False

    async def count(self) -> int:
        """Return total number of indexed exchanges. [M1 AnyIO]"""
        if not self._initialized:
            return 0
        try:

            def _sync_count():
                cursor = self._conn.execute("SELECT count(*) FROM exchanges")
                return cursor.fetchone()[0]

            return await anyio.to_thread.run_sync(_sync_count)
        except (sqlite3.Error, RuntimeError):
            return 0
