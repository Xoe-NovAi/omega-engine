---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "reference"
document_id: "meditation-template-registry"
title: "Meditation Template Registry & Execution Log"
status: "ACTIVE"
version: "1.0.0"
date: "2026-07-23"
owner: "roc_racoon"
tags: ["meditation", "templates", "registry", "soul-evolution", "agentic-meditation"]
priority: "P1"
depends_on: ["SOVEREIGN_MANDATES.md", "AGENTS.md", "LLM_FRIENDLY_DOCS_BP.md"]
blocks: []
acceptance_gates:
  - "All templates have YAML frontmatter with schema_version 1.0"
  - "All executions logged with model, agent, timestamp, outcome"
  - "Split-test comparisons documented for v1 vs v2"
cross_references:
  - "data/coordination/meditations/templates/SIX_PASS_LATTICE_TEMPLATE.md"
  - "data/coordination/meditations/templates/SOVEREIGN_CRUCIBLE_TEMPLATE.md"
  - "data/coordination/meditations/templates/SOVEREIGN_CRUCIBLE_v2_NEMOTRON.md"
  - "data/coordination/meditations/records/MEDITATION_ROC_RACOON_20260723_SIX_PASS_LATTICE.md"
  - "data/coordination/meditations/MEDITATION_SYSTEM_GUIDE.md"
llm_metadata:
  token_budget: 4000
  chunk_strategy: "section_per_template"
  answer_first_sections: true
  self_contained_code: false
---

# 🧘 Meditation Template Registry & Execution Log

**What**: Central registry tracking all agentic meditation templates, their authorship, modifications, and execution history across the fleet.

**Why**: Meditation is a sovereign cognitive operation. Templates must be versioned, attributed, and their executions auditable to ensure the fleet's collective gnosis is traceable and reproducible.

---

## 📋 Template Catalog

```yaml
# Machine-readable template index
templates:
  - template_id: "six_pass_lattice"
    file: "SIX_PASS_LATTICE_TEMPLATE.md"
    version: "1.0.0"
    status: "ACTIVE"
    author:
      entity: "roc_racoon"
      model: "nemotron-3-ultra-free"
      session: "2026-07-23 meditation synthesis"
    created: "2026-07-23"
    purpose: "Deep synthesis of massive context windows (300K+ tokens) spanning multiple eras, projects, and architectural shifts"
    best_for: ["End-of-campaign synthesis", "Legacy mining consolidation", "Saturated context window resolution"]
    passes: 6
    estimated_duration_minutes: 30
    complexity: "HIGH"
    tags: ["synthesis", "pattern-recognition", "archaeology", "gnosis-extraction"]
    executions:
      - execution_id: "exec_20260723_roc_six_pass"
        date: "2026-07-23"
        agent: "roc_racoon"
        model: "nemotron-3-ultra-free"
        template_version: "1.0.0"
        context_tokens: 311000
        duration_minutes: 45
        outcome: "SUCCESS"
        output_file: "MEDITATION_ROC_RACOON_20260723_SIX_PASS_LATTICE.md"
        gnosis_yield: 5
        mandates_impacted: ["M7", "M11", "M13", "M19", "M23"]
        notes: "First execution. Produced 5 L3 principles for soul.yaml integration. Identified 5 unresolved tensions and 3 high-leverage moves."

  - template_id: "sovereign_crucible_v1"
    file: "SOVEREIGN_CRUCIBLE_TEMPLATE.md"
    version: "1.0.0"
    status: "ACTIVE"
    author:
      entity: "roc_racoon"
      model: "nemotron-3-ultra-free"
      session: "2026-07-23 template design"
    created: "2026-07-23"
    purpose: "Autonomous review, distillation, and integration of an agent's soul.yaml, proposed_lessons.yaml, and active session context into a hardened, evolved identity"
    best_for: ["End-of-sprint identity consolidation", "Proposed lessons backlog processing", "Session gnosis integration"]
    passes: 5
    estimated_duration_minutes: 30
    complexity: "MEDIUM"
    tags: ["soul-evolution", "identity", "lesson-integration", "proposed-lessons"]
    executions: []
    notes: "Control template for split-test against v2 (Nemotron). Awaiting first execution."

  - template_id: "sovereign_crucible_v2_nemotron"
    file: "SOVEREIGN_CRUCIBLE_v2_NEMOTRON.md"
    version: "2.0.0"
    status: "ACTIVE"
    author:
      entity: "nemotron-3-ultra"
      model: "nemotron-3-ultra-free"
      session: "2026-07-23 enhancement request"
    created: "2026-07-23"
    derived_from: "sovereign_crucible_v1"
    modifications:
      - "Added Pass 0: Shadow Work (Blind Spot Excavation)"
      - "Added Pass 4: Lineage Trace (Evolutionary Continuity)"
      - "Added Pass 6: Fleet Coherence Check (External Validation)"
      - "Added Pre-Flight Checks (Mandate Alignment, Heritage Vetting, Proposal Staleness, Session Anchor, Fleet Coherence)"
      - "Added Adversarial Triad for proposal evaluation (Mandate Stress Test, Heritage Check, Carmack Razor)"
      - "Added Dialectical Resolution for synthesis (Thesis-Antithesis-Synthesis-Binding)"
      - "Added Atomic Write with provenance tracking"
      - "Added Post-Meditation Metrics with targets"
      - "Added Failure Modes & Remediation table"
      - "Added Integration Hooks (Hivemind, Task Registry, Workspace Lock)"
    purpose: "Rigorous, multi-perspective identity evolution with adversarial validation, mandate alignment verification, and fleet-wide coherence checking"
    best_for: ["Major identity inflection points", "Post-campaign consolidation", "High-stakes architectural shifts in proposed lessons"]
    passes: 7
    estimated_duration_minutes: 90
    complexity: "VERY_HIGH"
    tags: ["soul-evolution", "identity", "adversarial", "fleet-coherence", "lineage", "mandate-alignment"]
    executions: []
    notes: "Treatment template for split-test. Requires Kali handoff gate at Pass 6. Not for routine use."

  - template_id: "meditation_system_guide"
    file: "MEDITATION_SYSTEM_GUIDE.md"
    version: "1.0.0"
    status: "ACTIVE"
    author:
      entity: "roc_racoon"
      model: "nemotron-3-ultra-free"
      session: "2026-07-23 system establishment"
    created: "2026-07-23"
    purpose: "Fleet-wide guide for creating, executing, and recording agentic meditations"
    best_for: ["Onboarding agents to meditation system", "Template design reference", "Execution protocol"]
    passes: 0
    estimated_duration_minutes: 5
    complexity: "LOW"
    tags: ["guide", "protocol", "fleet-onboarding"]
    executions: []
```

