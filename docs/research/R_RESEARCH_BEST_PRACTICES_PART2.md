# 🔱 Omega Engine Autonomous Agent Research Job Design — Best Practices Guide
**AP Token**: `AP-RESEARCH-BEST-PRACTICES-v2.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ trc_research_bp ⬡ 2026-07-24

---

## §2 Research Job Design Framework

### 2.1 Forensic Context — Why This Framework Exists

Before the research job spec template was standardized, Omega Engine research jobs suffered from:

- **Scope creep**: Research questions expanded mid-execution, causing 40%+ schedule overruns
- **Missed acceptance criteria**: "Done" was subjective → outputs didn't match consumer expectations
- **Source credibility gaps**: Claims from low-credibility sources passed as authoritative
- **Tool budget exhaustion**: Unlimited search calls consumed credits with diminishing returns
- **Spec drift**: Research changed course mid-stream without documentation → lost institutional knowledge
- **Context poisoning**: Raw text dumps replaced structured conclusions → agent confusion

**The Turning Point**: The GEMMA4_WORKHORSE research demonstrated the value of the spec-first approach. Its acceptance checks included explicit TPM measurement targets, source verification requirements, and deliverable format specifications. The result: a directly actionable output that informed C-10.5 quota implementation without rework.

---

### 2.2 The Research Job Specification Template (YAML)

Every research job **must** begin with a complete specification following this template. Fill in every field — missing fields are early warning signs of incomplete scoping.

```yaml
job_id: "research-{domain}-{date}-{seq}"
title: "Descriptive title (max 80 chars)"
origin: "What triggered this research? (e.g., ticket, incident, gap analysis)"
priority: "P0|P1|P2"
campaign_duration: "Estimated days to complete"

core_question: "Single precise sentence restating the research question"
sub_questions: [5-10 specific, searchable sub-questions]
blocking_relationships: ["KG-X: other research this depends on"]
depends_on: ["Research that must complete before this can start"]

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
  protocol_reference: "docs/research/R_SEARCH_TOOL_PROTOCOL_V1.md"
  query_formulation: ["specificity_scaling", "multi_perspective", "date_bounded"]
  tier_hierarchy: "T0 cache → T1 websearch → T2 webfetch → T3 SearXNG → T4 Hub → T5 Firecrawl → T6 Sieve"
  iteration_rules: "Start authoritative → verify across 2+ sources → note contradictions → track all sources"
  tool_budget:
    max_search_calls_per_subquestion: 5
    stop_after_diminishing_returns: 3

confidence_scoring:
  primary_source: {score: 10/10, evidence: "URL + quoted text"}
  authoritative_secondary: {score: 8-9/10, evidence: "URL + context"}
  community_consensus: {score: 6-7/10, evidence: "Multiple corroborating sources"}
  agent_interpretation: {score: 5-6/10, evidence: "Must be verified against primary"}
  uncorroborated: {score: "<5/10", evidence: "DO NOT USE without verification"}

synthesis_techniques: ["thematic_grouping", "timeline_construction", 
  "stakeholder_mapping", "comparative_matrix", "evidence_pyramid"]

quality_gates:
  temple_grade: "make temple-grade passes (M13)"
  doc_standards: "make doc-llm-validate passes (M26)"
  completeness_check: "All sub-questions answered? Gaps marked [UNVERIFIED]?"
  bias_detection: "Source bias checklist applied?"
  citation_audit: "Every factual claim cited? URLs verifiable?"
  confidence_minimum: "All findings >= 6/10 confidence"
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
  - "Confidence minimum not achievable for key findings"

context_engineering:
  system_prompt_slots:
    - role_scope_constraints_stopping
    - tool_descriptions_with_when_when_not
    - planning_prompt_if_gt_5_steps
    - reflection_prompt_on_divergence
  context_assembly_order: [system, tools, long_term_memory, retrieved_knowledge, conversation_history, scratchpad, current_instruction]
  compression_triggers: "50% window → summarize tail; every N turns → rewrite scratchpad"
  isolation: "Sub-agent contexts isolated; only clean results returned to orchestrator"

