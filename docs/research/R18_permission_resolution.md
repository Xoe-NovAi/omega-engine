# 🔱 Omega Engine — R-18: OpenCode Permission Resolution Guide

**AP Token**: `AP-R18-RESOLVE-v1.0.0`
**Status**: RESOLVED
**Date**: 2026-05-14
**Agent**: Gemma 4-31B (Sovereign Master Researcher)

---

## 1. Problem Statement
The Research Agent encountered "Access Denied" errors when using `filesystem_*` tools (e.g., `filesystem_list_directory`, `filesystem_read_text_file`) while attempting to access critical project directories such as `.opencode/agents/` and `docs/`. Conversely, the `read` and `edit` tools continued to function normally.

## 2. Technical Audit

### 2.1 Tool Divergence
The OpenCode CLI provides two distinct sets of filesystem interaction tools:

| Tool Set | Examples | Permission Model | Access Level |
| :--- | :--- | :--- | :--- |
| **Native Tools** | `read`, `edit`, `write` | Privileged / System-level | Broad access within the environment boundaries. |
| **Filesystem Tools** | `filesystem_read_text_file`, `filesystem_list_directory` | Whitelist-based | Restricted to specifically "Allowed Directories." |

### 2.2 The "Allowed Directories" Mechanism
The `filesystem_*` toolset is powered by the `@modelcontextprotocol/server-filesystem` MCP server. This server implements a security boundary that prevents the agent from accessing files outside of a pre-defined set of paths.

The source of truth for these allowed paths is the `opencode.json` configuration file. Specifically, the `mcp.filesystem.args` array defines the root directories that the server is permitted to access.

### 2.3 Root Cause Analysis
The audit revealed that `filesystem_list_allowed_directories` returned an empty list. This occurred because:
1. The workspace-root `opencode.json` did not contain a configuration for the `filesystem` MCP server.
2. The global configuration in `~/.config/opencode/opencode.json` (which did contain the allowed path) was being overridden or ignored in favor of the local workspace configuration.
3. Without an explicit configuration in the active `opencode.json`, the `filesystem` MCP server initialized with an empty whitelist, resulting in "Access Denied" for all paths.

---

## 3. Resolution

### 3.1 Implementation
To resolve this, the `filesystem` MCP server configuration must be explicitly declared in the project's root `opencode.json` file.

**Required Configuration Block:**
```json
"mcp": {
  "filesystem": {
    "type": "local",
    "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem"],
    "args": ["/home/arcana-novai/Documents/Xoe-NovAi/omega-engine"],
    "enabled": true
  }
}
```

### 3.2 Verification Steps
1. **Update Config**: Add the above block to the `mcp` section of `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json`.
2. **Check Allowed List**: Run `filesystem_list_allowed_directories`. It should now return the workspace root path.
3. **Test Access**: Attempt to list the contents of `.opencode/agents/` using `filesystem_list_directory`.

---

## 4. Prevention of Regression
To prevent this issue in future sessions or when onboarding new agents:
- **Template Config**: Include the `filesystem` MCP server in the base `opencode.json` template for all new Omega Engine stacks.
- **Absolute Paths**: Always use absolute paths in the `args` array to avoid ambiguity across different shell environments.
- **Config Audit**: If "Access Denied" occurs despite the file existing, the first step should be to run `filesystem_list_allowed_directories` to verify the active whitelist.

## 5. Implementation Note
**To the Implementation Agent**: Ensure that any new workspace root established during project relocation is mirrored in the `opencode.json` `filesystem.args` list immediately to maintain autonomous agent capabilities.
