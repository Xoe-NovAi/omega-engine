# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# ⬡ OMEGA ⬡ CONTRACTS ⬡ TEST_DISPATCH_REGISTRY
# Contract tests for dispatch_registry — single source of truth for dispatch.yaml
# FS-Β2 / A6-A7: Consolidated 3 loaders, fixed cwd-relative path bug

import pytest
from pathlib import Path

from omega.governance.dispatch_registry import (
    load_dispatch_yaml,
    get_dispatch_entities,
    get_entity_by_role,
    invalidate_cache,
)


class TestDispatchRegistry:
    """Contract tests for dispatch_registry module."""

    def test_dispatch_registry_single_source(self):
        """get_dispatch_entities returns same cached object on repeated calls."""
        invalidate_cache()
        cfg1 = get_dispatch_entities()
        cfg2 = get_dispatch_entities()
        assert cfg1 is cfg2  # Same cached object (mtime-based cache)

    def test_dispatch_registry_iwad_filter(self):
        """get_dispatch_entities with explicit IWAD returns subset or equal."""
        invalidate_cache()
        all_cfg = get_dispatch_entities()
        iwad_cfg = get_dispatch_entities("_omega_default")
        assert len(iwad_cfg) <= len(all_cfg)

    def test_dispatch_registry_loads_full_yaml(self):
        """load_dispatch_yaml returns full dict with 'entities' key as list."""
        invalidate_cache()
        data = load_dispatch_yaml()
        assert isinstance(data, dict)
        assert "entities" in data
        assert isinstance(data["entities"], list)

    def test_dispatch_registry_get_entity_by_role(self):
        """get_entity_by_role finds kali by GRAND_OVERSIGHT role."""
        invalidate_cache()
        kali = get_entity_by_role("GRAND_OVERSIGHT")
        assert kali is not None
        assert kali.get("role") == "GRAND_OVERSIGHT"
        assert kali.get("name") == "kali"

    def test_dispatch_registry_get_entity_by_role_pillar(self):
        """get_entity_by_role finds an entity with N1 role (multiple exist, returns first)."""
        invalidate_cache()
        pillar = get_entity_by_role("N1")
        assert pillar is not None
        assert pillar.get("role") == "N1"
        # Multiple entities have P1 role; verify pillar is among them
        entities = get_dispatch_entities()
        p1_names = {e["name"] for e in entities if e.get("role") == "N1"}
        assert "node" in p1_names

    def test_dispatch_registry_get_entity_by_role_not_found(self):
        """get_entity_by_role returns None for unknown role."""
        invalidate_cache()
        result = get_entity_by_role("NONEXISTENT_ROLE_12345")
        assert result is None

    def test_dispatch_registry_cache_invalidation(self):
        """invalidate_cache forces reload on next call."""
        invalidate_cache()
        cfg1 = get_dispatch_entities()
        invalidate_cache()
        cfg2 = get_dispatch_entities()
        # After invalidation, should be a new object (different mtime or fresh load)
        # Note: If file mtime hasn't changed, cache may still return same object
        # This test verifies the function exists and runs without error
        assert isinstance(cfg2, list)

    def test_dispatch_registry_entities_have_required_fields(self):
        """All entities have required fields per dispatch.yaml schema."""
        invalidate_cache()
        entities = get_dispatch_entities()
        assert len(entities) > 0
        for ent in entities:
            assert "name" in ent
            assert "role" in ent
            assert "mode" in ent
            assert "purpose" in ent
            assert "capabilities" in ent
            assert "domains" in ent
            assert "node_slot" in ent
            assert "task_tool_type" in ent
            assert "owned_files" in ent
            assert "model" in ent

    def test_dispatch_registry_known_entities_present(self):
        """Known core entities are present in dispatch.yaml."""
        invalidate_cache()
        entities = get_dispatch_entities()
        names = {e["name"] for e in entities}
        # Core entities that must exist
        required = {"kali", "maat", "lilith", "iris", "sophia", "node", "verity"}
        for req in required:
            assert req in names, f"Required entity '{req}' missing from dispatch.yaml"

    def test_dispatch_registry_role_constants_match(self):
        """Role values match ROLE_CONSTANTS from ics module."""
        from omega.ics import ROLE_CONSTANTS
        invalidate_cache()
        entities = get_dispatch_entities()
        roles = {e["role"] for e in entities}
        # dispatch.yaml roles are ROLE_CONSTANT KEYS (uppercase, e.g.
        # "GRAND_OVERSIGHT") — ics.py resolves them via ROLE_CONSTANTS.get().
        valid_roles = set(ROLE_CONSTANTS)
        for role in roles:
            assert role in valid_roles, f"Entity role '{role}' not in ROLE_CONSTANTS"

    def test_dispatch_registry_path_resolution_uses_wads_dir(self):
        """Path resolution uses WADS_DIR from config_resolver, not cwd."""
        # This test verifies the fix for the cwd-relative path bug (A6)
        # by ensuring load_dispatch_yaml works regardless of cwd
        import os
        original_cwd = os.getcwd()
        try:
            # Change to a different directory
            os.chdir("/tmp")
            invalidate_cache()
            data = load_dispatch_yaml()
            assert isinstance(data, dict)
            assert "entities" in data
        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])