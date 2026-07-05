
import pytest
import anyio
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

from omega.oracle.oracle import Oracle, OracleResponse
from omega.oracle.entity_registry import EntityRegistry, Entity
from omega.oracle.model_gateway import ModelGateway
from omega.oracle.providers import MockProvider
from omega.memory_store import MemoryStore
from omega.oracle.soul_distiller import SoulDistillationPipeline
from omega.errors import OmegaError

# ── Test Configuration ─────────────────────────────────────────────────────

@pytest.fixture
def mock_env(tmp_path):
    """Set up a temporary environment for E2E testing."""
    # Create dummy WAD structure
    wad_dir = tmp_path / "config" / "wads" / "_omega_default"
    wad_dir.mkdir(parents=True)
    
    entities_yaml = wad_dir / "entities.yaml"
    entities_yaml.write_text("""
sysAdmin:
  name: "SysAdmin"
  personality: "The Infrastructure Keeper"
  model: "mock-model"
  slots: ["1"]
  domains: ["infrastructure", "deployment"]
  temperature: 0.7
""")
    
    return tmp_path

@pytest.fixture
async def e2e_oracle(mock_env):
    """Assemble a fully wired Oracle with mock backends."""
    # 1. Registry
    registry = EntityRegistry()
    # Manually inject the mock entity to avoid WAD loading issues in tests
    # The registry now stores layers (lists) for each entity key
    test_entity = Entity(
        name="SysAdmin",
        personality="The Infrastructure Keeper",
        model="mock-model",
        slots=["1"],
        domains=["infrastructure", "deployment"],
        temperature=0.7
    )
    registry._entities["sysadmin"] = [test_entity]
    
    # 2. Model Gateway with Mock Provider
    # We force the use of MockProvider
    gateway = ModelGateway()
    # Override the provider fabric to use MockProvider for everything
    gateway._providers = {"mock": MockProvider("mock", {})}
    
    # 3. Memory Store (InMemory)
    # We use the singleton but ensure it's clean
    memory = MemoryStore()
    
    # 4. Soul Distiller
    distiller = SoulDistillationPipeline()
    
    # 5. Oracle
    oracle = Oracle(registry=registry, model_gateway=gateway)
    oracle.memory_store = memory
    oracle.distiller = distiller
    
    return oracle

@pytest.mark.anyio
async def test_full_inference_chain_success(e2e_oracle):
    """
    Verify the complete loop: 
    Query -> Router -> ModelGateway -> Response -> MemoryStore -> SoulDistiller
    """
    query = "How do I deploy the engine?"
    entity_name = "sysadmin"
    
    # 1. Execute turn
    # We use summon to bypass Iris and go straight to the entity
    response = await e2e_oracle.summon(entity_name, query)
    
    # Assert Response
    assert isinstance(response, OracleResponse)
    assert response.entity == "SysAdmin"
    assert response.text is not None
    assert response.trace_id is not None
    
    # 2. Verify Memory Recording
    # Get the session ID from the response
    session_id = response.session_id
    assert session_id is not None
    
    # Check if the exchange was recorded in MemoryStore
    history = await e2e_oracle.memory_store.get_history(entity_name, session_id, limit=10)
    assert len(history) == 1
    assert history[0]["user"] == query
    assert history[0]["assistant"] == response.text
    
    # Build transcript for distillation
    lines = []
    for ex in history:
        user_msg = ex.get("user", "")
        asst_msg = ex.get("assistant", "")
        if user_msg:
            lines.append(f"[user]: {user_msg}")
        if asst_msg:
            lines.append(f"[assistant]: {asst_msg}")
    transcript = "\n".join(lines)
    
    # 3. Verify Soul Distillation
    # Trigger session close
    result = await e2e_oracle.distiller.run(
        session_transcript=transcript,
        entity_name=entity_name,
        source_trace_id=session_id
    )
    assert result is not None
    assert "L1" in result
    assert "L2" in result
    assert "L3" in result

@pytest.mark.anyio
async def test_inference_chain_with_provider_failure(e2e_oracle):
    """
    Verify that a provider failure is caught by the new (OmegaError, RuntimeError, OSError) 
    tuple and doesn't crash the Oracle.
    """
    # Force the mock provider to raise a RuntimeError
    with patch.object(MockProvider, 'generate', side_effect=RuntimeError("C-level crash")):
        query = "This should fail"
        
        # The Oracle should handle the RuntimeError and return a fallback or error response
        # instead of crashing the entire process.
        try:
            response = await e2e_oracle.summon("sysadmin", query)
            # If it didn't crash, it's a success for the Mandate 9 refactor
            assert response is not None
        except RuntimeError:
            pytest.fail("Oracle allowed RuntimeError to propagate, violating Mandate 9")

@pytest.mark.anyio
async def test_inference_chain_with_omega_error(e2e_oracle):
    """Verify that OmegaError is propagated correctly (as it is a typed error)."""
    with patch.object(MockProvider, 'generate', side_effect=OmegaError("Sovereign Violation")):
        query = "This should raise OmegaError"
        
        with pytest.raises(OmegaError):
            await e2e_oracle.summon("sysadmin", query)
