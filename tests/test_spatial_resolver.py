# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Tests for spatial_resolver.py — Force-Directed Graph (Fruchterman-Reingold) layout."""
import pytest
from omega.oracle.spatial_resolver import (
    Point3D,
    ForceDirectedSpatialResolver,
    get_spatial_resolver,
    ISpatialResolver,
)


class TestPoint3D:
    def test_dist_to(self):
        p1 = Point3D(0, 0, 0)
        p2 = Point3D(3, 4, 0)
        assert p1.dist_to(p2) == 5.0

    def test_dist_to_3d(self):
        p1 = Point3D(0, 0, 0)
        p2 = Point3D(1, 1, 1)
        assert abs(p1.dist_to(p2) - 1.7320508075688772) < 1e-10


class TestForceDirectedSpatialResolver:
    def test_empty_entities(self):
        resolver = ForceDirectedSpatialResolver()
        result = resolver.resolve_coordinates([], [])
        assert result == {}

    def test_single_entity(self):
        resolver = ForceDirectedSpatialResolver(iterations=10)
        result = resolver.resolve_coordinates(["entity1"], [])
        assert "entity1" in result
        assert isinstance(result["entity1"], Point3D)

    def test_two_entities_no_relationship(self):
        resolver = ForceDirectedSpatialResolver(iterations=10)
        result = resolver.resolve_coordinates(["e1", "e2"], [])
        assert "e1" in result
        assert "e2" in result
        # They should repel each other
        d = result["e1"].dist_to(result["e2"])
        assert d > 0

    def test_two_entities_with_relationship(self):
        resolver = ForceDirectedSpatialResolver(iterations=50, initial_temp=50.0)
        result = resolver.resolve_coordinates(["e1", "e2"], [("e1", "e2")])
        assert "e1" in result
        assert "e2" in result
        # They should attract each other, distance should be smaller than no-relationship case
        d = result["e1"].dist_to(result["e2"])
        # With attraction, they should be closer than pure repulsion
        # (exact value depends on iterations, but should be reasonable)
        assert d < 100  # sanity check

    def test_three_entities_chain(self):
        resolver = ForceDirectedSpatialResolver(iterations=50)
        result = resolver.resolve_coordinates(["a", "b", "c"], [("a", "b"), ("b", "c")])
        assert len(result) == 3
        for e in ["a", "b", "c"]:
            assert e in result
            assert isinstance(result[e], Point3D)

    def test_custom_parameters(self):
        resolver = ForceDirectedSpatialResolver(
            iterations=20,
            initial_temp=200.0,
            decay_factor=0.9,
            volume=500.0
        )
        result = resolver.resolve_coordinates(["x", "y"], [("x", "y")])
        assert len(result) == 2

    def test_relationship_with_missing_entity(self):
        """Relationships referencing unknown entities should be ignored gracefully."""
        resolver = ForceDirectedSpatialResolver(iterations=10)
        result = resolver.resolve_coordinates(["a"], [("a", "nonexistent")])
        assert "a" in result
        assert "nonexistent" not in result


class TestSpatialResolverSingleton:
    def test_get_spatial_resolver_returns_instance(self):
        resolver = get_spatial_resolver()
        assert isinstance(resolver, ForceDirectedSpatialResolver)
        # Protocol compliance: has resolve_coordinates method
        assert hasattr(resolver, 'resolve_coordinates')
        assert callable(resolver.resolve_coordinates)

    def test_singleton_returns_same_instance(self):
        r1 = get_spatial_resolver()
        r2 = get_spatial_resolver()
        assert r1 is r2


class TestISpatialResolverProtocol:
    def test_protocol_compliance(self):
        resolver = ForceDirectedSpatialResolver()
        # Should satisfy the protocol
        result = resolver.resolve_coordinates(["test"], [])
        assert isinstance(result, dict)
        assert "test" in result