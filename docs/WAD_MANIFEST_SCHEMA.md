# WAD Manifest Schema — Single Canonical Reference

> **Status:** ACTIVE
> **Date:** 2026-11-18
> **Scope:** All Omega Engine WADs (IWAD + PWAD)
> **Validator:** `scripts/validate_wad.py` + `scripts/lint_wad.py`

---

## 1. WAD Directory Structure

```
<wad_name>/
├── manifest.yaml          # Required — WAD identity, version, type, entities
├── entities/              # Required directory (may be empty)
│   ├── <entity_id>.yaml   # Flat entity definition (entity: envelope)
│   └── <entity_id>/       # Directory form (soul + entity + card)
│       ├── <entity_id>.yaml
│       ├── soul.yaml       # Identity contract (axioms, directives, voice)
│       ├── voice_dna.md    # Voice characteristics (referenced by soul.yaml)
│       └── card_assignment_*.yaml  # Tarot card correspondences (optional)
├── voices/                # Voice interface personas
│   └── <voice_id>.yaml
├── hierarchy.yaml         # Rank/recursion hierarchy (optional, default location)
├── dispatch.yaml          # Subagent dispatch config (optional, falls back to IWAD)
├── world/                 # VR world lumps (optional)
│   └── <sector_id>/
│       └── <lump_id>.yaml
├── ingestion/             # Domain ingestion configs (optional)
│   └── domains.yaml
├── templates/             # Card/entity templates (optional)
├── adapters/              # Memory adapter modules (optional)
└── meditate/              # Meditation lenses (optional)
    └── lenses.yaml
```

---

## 2. manifest.yaml

### Schema (V1 core + V2 heritage, extra=forbid)

```yaml
wad:
  name: "my_wad"              # required, non-empty string
  version: "1.0.0"            # required, non-empty string
  entities: []                 # required, list or dict
  author: "Your Name"         # optional string
  description: "..."          # optional string
  license: "Apache-2.0"       # optional string
  type: "iwad"                # optional: "iwad" or "pwad"
  mode: "production"          # optional string
  requires_engine: ">=1.6.0"  # optional semver specifier
  startup:                    # optional dict
    message: "WAD loaded."
  voices:                     # optional list or dict
    primary: "iris.yaml"
    secondary: []
  vr_scenes: []               # optional list or dict
  dependencies: []            # optional list or dict (WAD names)
  hierarchy: "hierarchy.yaml"  # optional relative path string
  priority: 0                  # optional int (PWADs: 1+)
  adapters:                   # optional list or dict
    memory:
      module: "omega.memory.adapters.mnemosyne_adapter"
      class: "MnemosyneAdapter"
```

### Manifest field types

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | ✅ | Non-empty |
| `version` | string | ✅ | Non-empty |
| `entities` | list or dict | ✅ | Loader scans `entities/` dir regardless |
| `author` | string | ❌ | |
| `description` | string | ❌ | |
| `license` | string | ❌ | |
| `type` | string | ❌ | `"iwad"` or `"pwad"` |
| `mode` | string | ❌ | e.g. `"production"`, `"personal"` |
| `requires_engine` | string | ❌ | Semver specifier, e.g. `">=1.6.0"` |
| `startup` | dict | ❌ | `{"message": "..."}` |
| `voices` | list or dict | ❌ | `{"primary": "iris.yaml", "secondary": []}` |
| `vr_scenes` | list or dict | ❌ | |
| `dependencies` | list or dict | ❌ | WAD names this WAD depends on |
| `hierarchy` | string | ❌ | Relative path to hierarchy file |
| `priority` | int | ❌ | PWAD override priority (1+) |
| `adapters` | list or dict | ❌ | Memory adapter config |

### IWAD vs PWAD

| Property | IWAD (base) | PWAD (override) |
|----------|-------------|-----------------|
| `type` | `"iwad"` | `"pwad"` |
| Load priority | 10 (base) | 100 + manifest.priority |
| Load order | First | After IWAD + dependencies |
| Entities | Define all base entities | Override or add entities |
| Shadow-Stacking | Base layer | Overrides IWAD entities with same name |

---

## 3. Entity YAML (`entity:` envelope)

