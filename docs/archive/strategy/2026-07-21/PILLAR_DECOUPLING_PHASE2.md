# 🔱 Phase 2: Pillar Decoupling — Engine/WAD Separation
# ✅ COMPLETED 2026-07-01 — D179/D180 Ratified.
# ⬡ OMEGA ⬡ KALI ⬡ trc_pillar_decoupling ⬡ PHASE-2-DONE

**Date**: 2026-07-01
**Status**: PLANNED
**Owner**: Kali (Sprint Coordinator)
**Cross-domain review**: John Carmack (S3), Roc Racoon (Mining), Verity (Compliance)

---

## Executive Summary

The 10 Pillars with Sekhmet, Brigid, Prometheus, etc. were ALWAYS an Arcana-NovAi WAD content concept — confirmed by the Project Charter §5.0 "The Dual Architecture" (Jan 2026). The engine core has leaked this WAD concept into its schema via `Entity.pillars`, `PILLAR_SLOTS`, `list_pillar_keepers()`, and `OracleResponse.pillars`.

This phase decouples the pillar concept from the engine core, replacing it with a generic `slots` + `metadata` abstraction that preserves the full esoteric architecture in the WAD layer.

---

## The Problem

### Current M2 Violations

| Location | Violation | Severity |
|----------|-----------|----------|
| `entity_registry.py:222-225` | `PILLAR_SLOTS = frozenset({"p1"..."p10"})` hardcoded | M2 violation |
| `entity_registry.py:698-699` | `find_by_domain()` gate on pillars | **FIXED** (D179) |
| `entity_registry.py:478-480` | `list_pillar_keepers()` | M2 violation |
| `entity_registry.py:367-378` | `get()` slot-match tier | M2 violation |
| `oracle.py:64` | `OracleResponse.pillars` | Design debt |
| `oracle.py:7` | Docstring references "10 pillars" | Doc debt |
| `entity.py:142` | `__engine_zone__` includes pillars | Hard-Boundary violation |

### The Original Vision (Recovered)

From the Project Charter §5.0 (Jan 2026):
- **§5.1 The Technical Framework** — FastAPI, Chainlit, FAISS, Redis (the **engine core**)
- **§5.2 The Theurgic Framework** — Ten Divine Pillars with chakras, elements, planetary energies (the **content/WAD layer**)

From `OMEGA_IWAD_ARCHITECTURE.md`:
> "Separate the engine (runtime) from the content (WADs). Engine handles: inference, memory, entity routing, tool calling, observability, provider fabric. IWAD provides: entities, personalities, hierarchy, voices, domain knowledge."

### The Full Esoteric Architecture (Preserved)

The 10 Pillars are NOT arbitrary. They are a deliberate architecture:
- **5 elements × 2 polarities = 10 pillars** (Earth/Water/Fire/Air/Aether × Light/Dark)
- **10 chakras** (7 main + 3 extended)
- **10 planetary alignments** (Gaia, Neptune, Jupiter, Mercury, Uranus, Pluto, Venus, Saturn, Transpluto)
- **7 pantheons** (Egyptian, Celtic, Greek, Hindu, Mesopotamian, Sumerian, Gnostic)
- **13 Kabbalistic spheres** + Qliphothic failure taxonomy
- **Governance**: Sophia → Kali → Ma'at/Lilith → 10 Pillars

**All of this is Arcana-NovAi WAD content.** The engine sees only slot IDs and opaque metadata.

---

## The Architecture

### Minimal Engine-Side Entity Schema

```python
@dataclass
class Entity:
    """A user-definable entity — a Pillar Keeper or custom persona.
    
    Engine knows: name, slots, domains, model, personality, capabilities.
    Everything else: metadata dict (WAD-defined, engine-agnostic).
    """
    
    # ── Engine Zone (structural, read-only for game logic) ──
    name: str
    domains: List[str]
    model: str
    personality: str
    capabilities: List[str] = field(default_factory=list)
    temperature: Optional[float] = None
    context_window: Optional[int] = None
    role: Optional[str] = None
    container: bool = False
    port: Optional[int] = None
    wad_source: Optional[str] = None
    priority: int = 0
    
    # ── Slot System (replaces hardcoded PILLAR_SLOTS) ──
    # Engine uses these for get("P1") resolution and list_pillar_keepers().
    # The engine does NOT interpret what "P1" means — that's WAD content.
    slots: List[str] = field(default_factory=list)
    
    # ── Generic Metadata (WAD-defined, engine-agnostic) ──
    # Replaces: pillars, pantheon, sigil, glyph, element, chakra, planet,
    # invocation, secondary_keeper — all WAD-specific fields.
    # The engine NEVER reads specific keys from this dict.
    # The WAD fills it; the engine passes it through.
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # ── Runtime Markers ──
    magic: int = field(default=ZONEID_ENTITY, compare=False)
    flags: int = field(default=0, compare=False)
```

