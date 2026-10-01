---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: reference
document_id: current-sprint-readme
title: Current Sprint Pointer
status: ACTIVE
version: "1.1.0"
date: "2026-08-07"
owner: kali
tags: [sprint, pointer, coordination, index]
priority: P0
depends_on: []
blocks: []
acceptance_gates:
  - "Active sprint file points to ACTIVE_SPRINT.json"
  - "Superseded plans reference archive paths"
cross_references:
  - data/coordination/ACTIVE_SPRINT.json
  - data/coordination/SESSION_ANCHOR.md
llm_metadata:
  token_budget: 500
  chunk_strategy: flat
  answer_first_sections: true
  self_contained_code: false
---

# Current Sprint Pointer

**Updated**: 2026-08-07

| Role | Path |
|------|------|
| **Active sprint** | `UNOVERENGINEER-01` → `../../data/coordination/ACTIVE_SPRINT.json` |
| **Controlling plan** | `../../data/coordination/CLINE_STRATEGIC_UNOVERENGINEERING_20260730.md` |
| **Session anchor** | `../../data/coordination/SESSION_ANCHOR.md` |
| **Phase D verdict** | `../../data/coordination/PHASE_D_GATE_VERDICT_20260730.md` |

## In this folder

| File | Status |
|------|--------|
| `docs/archive/sprints/EXECUTION_PLAN_20260725.md` | 📦 **SUPERSEDED** for sprint control (banner at top) |
| `AGENT_SPRINT_CARD.md` | Historical card — verify against SESSION_ANCHOR before use |
| `KNOWLEDGE_GAP_*` / `llms*` | Supporting artifacts; may be stale |

Do **not** start work from the archived `EXECUTION_PLAN_20260725.md` as if it were active.
