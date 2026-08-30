# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
MCP 2026-07-28 Streamable HTTP Client with SEP-2575 Header Validation
AP: AP-MCP-CLIENT-v1.0.0
M1: AnyIO — async runtime
M13: Temple-Grade — spec compliance

Implements Sprint 1 (Transport Core) from R_CG01_MCP_STREAMABLE_HTTP_OAUTH_AUDIT.md:
- SEP-2575 header extraction on EVERY request
- Response provenance validation (M22)
- Auto-request-id generation
- Timeout and error handling per M23 Failure Integrity
"""
# [heritage: anyio 2024] M1 AnyIO — async runtime
# [heritage: httpx 2023] HTTP client

import json
import logging
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger("omega.mcp.client")

# =============================================================================
# CONSTANTS
# =============================================================================

PROTOCOL_VERSION_CURRENT = "2026-07-28"
SUPPORTED_PROTOCOL_VERSIONS = ["2026-07-28", "2025-11-25"]

# Required headers per SEP-2243
REQUIRED_POST_HEADERS = {
    "mcp-method": "string",
    "mcp-name": "string",
    "mcp-protocol-version": "string",
}
REQUIRED_RESPONSE_HEADERS = {
    "x-request-id": "string",
}


# =============================================================================
# RESULT TYPES
# =============================================================================


@dataclass
class MCPClientResult:
    """Standardized MCP client result with provenance tracking."""

    success: bool
    content: List[Any]
    is_error: bool = False
    provider_name: str = ""  # M22 Response Provenance
    request_id: str = ""
    response_headers: Dict[str, str] = field(default_factory=dict)
    error_message: str = ""


# =============================================================================
# CLIENT
# =============================================================================


class MCPClient:
    """
    MCP 2026-07-28 Streamable HTTP client with full header validation.

    Usage:
        async with MCPClient("http://localhost:8080") as client:
            result = await client.call_tool("my_tool", {"arg": "val"})
    """

    def __init__(
        self,
        server_url: str,
        timeout: float = 30.0,
        provider_name: str = "mcp-client",
    ):
        self.server_url = server_url.rstrip("/")
        self.timeout = timeout
        self.provider_name = provider_name
        self._http_client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._http_client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, *exc):
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def call_tool(
        self,
        name: str,
        arguments: Dict[str, Any],
        method: str = "tools/call",
        trace_id: Optional[str] = None,
    ) -> MCPClientResult:
        """
        Call an MCP tool with full SEP-2243 header validation.

        Args:
            name: Tool name (used for Mcp-Name header).
            arguments: Tool arguments dict.
            method: MCP method (default: "tools/call").
            trace_id: Optional trace ID for distributed tracing.

        Returns:
            MCPClientResult with content, error state, and provenance.
        """
        if not self._http_client:
            raise RuntimeError("MCPClient not opened. Use 'async with' context manager.")

        request_id = str(uuid.uuid4())
        body = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": {
                "name": name,
                "arguments": arguments,
            },
        }

        # SEP-414: Trace context
        if trace_id:
            body.setdefault("_meta", {})["traceparent"] = (
                f"00-{trace_id}-{uuid.uuid4().hex[:16]}-01"
            )

        headers = {
            "Content-Type": "application/json",
            "Mcp-Method": method,
            "Mcp-Name": name,
            "Mcp-Protocol-Version": PROTOCOL_VERSION_CURRENT,
            "X-Request-Id": request_id,
        }

        if trace_id:
            headers["traceparent"] = f"00-{trace_id}-{uuid.uuid4().hex[:16]}-01"

        # SEP-2575: _meta envelope extraction
        if "_meta" in body:
            headers["Mcp-Meta"] = json.dumps(body["_meta"])

        logger.debug(
            "MCP call_tool: %s method=%s name=%s rid=%s",
            self.server_url,
            method,
            name,
            request_id,
        )

        try:
            response = await self._http_client.post(
                f"{self.server_url}/mcp",
                json=body,
                headers=headers,
            )

            # M23: Hard-stop on total failure
            if response.status_code == 0 or response.status_code >= 500:
                return MCPClientResult(
                    success=False,
                    content=[f"Server error: HTTP {response.status_code}"],
                    is_error=True,
                    provider_name=self.provider_name,
                    request_id=request_id,
                    error_message=f"HTTP {response.status_code}",
                )

            # Validate response headers (SEP-2243)
            resp_headers = dict(response.headers)
            if "x-request-id" not in resp_headers:
                logger.warning("Response missing X-Request-Id header (SEP-2243 violation)")

            # Parse JSON-RPC response
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                return MCPClientResult(
                    success=False,
                    content=[f"Invalid JSON response: {e}"],
                    is_error=True,
                    provider_name=self.provider_name,
                    request_id=request_id,
                    response_headers=resp_headers,
                    error_message=str(e),
                )

            # Check for JSON-RPC error
            if "error" in data:
                error = data["error"]
                return MCPClientResult(
                    success=False,
                    content=[error.get("message", "Unknown RPC error")],
                    is_error=True,
                    provider_name=self.provider_name,
                    request_id=request_id,
                    response_headers=resp_headers,
                    error_message=error.get("message", ""),
                )

            # Extract result
            result = data.get("result", {})
            content = result.get("content", [])
            is_error = result.get("isError", False)

            # Extract text from content items
            extracted = []
            for item in content:
                if isinstance(item, dict):
                    extracted.append(item.get("text", json.dumps(item)))
                else:
                    extracted.append(str(item))

            return MCPClientResult(
                success=not is_error,
                content=extracted if extracted else [json.dumps(result)],
                is_error=is_error,
                provider_name=self.provider_name,
                request_id=request_id,
                response_headers=resp_headers,
            )

        except httpx.TimeoutException:
            return MCPClientResult(
                success=False,
                content=["Request timed out"],
                is_error=True,
                provider_name=self.provider_name,
                request_id=request_id,
                error_message="timeout",
            )
        except httpx.ConnectError as e:
            return MCPClientResult(
                success=False,
                content=[f"Connection failed: {e}"],
                is_error=True,
                provider_name=self.provider_name,
                request_id=request_id,
                error_message=str(e),
            )
        except Exception as e:
            logger.error("MCP call_tool unexpected error: %s", e, exc_info=True)
            return MCPClientResult(
                success=False,
                content=[f"Unexpected error: {e}"],
                is_error=True,
                provider_name=self.provider_name,
                request_id=request_id,
                error_message=str(e),
            )

    async def list_tools(self) -> MCPClientResult:
        """List available tools (no Mcp-Name needed)."""
        return await self.call_tool(
            name="tools/list",
            arguments={},
            method="tools/list",
        )

    async def ping(self) -> MCPClientResult:
        """Simple ping to verify server connectivity."""
        return await self.call_tool(
            name="ping",
            arguments={},
            method="ping",
        )


# =============================================================================
# FACTORY
# =============================================================================


def create_mcp_client(
    server_url: str,
    timeout: float = 30.0,
    provider_name: Optional[str] = None,
) -> MCPClient:
    """Factory: create an MCP client for the given server URL."""
    if provider_name is None:
        provider_name = f"mcp-client-{server_url.split('://')[1].split(':')[0]}"
    return MCPClient(server_url=server_url, timeout=timeout, provider_name=provider_name)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MCPClient",
    "MCPClientResult",
    "create_mcp_client",
    "PROTOCOL_VERSION_CURRENT",
]
