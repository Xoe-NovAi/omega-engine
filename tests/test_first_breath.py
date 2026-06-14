import pytest
import anyio
import os
import json
from pathlib import Path
from src.omega.oracle.oracle import Oracle
from src.omega.oracle.entity_registry import EntityRegistry, Entity
from src.omega.astrology import get_birth_record
from unittest.mock import AsyncMock
from omega.memory_store import reset_memory_store

@pytest.fixture
async def oracle_setup(tmp_path):
    # 1. Reset singleton and set isolated data dir
    reset_memory_store()
    os.environ["OMEGA_DATA_DIR"] = str(tmp_path)
    
    # 2. Patch BIRTH_DB_PATH to use tmp_path
    import omega.astrology
    omega.astrology.BIRTH_DB_PATH = tmp_path / "entity_births.db"
    
    # 3. Setup Registry and other components with FRESH HealthMonitor (not singleton)
    registry = EntityRegistry()
    from omega.oracle.health_monitor import HealthMonitor
    hm = HealthMonitor()  # Fresh instance, not singleton
    from omega.oracle.model_gateway import ModelGateway
    mg = ModelGateway(health_monitor=hm)
    oracle = Oracle(registry=registry, model_gateway=mg)
    
    # 4. Bootstrap
    await oracle.bootstrap()
    
    # 5. Create a test entity
    test_entity = Entity(
        name="testentity",
        domains=["test"],
        model="mock",
        personality="A test entity",
        pillars=["p1"],
        role="Test Entity",
    )
    await registry.add(test_entity)
    
    # 6. Mock embedding manager to avoid Ollama/Qdrant hangs
    oracle.memory_store.embedding_manager = AsyncMock()
    oracle.memory_store.embedding_manager.get_embedding.return_value = [0.0] * 768
    oracle.memory_store.embedding_manager.current_dimension = 768
    
    # 7. Setup session
    session_id = "test_session_123"
    session_dir = tmp_path / "sessions"
    session_dir.mkdir(exist_ok=True)
    session_file = session_dir / f"{session_id}.active"
    with open(session_file, "w") as f:
        json.dump({"entity": "testentity", "session_id": session_id}, f)
        
    return oracle, "testentity"

@pytest.mark.anyio
async def test_first_breath_recording(oracle_setup):
    oracle, entity_id = oracle_setup
    
    # 1. First utterance should record birth
    await oracle.summon(entity_id, "Hello world!")
    
    record = await get_birth_record(entity_id)
    assert record is not None
    assert record.entity_id == entity_id
    assert record.timezone == "UTC"
    
    timestamp1 = record.utc_timestamp
    
    # 2. Second utterance should NOT change the birth record (idempotency)
    # Wait a bit to ensure timestamp would change if updated
    await anyio.sleep(0.1)
    await oracle.summon(entity_id, "Hello again!")
    
    record2 = await get_birth_record(entity_id)
    assert record2 is not None
    assert record2.utc_timestamp == timestamp1
    
@pytest.mark.anyio
async def test_first_breath_domain_routing(oracle_setup):
    oracle, _ = oracle_setup
    
    # Test that routing by domain also records birth
    await oracle.talk("Tell me about test")
    
    # The entity assigned to "test" domain should have a birth record
    # Based on our setup, "testentity" is the match
    record = await get_birth_record("testentity")
    assert record is not None
