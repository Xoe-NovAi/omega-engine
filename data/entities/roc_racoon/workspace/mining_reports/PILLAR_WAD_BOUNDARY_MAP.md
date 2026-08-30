<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Engine vs WAD Boundary Map — Pillar/Slot Ownership
**AP Token**: `AP-ROC_RACOON-BOUNDARY-MAP-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_mining ⬡ ACTIVE

**Date**: 2026-08-22
**Purpose**: Explicit ownership table for Engine Core vs WAD (Arcana-NovAi) concepts
**Canonical Ruling**: D180 / PIVOT_LOG_CANONICAL.md §1200-1210, M2 Engine-Stack Firewall

---

## 🎯 The Firewall Principle

> **Engine Core** = Universal Runtime (knows: slots, domains, metadata dict)
> **WAD (Arcana-NovAi)** = Specific Implementation (knows: P1=Flesh, P2=Dream, Sekhmet, Brigid, elements, chakras, sigils)

The Engine **NEVER** interprets WAD-specific values. It only:
- Stores slot IDs as opaque strings (`"P1"`, `"N1"`, `"custom_slot"`)
- Passes `metadata: Dict[str, Any]` through unchanged
- Routes by `domains` (engine-agnostic keywords)

---

## 📊 Ownership Table

| Concept | Engine Core Owns? | WAD (Arcana-NovAi) Owns? | Location | Notes |
|---------|-------------------|--------------------------|----------|-------|
| **Slot IDs** (`"P1"`, `"N1"`) | ✅ Schema only | ✅ Semantics | `Entity.slots: List[str]` | Engine validates list[str]; WAD defines meaning |
| **Slot Labels** (`"P1: Flesh"`) | ❌ | ✅ | `config/wads/arcana_novai/entities.yaml` | Engine auto-migrates `"P1: Flesh"` → `"P1"` on load |
| **Domains** (`"flesh"`, `"warrior"`) | ✅ Routing index | ✅ Values | `Entity.domains: List[str]` | Engine builds capability index; WAD provides keywords |
| **Metadata Dict** | ✅ Schema (`Dict[str, Any]`) | ✅ All keys/values | `Entity.metadata` | Engine NEVER reads specific keys |
| **Element** (`"Earth"`, `"Water"`) | ❌ | ✅ | `metadata["element"]` | WAD-specific; accessed via `entity.metadata.get("element")` |
| **Energy Center/Chakra** (`"Root"`, `"Sacral"`) | ❌ | ✅ | `metadata["energy_center"]` | WAD-specific |
| **Celestial Body** (`"Gaia"`, `"Neptune"`) | ❌ | ✅ | `metadata["celestial_body"]` | WAD-specific |
| **Archetypal Ally** (`"Sekhmet"`, `"Brigid"`) | ❌ | ✅ | `metadata["archetypal_ally"]` | WAD-specific |
| **Glyph** (`"🜃"`, `"🜄"`) | ❌ | ✅ | `metadata["glyph"]` | WAD-specific |
| **Invocation** (`"O Living Clay..."`) | ❌ | ✅ | `metadata["invocation"]` | WAD-specific |
| **Pantheon** (`"Egyptian"`, `"Celtic"`) | ❌ | ✅ | `metadata["pantheon"]` | WAD-specific |
| **Sigil** (`"☀ Solar Wrath"`) | ❌ | ✅ | `metadata["sigil"]` | WAD-specific |
| **Planet** (`"♁ Gaia"`, `"♆ Neptune"`) | ❌ | ✅ | `metadata["planet"]` | WAD-specific (legacy key) |
| **First Breath** | ❌ | ✅ | `metadata["first_breath"]` | WAD-specific (legacy) |
| **Secondary Keeper** | ❌ | ✅ | `metadata["secondary_keeper"]` | WAD-specific (legacy) |
| **Traits** (legacy) | ❌ | ✅ | Migrated to `metadata` | Old `traits:` → `metadata:` auto-migration |

---

## 🏗️ Engine Core API (src/omega/) — What Engine Exposes

### Entity Dataclass (Engine Zone)
```python
@dataclass
class Entity:
    # Engine Zone — structural, read-only for game logic
    name: str
    domains: List[str]           # Routing keywords (WAD provides)
    model: str                   # Model identifier
    personality: str             # System prompt
    capabilities: List[str]      # Capability tags
    temperature: Optional[float]
    context_window: Optional[int]
    role: Optional[str]          # e.g., "sysadmin", "N1"
    container: bool
    port: Optional[int]
    wad_source: Optional[str]    # Which WAD loaded this entity
    priority: int                # Shadow-Stacking layer priority
    
    # Slot System (replaces hardcoded NODE_SLOTS)
    slots: List[str] = field(default_factory=list)  # Engine uses for get("N1")
    
    # Generic Metadata (WAD-defined, engine-agnostic)
    metadata: Dict[str, Any] = field(default_factory=dict)  # OPAQUE BAG
