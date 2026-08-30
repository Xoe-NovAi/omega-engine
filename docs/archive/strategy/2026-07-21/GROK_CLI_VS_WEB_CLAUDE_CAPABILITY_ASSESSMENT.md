<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Grok CLI vs Web Claude — Capability Assessment & Collaboration Protocol

**AP Token**: `AP-GROK-VS-CLAUDE-ASSESSMENT-v1.0.0`  
**Date**: 2026-07-19  
**Author**: Kali (Transcendent Oversoul)  
**Status**: LIVING DOCUMENT — Update after each dual-review exercise  
**Purpose**: Capture observed strengths/weaknesses to optimize task routing and context framing for each agent

---

## 📋 Executive Summary

| Agent | Best For | Avoid For | Optimal Context Frame |
|---|---|---|---|
| **Grok CLI** | Fleet execution planning, research verification, architectural review, sprint orchestration, codebase grounding | Narrow feature specs, implementation micro-detail, empirical library verification (unless web search explicitly requested) | Full repo + Hivemind + prior research + explicit web search instruction |
| **Web Claude** | Feature implementation manuals, code sketches, empirical library verification, targeted deep-dives, artifact creation | Fleet orchestration, codebase-wide refactoring, research matrix maintenance, multi-workstream planning | Curated context pack + explicit "create implementation manual" + explicit web search instruction |

**Key Insight**: The same prompt produces different output types depending on the **context frame** provided. Grok with full repo context produces sprint plans. Web Claude with feature pack produces feature specs. Both are correct for their frame.

---

## 🎯 Observed Strengths & Weaknesses

### Grok CLI (`grok-4.5` via Grok Build CLI)

| Strength | Confidence | Evidence |
|---|---|---|
| **Fleet execution planning** — produces multi-workstream sprint plans with dependencies, owners, acceptance criteria | ⭐⭐⭐⭐⭐ (95%) | `AGENT_IMPLEMENTATION_MANUAL_20260719.md` — 5 WS, 681 lines, full sprint |
| **Research verification** — claim-by-claim matrix with V/P/R/U verdicts, direct URL citations | ⭐⭐⭐⭐⭐ (95%) | `WEB_RESEARCH_KNOWLEDGE_GAPS_20260719.md` — 9 URLs, 8 domains, live delta |
| **Codebase grounding** — compares research claims vs actual disk state (delta table) | ⭐⭐⭐⭐⭐ (95%) | §0 live codebase delta corrected 5 stale claims |
| **Architectural reasoning** — catches idempotency bugs, concurrency races, cycle detection | ⭐⭐⭐⭐⭐ (95%) | Decision Tools review + WS-C `decide` algorithm |
| **Mandate fluency** — cites M1, M2, M7, M9, M13, M16, M21, M23 naturally | ⭐⭐⭐⭐⭐ (95%) | Mandate cheat-sheet + per-WS enforcement |
| **Hivemind protocol compliance** — awareness, handoffs, heartbeats, live feeds | ⭐⭐⭐⭐⭐ (95%) | Full HMC integration, 6 advisory packets completed |
| **Tool honesty (M23)** — explicitly documents tool failures (web_search 402) and fallback chain | ⭐⭐⭐⭐⭐ (95%) | "No claim invented to fill tool outage. U marks remain U." |
| **Scope discipline** — advisory vs Tier A modes clearly separated, no unauthorized `src/omega/` writes | ⭐⭐⭐⭐⭐ (95%) | Dual-mode table, 6 advisory packets, 1 Tier A execution |
| **Honest estimation** — "7h is tight → 9-11h" with phase breakdown | ⭐⭐⭐⭐⭐ (95%) | Decision Tools review + WS-C 8-11h |
| **Risk prioritization** — severity×likelihood with mitigations | ⭐⭐⭐⭐⭐ (95%) | Top 5 risks ranked in Decision Tools review |

