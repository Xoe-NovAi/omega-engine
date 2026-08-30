# 🔱 RQ-11: Sovereign Siloing & WAD Evolution
## Implementation Architecture — Code-Mapped Spec
**AP Token**: AP-RQ-11-v1.0.0
⬡ OMEGA ⬡ RESEARCHER ⬡ big-pickle ⬡ opencode ⬡ trc_siloing_spec ⬡ ARCHITECTURE

**Date**: 2026-06-12
**Status**: IMPLEMENTATION-READY (Phases 2-4)
**Predecessor**: `docs/research/R_ID_SOFTWARE_RIGHT_APPROXIMATIONS.md` (RQ-10)

---

## §0 Executive Summary

The codebase already has entity layering (`_project_entity`, `priority`, `_entities: Dict[str, List[Entity]]`) and WAD loading. The **gaps** are:

1. **No formal tier convention** — priority integers have no semantic meaning
2. **No runtime hot-swapping** — WADs load at startup only
3. **No capability governor** — PWADs can override engine-critical fields
4. **No sovereign key registry** — ZONEID exists but isn't enforced as immutable
5. **Data quality debt** — `arcana_novai/entities.yaml` has raw engine_zone dumps

**Target files**: `entity_registry.py`, `wad_loader.py`, `omega.yaml`

---

## §1 4-Tier Overlay Stack

### Current State
```python
# entity_registry.py:69 — priority is unbounded int
priority: int = 0
# wad_loader.py:68 — load_single_wad hardcodes priority=10
async def load_single_wad(self, stack_name: str, priority: int = 10) -> bool:
```

### Design
Formalize 4 tiers with reserved priority ranges:

| Tier | Priority Range | Source | Mutable | Example |
|------|---------------|--------|---------|---------|
| Core | 1000+ | `constants.py`, `cvar_table.py` | ❌ Build-time only | ZONEID, Mandates |
| IWAD | 100-999 | `_omega_default/entities.yaml` | ❌ Engine restart | Default entity roles |
| PWAD | 1-99 | `config/wads/<stack>/` | ✅ Hot-swappable | arcana_novai entities |
| Runtime | 0 | `omega summon`, runtime API | ✅ Session scope | User overrides |

### Changes

**`entity_registry.py`** — Add tier constants and enforce during `_project_entity()`:
```python
class EntityRegistry:
    PRIORITY_CORE = 1000      # Immutable engine constants
    PRIORITY_IWAD = 100       # Base IWAD baseline
    PRIORITY_PWAD_MIN = 1     # PWAD range floor
    PRIORITY_PWAD_MAX = 99    # PWAD range ceiling
    PRIORITY_RUNTIME = 0      # Session-level overrides
    # Sovereign keys — fields that PWADs CANNOT override
    SOVEREIGN_KEYS = frozenset({
        "magic", "flags", "wad_source", "name",
    })
```

**`wad_loader.py:68`** — Change `load_single_wad` priority default from `10` to `IWA_PRIORITY=100`:
```python
async def load_single_wad(self, stack_name: str, priority: int = 100) -> bool:
```

**`wad_loader.py:166-227`** — Add sovereign key guard in `_load_entities()`:
```python
# Before entity creation, validate no sovereign keys are overridden
if priority < EntityRegistry.PRIORITY_IWAD:
    for key in EntityRegistry.SOVEREIGN_KEYS:
        if key in ent_data and ent_data[key] is not None:
            logger.warning(
                f"PWAD {wad_source} attempted to override sovereign key "
                f"'{key}' on entity '{entity_name}'. BLOCKED."
            )
            ent_data.pop(key)  # Strip the override, use default
```

---

## §2 Runtime Hot-Swapping

### Current State
```python
# wad_loader.py:49 — only called at startup
async def load_all_wads(self) -> Dict[str, bool]:
# No unload/reload mechanism exists
```

### Design
Add `unload_wad()` and `reload_wad()` to WADLoader. On unload, remove all entities with that `wad_source`. On reload, re-run `_load_entities()`.

### Changes

**`wad_loader.py`** — Add methods:
```python
async def unload_wad(self, stack_name: str) -> bool:
    """Hot-unload a PWAD. Removes all entities from this WAD source.
    IWADs (priority >= 100) cannot be unloaded at runtime.
    """
    # Find entities with this wad_source
    entities_to_remove = [
        e for e in self.registry.active_iter()
        if e.wad_source == stack_name and e.priority < 100
    ]
    if not entities_to_remove:
        logger.warning(f"No removable entities found for WAD {stack_name}")
        return False
    for entity in entities_to_remove:
        await self.registry.remove(entity.name)
    logger.info(f"Unloaded {len(entities_to_remove)} entities from WAD {stack_name}")
    return True

async def reload_wad(self, stack_name: str) -> bool:
    """Hot-reload a PWAD: unload then reload."""
    await self.unload_wad(stack_name)
    return await self.load_wad(stack_name, priority=50)
```

**`entity_registry.py`** — Add `get_by_wad_source()` for targeted removal:
```python
def get_by_wad_source(self, wad_name: str) -> List[Entity]:
    return [
        self._project_entity(layers)
        for key, layers in self._entities.items()
        if any(l.wad_source == wad_name for l in layers)
    ]
```

