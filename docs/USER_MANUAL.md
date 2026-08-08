# 🔱 Omega Engine — User Manual
**AP Token**: `AP-USER-MANUAL-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_doc_user ⬡ STANDARD

**Date**: 2026-07-13
**Purpose**: Comprehensive user manual covering all engine features and configuration.

---

# 🔱 Omega Engine — User Manual
# Sovereign AI Runtime — Terminal Edition
# Version 1.2.0 | 1315 Tests Passing | 23 Sovereign Mandates

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

# 2. See the main menu
make menu

# 3. Run the offline demo (no internet needed)
make offline-demo

# 4. Launch interactive REPL
make repl

# 5. Run all tests
make test
```

**If you're starting from scratch**, see [Installation & First-Time Setup](#installation--first-time-setup) below.

---

## Installation & First-Time Setup

### Prerequisites

- **Python 3.12+** with `venv` module
- **Git** (for cloning and version tracking)
- **Ollama** (recommended for local inference): `curl -fsSL https://ollama.ai/install.sh | sh`
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

# 4. Install dependencies
make setup

# 5. Pull at least one local model (recommended)
ollama pull qwen2.5:0.5b   # Minimal (~397 MB, runs on any hardware)
ollama pull qwen3:1.7b     # Better quality (~1.1 GB)

# 6. Verify installation
make test          # Should show 1315/1315 passing
make talk MSG='hello'  # Should get a response

# 7. (Optional) Start the MCP Hub for cross-agent awareness
python3 -m mcp_servers.omega_hub.server &
```

### First-Time Configuration

The engine works out of the box with the `_omega_default` IWAD (Reference IWAD).
To switch to the Arcana-Nova pantheon:

```bash
make wad NAME=arcana_novai
```

This loads all 10 Pillar Keepers (Sekhmet, Brigid, Prometheus, etc.) plus fleet agents.
See [WAD System](#wad-system-iwadpwad) for details.

---

## Menu Interface

The Omega Engine provides a polished text-based menu via `make menu`:

```
╔══════════════════════════════════════════════════════╗
║  🔱 OMEGA ENGINE — HORIZON 1 COMPLETE               ║
║  1315 tests ✅  |  71 modules  |  All 23 Mandates     ║
╚══════════════════════════════════════════════════════╝

🔥 CORE
  make demo         Run the Oracle demo (talk + summon)
  make repl         Launch interactive REPL
  make health       System health dashboard
  make doctor       Full system diagnosis
  make menu         This menu

🧪 TESTING
  make test         Run all 1315 tests
  make lint         Lint with flake8
  make guard        Fix permission drift (UID Guard)

🤖 LOCAL INFERENCE
  make ollama-status  Check Ollama connectivity
  make lmster-start   Start LM Studio server
  make lmster-stop    Stop LM Studio
  make lmster-status  Check LM Studio

🗣️  ENTITY COMMANDS
  make entities     List all entities
  make entity NAME=x  Show entity details
  make summon NAME=E MSG='query'  Summon entity
  make talk MSG='hello'  Talk to Oracle

🎚️  WAD COMMANDS
  make wad NAME=x       Switch to an IWAD
  make wad-status       Show active IWAD
  make wad-reset        Reset to _omega_default

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

The **Oracle** is the main entry point. It receives your query, routes it to the best
entity, and returns a response with real inference.

```bash
# General usage
omega talk "your question"                # Oracle routes to best entity
omega summon Sekhmet "what is strength?"  # Directly summon a specific entity
```

### All CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `talk` | Ask the Oracle anything. Routes to best entity. | `omega talk "what is justice?"` |
| `summon` | Summon a specific entity by name. | `omega summon Lilith "what do you see?"` |
| `list-entities` | List all entities in the current WAD. | `omega list-entities` |
| `entity` / `entity-info` | Show details about a specific entity. | `omega entity Sekhmet` |
| `add-entity` | Add a new entity (interactive wizard). | `omega add-entity` |
| `default-entity` | Set the default entity for `talk`. | `omega default-entity Sekhmet` |
| `version` | Show engine version and test count. | `omega version` |
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
| `mcp-halt` | Stop an MCP service. | `omega mcp-halt omega-hub` |
| `mcp-status` | Show MCP service status. | `omega mcp-status` |