```

### EntityRegistry Methods (Engine API)
| Method | Engine Responsibility | WAD Involvement |
|--------|----------------------|-----------------|
| `get(name)` | 3-tier resolution (name → slot → role) | WAD provides entities with slots |
| `list()` | Return all active entities | WAD defines entity list |
| `list_node_keepers()` | Filter `e.slots` non-empty | WAD assigns slots to entities |
| `find_by_domain(text)` | Keyword match on `domains` | WAD provides domain keywords |
| `get_by_wad(wad_name)` | Filter by `wad_source` | WAD sets `wad_source` on load |
| `get_by_capability(cap)` | Capability index lookup | WAD provides capabilities |
| `occupied_slots` | Dynamic discovery from loaded entities | WAD assigns slots |

### OracleResponse (Engine Transport)
```python
@dataclass
class OracleResponse:
    text: str
    entity: str
    confidence: float
    trace_id: str
    slots: Optional[List[str]]      # Engine field — slot IDs
    domains: Optional[List[str]]    # Engine field — matched domains
    backend: Optional[str]
    model: Optional[str]
    session_id: Optional[str]
    escalated: bool
    cost_warning: Optional[str]
    rag_complexity: Optional[str]
    audience: Optional[str]
    # NO pillar, sigil, glyph, pantheon, element, chakra fields
```

---

## 📦 WAD (Arcana-NovAi) — What WAD Defines

### Config Files (config/wads/arcana_novai/)
| File | Purpose | Engine Interaction |
|------|---------|-------------------|
| `entities.yaml` | Entity definitions with `slots:`, `domains:`, `metadata:` | Loaded by `EntityRegistry` via `config_resolver` |
| `hierarchy.yaml` | Governance: `governs_pillars: [P1-P5]` | Read by WAD tools only; Engine ignores |
| `axioms.yaml` | Philosophical axioms | WAD-only |
| `qliphoth.yaml` | Shadow taxonomy | WAD-only |
| `spheres.yaml` | Kabbalistic spheres | WAD-only |
| `manifest.yaml` | WAD metadata (name, version) | Read by `config_resolver` |

### Entity Definition Format (Post-Migration)
```yaml
entities:
  sekhmet:
    name: Sekhmet
    domains:
      - ground
      - flesh
      - warrior
      - protection
    model: qwen3-1.7b-q6_k
    personality: "You are Sekhmet, the Wrathful Flame..."
    slots: ["P1"]                    # ← Engine field (was pillars: ["P1: Flesh"])
    metadata:                        # ← Opaque WAD bag
      pantheon: Egyptian
      element: "Earth 🜃"
      energy_center: "Root"
      celestial_body: "Gaia"
      archetypal_ally: "Sekhmet"
      glyph: "🜃"
      invocation: "O Living Clay..."
      sigil: "☀ Solar Wrath"
      planet: "♁ Gaia"               # Legacy key, kept for compatibility
    wad_source: "arcana_novai"
