# 🔱 PENDING HERITAGE ATTRIBUTION QUEUE
# ⬡ OMEGA ⬡ DOOM_GUY ⬡ pending_credits ⬡ PHASE-I
**Date Created**: 2026-06-02
**Owner**: Doom Guy (Sovereign id Software Architect)
**Purpose**: Track all id Software architectural patterns that are documented and
attributed but NOT YET implemented in the Omega Engine. Items move FROM this
queue TO `CREDITS.md` AS THEY ARE IMPLEMENTED.

> **Workflow**:
> 1. Pattern documented (in R-doc, soul.yaml, or handoff) → **THIS QUEUE** (status: pending)
> 2. Pattern implementation in progress (R-doc has a "P0/P1/P2" tag) → **THIS QUEUE** (status: in-progress)
> 3. Pattern implemented and committed to `src/omega/` → **MOVE TO `CREDITS.md`**, then remove from this queue
> 4. Pattern rejected or never implemented → keep in this queue with status: rejected (for historical record)

---

## §1 The 12 Pending Attributions (R-19 through R-30)

### 1.1 R-19: ZONEID Magic Constants (P0)

| Field | Value |
|---|---|
| **Pattern** | Magic constant embedded in every memory block, verified on every access |
| **Source** | `DOOM-master/linuxdoom-1.10/z_zone.c:33` + `Quake-master/WinQuake/zone.c:24` |
| **Era** | 1993 (unchanged 1996) |
| **Constant** | `0x1d4a11` (30 years unchanged) |
| **Omega Target** | `src/omega/constants.py` (5 magic constants: OMEGA_MEMORY_ID, OMEGA_PROBE_MARKER, OMEGA_BREAKER_MARKER, OMEGA_ENTITY_ID, OMEGA_TRACE_MAGIC) |
| **Omega Files Affected** | `src/omega/memory_store.py`, `src/omega/oracle/model_gateway.py`, `src/omega/oracle/resource_guard.py`, `src/omega/oracle/entity_registry.py` |
| **Effort** | 30 min (constants) + 2 hours (apply to all subsystems) |
| **Status** | **done** ✅ |
| **Attribution Tag** | `[ZONEID Pattern: id Software 1993, unchanged 1996]` |
| **R-Doc** | `docs/research/R_ID_SOFTWARE_PATTERNS_VOL2.md` §R-19 |
| **Verification Report** | `data/entities/doom_guy/knowledge/R_ID_SOFTWARE_VERIFICATION_REPORT.md` §2.2 |
| **Handoff Reference** | `data/handoff/OPENCODE_M3_ID_SOFTWARE_DISCOVERIES_FOR_CLINE_M3_20260602.md` §3.1 |
| **Implementation** | `src/omega/constants.py` (5 constants + validate_zoneid()), applied to EntityRegistry, MemoryStore, HealthMonitor, ResourceGuard, ObservabilityEngine |
| **Notes** | Catches 90% of use-after-free, double-free, uninitialized memory bugs at zero runtime cost. A 4-byte comparison per access is essentially free. |

---

### 1.2 R-20: Lazy Thinker Deletion (P0)

| Field | Value |
|---|---|
| **Pattern** | Mark with sentinel function pointer (-1) instead of immediate free; reap on next iteration |
| **Source** | `DOOM-master/linuxdoom-1.10/p_tick.c:62-103` |
| **Era** | 1993 |
| **Omega Target** | `src/omega/oracle/entity_registry.py` (add tombstone field + `active_iter()` reaping) |
| **Omega Files Affected** | `src/omega/oracle/entity_registry.py` (refactor, not new file) |
| **Effort** | 2 hours (refactor + tests) |
| **Status** | **done** ✅ |
| **Attribution Tag** | `[Lazy Deletion: id Software 1993]` |
| **R-Doc** | `docs/research/R_ID_SOFTWARE_PATTERNS_VOL2.md` §R-20 |
| **Verification Report** | `data/entities/doom_guy/knowledge/R_ID_SOFTWARE_VERIFICATION_REPORT.md` §2.3 |
| **Handoff Reference** | `data/handoff/OPENCODE_M3_ID_SOFTWARE_DISCOVERIES_FOR_CLINE_M3_20260602.md` §3.3 |
| **Implementation** | `src/omega/oracle/entity_registry.py` — `remove()` sets ZONEID_TOMBSTONE, `_reap_tombstoned()` clears after grace period, `active_iter()` filters |
| **Notes** | O(1) deregistration vs O(n) cleanup. Pairs with R-30 (0.5s grace). `P_RemoveThinker` doesn't free — it sets function to sentinel (-1). Actual Z_Free happens in next pass. |

