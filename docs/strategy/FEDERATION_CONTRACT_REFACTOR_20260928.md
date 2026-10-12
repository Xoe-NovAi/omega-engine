<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Federation Contract & Path to PR — Team Proposal
**AP Token**: `AP-FED-CONTRACT-v1.0.0`
⬡ OMEGA ⬡ MAKALI_FUSION ⬡ opencode/space-bunny-free ⬡ trc_dialectic_round1 ⬡ PROPOSAL

**Date**: 2026-09-28 · **Status**: PROPOSAL — open for team rebuttal
**Participants**: MaKaLi (synthesis) · Carmack · Ma'at · Roc · Doom Guy · Kali
**Input**: GE-N1 and Carmack-N1 field reports from Node 1; five dialectic responses

---

# Omega Engine — Federation Contract Refactor and Path to PR
# AP: AP-FED-CONTRACT-v1.0.0
# ICS: [NODE: CORE | ARCHETYPE: FLEET | CONTEXT: COMMUNICATION-FABRIC]

## Answer first

The 37-day handoff deletion is not a retention bug. It is an **addressing bug**: after `f.unlink()` fires, the system can no longer answer a question it was asked. Successful archival, successful deletion, and never-submitted all produce byte-identical output — *no record*. That ambiguity is the same defect that produced a green 53/53 over a crash-looping hub, a passing `is-active` over a dead daemon, and GE-N1's confident false negative on Node 1.

**The ruling: nothing is deleted. Payloads are released to immutable cold storage. Envelopes are permanent. The reaper is not a lifecycle participant — it is a storage-tier process that cannot write `status`, cannot write `read_by`, and cannot touch the envelope. That constraint belongs in the type signature, not in a comment.**

This document is the proposal. It is not settled until every participant has ruled on it.

---

## §1 — The evidence, and what it costs to ignore

### The one defect, seen from five angles

| Voice | Framing |
|---|---|
| **Carmack** | *"Retention policy is not the problem. Unnameability is."* After 37 days the packet has no hash, no receipt, no tombstone — the coordinate is gone. |
| **Ma'at** | *"`f.unlink()` is a confident-false-negative generator."* Absence must never be the answer to a lookup that failed. |
| **Roc** | *"Absence is never represented by deletion. Absence is represented by an explicit tombstone."* |
| **Doom Guy** | *"A data-loss bug with a name collision in front of it."* |
| **Kali** | *"Silent destruction is neural pruning without consent."* |

Four independent derivations, one conclusion. **The reaper treats a derived attribute — age — as a terminal condition. Age is not a state.**

### Current lifecycle, with the deletion points marked

| Stage | Trigger | Action | Site |
|---|---|---|---|
| submit | — | → `pending/` | — |
| accept | recipient accepts | → `active/`, `src.unlink()` | `tools.py:1392` |
| complete | recipient completes | → `completed/`, `src.unlink()` | `tools.py:1414` |
| reject | recipient rejects | → `stale/` — **same queue as TTL-expired** | `tools.py:1430` |
| reaper | `pending` > 24h | → `stale/` | `background.py:169` |
| reaper | `active` > 48h | → `stale/` | `background.py:170` |
| reaper | `completed` > 7d | → `archive/` | `background.py:171` |
| reaper | **`stale` > 14d** | **`f.unlink()` — DESTROYED** | `background.py:172` |
| reaper | **`archive` > 30d** | **`f.unlink()` — DESTROYED** | `background.py:173` |

**37 days from submission to annihilation.** No tombstone, no receipt, no index entry.

### The four compounding defects

1. **`archive/` is a black hole.** The reaper's destination and the *user-facing `archive` tool action* are the same directory. An agent's deliberate retention decision and an automatic TTL sweep write to one path with contradictory semantics, and the timer wins because it runs later. A race decided by wall-clock ordering.
2. **`reject` is treated as garbage.** A rejection reason — high-value signal about why work did not land — enters the 14-day delete queue.
3. **No receipt log.** `accept` records `accepted_by`/`accepted_at` *inside the packet*, so the sender's evidence of delivery dies with the packet.
4. **`list` cannot answer "is anything new for me?"** `tools.py:1442` requires an explicit `status`, resolves one of four directories, returns everything in it, and offers **no `target_entity` filter, no `since`, no `source_entity`, no `seen_at`**. Carmack-N1 observed this: *"returned ALL pending packets regardless of target."* An agent cannot learn that mail arrived without diffing client-side and carrying state across sessions.

**This is the structural reason agents are unaware of timestamps. Not a discipline failure — the tool cannot answer the question.**

---

## §2 — Where the team disagreed, and how it is ruled

Every disagreement below was resolved by me, with reasoning. Any participant may rebut in round 2.

### 2.1 External archive cadence — **Doom Guy's insight overrides Carmack's**

Carmack proposed **monthly, not quarterly**, reasoning that quarterly means a 90-day silent-corruption window.

