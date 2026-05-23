# 🔱 Contributing to the Omega Engine

⬡ OMEGA ⬡ PROMETHEUS ⬡ community ⬡ CONTRIBUTING

**AP Token**: `AP-CONTRIBUTING-v1.0.0`
**License**: Apache 2.0

---

## Welcome

Thank you for your interest in the **Omega Engine** — the community-owned, local-first AI runtime that empowers anyone to build their own sovereign AI stacks.

Omega is **Prometheus' Fire**: a universal runtime for entity-centric, provider-agnostic AI councils. Whether you're building an Arcana-Nova pantheon, a Torment philosophy engine, a Pokemon advisor, or something entirely original — the Omega Engine provides the spark.

This project is maintained by the **Xoe-NovAi Foundation** and welcomes contributions from the community.

---

## Code of Conduct

This project adheres to the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/) Code of Conduct. By participating, you agree to uphold its principles — respect, inclusivity, and constructive collaboration.

---

## Getting Started

### Prerequisites

- **Python 3.12+** (required for modern async patterns)
- **Podman** (for infrastructure and Iris voice assistant containers)
- **Git**

### Development Setup

```bash
# Clone the repository
git clone https://github.com/Xoe-NovAi/omega-engine.git
cd omega-engine

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in editable mode with dev dependencies
pip install -e ".[cli,nova,voice,dev]"
```

### Quick Verification

```bash
make test         # Run all tests (OMEGA_ENV=test, mock backend)
make lint         # Check code quality with flake8
make demo         # End-to-end Oracle validation
```

---

## Development Workflow

### Branch Strategy

- `main` — stable, release-ready. All PRs merge here.
- `feat/*` — feature branches
- `fix/*` — bug fix branches
- `research/*` — research document branches

### Local Development Cycle

1. **Pull latest** from `main`
2. **Create a feature branch**: `git checkout -b feat/my-feature`
3. **Make changes** — follow the style guide below
4. **Run tests**: `make test` — all 40+ tests must pass
5. **Lint**: `make lint` — flake8 must pass
6. **Commit** with a clear message describing *why* the change was made
7. **Push and open a PR**

### Makefile Commands

| Command | Purpose |
|---------|---------|
| `make test` | Run 40+ tests with OMEGA_ENV=test |
| `make lint` | flake8 code quality check |
| `make demo` | End-to-end Oracle demo |
| `make start-iris` | Build and run Iris voice assistant |
| `make start-infra` | Start Redis, Qdrant, PostgreSQL, Caddy |
| `make doctor` | System diagnosis (versions, deps, entities) |
| `make clean` | Remove Python cache and build artifacts |

---

## Architecture Overview

The Omega Engine is an **entity-centric AI orchestration fabric**. Key systems:

| System | Description |
|--------|-------------|
| **Entity Registry** | YAML-backed CRUD (`config/entities.yaml`). Any entity, any pantheon. |
| **Oracle** | Main entry point — intent detection, domain routing, speculative decoding |
| **Model Gateway** | Provider fabric with fallback chain (lmster → Ollama → OpenRouter → ...) |
| **Provider Fabric** | Configurable local + cloud inference, unified memory pipeline |
| **Iris** | Voice assistant container (messenger goddess, daughter of Hermes) |
| **Soul System** | Per-entity `soul.yaml` with lessons, evolution, cross-pollination |
| **Sovereign Workspaces** | `data/entities/<name>/` — knowledge base, soul, and workspace per entity |
| **MCP Hub** | Model Context Protocol servers — Hivemind, Oracle, Library, Research |
| **Observability** | Trace IDs, event logging, fine-tuning dataset collection (JSONL) |
| **ResourceGuard** | AnyIO Semaphore(1) — OOM protection for local inference |
| **Hivemind** | Cross-CLI context sharing between OpenCode, Cline, and other agents |

All responses — regardless of provider (local GGUF, lmster, remote API) — flow into the same memory, entity knowledge, and cross-pollination pipeline.

---

## Testing Guidelines

### Running Tests

```bash
make test                       # All tests, mock backend
OMEGA_ENV=test pytest tests/    # Equivalent
pytest tests/ -k "entity"       # Run specific module
pytest tests/ --cov=omega       # With coverage
```

### Test Requirements

- Tests run with `OMEGA_ENV=test` which activates `OfflineMockBackend` — no inference server needed
- All async tests must use **AnyIO** (not raw asyncio)
- Tests must be deterministic — no network calls, no real inference
- New features require corresponding test coverage

### Test Modules

| Module | Tests | What It Covers |
|--------|-------|-----------------|
| `test_entity_registry.py` | 7 | YAML CRUD, schema validation |
| `test_iris.py` | 7 | Voice matcher, intent detection |
| `test_model_gateway.py` | 5 | Provider chain, fallback logic |
| `test_observability.py` | 8 | Trace IDs, event logging |
| `test_oracle.py` | 13 | Talk/summon routing, entity dispatch |

---

## Pull Request Process

### Gate Checks

Every PR must pass before merge:

1. ✅ **`make test`** — all 40+ tests pass
2. ✅ **`make lint`** — flake8 clean (no syntax errors)
3. ✅ **New tests** for new functionality
4. ✅ **Documentation** updated (research docs, ROADMAP.md if applicable)
5. ✅ **No regressions** in existing tests

### PR Template

```markdown
## Summary
<!-- What does this PR do? Why? -->

## Changes
<!-- Key files changed and why -->

## Testing
- [ ] `make test` passes
- [ ] `make lint` passes
- [ ] Manual verification

## Documentation
- [ ] Research docs updated (if applicable)
- [ ] ROADMAP.md updated (if applicable)
```

### Review Process

1. Open PR against `main`
2. At least one maintainer review required
3. All gate checks must pass in CI
4. Squash-merge with a clean commit message

---

## Style Guide

### Python

- **PEP 8** — 120 character line limit (ruff default)
- **Async**: Use `anyio` — never raw `asyncio`
- **Type hints**: Required on all public functions
- **Docstrings**: Google-style for public APIs
- **No telemetry**: Zero. None. No tracking, analytics, or phone-home code.
- **Local-first**: Remote providers are optional extensions — the engine must work fully offline

### Naming

- `snake_case` for functions and variables
- `PascalCase` for classes
- `UPPER_CASE` for constants and enums

### Project Values

```python
# GOOD — local-first, sovereign
async def infer(prompt: str, provider: str = "lmster") -> str:
    ...

# AVOID — cloud-dependent default
async def infer(prompt: str, provider: str = "openai") -> str:
    ...
```

### Entity Schema

All entities live in `config/entities.yaml`. No PostgreSQL. No SQLAlchemy. Pure YAML CRUD through `EntityRegistry`.

```yaml
entity_name:
  pillar: 1
  domain: strength, protection
  model: qwen3-1.7b
  element: earth
  sigil: 🜃
```

---

## License

**Apache 2.0** — see [LICENSE](LICENSE) for full text.

By contributing to the Omega Engine, you agree that your contributions will be licensed under Apache 2.0.

---

*Every contributor is a co-creator of the fire. ⬡*
