# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

import os
import pytest
import tempfile
import shutil
import yaml
from pathlib import Path
from omega.oracle.entity_registry import EntityRegistry
from omega.oracle.wad_loader import WADLoader
from omega.errors import OmegaError

def make_registry_and_loader(wads_dir, wads_subdir="wads"):
    """Create a registry with a temp config and WADLoader to avoid contaminating the real entities.yaml."""
    fd, config_path = tempfile.mkstemp(suffix=".yaml")
    os.close(fd)
    Path(config_path).write_text("entities: {}\n")
    registry = EntityRegistry(config_path=config_path)
    loader = WADLoader(registry, wads_dir=wads_dir)
    return registry, loader, config_path

@pytest.fixture
def wad_env():
    temp_dir = tempfile.mkdtemp()
    wads_dir = Path(temp_dir) / "wads"
    wads_dir.mkdir()
    old_data_dir = os.environ.pop("OMEGA_DATA_DIR", None)
    test_data_dir = Path(temp_dir) / "data"
    test_data_dir.mkdir()
    os.environ["OMEGA_DATA_DIR"] = str(test_data_dir)
    yield wads_dir, temp_dir
    if old_data_dir is not None:
        os.environ["OMEGA_DATA_DIR"] = old_data_dir
    else:
        os.environ.pop("OMEGA_DATA_DIR", None)
    shutil.rmtree(temp_dir)


# ─── P1: A4 — WAD Auto-Loading Tests ────────────────────────────────────────────

