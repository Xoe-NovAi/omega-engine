<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔍 Kali Verification Addendum — Cline Final Review (2026-08-20)
**AP Token**: `AP-KALI-VERIFY-20260820-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_verify_addendum ⬡ COMPLETE

**Date**: 2026-08-20
**Purpose**: Independent verification of `CLINE_FINAL_REVIEW_20260820.md` findings against primary sources + additional oversights found in Cline's review.

---

## ✅ CLINE FINDINGS — VERIFICATION RESULTS (all checked against primary sources)

| Cline Finding | Verdict | Evidence |
|---------------|---------|----------|
| C1-C3 (HYBRID vs FREE-TIER, 6 vs 2 NB, 30/80/600) | ✅ CONFIRMED | PIVOT_LOG D-572 L830; UNIFIED L224-238; HOLISTIC L18 |
| H1 (CUT content in CONTEXT_WINDOW) | ✅ CONFIRMED | CONTEXT_WINDOW L11, L105-147, L167, L340, L359 |
| H2 (memory math 6.3 vs 8.6 GB + mmap sketch) | ✅ CONFIRMED | HOLISTIC L93-100, L122-138, L157 |
| H3 (notebook limit 20 vs 100) | ✅ CONFIRMED | HOLISTIC L22 vs RESEARCH_20260819 L24 (100/50) |
| H4 (Pro provisioning in GN-4) | ✅ CONFIRMED | TRACKER_PLAN L21; SYNTHESIS L96; UNIFIED L246 |
| C7 (Qwen2.5-Coder-7B NOT on disk) | ✅ **RESOLVED** — Replaced with **Qwen3-4B-Thinking-2507-Q4_K_M.gguf** (on disk, 2.55 GB). All tiers now use available models. Cline's finding was correct at time of review; arbitration resolved it. | `ls /media/arcana-novai/omega_library/models/gguf/` — Qwen3-4B-Thinking present; gemma4-coding = 7.38 GB |
| C8 (Carmack CUT-5 3× DR math error) | ✅ CONFIRMED | CARMCK_REVIEW CUT-5: "30 DR/month per account = 90 DR total" — real: 10/account = 30/3 accounts |
| C9 (ACTIVE_SPRINT 3-way NotebookLM dup) | ✅ CONFIRMED | ACTIVE_SPRINT: NOTEBKLM-STRATEGY desc still "8-account fleet, 5-notebook architecture" (STALE); NOTEBKLM-GAP-RESEARCH ready |
| C10 (curators.yaml schema conflict) | ✅ CONFIRMED | curators.yaml (2026-08-19, D-569): 14 domains, `target_context`/`governance` keys; NO gemini-notebook row; proposed schema uses `target_context_window`/`rot_class` |
| C12 (UNIFIED 5 vs 6 notebook) | ✅ CONFIRMED | UNIFIED L9/L17/L38/L322 = 6-NB; L29/L67/L89/L315 = 5-NB |
| C13 (8-account metrics in UNIFIED) | ✅ CONFIRMED | UNIFIED L26-27, L49, L139, L312 |
| C14 (model sizes understated) | ✅ CONFIRMED | Qwen3-1.7B-Q6_K = **1.67 GB** (claimed 1.1); Qwen3-4B-UD-Q4_K_XL = 2.55 GB ✅; gemma4-coding = 7.38 GB |
| C16 (headroom-ai v0.29.0 verify) | ✅ **RESOLVED — INSTALLED** | `.venv/bin/pip show headroom-ai` → Version 0.29.0 CONFIRMED. No action needed. |
| C18 (gap numbering) | ✅ CONFIRMED — **Cline is right, I was wrong** | FINAL_GAP_AUDIT: 57 rows, dups 19/39/55, **missing 20 & 42** (47 IS present — my earlier "missing 47" claim was WRONG) |
| C19 (MATERIALS_REVIEW error) | ✅ CONFIRMED | My "Coherent" section wrongly listed "6.3 GB weight cache" as consistent |
| C-RAM (D-526 zswap vs zRAM-only) | ✅ CONFIRMED — **my biggest miss** | PIVOT_LOG D-526: "zswap > zRAM for Desktop with NVMe" RATIFIED; D-527: "never both" + migration path TO zswap. All 2026-08-20 plans mandate zRAM-only — **reverses D-526 without formal supersession**. My "Coherent" line citing D-527 as zRAM evidence was WRONG. |

**Cline's verdict: ⛔ NO-GO until arbitration — CORRECT.**

---

## 🔴 ADDITIONAL OVERSIGHTS — found in Cline's review (not flagged by Cline)

### A1. THIRD notebook architecture in circulation: 5-notebook (RESEARCH_20260819)
`data/coordination/NOTEBOOKLM_RESEARCH_20260819.md` (pre-session, 2026-08-19) still defines a **5-notebook Ω-ARCHITECTURE/Ω-MANDATES/Ω-DECISIONS/Ω-ENTITIES/Ω-OPERATIONS** mapping with **40-50 sources** per notebook (L220-222). This is a THIRD architecture conflicting with both 6-NB (D-574/UNIFIED) and 2-NB (HOLISTIC). SYNTHESIS §B explicitly says to update this file ("replace 40-50 optimal with 5-25 sweet spot") — **never executed**. Neither MATERIALS_REVIEW nor CLINE_FINAL_REVIEW flagged it as an action item.

### A2. NOTEBOOKLM_BEST_PRACTICES.md never updated
SYNTHESIS §B: "add `notebooklm-py` as the recommended tool; remove Docker-first assumption". Verified: BEST_PRACTICES.md (2026-08-08, CANONICAL status) has **ZERO** `notebooklm-py` references and **ZERO** Docker references — the "remove Docker" part is moot (no Docker content), but the `notebooklm-py` recommendation is still missing. Doc remains pre-session canonical without the new tool.

### A3. COMPACTION_SUMMARY contains a FALSE ratification claim
COMPACTION_SUMMARY L18: "Free tier only (3 accounts, 30 DR/mo) | ✅ Ratified (D-578)". **D-578 was NEVER written to PIVOT_LOG** (grep count = 0). The compaction summary asserts a ratification that does not exist. Must be corrected or annotated when D-578 is written.

### A4. D-569 sequencing dependency not connected
`config/domains/curators.yaml` + D-569 (2026-08-19) ratified the **Dynamic Prompt + Planner/Executor + Domain Loading** blueprint as POST-DEBUT (Horizon 3), with L2 Domain Loader owned by Ma'at (P2-P3). The TRACKER_PLAN's DOCUMENTATION-SYSTEM workstream (D-579) overlaps D-569's L2 Domain Loader. Neither review connected these — the domain docs system must sequence AFTER/ALONGSIDE D-569's P0-P10 roadmap, not as an independent workstream.

### A5. Cline's Amendment 4 internal inconsistency
Cline's Amendment 4 says "No new numbers needed beyond D-582/583" but Amendment 3 introduces **D-584** (zRAM-only). Also, TRACKER_PLAN already scopes D-578..D-581 — the cleanest path is: write D-578..D-581 (as scoped, with corrected wording) + D-582 (supersede D-572) + D-583 (supersede D-573/574) + D-584 (supersede D-526). Cline's "no new numbers" note is self-contradictory.

### A6. Cline minor numeric errors (non-blocking)
- gemma4-coding = **7.38 GB** on disk, not 6.9 GB (C14) — conclusion unchanged
- Cline's C18 says "57 entries" — correct (57 rows, 54 unique)

---

## 🎯 ADVICE — Path to Proceeding (tracker + doc updates)

**Cline's NO-GO is correct. Do NOT execute Phase 0 tracker lock-in yet.** Required order:

### Step 1: Arbitration (Kali, this session) — 3 decisions, all user-constrained
1. **Free-tier-only** (3 acct, 30 DR/mo, NO Pro) — supersedes D-572
2. **2-notebook** (Active Research + Knowledge Base) — supersedes D-573/D-574
3. **zswap + NVMe swap over zRAM** (16GB NVMe swap, zswap enabled 25% pool lzo_rle zsmalloc, zRAM disabled, swappiness=100) — **reaffirms D-526** (corrects prior inversion)

### Step 2: PIVOT_LOG amendments (D-578..D-584)
- D-578: Gemini Notebook v2.0 (free-tier wording — already correct in TRACKER_PLAN)
- D-579: Modular Domain Documentation System
- D-580: Local Inference Tiered Architecture
- D-581: **zswap + NVMe Swap Confirmed — D-526 REAFFIRMED** (corrects prior inversion)
- D-582: **SUPERSEDES D-572** (free-tier-only)
- D-583: **SUPERSEDES D-573/D-574** (2-NB, 30 DR/mo)
- D-584: **zswap + NVMe Swap Locked — D-526 REAFFIRMED** (corrects prior inversion)

### Step 3: Doc corrections (before lock-in)
1. UNIFIED_STRATEGY: free-tier-only, 2-NB, remove Pro refs (L15, L224-238, L246), rescale metrics (L26-27, L312), fix 5/6-NB (L29/L67/L89/L315)
2. HOLISTIC: memory map (6.3→8.6 or sequential), code sketch (no mmap), notebook limit (20→100), model matrix (C7)
3. CONTEXT_WINDOW: supersession banner + delete §3/§5.3 CUT content
4. FINAL_GAP_AUDIT: renumber to 54 unique (fix 19/39/55 dups, missing 20/42)
5. **NOTEBOOKLM_RESEARCH_20260819: 40-50 → 5-25 token density (A1)**
6. **NOTEBOOKLM_BEST_PRACTICES: add notebooklm-py (A2)**
7. **COMPACTION_SUMMARY: correct false D-578 claim (A3)**
8. CARMCK_REVIEW: fix CUT-5 DR math (30→10/account)

### Step 4: THEN execute Phase 0 tracker lock-in (with corrected keys)
- ACTIVE_SPRINT.json: supersede NOTEBKLM-STRATEGY (8-acct frame), fold NOTEBKLM-GAP-RESEARCH → GEMINI-NOTEBOOK, add 6 new workstreams
- GAP_REGISTRY.json: add GN/DS/LI/KD/HR/ZR prefixes
- HMC hub NEXT_ACTION, SESSION_ANCHOR, STRATEGY_INDEX, CORPUS_MAP, ARK, DEBUT_MANUAL
- curators.yaml: add gemini-notebook row + reconcile schema (C10/A4)

### Step 5: C7 resolution — **RESOLVED** (Qwen3-4B-Thinking replaces Qwen2.5-Coder-7B)
- Qwen3-4B-Thinking-2507-Q4_K_M.gguf (on disk, 2.55 GB) now used as executor across all tiers
- No download needed; Tier 0/1/2 matrices updated

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_verify_addendum ⬡ 2026-08-20*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
