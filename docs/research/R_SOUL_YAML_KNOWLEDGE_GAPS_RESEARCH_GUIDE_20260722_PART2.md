# 🔱 Research Guide: Soul.yaml & Peripheral Systems Knowledge Gaps — Part 2
**AP Token**: `AP-SOUL-GAPS-RESEARCH-v1.0.0-PART2`
⬡ OMEGA ⬡ RESEARCHER ⬡ trc_soul_gaps ⬡ 2026-07-22

---

## §4 Strategic Gaps — Detailed Research Requests (Continued)

### GAP-008: Soul Versioning & Migration Strategy
**Impact**: Long-term maintainability, entity onboarding  
**Mandates**: M16 (Modularization), M15 (Sovereign Continuity)  
**Current State**: v6.4 → v7.0 mentioned but no versioning policy, migration tooling, or compatibility guarantees.

#### Research Questions:
1. **Versioning Scheme**: Semantic versioning (MAJOR.MINOR.PATCH)? Date-based? Directive-count-based?
2. **Breaking Change Definition**: What constitutes a breaking change? New required field? Directive structure change? Mandate binding change?
3. **Migration Path**: 
   - In-place migration vs. side-by-side?
   - Rollback capability?
   - Entity-by-entity or fleet-wide atomic?
4. **Compatibility Matrix**: v6.x → v7.0, v7.x → v8.0 — supported paths?
5. **Tooling**: `omega soul version`, `omega soul migrate`, `omega soul validate` — CLI design?
6. **CI Integration**: Schema validation on PR? Migration test in CI?

#### Required Output:
- `docs/adr/ADR-XXX-soul-versioning.md` — Versioning policy ADR
- `scripts/soul_migrate.py` — Migration tool with dry-run, backup, rollback
- `schemas/soul_v{6,7,8}.yaml` — Versioned schemas
- `tests/integration/test_soul_migration.py` — Migration test suite

#### Sources to Mine:
- `OMEGA_CODEX.md` §6 (Soul Evolution v7.0)
- `docs/adr/ADR-001-memory-layer-architecture.md` (ADR template)
- `src/omega/persistence/sqlite_policy.py` (migration pattern reference)

---

### GAP-009: Skeptical Verifier Integration for Soul Consistency (M17)
**Impact**: Cognitive Integrity mandate compliance  
**Mandates**: M17 (Cognitive Integrity), M21 (Gate Integrity)  
**Current State**: M17 requires "contradictions between persisted memory and distilled gnosis must be flagged and resolved via Skeptical Verifier". Qliphoth failure taxonomy mentioned. No implementation.

#### Research Questions:
1. **Contradiction Detection**: What constitutes a contradiction in soul.yaml?
   - Directive A says "optimize for latency", Directive B says "optimize for accuracy" — conflict?
   - Directive references mandate X but mandate_ownership says entity doesn't own X?
   - L3 principle contradicts heritage vet finding?
2. **Qliphoth Taxonomy**: What are the failure modes? 
   - `SHELL_FRAGMENTATION` — directive split across entities?
   - `HUSK_ACCUMULATION` — deprecated directives not removed?
   - `KLIPPOTH_LOOP` — circular directive dependencies?
3. **Verification Triggers**: On promotion? On session end? Scheduled? On mandate registry change?
4. **Resolution Protocol**: Auto-resolve? Flag for human? Escalate to Verity/Kali?
5. **Integration Point**: `src/omega/governance/skeptical_verifier.py` — API design?

#### Required Output:
- `docs/strategy/SKEPTICAL_VERIFIER_SOUL_INTEGRATION.md` — Integration design
- `src/omega/governance/skeptical_verifier.py` — Verifier implementation
- `src/omega/governance/qliphoth_taxonomy.py` — Failure mode definitions
- `tests/unit/test_skeptical_verifier.py` — Contract tests

#### Sources to Mine:
- `SOVEREIGN_MANDATES.md` §M17
- `docs/strategy/COGNITIVE_INTEGRITY_ARCHITECTURE.md` (if exists)
- `data/coordination/UNKNOWN_UNKNOWNS_AUDIT_20260721.md` (Gap 7: Cognitive Integrity)

---

