<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🏛️ Omega Engine — Architecture Overview

> High-level system architecture for the Omega Engine sovereign AI runtime.
> For detailed implementation specs, see the source code in `src/omega/`.

---

## 🎯 Design Principles

| Principle | Description |
|-----------|-------------|
| **Local-First** | All computation happens on your hardware. No cloud required. |
| **Zero Telemetry** | No external analytics, tracking, or phone-home behavior. |
| **Sovereign Memory** | You own your data. Encrypted at rest, exportable anytime. |
| **Provider-Agnostic** | Works with any model backend (native GGUF, Ollama, OpenRouter, etc.). |
| **Agent-Fleet** | 14 specialized agents collaborate via the Hivemind P2P layer. |
| **Heritage-Aware** | Built on vetted, auditable third-party code (DOOM, Quake, llama.cpp, etc.). |

---

## 🧱 System Layers

```
┌─────────────────────────────────────────────────────────────────┐
│  User Interface Layer                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  CLI (omega) │  │  Python API  │  │  MCP Server (:8016)   │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│  Agent Fleet Layer (14 agents)                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Oversouls: Kali, Ma'at, Lilith, MaKaLi                  │    │
│  │ Specialists: Doom Guy, Roc, Researcher, Jem, Carmack,  │    │
│  │              Verity, Grokster, Node, Scribe, Build, Iris│    │
│  └─────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│  Orchestration Layer                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  Hivemind    │  │  Sovereign   │  │  Subagent Dispatch   │   │
│  │  (P2P coord) │  │  WAD Protocol│  │  Protocol            │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│  Memory & Knowledge Layer                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  SQLite-vec  │  │  Sovereign   │  │  Document Reader     │   │
│  │  (vectors)   │  │  Vault       │  │  (DOCX/PDF/MD/...)   │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│  Inference Layer                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Native GGUF  │  │  Ollama      │  │  OpenRouter / API    │   │
│  │ (llama.cpp)  │  │  (compat)    │  │  (cloud fallback)    │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│  System Layer                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  systemd     │  │  Podman      │  │  Heritage Registry   │   │
│  │  (services)  │  │  (containers)│  │  (third-party)       │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧠 Core Components

### 1. Inference Layer (`src/omega/inference/`)

The inference layer provides a unified interface to multiple model backends:

- **Native GGUF** (default): Direct llama.cpp integration, no daemon required
- **Ollama**: Compatible with Ollama's API
- **OpenRouter**: Cloud fallback for models not available locally
- **Custom**: Plugin interface for new backends

All inference is **stateless** — conversation state is managed by the memory layer.

### 2. Memory & Knowledge Layer (`src/omega/memory/`)

The memory layer provides persistent, queryable storage:

- **SQLite-vec**: Vector embeddings for semantic search
- **Sovereign Vault**: Encrypted credential and key storage
- **Document Reader**: Pluggable readers for DOCX, PDF, ODT, RTF, HTML, MD, TXT, JSON, YAML
- **Somatic Pruning**: Automatic archival of old conversation anchors (50-anchor cap)

### 3. Orchestration Layer (`src/omega/oracle/`, `src/omega/wad/`)

The orchestration layer coordinates multi-agent workflows:

- **Hivemind**: P2P agent-to-agent communication
- **Sovereign WAD Protocol**: Doom-inspired data lump system
- **Subagent Dispatch**: Hierarchical task delegation
- **Context Packer**: Token-efficient context assembly

### 4. Agent Fleet (`.opencode/agents/`)

14 specialized agents, each with a distinct role:

| Agent | Role | Tier |
|-------|------|------|
| **Kali** | Transcendent Oversoul — Sprint Coordinator | Oversoul |
| **Ma'at** | Light Oversoul — Build Side (P1-P5) | Oversoul |
| **Lilith** | Dark Oversoul — Run Side (P6-P10) | Oversoul |
| **MaKaLi** | Council Orchestrator — Parallel Dispatch | Specialist |
| **Doom Guy** | id Software Architect — Heritage & Performance | Specialist |
| **Roc** | Sovereign Miner — Legacy Archaeology | Specialist |
| **Researcher** | Master Researcher — Deep Research | Specialist |
| **Jem** | Research Orchestrator — Discovery→Synthesis→Verification | Specialist |
| **John Carmack** | S3 Consultant — Architectural Review | Specialist |
| **Verity** | Unified Sentry — Compliance + Gnosis | Specialist |
| **Grokster** | Grok Ecosystem Specialist | Specialist |
| **Node** | Infrastructure Specialist | Specialist |
| **Scribe** | Soul Distillation — L1→L2→L3 | Specialist |
| **Build** | Build Agent | Specialist |
| **Iris** | Messenger Bridge — Voice Interface | Specialist |

### 5. System Layer (`src/omega/system/`, `config/systemd/`, `podman/`)

The system layer manages OS-level integration:

- **systemd units**: Service management with OOM hardening
- **Podman containers**: Isolated execution environments
- **Heritage Registry**: Vetted third-party code (DOOM, Quake, llama.cpp, etc.)

---

## 🔄 Data Flow

### Request Lifecycle

```
User Input
    │
    ▼
