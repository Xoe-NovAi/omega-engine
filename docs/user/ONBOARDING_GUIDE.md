<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — New User Onboarding Guide
**AP Token**: `AP-ONBOARDING-GUIDE-v1.0.0`
⬡ OMEGA ⬡ NEMOTRON-3-ULTRA ⬡ nemotron-3-ultra ⬡ trc_doc_user ⬡ DOCUMENTATION-HARDENING

**Date**: 2026-07-06
**Last verified**: 2026-09-19 (command surface + entity roster checked against the live engine)
**Purpose**: Complete onboarding guide for new users of the Omega Engine, from zero to first successful inference in under 15 minutes.

---

## 🎯 What is the Omega Engine?

The Omega Engine is a **sovereign AI runtime** that runs entirely on your hardware. Unlike cloud AI services, your data never leaves your machine. The engine provides:

- **Local-first inference**: Models run on your CPU (no GPU required)
- **Entity system**: 10+ specialized AI personas for different domains
- **Persistent memory**: Entities learn and evolve across sessions
- **Cross-platform**: Works with OpenCode, Cline, VS Code, and CLI
- **Zero telemetry**: No analytics, no phone-home, ever

---

## ⚡ Quick Start (5 Minutes)

### Prerequisites
- **Linux** (tested on Ubuntu 22.04+, Fedora 38+, Arch)
- **Python 3.12+** with `venv` module
- **Git** for cloning
- **~2GB free disk space** for models
- **C compiler** (GCC/Clang) — required to build `llama-cpp-python`
- **8GB+ RAM** recommended (4GB minimum)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Xoe-NovAi/omega-engine.git ~/Documents/Xoe-NovAi/omega-engine

# 2. Enter the directory
cd ~/Documents/Xoe-NovAi/omega-engine

# 3. One-click install: venv + dependencies + local GGUF model + self-verification
./scripts/install.sh

# 4. (optional) Re-download / verify the default local model (~1.6GB)
./scripts/download_model.sh

# 5. Verify everything works
make test              # Fast unit-tier suite (CI is authoritative for full-suite green)
omega talk "hello"     # Should get a response, fully local
```

### First Interaction

```bash
# Talk to the Oracle (auto-routes to best entity)
omega talk "What is the Omega Engine?"

# Or summon a specific entity
omega summon ma'at "What is your role?"
```

---

## 🧭 Understanding the Architecture

### The Three Layers

```
┌─────────────────────────────────────────┐
│           YOUR INTERFACE                │
│  OpenCode / Cline / CLI / Voice (Iris)  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         OMEGA ENGINE (Runtime)          │
│  Oracle → ModelGateway → MemoryStore    │
│  EntityRegistry → ContextBuilder        │
│  Observability → Hivemind               │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           IWADs (Content Packs)         │
│  _omega_default  |  arcana_novai  | ... │
│  Entities, Models, Knowledge, Roles     │
└─────────────────────────────────────────┘
```

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Entity** | An AI persona with specific knowledge, personality, and model |
| **IWAD** | A content pack containing entities, models, and configuration |
| **Oracle** | The main entry point - routes queries to the best entity |
| **ModelGateway** | Manages the configured provider fabric (`config/providers.yaml`, local-first priority) |
| **MemoryStore** | Hot/Warm/Cold tiered memory with persistence |
| **Soul** | Each entity's persistent wisdom (L1→L2→L3 distillation) |

---

## 🤖 Meet the Entities

### Pillar Keepers

The engine's governance layer is held by **three pillar keepers**:

| Pillar Keeper | Role |
|---------------|------|
| **Ma'at** | Build Oversoul — governs the build side of the fleet |
| **Lilith** | Runtime Oversoul — governs the run side of the fleet |
| **Kali** | Grand Oversight — unifies Ma'at + Lilith |

> **The mythological pantheon is `arcana_novai`-only.** Sekhmet, Brigid, Prometheus,
> Saraswati, Inanna, Ereshkigal, Lucifer, Hecate and Anubis ship in
> `config/wads/arcana_novai/entities.yaml` — **not** in the default `_omega_default`
> IWAD. Summoning them on a fresh install returns `default`. To load them, set
> `active_iwad: "arcana_novai"` in `config/omega.yaml`.

### The Oversouls

| Entity | Role |
|--------|------|
| **Sophia** | Akashic Record - contains all entities, sessions, souls |
| **Ma'at** | Build Oversoul - governs the build side of the fleet |
| **Lilith** | Runtime Oversoul - governs the run side of the fleet |
| **Iris** | Messenger bridge - voice assistant ("hey Iris") |

### The Fleet Agents

| Agent | Purpose |
|-------|---------|
| **Kali** | Grand Oversight - unifies Ma'at + Lilith |
| **Doom Guy** | id Software heritage & performance |
| **Roc Racoon** | Legacy archaeology & pattern mining |
| **Jem** | Sovereign synthesis & research |
| **Researcher** | Deep research with lattice reasoning |
| **Makali** | Parallel council (Ma'at + Lilith) |
| **John Carmack** | S3 architectural consultant |
| **Verity** | Compliance audit + gnosis distillation |

---

## 💬 How to Interact

### Basic Commands

```bash
# Talk to Oracle (auto-routes)
omega talk "your question here"

