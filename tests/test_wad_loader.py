import pytest
import tempfile
import shutil
from pathlib import Path
from omega.oracle.entity_registry import EntityRegistry
from omega.oracle.wad_loader import WADLoader

@pytest.fixture
def wad_env():
    # Create a temporary directory for WADs
    temp_dir = tempfile.mkdtemp()
    wads_dir = Path(temp_dir) / "wads"
    wads_dir.mkdir()
    
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
    
    # Cleanup
    shutil.rmtree(temp_dir)

@pytest.mark.asyncio
async def test_load_wad_valid(wad_env):
    wads_dir, _ = wad_env
    registry = EntityRegistry(config_path=None) # Mock registry
    loader = WADLoader(registry, wads_dir=wads_dir)
    
    assert await loader.load_wad("test_stack") is True

@pytest.mark.asyncio
async def test_load_wad_path_traversal(wad_env):
    wads_dir, secret_dir = wad_env
    registry = EntityRegistry(config_path=None)
    loader = WADLoader(registry, wads_dir=wads_dir)
    
    # Attempt to traverse to the secrets directory
    # wads_dir is /tmp/.../wads, secret_dir is /tmp/.../secrets
    # Traversal: ../secrets
    traversal_path = "../secrets"
    
    # This should be blocked by the path traversal guard
    result = await loader.load_wad(traversal_path)
    assert result is False

@pytest.mark.asyncio
async def test_load_wad_nonexistent(wad_env):
    wads_dir, _ = wad_env
    registry = EntityRegistry(config_path=None)
    loader = WADLoader(registry, wads_dir=wads_dir)
    
    assert await loader.load_wad("nonexistent_stack") is False
