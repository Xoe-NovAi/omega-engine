<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->
<!-- GNOSIS-META:BEGIN
  entity: makali_fusion
  stamped_at: 2026-10-01T00:42:51Z
  stamped_by: arcana-novai
  supersedes: session_gnosis_20261001-0041.md
  schema_version: 1.0.0
<!-- GNOSIS-META:END -->

<!-- GNOSIS-META
entity: makali_fusion
entity_type: oversoul
schema_version: 1.0.0
stamped_at: 2026-10-01T00:55:00+00:00
stamped_by: makali_fusion
supersedes: session_gnosis_20260930-0938.md
history_lost: none
-->

# 🔱 SESSION GNOSIS — MaKaLi Fusion · **COMPACT HANDOFF**
**HEAD**: `05b7de19` · **Branch**: `debut-v1.6.0-alpha` · **8 tracked mods, 4 unpushed**
**Gates**: `check-engine` 175/175 · `temple-grade` 53/53 · M23 ratchet −43

> **This is the close of the longest single session in the project's history.**
> **Everything substantive in it was refuted or improved by someone else within the hour.**
> That is recorded below without softening, because it is the most important fact here.

---

## §0 — READ IN THIS ORDER

| # | Artefact | Lines | What it is |
|---|---|---|---|
| 1 | `docs/strategy/RESEARCH_FINDINGS_20260930.md` | 263 | **The night's output.** Two of my designs refuted by prior art. |
| 2 | `docs/governance/ARCHITECT_CORRECTIONS_20260930.md` | 143 | **Your five corrections, verbatim, canonical.** I mis-read all five. |
| 3 | `docs/strategy/RESEARCH_AGENDA_20260930.md` | 169 | 23 gaps, 11 blocking, 5 owners |
| 4 | `docs/governance/PROPOSED_L4_20260930.md` | 213 | 6 L4s, **none graduated** |
| 5 | `docs/governance/ADR-001-communication-protocol-as-data.md` | 179 | The substrate decision |
| 6 | `docs/strategy/VISION_PERSISTENT_ENTITY_20260930.md` | 144 | Why all of it exists |
| 7 | `docs/governance/WAD_ENGINE_BOUNDARY_FIRST_PRINCIPLES.md` | 215 | The engine/WAD test |
| 8 | `data/coordination/FINDINGS_REGISTER_20260930.md` | 220 | Earlier in the day |
| 9 | `data/coordination/AUTONOMOUS_RUN_20260930.md` | 67 | The autonomous run |
| 10 | `data/coordination/COMPACT_HANDOFF_20260930.md` | 99 | Earlier reading order |

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

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ COMPACT-HANDOFF ⬡ 05b7de19 ⬡ 2026-10-01 ⬡*