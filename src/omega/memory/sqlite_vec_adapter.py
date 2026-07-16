"""SQLite-vec Unified Memory Fabric Adapter for Omega Memory.
AP: AP-SQLITEVEC-ADAPTER-v1.0.0

Drop Qdrant entirely. Unified fabric only. One `omega_memory.db` (FTS5 + vec0 + SQL graph edges).

Implements IVectorStoreAdapter interface using sqlite-vec for vector search
and FTS5 for full-text search, with Reciprocal Rank Fusion in Python.

Corrections applied from Jem's R_SQLITEVEC_VERIFICATION_20260712.md:
- C3: Sovereign Isolation via entity_name TEXT partition key
- Class Overwrite Hazard: ADD a tier, never redefine the class
- Write Contention: anyio.Lock + exponential backoff (50/100/200ms)
- RRF Unification: Python-side RRF fusion (reuse existing search() logic)
"""
# [heritage: sqlite-fts5 2015] SQLite FTS5 — BM25 full-text search with Porter stemmer
# [heritage: sqlite-vec 2024] sqlite-vec — vector similarity search extension

import json
import logging
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import anyio

from .vector_adapters import IVectorStoreAdapter
from .hybrid_search import HybridSearchEngine, FTSResult, VecResult
from omega.errors import OmegaError, ProviderError, ProviderUnavailableError

logger = logging.getLogger(__name__)

# Default embedding dimension for mxbai-embed-large-v1
DEFAULT_EMBEDDING_DIM = 1024