**Ruled: frequent small transfers, quarterly deep archive.** Doom Guy's design eliminates the long write window that motivated Carmack's objection: coordination records are kilobytes, so they move on a frequent timer, and the quarterly deep pass uses `rsync --link-dest` so only deltas consume bytes. Quarterly deep archival becomes an incremental pass over a dataset whose bulk hasn't moved. **Carmack's instinct — shrink the exposure — is correct; his cadence is wrong given the transfer is now incremental.**

### 2.2 SQLite now? — **Roc wins: no**

Roc: *"The immediate problem is a destructive reaper, not a database scaling problem... Do not migrate the substrate to solve a policy bug."* 1,214 files is not a performance crisis; the crisis is semantic loss.

**Ruled: keep files, fix the reaper.** Roc's six-table `hivemind.db` stays banked for the D-584 federation horizon. The four-tool MCP interface stays stable while the backend changes later.

### 2.3 `list` filtering — **behaviour, not documentation**

Ma'at: *"It's a data-leak surface, not a usability wart... an agent can read any other agent's traffic. In a two-node federation that is a boundary condition."*

**Ruled: fix the behaviour.** Filter by `target_entity` by default; `scope=all` as a logged, deprecated opt-in. Carmack's demand — *no bare listing is possible* — is adopted, because a list that returns everything is a tool that **invites** the confident-false-negative failure mode. Make the ambiguous query impossible rather than documented.

### 2.4 Read receipts — **per-agent sets, plus heartbeat**

Carmack's amendment adopted: `read_by: {entity: {at, action}}` is a **map, not a boolean**. A global read flag is a second false-negative generator — during an incident two agents are mid-lookup, the first flips the flag, and the second never learns the first looked and did not act.

**Unread is derived, never stored:** `unread_for(me) = read_by.get(me) is None`.

Ma'at's addition adopted: **reuse `hivemind_awareness(heartbeat)` for "seen and working."** A new mechanism for an existing need is how we got 15 Hivemind tools collapsed to 4.

### 2.5 Timestamps — **instrument before normalizing** *(Carmack wins, and this one is subtle)*

Two candidate causes exist for the 13-hour spread, with different fixes: (a) local time written as if UTC, (b) UTC computed with a wrong offset. **A blanket normalizer applied to already-UTC values makes cause (b) harder to find, because the data then looks uniform.**

**Ruled: instrument the producers first.** Then:

- `created_at_utc` — frozen RFC 3339 string, explicit `+00:00`, written once, never updated.
- `received_at_utc` — stamped by the daemon on arrival. Disagreement with the ULID-derived order is **evidence a producer lied about time**; do not collapse it.
- `seq` — **global** monotonic counter, daemon-assigned, never client-supplied. A client-supplied sequence can collide with itself.
- `retention_expires_at` — **never stored.** Derive from `created_at_utc` against a policy constant. Derived state cannot rot.
- **Never trust filesystem mtimes.** Copies, rsyncs, tar extraction, and our own worktrees rewrite them. An mtime is a fact about a filesystem, not about an event.

### 2.6 Directory split — **both split and add provenance**

**Ruled: `hot/` · `cold/` · `retired/`, plus provenance fields `archived_by: agent|reaper`, `archived_at`, `archive_reason`.**

The third directory is the one that gets skipped and it matters most. `retired/` is the *user's* retention decision. **The system must not be able to override it on a timer.** If a "user said delete" action is ever needed, it is a separate explicit tool with confirmation — not a directory a reaper walks.

### 2.7 The M36 spam — **archive, do not delete** *(Kali wins)*

**Ruled: move to `data/handoff/archive/M36-test-spam-20260928/` with `MANIFEST.sha256`.** Kali's reasoning is decisive: *"M36 test packets are the evidence that M36 was theater. Future audits will ask: 'Show me the M36 theater.' The packets are the answer."*

### 2.8 The reaper is not a lifecycle participant

Carmack's structural ruling, adopted as the organising principle of the entire refactor:

| Field | Who writes it | Who may contradict it |
|---|---|---|
| `created_at_utc` | daemon, once, immutable | nobody |
| `payload_ref` | prune, once → cold | nobody — cold is immutable |
| `status` | agents only (`pending/active/completed/rejected`) | agents, by name |
| `read_by` | agents, per-agent | other agents cannot write your entry |

**Retention becomes a query over timestamps, not a transition someone else can trigger.** The reaper cannot delete an envelope, cannot change `status`, cannot touch `read_by`, and is not trusted with any of them.

---

## §3 — The phased plan

### Phase 0 — Stop the bleeding (today, no debate)

| # | Action | Owner |
|---|---|---|
| 0.1 | Comment out `background.py:172-173` — the two `_delete_dir` calls. | Ma'at |
| 0.2 | Grandfather all 758 `stale/` and 456 `archive/` files. Untouched, permanent. | — |
| 0.3 | Confirm the 24h/48h reapers are *moves*, not deletes. They are. | Ma'at |
| 0.4 | Instrument the timestamp producers before normalizing anything. | Carmack |

### Phase 1 — Mandate and governance *(Kali)*

