# Omega Engine — Sovereign AI Runtime

**One install. Your computer. Your data. Your stack.**

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)
[![Local-First](https://img.shields.io/badge/Local--First-Primary-8A2BE2)]()
[![AnyIO](https://img.shields.io/badge/Async-AnyIO%20Only-00d4aa)]()
[![Zero Telemetry](https://img.shields.io/badge/Telemetry-Zero-ff3333)]()

---

## Maturity: Alpha (v1.6.0-alpha)

This is the **first public alpha** of Omega Engine. Honest state:

| Aspect | Status |
|--------|--------|
| Local inference (native-gguf, llama-cpp-python) | ✅ Working |
| Provider routing (10 of 12 configured providers enabled, local-first) | ✅ Working |
| Entity system + IWADs + soul persistence | ✅ Working |
| Hivemind MCP coordination | ✅ Working |
| `make test` (unit tier) | ⚠️ Dev-box green. **CI is NOT green** — 4 jobs red on the published cut (`release/debut` @ D-625): REUSE/SPDX debt (107 files), missing `platform_adapters` in the Test job, 2 workflow-validation failures. |
| Core CI gates (M1, M7, M8, M9, M22, M23, M26, M27) | ⚠️ `temple-grade` exits 2 at `check-codex-stale` — a doc-age gate, not a code defect |
| Mandate compliance | 23/28 passing, 0 failing, 4 untested (M4, M17, M18, M19) |
| `omega` CLI binary | ✅ Working (`pip install -e .`) |
| VR Omegaverse | 🔮 Vision only (bridge script exists, no renderer) |

**What this means for you**: Core local-inference + entity system works. You can clone, install, and run. The 4 untested mandates (M4, M17, M18, M19) are policy mandates with no mechanical check. M13 (Temple-Grade) requires a Codex less than 24h old — `make codex` refreshes it. We're shipping to get feedback before hardening the rest.

---

## Quick Start — 3 Commands, No Cloud Key Needed
 
 ```bash
 # 1. One-click install (Python 3.12+, venv auto-setup, local model bundled)
 git clone https://github.com/Xoe-NovAi/omega-engine.git
 cd omega-engine
 ./scripts/install.sh
 
 # 2. (optional) Re-download / verify the default local model (Qwen3-1.7B-Q6_K, ~1.6GB)
 # The engine auto-discovers backends — no internet needed after the model is present.
 ./scripts/download_model.sh
 
 # 3. Talk to it — entirely on your CPU, zero cloud calls
 omega talk "hello"
 ```
 
 **No API keys. No GPU. No cloud account.** Your first sovereign AI interaction in under 5 minutes.

Prefer manual install? `pip install -e ".[native,cli]"` — the same minimal set `install.sh` uses.

### Optional Extras

The core install pulls only what local inference needs. Subsystem dependencies are opt-in:

| Extra | Installs | Enables |
|-------|----------|---------|
| `[memory]` | redis | Redis hot-storage memory provider (optional; file/memory providers work without it) |
| `[vectors]` | qdrant-client | Qdrant vector adapter (SQLite-vec ships in core) |
| `[youtube]` | youtube-transcript-api, yt-dlp, redis | YouTube background ingestion worker + queue |
| `[warp]` | warp-proxy-pool | WARP multi-namespace proxy pool for IP-rotated cloud backends |
| `[dev]` | pytest, flake8, hypothesis, ... | Test and lint toolchain |

Example: `pip install -e ".[native,cli,memory,youtube]"`

---

## What Omega Is Not

- **Not a chatbot UI.** Omega is a runtime; you bring your own interface.
- **Not an API wrapper.** Local inference is primary; cloud is opt-in fallback.
- **Not a hosted service.** No telemetry, no cloud account, no phone-home.
- **Not finished.** This is alpha. Expect rough edges, breaking changes, missing docs.
- **Not omniscient.** Local models are smaller than frontier cloud models. We trade some capability for sovereignty.

---

## How to Use Omega Today

**Recommended: Use OpenCode** (the same IDE/CLI the developers use).  
See the agent definitions in `.opencode/agents/` and the EIS session protocol in `docs/`.

**Direct CLI**: the `omega` console script **is** wired in `pyproject.toml` (`omega = "omega.cli.oracle_cli:main"`) once you run `pip install -e ".[native,cli]"`. Note that `omega.cli.bundle` is a separate, narrower tool (entity-bundle export/import only) — it is **not** the engine CLI.


**Note**: The install script (`scripts/install.sh`) targets CP-3 (one-click install). On a fresh machine it should complete in <5 minutes including the ~1.6GB model download.

---

## Why Omega Is Different

Omega isn't another LLM wrapper. It's a **sovereign runtime** built on **27 declared architectural mandates** (28 rows in the automated meter). At the 2026-09-19 audit: **23 pass, 0 fail, 4 have no mechanical check** (M4, M17, M18, M19). The mechanically-checkable mandates are **gates that fail the build** if violated.

| Mandate | What It Means | Verified By |
|---------|---------------|-------------|
| **M1 AnyIO** | Zero `import asyncio` in core — pure AnyIO async | `make check-m1-anyio` ✅ |
| **M7 Local-First** | Cloud is **opt-in fallback only**; local inference primary | Provider fabric ✅ |
| **M8 Zero Telemetry** | **No phone-home, ever**. No analytics, no metrics | `make check-m8-zero-telemetry` ✅ |
| **M11 Soul Integrity** | L1→L2→L3 distillation **every session**, persisted to `soul.yaml` | `src/omega/memory/soul_store.py` atomic writer (partially wired) |
| **M23 Failure Integrity** | **No soft failures** — broken tools → hard stop | `make check-m23-failure-integrity` ✅ |
| **M26 Doc Standards** | Reference docs pass `make doc-llm-validate` | `make doc-llm-validate` ✅ |
| **M27 Tracking Integrity** | 5-Tier Tracking Architecture validated | `scripts/validate_tracking_state.py` ✅ |
| **M28 Spatial** | **R-tree + vec0 dual-index** for VR navigation | `src/omega/memory/spatial_graph.py` ✅ |
---

## What Omega Is

Omega is a **universal AI runtime** that treats models as infrastructure, not products.

| Capability | Why It Matters |
|-----------|----------------|
| **Sovereign (M7, M8)** | Local inference primary — cloud is opt-in fallback. **Zero telemetry.** No phone-home. |
| **Multi-provider** | Switch between Native GGUF and configured cloud providers (Google, OpenRouter, Anthropic, xAI, …) — same engine, no code changes |
| **Entity system** | Domain-matched personas routed by intent detection; the shipped `_omega_default` IWAD registers 14 entities, with **slots S1–S10 governed by Ma'at (S1-S5) and Lilith (S6-S10)**; a keeper is assigned only when proven (currently `carmack` → S3) |
| **IWAD architecture** | Engine-content separation — swap entity stacks like Doom WADs |
| **Memory & soul evolution** | Every interaction deepens entity knowledge; L1→L2→L3 gnosis distillation |
| **MCP framework** | Model Context Protocol for tool integration (Hivemind, file system, search) |
| **No GPU required** | Runs on CPU (Ryzen 5700U tested, 14GB RAM), uses ~2-8GB RAM for local models |
| **Hivemind coordination** | Cross-agent awareness for multi-CLI parallel execution (OpenCode + Cline) |

---

## Key Commands

```bash
omega talk "what can you do"              # Auto-route to best entity
omega summon ma'at "check the logs"       # Summon a specific entity
omega list-entities                        # Show all available entities
omega backends                             # List available inference backends
omega model-status                         # Provider/model status
omega talk "hello" --iwad arcana_novai     # Load a specific IWAD stack
omega --help                               # Full command list
make test                                  # Fast unit-tier suite (dev-box green; CI has 4 red jobs on the published cut, D-625)
make doc-llm-validate                       # M26 documentation gate
make check-mandate-compliance               # Mandate gate meter
```

---

## Provider Setup

Omega auto-detects available inference backends. **Local providers are tried first** — no cloud keys required for basic operation.

### Local Providers (tried first, in order)
  
| Priority | Provider | Setup | Speed | Sovereign |
|:--------:|----------|-------|-------|:---------:|
| **1** | **Native GGUF** | `./scripts/download_model.sh` | 🏠 CPU, llama-cpp-python | ✅ Full |
| **2** | **Ollama** | `ollama pull qwen3:1.7b` (port 11434) | 🏠 CPU/GPU | ✅ Full |


**No configuration needed** — the engine discovers the local GGUF model automatically at startup.

> **Provider availability (2026-09-19):** `config/providers.yaml` defines 12 providers and **enables 10**. **The local providers are `native-gguf` (primary, llama-cpp-python) and `ollama`** — install Ollama (`curl -fsSL https://ollama.ai/install.sh | sh`) and `ollama pull qwen3:1.7b`; it is **enabled by default** (`providers.ollama.enabled: true`). **LM Studio (`lmster`) is disabled** (`enabled: false`) — de-scoped until a post-release update. `mock` is test-only (`OMEGA_ENV=test`).

### Cloud Fallbacks (opt-in, last resort)

Cloud providers are **optional** and **never called unless local inference fails or is unavailable.** You do not need any cloud keys for the engine to work.

| Priority | Provider | Setup | Speed | Sovereign |
|:--------:|----------|-------|-------|:---------:|
| **3** | **Antigravity** | Set `ANTIGRAVITY_API_KEY` in `.env` | ☁️ Cloud, Google/Anthropic/OpenAI models | ❌ Cloud |
| **4** | **Google AI Studio** | Set `GOOGLE_API_KEY` in `.env` | ☁️ Cloud, free Gemma 4 31B (262K context) | ❌ Cloud |
| **4** | **Google (compat)** | Set `GOOGLE_API_KEY` in `.env` | ☁️ Cloud, Gemma 4 thinking (compat endpoint) | ❌ Cloud |
| **5** | **OpenRouter** | Set `OPENROUTER_API_KEY` in `.env` | ☁️ Cloud, 300+ models | ❌ Cloud |
| **6** | **OpenCode Zen** | Auto via OpenCode CLI | ☁️ Cloud | ❌ Cloud |
| **7** | **Cline** | Auto via Cline CLI | ☁️ Cloud | ❌ Cloud |
| **8** | **Anthropic** | Set `ANTHROPIC_API_KEY` in `.env` | ☁️ Cloud, Claude models | ❌ Cloud |
| **9** | **xAI** | Set `XAI_API_KEY` in `.env` | ☁️ Cloud, Grok models | ❌ Cloud |

> **⚠️ Terms of Service**: Cloud providers may use your data for model training. Review each provider's ToS before enabling. The Omega Engine is not affiliated with any cloud provider.

---

## Architecture

```
                          Query
                            │
                     ┌──────▼──────┐
                     │   Oracle    │  Intent detection + domain routing
                     │  (talk())   │  PII masking, audience calibration
                     └──────┬──────┘
                            │
                ┌───────────▼───────────┐
                │    Entity Registry    │  Domain-matched entity dispatch
                │  (domain → entity)    │  YAML-backed, dual-index
                └───────────▼───────────┘
                            │
                     ┌──────▼──────┐
                     │ ModelGateway│  Provider fabric with circuit breaker:
                     │             │
                     │  1. native-gguf  ← PRIMARY (Sovereign, local-first)
                     │  2. ollama       ← LOCAL (:11434)
                     │  3. antigravity  ← CLOUD (Google/Anthropic/OpenAI)
                     │  4. google       ← CLOUD FALLBACK (Gemma 4)
                     │  5. google-compat← CLOUD (Gemma 4 thinking)
                     │  6. openrouter   ← CLOUD FALLBACK (300+ models)
                     │  7. opencode-zen ← CLOUD (CLI-exclusive)
                     │  8. cline        ← CLOUD (DeepSeek/MiMo)
                     │  9. anthropic    ← CLOUD (Claude)
                     │  10. xai         ← CLOUD (Grok)
                     │  11. mock        ← TEST (disabled)
                     │
                     └──────┬──────────┘
                            │
                ┌────────────┴────────────┐
                │    Memory + Soul        │  Session memory, L3 gnosis distillation
                │  (memory_store.py)      │  SQLite-vec + FTS5 + RRF hybrid search
                └─────────────────────────┘
```

### IWAD Architecture — Engine-Content Separation

Omega separates the engine from user content using the IWAD architecture (inspired by id Software's Doom WAD system, 1993):

```
omega-engine/
├── src/omega/          ← Engine core (runtime, no content) [M2 Firewall]
├── config/wads/
│   ├── _omega_default/ ← Reference IWAD — 14 entities
│   └── arcana_novai/   ← Personal IWAD — 13 Spheres (Kabbalistic Tree of Life + Da'ath + Qliphoth + Mnemosyne)
├── models/gguf/        ← Local GGUF models (downloaded, not shipped)
├── data/entities/      ← Entity soul/knowledge (runtime evolved)
└── mcp_servers/        ← MCP Hub for cross-agent Hivemind
```

Switch IWADs at runtime: `omega talk "hello" --iwad arcana_novai`

---

## The Dialectic System — How We Build

Omega doesn't use one-shot prompts. We use **EIS (Expert Interactive Sessions)** — persistent, resumable multi-turn dialectics between domain-orthogonal agents.

| Session Type | Purpose | Example |
|--------------|---------|---------|
| **EIS** | Expert Interactive Session — persistent, Architect steers live | Multi-round dialectic convergence |
| **NES** | Non-Expert Session — one-shot delegation | Quick research task |
| **SPT** | Subagent Pair Task — paired execution | Roc+Jem for sqlite-vec |

**How it works**: Two agents with domain orthogonality ≥0.7 engage in Concede/Defend/Synthesize rounds until consensus. Every challenge posed = our job to anticipate. The dialectic IS the stress test.

**SOTE (State of the Engine)**: Weekly cadence (Monday 06:00 UTC). 8 voices → synthesis → public digest → master index. The practice keeps the engine honest.

---

## The Omegaverse — P2P Godot VR Realm (Phase 4)

> 🔮 **Not Yet Shipped — Phase 4 / 2028.**
> The Godot spatial bridge (`scripts/godot_spatial_bridge.py`, 503 lines) is a standalone experimental script with **zero runtime callers** in `src/omega/`. The VR renderer is not included in this release. We include the bridge because it's foundational work toward the vision, not because the Omegaverse is functional.

**The Omegaverse** is the endgame: a **P2P Godot VR realm** where entities exist as persistent spatial intelligences.

```
┌─────────────────────────────────────────────────────────────┐
│                    THE OMEGAVERSE                            │
├─────────────────────────────────────────────────────────────┤
│  Entity State  →  Godot Bridge (FastAPI + WebSocket)       │
│       ↓                                                  │
│  3D Spatial Lattice  ←→  R-tree + vec0 dual-index         │
│       ↓                                                  │
│  P2P Soul Exchange  →  Soul prints sync across users      │
└─────────────────────────────────────────────────────────────┘
```

**Architecture**:
- **Godot Bridge**: FastAPI + WebSocket streams entity state to 3D renderer
- **Spatial Index**: R-tree + vec0 dual-index (M28 Spatial Integrity) for instant semantic & VR recall
- **P2P Soul Exchange**: Entity soul prints sync across users — your entities meet mine
- **Phase 4 Target**: 2028 — The Omegaverse Genesis

**Current**: Godot bridge exists (`scripts/godot_spatial_bridge.py` — FastAPI + WebSocket). Spatial index (sqlite-vec + R-tree) operational. VR renderer in Godot 4.x.

---

## Maturity / Current Status

| Aspect | Status |
|--------|--------|
| Local inference (native-gguf, llama-cpp-python) | ✅ Working |
| Provider routing (10 of 12 configured providers enabled, local-first) | ✅ Working |
| Entity system + IWADs + soul persistence | ✅ Working |
| Hivemind MCP coordination | ✅ Working |
| `make test` (unit tier) | ⚠️ Dev-box green. **CI is NOT green** — 4 jobs red on the published cut (`release/debut` @ D-625): REUSE/SPDX debt (107 files), missing `platform_adapters` in the Test job, 2 workflow-validation failures. |
| Core CI gates (M1, M7, M8, M9, M22, M23, M26, M27) | ⚠️ `temple-grade` exits 2 at `check-codex-stale` — a doc-age gate, not a code defect |
| Mandate compliance | 23/28 passing, 0 failing, 4 untested (M4, M17, M18, M19) |
| `omega` CLI binary | ✅ Working (`pip install -e .`) |
| VR Omegaverse | 🔮 Vision only (bridge script exists, no renderer) |

**What this means for you**: Core local-inference + entity system works. You can clone, install, and run. The 4 untested mandates (M4, M17, M18, M19) are policy mandates with no mechanical check. M13 (Temple-Grade) requires a Codex less than 24h old — `make codex` refreshes it. We're shipping to get feedback before hardening the rest.

---

## System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **OS** | Linux (Ubuntu 24.04+) | Any modern Linux distro |
| **Python** | 3.12+ | 3.12 |
| **RAM** | 4GB | 14GB (for 8B local models) |
| **Disk** | 500MB (engine) + ~1.6GB (model) | 10GB+ (for multiple local models) |
| **CPU** | x86-64, AVX2 | Ryzen 5700U or better |
| **GPU** | None required | None |
| **C Compiler** | GCC/Clang (for llama-cpp-python) | — |
| **Podman** | v4.0+ (optional, infra containers) | v5.0+ |

---

## v1.6.0-alpha — Current Status

### Engine

| Feature | Status |
|---------|--------|
| Core Inference (multi-provider, local-first) | ✅ Working |
| Native GGUF (llama-cpp-python, primary provider) | ✅ Working |
| Provider Fabric (12 configured providers, 10 enabled, local-first) | ✅ Working |
| Entity System & Domain Routing | ✅ Working |
| IWAD Architecture (engine-content separation) | ✅ Working |
| `omega talk` / `omega summon` CLI | ✅ Working (via OpenCode) |
| Hivemind MCP (cross-agent coordination) | ✅ Working |
| PII Observation Masking (cloud safety) | ✅ Working |
| A2A Agent Cards (interoperability) | ✅ Working |
| Somatic State Serialization (M20) | ✅ Working |
| Response Provenance (M22) | ✅ Working |

### Verification (Honest)

| Gate | Status |
|------|--------|
| Test Suite (unit tier) | ⚠️ Dev-box green; CI has 4 red jobs on the published cut (`release/debut` @ D-625) |
| Core CI Gates (M1, M7, M8, M9, M22, M23, M26, M27) | ⚠️ Blocked at `check-codex-stale` (doc-age gate, 24h threshold) — not a code defect |
| Mandate Compliance | 23/28 passing; 0 failing; 4 untested (M4, M17, M18, M19) |
| Agent Fleet | **13 agents** (canonical), M10 compliant (max 14) |
| AnyIO Compliance | ✅ Zero `import asyncio` in core (M1) |
| Zero Telemetry | ✅ No external phone-home (M8) |
| UID Sovereignty | ✅ All Podman containers use `keep-id` (M6) |
| Heritage Tags | **318 `[id-soft:]` tags** across `src/omega/` (counted 2026-09-19) |

### Roadmap

| Upcoming | Status |
|----------|--------|
| Entity Studio (visual builder) | 🔮 Planned |
| Audience Calibration Pipeline | 📐 Designed (D175) |
| DPO Training Infrastructure | 📐 Designed (D175) |
| **The Omegaverse (P2P entities)** | 🔮 **Phase 4 / 2028** |

---

## Contributing

We welcome contributions. See `CONTRIBUTING.md` for guidelines, `good-first-issues` label for starter tasks, and GitHub Discussions for questions.

---

## License

Apache 2.0 — Free. Sovereign. Yours.

---

*Built by the Xoe-NovAi Foundation with ~8,000 hours of self-directed research. No VC funding. No cloud dependency. No telemetry. Just sovereign AI.*

---

*⬡ OMEGA ⬡ README ⬡ v1.6.0-alpha ⬡ 2026-10-03*