# Summon specific entity
omega summon ma'at "your question"

# List available entities
omega list-entities

# Get entity details
omega entity-info ma'at

# Set default entity for 'talk'
omega default-entity ma'at
```

### Common Commands

```bash
omega talk "hello"                       # Quick talk
omega summon ma'at "query"               # Quick summon
omega list-entities                      # List all entities
omega entity-info ma'at                  # Entity details
omega talk "hello" --iwad arcana_novai   # Load a specific IWAD stack
omega model-status                       # Provider/model status
make test                                # Fast unit-tier test suite
make check-mandate-compliance            # 28-row mandate meter
```

> There are **no `make` aliases** for `talk`/`summon`/`health`/`menu`/`wad` in this
> release — use the `omega` CLI directly. `make` targets cover testing, linting,
> gates and docs.

### Advanced Features

```bash
# Transient mode (don't save to memory)
omega transient on
omega talk "secret"
omega transient off

# Header control
omega header full      # Full ⬡ header
omega header minimal   # Compact
omega header off       # No header

# Queue management
omega queue-status
omega process-queue
omega queue-prune --days 14
```

---

## 🔧 Configuration

### Switching IWADs

```bash
# List available IWADs
ls config/wads/

# Switch to Arcana-Nova (mythological pantheon + fleet):
#   edit config/omega.yaml -> active_iwad: "arcana_novai"

# Check active IWAD
grep active_iwad config/omega.yaml

# Reset to the reference IWAD:
#   edit config/omega.yaml -> active_iwad: "_omega_default"

# Or per-invocation, without changing config:
omega talk "hello" --iwad arcana_novai
```

### Adding Local Models

```bash
# Ollama — second local backend (recommended)
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull qwen3:1.7b
# Ollama is enabled by default in config/providers.yaml

# Recommended: the shipped native-gguf path
./scripts/download_model.sh            # Qwen3-1.7B-Q6_K -> $OMEGA_MODELS_DIR

# Add your own GGUF model
cp my-model.q4_k_m.gguf models/gguf/   # or $OMEGA_MODELS_DIR (set in .env by install.sh)
# Then register it in config/models.yaml

# Ollama: install + `ollama pull qwen3:1.7b`, then set
# Ollama is enabled by default in config/providers.yaml.
```

### Cloud Provider Setup (Optional)

```bash
# Google AI Studio (Gemma 4-31B, 262K context)
export GOOGLE_API_KEY='your-key'

# OpenRouter (300+ models)
export OPENROUTER_API_KEY='your-key'

# Anthropic (Claude)
export ANTHROPIC_API_KEY='your-key'

