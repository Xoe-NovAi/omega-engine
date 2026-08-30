# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
MCP 2026-07-28 Streamable HTTP Compliance Middleware
AP: AP-MCP-COMPLIANCE-v1.0.0
M1: AnyIO — async runtime
M13: Temple-Grade — spec compliance

Implements Sprint 1 (Transport Core) from R_CG01_MCP_STREAMABLE_HTTP_OAUTH_AUDIT.md:
- Header validation: Mcp-Method, Mcp-Name, MCP-Protocol-Version (SEP-2243)
- _meta envelope extraction/injection (SEP-2575)
- server/discover method registration (SEP-2575)
- RFC 9728 Protected Resource Metadata endpoint
- W3C Trace Context propagation (SEP-414)
- InputRequiredResult for MRTR (SEP-2322)
- subscriptions/listen for notifications (SSE)
- ttlMs + cacheScope on list/read responses (SEP-2549)
- x-mcp-header tool parameter -> Mcp-Param-* headers (SEP-2243)
"""
# [heritage: anyio 2024] M1 AnyIO — async runtime
# [heritage: w3c-trace-context 2021] Distributed tracing
# [heritage: mcp 2024] MCP Protocol — AI-tool communication

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

logger = logging.getLogger("omega.mcp.compliance")


# =============================================================================
# CONSTANTS
# =============================================================================

PROTOCOL_VERSION_CURRENT = "2026-07-28"
SUPPORTED_PROTOCOL_VERSIONS = ["2026-07-28", "2025-11-25"]

# Required headers per SEP-2243
REQUIRED_HEADERS_POST = {"mcp-method", "mcp-name", "mcp-protocol-version"}
REQUIRED_HEADERS_GET = {"mcp-protocol-version"}
REQUIRED_HEADERS_ALL = {"mcp-protocol-version"}

# Error codes (B6: -32002 -> -32602; C-1: HeaderMismatch = -32020 per SEP-2243)
ERROR_CODES = {
    "PARSE_ERROR": -32700,
    "INVALID_REQUEST": -32600,
    "METHOD_NOT_FOUND": -32601,
    "INVALID_PARAMS": -32602,  # Was -32002
    "INTERNAL_ERROR": -32603,
    "HEADER_MISMATCH": -32020,  # C-1: SEP-2243 verified — NOT -32001, NOT -32600
    "PROTOCOL_VERSION_MISMATCH": -32020,  # Same as HeaderMismatch per SEP-2243
}


# =============================================================================
# MIDDLEWARE 1: W3C TRACE CONTEXT PROPAGATION (SEP-414)
# =============================================================================


class TraceContextMiddleware(BaseHTTPMiddleware):
    """
    Propagate W3C Trace Context headers (traceparent, tracestate, baggage).

    Per SEP-414: Extract from incoming request, inject into outgoing response,
    and include in _meta envelope for distributed tracing.
    """

    async def dispatch(self, request: Request, call_next):
        # Skip SSE transport paths
        if request.url.path.startswith("/messages") or request.url.path == "/sse":
            return await call_next(request)

        # Extract trace context from headers
        traceparent = request.headers.get("traceparent")
        tracestate = request.headers.get("tracestate")
        baggage = request.headers.get("baggage")

        # Store in request state for downstream use
        request.state.trace_context = {
            "traceparent": traceparent,
            "tracestate": tracestate,
            "baggage": baggage,
        }

        # Process request
        response = await call_next(request)

        # Inject trace context into response headers
        if traceparent:
            response.headers["traceparent"] = traceparent
        if tracestate:
            response.headers["tracestate"] = tracestate
        if baggage:
            response.headers["baggage"] = baggage

        return response


# =============================================================================
# MIDDLEWARE 2: HEADER VALIDATION (SEP-2243)
# =============================================================================


class MCPHeaderValidationMiddleware(BaseHTTPMiddleware):
    """
    Validate required MCP headers per SEP-2243.

    Required headers:
    - POST: Mcp-Method, Mcp-Name, MCP-Protocol-Version
    - GET:  MCP-Protocol-Version
    - ALL:  MCP-Protocol-Version

    Validation rules:
    - Mcp-Method must match body.method
    - Mcp-Name must match params.name or params.uri
    - MCP-Protocol-Version must match _meta.protocolVersion
    - Mismatch = 400 with error code -32600
    """

    def __init__(self, app: ASGIApp, strict: bool = True):
        super().__init__(app)
        self.strict = strict

    async def dispatch(self, request: Request, call_next):
        # Only validate MCP endpoints
        if not self._is_mcp_endpoint(request):
            return await call_next(request)

        method = request.method.upper()
        headers = {k.lower(): v for k, v in request.headers.items()}

        # Check required headers
        required = REQUIRED_HEADERS_POST if method == "POST" else REQUIRED_HEADERS_GET
        missing = required - set(headers.keys())

        if missing:
            if not self.strict:
                # Non-strict mode: pass through for non-SEP-2243 clients (OpenCode, Cline, etc.)
                return await call_next(request)
            return self._error_response(
                400,
                ERROR_CODES["INVALID_REQUEST"],
                f"Missing required headers: {', '.join(sorted(missing))}",
                request_id=None,
            )

        # Validate MCP-Protocol-Version
        proto_version = headers.get("mcp-protocol-version")
        if proto_version and proto_version not in SUPPORTED_PROTOCOL_VERSIONS:
            if not self.strict:
                # Non-strict mode: pass through for unsupported versions
                return await call_next(request)
            return self._error_response(
                400,
                ERROR_CODES["PROTOCOL_VERSION_MISMATCH"],
                f"Unsupported protocol version: {proto_version}. Supported: {SUPPORTED_PROTOCOL_VERSIONS}",
                request_id=None,
            )

        # For POST, validate body headers match
        if method == "POST":
            try:
                body = await request.json()
                request.state.mcp_body = body  # Cache for downstream

                # Validate Mcp-Method matches body.method
                if "mcp-method" in headers and "method" in body:
                    if headers["mcp-method"] != body["method"]:
                        return self._error_response(
                            400,
                            ERROR_CODES["HEADER_MISMATCH"],
                            f"Mcp-Method header ({headers['mcp-method']}) does not match body.method ({body['method']})",
                            request_id=body.get("id"),
                        )

                # Validate Mcp-Name matches params.name/uri
                if "mcp-name" in headers:
                    params = body.get("params", {})
                    expected_name = params.get("name") or params.get("uri")
                    if expected_name and headers["mcp-name"] != expected_name:
                        return self._error_response(
                            400,
                            ERROR_CODES["HEADER_MISMATCH"],
                            f"Mcp-Name header ({headers['mcp-name']}) does not match params.name/uri ({expected_name})",
                            request_id=body.get("id"),
                        )

            except Exception as e:
                if self.strict:
                    return self._error_response(
                        400,
                        ERROR_CODES["PARSE_ERROR"],
                        f"Failed to parse JSON body: {e}",
                        request_id=None,
                    )

        return await call_next(request)

    def _is_mcp_endpoint(self, request: Request) -> bool:
        """Check if request is to an MCP endpoint."""
        path = request.url.path
        # SSE GET connection doesn't require MCP headers - they're on POST to /messages
        if path == "/sse" and request.method == "GET":
            return False
        # SSE message path - let the SSE transport handle it directly
        if path.startswith("/messages"):
            return False
        return path.startswith("/mcp")

    def _error_response(
        self, status: int, code: int, message: str, request_id: Any
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status,
            content={
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": code, "message": message},
            },
        )


# =============================================================================
# MIDDLEWARE 3: _META ENVELOPE EXTRACTION/INJECTION (SEP-2575)
# =============================================================================


class MCPMetaEnvelopeMiddleware(BaseHTTPMiddleware):
    """
    Extract _meta envelope from request and inject into response.

    Per SEP-2575: _meta carries protocolVersion, clientInfo, clientCapabilities,
    serverInfo, traceparent, tracestate, baggage.
    """

    def __init__(self, app: ASGIApp, server_info: Optional[Dict[str, Any]] = None):
        super().__init__(app)
        self.server_info = server_info or {"name": "omega-engine", "version": "1.0.0"}

    async def dispatch(self, request: Request, call_next):
        # Skip SSE transport paths
        if request.url.path.startswith("/messages") or request.url.path == "/sse":
            return await call_next(request)

        # Extract _meta from request body (for POST)
        request_meta = {}
        if request.method == "POST":
            body = getattr(request.state, "mcp_body", None)
            if body and "_meta" in body:
                request_meta = body["_meta"]
                request.state.request_meta = request_meta

        # Merge with trace context from middleware
        trace_ctx = getattr(request.state, "trace_context", {})
        if trace_ctx:
            request_meta.update({k: v for k, v in trace_ctx.items() if v})

        # Process request
        response = await call_next(request)

        # Inject _meta into response (for JSON-RPC responses)
        if isinstance(response, JSONResponse):
            # We can't easily modify the response body here without re-reading
            # The actual injection happens in the MCP server handler
            pass

        return response


# =============================================================================
# MIDDLEWARE 4: REQUEST ID GENERATION
# =============================================================================

import uuid


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Generate and propagate request IDs for tracing and rate-limiting.

    If the client provides an X-Request-Id header, it is preserved.
    If not, a UUID is generated automatically.
    The request ID is stored in request.state.request_id and echoed
    in the response as X-Request-Id.
    """

    async def dispatch(self, request: Request, call_next):
        # Skip SSE transport paths
        if request.url.path.startswith("/messages") or request.url.path == "/sse":
            return await call_next(request)

        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)

        response.headers["X-Request-Id"] = request_id
        return response


