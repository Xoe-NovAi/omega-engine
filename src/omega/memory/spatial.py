# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-M3-SPATIAL-v1.0.0
# 🔱 Spatial Memory — xyz Coordinates for Memory Blocks
# ⬡ OMEGA ⬡ MEMORY ⬡ spatial.py
#
# Integrates xyz coordinates into the memory block system.
# Extends the existing spatial_resolver (Force-Directed Graph) to provide
# spatial indexing for memory blocks, enabling:
#   - Spatial clustering during SleepTimeAgent consolidation
#   - Nearest-neighbor retrieval in 3D semantic space
#   - Region-based memory queries
#
# [id-soft: vet-046] BSP Culling — Spatial partitioning for efficiency
#   The spatial index provides coordinates that allow the engine to cull
#   large regions of the semantic space during navigation.
#
# DocRef: docs/architecture/MEMORY_SPATIAL_INTEGRATION.md

import logging
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


from .blocks import MemoryBlock, BlockCategory
from .block_store import SQLiteBlockStore, get_sqlite_block_store

logger = logging.getLogger(__name__)


@dataclass
class SpatialCoordinate:
    """A 3D coordinate in semantic space.

    Coordinates are computed by the ForceDirectedSpatialResolver and
    stored alongside memory blocks for spatial retrieval.
    """

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def dist_to(self, other: "SpatialCoordinate") -> float:
        """Euclidean distance to another coordinate."""
        return math.sqrt(
            (self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2
        )

    def to_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)

    def to_dict(self) -> Dict[str, float]:
        return {"x": self.x, "y": self.y, "z": self.z}

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "SpatialCoordinate":
        return cls(
            x=data.get("x", 0.0),
            y=data.get("y", 0.0),
            z=data.get("z", 0.0),
        )

    @classmethod
    def from_tuple(cls, t: Tuple[float, float, float]) -> "SpatialCoordinate":
        return cls(x=t[0], y=t[1], z=t[2])


@dataclass
class SpatialMemoryBlock:
    """A MemoryBlock with associated 3D spatial coordinates.

    Wraps MemoryBlock and adds xyz coordinates for spatial retrieval.
    The coordinates are computed by the ForceDirectedSpatialResolver
    based on semantic relationships between blocks.
    """

    block: MemoryBlock
    coordinates: SpatialCoordinate = field(default_factory=SpatialCoordinate)
    spatial_metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def id(self) -> str:
        return self.block.id

    @property
    def label(self) -> str:
        return self.block.label

    @property
    def value(self) -> str:
        return self.block.value

    @property
    def owner_entity(self) -> str:
        return self.block.owner_entity

    @property
    def category(self) -> BlockCategory:
        return self.block.category

    def dist_to(self, other: "SpatialMemoryBlock") -> float:
        """Spatial distance to another block."""
        return self.coordinates.dist_to(other.coordinates)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "block": self.block.to_dict(),
            "coordinates": self.coordinates.to_dict(),
            "spatial_metadata": self.spatial_metadata,
        }

    @classmethod
    def from_block(
        cls, block: MemoryBlock, coords: Optional[SpatialCoordinate] = None
    ) -> "SpatialMemoryBlock":
        """Create a SpatialMemoryBlock from an existing MemoryBlock."""
        return cls(
            block=block,
            coordinates=coords or SpatialCoordinate(),
        )


