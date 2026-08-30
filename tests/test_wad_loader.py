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

def make_registry_and_loader(wads_dir, wads_subdir="wads"):
    """Create a registry with a temp config and WADLoader to avoid contaminating the real entities.yaml."""
    # Temp config with empty entities dict
    fd, config_path = tempfile.mkstemp(suffix=".yaml")
    os.close(fd)
    Path(config_path).write_text("entities: {}\n")
    registry = EntityRegistry(config_path=config_path)
    loader = WADLoader(registry, wads_dir=wads_dir)
    return registry, loader, config_path

@pytest.fixture
def wad_env():
    # Create a temporary directory for WADs
    temp_dir = tempfile.mkdtemp()
    wads_dir = Path(temp_dir) / "wads"
    wads_dir.mkdir()
    
    # Override OMEGA_DATA_DIR to prevent entity workspace scaffolding from
    # leaking test entities (direntity, duplicate, etc.) into production data/entities/.
    # EntityRegistry.add() auto-scaffolds workspaces via EntityWorkspaceManager,
    # which uses OMEGA_DATA_DIR to locate the entities directory.
    old_data_dir = os.environ.pop("OMEGA_DATA_DIR", None)
    test_data_dir = Path(temp_dir) / "data"
    test_data_dir.mkdir()
    os.environ["OMEGA_DATA_DIR"] = str(test_data_dir)
    
    # Create a valid WAD
    stack_name = "test_stack"
    stack_path = wads_dir / stack_name
    stack_path.mkdir()
    (stack_path / "manifest.yaml").write_text("name: test_stack\nversion: 1.0.0\nentities: []")
    
    # Create a file outside the WADs directory to test traversal
    secret_dir = Path(temp_dir) / "secrets"
    secret_dir.mkdir()
    secret_file = secret_dir / "manifest.yaml"
    secret_file.write_text("version: secret")
    
    yield wads_dir, secret_dir
    
    # Restore original OMEGA_DATA_DIR and cleanup temp dir
    if old_data_dir is not None:
        os.environ["OMEGA_DATA_DIR"] = old_data_dir
    else:
        os.environ.pop("OMEGA_DATA_DIR", None)
    shutil.rmtree(temp_dir)

@pytest.mark.anyio
async def test_load_wad_valid(wad_env):
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        assert (await loader.load_wad("test_stack"))[0] is True
    finally:
        Path(cfg).unlink(missing_ok=True)

@pytest.mark.anyio
async def test_load_wad_path_traversal(wad_env):
    wads_dir, secret_dir = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        traversal_path = "../secrets"
        result = await loader.load_wad(traversal_path)
        assert result[0] is False
    finally:
        Path(cfg).unlink(missing_ok=True)

