# AP: AP-DEPLOYMENT-v1.0.0
# 🔱 Omega Engine — Deployment & Portability Guide
# ⬡ OMEGA ⬡ DEPLOYMENT ⬡ v1.1.0

This document covers system requirements, installation, configuration, and portability for the Omega Engine.

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Linux (Ubuntu 22.04+, Fedora 38+) | Ubuntu 24.04 LTS |
| **Python** | 3.12+ | 3.12+ |
| **RAM** | 8 GiB | 14+ GiB (Ryzen 5700U tested) |
| **Disk** | 10 GB free | 20+ GB free (models + data) |
| **CPU** | 4 cores, AVX2 | 8 cores (Zen 2 optimized) |
| **GPU** | None required | Integrated (Intel/AMD) sufficient |
| **Network** | Not required (local-first) | For initial model download + optional cloud providers |

---

## Installation

### Option 1: Git Clone (Recommended)

```bash
# Clone the repository
git clone https://github.com/Xoe-NovAi/omega-engine.git
cd omega-engine

# Run the bootstrap (creates venv, installs deps, sets up pre-commit hooks)
make bootstrap

# Download the default local model (Qwen 1.7B GGUF, ~1.6GB)
make model-download

# Verify everything works
make test
```

### Option 2: Manual Setup

```bash
# Create and activate venv
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Download model
make model-download
```

---

## Configuration

### Core Config: `config/omega.yaml`

All engine behavior is configured via YAML. No environment variables required for basic operation.

Key sections:
- `omega.entity.active_iwad` — Active WAD stack (default: `_omega_default`)
- `omega.provider_fabric.strategy` — `local_first` (default), `cloud_first`, or `balanced`
- `omega.memory.*` — Hot/warm/cold tier sizes and compaction settings
- `omega.security.*` — PII masking, TDP, tainted data quarantine
- `omega.hardware.*` — CPU threads, OpenBLAS core type, KV cache settings

### Provider Config: `config/providers.yaml`

Controls the inference backend priority chain. Local providers are tried first by default.

### Entity Config: `config/wads/<stack>/entities.yaml`

Entity definitions are WAD-scoped. The `_omega_default` IWAD provides universal entities.
PWADs (like `arcana_novai`) extend with domain-specific entities.

---

## Portability

### Absolute Paths (M16 Compliance)

The engine uses **zero hardcoded absolute paths** in core code. All paths resolve via:

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATA_DIR` | `data/` | Session memory, entity data, coordination files |
| `CONFIG_DIR` | `config/` | YAML configs, WAD definitions |
| `MODELS_DIR` | `models/gguf/` | GGUF model files |

### Symlink Support

For systems where the repo lives on a read-only partition or shared drive:

```bash
# Symlink models to external storage
ln -s /mnt/external/models/gguf models/gguf

# Symlink data directory
ln -s /mnt/external/omega-data data
```

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `OMEGA_ENV` | `production` | Set to `test` for mock backends |
| `OMEGA_INGESTION_SECRET` | (built-in) | HMAC secret for ingestion pipeline provenance |
| `LLAMA_CPP_N_THREADS` | `4` | CPU threads for GGUF inference |
| `LLAMA_CPP_F16_KV` | `true` | Use FP16 KV cache |
| `OPENBLAS_CORETYPE` | `ZEN` | OpenBLAS optimization target |
| `MALLOC_ARENA_MAX` | `2` | jemalloc arena limit (reduces fragmentation) |

---

## Infrastructure Containers

Optional Podman containers for production deployment:

```bash
# Start all infrastructure (Redis, Qdrant, PostgreSQL, Caddy)
make start-infra

# Check status
make infra-status

# Stop all
make stop-infra
```

| Container | Purpose | Port |
|-----------|---------|------|
| `redis` | Session cache, Hivemind pub/sub | 6379 |
| `qdrant` | Vector store for semantic search | 6333 |
| `postgres` | Persistent SQL storage | 5432 |
| `caddy` | Reverse proxy | 80/443 |

All containers run rootless with `UserNS=keep-id` + `User=1000` (M6 compliant).

---

## Hardware Optimization

The engine auto-detects hardware and applies optimal flags:

| Setting | Value | Rationale |
|---------|-------|-----------|
| `LLAMA_CPP_N_THREADS=4` | 4 of 8 cores | Leaves headroom for OS + other processes |
| `OPENBLAS_CORETYPE=ZEN` | Zen 2 | Matches Ryzen 5700U architecture |
| `LLAMA_CPP_F16_KV=true` | FP16 KV cache | 2x memory efficiency vs FP32 |
| `MALLOC_ARENA_MAX=2` | 2 arenas | Reduces RSS fragmentation by ~200MB |

---

## Troubleshooting

### "No module named omega"
```bash
# Ensure venv is activated
source .venv/bin/activate
# Reinstall in editable mode
pip install -e .
```

### "Model not found"
```bash
# Download the default model
make model-download
# Or list available models
make model-list
```

### Tests fail with "import asyncio"
This is a CI/M1 violation. Report it as a bug — all async code must use AnyIO.

### Permission errors on data/ directory
```bash
# Fix UID drift
make guard
# Or manually
sudo chown -R 1000:1000 data/
```

### Container fails to start
```bash
# Check Podman storage
make infra-status
# Verify UserNS=keep-id in container spec
podman inspect <container> | grep UserNS
```

---

## Version Information

| Component | Version |
|-----------|---------|
| Omega Engine | v1.1.0 |
| Python | 3.12+ |
| Qdrant | 1.17.1 (pinned) |
| Redis | 7-alpine |
| PostgreSQL | pgvector-pg17 |

---

*🔱 OMEGA ⬡ DEPLOYMENT ⬡ v1.1.0 ⬡ AP-DEPLOYMENT-v1.0.0*
