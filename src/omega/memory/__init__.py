# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-PR-READINESS-v1.0.0
# 🔱 Omega Engine — Memory Package
# ⬡ OMEGA ⬡ MEMORY ⬡ v1.0.0 ⬡ 2026-06-15
"""Memory subsystem — providers, vector adapters, embeddings, adapters, blocks."""

from .providers import (
    StorageProvider,
    RedisStorageProvider,
    FileStorageProvider,
    InMemoryStorageProvider,
    USMStorageProvider,
    DiskSpaceError,
)
from .vector_adapters import IVectorStoreAdapter, MemoryVectorAdapter
from .sqlite_vec_adapter import SQLiteVecAdapter
from .embeddings import (
    IEmbeddingProvider,
    OllamaEmbeddingProvider,
    SovereignFallbackEmbeddingProvider,
)
from .fts_index import ConversationFTSIndex
from .adapters import (
    IMemoryAdapter,
    MemoryAdapterRegistry,
    MemoryRecord,
    MemoryType,
    MemoryPriority,
)
from .blocks import (
    MemoryBlock,
    BlockCategory,
    GovernanceLevel,
    CATEGORY_DECAY_RATES,
    ESSENTIAL_BLOCKS,
    DOMAIN_BLOCKS,
    create_essential_block,
    create_essential_blocks,
    create_domain_blocks,
)
from .block_store import SQLiteBlockStore, get_sqlite_block_store
from .block_tools import (
    BlockTools,
    BlockStore,
    BlockOperationResult,
    block_read,
    block_append,
    block_replace,
    block_rethink,
    initialize_entity_blocks,
    SleepTimeAgent,
)
from .archival import ArchivalMemory, ArchivalTools, get_archival_memory
from .sleep_time import SleepTimeAgent as SleepTimeAgentV2, DaatDaemon, create_sleep_time_system

__all__ = [
    # Providers
    "StorageProvider",
    "RedisStorageProvider",
    "FileStorageProvider",
    "InMemoryStorageProvider",
    "USMStorageProvider",
    "DiskSpaceError",
    # Vector adapters
    "IVectorStoreAdapter",
    "MemoryVectorAdapter",
    "SQLiteVecAdapter",
    # Embeddings
    "IEmbeddingProvider",
    "OllamaEmbeddingProvider",
    "SovereignFallbackEmbeddingProvider",
    # FTS
    "ConversationFTSIndex",
    # Adapters
    "IMemoryAdapter",
    "MemoryAdapterRegistry",
    "MemoryRecord",
    "MemoryType",
    "MemoryPriority",
    # Blocks (D-283)
    "MemoryBlock",
    "BlockCategory",
    "GovernanceLevel",
    "CATEGORY_DECAY_RATES",
    "ESSENTIAL_BLOCKS",
    "DOMAIN_BLOCKS",
    "create_essential_blocks",
    "create_domain_blocks",
    # Block Store (D-283)
    "SQLiteBlockStore",
    "get_sqlite_block_store",
    # Block Tools
    "BlockTools",
    "BlockStore",
    "BlockOperationResult",
    "block_read",
    "block_append",
    "block_replace",
    "block_rethink",
    "initialize_entity_blocks",
    "SleepTimeAgent",
    # Archival (D-283 Phase 2)
    "ArchivalMemory",
    "ArchivalTools",
    "get_archival_memory",
]
