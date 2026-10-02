# Portability Contract

**Rule: nothing in the session-recall stack may assume Node, OpenCode, or this
machine.** The recall tools are the first subsystem intended to graduate into the
custom Omega CLI. Anything that hardcodes an assumption below becomes a porting
liability the day the CLI is built.

Cheap to enforce now. Expensive to recover later.

---

## 1. What the stack is

Three skills + two CLIs, deliberately zero OpenCode plugin coupling:

| Piece | What it is | Coupling to port away |
|---|---|---|
| `ochist` | Cross-agent session search CLI (Node, zero deps) | Node runtime; its own source adapters |
| `ocdb-ro` | Read-only SQL wrapper (bash + `sqlite3`) | bash, `sqlite3` CLI on PATH |
| `sqlite-utils` | Optional FTS5 index layer (Python) | Python + pip |
| `opencode-db` skill | Schema + verified queries | Hardcoded path, hardcoded column names |
| `agent-history` skill | Routes agents to `ochist` | Tool names |

The design principle: **an agent already has a shell.** A CLI composes with pipes;
a plugin returns fixed blobs. `ochist grep … | head` lets the agent control its own
context volume, which is why this stack is CLI-first.

## 2. Assumptions that must not leak

### 2.1 Node

| Assumption | Reality | Port rule |
|---|---|---|
| `node:sqlite` available | Node **≥22.5** only; used by `ochist` | The Omega CLI needs a SQLite binding of its own. Do not assume `node:sqlite` is "the" API. |
| Node is on PATH | On this box Node 22.22.1 | Ship a native binding, or make the CLI shell out like `ocdb-ro` does. |

**Why this matters:** the entire reason `ochist` could not be an OpenCode plugin is
that OpenCode's plugin runtime is embedded Bun 1.2, where `node:sqlite` does not
exist and `bun:sqlite` **rejects URI filenames**. Three runtimes, three different
SQLite stories. Any binding choice must be verified against the actual target runtime
before it is written, not after.

### 2.2 Paths

| Hardcoded | Where | Must become |
|---|---|---|
| `~/.local/share/opencode/opencode.db` | `ocdb-ro`, `opencode-db` skill | A resolved path from config/env. `ocdb-ro` already honours `OPENCODE_DB_PATH` — keep that. |
| `~/.config/opencode/` | skill install location | Whatever the Omega CLI uses |
| `~/.local/bin/` | `ocdb-ro` install | Configurable bin dir |
| `~/.agent-historian/` | `ochist` usage log | Same |

`ocdb-ro` reads `$OPENCODE_DB_PATH` with a fallback. That is the right shape: **an
env var override with a sane default**, not a hardcoded path.

### 2.3 Schema assumptions

The `opencode-db` skill encodes live-verified facts that will drift:

- `part.data` is a JSON blob; `$.type` discriminates the row shape
- **`text` and `reasoning` both store their string at `$.text`** — there is no
  `$.reasoning` key
- `session` is flat columns and has **no `data` blob** (the popular community schema
  reference doc is wrong about this — verified 2026-10-02)

**Port rule: re-verify schema before trusting any query.** `ocdb-ro --schema <table>`
is the escape hatch. Upstream OpenCode had four migration incidents in 2026, one of
which (`#42260`) had a different binary migrate the shared database in place and
break the stable install while `integrity_check` still reported `ok` — schema drift,
not corruption.

### 2.4 Read-only enforcement

Two layers, and **both must survive the port**:

1. Statement allowlist (SELECT/WITH/EXPLAIN/VALUES/PRAGMA; write keywords rejected
   outside string literals)
2. Engine-level enforcement (`sqlite3 -readonly` + `mode=ro`)

Verified independently: 9/9 legitimate reads pass, 13/13 write vectors blocked,
sandbox sha256 byte-identical, and bypassing layer 1 entirely still fails at the
engine with `attempt to write a readonly database`.

If the Omega CLI binds SQLite natively, layer 2 must be expressed in **that** binding's
read-only API. Do not rely on the CLI flag surviving the rewrite.

### 2.5 WAL reality

Read-only access to a WAL database is conditional — SQLite relaxed the old
"cannot open read-only WAL databases" rule only in 3.22.0, and only if the `-shm`
and `-wal` already exist, **or** the directory is writable, **or** `immutable` is used
(<https://sqlite.org/wal.html> §4).

- `immutable=1` **returns stale data** (measured 26 parts behind). Never a fallback.
- A read-only connection still needs physical write access to `-shm`.

**Port rule:** test the read path against a database on read-only media before
shipping. This is the failure mode most likely to appear only in production.

## 3. What is deliberately *not* portable

| Thing | Why it stays host-specific |
|---|---|
| `~/WanderGround/` (MemPalace, `wander`, sqlite-vec atlas) | Local knowledge capture; a different subsystem from session recall |
| MemPalace MCP tools | MCP-shaped, not CLI-shaped |
| `~/.config/opencode/agent/gaming-expert.md` | Different repo entirely |
| The Well `gnosis/well/` corpus | Machine-specific corrections, by design |

Do not generalise these into the CLI. They were not part of this stack.

## 4. Pre-port checklist

Before any of this is considered Omega CLI code:

- [ ] SQLite binding verified against the **target** runtime, not Node's
- [ ] Zero hardcoded `~/.local/share/opencode` paths; env override works
- [ ] Both read-only layers re-verified on the native binding, with evidence
- [ ] WAL read tested on genuinely read-only media (not just `mode=ro`)
- [ ] Schema facts re-verified against the live database via `--schema`
- [ ] No skill instructs `opencode db` (that command has no Omega CLI equivalent)
- [ ] Tool names stable, or the `agent-history` skill updated in the same commit

## 5. Provenance

Findings here are measured on Node 1 (2026-10-01/02) and documented with citations in
`docs/OPENCODE_DB_MANAGEMENT_BRIEFING.md` (35 sources). Runtime/plugin findings were
probed live through OpenCode's own plugin runtime, not inferred from documentation.