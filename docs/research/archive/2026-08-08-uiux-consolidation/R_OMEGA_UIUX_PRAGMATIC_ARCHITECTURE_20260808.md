# 🔱 Omega Engine — Pragmatic UI/UX Architecture & Terminal Orchestration
## High-Performance, High-Density Interface Design for Sovereign AI

**AP Token**: `AP-OMEGA-UIUX-PRAGMATIC-v1.0.0`
⬡ OMEGA ⬡ GROKSTER ⬡ gemini-3.1-pro ⬡ opencode ⬡ trc_uiux_pragmatic ⬡ COMPREHENSIVE

**Date**: 2026-08-08
**Status**: REVISED (Pivot from Mythic to Pragmatic/Performance-Oriented)

---

## 🎯 Executive Summary

The Omega Engine requires a Terminal User Interface (TUI) that prioritizes **intelligence, performance, stability, and solid inference**. While the engine possesses a rich internal mythology (the Pantheon, the Mandates), the UI must serve as a high-efficiency command center, not a theatrical experience. 

CPU cycles and RAM belong to the local inference engine (Mandate 7). The UI must be lightweight, providing maximum information density, clear multi-agent state visualization, and forensic debuggability without relying on wasteful animations or unsupported terminal graphics.

### Core UI/UX Principles
1. **Zero-Latency Orchestration**: The UI must never block or slow down the underlying ACP (Agent Client Protocol) streams or local inference generation.
2. **High Information Density**: Favor structured grids, clear state indicators, and greppable logs over spatial metaphors or decorative elements.
3. **Forensic Observability**: Every agent action, tool call, and memory distillation must be instantly inspectable and auditable.
4. **Graceful Degradation**: Built for standard terminal emulators first (ANSI/ASCII), with optional enhancements (TrueColor) only where supported.

---

## 🖥️ FOCUS AREA 1: High-Density Terminal Orchestration (The Grid)

