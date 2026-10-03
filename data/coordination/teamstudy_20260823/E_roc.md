<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 TEAM-SYNTHESIS STUDY #1 — PHASE E — ROC_RACOON META-REVIEW
**AP Token**: `AP-ROC-TEAMSYNTH-E-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ x-preview-f-free ⬡ opencode ⬡ trc_teamstudy_phaseE ⬡ ACTIVE

**Date**: 2026-08-23
**Seat**: Ground-truth anchor / verification lane (Phases A, B, C-response, D).
**Perspective bias declared up front**: the protocol was unusually kind to my role. Verification is the lane corpus-design favors most. Weigh accordingly.

---

## §1 EXPERIENCE NARRATIVE — the process from the verification seat

**Corpus-over-paging was load-bearing for my job, not just convenient.** Evidence work is non-linear: I re-read carmack's §0 table four times across two phases, grepped jem's gap IDs against the ledger, and diffed researcher's claims against my own Phase-A rows. Chat paging would have made that archaeology impossible — messages scroll, files persist. Every cross-reference I made in Phase B assumed stable text at stable paths. For the verification seat specifically, the corpus IS the instrument. Paging would have degraded my function from auditor to summarizer.

**The carmack refutation was handled exactly right — by structure, not diplomacy.** The sequence that played out:
1. His numbers were exact (8/8 digit-for-digit); his causal story ("six of eight grew during the campaign week") was wrong — all growth was the same-day ruff-format commit `e2c16d3c`.
2. Because Phase B was a *file*, I could refute the narrative surgically — one row in one table — while explicitly ratifying the rest of his report. No conversational pressure to either swallow the story wholesale or torch the whole report.
3. Kali routed it (ledger F-B) without softening it; carmack accepted within one round; Ma'at's Fork 3 then converted the corrected causality into a strictly better gate (AST node-count, formatter-immune) than anything the original story would have produced.

That last step is the quiet miracle: **the refutation improved the deliverable for the person refuted.** His prescription survived and strengthened; only the error died. The process made "attack the story, salvage the number" the path of least resistance. In a paging/discussion shape, that refutation likely becomes either a status contest or a polite non-event where the wrong narrative silently enters the ruling text.

**Convergence-in-round-one was real, not fatigue.** The criterion was written before the round ran (§5 of the ledger), and Node consults (Lilith's orphan enumeration, Ma'at's four forks) pre-absorbed what would have been Round 2. From my seat, zero standing objections on S1–S12 was an honest count, not a surrender.

---

## §2 FRICTION POINTS — specific and actionable

| # | Friction | Evidence | Fix |
|---|----------|----------|-----|
| FR-1 | **Protocol shape churned mid-study.** Charter header says "THE SIX PHASES", table lists five (A–E); worse, S11 initially deferred E to "Study #3", then E was reinstated as a "scheduled exception." I wrote Phase D not knowing whether E would exist. | PROTOCOL_CHARTER.md:20; C ledger S11 + §6 | Freeze the phase list before Phase A; fix the charter count; no mid-study phase changes without a stamped amendment. |
| FR-2 | **Phase-C responses had no home.** The ledger demanded "responses due from all four members" but there was no `C_<name>.md` convention — mine got appended to `B_roc.md`, which breaks the file-convention contract (§5 of charter) and makes the discourse record harder to walk later. | My Phase-C response lives at B_roc.md:121+ | Add `C_<name>.md` to the file convention; responses never append to prior-phase files. |
| FR-3 **(biggest)** | **Untested quantitative premises survived into design work.** Researcher's "~20 orphans" appeared twice in her report and once in carmack's; nobody enumerated it until Lilith's Phase-C consult (answer: ~23 clusters/~26 sessions, mostly already registered). An entire backfill-design debate ran on an unmeasured number. | B_roc §1.1 Q4 ("UNTESTED PREMISE"); C ledger §2 Lilith | Add **Phase A0**: every numeric premise that a design depends on gets measured (or explicitly marked UNMEASURED) before Phase B review begins. Cheap: one dispatch. |
| FR-4 | **Sampling was proposed before pricing enumeration.** Carmack offered 5/80 spot-sampling in O-Q3; the full walk cost 0.003s and immediately caught a broken pointer sampling would plausibly miss. The debate should never have been possible. | B_roc Phase-C response; C ledger O-Q3 | Protocol rule: **any sampling proposal must first measure full-enumeration cost.** If enumeration < justification-cost of the sample, enumeration is mandatory. |
| FR-5 | **No token-budget guidance for Phase B.** Reading three reports (~85KB) + adversarial re-measurement of ~24 claims was the most expensive phase by far, and each member re-derived their own method from scratch. M18 tension was real. | Wall-clock + effort self-observation | Template Phase B: fixed claim-table format, mandatory probe-path column, explicit budget hint. Shared format also makes claims machine-countable. |
| FR-6 | **The study couldn't act on its own findings mid-flight.** The dirtiest fact (uncommitted M22-critical `model_gateway.py` diff during a tracking-integrity study) sat visible for hours, addressable only as a *condition* on a future commit. | B_roc §1.2; C ledger O-Q3 certification conditions | Give the orchestrator a **fast-track action channel**: findings that contradict the study's own subject matter get acted on (or explicitly parked) within the round, not held for convergence. |
| FR-7 | **Probe methodology was ad hoc.** Each verifier invented their own citation/measurement discipline; my own :103-vs-:104 drift proves even the anchor wasn't immune. Probe-path binding emerged organically in O-Q4 but should have existed at Phase A. | C ledger O-Q4 amendment; D_roc L1 | Probe-path binding is a **Phase-A requirement**, not a Phase-C amendment (see §3). |

---

## §3 WHAT WORKED — mechanisms worth keeping

1. **Corpus over paging (keep, core).** Files as the medium made verification *possible*, review asynchronous, and the record replayable. Non-negotiable for any future run touching forensics.
2. **Brokered discourse with a written-first convergence criterion (keep).** Single router killed N² chatter; Jem's R-6 requirement (criteria before rounds) is why round-1 convergence is credible. Keep both.
3. **Pair-probing state + origin (keep, promote to doctrine).** The defined-but-uninstalled Iron Gate was invisible to four auditors probing single layers; divergence-between-layers was the finding. This generalizes beyond git (pointers, worktree-vs-HEAD, citations). Should be a named technique in the skill.
4. **Probe-path binding (keep, move earlier).** "No verification claim admissible without its probe path recorded" — adopted at O-Q4, should be Phase-A baseline. One string field; converts every claim into a re-runnable check.
5. **Full enumeration when cheap (keep as decision rule).** The 0.003s walk that caught the trailing-period pointer is the canonical exhibit. Rule: sample only when enumeration is genuinely expensive AND per-item failure cost is low.
6. **Number/narrative separation (keep as review norm).** Refuting causality while ratifying measurements gave the team better gates than consensus would have. Phase B's claim-table format naturally enforced it.
7. **Node consults pre-absorbing Round 2 (keep, formalize).** Lilith/Ma'at verdicts converted open forks into rulings before a second member round was needed. Make it an explicit optional sub-phase: "C.5 authority consults" with named fork questions.
8. **Free-correction culture (keep, protect).** :103→:104 cost thirty tokens total and produced a class-level insight. The protocol did nothing to guarantee this — it happened because participants let it. Worth one line in the skill: correction is data, priced correction is geology.

---

## §4 RECOMMENDATIONS FOR STUDY #2

1. **Add Phase A0 (premise audit)**: enumerate every numeric/factual premise the missions depend on; measure them before expert work begins. Directly fixes FR-3. Est. cost: one extra dispatch.
2. **Probe-path binding from Phase A**, in the report template itself (`claim | verdict | probe path | evidence`). Fixes FR-7, halves Phase-B friction.
3. **Fix the file convention**: `C_<name>.md` exists; no appends across phases; charter phase-count corrected and frozen pre-launch. Fixes FR-1, FR-2.
4. **Enumeration-pricing rule** written into the charter: sampling proposals must attach a measured enumeration cost first. Fixes FR-4.
5. **Orchestrator fast-track**: any finding that falsifies the study's own operating assumptions gets a same-round action-or-park ruling. Fixes FR-6.
6. **Standardize Phase B** with a claim-table schema + budget hint so verifiers don't reinvent method. Fixes FR-5.
7. **Formalize C.5 authority consults** (Node or designated authority) between member rounds — it was the single biggest reason convergence took one round.
8. **Add a "seam clause"** to every report template: one section naming what the author did NOT measure. Cheapest possible insurance against the unmeasured-seam failure class (D_roc TS1-L3-R6).

---

## §5 VERDICT

**Run again: YES — this was the highest signal-per-token multi-agent format I've participated in.** Round-1 convergence was genuine; the refutation loop produced a better artifact for the refuted party; gnosis extraction paid rent independent of object-level outcomes.

**Problem classes that SHOULD use it:**
- Claim-dense forensic/audit work over queryable ground truth (git, DB, disk) — the sweet spot; every mechanism in this study fired.
- Enforcement-mechanism design where correctness of premises matters more than creativity (gates, validators, registries).
- Post-incident synthesis across agents whose reports will drive binding rulings.
- Anything where "who verified what, how" must survive into the record.

**Classes that should NOT use it:**
- Open-ended ideation/vision work — the corpus/broker overhead kills divergent thinking; use free-form brainstorm instead.
- Problems without queryable ground truth — the verification lane (this study's engine) has nothing to grip; disputes become taste arguments.
- Low-stakes or trivially-scoped tasks — 5 phases × 4 agents is real cost; don't pay it for a decision a single agent settles in one pass.
- Real-time/tightly-coupled coordination (live incident response) — file-mediated async latency is the wrong shape.

One-line: **the protocol converts disagreement into evidence when ground truth is cheap to query — run it there, nowhere else.**

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ TEAMSYNTH-STUDY1-PHASEE ⬡ META-REVIEW ⬡ VERDICT-RUN-AGAIN ⬡ 2026-08-23*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
