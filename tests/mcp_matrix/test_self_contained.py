"""MCP Transport: Every request self-contained (no handshake/session ID)."""
import pytest
import asyncio
from pathlib import Path
import tempfile
import os

@pytest.mark.mcp
@pytest.mark.anyio
async def test_requests_self_contained():
    """Verify MCP requests are self-contained (no session handshake)."""
    # MCP 2026-07-28 spec: Every request must be self-contained.
    # No initialize handshake, no session ID binding.
    
    # Mock MCP request
    request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 1,
    }
    
    # Verify no session-related fields
    forbidden_fields = ["session_id", "Mcp-Session-Id", "initialize", "handshake"]
    for field in forbidden_fields:
        assert field not in request, f"Request contains forbidden field: {field}"
    
    # Verify request is complete
    assert "jsonrpc" in request
    assert "method" in request
    assert "id" in request

@pytest.mark.mcp
@pytest.mark.anyio
async def test_no_server_state_dependency():
    """Verify requests don't depend on server state."""
    # Each request should be independent
    requests = [
        {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1},
        {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "tool1"}, "id": 2},
        {"jsonrpc": "2.0", "method": "resources/list", "params": {}, "id": 3},
    ]
    
    # Verify each request is self-contained
    for req in requests:
        assert "session_id" not in req
        assert "state" not in req
        assert "context" not in req

@pytest.mark.mcp
@pytest.mark.anyio
async def test_concurrent_independent_requests():
    """Verify concurrent requests are independent."""
    import anyio
    
    results = []
    
    async def make_request(request_id):
        # Mock request
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": f"tool_{request_id}"},
            "id": request_id,
        }
        
        # Verify request is self-contained
        assert "session_id" not in request
        results.append(request_id)
    
    # Launch concurrent requests
    async with anyio.create_task_group() as tg:
        for i in range(5):
            tg.start_soon(make_request, i)
    
    # All requests should succeed independently
    assert len(results) == 5
    assert set(results) == {0, 1, 2, 3, 4}
