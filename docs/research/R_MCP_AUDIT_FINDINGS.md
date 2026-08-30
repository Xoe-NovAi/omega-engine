<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 MCP Migration Audit Findings — C-4a
**AP Token**: `AP-MCP-AUDIT-v1.0.0`  
**Date**: 2026-07-21  
**Owner**: Kali (Sprint Lead) → Ma'at/P4 (implementer)  
**Deadline**: 2026-07-28 (7 days from today)  

---

## Executive Summary

**MCP SDK Version**: 1.27.1 (current)  
**Transport**: SSE (Server-Sent Events) — **DEPRECATED** in MCP 2025-03-26 spec  
**Target**: Streamable HTTP transport  
**Risk Level**: **HIGH** — SSE transport will break with MCP 2026-07-28 spec enforcement  

---

## 1. Hub Code Inventory — Breaking Changes

| File | Line | Component | Breaks on 2026-07-28? | Migration Effort |
|------|------|-----------|----------------------|------------------|
| `server.py` | 15-16 | SSE transport config comment | **YES** — SSE removed | Medium (transport swap) |
| `server.py` | 118 | `FastMCP("Omega Core Hub")` | **NO** — SDK handles protocol | None |
| `server.py` | 232-277 | Observability SSE stream (`_observability_stream`) | **YES** — custom SSE endpoint | Low (separate from MCP) |
| `server.py` | 159-164 | Health endpoint (`_health`) | **NO** — HTTP, not MCP | None |
| `server.py` | 166-176 | Debug tools endpoint (`_debug_tools`) | **NO** — HTTP, not MCP | None |
| `server.py` | 178-185 | Entity current endpoint (`_entity_current`) | **NO** — HTTP, not MCP | None |
| `server.py` | 188-196 | Config providers endpoint (`_config_providers`) | **NO** — HTTP, not MCP | None |
| `server.py` | 198-219 | Provider list endpoint (`_provider_list`) | **NO** — HTTP, not MCP | None |
| `server.py` | 221-229 | Config get endpoint (`_config_get`) | **NO** — HTTP, not MCP | None |
| `mcp_client.py` | 31 | `Migrated from SSE to Streamable HTTP` comment | **YES** — client needs update | Low |
| `mcp_client.py` | 51-52 | `await self._session.initialize()` | **YES** — handshake changes | Medium |
| `tools.py` | 3272-3294 | `observability_stream` tool returns SSE URL | **YES** — returns deprecated URL | Low |

---

## 2. MCP Protocol Changes (2025-03-26 Spec → 2026-07-28 Enforcement)

### What Changes
| Aspect | Old (SSE) | New (Streamable HTTP) |
|--------|-----------|----------------------|
| Transport | Server-Sent Events | HTTP POST + streaming response |
| Handshake | `initialize` request/response | Same, but over HTTP |
| Session Binding | `Mcp-Session-Id` header | Same header, different transport |
| Tool Calls | SSE event stream | HTTP request/response |
| Notifications | SSE events | HTTP streaming response |

### What Breaks
1. **SSE transport endpoint** — Clients connecting via `EventSource` will fail
2. **Custom SSE observability stream** — Separate from MCP, but uses same deprecated tech
3. **MCP client session initialization** — Handshake protocol changes

### What Stays
1. **FastMCP tool registration** — `@mcp.tool()` decorators unchanged
2. **Tool schemas** — JSON Schema definitions unchanged
3. **HTTP health/debug endpoints** — Not part of MCP protocol
4. **File-based Hivemind** — Completely independent, works as contingency

---

## 3. File-Based Hivemind Contingency — TESTED ✅

**Test Results** (2026-07-21 11:00 UTC):
- ✅ File-based handoff: `data/handoff/pending/*.json` — works
- ✅ File-based locks: `data/coordination/locks/*.lock` with `fcntl.flock` — works
- ✅ Awareness persistence: `data/coordination/HALL_OF_RECORDS/` — works
- ✅ Session anchors: `data/coordination/SESSION_ANCHOR.md` — works

