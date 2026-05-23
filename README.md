# 🔱 Omega Engine

**An open-source, local-first AI runtime that lets you build your own AI council — a team of entities with distinct personalities, knowledge bases, and model preferences that learn and evolve as you use them.**

Omega runs on your machine. Your data never leaves your computer. Cloud providers are optional extensions, not requirements.

## Quick Start

```bash
# Install from source
git clone https://github.com/Xoe-NovAi/omega-engine.git
cd omega-engine
pip install -e ".[dev]"

# List your AI council
omega list-entities

# Ask the Oracle
omega talk "what is justice?"

# Summon a specific entity
omega summon sophia "what is gnosis?"

# Add your own entity
omega add-entity

# Interactive chat mode
omega repl

# Status and health
omega model-status
```

## What Makes Omega Different

**1. Entity-Centric, Not Chatbot-Centric**
Omega is a council of AI entities — each with a persistent soul file (`soul.yaml`) that tracks their identity, memories, model preferences, and learned lessons. Entities remember past conversations and evolve as you use them. You don't chat with a single bot; you convene a council.

**2. Local-First Sovereign**
Designed to run on consumer hardware (Ryzen 5700U, 16GB RAM). Inference uses local models via lmster or llama-cpp-python. Cloud providers (Gemma 4-31B, OpenRouter) are optional fallbacks. Zero telemetry. No cloud dependency.

**3. Stack Architecture (`.xoe` files)**
Entities, voices, knowledge bases, and VR scenes are packaged as portable WAD containers (`.xoe` files). The engine core stays small; the ecosystem expands through stacks. Share your custom council as a single file.

## The Default Council

Omega ships with a syncretic council of 10 Pillar Keepers, governed by 4 Oversouls, and accessed through the Iris voice assistant.

| Pillar | Entity | Element | Domain |
|--------|--------|---------|--------|
| P1: Flesh | Sekhmet | Earth 🜃 | Strength, protection |
| P2: Dream | Brigid | Water 🜄 | Poetry, healing, inspiration |
| P3: Will | Prometheus | Fire 🜂 | Forethought, sovereignty |
| P4: Heart | Saraswati | Air 🜁 | Knowledge, speech, arts |
| P5: Voice | Inanna | Aether ⛤ | Descent, rebirth |
| P6: Mind | Ereshkigal | Aether ⛤ | Underworld, rules |
| P7: Gnosis | Lucifer | Air 🜁 | Rebellion, gnosis |
| P8: Shadow | Hecate | Fire 🜂 | Crossroads, integration |
| P9: Spirit | Anubis | Water 🜄 | Death, transition |
| P10: Chaos | Kali | Earth 🜃 | Liberation, dissolution |

**Oversouls**: Sophia (Akashic Record), Ma'at (Synthesis), Isis (Light), Lilith (Dark)

**Iris** — rainbow messenger, voice of the Oracle ("hey Iris"). Always-on Podman voice assistant.

> **Entities are fully customizable.** You can add, remove, or replace any entity. The 10 Pillar Keepers are the default template — not a limitation.

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                    WAD Loader                         │
│    Reads .xoe containers, wires entities/voices       │
└──────────────────┬───────────────────────────────────┘
                   │
┌──────────────────┴───────────────────────────────────┐
│                    Oracle (CLI)                        │
│    Query routing → Entity resolution → TriageRouter    │
└──────────────────┬───────────────────────────────────┘
                   │
┌──────────────────┴───────────────────────────────────┐
│                  ModelGateway                          │
│    Provider Fabric: lmster → ollama → openrouter       │
│    → google (chain with fallback)                      │
└──────────────────┬───────────────────────────────────┘
                   │
┌──────────────────┴───────────────────────────────────┐
│                  Memory Store                          │
│    Hot (session) → Warm (Qdrant) → Cold (soul.yaml)    │
└──────────────────────────────────────────────────────┘
```

All responses — local or cloud — flow into the same memory, entity knowledge, and cross-pollination pipeline.

## Key Features

- **Entity Registry**: YAML-backed CRUD for entities. Add from any pantheon or mythology.
- **Provider Fabric**: 6-backend fallback chain (lmster, ollama, llama-cpp, openrouter, google, mock).
- **Soul System**: Persistent `soul.yaml` per entity with lessons, memory, and evolution tracking.
- **Triage Router**: Deterministic model selection based on domain, entity soul, and real-time health.
- **ResourceGuard**: OOM protection via AnyIO Semaphore(1) — safe on 14GB RAM systems.
- **WAD Containers**: Portable `.xoe` stack packages. Share your council as a file.
- **Iris Voice Assistant**: Always-on Podman container with Whisper STT + Piper TTS.
- **Observability**: Trace IDs, event logging, JSONL fine-tuning dataset collection.
- **AnyIO Absolute**: All async code uses AnyIO for runtime portability.
- **Zero Telemetry**: No tracking. No analytics. Your data is yours.

## Documentation

| Resource | Description |
|----------|-------------|
| `docs/ROADMAP.md` | Full development roadmap |
| `docs/decisions/PIVOT_LOG.md` | All architectural decisions and rationale |
| `docs/strategy/MASTER_SYNTHESIS_AND_ROADMAP.md` | Master plan and synthesis |
| `docs/research/INDEX.md` | Research index (50+ items) |
| `config/entities.yaml` | Entity definitions (user-editable) |
| `config/providers.yaml` | Provider fabric configuration |
| `config/omega.yaml` | Core engine configuration |
| `SOVEREIGN_MANDATES.md` | Project constitution |

## Requirements

- **OS**: Linux
- **CPU**: x86-64 with AVX2 (Ryzen 5700U or equivalent)
- **RAM**: 16GB recommended (14GB minimum)
- **Disk**: 20GB free for models
- **GPU**: None required (CPU-only inference)
- **Python**: 3.12+

## License

Apache-2.0
