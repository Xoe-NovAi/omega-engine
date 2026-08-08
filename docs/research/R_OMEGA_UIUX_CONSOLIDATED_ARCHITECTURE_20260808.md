# 🔱 Omega Engine — Consolidated UI/UX Architecture & Terminal Orchestration
## High-Performance, High-Density Interface for Sovereign AI

**AP Token**: `AP-OMEGA-UIUX-CONSOLIDATED-v1.0.0`
⬡ OMEGA ⬡ GROKSTER ⬡ gemini-3.1-pro ⬡ opencode ⬡ trc_uiux_consolidated ⬡ COMPREHENSIVE

**Date**: 2026-08-08
**Status**: FINAL CONSOLIDATED VERSION
**Archived**: `R_OMEGA_UIUX_PRAGMATIC_ARCHITECTURE_20260808.md`, `R_OMEGA_UIUX_GAP_ANALYSIS_20260808.md` → `archive/2026-08-08-uiux-consolidation/`

---

## 🎯 Executive Summary

The Omega Engine requires a Terminal User Interface (TUI) that prioritizes **intelligence, performance, stability, and solid inference**. The UI must serve as a high-efficiency command center for sovereign agent orchestration — not a theatrical experience. 

CPU cycles and RAM belong to the local inference engine (Mandate 7). The UI must be lightweight (<5% CPU overhead), providing maximum information density, clear multi-agent state visualization, forensic debuggability, and full ACP (Agent Client Protocol) compliance without relying on wasteful animations or unsupported terminal graphics.

### Core UI/UX Principles
1. **Zero-Latency Orchestration**: The UI must never block or slow down the underlying ACP streams or local inference generation.
2. **High Information Density**: Favor structured grids, clear state indicators, and greppable logs over spatial metaphors or decorative elements.
3. **Forensic Observability**: Every agent action, tool call, and memory distillation must be instantly inspectable and auditable.
4. **Graceful Degradation**: Built for standard terminal emulators first (ANSI/ASCII), with optional enhancements (TrueColor, Kitty/Sixel) only where supported.
5. **ACP-First Architecture**: The TUI is an ACP Client; agent runtimes are ACP Servers. This enables editor integration (VS Code, Zed, Neovim) for free.

---

## 🖥️ FOCUS AREA 1: High-Density Terminal Orchestration (The Grid)