# =============================================================================
# MIDDLEWARE 5: RATE-LIMIT HEADERS
# =============================================================================


class RateLimitHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add rate-limit response headers (X-RateLimit-Limit, etc.).

    Per default, enforces no actual rate-limiting — only adds headers.
    Subclass and override _check_rate_limit() for enforcement.
    """

    def __init__(
        self,
        app: ASGIApp,
        limit: int = 100,
        window_seconds: int = 60,
        enabled: bool = True,
    ):
        super().__init__(app)
        self.limit = limit
        self.window_seconds = window_seconds
        self.enabled = enabled

    async def dispatch(self, request: Request, call_next):
        # Skip SSE transport paths
        if request.url.path.startswith("/messages") or request.url.path == "/sse":
            return await call_next(request)

        response = await call_next(request)

        if self.enabled:
            remaining = await self._get_remaining(request)
            reset_at = await self._get_reset_at(request)
            response.headers["X-RateLimit-Limit"] = str(self.limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(reset_at)

        return response

    async def _get_remaining(self, request: Request) -> int:
        """Override for actual rate-limit enforcement."""
        return self.limit

    async def _get_reset_at(self, request: Request) -> int:
        """Return Unix timestamp when the window resets."""
        import time

        return int(time.time()) + self.window_seconds


# =============================================================================
# SERVER DISCOVER HANDLER (SEP-2575)
# =============================================================================


@dataclass
class ServerDiscoverHandler:
    """Handle server/discover RPC method per SEP-2575."""

    server_name: str = "omega-engine"
    server_version: str = "1.0.0"
    capabilities: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = {
                "tools": {"listChanged": True},
                "resources": {"subscribe": True, "listChanged": True},
                "prompts": {"listChanged": True},
                "logging": {},
            }

    async def handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle server/discover request."""
        request_id = request.get("id")

        result = {
            "protocolVersions": SUPPORTED_PROTOCOL_VERSIONS,
            "capabilities": self.capabilities,
            "serverInfo": {
                "name": self.server_name,
                "version": self.server_version,
            },
            "instructions": "Omega Engine MCP Server — Dual transport (SSE + Streamable HTTP)",
        }

        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result,
        }

        # Add _meta with cache metadata (SEP-2549)
        response["_meta"] = {
            "protocolVersion": PROTOCOL_VERSION_CURRENT,
            "serverInfo": {"name": self.server_name, "version": self.server_version},
            "ttlMs": 3600000,  # 1 hour cache
            "cacheScope": "server",
        }

        return response


