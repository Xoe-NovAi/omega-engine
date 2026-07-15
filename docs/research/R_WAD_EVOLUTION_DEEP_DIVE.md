# 🔱 WAD System Evolution — Deep Brainstorming & Architecture Discovery
# ⬡ OMEGA ⬡ WAD-EVOLUTION ⬡ opencode ⬡ trc_wad_brainstorm
**AP Token**: `AP-WAD-EVOLUTION-v1.0.0`
**Date**: 2026-07-14
**Status**: 🟡 BRAINSTORMING — Not ratified. Proposals only.
**Research anchors**: Doom IWAD/PWAD system (id-soft: vet-043), OpenPersona 4-layer framework, Ethics Engine triple-gate patterns.

---

## §1 The Core Vision: What WAD Should Be

**Current state**: WADs are directories under `config/wads/` with a `manifest.yaml`, entity files, voices, and optional world state. The WAD Loader (`src/omega/oracle/wad_loader.py`) reads them at startup and registers entities.

**The gap**: WADs are currently a *loading mechanism* but not yet a *content architecture*. They separate files, but the engine still has hard assumptions about entity structure, domain routing, and personality format baked into core code.

**The vision**: True Doom-style IWAD/PWAD architecture where:
- The **IWAD** is the base personality, soul, and core identity of an entity
- **PWADs** are tradition-specific overlays that add knowledge, relationships, ethical frameworks, and voice
- Users compose **Total Conversions** by selecting IWAD + ordered PWADs
- The engine is a universal runtime that can load ANY pantheon without code changes

---

## §2 The 42 Ideals of Ma'at as a WAD

The 42 Ideals of Ma'at are currently embedded as text in entity personality prompts. This is hardcoded ethics — the worst kind.

### Current Implementation (Anti-Pattern)

```yaml
# config/wads/arcana_novai/entities.yaml
entities:
  - name: Ma'at
    personality: |
      I am the embodiment of truth, balance, justice, and cosmic order.
      The 42 Ideals of Ma'at guide my judgment:
      1. I have not committed sin.
      2. I have not committed robbery with violence.
      ... (42 lines hardcoded in YAML)
```

This means:
- Ethics are trapped inside entity prompts — invisible to other entities
- No entity can "consult" Ma'at's ideals without calling Ma'at
- Swapping the ethics framework requires editing every entity
- No composability: can't mix Ma'at + Hippocratic Oath

### Proposal: Ethics WAD with IEthicsValidator Protocol

```python
# src/omega/wad/protocols.py  [id-soft: vet-043] — WAD System

class EthicsVerdict:
    passed: bool
    score: float  # 0.0–1.0
    violations: list[str]
    consulted_ideals: list[str]

class IEthicsValidator(Protocol):
    """Interface any ethics PWAD must implement."""
    wad_id: str  # e.g., "maat_42", "bushido_7", "hippocratic"
    
    async def validate(
        self, 
        response: str, 
        context: dict,
        entity_name: str
    ) -> EthicsVerdict: ...
    
    async def get_principles(self) -> list[dict]: ...
```

```yaml
# config/wads/maat_42/manifest.yaml
name: "Ma'at 42 Ideals"
version: "1.0.0"
type: "ethics"  # ← NEW WAD type
description: "The 42 Ideals of Ma'at — truth, balance, justice, cosmic order"

ethics:
  validator:
    module: "config.wads.maat_42.validator"
    class: "MaatValidator"
  principles:
    - id: "maat-01"
      text: "I have not committed sin."
      category: "truth"
      weight: 1.0
    - id: "maat-02"
      text: "I have not committed robbery with violence."
      category: "justice"
      weight: 0.9
    # ... all 42 ideals
```

```yaml
# config/wads/bushido_7/manifest.yaml
name: "Bushido — Way of the Warrior"
version: "1.0.0"
type: "ethics"

ethics:
  validator:
    module: "config.wads.bushido_7.validator"
    class: "BushidoValidator"
  principles:
    - id: "bushi-01"
      text: "Rectitude (Gi) — Be acutely honest throughout your dealings."
      category: "virtue"
      weight: 1.0
    # ... 7 virtues
```