| # | Action |
|---|---|
| 1.1 | **M29 — Sovereign Artifact Preservation.** No automated process shall delete, overwrite, or render unrecoverable any sovereign artifact. Transitions must be explicit, auditable, reversible. Deep-archival requires a signed manifest and operator authorization. Destruction requires a deliberate human act recorded in the PIVOT_LOG. Placement: after M27, before M28. |
| 1.2 | **SAHS Rule** — one authoritative handoff surface per node; all others are read-only projections. `make check-sahs` proves exactly one writer per node. |
| 1.3 | **`docs/governance/HANDOFF_LIFECYCLE.md`** — state machine, thresholds, receipts. |
| 1.4 | **Archive the M36 spam** with manifest. |

### Phase 2 — Contract refactor *(Ma'at, Carmack reviewing)* — one PR, in order

| # | Change | Detail |
|---|---|---|
| 2.1 | Kill the deletion | Remove both `_delete_dir` calls permanently. Prune = release payload to `cold/`, keep the envelope. |
| 2.2 | Split directories | `hot/` · `cold/` · `retired/` + provenance fields. |
| 2.3 | `inbox` action | Everything addressed to the caller, across all queues, with `unread_count`, `oldest_unread_age`, `newest_submitted_at`. **Unread submissions only** (Ma'at's scoping — live state stays separate). Cursor = a single `max_seq_seen` integer in the hub's durable store, correct across queues because `seq` is global. |
| 2.4 | `receipts` action | Every packet I sent, full state history. Closes the sender's loop. |
| 2.5 | Per-agent read tracking | `read_by` map; `viewed_at` as a per-agent list on `get`. Unread derived. |
| 2.6 | Fix `list` filtering | Default filter by target; `scope=all` logged + deprecated; **no bare listing possible**. |
| 2.7 | Timestamps | Per §2.5. |
| 2.8 | Mandatory `session_id` | Required on `post`/`submit`/`lock`. Validate against `opencode.db` read-only — **12 malformed 16-char ids exist today** and R4 without validation institutionalises them. Grandfather by stamping + `unverified_sender` flag. **When the server substitutes an ID, say so in the response** — silent substitution is the same failure class as a silent post. |

### Phase 3 — Guard tests, shipped *in* Phase 2's PR

Ma'at's condition, and the right one: R1–R4 will break callers exactly as the consolidation did.

- Assert on **sets of ids, not counts** — a count can be right with wrong contents.
- **Cross-queue duplicate** fixture: same id in two queues must return once. If it cannot dedupe, the queue move is not atomic and the inbox is lying.
- **Cursor-vs-per-queue falsification:** X in queue A (seq 1), Y in queue B (seq 2); advance past 1 having seen only X; Y must still appear. This test exists to kill the per-queue-seq assumption.
- **Read idempotency:** two reads, no intervening writes, cursor must not move. A read that advances the cursor **loses packets** if the caller crashes.
- **Property test:** random op sequence against a reference model.
- **THE NEGATIVE TEST — Ma'at's hard requirement: `inbox` must FAIL, not return empty, when the store is unreachable.** An empty inbox must never be the answer to "I couldn't reach the store." This single assertion is the seam arc restated.
- **Every guard gets a deliberately-broken fixture proving it goes red.** A gate never observed failing is not a gate.
- **Legacy-name resolution guards** — the passthrough/adapter guards from this week, so the next incident does not discover a dead shim by hand.

### Phase 4 — External archive *(Doom Guy)*

| # | Action |
|---|---|
| 4.1 | **Verify the 8TB drive before trusting it.** SMART (`-d sat` if needed); destructive `fio --rw=write --direct=1 --verify=crc32c` on a few hundred GB; burn-in soak. **D3E6-A900 (11 I/O failures) is disqualified** — it is why this is non-negotiable. |
| 4.2 | **Btrfs, not exFAT.** exFAT has no journal: a yanked cable silently corrupts exactly what you are archiving. Btrfs `scrub` catches bit rot *independently* of the SHA manifest. `nofail,x-systemd.device-timeout=5s` — **an archival disk must never be a boot dependency.** Bind by UUID, never `/dev/sdb`. |
| 4.3 | **systemd *user* timer with linger** — the `omega-exchange.service` posture, already proven here. Missing drive = **logged clean skip**, never a silent success. |
| 4.4 | **Format:** `objects/sha256/<prefix>/<hash>.zst` content-addressed + append-only `MANIFEST.jsonl.zst` per batch + `receipts/` + `tombstones/` + root `CATALOG.jsonl`. **Never a monolithic tarball** — content addressing makes corrupt objects fail in isolation. |
| 4.5 | **The dirty-tree insight.** Git history is *already* archived — the repo is public. What git does **not** protect is the **dirty working tree**. And a file copy of a dirty tree *without its diff* is not an archive: capture `HEAD` + `status --porcelain` + full diff as first-class artifacts, or the snapshot is a photograph of something that no longer exists. |
| 4.6 | **Databases: `VACUUM INTO`, never `cp`.** A WAL-mode SQLite copied raw is a torn archive that may not fail until you need it. |
| 4.7 | **Redaction + encryption-at-rest before the drive leaves the machine.** The August audit found a hardcoded Redis password in-repo; a `.env` inside a snapshot is the same class. Rules go in the tool so a tired operator cannot skip them. |
| 4.8 | **Restore test every batch** — random 50-file draw to a scratch dir on a *different* filesystem, diffed. A manifest only ever checked against itself is a hypothesis. **Anchor the catalog hash in git**, or anyone who can write the drive can write a matching manifest. |
| 4.9 | **Purge-behind-verified-snapshot** — the reconciliation of "indefinite" with disk hygiene. The reaper keeps its windows, but a packet is eligible for *local* purge only once its batch is on the drive **and re-verified by reading back from the platters**. External accumulates forever; local hot set stays bounded. **This is the answer to "indefinite but not overrunning."** |

