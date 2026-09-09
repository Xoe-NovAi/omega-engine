<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔧 ERRATA & PROPAGATION LEDGER — Council 2 Launch Package
⬡ OMEGA ⬡ MAKALI_FUSION ⬡ trc_first_light_c2_errata ⬡ STAGE-6 ACT (Ruling 2 + Carmack Pass-2 corrections)
**Status**: AUTHORITATIVE — dev team applies these mechanically at hydration minute 0, BEFORE any work package. This ledger is part of the launch package (N10 required-reading, position 0).

## FINDING 1 (CRITICAL — propagation gap, CLOSED BY THIS LEDGER)
Decree C2 rulings were fused AFTER arm snapshots; specs/packages predate them. Corrections below carry decree authority (SOVEREIGN_DECREE_C2.md §1-§2). Where inline application was not verifiable byte-safe, the correction is specified here EXACTLY rather than half-applied — a wrong edit is worse than a documented pending edit.

| # | File | Correction | Decree authority |
|---|------|-----------|------------------|
| E-1 | N9_doc_update_plan.md row 4.1 | Strike relay-codification EXECUTION; mark Q-3-reserved (Architect-owned); link SPEC-C record template | Ruling 1 / SCOPE-1 |
| E-2 | N10_launch_package.md bootstrap prompt | FIRST ACTION = S-2 schema-truth probe VERBATIM (from SYNTHESIS_ARM_REPORT_C2.md §6), NOT bare G8 loop. G8 alone false-closes (BS-1 proven live) | Ruling 3 |
| E-3 | N10_launch_package.md | Replace unnamed "single writer" with "MaKaLi (orchestrator session ses_fc758e6ddffeNEKptpEzboVfYq)" | Ruling 5 |
| E-4 | N8_work_packages.md | Registration-application path = decree Art. V ONLY (discovery fix G20 → single-writer apply G21 → retrieval ≥10). No interim workaround listed as live option | Ruling 5 (Consultant binding) |
| E-5 | SPEC_B_P1_MECHANISM_HONESTY.md WI-1 | Delete "no plugin key" precondition; ADD merge-semantics probe of nested .opencode/opencode.json plugin key (empirically present) to done-definition | Ruling 4 / BS-2 |
| E-6 | SPEC_A: WP-A2 | Shim descope APPLIED (WAKE_STATE validator = D6 standalone; SPEC-A keeps shim only); schema-guard scope = ~30 records (see Finding 2), not 1; effort re-estimated | Pass-2 / ADJ-3+CF-1 |
| E-7 | SPEC_E §1.2 | Fix broken bash (redirect-after-done; ${cluster} out of scope) — rewrite cluster loop before packaging | Pass-2 WP-E |
| E-8 | WP-A4 / G12 ownership | make sovereignty fix = SEPARATE PR (spec wins); remove bundling from N10 sprint list | Pass-2 |
| E-9 | SYNTHESIS_ARM_REPORT_C2.md §6 acceptance block | REMOVE `; true` suffix from G22 line (gate cannot fail as written — Exhibit-D class defect inside our own suite). Acceptance runs use UNNEUTERED gates | Pass-2 Finding 3 |
| E-10 | G15/G16/G3/G4 gate lines | Normalize to `.venv/bin/python` (venv sovereignty M24) | Pass-2 Finding 5 |
| E-11 | G16 | Fix short-circuit polarity (fragile `grep -qv … ||` construct → explicit exit-code check) | Pass-2 Finding 5 |

## FINDING 2 (CRITICAL — corruption blast radius, ARCHITECT-SIZING REQUIRED)
S-2 probe live result: **29 schema-flagged records across data/entities/lilith AND data/entities/maat** (maat L44-52 = newly discovered site). G8 parseability green throughout — BS-1 window fully open. WP-IX original premise (single locus, 0.5h) DEAD.
→ Queued as **WAKE_STATE Q-6**: Architect sizes real repair scope (schema normalization vs per-record triage) BEFORE WP-IX/S-2 enters any bootstrap claim of "clean". Until sized: bootstrap carries probe verbatim (E-2) and reports count, does not assert health.

## VERIFICATION (post-application)
Dev team confirms: `git log --oneline | head -3` shows errata commit · grep E-2 probe present in N10 bootstrap · `rg '; true' data/council/20260825-094633-first-light-c2/phase3_synthesis/` returns empty after E-9 · S-2 probe output count recorded in wake briefing.
<!-- PROVENANCE-CORRECTED 2026-09-09T05:13:35Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_first_light_c2_errata | verdict: AMBIGUOUS | multi-model session; candidates: nemotron-3-ultra-free, big-pickle, gemini-3.8-flash, mimo-v2.5-free
actual_models(Tier0): nemotron-3-ultra-free, big-pickle, gemini-3.8-flash, mimo-v2.5-free, x-preview-f-free, minimax/minimax-m3:free
first_audit: 2026-09-07T03:03:09Z | updated: 2026-09-09T05:13:35Z
-->





