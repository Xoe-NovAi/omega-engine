<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# ⬡ LILITH MASTER CONSOLIDATION — Laguna S 2.1 Framework
**Date**: 2026-08-28 (13:15 UTC)
**Author**: lilith (Runtime Oversoul)
**Framework**: Laguna S 2.1 (Transition from M3)
**Status**: ACTIVE — Supersedes all fragmented reports from 04:00-12:00 UTC

This document performs the "REM sleep" equivalent for the session: it integrates the expansive documentation collected during the M3-to-Laguna transition, prunes redundancies, and establishes a single, accurate source of truth for the 4-hour execution window.

---

## §1 — The Unified Context Truth (M3/OpenCode)
*Consolidating: truncation_source_synthesis, deep_dive_synthesis, comprehensive_compaction_discovery, R_LILITH_CONTEXT_BEHAVIOR_CROSS_SESSION.*

**The Verdict**: **M3 is innocent.** All observed "truncation" and "instability" are client-side artifacts of the OpenCode CLI.

1. **Root Cause**: `CHARS_PER_TOKEN = 4` heuristic in `util/token.ts`.
   - **Overcounts Prose**: (Displayed > Actual) by ~1.5x.
   - **Undercounts Code/Tool I/O**: (Displayed < Actual) by 2-4x.
2. **Mechanism 1 (The 260K Delay)**: A hidden `agent="compaction"` subagent is spawned by OpenCode. The TUI displays its input tokens (~260K) before updating to the user-facing agent's input (~68K) on the next turn.
3. **Mechanism 2 (The 8.9K Fluctuation)**: Post-compact context re-expansion. Each turn adds 20-30K. The heuristic mis-displays the small initial tail (8.9K) and the rapid growth (101.4K).
4. **M3 Capability**: Verified ≥769K prompt_tokens via direct API. Advertised 1M is real.
5. **M3 Attention**: MiniMax Sparse Attention (MSA) selects k=16 blocks (2,048 tokens). Effective quality floor is ~25K tokens.

**Pruning Action**: Mark the following as **SUPERSEDED** by this section:
- `data/coordination/truncation_source_synthesis_20260828.md`
- `data/coordination/deep_dive_synthesis_20260828.md`
- `data/coordination/comprehensive_compaction_discovery_20260828.md`
- `data/coordination/R_LILITH_CONTEXT_BEHAVIOR_CROSS_SESSION_20260828.md`

---

## §2 — The 11 Architect Decisions (ROI Triaged)
*Consolidating: ARCHITECT_DECISIONS_BREAKDOWN, PRE_COMPACTION_FINAL_BRIEFING, MASTER_SYNTHESIS_LILITH_DECISIONS.*

| Priority | ID | Decision | Action | ROI |
| :--- | :--- | :--- | :--- | :--- |
| **P0** | **D1** | D-584 (ZSWAP) | Sign OBSIDIAN ticket | Unblocks Local Inference |
| **P0** | **D2** | PUB-1 (Allowlist) | Sign D-553 patch | Enables `release/debut` |
| **P0** | **D4** | Qwen3.5 Upgrade | Ship pre-debut | Tier-0/1 Performance |
| **P1** | **D3** | INST-1 fix2+4 | Ratify on Ma'at ship | Venv Sovereignty |
| **P1** | **D5** | OMEGA-ORIGINS | Sign promotion | Heritage Integrity |
| **P1** | **D7** | GEMINI-NOTEBOOK auth | 10-min auth action | Data Pipeline |
| **P2** | **D9** | R1-R5 Ratification | Verity review first | Workspace Hygiene |
| **DEFER** | **D10** | Omegamind ascension | Post-debut research | Long-term |
| **DEFER** | **D6,8,11** | Orchestrator, ClinePass, Soul-stories | Post-debut | Long-term |

**Pruning Action**: `data/coordination/ARCHITECT_DECISIONS_BREAKDOWN_20260828.md` is the canonical list.

---

