Here's the full picture on how omega-hub MCP is exposed:

## 🔱 omega-hub MCP Server — Exposure Map

### 1. The Server Process
- **Entrypoint**: `mcp_servers/omega_hub/server.py` — a single **FastMCP** instance (`FastMCP("Omega Core Hub", json_response=True)`) that consolidates all hub services (hivemind, library, oracle, memory, github bridge, etc.) into one endpoint.
- **Launched by**: `systemd --user` unit `omega-hub.service` (running, PID 2512, `.venv/bin/python mcp_servers/omega_hub/server.py`)
- **Runtime**: `run_mcp()` from `src/omega/mcp_runtime.py` — dual-transport ASGI app (SSE + Streamable HTTP) with 2026-07-28 MCP compliance middleware (RFC 9728 OAuth protected-resource metadata + `server/discover`).

### 2. Transport & Port
| Setting | Value |
|---|---|
| **Transport** | `OMEGA_MCP_TRANSPORT=sse` (systemd env) |
| **Port** | `OMEGA_MCP_PORT=8016` |
| **Host** | `OMEGA_MCP_HOST=127.0.0.1` (loopback only — not exposed externally) |
| **SSE endpoint** | `GET /sse` → stream, `POST /messages/` |
| **Streamable HTTP** | `POST /mcp` (JSON-RPC) |
| **Health** | `GET /health` → `{"status":"healthy","version":"2.2.0"}` ✓ (live-checked) |
| **Compliance** | `GET /.well-known/oauth-protected-resource`, RPC `server/discover` |

### 3. How Clients Connect
- **OpenCode** (project `opencode.json` → `mcp.omega-hub`): `type: "remote"`, `url: "http://127.0.0.1:8016/mcp"` — **Streamable HTTP** (this is what I'm using right now)
- **Grok CLI / other SSE clients**: legacy `http://127.0.0.1:8016/sse` (dual SSE still available)
- **Canonical registry**: `config/mcp_servers.json` mirrors the same `:8016/mcp` endpoint

### 4. Hardening (systemd unit)
- **Crash-loop circuit breaker**: `StartLimitBurst=5` in 120s → stops instead of OOM restart-storm
- **Resource ceilings**: `MemoryMax=1G`, `TasksMax=200` (cgroup-level, kills only hub not system)
- **Cleanup**: `KillMode=control-group` + SIGTERM kills firecrawl/searxng children too
- **Watchdog**: `omega-hub-watchdog.service` (anyio health monitor) active

### 5. Security Posture
- **Loopback-only** (`127.0.0.1`) — no external network exposure
- `apply_security` middleware (m9_safe decorator, taint checks via `omega.oracle.security`)
- `json_response=True` for OpenCode/Cline compatibility

---

**TL;DR**: One FastMCP server on `127.0.0.1:8016`, systemd-managed, dual-transport (SSE `/sse` + Streamable HTTP `/mcp`), loopback-only, with OOM circuit-breaker and watchdog. OpenCode talks to it via Streamable HTTP at `/mcp`; legacy clients use `/sse`.

Want me to check anything deeper — e.g. the full route list, the compliance middleware details, or the watchdog's health-check cadence?

Roc Racoon
Xoe-NovAi Omega Engine - team tech and local repo expert
