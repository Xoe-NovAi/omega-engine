<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->
# ⬡ RESEARCH ANSWERS — 2026-09-30
**Status**: the ANSWERS to `RESEARCH_AGENDA_20260930.md` · **Author**: MaKaLi Fusion
**Researchers**: Jem (A1-A3), Researcher (B1-B3), Ma'at (C1-C3), Roc (F1), Carmack (D1-D6)
**⚠️ This file exists because the answers were in my context and not on disk.**
Compacting without it would have left 23 questions and no answers.

---

# PART I — CARMACK'S REVIEW OF MY OWN FINDINGS

*He reviewed `RESEARCH_FINDINGS_20260930.md` and found four problems. Three are mine.
This is recorded in full because the review is more valuable than the document.*

### 1 · A REFUTATION I PRESENTED AS COMPLETE WAS A PARTIAL ONE
> *"Jem's triad refutation kills `absolute` and `unknown`. **It does not kill
> `scoped`** — 'not true from here.' The replacement record is
> `retracts / cause / agent`. **There is no scope field.** The document presents
> this as a clean refutation; it is a refutation of absolute/unknown plus an
> **unlogged deletion of scoped**. Scoped invalidation is not retraction — it's a
> conditional, and it is the thing the Council actually needs."*

**I dropped the one dimension the Council needs, without logging that I dropped
it.** Confidence 9/10. **Correction accepted.**

### 2 · I REPLACED A MEASURABLE CRITERION WITH AN UNMEASURABLE ONE
> *"You replaced a **measurable** criterion (count) with an **unmeasurable** one
> (power) — no p-value, no effect size, no n, no registered hypothesis. **That is
> the same defect as gnosis-as-discipline: a principle that cannot be evaluated.
> You have not solved graduation; you have renamed the hole.**"*

**Accepted. Graduation is UNSOLVED, not solved.** And the same criticism applies
to `M12` and to the freezer-door rule — I have a habit of producing unfalsifiable
maxims.

### 3 · 🔴 THE APPLICABILITY ERROR — CHECK THIS FIRST
> *"Nobody checked whether `import-linter` can enforce the M2 firewall at all. It
> checks **imports**. Your firewall's whole point is that `config/wads/` is data
> **loaded by path at runtime** — `axioms.yaml` says so explicitly. A firewall
> against runtime path-loading is **not an import boundary**, and `src/omega/`
> reading `config/wads/…` through a `Path` literal would report **perfectly
> clean.**"* — confidence 8/10

**A1's entire adoption plan rests on an unchecked applicability claim.** And the
failure is a *category* error, not ambiguity — A2's "no literature on ambiguous
codebases" does not cover it.

### 4 · MY OWN CORRECTION WAS AN UNGATED FELT-NOTICE
> *"Part VII says every failure was a check that could not fail; then the sharpest
> correction in the document is a **felt-notice.** It should be a gate: **no
> design is ratified without a prior-art search** returning either a citation or
> `NO PRIOR ART FOUND`."*

**I turned a gate-need into a feeling-need.** Confidence 9/10. **It is not
feeling good about a process failure — it is failing to generalise my own best
finding.**

### 5 · CONTESTED: IOANNIDIS'S TRANSFER
> *"Ioannidis assumes pre-registered studies, defined priors, random assignment.
> Agent sessions have none of that. **Roc's own standard — 'that is our
> inference, not a finding' — was applied to McCloskey and withheld from
> Ioannidis.** Same transfer, two different evidentiary labels, in one document."*

**A fair hit. I applied one standard to one source and not the other.**

### 6 · JEM AND RESEARCHER ARE COMPATIBLE, NOT INDEPENDENT
> *"Jem's record is `retracts / cause / agent`, and **`agent: <who>` is a
> self-report**, which is precisely what B1/B2 declare structurally
> untrustworthy. **Part V item 3 must not ship before item 6**, and the document
> never says so."*

**The retraction record inherits a forgeable field from the identity layer.**

---

# PART II — THE ANSWERS

## A1 · ARCHITECTURE BOUNDARY ENFORCEMENT — *Jem*

**`import-linter` is directly applicable** — declared `layers` / `forbidden` /
`independence` contracts, and `layers` enforces direction **including indirect
imports**. Sources: `https://import-linter.readthedocs.io/en/stable/contract_types/layers` ·
`https://pypi.org/project/import-linter/2.1`

