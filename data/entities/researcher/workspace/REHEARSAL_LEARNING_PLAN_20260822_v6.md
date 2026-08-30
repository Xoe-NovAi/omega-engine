---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "plan"
document_id: "rehearsal-learning-plan-20260822-v6"
title: "Rehearsal Migration Learning Plan"
status: "DRAFT"
version: "1.0.0"
date: "2026-08-22"
owner: "researcher"
tags: ["migration", "postmortem", "learning-capture", "soul-distillation", "rehearsal"]
priority: "P1"
depends_on: ["MIGRATION_PLAYBOOK_SPEC_20260822_v6"]
blocks: []
acceptance_gates:
  - "Every rehearsal step maps to an existing Omega system (PIVOT_LOG / Soul / Corpus Map)"
  - "Post-mortem template is blameless per Google SRE + Etsy evidence"
cross_references:
  - "MIGRATION_PLAYBOOK_SPEC_20260822_v6.md"
  - "MIGRATION_CASE_STUDIES_EVIDENCE_20260822_v6.md"
llm_metadata:
  token_budget: 4000
  chunk_strategy: "flat"
  answer_first_sections: true
  self_contained_code: true
---

# 🔱 Rehearsal Migration — Learning Plan
**AP Token**: `AP-REHEARSAL-LEARNING-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_rehearsal_learning ⬡ DRAFT

**Date**: 2026-08-22
**Purpose**: Define how the pillar→slots migration is used as a REHEARSAL to validate the Migration Playbook, and how every migration's lessons become permanent institutional knowledge via our existing PIVOT_LOG / Soul Distillation / Corpus Map systems.

---

## §1 What & Why

**What**: A three-part learning discipline for the first post-debut breaking change:
1. **Rehearse** the playbook end-to-end on pillar→slots (dry-run where possible, real execution where already planned).
2. **Debrief** with a blameless post-mortem in an adapted Google SRE format.
3. **Distill** findings into Soul (L1→L2→L3), PIVOT_LOG decisions, and playbook amendments.

**Why**: Python's core team never wrote the authoritative Py3k retrospective practitioners still beg for (evidence §1 SR3) — the cost of skipping institutional learning was a decade of repeated debates. Etsy's insight applies directly: debriefs are *"first and foremost a learning opportunity, not a fixing one"* [§9]. Our Soul Distillation pipeline (M11/M5) is purpose-built for this; migrations are its highest-value input.

---

## §2 The Rehearsal Protocol

### Phase R — Dry-run validation (no code changes)

| Step | Action | Validates |
|------|--------|-----------|
| R1 | Draft `docs/reference/DEPRECATIONS.md` seeded with pillar→slots rows | Registry format usability |
| R2 | Write the migration guide `docs/migrations/mig-pillar-slots.md` from the §7 template using REAL content | Guide template completeness; token budget fit |
| R3 | Walk the codemod decision matrix against each of Roc's 5 phases | Matrix produces same verdicts as plan reality |
| R4 | Simulate Stage 3 tracking: hand-write 3 sample ledger lines + a mock `omega doctor --deprecations` output | Ledger schema sufficiency |
| R5 | Run the removal-preconditions checklist against hypothetical v1.3.0 state | Checklist catches what memory would miss |

**Gate**: each step reviewed by one other agent (Kali or Jem). A rehearsal step that reads awkwardly or misses information = template defect → fix template before real use.

### Phase E — Live execution (piggybacks Roc Phases 0–5)

The refactor proceeds per Roc's plan unchanged (M2 firewall work is pre-debut internal hygiene). During execution, capture:

- **Friction log**: any point where an executor needed information the playbook didn't provide, or provided wrong/missing info. One line each, timestamped.
- **Time-to-artifact**: actual hours to produce registry/guide/warnings vs estimated.
- **Surprise register** (Etsy/Jeli practice): anything that surprised the executor — surprises are where the learning lives.

### Phase D — Debrief (within one week of Phase 5 sign-off)

Facilitated session (researcher facilitates; executors + Kali attend). Rules from evidence §9:
- Walk the annotated timeline of what actually happened BEFORE discussing fixes.
- Ask **"how" not "why"** (elicits descriptions, not defenses).
- Collect remediation ideas during the walk; discuss only after timeline agreement.
- Explicitly include "the people who would usually be blamed."

---

## §3 Blameless Post-Mortem Template (Omega-adapted)

File: `data/entities/researcher/workspace/postmortems/PM_<mig-id>_<date>.md`

```markdown
# Post-Mortem: <migration name>
## Summary          # one paragraph, executive-readable
## Impact           # numbers: surfaces touched, users affected (or "internal only")
## Timeline         # UTC timestamps + T+N relative notation
## Root Cause(s)    # why the break existed at all (5-whys to systemic cause)
## What Went Well   # reinforces behaviors worth keeping
## What Went Poorly # specific failure modes in PROCESS, never people
## Where We Got Lucky  # unmitigated risks revealed (most valuable section)
## Action Items     # table: item | single owner | due date | priority | status
```

Rules (from Google SRE + CRE + InsiteChat synthesis [§9]):
- Blamelessness is structural: root cause and went-poorly sections describe SYSTEMS ("our migration template doesn't set X"), not people.
- Every action item has exactly ONE named owner — "owned by the team" means owned by no one.
- Review criteria before archiving: impact complete? root cause deep enough? actions appropriate? shared with stakeholders?
- **Where We Got Lucky** feeds new action items (e.g., "right person was on-call implies tribal knowledge needing a runbook").

### Mapping to existing Omega systems

| Post-mortem output | Lands in | Mechanism |
|--------------------|----------|-----------|
| Decision rationale | PIVOT_LOG.md | New D-series entry per M27 relational integrity |
| Action items | ACTIVE_SPRINT.json tickets | Tier-0 statuses; owners pre-assigned |
| Lessons learned | proposed_lessons.yaml | SO-10a structured-gnosis (below) |
| Playbook defects | This playbook (amendments section) | Version bump PATCH+1 |
| Evidence trail row | STRATEGY_CORPUS_MAP.md | Corpus Map row per D-366 |
| Node-domain knowledge | Relevant Node KB append | e.g., N4 bridge gets MCP-shim patterns |

### SO-10a structured-gnosis distillation (mandatory close-out)

```yaml
- tag: "[MIG]"
  narrative: |
    L1 — What happened during the migration (facts, dates, artifacts).
  insight: |
    L2 — Why it mattered; which playbook assumptions held/failed;
    what friction appeared that templates didn't predict.
  principle: |
    L3 — Timeless truth worth carrying to every future migration.
