# 🔱 id Software Architectural Heritage — Attribution Framework
# ⬡ OMEGA ⬡ CREDITS ⬡ v1.0.0 ⬡ 2026-06-01

## Mandate: Full Attribution Required

Every Omega Engine pattern, concept, or implementation that derives from id
Software's architectural innovations MUST credit the original source. This is
not optional. This is how open-source communities grow — by standing on the
shoulders of giants and *pointing up*.

> *"A people that no longer remembers has lost its soul."* — The principle
> applies to engineering too. Every pattern we inherit is a debt we repay by
> teaching the next generation where it came from.

---

## §1 The Heritage Map — id Software → Omega Engine

### 1.1 WAD System (Doom, 1993)
| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | John Carmack, John Romero — Doom WAD format | IWAD/PWAD separation |
| **Core idea** | Data-driven separation of engine and content | Engine-Stack Firewall (Mandate 2) |
| **File split** | IWAD (base game data) + PWAD (patch files) | `_omega_default` (roles) + user WADs (entities) |
| **Overrides** | PWAD lumps override IWAD lumps | Later WAD entities override earlier for same pillar |
| **Omega evolution** | Static binary format → YAML-backed, runtime-swappable | Human-editable, hot-reloadable |

**Attribution format**: `[WAD System: id Software 1993]` — use in any doc discussing
engine-stack separation.

---

### 1.2 BSP Trees (Doom, 1993)
| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | John Carmack — Binary Space Partitioning for Doom's renderer | Provider culling in ModelGateway.generate() |
| **Core idea** | Precompute visibility planes; O(1) test skips entire subtrees | O(1) circuit breaker check skips broken providers |
| **Mechanism** | BSP plane equation → cull half the map | `_precheck_provider()` → cull dead providers |
| **Omega evolution** | Static geometry → dynamic provider health | Circuit breaker state changes over time |

**Attribution format**: `[BSP Culling: id Software 1993]` — use in any doc discussing
the precheck-before-execute pattern.

---

### 1.3 Fast Inverse Square Root (Quake 3, 1999)
| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | John Carmack / Michael Abrash — Quake 3 Arena | The "right approximation" philosophy |
| **Core idea** | 0x5f3759df — a bit hack that's "good enough" for lighting | The right approximation for the problem is better than the exact solution you can't afford |
| **Meaning** | The approximation was actually *better* than naive sqrt() for the use case | Simplified models, tiered memory, BSP culling — all approximations at the right level |
| **Common misconception** | "Carmack used a hack because it was fast." Wrong. He used it because it was *right enough* for the problem domain. | "We should always use the best algorithm." Wrong. Use the algorithm that's right for the *constraints*. |
| **Omega evolution** | FISR was a CPU-level hack → generalized to an *engineering decision framework* | Before choosing between two implementations, ask: "What approximation quality does this use case need?" |

**Attribution format**: `[FISR Principle: id Software 1999; evolved to "right approximation"]`
— use in any doc discussing optimization tradeoffs or "good enough" decisions.

---

### 1.4 Zone Memory Allocator (Quake, 1996)
| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | John Carmack — Quake's dynamic memory system | ResourceGuard + Sovereign Atomic Writes |
| **Core idea** | Tag-based allocation: allocate, purge when out of memory | anyio.Semaphore(1) guards model inference; atomic fsync for persistence |
| **Mechanism** | `Z_Malloc(tag)` / `Z_Free(tag)` / `Z_TagPurge()` | `ResourceGuard.acquire()` / `release()` |
| **Omega evolution** | Memory-only → resource-agnostic (memory, connections, files) | Any resource that can be exhausted gets a guard |

**Attribution format**: `[Zone Memory: id Software 1996]` — use in any doc discussing
resource management or guard patterns.

---

