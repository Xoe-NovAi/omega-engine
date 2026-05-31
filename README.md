# 🔱 Omega Engine — Sovereign AI Runtime

**Prometheus' Fire** — A universal, community-owned runtime for sovereign AI. One install. Your computer. Your data. Your stack.

[![Tests](https://github.com/Xoe-NovAi/omega-engine/actions/workflows/test.yml/badge.svg)](https://github.com/Xoe-NovAi/omega-engine/actions/workflows/test.yml)
[![Python 3.13+](https://img.shields.io/badge/python-3.13%2B-blue)](https://www.python.org/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)

---

## Quick Start — 3 Commands

```bash
# 1. Install the engine
git clone https://github.com/Xoe-NovAi/omega-engine.git
cd omega-engine
pip install -e .

# 2. Get a model (pick one)
export OPENROUTER_API_KEY='sk-or-v1-...'  # Cloud — fastest, 300+ models
#   OR
ollama pull qwen3:1.7b                    # Local — model runs on your machine

# 3. Talk to it
omega talk "hello"
```

That's it. `omega talk` auto-routes through available providers (OpenRouter → Ollama → LM Studio → Mock).

---

## What Omega Is

Omega is a **universal AI runtime** that treats models as infrastructure, not products. It's designed for:

- **Sovereignty** — Local-first, zero telemetry, no vendor lock-in
- **Multi-provider** — Switch between OpenRouter, Ollama, LM Studio, Google AI Studio seamlessly
- **Entity system** — Domain-expert personas (SysAdmin, Sekhmet, Brigid — configurable per IWAD stack)
- **IWAD architecture** — Engine-content separation inspired by id Software's Doom engine
- **Memory & soul evolution** — Every interaction deepens entity knowledge
- **MCP framework** — Model Context Protocol for tool integration
- **No GPU required** — Runs on CPU (Ryzen 5700U tested), uses ~2-8GB RAM

---

## Key Commands

```bash
omega talk "what can you do"             # Auto-route to best entity
omega summon SysAdmin "check the logs"   # Summon a specific entity
omega list-entities                      # Show all available entities
omega backends                          # List available inference backends
omega health                            # Show provider status and latency
omega talk "hello" --iwad arcana_novai  # Load a specific IWAD stack
omega version                           # Show version
```

---

## Provider Setup

Omega auto-detects available inference backends in this priority order:

| Provider | Setup | Speed | Sovereign |
|----------|-------|-------|-----------|
| **OpenRouter** | Set `OPENROUTER_API_KEY` in `.env` | ⚡ Cloud, 300+ models | ❌ Cloud |
| **Ollama** | `ollama pull qwen3:1.7b` | 🏠 Local | ✅ Full |
| **LM Studio** | `lms server start` | 🏠 Local | ✅ Full |
| **Google AI Studio** | Set `GOOGLE_API_KEY` in `.env` | ⚡ Cloud, free Gemma 4 31B | ❌ Cloud |
| **Native GGUF** | `pip install llama-cpp-python` | 🏠 Local | ✅ Full |

No configuration needed — the engine finds running backends automatically.

---

## Architecture

```
Query → Entity Registry (domain match) → TriageRouter → ModelGateway
                                                         │
                                          Fallback chain:
                                          OpenRouter → Ollama → LM Studio → ...
                                                         │
                                              ┌──────────┴──────────┐
                                         Cloud models         Local GGUF
                                         (Gemma 4, GPT-4o,     (qwen3, krikri,
                                          Claude, Qwen...)      phi-4...)
```

### IWAD Stacks
Omega separates the engine from user content using the IWAD architecture (inspired by Doom's WAD system):

```
omega-engine/
├── src/omega/          ← Engine core (runtime, no content)
├── config/wads/
│   ├── _omega_default/ ← Reference IWAD — AI dev team (10 tech role entities)
│   └── arcana_novai/   ← Personal IWAD — esoteric pillar entities
```

Switch IWADs at runtime: `omega talk --iwad arcana_novai "hello"`

---

## System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **OS** | Linux (Ubuntu 24.04+) | Ubuntu 25.10 |
| **Python** | 3.13+ | 3.13 |
| **RAM** | 4GB | 14GB (for 8B local models) |
| **Disk** | 500MB (engine) | 10GB (for local models) |
| **CPU** | x86-64, AVX2 | Ryzen 5700U or better |
| **GPU** | None required | None |

---

## v0.5.0-alpha — Current Status

| Feature | Status |
|---------|--------|
| Core Inference (multi-provider) | ✅ Production-ready |
| Entity System & Domain Routing | ✅ Production-ready |
| IWAD Architecture | ✅ Production-ready |
| `omega talk` / `omega summon` | ✅ Production-ready |
| Test Suite (259 tests) | ✅ All passing |
| CI/CD Pipeline | ✅ GitHub Actions |
| Native GGUF (llama-cpp-python) | 🔧 Deferred to v0.6.0 |
| Arcana-NovAi IWAD entities | 🔧 Phase 1b |
| Entity Studio (visual builder) | 🔮 Phase 3 |
| The Omegaverse (P2P) | 🔮 Phase 4 |

---

## Project Status

Omega Engine is in **active development** (alpha). See [MASTER_LEDGER.md](docs/MASTER_LEDGER.md) for the full roadmap.

```
Phase 1a: ✅ IWAD Foundation — Engine-Stack Firewall, Reference IWAD
Phase 1b: 🔧 Arcana-NovAi IWAD, Entity Content
Phase 2:  🔮 Multi-Provider, Qdrant/Redis Backbone
Phase 3:  🔮 Community Tools, Entity Studio
Phase 4:  🔮 The Omegaverse (P2P Network)
```

---

## License

Apache 2.0 — Free. Sovereign. Yours.
