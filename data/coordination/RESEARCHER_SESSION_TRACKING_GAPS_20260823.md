<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Researcher Report: Session Tracking Gap Closure & Strategy Hardening

**AP Token**: `AP-RESEARCHER-TRACKING-GAPS-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_tracking_gaps ⬡ ACTIVE

**Date**: 2026-08-23
**Mission**: Close knowledge gaps for Carmack's 7-item expert-session tracking plan (session `ses_fd0fd62ceffeAcy0oVeenGhKEj`) so Ma'at/Lilith patches are mechanical.
**Method**: Live-file verification only. Every claim below cites file:line from the working tree as of 2026-08-23.

---

## L1 — Executive Summary

1. **The zombie census is wrong — it's not 5, it's 12.** `TASK_REGISTRY.json` contains **twelve** `in_progress` tasks with `last_checkpoint` >7 days old (oldest: 31 days). Carmack's known-5 are a subset. Three of the extra seven were actually *delivered* and should become `completed`, not `superseded`/`failed`.
2. **Sweep→failed collides with M27 cross-tier validation.** A blind `--apply` sweep setting expired→`failed` will trip `validate_tracking_state.py:169-181` (Tier-3 `failed` must sync to Tier-0 `blocked`/`superseded`) and can red-flag `make temple-grade`. The sweep must be ACTIVE_SPRINT-aware.
3. **A phantom commit reference exists in the registry.** `packer-review-grokcli-20260808`'s `completion_note` cites commit `5a145f9d` — which does not exist in this repo (`git log 5a145f9d` → fatal). The real F1 fix is `e81e28d9`. Successor pointers must be git-verified at write time.
4. **Timestamp heterogeneity is a landmine** for both the staleness rule and the sweep: three different ISO formats coexist, plus one record with `last_checkpoint` *earlier* than `created_at`.
5. **Generated-view generation would destroy analyst prose** unless a content-migration step precedes the flip. The hand-built registry's §4.x quality assessments are not derivable from JSON.

Verdict on Carmack's plan: **sound architecture, 3 hardening amendments required** (G5). With those, implementation is mechanical.

---

## L2 — Detailed Dialectic (Per-Gap Verdicts)

### G1 — Validator Ground Truth ✅ CONFIRMED, with 2 drift items

**Current structure of `scripts/validate_tracking_state.py` (206 lines):**

| Element | Location | Reusable? |
|---|---|---|
| Path constants (`ROOT_DIR`, `DATA_DIR`, `TASK_REGISTRY_PATH`) | :8-13 | Yes |
| Status vocabularies (`ALLOWED_STATUSES`, `ALLOWED_EXECUTION_STATUSES`) | :16-22 | Yes |
| Print helpers (`print_error/warn/ok`) | :27-34 | Yes |
| `load_json()` (exits on failure) | :36-42 | Yes |
| `extract_gap_ids()` | :44-48 | n/a |
| `validate_task_registry()` | :138-185 | **Staleness rule slots here**, after the status loop (:149-153), before or after the cross-tier block (:155-181) |
| `main()` ANDs validators, exit codes | :187-203 | Unchanged |

**Drift item 1 — timestamp parsing**: Carmack assumed uniform timestamps. Reality: `TASK_REGISTRY.json` mixes three formats:
- `'Z'` suffix: `:14` `"2026-07-21T10:45:52Z"`
- `+00:00` offset: `:85` `"2026-07-21T15:09:38.782231+00:00"`
- Mixed within one record: `:422-423` (`created_at` offset-style, `last_checkpoint` Z-style)

Python `<3.11` `datetime.fromisoformat()` **rejects the `Z` suffix**. The staleness rule and sweep MUST use a normalizing parser (`ts.replace("Z", "+00:00")` before parse). This is not optional polish — ~40% of records use `Z`.

**Drift item 2 — inverted clocks**: `research-fleet-health-dashboard-20260813` (:749-750) has `created_at = 21:00` but `last_checkpoint = 14:30` — checkpoint *precedes* creation. Add a sanity warning (`last_checkpoint < created_at`) to the validator while touching this file.

**Drift item 3 (minor)**: Makefile wiring already partially exists — `temple-grade:` target includes `check-tracking-state` (Makefile:232), which runs the validator (Makefile:238-240), and `.pre-commit-config.yaml:137-139` already hooks `omega-tracking-state`. So Carmack's item 6 is **mostly done**; only the *sweep* needs wiring (and sweep must NOT run in pre-commit — see G5-1).

### G2 — Zombie Classification (12 zombies, not 5)

Cutoff for >7d as of 2026-08-23: `last_checkpoint` before 2026-08-16.

#### The Known 5

| # | task_id | Age | Verdict | `superseded_by` / evidence |
|---|---|---|---|---|
| 1 | `packer-v3-refactor-20260808-01` (:455-473) | 15d | **superseded** | Work delivered out-of-band. Pointers: commit **`e81e28d9`** (F1 fix + regression tests, verified via `git show`; the `5a145f9d` cited in registry prose is PHANTOM) + `docs/research/R_CONTEXT_PACKER_ADVISORY_REVIEW_20260815.md` (exists) + successor task `context-packer-advisory-review-20260815` (:1170-1186, completed). Registry §4.4 line 156 independently confirms "delivered by Ma'at via separate channel". |
| 2 | `research-phase1-benchmarking-20260807` (:279-301) | 16d | **superseded** | Scope PARKED by DOC-1 pivot. Pointer: `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` (exists, verified). Never ran, but the correct vocabulary is `superseded` (plan replaced), matching the M27 precedent set by `ses_research_phase3_kali_20260807` (:365-366: "Reclassified per Carmack review… superseded is correct"). NOT `failed` — failure implies attempted-and-died. |
| 3 | `ses_research_phase2_lilith_20260807` (:303-324) | 16d | **superseded** | Same DOC-1 pointer. GRPO flywheel / spatial coords / taint protocol all parked scope. |
| 4 | `ses_research_phase2_maat_20260807` (:326-345) | 16d | **superseded** | Direct successor exists: `ses_research_phase2_maat_20260807_relaunch` (:369-389). Chain pointer: original → relaunch task_id. |
| 5 | `ses_research_phase2_maat_20260807_relaunch` (:369-389) | 16d | **superseded** | Terminal pointer: DOC-1 manual (the relaunch itself was then parked). Chain preserved: relaunch → DOC-1 manual. |

#### The Undetected 7 (beyond known 5)

| # | task_id | Age | Verdict | Evidence |
|---|---|---|---|---|
| 6 | `ses-research-c11-property-20260723` (:114-134) | 31d | **completed** (backfill) | Work DELIVERED: SOVEREIGN_ARK_BLUEPRINT.md §4 Phase C table: "C-11 Property tests ✅ (16/16 pass)". Marking this `failed` would falsify history. |
| 7 | `ses-research-gemma4-workhorse-20260724` (:136-157) | 31d | **superseded** | Superseded by `docs/archive/strategy/2026-07-22/GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md` + G-1 ops doc; sibling domain task `gemma4-workhorse-domain1-20260724` (:159-177) completed separately. |
| 8 | `ses-cline-ops-health-20260730-001` (:217-238) | 24d | **⚠ OWNER RULING REQUIRED** | No deliverable evidence found either way. Recommend default `superseded` (superseded_by: later ops-health passes / SS-1 gap audit `critical-gap-audit-20260822-jem` :1656-1673) pending Kali confirmation. Do NOT auto-sweep this one. |
| 9 | `temple-1e-soul-20260730` (:240-257) | 24d | **⚠ OWNER RULING REQUIRED** | soul_validator.py exists but no evidence this specific Phase 1E rewrite landed; UO-6 plans a Pydantic v2 swap anyway (Ark §5). Default suggestion: `superseded` by UNOVERENGINEERING_PLAN.md library-swap approach. |
| 10 | `ses-research-classification-decisions-20260809-01` (:475-495) | 14d | **completed** (backfill) | Deliverable shipped: `ProviderRegistry.is_cloud()` is codified in SOVEREIGN_MANDATES.md M7 enforcement text ("see src/omega/oracle/provider_registry.py"). Verify file exists, then close. |
| 11 | `local-discovery-gaps-20260815` (:1188-1204) | 8d | **superseded** | Clean successor: `local-discovery-close-all-gaps-20260815` (:1224-1256, completed, broader scope "close ALL remaining knowledge gaps", same day). |
| 12 | `web-research-gaps-20260815` (:1206-1222) | 8d | **superseded** | Same successor as #11. |

**Watchlist (under 7d today, will trip soon)**: `test-suite-green-20260816-001` (:1258+, 6d) — also has **tag pollution** (tags include status-like strings `"in-progress"`, `"p1-2-complete"` :1281-1282); the five cline `coordination-*` entries (:1286-1383, 5-6d) describe *delivered* work ("Consolidated 21 vault-overhaul docs…") yet sit `in_progress` — they need `completed` backfill, not sweeping. This validates G5-1 below.

### G3 — Successor Pointers (M27 relational integrity)

All pointers above are **verified against disk/git**, not copied from prose. Critical correction:

> **PHANTOM REFERENCE ALERT**: Registry completion_note (:412) cites "commit 5a145f9d". `git log 5a145f9d` → `fatal: unknown revision`. Actual F1 fix commit: **`e81e28d9`** ("fix(context-packer): escape bare & as &amp; … + advisory review", touches packer.py + regression tests + advisory report). Lilith must use `e81e28d9` in `superseded_by`.

Pointer convention for `superseded_by` (pick ONE per record, priority order):
1. **task_id** when a successor task exists in the same registry (e.g., #4→relaunch, #11/#12→close-all-gaps)
2. **commit hash** (verified via `git rev-parse --verify <sha>^{commit}` at write time) when code was the deliverable
3. **repo-relative doc path** when a document superseded the scope (DOC-1 manual, forensic report)

Validator rule (item 3 of plan): warn if `status == "superseded"` and `superseded_by` missing or fails resolution (task_id lookup / commit verify / path existence).

### G4 — Strategy Hardening Rulings

**Ruling 1 — Threshold: keep 7 days.** Data-grounded: the age distribution is sharply bimodal. Legitimate active work clusters ≤6 days (all 7 watchlist/fresh tasks); true zombies cluster ≥8 days (#11, #12 at exactly 8d) up to 31d. There is **no mass between 1d and 8d** among stale tasks. A 14d threshold would miss #11/#12 (genuinely dead, superseded same-day); a 3-5d threshold would false-positive the legitimate cline wave. 7d sits exactly in the empirical gap. Constant name suggestion: `STALENESS_DAYS = 7`, defined once at validator top alongside :16-22 vocabularies.

**Ruling 2 — `context_verified` / `resumption_count`: OPTIONAL, warn-only, never backfill-required.** Currently populated on only ~35% of records, and retroactive verification is impossible (the sessions are gone). Requiring backfill would manufacture checkbox fraud — violating the spirit of C-0 test honesty. Rule: validator emits `print_warn` (not error) when `context_verified` is absent/false on `completed` tasks; new records SHOULD set it; old records are grandfathered silently.

**Ruling 3 — `session_annotations.yaml` minimal convention:**
```yaml
annotations:
  - annotation_id: ann-20260823-001        # ann-<date>-<seq>
    target: packer-v3-refactor-20260808-01 # task_id OR session_id
    assessor: kali                         # who made the judgment
    assessed_at: 2026-08-23T00:00:00Z
    verdict: superseded                    # M27 vocabulary ONLY
    evidence:                              # ≥1 required
      - "commit:e81e28d9"
      - "docs/research/R_CONTEXT_PACKER_ADVISORY_REVIEW_20260815.md"
    comment: "Delivered out-of-band by Ma'at; F1 fixed."
