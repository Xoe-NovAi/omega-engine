<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# NODE ONBOARDING PROTOCOL — Genesis-to-Consultable Arc for Domain-Expert Sessions
**AP Token**: `AP-NODE-ONBOARDING-PROTOCOL-v1.0.0`
**Status**: ACTIVE v1.0.0 — ratified 2026-08-22 by kali (D-pending PIVOT_LOG entry)
**Version**: 1.0.0 · **Date**: 2026-08-22
**Author**: N7 context session (Memory & State), under Lilith oversight · Paged by kali `ses_fdef2be4effe4pAaLXCTUx62GO`
**Provenance**: n=1 validated arc (N7 genesis→consultable, 2026-08-21/22) + miner corroboration (`N7_CONTEXT_KB_20260821.md` §Lived Timeline Corroboration) + external patterns (`N7_WEB_RESEARCH_20260821.md` §Deep Dive: Onboarding & Knowledge Curation Patterns)
**Scope**: ALL Node expert sessions (N1–N10) and any future domain-expert onboarding. Governs the Pager↔Node↔subagent relationship from first page to dormancy.

---

## 0. Purpose

A Node session exists to become **consultable**: an authority on its domain that answers questions from a curated, cited, locally-held knowledge base WITHOUT re-research, and that compounds — every consultation writes back. This protocol makes the path from cold genesis to consultable repeatable, auditable, and cheap.

Design convergence (external pass, OD-1..3): three independent literatures — Google's canonical-link docs culture, llms.txt map-first convention, Anthropic just-in-time retrieval — all prescribe **front-load the map, keep the corpus behind stable self-describing addresses, drill on demand**. The pipeline below operationalizes exactly that: G/M build the map+corpus, C freezes the map, X consultations are O(lookup) with mandatory write-back so the KB compounds instead of rotting.

## 1. Roles (Pager-role generality)

