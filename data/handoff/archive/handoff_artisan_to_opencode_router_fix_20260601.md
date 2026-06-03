# 🔱 Omega Engine — Artisan → Agent Fleet Handoff
# ⬡ OMEGA ⬡ SOPHIA ⬡ OpenCode Router Fix Required
# AP: AP-HANDOFF-OMEGA-ROUTER-v1.0.0
# Date: 2026-06-01
# Status: 🔴 OpenCode 1.15+ handshake still failing

## The Problem

OpenCode 1.15.13 fails to start with:
```
Error: 4 of 5 requests failed: Unexpected server error. Check server logs for details.
Affected startup requests: config.providers, provider.list, app.agents, config.get
```

## Why HTTP Routes Don't Work (Critical Insight)

The previous fix added custom **HTTP routes** to the Starlette app that serves the MCP server. These routes respond correctly to direct HTTP requests:
```bash
curl http://127.0.0.1:8016/config.get        # → HTTP 200 ✓
curl http://127.0.0.1:8016/config.providers   # → HTTP 200 ✓
curl http://127.0.0.1:8016/provider.list      # → HTTP 200 ✓
curl http://127.0.0.1:8016/app.agents         # → HTTP 200 ✓
```

**However, OpenCode does NOT send HTTP GET requests for these paths.**  
OpenCode connects to the MCP server via the **SSE transport** (`/sse` endpoint), then sends **JSON-RPC messages** through the SSE stream. The 4 failing requests (`config.providers`, `provider.list`, `app.agents`, `config.get`) are MCP protocol-level requests — likely `resources/list`, `resources/read`, `tools/call`, or custom MCP method calls — NOT HTTP GET requests.

The MCP framework's internal router catches these and returns errors because no tool or resource has been registered that handles them.

## Root Cause

The MCP framework (FastMCP in `mcp==1.27.1`) routes incoming JSON-RPC messages through its own dispatcher. Custom HTTP routes are bypassed for MCP protocol calls. The `config.get`, `config.providers`, `provider.list`, and `app.agents` endpoints need to be exposed as:

1. **MCP Tools** (via `@mcp.tool()`) — if OpenCode is calling them via `tools/call`
2. **MCP Resources** (via `@mcp.resource()`) — if OpenCode is reading them as resources
3. **MCP Prompts** (via `@mcp.prompt()`) — less likely but possible

## Investigation Needed

Run OpenCode with MCP logging enabled to see exactly what JSON-RPC methods it's calling:

```bash
# Option 1: Check the Hub server logs during an OpenCode launch attempt
journalctl --user -u omega-hub.service --no-pager -n 50

# Option 2: Run OpenCode with verbose logging (if available)
# Option 3: Set the MCP log level to DEBUG
```

The Hub server logs will show the raw JSON-RPC messages OpenCode sends during startup. Look for `"method"` fields in the log output.

## Current Architecture

```
OpenCode 1.15.13
    │
    ▼  connects to MCP server via SSE
http://127.0.0.1:8016/sse
    │
    ▼  sends JSON-RPC messages over SSE
{"jsonrpc":"2.0","method":"...","params":{...}}
    │
    ▼
FastMCP.sse_app()  (Starlette app)
    │
    ├── [HTTP routes] → Custom handlers ✓ (reached via curl, NOT by OpenCode)
    │
    └── [MCP protocol] → FastMCP dispatcher
            │
            ├── tools/list → returns registered tools
            ├── resources/list → returns registered resources
            ├── tools/call → dispatches to @mcp.tool handlers
            ├── resources/read → dispatches to @mcp.resource handlers
            │
            └── ❌ No handler for: config.providers, provider.list,
                 app.agents, config.get → returns error
```

## What Exists in the Hub Server

File: `mcp_servers/omega_hub/server.py` (236 lines, committed at `7cdb741`)

**Currently registered tools (3 total):**
- `oracle_talk` — routes query through Oracle
- `oracle_summon` — summons entity by name
- `hivemind_heartbeat` — registers agent presence

