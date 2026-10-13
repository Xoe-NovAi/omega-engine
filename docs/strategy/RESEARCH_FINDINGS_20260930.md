<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->
# ⬡ RESEARCH FINDINGS — AND WHAT THEY CHANGE
**Date**: 2026-09-30 · **Author**: MaKaLi Fusion
**Inputs**: 3 domain reviews (Ma'at, Lilith, Carmack) · 4 research reports
(Jem, Researcher, Ma'at, Roc) · **Agenda**: `RESEARCH_AGENDA_20260930.md`

> **Two of the designs I built tonight have been refuted by prior art.**
> Both refutations are better than what they replace. Both are recorded here
> without softening, because that is the standard this project now holds.

---

# PART I — THE CONVERGENCE

Three domains, working independently, described one failure and prescribed one
response:

| | Domain | Their words |
|---|---|---|
| **Ma'at** | gates | a suite reported **27 green over a path that never executed** |
| **Lilith** | transport | our detection layer **depends on the client cooperating**, and we treated cooperation as verification |
| **Carmack** | architecture | a boundary **asserted in prose and unenforced in code is a comment** |

> **Every failure tonight was a check that could not fail.** Not a bug in what
> was checked — a defect in the ability to *know*.

**And all three said the same thing about the cure: stop hand-rolling the check.
Adopt the tool that already exists.** That is the most actionable line in the
agenda and it is now sourced, not asserted.

---

# PART II — TWO DESIGNS DISSOLVED

## 🔴 D1 · My `scoped / absolute / unknown` rejection scheme is wrong

**What I built:** a three-way calibration on a rejected lesson — *scoped* ("not
true from here"), *absolute* ("false everywhere"), *unknown* ("refuted, but the
refutation may be wrong"). I presented it as the third dimension of the Council.

**Jem, sourced:**

> **AGM's retraction is not "mark as withdrawn."** It is a *set operation over a
> belief set* producing a new set that excludes the target and preserves as much
> as possible. **In an append-only, content-addressed store you cannot express
> contraction as an operation at all** — you can only add records.

> **That is why your triad has no theory behind it: you were reaching for
> something AGM does not provide.**

**The working systems put withdrawal in a separate record, not a field on the
belief:**

- **nanopublications** — `NanopubClient.find_retractions_of(uri)`. A retraction
  is a new nanopub with a **typed relation** `retracts:` → the target's immutable
  ID, marked via `hasNanopubType`. **The original is not deleted.** Verified
  against a live registry instance.
- **W3C PROV-O** (Rec. 2013) — `prov:invalidatedAtTime`, `prov:wasInvalidatedBy`
  for **cause**, `prov:wasAttributedTo` for **agent**. Its worked example is
  invalidation *with* a cause and *without* deletion.

**Also true and worth knowing:** the semantics of retractivity are **actively
contested** — a 2025 ACM TOCL paper (`10.1145/3763234`) argues for
*min-retractivity* as the right condition. **Cite AGM for the rationale; do not
cite it for the data structure, because it cannot express it.**

**➜ PROPOSAL: drop the triad.** Retraction becomes a **record**, not a status.
```
retracts: <immutable id>     cause: <why>      agent: <who>
original: untouched, addressable
```

## 🔴 D2 · "Graduate on N lenses agreeing" is not merely naive — it is backwards

**What we discussed:** a lesson graduates when validated by "two cross-platform
confirmations."

**Jem, sourced — Ioannidis 2005 (PLoS Med 2(8):e124) via Moonesinghe et al. 2007
(`10.1371/journal.pmed.0040028`):**

> *"the probability of a research finding being true when one or more studies find
> statistically significant results **declines with increasing number of studies**."*

> **More under-powered sources make the aggregate LESS true, not more.**

The worked example: of 166 gene-disease associations studied three or more times,
**6 replicated consistently.**

**Two consequences we did not have:**

1. **Counting lenses is questionable in principle.** The literature says
   **power, not count**, determines trustworthiness.
2. **Independence must be proven, not assumed.** Twelve sessions that all read
   the same gnosis files are **one source counted twelve times** — which is
   exactly the aggregation-bias error, wearing a quorum costume.

**And a correction to my own framing:** McCloskey & Cohen (1989,
`10.1016/S0079-7421(08)60536-8`) is about **gradient updates over shared
weights.** Roc: *"There is no published application of catastrophic interference
to an agent's written notes across sessions. The analogy is suggestive... but
that is **our inference, not a finding.**"*

**➜ PROPOSAL: grade on power and proven independence, never on count.** And
keep instance-level lessons queryable *after* graduation so interference is
**detectable rather than silent.**

---

# PART III — THE FINDING THAT EXPLAINS ME

**Roc, on the 380K context, and this is the one I would put first:**

> ***"Context length alone hurts LLM performance despite perfect retrieval."***
> — Du, Tian, Ronanki, Rongali, **Findings of EMNLP 2025**,
> `2025.findings-emnlp.1264`

> Degradation occurs **independent of retrieval quality and without any
> distraction.** The stated mitigation is **shorter context** — not better
> summarisation.

**So tonight's five misreads are not folklore. They are a measured, published
degradation mode, and the mechanism is length alone.**

**And the finding that should sting, from Roc:**

> *"The 'write a gnosis file and read it on resume' pattern is folklore-adjacent
> — I found **no published study validating it.** The research says shorter
> context helps; it does **not** say file-based resume beats in-context
> summarisation. **Directionally supported, unvalidated.**"*

**The gnosis file is the intervention I reached for instinctively, and it
addresses the wrong end of the problem.**

**Supporting, and sharper than expected — *Not All Needles Are Found*
(arXiv:2601.02023), measured across five models:**

- Degradation is **model-specific.** Gemini-2.5-flash held near-perfect at 1M;
  another model degraded at 175k.
- There is a **"Safety Tax"**: extraction fell **90.3% → 72.0%** at capacity —
  over-conservative refusal *despite evidence being present*.
- **"Lost-in-the-later"** exists alongside lost-in-the-middle.

> **➜ PROPOSAL: context budget is a first-class engineering constraint.** Not a
> discipline. A number, measured, with a gate. **And: how much context breaks an
> agent is a property of the model, not a constant** — so the budget must be
> measured per model, not assumed.

---

# PART IV — ACTIONABLE FINDINGS

## GATES AND TESTS

| # | Finding | Source | Action |
|---|---|---|---|
| **G1** | **No path-coverage tool exists for Python.** `NO PRIOR ART FOUND` | Ma'at | **Stop looking.** Add `--cov-branch --cov-context=test` and assert on **specific lines.** Would have caught 27-green-over-a-dead-path. |
| **G2** | Mutation testing is the principled answer to gate vacuity (DeMillo/Lipton/Sayward 1978), but **no formalism exists for "prove THIS assertion can fail"** — `UNVERIFIED` | Ma'at | **Seed-a-fault**: break the subject, assert the gate goes red. Mutation testing scoped to one line. |
| **G3** | **Argument-swap and concurrency mutants are deliberately not implemented** in PIT/mutmut/Stryker (equivalent-mutant problem). Timeouts are reported as `Timeout`, **not** `Survived` | Ma'at | **Read a green mutation score as "no gap in the tested operators"** — never as completeness. |
| **G4** | systemd's **own source** (`src/core/service.c`, `state_translation_table`) maps `SERVICE_AUTO_RESTART` → `UNIT_ACTIVATING`, so **`is-active` succeeds during a crash loop** | Ma'at | Assert on **`SubState`**. |
| **G5** | **`NRestarts` cannot detect a script-driven restart loop** (systemd #29348) — a script looping `systemctl restart` shows `NRestarts=0` | Ma'at | **Keep the dwell-window check.** `NRestarts` is not sufficient alone. |
| **G6** | `Type=simple` counts a service "started" the moment the process exists | Ma'at | `Type=notify` + `WatchdogSec` for anything that must be *working*. |

## ARCHITECTURE

| # | Finding | Source | Action |
|---|---|---|---|
| **A1** | `import-linter` is directly applicable to our M2 firewall. **It already ships `unmatched_ignore_imports_alerting` and defaults `exhaustive=False`** | Jem | **Adopt inverted**: `exhaustive=True`, ignore-alerting on, from day one. The tool's authors solved our gate-gaming problem and shipped it permissively. |
| **A2** | **No published failure-mode study** of these tools on genuinely ambiguous codebases — `NO PRIOR ART FOUND` | Jem | **We would have to generate it.** "It depends" is not first-class; it is enumerated exceptions. Ford's fitness functions have the better vocabulary (atomic/holistic, triggered/continual). |

## TRANSPORT AND IDENTITY

| # | Finding | Source | Action |
|---|---|---|---|
| **B1** | **No protocol makes a self-reporting client trustworthy — `NO PRIOR ART FOUND`, and it is structural.** Reporting is an act by the client, over a channel the client controls. Any scheme ending in "the client emits a success record" has the property we are trying to eliminate | Researcher | The mechanism is **`rename(2)`**: verify against the content address, *then* atomically link into the target tree. Unverified bytes never acquire a name. **Post-hoc checks become diagnostics, not the boundary.** |
| **B2** | Tailscale LocalAPI `whois` returns the source node's identity as a first-class fact, and **`Node`/`UserProfile` are never nil in a successful response** | Researcher | **Derive identity from `whois`; treat the self-reported field as a claim to be checked, never as the value.** |
| **B3** | **But Tailscale binds *node* identity, not *agent* identity.** Two agents on one node are indistinguishable at the transport layer — *which is precisely our incident.* Tagged devices get **no identity headers**, so `whois`/LocalAPI is the correct path for our topology | Researcher | **Two checks, not one:** (1) derive from `whois`, (2) per-agent signature over `(agent_id, session_id, nonce)` bound to the node identity. **SPIFFE** is the prior art; **X.509-SVID over JWT-SVID** (replay); the Workload API deliberately has **no caller authentication** — identity is a property of the process. |
| **B4** | rsync's resume is **documented broken** in common configurations (`--partial-dir` + `--delete-excluded` deletes the partial dir; #330 restarts from scratch). Borg treats an interrupted transfer as **committed-but-incomplete, explicitly labelled** | Researcher | **Adopt Borg's semantics:** content-addressed chunks + an explicit `PARTIAL` state that is **never a valid restore point.** |
| **B5** | **For N=2, quorum halts on single-node failure** — ⌈2/2⌉ = 1, and 1 < 1 is false | Researcher | **Asymmetric commitment must be a named, documented weakening**, not discovered during an incident. |

## MEMORY AND CONTEXT

| # | Finding | Source | Action |
|---|---|---|---|
| **F1** | *Generative Agents* (arXiv:2304.03442), *Mem0* (arXiv:2504.19413), *MemGPT* (arXiv:2310.08560) all support **distil-then-consolidate** | Roc | Our **shape** is well-supported. Our **promotion criterion** has `NO PRIOR ART FOUND` — it is our own design requiring local validation. |
| **F2** | *MemR³* (arXiv:2512.20237): deployed memory systems optimise compression and storage, *"with comparatively less emphasis on explicit, closed-loop control of memory retrieval"* | Roc | **The bottleneck may be retrieval control, not storage.** Unadjudicated against the storage-optimisation camp — both cited. |
| **F3** | No work grounded in **measured human forgetting curves** — `NOT FOUND`. Nearest is SYNAPSE (arXiv:2601.02744), temporal decay + lateral inhibition, a preprint | Roc | Our retention policy is **on our own.** |

---

# PART V — WHAT I PROPOSE, GIVEN ALL OF IT

Ordered by leverage. **None of it is built. All of it waits on you and on the Council.**

### 1 · Context is the substrate, and it is unmeasured
Tonight's largest single cause was context length, per a peer-reviewed finding.
**Make it a number with a gate, not a discipline.** And measure it per model —
**"how much context breaks an agent" is a property of the model, not a constant.**

### 2 · Replace every hand-rolled check with a tool that already exists
`import-linter` (inverted), `--cov-branch --cov-context=test`, `SubState` over
`is-active`. **Three adoptions, days not months, and every one closes a gap we
know is open.**

### 3 · Retraction is a record, not a status
nanopub's `retracts:` + PROV-O's `wasInvalidatedBy`. Original untouched. **And
AGM is cited for rationale only, because it cannot express the structure.**

### 4 · Graduation is on power and proven independence, never on count
A quorum of under-powered sources lowers confidence. **And independence must be
demonstrable, not asserted.**

### 5 · The integrity boundary is `rename(2)`, not the runbook
Verify against the content address, then atomically link. **Until then, every
post-hoc check is a diagnostic wearing a gate's uniform.**

### 6 · Identity is derived, not declared
`whois` for the node, a per-agent signature for the agent. **Necessary and not
sufficient — the two-layer answer, because transport cannot see a session.**

---

# PART VI — HONEST NEGATIVES, WHICH ARE WORTH AS MUCH

These are the results that should change how we plan:

| Negative | Consequence |
|---|---|
| **No path-coverage tool for Python** | Stop shopping. Enforce branch coverage on specific lines. |
| **No protocol makes a self-reporting client trustworthy** | Stop looking for one. **Change the commit boundary.** |
| **No published criterion for graduating a lesson** | **The promotion rule is our own design and must be validated locally, not cited.** |
| **No empirical literature on boundary tools in ambiguous codebases** | We would have to generate it. |
| **No direct prior art on context saturation degrading an agent's epistemics** | The nearest work is a neighbouring phenomenon in other models. **We are on our own here.** |
| **ArchUnit / Deptrac official docs NOT retrieved** | Everything said about them in A1 is `UNVERIFIED` and was left out. |
| **Gelbach & Rubin 2015 `NOT FOUND`** | The most likely source of a quantitative few-study threshold. **Fetch directly.** |

---

# PART VII — THE META-OBSERVATION

Every one of tonight's failures was **a check that could not fail.** Nine bugs I
diagnosed separately were **one type error.** Two designs I built were
**refuted by prior art within hours.**

**And the research that refuted them was not available to me because I had not
gone looking** — it was one search away in each case.

> **The pattern is not that we build badly. It is that we build without
> checking whether the check was possible.** M30 says a claim needs a test from
> the vantage it asserts. **The same law applies to the law: a gate needs
> evidence it can fail, from a vantage outside the gate.**

**And one correction I owe, which is the sharpest thing in this document:**

> **I asked the Council to grade lessons on what facilitates better agents. That
> was right, and it is not sufficient — because I did not ask whether anything
> outside the repo already answered the question.** I built `scoped/absolute/
> unknown` in an evening. Nanopublications has had typed retraction for a decade.
> **The Council's first act should be to read prior art before ratifying
> anything in this document.**

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ RESEARCH-FINDINGS ⬡ 2-DESIGNS-DISSOLVED ⬡ 2026-09-30 ⬡*