# 🔱 John Carmack — Work Priority
# ⬡ OMEGA ⬡ john_carmack ⬡ WORK-PRIORITY ⬡ 2026-07-01

**Purpose**: Resolve plan ambiguity between active workspaces. After compaction,
read this first to determine which plan to execute.

---

## Active Plans (Ordered)

| Priority | Plan | File | Est. Time | Status |
|----------|------|------|-----------|--------|
| **1** | Entity Deepening — Source Ingestion | `ENTITY_DEEPENING_PLAN_20260701.md` | ~5 hr | 🔴 **READY — Phase 1 not started** |
| **2** | Training System — DPO Pipeline | `TRAINING_SYSTEM_DESIGN_20260701.md` | ~1.5 hr (post-ingestion) | 🟡 DESIGN COMPLETE, awaiting source data |
| **3** | Hardening Plan — Profiling & Audit | `HARDENING_PLAN_20260701.md` | ✅ COMPLETE | ✅ Done — C-FFI, MALLOC, baselines all verified |

---

## Execution Flow

```
Phase 1: Source Fetching (~45 min)
  ├── 1a: .plan files archive
  ├── 1b: GDC 1999 (Romero talk — use as context; use .plan for Carmack voice)
  ├── 1c: GDC 2011 Programming Keynote alternatives
  ├── 1d: Lex Fridman #309 transcript
  └── 1e: Masters of Doom excerpts
        ↓
Phase 2: Knowledge Ingestion (~2 hr)
  ├── 2a-2g: 7-step extraction pipeline (6 passes per source)
  └── Heritage Discovery sub-pipeline (vet records + contradiction check)
        ↓
Phase 3: Text Analytics (~30 min, ZERO token cost)
  ├── 3a: Vocabulary analysis
  ├── 3b: Sentence structure profiling
  └── 3c: FP language frequencies
        ↓
Phase 4: DPO + Graph (~45 min, ONE inference pass)
  ├── 4a: DPO pair generation
  └── 4b: Knowledge graph seeding
        ↓
Phase 5: Soul Hardening (~30 min)
  ├── 5a-5e: Directives, traits, lessons, prompt, confidence index
  └── git commit + Hivemind broadcast
```

## Current State

**Last Checkpoint**: None (not started)
**Current Phase**: Phase 0 (Pre-Execution)
**Blockers**: None
**Dependencies**: None — all sources are publicly fetchable

## References

- Checkpoint file: `DEEPENING_CHECKPOINT.yaml`
- Session anchor: `session_gnosis.md`
- Pipeline architecture: `INGESTION_PIPELINE_ARCHITECTURE.md`
- Agent prompt: `.opencode/agents/john_carmack.md`