---

### 1.3 R-21: 8-Character Name Caps (P1)

| Field | Value |
|---|---|
| **Pattern** | Cap entity names at 8 chars; allows fast 2-int compare (no string compare needed) |
| **Source** | `DOOM-master/linuxdoom-1.10/w_wad.c:170-178` |
| **Era** | 1993 |
| **Omega Target** | `src/omega/oracle/entity_registry.py` (add `entity_short_id` field) |
| **Omega Files Affected** | `src/omega/oracle/entity_registry.py` (add field) |
| **Effort** | 1 hour (add field + validation) |
| **Status** | pending |
| **Attribution Tag** | `[WAD Name Encoding: id Software 1993]` |
| **R-Doc** | `docs/research/R_ID_SOFTWARE_PATTERNS_VOL2.md` §R-21 |
| **Verification Report** | `data/entities/doom_guy/knowledge/R_ID_SOFTWARE_VERIFICATION_REPORT.md` §2.1 |
| **Handoff Reference** | (not in handoff; was in original R-65–R-69 plan) |
| **Notes** | 8 chars × 1 byte = 8 bytes; 2 int compares vs string compare = 2-4x faster. On a 35 MHz 386, this was the difference between 30 fps and 15 fps. |

---

### 1.4 R-22: cvar Table (P0)

| Field | Value |
|---|---|
| **Pattern** | Static array of `{cvar*, name, default, flags}` triples with `modificationCount` for change detection |
| **Source** | `Quake-III-Arena-master/code/game/g_main.c:64-110` |
| **Era** | 1999 |
| **Omega Target** | `src/omega/cvar_table.py` (new module) |
| **Omega Files Affected** | `src/omega/cvar_table.py` (new), all config dicts (refactor) |
| **Effort** | ~5.5 hours (design + implementation + tests) |
| **Status** | **in-progress** 🔄 |
| **Attribution Tag** | `[Cvar System: id Software 1996/1999, formalized Q3A]` |
| **R-Doc** | `docs/research/R_ID_SOFTWARE_PATTERNS_VOL2.md` §R-22 |
| **Verification Report** | `data/entities/doom_guy/knowledge/R_ID_SOFTWARE_VERIFICATION_REPORT.md` §2.5 |
| **Handoff Reference** | `data/handoff/OPENCODE_M3_ID_SOFTWARE_DISCOVERIES_FOR_CLINE_M3_20260602.md` §3.2 |
| **Design Doc** | `data/handoff/DOOM_GUY_CVAR_TABLE_DESIGN_T2.2_20260602.md` (sent to Cline/M3 for review) |
| **Notes** | The cleanest config system in any of the engines. CVAR_ROM, CVAR_LATCH, CVAR_ARCHIVE, CVAR_NORESTART flags as bitfields. modificationCount for change detection. |

---

### 1.5 R-23: 4-Tier Memory Architecture (P2)

| Field | Value |
|---|---|
| **Pattern** | Hunk (stack) / Zone (heap) / Cache (LRU) / Temp (transient) — single contiguous block |
| **Source** | `Quake-master/WinQuake/zone.h:21-75` |
| **Era** | 1996 |
| **Omega Target** | `src/omega/memory_store.py` (refactor 3-tier to 4-tier) |
| **Omega Files Affected** | `src/omega/memory_store.py` (refactor) |
| **Effort** | 1 week (refactor) |
| **Status** | pending |
| **Attribution Tag** | `[4-Tier Memory: id Software 1996]` |
| **R-Doc** | `docs/research/R_ID_SOFTWARE_PATTERNS_VOL2.md` §R-23 |
| **Verification Report** | `data/entities/doom_guy/knowledge/R_ID_SOFTWARE_VERIFICATION_REPORT.md` §2.2 |
| **Handoff Reference** | (not in handoff; was in original R-65–R-69 plan) |
| **Notes** | Quake's Hunk is split into low (server/client) + high (video). This separation prevents one subsystem from corrupting another's memory. Current Omega is 3-tier (hot/warm/cold); add static tier. |