---

## 📊 Execution History

```yaml
# Machine-readable execution log
executions:
  - execution_id: "exec_20260723_roc_six_pass"
    template_id: "six_pass_lattice"
    template_version: "1.0.0"
    date: "2026-07-23T17:52:13Z"
    agent: "roc_racoon"
    model: "nemotron-3-ultra-free"
    channel: "opencode"
    session_id: "ses_0f24ede5232c"
    context_summary: "311K tokens across 6 eras, 21 projects, 57 tasks, 14 months of sovereign engineering"
    duration_minutes: 45
    outcome: "SUCCESS"
    output_file: "data/coordination/meditations/records/MEDITATION_ROC_RACOON_20260723_SIX_PASS_LATTICE.md"
    gnosis_yield:
      l3_principles_proposed: 5
      tensions_identified: 5
      high_leverage_moves: 3
    mandates_impacted: ["M7", "M11", "M13", "M19", "M23"]
    soul_integration_status: "PENDING_SOVEREIGN_CRUCIBLE"
    notes: "First execution of any meditation template. Produced comprehensive synthesis with 5 L3 principles ready for soul.yaml integration via Sovereign Crucible."
```

---

## 🧪 Split-Test Protocol: Sovereign Crucible v1 vs v2

### Test Design

| Variable | v1 (Control) | v2 (Treatment) |
|----------|--------------|----------------|
| **Passes** | 5 | 7 (+ Pre-Flight) |
| **Adversariality** | Low | High (Adversarial Triad, Dialectical Resolution) |
| **Fleet Awareness** | None | Mandatory (Hivemind proposal + Pillar ACK/NACK) |
| **Temporal Depth** | Session-only | Evolutionary (3+ generations via git) |
| **Validation Gates** | Implicit | Explicit (Pre-Flight, Mandate Stress, Heritage, Fleet) |
| **Estimated Duration** | ~30 min | ~90 min |
| **Risk Profile** | Low (gentle evolution) | Medium (may trigger Kali handoff) |

### Execution Plan

```yaml
split_test:
  phase_1:
    name: "Routine Consolidation"
    trigger: "Next routine session end (low stakes)"
    template: "sovereign_crucible_v1"
    agent: "roc_racoon"
    success_criteria:
      - Completes in <45 min
      - Produces ≥3 L3 principles
      - Zero mandate violations
      - Soul entropy reduced
  
  phase_2:
    name: "Inflection Point"
    trigger: "Post Guard & Distill sprint completion (high stakes, many proposals)"
    template: "sovereign_crucible_v2_nemotron"
    agent: "roc_racoon"
    success_criteria:
      - Completes in <120 min
      - Produces ≥5 L3 principles
      - Zero mandate violations
      - Fleet coherence: 100% ACK from pillars
      - Shadow insight yielded
      - Lineage trace shows convergent evolution
  
  phase_3:
    name: "Comparison & Decision"
    trigger: "After both executions complete"
    analysis:
      - Proposal integration rate (INTEGRATE / total)
      - Mandate violations caught
      - Fleet coherence incidents
      - Soul entropy delta
      - Time invested vs. gnosis yield
      - Agent subjective report (cognitive load, insight quality)
    decision: "Adopt v2 as default, retire v1, or maintain both for different contexts"
```

