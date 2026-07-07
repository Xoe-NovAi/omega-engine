import pytest
import anyio
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock
from src.omega.oracle.oracle import Oracle
from src.omega.oracle.model_gateway import ModelGateway
from src.omega.oracle.entity_registry import EntityRegistry
from src.omega.oracle.backends.mock import OfflineMockBackend
from src.omega.oracle.session_lifecycle import SessionState

@pytest.mark.anyio
async def test_e2e_inference_chain():
    # 1. Setup: Create an Oracle with a Mock Backend
    # We use a custom ModelGateway that always uses the Mock backend
    oracle = Oracle()
    
    # Force the ModelGateway to use the Mock backend for all requests
    oracle.model_gateway.providers = [oracle.model_gateway._mock_backend]
    oracle.model_gateway._local_active = ["mock"]
    
    # 2. Execute: A full query cycle
    query = "What is the core mission of the Omega Engine?"
    entity_name = "sophia"
    
    # We use summon to ensure the full chain is exercised
    response = await oracle.summon(entity_name, query)
    
    # 3. Verify: Response Integrity
    assert response is not None
    assert "sever the umbilical cord of big ai" in response.text.lower()
    assert response.backend == "mock"
    
    # 4. Verify: Memory Persistence
    # Check if the session exists via the lifecycle manager
    active_sessions = await oracle.lifecycle.list_sessions_by_state(
        entity_name=entity_name, state=SessionState.ACTIVE
    )
    assert len(active_sessions) > 0
    
    # 5. Verify: Soul Distillation (M11)
    # The Oracle should have triggered a distillation check.
    # We check if a proposed_lessons.yaml exists for the entity.
    proposed_lessons_path = Path(f"data/entities/{entity_name}/proposed_lessons.yaml")
    # Note: Distillation might not happen on the very first turn depending on the threshold,
    # but we check if the system is wired.
    
    # To force distillation, we can simulate multiple turns
    for _ in range(10):
        await oracle.summon(entity_name, "Continue the conversation.")
        
    assert proposed_lessons_path.exists()
    content = proposed_lessons_path.read_text()
    assert "L1_narrative" in content or "proposals:" in content