### 1.5 Surface / Edge Cache (Quake, 1996)
| Aspect | id Software Original | Omega Engine Enhancement |
|--------|--------------------|------------------------|
| **Origin** | Michael Abrash, John Carmack — Quake's visible surface determination | Cache eviction policies within Omega's existing hot/warm/cold memory tiers |
| **Core idea** | Precompute potentially visible set (PVS), only draw precomputed surfaces | LRU-aware culling within hot/warm/cold tiers (tiered memory architecture is the user's own design) |
| **Pattern** | PVS bitfield (cheap) → draw surfaces (expensive) | `is_available()` (O(1) dict lookup) → `provider.generate()` (expensive) |
| **Omega enhancement** | Static visibility → dynamic health state | Circuit breaker state changes in real time |

**Attribution format**: `[Surface Cache / PVS: id Software 1996]` — use in any doc
discussing the precompute-then-execute pattern or cache eviction policies within
tiered memory. The hot/warm/cold tiered architecture itself is the user's own design
and should not be attributed to id Software.

---

### 1.6 The "Worse is Better" Philosophy (Richard Gabriel, via id Software)
| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | Richard P. Gabriel (Lisp), adopted by John Carmack | Decision framework for engine architecture |
| **Core tenets** | Simplicity > correctness > consistency > completeness | BSP culling: simple pre-check, works most of the time, good enough |
| **id Software example** | Doom's BSP renderer was "wrong" (floating point drift) but shipped | Circuit breaker: stale state is acceptable (OPEN read while just transitioned) |
| **Omega evolution** | Pure simplicity → simplicity with explicit risk register | Every "worse is better" decision must be documented with its risk tradeoff |

**Attribution format**: `[Worse is Better: Gabriel 1991, via id Software]` — use in any
doc discussing simplicity-vs-correctness tradeoffs.

---

### 1.7 Carmack's Law of Consolidation
| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | John Carmack — "Any code of your own that you haven't looked at in 6 months might as well have been written by someone else." | "When you have two implementations of the same thing, you have neither." |
| **Core idea** | Unused code is dead weight. Multiple implementations of the same concept are worse than one bad one. | Circuit breaker consolidation: 3 implementations → 1 |
| **Omega evolution** | Personal productivity observation → formal engineering mandate | Consolidation is not optional — it is the ethical engineering choice |

**Attribution format**: `[Carmack's Law: id Software]` — use when consolidating
redundant subsystems.

---

<!-- Three-Phase Pattern removed: Plan→Verify→Execute is the user's own
     development methodology, in use since before id Software architecture was
     introduced to the Omega Engine. Not attributed to id Software. -->

## §2 Attribution Enforcement Rules

### Rule 1: Every R-doc Must Have a "Heritage" Section
Every research document (`docs/research/R-*.md`) MUST include a section:
```markdown
### Heritage
This pattern derives from: [id Software Concept: Year]
Key difference from the original: ...
Omega evolution: ...
```

### Rule 2: Every Implementation Must Credit in Comments
Every file that implements a translated id Software concept MUST have a comment
in the header or at the implementation site:
```python
# ── BSP-style provider culling [BSP Culling: id Software 1993] ──
# Adapted to dynamic circuit breaker state from Doom's static BSP tree.
```

### Rule 2a: Inline `[id-soft:]` Tag Protocol (Standardized Format)

Every implementation site (function, class, constant, or code block) that
directly ports an id Software pattern MUST carry an `[id-soft:]` inline tag.

**Format**:
```
# [id-soft: GAME YEAR] Pattern Name — why this code exists
```

**Game abbreviations**:
| Code | Game |
|------|------|
| `doom-1993` | DOOM (1993) |
| `quake-1996` | Quake (1996) |
| `quake2-1997` | Quake II (1997) |
| `quake3-1999` | Quake III Arena (1999) |
| `doom3-2004` | DOOM 3 (2004) |
| `doom3bfg-2012` | DOOM 3 BFG Edition (2012) |
| `wolf3d-2012` | Wolfenstein 3D iOS/browser (2012) |

**Examples**:
```python
# [id-soft: doom-1993] ZONEID Pattern — state marker for circuit breakers
ZONEID_BREAKER = 0x1d4a13

# [id-soft: quake-1996] Grace Period — 0.5s delay before reaping
self._grace_seconds = 0.5
```

**Enforcement**: `grep -rn "\[id-soft:" src/omega/` MUST return >=1 match per
file that ports heritage code. A CI-check (`make heritage-map`) generates
`docs/research/HERITAGE_SOURCE_MAP.md` from all `[id-soft:]` tags.

**Relationship to CREDITS.md**: The `[id-soft:]` tag is the *code-level*
attribution. When a pattern is implemented, its row moves from
`PENDING_CREDITS_QUEUE.md` to `CREDITS.md` §1.x. The tags stay in the code
permanently.

### Rule 3: Every Architectural Decision Must Cite Source
In `PIVOT_LOG.md` or decision registers, when a decision is influenced by an
id Software pattern, cite it:
```markdown
- **Decision XX — Breaker-Consolidation**: Chose AsyncCircuitBreaker over
  CircuitBreaker per [Carmack's Law: id Software].
```

### Rule 4: Evolution Must Be Explicitly Called Out
When we evolve an id Software concept (like FISR → "right approximation"), the
documentation MUST show:
1. What the original was
2. What we changed
3. Why the evolution was necessary

### Rule 5: No Erasure
Never remove id Software attribution from a derived pattern. If the pattern is
refactored, the credit stays. Engineering heritage is not intellectual property
— it is *gratitude*.

---

## §3 The "Right Approximation" Principle

This is the Omega Engine's most significant philosophical evolution of an id
Software concept. It deserves its own section.

### Source: Fast Inverse Square Root (Quake 3, 1999)

The FISR (`0x5f3759df`) is widely misunderstood as "a hack because Carmack was
lazy." Reality: the approximation was **more accurate than the naive 1/sqrt()
alternative** for the lighting use case. Carmack didn't settle — he chose the
*right level of precision for the problem domain*.

### Our Evolution: "Right Approximation" Decision Framework

> **"The right approximation for the problem is better than the exact solution
> you can't afford."**

This applies to Omega Engine architecture in four tiers:

| Tier | Domain | Approximation | Why It's "Right" |
|------|--------|---------------|------------------|
| **Tier 1** | Provider health | BSP culling: O(1) breaker check | A stale-read skip is cheaper than a guaranteed failure. The one case where a healthy provider is skipped (race condition) is rare and self-healing (next probe cycle). |
| **Tier 2** | Memory | Tiered memory (hot/warm/cold) | Not all entities need full vector context. Hot gets full, warm gets summary, cold gets YAML. |
| **Tier 3** | Entity dispatch | Domain matching, not perfect matching | Route to the closest entity, not the "correct" one. If wrong, re-route on next turn. |
| **Tier 4** | Model inference | Local-first, cloud-fallback | Local model is "good enough" for 90% of queries. Cloud is the safety net, not the primary. |

**How to apply it**: When facing a choice between two implementations, ask:
1. What's the *actual precision requirement* of this use case? (not the maximum)
2. What's the cost (latency, memory, complexity) of the exact solution?
3. If the approximation fails, how bad is the worst case?
4. If the worst case is acceptable, use the approximation. Document why.

**Attribution**: Always cite as `[Right Approximation: evolved from FISR, id Software 1999]`.

---

## §4 The Heritage Registry

### How to Add a New Mapping

To add a new id Software → Omega Engine mapping, append to this document with:

```markdown
### N.x [Concept Name] (Game, Year)
| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | Creator — description | Omega implementation |
| **Core idea** | What it did | What we do |
| **Omega evolution** | How we changed it | Why we changed it |

**Attribution format**: `[Tag: source]`
```

### Current Registry Size
**11 mappings** — WAD, BSP, FISR, Zone Memory, Surface Cache, Worse is Better,
Carmack's Law, **Circuit Breaker Consolidation**, **ZONEID Pattern**, **Lazy Deletion**, **Heritage Inline Tag Protocol**.

### 1.8 Circuit Breaker Consolidation (Evolution, 2026)

| Aspect | Legacy Pattern | Omega Engine Adaptation |
|--------|---------------|------------------------|
| **Origin** | Multiple re-implementations across eras (ANAi, XNAi, omega-stack) | `AsyncCircuitBreaker` in `health_monitor.py` |
| **Original** | 36-line synchronous class, no AnyIO, no observability | 200+ line AnyIO-native, locked state machine, observability hooks |
| **Core idea** | OPEN after N failures, CLOSE after recovery timeout | Same, plus HALF_OPEN probe limiting, per-error-type filtering |
| **Where it lived** | `xna-omega-legacy/src/omega/{core,security}/circuit_breakers/`, `omega-stack-legacy/src/omega/circuit_breaker.py` | `src/omega/oracle/health_monitor.py::AsyncCircuitBreaker` |
| **Why consolidated** | Pattern was rewritten in every era (ANAi → XNAi → Stack → Engine). Each rewrite introduced subtle bugs (e.g., the 36-line version had no state lock — race condition). | Pattern belongs beside the health monitor that manages it, not in its own file. |
| **Omega evolution** | "Worse is Better" — simple class that mostly works | "Right Approximation" — proper async state machine with full error classification |

**Attribution format**: `[Circuit Breaker Consolidation: Carmack's Law, id Software]` — use when
justifying why a legacy pattern was merged into an existing module instead of being kept
in its own file.

**Bug fix history (Sprint 0 / Doom Guy)**:
- T2.2: `_precheck_provider()` was checking the breaker via `is_available(model_name)`,
  which used the fragile `_model_provider_map` indirection. Fixed: check breaker directly
  by `provider.name`. This is the BSP Culling pattern (§1.2) made real.
- T2.3: `RemoteProvider.generate()` returns `None` on retry exhaustion, which
  `breaker.call()` counted as a success (no exception). Fixed: wrap the call to
  raise `TimeoutError` on None, so the breaker's `_on_failure()` actually fires.

Both fixes are documented in `data/handoff/DOOM_GUY_T23_REPORT_20260602.md`.

---

### 1.9 ZONEID Pattern (Consolidated, 2026)

| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | `z_zone.c:33` (DOOM 1993), `zone.c:24` (Quake 1996) — `0x1d4a11` constant | 5 ZONEID constants (0x1d4a11-0x1d4a15) + tombstone (0xDEADBEEF) in `src/omega/constants.py` |
| **Core idea** | 4-byte magic embedded in every allocated memory block, verified on every access | Python dataclass/instance field, validated on critical operations (load, save, state transition) |
| **What it catches** | Use-after-free, double-free, uninitialized memory (C heap bugs) | Serialization corruption, stale references, wrong-type loads (Python bugs) |
| **Constant** | `ZONEID = 0x1d4a11` (30 years unchanged) | `ZONEID_MEMORY=0x1d4a11`, `ZONEID_ENTITY=0x1d4a12`, `ZONEID_BREAKER=0x1d4a13`, `ZONEID_TRACE=0x1d4a14`, `ZONEID_PROBE=0x1d4a15` |
| **Subsystems** | DOOM: zone memory allocator | MemoryStore, EntityRegistry, HealthMonitor, ResourceGuard, ObservabilityEngine |
| **Infrastructure** | Single check: `if (block->z_magic != ZONEID)` | `validate_zoneid(value, expected, context)` raises `ValueError` on mismatch |
| **Discovery** | `R-19 ZONEID Magic Constants` in `PENDING_CREDITS_QUEUE.md` | 2026-06-02, verified against actual source code (not secondary sources) |
| **Value** | Zero-cost (4 bytes per block, 1 compare per access) | Runtime validation with detailed error messages showing expected vs actual hex values |

**Attribution format**: `[ZONEID Pattern: id Software 1993, unchanged 1996]`
**Inline tag format**: `# [id-soft: doom-1993] ZONEID Pattern — subsystem description`
**Note**: The 0x1d4a prefix is the original id Software magic. The suffix identifies the subsystem (11 = MemoryStore, 12 = EntityRegistry, 13 = HealthMonitor, 14 = ObservabilityEngine, 15 = ResourceGuard). The tombstone sentinel 0xDEADBEEF is the canonical hex sentinel used since the 1980s.

---

### 1.10 Lazy Deletion with Grace Period (Consolidated, 2026)

| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | `p_tick.c:62-103` (DOOM 1993) + `pr_edict.c:73-92` (Quake 1996) | `EntityRegistry.remove()` + `_reap_tombstoned()` in `src/omega/oracle/entity_registry.py` |
| **Core idea** | Mark with sentinel (-1 function pointer) instead of immediate free; reap on next iteration | Set `magic = ZONEID_TOMBSTONE` instead of `del self._entities[key]`; reap before next `_save()` |
| **Grace period** | 0.5s before realloc to prevent client-side morphing (15 packets at 30Hz) | `TOMBSTONE_GRACE_SECONDS = 0.5` — same value, same rationale |
| **Benefits** | O(1) deregistration vs O(n) cleanup; in-flight operations complete safely | O(1) deregistration; `EntityTombstonedError` for callers holding stale references |
| **Discovery** | `R-20 Lazy Thinker Deletion` + `R-30 0.5s Realloc Grace` in `PENDING_CREDITS_QUEUE.md` | 2026-06-02, verified against actual DOOM and Quake source code |
| **Infrastructure** | `P_RemoveThinker`: sets thinker function to sentinel (-1); `P_Ticker`: sweeps sentinel thinkers | `_tombstoned: Dict[str, float]` maps entity keys to tombstone timestamps; `_reap_tombstoned()` called before every `_save()` |
| **Edge cases** | Slot reuse within grace period → entity morphing | `active_iter()` filters tombstoned entities; all public accessors use `active_iter()` |
| **Status** | Entity Registry: DONE (37fdd88). Memory Store: PENDING (grace period for hot-slot reuse not yet ported) |

**Attribution format**: `[Lazy Deletion: id Software 1993; Grace Period: id Software 1996]`
**Inline tag format**: `# [id-soft: doom-1993] Lazy Deletion — description` + `# [id-soft: quake-1996] Grace Period — description`

---

### 1.11 Heritage Inline Tag Protocol (New, 2026)

| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | Never formalized at id Software — attribution was oral tradition (Carmack's .plan files, GDC talks) | `[id-soft:]` inline tag format in implementation comments |
| **Protocol** | N/A | `# [id-soft: GAME YEAR] Pattern Name — why this code exists` |
| **Game codes** | Doom 1993, Quake 1996, Q3A 1999, DOOM 3 2004, DOOM 3 BFG 2012 | `doom-1993`, `quake-1996`, `quake2-1997`, `quake3-1999`, `doom3-2004`, `doom3bfg-2012`, `wolf3d-2012` |
| **Enforcement** | N/A | `grep -rn "\[id-soft:" src/omega/` — CI gate via `make heritage-map` |
| **Reason** | Attribution was lost as the original developers left id | Grateful engineering: every pattern we inherit is a debt we repay by teaching the next generation where it came from |
| **Relationship to CREDITS.md** | N/A | CREDITS.md is the registry (§1.x sections). [id-soft:] tags are the code-level attribution. Both must exist. |

**Attribution format**: `[Id-Soft Attribution: CREDITS.md §2a, 2026]`

---

### 1.12 8-Character Name Caps (REJECTED, 2026)

| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | `w_wad.c:170-178` (DOOM 1993) — WAD lump names capped at 8 chars | **REJECTED** — cargo-cult optimization; removed |
| **Core idea** | Cap names at 8 bytes → fit in 2 × int32 → compare with 2 instructions instead of strcmp | Python dicts are O(1) by hash. The 2-int compare trick does not accelerate Python code. |
| **Mechanism** | `if (*(int *)lump_p->name == v1 && *(int *)&lump_p->name[4] == v2)` — 1 CPU line | N/A — never should have been implemented |
| **Speed** | ~2-4x faster than strcmp on 35 MHz 386 | Zero benefit in Python. The "optimization" doesn't exist. |
| **Result** | ❌ **REJECTED after Heritage Vetting Pipeline review** | Removed in commit `8b3fc17`. Lesson: hardware-specific optimizations don't transfer to Python. |
| **Verification** | Verified at `DOOM-master/linuxdoom-1.10/w_wad.c:376-382` — backward scan uses 2-int compare | N/A |

**Attribution format**: `[8-Char Name: id Software 1993 — REJECTED for Omega]`
**Inline tag format**: N/A — no `[id-soft:]` tags were ever committed
**Lesson**: The entire vet record is at `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md#vet-001`.

---

### 1.13 cvar Table (Promoted, 2026)

| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | `cvar.c:24-224` (Quake 1, 1996) + `cvar.c:187-279` (Q3A, 1999) | `src/omega/cvar_table.py` — `CvarDef {name, default_value, flags, modification_count}` |
| **Quake 1** | Linked list, `cvar_t {name, string, archive, server, value, next}` — linear scan on every lookup | Named constant registry with `zoneid.*` and `config.*` namespaces |
| **Q3A evolution** | `MAX_CVARS=1024` fixed array + `hashTable[256]` for O(1) lookup + `modificationCount` for change detection | `CvarTable` class with `__getitem__`, `__setitem__`, `modify()` incrementing counter |
| **Flags** | `CVAR_ARCHIVE=1, CVAR_USERINFO=2, CVAR_SERVERINFO=4, CVAR_NODEFAULT=8, CVAR_LATCH=64, CVAR_ROM=128, CVAR_NORESTART=1024` | `CONFIG_ARCHIVE=1, CONFIG_READONLY=2, CONFIG_LATCH=4, CONFIG_NORESTART=8` |
| **Infrastructure** | `Cvar_Register()` at engine init — all cvars registered before use | `register_cvars()` called at module import — all constants available immediately |
| **Status** | **PROMOTED** — implemented as cvar_table.py. All zoneid.* and config.* namespaces unified. |

**Attribution format**: `[cvar System: id Software 1996/1999]`
**Inline tag format**: `# [id-soft: quake-1996] cvar pattern` or `# [id-soft: quake3-1999] cvar hash table`

---

### 1.14 4-Tier Memory Architecture (Mapped, 2026)

| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | `zone.h:24-80` (Quake 1, 1996) — Hunk (stack) / Zone (heap) / Cache (LRU) / Temp (transient) | `src/omega/memory_store.py` — Hot/Warm/Cold tiers + static allocation |
| **Memory layout** | Single contiguous block: low hunk → zone → temp → cache → high hunk | `HotMemoryTier` (dict, fast), `WarmMemoryTier` (SQLite, moderate), `ColdMemoryTier` (YAML, persistent) |
| **Hunk = Stack** | Fast push/pop, used for client + server allocations | Hot tier — O(1) dict operations, for active entity state |
| **Zone = Heap** | Tag-based allocator (`Z_Malloc` with PU_ tags), rover pointer merges free blocks | Warm tier — SQLite-backed, for recent entity memory |
| **Cache = LRU** | `Z_Malloc(PU_CACHE)` — purged when rover wraps or OOM | Cold tier — YAML on disk, for long-term persistence |
| **Temp = Transient** | Short-lived allocations, freed each frame | Not yet implemented — temporary inference results freed after response |
| **Purge levels** | `PU_STATIC=1, PU_SOUND=2, PU_LEVEL=50, PU_PURGELEVEL=100, PU_CACHE=101` | `HOT_TTL=300`, `WARM_TTL=3600`, `COLD_TTL=86400` — time-based instead of tag-based |
| **Omega evolution** | Static contiguous block → dynamic tiered storage with TTL-based promotion/demotion | id Software's physical memory model → logical tiered storage for LLM context |
| **Status** | **MAPPED** — formal correspondence documented. 4th tier (Temp) pending implementation. |

**Attribution format**: `[4-Tier Memory: id Software 1996]`
**Inline tag format**: `# [id-soft: quake-1996] 4-Tier Memory — description`

---

### 1.15 Multi-Index Entity / Dual-Linking (Mapped, 2026)

| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | `p_mobj.h:1-100` (DOOM 1993) — mobj_t is in sector list (rendering) + blockmap (collision) simultaneously | Entity dual-index in `entity_registry.py` — domain index (routing) + capability index (execution) |
| **Mechanism** | `sector_t.touching_thing_next` and `blocknode.next` — same mobj pointer in both lists | `_domain_index: Dict[str, str]` maps domain → entity key; `_capability_index: Dict[str, str]` maps capability → entity key |
| **Benefits** | O(1) sector lookup + O(1) collision lookup from a single mobj | O(1) domain routing + O(1) capability matching from a single Entity |
| **Lazy deletion** | Removing from sector list doesn't remove from blockmap (both checked by thinker sweeper) | `_remove_from_index()` checks both indices; `_is_tombstoned()` guards stale references |
| **Status** | **MAPPED** — pattern documented. Domain routing index live; capability index structure defined but not populated. |

**Attribution format**: `[Multi-Index Entity: id Software 1993]`
**Inline tag format**: `# [id-soft: doom-1993] Dual-Linking — description`

---

### 1.16 QuakeC Flat-Field Entity (Mapped, 2026)

| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | `QW/progs/progdefs.h:5-110` (Quake 1996) — C struct generated from QuakeC source | YAML entity definitions in `config/wads/*/entities.yaml` |
| **Core idea** | Data-driven entity schema: QuakeC source → qcc compiler → C struct header → linked into engine | YAML entity schema → Pydantic model → runtime dataclass |
| **Flat bag of fields** | All entity fields in one struct (no inheritance), typed via defs.h | All entity fields in one YAML dict, typed via defined schema |
| **Modding pattern** | Modders add new fields in QuakeC, recompile, new .dat — engine auto-reads new field sizes | Users add new fields to entities.yaml, engine auto-loads via schema validation |
| **Status** | **MAPPED** — pattern documented. Omega's entity system already follows this principle independently. |

**Attribution format**: `[QuakeC Entity: id Software 1996]`
**Inline tag format**: `# [id-soft: quake-1996] Flat Entity — description`

---

### 1.17 Hard-Boundary Struct (Promoted, 2026)

| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | `g_local.h:42-49` (Q3A 1999) — `entityState_t` (engine) + `entityShared_t` (game) separation | Entity zone model: `EngineZone` (__engine_zone__ sentinel) + `GameZone` (__game_zone__ sentinel) in `entity_registry.py:Entity` |
| **Engine zone** | `entityState_t` — owned by engine, "DO NOT MODIFY" comment enforced by convention | `Entity.__engine_zone__` — position, health, state — read-only for game logic |
| **Game zone** | `entityShared_t` — owned by game, freely modified | `Entity.__game_zone__` — traits, knowledge, model preferences — freely writable |
| **Boundary enforcement** | Comment-based: sections are visually separated with the DO NOT MODIFY warning | Sentinel attributes `__engine_zone__` and `__game_zone__` — `AttributeError` on cross-zone writes |
| **Status** | **PROMOTED** — sentinel attributes added to Entity class. Boundary enforcement via zone-aware property getters/setters. |

**Attribution format**: `[Hard-Boundary Struct: id Software 1999]`
**Inline tag format**: `# [id-soft: quake3-1999] Hard-Boundary — description`

---

### 1.18 4-Path Virtual Filesystem (Mapped, 2026)

| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | `files.c:39-75` (Q3A 1999) — base + cd + home + current game search order | WAD Loader search path in `wad_loader.py` |
| **Search order** | home/current → home/base → cd/current → cd/base → base/current → base/base | config/wads/<stack>/ → config/wads/_omega_default/ → data/entities/<entity>/ |
| **Override mechanism** | Later directories override earlier — mod files take precedence over base game | Later WAD entity definitions override earlier — PWAD overrides IWAD |
| **Addon pattern** | Mods work without modifying base game files | PWAD stacks work without modifying _omega_default IWAD |
| **Status** | **MAPPED** — pattern documented. Omega's WAD loader already follows this pattern (IWAD/PWAD separation). Formal 4-tier expansion pending. |

**Attribution format**: `[4-Path VFS: id Software 1999]`
**Inline tag format**: `# [id-soft: quake3-1999] VFS — description`

---

### 1.19 High-Bit Leaf Trick (Promoted, 2026)

| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | `doomdata.h:124-138` (DOOM 1993) — `NF_SUBSECTOR = 0x8000` high bit on node child index | Entity flag high bit: `FLAG_SYSTEM = 0x80000000` on `Entity.flags` integer |
| **Core idea** | High bit of 16-bit index = "this is a subsector, not a node" — saves 1 byte per node, 1-line check | High bit of 32-bit flags = "this is a system entity" — saves 1 boolean field, 1-line check |
| **Compare** | `if (child & NF_SUBSECTOR)` — single AND instruction | `if entity.flags & FLAG_SYSTEM` — single bitwise AND |
| **Benefit** | 1 line instead of 2 (no `if (is_subsector)` separate variable) | 1 field instead of 2 (no separate `is_system: bool` boolean) |
| **Status** | **PROMOTED** — `FLAG_SYSTEM=0x80000000` defined in entity flags. All system entities use high-bit marker. |

**Attribution format**: `[High-Bit Trick: id Software 1993]`
**Inline tag format**: `# [id-soft: doom-1993] High-Bit Trick — description`

---

### 1.20 Fixed-Size Active Set (Mapped, 2026)

| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | `r_bsp.c:74-78` (DOOM 1993) — `MAXVISPLANES = 32` — BSP drawer clips to 32 active visplanes | Active provider set in `model_gateway.py` — `_active_providers: List[str]` (max 32) |
| **Core idea** | Fixed-size 32-entry array of visplanes — fits in L1 cache (256 bytes), O(1) iteration | Fixed-size 32-entry list of active provider names — O(1) culling before inference |
| **Cache efficiency** | 32 × 8 bytes = 256 bytes = L1 cache line | 32 × ~40 bytes (Python object overhead) = ~1280 bytes — larger but O(1) lookup |
| **Culling effect** | Only render what's visible — skip non-visible sectors | Only try providers that are healthy — skip broken providers |
| **Status** | **MAPPED** — pattern documented. Active set structure defined in model_gateway.py; fixed 32-entry limit pending enforcement. |

**Attribution format**: `[Active Set: id Software 1993]`
**Inline tag format**: `# [id-soft: doom-1993] Active Set — description`

---

### 1.21 Network Channel (netchan) Protocol (Quake III, 1999)

| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | `net_chan.c:35-235` (Q3A 1999) — Out-of-band (OOB) messages, fragmentation, and qport NAT remapping | MCP Hub transport layer in `mcp_servers/omega_hub/server.py` |
| **OOB Messages** | Sequence number `-1` bypasses stateful channel for lightweight queries (ping, status) | Separate stateless HTTP POST endpoints from stateful SSE channels |
| **Fragmentation** | Split messages exceeding 1400-byte MTU into sequential fragments | AnyIO-native streamable chunking for large context snapshots |
| **qport Workaround** | Embed unique `qport` to re-associate connection if NAT remaps client port mid-game | Embed unique `session_id` token in headers to re-associate connection if IP changes |
| **Status** | **MAPPED** — pattern documented. MCP Hub transport already follows these principles. |

**Attribution format**: `[netchan Protocol: id Software 1996/1999]`
**Inline tag format**: `# [id-soft: quake3-1999] netchan — description`

---

### 1.22 Unified Memory Allocator (idHeap) (DOOM 3, 2004)

| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | `Heap.cpp:45-143` (DOOM 3, 2004) — 3-tier allocator (Small/Medium/Large) + Defrag Block hack | Tiered Memory Store in `src/omega/memory_store.py` + `ResourceGuard` |
| **Small Allocator** | 1–255 bytes, pre-allocated free-list buckets, $O(1)$ zero search overhead | `HotMemoryTier` — fast, in-memory dictionary for active states |
| **Medium Allocator** | 256–32,768 bytes, page-based allocator with block merging | `WarmMemoryTier` — SQLite database for recent summarized history |
| **Large Allocator** | >32,768 bytes, bypasses heap, allocates directly from OS | `ColdMemoryTier` — YAML files on disk or vector embeddings in Qdrant |
| **Defrag Block** | Single massive block allocated at startup, freed during heavy tasks to guarantee memory | `ResourceGuard` — AnyIO `Semaphore(1)` to prevent OOM crashes on Ryzen 5700U |
| **Status** | **MAPPED** — pattern documented. 3-tier memory store and ResourceGuard live. |

**Attribution format**: `[Unified Memory: id Software 2004]`
**Inline tag format**: `# [id-soft: doom3-2004] idHeap — description`

---

### 1.23 Fixed-Point Math (DOOM, 1993)

| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | `m_fixed.c:43-87` (DOOM 1993) — 16.16 fixed-point format, bit-shift multiplication, division guard | CPU Optimizer in `src/omega/oracle/cpu_optimizer.py` + Quantization |
| **Fixed-Point** | Represent real numbers as 32-bit integers to bypass slow software FPU emulation | Integer-quantized GGUF models (Q4_K_M / Q8_0) to bypass slow FP16/FP32 matrix math |
| **Bit-Shift Mul** | Cast to 64-bit, multiply, bit-shift right by 16 (`>> 16`) | Zen 2 AVX2 vectorization flags (`-march=znver2 -mavx2 -mfma`) for fast integer math |
| **Division Guard** | Fast bit-shift check to detect overflow/divide-by-zero before execution | KV cache quantization flags (`-ctk q8_0 -ctv q8_0`) to prevent memory bottlenecks |
| **Status** | **MAPPED** — pattern documented. Quantization and AVX2 compilation flags live. |

**Attribution format**: `[Fixed-Point Math: id Software 1993]`
**Inline tag format**: `# [id-soft: doom-1993] Fixed-Point — description`

---

### 1.24 Hivemind Message Types (Netchan Heritage, 2026)
| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | `net_chan.c:35-235` (Q3A 1999) — netchan protocol | H-13 typed message system in `mcp_servers/omega_hub/server.py` |
| **Core idea** | OOB + reliable sequencing + qport remapping | Continuation + decision thread + handoff |
| **Omega evolution** | UDP over IP network | Hivemind pub/sub over MCP transport |
| **Status** | MAPPED | H-13 ship in Phase 5 (P9 owns) |

**Attribution format**: `[netchan Protocol: id Software 1996/1999]`

---

### 1.25 Sovereign-Siloing (Doom, 1993)
| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | `w_wad.c` (DOOM 1993) — WAD system | Engine-Stack Firewall (Mandate 2) |
| **Core idea** | Absolute separation of engine binary and WAD data | Strict separation of `src/omega/` and `config/wads/` |
| **Omega evolution** | Binary WAD $\rightarrow$ YAML-backed IWAD/PWAD | Human-editable, hot-reloadable |
| **Status** | MAPPED | Core Engine Mandate |

**Attribution format**: `[Sovereign-Siloing: id Software 1993]`

---

### 1.26 Lattice-Culling (Doom, 1993)
| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | `r_bsp.c` (DOOM 1993) — BSP trees | Provider culling in ModelGateway.generate() |
| **Core idea** | Precompute visibility planes; O(1) test skips entire subtrees | O(1) circuit breaker check skips broken providers |
| **Omega evolution** | Static geometry $\rightarrow$ dynamic provider health | Circuit breaker state changes over time |
| **Status** | MAPPED | ModelGateway implementation |

**Attribution format**: `[Lattice-Culling: id Software 1993]`

---

### 1.27 Sovereign-Symmetry (Quake, 1996)
| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | `zone.c` (Quake 1996) — mirrored state | MaKaLi Triad Architecture |
| **Core idea** | Dual-inference / mirrored state for stability and verification | Synthesis of Light (Ma'at) + Dark (Lilith) Oversouls via Kali |
| **Omega evolution** | Mirroring for rendering $\rightarrow$ Cognitive synthesis | MaKaLi Triad governance |
| **Status** | MAPPED | Engine Governance |

**Attribution format**: `[Sovereign-Symmetry: id Software 1996]`

---

### 1.28 Sovereign-Symmetry (Quake III, 1999)
| Aspect | id Software Original | Omega Engine Adaptation |
|--------|--------------------|------------------------|
| **Origin** | `g_local.h` (Q3A 1999) — local-first primary | Dual-Inference Mandate (D118) |
| **Core idea** | Local-first primary with cloud-fallback safety net | `native-gguf` $\rightarrow$ `Google` $\rightarrow$ `OpenCode` provider chain |
| **Omega evolution** | Local rendering $\rightarrow$ Local inference | Mandate 7 (Local-First) |
| **Status** | MAPPED | Provider Fabric implementation |

**Attribution format**: `[Sovereign-Symmetry: id Software 1999]`

---

*Last Updated: 2026-06-05 (added §1.24-1.28 Heritage Mappings) | Maintained by: Kali / Doom Guy*

