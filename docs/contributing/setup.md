# Contributing Setup — Developer Environment

> How to set up the Omega Engine for development and contribution.

## Prerequisites

- Python 3.12+ with `venv` module
- Git
- Ollama (for local inference testing)
- Podman (optional, for container testing)

## Quick Setup

```bash
# Clone and enter the repo
git clone https://github.com/Xoe-NovAi/omega-engine.git ~/Documents/Xoe-NovAi/omega-engine
cd ~/Documents/Xoe-NovAi/omega-engine

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies (including dev tools)
make setup

# Verify everything works
make test                  # 855+ tests pass
make temple-grade          # T1-T11 quality gates
make heritage-map          # id Software attribution check
```

## Development Workflow

### 1. Branch and Work

```bash
git checkout -b feature/my-feature
# Make changes
make test                  # Always verify
make temple-grade          # Quality gates
```

### 2. Code Standards

| Rule | Standard | Enforcement |
|------|----------|-------------|
| **Async** | AnyIO only — never `asyncio` | CI grep `import asyncio` |
| **Errors** | Typed exceptions — no bare `except:` | CI grep `except:` |
| **Tests** | Every API boundary needs a contract test | `isinstance()` checks |
| **Config** | YAML only for entity/model config | No PostgreSQL for entities |
| **Paths** | Relative via `DATA_DIR` — no hardcoded absolute paths | `make temple-grade` |
| **Imports** | stdlib → third-party → local. Relative within packages | `make lint` |

### 3. Running Specific Tests

```bash
# Run all tests
make test

# Run a specific test file
source .venv/bin/activate
pytest tests/test_oracle.py -v

# Run with coverage
pytest --cov=src/omega tests/

# Run the slowest tests (for profiling)
pytest --durations=15
```

### 4. Code Quality

```bash
make lint                  # flake8 code quality
make temple-grade          # T1-T11 quality gates
make heritage-map          # Verify [id-soft:] tag coverage
make sovereignty           # Local/cloud inference ratio
```

### 5. Documentation

When writing documentation:

- Use the **R-doc format** (see `docs/research/_TEMPLATE.md`)
- Include an **AP token** in the header
- Use **Diátaxis quadrants**: Tutorials (learning), How-to (goal), Reference (info), Explanation (understanding)
- Check for broken links: `make doc-check`
- Check freshness: `make doc-freshness`

### 6. Commit Convention

```
feat: new feature
fix: bug fix
docs: documentation only
refactor: code change that neither fixes a bug nor adds a feature
test: adding or updating tests
ci: CI/CD changes
chore: maintenance tasks
```

## Architecture Overview

```
src/omega/
├── oracle/          # Main entry point (oracle.py, model_gateway.py, context_builder.py)
├── memory/          # Memory store (hot/warm/cold tiers)
├── nova/            # Voice assistant (FastAPI)
├── observability.py # Tracing, events, training data
├── cvar_table.py    # Configuration constants
└── cli/             # Typer CLI

config/
├── omega.yaml       # Engine configuration
├── providers.yaml   # Provider fabric (8 backends)
├── models.yaml      # Model specifications
└── wads/            # WAD stacks (IWAD/PWAD)

tests/               # 855+ tests
docs/                # Documentation (Diátaxis structure)
data/entities/       # Entity soul files and knowledge
```

## Key Commands

```bash
make test              # Run test suite
make temple-grade      # Quality gates (T1-T11)
make lint              # Code quality
make setup             # Install dependencies
make talk MSG='hello'  # Quick interaction
make summon ENTITY='kali' MSG='status'  # Direct entity invocation
make repl              # Interactive REPL
make health            # Provider & model dashboard
make offline-demo      # Demo without internet
```

## Getting Help

- Read `OMEGA_ENGINE.md` — the Single Source of Truth
- Read `SOVEREIGN_MANDATES.md` — the 22 constitutional laws
- Check `docs/research/INDEX.md` — 200+ research documents
- Ask in the project's issue tracker
