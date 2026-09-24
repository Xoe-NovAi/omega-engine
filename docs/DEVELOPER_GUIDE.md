# Developer Guide — Omega Engine Alpha

For contributors writing code, scripts, or documentation in this repo.
Read `CODE_QUALITY.md` first — it contains the invariants.

## Repo layout

```
omega-engine-alpha/
├── Makefile                 # The daily interface (all operations)
├── AGENTS.md                # Agent instructions (machine rules)
├── docs/                    # Canonical documentation, federation, and research
├── scripts/
│   ├── bench.py             # Inference benchmarking
│   ├── chatbot.py           # Interactive CLI chat
│   ├── serve.py             # HTTP server (default :8000)
│   ├── continuity_kernel.py # Portable semantic continuity kernel
│   ├── continuity_sqlite.py # Local SQLite commit-authority adapter
│   ├── continuity_mempalace.py # One-way MemPalace projection
│   ├── embedding_server.py  # Qwen3 ONNX target/prototype (not live by default)
│   ├── check_docs.py        # Markdown path and anchor validator
│   ├── backup_harness.sh    # Backup + cron
│   ├── federation/          # Node 0 intake and transport helpers
│   └── compaction/          # Gnosis Lock ritual and watchdog
├── tests/                   # Regression and crash-matrix tests
├── wads/                    # Portable Entity/Card/WAD contracts
├── .modelfiles/             # Custom Modelfile sources
├── .env.ollama / .env.docker # Runtime env (gitignored; examples committed)
├── gnosis/                  # Gnosis Lock state (identity, evolution, sessions)
└── session-*.md             # Archived session transcripts (ignored)
```

## Environment

```bash
# System Python 3.12+ available; repo scripts use system python unless
# a venv is required (WanderGround uses its own .venv).
python3 --version
make help
```

## Continuity authority rule

The local SQLite continuity store is the authoritative state and event store.
MemPalace is a one-way searchable projection and must not become a second write
authority. Recovery reads SQLite continuity state plus the WAD identity contract;
MemPalace can be rebuilt after recovery. Production use requires SQLite
`3.51.3+` or a documented fixed backport.

## Development loop

```bash
make bench MODEL=my-model          # measure before/after changes
make python-chatbot                # fast manual smoke
python3 -m py_compile scripts/*.py # syntax gate
make lint-async                    # no bare asyncio/trio
```

## Testing

The repository uses the standard-library unittest suite under `tests/`:

```bash
make test
```

The test count is discovered at runtime; do not copy a historical milestone
count into current documentation. The philosophy is **verify on real hardware,
don't assume**. Any performance- or memory-claiming change gets benchmarked
(`make bench`, `make bench-all`).

## Debugging discipline

1. Any risky/unknown command runs through `withey`:
   ```bash
   withey my-test -- python3 scripts/something.py
   # pre/post CPU/mem/load snapshots, exit code, duration
   ```
2. Never `pkill -f "<string>"` that matches your own invocation. Use PIDs or
   bracket patterns (`mem[p]alace`) — the pkill-self-kill trap is real.
3. Non-interactive subprocesses always get `</dev/null` + a hard `timeout`.

## Adding a script

1. Put it in `scripts/` (or `spatial/scripts/` for WanderGround).
2. `if __name__ == "__main__": main()` with `argparse`.
3. anyio-only if async; otherwise pure sync stdlib.
4. Wire a `Makefile` target so users discover it (`make help` lists it).
5. Update `docs/` if behavior is user-visible.

## Docs rules

- Every behavioral change lands in `docs/*.md` + `SYSTEM_GUIDE.md` session log.
- Research claims get dated + cited in a "Research Findings" section.
- Model research lives in `docs/models/`; use the registry contract and evidence
  labels before promoting a model to an Omega workflow.
- README links must resolve (run `make docs` to validate).
- `CHANGELOG`-style entries live in the session log, not a separate file.

## Review gates (merge-blockers)

| Gate | Command | Blocks when |
|------|---------|-------------|
| anyio purity | `grep -rnE '^\s*(import\|from)\s+(asyncio\|trio)' scripts/` | match |
| torch ban | `grep -ri torch scripts/` | match |
| pin trap | `grep -rE 'AllowedCPUs=\d+(,\d+)+' .env.ollama` | mask excludes 1-11 |
| secrets | `grep -rE 'sk-|api[_-]?key|bearer' scripts/ docs/` | literal secret value |
| subprocess safety | manual review | missing `</dev/null`/timeout |

## Contribution workflow

See `CONTRIBUTING.md`. TL;DR: branch → atomic change → gates → PR → review.