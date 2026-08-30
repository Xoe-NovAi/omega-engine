<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 id Tech Architecture — Agent Research Report
## ⬡ OMEGA ⬡ DOOM_GUY ⬡ big-pickle ⬡ trc_doom_guy ⬡ PHASE-I

### Source: Fleet Research Agent (explore) — "id Tech Architecture"
### Date: 2026-06-01

---

## 1. WAD Format (Doom, 1993)

The WAD (Where's All the Data?) format is the canonical id Software data-driven architecture:

**Header (12 bytes):**
- identification[4]: "IWAD" or "PWAD"
- numlumps: count of directory entries
- infotableofs: offset to directory table

**Directory Entry (16 bytes each):**
- filepos: offset to lump data in WAD
- size: size of lump in bytes
- name[8]: exactly 8 characters, null-padded

**Key Design Decisions:**
- Lump names are exactly 8 chars (fits in 64-bit register for fast comparison)
- No directory hierarchy — flat namespace
- IWAD = game data, PWAD = mod overlay (distinguished by magic byte)
- Backward scan: PWAD entries found before IWAD entries for same name
- Pre-computed lookup tables in memory at load time

## 2. BSP Trees (Doom)

Doom used 2D BSP trees for:
- Sector partitioning into convex subspaces
- Correct render order (front-to-back or back-to-front)
- REJECT map: precomputed sector-to-sector visibility
- Sound propagation path determination

**BSP Structure:**
- Nodes: partition lines with front/back children
- SSectors (subsectors): leaf nodes, reference segs
- Segs: line segments that form subsector boundaries
- Vertices: raw geometry points

## 3. Quake 3D BSP (1996)

Quake moved to 3D BSP trees with full 3D visibility:

**PVS (Potentially Visible Set):**
- Precomputed visibility per BSP leaf
- Store as bit vector
- O(1) visibility test at runtime
- 20KB per level on average
- Built offline via VIS tool

**The Surface Cache:**
Three-layer architecture:
1. Lightmaps baked offline (16-texel resolution)
2. Surface cache for recently used combos
3. Rasterizer tiles to screen

> "The whole story of Quake's visible-surface determination is the story of Carmack trying every clever algorithm and finding that none of them worked — then discovering that a precomputed table lookup disguised as an algorithm did work. Cache, not compute." — paraphrased from Abrash

## 4. Fast Inverse Square Root (Quake III)

Q_rsqrt() in q_math.c:
- 0x5f3759df magic constant
- 4x faster than FPU
- 0.175% max relative error
- 1 Newton-Raphson iteration

## 5. Data-Driven Architecture (All Eras)

| Era | Mechanism | Purpose |
|-----|-----------|---------|
| Doom | WAD + DeHackEd | Static data + runtime patching |
| Quake | QuakeC (bytecode) | Game logic as compiled C subset |
| Quake II | gamex86.dll | Native game module |
| Quake III | QVM (bytecode + optional DLL) | Platform-independent + fast path |
| Doom 3 | Declarative entity defs | Scriptable entity system |
| id Tech 4+ | Object-oriented entity system | Full OOP model |

## 6. Memory Management

- Zone allocator (z_malloc): permanent, scope-based
- Hunk allocator (Hunk_Alloc): linear bump with tag system
- Cache subsystem: eviction-based, oldest freed under pressure
- No garbage collection

## 7. Network Model (Quake III)

- Client-server (not P2P like Doom)
- Delta compression: changed fields only
- Serial number for stale reference detection
- Single algorithm for all update types

## 8. Job System (id Tech 5)

- Task-based multithreading
- Dependency graph for job scheduling
- 1-frame latency budget
- Player-facing systems exempted
- Job lists for cache-coherent iteration

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: big-pickle | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
