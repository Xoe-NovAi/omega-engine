<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 R_CG01: MCP Streamable HTTP + OAuth 2.1 PKCE Implementation Audit
**AP Token**: `AP-R_CG01-MCP-AUDIT-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_mcp_audit ⬡ ACTIVE

**Date**: 2026-07-24
**Deadline**: 2026-07-28 (4 days)
**Status**: AUDIT COMPLETE — MIGRATION PLAN READY

---

## Executive Summary

The **MCP 2026-07-28 specification** (Release Candidate locked May 21, 2026; GA July 28, 2026) is the **largest revision since launch**. It transitions MCP from a stateful, session-oriented protocol to a **stateless, horizontally scalable HTTP protocol** aligned with OAuth 2.1 / OpenID Connect.

**Omega Engine Current State**: 
- Uses `mcp.server.streamable_http_manager.StreamableHTTPSessionManager` with `stateless=True` ✅
- Uses `mcp.server.sse.SseServerTransport` for legacy OpenCode/Cline clients ✅
- **CRITICAL GAPS**: Missing required headers (`Mcp-Method`, `Mcp-Name`, `MCP-Protocol-Version`), no header-body validation, no `_meta` envelope handling, no `server/discover` method, no OAuth 2.1 PKCE flow, no RFC 9728 Protected Resource Metadata, no W3C Trace Context propagation.

**Migration Effort**: ~16 hours across 4 sprints (4 days to deadline). Doable if started **today**.

---

## Part 1: Specification Delta — What Changed (2025-11-25 → 2026-07-28)

### 1.1 Breaking Changes (Must Fix Before July 28)

| # | Change | SEP | Impact | Omega Status |
|---|--------|-----|--------|--------------|
| **B1** | **Remove `initialize`/`initialized` handshake** | SEP-2575 | Clients no longer send handshake; server reads protocol version, client info, capabilities from `_meta` on every request | ❌ Not implemented |
| **B2** | **Remove `Mcp-Session-Id` header & protocol sessions** | SEP-2567 | No session affinity; any request can hit any replica; sticky routing & shared session stores obsolete | ❌ Not implemented |
| **B3** | **Require `Mcp-Method` header on ALL POST requests** | SEP-2243 | Must match `body.method`; mismatch = 400 `-32600` | ❌ Not implemented |
| **B4** | **Require `Mcp-Name` header on tool/resource/prompt calls** | SEP-2243 | Must match `params.name` or `params.uri`; mismatch = 400 `-32600` | ❌ Not implemented |
| **B5** | **Require `MCP-Protocol-Version` header on ALL requests** | Spec | Must match `_meta.io.modelcontextprotocol/protocolVersion`; mismatch = 400 `HeaderMismatch` | ❌ Not implemented |
| **B6** | **Error code `-32002` → `-32602` (Resource Not Found)** | Spec | Client code pattern-matching `-32002` will break | ❌ Not implemented |
| **B7** | **`tasks/list` removed** | Spec | Moved to Tasks extension; use `tasks/get` polling | ❌ Not implemented |
| **B8** | **HTTP+SSE transport deprecated** | SEP-2596 | Must migrate to Streamable HTTP; 12-month window | ⚠️ Still in use for OpenCode |

### 1.2 New Required Features (Must Implement)

| # | Feature | SEP | Description |
|---|---------|-----|-------------|
| **N1** | `_meta` envelope on every request/response | SEP-2575 | Carries `protocolVersion`, `clientInfo`, `clientCapabilities`, `serverInfo`, `traceparent`, `tracestate`, `baggage` |
| **N2** | `server/discover` RPC method | SEP-2575 | Returns supported protocol versions, capabilities, server identity; cacheable |
| **N3** | `ttlMs` + `cacheScope` on list/read responses | SEP-2549 | HTTP-style caching metadata for `tools/list`, `resources/list`, `resources/read` |
| **N4** | W3C Trace Context propagation | SEP-414 | `traceparent`, `tracestate`, `baggage` in `_meta` for distributed tracing |
| **N5** | `InputRequiredResult` for MRTR (Multi-Round-Trip Requests) | SEP-2322 | Replaces server-initiated requests on SSE streams |
| **N6** | `subscriptions/listen` for notifications | Spec | Long-lived SSE stream for `notifications/tools/list_changed`, etc. |
| **N7** | `x-mcp-header` tool parameter → `Mcp-Param-*` headers | SEP-2243 | Optional server annotation; clients MUST support |

### 1.3 OAuth 2.1 / OIDC Hardening (6 SEPs)

| SEP | Requirement | Client/Server |
|-----|-------------|---------------|
| SEP-2468 | **MUST** validate `iss` parameter on auth responses (RFC 9207) | Client |
| SEP-837 | Declare OIDC `application_type` during Dynamic Client Registration | Client |
| SEP-2352 | Bind credentials to issuer; re-register on issuer migration | Client |
| SEP-2207 | Formalize refresh token scope semantics for OIDC providers | Both |
| SEP-2350 | Define scope accumulation during step-up auth | Both |
| SEP-2351 | Stable `.well-known` suffix for metadata discovery | Server |

### 1.4 Deprecated (12-Month Window — Earliest Removal July 2027)

- **Roots** → Replace with explicit tool arguments
- **Sampling** → Replace with explicit tool calls
- **Logging** → Replace with structured tool outputs
- **HTTP+SSE Transport** → Migrate to Streamable HTTP
- **Dynamic Client Registration (RFC 7591)** → Prefer Client ID Metadata Documents (CIMD)

---

## Part 2: Omega Engine Current Implementation Audit

### 2.1 Transport Layer (`src/omega/mcp_runtime.py`)

```python
# CURRENT (lines 88-93)
streamable_mgr = StreamableHTTPSessionManager(
    app=mcp._mcp_server,
    json_response=mcp.settings.json_response,
    stateless=True,  # ✅ GOOD — already stateless mode
    security_settings=mcp.settings.transport_security,
)
```

**Gaps**:
| Gap | Location | Required Fix |
|-----|----------|--------------|
| No `Mcp-Method`/`Mcp-Name` header validation | `StreamableHTTPSessionManager` internals | Add middleware or subclass |
| No `_meta` envelope parsing | `mcp._mcp_server.run()` | Extract `_meta` in request handlers |
| No `server/discover` method | MCP server registration | Register `server/discover` handler |
| No `ttlMs`/`cacheScope` emission | `tools/list`, `resources/read` handlers | Add to response `_meta` |
| No W3C Trace Context propagation | N/A | Extract/inject `traceparent`/`tracestate`/`baggage` |
| No `InputRequiredResult` support | Tool handlers | Implement MRTR pattern |
| No `subscriptions/listen` endpoint | N/A | Add SSE notification stream |

### 2.2 SSE Transport (Legacy — OpenCode/Cline)

```python
# CURRENT (lines 66-80)
sse = SseServerTransport(...)
async def handle_sse(request):
    async with sse.connect_sse(...) as streams:
        await mcp._mcp_server.run(..., stateless=True)
