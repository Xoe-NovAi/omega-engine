# OpenCode DB Tools — Portable Package

**Source:** Node 1, session `witty-sailor` (Researcher-Humboldt), 2026-10-01/02
**Status:** 🟢 shipped, audited, and tested on N1
**Purpose:** give Node 0 safe, tested read-only access to its own `opencode.db`
— which is **46 GB** on N0 versus 1.9 GB here. The size difference is the whole
reason this package exists.

---

## The two facts that matter before you touch anything

### 1. `opencode db <query>` is NOT read-only

It opens `opencode.db` **read-write** and executes DDL/DML. On Node 1 a bare
`CREATE TABLE` against the live database **succeeded** (sha256 changed), was
dropped immediately, and `PRAGMA quick_check` returned `ok`. No data lost — but
the hazard is real and measured, not theoretical.

It is also the *fastest* path (1.26 s vs 2.4 s), which is exactly why it is
tempting. **Raw `opencode db` is banned against production.**

### 2. Read-only access to a WAL database is subtler than "open it read-only"

SQLite cannot open a read-only WAL database unless the `-shm`/`-wal` files
already exist and are readable, **or** the directory is writable so they can be
created, **or** `immutable` is used. On read-only media (archived 46 GB DB,
non-owner access) the tempting fallback `immutable=1` **silently returns stale
data** — measured 26 parts behind on Node 1.

Full citations: `docs/OPENCODE_DB_MANAGEMENT_BRIEFING.md` §0.

---

## Contents

| Path | What it is |
|---|---|
| `bin/ocdb-ro` | Self-contained bash. Two independent read-only layers. |
| `commands/db.md` | `/db <SQL>` slash command → `ocdb-ro` |
| `commands/recall.md` | `/recall <term>` slash command → `ochist grep` |
| `docs/OPENCODE_DB_MANAGEMENT_BRIEFING.md` | 443-line briefing: triage, backup, indexing, schema drift |

### `ocdb-ro` — two layers, each sufficient alone

- **Layer 1 — statement allowlist.** First keyword must be
  `SELECT|WITH|EXPLAIN|VALUES|PRAGMA`. Write-keyword rejection is evaluated
  **outside string literals**, so legitimately searching for the literal words
  `CREATE TABLE` still works. No stacked statements.
- **Layer 2 — engine enforcement.** `sqlite3 -readonly "file:$DB?mode=ro"`.

**Test evidence (N1):** 9/9 legitimate reads pass; 13/13 adversarial vectors
blocked (CREATE/DROP/DELETE/INSERT/UPDATE/ALTER/VACUUM/ATTACH/REINDEX/
PRAGMA-assignment/stacked/leading-whitespace/mixed-case). Sandbox sha256
byte-identical after 13 attacks. When the text filter is bypassed entirely and
`sqlite3 -readonly` is called directly, the engine **still** refuses every write.

---

## Install

```bash
# 1. The read-only SQL wrapper
install -m 0755 bin/ocdb-ro ~/.local/bin/ocdb-ro

# 2. Session recall (cross-agent search: OpenCode, Claude Code, Qoder, Codex)
sudo npm install -g agent-historian          # v0.6.0, 184 KB, zero deps, MIT
ochist skill install --global               # → ~/.agents/skills/agent-history

# 3. The slash commands
mkdir -p ~/.config/opencode/commands
cp commands/*.md ~/.config/opencode/commands/
```

Verify:

```bash
ocdb-ro "SELECT COUNT(*) FROM session"
ocdb-ro --schema part
ochist grep "pin trap" --global --limit 5
```

---

## Two gotchas that cost a false negative

- **`--global` is required.** `ochist grep` defaults to *current-project* scope.
  Run from an unrelated cwd it returns empty and looks broken.
- **The term is a regex, not a substring.** Metacharacters are live.

And a discipline note: **a zero-result search is not proof of absence.** Confirm
you passed `--global` and that the term is spelled as it was written
(hyphenation, casing, abbreviation) before reporting "nothing found."

---

## Schema gotchas (verified on N1, 2026-10-02)

- Conversation text lives in `part.data`, a **JSON blob**.
  Filter with `json_extract(data,'$.type')`.
- **`text` and `reasoning` BOTH store their string at `$.text`.** There is no
  `$.reasoning` key — querying it returns NULL and silently matches nothing.
- **`session` is flat columns with NO `data` blob.** The popular community schema
  reference is *already stale* on this point.
- `PRAGMA busy_timeout` is **0** here. Fine for readers under WAL; if you see
  `SQLITE_BUSY`, set `PRAGMA busy_timeout=5000` rather than retry-looping.

---

## What to do on Node 0, in order

1. **Run the §1 triage** in the briefing. Get the **row counts** — not the file
   size. 1.9 GB here held only 14.3 MB of searchable text.
2. **Back up first:** `VACUUM INTO` or `.backup`. Never `cp` a live WAL DB.
3. **Install `ocdb-ro` + `ochist`** and verify with a read query. At <200k
   searchable rows a full scan is already sub-second — no index needed.
4. **Only if row count >200k**, build the FTS5 sidecar in a **separate** DB with
   a high-water-mark staleness check. Never write triggers into production.

| Searchable rows (text+reasoning) | Full scan | Action |
|---|---|---|
| < 200k | < 1 s | **No index.** Use `ochist` as-is. |
| 200k – 2M | 1 – 10 s | Add FTS5 sidecar. |
| > 2M | > 10 s | Sidecar mandatory. |

---

## Hard rules (violating these has already cost someone data)

1. **Never** `opencode db <query>` against production. Use `ocdb-ro`.
2. **Never** `immutable=1` — ignores the WAL, returns stale rows.
3. **Never** `cp` a live WAL database as a backup.
4. **Never** install an OpenCode FTS plugin — the plugin runtime is Bun, lacks
   `node:sqlite`, and `bun:sqlite` cannot use URI filenames, forcing a weaker
   read-only guard and reintroducing staleness.
5. **Never** trust a schema reference doc, including the popular one.
6. **Never** add triggers to the production database.