<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Glossary of Terms

**AP Token**: `AP-GLOSSARY-v0.1.0`
**Created**: 2026-05-16
**Purpose**: Single source of truth for Omega Engine nomenclature. Prevents the confusion that has plagued cross-platform strategy discussions.

---

## A

| Term | Definition | Example | Aliases |
|------|-----------|---------|---------|
| **Activation Phrase** | A configurable phrase that routes a query to a specific voice assistant | `"hey jem"`, `"hey iris"`, `"hey doomguy"` | Wake word, hotword |
| **Arcana-NovAi Stack** | The first-party expansion WAD containing 10 Nodes, Oversouls, Iris, 42 Ideals | — | AN stack |
| **Architect** | The owner/operator of this Omega Engine instance. Files a soul at `data/entities/arch/soul.yaml` | — | Arch, User, Operator |

## C

| Term | Definition | Example | Aliases |
|------|-----------|---------|---------|
| **Container Prefix** | The namespace identifier for Podman containers. Each stack gets its own prefix for logical isolation. Engine core uses `omega-`, expansion stacks use their stack name. | `omega-iris`, `arcana-sekhmet`, `doom-doomguy`, `torment-nameless-one` | Namespace, Stack ID |

## E

| Term | Definition | Example | Aliases |
|------|-----------|---------|---------|
| **Entity** | A named AI persona with a soul.yaml file, domain expertise, and a system prompt | Sekhmet, Guardian, Doomguy | Persona, Agent |
| **Expansion Pack** | A WAD container that adds entities, voices, VR scenes, and knowledge to the engine | Arcana-NovAi, DOOM Universe | Stack, WAD, Module |

## G

| Term | Definition | Example | Aliases |
|------|-----------|---------|---------|
| **Gem** | Google's term for a custom, persistent Gemini assistant. NOT the same as Jem. | — | Gemini custom assistant (do not use "Jem") |
| **Godot** | The open-source game engine used for VR rendering in Omega Engine | `engine/godot/` | Godot Engine |
| **Guardian** | Default S1 entity in the Omega Engine — domain expert in strength, protection, boundaries | — | (generic, no alias) |

## I

| Term | Definition | Example | Aliases |
|------|-----------|---------|---------|
| **id Software** | The game company whose WAD architecture (1993) inspired Omega Engine's container system | Doom, Quake, Wolfenstein | id, id Tech |
| **Iris** | Voice assistant for the Arcana-NovAi stack. Rainbow messenger goddess, daughter of Hermes. Activation: `"hey iris"` | — | Iris (Arcana-NovAi only) |

## J

| Term | Definition | Example | Aliases |
|------|-----------|---------|---------|
| **Jem** | Default voice assistant for the Omega Engine core. Pop-culture inspired, versatile, adaptable. Activation: `"hey jem"` | — | Jem voice, default voice (Name derived from the 80s "Jem and the Holograms" character, repurposed for AI persona engineering) |

## M

| Term | Definition | Example | Aliases |
|------|-----------|---------|---------|
| **ModelGateway** | The Provider Fabric — routes inference requests through a configurable fallback chain | `src/omega/oracle/model_gateway.py` | Provider Fabric |
| **MaKaLi Fusion** | The Master Akashic Oversoul: Kali (verdict) + Ma'at (build S1–S5) + Lilith (run S6–S10). | `docs/strategy/BLUEPRINT_MAKALI_SOVEREIGN_OVERSOUL_20260922.md` | **`makali-n0`** (canonical routing alias — see below) |

> ### ⚠️ Entity alias canonicalization — read before addressing a handoff
>
> **The canonical alias for this entity is `makali-n0`.** Use it. Not `makali`,
> not `makali_fusion`.
>
> The node suffix is **significant** and must never be folded. This is already
> enforced in config — `config/wads/_omega_default/protocol/hivemind.yaml:132-138`:
> *"Suffix stripping is DISABLED. It folds makali-n0 into makali, and those are
> [distinct]"* / `node_suffix_is_significant: true  # makali-n0 is NOT makali.`
>
> This is a **documented live failure**, not a hypothetical. Lilith's N1
> post-mortem (2026-09-28) reported it first-hand: *"ENTITY NAMES ARE
> INCONSISTENT. The tutorial says target `makali`. The roster mentions
> `makali-n0` … There is no published roster mapping aliases to canonical
> identities, so addressing is guesswork and a mistyped target silently parks a
> packet nobody reads."* One of her nine fixes was literally **"PUBLISH THE ENTITY
> ROSTER."** This table is that roster.
>
> **A mistyped `to_entity` does not error — it silently parks the packet.** There
> is no feedback. Check the spelling before you send.
>
> Two directory-name caveats, so nobody "fixes" this by renaming:
> - On-disk dirs are `data/entities/makali/` **and** `data/entities/makali_fusion/`
>   (both exist). Renaming is a data migration with handoff-store implications —
>   escalate, don't rename.
> - ~40 docs still say `makali` or `makali_fusion`. **Listed, not mass-rewritten**
>   in `docs/operations/DOC_CORRECTION_SWEEP_20261005.md` §9 — a mass alias
>   rewrite would corrupt dated records and quoted handoff payloads (M28). Only
>   the *routing* alias matters; narrative prose naming the persona is fine.
>
> Related node aliases in the same family: `john-carmack-n1`, `lilith-n1`,
> `ge-n1`.