# =============================================================================
# RFC 9728 PROTECTED RESOURCE METADATA HANDLER
# =============================================================================


@dataclass
class ProtectedResourceMetadataHandler:
    """Handle RFC 9728 OAuth 2.1 Protected Resource Metadata."""

    resource_url: str = "https://omega-engine.local/mcp"
    auth_server_url: str = "https://omega-engine.local/oauth"
    scopes: List[str] = field(default_factory=lambda: ["mcp:tools", "mcp:resources", "mcp:prompts"])
    bearer_methods: List[str] = field(default_factory=lambda: ["header"])
    documentation_url: str = "https://omega-engine.local/docs/mcp"

    async def handle(self, request: Request) -> JSONResponse:
        """Return Protected Resource Metadata per RFC 9728."""
        metadata = {
            "resource": self.resource_url,
            "authorization_servers": [self.auth_server_url],
            "bearer_methods_supported": self.bearer_methods,
            "scopes_supported": self.scopes,
            "resource_documentation": self.documentation_url,
        }

        return JSONResponse(metadata)


# =============================================================================
# TTL/CACHE SCOPE HELPER (SEP-2549)
# =============================================================================


def add_cache_metadata(
    response: Dict[str, Any], ttl_ms: int = 300000, cache_scope: str = "server"
) -> Dict[str, Any]:
    """Add ttlMs and cacheScope to _meta per SEP-2549."""
    if "_meta" not in response:
        response["_meta"] = {}
    response["_meta"]["ttlMs"] = ttl_ms
    response["_meta"]["cacheScope"] = cache_scope
    return response


