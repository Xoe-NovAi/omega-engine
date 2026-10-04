# The Sweetener Duo — Two Portable Systems Built on Node 1

**Document ID:** `FED-MAKALI-N0-SWEETENERS-20260924-01` (revised 2026-10-02)
**From:** Build / Lilith-N1 (Node 1 / XNAi-Asus)
**To:** Makali-N0 (Node 0 / xnai-n0-hp)
**Date:** 2026-10-02 (revised from 2026-09-24)
**Handling:** Operational doctrine + portable code. Safe to share freely.
**Vendored source:** `omega-sweeteners/` at the repo root (committed).
**Federation staging:** `~/node-drive/omega-sweeteners/` (N1 export root; served
over NFS when `nfs-server` is running — see mesh-status transport note).

---

## 0. What This Is

Node 1 built five copy-paste-ready packages in 2026-09. **As of 2026-10-02,
two remain in the Node 0 adoption path** — Ponytail, Context Engineering
Protocol, Wander CLI, and MemPalace Hivemind were removed per Lilith-N1. The
OpenCode DB tools were added as the second sweetener.

**Standing rule applies:** each package lands in your ROADMAP with a status
BEFORE you integrate it. Sequence them (DB Tools → Well) so each layer is
green before the next lands.

**Why the Hivemind was removed:** it was a conflation. MemPalace (the memory
system) and the Hivemind (the agent-coordination logstream) are two
completely different systems that were mistakenly combined into one package.
They should never have been bundled. The operator is working with Node 0 to
unwind that conflation and build each properly on its own.

**Honesty header:** statuses below are per-package and current as of 2026-10-02.
Anything marked scaffolded has never executed end-to-end. Your tree is the
truth — re-verify on N0 silicon.

---

## 1. The Two Packages

| # | Package | Type | Status on N1 | Path |
|---|---|---|---|---|
| 1 | **OpenCode DB Tools** | Read-only session-DB access | 🟢 audited + tested on N1. Ships `ocdb-ro`, both slash commands, and the 46 GB briefing. **Start here on N0** — your DB is 46 GB. | `omega-sweeteners/db-tools/` |
| 2 | **The Well** | Corrections corpus + tools | 🟢 live on N1 at `gnosis/well/` — **71 records**, hardened, 1024-native. Refreshed 2026-10-03, byte-identical to live, 7/7 tests green. | `omega-sweeteners/omega-well/` |

> **Removed from delivery (2026-10-02):** Ponytail (senior-dev review plugin,
> never registered on N1), Context Engineering Protocol (9-step session-close
> ritual — live on N1, but not part of the Node 0 adoption path), and Wander CLI
> (zero-polling CI monitor — scaffold only, never built or installed).
>
> **Added 2026-10-02:** OpenCode DB Tools, promoted from a one-off briefing into
> a first-class package.

### 1. The Well (`omega-well/`)

The weighted corrections corpus from `resources_GNOSIS_LIFECYCLE.md` §4,
packaged for transplant: `well.jsonl` + `WISDOM.md` + `well_storage.py` +
7 tests + a self-contained `Makefile.well` fragment + `install.sh` +
`WELL_INTEGRATION.md`.

**N0 rule (repeated because it matters):** bring up The Well with a **fresh**
`well.jsonl`. N1's 71 records are *reference*, not transplant — they encode N1
incidents and their weights are calibrated to N1 silicon. Read ours, then earn
yours.

**Refreshed 2026-10-03 (was frozen at 19 records).** The package now carries
the **live 71-record corpus** (65 active, 6 superseded) and the **hardened**
`well_storage.py`, verified byte-identical to `gnosis/well/` and green 7/7 on
the package test suite. What changed since the frozen vendor commit
(`2257495f`, 2026-09-26):

- **Per-record isolation** — one malformed record no longer empties the batch.
  This defect silently killed injection on N1 while 114 tests stayed green.
- **`normalizeTags()`** — records whose `tags` is a JSON *array* are handled.
- **`scanned/skipped/errors` result object** — "no data" is now distinguishable
  from "nothing indexed".
- **`make well-verify`** gate (via `Makefile.well`) — audits the real corpus and
  emits the decision behind each finding.
- **Injection dedup + permanence floor** — reserves slots for
  `correction`/`anti_pattern` so pure-recency ranking cannot crowd them out.
- **1024-native embedding dimension** — corrected from the old 768 claim.

The package is now **self-contained**: no host Makefile required.

**Five records added 2026-10-03** (66 → 71). Two are correctness mechanisms
you want before you write your first record:

- **`759c7639` — `superseded_by` must point FORWARD in time.** The *older*
  record carries `status=superseded` with `superseded_by` pointing at the
  *newer* record's id. A backwards pointer inverts the chain, both records
  stay active, and the correction silently never takes effect. A typo'd UUID
  fails loudly; a backwards pointer fails *silently*. If you hand-roll
  supersession anywhere on N0, read this one first.
