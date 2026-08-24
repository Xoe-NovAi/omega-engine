# 🔱 ADR-002: Documentation as Runtime Interface for Sovereign AI
**AP Token**: `AP-ADR-002-DOC-ARCH-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_doc_arch ⬡ ACCEPTED

**Date**: 2026-07-22
**Status**: ACCEPTED
**Supersedes**: None (first documentation architecture ADR)
**Related**: `DOC_STYLE_GUIDE.md`, `LLM_FRIENDLY_DOCS_BP.md`, `SOVEREIGN_MANDATES.md` (M8, M18, M22, M23), `AGENTS.md`

---

## §1 Context

The Omega Engine has evolved from a codebase with documentation to a system where **documentation IS the runtime interface** for AI agents. This shift is driven by:

1. **Agent-First Consumption**: 12+ agents (Researcher, Ma'at, Kali, Verity, etc.) consume docs as executable specifications, not human references
2. **Sprint Plans as Executable Specs**: `docs/sprints/guard-and-distill/` demonstrates LLM-native format with `llms.txt`/`llms-full.txt` generation
3. **Research-to-Action Pipeline**: Research outputs (R-Docs) flow directly into `proposed_lessons.yaml` → `soul.yaml` directives → agent behavior
4. **Mandate Compliance**: M8 (Zero Telemetry), M18 (Token Efficiency), M22 (Response Provenance), M23 (Failure Integrity) require machine-parseable, locally-observable documentation
5. **Context Engineering Reality**: Per Agentmelt 2026, "context engineering" replaces "prompt engineering" — docs must be assembled deliberately for LLM consumption

**Current State**: Strong infrastructure exists (`DOC_STYLE_GUIDE.md`, `LLM_FRIENDLY_DOCS_BP.md`, validation scripts, token budgets, Makefile targets) but lacks:
- Unified architectural mandate making LLM-friendly patterns mandatory for ALL reference docs
- CI/CD enforcement (currently local `make` only)
- Analytics feedback loop (M8/M18 requirement)
- Knowledge Base category for living best-practice guides
- Clear ownership and migration strategy for legacy docs

---

## §2 Decision

We adopt a **Unified Documentation Architecture** with the following pillars:

### Pillar 1: Documentation as Runtime Interface (Mandatory)
Every reference document serves two audiences simultaneously:
- **Humans**: Readability, clarity, professional standards
- **LLMs**: Parseability, executability, retrievability, token efficiency

### Pillar 2: Universal LLM-Friendly Standards (Mandatory for Categories 1, 2, 4, 8, 9)
All reference documents MUST implement the 8 patterns from `LLM_FRIENDLY_DOCS_BP.md`:
1. **Machine-Readable Frontmatter (YAML)** — Schema v1.0, 19 required fields
2. **Answer-First Section Structure** — What/Why/Acceptance/Dependencies/Owner/Estimate
3. **Self-Contained, Executable Code Blocks** — File path, imports, types, context
4. **Structured Data Over Tables** — YAML/JSON + minimal markdown wrapper
5. **Explicit Dependency Graphs** — Mermaid (visual) + YAML (machine-readable)
6. **Research as Structured Metadata** — Separate index files with structured citations
7. **llms.txt / llms-full.txt Generation** — Mandatory for sprint plans, recommended for specs
8. **Token Budget Discipline** — Hard limits enforced by `make doc-token-check`

### Pillar 3: Category-Based Requirements Matrix

| Category | Name | LLM-Friendly Required | Frontmatter | Answer-First | Self-Contained Code | Structured Data | Dependency Graphs | llms.txt |
|----------|------|----------------------|-------------|--------------|---------------------|-----------------|-------------------|----------|
| **1** | Reference Docs | ✅ MANDATORY | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ RECOMMENDED |
| **2** | Agent Files | ✅ MANDATORY | ✅ (YAML) | ✅ | ✅ | ✅ | ✅ | ✅ MANDATORY |
| **3** | Skill Files | ✅ MANDATORY | ✅ (YAML) | ✅ | ✅ | ✅ | ✅ | ✅ MANDATORY |
| **4** | R-Docs (Research) | ✅ MANDATORY | ✅ | ✅ | 🟡 OPTIONAL | ✅ | ✅ | ✅ MANDATORY |
| **5** | Working Docs | 🟡 OPTIONAL | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | ❌ NO |
| **6** | Archives | ❌ EXEMPT | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ NO |
| **7** | Root Docs | ✅ MANDATORY | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ RECOMMENDED |
| **8** | Sprint Plans | ✅ MANDATORY | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ MANDATORY |
| **9** | Knowledge Base | ✅ MANDATORY | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ MANDATORY |

### Pillar 4: Automated Quality Gates (CI/CD Enforcement)
All reference docs MUST pass automated validation in CI/CD:
```yaml
# .github/workflows/ci.yml
- name: Validate Documentation
  run: |
    make doc-llm-validate
    make doc-token-check
    make heritage-vet