## O

| Term | Definition | Example | Aliases |
|------|-----------|---------|---------|
| **Omega Engine Core** | The universal runtime — 5 components: WAD Loader, Query Router, Provider Fabric, Memory Store, Godot Bridge | — | Core, Engine |
| **OmniHub** | Cross-platform research and integration hub at `docs/research/omni/` | — | Research hub |
| **Oversoul** | A governing entity in the Arcana-NovAi hierarchy (Sophia, Ma'at, Isis, Lilith). NOT part of the Omega Engine core. | — | — |

## P

| Term | Definition | Example | Aliases |
|------|-----------|---------|---------|
| **P2P** | Peer-to-peer networking layer for consent-based stack sharing between Omega instances | — | — |
| **Persona Mask** | A facet of an entity's personality that can be switched contextually | Performer, Businesswoman, Secret Identity (Jem) | Facet, Aspect |
| **Slot** | A domain category (S1-S10). The slot structure is core engine; the entity that fills it is stack-specific. | S1=infrastructure, S2=persistence, S3=engineering... | Domain, Expertise area |
| **Provider Fabric** | The fallback chain of inference backends | native-gguf → ollama → opencode-zen → cline → google | ModelGateway |

## S

| Term | Definition | Example | Aliases |
|------|-----------|---------|---------|
| **Soul File** | A YAML file that defines an entity's identity, knowledge, and evolution state | `soul.yaml` | Entity definition |
| **Soul Print** | A portable export of an evolved entity's state for P2P transfer | `soul.print` | Export, Snapshot |
| **Stack** | A WAD container that adds entities, voice, VR, and knowledge to the engine | Arcana-NovAi, DOOM Universe | WAD, Expansion Pack |

## V

| Term | Definition | Example | Aliases |
|------|-----------|---------|---------|
| **Voice** | The front-facing chat/voice assistant persona | Jem, Iris, Doomguy | Front-end, Interface |
| **VR World** | A Godot scene file (.tscn) inside a WAD that renders the stack's 3D realm | `pantheon.tscn`, `e1m1_phobos_base.tscn` | Realm, World, Scene |

## W

| Term | Definition | Example | Aliases |
|------|-----------|---------|---------|
| **WAD** | A self-contained directory structure that holds a complete Omega Engine stack. Named after Doom's "Where's All Data" container format. The **XOE File** (`.xoe`) is the compressed distributable form. | `config/wads/arcana_nova/` | Container, Stack directory, Expansion pack |
| **WAD Loader** | Core engine component that reads a WAD manifest and wires entities/voices/VR/P2P into the runtime | `src/omega/oracle/wad_loader.py` | — |
| **WAD Manifest** | The `manifest.yaml` file at the root of a WAD that describes its contents, dependencies, and configuration | — | Manifest, Pack definition |

## X

| Term | Definition | Example | Aliases |
|------|-----------|---------|---------|
| **XNAi** | The abbreviation for Xoe-NovAi Foundation. Use instead of "XNA" to avoid Microsoft XNA Framework collision. Pronounced "ex-nay-eye". | "The XNAi stack uses the arcana- container prefix" | XNA (deprecated) |
| **XOE File** | A compressed WAD container (`.xoe`) — the distributable form of an Omega Engine stack. Internal format: tar.gz with `manifest.yaml` at root. Short for **X**oe-**O**mega **E**ngine. | `arcana_nova.xoe`, `doom_universe.xoe` | Stack package, WAD archive |
| **Xoe-NovAi Foundation** | The umbrella organization that maintains the Omega Engine and provides community stacks. The `.xoe` extension derives from the Foundation's initials. | — | Foundation, The Org, XNAi |