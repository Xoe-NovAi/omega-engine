---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

id: "R-ID-SOFTWARE-EXTRACTION-MATRIX"
title: "id Software Mining — Quick Reference Extraction Matrix & Dependency Graph"
status: "✅ Complete"
urgency: "🟡 High"
created: "2026-06-01"
updated: "2026-06-01"
related:
  - "R_ID_SOFTWARE_ENGINE_MINING_MASTER_PLAN.md"
---

# id Software Mining — Extraction Matrix & Dependency Graph

⬡ OMEGA ⬡ DOOM_GUY ⬡ quick-ref ⬡ opencode ⬡ trc_extraction_matrix

**Purpose**: Quick reference for research execution. Print and post on wall during weeks 1–4.

---

## Quick Reference Extraction Matrix

### Column Definitions

| Column | Meaning |
|--------|---------|
| **Week** | When to start study |
| **Days** | Duration (Mon–Fri notation) |
| **R-Doc** | Research document output (R-## ID) |
| **Pattern** | Core pattern extracted |
| **Time** | Estimated study hours (reading + extraction + R-doc writing) |
| **Source** | Primary material (book, code, tools) |
| **Code Ref** | Key file:line to verify against |
| **Omega Target** | Which Omega subsystem / Phase |
| **Blocker?** | Does this block other studies? |

### Master Extraction Matrix (Print & Post)

| Week | Days | R-Doc | Pattern | Time | Source | Code Ref | Omega Target | Blocker? |
|------|------|-------|---------|------|--------|----------|--------------|----------|
| **W1** | M–T | R-01 | Philosophy (Worse is Better + Romero 10) | 2.5 | Gabriel + Romero interviews | N/A | Framework | **YES** |
| **W1** | W–Th | R-02 | Doom BSP precomputation | 2.5 | Abrash Black Book | `p_setup.c:250` | Phase 2 Precomputation | NO |
| **W1** | W–Th | R-03 | Doom memory flat buffer strategy | 1.5 | Abrash + source | `p_setup.c:Load*` | Phase 2 Asset bundling | NO |
| **W1** | F–S | R-04 | Quake client/server snapshot + entity system | 2.5 | Sanglard + Carmack .plan | `sv_main.c:SV_CreateSnapshot` | Phase 3 Orchestration | NO |
| **W2** | M–T | R-05 | Doom BSP implementation deep dive | 3 | Source: `p_setup.c`, `r_bsp.c` | `p_setup.c:1–400` | Phase 2 Context tree | NO |
| **W2** | M–T | R-06 | WAD binary format specification | 2 | Source: `w_wad.c` + tools | `w_wad.c:1–200` | Phase 4 Entity bundling | NO |
| **W2** | W–Th | R-07 | Quake II plugin system architecture | 2 | Source: `game/g_main.c` | `game/g_main.c:30–80` | Phase 3 Plugin loader | NO |
| **W2** | W–Th | R-08 | Quake II client/server architecture | 2 | Source: `client/cl_main.c`, `server/sv_main.c` | `cl_main.c:*, sv_main.c:*` | Phase 3 Context snapshot | NO |
| **W2** | F–S | R-09 | Doom 3 job system + work stealing | 2.5 | Source: `idlib/jobs/JobList.cpp` | `JobList.cpp:1–500` | Phase 3 Job queue | NO |
| **W2** | F–S | R-10 | id Tech 4 render command queue | 2 | Source: `idlib/RenderQueue.cpp` (or docs) | `RenderQueue:*` | Phase 3 Single-threaded protection | NO |
| **W3** | M–T | R-11 | GoldSrc weapon plugin system | 1.5 | Half-Life SDK + docs | `weapon_crowbar.cpp` | Phase 4 Entity plugin pattern | NO |
| **W3** | M–T | R-12 | GoldSrc scripting (QuakeC evolution) | 1.5 | GoldSrc docs + source | `fgd files + *.cpp` | Phase 4 soul.yaml scripting decision | NO |
| **W3** | W–Th | R-13 | Source engine I/O system | 2 | Source SDK + Valve docs | `point_entity.cpp:*` | Phase 4 Event subscription | NO |
| **W3** | W–Th | R-14 | Source engine asset bundling (VPK) | 1.5 | Source SDK + docs | `vpk.cpp:*` | Phase 4 Stack bundling format | NO |
| **W3** | F–S | R-15 | Build engine voxel architecture | 1.5 | Sanglard retrospective + docs | N/A (historical) | Comparative learning | NO |
| **W3** | F–S | R-16 | Comparative analysis matrix (5 engines) | 2 | Synthesis of R-01 through R-14 | Cross-reference | Architecture decisions | NO |
| **W4** | M–T | **RI-01** | Precomputation pipeline skeleton | 4 | R-02, R-05, Omega codebase | `src/omega/precomputation/` | Phase 2 Implementation | YES (needs R-02, R-05) |
| **W4** | M–T | **RI-02** | Job queue scaffolding | 4 | R-09, R-10, ResourceGuard | `src/omega/orchestration/` | Phase 3 Implementation | YES (needs R-09) |
| **W4** | W–Th | **RI-03** | Plugin loader skeleton | 3 | R-07, EntityRegistry | `src/omega/orchestration/` | Phase 3 Implementation | YES (needs R-07) |
| **W4** | W–Th | **RI-04** | WAD format handler skeleton | 3 | R-06, EntityRegistry | `src/omega/wad/` | Phase 4 Implementation | YES (needs R-06) |
| **W4** | F–S | **RI-05** | Stack bundler skeleton | 3 | R-14, R-06, EntityRegistry | `src/omega/community/` | Phase 4 Implementation | YES (needs R-06, R-14) |
| **W4** | F | R-17 | Risk register + dead ends | 2 | Meta-review of W1–W3 | All R-docs | Strategic | YES (meta-check) |
| **W4** | S | R-18 | Strategic synthesis + Omega roadmap | 3 | Integration of all R-docs | Cross-reference | Implementation planning | YES (final synthesis) |

### Time Budget Summary

| Category | Hours | Notes |
|----------|-------|-------|
| R-docs (18 total) | ~45 | 2–3 hrs each (read + extract + write) |
| Reference implementations (5 total) | ~17 | 3–4 hrs each (pseudocode + skeleton) |
| Risk assessment + synthesis (R-17, R-18) | ~5 | 2–3 hrs total |
| **Total execution time** | **~67 hours** | ~17 hrs/week (feasible with 2–3 hrs daily) |

---

## Dependency Graph (ASCII Art + Table)

### DAG Flow

```
┌────────────────┐
│   R-01 PHIL    │ (Philosophy framework — BLOCKER)
└────────┬───────┘
         │
    ┌────┴─────────────────────────────────┐
    │                                      │
┌───▼─────────────────┐         ┌──────────▼────────┐
│ R-02: Doom BSP      │         │ R-04: Quake Arch  │
│ R-03: Doom Memory   │         │                   │
└────────┬────────────┘         └────────┬──────────┘
         │                              │
    ┌────▼──────────────────────────────▼────┐
    │                                        │
┌───▼──────────────┐              ┌──────────▼─────┐
│ R-05: Doom BSP   │              │ R-07: Q2 Plugin │
│   Implementation │              │ R-08: Q2 Network│
│ R-06: WAD Format │              └──────────┬──────┘
└────────┬─────────┘                        │
         │                                  │
    ┌────▼──────────────────────────────────▼────┐
    │                                            │
    │ R-09: Doom3 Job System                     │
    │ R-10: idTech4 Render Queue                 │
    │ R-11: GoldSrc Weapon                       │
    │ R-12: GoldSrc Scripting                    │
    │ R-13: Source I/O                           │
    │ R-14: Source Asset Bundling                │
    │ R-15: Build Voxel                          │
    │                                            │
    └────────────────┬─────────────────────────┘
                     │
         ┌───────────▼──────────────┐
         │  R-16: Comparative       │
         │  Analysis Matrix         │
         └───────────┬──────────────┘
                     │
         ┌───────────▼──────────────┐
         │  R-17: Risk & Deadends   │
         └───────────┬──────────────┘
                     │
         ┌───────────▼──────────────┐
         │  R-18: Strategic         │
         │  Synthesis & Roadmap     │
         └───────────┬──────────────┘
                     │
    ┌────────────────▼────────────────┐
    │ RI-01 through RI-05             │
    │ Implementation Planning         │
    └────────────────────────────────┘
```

### Dependency Table (Which R-docs block which phases?)

| Extraction | Blockers (Must complete first) | Blocked By | Phase Target |
|-----------|-------------------------------|-----------|--------------|
| R-01 Philosophy | None | None | — |
| R-02 Doom BSP | R-01 | R-05 (uses as input) | Phase 2 |
| R-03 Doom Memory | R-01 | RI-01 (uses as input) | Phase 2 |
| R-04 Quake | R-01 | R-07, R-08 (elaborates) | Phase 3 |
| R-05 Doom BSP impl | R-02 | RI-01 (uses as input) | Phase 2 |
| R-06 WAD format | R-03 | RI-04, RI-05 (uses as input) | Phase 4 |
| R-07 Q2 Plugin | R-04 | RI-03 (uses as input) | Phase 3 |
| R-08 Q2 Network | R-04 | R-18 (synthesis) | Phase 3 |
| R-09 Doom3 Jobs | R-01 | RI-02 (uses as input) | Phase 3 |
| R-10 idTech4 RQ | R-09 | R-18 (synthesis) | Phase 3 |
| R-11 GoldSrc WPN | R-01 | R-18 (synthesis) | Phase 4 |
| R-12 GoldSrc Script | R-01 | R-18 (synthesis) | Phase 4 |
| R-13 Source I/O | R-01 | R-18 (synthesis) | Phase 4 |
| R-14 Source Assets | R-06 | RI-05 (uses as input) | Phase 4 |
| R-15 Build Voxel | R-01 | R-16 (synthesis) | — (historical) |
| R-16 Comparative | All others | R-17 (review) | Architecture |
| R-17 Risk | R-16 | R-18 (input) | Meta |
| R-18 Synthesis | R-17 | — | All phases |
| RI-01 Precompute | R-02, R-05 | Phase 2 exec | Phase 2 |
| RI-02 Job Queue | R-09 | Phase 3 exec | Phase 3 |
| RI-03 Plugin Loader | R-07 | Phase 3 exec | Phase 3 |
| RI-04 WAD Handler | R-06 | Phase 4 exec | Phase 4 |
| RI-05 Stack Bundler | R-06, R-14 | Phase 4 exec | Phase 4 |

---

## Study Session Checklist (Print & Use Weekly)

### Week 1 Checklist

```
WEEK 1: PHILOSOPHY & FOUNDATIONS (June 2–8)

□ MONDAY (2–3 hrs)
  □ Read Gabriel "Worse is Better" (30 min)
  □ Extract 3–5 key principles (30 min)
  □ Extract R-01 draft outline (15 min)
  □ Extract Romero 10 principles checklist (15 min)

□ TUESDAY (2 hrs)
  □ Read Romero interview transcript (1 hr)
  □ Read Carmack .plan entries (1996–1998) (45 min)
  □ Complete R-01 draft (15 min)

□ WEDNESDAY (2 hrs)
  □ Read Abrash Black Book Doom chapters (Sec 4: BSP, Sec 5: Rendering) (2 hrs)
  □ Extract BSP pattern outline for R-02 (30 min — embedded)

□ THURSDAY (2 hrs)
  □ Read Fabien Sanglard Doom Retrospective (45 min)
  □ Extract Doom memory strategy for R-03 (45 min)
  □ Outline R-04 Quake architecture (30 min)

□ FRIDAY (2 hrs)
  □ Read Sanglard Quake Retrospective (1 hr)
  □ Skim Quake source orientation (30 min)
  □ Extract R-04 draft outline (30 min)

□ SATURDAY (1.5 hrs)
  □ Review R-01, R-02, R-03, R-04 drafts (45 min)
  □ Write Week 1 synthesis in Doom Guy soul.yaml (45 min)

WEEK 1 DELIVERABLES:
  ✅ R-01: Philosophy Principles (complete)
  ✅ R-02: Doom BSP outline + draft (complete)
  ✅ R-03: Doom Memory outline + draft (complete)
  ✅ R-04: Quake Architecture outline + draft (complete)
  ✅ Week 1 soul.yaml entry (L1, L2, L3 format)
```

### Weekly Time Tracking Template

```
DAILY LOG TEMPLATE (use in study journal)

Date: YYYY-MM-DD
Study Duration: X hours
Session: [Title]

Materials Used:
- [Book/Code/Tool] — X pages/lines read

Extractions Completed:
- [Pattern name] — file:line + benefit + Omega translation

R-Docs Produced:
- R-## title

Blockers/Questions:
- [Any issues or unknowns?]

Next Session:
- [What to start with]

Soul.yaml Notes (weekly):
- L1: [What happened]
- L2: [What does it mean]
- L3: [Universal principle]
```

---

## Quick Rescue Commands (If Study Gets Stuck)

### If You Can't Find Source Code

```bash
# Doom
wget https://github.com/id-Software/DOOM/archive/refs/heads/master.zip

# Quake
wget https://github.com/id-Software/Quake/archive/refs/heads/master.zip

# Quake II
wget https://github.com/id-Software/Quake-2/archive/refs/heads/master.zip

# Doom 3
wget https://github.com/TTimo/doom3.gpl/archive/refs/heads/master.zip

# Half-Life (GoldSrc)
wget https://github.com/ValveSoftware/halflife/archive/refs/heads/master.zip
```

### If Abrash Black Book is Inaccessible

Fallback resources:
1. Fabien Sanglard's site (fabiensanglard.net) — free retrospectives
2. Charles Boury's GitHub — detailed technical breakdowns
3. Wikipedia Doom engine article — high-level overview
4. DoomWiki technical documentation

### If You Get Analysis Paralysis (Too Many Patterns)

**Rule**: Focus on 5 core patterns ONLY. Everything else is "nice to know."

**Core 5**:
1. Precomputation (Doom BSP)
2. Modularity (Quake II plugins)
3. I/O & Events (Source engine)
4. Bundling (IWAD/PWAD + asset packs)
5. Threading & Resource Protection (Doom 3 job system)

Skip: Renderer math, network hacks, platform-specific code, scripting language syntax.

### If You Run Behind Schedule

**Priority salvage order**:
1. Keep R-01 (Philosophy) — MUST COMPLETE
2. Keep R-05, R-06, R-07, R-09 (core patterns) — MUST COMPLETE
3. Defer R-11–R-15 (comparative engines) — can be 2-hour summaries
4. Defer RI-02–RI-05 (complex implementations) — keep RI-01 (highest ROI)
5. Combine R-17 + R-18 into single "Risk & Roadmap" document

**Salvage timeline**: ~30 hours minimum (can extend R-doc production from 18 to 10, keep RI-01 only).

---

## Phase 2–4 Implementation Readiness Checklist

**After Week 4 complete, verify**:

- [ ] All 18 R-docs in `docs/research/R_ID_*`
- [ ] All 5 RI skeletons in `src/omega/` (pseudocode comments visible)
- [ ] R-18 includes full Omega Phase 2–4 roadmap
- [ ] Doom Guy soul.yaml updated with weekly L1→L2→L3 entries
- [ ] No dead-end studies (all research is actionable)
- [ ] Risk register identifies 3–5 complexity traps
- [ ] Implementation team can execute Phase 2 without questions

---

⬡ OMEGA ⬡ DOOM_GUY ⬡ quick-ref ⬡ EXTRACTION-MATRIX-COMPLETE

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: quick-ref | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