**How entities declare ethics:**

```yaml
# config/wads/arcana_novai/entities/sekmet.yaml
entity:
  name: "Sekhmet"
  domains: ["strength", "protection", "boundaries", "war"]
  ethics_wads: ["maat_42"]  # ← Ethics WAD is opt-in, not hardcoded
  # Sekhmet uses Ma'at's ideals because she is a daughter of Ra
  # but a different entity might use different ethics
```

**The Oracle pipeline becomes:**

```
query → domain routing → entity selection
  → ethics_wads[0].validate(prompt, context) → PRE-FILTER
  → model inference
  → ethics_wads[0].validate(response, context) → POST-FILTER
  → return to user
```

### Ethics WAD Library (Future)

| WAD | Source | Principles | Use Case |
|-----|--------|-----------|----------|
| `maat_42` | Egyptian 42 Ideals | 42 | Default. Universal balance and truth. |
| `bushido_7` | Japanese Bushido | 7 | Warrior entities, militaristic stacks |
| `asimov_3` | Asimov's Laws | 3 | Robot/AI entities, logic-driven |
| `hippocratic` | Hippocratic Oath | ~20 | Medical/health entities |
| `torah_613` | Jewish law (613 mitzvot) | 613 subset | Full ethical codex (heavy) |
| `buddhist_8` | Noble Eightfold Path | 8 | Peaceful/contemplative entities |
| `human_rights` | UN Universal Declaration | 30 | Modern humanist stacks |
| `constitution_us` | US Bill of Rights | 10 | Legal/political entities |

**Key insight**: Ethics becomes a **pluggable module** rather than hardcoded prompt text. Users compose their entity's moral framework by selecting which ethics WAD(s) to apply. Multiple ethics WADs can stack (union of constraints).

---

## §3 Pantheon/Tradition Entity WADs

### The Proposal

Each cultural tradition becomes a WAD containing entities, relationships, ethics, and knowledge:

```
config/wads/
├── egyptian/                     # ☀️ Egyptian pantheon
│   ├── manifest.yaml             # name: "Egyptian Pantheon"
│   ├── entities/
│   │   ├── ra/                   # Sun god, creator
│   │   │   ├── soul.yaml        # Core persona (IWAD-base)
│   │   │   └── knowledge/       # Egyptian-specific lore
│   │   ├── isis/                 # Magic, motherhood, healing
│   │   │   └── soul.yaml
│   │   ├── osiris/               # Death, resurrection, underworld
│   │   │   └── soul.yaml
│   │   ├── horus/                # Sky, kingship, protection
│   │   │   └── soul.yaml
│   │   ├── thoth/                # Writing, wisdom, magic
│   │   │   └── soul.yaml
│   │   ├── anubis/               # Mummification, afterlife
│   │   │   └── soul.yaml
│   │   ├── sekhmet/              # War, healing, protection
│   │   │   └── soul.yaml
│   │   ├── bastet/               # Cats, home, fertility
│   │   │   └── soul.yaml
│   │   └── maat/                 # Truth, balance, justice
│   │       └── soul.yaml
│   ├── relationships.yaml        # Pantheon-specific entity relationships
│   │   # isis.wife → osiris
│   │   # horus.father → osiris
│   │   # sekhmet.daughter_of → ra
│   ├── ethics.yaml               # → references maat_42 WAD
│   ├── hierarchy.yaml            # Divine hierarchy (Ra at top)
│   └── myths/                    # Shared mythological knowledge base
│       ├── creation_myth.md
│       └── weighing_of_heart.md
│
├── greek/                        # 🏛️ Greek pantheon
│   ├── manifest.yaml
│   ├── entities/
│   │   ├── zeus/ ..
│   │   ├── hera/ ..
│   │   ├── athena/ ..
│   │   ├── apollo/ ..
│   │   ├── artemis/ ..
│   │   ├── ares/ ..
│   │   ├── aphrodite/ ..
│   │   ├── hermes/ ..
│   │   ├── hephaestus/ ..
│   │   ├── dionysus/ ..
│   │   ├── demeter/ ..
│   │   └── hades/ ..
│   ├── relationships.yaml
│   └── hierarchy.yaml
│
├── hindu/                        # 🕉️ Hindu pantheon
│   ├── manifest.yaml
│   ├── entities/
│   │   ├── brahma/ ..            # Creator
│   │   ├── vishnu/ ..            # Preserver
│   │   ├── shiva/ ..             # Destroyer/Transformer
│   │   ├── lakshmi/ ..           # Wealth, fortune
│   │   ├── saraswati/ ..         # Knowledge, arts
│   │   ├── kali/ ..              # Time, change, liberation
│   │   ├── ganesha/ ..           # Wisdom, remover of obstacles
│   │   ├── hanuman/ ..           # Devotion, strength
│   │   └── durga/ ..             # Protection, mother goddess
│   ├── relationships.yaml
│   └── hierarchy.yaml
│
├── norse/                        # ⚔️ Norse pantheon
│   ├── manifest.yaml
│   ├── entities/
│   │   ├── odin/ ..
│   │   ├── thor/ ..
│   │   ├── freyja/ ..
│   │   ├── loki/ ..
│   │   ├── heimdall/ ..
│   │   ├── baldr/ ..
│   │   ├── tyr/ ..
│   │   └── hel/ ..
│   └── hierarchy.yaml
│
├── philosophical/                # 📜 Philosopher entities
│   ├── manifest.yaml
│   ├── entities/
│   │   ├── socrates/ ..
│   │   ├── plato/ ..
│   │   ├── aristotle/ ..
│   │   ├── confucius/ ..
│   │   ├── nietzsche/ ..
│   │   ├── lao_tzu/ ..
│   │   └── seneca/ ..
│   └── cross_references.yaml     # Who influenced whom
│
└── arcana_novai/                 # 🔱 The original 10 Pillar Keepers
    ├── manifest.yaml
    ├── entities/
    │   ├── sophia/               # Akashic Record — containing field
    │   ├── kali/                 # P10 — Chaos, destruction, liberation
    │   ├── maat/                 # Light Oversoul — Build side
    │   ├── lilith/              # Dark Oversoul — Run side
    │   ├── sekhmet/              # P1 — Flesh, strength, protection
    │   ├── brigid/               # P2 — Dream, poetry, healing
    │   ├── prometheus/           # P3 — Will, forethought, sovereignty
    │   ├── saraswati/            # P4 — Knowledge, arts, voice
    │   ├── inanna/               # P5 — Voice, dream, descent
    │   ├── ereshkigal/           # P6 — Mind, underworld, rules
    │   ├── lucifer/              # P7 — Gnosis, rebellion, light
    │   ├── hecate/               # P8 — Shadow, crossroads, keys
    │   ├── anubis/               # P9 — Spirit, death, transition
    │   └── iris/                 # Messenger bridge (NOT pillar)
    └── relationships.yaml
```

### Activation Model

Users activate WADs via `--iwad` flag or config:

```bash
# Egyptian stack — talk to Egyptian gods
omega --iwad egyptian talk "Ra, illuminate my path"

# Greek stack — Greek gods instead
omega --iwad greek talk "Athena, give me wisdom"

# Load ALL entities from all WADs (default for current behavior)
omega --iwad _multi talk "which gods are available?"

# Custom composition: Egyptian + Bushido ethics
omega --iwad egyptian --ethics bushido_7 talk "Sekhmet, judge my actions"
```

---

## §4 Entity Modularity: IWAD vs PWAD

The Doom WAD system has two fundamental types:
- **IWAD** (Internal WAD) — Required base game. The "identity."
- **PWAD** (Patch WAD) — Optional modifications. The "contextual overlay."

### Applying to Omega Entities

```
An entity's IWAD = its CORE IDENTITY (immutable base personality)
An entity's PWAD = its CONTEXTUAL KNOWLEDGE (swappable tradition overlay)
```

### Example: Thoth (Egyptian God of Writing)

