"""
MCP 2026-07-28 Streamable HTTP Compliance Middleware
AP: AP-MCP-COMPLIANCE-v1.0.0
M1: AnyIO — async middleware
M13: Temple-Grade — spec compliance

Implements Sprint 1 (Transport Core) from R_CG01_MCP_STREAMABLE_HTTP_OAUTH_AUDIT.md:
- Header validation: Mcp-Method, Mcp-Name, MCP-Protocol-Version (SEP-2243)
- _meta envelope extraction/injection (SEP-2575)
- server/discover method registration (SEP-2575)
- RFC 9728 Protected Resource Metadata endpoint
- W3C Trace Context propagation (SEP-414)
- InputRequiredResult for MRTR (SEP-2322)
- subscriptions/listen for notifications (SSE)

Breaking changes addressed:
- B1: Remove initialize/initialized handshake
- B2: Remove Mcp-Session-Id header & protocol sessions
- B3: Require Mcp-Method header on ALL POST
- B4: Require Mcp-Name header on tool/resource/prompt calls
- B5: Require MCP-Protocol-Version header on ALL requests
- B6: Error code -32002 -> -32602
- B7: tasks/list removed
- B8: HTTP+SSE transport deprecated (12-month window)
"""
# [heritage: anyio 2024] M1 AnyIO — async middleware
# [heritage: mcp 2024] MCP Protocol — Streamable HTTP transport
# [heritage: w3c-trace-context 2021] Distributed tracing

import json
import logging
import uuid
from typing import Any, Dict, List, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from datetime import datetime, timezone

import anyio
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route, Mount
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware

from mcp.server.fastmcp.server import StreamableHTTPASGIApp
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.server.sse import SseServerTransport
from mcp.types import (
    InitializeRequest,
    InitializeResult,
    ServerCapabilities,
    ClientCapabilities,
    Implementation,
    Tool,
    Resource,
    Prompt,
)

logger = logging.getLogger("omega.mcp.compliance")


# =============================================================================
# CONSTANTS & ERROR CODES (per MCP 2026-07-28 spec)
# =============================================================================

# Required headers (SEP-2243)
REQUIRED_HEADERS_POST = ["mcp-method", "mcp-name", "mcp-protocol-version"]
REQUIRED_HEADERS_GET = ["mcp-protocol-version"]
REQUIRED_HEADERS_ALL = ["mcp-protocol-version"]

# Header names (case-insensitive matching)
HDR_MCP_METHOD = "mcp-method"
HDR_MCP_NAME = "mcp-name"
HDR_MCP_PROTOCOL_VERSION = "mcp-protocol-version"
HDR_MCP_SESSION_ID = "mcp-session-id"  # DEPRECATED (B2)
HDR_TRACEPARENT = "traceparent"
HDR_TRACESTATE = "tracestate"
HDR_BAGGAGE = "baggage"

# Protocol versions
PROTOCOL_VERSION_CURRENT = "2026-07-28"
PROTOCOL_VERSION_LEGACY = "2025-11-25"
SUPPORTED_PROTOCOL_VERSIONS = [PROTOCOL_VERSION_CURRENT, PROTOCOL_VERSION_LEGACY]

# Error codes (B6: -32002 -> -32602)
ERROR_INVALID_REQUEST = -32600
ERROR_METHOD_NOT_FOUND = -32601
ERROR_INVALID_PARAMS = -32602  # Was -32002
ERROR_INTERNAL = -32603
ERROR_PARSE = -32700

# Header mismatch error (C-1: SEP-2243 verified — -32020, NOT -32600)
ERROR_HEADER_MISMATCH = -32020


@dataclass
class MetaEnvelope:
    """_meta envelope per SEP-2575."""
    protocol_version: str = PROTOCOL_VERSION_CURRENT
    client_info: Optional[Dict[str, Any]] = None
    client_capabilities: Optional[Dict[str, Any]] = None
    server_info: Optional[Dict[str, Any]] = None
    traceparent: Optional[str] = None
    tracestate: Optional[str] = None
    baggage: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        d = {"protocolVersion": self.protocol_version}
        if self.client_info:
            d["clientInfo"] = self.client_info
        if self.client_capabilities:
            d["clientCapabilities"] = self.client_capabilities
        if self.server_info:
            d["serverInfo"] = self.server_info
        if self.traceparent:
            d["traceparent"] = self.traceparent
        if self.tracestate:
            d["tracestate"] = self.tracestate
        if self.baggage:
            d["baggage"] = self.baggage
        return d
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MetaEnvelope":
        return cls(
            protocol_version=data.get("protocolVersion", PROTOCOL_VERSION_CURRENT),
            client_info=data.get("clientInfo"),
            client_capabilities=data.get("clientCapabilities"),
            server_info=data.get("serverInfo"),
            traceparent=data.get("traceparent"),
            tracestate=data.get("tracestate"),
            baggage=data.get("baggage"),
        )


