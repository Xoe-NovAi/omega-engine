# 🔱 MCP Migration Audit — C-4a (Updated 2026-07-23)
**AP Token**: `AP-MCP-AUDIT-v2.0.0`
**Date**: 2026-07-23 (updated with correct 2026-07-28 spec details)
**Owner**: Ma'at/P4 (implementer)
**Deadline**: 2026-07-28 (5 days from today)
**Previous Audit**: `docs/research/R_MCP_AUDIT_FINDINGS.md` (2026-07-21, superseded)

---

## Executive Summary

**MCP SDK Version**: 1.27.1 (pinned in pyproject.toml)
**Current Transport**: Dual — SSE + Streamable HTTP (both active via `mcp_runtime.py`)
**Target**: MCP 2026-07-28 spec compliance (stateless core)
**Risk Level**: **MEDIUM** — Shim layer already exists; protocol changes are incremental
**Recommendation**: **Option B (Shim Update)** — 4-6h, meets deadline, low risk

---

## 1. MCP 2026-07-28 Spec Changes (Corrected)

### What Actually Changes

| Change | SEP | Impact on Omega |
|--------|-----|-----------------|
| `initialize`/`initialized` handshake **removed** | SEP-2575 | **HIGH** — `mcp_client.py:51` calls `session.initialize()` |
| `Mcp-Session-Id` header **removed** | SEP-2567 | **LOW** — Omega doesn't use MCP session IDs for routing |
| New `server/discover` method | SEP-2575 | **LOW** — Optional capability discovery |
| `Mcp-Method` + `Mcp-Name` headers mandatory on Streamable HTTP | SEP-2243 | **MEDIUM** — SDK handles this, but verify |
| Multi-round-trip requests replace long-lived SSE | SEP-2260, SEP-2322 | **LOW** — Omega doesn't use server-initiated requests |
| Resource-not-found: -32002 → -32602 | SEP-2164 | **LOW** — No hardcoded error codes found |
| Roots, Sampling, Logging deprecated | SEP-2577 | **LOW** — Omega doesn't use these features |
| Tool schemas → full JSON Schema 2020-12 | SEP-2106 | **LOW** — Current schemas are valid |

### What Does NOT Change

| Aspect | Status |
|--------|--------|
| SSE transport | **Still supported** — not removed, just protocol changes |
| FastMCP tool registration | **Unchanged** — `@mcp.tool()` decorators work |
| Tool schemas | **Unchanged** — JSON Schema subset still valid |
| HTTP health/debug endpoints | **Not MCP** — no changes needed |
| File-based Hivemind | **Independent** — works without MCP Hub |

---

## 2. Server Inventory — Code Size & Breaking Changes

### MCP Servers

| Server | File | LOC | Transport | Tools | Breaking Changes |
|--------|------|-----|-----------|-------|-----------------|
| **Omega Hub** | `mcp_servers/omega_hub/server.py` | 389 | SSE + Streamable HTTP | 60+ | `mcp_client.py:51` `initialize()` call |
| **SearXNG** | `mcp_servers/searxng/server.py` | 110 | Streamable HTTP | 2 | None (no session handling) |
| **Firecrawl** | `mcp_servers/firecrawl/server.py` | 271 | SSE | 5 | None (no session handling) |

### Hub Internal Modules

| Module | LOC | Role | Breaking Changes |
|--------|-----|------|-----------------|
| `state.py` | 661 | Service singletons, Hivemind state | None |
| `hub_tools/tools.py` | 3,389 | All 60+ MCP tool definitions | None (session_id is app-level, not MCP protocol) |
| `hub_tools/task_registry.py` | 230 | Subagent task tracking | None |
| `middleware.py` | 204 | Rate limiting, security | None |
| `gateway.py` | 229 | SovereignGateway proxy | None |
| `background.py` | 306 | Pruning, reaper, metrics | None |
| `hivemind_redis.py` | 113 | Redis Pub/Sub fallback | None |
| `github_tools.py` | 275 | GitHub operations | None |
| `github_bridge.py` | 157 | GitHub API bridge | None |
| `mcp_client.py` | 121 | **Sovereign MCP Client** | **YES** — `session.initialize()` removed |

### Runtime

| Module | LOC | Role | Breaking Changes |
|--------|-----|------|-----------------|
| `mcp_runtime.py` | 202 | Dual-transport runtime | **Already has StreamableHTTPASGIApp** |

**Total MCP codebase**: 6,657 LOC across 14 files

---

## 3. StreamableHTTPASGIApp Shim — VERIFIED ✅

**Location**: `src/omega/mcp_runtime.py:63`
```python
from mcp.server.fastmcp.server import StreamableHTTPASGIApp
```