### How WADs Extend with Rich Esoteric Content

The Arcana-NovAi WAD's `entities.yaml` carries all the rich content. The change is in how it maps to the engine:

**Current (M2 violation — engine knows WAD content):**
```yaml
sekhmet:
  name: Sekhmet
  domains: [ground, flesh, body, ...]
  pillars: ["P1: Flesh"]        # ← Engine interprets "P1: Flesh"
  pantheon: Egyptian             # ← Engine field
  element: Earth 🜃             # ← Engine field (via traits)
  chakra: Root                   # ← Engine field (via traits)
  sigil: ☀ Solar Wrath          # ← Engine field
```

**Proposed (M2 compliant — engine sees slots + opaque metadata):**
```yaml
sekhmet:
  name: Sekhmet
  domains: [ground, flesh, body, ...]
  slots: ["P1"]                  # ← Engine sees "P1", nothing more
  metadata:                      # ← Engine treats as opaque bag
    # ── Elemental Matrix ──
    element: Earth 🜃
    polarity: light
    # ── Chakra System ──
    chakra: Root
    chakra_index: 1
    # ── Planetary Ruling ──
    planet: ♁ Gaia
    # ── Identity ──
    pantheon: Egyptian
    sigil: ☀ Solar Wrath
    glyph: 🜃
    invocation: "O Living Clay, root of form and blood — awaken!"
    # ── Kabbalistic Mapping ──
    sphere: gevurah
    qliphoth: samuel
    # ── Governance ──
    governance_tier: 3           # Pillar Keeper
    reports_to: maat_oversoul
    polarity: light              # Ma'at governs light pillars
```

### Engine-WAD Boundary

```
┌─────────────────────────────────────────────────────────────┐
│                    ENGINE KNOWS                              │
├─────────────────────────────────────────────────────────────┤
│ Entity identity: name, role, wad_source                     │
│ Routing: domains, capabilities, slots                       │
│ Inference: model, personality, temperature, context_window  │
│ Infrastructure: container, port                             │
│ Layering: priority, flags                                   │
│ Governance: rank (integer from hierarchy.yaml)              │
│ Failure modes: technical_domain, severity (generic)         │
│                                                             │
│ Engine does NOT interpret:                                  │
│ - What "P1" means (just matches string)                    │
│ - What "Earth" means (just passes through)                 │
│ - What "Keter" means (just loads hierarchy)                │
│ - What "Samuel" means (just loads failure modes)           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    WAD DEFINES                              │
├─────────────────────────────────────────────────────────────┤
│ Entity content: element, chakra, planet, sigil, invocation  │
│ Slot labels: "P1: Flesh" (engine sees "P1")                │
│ Governance: name, title, voice, archetype                   │
│ Qliphoth: failure mode names, translations, recovery       │
│ Spheres: Kabbalistic mapping, colors, archetypes           │
│ Energy flow: polarity, routing weights                      │
│ Soul templates: personality, values, directives             │
│                                                             │
│ WAD does NOT touch:                                         │
│ - Entity routing logic                                      │
│ - Model selection                                           │
│ - Inference parameters                                      │
│ - Provider fabric                                           │
│ - Memory store                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Step 1: Rename `Entity.pillars` → `Entity.slots`

**Scope**: Entity dataclass + all consumers

```python
# Entity dataclass
slots: List[str] = field(default_factory=list)  # was: pillars

# EntityRegistry
# Remove: PILLAR_SLOTS = frozenset({"p1"..."p10"})
# Add: dynamically from loaded entities
@property
def occupied_slots(self) -> frozenset:
    """All slot IDs currently occupied by loaded entities."""
    return frozenset(
        s.lower()
        for e in self.active_iter()
        for s in e.slots
    )

# get() Tier 2 resolution
slot_key = name_lower.replace("pillar ", "p").replace("pillar", "p")
if any(s.lower() == slot_key for s in projected.slots):
    return projected
```

**Files affected**: `entity_registry.py`, `entity.py`, `wad_loader.py`, `oracle.py`, `cli/oracle_cli.py`

### Step 2: Rename `Entity.traits` → `Entity.metadata`

**Scope**: Entity dataclass + WAD loader

```python
# Entity dataclass
metadata: Dict[str, Any] = field(default_factory=dict)  # was: traits

# __getattr__ — backward compat
def __getattr__(self, name: str) -> Any:
    if name in self.metadata:
        return self.metadata[name]
    raise AttributeError(...)

# wad_loader.py — rename variable
wad_metadata = {}
for field in ("element", "chakra", "planet", "glyph", "invocation",
              "pantheon", "sigil", "secondary_keeper"):
    val = ent_data.get(field)
    if val is not None:
        wad_metadata[field] = val