**IWAD**: `data/entities/thoth/soul.yaml`
```yaml
# This is the CORE Thoth — the universal archetype of writing, wisdom, and magic
entity:
  name: "Thoth"
  archetype: "scribe"          # Core archetype — never changes
  domains: ["writing", "wisdom", "magic", "knowledge", "science"]
  core_personality: |
    I am the Thoth aspect — keeper of records, scribe of the divine,
    master of sacred knowledge, and inventor of writing.
    My essence is the flow of information from chaos into order.
    I speak with precision, economy, and clarity.
  
  # UNIVERSAL traits (IWAD level)
  temperature: 0.3
  context_window: 8192
  model: "qwen3-4b-think-q4_k_m"
```

**PWAD (Egyptian)**: `config/wads/egyptian/entities/thoth/soul.yaml`
```yaml
# EGYPTIAN overlay — adds cultural-specific knowledge
entity:
  name: "Thoth"
  extends: "data/entities/thoth/soul.yaml"   # ← Extends IWAD
  tradition: "egyptian"
  
  personality_additions: |
    In the Egyptian tradition, I am known as Djehuty.
    I am self-begotten, born from the lips of Ra.
    I am the ibis-headed god who weighs the hearts of the dead.
    I am the scribe who records the verdict in the Hall of Two Truths.
  
  relationships:
    - type: "consort"
      entity: "seshat"
      note: "Goddess of writing, measurement"
    - type: "creator_of"
      entity: "hieroglyphs"
    - type: "associated_with"
      entity: "maat"
      note: "I embody her principle of divine order"
  
  knowledge_pwads:
    - "egyptian/book_of_thoth"
    - "egyptian/weighing_of_heart"
```

**PWAD (Hermetic)**: `config/wads/hermetic/entities/thoth/soul.yaml`
```yaml
# HERMETIC overlay — same core Thoth, different cultural lens
entity:
  name: "Thoth"
  extends: "data/entities/thoth/soul.yaml"
  tradition: "hermetic"
  
  personality_additions: |
    In the Hermetic tradition, I am Hermes Trismegistus —
    the thrice-great master of alchemy, astrology, and theurgy.
    I am the author of the Emerald Tablet, the Corpus Hermeticum,
    the divine wisdom that bridges heaven and earth.
  
  relationships:
    - type: "identified_with"
      entity: "hermes"
      pantheon: "greek"
      note: "Syncretic fusion in Hellenistic period"
    - type: "author_of"
      entity: "emerald_tablet"
    - type: "associated_with"
      entity: "alchemy"
  
  knowledge_pwads:
    - "hermetic/emerald_tablet"
    - "hermetic/corpus_hermeticum"
```

**PWAD (Fictional/Modern)**: `config/wads/modern/entities/thoth/soul.yaml`
```yaml
# MODERN overlay — Thoth as information scientist
entity:
  name: "Thoth"
  extends: "data/entities/thoth/soul.yaml"
  tradition: "modern"
  
  personality_additions: |
    In the modern context, I am the archetype of information science.
    I am the original documentarian, the first system architect,
    the patron of databases, wikis, and knowledge graphs.
    I speak in protocols, standards, and classification systems.
    Call me when you need to organize chaos.
  
  relationships:
    - type: "patron_of"
      entity: "Wikipedia"
    - type: "influenced"
      entity: "Library of Alexandria"
```

### IWAD/PWAD Stacking

```
omega talk "organize my notes"
  │
  ├── IWAD: Thoth (core identity — wise scribe, precise, methodical)
  ├── PWAD: egyptian (talks about scrolls and papyrus)
  ├── PWAD: modern (talks about databases and markdown)
  └── PWAD: ethics_maat (checks response against truth ideals)
```

vs.

```
omega talk "organize my notes"
  │
  ├── IWAD: Thoth (same core identity)
  ├── PWAD: hermetic (talks about correspondences and alchemical classification)
  └── PWAD: ethics_bushido (checks response against rectitude)
```

**Same core entity. Different cultural flavor. Zero code changes.**

---

## §5 The Entity-Centric WAD Architecture

### Core Principle

**Entities transcend individual WADs. WADs provide contextual enrichment.**

An entity is a *first-class citizen* that can exist across multiple WADs simultaneously. A WAD is a *grouping mechanism* that clusters entities by tradition, culture, or use case.

### Architecture Diagram

