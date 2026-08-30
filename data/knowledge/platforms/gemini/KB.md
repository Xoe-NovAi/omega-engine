<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔬 Gemini CLI — Knowledge Base
# ⬡ OMEGA ⬡ KALI ⬡ trc_platform_kb ⬡ v1.2.0
**Source**: Forensic Research Wave 1 (2026-06-07)
**Status**: FULLY SEEDED
**Last Updated**: 2026-06-07

---

## §1: Overview
Gemini CLI is a high-performance agentic interface for Google's Gemini models. It is distributed as a bundled Node.js application.

- **Binary**: `/home/arcana-novai/.nvm/versions/node/v25.9.0/bin/gemini`
- **Version**: `0.45.2` (Stable)
- **Runtime**: Node.js v25.9.0

---

## §2: Configuration & Auth
### Config Hierarchy (Precedence: Low $\rightarrow$ High)
1. **System Defaults**: `/etc/gemini-cli/system-defaults.json`
2. **User Settings**: `~/.gemini/settings.json`
3. **Project Context**: `~/.gemini/tmp/<project>/`
4. **Env Vars**: `GEMINI_API_KEY`, `GOOGLE_CLOUD_PROJECT`

### Critical Headless Settings
- `stream`: Boolean (controls response streaming)
- `max_history_items`: Integer (context window size)
- `telemetry_opt_out`: Boolean (MUST be `true` for sovereign compliance)
- `model.maxSessionTurns`: Integer (limits session length)

### Auth State
- **Credential Cache**: `/home/arcana-novai/.gemini/oauth_creds.json` (OAuth2 tokens)

---

## §3: ACP (Agent Client Protocol) & Headless API
Gemini CLI implements **ACP (JSON-RPC 2.0)** for programmatic control.

### Core Methods
| Method | Payload | Purpose |
| :--- | :--- | :--- |
| `session/create` | `{ "name": string, "model": string }` | New session |
| `session/prompt` | `{ "sessionId": string, "prompt": string, "stream": boolean }` | Submit prompt |
| `session/load` | `{ "sessionId": string }` | Hydrate from store |
| `session/close` | `{ "sessionId": string }` | Flush and close |
| `agent/execute_tool`| `{ "tool": string, "args": object }` | Trigger tool |

### Headless Operation
- Triggered via `-p` or `--prompt` for single-shot.
- ACP mode enabled via `--acp` for stateful programmatic control.

---

## §4: Session & Memory Architecture
### The JSONL Store
- **Path**: `~/.gemini/tmp/<project_name>/chats/*.jsonl`
- **Project Hash**: Truncated SHA-256 of the absolute project root path.
- **Structure**: JSON Lines. First line is metadata; subsequent lines are state changes (`$set`) or messages.
- **Branching**: Uses a "Parent Pointer" system with `{"type": "branch_point", "id": "msg_xxx"}` markers.
- **Retention**: Default 120 days, configurable via `settings.json`.

---

## §5: MCP Integration
- **Client**: Discovers servers via `~/.config/gemini/mcp_config.json`. Supports SSE transport.
- **Server**: Can be wrapped as an MCP server using `--acp` mode.
- **Auth**: Passes OAuth tokens from `oauth_creds.json` to remote MCP servers.

---

## §6: Key File Path Summary

| Component | Absolute Path |
| :--- | :--- |
| **Binary** | `/home/arcana-novai/.nvm/versions/node/v25.9.0/bin/gemini` |
| **User Settings** | `/home/arcana-novai/.gemini/settings.json` |
| **Auth Tokens** | `/home/arcana-novai/.gemini/oauth_creds.json` |
| **MCP Config** | `/home/arcana-novai/.config/gemini/mcp_config.json` |
| **Session Store** | `/home/arcana-novai/.gemini/tmp/<project>/chats/*.jsonl` |
| **Tmp Outputs** | `/home/arcana-novai/.gemini/tmp/<project>/tool-outputs/` |

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_platform_kb | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
