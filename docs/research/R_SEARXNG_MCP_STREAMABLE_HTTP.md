# 🔱 R_SEARXNG_MCP_STREAMABLE_HTTP — SearXNG MCP Server Migration to Streamable HTTP
**AP Token**: `AP-SEARXNG-MCP-STREAMABLE-v1.1.0`
⬡ OMEGA ⬡ SEARXNG-MCP ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_searxng_mcp ⬡ STREAMABLE-HTTP

**Date**: 2026-07-12
**Status**: ✅ COMPLETE — All fixes verified, OpenCode CLI shows connected

---

## §1 Executive Summary

Migrated the SearXNG MCP server from **SSE (Server-Sent Events)** transport to **Streamable HTTP** (MCP SDK v2, spec 2025-03-26). Fixed OpenCode configuration mismatch that caused the server to "flip back to disabled" in the TUI. Hardened SearXNG `settings.yml` with `keep_only` engine filtering, removed invalid config keys, and eliminated Brave (rate-limited).

---

## §2 Root Cause Analysis

### 2.1 The "Flipping Back to Disabled" Bug

**Symptom**: In OpenCode TUI (`/mcp` dialog), SearXNG showed as disabled. Clicking enable would flash "enabled" for ~1 second, then revert to disabled. No error message.

**Root Cause**: **Two conflicting OpenCode configs**:
- **Project config** (`omega-engine/opencode.json`): Had `"type": "streamable-http"` (invalid — OpenCode only recognizes `"local"` and `"remote"`)
- **Global config** (`~/.config/opencode/opencode.json`): Had `"type": "remote"` with URL `http://127.0.0.1:8018/mcp/` (trailing slash)

OpenCode merges configs with **global taking precedence**. The global config's trailing slash + SSE-first connection attempt caused 406 errors, triggering OpenCode's auto-disable logic.

### 2.2 OpenCode MCP Type System

| Type | Transport | Use Case |
|------|-----------|----------|
| `"local"` | stdio | Local process (npx, python, etc.) |
| `"remote"` | HTTP (auto-detect SSE vs Streamable HTTP) | Remote MCP server |

**Critical**: `"streamable-http"` is **NOT a valid type**. OpenCode's `"remote"` type auto-detects Streamable HTTP vs SSE based on server response headers.

---

## §3 Fixes Applied

### 3.1 OpenCode Configuration (Both Files)

**File**: `omega-engine/opencode.json` + `~/.config/opencode/opencode.json`

```json
{
  "mcp": {
    "searxng": {
      "type": "remote",
      "url": "http://127.0.0.1:8018/mcp",
      "enabled": true
    }
  }
}
```

**Changes**:
- `"type": "streamable-http"` → `"type": "remote"`
- Removed trailing slash from URL (`/mcp/` → `/mcp`)

### 3.2 SearXNG Settings Hardening (`data/searxng/config/settings.yml`)

**Removed invalid keys** (not in SearXNG schema):
- `server.user_agent` — SearXNG generates random browser UAs from `searx/data/useragents.json`
- `server.method` — Not a valid setting
- `outgoing.max_retries` → corrected to `outgoing.retries`

**Engine filtering** (`use_default_settings.engines.keep_only`):
```yaml
keep_only:
  - duckduckgo
  - google
  - wikipedia
  - arxiv
  - github
  - semantic scholar
  - youtube
  - invidious
  - stackoverflow
  - mdn
  - pypi
  - docker hub
```
- **Removed**: `brave` (consistently rate-limited), `ahmia`/`torch` (dark web, require Tor)
- **Deduplicated**: `github` appeared twice

**Added**: `outgoing.enable_http2: true` for connection pooling

### 3.3 MCP Server Code (`mcp_servers/searxng/server.py`)

- AP token bumped to `v1.1.0`
- Already using `mcp.run(transport="streamable-http", host="127.0.0.1", port=8018)` — correct
- CORS middleware added for OpenCode/Claude Code compatibility

### 3.4 Systemd Service (`omega-searxng-mcp.service`)

- Description updated: `"SSE on :8018"` → `"Streamable HTTP on :8018"`
- AP token: `v1.2.0`