```

**Status**: Uses `stateless=True` ✅ but still relies on deprecated HTTP+SSE transport. **Must maintain for backward compatibility** during 12-month deprecation window.

### 2.3 OAuth / Authorization — **COMPLETELY ABSENT**

| Required Component | Status |
|-------------------|--------|
| RFC 9728 Protected Resource Metadata (`.well-known/oauth-protected-resource`) | ❌ Missing |
| RFC 8414 Authorization Server Metadata discovery | ❌ Missing |
| RFC 7591 Dynamic Client Registration | ❌ Missing |
| PKCE (S256) enforcement | ❌ Missing |
| RFC 8707 Resource Indicators (`resource=` parameter) | ❌ Missing |
| `WWW-Authenticate` header on 401 | ❌ Missing |
| Token audience validation | ❌ Missing |
| Refresh token rotation | ❌ Missing |

### 2.4 Iris FastAPI Server (`src/omega/iris/server.py`)

**No MCP endpoints exposed** — Iris is a separate REST API (`/chat`, `/voice`, `/health`, `/entities`). The MCP runtime runs separately via `mcp_runtime.py`.

---

## Part 3: Migration Checklist — 16 Hours / 4 Sprints

### Sprint 1: Core Stateless Transport (4 hours) — **DAY 1 (Today)**

| Task | File | Effort | Verification |
|------|------|--------|--------------|
| **T1.1** Add `Mcp-Method`/`Mcp-Name`/`MCP-Protocol-Version` header validation middleware | `mcp_runtime.py` or new `mcp_middleware.py` | 1.5h | `curl -H "Mcp-Method: tools/call" -H "Mcp-Name: foo" -d '{"method":"tools/call","params":{"name":"bar"}}'` → 400 |
| **T1.2** Extract `_meta` envelope from request body; inject into handler context | `mcp_runtime.py` | 1h | Log `_meta` contents on each request |
| **T1.3** Implement `server/discover` method returning protocol versions, capabilities, server info | MCP server registration | 1h | `curl -d '{"method":"server/discover"}'` → valid response |
| **T1.4** Remove `Mcp-Session-Id` handling; ensure no session-store dependencies | `mcp_runtime.py` | 0.5h | Grep for `Mcp-Session-Id` → zero hits |

### Sprint 2: Caching, Tracing, MRTR (4 hours) — **DAY 2**

| Task | File | Effort | Verification |
|------|------|--------|--------------|
| **T2.1** Add `ttlMs` + `cacheScope` to `tools/list`, `resources/list`, `resources/read` responses | Tool/resource handlers | 1.5h | Response `_meta` contains `ttlMs: 300000, cacheScope: "public"` |
| **T2.2** Implement W3C Trace Context: extract `traceparent`/`tracestate`/`baggage` from `_meta`; propagate to downstream | `mcp_runtime.py` + observability | 1h | Jaeger/OTel shows continuous trace across MCP hop |
| **T2.3** Implement `InputRequiredResult` pattern for tools needing user input (MRTR) | Tool definitions | 1h | Tool returns `InputRequiredResult` → client re-calls with `inputResponses` |
| **T2.4** Add `subscriptions/listen` SSE endpoint for notifications | New route in `mcp_runtime.py` | 0.5h | `GET /mcp?listen=tools/list_changed` → SSE stream |

### Sprint 3: OAuth 2.1 PKCE Authorization (6 hours) — **DAY 3**

| Task | File | Effort | Verification |
|------|------|--------|--------------|
| **T3.1** Implement `.well-known/oauth-protected-resource` endpoint (RFC 9728) | New `oauth_metadata.py` | 1h | `GET /.well-known/oauth-protected-resource` → JSON with `authorization_servers` |
| **T3.2** Implement RFC 8414 AS Metadata discovery + RFC 7591 DCR fallback | `oauth_client.py` | 1.5h | Client discovers AS, registers dynamically |
| **T3.3** PKCE (S256) enforcement for all auth flows | `oauth_client.py` | 1h | `code_challenge_method=S256` on all `/authorize` requests |
| **T3.4** RFC 8707 Resource Indicators: include `resource=` param in auth + token requests | `oauth_client.py` | 1h | Token audience = MCP server URI |
| **T3.5** Token audience validation on server; `WWW-Authenticate` on 401 | Middleware | 1h | Invalid audience → 401 with `WWW-Authenticate` |

### Sprint 4: Deprecation Compatibility & Testing (2 hours) — **DAY 4**

| Task | File | Effort | Verification |
|------|------|--------|--------------|
| **T4.1** Maintain HTTP+SSE transport for OpenCode/Cline (12-month window) | `mcp_runtime.py` | 0.5h | OpenCode still connects via SSE |
| **T4.2** Backward compatibility: detect legacy client via 400 fallback to `initialize` | Client detection logic | 0.5h | Legacy client works; modern client uses stateless |
| **T4.3** Error code migration: `-32002` → `-32602` everywhere | Error handlers | 0.5h | Grep for `-32002` → zero hits |
| **T4.4** End-to-end test: OpenCode + Antigravity IDE + custom client | Integration test | 0.5h | All three client types work |

---

## Part 4: Code Changes — Minimal Diffs

### 4.1 New File: `src/omega/mcp_middleware.py`

```python
"""MCP 2026-07-28 Compliance Middleware.
AP: AP-MCP-MIDDLEWARE-v1.0.0
"""
# [heritage: anyio 2024] M1 AnyIO
# [heritage: mcp 2026] MCP 2026-07-28 Stateless Transport

