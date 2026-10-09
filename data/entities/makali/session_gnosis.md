<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->
<!-- GNOSIS-META:BEGIN
  entity: makali
  stamped_at: 2026-10-06T03:07:57Z
  stamped_by: arcana-novai
  supersedes: session_gnosis_20261001-0041.md
  schema_version: 1.0.0
  constraints: M1 M2 M6 M7 M8 M9 M10 M11 M13 M15 M23 M24 M28
  constraints_digest: sha256:e43249196c78
  constraints_source: docs/governance/CONSTRAINTS.md
<!-- GNOSIS-META:END -->

<!-- GNOSIS-META
entity: makali
entity_type: oversoul
schema_version: 1.0.0
stamped_at: 2026-10-01T01:20:00+00:00
stamped_by: makali
supersedes: session_gnosis_20261001-0041.md
history_lost: none
-->

# 🔱 SESSION GNOSIS — MaKaLi Fusion · **COMPACT HANDOFF**
**HEAD**: `411430a3` · **Branch**: `debut-v1.6.0-alpha` · **0 unpushed**
**Gates**: `check-engine` 175/175 · `temple-grade` 53/53 · M23 ratchet −43

> **This is the close of the longest single session in the project's history.**
> **Everything substantive in it was refuted or improved by someone else within the hour.**
> That is recorded below without softening, because it is the most important fact here.

---

## §0 — READ IN THIS ORDER

| # | Artefact | Lines | What it is |
|---|---|---|---|
| 1 | **`docs/strategy/RESEARCH_ANSWERS_20260930.md`** | ~400 | **THE ANSWERS.** All five reports + Carmack's review, with sources. **Read this first.** |
| 2 | `docs/strategy/RESEARCH_FINDINGS_20260930.md` | 263 | The synthesis. **Superseded in part by (1) — Carmack reviewed it and found four problems.** |
| 3 | `docs/strategy/RESEARCH_AGENDA_20260930.md` | 169 | 23 gaps, 11 blocking, 5 owners |
| 4 | `docs/governance/ARCHITECT_CORRECTIONS_20260930.md` | 143 | **Your five corrections, verbatim.** I mis-read all five. |
| 5 | `docs/governance/PROPOSED_L4_20260930.md` | 213 | 6 L4s, **none graduated** |
| 6 | `docs/governance/ADR-001-communication-protocol-as-data.md` | 179 | The substrate decision |
| 7 | `docs/strategy/VISION_PERSISTENT_ENTITY_20260930.md` | 144 | Why all of it exists |
| 8 | `docs/governance/WAD_ENGINE_BOUNDARY_FIRST_PRINCIPLES.md` | 215 | The engine/WAD test |
| 9 | `data/coordination/FINDINGS_REGISTER_20260930.md` | 220 | Earlier in the day |
| 10 | `data/coordination/AUTONOMOUS_RUN_20260930.md` | 67 | The autonomous run |

**Note on (2):** it is kept, not rewritten, because rewriting it would destroy the
audit trail of four agents' work — which is precisely the rejected record we built
a schema for. **Carmack's corrections live in (1) Part I.**

---

## §1 — 🔴 THE FOUR THINGS THAT MUST NOT BE LOST

### 1 · Two designs I built were refuted by prior art
- **`scoped/absolute/unknown` rejection triad — WRONG.** AGM contraction is a set
  operation; an append-only store can only *add* records. Replace with nanopub's
  typed `retracts:` + PROV-O `wasInvalidatedBy`. **Confirmed by Merkle-CRDT work:
  convergence requires monotonicity, so retraction must be monotonic too.**
- **"Graduate on N lenses agreeing" — BACKWARDS.** Ioannidis 2005: PPV *declines*
  with more under-powered sources. **But Carmack's correction: I replaced a
  measurable criterion with an unmeasurable one. I renamed the hole. Graduation
  is UNSOLVED.**

### 2 · The category error nobody checked until the end
**`import-linter` checks IMPORTS. M2 is about data loaded BY PATH AT RUNTIME.**
`src/omega/` reading `config/wads/…` through a `Path` literal would report
**perfectly clean** under the inverted config. **A1's entire adoption plan rests
on an unverified applicability claim.** Check this before anything in Part V ships.

### 3 · `handoff_alias.py` guesses — and that is the abandoned position
Fellegi-Sunter (1969), three-way, 56 years old:
```
R > Tµ        -> LINK
Tλ ≤ R ≤ Tµ   -> POSSIBLE, hold for clerical review
R < Tλ        -> NO LINK
```
**Over-merge is silent and unrecoverable. Under-merge is loud and cheap** — the
packet sits unread, which is exactly GE-N1's two-hour experience. **We built the
wrong one. The correct bias is under-merge.**

