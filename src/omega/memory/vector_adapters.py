"""Sovereign Vector Store Adapters for Omega Memory.
AP: AP-VECTOR-ADAPTERS-v1.0.0
"""

import logging
import uuid
import math
import anyio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from omega.errors import OmegaError, ProviderError, ProviderUnavailableError

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

class QdrantAdapter(IVectorStoreAdapter):
    """Qdrant implementation of the vector store adapter."""

    def __init__(self, host: str = "localhost", port: int = 6333, collection_name: str = "omega_memory"):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self._initialized = False

    async def _ensure_collection(self, vector_size: int):
        """Ensure the Qdrant collection exists with the correct configuration."""
        if self._initialized:
            return
        
        def _sync_ensure():
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if not exists:
                logger.info(f"Creating Qdrant collection: {self.collection_name} (size={vector_size})")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qmodels.VectorParams(
                        size=vector_size, 
                        distance=qmodels.Distance.COSINE
                    ),
                    # Enable scalar quantization for H2-S4 performance tuning
                    quantization_config=qmodels.ScalarQuantization(
                        scalar=qmodels.ScalarQuantizationConfig(
                            type=qmodels.ScalarType.INT8,
                            always_ram=True
                        )
                    )
                )

        try:
            await anyio.to_thread.run_sync(_sync_ensure)
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant collection: {e}", exc_info=True)
            raise ProviderUnavailableError("qdrant", f"Qdrant initialization failed: {e}", raw_error=e) from e

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
                        qmodels.PointStruct(
                            id=point_id,
                            vector=vector,
                            payload=payload
                        )
                    ]
                )
            
            await anyio.to_thread.run_sync(_sync_upsert)
            return str(point_id)
        except Exception as e:
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
        q_filter = qmodels.Filter(
            must=[
                qmodels.FieldCondition(
                    key="entity_name", 
                    match=qmodels.MatchValue(value=entity_name)
                )
            ]
        )
        
        # Merge with additional filters if provided
        if filter:
            # Simple implementation: add all filter keys as MatchValue conditions
            for k, v in filter.items():
                q_filter.must.append(
                    qmodels.FieldCondition(key=k, match=qmodels.MatchValue(value=v))
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
        except Exception as e:
            logger.error(f"Qdrant query failed for {entity_name}: {e}", exc_info=True)
            raise ProviderError("qdrant", f"Qdrant query failed: {e}", raw_error=e) from e

    async def delete(self, entity_name: str, ids: List[str]) -> bool:
        try:
            def _sync_delete():
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=qmodels.FilterSelector(
                        filter=qmodels.Filter(
                            must=[
                                qmodels.FieldCondition(key="entity_name", match=qmodels.MatchValue(value=entity_name)),
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
                    points_selector=qmodels.PointIdsList(points=ids),
                    wait=True,
                )
            await anyio.to_thread.run_sync(_sync_delete_ids)
            return True
        except Exception as e:
            logger.error(f"Qdrant delete failed for {entity_name}: {e}", exc_info=True)
            raise ProviderError("qdrant", f"Qdrant delete failed: {e}", raw_error=e) from e

    async def delete_session(self, entity_name: str, session_id: str) -> bool:
        try:
            def _sync_delete_session():
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=qmodels.FilterSelector(
                        filter=qmodels.Filter(
                            must=[
                                qmodels.FieldCondition(key="entity_name", match=qmodels.MatchValue(value=entity_name)),
                                qmodels.FieldCondition(key="session_id", match=qmodels.MatchValue(value=session_id))
                            ]
                        )
                    )
                )
            await anyio.to_thread.run_sync(_sync_delete_session)
            return True
        except Exception as e:
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
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