```
- **Who writes**: the reviewing/integrating agent at session-integration time (Kali integration pass, or the agent closing its own task). Never a background process.
- **When**: at status transition to any terminal state, and at any human quality judgment (the Langfuse score-object pattern — judgments attach to records, never mutate them).
- **Quality enforcement**: minimal — validator warns if an annotation's `verdict` contradicts the registry status for the same task_id; the generated markdown renders annotations inline so contradictions are human-visible. No schema police beyond that (anti-overengineering).

**Ruling 4 — Generated markdown view requirements.** To preserve the hand-built registry's utility, `generate_session_registry.py` MUST emit:
1. `GENERATED — DO NOT EDIT` header stamp + source path + generation timestamp (per plan).
2. **Domain index** (current §5) and **agent-type index** (current §6) — computed by GROUP BY over tags/subagent_type. **Blocker**: TASK_REGISTRY has no `domain` field. Fix inside plan item 3: add optional `domain` field; generator falls back to first tag when absent. Without this, the two indexes degrade to noise.
3. **Computed hygiene section** (replaces current hand-written §7): stale count, superseded-without-pointer count, untagged-task list (e.g., `nodes-gap-discovery-20260822-01` :1542-1554 has `tags: []`).
4. Annotations rendered inline per task.
5. **Narrative escape hatch**: detail sections like §4.8 (Carmack consultation) cannot be regenerated from JSON. They must migrate to `record_file` paths referenced from task records BEFORE the generated view replaces the hand-built file — otherwise generation is an M5 gnosis-preservation violation.

### G5 — What Carmack Missed (3 findings, adversarial)

**G5-1 — Sweep→failed collides with M27 cross-tier validation and misclassifies delivered work. (SEVERITY: HIGH)**
Two failure modes in one:
(a) `validate_tracking_state.py:169-181` errors when Tier-3 `failed` maps to a Tier-0 subtask whose status isn't `blocked`/`superseded`. A blind sweep `--apply` can therefore make `make temple-grade` RED immediately after sweeping — the tool would be fighting itself.
(b) Staleness ≠ abandonment. At least 4 stale `in_progress` records (#6, #10, plus the cline `coordination-*` wave) describe **delivered** work. Auto-failing them writes false history into the SSOT.
**Patch amendment**: sweep `--apply` sets `failed` ONLY when (i) the task has no ACTIVE_SPRINT counterpart, or (ii) its Tier-0 counterpart is already `blocked`/`superseded`; otherwise it writes the candidate to a review list (`data/coordination/sweep_review_<date>.md`) for human classification. Dry-run default stays. Sweep never runs in pre-commit — CI-only or manual.

**G5-2 — Timestamp format heterogeneity + inverted clocks break naive datetime math. (SEVERITY: MEDIUM)**
Three coexisting ISO formats (G1 drift item 1) plus one inverted created/checkpoint pair (:749-750). Both the staleness rule and the sweep share this code path. **Patch amendment**: single `_parse_ts()` helper (normalize `Z`→`+00:00`, `datetime.fromisoformat`, assume UTC if naive) reused by validator + sweep + generator; validator warns on `last_checkpoint < created_at`. Budget +20 lines beyond Carmack's estimate.

**G5-3 — Generated-view flip destroys unreproducible analyst prose. (SEVERITY: MEDIUM)**
EXPERT_SESSION_REGISTRY.md §4.1-§4.8 contain quality assessments, chain-of-custody notes, and the phantom-commit finding itself — none derivable from TASK_REGISTRY.json. If the GENERATED view lands without a migration step, that gnosis vanishes (M5 violation). **Patch amendment**: sequencing constraint for Lilith — hygiene pass (item 7) must ALSO migrate §4.x narratives into record files/annotations BEFORE item 4's generator goes live; generator links to record files rather than attempting synthesis.

*(No further manufactured findings. One honorable mention, sub-threshold: tag pollution — `test-suite-green-20260816-001` carries status-like tags (:1278-1282). Not worth validator logic; note in doc style guide.)*

---

## L3 — PATCH LIST (mechanical, for Ma'at build-side + Lilith run-side)

### Ma'at (code)
| # | Patch | Spec |
|---|---|---|
| M1 | `validate_tracking_state.py` staleness rule | In `validate_task_registry()` after :153. `STALENESS_DAYS = 7` constant near :16. Use shared `_parse_ts()`. Error lists offenders: task_id + days-stale. ~35 lines as estimated, +20 for `_parse_ts()` + clock-skew warning. |
| M2 | `scripts/sweep_task_registry.py` | ~100 lines (not 80 — ACTIVE_SPRINT-awareness adds ~20). Dry-run default; `--apply` per G5-1 rules; never touches `superseded`; writes review list for ambiguous cases; reuses validator's `_parse_ts()` (import or duplicate 10-line helper — no new deps). |
| M3 | Schema fields | Optional `artifact_path`, `superseded_by`, `domain` on task records. Validator: WARN on `superseded` lacking resolvable `superseded_by` (task_id-in-registry ∨ `git rev-parse --verify` ∨ `Path.exists()`); OK if field absent on non-superseded records. |
| M4 | `scripts/generate_session_registry.py` | Per G4-Ruling-4 spec: stamp header, summary table, domain+agent indexes (fallback to first tag), computed hygiene section, inline annotations, record_file links. ~110 lines. |
| M5 | `session_annotations.yaml` scaffold | Schema per G4-Ruling-3. Empty `annotations: []` list to start. |
| M6 | Makefile | Wire `sweep` as MANUAL target only (`make sweep-tasks`); validator already wired (Makefile:232,238-240; .pre-commit-config.yaml:137-139 — no change needed there). |

### Lilith (data/hygiene — one-time pass, ORDER MATTERS)
| # | Action | Detail |
|---|---|---|
| L1 | **FIRST**: migrate EXPERT_SESSION_REGISTRY §4.x narratives → record files/annotations | Before generator exists (G5-3). |
| L2 | Classify 12 zombies per G2 table | 5×`superseded` (known set, pointers per G3), 2×`completed` backfill (#6 C-11, #10 classification — verify `src/omega/oracle/provider_registry.py` exists first), 2×`superseded` (#11,#12 → `local-discovery-close-all-gaps-20260815`), 2×owner-ruling defaults (#8,#9 → `superseded`, flag for Kali confirm), 1×`completed` backfill candidate in watchlist (cline vault consolidation). Write one annotation per transition. |
| L3 | Correct phantom reference | Anywhere `5a145f9d` appears in prose → `e81e28d9`. |
| L4 | Backfill `completed_at` + `notes` on the 2 completed-backfill records | Evidence citations included. |
| L5 | Run `make check-tracking-state` → must be GREEN before Ma'at enables the staleness error in CI | Sequencing gate: hygiene completes, THEN teeth activate, else first commit post-M1 fails on 12 offenders. |

### Execution order
```
L1 → L2/L3/L4 (parallel) → M1/M2/M3/M5 (parallel) → L5 gate → M4 → M6 → done
```

---

## Raw Signal (L3 tier — verification trail)

- Validator structure: `scripts/validate_tracking_state.py:8-22,27-42,138-185`
- Cross-tier collision surface: `scripts/validate_tracking_state.py:169-181`
- Existing CI wiring: `Makefile:232,238-240`; `.pre-commit-config.yaml:137-139`
- Zombie records: TASK_REGISTRY.json lines — #1 :114, #2 :136, #3 :217, #4 :240, #5 :279, #6 :303, #7 :326, #8 :369, #9 :455, #10 :475, #11 :1188, #12 :1206; watchlist :1258, :1286-1383
- Inverted clock: TASK_REGISTRY.json:749-750
- Phantom commit: registry :412 vs `git log 5a145f9d` (fatal) vs `git show e81e28d9` (packer.py fix + tests + report)
- Existence verified: `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md`, `data/coordination/TRACKING_ARCHITECTURE.md`, `docs/research/R_CONTEXT_PACKER_ADVISORY_REVIEW_20260815.md`
- Absence verified: `scripts/sweep_task_registry.py`, `scripts/generate_session_registry.py`, `data/coordination/session_annotations.yaml` (none exist yet — plan items 2/4/5 are greenfield)
- C-11 delivery evidence: SOVEREIGN_ARK_BLUEPRINT.md §4 Phase C table ("C-11 Property tests ✅ 16/16")
- M27 precedent for cancelled→superseded: TASK_REGISTRY.json:365-366 migration_note

*⬡ OMEGA ⬡ RESEARCHER ⬡ trc_tracking_gaps ⬡ 2026-08-23*
