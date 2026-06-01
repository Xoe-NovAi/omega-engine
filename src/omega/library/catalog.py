# 🔱 Omega Engine — Library Catalog
# AP: AP-LIBRARY-CATALOG-v1.1.0
# SQLite-backed catalog for document metadata and search.
#
# Mandate 1 (AnyIO): SQLite operations use aiosqlite (or anyio.to_thread.run_sync).
# Mandate 9 (Error Integrity): Typed errors throughout.
# Research Enhancement: Multi-dimensional quality scoring (CRACQ pattern).

import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import anyio

from omega.errors import OmegaError

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"
LIBRARY_DIR = DATA_DIR / "library"
DB_PATH = LIBRARY_DIR / "library.db"


class CatalogError(OmegaError):
    """Base for library catalog errors."""

class DocumentNotFoundError(CatalogError):
    """Document not found in catalog."""


class LibraryCatalog:
    """
    Async-safe library catalog backed by SQLite.
    All DB operations run via anyio.to_thread.run_sync.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self._db_path = db_path or DB_PATH

    async def ensure_db(self):
        """Create the database and tables if they don't exist."""
        def _init():
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(self._db_path))
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    path TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    title TEXT,
                    author TEXT,
                    source_url TEXT,
                    quality_vector TEXT, -- JSON array [integrity, coherence, completeness, structure, domain_fit]
                    avg_quality REAL DEFAULT 0.0,
                    created_at TEXT NOT NULL,
                    indexed_at TEXT,
                    embedding_id TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_domain ON documents(domain)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_quality ON documents(avg_quality)")
            conn.commit()
            conn.close()

        await anyio.to_thread.run_sync(_init)

    async def register_document(
        self,
        doc_id: str,
        path: str,
        domain: str,
        title: Optional[str] = None,
        author: Optional[str] = None,
        source_url: Optional[str] = None,
        quality_vector: List[float] = None, # [integrity, coherence, completeness, structure, domain_fit]
    ) -> bool:
        """Register a document in the catalog with multi-dimensional quality."""
        await self.ensure_db()
        
        # Calculate average quality for sorting
        avg_q = sum(quality_vector) / len(quality_vector) if quality_vector else 0.0
        q_json = json.dumps(quality_vector) if quality_vector else "[]"

        def _insert():
            conn = sqlite3.connect(str(self._db_path))
            try:
                conn.execute(
                    """INSERT OR REPLACE INTO documents
                       (id, path, domain, title, author, source_url, quality_vector, avg_quality, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        doc_id, path, domain, title, author, source_url, q_json, avg_q,
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                conn.commit()
                return True
            except sqlite3.Error as e:
                raise CatalogError(f"Failed to register document: {e}") from e
            finally:
                conn.close()

        return await anyio.to_thread.run_sync(_insert)

    async def search(
        self,
        domain: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 20,
        min_quality: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """Search the catalog by domain and/or FTS query."""
        await self.ensure_db()

        def _search():
            conn = sqlite3.connect(str(self._db_path))
            conn.row_factory = sqlite3.Row
            try:
                conditions = ["avg_quality >= ?"]
                params = [min_quality]

                if domain:
                    conditions.append("domain = ?")
                    params.append(domain)

                if query:
                    conditions.append("(title LIKE ? OR author LIKE ?)")
                    params.extend([f"%{query}%", f"%{query}%"])

                sql = f"SELECT * FROM documents WHERE {' AND '.join(conditions)} ORDER BY avg_quality DESC LIMIT ?"
                params.append(limit)

                rows = conn.execute(sql, params).fetchall()
                results = [dict(r) for r in rows]
                
                # Deserialize quality vectors
                for r in results:
                    if r.get("quality_vector"):
                        r["quality_vector"] = json.loads(r["quality_vector"])
                
                return results
            except sqlite3.Error as e:
                raise CatalogError(f"Search failed: {e}") from e
            finally:
                conn.close()

        return await anyio.to_thread.run_sync(_search)

    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a single document by ID."""
        await self.ensure_db()

        def _get():
            conn = sqlite3.connect(str(self._db_path))
            conn.row_factory = sqlite3.Row
            try:
                row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
                if not row:
                    return None
                res = dict(row)
                if res.get("quality_vector"):
                    res["quality_vector"] = json.loads(res["quality_vector"])
                return res
            except sqlite3.Error as e:
                raise CatalogError(f"Failed to get document: {e}") from e
            finally:
                conn.close()

        return await anyio.to_thread.run_sync(_get)

    async def stats(self) -> Dict[str, Any]:
        """Get catalog statistics."""
        await self.ensure_db()

        def _stats():
            conn = sqlite3.connect(str(self._db_path))
            try:
                total = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
                by_domain = conn.execute(
                    "SELECT domain, COUNT(*) FROM documents GROUP BY domain"
                ).fetchall()
                avg_quality = conn.execute(
                    "SELECT AVG(avg_quality) FROM documents"
                ).fetchone()[0] or 0.0
                return {
                    "total_documents": total,
                    "by_domain": dict(by_domain),
                    "avg_quality": round(avg_quality, 2),
                }
            except sqlite3.Error as e:
                raise CatalogError(f"Stats failed: {e}") from e
            finally:
                conn.close()

        return await anyio.to_thread.run_sync(_stats)

    async def prune(self, max_age_days: int = 90) -> int:
        """Remove documents older than max_age_days."""
        await self.ensure_db()

        def _prune():
            conn = sqlite3.connect(str(self._db_path))
            try:
                result = conn.execute(
                    "DELETE FROM documents WHERE created_at < date('now', ?)",
                    (f"-{max_age_days} days",),
                )
                conn.commit()
                return result.rowcount
            except sqlite3.Error as e:
                raise CatalogError(f"Prune failed: {e}") from e
            finally:
                conn.close()

        return await anyio.to_thread.run_sync(_prune)
