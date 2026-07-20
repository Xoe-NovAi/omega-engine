# AP: AP-D283-MNEMOSYNE-v1.0.0
# 🔱 Archival Memory — Vector + KV + Graph Storage for Omega Engine
# ⬡ OMEGA ⬡ MEMORY ⬡ archival.py
#
# Implements Letta 2026 Archival tier: arbitrary facts stored in vector + KV + graph.
# Agent tools: archival_memory_insert, archival_memory_search
# Integrates with existing sqlite-vec unified fabric.

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import anyio

from .blocks import MemoryBlock, BlockCategory
from .sqlite_vec_adapter import SQLiteVecAdapter
from .vector_adapters import IVectorStoreAdapter
from omega.errors import OmegaError
from omega.infra.sqlite_policy import get_sqlite_connection

logger = logging.getLogger(__name__)


class ArchivalMemory:
    """
    Archival tier for arbitrary facts (Letta 2026 pattern).
    
    Three storage backends unified:
    - Vector: Semantic search via sqlite-vec (existing unified fabric)
    - KV: Exact key-value lookups via metadata table
    - Graph: Entity relationships via edge table (future)
    
    Agent tools:
    - archival_memory_insert: Store fact with optional metadata
    - archival_memory_search: Semantic search with filters
    """
    
    def __init__(
        self,
        vector_store: Optional[IVectorStoreAdapter] = None,
        db_path: Optional[str] = None,
    ):
        self.vector_store = vector_store
        self.db_path = db_path
        self._conn = None
        self._lock = anyio.Lock()
        self._initialized = False
    
    def _get_conn(self):
        """Get SQLite connection for KV/graph storage (FS-B4: profiled)."""
        if self._conn is None:
            from omega.memory_store import _get_memory_dir
            
            if self.db_path is None:
                self.db_path = str(_get_memory_dir() / "omega_memory.db")
            
            # FS-B4: Use sqlite_policy memory profile (32MB cache, D-282)
            self._conn = get_sqlite_connection(Path(self.db_path), profile="memory")
            
            # Operational PRAGMA (per A13 — not connection setup)
            self._conn.execute("PRAGMA optimize=0x10002")
        return self._conn
    
    async def _ensure_initialized(self) -> None:
        """Create archival tables if not exist."""
        if self._initialized:
            return
        
        def _sync_init():
            conn = self._get_conn()
            conn.execute("BEGIN IMMEDIATE")
            
            # KV store for exact lookups
            conn.execute("""
                CREATE TABLE IF NOT EXISTS archival_kv (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    metadata_json TEXT DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Graph edges for entity relationships (future)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS archival_edges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_entity TEXT NOT NULL,
                    target_entity TEXT NOT NULL,
                    relation_type TEXT NOT NULL,
                    properties_json TEXT DEFAULT '{}',
                    created_at TEXT NOT NULL
                )
            """)
            
            # Index for graph queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_archival_edges_source 
                ON archival_edges(source_entity)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_archival_edges_target 
                ON archival_edges(target_entity)
            """)
            
            conn.commit()
        
        await anyio.to_thread.run_sync(_sync_init)
        self._initialized = True
        logger.info("ArchivalMemory initialized")
    
    # ── Vector Operations (delegate to sqlite-vec unified fabric) ─────────────
    
    async def insert(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        vector: Optional[List[float]] = None,
    ) -> str:
        """
        Insert a fact into archival memory.
        
        Args:
            content: The fact/text to store
            metadata: Optional metadata (tags, source, category, etc.)
            vector: Optional pre-computed embedding (if None, vector_store must be set)
        
        Returns:
            UUID of the inserted record
        """
        await self._ensure_initialized()
        
        record_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        meta = metadata or {}
        meta["archival_id"] = record_id
        meta["created_at"] = now
        
        # Store in vector store if available
        if self.vector_store and vector:
            await self.vector_store.upsert(
                entity_name=meta.get("entity_name", "archival"),
                vector=vector,
                metadata={
                    **meta,
                    "content": content,
                    "archival_id": record_id,
                },
                id=record_id,
            )
        elif self.vector_store and not vector:
            logger.warning("vector_store set but no vector provided; content not indexed for semantic search")
        
        # Store in KV for exact retrieval
        def _sync_kv_insert():
            conn = self._get_conn()
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                "INSERT OR REPLACE INTO archival_kv (key, value, metadata_json, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (record_id, content, json.dumps(meta), now, now)
            )
            conn.commit()
        
        await anyio.to_thread.run_sync(_sync_kv_insert)
        
        logger.debug(f"Inserted archival record {record_id}")
        return record_id
    
    async def search(
        self,
        query: str,
        vector: Optional[List[float]] = None,
        limit: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[float, Dict[str, Any]]]:
        """
        Search archival memory.
        
        Args:
            query: Text query (for logging/debugging)
            vector: Query embedding vector (required if vector_store available)
            limit: Max results
            filter_metadata: Metadata filters (entity_name, tags, etc.)
        
        Returns:
            List of (score, metadata) tuples
        """
        if not self.vector_store or not vector:
            logger.warning("No vector_store or vector provided; returning empty results")
            return []
        
        # Build filter for vector store
        filter_dict = filter_metadata or {}
        
        results = await self.vector_store.query(
            entity_name=filter_dict.get("entity_name", "archival"),
            vector=vector,
            limit=limit,
            filter=filter_dict,
        )
        
        # Format results
        formatted = []
        for score, metadata in results:
            formatted.append((score, metadata))
        
        return formatted
    
    async def get(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Get a record by exact ID (KV lookup)."""
        await self._ensure_initialized()
        
        def _sync_get():
            conn = self._get_conn()
            row = conn.execute(
                "SELECT value, metadata_json, created_at, updated_at FROM archival_kv WHERE key = ?",
                (record_id,)
            ).fetchone()
            if row:
                return {
                    "id": record_id,
                    "content": row["value"],
                    "metadata": json.loads(row["metadata_json"]),
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
            return None
        
        return await anyio.to_thread.run_sync(_sync_get)
    
    async def delete(self, record_id: str) -> bool:
        """Delete a record by ID."""
        await self._ensure_initialized()
        
        # Delete from KV
        def _sync_delete():
            conn = self._get_conn()
            conn.execute("BEGIN IMMEDIATE")
            cursor = conn.execute("DELETE FROM archival_kv WHERE key = ?", (record_id,))
            conn.commit()
            return cursor.rowcount > 0
        
        kv_deleted = await anyio.to_thread.run_sync(_sync_delete)
        
        # Note: Vector store deletion would need the rowid, which we don't have here
        # In production, we'd maintain a mapping table
        
        return kv_deleted
    
    # ── Graph Operations (future) ─────────────────────────────────────────────
    
    async def add_edge(
        self,
        source: str,
        target: str,
        relation: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Add a relationship edge between entities."""
        await self._ensure_initialized()
        
        def _sync_add_edge():
            conn = self._get_conn()
            conn.execute("BEGIN IMMEDIATE")
            cursor = conn.execute(
                "INSERT INTO archival_edges (source_entity, target_entity, relation_type, properties_json, created_at) VALUES (?, ?, ?, ?, ?)",
                (source, target, relation, json.dumps(properties or {}), datetime.now(timezone.utc).isoformat())
            )
            conn.commit()
            return cursor.lastrowid
        
        return await anyio.to_thread.run_sync(_sync_add_edge)
    
    async def get_edges(
        self,
        entity: str,
        direction: str = "both",  # "out", "in", "both"
        relation: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get edges for an entity."""
        await self._ensure_initialized()
        
        def _sync_get_edges():
            conn = self._get_conn()
            
            if direction == "out":
                query = "SELECT * FROM archival_edges WHERE source_entity = ?"
                params = [entity]
            elif direction == "in":
                query = "SELECT * FROM archival_edges WHERE target_entity = ?"
                params = [entity]
            else:
                query = "SELECT * FROM archival_edges WHERE source_entity = ? OR target_entity = ?"
                params = [entity, entity]
            
            if relation:
                query += " AND relation_type = ?"
                params.append(relation)
            
            rows = conn.execute(query, params).fetchall()
            return [
                {
                    "id": row["id"],
                    "source": row["source_entity"],
                    "target": row["target_entity"],
                    "relation": row["relation_type"],
                    "properties": json.loads(row["properties_json"]),
                    "created_at": row["created_at"],
                }
                for row in rows
            ]
        
        return await anyio.to_thread.run_sync(_sync_get_edges)


# ── Agent Tools (Letta 2026 pattern) ──────────────────────────────────────────

class ArchivalTools:
    """
    Agent-callable tools for archival memory.
    
    Mirrors Letta's archival_memory_insert and archival_memory_search.
    """
    
    def __init__(self, archival: ArchivalMemory, embedding_provider=None):
        self.archival = archival
        self.embedding_provider = embedding_provider
    
    async def archival_memory_insert(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        requester_entity: str = "unknown",
    ) -> Dict[str, Any]:
        """
        Insert a fact into archival memory.
        
        Args:
            content: The fact/text to store
            metadata: Optional metadata (tags, category, source, etc.)
            requester_entity: Entity making the request (for audit)
        
        Returns:
            Dict with success status and record_id
        """
        meta = metadata or {}
        meta["inserted_by"] = requester_entity
        meta["inserted_at"] = datetime.now(timezone.utc).isoformat()
        
        # Generate embedding if provider available
        vector = None
        if self.embedding_provider:
            try:
                vector = await self.embedding_provider.embed(content)
            except Exception as e:
                logger.warning(f"Failed to generate embedding for archival insert: {e}")
        
        record_id = await self.archival.insert(content, meta, vector)
        
        return {
            "success": True,
            "record_id": record_id,
            "content": content,
        }
    
    async def archival_memory_search(
        self,
        query: str,
        limit: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
        requester_entity: str = "unknown",
    ) -> Dict[str, Any]:
        """
        Search archival memory semantically.
        
        Args:
            query: Search query text
            limit: Max results
            filter_metadata: Metadata filters
            requester_entity: Entity making the request (for audit)
        
        Returns:
            Dict with results list
        """
        # Generate query embedding
        vector = None
        if self.embedding_provider:
            try:
                vector = await self.embedding_provider.embed(query)
            except Exception as e:
                logger.warning(f"Failed to generate query embedding: {e}")
                return {"success": False, "error": "Embedding generation failed", "results": []}
        
        if not vector:
            return {"success": False, "error": "No embedding provider available", "results": []}
        
        results = await self.archival.search(query, vector, limit, filter_metadata)
        
        formatted = []
        for score, metadata in results:
            formatted.append({
                "score": score,
                "content": metadata.get("content", ""),
                "metadata": {k: v for k, v in metadata.items() if k != "content"},
            })
        
        return {
            "success": True,
            "query": query,
            "results": formatted,
        }


# Global instance
_archival_memory: Optional[ArchivalMemory] = None


def get_archival_memory(vector_store: Optional[IVectorStoreAdapter] = None) -> ArchivalMemory:
    """Get or create the global archival memory instance."""
    global _archival_memory
    if _archival_memory is None:
        _archival_memory = ArchivalMemory(vector_store=vector_store)
    return _archival_memory