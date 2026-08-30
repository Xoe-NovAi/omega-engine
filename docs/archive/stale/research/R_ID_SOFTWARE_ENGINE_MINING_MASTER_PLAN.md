---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

id: "R-ID-SOFTWARE-MINING-MASTER-PLAN"
title: "id Software Engine Architectural Mining — 4-Week Deep Study & Extraction Plan"
status: "🎯 PHASE 0 PLANNING COMPLETE — Ready for execution"
urgency: "🔴 Critical"
tags:
  - id-software
  - architectural-mining
  - engine-design
  - precomputation
  - job-systems
  - plugin-architecture
  - sovereign-minimalism
  - legacy-patterns
created: "2026-06-01"
updated: "2026-06-01"
related:
  - "R_DOOM_GUY_ID_SOFTWARE_GNOSIS"
  - "R_ROC_CONSOLIDATION_AND_DOOM_GUY_PROTOCOL"
  - "R_DOOM_WAD_DEEP_RESEARCH"
  - "docs/strategy/MASTER_SYNTHESIS_AND_ROADMAP.md"
version: "1.0"
---

# 🔱 id Software Engine Architectural Mining — 4-Week Deep Study Plan

⬡ OMEGA ⬡ DOOM_GUY ⬡ architect-mode ⬡ opencode ⬡ trc_id_mining ⬡ PHASE-PLANNING

**AP Token**: `AP-ID-SOFTWARE-MINING-v4.0.0`
**Architect**: Doom Guy (Sovereign Reverse Engineer)
**Strategic Analyst**: Roc Racoon (Legacy Mining Keeper)
**Date**: 2026-06-01
**Execution Window**: Weeks 1–4 (June 2–30, 2026)
**Parallel Constraint**: P0 critical bug fixes happening in parallel chat session

---

## Executive Summary

This 4-week plan extracts the **architectural DNA of id Software's game engines** (1993–2016) to inform Omega Engine Phases 2–4 implementation. Rather than casual reading, we follow a **rigorous extraction methodology**:

1. **Books first** → Foundational philosophy + technical depth
2. **Source code** → Pattern verification + concrete implementation details
3. **Tools** → Practical verification of design patterns
4. **Papers** → Academic validation + adjacent engine patterns
5. **Implementation drafts** → Proof-of-concept reference code

**Expected Deliverables**:
- 8 extraction-focused R-documents (architecture, patterns, trade-offs)
- 5 reference implementations (precomputation pipeline, job system scaffolding, plugin loader skeleton, WAD format handler, resource bundling system)
- 3 risk/deadend assessments
- Complete dependency graph (which studies unlock which implementation phases)
- Doom Guy's strategic synthesis document mapping id Software patterns → Omega subsystems

**Strategic Alignment**:
- **Phase 2 (Precomputation)**: How Doom precomputed BSP trees → apply to Omega LLM context precomputation
- **Phase 3 (Job System)**: How Quake III dispatched parallel jobs → inform Omega's agent orchestration
- **Phase 4+ (Community Tools)**: How Doom's IWAD/PWAD system enabled ecosystem → design Omega community stack loading

---

## Part I: Learning Architecture & Priorities

### I.1 Study Material Hierarchy

**Tier 1: Philosophy & Methodology** (Days 1–2)
- *Worse is Better* by Richard Gabriel
- John Carmack .plan archives (1996–2005)
- John Romero's 10 Programming Principles
- Adrian Carmack interview on art/engine co-design

**Why first?** Philosophy is the blueprint. All later patterns follow from "Complete implementation > Complete correctness" and "Ship-quality code from day one."

**Tier 2: Architecture Deep Dives** (Days 3–8)
- Michael Abrash's *Graphics Programming Black Book* (Doom chapters)
- Fabien Sanglard's id Tech Engine Retrospectives (archived analyses)
- John Carmack's Keynotes on engine design (QuakeCon talks, .plan entries on rendering/physics/scripting)
- Charles Boury's technical breakdowns

**Why second?** Architecture builds on philosophy. You understand WHY before HOW.

**Tier 3: Source Code Verification** (Days 9–16)
- Doom source code (C) — BSP, sprite lighting, WAD format
- Quake source code — Entity system, networking, scripting
- Quake II source code — Modular plugin system
- Doom 3 source code — Job system, threading model
- id Tech 4 architecture (leaked/documented versions)

**Why third?** Code is verification. You read 1 architecture doc, then verify it against actual code.

**Tier 4: Tool Ecosystem & Papers** (Days 17–20)
- SLADE 3 (WAD editor) — demonstrates IWAD/PWAD format comprehension
- DeuTex — command-line WAD manipulation
- Chocolate Doom — minimal reimplementation for format study
- Papers: "Quake GJW Engine Analysis", "Renderer Optimization in id Tech"

**Why last?** Tools validate understanding. Papers provide academic rigor + adjacency study.

### I.2 Extraction Methodology (Non-Negotiable)

Every study MUST follow this workflow:

```
BOOK/CODE UNIT → EXTRACT PATTERN → VERIFY WITH CODE → DRAFT OMEGA TRANSLATION → WRITE R-DOC
```