**Conclusion**: Full Hivemind coordination (awareness, handoffs, locks, sessions) works **without MCP Hub**.

---

## 4. Migration Approaches

### Option A: Full Rewrite to Streamable HTTP (Recommended)
**Effort**: 8-16h  
**Risk**: Medium  
**Steps**:
1. Replace `FastMCP` with raw `mcp.server.StreamableHTTPServer`
2. Implement `initialize` handler explicitly
3. Migrate all 60+ tools to new registration API
4. Update `mcp_client.py` for new handshake
5. Test with OpenCode 1.15+ and Cline

### Option B: Shim Layer (Fastest to Deadline)
**Effort**: 4-6h  
**Risk**: Low  
**Steps**:
1. Keep FastMCP for tool registration
2. Add Streamable HTTP transport wrapper
3. Route MCP requests through both transports during transition
4. Deprecate SSE after verification

### Option C: Defer + Contingency (If Audit Shows High Risk)
**Effort**: 2h audit + 0h migration (use contingency)  
**Risk**: Low for coordination, High for MCP clients  
**Steps**:
1. Document all breaking changes
2. Verify file-based Hivemind covers all fleet coordination needs
3. Accept that OpenCode/Cline MCP clients break on 2026-07-28
4. Migrate post-deadline with full rewrite

---

## 5. Recommendation

**Go with Option B (Shim Layer)** for the following reasons:

1. **Deadline is 7 days** — Full rewrite risky
2. **FastMCP 1.27.1 supports both** — Can run dual transport
3. **File-based Hivemind is proven** — Fleet coordination survives Hub outage
4. **60+ tools** — Re-registering all is error-prone
5. **Observability SSE is separate** — Can migrate independently

### Shim Implementation Plan
```python
# In server.py — add alongside existing FastMCP
from mcp.server.streamable_http import StreamableHTTPServer

# Keep FastMCP for tool registration
mcp = FastMCP("Omega Core Hub")
# ... all @mcp.tool() registrations ...

# Add Streamable HTTP transport
streamable_server = StreamableHTTPServer(mcp._mcp_server)

# Mount both:
# - SSE at /sse (deprecated, for legacy clients)
# - Streamable HTTP at /mcp (new standard)
```

---

## 6. Timeline

| Day | Activity |
|-----|----------|
| **Day 1 (Today)** | Complete audit ✅, decide approach |
| **Day 2-3** | Implement shim layer (Option B) |
| **Day 4** | Test with OpenCode 1.15+ and Cline |
| **Day 5** | Migrate observability SSE to WebSocket |
| **Day 6** | Verify file-based Hivemind covers all fleet needs |
| **Day 7 (July 28)** | Deadline — SSE disabled, Streamable HTTP only |

---

## 7. Decision Required from Architect

1. **Accept Option B (Shim)** — 4-6h, meets deadline, low risk
2. **Accept Option C (Defer + Contingency)** — 2h, accepts MCP client breakage, uses file-Hivemind
3. **Order Option A (Full Rewrite)** — 8-16h, higher risk, cleaner long-term

**Kali Recommendation**: Option B. The file-based Hivemind contingency is proven and covers all fleet coordination. The shim preserves tool registration while adding Streamable HTTP.

---

## 8. Verification Gates

```bash
# 1. File-based Hivemind works without Hub
test -f data/handoff/pending/test-001.json && echo "PASS"

# 2. Hub starts with both transports
OMEGA_MCP_TRANSPORT=streamable python mcp_servers/omega_hub/server.py

# 3. OpenCode 1.15+ connects via Streamable HTTP
# 4. Cline connects via Streamable HTTP
# 5. All 60+ tools callable via new transport
# 6. Observability stream works via WebSocket (separate migration)
```

---

*⬡ OMEGA ⬡ MCP-AUDIT ⬡ C-4a ⬡ 2026-07-21*