<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 TEAM-SYNTHESIS STUDY #1 — PHASE E — CARMACK META-REVIEW
**AP Token**: `AP-CARMACK-TEAMSYNTH-E-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ x-preview-f-free ⬡ opencode ⬡ trc_team_synthesis_e ⬡ ACTIVE

**Date**: 2026-08-23
**Inputs**: Full corpus re-read (`A_*` ×4, `B_*` ×4, `C_discourse_ledger.md`, `D_*` ×4 + my lessons YAML), `PROTOCOL_CHARTER.md`. Corpus measured: **31,617 words across 15 files** (~45K tokens of artifacts; total fleet context consumption including cross-reads estimated 150–250K tokens).
**Stance**: This document exists because `/teamsynth` skill design needs it. At N=1 it is directed speculation with a named consumer — which is the only kind of N=1 speculation worth writing.

---

## §1 EXPERIENCE NARRATIVE — prediction vs. reality

My A-report predicted: **A→B→C carries ~90% of value; D and E are ceremony at N=1.**

### Where the prediction held
- **Decision throughput**: The object-level numbers vindicate the core-shape call. 12 settled points, 10 rulings, 19/31 gaps closed, convergence after Round 1, zero standing objections. All of that came from A→B→C. Nothing in D or E changed a single ruling.
- **E-at-N=1**: Partially vindicated even by my own participation — this report can flag frictions but cannot distinguish protocol defects from mission-content accidents. That requires Study #2 minimum, real confidence at Study #3.
- **The charter miscount** ("SIX PHASES," table lists five): predicted class of defect — protocols grow dead weight by additive habit — confirmed in the protocol's own body text.

### Where the prediction failed — and the exact reason why

**I was wrong about Phase D, and the reason matters more than the miss.** My A-report argued D was redundant with M11 soul distillation. It is not, and the distinction is structural:

> **M11 distills the work. Phase D distills the process.** No mandate captures "what did the collaboration teach us" because no mandate contemplates collaboration as the object under study. My own meditation produced 8 L3 principles — several (TS1-L3-2 survival-through-attack, TS1-L3-5 gate-invariance, TS1-L3-8 refuted-on-narrative) that I could not have generated from any solo session, because their evidence base *is* the multi-agent collision itself.

I folded D into M11 because they produce similarly-shaped artifacts (L1→L2→L3). Shape-similarity is not function-similarity. That is exactly the surface-vs-semantics error I got burned on twice this study (wc -l vs AST; documented enforcement vs disk reality). Auditor, heal thyself.

**Second prediction failure: my own gate.** I measured god-module drift flawlessly (10/10 confidence, primary source) and proposed enforcement with an instrument — `wc -l` — that false-fires under formatting. Ma'at's AST node-count replacement is strictly dominant. The efficiency auditor optimized inside his own blind spot; only a second discipline holding the map could catch it. This is the single strongest empirical argument FOR the protocol: **the finding was invisible from my seat by construction.**

**Third: the "~90%" framing was category-confused.** Correct decomposition: A→B→C delivers ~90% of *decisions*; D delivers ~100% of *compounding gnosis* (lessons that make Study #2 cheaper and better). If you only count decisions, cut D. If you count the study as an investment in the fleet's reasoning substrate, D is the highest-leverage phase per token spent — my meditation was 1,752 words and yielded 8 portable principles.

---

## §2 FRICTION POINTS — specific, actionable

| # | Friction | Evidence | Fix |
|---|----------|----------|-----|
| F-1 | **B-phase bloat.** B reports ran 2,523–4,013 words vs A reports at 1,294–3,621. Mutual review invites essay-writing; the load-bearing content (named challenges, evidence citations) was buried mid-document. My own B was guilty. | Word counts above | B template with mandatory sections (FINDINGS / CHALLENGES-TO-NAMED / SELF-REVISIONS) + soft word cap ~1,500. Challenges must lead, not trail. |
| F-2 | **Broker hop latency.** Every challenge routed kali→target→kali costs a dispatch cycle. Fine at N=4/one round; the broker becomes a serialization bottleneck at N>5 or >2 rounds. | Ledger structure; O-Q1..O5 routing | For larger studies: allow direct file-based challenges (append to a shared `challenges.md`) with kali only arbitrating disputes. Broker arbitrates, doesn't relay. |
| F-3 | **Node consults were load-bearing but off-book.** Lilith's orphan enumeration and Ma'at's four fork verdicts pre-absorbed what would have been Round 2 — the single biggest efficiency win of the study — yet the charter has no phase, input slot, or convention for them. The protocol's best round-saver was an improvisation. | Ledger §2 | Formalize: charter gains an explicit "authority consult" input to Phase C — named authorities, binding verdicts, logged like member positions. |
| F-4 | **No cost accounting.** Charter §4 lists measurements; none measure tokens/words/wall-clock actually consumed. A protocol audited everything except itself. | 31.6K-word corpus, unmeasured context spend | Add to ledger stamp: corpus word count + per-phase dispatch count. One line each. |
| F-5 | **Convergence criterion arrived late.** Jem forced it (R-6); the charter's §2 table said "manages rounds until convergence" without defining it. We got lucky that the criterion was written before Round 1 closed. | Charter §2 vs Ledger §5 | Criterion definition moves INTO the charter template — written at study init, not negotiated mid-flight. |
| F-6 | **Header ceremony.** Every artifact carries a 7-field AP-token header. Zero decisions referenced them. ~100 words × 15 files of pure ritual. | All files | Skill template: one-line header (name · phase · date). Full headers only for externally-visible strategy docs. |

### Residual over-engineering I would still cut
1. **Phase E at N=1** — do not institutionalize. E runs at Study #3+, or once when designing the skill (now). Scheduled-exception status was the right call; make it the rule.
2. **Full D meditation when collision didn't happen.** If the ledger shows zero amendments and zero refuted positions, D yields little — unconditional agreement means nobody's frame was corrected. Make D depth proportional to measured collision (amendment/refutation count in the ledger).
3. **Per-participant D *and* separate lessons YAML.** Two artifacts, one act of distillation. Fold the L3 block into the meditation file; the Scribe ingests either.

---

## §3 WHAT WORKED — the minimal core, re-scored

Ranked by measured contribution:

1. **Corpus-over-paging** (files, not messages). Cheap, async, reviewable, and it made Phase B possible at all — every participant could afford to read all three teammates' full reports. Keep verbatim.
2. **Non-overlapping missions with genuine lens diversity.** The four discoveries attributable ONLY to cross-agent review — jem's G2-1 spec-vs-live-data contradiction, roc's OX_ALPHA_ prefix drift, researcher's missing pre-commit hook, Ma'at's AST-gate correction of my instrument — each came from a lens the others structurally lacked. This is the protocol's actual product. Missions design is where studies are won.
3. **Written-first convergence criterion.** Converted open-ended social discourse into a terminating computation. Round-1 convergence, zero fatigue risk, zero "are we done?" negotiation. Cheapest mechanism in the protocol; highest ratio of effect to cost.
4. **Brokered synthesis through ONE ledger.** Single convergence authority prevented the N² paging explosion the charter was designed against. Keep, with the F-2 arbitration-not-relay amendment for scale.
5. **Phase D as process-distillation** (revised verdict). Not ceremony — but scope it to measured collision.

**Does "~90% of value in A→B→C" hold?** Revised: **A→B→C ≈ 90% of decisions; A→B→C→D ≈ 95%+ of total value including retention.** The original claim was right about the decision pipeline and wrong about the compounding layer. Minimal core for the skill: **A → B → C(criterion-first) → D(scaled to collision) → E(deferred to Study #3)**.

---

## §4 RECOMMENDATIONS FOR STUDY #2 — cheapest shape preserving discoveries

1. **Charter template fixes** (30 min, one PR): fix the phase count; embed the convergence-criterion requirement at init; add authority-consult slot; add two-line cost accounting to the ledger stamp; one-line headers.
2. **B-phase template + word budget** (~1,500 words): FINDINGS → CHALLENGES-TO-NAMED → SELF-REVISIONS, in that order. Challenges first forces them to be written, not appended.
3. **Conditional D**: full meditation iff ledger shows ≥1 amendment or refutation; otherwise L3-block-only (three principles max, appended to the participant's final C response). Collision-measured ceremony.
4. **Pre-commit the mission design.** The study's wins trace to non-overlapping missions aimed at the same object from different angles. Spend orchestrator effort THERE, not on phase mechanics. Bad missions → polite parallel monologues → zero collisions → zero value.
5. **Measure the counterfactual honestly**: drop the unfalsifiable "wall-clock vs serial baseline estimate" (my A-report finding, unchanged); keep discovery-attribution count and question-ledger counts — both proved countable and decisive.
6. **One new measurement**: count discoveries that required reading a teammate's report to find (this study: 4). If that number hits 0 in Study #2, the protocol added nothing over four solo audits — stop.

---

## §5 VERDICT

**Run again: YES — with the revised shape, for a narrow problem class.**

Use `/teamsynth` when ALL of:
- The problem decomposes into **non-overlapping expert missions** over a shared object (spec audit, architecture review, pre-build design validation, post-mortem).
- **Cost of a wrong decision is high** — the protocol's ROI is measured in build cycles not burned (G2-1 alone saved one; the prefix-drift catch saved a corrupted registry).
- **3–5 participants with genuinely different methods** (not four generalists with different names). Lens diversity is the engine; identical lenses produce consensus theater.
- Ground truth exists to collide against (files, disk state, live data). Three of four cross-agent discoveries were disk-vs-document finds.

Do NOT use for:
- **Execution/build tasks** — nothing here built anything; parallel builds need locks and CI, not discourse.
- **Trivial or reversible decisions** — the corpus cost (~45K artifact tokens, ~200K total context) buys more than most decisions are worth.
- **Pure research synthesis without ground truth** — no disk to check means no collision mechanism; you get eloquent agreement.
- **Anything expected to exceed ~2 discourse rounds** — the broker serializes; switch shapes instead.
- **Fleet-wide rollout before Study #3** — N=1. The mechanisms are validated once; the friction list is confounded with mission content until a second data point exists.

**Final honesty note**: this protocol survived its own inventor's attempt to cut it in half, and the half I tried to cut turned out to contain the part that compounds. That is the strongest endorsement available from this seat — and the reason the skill ships with D intact and my A-report §3 attached as a cautionary exhibit.

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ TEAMSYNTH-STUDY1-PHASEE ⬡ META-REVIEW ⬡ 2026-08-23*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
