"""Standardized MCP Runtime for Omega Engine.
AP: AP-MCP-RUNTIME-v1.0.2
"""

import os
import logging
from typing import Any, Callable, Optional

logger = logging.getLogger("omega.mcp_runtime")

def run_mcp(mcp: Any, modify_app: Optional[Callable[[Any], None]] = None,
            custom_routes: Optional[list] = None):
    """Run an MCP server with transport selection via environment variables.

    Args:
        mcp: FastMCP instance to run.
        modify_app: Optional callback to add custom HTTP routes to the
            underlying Starlette ASGI app (returned by mcp.sse_app()).
            Called before the server starts accepting connections.
            Ignored when transport is 'stdio'.
        custom_routes: Optional list of Starlette Route objects to add
            at the TOP level of the app, before the MCP sub-app mount.
            These take priority over MCP framework routing.
    """
    transport = os.getenv("OMEGA_MCP_TRANSPORT", "stdio").lower()

    def _build_app():
        """Build a Starlette app with MCP mounted + custom routes.

        Uses a custom SSE handler with stateless=True so that clients
        (e.g. OpenCode) can reconnect and send tool calls without
        re-sending the InitializeRequest — which MCP SDK currently
        requires per-session.
        """
        from starlette.applications import Starlette
        from starlette.routing import Mount, Route
        from starlette.responses import Response
        from starlette.requests import Request
        from mcp.server.sse import SseServerTransport

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

        routes = [
            Route(mcp.settings.sse_path, endpoint=handle_sse, methods=["GET"]),
            Mount(mcp.settings.message_path, app=sse.handle_post_message),
        ]

        if modify_app:
            # Legacy support: modify_app expected a full Starlette app.
            # Build one for compatibility.
            from starlette.applications import Starlette
            legacy_app = Starlette(routes=routes)
            modify_app(legacy_app)
            return Starlette(
                routes=(custom_routes or []) + [Mount("/", app=legacy_app)],
                debug=mcp.settings.debug,
            )

        if custom_routes:
            all_routes = custom_routes + routes
            return Starlette(routes=all_routes, debug=mcp.settings.debug)
        return Starlette(routes=routes, debug=mcp.settings.debug)

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
