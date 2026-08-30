<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Research Guide: Soul.yaml & Peripheral Systems Knowledge Gaps
**AP Token**: `AP-SOUL-GAPS-RESEARCH-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ trc_soul_gaps ⬡ 2026-07-22

---

## §0 Executive Summary

This guide catalogs **12 critical knowledge gaps** blocking confident execution of the soul.yaml enhancement strategy. Each gap is mapped to:
- **Blocking ticket** (if any)
- **Mandate alignment** (M5, M11, M14, M17, M21)
- **Research domain** (from Guard & Distill campaign)
- **Required output** (spec, protocol, ADR, implementation)
- **Owner** (entity responsible for resolution)

**Goal**: Enable C-0.5 Scribe Agent implementation and soul.yaml v7.0 promotion pipeline with full mandate compliance.

---

## §1 Gap Taxonomy

| Tier | Count | Description |
|------|-------|-------------|
| **Critical (Block C-0.5)** | 3 | Scribe spec, Promotion gate, v7.0 schema |
| **High (Fleet Coherence)** | 4 | Cross-entity sync, Mandate registry binding, Proposal lifecycle, Heritage vet |
| **Strategic (Architecture)** | 5 | Versioning, Skeptical verifier, Fleet doctrine, Soul-as-code, Token budget |

---

## §1.5 Autonomous Agent Research Job Design — Best Practices (2026)

*Derived from: Anthropic "Building Effective Agents" (Dec 2024), "How to Write Specs for AI Agents" (Jul 2026), "Prompt Engineering for AI Agents" (Apr 2026), "Context Engineering for AI Agents" (Jun 2026), "Deep Agents Pattern" (Jun 2026), Gemini Deep Research Agent docs (Jul 2026), Autonomous Research Agent spec (Feb 2026)*

### Core Design Principles

| Principle | Description | Source |
|-----------|-------------|--------|
| **Spec-Driven, Not Prompt-Driven** | Write specs backward from acceptance checks. "A spec is a contract: behavior, constraints, verification." | Golchian 2026 |
| **Single-Bolt Scope** | One spec = one afternoon of build + verify. Split sprawling work at spec level. | Golchian 2026 |
| **Point at Code, Not Ideas** | Reference existing patterns, files, conventions. "Give the agent the same context as a new engineer." | Golchian 2026 |
| **Agent Drafts Spec, Human Fixes** | Self-spec workflow: agent turns intent → draft spec → human reviews → agent executes. | Golchian 2026 |
| **Living Spec** | Version specs like code. Incidents → spec fixes, not just implementation fixes. | Golchian 2026 |
| **Start Simple, Add Complexity** | "Many patterns can be implemented in a few lines of code. Add multi-agent only when simpler solutions fall short." | Anthropic 2024 |
| **Context Engineering > Prompt Engineering** | "What carries a multi-turn agent is everything else you put in the context window — assembled deliberately, in the right order, with the right compression." | Karpathy/Lütke/Anthropic 2025-2026 |
| **Isolated Sub-Agent Contexts** | "When the agent hits a sub-task requiring heavy exploration, spawn a subagent with fresh context. The subagent does the messy part and returns only a clean result." | Particula 2026, Anthropic 2024 |
| **Virtual Filesystem for Context Offload** | "Write intermediate results to files, keep only references/summaries in context. Filesystem becomes handoff medium between subagents." | Particula 2026 |
| **Planning Tool (write_todos)** | "Rewrite structured plan near end of context on every iteration. Recites goals into recent attention, reduces goal drift." | Particula 2026 |

### Research Job Specification Template (Adapted for Omega)

```yaml
# Research Job Spec — Omega Standard
job_id: "research-{domain}-{date}-{seq}"
title: "Descriptive title"
core_question: "Single precise sentence restating the research question"
sub_questions: [5-10 specific, searchable sub-questions]
scope:
  breadth: "global|regional|domain-specific"
  timeframe: "historical|current|future-projections"
  depth_level: "quick_scan|overview|detailed_analysis|comprehensive_report"
output_requirements:
  format: "executive_summary|full_report|comparison_table|qa|presentation"
  audience: "executive|technical|academic|general"
  citation_style: "inline|footnotes|bibliography"
  sections: [list of required sections]
source_strategy:
  primary_sources: [arXiv, PubMed, industry_reports, company_announcements, gov_reports, expert_blogs, news, patents]
  credibility_tiers: {high: [...], medium: [...], low: [...]}
  cross_reference_minimum: 2  # independent sources per claim