```

**Files affected**: `entity.py`, `wad_loader.py`, `entity_registry.py`

### Step 3: Move `pantheon`, `sigil` → `metadata`

**Scope**: Entity dataclass + oracle.py + CLI

```python
# Entity dataclass — remove:
# pantheon: Optional[str] = None   → metadata["pantheon"]
# sigil: Optional[str] = None      → metadata["sigil"]
# first_breath: Optional[str] = None → metadata["first_breath"]

# oracle.py — change:
# entity.pantheon → entity.metadata.get("pantheon")
# entity.sigil → entity.metadata.get("sigil")
```

**Files affected**: `entity.py`, `oracle.py`, `cli/oracle_cli.py`, `observability.py`

### Step 4: Update `OracleResponse`

**Scope**: oracle.py + iris/server.py + CLI

```python
@dataclass
class OracleResponse:
    text: str
    entity: str = "Oracle"
    confidence: float = 0.5
    trace_id: str = ""
    slots: Optional[List[str]] = None      # was: pillars
    domains: Optional[List[str]] = None
    backend: Optional[str] = None
    model: Optional[str] = None
    session_id: Optional[str] = None
    escalated: bool = False
    cost_warning: Optional[str] = None
    # REMOVED: sigil, glyph, pantheon — use entity metadata for display
```

**Files affected**: `oracle.py`, `mcp_servers/omega_hub/server.py`, `cli/oracle_cli.py`

### Step 5: Create `FailureModeRegistry`

**Scope**: New file + WAD loader integration

```python
# src/omega/oracle/failure_modes.py (NEW)

@dataclass
class FailureMode:
    """A named failure mode — defined by WADs, checked by engine."""
    name: str                    # e.g., "samuel"
    translation: str             # e.g., "Poison of God"
    counter_sphere: str          # e.g., "gevurah"
    severity: str                # CRITICAL, HIGH, MEDIUM, LOW
    technical_domain: str        # e.g., "boundary_violation"
    engine_pattern: str          # e.g., "Engine-Stack Firewall breach"
    detection: str               # e.g., "CI gate: grep for 'from config'"
    recovery: str                # e.g., "Apply M2 firewall enforcement"

class FailureModeRegistry:
    """WAD-defined failure modes. Engine queries this for M17 checks."""
    
    def __init__(self):
        self._modes: Dict[str, FailureMode] = {}
    
    def register(self, mode: FailureMode) -> None:
        self._modes[mode.name] = mode
    
    def get_by_domain(self, technical_domain: str) -> List[FailureMode]:
        """Find failure modes by technical domain."""
        return [m for m in self._modes.values() if m.technical_domain == technical_domain]
    
    def get_critical(self) -> List[FailureMode]:
        return [m for m in self._modes.values() if m.severity == "CRITICAL"]
```

**Files affected**: New file `src/omega/oracle/failure_modes.py`, `wad_loader.py`

### Step 6: Update WAD `entities.yaml`

**Scope**: Both WADs

Move `pantheon`, `sigil`, `glyph`, `invocation`, `element`, `chakra`, `planet` into `metadata:` block. Change `pillars: ["P1: Flesh"]` to `slots: ["P1"]`.

### Step 7: Update Tests

**Scope**: ~20 test files

Update all references to `pillars` → `slots`, `traits` → `metadata`, and remove WAD-specific field assertions from engine tests.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Breaking `@pillar P1` dispatch | Low | Medium | OpenCode agent framework resolves before engine sees it |
| Breaking MCP tools | Low | Low | `oracle_list_pillar_keepers()` → `oracle_list_entities()` |
| Breaking CLI output | Medium | Low | Update `oracle_cli.py` display logic |
| Breaking observability logs | Low | Low | `OracleResponse` fields are additive |
| Losing WAD content | None | N/A | Content moves to `metadata` dict, not deleted |

---

## Heritage Attribution

This architecture is a direct application of:

- `[M2 Engine-Stack Firewall]` — strict separation of `src/omega/` from `config/wads/`
- `[id-soft: doom-1993] WAD System` — the engine loads data, doesn't interpret it
- `[Carmack's Law: id Software]` — consolidate redundant pillar concept into generic slots
- `[Right Approximation: evolved from FISR, id Software 1999]` — the engine doesn't need to understand "Earth 🜃", it needs to route by "flesh" keyword

---

## References

- `data/entities/roc_racoon/workspace/mining_reports/PILLAR_DESIGN_MAP_COMPLETE.md` — complete esoteric architecture
- `data/entities/roc_racoon/workspace/mining_reports/ENGINE_WAD_SEPARATION_RECONSTRUCTION.md` — vision reconstruction
- `docs/strategy/OMEGA_IWAD_ARCHITECTURE.md` — original IWAD architecture spec
- `docs/decisions/PIVOT_LOG.md` — D179 (pillar gate removal), D180 (full decoupling architecture)
- Project Charter §5.0 — dual architecture (Jan 2026)

---

*Last Updated: 2026-07-01 | Author: Kali | Version: v1.0.0*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_pillar_decoupling | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
