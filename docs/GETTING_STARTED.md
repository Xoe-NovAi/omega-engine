# Getting Started — Omega Engine Alpha

From bare Ubuntu to a +14 t/s sovereign inference node in 10 minutes.

## Prerequisites

| Item | Minimum | Notes |
|------|---------|-------|
| OS | Ubuntu 26.04+ | Debian-family works with apt swaps |
| RAM | 16 GB | 32 GB recommended (dual-channel doubles throughput) |
| CPU | x86-64 with AVX2 | Intel hybrid preferred (see HARDWARE.md) |
| Disk | 20 GB free | Models + Docker + storage |
| Docker | 24+ | For Open WebUI |
| Python | 3.12+ | 3.14 works (WanderGround venv) |

> ⚠️ CPU-only: no GPU. This harness is tuned for CPU inference, and
> aggressively so (P-core + HT sibling pinning, KV q8_0, flash-attn).

## 1. Install the core

```bash
# Ollama (REST daemon)
curl -fsSL https://ollama.com/install.sh | sh

# Docker + Open WebUI
sudo apt install docker.io docker-compose
docker compose up -d               # Open WebUI on :3000

# Python + tools
sudo apt install python3 python3-venv git make jq
```

## 2. Clone & configure

```bash
git clone https://github.com/xnai/omega-engine-alpha.git
cd omega-engine-alpha

make env-setup      # generate .env.ollama from example
make env-apply      # write Ollama systemd override (pin + threads)
sudo systemctl restart ollama
make env-verify     # confirm 14+ t/s config
```

## 3. Pull a model & benchmark

```bash
ollama pull phi4-mini
make bench MODEL=phi4-mini        # expect ~13-14 t/s on i7-13620H
```

## 4. Talk to the engine

```bash
make python-chatbot   # interactive CLI
make python-serve     # HTTP :8080 (OpenAPI at /docs)
# or open http://localhost:3000 (Open WebUI)
```

## 5. Session continuity (Gnosis Lock)

```bash
make gnosis-lock      # 9-step pre-compaction ritual
make gnosis-stats     # evolution log
```

OpenCode users get this automatically via the `gnosis-leash` plugin
(session.created/idle/compacted events + compaction context injection).

## 6. WanderGround (explorer node, optional but glorious)

```bash
cp -r ~/WanderGround-example ~/WanderGround   # or clone the sibling repo
cd ~/WanderGround
make status            # inbox/archive/dossier/db status
make capture NOTE="first spark"
make ingest            # embed + archive + sqlite-vec refresh
make 3d-serve          # Three.js constellation on :8088
```

See `docs/WANDERGROUND_SPEC.md` for the full spatial-knowledge substrate.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| ~0.5 t/s after "pinning" | P-core-only mask trap | `AllowedCPUs=0-11`, NOT `0,2,4,6,8,10` |
| Swap thrash with 2 models | MAX_LOADED_MODELS = 2 on 16GB | Set `OLLAMA_MAX_LOADED_MODELS=1` |
| OWUI task model reloads | keep-alive mismatch | Set Keep Alive = `-1` per model in UI |
| Downloads stall | Flaky link | aria2 `-c -x8 -s8` or `curl -C -` to real disk |

## Next steps

- Read `docs/ARCHITECTURE.md` — how the two nodes federate.
- Read `docs/HARDWARE.md` — the full machine record and the pin trap.
- Build a custom model: `make create-coder MODEL=mychat-qwen3`.
- Join the build: `CONTRIBUTING.md`.