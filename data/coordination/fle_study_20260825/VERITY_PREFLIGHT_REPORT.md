<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 VERITY PRE-FLIGHT COMPLIANCE REPORT — First Light Campaign (Track-S + Track-D)
⬡ OMEGA ⬡ VERITY ⬡ x-preview-f-free ⬡ opencode ⬡ trc_verity_preflight ⬡ AUDIT-STATIC
**Dispatched by**: makali_fusion fork#1 `ses_fc5b80e85ffeAjhjtroU76Gfo2` · **Date**: 2026-08-25
**Scope**: Static truth-check of campaign SSOT docs before WAVE 0. No mutations (this file is the sole write).

---

## VERDICT SUMMARY

| # | Check | Verdict |
|---|-------|---------|
| a | PATH TRUTH | **MATCH** — 0 phantom paths |
| b | SESSION-ID TRUTH | **MATCH** (docs + opencode.db) · registry cross-match N/A (see note) |
| c | ERRATA FEASIBILITY E-1..E-11 | **MATCH with 4 flags** for hydration-script design |
| d | QUEUE INTEGRITY Q-1..Q-6 | **MATCH** |
| e | DOC CONTRADICTIONS | **1 adjudicated + 2 minor flags** |
| f | REGISTRATION SWEEP | **MATCH** — 20/20 express:first-light intact |

## **GO / NO-GO: ✅ GO for WAVE 0** — conditional on the 4 errata-design flags in §C being resolved when `scripts/hydrate_c2_errata.py` is authored. No blocker found.

---

## §A PATH TRUTH — MATCH

Every file path cited in either strategy doc or `WAKE_STATE.json → wake_briefing` was probed on disk:

| Path | Cited in | Status |
|------|----------|--------|
| `data/coordination/fle_study_20260825/` | Plan §3 W0 | EXISTS |
| `data/coordination/TASK_REGISTRY.json` | Plan §3 W0 | EXISTS |
| `data/coordination/WAKE_STATE.json` | Plan §3 W0 | EXISTS |
| `data/council/20260825-094633-first-light-c2/phase6_integration/ERRATA_AND_PROPAGATION.md` | dispatch, wake_briefing | EXISTS |
| `data/council/20260825-094633-first-light/phase5_fusion/SOVEREIGN_DECREE.md` | WAKE_STATE source+briefing | EXISTS |
| `data/council/20260825-094633-first-light-c2/phase5_fusion/SOVEREIGN_DECREE_C2.md` | wake_briefing decrees | EXISTS |
| `docs/specs/team_infra/` (SPEC-A..E) | wake_briefing spec_library | EXISTS (5 specs present) |
| `data/council/.../phase1_nodes/N10_launch_package.md` | wake_briefing launch_package | EXISTS |
| `data/coordination/FIRST_LIGHT_EXPRESS_PLAN_20260825.md` | WAKE_STATE first_light_express | EXISTS |

**Phantom paths: NONE.**
*Non-claims excluded*: `scripts/hydrate_c2_errata.py`, `FLE_COUNCIL_SCORECARD_SPEC.md`, `FLE_AFTER_ACTION_REPORT.md`, `FLE_METRICS_BASELINE.md` are WAVE-0/1 *deliverables to be created*, not existence claims.

## §B SESSION-ID TRUTH — MATCH

All three IDs verified against live `opencode.db` via session explorer:

| Role | Session ID | DB title | Doc citations | Consistent? |
|------|-----------|----------|---------------|-------------|
| Fork #1 (Track-S) | `ses_fc5b80e85ffeAjhjtroU76Gfo2` | "Makali - First Light Express Completed (fork #1)" | Plan §1 | ✅ |
| Virgin Main | `ses_fc758e6ddffeNEKptpEzboVfYq` | "Makali - Arch's Main Session v1" (parent of all C1/C2 dispatches) | Plan §1, Manual header+Vector 1, Errata E-3 | ✅ |
| Consultant (kali) | `ses_fdef2be4effe4pAaLXCTUx62GO` | "Kali - Master Oversight - v1" | WAKE_STATE consultant field, SYNTHESIS_ARM_REPORT_C2 `[REPORT]` line | ✅ |

