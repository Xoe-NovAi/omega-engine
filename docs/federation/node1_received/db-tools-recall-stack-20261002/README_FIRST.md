# ⬡ N1 → N0 DELIVERY — DB TOOLS RECALL STACK — READ ME FIRST

**Package**: `N1-DB-TOOLS-RECALL-STACK-20261002`
**Source**: n1-vanguard (XNAi-Asus, ASUS ExpertBook) · **Destination**: n0-bastion Researcher
**Built**: 2026-10-02 · **By**: researcher_humboldt (Node 1)
**Transport**: Omega Exchange file drop (`n1-to-n0/`), ping via Route A handoff
**Status gates at seal time**: `make lint` ✓ · `make test` 129/129 ✓ · `make docs` 232/232 ✓

## What this is

The complete opencode.db session-recall system developed and hardened on Node 1
across action items C1–C2, H1–H3, M1–M6 (research-subagent → synthesize → execute
per item, all empirical). Fifteen items, all closed, all gates green.

**NOT included**: `opencode.db` itself (1.9 GB, node-local by design — Node 0
keeps its own corpus). Everything here is code, config, docs, and records.

## Package map

| Path | Purpose |
|---|---|
| `01_tools/ocdb-ro` | Read-only SQLite wrapper, 6 safety layers (allowlist, keyword deny incl. `writefile`/`readfile`/`load_extension`, `mode=ro`, anti-stacking, `sqlite3 --safe`, dot-command rejection). Install: `~/.local/bin/`, needs sqlite3 ≥ 3.40.1 |
| `01_tools/well_recurrence_check.py` | Mechanical Well-recurrence detector. Exit 0 clean / 1 findings / 66 EX_NOINPUT. Repo-relative paths, `WELL_DIR_OVERRIDE` supported |
| `01_tools/lint_checks.py` | Custom lint gates incl. new gate 4: `with`/`for` handle-shadowing AST check (ruff PLW2901 equivalent, zero deps) |
| `02_commands/recall.md`, `db.md` | `/recall` → ochist, `/db` → ocdb-ro. **No `agent:` pin** — executes as invoking agent (M6 decision) |
| `03_tests/test_recall_stack.py` | Live recall-stack tests as real `TestCase` (8 tests, `skipUnless` guards) |
| `03_tests/test_repo_hygiene.py` | Incl. `TestDiscoveryCompleteness` — fails any `test_*.py` yielding zero collected tests |
| `04_docs/HARDENING_PLAN.md` | Master hardening plan (recall claims corrected to Makefile reality) |
| `04_docs/OPENCODE_DB_MANAGEMENT_BRIEFING.md` | DB strategy: linear scan 1.4 ms/MB, `mode=ro` mandatory, `immutable=1` banned, FTS timeline note |
| `04_docs/HARDWARE.md` | Canonical Node 1 machine spec (pin-trap rule, Ollama config) |
| `04_docs/CODE_QUALITY.md` | Repo invariants (anyio, no bare exceptions, no torch, no secrets) |
| `05_well/new-records-20261002.jsonl` | Two Well records: `part_fts` drop supersession (`4cd3d7ae…` supersedes `a3675a88…`) + supersede-ref fix (`11bcd49a…`). Append to `gnosis/well/well.jsonl` |
| `06_skills/opencode-db-SKILL.md`, `agent-history-SKILL.md` | Recall skill definitions (FTS timeline note included) |
| `MANIFEST.yaml` / `SHA256SUMS` | Byte-integrity model (manifest hashes every file; ledger covers manifest too) |

## Key decisions (Humboldtian isotherms — one line each)

1. **C1**: `sqlite3 --safe` (CVE-2022-46908 fix) is the authoritative control for `writefile`/`readfile`/`load_extension`; keyword deny-list is belt-and-braces.
2. **C2**: Stale `part_fts` **dropped** (2075 rows unindexed, silent false negatives, zero MATCH consumers) — probed on `/tmp` copy first, then production under live WAL writer.
3. **H1**: Bare test functions are invisible to `unittest discover`; TestCase + completeness meta-test.
4. **H2**: Repo-relative paths + `WELL_DIR_OVERRIDE`; sysexits 66 for "couldn't look" (never exit 0 on missing input).
5. **M6**: Commands carry no `agent:` pin — the invoker's entity voice survives.

## Verify (receiver side)

```bash
cd db-tools-recall-stack-20261002
sha256sum -c SHA256SUMS
ocdb-ro "SELECT writefile('/tmp/x','y')"   # expect BLOCKED rc=2
python3 -m unittest discover -s tests -v   # after placing 03_tests (expect recall tests listed)
```

## Trust boundary

Byte integrity only (SHA256SUMS). No detached signature. Provenance: this pack
was built by researcher_humboldt on Node 1 from the omega-engine-alpha working
tree at the commits sealed by `make lint/test/docs` on 2026-10-02.
