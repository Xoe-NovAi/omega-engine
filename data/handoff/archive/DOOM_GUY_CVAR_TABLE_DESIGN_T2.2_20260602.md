<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 cvar_table Design — T2.2 Handoff for Cline/M3 Review
# ⬡ OMEGA ⬡ DOOM_GUY ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_cvar_design ⬡ T2.2
# For: Cline/M3 (1M context) — review, validate, approve for BuildMaster impl

---

## §1 Precedent: Quake 3's cvarTable_t

**Source**: Quake III Arena (1999) `q3-1.32b/code/qcommon/common.c` line ~250

```c
typedef struct {
    vmCvar_t *vmCvar;   // QVM-allocated pointer for direct access
    char *name;          // String name (e.g. "sv_maxclients")
    char *defaultValue;  // Default value string
    int modificationCount; // Incremented on every change
} cvarTable_t;
```

**Key properties**:
- Static array — all cvars declared at compile time in a single table
- `modificationCount` — a monotonic counter that QVM checks to detect changes
- `defaultValue` — string-based, parsed when read (no type safety in the table itself)
- Two-tier access: `Cvar_Get()` for runtime, `cvarTable_t` for registration

**id Software's evolution**:
| Game | Cvar Mechanism |
|------|---------------|
| Quake (1996) | `cvar_t` linked list, `Cvar_Get()` walks the list |
| Q3A (1999) | `cvarTable_t` static array + `vmCvar_t` for QVM direct access |
| DOOM 3 (2004) | `idCVar` class with constructor-based registration |

---

## §2 Omega Engine's Current State

The engine currently has **~30 ad-hoc `config.get()` calls** across providers:

```python
# ModelGateway: 10 .get() calls with inline defaults
self._n_ctx = config.get("n_ctx", 4096)
self._n_threads = config.get("n_threads", 6)
self._type_k = config.get("type_k", 8)
# Oracle: 6 .get() calls
data_dir = self.config.get("omega", {}).get("data", {}).get("dir", str(DATA_DIR))
# Providers: 14 .get() calls
url = self.config.get("endpoint", "http://127.0.0.1:1234")
```

**Problems this creates**:
1. **No single source of truth** — defaults are scattered across 3+ files
2. **No type validation** — `"n_ctx"` could be a string without detection
3. **No runtime modification tracking** — can't detect when a config changes
4. **No discovery** — impossible to list all config keys without reading the code
5. **No bound checking** — `n_threads=999` would silently be accepted

---

## §3 Proposed Architecture

### cvar_table.py — The Static Table

```python
# [id-soft: quake3-1999] cvarTable_t — static config declaration table
# Maps id Software's cvarTable_t pattern to Python dataclass.
#
# Key differences from Q3A:
# - Typed: Python's type system replaces Q3A's string-only cvars
# - Dict-backed: YAML config loads into this table; no linked list needed
# - No vmCvar_t: Python doesn't have QVM, so we use @property accessors

@dataclass
class CvarDef:
    name: str
    type: type              # int, float, str, bool, list, dict
    default: Any
    description: str
    bounds: Optional[tuple] = None  # (min, max) for numeric cvars
    enum: Optional[list] = None     # valid choices for string cvars
    secret: bool = False            # API keys, masked in logs
    modification_count: int = 0     # [id-soft: quake3-1999] mod count
```

### Table Structure

The table is organized by subsystem, matching Omega's module layout:

```python
CVAR_TABLE = {
    # ── Inference / Provider Fabric ──
    "inference.strategy": CvarDef(str, "local_first", "Provider chain strategy"),
    "inference.fallback_chain": CvarDef(list, [], "Ordered provider fallback chain"),
    
    # ── Native GGUF Provider ──
    "gguf.n_ctx": CvarDef(int, 4096, "Context window size", bounds=(256, 131072)),
    "gguf.n_threads": CvarDef(int, 6, "CPU threads", bounds=(1, 32)),
    "gguf.type_k": CvarDef(int, 8, "Key cache type (4=f16, 8=q8_0)", enum=[4, 8]),
    "gguf.type_v": CvarDef(int, 8, "Value cache type (4=f16, 8=q8_0)", enum=[4, 8]),
    "gguf.use_mmap": CvarDef(bool, True, "Memory-map model file"),
    
    # ── Oracle / Entity Registry ──
    "omega.entity.default": CvarDef(str, "default", "Default entity name"),
    "omega.entity.active_iwad": CvarDef(str, "_omega_default", "Active IWAD name"),
    "omega.data.dir": CvarDef(str, "data/", "Data directory root"),
    
    # ── Observability ──
    "observability.enable_dataset": CvarDef(bool, False, "Enable fine-tuning dataset collection"),
    "observability.trace_dir": CvarDef(str, "data/traces/", "Trace output directory"),
    
    # ── Model Settings (from models.yaml) ──
    "models.default.type_k": CvarDef(int, 8, "Default key cache type"),
    "models.default.type_v": CvarDef(int, 8, "Default value cache type"),
}
```

