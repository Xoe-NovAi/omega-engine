"""SQLite-vec Unified Memory Fabric Adapter for Omega Memory.
AP: AP-SQLITEVEC-ADAPTER-v2.0.0

Canonical Embedding Strategy: 768-dim locked, multi-collection architecture.
One `omega_memory.db` (FTS5 + multiple vec0 collections + SQL graph edges).

Implements IVectorStoreAdapter interface using sqlite-vec for vector search
and FTS5 for full-text search, with Reciprocal Rank Fusion in Python.

Corrections applied from Jem's R_SQLITEVEC_VERIFICATION_20260712.md:
- C3: Sovereign Isolation via entity_name TEXT partition key
- Class Overwrite Hazard: ADD a tier, never redefine the class
- Write Contention: anyio.Lock + exponential backoff (50/100/200ms)
- RRF Unification: Python-side RRF fusion (reuse existing search() logic)

NEW: Canonical dimension enforcement (M23 Failure Integrity)
NEW: Multi-collection vec0 architecture (per-model isolation)
NEW: INT8 rescore quantization support
"""
# [heritage: sqlite-fts5 2015] SQLite FTS5 — BM25 full-text search with Porter stemmer
# [heritage: sqlite-vec 2024] sqlite-vec — vector similarity search extension
# [id-soft: doom-1993] Precomputed Lookup — embedding cache integrity

import json
import logging
import os
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import anyio

from .vector_adapters import IVectorStoreAdapter
from omega.errors import ProviderError, ProviderUnavailableError
from omega.infra.sqlite_policy import get_sqlite_connection

logger = logging.getLogger(__name__)

# ============================================================================
# CANONICAL EMBEDDING STRATEGY — HARDCODED, DO NOT CHANGE
# Source: docs/strategy/EMBEDDING_HARDENING_STRATEGY_20260720.md
# ============================================================================

# Canonical dimension — ALL primary providers MUST output 768-dim vectors
# EmbeddingGemma 300M (primary), nomic-embed-text-v1.5 (fallback) both native 768
CANONICAL_DIMENSION = 768

# Supported MRL dimensions for fallback tiers
MRL_DIMENSIONS = [768, 512, 256, 128, 64]

# Collection definitions — each gets its own vec0 table
COLLECTIONS = {
    # Primary: EmbeddingGemma 300M at canonical 768-dim
    "omega_vec_gemma_768": {
        "dimension": 768,
        "metric": "cosine",
        "quantization": "int8_rescore",
        "hnsw": {"m": 16, "ef_construction": 200, "ef_search": 64},
    },
    # Fallback: Nomic v1.5 at canonical 768-dim
    "omega_vec_nomic_768": {
        "dimension": 768,
        "metric": "cosine",
        "quantization": "int8_rescore",
        "hnsw": {"m": 16, "ef_construction": 200, "ef_search": 64},
    },
    # MRL tiers: Nomic truncated (separate collections for each dim)
    "omega_vec_nomic_512": {
        "dimension": 512,
        "metric": "cosine",
        "quantization": "int8_rescore",
        "hnsw": {"m": 16, "ef_construction": 200, "ef_search": 64},
    },
    "omega_vec_nomic_256": {
        "dimension": 256,
        "metric": "cosine",
        "quantization": "int8_rescore",
        "hnsw": {"m": 16, "ef_construction": 200, "ef_search": 64},
    },
    # Speed: MiniLM 384-dim (no MRL, separate collection)
    "omega_vec_minilm_384": {
        "dimension": 384,
        "metric": "cosine",
        "quantization": "none",
        "hnsw": {"m": 16, "ef_construction": 200, "ef_search": 64},
    },
    # Zero-cost: Static 64-dim
    "omega_vec_static_64": {
        "dimension": 64,
        "metric": "cosine",
        "quantization": "none",
        "hnsw": {"m": 16, "ef_construction": 200, "ef_search": 64},
    },
    # Library feature-hashing: 256-dim (simple bag-of-words, not ML embeddings)
    "omega_vec_library_256": {
        "dimension": 256,
        "metric": "cosine",
        "quantization": "none",
        "hnsw": {"m": 16, "ef_construction": 200, "ef_search": 64},
    },
}

# Legacy default (for backward compat during migration)
DEFAULT_EMBEDDING_DIM = CANONICAL_DIMENSION


