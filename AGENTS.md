# Omega Engine Alpha Project Rules

Local-AI harness for this machine (Ollama + Open WebUI, CPU-only inference) and the
opencode agent configuration that knows the hardware.

## Canonical Specs
The authoritative machine & setup record lives in **`docs/HARDWARE.md`**.
- **CPU**: i7-13620H, 6P+4E (10C/16T), no discrete GPU
- **RAM**: 1×16GB DDR5-5600 single-channel @ 5200 MT/s (2nd slot EMPTY, 32GB planned)
- **Ollama**: 0.33.3, `AllowedCPUs=0-11` + `OLLAMA_NUM_THREADS=8` = 14.4 t/s
- **Open WebUI**: container on port 3000→8080

## ⚠️ The P-core pin trap (DO NOT regress)
Do NOT narrow the CPU mask to physical P-cores only (`0,2,4,6,8,10`). That collapses
throughput to ~0.5 t/s via a `llama-server` spin-wait barrier convoy (ollama #17916).
Keep HT siblings (0–11) in the mask; exclude E-cores. See `docs/HARDWARE.md`.
When the user mentions "pin to P-cores", apply `AllowedCPUs=0-11` (P-core range incl. HT),
NOT only the 6 physical cores.

## Build, lint, test / main commands
Use `make` targets (see `Makefile`):
- `make bench MODEL=...` — benchmark a model (script: `scripts/bench.py`)
- `make bench-all`, `make bench-compare` — sweep/compare
- `make python-chatbot`, `make python-serve` — interactive chat / HTTP serve
- `make env-setup` / `make env-apply` / `make env-revert` — Ollama systemd override round-trip
- `make create-coder MODEL=...` — build custom model from a Modelfile in `.modelfiles/`

## Structure
- `Makefile` — main harness
- `scripts/bench.py`, `scripts/chatbot.py`, `scripts/serve.py` — working Python entry points
- `.modelfiles/` — Modelfile sources for custom models
- `docker-compose.yml`, `.env.docker` — Open WebUI stack
- `.env.ollama` — env source of truth (documents the pin trap)

## Game-research sibling
Not this repo. Gaming/Ollama-Iris-Xe agent config and knowledge base live under
`~/.config/opencode/agent/gaming-expert.md` and `~/GameResearch/` respectively.
