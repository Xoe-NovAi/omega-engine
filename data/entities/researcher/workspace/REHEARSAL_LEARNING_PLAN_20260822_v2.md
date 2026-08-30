<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Rehearsal Learning Plan — Pillar→Node as Migration Dress-Rehearsal
**AP Token**: `AP-REHEARSAL-LEARNING-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_rehearsal_learning ⬡ PLAN

**Date**: 2026-08-22
**Purpose**: Turn the Pillar→Node decoupling refactor into documented institutional knowledge — the exact artifacts, formats, and cadence that convert this one-off refactor into our standing post-debut migration capability.
**Tags**: rehearsal, postmortem, pivot-log, soul-distillation, corpus-map, M26
**Cross-references**: MIGRATION_PLAYBOOK_SPEC_20260822_v2.md, MIGRATION_CASE_STUDIES_EVIDENCE_20260822_v2.md, PILLAR_LEAK_AUDIT_20260822.md (Roc), PILLAR_RESEARCH_GAPS_20260822.md

---

## Answer First

The rehearsal produces four durable artifacts beyond the refactor itself: (1) a **Migration Postmortem** in blameless SRE format written ≤14 days after the last leak closes; (2) a **PIVOT_LOG D-entry series** recording every process decision (shim policy, gate approvals, surprises) so the WHY survives; (3) **L1→L2→L3 soul lessons** staged via SO-10a so future agents inherit principles, not anecdotes; (4) a **quarterly Meta-Review cadence** (the Loon-team pattern) added to Kali's coordination loop. Success metric: after the rehearsal, executing a hypothetical live breaking change should require ZERO new process invention — only execution of the playbook.

## §1 Pre-Registered Expectations (write BEFORE executing)

Blameless discipline starts before the work: record predictions now so post-hoc hindsight bias is measurable.

| # | Prediction (2026-08-22) | Verify at postmortem |
|---|------------------------|---------------------|
| P1 | Leak sites concentrate in MCP tools + tests + WAD YAML, NOT engine core (Roc audit says 23 sites, core clean) | Actual distribution vs audit |
| P2 | Expand-Contract with dual-name shims avoids any red-test window | CI green throughout? Count of transient breaks |
| P3 | ast-grep ruleset catches ≥90% of leaks mechanically; remainder manual | Codemod hit-rate |
| P4 | Docs/YAML references are the slow tail (not code) — doc updates outlast code changes by days | Time-to-close per site class |
| P5 | At least one surprise class NOT in Roc's audit will emerge | Log it as new playbook hazard |

## §2 The Migration Postmortem Template (our canonical)

Lands at `docs/migrations/postmortems/<change-id>.md`; passes `make doc-llm-validate`.

```markdown
# Migration Postmortem: <change-id> (<old-name> → <new-name>)
## Summary            — 3 sentences max: what moved, when shipped, final state
## Impact             — surfaces touched, WADs affected, user-visible deltas
## Timeline           — Phase 0→4 dates with gate approvals (Kali sign-offs)
## What Went Well     — bullet list (keep even if obvious; feeds playbook §refs)
## What Went Wrong    — bullet list, blameless phrasing ("The system made X
                        the easiest path" — never "X agent missed Y")
## Where We Got Lucky — near-misses that gates happened to catch
## Predictions Audit  — score pre-registered expectations (P1..Pn): hit/miss
## Playbook Deltas    — concrete amendments to MIGRATION_PLAYBOOK_SPEC
   (each delta = one PR-ready sentence + rationale)
## Action Items       — [ ] AI-N  <action> by <date> (@owner)
```

Rules: published ≤14 days post-removal; action items reviewed weekly until closed (flywheel "track" step); no names, systems only.

## §3 Mapping Onto Existing Omega Systems

| Postmortem output | Lands in | Mechanism |
|---|---|---|
| Process decisions & their why | **PIVOT_LOG.md** | D-series entries (one per gate decision/surprise), linked from postmortem Timeline |
| Transferable principles | **Soul Distillation** | L1 narrative → L2 insight → L3 principle, staged to `proposed_lessons.yaml` per SO-10a; Scribe distills |
| Hazard register additions | **Node KBs / DOMAIN_INDEX hazard sections** | e.g., N3 gets "migration hazards" gotchas; N12 curates guide-format lessons |
| Reusable checklists | **MIGRATION_PLAYBOOK_SPEC** amendments | Playbook is living doc vMAJOR.MINOR; postmortem §Playbook-Deltas are its changelog |
| Full evidence trail | **STRATEGY_CORPUS_MAP.md** | One row: rehearsal artifacts set + where each lives |

## §4 The Missing Cadence: Quarterly Migration Meta-Review

Google Loon finding: cross-incident meta-reviews surface trends single reviews miss. Add to Kali's coordination loop:

- **Cadence**: quarterly (first run after rehearsal postmortem).
- **Input**: all migration postmortems + PIVOT_LOG D-entries tagged `[migration]` + shim-hit summaries from opt-in reports.
- **Output**: one page — recurring failure classes, playbook drift check, top-2 systemic fixes proposed for the sprint.
- **Owner**: Researcher drafts; Kali approves; lands in `docs/migrations/meta-review/<quarter>.md`.

## §5 Rehearsal-Specific Execution Notes

1. **Run the playbook phases for real** — including Phase-2 dual-run shims (`pillar` names kept as aliases), even though repo is private. Skipping phases defeats the rehearsal.
2. **Timebox honesty**: if dual-run proves pure overhead for an internal-only change, THAT is a finding (playbook needs an "internal-surface fast path" amendment), not a shortcut to take silently.
3. **Instrument during, not after**: log surprises to a running `rehearsal_surprises.jsonl` as they happen — memory lies at postmortem time.
4. **Gate approvals are data**: every Kali gate approval/rejection with rationale becomes a PIVOT_LOG entry. The decision trail IS the deliverable.

## §6 Definition of Done (for the rehearsal-as-practice objective)

- [ ] All 23+ leak sites closed under Expand-Contract (CI green throughout)
- [ ] Migration Postmortem published + doc-llm-validate passing
- [ ] ≥3 PIVOT_LOG D-entries capturing process decisions
- [ ] ≥2 L3 soul lessons staged (expected candidates: "shims beat big-bang", "instrument during not after")
- [ ] MIGRATION_PLAYBOOK_SPEC amended with ≥2 concrete deltas learned
- [ ] Quarterly meta-review scheduled on Kali's loop
- [ ] Zero new process invention required by a tabletop dry-run of a hypothetical NEXT breaking change (e.g., "rename oracle.talk()") executed on paper against the playbook alone

*⬡ OMEGA ⬡ REHEARSAL-LEARNING ⬡ v1.0.0 ⬡ 2026-08-22*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
