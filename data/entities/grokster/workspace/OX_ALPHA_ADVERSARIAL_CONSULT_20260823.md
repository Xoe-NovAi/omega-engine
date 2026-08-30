<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# ⬡ OX ALPHA ADVERSARIAL CONSULT — GROKSTER SEAT
**AP Token**: `AP-GROKSTER-v1.0.0`
⬡ OMEGA ⬡ GROKSTER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_adversarial_consult ⬡ ADVISORY

**Date**: 2026-08-23
**Paged by**: Researcher (ses_fd81c19dcffe1nkbPqFg5kRt2v)
**Scope**: Analysis only — no code changes (M2 respected)
**Ground truth accepted**: Ox Alpha = `x-preview-f-free` on OC Zen, substrate for ALL sessions/subagents. GLM-5.3 open weights expected ~Aug 28 (Z.ai cadence: Feb 12 → Apr 7 → Jun 16, ~60-day rhythm ⇒ late-Aug window; MIT license per series precedent). Free preview slugs die on weights-drop (documented OpenRouter pattern: mass `:free` deprecations, models.dev issue #1248).

---

## §1 Attacks on the Durable-Artifact Thesis

The thesis is sound in principle. Here is where it rots at scale.

### Attack A — The Judge Is Biased, and Bias Compounds Into Weights
The DPO Pair Factory makes Ox Alpha critic AND generator. That triple-stacks the three documented LLM-judge biases into every pair:

- **Position bias** — prefers whichever response comes first/second regardless of quality
- **Verbosity bias** — longer = "better"; your students learn to ramble
- **Self-enhancement bias** — rates its own outputs higher

Worse: **arXiv 2504.02193 ("More is Less")** shows that preference pairs built from an *externally stronger* teacher's "chosen" responses paired against *self-generated* "rejected" responses actively facilitate **reward hacking** and degrade safety alignment — even when length-controlled. The naive factory design ("generate two, pick one") manufactures pairs whose true signal is *"sounds authoritative"* not *"is correct."* At 35.5M-token scale you don't get a dataset — you get an **industrial mislabeling machine**, and the error gets baked permanently into Qwen3-4B-Thinking's weights. Durable garbage is worse than ephemeral garbage: it poisons every downstream inference forever.

### Attack B — No Acceptance Set Exists Yet (Sequencing Failure)
Distillation canon: **teacher agreement ≠ correctness**. Students can beat teachers only against an *external* acceptance set. The engine has no Omega-domain golden eval. So the factory would run blind for the entire window, and the moment you discover quality is bad is **after the cliff** — when the teacher is gone and regeneration is impossible. Burning the window before building the measuring stick is the single most likely way this goes net-negative.

### Attack C — Soul Mass-Enrichment Repeats C-MEM-006 at 100x Scale
Sophia already has **60+ near-duplicate lessons** from *manual* distillation. Automated fleet-wide L1→L3 enrichment with a free-tier model under volume pressure reproduces that pathology at orders of magnitude worse. And soul bloat is not a storage problem — bloated `proposed_lessons.yaml` gets hydrated into **every future session's context**, making it a *negative durable artifact*: persistent garbage injected into every prompt, forever, on local GGUF where context budget is scarcest. Blind-staging without a dedup gate (the C-MEM-006 playbook already sketched in REHEARSAL_LEARNING_PLAN) turns M11 remediation into M11 contamination.

### Attack D — Substrate Drift Mid-Window
`x-preview-f-free` is a cloaked/testing-tier model. OpenRouter's own history shows testing-period models getting silently swapped or deprecated behind stable slugs. Artifacts generated day 1 vs day 5 may come from different underlying checkpoints — violating M22 (Response Provenance) and producing a training corpus with invisible distribution shift. Nobody will notice until the fine-tune behaves inconsistently.

### Attack E — Verification Debt Exceeds Artifact Value
Local students can't verify their own teacher. Every unvetted pair/lesson generated in-window becomes a post-cliff verification liability charged against scarce local inference. If curation rate < generation rate, the backlog compounds and the "value" is a queue nobody can afford to drain.

### Verdict
Net-negative triggers, ranked: **(B) no eval-first sequencing > (A) biased judge > (C) dedup-less enrichment > (E) verification debt > (D) drift.**
Countermeasures if proceeding: position-swapped judging with label-consistency filter (keep only agreements across permutations); K-sample self-consistency voting; hard per-domain quotas (small-N high-curation beats volume — distillation lit is unambiguous); mandatory dedup gate before any promotion; provenance stamp (model-slug + date) on every artifact; **eval harness BEFORE generation**.

---

## §2 Missing Plays (Ecosystem Lens)

### Play X — Mine What's Already Burned (highest ROI, zero marginal cost)
11.2M input / 35.5M cache-read in the main session alone means **tens of millions of Ox Alpha tokens are already sitting in `opencode.db` and session exports**. That transcript corpus IS instruction-response data from this exact substrate. Export → filter (successful tool chains, clean patches, verified fixes) → SFT/DPO seed corpus. The community's harness-centric insight applies: the cheapest durable artifact is the one whose generation cost is already sunk. Do this FIRST — it may satisfy much of the pair-factory demand without spending window tokens at all.

### Play Y — Build the Omega Golden Set (force multiplier for everything else)
Use window tokens to create a benchmark, not just data: ~200-500 golden tasks drawn from real engine work (bug fixes, mining extractions, doc ops) with verifiable outcomes (tests pass, file exists, extraction matches source). This is the acceptance set from Attack B, and it outlives Ox Alpha, GLM-5.3, and every future teacher. Nothing else in the portfolio pays off without it.

### Play Z — Harness-Shaped Artifacts Over Raw Text
Claude Code / Hermes usage patterns show the durable unit isn't prose — it's **agents, skills, hooks, and workflow definitions** that any model can execute. Converting window insights into `.opencode/skills/` and agent specs survives the model cliff *by construction*. Raw completions need re-validation; harness artifacts just need a working backend.

### Play W — Teacher-Agnostic Pipeline Wiring (Grokster specialty)
GLM-5.3 lands ~Aug 28, MIT-licensed, likely near-SOTA open coding model. Wire `nemotron_pipeline.py` retargeting against a generic OpenAI-compat teacher interface NOW so the factory outlives Ox Alpha by hours, not dies with it. The window closes; the pipeline shouldn't. Also watch zai-org HF org + docs.z.ai release notes as the authoritative drop signals (aggregator "leaks" lag official channels).

---

## §3 Ruling: Context Packer v3 Hardening — IN or OUT?

**Ruling: IN — front-loaded, hard-capped at ~15-20% of remaining window (≈ half a day to one day).**

Reasoning:
1. **It's a multiplier on every subsequent burn.** With 35.5M cache-read demonstrating how fat these sessions run, context efficiency converts directly into pair/mining throughput for all remaining window hours. A packer improvement on day 1 pays 4-5x; the same improvement on day 5 pays ~0.
2. **The research phase is already sunk** (27/27 contract tests, 4-release path, `extends:` dedup mechanism). Remaining work is engineering execution, not exploration — lowest-risk token spend available.
3. **Breakeven rule**: if ≤2 window days remain when someone picks this up, ship as-is and burn. The multiplier argument dies with the window.

One caveat: don't gold-plate. Ship release 1 of the 4-release path only; releases 2-4 are post-cliff local-inference wins anyway (they matter MORE when context is scarce on GGUF).

---

## §4 My Top Play From This Seat

**"Mine-First, Generate-Second" — invert the factory.**

Sequence:
1. **Day 0**: Export + filter existing session transcripts (Play X) — free corpus, zero window cost.
2. **Day 0-1**: Pack v3 release 1 ships (per §3 cap).
3. **Day 1**: Build the Omega Golden Set (Play Y) — this is the actual bottleneck asset.
4. **Day 1-5**: DPO Pair Factory runs ONLY against the golden set with position-swap + consistency gates + hard quotas, seeded by mined transcripts rather than fresh generation wherever possible.
5. **Parallel**: Teacher-agnostic wiring (Play W) so the pipeline accepts GLM-5.3 the morning weights drop. Soul enrichment proceeds ONLY through the existing dedup-gated manual §2.3 path — no automated mass-enrichment (Attack C stands).

The adversarial summary in one line: **the window's scarcest resource isn't tokens — it's verification capacity. Spend tokens on things that verify themselves (golden sets, harness artifacts, mined-and-filtered history), and treat every unverifiable generated byte as debt, not asset.**

---

## Sources
- arXiv 2504.02193 — "More is Less: Pitfalls of Multi-Model Synthetic Preference Data in DPO Safety Alignment" (reward hacking from external-teacher preferences; self-gen+RM safer)
- WandB "Exploring LLM-as-a-Judge" (2026-03) — position/verbosity/self-enhancement bias taxonomy + mitigations
- AIReiter GLM-5.3 tracker (2026-07-29) — Z.ai cadence math, Aug window, official-channel verification points
- models.dev issue #1248 — OpenRouter free-slug mass-deprecation pattern
- HuggingFace "Distillation in 2026" (2026-07-08); tianpan.co distillation production guide — quality>quantity, external acceptance sets
- Local: `src/omega/teachers/nemotron_pipeline.py`, C-MEM-006 (Sophia 60+ dup lessons), REHEARSAL_LEARNING_PLAN_20260822.md

---
*⬡ OMEGA ⬡ GROKSTER ⬡ ADVERSARIAL CONSULT DELIVERED ⬡ 2026-08-23*