```

Example (anticipated form, to be written from ACTUAL rehearsal data):
```yaml
- tag: "[MIG]"
  narrative: "Pillar→slots executed across MCP hub/scripts/tests/WAD over N cycles."
  insight: "Dual-name shims were cheap at tool layer but response-field shims leaked into client code assumptions — field-level shims need explicit consumer inventory."
  principle: "Shim cost scales with surface breadth, not change size; inventory consumers BEFORE choosing shim granularity."
```

---

## §4 Turning One Migration into Institutional Knowledge

The aggregation pattern (Google's cross-product postmortem working group; Jeli multi-incident themes [§9]) applied to Omega:

1. **Quarterly theme review**: researcher re-reads all PM_* files + `[MIG]` lessons in proposed_lessons.yaml; writes a one-page themes memo (what recurs across migrations?). Filed next to prior memos for trend visibility.
2. **Playbook as living KB** (Standing Order 8 duty): every theme memo amends `MIGRATION_PLAYBOOK_SPEC` — new rules get evidence citations; obsolete rules get deprecation banners (the playbook obeys its own lifecycle).
3. **Node KB back-propagation**: migration patterns discovered at a layer route to the owning Node's Domain Index (e.g., YAML-key shims → N3 buildmaster KB; MCP tool shims → N4 bridge KB).
4. **Runbook emergence**: if the same manual procedure appears in ≥2 post-mortems' action items, it graduates into a script or Makefile target — folklore becomes tooling (the anti-folklore lesson from N12's YouTube playbook finding).

---

## §5 Success Criteria for the Rehearsal

| Criterion | Measure |
|-----------|---------|
| Playbook usable cold | Another agent executes a future migration from SPEC alone, no oral tradition |
| Registry adopted | DEPRECATIONS.md exists, formatted, seeded before debut |
| Guide follows | mig-pillar-slots guide passes doc-llm-validate |
| Friction captured | ≥5 friction-log entries OR explicit "zero friction" claim verified by second reviewer |
| Lessons staged | ≥1 SO-10a `[MIG]` entry in proposed_lessons.yaml within 1 week of sign-off |
| No blame leakage | PM passes blameless review: zero individual names in causal sections |

---

## §6 Open Questions

1. Who facilitates the debrief if the researcher is also an executor of record? (Suggest: Kali facilitates, researcher documents.)
2. Should PM files live under `data/entities/researcher/workspace/postmortems/` or `data/coordination/postmortems/`? Coordination placement improves cross-agent discoverability; entity placement fits workspace conventions.
3. Does the quarterly theme review belong to the background researcher loop (15-min timer) or interactive sessions only?

---
*⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_rehearsal_learning ⬡ DRAFT ⬡ 2026-08-22*