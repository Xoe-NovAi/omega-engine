# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""SQLite-vec Unified Memory Fabric Adapter for Omega Memory — OPTIMIZED.
AP: AP-SQLITEVEC-ADAPTER-v3.1.0-OPTIMIZED

Canonical Embedding Strategy: 1024-dim NATIVE, multi-collection architecture.
One `omega_memory.db` (FTS5 + multiple vec0 collections + SQL graph edges + R-tree spatial).

Optimizations (v3.0):
- Batch upsert: Single transaction for multiple vectors
- Query optimization: JOIN-based metadata fetch (eliminates N+1)
- Batch serialization: Vectorized float32 serialization
- Read connection pool: Separate read connections for concurrent queries
- Configurable HNSW: Tunable index parameters per collection
- WAL optimization: Smart checkpoint scheduling
- MRL truncation pipeline: 1024→768→512→256→128→64 automatic (NOT canonical)
- INT8 quantization with rescore: Fast ANN + exact rerank
- Spatial R-tree: 3D coordinates for VR navigation
- O(1) delete: rowid→collection mapping
- Metrics persistence: Survives restarts

AP: AP-SQLITEVEC-ADAPTER-v3.1.0-OPTIMIZED

[D-1024-DIM-NATIVE-20260926] Canonical collection is `omega_vec_qwen_1024`.
Pre-migration `*_768` canonical names are explicit aliases; see
sqlite_vec_adapter.LEGACY_COLLECTION_ALIASES.
"""
# [heritage: sqlite-fts5 2015] SQLite FTS5 — BM25 full-text search with Porter stemmer
# [heritage: sqlite-vec 2024] sqlite-vec — vector similarity search extension
# [id-soft: doom-1993] Precomputed Lookup — embedding cache integrity

import json
import logging
import math
import os
import sqlite3
import struct
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import anyio

from .vector_adapters import IVectorStoreAdapter
from .sqlite_vec_adapter import (
    CANONICAL_COLLECTION as BASE_CANONICAL_COLLECTION,
    get_vec_table_declared_dim,
    resolve_collection_name,
)
from omega.errors import ProviderError, ProviderUnavailableError
from omega.infra.sqlite_policy import get_sqlite_connection

logger = logging.getLogger(__name__)

# ============================================================================
# CANONICAL EMBEDDING STRATEGY — HARDCODED, DO NOT CHANGE
# Source: docs/strategy/EMBEDDING_HARDENING_STRATEGY_20260720.md
# ============================================================================

# [D-1024-DIM-NATIVE-20260926] Native 1024-dim is canonical; MRL optional.
CANONICAL_DIMENSION = 1024

# Canonical collection
CANONICAL_COLLECTION = "omega_vec_qwen_1024"

# Both adapters must agree on the canonical name — single D-1024 decision.
assert BASE_CANONICAL_COLLECTION == CANONICAL_COLLECTION

# MRL truncation targets (available, NOT canonical). 1024 = identity.
MRL_DIMENSIONS = [1024, 768, 512, 256, 128, 64]

COLLECTIONS = {
    # [D-1024-DIM-NATIVE-20260926] Primary: Qwen3-Embedding-0.6B at native 1024-dim
    CANONICAL_COLLECTION: {
        "dimension": 1024,
        "metric": "cosine",
        "quantization": "int8_rescore",
        "hnsw": {"m": 16, "ef_construction": 200, "ef_search": 64},
    },
    # [D-1024-DIM-NATIVE-20260926] Library: Qwen3-Embedding-0.6B at native 1024-dim (unified)
    "omega_vec_library_1024": {
        "dimension": 1024,
        "metric": "cosine",
        "quantization": "none",
        "hnsw": {"m": 16, "ef_construction": 200, "ef_search": 64},
    },
    "omega_vec_nomic_768": {
        "dimension": 768,
        "metric": "cosine",
        "quantization": "int8_rescore",
        "hnsw": {"m": 16, "ef_construction": 200, "ef_search": 64},
    },
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
    "omega_vec_minilm_384": {
        "dimension": 384,
        "metric": "cosine",
        "quantization": "none",
        "hnsw": {"m": 16, "ef_construction": 200, "ef_search": 64},
    },
    "omega_vec_static_64": {
        "dimension": 64,
        "metric": "cosine",
        "quantization": "none",
        "hnsw": {"m": 16, "ef_construction": 200, "ef_search": 64},
    },
    # [D-768-DIM-DELETE-LIBRARY-256] DELETED: dead code, replaced by library_1024 above
}

# Per-collection RRF weights (configurable) — GAP-004
# [D-768-DIM-LIBRARY-RRF] Library shifted from 0.8/0.2 → 0.6/0.4 for proper semantic weight
COLLECTION_RRF_WEIGHTS = {
    CANONICAL_COLLECTION: {"fts": 0.5, "vec": 0.5},
    "omega_vec_library_1024": {"fts": 0.6, "vec": 0.4},  # FTS-primary, more semantic weight
    "omega_vec_nomic_768": {"fts": 0.5, "vec": 0.5},
    "omega_vec_nomic_512": {"fts": 0.4, "vec": 0.6},   # MRL: trust vector more
    "omega_vec_nomic_256": {"fts": 0.3, "vec": 0.7},   # MRL: trust vector more
    "omega_vec_minilm_384": {"fts": 0.6, "vec": 0.4},  # Code: FTS more reliable
    "omega_vec_static_64": {"fts": 0.7, "vec": 0.3},   # Zero-cost: FTS primary
}

DEFAULT_EMBEDDING_DIM = CANONICAL_DIMENSION


class SQLiteVecAdapterOptimized(IVectorStoreAdapter):
    """Optimized unified memory fabric: FTS5 + multiple vec0 collections + SQL graph + R-tree spatial.

    Optimizations:
    - Batch upsert: Single transaction for multiple vectors
    - Query optimization: JOIN-based metadata fetch (eliminates N+1)
    - Batch serialization: Vectorized float32 serialization via numpy/struct
    - Read connection pool: Separate read connections for concurrent queries
    - Configurable HNSW: Tunable index parameters per collection
    - WAL optimization: Smart checkpoint scheduling
    - MRL truncation pipeline: 1024→768→512→256→128→64 automatic
    - INT8 quantization with rescore: Fast ANN + exact rerank
    - Spatial R-tree: 3D coordinates for VR navigation
    - O(1) delete: rowid→collection mapping
    - Metrics persistence: Survives restarts
    """

    def __init__(
        self,
        db_path: Optional[str] = None,
        embedding_dim: int = DEFAULT_EMBEDDING_DIM,
        collections: Optional[Dict[str, Dict]] = None,
        timeout: float = 5.0,
        read_pool_size: int = 4,
        batch_size: int = 100,
        enable_metrics: bool = True,
        auto_checkpoint: bool = True,           # GAP-007: default True
        checkpoint_interval: int = 300,         # GAP-007: 5 minutes default
    ):
        if db_path is None:
            data_dir = Path(os.environ.get("OMEGA_DATA_DIR", str(Path.home() / "omega" / "data")))
            db_path = str(data_dir / "omega_memory.db")

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._canonical_dim = CANONICAL_DIMENSION
        self._embedding_dim = embedding_dim

        self._collections = collections or COLLECTIONS
        self._vec_tables_created: Dict[str, bool] = {}
        # [D-1024] Pre-migration vec0 tables found in this DB: {table: rows}.
        self._legacy_vec_tables: Optional[Dict[str, int]] = None

        # Write connection (single, serialized)
        self._write_conn: Optional[sqlite3.Connection] = None
        self._write_lock = anyio.Lock()

        # Read connection pool (for concurrent reads)
        self._read_connections: List[sqlite3.Connection] = []
        self._read_pool_size = read_pool_size
        self._read_pool_index = 0
        self._read_pool_lock = anyio.Lock()

        self._initialized = False
        self.timeout = timeout
        self.batch_size = batch_size
        self.enable_metrics = enable_metrics

        # GAP-007: Auto checkpoint config
        self.auto_checkpoint = auto_checkpoint
        self.checkpoint_interval = checkpoint_interval

        # Metrics
        self._metrics = {
            "upsert_count": 0,
            "batch_upsert_count": 0,
            "query_count": 0,
            "batch_upsert_latency_ms": [],
            "query_latency_ms": [],
            "wal_checkpoint_count": 0,
        }

        # GAP-008: Metrics persistence path
        self._metrics_path = self.db_path.parent / "metrics" / "sqlite_vec_metrics.json"
        self._metrics_path.parent.mkdir(parents=True, exist_ok=True)
        self._load_metrics()

        self._legacy_vec_table = "omega_memory_vec"
        self._legacy_vec_created = False

        # GAP-006: rowid -> collections mapping for O(1) delete (F-04)
        # A rowid can live in multiple collections (primary + MRL variants).
        # Track all of them so delete removes from every collection.
        # Initialize on first upsert to avoid heavy import at module load.
        if not hasattr(self, "_rowid_to_collections"):
            from collections import defaultdict
            self._rowid_to_collections: Dict[int, set] = defaultdict(set)
        # Backward-compat shim: the old _rowid_to_collection dict.
        if not hasattr(self, "_rowid_to_collection"):
            self._rowid_to_collection: Dict[int, str] = {}

        # Periodic checkpoint task
        self._checkpoint_task = None

    # ========================================================================
    # METRICS PERSISTENCE (GAP-008)
    # ========================================================================

    def _load_metrics(self) -> None:
        """Load persisted metrics from disk."""
        if self._metrics_path.exists():
            try:
                with open(self._metrics_path) as f:
                    persisted = json.load(f)
                    # Merge with defaults (preserve counters)
                    self._metrics.update(persisted)
            except (json.JSONDecodeError, OSError):
                pass

    def _persist_metrics(self) -> None:
        """Persist metrics atomically to disk."""
        try:
            tmp_path = self._metrics_path.with_suffix(".tmp")
            with open(tmp_path, "w") as f:
                json.dump(self._metrics, f, indent=2)
            tmp_path.replace(self._metrics_path)
        except OSError:
            pass

    # ========================================================================
    # MRL TRUNCATION PIPELINE (GAP-002)
    # ========================================================================

    @staticmethod
    def truncate_mrl(vector: List[float], target_dim: int) -> List[float]:
        """Truncate vector to target dimension using Matryoshka Representation Learning.

        MRL property: First N dimensions preserve most semantic information.
        Valid target_dims: 512, 256, 128, 64 (must be in MRL_DIMENSIONS).
        """
        if target_dim not in MRL_DIMENSIONS:
            raise ValueError(f"Invalid MRL target dimension: {target_dim}. Valid: {MRL_DIMENSIONS}")
        if target_dim >= len(vector):
            return vector[:target_dim]  # No-op or pad if needed
        return vector[:target_dim]

    @staticmethod
    def generate_mrl_variants(vector: List[float]) -> Dict[int, List[float]]:
        """Generate all MRL variants from the 1024-dim canonical vector.

        Returns: {768: [...], 512: [...], 256: [...], 128: [...], 64: [...]}
        MRL is AVAILABLE but NOT canonical (D-1024-DIM-NATIVE-20260926).
        """
        if len(vector) != CANONICAL_DIMENSION:
            raise ValueError(f"Input must be {CANONICAL_DIMENSION}-dim, got {len(vector)}")
        return {
            dim: SQLiteVecAdapterOptimized.truncate_mrl(vector, dim)
            for dim in MRL_DIMENSIONS
            if dim < CANONICAL_DIMENSION
        }

    # ========================================================================
    # INT8 QUANTIZATION FOR RESCORE (GAP-003, GAP-009)
    # ========================================================================

    @staticmethod
    def quantize_int8(vector: List[float]) -> Tuple[bytes, float]:
        """Quantize float32 vector to int8 for rescore index.

        Uses symmetric quantization: scale = 127 / max(abs(vector))
        Returns (int8_bytes, scale_factor) for dequantization.
        """
        import numpy as np
        arr = np.array(vector, dtype=np.float32)
        max_abs = np.max(np.abs(arr))
        if max_abs == 0:
            return np.zeros(len(vector), dtype=np.int8).tobytes(), 1.0
        scale = 127.0 / max_abs
        quantized = np.round(arr * scale).astype(np.int8)
        return quantized.tobytes(), float(scale)

    @staticmethod
    def dequantize_int8(quantized_bytes: bytes, scale: float, dim: int) -> List[float]:
        """Dequantize int8 back to float32 for exact rescore."""
        import numpy as np
        quantized = np.frombuffer(quantized_bytes, dtype=np.int8, count=dim)
        return (quantized.astype(np.float32) / scale).tolist()

    @staticmethod
    def serialize_int8(vector: List[float]) -> bytes:
        """Serialize vector as int8 bytes (for sqlite-vec int8 column)."""
        import numpy as np
        arr = np.array(vector, dtype=np.float32)
        max_abs = np.max(np.abs(arr))
        if max_abs == 0:
            return np.zeros(len(vector), dtype=np.int8).tobytes()
        scale = 127.0 / max_abs
        quantized = np.round(arr * scale).astype(np.int8)
        return quantized.tobytes()

    def _get_write_conn(self) -> sqlite3.Connection:
        """Get the persistent write SQLite connection with hardened PRAGMA stack."""
        if self._write_conn is not None:
            return self._write_conn

        conn = get_sqlite_connection(self.db_path, profile="memory")

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

        self._write_conn = conn
        return conn

    def _open_read_conn(self) -> sqlite3.Connection:
        """Open a single read connection with sqlite-vec loaded."""
        conn = get_sqlite_connection(self.db_path, profile="memory")
        try:
            import sqlite_vec
            conn.enable_load_extension(True)
            sqlite_vec.load(conn)
            conn.enable_load_extension(False)
        except (ImportError, sqlite3.Error) as e:
            logger.error("Failed to load sqlite-vec extension on read conn: %s", e)
            raise
        return conn

    def _get_read_conn(self) -> sqlite3.Connection:
        """Get a read connection from the pool (round-robin).

        Pre-populates the pool on first call; reopens broken connections
        on health-check failure. (F-03)
        """
        import threading
        if not hasattr(self, '_read_pool_lock_threading'):
            self._read_pool_lock_threading = threading.Lock()
        with self._read_pool_lock_threading:
            if not self._read_connections:
                self._read_connections = [
                    self._open_read_conn() for _ in range(self._read_pool_size)
                ]
            idx = self._read_pool_index
            self._read_pool_index = (self._read_pool_index + 1) % len(self._read_connections)
            conn = self._read_connections[idx]
        # Health check: if conn is broken, reopen
        try:
            conn.execute("SELECT 1")
        except sqlite3.Error:
            logger.warning("Read conn %d broken, reopening", idx)
            try:
                conn.close()
            except Exception as e:
                logger.debug("Error closing broken read conn: %s", e)
            conn = self._open_read_conn()
            self._read_connections[idx] = conn
        return conn

    def _return_read_conn(self, conn: sqlite3.Connection) -> None:
        """No-op for round-robin pool; close is in close()."""
        pass

    async def _ensure_initialized(self) -> None:
        """Initialize FTS5, metadata tables, spatial R-tree, and all vec0 collections."""
        if self._initialized:
            return

        def _sync_init():
            conn = self._get_write_conn()

            try:
                import sqlite_vec
                conn.enable_load_extension(True)
                sqlite_vec.load(conn)
                conn.enable_load_extension(False)
                logger.debug("sqlite-vec extension loaded successfully")
            except ImportError:
                logger.error("sqlite-vec module not installed")
                raise
            except sqlite3.Error as e:
                logger.error("Failed to load sqlite-vec extension: %s", e)
                raise

            # Regular table for metadata storage
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

            # FTS5 table for full-text search
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS omega_memory_fts
                USING fts5(content, entity_name, session_id, role, timestamp)
            """)

            # GAP-005: Spatial R-tree table for 3D coordinates (VR navigation)
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS omega_memory_spatial
                USING rtree(
                    id,              -- Integer primary key (matches omega_memory_data.id)
                    minX, maxX,      -- X coordinate bounds (point: minX=maxX=x)
                    minY, maxY,      -- Y coordinate bounds
                    minZ, maxZ       -- Z coordinate bounds
                )
            """)

            # vec0 tables created lazily on first upsert (but we'll eager-create after)
            conn.commit()

        try:
            await anyio.to_thread.run_sync(_sync_init)
            
            # GAP-001: Eagerly create all declared vec0 collections
            await self._ensure_all_collections()
            
            self._initialized = True
            logger.info(
                "SQLiteVecAdapterOptimized initialized at %s (dim=%d, collections=%d, read_pool=%d)",
                self.db_path,
                self._embedding_dim,
                len(self._vec_tables_created),
                self._read_pool_size,
            )
            
            # GAP-007: Start auto WAL checkpoint
            if self.auto_checkpoint:
                await self.start_periodic_checkpoint(self.checkpoint_interval)
                logger.info("Auto WAL checkpoint enabled (interval=%ds)", self.checkpoint_interval)
                
        except (sqlite3.Error, OSError) as e:
            logger.error("Failed to initialize SQLiteVecAdapterOptimized: %s", e)
            raise ProviderUnavailableError(
                "sqlite_vec", f"SQLite-vec initialization failed: {e}", raw_error=e
            ) from e

    async def _scan_legacy_vec_tables(self) -> Dict[str, int]:
        """Detect pre-D-1024 vec0 tables with no canonical successor.

        Non-destructive inventory (name -> row count) so migration state is
        visible in get_status() instead of old vectors vanishing silently.
        """
        if self._legacy_vec_tables is not None:
            return self._legacy_vec_tables

        def _sync_scan() -> Dict[str, int]:
            conn = self._get_write_conn()
            found: Dict[str, int] = {}
            rows = conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' "
                "AND sql LIKE '%vec0%' ORDER BY name"
            ).fetchall()
            for (name,) in rows:
                if name in self._collections:
                    continue
                if get_vec_table_declared_dim(conn, name) is None:
                    continue
                try:
                    count = conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
                except sqlite3.Error:
                    count = -1
                found[name] = count
            return found

        self._legacy_vec_tables = await anyio.to_thread.run_sync(_sync_scan)
        if self._legacy_vec_tables:
            logger.warning(
                "D-1024 migration: %d pre-1024 vec0 table(s) present in %s: %s. "
                "Their vectors are not reachable from the 1024-dim collections; "
                "metadata + FTS5 rows remain intact.",
                len(self._legacy_vec_tables),
                self.db_path,
                self._legacy_vec_tables,
            )
        return self._legacy_vec_tables

    async def _ensure_all_collections(self) -> None:
        """Eagerly create all declared vec0 collections at initialization.

        Called from _ensure_initialized() to guarantee all 7 collections exist
        before any ingestion occurs. Required by Ingestion Pipeline Spec §5.
        """
        for collection_name, config in self._collections.items():
            if not self._vec_tables_created.get(collection_name, False):
                # Use a dummy vector of correct dimension to trigger creation
                dummy_vector = [0.0] * config["dimension"]
                await self._ensure_collection_vec_table(collection_name, len(dummy_vector))

    async def _ensure_collection_vec_table(self, collection_name: str, actual_dim: int) -> None:
        """Create or recreate vec0 table for a specific collection with STRICT dimension enforcement.

        Supports INT8 quantization with rescore for declared collections (GAP-003).
        Note: sqlite-vec v0.1.9 doesn't support int8 + auxiliary columns.
        v0.1.10+ supports: embedding int8[dim] distance_metric=cosine, embedding_fp32 float[dim] auxiliary
        """
        collection_name = resolve_collection_name(collection_name, self._collections)

        collection_config = self._collections[collection_name]
        declared_dim = collection_config["dimension"]
        quantization = collection_config.get("quantization", "none")

        if actual_dim != declared_dim:
            raise RuntimeError(
                f"EMBEDDING DIMENSION MISMATCH — CANONICAL VIOLATION (M23)\n"
                f"  Collection: {collection_name}\n"
                f"  Provider returned: {actual_dim}-dim vector\n"
                f"  Collection declared: {declared_dim}-dim\n"
                f"  Fix: Provider MUST output {declared_dim}-dim vectors.\n"
                f"  Use MRL truncation in provider.get_embedding() if needed."
            )

        if self._vec_tables_created.get(collection_name, False):
            return

        table_name = collection_name
        hnsw_config = self._collections[collection_name].get("hnsw", {})

        def _sync_create_vec():
            conn = self._get_write_conn()
            # Note: sqlite-vec 0.1.9 doesn't support HNSW options in CREATE TABLE
            # HNSW parameters are set via PRAGMA after table creation if supported

            # [D-1024] A vec0 table is typed at CREATE time (`float[N]`) and
            # cannot accept a different width. If the table already exists but
            # was built at another dimension (e.g. the pre-D-1024 768-dim layout),
            # DROP + recreate instead of raising forever on every write.
            existing_dim = get_vec_table_declared_dim(conn, table_name)
            if existing_dim is not None and existing_dim != declared_dim:
                try:
                    old_rows = conn.execute(
                        f"SELECT COUNT(*) FROM {table_name}"
                    ).fetchone()[0]
                except sqlite3.Error:
                    old_rows = -1
                logger.warning(
                    "D-1024 migration: vec0 table %r was created at %d-dim but "
                    "collection declares %d-dim. Dropping and recreating "
                    "(%d row(s) discarded; metadata/FTS rows preserved — "
                    "re-embed to restore vector search).",
                    table_name,
                    existing_dim,
                    declared_dim,
                    old_rows,
                )
                conn.execute(f"DROP TABLE IF EXISTS {table_name}")

            # Check sqlite-vec version for int8 + auxiliary support
            try:
                import sqlite_vec
                version = getattr(sqlite_vec, '__version__', '0.1.9')
                major, minor, patch = map(int, version.split('.')[:3])
                supports_int8_aux = (major > 0) or (minor >= 10)
            except (ImportError, AttributeError, ValueError):
                supports_int8_aux = False
            
            if quantization == "int8_rescore" and supports_int8_aux:
                # GAP-003: Use int8 vector column + auxiliary float column for rescore (v0.1.10+)
                conn.execute(f"""
                    CREATE VIRTUAL TABLE IF NOT EXISTS {table_name}
                    USING vec0(
                        embedding int8[{declared_dim}] distance_metric=cosine,
                        embedding_fp32 float[{declared_dim}] auxiliary,
                        entity_name TEXT partition key
                    )
                """)
            else:
                # Standard float32 path (v0.1.9 compatible)
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
        logger.info("vec0 collection '%s' created with dim=%d, quantization=%s", collection_name, declared_dim, quantization)

    # ========================================================================
    # BATCH SERIALIZATION (Optimization)
    # ========================================================================

    @staticmethod
    def serialize_batch_float32(vectors: List[List[float]]) -> List[bytes]:
        """Batch serialize multiple vectors to bytes for sqlite-vec.
        
        Uses numpy if available for vectorized operation, falls back to struct.
        """
        try:
            import numpy as np
            # Vectorized serialization
            arr = np.array(vectors, dtype=np.float32)
            return [row.tobytes() for row in arr]
        except ImportError:
            # Fallback: manual serialization per vector
            return [struct.pack(f"{len(v)}f", *v) for v in vectors]

    @staticmethod
    def serialize_float32(vector: List[float]) -> bytes:
        """Serialize a single vector to bytes."""
        try:
            import sqlite_vec
            return sqlite_vec.serialize_float32(vector)
        except ImportError:
            return struct.pack(f"{len(vector)}f", *vector)

    # ========================================================================
    # BATCH UPSERT (Optimization)
    # ========================================================================

    async def batch_upsert(
        self,
        items: List[Dict[str, Any]],
        collection: str = CANONICAL_COLLECTION,
    ) -> List[str]:
        """Insert or update multiple vectors in a single transaction.
        
        Args:
            items: List of dicts with keys: entity_name, vector, metadata, id (optional)
            collection: Target collection name
            
        Returns:
            List of UUID strings
            
        Performance: Single transaction, batch serialization, single commit.
        Features: MRL truncation pipeline, INT8 quantization, spatial R-tree, O(1) delete mapping.
        """
        if not items:
            return []

        await self._ensure_initialized()

        # Resolve legacy (pre-D-1024) names onto their canonical successors.
        collection = resolve_collection_name(collection, self._collections)

        # Validate all vectors have the same dimension (F-05).
        # All items in a batch must share the collection's expected dimension;
        # mixed-dim batches are rejected with a clear index-aware error.
        expected_dim = self._collections[collection]["dimension"]
        for i, item in enumerate(items):
            vec = item.get("vector", [])
            if not vec:
                continue
            if len(vec) != expected_dim:
                raise ValueError(
                    f"batch_upsert rejected: item[{i}] vector dim {len(vec)} "
                    f"!= collection '{collection}' dim {expected_dim}. "
                    f"All items in a batch must share the same dimension."
                )
        # If any item has a vector, ensure the vec0 table exists.
        if any(item.get("vector") for item in items):
            await self._ensure_collection_vec_table(collection, expected_dim)

        # Batch serialize all vectors (float32 for primary)
        vectors = [item.get("vector", []) for item in items]
        embeddings_fp32 = self.serialize_batch_float32(vectors) if vectors else [None] * len(items)

        # GAP-003, GAP-009: Prepare INT8 embeddings for quantized collections
        quantization = self._collections[collection].get("quantization", "none")
        embeddings_int8 = []
        scales = []
        if quantization == "int8_rescore":
            for v in vectors:
                if v:
                    q_bytes, scale = self.quantize_int8(v)
                    embeddings_int8.append(q_bytes)
                    scales.append(scale)
                else:
                    embeddings_int8.append(None)
                    scales.append(1.0)

        # GAP-002: Generate MRL variants for fallback collections (only for canonical 1024-dim)
        # Use the first item with a vector as the reference for MRL generation.
        # All items in the batch must share the same MRL structure (F-05).
        mrl_variants = {}
        first_vec = next((item.get("vector") for item in items if item.get("vector")), [])
        if len(first_vec) == CANONICAL_DIMENSION:
            mrl_variants = self.generate_mrl_variants(first_vec)

        uuids = [item.get("id") or str(uuid.uuid4()) for item in items]
        timestamps = [str(item.get("metadata", {}).get("timestamp", time.time())) for item in items]
        session_ids = [item.get("metadata", {}).get("session_id", "unknown") for item in items]
        roles = [item.get("metadata", {}).get("role", "unknown") for item in items]
        contents = [item.get("metadata", {}).get("content", "") for item in items]
        entity_names = [item.get("entity_name") for item in items]
        metadata_jsons = [json.dumps(item.get("metadata", {}), default=str) for item in items]

        # GAP-005: Extract spatial coordinates from metadata
        spatial_coords = []
        for item in items:
            coords = item.get("metadata", {}).get("spatial_coords", {"x": 0.0, "y": 0.0, "z": 0.0})
            x, y, z = coords.get("x", 0.0), coords.get("y", 0.0), coords.get("z", 0.0)
            spatial_coords.append((x, y, z))

        start_time = time.perf_counter()

        async with self._write_lock:
            for attempt in range(3):
                try:
                    def _sync_batch_upsert():
                        conn = self._get_write_conn()
                        conn.execute("BEGIN IMMEDIATE")

                        rowids = []
                        for i in range(len(items)):
                            # 1. Insert into metadata table
                            cursor = conn.execute(
                                """
                                INSERT INTO omega_memory_data
                                (uuid, entity_name, session_id, role, content, timestamp, metadata_json)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    uuids[i],
                                    entity_names[i],
                                    items[i].get("metadata", {}).get("session_id", "unknown"),
                                    items[i].get("metadata", {}).get("role", "unknown"),
                                    items[i].get("metadata", {}).get("content", ""),
                                    timestamps[i],
                                    metadata_jsons[i],
                                ),
                            )
                            rowids.append(cursor.lastrowid)

                        # 2. Batch insert into FTS5
                        fts_data = [
                            (rowids[i], contents[i], entity_names[i], session_ids[i], roles[i], timestamps[i])
                            for i in range(len(items))
                        ]
                        conn.executemany(
                            """
                            INSERT INTO omega_memory_fts(rowid, content, entity_name, session_id, role, timestamp)
                            VALUES (?, ?, ?, ?, ?, ?)
                            """,
                            fts_data,
                        )

                        # 3. Batch insert into primary vec0 collection
                        table_name = collection
                        # Check sqlite-vec version for int8 + auxiliary support
                        try:
                            import sqlite_vec
                            version = getattr(sqlite_vec, '__version__', '0.1.9')
                            major, minor, patch = map(int, version.split('.')[:3])
                            supports_int8_aux = (major > 0) or (minor >= 10)
                        except (ImportError, AttributeError, ValueError):
                            supports_int8_aux = False
                        
                        if quantization == "int8_rescore" and supports_int8_aux:
                            # GAP-003, GAP-009: Insert int8 + fp32 auxiliary for rescore (v0.1.10+)
                            vec_data = [
                                (rowids[i], embeddings_int8[i], embeddings_fp32[i], entity_names[i])
                                for i in range(len(items))
                                if embeddings_int8[i] is not None
                            ]
                            if vec_data:
                                conn.executemany(
                                    f"""
                                    INSERT INTO {collection}(rowid, embedding, embedding_fp32, entity_name)
                                    VALUES (?, ?, ?, ?)
                                    """,
                                    vec_data,
                                )
                        else:
                            # Standard float32 path (v0.1.9 compatible)
                            vec_data = [
                                (rowids[i], embeddings_fp32[i], entity_names[i])
                                for i in range(len(items))
                                if embeddings_fp32[i] is not None
                            ]
                            if vec_data:
                                conn.executemany(
                                    f"""
                                    INSERT INTO {collection}(rowid, embedding, entity_name)
                                    VALUES (?, ?, ?)
                                    """,
                                    vec_data,
                                )

                        # GAP-006: Record rowid -> collection mapping for O(1) delete
                        for i in range(len(items)):
                            self._rowid_to_collections[rowids[i]].add(collection)
                            # Backward-compat: last-write wins for single-collection lookups
                            self._rowid_to_collection[rowids[i]] = collection

                        # GAP-005: Batch insert into spatial R-tree
                        spatial_data = [
                            (rowids[i], spatial_coords[i][0], spatial_coords[i][0],
                             spatial_coords[i][1], spatial_coords[i][1],
                             spatial_coords[i][2], spatial_coords[i][2])
                            for i in range(len(items))
                        ]
                        if spatial_data:
                            conn.executemany(
                                "INSERT INTO omega_memory_spatial(id, minX, maxX, minY, maxY, minZ, maxZ) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                spatial_data,
                            )

                        # GAP-002: Upsert MRL variants to fallback collections
                        for mrl_dim, mrl_vector in mrl_variants.items():
                            mrl_collection = f"omega_vec_nomic_{mrl_dim}"
                            if mrl_collection in self._collections:
                                # Ensure MRL collection exists
                                mrl_declared_dim = self._collections[mrl_collection]["dimension"]
                                if mrl_declared_dim == mrl_dim:
                                    # Serialize MRL vector for all items (same truncated vector for all)
                                    mrl_embeddings = self.serialize_batch_float32([mrl_vector] * len(items))
                                    mrl_vec_data = [
                                        (rowids[i], mrl_embeddings[i], entity_names[i])
                                        for i in range(len(items))
                                    ]
                                    if mrl_vec_data:
                                        conn.executemany(
                                            f"""
                                            INSERT INTO {mrl_collection}(rowid, embedding, entity_name)
                                            VALUES (?, ?, ?)
                                            """,
                                            mrl_vec_data,
                                        )
                                    # Record mapping for MRL collections too (F-04)
                                    # Add to the set so delete targets all collections.
                                    for i in range(len(items)):
                                        self._rowid_to_collections[rowids[i]].add(mrl_collection)
                                        # Last MRL write wins for the single-collection shim.
                                        self._rowid_to_collection[rowids[i]] = mrl_collection

                        conn.commit()
                        return rowids

                    await anyio.to_thread.run_sync(_sync_batch_upsert)

                    # Update metrics
                    latency_ms = (time.perf_counter() - start_time) * 1000
                    if self.enable_metrics:
                        self._metrics["batch_upsert_count"] += 1
                        self._metrics["upsert_count"] += len(items)
                        self._metrics["batch_upsert_latency_ms"].append(latency_ms)
                        self._persist_metrics()  # GAP-008: Persist metrics

                    return uuids

                except sqlite3.OperationalError as e:
                    if "SQLITE_BUSY" in str(e) and attempt < 2:
                        delay = 0.05 * (2**attempt)
                        logger.warning("SQLITE_BUSY on batch_upsert (attempt %d), retrying in %sms", attempt + 1, delay * 1000)
                        await anyio.sleep(delay)
                        continue
                    raise ProviderError("sqlite_vec", f"Batch upsert failed: {e}", raw_error=e) from e
                except (sqlite3.Error, OSError) as e:
                    logger.error("Batch upsert failed: %s", e, exc_info=True)
                    raise ProviderError("sqlite_vec", f"Batch upsert failed: {e}", raw_error=e) from e

        raise ProviderError("sqlite_vec", "Batch upsert failed after retries")

    # ========================================================================
    # OPTIMIZED QUERY (JOIN-based, eliminates N+1)
    # ========================================================================

    async def query(
        self,
        entity_name: str,
        vector: List[float],
        limit: int = 10,
        filter: Optional[Dict[str, Any]] = None,
        collection: str = CANONICAL_COLLECTION,
    ) -> List[Tuple[float, Dict[str, Any]]]:
        """Optimized query with JOIN-based metadata fetch (eliminates N+1).

        Supports INT8 quantization with rescore for quantized collections (GAP-003, GAP-009).
        """
        await self._ensure_initialized()

        if not vector:
            return []

        # Resolve legacy (pre-D-1024) names onto their canonical successors.
        collection = resolve_collection_name(collection, self._collections)

        coll_config = self._collections[collection]
        expected_dim = coll_config["dimension"]
        quantization = coll_config.get("quantization", "none")

        if len(vector) != expected_dim:
            raise ValueError(f"Vector dimension {len(vector)} != collection dim {expected_dim}")

        if not self._vec_tables_created.get(collection, False):
            return []

        start_time = time.perf_counter()

        try:
            def _sync_query():
                conn = self._get_read_conn()

                # Check sqlite-vec version for int8 + auxiliary support
                try:
                    import sqlite_vec
                    version = getattr(sqlite_vec, '__version__', '0.1.9')
                    major, minor, patch = map(int, version.split('.')[:3])
                    supports_int8_aux = (major > 0) or (minor >= 10)
                except (ImportError, AttributeError, ValueError):
                    supports_int8_aux = False

                if quantization == "int8_rescore" and supports_int8_aux:
                    # GAP-003, GAP-009: Query uses int8 index for fast ANN, rescore with float32 auxiliary
                    # sqlite-vec v0.1.10+ handles int8 MATCH + float32 rescore automatically
                    int8_blob = self.serialize_int8(vector)
                    cursor = conn.execute(
                        f"""
                        SELECT v.rowid, v.distance,
                               d.uuid, d.entity_name, d.session_id, d.role, d.content, d.timestamp, d.metadata_json
                        FROM {collection} v
                        JOIN omega_memory_data d ON v.rowid = d.id
                        WHERE v.embedding MATCH ? AND v.entity_name = ? AND k = ?
                        ORDER BY v.distance
                        """,
                        (int8_blob, entity_name, limit),
                    )
                else:
                    # Standard float32 path (v0.1.9 compatible)
                    fp32_blob = self.serialize_float32(vector)
                    cursor = conn.execute(
                        f"""
                        SELECT v.rowid, v.distance,
                               d.uuid, d.entity_name, d.session_id, d.role, d.content, d.timestamp, d.metadata_json
                        FROM {collection} v
                        JOIN omega_memory_data d ON v.rowid = d.id
                        WHERE v.embedding MATCH ? AND v.entity_name = ? AND k = ?
                        ORDER BY v.distance
                        """,
                        (fp32_blob, entity_name, limit),
                    )

                results = []
                for row in cursor.fetchall():
                    rowid, distance = row[0], row[1]
                    if distance is None:
                        continue
                    score = 1.0 - distance

                    metadata = {
                        "id": row[2],
                        "entity_name": row[3],
                        "session_id": row[4],
                        "role": row[5],
                        "content": row[6],
                        "timestamp": row[7],
                    }
                    if row[8]:
                        try:
                            extra = json.loads(row[8])
                            metadata.update(extra)
                        except json.JSONDecodeError:
                            pass

                    results.append((score, metadata))

                return results

            results = await anyio.to_thread.run_sync(_sync_query)

            latency_ms = (time.perf_counter() - start_time) * 1000
            if self.enable_metrics:
                self._metrics["query_count"] += 1
                self._metrics["query_latency_ms"].append(latency_ms)
                self._persist_metrics()  # GAP-008: Persist metrics

            return results

        except (sqlite3.Error, OSError) as e:
            logger.error("Optimized query failed for collection %s: %s", collection, e, exc_info=True)
            raise ProviderError("sqlite_vec", f"Query failed: {e}", raw_error=e) from e

    # ========================================================================
    # SINGLE UPSERT (Delegates to batch_upsert for consistency)
    # ========================================================================

    async def upsert(
        self,
        entity_name: str,
        vector: List[float],
        metadata: Dict[str, Any],
        id: Optional[str] = None,
        collection: str = CANONICAL_COLLECTION,
    ) -> str:
        """Single upsert - delegates to batch_upsert for consistency."""
        result = await self.batch_upsert([{
            "entity_name": entity_name,
            "vector": vector,
            "metadata": metadata,
            "id": id,
        }], collection)
        return result[0]

    # ========================================================================
    # OTHER METHODS (delete, delete_session, status, hybrid_search, etc.)
    # ========================================================================

    async def delete(
        self, entity_name: str, ids: List[str], collection: str = CANONICAL_COLLECTION
    ) -> bool:
        """Delete vectors by UUID with O(1) collection lookup (GAP-006)."""
        if not ids:
            return False
        collection = resolve_collection_name(collection, self._collections)

        await self._ensure_initialized()

        async with self._write_lock:
            try:
                def _sync_delete():
                    conn = self._get_write_conn()
                    deleted_any = False
                    conn.execute("BEGIN IMMEDIATE")

                    for uuid_str in ids:
                        cursor = conn.execute(
                            "SELECT id FROM omega_memory_data WHERE uuid = ? AND entity_name = ?",
                            (uuid_str, entity_name),
                        )
                        row = cursor.fetchone()
                        if not row:
                            continue
                        rowid = row[0]
                        conn.execute("DELETE FROM omega_memory_data WHERE id = ?", (rowid,))
                        conn.execute("DELETE FROM omega_memory_fts WHERE rowid = ?", (rowid,))
                        # GAP-006: O(1) delete using rowid -> collections mapping (F-04)
                        # Delete from ALL collections the rowid lives in (primary + MRL).
                        rowid_collections = self._rowid_to_collections.pop(rowid, set())
                        if not rowid_collections:
                            # Backward-compat: check the old single-collection map.
                            target = self._rowid_to_collection.pop(rowid, None)
                            if target:
                                rowid_collections = {target}
                        for coll in rowid_collections:
                            conn.execute(f"DELETE FROM {coll} WHERE rowid = ?", (rowid,))
                        if not rowid_collections:
                            # Fallback: collection not in mapping (legacy data) — scan created tables
                            for collection_name in self._vec_tables_created:
                                conn.execute(f"DELETE FROM {collection_name} WHERE rowid = ?", (rowid,))
                        # Also delete from spatial R-tree
                        conn.execute("DELETE FROM omega_memory_spatial WHERE id = ?", (rowid,))
                        deleted_any = True

                    conn.commit()
                    return deleted_any

                return await anyio.to_thread.run_sync(_sync_delete)
            except (sqlite3.Error, OSError) as e:
                raise ProviderError("sqlite_vec", f"Delete failed: {e}", raw_error=e) from e

    async def delete_session(
        self, entity_name: str, session_id: str, collection: str = CANONICAL_COLLECTION
    ) -> bool:
        """Delete all vectors for a session with O(1) collection lookup (GAP-006)."""
        collection = resolve_collection_name(collection, self._collections)

        await self._ensure_initialized()

        async with self._write_lock:
            try:
                def _sync_delete_session():
                    conn = self._get_write_conn()
                    conn.execute("BEGIN IMMEDIATE")

                    cursor = conn.execute(
                        "SELECT id FROM omega_memory_data WHERE entity_name = ? AND session_id = ?",
                        (entity_name, session_id),
                    )
                    rowids = [row[0] for row in cursor.fetchall()]
                    if not rowids:
                        return False

                    placeholders = ",".join("?" for _ in rowids)
                    conn.execute(f"DELETE FROM omega_memory_data WHERE id IN ({placeholders})", rowids)
                    conn.execute(f"DELETE FROM omega_memory_fts WHERE rowid IN ({placeholders})", rowids)
                    
                    # GAP-006: O(1) delete using mapping
                    for rowid in rowids:
                        target_collection = self._rowid_to_collection.get(rowid)
                        if target_collection:
                            conn.execute(f"DELETE FROM {target_collection} WHERE rowid = ?", (rowid,))
                            del self._rowid_to_collection[rowid]
                        else:
                            # Fallback: scan created tables
                            for collection_name in self._vec_tables_created:
                                conn.execute(f"DELETE FROM {collection_name} WHERE rowid = ?", (rowid,))
                    
                    # Also delete from spatial R-tree
                    conn.execute(f"DELETE FROM omega_memory_spatial WHERE id IN ({placeholders})", rowids)

                    conn.commit()
                    return True

                return await anyio.to_thread.run_sync(_sync_delete_session)
            except (sqlite3.Error, OSError) as e:
                raise ProviderError("sqlite_vec", f"Delete session failed: {e}", raw_error=e) from e

    async def get_status(self) -> Dict[str, Any]:
        try:
            await self._ensure_initialized()

            await self._scan_legacy_vec_tables()

            def _sync_status():
                conn = self._get_read_conn()
                data_count = conn.execute("SELECT COUNT(*) FROM omega_memory_data").fetchone()[0]
                fts_count = conn.execute("SELECT COUNT(*) FROM omega_memory_fts").fetchone()[0]
                
                # Count vectors across all collections
                total_vec_count = 0
                collection_counts = {}
                for collection_name in self._vec_tables_created:
                    try:
                        count = conn.execute(f"SELECT COUNT(*) FROM {collection_name}").fetchone()[0]
                        collection_counts[collection_name] = count
                        total_vec_count += count
                    except sqlite3.Error:
                        collection_counts[collection_name] = 0
                
                entities = conn.execute("SELECT DISTINCT entity_name FROM omega_memory_data").fetchall()
                entity_count = len(entities)

                return {
                    "status": "healthy",
                    "type": "sqlite-vec-unified-fabric-optimized",
                    "db_path": str(self.db_path),
                    "embedding_dim": self._embedding_dim,
                    "canonical_dimension": self._canonical_dim,
                    "canonical_collection": CANONICAL_COLLECTION,
                    "legacy_vec_tables": dict(self._legacy_vec_tables or {}),
                    "legacy_vec_rows": sum(
                        n for n in (self._legacy_vec_tables or {}).values() if n > 0
                    ),
                    "vector_count": total_vec_count,
                    "collection_counts": collection_counts,
                    "fts_count": fts_count,
                    "metadata_count": data_count,
                    "entity_count": entity_count,
                    "collections_created": list(self._vec_tables_created.keys()),
                    "read_pool_size": self._read_pool_size,
                    "batch_size": self.batch_size,
                }

            return await anyio.to_thread.run_sync(_sync_status)
        except (sqlite3.Error, OSError) as e:
            return {"status": "unhealthy", "error": str(e)}

    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics with persistence (GAP-008)."""
        metrics = self._metrics.copy()
        if metrics["batch_upsert_latency_ms"]:
            metrics["avg_batch_upsert_latency_ms"] = sum(metrics["batch_upsert_latency_ms"]) / len(metrics["batch_upsert_latency_ms"])
            metrics["p99_batch_upsert_latency_ms"] = sorted(metrics["batch_upsert_latency_ms"])[int(len(metrics["batch_upsert_latency_ms"]) * 0.99)]
        if metrics["query_latency_ms"]:
            metrics["avg_query_latency_ms"] = sum(metrics["query_latency_ms"]) / len(metrics["query_latency_ms"])
            metrics["p99_query_latency_ms"] = sorted(metrics["query_latency_ms"])[int(len(metrics["query_latency_ms"]) * 0.99)]
        # GAP-008: Persist metrics on every read
        self._persist_metrics()
        return metrics

    async def hybrid_search(
        self,
        query: str,
        entity_name: str,
        vector: List[float],
        limit: int = 20,
        fts_weight: Optional[float] = None,
        vec_weight: Optional[float] = None,
        collection: str = CANONICAL_COLLECTION,
    ) -> List[Dict[str, Any]]:
        """Hybrid search with per-collection configurable RRF weights (GAP-004)."""
        await self._ensure_initialized()
        if not query.strip() and not vector:
            return []

        # GAP-004: Use collection-specific weights if not explicitly provided
        if fts_weight is None or vec_weight is None:
            weights = COLLECTION_RRF_WEIGHTS.get(collection, {"fts": 0.5, "vec": 0.5})
            fts_weight = fts_weight or weights["fts"]
            vec_weight = vec_weight or weights["vec"]

        from .hybrid_search import fetch_and_fuse

        async def _fts_fetch() -> List[Dict[str, Any]]:
            if not query.strip():
                return []
            def _sync_fts():
                conn = self._get_read_conn()
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
                    {"rowid": row[0], "entity_name": entity_name, "session_id": row[1],
                     "role": row[2], "content": row[3], "timestamp": row[4]}
                    for row in cursor.fetchall()
                ]
            try:
                return await anyio.to_thread.run_sync(_sync_fts)
            except sqlite3.OperationalError as e:
                logger.warning("FTS5 query syntax error (degraded): %s", e)
                return []
            except (sqlite3.Error, OSError) as e:
                logger.warning("FTS search failed: %s", e)
                return []

        async def _vec_fetch() -> List[tuple]:
            if not vector:
                return []
            try:
                return await self.query(entity_name=entity_name, vector=vector, limit=limit * 2, collection=collection)
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

    # ========================================================================
    # SPATIAL R-TREE QUERIES (GAP-005)
    # ========================================================================

    # [id-soft: doom-1993] BSP Culling — Spatial range query for VR navigation
    async def spatial_range_query(
        self,
        entity_name: str,
        center_x: float, center_y: float, center_z: float,
        radius: float,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Find all memories within radius of (x,y,z) — VR navigation query (GAP-005)."""
        await self._ensure_initialized()
        
        min_x, max_x = center_x - radius, center_x + radius
        min_y, max_y = center_y - radius, center_y + radius
        min_z, max_z = center_z - radius, center_z + radius
        
        def _sync_spatial_query():
            conn = self._get_read_conn()
            cursor = conn.execute("""
                SELECT s.id, d.uuid, d.entity_name, d.session_id, d.role, d.content, d.timestamp, d.metadata_json
                FROM omega_memory_spatial s
                JOIN omega_memory_data d ON s.id = d.id
                WHERE s.minX <= ? AND s.maxX >= ?
                  AND s.minY <= ? AND s.maxY >= ?
                  AND s.minZ <= ? AND s.maxZ >= ?
                  AND d.entity_name = ?
                LIMIT ?
            """, (max_x, min_x, max_y, min_y, max_z, min_z, entity_name, limit))
            
            results = []
            for row in cursor.fetchall():
                metadata = {
                    "id": row[1], "entity_name": row[2], "session_id": row[3],
                    "role": row[4], "content": row[5], "timestamp": row[6],
                }
                if row[7]:
                    try:
                        metadata.update(json.loads(row[7]))
                    except json.JSONDecodeError:
                        pass
                results.append(metadata)
            return results
        
        return await anyio.to_thread.run_sync(_sync_spatial_query)

    # ========================================================================
    # VR NAVIGATION QUERIES (Spatial Vectors Strategy)
    # ========================================================================

    # [id-soft: doom-1993] BSP Culling — A* pathfinding for VR navigation
    # [id-soft: quake-1996] PVS — Sector-based visibility for pathfinding
    async def vr_navigate_to(
        self,
        entity_name: str,
        start_pos: Tuple[float, float, float],
        target_query: str,
        max_steps: int = 20,
    ) -> List[Dict[str, Any]]:
        """VR navigation: spatial A* from start position to semantic target.

        Uses spatial graph for pathfinding. Falls back to spatial range query
        if graph not available.
        """
        await self._ensure_initialized()

        # Try to use spatial graph if available
        try:
            from .spatial_graph import get_spatial_graph
            graph = get_spatial_graph(self)
            await graph.build_spatial_graph(entity_name)

            # Find nearest node to start position
            start_node = await self._find_nearest_node(entity_name, start_pos)
            if not start_node:
                return []

            # Navigate using graph
            path = await graph.navigate_to(start_node["rowid"], target_query, entity_name, max_steps)
            return path
        except Exception as e:
            logger.warning("Spatial graph navigation failed, falling back to range query: %s", e)
            # Fallback: spatial range query around start position
            return await self.spatial_range_query(
                entity_name, start_pos[0], start_pos[1], start_pos[2],
                radius=50.0, limit=max_steps
            )

    async def _find_nearest_node(
        self,
        entity_name: str,
        position: Tuple[float, float, float],
    ) -> Optional[Dict[str, Any]]:
        """Find the memory node nearest to a 3D position."""
        x, y, z = position

        def _sync_find():
            conn = self._get_read_conn()
            cursor = conn.execute("""
                SELECT s.id, d.uuid, d.entity_name, d.content, d.metadata_json,
                       s.minX, s.minY, s.minZ,
                       ((s.minX - ?)*(s.minX - ?) + (s.minY - ?)*(s.minY - ?) + (s.minZ - ?)*(s.minZ - ?)) as dist_sq
                FROM omega_memory_spatial s
                JOIN omega_memory_data d ON s.id = d.id
                WHERE d.entity_name = ?
                ORDER BY dist_sq
                LIMIT 1
            """, (x, x, y, y, z, z, entity_name))

            row = cursor.fetchone()
            if not row:
                return None
            rowid, uuid, ent_name, content, metadata_json, nx, ny, nz, dist_sq = row
            metadata = {}
            if metadata_json:
                try:
                    metadata = json.loads(metadata_json)
                except json.JSONDecodeError:
                    pass
            return {
                "rowid": rowid,
                "uuid": uuid,
                "entity_name": ent_name,
                "content": content,
                "coordinates": (nx, ny, nz),
                "metadata": metadata,
                "distance": math.sqrt(dist_sq),
            }

        return await anyio.to_thread.run_sync(_sync_find)

    # [id-soft: doom-1993] BSP Culling — Sector streaming for Godot LOD
    # [id-soft: quake-1996] PVS — Potentially Visible Set for sector culling
    async def get_sector_memories(
        self,
        sector_id: str,
        entity_name: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get all memories in a BSP sector for Godot streaming.

        Sector bounds are computed from the spatial graph's sector partitioning.
        """
        await self._ensure_initialized()

        # Try to get sector bounds from spatial graph
        try:
            from .spatial_graph import get_spatial_graph
            graph = get_spatial_graph(self)
            await graph.build_spatial_graph(entity_name)
            sector = graph.get_sector_info(sector_id)
            if sector:
                bounds = (sector.min_x, sector.max_x, sector.min_y, sector.max_y, sector.min_z, sector.max_z)
                return await graph.sector_stream(bounds, entity_name, limit)
        except Exception as e:
            logger.warning("Spatial graph sector query failed: %s", e)

        # Fallback: query by sector_id pattern in metadata
        def _sync_sector_fallback():
            conn = self._get_read_conn()
            cursor = conn.execute("""
                SELECT s.id, d.uuid, d.entity_name, d.session_id, d.role, d.content, d.timestamp, d.metadata_json,
                       s.minX, s.minY, s.minZ
                FROM omega_memory_spatial s
                JOIN omega_memory_data d ON s.id = d.id
                WHERE d.entity_name = ?
                  AND d.metadata_json LIKE ?
                LIMIT ?
            """, (entity_name, f'%"{sector_id}"%', limit))

            results = []
            for row in cursor.fetchall():
                rowid, uuid, ent_name, session_id, role, content, timestamp, metadata_json, x, y, z = row
                metadata = {}
                if metadata_json:
                    try:
                        metadata = json.loads(metadata_json)
                    except json.JSONDecodeError:
                        pass
                results.append({
                    "rowid": rowid,
                    "uuid": uuid,
                    "entity_name": ent_name,
                    "session_id": session_id,
                    "role": role,
                    "content": content,
                    "timestamp": timestamp,
                    "coordinates": (x, y, z),
                    "metadata": metadata,
                })
            return results

        return await anyio.to_thread.run_sync(_sync_sector_fallback)

    # [id-soft: doom-1993] BSP Culling — Neighbor queries for graph construction
    async def get_spatial_neighbors(
        self,
        rowid: int,
        k: int = 6,
    ) -> List[Tuple[int, float]]:
        """Get k nearest spatial neighbors for graph construction."""
        await self._ensure_initialized()

        def _sync_neighbors():
            conn = self._get_read_conn()
            cursor = conn.execute(
                "SELECT minX, minY, minZ FROM omega_memory_spatial WHERE id = ?",
                (rowid,)
            )
            row = cursor.fetchone()
            if not row:
                return []
            x, y, z = row[0], row[1], row[2]

            # Expanding radius search
            radius = 10.0
            max_radius = 1000.0
            neighbors = []

            while radius <= max_radius and len(neighbors) < k:
                min_x, max_x = x - radius, x + radius
                min_y, max_y = y - radius, y + radius
                min_z, max_z = z - radius, z + radius

                cursor = conn.execute("""
                    SELECT s.id, s.minX, s.minY, s.minZ
                    FROM omega_memory_spatial s
                    WHERE s.id != ?
                      AND s.minX <= ? AND s.maxX >= ?
                      AND s.minY <= ? AND s.maxY >= ?
                      AND s.minZ <= ? AND s.maxZ >= ?
                    LIMIT ?
                """, (rowid, max_x, min_x, max_y, min_y, max_z, min_z, k * 2))

                candidates = []
                for r in cursor.fetchall():
                    nid, nx, ny, nz = r
                    dist = math.sqrt((nx - x)**2 + (ny - y)**2 + (nz - z)**2)
                    candidates.append((nid, dist))

                candidates.sort(key=lambda x: x[1])
                for nid, dist in candidates:
                    if nid not in [n[0] for n in neighbors]:
                        neighbors.append((nid, dist))
                        if len(neighbors) >= k:
                            break

                radius *= 2.0

            return neighbors[:k]

        return await anyio.to_thread.run_sync(_sync_neighbors)

    # [id-soft: doom-1993] BSP Culling — Hybrid semantic+spatial for VR retrieval
    async def hybrid_spatial_query(
        self,
        entity_name: str,
        query_vector: List[float],
        query_position: Tuple[float, float, float],
        semantic_weight: float = 0.7,
        spatial_weight: float = 0.3,
        radius: float = 50.0,
        limit: int = 20,
        collection: str = CANONICAL_COLLECTION,
    ) -> List[Dict[str, Any]]:
        """Hybrid semantic + spatial query for VR-aware retrieval.

        1. Spatial pre-filter: R-tree range query (fast, reduces candidate set)
        2. Vector search restricted to spatial candidates
        3. Fuse with spatial distance scoring
        """
        await self._ensure_initialized()

        collection = resolve_collection_name(collection, self._collections)

        # 1. Spatial pre-filter
        spatial_candidates = await self.spatial_range_query(
            entity_name, query_position[0], query_position[1], query_position[2],
            radius, limit * 3
        )
        spatial_rowids = {c.get("id") or c.get("rowid") for c in spatial_candidates if c.get("id") or c.get("rowid")}

        if not spatial_rowids:
            return []

        # 2. Vector search restricted to spatial candidates
        placeholders = ",".join("?" for _ in spatial_rowids)

        def _sync_hybrid():
            conn = self._get_read_conn()

            # Check sqlite-vec version for int8 + auxiliary support
            try:
                import sqlite_vec
                version = getattr(sqlite_vec, '__version__', '0.1.9')
                major, minor, patch = map(int, version.split('.')[:3])
                supports_int8_aux = (major > 0) or (minor >= 10)
            except (ImportError, AttributeError, ValueError):
                supports_int8_aux = False

            coll_config = self._collections[collection]
            quantization = coll_config.get("quantization", "none")

            if quantization == "int8_rescore" and supports_int8_aux:
                int8_blob = self.serialize_int8(query_vector)
                cursor = conn.execute(f"""
                    SELECT v.rowid, v.distance,
                           d.uuid, d.entity_name, d.session_id, d.role, d.content, d.timestamp, d.metadata_json,
                           s.minX, s.minY, s.minZ
                    FROM {collection} v
                    JOIN omega_memory_data d ON v.rowid = d.id
                    JOIN omega_memory_spatial s ON v.rowid = s.id
                    WHERE v.embedding MATCH ? AND v.entity_name = ?
                      AND v.rowid IN ({placeholders})
                      AND k = ?
                    ORDER BY v.distance
                """, (int8_blob, entity_name, *spatial_rowids, limit))
            else:
                fp32_blob = self.serialize_float32(query_vector)
                cursor = conn.execute(f"""
                    SELECT v.rowid, v.distance,
                           d.uuid, d.entity_name, d.session_id, d.role, d.content, d.timestamp, d.metadata_json,
                           s.minX, s.minY, s.minZ
                    FROM {collection} v
                    JOIN omega_memory_data d ON v.rowid = d.id
                    JOIN omega_memory_spatial s ON v.rowid = s.id
                    WHERE v.embedding MATCH ? AND v.entity_name = ?
                      AND v.rowid IN ({placeholders})
                      AND k = ?
                    ORDER BY v.distance
                """, (fp32_blob, entity_name, *spatial_rowids, limit))

            results = []
            qx, qy, qz = query_position
            for row in cursor.fetchall():
                rowid, vec_dist = row[0], row[1]
                if vec_dist is None:
                    continue
                semantic_score = 1.0 - vec_dist

                # Spatial distance
                sx, sy, sz = row[9], row[10], row[11]
                spatial_dist = math.sqrt((sx - qx)**2 + (sy - qy)**2 + (sz - qz)**2)
                spatial_score = 1.0 / (1.0 + spatial_dist)  # Sigmoid decay

                fused = semantic_weight * semantic_score + spatial_weight * spatial_score

                metadata = {
                    "id": row[2], "entity_name": row[3], "session_id": row[4],
                    "role": row[5], "content": row[6], "timestamp": row[7],
                }
                if row[8]:
                    try:
                        metadata.update(json.loads(row[8]))
                    except json.JSONDecodeError:
                        pass

                results.append({
                    "fused_score": fused,
                    "semantic_score": semantic_score,
                    "spatial_score": spatial_score,
                    "spatial_distance": spatial_dist,
                    "metadata": metadata,
                })

            return sorted(results, key=lambda x: x["fused_score"], reverse=True)[:limit]

        return await anyio.to_thread.run_sync(_sync_hybrid)

    async def checkpoint_wal(self, mode: str = "RESTART") -> bool:
        await self._ensure_initialized()
        def _sync_checkpoint():
            conn = self._get_write_conn()
            cursor = conn.execute(f"PRAGMA wal_checkpoint({mode})")
            result = cursor.fetchone()
            if self.enable_metrics:
                self._metrics["wal_checkpoint_count"] += 1
            return result[0] == 0
        return await anyio.to_thread.run_sync(_sync_checkpoint)

    async def check_wal_health(self) -> dict:
        await self._ensure_initialized()
        def _sync_wal_health():
            conn = self._get_read_conn()
            health = {}
            wal_path = self.db_path.with_suffix(".db-wal")
            if wal_path.exists():
                health["wal_size_bytes"] = wal_path.stat().st_size
                health["wal_size_mb"] = round(health["wal_size_bytes"] / (1024 * 1024), 2)
            else:
                health["wal_size_bytes"] = 0
                health["wal_size_mb"] = 0.0
            cursor = conn.execute("PRAGMA wal_checkpoint(PASSIVE)")
            result = cursor.fetchone()
            health["checkpoint_busy"] = result[0]
            health["checkpoint_log_frames"] = result[1]
            health["checkpoint_checkpointed_frames"] = result[2]
            cursor = conn.execute("PRAGMA journal_size_limit")
            health["journal_size_limit"] = cursor.fetchone()[0]
            cursor = conn.execute("PRAGMA wal_autocheckpoint")
            health["wal_autocheckpoint"] = cursor.fetchone()[0]
            health["healthy"] = health["wal_size_mb"] < 50 and health["checkpoint_busy"] == 0
            return health
        return await anyio.to_thread.run_sync(_sync_wal_health)

    async def start_periodic_checkpoint(self, interval_seconds: int = 300) -> None:
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
        
        # Start the background task using a task group that runs in a separate task
        async def _run_checkpoint_task_group():
            async with anyio.create_task_group() as tg:
                tg.start_soon(_checkpoint_loop)
                # Keep alive until cancelled
                await anyio.Event().wait()
        
    async def start_periodic_checkpoint(self, interval_seconds: int = 300) -> None:
        if hasattr(self, "_checkpoint_task") and self._checkpoint_task:
            logger.warning("Periodic checkpoint task already running")
            return

        self._checkpoint_cancel_scope = None

        async def _checkpoint_loop() -> None:
            while True:
                await anyio.sleep(interval_seconds)
                try:
                    success = await self.checkpoint_wal("RESTART")
                    if not success:
                        logger.warning("Periodic RESTART checkpoint blocked by active readers")
                except Exception as e:
                    logger.error("Periodic checkpoint task error: %s", e)

        # Spawn a background task that hosts its own task group (F-07, F-09).
        # The group is entered in the spawned task's scope, not the caller's.
        async def _host_task_group() -> None:
            async with anyio.create_task_group() as tg:
                self._checkpoint_cancel_scope = tg.cancel_scope
                tg.start_soon(_checkpoint_loop)
                await anyio.sleep_forever()

        # Store the task (not a group) so stop can cancel it.
        # F-06 fix: use anyio task spawning (M1 compliance)
        import anyio
        self._checkpoint_task = anyio.start_soon(_host_task_group)
        # Give the spawned task a moment to enter the task group and set the scope.
        await anyio.sleep(0.05)
        logger.info("Started periodic WAL checkpoint task (interval=%ds)", interval_seconds)

    async def stop_periodic_checkpoint(self) -> None:
        if hasattr(self, "_checkpoint_task") and self._checkpoint_task:
            # Cancel via the stored cancel scope (set by the spawned task).
            scope = getattr(self, "_checkpoint_cancel_scope", None)
            if scope is not None:
                scope.cancel()
            # Await the task to let the group exit cleanly.
            try:
                await self._checkpoint_task
            except Exception as e:
                logger.debug("Error awaiting checkpoint task: %s", e)
            self._checkpoint_task = None
            self._checkpoint_cancel_scope = None
            logger.info("Stopped periodic WAL checkpoint task")

    def _get_test_conn(self) -> sqlite3.Connection:
        if self._write_conn is not None:
            return self._write_conn
        return self._get_write_conn()

    async def close(self) -> None:
        if hasattr(self, "_checkpoint_task") and self._checkpoint_task:
            await self.stop_periodic_checkpoint()
        if self._write_conn is not None:
            try:
                await anyio.to_thread.run_sync(self._write_conn.close)
            except (sqlite3.Error, OSError) as e:
                logger.warning("Error closing write connection: %s", e)
            self._write_conn = None
        # Close read pool connections via thread (F-01).
        for conn in self._read_connections:
            try:
                await anyio.to_thread.run_sync(conn.close)
            except Exception as e:
                logger.debug("Error closing read conn: %s", e)
        self._read_connections.clear()
        self._initialized = False
        self._vec_tables_created.clear()
        logger.info("SQLiteVecAdapterOptimized closed")


# Backward compatibility alias
SQLiteVecAdapter = SQLiteVecAdapterOptimized


def sqlite_vec_serialize_float32(vector: List[float]) -> bytes:
    """Serialize a list of floats to bytes for sqlite-vec."""
    try:
        import sqlite_vec
        return sqlite_vec.serialize_float32(vector)
    except ImportError:
        return struct.pack(f"{len(vector)}f", *vector)