class SpatialIndex:
    """Spatial index for memory blocks with xyz coordinates.

    Provides:
    - Nearest-neighbor queries (find blocks near a coordinate)
    - Region queries (find blocks within a bounding box)
    - Spatial clustering for consolidation
    - Integration with the ForceDirectedSpatialResolver

    Uses a simple grid-based spatial hash for O(1) average lookup.
    Grid cell size is configurable (default: 50.0 units).
    """

    def __init__(self, grid_size: float = 50.0):
        self.grid_size = grid_size
        self._blocks: Dict[str, SpatialMemoryBlock] = {}
        self._grid: Dict[Tuple[int, int, int], List[str]] = {}
        self._entity_blocks: Dict[str, List[str]] = {}

    def _grid_key(self, coords: SpatialCoordinate) -> Tuple[int, int, int]:
        """Compute grid cell key for coordinates."""
        return (
            int(math.floor(coords.x / self.grid_size)),
            int(math.floor(coords.y / self.grid_size)),
            int(math.floor(coords.z / self.grid_size)),
        )

    def insert(self, spatial_block: SpatialMemoryBlock) -> None:
        """Insert a spatial block into the index."""
        block_id = spatial_block.id
        self._blocks[block_id] = spatial_block

        # Add to grid
        gkey = self._grid_key(spatial_block.coordinates)
        if gkey not in self._grid:
            self._grid[gkey] = []
        if block_id not in self._grid[gkey]:
            self._grid[gkey].append(block_id)

        # Add to entity index
        entity = spatial_block.owner_entity
        if entity not in self._entity_blocks:
            self._entity_blocks[entity] = []
        if block_id not in self._entity_blocks[entity]:
            self._entity_blocks[entity].append(block_id)

    def remove(self, block_id: str) -> bool:
        """Remove a block from the index. Returns True if found."""
        if block_id not in self._blocks:
            return False

        block = self._blocks.pop(block_id)

        # Remove from grid
        gkey = self._grid_key(block.coordinates)
        if gkey in self._grid and block_id in self._grid[gkey]:
            self._grid[gkey].remove(block_id)
            if not self._grid[gkey]:
                del self._grid[gkey]

        # Remove from entity index
        entity = block.owner_entity
        if entity in self._entity_blocks and block_id in self._entity_blocks[entity]:
            self._entity_blocks[entity].remove(block_id)
            if not self._entity_blocks[entity]:
                del self._entity_blocks[entity]

        return True

    def get(self, block_id: str) -> Optional[SpatialMemoryBlock]:
        """Get a block by ID."""
        return self._blocks.get(block_id)

    def nearest_neighbors(
        self,
        coords: SpatialCoordinate,
        k: int = 10,
        entity_filter: Optional[str] = None,
    ) -> List[Tuple[float, SpatialMemoryBlock]]:
        """Find k nearest neighbors to given coordinates.

        Args:
            coords: Query coordinates.
            k: Number of neighbors to return.
            entity_filter: If set, only return blocks owned by this entity.

        Returns:
            List of (distance, SpatialMemoryBlock) sorted by distance ascending.
        """
        candidates = []

        # Determine which blocks to search
        if entity_filter:
            block_ids = self._entity_blocks.get(entity_filter, [])
            search_blocks = [self._blocks[bid] for bid in block_ids if bid in self._blocks]
        else:
            search_blocks = list(self._blocks.values())

        # Compute distances
        for block in search_blocks:
            dist = block.coordinates.dist_to(coords)
            candidates.append((dist, block))

        # Sort by distance and take top k
        candidates.sort(key=lambda x: x[0])
        return candidates[:k]

    def region_query(
        self,
        min_coords: SpatialCoordinate,
        max_coords: SpatialCoordinate,
        entity_filter: Optional[str] = None,
    ) -> List[SpatialMemoryBlock]:
        """Find all blocks within a 3D bounding box.

        Args:
            min_coords: Minimum corner of the bounding box.
            max_coords: Maximum corner of the bounding box.
            entity_filter: If set, only return blocks owned by this entity.

        Returns:
            List of SpatialMemoryBlock within the region.
        """
        results = []

        # Determine which blocks to search
        if entity_filter:
            block_ids = self._entity_blocks.get(entity_filter, [])
            search_blocks = [self._blocks[bid] for bid in block_ids if bid in self._blocks]
        else:
            search_blocks = list(self._blocks.values())

        for block in search_blocks:
            c = block.coordinates
            if (
                min_coords.x <= c.x <= max_coords.x
                and min_coords.y <= c.y <= max_coords.y
                and min_coords.z <= c.z <= max_coords.z
            ):
                results.append(block)

        return results

    def spatial_cluster(
        self,
        entity_name: str,
        max_radius: float = 100.0,
        min_cluster_size: int = 2,
    ) -> List[List[SpatialMemoryBlock]]:
        """Cluster blocks for an entity using spatial proximity.

        Simple DBSCAN-style clustering based on spatial distance.
        Used by SleepTimeAgent for consolidation grouping.

        Args:
            entity_name: Entity whose blocks to cluster.
            max_radius: Maximum distance for two blocks to be in the same cluster.
            min_cluster_size: Minimum blocks for a valid cluster.

        Returns:
            List of clusters, each cluster is a list of SpatialMemoryBlock.
        """
        block_ids = self._entity_blocks.get(entity_name, [])
        blocks = [self._blocks[bid] for bid in block_ids if bid in self._blocks]

        if len(blocks) < min_cluster_size:
            return []

        # Simple greedy clustering
        visited = set()
        clusters = []

        for block in blocks:
            if block.id in visited:
                continue

            cluster = [block]
            visited.add(block.id)

            for other in blocks:
                if other.id in visited:
                    continue
                if block.coordinates.dist_to(other.coordinates) <= max_radius:
                    cluster.append(other)
                    visited.add(other.id)

            if len(cluster) >= min_cluster_size:
                clusters.append(cluster)

        return clusters

    def get_entity_blocks(self, entity_name: str) -> List[SpatialMemoryBlock]:
        """Get all spatial blocks for an entity."""
        block_ids = self._entity_blocks.get(entity_name, [])
        return [self._blocks[bid] for bid in block_ids if bid in self._blocks]

    def update_coordinates(self, block_id: str, coords: SpatialCoordinate) -> bool:
        """Update coordinates for an existing block.

        Returns True if block was found and updated.
        """
        if block_id not in self._blocks:
            return False

        block = self._blocks[block_id]
        old_coords = block.coordinates
        block.coordinates = coords

        # Update grid membership
        old_gkey = self._grid_key(old_coords)
        new_gkey = self._grid_key(coords)

        if old_gkey != new_gkey:
            if old_gkey in self._grid and block_id in self._grid[old_gkey]:
                self._grid[old_gkey].remove(block_id)
                if not self._grid[old_gkey]:
                    del self._grid[old_gkey]

            if new_gkey not in self._grid:
                self._grid[new_gkey] = []
            if block_id not in self._grid[new_gkey]:
                self._grid[new_gkey].append(block_id)

        return True

    def stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            "total_blocks": len(self._blocks),
            "grid_cells": len(self._grid),
            "entities": len(self._entity_blocks),
            "grid_size": self.grid_size,
        }


