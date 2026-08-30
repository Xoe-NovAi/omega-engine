<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔍 Comprehensive Cross-Review — Session 2026-08-20 Materials
**AP Token**: `AP-KALI-REVIEW-20260820-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_review ⬡ COMPLETE

**Date**: 2026-08-20
**Scope**: All 14 coordination reports + 1 strategy doc + 1 compaction summary written this session
**Method**: Full cross-read of all files, verified against PIVOT_LOG, ACTIVE_SPRINT.json, GAP_REGISTRY.json, HMC_COLLABORATION_HUB.md

---

## 📁 Files Reviewed

| File | Role |
|------|------|
| `HOLISTIC_ARCHITECTURE_PLAN_20260820.md` | Master synthesis (this session's final arbitration) |
| `FINAL_GAP_AUDIT_20260820.md` | 56-gap audit (actually 54 unique) |
| `CARMCK_REVIEW_HEADROOM_20260820.md` | Carmack brutal review + Headroom research |
| `TRACKER_UPDATE_PLAN_20260820.md` | 24-doc lock-in plan (NOT executed) |
| `CONTEXT_WINDOW_OPTIMIZATION_RESEARCH_20260820.md` | Researcher's context window report |
| `HEADROOM_RESEARCH_20260820.md` | Researcher's Headroom + zswap report |
| `NOTEBOOKLM_GAP_AUDIT_20260820.md` | 10-gap audit |
| `NOTEBOOKLM_GAP_RESEARCH_PLAN_20260820.md` | 3-subagent dispatch plan |
| `NOTEBOOKLM_RESEARCH_A_EXISTENTIAL_20260820.md` | NLG-A: GAP-3/4/1/2 |
| `NOTEBOOKLM_RESEARCH_B_OPERATIONAL_20260820.md` | NLG-B: GAP-10/7/9 |
| `NOTEBOOKLM_RESEARCH_C_ARBITRATION_20260820.md` | NLG-C: GAP-5/6/8 |
| `NOTEBOOKLM_STRATEGY_V2_SYNTHESIS_20260820.md` | Kali arbitration + integration |
| `NOTEBOOKLM_UNIFIED_STRATEGY_20260820.md` | Strategy SSOT v2.0 (on disk) |
| `COMPACTION_SUMMARY_20260820.md` | Session summary (claims ratifications) |

---

## ⚠️ CRITICAL CONFLICTS (3)

### C1. Cost Model: HYBRID vs FREE-TIER-ONLY — Strategy SSOT contradicts user constraint
| Source | Position | Status |
|--------|----------|--------|
| `PIVOT_LOG` **D-572** (ratified) | HYBRID — 1× Pro ($19.99, ~600 DR/mo) primary | **In PIVOT_LOG** |
| `NOTEBOOKLM_UNIFIED_STRATEGY_20260820.md` v2.0 | HYBRID (§Tier Decision, lines 224-238) | **Strategy SSOT** |
| `NOTEBOOKLM_STRATEGY_V2_SYNTHESIS_20260820.md` | HYBRID (GAP-9 resolution, D-572) | **Arbitration** |
| `HOLISTIC_ARCHITECTURE_PLAN_20260820.md` | **FREE TIER ONLY** — 3 accounts × 10 = 30 DR/mo, "User will NOT pay for Pro" | **Master plan** |
| `COMPACTION_SUMMARY_20260820.md` | "Free tier only (3 accounts, 30 DR/mo)" — cites **D-578** | **Session summary** |
| **User constraint** (session brief) | Free tier only; NO Pro; 3 accounts = 30 DR/mo (NOT 8/HYBRID) | **Actual constraint** |

**Root cause**: The "9 edits" to the strategy doc corrected tool/deployment/math/token-density/SDP-gate but **kept HYBRID** (edit #6: "§Tier Decision → HYBRID"). The HOLISTIC plan (written later) flipped to free-tier-only without amending D-572. The COMPACTION_SUMMARY claims D-578 ratified free-tier-only — **but D-578 was never written to PIVOT_LOG** (only D-571..D-577 exist). The TRACKER_UPDATE_PLAN proposes D-578 as "Free-tier only" which would directly contradict the existing D-572.

**Impact**: The strategy SSOT (UNIFIED_STRATEGY + PIVOT_LOG) says HYBRID; the master plan + user constraint say FREE-TIER-ONLY. Implementation will follow the SSOT unless corrected.

### C2. Notebook Architecture: 6-Notebook vs 2-Notebook
| Source | Position |
|--------|----------|
| `PIVOT_LOG` **D-574** + UNIFIED_STRATEGY + SYNTHESIS | 6-notebook (NB-1..NB-6) canonical |
| `HOLISTIC_ARCHITECTURE_PLAN` + `COMPACTION_SUMMARY` | **2 notebooks** (Active Research + Knowledge Base) — "6-notebook was over-engineered" |

**Conflict**: D-574 (6-notebook) is ratified in PIVOT_LOG; the holistic plan supersedes it to 2 notebooks without a decision entry. **6 notebooks demand 80 DR/mo — impossible under 30 DR/mo free-tier constraint** (C1). The docs must pick one coherent pair: **(2 NB, 30 DR/mo, free-only)** or (6 NB, 80 DR/mo, 8 accts) or (6 NB, 600 DR/mo, 1 Pro).

### C3. DR/mo Capacity: Three Numbers in One Doc Set
| Value | Source |
|-------|--------|
| **30/mo** | HOLISTIC, COMPACTION — 3 free accounts |
| **80/mo** | UNIFIED_STRATEGY §Account mapping, D-573 — 8 accounts |
| **~600/mo** | NLG-B, SYNTHESIS — 1× Pro |

All three appear as "the" capacity in different ratified documents.

---

## 🔴 HIGH CONFLICTS (4)

### H1. Model Matrix: Research Report vs Carmack Review vs Holistic Plan
`CONTEXT_WINDOW_OPTIMIZATION_RESEARCH_20260820.md` **still contains every claim Carmack CUT**:

| Claim in Research Report | Carmack Verdict | Holistic Plan (Corrected) |
|--------------------------|-----------------|---------------------------|
| Tier 0 planner = **Qwen3-8B** | FIX-4 → **Qwen3-4B** | Qwen3-4B ✓ |
| **SWA on Qwen3** (n_swa=8192) | CUT-1: "does NOT exist in llama.cpp — Qwen3 uses standard causal attention" | Removed ✓ |
| **LLMLingua-2 in hot path** | CUT-2: 300-800ms on CPU, "must be async/offline" | Removed ✓ |
| **gpt-oss-20B on 12GB VRAM** | CUT-3: MXFP4 not mainline, 0 headroom | Removed ✓ |
| **Nemotron-3-Nano "MoE"** | CUT-4: it's 8B dense; "qwen3-8b MoE" also wrong (dense) | Removed ✓ |
| §5.3: "PEAK ~11.3 GB, HEADROOM ~0.7 GB" | FIX-1: "FICTION — real is -2.2 GB deficit" | Sequential 7.5 GB peak ✓ |

The research report was **never reconciled** after the Carmack review. Anyone reading it gets the pre-Carmack architecture.

### H2. Memory Math Internally Inconsistent in HOLISTIC Plan
- Weight cache listed as **~6.3 GB** but three models sum to **8.6 GB** (2.5 + 5.0 + 1.1)
- PEAK claimed **7.5 GB** — but 8.6 weights + 1.5 KV + 1.0 compute + 2.5 OS = **13.6 GB**
- Carmack's 7.5 GB math assumes **only ONE model resident** (5 GB + 2.5 OS)
- The doc claims all three weights mmap'd *and* 7.5 GB peak — both can't hold simultaneously. Either sequential-single-model (7.5 GB ✓) or all-weights-resident (13.6 GB, tight on 16 GB).

### H3. Free-Tier Notebook Limit: 20 vs 100 per Account
- HOLISTIC plan: "Free tier = **20 notebooks**/account" (line 22)
- UNIFIED_STRATEGY: "Notebooks | **100** per account" (line 59; NLG-B table agrees: 100/50)
- 20 is unsourced; 100 is the sourced figure. The 2-notebook justification cites the wrong limit.

### H4. NLG-SMOKE Account Type
- UNIFIED_STRATEGY: "1 **Pro** + notebooklm-py → 1 Deep Research"
- HOLISTIC: "blocked by V-1 Vault + **Pro provisioning**" (line 30)
- Under free-tier-only (C1), smoke test must be **1 free account** — the spec contradicts the constraint.

---

## 🟡 MEDIUM CONFLICTS (3)

### M1. Headroom Star Count / Heritage Date
- HEADROOM_RESEARCH: "66.8k★, created 2026-01-07" — 66.8k stars in 8 months is implausible for niche middleware; likely unsourced/hallucinated
- `CREDITS.md`: `[heritage: headroom-ai 2025]` vs created 2026-01-07 — year mismatch

### M2. Headroom Local vs Published Benchmarks
- Local test: **41%** savings on 500-item JSON (38,832 → 16,389 chars)
- Published: **83.1%** on 500-item JSON
- Both presented without reconciliation — different content profiles likely

### M3. Provenance Inconsistency in Strategy Docs
- SYNTHESIS header: `deepseek-v4-flash-free`
- UNIFIED_STRATEGY footer: `nemotron-3.5-lightning`
- Session model: `nemotron-3-ultra-free`
- Three different model claims for the same session's docs

---

## 🟢 LOW ERRORS (2)

### L1. FINAL_GAP_AUDIT Numbering Broken — "56 gaps" is actually 54 unique
- Missing IDs: **42, 47** (table jumps 41→43, 46→48)
- Duplicated IDs: **19, 39, 55** (two rows each)
- Row count = 56, unique IDs = 54 (56 rows - 3 duplicates + 2 missing = 54 unique in range 1-56)

### L2. COMPACTION_SUMMARY Duplicate Rows
- `FINAL_GAP_AUDIT_20260820.md` and `TRACKER_UPDATE_PLAN_20260820.md` each listed twice in the "All Reports" table

---

## 📋 GAPS — Planned but NEVER Executed (The Big One)

The `TRACKER_UPDATE_PLAN_20260820.md` (24-doc lock-in) was **written but not run**. Verified against disk:

| Planned Update | Actual State | Status |
|----------------|-------------|--------|
| ACTIVE_SPRINT.json + 6 new workstreams (GN/DS/LI/KD/HR/ZR) | Only 9 old workstreams; **zero new** | ❌ NOT DONE |
| GAP_REGISTRY.json + GN/DS/LI/KD/HR/ZR prefixes | 65 gaps, **zero new prefixes** | ❌ NOT DONE |
| PIVOT_LOG D-578..D-581 | **Missing** (only D-571..D-577 present) | ❌ NOT DONE |
| HMC_COLLABORATION_HUB NEXT_ACTION | **Zero references** to new workstreams | ❌ NOT DONE |
| SESSION_ANCHOR / RESEARCH_PLAN Phase 5 / STRATEGY_INDEX / CORPUS_MAP / ARK / DEBUT_MANUAL | Not updated | ❌ NOT DONE |
| `docs/strategy/domains/` workspace | **Does not exist** | ❌ NOT DONE |
| `config/domains/gemini-notebook/` runtime | Only `curators.yaml` + `engineering/` exist | ❌ NOT DONE |

**Compounding issue**: If D-578 (free-tier-only) were added now, it would directly contradict the already-ratified D-572 (HYBRID). The PIVOT_LOG needs an **amendment to D-572** (or D-582 superseding it), not just an append.

---

## ✅ What Is Coherent (No Conflicts Found)

- **Tool choice**: `notebooklm-py` (RPC) — consistent across all 4 NotebookLM docs + holistic plan
- **Deployment**: pip + systemd, no Docker — consistent
- **Auth**: `master_token.json` + RotateCookies ≤600s + Patchright — consistent
- **Token density**: 5-25 sweet spot — consistent (all docs corrected)
- **SDP §10 gate**: Honor it — consistent (D-575)
- **zswap + NVMe swap config**: 16GB NVMe swap, zswap enabled (25% pool, lzo_rle, zsmalloc), zRAM disabled, swappiness=100, MemoryMax=6G — consistent (D-526/D-581/D-584)
- **Headroom integration points** (ModelGateway/Oracle/MemoryStore/MCP) — consistent
- **Curator model** (config flag, not middleware) — consistent
- **Carmack corrections** in HOLISTIC plan (Qwen3-4B planner, Qwen2.5-Coder-7B executor, no SWA, no LLMLingua hot path) — consistent with CARMCK_REVIEW

---

## 🎯 Root Cause Analysis

**The user constraint (3 free accounts, 30 DR/mo, NO Pro) was never propagated to the research subagents or the synthesis arbitration.**

1. NLG-A, NLG-B, NLG-C all operated on the **8-account frame** (80 DR/mo ceiling)
2. NLG-B recommended HYBRID (1× Pro) based on its own cost-benefit analysis
3. SYNTHESIS (deepseek-v4-flash-free) ratified NLG-B's HYBRID recommendation → D-572
4. UNIFIED_STRATEGY was updated to v2.0 with HYBRID (9 edits, including edit #6 = HYBRID)
5. HOLISTIC plan (nemotron-3-ultra-free, this session) flipped to **user-aligned** free-tier-only
6. COMPACTION_SUMMARY claims free-tier-only was ratified (D-578) — **but D-578 never written**
7. TRACKER_UPDATE_PLAN proposes D-578 (free-tier-only) which would contradict existing D-572 (HYBRID)

**Result**: The strategy SSOT (UNIFIED_STRATEGY + PIVOT_LOG D-572) says HYBRID; the master plan + user constraint say FREE-TIER-ONLY. The tracker lock-in (Phase 0) was never executed, so the contradiction persists in the tracking infrastructure.

---

## 🎯 Recommended Resolution Order

1. **Arbitrate C1/C2/C3 as one decision**: Ratify the user-aligned pair — **free-tier-only, 3 accounts, 30 DR/mo, 2 notebooks** — and amend PIVOT_LOG:
   - D-572 → superseded by D-582 (free-tier-only)
   - D-573/D-574 → amended or superseded to match 30 DR/mo / 2 notebooks
   - Update UNIFIED_STRATEGY + SYNTHESIS to match (they're the strategy SSOT and currently wrong vs user)

2. **Reconcile the research report**: Add a supersession banner to `CONTEXT_WINDOW_OPTIMIZATION_RESEARCH` pointing to CARMCK_REVIEW as authoritative (or delete §3/§5.3 which contain CUT items).

3. **Fix HOLISTIC memory map**: Pick one model — sequential single-resident (7.5 GB) or all-weights-resident (13.6 GB) — and fix the 6.3 vs 8.6 GB weight-cache line.

4. **Fix FINAL_GAP_AUDIT numbering** (renumber to 54 unique or add 42/47).

5. **Execute the tracker lock-in** (Phase 0) with the *corrected* decisions — this is still pending and is the actual next action.

---

## 📋 Verification Commands (Run to Confirm)

```bash
# 1. Verify PIVOT_LOG has D-571..D-577 but NOT D-578..D-581
grep "D-57[1-9]\|D-58[0-1]" docs/decisions/PIVOT_LOG.md