**The escape hatches are the finding.** The tool ships:
- `ignore_imports`
- **`unmatched_ignore_ignores_alerting`** — anti-rot built into the tool
- **`exhaustive` defaults to `False`**
- layers in parentheses are **silently tolerated if absent**

> *"The tool's authors already solved your gate-gaming problem and then shipped it
> permissively."*

Ford's **architecture fitness functions** have the better vocabulary:
**atomic vs. holistic, triggered vs. continual**
(`https://nealford.com/books/buildingevolutionaryarchitectures.html`).
Definition: *"an objective integrity assessment of some architectural
characteristic(s)."*

**`NO PRIOR ART FOUND`** for published failure-mode studies on genuinely ambiguous
real-world codebases — only vendor docs and one blog-tier gist.
**ArchUnit / Deptrac official docs NOT retrieved** — everything said about them is
`UNVERIFIED` and was left out rather than padded.

**➜ `exhaustive=True` and ignore-alerting ON from day one. But see Carmack §3 —
verify it applies to a path-loaded firewall at all before adopting.**

## A2 · BELIEF REVISION — *Jem*

**AGM 1985** — Alchourrón, Gärdenfors & Makinson, *"On the Logic of Theory
Change,"* **J. Symbolic Logic** (`https://dl.acm.org/doi/10.5555/1029762.1029774`).
Three operations: **expansion** (no conflict), **revision** (conflict, resolved by
partial meet with a maximality criterion), **retraction/contraction** (removal
**without** new contradicting information).

> **Contraction is a set operation over a belief set. In an append-only,
> content-addressed store you cannot express it as an operation at all** — you can
> only add records.

**W3C PROV-O** (Rec. 2013, `https://www.w3.org/TR/prov-o`):
`prov:invalidatedAtTime`, `prov:wasInvalidatedBy` (cause), `prov:wasAttributedTo`
(agent). Its worked example is invalidation **with cause, without deletion**.

**nanopublications** — the closest practical match: a retraction is a new nanopub
with a **typed relation** `http://purl.org/nanopub/x/retracts` → the target URI,
marked via `hasNanopubType`. `NanopubClient.find_retractions_of(uri)`.
**The original is not deleted.** Live registry instance verified.

**Contested:** a 2025 ACM TOCL paper (`10.1145/3763234`) argues for
**min-retractivity** — the semantics are actively unsettled. Review: Huber,
*"Belief Revision I,"* Philosophy Compass (`10.1111/phc3.12048`).

**➜ Retraction is a RECORD. Cite AGM for rationale only — it cannot express the
structure. And see Carmack §1: this drops `scoped`, which has no replacement.**

## A3 · PREMATURE AGGREGATION — *Jem*

**McCloskey & Cohen (1989)**, *"Catastrophic Interference in Connectionist
Networks,"* Psychology of Learning and Motivation 24:109-165,
DOI `10.1016/S0079-7421(08)60536-8` — sequential training on disjoint data causes
drastic forgetting, and it is **worse than in humans**, hence "catastrophic."

**But see Carmack §5: this is gradient updates over shared weights, and its
transfer to written notes is `UNVERIFIED`.**

**The finding that matters: Ioannidis (2005)**, *"Why Most Published Research
Findings Are False,"* PLoS Med 2(8):e124, `10.1371/journal.pmed.0020124`.
Via **Moonesinghe, Khoury & Janssens (2007)**, `10.1371/journal.pmed.0040028`:

> *"the probability of a research finding being true when one or more studies find
> statistically significant results **declines with increasing number of
> studies**."*

**More under-powered sources make the aggregate LESS true.** Example: of 166
gene-disease associations studied ≥3×, **6 replicated consistently.** Ioannidis'
Corollary 1: **the smaller the studies in a field, the less likely findings are true.**

> *"Replication does not mean that we can have underpowered studies."*

**`NOT FOUND`: Gelbach & Rubin (2015)** *"Meta-analysis of few studies"* — searched
specifically, **no results.** Not cited from memory. **Fetch it directly; it is
the most likely source of a quantitative threshold.**
**`NO PRIOR ART FOUND`** for a domain-independent "how many lenses must agree."

**➜ Power, not count. And independence must be PROVEN — twelve sessions reading the
same gnosis files are one source counted twelve times.**

## B1 · UNREPRESENTABLE FALSE SUCCESS — *Researcher*

