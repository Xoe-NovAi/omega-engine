---
description: Run a read-only SQL query against the session database via the ocdb-ro wrapper. Use for counts, cost/token totals, table schema, and which sessions touched a file. Do NOT substitute the native `opencode db` command — it opens the database read-write.
agent: build
---

Run a read-only query against the session database using **`ocdb-ro`**.

$ARGUMENTS is the SQL.

```bash
ocdb-ro "$ARGUMENTS"
```

**This command maps to `ocdb-ro`, never to `opencode db`.** Those are different things
and the native one is dangerous:

- `ocdb-ro` — read-only, twice enforced (statement allowlist + `mode=ro`). Safe.
- `opencode db <query>` — opens `opencode.db` **read-write** and executes DDL/DML. A
  bare `CREATE TABLE` against the live database was verified to succeed. **Never use it.**
  (Well record `3becf4f3`.)

If you find yourself typing `opencode db`, stop and use `ocdb-ro` instead.

Also never use `immutable=1` — it ignores the WAL and silently returns stale data.

Schema reminders (verified 2026-10-02; confirm with `ocdb-ro --schema <table>` if unsure):

- Conversation text is in `part.data`, a JSON blob. Filter on `json_extract(data,'$.type')`.
- **`text` and `reasoning` BOTH store their string at `$.text`.** There is no
  `$.reasoning` key — querying it returns NULL and silently matches nothing.
- `session` is flat columns with **no `data` blob** (some external schema docs are wrong).
- Useful columns: `session.cost`, `tokens_input`, `tokens_output`, `tokens_reasoning`,
  `directory`, `title`, `time_created`.
- `ROUND(SUM(cost),2)` leaves float noise (23.4800000000000004). Harmless for display;
  use `printf('%.2f', …)` at the formatting layer if you need exact decimals.

Only `SELECT`/`WITH`/`EXPLAIN`/`VALUES`/`PRAGMA` pass the guard. If a write is genuinely
required, stop and tell the operator — do not attempt a workaround.

Report the raw result. Do not summarize away rows.