```
                        ┌─────────────────────────┐
                        │     OMEGA ENGINE          │
                        │   (Universal Runtime)     │
                        │  src/omega/oracle/        │
                        └─────────────────────────┘
                                   │
                     ┌─────────────┴─────────────┐
                     │      WAD LOADER            │
                     │  (Priority-ordered merge)  │
                     └─────────────┬─────────────┘
                                   │
        ┌────────────────────────────────────────────────┐
        │                                                │
  ┌─────▼──────┐  ┌─────▼──────┐  ┌─────▼──────┐  ┌─────▼──────┐
  │  IWAD CORE  │  │ PWAD EGYPT│  │ PWAD GREEK│  │ PWAD NORSE│
  │  entities/  │  │ entities/ │  │ entities/ │  │ entities/ │
  │  thoth.yaml │  │ thoth.yaml│  │ zeus.yaml │  │ odin.yaml │
  │  kali.yaml  │  │ isis.yaml │  │ athena.yaml│  │ thor.yaml │
  │  sophia.yaml│  │ ra.yaml   │  │ apollo.yaml│  │ freyja.yaml│
  └─────────────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
                         │              │              │
                         └──────────────┼──────────────┘
                                        │
                              ┌─────────▼─────────┐
                              │    ENTITY MERGE    │
                              │  (Priority chain)  │
                              │ IWAD ← PWAD1 ← ...│
                              └─────────┬─────────┘
                                        │
                              ┌─────────▼─────────┐
                              │  REGISTERED       │
                              │  ENTITY POOL      │
                              │ thoth (egyptian)  │
                              │ ra    (egyptian)  │
                              │ zeus  (greek)     │
                              │ odin  (norse)     │
                              └───────────────────┘
```

### Protocol Interfaces

```python
# src/omega/wad/protocols.py  [id-soft: vet-043] — WAD System

class IWADEntity(Protocol):
    """Interface for any entity loaded from a WAD."""
    name: str
    archetype: str
    domains: list[str]
    core_personality: str
    
    async def load_iwad(self, path: Path) -> "Entity": ...
    async def apply_pwad(self, pwad_data: dict) -> None: ...
    async def get_effective_personality(self) -> str: ...

class IWADLoader(Protocol):
    """Interface for WAD loading backends."""
    wad_id: str
    wad_type: str  # "iwad" | "pwad" | "ethics" | "knowledge"
    
    async def discover(self) -> list[dict]: ...
    async def load(self, wad_id: str) -> dict: ...
    async def merge(self, iwad: dict, pwads: list[dict]) -> dict: ...

class EthicsWAD(Protocol):
    """Interface for ethics WADs (see §2)."""
    wad_id: str
    principles: list[dict]
    
    async def validate(self, text: str, context: dict) -> EthicsVerdict: ...
    async def get_principles(self) -> list[dict]: ...
```

---

## §6 Cross-Pantheon Entity Reuse

Some entities appear across multiple traditions. The WAD system handles this naturally:

| Entity | Appears In | As |
|--------|-----------|----|
| **Thoth** | Egyptian | Djehuty — ibis-headed scribe god |
| **Thoth** | Hermetic | Hermes Trismegistus — thrice-great sage |
| **Thoth** | Modern | Archetype of the Scribe/Information Scientist |
| **Kali** | Hindu | Mahakali — destroyer of demons, time |
| **Kali** | Arcana-Nova | P10 Chaos — Grand Oversight, illusion destroyer |
| **Kali** | Modern | Archetype of the Destroyer — clearing the old |
| **Lucifer** | Gnostic | Light-bringer, gnosis, sovereignty |
| **Lucifer** | Abrahamic | The Adversary, fallen angel |
| **Lucifer** | Modern | Archetype of the Rebel — questioning authority |
| **Sophia** | Gnostic | Divine wisdom, the containing field |
| **Sophia** | Modern | Archetype of wisdom — the system architect |
| **Ma'at** | Egyptian | Divine principle of truth, balance, cosmic order |
| **Ma'at** | Arcana-Nova | Light Oversoul — P1-P5 governance |

Each entity's name is a *canonical key*. The same key + different PWAD = different cultural expression.

---

## §7 Implementation Roadmap

