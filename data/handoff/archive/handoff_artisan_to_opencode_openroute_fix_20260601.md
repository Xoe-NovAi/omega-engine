<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Artisan Handoff
# ⬡ OMEGA ⬡ SOPHIA ⬡ Handoff: Artisan → OpenCode
# AP: AP-HANDOFF-OMEGA-FIX-v1.0.0
# Date: 2026-06-01
# Status: ✅ OpenCode 1.15+ handshake fully restored

## Summary
Restored OpenCode 1.15+ startup handshake by fixing the Omega Hub MCP server's
HTTP routing. The "4 of 5 requests failed" error is resolved.

## What Changed
1. **`src/omega/mcp_runtime.py`** — New `custom_routes` parameter + `_build_app()`
   that creates a Starlette app with custom routes at TOP level, MCP as sub-app mount.
2. **`mcp_servers/omega_hub/server.py`** — Removed unsupported `@mcp.on_event()` decorator
   (mcp==1.27.1 lacks this API). Clean architecture with Starlette Route handlers.

## Verified Working
- ✅ `/health` — 200 OK
- ✅ `/config.get` (dot-path) — 200 OK, returns opencode.json
- ✅ `/config.providers` (dot-path) — 200 OK, returns provider chain
- ✅ `/provider.list` (dot-path) — 200 OK, 8 providers
- ✅ `/app.agents` (dot-path) — 200 OK, 16 agents
- ✅ `/config`, `/provider`, `/agent` (slash-paths) — 200 OK
- ✅ SSE endpoint returns 200
- ✅ OpenCode 1.15.13 launches without errors
- ✅ 292 tests pass

## Architecture
```
User/OpenCode → Starlette App (custom_routes first)
                     ↓
               Route match? → Yes → Handle directly (/config.get, etc.)
                     ↓ No
               Mount("/", app=mcp_app) → MCP handles SSE/Message
```

## Next Steps
- The HBAR config (HANDOFF_OPENCODE.md, HBAR_PROTOCOL.md) needs to be re-integrated
  with the OpenCode JSON config for the `app.config` endpoint to serve properly.
- Strategy doc consolidation — 45+ docs identified for dedup/archival.
- OpenCode session can resume with working MCP bridge.