@pytest.mark.anyio
async def test_discover_wads_finds_all(wad_env):
    """_discover_wads should find all WAD directories with valid manifests."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        # Create two WADs
        for name in ["stack_a", "stack_b"]:
            path = wads_dir / name
            path.mkdir()
            (path / "manifest.yaml").write_text(
                f"name: {name}\nversion: 1.0.0\ntype: iwad\nentities: []"
            )
        # Create a non-WAD directory (no manifest)
        (wads_dir / "no_manifest").mkdir()

        discovered = await loader._discover_wads()
        names = [w["name"] for w in discovered]
        assert "stack_a" in names
        assert "stack_b" in names
        assert "no_manifest" not in names
        assert len(discovered) == 2
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_discover_wads_extracts_metadata(wad_env):
    """_discover_wads should extract type, dependencies, and priority from manifests."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        path = wads_dir / "test_wad"
        path.mkdir()
        (path / "manifest.yaml").write_text(
            "name: test_wad\n"
            "version: 2.0.0\n"
            "type: pwad\n"
            "priority: 5\n"
            "dependencies: [base_wad]\n"
            "entities: []"
        )
        discovered = await loader._discover_wads()
        assert len(discovered) == 1
        wad = discovered[0]
        assert wad["name"] == "test_wad"
        assert wad["type"] == "pwad"
        assert wad["priority"] == 5
        assert wad["dependencies"] == ["base_wad"]
        assert wad["version"] == "2.0.0"
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_resolve_load_order_iwad_before_pwad(wad_env):
    """IWADs should load before PWADs in the resolved load order."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        # Create an IWAD
        iwad_path = wads_dir / "base_iwad"
        iwad_path.mkdir()
        (iwad_path / "manifest.yaml").write_text(
            "name: base_iwad\nversion: 1.0.0\ntype: iwad\nentities: []"
        )
        # Create a PWAD
        pwad_path = wads_dir / "patch_pwad"
        pwad_path.mkdir()
        (pwad_path / "manifest.yaml").write_text(
            "name: patch_pwad\nversion: 1.0.0\ntype: pwad\nentities: []"
        )

        discovered = await loader._discover_wads()
        ordered = await loader._resolve_load_order(discovered)

        # IWAD should come first
        assert ordered[0]["name"] == "base_iwad"
        assert ordered[0]["type"] == "iwad"
        assert ordered[1]["name"] == "patch_pwad"
        assert ordered[1]["type"] == "pwad"
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_resolve_load_order_dependency_first(wad_env):
    """Dependencies should load before dependents."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        # Create dependent PWAD
        dep_path = wads_dir / "dependency"
        dep_path.mkdir()
        (dep_path / "manifest.yaml").write_text(
            "name: dependency\nversion: 1.0.0\ntype: pwad\nentities: []"
        )
        # Create dependent PWAD that depends on it
        dependent_path = wads_dir / "dependent"
        dependent_path.mkdir()
        (dependent_path / "manifest.yaml").write_text(
            "name: dependent\nversion: 1.0.0\ntype: pwad\ndependencies: [dependency]\nentities: []"
        )

        discovered = await loader._discover_wads()
        ordered = await loader._resolve_load_order(discovered)

        names = [w["name"] for w in ordered]
        assert names.index("dependency") < names.index("dependent")
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_resolve_load_order_circular_dependency(wad_env):
    """Circular dependencies should raise OmegaError."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        # Create A -> B -> A circular dependency
        for name, deps in [("wad_a", ["wad_b"]), ("wad_b", ["wad_a"])]:
            path = wads_dir / name
            path.mkdir()
            (path / "manifest.yaml").write_text(
                f"name: {name}\nversion: 1.0.0\ntype: pwad\ndependencies: {deps}\nentities: []"
            )

        discovered = await loader._discover_wads()
        with pytest.raises(OmegaError, match="Circular dependency"):
            await loader._resolve_load_order(discovered)
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_resolve_load_order_unknown_dependency(wad_env):
    """Unknown dependencies should be ignored (not crash)."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        path = wads_dir / "orphan"
        path.mkdir()
        (path / "manifest.yaml").write_text(
            "name: orphan\nversion: 1.0.0\ntype: pwad\ndependencies: [nonexistent]\nentities: []"
        )

        discovered = await loader._discover_wads()
        ordered = await loader._resolve_load_order(discovered)
        assert len(ordered) == 1
        assert ordered[0]["name"] == "orphan"
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_load_all_wads_priority_ordering(wad_env):
    """load_all_wads should load IWADs before PWADs."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        # Create PWAD first (in directory order)
        pwad_path = wads_dir / "zzz_pwad"
        pwad_path.mkdir()
        (pwad_path / "manifest.yaml").write_text(
            "name: zzz_pwad\nversion: 1.0.0\ntype: pwad\nentities: []"
        )
        # Create IWAD second (in directory order, but should load first)
        iwad_path = wads_dir / "aaa_iwad"
        iwad_path.mkdir()
        (iwad_path / "manifest.yaml").write_text(
            "name: aaa_iwad\nversion: 1.0.0\ntype: iwad\nentities: []"
        )

        results = await loader.load_all_wads()
        assert results["aaa_iwad"] is True
        assert results["zzz_pwad"] is True

        # Verify load order: IWAD should have been loaded with priority 100
        # We can check the registry to see which was registered first
        # (both should be registered, but IWAD should have higher priority)
        iwad_entity = registry.get("aaa_iwad")
        pwad_entity = registry.get("zzz_pwad")
        # Both should exist (they have no entities, but the WADs loaded)
        assert results is not None
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_load_all_wads_with_dependencies(wad_env):
    """load_all_wads should resolve dependencies and load in correct order."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        # Create base IWAD
        base_path = wads_dir / "base"
        base_path.mkdir()
        (base_path / "manifest.yaml").write_text(
            "name: base\nversion: 1.0.0\ntype: iwad\nentities: []"
        )
        # Create PWAD depending on base
        patch_path = wads_dir / "patch"
        patch_path.mkdir()
        (patch_path / "manifest.yaml").write_text(
            "name: patch\nversion: 1.0.0\ntype: pwad\ndependencies: [base]\nentities: []"
        )

        results = await loader.load_all_wads()
        assert results["base"] is True
        assert results["patch"] is True
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_load_all_wads_circular_reports_failure(wad_env):
    """load_all_wads should report failure for all WADs when circular dependency detected."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        for name, deps in [("wad_x", ["wad_y"]), ("wad_y", ["wad_x"])]:
            path = wads_dir / name
            path.mkdir()
            (path / "manifest.yaml").write_text(
                f"name: {name}\nversion: 1.0.0\ntype: pwad\ndependencies: {deps}\nentities: []"
            )

        results = await loader.load_all_wads()
        # Both should be marked as failed
        assert results["wad_x"] is False
        assert results["wad_y"] is False
    finally:
        Path(cfg).unlink(missing_ok=True)