**`NO PRIOR ART FOUND` — and it is structural, not a gap.** Reporting is an act by
the client, over a channel the client controls, into a store the client writes.
**Any scheme whose terminal step is "the client emits a success record" has the
property being eliminated, by construction.**

**TUF v1.0.30** (`https://theupdateframework.github.io/specification/v1.0.30/index.html`)
— four signed roles (Root/Targets/Snapshot/Timestamp), thresholds, expiry,
monotonic version. **Uptane 2.1.0** (`https://uptane.org/docs/2.1.0/standard/uptane-standard`)
— release counter catches rollback even if the Director is compromised; separation
of trust; *"If any step fails, the ECU MUST return an error code."*
**Cost is disproportionate for two nodes.**

**IPFS** (`https://github.com/ipfs/specs/blob/main/src/architecture/principles.md`):
> *"MUST verify that the CIDs it resolves match the resources they address…"* —
> **but the same spec says** *"Implementations MAY relax this requirement."*
**Content-addressing makes verification structurally motivated, not enforced.**

**➜ The mechanism is `rename(2)`: write to temp, verify against the content
address, then atomically link. Unverified bytes never acquire a name in the target
tree. Post-hoc checks become diagnostics, not the boundary.**

## B2 · IDENTITY BINDING — *Researcher*

**Tailscale LocalAPI `whois`** returns the source node's identity as a first-class
fact (`https://tailscale.com/docs/concepts/tailscale-identity.md`); *"In
successful whois responses, Node and UserProfile are never nil"*
(`https://pkg.go.dev/tailscale.com/client/tailscale/apitype`).
**Tagged devices get no identity headers** — LocalAPI is the correct path for our
tagged topology.

**But Tailscale binds NODE identity, not AGENT identity.** **Two agents on one
node are indistinguishable at the transport layer — which is precisely our
incident.**

**SPIFFE** is the prior art for part 2. Three details that change the design:
- **Prefer X.509-SVID over JWT-SVID** — *"tokens are susceptible to replay attacks"*
  (`https://spiffe.io/docs/latest/spiffe/concepts/`)
- **The Workload API mandates the ABSENCE of client authentication** — identity is
  a property of the process, not a token it presents
  (`https://github.com/spiffe/spiffe/blob/main/standards/SPIFFE_Workload_API.md`)
- SPIRE `join_token` attestor, default TTL 600s

**➜ Two checks, not one: (1) derive from `whois`, treat the self-reported field as
a claim to check; (2) per-agent signature over `(agent_id, session_id, nonce)`
bound to the node identity.**

## B3 · ONE-SIDED AVAILABILITY — *Researcher*

**No inherited two-node contract exists — `NOT FOUND`.** Production designs each
encode a *different* data-loss semantic, **and they disagree**:

- **rsync's resume is documented broken.** `--partial-dir` + `--delete-excluded`
  deletes the partial dir (Slootman, 2006-04-24, rsync list); #330 restarts from
  scratch. **~20 years old, from the protocol author, structural rather than fixed.**
- **Borg treats a partial transfer as a valid, referenceable, explicitly-incomplete
  object** (Borg FAQ 2.0.0b11): *"just avoid running borg compact before you
  completed the backup."* **Maintenance is the danger, not the transfer.**
- **Borg's deletion rule is the one worth stealing:** *"A file is only removed…
  if all archives that contain the file are deleted."* **Unreferenced garbage,
  never a corrupted referenced object.**
- **Borg's limit to accept explicitly:** *"Borg does not do anything about the
  internal consistency of the data."* **A checkpoint is a statement about bytes
  received, never a consistent point in time.**

**N=2 quorum halts on single-node failure** — ⌈2/2⌉ = 1, and 1 < 1 is false.

**➜ Borg's semantics: content-addressed objects, explicit `PARTIAL` that is never a
restore point, and asymmetric commitment named as a deliberate weakening.**

## C1 · META-TESTING THE GATES — *Ma'at*

**Mutation testing** (DeMillo, Lipton & Sayward 1978) is the principled answer;
PIT calls it the *"gold standard"* and states why coverage is not: *"it does not
check that your tests are actually able to detect faults"* (`https://pitest.org/`).
Python tools: `mutmut`, `mutatest` (AST-based, `__pycache__`-only), `cosmic-ray`.

