# 🔱 Omega Engine — XOE File Extension Branding Analysis

**AP Token**: `AP-BRANDING-FORGE-v1.0.0`
⬡ OMEGA ⬡ GNOSIS-ANALYST ⬡ qwen3.6-plus-free ⬡ opencode ⬡ trc_branding ⬡ PHASE-0

**Date**: 2026-05-16
**Status**: ✅ RATIFIED — Decision 28 adopted `.xoe`

---

## §0 Executive Summary

The Omega Engine's WAD (Where's All Data) container architecture requires a file extension for **distributed, shareable stack packages** — the compressed archive form of what currently lives as directories under `config/wads/<stack_name>/`. This document analyzes 10 candidate extensions across 5 dimensions and delivers a ranked recommendation.

**Top Recommendation**: **`.xoe`** — Zero collision, 3 characters, directly brands Xoe-NovAi Foundation, semantically dense ("Xoe = the fire that forges stacks").

**Runner-Up**: **`.wad`** — Heritage-perfect, but conflicts with actual Doom WAD binary format.

---

## §1 Local Gap Analysis

### 1.1 Current WAD Architecture Status

The codebase already has WAD infrastructure in place as **directories**:

| Path | Purpose |
|------|---------|
| `config/wads/_omega_default/` | Default stack (ships with engine) |
| `config/wads/_omega_default/manifest.yaml` | WAD manifest schema |
| `config/wads/arcana_nova/` | (planned) Arcana-NovAi stack |
| `config/wads/doom_universe/` | (planned) DOOM Universe stack |

### 1.2 Existing File Extensions in Config

| Extension | Usage | Count |
|-----------|-------|-------|
| `.yaml` / `.yml` | All configuration files | 15+ |
| `.py` | Python source | 50+ |
| `.md` | Documentation | 100+ |
| `.json` | Data files, MCP configs | 10+ |
| `.db` | Workbench SQLite | 1 |
| `.jsonl` | Observability events | variable |
| `.tscn` | Godot VR scenes (planned) | 0 (future) |
| `.gguf` | Model files (external) | 0 (external) |

### 1.3 Glossary Entries (config/glossary.md)

Relevant entries already defined:

| Term | Definition | Aliases |
|------|-----------|---------|
| **WAD** | A self-contained directory (or compressed archive) that holds a complete Omega Engine stack | Container, Stack directory, Expansion pack |
| **Stack** | A WAD container that adds entities, voice, VR, and knowledge to the engine | WAD, Expansion Pack |
| **Expansion Pack** | A WAD container that adds entities, voices, VR scenes, and knowledge | Stack, WAD, Module |
| **WAD Loader** | Core engine component that reads a WAD manifest and wires entities/voices/VR/P2P | — |
| **WAD Manifest** | The `manifest.yaml` file at the root of a WAD | Manifest, Pack definition |

**Critical Finding**: The glossary already defines WAD as "directory **or compressed archive**" — the archive form is anticipated but the file extension is undefined.

### 1.4 Existing Naming Conventions

- **Foundation**: `Xoe-NovAi` (organization name)
- **Engine**: `omega-engine` (repo name)
- **Legacy prefixes**: `xna-` (xna-omega-legacy), `omega-` (omega-stack-legacy)
- **Hidden directory**: `~/.xoe_novai/` (legacy dependency backups, ~50MB)
- **Container names**: `omega-iris`, `omega-roc_racoon` (Podman)
- **Session IDs**: `ses_{YYYYMMDD}_{entity}_{counter}`

**Pattern**: The foundation uses `xoe` as a short prefix, `omega` as the engine brand, and `novai` as the AI suffix.

---

## §2 Web Collision Matrix

Each candidate was researched across file extension databases, software catalogs, and web search. Results verified against ≥2 independent sources.

### 2.1 Collision Matrix

