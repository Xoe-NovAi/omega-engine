# 🔱 Omega Engine Autonomous Agent Research Job Design — Best Practices Guide
**AP Token**: `AP-RESEARCH-BEST-PRACTICES-KB-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ trc_research_bp_kb ⬡ 2026-07-22

---

## Appendix A: Quick Reference Cheat Sheet

### A.1 Research Job Spec Template (Minimal Version)
```yaml
job_id: "research-{domain}-{date}-{seq}"
title: "Descriptive title"
core_question: "Single precise sentence"
sub_questions: [5-10 specific questions]
scope:
  breadth: "domain-specific"
  timeframe: "current"
  depth_level: "detailed_analysis"
output_requirements:
  format: "full_report"
  audience: "technical"
  citation_style: "inline"
  sections: ["Executive Summary", "Details", "Conclusion"]
source_strategy:
  primary_sources: [authoritative sources]
  credibility_tiers:
    high: [peer-reviewed, official docs]
    medium: [industry reports, expert blogs]
    low: [forums, unverified blogs]
  cross_reference_minimum: 2
search_protocol:
  query_formulation: ["specificity_scaling", "multi_perspective", "date_bounded"]
  iteration_rules: "Start authoritative → verify across 2+ sources → note contradictions"
  tool_budget:
    max_search_calls_per_subquestion: 5
    stop_after_diminishing_returns: 3
synthesis_techniques: ["thematic_grouping", "comparative_matrix", "evidence_pyramid"]
quality_gates:
  completeness_check: "All sub-questions answered? Gaps marked [UNVERIFIED]?"
  bias_detection: "Source bias checklist applied?"
  citation_audit: "Every factual claim cited? URLs verifiable?"
  contradiction_flag: "Conflicting sources surfaced with attribution?"
  mandate_cross_check: "Aligns with mapped mandates (M5, M11, M14, M17, M21)?"
  heritage_tag_validation: "Any heritage tags in output have vet records?"
stopping_conditions:
  - "All sub-questions resolved to target depth"
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
  compression_triggers: "50% window → summarize tail; every 5 turns → rewrite scratchpad"
  isolation: "Sub-agent contexts isolated; only clean results returned to orchestrator"
```

### A.2 Context Engineering Quick Reference

| Technique | What to Do | What NOT to Do |
|-----------|------------|----------------|
| Write Context | "Key finding: [conclusion]. Source: [URL]" | Paste raw text/content |
| Select Context | Retrieve only relevant subset | Dump all tools/memory/context |
| Compress | Summarize history >50%; rewrite scratchpad every 5 turns | Let context grow unchecked |
| Isolate Sub-Agents | Fresh context per sub-task; clean results only | Share state between sub-agents |
| Progressive Retrieval | Try snippets first → full page only if needed | Always fetch full pages |

### A.3 Tool Description Contract (5 Elements)
1. **What**: One sentence, direct
2. **When to use**: Specific conditions/triggers
3. **When NOT to use**: Explicit exclusions
4. **Output format**: Helps model interpret results
5. **Limitations**: Known failure modes/constraints

### A.4 Execution Pattern Selection

| Complexity | Pattern | When to Use |
|------------|---------|-------------|
| Low (<15 steps, tightly coupled) | Single-loop | Focused analysis, estimation, validation |
| Medium (15-25 steps, some separable) | Single-loop + context engineering | Technical specs, comparative analysis |
| High (>25 steps, separable sub-tasks) | Deep Agent | Architectural decisions, comprehensive reviews |
| Strategic (high stakes, irreversible) | Collaborative Planning | Governance policies, framework designs |

### A.5 Quality Gate Checklist (Pre-Delivery)
- [ ] All sub-questions answered? Gaps marked [UNVERIFIED]?
- [ ] Source bias checklist applied?
- [ ] Every factual claim cited? URLs verifiable?
- [ ] Conflicting sources surfaced with attribution?
- [ ] Aligns with mapped mandates (M5, M11, M14, M17, M21)?
- [ ] Any heritage tags in output have vet records?
- [ ] `make doc-llm-validate` passes
- [ ] For code: `tests/unit/test_*.py` with `isinstance(result, ExpectedType)`
- [ ] Manual review: Mandate alignment, source rigor, contrast handling

### A.6 Red Flags (Stop and Reassess)
- Vague spec like "Research LLMs for improvement"
- Pasting entire documents/logs into context
- Relying on single source for critical info
- Treating research as binary success/failure
- Never updating spec based on learning
- Conducting research without stakeholder input
- Using tools incorrectly (wrong tool for job)
- Skipping quality gates to "move faster"
- Applying same approach to all problems
- Focusing only on output, ignoring process

### A.7 Green Flags (Keep Doing This)
- Spec written backward from acceptance checks
- Conclusions written, not raw text dumped
- Specific, targeted queries with date bounds
- Cross-referencing claims across 2+ sources
- Using evidence pyramid for source evaluation
- Treating spec as living document
- Involving stakeholders early (especially for complex jobs)
- Using correct tool for job (read when/when-not)
- Enforcing all quality gates as non-negotiable
- Matching approach to problem type (use decision tree)
- Valuing both output and process; conducting AARs

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ trc_research_bp_kb ⬡ 2026-07-22*
*This cheat sheet summarizes the key points from the full 8-part guide.*
*For full details, refer to the complete guide in parts 1-8.*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_research_bp_kb | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
