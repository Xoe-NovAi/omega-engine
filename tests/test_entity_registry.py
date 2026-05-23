"""Tests for Omega Entity Registry."""

import tempfile
from pathlib import Path

import pytest
import yaml

from omega.oracle.entity_registry import Entity, EntityRegistry


SAMPLE_YAML = """
entities:
  test_entity:
    name: TestEntity
    pillars: ["P0: Test"]
    pantheon: Test
    element: "Earth 🜃"
    chakra: Root
    planet: "♁ Gaia"
    sigil: "★ Test Star"
    glyph: "🜃"
    domains: [test, example, sample]
    model: qwen3-1.7b-q6_k
    personality: "You are a test entity."
    temperature: 0.5
    context_window: 8192
    invocation: "O test entity, awaken."
"""


@pytest.fixture
def temp_config():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(SAMPLE_YAML)
        path = f.name
    yield path
    Path(path).unlink(missing_ok=True)


def test_load_entities(temp_config):
    registry = EntityRegistry(config_path=temp_config)
    assert registry.count() == 1

    entity = registry.get("testentity")
    assert entity is not None
    assert entity.name == "TestEntity"
    assert entity.pillars == ["P0: Test"]
    assert entity.pantheon == "Test"
    assert entity.element == "Earth 🜃"
    assert entity.sigil == "★ Test Star"


def test_list_entities(temp_config):
    registry = EntityRegistry(config_path=temp_config)
    entities = registry.list()
    assert len(entities) == 1
    assert entities[0].name == "TestEntity"


def test_list_pillar_keepers(temp_config):
    registry = EntityRegistry(config_path=temp_config)
    keepers = registry.list_pillar_keepers()
    assert len(keepers) == 1


def test_get_nonexistent(temp_config):
    registry = EntityRegistry(config_path=temp_config)
    assert registry.get("unknown") is None


def test_find_by_domain(temp_config):
    registry = EntityRegistry(config_path=temp_config)
    result = registry.find_by_domain("this is a test query")
    assert result is not None
    assert result.name == "TestEntity"


def test_find_by_domain_no_match(temp_config):
    registry = EntityRegistry(config_path=temp_config)
    result = registry.find_by_domain("completely unrelated topic")
    assert result is None


def test_entity_to_dict():
    entity = Entity(
        name="Test",
        domains=["test"],
        model="qwen3-1.7b-q6_k",
        personality="Test personality",
        pillars=["P0: Test"],
    )
    d = entity.to_dict()
    assert d["name"] == "Test"
    assert d["pillars"] == ["P0: Test"]
    # Fields with None should not be included
    assert "element" not in d


@pytest.mark.asyncio
async def test_entity_registry_concurrent_add():
    """Stress test concurrent add() calls to ensure lock prevents corruption."""
    import anyio
    
    # Use a temporary config file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("entities: {}")
        config_path = f.name
    
    try:
        registry = EntityRegistry(config_path=config_path)
        
        async def add_entity(i):
            ent = Entity(
                name=f"Entity_{i}",
                domains=[f"domain_{i}"],
                model="qwen3-1.7b",
                personality=f"Personality {i}",
            )
            await registry.add(ent)
        
        async with anyio.create_task_group() as tg:
            for i in range(50):
                tg.start_soon(add_entity, i)
        
        assert registry.count() == 50
        
        # Verify file integrity
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
            assert len(data["entities"]) == 50
            
    finally:
        Path(config_path).unlink(missing_ok=True)