omega_integration:
  consumer: "Who/what will use the output? (e.g., soul.yaml, heritage vet, mandate compliance)"
  mandate_alignment: [list specific mandates this research supports]
  tool_references: [list specific Omega tools this research will use]
  output_path: "docs/research/R_{DELIVERABLE_ID}.md"
```

---

### 2.3 Filled Example: GEMMA4 Workhorse Research

Here is a concrete example of the template filled in for a real research job:

```yaml
job_id: "research-gemma4-workhorse-20260724"
title: "Gemma 4 Workhorse Restoration & Model Intelligence"
origin: "Gemma 4 free-tier TPM collapsed from 1M to 16K ~2026-07-14, breaking OpenCode sessions"
priority: "P0 — Blocks all cloud inference capacity"
campaign_duration: "2 days"

core_question: "What viable workhorse model(s) can replace Gemma 4 31B for OpenCode sessions after free-tier TPM collapse?"
sub_questions:
  - "What is the current free tier landscape for all major providers (July 2026)?"
  - "Which providers offer 100K+ context windows on free tier?"
  - "How fast is each model for interactive coding sessions?"
  - "What local fallback options exist on Ryzen 5700U?"
  - "What is the effective TPM/RPM ceiling for each candidate?"
# ... more sub-questions

blocking_relationships: []
depends_on: []

scope:
  breadth: "global"
  timeframe: "current"
  depth_level: "comprehensive_report"

output_requirements:
  format: "full_report"
  audience: "technical"
  citation_style: "inline"
  sections: ["executive_summary", "domain_analysis", "comparison_matrices", "recommendations", "local_fallback"]

confidence_scoring:
  # Applied to all findings automatically

search_protocol:
  protocol_reference: "docs/research/R_SEARCH_TOOL_PROTOCOL_V1.md"
  # T0-T6 hierarchy followed

quality_gates:
  temple_grade: true
  doc_standards: true
  completeness_check: true
  citation_audit: true
  confidence_minimum: true
  mandate_cross_check: true

omega_integration:
  consumer: "C-10.5 quota tracker implementation, model routing decisions"
  mandate_alignment: ["M7 Local-First", "M22 Provenance Tracking"]
  tool_references: ["websearch", "webfetch", "SearXNG", "Omega Hub Sovereign Search"]
  
