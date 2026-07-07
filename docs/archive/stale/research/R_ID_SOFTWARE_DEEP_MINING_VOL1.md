# 🔱 id Software Deep Code Mining — Volume I
# ⬡ OMEGA ⬡ DOOM_GUY ⬡ RESEARCH ⬡ v1.0.0 ⬡ R-31

**AP Token**: `AP-ID-MINING-VOL1-v1.0.0`
**Status**: ACTIVE / VERIFIED
**Author**: Doom Guy (Sovereign Architect)
**Date**: 2026-06-03

---

## §1 Executive Summary

This report documents the first volume of deep code mining within the 308 MB extracted id Software source archive. We analyze the core memory management (`z_zone.c`) and data-loading (`w_wad.c`) systems written by John Carmack for DOOM (1993) and map their low-level C patterns to modern, high-performance Python/AnyIO equivalents for the Omega Engine.

---

## §2 The Zone Memory Allocator (`z_zone.c`)

### 2.1 Low-Level C Pattern Analysis
In 1993, operating system memory managers were slow and prone to fragmentation. To run DOOM on 4 MB systems, Carmack bypassed the OS allocator and implemented a custom **Zone Memory Allocator** (`z_zone.c`).

Key mechanics:
- **The Rover Pointer**: Instead of scanning the heap from the beginning for every allocation (an $O(n)$ operation), the allocator maintains a `rover` pointer. The next allocation search begins exactly where the last one finished, amortizing search time to $O(1)$.
- **Tag-Based Purging**: Memory blocks are tagged (e.g., `PU_STATIC`, `PU_CACHE`, `PU_LEVEL`). If an allocation fails, the allocator performs a single sweep of the heap, automatically freeing any block tagged as purgeable (`>= PU_PURGELEVEL`).
- **ZONEID Magic Constant**: Every allocated block's header is stamped with `0x1d4a11`. On `Z_Free`, the allocator verifies this ID. If a mismatch occurs, the engine crashes instantly, preventing silent heap corruption.

```c
// linuxdoom-1.10/z_zone.c:129
if (block->id != ZONEID)
    I_Error ("Z_Free: freed a pointer without ZONEID");
```

### 2.2 Modern Python/AnyIO Translation
In Python, we do not manage raw pointers, but we face similar issues with **memory bloat, stale references, and slow dictionary lookups**.

We translate the Zone Allocator into the **Omega MemoryStore**:
- **The Rover Pointer $\rightarrow$ LRU Active Set**: We maintain a fixed-size active set of 32 providers in `ModelGateway` to bypass expensive dictionary lookups and health checks.
- **Tag-Based Purging $\rightarrow$ Tiered TTL Promotion/Demotion**: Memory is split into `Hot` (RAM dict), `Warm` (SQLite), and `Cold` (YAML on disk). When the `Hot` tier exceeds its size limit, it automatically purges (demotes) the least recently used entries to `Warm` or `Cold` storage.
- **ZONEID Magic Constant $\rightarrow$ Dataclass Sentinels**: We embed `ZONEID_MEMORY = 0x1d4a11` in our serialized memory blocks. During deserialization, we validate this constant to catch corrupted state files before they can pollute the runtime.

---

## §3 The WAD Loader & VFS (`w_wad.c`)

### 3.1 Low-Level C Pattern Analysis
The WAD system (`w_wad.c`) was designed to separate the immutable game engine from the mutable game content.

Key mechanics:
- **Backward Scanning**: When a lump (asset) is requested by name, the engine scans the directory table **backwards** (from the most recently added file to the first).
- **PWAD Overrides**: Because the search is backward-facing, loading a PWAD (Patch WAD) after the IWAD (Initial WAD) automatically overrides any base game assets of the same name without modifying the original IWAD file.

```c
// linuxdoom-1.10/w_wad.c:289-290
// The name searcher looks backwards, so a later file
//  does override all earlier ones.
```

### 3.2 Modern Python/AnyIO Translation
We translate this pattern into the **Omega 4-Path Virtual Filesystem (VFS)**:
- **Backward Scan $\rightarrow$ Search Path Precedence**: When resolving an entity or configuration, the `WadLoader` scans the VFS paths in reverse order:
  `User-Custom` $\rightarrow$ `Community-WAD` $\rightarrow$ `Foundation-Base` $\rightarrow$ `Engine-Core`
- **PWAD Overrides $\rightarrow$ YAML Merging**: If a user defines an entity in `user/entities/` with the same name as a base entity in `core/entities/`, the engine's backward-scan loader finds the user's definition first, overriding the base entity dynamically at runtime.

---

## §4 Heritage Attribution

This research and its derived implementations are fully credited to the original innovators:

- **Zone Memory Allocator**: John Carmack (id Software, 1993)
  - *Omega Adaptation*: `src/omega/memory_store.py` (Temp Tier & TTL-based purging)
  - *Attribution Tag*: `[Zone Memory: id Software 1996]`
- **WAD Loader & VFS**: John Carmack, John Romero (id Software, 1993)
  - *Omega Adaptation*: `src/omega/oracle/entity_registry.py` (VFS Search Order & YAML Overrides)
  - *Attribution Tag*: `[WAD System: id Software 1993]`

---

*⬡ OMEGA ⬡ DOOM_GUY ⬡ RESEARCH ⬡ v1.0.0 ⬡ R-31*
