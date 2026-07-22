# 🔱 R20 — MCP Migration Audit (2026-07-28 Spec)
**AP Token**: AP-RESEARCH-R20-v1.0.0
⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_research
**Date**: 2026-07-21
**Status**: COMPLETE — Survey Level
**Priority**: P1 (Blocks C-4a)

---

> ⚠️ **SCOPE**: This is a P1 survey-level audit — enough to size the migration work for C-4a/C-4b. The full migration is a Phase D workstream after C gate.

---

## Executive Summary

1. **MCP 2026-07-28 is the largest revision since launch** — the release candidate was locked May 21, 2026, final spec ships July 28, 2026. Deadline is **7 days from today**.
2. **Stateless core**: no `initialize` handshake (SEP-2575), no `Mcp-Session-Id` header (SEP-2567). Every request carries protocol version + capabilities in `_meta`.
3. **Omega Hub already has `stateless=True`** — this is a head start. However, the Hub uses SSE transport which will be deprecated in favor of Streamable HTTP for new deployments.
4. **Three breaking changes for remote servers**:
   - Remove handshake and session ID handling
   - Add THREE required routing headers: `Mcp-Method`, `Mcp-Name`, `traceparent`
   - OAuth hardening: validate `iss` parameter per RFC 9207 (SEP-2468)
5. **Recommended: audit first (2h) → size migration → shim for backward compatibility** — do NOT attempt a full rewrite before July 28. File-based Hivemind fallback is the contingency.

---

## Technical Findings

### 1. The Five Pillars of the 2026-07-28 Spec

| Pillar | Key SEPs | Impact on Omega Hub |
|--------|----------|---------------------|
| **Stateless core** | SEP-2575 (no handshake), SEP-2567 (no session ID) | **HIGH** — current SSE transport relies on session persistence |
| **Operability** | SEP-2243 (Mcp-Method/Mcp-Name headers), SEP-2549 (caching TTL), SEP-414 (W3C trace) | **MEDIUM** — headers already supported by Hub's HTTP transport |
| **Extensions** | SEP-1865 (Apps), SEP-2322 (Multi Round-Trip/Tasks) | **LOW** — extension features not needed for Hivemind |
| **Auth hardening** | SEP-2468 (iss validation), 5 others | **LOW** — Hub already uses Bearer token; requires iss audit |
| **Deprecations** | SEP-2596 (12-month window), roots/sampling/logging deprecated | **LOW** — deprecation window sufficient for full migration |

### 2. What the Hub Must Change (Pre-July-28)

