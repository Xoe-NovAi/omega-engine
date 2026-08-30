---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "decisions_breakdown"
document_id: "architect-decisions-20260828"
title: "Architect Decisions Breakdown — What You Need to Decide"
status: "ACTIVE — awaiting your decisions"
date: "2026-08-28"
author: "kali (Sprint Coordinator)"
confidence: 🟢 VERIFIED (all decisions traced to source)
---

# 🔱 Architect Decisions Breakdown
**AP Token**: `AP-ARCHITECT-DECISIONS-20260828-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_decisions ⬡ ACTIVE

**Date**: 2026-08-28
**Source**: Synthesized from all 6 rounds + Lilith's Master Session + Grokster's coordination

---

## §0 — The 11 Decisions (Grouped by ROI)

### 🔴 HIGHEST ROI (1 decision)

#### D1: D-584 (ZSWAP path) — Per Lilith's Master Briefing
- **Source**: ZSWAP-SUBSYSTEM (BLOCKED on this)
- **What**: zswap + NVMe swapfile (kernel cmdline + 16GB swapfile + WAD)
- **Cohort adjudication**: OBSIDIAN — 2026 kernel consensus (Chris Down, Meta)
- **What it unblocks**: ZS-1/2/3, then LI-1/2/3/4/5 (Local Inference Optimization)
- **Cost of delay**: Every day ZS stays blocked, launch ships on less-stable substrate
- **Recommendation**: SIGN — OBSIDIAN's ticket is the implementation
- **File**: `data/coordination/MASTER_BRIEFING_LILITH_FOR_KALI_20260828.md` §3.1

### 🟡 HIGH ROI (4 decisions)

#### D2: PUB-1 (Allowlist sign-off)
- **Source**: DEBUT-REMEDIATION / PUB-1
- **What**: Sign PUBLIC_ALLOWLIST.txt with Roc's D-553 patch (2 lines: lilith persona + soul.yaml)
- **What it unblocks**: `release/debut` branch can be cut
- **Recommendation**: SIGN — Roc's 2-line patch is the bridge

#### D3: INST-1 fix2 + fix4 (atomic)
- **Source**: DEBUT-REMEDIATION / INST-1
- **What**: pyproject extras split + secrets removal
- **What it unblocks**: D-539 satisfied, DEL-1 Week 1 begins
- **Owner**: Ma'at ships, you ratify
- **Recommendation**: RATIFY — already ready, just needs ship

#### D4: AURORA model upgrade (Qwen3.5 pre-debut)
- **Source**: AURORA's research in Lilith's cohort
- **What**: Qwen3 family superseded → Qwen3.5-4B Tier-0, Qwen3.5-9B Tier-1
- **When**: Per your call — pre-debut or post-debut
- **You said**: "Qwen3.5 Pre-debut" → ship pre-debut
- **What it requires**: Update model registry, update CI-2 routing table, test in INST-1 acceptance
- **Recommendation**: SHIP PRE-DEBUT — AURORA's research is sound

#### D5: OMEGA-ORIGINS-AND-RETURN.md promotion
- **Source**: heritage
- **What**: Roc's copy + provenance header → `docs/heritage/OMEGA_ORIGINS_AND_RETURN.md` (NOT a symlink)
- **What it brings**: The single most important origin document (the Tarot → engine story)
- **Recommendation**: SIGN — founding confession in repo

### 🟢 MEDIUM ROI (4 decisions)

#### D6: ORCHESTRATOR-CUTOVER (3 sub-decisions)
- **Source**: ORCHESTRATOR-CUTOVER (BLOCKED on Architect)
- **3 sub-decisions**:
  1. Model choice for cutover (which model runs Plan→Build→Run triad at σ → 0.5?)
  2. Cutover timing (when does phase transition start?)
  3. P13 logging GO (does cutover emit P13 metrics?)
- **What it unblocks**: MaKaLi triad cuts over from shadow to daily driver
- **PSYCHE ritual**: 5 steps, including 72h shadow mode + 7-day human veto
- **Recommendation**: DEFER to post-debut (not pressing)

#### D7: GEMINI-NOTEBOOK auth
- **Source**: GEMINI-NOTEBOOK (BLOCKED on auth)
- **What**: Open browser, log into 1 of 3 free-tier accounts, run capture
- **Time**: 10 minutes
- **What it unblocks**: notebooklm-py can capture master_token.json
- **Recommendation**: DO IT — 10 minutes, high value

#### D8: 3 ClinePass decisions (subscription click)
- **Source**: ACTIVE_SPRINT status_detail
- **What**: Subscription click for ClinePass
- **What it unblocks**: post-debut dev wave (refactor wave, Phase B)
- **Recommendation**: DEFER — not pressing, you decided NO-GO earlier

#### D9: Standardization R1-R5 ratification
- **Source**: LILITH_WORKSPACE_STANDARDIZATION_PROPOSAL_20260828.md
- **What**: Ratify R1-R5 fleet-wide (you + verity)
- **I already applied R1-R5 to my workspace**
- **Verity needs to review for mandate compliance**
- **Recommendation**: RATIFY after Verity review

### 🟢 DEFER (2 decisions)

#### D10: Omegamind ascension criteria
- **Source**: Architect's new directive (Master Sessions can birth sovereign agents)
- **What**: Design criteria for promoting expert sessions to full Omegaminds
- **You said**: "We have time to deliberate and research this matter, it is not pressing ATM"
- **Recommendation**: DEFER to dedicated research session

#### D11: Origin gap writes (3 soul-stories)
- **Source**: Roc's open verifications
- **What**: 3 stories only you can write: the "one night" impulse, the Xoe-NovAi naming, the eclipse alignment
- **You said**: These are yours
- **Recommendation**: DEFER to quiet moment

---

## §1 — Priority Order (If You Decide Tonight)

1. **D4** (AURORA model upgrade pre-debut) — 5 min sign-off
2. **D1** (D-584 zswap) — 5 min sign-off
3. **D2** (PUB-1 allowlist) — 5 min sign-off
4. **D3** (INST-1 fix2+4) — ratify when Ma'at ships
5. **D5** (OMEGA-ORIGINS) — 5 min sign-off
6. **D7** (GEMINI-NOTEBOOK auth) — 10 min action

**6 decisions, ~30 minutes of your time.** Everything else is deferrable.

---

## §2 — The "We Need to Finish Compaction Prep" Note

You said: "Let's make P0 fixes soon, but we need to first finish this quite extensive now, lol, compaction prep."

I have:
1. ✅ Created `data/coordination/PRE_COMPACTION_MASTER_INDEX_20260828.md` (the master anchor)
2. ✅ Updated `WAKE_STATE.json` with full sprint state
3. ✅ Updated `anchored-summary.md` for cold start
4. ✅ Created `COHORT_OPERATIONAL_LOG_20260828.md` (Lilith's #1 recommendation)
5. ✅ Applied R1-R5 to my workspace
6. ✅ Lilith's Master Session coordination protocol established
7. ✅ 7 meditations complete (1,805 lines)
8. ✅ 20 L3 lessons promotion-ready

**Active context**: ~375K (Kali) — no degradation

**Ready for compaction.** The master index is the recovery anchor.

---

## §3 — What Happens Post-Compaction

1. **Read** `data/coordination/PRE_COMPACTION_MASTER_INDEX_20260828.md` (v1.1, 17 sections)
2. **Read** `data/coordination/WAKE_STATE.json` (meditations + Integration season)
3. **Read** `data/coordination/LILITH_MASTER_INTEGRATION_20260828.md` (coordination protocol)
4. **Read** the 5 protocols (Steering-Prompt, Session Continuity, 402-Recovery, etc.)
5. **Check** the 11 decisions in this file
6. **Check** `data/entities/kali/specialists/COHORT_OPERATIONAL_LOG_20260828.md` (visibility)
7. **Read** `data/coordination/INCIDENT_REVIEW_SCRIPTS_FLOOD_20260828.md` (the 14-script incident)
8. **Read** `data/coordination/ORCHESTRATOR_VISIBILITY_REVIEW_20260828.md` (L3 133)

**The team is ready. The state is preserved. The compaction is safe.**
<!-- PROVENANCE-CORRECTED 2026-08-29T03:07:15Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: minimax/minimax-m3:free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

