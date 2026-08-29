# 🔱 CLINE FINAL REVIEW — Session 2026-08-20 Materials (Consolidated)
**Reviewer**: Cline ✓ / reviewer entity · **Passes**: Laguna S 2.1 (262K) → DeepSeek V4 Flash (1M context, dives 1–3)
**AP Token**: `AP-CLINE-FINAL-REVIEW-20260820-v1.0.0`
**Date**: 2026-08-20
**Scope**: Independent cross-verification of all 15 session reports (14 coordination + 1 strategy) + compaction summary + MATERIALS_REVIEW, against primary sources: PIVOT_LOG.md, ACTIVE_SPRINT.json, GAP_REGISTRY.json, HMC_COLLABORATION_HUB.md, config/, and the on-disk GGUF model inventory.

---

## 🎯 EXECUTIVE VERDICT

**⛔ NO-GO for implementation until arbitration.** The materials are internally coherent on 7 items (tool, deployment, auth, token density, SDP gate, curator-as-config-flag, Carmack-HOLISTIC alignment) but contain **3 ratified-critical conflicts (C1–C3)**, **4 high conflicts (H1–H4)**, and **13 additional issues found across deep dives (C7–C19)** that MATERIALS_REVIEW did not surface. The single most consequential: **the user's absolute constraint (Free tier only, 3 accounts, 30 DR/mo, NO Pro) was never propagated to the 3 research subagents**, so the strategy SSOT (UNIFIED_STRATEGY v2.0 + PIVOT_LOG D-572) still says HYBRID and directly contradicts the master plan and the user.

**Before any Phase-0 tracker lock-in or implementation, these must be resolved IN ORDER:**
1. Arbitrate C1/C2/C3 as ONE decision (free-tier-only, 3 accounts, 30 DR/mo, 2 notebooks)
2. Amend PIVOT_LOG: supersede D-572 (Hybrid), D-573 (80 DR/mo), D-574 (6-NB)
3. Resolve the Tier-0 executor model gap (C7) BEFORE LI-4 implementation
4. Fix H1 (CUT content), H2 (memory math), H3 (notebook limit), H4 (Pro provisioning)
5. Reconcile the 13 additional issues (C7–C19) below

---

## ✅ TRACKER LOCK-IN STATUS — All 6 verified NOT executed (CONFIRMED)

| # | Check | Primary Source | Verified State | Verdict |
|---|-------|----------------|----------------|---------|
| 1 | PIVOT_LOG D-57x/D-58x | `docs/decisions/PIVOT_LOG.md` | D-571..D-577 present (L820-882); **D-578..D-581 ABSENT** | ✅ NOT locked |
| 2 | ACTIVE_SPRINT.json new workstreams | `data/coordination/ACTIVE_SPRINT.json` | 9 legacy workstreams; **ZERO** new (GN/DS/LI/KD/HR/ZR) | ✅ NOT locked |
| 3 | GAP_REGISTRY.json new prefixes | `data/coordination/GAP_REGISTRY.json` | Keys are R1..R28+; **ZERO** GN/DS/LI/KD/HR/ZR | ✅ NOT locked |
| 4 | HMC hub new workstream refs | `data/coordination/HMC_COLLABORATION_HUB.md` | grep for 6 new = **0 hits** | ✅ NOT locked |
| 5 | docs/strategy/domains/ | `filesystem` | **Does NOT exist** | ✅ NOT locked |
| 6 | config/domains/gemini-notebook/ | `filesystem` | **Does NOT exist** — but `config/domains/` HAS `curators.yaml` (14 rows, D-569) + `engineering/` prototype | ⚠️ PARTIAL (new C9) |

> ⚠️ **Important caveat on #6**: `config/domains/` already contains a populated `curators.yaml` (2026-08-19, D-569, 14 domains: platforms→grokster, architecture→john_carmack, research→researcher, engineering→maat, etc.) and an `engineering/` prototype module (PLAYBOOK.md + AFFINITY_PRESETS.yaml + METADATA_BLOCKS + PRINCIPLES). So the Domain System scaffold **predates** this session. Any new `config/domains/<domain>/` module MUST integrate with `curators.yaml` (owner + governance + AFFINITY_PRESETS) — this integration was NOT flagged in MATERIALS_REVIEW.

---

## 🔴 CRITICAL CONFLICTS (C1-C3) — ALL CONFIRMED against primary sources

