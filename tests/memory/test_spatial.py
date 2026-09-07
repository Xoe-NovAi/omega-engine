# AP: AP-M3-SPATIAL-TEST-v1.0.0
# 🔱 Tests for Spatial Memory (xyz Coordinates)
# ⬡ OMEGA ⬡ MEMORY ⬡ tests/memory/test_spatial.py
"""Tests for spatial memory integration with xyz coordinates.

Tests:
- SpatialCoordinate operations (distance, conversion)
- SpatialMemoryBlock wrapping
- SpatialIndex CRUD and queries
- Spatial clustering
- SpatialMemoryManager integration
"""
import pytest
import math

from omega.memory.spatial import (
    SpatialCoordinate,
    SpatialMemoryBlock,
    SpatialIndex,
    SpatialMemoryManager,
    spatial_consolidation,
    get_spatial_memory_manager,
)
from omega.memory.blocks import (
    MemoryBlock,
    BlockCategory,
    GovernanceLevel,
)


class TestSpatialCoordinate:
    def test_default_coordinates(self):
        coord = SpatialCoordinate()
        assert coord.x == 0.0
        assert coord.y == 0.0
        assert coord.z == 0.0

    def test_custom_coordinates(self):
        coord = SpatialCoordinate(x=1.0, y=2.0, z=3.0)
        assert coord.x == 1.0
        assert coord.y == 2.0
        assert coord.z == 3.0

    def test_dist_to_origin(self):
        coord = SpatialCoordinate(x=3.0, y=4.0, z=0.0)
        assert coord.dist_to(SpatialCoordinate(0, 0, 0)) == 5.0

    def test_dist_to_3d(self):
        coord = SpatialCoordinate(x=1.0, y=1.0, z=1.0)
        assert abs(coord.dist_to(SpatialCoordinate(0, 0, 0)) - math.sqrt(3)) < 1e-10

    def test_dist_to_same_point(self):
        coord = SpatialCoordinate(x=5.0, y=5.0, z=5.0)
        assert coord.dist_to(SpatialCoordinate(5.0, 5.0, 5.0)) == 0.0

    def test_to_tuple(self):
        coord = SpatialCoordinate(x=1.5, y=2.5, z=3.5)
        assert coord.to_tuple() == (1.5, 2.5, 3.5)

    def test_to_dict(self):
        coord = SpatialCoordinate(x=1.0, y=2.0, z=3.0)
        d = coord.to_dict()
        assert d == {"x": 1.0, "y": 2.0, "z": 3.0}

    def test_from_dict(self):
        coord = SpatialCoordinate.from_dict({"x": 1.0, "y": 2.0, "z": 3.0})
        assert coord.x == 1.0
        assert coord.y == 2.0
        assert coord.z == 3.0

    def test_from_dict_missing_keys(self):
        coord = SpatialCoordinate.from_dict({})
        assert coord.x == 0.0
        assert coord.y == 0.0
        assert coord.z == 0.0

    def test_from_tuple(self):
        coord = SpatialCoordinate.from_tuple((1.0, 2.0, 3.0))
        assert coord.x == 1.0
        assert coord.y == 2.0
        assert coord.z == 3.0


class TestSpatialMemoryBlock:
    def test_from_block_no_coords(self):
        block = MemoryBlock(label="test", value="content", owner_entity="test_entity")
        sblock = SpatialMemoryBlock.from_block(block)
        assert sblock.block == block
        assert sblock.coordinates.x == 0.0
        assert sblock.label == "test"
        assert sblock.value == "content"
        assert sblock.owner_entity == "test_entity"

    def test_from_block_with_coords(self):
        block = MemoryBlock(label="test", value="content", owner_entity="test_entity")
        coords = SpatialCoordinate(x=1.0, y=2.0, z=3.0)
        sblock = SpatialMemoryBlock.from_block(block, coords)
        assert sblock.coordinates.x == 1.0
        assert sblock.coordinates.y == 2.0
        assert sblock.coordinates.z == 3.0

    def test_dist_to(self):
        block1 = MemoryBlock(label="b1", value="v1", owner_entity="e")
        block2 = MemoryBlock(label="b2", value="v2", owner_entity="e")
        s1 = SpatialMemoryBlock.from_block(block1, SpatialCoordinate(0, 0, 0))
        s2 = SpatialMemoryBlock.from_block(block2, SpatialCoordinate(3, 4, 0))
        assert s1.dist_to(s2) == 5.0

    def test_to_dict(self):
        block = MemoryBlock(label="test", value="content", owner_entity="test_entity")
        coords = SpatialCoordinate(x=1.0, y=2.0, z=3.0)
        sblock = SpatialMemoryBlock.from_block(block, coords)
        d = sblock.to_dict()
        assert "block" in d
        assert "coordinates" in d
        assert d["coordinates"] == {"x": 1.0, "y": 2.0, "z": 3.0}


