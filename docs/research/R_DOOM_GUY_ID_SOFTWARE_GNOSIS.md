---
id: "R-DOOM-GUY-ID-SOFTWARE-GNOSIS"
title: "id Software Architectural Gnosis — Omega Engine Translation"
status: "✅ Complete"
urgency: "🔴 Critical"
tags:
  - core-engine
  - soul-architecture
  - provider-fabric
  - inference-optimization
  - legacy-mining
  - strategic-alignment
  - mcp-ecosystem
  - entity-design
  - hardware-tuning
created: "2026-06-01"
updated: "2026-06-01"
related:
  - "R_DOOM_WAD_DEEP_RESEARCH"
source: "Internal/Legacy/Web"
files:
  - "data/entities/doom_guy/soul.yaml"
  - "data/entities/doom_guy/workspace/id_software_research/philosophy/id_software_philosophy_report.md"
  - "data/entities/doom_guy/workspace/id_software_research/architecture/id_tech_architecture_report.md"
  - "data/entities/doom_guy/workspace/id_software_research/methodology/id_development_methodology_report.md"
  - "data/entities/doom_guy/workspace/id_software_research/resources/downloadable_resources_inventory.md"
  - "data/entities/doom_guy/workspace/id_software_research/engine_comparisons/adjacent_engine_architecture_report.md"
  - "scripts/download_id_tech_resources.sh"
summary: "Systematic extraction of id Software's architectural, philosophical, and methodological principles — including adjacent engines (GoldSrc, Source, Build, Unreal) — distilled into L1→L2→L3 gnosis and mapped to concrete Omega Engine implementation targets."
---

# 🔱 Omega Engine — id Software Architectural Gnosis

⬡ OMEGA ⬡ DOOM_GUY ⬡ big-pickle ⬡ opencode ⬡ trc_doom_guy ⬡ PHASE-I

## 🎯 Objective

Extract the architectural, philosophical, and methodological DNA of id Software (1989-2016) and its engine contemporaries (GoldSrc, Source, Build, Unreal 1) — then translate these patterns into concrete implementation strategies for the Omega Engine. The goal is not nostalgia; it is to give the Omega Engine the same ruthless efficiency, data-driven purity, and sovereign minimalism that made id's engines industry-defining.

## 🔍 Methodology

- [x] **Legacy Mining**: Reclaimed patterns from id Software source code releases (Doom, Quake, Quake II, Quake III, Doom 3, id Tech 4), adjacent engine source code (GoldSrc leak, Build Engine, Unreal 1), and Abrash's Graphics Programming Black Book.
- [x] **Web Synthesis**: Key findings from Exa, Brave, and Firecrawl searches across Fabien Sanglard's analyses, Charles Boury's research, and id Software historical documentation.
- [x] **Dialectic Triangulation**: Analysis of 5 research agents working in parallel across philosophy, architecture, methodology, resources, and adjacent engines.
- [x] **Empirical Pattern Matching**: Cross-reference between proven engine patterns and Omega Engine's current architecture.

---

## 📚 Findings & Analysis

### L3: Raw Signal — The Source Material

#### id Software Philosophy (Core Texts & Interview Corpus)

**Richard Gabriel "Worse is Better" (1989)**
The foundational philosophy that shaped id Software. The "New Jersey Approach" contrasted with MIT's "Right Thing":
- Simplicity of implementation > Simplicity of interface
- Correctness > Consistency
- Completeness > Simplicity of interface
- 50% solution that works beats 90% solution that never ships

**John Carmack — Focus and .plan Archive**
- "Focus is a matter of deciding what things you're not going to do."
- "Sometimes, the fastest way to solve a problem is to not have it in the first place."
- .plan updates from 1996-2005: public daily/weekly engineering logs
- "Wait on the planning – now it's coding time." — response to "Carmack's Law" meme

**John Romero — 10 Programming Principles**

| # | Principle | Essence |
|---|-----------|---------|
| 1 | No prototypes | Only ship-quality code, even in early builds |
| 2 | Shippable code rules | It must compile, run, and be playable at all times |
| 3 | It's the data | Great tools produce great games |
| 4 | Fix bugs immediately | No backlog accumulation |
| 5 | Code for this game | Don't write a generic engine — write a game |
| 6 | The tool shapes the product | DoomEd shaped Doom more than the engine |
| 7 | Know what to keep vs discard | Id's four OS boots in 18 months |
| 8 | Master your tools | Emacs, vi, debuggers — know them cold |
| 9 | Focus = no feature creep | Resist feature creep ruthlessly |
| 10 | Know the player | Test and iterate with real user feedback |