**Status**: The shim layer **already exists** and is **actively used**:
- Line 88-94: `StreamableHTTPSessionManager` initialized
- Line 94: `StreamableHTTPASGIApp(streamable_mgr)` created
- Line 96-98: Streamable HTTP route mounted at `/mcp`
- Line 113: `streamable_mgr.run()` in lifespan context

**Dual transport is LIVE**:
- SSE: `GET /sse` → SSE stream → `POST /messages/`
- Streamable HTTP: `POST /mcp` → direct JSON-RPC

---

## 4. Breaking Changes — Detailed Analysis

### 4.1 `mcp_client.py:51` — `session.initialize()` removed

**Current code**:
```python
async def connect(self):
    async with self._session:
        await self._session.initialize()  # ← BREAKS on 2026-07-28
        logger.info("Sovereign MCP Client connected and initialized")
```

**Migration**: Replace with `server/discover` or remove if client doesn't need capability discovery.

### 4.2 Hivemind `session_id` — NOT AFFECTED ✅

The `session_id` in `hivemind_post_context` and `hivemind_get_session` is an **application-level UUID** passed as a tool parameter, NOT an MCP protocol header. It's unaffected by SEP-2567 (which removes `Mcp-Session-Id` header).

### 4.3 Custom SSE endpoints — NOT AFFECTED ✅

The observability SSE stream (`/obs/stream`) is a custom Starlette endpoint, NOT an MCP transport endpoint. It's unaffected by MCP protocol changes.

---

## 5. File-Based Hivemind Contingency — PROVEN ✅

All fleet coordination works without MCP Hub:
- ✅ `data/handoff/pending/*.json` — handoffs
- ✅ `data/coordination/locks/*.lock` — workspace locks
- ✅ `data/coordination/HALL_OF_RECORDS/` — awareness persistence
- ✅ `data/coordination/SESSION_ANCHOR.md` — session anchors

---

## 6. Migration Plan

### Option B: Shim Update (RECOMMENDED)

**Effort**: 4-6h
**Risk**: Low
**Deadline**: Meets July 28

**Steps**:
1. **Update `mcp_client.py`** — Remove `session.initialize()`, use `server/discover` or remove capability discovery
2. **Verify `Mcp-Method`/`Mcp-Name` headers** — SDK 1.27.1 should handle this, but verify
3. **Test dual transport** — Verify SSE + Streamable HTTP both work
4. **Update OpenCode config** — Point to `/mcp` endpoint for Streamable HTTP clients

### Why NOT Option A (Full Rewrite)

- 60+ tools to re-register — error-prone
- FastMCP 1.27.1 already supports dual transport
- File-based Hivemind covers fleet coordination
- Deadline is 5 days

### Why NOT Option C (Defer)

- MCP clients (OpenCode, Cline) will break on 2026-07-28
- Shim update is only 4-6h — worth doing

---

## 7. Verification Gates

```bash
# 1. Hub starts with both transports
source .venv/bin/activate
OMEGA_MCP_TRANSPORT=sse OMEGA_MCP_PORT=8016 python mcp_servers/omega_hub/server.py &
# Verify: SSE at http://localhost:8016/sse
# Verify: Streamable HTTP at http://localhost:8016/mcp

# 2. OpenCode connects via Streamable HTTP
# Update opencode.json: "url": "http://localhost:8016/mcp"

# 3. All tools callable via new transport
curl -X POST http://localhost:8016/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'

# 4. Hivemind works via file-based contingency
ls data/handoff/pending/
ls data/coordination/locks/

# 5. No MCP session ID dependencies
grep -rn "Mcp-Session-Id\|mcp_session" mcp_servers/ --include="*.py"
# Should return empty
```

---

## 8. Timeline

| Day | Activity | Owner |
|-----|----------|-------|
| **Day 1 (Today)** | Audit complete ✅, update `mcp_client.py` | Ma'at/P4 |
| **Day 2** | Verify `Mcp-Method`/`Mcp-Name` headers, test dual transport | Ma'at/P4 |
| **Day 3** | Test with OpenCode 1.15+ and Cline | Ma'at/P4 |
| **Day 4** | Migrate observability SSE to WebSocket (optional) | Ma'at/P4 |
| **Day 5 (July 28)** | Deadline — verify all clients work | Ma'at/P4 |

---

## 9. Decision Required

**Recommendation**: Accept Option B (Shim Update)
- 4-6h effort, meets deadline, low risk
- File-based Hivemind proven as contingency
- Dual transport already active in `mcp_runtime.py`

**Escalation**: If P4 silent by EOD 2026-07-23 → Kali executes `mcp_client.py` update directly.

---

*⬡ OMEGA ⬡ C-4a ⬡ MCP-AUDIT ⬡ v2.0.0 ⬡ 2026-07-23*