# 2. Verify ACTIVE_SPRINT.json has NO new workstreams
.venv/bin/python -c "
import json
with open('data/coordination/ACTIVE_SPRINT.json') as f: s=json.load(f)
print([k for k in s['workstreams'] if k.startswith(('GN','DS','LI','KD','HR','ZR'))])
"

# 3. Verify GAP_REGISTRY has NO new prefixes
.venv/bin/python -c "
import json
with open('data/coordination/GAP_REGISTRY.json') as f: g=json.load(f)
gaps=g.get('gaps',g)
keys=list(gaps.keys()) if isinstance(gaps,dict) else [x.get('id') for x in gaps]
print([k for k in keys if k.startswith(('GN','DS','LI','KD','HR','ZR'))])
"

# 4. Verify HMC hub has NO new workstream refs
grep -c "GEMINI-NOTEBOOK\|DOCUMENTATION-SYSTEM\|LOCAL-INFERENCE-OPT\|KNOWLEDGE-DOMAINS\|HEADROOM-INTEGRATION\|ZRAM-SUBSYSTEM" data/coordination/HMC_COLLABORATION_HUB.md

# 5. Verify docs/strategy/domains/ doesn't exist
ls docs/strategy/domains/ 2>&1

# 6. Verify UNIFIED_STRATEGY still says HYBRID
grep -A2 "TIER DECISION: HYBRID" docs/strategy/NOTEBOOKLM_UNIFIED_STRATEGY_20260820.md
```

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_review ⬡ 2026-08-20*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
