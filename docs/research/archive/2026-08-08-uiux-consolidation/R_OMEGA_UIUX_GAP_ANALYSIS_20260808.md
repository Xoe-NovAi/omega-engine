<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine UI — Gap Analysis & Lessons from Grok Build / Freebuff
## Pragmatic Engineering Review

**AP Token**: `AP-OMEGA-UIUX-GAP-ANALYSIS-v1.0.0`
⬡ OMEGA ⬡ GROKSTER ⬡ gemini-3.1-pro ⬡ opencode ⬡ trc_gap_analysis ⬡ COMPREHENSIVE

**Date**: 2026-08-08
**Sources**: 
- Grok Build (xai-org/grok-build) — Rust/ACP/ratatui/JSONL/nono
- Freebuff (CodebuffAI) — TypeScript/OpenTUI/React/Elm/Generator agents
- Our Pragmatic Architecture: `R_OMEGA_UIUX_PRAGMATIC_ARCHITECTURE_20260808.md`

---

## ⚠️ CRITICAL GAPS IN OUR CURRENT PLAN

### Gap 1: ACP Client Capability Implementation (HIGH)
**Our Plan**: "Implement the ACP multiplexer to handle stdio streams from local agents"
**Reality**: ACP requires **specific client capabilities** that the agent (server) calls:
- `fs/read_text_file`, `fs/write_text_file`, `fs/list_directory`
- `terminal/create`, `terminal/output`, `terminal/kill`, `terminal/wait`
- `shell/exec` (for arbitrary commands)

**Missing**: We have no spec for the **Permission Broker** that mediates these calls. Grok Build implements a full permission modal with "Allow once / Allow always / Deny" per tool call. We need this before any agent can actually use tools.

### Gap 2: Session Management via ACP (HIGH)
**Our Plan**: "JSONL + Rewind Points for persistence"
**Reality**: ACP session lifecycle is explicit:
- `session/new` → returns `sessionId` + `grokSession` (opaque blob)
- `session/load` → resumes from `grokSession`
- `session/prompt` → streaming `session/update` notifications
- `session/cancel` → graceful interrupt

**Missing**: Our TUI must manage the **ACP session state machine** — creating sessions, persisting `grokSession` blobs, handling reconnection, and mapping our internal "rewind points" to ACP's `session/load`.

### Gap 3: MCP Server Integration via ACP (HIGH)
**Our Plan**: No mention of MCP
**Reality**: Grok Build's ACP `init` response includes `mcpCapabilities = {http: true, sse: true}`. The agent **discovers MCP servers** via ACP `session/new` (which accepts `mcpServers` config) or via `.mcp.json` in cwd. The agent-network runtime fixed a critical bug by passing `mcpServers` explicitly on every `session/new` to avoid stale `.mcp.json` discovery.

**Missing**: We need an **MCP Registry** in our TUI that:
- Discovers local MCP servers (stdio/HTTP/SSE)
- Injects them into `session/new` calls
- Handles the "MCP readiness race" (wait for handshake before first prompt)

### Gap 4: Plan Mode Enforcement (MEDIUM)
**Our Plan**: "Diff & Patch Preview" for approvals
**Reality**: Grok Build implements **Plan Mode at the protocol level** — a read-only `plan.md` gate that blocks tool dispatch until the user explicitly approves. This is enforced by the ACP server, not the client.

**Missing**: We need to implement the **ACP `plan` capability** and a plan-review UI that shows the proposed plan before any tools execute.

### Gap 5: Hook System (MEDIUM)
**Our Plan**: No mention
**Reality**: Grok Build has **14 lifecycle hooks** (blocking `PreToolUse`, `PostToolUse`, `PreCompact`, `SessionStart`, etc.). These are critical for safety gates, audit trails, and our Mandate Compliance Matrix.

**Missing**: We need a **Hook Registry** that allows entities to register blocking/async hooks, and the TUI must surface hook execution status.

### Gap 6: Skill System & `/skillify` Equivalent (MEDIUM)
**Our Plan**: No mention
**Reality**: Grok Build's `/skillify` runs a **4-round interview** (AIP-3 standard) to generate a portable `SKILL.md` with slash commands, hooks, and MCP configs. This is how users extend the agent.

