# 🔱 MCP Server Hardening Audit — Comprehensive Report
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ big-pickle ⬡ opencode ⬡ trc_mcp_audit ⬡ HARDENING

**AP Token**: AP-MCP-HARDENING-AUDIT-v1.0.0
**Date**: 2026-06-17
**Auditor**: roc_racoon (Sovereign Miner)
**Scope**: All MCP servers, systemd registrations, opencode.json, config files

---

## §1 MCP Server Inventory

### 1.1 Active MCP Servers

| # | Name | Port | Type | Transport | Status | opencode.json | systemd |
|---|------|------|------|-----------|--------|---------------|---------|
| 1 | **omega-hub** | 8016 | `remote` | SSE | ✅ RUNNING | ✅ `remote` | ✅ `omega-hub.service` (disabled) |
| 2 | **SearXNG MCP** | 8018 | `remote` | SSE | ✅ RUNNING | ✅ `remote` | ✅ `omega-searxng-mcp.service` (disabled) |
| 3 | **SearXNG Backend** | 8017 | container | HTTP | ❌ STOPPED | N/A | ✅ `omega-searxng.service` (inactive) |
| 4 | **Firecrawl** | N/A | `local` | stdio | ✅ REGISTERED | ✅ `local` | N/A (wrapper script) |
| 5 | **Exa** | N/A | `remote` | HTTPS | ✅ REGISTERED | ✅ `remote` | N/A (cloud) |

### 1.2 Dead/Stale MCP Services

| # | Name | Status | Cause | Port |
|---|------|--------|-------|------|
| 1 | **omega-stats** | ❌ FAILED | `mcp/omega-stats/server.py` not found (consolidated into hub) | 8012 (socket) |
| 2 | **omega-stats.socket** | ❌ FAILED | Activating failed service via socket activation | 8012 |
| 3 | **omega-research** | ❌ FAILED | Import chain broken in orchestrator.py (consolidated into hub) | N/A (timer) |

### 1.3 Infrastructure (Podman) Containers

| Name | Status | Ports |
|------|--------|-------|
| omega-infra-infra | ✅ Up 6h | 6333, 8080, 8088 |
| omega-caddy | ✅ Up 6h (healthy) | 6333, 8080, 8088, 443 |
| omega-postgres | ✅ Up 6h (healthy) | 6333, 8080, 8088, 5432 |
| omega-qdrant | ✅ Up 6h (healthy) | 6333, 8080, 8088, 6334 |

**SearXNG container not running** — `omega-searxng.service` shows inactive, no podman container for it.

---

## §2 CRITICAL Findings

### C-1: Permission Denied on Metrics Write (ACTIVE FAILURE)

**Severity**: 🔴 CRITICAL
**File**: `mcp_servers/omega_hub/background.py:61`
**Log evidence**:
```
ERROR Awareness pruning failed: [Errno 13] Permission denied:
'/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/coordination/metrics.json.tmp'
```

**Root cause**: The `data/coordination/` directory tree is owned by UID **100999** (podman subuid mapping), but the omega-hub service runs as UID **1000**. The `_write_metrics()` function in `background.py` fails every 60 seconds trying to write `metrics.json.tmp`.

```
UID 1000 (systemd service) → CAN'T WRITE → UID 100999 (podman-chowned dir)
```

**Diagnosis**: The `100999` ownership is from the **Mandate 6 (`:U` flag) violation pattern**. At some point, a podman container with `:U` on a volume mount chowned the coordination directory. This is the exact same root cause that `R_PODMAN_SOVEREIGN_V2.md` documents.

**Fix**:
```bash
sudo chown -R 1000:1000 /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/coordination/
```

**Verification**: After fix, monitor `journalctl --user -u omega-hub.service -n 50` for no more Permission denied errors.

---

### C-2: omega-stats Service — Stale Reference to Consolidated Path

**Severity**: 🔴 CRITICAL
**File**: `~/.config/systemd/user/omega-stats.service`
**Evidence**:
```
ExecStart=.../mcp/omega-stats/server.py  ← PATH DOES NOT EXIST
```

