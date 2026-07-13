# AP: AP-PR-READINESS-v1.0.0
# 🔱 Omega Engine — Memory Package
# ⬡ OMEGA ⬡ MEMORY ⬡ v1.0.0 ⬡ 2026-06-15
"""Memory subsystem — providers, vector adapters, embeddings, adapters."""

from .providers import (
    StorageProvider,
    RedisStorageProvider,
    FileStorageProvider,
    InMemoryStorageProvider,
    DiskSpaceError,
)
from .vector_adapters import IVectorStoreAdapter, QdrantAdapter, MemoryVectorAdapter
from .sqlite_vec_adapter import SQLiteVecAdapter
from .embeddings import IEmbeddingProvider, OllamaEmbeddingProvider, SovereignFallbackEmbeddingProvider
from .fts_index import ConversationFTSIndex
from .adapters import IMemoryAdapter, MemoryAdapterRegistry, MemoryRecord, MemoryType, MemoryPriority

__all__ = [
    # Providers
    "StorageProvider",
    "RedisStorageProvider",
    "FileStorageProvider",
    "InMemoryStorageProvider",
    "DiskSpaceError",
    # Vector adapters
    "IVectorStoreAdapter",
    "QdrantAdapter",
    "MemoryVectorAdapter",
    "SQLiteVecAdapter",
    # Embeddings
    "IEmbeddingProvider",
    "OllamaEmbeddingProvider",
    "SovereignFallbackEmbeddingProvider",
    # FTS
    "ConversationFTSIndex",
    # Adapters (NEW)
    "IMemoryAdapter",
    "MemoryAdapterRegistry",
    "MemoryRecord",
    "MemoryType",
    "MemoryPriority",
]
