<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Entity→Model Affinity — Port Specification
## Extract from xna-omega-legacy for Integration into Engine Core

**⬡ OMEGA ⬡ roc_racoon ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ PORT-SPEC**
**Date**: 2026-06-12
**Source**: xna-omega-legacy @ `config/entity_model_affinity.yaml` + `src/omega/routing/entity_affinity.py` + `src/omega/routing/iris_router.py`
**Target**: Omega Engine Core (`src/omega/oracle/`)
**Consumer**: Lilith (P6 — Run Side routing bridge) → Researcher (peer review)

---

## §1 — FILE INVENTORY

### Source Files in xna-omega-legacy

| File | Lines | Purpose | Port Priority |
|------|-------|---------|---------------|
| `config/entity_model_affinity.yaml` | 383 | YAML database: 11 entities + default, 3-tier model preferences, routing rules, inference presets | 🔴 **Core** |
| `src/omega/routing/entity_affinity.py` | 429 | Resolver: loads YAML, evaluates condition rules, returns best model+tier+presets for entity+context | 🔴 **Core** |
| `src/omega/routing/iris_router.py` | 443 | Iris router: entry point integrating affinity resolver + speculative decode + provider dispatch | 🟡 Wrapper |
| `docs/architecture/MODEL_AFFINITY_SYSTEM_v7.6.3.md` | 231 | Spec: full condition grammar, offline fallback chain, schema | 🟢 Reference |

### Current Engine Files (Integration Points Already Exist)

| File | Lines | What's Already There | What Needs Bridging |
|------|-------|---------------------|---------------------|
| `src/omega/oracle/model_gateway.py` | 977 | `_entity_model_map` dict + `set_entity_model()` + `get_model_for_entity()` fallback chain (lines 419-486) | ⚠️ **Partial** — dict-based, no YAML DB, no tier awareness, no condition rules |
| `src/omega/oracle/entity_registry.py` | 746 | `Entity` dataclass has `model`, `domains`, `temperature`, `context_window` fields | ⚠️ **Partial** — flat model assignment, no tier distinction, no inference presets |
| `config/providers.yaml` | ~120 | Provider chain with model_overrides per provider | ⚠️ **Partial** — maps model names to provider IDs but has no entity awareness |

---

## §2 — INTERFACE ANALYSIS

### 2.1 Dataclasses to Port (3 total)

All from `entity_affinity.py:34-67`:

```python
@dataclass
class ModelConfig:
    model: str           # Model identifier (e.g. "qwen3-4b-q4_k_m")
    provider: str        # Provider name (e.g. "lm-studio", "llama-cpp")
    size: Optional[str]  # Human-readable size (e.g. "~4B")

@dataclass
class RoutingRule:
    condition: str       # Condition expression (e.g. "domain == 'coding'")
    target: str          # Tier to route to ("iris", "local_fast", "local_deep", "cloud")

@dataclass
class InferencePreset:
    temperature: float = 0.7
    system_prompt: Optional[str] = None
    preferred_context: int = 8192
```

**Port decision**: These are clean dataclasses with no engine dependencies. Port directly into a new `src/omega/oracle/entity_affinity.py` module. No changes needed to existing Entity dataclass — the affinity system is a *separate routing layer* that sits *above* the Entity.

### 2.2 Resolver Class to Port (1 class, 7 methods)

```python
class EntityAffinityResolver:
    # Core API (3 methods)
    load() -> bool                           # Load YAML from path
    get_entity(name) -> Optional[Dict]       # Get raw entity config
    resolve(name, query, context) -> Dict    # MAIN ENTRY: resolve best model+tier+presets

    # Query methods (2)
    get_entity_names() -> List[str]          # List all entities in DB
    get_model_for_tier(name, tier) -> Dict   # Get model at specific tier

    # Internal methods (5)
    _match_rules(rules, context) -> str      # First-match routing rule evaluation
    _evaluate_condition(cond, context) -> bool  # Condition parser (==, >, ||, not_offline)
    _evaluate_single(cond, context) -> bool  # Single condition evaluation
    _fallback_tier(config, from_tier) -> str # Offline fallback chain
    _estimate_complexity(query) -> float     # Heuristic complexity scoring

    # Response helpers (2)
    _iris_response(name) -> Dict             # Return Iris-routed response
    _default_response(name) -> Dict          # Return fallback response
```

