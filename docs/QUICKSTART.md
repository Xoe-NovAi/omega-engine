# 🔱 Omega Engine — Quick Start Guide
**AP Token**: `AP-QUICKSTART-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_doc_user ⬡ STANDARD

**Date**: 2026-07-13
**Purpose**: 5-minute getting started guide for new Omega Engine users.

---

# Omega Engine — Quick Start

> Install and run your sovereign AI runtime in 5 minutes.

## Prerequisites

- **Python 3.12+** (check: `python3 --version`)
- **Git** (check: `git --version`)
- **Ollama** (recommended for local inference)

## Install

```bash
# 1. Clone the repo
git clone https://github.com/Xoe-NovAi/omega-engine.git ~/Documents/Xoe-NovAi/omega-engine
cd ~/Documents/Xoe-NovAi/omega-engine

# 2. Set up the environment
python3 -m venv .venv
source .venv/bin/activate
make setup

# 3. Pull a local model
ollama pull qwen3:1.7b     # ~1.1 GB, best quality/speed balance

# 4. Verify installation
make test                   # Should show 1315/1315 passing
```

## First Interaction

```bash
# Talk to the default entity (Sophia)
make talk MSG='hello'

# Summon a specific entity
make summon ENTITY='kali' MSG='what is your status?'

# List all registered entities
make list-entities

# Launch interactive REPL
make repl
```

## What You Get

| Component | Description |
|-----------|-------------|
| **Oracle** | Intent detection, entity routing, speculative decoding |
| **9 Providers** | native-gguf → lmster → Ollama → Antigravity → Google → OpenRouter → OpenCode → Cline → Mock |
| **13 Presences** | Kali (oversight), Ma'at/Lilith (oversouls), 6 specialists, Verity, Iris, Sophia |
| **23 Mandates** | Constitutional law governing all agent behavior |
| **1315 Tests** | Comprehensive test suite via `make test` |
| **Local-first** | Cloud is fallback, never dependency |

## Next Steps

- [User Manual](USER_MANUAL.md) — Full guide (1,198 lines)
- [Contributing Setup](contributing/setup.md) — Developer environment
- [Architecture Overview](explanation/architecture.md) — How it all works
- [First Entity Tutorial](tutorials/first-entity.md) — Create your own entity
- [llms.txt](llms.txt) — AI agent navigation sitemap

## Troubleshooting

**Tests fail with import errors?**
```bash
source .venv/bin/activate
pip install -e ".[dev]"
```

**Ollama connection refused?**
```bash
ollama serve &
sleep 2
make talk MSG='hello'
```

**No local model available?**
```bash
# Use the offline mock backend
OMEGA_ENV=test make talk MSG='hello'
```

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
