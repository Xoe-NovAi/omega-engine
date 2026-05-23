# 🔱 OpenCode MCP Hardening & Connectivity Guide
**AP Token**: `AP-MCP-HARDENING-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_core ⬡ INTERFACE-HARDENING

## 🛡️ Executive Summary
This document outlines the critical configuration and runtime requirements for maintaining a stable MCP (Model Context Protocol) fabric within the OpenCode environment.

## ⚙️ Configuration Architecture

### 1. The Merged Config Model
OpenCode utilizes a dual-layer configuration system:
- **Global Registry** (`~/.config/opencode/mcp_servers.json`): The primary source of truth. Uses the standard `mcpServers` key.
- **Project Local** (`opencode.json`): Project-specific overrides and additions. Uses the `mcp` key.

**Precedence**: Local `opencode.json` entries are merged into the global registry at runtime.

### 2. Server Type Requirements
OpenCode requires an explicit `type` field to determine the communication protocol. Failure to provide this results in the server being ignored.

| Type | Communication | Lifecycle | Config Requirement |
| :--- | :--- | :--- | :--- |
| `stdio` | Standard I/O | Spawned by OpenCode | `command` + `args` |
| `sse` | Server-Sent Events | **Passive** (Must be pre-running) | `url` |
| `remote` | HTTP/JSON-RPC | Always-on Cloud | `url` + `headers` |

## 🚀 Runtime Stability & Troubleshooting

### 1. The SSE Passive Gap
Unlike `stdio` servers, `sse` servers (like the Omega Core Hub) are not managed by OpenCode. If the underlying process (e.g., a systemd unit) is down, the server will simply disappear from `/status` without a specific error message.

**Verification**: Always use `curl -I <url>/sse` to verify the endpoint is emitting events before debugging OpenCode.

### 2. The `npx` Startup Timeout
Local servers launched via `npx` are subject to a **30-second startup timeout**. Slow network resolution or heavy system load can cause these servers to be marked as "down" even if they eventually start.

**Optimization**: Replace `npx -y <package>` with absolute paths to installed binaries in `node_modules` to bypass the resolution phase.

### 3. Permission & Pathing
Ensure that the `external_directory` whitelist in `opencode.json` covers all paths accessed by the `filesystem` MCP server to avoid "Permission Denied" errors.

## 🛠️ Recovery Protocol
When MCP servers are missing from `/status`:
1. **Check Process**: `ss -tulpn | grep <port>`
2. **Verify Endpoint**: `curl -I <url>/sse`
3. **Audit Config**: Ensure `type` is explicitly defined in `opencode.json`.
4. **Restart Services**: `systemctl --user restart <service>.service`
