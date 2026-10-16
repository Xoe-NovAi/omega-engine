# 🔱 MCP Core — Model Context Protocol 2026-07-28 Compliance
**AP Token**: `AP-MCP-CORE-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Reference documentation for the MCP 2026-07-28 Streamable HTTP client and compliance layer.
**Tags**: mcp, streamable-http, oauth, protocol-compliance, client
**Cross-references**: src/omega/mcp_core/client.py, src/omega/mcp_core/compliance.py, docs/architecture/ORACLE_DEEP_DIVE.md

---

## Overview

The `mcp_core` package implements the **MCP 2026-07-28** specification (Streamable HTTP + OAuth 2.1 PKCE) for the Omega Engine. It provides:

- A compliant **MCP client** with full SEP-2243 header validation
- **Protocol constants** and error codes
- **Middleware** for server-side compliance (trace context, meta envelopes, protected resource metadata)

This package is the transport foundation for all MCP tool communication in Omega.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Core Package                          │
├─────────────────────────────────────────────────────────────┤
│  client.py          │  MCPClient — Streamable HTTP client   │
│  compliance.py      │  Middleware, handlers, constants      │
│  __init__.py        │  Public exports                       │
└─────────────────────────────────────────────────────────────┘
```

**Key Design Decisions**:
- **AnyIO-only** (M1): No `asyncio` imports; all async via `anyio`
- **SEP-2243 header validation** on every request/response
- **M22 Response Provenance**: `provider_name` tracked in every result
- **M23 Failure Integrity**: Hard-stop on transport failure; no soft-failures

---

## Public API

### Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `PROTOCOL_VERSION_CURRENT` | `"2026-07-28"` | Current MCP protocol version |
| `SUPPORTED_PROTOCOL_VERSIONS` | `["2026-07-28", "2025-11-25"]` | Supported versions |
| `REQUIRED_POST_HEADERS` | `{"mcp-method", "mcp-name", "mcp-protocol-version"}` | Required request headers |
| `REQUIRED_RESPONSE_HEADERS` | `{"x-request-id"}` | Required response headers |

### MCPClientResult

Standardized result wrapper with provenance tracking.

```python
@dataclass
class MCPClientResult:
    success: bool
    content: List[Any]
    is_error: bool = False
    provider_name: str = ""          # M22: actual provider from response
    request_id: str = ""
    response_headers: Dict[str, str] = field(default_factory=dict)
    error_message: str = ""
```

### MCPClient

Main client for MCP 2026-07-28 Streamable HTTP communication.

#### Constructor

```python
MCPClient(
    server_url: str,
    timeout: float = 30.0,
    provider_name: str = "mcp-client"
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `server_url` | `str` | *Required* | Base URL of MCP server (e.g., `http://localhost:8080`) |
| `timeout` | `float` | `30.0` | Request timeout in seconds |
| `provider_name` | `str` | `"mcp-client"` | Identifier for M22 provenance tracking |

#### Methods

##### `async call_tool(name, arguments, method="tools/call", trace_id=None) -> MCPClientResult`

Call an MCP tool with full SEP-2243 header validation.

```python
async with MCPClient("http://localhost:8080") as client:
    result = await client.call_tool(
        name="search",
        arguments={"query": "sovereign AI"},
        trace_id="trace-123"
    )
    if result.success:
        print(result.content)
```

**Parameters**:
- `name`: Tool name (used for `Mcp-Name` header)
- `arguments`: Tool arguments dict
- `method`: MCP method (default: `"tools/call"`)
- `trace_id`: Optional trace ID for distributed tracing (adds `traceparent` header)

**Returns**: `MCPClientResult` with content, error state, and provenance.

##### `async list_tools() -> MCPClientResult`

List available tools (uses `tools/list` method, no `Mcp-Name` header needed).

##### `async ping() -> MCPClientResult`

Simple ping to verify server connectivity (uses `ping` method).

#### Context Manager

The client **must** be used as an async context manager:

```python
async with MCPClient("http://localhost:8080") as client:
    result = await client.call_tool("my_tool", {"arg": "value"})
# Automatic cleanup of httpx.AsyncClient
```

---

### Factory Function

```python
create_mcp_client(
    server_url: str,
    timeout: float = 30.0,
    provider_name: Optional[str] = None
) -> MCPClient
```

Convenience factory that auto-generates `provider_name` from the server URL if not provided.

