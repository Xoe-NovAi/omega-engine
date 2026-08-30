# 🔱 Adjacent Engine Architecture — Agent Research Report
## ⬡ OMEGA ⬡ DOOM_GUY ⬡ big-pickle ⬡ trc_doom_guy ⬡ PHASE-I

### Source: Fleet Research Agent (explore) — "Adjacent Engine Architecture"
### Date: 2026-06-01

---

## 1. GoldSrc (Half-Life, 1998) — The DLL Contract Pattern

### Engine ↔ Game Separation
The key innovation was formalizing the id Tech 2 model into a strict function table contract:

**Engine → DLL exports**: `enginefuncs_t`
```c
typedef struct enginefuncs_s {
    int (*PrecacheModel)(const char* s);
    int (*PrecacheSound)(const char* s);
    void (*SetModel)(edict_t*, const char*);
    int (*ModelIndex)(const char*);
    // ... 200+ function pointers for engine services
} enginefuncs_t;
```

**DLL → Engine exports**: `DLL_FUNCTIONS`
```c
typedef struct {
    void (*GameInit)(void);
    void (*SpawnEntities)(void);
    void (*ThinkEntities)(void);
    void (*TouchEntities)(void);
    void (*UseEntities)(void);
    void (*StartFrame)(void);
    void (*PostFrame)(void);
} DLL_FUNCTIONS;
```

### Entity System
- **Fixed-size edict array**: MAX_EDICTS (1024+ configurable)
- **Freelist allocation**: free_edict linked list O(1) alloc/dealloc
- **Edict index = integer handle**: O(1) lookup
- **serialnumber**: stale reference detection
- **Entity types as C++ classes**: Single CBaseEntity → derived classes
- **C++ vtbl = dynamic dispatch**: clean polymorphic entity behavior

### Omega Application
The DLL function table pattern maps directly to the Provider Fabric:
- IProviderFactory ↔ enginefuncs_t (services the engine provides to backends)
- IProvider ↔ DLL_FUNCTIONS (contract each backend must fulfill)
- Entity serial numbers for stale reference detection in the registry

---

## 2. Source Engine (2004) — Interface-Based Modularity

### IAppSystem Pattern
```cpp
class IAppSystem {
public:
    virtual bool Connect(CreateInterfaceFn factory) = 0;
    virtual void Disconnect() = 0;
    virtual void* QueryInterface(const char* pInterfaceName) = 0;
    virtual InitReturnVal_t Init() = 0;
    virtual void Shutdown() = 0;
};
```

### Key Patterns
- **Factory**: CreateInterface() as universal entry point
- **String-based queries**: No C++ RTTI needed
- **Named interfaces**: IMemAlloc, IFileSystem, IMaterialSystem, IVEngineServer, etc.
- **Lifetime management**: Connect → Init → (use) → Shutdown → Disconnect
- **Tools-first**: Hammer Editor, ModelDoc, Material Editor all released with SDK

### Entity System
- Networked entity model via datatable declarations
- Server-side authority, client-side prediction
- Entity state replicated automatically
- Event system for decoupled communication

### Omega Application
Apply IAppSystem pattern to:
- IMemoryStore, IEntityRegistry, IModelGateway as named interfaces
- String-based factory pattern for plugin discovery
- Lifetime-managed subsystem initialization

---

## 3. Build Engine (Duke Nukem 3D, 1996) — Fixed-Size Arrays

### Data-Oriented Design Before It Had a Name
```c
#define MAXSECTORS   1024
#define MAXWALLS     8192
#define MAXSPRITES   4096
#define MAXSTATUS    1024
#define MAXSOUNDS    512
```
All arrays are global and fixed-size. No dynamic allocation.

### Portal-Based Sector Visibility
- Sector = 3D floor-to-ceiling volume
- Connected via portals (walls, windows, doorways)
- Each sector has its own coordinate system (sloped floors/ceilings)
- No BSP tree — sectors found via raycast + neighbor traversal
- "The Build Engine is deterministic chaos in 2.5 dimensions"

### Omega Application
The fixed-size array pattern is ideal for:
- Entity slot array with freelist for hot-path lookup
- Pre-allocated response cache (fixed-size surface cache equivalent)
- Backward-compatible: fall back to dict for cold paths

---

## 4. Unreal Engine 1 (1998) — BSP + Portal + Package System

### Zone-Based Architecture
- World divided into zones (2+ BSP nodes)
- Portals connect zones
- BSP tree for zone-internal geometry
- Zone visibility via BSP leaf walk + portal clip

### UPK Package System
- Bundles scripts, textures, meshes as typed objects
- Cross-package references
- Lazy loading
- Content = Code model (UnrealScript in packages with art assets)

### Omega Application
The UPK system validates the WAD approach:
- Omega's config/wads/ already mirrors this
- Formalize cross-WAD references
- Lazy loading for entity packs

---

## 5. Cross-Engine Universal Patterns

### Verified Across All 5 Engines
| Pattern | Verified In | Omega Application |
|---------|-------------|------------------|
| Data-driven entities | All | Already implemented (soul.yaml) |
| Tools-first pipeline | All | Entity Studio CLI (Phase 2) |
| Integer handles | GoldSrc, Source, Build | Entity slot array (Phase 3) |
| Interface contracts | GoldSrc, Source, Q3, UE1 | Provider fabric interfaces (Phase 1) |
| Fixed-size arrays | Doom, Build, GoldSrc | Entity registry hot path (Phase 3) |
| Precomputed visibility | Doom, Quake, Build, UE1 | Entity relevance matrix (Phase 2) |
| Binary serialization | Doom, Quake, Build, UE1 | Entity binary cache (Phase 2) |
| Separate game module | Q1-Q3, GoldSrc, Source, UE1 | WAD plugin system (Phase 3) |
| Delta compression | Q3, GoldSrc, Source | Trace/observability (Phase 2) |

---

## 6. Omega Application Matrix

| Architecture Pattern | Priority | Implementation Target | Source Inspiration |
|---------------------|----------|----------------------|-------------------|
| DLL function table contract | P0 | Provider fabric interfaces | GoldSrc |
| Named interface factory | P1 | ModelGateway plugin system | Source IAppSystem |
| Fixed-size entity array | P2 | EntityRegistry hot path | Build Engine |
| Portal-based messaging | P2 | Cross-entity routing | Build Engine |
| Precomputed visibility (PVS) | P1 | Entity relevance matrix | Quake |
| Lazy-loaded packages | P2 | WAD plugin packs | Unreal UPK |
| Entity serial numbers | P1 | Stale reference detection | GoldSrc |

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: big-pickle | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