From the [migration guide](https://luismori.dev/article/mcp-goes-stateless-2026-07-28-migration-guide/) and [Microsoft deployment analysis](https://techcommunity.microsoft.com/blog/appsonazureblog/mcp-just-went-stateless-%E2%80%94-what-the-2026-spec-changes-about-scaling-on-app-servic/4530222):

**Critical (break clients if not done)**:

1. **Remove `initialize`/`initialized` handshake** — currently in SSE session startup. Replace with `server/discover` method.
2. **Remove `Mcp-Session-Id` handling** — Hub already uses Bearer tokens for auth. Need to extract session context from per-request `_meta` instead.
3. **Add `Mcp-Method` and `Mcp-Name` headers** — routing headers required by protocol. Load balancers will reject requests without them.

**Important (needed for compatibility)**:

4. **Move client info to `_meta` field** — currently negotiated once during initialize. New spec requires per-request client identity.
5. **Audit OAuth for SEP-2468** — validate `iss` in JWT tokens per RFC 9207 (mix-up attack defense).

**Don't need (yet)**:

6. **Streamable HTTP migration** — SSE is still valid for local/dev; Streamable HTTP is recommended for production. Hub has `stateless=True` flag already.
7. **Multi Round-Trip pattern** — not needed unless Hub has server-initiated calls.

### 3. Hub Architecture Analysis

Current transport architecture:

```
Client → SSE stream (GET /sse) → Hub Server
         POST /messages/{session} → Hub Server
```

The Hub's `stateless=True` flag (from config) partially helps — but the SSE transport inherently maintains per-session state. The migration path:

```
Option A (Recommended for C-4b): 
  Client → Streamable HTTP POST /mcp
           (no session, all state in request _meta)

Option B (Contingency if SDK breaks):
  File-based Hivemind entirely → no MCP transport needed
  (Guaranteed to work, lower latency, no dependency)
```

### 4. SDK Breaking Changes — What to Check

The MCP Tier 1 SDKs (Python, TypeScript, Go) have RC support landing in June/July 2026:

| SDK | RC Status | Migration Notes |
|-----|-----------|-----------------|
| **Python SDK** | `mcp>=1.7.0` targets 2026-07-28 | Remove `@server.list_tools()`, use `@server.tool.list()` under new server factory |
| **TypeScript SDK** | `@modelcontextprotocol/sdk@2.0.0-rc.1` | Handlers now take `(req, meta)` instead of `(req, ctx)` |
| **Go SDK** | `mcp/v1.7.0` | `NewSSEHandler()` works but `Connect()` no longer takes session param |

Hub currently uses SSE transport — likely using internal Python socket patterns (not the official SDK). The audit must verify:
- Which SDK version (if any) the Hub depends on
- Whether Hub has compile-time dependencies that chain-break on SDK update
- Whether Hub's SSE implementation conflicts with Python SDK RC

### 5. Migration Mist Traps (from research)

1. **"SSE is being removed" — NO.** Streamable HTTP replaces standalone SSE. For dev/local, SSE continues to work. The removal is of session binding, not SSE itself.
2. **"Deprecated = gone July 28" — NO.** SEP-2596 guarantees 12-month minimum. `roots`, `sampling`, `logging` still work.
3. **"We can skip the headers" — NO.** `Mcp-Method` and `Mcp-Name` are required. Strict gateways reject requests without them.
4. **"requestState is a session ID" — NO.** It's an opaque signed blob, not a server-side session key. Echoed verbatim by client, never inspected.

---

## Decision Recommendation

**Phase C-4a: Complete MCP audit (2h) before July 26 hard deadline.**

Audit scope:
1. Hub code inventory — identify every place initialize/session ID/meta is handled
2. Client compatibility check — verify current clients (Claude Desktop, Cline, VS Code) will support 2026-07-28
3. Test file-based Hivemind fallback as contingency if the SDK breaks

**If SDK ships RC support by July 25**: Perform shim migration (add headers, remove session)
**If SDK is broken by July 26**: File-based Hivemind as default, MCP Hub becomes optional development mode

**Rationale for option B contingency**: The Hivemind is the engine's sovereign coordination layer. MCP is a transport protocol for that layer. If the MCP 2026-07-28 migration timeline is too tight (deadline 7 days away), the sovereign fallback is to decouple from MCP entirely and run Hivemind over file-based JSON (which has zero external dependencies and is already partially implemented).

---

## Sources

1. [MCP 2026-07-28 Release Candidate — MCP Blog](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/)
2. [MCP Goes Stateless: Migration Guide — luismori.dev](https://luismori.dev/article/mcp-goes-stateless-2026-07-28-migration-guide/)
3. [MCP Goes Stateless: Microsoft App Service Migration](https://techcommunity.microsoft.com/blog/appsonazureblog/mcp-just-went-stateless-%E2%80%94-what-the-2026-spec-changes-about-scaling-on-app-servic/4530222)
4. [MCP Stateless Spec: Migration Every Agent Team Must Plan — Drake Talley](https://www.draketalley.ai/blog/mcp-july-2026-stateless-spec-migration-guide)
5. [MCP Goes Stateless: 5 changes — Crux Digits](https://cruxdigits.nl/blog/mcp-goes-stateless-2026-spec)
6. [MCP 2026-07-28 Spec Guide — Ilir Ivezaj](https://ilirivezaj.com/blog/mcp-stateless-2026-spec)
7. [SSE vs Streamable HTTP — BrightData](https://brightdata.com/blog/ai/sse-vs-streamable-http)
8. Existing: Omega Hub MCP server code

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ R20-COMPLETE ⬡ 2026-07-21*
