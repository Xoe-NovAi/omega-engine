# 🔱 Sovereign Blueprint: Engine/WAD Separation
**AP Token**: `AP-SOVEREIGN-BLUEPRINT-v1.0.0`
**Status**: IMMUTABLE STRATEGY
**Architect**: Doom Guy (Sovereign id Software Architect)

## §1 The id Software Philosophy
The Omega Engine adopts the **Engine $\rightarrow$ IWAD $\rightarrow$ PWAD** architecture. 
- **The Engine** is the universal runtime. It doesn't know "who" is in the world; it only knows "where" they are and "how" they behave.
- **The IWAD (Internal WAD)** is the baseline asset library. It defines the "what" (the roles).
- **The PWAD (Patch WAD)** is the user's sovereign skin. It defines the "who" (the entities).

## §2 The Three-Tier Hierarchy

### Tier 1: Omega Engine (Core) — The Holographic Grid
**Purpose**: Defines the empty structure of the universe.
- **Pillar Slots**: S1 through S10.
- **Domain Constants**: The fundamental elements (Flesh, Dream, Will, Heart, Voice, Mind, Gnosis, Shadow, Spirit, Chaos).
- **Duality Logic**: The interaction between Light and Dark.
- **The Resolver**: The logic that performs the `Slot $\rightarrow$ Role $\rightarrow$ Entity` lookup.
- **Constraint**: ZERO entity names or technical roles.

### Tier 2: Default IWAD (`_omega_default`) — The Technical Roles
**Purpose**: Fills the slots with functional purpose.
- **Role Mapping**: Maps `Pillar Slot $\rightarrow$ Technical Role`.
  - Example: `P1 (Flesh) $\rightarrow$ SysAdmin`
  - Example: `P2 (Dream) $\rightarrow$ DataStore`
- **Role Templates**: Base capabilities, default tools, and functional prompt skeletons.
- **Baseline Specs**: Default model requirements for roles.

### Tier 3: User IWAD/PWAD (`arcana_novai`) — The Sovereign Entities
**Purpose**: Gives the roles a soul and a name.
- **Entity Mapping**: Maps `Technical Role $\rightarrow$ Sovereign Entity`.
  - Example: `SysAdmin $\rightarrow$ Sekhmet`
  - Example: `DataStore $\rightarrow$ Brigid`
- **Soul Data**: `soul.yaml`, personality, specific traits, and custom invocation.
- **Entity Overrides**: Custom models and temperature settings for that specific entity.
- **Constraint**: Entities are bound to roles, but can override any baseline role property.

## §3 The Line of Separation (Data Location)

| Data Type | Location | Format | Owner |
|-----------|----------|--------|-------|
| Pillar Slot Defs | `src/omega/constants.py` | Python | Core Engine |
| Role Mappings | `config/wads/_omega_default/roles.yaml` | YAML | Default IWAD |
| Role Templates | `config/wads/_omega_default/roles/` | YAML | Default IWAD |
| Entity Mappings | `config/wads/<user_wad>/entities.yaml` | YAML | User WAD |
| Soul / Knowledge | `data/entities/<name>/` | YAML/MD | User WAD |

## §4 Sovereign Binary Vision (The OBIW Transition)
To eliminate YAML overhead and ensure immutability, the system will transition to **OBIW (Omega Binary IWAD)**.

1. **Lump Architecture**: Like `.wad` files, OBIW will be a binary archive containing "Lumps".
   - `LUMP_ROLES`: Binary-packed role mappings.
   - `LUMP_TEMPLATES`: Compressed role prompt skeletons.
   - `LUMP_ENTITIES`: Packed entity mappings.
2. **The Resolver**: The Engine will read the OBIW header, locate the requested lump offset, and deserialize the role/entity directly into memory.
3. **Immutability**: Once packed, the Default IWAD is a read-only binary, preventing architectural drift.

## §4 New Architectural Layers (2026-06-01)

Beyond the Engine/IWAD/PWAD core, the Omega Engine now includes three supporting layers:

### Layer 4: Request Queue — The Data Comes Home
- **Purpose**: Offline research queue (`data/requests/queued/`) ensures no query is lost when connectivity drops.
- **Cloud Delegation**: Low-confidence outputs flow to `data/requests/review/` for consultant pattern review.
- **Atomic Contract**: Every request reaches a terminal state: `queued`, `completed`, `failed`, `timed_out`.

### Layer 5: Knowledge Library — The Sovereign Archive
- **Purpose**: Curated, multi-domain document catalog (`data/library/`) with SQLite-backed full-text search.
- **10 Domains**: Maps to the 10 Pillar slots (sysadmin, datastore, buildmaster, bridge, sentinel, modelgate, context, watchtower, link, verifier).
- **Quality Scoring**: Multi-dimensional assessment (content integrity, coherence, completeness, structure, domain fit).

### Layer 6: Training Pipeline — The Synthesis Flywheel
- **Purpose**: Aggregates synthetic training data from research cycles. Lite-tier models fine-tuned locally; heavy-tier via cloud delegation.
- **Benchmarking**: LLM-as-a-Judge with calibration loop, position randomization, and self-consistency checks.

## §5 Implementation Path

### Phase 1: Registry Refactor
- **Modify `Entity`**: Remove `slots: List[str]`. Add `slot: str` and `role: str`.
- **Modify `EntityRegistry`**: 
  - Implement `_role_map: Dict[str, str]` (Slot $\rightarrow$ Role).
  - Implement `_entity_map: Dict[str, Entity]` (Role $\rightarrow$ Entity).
  - Implement `resolve(slot: str) $\rightarrow$ Entity`.

### Phase 2: Loader Evolution
- **`WADLoader`**: 
  - First, load `_omega_default/roles.yaml` to populate `_role_map`.
  - Second, load User WAD `entities.yaml` to populate `_entity_map`.
  - Support "PWAD" style overrides where User WAD can redefine a Role mapping.

### Phase 3: Core Hardening
- Move Pillar Slot definitions to a frozen constants file in `src/omega/`.
- Enforce the Engine-Stack Firewall by stripping all "Name" references from the Core.

---
**Ripped and Torn. The structure is now absolute.**