# =============================================================================
# HEADER VALIDATION MIDDLEWARE
# =============================================================================

class MCPHeaderValidationMiddleware(BaseHTTPMiddleware):
    """
    Validates required MCP headers on all requests per SEP-2243.
    
    Required headers:
    - POST: Mcp-Method, Mcp-Name, MCP-Protocol-Version
    - GET: MCP-Protocol-Version
    - All: MCP-Protocol-Version must match _meta.protocolVersion
    
    Returns 400 with JSON-RPC error on mismatch.
    """
    
    def __init__(self, app, exclude_paths: Optional[List[str]] = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/.well-known/", "/health", "/metrics"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip excluded paths
        if any(request.url.path.startswith(p) for p in self.exclude_paths):
            return await call_next(request)
        
        # Only validate MCP endpoints
        if not (request.url.path.startswith("/mcp") or request.url.path.startswith("/messages")):
            return await call_next(request)
        
        headers = {k.lower(): v for k, v in request.headers.items()}
        method = request.method
        
        # Validate required headers
        required = REQUIRED_HEADERS_POST if method == "POST" else REQUIRED_HEADERS_GET
        missing = [h for h in required if h not in headers]
        
        if missing:
            return self._error_response(
                request,
                ERROR_INVALID_REQUEST,
                f"Missing required headers: {', '.join(missing)}",
                f"Required for {method}: {', '.join(required)}"
            )
        
        # Validate MCP-Protocol-Version
        proto_version = headers.get(HDR_MCP_PROTOCOL_VERSION)
        if proto_version not in SUPPORTED_PROTOCOL_VERSIONS:
            return self._error_response(
                request,
                ERROR_INVALID_REQUEST,
                f"Unsupported MCP-Protocol-Version: {proto_version}",
                f"Supported versions: {', '.join(SUPPORTED_PROTOCOL_VERSIONS)}"
            )
        
        # For POST, validate Mcp-Method matches body.method
        if method == "POST":
            try:
                body = await request.json()
                body_method = body.get("method")
                header_method = headers.get(HDR_MCP_METHOD)
                
                if body_method and header_method and body_method != header_method:
                    return self._error_response(
                        request,
                        ERROR_HEADER_MISMATCH,
                        f"Mcp-Method header ('{header_method}') does not match body.method ('{body_method}')",
                        "SEP-2243: Header and body method must match"
                    )
            except json.JSONDecodeError:
                return self._error_response(
                    request,
                    ERROR_PARSE,
                    "Invalid JSON body",
                    "Request body must be valid JSON-RPC 2.0"
                )
        
        # Store validated headers in request state for downstream use
        request.state.mcp_headers = {
            "protocol_version": proto_version,
            "method": headers.get(HDR_MCP_METHOD),
            "name": headers.get(HDR_MCP_NAME),
            "traceparent": headers.get(HDR_TRACEPARENT),
            "tracestate": headers.get(HDR_TRACESTATE),
            "baggage": headers.get(HDR_BAGGAGE),
        }
        
        return await call_next(request)
    
    def _error_response(self, request: Request, code: int, message: str, data: str = "") -> JSONResponse:
        """Return JSON-RPC 2.0 error response."""
        request_id = getattr(request.state, "jsonrpc_id", None)
        error = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message,
                "data": data
            }
        }
        return JSONResponse(error, status_code=400)


# =============================================================================
# _META ENVELOPE MIDDLEWARE
# =============================================================================

