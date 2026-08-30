# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
MCP 2026-07-28 Compliance Test Suite
AP: AP-MCP-TEST-v1.0.0
M13: Temple-Grade — spec compliance
M21: Gate Integrity — type-checked results

Tests for the MCP compliance middleware, client, and runtime.
All tests are self-contained (no running server required).
"""
# [heritage: pytest 2024] Testing framework
# [heritage: httpx 2023] HTTP client mocking

import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import anyio
import pytest
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.routing import Route

from src.omega.mcp_core.compliance import (
    PROTOCOL_VERSION_CURRENT,
    SUPPORTED_PROTOCOL_VERSIONS,
    ERROR_CODES,
    TraceContextMiddleware,
    MCPHeaderValidationMiddleware,
    MCPMetaEnvelopeMiddleware,
    RequestIDMiddleware,
    RateLimitHeadersMiddleware,
    ServerDiscoverHandler,
    ProtectedResourceMetadataHandler,
    add_cache_metadata,
    extract_mcp_param_headers,
    InputRequiredResult,
    SubscriptionManager,
)
import httpx
from src.omega.mcp_core.client import MCPClient, MCPClientResult


# =============================================================================
# TEST 1: Request ID Middleware — generates UUID if missing
# =============================================================================

@pytest.mark.asyncio
async def test_request_id_middleware_generates_uuid():
    """RequestIDMiddleware generates UUID when client doesn't provide one."""

    async def ok_endpoint(request: Request):
        request_id = getattr(request.state, "request_id", None)
        assert request_id is not None, "request_id should be set"
        # Verify it's a valid UUID
        uuid.UUID(request_id)
        return JSONResponse({"ok": True})

    app = Starlette(
        routes=[Route("/test", endpoint=ok_endpoint)],
        middleware=[Middleware(RequestIDMiddleware)],
    )

    # Simulate a request without X-Request-Id
    from httpx import AsyncClient, ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/test")

    assert resp.status_code == 200
    # Verify response has X-Request-Id header
    assert "x-request-id" in resp.headers
    # Verify it's a valid UUID
    uuid.UUID(resp.headers["x-request-id"])


# =============================================================================
# TEST 2: Request ID Middleware — preserves client-provided ID
# =============================================================================

@pytest.mark.asyncio
async def test_request_id_middleware_preserves_client_id():
    """RequestIDMiddleware preserves client-provided X-Request-Id."""

    async def ok_endpoint(request: Request):
        request_id = getattr(request.state, "request_id", None)
        assert request_id == "my-custom-id"
        return JSONResponse({"ok": True})

    app = Starlette(
        routes=[Route("/test", endpoint=ok_endpoint)],
        middleware=[Middleware(RequestIDMiddleware)],
    )

    from httpx import AsyncClient, ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/test", headers={"X-Request-Id": "my-custom-id"})

    assert resp.status_code == 200
    assert resp.headers["x-request-id"] == "my-custom-id"


# =============================================================================
# TEST 3: Rate-Limit Headers Middleware — adds expected headers
# =============================================================================

@pytest.mark.asyncio
async def test_rate_limit_headers_middleware():
    """RateLimitHeadersMiddleware adds X-RateLimit-* headers."""

    async def ok_endpoint(request: Request):
        return JSONResponse({"ok": True})

    app = Starlette(
        routes=[Route("/test", endpoint=ok_endpoint)],
        middleware=[Middleware(RateLimitHeadersMiddleware, limit=50, window_seconds=30)],
    )

    from httpx import AsyncClient, ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/test")

    assert resp.status_code == 200
    assert resp.headers["x-ratelimit-limit"] == "50"
    assert resp.headers["x-ratelimit-remaining"] == "50"
    assert "x-ratelimit-reset" in resp.headers


# =============================================================================
# TEST 4: Header Validation — rejects missing Mcp-Protocol-Version
# =============================================================================

