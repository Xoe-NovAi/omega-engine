# 🔱 Research Job Spec: GAP-001 — Scribe Agent L1→L2→L3 Distillation Pipeline
**AP Token**: `AP-GAP001-SCRIBE-SPEC-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ trc_gap001_scribe ⬡ 2026-07-22

---

## §0 Job Specification (Per §1.5 Template)

```yaml
job_id: "research-gap001-scribe-distillation-20260722-001"
title: "Scribe Agent L1→L2→L3 Distillation Pipeline Specification"
core_question: "What is the complete implementation specification for the Scribe Agent's L1→L2→L3 distillation pipeline, including GBNF grammar, chunking algorithm, Refine vs Map-Reduce decision matrix, token budgeting, session hook API, error handling, and output format for proposed_lessons.yaml?"

sub_questions:
  - "What is the exact llama.cpp GBNF grammar schema for extracting L1 (Narrative), L2 (Insight), L3 (Universal Principle) from session transcripts?"
  - "What is the precise sliding window chunking algorithm (4k tokens, 500 overlap) for semantic coherence across session boundaries?"
  - "What is the decision matrix for Refine (sequential) vs Map-Reduce (parallel) distillation approaches? When to use each? Benchmarks?"
  - "What is the estimated token cost per session distillation (input, L1, L2, L3 outputs)? Per entity? Per proposal?"
  - "How does the distillation trigger? Post-session hook? Manual invocation? Scheduled batch? What is the exact API?"
  - "What happens when distillation fails? Partial output? Retry logic? Dead letter queue for failed sessions?"
  - "What is the exact YAML structure for proposed_lessons.yaml append? How are proposal IDs generated? Conflict resolution?"

scope:
  breadth: "domain-specific"  # Omega Engine soul.yaml enhancement
  timeframe: "current"  # Implementation for C-0.5 sprint
  depth_level: "comprehensive_report"  # Full implementation spec required

output_requirements:
  format: "full_report"  # SPEC_Scribe_Distillation_Pipeline.md
  audience: "technical"  # Ma'at/P3 engineering, Verity compliance, Kali architecture
  citation_style: "inline"
  sections:
    - "Executive Summary"
    - "GBNF Grammar Schema (complete with field definitions, validation rules, examples)"
    - "Chunking Algorithm Specification (sliding window, boundary handling, semantic coherence)"
    - "Refine vs Map-Reduce Decision Matrix (criteria, benchmarks, fallback)"
    - "Token Budget Specification (per session, per entity, per proposal, quota integration)"
    - "Session Hook API (trigger mechanisms, payload, response, error codes)"
    - "Error Handling & Retry Logic (partial output, dead letter queue, alerting)"
    - "Output Format Specification (proposed_lessons.yaml schema, ID generation, conflict resolution)"
    - "Integration Points (C-10.5 quota tracker, M21 contract tests, M14 heritage vet)"
    - "Acceptance Criteria (verifiable checks for each component)"

source_strategy:
  primary_sources:
    - "docs/sprints/guard-and-distill/02-p0-tickets/C-0.5-scribe-agent.md"
    - "docs/research/R_GUARD_DISTILL_RESEARCH_GUIDE_20260722.md §Domain 5"
    - "data/coordination/RESEARCH_INSIGHTS_FOR_SOUL_UPGRADE.md"
    - "llama.cpp GBNF grammar documentation (official)"
    - "llama.cpp distillation/finetuning examples"
    - "LangChain/LangGraph distillation patterns"
    - "Anthropic context engineering patterns for long-context processing"
  credibility_tiers:
    high:
      - "Official llama.cpp documentation and examples"
      - "Omega Engine internal research (R_GUARD_DISTILL)"
      - "Anthropic engineering blog posts"
    medium:
      - "LangChain/LangGraph documentation"
      - "Community distillation implementations"
    low:
      - "Forum discussions, blog posts without benchmarks"
  cross_reference_minimum: 2