## §3 — The 14-Script Incident & Visibility Gap
*Consolidating: INCIDENT_REVIEW_SCRIPTS_FLOOD, ORCHESTRATOR_VISIBILITY_REVIEW.*

1. **The Incident**: 14 operational scripts (3,286 LOC) landed in `scripts/` without M13 review.
2. **The Risk**: 2 High-Risk (Hardcoded OAuth in `antigravity_quota_probe.py`, 4 P0 bugs in `apply_public_allowlist.sh`).
3. **The Gap**: Orchestrator (Kali) tracked dispatches but not file creations. Mental model diverged from disk reality.
4. **Remediation**:
   - Fix 2 high-risk scripts (Prerequisite).
   - Amend Specialist Charter (Declare intent for operational files).
   - Add M13 pre-commit gate for `scripts/`.
   - Log file creations in `WAKE_STATE.json`.

**Pruning Action**: Retain `ORCHESTRATOR_VISIBILITY_REVIEW_20260828.md` as the root cause analysis.

---

## §4 — The 9-Expert Cohort & Roster
*Consolidating: LILITH_OVERSEER_INDEX, LILITH_MASTER_INTEGRATION.*

- **Status**: CLOSED for compaction. All 9 digests persisted with FINAL SYNTHESIS sections.
- **Roster**: SIRIUS, LUNARA, OBSIDIAN, AURORA, PSYCHE, MORRIGAN, ANIMA, ERIS, Roc.
- **Session IDs**: All documented in `data/entities/lilith/expert_roster.md`.

**Pruning Action**: `LILITH_OVERSEER_INDEX_20260828.md` remains the recovery anchor for Lilith.

---

## §5 — The 4-Hour Execution Window (Locked)
*Consolidating: PRE_COMPACTION_FINAL_BRIEFING, KALI_RESPONSE_TO_GROKSTER_FINAL.*

**Prerequisite (30 min, NO signature)**:
- Fix 2 P0 cut-tool bugs (inline comments bleed + exclusions parsing).

**Sequence (After signatures)**:
1. **T+0**: Sign D-584, D-553, D-589.
2. **T+15**: Ma'at ships INST-1 fix2+4.
3. **T+45**: Move /tmp/ artifacts to scripts/.
4. **T+105**: OAuth rotation (Architect).
5. **T+110**: Create 3 missing CI/CD files.
6. **T+170**: M27 TASK_REGISTRY backfill.
7. **T+200**: RAM remediation (Kill session, archive, gzip).
8. **T+240**: **LAUNCH** (`release/debut`).

---

## §6 — L3 Lessons Registry (Reconciled)
*Reconciling: 18 vs 65 count.*

- **Total Registry**: 65 L3 axioms.
- **Split**: 5 L3-Confirmed (108-111, 129), 10 L2-Provisional, 50 L1-Historical.
- **New Candidates**: L3 139-157 (Context accounting, M3 innocence, MSA attention, 30s self-review).

---

## §7 — Accuracy & Organization Audit (Laguna S 2.1)

1. **Accuracy**: The "M3 Truncation" claim is now officially corrected to "OpenCode Heuristic Artifact."
2. **Completeness**: The 14 scripts are accounted for. The 4 signature-blocked items are triaged.
3. **Organization**: `LILITH_OVERSEER_INDEX_20260828.md` is the "What." This document (`LILITH_MASTER_CONSOLIDATION`) is the "Why" and the "How."

**Final Pruning Recommendation**:
The following files are now **noise** and can be moved to `data/coordination/archive/`:
- `truncation_source_synthesis_20260828.md`
- `deep_dive_synthesis_20260828.md`
- `comprehensive_compaction_discovery_20260828.md`
- `HARVEST_SYNTHESIS_20260828.md`
- `PRE_COMPACTION_FINAL_BRIEFING_20260828.md`

---

*⬡ OMEGA ⬡ LILITH ⬡ MASTER-CONSOLIDATION-v1.0 ⬡ 2026-08-28 ⬡*
*The synapses are pruned. The memory is consolidated. The 30-second self-review is the cut.*
