# 🔱 MCP 2026-07-28 Streamable HTTP Client & Middleware
**AP Token**: `AP-MCP-CLIENT-v1.0.0`
⬡ OMEGA ⬡ MAAT ⬡ TRACK-D ⬡ 2026-07-25

---

## Overview

This document describes the MCP (Model Context Protocol) 2026-07-28 Streamable HTTP implementation in the Omega Engine, including the 5-layer middleware stack, the `MCPClient` with SEP-2243 header validation, and the compliance test suite.

### Key Specifications Implemented

| Spec | Description | Status |
|------|-------------|--------|
| **MCP 2026-07-28** | Streamable HTTP transport (replaces SSE) | ✅ Implemented |
| **SEP-2243** | Header validation (Mcp-Method, Mcp-Name, Mcp-Protocol-Version) | ✅ Implemented |
| **SEP-2575** | `_meta` envelope extraction/injection | ✅ Implemented |
| **SEP-414** | Trace context propagation (traceparent/tracestate/baggage) | ✅ Implemented |
| **SEP-2549** | Cache metadata (ttlMs, cacheScope) | ✅ Implemented |
| **RFC 9728** | Protected Resource Metadata | ✅ Implemented |
| **SEP-2322** | InputRequiredResult for multi-round-trip | ✅ Implemented |

---

## 5-Layer Middleware Stack

The middleware stack in `src/omega/mcp_runtime.py` (outermost → innermost):

| Layer | Class | Purpose | Spec |
|-------|-------|---------|------|
| **1** | `RequestIDMiddleware` | Auto-generates UUID request ID; preserves client-provided `X-Request-Id` | — |
| **2** | `RateLimitHeadersMiddleware` | Adds `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` | — |
| **3** | `TraceContextMiddleware` | Propagates traceparent/tracestate/baggage per SEP-414 | SEP-414 |
| **4** | `MCPHeaderValidationMiddleware` | Validates required MCP headers per SEP-2243 | SEP-2243 |
| **5** | `MCPMetaEnvelopeMiddleware` | Extracts/injects `_meta` envelope per SEP-2575 | SEP-2575 |

### Usage

```python
from src.omega.mcp_runtime import create_mcp_runtime

app = create_mcp_runtime(
    server_name="omega-engine",
    server_version="1.0.0",
    enable_compliance=True,  # Enables layers 2-5
)
```

---

## MCPClient — SEP-2243 Validated Client

### Location
`src/omega/mcp_core/client.py`

### Quick Start

```python
from src.omega.mcp_core.client import create_mcp_client

async with create_mcp_client("http://localhost:8080", provider_name="my-client") as client:
    result = await client.call_tool("my_tool", {"arg": "value"})
    if result.success:
        print(result.content)
    else:
        print(f"Error: {result.error_message}")
```

### Features

| Feature | Description |
|---------|-------------|
| **SEP-2243 Header Validation** | Sends `Mcp-Method`, `Mcp-Name`, `Mcp-Protocol-Version` on every request |
| **M22 Response Provenance** | Every result carries `provider_name` from actual inference backend |
| **M23 Failure Integrity** | Timeouts/connection errors return `MCPClientResult(is_error=True)` — no exceptions |
| **Trace Context** | Optional `trace_id` propagates via `traceparent` header |
| **Request ID** | Auto-generates UUID per request; echoed in `X-Request-Id` response header |

### Result Type: `MCPClientResult`

```python
@dataclass
class MCPClientResult:
    success: bool
    content: List[Any]
    is_error: bool = False
    provider_name: str = ""      # M22: actual backend that responded
    request_id: str = ""         # UUID from request
    response_headers: Dict[str, str] = field(default_factory=dict)
    error_message: str = ""
```

---

## Compliance Middleware Reference

### RequestIDMiddleware

```python
from src.omega.mcp_core.compliance import RequestIDMiddleware

app.add_middleware(RequestIDMiddleware)
```

**Behavior**:
- Reads `X-Request-Id` from incoming headers
- If missing, generates `uuid.uuid4()`
- Stores in `request.state.request_id`
- Echoes in response `X-Request-Id` header

### RateLimitHeadersMiddleware

```python
from src.omega.mcp_core.compliance import RateLimitHeadersMiddleware

app.add_middleware(
    RateLimitHeadersMiddleware,
    limit=100,           # requests per window
    window_seconds=60,   # sliding window
    enabled=True,        # header-only mode (no enforcement)
)
```

**Headers Added**:
- `X-RateLimit-Limit`: Configured limit
- `X-RateLimit-Remaining`: Calculated remaining (default = limit)
- `X-RateLimit-Reset`: Unix timestamp when window resets

**Subclass for enforcement**:
```python
class EnforcingRateLimitMiddleware(RateLimitHeadersMiddleware):
    async def _get_remaining(self, request: Request) -> int:
        # Implement Redis-backed sliding window
        ...
```

### TraceContextMiddleware (SEP-414)

```python
from src.omega.mcp_core.compliance import TraceContextMiddleware

app.add_middleware(TraceContextMiddleware)
```

**Headers Processed**:
- `traceparent` — W3C trace context
- `tracestate` — Vendor-specific trace state
- `baggage` — Cross-service context

### MCPHeaderValidationMiddleware (SEP-2243)

```python
from src.omega.mcp_core.compliance import MCPHeaderValidationMiddleware

app.add_middleware(MCPHeaderValidationMiddleware, strict=True)
```