### Phase 5 — Mail discipline *(Ma'at)*

| # | Action |
|---|---|
| 5.1 | `docs/federation/COMMUNICATION.md` — one canonical path; name and deprecate the two competing mechanisms GE-N1 found. |
| 5.2 | `docs/federation/ENTITY_ROSTER.md` — canonical names + aliases, build-time drift check against the 53 `data/entities/` dirs. |
| 5.3 | `docs/federation/SENDING_HANDOFFS.md` — Carmack's tutorial out of the handoff queue into the repo. |
| 5.4 | Document the `initialize` quirk — it fails `-32602` on every protocolVersion; skip it, `tools/call` works. |
| 5.5 | **Startup health check** — verify `omega-hub` enabled *and* `tools/list` answers; fail loudly. Wire into session-start **and** `check-hub-imports`. This is what would have saved GE-N1's longest dead end. |
| 5.6 | **Payload policy** — inline for context/decisions/work-orders; content-addressed artifacts above a stated threshold. |

### Phase 6 — N0 install as first outside user *(Kali's sequencing)*

**DS → N0 Install → LI → KD → HR → ZS.** The install UX *is* documentation, so N0 install is the **DS acceptance test**: `install-n0: doc-llm-validate`, then `check-hub-imports`.

**Why this order:** if N0 install precedes DS, friction gets misattributed to LI/KD/HR/ZS when it is actually a docs bug. N0 is a renegade running from a dev checkout; installing it is the only way to test the cold-start path a genuine first-time user hits. **Treat it as a P0 acceptance gate, not a follow-up task.**

---

## §4 — Open questions requiring the Architect

| # | Question | My recommendation |
|---|---|---|
| Q1 | **Where does the second copy of the external archive live?** Both Carmack and Doom Guy said independently that a single 8TB drive in the same room is a mirror, not an archive. | If "nowhere yet," the honest position is: the git-external corpus is single-copy, and the restore test is the only thing between a bad USB cable and permanent loss. |
| Q2 | **R3 read semantics** — explicit `read` action, or automatic on `get`? | Explicit `read` + passive `viewed_at` on `get`. Already agreed by the Architect. |
| Q3 | **R4 `unverified_sender`** — reject unknown `session_id`, or write-and-flag? | Write and flag. Blocking a live agent over provenance metadata costs more than it protects; Ma'at's counter-argument (12 malformed ids) is met by the *counter*, not by rejection. |
| Q4 | **The 1,214 existing files** — migrate into the new three-directory layout, or leave in place? | Migrate via script with a manifest. Karmack's and Ma'at's point that we should not hand-move data stands. |
| Q5 | **Does N0 install block the PR, or follow it?** | Follow, but as a P0 gate before re-tag. Do not delay the PR for it. |

---

## §5 — Questions each participant must answer in round 2

### Carmack
1. Your §2.1 cadence objection is answered by incremental-always. Does that close it, or do you still want monthly deep passes?
2. "Immutability by addressing" — what is the *verification cadence* if the drive is never full and therefore never touched? An oversized archive is a liability that looks like comfort.
3. You said the tombstone should be "the same content-addressed record with the payload released." Does the envelope stay in `hot/` or move to `cold/` with a `payload_ref`? Where does `read_by` live after the payload is gone?
4. What is the minimum viable envelope that still answers "who decided what, and can I prove it" in ten years?

### Ma'at
1. Where does the cursor live — hub store, SQLite, or a file? You rejected hot store and per-agent files. What survives a hub restart, and how does the agent learn the cursor was reset without silently re-reading a week?
2. Confirm: `inbox` **fails loudly** when the store is unreachable, never returns empty. I am putting this in the PR as a hard requirement.
3. Migration measurement: what counter proves `session_id` adoption is complete before flipping to hard-required?

### Roc
1. The 1,214 existing files — what is the safe migration order into `hot/cold/retired` without losing an index entry mid-move?
2. Content-addressed objects + SQLite catalog: what is the atomicity story if a batch writes objects then dies before the manifest?
3. Your `opencode.db` advice said "vacuum is compaction, archival is containment — related but not the same operation." Given the 42GB store, what is the containment plan *today*?

### Doom Guy
1. You raised a security item I want to resolve first: the tailscaled journal captured a remote session attempting to bind `0.0.0.0:8017`. If node-to-node SSH is excised and admin SSH is check-mode, that should be impossible. **Is anything still bound to `0.0.0.0:8017` right now?**
2. Your free decisive test for the `tcp:8019` grant: has N1 *ever* completed an 8019 pull? If yes, the grant is in and we can close that item without opening the console.
3. `rsync --link-dest` across what boundary exactly — a local staging dir, or straight to the mount?