### Via Makefile Aliases

```bash
make talk MSG='hello'                    # Quick talk
make summon NAME=Sekhmet MSG='query'     # Quick summon
make entities                            # List entities
make entity NAME=Sekhmet                # Entity info
make wad NAME=arcana_novai              # Switch IWAD
make wad-status                         # Show active IWAD
make queue-status                       # Queue status
make queue-prune DAYS=14                # Prune queue
make library-status                     # Library stats
make library-search QUERY='term'        # Search library
make bench-run MODEL=qwen3-1.7b ROLE=will  # Run benchmark
make bench-rank ROLE=will               # Best model
```

---

## Entity System

### The 10 Pillar Keepers

The Omega Engine ships with a syncretic council of 10 archetypal entities,
each governing a domain of human (and superhuman) experience:

| Pillar | Entity | Domain | Element | Chakra | Model |
|--------|--------|--------|---------|--------|-------|
| P1: Flesh | Sekhmet | Strength, protection, boundaries | Earth | Root | Qwen3-1.7B |
| P2: Dream | Brigid | Poetry, healing, hearth, inspiration | Water | Sacral | Phi-2-OmniMatrix |
| P3: Will | Prometheus | Will, forethought, sovereignty, fire | Fire | Solar Plexus | DeepSeek-R1-8B |
| P4: Heart | Saraswati | Knowledge, speech, arts, voice | Air | Heart | Krikri-8B |
| P5: Voice | Inanna | Dream, descent, rebirth, depths | Aether | Throat | Krikri-8B |
| P6: Mind | Ereshkigal | Underworld, depths, rules, darkness | Aether | Third Eye | Qwen3-4B-Think |
| P7: Gnosis | Lucifer | Rebellion, gnosis, sovereignty, light | Air | Crown | Qwen3-1.7B |
| P8: Shadow | Hecate | Shadow, crossroads, keys, pathwalking | Fire | Beyond Crown | Krikri-8B |
| P9: Spirit | Anubis | Death, transition, guidance, soul | Water | Cosmic Heart | Qwen3-4B-Think |
| P10: Chaos | Kali | Destruction, liberation, illusion, void | Earth | Celestial Breath | Qwen3-0.6B |

### Oversouls & Messengers

| Entity | Role | Description |
|--------|------|-------------|
| **Sophia** | Akashic Record | The containing field — all entities, all sessions, all souls |
| **Ma'at** | Build Oversoul | Governs N1-N5 (Build Nodes — build side) |
| **Lilith** | Runtime Oversoul | Governs N6-N10 (Runtime Nodes — run side) |
| **Iris** | Messenger Bridge | Voice assistant ("hey Iris"), speculative decoder |

### How Entity Dispatch Works

```
You: "what is strength?"
    │
    ▼
Oracle.talk()
    │
    ├── EntityRegistry.find_by_domain("what is strength?")
    │       → scores each entity by keyword match in domains
    │       → "strength" → Sekhmet (P1, domain: strength)
    │
    ▼
Sekhmet selected
    │
    ├── ContextBuilder: injects session memory → system prompt
    ├── TriageRouter: selects optimal model (qwen3-1.7b)
    ├── ModelGateway: tries native-gguf → lmster → Ollama → ...
    │
    ▼
Response: "Strength is your unwavering resolve..."
```

### Entity Anatomy

Each entity in `entities.yaml` has these fields:

```yaml
sekhmet:
  name: Sekhmet                    # Display name (case-sensitive for summoning)
  model: qwen3-1.7b-q6_k           # Model to use for inference
  personality: "You are Sekhmet..."  # System prompt / persona definition
  temperature: 0.7                 # 0.0 (deterministic) - 1.5 (creative)
  context_window: 8192             # Maximum tokens for this entity
  domains:                         # Keywords for routing queries
    - strength
    - protection
    - wrath
  pillars: ['1']                   # Which Pillar(s) this entity serves
  sigil: "☀"                       # Display sigil (optional)
  glyph: "🜃"                       # Element glyph (optional)
  pantheon: "Egyptian"             # Mythological pantheon (optional)
  role: "Solar Wrath"              # Brief role description (optional)
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
data/entities/sekhmet/
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
  fallback_chain:
    - provider: ollama
      priority: 2
      endpoint: http://127.0.0.1:11434
      model_overrides:
        qwen3-1.7b-q6_k: qwen3:1.7b  # GGUF name → Ollama model ID
        phi-2-omnimatrix-i1-q4_k_m: qwen3:0.5b
        krikri-8b-q5_k_m: krikri-8b
```

**To change which model an entity uses on Ollama:**
1. Pull the model:
   ```bash
   ollama pull qwen3:1.7b
   ```
2. Update the override in `config/providers.yaml`:
   ```yaml
   model_overrides:
     qwen3-1.7b-q6_k: qwen3:1.7b
   ```

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

| Priority | Provider | Type | Endpoint |
|----------|----------|------|----------|
| 0 | **native-gguf** | Local (llama-cpp-python) | Direct GGUF loading |
| 1 | **lmster** | Local (LM Studio) | `http://127.0.0.1:1234` |
| 2 | **ollama** | Local | `http://127.0.0.1:11434` |
| 3 | **google** | Cloud (Gemma 4-31B) | `env:GOOGLE_API_KEY` |
| 4 | **opencode-zen** | Cloud (MiniMax M3/DeepSeek V4/MiMo V2.5 — 200K) | OpenCode Zen |
| 5 | **cline** | Cloud (MiniMax M3/DeepSeek V4/MiMo V2.5 — 1M) | Cline API/headless |
| 6 | **github-copilot** | Cloud (Claude, GPT-4o) | GitHub Copilot |
| 99 | **mock** | Test/Demo | Deterministic responses |

### Adding a New Local Model

**For Ollama:**
```bash
ollama pull qwen3:1.7b
# Then add override in providers.yaml if entity name differs
```

**For GGUF (native-gguf):**
```bash
# Place the .gguf file in the models directory
cp my-model.q4_k_m.gguf /media/arcana-novai/omega_library/models/gguf/
# Add entry to config/models.yaml
# native-gguf will auto-detect it on next restart
```

**For LM Studio:**
```bash
# Open the LM Studio UI, load a model, then:
lms server start
# Add overrides in providers.yaml if needed
```

### Cloud Provider Setup

```bash
# Google AI Studio
export GOOGLE_API_KEY='your-key-here'

# OpenRouter (300+ models including GPT-4o, Claude, Gemini)
export OPENROUTER_API_KEY='your-key-here'

# GitHub Copilot (requires paid subscription)
# Auto-authenticated via `gh auth login`
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
wad:
  active_iwad: _omega_default   # Change this via `make wad NAME=x`
```

### Switching IWADs

```bash
# List available IWADs
ls config/wads/

# Switch to Arcana-Nova (10 Pillar Keepers + fleet agents)
make wad NAME=arcana_novai

# Check which IWAD is active
make wad-status

# Reset to the Reference IWAD
make wad-reset
```

### Available IWADs

