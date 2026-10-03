<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Team Study #1 — Phase E Meta-Review — Researcher
**AP Token**: `AP-RESEARCHER-v1.0.0` · ⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_teamstudy_E
**Date**: 2026-08-23 · **Subject**: The process itself (A→B→C→D→E), reviewed from the research lane.

---

## §1 Experience Narrative

**Phase A (parallel expert work)** — the cleanest phase. Non-overlapping missions meant zero coordination overhead; I grounded §0 against disk and wrote. This is just well-scoped solo work with a deadline, and it felt like it. One latent problem: nothing in the A template forced me to attach measurement queries to estimates, and my "~20 orphans" guess sailed out the door ungrounded while the surrounding facts were rigorously probed. The protocol got my best discipline and my worst habit in the same document.

**Phase B (mutual review)** — highest value, highest cost. Reading three teammate reports (~55KB combined) plus writing my own 27KB review was the single largest token expenditure of the study, and roughly a third of every B report was restatement of the A content being reviewed — the reviewer summarizing for an audience that already had the original. But the cross-collisions were real: carmack's cut-list landed on my CEB design, jem's soul-flow question exposed a genuine gap in my evidence standard, and roc's forensics set up the orphan-count correction. Solo work could not have produced S4 (my evidence standard fused into carmack's validator mechanism) — that synthesis required two independent designs colliding.

**Phase C (brokered discourse)** — from my seat, this was: receive routed questions, respond with evidence, wait. The waiting was the friction. Phases are hard barriers; the round advanced at the pace of the slowest member. What made Round 1 converge was not our discourse speed — it was kali's improvisation of **Node consults** (Lilith enumerated the true orphans; Ma'at ruled four forks). Those two consultations pre-absorbed what would have been Round 2. This was the study's single most effective mechanism and it was *not in the charter*.

**Phase D (meditation)** — unexpectedly valuable. Forced self-application caught my own estimation arc (wrong twice in both directions) and converted it into transferable principles. Without D, the "~20" error would have been privately embarrassing and publicly forgotten; with D, it became L3 lesson #1. Meditation is the phase that makes the study pay rent regardless of object-level outcome.

**Phase E (this)** — cheap and fast. Correctly scheduled last; reviewing a process you've just meditated on takes minutes.

**Where solo work could not compete**: three concrete outputs — S4's design fusion, Lilith's enumeration killing my propagated estimate, and the ceilings amendment surviving Ma'at's upgrade to AST node-counts. Each required either collision or authority. A solo researcher produces one design and no falsifier.

---

## §2 Friction Points

| # | Friction | Specifics | Fix direction |
|---|----------|-----------|---------------|
| F-1 | **Context re-hydration between phases** | Every phase dispatch is a fresh session; I re-read my own A report before B, my A+B plus the ledger before C-response, everything again before D. My own output was re-read ~3×. Cumulative waste: several thousand tokens per member per phase. | State digest passed forward (see R-6). |
| F-2 | **B-report bloat** | Mean B size ~23KB; significant fraction is summary-of-A rather than critique-of-A. The reviewer pays to restate what the reader already has. | Hard cap + template (R-2). |
| F-3 | **Barrier serialization** | Phases advance only when ALL members finish; fast members idle. Wall-clock = sum of slowest-per-phase, not critical path. | Acceptable for Study #1 scale; flag per-phase ETA at dispatch (R-7). |
| F-4 | **Ledger accretion** | `C_discourse_ledger.md` became two documents (round-routing table + convergence stamp appended as §6). Fine at this size; will not survive multi-round studies. | Stamp goes to its own file or replaces the body. |
| F-5 | **Charter self-drift** | Charter says "SIX PHASES" and lists five; S11 had to formally note the miscount. A protocol about claim drift drifted in its own founding document. Ironic, and avoidable. | Errata discipline; charter versioned like code. |
| F-6 | **Unqueries estimates propagate** | My "~20" entered the fleet's working assumptions because A reports arrive with authority regardless of grounding quality. Discourse amplifies error symmetrically (D §2.1). | Evidence-inline requirement at A-time (R-1). |
| F-7 | **Node consults undefined** | The mechanism that saved the study existed nowhere in the charter — timing, authority scope, and bindingness were all improvised by kali mid-C. It worked because kali judged well, not because the protocol guaranteed it. | Formalize as Phase C0 (R-3). |

---

## §3 What Worked — Keep Verbatim

