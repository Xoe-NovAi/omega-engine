import pytest
import tempfile
from pathlib import Path
from omega.oracle.entity_registry import EntityRegistry

def test_load_empty_yaml():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("") # Empty file
        path = f.name
    
    try:
        with pytest.raises(ValueError, match="entities.yaml is empty or malformed"):
            EntityRegistry(config_path=path)
    finally:
        Path(path).unlink()

def test_load_malformed_yaml():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("invalid: yaml: content:") # Malformed YAML
        path = f.name
    
    try:
        # EntityRegistry._load() wraps yaml.YAMLError in ValueError
        with pytest.raises(ValueError, match="empty or malformed"):
            EntityRegistry(config_path=path)
    finally:
        Path(path).unlink()