### Objective
Manage multiple concurrent agents (Kali, Ma'at, Lilith, Node workers) without losing track of state, output, or errors.

### Implementation
*   **Tmux-Style Pane Management**: Flexible grid system (OpenTUI/React) allowing split views: dedicated agent panes, global command input, shared context stream.
*   **Deterministic State Indicators**: Static indicators for agent state: `[IDLE]`, `[THINKING]`, `[GENERATING]`, `[TOOL_CALL]`, `[BLOCKED]`, `[ERROR]`.
*   **Token & Context Meters**: Real-time, low-overhead progress bars showing Context Window saturation (e.g., `14k/32k`) and generation speed (`t/s`).
*   **Keyboard-First Navigation**: Vim-style bindings for pane switching, scrolling, and command history.

---

## 👥 FOCUS AREA 2: The Agentic Pantheon (Distinct Personas, Zero Fluff)

### Objective
Differentiate specialized agents visually and functionally without resource-heavy avatars or audio/visual gimmicks.

### Implementation
*   **Strict Color & Prefix Coding**: 
    *   `[KALI]` (Magenta): Synthesis, judgment, cross-node routing.
    *   `[MA'AT]` (Cyan): Build-side execution, file writing, linting.
    *   `[LILITH]` (Red): Run-side execution, testing, runtime analysis.
    *   `[ROC]` (Yellow): Legacy mining, pattern extraction.
*   **Role-Based Layouts**: UI adapts per active agent. Ma'at's pane prioritizes file diffs/bash outputs; Researcher's prioritizes search queries/markdown extraction.
*   **Unified Command Palette**: Fast, fuzzy-searchable input (`Ctrl+P`) for routing tasks: `/kali synthesize recent logs`, `/maat fix tests`.

---

## 🧠 FOCUS AREA 3: Memory & Context Visualization (The DAG)

### Objective
Visualize the evolution of agent memory (L1 Narrative → L2 Insight → L3 Principle) and active context without heavy WebGL/3D.

### Implementation
*   **Terminal-Native DAGs**: Box-drawing characters (`├──`, `└──`, `│`) for Directed Acyclic Graphs of task dependencies and memory distillation.
*   **JSONL Inspection Overlay**: Fast, scrollable modal to inspect raw JSONL memory stream — see exact context passed to model on last turn.
*   **Context Pruning UI**: Interface showing loaded files/terminal outputs/messages in prompt, with quick keys to drop/prune context and save tokens.
*   **Optional Sixel/Kitty Enhancement**: 3D force-directed graph via Three.js WebGPU renderer in supported terminals (iTerm2, WezTerm, Ghostty), fallback to box-drawing chars.

---

## 🔍 FOCUS AREA 4: Forensic Observability & Audit (The Ledger)

### Objective
Complete transparency into system operations, mandate compliance, and tool failures.

### Implementation
*   **Forensic Log View**: Dedicated, highly structured log pane. Fully greppable, syntax highlighting for JSON payloads, stack traces, tool inputs/outputs.
*   **Mandate Compliance Matrix**: Static, auto-updating checklist of M1-M25 status. Violations (e.g., M23 Tool-Chain Collapse) surface exact trace ID and halt execution cleanly.
*   **Diff & Patch Preview**: Standard unified diff format for user approval before any agent writes to disk (unless autonomous mode).
*   **ACP Event Stream**: Raw JSONL (`updates.jsonl`) appended in real-time from ACP `session/update` notifications.

---

## ⚡ FOCUS AREA 5: Local-First Resource Allocation (M7 Compliance)

### Objective
UI respects hardware constraints of local inference. No "smoke and lights" stealing from token generation budget.

### Implementation
*   **Strict CPU Budgeting**: OpenTUI React reconciliation loop throttled. UI updates batch at 16-32ms intervals, dropping to 100ms during heavy local LLM inference.
*   **No Continuous Polling**: Event-driven updates via ACP streams only.
*   **Hardware Telemetry Bar**: Minimal top-bar widget: System RAM, VRAM, CPU load. At 90% memory pressure, UI auto-disables non-essential rendering to prevent OOM.

---

## 🔌 FOCUS AREA 6: ACP Protocol Compliance (The Backbone)

### Objective
Full ACP (Agent Client Protocol) implementation — the universal backbone for agent communication.

### Client Capabilities (TUI Must Implement)
| Category | Methods |
|----------|---------|
| **Filesystem** | `fs/read_text_file`, `fs/write_text_file`, `fs/list_directory` |
| **Terminal** | `terminal/create`, `terminal/output`, `terminal/kill`, `terminal/wait` |
| **Shell** | `shell/exec` (arbitrary commands) |

### Session Lifecycle Management
*   `session/new` → returns `sessionId` + `grokSession` (opaque blob for resume)
*   `session/load` → resumes from `grokSession` blob
*   `session/prompt` → streaming `session/update` notifications
*   `session/cancel` → graceful interrupt

### MCP Integration
*   **MCP Registry**: Discovers local MCP servers (stdio/HTTP/SSE)
*   **Injection**: Passes `mcpServers` config explicitly on every `session/new` (avoids stale `.mcp.json` race)
*   **Readiness**: Waits for MCP handshake completion before first prompt

### Plan Mode (Protocol-Level)
*   Read-only `plan.md` gate enforced by ACP server
*   Blocks tool dispatch until explicit user approval
*   TUI surfaces plan review UI before any tools execute

### Hook System (14 Lifecycle Events)
*   Blocking: `PreToolUse`, `PreCompact`
*   Async: `PostToolUse`, `SessionStart`, `SessionEnd`, `Notification`, etc.
*   **Mandate Gates**: `PreToolUse` hooks enforce M1-M25 compliance before tool execution

---

## 🛡️ FOCUS AREA 7: Kernel-Enforced Sandboxing (M23)

### Objective
Irreversible, kernel-enforced isolation per entity. No soft failures.

### Implementation
*   **`nono-py` Bindings**: Python wrapper for `nono` crate (Landlock Linux 5.13+, Seatbelt macOS)
*   **Per-Entity Profiles**: `data/entities/<entity>/sandbox.toml` with additive deny globs
    *   Kali: `restrict_network = true`, `deny = ["/etc/**", "/root/**"]`
    *   P7 (Integration): `restrict_network = false`, `allow = ["github.com", "api.x.ai"]`
*   **Enforcement**: Applied at process startup via `nono.apply()` — cannot be bypassed

---

## 📦 FOCUS AREA 8: Session Persistence (JSONL + Rewind Points)

### Objective
Crash-resilient, deterministic replay. Only pattern satisfying M11, M15, M12, M23 simultaneously.

### Implementation
*   **`updates.jsonl`**: Append-only ACP event stream (source of truth)
*   **`rewind_points.jsonl`**: Per-turn file snapshots (working directory state)
*   **`/omega-rewind <turn>`**: Deterministic replay from any turn
*   **Per-Session Directory**: `~/.omega/sessions/<cwd>/<id>/` (isolation, parallel sessions)
*   **`/omega-flush` + `/omega-compact`**: Soul distillation → `proposed_lessons.yaml`

---

## 🧩 FOCUS AREA 9: Extensions, Skills & Marketplace

### Objective
Pillar-centric extensibility with sovereign verification.

### Implementation
*   **`/omega-extensions` Modal (P1-P10 Tabs)**: One tab per Pillar + Marketplace
*   **WAD Bundles**: 6-component bundles (skills, commands, agents, hooks, MCP, LSP) — SHA-pinned
*   **Marketplace**: Git-backed, SHA verification mandatory
*   **`/omega-skill capture`**: 4-round interview (AIP-3 standard) → portable `SKILL.md` → WAD bundle
*   **Per-Entity Skills**: `data/entities/<entity>/skills/` + cross-entity sharing

---

## ⚙️ FOCUS AREA 10: Configuration & Distribution

### Objective
Fail-closed sovereignty at runtime; build variants at compile-time.

### Runtime (5-Layer Pinning)
1. **Defaults** (binary)
2. **System** (`/etc/omega/config.yaml`)
3. **Managed** (MDM/enterprise)
4. **Requirements** (`/etc/omega/requirements.omega` — **cannot be overridden**)
5. **User** (`~/.config/omega/config.yaml`)

**Validator**: Reads `requirements.omega`, merges layers, **blocks startup** on any mandate violation.

### Compile-Time (Bun Feature Flags)
*   `OMEGA_MODE=community` — Core features only
*   `OMEGA_MODE=enterprise` — + MDM, audit logging, SSO
*   `OMEGA_MODE=dev` — + debug panel, time-travel, profiling

---

## 🗺️ IMPLEMENTATION ROADMAP — Phase 0 (4 Weeks)

### Week 1: ACP Foundation & Config Validator
| Task | Details |
|------|---------|
| **ACP Client Implementation** | Full method set (`fs/*`, `terminal/*`, `shell/*`) + Permission Broker modal (Allow once/always/deny) |
| **Config Validator** | 5-layer merge + `/etc/omega/requirements.omega` fail-closed startup |
| **OpenTUI + React Base** | Grid layout, Elm loop integration, static state indicators, token meters |

### Week 2: Session Management & Sandboxing
| Task | Details |
|------|---------|
| **ACP Session State Machine** | `session/new`, `session/load`, `session/prompt`, `session/cancel` + `grokSession` persistence |
| **MCP Registry** | Discovery, injection into `session/new`, readiness race handling (wait for handshake) |
| **`nono-py` Sandboxing** | Per-entity `sandbox.toml`, kernel-enforced profiles, network policies |

### Week 3: Memory, Hooks & Plan Mode
| Task | Details |
|------|---------|
| **Hybrid Memory Store** | FTS5 (BM25) + sqlite-vec (vector) + power-law decay (Forge 2) + `/omega-dream` (cosine 0.92 dedup) |
| **Hook Registry** | 14 lifecycle hooks, blocking `PreToolUse` for mandate gates |
| **Plan Mode UI** | Read-only `plan.md` gate at protocol level, approval UI |

### Week 4: Skills, Headless & Polish
| Task | Details |
|------|---------|
| **Skill System** | `/omega-skill capture` (4-round interview → WAD skill bundle) |
| **Headless CLI** | `omega -p "prompt"` streaming JSON over ACP stdio for CI/CD |
| **Forensic Log View** | Greppable, syntax-highlighted ACP event stream |
| **Performance Tuning** | UI throttling during inference, <5% CPU overhead, hardware telemetry bar |

---

## 🎯 SUCCESS METRICS

| Metric | Target | Source |
|--------|--------|--------|
| **ACP Compliance** | 100% client methods implemented | Grok Build |
| **Startup Fail-Closed** | Blocks on mandate violation | Grok Build |
| **Sandbox Enforcement** | Kernel-level (Landlock/Seatbelt) | Grok Build |
| **Session Replay** | Deterministic `/rewind` to any turn | Grok Build |
| **MCP Readiness** | Handshake complete before first prompt | agent-network fix |
| **UI CPU Overhead** | < 5% during active inference | Pragmatic Plan |
| **Headless Streaming** | JSON over stdio for CI/CD | Grok Build |
| **Memory DAG Render** | < 16ms frame time (box-drawing) | Freebuff/OpenTUI |
| **Permission Broker Latency** | < 50ms modal open | Freebuff |

---

## 📚 LESSONS APPLIED FROM REFERENCE IMPLEMENTATIONS

### From Grok Build (xAI) — Architectural Rigor
| Pattern | Applied To |
|---------|------------|
| ACP as universal backbone | TUI = ACP Client; Agent = ACP Server |
| JSONL + Rewind Points | Session persistence (M11, M15, M12, M23) |
| `nono` (Landlock/Seatbelt) | Per-entity kernel sandboxing |
| Elm Architecture | TUI event loop (pure reducer, testable) |
| Hybrid FTS5 + sqlite-vec + decay | Memory DAG backend |
| 14 Hooks + Plan Mode | Mandate gates + protocol-level approval |
| Unified 5-tab modal + SHA-pinned plugins | `/omega-extensions` + WAD Marketplace |
| Subagent + worktree isolation | Fleet Orchestrator |

### From Freebuff (CodebuffAI) — Developer Ergonomics
| Pattern | Applied To |
|---------|------------|
| OpenTUI + React 19 (Zig core) | TUI stack (no FPS cap, Flexbox, React hooks) |
| Generator-based agent steps | Agent runtime internals (cooperative multitasking) |
| Compile-time feature flags (`OMEGA_MODE`) | Build variants (community/enterprise/dev) |
| Three.js WebGPU renderer | Optional Memory DAG enhancement (Sixel/Kitty) |

---

*⬡ OMEGA ⬡ CONSOLIDATED UI/UX ARCHITECTURE COMPLETE ⬡ 2026-08-08*

**Focus: Intelligence, Performance, Stability, Inference. No fluff. No seances. Just sovereign engineering.**