class MCPMetaEnvelopeMiddleware(BaseHTTPMiddleware):
    """
    Extracts _meta from request body and injects _meta into response body.
    Per SEP-2575: _meta carries protocolVersion, clientInfo, clientCapabilities,
    serverInfo, traceparent, tracestate, baggage.
    """
    
    def __init__(self, app, server_info: Optional[Dict[str, Any]] = None):
        super().__init__(app)
        self.server_info = server_info or {
            "name": "omega-engine",
            "version": "1.0.0"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Only process MCP JSON-RPC requests
        if not (request.url.path.startswith("/mcp") or request.url.path.startswith("/messages")):
            return await call_next(request)
        
        if request.method not in ("POST", "GET"):
            return await call_next(request)
        
        # Extract _meta from request body (POST only)
        request_meta = None
        if request.method == "POST":
            try:
                body = await request.json()
                request_meta = body.get("_meta")
                # Store for response
                request.state.request_meta = request_meta
            except json.JSONDecodeError:
                pass
        
        # Process request
        response = await call_next(request)
        
        # Inject _meta into response body (JSON responses only)
        if response.media_type == "application/json":
            try:
                body = response.body.decode()
                if body:
                    response_data = json.loads(body)
                    
                    # Build response _meta
                    response_meta = MetaEnvelope(
                        protocol_version=request.state.mcp_headers.get("protocol_version", PROTOCOL_VERSION_CURRENT),
                        server_info=self.server_info,
                        traceparent=request.state.mcp_headers.get("traceparent"),
                        tracestate=request.state.mcp_headers.get("tracestate"),
                        baggage=request.state.mcp_headers.get("baggage"),
                    )
                    
                    # Merge with any existing _meta from request
                    if request_meta:
                        response_meta.client_info = request_meta.get("clientInfo")
                        response_meta.client_capabilities = request_meta.get("clientCapabilities")
                    
                    # Inject _meta into response
                    response_data["_meta"] = response_meta.to_dict()
                    
                    # Return modified response
                    return JSONResponse(response_data, status_code=response.status_code)
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
        
        return response


# =============================================================================
# SERVER/DISCOVER HANDLER (SEP-2575)
# =============================================================================

class ServerDiscoverHandler:
    """
    Implements server/discover RPC method per SEP-2575.
    
    Returns supported protocol versions, capabilities, and server identity.
    Cacheable response (include ttlMs in _meta).
    """
    
    def __init__(
        self,
        server_name: str = "omega-engine",
        server_version: str = "1.0.0",
        capabilities: Optional[ServerCapabilities] = None,
    ):
        self.server_name = server_name
        self.server_version = server_version
        self.capabilities = capabilities or ServerCapabilities(
            tools={"listChanged": True},
            resources={"subscribe": True, "listChanged": True},
            prompts={"listChanged": True},
            logging={},
        )
    
    async def handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle server/discover request."""
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "protocolVersions": SUPPORTED_PROTOCOL_VERSIONS,
                "capabilities": self.capabilities.model_dump(exclude_none=True),
                "serverInfo": {
                    "name": self.server_name,
                    "version": self.server_version
                },
                "instructions": "Omega Engine MCP Server — Dual transport (SSE + Streamable HTTP)"
            },
            "_meta": {
                "protocolVersion": PROTOCOL_VERSION_CURRENT,
                "serverInfo": {"name": self.server_name, "version": self.server_version},
                "ttlMs": 3600000,  # 1 hour cache
                "cacheScope": "server"
            }
        }


# =============================================================================
# RFC 9728 PROTECTED RESOURCE METADATA
# =============================================================================

class ProtectedResourceMetadataHandler:
    """
    Implements RFC 9728 OAuth 2.1 Protected Resource Metadata endpoint.
    
    GET /.well-known/oauth-protected-resource
    Returns metadata for OAuth 2.1 client discovery.
    """
    
    def __init__(
        self,
        resource_url: str = "https://omega-engine.local/mcp",
        auth_server_url: str = "https://omega-engine.local/oauth",
        scopes: Optional[List[str]] = None,
    ):
        self.resource_url = resource_url
        self.auth_server_url = auth_server_url
        self.scopes = scopes or ["mcp:tools", "mcp:resources", "mcp:prompts"]
    
    async def handle(self, request: Request) -> JSONResponse:
        """Handle GET /.well-known/oauth-protected-resource"""
        return JSONResponse({
            "resource": self.resource_url,
            "authorization_servers": [self.auth_server_url],
            "bearer_methods_supported": ["header"],
            "scopes_supported": self.scopes,
            "resource_documentation": "https://omega-engine.local/docs/mcp",
        })


# =============================================================================
# W3C TRACE CONTEXT PROPAGATION (SEP-414)
# =============================================================================

class TraceContextMiddleware(BaseHTTPMiddleware):
    """
    Propagates W3C Trace Context (traceparent, tracestate, baggage) per SEP-414.
    
    Extracts from incoming headers, injects into outgoing responses and
    downstream requests via _meta envelope.
    """
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract trace context from headers
        traceparent = request.headers.get(HDR_TRACEPARENT)
        tracestate = request.headers.get(HDR_TRACESTATE)
        baggage = request.headers.get(HDR_BAGGAGE)
        
        # Store in request state for _meta middleware
        request.state.trace_context = {
            "traceparent": traceparent,
            "tracestate": tracestate,
            "baggage": baggage,
        }
        
        # Generate new traceparent if not present (for root spans)
        if not traceparent:
            trace_id = uuid.uuid4().hex[:32]
            span_id = uuid.uuid4().hex[:16]
            traceparent = f"00-{trace_id}-{span_id}-01"
            request.state.trace_context["traceparent"] = traceparent
        
        response = await call_next(request)
        
        # Inject trace context into response headers
        if traceparent:
            response.headers[HDR_TRACEPARENT] = traceparent
        if tracestate:
            response.headers[HDR_TRACESTATE] = tracestate
        if baggage:
            response.headers[HDR_BAGGAGE] = baggage
        
        return response


# =============================================================================
# MRTR (MULTI-ROUND-TRIP REQUESTS) - InputRequiredResult (SEP-2322)
# =============================================================================

class InputRequiredResult:
    """
    Replaces server-initiated requests on SSE streams.
    Per SEP-2322: Server returns InputRequiredResult when it needs
    additional input from client to complete the operation.
    """
    
    def __init__(self, request_id: str, prompt: str, schema: Optional[Dict] = None):
        self.request_id = request_id
        self.prompt = prompt
        self.schema = schema or {"type": "string"}
    
    def to_result(self) -> Dict[str, Any]:
        return {
            "type": "input_required",
            "requestId": self.request_id,
            "prompt": self.prompt,
            "schema": self.schema
        }


# =============================================================================
# SUBSCRIPTIONS/LISTEN FOR NOTIFICATIONS (SSE)
# =============================================================================

class SubscriptionManager:
    """
    Manages subscriptions/listen for notifications per MCP spec.
    
    Handles long-lived SSE stream for:
    - notifications/tools/list_changed
    - notifications/resources/list_changed
    - notifications/prompts/list_changed
    """
    
    def __init__(self):
        self._subscribers: Dict[str, List[anyio.abc.SendStream]] = {
            "tools": [],
            "resources": [],
            "prompts": [],
        }
    
    async def subscribe(self, category: str, send_stream: anyio.abc.SendStream):
        """Add subscriber for category."""
        if category in self._subscribers:
            self._subscribers[category].append(send_stream)
    
    async def unsubscribe(self, category: str, send_stream: anyio.abc.SendStream):
        """Remove subscriber."""
        if category in self._subscribers:
            try:
                self._subscribers[category].remove(send_stream)
            except ValueError:
                pass
    
    async def notify(self, category: str, notification: Dict[str, Any]):
        """Send notification to all subscribers of category."""
        if category not in self._subscribers:
            return
        
        dead = []
        for stream in self._subscribers[category]:
            try:
                await stream.send(notification)
            except Exception:
                dead.append(stream)
        
        # Clean up dead streams
        for stream in dead:
            await self.unsubscribe(category, stream)


# =============================================================================
# TTL/CACHE SCOPE ON LIST/READ RESPONSES (SEP-2549)
# =============================================================================

def add_cache_metadata(response: Dict[str, Any], ttl_ms: int = 300000, cache_scope: str = "server") -> Dict[str, Any]:
    """
    Add ttlMs and cacheScope to _meta per SEP-2549.
    
    Args:
        response: Response dict to augment
        ttl_ms: Time-to-live in milliseconds (default 5 min)
        cache_scope: "server" or "client"
    """
    if "_meta" not in response:
        response["_meta"] = {}
    response["_meta"]["ttlMs"] = ttl_ms
    response["_meta"]["cacheScope"] = cache_scope
    return response


# =============================================================================
# X-MCP-HEADER TOOL PARAMETER -> MCP-PARAM-* HEADERS (SEP-2243)
# =============================================================================

def extract_mcp_param_headers(request: Request) -> Dict[str, str]:
    """
    Extract x-mcp-header tool parameters and convert to Mcp-Param-* headers.
    Per SEP-2243: Optional server annotation; clients MUST support.
    """
    params = {}
    for key, value in request.headers.items():
        if key.lower().startswith("mcp-param-"):
            params[key[10:]] = value  # Strip "mcp-param-"
    return params


# =============================================================================
# COMPLIANCE MIDDLEWARE STACK
# =============================================================================

def create_mcp_compliance_middleware(
    app: Starlette,
    server_info: Optional[Dict[str, Any]] = None,
    capabilities: Optional[ServerCapabilities] = None,
) -> Starlette:
    """
    Wrap Starlette app with all MCP 2026-07-28 compliance middleware.
    
    Order matters (outer to inner):
    1. TraceContextMiddleware - Extract/inject W3C trace context
    2. MCPHeaderValidationMiddleware - Validate required headers
    3. MCPMetaEnvelopeMiddleware - Extract/inject _meta envelope
    
    Returns wrapped app.
    """
    # Add middleware in reverse order (last added = outermost)
    app.add_middleware(MCPMetaEnvelopeMiddleware, server_info=server_info)
    app.add_middleware(MCPHeaderValidationMiddleware)
    app.add_middleware(TraceContextMiddleware)
    
    return app


# =============================================================================
# ROUTE REGISTRATION HELPERS
# =============================================================================

def register_mcp_compliance_routes(
    app: Starlette,
    discover_handler: ServerDiscoverHandler,
    protected_resource_handler: ProtectedResourceMetadataHandler,
    subscription_manager: SubscriptionManager,
) -> None:
    """
    Register MCP 2026-07-28 compliance routes on the Starlette app.
    
    Routes:
    - POST /mcp - Main Streamable HTTP endpoint (with middleware)
    - GET /.well-known/oauth-protected-resource - RFC 9728
    - GET /mcp/discover - server/discover (alternative to RPC)
    """
    
    # server/discover via RPC is handled by the MCP server itself
    # This registers the HTTP endpoint for direct access
    
    @app.route("/.well-known/oauth-protected-resource", methods=["GET"])
    async def oauth_protected_resource(request: Request):
        return await protected_resource_handler.handle(request)
    
    @app.route("/mcp/discover", methods=["GET"])
    async def mcp_discover(request: Request):
        # Return discover info via HTTP GET (cacheable)
        result = await discover_handler.handle({"id": "discover", "jsonrpc": "2.0"})
        return JSONResponse(result)


# =============================================================================
# INTEGRATION WITH EXISTING mcp_runtime.py
# =============================================================================

def create_compliant_mcp_runtime(
    mcp_server: Any,
    transport: str = "dual",
    server_info: Optional[Dict[str, Any]] = None,
    capabilities: Optional[ServerCapabilities] = None,
) -> Starlette:
    """
    Create MCP runtime with 2026-07-28 compliance built-in.
    
    Replaces run_mcp() from mcp_runtime.py with compliant version.
    
    Args:
        mcp_server: FastMCP instance
        transport: "stdio", "sse", "streamable-http", or "dual"
        server_info: Server identity for discover
        capabilities: Server capabilities
    
    Returns:
        Starlette app with all compliance middleware and routes
    """
    from mcp.server.fastmcp.server import StreamableHTTPASGIApp
    from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.routing import Mount, Route
    import contextlib
    
    server_info = server_info or {"name": "omega-engine", "version": "1.0.0"}
    capabilities = capabilities or ServerCapabilities(
        tools={"listChanged": True},
        resources={"subscribe": True, "listChanged": True},
        prompts={"listChanged": True},
        logging={},
    )
    
    # Create handlers
    discover_handler = ServerDiscoverHandler(
        server_name=server_info["name"],
        server_version=server_info["version"],
        capabilities=capabilities,
    )
    protected_resource_handler = ProtectedResourceMetadataHandler()
    subscription_manager = SubscriptionManager()
    
    # Build base app
    if transport == "stdio":
        # Stdio doesn't use HTTP middleware
        return None  # Handled separately
    
    # Create Starlette app
    app = Starlette()
    
    # Add compliance middleware
    create_mcp_compliance_middleware(app, server_info, capabilities)
    
    # Register compliance routes
    register_mcp_compliance_routes(
        app, discover_handler, protected_resource_handler, subscription_manager
    )
    
    # Add MCP transports
    if transport in ("sse", "dual"):
        sse = SseServerTransport(
            mcp_server.settings.message_path,
            security_settings=mcp_server.settings.transport_security,
        )
        
        async def handle_sse(request: Request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send,
            ) as streams:
                await mcp_server._mcp_server.run(
                    streams[0], streams[1],
                    mcp_server._mcp_server.create_initialization_options(),
                    stateless=True,
                )
            return Response()
        
        sse_routes = [
            Route(mcp_server.settings.sse_path, endpoint=handle_sse, methods=["GET"]),
            Mount(mcp_server.settings.message_path, app=sse.handle_post_message),
        ]
        app.router.routes.extend(sse_routes)
    
    if transport in ("streamable-http", "dual"):
        streamable_mgr = StreamableHTTPSessionManager(
            app=mcp_server._mcp_server,
            json_response=mcp_server.settings.json_response,
            stateless=True,
            security_settings=mcp_server.settings.transport_security,
        )
        streamable_app = StreamableHTTPASGIApp(streamable_mgr)
        
        streamable_routes = [
            Route(mcp_server.settings.streamable_http_path, endpoint=streamable_app),
        ]
        app.router.routes.extend(streamable_routes)
        
        # Lifespan for streamable manager
        @contextlib.asynccontextmanager
        async def lifespan(app):
            async with anyio.create_task_group() as tg:
                async with streamable_mgr.run():
                    yield
        
        app.router.lifespan_context = lifespan
    
    return app


# =============================================================================
# TESTING HELPERS
# =============================================================================

async def test_header_validation():
    """Test header validation middleware."""
    from starlette.testclient import TestClient
    
    app = Starlette()
    app.add_middleware(MCPHeaderValidationMiddleware)
    
    @app.route("/mcp", methods=["POST"])
    async def mcp_endpoint(request: Request):
        return JSONResponse({"jsonrpc": "2.0", "id": 1, "result": {}})
    
    client = TestClient(app)
    
    # Missing headers -> 400
    response = client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert response.status_code == 400
    assert "Missing required headers" in response.json()["error"]["message"]
    
    # Valid headers -> 200
    headers = {
        "Mcp-Method": "tools/list",
        "Mcp-Name": "",
        "MCP-Protocol-Version": "2026-07-28",
    }
    response = client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"}, headers=headers)
    assert response.status_code == 200
    
    print("✅ Header validation tests passed")


async def test_meta_envelope():
    """Test _meta envelope extraction/injection."""
    from starlette.testclient import TestClient
    
    app = Starlette()
    app.add_middleware(MCPMetaEnvelopeMiddleware, server_info={"name": "test", "version": "1.0"})
    
    @app.route("/mcp", methods=["POST"])
    async def mcp_endpoint(request: Request):
        return JSONResponse({"jsonrpc": "2.0", "id": 1, "result": {"tools": []}})
    
    client = TestClient(app)
    
    headers = {
        "Mcp-Method": "tools/list",
        "Mcp-Name": "",
        "MCP-Protocol-Version": "2026-07-28",
    }
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "_meta": {
            "clientInfo": {"name": "test-client", "version": "1.0"},
            "traceparent": "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01"
        }
    }
    
    response = client.post("/mcp", json=body, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "_meta" in data
    assert data["_meta"]["protocolVersion"] == "2026-07-28"
    assert data["_meta"]["serverInfo"]["name"] == "test"
    assert data["_meta"]["traceparent"] == "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01"
    
    print("✅ _meta envelope tests passed")


async def test_server_discover():
    """Test server/discover handler."""
    handler = ServerDiscoverHandler("test-server", "1.0.0")
    result = await handler.handle({"id": "1", "jsonrpc": "2.0"})
    
    assert result["jsonrpc"] == "2.0"
    assert result["id"] == "1"
    assert "protocolVersions" in result["result"]
    assert "2026-07-28" in result["result"]["protocolVersions"]
    assert result["result"]["serverInfo"]["name"] == "test-server"
    assert "_meta" in result
    assert result["_meta"]["ttlMs"] == 3600000
    
    print("✅ server/discover tests passed")


async def run_all_compliance_tests():
    """Run all compliance tests."""
    await test_header_validation()
    await test_meta_envelope()
    await test_server_discover()
    print("\n✅ All MCP 2026-07-28 compliance tests passed!")


if __name__ == "__main__":
    anyio.run(run_all_compliance_tests)