search_protocol:
  query_formulation: ["specificity_scaling", "multi_perspective", "date_bounded"]
  iteration_rules: "Start authoritative → verify across 2+ sources → note contradictions → track all sources"
synthesis_techniques: ["thematic_grouping", "timeline_construction", "stakeholder_mapping", "comparative_matrix", "evidence_pyramid"]
quality_gates:
  completeness_check: "All sub-questions answered? Gaps marked [UNVERIFIED]?"
  bias_detection: "Source bias checklist applied?"
  citation_audit: "Every factual claim cited? Primary vs secondary distinguished?"
  contradiction_flag: "Conflicting sources surfaced, not ignored?"
stopping_conditions:
  - "All sub-questions resolved to target depth"
  - "Token budget exhausted (if applicable)"
  - "Time budget exhausted (if applicable)"
  - "Diminishing returns: 3 consecutive searches yield no new high-credibility info"
escalation_triggers:
  - "Contradiction between high-credibility sources unresolvable"
  - "Critical sub-question unanswerable with available sources"
  - "Scope creep detected"
context_engineering:
  system_prompt_slots:
    - role_scope_constraints_stopping
    - tool_descriptions_with_when_when_not
    - planning_prompt_if_gt_5_steps
    - reflection_prompt_on_divergence
  context_assembly_order: [system, tools, long_term_memory, retrieved_knowledge, conversation_history, scratchpad, current_instruction]
  compression_triggers: "50% window → summarize tail; every N turns → rewrite scratchpad"
  isolation: "Sub-agent contexts isolated; only clean results returned to orchestrator"