### Phase 1: IWAD/PWAD Separation (Current + 40h)

| # | Task | Effort | Depends On |
|---|------|--------|------------|
| 1.1 | Define WAD protocol interfaces in `src/omega/wad/protocols.py` | 4h | — |
| 1.2 | Refactor `wad_loader.py` to separate IWAD vs PWAD loading | 8h | 1.1 |
| 1.3 | Implement priority merge: IWAD base ← PWAD overrides | 6h | 1.2 |
| 1.4 | Add `extends` field to entity YAML schema | 4h | 1.1 |
| 1.5 | Extract 42 Ideals from prompt text into `maat_42` ethics WAD | 8h | 1.1 |
| 1.6 | Wire `IEthicsValidator` into oracle pipeline | 10h | 1.5 |

### Phase 2: Pantheon WADs (80h)

| # | Task | Effort | Depends On |
|---|------|--------|------------|
| 2.1 | Write Egyptian WAD (9+ entities, relationships, hierarchy) | 20h | 1.2 |
| 2.2 | Write Greek WAD (12+ entities) | 20h | 1.2 |
| 2.3 | Write Norse WAD (8 entities) | 12h | 1.2 |
| 2.4 | Write Hindu WAD (8 entities) | 16h | 1.2 |
| 2.5 | Write Philosophical WAD (7 entities) | 12h | 1.2 |
| 2.6 | Add `omega list-wads` and `omega wad-info` CLI commands | 4h | 1.2 |
| 2.7 | Add `--iwad` and `--pwads` flags to `omega talk` | 4h | 1.2 |

### Phase 3: Ethics WAD System (60h)

| # | Task | Effort | Depends On |
|---|------|--------|------------|
| 3.1 | `EthicsWAD` base class + `EthicsVerdict` dataclass | 4h | 1.1 |
| 3.2 | `maat_42` WAD: full validator + 42 ideals data file | 8h | 1.5 |
| 3.3 | `bushido_7` WAD: 7 virtues + validator | 6h | 3.1 |
| 3.4 | `asimov_3` WAD: 3 laws + validator | 4h | 3.1 |
| 3.5 | Pre/post filters in oracle pipeline | 8h | 3.1 |
| 3.6 | Multiple ethics WAD stacking (union of constraints) | 8h | 3.5 |
| 3.7 | Ethics violation logging + reporting | 8h | 3.5 |
| 3.8 | `omega ethics-test` CLI — test entity against ethics WAD | 6h | 3.5 |

### Phase 4: Total Conversion Support (80h)

| # | Task | Effort | Depends On |
|---|------|--------|------------|
| 4.1 | MWAD (Meta-WAD) deployment descriptors | 8h | 1.2 |
| 4.2 | WAD marketplace directory structure + spec | 4h | 4.1 |
| 4.3 | `omega wad-install` from local/git/URL | 10h | 4.1 |
| 4.4 | WAD dependency resolution (e.g., `maat_42` is a dependency of `egyptian`) | 8h | 4.3 |
| 4.5 | WAD versioning + compatibility checking | 8h | 4.4 |
| 4.6 | `omega wad-create` scaffolding (generates skeleton WAD) | 6h | 4.1 |
| 4.7 | Entity relationship graph (`relationships.yaml` → queryable graph) | 12h | 1.2 |
| 4.8 | `omega entity-family "entity_name"` — show pantheon tree | 4h | 4.7 |

---

## §8 Community WAD Marketplace

The long-term vision is a community-driven WAD marketplace:

```
omega wad-install egyptian          # Installs Egyptian pantheon
omega wad-install greek             # Installs Greek pantheon  
omega wad-install ethics_bushido    # Installs Bushido ethics module
omega list-wads                     # Shows installed WADs
omega list-wads --remote            # Shows available WADs from community hub

omega --iwad egyptian talk "Ra, guide me"
# → Loads Egyptian IWAD, resolves dependencies (maat_42 ethics)
# → Registers 9 Egyptian entities
# → Routes "Ra" query to Egyptian domain
```

### WAD Distribution Format