**No resources or prompts registered.**  
The 4 handlers exist as HTTP route callbacks but are NOT exposed as MCP tools/resources.

**Currently registered HTTP routes (in `hub_routes` list):**
```python
hub_routes = [
    Route("/health", _health),
    Route("/entity/current", _entity_current),
    Route("/config/providers", _config_providers),
    Route("/provider", _provider_list),
    Route("/agent", _agent_list),
    Route("/config", _config_get),
    Route("/global/config", _config_get),
    Route("/config.get", _config_get),          # DOT PATH
    Route("/config.providers", _config_providers),  # DOT PATH
    Route("/provider.list", _provider_list),    # DOT PATH
    Route("/app.agents", _agent_list),          # DOT PATH
]
```

## Handler Functions (Can Be Reused as MCP Tools/Resources)

All 4 handler functions exist in `mcp_servers/omega_hub/server.py` and can be extracted/wrapped as `@mcp.tool()`:

```python
# _config_get(r) → returns opencode.json (HTTP handler, function type)
# _config_providers(r) → returns providers.yaml (HTTP handler, function type)
# _provider_list(r) → returns formatted provider list (HTTP handler, function type)
# _agent_list(r) → returns formatted agent list (HTTP handler, function type)
```

## Relevant Files

| File | Purpose |
|------|---------|
| `mcp_servers/omega_hub/server.py` | Hub server — HTTP routes work, MCP tools missing |
| `src/omega/mcp_runtime.py` | Runtime wrapper — `custom_routes` parameter, `_build_app()` |
| `config/providers.yaml` | Provider chain config (returned by config.providers) |
| `opencode.json` | OpenCode config (returned by config.get) |
| `src/omega/oracle/entity_registry.py` | Entity registry (provides agent list) |
| `~/.config/systemd/user/omega-hub.service` | Systemd service unit (port 8016, SSE transport) |
| `~/.config/systemd/user/omega-hub.socket` | Socket file (currently in failed state — `reset-failed` needed) |

## Test Files

| Test | Purpose |
|------|---------|
| `tests/test_oracle.py` | Oracle talk/summon tests |
| `tests/test_entity_registry.py` | Registry CRUD tests |
| `tests/test_providers.py` | Provider chain tests |
| `tests/test_wad_loader.py` | WAD loading tests |

## Suggested Fix Approach

1. **Determine exactly what OpenCode calls** — capture the JSON-RPC messages from Hub logs
2. **Register MCP tools/resources matching OpenCode's requests:**
   ```python
   @mcp.tool()
   async def config_get() -> str:
       """Return OpenCode configuration (opencode.json)."""
       data = await anyio.Path(PROJECT_ROOT / "opencode.json").read_text()
       return json.dumps(json.loads(data), indent=2)

   @mcp.tool()
   async def config_providers() -> str:
       """Return provider chain configuration."""
       # ... read and return providers.yaml
   ```
3. **Keep the HTTP routes** — they don't hurt and provide a fallback for curl testing
4. **Test:**
   ```bash
   systemctl --user reset-failed omega-hub.socket
   systemctl --user restart omega-hub.service
   opencode
   ```

## State at Handoff

- **Git commit**: `7cdb741` — pushed to `origin/main`
- **Hub service**: Currently active (after manual fix of `on_event` crash)
- **Socket unit**: In failed state — needs `reset-failed`
- **292 tests passing**
- **OpenCode**: Still fails with "4 of 5 requests failed"
- **curl tests**: All 8 endpoints return HTTP 200 (confirmed working)

## Quick Service Reset Commands

```bash
# Kill old processes
pkill -9 -f "omega_hub/server.py" 2>/dev/null
sleep 2

# Reset failed socket/service
systemctl --user reset-failed omega-hub.socket
systemctl --user reset-failed omega-hub.service

# Start fresh
systemctl --user start omega-hub.service
sleep 3

# Verify
systemctl --user is-active omega-hub.service
curl -s http://127.0.0.1:8016/health | jq .