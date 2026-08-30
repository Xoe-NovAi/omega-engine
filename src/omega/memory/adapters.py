# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-PR-READINESS-v1.0.0
# 🔱 Omega Engine — Memory Adapters
# ⬡ OMEGA ⬡ MEMORY ⬡ ADAPTERS ⬡ v1.0.0 ⬡ 2026-06-15
"""WAD-pluggable memory adapter — dual-interface bridge for memory subsystems.

Provides `IMemoryAdapter`, a generic ABC that the core engine uses to delegate
entity-specific memory operations (vaults, cross-pollination, lifecycle hooks)
to WAD-layer implementations. The Engine-Stack Firewall (M2) is enforced by
keeping all esoteric/Kabbalistic terminology in the Arcana-NovAi WAD.

Architecture:
    MemoryStore (core)
        └── adapter_registry: MemoryAdapterRegistry
            ├── get_for_entity("entity_name")
            │   └── returns WAD-specific IMemoryAdapter
            └── wrapped providers
                └── StorageProvider chain still handles exchange persistence
"""
# DocRef: docs/architecture/MEMORY_STORE_DEEP_DIVE.md

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """Classification of a memory record by cognitive function."""

    EPISODIC = "episodic"  # What happened — raw events, exchanges
    SEMANTIC = "semantic"  # What is known — extracted facts, abstractions
    PROCEDURAL = "procedural"  # How to do things — workflows, patterns


class MemoryPriority(Enum):
    """Retention priority for a memory record."""

    CRITICAL = 10  # Must never be pruned (decisions, principles)
    HIGH = 8  # Long-term retention (key insights)
    NORMAL = 5  # Standard retention
    LOW = 2  # May be pruned under pressure
    TRANSIENT = 1  # Ephemeral — safe to discard any time


class MemoryRecord:
    """A single memory observation with metadata.

    Used by IMemoryAdapter to exchange structured memory data
    between the core engine and WAD-layer implementations.
    """

    def __init__(
        self,
        memory_id: str,
        entity_name: str,
        memory_type: MemoryType,
        priority: MemoryPriority,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[float] = None,
        source_trace_id: Optional[str] = None,
    ):
        self.memory_id = memory_id
        self.entity_name = entity_name
        self.memory_type = memory_type
        self.priority = priority
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = timestamp
        self.source_trace_id = source_trace_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "entity_name": self.entity_name,
            "memory_type": self.memory_type.value,
            "priority": self.priority.value,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "source_trace_id": self.source_trace_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryRecord":
        return cls(
            memory_id=data["memory_id"],
            entity_name=data["entity_name"],
            memory_type=MemoryType(data.get("memory_type", "episodic")),
            priority=MemoryPriority(data.get("priority", 5)),
            content=data["content"],
            metadata=data.get("metadata"),
            timestamp=data.get("timestamp"),
            source_trace_id=data.get("source_trace_id"),
        )


