"""Standardized MCP Runtime for Omega Engine.
AP: AP-MCP-RUNTIME-v1.0.2
"""

import os
import logging
from typing import Any, Callable, Optional

logger = logging.getLogger("omega.mcp_runtime")

def run_mcp(mcp: Any, modify_app: Optional[Callable[[Any], None]] = None):
    """Run an MCP server with transport selection via environment variables.
    
    Args:
        mcp: FastMCP instance to run.
        modify_app: Optional callback to add custom HTTP routes to the
            underlying Starlette ASGI app (returned by mcp.sse_app()).
            Called before the server starts accepting connections.
            Ignored when transport is 'stdio'.
    """
    transport = os.getenv("OMEGA_MCP_TRANSPORT", "stdio").lower()
    
    # --- Systemd Socket Activation Logic ---
    listen_fds = os.getenv("LISTEN_FDS")
    if listen_fds and int(listen_fds) > 0:
        logger.info(f"Systemd socket activation detected (FDs: {listen_fds})")
        if transport == "sse":
            import uvicorn
            from anyio import run
            
            async def _run_sse_socket():
                # FastMCP doesn't natively support FD-based uvicorn config
                # so we manually bootstrap the Starlette app it generates.
                logger.info(f"Starting MCP server '{mcp.name}' on systemd socket (FD 3)")
                app = mcp.sse_app()
                if modify_app:
                    modify_app(app)
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
        
        if modify_app:
            # Custom routes require manual uvicorn boot so we can inject
            # routes into the Starlette app before serving.
            import uvicorn
            from anyio import run
            
            async def _run_sse_modified():
                app = mcp.sse_app()
                modify_app(app)
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
            # FastMCP settings are stored in mcp.settings
            mcp.settings.host = host
            mcp.settings.port = port
            mcp.run(transport="sse")
    else:
        logger.info(f"Starting MCP server '{mcp.name}' on stdio")
        mcp.run(transport="stdio")