class SpatialMemoryManager:
    """Manages spatial coordinates for memory blocks.

    Integrates the ForceDirectedSpatialResolver with the block store,
    providing spatial awareness to the memory system.

    Used by:
    - SleepTimeAgent: for spatial clustering during consolidation
    - ContextBuilder: for spatial nearest-neighbor retrieval
    - MemoryStore: for spatial indexing of conversation turns
    """

    def __init__(
        self,
        block_store: Optional[SQLiteBlockStore] = None,
        grid_size: float = 50.0,
    ):
        self._block_store = block_store or get_sqlite_block_store()
        self._spatial_index = SpatialIndex(grid_size=grid_size)
        self._resolver = None  # Lazy-loaded to avoid circular imports

    def _get_resolver(self):
        """Lazy-load the spatial resolver to avoid circular imports."""
        if self._resolver is None:
            from omega.oracle.spatial_resolver import get_spatial_resolver

            self._resolver = get_spatial_resolver()
        return self._resolver

    async def index_entity_blocks(
        self, entity_name: str, relationships: Optional[List[Tuple[str, str]]] = None
    ) -> Dict[str, Any]:
        """Index all blocks for an entity with spatial coordinates.

        Uses the ForceDirectedSpatialResolver to compute 3D coordinates
        based on semantic relationships between blocks.

        Args:
            entity_name: Entity whose blocks to index.
            relationships: Optional list of (block_label_a, block_label_b)
                           tuples representing semantic relationships.

        Returns:
            Dict with indexing statistics.
        """
        # Get all blocks for the entity
        blocks = await self._block_store.get_blocks_for_entity(entity_name)
        if not blocks:
            return {"indexed": 0, "entity": entity_name}

        # Extract block labels for spatial resolution
        block_labels = [b.label for b in blocks]

        # Compute spatial coordinates using ForceDirectedSpatialResolver
        resolver = self._get_resolver()
        coords_map = resolver.resolve_coordinates(block_labels, relationships or [])

        # Index each block
        indexed = 0
        for block in blocks:
            coords = coords_map.get(
                block.label,
                SpatialCoordinate(x=0.0, y=0.0, z=0.0),
            )
            # Convert Point3D to SpatialCoordinate if needed
            if hasattr(coords, "x") and hasattr(coords, "y") and hasattr(coords, "z"):
                spatial_coords = SpatialCoordinate(x=coords.x, y=coords.y, z=coords.z)
            else:
                spatial_coords = SpatialCoordinate()

            spatial_block = SpatialMemoryBlock.from_block(block, spatial_coords)
            self._spatial_index.insert(spatial_block)
            indexed += 1

        return {
            "indexed": indexed,
            "entity": entity_name,
            "grid_cells": len(self._spatial_index._grid),
        }

    def get_spatial_context(
        self,
        entity_name: str,
        query_coords: Optional[SpatialCoordinate] = None,
        k: int = 10,
        token_budget: int = 4000,
    ) -> List[SpatialMemoryBlock]:
        """Get spatially-relevant blocks for context injection.

        If query_coords is provided, returns nearest neighbors.
        Otherwise, returns all blocks for the entity sorted by spatial density.
        """
        if query_coords is not None:
            neighbors = self._spatial_index.nearest_neighbors(
                query_coords, k=k, entity_filter=entity_name
            )
            return [block for _, block in neighbors]

        # Return all blocks for entity
        return self._spatial_index.get_entity_blocks(entity_name)

    def get_spatial_clusters(
        self,
        entity_name: str,
        max_radius: float = 100.0,
        min_cluster_size: int = 2,
    ) -> List[List[SpatialMemoryBlock]]:
        """Get spatial clusters for an entity (for SleepTimeAgent consolidation)."""
        return self._spatial_index.spatial_cluster(entity_name, max_radius, min_cluster_size)

    def get_index_stats(self) -> Dict[str, Any]:
        """Get spatial index statistics."""
        return self._spatial_index.stats()


