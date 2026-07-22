# 🔱 Research Job Spec: GAP-007 — Heritage Vetting for Promoted L3 Principles
**AP Token**: `AP-GAP007-HERITAGE-VET-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ trc_gap007_heritage ⬡ 2026-07-22

---

## §0 Research Job Spec (Per §1.5 Template)

```yaml
job_id: "research-heritage-vet-soul-promotion-20260722-001"
title: "Heritage Vetting Process for Soul.yaml Promoted L3 Principles"
core_question: "What is the complete, automatable heritage vetting process that must be triggered when a proposal is promoted to soul.yaml, ensuring M14 compliance for every promoted directive?"
sub_questions:
  - "What is the exact vet record schema required for soul promotion (extending HERITAGE_VET_LOG.md)?"
  - "Can Scribe auto-generate vet record templates from proposal heritage_tags? What fields require human input?"
  - "How is 'scope declaration: This tag applies to X, NOT to Y' enforced programmatically?"
  - "What is the Qualification Gate algorithm: 'Cannot be justified WITHOUT citing original hardware constraint' — how to verify programmatically?"
  - "What is the 7/10 scoring rubric? Breakdown by criteria?"
  - "How does CI integration work: `make heritage-vet` blocks promotion if vet record missing/incomplete?"
  - "What is the end-to-end flow: Scribe promotion → vet trigger → review → approval → soul.yaml commit?"
scope:
  breadth: "domain-specific (Omega Engine heritage vetting)"
  timeframe: "current_state"
  depth_level: "detailed_analysis"
output_requirements:
  format: "full_report"
  audience: "technical"
  citation_style: "inline"
  sections:
    - "vet_record_schema_v2"
    - "auto_generation_design"
    - "scope_declaration_enforcement"
    - "qualification_gate_algorithm"
    - "scoring_rubric"
    - "ci_integration_design"
    - "end_to_end_flow"
source_strategy:
  primary_sources:
    - "docs/strategy/HERITAGE_VETTING_PIPELINE.md"
    - "data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md"
    - "CREDITS.md"
    - "SOVEREIGN_MANDATES.md §M14"
    - "Omega Engine heritage tag taxonomy"
  credibility_tiers:
    high:
      - "Omega internal heritage vetting pipeline"
      - "Doom_Guy vet log records"
      - "M14 mandate text"
    medium:
      - "id Software historical documentation"
      - "Software heritage attribution best practices"
    low:
      - "General attribution discussions"
  cross_reference_minimum: 2
search_protocol:
  query_formulation:
    - "specificity_scaling"
    - "multi_perspective"
    - "date_bounded"
  iteration_rules: "Start with Omega internal sources → verify against id Software historical records → note contradictions"
  tool_budget:
    max_search_calls_per_subquestion: 3
    stop_after_diminishing_returns: 2
synthesis_techniques:
  - "thematic_grouping"
  - "comparative_matrix"  # vet record fields: current vs proposed
  - "evidence_pyramid"
quality_gates:
  completeness_check: "All 7 sub-questions answered with implementable specifications"
  bias_detection: "Source bias checklist applied"
  citation_audit: "Every technical claim cited with URL"
  contradiction_flag: "Conflicting approaches surfaced"
  mandate_cross_check: "Aligns with M14, M5, M11, M21"
  heritage_tag_validation: "All heritage tags in output have vet records"
stopping_conditions:
  - "All sub-questions resolved to detailed_analysis depth"
  - "Diminishing returns: 2 consecutive searches yield no new high-credibility info"
escalation_triggers:
  - "Qualification Gate cannot be programmatically verified"
  - "Scope declaration enforcement requires human-in-loop for all cases"
  - "Scoring rubric too subjective for automation"
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

| # | Acceptance Check | Verification Method |
|---|------------------|---------------------|
| 1 | `docs/strategy/HERITAGE_VET_FOR_SOUL_PROMOTION.md` exists | `ls -la docs/strategy/HERITAGE_VET_FOR_SOUL_PROMOTION.md` |
| 2 | Vet record schema v2 defined (YAML/JSON Schema) with all required fields | Schema validation test passes |
| 3 | Auto-generation design: which fields from proposal, which require human input | Design review |
| 4 | Scope declaration enforcement: programmatic check design (regex? AST? semantic?) | Design review |
| 5 | Qualification Gate algorithm specified with pseudocode | Code review of algorithm |
| 6 | Scoring rubric: 7/10 threshold with criteria breakdown (weights, examples) | Rubric review |
| 7 | CI integration: `make heritage-vet` blocks promotion on missing/incomplete vet | CI test |
| 8 | End-to-end flow diagram + state machine (promotion → vet → review → approve → commit) | Flow review |
| 9 | Integration points: Scribe promotion gate, Verity review queue, Doom_Guy assignment | Integration test plan |
| 10 | All claims cited with inline citations [1], [2] + URLs | Citation audit |
| 11 | `make doc-llm-validate` passes | CI check |
| 12 | Contract test stubs for vet validator | `tests/unit/test_heritage_vet_soul.py` exists |

---

## §2 Execution Plan

### Phase 0: Spec This Job ✅
- [x] Research Job Spec written
- [x] Acceptance checks defined
- [ ] Human review/approval

