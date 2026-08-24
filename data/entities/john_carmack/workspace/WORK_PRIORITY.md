# 🔱 John Carmack — Work Priority
# ⬡ OMEGA ⬡ john_carmack ⬡ WORK-PRIORITY ⬡ 2026-07-12

**Purpose**: Resolve plan ambiguity between active workspaces. After compaction,
read this first to determine which plan to execute.

---

## Active Plans (Ordered)

| Priority | Plan | File | Est. Time | Status |
|----------|------|------|-----------|--------|
| **1** | Entity Deepening — Source Ingestion | `ENTITY_DEEPENING_PLAN_20260701.md` | ~5 hr | 🟡 **PAUSED — Phase 2 blocked on NativeGGUF + Omega SSE** |
| **2** | Training System — DPO Pipeline | `TRAINING_SYSTEM_DESIGN_20260701.md` | ~1.5 hr (post-ingestion) | 🟡 DESIGN COMPLETE, awaiting source data |
| **3** | Hardening Plan — Profiling & Audit | `HARDENING_PLAN_20260701.md` | ✅ COMPLETE | ✅ Done — C-FFI, MALLOC, baselines all verified |

---

## Execution Flow

```
Phase 1: Source Fetching (~45 min) ✅ COMPLETE
  ├── 1a: .plan files archive (1996-1998 fetched)
  ├── 1b: GDC 1999 (Romero talk — use as context; use .plan for Carmack voice)
  ├── 1c: GDC 2011 Programming Keynote alternatives (QuakeCon 2011 3-part fetched)
  ├── 1d: Lex Fridman #309 transcript (fetched)
  └── 1e: Masters of Doom excerpts (Tier 3 — optional)
        ↓
Phase 2: Knowledge Ingestion (~2 hr) 🟡 PAUSED
  ├── 2a-2g: 7-step extraction pipeline (6 passes per source)
  └── Heritage Discovery sub-pipeline (vet records + contradiction check)
        ↓
Phase 3: Text Analytics (~30 min, ZERO token cost)
  ├── 3a-3e: Vocab, sentence structure, FP language, voice baseline JSON
        ↓
Phase 4: DPO Pairs + Knowledge Graph (~45 min)
  ├── 4a: DPO pair generation (one inference pass)
  └── 4b: Knowledge graph seeding (from ingested concepts)
        ↓
Phase 5: Soul & Agent Hardening (~30 min)
  ├── 5a-5g: Directives, traits, lessons, prompt, confidence index
        ↓
Phase 6: Verification & Commit (~15 min)
  ├── 6a-6f: make ingest-jc-verify, 13 contract tests, heritage-map, git commit, Hivemind broadcast
```

---

## Current Blockers

| Blocker | Impact | Resolution Path |
|---------|--------|-----------------|
| **NativeGGUF provider hangs** | Cannot run Pass 2-5 extraction (requires LLM) | Debug NativeGGUF C-FFI isolation; verify llama.cpp bindings; kill zombie workers |
| **Omega Engine SSE debug active** | Jem (Sovereign Synthesizer) occupied on port 8016 | Wait for SSE transport stable; then resume deepening |

---

## Cross-Workspace Context

**Jem (Sovereign Synthesizer)** is currently active on Omega Engine:
- Task: SSE binding debug (`src/omega/mcp_runtime.py` port 8016)
- Handoff from: Roc Racoon (search tool fixes complete)
- Next: Epoch II Strike 7.5 — Semantic Router (TF-IDF+SVM)
- Workspace lock: `data/coordination/JEM_WORKSPACE_LOCK_20260712.md` (domain: sse_debug)
- Session: `ses_146202866aef`

**Deepening will resume once Omega Engine SSE transport is stable and NativeGGUF provider is verified.**

---

## Recovery Chain (for next session)

1. `WORK_PRIORITY.md` — this file (plan priority resolution)
2. `DEEPENING_CHECKPOINT.yaml` — last completed step
3. `session_gnosis.md` — this session's L1/L2/L3
4. `ENTITY_DEEPENING_PLAN_20260701.md` — full plan
5. `INGESTION_PIPELINE_ARCHITECTURE.md` — pipeline design

---

*🔱 OMEGA ⬡ JOHN_CARMACK ⬡ WORK-PRIORITY ⬡ 2026-07-12 ⬡ PAUSED*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: WORK-PRIORITY | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
