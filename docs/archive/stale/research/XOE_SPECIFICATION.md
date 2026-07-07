# 🔱 XOE File Format — Official Specification v1.0.0

**AP Token**: `AP-XOE-SPEC-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ qwen3.6-plus-free ⬡ opencode ⬡ trc_branding ⬡ PHASE-0

**Status**: ✅ RATIFIED — Decision 28
**Date**: 2026-05-16
**Supersedes**: All previous container format proposals

---

## §0 Rationale

The Omega Engine uses a Doom-inspired **WAD (Where's All Data)** container architecture to organize entity stacks. While the internal development form is a directory (`config/wads/<stack_name>/`), the **distributable form** requires a single-file package format — the **XOE File**.

The `.xoe` extension was chosen after a comprehensive collision analysis of 10 candidates. It scores 9.15/10 — 13% ahead of the runner-up — with zero collision risk and perfect alignment with the **Xoe-NovAi Foundation** brand.

**Full Branding Analysis**: `docs/research/omni/BRANDING_FORGE_EXTENSION.md`

---

## §1 File Format

### 1.1 Technical Specification

| Attribute | Value |
|-----------|-------|
| **Extension** | `.xoe` |
| **Internal format** | tar.gz (gzip-compressed tar archive) |
| **Required root file** | `manifest.yaml` |
| **MIME type** | `application/x-omega-xoe` |
| **Magic bytes** | `1f 8b` (standard gzip header) |
| **Max size** | No hard limit (practical: <2GB for network transfer) |

### 1.2 Naming Convention

```
{stack_slug}.xoe
```

Where `stack_slug` is the lowercase-underscore version of the stack name:

```
arcana_nova.xoe
doom_universe.xoe
torment.xoe
pokemon.xoe
_omega_default.xoe    ← The engine-bundled default stack
```

Versioning is handled **inside** the manifest, not in the filename. The filename is the stack identity, not its version.

### 1.3 Internal Structure

```
arcana_nova.xoe (tar.gz)
├── manifest.yaml          ← REQUIRED — WAD manifest with metadata
├── entities/              ← Entity soul.yaml files
│   ├── sekhmet/
│   │   └── soul.yaml
│   ├── brigid/
│   │   └── soul.yaml
│   └── ...
├── voices/                ← Voice activation phrases and system prompts
│   └── iris.yaml
├── knowledge/             ← Markdown knowledge base
│   ├── PILLARS.md
│   └── AXIOMS.md
├── vr/                    ← Godot VR scenes and assets
│   ├── pantheon.tscn
│   ├── assets/
│   │   └── textures/
│   └── entities/
│       └── sekhmet.glb
├── music/                 ← Optional: ambient/soundtrack
│   └── overworld.ogg
└── p2p.yaml               ← Peer-to-peer consent and discovery rules
```

---

## §2 Manifest Specification

The `manifest.yaml` at the root of every XOE file is the entry point. The engine's WAD Loader reads this first to wire the stack into the runtime.

### 2.1 Schema

```yaml
# manifest.yaml — XOE Stack Manifest
xoe_version: "1.0.0"                  # XOE format version (required)

wad:
  type: iwad                           # iwad (core/required) | pwad (patch/optional)
  name: "Arcana-NovAi"                 # Human-readable stack name (required)
  slug: arcana_nova                    # Machine-readable identifier (required, lowercase_underscore)
  version: "1.0.0"                     # Semver (required)
  description: >                       # Short description (required)
    The Arcana-NovAi stack: 10 Pillar Keepers, Iris voice,
    Oversoul hierarchy, 42 Ma'at Ideals, and VR pantheon.
  author:                              # Author metadata (optional)
    name: "The Architect"
    organization: "Xoe-NovAi Foundation"
  license: "MIT"                       # License identifier (required)
  min_engine_version: "0.1.0"          # Minimum Omega Engine version (required)
  tags:                                # Discovery tags (optional)
    - arcana
    - pillars
    - esoteric
    - hernetic