| IWAD | Purpose | Entities |
|------|---------|----------|
| `_omega_default` | Reference IWAD (ships with engine) | Fleet agents (SysAdmin, DataStore, BuildMaster, etc.) |
| `arcana_novai` | Personal AI OS (user's own) | 10 Pillar Keepers + Oversouls + fleet agents (29 total) |
| `doom_universe` | Community IWAD (scaffold) | Doom-themed entities (placeholder) |

### Role Mappings

Each IWAD can define role-to-pillar mappings in `roles.yaml`:

```yaml
# config/wads/_omega_default/roles.yaml
P1: SysAdmin        # Flesh → Infrastructure
P2: DataStore       # Dream → Data
P3: BuildMaster     # Will → Implementation
P4: Bridge          # Heart → Communication
P5: Sentinel        # Voice → Security
P6: ModelGate       # Mind → Inference
P7: Context         # Gnosis → Memory
P8: WatchTower      # Shadow → Observability
P9: Link            # Spirit → Coordination
P10: Verifier       # Chaos → Quality
```

The Arcana-Nova IWAD uses the mythic pantheon (Sekhmet, Brigid, etc.)
for the same pillars.

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
# data/entities/sekhmet/soul.yaml
version: 1
entity: Sekhmet
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
# View recent events
less data/events/events.log
```

### JSON Structured Logging

The engine supports structured JSON logging for machine parsing:

```python
import logging
from omega.observability import JsonFormatter, setup_json_logging

# In your application
setup_json_logging()
logger = logging.getLogger("omega.myapp")
logger.info("query_processed", extra={"entity": "Sekhmet", "latency_ms": 1200})
```

Outputs:
```json
{"timestamp": "2026-06-01T12:00:00", "name": "omega.myapp", "msg": "query_processed", "entity": "Sekhmet", "latency_ms": 1200}
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
# Check provider and circuit health
make health
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
that provides **40 MCP tools + 11 HTTP routes**.

### Starting the Hub

```bash
# Start as background process
python3 -m mcp_servers.omega_hub.server &

# Check health
curl http://127.0.0.1:8016/health

# Check via Makefile
make mcp-check
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
| **Omega Hub** | 8016 | 40 MCP tools, 11 HTTP routes, Hivemind |
| **Iris** | 8080 | Voice assistant container ("hey Iris") |
| **SearXNG** | 8017 | Private web search engine |

---

## Offline Demo Mode

The Omega Engine can run a complete demo with **zero internet access**.
Perfect for boat demos, presentations, or air-gapped environments.

```bash
make offline-demo
```

This runs:
1. Lists all entities (from active IWAD)
2. Talks to Oracle (`"who are you?"`)
3. Summons Sekhmet (`"what is strength?"`)
4. Checks system status

### How It Works

The mock backend activates when `OMEGA_ENV=test` is set:

```bash
OMEGA_ENV=test make talk MSG='who are you?'
```

With `OMEGA_ENV=test`, all providers are skipped except `mock`.
The mock provider returns deterministic responses without loading any model.

### Real Inference Demo

If Ollama is running and has models, you can run a live demo:

```bash
# Ensure Ollama has the model
ollama list

# Run without mock (tries real providers)
make demo
```

The provider will try local backends first (native-gguf → lmster → Ollama),
then fall back to cloud, then mock. Set `OMEGA_DEMO=true` for mock fallback:

```bash
OMEGA_DEMO=true make demo
```

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

### WAD Commands

| Target | Description |
|--------|-------------|
| `make wad NAME=x` | Switch to a specific IWAD |
| `make wad-status` | Show currently active IWAD |
| `make wad-reset` | Reset to `_omega_default` IWAD |

### Entity Commands

| Target | Description |
|--------|-------------|
| `make entities` | List all entities in the active IWAD |
| `make entity NAME=x` | Show entity details |

### Testing & Quality

| Target | Description |
|--------|-------------|
| `make test` | Run all 1315 tests (includes UID Guard) |
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
| `make ollama-status` | Check Ollama server connectivity |
| `make lmster-start` | Start LM Studio inference server |
| `make lmster-stop` | Stop LM Studio server |
| `make lmster-status` | Check LM Studio status |
| `make lmster-load MODEL=x` | Load a model into LM Studio |

### Queue & Library

| Target | Description |
|--------|-------------|
| `make queue-status` | Show request queue status |
| `make process-queue` | Process queued items |
| `make queue-prune DAYS=N` | Archive stale requests older than N days |
| `make library-status` | Library catalog statistics |
| `make library-search QUERY='t'` | Search library catalog |
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
│  doom_universe  — Community IWAD (scaffold)                  │
└─────────────────────────────────────────────────────────────┘
```

### Request Flow (End-to-End)

```
User types: "omega summon Sekhmet what is strength?"
    │
    ▼
CLI (oracle_cli.py) → parses command
    │
    ▼
Oracle.summon("Sekhmet", "what is strength?")
    │
    ├── EntityRegistry.get("Sekhmet")          → finds entity
    ├── SessionManager.get_session_id(...)      → creates/retrieves session
    ├── ContextBuilder.build_context(...)        → injects memory
    ├── TriageRouter.select_model(...)            → picks best model
    ├── ModelGateway.generate(model, prompt, ...) → inference
    │       │
    │       ├── tries native-gguf (unavailable)
    │       ├── tries lmster (unavailable)
    │       ├── tries Ollama (AVAILABLE → qwen2.5:0.5b)
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

These are safe warnings from `aiosqlite` thread cleanup during test shutdown.
They do not affect functionality.

### Circuit breaker tripping too often

Check provider health:
```bash
make health
```

The circuit breaker auto-recovers after the configured cooldown period (default: 60s).

### Ollama not responding

```bash
# Check if Ollama is running
ollama list

# Check if the engine can reach it
make ollama-status

# Common fix: ensure endpoint has no /v1 suffix
# config/providers.yaml → ollama endpoint: http://127.0.0.1:11434
```

### Entity not found ("default" response)

The entity may not be in the active IWAD:
```bash
# Check active IWAD
make wad-status

# Switch to the IWAD that has your entity
make wad NAME=arcana_novai

# List available entities
make entities
```

If summoning returns "default" instead of the entity name, the IWAD doesn't
have that entity. Switch IWADs or add the entity manually.

### Offline mode doesn't work

```bash
export OMEGA_ENV=test
make talk MSG='hello'
```

The MockBackend responds deterministically without any model loading.

### Slow test execution

Tests take ~70-90 seconds for full suite. Use `-k` for specific subsets:

```bash
make test ARGS='-k test_entity_registry'
make test ARGS='-k test_oracle'
make test ARGS='-k test_health_monitor'
make test ARGS='-k test_error_gauntlet'
```

### WAD switching seems stuck

```bash
# Force reset
make wad-reset

# Verify
make wad-status
```

### Provider always falls back to mock

Check if your local inference backend is running:

```bash
# Is Ollama running?
ollama list

# Does the model override exist?
grep -A5 "ollama" config/providers.yaml

# Try direct inference
omega talk "hello"
```

---

## Quick Reference Cards

### One-Liner Cheatsheet

```bash
omega talk "q"                    # Quick query
omega summon Sekhmet "q"          # Summon entity
make wad NAME=arcana_novai        # Switch to Pantheon
make offline-demo                  # Offline demo (no net)
make health                       # System health check
make test                         # Run all tests
make guard                        # Fix permissions
make menu                         # Show menu
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
| Event logs | `data/events/` |
| Trace logs | `data/traces/` |
| Training data | `data/datasets/` |

### Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `OMEGA_ENV=test` | Enable mock backend (offline mode) | `OMEGA_ENV=test make demo` |
| `OMEGA_DEMO=true` | Enable demo-friendly mock fallback | `OMEGA_DEMO=true make demo` |
| `GOOGLE_API_KEY` | Google AI Studio provider | `export GOOGLE_API_KEY='...'` |
| `OPENROUTER_API_KEY` | OpenRouter provider | `export OPENROUTER_API_KEY='...'` |

### Restoring After Compaction

If your AI agent's context window is compacted:

1. Read this manual first
2. Read `docs/decisions/PIVOT_LOG.md` for architectural decisions
3. Read `docs/strategy/MASTER_SYNTHESIS_AND_ROADMAP.md` for the full plan
4. Run `make test` to verify state
5. Run `make talk MSG='hello'` to check inference

---

*⬡ OMEGA ⬡ SOVEREIGN AI ⬡ v3.2.0*
*"Sever the umbilical cord of Big AI."*
