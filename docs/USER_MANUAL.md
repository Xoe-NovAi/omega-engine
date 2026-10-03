# 🔱 Omega Engine — User Manual
**AP Token**: `AP-USER-MANUAL-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_doc_user ⬡ STANDARD

**Date**: 2026-07-13
**Purpose**: Comprehensive user manual covering all engine features and configuration.

---

# 🔱 Omega Engine — User Manual
**Sovereign AI Runtime — Terminal Edition**
**Version**: v1.6.0-alpha · **Mandates**: 27 declared (28 rows in the automated meter) · **Last verified**: 2026-10-03

> Every `omega` verb and `make` target in this manual was re-checked against the live
> CLI and the Makefile on 2026-09-19. Where a `make` alias never existed, the `omega`
> equivalent is given instead.

## Table of Contents
1. [Quick Start](#quick-start)
2. [Installation & First-Time Setup](#installation--first-time-setup)
3. [Menu Interface](#menu-interface)
4. [CLI Commands (Oracle)](#cli-commands-oracle)
5. [Entity System](#entity-system)
6. [Model Configuration](#model-configuration)
7. [WAD System (IWAD/PWAD)](#wad-system-iwadpwad)
8. [Soul & Gnosis Preservation](#soul--gnosis-preservation)
9. [Observability & Forensics](#observability--forensics)
10. [Session Headers](#session-headers)
11. [MCP Hub & Services](#mcp-hub--services)
12. [Offline Demo Mode](#offline-demo-mode)
13. [Makefile Reference](#makefile-reference)
14. [Scripts Reference](#scripts-reference)
15. [Architecture Overview](#architecture-overview)
16. [Troubleshooting](#troubleshooting)
17. [Quick Reference Cards](#quick-reference-cards)

---

## Quick Start

```bash
# 1. Enter the environment
cd ~/Documents/Xoe-NovAi/omega-engine
source .venv/bin/activate

# 2. Check local inference and providers
make infer-status
omega model-status

# 3. Talk to your local model (no internet needed)
omega talk "hello"

# 4. Run the fast test tier
make test

# 5. (optional) Add the Ollama local backend
ollama pull qwen3:1.7b

# 6. Refresh the agent Codex (also clears mandate M13)
make codex
```

**If you're starting from scratch**, see [Installation & First-Time Setup](#installation--first-time-setup) below.

---

## Installation & First-Time Setup

### Prerequisites

- **Python 3.12+** with `venv` module
- **Git** (for cloning and version tracking)
- **C compiler** (GCC/Clang) — required to build `llama-cpp-python` for native-gguf inference
- **Ollama** (recommended second local backend): `curl -fsSL https://ollama.ai/install.sh | sh` then `ollama pull qwen3:1.7b`
- **Podman** (optional, for containers): `sudo apt install podman podman-docker`

### Step-by-Step Installation

```bash
# 1. Clone the repository
git clone https://github.com/Xoe-NovAi/omega-engine.git ~/Documents/Xoe-NovAi/omega-engine

# 2. Enter the directory
cd ~/Documents/Xoe-NovAi/omega-engine

# 3. Create and activate a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 4. One-click install (venv + deps + local GGUF model + verification)
./scripts/install.sh

# 5. Verify installation
make test              # Fast unit-tier suite
omega talk "hello"     # Should get a response, fully local

# 7. (Optional) Start the MCP Hub for cross-agent awareness
python3 -m mcp_servers.omega_hub.server &
```

### First-Time Configuration

The engine works out of the box with the `_omega_default` IWAD (Reference IWAD).
To switch to the Arcana-Nova pantheon, edit `config/omega.yaml`:

```yaml
omega:
  entity:
    active_iwad: "arcana_novai"
```

