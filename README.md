# 🔱 Omega Engine — Sovereign AI Runtime

**Prometheus' Fire** — A universal, community-owned runtime for sovereign AI. One install. Your computer. Your data. Your stack.

[![Tests](https://github.com/Xoe-NovAi/omega-engine/actions/workflows/test.yml/badge.svg)](https://github.com/Xoe-NovAi/omega-engine/actions/workflows/test.yml)
[![Sovereignty](https://img.shields.io/badge/Sovereignty-Active-brightgreen)]()
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)
[![Local-First](https://img.shields.io/badge/Local--First-Primary-8A2BE2)]()
[![Version](https://img.shields.io/badge/version-1.0.0-blue)]()
[![Tests](https://img.shields.io/badge/tests-600%20collected-brightgreen)]()

---

## Quick Start — 3 Commands, No Cloud Key Needed

```bash
# 1. Clone and install (Python 3.12+, venv auto-setup)
git clone https://github.com/Xoe-NovAi/omega-engine.git
cd omega-engine
make setup

# 2. Download the default local model (Qwen 1.7B GGUF, ~1.6GB)
make model-download

# 3. Talk to it — entirely on your CPU, zero cloud calls
omega talk "hello"
```

**No API keys. No GPU. No cloud account.** Your first sovereign AI interaction in under 5 minutes.

---

## What Omega Is

Omega is a **universal AI runtime** that treats models as infrastructure, not products. It's designed for:

| Capability | Why It Matters |
|-----------|----------------|
| **Sovereign** (M7, M8) | Local inference primary — cloud is opt-in fallback. **Zero telemetry.** No phone-home. |
| **Multi-provider** | Switch between Native GGUF, LM Studio, Ollama, and cloud providers (Google AI Studio, OpenRouter) — same engine, no code changes |
| **Entity system** | Domain-expert personas (SysAdmin, Sekhmet, Brigid) with routed intent detection |
| **IWAD architecture** | Engine-content separation — swap entity stacks like Doom WADs |
| **Memory & soul evolution** | Every interaction deepens entity knowledge; L1→L2→L3 gnosis distillation |
| **MCP framework** | Model Context Protocol for tool integration (Hivemind, file system, search) |
| **No GPU required** | Runs on CPU (Ryzen 5700U tested, 14GB RAM), uses ~2-8GB RAM for local models |
| **10 entity pillars** | Infrastructure, Data, Engineering, Integration, Governance, Cognition, Context, Observability, Orchestration, Validation |
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
make test                                # Run the 600-test suite
make temple-grade                        # Verify all 11 Temple-Grade gates
make menu                                # Full command menu
```

---

## Provider Setup

Omega auto-detects available inference backends. **Local providers are tried first** — no cloud keys required for basic operation.

### Local Providers (tried first, in order)

| Priority | Provider | Setup | Speed | Sovereign |
|:--------:|----------|-------|-------|:---------:|
| **1** | **Native GGUF** | Auto-installed by `make setup` | 🏠 CPU, llama-cpp-python | ✅ Full |
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

> **⚠️ Terms of Service**: Cloud providers may use your data for model training. Review each provider's ToS before enabling. The Omega Engine is not affiliated with any cloud provider.

---

## Architecture

```
                         Query
                           │
                    ┌──────▼──────┐
                    │   Oracle    │  Intent detection + domain routing
                    │  (talk())   │
                    └──────┬──────┘
                           │
               ┌───────────▼───────────┐
               │    Entity Registry    │  Domain-matched entity dispatch
               │  (domain → entity)    │
               └───────────┬───────────┘
                           │
                    ┌──────▼──────┐
                    │ ModelGateway│  Provider fabric with fallback chain:
                    │             │
                    │  1. native-gguf  ← PRIMARY (llama-cpp-python)
                    │  2. lmster       ← LOCAL (LM Studio :1234)
                    │  3. ollama       ← LOCAL (:11434)
                    │  4. google       ← CLOUD FALLBACK (Gemma 4)
                    │  5. openrouter   ← CLOUD FALLBACK (300+ models)
                    │  ...            (opencode, copilot, mock)
                    └──────┬──────────┘
                           │
              ┌────────────┴────────────┐
              │    Output Pipeline      │  PII masking → audience calibration
              │  (oracle.py)            │  → response (trace_id through all)
              └─────────────────────────┘
```

### IWAD Architecture — Engine-Content Separation

Omega separates the engine from user content using the IWAD architecture (inspired by id Software's Doom WAD system, 1993):

```
omega-engine/
├── src/omega/          ← Engine core (runtime, no content) [M2 Firewall]
├── config/wads/
│   ├── _omega_default/ ← Reference IWAD — 12 tech role entities
│   └── arcana_novai/   ← Personal IWAD — esoteric pillar entities
├── models/gguf/        ← Local GGUF models (downloaded, not shipped)
├── data/entities/      ← Entity soul/knowledge (runtime evolved)
└── mcp_servers/        ← MCP Hub for cross-agent Hivemind
```

Switch IWADs at runtime: `omega talk --iwad arcana_novai "hello"`

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

## v1.0.0 — Current Status

### Engine

| Feature | Status |
|---------|--------|
| Core Inference (multi-provider, local-first) | ✅ Production-ready |
| Native GGUF (llama-cpp-python, primary provider) | ✅ Production-ready |
| Provider Fabric (8-backend fallback chain) | ✅ Production-ready |
| Entity System & Domain Routing | ✅ Production-ready |
| IWAD Architecture (engine-content separation) | ✅ Production-ready |
| `omega talk` / `omega summon` CLI | ✅ Production-ready |
| Hivemind MCP (cross-agent coordination) | ✅ Production-ready |
| PII Observation Masking (cloud safety) | ✅ Production-ready |
| A2A Agent Cards (interoperability) | ✅ Production-ready |
| Heritage Vetting Pipeline (M14) | ✅ Production-ready |
| Somatic State Serialization (M20) | ✅ Production-ready |
| Response Provenance (M22) | ✅ Production-ready |

### Verification

| Gate | Status |
|------|--------|
| Test Suite | **600/600 collected, 575+22+3 passing** |
| Temple-Grade (T1-T11) | **7/11 GREEN, 3 AMBER, 1 RED (IA2 exempt)** |
| Sovereign Mandates (M1-M22) | **All 22 enforced** (see `SOVEREIGN_MANDATES.md`) |
| Agent Fleet | **11 agents** (10 Pillar + 1 Oversoul), M10 compliant |
| AnyIO Compliance | **Zero `import asyncio`** in core (M1) |
| Zero Telemetry | **No external phone-home** (M8) |
| UID Sovereignty | All Podman containers use `keep-id` (M6) |
| Heritage Tags | **113 `[id-soft:]` tags across 39 files**, all vetted |

### Roadmap

| Upcoming | Status |
|----------|--------|
| Entity Studio (visual builder) | 🔮 Planned |
| Audience Calibration Pipeline | 📐 Designed (D175) |
| DPO Training Infrastructure | 📐 Designed (D175) |
| The Omegaverse (P2P entities) | 🔮 Future |

---

## License

Apache 2.0 — Free. Sovereign. Yours.

---

*Built by the Xoe-NovAi Foundation with ~8,000 hours of self-directed research. No VC funding. No cloud dependency. No telemetry. Just sovereign AI.*