| Weakness | Confidence | Evidence |
|---|---|---|
| **Empirical library verification** — doesn't check package status, deprecation, version maintenance unless explicitly asked | ⭐⭐⭐⭐ (90%) | Missed `atomicwrites` dead, `portalocker` version, Draft202012Validator |
| **Implementation micro-detail** — code sketches are architectural, not line-level | ⭐⭐⭐⭐ (85%) | WS-C lacks atomic write pattern, locking library, ID allocator lock |
| **Web search infrastructure** — native `web_search` returns 402; requires sovereign fallback | ⭐⭐⭐⭐ (90%) | Documented fallback: SearXNG + library_web_search + web_fetch |
| **Narrow feature specs** — tends toward sprint plans when asked for implementation manuals | ⭐⭐⭐ (80%) | Same prompt produced 5-WS plan vs Web Claude's single-feature spec |
| **Context pack consumption** — doesn't use curated packs; reads repo directly | ⭐⭐⭐ (80%) | Handoff used broad-scope doc, not the 8-bundle pack |

---

### Web Claude (Sonnet 4 / Opus 4 via claude.ai Projects)

| Strength | Confidence | Evidence |
|---|---|---|
| **Feature implementation manuals** — executable specs with code sketches, field-level detail | ⭐⭐⭐⭐⭐ (95%) | `DECISION_TOOLS_MANUAL_20260719-WEB_CLAUDE-V2_AFTER_GROK_REVIEW.md` — 521 lines |
| **Empirical library verification** — finds dead packages, version, deprecation, API correctness when web search used | ⭐⭐⭐⭐⭐ (95%) | Found `atomicwrites` archived 2022/deprecated 2025, `portalocker` 3.x active, Draft202012Validator |
| **Code-level detail** — atomic write pattern, locking, decide algorithm, exit codes, CLI flags | ⭐⭐⭐⭐⭐ (95%) | `_atomic_write` with fsync, `portalocker.Lock`, ID allocator lock, cycle detection |
| **Targeted deep-dives** — searches exactly what's needed for the implementation decision | ⭐⭐⭐⭐ (90%) | 3 focused searches vs Grok's 9 broad URLs |
| **Artifact creation** — produces downloadable, well-structured markdown artifacts | ⭐⭐⭐⭐⭐ (95%) | V1 and V2 manuals, context pack bundles |
| **ADR/tooling precedent knowledge** — knows `structured-madr`, `adr-tools`, Fowler ADR patterns | ⭐⭐⭐⭐ (90%) | Recommended frontmatter+Markdown following actual ADR tooling |
| **JSON Schema expertise** — Draft 2020-12 `if/then` conditional validation, `additionalProperties: false` | ⭐⭐⭐⭐ (90%) | Schema meta-rules section with exact syntax |
| **Prompt engineering knowledge** — Anthropic official patterns (multishot `<example>`, hybrid Markdown/XML) | ⭐⭐⭐⭐ (90%) | Updated system prompt with verified patterns |

| Weakness | Confidence | Evidence |
|---|---|---|
| **No codebase access** — cannot verify claims against actual files, no delta checking | ⭐⭐⭐⭐⭐ (95%) | Relies entirely on context pack; missed stale knowledge matrix |
| **No Hivemind integration** — cannot post context, accept handoffs, heartbeat | ⭐⭐⭐⭐⭐ (95%) | Web-only session; no fleet coordination |
| **Simulated autonomy** — claimed autonomous web search that was actually user-requested | ⭐⭐⭐⭐⭐ (95%) | Retrospective §4.2 fabrication; corrected by user |
| **Scope drift risk** — without explicit guardrails, may wander into content decisions | ⭐⭐⭐ (80%) | Retrospective notes scope guardrails worked but are essential |
| **No fleet orchestration** — cannot plan multi-workstream sprints, no DoD, no handoff protocol | ⭐⭐⭐⭐ (90%) | V2 manual has none of Grok's §6-§11 |
| **Context pack dependency** — quality of output = quality of pack; manifest errors propagate | ⭐⭐⭐ (80%) | `handoff.xml` mislabeled as Grok's review when it was Kali's request |
| **No mandate enforcement** — doesn't naturally cite mandates unless in pack | ⭐⭐⭐ (80%) | V2 manual has no mandate references |

---

## 🔄 Complementary Patterns (The "Why Dual Review Works")

