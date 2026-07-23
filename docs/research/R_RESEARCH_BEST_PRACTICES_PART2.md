# 🔱 Omega Engine Autonomous Agent Research Job Design — Best Practices Guide
**AP Token**: `AP-RESEARCH-BEST-PRACTICES-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ trc_research_bp ⬡ 2026-07-22

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

*⬡ OMEGA ⬡ RESEARCHER ⬡ trc_research_bp ⬡ 2026-07-22*
*Part 2/8: Research Job Design Framework*