search_protocol:
  query_formulation:
    - "specificity_scaling"
    - "multi_perspective"
    - "date_bounded"
  iteration_rules: "Start authoritative (llama.cpp docs, Omega internal) → verify across 2+ sources → note contradictions → track all sources"
  tool_budget:
    max_search_calls_per_subquestion: 5
    stop_after_diminishing_returns: 3

synthesis_techniques:
  - "thematic_grouping"
  - "comparative_matrix"  # Refine vs Map-Reduce
  - "evidence_pyramid"

quality_gates:
  completeness_check: "All 7 sub-questions answered with verifiable specifications"
  bias_detection: "Source bias checklist applied (llama.cpp official = high, community = medium)"
  citation_audit: "Every technical claim cited with URL"
  contradiction_flag: "Conflicting approaches surfaced with attribution"
  mandate_cross_check: "Aligns with M5, M11, M14, M17, M21"
  heritage_tag_validation: "Any heritage tags in output have vet records"

stopping_conditions:
  - "All sub-questions resolved to comprehensive_report depth"
  - "Token budget exhausted (if applicable)"
  - "Diminishing returns: 3 consecutive searches yield no new high-credibility info"

escalation_triggers:
  - "GBNF grammar cannot be validated against llama.cpp schema"
  - "Token budget estimates vary >50% across sources"
  - "Refine vs Map-Reduce benchmarks unavailable for target hardware (Ryzen 5700U)"

context_engineering:
  system_prompt_slots:
    - "role_scope_constraints_stopping"
    - "tool_descriptions_with_when_when_not"
    - "planning_prompt_if_gt_5_steps"
    - "reflection_prompt_on_divergence"
  context_assembly_order: ["system", "tools", "long_term_memory", "retrieved_knowledge", "conversation_history", "scratchpad", "current_instruction"]
  compression_triggers: "50% window → summarize tail; every 5 turns → rewrite scratchpad"
  isolation: "Sub-agent contexts isolated; only clean results returned to orchestrator"
