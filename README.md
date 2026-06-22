# 🔱 Omega Engine — Sovereign AI Runtime

**Prometheus' Fire** — A universal, community-owned runtime for sovereign AI. One install. Your computer. Your data. Your stack.

[![Tests](https://github.com/Xoe-NovAi/omega-engine/actions/workflows/test.yml/badge.svg)](https://github.com/Xoe-NovAi/omega-engine/actions/workflows/test.yml)
[![Sovereignty](https://img.shields.io/badge/Sovereignty-Active-brightgreen)]()
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)
[![Local-First](https://img.shields.io/badge/Local--First-Primary-8A2BE2)]()

---

## Quick Start — 4 Commands

```bash
# 1. Clone and install
git clone https://github.com/Xoe-NovAi/omega-engine.git
cd omega-engine
make setup                    # Python venv + all dependencies (includes llama-cpp-python)

# 2. Download the local model (Qwen 1.7B, ~1GB)
make model-download

# 3. Talk to it — runs entirely on your CPU, no cloud keys needed
omega talk "hello"
```

That's it. Your first sovereign AI interaction. The engine auto-routes through available local providers (Native GGUF → LM Studio → Ollama) with cloud as a fallback.

---

## What Omega Is

Omega is a **universal AI runtime** that treats models as infrastructure, not products. It's designed for:

- **Sovereignty** — Local-first, zero telemetry, no vendor lock-in
- **Multi-provider** — Switch seamlessly between native GGUF, LM Studio, Ollama, and cloud fallbacks
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

Omega auto-detects available inference backends. **Local providers are tried first** — no cloud keys required for basic operation.

### Primary: Local Providers

| Provider | Setup | Speed | Sovereign |
|----------|-------|-------|-----------|
| **Native GGUF** | Auto-installed by `make setup` | 🏠 Local | ✅ Full |
| **LM Studio** | `lms server start` | 🏠 Local | ✅ Full |
| **Ollama** | `ollama pull qwen3:1.7b` | 🏠 Local | ✅ Full |

No configuration needed — the engine finds running backends automatically.

### Advanced: Cloud Fallbacks

Cloud providers are optional fallbacks for when local inference is unavailable or you need larger models. **You do not need any cloud keys for the engine to work.**

| Provider | Setup | Speed | Sovereign |
|----------|-------|-------|-----------|
| **OpenRouter** | Set `OPENROUTER_API_KEY` in `.env` | ⚡ Cloud, 300+ models | ❌ Cloud |
| **Google AI Studio** | Set `GOOGLE_API_KEY` in `.env` | ⚡ Cloud, free Gemma 4 31B | ❌ Cloud |
| **Antigravity** | Install `opencode-antigravity-auth` plugin & run `opencode auth login` | ⚡ Cloud, Claude Opus 4.6, Gemini 3.1 Pro | ❌ Cloud |

> **⚠️ Terms of Service**: Cloud providers may use your data for model training. Review each provider's ToS before enabling. The Omega Engine is not affiliated with any cloud provider.

#### Antigravity Models (OpenCode CLI Only)

The Antigravity plugin enables access to premium models through OpenCode CLI with your Google account. **This is NOT wired into the engine's provider fabric round-robin** — it is for explicit CLI usage only (`--model=google/...` flags).

**Setup:**
1. The plugin reference is already in the repo-level `opencode.json`: `"plugin": ["opencode-antigravity-auth@latest"]`
2. Run `opencode auth login` and authenticate with your Google account
3. Select **"Configure models in opencode.json"** when prompted (or models are already configured)

**Available models:**
| Model | Variants | Type |
|-------|----------|------|
| `google/antigravity-gemini-3-pro` | low, high | Gemini 3 Pro with thinking |
| `google/antigravity-gemini-3.1-pro` | low, high | Gemini 3.1 Pro with thinking |
| `google/antigravity-gemini-3-flash` | minimal, low, medium, high | Gemini 3 Flash with thinking |
| `google/antigravity-claude-sonnet-4-6` | — | Claude Sonnet 4.6 |
| `google/antigravity-claude-opus-4-6-thinking` | low, max | Claude Opus 4.6 with extended thinking |
| `google/gemini-2.5-flash` | — | Gemini 2.5 Flash (Gemini CLI quota) |
| `google/gemini-2.5-pro` | — | Gemini 2.5 Pro (Gemini CLI quota) |
| `google/gemini-3-flash-preview` | — | Gemini 3 Flash Preview (Gemini CLI quota) |
| `google/gemini-3-pro-preview` | — | Gemini 3 Pro Preview (Gemini CLI quota) |

**Usage:**
```bash
opencode run "hello" --model=google/antigravity-gemini-3-flash --variant=low
opencode run "hello" --model=google/antigravity-claude-opus-4-6-thinking --variant=max
```

> **⚠️ WARNING**: Using the Antigravity plugin may violate Google's Terms of Service. Users have reported account bans or shadow-bans. Use at your own risk. See the plugin README at `opencode-antigravity-auth/README.md` for full details.

---

## Architecture

```
Query → Entity Registry (domain match) → TriageRouter → ModelGateway
                                                          │
                                           Fallback chain:
                                           native-gguf → LM Studio → Ollama → ...
                                                          │
                                               ┌──────────┴──────────┐
                                          Local models          Cloud fallbacks
                                          (qwen3, krikri,       (Gemma 4, GPT-4o,
                                           phi-4...)             Claude, Qwen...)
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
| **OS** | Linux (Ubuntu 24.04+) | Any modern Linux distro |
| **Python** | 3.12+ | 3.12 |
| **RAM** | 4GB | 14GB (for 8B local models) |
| **Disk** | 500MB (engine) | 10GB (for local models) |
| **CPU** | x86-64, AVX2 | Ryzen 5700U or better |
| **GPU** | None required | None |
| **C Compiler** | GCC/Clang (for llama-cpp-python compilation) | — |

---

## v1.0.0 — Current Status

| Feature | Status |
|---------|--------|
| Core Inference (multi-provider) | ✅ Production-ready |
| Native GGUF (llama-cpp-python) | ✅ Production-ready (primary provider) |
| Entity System & Domain Routing | ✅ Production-ready |
| IWAD Architecture | ✅ Production-ready |
| `omega talk` / `omega summon` | ✅ Production-ready |
| Test Suite (457 tests) | ✅ All passing |
| CI/CD Pipeline | ✅ GitHub Actions |
| Arcana-NovAi IWAD entities | ✅ Production-ready |
| Entity Studio (visual builder) | 🔮 Planned |
| The Omegaverse (P2P) | 🔮 Future |

---

## License

Apache 2.0 — Free. Sovereign. Yours.