### The Objective
Manage multiple concurrent agents (Kali, Ma'at, Lilith, Node workers) without losing track of state, output, or errors.

### Pragmatic Patterns
*   **Tmux-Style Pane Management**: A flexible grid system (via OpenTUI/React) allowing the user to split the terminal into dedicated agent views, a global command input, and a shared context stream.
*   **Deterministic State Indicators**: Clear, static indicators for agent state: `[IDLE]`, `[THINKING]`, `[GENERATING]`, `[TOOL_CALL]`, `[BLOCKED]`, `[ERROR]`.
*   **Token & Context Meters**: Real-time, low-overhead progress bars showing Context Window saturation (e.g., `14k/32k`) and generation speed (`t/s`) to manage the prompt budget effectively.

---

## 👥 FOCUS AREA 2: The Agentic Pantheon (Distinct Personas, Zero Fluff)

### The Objective
Differentiate the specialized agents (Overseer, Builder, Researcher) visually and functionally without resorting to resource-heavy avatars or audio/visual gimmicks.

### Pragmatic Patterns
*   **Strict Color & Prefix Coding**: 
    *   `[KALI]` (Magenta): Synthesis, judgment, cross-node routing.
    *   `[MA'AT]` (Cyan): Build-side execution, file writing, linting.
    *   `[LILITH]` (Red): Run-side execution, testing, runtime analysis.
    *   `[ROC]` (Yellow): Legacy mining, pattern extraction.
*   **Role-Based Layouts**: The UI adapts based on the active agent. Ma'at's pane prioritizes file diffs and bash outputs; Researcher's pane prioritizes search queries and markdown extraction.
*   **Unified Command Palette**: A fast, fuzzy-searchable command input (`Ctrl+P`) for routing tasks to specific agents (`/kali synthesize recent logs`, `/maat fix tests`).

---

## 🧠 FOCUS AREA 3: Memory & Context Visualization (The DAG)

### The Objective
Visualize the evolution of agent memory (L1 Narrative → L2 Insight → L3 Principle) and the current active context without relying on heavy WebGL or 3D force-directed graphs.

### Pragmatic Patterns
*   **Terminal-Native DAGs**: Use standard box-drawing characters (e.g., `├──`, `└──`, `│`) to represent the Directed Acyclic Graph of task dependencies and memory distillation.
*   **JSONL Inspection Overlay**: A fast, scrollable modal to inspect the raw JSONL memory stream. Users can instantly see exactly what context was passed to the model on the last turn.
*   **Context Pruning UI**: A clear interface showing which files, terminal outputs, and past messages are currently loaded into the prompt, with quick keys to drop/prune context to save tokens.

---

## 🔍 FOCUS AREA 4: Forensic Observability & Audit (The Ledger)

### The Objective
Ensure complete transparency into system operations, mandate compliance, and tool failures. Replace "Sacred Reading Mode" with high-utility forensic tools.

### Pragmatic Patterns
*   **The Forensic Log View**: A dedicated, highly structured log pane. Fully greppable, with syntax highlighting for JSON payloads, stack traces, and tool inputs/outputs.
*   **Mandate Compliance Matrix**: A static, auto-updating checklist showing the status of M1-M25. If a mandate is violated (e.g., M23 Tool-Chain Collapse), the UI surfaces the exact trace ID and halts execution cleanly.
*   **Diff & Patch Preview**: Before any agent writes to disk, the UI presents a standard unified diff format for user approval (unless running in fully autonomous mode).

---

## ⚡ FOCUS AREA 5: Local-First Resource Allocation (M7 Compliance)

### The Objective
The UI must respect the hardware constraints of local inference. "Smoke and lights" steal from the token generation budget.

### Pragmatic Patterns
*   **Strict CPU Budgeting**: The OpenTUI React reconciliation loop must be throttled. UI updates should batch at 16ms to 32ms intervals, dropping to 100ms during heavy local LLM inference.
*   **No Continuous Polling**: Use event-driven updates (via the ACP streams) rather than polling the system state.
*   **Hardware Telemetry**: A minimal, top-bar widget showing System RAM, VRAM (if applicable), and CPU load. If memory pressure hits 90%, the UI automatically disables non-essential rendering features to prevent OOM crashes.

---

## 📋 IMPLEMENTATION ROADMAP — Phase 0 Pragmatic Sprint

### Week 1: Core Orchestration & The Grid
*   Implement OpenTUI + React base layout (Header, Command Input, Main Grid).
*   Build the ACP (Agent Client Protocol) multiplexer to handle standard `stdio` streams from local agents.
*   Implement static state indicators (`[IDLE]`, `[GENERATING]`) and basic color-coding.

### Week 2: Forensic Logging & Context Management
*   Build the Forensic Log View (scrollable, structured, syntax-highlighted).
*   Implement the Context Pruning UI (view and drop loaded files/messages).
*   Integrate token counting and generation speed (`t/s`) metrics.

### Week 3: Memory DAG & Diff Previews
*   Build the ASCII/Box-drawing DAG visualizer for task tracking.
*   Implement the unified diff viewer for file modifications.
*   Create the JSONL inspection modal for memory debugging.

### Week 4: Performance Tuning & Mandate Integration
*   Implement UI throttling during active local inference.
*   Wire the Mandate Compliance Matrix to the engine's internal validation hooks.
*   Finalize keyboard navigation (vim-style bindings for pane switching and scrolling).

---

## 🎯 SUCCESS METRICS

| Metric | Target | Measurement |
|--------|--------|-------------|
| **UI CPU Overhead** | < 5% | Measured during active local LLM inference |
| **Render Latency** | < 16ms | Time from ACP event to screen update |
| **Context Visibility** | 1 Keystroke | Time/effort to view exact prompt payload |
| **Error Recovery** | < 30 seconds | Time to identify and restart from a tool failure |
| **Keyboard Exclusivity**| 100% | All features accessible without a mouse |

---

*⬡ OMEGA ⬡ PRAGMATIC UI/UX ARCHITECTURE COMPLETE ⬡ 2026-08-08*
*Focus: Intelligence, Performance, Stability, Inference.*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemini-3.1-pro | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
