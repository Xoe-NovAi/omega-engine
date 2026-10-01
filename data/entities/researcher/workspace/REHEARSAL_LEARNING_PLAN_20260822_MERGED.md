<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Rehearsal Learning Plan — Pillar→Node as Migration Dress-Rehearsal (Canonical Merge)
**AP Token**: `AP-REHEARSAL-LEARNING-v1.1.0`
⬡ OMEGA ⬡ RESEARCHER+KALI ⬡ opencode ⬡ trc_rehearsal_learning ⬡ MERGED-DRAFT

**Date**: 2026-08-22
**Status**: MERGED DRAFT — awaiting Kali ratification
**Provenance**: Merge of `REHEARSAL_LEARNING_PLAN_20260822.md` (fresh session) + `REHEARSAL_LEARNING_PLAN_20260822_v2.md` (primed session). Companion to `MIGRATION_PLAYBOOK_SPEC_20260822_MERGED.md`.
**Tags**: rehearsal, postmortem, pivot-log, soul-distillation, corpus-map, M8, M23, M26

---

## Answer First

The refactor's code outcome is nearly guaranteed (23 enumerated violations, clean plan). The *learning* is not automatic — it must be designed. The rehearsal produces four durable artifacts beyond the code: **(1)** a blameless Migration Postmortem ≤14 days after the last leak closes; **(2)** a PIVOT_LOG D-entry series capturing every process decision so the WHY survives; **(3)** L1→L2→L3 soul lessons staged via SO-10a so future agents inherit principles, not anecdotes; **(4)** a quarterly Meta-Review cadence added to Kali's coordination loop. Success metric: executing a hypothetical NEXT breaking change requires ZERO new process invention — only playbook execution.

## §1 Pre-Registered Hypotheses (recorded BEFORE execution — hindsight-bias control)

| # | Hypothesis | Test | Falsifier |
|---|---|---|---|
| H1 | Dual-name shims add measurable API-surface noise (≥10% extra entries in adjacent tool listings/docs) | Count public symbols before vs during shim window | <5% delta → shims cheap; keep longer post-debut |
| H2 | ast-grep ruleset covers ≥80% of the 23 violation sites mechanically | Run rules on pre-refactor snapshot; diff vs Roc's manual fix list | <50% → codemods not worth building at our scale |
| H3 | Writing the migration guide takes longer than the code change itself | Time-box both; record hours | Guide < code time → guide under-invested |
| H4 | Runtime deprecation warnings alone catch ≥90% of pillar leaks without the manual audit | Enable warnings on PRE-refactor codebase; run suite + setup.sh; compare vs audit's 23 | <70% → runtime signals insufficient; static scan mandatory |
| H5 | Shim-disable flag rehearsal surfaces hidden dependencies grep missed | Flip flag with shims present; run suite + setup.sh | Zero new failures → grep verification sufficient |
| H6 | "Stranger test" (non-author agent migrates fixture using ONLY the guide) fails on first attempt | Run it; log failure points | Passes first try → guide quality bar can be lower than feared |

## §2 Metrics Ledger (manual recording — zero telemetry, M8)

Ledger: `data/entities/researcher/workspace/REHEARSAL_METRICS_LEDGER_20260822.md`, one row per event:

| Metric | Definition | When |
|---|---|---|
| Violation count baseline | Sites matching old names (Roc audit: 23) | Phase 0 |
| Codemod mechanical-fix rate | % sites fixed by ast-grep unattended | Phases 1/3 |
| Manual-fix residue | Sites needing judgment, categorized (semantic/test-only/YAML) | Phases 1/3 |
| Shim hit count | Lines appended to `data/logs/deprecations.log` per run | Every suite/setup.sh run during window |
| Warning actionability score | % warnings containing replacement name + removal version (self-audit) | Phase 1 |
| Guide stranger-test failures | # stalls by non-author agent, with cause tags | Phase 2 |
| Suite runtime delta | % overhead from shim indirection + warning emission | Phases 1–3 |
| Flag-flip breakage count | New failures when shims disabled | Phase 3 |
| Total calendar time | Wall-clock days vs Roc's original estimate | End |

**Integrity note (M23)**: every metric row gets an honest value including "not measured" — no vanity numbers (C-0 lesson).

**Instrument during, not after**: log surprises to running `rehearsal_surprises.jsonl` as they happen — memory lies at postmortem time.

## §3 Gotcha Log Format

