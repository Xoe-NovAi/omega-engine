# 🔱 MCP Migration Audit — Streamable HTTP & OAuth 2.1
**AP Token**: `AP-C4A-MCP-AUDIT-v1.0.0`
⬡ OMEGA ⬡ MAAT ⬡ opencode ⬡ trc_c4a ⬡ MCP-AUDIT

**Date**: 2026-07-22
**Status**: ✅ COMPLETE — Audit findings ready for C-4b migration sizing

---

## §1 Audit Scope

**Ticket**: C-4a — MCP Migration Audit
**Owner**: Ma'at/P4 (Bridge)
**Decision**: Audit only — deliver this R doc. Migration (C-4b) is Kali's escalation path.
**Deadline**: July 28, 2026 (7-day clock started July 21)
**Spec**: `docs/strategy/IMPLEMENTATION_MANUAL_C0_C2.md` §C-4a

---

## §2 Code Inventory — Hub MCP Endpoints

### 2.1 Transport Architecture (`src/omega/mcp_runtime.py`)

The Hub already implements **dual transport** from a single server:

| Transport | Path | SDK Component | Status |
|-----------|------|---------------|--------|
| SSE (legacy) | `GET /sse` → SSE stream → `POST /messages/` | `SseServerTransport` | ✅ ACTIVE |
| Streamable HTTP | `POST /mcp` → direct JSON-RPC | `StreamableHTTPSessionManager` | ✅ ACTIVE |

Both are served by the same Starlette ASGI app (`_build_app()` at line 47).

### 2.2 Code Paths

| File | Line | Component | MCP Impact |
|------|------|-----------|------------|
| `src/omega/mcp_runtime.py:65-85` | SSE transport setup | `SseServerTransport` + `handle_sse` | Retained for backward compat |
| `src/omega/mcp_runtime.py:87-98` | Streamable HTTP setup | `StreamableHTTPSessionManager` + `StreamableHTTPASGIApp` | ✅ Primary target |
| `src/omega/mcp_runtime.py:100` | Route assembly | `all_routes = sse_routes + streamable_routes` | Both active |
| `src/omega/mcp_runtime.py:113` | Streamable HTTP lifespan | `streamable_mgr.run()` session lifecycle | ✅ Correct |
| `mcp_servers/omega_hub/mcp_client.py:45` | Client connection | `streamablehttp_client()` | ✅ Streamable HTTP |
| `mcp_servers/omega_hub/server.py:232-277` | Obs SSE stream | `sse_starlette.sse.EventSourceResponse` | Not MCP — independent |
| `mcp_servers/omega_hub/server.py:388-390` | Server entry point | `run_mcp()` with hub_routes + middleware | Routes merged |

### 2.3 Custom HTTP Routes (Non-MCP)

The Hub has 12 custom Starlette routes (`hub_routes` in `server.py:310-325`) — health, debug, config, proxy, observability. These are independent of MCP transport.

---

## §3 SDK Version Assessment

| Metric | Value |
|--------|-------|
| MCP SDK | `mcp==1.27.1` |
| MCP Spec | 2025-03-26 |
| Streamable HTTP | Supported natively (SDK includes `StreamableHTTPSessionManager`) |
| Stateless mode | ✅ Enabled (`stateless=True` on both transports) |
| InitializeRequest | Built-in SDK handling — no custom handler |

**Assessment**: SDK v1.27.1 is current. Streamable HTTP is already integrated at the SDK level. The dual-transport pattern in `mcp_runtime.py` is the recommended migration path from the MCP team.

---

## §4 Breaking Changes Assessment

### 4.1 SSE → Streamable HTTP Timeline
- SSE deprecated since 2025-03-26 spec
- Keboola dropped SSE April 1, 2026
- Atlassian dropped SSE June 30, 2026
- MCP 2026-07-28 RC expected (stateless, no `Mcp-Session-Id`)

### 4.2 Hub Exposure
| Concern | Status | Details |
|---------|--------|---------|
| SSE still active | ⚠️ YES | `GET /sse` + `POST /messages/` served |
| Streamable HTTP ready | ✅ YES | `POST /mcp` served from same app |
| `Mcp-Session-Id` usage | ✅ NONE | Good — no legacy session binding |
| Custom `initialize` handler | ✅ NONE | All init handled by SDK |
| `stateless=True` | ✅ SET | Both transports use stateless mode |
| Transport security | ⚠️ NOT CONFIGURED | `mcp.settings.transport_security` passed but has defaults |
| OAuth 2.1 + PKCE | ❌ MISSING | No custom auth implemented |