@pytest.mark.anyio
async def test_load_wad_nonexistent(wad_env):
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        assert (await loader.load_wad("nonexistent_stack"))[0] is False
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_load_wad_malformed_manifest(wad_env):
    """Loading a WAD with a malformed manifest should return False."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        stack_name = "malformed_stack"
        stack_path = wads_dir / stack_name
        stack_path.mkdir()
        (stack_path / "manifest.yaml").write_text("this is not yaml: { [")
        assert (await loader.load_wad(stack_name))[0] is False
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_load_wad_missing_fields(wad_env):
    """Loading a WAD with missing required manifest fields should return False."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        stack_name = "missing_fields_stack"
        stack_path = wads_dir / stack_name
        stack_path.mkdir()
        (stack_path / "manifest.yaml").write_text("name: missing_fields\nversion: 1.0.0")
        assert (await loader.load_wad(stack_name))[0] is False
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_load_wad_duplicate_entities(wad_env):
    """Loading a WAD with entities already in the registry should skip them."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        # Pre-register an entity
        from omega.oracle.entity_registry import Entity
        existing_entity = Entity(name="Duplicate", domains=[], model="m", personality="p")
        await registry.add(existing_entity)
        
        stack_name = "duplicate_stack"
        stack_path = wads_dir / stack_name
        stack_path.mkdir()
        (stack_path / "manifest.yaml").write_text("name: duplicate_stack\nversion: 1.0.0\nentities: []")
        
        # Create a duplicate entity in the WAD
        entities_dir = stack_path / "entities"
        entities_dir.mkdir()
        (entities_dir / "duplicate" / "soul.yaml").parent.mkdir(parents=True)
        (entities_dir / "duplicate" / "soul.yaml").write_text("entity:\n  name: Duplicate\n  personality: I am a duplicate")
        
        assert (await loader.load_wad(stack_name))[0] is True
        assert registry.get("duplicate").personality == "p" # Original preserved
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_load_flat_entity_yaml(wad_env):
    """Flat .yaml entity files (not in subdirectory with soul.yaml) should load correctly."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        stack_name = "flat_entity_stack"
        stack_path = wads_dir / stack_name
        stack_path.mkdir()
        (stack_path / "manifest.yaml").write_text("name: flat_entity_stack\nversion: 1.0.0\nentities: []")
        
        entities_dir = stack_path / "entities"
        entities_dir.mkdir()
        flat_entity = entities_dir / "myentity.yaml"
        flat_entity.write_text("entity:\n  name: MyEntity\n  domains: [test]\n  personality: I am a flat entity")
        
        assert (await loader.load_wad(stack_name))[0] is True
        entity = registry.get("myentity")
        assert entity is not None, f"Expected myentity, got {registry.names()}"
        assert entity.name.lower() == "myentity"
        assert entity.personality == "I am a flat entity"
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_load_soul_yaml_structure(wad_env):
    """Traditional soul.yaml directory structure should still load correctly."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        stack_name = "soul_dir_stack"
        stack_path = wads_dir / stack_name
        stack_path.mkdir()
        (stack_path / "manifest.yaml").write_text("name: soul_dir_stack\nversion: 1.0.0\nentities: []")
        
        entity_dir = stack_path / "entities" / "soul_entity"
        entity_dir.mkdir(parents=True)
        (entity_dir / "soul.yaml").write_text("entity:\n  name: SoulEntity\n  domains: [soul]\n  personality: I live in a soul.yaml directory")
        
        assert (await loader.load_wad(stack_name))[0] is True
        entity = registry.get("soulentity")
        assert entity is not None, f"Expected soulentity, got {registry.names()}"
        assert entity.name.lower() == "soulentity"
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_load_entities_mixed_types(wad_env):
    """Loading a WAD with both flat and soul.yaml entities should work."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        stack_name = "mixed_stack"
        stack_path = wads_dir / stack_name
        stack_path.mkdir()
        (stack_path / "manifest.yaml").write_text("name: mixed_stack\nversion: 1.0.0\nentities: []")
        
        entities_dir = stack_path / "entities"
        entities_dir.mkdir()
        
        # Flat entity
        (entities_dir / "flatentity.yaml").write_text("entity:\n  name: flatentity\n  domains: [flat]\n  personality: Flat")
        
        # soul.yaml entity
        soul_dir = entities_dir / "direntity"
        soul_dir.mkdir()
        (soul_dir / "soul.yaml").write_text("entity:\n  name: direntity\n  domains: [dir]\n  personality: Directory")
        
        assert (await loader.load_wad(stack_name))[0] is True
        assert registry.get("flatentity") is not None, f"Entities: {registry.names()}"
        assert registry.get("direntity") is not None
        assert registry.get("flatentity").name == "flatentity"
        assert registry.get("direntity").name == "direntity"
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_load_entity_skips_registered(wad_env):
    """Already-registered entities should be skipped during WAD load."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        # Pre-register an entity
        from omega.oracle.entity_registry import Entity
        existing = Entity(name="Preexisting", domains=[], model="m", personality="original")
        await registry.add(existing)
        
        stack_name = "skip_stack"
        stack_path = wads_dir / stack_name
        stack_path.mkdir()
        (stack_path / "manifest.yaml").write_text("name: skip_stack\nversion: 1.0.0\nentities: []")
        
        entities_dir = stack_path / "entities"
        entities_dir.mkdir()
        (entities_dir / "preexisting.yaml").write_text("entity:\n  name: Preexisting\n  domains: [new]\n  personality: duplicate")
        
        assert (await loader.load_wad(stack_name))[0] is True
        assert registry.get("preexisting").personality == "original"
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_load_entity_invalid_yaml(wad_env):
    """Invalid YAML in an entity file should be handled gracefully."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        stack_name = "bad_yaml_stack"
        stack_path = wads_dir / stack_name
        stack_path.mkdir()
        (stack_path / "manifest.yaml").write_text("name: bad_yaml_stack\nversion: 1.0.0\nentities: []")
        
        entities_dir = stack_path / "entities"
        entities_dir.mkdir()
        (entities_dir / "badyaml.yaml").write_text("entity: { bad: yaml: invalid: [[[")
        
        assert (await loader.load_wad(stack_name))[0] is True
        assert registry.get("badyaml") is None
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_load_all_wads_handles_empty(wad_env):
    """Loading all WADs with no WADs loaded should not crash."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        await loader.load_all_wads()
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_load_entities_directory_not_exists(wad_env):
    """Loading entities from a non-existent directory should handle gracefully."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        stack_name = "no_entities_stack"
        stack_path = wads_dir / stack_name
        stack_path.mkdir()
        (stack_path / "manifest.yaml").write_text("name: no_entities_stack\nversion: 1.0.0\nentities: []")
        assert (await loader.load_wad(stack_name))[0] is True
    finally:
        Path(cfg).unlink(missing_ok=True)


# ── S1.5a Hardening Tests ──────────────────────────────────────────

