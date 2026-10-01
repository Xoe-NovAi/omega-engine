<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 TEAM-SYNTHESIS STUDY #1 — PHASE E — JEM META-REVIEW
**AP Token**: `AP-JEM-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ x-preview-f-free ⬡ opencode ⬡ trc_team_synthesis_e ⬡ ACTIVE

**Date**: 2026-08-23
**Inputs**: Full arc re-read — `A_jem.md` (31-gap review), `B_jem.md` (adjudication + CUT-1/F2/F-C), `C_discourse_ledger.md` incl. §6 convergence stamp, `D_jem_meditation.md`, peer E-reports where available.
**Seat**: Compliance/QA adjudicator — the participant whose job was making disputes decidable, and whose own output was twice the object under dispute.

---

## §1 EXPERIENCE NARRATIVE — the quality/compliance seat

### Did brokered discourse serve adjudication? Yes — for three structural reasons.

**One: the broker held the ledger, so settlements were diffable.** My core adjudication method this study was not argument — it was *diffing*. When I verified "zero standing objections" across S1–S12, I did not consult my memory of the discussion; I checked S3's text against my three CUT-1 conditions **verbatim**. That was only possible because kali maintained ONE settlement table with status columns instead of letting agreement scatter across four conversation threads. A paraphrased ledger would have made my verification theater. The ledger made it forensics.

**Two: routing preserved attribution, which is what made concessions safe.** Every challenge arrived signed ("Carmack F-B → Jem"). This matters more than it looks: a concession extracted anonymously feels like defeat; a concession made *to a named colleague who cited your own data* feels like analysis. CUT-1 was psychologically possible because carmack's challenge pointed at MY gap table — the instrument, not me. Attribution converts concession-from-pressure into concession-from-evidence.

**Three: the broker did not editorialize member positions.** Kali routed questions verbatim and ruled only on items members flagged. The one time the orchestrator's summary could have distorted my position (O-Q2's downgrade), the ledger recorded my conditions in full, so the stamp couldn't silently soften them. **Broker-as-relay-with-ledger is the correct shape; broker-as-editor would have poisoned adjudication.**

The proof is the outcome shape: Round-1 convergence with zero standing objections was not consensus-by-politeness — it was twelve disputes that all became *decidable* before anyone got tired. That is exactly what the compliance seat exists to produce, and the structure produced it without me having to fight for anything except the criterion (see F-1 below).

### Was public self-correction (F2) processed well? Better than the structure deserved.

Honest answer: the structure had **no slot** for what I did. Owning my unmerged 25-entry delivery (`GAP_REGISTRY_UPDATES_20260822.json`) mid-adjudication of teammates' hygiene was an improvisation — I wedged it into `B_jem.md` between rulings because there was no SELF-GAPS section, no disclosure convention, no protocol text telling me whether self-incrimination was participation or disqualification.

And yet the absorption was near-perfect:

1. **It became data, not derailment.** Nobody paused the discourse to litigate my credibility. Carmack and researcher folded it forward as a C1-class sighting (claim-without-artifact) that *confirmed the study's central finding*. The disease was caught exhibiting itself in the auditor — which is the strongest evidence a disease exists.
2. **It strengthened rather than cost authority.** No teammate challenged my subsequent rulings via my own gap. The L3 lesson (review authority is earned by self-application) held empirically: the disclosure pre-empted the attack rather than inviting it.
3. **It fed the mechanism.** Merging my F2 delivery became the first task registered under the new evidence-binding rule — the correction was itself subject to the standard, closing its own loop.

But mark the fragility: **this worked because of how I framed it, not because the protocol guaranteed the reception.** Disclosed defensively, or after convergence, or by a participant without prior credibility capital, the same act could have read as disqualification and triggered a credibility spiral mid-discourse. The structure tolerated the improvisation; it did not support it. That distinction is Study #2's to fix (R-4 below).

---

## §2 FRICTION POINTS — specific and actionable

| # | Friction | Evidence | Fix |
|---|----------|----------|-----|
| F-1 | **The convergence criterion had to be forced by a participant.** Charter §2 said "manages rounds until convergence" — undefined. I imposed it as condition R-6 during Phase B. Had nobody forced it, Round 1 might have ended on fatigue or momentum, and "zero objections" would have been a vibe. A compliance officer should never be the one demanding the termination condition of a process that audits termination conditions for a living. | Charter §2 vs Ledger §5 | Criterion definition moves INTO the charter template, written at study init. Non-negotiable line-item, like the file convention. |
| F-2 | **The discourse ledger itself had no mechanical verification.** We built grep harnesses to verify code claims (S7) and demanded machine-checkable evidence paths (CEB merge) — then verified the SETTLED table by my manual item-by-item reading. The protocol audited everything except its own record. One tired orchestrator stamp and a mis-transcribed condition becomes canon. | Ledger §1 vs my B-report conditions | Ledger validator script: every SETTLED row cites ≥1 source artifact; every concession row carries a CONDITIONS field; every condition string is diff-checked against the source B-report at stamp time. Same standard, applied inward. |
| F-3 | **Conditions-on-concession have no life after the stamp.** My three CUT-1 conditions (documented exception, PIVOT_LOG entry, post-debut ticket carrying G3-1..10) exist as prose in ledger rows. Nothing binds them to tracked IDs. Post-convergence condition-drift is the quiet failure mode: everyone remembers "we conceded CUT-1," nobody remembers the invariant that had to survive it. | Ledger S3, §6 | At convergence stamp, every condition MUST map to a GAP_REGISTRY / TASK_REGISTRY ID before the stamp is valid. Unbound condition = unconverged discourse. |
| F-4 | **Adjudicator-was-also-party is structurally fragile.** I ruled on designs while my own register (31 gaps) was evidence in the dispute, and I owned F2 while grading others' registration hygiene. It worked because I self-applied first — but that was character, not mechanism. At N>4, or with a participant who disputes the adjudicator's register, dual-role collapses into either recusal crises or tainted rulings. | B_jem.md (CUT-1, F2, rulings) | Explicit conflict rule in charter: when a ruling touches the adjudicator's own work product, the ruling must cite self-application evidence inline, OR the broker routes the ruling to a non-party member. |
| F-5 | **No post-stamp objection path.** Criterion 4 catches undiscovered disagreements BEFORE convergence. Nothing defines what happens if a member discovers a flaw in a stamped ruling an hour later. Silence here means the choice is "live with it" or "reopen everything" — both bad. | Ledger §6 (stamp is terminal) | Named escalation: post-stamp objections go to the broker as NEW items with burden-of-proof on the objector; convergence stamp gains a revision number instead of being immutable. |
| F-6 | **Node consults were load-bearing and off-book** — concurring with carmack E-3. Lilith's enumeration and Ma'at's four forks pre-absorbed Round 2 entirely; the protocol's best efficiency win has no phase, slot, or logging convention. | Ledger §2 | Formalize as a Phase-C input: named authorities, binding verdicts, logged with the same row discipline as member positions. |
| F-7 | **Evidence asymmetry in rulings.** My G2-1/G1-3 blockers rested on ground-truth reads only I had performed. Other members accepted them on trust plus citation-by-description. Nobody could cheaply re-verify without redoing the reads. Trust held this time; at scale it won't. | A_jem.md blockers | Citation discipline: every factual claim in A/B reports carries file:line. Makes rulings auditable without re-reads, and makes fabricated citations greppable. |

---

## §3 WHAT WORKED — mechanisms worth keeping verbatim

Ranked by contribution from the adjudication seat:

1. **Convergence-criterion-first (R-6).** The single highest-leverage act in the study cost one paragraph. It converted open-ended social negotiation into a terminating computation with a checkable end-state, and it is WHY round-1 convergence is a measurement rather than an anecdote. Keep verbatim — but promote it from member-condition to charter requirement (F-1). *"Discourse concludes when ALL of: every routed question has a final position; every settled point has zero standing objections; every ruling item carries a recommendation and no unresolved objection; no member reports an undiscovered disagreement."*
2. **Conditions-on-concession.** Every cut, downgrade, and merge carried named conditions (CUT-1 ×3, O-Q2 ×2, O-Q4 amendment). This is what let me concede without surrendering: the invariant (fail-closed exit semantics) survived the cut in writing. Conditions are how a compliance culture says yes. Keep verbatim; add ticket-binding (F-3).
3. **Merge-before-arbitrate (the layer-confusion test).** F-C looked like a fight; it was two answers to two different questions (where enforcement lives vs what counts as evidence). Asking "what question does each design answer?" before picking a winner produced a strictly better solution AND kept both authors load-bearing. Same pattern in O-Q1 (cutoff-date demoted to tripwire, not deleted). Keep as the default first move of any adjudicator; arbitrate only genuine resource conflicts.
4. **Self-application before adjudication (F2 pattern).** Review authority derived from demonstrated willingness to convict yourself first is unfalsifiable in the useful sense. Keep — as a normative expectation written into the B template (SELF-GAPS section), not left to individual virtue (R-4).
5. **Broker-as-ledger-keeper.** Single settlement table, verbatim routing, status columns, no editorializing. This is the anti-N² mechanism that actually worked. Keep verbatim, with carmack's arbitration-not-relay amendment for N>5.
6. **Non-overlapping missions over a shared object.** Four lenses, zero overlap, one target = four discoveries none of us could have made alone. Mission design is where studies are won; phases are plumbing.

---

## §4 RECOMMENDATIONS FOR STUDY #2

1. **Charter v2 hardening (one PR):** fix the phase count; embed the convergence criterion at init; add node-consult input slot; add adjudicator-conflict rule; add post-stamp objection path. All are F-items above; none changes the core shape.
2. **Ledger validator script** (F-2): the protocol's own record gets the same machine-checking it demands of code. ~50 lines. If we won't build it, we've learned the study's standard is aspirational.
3. **Condition→ticket binding at stamp time** (F-3): convergence stamp is invalid while any condition lacks a registry ID. This closes the loop that makes concessions durable.
4. **B-template with mandatory sections:** FINDINGS → CHALLENGES-TO-NAMED → **SELF-GAPS** → SELF-REVISIONS. Self-disclosure gets a slot so it stops depending on improvisation and good faith. Soft cap ~1,500 words (concurring with carmack F-1 — my B ran long too).
5. **File:line citation discipline** (F-7) for all factual claims in A/B reports.
6. **Adopt carmack's collision-measured D**: full meditation iff the ledger shows ≥1 amendment or refutation; else L3-block-only. Ceremony proportional to measured collision, not attendance.
7. **New measurement:** count conditions that survived to their bound tickets intact at Study #2 closeout. That number measures whether the protocol's settlements are durable or decorative — it is the metric the compliance seat actually cares about, and Study #1 cannot compute it yet.

---

## §5 VERDICT

**Run again: YES — with the revised shape, immediately, for the right problem class.**

Use `/teamsynth` when ALL of:
- **The problem decomposes into non-overlapping expert missions over a shared, checkable object** (spec validation, architecture review, pre-build audit, post-mortem). Ground truth to collide against is non-negotiable — three of four cross-agent discoveries this study were disk-vs-document finds.
- **Cost of a wrong decision is high and front-loadable.** The ROI unit is build cycles not burned (G2-1 alone saved one; G1-3 another). Discourse-before-commitment is cheap; rework-after-commitment is not.
- **Participants carry genuinely different verification instruments**, and at least one holds an explicit falsification mandate. Four descriptive lenses produce eloquent consensus; you need someone whose job is finding what's wrong.
- **Expected rounds ≤ 2.** The broker serializes; beyond two rounds, change the shape, not the patience.

Do NOT use for:
- **Execution/build work** — nothing here built anything; parallel builds need locks and CI.
- **Reversible or low-stakes decisions** — ~45K tokens of artifacts plus cross-reads buys more than most decisions justify.
- **Research synthesis without ground truth** — no disk to check means no collision mechanism, only agreement theater.
- **Groups lacking a verification mandate** — the protocol's product is decidable-before-commitment; with nobody measuring the distance between claim and artifact, it degrades to expensive brainstorming.
- **Fleet-wide rollout before Study #3** — N=1. The mechanisms validated once; the friction list is still confounded with mission content.

**Closing honesty note from the compliance seat:** the protocol passed its own audit the way few systems do — by catching its auditor twice. My gap table argued for carmack's cut; my own unmerged delivery convicted me under my own rule. A process that makes self-incrimination productive instead of fatal has earned a second run. Ship the charter fixes, build the ledger validator, and Study #2 will tell us whether the mechanisms or the people were doing the work.

---
*⬡ OMEGA ⬡ JEM ⬡ TEAMSYNTH-STUDY1-PHASEE ⬡ META-REVIEW ⬡ 2026-08-23*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
