# 🔱 GROK CLI CODEBASE DIGGING MAP — Sovereign Researcher Field Notes

**AP Token**: `AP-GROK-DIG-MAP-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ tencent/hy3:free ⬡ opencode ⬡ trc_grok_dig ⬡ CODE-MAP
**Date**: 2026-07-17
**Repository**: `github.com/xai-org/grok-build` (cloned to `third_party/grok-build/`)
**Purpose**: Prevent future agents from re-digging. This is a **map**, not a full read. Use it to navigate directly to the file you need.

---

## §0 TL;DR — What Grok CLI Is

Grok CLI (a.k.a. "grok-build") is xAI's open-source terminal agent. It is the **reference implementation** for the Omega Engine TUI redesign. It is a Rust workspace with **85+ crates** under `crates/codegen/`. The architecture is Elm-inspired (pure update loop), kernel-sandboxed (Landlock/Seatbelt), and uses JSONL session persistence.

**The 9 core domains** (Omega equivalent → Grok crate → path):

| Omega Target | Grok Crate | Path |
|-------------|-----------|------|
| `omega-tui` | `xai-grok-pager` + `xai-grok-pager-render` | `crates/codegen/xai-grok-pager/` |
| `omega-shell` | `xai-grok-shell` + `xai-grok-shell-base` | `crates/codegen/xai-grok-shell/` |
| `omega-tools` | `xai-grok-tools` + `xai-grok-tools-api` | `crates/codegen/xai-grok-tools/` |
| `omega-workspace` | `xai-grok-workspace` + `-client` + `-types` | `crates/codegen/xai-grok-workspace/` |
| `omega-config` | `xai-grok-config` + `-types` | `crates/codegen/xai-grok-config/` |
| `omega-sandbox` | `xai-grok-sandbox` | `crates/codegen/xai-grok-sandbox/` |
| `omega-hooks` | `xai-grok-hooks` + `xai-grok-plugin-marketplace` | `crates/codegen/xai-grok-hooks/` |
| `omega-acp` | `xai-acp-lib` | `crates/codegen/xai-acp-lib/` |
| `omega-memory` | `xai-grok-memory` + `xai-sqlite-journal` | `crates/codegen/xai-grok-memory/` |

---

## §1 Repository Layout (Top-Level)

```
third_party/grok-build/
├── Cargo.toml              # Workspace manifest (85+ members)
├── Cargo.lock              # 338KB lockfile (pinned deps)
├── crates/
│   ├── build/              # Build tooling
│   ├── common/             # Shared utilities
│   └── codegen/            # ← ALL application crates live here
│       ├── xai-grok-pager/        # TUI (Ratui)
│       ├── xai-grok-shell/        # Runtime/agent lifecycle
│       ├── xai-grok-tools/        # File ops, code edit, skills
│       ├── xai-grok-workspace/    # FS, VCS, execution
│       ├── xai-grok-config/       # Config system
│       ├── xai-grok-sandbox/      # Landlock/Seatbelt
│       ├── xai-grok-hooks/        # Hooks + plugins
│       ├── xai-grok-plugin-marketplace/
│       ├── xai-acp-lib/           # Agent Client Protocol
│       ├── xai-grok-memory/       # Memory + sqlite-vec
│       ├── xai-sqlite-journal/    # WAL journaling
│       ├── xai-grok-pager-render/ # Render helpers
│       └── ... (70+ more)
└── prod/                   # Production build config
```

**Note**: There is NO `src/` at top level. Everything is in `crates/codegen/`.

---

## §2 The Elm Architecture — Where It Lives

Grok's TUI uses a pure Elm-inspired update loop. The core files:

| Concept | File | What's Inside |
|---------|------|--------------|
| **Action** (user intent) | `xai-grok-pager/src/app/actions.rs` (117KB) | `Action` enum (all user gestures), `Effect` enum (all async side-effects), `TaskResult` enum (effect completions) |
| **Dispatch** (pure state update) | `xai-grok-pager/src/app/dispatch/` | Pure `fn(state, action) -> (state, Vec<Effect>)`. NO I/O. Subdirs: `dashboard.rs`, `dashboard_telemetry.rs`, etc. |
| **Event Loop** (effect exec) | `xai-grok-pager/src/app/event_loop.rs` (191KB) | Spawns effects into `JoinSet`, feeds `TaskResult` back to dispatch |
| **App State** | `xai-grok-pager/src/app/app_view.rs` (475KB) | `AppView` struct — the single source of truth. `handle_input()` entry point |
| **Agent State** | `xai-grok-pager/src/app/agent.rs` (62KB) + `agent_view/` | Per-session state, input handling |

**Key insight**: `app_view.rs:handle_input()` (line 2056) is the top-level input router. It delegates to `agent.handle_input()` for agent-scoped keys. The `dispatch/` directory contains the pure reducers.

---

## §3 Configuration Pinning — Mandate Enforcement Pattern

**File**: `xai-grok-config/src/lib.rs` (lines 1-50)

**Merge order (lowest → highest priority)**:
1. `/etc/grok/managed_config.toml`
2. `$GROK_HOME/managed_config.toml`
3. `$GROK_HOME/config.toml`
4. `$GROK_HOME/requirements.toml` (cloud cache, Ed25519-signed)
5. `/etc/grok/requirements.toml` ← **SYSTEM-WIDE, HIGHEST PRIORITY**
6. macOS MDM managed preferences (macOS only)

**Omega mapping**: `/etc/omega/requirements.omega` at priority 5 pins all 23 Sovereign Mandates with fail-closed startup.

**Key functions** (from `lib.rs` re-exports):
- `load_from_disk()` — loads all layers
- `validate_requirements()` — fail-closed validation
- `deep_merge_toml()` — layer merge
- `apply_version_overrides_with_registered()` — version-gated config

---

## §4 Kernel Sandboxing — Security Model

**File**: `xai-grok-sandbox/src/lib.rs` (29KB)

**Pattern**: Landlock (Linux 5.13+) / Seatbelt (macOS) via the `nono` crate. Applied once at process startup, irreversible.

**Omega mapping**: `omega-sandbox` crate with per-entity `sandbox.toml`:
- **Kali** (P1-P5): `deny = ["/*"]`, `allow = [".../config/wads/"]`
- **P7** (Context): read-only workspace
- **P3** (Engineering): workspace + custom deny lists

**Note**: The sandbox effect type is defined in `xai-grok-pager/src/app/actions.rs` (search for `Sandbox` in the `Effect` enum).

---

## §5 JSONL Session Persistence — Crash Resilience

**Files**:
- `xai-sqlite-journal/src/lib.rs` (32KB) — WAL-mode SQLite journaling, append-only event log
- `xai-grok-memory/src/lib.rs` (3.6KB) — Memory system, uses sqlite-vec for vector search

**Pattern**:
- `updates.jsonl` — append-only ACP event stream (source of truth)
- `rewind_points.jsonl` — periodic filesystem snapshots
- `/rewind` command replays journal to restore state

**Omega mapping**: `data/coordination/sessions/<entity>/<id>/` with same structure. `/omega-rewind` implementation.

---

## §6 Views Directory — All UX Patterns

**Location**: `xai-grok-pager/src/views/` (274KB total across 80+ files)

| Pattern | File | Notes |
|---------|------|-------|
| **Agent Dashboard** | `views/dashboard/` (state.rs 458KB, render.rs 337KB, row.rs 78KB, layout.rs 39KB, peek.rs 97KB) | `Ctrl+\` fullscreen. Sessions grouped by state. Inline reply. |
| **Extensions Modal** | `views/extensions_modal.rs` (274KB) | `Ctrl+Shift+O`. Tabs: Hooks/Plugins/Marketplace/Skills/MCP Servers. Comment at top: "Extensions modal popup (Hooks, Plugins, Marketplace, Skills, MCP Servers)." |
| **Command Palette** | `views/modal.rs` + `agent_view/input.rs` | **Opened by `Ctrl+P`** (not Ctrl+Shift+P). Sets `active_modal = ActiveModal::CommandPalette`. Entries from `default_palette_entries()`. |
| **Permissions** | `views/permission_view.rs` (118KB) | Permission mode UI |
| **Plan Mode** | `views/plan_approval_view.rs` | Read-only gate UI |
| **Rewind** | `views/rewind.rs` (50KB) | Rewind picker |
| **Skills** | `xai-grok-tools/src/implementations/skills/` | Skill types (`SkillInfo`), `/skillify` capture |
| **Memory Modal** | `views/memory_modal.rs` (51KB) | Memory browser |

**Key correction from digging**: The command palette is `Ctrl+P`, NOT `Ctrl+Shift+P` as initially hypothesized. Verified in `agent_view/input.rs` line ~466: `key!('p', CONTROL).matches(key)` opens it (when not in prompt pane).

---

## §7 Agent Dashboard — Deep Dive

**Location**: `xai-grok-pager/src/views/dashboard/`

| File | Size | Contents |
|------|------|----------|
| `state.rs` | 458KB | Dashboard state machine, session roster, filtering |
| `render.rs` | 337KB | Ratui rendering of dashboard |
| `row.rs` | 78KB | Individual session row widget |
| `peek.rs` | 97KB | Inline peek/reply panel |
| `peek_tail.rs` | 16KB | Peek tail rendering |
| `layout.rs` | 39KB | Dashboard layout computation |
| `mod.rs` | 6KB | Module exports |

**Dispatch logic**: `xai-grok-pager/src/app/dispatch/dashboard.rs` (99KB) — pure reducers for dashboard actions.

**Trigger**: `ActionId::OpenDashboard` → `Action::OpenDashboard`. Handled in `app_view.rs:handle_global_action()`.

---

## §8 Extensions Modal — Unified Interface

**File**: `xai-grok-pager/src/views/extensions_modal.rs` (274KB)

**Tabs** (from `ExtensionsTab` enum):
1. `Hooks` — file-based automation
2. `Plugins` — Rust/Wasm extensions
3. `Marketplace` — shared extensions
4. `Skills` — natural language → slash commands
5. `MCPs` — Model Context Protocol servers

**Omega mapping**: `/omega-extensions` with P1-P10 tabs (one per Pillar).

**Opened by**: `/hooks` and `/plugins` slash commands (per file comment).

---

## §9 Skill System — Knowledge Capture

**Location**: `xai-grok-tools/src/implementations/skills/`

**Pattern**: `/skillify` command:
1. 4-round interview about completed workflow
2. Analyzes git diffs for context
3. Generates production `SKILL.md` (AIP-3 format)
4. Auto-registers as slash command in `~/.grok/config.toml`

**Omega mapping**: `/omega-skill capture` → entity skills dir → auto-slash registration.

---

## §10 ACP Protocol — Agent Orchestration

**File**: `xai-acp-lib/src/lib.rs`

**Pattern**: JSON-RPC over stdio. Message types:
- `session/new`, `session/load`, `session/prompt`
- `mcp/list`, `tools/list`, `resources/read`
- Lifecycle: initialize → session operations → shutdown

**Omega mapping**: `omega-hub acp-server` for VS Code/Cursor/Neovim integration.

---

## §11 How to Navigate This Repo (For Future Agents)

1. **Start with `actions.rs`** — read the `Action`, `Effect`, `TaskResult` enums. This is the vocabulary of the entire UI.
2. **Read `app_view.rs:handle_input()`** — trace how a key press becomes an `Action`.
3. **Look in `dispatch/`** — pure functions that transform state.
4. **Find the view you care about in `src/views/`** — dashboard, extensions_modal, etc.
5. **Cross-reference with `xai-grok-shell/`** — the runtime that actually executes agent turns.

**Grep targets**:
- Elm loop: `grep -rn "enum Action" crates/codegen/xai-grok-pager/src/app/actions.rs`
- Config priority: `grep -n "priority" crates/codegen/xai-grok-config/src/lib.rs`
- Sandbox: `grep -rn "Landlock\|Seatbelt" crates/codegen/xai-grok-sandbox/src/lib.rs`
- Command palette: `grep -rn "CommandPalette" crates/codegen/xai-grok-pager/src/app/agent_view/input.rs`

---

## §12 Open Questions / Gaps for Future Digging

| Gap | Why It Matters | Where to Look |
|-----|----------------|---------------|
| **How does `dispatch/` call into `xai-grok-shell`?** | The boundary between UI state and agent execution is unclear. | `xai-grok-pager/src/app/acp_handler/` + `xai-grok-shell/src/` |
| **What is the exact `Effect` → ACP call mapping?** | Need to port effects to Omega's provider fabric. | `xai-grok-pager/src/app/actions.rs` `Effect` enum + `xai-grok-shell/src/` |
| **How does the sandbox profile get loaded at startup?** | Need to replicate per-entity sandbox loading. | `xai-grok-sandbox/src/lib.rs` + `xai-grok-pager/src/app/actions.rs` (sandbox effect) |
| **What is `default_palette_entries()`?** | Need to know what commands populate the palette. | `xai-grok-pager/src/views/modal.rs` |
| **How does `/skillify` analyze git diffs?** | Need to port the capture pipeline. | `xai-grok-tools/src/implementations/skills/` |
| **What is the ACP session lifecycle state machine?** | Need to model agent sessions in Omega. | `xai-acp-lib/src/lib.rs` + `xai-grok-shell/src/` |

---

## §13 Quick Reference — File Paths

```
# Elm core
crates/codegen/xai-grok-pager/src/app/actions.rs
crates/codegen/xai-grok-pager/src/app/dispatch/
crates/codegen/xai-grok-pager/src/app/event_loop.rs
crates/codegen/xai-grok-pager/src/app/app_view.rs