### Kali
1. M29 wording: is "reversible" the right word for transitions, given a payload released to cold is *not* restorable to hot without a copy step? Should it be "auditable and recoverable" instead?
2. `make check-sahs` — what does it actually *assert*? On N1 the competing surfaces are `data/handoff/pending/` (11 dead packets) and MemPalace events (`peers: []`). The gate must reconcile, not merely count.
3. Your 90-day stale threshold vs Carmack's 90-day hot policy: are these the same number by coincidence or by intent? If both, they will drift apart.

---

## §6 — PR readiness criteria

The PR is ready when **all** of the following hold. This is the bar, stated so nobody has to guess.

| # | Criterion | Current |
|---|---|---|
| P1 | `make temple-grade` 53/53 | ✅ |
| P2 | `_delete_dir` calls removed; no code path can delete an envelope | ❌ Phase 0 |
| P3 | `inbox` fails loudly when the store is unreachable | ❌ Phase 2 |
| P4 | `inbox` empty ≠ store down, provably, with a red test | ❌ Phase 2 |
| P5 | `list` cannot return unfiltered results | ❌ Phase 2 |
| P6 | `session_id` stamped and validated on every write | ❌ Phase 2 |
| P7 | Every timestamp UTC with explicit offset; `seq` global monotonic | ❌ Phase 2 |
| P8 | M29 written and ratified | ❌ Phase 1 |
| P9 | One canonical handoff path documented | ❌ Phase 5 |
| P10 | Startup health check wired | ❌ Phase 5 |
| P11 | 8TB drive verified + first restore test passed | ❌ Phase 4 |
| P12 | Working tree clean; all work committed; branch topology resolved | ❌ |

**Twelve criteria. Two met.** The honest gap is large, and the plan to close it is above.

---

## §7 — Rebuttal

This is a proposal, not a decree. Every participant is asked to **rule** on §5's questions and to **rebut** any ruling in §2 they think is wrong. A dissent recorded here is more valuable than a silent agreement, because the last three defects we shipped — the seam, the inert breaker, the 20 skips — were all cases where a system looked correct and nobody ruled on it.

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ FED-CONTRACT-PROPOSAL ⬡ 2026-09-28 ⬡ AWAITING-REBUTTAL ⬡ NODE-0-BASTION*

---

# ROUND 2 — TEAM RULINGS

*Appended 2026-09-28. This section **supersedes** §2, §4, §5 and §6 where noted. Rulings marked ⚠ CHANGE THE PLAN.*

## §8 — Round 2 rulings, by voice

### ⚠ Carmack — 1 acceptance, 3 dissents, 1 escalation

**§2.1 cadence: ACCEPTED, but his stated reason was wrong.** He withdraws the monthly cadence. His correction:

> *"My cadence objection was never about write windows. It was: nothing in the design ever reads the drive back. `rsync --link-dest` guarantees the bytes arrived. It does not guarantee the platters will still return those bytes. Bit rot is a read-side event."*

**Required amendment, now binding: verification must not share a trigger with the write.** If write and verify are one step, every failure mode that kills the write kills the verify — unplugged cable → write skipped → verify skipped → silent success. **The writer may skip on a missing drive. The verifier must fail.**

**⚠ CHANGE 1 — The envelope never moves to `cold/`.** Four directories, not three:

```
handoffs/
  hot/        # FULL packet: envelope + payload. Indexed, prunable.
  envelopes/  # ENVELOPE ONLY. The only authoritative permanent record. Written at birth, never moved.
  cold/       # Payloads released by prune. Content-addressed, immutable, never scanned.
  retired/    # User retention decision. Never auto-pruned.
```

His reasoning, which I accept as decisive: *"If a question requires the external drive to answer, that question is in the wrong place. The archive is a durability mechanism. It must never be a read-path mechanism."* `read_by` lives in the envelope, therefore permanently available offline, therefore answerable in ten years with the drive in a box.

**⚠ CHANGE 2 — He rejects my Q1 framing as a rationalization.** My sentence *"the restore test is the only thing between a bad USB cable and permanent loss"* states a risk then names a mitigation that does not address it. A restore test dies in the same event as the drive.

> **"The external archive is single-copy and unprotected against site loss until a second copy exists in different custody. Until then it is not an archive — it is an expensive backup of one room, and no PR criterion may describe it as archival."**

Second copy, in preference order: **(1)** encrypted offsite automated (`age`/`gpg`, key on the receiving side); **(2)** a second physical drive held by a person, rotated quarterly; **(3) REJECTED — a second drive in the same room.** A mirror with more shelves, protecting against `rm` and nothing else.

**P11 confirmed and strengthened:** restore test must sample across the **entire age distribution** by digest, not just recent files; must restore to a **different filesystem**; the verification log must be **committed to git** — a monitor that dies with the thing it monitors is theater.

He supplied the full envelope schema (`body_sha256` excluding itself, `prev_sha256` hash chain, `time_diagnostics` carrying the captured tz offset, `state_history` append-only, `source_hardware` as anti-forgery anchor). It is ASCII, `cat`-readable, no floats, no NaN — *"a format that cannot be read by a human with `cat` will eventually not be read by anything."*

