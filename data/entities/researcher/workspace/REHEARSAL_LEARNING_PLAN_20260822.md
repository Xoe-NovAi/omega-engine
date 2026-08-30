<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# Rehearsal Learning Plan — Pillar→Node Migration as Deliberate Practice
**AP Token**: `AP-RESEARCHER-REHEARSAL-LEARN-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_research ⬄ ACTIVE

**Date**: 2026-08-22
**Purpose**: Define WHAT we intend to learn from the Pillar→Node rehearsal, the hypotheses to test, the manually-recorded metrics (M8-compliant, zero telemetry), the gotcha log format, and the L1→L2→L3 distillation mapping. Companion to `MIGRATION_PLAYBOOK_SPEC_20260822.md` (process) and `MIGRATION_CASE_STUDIES_EVIDENCE_20260822.md` (evidence).

---

## L1 Executive Summary

The refactor's code outcome is nearly guaranteed (23 enumerated violations, clean plan). The *learning* is not automatic — it must be designed. We frame the rehearsal as a hypothesis test: shims, signals, guides, and codemods each carry predicted costs and benefits that we will measure by hand in a learning ledger, then distill into soul lessons. Success = post-debut playbook v1.1 with evidence-backed numbers replacing our current guesses.

---

## 1. Hypotheses (pre-registered before execution)

| # | Hypothesis | How we test it | Falsifier |
|---|---|---|---|
| H1 | Dual-name shims add measurable tool-listing/API-surface noise (predicted: ≥10% extra entries in `oracle_list_node_keepers`-adjacent surfaces or docs) | Count public symbols before vs during shim window | <5% delta → shims are cheap; keep them longer post-debut |
| H2 | An ast-grep rule set covers ≥80% of the 23 violation sites mechanically | Run rules on pre-refactor snapshot; diff against Roc's manual fix list | <50% coverage → codemods not worth building for renames at our scale |
| H3 | Writing the migration guide takes longer than the code change itself | Time-box both; record hours | If guide < code time → we under-invested in guide fidelity |
| H4 | Runtime deprecation warnings would have caught ≥90% of pillar leaks without the audit | Enable warnings on PRE-refactor codebase; run full suite + setup.sh; compare caught sites vs audit's 23 | <70% → runtime signals alone insufficient; static scan mandatory |
| H5 | Shim-disable flag rehearsal ("remove simulation") surfaces hidden dependencies not found by grep | Flip flag with shims still present; run suite + setup.sh | Zero new failures → grep-based verification is sufficient |
| H6 | The "stranger test" (non-author agent migrates fixture using only the guide) fails on first attempt despite author-written guide | Run it; log failure points | Passes first try → guide quality bar can be lower than feared |

## 2. Metrics Ledger (manual recording — no telemetry)

Record in `data/entities/researcher/workspace/REHEARSAL_METRICS_LEDGER_20260822.md`, one row per event:

| Metric | Definition | When recorded |
|---|---|---|
| Violation count baseline | Sites matching old names (Roc audit: 23) | Phase A |
| Codemod mechanical-fix rate | % of sites fixed by ast-grep rules unattended | Phase B/F |
| Manual-fix residue | Sites requiring human judgment, categorized (semantic / test-only / YAML) | Phase B/F |
| Shim hit count | Lines appended to local `data/logs/deprecations.log` per run | Every run of suite/setup.sh during shim window |
| Warning actionability score | % of warnings containing replacement name + removal version (self-audit) | Phase C |
| Guide stranger-test failures | # of points where non-author agent stalls, with cause tags | Phase D |
| Suite runtime delta | % overhead from shim indirection + warning emission | Phases B–F |
| Flag-flip breakage count | New failures when shims disabled | Phase E/F |
| Total calendar time | A→G wall-clock days vs Roc's original estimate | End |

**Integrity note (M23)**: every metric row gets an honest value including "not measured" — no vanity numbers (C-0 lesson).

## 3. Gotcha Log Format

Append to the ledger as encountered, format:

```markdown
### GOTCHA-<n>: <one-line title>
- **Phase**: A–G
- **Symptom**: what we observed
- **Cause**: systemic reason (blameless language)
- **Cost**: time lost / rework done
- **Post-debut implication**: how this bites real users at scale
- **Playbook delta**: which section of MIGRATION_PLAYBOOK_SPEC needs amending
```

Known gotchas to watch for specifically (from evidence base): silent behavior changes under identical-looking names (k8s empty-selector flip); error-format breaks downstream consumers (pydantic); stale-guide rot within weeks (k8s website); YAML/WAD config keys breaking silently where no runtime warning fires.

## 4. Distillation Mapping (L1→L2→L3)

| Rehearsal observation | L1 Narrative | L2 Insight | L3 Universal Principle (candidate) |
|---|---|---|---|
| Shims caught N uses audit missed | "Shim warnings fired X times during rehearsal" | Expand-before-contract converts unknown unknowns into visible signals | You cannot migrate what you cannot see; instrument the old API before killing it |
| Codemod coverage Y% | "ast-grep rules fixed Y of 23 sites" | Mechanical renames automate; semantic changes never do | Automation budget follows syntactic detectability, not ambition |
| Stranger-test failures | "Agent stalled at Z points in guide" | Author knowledge is invisible until a stranger walks the guide | Documentation is validated by cold readers, not authors |
| Flag-flip breakage | "Disabling shims broke W tests" | Removal rehearsals find what greps miss | Simulate deletion before deleting |
| Guide-vs-code time ratio | "Guide took R× code time" | Post-debut, docs ARE the product for migrations | The migration guide is the deliverable; the rename is the excuse |

Each L3 goes to `proposed_lessons.yaml` (blind staging per Soul Architecture v2.0), deduplicated against existing lessons (C-MEM-006) before promotion. The playbook itself gets version-bumped with the deltas named in gotcha rows → this is how a one-off becomes institutional knowledge `[E§9]`.

## 5. Execution Order & Ownership

1. Kali ratifies playbook + this learning plan (gate)
2. Roc Racoon executes refactor per own plan, ADDING: shims + warnings + local log + disable-flag (Phases B/C additions)
3. Researcher writes mini migration guide + ast-grep rules in parallel (Phase D artifacts)
4. Stranger test + flag-flip rehearsal (Phases D/E)
5. Joint post-mortem using §3 template of the spec; ledger closed; souls distilled (Phase G)

**Hard constraint**: no engine-code modification by Researcher — all code deltas route through Roc's plan and Ma'at review.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