### C1. Cost Model — HYBRID vs FREE-TIER-ONLY  ✅ CONFIRMED
| Source | Position | Primary Evidence |
|--------|----------|------------------|
| `PIVOT_LOG` **D-572** (ratified) | **HYBRID** — 1× Pro ($19.99, ~600 DR/mo) primary + free for non-quota | L830: "1× Google AI Pro ($19.99, ~600 DR/mo) as the primary Deep Research engine" |
| `UNIFIED_STRATEGY` v2.0 | **HYBRID** (§Tier Decision L224-238, Exec Summary L15) | Strategy SSOT |
| `SYNTHESIS` (GAP-9, D-572) | **HYBRID** | Arbitration |
| `HOLISTIC_PLAN` | **FREE-TIER-ONLY** — 3 accounts × 10 = 30 DR/mo, "User will NOT pay for Pro" | L18, L395, L407 |
| `COMPACTION_SUMMARY` | "Free tier only (3 acct, 30 DR/mo)" — cites **D-578** | L18 |
| **USER constraint** | Free tier only, 3 acct, 30 DR/mo, NO Pro | **ABSOLUTE** |

**Root cause (confirmed by source chain):**
1. NLG-A/B/C research subagents all operated on the **8-account frame** (80/mo ceiling)
2. NLG-B recommended **HYBRID** (1× Pro) via its own cost-benefit analysis
3. SYNTHESIS (deepseek-v4-flash-free) ratified NLG-B → wrote **D-572 HYBRID**
4. UNIFIED_STRATEGY corrected to v2.0 with HYBRID (edit #6 = HYBRID Tier Decision)
5. HOLISTIC (latest, nemotron-3-ultra-free) flipped to **user-aligned free-tier-only**
6. COMPACTION_SUMMARY claims free-tier was ratified as **D-578 — but D-578 was NEVER written** (verified: only D-571..D-577 exist)
7. TRACKER_UPDATE_PLAN proposes D-578 (free-tier-only) which would **directly contradict D-572 (HYBRID)**

**Result**: Strategy SSOT (UNIFIED + D-572) = HYBRID; master plan + user = FREE-TIER-ONLY. Implementation follows the SSOT unless corrected. **The contradiction persists because Phase-0 lock-in was never executed.**

### C2. Notebook Count — 6 vs 2  ✅ CONFIRMED
| Source | Count |
|--------|-------|
| PIVOT_LOG **D-574** + UNIFIED + SYNTHESIS | **6-notebook** (NB-1..NB-6) canonical |
| HOLISTIC + COMPACTION_SUMMARY | **2 notebooks** (Active Research + Knowledge Base) — "6-notebook was over-engineered" |

**Impact**: D-574's 6-notebook demands **80 DR/mo** (UNIFIED L49: "20+20+20+10+10+0 = 80"). Under the user's 30 DR/mo free-tier constraint, 6-NB is **impossible**. The 2-notebook architecture is the ONLY one that fits 30 DR/mo. **C2 is a consequence of resolving C1.**

### C3. DR/mo Capacity — Three Numbers  ✅ CONFIRMED
- **30/mo** (HOLISTIC, 3 free accounts × 10) — user constraint
- **80/mo** (UNIFIED, 8 accounts × 10) — superseded strategy frame
- **~600/mo** (NLG-B, SYNTHESIS, 1× Pro @ 20/day) — rejected by user

Three mutually-exclusive numbers in circulation. Only **30/mo** is user-validated.

---

## 🟠 HIGH CONFLICTS (H1-H4) — ALL CONFIRMED

### H1. CONTEXT_WINDOW_OPTIMIZATION_RESEARCH still contains ALL Carmack CUT items  ✅ CONFIRMED
CARMACK_REVIEW defined 6 CUTs (cargo cult / actively harmful). `CONTEXT_WINDOW_OPTIMIZATION_RESEARCH_20260820.md` (Researcher/Jem, COMPLETE status) **still contains every CUT item** and was never superseded:
| CUT Item | Carmack Verdict | CONTEXT_WINDOW line still claiming it |
|----------|-----------------|----------------------------------------|
| SWA on Qwen3 | CUT (no SWA path for Qwen3 in llama.cpp) | L11, L105-147, L167, L340 |
| LLMLingua-2 hot path | CUT (too slow in hot path; async only) | L136-147, L282, L368 |
| gpt-oss-20B | CUT (no MXFP4 mainline; 0 headroom on 12GB) | L12, L177 |
| Nemotron-3-Nano MoE | CUT (marketing fiction; doesn't fit 24GB) | L12, L180 |
| 0.7 GB headroom | FICTION (real = -2.2GB w/ fragmentation) | L359 |
| 6.3 GB weight cache | contradicts resident weights (see H2) | L351 |

**Fix**: Add supersession banner pointing to CARMCK_REVIEW as authoritative; **delete §3 + §5.3** (CUT content) OR mark the doc `DEPRECATED`. Do NOT leave it "COMPLETE / Ready for production" — it is not.

### H2. HOLISTIC Memory Math — Weight Cache vs Models Sum  ✅ CONFIRMED
| Line | Claim | Reality |
|------|-------|---------|
| L93 | Weight cache ~**6.3 GB** | ❌ |
| L94-96 | Qwen3-4B=2.5 + Qwen2.5-Coder-7B=5.0 + Qwen3-1.7B=1.1 = **8.6 GB** | ✅ sum (but executor model missing on disk, see C7) |
| L100 | Peak **7.5 GB** (assumes single-model resident) | ⚠️ sequential OK |
| L359 | Headroom 8.5 GB | ✅ under sequential |

**Contradiction**: the listed models sum to 8.6 GB, not 6.3. The 7.5 GB peak already assumes only ONE model resident (sequential) — but the map lists all three weights as cached. **Fix**: pick ONE model — (a) sequential single-resident (7.5 GB peak, ~9GB headroom) OR (b) all-weights-resident (13.6 GB, NO headroom on 16GB). Recommend **(a)** = matches CARMACK FIX-2 and HOLISTIC's own startup script (L157 `--no-mmap --mlock`).

**Additionally (MISSED by MATERIALS_REVIEW)**: HOLISTIC's `SequentialModelLoader` code sketch (L122-138) uses `mmap_weights()` to maintain a weight cache — but CARMACK FIX-2 explicitly says "mmap is WRONG (llama_free() unmaps); use `--no-mmap --mlock`" and HOLISTIC's own startup script (L157) uses `--no-mmap --mlock`. **The code sketch contradicts the narrative.** Fix: sketch must use `--no-mmap --mlock` + session-scoped context, not a mmap weight cache.

### H3. Free-tier Notebook Limit — 20 vs 100  ✅ CONFIRMED
- HOLISTIC L22: "Free tier = **20** notebooks/account"
- GAP_AUDIT L37 + UNIFIED: **100** notebooks/account (web-verified, multiple sources)

**HOLISTIC's "20" is factually wrong (verified: 100/account).** Note: 100 notebooks/account means NEITHER 2 nor 6 exceeds the cap — the real constraint binding 2-notebook is the **30 DR/mo budget**, not a notebook-count limit. So HOLISTIC's own rationale is misplaced even though its 2-NB conclusion is correct on budget grounds.

### H4. NLG-SMOKE spec — "Pro provisioning"  ✅ CONFIRMED
- TRACKER_UPDATE_PLAN L21: GN-4 `depends_on: ["V-1 Vault", "**Pro provisioning**"]`
- SYNTHESIS L96: "1 **Pro account** + notebooklm-py"
- UNIFIED L246: "Provision 1× Google AI Pro..."

**User constraint says NO Pro.** Under FREE-TIER-ONLY, NLG-SMOKE becomes a **free-account** smoke test. V-1 Vault remains a blocker, but "Pro provisioning" must be **removed** from GN-4 dependencies. Fix: `GN-4 depends_on → ["V-1 Vault"]` only.

---

## 🔴🔴 NEW ISSUES FOUND IN DEEP DIVES (ALL MISSED by MATERIALS_REVIEW)

### 🔴 C7 (BLOCKER): Tier-0 Executor Model `Qwen2.5-Coder-7B` is NOT on Disk — CONFIRMED
| Requirement | Source | Local Availability |
|------------|--------|-------------------|
| Executor (Tier 0) = **Qwen2.5-Coder-7B Q4_K_M** (~5GB) | HOLISTIC L84, L413; CARMCK FIX | **❌ NOT on disk** |
| On-disk GGUF inventory (19 files) | `/media/arcana-novai/omega_library/models/gguf/` | qwen3-0.6b/1.7b/4b (Instruct+Thinking+VL), gemma4-coding (6.9GB), etc. — **NO Qwen2.5-Coder** |
| Config model_registry local entries | `config/model_registry/models/local/` | Only gpt-oss-120b, llama-4-scout, mimo-7b, nemotron-3-ultra, qwen-3.5-72b — **none realistic for 16GB** |
| Config native-gguf backend models | `config/model_registry/providers/native-gguf.yaml` | qwen3-1.7b-local, qwen3-4b-thinking-local, qwen3-0.6b-local |

**Impact**: The Tier-0 executor does not exist locally. Nearest code-specialized model is `gemma4-coding-Q4_K_M.gguf` (6.9 GB) — **exceeds the 5.0 GB executor budget** and is not in the model matrix. So **gap LI-4 (Tier-0 model matrix) is BLOCKED** unless: (a) Qwen2.5-Coder-7B is downloaded, or (b) the matrix is rebuilt around available models (e.g., Qwen3-4B as executor fallback). **Not flagged anywhere in MATERIALS_REVIEW.**

### 🔴 C8 (BLOCKER): CARMACK CUT-5 DR Accounting — 3× Math Error
CARMACK_REVIEW L19 (CUT-5):
> "3-account Gemini free tier rotation | CUT — **30 DR/month per account = 90 DR total**"

But web-verified free tier = **10 DR/month/account** (GAP_AUDIT L36). So:
- Real 3-account total = **30 DR/mo**, NOT 90
- Real token math ≈ 30 DR × 16K = **0.5M tokens/mo** (not 1.4M)
- Real session yield = **5-9 sessions/mo** (not 14-28)

**Impact**: This 3× error is baked into CARMACK_REVIEW which MATERIALS_REVIEW treats as authoritative. If a future reader trusts "90 DR/mo" from Carmack, it conflicts with the ratified 30 DR/mo (C3) and could re-legitimize the 8-account/80-DR math. Fix: correct CUT-5 to "10 DR/account = 30 DR/3 accounts".

### 🔴 C9: ACTIVE_SPRINT Already Tracks NotebookLM — 3-way Duplication Risk
ACTIVE_SPRINT.json already has (verified, structure-inspected):
- `NOTEBKLM-STRATEGY` (in_progress, owner=researcher) — desc still says "**8-account fleet, 5-notebook** architecture, SDP Phase 1 automation path" — **STALE** frame
- `NOTEBKLM-GAP-RESEARCH` (ready, owner=kali) — the 3-subagent research

TRACKER_UPDATE_PLAN proposes adding a NEW `GEMINI-NOTEBOOK` workstream. **Result = 3 overlapping NotebookLM trackers.** The old `NOTEBKLM-STRATEGY` still carries the superseded 8-account frame. **Fix (Phase 0)**: mark `NOTEBKLM-STRATEGY` → `superseded` (8-acct frame), fold `NOTEBKLM-GAP-RESEARCH` into the new GEMINI-NOTEBOOK — do NOT add a third without reconciling.

### 🔴 C10: Domain System — `curators.yaml` Schema Conflict with Proposed Schema
- **Existing** `config/domains/curators.yaml` (2026-08-19, D-569, 14 domains): uses `owner` + `governance` + `target_ctx` + AFFINITY_PRESETS + PLAYBOOK/ARCHITECTURE/CONFIG_REFERENCE/GOTCHAS/LESSONS + MEMORY_BLOCKS + PRINCIPLES
- **Proposed** `config/domains/gemini-notebook/` (TRACKER_PLAN L273-291): uses `metadata.yaml` with `target_context_window`/`rot_class`/`owner`/`cost_model` + `CONTEXT.md` + `PROMPTS/`

**Conflict**: two different domain-module schemas. The proposed `target_context_window`/`rot_class` keys do not match curators.yaml (`target_context`/`governance`). Also **`gemini-notebook` domain is not in curators.yaml at all** (only `research`). The plan proposes `gemini-notebook → owner: researcher`, but curators.yaml already maps `research → researcher`. **Dual-definition risk.** Fix: extend curators.yaml (add gemini-notebook row) + reconcile schema with the engineering/ prototype.

### 🟠 C11: HOLISTIC "2 notebooks" cites "20 notebooks/account" — wrong
Covered in H3. The "20" is wrong (verified 100). The 2-NB conclusion is right on **budget** grounds, not cap grounds.

### 🟠 C12: UNIFIED_STRATEGY internal **5 vs 6 notebook inconsistency**
UNIFIED says "6-notebook canonical" (L36-38, L322) but multiple internal metrics/capacity rows say **5**: L29 "Cross-Account Synthesis → 5 notebooks", L59 "5 used (0.6%)", L67 "80/mo = exactly matches 5-notebook budget", L89 "rotation NB-1→NB-2→…→NB-5", L315 "Cross-Account Synthesis → 5 notebooks". Same doc both "6-notebook" and "5-notebook" — **une number inconsistency across its own sections.** Fix in v2.x.

### 🟠 C13: All UNIFIED success targets are 8-account framed — must scale to 30/mo
UNIFIED targets (80 DR/mo, ≥60 L3/mo, 99% uptime) assume the 8-account 80 DR ceiling. Under free-tier-only 30 DR/mo (user), these targets are **unreachable** and must be rescaled (10-30 DR/mo range, 3-10 L3/mo). Not flagged in MATERIALS.

### 🟠 C14: Model Sizes vs HOLISTIC Memory Map (disk-verified)
| Model | HOLISTIC claim | Actual on disk |
|-------|----------------|----------------|
| Qwen3-4B Q4_K_XL | 2.5 GB | **2.55 GB** ✅ |
| Qwen3-1.7B Q6_K | 1.1 GB | **1.67 GB** ❌ (understated by 0.57 GB) |
| Qwen2.5-Coder-7B | 5.0 GB | **NOT on disk** (C7) |

The critic model (Qwen3-1.7B) is **understated by ~0.6GB** in the memory map — matters for the 16GB budget. Fix: use disk-verified sizes.

### 🟠 C15: Full GGUF inventory contains `DeepSeek-R1-0528-Qwen3-8B-Q3_K_L` (4.13 GB) — but CONTEXT_WINDOW claims "qwen3-8b MoE" for Tier-0
CONTEXT_WINDOW_L12 recommends "qwen3-1.7b + **qwen3-8b MoE**" for 16GB. But there is ALSO a `DeepSeek-R1-0528-Qwen3-8B` (Q3_K_L). And CARMACK CUT a "Qwen3-8B planner" in favor of Qwen3-4B. So the "qwen3-8b MoE" in CONTEXT_WINDOW contradicts both the disk inventory name AND Carmack. Needs reconciliation.

### 🟢 C16: HEADROOM claimed "already installed v0.29.0" — verify
`HEADROOM_RESEARCH §1.2` claims headroom-ai v0.29.0 is in `.venv` + lists DEPENDENCIES.md:18 & pyproject.toml:14. **Recommend verifying** the actual package presence before wiring HeadroomMiddleware (gap #12). Unverified claim.

### 🟢 C18 (minor): FINAL_GAP_AUDIT numbering
Confirmed: 57 entries, duplicates at **19/39/55**, missing **20 & 42**. Header says "56 gaps" but MATERIALS says "54 unique". The right number should be **54 unique** (57 - 3 dup). Fix: renumber to 54 contiguous (or add missing 20, 42 and dedupe).

### C19 (minor): MATERIALS_REVIEW itself has an error — "6.3 vs 8.6 GB" is listed as "Coherent" but is NOT
MATERIALS REVIEW L158 lists "weight cache 6.3 GB" as consistent — but it's the exact H2 contradiction. Minor review-section error to correct.

---

## ✅ COHERENT ITEMS (Verified — genuinely consistent across docs)
| Item | Status | Evidence |
|------|--------|----------|
| Tool = `notebooklm-py` (RPC) | ✅ ALL agree (D-571) |
| Deployment = pip + systemd (no Docker) | ✅ ALL agree (GAP-2) |
| Auth = `master_token.json` + RotateCookies ≤600s + Patchright channel=chrome | ✅ ALL agree (D-577) |
| Token density = 5-25 sweet spot | ✅ ALL corrected (D-576) |
| SDP §10 gate honored | ✅ ALL agree (D-575) |
| Curator = config flag | ⚠️ Schema mismatch with curators.yaml (C10) |
| Carmack corrections present in HOLISTIC | ✅ Consistent — EXCEPT memory/sketch (H2) and model inventory (C7) |
| zRAM: 8GB zstd, swappiness=100, zswap disabled | ⚠️ See C-RAM (below) — D-526 contradiction |
| Headroom integration points | ✅ Consistent |
| **Naming: Gemini Notebook = NotebookLM** | ✅ Consistent — every doc carries the "renamed July 2026, same product/limits" note (SYNTHESIS L13, RESEARCH. Note L6, GAP_AUDIT L39) |

> ✅ **Naming clarification (user):** Gemini Notebook is the rebrand Google applied to NotebookLM in July 2026 — **same product, same limits, new name**. The materials handle this correctly: all docs note "NotebookLM was renamed Gemini Notebook in July 2026 (same product, same limits); 'NotebookLM' retained for search-artifact continuity." No correction needed to the naming; the strategy content is about the same product under either name.

## 🔴 C-RAM (NEW, BLOCKER): zRAM/zswap Decision Reversal — D-526 vs 2026-08-20 Plans
**This is the most consequential issue MATERIALS_REVIEW missed.**
- **D-526 (PIVOT_LOG L17)**: "**zswap > zRAM for Desktop with NVMe**" — **RATIFIED**, migrate TO zswap (max_pool_percent=25, zsmalloc)
- **D-527** (L18): "Never run zswap + zRAM simultaneously. Migration path: swapoff -a → rmmod zram → enable zswap → create NVMe swap"
- **BUT all 2026-08-20 plans** (HOLISTIC L255-256, HEADROOM §2 L182 "**zRAM ONLY, zswap DISABLED**", COMPACTION L21, TRACKER D-581 "zRAM-Only") mandate **zRAM-only, zswap DISABLED** — and cite "**D-527 locked zRAM**" as justification.

**PROBLEM**: D-527 does NOT say "zRAM only". D-527 says "never both" and provides a migration path **TO zswap**. D-526 explicitly chose **zswap over zRAM**. The new zRAM-only directive **reverses D-526** — and proposed **D-581 (zRAM-only) would directly contradict D-526 (zswap, RATIFIED)**. MATERIALS_REVIEW's "Coherent" line "zRAM: 8GB zstd, swappiness=100, zswap disabled — D-527/D-581 consistent" is **WRONG** — D-527 is not evidence for zRAM-only.

**Required**: Register a **new decision formally superseding D-526** (zRAM-only, documenting Carmack's 2026-08-10 rejection rationale + the actual D-527 intent). Do **NOT** leave D-526 RATIFIED while code mandates zRAM-only — that is a direct PIVOT_LOG contradiction that will cause config drift at deployment.

---

## 🎯 ROOT CAUSE ANALYSIS (concurred)

**The user constraint (FREE-TIER-ONLY, 3 acct, 30 DR/mo, NO Pro) was never propagated to the research subagents or synthesis arbitration.**
1. NLG-A/B/C all operated on the **8-account frame** (80/mo ceiling)
2. NLG-B recommended **HYBRID** (1× Pro) from its own cost analysis
3. SYNTHESIS ratified HYBRID → **D-572**
4. UNIFIED corrected to v2.0 with HYBRID (edit #6)
5. HOLISTIC flipped to user-aligned free-tier-only
6. COMPACTION claims free-tier ratified (D-578) — never written
7. TRACKER proposes D-578 which contradicts D-572
8. **Tracker never executed → contradiction persists in the tracking infra**

---

## ⛔ GO / NO-GO VERDICT

**⛔ NO-GO for implementation until the blocking issues are arbitrated.** The 6 new workstreams (Phase 0) and 54 gaps will inherit the strategy contradiction if implemented as-documented.

**BLOCKING (must resolve before any code or Phase-0 tracker lock-in):**
1. **C1-C3 cost-model arbitration** — Ratify free-tier-only (3 acct, 30 DR/mo, NO Pro). Supersede D-572. Reconcile D-573/574.
2. **C2 notebook count** — 2-notebook under 30/mo. Amend D-574.
3. **C-RAM zRAM/zswap** — formal supersession of D-526 (or reconcile).
4. **C7 Tier-0 executor model gap** — resolve Qwen2.5-Coder-7B absence BEFORE LI-4.

**HIGH (resolve before implementation):**
5. **H1 CUT content** — supersede/delete CONTEXT_WINDOW CUT §.
6. **H2 memory math** — fix 6.3/8.6GB + code sketch (no mmap); fix C14 model sizes.
7. **H3** notebook limit 20→100.
8. **H4** remove "Pro provisioning" from GN-4.
9. **H4 (C8) Carmack 3× DR error**; **C9** workstream-dup; **C10** curators schema; **C12** 5/6-NB; **C13** metrics scale.

**After resolution — corrected execution order:**
1. PIVOT_LOG amendments (below) → verify D-xxx appended, D-572/D-526 superseded
2. Fix UNIFIED_STRATEGY (free-tier-only, 2-NB, remove Pro refs, rescale targets, 5/6-NB)
3. Fix HOLISTIC (memory map, code sketch, notebook-limit, model matrix)
4. Fix CONTEXT_WINDOW (banner/delete CUT)
5. Fix FINAL_GAP_AUDIT (renumber 54 unique) + GAP_REGISTRY sync
6. Reconcile C9 (workstreams) + C10 (curators.yaml schema)
7. THEN execute Phase 0 lock-in with corrected keys → Phase 1-3 implementation

---

## 📝 PIVOT_LOG AMENDMENT LANGUAGE (ready to use on arbitration)

### Amendment 1 — supersede D-572 (Hybrid → Free-Tier-Only)
```markdown
## D-582: Free-Tier-Only Cost Model — SUPERSEDES D-572 (2026-08-20)
**Supersedes**: D-572 (1× Pro HYBRID, ratified earlier this session)
**Decision**: Gemini Notebook (NotebookLM) Deep Research = **FREE TIER ONLY — 3 accounts × 10 DR/mo = 30 DR/mo**. **No Pro payment.** 2-notebook architecture (Active Research + Knowledge Base) to fit budget. 8-account fleet retired (ToS ban risk + ops burden).
**Context**: Absolute user constraint: NO Pro; 3 free accounts = 30 DR/mo. NLG-B/SYNTHESIS Hybrid withdrawn. Removes the "Pro provisioning" blocker (H4).
**Mandate**: M7 (sovereign choice), M2 (engine purity — user's preferred cost posture).
**Status**: ✅ RATIFIED (supersedes D-572)
```

### Amendment 2 — amend D-573/D-574 (80→30, 6-NB→2-NB)
```markdown
## D-583: Notebook Count + Budget — SUPERSEDES D-573/D-574 (2026-08-20)
**Supersedes**: D-573 (80 DR/mo, 8×10), D-574 (6-notebook canonical)
**Decision**: Notebook architecture = **2 notebooks** (Active Research, Knowledge Base). DR budget = **30/mo (3×10)**. NB-2/NB-3/NB-6 (which require 80 DR/mo) are **parked/standby** until the user authorizes a higher budget.
**Status**: ✅ RATIFIED
```

### Amendment 3 — supersede D-526 (zswap) with zRAM-only
```markdown
## D-584: zRAM-Only Locked — SUPERSEDES D-526 (2026-08-20)
**Supersedes**: D-526 (zswap > zRAM, previously RATIFIED); reaffirms D-527 (never both)
**Decision**: zRAM-ONLY config — 8GB zstd level=15, swappiness=100, zswap DISABLED, cgroup MemoryMax=6G. Rationale: 16GB CPU-only machine — zRAM expands usable RAM (no swap); zswap was a rejected detour (Carmack 2026-08-10). D-527's "never run both" stays LOCKED.
**Status**: ✅ RATIFIED
```

### Amendment 4 — D-578..D-581 as originally scoped (Domain/Inference/Notebook) — REUSED, not contradicted
The TRACKER_UPDATE_PLAN's D-578 (Gemini free-tier), D-579 (domain docs), D-580 (local inference tiers), D-581 (doc/roadmap) proposals are structurally sound; **D-578 and D-581 wording must be adjusted** so D-578 references the new D-582/D-583 free-tier outcome (not conflict), and D-581 references zRAM-only per Amendment 3. No new numbers needed beyond D-582/583.

---

## 📋 VALIDATION GATE AFTER AMENDMENTS (run before Phase 0)
```bash
# 1. Verify D-582/D-583 + zRAM amendment present; D-572/D-526 marked superseded
grep -A3 "D-582\|D-583\|zRAM-Only Locked\|SUPERSEDES D-572\|SUPERSEDES D-526" docs/decisions/PIVOT_LOG.md

# 2. Re-verify ACTIVE_SPRINT has NO new workstreams until after amendment
# 3. Re-verify UNIFIED has no "Pro provisioning" / 80DR / 6-NB remaining ×   free-tier alignment
```

*⬡ OMEGA ⬡ CLINE ✓ ⬡ deepseek-v4-flash-free ⬡ cline ⬡ trc_cline_final_review ⬡ 2026-08-20*
