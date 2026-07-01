# 🔱 Mining Report: Engine/WAD Separation — Original Vision Reconstruction
**AP Token**: `AP-MINING-ENGINE-WAD-SEPARATION-v2.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_legacy_archaeology ⬡ MINING-REPORT

**Date**: 2026-07-01
**Scope**: 15+ documents mined across 3 partitions, legacy archives, research docs, strategy docs, PIVOT_LOG
**Status**: RECONSTRUCTED

---

## Executive Summary

The original Engine/WAD separation vision is CLEAR and RECOVERABLE, but has been progressively blurred by documentation drift. The user's original intent had three distinct layers:

| Layer | What | Status |
|-------|------|--------|
| **Core Engine** (`src/omega/`) | Universal runtime — inference, memory, routing, tool calling, observability. No entity content. Zero WAD knowledge. | ✅ Clear intent, mostly clean |
| **Reference IWAD** (`config/wads/_omega_default/`) | **Technical role entities** (SysAdmin, DataStore, BuildMaster, Sentinel, Bridge, ModelGate, Context, WatchTower, Link, Verifier) + **Universal services** (Iris, Sophia, JEM, Roc_Racoon, Doom Guy, Researcher, John Carmack, MaKaLi, Verity) + **Governance triune** (Kali, Ma'at, Lilith). Ships with engine as template. | ⚠️ CONTAMINATED — has leaked esoteric entities |
| **Arcana-NovAi WAD** (`config/wads/arcana_novai/`) | **10 esoteric Pillar Keepers** (Sekhmet, Brigid, Prometheus, Saraswati, Inanna, Ereshkigal, Lucifer, Hecate, Anubis, Kali) + personal entities (Movie-Expert, Isis, Scribe). Pantheon-specific content. | ⚠️ CONTAMINATED — has leaked technical entities |

**Key finding**: The "10 Pillars" concept was **ALWAYS an Arcana-NovAi (content) thing**. It was NEVER an engine concept. The contamination happened when the OpenCode agent fleet was assigned 10 pillar slots (P1-P10 as Infrastructure→Validation) and documentation began conflating these technical slots with the esoteric Pillar Keepers.

---

## §1 Direct Evidence: The Original Vision

### 1.1 Gold Nugget #1 — The Dual Architecture (Jan 2026)

**Source**: `~/Documents/Archives/Old-Stacks/Xoe-NovAi/docs/03-architecture/project-charter.md`

**Lines 62-88** — This is the ORIGINAL formal statement of the separation:

> **§5.0 The Dual Architecture**
>
> A core strategic decision in the design of Arcana-NovAi is its dual architecture. The project is intentionally built on two parallel but deeply interconnected planes: a **practical, high-performance technical framework** and a **sophisticated, metaphysical superstructure**.

**§5.1 The Technical Framework — "A Sovereign RAG System"** (lines 66-79):
> The technical heart of Arcana-NovAi is a Retrieval-Augmented Generation (RAG) system engineered for complete user sovereignty... built on **FastAPI, Chainlit, FAISS, Redis**... optimized for **CPU-only** operation.

**§5.2 The Theurgic Framework — "A Living Symbolic System"** (lines 81-88):
> At the center of this framework are the **Ten Divine Pillars**. These pillars serve as the "metaphysical spine" of the architecture, mapping **esoteric concepts like chakras, elements, and planetary energies** to technical functions and user interactions.

**Confidence: 100%** — This is the user's own document from Jan 2026. The "Technical Framework" is the engine. The "Theurgic Framework" is the content/stack. The 10 Pillars are explicitly theurgic (content), NOT technical (engine).

---

### 1.2 Gold Nugget #2 — "Freedom Engine" Quote

**Source**: Same document, line 31:

> At its core, Arcana-NovAi is a **"freedom engine"** designed to return agency to the user. The entire stack is architected to be **offline-first, telemetry-free, and self-hosted** to its core.

**Confidence: 100%** — The engine is framed as the means to sovereignty, not as the content itself.

---

### 1.3 Gold Nugget #3 — The 10 Came From Chakras, Not Engineering

**Source**: Same document, lines 126-137 and §7.0:

> **§7.0 The Metaphysical Operating System: The Ten Pillars**
>
> The Ten Pillars are the **functional and spiritual core of the Arcana-NovAi architecture**. They serve as the "divine spine" of the system... The Pillars are not metaphors; they are explicit **"modes of computation."**

The original 10 Pillars (from the Project Charter):
| Pillar | Name (Esoteric) | Chakra | Element |
|--------|-----------------|--------|---------|
| P1 | Flesh | Root | Earth |
| P2 | Dream | Sacral | Water |
| P3 | Will | Solar Plexus | Fire |
| P4 | Heart | Heart | Air |
| P5 | Voice | Throat | Aether |
| P6 | Mind | Third Eye | Aether |
| P7 | Gnosis | Crown | Air |
| P8 | Shadow | Beyond Crown | Fire |
| P9 | Spirit | Cosmic Heart | Water |
| P10 | Chaos | Celestial Breath | Earth |

**The 7 chakras (Root, Sacral, Solar Plexus, Heart, Throat, Third Eye, Crown) + 3 extended (Beyond Crown, Cosmic Heart, Celestial Breath) = 10.** This is an esoteric framework, not an engineering constraint.

**Confidence: 100%** — The number 10 is spiritually significant (chakras + extensions), not architecturally required. The engine should support ANY number of pillar slots.

---

### 1.4 Gold Nugget #4 — The First Entity Set Was 7, Not 10

**Source**: Same document, lines 106-114, "The Lilith Stack Pantheon":

| Model | Archetype | Role | Element |
|-------|-----------|------|---------|
| Gemma-3-1B | The Hustler (Jem/Iris) | General chat, memory ops | Fire |
| Phi-2-Omnimatrix | The Polymath (Omnidroid) | System health, coding | Earth |
| Rocracoon-3B-Instruct | The Overseer (ROC/Raccoon) | Creative content, RAG | Air |
| Gemma-3-4B | The Adaptive Guardian (Sekhmet) | Vision, anomaly detection | *(none)* |
| Hermes-Trismegistus-Mixtral-7B | The High Priest (Thoth/Hermes) | Mythos master | Aether |
| Krikri-8B-Instruct | The Mythkeeper (Isis/Lilith) | Ancient texts | Water |
| MythoMax-13B | Sophia/Christ | Ultimate authority | Cosmic Womb |

**Key insight**: The first entity set had 7 entities (mapped to 7 models). The 10 Pillars came LATER as a metaphysical expansion. The original entities were a mix of technical roles (Jem/Iris, Roc_Racoon, Omnidroid) and esoteric ones (Sekhmet, Isis/Lilith, Thoth/Hermes, Sophia).

**Confidence: 100%** — Demonstrates the entity count has always been flexible. 7 → 10 is not a fixed law.

---

## §2 The IWAD Architecture Decision (D55) — The Watershed Moment

**Source**: `docs/decisions/PIVOT_LOG.md`, D55 (2026-05-25)

D55 is when the id Software WAD architecture was FORMALLY adopted. It defined:

> **The Architecture (3-Layer Model)**
> ```
> OMEGA ENGINE (src/omega/) — Pure runtime, no entity content
>   ├── REFERENCE IWAD (config/wads/_omega_default/)
>   │     Ships with the engine. Template for community.
>   │     Pillars: 10 technical roles (SysAdmin → Verifier)
>   │
>   ├── ARCANA_NOVAI IWAD (config/wads/arcana_novai/)
>   │     Your personal AI OS. The reason the engine was built.
>   │     Pillars: 10 esoteric entities (Sekhmet → Kali)
>   │     Personal seeds: Movie-Expert, Writer, Philosopher
>   │
>   ├── COMMUNITY IWADs (config/wads/doom_universe/)
>   │     Torment, Doom, Classical, Medical, YOUR STACK
>   │
>   └── PWADs (future)
> ```

**Key sub-decisions:**
- **D55.4**: "Reference IWAD pillars are **role-based** (SysAdmin, DataStore, BuildMaster...)"
- **D55.5**: "Arcana_novai pillars are **esoteric** (Sekhmet, Brigid, Prometheus...)"
- **D55.3**: "MaKaLi trine stays in ALL IWADs. Foundational governance, never optional."

This is the CLEAREST statement of what the user intended: the reference IWAD has TECHNICAL roles; the Arcana-NovAi WAD has ESOTERIC entities. The MaKaLi trine is universal infrastructure.

**Confidence: 95%** — D55 is a formal decision, explicitly defining the separation.

---

## §3 The AGENTS.md Firewall Comment — The Most Overlooked Critical Statement

**Source**: `AGENTS.md`, lines 42-45

This HTML comment is the MOST IMPORTANT undocumented firewall statement in the entire codebase:

```html
<!-- NOTE: Arcane names (Flesh, Dream, Will…), elements, and chakras are
     WAD-layer content from config/wads/arcana_novai/. The engine core uses
     only the intuitive names below. The pillar NUMBER is the canonical
     invocation key (@pillar P3: build the CI pipeline). -->