**Missing**: We need `/omega-skill capture` that interviews the user and generates a WAD-compatible skill bundle.

### Gap 7: Headless Mode & CI/CD Integration (MEDIUM)
**Our Plan**: No mention
**Reality**: Grok Build's headless mode (`grok -p "prompt"`) outputs streaming JSON and is designed for CI/CD pipelines. The ACP `session/prompt` supports `stream: true` for real-time updates.

**Missing**: Our TUI must support a **headless CLI entry point** that speaks ACP over stdio for scripting.

### Gap 8: Configuration Pinning & Fail-Closed Startup (HIGH)
**Our Plan**: No mention
**Reality**: Grok Build uses a **5-layer config merge** with `requirements.toml` that **cannot be overridden** (fail-closed). If mandates are violated, the binary refuses to start.

**Missing**: We need the **Omega Config Validator** that reads `/etc/omega/requirements.omega`, merges 5 layers, and blocks startup on any mandate violation.

---

## ✅ LESSONS TO APPLY FROM GROK BUILD

### 1. ACP as the Universal Backbone
**Lesson**: Don't build custom agent communication. ACP (JSON-RPC 2.0 over stdio) is the standard. Our TUI = ACP Client. Agent Runtime = ACP Server. This gives us editor integration (VS Code, Zed, Neovim) for free.

**Apply**: Implement the full ACP client method set (`fs/*`, `terminal/*`, `shell/*`) with a Permission Broker modal.

### 2. JSONL + Rewind Points = Sovereign Continuity
**Lesson**: Grok Build's `updates.jsonl` (ACP event stream) + `rewind_points.jsonl` (per-turn file snapshots) is the **only pattern** that survives crashes, compaction, and enables deterministic replay.

**Apply**: Our pragmatic plan's "JSONL + Rewind" is correct. Ensure we map ACP `session/update` notifications directly to JSONL append.

### 3. Kernel-Enforced Sandboxing (nono)
**Lesson**: `nono` (Landlock/Seatbelt) provides **irreversible, kernel-enforced** sandboxing at process startup. Per-profile `sandbox.toml` with additive deny globs. This is non-negotiable for M23.

**Apply**: Use `nono-py` bindings. Define per-entity `sandbox.toml` in `data/entities/<entity>/`. Kali = network blocked, P7 = network allowed.

### 4. Elm Architecture for TUI Event Loop
**Lesson**: Grok CLI uses pure Elm (Action → dispatch → Effect → Event Loop). The `dispatch` function is a **pure reducer** — fully testable, zero I/O. Effects are explicit enums spawned in a `JoinSet`.

**Apply**: Our TUI core loop must be Elm-style. React components handle rendering; the Elm loop handles state transitions. This survives compaction and enables time-travel debugging.

### 5. Hybrid Memory: FTS5 + sqlite-vec + Temporal Decay
**Lesson**: Grok Build uses FTS5 (BM25) + sqlite-vec (vector) with 0.7/0.3 weighting, source weights, and **half-life 7 days** temporal decay. `/dream` reorganizes memory (cosine 0.92 dedup).

**Apply**: Our Memory DAG must be backed by this hybrid store. Power-law decay (Forge 2) is the Omega enhancement.

### 6. Unified Extension Modal (5 Tabs)
**Lesson**: Grok Build's `Ctrl+Shift+O` opens a unified modal: Hooks, Plugins, Marketplace, Skills, MCPs. SHA-pinned plugins. Marketplace installs from git.

**Apply**: Our `/omega-extensions` with P1-P10 tabs + Marketplace. WAD bundles (SHA-pinned) instead of plugins.

### 6. Subagent Spawning with Worktree Isolation
**Lesson**: Grok Build spawns subagents via ACP `spawn_subagent` with **capability modes** and **git worktree isolation** (each subagent gets its own worktree to prevent conflicts).

**Apply**: Our Fleet Orchestrator must spawn subagents with isolated worktrees and explicit capability grants.

---