```yaml
entity:
  name: "kali"                # required string, max 128 chars
  domains:                    # required list, max 20 items
    - vision
    - strategy
  personality: "You are Kali..."  # optional string
  temperature: 0.5             # optional float, 0.0–2.0
  context_window: 8192        # optional int, 1–131072
  slots: []                   # optional list
  role: "Founder"             # optional string
  container: false            # optional bool
  port: null                  # optional int, 1–65535
  model: "opencode/big-pickle"  # optional string (defaults to DEFAULT_ENTITY_MODEL)
  # WAD-specific fields (archetype, element, sigil, etc.) become metadata
```

### Entity field types

| Field | Type | Required | Range |
|-------|------|----------|-------|
| `name` | string | ✅ | max 128 chars |
| `domains` | list | ✅ | max 20 items |
| `personality` | string | ❌ | |
| `temperature` | float | ❌ | 0.0–2.0 |
| `context_window` | int | ❌ | 1–131072 |
| `slots` | list | ❌ | |
| `role` | string | ❌ | |
| `container` | bool | ❌ | |
| `port` | int | ❌ | 1–65535 |
| `model` | string | ❌ | Defaults to `opencode/big-pickle` |
| `nodes` | list | ❌ | |
| `sovereignty` | any | ❌ | |
| (any other) | any | ❌ | Becomes WAD metadata (D-282) |

---

## 4. soul.yaml (Identity Contract)

### ANAi Schema (`identity:` + `axioms:` + `directives:` + `voice:`)

```yaml
identity:
  keeper: "kali"              # required — entity name
  epithet: "The Voidmother"   # optional
  seat: "Dark (P6–P10)"      # optional
  version: "0.1.0-draft"     # optional
  status: "draft"             # optional
  persona_boundary: "..."     # optional — hoisted above fold in render

axioms:                       # optional list
  - id: "KALI-001"
    text: "Creation and destruction are the same rhythm."
    links: ["KALI-002"]       # optional cross-references

directives:                   # optional list
  - id: "D-KALI-001"
    rule: "Hold the failure curriculum as a syllabus."

principles: []                # optional list of strings

voice:                        # optional dict
  dna_ref: "voice_dna.md"
  default_preset: "shadow_work"
  base_weights:
    fierce: 0.9
    tender: 0.5

sovereignty:                  # optional dict
  wing: "wing_kali"
  diary_agent: "kali"
  kg_prefix: "kali_n1:"

held: []                      # optional list (non-negotiables)
```

### OED Schema (`entity:` + `identity:` values/strengths)

```yaml
entity:
  name: "Lilith"
  short: "LI"                 # 2-6 chars
  archetype: "Runtime Oversoul"
  hierarchy_level: 2
  sovereignty_level: 6
  element: "Void"
  domain: "Runtime Oversoul"
  soul_version: "6.1"
  last_updated: "2026-09-25T05:46:00Z"
  lessons_learned: []

identity:
  voice_summary: "..."
  values: [sovereignty, freedom]
  strengths: [boundary, refusal]
  growth_areas: []
```

### Researcher Schema (`entity:` + domain_affinities + methodology)

```yaml
entity:
  id: "researcher_humboldt"
  name: "Alexander von Humboldt"
  archetype: "Universal Synthesist / Polymath Explorer"
  epithet: "The Last Man Who Knew Everything"
  entity_class: "Researcher"
  born: 1769
  died: 1859
  domain_affinities:
    - local_ai: "Quantification of nature"
  methodology:
    - "Measure everything"
  voice_dna:
    tone: "Precise, lyrical"
    register: "Scientific German precision"
    metaphors: [isotherms, magnetic curves]
    cadence: "Long periodic sentences"
    quirks:
      - "Opens with a measurement"
  sovereignty:
    - "Own wing: wing_researcher_humboldt"
  persistence:
    gnosis_lock_integration: true
    mempalace_wing: "wing_researcher_humboldt"
  federation:
    node_0_needs: "Correspondence archive"
    node_1_active: "Field notebooks"
  instruments:
    - "Barometer (pressure)"
  mount_chimborazo:
    elevation_m: 6263
    date: "1802-06-23"
    insight: "Vegetation zones stack globally"
    quote: "Nature is a unified whole..."

card_assignments: []            # Researchers hold no card seats

well_seeds:                     # Optional Well corrections
  - kind: "correction"
    domain: "local_ai"
    rule: "Measure first, theorize second"
    rationale: "Benchmarks before architecture"
```

### Axiom ceiling