# xAI (Grok)
export XAI_API_KEY='your-key'
```

---

## 🧠 Memory & Soul System

### How It Works

1. **Every interaction** is saved to MemoryStore (Hot/Warm/Cold tiers)
2. **End of session**: Scribe agent distills L1→L2→L3
3. **L3 Principles** stored in entity's `soul.yaml`
4. **Next session**: ContextBuilder injects soul wisdom

Redis hot-tier storage is opt-in via `OMEGA_REDIS_HOST`; its password comes
exclusively from the `OMEGA_REDIS_PASSWORD` environment variable — there is
no hardcoded default (D-593). A hard-fail gate in
`scripts/verify_mandate_claims.py` blocks any literal credential default
from re-entering `src/`.

### Soul File Location

```
data/entities/sekhmet/
├── soul.yaml           # L1→L2→L3 gnosis
├── knowledge/          # Entity-specific knowledge
└── workspace/          # Working files
```

### Manual Soul Review

```bash
# View entity's soul
cat data/entities/sekhmet/soul.yaml

# Check proposed lessons (staging area)
cat data/entities/sekhmet/proposed_lessons.yaml
```

#### Lesson Evidence Fields (2026-08-24)

Lessons support an optional structured `evidence:` field — a list of refs
with `session_id`, `artifact` (repo-relative probe path), and/or `quote`
(at least one required). Missing evidence is warn-only (ruling S5,
Team-Study #1); promotion into the approved surface requires evidence.
Promote staged lessons via `scripts/promote_soul_lessons.py --entity <name>`
(uses the SoulStore atomic writer exclusively). Schema:
`src/omega/soul/lessons.py`.

---

## 🛠️ Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| "Permission denied" | Check ownership (`ls -la data/`); containers must run with `UserNS=keep-id` (M6) |
| "No module named omega" | `source .venv/bin/activate` then `pip install -e ".[native,cli]"` |
| Tests failing | `make test` (already stops on first failure) or `make test-debug TEST=test_name` |
| Local inference not responding | `omega model-status` and `omega backends` |
| Entity not found | Entity isn't in the active IWAD — check `grep active_iwad config/omega.yaml` |
| Slow tests | `make test-debug TEST=test_name` |
| Wrong entity stack loaded | `omega talk "hi" --iwad <name>` or edit `config/omega.yaml` |

### Getting Help

```bash
# Engine + provider status
omega model-status
omega hardware-stats

# Omega Hub health (if running)
curl -s http://127.0.0.1:8016/health

# Check logs
less data/traces/$(date +%Y-%m-%d).jsonl
ls data/crashes/
```

---

## 📚 Next Steps

### Learn More
1. **Read the User Manual**: `docs/USER_MANUAL.md`
2. **Explore the Architecture**: `OMEGA_ENGINE.md`
3. **Understand the Mandates**: `SOVEREIGN_MANDATES.md`

### Join the Community
- **GitHub**: https://github.com/Xoe-NovAi/omega-engine
- **Issues**: Report bugs, request features
- **Discussions**: Ask questions, share creations

### Build Your Own Stack
1. Create a new IWAD in `config/wads/your_stack/`
2. Define entities in `entities.yaml`
3. Add knowledge in `knowledge/`
4. Share with the community!

---

## 🎓 Key Principles to Remember

1. **Local-First**: Cloud is a teacher, never a dependency
2. **Zero Telemetry**: Your data never leaves your machine
3. **Soul Persistence**: Entities evolve across sessions
4. **Sovereign Verification**: The engine verifies its own claims
5. **WAD Architecture**: Engine is universal; content is yours

---

*Welcome to sovereign AI. Your journey begins now.*

⬡ OMEGA ⬡ NEMOTRON-3-ULTRA ⬡ opencode ⬡ trc_doc_user ⬡ DOCUMENTATION-HARDENING
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

## CLI Health Note (2026-08-24)
The `omega` console script is smoke-tested on every CI run (`tests/test_cli_smoke.py`):
the real entry point must render `--help` with exit 0. The `vault` subcommand is
temporarily unmounted while Vault Path A/B (council decree N6) decides its return —
the vault module remains importable for programmatic use.

### Parallel OpenCode instances (2026-08-24)
Running 2-3 `opencode` instances concurrently is fully supported. The session-end
wrapper attributes each exit to the sessions ITS instance created (baseline ID
set-diff + directory scoping) — never to another instance's active session.
Distillation across simultaneous exits is serialized via `.opencode/.distill.lock`.