@pytest.mark.asyncio
async def test_header_validation_missing_protocol():
    """MCPHeaderValidationMiddleware rejects POST requests missing ALL required headers."""

    async def ok_endpoint(request: Request):
        return JSONResponse({"ok": True})

    app = Starlette(
        routes=[Route("/mcp/test", endpoint=ok_endpoint)],
        middleware=[Middleware(MCPHeaderValidationMiddleware)],
    )

    from httpx import AsyncClient, ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/mcp/test", json={"method": "test"})

    assert resp.status_code == 400
    data = resp.json()
    assert data["error"]["code"] == ERROR_CODES["INVALID_REQUEST"]
    # POST requires mcp-method, mcp-name, mcp-protocol-version
    assert "mcp-protocol-version" in data["error"]["message"].lower()


# =============================================================================
# TEST 5: Header Validation — rejects unsupported protocol version
# =============================================================================

@pytest.mark.asyncio
async def test_header_validation_unsupported_version():
    """MCPHeaderValidationMiddleware rejects unsupported protocol versions."""

    async def ok_endpoint(request: Request):
        return JSONResponse({"ok": True})

    app = Starlette(
        routes=[Route("/mcp/test", endpoint=ok_endpoint)],
        middleware=[Middleware(MCPHeaderValidationMiddleware)],
    )

    from httpx import AsyncClient, ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/mcp/test",
            json={"method": "test"},
            headers={
                "Mcp-Protocol-Version": "2024-01-01",
                "Mcp-Method": "test",
                "Mcp-Name": "test",
            },
        )

    assert resp.status_code == 400
    data = resp.json()
    # With all required headers present, unsupported version returns -32600 (INVALID_REQUEST)
    # since the validation uses HEADER_MISMATCH by default for protocol version
    assert data["error"]["code"] in (ERROR_CODES["INVALID_REQUEST"], ERROR_CODES["PROTOCOL_VERSION_MISMATCH"])


# =============================================================================
# TEST 6: Server/Discover — returns correct capabilities
# =============================================================================

@pytest.mark.asyncio
async def test_server_discover_handler():
    """ServerDiscoverHandler returns capabilities and metadata."""

    handler = ServerDiscoverHandler(
        server_name="test-server",
        server_version="2.0.0",
    )

    request = {"id": "req-1"}
    response = await handler.handle(request)

    assert response["jsonrpc"] == "2.0"
    assert response["id"] == "req-1"
    assert "result" in response
    result = response["result"]
    assert "2026-07-28" in result["protocolVersions"]
    assert result["serverInfo"]["name"] == "test-server"
    assert result["serverInfo"]["version"] == "2.0.0"
    assert "tools" in result["capabilities"]
    assert "resources" in result["capabilities"]
    assert "prompts" in result["capabilities"]
    # _meta envelope (SEP-2549)
    assert "_meta" in response
    assert response["_meta"]["ttlMs"] == 3600000


# =============================================================================
# TEST 7: Protected Resource Metadata (RFC 9728)
# =============================================================================

@pytest.mark.asyncio
async def test_protected_resource_metadata():
    """ProtectedResourceMetadataHandler returns RFC 9728 metadata."""

    from starlette.requests import Request as StarletteRequest
    from unittest.mock import MagicMock

    handler = ProtectedResourceMetadataHandler(
        resource_url="https://test.local/mcp",
        auth_server_url="https://test.local/oauth",
        scopes=["mcp:tools", "mcp:resources"],
    )

    # Create minimal request object
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/.well-known/oauth-protected-resource",
        "headers": [],
    }
    request = StarletteRequest(scope)

    response = await handler.handle(request)

    assert response.status_code == 200
    data = json.loads(response.body)
    assert data["resource"] == "https://test.local/mcp"
    assert data["authorization_servers"] == ["https://test.local/oauth"]
    assert "mcp:tools" in data["scopes_supported"]


# =============================================================================
# TEST 8: MCP Client — call_tool returns MCPClientResult (M21 Gate)
# =============================================================================

