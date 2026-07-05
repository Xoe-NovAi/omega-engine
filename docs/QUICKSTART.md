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
make test                   # Should show 705/705 passing
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
| **8 Providers** | native-gguf → lmster → Ollama → Google → OpenRouter → OpenCode → Copilot → Mock |
| **13 Agents** | Kali (oversight), Ma'at/Lilith (oversouls), 6 specialists, Verity, Iris, Sophia |
| **22 Mandates** | Constitutional law governing all agent behavior |
| **705+ Tests** | Comprehensive test suite via `make test` |
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