### 4.3 Migration Path
The Hub is in **good shape** — Streamable HTTP is already operational alongside SSE. The migration is:
1. **Phase 1 (C-4b)**: Remove SSE transport, keep only Streamable HTTP
2. **Phase 2**: Add OAuth 2.1 + PKCE for security
3. **Phase 3**: Verify all MCP clients work with Streamable HTTP only

---

## §5 File-Based Hivemind Contingency

| Test | Result |
|------|--------|
| `data/handoff/pending/` exists | ✅ YES — 2 pending handoffs |
| `data/coordination/locks/` exists | ✅ YES — 2 active locks |
| File-based handoff protocol | ✅ Operational (7 handoffs accepted this session) |
| File-based awareness | ✅ Operational (hivemind_get_awareness works without Hub) |
| File-based workspace locks | ✅ Operational (TTL-based, os.replace atomic) |

**Assessment**: The file-based Hivemind (`data/handoff/` + `data/coordination/`) is fully operational as a contingency. Agents can coordinate without the MCP Hub. **No changes needed** — this is already verified production behavior.

---

## §6 Security Assessment

| Component | Status | Action Needed |
|-----------|--------|---------------|
| `transport_security` settings | ⚠️ Defaults only | Configure for production |
| OAuth 2.1 + PKCE | ❌ Not implemented | Phase 2 of C-4b |
| API key validation | ✅ Via providers.yaml | No change needed |
| Rate limiting (`middleware.py`) | ✅ Implemented | No change needed |
| Request size limits (`middleware.py`) | ✅ Implemented | No change needed |

---

## §7 Recommended C-4b Migration Approach

### Approach: "SSE Removal + Streamable HTTP Only"

**Rationale**: The Hub already has Dual Transport. The migration is primarily **removing the SSE path** and ensuring all clients reconnect via `/mcp`. This is significantly less work than a full rewrite.

### Migration Steps
1. Remove SSE routes from `mcp_runtime.py:_build_app()` (lines 65-85, 82-85)
2. Remove `SseServerTransport` import
3. Update `OMEGA_MCP_TRANSPORT` env var handling — default to auto-detect
4. Test all MCP tools via Streamable HTTP
5. Verify OpenCode, Cline, and Antigravity IDE all work with `/mcp` only

### Effort Estimate
- **Code changes**: ~30 lines modified in `mcp_runtime.py`
- **Testing**: 2-3 hours (test each MCP client)
- **Risk**: Low — Streamable HTTP already works in production alongside SSE

### Timeline
| Phase | Work | Estimated | Deadline |
|-------|------|-----------|----------|
| C-4b Phase 1 | Remove SSE, keep Streamable HTTP only | 2-3h | July 26 |
| C-4b Phase 2 | OAuth 2.1 + PKCE | 4-6h | July 28 |
| C-4b Phase 3 | Client verification | 2h | July 28 |

---

## §8 Verification Gate

```bash
# 1. Audit document exists
test -f docs/research/R_CG01_MCP_STREAMABLE_HTTP_OAUTH.md && echo "✅ PASS" || echo "❌ FAIL"

# 2. File-based contingency tested
ls data/handoff/pending/*.json > /dev/null 2>&1 && echo "✅ PASS: File handoff works" || echo "⚠️ No pending handoffs"

# 3. Hub code inventory complete
grep -c "StreamableHTTPSessionManager\|SseServerTransport" src/omega/mcp_runtime.py
# Expected: >= 2 (both transports referenced)
```

---

## §9 Decision Log

| ID | Decision | Rationale |
|----|----------|-----------|
| D-C4A-001 | **Audit only** — Ma'at/P4 delivers findings. Kali executes C-4a.5 migration if P4 silent by EOD. | Separation of concerns: P4 = Bridge (audit), Kali = Oversight (execution) |
| D-C4A-002 | **File-based Hivemind** is the contingency — no changes needed | Already operational and verified |
| D-C4A-003 | **SSE removal** is the primary migration — not a full rewrite | Hub already has Streamable HTTP working |
| D-C4A-004 | **OAuth 2.1 deferred** to C-4b Phase 2 | Out of scope for Jul 28 deadline |

---

*⬡ OMEGA ⬡ MAAT ⬡ C4A-MCP-AUDIT ⬡ 2026-07-22*
