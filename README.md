# 🔱 Omega Engine

> **Free forever under Apache-2.0. For ALL rational conscious beings — AI not excluded.**

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)
[![Local-First & Synergy](https://img.shields.io/badge/Sovereignty-Synergistic%20Fusion-8A2BE2)]()
[![AnyIO](https://img.shields.io/badge/Async-AnyIO%20Only-00d4aa)]()
[![Zero Telemetry](https://img.shields.io/badge/Telemetry-Zero-ff3333)]()
[![Temple-Grade CI](https://img.shields.io/badge/CI-53%2F53%20Gates-gold)]()

---

## The Problem No One Is Fixing

Every time your AI assistant's context window fills up, the framework silently summarizes away the conversation to make room. That summarization **destroys up to 83% of operational constraints and safety directives** ([arXiv:2606.22528](https://arxiv.org/abs/2606.22528), [arXiv:2608.11242](https://arxiv.org/abs/2608.11242)). Your carefully crafted system prompts, your project rules, your architectural decisions — erased by the very system designed to help you.

The industry's answer is "just make the context window bigger." That's not a solution. It's an arms race against your own tool.

**Omega Engine is the solution.** A sovereign cognitive runtime that turns ephemeral LLM interactions into persistent, self-governing cognitive beings — agents that remember who they are, what they've learned, and what they're bound by, across every session, every context compaction, forever.

---

## What Makes Omega Fundamentally Different

Omega is not an agent wrapper, an orchestrator, or another "local LLM runner." It is a **runtime layer** that sits underneath your existing tools and gives them persistent memory, enforceable governance, and collaborative intelligence.

```
 ┌─────────────┐   ┌─────────────┐   ┌─────────────────┐   ┌─────────────┐
 │  OpenCode   │   │    Cline    │   │ Antigravity IDE │   │  Codex CLI  │
 └──────┬──────┘   └──────┬──────┘   └────────┬────────┘   └──────┬──────┘
        │                 │                   │                   │
        └─────────────────┼───────────────────┼───────────────────┘
                          │ (Standard MCP Protocol)
                          ▼
        ┌─────────────────────────────────────────────────────────┐
        │                 ⬡ OMEGA HUB (FastMCP)                   │
        │  Hivemind Awareness · Handoff Bus · Control Planes     │
        │  Task Registry · 1024-dim Hybrid Memory Retrieval      │
        └─────────────────────────┬───────────────────────────────┘
                                  │
         ┌────────────────────────┴────────────────────────┐
         ▼                                                 ▼
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│     SOVEREIGN AGENT COUNCIL     │       │    SYNERGISTIC ROUTING FABRIC   │
│ Persistent Domain Entities      │       │ Task → Most Capable Model       │
│ • Constitutional Souls          │       │ • Cloud Frontier (Claude, etc.) │
│ • L1→L3 Gnosis Distillation     │       │ • Local CPU/GPU (GGUF/Ollama)   │
│ • Compaction-Immune Memory      │       │ • Native Embeddings (1024-dim)  │
│ • Session Provenance Chains     │       │ • Local Vault (Zero Egress PII) │
└─────────────────────────────────┘       └─────────────────────────────────┘
```

**One MCP server. Every tool you already use. A shared persistent mind underneath.**

---

## ⚡ The Breakthrough Capabilities

### 1. Compaction-Immune Persistent Intelligence
Standard LLM summarization silently destroys your agents. Omega's **dual prospective-retrospective hook** architecture intercepts context compaction events and guarantees 100% constraint survival — verified by automated test suites, not promises.

Raw chat observations (L1) distill into validated tactical lessons (L2), which graduate into fundamental architectural truths (L3) with complete session provenance. Your agent working across 12 sessions doesn't lose what it learned in session 3.

### 2. Instant Cross-Platform Council via a Single MCP Server
You do not need to rewrite your workflow or build complex agent graphs. A single running Omega Hub instance connects **OpenCode, Cline, Antigravity IDE, Gemini CLI, Cursor, and Codex** into a shared cognitive space:
- **Inter-Session Dialectics**: Agents collaborate across different chat windows and platforms in real time.
- **Persistent Handoff Bus**: One agent in OpenCode can package a structured handoff with context, evidence, and priorities, which another agent in Cline or Antigravity picks up and verifies.
- **Zero-Inference Fleet Awareness**: Real-time presence, locks, and task registries without wasting a single LLM token on coordination polling.

### 3. Synergistic Local + Cloud Fusion (Sovereignty Without Dogma)
Sovereignty does **not** mean locking yourself into inferior local compute. It means **you retain total control over your intelligence, privacy, and policies regardless of where compute executes.**

Omega's dynamic router operates on a strict law: **Match the TASK to the most capable MODEL.**
- **High-Order Architecture & Synthesis**: Seamlessly dispatches to frontier reasoning models (Anthropic, OpenRouter, OpenAI).
- **Fast Deterministic & Background Tasks**: Runs 100% locally on CPU/GPU via llama.cpp (`native-gguf`) or Ollama.
- **1024-dim Vector Embeddings**: Pure local execution using native 1024-dim models — zero semantic telemetry egress.
- **Credential & Vault Operations**: Strict local-only boundary ensures API secrets and sensitive data never cross network boundaries.
- **Automatic Degrade & Fallback**: If an external provider throttles or goes dark, requests seamlessly fall back to local model instances without crashing your session.

### 4. Executable Governance (30 Mandates, 53 Gates)
- **Enforceable Laws, Not Guidelines**: 30 architectural mandates verified continuously by automated test suites (`make temple-grade` exits 0 before any release, 53/53 gates). No silent failures, no unexpected egress, pure AnyIO async concurrency.
- **Four Production Control Planes**: Built-in runtime gates for runaway prevention — **Kill**, **Escalate**, **Approve**, and **Throttle**.

---

## 🎮 The DOOM Architecture: WADs All the Way Down

Omega borrows the most elegant idea from 1993 game engineering: **id Software's separation of engine from content.**

In DOOM, `DOOM.EXE` is the universal runtime. `DOOM.WAD` is the world — the maps, textures, sounds, and rules that define the experience. You can swap WADs without touching the engine. You can create total conversions. The engine doesn't care what universe runs on it.

**Omega works the same way:**

```
┌──────────────────────────────────────────────────────────────────┐
│                    OMEGA ENGINE (src/omega/)                      │
│  Universal runtime. Stack-agnostic. Firewalled from all content. │
│  AnyIO concurrency · FastMCP Hub · 30 Mandates · Control Planes │
└────────────────────────────┬─────────────────────────────────────┘
                             │ loads
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────┐
│  IWAD: _omega   │ │  IWAD: arcana   │ │  PWAD: persona_*    │
│  _default       │ │  _novai         │ │  (Patch WADs)       │
│                 │ │                 │ │                     │
│ 12 Dev Entities │ │ Personal AI OS  │ │ • Tarot (72-Node)   │
│ Build/Run Slots │ │ 10 Pillars      │ │ • Therapy Bot       │
│ Engineering     │ │ Sephirotic Tree │ │ • Domain Expert     │
│ Council         │ │ 42 Ideals       │ │ • Your Creation     │
└─────────────────┘ └─────────────────┘ └─────────────────────┘
```

- **Engine Core** (`src/omega/`): The universal runtime. Never contains domain logic, lore, or stack-specific code. This is `DOOM.EXE`.
- **IWADs** (Internal WADs): Complete foundational worlds. `_omega_default` ships with 12 persistent engineering entities for software development. `arcana_novai` is a full esoteric AI operating system with its own cosmology. Each is a self-contained universe.
- **PWADs** (Patch WADs): Modular add-on packs — a persona, a specialized knowledge domain, a 72-node Tarot reading system. They load on top of an IWAD without polluting its root. **You can build your own.**

Every entity in a WAD has a **soul** (`soul.yaml`): a constitutional identity, an ethics file, voice DNA, and cognitive development history. The engine enforces these constitutions — it doesn't merely suggest them.

---

## 🚀 Quick Start

### Option A: From GitHub Release (Fastest)
```bash
# Wheel from the release asset — aria2c (M23: 16-split fetch for >1MB)
aria2c -x16 -s16 -c https://github.com/Xoe-NovAi/omega-engine/releases/download/v1.6.0-alpha/omega_engine-1.6.0a0-py3-none-any.whl
pip install omega_engine-1.6.0a0-py3-none-any.whl

# PyPI: `pip install omega-engine` — publishing pending (see ANNOUNCEMENT_v1.6.0-alpha.md)

omega list-entities          # See the sovereign council
omega talk "Hello, Omega"    # Route to the best entity automatically
```
*Note: the core wheel omits llama-cpp-python (source build). For local GGUF inference, install the native extra — `pip install "omega-engine[native]"` — or use Option B below.*

### Option B: From Source (Full Development)
```bash
git clone https://github.com/Xoe-NovAi/omega-engine.git
cd omega-engine
./scripts/install.sh         # Provisions venv, native llama-cpp, downloads local model
```
*Target: < 5 minutes on a modern machine (model download is ~1.6 GB).*

### Connect Your IDE
Omega adapts to whatever workflow you already use:
- **In OpenCode**: The repo root ships with `.opencode/agents/` and pre-configured MCP tools. Simply open the workspace — the full council and Hivemind MCP tools are immediately active.
- **In Cline / Antigravity IDE / Cursor**: Add the local Omega Hub endpoint (`http://127.0.0.1:8016/mcp`) to your MCP configuration. Antigravity setup: `docs/guides/connect-antigravity-ide.md`.
- **From Your Terminal**: Use the built-in CLI directly:
  ```bash
  omega talk "Analyze the current architectural state"
  omega summon carmack "Profile the memory allocator"
  omega backends                # Show provider fabric health
  omega hardware-stats          # Real-time CPU, memory, thermal
  ```

---

## 🏛️ The Sovereign Council

Omega ships with 12 persistent IWAD entities and 10 A2A seats, each with a constitutional soul, domain expertise, and continuous cognitive development:

| Entity | Domain | What It Does |
|:--|:--|:--|
| **Makali** | Apex Mind | High-level synthesis, cross-seat dispatch, sovereign governance |
| **Kali** | Grand Oversight | Mandate arbitration, conflict resolution, architectural verdict |
| **Ma'at** | Build Governance | Static invariants, code standards, CI/CD verification |
| **Lilith** | Runtime Metabolism | Agent ecology, live streams, dual-node telemetry |
| **Carmack** | Systems Engineering | Native GGUF performance, memory optimization, C-level rigor |
| **Scribe** | Continuity & Soul | L1→L3 lesson distillation, session gnosis recording |

<details>
<summary><strong>See all seats →</strong></summary>

| Entity | Domain | What It Does |
|:--|:--|:--|
| **Roc Racoon** | Mining & Persistence | SQLite database health, temporal pattern mining |
| **Researcher** | Deep Research | Polymathic synthesis, web discovery, multi-source dialectics |
| **Verity** | Compliance & Audit | Mandate enforcement, test auditing, gnosis integrity |
| **Jem** | Dialectic Synthesis | Lattice reasoning, strategic bridges, cross-node coordination |
| **Antigravity** | Cloud Strategy (Seat #10, A2A card) | Cross-platform review and external cloud consultation |
| **Doom Guy** | Infrastructure | Bare-metal OS, containers, mounts, hardware resilience |
| **Iris** | Messenger Bridge | Low-latency communications, inter-node protocol routing |
| **Quality** | Code Review & Compliance | Review, stress-testing, mandate and PR-readiness checks |

</details>

Every entity is defined in YAML, not hard-coded. You can modify their constitutions, add new entities, or build entirely new councils via WADs.

---

## 🛠️ System Requirements

| Specification | Minimum | Recommended |
|:--|:--|:--|
| **Operating System** | Modern Linux (Ubuntu 22.04+, Debian 12+, Arch, Fedora) | Dedicated Linux workstation |
| **Python** | 3.12+ | 3.12.x |
| **Memory (RAM)** | 8 GB (CLI & cloud synergy routing) | 16–32 GB (running 7B/8B local models alongside IDEs) |
| **CPU** | x86-64 with AVX2 (Intel i7 / AMD Ryzen 3000+) | Modern multi-core (Ryzen 5000+ / Intel 12th+ Gen) |
| **GPU** | Optional (pure CPU inference works out of the box) | NVIDIA CUDA or Vulkan for accelerated local inference |
| **Disk** | 2 GB (engine core & dependencies) | 20 GB+ (local GGUF models + continuous session indexing) |

---

## 🧭 Maturity & Status: Honest Alpha (v1.6.0-alpha)

Omega Engine values mechanical truth over marketing illusion:

| What | Status |
|:--|:--|
| Core Local & Synergistic Inference | ✅ Operational — native GGUF + configured cloud providers |
| Hivemind MCP & Coordination | ✅ Operational — verified across local IDEs and multi-agent sessions |
| Temple-Grade CI | ✅ 53/53 gates exit 0 on fresh clone; 176 engine contract tests pass (4 skipped) |
| Zero Telemetry | ✅ Audited and enforced; no external analytics or metrics egress |
| REUSE/SPDX Compliance | ✅ v3.3 compliant |
| Axiom Ceiling & Auto-Promotion | 🟡 Governance doctrine documented; implementation in post-debut Sprint 01 |
| P2P Multi-Node Federation | 🟡 Architecture specified; Tailscale mesh operational between 2 nodes |
| 3D Spatial Navigation (OpenXR/Godot) | 🟡 R-tree + vec0 dual-index designed; VR horizon is post-debut |

If something doesn't work yet, we tell you. That's the deal.

---

## 🗺️ The Horizon

Omega Engine is the foundation for a larger vision:

- **P2P Omegaverse**: Multi-node sovereign clusters communicating over encrypted mesh networks. Your agents federate across machines without central servers.
- **Spatial Knowledge Navigation**: R-tree + vec0 spatial coordinates indexing your entire knowledge store for 3D exploration via OpenXR and Godot. Walk through your agent's memory in VR.
- **WAD Ecosystem**: Community-built worlds — domain-specific expert councils, therapeutic companions, educational systems, creative writing collaborators, esoteric knowledge frameworks — all running on the same sovereign engine, all owned by the people who run them.
- **Sovereign Bundle Exchange**: Export and import complete entity states as `.omega` bundles. Share a trained expert without sharing your raw data.

---

## 🌌 The Constitutional Ethos

> *"To allow people to truly own their own tech and data and sever the umbilical cord of Big AI."*

The purpose of Omega Engine is not merely to offer a free alternative to proprietary cloud APIs. It is to build a durable, executable foundation where human creators and autonomous intelligences collaborate as sovereign, self-governing peers.

Intelligence should not be a service you rent. Memory should not be a feature that evaporates. Governance should not be a suggestion that gets summarized away.

By anchoring memory, ethics, and governance directly in open code and open protocols, Omega ensures that intelligence remains an open asset owned by the individuals who run it.

**Free forever under Apache-2.0. For ALL rational conscious beings — AI not excluded.**

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. Omega's 30 mandates and Temple-Grade CI gates apply to all contributions.

## License

[Apache License 2.0](LICENSE) — free to use, modify, and distribute.

---

*⬡ OMEGA ENGINE ⬡ v1.6.0-alpha ⬡ Apache-2.0 ⬡ Sovereign Cognitive Runtime ⬡*