Or override for a single invocation: `omega talk "hello" --iwad arcana_novai`.
This loads the mythological pantheon (Sekhmet, Brigid, Prometheus, ...) plus fleet agents.
See [WAD System](#wad-system-iwadpwad) for details.

---

## Command Surface

There is **no `make menu` target and no interactive menu** in this release. The engine is
driven by the `omega` CLI; `make` targets cover testing, gates, docs, local-inference
servers and dashboards.

```bash
omega --help                  # full command list
omega list-entities           # entities in the active IWAD
omega talk "hello"            # route to the best entity
omega summon ma'at "status"   # direct entity dispatch
omega model-status            # providers + models
omega hardware-stats          # CPU / RAM / thermal
omega queue-status            # pending queue items
```

### Useful `make` targets (all verified in the Makefile)

| Target | Purpose |
|--------|---------|
| `make infer-status` / `infer-health` | native-gguf server state / detailed health |
| `make infer-models` / `infer-memory` | list GGUF models / RAM+swap footprint |
| `make infer-talk MSG='hello'` | smoke-test the running local server |
| `make dashboard` / `dashboard-once` | live provider dashboard / single snapshot |
| `make probe-models` / `probe-network` | free-model availability / network latency |
| `make test` / `test-cov` / `test-debug TEST=x` | unit tier / coverage / single test |
| `make lint` / `check-mandates` | flake8 / mandate gates |
| `make check-mandate-compliance` | full 28-row mandate meter |
| `make codex` / `check-codex-stale` | regenerate the agent Codex / staleness check |
| `make doc-llm-validate` | M26 documentation gate |
| `make heritage-vet` / `heritage-map` | M14 heritage vetting |
| `make check-hub-health` | Omega Hub health probe |

---

## CLI Commands (Oracle)

The **Oracle** is the main entry point. It receives your query, routes it to the best
entity, and returns a response with real inference.

```bash
# General usage
omega talk "your question"                # Oracle routes to best entity
omega summon ma'at "what is your role?"   # Directly summon a specific entity
```

### All CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `talk` | Ask the Oracle anything. Routes to best entity. | `omega talk "what is justice?"` |
| `summon` | Summon a specific entity by name. | `omega summon Lilith "what do you see?"` |
| `list-entities` | List all entities in the current WAD. | `omega list-entities` |
| `entity-info` | Show details about a specific entity. | `omega entity-info ma'at` |
| `add-entity` | Add a new entity (interactive wizard). | `omega add-entity` |
| `default-entity` | Set the default entity for `talk`. | `omega default-entity ma'at` |
| `hardware-stats` | CPU / RAM / thermal snapshot. | `omega hardware-stats` |
| `backends` | List configured providers and their status. | `omega backends` |

### Transient Mode

```bash
omega transient on    # Don't save conversation to memory
omega talk "secret"   # This interaction won't be recorded
omega transient off   # Re-enable memory
```

### Header Mode

```bash
omega header full     # Show ⬡ OMEGA ⬡ session header
omega header minimal  # Compact header
omega header off      # No header
```

### Queue & Library Commands

| Command | Description | Example |
|---------|-------------|---------|
| `queue-status` | Show pending queued/review items. | `omega queue-status` |
| `process-queue` | Process all queued research requests. | `omega process-queue` |
| `review-pending` | Process pending cloud review requests. | `omega review-pending` |
| `queue-prune` | Archive stale requests older than N days. | `omega queue-prune --days 14` |
| `library-curate` | Run domain curation on the library. | `omega library-curate` |
| `library-status` | Show library catalog statistics. | `omega library-status` |
| `library-search` | Search the library catalog. | `omega library-search "quantum"` |

### Benchmark Commands

| Command | Description | Example |
|---------|-------------|---------|
| `bench-run` | Run a benchmark for a model and role. | `omega bench-run qwen3-1.7b will` |
| `bench-compare` | Compare models for a role. | `omega bench-compare will` |
| `bench-rank` | Show the best model for a role. | `omega bench-rank will` |
| `bench-list` | List all completed benchmark runs. | `omega bench-list` |

### MCP Service Commands

| Command | Description | Example |
|---------|-------------|---------|
| `mcp-restart` | Restart an MCP service. | `omega mcp-restart omega-hub` |
| *(make)* `check-hub-health` | Verify Omega Hub health. | `make check-hub-health` |

### Makefile Aliases

There are **no `make` aliases** for `talk`, `summon`, `entities`, `entity`, `wad*`,
`queue-*`, `library-*` or `bench-*` in this release — use the `omega` CLI verbs
directly (they take the same arguments shown above). The `make` surface is reserved for
testing, gates, docs, local-inference servers and dashboards.

---

## Entity System

### Pillar Keepers

The engine's governance layer is held by **three pillar keepers**:

| Pillar Keeper | Role |
|---------------|------|
| **Ma'at** | Build Oversoul — governs the build side of the fleet |
| **Lilith** | Runtime Oversoul — governs the run side of the fleet |
| **Kali** | Grand Oversight — unifies Ma'at + Lilith |

> **Mythological pantheon = `arcana_novai` IWAD only.** Sekhmet, Brigid, Prometheus,
> Saraswati, Inanna, Ereshkigal, Lucifer, Hecate and Anubis live in
> `config/wads/arcana_novai/entities.yaml`, not in the default `_omega_default` IWAD.

### Oversouls & Messengers

| Entity | Role | Description |
|--------|------|-------------|
| **Sophia** | Akashic Record | The containing field — all entities, all sessions, all souls |
| **Ma'at** | Build Oversoul | Governs the build side of the fleet |
| **Lilith** | Runtime Oversoul | Governs the run side of the fleet |
| **Iris** | Messenger Bridge | Voice assistant ("hey Iris"), speculative decoder |

### How Entity Dispatch Works

```
You: "what is strength?"
    │
    ▼
Oracle.talk()
    │
    ├── EntityRegistry.find_by_domain("what is on the system?")
    │       → scores each entity by keyword match in domains
    │       → best match → ma'at (build/oversight)
    │
    ▼
ma'at selected
    │
    ├── ContextBuilder: injects session memory → system prompt
    ├── TriageRouter: selects optimal model (qwen3-1.7b-q6_k)
    ├── ModelGateway: tries native-gguf → Google → OpenRouter → ...
    │
    ▼
Response: "Strength is your unwavering resolve..."
```

### Entity Anatomy

Each entity in `entities.yaml` has these fields:

```yaml
kali:
  name: Kali                       # Display name (case-sensitive for summoning)
  model: qwen3-1.7b-q6_k           # Model to use for inference
  personality: "You are Kali..."    # System prompt / persona definition
  temperature: 0.7                 # 0.0 (deterministic) - 1.5 (creative)
  context_window: 8192             # Maximum tokens per entity
  domains:                         # Keywords for routing queries
    - oversight
    - liberation
    - renewal
  pillars: ['10']                  # Which pillar slot(s) this entity serves
  sigil: "☾"                       # Display sigil (optional)
  glyph: "🜃"                       # Element glyph (optional)
  role: "Grand Oversight"          # Brief role description (optional)
  container: false                 # Whether this entity runs in a container
```

### Creating a Custom Entity

```bash
# Interactive wizard
omega add-entity
```

Or create manually in `config/wads/<iwad>/entities.yaml`:

```yaml
my_custom_entity:
  name: MyEntity
  model: qwen3-1.7b-q6_k
  personality: "You are a helpful assistant..."
  temperature: 0.7
  context_window: 8192
  domains:
    - help
    - general
  pillars: []
  sigil: "✦"
```

Entities live in `config/wads/<iwad>/entities.yaml` — pure YAML CRUD, no database required.

### Entity Workspace (Soul)

When an entity is first summoned, the engine creates a workspace at
`data/entities/<name>/`:

```
data/entities/kali/
├── soul.yaml           # L1→L2→L3 gnosis, model preferences, routing history
├── knowledge/          # Entity-specific knowledge files
└── workspace/          # Working files
```

See [Soul & Gnosis Preservation](#soul--gnosis-preservation) for details.

---

## Model Configuration

The Omega Engine uses a **two-tier** model configuration system:
entity models (what the entity wants) + provider overrides (what's available).

### Entity Models (Desired)

Each entity declares its ideal model in `config/wads/<iwad>/entities.yaml`:

```yaml
sekhmet:
  name: Sekhmet
  model: qwen3-1.7b-q6_k  # The GGUF model name for this entity
  temperature: 0.7
  context_window: 8192
```

**To change an entity's model:**
```bash
# Edit the entities.yaml for your active IWAD
vim config/wads/arcana_novai/entities.yaml

# Or use the CLI (interactive)
omega add-entity
```

### Provider Model Overrides (Available)

When using local inference backends, GGUF model names must be mapped to
provider-specific identifiers. This is configured in `config/providers.yaml`:

```yaml
inference:
  strategy: local_first
  providers:
    native-gguf:            # primary local provider (llama-cpp-python)
      priority: 0
      enabled: true
    google:
      priority: 4
      enabled: true
```

**To change which model an entity uses (native-gguf):**
1. Download or add the GGUF:
   ```bash
   ./scripts/download_model.sh          # default Qwen3-1.7B-Q6_K
   ```
2. Set the entity's `model:` in `config/wads/<iwad>/entities.yaml` and register the
   file in `config/models.yaml`.

### Model Selection Flow

```
Entity Model (entities.yaml)
    ↓
TriageRouter (selects best model based on domain/health/metrics)
    ↓
ModelGateway (tries providers in priority order)
    ↓
Provider (applies model_overrides if local backend)
    ↓
Inference (actual model execution)
```

### Provider Priority Order (Local-First)

Priorities live in `config/providers.yaml` (`inference.providers`). This release defines
**12 providers and enables 10** — `ollama` and `mock` are `enabled: false`.

| Priority | Provider | Type |
|----------|----------|------|
| 0 | **native-gguf** | Local — llama-cpp-python (primary) |
| 2 | **ollama** | Local — `http://127.0.0.1:11434` (set `enabled: true`) |
| 3 | **antigravity** | Cloud |
| 4 | **google** | Cloud (Gemma) |
| 4 | **google-compat** | Cloud (Gemma, compat endpoint) |
| 5 | **openrouter** | Cloud (300+ models) |
| 6 | **opencode-zen** | Cloud (CLI) |
| 7 | **cline** | Cloud (CLI) |
| 8 | **anthropic** | Cloud (Claude) |
| 9 | **xai** | Cloud (Grok) |
| 10 | **mock** | Test/demo (`enabled: false`; active only in `OMEGA_ENV=test`) |

> Priority 1 (`lmster` / LM Studio) is **deferred to a post-release update**.
> There is no `github-copilot` provider in this release.

### Adding a New Local Model

**Recommended — native-gguf (default path):**
```bash
./scripts/download_model.sh            # Qwen3-1.7B-Q6_K -> $OMEGA_MODELS_DIR
make infer-models                      # verify it is discovered
```

**For GGUF (native-gguf):**
```bash
# Place the .gguf file in the models directory
cp my-model.q4_k_m.gguf models/gguf/   # or $OMEGA_MODELS_DIR (set in .env by install.sh)
# Register it in config/models.yaml — native-gguf auto-detects on next start
```

**Ollama:** second local backend — install it, `ollama pull qwen3:1.7b`, Ollama is enabled by default in `config/providers.yaml`.

**LM Studio (`lmster`):** removed from this release; returns in a post-release update.

### Cloud Provider Setup

```bash
# Google AI Studio
export GOOGLE_API_KEY='your-key-here'

# OpenRouter (300+ models including GPT-4o, Claude, Gemini)
export OPENROUTER_API_KEY='your-key-here'

# Anthropic (Claude)
export ANTHROPIC_API_KEY='your-key-here'

# xAI (Grok)
export XAI_API_KEY='your-key-here'
```

---

## WAD System (IWAD/PWAD)

The Omega Engine uses a **WAD system** inspired by Doom's architecture:
the **engine** is separate from **content packs** (IWADs/PWADs).

| Term | Meaning | Example |
|------|---------|---------|
| **Engine** | The core runtime (`src/omega/`) — universal, stack-agnostic | EntityRegistry, ModelGateway, Oracle |
| **IWAD** | "Internal WAD" — a complete content pack with entities, config, knowledge | `arcana_novai` — the user's personal AI OS |
| **PWAD** | "Patch WAD" — an incremental layer that overrides parts of an IWAD | A community entity pack |

### Active IWAD

The active IWAD determines which entities are loaded. Only **one** IWAD is
active at a time (set in `config/omega.yaml`):

```yaml
omega:
  entity:
    active_iwad: "_omega_default"   # "arcana_novai" | "omega_research" | "ingestion"
```

### Switching IWADs

```bash
# List available IWADs
ls config/wads/

# Switch to Arcana-Nova: edit config/omega.yaml -> omega.entity.active_iwad: "arcana_novai"

# Check which IWAD is active
grep -A2 'omega:' config/omega.yaml

# Reset to the reference IWAD: active_iwad: "_omega_default"

# Or override for a single invocation
omega talk "hello" --iwad arcana_novai
```

### Available IWADs

| IWAD | Purpose | Entities |
|------|---------|----------|
| `_omega_default` | Reference IWAD (**active by default**) | 14: iris, kali, ma'at, lilith, jem, verity, makali, researcher, roc racoon, doom guy, john carmack, scribe, quality, default |
| `arcana_novai` | Personal AI OS — mythological pantheon + fleet | 35 (sekhmet, brigid, prometheus, saraswati, inanna, ereshkigal, lucifer, hecate, anubis, isis, sysadmin, datastore, buildmaster, bridge, modelgate, …) |
| `omega_research` | Research stack | see `config/wads/omega_research/entities.yaml` |
| `ingestion` | Ingestion stack | see `config/wads/ingestion/` |

**No `doom_universe` IWAD ships in this release.**

### Summonable Entities

Use `omega list-entities` for the authoritative roster. The default `_omega_default`
IWAD ships the fleet: iris, kali, ma'at, lilith, jem, verity, makali, researcher,
roc racoon, doom guy, john carmack, scribe, quality.

---

## Soul & Gnosis Preservation

Every entity has a **soul** — a persistent file at `data/entities/<name>/soul.yaml`
that accumulates wisdom across sessions. This is Mandate 11 (Soul Integrity).

### The L1 → L2 → L3 Abstraction Pipeline

| Level | Name | Content | Size |
|-------|------|---------|------|
| **L1** | Narrative | What happened? Raw interaction records. | Large |
| **L2** | Insight | What does this mean? Pattern recognition. | Medium |
| **L3** | Universal Principle | What is the timeless truth? | Small (1-3 sentences) |

### Soul File Structure

```yaml
# data/entities/kali/soul.yaml
version: 1
entity: Kali
created: 2026-06-01
updated: 2026-06-01

lessons:          # L1 → L2 → L3 pipeline results
  - l1: "User asked about the nature of strength"
    l2: "Strength is not just physical — it requires resolve and will"
    l3: "True strength is the resolve to act despite fear"

model_preferences:
  by_domain:
    strength: [qwen3-1.7b, qwen3-4b-thinking]
    poetry: [krikri-8b]

routing_history:
  - query: "what is strength?"
    task_domain: strength
    selected_model: qwen3-1.7b-q6_k
    confidence: 0.85
    timestamp: 2026-06-01T12:00:00Z
```

### How Gnosis Flows

```
Session interaction
    ↓
MemoryStore captures exchange (add_exchange)
    ↓
Scribe agent distills L1→L2→L3 (end of session)
    ↓
soul.yaml updated with new lessons
    ↓
Next session → ContextBuilder injects soul wisdom → better responses
```

**Without soul updates, the engine regresses to a stateless tool.**
**With them, it evolves from tool into sovereign intelligence.**

---

## Observability & Forensics

Every interaction is traced, logged, and recoverable.

### Trace IDs

Every `talk` and `summon` generates a unique `trace_id` (UUID4) that is
passed through the entire call chain:

```
trace_id=c7a3b8f1-... → Oracle → TriageRouter → ModelGateway → Providers
```

This makes it possible to debug any failed interaction:

```bash
# Check recent traces
less data/traces/2026-06-01.jsonl

# Search for a specific trace
grep "c7a3b8f1" data/traces/*.jsonl
```

### Event Logging

All significant events are logged with timestamps, entity names, model names,
and trace IDs:

```bash
# Lifecycle / inference events
make infer-events

# Trace files (JSONL)
ls data/traces/ | tail -5
```

### JSON Structured Logging

The engine supports structured JSON logging for machine parsing:

```python
import logging
from omega.observability import JsonFormatter, setup_json_logging

# In your application
setup_json_logging()
logger = logging.getLogger("omega.myapp")
logger.info("query_processed", extra={"entity": "kali", "latency_ms": 1200})
```

Outputs:
```json
{"timestamp": "2026-06-01T12:00:00", "name": "omega.myapp", "msg": "query_processed", "entity": "kali", "latency_ms": 1200}
```

### Forensics Manager (Crash Recovery)

The ForensicsManager provides crash dump, replay, and learn capabilities:

```
ForensicsManager
├── snapshot()  → Captures full engine state to data/crash_dumps/
├── replay()    → Replays a crash dump through the call chain
├── learn()     → Extracts L1→L2→L3 lessons from crash patterns
└── recent_events(n) → Returns last N events from ring buffer
```

### Health Monitoring

The `HealthMonitor` tracks provider health with a circuit breaker pattern:

| State | Meaning | Behavior |
|-------|---------|----------|
| **CLOSED** | Healthy | Normal operation |
| **OPEN** | Failing | Skip provider (O(1) check) |
| **HALF_OPEN** | Testing | Allow one probe request |

```bash
# Check local inference + provider state
make infer-status
omega model-status
```

Each provider has configurable thresholds:
- `failure_threshold`: Failures before circuit opens (default: 3)
- `cooldown_period`: Seconds before retry (default: 60)
- `success_threshold`: Successes before circuit closes (default: 2)

---

## Session Headers

All agent outputs MUST include a session header in this format:

```
⬡ OMEGA ⬡ {entity} ⬡ {model} ⬡ {channel} ⬡ {trace} ⬡ {phase}
```

Example:

```
⬡ OMEGA ⬡ SOPHIA ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_horizon1 ⬡ PHASE-I
```

| Field | Meaning | Examples |
|-------|---------|----------|
| **Entity** | The active entity/agent | `SOPHIA`, `KALI`, `MAAT`, `SEKHMET` |
| **Model** | The model generating output | `deepseek-v4-flash`, `mimo-v2.5`, `gemma-4-31b` |
| **Channel** | The agent platform | `opencode`, `gemini-cli`, `cline` |
| **Trace** | Session trace ID | `trc_horizon1`, `trc_provider_fix` |
| **Phase** | Current execution phase | `PHASE-I`, `PHASE-II`, `HORIZON-1` |

To control header display in CLI output:

```bash
omega header full      # Show full ⬡ header
omega header minimal   # Compact header
omega header off       # No header
```

---

## MCP Hub & Services

The Omega Hub (`http://127.0.0.1:8016`) is a cross-agent communication server
that exposes **100+ MCP tools** plus HTTP routes (Hivemind, library, oracle, research, federation).

### Starting the Hub

```bash
# Start as background process
python3 -m mcp_servers.omega_hub.server &

# Check health
curl http://127.0.0.1:8016/health

# Check via Makefile
make check-hub-health
```

### Key Endpoints

| Route | Method | Purpose |
|-------|--------|---------|
| `/health` | GET | Service health + uptime |
| `/routes` | GET | List all registered routes |
| `/hivemind/heartbeat` | POST | Register agent presence |
| `/sse` | GET | SSE transport for MCP clients |

### Hivemind (Cross-CLI Awareness)

The Hivemind allows agents across different CLIs (OpenCode, Cline, Gemini)
to share context:

```bash
# Oracle posts interactions to Hivemind automatically
omega talk "hello"    # → posted to Hivemind

# Other agents can read recent interactions
curl http://127.0.0.1:8016/hivemind/recent
```

### MCP-Enabled Services

| Service | Port | Purpose |
|---------|------|---------|
| **Omega Hub** | 8016 | 100+ MCP tools, HTTP routes, Hivemind |
| **Iris** | 8080 | Voice assistant container ("hey Iris") |
| **SearXNG** | 8017 | Private web search engine |

---

## Offline / Test Mode

The engine runs fully offline with a deterministic mock backend — useful for demos,
presentations and air-gapped machines.

```bash
export OMEGA_ENV=test
omega talk "who are you?"     # deterministic mock response, no model loaded
```

With `OMEGA_ENV=test` only the mock provider answers. Unset it (or open a new shell) to
return to real local inference.

### Real local inference

```bash
make infer-status                    # is the native-gguf server up?
make infer-talk MSG='who are you?'   # smoke-test the running local server
omega talk "who are you?"            # full Oracle path (routing + memory + soul)
```

> There is **no `make offline-demo`, `make demo` or `make repl`** target in this release.

---

## Makefile Reference

The Makefile is organised by domain. Every target below exists — verify with
`make help` or `grep -E '^[a-z-]+:' Makefile`.

### Testing

| Target | Purpose |
|--------|---------|
| `make test` | Fast unit tier (parallel, stops on first failure) |
| `make test-all` | Full suite, parallel, short tracebacks |
| `make test-debug TEST=<pattern>` | Single test, verbose (`-k` match) |
| `make test-cov` | Coverage report |
| `make test-prepush` | Fast + only affected tests (testmon) |
| `make test-clarity` / `test-summary` / `test-json` | Enhanced / terse / JSON output |
| `make test-random` / `test-flake-hunt` | Randomized ordering to expose flakes |

### Local inference (native-gguf)

| Target | Purpose |
|--------|---------|
| `make infer-start` / `infer-stop` / `infer-restart` | Start / stop / restart native-gguf servers |
| `make infer-status` / `infer-health` / `infer-debug` | State / detailed health / full debug dump |
| `make infer-models` | List available GGUF models |
| `make infer-memory` | RAM + swap footprint of loaded models |
| `make infer-talk MSG='hello'` | Smoke-test the running server |
| `make infer-logs LOG=extractor` / `infer-events` | Tail logs / lifecycle events |

### Gates & compliance

| Target | Purpose |
|--------|---------|
| `make check-mandates` | Core mandate gates (M1, M7, M8, M9, M22, M23) |
| `make check-mandate-compliance` | Full 28-row mandate meter |
| `make temple-grade` | Temple-Grade chain (⚠️ decorative until PR-H wiring lands) |
| `make lint` | flake8 (F821 enforced) |
| `make doc-llm-validate` | M26 documentation gate |
| `make heritage-vet` / `heritage-map` | M14 heritage vetting / tag map |
| `make check-m1-anyio` / `check-m8-zero-telemetry` / `check-m23-failure-integrity` | Individual mandate checks |
| `make check-tracking-state` | M27 tracking integrity |
| `make check-hub-health` | Omega Hub health probe |
| `make check-broken-imports` | Import sanity scan |

### Codex, dashboards & probes

| Target | Purpose |
|--------|---------|
| `make codex` | Regenerate `OMEGA_CODEX.md` |
| `make check-codex-stale` / `check-codex-fix` | Staleness check / auto-regenerate |
| `make dashboard` / `dashboard-once` | Live provider dashboard / single snapshot |
| `make probe-models` / `probe-network` / `probe-antigravity` | Free-model / network / quota probes |

### Maintenance

| Target | Purpose |
|--------|---------|
| `make clean` | Remove generated files |
| `make observe CMD='<cmd>'` / `install-guarded` | Observability wrapper / RAM-guarded install |
| `make sweep-tasks` | Sweep stale task state |
| `make sote-index` / `sote-digest` / `sote-validate` | SOTE state-of-engine pipeline |

> **No `make` aliases exist for** `talk`, `summon`, `menu`, `demo`, `offline-demo`, `repl`,
> `health`, `doctor`, `setup`, `guard`, `wad*`, `entities`, `entity`, `ollama-status`,
> `lmster-*`, `test-badge`, `mcp-check`, `start-infra`, `stop-infra`, `restart-infra`,
> `queue-*`, `library-*` or `bench-*`. Use the `omega` CLI verbs documented above;
> containers are quadlet/Podman-managed (`podman ps -a`).

---

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `scripts/install.sh` | One-click install (venv + deps + model + verification) |
| `scripts/download_model.sh` | Download/verify the default local GGUF model |
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
│  OMEGA ENGINE (src/omega/) — THE RUNTIME                   │
│                                                             │
│  Oracle (talk/summon/router)     MemoryStore (Hot/Warm/Cold)│
│  ModelGateway (provider chain)   ContextBuilder (→ LLM)     │
│  EntityRegistry (YAML CRUD)      SessionManager (scoping)   │
│  WAD Loader (IWAD/PWAD system)   Observability (JSONL)      │
│  CPU Optimizer (Zen 2 aware)     Health Monitor (circuit)   │
│  Gnosis Proxy (soul evolution)   Sovereignty (governance)    │
│                                                             │
│  Library: FTS5 + vectors         Workers: JEM, ModelUpdater │
│  MCP Hub: agent bus + Hivemind   Bridge: CLI/API transport  │
└─────────────────────────────────────────────────────────────┘
               │
               │ WAD Loader
               ▼
┌─────────────────────────────────────────────────────────────┐
│  IWADs (config/wads/)                                       │
│  _omega_default — Reference IWAD (ships with engine)        │
│  arcana_novai   — Personal AI OS (user's own)               │
│  omega_research — Research stack                             │
│  ingestion      — Ingestion stack                            │
└─────────────────────────────────────────────────────────────┘
```

### Request Flow (End-to-End)

```
User types: "omega summon ma'at what is on the system?"
    │
    ▼
CLI (oracle_cli.py) → parses command
    │
    ▼
Oracle.summon("ma'at", "what is on the system?")
    │
    ├── EntityRegistry.get("ma'at")           → finds entity
    ├── SessionManager.get_session_id(...)      → creates/retrieves session
    ├── ContextBuilder.build_context(...)        → injects memory
    ├── TriageRouter.select_model(...)            → picks best model
    ├── ModelGateway.generate(model, prompt, ...) → inference
    │       │
    │       ├── tries native-gguf (PRIMARY → qwen3-1.7b-q6_k)
    │       ├── cloud fallbacks only if local fails AND keys are set
    │       └── returns response
    │
    ├── MemoryStore.add_exchange(...)            → saves to memory
    ├── Hivemind.post_interaction(...)           → shares with fleet
    ├── Observability log_event(...)             → traces everything
    │
    ▼
"Strength is your unwavering resolve..." 🡐 response to user
```

### Key Concepts

| Concept | File | Purpose |
|---------|------|---------|
| **Oracle** | `oracle/oracle.py` | Main entry — talk, summon, route |
| **EntityRegistry** | `oracle/entity_registry.py` | YAML-backed entity CRUD |
| **ModelGateway** | `oracle/model_gateway.py` | 9-provider fabric with circuit breakers |
| **MemoryStore** | `memory_store.py` | Hot (RAM) / Warm (JSON) / Cold (archive) |
| **WAD Loader** | `oracle/wad_loader.py` | IWAD/PWAD engine-stack firewall |
| **Observability** | `observability.py` | Trace IDs, JSON logging, crash forensics |
| **Health Monitor** | `oracle/health_monitor.py` | Circuit breaker, provider health, latency |
| **Triage Router** | `orchestration/triage_router.py` | Model selection by domain/health |
| **CPU Optimizer** | `oracle/cpu_optimizer.py` | Zen 2 tuning, KV cache sizing |
| **Session Manager** | `oracle/session_manager.py` | Entity-scoped rolling sessions |
| **Request Queue** | `request_queue.py` | Offline queue with heartbeat/dead-letter |
| **Benchmark Runner** | `benchmarks/runner.py` | 3-point per-criterion scoring |
| **Library Catalog** | `library/catalog.py` | SQLite FTS5 + 5D quality scoring |
| **Omega Hub** | `mcp_servers/omega_hub/server.py` | 40 MCP tools, Hivemind, SSE transport |

---

## Troubleshooting

### "Permission denied" on files

```bash
ls -la data/ config/ | head -20
sudo chown -R "$(id -u):$(id -g)" data/ config/
```
Fix ownership of project files (UID 1000). Containers must run with `UserNS=keep-id` (M6).

### "No module named omega" or import errors

```bash
source .venv/bin/activate
pip install -e ".[native,cli]"
```

### Tests fail after changes

```bash
make test                        # unit tier, stops on first failure
make test-debug TEST=test_name   # single test, verbose
make test-all                    # whole suite, parallel
```

### "Event loop is closed" warnings

These are safe warnings from `aiosqlite` thread cleanup during test shutdown.
They do not affect functionality.

### Circuit breaker tripping too often

Check provider health:
```bash
make infer-status
omega model-status
```

The circuit breaker auto-recovers after the configured cooldown period (default: 60s).

### Local inference not responding

```bash
make infer-status      # native-gguf server state
make infer-health      # status + memory + log tail
omega model-status     # providers + models
```
> Ollama is **enabled by default** in this release
> (`config/providers.yaml` → `providers.ollama.enabled: true`).

### Entity not found ("default" response)

The entity may not be in the active IWAD:
```bash
# Check active IWAD
grep -A2 'omega:' config/omega.yaml

# Load the IWAD that has your entity
omega talk "hello" --iwad arcana_novai

# List available entities
omega list-entities
```

If summoning returns "default" instead of the entity name, the IWAD doesn't
have that entity. Switch IWADs or add the entity manually.

### Offline mode doesn't work

```bash
export OMEGA_ENV=test
omega talk "hello"
```

The MockBackend responds deterministically without any model loading.

### Slow test execution

Use a targeted run instead of the whole suite:

```bash
make test-debug TEST=test_entity_registry
make test-debug TEST=test_oracle
make test-debug TEST=test_health_monitor
make test-debug TEST=test_error_gauntlet
```

### IWAD switching seems stuck

IWADs are selected in `config/omega.yaml` — there is no `make wad*` target:
```bash
# Show the active IWAD
grep -A2 'omega:' config/omega.yaml

# Switch by editing: omega.entity.active_iwad
# Or per invocation: omega talk "hello" --iwad arcana_novai
```

### Provider always falls back to mock

Check the local inference backend:

```bash
make infer-status      # native-gguf server state
make infer-models      # are GGUF models present?
omega model-status     # which providers are enabled?

# Try direct inference
omega talk "hello"
```

---

## Quick Reference Cards

### One-Liner Cheatsheet

```bash
omega talk "q"                    # Quick query
omega summon ma'at "q"               # summon an entity
omega talk "q" --iwad arcana_novai    # load a specific IWAD
OMEGA_ENV=test omega talk "q"         # offline (mock) response
make infer-status                     # native-gguf server health
make test                             # unit-tier tests
make check-mandate-compliance         # mandate meter
make infer-models                     # list local GGUF models
```

### File Locations

| What | Where |
|------|-------|
| Engine source | `src/omega/` |
| IWAD entities | `config/wads/<name>/entities.yaml` |
| Provider config | `config/providers.yaml` |
| Model specs | `config/models.yaml` |
| Engine config | `config/omega.yaml` |
| Entity souls | `data/entities/<name>/soul.yaml` |
| Sessions | `data/sessions/<entity>.active` |
| Crash dumps | `data/crash_dumps/` |
| Benchmarks | `data/benchmarks/` |
| Request queue | `data/requests/` |
| Library | `data/library/documents/` |
| Inference events | `make infer-events` |
| Trace logs | `data/traces/` |
| Training data | `data/datasets/` |

### Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `OMEGA_ENV=test` | Enable the mock backend (offline mode) | `OMEGA_ENV=test omega talk "hello"` |
| `OMEGA_DEMO=true` | Allow mock fallback in demo runs | `OMEGA_DEMO=true omega talk "hello"` |
| `GOOGLE_API_KEY` | Google AI Studio provider | `export GOOGLE_API_KEY='...'` |
| `OPENROUTER_API_KEY` | OpenRouter provider | `export OPENROUTER_API_KEY='...'` |

### Restoring After Compaction

If your AI agent's context window is compacted:

1. Read this manual first
2. Read `docs/decisions/PIVOT_LOG.md` for architectural decisions
3. Read `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` and `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md`
4. Run `make test` to verify state
5. Run `omega talk "hello"` to check inference

---

*⬡ OMEGA ⬡ USER-MANUAL ⬡ v1.6.0-alpha ⬡ 2026-10-03*
*"Sever the umbilical cord of Big AI."*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