**Root cause**: The omega-stats MCP was consolidated into the omega-hub (Decision 050), but the systemd service still points to the old `mcp/omega-stats/server.py` path. The `omega-stats.socket` (port 8012) activates this service on connection, generating repeated failures.

**API key exposure in service file**: The service file contains **3 API keys in plaintext** in the `Environment=` lines:
- `BRAVE_API_KEY=[REDACTED-GITLEAKS-GENERIC-API-KEY]`
- `EXA_API_KEY=[REDACTED-GITLEAKS-GENERIC-API-KEY]`
- `TAVILY_API_KEY=[REDACTED-GITLEAKS-GENERIC-API-KEY]`

**Fix**:
```bash
systemctl --user stop omega-stats.service omega-stats.socket
systemctl --user disable omega-stats.service omega-stats.socket
rm ~/.config/systemd/user/omega-stats.service ~/.config/systemd/user/omega-stats.socket
systemctl --user daemon-reload
```

**Verification**: `systemctl --user list-units --state=failed` no longer shows omega-stats.

---

### C-3: omega-research Service — Stale (Consolidated into Hub)

**Severity**: 🔴 CRITICAL
**File**: `~/.config/systemd/user/omega-research.service`
**Evidence**: Timer-triggered service crashes with import error in orchestrator.py.

**Root cause**: The research engine was consolidated into the hub. The `omega-research.timer` still activates this service periodically, generating repeated failures in the journal.

**Fix**:
```bash
systemctl --user stop omega-research.service omega-research.timer
systemctl --user disable omega-research.service omega-research.timer
rm ~/.config/systemd/user/omega-research.service ~/.config/systemd/user/omega-research.timer
systemctl --user daemon-reload
```

**Verification**: `systemctl --user list-units --state=failed` no longer shows omega-research.

---

### C-4: SearXNG Container Not Running

**Severity**: 🔴 CRITICAL
**Evidence**: `omega-searxng.service` shows inactive/dead. No podman container for searxng exists.

**Root cause**: The SearXNG backend container (required by the MCP proxy on port 8018) is stopped. The MCP proxy (`omega-searxng-mcp.service`) is running but will fail on any actual search query with connection errors.

**Fix**:
```bash
systemctl --user start omega-searxng.service
# Verify:
podman ps | grep searxng
curl -sf http://localhost:8017/healthz
```

**Verification**: `curl -sf http://localhost:8017/healthz` returns 200.

---

## §3 HIGH Severity Findings

### H-1: SearXNG MCP — Missing `@m9_safe` Error Boundary

**Severity**: 🟠 HIGH
**File**: `mcp_servers/searxng/server.py`
**Issue**: The `searxng_search` tool function lacks the `@m9_safe` decorator. It catches exceptions with bare `except Exception as e:` and returns the error as a plain string (not a typed `CallToolResult(isError=True)`).

**Current code** (line 53):
```python
except Exception as e:
    return f"Error connecting to SearXNG: {str(e)}"
```

**This violates M9 (Error Integrity)** — errors should be typed and traceable.

**Fix**: Add `@m9_safe("searxng_search")` decorator and proper `_require_service()` pattern. The function should return `CallToolResult(content=[...], isError=True)` on failure.

**Verification**: Call searxng_search with a query when the backend container is down. Should see `isError=True` in response.

---

### H-2: `config/mcp_servers.json` — Wrong `"type": "sse"` Format

**Severity**: 🟠 HIGH
**File**: `config/mcp_servers.json`
**Issue**: The `omega-hub` entry uses `"type": "sse"`, which OpenCode 1.17.3 does not recognize. It should be `"type": "remote"`.

**This file is the source for IDE sync via `sync_ide_mcp.sh`**, meaning incorrect configs propagate to VSCodium, Code, and Antigravity IDE.

**Fix**:
```json
"omega-hub": {
  "type": "remote",
  "url": "http://127.0.0.1:8016/sse"
}
```

**Verification**: `sync_ide_mcp.sh` propagates correct type to IDEs.

---

### H-3: RequestSizeLimitMiddleware Disabled