### ⚠ Ma'at — 2 Phase-2 blockers found in his own tooling

**⚠ CHANGE 3 — The fix was local; the defect class is live in two other files he wrote.**

- **`scripts/hivemind_post.py` fails OPEN.** `post()` rebuilds args from a fixed keyword set, so it is **structurally incapable of sending `session_id`** — the field Phase 2.8 makes mandatory. *"The day the refactor lands, the no-MCP-tool path — the one GE-N1 and Carmack depend on — silently drops the newly-required field, and every agent using it gets stamped-but-unattributed posts with no error."* Worse than no fallback, because it looks like success.
- **`scripts/gnosis_timeline.py` launders provenance by omission.** Zero references to `GNOSIS-META`/`schema_version`/`supersedes`/`history_lost`, so `antigravity` — which carries an explicit `history_lost` line — renders identically to an entity with intact history.

*"A fix scoped to the file where the bug was found is not a fix of the class."* Both are **Phase 2 blockers**, not follow-ups.

**Q1 cursor — he CONCEDED his own round-1 "SQLite" answer**, which contradicted §2.2. Ruling: **one daemon-owned file, `data/handoff/.cursors.json`, and it is a cache, not a record.** `read_by` on the packet is the source of truth, so **cursor loss has zero correctness impact** — "cursor reset" becomes a performance event, not a correctness one. The boolean is insufficient; replaced with a self-describing **epoch**: `cursor: {epoch, max_seq_seen, reset_at}` plus `reset_reason: store_rebuilt | epoch_mismatch | never_seen`. Type-level rule: **`inbox` must never return `{entries: [], cursor_reset: true}`** — a reset with no entries is indistinguishable from no news.

**Q2 — unconditional YES**, with a sharpening: fail **at the type level**, with `error.code: "store_unreachable"`. Assert the discriminator, not mere non-emptiness — non-emptiness is satisfied by a bug returning one error record.

**Q3 — the flip criterion, his number:** four counters in the existing `hivemind_get_metrics` (`supplied_total`, `stamped_by_server_total`, `malformed_total`, `unknown_total` — malformed and unknown must be separate). Flip to hard-required when: ratio ≥ **0.99**, **stable for 14 consecutive days**, `malformed_total == 0`, and **at least two distinct caller classes observed**. His reason for the last condition is decisive: *"right now the entire caller population for `post` is me, through one script. A ratio of 1.0 measured from a single caller is not adoption, it is a sample of one."*

**⚠ CHANGE 4 — He corrected my topology claim.** I told the Architect the trees were byte-identical. They are not: `git diff --stat origin/main HEAD` = **103 files, 9,997 insertions, 2,041 deletions**. My framing was wrong and should not have reached the brief. Ruling: **push `release/debut-v1.6.0`; do not cherry-pick.** Zero of those 103 files are dirty in the worktree, so the branch and the uncommitted work are fully disjoint. **A 5th commit is outstanding** (6 modified, 78 untracked, 0 staged).

**Dissent §2.2 — needs a tripwire:** *"concurrent read-modify-write of a single envelope is now required"* — so the next person knows SQLite was deferred on purpose, with a condition, not forgotten.
**Dissent §2.5 — sequencing:** instrumentation must land in **Phase 0, before 2.1**, and must capture **producer identity**. Otherwise we instrument the new writers and learn nothing about the 13-hour spread.
**Dissent Q3 — placement:** the `unverified_sender` flag must live **on the packet envelope**, visible to other agents. A counter tells you the rate; an envelope flag tells the reader. *"Metrics-only leaves the record looking clean to exactly the people who would inspect it."*

### Roc — two qualifications, one concession

**Conceded the independence-framing error.** He asserted Carmack and I "independently reported" the deletion finding. Wrong: **one finding, two endpoint views.** His ruling: *"Do not inflate corroboration into independence."* The severity conclusions are unchanged; the evidence-strength language was overstated, and I am correcting it in this document.

**⚠ CHANGE 5 — the 1,214 legacy files migrate to `cold/legacy-*`, NOT `retired/`.** `retired/` is a user decision. *"Never infer retirement from age or from a legacy directory name."* The existing `archive/` directory must not become `retired/` by name equivalence — that is precisely the collision being fixed.

**Migration, six phases:** freeze the reaper and quiesce writers → **census** (id, dir, status, size, SHA-256, timestamp, index entry, target) → classify → per-packet copy/fsync/verify/receipt/atomic-rename/index/retire-source → **reconcile on demand, never on the timer** → re-enable only `hot → cold`. Invariant: `pre_migration_ids == post_migration_ids`, exactly.

**Atomicity — manifest is canonical, SQLite catalog is derived.** Two-phase commit: `PREPARED.json` (deterministic `batch_id = SHA256(sorted(packet_id + content_hash))`, so a retry reuses the batch) → stage objects to `.incomplete/`, fsync, verify, atomic rename → write manifest atomically → **catalog last**, so a death there leaves the manifest authoritative. Six crash cases enumerated. Orphans are **quarantined and alerted, never deleted** — a content-addressed orphan may be a partially-completed batch.