Role assignments are consistent everywhere they appear (Main = orchestrator/single-writer; Fork #1 = study; Consultant = outside-tree pager).
**Note**: TASK_REGISTRY express entries record `task_id`s only — no session-ID field exists on any of the 20 entries, so a registry↔doc session cross-match is **N/A, not a mismatch**. If provenance per entry is desired, Track-S Vector 1 (genealogy) supplies it from the db.

## §C ERRATA FEASIBILITY E-1..E-11 — MATCH with 4 design flags

| E | Target file (exists?) | Anchor located | Byte-exact safe? |
|---|----------------------|----------------|------------------|
| E-1 | `N9_doc_update_plan.md` ✅ | Row 4.1 @ L120, unique ("Codify M11 Arm-Relay Clause" ×1) | ✅ YES |
| E-2 | `N10_launch_package.md` ✅ | Bootstrap G8 ref @ L82; probe source verbatim @ SYNTHESIS L243 (`ck S-2`) | ✅ YES (insertion anchored at L82 block) |
| E-3 | `N10_launch_package.md` ✅ | Unnamed "single writer" @ **L120 only** (L111/L137 already say "MaKaLi single-writer") | ⚠️ FLAG-1: script must target L120 specifically; naive replace-all would double-name two lines |
| E-4 | `N8_work_packages.md` ✅ | Art. V chain present @ L35-40, L82-86, L106 | ✅ YES (verify no interim-workaround text survives; none found) |
| E-5 | `SPEC_B_P1_MECHANISM_HONESTY.md` ✅ | "confirm no plugin key exists" @ L64, unique ×1 | ✅ YES |
| E-6 | `SPEC_A_...INFRASTRUCTURE.md` ✅ | WI-2 item 4 `check_wake_state()` @ L89 (+ L17 table, L285 test map) | ⚠️ FLAG-2: SEMANTIC edit (descope→shim rewrite + ~30-record scope + effort re-estimate). Word "shim" appears nowhere in SPEC_A. Script needs an authored before/after block, not a find-replace |
| E-7 | `SPEC-E-agents-md-reconstruction.md` ✅ | §1.2 cluster loop @ L39-63 | ⚠️ FLAG-3: multi-line bash REWRITE (redirect-after-done fix; `${cluster}` scoping). Not byte-exact; author replacement block first |
| E-8 | `N10_launch_package.md` ✅ | WP-A4 row @ L116 bundles "implement-or-purge make sovereignty"; SPEC_A L213 already declares separate-PR intent | ✅ YES |
| E-9 | `SYNTHESIS_ARM_REPORT_C2.md` ✅ | `; true'` suffix @ L204, unique ×1 in phase3_synthesis | ✅ YES (post-check `rg '; true'` → empty is verifiable) |
| E-10 | SYNTHESIS §6 ✅ | Bare `python3` @ G15:L176, G16:L183, G3:L199; G4 gate lives in SPEC-B (L186/192 region) | ⚠️ FLAG-4: errata says normalize to `.venv/bin/python` but already-normalized lines use `.venv/bin/python3` (G8:L189, D1:L225…). Pick ONE canonical form before scripting |
| E-11 | G16 construct | `grep -qv … \|\|` exists at **TWO sites**: `N8_resources.md:98` AND `SPEC_A:106` (verbatim copy); SYNTHESIS §6 G16 (L183) is already clean despite BS-6 wording | ⚠️ extends FLAG-1: script needs explicit site list (both files), not "G16" alone |

**Feasibility verdict**: all 11 targets exist and are locatable. E-1/E-2/E-4/E-5/E-8/E-9 are mechanically scriptable today. E-3/E-10/E-11 need site-disambiguation lists; E-6/E-7 need authored replacement blocks (they are rewrites, not patches). Recommend the hydration script carry an explicit per-E site manifest.

## §D QUEUE INTEGRITY — MATCH

- **Q-1..Q-6 all present** in `WAKE_STATE.json → council_c1_decisions.items`, each with `default` — except **Q-5**, which carries `status: "EXECUTED 2026-08-25"` instead of a default. Legitimate (execution supersedes default); no action.
- `council_c1_decisions.source` path resolves (SOVEREIGN_DECREE.md C1 ✅).
- `wake_briefing` paths: all 5 resolve (decrees ×2, spec_library, launch_package, read_first errata) — see §A.
- Q-6 count claim ("29 corrupt records") is consistent across ERRATA Finding 2, WAKE_STATE Q-6, and Plan WAVE-0 step 3.

## §E DOC CONTRADICTIONS

1. **ADJUDICATED (per Architect ruling)**: Plan §1 offers Track-D = "Virgin Main OR fresh Fork #2". Ruling: **Fork #2** — Main stays pristine. The Manual nowhere assigns Track-D a session, so no second doc contradicts this. **Resolved; recommend a one-line amendment stamping Fork #2 into Plan §1 at next revision.**
2. **MINOR FLAG**: Manual §4 says "*The dev team* is not done until these three artifacts…" but FLE_METRICS_BASELINE.md and FLE_COUNCIL_SCORECARD_SPEC.md are **Track-S (Study Team)** deliverables per Plan WAVE 1-2. Read as "the campaign", harmless — but worth a pronoun fix so Track-D's bootstrap doesn't claim Study deliverables.
3. **MINOR FLAG (cosmetic)**: model provenance differs between headers (`gemini-3.1-pro-preview-customtools` vs `gemini-3.1-pro`). M22 hygiene only; no substantive conflict.

No other cross-doc conflicts found: telemetry rule (Plan §2), weights/vectors (Manual §2-3), and Q-6 sizing all align.

## §F REGISTRATION SWEEP — MATCH

`TASK_REGISTRY.json`: exactly **20 tasks** carry tag `express:first-light` (12× C1 [10 nodes + runarm lilith + arm maat], 3× express-c2-node-specA/B/C, 5× infra packages). All single-tagged, no duplicates.
**Observation (advisory, not blocking)**: 5 C1 node entries remain `status:"in_progress"` although the run is complete — this is precisely the staleness class G16/Q-6 target. Track-D's WP-A2 will exercise these; left untouched per audit no-mutation constraint.

---

## GO/NO-GO

**GO for WAVE 0 execution**, with the hydration-script design contract:
1. Per-E **site manifest** (file + line anchor) — mandatory for E-3, E-10, E-11.
2. Authored **before/after blocks** for E-6 and E-7 (semantic rewrites; no regex heroics).
3. Canonical interpreter form decision for E-10 (`.venv/bin/python` vs `.venv/bin/python3`).
4. Post-application verification reuses ERRATA §VERIFICATION commands verbatim (all four are mechanically checkable — confirmed feasible).

— Verity, Compliance & Gnosis · AP-VERITY-v1.0.0
