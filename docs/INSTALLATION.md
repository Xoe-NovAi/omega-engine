# Installation — Omega Engine Alpha Node 1

**Audience:** Operators installing the local Node 1 harness.  
**Scope:** This guide installs and verifies the local Ollama/Python/WebUI path. WanderGround, MemPalace spatial migration, Gnosis, and federation are separate layers with different prerequisites.

## 1. Supported target

The documented target is:

- Ubuntu 26.04 LTS or a compatible Debian-family system;
- x86-64 CPU with AVX2;
- 16 GB RAM minimum;
- Python 3.12+;
- Docker 24+ for Open WebUI;
- 20 GB free disk minimum, plus room for model weights.

The current hardware-specific profile is the ASUS ExpertBook P1503CVA with Intel i7-13620H, 16 GB DDR5, and CPU-only inference. Do not copy the P-core mask to unrelated hardware without measuring it first.

## 2. Install prerequisites

```bash
sudo apt update
sudo apt install -y curl python3 python3-venv git make jq docker.io
```

Install Ollama using its official installer:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Verify the service:

```bash
ollama --version
systemctl status ollama --no-pager
```

The repository's current hardware profile uses rollback journaling and the following continuity/runtime policy:

```text
OLLAMA_MAX_LOADED_MODELS=1
OLLAMA_NUM_THREADS=8
OLLAMA_CONTEXT_LENGTH=8192
OLLAMA_KV_CACHE_TYPE=q8_0
```

## 3. Clone and configure

```bash
git clone https://github.com/xnai/omega-engine-alpha.git
cd omega-engine-alpha
cp .env.ollama.example .env.ollama
```

Review `.env.ollama` before applying it. It is the source of truth for the Node 1 Ollama service profile.

Apply the profile to the systemd service:

```bash
make env-setup
make env-show
make status
```

`make env-setup` requires permission to write the systemd override and restart Ollama. It is not a dry-run command.

## 4. Pull and benchmark a model

```bash
make pull MODEL=phi4-mini
make status
make bench MODEL=phi4-mini
```

A successful benchmark records the actual model, prompt count, warm/cold state, throughput, and host conditions. Do not treat a result from another machine as a Node 1 baseline.

The current ASUS configuration is tuned for the Intel hybrid CPU trap:

```text
AllowedCPUs=0-11
OLLAMA_NUM_THREADS=8
```

Do not replace this with physical-P-core-only masking without a controlled benchmark.

## 5. Run the local interfaces

### Terminal chat

```bash
make python-setup
make python-test
make chat-fast
```

### HTTP wrapper

```bash
make python-serve
```

The default HTTP port is `8000`:

```text
http://localhost:8000
```

The service exposes:

- `GET /health`
- `POST /chat`
- OpenAPI documentation at `/docs` when FastAPI is available.

To choose another port:

```bash
make python-serve PORT=8080
```

## 6. Optional Open WebUI

Open WebUI is optional. The Make target uses a persistent Docker volume named `open-webui` and exposes the UI on port `3000`.

```bash
make webui
make webui-status
```

Open:

```text
http://localhost:3000
```

Useful commands:

```bash
make webui-logs
make webui-down
```

Current Node 1 guidance:

- leave per-model `num_ctx` unset so Ollama's server context is inherited;
- set per-model Keep Alive to `-1` or `30m` if model reloading is unwanted;
- do not treat Open WebUI as a second model authority;
- keep `OLLAMA_MAX_LOADED_MODELS=1` on 16 GB single-channel systems.

## 7. Optional Gnosis and continuity tooling

Gnosis and continuity are not required for basic chat. They are required for durable agent state and session recovery.

```bash
make gnosis-ledger
make gnosis-leash-status
make well-stats
make test
make lint
```

The local SQLite continuity store is the authoritative state/event store. MemPalace is a one-way searchable projection and must not be used as a second write authority.

Production continuity requires SQLite `3.51.3+` or a documented fixed backport. The current Node 1 runtime remains a reference/test environment until that gate is satisfied.

## 8. Optional WanderGround / MemPalace

WanderGround is a sibling workspace, not a command bundled into this repository. The current Node 1 state is:

- MemPalace `3.10.0` available;
- `sqlite_exact.sqlite3` backend;
- 5,047 documents currently at 384 dimensions;
- `spatial/knowledge_atlas.db` absent;
- 3D viewer on port `8088` absent;
- standalone Qwen3 768-D embedding service not live.

The current 384-D corpus is not automatically compatible with the target Qwen3 768-D space. Do not mix dimensions in one index. Follow the blue/green migration guidance in `docs/WANDERGROUND_SPEC.md` and the embedding decision record before attempting migration.

## 9. Optional federation

Federation requires Node 0, the signed/verified USB or network handoff, and the current operator procedure. This repository does not ship a live first-contact script.

Start with:

```text
docs/federation/README.md
docs/federation/MAKALI_N0_SYSTEM_BRIEFING_CONSOLIDATED.md
```

The live SQLite authority remains local to each node. NFS is not used for a live SQLite database.

## 10. Post-install verification

Run:

```bash
make status
make webui-status       # only if Open WebUI was installed
make python-test
make docs
make lint
make test
make gnosis-leash-status
```

Expected baseline:

- Ollama responds on `localhost:11434`;
- `make bench MODEL=phi4-mini` reports a measured result;
- `make python-test` reaches Ollama;
- `make docs` reports valid documentation links;
- `make lint` and `make test` pass;
- Gnosis watchdog is healthy or clearly reports an in-flight capture.

## 11. If setup fails

| Symptom | Check | Corrective direction |
|---|---|---|
| `env-setup` cannot find `.env.ollama` | `ls -l .env.ollama` | Copy `.env.ollama.example` first |
| Ollama is not responding | `make status` and `systemctl status ollama` | Start/restart the service, then rerun `make status` |
| Throughput collapses near 0.5 t/s | Inspect `AllowedCPUs` | Restore `0-11`; do not use physical P-cores only |
| Open WebUI cannot connect | `make webui-logs` and `make status` | Check Ollama, host gateway, and port 3000 |
| Python chatbot cannot import `ollama` | `.venv/bin/python3 -c 'import ollama'` | Run `make python-setup` |
| Atlas or viewer missing | Check `~/WanderGround/spatial/` | These are target services, not installation failures |
| Continuity says SQLite version is too old | `python3 -c 'import sqlite3; print(sqlite3.sqlite_version)'` | Select a fixed runtime before production use |
| Federation commands are absent | `make help` and federation docs | Node 0 access is a separate external dependency |

## 12. Next references

- `docs/USER_GUIDE.md` — actual user workflows;
- `docs/AGENT_RUNBOOK.md` — agent/session operations;
- `docs/CONTINUITY_KERNEL.md` — continuity architecture;
- `docs/HARDWARE.md` — machine-specific tuning;
- `docs/federation/README.md` — federation operations.
