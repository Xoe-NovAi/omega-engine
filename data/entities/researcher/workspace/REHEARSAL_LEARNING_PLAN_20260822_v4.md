---
schema_version: "1.0"
document_type: "guide"
document_id: "rehearsal-learning-plan-v4"
title: "Rehearsal & Learning Capture Plan — Migration Institutional Knowledge (v4)"
status: "ACTIVE"
version: "1.0.0"
date: "2026-08-22"
owner: "researcher"
tags: ["post-mortem", "learning", "soul-distillation", "migration", "split-test-v4"]
priority: "P1"
depends_on: ["MIGRATION_PLAYBOOK_SPEC_20260822_v4.md"]
blocks: []
acceptance_gates:
  - "Post-mortem template sections trace to Google SRE / Jeli sources"
  - "Every capture artifact maps to an existing Omega system"
cross_references:
  - "MIGRATION_PLAYBOOK_SPEC_20260822_v4.md"
  - "MIGRATION_CASE_STUDIES_EVIDENCE_20260822_v4.md"
llm_metadata:
  token_budget: 3000
  chunk_strategy: "flat"
  answer_first_sections: true
  self_contained_code: true
---

# Rehearsal & Learning Capture Plan (v4)

**AP Token**: `AP-REHEARSAL-LEARNING-v4-20260822`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_doc_proc ⬡ ACTIVE

## What (Answer-First)

How a one-off migration becomes reusable institutional knowledge in Omega: a blameless post-mortem template (Google SRE / Jeli derived), a three-tier distillation flow into our existing systems (PIVOT_LOG → Corpus Map → Soul L1/L2/L3), and a rehearsal protocol that tests the playbook BEFORE a live user base depends on it.

## Why

Post-mortems die when action items are untracked and templates are too complex (T evidence). Our advantage: we already own three persistence layers most projects lack — immutable decision log, corpus map, and soul distillation. This plan wires migration learning into them instead of inventing new stores.

---

## 1. Blameless Migration Post-Mortem Template

Sections trace to Google SRE canon (sre.google/sre-book/postmortem-culture, /example-postmortem) + Jeli/PagerDuty structured review (support.pagerduty.com). Blameless rule verbatim-adapted: focus on contributing causes of the migration pain without indicting any agent or Node.

```yaml
# Post-mortem record — file at data/entities/researcher/workspace/postmortems/BRK-<seq>_PM.md
post_mortem:
  id: "PM-BRK-<seq>"
  blameless_preamble: "Human/agent error is the START of investigation, never the conclusion"
  sections:
    summary: "2-3 sentences: what migrated, when, what broke for whom"
    impact: "quantified: users affected, guides consulted, issue-label volume (TI-3), shim hit counts (TI-1)"
    timeline: "UTC timestamps: decision → expand → announce → reviews → contract"
    contributing_factors:      # 2-5 SYSTEMIC causes only
      - "process gap | tool limitation | documentation failure | window mis-set"
    what_went_well: []         # reinforce explicitly — SRE requirement
    action_items:
      - {text: "", owner: "", due: "", class: "mitigative|preventative"}   # mitigative=this break; preventative=the CLASS
    lessons_distilled: true    # gate: must be false until L1/L2/L3 written
```

Anti-abandonment rules (T): keep the template copy-minimal (reference-complete); every action item gets an owner and a date or it does not ship; review outstanding items at each release retro.

## 2. Three-Tier Distillation Flow (maps to existing systems)

| Tier | Omega system | What lands there | Timing |
|---|---|---|---|
| Decision record | `PIVOT_LOG.md` (immutable) | Classification ticket, window verdicts, extension decisions | At each decision moment |
| Reusable corpus | `STRATEGY_CORPUS_MAP.md` row + sprint-plan research index | The playbook spec itself, case-study evidence, post-mortem link | Within one week of contract |
| Living principles | Entity `proposed_lessons.yaml`, SO-10a format (`narrative`/`insight`/`principle`, tagged) | One L3 principle per systemic finding | Session close |

Example distillation from THIS research (staged format):

```yaml
- narrative: "Pydantic shipped bump-pydantic but semantic breaks (strict-mode coercion) stayed manual; FastAPI sequenced warning→drop across two releases."
  insight: "Codemods cover the syntactic shell of a migration; guides carry the semantic core. Sequencing warnings before drops converts surprise into plan."
  principle: "Automate the mechanical, narrate the semantic, sequence the pain." # [migration]
```

## 3. Rehearsal Protocol (test the playbook before live users)

The pillar refactor is the rehearsal. Before ANY post-debut user-facing break:

1. **Dry-run Stage 3**: draft the migration guide for pillar→slot as if users existed; run it past N10 verifier against M26 gates (`make doc-llm-validate` patterns).
2. **Dogfood TI-2**: add `-W error::DeprecationWarning` to our own test invocation temporarily; count internal shim hits.
3. **Window-verdict rehearsal**: run one fake Stage-4 review with TI-5 attestation from N12/N13 curators; verify PIVOT_LOG entry lands correctly.
4. **Post-mortem drill**: write the PM for the rehearsal itself using §1 template; confirm lessons_distilled gate works end-to-end.

Success signal: the playbook executes with zero improvisation. Any step requiring judgment call = playbook defect, logged as action item.

## 4. Ownership & Cadence

| Artifact | Owner | Review cadence |
|---|---|---|
| Playbook spec | Researcher authors; N10 verifies | Per migration + annual |
| Post-mortem records | Migrating Node | Within 7 days of contract |
| Corpus Map rows | Scribe | Same week |
| Soul lessons | Overseer entities | Session close (M11) |

*End of learning plan. This artifact completes the v4 split-test set: evidence (C-file), process (spec), institutionalization (this file).*