**Severity**: 🟠 HIGH
**File**: `mcp_servers/omega_hub/middleware.py:192-193`
**Issue**: The `RequestSizeLimitMiddleware` is commented out with the note:
```python
# Temporarily disabled RequestSizeLimitMiddleware to debug ASGI protocol error
# app.add_middleware(RequestSizeLimitMiddleware, max_size=25 * 1024 * 1024)
```

**Root cause**: "Temporarily" seems permanent. The hub has no payload size protection, making it vulnerable to OOM via large context posts (25MB+).

**Risk**: An agent posting a 100MB context snapshot could exhaust the hub's 130MB RSS allocation and crash the server.

**Fix**: Re-enable with a reasonable limit (25MB for context posts is appropriate):
```python
app.add_middleware(RequestSizeLimitMiddleware, max_size=25 * 1024 * 1024)
```

**Verification**: POST a payload >25MB to `/mcp` — should get HTTP 413.

---

### H-4: API Keys in Version-Controlled `opencode.json`

**Severity**: 🟠 HIGH
**File**: `opencode.json` (lines 43-44, 52-53)
**Issue**: Two API keys stored in plaintext in the project's main config file:
- `FIRECRAWL_API_KEY`: `***REMOVED***`
- `x-api-key` (Exa): `***REMOVED***`

**Risk**: If the repo is shared or pushed to a public remote, these keys are exposed.

**Fix**: Move to environment variables. Reference via `${FIRECRAWL_API_KEY}` and `${EXA_API_KEY}` in `opencode.json` and set them in `.env` or systemd service files.

**Verification**: `grep -rn "fc-[a-f0-9]\{32\}" opencode.json` returns empty.

---

## §4 MEDIUM Severity Findings

### M-1: tools.py Monolith (2361 lines)

**Severity**: 🟡 MEDIUM
**File**: `mcp_servers/omega_hub/tools.py`
**Issue**: After the P1b extraction of state.py, background.py, gateway.py, and middleware.py, `tools.py` remains a 2361-line monolithic file containing **50+ MCP tool functions** across 9 categories.

**Line breakdown**:
- Oracle tools (8): lines 116-333
- Sovereign search (1): lines 335-350
- Delegate task (1): lines 354-376
- Hivemind tools (13): lines 380-1459
- Library tools (12): lines 1462-1697
- Discovery tools (3): lines 1699-1754
- Memory tools (6): lines 1757-1929
- Research tools (5): lines 1932-2019
- Stats/Observability/ICS (8): lines 2022-2361

**Fix**: Split into submodule files:
```
mcp_servers/omega_hub/tools/
  __init__.py       # Re-export all
  oracle.py         # Oracle tools (8)
  hivemind.py       # Hivemind tools (13)
  library.py        # Library + Discovery tools (15)
  memory.py         # Memory tools (6)
  research.py       # Research tools (5)
  stats.py          # Stats + Observability + ICS (8)
```

**Verification**: All 50+ MCP tools still accessible after split, identical behavior.

---

### M-2: Hardcoded Paths Violating M16 (Modularization & Portability)

**Severity**: 🟡 MEDIUM
**Files**: `mcp_servers/omega_hub/tools.py` and `mcp_servers/omega_hub/gateway.py`
**Issue**: Several hardcoded paths assume the engine is running on `arcana-novai`'s machine:

| Line | Path | Context |
|------|------|---------|
| tools.py:2094 | `/media/arcana-novai/omega_library` | Disk stats |
| tools.py:2109 | `/sys/class/drm/card1/device/gpu_busy_percent` | GPU stats (hardware-specific) |
| tools.py:2136 | `/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor` | CPU governor (Linux-specific) |
| tools.py:2207 | `/media/arcana-novai/omega_library/models/gguf` | Model check |
| tools.py:2233 | `/media/arcana-novai/omega_library/podman-storage` | Podman storage |

**Risk**: These are in informational tools, so they won't crash the engine, but they return `"available": False` for anyone else running the engine. Violates M16 portability.

**Fix**: Move library paths to environment variables (`OMEGA_LIBRARY_PATH`, `OMEGA_MODELS_PATH`, `OMEGA_PODMAN_STORAGE`) with fallbacks.

**Verification**:
```bash
OMEGA_LIBRARY_PATH=/custom/path  # Would override hardcoded path
```

---

