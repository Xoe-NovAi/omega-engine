# 🔱 Omega Engine — User Manual
# Sovereign AI Runtime — Terminal Edition
# Version 3.0.0 | HORIZON 1 COMPLETE | 302 Tests Passing

## Table of Contents
1. [Quick Start](#quick-start)
2. [Menu Interface](#menu-interface)
3. [CLI Commands (Oracle)](#cli-commands-oracle)
4. [Offline Demo Mode](#offline-demo-mode)
5. [Makefile Reference](#makefile-reference)
6. [Scripts Reference](#scripts-reference)
7. [Architecture Overview](#architecture-overview)
8. [Entity System](#entity-system)
9. [Troubleshooting](#troubleshooting)

---

## Quick Start

```bash
# 1. Enter the environment
cd ~/Documents/Xoe-NovAi/omega-engine
source .venv/bin/activate

# 2. See the main menu
make menu

# 3. Run the offline demo (no internet needed)
make offline-demo

# 4. Launch interactive REPL
make repl

# 5. Run all tests
make test
```

---

## Menu Interface

The Omega Engine provides a polished text-based menu via `make menu`:

```
╔══════════════════════════════════════════════════════╗
║  🔱 OMEGA ENGINE — HORIZON 1 COMPLETE               ║
║  302 tests ✅  |  71 modules  |  All 12 Mandates     ║
╚══════════════════════════════════════════════════════╝

🔥 CORE
  make demo         Run the Oracle demo (talk + summon)
  make repl         Launch interactive REPL
  make health       System health dashboard
  make doctor       Full system diagnosis
  make menu         This menu

🧪 TESTING
  make test         Run all 302 tests
  make lint         Lint with flake8
  make guard        Fix permission drift (UID Guard)

🤖 LOCAL INFERENCE
  make lmster-start  Start LM Studio server
  make lmster-stop   Stop LM Studio
  make lmster-status Check LM Studio

🗣️  ENTITY COMMANDS
  make entities     List all entities
  make entity NAME=x  Show entity details
  make summon NAME=E MSG='query'  Summon entity
  make talk MSG='hello'  Talk to Oracle

📦 QUEUE & LIBRARY
  make queue-status      Show request queue
  make library-status    Library catalog stats
  make library-search    Search library

📊 BENCHMARKS
  make bench-run     Run a benchmark
  make bench-list    List completed runs
  make bench-rank    Show best model

🏗️  INFRASTRUCTURE
  make start-infra   Start Redis/Qdrant/PostgreSQL/Caddy containers
  make stop-infra    Stop all containers
  make mcp-check     MCP service health check

🧹 MAINTENANCE
  make clean         Clean Python cache
  make setup         Install dependencies
  make bootstrap     Full system bootstrap
```

---

## CLI Commands (Oracle)

The Oracle is the main entry point for interacting with the Omega Engine.

```bash
# General usage
omega talk "your question"              # Ask the Oracle anything
omega summon Sekhmet "what is strength?"  # Summon a specific entity
```

### All CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `talk` | Ask the Oracle anything. Routes to best entity. | `omega talk "what is justice?"` |
| `summon` | Summon a specific entity by name. | `omega summon Lilith "what do you see?"` |
| `list-entities` | List all entities in the current pantheon. | `omega list-entities` |
| `entity` / `entity-info` | Show details about a specific entity. | `omega entity Sekhmet` |
| `add-entity` | Add a new entity (interactive). | `omega add-entity` |
| `default-entity` | Set the default entity. | `omega default-entity Sekhmet` |
| `transient` | Toggle transient mode (no memory). | `omega transient on` |
| `header` | Toggle session header mode. | `omega header full` |
| `mcp-restart` | Restart an MCP service. | `omega mcp-restart omega-hub` |
| `queue-status` | Show pending queued/review items. | `omega queue-status` |
| `process-queue` | Process all queued research requests. | `omega process-queue` |
| `review-pending` | Process pending cloud review requests. | `omega review-pending` |
| `queue-prune` | Archive stale requests older than N days. | `omega queue-prune --days 14` |
| `library-curate` | Run domain curation on the library. | `omega library-curate` |
| `library-status` | Show library catalog statistics. | `omega library-status` |
| `library-search` | Search the library catalog. | `omega library-search "quantum"` |
| `bench-run` | Run a benchmark for a model and role. | `omega bench-run qwen3-1.7b will` |
| `bench-compare` | Compare models for a role. | `omega bench-compare will` |
| `bench-rank` | Show the best model for a role. | `omega bench-rank will` |
| `bench-list` | List all completed benchmark runs. | `omega bench-list` |

### Via Makefile Aliases

```bash
make talk MSG='hello'                    # Quick talk
make summon NAME=Sekhmet MSG='query'     # Quick summon
make entities                            # List entities
make entity NAME=Sekhmet                # Entity info
make queue-status                       # Queue status
make queue-prune DAYS=14                # Prune queue
make library-status                     # Library stats
make library-search QUERY='term'        # Search library
make bench-run MODEL=qwen3-1.7b ROLE=will  # Run benchmark
make bench-rank ROLE=will               # Best model
```

---

## Offline Demo Mode

The Omega Engine can run a complete demo with **zero internet access**.
Perfect for boat demos, presentations, or air-gapped environments.

```bash
make offline-demo
```

This runs:
1. Lists all entities
2. Talks to Oracle (`"who are you?"`)
3. Summons Sekhmet (`"what is strength?"`)
4. Checks system status

All responses are generated by `OfflineMockBackend` — a deterministic mock
that requires no model loading, no network calls, and no infrastructure.

### How It Works

The mock backend activates when `OMEGA_ENV=test` is set:
```bash
OMEGA_ENV=test make talk MSG='who are you?'
```

The provider chain is:
```
native-gguf → lmster → Ollama → Google → OpenRouter → OpenCode → Copilot → MOCK
```

With `OMEGA_ENV=test`, all providers are skipped except MOCK.
Without the test env variable, the engine tries local providers first, then cloud.

---

## Makefile Reference

### Core Commands

| Target | Description |
|--------|-------------|
| `make menu` | Show the polished text-based menu |
| `make demo` | Run the Oracle demo (talk + summon) |
| `make offline-demo` | Run demo with MockBackend (no internet) |
| `make repl` | Launch interactive REPL |
| `make health` | System health dashboard |
| `make doctor` | Full system diagnosis |
| `make talk MSG='q'` | Quick talk to Oracle |
| `make summon NAME=E MSG='q'` | Quick entity summon |
| `make entities` | List all entities |
| `make entity NAME=x` | Show entity details |

### Testing & Quality

| Target | Description |
|--------|-------------|
| `make test` | Run all 302 tests (includes UID Guard) |
| `make test ARGS='-k pattern'` | Run filtered tests |
| `make test-cov` | Run tests with coverage report |
| `make lint` | Lint with flake8 |
| `make guard` | Fix permission drift (UID Guard) |
| `make mcp-check` | MCP service health check |

### Infrastructure

| Target | Description |
|--------|-------------|
| `make start-infra` | Start Redis, Qdrant, PostgreSQL, Caddy containers |
| `make stop-infra` | Stop all containers |
| `make restart-infra` | Restart all containers |
| `make infra-status` | Check container status |
| `make start-iris` | Start Iris voice assistant container |
| `make stop-iris` | Stop Iris container |

### Local Inference

| Target | Description |
|--------|-------------|
| `make lmster-start` | Start LM Studio inference server |
| `make lmster-stop` | Stop LM Studio server |
| `make lmster-status` | Check LM Studio status |
| `make lmster-load MODEL=x` | Load a model into LM Studio |

### Queue & Library

| Target | Description |
|--------|-------------|
| `make queue-status` | Show request queue status |
| `make process-queue` | Process queued items |
| `make queue-prune` | Archive stale requests |
| `make library-status` | Library catalog statistics |
| `make library-search` | Search library catalog |
| `make library-curate` | Run domain curation |

### Benchmarks

| Target | Description |
|--------|-------------|
| `make bench-run MODEL=x ROLE=y` | Run a benchmark |
| `make bench-list` | List completed runs |
| `make bench-rank ROLE=y` | Show best model for role |
| `make bench-compare ROLE=y` | Compare all models for role |

### Research & Docs

| Target | Description |
|--------|-------------|
| `make research-run` | Manual research cycle trigger |
| `make research-status` | Show research queue status |
| `make validate-research` | Validate research document integrity |
| `make mkdocs-serve` | Serve research documentation site |
| `make mkdocs-build` | Build static research docs |

### Maintenance

| Target | Description |
|--------|-------------|
| `make setup` | Install Python dependencies |
| `make bootstrap` | Complete system bootstrap |
| `make clean` | Clean Python cache and artifacts |
| `make doctor` | Full system diagnosis |

### Git

| Target | Description |
|--------|-------------|
| `make git-status` | Show working tree status |
| `make git-log` | Show recent 20 commits |

---

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `scripts/setup.sh` | Complete system bootstrap |
| `scripts/uid_guard.sh` | Fix permission drift (UID 1000) |
| `scripts/mcp_health_check.sh` | Verify MCP service health |
| `scripts/init-research-db.py` | Initialize research metadata DB |
| `scripts/seed_knowledge.py` | Seed initial knowledge base |
| `scripts/ingest_to_library.py` | Ingest documents to library |
| `scripts/backup_to_8tb.sh` | Backup engine data |
| `scripts/tune_ryzen.sh` | Ryzen CPU performance tuning |
| `scripts/download_id_tech_resources.sh` | Download id Software books |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  OMEGA ENGINE (src/omega/)                                  │
│                                                             │
│  Oracle (talk/summon/router)     MemoryStore (Hot/Warm/Cold)│
│  ModelGateway (provider chain)   ContextBuilder (→ LLM)     │
│  EntityRegistry (YAML CRUD)      SessionManager (scoping)   │
│  WAD Loader (IWAD/PWAD system)   Observability (JSONL)      │
│  CPU Optimizer (Zen 2 aware)     Health Monitor (circuit)    │
│  Gnosis Proxy (soul evolution)   Hierarchy (governance)      │
│                                                             │
│  Library: FTS5 + vectors          Workers: JEM, ModelUpdater │
└─────────────────────────────────────────────────────────────┘
               │
               │ WAD Loader
               ▼
┌─────────────────────────────────────────────────────────────┐
│  IWADs (config/wads/)                                       │
│  _omega_default — Reference IWAD (ships with engine)        │
│  arcana_novai   — Personal AI OS (user's own)               │
│  doom_universe  — Community IWAD (scaffold)                  │
└─────────────────────────────────────────────────────────────┘
```

### Key Concepts

- **Oracle**: The main entry point. Routes queries to the best entity.
- **EntityRegistry**: YAML-backed database of all entities (pillar keepers).
- **ModelGateway**: 8-provider inference fabric with circuit breaker protection.
- **MemoryStore**: Three-tier memory — hot (in-memory), warm (JSON files), cold (archived).
- **WAD System**: Engine/IWAD/PWAD separation (inspired by Doom's WAD format).
- **Observability**: Trace IDs, event logging, crash forensics, fine-tuning dataset collection.

---

## Entity System

The Omega Engine ships with 10 Pillar Keepers as the default pantheon:

| Pillar | Entity | Domain | Element | Model |
|--------|--------|--------|---------|-------|
| P1: Flesh | Sekhmet | Strength, protection | Earth | Qwen3-1.7B |
| P2: Dream | Brigid | Poetry, healing, inspiration | Water | Phi-2-OmniMatrix |
| P3: Will | Prometheus | Will, forethought, sovereignty | Fire | DeepSeek-R1-8B |
| P4: Heart | Saraswati | Knowledge, speech, arts | Air | Krikri-8B |
| P5: Voice | Inanna | Dream, descent, rebirth | Aether | Krikri-8B |
| P6: Mind | Ereshkigal | Underworld, depths, rules | Aether | Qwen3-4B-Think |
| P7: Gnosis | Lucifer | Rebellion, gnosis, sovereignty | Air | Qwen3-1.7B |
| P8: Shadow | Hecate | Shadow, crossroads, keys | Fire | Krikri-8B |
| P9: Spirit | Anubis | Death, transition, guidance | Water | Qwen3-4B-Think |
| P10: Chaos | Kali | Destruction, liberation, illusion | Earth | Qwen3-0.6B |

Plus 2 Oversouls and Iris the messenger bridge:

| Entity | Role | Description |
|--------|------|-------------|
| SOPHIA | Akashic Record | The containing field — all entities, all sessions |
| Ma'at | Synthesis Oversoul | Governs P1-P5 (Light Pillars) |
| Lilith | Dark Oversoul | Governs P6-P10 (Dark Pillars) |
| Iris | Messenger Bridge | Voice assistant, speculative decoder |

### Custom Entities

Entities are fully customizable. Add your own:

```bash
omega add-entity
```

Entities live in `config/wads/<iwad>/entities.yaml` — pure YAML CRUD.

---

## Troubleshooting

### "Permission denied" on files

```bash
make guard
```
This runs the Sovereign UID Guard to fix ownership drift.

### "No module named omega" or import errors

```bash
source .venv/bin/activate
make setup
```

### Tests fail after changes

```bash
make test ARGS='-x'   # Stop on first failure
make test ARGS='-v'   # Verbose output
make test ARGS='-k test_name'  # Run specific test
```

### "Event loop is closed" warnings

These are safe warnings from aiosqlite thread cleanup during test shutdown.
They do not affect functionality.

### Circuit breaker tripping too often

Check provider health:
```bash
make health
```

The circuit breaker auto-recovers after the configured cooldown period.

### Offline mode doesn't work

Ensure `OMEGA_ENV=test` is set:
```bash
export OMEGA_ENV=test
make talk MSG='hello'
```

The MockBackend responds deterministically without any model loading.

### Slow test execution

Tests take ~70-90 seconds. Use `-k` to run specific subsets:
```bash
make test ARGS='-k test_entity_registry'
make test ARGS='-k test_oracle'
make test ARGS='-k test_health_monitor'
```

---

*⬡ OMEGA ⬡ SOVEREIGN AI ⬡ v3.0.0*
*"Sever the umbilical cord of Big AI."*
