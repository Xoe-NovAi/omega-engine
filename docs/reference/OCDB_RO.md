# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# `ocdb-ro` — read-only access to `opencode.db`

> **Status: host-local tool, NOT a repo artifact.** See [Identity](#identity-identity)
> before writing any allowlist or gate that references it.

## Identity (identity)

There are three different paths in circulation for this tool. Only one of them
exists. Getting this wrong is the defect recorded as Phase 2 task 2.9.

| Path | Exists? | Notes |
|------|---------|-------|
| `~/.local/bin/ocdb-ro` | ✅ **This is the real one** | Host-local, installed per-machine. Self-contained bash. |
| `scripts/ocdb-ro` | ❌ Never existed | Named in `FINAL_LAUNCH_PLAN_20261007.md` item 4.1. Not tracked in git (`scripts/` has 70 tracked files; this is not one). |
| `01_tools/ocdb-ro` | ⚠️ Federation receipt only | Path inside the Node 1 transfer bundle (`docs/federation/node1_received/db-tools-recall-stack-20261002/`). Source-of-truth receipt for the artifact, not an install path. |

**Consequence:** the tool is NOT reproducible from a fresh clone. A clean
`git clone` + `make bootstrap` does not yield `ocdb-ro`. Any gate or allowlist
that assumes `scripts/ocdb-ro` will pass vacuously — it checks a path that is
absent and concludes "nothing to worry about". A gate that cannot fail is not a
gate. This is the same defect class as the 53/53 temple-grade result over a
crash-looping hub.

**If you need it in CI or on a fresh clone**, either:
1. Vendor `ocdb-ro` into `scripts/ocdb-ro` (tracked, with SPDX headers), or
2. Gate on `command -v ocdb-ro` and mark the gate **skipped-but-declared** when
   absent — never silently green.

Resolution is Architect-level (whether to vendor a host tool into the repo).
Ma'at has not vendored it: that is a supply-chain decision, not a build fix.

## Why it exists

`opencode db <query>` in opencode 1.18.33 opens the database **READ-WRITE** and
executes DDL/DML. Verified 2026-10-01: a bare `CREATE TABLE` against the live
1.9 GB `opencode.db` succeeded. `ocdb-ro` makes the read-only contract
**structural** instead of aspirational.

This is M23 (Failure Integrity) applied to a tool rather than a gate: no soft
path, no "I'll be careful with the query".

## The 6 safety layers

Any one alone is insufficient. This is stated as a conjunction deliberately —
a reader who believes layer 3 alone is sufficient has misread the design.

| # | Layer | What it blocks |
|---|-------|----------------|
| 1 | Statement allowlist | First keyword must be `SELECT`/`WITH`/`EXPLAIN`/`VALUES`/`PRAGMA` |
| 2 | Write-keyword rejection | DDL/DML hidden inside CTEs or comments |
| 3 | Read-only URI | `file:${DB}?mode=ro` handed to the sqlite3 CLI itself |
| 4 | Multi-statement rejection | Stacked statements |
| 5 | `sqlite3 --safe` | `writefile()`/`readfile()`/`load_extension()`, `.shell`/`.output`, `ATTACH` (CVE-2022-46908 class; requires sqlite3 >= 3.40.1) |
| 6 | Dangerous-function deny-list | Function-level denials + dot-command line rejection |

PRAGMA is allowlisted but a PRAGMA **assignment** (`PRAGMA x = y`) is rejected as
a mutation. That carve-out is intentional and is checked separately.

## Usage

```bash
ocdb-ro "SELECT COUNT(*) FROM part"
ocdb-ro --json "SELECT id,title FROM session LIMIT 5"
ocdb-ro --schema part
ocdb-ro --search "pin trap" --limit 20
ocdb-ro --explain "EXPLAIN SELECT ..."   # EXPLAIN output is NOT JSON (sqlite3 limitation)
```

DB path resolution: `$OPENCODE_DB_PATH`, else
`$HOME/.local/share/opencode/opencode.db`.

## Verified behaviour

| Probe | Expected | Meaning |
|-------|----------|---------|
| `SELECT COUNT(*) FROM part` | exit 0 | read path works |
| `CREATE TABLE x(a)` | **exit 2** | statement allowlist rejects |
| `PRAGMA journal_mode=WAL` | **exit 2** | PRAGMA-assignment rejection |

Node 0 smoke test (`data/entities/roc_racoon/workspace/mining_reports/N1_DB_TOOLS_RECALL_STACK_INSTALL_20261002.md:15`):
SELECT ok, `writefile` BLOCKED rc=2.

## Known limits

- **Never run against a 46 GB database.** Its logic is size-agnostic — meaning
  *untested* at that scale, not that it is safe. Budget accordingly.
- Not in-repo (see above), so it is absent on any fresh clone.

## Cross-references

- Node 1 receipt: `docs/federation/node1_received/db-tools-recall-stack-20261002/OPENCODE_DB_MANAGEMENT_BRIEFING.md`
- Transfer manifest: `.../MANIFEST.yaml`
- Open questions 2.9 / 4.1: `data/coordination/FINAL_LAUNCH_PLAN_20261007.md`