### M-3: SovereignGateway is Stubbed/Mocked

**Severity**: 🟡 MEDIUM
**File**: `mcp_servers/omega_hub/gateway.py:112-113`
**Issue**: The `proxy_request()` method returns a hardcoded mock response:
```python
return {"status": "proxied", "provider": provider_name, "payload": payload}
```
The start-backoff and rate-limiting logic are also commented out (lines 95-99).

**Risk**: The `/proxy/{provider}` HTTP endpoint is registered and exposed, but any call to it returns a fake response. If an agent relies on this proxy, it gets simulated data.

**Fix**: Wire to actual `ModelGateway` provider instances, or remove the endpoint and mark as TBD.

**Verification**: `curl -X POST http://127.0.0.1:8016/proxy/google -d '{"model":"gemma"}'` returns real response or 501 Not Implemented.

---

### M-4: Redundant HTTP Route Aliases

**Severity**: 🟡 MEDIUM
**File**: `mcp_servers/omega_hub/server.py:222-234`
**Issue**: Multiple route aliases create unnecessary attack surface:
```python
Route("/config", _config_get),
Route("/global/config", _config_get),
Route("/config.get", _config_get),       # dot-separated version
Route("/config.providers", _config_providers),
Route("/provider.list", _provider_list),
Route("/app.agents", _agent_list),
```

**Risk**: The dot-separated routes expose engine configuration through HTTP. While local-only, this is defense-in-depth surface area.

**Fix**: Remove dot-separated aliases that mirror MCP tool names. Keep only canonical paths.

**Verification**: No MCP clients break (they use the MCP protocol, not HTTP routes).

---

### M-5: Start-up Race Condition — Error Typing

**Severity**: 🟡 MEDIUM
**Files**: `mcp_servers/omega_hub/state.py:79-87`, `mcp_servers/omega_hub/tools.py`
**Issue**: `_require_service()` raises a generic `RuntimeError` if services are not ready. The `m9_safe` decorator catches this and returns a typed error, but the HTTP routes return a plain JSON error.

**Fix**: Have `_require_service()` raise a specific `OmegaError` subtype, and return 503 Service Unavailable from HTTP routes during init.

**Verification**: Calling any tool within 2 seconds of hub startup returns typed error, not crash.

---

## §5 FastMCP SSE Delivery Pattern Documentation Gap

### The 202 Accepted + Async SSE Pattern

**Current state**: This is **not documented anywhere in the codebase**. Engineers encountering the hub for the first time must reverse-engineer it from FastMCP source code.

**The pattern**:
1. Client connects to `GET /sse` → establishes long-lived SSE stream
2. Server sends `event: endpoint` with `data: /messages/?session_id=<uuid>`
3. Client sends tool calls via `POST /messages/?session_id=<uuid>`
4. Server processes the request asynchronously
5. Server sends the result back on the SSE stream as `event: message`

**What's not obvious**: The SSE connection is half-duplex — the client reads events, but sends tool calls via separate HTTP POST. The session ID is ephemeral — if the client disconnects and reconnects, they get a new session ID and any in-flight tool calls are orphaned.

**Documentation needed in `server.py`**:
```python
# FastMCP SSE Transport — Key Architectural Notes
#
# 1. SSE is READ-ONLY from the client's perspective.
#    Tool calls are sent via POST /messages/?session_id=<uuid>.
#    The session_id is obtained from the first SSE event.
#
# 2. The server accepts tool calls with HTTP 202 (Accepted) immediately,
#    processes asynchronously, and delivers the result on the SSE stream.
#    The HTTP response does NOT contain the result.
#
# 3. Stateless mode (stateless=True) allows clients to reconnect and
#    receive a new session without re-initializing. In-flight requests
#    from a previous session are lost.
#
# 4. Session IDs are generated per SSE connection. There is no persistent
#    session across reconnects — any pending tool call from a disconnected
#    session will never complete.
#
# 5. Streamable HTTP (POST /mcp) is an ALTERNATIVE to SSE for clients
#    that prefer request-response semantics. It uses single POST per
#    tool call and is compatible with OpenCode 1.15+ (type: "remote").
```

---

## §6 Legacy Patterns Recovered