class TestSpatialIndex:
    def test_empty_index(self):
        idx = SpatialIndex()
        assert idx.stats()["total_blocks"] == 0

    def test_insert_and_get(self):
        idx = SpatialIndex()
        block = MemoryBlock(label="test", value="content", owner_entity="entity1")
        sblock = SpatialMemoryBlock.from_block(
            block, SpatialCoordinate(1.0, 2.0, 3.0)
        )
        idx.insert(sblock)
        assert idx.stats()["total_blocks"] == 1
        result = idx.get(sblock.id)
        assert result is not None
        assert result.label == "test"

    def test_remove(self):
        idx = SpatialIndex()
        block = MemoryBlock(label="test", value="content", owner_entity="entity1")
        sblock = SpatialMemoryBlock.from_block(
            block, SpatialCoordinate(1.0, 2.0, 3.0)
        )
        idx.insert(sblock)
        assert idx.remove(sblock.id) is True
        assert idx.get(sblock.id) is None
        assert idx.remove(sblock.id) is False  # Already removed

    def test_nearest_neighbors(self):
        idx = SpatialIndex()
        # Insert 5 blocks at different coordinates
        for i in range(5):
            block = MemoryBlock(label=f"block_{i}", value=f"v{i}", owner_entity="e")
            coords = SpatialCoordinate(x=float(i * 10), y=0, z=0)
            idx.insert(SpatialMemoryBlock.from_block(block, coords))

        # Query nearest to (5, 0, 0)
        neighbors = idx.nearest_neighbors(SpatialCoordinate(5, 0, 0), k=2)
        assert len(neighbors) == 2
        # Closest should be block at x=0 or x=10 (both distance 5)
        assert neighbors[0][0] <= 5.0

    def test_nearest_neighbors_with_entity_filter(self):
        idx = SpatialIndex()
        block1 = MemoryBlock(label="b1", value="v1", owner_entity="entity1")
        block2 = MemoryBlock(label="b2", value="v2", owner_entity="entity2")
        idx.insert(SpatialMemoryBlock.from_block(block1, SpatialCoordinate(0, 0, 0)))
        idx.insert(SpatialMemoryBlock.from_block(block2, SpatialCoordinate(10, 0, 0)))

        neighbors = idx.nearest_neighbors(SpatialCoordinate(0, 0, 0), k=5, entity_filter="entity1")
        assert len(neighbors) == 1
        assert neighbors[0][1].label == "b1"

    def test_region_query(self):
        idx = SpatialIndex()
        for i in range(5):
            block = MemoryBlock(label=f"b{i}", value=f"v{i}", owner_entity="e")
            coords = SpatialCoordinate(x=float(i * 10), y=0, z=0)
            idx.insert(SpatialMemoryBlock.from_block(block, coords))

        # Query region [0, 25] x [0, 0] x [0, 0]
        results = idx.region_query(
            SpatialCoordinate(0, 0, 0),
            SpatialCoordinate(25, 0, 0),
        )
        assert len(results) == 3  # blocks at x=0, 10, 20

    def test_spatial_cluster(self):
        idx = SpatialIndex()
        # Create two clusters: 0-10 and 100-110
        for i in range(3):
            block = MemoryBlock(label=f"cluster1_{i}", value=f"v{i}", owner_entity="e")
            idx.insert(SpatialMemoryBlock.from_block(block, SpatialCoordinate(float(i * 5), 0, 0)))

        for i in range(3):
            block = MemoryBlock(label=f"cluster2_{i}", value=f"v{i}", owner_entity="e")
            idx.insert(SpatialMemoryBlock.from_block(block, SpatialCoordinate(100 + i * 5, 0, 0)))

        clusters = idx.spatial_cluster("e", max_radius=20.0, min_cluster_size=2)
        assert len(clusters) == 2
        assert all(len(c) >= 2 for c in clusters)

    def test_update_coordinates(self):
        idx = SpatialIndex()
        block = MemoryBlock(label="test", value="content", owner_entity="e")
        sblock = SpatialMemoryBlock.from_block(block, SpatialCoordinate(0, 0, 0))
        idx.insert(sblock)

        # Move to new coordinates
        new_coords = SpatialCoordinate(100, 100, 100)
        assert idx.update_coordinates(sblock.id, new_coords) is True
        assert idx.get(sblock.id).coordinates.x == 100.0

        # Update non-existent block
        assert idx.update_coordinates("nonexistent", new_coords) is False

    def test_get_entity_blocks(self):
        idx = SpatialIndex()
        block1 = MemoryBlock(label="b1", value="v1", owner_entity="entity1")
        block2 = MemoryBlock(label="b2", value="v2", owner_entity="entity2")
        idx.insert(SpatialMemoryBlock.from_block(block1, SpatialCoordinate(0, 0, 0)))
        idx.insert(SpatialMemoryBlock.from_block(block2, SpatialCoordinate(10, 0, 0)))

        entity1_blocks = idx.get_entity_blocks("entity1")
        assert len(entity1_blocks) == 1
        assert entity1_blocks[0].label == "b1"

    def test_stats(self):
        idx = SpatialIndex(grid_size=25.0)
        for i in range(5):
            block = MemoryBlock(label=f"b{i}", value=f"v{i}", owner_entity="e")
            idx.insert(SpatialMemoryBlock.from_block(block, SpatialCoordinate(float(i * 10), 0, 0)))

        stats = idx.stats()
        assert stats["total_blocks"] == 5
        assert stats["entities"] == 1
        assert stats["grid_size"] == 25.0