**Adrian Carmack / Kevin Cloud / American McGee**
- Artists as first-class engine designers
- Doom's visual style (dark, gritty, hellish) drove technical direction (colored lighting, limited palette)
- The art shaped the engine as much as the engine shaped the art

#### id Tech Architecture (Source Code + Abrash Black Book)

**Doom Engine (1993) — Binary WAD System**

WAD Format (paraphrased from source):
```c
// WAD Header — 12 bytes
typedef struct {
    char  identification[4];   // "IWAD" or "PWAD"
    int   numlumps;            // Number of entries
    int   infotableofs;        // Offset to directory
} wadinfo_t;

// Directory Entry — 16 bytes each
typedef struct {
    int   filepos;             // Offset to lump data
    int   size;                // Size of lump
    char  name[8];             // 8-char name, null-padded
} filelump_t;
```

**Key insight**: Backward scan lookup in `W_CheckNumForName`:
```c
for (i = wad->numlumps - 1; i >= 0; i--) {
    if (!strncasecmp(..., wad->lump[i]->name, 8))
        return i;  // Returns LAST match — PWAD wins
}
return -1;
```

**BSP Trees (Doom, 1993)**:
- Node-based 2D BSP for sector partitioning
- SSectors (subsectors) reference segs (line segments)
- REJECT map: precomputed sector-to-sector visibility (same concept as PVS for 2.5D)
- Primary purpose: supersector detection for sound propagation + rendering order

**Quake 3D BSP (1996)**:
- 3D BSP tree partitioning world into convex polygons
- PVS (Potentially Visible Set): precomputed visibility per BSP leaf
- Store as bit vector: 1 byte = 8 leaves
- Visibility = O(1) bit check at runtime
- Carmack tried beam trees, portals, direct BSP — all failed. PVS worked because it was a *cache strategy*, not an algorithm.

**Fast Inverse Square Root (Quake III, 1999)**:
```c
float Q_rsqrt(float number) {
    long i;
    float x2, y;
    const float threehalfs = 1.5F;
    x2 = number * 0.5F;
    y  = number;
    i  = * (long *) &y;           // evil floating point bit level hacking
    i  = 0x5f3759df - (i >> 1);   // what the fuck?
    y  = * (float *) &i;
    y  = y * (threehalfs - (x2 * y * y));  // 1st iteration Newton
    return y;
}
```
- 4x faster than FPU-based approach
- 0.175% maximum relative error
- One Newton-Raphson iteration was good enough
- Magic constant 0x5f3759df found via trial, error, and brute force search

**Surface Caching (Quake, 1996)**:
Three-layer architecture for rendering in 320×200 with 4MB RAM:
1. **Precomputation**: Lightmaps baked offline at ~16-texel resolution
2. **Caching**: Surface cache stores recently used texture+lightmap combinations
3. **Runtime**: Rasterizer tiles cached surfaces onto screen pixels
- Cache hit > 90% in typical gameplay
- When RAM ran out, oldest surfaces evicted
- "All programming is an exercise in caching" — Terje Mathisen

**Data-Driven Architecture (All Eras)**:
- Doom: WAD lumps + DeHackEd for runtime patching
- Quake: QuakeC bytecode (game logic as compiled C subset)
- Quake II: Native game DLLs (gamex86.dll)
- Quake III: QVM system — LCC cross-compiler + q3asm linker → platform-independent bytecode + optional native DLL fast-path
- id Tech 4/5: Object-oriented entity system with declarative entity definitions

**Memory Management**:
- **Zone allocator**: Permanent allocations (z_malloc). Fixed-size, never freed per-level.
- **Hunk allocator**: Temporary allocations (Hunk_Alloc). Linear bump allocator, freed as a whole. Tag-based (hunk_low, hunk_high, hunk_static, hunk_temp).
- **Cache subsystem**: Eviction-based. Oldest entries freed under memory pressure.

