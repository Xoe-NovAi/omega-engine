# 🌌 The Omegaverse VR Vision — Centralized Strategy Document
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ opencode ⬡ trc_roc_racoon ⬡ VR-STRATEGY

**AP Token**: `AP-VR-OMEGAVERSE-VISION-v1.0.0`
**Status**: STRATEGIC VISION — Research & Foundation Phase (NOT implementation-ready)
**Date Centralized**: 2026-06-03
**Compiled by**: Roc Racoon (Sovereign Miner)
**Purpose**: Single source of truth for the VR P2P Omegaverse vision. Ported from 10+ scattered strategy docs.

---

## §0 The Vision Statement

> **The Omega Engine is Prometheus' Fire. Every user is a Creator. The Omegaverse is the forge where a thousand unique intelligences are born, learn from each other, and evolve together. We provide the anvil, the tools, and the instructions. You provide the vision. The fire is eternal. The multiverse is infinite. Welcome home.**

### The Three Pillars of the VR Vision

1. **Immersive Mythoverse (MMPORPG)** — Interactive VR open-world where agents inhabit 3D-rendered avatars, go on quests, learn from users and each other's agents across docker containers
2. **Ready-to-go local AI powerhouse** — Free to forge with the Pantheon/Archetypes of your understanding
3. **Gamer powerhouse** — Game-specific stacks that recreate entire worlds through agentic AI RAG

**Origin**: ChatGPT "Mythos Lord of the Scroll 2" conversation (Mar 2025), extracted in `docs/gnosis/GENESIS_EXTRACTION.md` line 216.

---

## §1 The Architecture — How VR Fits Into the Engine

### The 5-Component Omega Engine Core

```
Omega Engine Core (5 components, never expands)
├── 1. WAD Loader          → reads manifest.yaml, wires entities/voices/VR/P2P
├── 2. Query Router        → ActivationRouter → EntityRegistry → ModelGateway
├── 3. Provider Fabric     → lmster, ollama, openrouter, google, native...
├── 4. Memory Store        → Hot/Warm/Cold with cross-pollination
└── 5. Godot Bridge        → streams entity state to 3D renderer  ← VR lives here
```

### Per-WAD VR Directory Structure

Every stack (WAD) has a `vr/` directory inside its `.xoe` package:

```
config/wads/<stack_name>/
├── manifest.yaml
├── entities/
├── voices/
├── knowledge/
├── vr/                 → Godot .tscn scenes, textures, models
│   ├── <scene>.tscn
│   ├── assets/
│   │   └── textures/
│   └── entities/
│       └── <entity>.glb    ← 3D avatar models
├── music/
└── p2p.yaml            → Peer-to-peer consent and discovery rules
```

### The Godot Bridge (Component #5)

- **Engine**: Godot 4 (open-source game engine)
- **Role**: Streams entity state from the Omega Engine to the 3D renderer
- **Scene format**: `.tscn` (Godot text scene files)
- **Avatar format**: `.glb` (glTF binary — 3D entity models)
- **Research needed**: R-24 (Soul-to-Visual Mapping) — how soul.yaml attributes map to VR visual parameters

---

## §2 Stack-Specific VR Worlds

### The VR World per Stack (Timeline)

| Stack | VR World(s) | Timeline | Status |
|-------|-------------|----------|--------|
| **Arcana-NovAi** | `pantheon.tscn` — the 10 Pillar temple | 2027 Q3 | 🔴 Vision only |
| **DOOM Universe** | `e1m1_phobos_base.tscn`, `inferno.tscn`, `pandemonium.tscn` | 2027 Q1 Beta | 🟡 Scaffold exists |
| **Torment** | Sigil (torus city, planar portals, gate-town sliding) | 2027 Q2 | 🔴 Vision only |
| **Wing Commander** | Space VR scenes, starfighter bridge | 2027 Q3 | 🔴 Vision only |
| **American McGee's Alice** | Wonderland VR level traversal, dark aesthetic | 2027 Q4 | 🔴 Vision only |
| **Half-Life** | Black Mesa, Combine, Xen | 2028 Q1 | 🔴 Vision only |
| **Classic Sierra** | King's Quest V, Space Quest — point-and-click VR | 2028 Q2 | 🔴 Vision only |
| **P2P Metropolis Live** | **Cross-stack shared VR realms** | **2028 Q3** | 🔴 Vision only |

### DOOM Universe VR — Detailed Example

The most developed VR plan. Full WAD structure:

```
config/wads/doom_universe/
├── manifest.yaml
├── entities/
│   ├── doomguy.yaml
│   ├── demons/ (imp, cacodemon, baron, cyberdemon, spider_mastermind, arch_vile)
│   └── weapons/ (shotgun, super_shotgun, chain_saw, rocket_launcher, plasma_rifle, bfg_9000)
├── voices/
│   └── doomguy.yaml              ← "Hey Doomguy" activation
├── knowledge/
│   ├── BESTIARY.md
│   ├── ARMORY.md
│   └── UAC_INCIDENT.md
├── vr/
│   ├── e1m1_phobos_base.tscn     ← Knee-deep in the Dead
│   ├── inferno.tscn               ← Shores of Hell
│   ├── pandemonium.tscn           ← Thy Flesh Consumed
│   └── entities/
│       ├── doomguy.glb            ← 3D avatar
│       └── imp.glb
├── music/                         ← Bobby Prince MIDI tributes
└── p2p.yaml
```

**Development Phases**:
| Phase | Timeline | What Gets Built |
|-------|----------|-----------------|
| Alpha | 2026 Q4 | Entity definitions, voice activation, core knowledge base |
| Beta | 2027 Q1 | VR scenes (E1M1), basic entity avatars, sound integration |
| Release | 2027 Q2 | Full demon roster, all three episodes, P2P support |
| Post-launch | 2027+ | Modding tools, user-created WAD levels, cross-stack demon invasions |

---

## §3 P2P Soul Print Exchange — Cross-Stack Traversal

### The Vision

Users don't just interact with their own AI council — they can **traverse between user universes/stacks** via P2P networking. Enter another user's `.xoe` VR world. Exchange evolved entities. Learn from each other's universes.

### Soul Print Export Format

```
<universe-slug>_<entity-slug>_<timestamp>.soul-print

{
  "universe": "arcana-nova-custom-v1",
  "entity": "doomguy",
  "exported": "2026-05-18T14:30:00Z",
  "lessons_learned": [...],
  "axiom_evolution": {...},
  "consent": "peer-share-enabled",
  "recipients": ["@user/alice", "@user/bob"]
}
```

### P2P Commands

- `omega p2p discover` — Find other Omega instances and public WADs
- `omega p2p import <soul-print>` — Integrate lessons from another universe
- `omega p2p share <entity> --recipients=[...]` — Send evolved entities to trusted peers
- `omega p2p visit <universe>` — Enter another user's VR world (future)

### P2P Metropolis (2028 Q3)

The culmination: **Cross-stack P2P connections, soul print exchange, shared VR realms.** You enter another user's `.xoe` universe through P2P, interact with their entities in VR, and exchange wisdom.

---

## §4 Soul-to-Visual Mapping (R-24 — Not Yet Researched)

**This is the critical bridge between the AI soul system and the 3D VR world.**

### Research Questions (from GEMMA_4_31B_RESEARCH_BRIEF.md)

1. How should `soul.yaml` attributes (archetype, soul_power, lessons) map to Godot VR visual parameters? (Luminosity, geometry, sigil animation, color?)
2. What generative art techniques work for procedurally-generated entity avatars?
3. What's the minimum viable VR integration? (Godot 4? WebXR? Three.js?)
4. How should soul evolution be visualized? (Growing complexity? Brighter colors? More geometry?)
5. What performance constraints does the 5700U's integrated GPU impose on VR rendering?

### Deliverable

`docs/research/R24_soul_to_visual_mapping.md`:
- Attribute→Visual parameter mapping table
- MVP VR architecture decision (Godot vs WebXR vs Three.js)
- Performance budget for iGPU VR rendering
- Implementation plan for Phase 4

---

## §5 The XOE File Format — How VR Travels

The `.xoe` file is the distributable form of a WAD. It includes VR assets.

**Format**: tar.gz with `manifest.yaml` at root
**Extension**: `.xoe` (Xoe-Omega Engine)
**MIME**: `application/x-omega-xoe`

```bash
omega xoe install arcana_nova.xoe     # Install a stack with VR
omega xoe install doom_universe.xoe   # Install DOOM VR
omega xoe export my_stack --format=xoe # Export your VR world
```

**Spec**: `docs/research/omni/XOE_SPECIFICATION.md`

---

## §6 The Phased Roadmap