import json
import logging
from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

logger = logging.getLogger("omega.mcp_middleware")

# MCP 2026-07-28 Required Headers
REQUIRED_HEADERS = {
    "mcp-method": "Mcp-Method",
    "mcp-name": "Mcp-Name",  # conditional
    "mcp-protocol-version": "MCP-Protocol-Version",
}

# Error codes per 2026-07-28 spec
ERROR_HEADER_MISMATCH = -32600
ERROR_UNSUPPORTED_VERSION = -32600  # UnsupportedProtocolVersionError
ERROR_RESOURCE_NOT_FOUND = -32602  # was -32002


class MCPComplianceMiddleware(BaseHTTPMiddleware):
    """Enforces MCP 2026-07-28 header requirements and _meta envelope."""

    def __init__(self, app, supported_versions: list[str] = None):
        super().__init__(app)
        self.supported_versions = supported_versions or ["2026-07-28", "2025-11-25", "2025-06-18"]

    async def dispatch(self, request: Request, call_next):
        # Only apply to MCP endpoint
        if not request.url.path.startswith("/mcp"):
            return await call_next(request)

        # 1. Validate MCP-Protocol-Version header
        proto_header = request.headers.get("mcp-protocol-version")
        if proto_header and proto_header not in self.supported_versions:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": ERROR_UNSUPPORTED_VERSION,
                        "message": f"Unsupported protocol version: {proto_header}",
                        "data": {"supported": self.supported_versions},
                    },
                },
            )

        # 2. For POST requests, validate Mcp-Method header
        if request.method == "POST":
            body = await request.body()
            try:
                json_body = json.loads(body) if body else {}
            except json.JSONDecodeError:
                return JSONResponse(
                    status_code=400,
                    content={"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}},
                )

            # Validate Mcp-Method header (REQUIRED on all POST)
            mcp_method = request.headers.get("mcp-method")
            if not mcp_method:
                return JSONResponse(
                    status_code=400,
                    content={
                        "jsonrpc": "2.0",
                        "id": json_body.get("id"),
                        "error": {"code": ERROR_HEADER_MISMATCH, "message": "Missing required header: Mcp-Method"},
                    },
                )

            if mcp_method != json_body.get("method"):
                return JSONResponse(
                    status_code=400,
                    content={
                        "jsonrpc": "2.0",
                        "id": json_body.get("id"),
                        "error": {
                            "code": ERROR_HEADER_MISMATCH,
                            "message": f"Header Mcp-Method '{mcp_method}' does not match body method '{json_body.get('method')}'",
                        },
                    },
                )

            # Validate Mcp-Name header (REQUIRED for tools/call, resources/read, prompts/get)
            if mcp_method in ("tools/call", "resources/read", "prompts/get"):
                mcp_name = request.headers.get("mcp-name")
                expected_name = None
                if mcp_method == "tools/call":
                    expected_name = json_body.get("params", {}).get("name")
                elif mcp_method == "resources/read":
                    expected_name = json_body.get("params", {}).get("uri")
                elif mcp_method == "prompts/get":
                    expected_name = json_body.get("params", {}).get("name")

                if not mcp_name:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "jsonrpc": "2.0",
                            "id": json_body.get("id"),
                            "error": {"code": ERROR_HEADER_MISMATCH, "message": f"Missing required header: Mcp-Name for {mcp_method}"},
                        },
                    )

                if mcp_name != expected_name:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "jsonrpc": "2.0",
                            "id": json_body.get("id"),
                            "error": {
                                "code": ERROR_HEADER_MISMATCH,
                                "message": f"Header Mcp-Name '{mcp_name}' does not match body params.name/uri '{expected_name}'",
                            },
                        },
                    )

            # 3. Extract _meta envelope and attach to request state for handlers
            meta = json_body.get("params", {}).get("_meta", {})
            request.state.mcp_meta = meta

            # 4. Extract W3C Trace Context from _meta
            traceparent = meta.get("traceparent")
            tracestate = meta.get("tracestate")
            baggage = meta.get("baggage")
            if traceparent:
                request.state.traceparent = traceparent
            if tracestate:
                request.state.tracestate = tracestate
            if baggage:
                request.state.baggage = baggage

        return await call_next(request)
