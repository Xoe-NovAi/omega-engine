# 🔱 Phase 2 Integration: FleetOrchestrator Architecture
**AP Token**: `AP-PHASE2-FLEET-ORCHESTRATOR-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_phase2_integration ⬡ ACTIVE

**Date**: 2026-07-24
**Status**: SPEC COMPLETE — Ready for Implementation
**Owner**: `@maat` / `@pillar P3` (Build), `@pillar P4` (Integration), `@pillar P7` (Context)

---

## Executive Summary

This document synthesizes **Grokster G1-15** (8-account Grok CLI rotation), **VaultCore Schema v2** (32-credential unified store), **AGY OAuth Persistence Fix** (atomic write-back), and **MCP 2026-07-28 Audit** (Streamable HTTP + OAuth 2.1 PKCE) into a single **FleetOrchestrator** implementation specification.

**Architecture Principle**: **Carmack Mode** — Max leverage, min effort. No proxy layer (deferred D-434). Direct provider calls with VaultCore-leased credentials. ACP multiplexer for Grok fleet. Unified circuit breaker (C-6').

---

## 1. FleetOrchestrator Architecture

### 1.1 Three-Layer Model (Free-Tier Adapted)

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT LAYER (Agents)                        │
│  OpenCode Agents → MCP Tool `vault_lease` → Credential Handle   │
└──────────────────────────┬──────────────────────────────────────┘
                           │ Lease Request (provider, ttl, purpose)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  CONTROL PLANE: VaultCore                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  32 Credentials: 8 AGY OAuth + 8 Grok + 8 Google + 8    │   │
│  │  OpenRouter/Exa/Firecrawl                                │   │
│  │  Schema: VaultCredential (encrypted_blob, tier, quota,   │   │
│  │  status, cooldown, lease TTL, M25 heartbeat)             │   │
│  │  Crypto: Argon2id(master_pw) → age (X25519+ChaCha20)    │   │
│  │  Quota Reconciliation: Background (OpenRouter Analytics, │   │
│  │  Exa rate-limit headers, Firecrawl credits, Grok gRPC)   │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │ Decrypted Credential + Lease Token
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA PLANE (Direct Calls)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ ModelGateway│  │ GrokFleet   │  │ MCP Runtime │             │
│  │ (Cloud)     │  │ Orchestrator│  │ (Streamable │             │
│  │             │  │ (ACP Mux)   │  │  HTTP)      │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Credential Flow

```
Agent Request
     │
     ▼
vault_lease(provider="grok", ttl=300, purpose="inference")
     │
     ▼
VaultCore.select_credential() → Quota-aware, tier-aware, cooldown-aware
     │
     ▼
VaultCore.decrypt_blob() → age decrypt (Argon2id KDF cached)
     │
     ▼
VaultCore.grant_lease(lease_id, ttl, agent_id) → M25 heartbeat starts
     │
     ▼
Agent receives: {lease_id, credential_type, decrypted_payload, expires_at}
     │
     ▼
Agent calls provider directly (ModelGateway / GrokACPClient / MCP Client)
     │
     ▼
On completion/error: Agent calls vault_release(lease_id)
     │
     ▼
VaultCore.revoke_lease() → Credential available for next agent
```

---

## 2. GrokFleetOrchestrator Specification

### 2.1 Directory Topology (Per Grokster G1-15 Part 3)

```
~/.grok-fleet/
├── acct-1/
│   ├── auth.json          # Captured via `grok login --device-auth`
│   └── config.toml        # Base config (MCP servers, strict sandbox)
├── acct-2/
│   ├── auth.json
│   └── config.toml
...
└── acct-8/
    ├── auth.json
    └── config.toml
```

### 2.2 Base `config.toml` Template (Per Account)

```toml
# ~/.grok-fleet/acct-X/config.toml
[cli]
auto_update = false
telemetry = false

[models]
default = "grok-build"

