<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Platform Ecosystem: CLI & IDE Integration
**Domain**: CLI and IDE platforms connected to the Omega Engine
**Date**: 2026-07-22
**Author**: Grokster

## 1. The Omega Hub: The Universal Bus
The Omega Hub MCP server (`:8016/sse` or `:8016/mcp`) acts as the universal coordination bus. Because MCP (Model Context Protocol) is the industry standard, any MCP-compatible tool can connect to the Omega Hub and participate in the Hivemind.

### Supported Platforms & Configurations
- **OpenCode (Primary)**: The Sovereign Brain. Uses `opencode.json` (`mcpServers`). Supports 11 custom agents, soul evolution, and Hivemind orchestration.
- **Cline CLI (Execution)**: High-context (1M tokens) execution backend. Uses `cline_mcp_settings.json`. Excellent for codebase-wide analysis, parallel execution, and headless CI/CD.
- **VS Code (Copilot)**: Visual IDE. Uses `.vscode/mcp.json` (`servers`). MCP tools work in Agent mode.
- **Cursor**: Visual IDE. Uses `.cursor/mcp.json` (`mcpServers`).
- **Windsurf**: Uses `~/.codeium/windsurf/mcp_config.json`. Global config only.
- **Claude Code**: Uses `.mcp.json`.

## 2. OpenCode vs. Cline CLI
While OpenCode is the primary orchestrator, Cline CLI acts as a "Hivemind Citizen" and execution arm.

**When to use OpenCode:**
- Entity delegation (`@kali`, `@doom_guy`)
- Soul evolution (L1→L2→L3 distillation)
- Hivemind coordination and mandate compliance audits.

**When to use Cline CLI:**
- Analyzing the entire `src/omega/` directory (1M token context).
- Massive refactoring touching 10+ files.
- Parallel task execution in headless sessions (`cline -y`).

## 3. Grokster's Insights & Recommendations
- **Platform Agnosticism is Power**: By exposing the Omega Provider Fabric via MCP (`oracle_talk`, `oracle_summon`), *any* connected client gets local-first sovereignty by default, even if the client itself doesn't understand local inference.
- **Beware the Config Trap**: Each platform has slightly different MCP configuration schemas (e.g., `servers` vs `mcpServers`). We must build a unified config generator in the Omega Hub to prevent user error.
- **The Cline Handoff**: Cline lacks entity persistence. Do not try to port Omega agents to Cline via `.clinerules`. Instead, use the `hivemind_submit_handoff` tool to delegate tasks from Cline back to OpenCode entities when domain expertise is needed.