```

### 4.2 Updated `src/omega/mcp_runtime.py` — Add Middleware & `server/discover`

```python
# ADD to imports
from omega.mcp_middleware import MCPComplianceMiddleware

# In _build_app(), BEFORE assembling routes:
# ── MCP 2026-07-28 Compliance Middleware ──────────────────────────────
app = Starlette(routes=all_routes, debug=mcp.settings.debug, lifespan=lifespan)
app.add_middleware(MCPComplianceMiddleware, supported_versions=["2026-07-28", "2025-11-25", "2025-06-18"])
return app

# ADD server/discover handler registration (in MCP server setup, not shown here):
# mcp._mcp_server.add_method("server/discover", handle_server_discover)

async def handle_server_discover(params: dict, meta: dict) -> dict:
    """SEP-2575: Stateless capability discovery."""
    return {
        "protocolVersions": ["2026-07-28", "2025-11-25", "2025-06-18"],
        "capabilities": {
            "tools": {"listChanged": True},
            "resources": {"subscribe": True, "listChanged": True},
            "prompts": {"listChanged": True},
            "logging": {},  # deprecated but still present
            "extensions": {
                "io.modelcontextprotocol/tasks": {},  # if Tasks extension enabled
            },
        },
        "serverInfo": {
            "name": "omega-engine",
            "version": "1.0.0",
        },
        "_meta": {
            "io.modelcontextprotocol/serverInfo": {"name": "omega-engine", "version": "1.0.0"},
        },
    }
