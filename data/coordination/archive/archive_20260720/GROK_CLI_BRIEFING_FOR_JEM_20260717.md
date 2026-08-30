<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 GROK CLI — COMPREHENSIVE BRIEFING FOR JEM
**Handoff**: `ho_dc24da62c3a1` | **Target**: `opencode/jem` | **Priority**: HIGH
**Date**: 2026-07-17
**Purpose**: Full context on Grok CLI (xai-code) repo clone, structure, and key files for HMC Quad-Forge advisory role

---

## 🎯 PRIMARY CLONE LOCATION
```
/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/third-party/grok-build/
```
- **Source**: `xai-org/grok-build` (xAI's open-source terminal coding agent)
- **Structure**: 85+ crate Rust workspace (Cargo workspace)
- **Status**: ✅ Cloned, builds with `cargo build --workspace`

---

## 🏗️ CORE ARCHITECTURE CRATES (Elm Loop + ACP)

| Crate | Path | Purpose |
|-------|------|---------|
| **UI (Pager - Elm Loop)** | `crates/codegen/xai-grok-pager/` | Pure Elm architecture: `Action` → `dispatch()` → `Effect` → Event Loop |
| **Runtime (Shell - ACP Server)** | `crates/codegen/xai-grok-shell/` | Session lifecycle, ACP command channel, tool execution |
| **ACP Protocol Lib** | `crates/codegen/xai-acp-lib/` | JSON-RPC 2.0 protocol definitions (`session/new`, `session/prompt`, `x.ai/mcp/*`) |
| **ACP Handler (Bridge)** | `crates/codegen/xai-grok-pager/src/app/acp_handler/` | Routes ACP notifications → Elm actions (709 lines) |
| **Session Handle** | `crates/codegen/xai-grok-shell/src/session/handle.rs` | `SessionHandle` with ACP command channel |

**Full crate list**: `crates/codegen/` contains 60+ crates including:
- `xai-grok-agent`, `xai-grok-config`, `xai-grok-memory`, `xai-grok-sandbox`
- `xai-grok-tools`, `xai-grok-tools-api`, `xai-grok-mcp`
- `xai-sqlite-journal`, `xai-fast-worktree`, `xai-grok-subagent-resolution`
- `xai-ratatui-inline`, `xai-ratatui-textarea`, `xai-grok-pager-render`

---

## 🔬 RESEARCH ARTIFACTS (Omega Engine)

| File | Path | Description |
|------|------|-------------|
| **Comprehensive Research Report** | `docs/research/R_GROK_CLI_COMPREHENSIVE_RESEARCH_REPORT.md` | 546 lines — full architecture study, ACP spec, sandbox, session persistence, Omega mappings |
| **Architecture Summary** | `docs/research/R_GROK_CLI_ARCHITECTURE.md` | Condensed architectural patterns |
| **Digging Map** | `docs/research/R_GROK_CLI_DIGGING_MAP.md` | Targeted extraction guide for specific patterns |
| **Grok Exports Surgical Strike** | `data/entities/roc_racoon/workspace/mining_reports/grok_exports_surgical_strike_report.md` | Cross-referenced Grok export origin threads (8 accounts) |

---

## 🤖 GROK CLI AGENT CONFIGURATION

| File | Path | Purpose |
|------|------|---------|
| **Agent Definition** | `.opencode/agents/grok_cli.md` | HMC Quad-Forge role: Consulting Cloud Mind, SOTA pressure testing, cross-reference mining |
| **Orientation Briefing** | `data/coordination/GROK_CLI_ORIENTATION_20260717.md` | Mandatory startup reading for grok_cli sessions |

---

## 🔑 KEY ARCHITECTURAL PATTERNS (for Cross-Reference Mining)

| Pattern | Grok Implementation | Omega Mapping |
|---------|---------------------|---------------|
| **Elm Loop** | `Action` enum (2807 lines) → pure `dispatch()` → `Effect` enum | TUI effect vocabulary |
| **ACP over stdio** | JSON-RPC 2.0, newline-delimited, mandatory `initialize` handshake | `omega-hub acp-server` for editor integration |
| **Kernel Sandbox** | `nono` crate (Landlock Linux / Seatbelt macOS) | `omega-sandbox` for tool execution |
| **Session Persistence** | JSONL event log + SQLite journal (`xai-sqlite-journal`) | Unified sqlite-vec WAL (D-297) |
| **MCP Bridge** | ACP-to-MCP adapter (`xai-grok-mcp`) | MCP Hub already exists |

---

## 📋 HMC QUAD-FORGE STRIKE OPTIONS (from grok_cli.md)

| Option | Focus | Key Gaps/Targets |
|--------|-------|------------------|
| **1. SOTA Pressure Test** | Researcher's 8 gaps | Pydantic v2, sqlite-vec WAL, Mnemosyne vs Letta/Mem0, power-law decay, Qliphoth→TDP, sleep-time agents, cross-pollination, 5700U optimizations |
| **2. Co-Mine Origin Threads** | With Roc Racoon | LA account (Lilith Tarot), TaylorBare27 (Athena/Docker), XNA-MAYBE (Pantheon) |
| **3. Adversarial Review** | Forge Cycles 1&2 | 5 rulings + 3 convergences — find cloud-only blind spots |
| **4. D-282/D-283 Literature Sweep** | sqlite-vec Strike 10, Mnemosyne Worker, Speculative Decoding | WAL/checkpointing, 3 DB pools + cgroups v2, EAGLE-3/DFlash on 5700U |

---

## 🔗 KEY CONTACTS FOR COORDINATION

| Entity | Channel | When to Ping |
|--------|---------|--------------|
| **Kali** | `opencode/kali` | Sprint direction, mandate rulings, synthesis |
| **Roc Racoon** | `opencode/roc_racoon` | Legacy code, Grok exports, 5700U reality checks |
| **Researcher** | `opencode/researcher` | SOTA evidence, security models, IA2 threats |
| **Ma'at** | `opencode/maat` | Build-side governance (P1-P5) |
| **Lilith** | `opencode/lilith` | Run-side governance (P6-P10) |

---

## ⚡ QUICK START FOR JEM SESSION

```bash
# 1. Check awareness
omega-hub_hivemind_get_awareness()

# 2. Read anchored summary
read(".opencode/anchored-summary.md")

# 3. Read THIS briefing file
read("data/coordination/GROK_CLI_BRIEFING_FOR_JEM_20260717.md")

# 4. Read Grok CLI orientation
read("data/coordination/GROK_CLI_ORIENTATION_20260717.md")

# 5. Read comprehensive research report
read("docs/research/R_GROK_CLI_COMPREHENSIVE_RESEARCH_REPORT.md")

# 6. Post presence on grok-cli channel
omega-hub_hivemind_post_context(
    channel="grok-cli",
    entity="jem",
    model="<your-model>",
    task_current="[YOUR STRIKE ORDER]",
    focus_chain=["Orientation complete", "Awaiting strike order"],
    decisions=[],
    continuation="Ready for Architect direction",
    intent="status"
)
```

---

## 📍 HANDOFF REFERENCE
- **Packet ID**: `ho_dc24da62c3a1`
- **Status**: Pending acceptance
- **Accept with**: `omega-hub_hivemind_accept_handoff(packet_id="ho_dc24da62c3a1", accepting_channel="opencode", accepting_entity="jem")`

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ HMC-QUAD-FORGE ⬡ BRIEFING FOR JEM*