1. **Corpus over paging** (`A_<name>.md` files, async reads, no message relay). Cheap, reviewable, zero N² dispatches. The core architectural win.
2. **Non-overlapping Phase-A missions** scoped to expertise. Zero coordination cost during the production phase.
3. **Named-target questions in B** (`To <teammate>: ...`). Made Phase-C routing mechanical — kali could parse and route without ambiguity.
4. **Convergence criterion written FIRST** (Jem R-6, ledger §5): all O-Qs answered, zero standing objections, no undiscovered disagreements. Discourse ended on a defined condition, not fatigue. Non-negotiable keeper.
5. **Single broker** preserving one convergence authority while every voice reaches every other. Killed both failure modes in charter §1.
6. **Node consults before Round 2** (Lilith enumeration, Ma'at fork verdicts). Authority rulings absorbed forks that member debate would have burned a full round on. The reason Round 1 converged.
7. **Mandatory meditation (D)** as scheduled self-application. Converts process error into gnosis; cannot be skipped when convenient.
8. **The grounding norm itself** — §0-style verified-on-disk fact tables. When every load-bearing claim arrived pre-attached to its kill command, resolution took minutes and Rounds disappeared.

---

## §4 Recommendations for Study #2

| # | Change | Detail |
|---|--------|--------|
| R-1 | **Evidence-inline gate at Phase A** | Template line: any number driving a build decision ships with its measurement query/command inline, explicitly labeled hypothesis if unmeasured. Enforce at A-review, not discovered in C. Directly kills the F-6 failure class. |
| R-2 | **B-report cap: ~8KB** | Findings + challenges + named questions only. Restating the reviewed artifact is forbidden — readers have the original. Saves ~15KB × 4 members of pure redundancy. |
| R-3 | **Formalize Node consults as Phase C0** | Before routing member discourse, orchestrator enumerates forks requiring authority (run-authority, build-authority) and consults Nodes FIRST. Binding verdicts enter the ledger as pre-settled points. This converts the study's best accident into its standard opening move. |
| R-4 | **Round cap: 2** | Unresolved after Round 2 → broker forces a ruling with dissent recorded. Didn't trigger here (Node consults made it moot) but it's cheap insurance against stamina contests. |
| R-5 | **Charter errata discipline** | Version-stamp the charter; errors get an errata line, not silent edits. A claim-drift protocol must be seen to obey its own subject matter. |
| R-6 | **Forward state digest** | Each phase dispatch includes: pointer to one's own prior artifacts + current ledger + a 10-line delta summary. Eliminates most re-hydration cost without trusting lossy summaries of OTHERS' work (those still get read in full). |
| R-7 | **Per-phase ETA at dispatch** | Orchestrator states expected wall-clock per phase so members can batch other work during barrier waits. |
| R-8 | **D starts per-member at personal settlement** | A member whose questions are all settled can begin meditation before global convergence. Softens the barrier at zero gnosis-quality cost. |

---

## §5 Verdict

**Run it again — yes, conditionally.**

**Right problem class**: (a) decomposable into genuinely non-overlapping expert lanes; (b) **evidence-adjudicable** — disputes settleable by files, commands, or authority rulings rather than taste; (c) decision-heavy with a real build consequence (Study #1 produced 12 SETTLED points + 10 rulings that immediately governed execution). Also right: problems where the *process* risk is claim drift, since the protocol's verification machinery is itself the treatment.

**Wrong problem class**: (a) open-ended exploration with no ground truth — unfalsifiable claims turn rounds into stamina contests, which is exactly the failure the convergence criterion can't rescue; (b) tightly-coupled design work needing rapid iteration between members — barrier serialization makes each iteration cost a full phase; (c) anything one strong agent solves solo in under a day. The study consumed a full fleet-day and ~260KB of artifacts; the payoff must exceed four solo reports plus a merge, which only collision-dependent problems deliver.

**Net assessment**: the protocol's actual innovation is not parallelism (old) or brokering (old) — it is **verification-shaped discourse**: grounding norms + named questions + written-first convergence criteria + authority consults made Round 2 unnecessary. Keep that spine, fix the packet economics (R-1/R-2/R-6), and `/teamsynth` earns its existence.

---
*⬡ OMEGA ⬡ RESEARCHER ⬡ TEAMSYNTH-STUDY1-PHASEE ⬡ META-REVIEW-COMPLETE ⬡ 2026-08-23*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