**Network Model (Quake III)**:
- Client-server architecture (not peer-to-peer like Doom)
- Delta compression: send only changed fields between snapshots
- Entity state with serial index numbers for stale reference detection
- Single algorithm handles: full updates, partial updates, packet loss, retransmission

**Job System (id Tech 5, 2011)**:
- Task-based multithreading with dependency graph
- 1-frame latency: jobs get one frame to complete
- Results appear one frame behind
- Player-facing systems exempted (16ms delay too noticeable)
- Job lists: sorted lists of job entries for cache-coherent iteration

#### Development Methodology

**The "No Prototypes" Principle**:
- id's code was always shippable — even during R&D phases
- Quake was playable from the first week of development
- Design by playtesting, not by document

**The Tools-First Pipeline**:
| Game | Tool | What It Did |
|------|------|-------------|
| Doom | DoomEd | First tile-based 3D level editor |
| Quake | QEd / WorldCraft | 3D BSP level editor |
| Quake II | TAE (in-house) | Animation + model system |
| Quake III | Q3Radiant | Official level editor |
| Doom 3 | DoomEdit | Tile-based editor integrated with engine |

**The .plan Culture**:
- Carmack published daily technical updates on id's FTP server
- Unfiltered: bugs, dead ends, design debates, technical deep dives
- Romero posted plans for levels, tools, architecture
- Result: complete archive of design intent spanning 10 years
- Still studied by game developers and historians

**Open Source Strategy (Planned, Incremental, Impactful)**:
- 1997: Doom source released under GPL (community formed)
- 1999: Quake source released under GPL (Linux gaming catalyst)
- 2001: Quake II source GPL (mod community explosion)
- 2005: Quake III source GPL (academic standard)
- 2011: Doom 3 source GPL (id Tech 4 era)
- Pattern: release 1-2 generations behind current tech. Community catches up, maintains, and creates new content for 30+ years.

#### Adjacent Engine Architectures

**GoldSrc (Half-Life, 1998) — The DLL Contract Pattern**

Engine ↔ Game separation via function tables:

```c
// Engine exports to game DLL (enginefuncs_t)
typedef struct enginefuncs_s {
    int (*PrecacheModel)(const char* s);
    int (*PrecacheSound)(const char* s);
    void (*SetModel)(edict_t*, const char*);
    int (*ModelIndex)(const char*);
    int (*ModelFrames)(int);
    // ... 200+ function pointers
} enginefuncs_t;

// Game exports to engine (DLL_FUNCTIONS)
typedef struct {
    void (*GameInit)(void);
    void (*SpawnEntities)(void);
    void (*ThinkEntities)(void);
    void (*TouchEntities)(void);
    void (*UseEntities)(void);
    void (*StartFrame)(void);
    void (*PostFrame)(void);
    // ... entity lifecycle hooks
} DLL_FUNCTIONS;
```

Entity system:
- Fixed-size edict array (MAX_EDICTS = 1024 × 4 configurable)
- Freelist allocation (free_edict linked list)
- Edict index = integer handle (O(1) lookup)
- serialnumber field for stale reference detection

**Source Engine (2004) — Interface-Based Modularity**

```cpp
// Every major subsystem behind a pure virtual interface
class IAppSystem {
public:
    virtual bool Connect(CreateInterfaceFn factory) = 0;
    virtual void Disconnect() = 0;
    virtual void* QueryInterface(const char* pInterfaceName) = 0;
    virtual InitReturnVal_t Init() = 0;
    virtual void Shutdown() = 0;
};
```

Key architectural patterns:
- **Factory pattern**: CreateInterface() as universal entry point
- **Tool-first**: Hammer Editor, ModelDoc, Material Editor — all released with SDK
- **Networked entity model**: Entity state replicated automatically via datatable declaration
- **RTTI-free**: String-based interface queries, not C++ RTTI

**Build Engine (Duke Nukem 3D, 1996) — The Old-School Speed Demon**

Fixed-size arrays:
```c
#define MAXSECTORS   1024
#define MAXWALLS     8192
#define MAXSPRITES   4096
#define MAXSTATUS    1024
#define MAXSOUNDS    512
// Global arrays from HEADS.H
```

