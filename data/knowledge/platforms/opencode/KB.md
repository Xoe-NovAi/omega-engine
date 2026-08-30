<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔬 OpenCode CLI — Knowledge Base
# ⬡ OMEGA ⬡ KALI ⬡ trc_platform_kb ⬡ v1.2.0
**Source**: 6-wave research (R1-R4, 2026-06-07)
**Status**: FULLY SEEDED
**Last Updated**: 2026-06-07

---

## §1: Overview
OpenCode is an open-source AI coding assistant (MIT, `github.com/anomalyco/opencode`, 171K stars). TypeScript stack: Effect (functional), Hono (HTTP), Drizzle (ORM), Bun (runtime + SQLite).

- **Binary**: `~/.opencode/bin/opencode` (ELF 64-bit, v1.15.13+)
- **Config**: `~/.config/opencode/opencode.json` (global), `<project>/opencode.json` (project)
- **Plugin system**: `@opencode-ai/plugin@1.4.0` — 25+ hooks
- **SDK**: `@opencode-ai/sdk@1.4.0` — auto-generated from OpenAPI spec
- **Python SDK**: `pip install --pre opencode-ai`

---

## §2: Architecture — Interactive + Headless Daemon
**CRITICAL**: When `opencode` runs interactively, it spawns `opencode serve --register` as a detached daemon on port 4096. The TUI is an HTTP **client** of this daemon, not a standalone process.

### Native Control Surface (v1.15.13+)
| Endpoint/Event | Type | Worker Utility |
| :--- | :--- | :--- |
| `/global/event` | SSE Stream | Real-time observability of all session events. |
| `session.next.*` | Event | Tracing reasoning cycles and tool execution. |
| `session.next.reasoning`| Event | Access to native "hidden" chain-of-thought. |
| `question.*` | Event | Active steering via `question.replied` API. |
| `tui.toast.show` | API | Injecting notifications directly into the user's TUI. |
| `/v2` Routes | JSON-RPC | Programmatic access to models and messages. |

---

## §3: SQLite Session Store
**Path**: `~/.local/share/opencode/opencode.db` (350MB, WAL mode)
**Tables**: 16 (session, message, part, project, session_message, event, etc.)

**ID Formats**:
- Session: `ses_` (base62)
- Message: `msg_` (base62)
- Part: `prt_` (base62)

**Part types**: `text`, `reasoning`, `tool`, `step-start`, `step-finish`, `file`, `patch`, `compaction`, `agent`

---

## §4: Antigravity Integration
**Plugin**: External `npm:opencode-antigravity-auth` at `NoeFabris/opencode-antigravity-auth`
**Config**: `~/.config/opencode/antigravity.json` (strategy), `antigravity-accounts.json` (OAuth2 tokens)

**To disable rotation**: Set `"account_selection_strategy": "sticky"` in `antigravity.json`.

---

## §5: Compaction System
Compaction runs in two phases. **Neither deletes data from SQLite.**
- **Phase 1 — Prune**: Marks tool `part` rows as compacted. Set `"prune": false` to disable.
- **Phase 2 — Summarize**: LLM generates a structured summary. Keep `"auto": true`.
- **Config fix**: Set `"prune": false`, increase `"tail_turns": 5`.

**Plugin hook**: `experimental.session.compacting` — fires before LLM summary.

---

## §6: Native Capabilities Matrix (v1.15.13+)
| Feature | CLI Command | API/Event | Utility |
| :--- | :--- | :--- | :--- |
| **Session Discovery** | `session list` | `/session` | Identify target sessions. |
| **Prompt Injection** | `run [msg]` | `/v2/prompt` | Headless steering. |
| **State Export** | `export [id]` | `/session/export` | High-fidelity snapshots. |
| **TUI Notification** | N/A | `tui.toast.show` | User alerts. |
| **MCP Management** | `mcp add/list` | `/mcp` | Tool expansion. |
| **Resource Audit** | `stats` | `/stats` | Token/Cost tracking. |

---

## §7: Key File Paths

| Component | Absolute Path |
| :--- | :--- |
| **Main config** | `~/.config/opencode/opencode.json` |
| **Project config** | `<project>/opencode.json` |
| **SQLite DB** | `~/.local/share/opencode/opencode.db` |
| **Antigravity config** | `~/.config/opencode/antigravity.json` |
| **Antigravity accounts** | `~/.config/opencode/antigravity-accounts.json` |
| **SDK** | `~/.config/opencode/node_modules/@opencode-ai/sdk/` |
| **Plugin SDK** | `~/.config/opencode/node_modules/@opencode-ai/plugin/` |
| **Snapshot storage** | `~/.local/share/opencode/snapshot/` |
| **Binary** | `~/.opencode/bin/opencode` |
| **Server registration** | `~/.local/share/opencode/server.json` |
| **Auth** | `~/.local/share/opencode/auth.json` |

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_platform_kb | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