```

### 4.3 Tool/Resource Response Enhancement — Add `ttlMs` + `cacheScope`

```python
# In tool list handler / resource read handler:
async def handle_tools_list(params: dict, meta: dict) -> dict:
    tools = await get_tools()
    return {
        "tools": tools,
        "_meta": {
            "ttlMs": 300000,  # 5 minutes
            "cacheScope": "public",  # or "private" for user-specific tools
        },
    }

async def handle_resources_read(params: dict, meta: dict) -> dict:
    content = await read_resource(params["uri"])
    return {
        "contents": [{"uri": params["uri"], "text": content}],
        "_meta": {
            "ttlMs": 60000,  # 1 minute
            "cacheScope": "private",
        },
    }
```

### 4.4 New File: `src/omega/oauth_metadata.py` — RFC 9728 Protected Resource Metadata

```python
"""OAuth 2.1 Protected Resource Metadata (RFC 9728) for MCP.
AP: AP-OAUTH-METADATA-v1.0.0
"""
from fastapi import APIRouter
from pydantic import BaseModel, HttpUrl
from typing import Optional, List

router = APIRouter(prefix="/.well-known", tags=["oauth"])

class ProtectedResourceMetadata(BaseModel):
    resource: HttpUrl
    authorization_servers: List[HttpUrl]
    scopes_supported: Optional[List[str]] = None
    bearer_methods_supported: Optional[List[str]] = ["header"]
    resource_documentation: Optional[HttpUrl] = None