@pytest.mark.asyncio
async def test_mcp_client_call_tool_returns_mcpclientresult():
    """M21 Contract Test: MCPClient.call_tool returns MCPClientResult."""

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"x-request-id": "test-rid", "content-type": "application/json"}
    mock_resp.json.return_value = {
        "jsonrpc": "2.0",
        "id": "test-1",
        "result": {
            "content": [{"text": "Hello from mock"}],
            "isError": False,
        },
    }

    async with MCPClient("http://test-server", timeout=10, provider_name="test-provider") as client:
        with patch.object(client._http_client, "post", AsyncMock(return_value=mock_resp)):
            result = await client.call_tool("hello", {"name": "world"})

    # M21 Gate: Type check
    assert isinstance(result, MCPClientResult)
    # M22 Gate: Provenance
    assert result.provider_name == "test-provider"
    assert result.success is True
    assert result.content == ["Hello from mock"]
    assert result.is_error is False
    # request_id is the UUID generated by the client, not the response header
    assert isinstance(result.request_id, str) and len(result.request_id) > 0
    # response_headers should contain what the mock returned
    assert result.response_headers.get("x-request-id") == "test-rid"


# =============================================================================
# TEST 9: MCP Client — timeout returns error result (M23)
# =============================================================================

@pytest.mark.asyncio
async def test_mcp_client_timeout_returns_error():
    """M23 Failure Integrity: timeout returns MCPClientResult with is_error=True."""

    async with MCPClient("http://slow-server", timeout=0.001) as client:
        with patch.object(client._http_client, "post", AsyncMock(side_effect=httpx.TimeoutException("Request timed out"))):
            result = await client.call_tool("slow_tool", {})

    assert isinstance(result, MCPClientResult)
    assert result.is_error is True
    assert result.success is False
    assert "timed out" in result.content[0].lower() or "timeout" in result.content[0].lower()


# =============================================================================
# TEST 10: MCP Param Headers Extraction (SEP-2243)
# =============================================================================

def test_extract_mcp_param_headers():
    """extract_mcp_param_headers correctly extracts Mcp-Param-* headers."""

    from starlette.requests import Request as StarletteRequest

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/mcp/test",
        "headers": [
            (b"mcp-param-tool-name", b"my_tool"),
            (b"mcp-param-timeout", b"30"),
            (b"content-type", b"application/json"),
        ],
    }
    request = StarletteRequest(scope)

    params = extract_mcp_param_headers(request)
    assert params["tool-name"] == "my_tool"
    assert params["timeout"] == "30"
    assert "content-type" not in params


# =============================================================================
# TEST 11: InputRequiredResult (SEP-2322)
# =============================================================================

def test_input_required_result():
    """InputRequiredResult returns correct structure per SEP-2322."""

    result = InputRequiredResult(
        request_id="req-123",
        prompt="Enter your API key",
        schema={"type": "string", "description": "Your API key"},
    )

    data = result.to_result()
    assert data["type"] == "input_required"
    assert data["requestId"] == "req-123"
    assert data["prompt"] == "Enter your API key"
    assert data["schema"]["type"] == "string"


# =============================================================================
# TEST 12: Subscription Manager — subscribe/notify/unsubscribe
# =============================================================================

@pytest.mark.asyncio
async def test_subscription_manager():
    """SubscriptionManager correctly manages subscriptions and notifications."""

    mgr = SubscriptionManager()
    send_stream_1 = AsyncMock()
    send_stream_2 = AsyncMock()

    # Subscribe
    await mgr.subscribe("tools", send_stream_1)
    await mgr.subscribe("tools", send_stream_2)

    # Notify
    notification = {"type": "tools/listChanged"}
    await mgr.notify("tools", notification)

    send_stream_1.send.assert_called_once_with(notification)
    send_stream_2.send.assert_called_once_with(notification)

    # Reset both to clear first notification
    send_stream_1.reset_mock()
    send_stream_2.reset_mock()

    # Unsubscribe
    await mgr.unsubscribe("tools", send_stream_1)

    notification2 = {"type": "tools/listChanged"}
    await mgr.notify("tools", notification2)

    # After unsubscribe, only stream 2 should receive
    send_stream_1.send.assert_not_called()
    send_stream_2.send.assert_called_once_with(notification2)