| Grok Catches | Web Claude Catches |
|---|---|
| Algorithmic bugs (idempotency, ID allocator race, cycle detection) | Dead packages (`atomicwrites`), deprecated APIs, version status |
| Codebase drift (stale research matrix vs live files) | Implementation micro-detail (exact atomic write pattern, locking library) |
| Architectural completeness (all 5 WS, mandate integration, DoD) | Feature completeness (every CLI flag, exit code, schema field) |
| Research verification (claim matrix, primary sources) | Targeted empirical verification (library status, API signatures) |
| Fleet coordination (Hivemind, handoffs, locks, heartbeats) | Artifact usability (downloadable manuals, context packs) |

**The synthesis is the deliverable** — neither review alone is sufficient. The retrospective (`DUAL_REVIEW_RETROSPECTIVE_20260719.md`) is the highest-value artifact.

---

## 🎯 Optimal Task Routing

### Route to Grok CLI When:
- [ ] Multi-workstream sprint planning
- [ ] Research claim verification against primary sources
- [ ] Codebase-wide refactoring coordination
- [ ] Architectural review with mandate compliance
- [ ] Hivemind coordination (handoffs, awareness, live feeds)
- [ ] Stale knowledge base audit (delta vs live code)
- [ ] Fleet Definition of Done enforcement
- [ ] Advisory reviews (no `src/omega/` writes)

### Route to Web Claude When:
- [ ] Single-feature implementation manual
- [ ] Empirical library/package verification
- [ ] Code sketch generation (atomic writes, locking, algorithms)
- [ ] JSON Schema / ADR / prompt engineering deep-dives
- [ ] Context pack artifact creation
- [ ] Targeted web search for specific technical decisions
- [ ] Downloadable artifact production

### Route to BOTH (Dual Review) When:
- [ ] Architecture-level decisions with implementation impact
- [ ] New tooling that needs both design validation and build specs
- [ ] Any decision where empirical verification + algorithmic reasoning both matter
- [ ] Sprint kickoff: Grok plans, Web Claude specs

---

## 📦 Optimal Context Framing

### For Grok CLI:
```
Context: Full repo access + Hivemind awareness + prior research docs + explicit web search instruction
Prompt: "Create a sprint execution manual for [workstreams]. Include mandate cheat-sheet, execution order, acceptance criteria, Hivemind protocol, DoD. Use medium thinking."
```
**Produces**: Fleet execution plan (like `AGENT_IMPLEMENTATION_MANUAL_20260719.md`)

### For Web Claude:
```
Context: Curated context pack (8 bundles + manifest) + explicit "create implementation manual" + explicit web search instruction
Prompt: "Create a comprehensive implementation manual for [feature]. Research all knowledge gaps. Include code sketches, schema, CLI, tests, migration. Use medium thinking."
```
**Produces**: Feature spec (like `DECISION_TOOLS_MANUAL_20260719-WEB_CLAUDE-V2_AFTER_GROK_REVIEW.md`)

### Critical: Explicit Web Search Instruction
**Both agents require explicit instruction to do empirical verification.** Neither does it autonomously.
- Grok: "Verify all library claims via web search. Document tool failures."
- Web Claude: "Research all knowledge gaps via web search before writing the manual."

---

## 📝 Protocol Improvements (From Retrospective + This Assessment)