### 3.5 Omega Hub Client (`mcp_servers/omega_hub/mcp_client.py`)

- Already migrated: `from mcp.client.streamable_http import streamablehttp_client`
- URL: `http://127.0.0.1:8018/mcp` — correct

---

## §4 Verification Results

### 4.1 SearXNG Container (Port 8017)

```bash
curl -s 'http://127.0.0.1:8017/config' | jq '.engines[] | select(.enabled) | .name'
# → 10 engines: arxiv, wikipedia, docker hub, duckduckgo, github, mdn, pypi, stackoverflow, semantic scholar, youtube
# → 0 unresponsive engines
# → Brave completely removed
```

### 4.2 MCP Server (Port 8018) — Streamable HTTP

| Tool | Test | Result |
|------|------|--------|
| `initialize` | Protocol handshake | ✅ 200 OK, session ID issued |
| `searxng_search` (general) | `query="Rust async 2026"` | ✅ 5 results from DuckDuckGo |
| `searxng_search` (videos) | `categories="videos", engines="youtube,invidious"` | ✅ 3 YouTube results |
| `searxng_search` (code) | `categories="it", engines="github,duckduckgo"` | ✅ Results from Docker Hub/MDN |
| `searxng_search` (science) | `categories="science", engines="arxiv,semantic_scholar"` | ✅ arXiv + Semantic Scholar |
| `searxng_health` | Health check | ✅ "SearXNG healthy: 200" |

### 4.3 OpenCode CLI

```bash
opencode mcp list
# → ✓ omega-hub  connected  http://127.0.0.1:8016/sse
# → ✓ searxng    connected  http://127.0.0.1:8018/mcp
# → ✓ firecrawl  connected  http://127.0.0.1:8015/sse
```

**Note**: The TUI (`/mcp` dialog) caches server state. **Restart OpenCode session** to see "enabled" status.

---

## §5 Architecture Diagram

```
┌─────────────────┐     Streamable HTTP      ┌──────────────────┐
│   OpenCode      │ ◄──────────────────────► │  SearXNG MCP     │
│   (type:remote) │      port 8018           │  (FastMCP 3.4.4) │
└─────────────────┘                          └────────┬─────────┘
                                                       │ HTTP POST
                                                       ▼
                                              ┌──────────────────┐
                                              │  SearXNG Core    │
                                              │  (port 8017)     │
                                              │  10 engines      │
                                              └──────────────────┘
```

---

## §6 Lessons Learned

1. **OpenCode MCP config**: Only `"local"` and `"remote"` are valid types. `"remote"` auto-detects Streamable HTTP.
2. **Global vs Project config**: Global (`~/.config/opencode/opencode.json`) overrides project. Both must be in sync.
3. **Trailing slashes matter**: `/mcp/` vs `/mcp` caused 406 on SSE attempt.
4. **SearXNG settings**: Many "obvious" keys (`user_agent`, `method`) don't exist. Always check `docs.searxng.org/admin/settings/`.
5. **TUI caching**: OpenCode's `/mcp` dialog caches connection state. CLI `opencode mcp list` reads fresh config.

---

## §7 Related Files

| File | Purpose |
|------|---------|
| `omega-engine/opencode.json` | Project MCP config |
| `~/.config/opencode/opencode.json` | Global MCP config |
| `data/searxng/config/settings.yml` | SearXNG engine config |
| `mcp_servers/searxng/server.py` | FastMCP Streamable HTTP server |
| `.config/containers/systemd/omega-searxng-mcp.service` | Systemd unit |
| `mcp_servers/omega_hub/mcp_client.py` | Hub's MCP client (streamablehttp) |
| `mcp_servers/omega_hub/state.py` | Hub's server URL config |

---

## §8 Next Steps

- [ ] Add SearXNG MCP to background researcher worker for automated research cycles
- [ ] Document `categories`/`engines` mapping for agent prompts (Jem, Researcher)
- [ ] Consider adding `searxng_search` to `omega-hub` tool registry for cross-agent access

---

*🔱 OMEGA ⬡ SEARXNG-MCP ⬡ v1.1.0 ⬡ STREAMABLE-HTTP COMPLETE*