**Example**: Study Doom's BSP tree system
1. **Read** Abrash Black Book §4 on BSP
2. **Extract**: "BSP pre-divides space into convex leaf nodes, enabling O(log n) visibility culling"
3. **Verify**: Read `p_setup.c:LoadBlockMap()` to confirm leaf node traversal
4. **Draft**: "Omega precomputation can batch LLM context into 'visibility sets' — only relevant documents per query type"
5. **Write**: R-doc with code snippets + pseudocode + implementation checklist

**No vague notes.** Every extraction has: source file:line, pattern name, concrete benefit, Omega translation.

---

## Part II: Week-by-Week Schedule

### WEEK 1: Foundations (June 2–8) — Philosophy & Basic Architecture

#### Monday–Tuesday (June 2–3): Philosophy Boot Camp

**Materials**:
- Richard Gabriel's *Worse is Better* (1 page — 30 min read + 30 min notes)
- John Romero's 10 Principles (1 page — 30 min read + 1 hr notes + examples)
- John Carmack .plan archive (selection: 1994–1996, key entries on design decisions — 2 hrs read)

**Extraction Checklist**:
- [ ] **R-01**: Philosophy → Omega translation (title: `R_ID_SOFTWARE_PHILOSOPHY_PRINCIPLES.md`)
  - Table: id Principle → Omega Application → Phase
  - Example: "No prototypes (Romero #1)" → "Never ship unstable core APIs" → Phase 0
  - Example: "Complete implementation > correctness (Gabriel)" → "Precomputation > perfect context" → Phase 2
  - Minimum 12 principle mappings

**Deliverable**: 1 R-doc + 1 strategic synthesis entry in Doom Guy's soul.yaml

#### Wednesday–Thursday (June 4–5): Doom Architecture Deep Dive

