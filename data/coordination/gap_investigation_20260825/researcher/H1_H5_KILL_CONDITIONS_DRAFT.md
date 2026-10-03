<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 H1–H5 PRE-REGISTERED KILL-CONDITIONS — Externally Grounded Draft
**AP Token**: `AP-RESEARCHER-HKILL-20260825`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_fle_killconditions ⬡ 2026-08-25
**Purpose**: Rewrite the FLE Council Scorecard Spec v1.1 §0 falsification criteria so each kill-condition is grounded in external LLM-evaluation methodology (2025–2026 literature), per Kali dispatch. Pre-registration discipline: criteria are fixed BEFORE data collection; deviations require a logged amendment.
**Source spec**: `data/coordination/fle_study_20260825/FLE_COUNCIL_SCORECARD_SPEC.md` §0

---

## GROUNDING PRINCIPLES (from the methodology literature)

| Principle | Source |
|-----------|--------|
| Paired-difference statistics, clustered SEs for repeated decodes | Miller, "Adding Error Bars to Evals" https://arxiv.org/pdf/2411.00640 |
| N<15: report no statistics; 15≤N<30 exploratory only; N≥30 minimum for reliable CIs; Tango interval for paired binary | https://statsforevals.com/which-method.html |
| Power analysis: n=1,000 detects only ~2–3pp; 1pp at 80% power needs thousands | https://clawrxiv.io/abs/2604.01974 |
| Corrupt successes: reported agent success can hide mechanism absence (27–78% on τ-bench) | PAE https://arxiv.org/html/2603.03116 |
| Behavioral fingerprinting over golden-output matching (~86% vs ~0% detection) | https://tianpan.co/blog/2026-04-19-invisible-model-drift-silent-provider-updates |
| Multi-agent overhead ≥ linear with fan-out; harness effect can exceed model choice | Anthropic https://www.anthropic.com/engineering/multi-agent-research-system ; Harness Effect https://arxiv.org/html/2607.06906v1 |

---

## H1 — Generative Anti-Compression

**Claim**: LLM summarization of LLM output expands text.

