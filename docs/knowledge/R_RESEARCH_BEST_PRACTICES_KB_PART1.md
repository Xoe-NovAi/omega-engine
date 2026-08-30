# 🔱 Omega Engine Autonomous Agent Research Job Design — Best Practices Guide
**AP Token**: `AP-RESEARCH-BEST-PRACTICES-KB-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ trc_research_bp_kb ⬡ 2026-07-22

---

## §0 Executive Summary

This guide captures **production-tested best practices** for designing autonomous agent research jobs in the Omega Engine ecosystem, synthesized from:
- 8 authoritative sources (2024-2026)
- Internal Omega Engine research (Guard & Distill campaign)
- Practical implementation lessons from GAP-001 and GAP-007 job specs
- Anthropic, Golchian, Agentmelt, Particula, and Gemini Deep Research patterns

**Purpose**: Enable consistent, high-sovereignty agents (Researcher, Ma'at, Kali, Verity, etc.) to design research jobs that are:
- **Spec-driven** (not prompt-driven)
- **Context-engineered** (not prompt-engineered)
- **Quality-gated** (with Temple-Grade, Doc Standards, Mandate alignment)
- **Living documents** (specs versioned like code)
- **Cost-aware** (token budgeting integrated with C-10.5 quota tracker)

**Scope**: Applies to all research tasks in `docs/research/` and `docs/strategy/` requiring deep investigation, synthesis, and deliverable creation.

**Knowledge Base Location**: This guide is the canonical reference for research job design in the Omega Engine KB (`docs/knowledge/`).

---

## §1 Core Principles — The Foundation

### 1.1 Spec-Driven, Not Prompt-Driven (Golchian 2026)
> "The single most expensive habit in agentic development is typing a vague prompt and hoping."

**Implementation**:
- Write specs **backward from acceptance checks** (Definition of Done)
- A spec is a **contract**: behavior, constraints, verification
- **Agent drafts spec → Human reviews/fixes → Agent executes** (self-spec workflow)
- **Living spec**: Version specs like code; incidents → spec fixes, not just implementation fixes

### 1.2 Context Engineering > Prompt Engineering (Agentmelt 2026)
> "What carries a multi-turn agent is everything else you put in the context window — assembled deliberately, in the right order, with the right compression."

**Implementation**:
- **7 Context Slots** (in order):
  1. System prompt (role, scope, constraints, stopping conditions)
  2. Tool definitions (JSON schemas)
  3. Long-term memory (selective retrieval)
  4. Retrieved knowledge (RAG chunks)
  5. Conversation history (compressed)
  6. Scratchpad / working memory (explicit conclusions)
  7. Current step's instruction
- **Failure Modes to Fix** (not with better prompts):
  - **Poisoning**: Write conclusions, not raw text; validate before commit
  - **Distraction**: Compress: summarize tail, rewrite scratchpad
  - **Confusion**: Select context, don't dump; retrieve relevant subset
  - **Clash**: Explicit conflict resolution in synthesis; evidence pyramid

### 1.3 Start Simple, Add Complexity (Anthropic 2024)
> "Many patterns can be implemented in a few lines of code. Add multi-agent only when simpler solutions fall short."

**Decision Rule** (Particula 2026):
- **Single-loop agent** (or no agent): Under ~15-20 steps with tightly coupled work
- **Deep agent** (planner + filesystem + isolated subagents + memory): Beyond 15-20 steps with separable exploratory sub-tasks
- **Cost reality**: Deep agents use ~15× tokens of single chat; KV-cache hit rate becomes primary production metric

### 1.4 Point at Code, Not Ideas (Golchian 2026)
> "Give the agent the same context you would give a new engineer on their first day: here is how we do things here."

**Implementation**:
- Reference existing Omega patterns, files, conventions
- Point to specific code: `src/omega/hub/task_registry.py`, `docs/strategy/HERITAGE_VETTING_PIPELINE.md`
- Reference internal docs: `OMEGA_CODEX.md`, `SOVEREIGN_MANDATES.md`, `AGENTS.md`

---

## §2 Research Job Design Framework

### 2.1 The Research Job Specification Template (YAML)

Every research job **must** begin with a complete specification following this template:

```yaml
job_id: "research-{domain}-{date}-{seq}"
title: "Descriptive title (max 80 chars)"
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
  primary_sources: [list of authoritative sources per sub-question]
  credibility_tiers:
    high: [peer-reviewed, official docs, government standards]
    medium: [industry reports, expert blogs, reputable news]
    low: [forums, unverified blogs, social media]
  cross_reference_minimum: 2  # independent sources per claim