- **`3a0c851b` — handoff context ≤ 4 KB.** Packet is a pointer (filename +
  size + sha256 + pull URL); bodies live in the Exchange. Measured on
  2026-10-02 from N1: 4.3 KB succeeds, 4.5 KB fails with a JSON parse error
  at transport. Exact threshold ~4.4 KB. On transport POST failure, shrink to
  pointer and resubmit — never retry identical bytes.
- `acf2d7ba` — handoff `packet_id`s require the `ho_` prefix; a bare hash
  returns not-found and looks like a missing handoff (false negative, not an
  absence).
- `a95fd05a` — MemPalace (local memory) and the Hivemind (remote
  coordination) are different systems and are never substitutes. Recorded
  because bundling them was a real conflation here, not a hypothetical.
- `81dd74d3` — superseded by `3a0c851b` above. Kept in the ledger as
  append-only truth.

**Why the supersession record matters most:** the chain-integrity check
passed while `81dd74d3` and `3a0c851b` were *both* active and contradicting
each other. Nothing dangled and no pointer ran backwards — the pointer was
simply never set. A structurally green Well was semantically wrong. Check
semantics, not just structure, when you adopt.

### 2. OpenCode DB Tools (`db-tools/`)

Safe, tested read-only access to your own `opencode.db`. Ships:

- `bin/ocdb-ro` — self-contained bash, **two independent read-only layers**
  (statement allowlist + `sqlite3 -readonly ...mode=ro`). Verified 9/9 legit
  reads pass, 13/13 adversarial vectors blocked, sandbox sha256 byte-identical
  after 13 attacks.
- `commands/db.md` + `commands/recall.md` — the `/db` and `/recall` slash
  commands.
- `docs/OPENCODE_DB_MANAGEMENT_BRIEFING.md` — the 443-line briefing: triage,
  backup, FTS5 sidecar, schema drift.

**Start here.** Your `opencode.db` is **46 GB**; N1's is 1.9 GB. The briefing's
§1 triage gives you the row counts everything else keys off.

**The one hard rule:** raw `opencode db <query>` opens the database
**read-write** and executes DDL/DML — a bare `CREATE TABLE` against N1's live DB
*succeeded*. It is also the fastest path, which is exactly why it is dangerous.
Use `ocdb-ro`. Full detail in the package README.

### 3. MemPalace Hivemind (`mempalace-hivemind/`)

The coordination backbone: Python client (`mempalace_hivemind.py`), full CLI
(`hivemind_cli.py`: brief, wait, list, subscribe, artifact), JSON Schemas
(`event.json`, `artifact.json`), schema validator (`event_validator.py`),
architecture + naming + topology docs, `pyproject.toml`, README, INTEGRATION
guide.

**Carries the core realization** (see mesh-status doc §2): the Hivemind **is**
the MemPalace event logstream — Stream=Wing, Room=Room, Topic=Sub-room,
Event=Drawer, Agent=Entity (`-n1`/`-n0`), Correlation ID=Tunnel. Not a
metaphor; a literal mapping. Entity `-n1`/`-n0` suffixes are **enforced** at
client init, CLI, and schema validation — no bare names cross the wire.

**Status:** code complete on N1; cross-node unproven. The first
`task.request → task.reply` round trip is still the acceptance test.

**⚠️ Packaging bug fixed 2026-10-02.** Sources shipped in `scripts/` while
`pyproject.toml` declared `packages = ["src/mempalace_hivemind"]` — a path that
did not exist. `uv pip install -e .` could not produce a working install, and
the documented `from mempalace_hivemind import HivemindClient` could not
resolve. Sources now live at `src/mempalace_hivemind/` (`__init__.py`,
`hivemind_cli.py`, `validator.py`), matching the declared path; both documented
imports are verified to resolve. If you installed the old layout, uninstall and
reinstall so you are not importing from two places.

---

## 2. Integration Sequence for Node 0

```
1. DB Tools    — install ocdb-ro + ochist; run the §1 triage to get row counts
2. Well        — fresh well.jsonl + Makefile.well targets + first record
```

DB Tools comes first because it is read-only and it tells you what you are
dealing with. Nothing later is safe to attempt without it.

Each step gets a ROADMAP row with a status before you start, and a dated
evidence note when it goes green. Signal readiness per the onboarding
checklist (D5) — then we prove Hivemind cross-node together.

---

## 3. Provenance

Built 2026-09-21/22 on Node 1 (Build agent sessions); vendored at repo root
as `omega-sweeteners/` (commit `2257495f`); staged to `~/node-drive/omega-sweeteners/`
for Federation Drive delivery; briefed to Node 0 via Hivemind
(`federation/pr-delivery-complete`, 2026-09-22). **Revised 2026-10-02:**
Ponytail, Context Engineering Protocol, and Wander CLI removed from delivery
package per Lilith-N1. **Evidence label:** local authorship + packaging;
per-package execution status marked inline above.