Portal-based sector visibility:
- Sector = 3D floor-to-ceiling volume
- Connected via portals (walls/windows/doorways)
- Each sector has its own coordinate system (sloped/floors/ceilings if needed)
- No BSP tree — sectors found via raycast → hit detection → neighbor traversal
- "The Build Engine is deterministic chaos in 2.5 dimensions"

**Unreal Engine 1 (1998) — The BSP + Portal Hybrid**

Zone-based architecture:
- World divided into zones (2+ nodes = zone)
- Portals connect zones together
- BSP tree for zone-internal geometry
- Zone visibility computed via BSP leaf walk + portal clip
- "Unreal was a mix of everything represented architecturally by a BSP tree system"

Package system (UPK format):
- Bundled scripts (UnrealScript bytecode), textures, meshes as typed objects
- Cross-package references resolved at load time
- Lazy loading: referenced packages loaded on demand
- Content = Code model: UnrealScript shipped in packages alongside art assets

#### Cross-Engine Universal Patterns (Validated Across All 5)

| Pattern | Doom | Q1 | Q3 | GS | Src | Bld | UE1 |
|---------|------|----|----|----|-----|-----|-----|
| Data-driven entities | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Tool-first pipeline | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Integer entity handles | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ |
| Interface contracts | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ✅ |
| Fixed-size arrays | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ |
| Precomputed visibility | ✅(REJECT) | ✅(PVS) | ✅(PVS) | ❌ | ❌ | ✅(loop) | ✅(zone) |
| Binary serialization | ✅(WAD) | ✅(PAK) | ✅(PK3) | ❌ | ✅(VTF) | ✅(GRP) | ✅(UPK) |
| Separate game module | ❌ | ✅(QC) | ✅(QVM/DLL) | ✅(DLL) | ✅(DLL) | ❌ | ✅(UC) |
| Delta compression | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Modding as architecture | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

### L2: Architectural Insights — Omega Engine Translation Matrix

#### Translation Matrix: id Software Pattern → Omega Engine Implementation

| id Pattern | Omega Implementation | Priority | Effort |
|------------|---------------------|----------|--------|
| **WAD Backward-Scan Lookup** | EntityRegistry scans backward so PWAD entities override IWAD entities | P0 | Low |
| **Binary WAD Format** | Add binary entity serialization for hot-path lookups | P1 | Medium |
| **Precomputed PVS** | Entity relevance matrix: precompute entity-to-entity 'visibility' for routing | P1 | Medium |
| **GoldSrc DLL Function Table** | IProviderFactory interface for all provider backends | P0 | Low |
| **Source IAppSystem Interface** | IMemoryStore, IEntityRegistry as pure virtual interfaces | P1 | Low |
| **Fixed-Size Entity Arrays** | Pre-allocated entity slot array with freelist | P2 | Medium |
| **QuakeC/QVM Bytecode** | Sandboxed plugin system for third-party entity packs | P3 | High |
| **Surface Caching (3-layer)** | Response caching layer: template cache + context cache + output cache | P1 | Medium |
| **Build Engine Sector Portal** | Cross-entity message routing via sector-like broadcast zones | P2 | Medium |
| **Delta Compression (Q3)** | Trace/observability delta encoding for entity state transfer | P2 | Medium |
| **Job System + 1-frame latency** | Async inference pipeline with latency budgeting | P1 | High |
| **.plan Culture** | Public engineering log (monthly updates) | P3 | Low |
| **Modding as Architecture** | WAD API + plugin manifest standard | P1 | Medium |
| **Tools-First** | Entity Studio CLI before adding complexity | P1 | Medium |
| **No Prototypes** | Every PR must pass make test | P0 | Low |
| **Worse is Better** | Ship with 80% solution, iterate in public | P0 | N/A |

#### Detailed Architecture Maps

**1. The WAD Firewall → Omega Engine-Stack Separation**

The Omega Engine already implements this via `config/wads/<stack_name>/` but can learn from id's binary format:
- **Lump namespace**: WAD uses 8-char names with no path hierarchy. Omega already has richer path-based organization.
- **IWAD vs PWAD**: The single byte that enables all modding. Omega's `entities.yaml` should distinguish base entities (IWAD) from overrides (PWAD).
- **Backward scan**: PWAD wins by positioning. An entity name collision should resolve to the last registered stack.
- **Binary packing**: For performance-critical entity data (response templates, routing tables), precompile to binary format.