deliverable: "docs/research/R_GEMMA4_WORKHORSE_INTEL_20260724.md"
```

---

### 2.4 Acceptance Checks (Definition of Done)

Before writing a single word of research, define **verifiable acceptance checks**. These are the gates that the output must pass to be considered complete:

| Check Type | Example | Verification Method |
|------------|---------|---------------------|
| **Existence** | `docs/research/R_GAP001_SPEC.md` exists | `ls -la docs/research/R_GAP001_SPEC.md` |
| **Technical Validity** | GBNF grammar schema validates against llama.cpp parser | `llama-gguf-validate --grammar specs/grammar.gbnf` |
| **Algorithmic Correctness** | Chunking algorithm includes boundary handling for semantic coherence | Code review of specification |
| **Decision Matrix** | Refine vs Map-Reduce includes criteria, benchmarks (or TBD), fallback logic | Specification review |
| **Resource Budget** | Token budget table: per-session, per-entity, per-proposal, quota integration | Specification review |
| **API Specification** | Session hook API: trigger types, payload schema, response codes | Specification review |
| **Error Handling** | Covers partial output, retry logic (max 3, exp backoff), dead letter queue | Specification review |
| **Output Format** | Output schema extension, ID format, conflict resolution | Specification review |
| **Integration Points** | Documented: C-10.5 quota tracker, M21 contract tests, M14 heritage vet trigger | Specification review |
| **Citation Discipline** | Every claim cited [1], [2] + URLs; primary vs secondary distinguished | Citation audit |
| **Doc Standards** | `make doc-llm-validate` passes | CI check |
| **Contract Tests** | For code deliverables: `tests/unit/test_*.py` with `isinstance(result, ExpectedType)` | `make test` |
| **Living Spec** | Spec versioned; incidents trigger spec updates, not just implementation fixes | Git history review |
| **Source Confidence** | All findings >= minimum confidence tier | Manual confidence audit |
| **Consumer Verification** | Output matches the format and specificity the consumer requires | Stakeholder review |
| **Acknowledged Gaps** | Any [UNVERIFIED] gaps are explicit with explanation | Spec review |

---

### 2.5 The Spec-First Workflow

1. **Identify Knowledge Gap** — What don't we know that blocks action? → Create gap entry in workbench
2. **Write the Research Job Spec** (this template) → Save as `docs/research/specs/JOB_ID_Job_Spec.md`
3. **Define Acceptance Checks First** (before any search) — Use the table above
4. **Specify Omega Integration** — Who will use this? How does it connect to mandates, tools, systems?
5. **Human Review/Approval** of spec (Kali/MaKaLi/Verity as appropriate)
6. **Execute** according to spec (no deviations without spec update)
7. **Verify Against Acceptance Checks** (all must pass)
8. **Distill Lessons** — What did we learn about the research process itself?
9. **Incorporate Feedback** → Update spec (living principle), not just implementation
10. **Update Hivemind** — Post completion with `intent: decision` for team awareness

---

### 2.6 Common Mistakes and How to Avoid Them

| Mistake | Symptom | Fix |
|---------|---------|-----|
| **Missing blocking relationships** | Research concludes, discovers it depends on another unstarted job | Map dependencies explicitly in `depends_on` field |
| **Vague output requirements** | Consumer says "this isn't what I needed" | Specify concrete `sections` and `output_requirements` |
| **No confidence scoring** | Findings accepted at face value, later found to be from low-credibility sources | Mandate confidence tiers in spec |
| **Missing consumer** | Beautiful report sits unused | Specify `omega_integration.consumer` and output structure |
| **No stopping conditions** | Research continues past diminishing returns indefinitely | Define explicit `stopping_conditions` with thresholds |
| **No escalation triggers** | Research hits unresolvable contradiction, stalls | Define `escalation_triggers` with clear escalation path |
| **Context isolation violations** | Sub-agent context poisoning contaminates synthesizer | Enforce `context_engineering.isolation: true` |
| **No mandate alignment** | Research output violates or ignores mandates | Fill required mandates in `omega_integration.mandate_alignment` |

---

### 2.7 Cross-Reference: How This Connects to Other Parts

| Part | Connection | How to Use Together |
|------|------------|---------------------|
| **PART1 — Core Principles** | The spec template implements spec-driven, context-engineered, quality-gated principles | Read PART1 first to understand the "why", then use this template for the "how" |
| **PART3 — Context Engineering Rules** | The `context_engineering` section references 7 context slots, 5 techniques | Use PART3 to fill in the context engineering section of the spec |
| **PART4 — Tool Design Principles** | The `tool_budget` constraints are based on tool descriptions from PART4 | Use PART4 to refine tool choices and budgets in the spec |
| **PART5 — Execution Patterns** | The `sub_questions` count informs single-loop vs deep agent decision | Use PART5 to determine execution pattern based on scope and sub-questions |
| **PART6 — Quality Gates** | The `quality_gates` section maps to the multilayered system in PART6 | Use PART6 to verify all quality gates are specified in the spec |

---

### 2.8 Research Job Lifecycle Integration

```
GAP IDENTIFIED
    │
    ▼
JOB SPEC WRITTEN ←── Fills template from this section
    │
    ▼
SPEC REVIEWED BY HUMAN ←── If unsure, start at autonomy level 0
    │
    ▼
RESEARCH EXECUTED ←── Following context engineering rules (PART3)
    │
    ▼
OUTPUT VERIFIED ←── Against acceptance checks (this section)
    │
    ▼
OUTPUT DELIVERED ←── To specified consumer (omega_integration.consumer)
    │
    ▼
LIVING SPEC UPDATED ←── With lessons learned from this cycle
    │
    ▼
GAP CLOSED ←── Or escalated if unresolvable
```

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ RESEARCH-BEST-PRACTICES ⬡ v2.0.0 ⬡ 2026-07-24*
*Part 2/6: Research Job Design Framework — Enhanced with filled example, common mistakes, and cross-references*
*This guide is a living document. Updates must be made via PR with spec-driven changes.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_research_bp | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