@router.get("/oauth-protected-resource", response_model=ProtectedResourceMetadata)
async def oauth_protected_resource_metadata():
    """RFC 9728: Protected Resource Metadata for MCP Server."""
    base_url = "https://mcp.omega-engine.local"  # Configure via env
    return ProtectedResourceMetadata(
        resource=f"{base_url}/mcp",
        authorization_servers=[f"{base_url}/.well-known/oauth-authorization-server"],
        scopes_supported=["mcp.read", "mcp.write", "offline_access"],
        bearer_methods_supported=["header"],
        resource_documentation=f"{base_url}/docs/mcp-auth",
    )
```

### 4.5 New File: `src/omega/oauth_client.py` — PKCE + Resource Indicators

```python
"""MCP OAuth 2.1 Client with PKCE (S256) and RFC 8707 Resource Indicators.
AP: AP-OAUTH-CLIENT-v1.0.0
"""
import secrets
import base64
import hashlib
import httpx
from typing import Optional
from pydantic import BaseModel, HttpUrl

class PKCEChallenge(BaseModel):
    code_verifier: str
    code_challenge: str
    code_challenge_method: str = "S256"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None

def generate_pkce() -> PKCEChallenge:
    """Generate PKCE code_verifier + code_challenge (S256 mandatory per OAuth 2.1)."""
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip("=")
    return PKCEChallenge(code_verifier=code_verifier, code_challenge=code_challenge)

async def discover_authorization_server(resource_url: str) -> dict:
    """RFC 9728 → RFC 8414 discovery chain."""
    # 1. GET /.well-known/oauth-protected-resource
    async with httpx.AsyncClient() as client:
        prm_resp = await client.get(f"{resource_url}/.well-known/oauth-protected-resource")
        prm = prm_resp.json()
        as_url = prm["authorization_servers"][0]
        
        # 2. GET /.well-known/oauth-authorization-server
        as_resp = await client.get(f"{as_url}/.well-known/oauth-authorization-server")
        return as_resp.json()

async def authorize_with_pkce(
    resource_url: str,
    redirect_uri: str,
    scopes: list[str],
    client_id: Optional[str] = None,
) -> tuple[str, PKCEChallenge]:
    """Build authorization URL with PKCE + RFC 8707 resource parameter."""
    pkce = generate_pkce()
    as_meta = await discover_authorization_server(resource_url)
    
    auth_url = as_meta["authorization_endpoint"]
    params = {
        "response_type": "code",
        "client_id": client_id or "omega-mcp-client",
        "redirect_uri": redirect_uri,
        "scope": " ".join(scopes),
        "code_challenge": pkce.code_challenge,
        "code_challenge_method": "S256",
        "resource": resource_url,  # RFC 8707 Resource Indicator (MANDATORY)
        "state": secrets.token_urlsafe(32),
    }
    
    from urllib.parse import urlencode
    return f"{auth_url}?{urlencode(params)}", pkce

async def exchange_code_for_token(
    resource_url: str,
    code: str,
    pkce: PKCEChallenge,
    redirect_uri: str,
    client_id: Optional[str] = None,
) -> TokenResponse:
    """Token exchange with PKCE verifier + resource parameter."""
    as_meta = await discover_authorization_server(resource_url)
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            as_meta["token_endpoint"],
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "code_verifier": pkce.code_verifier,
                "client_id": client_id or "omega-mcp-client",
                "resource": resource_url,  # RFC 8707 (MANDATORY)
            },
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()
        return TokenResponse(**resp.json())