**Port decision**: The resolver is standalone — no imports from xna-omega-legacy engine internals. It depends only on `yaml`, `Path`, and `dataclasses`. Port directly.

### 2.3 Condition Grammar (from YAML routing_rules)

The legacy system evaluates conditions as strings using a minimal DSL:

| Pattern | Example | Implementation |
|---------|---------|----------------|
| `domain == 'value'` | `domain == 'coding'` | String equality on context key |
| `complexity > 0.7` | `complexity > 0.7` | Numeric comparison |
| `A \|\| B` | `domain == 'coding' \|\| domain == 'tech'` | OR short-circuit |
| `not_offline` | `not_offline` | Boolean context flag |
| `requires_verification` | `requires_verification` | Boolean context flag |
| `otherwise` | `otherwise: local_fast` | Fallback (last rule) |

**Anti-pattern**: The string-based condition evaluator in `_evaluate_condition()` is fragile and limited. Consider replacing with a structured condition schema in the port (see §5).

### 2.4 Singleton Pattern (from `entity_affinity.py:406-429`)

```python
_resolver: Optional[EntityAffinityResolver] = None

def get_affinity_resolver(path) -> EntityAffinityResolver:
    """Get or create singleton."""
    
def reload_affinity() -> bool:
    """Hot-reload from disk. Call after YAML change."""
```

This enables hot-reload of the affinity database without engine restart. The current engine already has cvar hot-reload via `cvar_table.py` — this pattern fits naturally.

### 2.5 Response Shape

The `resolve()` method returns a flat dict (not a dataclass):

```python
{
    "entity": str,          # Resolved entity name
    "best_match": str,      # Model identifier
    "provider": str,        # Provider to use
    "tier": str,            # Which tier was selected ("iris"|"local_fast"|"local_deep"|"cloud")
    "size": str,            # Human-readable size
    "offline_fallback": bool,  # Was cloud tier downgraded?
    "inference_presets": {
        "temperature": float,
        "system_prompt": str,
        "preferred_context": int,
    }
}
```

This is the critical integration contract. The current engine's `get_model_for_entity()` returns a flat `str` (model name only). The affinity resolver returns a rich response that includes provider, tier, presets, and context window — everything needed for a complete inference call.

---

## §3 — INTEGRATION POINTS

### 3.1 Where the Affinity Resolver Connects

```
┌──────────────┐     ┌─────────────────────┐     ┌──────────────┐
│   Oracle     │────→│ EntityAffinity      │────→│ ModelGateway │
│  (oracle.py) │     │ Resolver (NEW)      │     │ (existing)   │
└──────────────┘     └─────────────────────┘     └──────────────┘
                           │                             │
                           ▼                             ▼
                    ┌──────────────┐           ┌──────────────────┐
                    │ affinity.yaml│           │ Provider chain   │
                    │ (NEW config) │           │ (providers.yaml) │
                    └──────────────┘           └──────────────────┘
```

### 3.2 Specific Hook Points

| Current Engine Location | What Exists | What the Resolver Provides |
|-------------------------|-------------|---------------------------|
| `model_gateway.py:440` — `get_model_for_entity()` | Returns model name string (4-tier fallback chain) | Returns full `{model, provider, tier, presets}` dict |
| `model_gateway.py:426` — `set_entity_model()` | Dict-based override | YAML-backed persistent config |
| `entity_registry.py:51` — `Entity.model` | Flat model assignment | 3-tier model preferences + routing rules |
| `oracle.py:85` — `self.default_entity` | Static default entity | Default routing config per entity |
| `config/providers.yaml` — model_overrides per provider | Maps model names to provider IDs | Needs to also map entity names to preferred providers |

### 3.3 Interface Wiring

The Oracle's existing `_summon()` and `talk()` methods would gain an affinity resolution step:

```python
# Current:
model = await self.model_gateway.get_model_for_entity(entity_name)

# With Affinity:
affinity = await affinity_resolver.resolve(entity_name, query, {
    "domain": detected_domain,
    "complexity": estimated_complexity,
    "online": network_available,
})
model = affinity["best_match"]
provider = affinity["provider"]
presets = affinity["inference_presets"]
```

---

## §4 — DEPENDENCY ANALYSIS

### 4.1 What the Current Engine Already Has