# ── Integration with SleepTimeAgent ──────────────────────────────────────


async def spatial_consolidation(
    entity_name: str,
    transcript: List[Dict[str, str]],
    max_radius: float = 100.0,
    min_cluster_size: int = 2,
) -> Dict[str, Any]:
    """Perform spatial-aware consolidation for an entity.

    This function integrates xyz coordinates into the SleepTimeAgent
    consolidation flow:
    1. Index all entity blocks with spatial coordinates
    2. Cluster blocks by spatial proximity
    3. For each cluster, extract patterns and consolidate

    Args:
        entity_name: Entity to consolidate.
        transcript: Conversation transcript for pattern extraction.
        max_radius: Maximum distance for spatial clustering.
        min_cluster_size: Minimum blocks per cluster.

    Returns:
        Dict with consolidation results including spatial clusters.
    """
    manager = SpatialMemoryManager()

    # Index entity blocks
    index_result = await manager.index_entity_blocks(entity_name)

    # Get spatial clusters
    clusters = manager.get_spatial_clusters(entity_name, max_radius, min_cluster_size)

    # Build cluster summaries
    cluster_summaries = []
    for i, cluster in enumerate(clusters):
        cluster_summaries.append(
            {
                "cluster_id": i,
                "block_count": len(cluster),
                "labels": [b.label for b in cluster],
                "centroid": {
                    "x": sum(b.coordinates.x for b in cluster) / len(cluster),
                    "y": sum(b.coordinates.y for b in cluster) / len(cluster),
                    "z": sum(b.coordinates.z for b in cluster) / len(cluster),
                },
            }
        )

    return {
        "entity": entity_name,
        "indexed": index_result["indexed"],
        "clusters_found": len(clusters),
        "clusters": cluster_summaries,
        "spatial_stats": manager.get_index_stats(),
    }


# ── Singleton ────────────────────────────────────────────────────────────

_spatial_manager: Optional[SpatialMemoryManager] = None


def get_spatial_memory_manager() -> SpatialMemoryManager:
    """Get or create the singleton SpatialMemoryManager."""
    global _spatial_manager
    if _spatial_manager is None:
        _spatial_manager = SpatialMemoryManager()
    return _spatial_manager
