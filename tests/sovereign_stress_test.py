import pytest
import anyio
import asyncio
import time
import os
from unittest.mock import AsyncMock, MagicMock, patch
from omega.oracle.model_gateway import ModelGateway
from omega.oracle.backends.remote_provider import RemoteProvider, ProviderConfig, ProviderHealth
from omega.oracle.providers import LocallmsterProvider, MockProvider
from omega.orchestration.triage_router import TriageRouter, TriageRequest, TaskRequest, EntityContext, Constraints, SessionContext
from pathlib import Path
import json

# --- Mock Provider for Hangs ---
class HangingProvider(LocallmsterProvider):
    async def generate(self, model, system, user, temp, max_tokens):
        await anyio.sleep(10) # Simulate a hang
        return "Should have timed out"

@pytest.mark.anyio
async def test_provider_fallback_gauntlet():
    """Scenario 1: Verify the fallback chain follows priority and handles failures."""
    gateway = ModelGateway()
    
    # Setup: P1 (Fail), P2 (Fail), P3 (Success)
    # Use MagicMock to track calls
    p1 = MagicMock(spec=RemoteProvider)
    p1.name = "p1"
    p1.config = ProviderConfig(name="p1", priority=1)
    p1.is_available = AsyncMock(return_value=True)
    p1.generate = AsyncMock(side_effect=Exception("P1 Failed"))
    
    p2 = MagicMock(spec=RemoteProvider)
    p2.name = "p2"
    p2.config = ProviderConfig(name="p2", priority=2)
    p2.is_available = AsyncMock(return_value=True)
    p2.generate = AsyncMock(side_effect=Exception("P2 Failed"))
    
    p3 = MagicMock(spec=RemoteProvider)
    p3.name = "p3"
    p3.config = ProviderConfig(name="p3", priority=3)
    p3.is_available = AsyncMock(return_value=True)
    p3.generate = AsyncMock(return_value="Success from P3")
    
    gateway.providers = [p1, p2, p3]
    
    with patch.dict(os.environ, {"OMEGA_ENV": "production"}):
        result = await gateway.generate("test-model", "sys", "query")
        assert result == "Success from P3"
        assert p1.generate.called
        assert p2.generate.called
        assert p3.generate.called

@pytest.mark.anyio
async def test_local_provider_hang_timeout():
    """Scenario 2: Verify that a hanging local provider is cut off by anyio.move_on_after."""
    gateway = ModelGateway()
    
    # Setup: P1 (Hangs), P2 (Success)
    p1 = HangingProvider("p1", {"priority": 1})
    p1.is_available = AsyncMock(return_value=True)
    
    p2 = MockProvider("p2", {"priority": 2})
    p2.is_available = AsyncMock(return_value=True)
    p2.generate = AsyncMock(return_value="Success from P2")
    
    gateway.providers = [p1, p2]
    
    with patch.dict(os.environ, {"OMEGA_ENV": "production"}):
        # We use a shorter timeout for the test by patching anyio.move_on_after 
        # or just accepting that it will take 130s. 
        # To make the test fast, we'll mock move_on_after to raise TimeoutError immediately.
        with patch("anyio.move_on_after", side_effect=lambda timeout: anyio.fail_after(0.1)):
            start = time.monotonic()
            result = await gateway.generate("test-model", "sys", "query")
            elapsed = time.monotonic() - start
            
            assert result == "Success from P2"
            assert elapsed < 2.0

@pytest.mark.anyio
async def test_resource_guard_concurrency():
    """Scenario 3: Verify ResourceGuard limits concurrency for local providers."""
    gateway = ModelGateway()
    
    class SlowLocalProvider(LocallmsterProvider):
        async def generate(self, model, system, user, temp, max_tokens):
            await anyio.sleep(0.5)
            return "Done"
            
    p1 = SlowLocalProvider("p1", {"priority": 1})
    p1.is_available = AsyncMock(return_value=True)
    gateway.providers = [p1]
    
    with patch.dict(os.environ, {"OMEGA_ENV": "production"}):
        results = []
        start = time.monotonic()
        async with anyio.create_task_group() as tg:
            async def call_and_append():
                res = await gateway.generate("m", "s", "q")
                results.append(res)
            
            tg.start_soon(call_and_append)
            tg.start_soon(call_and_append)
            tg.start_soon(call_and_append)
        elapsed = time.monotonic() - start
        
        assert len(results) == 3
        assert elapsed >= 1.4 

@pytest.mark.anyio
async def test_corrupted_soul_resilience():
    """Scenario 5: Verify TriageRouter handles corrupted soul files gracefully."""
    router = TriageRouter()
    
    soul_path = Path("tests/corrupted_soul.json")
    soul_path.write_text("{ invalid json ...")
    
    try:
        request = TriageRequest(
            task=TaskRequest(description="Hello"),
            entity=EntityContext(name="Test", soul_path=soul_path),
            constraints=Constraints(),
            session=SessionContext(id="1", trace_id="1")
        )
        
        response = await router.select_model(request)
        assert response.selected_model.name is not None
    finally:
        if soul_path.exists():
            soul_path.unlink()

@pytest.mark.anyio
async def test_anyio_blocking_scan():
    """Scenario 6: Basic check for AnyIO compliance in TriageRouter."""
    import inspect
    from omega.orchestration.triage_router import TriageRouter
    
    source = inspect.getsource(TriageRouter._load_soul)
    assert "anyio.to_thread.run_sync" in source
    assert "await" in source