class SQLiteVecAdapter(IVectorStoreAdapter):
    """SQLite-vec implementation of the vector store adapter.
    
    Unified fabric: FTS5 + vec0 + metadata in one omega_memory.db.
    Entity isolation via partition key (Correction C3).
    Write contention mitigation via anyio.Lock + exponential backoff.
    
    Schema design:
    - omega_memory_data: INTEGER PRIMARY KEY (rowid), uuid TEXT, entity_name, session_id, role, content, timestamp, metadata_json
    - omega_memory_fts: FTS5 virtual table (content, entity_name, session_id, role, timestamp)
    - omega_memory_vec: vec0 virtual table (embedding, entity_name partition key)
    
    All three tables share the same rowid for O(1) joins.
    """

    def __init__(
        self,
        db_path: Optional[Path] = None,
        embedding_dim: int = DEFAULT_EMBEDDING_DIM,
        timeout: float = 5.0,
    ):
        if db_path is None:
            # Default to data/memory/omega_memory.db
            from omega.memory_store import _get_memory_dir
            db_path = _get_memory_dir() / "omega_memory.db"
        
        self.db_path = db_path
        self._embedding_dim = embedding_dim
        self.timeout = timeout
        self._conn: Optional[sqlite3.Connection] = None
        self._write_lock = anyio.Lock()
        self._initialized = False
        self._vec_table_created = False

    def _get_conn(self) -> sqlite3.Connection:
        """Get or create the SQLite connection with hardened PRAGMA stack.
        
        PRAGMA stack per Researcher's hardware validation (Ryzen 7 5700U, 14Gi RAM, NVMe):
        - journal_mode=WAL: Concurrent reads during writes
        - busy_timeout=30000: 30s for background researcher + agent contention
        - synchronous=NORMAL: Safe for committed transactions, fsync at checkpoint
        - journal_size_limit=67108864: 64MB WAL cap — prevents unbounded growth
        - cache_size=-524288: 512MB page cache — adaptive for 14Gi RAM (Music Assistant pattern)
        - mmap_size=268435456: 256MB memory-mapped I/O — capped default, scales with DB (2× DB, max 256MB)
        - wal_autocheckpoint=1000: Passive checkpoint every 1000 pages
        - foreign_keys=ON: Good practice for schema integrity
        - temp_store=MEMORY: Faster temp tables for agent operations
        - optimize=0x10002: Auto-analyze + auto-index for long-lived connections
        """
        if self._conn is None:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(
                str(self.db_path),
                timeout=self.timeout,
                check_same_thread=False,
            )
            self._conn.row_factory = sqlite3.Row
            
            # Hardened PRAGMA stack (D-282 Critical Path)
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA busy_timeout=30000")
            self._conn.execute("PRAGMA synchronous=NORMAL")
            self._conn.execute("PRAGMA journal_size_limit=67108864")
            self._conn.execute("PRAGMA cache_size=-524288")
            self._conn.execute("PRAGMA mmap_size=268435456")
            self._conn.execute("PRAGMA wal_autocheckpoint=1000")
            self._conn.execute("PRAGMA foreign_keys=ON")
            self._conn.execute("PRAGMA temp_store=MEMORY")
            self._conn.execute("PRAGMA optimize=0x10002")
        return self._conn

    def _load_extension(self, conn: sqlite3.Connection) -> None:
        """Load the sqlite-vec extension into a connection."""
        import sqlite_vec
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)

    async def _ensure_initialized(self) -> None:
        """Initialize FTS5, metadata tables if not already done.
        
        NOTE: vec0 table is created lazily on first upsert() when we know
        the actual embedding dimension. This prevents dimension mismatch
        between configured default and actual embedding chain output.
        """
        if self._initialized:
            return
        
        def _sync_init():
            conn = self._get_conn()
            
            # Load sqlite-vec extension
            try:
                self._load_extension(conn)
                logger.debug("sqlite-vec extension loaded successfully")
            except ImportError:
                logger.error("sqlite-vec module not installed")
                raise
            except sqlite3.Error as e:
                logger.error("Failed to load sqlite-vec extension: %s", e)
                raise
            
            # Regular table for metadata storage (INTEGER PRIMARY KEY for rowid alignment)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS omega_memory_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uuid TEXT NOT NULL,
                    entity_name TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata_json TEXT
                )
            """)
            
            # FTS5 table for full-text search (rowid matches omega_memory_data.id)
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS omega_memory_fts
                USING fts5(content, entity_name, session_id, role, timestamp)
            """)
            
            # vec0 table is created lazily in _ensure_vec_table() on first upsert
            # when we know the actual embedding dimension from the embedding chain.
            
            conn.commit()
        
        try:
            await anyio.to_thread.run_sync(_sync_init)
            self._initialized = True
            logger.info(
                "SQLiteVecAdapter initialized at %s (dim=%d, vec0 deferred)",
                self.db_path, self._embedding_dim
            )
        except (sqlite3.Error, OSError) as e:
            logger.error("Failed to initialize SQLiteVecAdapter: %s", e)
            raise ProviderUnavailableError(
                "sqlite_vec",
                f"SQLite-vec initialization failed: {e}",
                raw_error=e
            ) from e

    async def _ensure_vec_table(self, actual_dim: int) -> None:
        """Create or recreate vec0 table with correct dimension.
        
        Called on first upsert() when we know the actual embedding dimension.
        If dimension changes (model upgrade), drops and recreates the vec0 table.
        """
        if self._vec_table_created and actual_dim == self._embedding_dim:
            return  # Already created with correct dimension
        
        if self._vec_table_created and actual_dim != self._embedding_dim:
            # Dimension changed (model upgrade) — drop and recreate
            logger.warning(
                "Embedding dimension changed %d → %d. Recreating vec0 table.",
                self._embedding_dim, actual_dim
            )
            def _sync_drop():
                conn = self._get_conn()
                conn.execute("DROP TABLE IF EXISTS omega_memory_vec")
                conn.commit()
            await anyio.to_thread.run_sync(_sync_drop)
            self._vec_table_created = False
        
        def _sync_create_vec():
            conn = self._get_conn()
            conn.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS omega_memory_vec
                USING vec0(embedding float[{actual_dim}], entity_name TEXT partition key)
            """)
            conn.commit()
        
        await anyio.to_thread.run_sync(_sync_create_vec)
        self._embedding_dim = actual_dim
        self._vec_table_created = True
        logger.info("vec0 table created with dim=%d", actual_dim)

    async def upsert(
        self,
        entity_name: str,
        vector: List[float],
        metadata: Dict[str, Any],
        id: Optional[str] = None,
    ) -> str:
        """Insert or update a vector and its metadata.
        
        Returns the UUID string identifier (not the integer rowid).
        Auto-detects embedding dimension from first vector and creates vec0 table.
        """
        await self._ensure_initialized()
        # Lazy vec0 creation: create table with actual dimension from embedding chain
        if vector:
            await self._ensure_vec_table(len(vector))
        
        point_uuid = id or str(uuid.uuid4())
        timestamp = str(metadata.get("timestamp", time.time()))
        session_id = metadata.get("session_id", "unknown")
        role = metadata.get("role", "unknown")
        content = metadata.get("content", "")
        
        # Serialize embedding to blob
        embedding_blob = sqlite_vec_serialize_float32(vector) if vector else None
        
        async with self._write_lock:
            # Exponential backoff for SQLITE_BUSY
            for attempt in range(3):
                try:
                    def _sync_upsert():
                        conn = self._get_conn()
                        
                        # CRITICAL: BEGIN IMMEDIATE prevents SQLITE_BUSY_SNAPSHOT
                        # (Researcher finding: busy_timeout does NOT cover snapshot conflicts)
                        conn.execute("BEGIN IMMEDIATE")
                        
                        # 1. Insert into metadata table (gets auto-incremented rowid)
                        cursor = conn.execute("""
                            INSERT INTO omega_memory_data
                            (uuid, entity_name, session_id, role, content, timestamp, metadata_json)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            point_uuid,
                            entity_name,
                            session_id,
                            role,
                            content,
                            timestamp,
                            json.dumps(metadata, default=str),
                        ))
                        rowid = cursor.lastrowid
                        
                        # 2. Insert into FTS5 with explicit rowid (matches metadata)
                        conn.execute("""
                            INSERT INTO omega_memory_fts(rowid, content, entity_name, session_id, role, timestamp)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (rowid, content, entity_name, session_id, role, timestamp))
                        
                        # 3. Insert into vec0 with explicit rowid (matches metadata)
                        # Correction C3: entity_name is partition key
                        if vector and embedding_blob:
                            conn.execute("""
                                INSERT INTO omega_memory_vec(rowid, embedding, entity_name)
                                VALUES (?, ?, ?)
                            """, (rowid, embedding_blob, entity_name))
                        
                        conn.commit()
                        return rowid
                    
                    await anyio.to_thread.run_sync(_sync_upsert)
                    return point_uuid
                    
                except sqlite3.OperationalError as e:
                    if "SQLITE_BUSY" in str(e) and attempt < 2:
                        # Exponential backoff: 50ms, 100ms, 200ms
                        delay = 0.05 * (2 ** attempt)
                        logger.warning(
                            "SQLITE_BUSY on upsert (attempt %d), retrying in %sms",
                            attempt + 1, delay * 1000
                        )
                        await anyio.sleep(delay)
                        continue
                    raise ProviderError(
                        "sqlite_vec",
                        f"SQLite-vec upsert failed: {e}",
                        raw_error=e
                    ) from e
                except (sqlite3.Error, OSError) as e:
                    logger.error("SQLite-vec upsert failed: %s", e, exc_info=True)
                    raise ProviderError(
                        "sqlite_vec",
                        f"SQLite-vec upsert failed: {e}",
                        raw_error=e
                    ) from e

    async def query(
        self,
        entity_name: str,
        vector: List[float],
        limit: int = 10,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[float, Dict[str, Any]]]:
        """Query the vector store for the most similar entries.
        
        Returns list of (score, metadata) tuples, sorted by score descending.
        Score is cosine similarity (1 - cosine_distance).
        """
        await self._ensure_initialized()
        
        if not vector:
            return []
        
        # If vec0 table doesn't exist yet (no upserts), return empty
        if not self._vec_table_created:
            return []
        
        try:
            def _sync_query():
                conn = self._get_conn()
                
                # Query vec0 with entity_name partition key (Correction C3)
                embedding_blob = sqlite_vec_serialize_float32(vector)
                
                # Use vec0 KNN search with partition key
                cursor = conn.execute("""
                    SELECT rowid, distance
                    FROM omega_memory_vec
                    WHERE embedding MATCH ? AND entity_name = ?
                    ORDER BY distance
                    LIMIT ?
                """, (embedding_blob, entity_name, limit))
                
                results = []
                for row in cursor.fetchall():
                    rowid = row[0]
                    distance = row[1]
                    # Convert distance to similarity score (1 - cosine_distance)
                    score = 1.0 - distance
                    
                    # Get metadata from the data table (O(1) join by rowid)
                    meta_cursor = conn.execute("""
                        SELECT uuid, entity_name, session_id, role, content, timestamp, metadata_json
                        FROM omega_memory_data
                        WHERE id = ?
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
                        # Parse additional metadata from JSON
                        if meta_row[6]:
                            try:
                                extra = json.loads(meta_row[6])
                                metadata.update(extra)
                            except json.JSONDecodeError:
                                pass
                        
                        results.append((score, metadata))
                
                return results
            
            return await anyio.to_thread.run_sync(_sync_query)
            
        except (sqlite3.Error, OSError) as e:
            logger.error("SQLite-vec query failed: %s", e, exc_info=True)
            raise ProviderError(
                "sqlite_vec",
                f"SQLite-vec query failed: {e}",
                raw_error=e
            ) from e

    async def delete(self, entity_name: str, ids: List[str]) -> bool:
        """Delete specific vectors by UUID.
        
        Args:
            entity_name: The entity that owns the vectors.
            ids: List of UUID strings to delete.
        """
        if not ids:
            return False
        
        await self._ensure_initialized()
        
        async with self._write_lock:
            try:
                def _sync_delete():
                    conn = self._get_conn()
                    deleted_any = False
                    
                    # CRITICAL: BEGIN IMMEDIATE prevents SQLITE_BUSY_SNAPSHOT
                    conn.execute("BEGIN IMMEDIATE")
                    
                    for uuid_str in ids:
                        # Find rowid by UUID
                        cursor = conn.execute(
                            "SELECT id FROM omega_memory_data WHERE uuid = ? AND entity_name = ?",
                            (uuid_str, entity_name)
                        )
                        row = cursor.fetchone()
                        if not row:
                            continue
                        
                        rowid = row[0]
                        
                        # Delete from all three tables
                        conn.execute("DELETE FROM omega_memory_data WHERE id = ?", (rowid,))
                        conn.execute("DELETE FROM omega_memory_fts WHERE rowid = ?", (rowid,))
                        conn.execute("DELETE FROM omega_memory_vec WHERE rowid = ?", (rowid,))
                        deleted_any = True
                    
                    conn.commit()
                    return deleted_any
                
                return await anyio.to_thread.run_sync(_sync_delete)
                
            except (sqlite3.Error, OSError) as e:
                logger.error("SQLite-vec delete failed: %s", e, exc_info=True)
                raise ProviderError(
                    "sqlite_vec",
                    f"SQLite-vec delete failed: {e}",
                    raw_error=e
                ) from e

    async def delete_session(self, entity_name: str, session_id: str) -> bool:
        """Delete all vectors associated with a specific session."""
        await self._ensure_initialized()
        
        async with self._write_lock:
            try:
                def _sync_delete_session():
                    conn = self._get_conn()
                    
                    # CRITICAL: BEGIN IMMEDIATE prevents SQLITE_BUSY_SNAPSHOT
                    conn.execute("BEGIN IMMEDIATE")
                    
                    # Find all rowids for this session
                    cursor = conn.execute("""
                        SELECT id FROM omega_memory_data
                        WHERE entity_name = ? AND session_id = ?
                    """, (entity_name, session_id))
                    
                    rowids = [row[0] for row in cursor.fetchall()]
                    if not rowids:
                        return False
                    
                    # Delete from all three tables
                    placeholders = ",".join("?" for _ in rowids)
                    conn.execute(f"DELETE FROM omega_memory_data WHERE id IN ({placeholders})", rowids)
                    conn.execute(f"DELETE FROM omega_memory_fts WHERE rowid IN ({placeholders})", rowids)
                    conn.execute(f"DELETE FROM omega_memory_vec WHERE rowid IN ({placeholders})", rowids)
                    
                    conn.commit()
                    return True
                
                return await anyio.to_thread.run_sync(_sync_delete_session)
                
            except (sqlite3.Error, OSError) as e:
                logger.error("SQLite-vec delete_session failed: %s", e, exc_info=True)
                raise ProviderError(
                    "sqlite_vec",
                    f"SQLite-vec delete_session failed: {e}",
                    raw_error=e
                ) from e

    async def get_status(self) -> Dict[str, Any]:
        """Get the current health and status of the vector store."""
        try:
            await self._ensure_initialized()
            
            def _sync_status():
                conn = self._get_conn()
                
                # Count rows in data table
                try:
                    data_count = conn.execute(
                        "SELECT COUNT(*) FROM omega_memory_data"
                    ).fetchone()[0]
                except sqlite3.Error:
                    data_count = 0
                
                # Count FTS entries
                try:
                    fts_count = conn.execute(
                        "SELECT COUNT(*) FROM omega_memory_fts"
                    ).fetchone()[0]
                except sqlite3.Error:
                    fts_count = 0
                
                # Count vec entries
                try:
                    vec_count = conn.execute(
                        "SELECT COUNT(*) FROM omega_memory_vec"
                    ).fetchone()[0]
                except sqlite3.Error:
                    vec_count = 0
                
                # Get distinct entities
                try:
                    entities = conn.execute(
                        "SELECT DISTINCT entity_name FROM omega_memory_data"
                    ).fetchall()
                    entity_count = len(entities)
                except sqlite3.Error:
                    entity_count = 0
                
                return {
                    "status": "healthy",
                    "type": "sqlite-vec-unified-fabric",
                    "db_path": str(self.db_path),
                    "embedding_dim": self._embedding_dim,
                    "vector_count": vec_count,
                    "fts_count": fts_count,
                    "metadata_count": data_count,
                    "entity_count": entity_count,
                }
            
            return await anyio.to_thread.run_sync(_sync_status)
            
        except (sqlite3.Error, OSError) as e:
            return {"status": "unhealthy", "error": str(e)}

    async def hybrid_search(
        self,
        query: str,
        entity_name: str,
        vector: List[float],
        limit: int = 20,
        fts_weight: float = 0.5,
        vec_weight: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """Hybrid search combining FTS5 and vec0 with Reciprocal Rank Fusion.
        
        This method is called by MemoryStore.search() to fuse FTS and vector results.
        Uses HybridSearchEngine for unified RRF fusion (k=60).
        
        Correction C6: Python-side RRF fusion via HybridSearchEngine.
        """
        await self._ensure_initialized()
        
        if not query.strip() and not vector:
            return []
        
        # 1. Fetch FTS results
        fts_results: List[Dict[str, Any]] = []
        if query.strip():
            try:
                def _sync_fts():
                    conn = self._get_conn()
                    cursor = conn.execute("""
                        SELECT rowid, session_id, role, content, timestamp
                        FROM omega_memory_fts
                        WHERE omega_memory_fts MATCH ? AND entity_name = ?
                        ORDER BY rank
                        LIMIT ?
                    """, (query, entity_name, limit * 2))
                    
                    results = []
                    for row in cursor.fetchall():
                        metadata = {
                            "rowid": row[0],
                            "entity_name": entity_name,
                            "session_id": row[1],
                            "role": row[2],
                            "content": row[3],
                            "timestamp": row[4],
                        }
                        results.append(metadata)
                    return results
                
                fts_results = await anyio.to_thread.run_sync(_sync_fts)
            except (sqlite3.Error, OSError) as e:
                logger.warning("FTS search failed: %s", e)
        
        # 2. Fetch vector results
        vec_results: List[Tuple[float, Dict[str, Any]]] = []
        if vector:
            try:
                vec_results = await self.query(
                    entity_name=entity_name,
                    vector=vector,
                    limit=limit * 2,
                )
            except (ProviderError, RuntimeError) as e:
                logger.warning("Vector search failed: %s", e)
        
        # 3. Apply Reciprocal Rank Fusion (RRF) via HybridSearchEngine
        # RRF formula: score = sum( weight / (k + rank) ) with k=60
        engine = HybridSearchEngine(k=60)
        
        # Convert FTS results to FTSResult objects
        fts_objects = []
        for i, r in enumerate(fts_results):
            doc_id = f"{r.get('session_id', '')}:{r.get('timestamp', '')}"
            fts_objects.append(FTSResult(
                doc_id=doc_id,
                rank=i + 1,
                metadata=r,
            ))
        
        # Convert vector results to VecResult objects
        vec_objects = []
        for i, (score, payload) in enumerate(vec_results):
            doc_id = f"{payload.get('session_id', '')}:{payload.get('timestamp', '')}"
            vec_objects.append(VecResult(
                doc_id=doc_id,
                rank=i + 1,
                score=score,
                metadata=payload,
            ))
        
        # Fuse using HybridSearchEngine
        fused_results = engine.fuse(
            fts_objects, vec_objects,
            limit=limit,
            fts_weight=fts_weight,
            vec_weight=vec_weight,
        )
        
        # 4. Final results construction (convert to dict format for compatibility)
        final_results = []
        for result in fused_results:
            doc = result.metadata.copy()
            doc["_rrf_score"] = result.fused_score
            doc["_source_rank_fts"] = result.source_rank_fts
            doc["_source_rank_vec"] = result.source_rank_vec
            final_results.append(doc)
        
        return final_results

    async def checkpoint_wal(self, mode: str = "RESTART") -> bool:
        """Force a WAL checkpoint to prevent checkpoint starvation.
        
        Args:
            mode: Checkpoint mode - "PASSIVE", "FULL", or "RESTART".
                  RESTART is recommended for production to ensure clean checkpoint.
        
        Returns:
            True if checkpoint succeeded, False if blocked by active readers.
        """
        await self._ensure_initialized()
        
        def _sync_checkpoint():
            conn = self._get_conn()
            cursor = conn.execute(f"PRAGMA wal_checkpoint({mode})")
            result = cursor.fetchone()
            # result: (busy, log, checkpointed)
            # busy=0 means checkpoint completed
            return result[0] == 0
        
        return await anyio.to_thread.run_sync(_sync_checkpoint)

    async def check_wal_health(self) -> dict:
        """Check WAL file health - size, checkpoint status, and potential issues.
        
        Returns:
            Dict with WAL health metrics for monitoring/alerting.
        """
        await self._ensure_initialized()
        
        def _sync_wal_health():
            conn = self._get_conn()
            health = {}
            
            # WAL file size
            wal_path = self.db_path.with_suffix(".db-wal")
            if wal_path.exists():
                health["wal_size_bytes"] = wal_path.stat().st_size
                health["wal_size_mb"] = round(health["wal_size_bytes"] / (1024 * 1024), 2)
            else:
                health["wal_size_bytes"] = 0
                health["wal_size_mb"] = 0.0
            
            # Checkpoint status
            cursor = conn.execute("PRAGMA wal_checkpoint(PASSIVE)")
            result = cursor.fetchone()
            health["checkpoint_busy"] = result[0]  # 0 = not busy, 1 = busy
            health["checkpoint_log_frames"] = result[1]
            health["checkpoint_checkpointed_frames"] = result[2]
            
            # Journal size limit
            cursor = conn.execute("PRAGMA journal_size_limit")
            health["journal_size_limit"] = cursor.fetchone()[0]
            
            # WAL autocheckpoint
            cursor = conn.execute("PRAGMA wal_autocheckpoint")
            health["wal_autocheckpoint"] = cursor.fetchone()[0]
            
            # Health assessment
            health["healthy"] = (
                health["wal_size_mb"] < 50 and  # Alert at 50MB
                health["checkpoint_busy"] == 0
            )
            
            return health
        
        return await anyio.to_thread.run_sync(_sync_wal_health)

    async def start_periodic_checkpoint(self, interval_seconds: int = 300) -> None:
        """Start a background task that runs periodic RESTART checkpoints.
        
        This prevents checkpoint starvation under sustained reader load.
        Call this once at application startup.
        
        Args:
            interval_seconds: Interval between checkpoints (default 5 minutes).
        """
        if hasattr(self, "_checkpoint_task") and self._checkpoint_task:
            logger.warning("Periodic checkpoint task already running")
            return
        
        async def _checkpoint_loop():
            while True:
                try:
                    await anyio.sleep(interval_seconds)
                    success = await self.checkpoint_wal("RESTART")
                    if success:
                        logger.debug("Periodic RESTART checkpoint completed")
                    else:
                        logger.warning("Periodic RESTART checkpoint blocked by active readers")
                except Exception as e:
                    logger.error("Periodic checkpoint task error: %s", e)
        
        self._checkpoint_task = anyio.create_task_group()
        self._checkpoint_task.start_soon(_checkpoint_loop)
        logger.info("Started periodic WAL checkpoint task (interval=%ds)", interval_seconds)

    async def stop_periodic_checkpoint(self) -> None:
        """Stop the periodic checkpoint task."""
        if hasattr(self, "_checkpoint_task") and self._checkpoint_task:
            self._checkpoint_task.cancel_scope.cancel()
            self._checkpoint_task = None
            logger.info("Stopped periodic WAL checkpoint task")

    async def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            try:
                self._conn.close()
            except (sqlite3.Error, OSError):
                pass
            self._conn = None
            self._initialized = False
            logger.info("SQLiteVecAdapter closed")


def sqlite_vec_serialize_float32(vector: List[float]) -> bytes:
    """Serialize a list of floats to bytes for sqlite-vec.
    
    Uses sqlite_vec's built-in serialization if available,
    otherwise falls back to manual packing.
    """
    try:
        import sqlite_vec
        return sqlite_vec.serialize_float32(vector)
    except ImportError:
        # Fallback: manual serialization
        import struct
        return struct.pack(f'{len(vector)}f', *vector)
