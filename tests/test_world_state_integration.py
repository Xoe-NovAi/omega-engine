import pytest
import anyio
from src.omega.oracle.world_state import WorldState, WorldLump, world_state
from src.omega.oracle.context_builder import ContextBuilder
from unittest.mock import MagicMock, AsyncMock

@pytest.mark.anyio
async def test_world_state_injection():
    """
    Verify that WorldState data is correctly injected into the context block
    produced by ContextBuilder.
    """
    # 1. Setup WorldState with sample data
    ws = WorldState()
    # Clear existing state for isolation
    ws._sectors = {}
    ws._global_state = {}
    
    sector_id = "sector_01"
    lump_id = "lump_alpha"
    lump_data = {"description": "A glowing crystal", "energy": 100}
    lump = WorldLump(lump_id=lump_id, data=lump_data)
    
    await ws.load_lump(sector_id, lump)
    ws.set_global("world_time", "12:00")
    
    # 2. Mock MemoryStore to return no history (focus on world state)
    mock_memory_store = MagicMock()
    mock_memory_store.get_history = AsyncMock(return_value=[])
    
    # 3. Use ContextBuilder to build context
    builder = ContextBuilder(memory_store=mock_memory_store)
    context = await builder.build_context(
        entity_name="test_entity",
        session_id="test_session"
    )
    
    # 4. Assertions
    assert "## Active World State Context" in context
    assert "world_time: 12:00" in context
    assert f"Sector [{sector_id}]" in context
    assert f"Lump {lump_id}" in context
    assert "A glowing crystal" in context

@pytest.mark.anyio
async def test_world_state_empty():
    """
    Verify that ContextBuilder returns an empty string or just memory 
    when WorldState is empty.
    """
    ws = WorldState()
    ws._sectors = {}
    ws._global_state = {}
    
    mock_memory_store = MagicMock()
    mock_memory_store.get_history = AsyncMock(return_value=[
        {"timestamp": "2026-01-01T00:00:00", "user": "Hi", "assistant": "Hello"}
    ])
    
    builder = ContextBuilder(memory_store=mock_memory_store)
    context = await builder.build_context(
        entity_name="test_entity",
        session_id="test_session"
    )
    
    # Should not contain world state header if empty
    assert "## Active World State Context" not in context
    # Should still contain memory
    assert "User: Hi" in context