class TestSpatialMemoryManager:
    @pytest.mark.anyio
    async def test_index_entity_blocks_empty(self):
        manager = SpatialMemoryManager()
        result = await manager.index_entity_blocks("nonexistent_entity")
        assert result["indexed"] == 0

    @pytest.mark.anyio
    async def test_get_spatial_context_empty(self):
        manager = SpatialMemoryManager()
        context = manager.get_spatial_context("nonexistent_entity")
        assert context == []

    def test_get_index_stats_empty(self):
        manager = SpatialMemoryManager()
        stats = manager.get_index_stats()
        assert stats["total_blocks"] == 0

    def test_get_spatial_clusters_empty(self):
        manager = SpatialMemoryManager()
        clusters = manager.get_spatial_clusters("nonexistent_entity")
        assert clusters == []


class TestSpatialConsolidation:
    @pytest.mark.anyio
    async def test_spatial_consolidation_no_blocks(self):
        result = await spatial_consolidation(
            entity_name="nonexistent_entity",
            transcript=[],
        )
        assert result["indexed"] == 0
        assert result["clusters_found"] == 0

    @pytest.mark.anyio
    async def test_spatial_consolidation_with_mock_blocks(self):
        """Test spatial consolidation with mocked block store."""
        from unittest.mock import AsyncMock, MagicMock, patch

        # Create a mock block store
        mock_store = MagicMock()
        mock_store.get_blocks_for_entity = AsyncMock(return_value=[])

        with patch(
            "omega.memory.spatial.get_sqlite_block_store",
            return_value=mock_store,
        ):
            from omega.memory.spatial import SpatialMemoryManager
            manager = SpatialMemoryManager(block_store=mock_store)
            result = await manager.index_entity_blocks("test_entity")
            assert result["indexed"] == 0


class TestSingleton:
    def test_get_spatial_memory_manager_returns_instance(self):
        manager = get_spatial_memory_manager()
        assert isinstance(manager, SpatialMemoryManager)

    def test_singleton_returns_same_instance(self):
        m1 = get_spatial_memory_manager()
        m2 = get_spatial_memory_manager()
        assert m1 is m2