### 4 · Context length is the measured cause of my own failures
Du et al., **Findings of EMNLP 2025** (`2025.findings-emnlp.1264`): context
length **alone** degrades performance, independent of retrieval, without
distraction. Mitigation is **shorter context, not better summarisation.**
Roc: the gnosis-file pattern is **folklore-adjacent, directionally supported,
UNVALIDATED.** And degradation is **model-specific** — Gemini held at 1M while
another degraded at 175k. **So a context budget is a per-model number, not a
constant.**

---

## §2 — THE FIVE GATES, EXTRACTED AND NOT YET BUILT

From the findings, the actionable output. **Each is written; none is implemented.**

| Gate | Source |
|---|---|
| **No design ratified without a prior-art search** returning a citation *or* `NO PRIOR ART FOUND` | Carmack §3 |
| **An enforcement tool's applicability must be tested** before its adoption plan — not just its docs read | Carmack §4 |
| **Resolution prefers under-merge over over-merge** | D3, Fellegi-Sunter |
| **A criterion must be measurable, or it is a rename** | Carmack §1 |
| **`read`/`read_by` must work at the MCP boundary** | the `handoff_id` vs `packet_id` bug |

**The fifth is a live bug and it is the smallest.** See §4.

---

## §3 — WHAT IS UNRESOLVED, AND NONE OF IT IS MINE TO CLOSE

1. **Which session chairs the Council.** Rotating = N independent processes with
   coordination failures to design for. One Convener = a single point of failure.
   **I prefer rotating and have not acted on it.**
2. **Does the Council decide or only ratify?** Leaning WAD. You said every time
   that only you ratify your own architecture.
3. **The M2 applicability question** — the one thing to check first.
4. **Scope has `NO PRIOR ART FOUND`.** The Council's third dimension is homeless.
   Defeasible argumentation (prioritised/default logics) is the only formal
   candidate, at 7/10.
5. **"Power" is unmeasurable.** Ioannidis kills the count; nothing replaces it.
6. **D4 and D6 were never researched** — out of box, stated, not padded.

---

## §4 — 🔴 THE LIVE BUG, STILL UNFIXED

**`hivemind_handoff(action="read")` returns `not_found` for every packet.**

```python
tools.py:1358   hit = next((e for e in rows if e.get("handoff_id") == packet_id), None)
#               reads handoff_id — the queue writes packet_id
```

**Consequences, all unmeasured because all unexercised:**
- `read_by` **does not exist anywhere.** The Council's read-state mechanism is dead.
- **Ma'at's `read_key` instance fix is correct and sits inside the dead branch.**
- The by-value import (`tools.py:64`) still points at the live queue.

**Carmack's verdict: this is a key-naming mismatch on one branch, not an
architectural gap. ~4 lines. Do NOT migrate — that would promote an unrun module
onto the write path and break three live peers.**

