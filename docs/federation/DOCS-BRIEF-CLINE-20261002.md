<!-- SPDX-FileCopyrightText: 2026 Xoe-NovAi / SPDX-License-Identifier: Apache-2.0 -->
# DOCS COMPLETION BRIEF — for Cline CLI
**From:** makali_fusion (Node 0) · **Date:** 2026-10-02 · **Priority:** PR BLOCKER

## WHY YOU
The previous agent (Jem) looped: it re-read the same docs repeatedly and hit
~500K context without converging. The cause is scope — TASK 1 below asked one
agent to read 43 files and synthesize them. That is a machine task, not an agent
task. Split it.

## ALREADY DONE — DO NOT REDO
- 23 module docs in `docs/reference/api/` (mcp_core, orchestration, rag, search,
  workers, council, model_registry, monitoring, bridge, cli, doc_reader, eval,
  experiments, infra, integrations, iris, state, tools, training, hub,
  request_queue, research, skills) — committed `b0f…`
- 3 tutorials in `docs/tutorials/`: how-to-add-mcp-tool, how-to-create-wad,
  how-to-federate-node
- 3 guides in `docs/guides/`: how-to-debug-hub, how-to-add-agent,
  how-to-configure-exchange
- `docs/reference/API_REFERENCE.md`
- `docs/federation/N1_FINDINGS_INVESTIGATION_20261002.md`
- `docs/research/WEB_RESEARCH_KNOWLEDGE_GAPS_20261002.md`

## REMAINING — THREE TASKS, DO THEM IN ORDER, ONE FILE EACH
**Rule that prevents the loop: write each file ONCE. Do not re-read a file you
have already read. Do not attempt to consolidate 43 files in one pass.**

### TASK 1 — 5 ADRs (one file each, no synthesis, no re-reading)
Write these to `docs/decisions/`, one file per ADR, Nygard template
(Title / Status / Context / Decision / Consequences / Alternatives Considered).
Max 1 page each. **You may answer entirely from the brief below — do not go
read source code.**

- `ADR-003-file-based-handoff-store.md` — Context: handoff must survive
  context loss, survive compaction, be auditable. Decision: JSON envelopes on
  local disk under `data/handoff/{pending,active,completed,stale,archive}/`,
  not SQLite. Consequences: crash-safe, human-readable, git-tracked; cost is
  no ACID multi-writer (mitigated by flock + O_EXCL).
- `ADR-004-read-only-exchange-pipe.md` — Context: two nodes must move files.
  Decision: GET/HEAD only over Tailscale Serve, writes are 405 by design.
  Consequences: a writable pipe is an RCE surface; manifest+sha256 is the only
  defence; cost is no push (each node publishes its own root).
- `ADR-005-node-suffix-identity.md` — Context: `lilith` existed on N0 and N1;
  the store folded `lilith-n1`→`lilith` and reported `resolved: true`.
  Decision: `-n<N>` is a DISTINGUISHING token (regex `-n\d+$`), never folded;
  unmatched suffix REFUSES. Consequences: node identity is in the name;
  cost is suffix discipline on every sender.
- `ADR-006-sidecar-receipt-journal.md` — Context: 0 of 10 packets had
  `read_by`; read and unread were identical; mutating the envelope crashed on
  legacy packets. Decision: append-only `{id}.receipts.jsonl` sidecars, fsync
  per receipt, envelope never mutated. Consequences: M28-clean pure addition;
  cost is a second file per packet.
- `ADR-007-mtime-version-probe.md` — Context: hub ran pre-fix code for hours
  because uptime was green while the code was stale (P0-3). Decision: stamp
  source mtimes at startup, compare on demand, report STALE. Consequences:
  catchable in CI; cost is mtime-only fidelity (a same-mtime edit evades it).

### TASK 2 — 2 explanation docs (`docs/architecture/`)
- `HOW_THE_HIVEMIND_WORKS.md` — awareness (heartbeat, presence only), handoff
  (packets on disk), receipts (read state in sidecars), discovery (pointer
  files in the Exchange manifest; `inbox`/`awareness(get)` are BANNED as
  absence evidence). Include an ASCII flow diagram and the three laws.
- `HOW_THE_EXCHANGE_WORKS.md` — publish root (`~/exchange` symlink → real
  store), manifest (`served_by`, `url_form`, sha256 per entry), pull + verify,
  read-only enforcement (GET/HEAD only, 405 on write, `ProtectSystem=strict`),
  node identity via `OMEGA_NODE_NAME/HOST/PORT`. ASCII flow + invariants.

### TASK 3 — `docs/api/API_REFERENCE.md`
Do NOT read all 43 files. Instead: read `docs/reference/API_REFERENCE.md`
(already written, 9.4 KB) and `docs/reference/api/README.md`-style headers.
Produce a **thin index** that lists each module, its one-line purpose, and a
link to its detail file under `docs/reference/api/`. An index, not a
rewrite. Max 2 pages.

## MANDATES
- M1 no `import asyncio` in `src/omega/` — you are writing .md only.
- M26 reference docs pass `make doc-llm-validate`.
- Every file: SPDX header, no bare `*.md` gitignore surprises (the repo
  now un-ignores `docs/**/*.md`).

## ACCEPTANCE
- 5 ADR files exist in `docs/decisions/`
- 2 explanation docs exist in `docs/architecture/`
- `docs/api/API_REFERENCE.md` exists as an index
- `make doc-llm-validate` passes
- Do NOT commit. Report the file list when done.

## ANTI-LOOP DIRECTIVE (read this twice)
The last agent failed by re-reading. Your budget: read at most 6 files
total. Everything you need is in this brief. If you feel the urge to survey
`docs/reference/api/` again — do not. Write the ADRs from the text above.