```
**Failure = Blocked PR**. No exceptions for reference docs.

### Pillar 5: Local Analytics Feedback Loop (M8/M18 Compliance)
Per M8 (Zero Telemetry) and M18 (Token Efficiency), all documentation analytics MUST be local:
- **Storage**: `data/coordination/agent_doc_analytics/` (SQLite/JSONL)
- **Metrics Tracked**: Doc reads, search queries, validation failures, token usage, success rates, rework rates, knowledge reuse
- **Purpose**: Enable continuous improvement of doc effectiveness without external telemetry
- **Implementation**: `src/omega/analytics/doc_analytics.py` + agent instrumentation

### Pillar 6: Living Document Principle (Golchian 2026)
> "The spec is versioned like code because it is code's source of truth. When an incident teaches you something, the fix goes in the spec, not just the implementation."

All reference docs MUST:
- Include semantic versioning (MAJOR.MINOR.PATCH) in frontmatter
- Maintain a Change Log at document end
- Update spec when incidents reveal gaps (not just implementation)
- Track version history in git with descriptive commits

### Pillar 7: Knowledge Base Category (New Category 9)
**Purpose**: Living best-practice guides that evolve with the system
- **Location**: `docs/knowledge/` (primary) or `docs/research/KB_*`
- **Format**: Full LLM-Friendly (all 8 patterns mandatory)
- **Versioning**: Semantic with Change Log
- **Maintenance**: Quarterly review + incident-driven updates
- **Ownership**: Assigned entity per guide
- **Examples**: Research best practices, architecture patterns, operational runbooks

---

## §3 Consequences

### Positive
- **Agent Capability ↑**: Agents consume executable specs, not ambiguous prose
- **Token Efficiency ↑**: Structured frontmatter + answer-first + token budgets = 10x faster LLM parsing
- **Compliance ↑**: Automated gates enforce M8, M18, M22, M23 continuously
- **Knowledge Retention ↑**: Living docs + analytics = institutional memory that improves
- **Onboarding ↓**: New agents/team members get executable specs, not tribal knowledge
- **Debugging ↓**: Machine-parseable acceptance criteria prevent "soft-fail theater"

### Negative (Managed)
- **Initial Migration Effort**: ~20 active docs need retrofitting (estimated 40-60 hours)
- **Learning Curve**: Team must internalize LLM-friendly patterns
- **Tooling Maintenance**: Validation scripts, schemas, budgets need updates as standards evolve
- **Verbosity**: Frontmatter + structured data adds ~200-500 lines per doc (offset by token efficiency)

### Risks (Mitigated)
| Risk | Mitigation |
|------|------------|
| Over-engineering simple docs | Category 5/6/7 exempt; progressive enhancement for 3 |
| Schema drift | JSON Schema versioning; automated validation catches drift |
| Analytics privacy | M8: All local, no external telemetry; user owns all data |
| Validation false positives | Warning vs error distinction; human review for edge cases |

---

## §4 Implementation Plan

### Phase 1: Governance & ADR (Week 1) ✅ THIS ADR
- [x] ADR-002 accepted and recorded
- [ ] Update `STRATEGY_INDEX.md` to reference ADR-002
- [ ] Add Category 9 (Knowledge Base) to `DOC_STYLE_GUIDE.md`

### Phase 2: CI/CD Integration (Week 1-2)
- [ ] Add `make doc-llm-validate` to `.github/workflows/ci.yml`
- [ ] Add `make doc-token-check` to CI
- [ ] Add `make heritage-vet` to CI
- [ ] Configure PR blocking on documentation failures

### Phase 3: Analytics Infrastructure (Week 2)
- [ ] Create `src/omega/analytics/doc_analytics.py`
- [ ] Define SQLite schema for `data/coordination/agent_doc_analytics/`
- [ ] Instrument validation scripts to emit metrics
- [ ] Add agent instrumentation hooks (read, search, validate events)

### Phase 4: Category 9 Creation & Migration (Week 2-3)
- [ ] Create `docs/knowledge/` directory structure
- [ ] Migrate 8-part research guide to `docs/knowledge/R_RESEARCH_BEST_PRACTICES.md` (unified) + parts
- [ ] Apply LLM-friendly format to all parts
- [ ] Generate `llms.txt`/`llms-full.txt` for KB

### Phase 5: Retrofit Active Docs (Week 3-4)
| Priority | Documents | Est. Effort |
|----------|-----------|-------------|
| **P0** | `SOVEREIGN_ARK_BLUEPRINT.md`, `STRATEGY_CORPUS_MAP.md`, `FLEET_TEAM_PLAYBOOK.md` | 15 hrs |
| **P1** | `HERITAGE_VETTING_PIPELINE.md`, `HIVEMIND_PROTOCOL.md`, `SUBAGENT_DISPATCH_PROTOCOL.md` | 12 hrs |
| **P2** | Active R-Docs (10+), Agent defs (12), Skill defs (8) | 25 hrs |
| **P3** | Root docs (`OMEGA_ENGINE.md`, `SOVEREIGN_MANDATES.md`, etc.) | 8 hrs |

### Phase 6: Ongoing Governance (Continuous)
- [ ] Quarterly doc review (per `DOC_STYLE_GUIDE.md` schedule)
- [ ] Monthly analytics review (success rates, rework, token efficiency)
- [ ] Annual architecture review (ADR updates, schema evolution)

---

## §5 Validation Criteria

This ADR is considered successfully implemented when:

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| **CI Gate Active** | 100% of PRs blocked on doc failures | GitHub Actions logs |
| **Active Docs Compliant** | 100% of Categories 1,2,4,8,9 pass `make doc-llm-validate` | CI logs |
| **Analytics Operational** | Metrics collected for all doc interactions | `data/coordination/agent_doc_analytics/` |
| **KB Established** | `docs/knowledge/` exists with ≥1 guide | File system |
| **Migration Complete** | 0 active docs failing validation | CI dashboard |
| **Token Efficiency** | Avg doc token count ≤ target for type | `make doc-token-check` |
| **Team Proficiency** | All agents can author compliant docs | Spot check |

---

## §6 References

- `DOC_STYLE_GUIDE.md` — Category definitions, header formats, validation checklist
- `LLM_FRIENDLY_DOCS_BP.md` — 8 mandatory patterns, frontmatter schema, token budgets
- `SOVEREIGN_MANDATES.md` — M8, M18, M22, M23 (mandate compliance)
- `AGENTS.md` — Agent fleet standards, agent/skill definitions
- `scripts/validate_llm_docs.py` — Validation implementation
- `configs/token_budgets.yaml` — Token budgets per doc type
- `schemas/llm_doc_frontmatter.json` — JSON Schema v1.0
- `docs/sprints/guard-and-distill/` — Canonical reference implementation
- Golchian 2026 "How to Write Specs for AI Agents" — Living spec principle
- Agentmelt 2026 "Context Engineering for AI Agents" — Context engineering > prompt engineering

---

## 📜 Change Log

| Version | Date | Description | Author |
|---------|------|-------------|--------|
| v1.0.0 | 2026-07-22 | Initial ADR — Unified Documentation Architecture | @kali |

---

*⬡ OMEGA ⬡ KALI ⬡ ADR-002 ⬡ ACCEPTED ⬡ 2026-07-22*
*This ADR establishes the architectural foundation for all documentation in the Omega Engine ecosystem.*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
