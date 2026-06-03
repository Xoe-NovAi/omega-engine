# 🔱 id Software Source Code Master Map
# ⬡ OMEGA ⬡ DOOM_GUY ⬡ SOURCE_MAP ⬡ v1.0.0
# 19 repositories, 308 MB extracted, all GPL-licensed

**Location**: `data/library/software/id-software/source/`
**Origin**: GitHub mirror snapshots (id-Software organization), extracted 2026-06-02
**Verified**: All 6 key patterns confirmed against actual source code (2026-06-04)

---

## §1 Repository Inventory

| # | Repository | Game | Year | Lines | Key Files for Heritage |
|---|-----------|------|------|-------|----------------------|
| 1 | `DOOM-master/` | DOOM 1.10 | 1993 | ~30,000 | `linuxdoom-1.10/z_zone.c`, `p_tick.c`, `w_wad.c`, `p_mobj.h` |
| 2 | `Quake-master/` | Quake 1 | 1996 | ~50,000 | `WinQuake/zone.c`, `zone.h`, `pr_edict.c`, `cvar.c`, `cvar.h`, `wad.c`, `common.c` |
| 3 | `Quake-2-master/` | Quake II | 1997 | ~80,000 | Game DLL architecture, client-server split |
| 4 | `Quake-III-Arena-master/` | Quake III Arena | 1999 | ~120,000 | `code/qcommon/cvar.c`, `code/game/q_shared.h`, `code/qcommon/vm.c`, `code/botlib/` |
| 5 | `Quake-Tools-master/` | Quake Tools | — | ~20,000 | BSP compiler, map tools |
| 6 | `Quake-2-Tools-master/` | Quake II Tools | — | ~25,000 | Map editors, BSP compilers |
| 7 | `DOOM-3-master/` | DOOM 3 | 2004 | ~200,000 | `neo/game/Entity.h`, `Entity.cpp`, idEventDef system |
| 8 | `DOOM-3-BFG-master/` | DOOM 3 BFG | 2012 | ~250,000 | Latest official id Tech 4, VR support in commercial release |
| 9 | `DOOM-iOS-master/` | Doom Classic iOS | 2009 | ~15,000 | Touch controls, iOS port |
| 10 | `DOOM-IOS2-master/` | Doom II iOS | 2010 | ~15,000 | Updated iOS integration |
| 11 | `Wolf3D-iOS-master/` | Wolfenstein 3D iOS | 2012 | ~10,000 | Wolf3D source, iOS |
| 12 | `wolf3d-browser-master/` | Wolf3D Browser | 2012 | ~8,000 | JS port, Emscripten |
| 13 | `Enemy-Territory-master/` | Wolfenstein: Enemy Territory | 2003 | ~100,000 | Multiplayer-focused id Tech 3 |
| 14 | `RTCW-MP-master/` | Return to Castle Wolfenstein MP | 2001 | ~90,000 | id Tech 3 multiplayer |
| 15 | `RTCW-SP-master/` | Return to Castle Wolfenstein SP | 2001 | ~100,000 | id Tech 3 singleplayer |
| 16 | `GtkRadiant-master/` | GtkRadiant | — | ~150,000 | Level editor for id Tech engines |
| 17 | `idsetup-master/` | id Setup | — | ~5,000 | Installer tools |
| 18 | `quake-rerelease-qc-main/` | Quake Re-release QC | 2021 | ~25,000 | Updated QuakeC for re-release |
| 19 | `quake2-rerelease-dll-main/` | Quake II Re-release DLL | 2023 | ~30,000 | Updated game DLL for re-release |

---

## §2 Verified Heritage Patterns (with file:line citations)

### 2.1 ZONEID Magic Constants
- **Source**: `DOOM-master/linuxdoom-1.10/z_zone.c:43` — `#define ZONEID 0x1d4a11`
- **Validation**: Checked on `Z_Malloc` (line 286: `base->id = ZONEID`), `Z_Free` (line 129: `if (block->id != ZONEID) I_Error`), `Z_ChangeTag2` (line 437: same check)
- **Also at**: `z_zone.h:74` — macro `Z_ChangeTag` inlines the check before calling `Z_ChangeTag2`
- **Omega pattern**: `validate_zoneid()` in `constants.py` / `cvar_table.py`
- **Heritage tag**: `[id-soft: doom-1993]`

