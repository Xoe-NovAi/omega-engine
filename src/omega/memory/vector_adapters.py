"""Sovereign Vector Store Adapters for Omega Memory.
AP: AP-VECTOR-ADAPTERS-v1.0.0
"""
# DocRef: docs/architecture/MEMORY_STORE_DEEP_DIVE.md

import logging
import uuid
import math
import anyio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

from omega.errors import OmegaError, ProviderError, ProviderUnavailableError

def _lazy_qdrant():
    """Lazy-import Qdrant client — only triggered when QdrantAdapter is instantiated.
    
    This allows the engine to start without Qdrant installed, supporting
    the M2 Engine-Stack Firewall and enabling clean Qdrant decommission (Strike 10)."""
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qmodels
    from qdrant_client.models import PayloadSchemaType
    return QdrantClient, qmodels, PayloadSchemaType

logger = logging.getLogger(__name__)

class IVectorStoreAdapter(ABC):
    """Abstract base class for vector store adapters.
    
    Ensures the Omega Engine remains DB-agnostic for semantic memory.
    """
    
    @abstractmethod
    async def upsert(
        self, 
        entity_name: str, 
        vector: List[float], 
        metadata: Dict[str, Any], 
        id: Optional[str] = None
    ) -> str:
        """Insert or update a vector and its metadata."""
        pass
    
    @abstractmethod
    async def query(
        self, 
        entity_name: str, 
        vector: List[float], 
        limit: int = 10, 
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[float, Dict[str, Any]]]:
        """Query the vector store for the most similar entries."""
        pass
    
    @abstractmethod
    async def delete(self, entity_name: str, ids: List[str]) -> bool:
        """Delete specific vectors by ID."""
        pass
    
    async def delete_session(self, entity_name: str, session_id: str) -> bool:
        """Delete all vectors associated with a specific session.
        
        Default implementation returns False. Subclasses should override.
        """
        return False
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Get the current health and status of the vector store."""
        pass

class MemoryVectorAdapter(IVectorStoreAdapter):
    """In-memory stub for vector store. Used when Qdrant is unavailable.
    
    Implements basic cosine similarity for sovereign fallback.
    """
    
    def __init__(self):
        # Store: {entity_name: [(id, vector, metadata), ...]}
        self._store: Dict[str, List[Tuple[str, List[float], Dict[str, Any]]]] = {}
        logger.info("MemoryVectorAdapter initialized as sovereign fallback.")

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        if len(v1) != len(v2):
            return 0.0
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm_a = math.sqrt(sum(a * a for a in v1))
        norm_b = math.sqrt(sum(b * b for b in v2))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    async def upsert(
        self, 
        entity_name: str, 
        vector: List[float], 
        metadata: Dict[str, Any], 
        id: Optional[str] = None
    ) -> str:
        if entity_name not in self._store:
            self._store[entity_name] = []
        
        point_id = id or str(uuid.uuid4())
        
        # Update if exists, else append
        for i, (pid, _, _) in enumerate(self._store[entity_name]):
            if pid == point_id:
                self._store[entity_name][i] = (point_id, vector, metadata)
                return point_id
        
        self._store[entity_name].append((point_id, vector, metadata))
        return point_id

    async def query(
        self, 
        entity_name: str, 
        vector: List[float], 
        limit: int = 10, 
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[float, Dict[str, Any]]]:
        if entity_name not in self._store:
            return []
        
        results = []
        for pid, v, meta in self._store[entity_name]:
            # Apply simple filter if provided
            if filter:
                match = True
                for k, v_filter in filter.items():
                    if meta.get(k) != v_filter:
                        match = False
                        break
                if not match:
                    continue
            
            score = self._cosine_similarity(vector, v)
            results.append((score, meta))
        
        # Sort by score descending
        results.sort(key=lambda x: x[0], reverse=True)
        return results[:limit]

    async def delete(self, entity_name: str, ids: List[str]) -> bool:
        if entity_name not in self._store:
            return False
        
        initial_count = len(self._store[entity_name])
        self._store[entity_name] = [
            item for item in self._store[entity_name] if item[0] not in ids
        ]
        return len(self._store[entity_name]) < initial_count

    async def delete_session(self, entity_name: str, session_id: str) -> bool:
        if entity_name not in self._store:
            return False
        
        initial_count = len(self._store[entity_name])
        self._store[entity_name] = [
            item for item in self._store[entity_name] if item[2].get("session_id") != session_id
        ]
        return len(self._store[entity_name]) < initial_count

    async def get_status(self) -> Dict[str, Any]:
        total_vectors = sum(len(v) for v in self._store.values())
        return {
            "status": "healthy",
            "type": "in-memory-stub",
            "vector_count": total_vectors,
            "entities_tracked": len(self._store)
        }

# DEPRECATED: QdrantAdapter retained for heritage reference only.
# [heritage: qdrant-2021] Vector database — Qdrant implementation.
# Use SQLiteVecAdapter for unified fabric (D225).
class QdrantAdapter(IVectorStoreAdapter):
    """Qdrant implementation of the vector store adapter."""

    def __init__(self, host: str = "localhost", port: int = 6333, collection_name: str = "omega_memory"):
        QdrantClient, qmodels, PayloadSchemaType = _lazy_qdrant()
        self._QdrantClient = QdrantClient
        self._qmodels = qmodels
        self._PayloadSchemaType = PayloadSchemaType
        self.client = QdrantClient(host=host, port=port, check_compatibility=False)
        self.collection_name = collection_name
        self._initialized = False

    async def _ensure_collection(self, vector_size: int):
        """Ensure the Qdrant collection exists with the correct configuration and dimensionality."""
        if self._initialized:
            return
        
        def _sync_ensure():
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if exists:
                # Check for dimensional mismatch
                col_info = self.client.get_collection(self.collection_name)
                current_dim = col_info.config.params.vectors.size
                if current_dim != vector_size:
                    logger.warning(
                        f"Qdrant dimensional mismatch for {self.collection_name}: "
                        f"expected {vector_size}, found {current_dim}. Recreating collection..."
                    )
                    self.client.delete_collection(collection_name=self.collection_name)
                    exists = False # Force recreation

            if not exists:
                logger.info(f"Creating Qdrant collection: {self.collection_name} (size={vector_size})")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=self._qmodels.VectorParams(
                        size=vector_size, 
                        distance=self._qmodels.Distance.COSINE
                    ),
                    # Enable scalar quantization for H2-S4 performance tuning
                    quantization_config=self._qmodels.ScalarQuantization(
                        scalar=self._qmodels.ScalarQuantizationConfig(
                            type=self._qmodels.ScalarType.INT8,
                            always_ram=True
                        )
                    )
                )

        try:
            await anyio.to_thread.run_sync(_sync_ensure)
            # ── Payload Indexes (62x speedup on selective filters) ──
            # [heritage: qdrant-2021] Filter-before-search optimization
            await self.ensure_payload_indexes()
            self._initialized = True
        except (RuntimeError, OSError) as e:
            logger.error(f"Failed to initialize Qdrant collection: {e}", exc_info=True)
            raise ProviderUnavailableError("qdrant", f"Qdrant initialization failed: {e}", raw_error=e) from e

    async def ensure_payload_indexes(self) -> None:
        """Create payload indexes for entity_name and session_id filtering.

        [heritage: qdrant-2021] Payload indexes let Qdrant apply filters at
        search time without scanning every point — the sovereign equivalent of
        an indexed column. Without them, filtered queries on entity_name /
        session_id degrade to full-collection scans.

        Best-effort: if an index already exists (e.g. after a restart), Qdrant
        raises a recoverable error which we log and ignore (idempotent-safe).
        """
        indexes = [
            ("entity_name", self._PayloadSchemaType.KEYWORD),
            ("session_id", self._PayloadSchemaType.KEYWORD),
        ]
        for field_name, field_schema in indexes:
            try:
                def _sync_create_index():
                    self.client.create_payload_index(
                        collection_name=self.collection_name,
                        field_name=field_name,
                        field_schema=field_schema,
                    )
                await anyio.to_thread.run_sync(_sync_create_index)
            except (RuntimeError, OSError) as e:
                # Index may already exist after a restart — idempotent-safe
                if "already exists" not in str(e).lower():
                    logger.warning("Payload index creation failed for %s: %s", field_name, e)
            except Exception as e:  # noqa: BLE001 — best-effort optimization
                # Payload indexes are a performance optimization, not a
                # correctness requirement. Log (never silently swallow, M9) and
                # continue so collection creation is not blocked.
                if "already exists" not in str(e).lower():
                    logger.warning("Payload index creation skipped for %s: %s", field_name, e)

    async def upsert(
        self, 
        entity_name: str, 
        vector: List[float], 
        metadata: Dict[str, Any], 
        id: Optional[str] = None
    ) -> str:
        await self._ensure_collection(len(vector))
        
        # Ensure entity_name is in metadata for filtering
        payload = {**metadata, "entity_name": entity_name}
        
        try:
            # Use a generated ID if none provided
            point_id = id or uuid.uuid4()
            
            def _sync_upsert():
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=[
                        self._qmodels.PointStruct(
                            id=point_id,
                            vector=vector,
                            payload=payload
                        )
                    ]
                )
            
            await anyio.to_thread.run_sync(_sync_upsert)
            return str(point_id)
        except (RuntimeError, OSError) as e:
            logger.error(f"Qdrant upsert failed for {entity_name}: {e}", exc_info=True)
            raise ProviderError("qdrant", f"Qdrant upsert failed: {e}", raw_error=e) from e

    async def query(
        self, 
        entity_name: str, 
        vector: List[float], 
        limit: int = 10, 
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[float, Dict[str, Any]]]:
        await self._ensure_collection(len(vector))
        
        # Always filter by entity_name to ensure sovereign isolation
        q_filter = self._qmodels.Filter(
            must=[
                self._qmodels.FieldCondition(
                    key="entity_name", 
                    match=self._qmodels.MatchValue(value=entity_name)
                )
            ]
        )
        
        # Merge with additional filters if provided
        if filter:
            # Simple implementation: add all filter keys as MatchValue conditions
            for k, v in filter.items():
                q_filter.must.append(
                    self._qmodels.FieldCondition(key=k, match=self._qmodels.MatchValue(value=v))
                )

        try:
            def _sync_search():
                result = self.client.query_points(
                    collection_name=self.collection_name,
                    query=vector,
                    limit=limit,
                    query_filter=q_filter,
                    with_payload=True
                )
                return result.points
            
            results = await anyio.to_thread.run_sync(_sync_search)
            return [(res.score, res.payload) for res in results]
        except (RuntimeError, OSError) as e:
            logger.error(f"Qdrant query failed for {entity_name}: {e}", exc_info=True)
            raise ProviderError("qdrant", f"Qdrant query failed: {e}", raw_error=e) from e

    async def delete(self, entity_name: str, ids: List[str]) -> bool:
        if not ids:
            return False
        try:
            def _sync_delete():
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=self._qmodels.FilterSelector(
                        filter=self._qmodels.Filter(
                            must=[
                                self._qmodels.FieldCondition(key="entity_name", match=self._qmodels.MatchValue(value=entity_name)),
                            ]
                        )
                    ),
                    wait=True,
                )
            await anyio.to_thread.run_sync(_sync_delete)
            # Individual point deletion by ID
            def _sync_delete_ids():
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=self._qmodels.PointIdsList(points=ids),
                    wait=True,
                )
            await anyio.to_thread.run_sync(_sync_delete_ids)
            return True
        except (RuntimeError, OSError) as e:
            logger.error(f"Qdrant delete failed for {entity_name}: {e}", exc_info=True)
            raise ProviderError("qdrant", f"Qdrant delete failed: {e}", raw_error=e) from e

    async def delete_session(self, entity_name: str, session_id: str) -> bool:
        try:
            def _sync_delete_session():
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=self._qmodels.FilterSelector(
                        filter=self._qmodels.Filter(
                            must=[
                                self._qmodels.FieldCondition(key="entity_name", match=self._qmodels.MatchValue(value=entity_name)),
                                self._qmodels.FieldCondition(key="session_id", match=self._qmodels.MatchValue(value=session_id))
                            ]
                        )
                    )
                )
            await anyio.to_thread.run_sync(_sync_delete_session)
            return True
        except (RuntimeError, OSError) as e:
            logger.error(f"Qdrant delete_session failed for {entity_name}/{session_id}: {e}", exc_info=True)
            raise ProviderError("qdrant", f"Qdrant delete_session failed: {e}", raw_error=e) from e

    async def get_status(self) -> Dict[str, Any]:
        try:
            def _sync_get_status():
                # Use get_collection() to get full CollectionInfo with points_count
                col_info = self.client.get_collection(self.collection_name)
                return col_info.points_count if col_info else 0
            
            points_count = await anyio.to_thread.run_sync(_sync_get_status)
            return {
                "status": "healthy",
                "collection": self.collection_name,
                "vector_count": points_count
            }
        except (RuntimeError, OSError) as e:
            return {"status": "unhealthy", "error": str(e)}
