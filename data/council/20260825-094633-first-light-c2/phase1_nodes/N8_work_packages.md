<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# N8 — WORK PACKAGES: Council 2 Dev-Team Remediation Breakdown
⬡ OMEGA ⬡ LILITH/node8 ⬡ opencode/x-preview-f-free ⬡ trc_first_light_c2_wp ⬡ COUNCIL-2 PREP ARTIFACT
**Session**: `20260825-094633-first-light-c2` · **Date**: 2026-08-25
**Authority**: SOVEREIGN_DECREE.md (`data/council/20260825-094633-first-light/phase5_fusion/SOVEREIGN_DECREE.md`) Art. V, VI, IX, X priority tiers, §4 gates G1–G30
**Gate source (verbatim)**: SYNTHESIS_ARM_REPORT.md §6 G1–G28 + decree §4 G29/G30. Gate commands are NOT restated in full here where a package's runnable form lives in `N8_resources.md` §2 (paste-and-run checklist) — this file cites gate IDs; the resources file carries the copy-paste bash.
**Spec inputs**:
- SPEC-A (`docs/specs/team_infra/SPEC-A-p0-truth-infra.md`) — **PENDING** (Ma'at Build Arm, parallel draft)
- SPEC-B (`docs/specs/team_infra/SPEC-B-p1-mechanism-honesty.md`) — **PENDING** (Ma'at Build Arm)
- SPEC-C (`docs/specs/team_infra/SPEC-C-p1-security-posture.md`) — **PENDING** (Ma'at Build Arm)
- SPEC-D (`docs/specs/team_infra/SPEC-D-p2-hygiene.md`) — DRAFTED (lilith/node6) · cluster total 29.5h
- SPEC-E (`docs/specs/team_infra/SPEC-E-agents-md-reconstruction.md`) — DRAFTED (lilith/node7) · ≈10h
**Rules honored**: M10 slot-based ownership (no new agents) · Art. XII anti-big-bang sizing (every package incrementally committable) · pairwise binding Art. II.2 (validator ships with first fix).

---

## §1 PACKAGE REGISTER

Effort estimates for SPEC-D/E packages are copied from their drafted specs. SPEC-A/B/C estimates are **PROVISIONAL** pending spec ratification — dev team re-baselines at integration start.

### P0 — Truth-Bearing Infrastructure (Art. X tier 1)

| ID | Package | Owner slot | Inputs | Depends on | Gates | Effort | Status |
|---|---|---|---|---|---|---|---|
| **WP-IX** | Corrupt entity-YAML repair (parseability-only, snapshots committed, single writer) | MaKaLi single-writer (decree Art. IX names the actor; NOT re-delegated) | Decree Art. IX; Q-5 directive | none — FIRST package | **G8** | 2h | EXECUTABLE (verify-first: run G8; repair only red loci) |
| **WP-A1** | Pre-commit framework install + tracking-hook fire verify | `node --slot P3` (build-side infra role) | SPEC-A (pending); decree Art. II.4; Ma'at F1 ordering | none | **G7** | 3h PROV | EXECUTABLE |
| **WP-A2** | Validator ERROR-class checks: future-dating, hours-resolution staleness, blockers[] vocab scan, WAKE_STATE parse+staleness | `node --slot P4` (validation role) | SPEC-A (pending); decree Art. III; N8 F-1/F-2 evidence | WP-A1 (hooks must exist to fire new checks) | **G15, G16** (+D6.1/D6.2 pattern for WAKE_STATE block) | 8h PROV | EXECUTABLE |
| **WP-A3** | Registry-writer atomicity (mkstemp/os.replace in task_registry.py) | `node --slot P3` | SPEC-A (pending); decree Art. X P0; N2 F-2.1 | none | **G6** | 3h PROV | EXECUTABLE |
| **WP-A4** | Mandate enforcement-stamps — machine-derived from Makefile+hooks, never hand-written; temple-grade stub removed; `make sovereignty` implemented or refs purged | `node --slot P5` (governance/mandates role) | SPEC-A (pending); decree Art. II.1–II.3 | WP-A1 (stamps derive from installed hook inventory) | **G12, G13** | 6h PROV | EXECUTABLE |
| **WP-A5** | M8 zero-telemetry gate regex fix (word-boundary/import-line anchor) | `node --slot P3` | SPEC-A (pending); decree Art. II.5; ics.py:197 false-positive evidence | none | **G29** | 1h PROV | EXECUTABLE |

### P1 — Mechanism Honesty (Art. X tier 2)

| ID | Package | Owner slot | Inputs | Depends on | Gates | Effort | Status |
|---|---|---|---|---|---|---|---|
| **WP-B1** | Plugin registration path fixes (dead `.opencode/plugin/` paths → live dirs) | `node --slot P3` | SPEC-B (pending); decree Art. VIII.1; GAP-1 verdict | WP-A1..A5 merged (P0→P1 tier gate) | **G1** | 2h PROV | EXECUTABLE |
| **WP-B2** | `instructions[]` → `prompt:{file:}` migration, 12 agent defs (data-exposure class, HIGH urgency per GAP-4) | `node --slot P3` | SPEC-B (pending); decree Art. VIII.4 | WP-B1 (same config surface; avoids merge conflicts) | **G10** | 6h PROV | EXECUTABLE |
| **WP-B3** | Provider-order/M7 text alignment to Ark D-355 + credentialed-fabric honesty statement | `node --slot P5` | SPEC-B (pending); decree Art. VIII.5; Ark D-355 | WP-A1..A5 merged | **G3, G4** | 3h PROV | EXECUTABLE |
| **WP-B4** | `validate_llm_docs.py --strict` code change (strict mode does not exist today — verity confirmed) | `node --slot P4` | SPEC-B (pending); decree Art. III | WP-A2 (shares validator codebase patterns) | **G22** | 4h PROV | EXECUTABLE |
| **WP-B5a** | Discovery fix: `task_registry.py:134` status-filter bug + `.gitignore:109` ripgrep blindness | `node --slot P4` | SPEC-B (pending); decree Art. V.1; jem GAP-5 file:line citations | WP-A1..A5 merged | **G20** | 3h PROV | EXECUTABLE |
| **WP-B5b** | Identity repair via staged payloads (`registration_payloads.json` mass-apply; canonical `subagent_type="node<N>"`, `entity="node<N>"`, 4-tag set); retrieval verification ≥10 required | MaKaLi single-writer (decree Art. V.2 "single writer AFTER discovery fix") | Decree Art. V.2–V.3; §5 tracker directive 1; COUNCIL2_PLAN §3 payload path | **WP-B5a — HARD EDGE, G20 green BEFORE any identity write** | **G21** | 3h PROV | EXECUTABLE after B5a |
| **WP-C1** | `"/*": "allow"` risk-acceptance decision recorded + wildcard removed or annotated | Architect decides (WAKE_STATE **Q-3**); `node --slot P3` executes record | SPEC-C (pending); decree Art. VIII.2 / T-7 ruling | **BLOCKED on Architect Q-3 decision** | **G2** | 1.5h PROV (post-decision) | ⛔ BLOCKED |
| **WP-C2** | Depth-vs-relay codification (depth bump OR Arm-Relay clause codified in SUBAGENT_DISPATCH_PROTOCOL) | Architect decides (WAKE_STATE **Q-3**, GAP-11); `node --slot P9-role` executes | SPEC-C (pending); decree Art. IV; T-3/T-8 dissent record | **BLOCKED on Architect Q-3 decision** | **G26** | 2h PROV (post-decision) | ⛔ BLOCKED |

### P2 — Hygiene & Drift (Art. X tier 3)

| ID | Package | Owner slot | Inputs | Depends on | Gates | Effort | Status |
|---|---|---|---|---|---|---|---|
| **WP-D1** | Version-stamp discipline: frontmatter lint script + make target + top-10 doc backfill | `node --slot P5` | SPEC-D sub-spec D1 (drafted, 6h breakdown inside) | WP-A1..A5 merged | **G14** + lint exit-0 | 6h | EXECUTABLE |
| **WP-D2** | Command fossil quarantine (council-local/fast → quarantine dir + README) | `node --slot P3` | SPEC-D sub-spec D2 | WP-D1 (lint pattern family) | **G9** | 1.5h | EXECUTABLE |
| **WP-D3** | Skill stub usage-evidence test + disposition sweep + meditation quartet consolidation | `node --slot P4` | SPEC-D sub-spec D3; T-6 ruling | WP-A1 (test registered via pre-commit) | **G11** | 7h | EXECUTABLE |
| **WP-D4** | Strategy-orphan sweep (~40 docs, batches ≤20/commit) + phantom subsystem resolution | `node --slot P7-role` (docs/indexing role) | SPEC-D sub-spec D4 | WP-D1 (orphan check extends D1 lint script) | **G23, G24** | 8h | EXECUTABLE |
| **WP-D5** | Handoff TTL sweep script + stale-dir sidecars + owner wiring | lilith coordination role (named owner per Q-2 pattern); `node --slot P4` builds script | SPEC-D sub-spec D5 | WP-A1..A5 merged | **G19** | 3h | EXECUTABLE |
| **WP-D6** | WAKE_STATE freshness validator (`validate_wake_state.py`, parse/stage/freshness-in-hours) | `node --slot P4` | SPEC-D sub-spec D6; decree Art. III; Q-2 ownership = MaKaLi at stage boundaries | WP-A2 (ERROR-class taxonomy reuse) | **D6.1, D6.2** (new checks, no inherited G-number) | 4h | EXECUTABLE |

### Cross-tier — AGENTS.md Reconstruction (Art. VI)

| ID | Package | Owner slot | Inputs | Depends on | Gates | Effort | Status |
|---|---|---|---|---|---|---|---|
| **WP-E** | Root AGENTS.md reconstruction from citation-web expectations (S1–S9 sections, incremental one-section-per-commit) | `node --slot P7-role` + `node --slot P5` review | SPEC-E (drafted, full procedure §1–§6); decree Art. VI; **Q-4 default-GO on Architect silence** | WP-D1 (S1 stamp uses D1 frontmatter format); runs PARALLEL to P1/P2 otherwise | **G25, G25a–d, G30** | ≈10h (SPEC-E §5) | EXECUTABLE under Q-4 default-GO (Architect objection flips to BLOCKED) |

---

## §2 DEPENDENCY GRAPH

### ASCII DAG

```
TIER LEGEND: [P0]═══▶ [P1] ───▶ [P2]   (Art. X severity-by-impact order)

[P0]─────────────────────────────────────────────────────────────
  WP-IX (G8, YAML repair)          ◀── Art. IX: precedes ALL distillation
    │
  WP-A1 (G7 pre-commit) ══╦══▶ WP-A4 (G12,G13 stamps)      [P0]
                          ╠══▶ [P1 TIER GATE] ─────────────┐
  WP-A2 (G15,G16 err-class)═╩══▶ WP-B4 (G22 strict)        │
    ╠════════════════════════════▶ WP-D6 (D6.1/D6.2)  [P2] │
  WP-A3 (G6 atomicity)                                     │
  WP-A5 (G29 M8 regex)                                     ▼
                                                        [P1]──────────────────────────
                                                           WP-B1 (G1) ──▶ WP-B2 (G10)
                                                           WP-B3 (G3,G4)
                                                           WP-B5a (G20 discovery)
                                                             │ HARD EDGE (Art. V:
                                                             │ G20 BEFORE G21)
                                                             ▼
                                                           WP-B5b (G21 identities,
                                                                  single-writer)
[⛔ BLOCKED — Architect Q-3]                               WP-C1 (G2), WP-C2 (G26)
                                                             ▲ unblock on decision

[P2]─────────────────────────────────────────────────────────────
  WP-D1 (G14) ══╦══▶ WP-D2 (G9)
                ╠══▶ WP-D4 (G23,G24)
                ╚══▶ (frontmatter template feeds WP-E S1)
  WP-D3 (G11)   WP-D5 (G19)

[CROSS]──────────────────────────────────────────────────────────
  WP-E (G25*, ≈10h) — parallel lane, Q-4 default-GO;
    needs WP-D1 template only for S1 stamp section.
```

### Edge table (every edge carries its authority)

| From | To | Type | Authority |
|---|---|---|---|
| WP-B5a | WP-B5b | **HARD** (no identity writes before discovery fix) | Decree Art. V.1–V.2 ("before any mass identity repair"); gate note "RUN AFTER G20" at SYNTHESIS §6 G21 |
| WP-IX | any distillation act | **HARD** (repair precedes session-end distillation) | Decree Art. IX title + B-2 rationale |
| WP-A1 | WP-A4 | soft (stamps derive from hook inventory) | Decree Art. II.1 ("generated from Makefile+hooks") |
| WP-A1 | all P1/P2 packages | tier gate | Decree Art. X ordering (P0 before P1 before P2) |
| WP-A2 | WP-B4, WP-D6 | soft (shared validator patterns/taxonomy) | Decree Art. III; SPEC-D D6 proposed-change §1 |
| WP-B1 | WP-B2 | soft (same opencode.json surface) | merge-conflict hygiene (ROC guard #5 analog) |
| WP-D1 | WP-D2, WP-D4 | soft (lint script extension family) | SPEC-D D4 validator-first clause ("same file, same commit family") |
| WP-D1 | WP-E (S1 only) | soft (frontmatter format reuse) | SPEC-E §2.2 S1 row |
| Architect Q-3 | WP-C1, WP-C2 | **BLOCKER** (decision queue, not technical) | Decree §5 directive Q-3; Art. VIII.2; GAP-11 |
| Architect silence | WP-E default-GO | default-on-silence | Decree Art. VI + §5 Q-4 |

### Critical path

```
WP-A1 (3h) → WP-B1 (2h) → WP-B2 (6h) → done-of-P1-core     = 11h spine
WP-B5a (3h) → WP-B5b (3h)                                   = 6h identity chain (hard-edged)
WP-D1 (6h) → WP-D4 (8h)                                     = 14h longest P2 chain
```
**Longest serial path ≈ A1→B1→B2 then D1→D4 ≈ 25h of true serialization**; everything else parallelizes within tiers. Total register ≈ **90h** (≈61h executable now, ~3.5h blocked on Q-3, remainder is the P0 provisional block).

---

## §3 BLOCKED vs EXECUTABLE SPLIT

| Class | Packages | Unblock condition |
|---|---|---|
| ✅ Immediately executable (13) | WP-IX, A1–A5, B1–B4, B5a→B5b, D1–D6 | none — start at integration, respect edges above |
| ⛔ BLOCKED on Architect (2) | WP-C1 (G2), WP-C2 (G26) | WAKE_STATE Q-3 decision (wildcard risk-acceptance + subagent_depth). Work may be *spec-readied* but no production edit until decision lands |
| 🔶 Default-GO-on-silence (1) | WP-E (G25*) | Q-4: proceeds unless Architect objects before integration start; flip-to-blocked is a one-line status change here |

**Sequencing mandate for the dev team launch package** (feeds COUNCIL2_PLAN §2 item 5): Sprint 1 = WP-IX + WP-A1 + WP-A5 + WP-A3 (quick P0 wins, ≤9h, each independently committable). Sprint 2 = WP-A2 + WP-A4 + WP-B5a. Sprint 3 = WP-B5b + B-cluster remainder. Sprints 4–5 = D-cluster + WP-E parallel lane. No package exceeds one sprint; every package leaves the tree greener on its own gates (Art. XII anti-big-bang).

---

*⬡ OMEGA ⬡ LILITH/NODE8 ⬡ N8_WORK_PACKAGES ⬡ PREP-ONLY ⬡ NEW-FILE-ONLY ⬡ 2026-08-25*
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:04Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode/x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