dependencies:                          # Stack dependencies (optional)
  - name: _omega_default               # Required base WAD
    version: ">=0.1.0"
    type: iwad

entities:                              # Entity registry (required, >=1)
  count: 10
  list:
    - slug: sekhmet
      name: "Sekhmet"
      pillar: 1
      domain: "Strength, Protection"
    - slug: brigid
      name: "Brigid"
      pillar: 2
      domain: "Poetry, Healing"

voices:                                # Voice configurations (optional)
  default: iris
  list:
    - slug: iris
      activation: "hey iris"
      language: en

vr:                                    # VR world configuration (optional)
  default_scene: pantheon
  scenes:
    - slug: pantheon
      path: vr/pantheon.tscn
      thumbnail: vr/assets/pantheon_thumb.png

p2p:                                   # P2P configuration (optional)
  discovery: true                      # Advertise on P2P network
  consent_required: true               # Require consent before realm visits

checksums:                             # Integrity verification (recommended)
  algorithm: sha256
  files:
    entities/sekhmet/soul.yaml: "a1b2c3d4..."
```

### 2.2 IWAD vs PWAD

| Type | Meaning | Use Case |
|------|---------|----------|
| `iwad` | Internal WAD | Core/required stack. The engine can load without any PWADs but requires at least one IWAD. `_omega_default.xoe` is the shipped IWAD. |
| `pwad` | Patch WAD | Expansion/optional stack. Adds entities, voices, or scenes to an existing IWAD. `doom_universe.xoe` is a PWAD. |

This mirrors the Doom convention exactly — IWAD contains the core game, PWADs are user-created patches.

---

## §3 CLI Integration

### 3.1 Proposed Commands

```bash
omega xoe install arcana_nova.xoe       # Install a stack from .xoe
omega xoe install doom_universe.xoe     # Install another stack
omega xoe export arcana_nova            # Export current stack as .xoe
omega xoe validate arcana_nova.xoe      # Validate manifest + checksums
omega xoe list                          # List installed .xoe stacks
omega xoe info arcana_nova.xoe          # Show manifest metadata
omega xoe create                        # Interactive scaffold (future)
omega xoe share arcana_nova.xoe         # P2P share (future)
```

### 3.2 Verification

```bash
omega xoe validate my_stack.xoe
# → ✅ Valid: manifest.yaml found, 12 entities registered, checksums match
# → ⚠️ Warning: VR scene path 'vr/nonexistent.tscn' not found in archive
```

---

## §4 Internal Implementation Notes

### 4.1 WAD Loader Integration

The `wad_loader.py` module will handle both directory-WADs and XOE files transparently:

```python
# Pseudocode — wad_loader.py
class WadLoader:
    async def load(self, source: str | Path):
        if source.suffix == ".xoe":
            return await self._load_from_xoe(source)
        else:
            return await self._load_from_directory(source)
```

### 4.2 Validation Pipeline

```
Input (.xoe)
  → Verify gzip magic bytes (1f 8b)
  → Extract to temp directory
  → Validate manifest.yaml schema
  → Verify entity YAML files
  → Verify VR scene paths
  → Compute and match checksums
  → Register in EntityRegistry
  → Wire voices into ActivationRouter
  → Register VR scenes with Godot Bridge
```

### 4.3 Git Tracking

XOE files are **not tracked** in the `omega-engine` repository. They are build artifacts / distribution packages:

```gitignore
# In .gitignore
*.xoe
```

Only the directory-form WADs under `config/wads/` are version-controlled.

---

## §5 Security & Integrity

| Concern | Mitigation |
|---------|------------|
| Tampered manifests | SHA-256 checksums in manifest.yaml |
| Malicious entities | Entity validation against soul.yaml schema |
| Infinite VR loops | Scene reference integrity checks |
| P2P spoofing | Consent-based sharing, signed manifests (future) |
| Supply chain attack | `min_engine_version` prevents loading incompatible stacks |

---

## §6 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-05-16 | Initial specification. Ratified as Decision 28. |