```

---

## §1 Acceptance Checks (Definition of Done)

The research job is **complete** when ALL of the following are verifiably true:

| # | Acceptance Check | Verification Method |
|---|------------------|---------------------|
| 1 | `docs/specs/SPEC_Scribe_Distillation_Pipeline.md` exists | `ls -la docs/specs/SPEC_Scribe_Distillation_Pipeline.md` |
| 2 | GBNF grammar schema is complete, valid llama.cpp syntax, includes all 3 L1/L2/L3 fields with validation rules | `llama-gguf-validate --grammar specs/grammar.gbnf` (or equivalent) |
| 3 | Chunking algorithm specified with pseudocode + boundary handling for semantic coherence | Code review of specification |
| 4 | Refine vs Map-Reduce decision matrix includes: criteria, benchmarks (or "TBD: benchmark on Ryzen 5700U"), fallback logic | Specification review |
| 5 | Token budget table: per-session input/output, per-entity, per-proposal, C-10.5 quota integration points | Specification review |
| 6 | Session hook API documented: trigger types, payload schema, response codes, error handling | Specification review |
| 7 | Error handling covers: partial output, retry (max 3, exponential backoff), dead letter queue location, alerting | Specification review |
| 8 | Output format: proposed_lessons.yaml schema extension, proposal ID format (proposal-YYYYMMDD-NNN), conflict resolution (last-write-wins with audit) | Specification review |
| 9 | Integration points documented: C-10.5 quota tracker API, M21 contract test patterns, M14 heritage vet trigger | Specification review |
| 10 | All claims cited with inline citations [1], [2] + URLs; primary vs secondary distinguished | Citation audit |
| 11 | `make doc-llm-validate` passes on the spec document | CI check |
| 12 | Contract test stubs provided for each component (M21) | `tests/unit/test_scribe_distillation.py` exists with `isinstance` checks |

---

## §2 Execution Plan

### Phase 0: Spec This Job ✅ (This Document)
- [x] Research Job Spec written (this file)
- [x] Acceptance checks defined
- [ ] Human review/approval of spec

### Phase 1: Mine Internal Artifacts (Context Engineering)
- [ ] Read `C-0.5-scribe-agent.md` → extract findings to `data/coordination/research_findings/gap001/scribe_ticket.md`
- [ ] Read `R_GUARD_DISTILL_RESEARCH_GUIDE_20260722.md §Domain 5` → extract to `.../domain5_findings.md`
- [ ] Read `RESEARCH_INSIGHTS_FOR_SOUL_UPGRADE.md` → extract L1→L2→L3 format reference to `.../l1_l2_l3_format.md`
- [ ] Read current `proposed_lessons.yaml` → extract schema to `.../current_proposals_schema.md`
- [ ] Read `soul.yaml` v6.4 → extract directive structure to `.../soul_v64_structure.md`
- [ ] **Scratchpad**: Write conclusions from each, not raw text

### Phase 2: External Research (Systematic Search)
Per sub-question, execute with tool budget discipline:

| Sub-Q | Primary Search Queries | Authoritative Sources |
|-------|------------------------|----------------------|
| GBNF Grammar | "llama.cpp GBNF grammar schema example", "llama.cpp structured output grammar", "GBNF schema validation llama.cpp" | llama.cpp GitHub docs, examples/grammar/ |
| Chunking | "sliding window chunking 4k tokens 500 overlap semantic coherence", "long context distillation chunking strategy llama.cpp" | Anthropic context engineering, LangChain text splitters |
| Refine vs Map-Reduce | "Refine vs Map-Reduce distillation LLM", "sequential vs parallel distillation benchmark", "LangChain Refine chain MapReduce chain comparison" | LangChain docs, Anthropic research |
| Token Budget | "llama.cpp token estimation distillation", "token budget planning LLM distillation", "C-10.5 quota tracker integration" | Omega C-10.5 research, llama.cpp tokenization |
| Session Hook | "post-session hook agent distillation", "session end trigger automatic processing", "Omega Engine session hook architecture" | Omega AGENTS.md, hivemind protocol |
| Error Handling | "dead letter queue LLM pipeline", "partial output retry logic distillation", "distillation failure handling" | LangGraph error handling, production LLM patterns |
| Output Format | "proposed_lessons.yaml schema", "proposal ID generation scheme", "YAML conflict resolution last write wins" | Omega current format, YAML best practices |

### Phase 3: Synthesis & Analysis
- [ ] Apply thematic grouping to organize findings
- [ ] Build comparative matrix for Refine vs Map-Reduce
- [ ] Construct evidence pyramid for each technical claim
- [ ] Structure output per required sections

### Phase 4: Quality Assurance
- [ ] Completeness check: all 7 sub-questions answered
- [ ] Bias detection: source credibility applied
- [ ] Citation audit: every claim cited, URLs verifiable
- [ ] Contradiction flag: conflicts surfaced
- [ ] Mandate cross-check: M5, M11, M14, M17, M21 alignment
- [ ] Heritage tag validation: any tags have vet records

### Phase 5: Draft Deliverable
- [ ] Write `docs/specs/SPEC_Scribe_Distillation_Pipeline.md`
- [ ] Include machine-readable artifacts: `specs/grammar.gbnf`, `schemas/proposed_lessons_v2.yaml`
- [ ] Write contract test stubs: `tests/unit/test_scribe_distillation.py`
- [ ] Run `make doc-llm-validate`

### Phase 6: Review & Iterate
- [ ] Kali/MaKaLi architectural review
- [ ] Verity compliance review
- [ ] Incorporate feedback → update spec (living spec principle)

---

## §3 Context Engineering Rules for This Job

| Rule | Implementation |
|------|----------------|
| **Write context, don't dump it** | Scratchpad files in `data/coordination/research_findings/gap001/scratchpad.md` — conclusions only |
| **Select context, don't include it** | Per sub-question: retrieve only relevant sources; don't dump all llama.cpp docs |
| **Compress at threshold** | Every 5 search iterations → rewrite scratchpad to keep only load-bearing conclusions |
| **Isolate sub-task contexts** | If spawning sub-agents via `task()`, each gets fresh context; returns only clean result |
| **Assembly order** | [system, tools, long-term memory (Omega patterns), retrieved knowledge, conversation history, scratchpad, current sub-question] |

---

## §4 Tool Descriptions for This Job

| Tool | When to Use | When NOT to Use | Output Format | Limitations |
|------|-------------|-----------------|---------------|-------------|
| `websearch` | Broad queries, finding official docs, recent benchmarks | Deep technical specs, schema validation | Markdown with citations | Limited to top 10 results |
| `webfetch` | Fetching full llama.cpp grammar docs, specific GitHub files | When snippet suffices | Raw HTML/markdown | Single URL per call |
| `searxng_search` | Semantic search for "distillation patterns", "chunking strategies" | Precision technical specs | JSON with snippets | Category/engine dependent |
| `omega-hub_sovereign_search` | Precision seeds: "llama.cpp GBNF grammar official documentation" | Broad exploration | Structured results | Requires API key |
| `omega-hub_library_discovery_research` | Deep research with citations for multi-source synthesis | Quick fact checks | Consolidated report | Slower, higher token cost |
| `think_tool` | **AFTER EVERY SEARCH** — reflect: key info, missing, enough?, continue? | Never skip | Structured reflection | Mandatory per protocol |

---

## §5 Token Budget Estimate (Pre-Research)

| Phase | Estimated Tokens | Notes |
|-------|------------------|-------|
| Phase 1 (Internal Mining) | ~5,000 | Reading 5-6 internal files |
| Phase 2 (External Search) | ~25,000 | 7 sub-questions × ~3 searches × ~1,200 tokens |
| Phase 3 (Synthesis) | ~10,000 | Structured analysis, matrix building |
| Phase 4 (QA) | ~3,000 | Checklist verification |
| Phase 5 (Drafting) | ~15,000 | Writing spec + artifacts + tests |
| Phase 6 (Review) | ~5,000 | Incorporating feedback |
| **Total** | **~63,000** | Within single-agent budget; no deep-agent pattern needed |

**Decision Rule Check**: ~7 sub-questions, tightly coupled (all about one pipeline), <15 steps → **Single research agent pattern** (not deep-agent). Confirmed.

---

## §6 Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| GBNF grammar invalid for llama.cpp | Medium | High | Validate against llama.cpp schema before finalizing; test with `llama-gguf-validate` |
| Token estimates vary >50% | High | Medium | Document range; use conservative (high) estimate for quota reservation; flag for benchmarking |
| Refine vs Map-Reduce benchmarks unavailable for Ryzen 5700U | High | Medium | Specify "TBD: benchmark on target hardware"; provide decision matrix for when benchmarks exist |
| C-10.5 quota API not finalized | Medium | High | Document integration points as interfaces; coordinate with Ma'at/P3 on C-10.5 timeline |
| Heritage vet integration unclear | Low | Medium | Coordinate with Verity/Doom_Guy; specify trigger as "on promotion gate entry" |

---

## §7 Sign-Off

| Role | Name | Approval | Date |
|------|------|----------|------|
| **Researcher (Author)** | @john_carmack | ☐ | 2026-07-22 |
| **Engineering Lead** | @maat (P3) | ☐ | |
| **Compliance Lead** | @verity | ☐ | |
| **Architecture Lead** | @kali | ☐ | |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ trc_gap001_scribe ⬡ 2026-07-22*
*This spec is the contract. Execution follows the spec. Spec lives in `docs/research/specs/GAP001_Scribe_Distillation_Job_Spec.md`.*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_gap001_scribe | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