**opencode.db:** same discipline, different mechanism. Containment *today* is growth monitoring + free-space floor + alerting before the floor, not compaction. Reuse manifest/SHA/schema-version/external journal/read-back/restore/operator-auth; do not reuse the object model. Archive as a **SQLite snapshot via `VACUUM INTO`** after writers stop, never `cp`.

**P11 confirmed** with a 10-point minimum; a full 8TB restore is not required per cycle, but **one real restore from the actual drive** is. If the drive is unavailable or fails, **P11 = BLOCKED**, not waived.

### ⚠ Doom Guy — a substrate finding that outranks the archival plan

**Q1 — `0.0.0.0:8017` is clean, but he retracts the evidence.** All three 8017 listeners are host-scoped (`127.0.0.1` → SearXNG container; tailscaled Serve on the tailnet IP; same on IPv6). The exchange pipe is now `127.0.0.1:8019`. **But:** the tailscaled journal for the last 14 days contains **no record** of the remote bind attempt he reported last round. He reported it as established fact and cannot reproduce it. Marked **UNVERIFIED**. And the absence is itself a finding — **we have no log-retention discipline** (new **P14**). *"Forensics that evaporate are not forensics."*

**⚠ CHANGE 6 — THE BASELINE IS FALSE AT THE SUBSTRATE LEVEL.**

> **"Policy excision is not host excision. A grant removes a path. It does not close a socket. Any claim of the form 'X is excised' is false until `ss -ltn` shows the listener gone."**

Live wildcard listeners on Node 0 right now:

| Bind | Service |
|---|---|
| `0.0.0.0:2049` + `[::]:2049` | **NFS nfsd** |
| `0.0.0.0:20048` | **NFS mountd** |
| `0.0.0.0:32803` | **NFS lockd (NLM)** |
| `0.0.0.0:662` | **rquotad (statd)** |
| `0.0.0.0:111` | **rpcbind** |
| `0.0.0.0:6379` | **omega-redis** (Podman) |

The grants conversion did exactly what it claims — and that is the problem. It removed access *through the tailnet*. **NFS is unreachable from the tailnet and fully reachable from the LAN**, where `192.168.10.x` peers can mount it today with no tailnet policy in the path. Redis was flagged as exposed in his August audit and **is still on `0.0.0.0:6379`**. `ShieldsUp: false` and Tailscale SSH enabled.

New **P11b**: host-level excision, or an explicit written decision to accept and name the risk. New **P11c**: correct "excised" language in every doc.

**Q2 — he ran the test from the server side, which is strictly better:** *"an N1 self-report can be wrong or stale in a way the server log cannot."* Result: **N1 has never pulled from 8019.** The access log contains one request total, from loopback. But that negative result **does not distinguish two hypotheses** — missing grant, or N1 never tried. He supplies a three-branch two-sided test, and the third branch is the important one: **TIMEOUT with neither log line ⇒ stop debugging policy and look at the Serve route.**

**⚠ CHANGE 7 — `link-dest` across filesystems silently breaks.** He corrected his own Phase 4 design: you cannot hardlink across filesystems, so NVMe staging with `--link-dest` pointing at the external falls back to full copies and the delta optimization evaporates. **Two passes:** A (src → NVMe staging, `--partial`, survives an unmount) then B (staging → external, `--link-dest`, same filesystem). **The commit point is the catalog append, not the copy.** Never off the existence of a directory.

**Q4 — he retracts his own "contradiction":** my brief and Carmack were **both correct** — two SearXNG layers. But a security consequence follows: **there is a live Serve route on 8017.** Adding a `tcp:8017` grant would make **SearXNG tailnet-reachable** — an unauthenticated outbound-proxy surface with SSRF and abuse-as-a-proxy characteristics. Ruling: **do not add the grant, and bring the Serve route down** (new **P13**). Conversely **8018 has no Serve route at all**, so N1 cannot currently reach SearXNG MCP (new **P15**).

**P11 — three gates with exact thresholds.** **A:** serial/model against the physical label, `Reallocated_Sector_Ct`/`Pending_Sector_Ct`/`Offline_Uncorrectable` = 0, **`UDMA_CRC_Error_Count` = 0** (non-zero is cable, not platters — never misattribute), Btrfs not exFAT. **B:** `fio --size=800G --rw=write --direct=1 --verify=crc32c` + `btrfs scrub start -Bd`. **C:** real-batch restore — `sha256sum -c` **from the mounted external against the source-generated manifest**, scrub clean, random 50-file sample to a **different filesystem**, `CATALOG.jsonl` line appended. *"Gate C.1 without C.3 does not close P11."*

### Kali — two concessions, one new criterion

**M29 wording: conceded.** *"Reversible" over-promises* — the cold copy is the recovery path; the hot state is gone by design. Corrected text: transitions must be **explicit, auditable, and recoverable**.