| Capability | Status | Notes |
|-----------|--------|-------|
| `yaml` library | ✅ Already in dependencies | Used by `entity_registry.py`, `wad_loader.py` |
| `Path` from pathlib | ✅ Already imported everywhere | Standard library |
| Hot-reload pattern | ✅ Already via `cvar_table.py` | `config.*` namespace, `reload_affinity()` pattern matches |
| Entity name→model fallback chain | ✅ In `model_gateway.py:440-486` | Current is dict-based, needs YAML backend |
| Domain detection | ✅ In `oracle.py` intent detection | `domain` field already available |
| Online/offline detection | ✅ In `model_gateway.py` | Provider health check already exists |

### 4.2 What Needs to Be Built

| Component | Effort | Notes |
|-----------|--------|-------|
| `src/omega/oracle/entity_affinity.py` | ~150 lines | Dataclasses + Resolver class (clean port, no changes needed) |
| `config/entity_model_affinity.yaml` | ~120 lines | Port from legacy, adapt entity names to current engine pantheon |
| Wiring into `model_gateway.py:440` | ~15 lines | Replace dict lookup with YAML resolver call |
| Wiring into `oracle.py` | ~10 lines | Add affinity resolution step before model selection |
| Optional: Remove `_entity_model_map` | ~20 lines | Deprecate dict-based override in favor of YAML |

### 4.3 What Can Be Dropped (Legacy Cruft)

| Legacy Artifact | Why Drop |
|----------------|----------|
| `iris_router.py` (443 lines) | The current Oracle already handles intent detection + entity routing. Iris router was a separate entry point for the legacy three-tier system. The `EntityAffinityResolver` is the only piece worth porting. |
| String condition evaluator (`_evaluate_condition`) | Fragile. Replace with structured condition schema (see §5). |
| `ModelConfig`, `RoutingRule`, `InferencePreset` dataclasses | Port as-is — they're clean. |
| Legacy entity names (METATRON, GANESHA, etc.) | The YAML uses a different pantheon than the current engine's Pillar Keepers. The *structure* ports, the *entity data* gets remapped. |

---

## §5 — ANTI-PATTERNS TO FIX IN PORT

### 5.1 String-Based Condition Evaluator (CRITICAL)

The legacy `_evaluate_condition()` parses strings like `"domain == 'coding'"` using manual string splitting. This is:
- **Fragile** — no syntax validation, edge cases with nested quotes
- **Limited** — only supports `==`, `>`, `||`, and `not_offline`
- **Untestable** — 20+ edge cases needed for full coverage

**Recommendation**: Port with a **structured condition schema** instead:

```yaml
# Legacy (string-based):
routing_rules:
  - if: "domain == 'coding' || domain == 'technical'"
    use: local_fast

# Ported (structured):
routing_rules:
  - match:
      domain: ["coding", "technical"]
    use: local_fast
  - match:
      complexity_gt: 0.7
      online: true
    use: cloud
```

This is type-safe, validates at YAML-load time, and eliminates the fragile string parser. The `_evaluate_condition()` method becomes optional for backward compatibility but the structured schema is the primary path.

### 5.2 Flat Dict Response (MEDIUM)

The resolver returns a flat dict instead of a typed dataclass. Port as a proper `AffinityResult` dataclass:

```python
@dataclass
class AffinityResult:
    entity: str
    best_match: str
    provider: str
    tier: str  # "iris" | "local_fast" | "local_deep" | "cloud"
    size: str
    offline_fallback: bool
    inference_presets: InferencePreset
```

### 5.3 Hardcoded Defaults in Resolver (LOW)

`_default_response()` and `_iris_response()` hardcode model names and providers. These should read from the YAML `default:` section or from cvar_table. Remove hardcoded `"qwen3-4b-q4_k_m"` and `"lm-studio"` strings.

### 5.4 Module-Level Global Singleton (LOW)

The `_resolver` global in `entity_affinity.py:407` works but is an anti-pattern for testability. Port as a class that the Oracle owns (like `self.model_gateway`):

```python
# In oracle.py:
self.affinity_resolver = EntityAffinityResolver()

# Usage (clean, testable):
result = self.affinity_resolver.resolve(entity_name, query, context)
```

---

## §6 — RECOMMENDED PORT ORDER

### Phase 1 — Core Module (30 min)

