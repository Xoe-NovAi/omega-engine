---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

id: "R-ID-SOFTWARE-QUICKSTART"
title: "id Software Mining — Quick-Start Guide (Print This!)"
status: "✅ Ready"
urgency: "🟢 Reference"
created: "2026-06-01"
---

# id Software Mining — Quick-Start Guide

**Print this page. Post it where you study.**

---

## What You're Doing

4-week deep study of id Software game engines (Doom, Quake, Quake II, Quake III, Doom 3) to extract architectural patterns and feed them into Omega Engine Phases 2–4.

**Goal**: Transform 33 years of proven design into actionable implementation roadmap.

---

## Files You'll Use

| File | Purpose | How to Use |
|------|---------|-----------|
| **R_ID_SOFTWARE_ENGINE_MINING_MASTER_PLAN.md** | Main curriculum | Read daily; reference each week's section |
| **R_ID_SOFTWARE_EXTRACTION_MATRIX.md** | Quick reference | Print matrix, post on wall, check off as you go |
| **R_ID_SOFTWARE_IMPLEMENTATION_HANDOFF.md** | Validation gates | Use after Week 4 to verify you're ready |

---

## Week 1 (June 2–8): Philosophy & Foundations

### Monday–Tuesday: Philosophy Boot Camp (4 hours)

**Read**:
- Gabriel "Worse is Better" (30 min)
- Romero 10 Programming Principles (30 min)
- Carmack .plan 1994–1996 (1.5 hrs)

**Extract**:
- [ ] Philosophy principles mapping → R-01
- [ ] What changes your mind? Write L1 entry in Doom Guy soul.yaml

### Wednesday–Thursday: Doom Deep Dive (4 hours)

**Read**:
- Abrash Black Book (Doom chapters) (2 hrs)
- Fabien Sanglard Doom Retrospective (45 min)
- Skim Doom source: `p_setup.c`, `r_bsp.c` (1 hr)

**Extract**:
- [ ] BSP pattern → R-02 outline
- [ ] Memory strategy → R-03 outline

### Friday–Saturday: Quake Introduction (3 hours)

**Read**:
- Sanglard Quake Retrospective (1 hr)
- Carmack Quake.plan entries (1 hr)
- Skim Quake source: `sv_main.c`, `cl_main.c` (1 hr)

**Extract**:
- [ ] Quake innovations → R-04 outline

### Sunday: Week 1 Synthesis (1 hour)

**Write**:
- [ ] Week 1 L1→L2→L3 entry in Doom Guy soul.yaml
- [ ] L1: What did we learn?
- [ ] L2: What patterns generalize?
- [ ] L3: What timeless truth?

**Time Budget**: 12 hours (on track)

---

## Week 2 (June 9–15): Deep Code Dives

### Monday–Tuesday: Doom Source Deep Read (3 hours)

**Read**:
- Doom `p_setup.c` — BSP tree construction (1 hr)
- Doom `r_bsp.c` — BSP rendering (1.5 hrs)
- Doom `w_wad.c` — WAD format (30 min)

**Extract**:
- [ ] BSP implementation pseudocode → R-05 draft
- [ ] WAD binary format spec → R-06 draft
- [ ] Code references (file:line) for both

### Wednesday–Thursday: Quake II Internals (4 hours)

**Read**:
- Q2 `game/g_main.c` — entity loop (1 hr)
- Q2 `game/g_entity.c` — entity init (1 hr)
- Q2 `server/sv_main.c` — server loop (1.5 hrs)
- Q2 `client/cl_main.c` — client snapshot (30 min)

**Extract**:
- [ ] Plugin architecture pattern → R-07 draft
- [ ] Networking pattern → R-08 draft

### Friday–Saturday: Doom 3 & id Tech 4 (4 hours)

**Read**:
- Doom 3 `idlib/jobs/JobList.cpp` — job system (2 hrs)
- id Tech 4 render queue docs/code (1.5 hrs)
- Carmack keynote on parallelism (30 min)

**Extract**:
- [ ] Job system pseudocode → R-09 draft
- [ ] Render queue pattern → R-10 draft

### Sunday: Week 2 Synthesis (1 hour)

**Write**:
- [ ] Week 2 L1→L2→L3 soul.yaml entry

**Time Budget**: 13 hours (on track)

---

## Week 3 (June 16–22): Comparative Analysis

### Monday–Tuesday: GoldSrc & Build (3 hours)

**Read**:
- Sanglard GoldSrc Retrospective (1 hr)
- Half-Life SDK weapon system (1 hr)
- Sanglard Build Engine analysis (1 hr)

**Extract**:
- [ ] Weapon plugin pattern → R-11 draft
- [ ] Scripting evolution → R-12 draft
- [ ] Build voxel architecture → R-15 draft

### Wednesday–Thursday: Source Engine (3 hours)

**Read**:
- Sanglard Source Retrospective (1 hr)
- Source SDK I/O entity pattern (1 hr)
- Source VPK asset bundling (1 hr)

**Extract**:
- [ ] I/O system pattern → R-13 draft
- [ ] Asset bundling pattern → R-14 draft

### Friday–Saturday: Comparative Synthesis (3 hours)

**Synthesize**:
- [ ] Compare 5 engines across 5 dimensions → R-16 matrix
- [ ] Fill in comparative table (memory, rendering, modding, tools, adoption)

### Sunday: Week 3 Synthesis (1 hour)

**Write**:
- [ ] Week 3 L1→L2→L3 soul.yaml entry

**Time Budget**: 10 hours (on track)