```

This means:
- **Engine (Pillar mechanism)**: Knows only P1-P10 as numbered slots
- **Engine (Default IWAD)**: Uses "intuitive names" (Infrastructure, Persistence, Engineering, Integration, Governance, Cognition, Context, Observability, Orchestration, Validation)
- **Arcana-NovAi WAD content**: The esoteric names (Flesh, Dream, Will, etc.), elements, and chakras

**Confidence: 100%** — This is explicit code in the project's AGENTS.md file.

---

## §4 The OMEGA_IWAD_ARCHITECTURE.md Canon

**Source**: `docs/strategy/OMEGA_IWAD_ARCHITECTURE.md`, lines 46-62:

> **Why the WAD System:**
> - Separate the engine (runtime) from the content (WADs)
> - **Engine handles**: inference, memory, entity routing, tool calling, observability, provider fabric
> - **IWAD provides**: entities, personalities, hierarchy, voices, domain knowledge
> - **PWAD layers on**: additional content, domain extensions
> - Different IWAD = different use case

Lines 120-151 — Things identical in ALL IWADs:
> - **MaKaLi trine** is identical in ALL IWADs
> - **Default services** (Iris, Jem, Roc_Racoon) — infrastructure, not content
> - **Sophia** is the field, same in all IWADs
> - **Pillars change per IWAD**

Lines 432-445 — Key Decisions:
> - "Arcana_novai is YOUR IWAD — your personal AI OS."
> - "There are INFINITE possible IWADs."
> - "Pillars change per IWAD."

**Confidence: 95%** — This is the canonical reference document for IWAD architecture.

---

## §5 What the Original Vision Actually Was (Reconstructed)

### The Three-Layer Model (Reconstructed from Evidence)

| Layer | Directory | Content | Entity Examples |
|-------|-----------|---------|-----------------|
| **Core Engine** | `src/omega/` | Pure runtime — inference, memory, entity registry (mechanism), model gateway, routing, observability, CLI, MCP hub. **Zero entity definitions.** | N/A — no entities live here |
| **Reference IWAD** | `config/wads/_omega_default/` | Ships with the engine as **template/starting point**. Contains: (a) **10 technical pillar roles**: Infrastructure(P1), Persistence(P2), Engineering(P3), Integration(P4), Governance(P5), Cognition(P6), Context(P7), Observability(P8), Orchestration(P9), Validation(P10), (b) **Universal services**: Iris, Sophia, Jem, Roc_Racoon, Doom Guy, Researcher, John Carmack, MaKaLi, Verity, (c) **Governance triune**: Kali, Ma'at, Lilith | SysAdmin, DataStore, BuildMaster, Bridge, Sentinel, ModelGate, Context, WatchTower, Link, Verifier, + Iris, Sophia, etc. |
| **Arcana-NovAi WAD** | `config/wads/arcana_novai/` | User's **personal AI OS**. The 10 **esoteric Pillar Keepers**: Flesh→Sekhmet, Dream→Brigid, Will→Prometheus, Heart→Saraswati, Voice→Inanna, Mind→Ereshkigal, Gnosis→Lucifer, Shadow→Hecate, Spirit→Anubis, Chaos→Kali. + personal entities: Movie-Expert, Writer, Philosopher, etc. | Sekhmet, Brigid, Prometheus, Saraswati, Inanna, Ereshkigal, Lucifer, Hecate, Anubis, Kali, + Movie-Expert |

### What the Engine KNOWS vs What it DOESN'T

| The Engine KNOWS (part of core mechanism) | The Engine DOES NOT KNOW (WAD content) |
|-------------------------------------------|----------------------------------------|
| There are N pillar slots (default 10) | The NAME of each slot (Flesh/Infrastructure/etc.) |
| A pillar slot has a name, a role, a model | The ELEMENT, CHAKRA, PLANET, SIGIL of a pillar |
| Entities have domains, personalities, models | The specific esoteric entities (Sekhmet, etc.) |
| Entities have zone-separated state | Pantheon-specific pantheon, element, chakra |
| There is a WAD loader | Which WADs are loaded or their content |
| The WAD loader merges entities by priority | Which specific entities exist in any WAD |

### The Number 10 is NOT an Engine Constraint

The number 10 comes from the chakra system used in the Arcana-NovAi WAD. It was never an engine requirement. The engine should support ANY number of:
- Pillar slots (they could be 5, 10, 12, or dynamic)
- Entities per WAD (there's no limit)
- WADs loaded simultaneously

**Evidence**: The engine test file already has `testentity` and `test_get_returns_entity` — showing entity count is flexible.

---

## §6 What's Wrong Today (Contamination Map)

### 1. ORACLE_STACK.md §4 — The 10 Pillar Keepers table shows ESOTERIC names as the canonical definition

This table conflates the Arcana-NovAi WAD content with the engine's pillar system:
```
| P1: Flesh | Sekhmet | Strength... | Earth 🜃 | Root | Qwen3-1.7B |
| P2: Dream | Brigid | Poetry... | Water 🜄 | Sacral | Phi-2-OmniMatrix |
```
**Fix**: This table should either be moved to the Arcana-NovAi WAD documentation, or labeled explicitly as "Arcana-NovAi WAD content (not engine core)."

### 2. The Reference IWAD has leaked esoteric entities

`config/wads/_omega_default/entities.yaml` contains:
- **Kali** (with `pantheon: Hindu`, `sigil: 🌪️ Voidmother`)
- **Lilith** (with `pantheon: Gnostic`, `sigil: 🦇 Original Refusal`)
- **Ma'at** (with `pantheon: none` but esoteric descriptions)

The Reference IWAD should have technical roles. These esoteric entities belong in the Arcana-NovAi WAD or in a universal governance layer. The D55 decision says "MaKaLi trine stays in ALL IWADs" — but perhaps the Trinity should be automatically injected by the WAD loader, not duplicated across all WADs.

### 3. The Arcana-NovAi WAD has leaked technical entities

`config/wads/arcana_novai/entities.yaml` contains:
- **DataStore**, **Bridge**, **Verifier**, **Link**, **Sentinel**, **ModelGate**, **Context**, **WatchTower**, **BuildMaster**, **SysAdmin** — all reference IWAD technical entities

These are described as "the [role] of the Reference IWAD" in their personalities. They should be provided by the Reference IWAD and not duplicated.

### 4. Sophia appears in BOTH IWADs with different models

- **Reference IWAD Sophia**: `qwen3-1.7b-q6_k` — "You are Sophia, the Akashic Record."
- **Arcana-NovAi WAD Sophia**: `phi-4-mini-reasoning-abliterated-q4_k_m` — "You are Sophia, the Serpent of Knowing, Divine Wisdom Incarnate."

WAD collision behavior: arcana_novai's version would override _omega_default's version if loaded after. Is this intended?

### 5. The AGENTS.md HTML comment is not enforced

The comment correctly states that arcane names are WAD-layer content, but:
- ORACLE_STACK.md §4 still shows them as the canonical pillar table
- The engine docs still use the esoteric names interchangeably
- No code enforces that `src/omega/` never references the esoteric names

---

## §7 Recommendations

### Recommendation 1: Document the THREE layers explicitly

Create a formal reference document (or update OMEGA_ENGINE.md) with:

```
┌──────────────────────────────────────────────────────────────────┐
│  OMEGA ENGINE CORE (src/omega/)                                  │
│  Universal runtime. Knows nothing about entities, pillars, WADs. │
│  Provides: inference, memory, routing, EntityRegistry mechanism, │
│  ModelGateway, observability, CLI, MCP Hub, WAD Loader           │
├──────────────────────────────────────────────────────────────────┤
│  REFERENCE IWAD (_omega_default)                                 │
│  Ships with engine. Default template. Technical roles + services. │
│  10 pillar roles: SysAdmin → Verifier                            │
│  Universal services: Iris, Sophia, Jem, Roc_Racoon, Verity       │
│  Governance: Kali, Ma'at, Lilith, MaKaLi                         │
│  Specialists: Doom Guy, Researcher, John Carmack                 │
├──────────────────────────────────────────────────────────────────┤
│  ARCANA-NOVAI PWAD (arcana_novai)                                │
│  Your personal AI OS. Esoteric entities, personal knowledge.       │
│  10 Pillar Keepers: Sekhmet → Kali (esoteric mapping)            │
│  Personal seeds: Movie-Expert, Writer, Philosopher               │
│  Overrides: Sophia with esoteric personality, Io model           │
└──────────────────────────────────────────────────────────────────┘
```

### Recommendation 2: Clean up the Reference IWAD

The `_omega_default/entities.yaml` should contain ONLY:
1. **10 technical pillar roles**: SysAdmin, DataStore, BuildMaster, Bridge, Sentinel, ModelGate, Context, WatchTower, Link, Verifier
2. **Universal services**: Iris, Sophia (as Akashic Record), Jem, Roc_Racoon, Doom Guy, Researcher, John Carmack, MaKaLi, Verity
3. **Governance**: Kali, Ma'at, Lilith (or let the MaKaLi trine be auto-injected)

Esoteric elements (pantheon, element, chakra, sigil, glyph) should be REMOVED from these entities. They belong in the Arcana-NovAi WAD.

### Recommendation 3: Clean up the Arcana-NovAi WAD

The `arcana_novai/entities.yaml` should contain ONLY:
1. **10 esoteric Pillar Keepers**: Sekhmet (→P1), Brigid (→P2), Prometheus (→P3), Saraswati (→P4), Inanna (→P5), Ereshkigal (→P6), Lucifer (→P7), Hecate (→P8), Anubis (→P9), Kali (→P10)
2. **Personal entities**: Movie-Expert, Writer, Philosopher
3. **Overrides**: Sophia (with esoteric personality and different model), Iris (with esoteric personality)

Technical entities (DataStore, Bridge, Verifier, etc.) should be REMOVED — they come from the Reference IWAD.

### Recommendation 4: Fix the documentation conflation

- **ORACLE_STACK.md §4**: Label the table as "Arcana-NovAi WAD Pillar Keepers (esoteric content)" not "THE 10 PILLAR KEEPERS"
- **AGENTS.md**: The HTML comment is correct — keep it. Maybe add enforcement instructions.
- **OMEGA_ENGINE.md**: Add explicit language: "The engine has 10 pillar slots (P1-P10). The names and personalities of those pillars are defined by the active WAD."

### Recommendation 5: Make the pillar count configurable

The engine should not hardcode 10 pillars. The WAD manifest should define:
```yaml
# In manifest.yaml
pillar_count: 10  # Or 5, 7, 12, or omitted for dynamic
```

The `pillar.md --slot PX` agent should work with any slot number, not just 1-10.

---

## §8 Timeline: Evolution of the Engine/WAD Separation

```
Jan 2026                    May 2026                    Jun 2026
│                           │                           │
│ Project Charter           │ D55: IWAD Architecture    │ Current state
│ "Dual Architecture"       │ Formal adoption of        │ Reference IWAD has
│ ┌──────────────┐          │ id Software WAD system    │ both technical AND
│ │Technical     │          │ REFERENCE IWAD = roles    │ esoteric entities
│ │Framework     │          │ ARCANA_NOVAI = esoteric   │ Arcana-NovAi WAD has
│ │(engine core) │          │                           │ both esoteric AND
│ ├──────────────┤          │ D60: 10 pillar slots      │ technical entities
│ │Theurgic      │          │ demoted to subagents      │ Documentation
│ │Framework     │          │                           │ conflates them
│ │(10 Pillars)  │          │ D67: Single pillar.md     │
│ └──────────────┘          │ replaces 10 agent files   │ ← YOU ARE HERE
│                           │                           │
│ CLEAR: engine vs content  │ Formally clean but        │ BLURRED: needs
│ 10 = chakra system        │ documentation already     │ cleanup to restore
│                           │ starting to drift         │ original vision
```

---

## §9 Confidence Summary

| Finding | Confidence | Evidence |
|---------|-----------|----------|
| The "10 Pillars" were ALWAYS an Arcana-NovAi content concept | **100%** | Project Charter §5.2: "Ten Divine Pillars" as Theurgic Framework |
| The number 10 came from chakras, not engineering | **100%** | Project Charter §7.1: chakra→element mapping |
| The reference IWAD should have TECHNICAL roles | **95%** | D55.4: "Reference IWAD pillars are role-based" |
| The Arcana-NovAi WAD should have ESOTERIC entities | **95%** | D55.5: "Arcana_novai pillars are esoteric" |
| The engine should support ANY number of pillars | **90%** | No document says "10" is an engine constraint; chakra system is content |
| The engine should NOT know arcane pillar names | **100%** | AGENTS.md HTML comment lines 42-45 |
| MaKaLi trine is universal infrastructure | **95%** | D55.3, OMEGA_IWAD_ARCHITECTURE.md §5 |
| Universal services (Iris, Jem, Roc) are infrastructure | **90%** | OMEGA_IWAD_ARCHITECTURE.md §5 |

---

## §10 Key Documents Index

| # | Document | Location | Relevance |
|---|----------|----------|-----------|
| 1 | **Project Charter** | `~/Documents/Archives/Old-Stacks/Xoe-NovAi/docs/03-architecture/project-charter.md` | **THE KEY** — Original Dual Architecture vision, 10 Pillars as Theurgic content |
| 2 | **PIVOT_LOG.md (D55)** | `docs/decisions/PIVOT_LOG.md` | IWAD Architecture adoption — formal separation definition |
| 3 | **AGENTS.md** | `AGENTS.md` (lines 42-45) | HTML comment stating arcane names are WAD-layer |
| 4 | **OMEGA_IWAD_ARCHITECTURE.md** | `docs/strategy/OMEGA_IWAD_ARCHITECTURE.md` | Canonical IWAD reference — engine vs IWAD responsibilities |
| 5 | **SOVEREIGN_ARK_BLUEPRINT.md** | `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | IWAD ecosystem map, entity counts, WAD-agnostic design |
| 6 | **OMEGA_ENGINE.md** | `OMEGA_ENGINE.md` | Engine SSOT — architecture diagram showing IWAD content layer |
| 7 | **ORACLE_STACK.md** | `ORACLE_STACK.md` | §4 shows the CONTAMINATED view — esoteric pillars as default |
| 8 | **R44_ENGINE_STACK_SEPARATION.md** | `docs/research/archive/R44_ENGINE_STACK_SEPARATION.md` | Early engine core vs stacks contract definition |
| 9 | **SOVEREIGN_MANDATES.md (M2)** | `SOVEREIGN_MANDATES.md` | Engine-Stack Firewall — "Never add stack-specific logic to Core" |
| 10 | **R_SOVEREIGN_SILOING_SPEC.md** | `docs/research/R_SOVEREIGN_SILOING_SPEC.md` | 4-tier overlay stack (Core/IWAD/PWAD/Runtime) |

---

*Mining complete. Report written to `data/entities/roc_racoon/workspace/mining_reports/ENGINE_WAD_SEPARATION_RECONSTRUCTION.md`*