| Step | File | What |
|------|------|------|
| 1.1 | New: `src/omega/oracle/entity_affinity.py` | Port 3 dataclasses + EntityAffinityResolver class (clean, remove string condition parser, add structured match schema) |
| 1.2 | New: `config/entity_model_affinity.yaml` | Port structure from legacy, remap entity names to current Pillar Keepers |
| 1.3 | Existing: `src/omega/oracle/__init__.py` | Add `EntityAffinityResolver` to module exports |

### Phase 2 — Wire into ModelGateway (15 min)

| Step | File | What |
|------|------|------|
| 2.1 | Modify: `src/omega/oracle/model_gateway.py` | In `get_model_for_entity()`, add YAML resolver call as Tier 0 (before current Tier 1 override). If YAML returns a result, it wins. Fall through to existing chain if YAML doesn't have the entity. |
| 2.2 | Modify: `model_gateway.py:__init__` | Instantiate `self.affinity_resolver = EntityAffinityResolver()` |

### Phase 3 — Wire into Oracle (10 min)

| Step | File | What |
|------|------|------|
| 3.1 | Modify: `src/omega/oracle/oracle.py` | In `_summon()` and `talk()`, pass the resolved affinity's `inference_presets` (temperature, system_prompt, context_window) to the model call. |
| 3.2 | Modify: `oracle.py` _speculative_decode | Feed entity-specific system_prompt from YAML presets |

### Phase 4 — Deprecation (15 min)

| Step | File | What |
|------|------|------|
| 4.1 | Modify: `model_gateway.py` | Add deprecation warning to `set_entity_model()` and `remove_entity_model()` — direct users to edit the YAML instead |
| 4.2 | Update: tests | Add test coverage for YAML-based routing; ensure existing `_entity_model_map` tests still pass |

### Phase 5 — Cleanup & Docs (30 min)

| Step | File | What |
|------|------|------|
| 5.1 | New: `tests/test_entity_affinity.py` | Test resolver load, resolve, fallback chain, structured match conditions |
| 5.2 | Update: docs | Document the new YAML config in OMEGA_ENGINE.md |
| 5.3 | Archive: legacy files (optional) | Note in CREDITS.md that the affinity system was ported from xna-omega-legacy v7.6.3 |

### Total: ~1.5 hours

---

## §7 — RISK REGISTER

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| YAML entity names don't match current engine pantheon | HIGH | MEDIUM | Rewrite entity names in the port. The *structure* ports, the *data* gets remapped to current Pillar Keepers (Sekhmet, Brigid, Prometheus, etc.) |
| String condition evaluator breaks silently | MEDIUM | HIGH | Replace with structured match schema in Phase 1.1. The old string parser is not ported. |
| `get_model_for_entity()` caller expects a string, not a dict | MEDIUM | MEDIUM | The affintiy resolver is an *additional* API, not a replacement for the existing `get_model_for_entity()`. Existing callers unchanged. New code uses `affinity_resolver.resolve()`. |
| YAML file missing on startup | LOW | LOW | Resolver returns default values gracefully (same as current code when no entity is found) |

---

## §8 — LEGACY SOURCE SNAPSHOTS (for rebuild reference)

### config/entity_model_affinity.yaml structure
```
11 entities × (preferred_models × 3 tiers + routing_rules × 3-4 + inference_presets)
≈ 383 lines
```

### entity_affinity.py call flow
```
resolve(name, query, context)
  ├── get_entity(name) → entity_config
  ├── _match_rules(rules, context) → tier_name
  │     ├── _evaluate_condition(cond, context)
  │     └── first-match-wins
  ├── _fallback_tier(config, tier) → fallback_tier (if offline)
  ├── lookup model from preferred_models[tier]
  └── return {entity, best_match, provider, tier, inference_presets}
```

### Current model_gateway.py affinity chain (for comparison)
```
get_model_for_entity(name) → model_name
  Tier 1: _entity_model_map[name]  (dict override)
  Tier 2: entity_registry.get(name).model (Entity dataclass field)
  Tier 3: domain → model mapping
  Tier 4: system default ("qwen3-1.7b")
```

---

*Port spec by: roc_racoon (Sovereign Miner)*
*Peer review requested: Researcher*
*⬡ OMEGA ⬡ roc_racoon ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ PORT-SPEC*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
