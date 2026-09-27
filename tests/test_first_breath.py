# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

import pytest
import anyio
import os
import json
from pathlib import Path
from src.omega.oracle.oracle import Oracle
from src.omega.oracle.entity_registry import EntityRegistry, Entity
from src.omega.astrology import get_birth_record
from unittest.mock import AsyncMock
from omega.memory.sqlite_vec_adapter import CANONICAL_DIMENSION
from omega.memory_store import reset_memory_store

# ── FIRST-BREATH SYSTEM DISABLED — D-605 (2026-09-20, Architect ruling) ──────────────
# Why (verified on 70291e94 by Cline, 2026-09-20):
#   1. `record_first_breath()` is DEFINED at src/omega/astrology.py:153 but is NEVER
#      called from the summon path anywhere in src/ — the hook is unwired dead code.
#   2. This test nonetheless passed LOCALLY only because the untracked
#      data/memory/entity_births.db holds a stale row for "testentity" dated 2026-06-13.
#      In CI (no data/ checkout) the DB is empty → `assert record is not None` fails.
#   3. The fixture patches `omega.astrology.BIRTH_DB_PATH` but imports from
#      `src.omega.astrology` — the same file under two module identities — so the
#      tmp_path isolation never took effect.
# Disabled (not deleted) pending the post-PR#3 first-breath re-implementation.
pytestmark = pytest.mark.skip(
    reason="FIRST-BREATH SYSTEM DISABLED (D-605): the hook is unwired dead code and this "
           "test was masked by a stale local DB row; scheduled for a post-PR#3 update."
)

@pytest.fixture
async def oracle_setup(tmp_path):
    # 1. Reset singleton and set isolated data dir
    reset_memory_store()
    os.environ["OMEGA_DATA_DIR"] = str(tmp_path)
    
    # 2. Patch BIRTH_DB_PATH to use tmp_path
    import omega.astrology
    omega.astrology.BIRTH_DB_PATH = tmp_path / "entity_births.db"
    
    # 2b. Pre-create entities dir — archive_old_sessions() iterates it during bootstrap
    (tmp_path / "memory" / "entities").mkdir(parents=True, exist_ok=True)
    
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
        slots=["p1"],
        role="Test Entity",
    )
    await registry.add(test_entity)
    
    # 6. Mock embedding manager to avoid Ollama/Qdrant hangs
    oracle.memory_store.embedding_manager = AsyncMock()
    # [D-1024-DIM-NATIVE-20260926] mock must answer at the canonical width,
    # otherwise the adapter's dimension guard rejects every write (M23).
    oracle.memory_store.embedding_manager.get_embedding.return_value = (
        [0.0] * CANONICAL_DIMENSION,
        "mock",
    )
    oracle.memory_store.embedding_manager.current_dimension = CANONICAL_DIMENSION
    
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

    # Deterministic domain routing: pin the semantic router to testentity so
    # this test verifies the BIRTH-RECORD mechanism, not router internals
    # (tfidf_svm can route "Tell me about test" to researcher in CI).
    from unittest.mock import AsyncMock
    from omega.oracle.entity_registry import EntityRegistry
    reg = oracle.registry
    test_entity = reg.get("testentity")
    oracle.semantic_router.route = AsyncMock(
        return_value=(test_entity, 0.9, "keyword")
    )

    # Test that routing by domain also records birth
    await oracle.talk("Tell me about test")

    # The entity assigned to "test" domain should have a birth record
    # Based on our setup, "testentity" is the match
    record = await get_birth_record("testentity")
    assert record is not None
