# 🔱 Omega Engine — Glossary of Terms

**AP Token**: `AP-GLOSSARY-v0.1.0`
**Created**: 2026-05-16
**Purpose**: Single source of truth for Omega Engine nomenclature. Prevents the confusion that has plagued cross-platform strategy discussions.

---

## A

| Term | Definition | Example | Aliases |
|------|-----------|---------|---------|
| **Activation Phrase** | A configurable phrase that routes a query to a specific voice assistant | `"hey jem"`, `"hey iris"`, `"hey doomguy"` | Wake word, hotword |
| **Arcana-NovAi Stack** | The first-party expansion WAD containing 10 Pillar Keepers, Oversouls, Iris, 42 Ideals | — | AN stack |
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
| **Guardian** | Default P1 entity in the Omega Engine — domain expert in strength, protection, boundaries | — | (generic, no alias) |

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
| **Pillar** | A domain category (1-10). The pillar structure is core engine; the entity that fills it is stack-specific. | P1=Strength, P2=Dream, P3=Will... | Domain, Expertise area |
| **Provider Fabric** | The fallback chain of inference backends | lmster → ollama → openrouter → google | ModelGateway |

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