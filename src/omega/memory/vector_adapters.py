# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Sovereign Vector Store Adapters for Omega Memory.
AP: AP-VECTOR-ADAPTERS-v1.0.0
"""
# DocRef: docs/architecture/MEMORY_STORE_DEEP_DIVE.md

import logging
import uuid
import math
import anyio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from omega.errors import ProviderError, ProviderUnavailableError


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
        id: Optional[str] = None,
        collection: str = "default",
    ) -> str:
        """Insert or update a vector and its metadata."""
        pass

    @abstractmethod
    async def query(
        self,
        entity_name: str,
        vector: List[float],
        limit: int = 10,
        filter: Optional[Dict[str, Any]] = None,
        collection: str = "default",
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
        id: Optional[str] = None,
        collection: str = "default",
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
        filter: Optional[Dict[str, Any]] = None,
        collection: str = "default",
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
        self._store[entity_name] = [item for item in self._store[entity_name] if item[0] not in ids]
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
            "entities_tracked": len(self._store),
        }