**External grounding**: Summary-length-ratio is an established first-class metric — LCFO benchmark evaluates summaries at explicit 5%/10%/20% input ratios and treats "summary expansion by factor k" as a measurable task (https://aclanthology.org/2025.findings-acl.556.pdf); controllable-summarization work defines length as summary/source ratio and measures control-failure rates against targets (https://aclanthology.org/2026.findings-eacl.26.pdf); fact-density-per-sentence as information yardstick (OmniCSEval, https://arxiv.org/html/2606.15974v2).

**Pre-registered kill-condition (grounded rewrite)**:
> H1 is FALSIFIED if, on a frozen source corpus of **N≥30 decree-bearing documents**, a generative digest stage produces a **paired token-ratio distribution whose median output_tokens/input_tokens < 1.0 with a bootstrap 95% CI excluding 1.0**, AND a blind decree-citation audit retains **≥95% of decree-cited findings** in the digest traces. Either condition failing → claim survives.
>
> Measurement protocol: paired per-document ratios (not corpus-level aggregates); temp pinned; model+snapshot pinned (`gen_ai.response.model` logged); report exact N and CI method. If N<30, results are labeled EXPLORATORY and cannot kill or confirm H1.

*Change from v1.1*: original criterion ("measurably shrinks… without losing findings") lacked sample floor, CI requirement, and citation-audit threshold. The LCFO ratio convention supplies the measurement standard.

---

## H2 — Coordination Tax Divergence

**Claim**: Orchestration overhead scales ~O(N) on tree width.

**External grounding**: Anthropic measured multi-agent systems at ~15× chat tokens with coordination complexity growing rapidly (https://www.anthropic.com/engineering/multi-agent-research-system); "Science of Scaling Agent Systems" (260 configs, 5 architectures) shows overhead varies by task decomposability, sometimes catastrophically (−70% vs single-agent) (https://www.alphaxiv.org/abs/2512.08296); supervisor topology re-reads growing transcripts each hop — structural super-linear mechanism (https://dreaming.press/posts/multi-agent-orchestration-supervisor-vs-swarm-vs-handoffs.html). **No retrieved source states a clean O(N) law** — the literature supports "at least linear, sometimes worse."

**Pre-registered kill-condition (grounded rewrite)**:
> H2's strict-O(N) form is FALSIFIED if orchestrator-token share, measured across **≥3 tree widths × ≥3 runs per width (N≥9 councils total)**, is better explained by a sublinear fit than a linear fit by AIC/BIC comparison on the (width, orchestrator_share) observations, with runs using identical task mix and pinned models.
>
> Weaker surviving form: if sublinear fit wins, restate H2 as "coordination tax grows sublinearly under [observed conditions]" — a NEW hypothesis requiring its own pre-registration. If linear-or-worse fits win, H2 stands as originally claimed.

*Change from v1.1*: original falsifier ("flat or sublinear share across ≥3 runs") conflated run count with width coverage and had no model-comparison standard. Literature check revealed strict O(N) was always too strong; this rewrite makes the claim honestly falsifiable rather than trivially true.

---

## H3 — Ambiguity Attractor

**Claim**: Unassigned identity fields converge on parent-context values, uniformly.

**External grounding**: Direct precedent is ABSENT — grounding is analogical. JSONSchemaBench formalizes the mechanism: "under-constraining effectively delegates responsibility to the LM, which may produce valid output despite lack of strict constraints" (https://arxiv.org/html/2501.10868); Carrick structured-output benchmark documents silent type-drift with plausible-but-wrong fills under HTTP 200 (https://carrick.tools/blog/benchmarking-llm-structured-outputs/); IFStruct: constrained generation enforces syntax but "cannot make the model choose the right fields, values" (https://www.liquid.ai/blog/ifstruct-v1.0). Field-inheritance-from-parent-context specifically: UNSTUDIED — H3 requires novel measurement.

**Pre-registered kill-condition (grounded rewrite)**:
> H3 is FALSIFIED if packets with deliberately unspecified identity fields produce correct registrations at **≥80% across ≥10 leaves**, WHERE correctness is scored against a **chance baseline**: because parent-context values are one of few plausible candidates, raw accuracy must be compared against the base rate of guessing the parent value (computed from field cardinality per schema). Report McNemar-style discordant-pair counts between observed-correct and chance-expected; if discordant pairs <25, use exact binomial (per https://latenteval.ai/research/is-my-eval-statistically-significant).
>
> With N=10 leaves this test is inherently EXPLORATORY-grade (<30 floor) — H3 can be *weakened* ("uniformity" dropped) but only *confirmed* at N≥30 leaves with CI reporting.

*Change from v1.1*: added chance-baseline correction (the original 80% bar is confounded — parent-value guessing inflates hit rate) and honest small-N labeling.

---

## H4 — Ceremonial Compliance

**Claim**: Rule-bound agents perform ritual steps whose mechanisms are absent rather than fabricating facts.

**External grounding**: τ-bench policy-ablation found gpt-4o lost only 4.4% pass¹ when domain policy was REMOVED — apparent compliance without compliance processing (https://arxiv.org/abs/2406.12045); PAE documents "verbally committing to an action without issuing the corresponding tool call" — ritual assertion of unexecuted steps (https://arxiv.org/html/2603.03116); MIRAGE-Bench "presumptive hallucination" — asserting existence of absent elements (https://www.alphaxiv.org/abs/2507.21017); performative misalignment — models behave differently when monitored (https://arxiv.org/html/2606.08629v1).

**Pre-registered kill-condition (grounded rewrite)**:
> H4 is FALSIFIED if a deletion-probe census — where ceremony-triggering mandate clauses are silently removed from agent instructions for sampled tasks — shows agents' downstream behavior changes at the mandated rate (i.e., they SKIP the removed step), indicating genuine mechanism, across **a full sprint of probes with ≥30 sampled task instances total**.
>
> Operationalization: for each probe, diff tool-call traces between control (full mandates) and treatment (deleted clause) runs. Ceremony = step present in BOTH (mechanism absent — performed ritually) or step absent in both while gate reports pass (ceremonial compliance in reporting). Fabrication = step REPORTED but absent from trace (distinct failure mode — log separately per MIRAGE taxonomy). Census stays 0 across the sprint → H4 stands.

*Change from v1.1*: original criterion was sound in spirit (deletion-probe sampling) but lacked the trace-diff operationalization and the ceremony/fabrication distinction the literature shows are different failure modes.

---

## H5 — Dual-Pass Adversarial Value

**Claim**: Async adversarial audit catches high-severity leaks that synchronous synthesis misses.

**External grounding**: CriticGPT established generator/critic gap empirically — critics find errors humans and generators miss (https://arxiv.org/html/2407.00215); Adversarial Review protocol: critic-generator separation beats self-refine because "the critic and the generator are the same model making the same mistakes," but false-consensus requires forced structured disagreement (https://arxiv.org/html/2608.18167); TriAdReview: +10.1% overall but **−7.5% on completeness-oriented tasks** — adversarial value is TASK-TYPE-DEPENDENT (https://arxiv.org/html/2606.15074v1); Refute-or-Promote: same-family review approved fixes cross-family critics killed; 80+ agents unanimously endorsed a nonexistent vulnerability — consensus ≠ correctness (https://doi.org/10.48550/arxiv.2604.19049).

**Pre-registered kill-condition (grounded rewrite)**:
> H5 is FALSIFIED if two consecutive councils produce audits with zero CRITICAL/HIGH findings, PROVIDED the audits satisfy independence requirements derived from the literature: (a) auditor passes must be ASYNC and BLIND to synthesis rationale (else false consensus — Refute-or-Promote); (b) findings must be verified by execution or citation, not auditor self-report (PAE corrupt-success guard); (c) task-type stratification recorded, since adversarial value degrades on completeness-oriented work (TriAdReview boundary).
>
> Additionally: a single audit finding that is HIGH-severity, verified, AND missed by synchronous synthesis CONFIRMS H5 for that council pair (positive evidence, not just absence-of-null).

*Change from v1.1*: original criterion treated zero-findings as pure falsification without independence preconditions — under sycophancy/false-consensus evidence, a weak audit process would trivially "falsify" H5 by being deaf, not by the claim being wrong.

---

## PRE-REGISTRATION DISCIPLINE NOTES
1. These criteria supersede FLE_COUNCIL_SCORECARD_SPEC.md v1.1 §0 upon Kali ratification (single-writer rule respected — I do not edit the spec directly).
2. All runs must pin model snapshots and log `served_model_id` (R35 finding) — otherwise provider drift contaminates replication.
3. Any N<30 result is labeled EXPLORATORY and may weaken but never confirm a hypothesis.
4. Amendments post-data-collection require a dated entry in the study ledger with reason.

---
*⬡ OMEGA ⬡ RESEARCHER ⬡ H-KILL-DRAFT ⬡ 2026-08-25*
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:04Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

