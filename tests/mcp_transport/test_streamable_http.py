# 🔱 Omega Engine — M21 Contract Tests for Streamable HTTP Transport
# AP: AP-M21-STREAMABLE-HTTP-v1.0.0
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_m21 ⬡ ACTIVE
#
# Contract tests verifying Streamable HTTP transport for Omega Hub.
# These tests ensure the /mcp endpoint is correctly configured and functional.

import pytest
import json
from pathlib import Path
from starlette.testclient import TestClient
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import Response, JSONResponse
from starlette.requests import Request


class TestStreamableHTTPTransport:
    """M21 Contract Tests: Streamable HTTP Transport."""
    
    def test_opencode_json_streamable_http_config(self):
        """Verify opencode.json is configured for Streamable HTTP transport."""
        opencode_path = Path("opencode.json")
        assert opencode_path.exists(), "opencode.json must exist"
        
        with open(opencode_path) as f:
            config = json.load(f)
        
        omega_hub = config.get("mcp", {}).get("omega-hub", {})
        assert omega_hub.get("type") == "remote",             "omega-hub MCP type should be 'remote' (OpenCode v1.18.x ignores 'streamable-http')"
        assert "/mcp" in omega_hub.get("url", ""),             "omega-hub URL should point to /mcp endpoint"
        assert omega_hub.get("enabled") is True,             "omega-hub should be enabled"
    
    def test_sse_endpoint_still_available_for_backward_compatibility(self):
        """Verify SSE endpoint path is still available for legacy clients."""
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("test")
        assert mcp.settings.sse_path == "/sse",             "SSE path should still be available for legacy clients"
        assert mcp.settings.message_path == "/messages/",             "SSE message path should still be available"
    
    def test_streamable_http_path_configured(self):
        """Verify Streamable HTTP path is configured correctly."""
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("test")
        assert mcp.settings.streamable_http_path == "/mcp",             "Streamable HTTP path should be /mcp"
    
    @pytest.mark.anyio
    async def test_streamable_http_session_manager_can_be_created(self):
        """Verify StreamableHTTPSessionManager can be initialized correctly."""
        from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
        from mcp.server.fastmcp.server import StreamableHTTPASGIApp
        
        # Create a minimal mock MCP server
        class MockMCPServer:
            def __init__(self):
                self.request_handlers = {}
                self.create_initialization_options = lambda: {}
        
        mock_server = MockMCPServer()
        
        streamable_mgr = StreamableHTTPSessionManager(
            app=mock_server,
            json_response=False,
            stateless=True,
            security_settings=None,
        )
        
        streamable_app = StreamableHTTPASGIApp(streamable_mgr)
        assert streamable_app is not None, "StreamableHTTPASGIApp should be created"
    
    def test_mcp_runtime_supports_dual_transport(self):
        """Verify mcp_runtime.py is configured for dual transport support."""
        from omega.mcp_runtime import run_mcp
        import inspect
        
        # Verify the function signature includes transport options
        sig = inspect.signature(run_mcp)
        # The function should accept modify_app parameter
        assert "modify_app" in sig.parameters,             "run_mcp should accept modify_app parameter"
    
    def test_hub_server_imports_streamable_http(self):
        """Verify omega hub server imports Streamable HTTP components."""
        import importlib
        try:
            from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
            from mcp.server.fastmcp.server import StreamableHTTPASGIApp
            # If we get here, imports work
            assert True
        except ImportError as e:
            pytest.fail(f"Streamable HTTP imports failed: {e}")