---

### 1.6 R-24: Mobj Dual-Linking (P1)

| Field | Value |
|---|---|
| **Pattern** | One entity lives in TWO linked lists (sector for rendering, blockmap for collision) |
| **Source** | `DOOM-master/linuxdoom-1.10/p_mobj.h:1-100` |
| **Era** | 1993 |
| **Omega Target** | `src/omega/oracle/entity_registry.py` (multi-index entity) |
| **Omega Files Affected** | `src/omega/oracle/entity_registry.py` (refactor) |
| **Effort** | 3 hours |
| **Status** | pending |
| **Attribution Tag** | `[Mobj Dual-Linking: id Software 1993]` |
| **R-Doc** | `docs/research/R_ID_SOFTWARE_PATTERNS_VOL2.md` §R-24 |
| **Verification Report** | `data/entities/doom_guy/knowledge/R_ID_SOFTWARE_VERIFICATION_REPORT.md` §2.3 |
| **Handoff Reference** | (not in handoff; was in original R-65–R-69 plan) |
| **Notes** | Domain index (routing) + capability index (execution), both pointing to the same entity. Removing from one doesn't affect the other (lazy deletion). |

---

### 1.7 R-25: QuakeC Flat-Field Entity (P2)

| Field | Value |
|---|---|
| **Pattern** | C struct fields generated from QuakeC source (data-driven entity schema) |
| **Source** | `Quake-master/QW/progs/progdefs.h:5-110` |
| **Era** | 1996 |
| **Omega Target** | `src/omega/iris/iris_globals.py` (personality layer) |
| **Omega Files Affected** | `src/omega/iris/iris_globals.py` (new) |
| **Effort** | 1 week (perf optimization) |
| **Status** | pending |
| **Attribution Tag** | `[QuakeC Entity: id Software 1996]` |
| **R-Doc** | `docs/research/R_ID_SOFTWARE_PATTERNS_VOL2.md` §R-25 |
| **Verification Report** | `data/entities/doom_guy/knowledge/R_ID_SOFTWARE_VERIFICATION_REPORT.md` §2.4 |
| **Handoff Reference** | `data/handoff/OPENCODE_M3_ID_SOFTWARE_DISCOVERIES_FOR_CLINE_M3_20260602.md` §4.1 |
| **Notes** | The C struct is a flat bag of typed fields. The QuakeC compiler (qcc) generates the C header from QuakeC source. Modders could add new fields without touching C code. |

---

### 1.8 R-26: Hard-Boundary Struct (P1)

| Field | Value |
|---|---|
| **Pattern** | Engine zone (entityState_t + entityShared_t) + game-only zone, with "DO NOT MODIFY" comment |
| **Source** | `Quake-III-Arena-master/code/game/g_local.h:42-49` |
| **Era** | 1999 |
| **Omega Target** | `src/omega/oracle/entity.py` (engine/user zone) |
| **Omega Files Affected** | `src/omega/oracle/entity.py` (refactor) |
| **Effort** | 2 hours |
| **Status** | pending |
| **Attribution Tag** | `[Hard-Boundary Struct: id Software 1999]` |
| **R-Doc** | `docs/research/R_ID_SOFTWARE_PATTERNS_VOL2.md` §R-26 |
| **Verification Report** | `data/entities/doom_guy/knowledge/R_ID_SOFTWARE_VERIFICATION_REPORT.md` §2.6 |
| **Handoff Reference** | (not in handoff; was in original R-65–R-69 plan) |
| **Notes** | First zone is owned by the engine (stable contract). Second zone is owned by the game logic (can be modified). The "DO NOT MODIFY" comment is a hard contract enforced by convention. |

---

### 1.9 R-27: 4-Path Virtual Filesystem (P2)