class SQLiteVecAdapter(IVectorStoreAdapter):
    """Unified memory fabric: FTS5 + multiple vec0 collections + SQL graph.

    Canonical Architecture:
    - One SQLite file: omega_memory.db
    - FTS5: omega_memory_fts (full-text search)
    - vec0: Multiple collections per embedding model/dimension
    - SQL: omega_memory_data (metadata), omega_memory_graph (edges)

    Canonical Dimension Enforcement (M23):
    - Primary providers (Gemma, Nomic) MUST output 768-dim vectors
    - Vec0 tables locked to their declared dimension
    - Dimension mismatch raises RuntimeError (not silent corruption)
    """

    def __init__(
        self,
        db_path: Optional[str] = None,
        embedding_dim: int = DEFAULT_EMBEDDING_DIM,
        collections: Optional[Dict[str, Dict]] = None,
        timeout: float = 5.0,
    ):
        # Use OMEGA_DATA_DIR if db_path not explicitly provided
        if db_path is None:
            data_dir = Path(os.environ.get("OMEGA_DATA_DIR", str(Path.home() / "omega" / "data")))
            db_path = str(data_dir / "omega_memory.db")

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Canonical dimension lock
        self._canonical_dim = CANONICAL_DIMENSION
        self._embedding_dim = embedding_dim  # Legacy compat

        # Multi-collection support
        self._collections = collections or COLLECTIONS
        self._vec_tables_created: Dict[str, bool] = {}

        # Connection & locks
        self._conn: Optional[sqlite3.Connection] = None
        self._write_lock = anyio.Lock()
        self._initialized = False
        self.timeout = timeout

        # Legacy vec0 table name (for backward compat during migration)
        self._legacy_vec_table = "omega_memory_vec"
        self._legacy_vec_created = False

    def _get_conn(self) -> sqlite3.Connection:
        """Get the persistent SQLite connection with hardened PRAGMA stack and vec0 extension.

        Connection is created once and reused across all operations (M1 AnyIO).
        Uses sqlite_policy memory profile (D-282 PRAGMA stack is law per A10).
        """
        if self._conn is not None:
            return self._conn

        # FS-Β4: Use sqlite_policy for profiled connection (memory profile)
        conn = get_sqlite_connection(self.db_path, profile="memory")

        # Load sqlite-vec extension for this connection
        try:
            import sqlite_vec

            conn.enable_load_extension(True)
            sqlite_vec.load(conn)
            conn.enable_load_extension(False)
        except ImportError:
            logger.error("sqlite-vec module not installed")
            raise
        except sqlite3.Error as e:
            logger.error("Failed to load sqlite-vec extension: %s", e)
            raise

        self._conn = conn
        return conn

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
                self.db_path,
                self._embedding_dim,
            )
        except (sqlite3.Error, OSError) as e:
            logger.error("Failed to initialize SQLiteVecAdapter: %s", e)
            raise ProviderUnavailableError(
                "sqlite_vec", f"SQLite-vec initialization failed: {e}", raw_error=e
            ) from e

    async def _ensure_collection_vec_table(self, collection_name: str, actual_dim: int) -> None:
        """Create or recreate vec0 table for a specific collection with STRICT dimension enforcement.

        Canonical Dimension Lock (M23 Failure Integrity):
        - Primary collections (gemma_primary, nomic_fallback) MUST use 768-dim
        - MRL tier collections use their declared dimension (512, 256, etc.)
        - Speed/zero-cost collections use their native dimension (384, 64)
        - Dimension mismatch raises RuntimeError — NO silent corruption

        Args:
            collection_name: Name of the collection (must be in self._collections)
            actual_dim: Actual dimension from embedding provider

        Raises:
            RuntimeError: If dimension doesn't match collection's declared dimension
        """
        if collection_name not in self._collections:
            raise ValueError(
                f"Unknown collection: {collection_name}. Valid: {list(self._collections.keys())}"
            )

        collection_config = self._collections[collection_name]
        declared_dim = collection_config["dimension"]

        # CANONICAL DIMENSION ENFORCEMENT
        if actual_dim != declared_dim:
            raise RuntimeError(
                f"EMBEDDING DIMENSION MISMATCH — CANONICAL VIOLATION (M23)\n"
                f"  Collection: {collection_name}\n"
                f"  Provider returned: {actual_dim}-dim vector\n"
                f"  Collection declared: {declared_dim}-dim\n"
                f"  Fix: Provider MUST output {declared_dim}-dim vectors.\n"
                f"  Use MRL truncation in provider.get_embedding() if needed."
            )

        # Already created with correct dimension
        if self._vec_tables_created.get(collection_name, False):
            return

        # Create the vec0 table for this collection
        # Collection names already include the prefix (e.g., "omega_vec_gemma_768")
        table_name = collection_name

        def _sync_create_vec():
            conn = self._get_conn()
            conn.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS {table_name}
                USING vec0(
                    embedding float[{declared_dim}] distance_metric=cosine,
                    entity_name TEXT partition key
                )
            """)
            conn.commit()

        await anyio.to_thread.run_sync(_sync_create_vec)
        self._vec_tables_created[collection_name] = True
        logger.info("vec0 collection '%s' created with dim=%d", collection_name, declared_dim)

    async def _ensure_legacy_vec_table(self, actual_dim: int) -> None:
        """Legacy vec0 table creation for backward compatibility during migration.

        DEPRECATED: Use _ensure_collection_vec_table() instead.
        Enforces canonical 768-dim for legacy table.
        """
        if self._legacy_vec_created and actual_dim == self._embedding_dim:
            return

        # Legacy table MUST be canonical dimension
        if actual_dim != CANONICAL_DIMENSION:
            raise RuntimeError(
                f"LEGACY VEC0 TABLE DIMENSION VIOLATION\n"
                f"  Legacy table 'omega_memory_vec' requires {CANONICAL_DIMENSION}-dim vectors.\n"
                f"  Provider returned: {actual_dim}-dim\n"
                f"  Migration required: Use collection-specific vec0 tables."
            )

        if self._legacy_vec_created and actual_dim != self._embedding_dim:
            logger.warning(
                "Legacy embedding dimension changed %d → %d. Recreating legacy vec0 table.",
                self._embedding_dim,
                actual_dim,
            )

            def _sync_drop():
                conn = self._get_conn()
                conn.execute("DROP TABLE IF EXISTS omega_memory_vec")
                conn.commit()

            await anyio.to_thread.run_sync(_sync_drop)
            self._legacy_vec_created = False

        def _sync_create_vec():
            conn = self._get_conn()
            conn.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS omega_memory_vec
                USING vec0(embedding float[{CANONICAL_DIMENSION}], entity_name TEXT partition key)
            """)
            conn.commit()

        await anyio.to_thread.run_sync(_sync_create_vec)
        self._embedding_dim = actual_dim
        self._legacy_vec_created = True
        logger.info("Legacy vec0 table created with canonical dim=%d", CANONICAL_DIMENSION)

    async def upsert(
        self,
        entity_name: str,
        vector: List[float],
        metadata: Dict[str, Any],
        id: Optional[str] = None,
        collection: str = "omega_vec_gemma_768",  # Default to primary canonical collection
    ) -> str:
        """Insert or update a vector and its metadata in a specific collection.

        Canonical Architecture:
        - Each collection has its own vec0 table with declared dimension
        - Dimension mismatch raises RuntimeError (M23 Failure Integrity)
        - Default collection: omega_vec_gemma_768 (canonical 768-dim)

        Args:
            entity_name: Sovereign entity identifier (partition key)
            vector: Embedding vector (MUST match collection's declared dimension)
            metadata: Document metadata (content, session_id, role, timestamp, etc.)
            id: Optional UUID (auto-generated if not provided)
            collection: Target collection name (must be in self._collections)

        Returns:
            UUID string identifier
        """
        await self._ensure_initialized()

        # Validate collection exists
        if collection not in self._collections:
            raise ValueError(
                f"Unknown collection: {collection}. Valid: {list(self._collections.keys())}"
            )

        # Lazy vec0 creation: create table with actual dimension from embedding
        if vector:
            await self._ensure_collection_vec_table(collection, len(vector))

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
                        conn.execute("BEGIN IMMEDIATE")

                        # 1. Insert into metadata table (gets auto-incremented rowid)
                        cursor = conn.execute(
                            """
                            INSERT INTO omega_memory_data
                            (uuid, entity_name, session_id, role, content, timestamp, metadata_json)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                            (
                                point_uuid,
                                entity_name,
                                session_id,
                                role,
                                content,
                                timestamp,
                                json.dumps(metadata, default=str),
                            ),
                        )
                        rowid = cursor.lastrowid

                        # 2. Insert into FTS5 with explicit rowid (matches metadata)
                        conn.execute(
                            """
                            INSERT INTO omega_memory_fts(rowid, content, entity_name, session_id, role, timestamp)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """,
                            (rowid, content, entity_name, session_id, role, timestamp),
                        )

                        # 3. Insert into COLLECTION-SPECIFIC vec0 with explicit rowid
                        # Correction C3: entity_name is partition key
                        # Collection names already include the prefix (e.g., "omega_vec_gemma_768")
                        if vector and embedding_blob:
                            table_name = collection
                            conn.execute(
                                f"""
                                INSERT INTO {table_name}(rowid, embedding, entity_name)
                                VALUES (?, ?, ?)
                            """,
                                (rowid, embedding_blob, entity_name),
                            )

                        conn.commit()
                        return rowid

                    await anyio.to_thread.run_sync(_sync_upsert)
                    return point_uuid

                except sqlite3.OperationalError as e:
                    if "SQLITE_BUSY" in str(e) and attempt < 2:
                        # Exponential backoff: 50ms, 100ms, 200ms
                        delay = 0.05 * (2**attempt)
                        logger.warning(
                            "SQLITE_BUSY on upsert (attempt %d), retrying in %sms",
                            attempt + 1,
                            delay * 1000,
                        )
                        await anyio.sleep(delay)
                        continue
                    raise ProviderError(
                        "sqlite_vec", f"SQLite-vec upsert failed: {e}", raw_error=e
                    ) from e
                except (sqlite3.Error, OSError) as e:
                    logger.error("SQLite-vec upsert failed: %s", e, exc_info=True)
                    raise ProviderError(
                        "sqlite_vec", f"SQLite-vec upsert failed: {e}", raw_error=e
                    ) from e

    async def query(
        self,
        entity_name: str,
        vector: List[float],
        limit: int = 10,
        filter: Optional[Dict[str, Any]] = None,
        collection: str = "omega_vec_gemma_768",  # Default to primary canonical collection
    ) -> List[Tuple[float, Dict[str, Any]]]:
        """Query a specific vec0 collection for the most similar entries.

        Args:
            entity_name: Entity partition key (sovereign isolation)
            vector: Query embedding vector
            limit: Maximum results to return
            filter: Optional metadata filters (not yet implemented)
            collection: Vec0 collection name (must be in COLLECTIONS)

        Returns:
            List of (score, metadata) tuples, sorted by score descending.
            Score is cosine similarity (1 - cosine_distance).

        Raises:
            ValueError: If collection not found or dimension mismatch
        """
        await self._ensure_initialized()

        if not vector:
            return []

        # Validate collection exists
        if collection not in self._collections:
            raise ValueError(
                f"Unknown collection: {collection}. Available: {list(self._collections.keys())}"
            )

        coll_config = self._collections[collection]
        expected_dim = coll_config["dimension"]

        # Canonical dimension enforcement
        if len(vector) != expected_dim:
            raise ValueError(
                f"VECTOR DIMENSION MISMATCH — CANONICAL VIOLATION\n"
                f"  Collection: {collection} (declared dim={expected_dim})\n"
                f"  Query vector: {len(vector)}-dim\n"
                f"  Fix: Provider MUST output {expected_dim}-dim vectors for this collection.\n"
                f"  Use MRL truncation in provider.get_embedding() if needed."
            )

        # Check if vec0 table for this collection exists
        if not self._vec_tables_created.get(collection, False):
            return []  # No data yet in this collection

        try:

            def _sync_query():
                conn = self._get_conn()

                # Query specific vec0 collection with entity_name partition key
                embedding_blob = sqlite_vec_serialize_float32(vector)

                cursor = conn.execute(
                    f"""
                    SELECT rowid, distance
                    FROM {collection}
                    WHERE embedding MATCH ? AND entity_name = ?
                    ORDER BY distance
                    LIMIT ?
                """,
                    (embedding_blob, entity_name, limit),
                )

                results = []
                for row in cursor.fetchall():
                    rowid = row[0]
                    distance = row[1]
                    # vec0 returns NULL distance for rows in non-matching partitions
                    if distance is None:
                        continue
                    score = 1.0 - distance

                    # Get metadata from the data table (O(1) join by rowid)
                    meta_cursor = conn.execute(
                        """
                        SELECT uuid, entity_name, session_id, role, content, timestamp, metadata_json
                        FROM omega_memory_data
                        WHERE id = ?
                    """,
                        (rowid,),
                    )
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
            logger.error(
                "SQLite-vec query failed for collection %s: %s", collection, e, exc_info=True
            )
            raise ProviderError("sqlite_vec", f"SQLite-vec query failed: {e}", raw_error=e) from e

    async def delete(
        self, entity_name: str, ids: List[str], collection: str = "omega_vec_gemma_768"
    ) -> bool:
        """Delete specific vectors by UUID.

        Args:
            entity_name: The entity that owns the vectors.
            ids: List of UUID strings to delete.
            collection: Target collection name (must be in self._collections).

        [FIX P0-2 / audit r2 §2] The ABC signature (IVectorStoreAdapter.delete)
        has no collection param, so callers (MemoryStore, SelectiveHydration,
        Indexer) always hit the default collection. A vector may have been
        upserted into ANY created collection. rowid is scoped to exactly one
        vec0 table per upsert() call, so issuing DELETE against every created
        collection is safe — at most one matches, the rest are no-ops.
        Table names come from self._vec_tables_created keys (derived from the
        hardcoded COLLECTIONS dict, not user input) — no injection risk.
        """
        if not ids:
            return False

        if collection not in self._collections:
            raise ValueError(
                f"Unknown collection: {collection}. Valid: {list(self._collections.keys())}"
            )

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
                            (uuid_str, entity_name),
                        )
                        row = cursor.fetchone()
                        if not row:
                            continue

                        rowid = row[0]

                        # Delete from data + FTS tables
                        conn.execute("DELETE FROM omega_memory_data WHERE id = ?", (rowid,))
                        conn.execute("DELETE FROM omega_memory_fts WHERE rowid = ?", (rowid,))
                        # [FIX P0-2] Delete from EVERY created vec0 collection —
                        # rowid is scoped to exactly one, rest are no-op DELETEs.
                        for collection_name in self._vec_tables_created:
                            conn.execute(f"DELETE FROM {collection_name} WHERE rowid = ?", (rowid,))
                        deleted_any = True

                    conn.commit()
                    return deleted_any

                return await anyio.to_thread.run_sync(_sync_delete)

            except (sqlite3.Error, OSError) as e:
                logger.error("SQLite-vec delete failed: %s", e, exc_info=True)
                raise ProviderError(
                    "sqlite_vec", f"SQLite-vec delete failed: {e}", raw_error=e
                ) from e

    async def delete_session(
        self, entity_name: str, session_id: str, collection: str = "omega_vec_gemma_768"
    ) -> bool:
        """Delete all vectors associated with a specific session.

        Args:
            entity_name: The entity that owns the vectors.
            session_id: Session identifier.
            collection: Target collection name (must be in self._collections).

        [FIX P0-2 / audit r2 §2] Same multi-collection issue as delete(): the
        ABC signature (IVectorStoreAdapter.delete_session) has no collection
        param, so callers (MemoryStore) always hit the default collection.
        A session's vectors may live in ANY created vec0 collection. rowid is
        scoped to exactly one vec0 table per upsert() call, so issuing DELETE
        against every created collection is safe — at most one matches, the
        rest are no-ops. Table names come from self._vec_tables_created keys
        (derived from the hardcoded COLLECTIONS dict, not user input).
        """
        if collection not in self._collections:
            raise ValueError(
                f"Unknown collection: {collection}. Valid: {list(self._collections.keys())}"
            )

        await self._ensure_initialized()

        async with self._write_lock:
            try:

                def _sync_delete_session():
                    conn = self._get_conn()

                    # CRITICAL: BEGIN IMMEDIATE prevents SQLITE_BUSY_SNAPSHOT
                    conn.execute("BEGIN IMMEDIATE")

                    # Find all rowids for this session
                    cursor = conn.execute(
                        """
                        SELECT id FROM omega_memory_data
                        WHERE entity_name = ? AND session_id = ?
                    """,
                        (entity_name, session_id),
                    )

                    rowids = [row[0] for row in cursor.fetchall()]
                    if not rowids:
                        return False

                    # Delete from data + FTS tables
                    placeholders = ",".join("?" for _ in rowids)
                    conn.execute(
                        f"DELETE FROM omega_memory_data WHERE id IN ({placeholders})", rowids
                    )
                    conn.execute(
                        f"DELETE FROM omega_memory_fts WHERE rowid IN ({placeholders})", rowids
                    )
                    # [FIX P0-2] Delete from EVERY created vec0 collection —
                    # rowids are scoped to exactly one, rest are no-op DELETEs.
                    for collection_name in self._vec_tables_created:
                        conn.execute(
                            f"DELETE FROM {collection_name} WHERE rowid IN ({placeholders})",
                            rowids,
                        )

                    conn.commit()
                    return True

                return await anyio.to_thread.run_sync(_sync_delete_session)

            except (sqlite3.Error, OSError) as e:
                logger.error("SQLite-vec delete_session failed: %s", e, exc_info=True)
                raise ProviderError(
                    "sqlite_vec", f"SQLite-vec delete_session failed: {e}", raw_error=e
                ) from e

    async def get_status(self) -> Dict[str, Any]:
        """Get the current health and status of the vector store."""
        try:
            await self._ensure_initialized()

            def _sync_status():
                conn = self._get_conn()

                # Count rows in data table
                try:
                    data_count = conn.execute("SELECT COUNT(*) FROM omega_memory_data").fetchone()[
                        0
                    ]
                except sqlite3.Error:
                    data_count = 0

                # Count FTS entries
                try:
                    fts_count = conn.execute("SELECT COUNT(*) FROM omega_memory_fts").fetchone()[0]
                except sqlite3.Error:
                    fts_count = 0

                # Count vec entries
                try:
                    vec_count = conn.execute("SELECT COUNT(*) FROM omega_memory_vec").fetchone()[0]
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
                    "canonical_dimension": self._canonical_dim,
                    "strategy_dimension": self._embedding_dim,
                    "dimension_match": self._canonical_dim == self._embedding_dim,
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
        """Hybrid search combining FTS5 and vec0 with Reciprocal Rank Fusion."""
        await self._ensure_initialized()

        if not query.strip() and not vector:
            return []

        from .hybrid_search import fetch_and_fuse

        async def _fts_fetch() -> List[Dict[str, Any]]:
            if not query.strip():
                return []

            def _sync_fts():
                conn = self._get_conn()
                # [P2-6] Escape user query to prevent FTS5 MATCH syntax injection.
                from .fts_index import escape_fts_query

                fts_query = escape_fts_query(query)
                cursor = conn.execute(
                    """
                    SELECT rowid, session_id, role, content, timestamp
                    FROM omega_memory_fts
                    WHERE omega_memory_fts MATCH ? AND entity_name = ?
                    ORDER BY rank
                    LIMIT ?
                """,
                    (fts_query, entity_name, limit * 2),
                )
                return [
                    {
                        "rowid": row[0],
                        "entity_name": entity_name,
                        "session_id": row[1],
                        "role": row[2],
                        "content": row[3],
                        "timestamp": row[4],
                    }
                    for row in cursor.fetchall()
                ]

            try:
                return await anyio.to_thread.run_sync(_sync_fts)
            except sqlite3.OperationalError as e:
                # FTS5 syntax error from a malformed query — degrade gracefully.
                logger.warning("FTS5 query syntax error (degraded): %s", e)
                return []
            except (sqlite3.Error, OSError) as e:
                logger.warning("FTS search failed: %s", e)
                return []

        async def _vec_fetch() -> List[tuple]:
            if not vector:
                return []
            try:
                return await self.query(entity_name=entity_name, vector=vector, limit=limit * 2)
            except (ProviderError, RuntimeError) as e:
                logger.warning("Vector search failed: %s", e)
                return []

        fused = await fetch_and_fuse(
            fts_fetch=_fts_fetch,
            vec_fetch=_vec_fetch,
            limit=limit,
            fts_weight=fts_weight,
            vec_weight=vec_weight,
        )

        final_results = []
        for result in fused:
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
                health["wal_size_mb"] < 50  # Alert at 50MB
                and health["checkpoint_busy"] == 0
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

    def _get_test_conn(self) -> sqlite3.Connection:
        """Get a connection for testing purposes.

        Returns the persistent connection if available, otherwise creates a new one.
        """
        if self._conn is not None:
            return self._conn
        return self._get_conn()

    async def close(self) -> None:
        """Close the database connection and release resources."""
        if self._conn is not None:
            try:
                await anyio.to_thread.run_sync(self._conn.close)
            except (sqlite3.Error, OSError) as e:
                logger.warning("Error closing SQLiteVecAdapter connection: %s", e)
            self._conn = None
        self._initialized = False
        self._vec_tables_created.clear()
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

        return struct.pack(f"{len(vector)}f", *vector)