- **Maximum axioms per soul:** 20 (raised from 15 for Lilith's 19 axioms)
- Axioms should have `id` and `text` fields
- `links` field is optional (cross-references between axioms)

---

## 5. voices/<voice_id>.yaml

```yaml
voice:
  name: "Lilith Empress"        # required
  activation: "hey lilith"     # optional
  personality: "..."           # required
  temperature: 0.8              # optional float
  top_p: 0.9                   # optional float
  model_recommendation: "opencode/big-pickle"  # optional
  tags: [arcana, tarot]        # optional list
  dna_ref: "voice_dna.md"      # optional (relative to entity dir)
```

---

## 6. dispatch.yaml

```yaml
entities:
  - name: "kali"               # lowercase agent key
    role: "GRAND_OVERSIGHT"    # ROLE_CONSTANT
    mode: "primary"            # "primary" or "subagent"
    purpose: "Grand Oversight"
    capabilities: [oversight, delegation]
    domains: [strategy, architecture]
    slot: null                 # "SX" or null
    task_tool_type: "general"  # general | buildmaster | verity | node | explore
    owned_files: []             # list of file paths
    model: "opencode/big-pickle"  # optional (defaults to DEFAULT_ENTITY_MODEL)
```

### Fallback behavior

If a PWAD has no `dispatch.yaml`, the loader falls back to the IWAD's `dispatch.yaml` (`_omega_default`).

---

## 7. hierarchy.yaml

```yaml
hierarchy:
  <node_id>:
    name: "Kali"
    title: "Founder — Grand Oversight"
    role: "Sets direction"
    voice: "I dance because..."
    governs: [maat_cto, lilith_ciso]  # list of child node IDs
    reports_to: kali_founder            # parent node ID
    archetype: "The Founder"
    element: "Aether"
    governs_slots: [S1, S2, S3]       # optional slot list
    contains: [lilith_unifier]         # optional containment
    keeper: null                       # optional entity name or null
    oversoul: maat_cto                 # optional oversoul reference
```

---

## 8. World Lumps (world/<sector_id>/<lump_id>.yaml)

```yaml
lump_id: "example_lump"
sector_id: "sector_01"
world_data:
  # arbitrary world state data
metadata:
  wad_source: "arcana_novai"
  path: "config/wads/arcana_novai/world/sector_01/example_lump.yaml"
```

---

## 9. Validation Tools

| Tool | Command | What it checks |
|------|---------|----------------|
| `validate_wad.py` | `python scripts/validate_wad.py <wad_dir>` | Manifest schema, entity files, voice refs, hierarchy, souls, card assignments, world lumps |
| `lint_wad.py` | `python scripts/lint_wad.py <wad_dir>` | Duplicate keys, axiom ceiling, voice_dna refs, hierarchy integrity, card refs, dual-tree drift |
| `validate_soul_architecture.py` | `python scripts/validate_soul_architecture.py` | Axiom coverage, flat-list contract, axiom ceiling (20), duplicate keys |

---

## 10. PWAD Override Rules (Shadow-Stacking)

1. **IWAD loads first** (priority 10 + manifest.priority)
2. **PWAD loads after** (priority 100 + manifest.priority)
3. **Entity collision:** PWAD entity with same canonical name overrides IWAD entity
4. **Name canonicalization:** Apostrophes stripped, lowercased, spaces → underscores (`Ma'at` → `maat`)
5. **Layer preservation:** Both IWAD and PWAD layers are tracked in `_wad_sources`
6. **Unload:** `unload_wad()` removes only the specified WAD's layers, preserving others
7. **Dispatch fallback:** PWAD without `dispatch.yaml` falls back to IWAD's

---

## 11. Soul Rendering

```bash
# Render a single entity's soul to stdout
python scripts/soul_render.py <entity_id> [--wad <wad_name>] [--wads-dir <path>]

# List all renderable entities in a WAD
python scripts/soul_render.py --all [--wad <wad_name>]
```

Supports both ANAi (`identity:`) and OED (`entity:`) soul schemas. Output is target-neutral markdown.

---

## 12. WAD Scaffold

```bash
# Create a new PWAD skeleton
python scripts/create_wad.py my_wad --type pwad

# Create a new IWAD skeleton
python scripts/create_wad.py my_iwad --type iwad
```

---

## 13. Runtime WAD Switching

```python
# Via Omega Hub MCP tool
wad_switch(stack_name="arcana_novai", action="switch")
wad_switch(action="list")
wad_switch(stack_name="arcana_novai", action="unload")
```

Or programmatically:
```python
result = await wad_loader.wad_switch("arcana_novai")
# Returns: {success, switched_to, wad_type, priority, unloaded, loaded_wads, entity_count, startup_message, hierarchy_path}
```