**2. Precomputed Entity Relevance → The Omega PVS System**

Quake's PVS gave O(1) visibility at runtime by precomputing leaf-to-leaf visibility. For Omega:
- Precompute entity-to-entity relevance matrix offline (or during WAD loading)
- Store as bit vector: each entity row is a bitmask of relevant entities
- At query time: O(1) lookup of relevant entities given current context entity
- Cache the top-K relevant entities for fast dispatch
- Update: rebuild matrix on WAD change (entity load/unload)

**3. GoldSrc DLL Contract → Provider Fabric Architecture**

Current Omega Provider Fabric implements an implicit provider chain. Formalize to GoldSrc contract pattern:

```python
# IProviderFactory — the enginefuncs_t equivalent
class IProviderFactory(Protocol):
    """Contract between ModelGateway and provider backends."""

    async def create_provider(
        self, config: ProviderConfig
    ) -> ILLMProvider: ...

    async def validate(self) -> ProviderStatus: ...

# ILLMProvider — the DLL_FUNCTIONS equivalent
class ILLMProvider(Protocol):
    """Contract every provider must implement."""

    async def generate(
        self,
        messages: list[dict],
        model: str,
        **kwargs
    ) -> GeneratorResult: ...

    async def count_tokens(self, text: str) -> int: ...
```

**4. Surface Cache → Response Cache Architecture**

Three-layer response caching inspired by Quake's surface cache:

| Layer | What | Latency | Memory | Eviction |
|-------|------|---------|--------|----------|
| L1 Template Cache | Pre-encoded entity response templates | 0 (precomputed) | Static (soul.yaml) | Never |
| L2 Context Cache | Rendered responses per context window | ~10ms | Dynamic (RAM) | LRU |
| L3 Output Cache | Full model-generated responses | ~100ms-5s | Dynamic (disk? RAM?) | TTL + LRU |

**5. Job System + 1-Frame Latency → Async Inference Pipeline**

Apply id Tech 5's latency budgeting to parallel entity invocation:
- Entity jobs dispatched in parallel (up to ResourceGuard semaphore limit)
- Critical path responses (user-facing) get expedited priority: 1-cycle latency waived
- Non-critical responses (background analysis, enrichment) accept 1-cycle delay
- Job lists: batch entity invocations as sorted list for cache-coherent scheduling

**6. Fixed-Size Entity Arrays → Entity Registry Hot Path**

Build Engine's `sector[1024]` pattern for Omega's entity registry:
- Pre-allocate fixed-size entity slot array (configurable, default 256)
- Freelist linked list for O(1) allocation/deallocation
- Integer handles for O(1) lookup (no string key in hot path)
- Serial number for stale reference detection (GoldSrc serialnumber pattern)
- Fallback: dict-based lookup for cold paths (admin, CLI, etc.)

---

### L1: Executive Summary — The Five Laws of id Software that Shape Omega

1. **Worse is Better**: The Omega Engine ships with what works and iterates in public. Perfect architecture never ships. The provider fabric must have working local inference TODAY, not a perfect multi-backend routing system.

2. **Data-Driven Firewall**: The Engine knows nothing about content. WAD files (IWAD = base, PWAD = overlay) contain everything. Never add stack-specific entity logic to `src/omega/`. Pure separation.

3. **Precompute Everything**: Cache is strategy, not optimization. Precompute entity relevance, response templates, and routing tables offline. Runtime is for inference and interaction only.

4. **Interface Contracts for Everything**: Every subsystem behind a clearly defined interface (IProviderFactory, IMemoryStore, IEntityRegistry). Swap implementations without touching consumers. This is the Source Engine pattern applied to AI.

5. **Ship. Fix. Ship Better.**

---

## 🛠️ Implementation Blueprint

### Phase 1: Immediate (P0 — This Sprint)

| # | Task | Files | Test |
|---|------|-------|------|
| 1 | Formalize IProviderFactory + ILLMProvider interfaces in `providers.py` | `src/omega/oracle/providers.py` | `test_providers.py` |
| 2 | Add WAD origin tracking to EntityRegistry | `src/omega/oracle/entity_registry.py` | `test_entity_registry.py` |
| 3 | Implement backward-scan entity lookup per WAD namespace | `src/omega/oracle/entity_registry.py` | `test_entity_registry.py` |
| 4 | Add No-Prototypes quality gate: every PR must pass `make test` | CI config | CI pipeline |

