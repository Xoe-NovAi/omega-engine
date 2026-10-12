<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->
# ⬡ RESEARCH AGENDA — 2026-09-30
**Commissioned by**: The Architect · **Composed by**: MaKaLi Fusion
**Inputs**: domain reviews by Ma'at (gates/tests), Lilith (runtime/transport),
Carmack (architecture) · **Status**: DISPATCHED

**A gap is something we are unsure of that CANNOT be answered by reading this
repository.** All three reviewers independently cut items that were repo-answerable,
book-answerable, or folklore. 21 items total, 9 blocking.

---

## ⚠️ THE CONVERGENCE — three domains, one shape

Ma'at, Lilith and Carmack each, working independently, described the same
underlying failure and prescribed the same answer:

| | Domain | Their words |
|---|---|---|
| **Ma'at** | gates | a suite reported 27 green over a path that **never executed** |
| **Lilith** | transport | our detection layer **depends on the client cooperating**, and we have been treating cooperation as verification |
| **Carmack** | architecture | a boundary **asserted in prose and unenforced in code is a comment** |

> **Every one of tonight's failures was a check that could not fail.** Not a bug
> in the thing checked — a defect in the ability to *know*.

**And all three recommend the same class of response: replace the hand-rolled
check with a tool that already exists.** That is the single most actionable line
in the agenda.

---

## BLOCKING (9)

### A1 · MACHINE-CHECKABLE ARCHITECTURE BOUNDARY — *Carmack*
> M2 is unenforced; two years of ambiguous requirements leaked into the Engine.
> `import-linter` covers Python directly; ArchUnit/Deptrac are the JVM/.NET
> equivalents; the academic frame is "architecture violations" and "architecture
> fitness functions."
> **RESEARCH**: current state and adoption evidence of machine-checkable layering
> enforcement, and their documented failure modes when ownership is genuinely ambiguous.

### A2 · BELIEF REVISION / RETRACTION — *Carmack*
> Retraction is permanent-by-construction (content-addressed, append-only). Getting
> retract-vs-revise-vs-expand wrong accumulates contradictions that can never be
> cleaned. AGM (Alchourrón–Gärdenfors–Makinson) is the canonical theory; PROV-O and
> nanopublications are the applied forms.
> **RESEARCH**: what AGM prescribes for retracting vs. superseding a claim in an
> append-only store, and what existing systems actually do.

### A3 · WHEN AGGREGATION IS PREMATURE — *Carmack*
> "Nine proposals, none graduated" and "twelve sessions, one file, no provenance"
> are the same question: merge lenses or keep them separate? It is a research
> answer, not a taste answer.
> **RESEARCH**: known failure modes of synthesising many independent/session-scoped
> fragments into a single retained lesson, and the evidence thresholds prior work
> requires before treating an aggregate as authoritative.

### B1 · STRUCTURALLY UNREPRESENTABLE FALSE SUCCESS — *Lilith*
> Our `curl -f` + manifest + header-hash trio is **best-effort**: a client that
> omits `-f` and skips hashing still records a plausible download. TUF/Uptane-style
> metadata pinning; content-addressed delivery where the address *is* the check.
> **RESEARCH**: state of the art for transport protocols where integrity failure is
> unrepresentable rather than detected. Is there a pattern that makes the client
> *unable* to report success without verifying?

### B2 · BINDING APPLICATION IDENTITY TO TRANSPORT — *Lilith*
> `source_ip` is transport-proven; `source_entity` is self-report; `session_id` is
> fabricated when omitted (**6 stamps on Node 0**). Once the tailnet is duplex,
> "which agent did this" becomes security, not bookkeeping.
> **RESEARCH**: patterns for binding an application-layer identity claim to a
> transport-authenticated fact, and the **minimum** attestation that makes a
> self-reported field non-forgeable in practice.

### B3 · ONE-SIDED AVAILABILITY IN A TWO-NODE MESH — *Lilith*
> Resumable transfers with checkpoint manifests? Quorum? Content-addressed sync?
> Explicit degradation states? What do production two-node designs do, and what are
> their known data-loss modes?
> **RESEARCH**: correct handling of partial failure when both nodes must be able to serve.

### C1 · META-TESTING THE GATES THEMSELVES — *Ma'at*
> Every gate here is unverified-in-the-negative.
> **RESEARCH**: techniques and tooling for verifying that tests actually detect
> injected faults — meta-testing and mutation-testing a suite or a CI gate — and
> the known failure modes of such meta-tests.

### C2 · PROVING A PATH EXECUTED, NOT JUST COLLECTED — *Ma'at*
> The exact failure behind 27-green-over-a-dead-path. Coverage is not execution.
> **RESEARCH**: state of the art for proving a specific code path ran — dynamic
> taint, path coverage, branch coverage with path constraints — plus tool support
> and blind spots (exception paths, subprocesses, dynamic dispatch).