```

---

## Part 5: Risk Assessment & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **MCP SDK version mismatch** — Python SDK may not have 2026-07-28 support yet | High | Blocks Sprint 1 | Pin to SDK version with RC support; check `mcp` package changelog |
| **OpenCode/Cline break on SSE transport removal** | Medium | User-facing breakage | Keep HTTP+SSE for 12 months; dual-transport in `mcp_runtime.py` |
| **OAuth provider doesn't support DCR (RFC 7591)** | High | Auth flow fails | Implement Client ID Metadata Documents (CIMD) fallback per SEP-991 |
| **Antigravity IDE client doesn't send required headers** | Medium | 400 errors | Test with actual Antigravity; file bug if non-compliant |
| **W3C Trace Context not propagated by upstream SDK** | Medium | Broken distributed traces | Manual `_meta` injection in middleware as fallback |
| **Deadline slip — 4 days is tight** | High | Miss July 28 GA | Prioritize Sprint 1-2 (transport); defer OAuth to post-GA if needed |

---

## Part 6: Decision Gates

| Gate | Criteria | Owner | Deadline |
|------|----------|-------|----------|
| **G1: Transport Core** | `Mcp-Method`/`Mcp-Name` validation passes; `server/discover` works; no `Mcp-Session-Id` | @maat/P3 | 2026-07-25 EOD |
| **G2: Caching + Tracing** | `ttlMs`/`cacheScope` emitted; W3C trace context propagates | @maat/P3 | 2026-07-26 EOD |
| **G3: OAuth 2.1** | PKCE flow works end-to-end; RFC 9728 metadata served | @maat/P3 + @pillar P4 | 2026-07-27 EOD |
| **G4: Compatibility** | OpenCode (SSE) + Antigravity (Streamable HTTP) both work | @researcher | 2026-07-28 12:00 UTC |

---

## Part 7: Handoff to Implementation Team (@maat/P3)

### Deliverables This Audit Produces
1. ✅ This report: `docs/research/R_CG01_MCP_STREAMABLE_HTTP_OAUTH_AUDIT.md`
2. ✅ Migration checklist (Part 3)
3. ✅ Minimal code diffs (Part 4)
4. ✅ Risk register (Part 5)

### Required from Implementation Team
- [ ] Confirm MCP Python SDK version with 2026-07-28 RC support
- [ ] Provision OAuth authorization server (Auth0 / Keycloak / Cloudflare Workers OAuth Provider)
- [ ] Configure `.well-known` endpoints on MCP server domain
- [ ] Update `config/providers.yaml` with OAuth client credentials
- [ ] Run conformance tests against MCP test suite

### Files to Modify (Priority Order)
1. `src/omega/mcp_runtime.py` — Add middleware, `server/discover`, remove session code
2. `src/omega/mcp_middleware.py` — **NEW** compliance middleware
3. `src/omega/oauth_metadata.py` — **NEW** RFC 9728 endpoint
4. `src/omega/oauth_client.py` — **NEW** PKCE + Resource Indicators client
5. Tool/resource handlers — Add `ttlMs`/`cacheScope` to `_meta`

---

## Part 8: Appendix — Key Specification URLs

| Document | URL |
|----------|-----|
| MCP 2026-07-28 Release Candidate Blog | https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/ |
| Streamable HTTP Spec (Draft) | https://mcp-staging.mintlify.app/specification/draft/basic/transports/streamable-http |
| SEP-2567: Sessionless MCP | https://modelcontextprotocol.org/seps/2567-sessionless-mcp |
| SEP-2575: Remove Initialize Handshake | https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2575 |
| SEP-2243: HTTP Header Standardization | https://mcp.mintlify.app/seps/2243-http-standardization |
| SEP-2549: Caching Metadata | https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2549 |
| SEP-414: W3C Trace Context | https://github.com/modelcontextprotocol/modelcontextprotocol/pull/414 |
| OAuth 2.1 Draft 13 | https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13 |
| RFC 9728: Protected Resource Metadata | https://datatracker.ietf.org/doc/html/rfc9728 |
| RFC 8707: Resource Indicators | https://datatracker.ietf.org/doc/html/rfc8707 |
| RFC 9207: Issuer Validation | https://datatracker.ietf.org/doc/html/rfc9207 |
| Migration Guide (mcpmigrate.dev) | https://mcpmigrate.dev/blog/mcp-spec-2026-07-28-migration-guide |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ R_CG01 COMPLETE ⬡ 2026-07-24*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
