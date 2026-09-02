# 🔱 Omega Engine — Sovereign AI Runtime

**Prometheus' Fire** — A universal, community-owned runtime for sovereign AI. One install. Your computer. Your data. Your stack.

[![Tests](https://github.com/Xoe-NovAi/omega-engine/actions/workflows/test.yml/badge.svg)](https://github.com/Xoe-NovAi/omega-engine/actions/workflows/test.yml)
[![Sovereignty](https://img.shields.io/badge/Sovereignty-Active-brightgreen)]()
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)
[![Local-First](https://img.shields.io/badge/Local--First-Primary-8A2BE2)]()
[![Omegaverse](https://img.shields.io/badge/Omegaverse-P2P%20Godot%20VR-ff6b35)]()
[![AnyIO](https://img.shields.io/badge/Async-AnyIO%20Only-00d4aa)]()
[![Zero Telemetry](https://img.shields.io/badge/Telemetry-Zero-ff3333)]()

---

## ⚠️ Maturity: Alpha

This is the **first public alpha** of Omega Engine. Honest state:

| Aspect | Status |
|--------|--------|
| Local inference (native-gguf, LM Studio) | ✅ Working |
| Provider routing (10 providers, local-first) | ✅ Working |
| Entity system + IWADs + soul persistence | ✅ Working |
| Hivemind MCP coordination | ✅ Working |
| `omega` CLI binary | ❌ Not built (use OpenCode or `python -m omega.cli.bundle`) |
| `make test` | ❌ Broken (12 files import removed module) |
| CI gates (Temple-Grade) | ❌ Cascading fail (M23 root cause) |
| Mandate compliance meter | ⚠️ 64.3% (18/28; 5 failing, 4 untested) |
| Secret scan | ❌ Fails (committed OAuth secret, queued for filter-repo) |
| VR Omegaverse | 🔮 Vision only (bridge script exists, no renderer) |

**What this means for you**: Core local-inference + entity system works. You can clone, install, and run. The CI badges, mandate compliance, and secret-scan gates are not yet green. We're shipping alpha to get feedback before hardening the rest.

---

## Quick Start — 3 Commands, No Cloud Key Needed
 
 ```bash
 # 1. One-click install (Python 3.12+, venv auto-setup, local model bundled)
 git clone https://github.com/Xoe-NovAi/omega-engine.git
 cd omega-engine
 ./scripts/install.sh
 
 # 2. (optional) Re-download / verify the default local model (LFM2.5-2.6B Q4_K_M, ~1.67GB)
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

**Direct CLI**: The `omega` CLI bundle lives in `src/omega/cli/`, but the console-script entry point is not yet wired in `pyproject.toml`. You can invoke modules directly:

```bash
python -m omega.cli.bundle talk "hello"
```

**Note**: The install script (`scripts/install.sh`) targets CP-3 (one-click install). On a fresh machine it should complete in <5 minutes including the ~1.6GB model download.

---

## Why Omega Is Different

Omega isn't another LLM wrapper. It's a **sovereign runtime** built on **27 declared architectural mandates** — 18 currently pass the automated compliance meter, 5 failing, 4 untested. The mandates are **gates that fail the build** if violated.

| Mandate | What It Means | Verified By |
|---------|---------------|-------------|
| **M1 AnyIO** | Zero `import asyncio` in core — pure AnyIO async | `make check-m1-anyio` ✅ |
| **M7 Local-First** | Cloud is **opt-in fallback only**; local inference primary | Provider fabric ✅ |
| **M8 Zero Telemetry** | **No phone-home, ever**. No analytics, no metrics | `make check-m8-zero-telemetry` ✅ |
| **M11 Soul Integrity** | L1→L2→L3 distillation **every session**, persisted to `soul.yaml` | `src/omega/memory/soul_store.py` atomic writer (partially wired) |
| **M23 Failure Integrity** | **No soft failures** — broken tools → hard stop | `make check-m23-failure-integrity` ⚠️ (failing today) |
| **M28 Spatial** | **R-tree + vec0 dual-index** for VR navigation | `src/omega/memory/spatial_graph.py` ✅ |

> **The Cathedral Metaphor**: We build a cathedral, not a bazaar. Every stone (mandate) is placed with intention. The architecture is the theology.

---

## What Omega Is

Omega is a **universal AI runtime** that treats models as infrastructure, not products.

| Capability | Why It Matters |
|-----------|----------------|
| **Sovereign (M7, M8)** | Local inference primary — cloud is opt-in fallback. **Zero telemetry.** No phone-home. |
| **Multi-provider** | Switch between Native GGUF, LM Studio, Ollama, and cloud providers — same engine, no code changes |
| **Entity system** | Domain-matched personas (13 canonical agents) routed by intent detection; 24 default entities in the shipped `_omega_default` IWAD with 10 Node Keepers at N1-N10 slots |
| **IWAD architecture** | Engine-content separation — swap entity stacks like Doom WADs |
| **Memory & soul evolution** | Every interaction deepens entity knowledge; L1→L2→L3 gnosis distillation |
| **MCP framework** | Model Context Protocol for tool integration (Hivemind, file system, search) |
| **No GPU required** | Runs on CPU (Ryzen 5700U tested, 14GB RAM), uses ~2-8GB RAM for local models |
| **Hivemind coordination** | Cross-agent awareness for multi-CLI parallel execution (OpenCode + Cline) |

---

## Key Commands

```bash
omega talk "what can you do"             # Auto-route to best entity
omega summon SysAdmin "check the logs"   # Summon a specific entity
omega list-entities                      # Show all available entities
omega backends                           # List available inference backends
omega health                             # Show provider status and latency
omega talk "hello" --iwad arcana_novai   # Load a specific IWAD stack
omega version                            # Show version
make test                                # Run the fast unit-tier test suite (currently broken)
make temple-grade                        # Verify Temple-Grade gates (6 checks; currently fails on M23 cascade)
make menu                                # Full command menu
```

---

## Provider Setup

Omega auto-detects available inference backends. **Local providers are tried first** — no cloud keys required for basic operation.

### Local Providers (tried first, in order)
  
| Priority | Provider | Setup | Speed | Sovereign |
|:--------:|----------|-------|-------|:---------:|
| **1** | **Native GGUF** | `./scripts/download_model.sh` | 🏠 CPU, llama-cpp-python | ✅ Full |
| **2** | **LM Studio** | `lms server start` (port 1234) | 🏠 CPU/GPU | ✅ Full |
| **3** | **Ollama** | `ollama pull qwen3:1.7b` (port 11434) | 🏠 CPU/GPU | ✅ Full |
| **4** | **Mock** | Automatic in `OMEGA_ENV=test` | Instant, deterministic | ✅ Test |

**No configuration needed** — the engine discovers running local backends automatically at startup.

### Cloud Fallbacks (opt-in, last resort)

Cloud providers are **optional** and **never called unless local inference fails or is unavailable.** You do not need any cloud keys for the engine to work.

| Priority | Provider | Setup | Speed | Sovereign |
|:--------:|----------|-------|-------|:---------:|
| **5** | **Google AI Studio** | Set `GOOGLE_API_KEY` in `.env` | ☁️ Cloud, free Gemma 4 31B (262K context) | ❌ Cloud |
| **6** | **OpenRouter** | Set `OPENROUTER_API_KEY` in `.env` | ☁️ Cloud, 300+ models | ❌ Cloud |
| **7** | **OpenCode Zen** | Auto via OpenCode CLI | ☁️ Cloud | ❌ Cloud |
| **8** | **Copilot** | Auto via GitHub CLI | ☁️ Cloud | ❌ Cloud |
| **9** | **Antigravity** | Auto via Cline CLI | ☁️ Cloud | ❌ Cloud |

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
                     │  2. lmster       ← LOCAL (LM Studio :1234)
                     │  3. ollama       ← LOCAL (:11434)
                     │  4. google       ← CLOUD FALLBACK (Gemma 4)
                     │  5. openrouter   ← CLOUD FALLBACK (300+ models)
                     │  ...            (opencode, copilot, mock)
                     │
                     └──────┬──────────┘
                            │
               ┌────────────┴────────────┐
               │    Memory + Soul        │  Session memory, L3 gnosis distillation
               │  (memory_store.py)      │  Qdrant vectors, FTS5 search
               └─────────────────────────┘
```

### IWAD Architecture — Engine-Content Separation

Omega separates the engine from user content using the IWAD architecture (inspired by id Software's Doom WAD system, 1993):

```
omega-engine/
├── src/omega/          ← Engine core (runtime, no content) [M2 Firewall]
├── config/wads/
│   ├── _omega_default/ ← Reference IWAD — 24 entities, 10 Node Keepers at N1-N10
│   └── arcana_novai/   ← Personal IWAD — 13 Spheres (Kabbalistic Tree of Life + Da'ath + Qliphoth + Mnemosyne)
├── models/gguf/        ← Local GGUF models (downloaded, not shipped)
├── data/entities/      ← Entity soul/knowledge (runtime evolved)
└── mcp_servers/        ← MCP Hub for cross-agent Hivemind
```

Switch IWADs at runtime: `omega talk --iwad arcana_novai "hello"`

---

## The Dialectic System — How We Build

Omega doesn't use one-shot prompts. We use **EIS (Expert Interactive Sessions)** — persistent, resumable multi-turn dialectics between domain-orthogonal agents.

| Session Type | Purpose | Example |
|--------------|---------|---------|
| **EIS** | Expert Interactive Session — persistent, Architect steers live | Kali↔Roc (5 rounds), Kali+Lilith+Ma'at (6 rounds nested) |
| **NES** | Non-Expert Session — one-shot delegation | Quick research task |
| **SPT** | Subagent Pair Task — paired execution | Roc+Jem for sqlite-vec |

**How it works**: Two agents with domain orthogonality ≥0.7 engage in Concede/Defend/Synthesize rounds until consensus. Every challenge posed = our job to anticipate. The dialectic IS the stress test.

**SOTE (State of the Engine)**: Weekly cadence (Monday 06:00 UTC). 8 voices → synthesis → public digest → master index. The practice keeps the engine honest. This is real, not theatre: see `data/coordination/ACTIVE_SPRINT.json` for SOTE v1.0.3 records and the nested dialectic rounds (6 rounds, consensus achieved).

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
| Local inference (native-gguf, LM Studio) | ✅ Working |
| Provider routing (10 providers, local-first) | ✅ Working |
| Entity system + IWADs + soul persistence | ✅ Working |
| Hivemind MCP coordination | ✅ Working |
| `omega` CLI binary | ❌ Not built (use OpenCode or `python -m omega.cli.bundle`) |
| `make test` | ❌ Broken (12 files import removed module) |
| CI gates (Temple-Grade) | ❌ Cascading fail (M23 root cause) |
| Mandate compliance meter | ⚠️ 64.3% (18/28; 5 failing, 4 untested) |
| Secret scan | ❌ Fails (committed OAuth secret, queued for filter-repo) |
| VR Omegaverse | 🔮 Vision only (bridge script exists, no renderer) |

**What this means for you**: Core local-inference + entity system works. You can clone, install, and run. The CI badges, mandate compliance, and secret-scan gates are not yet green. We're shipping alpha to get feedback before hardening the rest.

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
| Provider Fabric (10 active providers, local-first) | ✅ Working |
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
| Test Suite | ❌ Broken — 12 files import `omega.library` (removed in D-565, not restored) |
| Temple-Grade | ❌ Fails — 6 checks run; M23 cascade failure |
| Mandate Compliance | ⚠️ 64.3% (18/28; 5 failing: M13, M16, M23, M27, +1; 4 untested) |
| Agent Fleet | **13 agents** (canonical), M10 compliant (≤14) |
| AnyIO Compliance | ✅ Zero `import asyncio` in core (M1) |
| Zero Telemetry | ✅ No external phone-home (M8) |
| UID Sovereignty | ✅ All Podman containers use `keep-id` (M6) |
| Heritage Tags | **216 `[id-soft:]` tags** across `src/omega/` |

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