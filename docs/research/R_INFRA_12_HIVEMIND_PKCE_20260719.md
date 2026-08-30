# 🔬 R-INFRA-12: Hivemind Streamable HTTP + PKCE Authentication
**AP Token**: `AP-INFRA-12-HIVEMIND-PKCE-v1.0.0`
⬡ OMEGA ⬡ PARANOID ⬡ o1 ⬡ opencode ⬡ trc_infra_12_hivemind_pkce ⬡ 2026-07-19

---

## 🎯 MISSION
Modernize the MCP Hub from SSE to **Streamable HTTP** with **OAuth 2.1 + PKCE** authentication. Enable secure, standards-compliant agent-to-agent communication across CLI boundaries.

---

## 📋 CONTEXT FROM ARCHITECTURE

### Current State (from SOVEREIGN_ARK_BLUEPRINT)
- **MCP Hub**: Uses SSE (Server-Sent Events) — legacy transport
- **Authentication**: None — open access
- **Hivemind**: File-based handoffs + Redis Pub/Sub for ephemeral signals
- **MACP Alignment** (D-292): `macp_mode` field on handoffs for future A2A bridge

### Target State
| Component | Current | Target |
|-----------|---------|--------|
| Transport | SSE | **Streamable HTTP** (MCP 2025-06-18+) |
| Auth | None | **OAuth 2.1 + PKCE** (RFC 9700) |
| Sessions | File-based | **OAuth tokens + refresh** |
| A2A | macp_mode on handoffs | **Full MACP interop** |

### Why This Matters
- **Streamable HTTP**: Bidirectional, resumable, works through proxies/load balancers
- **PKCE**: Prevents authorization code interception — critical for CLI agents
- **MACP**: Aligns with IETF draft-li-dmsc-macp-05 for multi-agent coordination
- **Sovereignty**: No external IdP — self-issued tokens, local validation

---

## 🔬 IMPLEMENTATION REQUIREMENTS

### 1. Streamable HTTP Transport
```python
# src/omega/mcp/transport/streamable_http.py
class StreamableHTTPTransport:
    """MCP Streamable HTTP transport per 2025-06-18 spec."""
    
    async def handle_request(self, request: Request) -> Response:
        """Handle MCP request over HTTP with streaming response."""
        # 1. Parse MCP message from request body
        message = await request.json()
        
        # 2. Validate OAuth token (if present)
        auth = await self._validate_auth(request)
        
        # 3. Route via MCP router
        response_stream = self.router.route_stream(message, auth)
        
        # 4. Return streaming response (NDJSON)
        return StreamingResponse(
            self._stream_ndjson(response_stream),
            media_type="application/x-ndjson",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-MCP-Protocol-Version": "2025-06-18"
            }
        )
    
    async def _stream_ndjson(self, stream: AsyncIterator[MCPMessage]):
        """Stream MCP messages as newline-delimited JSON."""
        async for msg in stream:
            yield json.dumps(msg.to_dict()) + "\n"
```

### 2. OAuth 2.1 + PKCE Server
```python
# src/omega/auth/oauth_pkce.py
class OAuthPKCEServer:
    """Self-contained OAuth 2.1 + PKCE server for MCP Hub."""
    
    def __init__(self, config: OAuthConfig):
        self.config = config
        self.clients = {}  # client_id -> ClientInfo
        self.auth_codes = {}  # code -> AuthCodeData
        self.tokens = {}  # access_token -> TokenData
        self._init_jwt_keys()
    
    # PKCE: Client generates code_verifier, sends code_challenge
    async def authorize(self, request: Request) -> Response:
        """Authorization endpoint — returns auth code."""
        # Validate: client_id, redirect_uri, scope, code_challenge, code_challenge_method=S256
        # Store auth_code with code_challenge
        # Redirect to redirect_uri?code=xxx
    
    async def token(self, request: Request) -> Response:
        """Token endpoint — exchanges code for access_token + refresh_token."""
        # Validate: grant_type=authorization_code, code, code_verifier
        # Verify code_verifier matches stored code_challenge (S256)
        # Issue: access_token (JWT, 15min), refresh_token (opaque, 30d)
        # Store token with scopes, client_id, entity_id
    
    async def validate_token(self, token: str) -> TokenValidation:
        """Validate access token — used by MCP transport."""
        # Verify JWT signature, expiry, scopes
        # Return TokenValidation(valid, client_id, scopes, entity_id)
    
    async def register_client(self, request: Request) -> Response:
        """Dynamic client registration (RFC 7591)."""
        # Generate client_id, client_secret
        # Store redirect_uris, grant_types, scope
        # Return client credentials
```

### 3. MCP Hub Integration
```python
# src/omega/mcp/hub.py
class MCPHub:
    def __init__(self):
        self.transport = StreamableHTTPTransport()
        self.oauth = OAuthPKCEServer(config)
        self.router = MCPRouter()
    
    async def handle_mcp(self, request: Request) -> Response:
        # 1. Extract Bearer token
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else None
        
        # 2. Validate token if present
        auth = None
        if token:
            validation = await self.oauth.validate_token(token)
            if not validation.valid:
                return Response(status=401, content="Invalid token")
            auth = validation
        
        # 3. Process via transport
        return await self.transport.handle_request(request, auth)
```