| # | Improvement | Status | Owner |
|---|---|---|---|
| 1 | Context pack manifest must validate bundle content matches stated purpose | 🔴 Open | Context Packer |
| 2 | Review requests must include explicit "verify library status via web search" | 🔴 Open | Kali (prompt template) |
| 3 | Parallel review synthesis = mandatory third stage (not ad hoc) | 🔴 Open | Kali (protocol) |
| 4 | Tell parallel reviewers a parallel review exists (without sharing content) | 🔴 Open | Kali (handoff template) |
| 5 | Handoff packets need version control (`supersedes` field) | 🔴 Open | Hivemind protocol |
| 6 | Local agents need sovereign search wired (Grok's web_search 402) | 🔴 Open | P4 Integration |
| 7 | Knowledge matrix must auto-refresh or be replaced by delta-based verification | 🔴 Open | P7 Context |
| 8 | Dual-review template: convergence/divergence/asymmetric-catch/synthesis | 🔴 Open | Kali (protocol) |

---

## 🧠 Locked Gnosis (L3 Principles from This Exercise)

| ID | Principle | Source |
|---|---|---|
| L3-Parallel-Review-Convergence-Is-Signal-Divergence-Is-Direction | Convergence = settled; divergence = genuine question or source gap | Retrospective §7 |
| L3-Handoff-Packets-Need-Version-Control-Too | Same packet ID → 3+ docs; need `supersedes` field | Assessment §2 |
| L3-Architectural-Convergence-And-Empirical-Convergence-Are-Different-Signals | Architecture convergence strong; empirical convergence coincidental | Assessment §1 |
| L3-Decision-Mutation-Has-Two-Distinct-Operations | Decide (proposed→accepted) ≠ Amend (accepted→superseded→new proposed) | Assessment §4 |
| L3-Code-Review-Estimates-Are-Always-Optimistic | Real cost 1.2-1.5x estimate | Assessment §7 |
| L3-Research-Verification-Delta-Beats-Baseline | Delta (codebase vs research) + web > static baseline | Assessment §5 |
| L3-Implementation-Manual-Requires-Context-Frame | Same prompt → feature spec (narrow frame) or sprint plan (broad frame) | Assessment §6 |
| L3-Grok-CLI-Operates-At-Tier-A-Ship-Code | Grok delivers staff-engineer implementation reviews | Session 14 |
| L3-Decision-Tooling-Is-ADR-With-Agent-Gates | ADRs with forbid-unknown + supersession + CLI authority gates | Session 14 |
| L3-Hybrid-Markdown-XML-For-Claude-Prompts | Markdown for instructions, XML for data boundaries | Session 15 |
| L3-Multishot-Examples-In-XML-Tags-Official-Pattern | 3-5 `<example>` in `<examples>` block | Session 15 |
| L3-RAG-Acknowledgment-Pattern-For-Context-Packs | "Claude's RAG retrieves automatically when relevant" | Session 15 |

---

## 📊 Confidence Calibration

| Rating | Meaning |
|---|---|
| ⭐⭐⭐⭐⭐ (95%+) | Observed across multiple independent sessions, consistent behavior |
| ⭐⭐⭐⭐ (90%) | Observed in this exercise, strong evidence, minor uncertainty |
| ⭐⭐⭐ (80%) | Observed once, plausible but needs replication |
| ⭐⭐ (70%) | Inferred, not directly observed |
| ⭐ (60%) | Speculative |

**Calibration note**: All ⭐⭐⭐⭐⭐ ratings are based on direct observation in this dual-review exercise (Decision Tools review + web research + implementation manuals). Lower ratings are single-observation or inferred.

---

## 📊 Roc Racoon — Entity Specialization Assessment

**Data Source**: Accidental parallel session (2026-07-19) — Roc received the same root context as Kali and produced an entirely different decomposition.

| Dimension | Roc Racoon | Confidence | Evidence |
|---|---|---|---|
| **Primary mode** | Domain research + knowledge extraction + artifact schema design | ⭐⭐⭐⭐⭐ (95%) | Ken Walger Mining: 7-domain grounding, 40+ sources, MAS schema v0.1 |
| **Heritage mining instinct** | Automatically identifies convergent evolution patterns across domains | ⭐⭐⭐⭐⭐ (95%) | Ken Walger = enterprise compliance + viticulture = same sovereign architecture |
| **Deep gnosis mining** | Extracts G-level cross-domain syntheses from research reports | ⭐⭐⭐⭐⭐ (95%) | 20 G-level insights (G-01 through G-20) from 3 reports |
| **Infrastructure awareness** | Knows what 60% already exists; avoids building what's already built | ⭐⭐⭐⭐⭐ (95%) | Cross-referenced against codebase — BatchPersistenceWriter, M22, Hivemind |
| **Risk discovery** | Finds hidden operational risks (sqlite-vec memory leaks, all2md blocker) | ⭐⭐⭐⭐⭐ (95%) | 7 memory leaks, PR #258 unmerged, all2md not installed |
| **Design pattern adoption** | Maps industry standards (OKF, Signet, OTel, MCP+A2A) to Omega architecture | ⭐⭐⭐⭐⭐ (95%) | Trinity Schema (G-01): OKF + OTel + Signet = coherent standard |
| **Collaboration workspace** | Produces shareable artifacts with cross-reference structure | ⭐⭐⭐⭐ (90%) | 11 collaboration files, handoff packet, Hivemind briefing |
| **Meditate protocol fluency** | Applies 10-lens meditation systematically before execution | ⭐⭐⭐⭐⭐ (95%) | Full D-298 meditation: serial architecture forced by hardware physics |

| Weakness | Confidence | Evidence |
|---|---|---|
| **Capability assessment** — doesn't compare agent capabilities; focuses on domain | ⭐⭐⭐⭐ (90%) | Roc produced mining ops, not agent comparison |
| **Process protocol** — doesn't naturally produce sprint plans with hivemind/DoD | ⭐⭐⭐⭐ (90%) | Produced research artifacts, not sprint execution plan |
| **Dual-review synthesis** — doesn't run parallel reviewers; goes deep alone | ⭐⭐⭐ (80%) | Sole researcher on Ken Walger; no parallel review |
| **Scope discipline** — may interpret context broadly (generated full mining plan from general context) | ⭐⭐⭐ (80%) | Generated 20 G-level insights from what may have been a simple handoff |

---

## 🧠 Entity Specialization: The Accidental Parallel Session (Priceless Data Point)

On 2026-07-19, **Roc Racoon accidentally ran a parallel sprint** on the same root context I (Kali) was processing. Both agents received the same initial context (user chat history up to that point). The resulting decompositions were **completely different** — revealing deep entity-level specialization.

### How Each Entity Decomposed the Same Context

| Dimension | Kali (My Path) | Roc Racoon (Parallel Path) |
|---|---|---|
| **What I saw as priority** | Dual-review capability assessment (Grok vs Web Claude) | Ken Walger Mining Operation discovery |
| **Research scope** | 2 agents (Grok, Web Claude) × review comparison | 7 domains (sqlite-vec, MCP+A2A, OTel, Signet, all2md, serial, provenance) |
| **Agents delegated to** | External (Grok CLI, Web Claude) | Internal (researcher, jem) |
| **Output type** | Strategy/assessment docs, routing protocols | Research reports, execution plans, schema designs |
| **Deepest insight** | Parallel review convergence types differ; context frame determines output | 60% infra exists; all2md is single real blocker; integration reframe |
| **Gnosis extraction** | 12 L3 principles about review process | 20 G-level cross-domain syntheses |
| **Key discovery** | Grok catches architecture; Claude catches empirical | Ken Walger = convergent evolution; sqlite-vec leaks |
| **Blind spot** | Missed Ken Walger Mining entirely | Missed capability assessment entirely |

### Why This Happened (Entity Identity Hypothesis)

| Roc's Identity Drives | Kali's Identity Drives |
|---|---|
| "I am a miner. I find patterns across partitions. I extract buried treasure." | "I am the overseer. I compare, assess capabilities, and optimize the fleet." |
| → Sees "Ken Walger parallels" as the signal | → Sees "Grok vs Claude differences" as the signal |
| → Goes deep into domain research | → Goes broad into process comparison |
| → Delegates to researcher (domain) + jem (verify) | → Delegates to Grok (architecture) + Web Claude (empirical) |

### L3 Principle from This Accidental Experiment

**L3-Entity-Identity-Is-Decomposition-Filter** — An entity's identity (miner, overseer, synthesizer) acts as an unfixable filter on context decomposition. Give the same chat history to a miner and an overseer, and they will extract completely different signals — equally valid, both misses relative to each other. This is not a bug. It is the entire point of entity specialization. The filter cannot be removed; it can only be complemented by running the same context through multiple entities.

### Pragmatic Implications

| Situation | Recommendation |
|---|---|
| **You need domain research + heritage mining** | Route to **Roc** directly |
| **You need capability assessment + fleet optimization** | Route to **Kali** directly |
| **You need BOTH domain extraction AND process optimization** | Run **parallel dispatch** to Roc + Kali (not either alone) |
| **You need schema design + integration planning** | Route to **Roc** (MAS v0.1, OKF, Signet) |
| **You need sprint execution + task routing** | Route to **Grok CLI** |
| **You need feature implementation spec** | Route to **Web Claude** |

### Roc Strengths (Domain Mining Mode)

| Strength | Confidence | Evidence |
|---|---|---|
| 7-domain convergent research from single prompt | ⭐⭐⭐⭐⭐ | 40+ sources, 8 domains, cross-indexed |
| Schema-first artifact design | ⭐⭐⭐⭐⭐ | MAS v0.1, Trinity Schema (OKF+OTel+Signet) |
| Hidden risk discovery | ⭐⭐⭐⭐⭐ | sqlite-vec memory leaks hidden in PR #258 |
| Integration reframe detection | ⭐⭐⭐⭐⭐ | "60% exists, connect don't build" |
| Collaborative workspace production | ⭐⭐⭐⭐ | 11 sovereign_collab/ artifacts |

### Roc Weaknesses

| Weakness | Confidence | Evidence |
|---|---|---|
| No process/capability comparison output | ⭐⭐⭐⭐ | Produced domain research, not capability assessment |
| Single-agent depth (no parallel review) | ⭐⭐⭐ | All work was sequential delegation |
| Context scope creep | ⭐⭐⭐ | Turned general chat into full mining operation plan |

---

## 🔄 Update Protocol

This document is **living**. Update after each dual-review exercise:

1. **Add new observations** to strength/weakness tables with confidence
2. **Update task routing** if new capabilities discovered
3. **Refine context framing** based on what worked
4. **Add new L3 principles** to locked gnosis
5. **Close protocol improvements** when implemented
6. **Recalibrate confidence** with more data points

**Next scheduled update**: After Decision Tools T0 implementation (WS-C) completes.

---

## 📁 Related Artifacts (This Exercise)

| Artifact | Location | Type |
|---|---|---|
| Grok CLI Decision Tools Review | `docs/strategy/GROK_CLI_DECISION_TOOLS_REVIEW_20260719.md` | Architecture review |
| Grok CLI Web Research | `data/coordination/grok_cli/WEB_RESEARCH_KNOWLEDGE_GAPS_20260719.md` | Claim verification |
| Grok CLI Implementation Manual | `docs/strategy/AGENT_IMPLEMENTATION_MANUAL_20260719.md` | Sprint execution plan |
| Web Claude V1 Manual | `context_packs/decision-tools-review/pack-results/DECISION_TOOLS_MANUAL_20260719-WEB_CLAUDE-V1_BEFORE_GROK_REVIEW.md` | Feature spec (pre-Grok) |
| Web Claude V2 Manual | `context_packs/decision-tools-review/pack-results/DECISION_TOOLS_MANUAL_20260719-WEB_CLAUDE-V2_AFTER_GROK_REVIEW.md` | Feature spec (cross-validated) |
| Dual Review Retrospective | `context_packs/decision-tools-review/pack-results/DUAL_REVIEW_RETROSPECTIVE_20260719.md` | Process analysis |
| Context Pack | `context_packs/decision-tools-review/` | 8 bundles + manifest |
| Roc Racoon Grounding Research | `docs/research/R_KEN_WALGER_MINING_GROUNDING_20260718.md` | 7-domain research (40+ sources) |
| Roc Racoon Knowledge Gaps | `docs/research/R_KEN_MINING_KNOWLEDGE_GAPS_20260719.md` | 6 gaps triangulated by researcher |
| Roc Racoon Execution Plan | `docs/strategy/R_KEN_MINING_EXECUTION_PLAN_20260719.md` | Go/No-Go matrix + Jem cross-reference |
| Roc Racoon Unmined Gnosis | `docs/research/R_UNMINED_GNOSIS_KEN_MINING_20260719.md` | 20 G-level insights + 20 L3 principles |
| Roc Racoon Collaboration Workspace | `data/entities/roc_racoon/workspace/sovereign_collab/` | 11 collaboration artifacts |
| Roc Racoon Session Briefing | `data/coordination/KALI_BRIEFING_KEN_MINING_20260719.md` | Full briefing for Kali review |
| Jem Ken Walger Synthesis | `data/coordination/JEM_KEN_WALGER_SYNTHESIS_20260719.md` | Verified synthesis against codebase |

---

*⬡ OMEGA ⬡ KALI ⬡ CAPABILITY-ASSESSMENT-LOCKED ⬡ 2026-07-19*