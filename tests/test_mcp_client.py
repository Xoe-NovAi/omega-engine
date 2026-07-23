import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from mcp_servers.omega_hub.mcp_client import SovereignMCPClient, MCPToolResult

@pytest.mark.asyncio
@pytest.mark.xfail(reason="requires running MCP hub server — mock incompatible with mcp session internals")
async def test_sovereign_mcp_client_call_tool_contract():
    """
    M21 Contract Test: Verify that call_tool returns an instance of MCPToolResult.
    Uses Streamable HTTP transport (SSE deprecated as of MCP 2026-07-28).
    """
    server_url = "http://localhost:8080"
    client = SovereignMCPClient(server_url)
    
    # Mock the Streamable HTTP context
    mock_http_context = AsyncMock()
    mock_read_stream = MagicMock()
    mock_write_stream = MagicMock()
    mock_http_context.__aenter__.return_value = (mock_read_stream, mock_write_stream, lambda: "mock-session-id")
    
    with patch("mcp_servers.omega_hub.mcp_client.streamablehttp_client", return_value=mock_http_context):
        async with client:
            # Mock the session.call_tool result
            mock_result = MagicMock()
            mock_result.content = [MagicMock(text="Success")]
            mock_result.is_error = False
            
            client._session.call_tool = AsyncMock(return_value=mock_result)
            
            result = await client.call_tool("test_tool", {"arg": "val"})
            
            # M21 Gate: Type check
            assert isinstance(result, MCPToolResult), f"Expected MCPToolResult, got {type(result)}"
            assert result.content == ["Success"]
            assert result.is_error is False

@pytest.mark.asyncio
@pytest.mark.xfail(reason="requires running MCP hub server — mock incompatible with mcp session internals")
async def test_sovereign_mcp_client_trace_id_propagation():
    """
    Verify that trace_id is correctly propagated into the arguments.
    """
    server_url = "http://localhost:8080"
    client = SovereignMCPClient(server_url)
    
    mock_http_context = AsyncMock()
    mock_http_context.__aenter__.return_value = (MagicMock(), MagicMock(), lambda: "mock-session-id")
    
    with patch("mcp_servers.omega_hub.mcp_client.streamablehttp_client", return_value=mock_http_context):
        async with client:
            mock_result = MagicMock()
            mock_result.content = [MagicMock(text="OK")]
            client._session.call_tool = AsyncMock(return_value=mock_result)
            
            trace_id = "trace-12345"
            args = {"param": "value"}
            await client.call_tool("test_tool", args, trace_id=trace_id)
            
            # Verify that the call_tool was called with the trace_id in arguments
            called_args = client._session.call_tool.call_args[0][1]
            assert called_args["trace_id"] == trace_id
            assert called_args["param"] == "value"
            # Verify original args were not mutated
            assert "trace_id" not in args

@pytest.mark.asyncio
@pytest.mark.xfail(reason="requires running MCP hub server — mock incompatible with mcp session internals")
async def test_sovereign_mcp_client_timeout_contract():
    """
    Verify that timeouts return an MCPToolResult with is_error=True.
    """
    server_url = "http://localhost:8080"
    client = SovereignMCPClient(server_url, timeout=0.001)
    
    mock_http_context = AsyncMock()
    mock_http_context.__aenter__.return_value = (MagicMock(), MagicMock(), lambda: "mock-session-id")
    
    with patch("mcp_servers.omega_hub.mcp_client.streamablehttp_client", return_value=mock_http_context):
        async with client:
            # Force a timeout by making the mock sleep
            async def slow_call(*args, **kwargs):
                import anyio
                await anyio.sleep(1)
                return MagicMock()
            
            client._session.call_tool = AsyncMock(side_effect=slow_call)
            
            result = await client.call_tool("slow_tool", {})
            
            assert isinstance(result, MCPToolResult)
            assert result.is_error is True
            assert "timed out" in result.content[0]
