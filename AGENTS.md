# Omega Engine Alpha Project Rules

Local-AI harness for this machine (Ollama + Open WebUI, CPU-only inference) and the
opencode agent configuration that knows the hardware.

## Canonical Specs
The authoritative machine & setup record lives in **`docs/HARDWARE.md`**.
- **CPU**: i7-13620H, 6P+4E (10C/16T), no discrete GPU
- **RAM**: 1×16GB DDR5-5600 single-channel @ 5200 MT/s (2nd slot EMPTY, 32GB planned)
- **Ollama**: see `docs/HARDWARE.md` for the live version; `AllowedCPUs=0-11` (P-cores incl. HT)
- **Open WebUI**: container on port 3000→8080

## ⚠️ Downloads: always use `aria2c`, never bare `curl`/`wget` (DO NOT regress)
`aria2c` is installed (`/usr/bin/aria2c`, v1.37.0). For **any file over ~5 MB** — release
tarballs, GGUF weights, Python wheels, model blobs, container layers — use multi-connection
download:

```bash
aria2c -x 16 -s 4 -k 1M --file-allocation=none -o <outfile> <url>
```

Bare `curl -o` on a large file wastes 10–20x the wall-clock. Observed 2026-09-26 on the
1.43 GB Ollama 0.34.4 tarball: `curl` did not finish in 5 minutes; `aria2c -x 16 -s 4`
completed in 7m32s at 3.0 MiB/s average with resume support.

Companion rules that go with it:
- **Verify the checksum before installing anything.** Ollama publishes `sha256sum.txt` per
  release; M23 failure integrity means no install on mismatch.
- Prefer `curl` only for small text/API responses (< ~1 MB).
- `aria2c` resumes automatically; do not delete a partial file on failure, re-run the same
  command.
- Ollama Linux release assets are `.tar.zst` (not `.tgz`) as of the 0.34.x series — a `.tgz`
  URL 404s. List real asset names with the GitHub releases API before guessing a URL.

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
- `make lint` — code-quality gates (anyio purity, no bare exceptions, no torch)
- `make test` — regression suite (`tests/`, 24+ tests)
- `make docs` — validate docs integrity (README + doc links)
- `make gnosis-lock REASON="..."` — pre-compaction ritual capture (CLI)
- `make gnosis-stats` — evolution-log stats + timeline
- `make gnosis-leash-status` — watchdog for the automated gnosis-leash plugin

## Session-close & gnosis protocols (IMPORTANT — see docs/AGENT_RUNBOOK.md)
- **`/gnosis-lock`** (TUI command + skill): capture + dynamic human reflection via
  the native `question` tool + narrative commit. Does NOT do docs/lint/test.
- **"Prepare for compaction"**: full orchestration — gnosis-lock + doc updates +
  `make lint` + `make test` + commit.
- **`/compact`**: standalone line ONLY, zero arguments — text after it turns into
  a normal prompt (tested fact, differs from Gemini CLI).
- **gnosis-leash.js plugin** (in ~/.config/opencode/plugins/): logs session events,
  injects WanderGround INDEX + your narrative into compaction, appends operating
  rules to every system prompt. Watch with `make gnosis-leash-status`.
- **WanderGround** (`~/WanderGround/`): `wander` CLI capture, MemPalace MCP
  (`mempalace`), knowledge atlas (sqlite-vec), curator timer, 3D viewer, MkDocs.
- **Zen privacy**: free Zen models collect prompt data; private work uses paid
  zero-retention models (docs/WANDERGROUND_SPEC.md §10.4).

## Structure
- `Makefile` — main harness (includes gnosis-lock, gnosis-stats, gnosis-leash-status)
- `scripts/bench.py`, `scripts/chatbot.py`, `scripts/serve.py` — working Python entry points
- `scripts/compaction/` — ritual + evolution log + leash_status watchdog
- `tests/` — regression suite (repo hygiene, secrets, evolution log, gnosis-leash, leash-status)
- `.modelfiles/` — Modelfile sources for custom models
- `docker-compose.yml`, `.env.docker` — Open WebUI stack
- `.env.ollama` — env source of truth (documents the pin trap)
- `docs/AGENT_RUNBOOK.md` — canonical awareness runbook for agents
- `docs/ROADMAP.md` — the single ordered backlog (new ideas land here with a
  status BEFORE implementation — standing rule)
- `docs/GNOSIS_USAGE.md` — protocol deep-dive & exact command reference
- `docs/CODE_QUALITY.md` — invariants & enforcement

## Game-research sibling
Not this repo. Gaming/Ollama-Iris-Xe agent config and knowledge base live under
`~/.config/opencode/agent/gaming-expert.md` and `~/GameResearch/` respectively.

## OpenCode model config (Big Pickle)
Built-in (models.dev registry — zero custom config; `opencode models` lists it).
History: a custom 1M-window override existed here and matched reality (sessions
at 205.8K+ tokens) — then Zen moved Big Pickle to 200K within ~a day
(operator-observed 2026-09-18, registry snapshot confirms 200K/160K/32K).
Doctrine: NEVER hardcode model limits; drift-detect against live models.dev
(`scripts/opencode_provider_doctor.sh`). See gaps guide §11.8/§13.
