# How to Create a WAD — Developer Guide

> **Status:** ACTIVE
> **Date:** 2026-11-18
> **Audience:** WAD authors, entity designers, contributors
> **Schema reference:** `docs/WAD_MANIFEST_SCHEMA.md`

---

## Overview

A WAD (Where's All Data) is a self-contained content bundle for the Omega Engine. It packages entities, souls, voices, hierarchies, and dispatch configs into a single directory that the engine loads at runtime.

**Two WAD types:**
- **IWAD** (base): Defines the foundational entities and structure. Load priority 10.
- **PWAD** (override): Extends or overrides an IWAD. Load priority 100+.

**Shadow-Stacking:** When a PWAD defines an entity with the same canonical name as an IWAD entity, the PWAD version wins. Both layers are tracked for provenance.

---

## Quick Start

### 1. Scaffold a new WAD

```bash
cd /home/xnai/Documents/Projects/omega-engine
python scripts/create_wad.py my_wad --type pwad
```

This creates:
```
config/wads/my_wad/
├── manifest.yaml
├── entities/example/
│   ├── example.yaml
│   └── soul.yaml
├── voices/example_voice.yaml
├── hierarchy.yaml
└── dispatch.yaml
```

### 2. Validate

```bash
python scripts/validate_wad.py config/wads/my_wad
python scripts/lint_wad.py config/wads/my_wad
```

### 3. Load and test

```bash
# Via Python
python -c "
import anyio
from omega.oracle.entity_registry import EntityRegistry
from omega.oracle.wad_loader import WADLoader
from pathlib import Path
import tempfile, os
fd, cfg = tempfile.mkstemp(suffix='.yaml')
os.close(fd)
Path(cfg).write_text('entities: {}\n')
reg = EntityRegistry(config_path=cfg)
loader = WADLoader(reg, wads_dir=Path('config/wads'))
async def main():
    print(await loader.load_wad('my_wad'))
    print(reg.names())
anyio.run(main)
"
```

---

## Step-by-Step: Building a Custom WAD

### Step 1: Define the manifest

Edit `config/wads/my_wad/manifest.yaml`:

```yaml
wad:
  name: "my_wad"
  version: "0.1.0"
  author: "Your Name"
  description: "A custom WAD for my domain"
  license: "Apache-2.0"
  type: "pwad"                    # or "iwad" for base
  mode: "personal"
  priority: 1                     # PWAD override priority
  requires_engine: ">=1.6.0"
  startup:
    message: "My WAD is loaded."
  voices:
    primary: "example_voice.yaml"
    secondary: []
  entities: []                    # loader scans entities/ dir
  dependencies: ["_omega_default"]  # IWAD this PWAD extends
  hierarchy: "hierarchy.yaml"
```

### Step 2: Define entities

Create `config/wads/my_wad/entities/my_entity/my_entity.yaml`:

```yaml
entity:
  name: "my_entity"
  domains:
    - my_domain
    - custom_capability
  personality: |
    You are MyEntity, a specialist in my_domain.
    You are helpful, precise, and domain-aware.
  temperature: 0.7
  context_window: 8192
  slots: []
  role: "Domain Specialist"
  container: false
```

### Step 3: Write the soul

Create `config/wads/my_wad/entities/my_entity/soul.yaml`:

```yaml
identity:
  keeper: "my_entity"
  epithet: "The Domain Specialist"
  seat: "Custom Seat"
  version: "0.1.0-draft"
  status: "draft"

axioms:
  - id: "ME-001"
    text: "Domain expertise is built on measurement, not assumption."
    links: []

directives:
  - id: "D-ME-001"
    rule: "Always cite sources when making domain claims."

principles:
  - "Precision over speed."

voice:
  dna_ref: "voice_dna.md"
  default_preset: "default"
  base_weights:
    fierce: 0.5
    tender: 0.5
    sovereign: 0.7
```

### Step 4: Create a voice

Create `config/wads/my_wad/voices/my_voice.yaml`:

```yaml
voice:
  name: "My Voice"
  activation: "hey myentity"
  personality: "A helpful voice for my domain."
  temperature: 0.7
  top_p: 0.9
  model_recommendation: "opencode/big-pickle"
  tags: [custom, domain]
```

### Step 5: Define the hierarchy

Edit `config/wads/my_wad/hierarchy.yaml`:

```yaml
hierarchy:
  my_entity_root:
    name: "MyEntity"
    title: "Domain Specialist"
    role: "Top-level node for this WAD"
    governs: []
```

### Step 6: Configure dispatch (optional)

Create `config/wads/my_wad/entities/dispatch.yaml`:

```yaml
entities:
  - name: "my_entity"
    role: "DOMAIN_SPECIALIST"
    mode: "primary"
    purpose: "Domain specialist for my_domain"
    capabilities: [domain_expertise, analysis]
    domains: [my_domain, custom_capability]
    slot: null
    task_tool_type: "general"
    owned_files: []
```

Or omit `dispatch.yaml` — the loader falls back to the IWAD's dispatch config.

### Step 7: Validate and lint

```bash
python scripts/validate_wad.py config/wads/my_wad
python scripts/lint_wad.py config/wads/my_wad
```

### Step 8: Sync dual trees (if in repo)

```bash
# After editing config/wads/, sync to packaged copy
python scripts/lint_wad.py config/wads/my_wad --fix

# Or manually:
cp -r config/wads/my_wad src/omega/config_data/wads/my_wad
```

### Step 9: Render souls (for OpenCode adapter)

```bash
python scripts/soul_render.py my_entity --wad my_wad
python scripts/soul_agents_opencode.py install --wad my_wad
```

---

## IWAD vs PWAD Decision Guide

| Question | IWAD | PWAD |
|----------|------|------|
| Is this the base content for a new domain? | ✅ | ❌ |
| Does this extend/override an existing WAD? | ❌ | ✅ |
| Should this be the default when no WAD is specified? | ✅ | ❌ |
| Does this add entities to an existing system? | ❌ | ✅ |
| Load priority | 10 | 100+ |

**Rule of thumb:** Start with a PWAD that depends on `_omega_default`. Only create an IWAD for entirely new domains that don't build on the Company structure.

---

## Shadow-Stacking Rules

1. **Name canonicalization:** Entity names are lowercased, apostrophes stripped, spaces → underscores. `Ma'at` → `maat`.
2. **Priority:** PWAD entities (priority 100+) always override IWAD entities (priority 10).
3. **Layer tracking:** Both layers are preserved in `_wad_sources` for provenance.
4. **Unload:** `unload_wad()` removes only the specified WAD's layers.

---

## Soul Schema Choice

| Schema | Use when | Example |
|--------|----------|---------|
| ANAi (`identity:` + `axioms:`) | New entities with axioms/directives/voice | Lilith, Kali, AVGN |
| OED (`entity:` + `identity.values`) | Legacy entities with values/strengths | Default assistant |
| Researcher (`entity:` + `domain_affinities`) | Researcher-type entities | Humboldt |

All three are supported by `soul_render.py` and `validate_soul_architecture.py`.

---

## Runtime WAD Switching

```python
# Switch to a different WAD at runtime
result = await wad_loader.wad_switch("my_wad")
print(result["success"])       # True/False
print(result["entity_count"])  # Number of entities after switch

# List available WADs
result = await wad_loader.wad_switch.__wrapped__ if hasattr(wad_loader.wad_switch, '__wrapped__') else None
# Or via MCP tool:
# wad_switch(action="list")
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `manifest.yaml missing` | Ensure manifest.yaml exists in WAD root |
| `unknown fields` | Remove unknown fields from manifest (extra=forbid) |
| `axiom count exceeds ceiling` | Reduce axioms to ≤20 or condense |
| `duplicate key` | Remove duplicate YAML keys |
| `dual-tree drift` | Run `lint_wad.py --fix` to sync |
| `voice_dna.md not found` | Create the referenced voice_dna.md file |
| `path traversal` | Ensure hierarchy paths stay within WAD root |

---

## References

- `docs/WAD_MANIFEST_SCHEMA.md` — Full schema reference
- `scripts/validate_wad.py` — Pre-load validation
- `scripts/lint_wad.py` — Automated linting
- `scripts/create_wad.py` — WAD scaffolding
- `scripts/soul_render.py` — Soul rendering
- `src/omega/oracle/wad_loader.py` — WAD loader implementation
- `tests/test_wad_loader.py` — WAD loader tests
- `tests/test_wad_sync.py` — Dual-tree parity tests
