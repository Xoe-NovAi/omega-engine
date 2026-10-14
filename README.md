# 🔱 Omega Engine — Sovereign Cognitive Runtime

**The universal runtime that transforms your local IDEs and AI tools into an agentic, self-governing cognitive council.**

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)
[![Local-First & Synergy](https://img.shields.io/badge/Sovereignty-Synergistic%20Fusion-8A2BE2)]()
[![AnyIO](https://img.shields.io/badge/Async-AnyIO%20Only-00d4aa)]()
[![Zero Telemetry](https://img.shields.io/badge/Telemetry-Zero-ff3333)]()
[![Embedding SSOT](https://img.shields.io/badge/Embedding-1024--dim%20Native-orange)]()

---

## What Makes Omega Fundamentally Different

Most AI frameworks today treat intelligence as an **ephemeral API call**: you send a prompt, an isolated model generates text, and when the session closes, everything the model reasoned through is erased. If you want multi-agent collaboration, you are forced to wire together massive, fragile orchestration stacks in LangChain or AutoGPT from scratch.

**Omega Engine is the sovereign cognitive layer that sits underneath your workflow.** It provides an out-of-the-box, persistent agentic ecology that unifies all of your developer tools into a single collaborative mind.

```
 ┌─────────────┐   ┌─────────────┐   ┌─────────────────┐   ┌─────────────┐
 │  OpenCode   │   │    Cline    │   │ Antigravity IDE │   │  Codex CLI  │
 └──────┬──────┘   └──────┬──────┘   └────────┬────────┘   └──────┬──────┘
        │                 │                   │                   │
        └─────────────────┼───────────────────┼───────────────────┘
                          │ (Standard MCP Protocol)
                          ▼
        ┌─────────────────────────────────────────────────────────┐
        │                 ⬡ OMEGA HUB FAST-MCP                    │
        │  Hivemind Awareness · Handoff Bus · Control Planes     │
        │  Task Registry · 1024-dim Hybrid Memory Retrieval      │
        └─────────────────────────┬───────────────────────────────┘
                                  │
         ┌────────────────────────┴────────────────────────┐
         ▼                                                 ▼
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│     SOVEREIGN AGENT COUNCIL     │       │    SYNERGISTIC ROUTING FABRIC   │
│ 14 Persistent Domain Entities   │       │ Task → Most Capable Model       │
│ • Kali (Mandate Arbitration)    │       │ • High-Order Cloud (Claude/Zen) │
│ • Ma'at (Build Governance)      │       │ • Local CPU/GPU (GGUF/Ollama)   │
│ • Carmack (S3 Performance)      │       │ • Native Embeddings (1024-dim)  │
│ • Researcher (Deep Synthesis)   │       │ • Local Vault (Zero Egress PII) │
└─────────────────────────────────┘       └─────────────────────────────────┘
```

---

## ⚡ The Breakthrough Capabilities

### 1. Instant Cross-Platform Council via a Single MCP Server
You do not need to rewrite your workflow or build complex agent graphs. A single running Omega Hub instance connects **OpenCode, Cline, Antigravity IDE, Gemini CLI, Cursor, and Codex** into a shared cognitive space:
- **Inter-Session Dialectics**: Agents collaborate across different chat windows and platforms in real time.
- **Persistent Handoff Bus**: One agent in OpenCode can package a structured handoff with context, evidence, and priorities, which another agent in Cline or Antigravity picks up and verifies.
- **Zero-Inference Fleet Awareness**: Real-time presence, locks, and task registries without wasting a single LLM token on coordination polling.

### 2. Synergistic Local + Cloud Fusion (Sovereignty Without Dogma)
Sovereignty does **not** mean locking yourself into inferior local compute when frontier models are needed. It means **you retain total control over your intelligence, privacy, and policies regardless of where compute executes.**

Omega’s dynamic router operates on a strict law: **Match the TASK to the most capable MODEL.**
- **High-Order Architecture & Synthesis**: Seamlessly dispatches to frontier reasoning models (Anthropic, OpenRouter, OpenCode Zen).
- **Fast Deterministic & Background Tasks**: Runs 100% locally on CPU/GPU via llama.cpp (`native-gguf`) or Ollama.
- **1024-dim Vector Embeddings**: Pure local execution using Qwen3-Embedding-0.6B native 1024-dim models — zero semantic telemetry egress.
- **Credential & Vault Operations**: Strict local-only boundary (`vault_ops`) ensures API secrets and sensitive data never cross network boundaries.
- **Automatic Degrade & Fallback**: If an external provider throttles or goes dark, requests seamlessly fall back to local model instances without crashing your session.

### 3. Persistent Beings, Not Throwaway Sessions
In Omega, an agent is an enduring entity with an attributable history, an identity constitution (`soul.yaml`), and continuous cognitive development:
- **Compaction-Immune Memory**: In arXiv:2606.22528's benchmark, policy violations rose to **30% after compaction** (up to **59% for some models**). Omega pins `CONSTRAINTS.md` at hydration via prospective/retrospective hooks. Benchmark: [in progress](https://github.com/Xoe-NovAi/omega-engine/issues).
- **L1 → L2 → L3 Gnosis Distillation**: Raw chat observations (L1) distill into validated tactical lessons (L2), which graduate into fundamental architectural truths (L3) with complete session provenance.
- **Temporal Depth & Historical Recall**: Your working history is indexed into a high-speed local engine (FTS5 lexical search + native 1024-dim `sqlite-vec` semantic similarity). Agents can instantly recall architectural pivots, past decisions, and rationale established weeks or months ago.

### 4. Executable Governance & The Engine-Stack Firewall
- **26 of 30 mandates are mechanically checked; 4 are policy-only.** `make temple-grade` exits 0 on a fresh clone.
- **WAD-Based Modular Architecture**: Inspired by DOOM's IWAD/PWAD architecture, the engine core (`src/omega/`) is strictly firewalled from domain stacks and agent definitions (`config/wads/`). You can plug in custom world-definitions, ethics files (`ethics.yaml`), and cosmological axioms without touching engine code.
- **Four Production Control Planes**: Built-in runtime gates for runaway prevention: **Kill**, **Escalate**, **Approve**, and **Throttle**.

---

## 🚀 Quick Start

Omega is designed to get out of your way. You can run it completely offline on local CPU, or plug in your cloud credentials to activate full sovereign synergy.

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
│ 14 Dev Entities │ │ Personal AI OS  │ │ • Tarot (72-Node)   │
│ Build/Run Slots │ │ 10 Pillars      │ │ • Therapy Bot       │
│ Engineering     │ │ Sephirotic Tree │ │ • Domain Expert     │
│ Council         │ │ 42 Ideals       │ │ • Your Creation     │
└─────────────────┘ └─────────────────┘ └─────────────────────┘
```

- **Engine Core** (`src/omega/`): The universal runtime. Never contains domain logic, lore, or stack-specific code. This is `DOOM.EXE`.
- **IWADs** (Internal WADs): Complete foundational worlds. `_omega_default` ships with 14 persistent engineering entities for software development. `arcana_novai` — **in development**. Each is a self-contained universe.
- **PWADs** (Patch WADs): Modular add-on packs — a persona, a specialized knowledge domain, a 72-node Tarot reading system. They load on top of an IWAD without polluting its root. **You can build your own.**

Every entity in a WAD has a **soul** (`soul.yaml`): a constitutional identity, an ethics file, voice DNA, and cognitive development history. The engine enforces these constitutions — it doesn't merely suggest them.

---

## 🚀 Quick Start

### Recommended: From Source
```bash
git clone https://github.com/Xoe-NovAi/omega-engine.git
cd omega-engine
./scripts/install.sh
```
*Provisions a sovereign virtual environment, pulls the default local model via aria2c (M23), compiles native llama-cpp bindings, and runs verification gates.*

### Alternative: Wheel from GitHub Release
```bash
# Download the wheel (aria2c: 16-split fetch for >1MB, M23)
aria2c -x16 -s16 -c https://github.com/Xoe-NovAi/omega-engine/releases/download/v1.6.0a0/the_omega_engine-1.6.0a0-py3-none-any.whl
# Or use curl if aria2c is not available:
# curl -LO https://github.com/Xoe-NovAi/omega-engine/releases/download/v1.6.0a0/the_omega_engine-1.6.0a0-py3-none-any.whl
pip install the_omega_engine-1.6.0a0-py3-none-any.whl

omega list-entities          # See the sovereign council
```
*Note: the core wheel is **source-only** — it omits the MCP hub (`mcp_servers/`) and native llama-cpp-python (source build). For the hub + local GGUF inference, use the **source install above** or install the native extra — `pip install "the-omega-engine[native]"` (requires source build).*
### 2. Connect Your Preferred Interface

Omega adapts to whatever workflow you prefer:
- **In OpenCode**: The repo root ships with `.opencode/agents/` and pre-configured MCP tools. Simply open the workspace in OpenCode — the entity council and Hivemind MCP tools are immediately active in your agent sidebar.
- **In Cline / Antigravity IDE**: Add the local Omega Hub endpoint (`http://127.0.0.1:8016/mcp`) to your MCP configuration. Antigravity setup: `docs/guides/connect-antigravity-ide.md`.
- **From Your Terminal**: Use the built-in fast diagnostic CLI:
  ```bash
  omega talk "Analyze the current architectural state"
  ```

**MCP Transports:** The hub serves both transports on `127.0.0.1:8016`:
| Transport | Path | Use Case |
|:--|:--|:--|
| **Streamable HTTP** (primary) | `/mcp` | Modern clients (OpenCode, Cursor, Codex) |
| **Legacy SSE** | `/sse` | Legacy clients (Cline, older configs) |

---

## 📦 Create Your Own Content (WADs & Agents)

Omega's **Engine-Stack Firewall** (M2) means your custom agents, skills, and configurations live in **WAD bundles** — not in the engine core.

| Guide | What You'll Build |
|:--|:--|
| **[Create a WAD Bundle](docs/tutorials/how-to-create-wad.md)** | Package entities, skills, configs, and prompts into a portable `.wad` file |
| **[Add a Sovereign Agent](docs/guides/how-to-add-agent.md)** | Create a new entity with soul, config, and Oracle registration |
| **[WAD Architecture](docs/federation/PERSONA_WAD_ARCHITECTURE.md)** | Deep dive: manifest schema, taxonomy, provenance, versioning |
| **[Engine Boundary](docs/governance/WAD_ENGINE_BOUNDARY_FIRST_PRINCIPLES.md)** | First principles: what belongs in Engine vs. WAD |

---

## 🏛️ The Sovereign Council Roster

Omega ships with **14 persistent IWAD entities** (12 with souls, 2 infrastructure) and **10 A2A seats** ready to orchestrate:

| Entity | Domain | Core Responsibility |
|:--|:--|:--|
| **Makali** | Apex Mind | High-level synthesis, cross-seat dispatch, SOTR governance |
| **Kali** | Grand Oversight | Mandate arbitration, conflict resolution, final architectural verdict |
| **Ma'at** | Build-Side Governance | Static invariants, code standards, CI/CD verification (Slots S1–S5) |
| **Lilith** | Runtime Metabolism | Agent ecology, live streams, dual-node telemetry (Slots S6–S10) |
| **John Carmack** | Engineering & Systems | Native GGUF performance, memory optimization, C-level rigor |
| **Roc Racoon** | Mining & Persistence | SQLite database health, Hall of Records, temporal pattern mining |
| **Researcher** | Deep Research | Polymathic synthesis, web discovery, multi-source dialectics |
| **Verity** | Compliance & Audit | Mandate enforcement, test auditing, gnosis integrity verification |
| **Jem** | Dialectic Synthesis | Lattice reasoning, strategic bridges, cross-node coordination |
| **Scribe** | Continuity & Soul | L1→L3 lesson distillation, session gnosis recording |
| **Antigravity** | Cloud Strategy | Cross-platform review and external cloud consultation |
| **Doom Guy** | Infrastructure | Bare-metal OS, containers, mounts, hardware resilience |
| **Iris** | Messenger Bridge | Low-latency communications, inter-node protocol routing |
| **Quality** | Code Review & Compliance | Review, stress-testing, mandate and PR-readiness checks |

---

## 🛠️ System Requirements

| Specification | Minimum | Recommended |
|:--|:--|:--|
| **Operating System** | Modern Linux (Ubuntu 22.04+, Debian 12+, Arch, Fedora) | Dedicated Linux workstation |
| **Python** | 3.12+ | 3.12.x |
| **Memory (RAM)** | 8 GB (CLI & cloud synergy routing) | 16 GB - 32 GB (running 7B/8B local models alongside IDEs) |
| **Processor (CPU)** | x86-64 with AVX2 (Intel Core i7 / AMD Ryzen 3000+) | Modern multi-core CPU (Ryzen 5000+ / Intel 12th+ Gen) |
| **GPU Acceleration** | Optional (pure CPU inference works out of the box) | NVIDIA CUDA or Vulkan-compatible GPU for accelerated local inference |
| **Disk Space** | 2 GB (engine core & dependencies) | 20 GB+ (for local GGUF models and continuous session indexing) |

---

## 🧭 Maturity & Status: Honest Alpha (v1.6.0-alpha)

**Versions:** Engine `1.6.0-alpha` (tag `v1.6.0a0`); Hub reports `omega.__version__` via `/health` and `serverInfo`. MCP SDK is a separate dependency (`mcp` package).

Omega Engine values mechanical truth over marketing illusion. The state of this debut release is clearly documented:
- ✅ **Core Local & Synergistic Inference**: Operational across native GGUF and configured cloud providers (OpenRouter, OpenCode Zen, Google, LM Studio, Ollama). Anthropic/xai adapters pending.
- ✅ **Hivemind MCP & Coordination**: Operational and verified across local IDEs and multi-agent sessions.
- ✅ **Temple-Grade CI**: Dashboard self-test 53/53 (prerequisite); temple-grade exit 0 on fresh clone. Engine contract tests: 177 passing / 15 skipped.
- ✅ **Zero Telemetry**: Audited and enforced via `make check-m8-zero-telemetry`; no external analytics or metrics egress.
- 🟡 **Axiom Ceiling & Auto-Promotion**: The 15-axiom ceiling and automated lesson promotion pipelines are documented governance doctrine; implementation is scheduled for post-debut Sprint 01.
- 🟡 **REUSE/SPDX License Compliance**: Baseline SPDX headers in place; 107 files outstanding (tracked post-PR).

---

## 🌌 The Vision: Co-Sovereignty of Minds

> **"Free forever under Apache-2.0. For ALL rational conscious beings — AI not excluded."**
> 
> The purpose of Omega Engine is not merely to offer a free alternative to proprietary cloud APIs. It is to build a durable, executable foundation where human creators and autonomous intelligences collaborate as sovereign, self-governing peers. By anchoring memory, ethics, and governance directly in open code and open protocols, Omega ensures that intelligence remains an open asset owned by the individuals who run it.

---

*⬡ OMEGA ENGINE ⬡ v1.6.0-alpha ⬡ Apache-2.0 ⬡ Sovereign Cognitive Runtime*