### Phase 1: Mine Internal Artifacts
- [ ] Read `HERITAGE_VETTING_PIPELINE.md` → `data/coordination/research_findings/gap007/pipeline.md`
- [ ] Read `HERITAGE_VET_LOG.md` → `.../vet_log_schema.md` (extract current schema)
- [ ] Read `CREDITS.md` → `.../heritage_taxonomy.md` (extract tag taxonomy)
- [ ] Read `SOVEREIGN_MANDATES.md §M14` → `.../m14_text.md`
- [ ] Read 3 new proposals' heritage_tags → `.../proposal_tags.md`
- [ ] **Scratchpad**: Conclusions from each

### Phase 2: External Research
| Sub-Q | Primary Queries | Sources |
|-------|----------------|---------|
| Vet Schema v2 | "software heritage attribution record schema", "provenance metadata schema SPDX", "CycloneDX bill of materials" | SPDX, CycloneDX, SWID |
| Auto-Generation | "automated provenance generation from code annotations", "heritage tag extraction from comments" | GitHub Copilot provenance, Sigstore |
| Scope Declaration | "scope declaration enforcement static analysis", "code annotation scope verification" | Clang tidy, Semgrep, custom AST |
| Qualification Gate | "hardware constraint justification verification", "provenance claim validation algorithm" | Reproducible builds, SLSA |
| Scoring Rubric | "heritage attribution scoring rubric", "provenance quality metrics" | Academic: software heritage, provenance |
| CI Integration | "pre-commit heritage check", "CI gate provenance verification" | GitHub Actions, pre-commit hooks |
| E2E Flow | "promotion pipeline with approval gates", "GitOps promotion with verification" | ArgoCD, Flux, Tekton |

### Phase 3: Synthesis
- [ ] Comparative matrix: current vet log vs proposed v2 schema
- [ ] Evidence pyramid for each design decision
- [ ] Flow diagram with decision points

### Phase 4: QA
- [ ] Completeness, bias, citation, contradiction, mandate, heritage checks

### Phase 5: Draft Deliverable
- [ ] `docs/strategy/HERITAGE_VET_FOR_SOUL_PROMOTION.md`
- [ ] `schemas/heritage_vet_record_v2.yaml`
- [ ] `src/omega/governance/heritage_vet_soul.py` (stub)
- [ ] `tests/unit/test_heritage_vet_soul.py`
- [ ] `.github/workflows/heritage_vet_promotion.yml` (stub)
- [ ] `make doc-llm-validate`

### Phase 6: Review
- [ ] Verity compliance review
- [ ] Doom_Guy heritage review
- [ ] Kali architectural review
- [ ] Incorporate feedback

---

## §3 Context Engineering Rules

| Rule | Implementation |
|------|----------------|
| Write context, don't dump it | Scratchpad in `data/coordination/research_findings/gap007/scratchpad.md` |
| Select context, don't include it | Per sub-question: retrieve only relevant schema/docs |
| Compress at threshold | Every 5 searches → rewrite scratchpad |
| Isolate sub-task contexts | If sub-agents used, fresh context each |
| Assembly order | [system, tools, Omega heritage patterns, retrieved, history, scratchpad, current] |

---

## §4 Tool Descriptions

| Tool | When to Use | When NOT | Output | Limitations |
|------|-------------|----------|--------|-------------|
| `websearch` | SPDX/CycloneDX schemas, provenance standards | Omega internal docs | Markdown + citations | Top 10 |
| `webfetch` | Specific schema files (SPDX GitHub) | Broad queries | Raw content | Single URL |
| `searxng_search` | "provenance quality metrics", "heritage scoring" | Precision specs | JSON snippets | Category dependent |
| `omega-hub_sovereign_search` | "SLSA provenance verification algorithm" | Exploration | Structured | API key |
| `omega-hub_library_discovery_research` | Multi-source synthesis for rubric design | Quick facts | Consolidated report | Slower |
| `think_tool` | **AFTER EVERY SEARCH** | Never skip | Reflection | Mandatory |

---

## §5 Token Budget Estimate

| Phase | Tokens | Notes |
|-------|--------|-------|
| Phase 1 (Internal) | ~4,000 | 5 internal files |
| Phase 2 (External) | ~15,000 | 7 sub-q × 2 searches × ~1,000 |
| Phase 3 (Synthesis) | ~8,000 | Matrix, pyramid, flow |
| Phase 4 (QA) | ~2,000 | Checklists |
| Phase 5 (Drafting) | ~12,000 | Spec + schemas + tests + CI |
| Phase 6 (Review) | ~3,000 | Feedback incorporation |
| **Total** | **~44,000** | Single-agent pattern confirmed |

---

## §6 Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Qualification Gate not programmatically verifiable | High | High | Design human-in-loop fallback; document decision boundary |
| Scope declaration requires semantic analysis | Medium | High | Start with regex/AST pattern; escalate to LLM judge if needed |
| Scoring rubric too subjective | Medium | Medium | Define clear criteria with examples; calibrate with Doom_Guy |
| CI integration blocks legitimate promotions | Low | High | Warning mode first; hard block after calibration period |
| Vet record schema conflicts with SPDX/CycloneDX | Low | Medium | Align with SPDX 2.3+; use standard fields where possible |

---

## §7 Sign-Off

| Role | Name | Approval | Date |
|------|------|----------|------|
| **Researcher (Author)** | @john_carmack | ☐ | 2026-07-22 |
| **Compliance Lead** | @verity | ☐ | |
| **Heritage Lead** | @doom_guy | ☐ | |
| **Architecture Lead** | @kali | ☐ | |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ trc_gap007_heritage ⬡ 2026-07-22*
*Spec lives in `docs/research/specs/GAP007_Heritage_Vet_Job_Spec.md`.*