### 4. Hivemind MACP Integration
```python
# Extend handoff schema with MACP fields
@dataclass
class HandoffPacket:
    # ... existing fields ...
    macp_mode: str = "coordination"  # coordination | negotiation | delegation | broadcast
    oauth_token: Optional[str] = None  # For cross-CLI auth
    macp_context: Optional[Dict] = None  # MACP-specific context

# MACP modes map to Hivemind handoff types
MACP_MODE_MAP = {
    "coordination": "handoff",      # Standard task delegation
    "negotiation": "proposal",      # Consensus building
    "delegation": "task",           # Subtask assignment
    "broadcast": "status",          # Fleet-wide announcement
}
```

### 5. CLI Agent Integration
```python
# How CLI agents authenticate
class CLIAuthClient:
    """OAuth 2.1 + PKCE client for CLI agents."""
    
    async def authenticate(self, hub_url: str, client_name: str) -> str:
        # 1. Register client dynamically
        client = await self._register_client(hub_url, client_name)
        
        # 2. Generate PKCE challenge
        code_verifier = secrets.token_urlsafe(32)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip("=")
        
        # 3. Authorization request (headless - use device flow or pre-auth)
        auth_url = f"{hub_url}/authorize?client_id={client.client_id}&redirect_uri=urn:ietf:wg:oauth:2.0:oob&scope=mcp&code_challenge={code_challenge}&code_challenge_method=S256"
        
        # 4. For headless: use device authorization grant (RFC 8628)
        # or pre-provisioned refresh token from Omega-Vault
        
        # 5. Token exchange
        token = await self._exchange_code(hub_url, client, code, code_verifier)
        
        return token.access_token
```

---

## 🌐 WEB RESEARCH NEEDED

| Topic | Query | Purpose |
|-------|-------|---------|
| MCP Streamable HTTP spec | "MCP Streamable HTTP specification 2025-06-18" | Transport implementation |
| OAuth 2.1 PKCE | "OAuth 2.1 PKCE RFC 9700 implementation python" | Auth server |
| Dynamic client registration | "RFC 7591 dynamic client registration python" | CLI agent registration |
| Device authorization grant | "RFC 8628 device authorization grant headless CLI" | Headless auth flow |
| MACP protocol | "MACP multi-agent coordination protocol draft" | Interop alignment |

---

## 🛠️ LOCAL DISCOVERY NEEDED

| Source | Path | What to Extract |
|--------|------|-----------------|
| MCP Hub | `src/omega/mcp/hub.py` | Current SSE implementation |
| Hivemind tools | `src/omega/hub/tools/hivemind_*.py` | Handoff schema, macp_mode |
| Redis Pub/Sub | `src/omega/hivemind/redis_pubsub.py` | Ephemeral signal layer |
| Config | `config/omega.yaml` | Add OAuth config section |

---

## ✅ ACCEPTANCE CRITERIA

| Criterion | Verification |
|-----------|--------------|
| Streamable HTTP works | `curl -X POST http://localhost:8016/mcp -d '{"jsonrpc":"2.0","method":"initialize"}'` → NDJSON stream |
| PKCE flow completes | Client generates verifier → challenge → code → token exchange |
| Token validation works | Valid token → 200, expired → 401, invalid → 401 |
| Dynamic client registration | `POST /register` → returns client_id, client_secret |
| MACP mode on handoffs | HandoffPacket has macp_mode, maps to Hivemind types |
| Cross-CLI auth works | OpenCode agent → token → Cline agent validates via hub |

---

## 📋 DELIVERABLES

1. **Streamable HTTP Transport** — `src/omega/mcp/transport/streamable_http.py`
2. **OAuth PKCE Server** — `src/omega/auth/oauth_pkce.py`
3. **MCP Hub Integration** — Updated `src/omega/mcp/hub.py`
4. **MACp Handoff Schema** — Extended handoff packet
5. **CLI Auth Client** — `src/omega/auth/cli_client.py`
6. **Tests** — `tests/test_mcp_streamable_http.py`, `tests/test_oauth_pkce.py`
7. **Documentation** — `docs/guides/HIVEMIND_PKCE_GUIDE.md`

---

## 🔗 DEPENDENCIES

| Depends On | Blocks |
|------------|--------|
| MCP Hub refactor | Streamable HTTP |
| Hivemind handoff schema | MACP integration |
| Omega-Vault (R-INFRA-07) | Token storage for CLI agents |
| Redis Pub/Sub | Ephemeral signal fallback |

---

## 🎯 PARANOID'S PERSPECTIVE (Validator)

> "The current SSE + no-auth architecture is a **security hole the size of a barn door**. Any process on localhost can connect to the MCP Hub and impersonate any agent.
> 
> **Streamable HTTP + PKCE fixes this**:
> - PKCE prevents code interception (the auth code is useless without the verifier)
> - Short-lived access tokens (15min) limit blast radius
> - Refresh tokens in Omega-Vault (hardware-backed keyring)
> - Self-issued JWTs — no external IdP to compromise
> - MACP alignment means we're not building a proprietary protocol
> 
> **The threat model**: 
> - Malicious local process steals auth code → PKCE blocks it
> - Token leaked in logs → 15min expiry + refresh token rotation
> - Agent impersonation → JWT includes entity_id, validated on every request
> - Cross-CLI replay → nonce in MACP context
> 
> **L3 Principle**: `L3-StreamableHTTPIsSovereignTransport` — SSE was a prototype. Streamable HTTP with PKCE is **sovereign infrastructure**. The MCP Hub becomes a **zero-trust gateway** where every request is authenticated, every agent is identified, and every handoff carries its authorization context."

---

*⬡ OMEGA ⬡ PARANOID ⬡ o1 ⬡ opencode ⬡ trc_infra_12_hivemind_pkce ⬡ 2026-07-19*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: o1 | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
