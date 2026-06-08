"""Sovereign Vector Store Adapters for Omega Memory.
AP: AP-VECTOR-ADAPTERS-v1.0.0
"""

import logging
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

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Get the current health and status of the vector store."""
        pass

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
        
        try:
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
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant collection: {e}", exc_info=True)
            raise ProviderUnavailableError(f"Qdrant initialization failed: {e}", raw_error=e) from e

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
            point_id = id or self.client.uuid.uuid4()
            
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
            return str(point_id)
        except Exception as e:
            logger.error(f"Qdrant upsert failed for {entity_name}: {e}", exc_info=True)
            raise ProviderError(f"Qdrant upsert failed: {e}", raw_error=e) from e

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
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=vector,
                limit=limit,
                query_filter=q_filter,
                with_payload=True
            )
            
            return [(res.score, res.payload) for res in results]
        except Exception as e:
            logger.error(f"Qdrant query failed for {entity_name}: {e}", exc_info=True)
            raise ProviderError(f"Qdrant query failed: {e}", raw_error=e) from e

    async def delete(self, entity_name: str, ids: List[str]) -> bool:
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=qmodels.FilterSelector(
                    filter=qmodels.Filter(
                        must=[
                            qmodels.FieldCondition(key="entity_name", match=qmodels.MatchValue(value=entity_name)),
                            qmodels.FieldCondition(key="id", match=qmodels.MatchValue(value=ids)) # This is simplified
                        ]
                    )
                )
            )
            # Note: Qdrant delete by IDs is usually simpler:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=qmodels.PointIdsList(points=ids)
            )
            return True
        except Exception as e:
            logger.error(f"Qdrant delete failed for {entity_name}: {e}", exc_info=True)
            raise ProviderError(f"Qdrant delete failed: {e}", raw_error=e) from e

    async def get_status(self) -> Dict[str, Any]:
        try:
            collections = self.client.get_collections().collections
            col = next((c for c in collections if c.name == self.collection_name), None)
            return {
                "status": "healthy" if col else "uninitialized",
                "collection": self.collection_name,
                "vector_count": col.points_count if col else 0
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