### Runtime Integration

```python
class CvarTable:
    """Typed config table — [id-soft: quake3-1999] cvarTable_t pattern."""

    def __init__(self):
        self._cvars: Dict[str, Any] = {}
        self._meta: Dict[str, CvarDef] = CVAR_TABLE
        self._mod_counts: Dict[str, int] = {}
        
    def load_from_yaml(self, config: dict, prefix: str = ""):
        """Bulk-load a YAML config dict into the cvar table.
        
        Flattens nested dicts: {"inference": {"strategy": "local_first"}}
        becomes cvar["inference.strategy"] = "local_first".
        """
        for key, cvar in self._meta.items():
            value = self._resolve_nested(config, key)
            if value is not None:
                self._set_typed(key, value)
                
    def get(self, name: str) -> Any:
        """Get a typed cvar value. Validates type and bounds on read."""
        ...
        
    def set(self, name: str, value: Any):
        """Set a cvar value. Triggers modification_count increment.
        
        [id-soft: quake3-1999] modificationCount — every set increments;
        consumers can poll to detect changes.
        """
        ...
        
    def dump(self) -> Dict[str, Any]:
        """[id-soft: quake3-1999] Cvar_WriteVariables — serialize modified cvars."""
        ...
```

### Migration from Config.get()

The current pattern:
```python
self._n_ctx = config.get("n_ctx", 4096)
```

Becomes:
```python
self._n_ctx = cvar_table.get("gguf.n_ctx")
```

Benefits:
- Default lives in one place (the table), not scattered across files
- Type checking happens once at load time
- `modificationCount` enables hot-reload detection
- `bounds` catches config errors early (e.g., `n_threads=999`)

---

## §4 Q3A Patterns We Deliberately Skip

| Q3A Feature | Skip Reason |
|-------------|-------------|
| `vmCvar_t` direct pointer | No QVM in Omega; Python @property suffices |
| String-only values | Python's type system is better |
| `Cvar_Command()` auto-CLI | Omega has its own Typer CLI |
| Per-frame `Cvar_VariableString()` | Python dict access is fast enough |

---

## §5 Implementation Plan

| Phase | Scope | Effort | Agent |
|-------|-------|--------|-------|
| **1** | `cvar_table.py` — table + load + typed get | 2 hrs | BuildMaster |
| **2** | Wire into ModelGateway (replaced `config.get()` for GGUF provider) | 1 hr | BuildMaster |
| **3** | Wire into Oracle (replaced `config.get()` for omega.* cvars) | 30 min | BuildMaster |
| **4** | Wire into Providers (endpoints, timeouts, model_overrides) | 1 hr | BuildMaster |
| **5** | Add `modificationCount` polling for hot-reload | 30 min | BuildMaster |
| **6** | Verify: `make test` + `make temple-grade` | 15 min | Quality |

**Total**: ~5.5 hours of implementation, well-scoped for BuildMaster.

---

## §6 Open Questions for Cline/M3

1. **Table granularity**: The proposed table has ~25 entries. Q3A had ~500+ cvars. Should Omega be exhaustive or use a "just the moving parts" approach? I recommend "just the moving parts" (module-scope defaults stay in code, only user-tunable knobs go in the table).

2. **Hot-reload polling**: Q3A checked `modificationCount` per-frame via `trap->Cvar_VariableString()`. Omega should check on config save. Is there an existing file-watch mechanism we should hook into?

3. **Secret cvars**: API keys (`google_api_key`, `openrouter_key`) should be in the table but masked on dump. Should secrets be in a separate file entirely?

4. **Relationship to ZONEID constants**: The ZONEID_TABLE I placed in `constants.py` is a lightweight example of this pattern (a static table of magic constants). Should the cvar table subsume it, or keep them separate?

---

## §7 Heritage

This pattern derives from: Quake III Arena (1999) `cvarTable_t` at `common.c:250`
Key difference from the original: Q3A's was string-typed with `vmCvar_t` indirection for QVM; Omega's is Python-typed with property accessors and bound validation.
Omega evolution: Static table → runtime-loadable from YAML. Modification count → hot-reload polling.

---

*Handoff from Doom Guy to Cline/M3. Review, validate, then delegate to BuildMaster for implementation.*
*All [id-soft:] tags in this doc are design proposals — actual code tags will be added during implementation.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