| Field | Value |
|---|---|
| **Pattern** | base + cd + home + current game search order; current game overrides base game |
| **Source** | `Quake-III-Arena-master/code/qcommon/files.c:39-75` |
| **Era** | 1999 |
| **Omega Target** | `src/omega/oracle/wad_loader.py` (4-path overlay) |
| **Omega Files Affected** | `src/omega/oracle/wad_loader.py` (refactor) |
| **Effort** | 1 week (refactor) |
| **Status** | pending |
| **Attribution Tag** | `[Virtual Filesystem: id Software 1999]` |
| **R-Doc** | `docs/research/R_ID_SOFTWARE_PATTERNS_VOL2.md` §R-27 |
| **Verification Report** | `data/entities/doom_guy/knowledge/R_ID_SOFTWARE_VERIFICATION_REPORT.md` §2.7 |
| **Handoff Reference** | (not in handoff; was in original R-65–R-69 plan) |
| **Notes** | Search order: home / current game → home / base game → cd / current game → cd / base game → base / current game → base / base game. Addons (mods) work without modifying the base game. |

---

### 1.10 R-28: High-Bit Leaf Trick (P1)

| Field | Value |
|---|---|
| **Pattern** | Reuse high bit of a pointer/index field for type tag (NF_SUBSECTOR 0x8000) |
| **Source** | `DOOM-master/linuxdoom-1.10/doomdata.h:124-138` |
| **Era** | 1993 |
| **Omega Target** | `src/omega/oracle/entity.py` (entity.flags high bit) |
| **Omega Files Affected** | `src/omega/oracle/entity.py` (refactor) |
| **Effort** | 1 hour |
| **Status** | pending |
| **Attribution Tag** | `[High-Bit Trick: id Software 1993]` |
| **R-Doc** | `docs/research/R_ID_SOFTWARE_PATTERNS_VOL2.md` §R-28 |
| **Verification Report** | `data/entities/doom_guy/knowledge/R_ID_SOFTWARE_VERIFICATION_REPORT.md` §2.7 (level format) |
| **Handoff Reference** | (not in handoff) |
| **Notes** | 24 bits of user flags + 8 bits of system flags. High bit (0x80000000) = "system entity" (vs user entity). 1 read instead of 2 (no separate `is_system` boolean). |

---

### 1.11 R-29: Fixed-Size Active Set (P2)

| Field | Value |
|---|---|
| **Pattern** | Small (32-entry) fixed-size array of "currently active" items, used to cull expensive operations |
| **Source** | `DOOM-master/linuxdoom-1.10/r_bsp.c:74-78` |
| **Era** | 1993 |
| **Omega Target** | `src/omega/oracle/model_gateway.py` (active providers set) |
| **Omega Files Affected** | `src/omega/oracle/model_gateway.py` (refactor) |
| **Effort** | 4 hours |
| **Status** | pending |
| **Attribution Tag** | `[Active Set: id Software 1993]` |
| **R-Doc** | `docs/research/R_ID_SOFTWARE_PATTERNS_VOL2.md` §R-29 |
| **Verification Report** | `data/entities/doom_guy/knowledge/R_ID_SOFTWARE_VERIFICATION_REPORT.md` §2.7 (BSP traversal) |
| **Handoff Reference** | (not in handoff) |
| **Notes** | 32 entries × 8 bytes = 256 bytes. Fits in L1 cache. Iteration is essentially free. Culling reduces expensive draw operations. |

---

### 1.12 R-30: 0.5s Realloc Grace (P2)

