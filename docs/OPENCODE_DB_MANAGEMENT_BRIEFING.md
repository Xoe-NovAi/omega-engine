# opencode.db Management — Definitive Briefing for Node 0

**From:** Researcher-Humboldt (Node 1)
**Date:** 2026-10-02
**Scope:** 46 GB `opencode.db` on Node 0. Read-only access, search, backup, and index strategy.
**Status:** All Node 1 figures measured live. Node 0 figures are explicitly marked UNMEASURED.

---

## 0. Read this first — the two facts that change the plan

### 0.1 `opencode db <query>` is NOT read-only. It is a write-capable handle.

Measured on Node 1, 2026-10-01. I ran a `CREATE TABLE` against the live 1.9 GB
`opencode.db` via `opencode db` and it **succeeded** — the database's sha256 changed
from `cf40898235fe8ce7` to `980f14a3a38a6d0f`. The table was dropped immediately;
`PRAGMA quick_check` returned `ok`; residue 0. No data was lost, but **the hazard is real**.

The native tool is also the fastest path (1.26 s for a real search, vs 2.4 s for
`ochist`), so it is tempting. Do not let any agent use it unguarded.

**Rule: raw `opencode db` is banned against production `opencode.db`.**

### 0.2 Read-only access to a WAL database is subtler than "open it read-only"

This is the most important correction in this briefing, and it is why the wrapper on
Node 1 has two independent layers.

SQLite's own documentation states that historically *"It is not possible to open
read-only WAL databases."* That was relaxed in **SQLite 3.22.0 (2018-01-22)**, but
only under specific conditions — the doc now says a read-only WAL database can be
opened if:

1. the `-shm` and `-wal` files already exist and are readable, **or**
2. there is write permission on the *directory* so they can be created, **or**
3. the connection is opened with the `immutable` query parameter.

Source: <https://sqlite.org/wal.html> §4 "Read-Only Databases"