class IMemoryAdapter(ABC):
    """WAD-pluggable memory adapter interface.

    The core engine uses this interface to delegate entity-specific memory
    operations (vault reads/writes, lifecycle hooks, cross-pollination) to
    WAD-layer implementations. Each WAD that needs custom memory behavior
    implements this class.

    Core contract:
      - get_history / save_history / archive / close
        These mirror StorageProvider for backward compatibility.

    WAD-layer extensions:
      - get_vault / put_vault / get_sphere / get_qliphoth
        Entity-specific operations that live outside the exchange path.

    Lifecycle hooks:
      - on_session_end / on_pre_compact
        Called by the engine at key lifecycle events.
    """

    @abstractmethod
    async def get_history(
        self, entity_name: str, session_id: str, limit: int
    ) -> List[Dict[str, Any]]:
        """Retrieve exchange history for an entity session."""
        ...

    @abstractmethod
    async def save_history(
        self, entity_name: str, session_id: str, exchanges: List[Dict[str, Any]]
    ) -> None:
        """Persist exchange history for an entity session."""
        ...

    @abstractmethod
    async def archive(self, entity_name: str, session_id: str) -> bool:
        """Archive a session — promote from hot/warm to cold storage."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Release all resources held by this adapter."""
        ...

    # ── Vault Operations (Entity-Specific Shadow State) ──

    @abstractmethod
    async def get_vault(self, entity_name: str, vault_key: str) -> Optional[Dict[str, Any]]:
        """Read a value from the entity's vault (shadow state)."""
        ...

    @abstractmethod
    async def put_vault(self, entity_name: str, vault_key: str, data: Dict[str, Any]) -> None:
        """Write a value to the entity's vault (shadow state)."""
        ...

    # ── Lifecycle Hooks ──

    async def on_session_end(
        self, entity_name: str, session_transcript: str, trace_id: Optional[str] = None
    ) -> List[MemoryRecord]:
        """Called when a session ends. May return distilled memories.

        Default implementation returns an empty list.
        Override in WAD adapters to distill session insights.

        Args:
            entity_name: Name of the entity
            session_transcript: Full session transcript for distillation
            trace_id: Optional trace ID for observability correlation
        """
        return []

    async def on_pre_compact(self, entity_name: str, session_id: str) -> Dict[str, Any]:
        """Called before context compaction. May return state to preserve.

        Default implementation returns an empty dict.
        Override in WAD adapters to preserve vault state across compaction.
        """
        return {}

    # ── Domain/Sphere Operations (WAD-layer extension) ──

    async def get_sphere(
        self, entity_name: str, sphere_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Retrieve sphere metadata for an entity.

        Default implementation returns empty dict.
        Override in WAD adapters implementing sphere-based memory.
        """
        return {}

    async def get_qliphoth(self, entity_name: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve Qliphothic failure taxonomy for an entity.

        Default implementation returns empty dict.
        Override in WAD adapters implementing failure taxonomy.
        """
        return {}


class MemoryAdapterRegistry:
    """Registry of WAD-layer IMemoryAdapter implementations.

    The WAD loader populates this registry at startup. The MemoryStore
    queries it to find the correct adapter for each entity.

    Thread-safe: all operations use module-level dict with atomic operations.
    """

    def __init__(self):
        self._adapters: Dict[str, IMemoryAdapter] = {}
        self._entity_to_adapter: Dict[str, str] = {}

    def register(self, wad_name: str, adapter: IMemoryAdapter) -> None:
        """Register an adapter for a WAD.

        Args:
            wad_name: Name of the WAD (e.g., '_omega_default', 'arcana_novai')
            adapter: Concrete IMemoryAdapter instance.
        """
        if not isinstance(adapter, IMemoryAdapter):
            raise TypeError(
                f"Adapter for WAD '{wad_name}' must implement IMemoryAdapter, "
                f"got {type(adapter).__name__}"
            )
        self._adapters[wad_name] = adapter
        logger.info(f"Registered memory adapter for WAD '{wad_name}' ({type(adapter).__name__})")

    def register_entity_to_wad(self, entity_name: str, wad_name: str) -> None:
        """Map an entity to its WAD's adapter.

        This is populated by the WAD loader when it loads entities.
        """
        if wad_name not in self._adapters:
            logger.warning(
                f"Cannot map entity '{entity_name}' to WAD '{wad_name}' — "
                f"no adapter registered for that WAD"
            )
            return
        self._entity_to_adapter[entity_name] = wad_name

    def get_for_entity(self, entity_name: str) -> Optional[IMemoryAdapter]:
        """Get the memory adapter for a specific entity.

        Returns None if no adapter is registered for the entity's WAD,
        making this safe for entities that don't have custom memory.
        """
        wad_name = self._entity_to_adapter.get(entity_name)
        if wad_name is None:
            return None
        return self._adapters.get(wad_name)

    def get_for_wad(self, wad_name: str) -> Optional[IMemoryAdapter]:
        """Get the memory adapter for a specific WAD name."""
        return self._adapters.get(wad_name)

    def list_adapters(self) -> Dict[str, str]:
        """List all registered adapters and their WAD names."""
        return {wad_name: type(adapter).__name__ for wad_name, adapter in self._adapters.items()}

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics for observability."""
        return {
            "adapters": len(self._adapters),
            "wads": list(self._adapters.keys()),
            "entity_mappings": len(self._entity_to_adapter),
        }
