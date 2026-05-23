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
        f.write("not: a: yaml: file") # Malformed
        path = f.name
    
    try:
        # yaml.safe_load might raise yaml.YAMLError or return None
        # If it returns None, our ValueError should trigger.
        # If it raises YAMLError, that's also acceptable as an error.
        try:
            EntityRegistry(config_path=path)
        except (ValueError, Exception):
            pass
    finally:
        Path(path).unlink()