```markdown
### GOTCHA-<n>: <one-line title>
- **Phase**: 0–4
- **Symptom**: what we observed
- **Cause**: systemic reason (blameless language)
- **Cost**: time lost / rework done
- **Post-debut implication**: how this bites real users at scale
- **Playbook delta**: which section of MIGRATION_PLAYBOOK_SPEC needs amending
```

Known gotchas to watch (from evidence base): silent behavior changes under identical-looking names (k8s empty-selector flip); error-format breaks downstream consumers (pydantic); stale-guide rot within weeks (k8s website); YAML/WAD config keys breaking silently where no runtime warning fires.

## §4 Mapping Onto Existing Omega Systems

| Postmortem output | Lands in | Mechanism |
|---|---|---|
| Process decisions & why | PIVOT_LOG.md | D-series entries (one per gate decision/surprise), linked from Timeline |
| Transferable principles | Soul Distillation | L1→L2→L3 staged to `proposed_lessons.yaml` per SO-10a; Scribe distills |
| Hazard register additions | Node KBs / DOMAIN_INDEX hazard sections | N3 gets "migration hazards" gotchas; N12 curates guide-format lessons |
| Reusable checklists | MIGRATION_PLAYBOOK_SPEC amendments | Playbook is living doc vMAJOR.MINOR; postmortem §Playbook-Deltas = its changelog |
| Full evidence trail | STRATEGY_CORPUS_MAP.md | One row: rehearsal artifact set + where each lives |

### Distillation seeds (candidate L3 principles)

| Observation | L1 Narrative | L2 Insight | L3 Universal candidate |
|---|---|---|---|
| Shims caught N uses audit missed | "Shim warnings fired X times" | Expand-before-contract converts unknown unknowns into visible signals | You cannot migrate what you cannot see; instrument the old API before killing it |
| Codemod coverage Y% | "ast-grep fixed Y of 23 sites" | Mechanical renames automate; semantic changes never do | Automation budget follows syntactic detectability, not ambition |
| Stranger-test failures | "Agent stalled at Z points" | Author knowledge invisible until a stranger walks the guide | Documentation is validated by cold readers, not authors |
| Flag-flip breakage | "Disabling shims broke W tests" | Removal rehearsals find what greps miss | Simulate deletion before deleting |
| Guide-vs-code time ratio | "Guide took R× code time" | Post-debut, docs ARE the product for migrations | The migration guide is the deliverable; the rename is the excuse |

Each L3 goes to `proposed_lessons.yaml` (blind staging per Soul Architecture v2.0), deduplicated against existing lessons before promotion.

## §5 Quarterly Migration Meta-Review (new standing cadence)

Google Loon finding: cross-incident meta-reviews surface trends single reviews miss.

- **Cadence**: quarterly; first run after rehearsal postmortem.
- **Input**: all migration postmortems + PIVOT_LOG D-entries tagged `[migration]` + opt-in shim-hit summaries.
- **Output**: one page — recurring failure classes, playbook drift check, top-2 systemic fixes proposed for sprint.
- **Owner**: Researcher drafts; Kali approves; lands `docs/migrations/meta-review/<quarter>.md`.

## §6 Execution Order & Ownership

1. Kali ratifies merged playbook + this plan (gate)
2. Roc Racoon executes refactor per own plan, ADDING: shims + warnings + local log + disable-flag (Phases 1–2 additions)
3. Researcher writes mini migration guide + ast-grep rules in parallel (Phase 2 artifacts)
4. Stranger test + flag-flip rehearsal (Phases 2–3)
5. Joint post-mortem using Playbook §8 template; ledger closed; souls distilled (Phase 4)

**Hard constraint**: no engine-code modification by Researcher — all code deltas route through Roc's plan and Ma'at review.

## §7 Definition of Done (rehearsal-as-practice objective)

- [ ] All 23+ leak sites closed under Expand-Contract (CI green throughout)
- [ ] Migration Postmortem published + doc-llm-validate passing
- [ ] ≥3 PIVOT_LOG D-entries capturing process decisions
- [ ] ≥2 L3 soul lessons staged
- [ ] MIGRATION_PLAYBOOK_SPEC amended with ≥2 concrete deltas learned
- [ ] Quarterly meta-review scheduled on Kali's loop
- [ ] Zero new process invention required by tabletop dry-run of a hypothetical NEXT breaking change ("rename oracle.talk()") executed on paper against the playbook alone

---
*Merge executed by Kali 2026-08-22. Ratification pending.*

*⬡ OMEGA ⬡ REHEARSAL-LEARNING ⬡ v1.1.0-merged ⬡ 2026-08-22*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
