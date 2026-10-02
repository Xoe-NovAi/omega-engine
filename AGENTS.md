# Omega Engine Alpha — Agent Orientation

Local-AI harness (Ollama + Open WebUI, CPU-only) plus the opencode agent config that
knows the hardware. This file is a **map, not a manual**. Read the linked doc when a
topic becomes relevant; do not preload it.

## Session recall — check your own history before asking

~2 years and ~12,000 hours of work live in the session database. Do not re-derive it,
and do not ask the user to repeat it.

| Question | Tool | Skill |
|---|---|---|
| "What did we decide about X?" · past debugging · prior traps | `ochist` | `agent-history` |
| Counts, cost/token totals, schema, aggregates, which sessions edited a file | `ocdb-ro` | `opencode-db` |
| Claude Code / Pi / OMP sessions | `claude-history` | `claude-history` |

```bash
ochist grep "pin trap" --global --limit 5   # note: regex, and --global avoids
                                           # current-project-only false negatives
ocdb-ro --search "gnosis" --limit 5          # prose search
ocdb-ro "SELECT ROUND(SUM(cost),2) FROM session"   # any read-only SQL
```

Use `ocdb-ro`, never raw `opencode db` — see the hard rules below.

## Hard rules — never re-derive these

1. **NEVER run `opencode db <query>` against production `opencode.db`.** It opens
   read-write and executes DDL/DML. Verified: a bare `CREATE TABLE` succeeded against
   the live database. Use `ocdb-ro` (two independent read-only layers). Well `3becf4f3`.
2. **NEVER use `immutable=1`** on a SQLite database. It ignores the WAL and returns
   stale data (measured 26 parts behind). Always `mode=ro`. Well `a3675a88`.
3. **Probe destructive paths on a `/tmp` COPY, never on production.** This one was
   learned by getting it wrong; `PRAGMA quick_check` after, always.
4. **Never narrow the Ollama CPU mask to physical P-cores** (`0,2,4,6,8,10`). Use
   `AllowedCPUs=0-11` (P-cores **including HT siblings**) + `OLLAMA_NUM_THREADS=8`
   = 14.4 t/s. Physical-only collapses to ~0.5 t/s via a spin-wait barrier convoy
   (ollama #17916). DO NOT REGRESS.
5. **Warm a model before benchmarking it.** A cold first call is not the number.
   `qwen3-embedding:0.6b` measured 10,645 ms/embed cold vs 122 ms warm — 87×. Well `a3675a88`.
6. **Never hardcode model context limits.** Drift-detect against live models.dev
   (`scripts/opencode_provider_doctor.sh`).

## Gates — run before claiming done

```bash
make lint   # anyio purity, no bare exceptions, no torch, model-card validation
make test   # regression suite (121 tests)
make docs   # README + internal doc links
```

All three must be green. "Temple-grade over speed" — the finish gate is the contract.

## Machine — the short version

- **CPU** i7-13620H, 6P+4E, 10C/16T, no discrete GPU
- **RAM** 1×16 GB DDR5-5600 single-channel (2nd slot empty, 32 GB planned)
- **Inference** CPU-only, `AllowedCPUs=0-11`
- Authoritative record: **`docs/HARDWARE.md`**

## Downloads — aria2c, never bare curl

For any file over ~5 MB (tarballs, GGUF weights, wheels, model blobs, container
layers): `aria2c -x 16 -s 4 -k 1M --file-allocation=none -o <out> <url>`.
Bare `curl -o` wastes 10–20× wall-clock (measured: 1.43 GB Ollama tarball, 5 min vs
7m32s). Verify checksums before installing — M23 failure integrity means no install on
mismatch. Use `curl` only for small text/API responses. Details: `docs/HARDWARE.md`.

## Main commands

`make bench MODEL=…` · `bench-all` · `bench-compare` · `python-chatbot` · `python-serve`
· `env-setup`/`env-apply`/`env-revert` (Ollama systemd round-trip) · `create-coder`
· `lint` · `test` · `docs` · `gnosis-lock` · `gnosis-stats` · `gnosis-leash-status`

## Session close

- `/gnosis-lock` — ritual capture + human reflection + narrative commit. Does NOT run
  docs/lint/test.
- "Prepare for compaction" = gnosis-lock + doc updates + `make lint` + `make test` + commit.
- `/compact` — **standalone line only, zero arguments.** Text after it becomes a normal prompt.
- New ideas land in `docs/ROADMAP.md` with a status **before** implementation (standing rule).

## Where things are

| Path | Holds |
|---|---|
| `docs/HARDWARE.md` | canonical machine + setup record |
| `docs/AGENT_RUNBOOK.md` | full agent awareness runbook |
| `docs/INDEX.md` | **documentation map — start here** |
| `docs/ROADMAP.md` | the single ordered backlog |
| `docs/OPENCODE_DB_MANAGEMENT_BRIEFING.md` | session-DB read/search/index strategy |
| `docs/PORTABILITY.md` | what must not leak into the future Omega CLI |
| `docs/GNOSIS_USAGE.md` | protocol deep-dive |
| `docs/CODE_QUALITY.md` | invariants + enforcement |
| `gnosis/well/` | The Well — active corrections injected into system prompts |
| `~/WanderGround/` | knowledge capture: `wander` CLI, MemPalace MCP, sqlite-vec atlas |
| `~/.config/opencode/agent/gaming-expert.md` | gaming sibling (different repo) |

## Privacy

Free Zen models collect prompt data. Private work uses paid zero-retention models
only (`docs/WANDERGROUND_SPEC.md` §10.4).