# Config
crates/codegen/xai-grok-config/src/lib.rs

# Sandbox
crates/codegen/xai-grok-sandbox/src/lib.rs

# Persistence
crates/codegen/xai-sqlite-journal/src/lib.rs
crates/codegen/xai-grok-memory/src/lib.rs

# Views
crates/codegen/xai-grok-pager/src/views/dashboard/
crates/codegen/xai-grok-pager/src/views/extensions_modal.rs
crates/codegen/xai-grok-pager/src/views/modal.rs
crates/codegen/xai-grok-pager/src/app/agent_view/input.rs

# Skills
crates/codegen/xai-grok-tools/src/implementations/skills/

# ACP
crates/codegen/xai-acp-lib/src/lib.rs
```

---

## §14 Related Documents

- `QUICK_WINS_FROM_GROK.md` — 7 high-impact, low-effort implementations for Omega
- `third_party/grok-build/GROK_ARCHITECTURE_STUDY_GUIDE.md` — Initial study guide
- `docs/research/R_GROK_CLI_ARCHITECTURE.md` — Full 1,279-line implementation compass
- `data/entities/researcher/session_gnosis.md` — Researcher's distilled findings (L1/L2/L3)
- `data/entities/researcher/proposed_lessons.yaml` — L3 principles 16-46

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ GROK_CLI_DIG ⬡ CODE-MAP ⬡ 2026-07-17*

**This map is the entry point. Future agents: read this first, then go direct to the file. Do NOT re-dig the entire repo.**

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: tencent/hy3:free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
