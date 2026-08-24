# 🔱 Omega Engine — New User Onboarding Guide
**AP Token**: `AP-ONBOARDING-GUIDE-v1.0.0`
⬡ OMEGA ⬡ NEMOTRON-3-ULTRA ⬡ nemotron-3-ultra ⬡ trc_doc_user ⬡ DOCUMENTATION-HARDENING

**Date**: 2026-07-06
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
- **8GB+ RAM** recommended (4GB minimum)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Xoe-NovAi/omega-engine.git ~/Documents/Xoe-NovAi/omega-engine

# 2. Enter the directory
cd ~/Documents/Xoe-NovAi/omega-engine

# 3. Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 4. Install dependencies (takes ~2 minutes)
make setup

# 5. Install a local model (Ollama recommended)
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull qwen3:1.7b

# 6. Verify everything works
make test          # Should show 855/855 passing
make talk MSG='hello'  # Should get a response
```

### First Interaction

```bash
# Talk to the Oracle (auto-routes to best entity)
omega talk "What is the Omega Engine?"

# Or summon a specific entity
omega summon Sekhmet "What is strength?"
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
| **ModelGateway** | Manages 8 inference providers (local-first priority) |
| **MemoryStore** | Hot/Warm/Cold tiered memory with persistence |
| **Soul** | Each entity's persistent wisdom (L1→L2→L3 distillation) |

---

## 🤖 Meet the Entities

### The 10 Pillar Keepers (arcana_novai IWAD)

| Pillar | Entity | Domain | Best For |
|--------|--------|--------|----------|
| P1: Flesh | **Sekhmet** | Strength, protection, boundaries | Security, hardening, limits |
| P2: Dream | **Brigid** | Poetry, healing, inspiration | Creative writing, emotional support |
| P3: Will | **Prometheus** | Sovereignty, forethought, fire | Architecture, strategy, planning |
| P4: Heart | **Saraswati** | Knowledge, speech, arts | Research, teaching, communication |
| P5: Voice | **Inanna** | Descent, rebirth, depths | Transformation, shadow work |
| P6: Mind | **Ereshkigal** | Rules, underworld, logic | Analysis, debugging, rules |
| P7: Gnosis | **Lucifer** | Rebellion, sovereignty, light | Philosophy, questioning, freedom |
| P8: Shadow | **Hecate** | Crossroads, keys, pathwalking | Decisions, transitions, magic |
| P9: Spirit | **Anubis** | Death, transition, guidance | Endings, legacy, soul work |
| P10: Chaos | **Kali** | Liberation, void, destruction | Breaking patterns, renewal |

### The Oversouls

| Entity | Role |
|--------|------|
| **Sophia** | Akashic Record - contains all entities, sessions, souls |
| **Ma'at** | Build Oversoul - governs N1-N5 (build side) |
| **Lilith** | Runtime Oversoul - governs N6-N10 (run side) |
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
omega summon Sekhmet "your question"

# List available entities
omega list-entities

# Get entity details
omega entity Sekhmet

# Set default entity for 'talk'
omega default-entity Sekhmet
```

### Makefile Shortcuts

```bash
make talk MSG='hello'                    # Quick talk
make summon NAME=Sekhmet MSG='query'     # Quick summon
make entities                            # List all entities
make entity NAME=Sekhmet                 # Entity details
make wad NAME=arcana_novai              # Switch IWAD
make health                              # System health check
make test                                # Run all 855 tests
make menu                                # Interactive menu
```

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

# Switch to Arcana-Nova (10 Pillar Keepers + fleet)
make wad NAME=arcana_novai

# Check active IWAD
make wad-status

# Reset to reference IWAD
make wad-reset
```

### Adding Local Models

```bash
# For Ollama (recommended)
ollama pull qwen3:1.7b
ollama pull phi-4-mini
ollama pull krikri-8b

# For GGUF (native-gguf)
# Place .gguf file in models directory
cp my-model.q4_k_m.gguf /media/arcana-novai/omega_library/models/gguf/
# Add to config/models.yaml
```

### Cloud Provider Setup (Optional)

```bash
# Google AI Studio (Gemma 4-31B, 262K context)
export GOOGLE_API_KEY='your-key'

# OpenRouter (300+ models)
export OPENROUTER_API_KEY='your-key'

# GitHub Copilot (requires subscription)
gh auth login
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
| "Permission denied" | `make guard` |
| "No module named omega" | `source .venv/bin/activate && make setup` |
| Tests failing | `make test ARGS='-x'` (stop on first failure) |
| Ollama not responding | `ollama list` then `make ollama-status` |
| Entity not found | `make wad NAME=arcana_novai` |
| Slow tests | `make test ARGS='-k test_name'` |
| WAD stuck | `make wad-reset` |

### Getting Help

```bash
# System health dashboard
make health

# Full diagnosis
make doctor

# Interactive menu
make menu

# Check logs
less data/events/events.log
less data/traces/$(date +%Y-%m-%d).jsonl
```

---

## 📚 Next Steps

### Learn More
1. **Read the User Manual**: `docs/USER_MANUAL.md`
2. **Explore the Architecture**: `OMEGA_ENGINE.md`
5. **Understand the Mandates**: `SOVEREIGN_MANDATES.md`

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