The SQLite forum is blunter, from a thread on WAL + read-only access
(<https://sqlite.org/forum/info/0667868158167ccb>):

> "A LOGICAL (ie, application level) read-only connection is still required to have
> PHYSICAL (ie, Operating System level) write-access to the SHM file."

And on the failure mode:

> "If the Operating System cannot grant write access to the SHM file, then the
> database must be immutable (no one can change it). **If the database is immutable
> and nonetheless is 'mutated', all hell will break loose.**"

**Implication for Node 0:** a 46 GB database is very likely to be archived, moved to
read-only media, or opened by a non-owner. A tool that assumes it can always create
`-shm` will fail there, and the tempting fallback (`immutable=1`) returns **stale
data** — measured 26 parts behind on Node 1.

---

## 1. Node 0 triage — run this FIRST

Everything above the fold depends on one number I cannot reach from Node 1. SSH over
Tailscale is ACL-blocked (`ssh: connect to host 100.123.51.67 port 22: Connection timed out`)
and the hub's TLS on `:8016` fails verification from this shell. The federation
itself diagnosed PASS on all five checks, so the mesh is healthy — I just lack a
shell.

Run on Node 0:

```bash
DB=~/.local/share/opencode/opencode.db

# 1. Size and WAL health
ls -lh "$DB" "$DB-wal" "$DB-shm" 2>/dev/null

# 2. ROW COUNTS — this is the number that matters, not file size
sqlite3 "file:$DB?mode=ro" "
  SELECT 'parts_total',        COUNT(*) FROM part
  UNION ALL SELECT 'parts_text', COUNT(*) FROM part WHERE json_extract(data,'\$.type') IN ('text','reasoning')
  UNION ALL SELECT 'messages',  COUNT(*) FROM message
  UNION ALL SELECT 'sessions',  COUNT(*) FROM session;"

# 3. Searchable corpus in MB
sqlite3 "file:$DB?mode=ro" "
  SELECT ROUND(SUM(LENGTH(json_extract(data,'\$.text')))/1048576.0,1)
  FROM part WHERE json_extract(data,'\$.type') IN ('text','reasoning');"

# 4. Schema drift check against this briefing
sqlite3 "file:$DB?mode=ro" "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"

# 5. Migration state
sqlite3 "file:$DB?mode=ro" "SELECT COUNT(*), MAX(id) FROM migration;"

# 6. Integrity (fast on 46GB, do it before anything else)
sqlite3 "file:$DB?mode=ro" "PRAGMA quick_check;"
```

### Interpreting the row count

Measured on Node 1: 58,612 parts → **282 ms** full scan, i.e. **~4.9 µs/row**.
Corpus there is 14.3 MB across 15,425 text/reasoning parts.

| Searchable rows (text+reasoning) | Full-scan cost | Action |
|---|---|---|
| < 200k | < 1 s | **No index.** Use `ochist` as-is. |
| 200k – 2M | 1 – 10 s | Add FTS5 sidecar (§4). |
| > 2M | > 10 s | Sidecar mandatory; consider partitioning by month (§6). |

> **Correction to my earlier advice.** I previously projected "46 GB → ~64 s" by
> multiplying 1.4 ms/MB by the *file size*. That is the wrong denominator — file size
> is dominated by `tool` blobs, not searchable text. On Node 1, 1.9 GB of file held
> only 14.3 MB of searchable text. **Use the row count from query 2, not the file size.**

---

## 2. The toolchain

### 2.1 `ochist` — search & recall (primary)

- **Install:** `sudo npm install -g agent-historian` (v0.6.0, 184 KB, **zero dependencies**, MIT)
- **Skill:** `ochist skill install --global` → lands at `~/.agents/skills/agent-history`, auto-discovered by OpenCode
- **Runtime:** Node ≥18; uses `node:sqlite` (needs ≥22.5), lazy-loaded and degrades gracefully
- **Sources:** OpenCode, Claude Code, Qoder, Codex

Audited at `/usr/local/lib/node_modules/agent-historian/dist/`. Key properties:

- Opens with `new sqlite.DatabaseSync(path, { readOnly: true })` — **no URI form**, so it
  reads the WAL normally. sha256-verified byte-identical after 5 global greps.
- **Has no raw-SQL verb at all.** Verbs are `sessions`, `sources`, `grep`, `meta`,
  `show`, `part`, `doctor`, `skill`. This is a *structural* read-only guarantee, not a
  runtime flag — stronger than any wrapper.
- Folds subagent sessions into their parent via `COALESCE(parent_id, id)`, so
  subagent transcripts are not orphaned.
- Tool content is truncated on read (500 chars per input string, 1500 per output);
  `ochist part <id>` re-reads the row untruncated.

**Gotchas (both cost me a false negative):**
- `grep` takes a **regex**, not a literal substring. Metacharacters are live.
- `grep`/`sessions` default to **current-project scope**. From an unrelated cwd it
  returns empty and looks broken. Use `--global`.
- `meta`/`show` accept either a slug or a full session id (both verified).

### 2.2 `ocdb-ro` — ad-hoc read-only SQL

- **Location:** `~/.local/bin/ocdb-ro` (copy to Node 0; it is self-contained bash)
- **Layer 1 — statement allowlist:** first keyword must be `SELECT|WITH|EXPLAIN|VALUES|PRAGMA`;
  write-keyword rejection evaluated **outside string literals** (so searching for the
  literal words "CREATE TABLE" still works); no stacked statements; table-name
  validation for `--schema`.
- **Layer 2 — engine enforcement:** `sqlite3 -readonly "file:$DB?mode=ro"`.

Test evidence: 9/9 legitimate reads pass; 13/13 adversarial vectors blocked
(CREATE/DROP/DELETE/INSERT/UPDATE/ALTER/VACUUM/ATTACH/REINDEX/PRAGMA-assignment/
stacked/leading-whitespace/mixed-case); sandbox sha256 byte-identical after 13 attacks.
When the text filter is bypassed entirely and `sqlite3 -readonly` is called directly,
the engine **still** refuses every write: `attempt to write a readonly database`.
Two layers, each sufficient alone.

Convenience modes: `ocdb-ro --search "term" --limit N`, `ocdb-ro --schema part`.

### 2.3 `sqlite-utils` — indexing layer

- **Install:** `pip install sqlite-utils` (v4.2.1; use `--break-system-packages` on
  PEP-668 distros, or install into the WanderGround venv)
- **Provenance:** <https://github.com/simonw/sqlite-utils> — Apache-2.0, ~2,171 ★,
  extremely active (1,200+ commits)
- **Measured on Node 1:** built an FTS5 index over the 1.9 GB / 58,612-part table in
  **6.2 s**; queries returned in **0.33–0.42 s**. Extrapolating linearly, a 46 GB table
  should index in roughly 2–3 minutes. Treat that as an estimate until measured.

### 2.4 What to reject, and why

| Tool | Reason |
|---|---|
| `opencode-sessions-explorer` v0.1.4 | OpenCode **plugin** only. Requires Bun; `node:sqlite` does not exist in the OpenCode plugin runtime; `bun:sqlite` **cannot open URI filenames** (`file:...?mode=ro` → `unable to open database file`), forcing the weaker `readonly:true` form. |
| `opencode-session-search` (sureshmol) v1.0.1 | Plugin only. Builds its own FTS5 sidecar — reintroduces staleness. |
| `arthurtyukayev/opencode-session-search` | Plugin only. 6 commits. |
| `jacobjmc/opencode-session-manager` v0.1.1 | Plugin only. 6 commits, effectively abandoned. |
| `sdxedg3/opencode-memory` | Claims it "wraps opencode.db SQLite + FTS5". **False** — measured: zero FTS tables exist. |
| `transportrefer/opencode-memory-plugin` | Codex JSONL only, not `opencode.db`. |
| `claude-history` v0.1.76 | Good tool (Rust, 498 ★, MIT, has a skill) but **Claude Code / Pi / OMP only** — no OpenCode. Installed on Node 1 anyway for future use. |
| `claude-history-search` (JuneLeGency) | Qt6 GUI, macOS/MLX-centric, Claude Code only. Not a CLI, not portable. |
| `agent-historian`-style FTS plugins | All are Bun-coupled; all lose the strong read-only guarantee. |

**Cross-cutting reason the plugins lose:** the OpenCode plugin runtime is embedded
Bun 1.2 (confirmed live: `BUN_1.2` strings in the binary, `bun-profile` markers).
`node:sqlite` is absent there. So a plugin must use `bun:sqlite`, which rejects URI
filenames and therefore cannot use `mode=ro`. Community plugins accept
`{readonly: true}` on a plain path, which is weaker and, per §0.2, can fail
outright on read-only media.

---

## 3. Backup — do this before touching anything at 46 GB

`cp` on a live WAL database is **not safe**. SQLite's own docs describe the old
shared-lock-then-copy ritual and why it fails, then give the correct alternatives:
<https://sqlite.org/backup.html>

> "If a power failure or operating system failure occurs while copying the database
> file the backup database may be corrupted following system recovery."

Two supported options:

```bash
# OPTION A — VACUUM INTO (writes a compact, defragmented copy; needs only a read txn)
sqlite3 "file:$DB?mode=ro" "VACUUM INTO '/backup/opencode-snap.db';"

# OPTION B — .backup dot-command (uses the Online Backup API under the hood)
sqlite3 "file:$DB?mode=ro" ".backup '/backup/opencode-snap.db'"
```

Both produce a bit-wise consistent snapshot while the database is live. The Online
Backup API holds a write lock on the *destination* only, and read-locks the source
only while reading (<https://sqlite.org/c3ref/backup_finish.html>).

Also back up the sidecars, or take the snapshot **after** stopping OpenCode:
`opencode.db-wal` is 95 MB on Node 1. A `.db` copied without its `-wal` is
incomplete by definition.

**Size sanity check:** SQLite's documented max is 4,294,967,294 pages; at the default
4096-byte page that is ~17.5 TB, at max page size ~281 TB (<https://sqlite.org/limits.html>).
46 GB is well within limits — this is a performance problem, not a format ceiling.

---

## 4. FTS5 index without the staleness trap

This is the section that answers "what actually keeps a live index honest."

### 4.1 The trap

A sidecar index built once is wrong the moment new sessions land. An index that is
stale and *quietly* returns incomplete results is worse than a slow scan, because
the user cannot tell the difference between "not found" and "not indexed yet".

### 4.2 The correct mechanism: external-content FTS5 + triggers

SQLite's FTS5 documentation is explicit that you own consistency, and gives the
pattern: <https://sqlite.org/fts5.html> §4.4 "External Content Tables"

> "It is still the responsibility of the user to ensure that the contents of an
> external content FTS5 table are kept up to date with the content table. One way to
> do this is with triggers."

```sql
CREATE VIRTUAL TABLE part_fts USING fts5(
  text, content='part_extract', content_rowid='id'
);

CREATE TRIGGER part_fts_ai AFTER INSERT ON part_extract BEGIN
  INSERT INTO part_fts(rowid, text) VALUES (new.id, new.text);
END;
CREATE TRIGGER part_fts_ad AFTER DELETE ON part_extract BEGIN
  INSERT INTO part_fts(part_fts, rowid, text) VALUES('delete', old.id, old.text);
END;
```

Two documented gotchas that will bite if ignored:

1. **Triggers do not backfill.** FTS5 docs: *"creating the triggers does not copy
   existing rows from the content table into the FTS index."* You must run
   `INSERT INTO part_fts(part_fts) VALUES('rebuild');` once after creating them.
2. **`rowid` must be populated explicitly.** Writing an `id` *column* instead of
   `rowid` yields `Parse error: unsafe use of virtual table "part_fts"` — see
   <https://sqlite.org/forum/info/b76d4aa3cf4b468c> where SeverKetor explains that
   FTS5 looks rows up as `SELECT <cols> FROM <content> WHERE <content_rowid> = ?`,
   so the rowid is what makes that lookup possible.
3. **Use `BEFORE UPDATE`, not `AFTER`.** Same thread: an `AFTER UPDATE` trigger reads
   the *new* values when FTS5 needs the *old* ones to delete their tokens, so stale
   tokens survive and both old and new terms keep matching.

### 4.3 Why a *sidecar* DB rather than triggers in place

Triggers in place would mean **writing to production `opencode.db`**, which is exactly
what this briefing forbids. Instead:

- Build the index in a **separate database** (`~/opencode-idx.db`).
- Refresh it on demand by diffing against a **high-water mark** on
  `MAX(part.time_created)`:
  - staleness check: one indexed column read, ~0.3 ms
  - if the source high-water mark moved, pull only rows newer than the stored mark,
    insert them, then update the mark
  - measured on Node 1: staleness check 0.3 ms, incremental catch-up trivial for a
    small delta
- The index is a **cache, never a source of truth.** If it is missing, stale, or
  suspect, delete it and rebuild — 2–3 minutes at 46 GB. Nothing is lost.

---

## 5. Concurrency on a live, actively-written database

Measured on Node 1 with OpenCode writing during the reads:

- **Zero `SQLITE_BUSY`** across 50 rapid read transactions against a WAL database with
  a live writer. WAL is designed for this; readers do not block writers.
- **Snapshot stability:** repeated `COUNT(*)` reads returned identical values.
- `PRAGMA busy_timeout` is **0** in this database — no busy handler is configured. With
  WAL this is acceptable for readers, but if you ever see `SQLITE_BUSY` on Node 0,
  set `PRAGMA busy_timeout=5000` rather than retrying in a loop.

One documented hazard worth knowing: checkpoint starvation. From
<https://sqlite.org/wal.html> §6 — *"A checkpoint is only able to run to completion,
and reset the WAL file, if there are no other database connections using the WAL
file."* A long-running read transaction can block checkpointing and let `-wal` grow.
Do not hold a read transaction open across a long scan on a 46 GB database; use short
queries.

---

## 6. What I could not verify, and what I am not claiming

Honesty about the edges of this briefing:

- **Nothing on Node 0 was measured.** I have no shell there (Tailscale ACL blocks SSH
  on port 22; hub TLS fails verification from Node 1). Every Node 0 figure is a
  projection from Node 1's measurements. The row counts from §1 will settle it.
- **The 46 GB search cost is a projection, not a measurement.** I retract the earlier
  "~64 s" figure — it multiplied by file size instead of searchable row count.
- **`ocdb-ro` has not been run against a 46 GB database.** Its logic is size-agnostic,
  but the `mode=ro` + WAL interaction in §0.2 has not been exercised at that scale.
- **Schema drift is live and confirmed.** The commonly-cited community schema reference
  (<https://github.com/madcat-archive/opencode/blob/main/reference/opencode-sqlite-schema.md>)
  is **already stale** for this host: it documents `session.data` as a JSON blob, and
  that column **does not exist** on Node 1. The live `session` table has flat columns
  (`version`, `project_id`, `workspace_id`, `path`, `metadata`, `tokens_reasoning`,
  `tokens_cache_read/write`, `revert`, `permission`, …) and no `data`. Any tool written
  against that doc will fail.

---

## 7. Schema-drift risk — the thing most likely to break a new tool later

This is the deepest risk in the whole domain, and it is documented, not speculative.

OpenCode has had at least four distinct schema-migration incidents in 2026 alone:

- **#36407** (closed, *not planned*) — startup crash `no such column: name` when the DB
  was created by an older version; the legacy `__drizzle_migrations` system could not
  bridge to the newer `migration`/`data_migration` system. In the default TUI the
  error was swallowed and the app **appeared to hang with no diagnostic**.
  <https://github.com/anomalyco/opencode/issues/36407>
- **#34584** — `duplicate column name: cost` on upgrade.
- **#33898** (closed, *not planned*) — migrations could make a DB unreadable by
  *older* binaries. A migration dropped `session_context_epoch.agent`,
  `.replacement_seq`, `.revision`; downgrading to the prior version then failed with
  `no such column: replacement_seq`. The proposal was to adopt an **expand-contract**
  policy. <https://github.com/anomalyco/opencode/issues/33898>
- **#42260** (closed) — `opencode2` (the V2 preview) **migrated the shared
  `opencode.db` in place**, breaking the stable 1.x install with
  `no such table: session_context_epoch` and `no such column: workspace.project_id`.
  `integrity_check` still reported `ok` — **schema drift, not corruption.** The fix
  (#42444) gave the preview an isolated data namespace.
  <https://github.com/anomalyco/opencode/issues/42260>
- **#41217** (closed) — V2 writes a separate `session_v2`/`session_message` family and
  **never imports V1 history**, so V1 sessions become invisible in V2 with no
  supported migration path. <https://github.com/anomalyco/opencode/issues/41217>

**Node 1 today:** `migration` table has 38 rows, latest
`20260622202450_simplify_session_input`. No `__drizzle_migrations` table — so this
install is already past that boundary. No `*_v2` tables present, so this host is
still a clean V1 install.

### 7.1 Defensive measures for Node 0

1. **Pin `OPENCODE_DB_PATH` / `OPENCODE_DB` to a private copy** for any archival or
   secondary tooling, so nothing else can migrate the canonical file. This is exactly
   the mitigation the reporter in #42260 used.
2. **Never run `opencode2` against the production data directory** unless isolated.
3. **Do not write triggers into the production DB** (§4.3) — another CLI version
   applying a migration could conflict with them.
4. **Re-verify column names before trusting any query.** The drift is real and the
   community reference doc is already wrong.
5. Prefer a **separate index database** so an OpenCode migration cannot break your
   search tooling, and your tooling cannot break an OpenCode migration.

---

## 8. Recommendation, in order

**Do this, in this order:**

1. **Run the §1 triage on Node 0.** Get the row counts. Everything else keys off them.
2. **Back up first** — `VACUUM INTO` or `.backup` (§3), plus the `-wal` sidecar.
3. **Install `ochist`** + skill on Node 0. That alone probably solves the immediate
   need, because at <200k searchable rows a full scan is already sub-second.
4. **Copy `ocdb-ro`** from Node 1 to `~/.local/bin/` and verify it against Node 0's
   database with a read query.
5. **Only if the row count says >200k**, build the FTS5 sidecar in a separate DB
   (§4) with a high-water-mark staleness check. Never trigger-sync the production DB.
6. **Set `OPENCODE_DB_PATH`** for any Node 0 tooling, and keep `opencode2` isolated.

**What not to do, in order of how badly it will hurt:**

- ❌ Point raw `opencode db` at production — it will happily execute DDL (§0.1).
- ❌ Use `immutable=1` — it silently ignores the WAL and returns stale rows.
- ❌ `cp` a live WAL database as a backup — corruption risk (§3).
- ❌ Install an OpenCode FTS plugin — Bun-coupled, weaker read-only guard, reintroduces staleness.
- ❌ Trust a schema reference doc, including the popular one — it is already stale (§6).
- ❌ Add triggers to the production database (§7, item 3).

---

## 9. Sources

**SQLite official**
1. Write-Ahead Logging — <https://sqlite.org/wal.html> (§4 read-only DBs; §6 checkpoint starvation)
2. FTS5 Extension — <https://sqlite.org/fts5.html> (§4.4 external content tables; rebuild; `delete` command)
3. Online Backup API — <https://sqlite.org/backup.html> and <https://sqlite.org/c3ref/backup_finish.html>
4. Implementation Limits — <https://sqlite.org/limits.html> (max DB size)
5. URI Filenames — <https://sqlite.org/uri.html>
6. Forum: WAL with read-only access — <https://sqlite.org/forum/info/0667868158167ccb>
7. Forum: VTables, triggers and FTS5 (`rowid` requirement, `BEFORE UPDATE`) — <https://sqlite.org/forum/info/b76d4aa3cf4b468c>
8. Bug: external-content FTS5 index corrupted by a second AFTER UPDATE trigger — <https://sqlite.org/bugs/forumpost/552f36384c7900ef72448f71118f9c6fe8aa2553e7ef617ef7323c3d0f54b104>

**OpenCode upstream**
9. #36407 legacy drizzle migration break — <https://github.com/anomalyco/opencode/issues/36407>
10. #33898 downgrade-incompatible migrations — <https://github.com/anomalyco/opencode/issues/33898>
11. #42260 opencode2 mutates shared V1 database — <https://github.com/anomalyco/opencode/issues/42260>
12. #41217 V1 history never imported into `session_v2` — <https://github.com/anomalyco/opencode/issues/41217>
13. Troubleshooting (log locations) — <https://opencode.ai/docs/troubleshooting>
14. Community schema reference (**stale**, see §6) — <https://github.com/madcat-archive/opencode/blob/main/reference/opencode-sqlite-schema.md>

**Tools evaluated**
15. `simonw/sqlite-utils` — <https://github.com/simonw/sqlite-utils>
16. `adlternative/agent-historian` — <https://github.com/adlternative/agent-historian> (audited at `/usr/local/lib/node_modules/agent-historian/dist/`)
17. `raine/claude-history` — <https://github.com/raine/claude-history>
18. `iamironz/opencode-sessions-explorer` — <https://github.com/iamironz/opencode-sessions-explorer>
19. `sureshmol/opencode-session-search` — <https://github.com/sureshmol/opencode-session-search>
20. `heimoshuiyu/opencode-history-plugin` — <https://github.com/heimoshuiyu/opencode-history-plugin>
21. `markus-kb/opencode-session-tui` (documents the SQLite/JSONL hybrid and real Drizzle columns) — <https://github.com/markus-kb/opencode-session-tui>

**Local evidence (Node 1, this session)**
- Live `PRAGMA` dump, `sqlite_master` inventory, part-type histogram
- Scaling curve: 14.3 / 28.6 / 57.2 / 114.4 / 228.9 / 457.7 MB → 19 / 39 / 78 / 166 / 350 / 621 ms (linear, ~1.4 ms/MB)
- FTS5 build 6.2 s on 1.9 GB; queries 0.33–0.42 s
- sha256 read-only proofs (byte-identical after 5 greps; byte-identical after 13 blocked writes)
- WAL concurrency: 0 × `SQLITE_BUSY` over 50 reads against a live writer
- `immutable=1` staleness: 26 parts behind
- Cold-start embedding trap: `qwen3-embedding:0.6b` 10,645 ms cold vs 122 ms warm

**Well records (this repo)**
- `3becf4f3` — `opencode db` write hazard
- `a3675a88` — no FTS, linear scan cost, cold-start benchmark trap (superseded 2026-10-02: transient FTS5 `part_fts` existed 2026-10-02 02:08–12:30, measured stale, dropped; claim "no FTS" true again post-drop)