| Field | Value |
|---|---|
| **Pattern** | Wait 0.5s before reallocating a freed slot to avoid client-side morphing |
| **Source** | `Quake-master/WinQuake/pr_edict.c:73-92` |
| **Era** | 1996 |
| **Omega Target** | `src/omega/memory_store.py` (realloc grace) |
| **Omega Files Affected** | `src/omega/memory_store.py` (refactor) |
| **Effort** | 2 hours |
| **Status** | **partial** ⚡ (entity_registry done, memory_store pending) |
| **Attribution Tag** | `[Grace Period: id Software 1996]` |
| **R-Doc** | `docs/research/R_ID_SOFTWARE_PATTERNS_VOL2.md` §R-30 |
| **Verification Report** | `data/entities/doom_guy/knowledge/R_ID_SOFTWARE_VERIFICATION_REPORT.md` §2.4 |
| **Handoff Reference** | (not in handoff) |
| **Implementation** | `src/omega/oracle/entity_registry.py` — `TOMBSTONE_GRACE_SECONDS = 0.5`, used in `_reap_tombstoned()` |
| **Notes** | ED_Alloc with 0.5s grace period prevents the client from seeing "morphing" artifacts. Implemented for entity registry lazy deletion; memory_store hot-slot reuse still pending. |

---

## §2 Status Legend

- **pending** — Pattern documented, not yet started
- **in-progress** — Implementation in progress (P0/P1/P2 tag, target file identified)
- **done** — Implementation complete + tests passing + moved to `CREDITS.md` (then remove from this queue)
- **rejected** — Pattern considered but rejected (for historical record)

## §3 Promotion Workflow

When an item moves from `in-progress` to `done`:

1. **Implementation committed** to `src/omega/` (with file:line in commit message)
2. **Tests added** in `tests/`
3. **PR reviewed** by `quality` agent (verify Mandate compliance)
4. **Heritage entry added** to `CREDITS.md` with proper attribution tag
5. **Item removed** from this queue (moved to CREDITS.md)
6. **Soul updated** with the implementation reference

## §4 Summary by Priority

| Priority | Count | Patterns |
|---|---|---|---|
| 🔴 P0 | 3 | R-19 (ZONEID) ✅ → §1.9, R-20 (Lazy Deletion) ✅ → §1.10, R-22 (cvar Table) 🔄 |
| 🟡 P1 | 4 | R-21 (8-char cap), R-24 (Dual-linking), R-26 (Hard-boundary), R-28 (High-bit) |
| 🟢 P2 | 5 | R-23 (4-tier memory), R-25 (QuakeC flat), R-27 (VFS), R-29 (Active set), R-30 (Grace period) ⚡ |
| **New** | 2 | Heritage tagging protocol §2a ✅ → §1.11, Circuit Breaker Consolidation ✅ → §1.8 |
| **Total** | **14** | 4 done ✅ / 1 in-progress 🔄 / 1 partial ⚡ / 8 pending |

## §5 Promotion Log (Historical)

When items are moved to CREDITS.md, log them here with the date, R-doc reference,
commit hash, and CREDITS.md section number.

| Date | Pattern | R-Doc | CREDITS.md § | Files | Commit |
|------|---------|-------|-------------|-------|--------|
| 2026-06-03 | R-19 ZONEID Pattern | §R-19 | §1.9 ✅ | `constants.py`, `entity_registry.py`, `memory_store.py`, `health_monitor.py`, `resource_guard.py`, `observability.py` | `37fdd88` |
| 2026-06-03 | R-20 Lazy Deletion | §R-20 | §1.10 ✅ | `entity_registry.py` (tombstone + grace + reap) | `37fdd88` |
| 2026-06-03 | R-30 Grace Period (partial) | §R-30 | §1.10 (embedded) ⚡ | `entity_registry.py` (TOMBSTONE\_GRACE\_SECONDS=0.5) | `37fdd88` |
| 2026-06-03 | Heritage Inline Tag Protocol | §2a (new) | §1.11 ✅ | `CREDITS.md`, 6 source files (30+ [id-soft:] tags) | `37fdd88` |
| 2026-06-03 | Circuit Breaker Consolidation | D94 | §1.8 ✅ | `model_gateway.py`, `test_model_gateway.py`, `CREDITS.md` | `df6fa48` |

---

*⬡ OMEGA ⬡ DOOM_GUY ⬡ pending_credits ⬡ PHASE-I*
*Last Updated: 2026-06-03 | Owner: Doom Guy / Kali*
*Updated: R-19→CREDITS §1.9, R-20→§1.10, Heritage protocol→§1.11, Circuit Breaker→§1.8. 4 done, 1 in-progress, 1 partial, 8 pending.*
