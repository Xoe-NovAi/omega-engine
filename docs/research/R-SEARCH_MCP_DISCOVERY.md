# R-SEARCH_MCP_DISCOVERY – Search MCP Integration Deep Dive

**AP Token**: `AP-SEARCH-MCP-DISCOVERY`
**Date**: 2026-05-15
**Prepared by**: Omega Master Researcher (DeepSeek Flash V4)

## 🔍 Core Findings

### 1. The MCP Disconnect Crisis
**Symptom**: Search MCP servers (Exa, Brave, Tavily) are absent from `/status` output and not starting.

**Root Cause**: 
- **Architectural Decoupling**: The current discovery pipeline (`src/omega/library/discovery.py`) implements direct HTTP REST calls to providers. It does not use the MCP protocol for search.
- **Orphaned Config**: The entries in `opencode.json` for these servers are purely descriptive and are never instantiated by the engine.
- **Config Override**: The global `~/.config/opencode/mcp_servers.json` was empty, overriding project-local settings and disabling the filesystem MCP server.

### 2. The Filesystem Access Block
**Symptom**: `filesystem_*` tools return "Access denied - path outside allowed directories".

**Root Cause**:
- **Permission Mismatch**: The OpenCode permission rules deny `external_directory` access by default. The project root (`/home/arcana-novai/Documents/Xoe-NovAi/omega-engine`) is not explicitly added to the allow list.
- **MCP Server Failure**: The filesystem MCP server fails to start or register the project root because of the global config override.

### 3. Dependency Drift
**Symptom**: `npx` fails to find search server packages.

**Root Cause**: Package names in `opencode.json` were stale.
- `@anthropic/brave-search-mcp-server` $\rightarrow$ `@brave/brave-search-mcp-server`
- `tavily-mcp-server` $\rightarrow$ `tavily-mcp`

## 🛠️ Temple-Grade Solutions

### ✅ Immediate Remediation (Applied)
- **Config Cleanup**: Fixed package names in `opencode.json` for Brave and Tavily.
- **Localised Exa**: Switched from remote SSE to local `exa-mcp-server` to improve privacy and latency.

### 🚀 Strategic Path Forward (Sovereign Search Fabric)

**Step 1: Configuration Alignment**
- Prune obsolete search MCP entries from `opencode.json` to remove confusion.
- Update `docs/README.md` and `R27_web_research_audit.md` to document the direct HTTP architecture.

**Step 2: Unified MCP Wrapper (The "Sovereign Bridge")**
- Implement lightweight Python wrappers in `src/omega/mcp/` for Exa, Brave, and Tavily.
- These wrappers will handle the HTTP calls but present as MCP servers.
- Register these in `Orchestrator.mcp_ports` so they are monitored by `/status`.
- Update `DiscoveryOrchestrator` to use the MCP client protocol.

**Step 3: Permission Hardening**
- User must add the project root to the `external_directory` allow list in the OpenCode settings to restore `filesystem_*` tool functionality.

## 🏁 Final Verification
The discovery pipeline is verified and functional using keys from `.env`. The `/status` discrepancy is a known architectural artifact of the current MVE implementation.

---
*End of report.*