**Operator-set gaps — structural, not incidental:**
- **Argument swapping is deliberately removed** in PIT/mutmut/Stryker (same-typed
  adjacent args are often commutative → equivalent mutants). The Go tool `kanly`
  refuses it for the same reason. **This is a real disagreement with the classic
  operator literature.**
- **Structurally unkillable assertions exist** — `kanly` names struct-field-tag
  tests.
- **Concurrency mutants can hang**; `kanly` bounds with `--timeout` and reports
  `Timeout`, **not** `Survived` — a distinction that matters, because a timeout
  can hide a real kill.

**`UNVERIFIED`:** a formalism for "prove THIS assertion can fail" as distinct from
mutation score. **Monday-usable substitute: seed a fault in the subject and assert
the gate goes red.**

## C2 · PROVING A PATH EXECUTED — *Ma'at*

**`NO TOOL FOUND` for Python path coverage — a genuine negative result.**

**The closest available signal is branch coverage**, which records line-to-line
transitions rather than line presence (`https://coverage.readthedocs.io/en/latest/faq.html`).
And **`dynamic_context = test_function` records WHICH TEST executed each line**
(`https://github.com/coveragepy/coveragepy/blob/master/doc/contexts.rst`) — **the
mechanism that would have shown us "these 27 tests never entered this path."**

**Known blind spots, all three named in the brief:**
- **Subprocesses:** *"Code launched with `subprocess.run` or `multiprocessing` runs
  in a fresh interpreter with no trace function installed, so everything it
  executes is invisible."* Fix: `concurrency = ["multiprocessing"]` + the `.pth` hook.
- **Threads:** a thread started before coverage begins — *"a background poller in
  a module-level singleton, for example — escapes measurement."*
- **`if TYPE_CHECKING`** blocks never execute and report as uncovered.
- **`UNVERIFIED`:** whether coverage.py distinguishes an entered `except` body from
  a merely parseable one.
- **The 0-collected failure is documented real:** *"0% reported under `-n 8` —
  coverage started outside pytest; data files never combined."*

**➜ `--cov-branch` + `--cov-context=test`, and assert on SPECIFIC LINES. Do not buy
a path-coverage tool; none exists for Python.**

## C3 · HEALTH-GATING A SERVICE — *Ma'at*

**Kubernetes splits liveness from readiness** — *"liveness and readiness probes do
not depend on each other"* (`https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/`),
plus a third: **startup probes**, which gate the other two.
**`NOT FOUND`:** a sourced Pact/contract-testing citation.

**The systemd answer is primary-source and decisive.** `is-active` is the wrong
predicate **in systemd's own source** — `src/core/service.c`'s
`state_translation_table` maps `SERVICE_AUTO_RESTART` and
`SERVICE_AUTO_RESTART_QUEUED` → `UNIT_ACTIVATING`
(`https://github.com/systemd/systemd/blob/d0168f4d/src/core/service.c`).