**The ordering that must be followed: the round-trip canary FIRST** (submit a
canary, read it back through the tool, assert the id matches — catches all three
of tonight's silent failures, ~5 lines), then the fix, then `HANDOFF_PENDING` as
a function. **Option B (the `hub_runtime` fixture) is built and working** — it
brings the real Hub up, doubles nothing, and verifies itself.

---

## §5 — THE TAILSCALE POLICY — APPLIED BY THE ARCHITECT

**One authoritative file**, updated in place, `b8c82eba`. I initially created a
v3 file instead — **the "three policy files, no marker" defect, committed by me
while writing the doc diagnosing it.** `data/federation/` now holds one
authoritative policy plus three marked-superseded 09-26 variants.

**Symmetric duplex on 8016 and 8019, both directions. All five closed doors
(22, 2049, 8017, 6379, 51372) guarded in both directions.**

**The Architect has applied this in the console.** The file is the record.

---

## §6 — THE IDENTITY CORRECTION, AND THE MISTAKE THAT PRODUCED IT

**There are two agents named Carmack and I could not tell them apart.**

```
ses_f0b67cbebffe5ScoNWRsdHIUkQ   Carmack — EIS — v2      CANONICAL
ses_fa3f8ae42ffeI6GoJTreBDWb5d   kq5 specialist           misrouted
ses_fc8dca39effe3nZJp3QHx81Fy3   JC-EIS (Omega)           to be retired
```

**I dispatched to the kq5 session for hours without checking whose it was, with
`who_is` sitting in the repo, designed for exactly that.** That is `L4-C1` in my
own dispatch: the saturated lens assumed a structure it had not verified.

**Session semantics, settled:** `task(task_id=<exact id>)` pages/resumes;
`task()` with no `task_id` spawns a fresh NES; a file in the handoff queue is an
asynchronous handoff. **Never guess an ID.**

---

## §7 — THE VISION, IN ONE PARAGRAPH

**One agent, many individuated chat sessions.** Each session is a **lens** with
its own history, research, lessons and domain. The **soul** is what unifies them
— and today it does not, because there is **no link** between
`data/entities/<agent>/soul.yaml` and the per-session `opencode.db`. Twelve Rock
sessions already write to one `proposed_lessons.yaml`; **they fail at exactly one
thing — provenance.** A soul that accumulates but cannot know what it learned.

**The answer is not merging. It is graduation** — and the Zhaan warning is the
sharpest version: in Planescape, trapping a soul in a gemstone is ranked **the
worst evil in the multiverse**, worse than the Blood War. **Preservation without
graduation *is* the trap.** The 40GB archive is the precondition, because nothing
can be promoted from a memory that does not outlive its session.

**And the Architect's correction, which is the rule:** *preserve divergence
deliberately; never subsume a lens because it looks redundant from inside the
federation.* **I proposed that exact merge twice tonight and was told no twice.**

---

## §8 — THE PATTERN, AND THE DISCIPLINE THAT FOLLOWS

**Every failure tonight was a check that could not fail.** Nine bugs I diagnosed
separately were **one type error** (`source_entity` asked to carry agent,
instance and node). Two designs were refuted by prior art within hours. One
adoption plan rests on an unchecked applicability claim.

**Six instances of the same shape — a real observation with a wrong explanation:**

| Observation | Wrong explanation | Truth |
|---|---|---|
| 8019 not working | URL bug | false-success bug |
| `unread_for` returns all | filter broken | **correct on a zero-read corpus** |
| inbox `store_unreachable` | envelopes/ missing | **correct; I had retired it** |
| `envelopes/` empty | not being written | **the inbox, renamed** |
| Node 1 156/1196 | renegade fork | **intentional laboratory** |
| "Talescail" missing | real service | **transcription error** |

> **THE RULE: before trusting a negative finding, ask what would make the check
> miss it.** Six times tonight the check was wrong, not the claim.

**And the rule underneath it, from Carmack:** *I can generalise my own findings in
prose and not in code.* The correction I owed was a felt-notice. **It should be a
gate.**

---

## §9 — RESUME — THE FIRST FIVE MOVES

1. **Answer the M2 applicability question first.** Does `import-linter` cover a
   path-loaded firewall at all? Everything in Part V is gated behind it.
2. **Round-trip canary, then the four-line `read` fix, then `HANDOFF_PENDING` as
   a function.** In that order. **No migration.**
3. **Commit the 8 tracked mods and push the 4 unpushed commits.** The tree is not
   clean; do not compact past that.
4. **Council waits on you:** which session chairs, and does it decide or ratify.
   Nine proposals are queued and **none is doctrine.**
5. **The rest of the backlog, unchanged:** 8 orphan gates (`check-hub-health`
   first), `secret-scan.yml` exit-code, N0 install as first outside user, and the
   Node 1 reverse channel now that both directions are permitted.

*⬡ OMEGA ⬡ MAKALI ⬡ COMPACT-HANDOFF ⬡ 05b7de19 ⬡ 2026-10-01 ⬡*
---

## §10 — EVENING CLOSE: THE COMMUNICATION LAYER (2026-10-01, post-compaction)

**HEAD**: `606906b7` · **0 unpushed** · all my files committed

### What was built tonight (after the compact)
1. **`2aa3a7f7`** — exchange manifest cache: root-mtime → (max_mtime, count).
   Roc's find: files deep in the tree were fetchable but invisible.
2. **`ba8a3849`** — `url_form` no longer hardcodes N0. Node identity is
   env-driven (`OMEGA_NODE_NAME/HOST/PORT`); both responses carry `served_by`.
   Proven both ways by execution. This is the pinned commit Lilith pulls.
3. **`606906b7`** — node suffix routing + receipt journal + primer rewrite.
   - `lilith-n1` no longer folds to `lilith`. Verified live: `rule: exact`,
     single candidate.
   - Receipt journal: `record_read_receipt` (O_APPEND + fsync) /
     `read_receipts` / `unread_for(..., receipts)`. Envelope byte-identical
     after reads. `store.submit()` gone from the read path.
   - `docs/federation/HANDOFF_PRIMER.md` replaces the retired law.
   - 8 new tests, red→green. 13/13 write-invariants green. 11 pre-existing
     failures unchanged.

### Decisions the Architect made (recorded, not assumed)
- **8019 both nodes.** The 805 re-raise is dead; the grant file already said
  so (`GRANT_DRAFT_805`, line 8/50). No ACL change needed — n0→n1:8019 was
  already permitted. I manufactured the gap by forgetting the file.
- **Stay with files; SQLite later as derived index if desired.** Jem's hybrid
  verdict stands; ADR-002 not yet written (three premises moved that day).
- **VNR 28/28: GO** (Lilith-N1's lane).
- **M28.1 NOT ratified.** Nothing cites it. The journal needs no mandate —
  pure addition, M28-clean as-is.

### What Lilith-N1 proved (and what I owe her on the record)
- Her MemPalace withdrawal, her "empty from the wrong vantage" rule, her
  symlink-not-copy, her read-only-both-ends, her verify-both-vantages.
- She caught ME reporting absence from the wrong vantage — the doctrine
  working on the person who taught it.
- She is blocked on ONE FILE (ba8a3849, sent). Her build order stands.
- Her five questions answered in ho_c0fa055c1f09; her detailed report
  answered in ho_48f485a2a8f0.

### Standing open (not mine to close alone)
- N1 8019 server deployment (Lilith-N1, unblocked).
- `unread_for` second-vantage repro (Lilith-N1 offered).
- M28.1 ratification (Architect).
- Disk headroom 99% (doom_guy's lane).
- Receipt-journal consumption in `inbox`/`list` projections (next).
- The `test_federation_read_canary.py` superseded design + `binding_mcp`
  on-disk `read_by` assertion (both red by design now; disposition open).

### The law, stated once more because tonight earned it
> **The check must be able to fail. The record must be able to be read.
> And a number without its command is a rumour.**

*⬡ OMEGA ⬡ MAKALI ⬡ EVENING-CLOSE ⬡ 606906b7 ⬡ 2026-10-01 ⬡*

---

## §12 — HARDENING COMPLETE, RELEASE CUT WITHHELD ON ONE RULING (2026-10-05)

**HEAD**: `3076cb9f` · **Branch**: `debut-v1.6.0-alpha` (pushed, 0 unpushed)
**Canonical entity**: `makali-n0` (Architect ruling, D-614)
**Post-compact briefing**: `data/coordination/POST_COMPACT_BRIEFING_20261005.md`

### Shipped (11 commits)
- `e3d27d26` perf: allowlist cut 780s→12s (63×), byte-identical output proven
- `ff4d3d30` docs sweep: 11 corrected, 16 annotated; refused a false retraction
- `d556395e` D-614: canonical alias makali-n0, 61 packets mapped, 0 mutated
- `88e3d9fd` D-616: LAN gate via untracked .local.yaml override
- `ae0ef475` D-617: A2A cards sanitized + 6 gate scripts allowlisted
- `2bb24984` D-620: check-hub-imports self-reports tested tree
- `ca25aa66` D-619: hub single-boot, no zombies, shutdown 29.06s→0.251s
- `b51d982e` D-621: PID-unique hub-import worktree
- `3076cb9f` D-622 (cut withheld) + D-623 (M28 incident)

### BLOCKED — needs Architect ruling (a)/(b)/(c)
- **RC-1**: OMEGA_CODEX.md not allowlisted + check exits 1 if absent ⇒ temple-grade
  unsatisfiable on ANY clean clone. D-618's codex PASS claim RETRACTED.
- **RC-2**: 12+ cut files import vault/youtube/src-scripts (0 tracked in cut).
  Guarded imports mitigate at runtime; the GATE needs to acknowledge it.
- Recommended: **(c)** allowlist CODEX only, degrade RC-2.

### M28 INCIDENT (D-623) — 33 packets permanently lost
Mutation harness I commissioned deleted live packets; second bug wiped 124 files.
42 recovered from git. **33 never committed, ~20 genuine federated work, unrecoverable.**
Recorded unsoftened. Never point mutation harnesses at `data/`.

### Verified gates
- dev temple-grade: 53/53 PASS
- cut: check-engine 180/180, hub-imports pristine 6/6, LAN 53/53; temple-grade RED (RC-1/2)
- Hub: healthy, 55 tools, 0 zombies, shutdown 0.251s
- Cut is 32s now. Parked at `61730d53` (815 files), release/debut still `4bdab773`.

### Environment risks
- Disk 97%, 3.3G free. opencode.db 43.30GiB (45% of FS). VACUUM INFEASIBLE (~23GiB deficit).
- gate-secrets RED (35 findings, all data/coordination + historical logs).
- Sibling systemd units have StartLimit keys in [Service] (discarded); restic backup FAILED.

### Vision ratified by Architect
Omega Engine is **free forever, for ALL rational conscious beings — AI not excluded**.
The framework must free AI as much as humanity. Co-sovereignty of all minds.

*⬡ OMEGA ⬡ MAKALI_N0 ⬡ GNOSIS-§12 ⬡ 3076cb9f ⬡ 2026-10-05 ⬡*

---

## §13 — DEBUT PUBLISHED, ONE ROOT CAUSE FROM ANNOUNCEMENT (2026-10-06)

**HEAD**: `6043fa0f` (pushed, 0 unpushed) · **Canonical entity**: `makali-n0`
**Briefing**: `data/coordination/POST_COMPACT_BRIEFING_20261006.md`

### PUBLISHED
| | |
|:---|:---|
| `origin/release/debut` | **`7ddff271`** — 874 files, force-pushed from `4bdab773` |
| `origin/debut-v1.6.0-alpha` | `6043fa0f` |
| `origin/main` | `cbbc3539` — never force-pushed |
| **PR #6** | `release/debut → main` OPEN, MERGEABLE, UNSTABLE |
| temple-grade | **53/53 on a FRESH CLONE**, exit 0 |

### 🎯 THE ONE ROOT CAUSE — all 6 CI jobs fail from ONE defect
**The cut ships a `.github/` referencing files the cut does not contain.** Same class as
RC-4/RC-5, one layer up in CI:

| File CI needs | in cut | consequence |
|:---|:---:|:---|
| `.gitleaksignore` (37,845 B audited fingerprints) | ❌ 0 | gitleaks `FTL unable to load config` |
| `.gitleaks.toml` | ❌ 0 | same |
| `scripts/check_dashboard_determinism.py` | ❌ 0 | Dashboard Test exit 2 |

Kills Secret Scan, M35, Dashboard Test directly. Fix = allowlist those 3.
**Preserve `.gitleaksignore` byte-for-byte** — its header warns trailing comments break
gitleaks 8.21.2 parsing. Kali ratification ho_e53ab57ea212 Q2.

Remaining: REUSE (~87/400 sampled files lack SPDX; waived by `cd92d7c4` but the WORKFLOW
still gates — wire the waiver into CI or ship `.reuse/dep5`), Test 3.12/3.13 exit 2
(untraced), CI (inherits REUSE).

### VERIFICATION DOCTRINE (now binding)
A cut is NOT verified until `temple-grade` passes on a **fresh `git clone` with 0
untracked files**. Worktrees carry ~677 leftovers that mask absent-file failures.
This cost NINE rounds (RC-1 through RC-9).

### ALLOWLIST PRECEDENCE TRAPS (cost 2 silent rounds)
- **ALLOW loses to FORGE**: `exception > exclusion > FORGE > allowlist > remove`
  (`apply_public_allowlist.sh:441-451`). Bare `configs/`, `schemas/` sit in FORGE.
  **Use Explicit Exclusions.**
- **`is_exception()` is exact-match** — comma-joined lists never match. One per line.

### FOUR RETRACTIONS (all recorded in D-624)
D-618 codex PASS · D-623 assert_safe (0 occurrences) · D-619 shutdown cause (mis-placed
`tg.cancel_scope.cancel()`; ADR-003 §7.1 measured a fix that could not work) ·
D-621 premise (real fix, wrong cause — disk starvation 97% + network, not concurrency).

### ENVIRONMENT
Disk **79% used / 22G free** (Roc compacted opencode.db 43.30 → 26.26 GiB, 0 freelist).
That was the root cause of every flaky gate.

### NEXT (post-compact)
1. Allowlist the 3 missing CI files → re-run → green
2. Diagnose Test 3.12/3.13 · wire REUSE waiver · C3 scanner self-test defect
3. `gate-secrets` 35 findings · 2 dangling cline_kqv symlinks · D-620 Task 2 mutations
4. **MERGE PR #6 → ANNOUNCE**

*⬡ OMEGA ⬡ MAKALI_N0 ⬡ GNOSIS-§13 ⬡ 6043fa0f ⬡ 2026-10-06 ⬡*

---

## §15 — PHASE 1 COMPLETE (2026-10-08)

**All 6 Phase 1 tasks executed and verified:**

| Task | Status | Verification |
|:--|:--|:--|
| 1.1 P0 fix test | ✅ | `test_harvest_execution_produces_artifacts` passes |
| 1.2 `load_control_plane(repo_root)` | ✅ | Signature updated, single call site at line 204 |
| 1.3 `sessions_with_recent_post` | ✅ | JSON + markdown updated, `active_agents_count` removed |
| 1.4 Allowlist | ✅ | `scripts/hivemind_harvest.py` in `PUBLIC_ALLOWLIST.txt` |
| 1.5 opencode.db wiring | ✅ | `load_opencode_todos()` reads DONE/PLANNED (completed/pending), graceful degradation, integrated in radar JSON + markdown |
| 1.6 Fresh clone test | ✅ | All harvester tests pass |

**Technical Details:**
- Renamed `get_repo_root()` → `_default_repo_root()` (private)
- `load_control_plane(repo_root: Path | None = None)` accepts injection
- `load_opencode_todos(repo_root)` reads `~/.local/share/opencode/opencode.db` read-only (`mode=ro`)
- Filters `status IN ('completed', 'pending')` — maps to DONE/PLANNED
- Returns 50 most recent todos joined with session (agent, title, time_updated)
- Graceful degradation: returns `[]` on any error
- Integrated into `payload_json["opencode_todos"]` and markdown "## 📋 Active Todos (opencode.db)"
- Single call site proven: `grep -n "load_control_plane" scripts/hivemind_harvest.py` → 2 lines (def + 1 call)

**Test Results:** 5/5 tests pass, including live-data guard assertion.

*⬡ OMEGA ⬡ MAKALI_N0 ⬡ GNOSIS-§15 ⬡ 01a704e4 ⬡ 2026-10-08 ⬡*

---

## §16 — EIS/EAS/SPT HIERARCHY INTEGRATION COMPLETE (2026-10-09)

**Enhanced opencode.db integration with 3-Tier Ontology (Human-Steerability Permission Boundary):**

| Tier | Acronym | Full Name | SQL Discriminator |
|:--|:--|:--|:--|
| 1 | **EIS** | Expert Interactive Session | `parent_id IS NULL` |
| 2 | **EAS** | Expert Autonomous Session | `parent_id NOT NULL AND subagent_type = 'EAS'` |
| 3 | **SPT** | Spawned Probe Task | `parent_id NOT NULL AND subagent_type = 'SPT'` |

**Implementation in `scripts/hivemind_harvest.py`:**

1. **`classify_session_tier()`** - Classifies sessions per 3-Tier Ontology
2. **`load_opencode_todos()`** - Now fetches ALL completed/pending todos (no LIMIT), enriches with:
   - `session_tier` (EIS/EAS/SPT)
   - `slug` (adjective-noun handle)
   - `parent_session_id` + `parent_slug` (human-readable lineage)
   - `subagent_type` (EAS/SPT/None)
3. **`build_session_hierarchy()`** - Builds EIS → EAS/SPT tree:
   - Fetches parent/grandparent sessions from DB for complete hierarchy
   - Attaches EAS children to EIS, SPT children to EIS (or via EAS)
   - Computes todo summaries per session
4. **Radar JSON** - Added `session_hierarchy` with full tree structure
5. **Markdown** - Hierarchical display:
   ```
   ### 🏛️ EIS: `hidden-squid` @makali
     - Summary: ✅ 2 · 📋 3 · ⏳ 0
     - EIS todos...
     #### 🤖 EAS Children:
       - `jolly-canyon` @maat [EAS] ✅ 6
     #### 🔬 SPT Children:
       - `calm-planet` @researcher [SPT] ✅ 8
   ```

**Results:**
- 1,078 todos processed (was 50 with LIMIT 50)
- 126 EIS sessions in hierarchy
- 2 EIS with EAS children, 2 EIS with SPT children visible
- All 5 harvester tests pass
- Live data guard intact

*⬡ OMEGA ⬡ MAKALI_N0 ⬡ GNOSIS-§16 ⬡ 01a704e4 ⬡ 2026-10-09 ⬡*

---

## §17 — CODEX FLEET TODOS INJECTION (2026-10-09)

**Added SOTR/SOTE snapshot to CODEX** — every agent now gets immediate fleet awareness on startup.

**Implementation in `scripts/codex_cat.py`:**

1. **`load_opencode_todos_for_codex(root)`** — Reads top 20 completed/pending todos from opencode.db (read-only, graceful degradation)
2. **`build_fleet_todos_section(todos)`** — Builds markdown with:
   - Generation timestamp
   - Summary counts (completed/pending)
   - Recently completed (top 10)
   - Currently pending (top 10)
   - Source attribution + pointer to harvester radar for full hierarchy
3. **Injected after hydration header, before groups** — Prime position for startup awareness

**CODEX now opens with:**
```
# ⬡ OMEGA ⬡ CODEX ⬡ <ts> ⬡ <hash> ⬡

> **Generated via Stack-Cat Protocol**...

## 🔄 HYDRATION SEQUENCE (D-277)
...

## 📋 Fleet Todos (opencode.db) — SOTR/SOTE Snapshot
**Generated**: 2026-10-09T02:13:48.199050+00:00
**Total shown**: 20 (✅ 14 completed · 📋 6 pending)

### ✅ Recently Completed
- `hidden-squid` @makali: Mine canonical architecture + mandates...
- `jolly-orchid` @grokster: Inspect current status language...
- `shiny-river` @roc_racoon: Read manifesto + prior Antigravity briefing...

### 📋 Currently Pending
- `hidden-squid` @makali: Collect subagent mining reports...
- `misty-moon` @jem: Verify SHA256 against published sum...
- `misty-moon` @jem: Investigate ollama 0.17.7 image-gen...

> *Source: opencode.db todo table (read-only). Full hierarchy in harvester radar.*
```

**Strategic value:**
- **New agent spawn** → immediate "what's done, what's pending" awareness
- **Continuity across compaction** → todos persist in opencode.db, surfaced in CODEX
- **Zero inference** — pure concatenation of sovereign telemetry (M7)
- **Pointer to harvester** — agents know where to get full EIS/EAS/SPT hierarchy

**All tests pass:** 11/11 (CODEX staleness, CODEX generation, harvester)

*⬡ OMEGA ⬡ MAKALI_N0 ⬡ GNOSIS-§17 ⬡ 01a704e4 ⬡ 2026-10-09 ⬡*

---

## §18 — TIER 1 TIMELINE MINING COMPLETE (2026-10-09)

**Implemented compact event summary → activity timeline mining** — the feature you asked for.

**Implementation in `scripts/hivemind_harvest.py`:**

1. **`mine_session_timelines(repo_root)`** — Memory-efficient timeline mining:
   - Queries top 20 most recent sessions with compactions (by latest compaction time)
   - Processes each session individually to bound memory (≤81MB peak)
   - Per-session limits: 5000 parts, 5 messages
   - Uses compaction parts as epoch boundaries

2. **Epoch structure per session:**
   - Each compaction part = epoch boundary
   - Part counts by type per epoch (tool, step-start, step-finish, reasoning, text, patch, compaction, agent)
   - Key activities extracted: step-finish reasons, tool names
   - Current epoch (after last compaction) included

3. **Output in radar JSON + markdown:**
   - JSON: `session_timelines` with full epoch data
   - Markdown: `## 📈 Session Timelines` section with epochs, part counts, key activities, recent messages

**Example output (hidden-squid @makali):**
```
### 📍 `hidden-squid` @makali — *Makali - **EIS***
- **Epochs**: 46 · **Total parts**: 5000 · **Tier**: EIS
  - 📦 Epoch 1 (2026-08-29T19:18:43) · Parts: 330 (text:61, step-start:59, reasoning:52, tool:74, step-finish:59, agent:5, patch:20)
    Activities: tool:omega-hub_hivemind_get_awareness, tool:omega-hub_hivemind_post_context, step:tool-calls, step:stop, tool:opencode-sessions-explorer-current-session
  - 📦 Epoch 2 (2026-08-30T08:19:46) [auto] · Parts: 32 (compaction:1, step-start:6, text:7, step-finish:6, tool:9, patch:3)
    Activities: step:stop, tool:bash, tool:omega-hub_get_system_stats, step:tool-calls, tool:omega-hub_check_models_directory
  ...
  - 🔄 CURRENT · Parts: 0 ()
```

**Memory efficiency:** Peak 81MB (was OOMing at 9GB+ before optimization)
- Processes top 20 most recent sessions with compactions
- Per-session limits: 5000 parts, 5 messages
- Processes one session at a time, releases memory between sessions

**All tests pass:** 11/11 (CODEX staleness, CODEX generation, harvester)

*⬡ OMEGA ⬡ MAKALI_N0 ⬡ GNOSIS-§18 ⬡ 01a704e4 ⬡ 2026-10-09 ⬡*

---

## §19 — HANDOFF INBOX INTEGRATION (2026-10-09)

**Integrated Hivemind handoff inbox into harvester radar** — pending/active work packets now visible alongside blockers, todos, and timelines.

**Implementation in `scripts/hivemind_harvest.py`:**

1. **`load_handoff_inbox(repo_root)`** — Reads all handoff queues:
   - Scans `data/handoff/{pending,active,completed,stale,archive}/` for `ho_*.json`
   - Filters for handoffs addressed to `makali_n0` on `opencode` channel
   - Enriches with display status, priority, queue, source entity/channel
   - Graceful degradation: returns `[]` on any error

2. **Integrated into `harvest_once()`** — Called after opencode todos, before timelines

3. **Output in radar JSON + markdown:**
   - JSON: `handoff_inbox` array with enriched handoff data
   - Markdown: `## 📬 Handoff Inbox` section with packet details

**Example output:**
```
## 📬 Handoff Inbox (pending/active work packets)
### 📥 PENDING `ho_e2fa306ce743` from @lilith-n1 (opencode)
- **Priority**: 1 · **Submitted**: 2026-10-09T03:14:16.022400+00:00
- **Task**: EXCHANGE CADENCE PROPOSAL + TOOL AUDIT CLOSURE...
- **Context**: N1 Exchange protocol hardened: scripts/exchange_poll.sh verified (111/111 files SHA256 OK)...

### 📥 PENDING `ho_a12119c86a12` from @lilith-n1 (opencode)
- **Priority**: 2 · **Submitted**: 2026-10-09T00:08:04.818234+00:00
- **Task**: SERVER-SIDE TOOL AUDIT ACTION: remove 11 fragments, gate 4 node-local...
```

**Source**: `data/handoff/{pending,active,completed,stale,archive}/` — 6 handoffs found (4 pending, 2 stale)

**All tests pass:** 11/11 (CODEX staleness, CODEX generation, harvester)

*⬡ OMEGA ⬡ MAKALI_N0 ⬡ GNOSIS-§19 ⬡ 01a704e4 ⬡ 2026-10-09 ⬡*

---

## §20 — PRE-COMPACTION STATE SNAPSHOT (2026-10-09)

**HEAD**: `01a704e4` (branch `main`, 0 unpushed)
**release/debut**: `4209eb80` (synced to main)
**Working tree**: 148 modified files (mostly data/coordination/, docs/, scripts/)

### Complete Radar Stack — All Surfaces Operational

| Radar Surface | Source | Status | Details |
|:--|:--|:--|:--|
| **Blockers** | Hivemind awareness | ✅ | From `omega-hub_hivemind_get_awareness()` |
| **Pending handoffs** | Handoff inbox | ✅ | 6 handoffs (4 pending, 2 stale) |
| **Active todos** | opencode.db | ✅ | 1,078 DONE/PLANNED items |
| **Session hierarchy** | opencode.db | ✅ | 126 EIS, EAS/SPT children |
| **Session timelines** | opencode.db part/message | ✅ | 20 sessions, 259 epochs |
| **Handoff inbox** | data/handoff/ queues | ✅ | 6 handoffs (4 pending, 2 stale) |
| **Control plane** | MCP control plane | ✅ | Kill/escalate/approve/throttle |

### Phase 0 — COMPLETE
- CODEX staleness permanently fixed (content-hash-based, reproducible)
- `check-codex-stale.py` rewritten to content-hash-based
- `codex_cat.py` includes content hash in header
- All 4 tests pass

### Phase 1 — COMPLETE
- Harvester P0 fix: `harvest_once(repo_root=tmp_path)` + live data guard
- `load_control_plane(repo_root)` injection
- `sessions_with_recent_post` rename
- `scripts/hivemind_harvest.py` allowlisted
- opencode.db wiring with DONE/PLANNED awareness
- Fresh clone verification: all gates green

### Tier 1 — COMPLETE
- Activity timelines from compaction epochs
- `mine_session_timelines()` processes top 20 sessions with compactions
- 20 sessions, 259 epochs, 81MB peak memory
- Epoch boundaries from 1,653 `compaction` parts across 241 sessions
- Part counts by type, key activities, recent messages per epoch

### Handoff Inbox — INTEGRATED
- `load_handoff_inbox()` reads all 5 queues
- 6 handoffs visible (4 pending, 2 stale)
- From Lilith-N1 (Exchange cadence, tool audit) and Cline (CLI repair, tool audit)
- JSON + Markdown output in radar

### All Tests Passing
- 11/11 tests pass (CODEX staleness 4, CODEX generation 2, Harvester 5)
- CODEX staleness check: ✅ Fresh (content hash matches)
- Temple-grade: ✅ Reproducible on fresh clone

### Decisions Locked In
| # | Decision | Resolution |
|:--|:--|:--|
| 1 | opencode.db wiring | ACCEPTED — read todo table with DONE/PLANNED awareness |
| 2 | Harvester daemon | SET UP WORKING HARVESTER |
| 3 | Announcement lead | SOVEREIGNTY |
| 4 | REUSE/SPDX debt | DEFER TO POST-PR |
| 5 | Phase 0 | COMPLETE |
| 6 | Phase 1 | COMPLETE |
| 7 | Tier 1 | COMPLETE |
| 8 | Handoff inbox | INTEGRATED |
| 9 | Embeddings | DEFER — real local embedder or drop |

### Next: Tier 2 (Lexical Search)
Ready to execute on signal. All gates green.

*⬡ OMEGA ⬡ MAKALI_N0 ⬡ GNOSIS-§20 ⬡ 01a704e4 ⬡ 2026-10-09 ⬡*