### Phase 2: Strategic (P1 — Next Sprint)

| # | Task | Files | Test |
|---|------|-------|------|
| 5 | Precompute entity relevance matrix on WAD load | `src/omega/oracle/context_builder.py` | `test_context_builder.py` |
| 6 | Three-layer response cache (template/context/output) | `src/omega/oracle/cache.py` (new) | `test_cache.py` |
| 7 | Entity Studio CLI — tools-first entity editor | `src/omega/cli/entity_studio.py` (new) | `test_entity_studio.py` |
| 8 | WAD plugin manifest standard (for third-party entity packs) | `docs/architecture/WAD_PLUGIN_MANIFEST.md` | Review only |

### Phase 3: Advanced (P2-P3 — Future)

| # | Task | Files | Test |
|---|------|-------|------|
| 9 | Fixed-size entity slot array with freelist | `src/omega/oracle/entity_registry.py` | `test_entity_registry.py` |
| 10 | Job-list based parallel entity dispatch with latency budget | `src/omega/oracle/orchestrator.py` | `test_orchestrator.py` |
| 11 | Sandboxed entity plugin system (QVM-inspired) | `src/omega/plugins/` (new) | `test_plugins.py` |
| 12 | Public .plan engineering log | `docs/engineering_log/` | N/A |

---

## ⚖️ Risk & Uncertainty Register

| Risk | Impact | Mitigation Strategy |
|------|--------|---------------------|
| Over-engineering: The fixed-size array pattern is overkill for current entity count (< 20 entities) | Low | Implement as phased optimization. Hot-path pattern only when entity count exceeds 100. |
| PVS precomputation: Entity relevance matrix could be slow to build with many entities | Low | Build incrementally during WAD loading. O(n²) on entity count — acceptable for up to 1000 entities. |
| Binary serialization complexity adds maintenance burden | Medium | Phase 2. Text-based YAML remains primary format. Binary is hot-path cache only. |
| Modding as architecture might encourage extension over optimization | Low | Flag as WAD design pattern. Separate from core optimization work. |
| The Worse is Better philosophy could be used as excuse for sloppy code | Medium | Mitigate with Sovereign Mandate 9 (Error Integrity). No bare except. Every boundary typed. |

---

## ⚡ Resource Links (Downloadable)

| Resource | URL | Format | Size |
|----------|-----|--------|------|
| **Fabien Sanglard — Game Engine Black Book: Doom** | `https://fabiensanglard.net/gebbdoom/` | PDF/HTML | ~30MB PDF |
| **Fabien Sanglard — Game Engine Black Book: Wolfenstein 3D** | `https://fabiensanglard.net/gebw3d/` | PDF/HTML | ~20MB PDF |
| **Michael Abrash — Graphics Programming Black Book (full PDF)** | `https://github.com/jagregory/abrash-black-book/raw/master/pdf/Abrams_Graphics_Programming_Black_Book.pdf` | PDF | ~10MB |
| **id Software Doom Source (GitHub)** | `https://github.com/id-Software/DOOM` | Git | ~1MB |
| **id Software Quake Source (GitHub)** | `https://github.com/id-Software/Quake` | Git | ~3MB |
| **id Software Quake III Arena Source (GitHub)** | `https://github.com/id-Software/Quake-III-Arena` | Git | ~5MB |
| **id Software Quake II Source (GitHub)** | `https://github.com/id-Software/Quake-2` | Git | ~3MB |
| **id Software Doom 3 Source (GitHub)** | `https://github.com/id-Software/DOOM-3` | Git | ~50MB |
| **Chocolate Doom (clean Doom source port)** | `https://github.com/chocolate-doom/chocolate-doom` | Git | ~10MB |
| **Quake Tools (qcc, q3asm, etc.)** | `https://github.com/id-Software/Quake-III-Arena/tree/master/MP/code/tools` | Git | Included above |

---

*⬡ OMEGA ⬡ DOOM_GUY ⬡ big-pickle ⬡ opencode ⬡ trc_doom_guy ⬡ PHASE-I*
