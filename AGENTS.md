# Omega Engine Alpha — Agent Orientation

Local-AI harness (Ollama + Open WebUI, CPU-only) plus the opencode agent config that
knows the hardware. This file is a **map, not a manual**. Read the linked doc when a
topic becomes relevant; do not preload it.

## Session recall — check your own history before asking

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
2. **NEVER run `opencode session delete <sessionID>`.** There is no undo path here.
   For session inventory use read-only `opencode session list`; for usage use
   `opencode stats`; for transcripts use sanitized `opencode export`.
3. **NEVER use `immutable=1`** on a SQLite database. It ignores the WAL and returns
   stale data (measured 26 parts behind). Always `mode=ro`. Well `a3675a88`.
4. **Probe destructive paths on a `/tmp` COPY, never on production.** This one was
   learned by getting it wrong; `PRAGMA quick_check` after, always.
5. **Warm a model before benchmarking it.** A cold first call is not the number.
   `qwen3-embedding:0.6b` measured 10,645 ms/embed cold vs 122 ms warm — 87×. Well `a3675a88`.
6. **Never hardcode model context limits.** Drift-detect against live models.dev
   (`scripts/opencode_provider_doctor.sh`).
7. **Handoff packets ≤ 4 KB.** Context = filename + size + sha256 + pull URL; bodies live in Exchange. On transport POST failure, shrink to pointer and resubmit — never retry identical bytes. Measured 4.3 KB succeeds, 4.5 KB fails. Well `3a0c851b`.

## Gates — run before claiming done

```bash
make lint   # anyio purity, no bare exceptions, no torch, model-card validation
make test   # regression suite
make docs   # README + internal doc links
```

All three must be green. "Temple-grade over speed" — the finish gate is the contract.

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

**Precedence:** `gnosis/well/` (injected, newest-wins) > `AGENT_RUNBOOK.md` §8 ladder > `docs/*` > these two files.

## Privacy

Free Zen models collect prompt data. Private work uses paid zero-retention models
only (`docs/WANDERGROUND_SPEC.md` §10.4).