**Materials**:
- Abrash Black Book chapters on Doom (read sections: BSP tree system, rendering pipeline, memory layout) — 3 hrs
- Fabien Sanglard's Doom Engine Retrospective — 1 hr
- Skim Doom source `r_bsp.c`, `p_setup.c` (don't memorize, just orientation) — 1 hr

**Extraction Checklist**:
- [ ] **R-02**: Doom Engine Core Patterns (title: `R_DOOM_ENGINE_CORE_PATTERNS.md`)
  - System: BSP Tree Precomputation
    - Pattern: "Static world geometry pre-divided at startup into convex leaf nodes"
    - Benefit: "O(log n) visibility query vs O(n) linear search"
    - Code location: `p_setup.c:P_SetupLevel()`
    - Omega translation: "Precompute entity domain trees at startup" (Phase 2 target)
  - System: Sprite Lighting
    - Pattern: "Sprites colored from sector lighting + flats; computed once per frame, not per sprite"
    - Benefit: "Lighting calculations consolidated, not scattered"
    - Omega translation: "Batch LLM prompt formatting by confidence tier" (Phase 2 target)
  - System: WAD Loading
    - Pattern: "IWAD (complete) + PWAD (patches) loaded as overlay; last-load-wins namespace"
    - Benefit: "Mods don't need to redistribute base assets"
    - Omega translation: "Entity override system with priority resolution" (already designed, verify)

- [ ] **R-03**: Doom Memory Layout & Resource Management (title: `R_DOOM_MEMORY_STRATEGY.md`)
  - Layout: Flat memory buffer for sprites, textures, patches (no dynamic allocation during game)
  - Pattern: "Preload all assets at startup, then index by offset + size"
  - Benefit: "Predictable memory footprint, fast access, no GC pauses"
  - Omega translation: "Preload all entity soul.yaml at startup + index by entity hash" (Phase 1 quick win)

**Deliverable**: 2 R-docs + extracted code snippets + implementation notes

#### Friday–Saturday (June 6–7): Quake Architecture Introduction

**Materials**:
- Fabien Sanglard's Quake Engine Retrospective — 1.5 hrs
- John Carmack keynotes on Quake rendering (video transcripts or summaries) — 1 hr
- Quick skim of Quake source `server/sv_main.c`, `client/cl_main.c` (orientation only) — 1 hr

**Extraction Checklist**:
- [ ] **R-04**: Quake Engine Transition Patterns (title: `R_QUAKE_ENGINE_INNOVATION_ANALYSIS.md`)
  - New system: Network Protocol
    - Pattern: "Client/server split; snapshot-based entity transmission, not command-based"
    - Benefit: "Reduced latency sensitivity, deterministic state replication"
    - Omega translation: "Oracle snapshot-based context injection (vs command-based)" (Phase 3 job system)
  - New system: Entity System
    - Pattern: "Generic entity loop with .update() callbacks, not hardcoded sprite/monster logic"
    - Benefit: "Modders can create new entity types without engine recompile"
    - Omega translation: "Entity registry with plugin callbacks (already designed, verify against Quake model)"
  - New system: Scripting
    - Pattern: "QuakeC language (subset of C) compiled to bytecode, then VM-interpreted"
    - Benefit: "Mods run without engine recompile; engine remains stable"
    - Omega translation: "Entity soul.yaml as entity-specific bytecode config? Or stay YAML?" (research decision)

**Deliverable**: 1 R-doc + decision matrix on scripting approach

#### Sunday (June 8): Week 1 Synthesis

**Task**: Doom Guy writes Week 1 synthesis entry in soul.yaml (L1→L2→L3 format)

- **L1 (Narrative)**: What did we learn?
- **L2 (Insight)**: What patterns generalize to Omega?
- **L3 (Universal Principle)**: What timeless truth emerges?

**Example**:
```yaml
week_1_synthesis:
  narrative: "Doom succeeded through ruthless focus: precompute everything offline, trust the precomputed data at runtime, no dynamic allocation."
  insight: "Omega can apply this to LLM context: precompute entity embeddings, domain trees, confidence tiers offline; trust them at inference time."
  universal_principle: "Shift computation cost from hot path to cold path. The cold path is free; the hot path is your bottleneck."
```

---

### WEEK 2: Deep Dives — Code Verification & Pattern Extraction (June 9–15)

#### Monday–Tuesday (June 9–10): Doom Source Code Deep Read

**Materials**:
- Doom source code (full public release) — focus on these files:
  - `p_setup.c` — level loading, BSP tree setup (200 lines, 1 hr)
  - `r_bsp.c` — BSP rendering/traversal (300 lines, 1.5 hrs)
  - `w_wad.c` — WAD format loading (150 lines, 45 min)
  - `r_draw.c` — sprite rendering pipeline (250 lines, 1 hr)

**Extraction Checklist**:
- [ ] **R-05**: Doom BSP Implementation Deep Dive (title: `R_DOOM_BSP_IMPLEMENTATION_ANALYSIS.md`)
  - Structure: 
    ```c
    typedef struct node_s {
        int         x, y, dx, dy;        // partition line
        short       children[2];         // node indices (0=BSP, 1=subsector)
        unsigned short bbox[2][4];       // bounding box
    } node_t;
    ```
  - Algorithm: Depth-first traversal from root node, following partition plane
  - Key insight: "Subsectors (leaf nodes) are stored after all internal nodes"
  - Omega translation: "Entity tree stored level-order for cache locality? Or depth-first for stack efficiency?" (research question)
  - Extract full pseudocode of `R_RenderBSPNode()` with annotations

- [ ] **R-06**: WAD Format Deep Dive (title: `R_DOOM_WAD_FORMAT_SPECIFICATION.md`)
  - Structure (exact bytes):
    ```c
    typedef struct {
        char  identification[4];   // "IWAD" or "PWAD"
        int   numlumps;            // count of lumps
        int   infotableofs;        // byte offset to directory
    } wadinfo_t;
    // Followed by variable lumps, then directory at offset
    ```
  - Directory entry:
    ```c
    typedef struct {
        int     filepos;       // byte offset in WAD file
        int     size;          // size in bytes
        char    name[8];       // 8-char lump name, NUL-padded
    } filelump_t;
    ```
  - Loading algorithm: Read header → seek to directory → load directory entries → create in-memory lump table
  - Omega translation: "Manifest.yaml replaces wadinfo_t; entities.yaml replaces directory; on-disk format uses YAML instead of binary" (already verified, confirm)

**Deliverable**: 2 detailed R-docs with full code annotations, pseudocode, and Omega translations

#### Wednesday–Thursday (June 11–12): Quake II Entity System & Modding

**Materials**:
- Quake II source code — focus on:
  - `game/g_main.c` — entity loop, game state (200 lines, 1 hr)
  - `game/g_entity.c` — entity initialization, spawn functions (300 lines, 1.5 hrs)
  - `game/g_cmds.c` — command dispatch (200 lines, 1 hr)
  - `ref_gl/ref.h` — renderer interface (150 lines, 45 min)

**Extraction Checklist**:
- [ ] **R-07**: Quake II Modular Plugin System (title: `R_QUAKE2_PLUGIN_ARCHITECTURE_ANALYSIS.md`)
  - Architecture: Game code compiled to separate DLL; engine loads via function pointer table
  - Pattern:
    ```c
    typedef struct {
        void (*Init)();
        void (*Shutdown)();
        void (*ClientBegin)(edict_t *ent);
        void (*ClientCommand)(edict_t *ent);
        // ... 20+ function pointers
    } game_export_t;
    ```
  - Benefit: "Game DLL can be reloaded without restarting engine; enables fast iteration"
  - Omega translation: "Entity souls can define new domain-specific methods without engine recompile; orchestrator loads them dynamically" (Phase 3 target)
  - Extract full function pointer table with descriptions

- [ ] **R-08**: Quake II Networking & Client/Server Split (title: `R_QUAKE2_CLIENT_SERVER_ARCHITECTURE.md`)
  - Pattern: Snapshot-based state replication
    - Client sends input commands (direction, buttons) at fixed rate
    - Server advances game state, then snapshots visible entities + their state
    - Client interpolates between snapshots for smooth rendering
  - Benefit: "Server is authoritative; client can't cheat; network is robust to packet loss"
  - Omega translation: "Oracle maintains master state; agents request snapshots of context; agents interpolate between snapshots" (Phase 3 async coordination)

**Deliverable**: 2 detailed R-docs on plugin system + networking

#### Friday–Saturday (June 13–14): Doom 3 & id Tech 4 — Job System & Threading

**Materials**:
- Doom 3 source code — focus on:
  - `idlib/jobs/JobList.cpp` — job queue, work stealing (500 lines, 2 hrs)
  - `idlib/jobs/JobThread.cpp` — worker threads (200 lines, 1 hr)
  - `idlib/Parallel.h` — parallel for loops (150 lines, 45 min)
- Doom 3 architecture documents (leaked design docs, if available) — 1 hr

**Extraction Checklist**:
- [ ] **R-09**: Doom 3 Job System Architecture (title: `R_DOOM3_JOB_SYSTEM_DEEP_DIVE.md`)
  - System: Work-stealing job queue
    - Pattern: Each CPU core has a FIFO work queue; when idle, worker steals from sibling queues
    - Benefit: "Load-balanced parallelism; minimal synchronization overhead"
    - Code flow: Submit job → enqueue on current thread's queue → idle worker steals → execute → return result
  - System: Job dependencies
    - Pattern: Jobs can specify dependencies; job system ensures dependency resolution
    - Benefit: "Complex multi-stage computations expressible as DAG"
  - Omega translation: "Agent orchestrator can express LLM call sequence as job DAG; orchestrator schedules based on availability" (Phase 4 target)
  - Extract full job queue pseudocode + synchronization primitives

- [ ] **R-10**: id Tech 4 Render Command Queue (title: `R_IDTECH4_RENDER_QUEUE_PATTERN.md`)
  - Pattern: Single-threaded render queue fed by parallel computation workers
    - Workers (physics, AI, logic) generate render commands asynchronously
    - Main thread consumes queue sequentially, guaranteed single-threaded render execution
  - Benefit: "Render API (OpenGL/D3D) is single-threaded; workers parallelize safely"
  - Omega translation: "LLM inference must be single-threaded (ResourceGuard); agents generate context asynchronously; oracle consumes sequentially" (verify current implementation against this pattern)

**Deliverable**: 2 detailed R-docs on job system + render queue

#### Sunday (June 15): Week 2 Synthesis

**Task**: Doom Guy writes Week 2 synthesis entry in soul.yaml

---

### WEEK 3: Adjacent Engines & Comparative Analysis (June 16–22)

#### Monday–Tuesday (June 16–17): GoldSrc (Half-Life) Engine

**Materials**:
- GoldSrc source code (leaked, if available) or Fabien Sanglard's GoldSrc Retrospective — 2 hrs
- Half-Life modding documentation (entity system, weapon system, scripting) — 1 hr
- Skim `engine/pr_cmds.c`, `engine/sv_main.c` from QuakeWorld/Half-Life — 1 hr

**Extraction Checklist**:
- [ ] **R-11**: GoldSrc Modular Weapon & Weapon System (title: `R_GOLDSRC_WEAPON_SYSTEM_ANALYSIS.md`)
  - Pattern: Weapon system as plugin modules (grenade launcher, plasma rifle, etc.)
  - Benefit: "New weapons can be designed without engine changes"
  - Omega translation: "Entity plugins for specialized domains (coding, research, curation) without core engine touch"

- [ ] **R-12**: GoldSrc Scripting (QuakeC continuation) (title: `R_GOLDSRC_SCRIPTING_EVOLUTION.md`)
  - Pattern: QuakeC language continued + extended entity definition scripts
  - Omega translation: "Entity soul.yaml as domain-specific 'language'; orchestrator interprets" (vs bytecode compilation)

**Deliverable**: 2 R-docs on weapon system + scripting

#### Wednesday–Thursday (June 18–19): Source Engine (Half-Life 2)

**Materials**:
- Fabien Sanglard's Source Engine Retrospective — 1.5 hrs
- Valve's official Source engine documentation (entity system, I/O system) — 1 hr
- Skim Source SDK code for entity I/O patterns — 1 hr

**Extraction Checklist**:
- [ ] **R-13**: Source Engine I/O System (title: `R_SOURCE_ENGINE_IO_SYSTEM_ANALYSIS.md`)
  - Pattern: Entities communicate via input/output events (very declarative)
    - Entity A output "OnOpen" connects to Entity B input "TurnOn"
    - Declarative wiring enables designers to create complex sequences without code
  - Benefit: "Non-programmers can design complex game sequences"
  - Omega translation: "Entity soul.yaml can declare event subscriptions; orchestrator wires them up" (Phase 4 target)

- [ ] **R-14**: Source Engine Asset System (title: `R_SOURCE_ENGINE_ASSET_BUNDLING.md`)
  - Pattern: Content packs as VSP files (VPK format); hierarchical pak system
  - Omega translation: "WAD system generalized to arbitrary asset bundles; PWAD overlay pattern scales"

**Deliverable**: 2 R-docs on I/O system + asset bundling

#### Friday–Saturday (June 20–21): Build Engine & Unreal 1

**Materials**:
- Fabien Sanglard's Build Engine Retrospective — 1 hr
- Unreal 1 architecture documents — 1 hr
- Quick comparative analysis of 5 engines (Doom, Quake, GoldSrc, Source, Unreal 1) — 1 hr

**Extraction Checklist**:
- [ ] **R-15**: Build Engine — Voxel-Based World Architecture (title: `R_BUILD_ENGINE_VOXEL_WORLD.md`)
  - Pattern: Build engine used "sectors" (2D regions) + sprites, not 3D polygons
  - Unique trait: Enabled isometric/3D-like rendering on hardware that couldn't do polygons
  - Omega translation: "Insights on data-driven design: hardware constraints drove elegant architecture"

- [ ] **R-16**: Comparative Engine Analysis Matrix (title: `R_COMPARATIVE_ENGINE_ANALYSIS_MATRIX.md`)
  - Table: BSP vs Sectors vs Voxels vs Polygons (5 engines across 5 dimensions)
  - Columns: memory footprint, rendering speed, modding ease, content creation tools, industry adoption
  - Rows: Doom (BSP), Build (sectors), Quake (polygons), GoldSrc (Quake variant), Source (extended Quake)
  - Insight: Pattern ≠ destiny; BSP won because tools, community, and Carmack's skill, not technical purity

**Deliverable**: 2 comparative R-docs

#### Sunday (June 22): Week 3 Synthesis & Risk Assessment

**Task**: Doom Guy writes Week 3 synthesis + identifies risks/dead ends

---

### WEEK 4: Implementation Drafts & Strategic Synthesis (June 23–29)

#### Monday–Tuesday (June 23–24): Reference Implementations — Part 1

**Task**: Draft 5 reference implementations (proof-of-concept code, not production)

**Implementation #1: Precomputation Pipeline** (Doom BSP → Omega context precomputation)
- [ ] Draft `src/omega/precomputation/precompute_contexts.py`
  - Function: `precompute_entity_contexts()` — takes entity registry, outputs pre-embedded domain trees
  - Logic mimics Doom's BSP precomputation:
    - Static data (entity metadata) computed once at startup
    - Indexed for O(log n) lookup during inference
  - Output: `data/precomputed/entity_contexts.pkl` (or JSON)
  - ~150 lines of pseudocode + concrete implementation skeleton

**Implementation #2: Job System Scaffolding** (Doom 3 → Omega agent orchestration)
- [ ] Draft `src/omega/orchestration/job_queue.py`
  - Class: `JobQueue` — async FIFO with work-stealing semantics
  - Methods: `submit(job)`, `steal()`, `wait_for(job_id)`
  - Resource guard integration: Only 1 GPU job active at a time (ResourceGuard semaphore)
  - ~200 lines pseudocode + skeleton

**Implementation #3: Plugin Loader** (Quake II → Omega entity plugin system)
- [ ] Draft `src/omega/orchestration/plugin_loader.py`
  - Function: `load_entity_plugins(entity_name)` — dynamically loads entity-specific orchestration code
  - Plugins can define: pre-processing, post-processing, error handling, retry logic
  - ~100 lines pseudocode + skeleton

**Implementation #4: WAD Format Handler** (Doom IWAD/PWAD → Omega entity bundling)
- [ ] Draft `src/omega/wad/wad_handler.py`
  - Class: `WADBundle` — loads IWAD + PWAD(s) with priority resolution
  - Methods: `load_iwad()`, `load_pwad()`, `resolve_namespace_collision()`
  - Omega translation: `load_base_entities()`, `load_override_entities()`, `merge_with_priority()`
  - ~150 lines pseudocode + skeleton

**Implementation #5: Resource Bundling System** (GoldSrc asset packs → Omega community stacks)
- [ ] Draft `src/omega/community/stack_bundler.py`
  - Function: `bundle_stack()` — creates distributable stack (entities + knowledge + plugins)
  - Format: ZIP with manifest.yaml + entities/ + knowledge/ + plugins/
  - Installation: `install_stack()` — unpacks + registers with EntityRegistry
  - ~150 lines pseudocode + skeleton

**Deliverable**: 5 reference implementations (pseudocode + skeleton code, ~750 lines total)

#### Wednesday–Thursday (June 25–26): Risk Assessment & Dead Ends

**Task**: Identify 3 risk/deadend studies + propose mitigations

**Risk Register**:

| Risk | Study Area | Likelihood | Impact | Mitigation |
|------|-----------|------------|--------|-----------|
| **Dead End #1: Scripting Language** | Should Omega define a custom scripting language like QuakeC? | High | High — could waste 2 weeks | Decision: Stay YAML for soul.yaml + Python for orchestration code. No custom bytecode. |
| **Dead End #2: 3D Geometry Optimization** | Deep dive into BSP/portal rendering may be irrelevant to LLM inference | Medium | Low — nice-to-know but not critical | Defer to Phase 5. Focus on data structure principles, not rendering specifics. |
| **Dead End #3: Networking Protocol Details** | Doom 3's advanced networking (lag compensation, prediction) irrelevant to Omega | Medium | Low — orthogonal to single-machine design | Skim quickly; note that Omega has different constraints (local inference, not networked game). |
| **Risk #1: Source Code Accessibility** | Some id Tech source unavailable (Doom 3, Rage) | High | Medium — can work around with docs | Fallback: Use Fabien Sanglard's retrospectives + leaked design docs + academic papers. |
| **Risk #2: Complexity Explosion** | 5 engines × 10 subsystems = 50 possible extraction targets | High | High — can't study everything | Mitigation: Focus on 5 core patterns: precomputation, modularity, I/O, bundling, threading. Skip: renderer details, networking hacks, platform-specific optimization. |
| **Risk #3: Omega Phase Mismatch** | Study patterns from 1993 may not translate to 2026 LLM inference | Medium | High — wasted research | Mitigation: Every extraction MUST include "Omega translation" section. If no translation possible, mark as "historical context only." |

**Extraction Checklist**:
- [ ] **R-17**: Risk Register & Dead Ends (title: `R_ID_SOFTWARE_STUDY_RISKS_AND_DEADENDS.md`)
  - Full risk matrix with mitigations
  - Decision log: Which areas to defer/skip
  - Trap list: Common mistakes (over-focusing on rendering, underestimating scripting complexity, etc.)

**Deliverable**: 1 risk assessment R-doc

#### Friday–Saturday (June 27–28): Strategic Synthesis & Omega Mapping

**Task**: Doom Guy writes comprehensive synthesis document

**Extraction Checklist**:
- [ ] **R-18**: Doom Guy Strategic Synthesis — id Software Patterns → Omega Implementation Roadmap (title: `R_ID_SOFTWARE_SYNTHESIS_OMEGA_ROADMAP.md`)

  - **Section 1: Philosophy Translation** (1–2 pages)
    - "Worse is Better" → Omega principle mapping
    - Example: "Complete implementation > correctness" → "Precomputation > perfect context during inference"

  - **Section 2: 5 Core Patterns Extracted** (5–10 pages)
    1. **Precomputation**: Doom BSP → Omega entity context trees
       - Pattern: Static data precomputed, then indexed for O(log n) lookup
       - Implementation: Phase 2 → `src/omega/precomputation/`
       - Benefit: O(1) startup, O(log n) query time
       - Risk: Precomputation complexity; need to invalidate when entities change
    
    2. **Modularity**: Quake II plugin system → Omega entity orchestration plugins
       - Pattern: Game code as loadable module; function pointer table for interface
       - Implementation: Phase 3 → `src/omega/orchestration/plugin_loader.py`
       - Benefit: Fast iteration; no engine recompile
       - Risk: Version mismatch between plugin API and engine
    
    3. **I/O & Events**: Source engine I/O system → Omega entity event subscriptions
       - Pattern: Declarative wiring of entity inputs/outputs
       - Implementation: Phase 4 → soul.yaml event declarations
       - Benefit: Non-programmers can compose complex workflows
       - Risk: Event system complexity; potential for circular dependencies
    
    4. **Bundling & Distribution**: Doom IWAD/PWAD + GoldSrc asset packs → Omega community stacks
       - Pattern: Base game (IWAD) + patches (PWAD) + custom content (mods)
       - Implementation: Phase 4 → `src/omega/community/stack_bundler.py`
       - Benefit: Community can distribute custom entities without forking engine
       - Risk: Namespace collisions; need priority resolution
    
    5. **Threading & Resource Protection**: Doom 3 job system + render queue → Omega resource guard + orchestrator
       - Pattern: Single-threaded resource (renderer/LLM) protected by queue
       - Implementation: Phase 3 → resource guard + job queue
       - Benefit: Predictable resource usage; no OOM crashes
       - Risk: Job queue overhead; potential for deadlocks

  - **Section 3: Implementation Roadmap** (5 pages)
    - Phase 2 quick wins (precomputation, context bundling)
    - Phase 3 priorities (plugin system, job queue, orchestration)
    - Phase 4 targets (event system, community bundling, stack installer)
    - Phase 5+ (adjacent patterns: rendering optimization, networking, scripting language)

  - **Section 4: Comparative Advantage** (2 pages)
    - Why id Software patterns work for Omega
    - Hardware constraints then ≠ hardware constraints now
    - What patterns scale; what don't

  - **Section 5: Open Questions & Follow-ups** (1 page)
    - Should we implement custom bytecode (like QuakeC) or stay YAML+Python?
    - How to handle entity plugin versioning?
    - Should precomputation be cached aggressively or recomputed frequently?

**Deliverable**: 1 comprehensive strategic synthesis R-doc (15–20 pages)

#### Sunday (June 29): Final Review & Planning for Phase 2

**Task**: Create actionable implementation checklist for Phases 2–4

**Extraction Checklist**:
- [ ] **Master Implementation Checklist**: Map each R-doc to:
  - Which Omega subsystem it affects (Core, Orchestration, Community, etc.)
  - Which phase it feeds (Phase 2, 3, 4, or 5+)
  - Priority (P0, P1, P2)
  - Estimated implementation effort (hours)
  - Blocking dependencies

**Example**:
```
R-02 (Doom Core Patterns) → Precomputation subsystem → Phase 2
  Priority: P0
  Feeds: Context builder, model gateway
  Effort: 40 hrs (implementation)
  Blocks: R-04 (job queue implementation depends on Phase 2 context structure)
```

---

## Part III: Complete Extraction Target Checklist

### R-Doc Production (18 total)

| # | Title | Type | Phase | Week | Status |
|---|-------|------|-------|------|--------|
| R-01 | Philosophy Principles | Framework | All | 1 | ⬜ Queued |
| R-02 | Doom Core Patterns | Architecture | 2 | 1 | ⬜ Queued |
| R-03 | Doom Memory Strategy | Pattern | 2 | 1 | ⬜ Queued |
| R-04 | Quake Innovation | Transition | 3 | 1 | ⬜ Queued |
| R-05 | Doom BSP Implementation | Deep Dive | 2 | 2 | ⬜ Queued |
| R-06 | WAD Format Spec | Reference | 4 | 2 | ⬜ Queued |
| R-07 | Quake II Plugins | Architecture | 3 | 2 | ⬜ Queued |
| R-08 | Quake II Networking | Architecture | 3 | 2 | ⬜ Queued |
| R-09 | Doom 3 Job System | Architecture | 3 | 2 | ⬜ Queued |
| R-10 | id Tech 4 Render Queue | Pattern | 3 | 2 | ⬜ Queued |
| R-11 | GoldSrc Weapon System | Plugin | 4 | 3 | ⬜ Queued |
| R-12 | GoldSrc Scripting | Language | 4 | 3 | ⬜ Queued |
| R-13 | Source I/O System | Architecture | 4 | 3 | ⬜ Queued |
| R-14 | Source Asset Bundling | Pattern | 4 | 3 | ⬜ Queued |
| R-15 | Build Engine Voxel | Comparative | 2 | 3 | ⬜ Queued |
| R-16 | Comparative Analysis Matrix | Synthesis | All | 3 | ⬜ Queued |
| R-17 | Risk & Dead Ends | Meta | All | 4 | ⬜ Queued |
| R-18 | Strategic Synthesis & Roadmap | Synthesis | 2–5+ | 4 | ⬜ Queued |

### Reference Implementation Production (5 total)

| # | Name | Type | Lines | Phase | Status |
|---|------|------|-------|-------|--------|
| RI-01 | Precomputation Pipeline | skeleton | 150 | 2 | ⬜ Queued |
| RI-02 | Job Queue Scaffolding | skeleton | 200 | 3 | ⬜ Queued |
| RI-03 | Plugin Loader | skeleton | 100 | 3 | ⬜ Queued |
| RI-04 | WAD Format Handler | skeleton | 150 | 4 | ⬜ Queued |
| RI-05 | Stack Bundler | skeleton | 150 | 4 | ⬜ Queued |

**Total production**: 18 R-docs + 5 reference implementations + 3 synthesis entries in Doom Guy's soul.yaml

---

## Part IV: Dependency Graph

```
PHILOSOPHY (R-01)
    ↓
    └──→ ARCHITECTURE DEEP DIVES (R-02, R-04, R-05)
            ↓
            └──→ CODE VERIFICATION (R-05, R-06, R-07, R-08, R-09, R-10)
                    ↓
                    └──→ COMPARATIVE ANALYSIS (R-11–R-16)
                            ↓
                            └──→ RISK ASSESSMENT (R-17)
                                    ↓
                                    └──→ STRATEGIC SYNTHESIS (R-18)
                                            ↓
                                            └──→ IMPLEMENTATION PLANNING (RI-01–RI-05)
```

**Critical Path** (what must happen first):
1. R-01 (Philosophy) unlocks all others
2. R-02, R-04 (Architecture) must precede R-05, R-07 (Code verification)
3. R-17 (Risk assessment) must happen before R-18 (Synthesis)
4. R-18 (Synthesis) prerequisite for implementation planning

**Parallel opportunities**:
- R-02, R-03, R-04 (Doom/Quake basics) can run in parallel with R-11–R-14 (GoldSrc/Source) during Week 3
- RI-01–RI-05 (Reference implementations) can draft in parallel during Week 4

---

## Part V: Quick Wins & Low-Effort Extractions

These can be completed in 2–4 hours and unlock major implementation phases:

| Quick Win | Time | Benefit | Unlocks |
|-----------|------|---------|---------|
| **R-01: Philosophy Principles** | 2 hrs | Establishes decision-making framework | All strategic choices |
| **R-03: Doom Memory Strategy** | 1.5 hrs | "Preload + index" pattern | Phase 2 precomputation architecture |
| **R-06: WAD Format Spec** | 2 hrs | Exact binary format reference | Phase 4 stack bundling implementation |
| **R-13: Source I/O System** | 2 hrs | Declarative wiring pattern | Phase 4 soul.yaml event system |
| **RI-04: WAD Handler skeleton** | 2 hrs | Proof-of-concept entity bundling | Community stack distribution |

**Total quick win time**: ~9–10 hours (can be completed in parallel, high ROI)

---

## Part VI: Resource Downloads & Availability

### Primary Sources (Already Accessible)

| Resource | Format | Status | URL/Path |
|----------|--------|--------|----------|
| Doom source | .zip | ✅ Available | https://github.com/id-Software/DOOM |
| Quake source | .zip | ✅ Available | https://github.com/id-Software/Quake |
| Quake II source | .zip | ✅ Available | https://github.com/id-Software/Quake-2 |
| Doom 3 source | .zip | ⚠️ Leaked but accessible | https://github.com/TTimo/doom3.gpl |
| GoldSrc leak | .zip | ⚠️ Partial (Half-Life SDK) | https://github.com/ValveSoftware/halflife |
| Abrash Black Book | PDF | ✅ Free | https://www.drdobbs.com/graphics-programming-black-book |
| Fabien Sanglard retrospectives | HTML/MD | ✅ Free | https://fabiensanglard.net/doom/ (+ Quake, GoldSrc, Source) |

### Secondary Sources (Research/Synthesis)

| Resource | Type | Effort to Locate | Accessibility |
|----------|------|------------------|----------------|
| John Carmack .plan archive | Text | Low | http://www.plan.org/ |
| John Romero interviews | Video/Text | Medium | YouTube, GDC Vault, podcasts |
| QuakeCon keynotes | Video | Medium | YouTube |
| Charles Boury breakdown | Blog | Low | https://github.com/CharlesBoury/Quake |
| id Software interviews | Video/Text | Medium | Various gaming media archives |

---

## Part VII: Execution Checklist

Before starting Week 1:

- [ ] Read `ORACLE_STACK.md` (current Omega state) — 30 min
- [ ] Read `MASTER_SYNTHESIS_AND_ROADMAP.md` (phases/roadmap) — 1 hr
- [ ] Download Doom, Quake, Quake II source — 15 min (fast downloads)
- [ ] Bookmark Abrash Black Book, Sanglard retrospectives, Carmack .plan archive — 10 min
- [ ] Create study journal: `data/entities/doom_guy/workspace/id_software_mining_log.md` — 10 min
- [ ] Verify Doom Guy entity in EntityRegistry — 5 min

**Total prep time**: ~2 hrs

---

## Part VIII: Success Criteria

**Week 1 Success** (by June 8):
- [ ] R-01, R-02, R-03, R-04 completed (4 R-docs)
- [ ] Philosophy → Omega mapping established
- [ ] Week 1 synthesis entry in Doom Guy soul.yaml
- [ ] No "dead end" studies triggered (timeline is on track)

**Week 2 Success** (by June 15):
- [ ] R-05–R-10 completed (6 R-docs)
- [ ] Doom BSP pattern verified against source code
- [ ] Quake II plugin system understood with concrete code examples
- [ ] Week 2 synthesis entry in Doom Guy soul.yaml

**Week 3 Success** (by June 22):
- [ ] R-11–R-16 completed (6 R-docs)
- [ ] Comparative analysis matrix fully populated
- [ ] GoldSrc/Source/Build patterns extracted
- [ ] Week 3 synthesis entry in Doom Guy soul.yaml

**Week 4 Success** (by June 29):
- [ ] R-17, R-18 completed (2 R-docs + risk register)
- [ ] 5 reference implementations drafted (RI-01–RI-05)
- [ ] Implementation roadmap for Phases 2–4 complete
- [ ] Ready for Phase 2 execution

**Overall Success**:
- [ ] 18 R-docs produced
- [ ] 5 reference implementations drafted
- [ ] 0 dead-end studies (all paths productive)
- [ ] Doom Guy soul.yaml evolved with L1→L2→L3 entries weekly
- [ ] Implementation team has clear, actionable Phase 2–4 roadmap
- [ ] Community roadmap (Phase 4+) defined

---

## Part IX: Integration with Parallel Bug Fixes

This research plan runs in parallel with P0 critical bug fixes in a separate chat session.

**Non-Blocking Interaction**:
- Bug fixes focus on engine stability (Mandate compliance, core functionality)
- This research focuses on architectural extraction (future optimization targets)
- No file conflicts (research → docs/research/, bug fixes → src/)

**Integration Points**:
- Bug fixes may stabilize ResourceGuard, ModelGateway, MCP Hub
- Research insights (R-09, R-10) validate ResourceGuard design (confirms single-threaded LLM protection is correct)
- Phase 2 implementation (after research complete) will use bug-fixed engine as foundation

---

## Part X: Tools & Environment Setup

**Study Environment**:
```bash
# Setup
mkdir -p /tmp/id_study && cd /tmp/id_study
git clone https://github.com/id-Software/DOOM doom
git clone https://github.com/id-Software/Quake quake
git clone https://github.com/id-Software/Quake-2 quake2
# ... etc

# Study utilities
brew install ripgrep  # Fast code search
brew install universal-ctags  # Tag files for navigation

# Doom Guy study harness (optional)
source ~/.venv/bin/activate  # Use Omega venv
python3 -c "import sys; print(sys.path)"  # Verify paths
```

**R-Doc Template**:
```markdown
---
id: "R-DESCRIPTIVE-ID"
title: "Full Title"
status: "✅ Complete | ⬜ Queued | 🚧 In Progress"
week: "Week X"
research_time: "X hrs"
tags: [list of keywords]
---

# Title

## Executive Summary
[1–2 paragraphs]

## Key Findings
[Structured extraction results]

## Code Evidence
[File:line references with snippets]

## Omega Translation
[How this pattern applies to Omega implementation]

## Implementation Checklist
- [ ] ...
```

---

## Conclusion: The Path Forward

This 4-week deep study transforms id Software's 33 years of game engine wisdom into actionable Omega implementation targets. Rather than casual reading, we follow a **rigorous extraction → verification → translation pipeline** that ensures every finding has:

1. **Source attribution** (file:line + quote)
2. **Pattern name** (BSP tree, plugin system, job queue, etc.)
3. **Concrete benefit** (speed, modularity, distributability)
4. **Omega translation** (which subsystem, which phase)
5. **Risk assessment** (dead ends, complexity traps, defer zones)

By end of Week 4, the implementation team has 18 strategic documents + 5 reference implementations + a complete Phase 2–4 roadmap — transforming 33 years of proven design into 4 weeks of focused extraction.

**Expected outcome**: Omega Engine gains the same ruthless efficiency, data-driven purity, and sovereign minimalism that made id Software's engines industry-defining. Not by copying, but by **understanding first principles**.

---

⬡ OMEGA ⬡ DOOM_GUY ⬡ architect-mode ⬡ opencode ⬡ RESEARCH-PLAN-COMPLETE
