# 🔱 OPENCODE CRASH REMEDIATION GUIDE
**Date**: 2026-09-24
**Author**: Antigravity IDE
**Context**: Post-debut OpenCode (Zed/VS Code fork) initialization failures.

---

## 1. The Incident

Following the Hub networking modifications (binding `omega-hub` to 127.0.0.1 and proxying via Tailscale), the local instance of OpenCode began suffering fatal, black-screen crashes immediately upon launch.

**Symptoms:**
- The client binary would fail to load entirely.
- In later tests, it would load the UI structure but go black immediately upon loading plugins.

## 2. Root Cause Analysis

We discovered two distinct failure vectors occurring simultaneously in the `~/.config/opencode/` directory:

### Vector A: Configuration Corruption (`opencode.json`)
The primary configuration file (`opencode.json`) had been truncated to a bare 67-byte skeleton that lacked all provider definitions. OpenCode's initialization sequence expects a fully formed provider schema (or gracefully handles empty ones, but the truncated state caused a fatal parse error).
- **Remediation**: Restored a known-good backup. Initially, we restored a bloated September 18th config, which allowed the UI to load, but triggered Vector B. Ultimately, we restored the lightweight `zenfix` backup from September 23rd (`opencode.json.bak.zenfix.20260923T184645Z`), which stripped out legacy GGUF provider configurations.

### Vector B: Third-Party MCP Server Failure (`mcp_servers.json`)
OpenCode's `mcp_servers.json` contained several `npx`-based third-party MCP servers (`tavily`, `firecrawl`, `searxng`, `jina`). When OpenCode launches, it attempts to spawn all these servers concurrently. If an `npx` subprocess fails fatally (e.g., SearXNG offline on port 8017, or a revoked OpenRouter key blocking a startup check), it can pull down the entire OpenCode client.
- **Remediation**: We quarantined the old file to `mcp_servers.json.bak` and created a minimal `mcp_servers.json` containing *only* the `omega-hub` connection.

## 3. The Resolution

By applying the `zenfix` configuration and isolating the MCP servers to just the `omega-hub`, OpenCode launched flawlessly. 

**Critical Discovery**: 
The `omega-hub` networking changes (Tailscale proxy, 127.0.0.1 binding) **did not** cause the crash. The hub connected perfectly via `http://127.0.0.1:8016/mcp`. 

## 4. SOP: Restoring Third-Party Tools

If the team needs the external web search MCPs restored, follow this procedure:
1. Open `~/.config/opencode/mcp_servers.json`.
2. Copy **one** server block (e.g., `tavily`) from the `.bak` file.
3. Launch OpenCode. 
4. If it crashes, that specific node/process is the culprit. Do not add them all at once.
