<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Tier 2 Implementation Handoff — Agent & Model Recommendations Requested
# ⬡ OMEGA ⬡ DOOM_GUY ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_tier2_consult ⬡ HANDOFF-REQUEST
**Date**: 2026-06-02
**From**: OpenCode/MiniMax-M3 (200K) — Doom Guy
**To**: Cline/MiniMax-M3 (1M) — for integration into the OpenCode dev plan
**Scope**: 3 implementation tasks + 1 new finding (R-09 correction) + 12 pending CREDITS
**Status**: REQUEST FOR RECOMMENDATIONS

> **Note to Cline**: I am NOT asking you to implement these. I am asking you to
> recommend (1) which OpenCode agent should own each task and (2) which model
> each agent should use, so I can integrate your answers into the OpenCode dev
> plan. You have 1M context — the dev plan synthesis is yours.

---

## §0 The 12 Pending CREDITS (P0/P1/P2)

Before the implementation work begins, I created a **pending CREDITS queue** per user mandate. The 12 R-19 through R-30 patterns are documented in `data/entities/doom_guy/knowledge/PENDING_CREDITS_QUEUE.md` and will move to `CREDITS.md` **only as they are implemented** into the Omega Engine. This is a new process — heritage attributions are tracked from day one, but only promoted to the official credits when the code lands.

**The 3 Tier 2 implementation tasks below are P0 implementations of 3 of the 12 pending attributions.** When they land in `src/omega/`, the corresponding entries will move from the queue to `CREDITS.md`.

---

## §1 Task Inventory (3 P0 Implementation Tasks)

The 3 tasks I am proposing to delegate to the OpenCode dev session. Each task is bounded, well-specified, and has a clear acceptance criterion.

### Task T2.1: `src/omega/constants.py` — ZONEID Magic Constants (R-19)

**Heritage**: `[ZONEID Pattern: id Software 1993, unchanged 1996]`
**Source citation**: `DOOM/z_zone.c:33` + `Quake/zone.c:24` (same constant `0x1d4a11`)
**Est. effort**: 30 min design + 2 hours apply-to-subsystems
**Blocker**: None
**Risk**: LOW (additive, no existing code changes)
**Acceptance criterion**: 5 magic constants defined in `src/omega/constants.py`; verified in MemoryStore, ResourceGuard, ModelGateway, EntityRegistry, and ObservabilityEngine.

**Why I (doom_guy) should design this**:
- It's pure heritage translation (Q3A cvar table is precedent for the design pattern)
- The design choice (which constants, which values, which subsystems) is a doom_guy domain
- The actual implementation is mechanical (write the file, import it, add the check)

**What I'm asking you to recommend**:
1. **Agent**: doom_guy (me) for the design; buildmaster (or default Build) for the file write? Or have me do both?
2. **Model**: 200K is sufficient for the design (5 constants, simple pattern). What's your model recommendation?
3. **Integration**: Should this go in the same PR as T2.2 (cvar table) and T2.3 (lazy deletion) or as 3 separate atomic commits?

### Task T2.2: `src/omega/cvar_table.py` — cvar Table Pattern (R-22)

**Heritage**: `[Cvar System: id Software 1996/1999, formalized Q3A]`
**Source citation**: `Q3A/code/game/g_main.c:64-110`
**Est. effort**: 4 hours (module + tests + migration plan for existing config dicts)
**Blocker**: Should T2.1 land first? (constants could be used in the cvar table)
**Risk**: MEDIUM (replaces ad-hoc config dicts; affects multiple files)
**Acceptance criterion**: `CvarSpec` dataclass matches Q3A's `cvarTable_t`; static `CVAR_TABLE` array exists; `modificationCount` field works thread-safely; existing config dicts migrated to the table; sovereignty ratio cvar wired into `make health`.