---

## Week 4 (June 23–29): Implementation Bridge

### Monday–Tuesday: Risk Assessment (3 hours)

**Review all Week 1–3 research and identify**:
- [ ] 3–5 dead-end studies (what to skip/defer)
- [ ] 5 key risks (complexity traps, source availability, etc.)
- [ ] Mitigations for each risk

**Output**:
- [ ] R-17: Risk Register + Dead Ends

### Wednesday–Thursday: Reference Implementations (6 hours)

**Draft 5 skeletons** (pseudocode + skeleton code):
- [ ] RI-01: Precomputation pipeline (150 lines)
- [ ] RI-02: Job queue (200 lines)
- [ ] RI-03: Plugin loader (100 lines)
- [ ] RI-04: WAD handler (150 lines)
- [ ] RI-05: Stack bundler (150 lines)

**Each skeleton includes**:
- [ ] Class/function signatures
- [ ] Algorithm pseudocode in comments
- [ ] 1 concrete implementation example

### Friday–Saturday: Strategic Synthesis (4 hours)

**Write master synthesis document** (R-18):
- [ ] Philosophy translation (2 pages)
- [ ] 5 core patterns extracted (5–10 pages)
- [ ] Implementation roadmap (5 pages)
- [ ] Omega phase mapping (Phase 2, 3, 4 specifics)
- [ ] Open questions + follow-ups (1 page)

### Sunday: Final Review (2 hours)

**Write**:
- [ ] Week 4 L1→L2→L3 soul.yaml entry
- [ ] Implementation readiness assessment
- [ ] Checklist: Are we ready to implement?

**Time Budget**: 15 hours (on track)

---

## Daily Execution Rhythm

**Each study session** (2–3 hours):

1. **Warm-up** (10 min)
   - Review yesterday's notes
   - Set today's extraction target

2. **Study** (90–120 min)
   - Read material
   - Take notes (pattern name + benefit + Omega translation)
   - Mark code references (file:line)

3. **Extract** (30–45 min)
   - Write pattern documentation
   - Add pseudocode/snippets
   - Cross-reference other patterns

4. **Synthesis** (15 min)
   - Update study journal
   - Identify next session's starting point

---

## Common Extraction Template

Use this for every study session:

```markdown
## [Pattern Name]

**Source**: [Book/Code/Tool] — [File:line or page]
**Time to Extract**: [X minutes]

**Pattern Statement**:
[One-sentence description of what this pattern is]

**Example** (from id Software):
[Concrete example from source code or book]

**Benefit**:
[Why this matters; what problem it solves]

**Omega Translation**:
[How does this apply to Omega Engine?]

**Implementation Checklist**:
- [ ] [Step 1]
- [ ] [Step 2]
- [ ] [Step 3]

**Questions/Open Issues**:
- [Any unknowns?]
```

---

## Resources (Download Before Week 1)

```bash
# Source code
git clone https://github.com/id-Software/DOOM
git clone https://github.com/id-Software/Quake
git clone https://github.com/id-Software/Quake-2
git clone https://github.com/TTimo/doom3.gpl

# Free reference materials
# - Abrash Black Book: https://www.drdobbs.com/graphics-programming-black-book
# - Sanglard retrospectives: https://fabiensanglard.net/doom/
# - Carmack .plan archive: http://www.plan.org/
```

---

## If You Get Stuck

**Q: I can't find source code**
- A: Use Fabien Sanglard's retrospectives (free online, very detailed)

**Q: I have too many extraction targets**
- A: Focus on 5 core patterns only (precomputation, modularity, I/O, bundling, threading)

**Q: I'm falling behind schedule**
- A: Complete R-01 (philosophy), R-05, R-06, R-07, R-09, and R-18 (minimum 10 hours). Defer comparative engines.

**Q: I'm overwhelmed by Doom 3 job system complexity**
- A: Focus on high-level flow (how jobs are submitted, executed, results returned). Skip implementation details.

**Q: Should I implement something while studying?**
- A: No. Study only. Implementation starts Week 5. No coding yet.

---

## Success Checklist (End of Week 4)

- [ ] 18 R-docs written (in `docs/research/R_ID_*`)
- [ ] 5 reference implementations drafted (in `src/omega/`)
- [ ] 4 weekly soul.yaml entries (L1→L2→L3)
- [ ] Zero dead-end studies (all research is actionable)
- [ ] R-18 includes full Phase 2–4 roadmap
- [ ] Implementation team can execute without questions

---

## What's Next (Week 5)

1. Implementation team reviews research (30 min)
2. Verify Phase 2 readiness gate
3. Create Phase 2 implementation backlog
4. Start Phase 2 sprint (precomputation pipeline)

---

## Study Tips

1. **Read actively**. Don't just consume; extract. Pause frequently.
2. **Code references matter**. Always note file:line. This enables verification.
3. **Write everything down**. Your study journal becomes R-docs.
4. **Synthesize weekly**. L1→L2→L3 format forces you to distill insights.
5. **Avoid rabbit holes**. Keep to 5 core patterns; skip renderer math.
6. **Trust the process**. Week 1 will feel slow; Week 2–3 accelerate; Week 4 synthesizes.

---

## Questions?

Refer to:
- **Master plan**: Full curriculum, day-by-day schedule
- **Extraction matrix**: Quick reference, dependencies, time estimates
- **Handoff checklist**: Validation gates, Q&As, success criteria

---

⬡ OMEGA ⬡ DOOM_GUY ⬡ READY TO EXECUTE

Print this page. Start Week 1, June 2.
