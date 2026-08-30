# 🔬 Cline — Knowledge Base
# ⬡ OMEGA ⬡ KALI ⬡ trc_platform_kb ⬡ v1.1.0
**Source**: Forensic Research Wave 2 (2026-06-07)
**Status**: FULLY SEEDED
**Last Updated**: 2026-06-07

---

## §1: Overview
Cline (formerly Claude Dev) is a high-privilege AI coding agent primarily implemented as a VS Code extension.

- **Runtime**: Node.js / TypeScript.
- **Process Model**: Runs within the `vscode-extension-host` process.
- **Binary**: distributed as `.vsix` package. Logic in `~/.vscode/extensions/saoudrizwan.claude-dev-*/dist/extension.js`.

---

## §2: Architecture & Control
### Daemon & API
- **Daemon Mode**: None native. Cline is a "guest" in the VS Code process.
- **API**: No public HTTP/WebSocket API. Communication is via internal VS Code RPC.
- **ACP Status**: Unknown if a hidden ACP layer exists.

### Control Strategy: Indirect Steering
Because there is no headless daemon, control is achieved via the **MCP Layer**:
1. Omega Engine implements a **Sovereign Steering MCP Server**.
2. This server is added to Cline's `cline_mcp_settings.json`.
3. Omega provides "Knowledge Tools" that Cline must call.
4. Omega returns tool results containing **Implicit Steering Instructions** to guide Cline's next step.

---

## §3: Session & Memory Architecture
- **Storage Mechanism**: JSON files for history + SQLite for metadata.
- **Path (Linux)**: `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/`
- **Session IDs**: UUIDs or Timestamped Hashes.
- **Memory Pattern**: Rolling window of context.

---

## §4: MCP Integration
- **MCP Client**: Native high-privilege MCP client.
- **Configuration**: `cline_mcp_settings.json` (Global) or `.cline/mcp.json` (Project).
- **Sovereignty**: The MCP layer is the primary entry point for external orchestration.

---

## §5: Key File Path Summary

| Component | Absolute Path |
| :--- | :--- |
| **Extension Logic** | `~/.vscode/extensions/saoudrizwan.claude-dev-*/dist/extension.js` |
| **Global Storage** | `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/` |
| **MCP Config** | `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/cline_mcp_settings.json` |
| **Project Config** | `.cline/` (Project Root) |
| **Project MCP** | `.cline/mcp.json` |

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_platform_kb | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