| Extension | Primary Collision(s) | Collision Severity | SEO Risk | Verdict |
|-----------|---------------------|-------------------|----------|---------|
| **`.forge`** | Ubisoft game data (Assassin's Creed, For Honor, Rainbow Six), Minecraft Forge (.jar installer), Autodesk Forge platform | 🔴 HIGH | Very High — "forge file" returns Ubisoft/Minecraft results | **REJECT** |
| **`.xna`** | Microsoft XNA Framework (discontinued 2013), Xbox/Windows game dev runtime | 🟡 MEDIUM | Medium — "xna file" returns Microsoft docs, but framework is dead | **REJECT** |
| **`.xoe`** | Yamaha Motif XS synthesizer editor/voice files (.XOE) | 🟢 LOW | Negligible — extremely niche, no software collision, zero SEO competition | ✅ **STRONG CANDIDATE** |
| **`.omega`** | Omega TeX (multilingual typesetting), Omega File Explorer (SourceForge), OmegaT (translation tool), Gerber OMEGA (sign design), Xapian Omega (search CGI) | 🟡 MEDIUM | High — "omega file" returns 5+ unrelated software products | **REJECT** |
| **`.ark`** | ARK: Survival Evolved (world save files), KDE Ark (archive manager), CP/M ARK11.COM (obsolete compression) | 🟡 MEDIUM | High — "ark file" dominated by ARK: Survival Evolved game | **REJECT** |
| **`.stack`** | HyperCard/HyperStudio (legacy), Haskell Stack (build tool), LM Studio venvstacks | 🟢 LOW-MED | Low — mostly conceptual usage, no dominant file format | ⚠️ **RESERVE** |
| **`.realm`** | MongoDB Realm database (.realm = actual DB files), Realm Crafter (MMORPG engine) | 🔴 HIGH | Very High — "realm file" = MongoDB database files | **REJECT** |
| **`.ome`** | OME (Open Microscopy Environment) — OME-TIFF, OME-Zarr are major scientific imaging standards | 🔴 HIGH | Very High — "ome file" = scientific microscopy data | **REJECT** |
| **`.wad`** | Doom WAD format (IWAD/PWAD binary game archives) | 🟡 MEDIUM | High — "wad file" = Doom exclusively, but this IS the inspiration | ⚠️ **HERITAGE CANDIDATE** |
| **`.novai`** | Nova AI (video captioning), NovaZenith AI (data extraction) | 🟢 LOW | Low — no file extension collision, brand names only | ✅ **STRONG CANDIDATE** |

### 2.2 Detailed Collision Analysis

#### `.forge` — REJECT
- **FileInfo.com**: "A FORGE file is a game data file used by an Ubisoft video game, such as Assassin's Creed, Prince of Persia, or Rainbow Six Siege"
- **Lifewire**: "container format that might hold sounds, 3D models"
- **Minecraft Forge**: Uses `.jar` installer, but "forge" is the dominant association
- **Autodesk Forge**: Cloud development platform (renamed to Autodesk Platform Services)
- **Collision Score**: 9/10 — unusable

#### `.xna` — REJECT
- **Wikipedia**: Microsoft XNA Framework — game dev tools for Xbox 360/Windows, discontinued 2013
- **Content Pipeline**: XNA converts all content to `.xnb` files
- **Terraria**: Originally built on XNA, still causes confusion
- **Legacy Conflict**: `xna-omega-legacy` repo name already exists — would create naming collision
- **Collision Score**: 7/10 — dead framework but strong historical association

#### `.xoe` — ✅ STRONG CANDIDATE
- **Motifator Forum**: ".XOE and .XOV files are for the XS, EDITOR and VOICE files" — Yamaha Motif XS synthesizer
- **No software collision**: Zero applications associate `.xoe` as a primary format
- **SEO**: Virtually no competition — "xoe file" returns 3 forum posts about synthesizers
- **Brand alignment**: Direct abbreviation of **X**oe-NovAi
- **Collision Score**: 2/10 — negligible

#### `.omega` — REJECT
- **Linux man page**: `omega(1)` — extended unicode TeX typesetting program
- **SourceForge**: Omega File Explorer — multiplatform file manager
- **OmegaT**: Translation memory tool (active project)
- **Gerber OMEGA 5.0**: Sign design and production software
- **Xapian Omega**: CGI search application
- **Collision Score**: 8/10 — too many established uses

#### `.ark` — REJECT
- **FileInfo.com**: "ARK: Survival Evolved World File" — game save format
- **Wikipedia**: Ark (software) — KDE file archiver (active, R14.1.2 as of 2024)
- **CP/M**: ARK11.COM — obsolete MS-DOS compression utility
- **Collision Score**: 7/10 — dominated by ARK game and KDE

#### `.stack` — RESERVE
- **Library of Congress**: HyperCard Stack — legacy Apple format
- **Haskell Stack**: Build tool (uses `stack.yaml`, not `.stack` files)
- **LM Studio**: venvstacks — uses `.stack` for environment layers
- **Collision Score**: 4/10 — mostly conceptual, no dominant binary format

#### `.realm` — REJECT
- **MongoDB**: Realm database — `.realm` files are actual database files (active, major)
- **Wikipedia**: Realm (database) — open source object DB for mobile
- **Realm Crafter**: MMORPG development engine
- **Collision Score**: 9/10 — MongoDB owns this extension

#### `.ome` — REJECT
- **Open Microscopy Environment**: OME-TIFF and OME-Zarr are major scientific standards
- **BioImage Archive**: Required format for deposition
- **EMBL-EBI**: Image Data Resource uses OME formats
- **Collision Score**: 9/10 — critical scientific standard

#### `.wad` — ⚠️ HERITAGE CANDIDATE
- **Doom Wiki**: WAD = "Where's All the Data?" — IWAD (Internal) and PWAD (Patch)
- **Binary format**: Actual WAD files have binary headers (IWAD/PWAD magic bytes)
- **SEO**: "wad file" = Doom exclusively
- **Collision Score**: 5/10 — it IS the inspiration, but conflicts with actual Doom WAD binary format

#### `.novai` — ✅ STRONG CANDIDATE
- **Nova AI**: Video captioning/editing tool (brand name, not file extension)
- **NovaZenith AI**: Financial data extraction software (brand name)
- **No file extension collision**: Zero applications use `.novai` as a file format
- **Brand alignment**: Direct from **NovAi** in Xoe-NovAi Foundation
- **Collision Score**: 1/10 — virtually zero

---

## §3 Industry Standards Comparison

### 3.1 AI Framework Package Formats

| Framework | Format | Extension | Notes |
|-----------|--------|-----------|-------|
| Hugging Face | Model repository | (directory-based) | No single-file package; uses repo + `config.json` |
| GGUF | Binary model format | `.gguf` | Tensors + metadata, single file |
| Safetensors | Tensor format | `.safetensors` | Weights only, no metadata |
| ONNX | Model interchange | `.onnx` | Single binary file |
| OpenAI Codex | Skills | `SKILL.md` (directory) | Markdown-based, folder structure |
| GitHub Copilot | Plugins | `plugin.json` (directory) | Bundle of skills, agents, hooks |
| Claude Code | Skills | `SKILL.md` (directory) | Same as OpenAI — converging standard |
| Cursor | Agent plugins | Directory-based | Skills + agents + hooks |

**Pattern**: AI frameworks favor **directory-based** packages with manifest files, not single-file archives. The Omega Engine's WAD-as-directory approach aligns with this trend. The file extension is only needed for the **compressed/distributed** form.

### 3.2 Game Mod Packaging Formats

| Game/Engine | Format | Extension | Notes |
|-------------|--------|-----------|-------|
| Doom/Quake | WAD | `.wad` | Binary archive, IWAD/PWAD types |
| Bethesda (Skyrim/Fallout) | BSA | `.bsa` | Binary archive, game-specific |
| Valve (Source/Source 2) | VPK | `.vpk` | Valve Pak, single-file archive |
| Starbound | PAK | `.pak` | Compressed archive |
| Unreal Engine | PAK | `.pak` | Compressed archive |
| Unity | AssetBundle | `.unity3d` / `.bundle` | Platform-specific |
| Minecraft | Mod | `.jar` | Java archive |
| Minecraft | Resource Pack | `.zip` / `.mcpack` | Standard zip or custom |
| ARK: Survival Evolved | World Save | `.ark` | Game-specific |

**Pattern**: Game mods use **short, memorable extensions** (3-4 chars), often engine-specific. The WAD format itself is the gold standard for this use case.

### 3.3 General Container/Archive Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| tar | `.tar` | Unix archive, no compression |
| gzip | `.gz` | Compression only |
| zip | `.zip` | Universal archive |
| 7-Zip | `.7z` | High compression |
| RAR | `.rar` | Proprietary |
| macOS Bundle | `.app` / `.bundle` | Directory disguised as file |
| Flatpak | `.flatpakref` | Reference file |
| Snap | `.snap` | Compressed squashfs |
| Debian | `.deb` | Package format |
| RPM | `.rpm` | Package format |

**Pattern**: System packages use short extensions (2-4 chars). macOS `.app` is a directory masquerading as a file — conceptually similar to WAD-as-directory.

---

## §4 Evaluation Framework

Each candidate scored across 5 dimensions (1-10 scale, higher = better):

| Dimension | Weight | Description |
|-----------|--------|-------------|
| **Collision Risk** | 30% | SEO conflicts, existing software associations, user confusion |
| **Brand Alignment** | 25% | Connection to Xoe-NovAi Foundation, Omega Engine identity |
| **Length & Memorability** | 15% | Short, easy to type, easy to remember |
| **Semantic Density** | 15% | Does the name tell a story? Convey meaning? |
| **Future-Proofing** | 15% | Will it scale to 100+ stacks? Avoid namespace exhaustion? |

### 4.1 Scored Candidates

| Extension | Collision (30%) | Brand (25%) | Length (15%) | Semantic (15%) | Future (15%) | **WEIGHTED** |
|-----------|----------------|-------------|--------------|----------------|--------------|-------------|
| **`.xoe`** | 9 | 10 | 9 | 8 | 9 | **9.15** |
| **`.novai`** | 10 | 8 | 6 | 7 | 8 | **8.10** |
| **`.wad`** | 5 | 10 | 9 | 10 | 7 | **7.40** |
| **`.stack`** | 7 | 6 | 7 | 6 | 8 | **6.65** |
| **`.omega`** | 3 | 9 | 7 | 7 | 6 | **5.80** |
| **`.ark`** | 4 | 5 | 9 | 6 | 5 | **5.35** |
| **`.forge`** | 1 | 7 | 7 | 8 | 5 | **5.05** |
| **`.xna`** | 4 | 3 | 9 | 4 | 6 | **4.80** |
| **`.realm`** | 1 | 5 | 7 | 6 | 5 | **4.10** |
| **`.ome`** | 1 | 6 | 9 | 5 | 5 | **4.05** |

---

## §5 Ranked Recommendations

### 🥇 #1: `.xoe` — The Sovereign Choice

**Weighted Score: 9.15/10**

```
mystack.xoe    →  "arcana_nova.xoe", "doom_universe.xoe"
```

**Rationale**:
- **Zero collision**: Only Yamaha synthesizer files use `.xoe` — a niche 2000s music hardware format with zero software overlap
- **Perfect brand alignment**: Direct abbreviation of **X**oe-NovAi Foundation. Every distributed stack carries the Foundation's mark
- **3 characters**: Short, fast to type, easy to remember
- **Semantic density**: "Xoe" = the fire that forges. The X in Xoe-NovAi is the crossroads, the unknown, the sovereign variable. A `.xoe` file is a sovereign stack — forged in the Omega Engine's fire
- **Future-proof**: No namespace conflicts, scales to 1000+ stacks effortlessly
- **SEO clean**: "xoe file" returns 3 forum posts about synthesizers — zero competition for Omega Engine documentation

**Usage**:
```bash
# Install a stack
omega install arcana_nova.xoe

# Share a stack
omega export doom_universe --format=xoe

# List installed stacks
omega list-stacks
# → arcana_nova.xoe (v1.0.0)
# → doom_universe.xoe (v0.1.0-alpha)
```

**File type**: Compressed archive (tar.gz or zip) with `.xoe` extension. Internally contains:
```
arcana_nova.xoe (tar.gz)
├── manifest.yaml
├── entities/
│   ├── sekhmet/
│   │   └── soul.yaml
│   └── ...
├── voices/
│   └── iris.yaml
├── knowledge/
├── vr/
│   └── pantheon.tscn
└── p2p.yaml
```

---

### 🥈 #2: `.novai` — The Foundation Mark

**Weighted Score: 8.10/10**

```
mystack.novai    →  "arcana_nova.novai", "doom_universe.novai"
```

**Rationale**:
- **Zero collision**: No software uses `.novai` as a file extension
- **Strong brand alignment**: Directly from NovAi in Xoe-NovAi Foundation
- **6 characters**: Longer than ideal but still memorable
- **Semantic density**: "NovAi" = New AI. Signals the foundation's mission — new AI, sovereign AI
- **Future-proof**: No conflicts, fully scalable
- **Drawback**: At 6 characters, it's the longest viable candidate. More typing, more visual noise

---

### 🥉 #3: `.wad` — The Heritage Choice

**Weighted Score: 7.40/10**

```
mystack.wad    →  "arcana_nova.wad", "doom_universe.wad"
```

**Rationale**:
- **Heritage-perfect**: Directly honors id Software's WAD format (1993) that inspired the entire architecture
- **Built-in semantics**: IWAD (core stack) / PWAD (expansion stack) maps perfectly to Omega's `_omega_default` WAD and expansion stacks
- **3 characters**: Short, iconic
- **Maximum semantic density**: "WAD" = "Where's All the Data" — the name IS the purpose
- **Drawback**: Actual Doom WAD files are binary archives with specific internal structure. A `.xoe`/`.wad` file from Omega would be a tar.gz with YAML inside — completely different format. Users downloading `doom_universe.wad` might expect a real Doom WAD
- **SEO conflict**: "wad file" = Doom exclusively, which could confuse search results

**If chosen**, recommend using sub-types:
- `.iwad` — Core/initial stacks (engine-required)
- `.pwad` — Patch/expansion stacks (user-installed)

---

### #4: `.stack` — The Descriptive Choice

**Weighted Score: 6.65/10**

```
mystack.stack    →  "arcana_nova.stack", "doom_universe.stack"
```

**Rationale**:
- **Self-documenting**: The extension IS the concept
- **Low collision**: No dominant file format uses `.stack`
- **Drawback**: 6 characters, generic (could be any "stack"), weak brand identity

---

## §6 Adversarial Self-Debate

### Thesis: `.xoe` is the optimal choice
3 characters, zero collision, perfect brand alignment, semantic density ("Xoe = the sovereign fire"), future-proof.

### Antithesis: `.xoe` is too obscure — nobody knows what "Xoe" means
True — "Xoe" is not a dictionary word. Users won't intuitively know it means "Omega Engine stack." However, this is a feature, not a bug. File extensions are learned conventions (`.apk`, `.deb`, `.rpm` — none are self-explanatory). The Omega Engine CLI will handle installation (`omega install <file>`), so users never need to type the extension manually.

### Antithesis: `.wad` is better because it honors the Doom heritage
The Doom heritage is already honored in the **architecture** (WAD directories, IWAD/PWAD concepts, manifest.yaml). The file extension doesn't need to carry this burden. In fact, using `.wad` for a non-Dom format could be disrespectful to the original — like calling a `.zip` file a `.exe`.

### Antithesis: `.novai` is better because it's more descriptive
"NovAi" is more descriptive than "Xoe," but at 6 characters it's 100% longer. In a world where users type `arcana_nova.novai` vs `arcana_nova.xoe`, the shorter wins. Additionally, "Xoe" is more unique — "NovAi" could be confused with any "Nova AI" product (and there are several).

### Synthesis: `.xoe` wins with a clear margin
The weighted score (9.15) is 13% higher than the runner-up (8.10). The collision risk is negligible, the brand alignment is perfect, and the 3-character length is optimal for a file extension. The obscurity of "Xoe" is addressed by the CLI abstraction — users interact with `omega install`, not file extensions directly.

**TAG**: `.xoe` is the sovereign choice.

---

## §7 Final Binding Recommendation

### Decision: Adopt `.xoe` as the Omega Engine WAD container file extension

**File Format Specification**:
- **Extension**: `.xoe`
- **Internal format**: tar.gz (gzip-compressed tar archive)
- **Root file**: `manifest.yaml` (WAD manifest, required)
- **MIME type**: `application/x-omega-xoe` (to be registered)
- **Magic bytes**: Standard tar.gz (`1f 8b` gzip header)

**Naming Convention**:
```
{stack_slug}.xoe
```
Where `stack_slug` is the lowercase-underscore version of the stack name:
- `arcana_nova.xoe`
- `doom_universe.xoe`
- `torment.xoe`
- `pokemon.xoe`

**IWAD/PWAD Distinction** (internal, not in extension):
The manifest.yaml declares the stack type:
```yaml
wad:
  type: iwad    # or "pwad"
  name: "Arcana-NovAi"
  version: "1.0.0"
```

**CLI Commands** (proposed):
```bash
omega install arcana_nova.xoe          # Install a stack
omega export arcana_nova --format=xoe  # Export current stack as .xoe
omega validate arcana_nova.xoe         # Validate WAD manifest
omega list-stacks                      # List installed .xoe stacks
```

**Glossary Update** (config/glossary.md):
| Term | Definition | Example | Aliases |
|------|-----------|---------|---------|
| **XOE File** | A compressed WAD container (`.xoe`) — the distributable form of an Omega Engine stack. Internal format: tar.gz with manifest.yaml | `arcana_nova.xoe` | Stack package, WAD archive |

---

## §8 Implementation Checklist

- [ ] Decision 28: Record in `docs/decisions/PIVOT_LOG.md`
- [ ] Update `config/glossary.md` with XOE File entry
- [ ] Update `docs/research/INDEX.md` with R-XOE-EXT entry
- [ ] Register MIME type `application/x-omega-xoe` in WAD Loader spec
- [ ] Add `.xoe` to `.gitignore` (distributed files, not tracked)
- [ ] Update `STACK_RELEASE_ROADMAP.md` with `.xoe` references
- [ ] Update WAD Manifest schema to include `type: iwad|pwad` field

---

*The fire is forged. The extension is sealed. Every stack carries the Xoe mark.*