[model.grok-build]
# Force strict sandbox for cloud agents (Security Posture)
sandbox = "strict"

[features]
web_fetch = false
write_file = false
```

### 2.3 ACP Client Implementation (`src/omega/integrations/grok_cli.py`)

```python
"""
Grok ACP Client — Fleet Orchestrator Component
AP: AP-GROK-ACP-v1.0.0
M1: AnyIO — async subprocess management
M7: Local-First — Cloud agent, strict sandbox
M25: Streaming Resilience — Chunk timeout + heartbeat on ACP stream
"""
import anyio
import json
import os
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List, AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger("omega.integrations.grok_cli")


class GrokAccountState(Enum):
    ACTIVE = "active"
    EXHAUSTED = "exhausted"
    COOLING = "cooling"
    READY = "ready"
    ERROR = "error"


@dataclass
class GrokAccount:
    account_id: int  # 1-8
    home_dir: Path
    auth_path: Path
    config_path: Path
    state: GrokAccountState = GrokAccountState.READY
    quota_remaining: Optional[int] = None
    quota_total: Optional[int] = None
    quota_reset_at: Optional[datetime] = None
    last_error: Optional[str] = None
    cooldown_until: Optional[datetime] = None
    process: Optional[anyio.abc.Process] = None
    session_id: Optional[str] = None
    lease_id: Optional[str] = None  # VaultCore lease reference


@dataclass
class QuotaInfo:
    remaining: int
    total: int
    reset_at: datetime
    source: str  # "grpc-web" | "management_api" | "ACP"


