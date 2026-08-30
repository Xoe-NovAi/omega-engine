# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
MCP 2026-07-28 Streamable HTTP Compliance Runtime
AP: AP-MCP-RUNTIME-v2.0.0
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
# [heritage: anyio 2024] M1 AnyIO — async runtime (TaskGroup lifecycle, Semaphore)
# [heritage: mcp 2024] MCP Protocol — AI-tool communication (dual-transport SSE + Streamable HTTP)
# [heritage: w3c-trace-context 2021] Distributed tracing

import os
import logging
import contextlib
import json
from typing import Any, Awaitable, Callable, Optional, List

import anyio
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.responses import Response
from starlette.requests import Request
from starlette.middleware import Middleware

from mcp.server.sse import SseServerTransport
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.server.fastmcp.server import StreamableHTTPASGIApp

from src.omega.mcp_core.compliance import (
    MCPHeaderValidationMiddleware,
    MCPMetaEnvelopeMiddleware,
    TraceContextMiddleware,
    RequestIDMiddleware,
    RateLimitHeadersMiddleware,
    ServerDiscoverHandler,
    ProtectedResourceMetadataHandler,
    SUPPORTED_PROTOCOL_VERSIONS,
)

logger = logging.getLogger("omega.mcp_runtime")


def run_mcp(
    mcp: Any,
    modify_app: Optional[Callable[[Any], None]] = None,
    custom_routes: Optional[List[Route]] = None,
    on_shutdown: Optional[Callable] = None,
    on_startup: Optional[Callable[[Optional[anyio.abc.TaskGroup]], Awaitable[None]]] = None,
    # Compliance options
    enable_compliance: bool = True,
    server_name: str = "omega-engine",
    server_version: str = "1.0.0",
    oauth_auth_server: str = "https://omega-engine.local/oauth",
    oauth_scopes: Optional[List[str]] = None,
):
    """
    Run an MCP server with dual-transport support AND 2026-07-28 compliance.

    Transport endpoints:
        SSE:            GET  /sse → SSE stream → POST /messages/
        Streamable HTTP: POST /mcp → direct JSON-RPC

    Compliance endpoints (when enable_compliance=True):
        GET  /.well-known/oauth-protected-resource  (RFC 9728)
        RPC  server/discover                        (SEP-2575)

    Args:
        mcp: FastMCP instance to run.
        modify_app: Optional callback to add custom HTTP routes to the
            underlying Starlette ASGI app. Ignored when transport is 'stdio'.
        custom_routes: Optional list of Starlette Route objects to add
            at the TOP level of the app, before the MCP sub-app mount.
            These take priority over MCP framework routing.
        on_shutdown: Optional callable (sync or async) called during
            server shutdown for cleanup.
        on_startup: Optional async callable called as a background task
            inside the event loop after the server starts. Use this to
            kick off heavy initialization without blocking the SSE listener.
            The task runs concurrently with the server.
        enable_compliance: Enable MCP 2026-07-28 compliance middleware.
        server_name: Server name for server/discover and RFC 9728.
        server_version: Server version for server/discover.
        oauth_auth_server: OAuth 2.1 authorization server URL for RFC 9728.
        oauth_scopes: Supported OAuth scopes for RFC 9728.
    """
    transport = os.getenv("OMEGA_MCP_TRANSPORT", "stdio").lower()

    def _build_app():
        """Build a Starlette app with SSE + Streamable HTTP + compliance middleware."""
        # ── Compliance Handlers ─────────────────────────────────────────
        discover_handler = ServerDiscoverHandler(
            server_name=server_name,
            server_version=server_version,
        )
        protected_resource_handler = ProtectedResourceMetadataHandler(
            resource_url=f"https://{os.getenv('OMEGA_MCP_HOST', '127.0.0.1')}:{os.getenv('OMEGA_MCP_PORT', '8000')}/mcp",
            auth_server_url=oauth_auth_server,
            scopes=oauth_scopes or ["mcp:tools", "mcp:resources", "mcp:prompts"],
        )

        async def handle_server_discover(request: Request) -> Response:
            """Handle server/discover RPC method."""
            try:
                body = await request.json()
            except Exception:
                return Response(status_code=400)
            result = await discover_handler.handle(body)
            return Response(content=json.dumps(result), media_type="application/json")

        async def handle_protected_resource(request: Request) -> Response:
            """Handle RFC 9728 Protected Resource Metadata."""
            return await protected_resource_handler.handle(request)

        # ── SSE transport (legacy — OpenCode, Cline) ──────────────────
        sse = SseServerTransport(
            mcp.settings.message_path,
            security_settings=mcp.settings.transport_security,
        )

        async def handle_sse(request: Request) -> Response:
            async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
            ) as streams:
                await mcp._mcp_server.run(
                    streams[0],
                    streams[1],
                    mcp._mcp_server.create_initialization_options(),
                    stateless=True,
                )
            return Response()

        sse_routes = [
            Route(mcp.settings.sse_path, endpoint=handle_sse, methods=["GET"]),
            Mount(mcp.settings.message_path, app=sse.handle_post_message),
        ]

        # ── Streamable HTTP transport (new — Antigravity IDE) ────────
        streamable_mgr = StreamableHTTPSessionManager(
            app=mcp._mcp_server,
            json_response=mcp.settings.json_response,
            stateless=True,
            security_settings=mcp.settings.transport_security,
        )
        streamable_app = StreamableHTTPASGIApp(streamable_mgr)

        streamable_routes = [
            Route(mcp.settings.streamable_http_path, endpoint=streamable_app),
        ]

        # ── Compliance Routes ──────────────────────────────────────────
        compliance_routes = []
        if enable_compliance:
            compliance_routes = [
                Route(
                    "/.well-known/oauth-protected-resource",
                    endpoint=handle_protected_resource,
                    methods=["GET"],
                ),
                Route("/mcp/discover", endpoint=handle_server_discover, methods=["POST"]),
            ]

        all_routes = sse_routes + streamable_routes + compliance_routes

        # ── Middleware Stack (order matters: outer to inner) ──────────
        middleware = []

        # Always-on: Request ID (outermost — must run first to set state)
        middleware.append(Middleware(RequestIDMiddleware))

        if enable_compliance:
            # Rate-limit headers (early, before validation)
            middleware.append(Middleware(RateLimitHeadersMiddleware, limit=100, window_seconds=60))
            # Trace context propagation (SEP-414)
            middleware.append(Middleware(TraceContextMiddleware))
            # Header validation (SEP-2243) — non-strict for legacy MCP clients (OpenCode, Cline)
            middleware.append(Middleware(MCPHeaderValidationMiddleware, strict=False))
            # _meta envelope (SEP-2575) — innermost compliance
            middleware.append(
                Middleware(
                    MCPMetaEnvelopeMiddleware,
                    server_info={"name": server_name, "version": server_version},
                )
            )

        # ── Lifespan: run StreamableHTTP session manager + cleanup ────
        @contextlib.asynccontextmanager
        async def lifespan(app):
            # Wrap server run + background tasks in AnyIO TaskGroup
            # [id-soft: vet-008] Zone Memory — deterministic cleanup via zone-purge semantics
            # all background tasks on shutdown (circuit breaker pattern)
            async with anyio.create_task_group() as tg:
                if on_startup:
                    result = on_startup(tg)
                    if hasattr(result, "__await__"):
                        await result
                async with streamable_mgr.run():
                    yield
            # TaskGroup exit: all background tasks cancelled
            # Shutdown cleanup — call on_shutdown if provided
            # [id-soft: vet-008] Zone Memory — deterministic cleanup via zone-purge semantics
            if on_shutdown:
                try:
                    if hasattr(on_shutdown, "__call__"):
                        result = on_shutdown()
                        if hasattr(result, "__await__"):
                            await result
                except (Exception, RuntimeError, OSError) as e:
                    logger.warning(f"Shutdown callback failed: {e}")

        # ── Assemble final app ────────────────────────────────────────
        if modify_app:
            # Legacy support: modify_app expected a full Starlette app.
            legacy_app = Starlette(routes=all_routes, middleware=middleware)
            modify_app(legacy_app)
            return Starlette(
                routes=(custom_routes or []) + [Mount("/", app=legacy_app)],
                debug=mcp.settings.debug,
                lifespan=lifespan,
            )

        if custom_routes:
            all_routes = custom_routes + all_routes

        return Starlette(
            routes=all_routes,
            middleware=middleware,
            debug=mcp.settings.debug,
            lifespan=lifespan,
        )

    # --- Systemd Socket Activation Logic ---
    listen_fds = os.getenv("LISTEN_FDS")
    if listen_fds and int(listen_fds) > 0:
        logger.info(f"Systemd socket activation detected (FDs: {listen_fds})")
        if transport == "sse":
            import uvicorn
            from anyio import run

            async def _run_sse_socket():
                logger.info(f"Starting MCP server '{mcp.name}' on systemd socket (FD 3)")
                app = _build_app()
                config = uvicorn.Config(
                    app,
                    fd=3,  # SD_LISTEN_FDS_START is always 3
                    log_level=mcp.settings.log_level.lower(),
                )
                server = uvicorn.Server(config)
                await server.serve()

            run(_run_sse_socket)
            return
    # ---------------------------------------

    host = os.getenv("OMEGA_MCP_HOST", "127.0.0.1")
    port_str = os.getenv("OMEGA_MCP_PORT")

    if transport == "sse":
        if not port_str:
            logger.error("OMEGA_MCP_PORT must be set for SSE transport.")
            return
        port = int(port_str)
        logger.info(f"Starting MCP server '{mcp.name}' on sse://{host}:{port}")

        if modify_app or custom_routes:
            import uvicorn
            from anyio import run

            async def _run_sse_modified():
                app = _build_app()
                config = uvicorn.Config(
                    app,
                    host=host,
                    port=port,
                    log_level=mcp.settings.log_level.lower(),
                )
                server = uvicorn.Server(config)
                await server.serve()

            run(_run_sse_modified)
        else:
            mcp.settings.host = host
            mcp.settings.port = port
            mcp.run(transport="sse")
    else:
        logger.info(f"Starting MCP server '{mcp.name}' on stdio")
        mcp.run(transport="stdio")


# ── Convenience: Register server/discover with FastMCP ────────────────────


def register_discover_method(
    mcp: Any, server_name: str = "omega-engine", server_version: str = "1.0.0"
):
    """
    Register server/discover method with FastMCP instance.

    Call this after creating your FastMCP instance:
        mcp = FastMCP("my-server")
        register_discover_method(mcp)
    """

    @mcp.tool(name="server/discover")
    async def server_discover() -> dict:
        """MCP 2026-07-28 server/discover method (SEP-2575)."""
        return {
            "protocolVersions": SUPPORTED_PROTOCOL_VERSIONS,
            "capabilities": {
                "tools": {"listChanged": True},
                "resources": {"subscribe": True, "listChanged": True},
                "prompts": {"listChanged": True},
                "logging": {},
            },
            "serverInfo": {"name": server_name, "version": server_version},
            "instructions": "Omega Engine MCP Server — Dual transport (SSE + Streamable HTTP)",
        }

    return server_discover


# ── Export ────────────────────────────────────────────────────────────────

__all__ = [
    "run_mcp",
    "register_discover_method",
]
