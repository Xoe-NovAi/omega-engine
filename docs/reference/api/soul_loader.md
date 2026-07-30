# 🔱 SoulLoader — Public/Private Soul Split (R19)
**AP Token**: `AP-API-SOUL-LOADER-v1.0.0`
⬡ OMEGA ⬡ P3 ⬡ soul_loader ⬡ API-REFERENCE
**Package**: `omega.soul`

---

## Overview

The `omega.soul` package implements the **R19 Soul Privacy Model** — splitting entity soul data into PUBLIC (git-tracked), BONDED, and PRIVATE (gitignored, encrypted) tiers. This ensures that sensitive entity data never leaks into version control while keeping the public identity graph navigable by all agents.

### Module: `omega.soul.loader`

| Export | Type | Purpose |
|--------|------|---------|
| `SoulLoader` | class | Loader with visibility-tier splitting and privacy-filtered recall |
| `create_soul_loader(entity_name)` | factory | Convenience factory for `SoulLoader` |

---

## SoulLoader

```python
class SoulLoader(entity_name: str, base_path: Optional[Path] = None)
```

### Visibility Tiers (Class Constants)
| Constant | Value | Purpose |
|----------|-------|---------|
| `VISIBILITY_PUBLIC` | `"public"` | Git-tracked — identity, archetype, domain, public directives |
| `VISIBILITY_BONDED` | `"bonded"` | Git-tracked but redacted — visible only to bonded entities |
| `VISIBILITY_PRIVATE` | `"private"` | Gitignored — memories, evolution data, private skills |

### Directory Structure
```
data/entities/{entity_name}/
├── soul.public.yaml           # PUBLIC + BONDED (bonded fields redacted)
├── soul.private/              # Gitignored
│   ├── memories/              # Private memories
│   ├── bonds/                 # Bond strength data
│   ├── skills/                # Private/evolving skills
│   └── evolution/             # Evolution history
```

### Key Methods

#### `load(visibility: Optional[str] = None, requester: Optional[str] = None) -> dict`
Load soul data filtered by visibility tier.

- `visibility`: One of `"public"`, `"bonded"`, `"private"`, or `None` (all)
- `requester`: Entity name — if set, BONDED data may be visible based on bond strength
- Returns: Dict of merged soul data

#### `save(data: dict, visibility: str = "public") -> None`
Save soul data to the appropriate tier file.

- `data`: Dict to save
- `visibility`: Which tier to save to

#### `recall(filter_tier: str = "public", requester: Optional[str] = None, bond_threshold: float = 0.5) -> dict`
Privacy-filtered recall based on requester identity and bond strength.

- `filter_tier`: Maximum tier to include (`"public"`, `"bonded"`, or `"private"`)
- `requester`: Entity requesting the data (for bond checks)
- `bond_threshold`: Minimum bond strength for BONDED access (default: 0.5)
- Returns: Filtered dict with PRIVATE data excluded for non-bonded requesters

#### `migrate_from_legacy() -> bool`
Migrate from legacy `soul.yaml` format to PUBLIC/BONDED/PRIVATE split.

- Reads existing `soul.yaml`, classifies fields by visibility tier
- Writes `soul.public.yaml` + `soul.private/` structure
- Backs up original to `soul.yaml.bak`
- Returns: `True` if migration happened

#### `list_tiers() -> dict`
List available data by visibility tier.

- Returns: `{"public": [...], "bonded": [...], "private": [...]}`

#### `get_bond_strength(other_entity: str) -> float`
Get bond strength with another entity (0.0 = no bond, 1.0 = maximum).

#### `set_bond_strength(other_entity: str, strength: float) -> None`
Set bond strength with another entity.

---

## Factory Functions

### `create_soul_loader(entity_name: str) -> SoulLoader`
```python
from omega.soul import create_soul_loader

loader = create_soul_loader("maat")
data = loader.load(visibility="public")
```

---

## R19 Compliance

| R19 Requirement | Implementation |
|-----------------|----------------|
| PUBLIC/BONDED/PRIVATE split | `soul.public.yaml` + `soul.private/` |
| Privacy-filtered recall | `recall()` method with bond strength check |
| Legacy migration | `migrate_from_legacy()` with backup |
| Gitignore integration | `soul.private/` is gitignored (via `.gitignore` patterns) |

---

## Cross-Reference

| System | Relation |
|--------|----------|
| `omega.privacy.kernel` | PrivacyKernel uses SoulLoader for accessing entity directives |
| `omega.config.loader` | ConfigLoader provides runtime config for privacy thresholds |
| `omega.soul_store` | Underlying atomic writer for all soul file operations |
| `SOVEREIGN_MANDATES.md` M11 | Soul Integrity mandates L1→L2→L3 distillation |
| `docs/research/R_SOUL_PRIVACY_MODEL.md` | Full R19 spec |

---

*⬡ OMEGA ⬡ P3 ⬡ soul_loader ⬡ v1.0.0*