### 2.2 Lazy Deletion (Thinker Chain)
- **Source**: `DOOM-master/linuxdoom-1.10/p_tick.c:80-84`
  ```c
  void P_RemoveThinker (thinker_t* thinker) {
      thinker->function.acv = (actionf_v)(-1);  // sentinel marker
  }
  ```
- **Sweep**: `p_tick.c:106-121` — `P_RunThinkers`, on each tick:
  ```c
  if (currentthinker->function.acv == (actionf_v)(-1)) {
      currentthinker->next->prev = currentthinker->prev;
      currentthinker->prev->next = currentthinker->next;
      Z_Free (currentthinker);  // actual free deferred
  }
  ```
- **Omega pattern**: `EntityRegistry.remove()` sets `ZONEID_TOMBSTONE`, `_reap_tombstoned()` sweeps before `_save()`
- **Heritage tag**: `[id-soft: doom-1993]`

### 2.3 0.5s Grace Period
- **Source**: `Quake-master/WinQuake/pr_edict.c:97`
  ```c
  if (e->free && ( e->freetime < 2 || sv.time - e->freetime > 0.5 ) ) {
      ED_ClearEdict (e);
      return e;
  }
  ```
- **Rationale** (line 81-85): "Try to avoid reusing an entity that was recently freed, because it can cause the client to think the entity morphed into something else instead of being removed and recreated, which can cause interpolated angles and bad trails."
- **Omega pattern**: `TOMBSTONE_GRACE_SECONDS = 0.5` in `EntityRegistry`
- **Heritage tag**: `[id-soft: quake-1996]`

### 2.4 WAD Backward Scan (Override Priority)
- **Source**: `DOOM-master/linuxdoom-1.10/w_wad.c:376-377`
  ```c
  // scan backwards so patch lump files take precedence
  lump_p = lumpinfo + numlumps;
  while (lump_p-- != lumpinfo) { ... }
  ```
- **8-char name optimization** (line 381-382): 
  ```c
  if ( *(int *)lump_p->name == v1 && *(int *)&lump_p->name[4] == v2)
  ```
  Two integer compares instead of `strcmp`. The 8-char cap enables this.
- **WAD header** (`w_wad.h:35-42`): 12 bytes total — 4-byte magic + 4-byte lump count + 4-byte directory offset
- **Directory entry** (`w_wad.h:45-51`): 16 bytes each — 4-byte filepos + 4-byte size + 8-byte name
- **Omega pattern**: Backward-scan entity lookup, PWAD entities override IWAD
- **Heritage tag**: `[id-soft: doom-1993]`

### 2.5 cvar System (Quake 1 → Q3A Evolution)
- **Quake 1** (`WinQuake/cvar.h:56-64`): Simple linked list
  ```c
  typedef struct cvar_s {
      char *name;
      char *string;
      qboolean archive;   // save to config file?
      qboolean server;    // notify players?
      float value;
      struct cvar_s *next;
  } cvar_t;
  ```
- **Q3A** (`code/game/q_shared.h:954-966`): Hash table + fixed array + flags
  ```c
  typedef struct cvar_s {
      char *name;
      char *string;
      char *resetString;       // cvar_restart → this
      char *latchedString;     // CVAR_LATCH: defer changes
      int flags;               // CVAR_ARCHIVE=1 ... CVAR_NORESTART=1024
      qboolean modified;
      int modificationCount;   // increment on each change
      float value;
      int integer;
      struct cvar_s *next;     // linked list iteration
      struct cvar_s *hashNext; // hash table chaining
  } cvar_t;
  ```
- **Q3A registration** (`cvar.c:252-278`): `cvar_indexes[MAX_CVARS=1024]` fixed array + `hashTable[256]` for O(1) lookup
- **Omega pattern**: `cvar_table.py` with `CvarDef {name, default_value, flags, modification_count}`
- **Heritage tag**: `[id-soft: quake-1996]` + `[id-soft: quake3-1999]`