---

## §3 Capability Governor

### Current State
```python
# entity_registry.py:353-391 — _project_entity merges all fields unconditionally
# No capability validation, no boundary check
```

### Design
Add a `capability_registry` field to each Entity that defines what fields this layer is ALLOWED to override. PWADs loaded from untrusted sources must have explicit capability grants.

### Changes

**`entity_registry.py:Entity`** — Add capability guard:
```python
@dataclass
class Entity:
    capabilities: List[str] = field(default_factory=list)
    # NEW: Override scope — which fields this layer can modify
    override_scope: List[str] = field(default_factory=lambda: [
        "personality", "temperature", "invocation",
        "element", "chakra", "planet", "sigil", "glyph",
    ])
    # IWAD layers also get:
    # "domains", "model", "role", "pantheon", "context_window"
```

**`entity_registry.py:_project_entity()`** — Validate scope during merge:
```python
for layer in reversed(layers):
    allowed = layer.override_scope
    # Only merge fields within the layer's override scope
    if "personality" in allowed and layer.personality:
        projected.personality = merge_personality(projected.personality, layer.personality)
    if "model" in allowed and layer.model:
        projected.model = layer.model
    # ... etc
```

---

## §4 Sovereign Key Guarding

### Current State
```python
# entity_registry.py:71 — magic is set but not validated during _load()
magic: int = field(default=ZONEID_ENTITY, compare=False)
# No check during WAD loading that ZONEID or flags are authentic
```

### Design
Maintain an immutable `SOVEREIGN_KEYS` registry in `EntityRegistry`. Any layer attempting to override these keys is silently blocked (with a warning log). The registry itself is set at build time from `constants.py` and `cvar_table.py`.

### Changes

**`constants.py`** — Add the sovereign key list (already has ZONEID constants):
```python
# Immutable registry of keys that no WAD or runtime layer can override
SOVEREIGN_KEYS = frozenset({
    "magic",           # ZONEID integrity marker
    "flags",           # High-bit system flags
    "wad_source",      # Provenance tracking
    "name",            # Entity identity
    "priority",        # Layer ordering
    "override_scope",  # Self-limiting capability boundary
})
```

**`entity_registry.py:Entity.__post_init__`** — Prevent runtime override of sovereign keys:
```python
def __setattr__(self, name, value):
    if name in SOVEREIGN_KEYS and name in self.__dict__:
        raise InvariantViolationError(
            f"Cannot override sovereign key '{name}' on entity '{self.name}'"
        )
    super().__setattr__(name, value)
```

---

## §5 Data Quality Remediation

### Current State
`config/wads/arcana_novai/entities.yaml` (2335 lines) contains raw `__engine_zone__` and `__game_zone__` serialization artifacts — these are runtime constructs, not user-editable config.

### Fix
Strip runtime-only fields from the YAML serialization in `Entity.to_dict()`:
```python
def to_dict(self) -> Dict[str, Any]:
    result = {}
    for k, v in asdict(self).items():
        if v is None: continue
        if isinstance(v, (list, dict)) and not v: continue
        if k in ("magic", "flags", "override_scope"): continue  # Runtime-only
        # Do NOT serialize engine_zone/game_zone — they are runtime constructs
        if k.startswith("__") and k.endswith("__"): continue
        result[k] = v
    return result
```
Then run `registry._save()` to regenerate `arcana_novai/entities.yaml` clean.

---

## §6 Implementation Order

```
Step 1: Sovereign Key Guarding (constant.py + entity_registry.py)  ← 1 hour
  - Add SOVEREIGN_KEYS constant
  - Add __setattr__ guard 
  - Add priority tier constants
  - This is the FOUNDATION — nothing else builds on unsafe data

Step 2: Capability Governor (entity_registry.py)                    ← 2 hours
  - Add override_scope field to Entity
  - Wire scope validation into _project_entity()
  - Update _load() to set IWAD-scope vs PWAD-scope

Step 3: Runtime Hot-Swapping (wad_loader.py)                        ← 2 hours
  - Add unload_wad() method
  - Add reload_wad() method
  - Wire into MCP Hub tool set for CLI invocation

Step 4: Data Quality Fix (entity_registry.py:to_dict) + save cycle  ← 30 min
```

---

## §7 Test Plan

| Test | What | Expected |
|------|------|----------|
| `test_pwad_cannot_override_sovereign_key` | Load PWAD that sets magic=0 | Blocked, warning logged |
| `test_hot_unload_removes_pwad_entities` | Load PWAD, unload, check count | Entities count decreases |
| `test_iwad_cannot_be_unloaded` | Call unload_wad on _omega_default | Returns False, warning |
| `test_capability_scope_limits_override` | PWAD tries to override model without scope | Blocked, IWAD value preserved |
| `test_to_dict_no_zone_dump` | Serialize entity, check output | No __engine_zone__ in YAML |

---

*⬡ This spec maps directly to code. Each § section has target file, line numbers, and change description. Ready for P3 (BuildMaster) implementation. ⬡*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: big-pickle | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
