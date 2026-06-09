"""SQLite FTS5 Full-Text Search Index for Omega Memory.

[FTS5 Search Pattern: SQLite public domain]
Provides BM25-ranked search across conversation history with sovereign isolation.
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger("omega.memory.fts")

class ConversationFTSIndex:
    """SQLite FTS5 index for conversation exchanges."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._conn = None
        self._initialized = False

    def initialize(self):
        """Initialize the FTS5 virtual table."""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            
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
        except Exception as e:
            logger.error("Failed to initialize FTS5 index: %s", e)
            self._initialized = False

    def index_exchange(self, session_id: str, entity_name: str, role: str, content: str):
        """Index a single exchange. [C2: try/except wrapped in MemoryStore]"""
        if not self._initialized:
            return
            
        try:
            self._conn.execute(
                "INSERT INTO exchanges (session_id, entity_name, role, content, timestamp) VALUES (?, ?, ?, ?, ?)",
                (session_id, entity_name, role, content, datetime.now(timezone.utc).isoformat())
            )
            self._conn.commit()
        except Exception as e:
            logger.warning("FTS index write failed for session %s: %s", session_id, e)

    def search(self, query: str, entity_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search across exchanges for a specific entity. [C3: entity_name REQUIRED]"""
        if not self._initialized:
            return []
            
        try:
            # BM25 ranking via FTS5 'rank'
            cursor = self._conn.execute("""
                SELECT session_id, role, content, timestamp, rank
                FROM exchanges 
                WHERE exchanges MATCH ? AND entity_name = ?
                ORDER BY rank
                LIMIT ?
            """, (query, entity_name, limit))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error("FTS search failed: %s", e)
            return []

    def remove_session(self, session_id: str):
        """Remove all exchanges for a session (C1 fix)."""
        if not self._initialized:
            return
            
        try:
            self._conn.execute("DELETE FROM exchanges WHERE session_id = ?", (session_id,))
            self._conn.commit()
            logger.info("Removed session %s from FTS index", session_id)
        except Exception as e:
            logger.error("Failed to remove session %s from FTS: %s", session_id, e)

    def close(self):
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
            self._initialized = False

    def count(self) -> int:
        """Return total number of indexed exchanges."""
        if not self._initialized:
            return 0
        try:
            cursor = self._conn.execute("SELECT count(*) FROM exchanges")
            return cursor.fetchone()[0]
        except Exception:
            return 0
