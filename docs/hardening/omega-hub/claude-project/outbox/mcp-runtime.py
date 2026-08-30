"""Standardized MCP Runtime for Omega Engine.
AP: AP-MCP-RUNTIME-v1.0.4
"""

import os
import logging
import contextlib
from typing import Any, Awaitable, Callable, Optional

logger = logging.getLogger("omega.mcp_runtime")

def run_mcp(mcp: Any, modify_app: Optional[Callable[[Any], None]] = None,
            custom_routes: Optional[list] = None,
            on_shutdown: Optional[Callable] = None,
            on_startup: Optional[Callable[[], Awaitable[None]]] = None):
    """Run an MCP server with dual-transport support.

    Serves both SSE (for OpenCode/Cline) and Streamable HTTP (for
    Antigravity IDE / VS Code forks) from a single server instance.

    Transport endpoints:
        SSE:            GET  /sse → SSE stream → POST /messages/
        Streamable HTTP: POST /mcp → direct JSON-RPC

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
    """
    transport = os.getenv("OMEGA_MCP_TRANSPORT", "stdio").lower()

    def _build_app():
        """Build a Starlette app with SSE + Streamable HTTP + custom routes.

        SSE handler uses stateless=True so clients (e.g. OpenCode) can
        reconnect without re-sending InitializeRequest.

        Streamable HTTP endpoint (/mcp) enables Antigravity IDE and other
        VS Code-fork MCP clients that POST directly to the serverURL.
        """
        import contextlib as _ctx
        from starlette.applications import Starlette
        from starlette.routing import Mount, Route
        from starlette.responses import Response
        from starlette.requests import Request
        from mcp.server.sse import SseServerTransport
        from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
        from mcp.server.fastmcp.server import StreamableHTTPASGIApp

        # ── SSE transport (legacy — OpenCode, Cline) ──────────────────
        sse = SseServerTransport(
            mcp.settings.message_path,
            security_settings=mcp.settings.transport_security,
        )

        async def handle_sse(request: Request) -> Response:
            async with sse.connect_sse(
                request.scope, request.receive, request._send,
            ) as streams:
                await mcp._mcp_server.run(
                    streams[0], streams[1],
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

        all_routes = sse_routes + streamable_routes

        # ── Lifespan: run StreamableHTTP session manager + cleanup ────
        @_ctx.asynccontextmanager
        async def lifespan(app):
            import anyio
            # Start background initialization task (runs concurrently with server)
            _startup_task = None
            if on_startup:
                _startup_task = anyio.create_task(on_startup())
            async with streamable_mgr.run():
                yield
            # Cancel startup task if still running on shutdown
            if _startup_task and not _startup_task.done():
                _startup_task.cancel()
                try:
                    await _startup_task
                except anyio.CancelledError:
                    pass
            # Shutdown cleanup — call on_shutdown if provided
            # [id-soft: quake-1996] Zone Memory — free allocated resources on exit
            if on_shutdown:
                try:
                    if hasattr(on_shutdown, '__call__'):
                        result = on_shutdown()
                        if hasattr(result, '__await__'):
                            await result
                except Exception as e:
                    logger.warning(f"Shutdown callback failed: {e}")

        # ── Assemble final app ────────────────────────────────────────
        if modify_app:
            # Legacy support: modify_app expected a full Starlette app.
            legacy_app = Starlette(routes=all_routes)
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