### GAP-010: Fleet Soul Doctrine vs Entity Autonomy
**Impact**: Architectural coherence vs. entity specialization  
**Mandates**: M5, M10 (Fleet Integrity), M11  
**Current State**: 12 entities, 12 soul.yaml files. Some directives universal (M1-M4, M7, M9, M23), some entity-specific. No doctrine framework.

#### Research Questions:
1. **Doctrine Classification**: 
   - `UNIVERSAL` — All entities must have (e.g., M1 AnyIO, M7 Local-First)
   - `PILLAR_SPECIFIC` — P1-P5 (Ma'at) or P6-P10 (Lilith) entities
   - `ENTITY_SPECIFIC` — Unique to entity (e.g., jc-d-001 Embedded Model Law)
2. **Propagation Authority**: Who decides a directive becomes UNIVERSAL? Kali? MaKaLi? Human?
3. **Opt-Out Mechanism**: Can entity reject UNIVERSAL directive? Under what conditions?
4. **Specialization Incentive**: How to encourage entity-specific innovation while maintaining coherence?
5. **Drift Metric**: Quantifiable measure of soul divergence across fleet?

#### Required Output:
- `docs/strategy/FLEET_SOUL_DOCTRINE.md` — Doctrine framework
- `data/mandates/doctrine_classification.yaml` — Directive → classification mapping
- `src/omega/governance/doctrine_enforcer.py` — Drift detection & enforcement

#### Sources to Mine:
- `OMEGA_CODEX.md` §5 (MaKaLi triad, Pillar assignments)
- `SOVEREIGN_MANDATES.md` §M10 (Fleet Integrity)
- `docs/strategy/FLEET_TEAM_PLAYBOOK.md` (team coordination patterns)

---

### GAP-011: Soul-as-Config vs Soul-as-Code Evolution
**Impact**: Future extensibility, policy-as-code  
**Mandates**: M16 (Modularization), M21 (Gate Integrity)  
**Current State**: Soul.yaml = YAML directives (config). Future: executable constraints, policy-as-code?

#### Research Questions:
1. **Executable Directives**: Can directives become runnable validation? e.g., `jc-d-001` → `assert not loads_embedding_in_test_mode()`
2. **Policy Language**: Rego/OPA? Custom DSL? Python predicates?
3. **Runtime Enforcement**: Pre-commit? CI gate? Runtime hook in Oracle?
4. **Backward Compatibility**: YAML directives remain human-readable; code layer optional?
5. **Migration Path**: Gradual adoption per directive? Per entity?

#### Required Output:
- `docs/adr/ADR-XXX-soul-as-code.md` — Architecture decision
- `src/omega/governance/soul_executor.py` — Directive execution engine (if approved)
- `schemas/soul_directive_v2.yaml` — Extended schema with `executable` field

#### Sources to Mine:
- `src/omega/governance/config_resolver.py` (config resolution pattern)
- `src/omega/oracle/health_monitor.py` (runtime validation pattern)
- Industry: OPA/Rego, CEL, Kyverno policy-as-code patterns

---

### GAP-012: Token Budget for Distillation Pipeline (C-10.5 Integration)
**Impact**: C-0.5 Scribe implementation feasibility  
**Mandates**: M7 (Local-First), M18 (Token Efficiency), M25 (Streaming Resilience)  
**Current State**: C-10.5 quota tracker being implemented. Scribe needs reserved budget. No estimates.

#### Research Questions:
1. **Per-Session Cost**: 
   - Input: ~50k tokens (session context)
   - L1 extraction: ~5k tokens output
   - L2 synthesis: ~3k tokens output  
   - L3 distillation: ~1k tokens output
   - Total: ~60k tokens per session per entity?
2. **Batch vs Streaming**: Process all sessions at once (batch) or stream per session?
3. **Model Selection**: Local (Qwen3-1.7B) vs Cloud (Nemotron) for distillation? Cost/quality tradeoff?
4. **Quota Reservation**: How much of C-10.5 local budget to reserve for Scribe? Priority level?
5. **Fallback**: If local quota exhausted, cloud fallback? Which provider? Cost ceiling?

#### Required Output:
- `docs/specs/SPEC_Scribe_Token_Budget.md` — Budget specification
- `src/omega/oracle/quota_tracker.py` — Scribe integration (C-10.5)
- `config/providers.yaml` — Scribe provider profile with reserved quota

#### Sources to Mine:
- `docs/sprints/guard-and-distill/02-p0-tickets/C-10.5-quota-routing.md`
- `docs/research/R_GUARD_DISTILL_RESEARCH_GUIDE_20260722.md` §Domain 5
- `src/omega/oracle/cascade_router.py` (provider routing)

---

## §5 Strategic Research Request — Unified Execution Plan

### Phase 1: Critical Path (Week 1-2) — Unblocks C-0.5
| Gap | Owner | Deliverable | Depends On |
|-----|-------|-------------|------------|
| GAP-001 | Researcher + Ma'at/P3 | `SPEC_Scribe_Distillation_Pipeline.md` | C-10.5 research complete |
| GAP-002 | Verity + Kali | `SOUL_GOVERNANCE_PROTOCOL.md` | GAP-001 (promotion triggers) |
| GAP-003 | Ma'at/P3 + Researcher | `ADR-XXX-soul-schema-v7.md` | GAP-002 (governance informs schema) |

### Phase 2: Fleet Coherence (Week 2-3) — Enables Scale
| Gap | Owner | Deliverable | Depends On |
|-----|-------|-------------|------------|
| GAP-004 | Kali + Lilith/P7 | `SOUL_SYNC_PROTOCOL.md` | GAP-003 (v7.0 schema) |
| GAP-005 | Ma'at/P5 + Researcher | `mandate_registry.yaml` + resolver | GAP-002 (ownership model) |
| GAP-006 | Scribe (once built) | `PROPOSAL_LIFECYCLE.md` | GAP-002 (state machine) |
| GAP-007 | Doom_Guy + Verity | `HERITAGE_VET_FOR_SOUL_PROMOTION.md` | GAP-002 (promotion gate) |

### Phase 3: Strategic Architecture (Week 3-4) — Future-Proofing
| Gap | Owner | Deliverable | Depends On |
|-----|-------|-------------|------------|
| GAP-008 | Ma'at/P3 | `ADR-XXX-soul-versioning.md` + tooling | GAP-003 |
| GAP-009 | Verity + Researcher | `SKEPTICAL_VERIFIER_SOUL_INTEGRATION.md` | GAP-002, GAP-003 |
| GAP-010 | Kali + MaKaLi | `FLEET_SOUL_DOCTRINE.md` | GAP-004, GAP-005 |
| GAP-011 | Researcher + Ma'at/P3 | `ADR-XXX-soul-as-code.md` | GAP-003, GAP-009 |
| GAP-012 | Ma'at/P3 + Lilith/P6 | `SPEC_Scribe_Token_Budget.md` | C-10.5 implementation |

---

## §6 Research Methodology — Enhanced with 2026 Best Practices

### For Each Gap — Spec-Driven Research Workflow

*Adapted from: "How to Write Specs for AI Agents" (Golchian 2026), "Building Effective Agents" (Anthropic 2024), "Context Engineering for AI Agents" (Agentmelt 2026), "Deep Agents Pattern" (Particula 2026), "Autonomous Research Agent" spec (FindSkill 2026)*

#### Phase 0: Spec the Research Job (Before Any Search)
1. **Write the Research Job Spec** using the template in §1.5 — define core_question, sub_questions, scope, output_requirements, source_strategy, search_protocol, synthesis_techniques, quality_gates, stopping_conditions, escalation_triggers, context_engineering
2. **Define Acceptance Checks First** — "What concrete conditions prove this gap is resolved?" (e.g., "SPEC_Scribe_Distillation_Pipeline.md exists with complete GBNF grammar, chunking algorithm, decision matrix, token budget, hook API, error handling, output format")
3. **Size to Single Bolt** — If spec sprawls past one afternoon of build+verify, split at spec level into independent pieces
4. **Point at Code** — Reference existing Omega patterns, files, conventions the research must align with

#### Phase 1: Mine Existing Artifacts (Internal Context Engineering)
1. **Read All Referenced Sources First** — No external search until internal knowledge exhausted
2. **Use Virtual Filesystem for Context Offload** — Write intermediate findings to `data/coordination/research_findings/{gap_id}/` as markdown files; keep only references/summaries in context
3. **Maintain Scratchpad** — Write conclusions from each source, not raw text. Next turn, scratchpad carries conclusion in 50 tokens instead of 5,000
4. **Isolate Context Per Sub-Task** — If gap requires multiple distinct investigations, spawn isolated sub-agents (via `task()` tool) with fresh context; each returns only clean result

#### Phase 2: External Research (Systematic Search Execution)
1. **Start with Authoritative Sources** — Per sub-question: academic papers, industry reports, government standards, official docs
2. **Use Specific, Targeted Queries** — Not broad/vague. Apply query formulation techniques:
   - **Specificity Scaling**: Broad → narrow as you gather info
   - **Multi-Perspective**: "X vs Y", "criticism of X", "alternatives to X"
   - **Date-Bounded**: "2026", "last 6 months", "since 2024"
3. **Verify Key Claims Across ≥2 Independent Sources** — Cross-reference strategy mandatory
4. **Note Contradictions** — Don't ignore; flag for synthesis
5. **Track All Sources for Citations** — Every factual claim must have inline citation [1], [2] with URL
6. **Tool Budget Discipline** — Max 5 search tool calls per sub-question; stop when 3 consecutive searches yield no new high-credibility info

#### Phase 3: Synthesis & Analysis (Structured, Not Freeform)
1. **Apply Synthesis Techniques** (from Autonomous Research Agent spec):
   - **Thematic Grouping** — Group findings by theme, not source; identify patterns; note overlaps/conflicts
   - **Timeline Construction** — For evolutionary topics
   - **Stakeholder Mapping** — Who holds which positions
   - **Comparative Matrix** — Side-by-side comparison of approaches
   - **Evidence Pyramid** — Rank findings by strength: primary research > industry reports > expert blogs > news > forums
2. **Structure Output Per Required Format** — Executive summary, full report, comparison table, etc.
3. **Citation Discipline** — Every claim cited; primary vs secondary distinguished; unverified marked [UNVERIFIED]

#### Phase 4: Quality Assurance (Before Delivery)
1. **Completeness Check** — All sub-questions answered? Gaps marked [UNVERIFIED]?
2. **Bias Detection** — Source bias checklist applied (company announcements = medium credibility, may be biased)
3. **Citation Audit** — Every factual claim cited? URLs verifiable?
4. **Contradiction Flag** — Conflicting sources surfaced with attribution, not silently merged
5. **Mandate Cross-Check** — Deliverable aligns with all mapped mandates (M5, M11, M14, M17, M21)
6. **Heritage Tag Validation** — Any heritage tags in output have vet records (M14)

#### Phase 5: Draft Deliverable (Spec-Compliant)
1. **Write to Target Location** — `docs/research/` or `docs/strategy/` per Doc Standards
2. **Follow Omega Doc Standards** — `make doc-llm-validate` must pass
3. **Include Machine-Readable Artifacts** — JSON Schema, Pydantic models, YAML configs where applicable
4. **Contract Tests** — For any code deliverable, write `tests/unit/test_*.py` with `isinstance(result, ExpectedType)` (M21)

#### Phase 6: Review & Iterate (Kali/MaKaLi Council)
1. **Architectural Review** — Kali/MaKaLi for decisions affecting fleet coherence
2. **Compliance Review** — Verity for mandate alignment
3. **Heritage Review** — Doom_Guy for heritage tags
4. **Incorporate Feedback** — Update spec, not just implementation; living spec principle

---

### Research Job Execution Patterns (Per Gap Complexity)

| Gap Complexity | Pattern | Token Cost | When to Use |
|----------------|---------|------------|-------------|
| **Single focused question** (GAP-007, GAP-012) | Single research agent, 1-2 iterations | ~1× baseline | Sub-questions tightly coupled, <5 steps |
| **Multi-faceted, separable aspects** (GAP-001, GAP-003) | Planner → parallel sub-agents (isolated contexts) → aggregator → verifier | ~15× baseline | Open-ended, >15 steps, parallelizable reads |
| **Architectural decision** (GAP-002, GAP-008, GAP-010, GAP-011) | Collaborative planning: agent proposes plan → human refines → approve → execute | ~3-5× baseline | High stakes, irreversible, needs human judgment |

**Decision Rule** (Particula 2026): "Under ~15-20 steps with tightly coupled work, stay single-loop. Beyond that, with separable exploratory sub-tasks, deep-agent pattern pays for 15× token premium."

---

### Context Engineering Rules for Research Agents

| Rule | Implementation |
|------|----------------|
| **Write context, don't dump it** | Scratchpad = conclusions (50 tokens), not raw text (5,000) |
| **Select context, don't include it** | Retrieve relevant subset per turn; don't dump all tools/memory |
| **Compress at threshold** | 50% window → summarize conversation tail; every N turns → rewrite scratchpad |
| **Isolate sub-agent contexts** | Sub-agents get fresh context; return only clean results to orchestrator |
| **Order context assembly** | [system, tools, long-term memory, retrieved knowledge, conversation history, scratchpad, current instruction] |

---

### Tool Design for Research (Anthropic Appendix 2)

| Tool | Description Must Include |
|------|-------------------------|
| `websearch` | When to use (broad queries), when NOT (deep technical), output format, limitations |
| `webfetch` | When to use (full page needed), when NOT (snippet sufficient), output format |
| `searxng_search` | When to use (semantic/neural), categories/engines params, output format |
| `omega-hub_sovereign_search` | When to use (precision seeds), force_tier param, output format |
| `omega-hub_library_discovery_research` | When to use (deep research with citations), depth param, output format |
| `think_tool` | **CRITICAL**: Use after EACH search to reflect: "What key info found? What's missing? Enough to answer? Search more or answer?" |

---

### Evaluation & Quality Gates for Research Outputs

| Gate | Criteria | Tool |
|------|----------|------|
| **Temple-Grade** | `make temple-grade` passes (T1-T11) | CI |
| **Doc Standards** | `make doc-llm-validate` passes | CI |
| **Heritage Vet** | All `[id-soft:]` tags have vet record ≥7/10 | `make heritage-vet` |
| **Contract Tests** | All new modules have `isinstance(result, ExpectedType)` tests | `make test` |
| **Provenance** | Research logs show actual provider, not configured intent | M22 compliance |
| **Success Rate** | Not binary "did it work?" — measure "how often does it succeed?" | Eval harness |

---

### Immediate Action Items (Updated)

#### For Researcher (You):
1. **Write Research Job Spec for GAP-001** using §1.5 template → then execute
2. **Write Research Job Spec for GAP-007** using §1.5 template → then execute
3. **Research policy-as-code patterns (OPA, CEL, Kyverno)** → Inform GAP-011
4. **Research semantic versioning + migration tooling patterns** → Inform GAP-008

#### For Ma'at/P3 (Engineering):
1. **Implement C-10.5 quota tracker** → Unblocks GAP-012
2. **Draft mandate_registry.yaml** → Unblocks GAP-005
3. **Build soul_migrate.py skeleton** → Prepares GAP-008

#### For Verity (Compliance):
1. **Draft SOUL_GOVERNANCE_PROTOCOL.md** → Closes GAP-002
2. **Define Skeptical Verifier API** → Prepares GAP-009
3. **Audit current proposals for heritage vet readiness** → Prepares GAP-007

#### For Kali (Architecture):
1. **Adjudicate GAP-010 (Fleet Doctrine)** — Requires MaKaLi council
2. **Approve v7.0 schema direction** — Unblocks GAP-003
3. **Define promotion authority** — Core to GAP-002

---

## §7 Success Criteria (Updated)

| Metric | Target |
|--------|--------|
| All 12 gaps have drafted deliverables | Week 4 |
| C-0.5 Scribe implementation begins | Week 2 (after GAP-001, 002, 003) |
| First soul.yaml v7.0 promotion | Week 3 |
| Fleet doctrine v1.0 ratified | Week 4 |
| Mandate registry operational | Week 3 |
| Zero unvetted heritage tags in promoted directives | Ongoing (M14) |
| `make temple-grade` passes with new modules | All phases |
| Research job specs written for all gaps before execution | Week 1 |
| Context engineering rules followed (scratchpad, isolation, compression) | All research |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ trc_soul_gaps ⬡ 2026-07-22*
*This guide is the single source of truth for soul.yaml enhancement knowledge gaps.*
*All research outputs must be written to `docs/research/` or `docs/strategy/` per Doc Standards.*