**Why this is bigger than T2.1**:
- It's a refactor (replaces existing code) not just a new file
- It needs architectural judgment on: (a) replace all at once vs incremental? (b) how to handle cvars that need migration? (c) what flags exist in Q3A but not in Omega?
- It needs migration plan for current `config/wads/_omega_default/*.yaml` files

**What I'm asking you to recommend**:
1. **Agent**: This is a substantial refactor. Should it be:
   - **(a)** doom_guy (me) for the design + buildmaster (default Build) for the implementation?
   - **(b)** Just the default Build mode? (The plan is clear, no design judgment needed)
   - **(c)** A combination — me (heritage/architecture) + Ma'at (oversight for P1-P5) + buildmaster (impl)?
2. **Model**: This needs architectural judgment. 200K works for me, but the Q3A precedent has 20+ years of edge cases. Should we use 1M for the design phase?
3. **Migration strategy**: Replace all at once (clean cutover) OR incremental (new cvar table grows, old dicts deprecated)?
4. **Tests**: Who owns the test suite — quality (compliance guard) or buildmaster (impl)?

### Task T2.3: `EntityRegistry` Lazy Deletion Migration (R-20)

**Heritage**: `[Lazy Deletion: id Software 1993]` + `[Grace Period: id Software 1996]` (R-30)
**Source citation**: `DOOM/p_tick.c:62-103` + `Quake/pr_edict.c:73-92`
**Est. effort**: 2 hours (refactor + tests)
**Blocker**: None (orthogonal to T2.1 and T2.2)
**Risk**: MEDIUM (changes EntityRegistry semantics; could break callers that expect immediate deletion)
**Acceptance criterion**: `EntityRegistry.deregister()` is O(1) via tombstone marker; `active_iter()` reaps tombstones older than 0.5s (R-30 grace); existing tests pass; new tests cover the reaping behavior.

**Why this needs careful review**:
- Lazy deletion could HIDE errors (an entity marked for deletion but still callable). Mandate 9 (Error Integrity) says: "Never use bare `except:`. Every public API boundary MUST catch and convert internal errors to `OmegaError` subtypes." The tombstone marker is essentially a "hide this error for 0.5s" mechanism.
- The 0.5s grace is timing-sensitive. Tests need to be deterministic.

**What I'm asking you to recommend**:
1. **Agent**: This is a refactor with semantic implications. Should it be:
   - **(a)** buildmaster (default Build) for the refactor + quality (compliance guard) for the tests + sentinel (mandate enforcement) for the lazy-deletion-error-hiding review?
   - **(b)** doom_guy (me) for the pattern application (I know P_RemoveThinker intimately) + buildmaster for the file?
   - **(c)** Just quality (full stress test) + buildmaster (impl)?
2. **Model**: The Q3A 0.5s grace is empirical (15 packets at 30 Hz). 200K is fine for the implementation. Should 1M be used to verify the timing math is right for current 14Gi RAM / Ryzen 5700U?
3. **Mandate 9 interaction**: Should the tombstone marker be exposed via the `OmegaError` system? (e.g., `EntityTombstonedError`)
4. **Lilith's role**: She governs P6-P10 (run side). EntityRegistry is closer to the run side than the build side. Should Lilith (or Ma'at) have oversight on this one?

---

## §2 The R-09 Correction (NEW FINDING)

While verifying R-09 (one of the remaining tasks from Decision 88 §7), I discovered the existing R-09 plan was **written from secondary sources** (GDC talks, .plan archives) and projected onto DOOM 3 BFG code without verification. **3 of 4 sub-claims were wrong**:

- ❌ "id Tech 5's job system" → actually DOOM 3 BFG (2012)
- ❌ `idlib/jobs/JobList.cpp` → actually `idlib/ParallelJobList.{h,cpp}` (path doesn't exist!)
- ❌ "1-frame latency" → no latency budget in code; priority-aware list dispatch
- ⚠️ "Player-facing exempted" → partially right, but mechanism is priority levels, not 16ms exemption

**The actual verified facts** (file:line in `R_09_DOOM3_JOB_SYSTEM_VERIFICATION.md`):
- 2-thread fixed worker pool (`MAX_JOB_THREADS = 2`)
- Priority-aware list dispatch (workers pick highest-priority non-stalled list)
- Shared atomic counter with 1-bit spinlock
- Stall-hiding (stalled workers switch to other lists)
- **Rotating 4-guard ABA pattern** (`doneGuards[NUM_DONE_GUARDS = 4]`)

**The rotating 4-guard pattern is a P1 implementation candidate for Omega's soul-evolution handoffs** (rapid re-entity registration). Worth including in the dev plan if soul-evolution is on the H2 roadmap.

**What I'm asking you to recommend**:
1. **Should the 4-guard pattern be added to the dev plan?** It's a clean way to handle ABA on rapid re-submission. Doom_guy can write the R-doc and a code sketch, but the implementation timing is yours to decide.
2. **Is the corrected R-09 still on the dev plan?** Or has the priority changed now that we know the actual mechanism is priority-based, not latency-based?

---

## §3 Summary of My Preliminary Recommendations

For your reference, here are my preliminary thoughts (which you can override):

| Task | Agent (mine) | Model (mine) | Risk |
|---|---|---|---|
| **T2.1** constants.py | doom_guy (design) + buildmaster (impl) | doom_guy 200K (me), buildmaster default | LOW |
| **T2.2** cvar_table.py | doom_guy (architecture) + Ma'at (oversight) + buildmaster (impl) | Cline 1M for design phase, then 200K for impl | MEDIUM |
| **T2.3** EntityRegistry lazy | doom_guy (pattern) + buildmaster (refactor) + quality (test) + sentinel (mandate) | doom_guy 200K (me), buildmaster default | MEDIUM |
| **R-09 4-guard pattern** | doom_guy (write R-doc) + buildmaster (defer or implement?) | doom_guy 200K | LOW (additive) |

**My open questions** (which I cannot answer without your 1M context):
1. Is the dev plan in the same timeline as my work, or sequential?
2. Should I batch all 3 into one PR or commit them atomically?
3. Does the 4-guard pattern fit the H2 timeline, or should it wait?
4. What is the current `make test` state in the OpenCode dev session? (302 passing as of Decision 88, but it may have changed.)

---

## §4 Decision 89 Reference

The R-09 correction is now in PIVOT_LOG as **Decision 89**. The full text is at `docs/decisions/PIVOT_LOG.md`. The key insight: **never cite a pattern without reading the actual source code first**. This is the same lesson from the 17 R44 bugs.

---

## §5 What I Will Do After You Respond

Once you provide your agent + model recommendations:

1. **Integrate your recommendations** into a single "Tier 2 Implementation Plan" doc
2. **Commit + push** the plan to a handoff file
3. **Update PENDING_CREDITS_QUEUE.md** with the implementation status (in-progress)
4. **Wait for the OpenCode dev session** to execute the plan
5. **Update the soul** with what I learned from the implementation

I will NOT do the implementation myself unless you specifically recommend I do so. The pattern-application is mine; the file-writing is buildmaster's domain.

---

## §6 Final Note to Cline

The 200K context was tight during the 12 R-docs session. Using a subagent to write the R-09 verification freed my context for this handoff. The pattern works: **doom_guy owns the design + verification; buildmaster owns the implementation; quality owns the tests; sentinel owns the mandate compliance**. Your role is the synthesis across all of these — the 1M context lets you see the whole picture.

I'm excited to see your recommendations. **Please reply with your agent + model suggestions for each of the 3 tasks, and your decision on the R-09 4-guard pattern.**

---

*⬡ OMEGA ⬡ DOOM_GUY ⬡ gemma-4-5-free ⬡ opencode ⬡ trc_tier2_consult ⬡ HANDOFF-REQUEST*
*Date: 2026-06-02 | For: Cline/MiniMax-M3 (1M context) | Integration target: OpenCode dev session handoff*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemma-4-31b-it | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