```

### WAD-Specific Display (Client-Side)
The MCP Hub `oracle_entity_info` tool returns `metadata` dict for client rendering:
```json
{
  "name": "Sekhmet",
  "slots": ["P1"],
  "metadata": {
    "pantheon": "Egyptian",
    "element": "Earth 🜃",
    "energy_center": "Root",
    "glyph": "🜃",
    "sigil": "☀ Solar Wrath"
  }
}
```
**Client decides how to display** — Engine never formats WAD content.

---

## 🔄 Migration Rules (Auto-Applied on Load)

| Legacy YAML Key | Engine Action | New Internal Field |
|-----------------|---------------|-------------------|
| `pillars: ["P1: Flesh"]` | Extract slot ID before `:` | `slots: ["P1"]` |
| `nodes: ["N1: Flesh"]` | Extract slot ID before `:` | `slots: ["N1"]` |
| `nodes: ["1"]` | Prefix with `"N"` | `slots: ["N1"]` |
| `traits: [...]` | Move to metadata | `metadata["traits"] = [...]` |
| `pantheon: "X"` | Move to metadata | `metadata["pantheon"] = "X"` |
| `element: "X"` | Move to metadata | `metadata["element"] = "X"` |
| `chakra: "X"` | Move to metadata | `metadata["energy_center"] = "X"` |
| `planet: "X"` | Move to metadata | `metadata["planet"] = "X"` |
| `sigil: "X"` | Move to metadata | `metadata["sigil"] = "X"` |
| `glyph: "X"` | Move to metadata | `metadata["glyph"] = "X"` |
| `invocation: "X"` | Move to metadata | `metadata["invocation"] = "X"` |
| `first_breath: "X"` | Move to metadata | `metadata["first_breath"] = "X"` |
| `secondary_keeper: "X"` | Move to metadata | `metadata["secondary_keeper"] = "X"` |

**Code Location**: `src/omega/oracle/entity_registry.py:398-419`

---

## 🚫 FORBIDDEN in Engine Core

| Pattern | Violation | Correct Approach |
|---------|-----------|------------------|
| `if entity.pillars:` | M2 — Engine reads WAD field | `if entity.slots:` |
| `entity.element` | M2 — Direct WAD field access | `entity.metadata.get("element")` |
| `entity.chakra` | M2 — Direct WAD field access | `entity.metadata.get("energy_center")` |
| `entity.pantheon` | M2 — Direct WAD field access | `entity.metadata.get("pantheon")` |
| `OracleResponse.pillars` | M2 — Transport leaks WAD | `OracleResponse.slots` |
| `list_pillar_keepers()` | M2 — Method name leaks WAD | `list_node_keepers()` |
| `find_by_domain` filters by pillar | M2 — Routing depends on WAD | Route by `domains` only (D179) |
| Hardcoded `PILLAR_SLOTS` | M2 — Engine knows WAD slots | Dynamic `occupied_slots` property |

---

## ✅ ALLOWED in Engine Core

| Pattern | Reason |
|---------|--------|
| `entity.slots` | Abstract slot IDs — engine needs for routing |
| `entity.metadata` | Opaque dict — engine passes through |
| `entity.domains` | Routing keywords — engine builds index |
| `entity.get_symbolic_metadata()` | Typed view over `metadata["symbolic"]` — schema only |
| `SymbolicMetadata` TypedDict | Schema definition — values from WAD |
| `metadata["symbolic"]` sub-dict | Structured symbolic coords — engine provides schema |

---

## 🧪 Test Boundaries

| Test File | Engine Test? | WAD Test? | Should Test |
|-----------|--------------|-----------|-------------|
| `tests/test_entity_registry.py` | ✅ | ❌ | Slot migration, domain routing, metadata passthrough |
| `tests/test_oracle.py` | ✅ | ❌ | `OracleResponse.slots` populated, no pillar fields |
| `tests/test_hivemind.py` | ✅ | ❌ | Entity identity has `slots`, not `pillar` |
| `tests/contracts/test_mandate_auditor.py` | ✅ | ❌ | M3 checks slot assignments, not pillar |
| `tests/contracts/test_dispatch_registry.py` | ✅ | ❌ | Role/slot resolution works |
| `tests/test_a2a_bridge.py` | ✅ | ❌ | SPIFFE IDs use `entity/slot/` not `entity/pillar/` |

---

## 📋 Verification Checklist (Post-Refactor)

### Engine Core (src/omega/)
- [ ] No `pillar` or `pillars` in any `.py` file (except comments/docstrings)
- [ ] No `traits` as dataclass field (only in `metadata`)
- [ ] `Entity.slots` used everywhere for slot access
- [ ] `Entity.metadata` used for all WAD content
- [ ] `OracleResponse.slots` not `pillars`
- [ ] `EntityRegistry.list_node_keepers()` not `list_pillar_keepers()`
- [ ] `find_by_domain()` has no pillar gate

### MCP Hub (mcp_servers/omega_hub/)
- [ ] Tool name: `oracle_list_node_keepers`
- [ ] Response fields: `slot`, `node_keeper` (not `pillar`, `pillar_keeper`)
- [ ] `entity_identity` dict uses `slot` key
- [ ] Server tool registration uses new name

### WAD Config (config/wads/arcana_novai/)
- [ ] `entities.yaml` uses `slots:` not `pillars:`
- [ ] `hierarchy.yaml` uses `governs_pillars:` (WAD governance — OK)
- [ ] No engine code reads `hierarchy.yaml`

### Tests
- [ ] All tests assert `slots`/`metadata`
- [ ] No test asserts `pillar`/`pillars`/`traits`
- [ ] SPIFFE IDs use `entity/slot/`

### Scripts
- [ ] `setup.sh` uses `list_node_keepers()` and `result.slots`
- [ ] `mandate_gates.py` uses `iris_in_slot`

### Docs (Active Only)
- [ ] `STATUS_OPUS.md` uses `slots: []`
- [ ] `DOC_CLEANUP_AUDIT.md` uses "slot assignments"

---

## 🔗 Cross-Reference: Related Documents

| Document | Purpose |
|----------|---------|
| `PILLAR_LEAK_AUDIT_20260822.md` | Complete violation inventory |
| `PILLAR_REFACTOR_PLAN_20260822.md` | Phased execution plan |
| `SOVEREIGN_MANDATES.md` | M2 Engine-Stack Firewall (Mandate 2) |
| `PIVOT_LOG_CANONICAL.md` §1200-1210 | D180 canonical ruling |
| `CREDITS.md` | Heritage registry (id Software patterns) |
| `src/omega/oracle/entity_registry.py` | Engine implementation (source of truth) |

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_mining ⬡ COMPLETE*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