search_protocol:
  query_formulation: ["specificity_scaling", "multi_perspective", "date_bounded"]
  iteration_rules: "Start authoritative → verify across 2+ sources → note contradictions → track all sources"
  tool_budget:
    max_search_calls_per_subquestion: 5
    stop_after_diminishing_returns: 3
synthesis_techniques: ["thematic_grouping", "timeline_construction", "stakeholder_mapping", "comparative_matrix", "evidence_pyramid"]
quality_gates:
  completeness_check: "All sub-questions answered? Gaps marked [UNVERIFIED]?"
  bias_detection: "Source bias checklist applied?"
  citation_audit: "Every factual claim cited? URLs verifiable?"
  contradiction_flag: "Conflicting sources surfaced with attribution?"
  mandate_cross_check: "Aligns with mapped mandates (M5, M11, M14, M17, M21)?"
  heritage_tag_validation: "Any heritage tags in output have vet records?"
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

### 2.2 Acceptance Checks (Definition of Done)

Before writing a single word of research, define **verifiable acceptance checks**:

| Check Type | Example | Verification Method |
|------------|---------|---------------------|
| **Existence** | `docs/research/R_GAP001_SPEC.md` exists | `ls -la docs/research/R_GAP001_SPEC.md` |
| **Technical Validity** | GBNF grammar schema validates against llama.cpp parser | `llama-gguf-validate --grammar specs/grammar.gbnf` |
| **Algorithmic Correctness** | Chunking algorithm includes boundary handling for semantic coherence | Code review of specification |
| **Decision Matrix** | Refine vs Map-Reduce includes criteria, benchmarks (or TBD), fallback logic | Specification review |
| **Resource Budget** | Token budget table: per-session, per-entity, per-proposal, quota integration | Specification review |
| **API Specification** | Session hook API: trigger types, payload schema, response codes | Specification review |
| **Error Handling** | Covers partial output, retry logic (max 3, exp backoff), dead letter queue | Specification review |
| **Output Format** | Output schema: proposed_lessons.yaml extension, ID format, conflict resolution | Specification review |
| **Integration Points** | Documented: C-10.5 quota tracker, M21 contract tests, M14 heritage vet trigger | Specification review |
| **Citation Discipline** | Every claim cited [1], [2] + URLs; primary vs secondary distinguished | Citation audit |
| **Doc Standards** | `make doc-llm-validate` passes | CI check |
| **Contract Tests** | For code deliverables: `tests/unit/test_*.py` with `isinstance(result, ExpectedType)` | `make test` |
| **Living Spec** | Spec versioned; incidents trigger spec updates, not just implementation fixes | Git history review |

### 2.3 The Spec-First Workflow

1. **Write the Research Job Spec** (this template) → Save as `docs/research/specs/JOB_ID_Job_Spec.md`
2. **Define Acceptance Checks First** (before any search)
3. **Human Review/Approval** of spec (Kali/MaKaLi/Verity as appropriate)
4. **Execute** according to spec (no deviations without spec update)
5. **Verify Against Acceptance Checks** (all must pass)
6. **Incorporate Feedback** → Update spec (living principle), not just implementation

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ trc_research_bp_kb ⬡ 2026-07-22*
*This is Part 1 of 8. Continue to Part 2 for Research Job Design Framework details.*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_research_bp_kb | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