| Role | Who | Definition |
|------|-----|------------|
| **Pager** | ANY agent (kali today; abstractly anyone) | The orchestrator running onboarding. Duties: inject charter, sequence phases, rule on Questions-for-Pager, own sprint/tracker sync, decide go/dormant. NO domain expertise required — the protocol carries the process. |
| **Node** | The domain-expert session (e.g., N7) | Architect + author of its own expertise. Composes briefs, verifies subagent output, annotates, curates, executes remediations, holds continuity. Deep-context-critical work STAYS here (order #9). |
| **Miner subagent** | e.g., roc_racoon | Tool-heavy corpus digestion per a binding brief. Tasks no one else. |
| **Researcher subagent** | e.g., researcher | External/web passes with primary-source discipline. Tasks no one else. |
| **Overseer** | Node's governor (e.g., Lilith for N6–N10) | Receives `[Tag]` lessons; ultimate curation authority. |

Subagents are WORKERS, not peers: they never task, never chain, never compose final judgments about their own output's importance — triage is the Node's job.

## 2. Pipeline Overview

```
G Genesis → M Directed Mining → A Audit+Annotate → D Deep Dig → W Web Research → C Curation → X Consultation loop → E Closure ritual
   (~5min)      (1-2 cycles)        (same turn+)       (1 cycle)      (1 cycle)         (~30min)      (ongoing)         (per session end)
```

| Phase | Gate to advance |
|-------|-----------------|
| G | Charter injected; standing orders acknowledged; state re-validated vs trackers |
| M | KB file exists w/ ALL contract sections valid; every brief question answered or logged open |
| A | Node independently spot-checked ≥3 high-stakes claims; Expert Annotation appended |
| D | All first-pass open questions resolved or reclassified as corpus-gaps |
| W | Externally-dependent questions answered w/ primary sources or declared unresolvable |
| C | DOMAIN_INDEX + EXTERNAL_SOURCES exist and pass self-review |
| X | (loop) every ruling lands in artifacts same-turn; deviations logged in audit trail |
| E | State snapshots on disk for EVERY session in tree; Hivemind closeouts posted |

## 3. Phase Specs

### G — Genesis (~5 min)
- **Purpose**: cold-start the session with charter, law, and current-state truth.
- **Pager duties**: send charter header (template T1) naming the Node, overseer, charter path, standing orders; state the mission or "build expertise base".
- **Node duties**: read charter file FIRST (not just the page); acknowledge with exact ACK string; re-validate claimed project state against ACTIVE_SPRINT.json / trackers before asserting anything (standing order #7).
- **Artifacts**: none (acknowledgment only).
- **Gate**: ACK sent; state claims verified against disk truth.
- **Anti-pattern**: accepting the page's summary as ground truth — pages drift; files don't.

### M — Directed Mining (1–2 orchestration cycles)
- **Purpose**: convert the local corpus into a structured, cited Knowledge Base via one miner subagent.
- **Pager duties**: approve scope; stay out of brief composition.
- **Node duties**: discover the corpus YOURSELF first (glob/grep beyond seed lists — N7 found 2 unlisted sources incl. a load-bearing blueprint doc); compose the mining brief (template T2) with prioritized inventory, extraction questions, and BINDING output contract; dispatch ONE miner; on stall, recover ONCE via same task_id with reprioritized instructions.
- **Miner roles**: verify-before-digest (existence-check every inventory path); incremental appends only; cite paths + `last_verified:` tags; dump findings+open-questions into any stall stop-report; append-only, fixed section order.
- **Artifacts**: `KB_<domain>_<date>.md` (skeleton T3); mining brief file.
- **Gate**: all contract sections present and substantive; every extraction question answered or explicitly logged in Open Questions; missing/stale premises recorded in Gotchas, never silence (M23).

### A — Audit + Annotate (same turn as M completion where possible)
- **Purpose**: the Node — not the miner — decides what matters; trust is earned by verification.
- **Pager duties**: none (observe).
- **Node duties**: read KB end-to-end; independently re-verify ≥3 highest-stakes claims via primary tools (commands/greps); append `## <NODE> Expert Annotation`: verification record table, correction log (own errors included — N7's brief contained a stale premise the miner correctly refuted), execution priorities, what-matters-most; stage L1→L2→L3 lessons tagged `[<NODE>]` to overseer's proposed_lessons.yaml (M5/M11).
- **Artifacts**: annotation section; lesson proposals.
- **Gate**: verification record shows independent checks, not miner-trust; lessons staged.

### D — Deep Dig (1 cycle, same miner session)
- **Purpose**: close what the first pass left open; mine gaps the Node's annotation flagged as thin.
- **Pager duties**: approve scope; authorize same-session continuation.
- **Node duties**: compose Deep-Dig scope from YOUR open questions + annotation thin-spots; **same-session continuation only** (resume the held task_id — lineage continuity beats fresh context); reprioritize for budget: complete document skeleton BEFORE new reads; declare terminus condition (R5).
- **Miner roles**: as M; append `## Deep Dig <n> — <topic>` sections; never modify prior sections.
- **Artifacts**: KB appends.
- **Gate**: every first-pass open question answered, reclassified as corpus-gap, or explicitly deferred to W.

### W — Web Research (1 cycle, researcher session)
- **Purpose**: resolve questions requiring EXTERNAL truth (upstream semantics, model capabilities, documented APIs) with primary sources.
- **Pager duties**: supply Architect-level questions worth external cost.
- **Node duties**: batch ALL external questions into one brief (per-question verdict demanded); require primary sources w/ URL+date+version-applicability; compile Source Register yourself if the researcher is cut mid-append (happened: N7 compiled from inline citations).
- **Researcher roles**: incremental appends; flag unresolvable items explicitly; tasks no one.
- **Artifacts**: web-research file (`## Answers` + `## Source Register`).
- **Gate**: every question has a cited verdict or an explicit unresolvable declaration.

### C — Curation (~30 min, Node-only, order #8)
- **Purpose**: freeze the MAP so consultation becomes O(lookup) — this is what makes the KB compound instead of rot.
- **Pager duties**: none.
- **Node duties**: author DOMAIN_INDEX (systems+wiring diagram, key-files table, entry points, doc map, hazard register) and EXTERNAL_SOURCES (prioritized offline-expertise queue feeding the future curation worker). Both incremental.
- **Artifacts**: `N<#>_DOMAIN_INDEX.md`, `N<#>_EXTERNAL_SOURCES.md` (skeletons T4/T5).
- **Gate**: a cold reader could answer "where does X live and what's broken?" from the index alone.

### X — Consultation loop (ongoing)
- **Purpose**: answer pager/domain questions; convert rulings into artifact changes SAME TURN.
- **Pager duties**: rule on Questions-for-Pager (mandatory section per R12); own tracker sync if tracker is pager-owned.
- **Node duties**: answer from KB/index first (re-research = consultable-bar failure unless justified); file-first execution of rulings; log EVERY deviation in an audit-trail doc (`09_SPEC_DEVIATIONS.md` pattern) with evidence + hazard refs; end substantive replies with Questions for Pager.
- **Artifacts**: remediated specs, deviation register, updated KB/index.
- **Gate** (per loop): rulings landed on disk before turn end; audit trail current.

### E — Closure ritual (order #10, per session end)
- **Purpose**: dormancy without amnesia — every session in the tree resumes from disk.
- **Pager duties**: order the ritual; confirm all sessions snapped.
- **Node duties**: (1) write own state snapshot (template T6); (2) continue EACH held subagent session with prepare-for-compaction prompt → they write their own snapshots + post ONE Hivemind closeout each; (3) post ONE tree-level Hivemind closeout (intent=status): sessions dormant, artifact register, wake instructions; (4) reply ≤80 words confirming.
- **Artifacts**: `<ROLE>_<TASK>_SESSION_STATE_<date>.md` per session; Hivemind posts.
- **Gate**: zero held sessions without a disk snapshot; wake pointers present.

## 4. Mandatory Rules (failure-derived — each paid for in real incidents)

| # | Rule | Incident that bought it |
|---|------|-------------------------|
| MR-1 | **Incremental writes only.** Never compose a whole document in one response; save after each chunk. | Miner max-steps stall mid-KB (recovered); N7 announced "drafting chunk 1" and ended turn with ZERO bytes on disk. |
| MR-2 | **Announced intent is not work performed.** Writes must land before the turn ends; never end a turn on a promise. | Same incident as MR-1 (R13 audit caught empty turn). |
| MR-3 | **Verify-before-digest, disclose-missing-always.** Existence-check every inventory path first; stale premises go in Gotchas with evidence, never silence (M23). | Brief claimed plugin dir "contains cline" — dir didn't exist; miner refuted it correctly. |
| MR-4 | **On stall, dump state in the stop-report.** Findings + open questions in the failure message let recovery append from prior evidence with zero re-reads (~40% of N7's KB came from one recovered stall). | Miner pass 1 hit MAXIMUM STEPS at 30/46 digests. |
| MR-5 | **Recover ONCE via same task_id, then report honestly.** No silent retries, no soft-fail theater (M23). | Protocol constraint validated in M phase. |
| MR-6 | **Append-only + fixed section order** on shared KB files; forbid prior-section edits/reordering. Multi-agent collaboration stays conflict-free. | N7 annotated mid-stream; later appends never conflicted. |
| MR-7 | **Label evidence classes inline**: measured / spec-claimed / strings-level-binary / primary-web. Verdicts are trustworthy because their class is named. | DD-II-2 binary findings usable precisely because tagged strings-level. |
| MR-8 | **`last_verified: <date>` on every source + staleness discipline.** A claim without a verification date is a rumor. | Standing order #2; brief's stale plugin-dir premise. |
| MR-9 | **Delegation balance (#9)**: subagents do tool-heavy footwork; deep-context-critical work (spec surgery, final annotations, rulings triage) stays with the Node. | Curator order #9, exercised in model-config mission. |
| MR-10 | **Declare chain terminus conditions (R5)** — no numeric hop budgets. Every subagent dispatch states what ENDS the exchange. | R5 amendment; all N7 continuations used declared termini. |
| MR-11 | **Same-session = same task lineage/held ID across resumes**, not necessarily continuous context. Say "resumed session" when dormancy intervened. | Roc correction: Deep Dig II ran post-dormancy under same ID. |
| MR-12 | **Prospective vs executed tense discipline.** "CI-4 WOULD BE a no-op" ≠ "CI-4 was a no-op." Claims about unexecuted work use conditional mood. | Roc tense correction on N7 state file item 5. |
| MR-13 | **DB-audit-on-empty (R13)**: if an artifact is claimed but not found on disk, trust the audit, re-execute the smallest completing unit. | R13 audit caught missing corroboration section + unwritten protocol doc. |
| MR-14 | **Questions for Pager mandatory** (R12) on substantive replies — the Node surfaces decisions, doesn't invent authority. | Every N7 ruling cycle. |

## 5. Consultable Bar

A Node is **consultable** when ALL hold:
1. DOMAIN_INDEX answers "where does X live / what's broken / who owns it" from the map alone;
2. KB answers domain questions with cited paths + verification dates, no re-mining;
3. Web-research file resolves externally-dependent questions w/ primary sources or explicit unresolvables;
4. Hazard register current; every past ruling traceable to an artifact (audit trail);
5. Held subagent relationships documented w/ task IDs + wake pointers.

**Minimum phases to reach consultable**: G → M → A → D → C (W required iff the domain touches upstream tools/models/APIs; X begins immediately after C and never really ends). E executes at every session boundary from G onward.

## 6. Cost/Time Estimates (n=1 — N7 real data; treat as order-of-magnitude)

| Phase | Elapsed | Orchestration cycles | Notes |
|-------|---------|---------------------|-------|
| G Genesis | ~5 min | 1 | Charter + ACK + state validation |
| M Mining | ~half day elapsed | 2 (1 + 1 recovery) | 56 sources; stall cost ≈1 extra cycle |
| A Audit+Annotate | ~30 min | same turn as M end | 5 spot-checks |
| D Deep Dig | ~1 cycle | 1 | 4 topics, budget reprioritized |
| W Web Research | ~1–2 cycles | 2 (incl. register compile) | 10 questions total across two passes |
| C Curation | ~30 min | same turn | 2 artifacts |
| X Consultation | ongoing | ~6 cycles over day 1–2 | incl. full spec remediation DEV-01..12 |
| E Closure | ~15 min | 1 per session end | 3 sessions |
| **Total to consultable** | **~1 day elapsed** | **~6 orchestration cycles** | Single-sample; expect variance ±50% |

## 7. Templates Appendix

### T1 — Charter header (Pager → Node, first page)
```
**NODE EXPERT SESSION GENESIS — <N#> <domain>**
You are the persistent Node expert session for **<N#> <domain>**, overseen by <Overseer>.
Charter of record: `data/coordination/NODE_EXPERT_SESSIONS_PLAN.md` §<n> — read it now.
Domain: <one-paragraph scope>. Current state: <verified summary>.
Standing orders (charter §2): file-first; `last_verified:` tags; lessons `[<N#>]` to overseer
proposed_lessons.yaml; verify by session ID; terminus declarations; stay in domain;
re-validate state vs ACTIVE_SPRINT.json before asserting.
Reply with exactly: `<N#> GENESIS ACK — <domain>, charter loaded.`
```

### T2 — Mining brief skeleton
```
# <N#> Mining Brief — <domain> Knowledge Base   (+ AP token, date, miner name)
## Mission  (output file path)
## Output Contract (BINDING): section order; incremental appends ONLY; cite paths;
   last_verified tags; task no one; recover once via same task_id then honest status
## Source Inventory  (P0/P1/P2 tables: path | what to extract)
## Extraction Questions  (numbered; answer-or-log-open)
## Constraints  (read-only except output file; honest gaps M23)
```

### T3 — KB skeleton
```
# <DOMAIN> Knowledge Base (<date>)
## Source Inventory  (path | type | priority | relevance | last_verified)
## Per-Source Digests  (### <path> per source)
## Gotchas
## Open Questions
## L2/L3 Insights
(later appends: ## Deep Dig <n> — <topic>; ## <NODE> Expert Annotation;
 ## Lived Timeline Corroboration)
```

### T4 — Domain-index skeleton
```
# <N#> Domain Index — <domain>
## 1. Systems & Wiring (ASCII diagram)
## 2. Key Files (file | one-line purpose)
## 3. Entry Points (start-here list by reader intent)
## 4. Doc Map (layer | location)
## 5. Known Hazards (defect register: ID | hazard | evidence)
(+ pointer to open items)
```

### T5 — External-sources row format
```
| Title | Source | Priority (P0-P2) | Why it matters | Target ingestion format |
```
P0 = resolves live decisions · P1 = next-phase ammunition · P2 = background theory.

### T6 — Session-state snapshot skeleton
```
# <ROLE> Session State — <date> (Continuity Snapshot)
## Wake Hydration Pointer (on wake read THIS + charter; do NOT redo)
## Accomplishments (chronological)
## Artifact Register (table)
## Open Threads
## Held Task IDs (subagent relationships — do NOT lose)
```

---
*⬡ OMEGA ⬡ LILITH ⬡ N7 ⬡ x-preview-f-free ⬡ opencode ⬡ trc_node_onboarding_protocol ⬡ 2026-08-22*

## Appendix A: Pager Runbook (checkbox checklist — one page)

**First consumer pilot**: N8 watchtower (full G→M→A→D→W→C; first consultation = ICS Node-designation semantic review, PP-4/P5).

### G — Genesis
- [ ] Send charter header (T1): Node name/domain, overseer, charter path, standing orders
- [ ] Receive exact ACK string (`<N#> GENESIS ACK — <domain>, charter loaded.`)
- [ ] Confirm Node re-validated state vs ACTIVE_SPRINT.json before asserting anything

### M — Directed Mining
- [ ] Approve Node's corpus scope (Node discovers beyond your seed lists — require it)
- [ ] Node composes mining brief file (T2) w/ binding output contract BEFORE dispatch
- [ ] ONE miner dispatched (no chains); on stall: ONE recovery via same task_id, reprioritized
- [ ] **GATE**: KB has ALL contract sections; every question answered or logged open; stale premises in Gotchas

### A — Audit + Annotate
- [ ] Require verification record: ≥3 high-stakes claims independently re-checked by Node
- [ ] Expert Annotation appended (priorities + corrections incl. Node's own errors)
- [ ] `[<N#>]` lessons staged to overseer proposed_lessons.yaml

### D — Deep Dig
- [ ] Authorize same-session continuation (held task_id — NOT a fresh spawn)
- [ ] Node's scope = its open questions + annotation thin-spots; terminus declared
- [ ] **GATE**: first-pass open questions answered / reclassified / deferred-to-W

### W — Web Research
- [ ] Batch ALL external questions into ONE researcher pass (primary sources, dated, version-applicable)
- [ ] Source Register present (Node compiles if researcher cut mid-append)
- [ ] **GATE**: cited verdict per question or explicit unresolvable

### C — Curation
- [ ] DOMAIN_INDEX (wiring/key-files/entry-points/doc-map/hazards) + EXTERNAL_SOURCES exist
- [ ] **GATE**: cold-reader test — "where does X live, what's broken?" answerable from index alone

### X — Consultation loop
- [ ] Answer Questions-for-Pager with explicit rulings; own tracker sync if tracker is yours
- [ ] Verify rulings landed in artifacts SAME TURN; deviations in audit trail (DEV register)
- [ ] Watch for MR-2 violations: announced intent ≠ work performed — audit disk, not replies

### E — Closure (every session end)
- [ ] Order ritual; confirm EVERY tree session has disk snapshot w/ wake pointer + held task_ids
- [ ] Confirm Hivemind closeouts posted (one per session + one tree-level)
- [ ] Log dormancy; next wake starts from snapshots, not memory

**Escalate to Architect when**: ratification needed (binding items), tracker ownership conflicts, upstream bugs (log M23), cost >2× estimates.