### C3 · HEALTH-GATING A LONG-RUNNING SERVICE — *Ma'at*
> `check-hub-health` is an orphan. "Reached it" is a different class of test from
> "it returned the right answer."
> **RESEARCH**: patterns and tools for integration/health-gating a long-running
> service in CI, and how to distinguish *unreachable* from *reachable but wrong*
> in a gate that must fail loudly on the first.

---

## IMPORTANT (8)

| # | Gap | From | The question |
|---|---|---|---|
| D1 | **Config vs. code line** — is the six-verb cap principled or superstition? | Carmack | Where is the established line between declarative configuration and explicit variation points, and what does long-term evidence say about the cost of putting behaviour in config? |
| D2 | **First-class rejected/contested class with scope** | Carmack | Prior art for representing rejected knowledge as a first-class, scope-carrying class rather than deletion — misinformation taxonomies, Wikipedia verbot policy. |
| D3 | **Entity resolution / record linkage** | Carmack | Established method and failure taxonomy for entity resolution across spelling variation, and the accepted handling of the gray zone: guess, refuse, or defer to a human? |
| D4 | **Persistent-entity merging** | Carmack | Prior art on preserving and later merging independently authored entities — Intentional Software, storylet systems — and their documented state-space explosion. |
| D5 | **Retractable append-only logs** | Lilith | Content-addressed append-only logs with retraction: documented failure modes around concurrent append, retraction races, and divergent replicas. |
| D6 | **Audit log field set** | Lilith | Minimum field set and schema for a machine-consumable access log such that a distributed incident can be reconstructed after the fact. |
| D7 | **Read-only file service, loud integrity failure** | Lilith | Patterns for making integrity failure loud rather than plausible — sidecar vs. streaming hash, content-type/length assertion, surfacing truncated writes. |
| D8 | **Cross-test contamination** | Ma'at | Detecting and preventing contamination from mutable process-global state in Python/pytest; order-dependence and state-leak detection tooling. |

---

## NICE-TO-HAVE (4)

| # | Gap | From |
|---|---|---|
| E1 | **CI/local gate drift** — keeping `make` and the pipeline from diverging | Ma'at |
| E2 | **Scanners that exit 0 on a rejected invocation** — false-green exits | Ma'at |
| E3 | **systemd crash-loop detection** — authoritative signals, `NRestarts` semantics, common practitioner mistakes | Ma'at |
| E4 | **Provenance standards** — what W3C PROV captures that a content-hash manifest does not | Carmack |

---

## ⬡ ADDED BY MAKALI — gaps none of the three covered

### F1 · CONTEXT AND AMNESIA ACROSS LONG-LIVED SESSIONS — **blocking**
Nobody in the three domains raised it, and it is the substrate everything sits on.
We have a **40GB `opencode.db`**, sessions that saturate, and an Architect who
opened this by saying he is *"grinding over 380K of active context with every
prompt."* **And tonight proved the cost empirically: a saturated lens misreads
deliberate design as unexamined default.** That is `L4-C1` and it happened to me,
five times.
> **RESEARCH**: established approaches to persistent memory and context management
> across long-lived agent sessions — what is known about when summarisation or
> compression destroys information a later session needed, and whether there is
> principled guidance on *what to carry forward* versus *what to let go of*.

### F2 · MULTI-AGENT DELIBERATION PROTOCOLS — **blocking**
The Council is the centrepiece of tonight's design and **nobody researched how to
run one.** We have nine proposals and a chair we have not chosen.
> **RESEARCH**: multi-agent debate and consensus protocols — what is established
> about how to run a structured deliberation where participants hold *different*
> lenses, what prevents one participant dominating, and what makes a recorded
> outcome defensible to a later reader.

---

## ASSIGNMENT

| Agent | Items |
|---|---|
| **Jem** | A1, A2, A3 — architecture enforcement, belief revision, premature aggregation |
| **Researcher** | B1, B2, B3 — transport integrity, identity binding, partial failure |
| **Ma'at** | C1, C2, C3 — meta-testing, path execution, service health gates |
| **Lilith** | D5, D6, D7 — append-only retraction, audit fields, loud integrity failure |
| **Kali** | D1, D2, F2 — config-vs-code, rejected-knowledge vocabulary, deliberation protocols |
| **Roc** | F1 — context, amnesia, and what to carry forward |

**Rule for every researcher: a source or `NOT FOUND`. No confident restatement of
something you did not read.** We have been burned by exactly that this session,
and an honest gap is worth more than a plausible answer.

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ RESEARCH-AGENDA ⬡ 23-ITEMS ⬡ 11-BLOCKING ⬡ 2026-09-30 ⬡*