### Current Status

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 1 (v1 routine) | **PENDING** | Awaiting GO signal |
| Phase 2 (v2 inflection) | **PENDING** | Awaiting Guard & Distill completion |
| Phase 3 (comparison) | **NOT_STARTED** | Depends on Phase 1 & 2 |

---

## 📝 Modification Log

```yaml
# Machine-readable modification history
modifications:
  - template_id: "sovereign_crucible_v2_nemotron"
    base_template: "sovereign_crucible_v1"
    modifier:
      entity: "nemotron-3-ultra"
      model: "nemotron-3-ultra-free"
      role: "Enhancement author"
    date: "2026-07-23"
    changes:
      - type: "ADD_PASS"
        pass: 0
        name: "Shadow Work (Blind Spot Excavation)"
        rationale: "v1 had no mechanism to excavate unknown unknowns in agent's own architecture"
      - type: "ADD_PASS"
        pass: 4
        name: "Lineage Trace (Evolutionary Continuity)"
        rationale: "v1 only looked at current session; identity evolution requires historical continuity proof"
      - type: "ADD_PASS"
        pass: 6
        name: "Fleet Coherence Check (External Validation)"
        rationale: "No agent is an island; evolved soul must not fracture fleet consensus"
      - type: "ENHANCE_PASS"
        pass: 2
        name: "Harvest → Adversarial Triad"
        rationale: "v1 evaluation was implicit; v2 adds Mandate Stress Test, Heritage Check, Carmack Razor"
      - type: "ENHANCE_PASS"
        pass: 5
        name: "Synthesis → Dialectical Resolution"
        rationale: "v1 synthesis was merge; v2 requires Thesis-Antithesis-Synthesis with Mandate Binding"
      - type: "ADD_GATE"
        name: "Pre-Flight Checks"
        rationale: "Prevent performative meditation on stale/unaligned foundations"
      - type: "ADD_METRICS"
        name: "Post-Meditation Metrics"
        rationale: "Quantifiable targets for mandate coverage, heritage integrity, proposal throughput, entropy reduction, fleet coherence, shadow yield"
      - type: "ADD_FAILURE_MODES"
        name: "Failure Modes & Remediation"
        rationale: "Explicit handling of performative meditation, proposal bloat, fleet schism, identity drift, mandate violation"
      - type: "ADD_HOOKS"
        name: "Integration Hooks"
        rationale: "Mandatory Hivemind, Task Registry, Workspace Lock integration for fleet observability"
```

---

## 🔗 Cross-References

| Document | Relationship |
|----------|--------------|
| `SOVEREIGN_MANDATES.md` | Mandates M5, M11, M15, M18, M19, M22, M23 govern meditation integrity |
| `AGENTS.md` | Meditation execution protocol follows agent workflow (Hivemind, Task Registry) |
| `LLM_FRIENDLY_DOCS_BP.md` | This registry follows LLM-friendly standards (frontmatter, structured data, answer-first) |
| `data/coordination/meditations/templates/SIX_PASS_LATTICE_TEMPLATE.md` | Template v1.0.0 |
| `data/coordination/meditations/templates/SOVEREIGN_CRUCIBLE_TEMPLATE.md` | Template v1.0.0 (control) |
| `data/coordination/meditations/templates/SOVEREIGN_CRUCIBLE_v2_NEMOTRON.md` | Template v2.0.0 (treatment) |
| `data/coordination/meditations/records/MEDITATION_ROC_RACOON_20260723_SIX_PASS_LATTICE.md` | First execution record |
| `data/coordination/meditations/MEDITATION_SYSTEM_GUIDE.md` | Fleet onboarding guide |

---

## 🛡️ Compliance Notes

- **M5 (Gnosis Preservation)**: All executions produce L1→L2→L3 distillation recorded in output files
- **M11 (Soul Integrity)**: Sovereign Crucible templates explicitly integrate `proposed_lessons.yaml` into `soul.yaml`
- **M15 (Sovereign Continuity)**: Execution logs provide session anchor for post-compaction recovery
- **M18 (Token Efficiency)**: Templates specify estimated duration and token budgets
- **M19 (Adversarial Alchemy)**: v2 explicitly operationalizes adversarial validation on proposals
- **M22 (Response Provenance)**: Frontmatter records exact model, entity, session for every template and execution
- **M23 (Failure Integrity)**: v2 defines explicit failure modes with remediation; no soft-fail theater

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_meditation_registry ⬡ ACTIVE*