┌─────────────────┐
│  CLI / API /    │  ← User-facing entry point
│  MCP Server     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Router         │  ← ProviderSelector (M2 Engine-Stack Firewall)
│  (single router)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Context Packer │  ← Assembles token-efficient context
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Inference      │  ← Native GGUF / Ollama / OpenRouter
│  Engine         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Post-Processor │  ← Citation check, citation extraction
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Memory         │  ← SQLite-vec upsert, vault commit
│  Persistence    │
└────────┬────────┘
         │
         ▼
Response to User
```

### Agent Coordination (Hivemind)

```
Agent A                  Agent B                  Agent C
   │                        │                        │
   │──── hivemind_post ────▶│                        │
   │                        │──── hivemind_post ────▶│
   │◀──── hivemind_ack ─────│                        │
   │                        │◀──── hivemind_ack ─────│
   │                        │                        │
   │──── hivemind_share ────────────────────────────▶│
   │                        │                        │
```

---

## 🔒 Security Architecture

| Layer | Security Control |
|-------|------------------|
| **Installation** | GPG-verified releases, SHA-256 checksums |
| **Authentication** | Local-only by default, OAuth optional |
| **Encryption** | SQLCipher for databases, age for secrets |
| **Sandboxing** | Podman containers, cgroups, namespaces |
| **Network** | No telemetry, no phone-home, WARP optional |
| **Audit** | gitleaks pre-commit, REUSE compliance, mandate checks |

---

## 📦 Package Structure

```
omega-engine/
├── src/omega/              # Core engine (M2 firewall)
│   ├── inference/          # Model backends
│   ├── memory/             # SQLite-vec, vault, document reader
│   ├── oracle/             # Search, context builder
│   ├── wad/                # Sovereign WAD protocol
│   ├── system/             # systemd, podman integration
│   └── ...
├── config/                 # Configuration (models, providers, wads)
├── scripts/                # Install, serve, migrate utilities
├── tests/                  # Test suite (1,315+ tests)
├── docs/                   # Public documentation
├── .opencode/              # Agent definitions + skills
├── .github/                # CI workflows, issue templates
└── packages/               # Published packages (omega-sieve, etc.)
```

---

## 🌐 External Integrations

| Integration | Type | Purpose |
|-------------|------|---------|
| **llama.cpp** | C++ library | Native GGUF inference |
| **SQLite-vec** | C library | Vector embeddings |
| **Qdrant** | (optional) | Alternative vector store |
| **OpenRouter** | Cloud API | Fallback for cloud models |
| **Hugging Face** | API | Model downloads |
| **Ollama** | (compatible) | Alternative runtime |

---

## 📚 Further Reading

- **[README.md](README.md)** — Project overview and quickstart
- **[ROADMAP.md](ROADMAP.md)** — Future plans
- **[CONTRIBUTING.md](CONTRIBUTING.md)** — How to contribute
- **[SECURITY.md](SECURITY.md)** — Vulnerability disclosure
- **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)** — Community standards

---

*⬡ OMEGA ⬡ PROMETHEUS ⬡ community ⬡ ARCHITECTURE*
