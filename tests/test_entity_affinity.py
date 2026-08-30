# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

import pytest
import yaml
from pathlib import Path
from omega.oracle.entity_affinity import EntityAffinityResolver, AffinityResult, InferencePreset
from omega.errors import ProviderValidationError

@pytest.fixture
def affinity_yaml(tmp_path):
    """Create a temporary affinity YAML for testing."""
    yaml_content = {
        "__default__": {
            "preferred_models": {
                "local_fast": {"model": "default-fast", "provider": "native-gguf"},
                "local_deep": {"model": "default-deep", "provider": "native-gguf"},
                "cloud": {"model": "default-cloud", "provider": "google"},
            },
            "routing_rules": [
                {"match": {"domain": ["general"]}, "use": "iris"},
                {"match": {"complexity_gt": 0.8}, "use": "local_deep"},
                {"match": {"online": True}, "use": "cloud"},
            ],
            "inference_presets": {
                "temperature": 0.7,
                "preferred_context": 8192,
            },
        },
    "test_entity": {
        "preferred_models": {
            "local_fast": {"model": "test-fast", "provider": "native-gguf"},
            "local_deep": {"model": "test-deep", "provider": "native-gguf"},
            "cloud": {"model": "test-cloud", "provider": "google"},
        },
        "routing_rules": [
            {"match": {"domain": ["coding"]}, "use": "local_fast"},
            {"match": {"complexity_gt": 0.5}, "use": "cloud"},
            {"match": {"prompt_length_lt": 10}, "use": "iris"},
        ],
        "inference_presets": {
            "temperature": 0.2,
            "system_prompt": "Test System Prompt",
            "preferred_context": 16384,
        },
    },
    }
    path = tmp_path / "test_affinity.yaml"
    with open(path, "w") as f:
        yaml.dump(yaml_content, f)
    return path

@pytest.mark.asyncio
async def test_basic_resolution(affinity_yaml):
    """Test that an entity is resolved to its default local_fast model."""
    resolver = EntityAffinityResolver(yaml_path=affinity_yaml)
    await resolver.load()
    
    # No context, should use default tier (local_fast)
    result = await resolver.resolve("test_entity", query="Hello")
    assert result is not None
    assert result.best_match == "test-fast"
    assert result.tier == "local_fast"
    assert result.inference_presets.temperature == 0.2

@pytest.mark.asyncio
async def test_structured_match_domain(affinity_yaml):
    """Test routing based on domain match."""
    resolver = EntityAffinityResolver(yaml_path=affinity_yaml)
    await resolver.load()
    
    result = await resolver.resolve("test_entity", query="Write code", context={"domain": "coding"})
    assert result.tier == "local_fast"
    assert result.best_match == "test-fast"

@pytest.mark.asyncio
async def test_structured_match_complexity_online(affinity_yaml):
    """Test routing based on complexity and online status."""
    resolver = EntityAffinityResolver(yaml_path=affinity_yaml)
    await resolver.load()
    
    # Complexity > 0.5 and online = True -> cloud
    result = await resolver.resolve("test_entity", query="Hard problem", context={"complexity": 0.7, "online": True})
    assert result.tier == "cloud"
    assert result.best_match == "test-cloud"
    
    # Complexity > 0.5 but offline -> fallback to local_deep (if available) or local_fast
    result = await resolver.resolve("test_entity", query="Hard problem", context={"complexity": 0.7, "online": False})
    # Since cloud is unavailable, it should fall back to the next available tier in the list.
    # In our YAML, local_deep is available.
    assert result.tier != "cloud"
    assert result.best_match == "test-deep"

@pytest.mark.asyncio
async def test_prompt_length_match(affinity_yaml):
    """Test routing based on prompt length."""
    resolver = EntityAffinityResolver(yaml_path=affinity_yaml)
    await resolver.load()
    
    # Short prompt -> iris target
    result = await resolver.resolve("test_entity", query="Hi", context={})
    # Since 'iris' tier is not defined in preferred_models, it should fall back to local_fast
    assert result.best_match == "test-fast"
    assert result.tier == "local_fast"

@pytest.mark.asyncio
async def test_default_entity_resolution(affinity_yaml):
    """Test resolution for unknown entities using __default__ config."""
    resolver = EntityAffinityResolver(yaml_path=affinity_yaml)
    await resolver.load()
    
    result = await resolver.resolve("unknown_entity", query="General query", context={"domain": "general"})
    assert result is not None
    assert result.tier == "local_fast"
    assert result.best_match == "default-fast"

@pytest.mark.asyncio
async def test_provider_validation_r3(affinity_yaml, caplog):
    """Test that unknown providers trigger a warning (R3)."""
    # Modify YAML to include an unknown provider
    yaml_content = {
        "test_entity": {
            "preferred_models": {
                "local_fast": {"model": "m", "provider": "unknown-provider-xyz"},
                "local_deep": {"model": "d", "provider": "native-gguf"},
            },
        }
    }
    path = affinity_yaml.with_name("invalid_provider.yaml")
    with open(path, "w") as f:
        yaml.dump(yaml_content, f)
        
    resolver = EntityAffinityResolver(yaml_path=path)
    with pytest.raises(ProviderValidationError) as excinfo:
        await resolver.load()
    
    assert "R3 Provider Chain Validation failed" in str(excinfo.value)
    assert "unknown-provider-xyz" in str(excinfo.value)

@pytest.mark.asyncio
async def test_legacy_dict_conversion(affinity_yaml):
    """Test the .to_legacy_dict() method for backward compatibility."""
    resolver = EntityAffinityResolver(yaml_path=affinity_yaml)
    await resolver.load()
    
    result = await resolver.resolve("test_entity", query="Hello")
    legacy_dict = result.to_legacy_dict()
    
    assert legacy_dict["entity"] == "test_entity"
    assert "inference_presets" in legacy_dict
    assert legacy_dict["inference_presets"]["temperature"] == 0.2