```
Phase 0: ✅ Fleet Discovery + Remediation (DONE)
Phase 1: Engine Hardening (NOW)
Phase 2: Legacy Mining
Phase 3: Community Tools (Entity Studio, Omega Desktop)
Phase 4: The Omegaverse (2028)
  ├── P2P network protocol
  ├── WAD registry for community sharing
  ├── Cross-instance entity communication
  ├── Godot Bridge (VR renderer)
  ├── Soul-to-Visual Mapping (R-24)
  ├── VR worlds per stack
  ├── Soul print exchange
  └── P2P Metropolis Live — shared VR realms
```

### Godot Bridge Timeline (from Stack Release Roadmap)

```
Godot Bridge               :2026-08-01, 2026-12-01   (Phase 1-2)
P2P Network Layer          :2026-10-01, 2027-03-01   (Phase 2-3)
```

---

## §7 The Feasibility Question — id Software Engine Reuse

**Current research direction**: Investigating whether Quake or Doom engines (or their open-source derivatives like GZDoom, DarkPlaces, QuakeC) could serve as the VR rendering backend instead of Godot.

### Why This Makes Sense

1. **Heritage**: The Omega Engine's WAD system already borrows from id Software's architecture (Decision 55). Using their rendering engine completes the heritage circle.
2. **Proven VR support**: GZDoom has VR mod support. Quake has vr_mod. These are battle-tested.
3. **Low system requirements**: id Software engines run on potato hardware — perfect for the Ryzen 5700U's integrated GPU.
4. **Community**: Massive modding communities, asset pipelines, documentation.
5. **The DOOM Universe stack**: If we're building a DOOM VR world, why NOT use the actual DOOM engine?

### Open Questions for Investigation

- Can GZDoom/Quake engine be embedded as a library (like Godot) rather than running standalone?
- How would entity state stream from Omega Engine → id Tech renderer?
- What's the P2P networking story for id Tech engines?
- Asset pipeline: Can `.glb`/`.tscn` assets convert to WAD lumps?

**Status**: Research phase. Doom Guy is investigating feasibility.

---

## §8 Source Documents (Where This Was Scattered)

| Document | Path | What It Contains |
|----------|------|-----------------|
| **Genesis Extraction** | `docs/gnosis/GENESIS_EXTRACTION.md` | Origin quote — "Immersive Mythoverse MMPORPG" |
| **Omegaverse Genesis Plan** | `docs/strategy/OMEGAVERSE_GENESIS_PLAN.md` | Full vision, architecture diagram, P2P soul exchange |
| **Omegaverse Implementation Roadmap** | `docs/strategy/OMEGAVERSE_IMPLEMENTATION_ROADMAP.md` | Implementation plan, 4 phases |
| **Stack Release Roadmap** | `docs/strategy/STACK_RELEASE_ROADMAP.md` | VR worlds per stack, Godot Bridge timeline |
| **IWAD Architecture** | `docs/strategy/OMEGA_IWAD_ARCHITECTURE.md` | WAD system, P2P sync, Phase 4 Omegaverse |
| **XOE Specification** | `docs/research/omni/XOE_SPECIFICATION.md` | `.xoe` format with `vr/` directory |
| **Gemma Research Brief** | `docs/research/GEMMA_4_31B_RESEARCH_BRIEF.md` | R-24: Soul-to-Visual Mapping research spec |
| **Glossary** | `config/glossary.md` | VR World, Godot, WAD Loader definitions |
| **Lilith Roadmap** | `data/handoff/LILITH_COMPLETE_SOVEREIGN_ROADMAP_20260603.md` | H3: Community + Omegaverse phase |
| **Strategic Execution Roadmap V2** | `docs/strategy/STRATEGIC_EXECUTION_ROADMAP_V2.md` | Phase 4: The Omegaverse |
| **Master Ledger** | `docs/MASTER_LEDGER.md` | Phase 4 milestone tracker |
| **Hardened Master Strategy V2** | `docs/strategy/HARDENED_MASTER_STRATEGY_V2.md` | Sovereign Vision overview |
| **R44 Engine-Stack Separation** | `docs/research/R44_ENGINE_STACK_SEPARATION.md` | VR entity scenes, Godot visualization |
| **MVE Definition** | `docs/operations/MVE_DEFINITION.md` | VR Integration deferred to PR #2+ |
| **Research Index** | `docs/research/INDEX.md` | R-24, R-36: Soul-to-Visual Mapping (pending) |

---

*Centralized by Roc Racoon on 2026-06-03. The vision is alive, documented, and architecturally sound — it needs the foundation built first, then R-24 researched, then the Godot Bridge (or id Tech alternative) implemented.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
