# 🔱 CLI — Omega Engine Command-Line Interface
**AP Token**: `AP-CLI-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Reference documentation for the CLI package — command-line tools for vault management, bundle operations, fleet status, Oracle interaction, soul staging, YouTube worker, and local queue.
**Tags**: cli, vault, bundle, fleet, oracle, soul, youtube, queue
**Cross-references**: src/omega/cli/vault.py, src/omega/cli/bundle.py, src/omega/cli/fleet_status_tui.py, src/omega/cli/oracle_cli.py, src/omega/cli/soul_stage.py, src/omega/cli/youtube_cli.py, src/omega/cli/local_queue.py

---

## Overview

The `cli` package provides **command-line interfaces** for operational tasks in the Omega Engine. Each module is a standalone CLI tool with its own argument parsing and execution logic.

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI Package                             │
├─────────────────────────────────────────────────────────────┤
│  vault.py            │  VaultCore credential management     │
│  bundle.py           │  WAD bundle creation/inspection      │
│  fleet_status_tui.py │  Terminal UI for fleet status        │
│  oracle_cli.py       │  Direct Oracle interaction           │
│  soul_stage.py       │  Soul distillation staging           │
│  youtube_cli.py      │  YouTube worker control              │
│  local_queue.py      │  Local worker queue management       │
└─────────────────────────────────────────────────────────────┘
```

---

## vault.py — VaultCore Credential Management

Manage encrypted credentials in VaultCore.

### Commands

```bash
# List all credentials
python -m omega.cli.vault list

# Get a credential (decrypts to stdout)
python -m omega.cli.vault get <credential_id>

# Set a credential (encrypts from stdin or --value)
python -m omega.cli.vault set <credential_id> --value "secret"
echo "secret" | python -m omega.cli.vault set <credential_id>

# Delete a credential
python -m omega.cli.vault delete <credential_id>

# Rotate master key
python -m omega.cli.vault rotate-key
```

### Usage Example

```bash
# Store OpenRouter API key
echo "sk-or-v1-..." | python -m omega.cli.vault set openrouter:api_key

# Retrieve for use in scripts
API_KEY=$(python -m omega.cli.vault get openrouter:api_key)
```

---

## bundle.py — WAD Bundle Operations