### 6.1 From omega-stack MCP Architecture

The legacy `omega-stack` had two independent MCP server patterns that were consolidated:

| Legacy Pattern | What It Did | Where It Went |
|---------------|-------------|---------------|
| `mcp/omega-stats/server.py` | System stats via MCP | → `omega-hub` get_system_stats tool |
| `mcp/omega-research/server.py` | Background research | → `omega-hub` research tools |

**Lesson**: Both were consolidated into the hub via Decision 050, but **the systemd service files were never cleaned up**. This created the dead services in §2 (C-2, C-3).

### 6.2 From omega-stats Socket Activation

The `omega-stats.socket` pattern using systemd socket activation (port 8012) is a legitimate pattern for on-demand MCP servers. However, since the stats service was consolidated into the always-running hub, the socket activation adds unnecessary complexity.

### 6.3 SearXNG MCP Proxy Pattern

The SearXNG MCP server (`mcp_servers/searxng/server.py`) follows a clean proxy pattern: a lightweight FastMCP wrapper that forwards requests to a backend container. This is a good pattern for wrapping non-MCP services. However, it lacks the safety features of the hub:
- No `@m9_safe` decorator (H-1)
- No `httpx` timeout generalization
- No health-check dependency on the searxng container

### 6.4 Legacy API Key Exposure Pattern

The omega-stats service file contained API keys in `Environment=` declarations — a legacy pattern from the old stack that should have been migrated to a `.env` file or systemd `EnvironmentFile=` directive. This is a reminder that **config audit must include systemd service files**, not just `opencode.json`.

---

## §7 Summary — 16 Findings Total

| ID | Severity | Finding | Status | Fix Difficulty |
|----|----------|---------|--------|----------------|
| C-1 | 🔴 CRITICAL | `data/coordination/` owned by UID 100999 → metrics write fails every 60s | ACTIVE | EASY |
| C-2 | 🔴 CRITICAL | omega-stats.service references dead path + exposes API keys | ACTIVE | EASY |
| C-3 | 🔴 CRITICAL | omega-research.service dead (consolidated into hub) | ACTIVE | EASY |
| C-4 | 🔴 CRITICAL | SearXNG backend container not running | ACTIVE | EASY |
| H-1 | 🟠 HIGH | SearXNG MCP missing @m9_safe error boundary | ACTIVE | EASY |
| H-2 | 🟠 HIGH | config/mcp_servers.json uses wrong "type": "sse" | ACTIVE | EASY |
| H-3 | 🟠 HIGH | RequestSizeLimitMiddleware disabled (no payload protection) | ACTIVE | EASY |
| H-4 | 🟠 HIGH | API keys in plaintext in version-controlled opencode.json | ACTIVE | MEDIUM |
| M-1 | 🟡 MEDIUM | tools.py monolith (2361 lines) | ACTIVE | HARD |
| M-2 | 🟡 MEDIUM | Hardcoded paths violate M16 | ACTIVE | MEDIUM |
| M-3 | 🟡 MEDIUM | SovereignGateway is stubbed/mocked | ACTIVE | MEDIUM |
| M-4 | 🟡 MEDIUM | Redundant HTTP route aliases | ACTIVE | EASY |
| M-5 | 🟡 MEDIUM | Start-up race condition error typing | ACTIVE | MEDIUM |

---

## §8 Immediate Actions (Priority Order)

1. **Fix C-1**: `sudo chown -R 1000:1000 /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/coordination/`
2. **Fix C-2**: Disable and remove omega-stats.service + omega-stats.socket
3. **Fix C-3**: Disable and remove omega-research.service + omega-research.timer
4. **Fix C-4**: `systemctl --user start omega-searxng.service`
5. **Fix H-2**: Change `"type": "sse"` to `"type": "remote"` in config/mcp_servers.json
6. **Fix H-1**: Add `@m9_safe` decorator and typed error boundary to SearXNG MCP
7. **Fix H-3**: Re-enable RequestSizeLimitMiddleware
8. **Fix H-4**: Move API keys to environment variables

---

*Report by: roc_racoon, Sovereign Miner*
*Next scheduled audit: D144 (7-day cadence)*