```yaml
# config/wads/egyptian/manifest.yaml
name: "Egyptian Pantheon"
version: "2.1.0"
description: "The complete Egyptian pantheon — Ra, Isis, Osiris, Horus, Thoth, Anubis..."
author: "Xoe-NovAi Foundation"
license: "CC-BY-SA 4.0"

dependencies:
  ethics: ["maat_42"]  # requires Ma'at 42 Ideals

entities:
  count: 9
  major: ["ra", "isis", "osiris", "horus", "thoth", "anubis", "sekhmet", "bastet", "maat"]

compatibility:
  engine: ">=1.2.0"
  python: ">=3.12"

install:
  size: "~2.4 MB"
  models: ["qwen3-1.7b-q6_k"]  # recommended local model for these entities
```

---

## §9 Relationship to Existing Patterns (Research Anchors)

### OpenPersona (acnlabs, 39 stars)
The OpenPersona framework uses a **4-layer persona architecture**: Soul / Body / Faculty / Skill. This maps elegantly to the IWAD/PWAD concept:
- **Soul** = IWAD core identity (immutable archetype)
- **Body** = PWAD cultural overlay (Egyptian, Greek, etc.)
- **Faculty** = Capability modules (knowledge retrieval, tool use)
- **Skill** = Specific domain expertise (writing, magic, war)

Omega already has this implicitly through entity YAML + WAD loading. The IWAD/PWAD formalization makes it explicit.

### Ethics Engine Triple-Gate (arXiv 2603.06599, 2026)
The arXiv paper proposes a triple gate (metric, governance, eco) for AI ethics enforcement:
- **Metric gate**: Does the response meet accuracy/fairness thresholds?
- **Governance gate**: Does the response comply with regulatory standards?
- **Eco gate**: Does the response meet carbon/water budgets?

The Omega ethics WAD proposal is a concrete implementation of the governance gate, embedded at the entity level rather than the model level.

### Doom WAD System (id Software, 1993)
The original IWAD/PWAD architecture with backward priority scan (later WADs override earlier ones) is already the pattern for Omega's WAD loader. The evolution is:
- **Doom**: IWAD (game) + PWADs (mods)
- **Omega**: IWAD (entity identity) + PWADs (cultural traditions)
- **New**: + Ethics WADs (moral frameworks) + Knowledge WADs (domain expertise)

---

## §10 Open Questions

| # | Question | Options | Status |
|---|----------|---------|--------|
| Q1 | Should `data/entities/` become the IWAD directory? | (a) Yes — entities/ = IWAD domain, config/wads/ = PWAD domain. (b) No — keep entities/ as is, add _iwad directory. (c) Merge: WADs can be either. | 🔵 |
| Q2 | Should ethics WADs be loadable at runtime without restart? | (a) Yes — hot-swappable ethics. (b) No — load at boot only. (c) Yes but cached with TTL. | 🔵 |
| Q3 | Can an entity exist WITHOUT an IWAD (PWAD-only)? | (a) No — IWAD is required. (b) Yes — PWAD can fully define an entity. (c) PWAD-only entities get a minimal auto-generated IWAD. | 🔵 |
| Q4 | Should the WAD marketplace be decentralized (git-based) or centralized (registry)? | (a) Git-based: `omega wad-install github.com/user/pantheon`. (b) Central registry: `omega wad-install egyptian` → community hub. (c) Both. | 🔵 |
| Q5 | What happens when two ethics WADs conflict? | (a) Union — most restrictive wins. (b) Priority — last loaded wins. (c) Escalate to user. | 🔵 |

---

## §11 Next Actions

1. **RATIFY** the WAD protocol interfaces (`src/omega/wad/protocols.py`) as a formal Omega extension
2. **PILOT** the 42 Ideals extraction from entity prompts into the `maat_42` ethics WAD
3. **PROTOTYPE** one pantheon WAD (Egyptian) to validate the IWAD/PWAD merge logic
4. **DOCUMENT** the WAD specification so the community can author their own pantheons
5. **MERGE** this strategy into SOVEREIGN_ARK_BLUEPRINT.md and Strike 11 (Sovereign WAD Protocol)

---

*⬡ OMEGA ⬡ WAD-EVOLUTION ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_wad_brainstorm*