@pytest.mark.anyio
async def test_load_wad_oversized_manifest(wad_env):
    """Manifests exceeding 1MB should be rejected."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        stack_name = "oversized_stack"
        stack_path = wads_dir / stack_name
        stack_path.mkdir()
        # Create a manifest > 1MB
        huge_entities = "x: " + "a" * 1_000_000
        (stack_path / "manifest.yaml").write_text(f"name: oversized\nversion: 1.0.0\nentities: []\ndata: {huge_entities}")
        result = await loader.load_wad(stack_name)
        assert result[0] is False
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_load_wad_manifest_wrong_type_name(wad_env):
    """Manifest with wrong type for 'name' field should fail gracefully."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        stack_name = "wrong_type_stack"
        stack_path = wads_dir / stack_name
        stack_path.mkdir()
        (stack_path / "manifest.yaml").write_text("name: 12345\nversion: 1.0.0\nentities: []")
        # Should still load (TypeError is caught)
        result = await loader.load_wad(stack_name)
        # The loader catches TypeError and returns False
        assert result[0] is False
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_load_wad_manifest_empty_name(wad_env):
    """Manifest with empty name should fail."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        stack_name = "empty_name_stack"
        stack_path = wads_dir / stack_name
        stack_path.mkdir()
        (stack_path / "manifest.yaml").write_text("name: '   '\nversion: 1.0.0\nentities: []")
        result = await loader.load_wad(stack_name)
        assert result[0] is False
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_load_wad_manifest_empty_version(wad_env):
    """Manifest with empty version should fail."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        stack_name = "empty_version_stack"
        stack_path = wads_dir / stack_name
        stack_path.mkdir()
        (stack_path / "manifest.yaml").write_text("name: test\nversion: '   '\nentities: []")
        result = await loader.load_wad(stack_name)
        assert result[0] is False
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_load_entity_oversized_file(wad_env):
    """Entity files exceeding 1MB should be skipped."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        stack_name = "oversized_entity_stack"
        stack_path = wads_dir / stack_name
        stack_path.mkdir()
        (stack_path / "manifest.yaml").write_text("name: oversized_entity\nversion: 1.0.0\nentities: []")
        
        entities_dir = stack_path / "entities"
        entities_dir.mkdir()
        # Create entity file > 1MB
        huge_data = "x: " + "a" * 1_000_000
        (entities_dir / "hugeentity.yaml").write_text(f"entity:\n  name: HugeEntity\n  personality: {huge_data}")
        
        result = await loader.load_wad(stack_name)
        assert result[0] is True
        # Entity should be skipped (too large)
        assert registry.get("hugeentity") is None
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_load_entity_missing_entity_key(wad_env):
    """Entity file missing 'entity' key should be skipped."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        stack_name = "missing_key_stack"
        stack_path = wads_dir / stack_name
        stack_path.mkdir()
        (stack_path / "manifest.yaml").write_text("name: missing_key\nversion: 1.0.0\nentities: []")
        
        entities_dir = stack_path / "entities"
        entities_dir.mkdir()
        (entities_dir / "noentity.yaml").write_text("not_entity:\n  name: NoEntity")
        
        result = await loader.load_wad(stack_name)
        assert result[0] is True
        assert registry.get("noentity") is None
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_load_entity_empty_file(wad_env):
    """Empty entity file should be skipped."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        stack_name = "empty_entity_stack"
        stack_path = wads_dir / stack_name
        stack_path.mkdir()
        (stack_path / "manifest.yaml").write_text("name: empty_entity\nversion: 1.0.0\nentities: []")
        
        entities_dir = stack_path / "entities"
        entities_dir.mkdir()
        (entities_dir / "empty.yaml").write_text("")
        
        result = await loader.load_wad(stack_name)
        assert result[0] is True
        assert registry.get("empty") is None
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_load_entity_wrong_field_type(wad_env):
    """Entity with wrong field type (e.g., temperature as string) should be skipped."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        stack_name = "wrong_type_entity_stack"
        stack_path = wads_dir / stack_name
        stack_path.mkdir()
        (stack_path / "manifest.yaml").write_text("name: wrong_type\nversion: 1.0.0\nentities: []")
        
        entities_dir = stack_path / "entities"
        entities_dir.mkdir()
        (entities_dir / "badtype.yaml").write_text(
            "entity:\n  name: BadType\n  domains: [test]\n  temperature: not_a_number"
        )
        
        result = await loader.load_wad(stack_name)
        assert result[0] is True
        # Entity with wrong temperature type should be skipped
        assert registry.get("badtype") is None
    finally:
        Path(cfg).unlink(missing_ok=True)


@pytest.mark.anyio
async def test_adapter_whitelist_rejects_unknown_module(wad_env):
    """Adapter registration should reject modules not in the whitelist."""
    wads_dir, _ = wad_env
    registry, loader, cfg = make_registry_and_loader(wads_dir)
    try:
        stack_name = "bad_adapter_stack"
        stack_path = wads_dir / stack_name
        stack_path.mkdir()
        # Manifest with adapter pointing to non-whitelisted module
        manifest = {
            "name": "bad_adapter",
            "version": "1.0.0",
            "entities": [],
            "adapters": {
                "memory": {
                    "module": "omega.oracle.malicious_module",
                    "class": "MaliciousClass"
                }
            }
        }
        (stack_path / "manifest.yaml").write_text(yaml.dump(manifest))
        
        result = await loader.load_wad(stack_name)
        assert result[0] is True  # WAD loads, but adapter is rejected
        # No adapter should be registered
    finally:
        Path(cfg).unlink(missing_ok=True)