**Required Headers (POST)**:
- `Mcp-Method` — Must match `body.method`
- `Mcp-Name` — Must match `params.name` or `params.uri`
- `Mcp-Protocol-Version` — Must be in `SUPPORTED_PROTOCOL_VERSIONS`

**Required Headers (GET)**:
- `Mcp-Protocol-Version`

**Error Codes**:
| Code | Constant | Meaning |
|------|----------|---------|
| -32600 | `INVALID_REQUEST` | Missing required headers |
| -32020 | `PROTOCOL_VERSION_MISMATCH` | Unsupported protocol version |
| -32602 | `HEADER_MISMATCH` | Header/body mismatch |

### MCPMetaEnvelopeMiddleware (SEP-2575)

```python
from src.omega.mcp_core.compliance import MCPMetaEnvelopeMiddleware

app.add_middleware(
    MCPMetaEnvelopeMiddleware,
    server_info={"name": "omega-engine", "version": "1.0.0"},
)
```

**Extracts from request**: `_meta` envelope from JSON-RPC body
**Injects into response**: `_meta` with `protocolVersion`, `serverInfo`, `ttlMs`, `cacheScope`

---

## Server/Discover Handler (SEP-2575)

```python
from src.omega.mcp_core.compliance import ServerDiscoverHandler

handler = ServerDiscoverHandler(
    server_name="omega-engine",
    server_version="1.0.0",
    capabilities={
        "tools": {"listChanged": True},
        "resources": {"subscribe": True, "listChanged": True},
        "prompts": {"listChanged": True},
        "logging": {},
    },
)

result = await handler.handle({"id": "req-1", "method": "server/discover"})
```

**Returns**: Protocol versions, capabilities, server info, and `_meta` with cache metadata.

---

## Protected Resource Metadata (RFC 9728)

```python
from src.omega.mcp_core.compliance import ProtectedResourceMetadataHandler

handler = ProtectedResourceMetadataHandler(
    resource_url="https://omega-engine.local/mcp",
    auth_server_url="https://omega-engine.local/oauth",
    scopes=["mcp:tools", "mcp:resources", "mcp:prompts"],
)

response = await handler.handle(request)
```

**Returns**: OAuth 2.1 protected resource metadata for MCP endpoints.

---

## Test Suite

### Location
`tests/mcp/test_mcp_compliance.py`

### Tests (12 passing)

| Test | What It Verifies |
|------|------------------|
| `test_request_id_middleware_generates_uuid` | Auto-generates UUID when client omits header |
| `test_request_id_middleware_preserves_client_id` | Preserves client-provided `X-Request-Id` |
| `test_rate_limit_headers_middleware` | Adds `X-RateLimit-Limit/Remaining/Reset` |
| `test_header_validation_missing_protocol` | Rejects POST missing all 3 required headers |
| `test_header_validation_unsupported_version` | Rejects unsupported protocol version |
| `test_server_discover_handler` | Returns capabilities + `_meta` envelope |
| `test_protected_resource_metadata` | RFC 9728 metadata structure |
| `test_mcp_client_call_tool_returns_mcpclientresult` | **M21 Gate** — Type-checked result with provenance |
| `test_mcp_client_timeout_returns_error` | **M23** — Timeout returns error result, no exception |
| `test_extract_mcp_param_headers` | SEP-2243 `Mcp-Param-*` extraction |
| `test_input_required_result` | SEP-2322 structure |
| `test_subscription_manager` | SSE notification subscribe/notify/unsubscribe |

### Run Tests

```bash
source .venv/bin/activate && python -m pytest tests/mcp/ -v
```

---

## Dual Transport Verification

The MCP runtime supports both transports simultaneously:

| Transport | Path | Status |
|-----------|------|--------|
| **Streamable HTTP** | `/mcp` (POST) | ✅ Primary (MCP 2026-07-28) |
| **SSE** | `/sse` (GET) + `/messages` (POST) | ✅ Backward compatible |

**Test**: `tests/mcp_transport/test_streamable_http.py::TestStreamableHTTPTransport::test_mcp_runtime_supports_dual_transport` — PASSED

---

## Integration Points

| Component | File | Role |
|-----------|------|------|
| Runtime factory | `src/omega/mcp_runtime.py:create_mcp_runtime()` | Creates Starlette app with middleware stack |
| Compliance middleware | `src/omega/mcp_core/compliance.py` | 5 middleware classes + handlers |
| Client | `src/omega/mcp_core/client.py` | `MCPClient` with SEP-2243 validation |
| Tests | `tests/mcp/test_mcp_compliance.py` | 12 unit tests (no server required) |
| Transport tests | `tests/mcp_transport/` | Dual-transport integration tests |
| Matrix tests | `tests/mcp_matrix/` | OAuth + self-contained request tests |

---

## Related Documents

| Document | Purpose |
|----------|---------|
| `R_CG01_MCP_STREAMABLE_HTTP_OAUTH_AUDIT.md` | Sprint 1 audit & spec |
| `R_VAULTCORE_LEASE_PROTOCOL.md` | Lease pattern from AGY OAuth fix |
| `SOVEREIGN_MANDATES.md` | M1 AnyIO, M7 Local-First, M13 Temple-Grade, M21 Gate Integrity, M22 Provenance, M23 Failure Integrity |

---

*⬡ OMEGA ⬡ MCP-CLIENT ⬡ v1.0.0 ⬡ 2026-07-25*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: TRACK-D | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