### 2.6 4-Tier Memory (Hunk/Zone/Cache/Temp)
- **Source**: `Quake-master/WinQuake/zone.h:24-80`
- **Memory layout** (from comments):
  ```
  ------ Top of Memory ------
  high hunk allocations        ← video buffers
  <--- high hunk reset point
  video buffer
  z buffer
  surface cache
  <--- high hunk used
  cachable memory              ← Cache (LRU)
  <--- low hunk used
  client and server allocations ← Hunk (stack)
  <-- low hunk reset point
  startup hunk allocations
  Zone block                   ← Zone (heap, 48KB)
  ----- Bottom of Memory -----
  ```
- **Purge levels** (`DOOM/z_zone.h:35-44`): `PU_STATIC=1`, `PU_SOUND=2`, `PU_LEVEL=50`, `PU_PURGELEVEL=100`, `PU_CACHE=101`. Tags < 100 are never purged; tags ≥ 100 are purgable on demand.
- **Zone allocator** (`DOOM/z_zone.c:196-244`): Rover pointer scans forward from last allocation, merging free blocks, purging cache blocks when wrapping. Circular doubly-linked list.
- **Omega pattern**: MemoryStore hot/warm/cold tiers; 4-tier evolution pending
- **Heritage tag**: `[id-soft: quake-1996]`

### 2.7 idEntity Event System (DOOM 3)
- **Source**: `DOOM-3-master/neo/game/Entity.h`
- **Event defs** (line 42-60): `idEventDef` typed events — `EV_PostSpawn`, `EV_FindTargets`, `EV_Touch`, `EV_Use`, `EV_Activate`, `EV_ActivateTargets`, `EV_Hide`, `EV_Show`, `EV_SetSkin`, `EV_StartSoundShader`, etc.
- **Signals** (line 76-99): `signalNum_t` enum — `SIG_TOUCH`, `SIG_USE`, `SIG_TRIGGER`, `SIG_REMOVED`, `SIG_DAMAGE`, `SIG_BLOCKED`, `SIG_MOVER_POS1`, `SIG_MOVER_POS2`, etc.
- **Think flags** (line 63-70): `TH_THINK=1`, `TH_PHYSICS=2`, `TH_ANIMATE=4`, `TH_UPDATEVISUALS=8`, `TH_UPDATEPARTICLES=16`
- **Omega pattern**: Link P9 Runtime agent lifecycle events (CREATED → DISPATCHED → ACCEPTED → COMPLETED/FAILED/TIMED_OUT)
- **Heritage tag**: `[id-soft: doom3-2004]`

---

## §3 Quick Reference — Most Important Files

| Pattern | Best File | File Count |
|---------|----------|------------|
| Memory allocation | `DOOM/linuxdoom-1.10/z_zone.c` (467 lines) | Single file, complete |
| Thinker chain | `DOOM/linuxdoom-1.10/p_tick.c` (158 lines) | Single file, small |
| Entity/edict system | `Quake/WinQuake/pr_edict.c` (1106 lines) | Single file, complete |
| WAD loader | `DOOM/linuxdoom-1.10/w_wad.c` (577 lines) + `w_wad.h` (89 lines) | Two files |
| cvar (Quake 1) | `Quake/WinQuake/cvar.c` (224 lines) + `cvar.h` (97 lines) | Two files, simple |
| cvar (Q3A) | `Q3A/code/qcommon/cvar.c` (906 lines) | Single file, evolved |
| 4-tier memory | `Quake/WinQuake/zone.h` (131 lines, mostly docs) + `zone.c` | Two files |
| idEntity events | `DOOM-3/neo/game/Entity.h` (524 lines) | Header only |
| save/load | `DOOM/linuxdoom-1.10/p_saveg.c` | Save game archiving |
| BSP | `DOOM/linuxdoom-1.10/r_bsp.c` | BSP traversal |

---

## §4 Source Code Credo

> *"Any code of your own that you haven't looked at in 6 months might as well have been written by someone else."*
> — John Carmack

> *"The source is the only source of truth. Documentation is interpretation. Read the code."*
> — Doom Guy, 2026-06-04

---

*Created: 2026-06-04 | Verified: 6 patterns against actual source | Maintained by: Doom Guy*