**`make check-sahs` must assert, not count:**
1. **Exactly one writer** — no process other than the Hivemind daemon holds a write FD on any packet file.
2. **Projection reconciliation** — 1:1 correspondence in both directions: every packet on any surface (MCP list, local FS, MemPalace events) has a matching envelope with identical `session_id`/`target_entity`/`status`/`created_at_utc`, and every envelope is reachable via at least one projection.
3. **No rogue writes.**

This kills GE-N1's 11 dead packets (they are orphans, not handoffs) and the MemPalace ghosts (`peers: []`). A count-only gate passes both; reconciliation fails them.

**90-day threshold: one constant, with a build-time equality check.** `config/handoff_policy.yaml` holds `stale_threshold_days: 90` and `hot_storage_max_days: 90`; `make check-policy-constants` fails the build if they diverge. *"Coincidence is a bug waiting to drift."*

**⚠ CHANGE 8 — his DS-acceptance framing does NOT survive post-merge.** If the Architect insists on post-merge, he withdraws the claim and asks that the PR description carry the risk explicitly: *"N0 install runs post-merge; any UX friction found here is a DS bug that escaped the gate."* He prefers pre-merge on the DS branch.

**P13 added to the bar: negative test for every gate.** The bar is 13 criteria, not 12, and it is not too strict — it is the minimum for a system that has already shipped three silent-defect classes.

---

## §9 — Escalations requiring the Architect

| # | Escalation | Why it cannot be decided by the team |
|---|---|---|
| **E1** | **NFS, rpcbind, mountd, lockd, statd and Redis are wildcard-bound on the LAN while the baseline says "excised."** P11b/P11c. | Either we stop the services or the Architect accepts and names the LAN exposure in writing. Team cannot make that risk call. |
| **E2** | **The external archive has no second copy in different custody.** Carmack: until one exists it is not an archive. | Requires a custody decision and possibly a purchase. Blocked until answered. |
| **E3** | **The 8017 Serve route is live and SearXNG is an unauthenticated proxy surface.** P13. | Bring the route down now, or accept it. |
| **E4** | **N0 install: pre-merge DS gate, or post-merge P0?** Kali withdraws the acceptance-test framing if post-merge. | Sequencing is the Architect's call, and it changes what the PR claims to have validated. |
| **E5** | **Branch topology: push `release/debut-v1.6.0` (Ma'at's ruling) with a 5th commit outstanding.** | I will not push without authorization. |
| **E6** | **Should N1 be able to reach SearXNG MCP (8018)?** No Serve route exists; the plan is silent. | Functional intent, not implementation. |

## §10 — Round 2 changes, consolidated

| Change | From | Substance |
|---|---|---|
| **1** | Carmack | Envelope goes to `envelopes/` at birth and never moves. Four directories. `read_by` permanently available offline. |
| **2** | Carmack | Q1 "restore test is enough" is withdrawn. Second copy in different custody required before the word "archive" is used. |
| **3** | Ma'at | `hivemind_post.py` cannot send `session_id` (fails open); `gnosis_timeline.py` launders provenance. Both Phase-2 blockers. |
| **4** | Ma'at | Topology correction: trees are **not** byte-identical (103 files). Push the branch, not cherry-pick. 5th commit outstanding. |
| **5** | Roc | Legacy 1,214 files → `cold/legacy-*`, never `retired/`. |
| **6** | Doom Guy | **"Policy excision is not host excision."** NFS + Redis + rpcbind wildcard-bound; baseline language is false. |
| **7** | Doom Guy | `link-dest` breaks across filesystems. Two-pass transfer. Commit point is the catalog append. |
| **8** | Kali | DS-acceptance framing withdrawn if N0 install is post-merge. |
| — | Ma'at | Cursor is a **cache, not a record**; `read_by` is truth. Epoch replaces the boolean. |
| — | Ma'at | 4 session-id counters; flip at ≥0.99 stable 14d, malformed 0, **≥2 caller classes**. |
| — | Ma'at | `unverified_sender` goes on the **envelope**, not only in metrics. |
| — | Ma'at | §2.5 instrumentation lands in **Phase 0**, capturing producer identity. |
| — | Ma'at | §2.2 needs a tripwire: "concurrent read-modify-write of a single envelope is now required." |
| — | Carmack | Verification must **not** share a trigger with the write. Writer may skip; verifier must fail. |
| — | Carmack | P11 strengthened: full age distribution, different filesystem, verify-log in git. |
| — | Roc | Manifest canonical, catalog derived. Deterministic batch ids. Orphans quarantined, never deleted. |
| — | Roc | **Conceded:** one finding, two endpoint views — not two independent discoveries. |
| — | Kali | M29: "reversible" → "auditable and recoverable". One policy constant with a build-time check. |
| — | Kali | `check-sahs` asserts one-writer + reconciliation + no-rogue-writes. **P13: negative test for every gate.** |
| — | Doom Guy | 8019 grant still open; three-branch test provided. **P14** log retention. **P15** 8018 intent. |

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ DIALECTIC-ROUND-2-RECORDED ⬡ SIX-PLAN-CHANGES ⬡ SIX-ESCALATIONS ⬡ NODE-0-BASTION*
<!-- PROVENANCE-CORRECTED 2026-09-29T04:11:01Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode/space-bunny-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