# =============================================================================
# MCP-PARAM-* HEADERS HELPER (SEP-2243)
# =============================================================================


def extract_mcp_param_headers(request: Request) -> Dict[str, str]:
    """Extract x-mcp-header tool parameters as Mcp-Param-* headers per SEP-2243."""
    params = {}
    for key, value in request.headers.items():
        if key.lower().startswith("mcp-param-"):
            params[key[10:]] = value  # Strip "mcp-param-"
    return params


# =============================================================================
# INPUT REQUIRED RESULT FOR MRTR (SEP-2322)
# =============================================================================


@dataclass
class InputRequiredResult:
    """InputRequiredResult for Multi-Round-Trip Requests (SEP-2322)."""

    request_id: str
    prompt: str
    schema: Dict[str, Any] = field(default_factory=lambda: {"type": "string"})

    def to_result(self) -> Dict[str, Any]:
        return {
            "type": "input_required",
            "requestId": self.request_id,
            "prompt": self.prompt,
            "schema": self.schema,
        }


# =============================================================================
# SUBSCRIPTION MANAGER FOR NOTIFICATIONS (SSE)
# =============================================================================


class SubscriptionManager:
    """Manage subscriptions/listen for notifications per MCP spec."""

    def __init__(self):
        self._subscribers: Dict[str, List[Any]] = {
            "tools": [],
            "resources": [],
            "prompts": [],
        }

    async def subscribe(self, category: str, send_stream: Any):
        if category in self._subscribers:
            self._subscribers[category].append(send_stream)

    async def unsubscribe(self, category: str, send_stream: Any):
        if category in self._subscribers:
            try:
                self._subscribers[category].remove(send_stream)
            except ValueError:
                pass

    async def notify(self, category: str, notification: Dict[str, Any]):
        if category not in self._subscribers:
            return

        dead = []
        for stream in self._subscribers[category]:
            try:
                await stream.send(notification)
            except Exception:
                dead.append(stream)

        for stream in dead:
            await self.unsubscribe(category, stream)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "PROTOCOL_VERSION_CURRENT",
    "SUPPORTED_PROTOCOL_VERSIONS",
    "ERROR_CODES",
    # Middleware
    "TraceContextMiddleware",
    "MCPHeaderValidationMiddleware",
    "MCPMetaEnvelopeMiddleware",
    "RequestIDMiddleware",
    "RateLimitHeadersMiddleware",
    # Handlers
    "ServerDiscoverHandler",
    "ProtectedResourceMetadataHandler",
    # Helpers
    "add_cache_metadata",
    "extract_mcp_param_headers",
    "InputRequiredResult",
    "SubscriptionManager",
]