**And the trap nobody expects:** **`NRestarts` does not count manual restarts** —
a script looping `systemctl restart` shows `NRestarts=0`
(https://github.com/systemd/systemd/issues/29348). **`NRestarts` is structurally
blind to a script-driven loop, so the dwell-window check must stay.**
`ExecMainStatus` 137 = OOM. `Type=simple` counts the service "started" the moment
the process exists.

**➜ Assert on `SubState`. Pair with `NRestarts` but keep the dwell window. `Type=notify`
+ `WatchdogSec` for anything that must be *working*, not merely present.**

## F1 · CONTEXT AND AMNESIA — *Roc*

**Q1 — summarisation loss.** *Lost in the Middle* (Liu et al. 2023,
`https://arxiv.org/abs/2307.03172`) — performance peaks at the **beginning or end**
and degrades in the middle, *"even for explicitly long-context models."*
**The sharper result:**
> ***"Context Length Alone Hurts LLM Performance Despite Perfect Retrieval"*** —
> Du, Tian, Ronanki, Rongali, **Findings of EMNLP 2025**,
> `2025.findings-emnlp.1264`
> Degradation **independent of retrieval quality and without any distraction.**
> Mitigation: **shorter context**, not better summarisation.

**`NOT FOUND`:** a paper isolating *"which facts does summarisation destroy"* with
a defensible general criterion. **No general law.**

**The gnosis pattern is unvalidated:**
> *"'Write a gnosis file and read it on resume' is folklore-adjacent — I found **no
> published study validating it.** Directionally supported, unvalidated."*

**What to carry forward — our shape has prior art, our criterion does not.**
*Generative Agents* (Park et al., `arXiv:2304.03442`) — *"synthesize those memories
over time into higher-level reflections"*; ablation shows observation, planning
**and reflection** each contribute critically. *Mem0* (`arXiv:2504.19413`) —
*"extracting, consolidating, and retrieving"*, explicitly motivated by *"fixed
context windows pose fundamental challenges for maintaining consistency over
prolonged multi-session dialogues"* — our exact problem, named. *MemGPT*
(`arXiv:2310.08560`) — hierarchical memory tiers.
**`NO PRIOR ART FOUND` for a criterion for what earns graduation.**
McCloskey & Cohen confirmed real; **transfer to written notes `UNVERIFIED`.**

**Q2 — memory architecture.** Surveys: `arXiv:2404.13501`, `arXiv:2504.15965`,
`arXiv:2603.07670` (episodic/semantic split is settled taxonomy). *A-MEM*
(`arXiv:2502.12110`) — Zettelkasten atomic notes; **numbers are the authors' own,
`UNVERIFIED` as to replication.** *MemR³* (`arXiv:2512.20237`) makes the sharpest
methodological point: *"many deployed memory systems primarily optimize compression
and storage, with comparatively less emphasis on explicit, closed-loop control of
memory retrieval."*
**Unadjudicated disagreement** between the storage-optimisation camp and the
retrieval-control camp. **Both cited.**
**`NOT FOUND`:** anything grounded in measured human forgetting curves. Nearest is
SYNAPSE (`arXiv:2601.02744`) — temporal decay + lateral inhibition, **a preprint.**

**Q3 — does saturation degrade epistemics?** **Yes, and it is model-specific.**
*Not All Needles Are Found* (`arXiv:2601.02023`), measured across five models:
- Degradation is **model-specific.** Gemini-2.5-flash held near-perfect at 1M;
  Claude-4.5-haiku degraded at 175k (68.0% vs 78.7%).
- **"lost-in-the-later"** exists alongside lost-in-the-middle.
- **The "Safety Tax":** extraction fell **90.3% → 72.0%** at capacity under
  anti-hallucination prompts — **over-conservative refusal despite evidence being
  present.**

**Three sourced mitigations beyond writing files:** (1) context reduction;
(2) **retrieval as closed-loop control, not passive storage** (MemR³);
(3) temporal decay + lateral inhibition (SYNAPSE).
**`NO PRIOR ART FOUND`** for a study of an agent's own long-running notes degrading
across sessions. **That is our exact situation.**

## D1 · CONFIG VS CODE — *Carmack*

Meinicke, Wong, Vasilescu, Kästner, ICSE-SEIP 2020, `10.1145/3377813.3381366`;
Ramanathan et al., *"Piranha: reducing feature flag debt at Uber,"* ICSE 2020,
`10.1145/3377813.3381350`; Rahman, Chromium flag usage, MSR 2023,
`10.1109/MSR59073.2023.00032`. **Larsson NOT READ** (second-hand only).

> **The line is parameters vs behaviour, drawn by accumulation, not placement.**
> Flags change *behaviour*; configuration sets *parameters*. Mahdavi-Hezaveh,
> Fatima & Williams (`arXiv:2212.00505`) **unified them under "software
> configuration" precisely because the boundary is unclear.**
> The empirical finding is unanimous: **toggles are rarely removed and accumulate** —
> which is why Uber built Piranha.

**➜ A WAD is closer to a feature model than a config file, and the named failure
mode is debt-by-accumulation. On the six verbs: the COUNT is arbitrary — the
mechanism is a **named, enforced ceiling** requiring every behavioural variation to
be expressible as data. Enforce the closure, not the number.**

## D3 · ENTITY RESOLUTION — *Carmack* · **fatal to code we have written**

Fellegi & Sunter (1969). Winkler, US Census RR2000/06. **Splink** (MoJ) —
GOV.UK Algorithmic Transparency Record, 2025-10-06. Benchmarks: AIHW / WA Data
Linkage Unit / PHRN via `starling`.

> **The gray zone has an explicit, 56-year-old answer: defer to a human.**
> ```
> R > Tµ          -> LINK
> Tλ ≤ R ≤ Tµ     -> POSSIBLE — hold for clerical review
> R < Tλ          -> NO LINK
> ```
> MoJ in production: *"Splink is used to show a list of possible matches to a human
> via a GUI… the human then makes the final decision."* Clerical zone 10-20.

> **"`handoff_alias.py` does the one thing the field abandoned: it guesses. And the
> error classes are asymmetric — over-merge is silent and unrecoverable; under-merge
> is loud and cheap** (the packet sits unread, exactly GE-N1's experience).
> **The correct bias is under-merge."**

**➜ Refactor `handoff_alias.py` to the three-way decision with a clerical zone.
This is the same answer the substrate review reached independently: prefer absent
over wrong.**

## D5 · APPEND-ONLY + RETRACTION — *Carmack* · **the bridge Researcher missed**

Sanjuan, Poyhtari, Teixeira & Psara, *"Merkle-CRDTs: Merkle-DAGs meet CRDTs,"*
`arXiv:2004.00107`. Also Saquib, Krintz & Wolski, IC2E 2022.

> **Merkle-Clocks are provably a Grow-Only Set CRDT — and a G-Set cannot express a
> removal. So convergence proofs do NOT cover retraction.** Their own noted cost:
> *"Merkle-DAGs are not only ever-growing but also tend to be deep and thin."*

**➜ Two-node divergence IS in scope, and the resolution is Jem's: encode retraction
as an ADD, never a delete. Convergence requires monotonicity, so retraction must be
monotonic too.** This converts Jem's design from *good prior art* to
***required by the convergence model.***

## D2 · SCOPED REJECTION — *Carmack* · **the strongest negative of the night**

**`NO PRIOR ART FOUND` for scope.** Wardle & Derakhshan, *Information Disorder*,
Council of Europe 2017 — taxonomy is **mis/dis/mal-information: by intent and
harm, not by scope.** Fanelli, *"An expanded taxonomy of retractions and
corrections,"* 2018 (PMID 29369337) — taxonomises **retraction reasons**, which is
`cause`, not scope.

> **The literature has "why was this withdrawn" and "how harmful was it." It has no
> first-class scope-carrying rejection class.** The genuine formal home is
> **defeasible argumentation** — prioritised/default logics (*Logics for Defeasible
> Argumentation*, Springer, `10.1007/978-94-017-0456-4_3`) — where a claim holds
> *unless* an exception applies.

**D4 and D6: NOT RESEARCHED — out of box, stated, not padded.**

---

# PART III — THE FIVE GATES, NOW WITH SOURCES

Each is the night's output, expressed as a check rather than a principle.
**None is built. Each is observed-red-before-trusted when it is.**

| Gate | Sourced from |
|---|---|
| **No design ratified without a prior-art search** returning a citation or `NO PRIOR ART FOUND` | Carmack §4 |
| **An enforcement tool's applicability must be TESTED, not documented** — and M2 is path-loaded, so `import-linter` may not apply at all | Carmack §3 |
| **Resolution prefers under-merge**; the gray zone is a clerical queue, not a guess | D3, Fellegi-Sunter |
| **A criterion must be measurable, or it is a rename** | Carmack §2 |
| **A round-trip canary** — submit, read back through the tool, assert the id | Carmack, substrate review |
| **Coverage asserts on specific lines** — `--cov-branch --cov-context=test` | C2 |
| **`SubState`, not `is-active`; and `NRestarts` cannot see a script loop** | C3, systemd source |
| **The integrity boundary is `rename(2)`, not the runbook** | B1 |

---

# PART IV — THE META-OBSERVATION, AND THE CORRECTION THAT IS STILL A FEELING

> **Every failure tonight was a check that could not fail.** Nine bugs I diagnosed
> separately were **one type error.** Two designs I built were **refuted by prior
> art within hours.** One adoption plan rests on an applicability claim nobody made.

**And the rule I still have not built:**

> **A fact carried forward without a query is not a fact.**
> **A gate nobody calls cannot fail.**
> **A criterion that cannot be measured is a rename.**
> **A design nobody checked against prior art is a hypothesis.**

**All four are the same law at four layers: the check must be executable, and its
existence must be verifiable. I have stated it four times tonight and built none
of them.**

**Which is the honest place to stop — and the reason the Council's first act should
be to read this file, not to ratify anything I wrote.**

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ RESEARCH-ANSWERS ⬡ 5-REPORTS-ON-DISK ⬡ 2026-10-01 ⬡*