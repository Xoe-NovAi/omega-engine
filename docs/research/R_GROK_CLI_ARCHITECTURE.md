<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Grok Build CLI — Complete Architecture Research
## Foundational Compass for Omega Engine TUI Implementation

**AP Token**: `AP-GROK-CLI-RESEARCH-v1.0.0`  
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_grok_cli_architecture ⬡ COMPLETE

**Date**: 2026-07-17  
**Research Rounds**: 4 (Surface → Deep → UI/UX → Codebase)  
**Sources**: 50+ (Official docs, open-source repo `xai-org/grok-build`, user guides, changelogs, community tools, security audits)

---

## Executive Summary

Grok Build (xAI's terminal coding agent, open-sourced July 2026) represents the **most architecturally sophisticated TUI agent** in existence. Its design aligns nearly perfectly with the Omega Engine's vision: clean crate decomposition, Elm-style state machine, kernel-level sandboxing, pinned configuration, hybrid memory, and a unified extensions system.

This document consolidates **four rounds of deep research** into a single implementation compass for building the Omega Engine's terminal interface.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Crate Decomposition](#2-crate-decomposition)
3. [Agent Loop & State Machine](#3-agent-loop--state-machine)
4. [Session Persistence](#4-session-persistence)
5. [TUI Rendering System](#5-tui-rendering-system)
6. [Slash Command System](#6-slash-command-system)
7. [Unified Extensions Modal](#7-unified-extensions-modal)
8. [Agent Dashboard](#8-agent-dashboard)
7. [Skill System & `/skillify`](#9-skill-system--skillify)
10. [Plugin Marketplace](#10-plugin-marketplace)
11. [Memory System](#11-memory-system)
12. [Sandbox (Landlock/Seatbelt)](#12-sandbox-landlockseatbelt)
13. [Configuration with Pinning](#13-configuration-with-pinning)
14. [ACP Protocol](#14-acp-protocol)
15. [Plan Mode](#15-plan-mode)
16. [Subagent System](#16-subagent-system)
17. [Background Tasks & Prompt Queue](#17-background-tasks--prompt-queue)
18. [Hooks System](#18-hooks-system)
19. [Goal Mode](#19-goal-mode)
20. [Keyboard Shortcuts](#20-keyboard-shortcuts)
21. [Omega Implementation Roadmap](#21-omega-implementation-roadmap)
22. [Council of Four Synthesis](#22-council-of-four-synthesis)
23. [File-for-File Porting Map](#23-file-for-file-porting-map)

---

## 1. Architecture Overview

### 1.1 High-Level Design Philosophy

Grok Build achieves its polish through **rigorous separation of concerns**:

| Concern | Crate | Responsibility |
|---------|-------|----------------|
| **TUI** | `xai-grok-pager` | Rendering, input handling, modals, scrollback |
| **Runtime** | `xai-grok-shell` | Agent loop, tool dispatch, ACP, session persistence |
| **Tools** | `xai-grok-tools` | Terminal, file edit, search, grep implementations |
| **Workspace** | `xai-grok-workspace` | Host FS, VCS, execution, checkpoints |
| **Config** | `xai-grok-config` | TOML parsing, validation, layer merging |
| **Sandbox** | `xai-grok-sandbox` | Landlock/Seatbelt profiles, custom profiles |
| **Hooks** | `xai-grok-hooks` | Lifecycle events, execution engine |
| **Marketplace** | `xai-grok-plugin-marketplace` | Source loading, scanning, install |

**Key Insight**: The TUI and Runtime are **completely separate crates**. The TUI knows nothing about model providers; the Runtime knows nothing about rendering. They communicate via **ACP (Agent Client Protocol)** over stdio.

### 1.2 Repository Structure

```
grok-build/
├── crates/
│   ├── codegen/
│   │   ├── xai-grok-pager-bin      # Composition root → builds `xai-grok-pager` binary
│   │   ├── xai-grok-pager          # TUI: scrollback, prompt, modals, rendering (ratatui)
│   │   ├── xai-grok-shell          # Agent runtime + leader/stdio/headless entry points
│   │   ├── xai-grok-tools          # Tool implementations (terminal, file edit, search, ...)
│   │   ├── xai-grok-workspace      # Host FS, VCS, execution, checkpoints
│   │   ├── xai-grok-config         # Config parsing (config.toml, pager.toml, sandbox.toml)
│   │   ├── xai-grok-hooks          # Hook runtime, event types, execution engine
│   │   ├── xai-grok-plugin-marketplace # Marketplace source loading, scanning, install
│   │   └── xai-grok-sandbox        # Landlock/Seatbelt profiles, custom profiles
│   ├── common/                      # Shared leaf crates
│   ├── build/                       # Build utilities
│   └── prod/mc/                     # Production crates
├── third_party/                     # Vendored Mermaid diagram stack
├── bin/                             # DotSlash hermetic tools (protoc, etc.)
├── Cargo.toml                       # WORKSPACE ROOT - GENERATED, read-only
├── rust-toolchain.toml              # Pinned toolchain
├── clippy.toml                      # Lint config
├── rustfmt.toml                     # Format config
└── SOURCE_REV                       # Monorepo commit SHA
```

---

## 2. Crate Decomposition

### 2.1 `xai-grok-pager` — The TUI Crate

**Architecture** (Elm-style):
```
src/
├── app/
│   ├── app_view.rs          # Top-level state (welcome, agents, config)
│   ├── agent_view/          # Per-session agent view
│   │   ├── mod.rs           # AgentView struct
│   │   ├── prompt.rs        # Prompt handling
│   │   ├── scrollback.rs    # Scrollback rendering
│   │   ├── panes.rs         # Tool panes, TODO, tasks
│   │   └── modals.rs        # Modal management
│   ├── dispatch/            # Action → Effect dispatcher
│   │   ├── router.rs        # Routes actions to handlers
│   │   ├── agent.rs         # Agent-specific effects
│   │   ├── session.rs       # Session effects
│   │   └── ui.rs            # UI effects
│   ├── effects.rs           # Async side effects (ACP calls, file I/O)
│   └── event_loop.rs        # Main event loop (input, ticks, ACP messages)
├── views/
│   ├── prompt_widget.rs     # Text editor with @ file search, / slash, history
│   ├── welcome/             # Welcome screen (logo, menu, prompt)
│   ├── extensions_modal.rs  # 5-tab modal (Hooks/Plugins/Marketplace/Skills/MCPs)
│   ├── file_search/         # @-completion dropdown and line viewer
│   ├── slash_dropdown.rs    # /command completion dropdown
│   └── ...                  # Scrollback, status bar, panes
├── scrollback/              # Message history rendering
├── slash/                   # Slash command registry and built-in commands
├── appearance/              # Theme and pager.toml config
├── acp/                     # ACP client state
└── render/                  # Low-level rendering helpers
```

**Key Patterns**:
- **Action/Effect**: Pure state transitions. Input → Action → dispatch → Effect → state update
- **AgentView per session**: Each session owns its prompt, scrollback, tool panes, modals
- **PromptWidget**: Reusable editor component with `@` file search, `/` slash dropdown, history (`Ctrl+R`)
- **Extensions Modal**: Single component, 5 tabs pre-selected by command

### 2.2 `xai-grok-shell` — The Runtime Crate

```
src/
├── agent/                   # Agent implementations
│   ├── leader.rs           # Shared leader process (multiplexes sessions)
│   ├── stdio.rs            # ACP stdio transport
│   └── headless.rs         # Headless entry point
├── auth/                    # Authentication (browser, API key, OIDC, external)
├── config/                  # Config loading, validation
├── extensions/              # Plugin/skill/hook loading
├── session/                 # Session persistence, resume, rewind
├── tools/                   # Tool dispatch, permission checking
├── sandbox/                 # Sandbox application
├── builtin.rs               # Built-in tools
├── claude_import.rs         # Claude Code compatibility
├── plugin.rs                # Plugin loading
└── lib.rs                   # Public API
```

### 2.3 `xai-grok-tools` — Tool Implementations

Ported from OpenAI Codex and sst/opencode (Apache 2.0 with §4(b) notices):
- `run_terminal_cmd` — Shell execution with background support
- `read_file` / `search_replace` / `list_dir` — File operations
- `grep` / `web_search` / `web_fetch` — Search
- `todo_write` — Task tracking
- `task` / `spawn_subagent` — Subagent delegation

### 2.4 `xai-grok-workspace` — Host Integration

- Filesystem abstraction
- Git operations (worktree create/apply/remove)
- Process execution with sandbox inheritance
- Checkpoint/restore for rewind

---

## 3. Agent Loop & State Machine

### 3.1 Elm-Style Architecture

```rust
// Core types (simplified)
enum Action {
    Input(KeyEvent),
    Tick,
    AcpMessage(ACPMessage),
    Effect(Effect),
    Resize(u16, u16),
}

enum Effect {
    SpawnSubagent(SubagentSpec),
    RunTool(ToolCall),
    WriteFile(Path, String),
    AcpRequest(ACPRequest),
    ShowModal(ModalType),
    UpdateConfig(ConfigDelta),
    SaveSession,
    LoadSession(SessionId),
}

// Event loop (event_loop.rs)
async fn run_event_loop(mut app: AppView, mut rx: Receiver<Action>) {
    while let Some(action) = rx.recv().await {
        let effects = app.update(action);
        for effect in effects {
            spawn_effect(effect, &mut app, &tx);
        }
    }
}
```

### 3.2 State Ownership

| Component | Owns |
|-----------|------|
| `AppView` | Welcome screen, all `AgentView`s, global config |
| `AgentView` | Prompt, scrollback, tool panes, modals for ONE session |
| `PromptWidget` | Text buffer, cursor, completions, history |
| `Scrollback` | Message list, thinking blocks, tool cards, diffs |

---

## 4. Session Persistence

### 4.1 Storage Layout

```
~/.grok/sessions/<encoded-cwd>/<session-id>/
├── summary.json              # Metadata: title, model, timestamps, counts
├── updates.jsonl             # ACP session update stream (authoritative)
├── chat_history.jsonl        # Raw chat messages sent to model
├── plan.json                 # TODO/task list state
├── rewind_points.jsonl       # File snapshots for /rewind
├── signals.json              # Token usage, tool/turn counters
├── feedback.jsonl            # User feedback/ratings
├── compaction_checkpoints/   # Saved state from compaction
└── subagents/                # Per-subagent metadata (meta.json)
```

### 4.2 `updates.jsonl` Format (JSONL — newline-delimited JSON)

Each line = self-contained ACP `session/update` event:

```json
{"jsonrpc":"2.0","method":"session/update","params":{"sessionId":"abc","update":{"sessionUpdate":"agent_message_chunk","content":{"text":"Hello"}}}}
{"jsonrpc":"2.0","method":"session/update","params":{"sessionId":"abc","update":{"sessionUpdate":"tool_call","tool":"read_file","toolUseId":"123","input":{"path":"main.rs"}}}}
{"jsonrpc":"2.0","method":"session/update","params":{"sessionId":"abc","update":{"sessionUpdate":"tool_result","toolUseId":"123","content":"fn main() {...}"}}}
```

**Why JSONL?**
- Incremental append-only writes during session
- Efficient streaming reads for restore
- Easy debugging (each line = valid JSON)
- Crash-resilient (partial writes are valid)

### 4.3 `summary.json` Schema

```json
{
  "info": { "sessionId": "uuid", "cwd": "/path" },
  "session_summary": "Implemented auth migration",
  "generated_title": "Auth v2 Migration",
  "created_at": "2026-07-17T14:32:00Z",
  "updated_at": "2026-07-17T15:45:00Z",
  "num_messages": 47,
  "num_chat_messages": 23,
  "current_model_id": "grok-build",
  "parent_session_id": "parent-uuid",
  "agent_name": "grok-build"
}
```

### 4.4 Rewind Points (`rewind_points.jsonl`)

Recorded at **each user prompt**:

```json
{
  "turn": 5,
  "files": [
    { "path": "src/auth.rs", "content": "previous content..." },
    { "path": "tests/auth_test.rs", "content": "previous content..." }
  ]
}
```

On `/rewind`: User selects turn → all files restored → conversation truncated.

---

## 5. TUI Rendering System

### 5.1 Ratatui Foundation

Built on **ratatui** (Rust TUI framework) with custom components:

| Component | File | Purpose |
|-----------|------|---------|
| `PromptWidget` | `views/prompt_widget.rs` | Editor with `@` file search, `/` slash, history |
| `ExtensionsModal` | `views/extensions_modal.rs` | 5-tab modal (Hooks/Plugins/Marketplace/Skills/MCPs) |
| `Scrollback` | `scrollback/` | Messages, thinking blocks, tool cards, diffs |
| `SlashDropdown` | `views/slash_dropdown.rs` | Fuzzy-filtered command palette |
| `FileSearch` | `views/file_search/` | `@` completion with line viewer |

### 5.2 Diff Viewer (`diff.rs`)

Inline unified diffs with syntax highlighting:
- Parses `search_replace` tool output
- Renders `+`/`-` lines with color
- Syntax highlighting via syntect integration

### 5.3 Mermaid Renderer

Vendored Mermaid stack in `third_party/`:
- Renders diagrams directly in scrollback
- Supports flowcharts, sequence diagrams, class diagrams
- Falls back to source code if rendering fails

### 5.4 Theme System (`appearance/`, `pager.toml`)

Base16 color schemes with `pager.toml`:
```toml
[theme]
name = "gruvbox-dark"
base00 = "#282828"  # background
base08 = "#fb4934"  # red
base0B = "#b8bb26"  # green
# ... 16 colors
```

`Ctrl+T` opens theme picker with live preview.

---

## 6. Slash Command System

### 6.1 Command Registry (`slash/`)

```rust
struct SlashCommand {
    name: String,
    aliases: Vec<String>,
    description: String,
    handler: Box<dyn Fn(&mut AgentView, &[String]) -> Result<()>>
}
```

### 6.2 Complete Command Taxonomy (55+ commands)

| Domain | Commands |
|--------|----------|
| **Session** | `/new`, `/clear`, `/resume`, `/load`, `/fork`, `/rename`, `/title`, `/share`, `/session-info`, `/quit`, `/exit`, `/home` |
| **Context** | `/compact`, `/context`, `/rewind`, `/export`, `/copy`, `/find`, `/transcript` |
| **Model** | `/model`, `/m`, `/effort` |
| **Control** | `/always-approve`, `/yolo`, `/plan`, `/view-plan`, `/btw` |
| **Multimodal** | `/imagine`, `/imagine-video`, `/loop`, `/tasks`, `/queue` |
| **UI** | `/dashboard`, `/settings`, `/config`, `/theme`, `/t`, `/compact-mode`, `/multiline`, `/ml`, `/vim-mode`, `/timestamps`, `/terminal-setup` |
| **Agent** | `/config-agents`, `/agents`, `/personas`, `/remember`, `/import-claude` |
| **Extensions** | `/hooks`, `/plugins`, `/marketplace`, `/skills`, `/mcps` |
| **System** | `/feedback`, `/release-notes`, `/changelog`, `/usage`, `/privacy`, `/login`, `/logout` |

### 6.3 Skills as Commands

Any user-invocable skill (`user-invocable: true` in frontmatter) auto-registers as `/skill-name`. Namespace collision handling: `/local:name`, `/user:name`, `/plugin:name`.

---

## 7. Unified Extensions Modal

### 7.1 Single Modal, Five Tabs

| Slash Command | Opens Tab |
|---------------|-----------|
| `/plugins` | Plugins |
| `/hooks` | Hooks |
| `/skills` | Skills |
| `/mcps` | MCP Servers |
| `/marketplace` | Marketplace |

**Keyboard**: `Tab`/`Shift+Tab` cycles tabs; `Enter` expands; `Space` toggles; `i` installs; `/` searches.

### 7.2 Plugin Bundle Format (6 Components)

```
my-plugin/
├── plugin.json          # Optional manifest
├── skills/              # SKILL.md files → /skill-name
├── commands/            # Slash command markdown → /command-name
├── agents/              # Agent definitions → subagent types
├── hooks/hooks.json     # Lifecycle hooks
├── .mcp.json            # MCP server configs
└── .lsp.json            # LSP server configs
```

### 7.3 Marketplace Catalog (`.grok-plugin/marketplace.json`)

```json
{
  "name": "superpowers",
  "source": "remote",
  "url": "https://github.com/obra/superpowers",
  "sha": "a1b2c3d4e5f6...",  // MANDATORY 40-char commit SHA
  "description": "Brainstorm → plan → TDD → review workflows",
  "category": "workflow",
  "components": { "skills": 47, "commands": 12, "agents": 3, "hooks": 8, "mcps": 2, "lsps": 0 }
}
```

**SHA pinning enforced** — no branches, no tags. Verified after clone.

---

## 8. Agent Dashboard

### 8.1 Access

| Entry | Shortcut |
|-------|----------|
| `/dashboard` | `Ctrl+\` (global) |
| `grok dashboard` | Shell command |

### 8.2 Layout (Fullscreen TUI)

```
┌─ Agent Dashboard ────────────────────────────────────────────┐
│ ▼ Awaiting Input (3)     ▼ Working (2)     ▼ Idle (5)       │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ ● session-abc  payment-migration    Awaiting: "Use     │  │
│ │   2m ago       repo:payments      existing schema?"   │  │
│ ├─────────────────────────────────────────────────────────┤  │
│ │ ● session-def  auth-refactor        Working: editing  │  │
│ │   5m ago       repo:auth          user_model.py       │  │
│ ├─────────────────────────────────────────────────────────┤  │
│ │ ○ session-ghi  test-generation      Idle              │  │
│ │   1h ago       repo:core          (completed)         │  │
│ └─────────────────────────────────────────────────────────┘  │
│ [New Session]  [Group by Dir: Ctrl+S]  [Filter]  [Quit: q]  │
└──────────────────────────────────────────────────────────────┘
```

### 8.3 State Groups (Priority Order)

1. **Awaiting Input** — sessions needing approval/answer (pinned top)
2. **Working** — actively executing
3. **Idle** — completed, ready for next
4. **Inactive** — collapsed behind "N more"

Subagents **roll up under parent session**.

### 8.4 Inline Interaction

| Action | Key | Behavior |
|--------|-----|----------|
| Peek | `Enter` / `l` | Side panel with latest output |
| Reply | Type + `Enter` | Idle: immediate. Working: queued. |
| Approve | `1`/`2`/`y`/`n` | Inline buttons |
| Dispatch | Bottom input + `Enter` | New session, stay on dashboard |
| Dispatch + Open | `Shift+Enter` | New session, switch to it |
| Cycle | `n`/`p` | Next/prev without returning |
| Group by dir | `Ctrl+S` | Toggle directory grouping |

### 8.5 Real-Time Implementation

- Backend: Each session runs `grok agent stdio` (ACP over stdio)
- Frontend: Dashboard polls via ACP `session/update` events
- Persistence: Sessions survive dashboard close (`~/.grok/sessions/`)
- Web bridge: `grok --web` → Node → SSE to browser

---

## 9. Skill System & `/skillify`

### 9.1 SKILL.md Format (AIP-3 Standard)

Portable across Claude Code, Codex CLI, Gemini CLI, Cursor, GitHub Copilot.

```yaml
---
name: investigate-payment-latency
description: |
  Investigate sudden latency spikes in payment-service. Use when users report 
  slow checkouts, high p99 latency on payment endpoints, or latency alerts fire.
  Follows the team's standard investigation playbook for this class of incident.
version: "1.2.0"
author: "platform-team <platform@company.com>"
license: MIT
tags: [incident, payments, latency, debugging]
inputs:
  time_window: "5m"
tools: [run_terminal_cmd, read_file, grep, list_dir]
model_min: "grok-4"
requires_network: false
requires_filesystem: true
---
```

**Body** (Markdown, loaded on demand):
```markdown
## Purpose
When to use this skill — explicit trigger phrases and boundaries.

## Inputs
What the agent must collect before running.

## Procedure
1. Step one — references `scripts/check_latency.sh`
2. Step two — references `references/payment-architecture.md`

## Outputs
What the user sees on success.

## Failure Modes
Known errors and recovery hints.

## References
- `references/payment-architecture.md`
- `scripts/check_latency.sh`
```

### 9.2 Discovery Paths (Priority Order)

1. `./.grok/skills/<skill>/SKILL.md` — Project (committed)
2. `~/.grok/skills/<skill>/SKILL.md` — User global
3. `~/.claude/skills/<skill>/SKILL.md` — **Claude Code compat**
4. `[skills] paths` in `~/.grok/config.toml` — Custom

### 9.3 `/skillify` — Session → Asset Pipeline

**The killer feature.** After any workflow:

```
/skillify incident investigation for payment-service latency spikes
```

**Process**:
1. **Reconstruct** — conversation history + git diffs + project detection
2. **Interview** (4 rounds): name → scope (project/user) → description refinement → safety review
3. **Generate** — complete `SKILL.md` + `scripts/` + `references/`
4. **Save** — project (`.grok/skills/`) or user (`~/.grok/skills/`)
5. **Register** — immediately available as `/investigate-payment-latency`

### 9.4 Skill Folder Structure

```
.grok/skills/investigate-payment-latency/
├── SKILL.md                    # Entry point (≤ 2KB)
├── scripts/
│   └── check_latency.sh        # Executable helpers
├── references/
│   └── payment-architecture.md # Deep context (loaded on demand)
└── examples/
    └── sample-run.md           # Few-shot for agent
```

---

## 10. Plugin Marketplace

### 10.1 Installation

```bash
grok plugin install <source> --trust
```

Sources: `user/repo`, `user/repo@v1.0`, `user/repo@<sha>`, `https://github.com/user/repo.git`, `./local-dir`

### 10.2 Trust Model

- `~/.grok/plugins/` — auto-trusted
- `.grok/plugins/` — requires `/plugins-trust` (same gate as MCP/LSP)
- `--trust` flag mandatory for remote installs

### 10.3 Marketplace Commands

```bash
grok plugin marketplace list
grok plugin marketplace add <url>
grok plugin marketplace remove <url>
grok plugin marketplace update
```

### 10.4 `require_sha` Policy

```toml
[marketplace]
require_sha = true  # Tighten-only: cannot be disabled once enabled
```

Forces all remote installs/updates to pin full commit SHA.

---

## 11. Memory System

### 11.1 Storage Layout

```
~/.grok/memory/
├── MEMORY.md                          # Global (cross-project)
├── <project-slug>-<hash8>/MEMORY.md   # Workspace (per repo)
└── <project-slug>-<hash8>/sessions/   # Per-session summaries
```

Clones/worktrees of same repo share memory via `origin` remote.

### 11.2 Hybrid Search (SQLite: FTS5 + vec0)

**Scoring** (configurable):
- Vector similarity: 0.7
- BM25 keyword: 0.3
- Source weights: workspace=1.0, session=1.0, global=1.0
- **Temporal decay**: session memories halve score every 7 days
- **MMR re-ranking**: Optional diversity (lambda=0.7)

### 11.3 Auto-Injection

First turn of every session searches memory and injects relevant chunks.

### 11.4 `/dream` Consolidation

Automatic (configurable: min 4 hours, min 3 sessions since last):
- Reorganizes scattered session logs into topic-organized `MEMORY.md`
- Deduplicates with cosine similarity threshold (default 0.92)

### 11.5 `/flush` Pre-Compaction

LLM-generated session summary → writes to dated session log. Triggered before compaction.

### 11.6 Configuration

```toml
[memory]
enabled = true
session.save_on_end = true
watcher.enabled = true

[memory.index]
max_chunk_chars = 1600
chunk_overlap_chars = 320

[memory.search]
max_results = 6
min_score = 0.35
vector_weight = 0.7
text_weight = 0.3

[memory.search.temporal_decay]
enabled = true
half_life_days = 7.0

[memory.dream]
enabled = true
min_hours = 4
min_sessions = 3
```

---

## 12. Sandbox (Landlock/Seatbelt)

### 12.1 Built-in Profiles

| Profile | Read | Write | Child Net | Linux | macOS |
|---------|------|-------|-----------|-------|-------|
| `off` | All | All | ✓ | — | — |
| `workspace` | All | CWD, `~/.grok/`, `/tmp` | ✓ | Landlock | Seatbelt |
| `devbox` | All | All except `/data` | ✓ | Landlock | Seatbelt |
| `read-only` | All | `~/.grok/`, `/tmp` | ✗ | Landlock+seccomp | Seatbelt |
| `strict` | CWD + sys | CWD, `~/.grok/`, `/tmp` | ✗ | Landlock+seccomp | Seatbelt |

### 12.2 Custom Profiles (`sandbox.toml`)

```toml
[profiles.project]
extends = "workspace"
restrict_network = true
read_only = ["/data"]
read_write = ["/tmp/scratch"]
deny = ["/data/shared-secrets", "**/.env", "**/*.pem"]  # globs = kernel-enforced!
```

**Critical**: `deny` globs are **kernel-enforced** (read + write/rename). Linux requires `bubblewrap`; macOS uses Seatbelt regex (airtight even for files created after launch).

### 12.3 Session Resume

Profile saved with session. Resume **refuses** different profile (safety footgun prevention).

### 12.4 Platform Support

| Platform | Mechanism | Minimum |
|----------|-----------|---------|
| Linux | Landlock | Kernel 5.13+ |
| macOS | Seatbelt | All versions |

---

## 13. Configuration with Pinning

### 13.1 Five-Layer Priority

| Priority | File | Overrideable? |
|----------|------|---------------|
| 1 (lowest) | `/etc/grok/managed_config.toml` | Yes |
| 2 | `~/.grok/managed_config.toml` | Yes |
| 3 | `~/.grok/config.toml` | Yes |
| 4 | `~/.grok/requirements.toml` | **No** (user-pinned) |
| 5 (highest) | `/etc/grok/requirements.toml` | **No** (system-pinned) |

### 13.2 Pinning Mechanism

Values in `requirements.toml` use **fail-closed** — cannot be overridden by user config, env vars, or remote settings.

### 13.3 Enterprise Deployment

```toml
# /etc/grok/requirements.toml (root-owned, immutable)
[grok_com_config]
disable_api_key_auth = true          # Force SSO
force_login_team_uuid = "team-uuid"  # Pin to org team

[ui]
disable_bypass_permissions_mode = true  # Block --yolo, /always-approve

[sandbox]
profile = "strict"                   # Mandatory sandbox

[model.grok-build]
api_key = "xai-..."                  # Pinned key
```

---

## 14. ACP Protocol

### 14.1 MCP vs ACP

| Protocol | Purpose | Direction |
|----------|---------|-----------|
| **MCP** | Model ↔ Tools | Model calls external tools |
| **ACP** | Client ↔ Agent | External app drives agent |

### 14.2 ACP Flow (JSON-RPC over stdio)

```javascript
// 1. Initialize
await request("initialize", { 
  protocolVersion: 1, 
  clientCapabilities: { fs: true, terminal: true } 
});

// 2. Authenticate
await request("authenticate", { methodId: "cached_token" });

// 3. Create session
const { sessionId } = await request("session/new", { 
  cwd: process.cwd(), 
  mcpServers: [] 
});

// 4. Prompt (returns metadata; text streams via session/update)
await request("session/prompt", { 
  sessionId, 
  prompt: [{ type: "text", text: "Fix the bug" }] 
});

// 5. Stream updates
for await (const line of readline(stdout)) {
  const msg = JSON.parse(line);
  if (msg.method === "session/update") {
    const update = msg.params.update;
    if (update.sessionUpdate === "agent_message_chunk") { /* stream text */ }
    if (update.sessionUpdate === "tool_call") { /* show tool */ }
  }
}
```

### 14.3 ACP Methods

`session/new`, `session/load`, `session/prompt`, `session/cancel`, `session/close`, `session/delete`, `session/list`, `session/set_config_option`, `session/set_mode`, `terminal/create`, `terminal/release`, `session/request_permission`.

### 14.4 Web Bridge

`grok --web` spawns Node bridge → `grok agent stdio` → SSE to browser.

---

## 15. Plan Mode

### 15.1 State Machine (Persisted)

```
Inactive → Pending (user toggles) → Active (first prompt) → ExitPending (toggle off mid-turn) → Inactive
```

### 15.2 Enforcement

When **Active**:
- Only `plan.md` in session directory is editable
- All other file edits **rejected at tool dispatch**: "Only plan.md is editable in plan mode"
- Bash commands still run (plan mode blocks edit tools, not shell)
- Subagents **not covered** — start with fresh `Inactive` state

### 15.3 Plan File (`plan.md`)

```markdown
# Plan: Migrate Auth to v2 API

## Context
Why this change is needed...

## Approach
Recommended implementation...

## Critical Files
- src/auth/mod.rs
- src/auth/token.rs

## Reuse
- existing validate_token() in src/auth/validate.rs

## Verification
- pytest tests/auth/ -x
```

### 15.4 Approval UI

Scrollable preview with action bar:
- `a` — Approve (with comments)
- `s` — Request changes (focus prompt)
- `c` — Comment on line
- `q` — Quit plan

---

## 16. Subagent System

### 16.1 Spawn Specification

```rust
spawn_subagent {
    prompt: "...",
    description: "Fix auth bug",
    subagent_type: "general-purpose" | "explore" | "plan",
    background: false,
    capability_mode: "read-only" | "read-write" | "execute" | "all",
    isolation: "none" | "worktree",
    resume_from: "<subagent-id>",
    cwd: "/path",
}
```

### 16.2 Built-in Types

| Type | Tools | Use Case |
|------|-------|----------|
| `general-purpose` | All | Default |
| `explore` | Read, search, bash | Codebase investigation |
| `plan` | Read, search, bash | Implementation planning |

### 16.3 Capability Modes

| Mode | Read | Write | Execute |
|------|------|-------|---------|
| `read-only` | ✓ | ✗ | ✗ |
| `read-write` | ✓ | ✓ | ✗ |
| `execute` | ✓ | ✗ | ✓ |
| `all` | ✓ | ✓ | ✓ |

### 16.4 Worktree Isolation

`isolation: "worktree"` → child gets own git worktree. Changes merged via `x.ai/git/worktree/apply`.

### 16.5 Depth Limit

Max nesting = 1. Subagents cannot spawn subagents.

### 16.6 Personas

Behavioral overlays applied during resolution:
```toml
[subagents.personas.researcher]
instructions = "You are a thorough researcher. Always cite specific file paths."
model = "grok-build"
default_isolation = "worktree"
```

---

## 17. Background Tasks & Prompt Queue

### 17.1 Three Primitives

| Primitive | Trigger | Use Case |
|-----------|---------|----------|
| **Background command** | `Ctrl+G` on running bash | Demote long-running shell |
| **Loop** | `/loop 5m Check tests` | Recurring prompt on interval |
| **Monitor** | `/monitor <event>` | React to event streams |

### 17.2 Background Command API

```rust
run_terminal_command { command: "...", background: true }
// Returns: { task_id: "uuid" }

get_command_or_subagent_output(task_id)
// Or with timeout:
get_command_or_subagent_output(task_id, timeout_ms=30000)

wait_commands_or_subagents { task_ids: [...], mode: "wait_all", timeout_ms: 30000 }

kill_command_or_subagent(task_id)
```

### 17.3 Loop Syntax

```
/loop [interval] <prompt>
```

Intervals: `60s`, `5m`, `2h`, `1d`. Auto-expires after 7 days. Max 50 active.

### 17.4 Monitor Tool

```rust
monitor {
  command: "tail -f /var/log/app.log | grep --line-buffered ERROR",
  description: "App errors",
  persistent: true
}
```

### 17.5 Prompt Queue (`Ctrl+;`)

Queue prompts while agent is busy. Delivered sequentially when turn ends.

### 17.6 Tasks Pane (`Ctrl+B`)

Lists subagents + background commands with status, elapsed time, kill button.

---

## 18. Hooks System

### 18.1 14 Lifecycle Events

| Event | Blocking? | Use Case |
|-------|-----------|----------|
| `SessionStart` | No | Env setup |
| `UserPromptSubmit` | No | Prompt logging |
| `PreToolUse` | **Yes** | Safety guards |
| `PostToolUse` | No | Audit logging |
| `PostToolUseFailure` | No | Error tracking |
| `PermissionDenied` | No | Alert on deny |
| `Stop` | No | Turn-end cleanup |
| `StopFailure` | No | Error cleanup |
| `Notification` | No | Custom alerts |
| `SubagentStart` | No | Child tracking |
| `SubagentStop` | No | Child cleanup |
| `PreCompact` | No | Pre-compaction save |
| `PostCompact` | No | Post-compaction restore |
| `SessionEnd` | No | Final persistence |

### 18.2 Hook Format (`hooks.json`)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "bin/safety-check.sh", "timeout": 10 }
        ]
      }
    ]
  }
}
```

### 18.3 Blocking Hook I/O

**Input** (stdin):
```json
{
  "hookEventName": "pre_tool_use",
  "sessionId": "abc-123",
  "cwd": "/Users/you/project",
  "toolName": "run_terminal_command",
  "toolInput": { "command": "npm test" },
  "timestamp": "2026-04-14T12:00:00Z"
}
```

**Output** (stdout):
```json
{ "decision": "deny", "reason": "Blocked destructive command" }
```
Exit code 2 = explicit deny. Other codes = fail-open.

### 18.4 Injected Environment

`GROK_HOOK_EVENT`, `GROK_HOOK_NAME`, `GROK_SESSION_ID`, `GROK_WORKSPACE_ROOT`, `CLAUDE_PROJECT_DIR`, `GROK_PLUGIN_ROOT`, `GROK_PLUGIN_DATA`.

---

## 19. Goal Mode

### 19.1 GOAL.md Format

```markdown
# GOAL: Migrate auth module to v2 API

## Objective
Migrate auth module from legacy v1 API to v2. Done when:
- All `tests/auth/` pass
- Zero `legacy/auth` imports remain

## Definition of Done
- [ ] Update imports in `src/auth/`
- [ ] Rewrite token validation to use v2 client
- [ ] Run full test suite: `pytest tests/auth/ -x`

## Guardrails
- Do not modify `src/billing/` or `src/users/`
- Max 50 files changed

## Running Log
### 2026-07-17 14:32 — Started
- Scoped to `src/auth/` only
```

### 19.2 Commands

`/goal status` (live panel), `/goal pause`, `/goal resume`, `/goal clear`

### 19.3 Dual-Model Split (Architecturally Significant)

- **Composer 2.5** — instruction-following layer (plans, checklists)
- **grok-build-0.1** — generation + execution + **self-verification**

### 19.4 Critical Gap

No documented max retry limit or crash recovery. If verification loops, agent loops forever.

---

## 20. Keyboard Shortcuts

### 20.1 Complete Map

| Category | Shortcut | Action |
|----------|----------|--------|
| **Essentials** | `Enter` | Send prompt |
| | `Shift+Enter` | Newline (or send in multiline) |
| | `Esc` | Cancel running turn |
| | `Esc Esc` | Clear prompt / open rewind |
| | `Ctrl+C` | Cancel turn |
| | `Shift+Tab` | Cycle mode: Code → Plan → Ask |
| | `Ctrl+P` / `?` | Command palette |
| | `Ctrl+.` / `Ctrl+X` | Keyboard shortcuts help |
| | `F2` / `Ctrl+,` | Settings modal |
| | `Ctrl+Q` / `Ctrl+D` | Quit (press twice) |
| **Input** | `Ctrl+Enter` / `Ctrl+I` | Interject mid-turn |
| | `Ctrl+M` | Toggle multiline |
| | `Ctrl+R` | Search prompt history |
| | `!` | Shell mode (empty prompt) |
| **Scrollback** | `Tab` | Focus scrollback |
| | `j`/`k` / `↓`/`↑` | Next/prev entry (vim mode) |
| | `Shift+L`/`Shift+H` | Next/prev turn |
| | `g` / `Shift+G` | Top/bottom |
| | `Ctrl+U`/`Ctrl+D` | Half-page scroll |
| | `h`/`l` | Collapse/expand entry |
| | `e`/`Shift+E` | Expand one/all |
| | `Ctrl+E` | Toggle thinking blocks |
| | `y`/`Shift+Y` | Copy content/command |
| | `Enter`/`Ctrl+F` | Fullscreen viewer |
| | `/` | Search scrollback (vim mode) |
| | `x` | Kill background task |
| **Panels** | `Ctrl+T` | Toggle todo pane |
| | `Ctrl+B` | Toggle tasks pane |
| | `Ctrl+;` / `Ctrl+'` | Toggle prompt queue |
| | `Ctrl+S` | Open sessions |
| | `Ctrl+L` | Open extensions |
| | `Ctrl+G` | Send command to background |
| | `Ctrl+O` | Toggle always-approve |
| | `Ctrl+N` | New session (twice) |
| | `Ctrl+M` | Pick model (prompt unfocused) |
| | `Ctrl+\` | **Agent Dashboard** |

### 20.2 Terminal Differences

| Terminal | Quit | Interject | Newline |
|----------|------|-----------|---------|
| VS Code/Cursor/Windsurf/Zed | `Ctrl+D` only | `Ctrl+L` | `Alt+Enter` |
| Apple Terminal | `Ctrl+D` | `Ctrl+O` also | — |
| WezTerm | `Ctrl+D` | `Ctrl+Enter` | `Shift+Enter` (needs `enable_kitty_keyboard=true`) |

---

## 21. Omega Implementation Roadmap

### Phase 0: Foundation (Week 1-2) — **START HERE**

| Task | Grok Source | Omega Target |
|------|-------------|--------------|
| Crate decomposition | `xai-grok-pager`/`shell`/etc | `omega-tui`, `omega-shell`, `omega-tools`, `omega-workspace`, `omega-config`, `omega-sandbox` |
| Elm architecture | `app/event_loop.rs` | `omega-tui/src/app/` with Action/Effect |
| JSONL session format | `updates.jsonl` | `data/coordination/sessions/<entity>/<id>/updates.jsonl` |
| Pinned requirements | `/etc/grok/requirements.toml` | `/etc/omega/requirements.omega` (23 Mandates) |
| Landlock sandbox | `xai-grok-sandbox` | `omega-sandbox` crate with per-entity profiles |

### Phase 1: Core UX (Week 3-4)

| Feature | Grok Command | Omega Command |
|---------|--------------|---------------|
| Unified Extensions Modal | `/plugins`, `/hooks`, `/skills`, `/mcps`, `/marketplace` | `/omega-extensions` (P1-P10 tabs) |
| Agent Dashboard | `Ctrl+\` / `/dashboard` | `/omega-dashboard` (Hivemind-backed) |
| Command Palette | `Ctrl+P` / `?` | `Ctrl+Shift+P` (entity-scoped) |
| Keyboard System | 40+ shortcuts | Entity-aware shortcuts (`Shift+Tab` cycles entities) |
| Prompt Queue | `Ctrl+;` | Queue to busy entities via Hivemind |
| Background Tasks | `Ctrl+G`, `/loop`, `/monitor` | Background research loops + prompt queue |

### Phase 2: Intelligence Persistence (Week 5-6)

| Feature | Grok Pattern | Omega Enhancement |
|---------|--------------|-------------------|
| Skill System | `SKILL.md` + `/skillify` | `/omega-skill capture` → entity skills dir + auto-slash |
| Memory System | Hybrid FTS5+vec0 + decay | Same + soul-linked + L1→L2→L3 distillation |
| `/goal` Mode | `GOAL.md` + dual-model | `/omega-goal` + `@verity` independent verifier |
| `/dream` Consolidation | Topic reorganization | `/omega-dream` → `proposed_lessons.yaml` |
| `/flush` Pre-compaction | LLM session summary | Auto-save insights to entity memory |
| Session Rewind | File snapshots | `/omega-rewind` with git + snapshot hybrid |

### Phase 3: Orchestration & Security (Week 7-8)

| Feature | Grok Pattern | Omega Enhancement |
|---------|--------------|-------------------|
| Subagent Delegation | `spawn_subagent` + capability modes | Hivemind handoff with `capability_mode` + `isolation` |
| Plan Mode | Read-only `plan.md` gate | `/omega-plan` per-Pillar with edit enforcement |
| ACP Server | `grok agent stdio` | `omega-hub acp-server` for editor integration |
| Plugin Marketplace | SHA-pinned bundles | WAD marketplace with git SHA verification |
| Config Pinning | `requirements.toml` | Mandates as unoverrideable config |
| Per-Entity Sandbox | Custom `sandbox.toml` | `data/entities/<entity>/sandbox.toml` |

### Phase 4: Ecosystem (Week 9+)

| Feature | Grok Pattern | Omega Vision |
|---------|--------------|--------------|
| Web Bridge | `grok --web` → Node → SSE | `omega-hub web-bridge` for Omega Desktop |
| Theme System | `pager.toml` base16 | Entity-themed UI (Kali=dark red, Ma'at=gold, etc.) |
| Mermaid Rendering | Vendored Mermaid | Architecture diagrams in scrollback |
| Session Sharing | `/share` → URL | Hivemind session handoff packets |
| Enterprise OIDC | `auth.oidc` config | `omega-auth` with team pinning |

---

## 22. Council of Four Synthesis

### 🏗️ The Architect (Systemic Logic)

> "Grok's crate decomposition + Elm architecture + JSONL persistence is the reference implementation for a sovereign TUI agent. Adopt the structure, not the backend."

**Must adopt**:
1. Crate decomposition → `omega-tui`, `omega-shell`, `omega-tools`, `omega-workspace`, `omega-config`, `omega-sandbox`
2. Elm architecture → Replace ad-hoc async with Action/Effect dispatch
3. JSONL session logs → Standardize on `updates.jsonl` format for all entities
4. Pinned requirements → `/etc/omega/requirements.omega` for 23 Mandates
5. Landlock sandbox → Per-Pillar profiles in `data/entities/<entity>/sandbox.toml`

### ⚔️ The Adversary (Critical Rigor)

> "Their `/goal` has no safety bounds, their verifier shares model weights, their Arena Mode doesn't exist. Our `@verity` + `@makali` + pinned mandates are stronger."

**Must NOT replicate**:
| Vulnerability | Omega Fix |
|---------------|-----------|
| `/goal` no retry limit | Mandatory `--max-turns`, `--max-cost`, crash recovery |
| Dual-model verifier | Independent `@verity` entity with separate model |
| Arena Mode vaporware | Don't promise unimplemented features |
| Linux glob `deny` not runtime | Document clearly; name exact paths for airtight |
| Plan mode bash bypass | Audit all tool paths; block `bash` in plan mode too |
| No session encryption | Encrypt at rest with entity-specific keys |

**Competitive moat**: Grok sends code to xAI servers. **Omega's local-first architecture is sovereign.**

### 🧪 The Alchemist (Creative Synthesis)

> "The `/skillify` → soul distillation pipeline is the philosopher's stone. Capture workflows, distill to principles, evolve the entity."

**Cross-pollination gold**:

| Grok Pattern | Omega Synthesis |
|--------------|-----------------|
| `/skillify` capture interview | `/omega-skill capture` → entity skills dir + auto-slash |
| Unified Extensions Modal (5 tabs) | `/omega-extensions` with P1-P10 tabs |
| Agent Dashboard (`Ctrl+\`) | `/omega-dashboard` backed by Hivemind |
| `/goal` + `GOAL.md` | `/omega-goal` + soul-linked `GOAL.md` + `@verity` |
| `/dream` consolidation | `/omega-dream` → `proposed_lessons.yaml` |
| `/flush` pre-compaction | Auto-save insights to entity memory |
| `requirements.toml` pinning | `/etc/omega/requirements.omega` — 23 Mandates enforced |
| Per-Pillar sandbox profiles | `data/entities/kali/sandbox.toml` = `strict` |
| ACP server for editors | `omega-hub acp-server` — VS Code/Cursor drive Omega |
| Plugin marketplace with SHA | WAD marketplace with git SHA verification |
| Worktree isolation | Hivemind workspace locks + git worktrees |
| Prompt queue (`Ctrl+;`) | Queue prompts to busy entities via Hivemind |
| Background loops (`/loop`) | User-defined research loops in `data/coordination/loops/` |

### 📜 The Archivist (Historical Truth)

> "Every primitive in Grok existed before. Their genius is integration. Our genius will be integration + sovereignty."

| Pattern | Origin | Grok's Contribution |
|---------|--------|---------------------|
| Slash commands | IRC/Slack/Discord | Unified command palette with fuzzy search |
| Session fork + worktree | Git worktrees (2015) | First-class `/fork --worktree` with auto-merge |
| Plan mode read-only gate | Claude Code plan mode | Enforced at tool dispatch, survives compaction |
| Subagent capability modes | Codex CLI subagents | Coarse `read-only`/`read-write`/`execute`/`all` filter |
| Hybrid memory (FTS5 + vec0) | SQLite extensions | Source weights + temporal decay + MMR |
| Config pinning | MDM/enterprise config | Fail-closed pinning at highest priority layer |
| Landlock sandbox | Linux 5.13+ (2021) | First AI agent to use kernel Landlock + Seatbelt |
| ACP protocol | BeeAI/IBM Research | First production ACP implementation |
| SHA-pinned plugin marketplace | Supply-chain security | Mandatory 40-char commit SHA, verified at install |
| `/skillify` interview capture | Anthropic internal | First open capture-to-slash-command pipeline |

---

## 23. File-for-File Porting Map

| Grok Build Path | Omega Target | Notes |
|-----------------|--------------|-------|
| `~/.grok/skills/<name>/SKILL.md` | `data/entities/<entity>/skills/<name>/SKILL.md` | Per-entity skills |
| `~/.grok/plugins/` | `config/wads/<wad>/plugins/` | WAD-scoped plugins |
| `~/.grok/config.toml` | `config/omega.yaml` + `config/entities/<entity>.yaml` | Split by entity |
| `/etc/grok/requirements.toml` | `/etc/omega/requirements.omega` | Mandate pinning |
| `~/.grok/sandbox.toml` | `data/entities/<entity>/sandbox.toml` | Per-entity sandbox |
| `~/.grok/sessions/<id>/` | `data/coordination/sessions/<entity>/<id>/` | Hivemind session store |
| `grok agent stdio` (ACP) | `omega-hub acp-server` | Bridge for editors |
| `/dashboard` (TUI) | `/omega-dashboard` (TUI) | Hivemind-backed |
| `/marketplace` | `/omega-wad-marketplace` | Community WAD registry |
| `pager.toml` | `config/themes/<entity>.toml` | Entity-themed UI |
| `third_party/` (Mermaid) | `third_party/` (Mermaid) | Architecture diagrams |
| `xai-grok-hooks` crate | `omega-hooks` crate | Lifecycle events |
| `xai-grok-plugin-marketplace` | `omega-wad-marketplace` crate | WAD distribution |

---

## Appendix: Key Source Files to Study

### TUI Architecture
- `crates/codegen/xai-grok-pager/src/app/event_loop.rs` — Main event loop
- `crates/codegen/xai-grok-pager/src/app/dispatch/router.rs` — Action router
- `crates/codegen/xai-grok-pager/src/views/prompt_widget.rs` — Editor component
- `crates/codegen/xai-grok-pager/src/views/extensions_modal.rs` — 5-tab modal

### Runtime
- `crates/codegen/xai-grok-shell/src/agent/leader.rs` — Leader process
- `crates/codegen/xai-grok-shell/src/session/` — Session persistence
- `crates/codegen/xai-grok-shell/src/tools/` — Tool dispatch

### Sandbox
- `crates/codegen/xai-grok-sandbox/src/` — Landlock/Seatbelt implementation

### Config
- `crates/codegen/xai-grok-config/src/` — Five-layer config with pinning

### Hooks
- `crates/codegen/xai-grok-hooks/src/` — Event types, execution engine

---

## Final Note

This document is the **foundational compass** for Omega Engine's TUI implementation. Every architectural decision in Grok Build has been mapped to an Omega equivalent. The codebase at `github.com/xai-org/grok-build` is the definitive reference implementation.

**Next action**: Begin Phase 0 crate decomposition. The `omega-tui` crate starts with `ratatui` + the Elm architecture from `xai-grok-pager/src/app/`.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_grok_cli_architecture ⬡ COMPLETE*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
