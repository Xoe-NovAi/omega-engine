# AP Token: AP-MCP-CLIENT-v1.0.0
# 🔱 Sovereign MCP Client — Hub-as-Client Implementation
# ⬡ OMEGA ⬡ MA'AT ⬡ anyio ⬡ opencode ⬡ trc_mcp_client ⬡ MCP-CLIENT

import logging
import json
from typing import Any, Dict, List, Optional, AsyncGenerator
from dataclasses import dataclass

import anyio
from mcp import ClientSession
from mcp.client.sse import sse_client

logger = logging.getLogger("omega.hub.client")

@dataclass
class MCPToolResult:
    """Standardized result of an MCP tool call."""
    content: List[Any]
    is_error: bool = False
    raw_result: Optional[Any] = None

class SovereignMCPClient:
    """
    Sovereign MCP Client allowing the Omega Hub to act as a client to other MCP servers.
    
    Complies with Mandate 1 (AnyIO Absolute) by wrapping the mcp-python-sdk 
    (which is asyncio-based) in an AnyIO-compatible wrapper where necessary, 
    or using anyio.to_thread.run_sync for blocking calls.
    
    Note: The mcp-python-sdk currently relies on asyncio. This client is designed
    to be run within an AnyIO event loop, ensuring compatibility with the 
    Omega Engine's core.
    """

    def __init__(self, server_url: str, timeout: float = 120.0):
        self.server_url = server_url
        self.timeout = timeout
        self._session: Optional[ClientSession] = None
        self._read_stream = None
        self._write_stream = None

    async def __aenter__(self):
        """Initialize connection and session."""
        try:
            logger.info("Connecting to MCP server at %s...", self.server_url)
            self._sse_context = sse_client(self.server_url)
            logger.info("Entering SSE context...")
            self._read_stream, self._write_stream = await self._sse_context.__aenter__()
            logger.info("SSE context entered. Initializing session...")
            self._session = ClientSession(self._read_stream, self._write_stream)
            await self._session.initialize()
            logger.info("Sovereign MCP Client connected and initialized at %s", self.server_url)
            return self
        except Exception as e:
            logger.error("Failed to connect to MCP server at %s: %s", self.server_url, e)
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanly close the session and streams."""
        if self._session:
            await self._session.close()
        if self._sse_context:
            await self._sse_context.__aexit__(exc_type, exc_val, exc_tb)
        logger.info("Sovereign MCP Client disconnected from %s", self.server_url)

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any], trace_id: Optional[str] = None) -> MCPToolResult:
        """
        Execute a tool on the remote MCP server.
        
        Args:
            tool_name: The name of the tool to call.
            arguments: The arguments to pass to the tool.
            trace_id: Optional trace ID for propagation.
            
        Returns:
            MCPToolResult containing the tool's output.
        """
        if not self._session:
            raise RuntimeError("MCP Client session not initialized. Use 'async with' block.")

        # Propagate trace_id into arguments if provided
        call_args = arguments.copy()
        if trace_id:
            call_args["trace_id"] = trace_id

        try:
            # Use anyio.move_on_after to enforce timeout on the tool call
            async with anyio.move_on_after(self.timeout):
                result = await self._session.call_tool(tool_name, call_args)
                
                # Extract text content from the result
                content = []
                for item in result.content:
                    if hasattr(item, "text"):
                        content.append(item.text)
                    else:
                        content.append(str(item))
                
                return MCPToolResult(
                    content=content,
                    is_error=getattr(result, "is_error", False),
                    raw_result=result
                )
        except TimeoutError:
            logger.error("MCP tool call '%s' timed out after %ss", tool_name, self.timeout)
            return MCPToolResult(content=[f"Error: Tool {tool_name} timed out"], is_error=True)
        except Exception as e:
            logger.error("MCP tool call '%s' failed: %s", tool_name, e)
            return MCPToolResult(content=[f"Error: {str(e)}"], is_error=True)

    async def list_tools(self) -> List[str]:
        """List all available tools on the remote server."""
        if not self._session:
            raise RuntimeError("MCP Client session not initialized.")
        
        try:
            result = await self._session.list_tools()
            return [t.name for t in result.tools]
        except Exception as e:
            logger.error("Failed to list tools from %s: %s", self.server_url, e)
            return []