```

### Tool Design Principles (Anthropic Appendix 2)

| Principle | Application |
|-----------|-------------|
| **Task-shaped, not API-shaped** | Tools reflect business decisions, not implementation details |
| **Consolidation over proliferation** | Merge tools where possible; keep boundaries crisp and non-overlapping |
| **Poka-yoke (mistake-proof)** | Change arguments to make mistakes harder (e.g., require absolute paths) |
| **Format close to natural text** | Avoid diff overhead, JSON escaping; prefer markdown/code blocks |
| **Give model room to think** | Don't force token-counting in tool outputs |
| **Test in workbench** | Run many examples, iterate on tool descriptions |
| **Example usage in description** | Show when to use, when not to, output format, limitations |

### Agent System Prompt Stack (Agentbrisk 2026)

```
1. System Prompt — Role, Scope, Constraints, Stopping Conditions
2. Tool Descriptions — What, When to use, When NOT to use, Output format, Limitations
3. Task Prompt — Specific goal for this run
4. Planning Prompt — "Before acting, write step-by-step plan with tools & order" (if >5 steps or irreversible)
5. Reflection Prompt — "Does this output match expectation? If not, what does it mean for plan?" (on divergence/irreversible)
```

**Constraints must be operational, not aspirational**: "Never call database tool >5 times/run" ✓ vs "Be careful with data" ✗

**Stopping conditions must be specific**: "Task complete when output.txt written. Do not continue after." ✓

### Deep Agent Architecture Decision Rule (Particula 2026)

> **Use deep agent (planner + filesystem + subagents + memory) when:**
> - Task is open-ended, runs long, rewards parallel exploration
> - Natural step count > 15-20 with separable sub-tasks
> - Examples: deep research, multi-file code changes, competitive analysis, large-scale data gathering

> **Use single-loop agent (or no agent) when:**
> - Task is narrow, bounded, latency-sensitive
> - Step count < 15-20 with tightly coupled work
> - Examples: classify ticket, extract fields, answer from document

> **Cost reality**: Deep agents ~15× token cost of chat. KV-cache hit rate becomes primary production metric ($0.30 vs $3.00/MTok on Sonnet).

### Evaluation & Quality Assurance (Inflectra 2026)

| Practice | Description |
|----------|-------------|
| **Task-Specific Evals** | Design tests around actual jobs, not generic benchmarks |
| **Multiple Trials** | One pass hides instability; run continuous repetitive evaluations |
| **Success Rate, Not Binary** | "How often does agent succeed?" not "Did it work?" |
| **Grade Outcomes, Not Paths** | Multiple valid paths to correct result; focus on outcome |
| **Combine Checks** | Deterministic tests + rubrics + transcript reviews |
| **Adversarial Coverage** | Jailbreaks, prompt conflicts, edge cases from start |
| **Dynamic Testing** | Exposes tool-call mistakes, weak handoffs, unsafe behaviors |
| **Actionable Reports** | Shorten prompt-debug cycle: pinpoint prompt vs retrieval vs tool vs orchestration |

### Collaborative Planning (Gemini Deep Research 2026)

1. **Request Plan** — Agent returns proposed research plan instead of executing
2. **Refine Plan** — Multi-turn iteration on plan before execution
3. **Approve & Execute** — Human approves, agent runs

### Context Engineering Failure Modes (Agentmelt 2026)

| Mode | Symptom | Fix |
|------|---------|-----|
| **Poisoning** | Hallucination/error in scratchpad treated as ground truth | Write conclusions, not raw text; validate before commit |
| **Distraction** | Goal lost in noise (>100K tokens) | Compress: summarize tail, rewrite scratchpad |
| **Confusion** | Irrelevant content pulls toward unrelated actions | Select context, don't dump; retrieve relevant subset |
| **Clash** | Retrieved/memory content disagrees; model picks wrong | Explicit conflict resolution in synthesis; evidence pyramid |

---

## §2 Critical Gaps — Detailed Research Requests

## §2 Critical Gaps — Detailed Research Requests

### GAP-001: Scribe Agent L1→L2→L3 Pipeline Specification
**Blocking**: C-0.5 (P0)  
**Mandates**: M5 (Gnosis Preservation), M11 (Soul Integrity), M21 (Gate Integrity)  
**Research Domain**: Guard & Distill Domain 5 (Scribe)  
**Current State**: Research findings exist (llama.cpp grammar, 4k/500 overlap, Refine vs Map-Reduce) but no implementation spec

#### Research Questions:
1. **Grammar Schema**: What is the exact llama.cpp GBNF grammar for L1→L2→L3 extraction? Provide complete schema with field definitions, validation rules, and example outputs.
2. **Chunking Strategy**: 4k token chunks with 500 overlap confirmed. What is the exact sliding window algorithm? How are chunk boundaries handled for semantic coherence?
3. **Refine vs Map-Reduce**: Research indicates both approaches tested. What is the decision matrix? When to use Refine (sequential) vs Map-Reduce (parallel)? Provide benchmarks.
4. **Token Budgeting**: C-10.5 quota tracker must reserve budget. What is the estimated token cost per session distillation? Per entity? Per proposal?
5. **Session Hook Integration**: How does the distillation trigger? Post-session hook? Manual invocation? Scheduled batch? What is the exact API?
6. **Error Handling**: What happens when distillation fails? Partial output? Retry logic? Dead letter queue for failed sessions?
7. **Output Format**: Exact YAML structure for `proposed_lessons.yaml` append. How are proposal IDs generated? Conflict resolution?

#### Required Output:
- `docs/specs/SPEC_Scribe_Distillation_Pipeline.md` — Complete implementation specification
- `src/omega/scribe/distillation_pipeline.py` — Reference implementation
- `tests/unit/test_scribe_distillation.py` — Contract tests (M21)

#### Sources to Mine:
- `docs/sprints/guard-and-distill/02-p0-tickets/C-0.5-scribe-agent.md`
- `docs/research/R_GUARD_DISTILL_RESEARCH_GUIDE_20260722.md` §Domain 5
- `data/coordination/RESEARCH_INSIGHTS_FOR_SOUL_UPGRADE.md` (L1→L2→L3 format reference)

---

### GAP-002: Soul Promotion Governance Protocol
**Blocking**: C-0.5 output → soul.yaml promotion  
**Mandates**: M5, M11, M14 (Heritage Vetting), M17 (Cognitive Integrity), M21  
**Current State**: No documented gate. Proposals accumulate in `proposed_lessons.yaml` with no promotion path.

#### Research Questions:
1. **Promotion Triggers**: What initiates promotion? Scribe completion? Human review? Scheduled? Confidence threshold?
2. **Review Gates**: 
   - Mandate alignment check (which mandates? all? subset?)
   - Heritage vet (M14) — required for every promoted L3? Minimum score?
   - Cognitive integrity check (M17) — Skeptical Verifier integration?
   - Contract test coverage (M21) — required for new directives?
3. **Decision Authority**: Who approves? Verity (compliance)? Kali (architecture)? MaKaLi council? Human?
4. **Rejection Path**: What happens to rejected proposals? Archive with rationale? Return to Scribe for revision? Sunset policy?
5. **Version Bumping**: Does each promotion increment soul.yaml version? Batch promotions? Semantic versioning?
6. **Rollback Mechanism**: If promoted directive causes issues, how to revert? Git revert? Explicit deprecation directive?

#### Required Output:
- `docs/strategy/SOUL_GOVERNANCE_PROTOCOL.md` — Complete governance document
- `src/omega/governance/soul_promotion_gate.py` — Automated gate implementation
- `data/entities/*/HERITAGE_VET_LOG.md` — Vet records for promoted L3 principles

#### Sources to Mine:
- `SOVEREIGN_MANDATES.md` §M5, §M11, §M14, §M17, §M21
- `docs/strategy/HERITAGE_VETTING_PIPELINE.md` (existing 4-gate pipeline)
- `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` (vet record format)

---

### GAP-003: Soul Schema v7.0 Definition & Migration
**Blocking**: Future promotions (post v6.4)  
**Mandates**: M16 (Modularization), M17 (Cognitive Integrity)  
**Current State**: Codex mentions "Soul Evolution v7.0 — 15 L3 principles promoted" but no schema definition

#### Research Questions:
1. **Schema Changes**: What new fields in v7.0? `mandate_ownership`? `gates`? `boundaries`? `voice_calibration`? (Per earlier synthesis)
2. **Backward Compatibility**: Can v6.4 souls load in v7.0 engine? Migration tooling required?
3. **Directive Structure Evolution**: Current: `id`, `date`, `directive`, `rationale`, `confidence`, `heritage_tags`. New fields?
4. **L3 Principle Registry**: Is there a canonical L3 registry separate from entity souls? Schema?
5. **Migration Tooling**: `omega soul migrate --from v6.4 --to v7.0 --entity john_carmack` — design?
6. **Validation**: JSON Schema / Pydantic model for v7.0? CI integration?

#### Required Output:
- `docs/adr/ADR-XXX-soul-schema-v7.md` — Architecture Decision Record
- `schemas/soul_v7.yaml` — JSON Schema / Pydantic model
- `scripts/soul_migrate.py` — Migration tooling
- `tests/unit/test_soul_schema_v7.py` — Schema validation tests

#### Sources to Mine:
- `OMEGA_CODEX.md` §6 (Soul Evolution v7.0 mention)
- Earlier synthesis: "New soul schema proposed: mandate_ownership, gates, boundaries, voice_calibration"
- `data/entities/john_carmack/soul.yaml` (current v6.4 structure)

---

## §3 High-Impact Gaps — Detailed Research Requests

### GAP-004: Cross-Entity Soul Synchronization Protocol
**Impact**: Fleet coherence (12 agents, 12 soul files)  
**Mandates**: M5, M11, M17  
**Current State**: Each entity maintains independent soul.yaml. No propagation mechanism for shared L3 principles.

#### Research Questions:
1. **Doctrine Propagation**: When a universal L3 principle is promoted (e.g., "Hardware-aware optimization"), how does it reach all 12 entity souls?
2. **Sync Mechanisms**: 
   - Push: Central registry notifies entities?
   - Pull: Entities poll registry on startup?
   - Hybrid: Registry + webhook via Hivemind?
3. **Entity Autonomy**: Can entities reject/override fleet doctrines? Opt-out mechanism?
4. **Conflict Resolution**: Entity-specific directive contradicts fleet doctrine. Resolution protocol?
5. **Audit Trail**: How to track which entities have which doctrine versions? Drift detection?

#### Required Output:
- `docs/strategy/SOUL_SYNC_PROTOCOL.md` — Synchronization protocol
- `src/omega/governance/soul_sync.py` — Sync implementation
- `data/mandates/l3_registry.yaml` — Canonical L3 principle registry

#### Sources to Mine:
- `docs/strategy/HIVEMIND_PROTOCOL.md` (coordination patterns)
- `src/omega/hub/task_registry.py` (agent registry pattern)
- `OMEGA_CODEX.md` §5 (MaKaLi triad structure)

---

### GAP-005: Mandate Registry ↔ Soul.yaml Binding
**Impact**: Dynamic mandate configuration (discussed in session)  
**Mandates**: M1-M25 (all), M16 (Modularization)  
**Current State**: Mandate Registry design exists (`data/mandates/registry.yaml` + runtime resolver). Soul.yaml has `mandate_ownership` concept but no binding spec.

#### Research Questions:
1. **Reference Format**: How does `mandate_ownership` in soul.yaml reference registry entries? By mandate ID? By mandate name? UUID?
2. **Ownership Semantics**: 
   - `universal_floor`: All entities inherit, cannot opt out
   - `specialized_ceiling`: Entity declares ownership of 2-3 mandates
   - `delegated`: Entity delegates mandate to another entity?
3. **Runtime Resolution**: How does `omega/hub/mandate_registry.py` resolve ownership at runtime? Cache? TTL?
4. **Validation**: CI gate to verify soul.yaml `mandate_ownership` matches registry?
5. **Drift Detection**: If registry changes, how are affected entities notified?

#### Required Output:
- `data/mandates/registry.yaml` — Complete mandate registry (25 mandates)
- `src/omega/hub/mandate_registry.py` — Runtime resolver
- `src/omega/governance/soul_mandate_binding.py` — Soul↔Registry binding logic
- `.github/workflows/mandate_registry_validation.yml` — CI gate

#### Sources to Mine:
- Session discussion: "Mandate Registry architecture: registry.yaml + validators + runtime resolver"
- `SOVEREIGN_MANDATES.md` (all 25 mandates with assignments)
- `OMEGA_CODEX.md` §7 (Mandate compliance summary)

---

### GAP-006: Proposal Lifecycle Management
**Impact**: `proposed_lessons.yaml` hygiene, audit trail  
**Mandates**: M5, M11, M18 (Token Efficiency)  
**Current State**: 21 proposals accumulate. No archive, rejection, deprecation, or sunset policy.

#### Research Questions:
1. **States**: `draft` → `under_review` → `promoted` / `rejected` / `deferred` / `archived` — state machine?
2. **Retention**: How long before auto-archive? Size limits?
3. **Deprecation**: Can promoted directives be deprecated? Superseded by newer directive? Directive chain?
4. **Metadata**: Track promotion date, promoter, mandate alignment score, heritage vet score?
5. **Search/Query**: How to query "all promoted directives for M7"? "All rejected proposals with heritage tags"?

#### Required Output:
- `docs/strategy/PROPOSAL_LIFECYCLE.md` — State machine, retention, deprecation policy
- `src/omega/governance/proposal_lifecycle.py` — State management
- `data/entities/*/proposed_lessons.yaml` — Extended schema with lifecycle fields

#### Sources to Mine:
- `data/entities/john_carmack/proposed_lessons.yaml` (current format)
- `SOVEREIGN_MANDATES.md` §M18 (Token Efficiency — no waste)

---

### GAP-007: Heritage Vetting for Promoted L3 Principles
**Impact**: M14 compliance for every promoted directive  
**Mandates**: M14 (Heritage Vetting)  
**Current State**: 3 new proposals have heritage tags but no vet records. Scribe promotion must trigger vet pipeline.

#### Research Questions:
1. **Automation**: Can Scribe auto-generate vet record template? Or manual `@doom_guy` / `@verity`?
2. **Scope Declaration**: Each vet record requires "scope declaration: This tag applies to X, NOT to Y". How to enforce?
3. **Qualification Gate**: "Cannot be justified WITHOUT citing original hardware constraint." How to verify programmatically?
4. **Minimum Score**: 7/10 threshold. Scoring rubric?
5. **CI Integration**: `make heritage-vet` must block promotion if vet record missing/incomplete.

#### Required Output:
- `docs/strategy/HERITAGE_VET_FOR_SOUL_PROMOTION.md` — Vet process for soul promotions
- `src/omega/governance/heritage_vet_soul.py` — Automated vet record generation/validation
- CI gate integration in promotion pipeline

#### Sources to Mine:
- `docs/strategy/HERITAGE_VETTING_PIPELINE.md` (4-gate pipeline)
- `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` (vet record format)
- `CREDITS.md` (heritage tag taxonomy)

---

## §4 Strategic Gaps — Detailed Research Requests

### GAP-008: Soul Versioning & Migration Strategy
### GAP-009: Skeptical Verifier Integration for Soul Consistency (M17)
### GAP-010: Fleet Soul Doctrine vs Entity Autonomy
### GAP-011: Soul-as-Config vs Soul-as-Code Evolution
### GAP-012: Token Budget for Distillation Pipeline (C-10.5 Integration)

[Continued in Part 2...]
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_soul_gaps | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