## ✅ LESSONS TO APPLY FROM FREEBUFF

### 1. OpenTUI + React = Developer Velocity
**Lesson**: OpenTUI's Zig core + React 19 reconciler gives **no FPS cap**, ~50MB memory, Flexbox layout (Yoga), and familiar React patterns. Used in production by OpenCode and Freebuff.

**Apply**: Our TUI stack (OpenTUI + React) is correct. Leverage React hooks for local component state; Elm loop for global state.

### 2. Generator-Based Agent Steps (Internal to Agent)
**Lesson**: Freebuff uses `function* handleSteps` for cooperative multitasking within an agent turn. This keeps the agent responsive during long tool chains.

**Apply**: Our agent runtime (not the TUI) should use generator-based step execution for long-running tasks.

### 3. Compile-Time Feature Flags for Distribution
**Lesson**: Freebuff uses `FREEBUFF_MODE=true` (Bun `--define`) for dead-code elimination between Free/Paid variants.

**Apply**: Add `OMEGA_MODE=community|enterprise|dev` compile-time flags via Bun for build variants. Runtime 5-layer config handles sovereignty.

### 4. Three.js WebGPU Renderer for Architecture Diagrams
**Lesson**: OpenTUI supports a Three.js WebGPU renderer for 3D diagrams in terminals that support Kitty/Sixel graphics.

**Apply**: Optional enhancement for our Memory DAG — render as 3D force-directed graph in supported terminals (iTerm2, WezTerm, Ghostty), fallback to box-drawing chars.

---

## 🗺️ UPDATED IMPLEMENTATION PRIORITIES (Revised Phase 0)

### Week 1: ACP Foundation & Config Validator
1. **ACP Client Implementation** — Full method set (`fs/*`, `terminal/*`, `shell/*`) + Permission Broker modal
2. **Config Validator** — 5-layer merge + `/etc/omega/requirements.omega` fail-closed startup
3. **OpenTUI + React Base** — Grid layout, Elm loop integration, static state indicators

### Week 2: Session Management & Sandboxing
4. **ACP Session State Machine** — `session/new`, `session/load`, `session/prompt`, `session/cancel` + `grokSession` persistence
5. **MCP Registry** — Discovery, injection into `session/new`, readiness race handling
6. **nono-py Sandboxing** — Per-entity `sandbox.toml`, kernel-enforced profiles

### Week 3: Memory, Hooks & Plan Mode
7. **Hybrid Memory Store** — FTS5 + sqlite-vec + power-law decay + `/omega-dream`
8. **Hook Registry** — 14 lifecycle hooks, blocking `PreToolUse` for mandate gates
9. **Plan Mode UI** — Read-only `plan.md` gate at protocol level

### Week 4: Skills, Headless & Polish
10. **Skill System** — `/omega-skill capture` (4-round interview → WAD skill bundle)
11. **Headless CLI** — `omega -p "prompt"` streaming JSON over ACP stdio
12. **Forensic Log View** — Greppable, syntax-highlighted ACP event stream
13. **Performance Tuning** — UI throttling during inference, <5% CPU overhead

---

## 🎯 REVISED SUCCESS METRICS

| Metric | Target | Source |
|--------|--------|--------|
| **ACP Compliance** | 100% client methods | Grok Build |
| **Startup Fail-Closed** | Blocks on mandate violation | Grok Build |
| **Sandbox Enforcement** | Kernel-level (Landlock/Seatbelt) | Grok Build |
| **Session Replay** | Deterministic `/rewind` to any turn | Grok Build |
| **MCP Readiness** | Handshake complete before first prompt | agent-network fix |
| **UI CPU Overhead** | < 5% during inference | Pragmatic Plan |
| **Headless Streaming** | JSON over stdio for CI/CD | Grok Build |

---

*⬡ OMEGA ⬡ GROKSTER ⬡ GAP ANALYSIS COMPLETE ⬡ 2026-08-08*

**Our pragmatic plan was directionally correct but missed the ACP protocol depth. The gaps above are not optional — they are the difference between a demo and a sovereign agent runtime.**
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemini-3.1-pro | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