Create, inspect, and validate WAD (Where's All Data) bundles — the Omega Engine's content distribution format (heritage: id Software WAD system).

### Commands

```bash
# Create a bundle from directory
python -m omega.cli.bundle create <source_dir> <output.wad> --name "My WAD" --version "1.0.0"

# Inspect bundle contents
python -m omega.cli.bundle inspect <bundle.wad>

# Validate bundle structure
python -m omega.cli.bundle validate <bundle.wad>

# Extract bundle
python -m omega.cli.bundle extract <bundle.wad> <output_dir>
```

### Bundle Structure

```
bundle.wad
├── manifest.json          # Metadata: name, version, author, dependencies
├── content/               # Content files (configs, models, prompts)
│   ├── entities/
│   ├── skills/
│   └── configs/
└── signatures/            # Cryptographic signatures (optional)
```

---

## fleet_status_tui.py — Fleet Status Terminal UI

Real-time terminal dashboard for monitoring the Omega fleet (entities, workers, queue, resources).

### Usage

```bash
# Launch TUI
python -m omega.cli.fleet_status_tui

# Key bindings:
#   q / Ctrl+C  — Quit
#   r           — Refresh
#   1-9         — Switch tabs
#   ↑/↓         — Navigate lists
#   Enter       — Drill down
```

### Tabs

| Tab | Content |
|-----|---------|
| 1. Overview | System health, resource usage, active entities |
| 2. Entities | Entity status, current task, session info |
| 3. Workers | Background worker status, cycles, metrics |
| 4. Queue | Handoff queue depth, pending/completed |
| 5. Resources | CPU, memory, GPU, disk, network |
| 6. Logs | Recent structured logs |

---

## oracle_cli.py — Direct Oracle Interaction

Interact with the Omega Oracle directly from command line.

### Commands

```bash
# Talk to Oracle (routes via Iris)
python -m omega.cli.oracle_cli talk "What is the Engine-Stack Firewall?"

# Summon specific entity
python -m omega.cli.oracle_cli summon Prometheus "Harden the container security"

# List entities
python -m omega.cli.oracle_cli entities

# Check entity soul
python -m omega.cli.oracle_cli soul Prometheus

# Health check
python -m omega.cli.oracle_cli health
```

### Options

```bash
# Transient mode (no memory persistence)
python -m omega.cli.oracle_cli talk "One-off query" --transient

# Specify session
python -m omega.cli.oracle_cli talk "Continue..." --session ses_abc123

# JSON output
python -m omega.cli.oracle_cli talk "Query" --json
```

---

## soul_stage.py — Soul Distillation Staging

Stage and review proposed soul lessons before Scribe canonicalization.

### Commands

```bash
# List proposed lessons for entity
python -m omega.cli.soul_stage list Prometheus

# Review a specific lesson
python -m omega.cli.soul_stage show Prometheus lesson_001

# Approve lesson (moves to Scribe queue)
python -m omega.cli.soul_stage approve Prometheus lesson_001

# Reject lesson
python -m omega.cli.soul_stage reject Prometheus lesson_001 --reason "Duplicate of L3-042"

# Export all proposed lessons
python -m omega.cli.soul_stage export Prometheus --format json
```

### Lesson Format

```yaml
# proposed_lessons.yaml entry
- principle: "Always validate provider provenance from response, not intent"
  level: 3
  source_session: "ses_abc123"
  source_entity: "Prometheus"
  confidence: 0.95
  tags: ["M22", "provenance", "security"]
  created_at: "2026-10-02T14:30:00Z"
```

---

## youtube_cli.py — YouTube Worker Control

Control the YouTube background worker (ingestion, synthesis, daemon).

### Commands

```bash
# Run one ingestion cycle
python -m omega.cli.youtube_cli --once

# Run as daemon (with watchdog, CPU ceiling)
python -m omega.cli.youtube_cli --daemon --cpu-ceiling 85 --interval 5

# Submit URL to queue
python -m omega.cli.youtube_cli --queue-url "https://youtube.com/watch?v=..."

# Expand and ingest playlist
python -m omega.cli.youtube_cli --playlist "https://youtube.com/playlist?list=..."

# Search and ingest by topic
python -m omega.cli.youtube_cli --topic "sovereign AI 2026"

# Batch process from file
python -m omega.cli.youtube_cli --file urls.txt --batch --batch-size 10

# Show worker status
python -m omega.cli.youtube_cli --status
```

### Daemon Options

| Option | Default | Description |
|--------|---------|-------------|
| `--cpu-ceiling` | 85.0 | Throttle if CPU exceeds % |
| `--interval` | 5.0 | Seconds between cycles |
| `--max-cycles` | 0 | Max cycles (0=unlimited) |
| `--config` | config/youtube_worker.yaml | Config file path |

---

## local_queue.py — Local Worker Queue Management

Manage the local worker queue (fire-and-forget GGUF inference tasks).

### Commands

```bash
# Submit task to local queue
python -m omega.cli.local_queue submit "Summarize this research paper" --model qwen3-1.7b

# List tasks
python -m omega.cli.local_queue list --status queued

# Get task status
python -m omega.cli.local_queue status <task_id>

# Get task result
python -m omega.cli.local_queue result <task_id>

# Cancel task
python -m omega.cli.local_queue cancel <task_id>
```

### Task Lifecycle

```
QUEUED → RUNNING → COMPLETED | FAILED
```

---

## Common Patterns

### Environment Variables

All CLI tools respect:

| Variable | Description |
|----------|-------------|
| `OMEGA_DATA_DIR` | Override data directory (default: repo root/data) |
| `OMEGA_CONFIG_DIR` | Override config directory |
| `VAULT_MASTER_KEY` | Vault encryption key |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Resource not found |
| 4 | Permission denied |
| 5 | Vault/encryption error |

### JSON Output

Most commands support `--json` for machine-readable output:

```bash
python -m omega.cli.vault list --json
# [{"id": "openrouter:api_key", "created": "2026-01-15T10:30:00Z", "tags": ["api"]}]
```

---

## Usage Examples

```bash
# Full workflow: store credential, create bundle, deploy
python -m omega.cli.vault set openrouter:api_key --value "$OPENROUTER_KEY"
python -m omega.cli.bundle create ./my_wad_content my_wad.wad --name "My WAD" --version "1.0.0"
python -m omega.cli.bundle validate my_wad.wad

# Operational monitoring
python -m omega.cli.fleet_status_tui

# Quick Oracle query
python -m omega.cli.oracle_cli talk "Explain the Sovereign Mandates" --json

# Soul governance
python -m omega.cli.soul_stage list Prometheus
python -m omega.cli.soul_stage approve Prometheus lesson_005

# Background processing
python -m omega.cli.youtube_cli --daemon &
python -m omega.cli.local_queue submit "Analyze this codebase" --model qwen3-4b
```

---

## Mandate Compliance

| Mandate | Compliance |
|---------|------------|
| **M1 AnyIO** | All async via `anyio` where applicable |
| **M7 Local-First** | Local operations preferred; cloud only when explicit |
| **M8 Zero Telemetry** | No external analytics; local logging only |
| **M13 Temple-Grade** | Input validation; structured errors; atomic operations |
| **M24 Venv Sovereignty** | Runs in `.venv`; no system package dependencies |

---

## Testing

```bash
pytest tests/test_cli_vault.py tests/test_cli_bundle.py tests/test_cli_oracle.py -v
```

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ CLI-v1.0.0 ⬡ 2026-10-02 ⬡*