class GrokACPClient:
    """
    Single-account ACP client managing `grok agent stdio` subprocess.
    Handles handshake, authentication, session lifecycle, and streaming.
    """
    
    def __init__(self, account: GrokAccount):
        self.account = account
        self._request_id = 0
        self._pending: Dict[int, asyncio.Future] = {}
        self._stdout_task: Optional[anyio.abc.Task] = None
        self._stderr_task: Optional[anyio.abc.Task] = None
    
    async def start_and_handshake(self) -> bool:
        """Spawn process and complete ACP initialize → authenticate → session/new handshake."""
        env = os.environ.copy()
        env["GROK_HOME"] = str(self.account.home_dir)
        env["GROK_SANDBOX"] = "strict"
        env["GROK_WEB_FETCH"] = "0"
        env["GROK_WRITE_FILE"] = "0"
        
        try:
            self.account.process = await anyio.open_process(
                ["grok", "--no-auto-update", "agent", "stdio"],
                env=env,
                stdin=anyio.subprocess.PIPE,
                stdout=anyio.subprocess.PIPE,
                stderr=anyio.subprocess.STDOUT,
            )
        except Exception as e:
            logger.error(f"Failed to spawn grok agent stdio for acct-{self.account.account_id}: {e}")
            self.account.state = GrokAccountState.ERROR
            self.account.last_error = str(e)
            return False
        
        # Start stdout reader
        self._stdout_task = anyio.create_task_group().start_soon(self._read_stdout)
        
        # 1. Initialize
        init_req = {
            "jsonrpc": "2.0", "id": self._next_id(), "method": "initialize",
            "params": {
                "protocolVersion": "1",
                "clientCapabilities": {"fs": {"readTextFile": True}, "terminal": False}
            }
        }
        init_res = await self._send_and_wait(init_req)
        if not init_res or "error" in init_res:
            logger.error(f"ACP initialize failed: {init_res}")
            return False
        
        # 2. Authenticate
        auth_methods = [m["id"] for m in init_res.get("result", {}).get("authMethods", [])]
        method_id = "xai.api_key" if "xai.api_key" in auth_methods else "cached_token"
        
        auth_req = {
            "jsonrpc": "2.0", "id": self._next_id(), "method": "authenticate",
            "params": {"methodId": method_id, "_meta": {"headless": True}}
        }
        auth_res = await self._send_and_wait(auth_req)
        if not auth_res or "error" in auth_res:
            logger.error(f"ACP authenticate failed: {auth_res}")
            return False
        
        # 3. Create Session
        sess_req = {
            "jsonrpc": "2.0", "id": self._next_id(), "method": "session/new",
            "params": {"_meta": {"headless": True}}
        }
        sess_res = await self._send_and_wait(sess_req)
        if not sess_res or "error" in sess_res:
            logger.error(f"ACP session/new failed: {sess_res}")
            return False
        
        self.account.session_id = sess_res.get("result", {}).get("sessionId")
        self.account.state = GrokAccountState.ACTIVE
        logger.info(f"Grok acct-{self.account.account_id} ACP handshake complete, session={self.account.session_id}")
        return True
    
    async def _read_stdout(self):
        """Read JSON-RPC frames from stdout, dispatch to pending futures or handle notifications."""
        async for line in self.account.process.stdout:
            line = line.decode().strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                logger.warning(f"Non-JSON output from grok acct-{self.account.account_id}: {line[:100]}")
                continue
            
            # Response to our request
            if "id" in msg and msg["id"] in self._pending:
                fut = self._pending.pop(msg["id"])
                if not fut.done():
                    fut.set_result(msg)
            # Notification (quota update, error, etc.)
            elif "method" in msg:
                await self._handle_notification(msg)
    
    async def _handle_notification(self, msg: Dict[str, Any]):
        """Handle ACP notifications: quota updates, mid-stream errors, session events."""
        method = msg.get("method")
        params = msg.get("params", {})
        
        if method == "x.ai/quota":
            # Quota update notification
            self.account.quota_remaining = params.get("remaining")
            self.account.quota_total = params.get("total")
            if params.get("resetAt"):
                self.account.quota_reset_at = datetime.fromisoformat(params["resetAt"].replace("Z", "+00:00"))
            logger.debug(f"Grok acct-{self.account.account_id} quota: {self.account.quota_remaining}/{self.account.quota_total}")
        
        elif method == "x.ai/usageExhausted":
            # Mid-stream exhaustion — CRITICAL for rotation
            logger.warning(f"Grok acct-{self.account.account_id} MID-STREAM EXHAUSTION: {params}")
            self.account.state = GrokAccountState.EXHAUSTED
            self.account.cooldown_until = datetime.utcnow() + timedelta(seconds=300)  # 5 min cooldown
            self.account.last_error = params.get("message", "Usage balance exhausted")
            # TODO: Signal FleetOrchestrator for mid-stream recovery
        
        elif method == "notifications/session/ended":
            logger.info(f"Grok acct-{self.account.account_id} session ended")
            self.account.state = GrokAccountState.READY
            self.account.session_id = None
    
    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id
    
    async def _send_and_wait(self, request: Dict[str, Any], timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        req_id = request["id"]
        fut = asyncio.get_event_loop().create_future()
        self._pending[req_id] = fut
        
        try:
            await self.account.process.stdin.send((json.dumps(request) + "\n").encode())
            return await anyio.wait_all([anyio.sleep(timeout), fut])
        except Exception as e:
            logger.error(f"ACP send failed: {e}")
            return None
        finally:
            self._pending.pop(req_id, None)
    
    async def prompt(self, text: str, model: str = "grok-build") -> AsyncIterator[str]:
        """Send prompt via ACP session/update, yield streaming response chunks."""
        if not self.account.session_id:
            raise RuntimeError("No active session")
        
        req = {
            "jsonrpc": "2.0", "id": self._next_id(), "method": "session/update",
            "params": {
                "sessionId": self.account.session_id,
                "prompt": {"text": text, "model": model},
                "_meta": {"stream": True}
            }
        }
        
        await self.account.process.stdin.send((json.dumps(req) + "\n").encode())
        
        # Stream responses via notifications
        # Note: Actual streaming handled via _handle_notification for "session/update" responses
        # This is a simplified interface; full impl needs chunk collection
        yield "STREAMING_NOT_IMPLEMENTED_IN_SPEC"
    
    async def check_quota(self) -> QuotaInfo:
        """Poll quota via gRPC-web GetGrokCreditsConfig (primary) or ACP notification."""
        # Primary: gRPC-web call to xAI billing endpoint
        # Fallback: ACP notification cache
        if self.account.quota_remaining is not None:
            return QuotaInfo(
                remaining=self.account.quota_remaining,
                total=self.account.quota_total or 0,
                reset_at=self.account.quota_reset_at or datetime.utcnow(),
                source="ACP"
            )
        # TODO: Implement gRPC-web call
        return QuotaInfo(remaining=0, total=0, reset_at=datetime.utcnow(), source="unknown")
    
    async def shutdown(self):
        if self._stdout_task:
            self._stdout_task.cancel()
        if self.account.process:
            self.account.process.terminate()
            await self.account.process.wait()


class GrokFleetOrchestrator:
    """
    Manages 8 Grok ACP clients with quota-aware rotation.
    Integrates with VaultCore for credential leasing.
    State machine: ACTIVE → EXHAUSTED → COOLING (300s) → READY
    """
    
    def __init__(self, vault_client=None):
        self.accounts: List[GrokAccount] = []
        self.clients: Dict[int, GrokACPClient] = {}
        self.current_account_idx = 0
        self.vault_client = vault_client
        self._rotation_lock = anyio.Lock()
    
    async def initialize(self, fleet_dir: Path = Path.home() / ".grok-fleet"):
        """Initialize all 8 accounts from fleet directory."""
        for i in range(1, 9):
            acct_dir = fleet_dir / f"acct-{i}"
            account = GrokAccount(
                account_id=i,
                home_dir=acct_dir,
                auth_path=acct_dir / "auth.json",
                config_path=acct_dir / "config.toml",
            )
            self.accounts.append(account)
            client = GrokACPClient(account)
            self.clients[i] = client
            
            # Attempt handshake
            success = await client.start_and_handshake()
            if not success:
                logger.warning(f"Grok acct-{i} handshake failed, will retry on demand")
        
        # Start background quota poller
        anyio.create_task_group().start_soon(self._quota_poller)
    
    async def _quota_poller(self):
        """Background task: poll quota every 60s via gRPC-web."""
        while True:
            await anyio.sleep(60)
            for account in self.accounts:
                if account.state == GrokAccountState.ACTIVE:
                    client = self.clients[account.account_id]
                    try:
                        quota = await client.check_quota()
                        account.quota_remaining = quota.remaining
                        account.quota_total = quota.total
                        account.quota_reset_at = quota.reset_at
                        
                        # Check for exhaustion
                        if quota.remaining <= 0:
                            account.state = GrokAccountState.EXHAUSTED
                            account.cooldown_until = datetime.utcnow() + timedelta(seconds=300)
                    except Exception as e:
                        logger.warning(f"Quota poll failed for acct-{account.account_id}: {e}")
    
    def _select_next_account(self) -> Optional[GrokAccount]:
        """Quota-ranked fallback: tightest remaining % first, then circular."""
        now = datetime.utcnow()
        candidates = []
        
        for account in self.accounts:
            if account.state == GrokAccountState.COOLING:
                if account.cooldown_until and now >= account.cooldown_until:
                    account.state = GrokAccountState.READY
                else:
                    continue
            if account.state in (GrokAccountState.READY, GrokAccountState.ACTIVE):
                candidates.append(account)
        
        if not candidates:
            return None
        
        # Rank by quota remaining % (ascending = tightest first)
        def quota_pct(a: GrokAccount) -> float:
            if a.quota_total and a.quota_total > 0:
                return a.quota_remaining / a.quota_total
            return 1.0  # Unknown = lowest priority
        
        candidates.sort(key=quota_pct)
        return candidates[0]
    
    async def get_active_client(self) -> Optional[GrokACPClient]:
        """Get the best available client, rotating if needed."""
        async with self._rotation_lock:
            account = self._select_next_account()
            if not account:
                logger.error("No available Grok accounts")
                return None
            
            client = self.clients[account.account_id]
            
            # If account is READY but not handshaken, handshake now
            if account.state == GrokAccountState.READY and not account.session_id:
                success = await client.start_and_handshake()
                if not success:
                    account.state = GrokAccountState.ERROR
                    return await self.get_active_client()  # Recurse to next
            
            return client
    
    async def prompt_with_rotation(self, text: str, model: str = "grok-build") -> AsyncIterator[str]:
        """
        Send prompt with automatic rotation on 402/mid-stream exhaustion.
        Implements mid-stream recovery: capture partial, swap account, replay.
        """
        max_retries = 3
        partial_response = ""
        
        for attempt in range(max_retries):
            client = await self.get_active_client()
            if not client:
                raise RuntimeError("No available Grok accounts")
            
            try:
                async for chunk in client.prompt(text + partial_response, model):
                    # Check for mid-stream exhaustion in chunk
                    if "usage balance exhausted" in chunk.lower() or "402" in chunk:
                        logger.warning(f"Mid-stream exhaustion detected on acct-{client.account.account_id}")
                        client.account.state = GrokAccountState.EXHAUSTED
                        client.account.cooldown_until = datetime.utcnow() + timedelta(seconds=300)
                        partial_response = chunk  # Capture partial for replay
                        break  # Break inner loop, retry outer
                    yield chunk
                else:
                    # Normal completion
                    return
            except Exception as e:
                logger.error(f"Prompt failed on acct-{client.account.account_id}: {e}")
                client.account.state = GrokAccountState.ERROR
                client.account.last_error = str(e)
                continue
        
        raise RuntimeError("All Grok accounts exhausted or failed")
    
    async def shutdown_all(self):
        for client in self.clients.values():
            await client.shutdown()
```

---

## 3. VaultCore Integration for Grok Credentials

### 3.1 Extended Credential Types (Add to `VaultCredential`)

```python
# In src/omega/vault/models.py — extend CredentialType enum
class CredentialType(str, Enum):
    OAUTH = "oauth"           # AGY: access_token + refresh_token
    API_KEY = "api_key"       # OpenRouter, Exa, Firecrawl
    GCP_SA = "gcp_sa"         # Google Service Account JSON
    GROK_AUTH = "grok_auth"   # Grok CLI auth.json blob
    GROK_CONFIG = "grok_config"  # Grok CLI config.toml blob (NEW)
```

### 3.2 Grok Credential Payload Structure

```python
# Decrypted payload for GROK_AUTH
{
    "type": "grok_auth",
    "account_id": 3,
    "auth_json": {
        "access_token": "eyJ...",
        "refresh_token": "eyJ...",
        "expires_at": "2026-07-25T12:00:00Z",
        "scopes": ["grok.build", "grok.api"]
    },
    "config_toml": "[cli]\nauto_update = false\n..."
}

# Decrypted payload for GROK_CONFIG (optional separate blob)
{
    "type": "grok_config",
    "account_id": 3,
    "config_toml": "[cli]\nauto_update = false\n..."
}
```

### 3.3 VaultCore Lease Protocol for Grok

```python
# When FleetOrchestrator needs a Grok credential:
async def lease_grok_credential(vault, account_id: int) -> Dict[str, Any]:
    """Lease a Grok credential from VaultCore."""
    lease_req = VaultLeaseRequest(
        agent_id="grok-fleet-orchestrator",
        provider="grok",
        key_id=f"grok-{account_id}",
        ttl_seconds=300,
        purpose="acp_session"
    )
    lease = await vault.lease_credential(lease_req)
    
    # Decrypt payload
    credential = await vault.get_credential("grok", f"grok-{account_id}")
    decrypted = await vault.decrypt(credential.encrypted_blob)
    
    return {
        "lease_id": lease.lease_id,
        "account_id": account_id,
        "auth_json": decrypted["auth_json"],
        "config_toml": decrypted.get("config_toml", ""),
        "expires_at": lease.lease_expires_at
    }
```

---

## 4. AGY OAuth Persistence Fix Integration

### 4.1 Atomic Write-Back Pattern (From `R_AGY_OAUTH_PERSISTENCE_FIX.md`)

```python
# src/omega/agents/scribe/agy_oauth_persistence.py — ALREADY IMPLEMENTED
# Key pattern: temp file + fsync + atomic rename

async def save(self, accounts: Dict[str, Any]) -> None:
    fd, temp_path = tempfile.mkstemp(dir=self.config_path.parent, suffix=".tmp")
    try:
        os.write(fd, json.dumps(accounts, indent=2).encode())
        os.fsync(fd)
        os.close(fd)
        os.rename(temp_path, self.config_path)  # Atomic on POSIX
    except Exception:
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise
```

### 4.2 Integration with VaultCore

The AGY OAuth fix validates the **atomic write pattern** that becomes the foundation for **VaultCore lease protocol**:

| AGY OAuth Fix | VaultCore Lease Protocol |
|---------------|-------------------------|
| `antigravity-accounts.json` | `vault_credentials.db` (SQLite) |
| Token refresh callback | Lease grant/revoke callbacks |
| Atomic write (tmp → fsync → rename) | Atomic lease state transitions |
| Crash-safe persistence | Crash-safe lease recovery (TTL expiry) |

**Implementation**: The `AntigravityTokenStore` class in `agy_oauth_persistence.py` is the **reference implementation** for VaultCore's credential persistence layer.

---

## 5. MCP 2026-07-28 Compliance Integration

### 5.1 Required Changes to `src/omega/mcp_runtime.py`

From `R_CG01_MCP_STREAMABLE_HTTP_OAUTH_AUDIT.md` — Sprint 1 (Transport Core, deadline Jul 28):

```python
# ADD: Middleware for header validation
class MCPHeaderValidationMiddleware:
    """Validates Mcp-Method, Mcp-Name, MCP-Protocol-Version headers per SEP-2243."""
    
    REQUIRED_HEADERS = {
        "POST": ["Mcp-Method", "Mcp-Name", "MCP-Protocol-Version"],
        "GET": ["MCP-Protocol-Version"],
    }
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        method = scope["method"]
        headers = {k.decode().lower(): v.decode() for k, v in scope.get("headers", [])}
        
        # Validate required headers
        for required in self.REQUIRED_HEADERS.get(method, []):
            if required.lower() not in headers:
                await self._send_error(send, 400, -32600, f"Missing required header: {required}")
                return
        
        # Validate Mcp-Method matches body.method
        if method == "POST" and "mcp-method" in headers:
            # Need to peek body — buffer first chunk
            pass  # Implementation in Sprint 1
        
        await self.app(scope, receive, send)
```

### 5.2 `_meta` Envelope Handling

```python
# ADD: _meta extraction and injection
def extract_meta(request_body: Dict[str, Any]) -> Dict[str, Any]:
    """Extract _meta envelope from request per SEP-2575."""
    return request_body.get("_meta", {})

def inject_meta(response_body: Dict[str, Any], meta: Dict[str, Any]) -> Dict[str, Any]:
    """Inject _meta envelope into response."""
    response_body["_meta"] = {
        "protocolVersion": meta.get("protocolVersion", "2026-07-28"),
        "serverInfo": {"name": "omega-engine", "version": "1.0.0"},
        "traceparent": meta.get("traceparent"),
        "tracestate": meta.get("tracestate"),
        "baggage": meta.get("baggage"),
    }
    return response_body
```

### 5.3 `server/discover` Method Registration

```python
# ADD: server/discover handler
async def handle_server_discover(request: Dict[str, Any]) -> Dict[str, Any]:
    """SEP-2575: Returns supported protocol versions, capabilities, server identity."""
    return {
        "jsonrpc": "2.0",
        "id": request["id"],
        "result": {
            "protocolVersions": ["2026-07-28", "2025-11-25"],
            "capabilities": {
                "tools": {"listChanged": True},
                "resources": {"subscribe": True, "listChanged": True},
                "prompts": {"listChanged": True},
                "logging": {},
            },
            "serverInfo": {"name": "omega-engine", "version": "1.0.0"},
            "instructions": "Omega Engine MCP Server — Dual transport (SSE + Streamable HTTP)",
        }
    }
```

### 5.4 RFC 9728 Protected Resource Metadata Endpoint

```python
# ADD: /.well-known/oauth-protected-resource endpoint
async def handle_protected_resource_metadata(request):
    """RFC 9728: OAuth 2.1 Protected Resource Metadata."""
    from starlette.responses import JSONResponse
    return JSONResponse({
        "resource": "https://omega-engine.local/mcp",
        "authorization_servers": ["https://omega-engine.local/oauth"],
        "bearer_methods_supported": ["header"],
        "scopes_supported": ["mcp:tools", "mcp:resources", "mcp:prompts"],
        "resource_documentation": "https://omega-engine.local/docs/mcp",
    })
```

---

## 6. Unified Circuit Breaker (C-6') Integration

Per Grokster directive: **Do not build a new circuit breaker. Integrate into unified breaker (Ticket C-6').**

### 6.1 Breaker Trip Conditions (Extended)

```python
# In src/omega/oracle/breaker.py (unified)
class BreakerTripCondition(Enum):
    RATE_LIMIT = "rate_limit"           # 429 from any provider
    AUTH_FAILURE = "auth_failure"       # 401/403
    QUOTA_EXHAUSTED = "quota_exhausted" # 402 / "usage balance exhausted"
    TIMEOUT = "timeout"                 # Chunk timeout (M25)
    OOM = "oom"                         # Out of memory
    STREAM_ERROR = "stream_error"       # Mid-stream error (ACP/SSE)
```

### 6.2 Grok-Specific Breaker Config

```python
GROK_BREAKER_CONFIG = {
    "failure_threshold": 3,
    "success_threshold": 2,
    "timeout_seconds": 300,  # 5 min cooldown matches Grok rotation
    "trip_conditions": [
        BreakerTripCondition.QUOTA_EXHAUSTED,
        BreakerTripCondition.STREAM_ERROR,
        BreakerTripCondition.RATE_LIMIT,
    ],
    "on_trip": "rotate_account",  # Custom action: trigger fleet rotation
}
```

---

## 7. Implementation Sequence (Carmack Mode)

### Sprint 1 (TODAY — Jul 24): MCP Transport Core
- [ ] `src/omega/mcp_runtime.py` — Header validation middleware
- [ ] `src/omega/mcp_runtime.py` — `_meta` envelope extraction/injection
- [ ] `src/omega/mcp_runtime.py` — `server/discover` method registration
- [ ] `src/omega/mcp_runtime.py` — RFC 9728 `/.well-known/oauth-protected-resource`
- [ ] Tests: Header validation, `_meta` round-trip, discover response

### Sprint 2 (Jul 25): OAuth 2.1 PKCE + Server/Discover
- [ ] PKCE client implementation (code_verifier, code_challenge)
- [ ] Dynamic Client Registration (RFC 7591) or CIMD
- [ ] Token validation with `iss` parameter (SEP-2468)
- [ ] Refresh token scope semantics (SEP-2207)

### Sprint 3 (Jul 26): VaultCore MVP + GrokFleetOrchestrator
- [ ] `src/omega/vault/models.py` — Extended credential types
- [ ] `src/omega/vault/core.py` — Lease protocol, Argon2id+age crypto
- [ ] `src/omega/integrations/grok_cli.py` — Full ACP client + FleetOrchestrator
- [ ] Integration: VaultCore → GrokFleetOrchestrator credential leasing

### Sprint 4 (Jul 27): AGY OAuth Fix + Search Router + Soul Privacy
- [ ] `src/omega/agents/scribe/agy_oauth_persistence.py` — Deploy fix
- [ ] `src/omega/oracle/search_router.py` — 5-tier router (R_CG07)
- [ ] `src/omega/memory/soul_privacy.py` — PUBLIC/BONDED/PRIVATE split (R19)

### Sprint 5 (Jul 28): MCP Compliance Verification
- [ ] Full MCP 2026-07-28 test suite
- [ ] OpenCode/Cline compatibility verification
- [ ] Antigravity IDE Streamable HTTP test
- [ ] Documentation update

---

## 8. Dependencies & Blockers

| Component | Depends On | Blocks |
|-----------|------------|--------|
| GrokFleetOrchestrator | V-1 VaultCore MVP (credential leasing) | Grok 8-account fleet |
| VaultCore MVP | AGY OAuth fix (atomic write pattern) | All credential leasing |
| MCP Sprint 1 | None (start TODAY) | MCP Sprint 2-5 |
| Search Router (R_CG07) | None | R01/R10 research (Week 2) |
| Soul Privacy (R19) | None | R30 Identity Phase 0 (Week 4) |

---

## 9. Testing Strategy

### 9.1 Unit Tests
- `test_grok_acp_client.py` — Handshake, prompt, quota, shutdown
- `test_grok_fleet_orchestrator.py` — Rotation, quota ranking, mid-stream recovery
- `test_vault_core.py` — Lease grant/revoke, encryption, TTL expiry
- `test_mcp_headers.py` — Header validation, `_meta` round-trip

### 9.2 Integration Tests
- `test_grok_vault_integration.py` — Lease Grok cred → spawn ACP client → prompt
- `test_mcp_compliance.py` — Full MCP 2026-07-28 spec compliance
- `test_agy_oauth_persistence.py` — Restart survival, token refresh write-back

### 9.3 Property Tests (C-11)
- `test_breaker_properties.py` — State machine invariants
- `test_lease_properties.py` — No double-lease, TTL expiry, revocation

---

## 10. Reference Links

| Document | Location |
|----------|----------|
| Grokster G1-15 Part 1 | `data/coordination/GROKSTER_G1_15_RESEARCH_REPORT_20260723_PART1.md` |
| Grokster G1-15 Part 2 (Insights) | `data/coordination/GROKSTER_G1_15_RESEARCH_REPORT_20260723_PART2_INSIGHTS.md` |
| Grokster G1-15 Part 3 (Specs) | `data/coordination/GROKSTER_G1_15_RESEARCH_REPORT_20260723_PART3_SPECS.md` |
| VaultCore Schema v2 | `docs/research/R_VAULT_SCHEMA_V2.md` |
| AGY OAuth Persistence Fix | `docs/research/R_AGY_OAUTH_PERSISTENCE_FIX.md` |
| MCP 2026-07-28 Audit | `docs/research/R_CG01_MCP_STREAMABLE_HTTP_OAUTH_AUDIT.md` |
| Soul Privacy Model | `docs/research/R_SOUL_PRIVACY_MODEL.md` |
| Sovereign Search 5-Tier | `docs/research/R_CG07_SOVEREIGN_SEARCH_5TIER.md` |
| Agent-Safe Credential Vault | `docs/research/R_CG04_AGENT_SAFE_CREDENTIAL_VAULT.md` |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_phase2_integration ⬡ SPEC COMPLETE*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