---

## Compliance Layer (`compliance.py`)

The compliance module provides server-side middleware and handlers for MCP 2026-07-28 spec compliance.

### Exported Components

| Component | Type | Purpose |
|-----------|------|---------|
| `TraceContextMiddleware` | Middleware | Extracts/validates `traceparent` headers (SEP-414) |
| `MCPHeaderValidationMiddleware` | Middleware | Validates required MCP headers on every request |
| `MCPMetaEnvelopeMiddleware` | Middleware | Handles `Mcp-Meta` envelope extraction (SEP-2575) |
| `ServerDiscoverHandler` | Handler | `/.well-known/mcp` discovery endpoint |
| `ProtectedResourceMetadataHandler` | Handler | OAuth 2.1 protected resource metadata |
| `SubscriptionManager` | Class | Manages SSE subscriptions for streaming |
| `InputRequiredResult` | Type | Standardized input-required response |
| `add_cache_metadata` | Function | Adds cache headers to responses |
| `extract_mcp_param_headers` | Function | Extracts MCP param headers from request |

### Error Codes

```python
ERROR_CODES = {
    "PARSE_ERROR": -32700,
    "INVALID_REQUEST": -32600,
    "METHOD_NOT_FOUND": -32601,
    "INVALID_PARAMS": -32602,
    "INTERNAL_ERROR": -32603,
    "MCP_METHOD_NOT_ALLOWED": -32000,
    "MCP_INVALID_PROTOCOL_VERSION": -32001,
    "MCP_MISSING_REQUIRED_HEADER": -32002,
    "MCP_INVALID_META_ENVELOPE": -32003,
}
```

---

## Usage Example

```python
from omega.mcp_core import create_mcp_client, MCPClientResult

async def search_via_mcp(query: str) -> list[str]:
    """Search using an MCP server."""
    client = create_mcp_client("http://mcp-server:8080")
    
    async with client:
        # List available tools
        tools_result = await client.list_tools()
        print(f"Available tools: {tools_result.content}")
        
        # Call search tool
        result = await client.call_tool(
            name="web_search",
            arguments={"query": query, "max_results": 10},
            trace_id="search-001"
        )
        
        if not result.success:
            raise RuntimeError(f"MCP call failed: {result.error_message}")
        
        return result.content

# Usage
results = await search_via_mcp("Omega Engine architecture")
```

---

## Configuration

The client respects the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_TIMEOUT` | Global timeout override (seconds) | `30.0` |
| `MCP_PROTOCOL_VERSION` | Override protocol version | `2026-07-28` |

Server URL and authentication are configured per-client instance.

---

## Error Handling

All transport errors return `MCPClientResult` with `success=False` and `is_error=True`. The `error_message` field contains a human-readable description.

**Common error scenarios**:

| Scenario | `error_code` | `error_message` |
|----------|--------------|-----------------|
| Connection refused | `ConnectError` | `"Connection failed: ..."` |
| Request timeout | `TimeoutException` | `"Request timed out"` |
| HTTP 5xx | `HTTP 500` | `"Server error: HTTP 500"` |
| Invalid JSON response | `JSONDecodeError` | `"Invalid JSON response: ..."` |
| JSON-RPC error | RPC error code | RPC error message |
| Missing `X-Request-Id` header | (warning logged) | Result still returned |

**M23 Compliance**: The client **never** silently swallows errors. Every failure path returns a structured `MCPClientResult` with full context.

---

## Heritage & References

- [heritage: mcp 2024] MCP Protocol — Streamable HTTP + OAuth 2.1 PKCE
- [heritage: anyio 2024] M1 AnyIO — async runtime
- [heritage: httpx 2023] HTTP client

**Specification References**:
- MCP 2026-07-28 Spec
- SEP-2243 (Header Requirements)
- SEP-2575 (Meta Envelope)
- SEP-414 (Trace Context)
- OAuth 2.1 PKCE (RFC 9207)

---

## Testing

Run the MCP client tests:

```bash
pytest tests/test_mcp_client.py -v
```

Key test scenarios:
- Header validation on request/response
- Protocol version negotiation
- Error code mapping
- Provenance tracking (M22)
- Timeout and connection error handling

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ MCP_CORE-v1.0.0 ⬡ 2026-10-02 ⬡*
<!-- PROVENANCE-CORRECTED 2026-10-03T06:22:36Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

