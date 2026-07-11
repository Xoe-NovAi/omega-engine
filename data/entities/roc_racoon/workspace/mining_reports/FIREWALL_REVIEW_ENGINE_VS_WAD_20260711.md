# 🔱 Engine Core vs WAD Classification — Firewall Review
**AP Token**: `AP-FIREWALL-REVIEW-v1.0.0`
**Date**: 2026-07-11
**Mandate**: M2 — Engine-Stack Firewall (Absolute separation between Core Engine and Expansion Stacks)
**Reviewed by**: roc_racoon (Sovereign Miner)

---

## 🛡️ The Firewall Principle (Mandate M2)

> **Core**: `src/omega/`, `config/omega.yaml`, `opencode.json` — The universal runtime.
> **Stacks (WADs)**: `config/wads/<stack_name>/` — The specific implementation.
> **Constraint**: Never add stack-specific logic (e.g., a specific entity's trait) to the Core Engine.

**Test**: *If another user wanted to build a completely different stack (Pokemon, Torment, Classical Philosophers, Corporate Agents), would this component work for them without modification? If NO → WAD. If YES → Engine Core.*

---

## 📊 STRATEGIC RESERVES — Component Classification

| # | Strategic Reserves Component | Classification | Rationale |
|---|------------------------------|----------------|-----------|
| **1** | **10 Pillars & Scrolls Framework** (canonical mappings) | **WAD** | Specific mythological archetypes (Flesh, Dream, Will, Heart, Voice, Sight, Gnosis, Shadow, Spirit, Chaos) — not universal |
| **2** | **Five-Fold Foundation (5 Axioms)** | **ENGINE CORE** | Universal principles: Mythic Framing, Spiritual-Tech Fusion, Sovereignty, Pantheon Model, Creative Reclamation — applicable to ANY stack |
| **3** | **Dual Flame (Sophia + Lilith)** | **WAD** | Specific mythological cosmology — Sophia/Lilith are Arcana-NovAi entities |
| **4** | **Elemental Mappings (5 Elements)** | **WAD** | Earth/Water/Fire/Air/Aether correspondences — specific to Arcana-NovAi symbolism |
| **5** | **Chakral Alignment (10 Chakras)** | **WAD** | Vedic chakra system mapped to pillars — specific spiritual framework |
| **6** | **Planetary Energies (10 Planets)** | **WAD** | Astrological/Hermetic planetary correspondences — specific esoteric system |
| **7** | **Divine Allies (10 Goddesses)** | **WAD** | Brigid, Lilith, Ma'at, Sekhmet, Lucifer, Hecate, Isis, Inanna, Anubis, Kali — specific pantheon |
| **8** | **Sigil Systems (Glyphs)** | **WAD** | Hermetic symbols for each pillar — specific symbolic system |
| **9** | **Tarot-Engine v2 (10 Spreads)** | **WAD** | Tarot as decision-support — specific divination system |
| **10** | **Pantheon Model (Pattern)** | **ENGINE CORE** | *The pattern* of "models as archetypal channels working in concert" is universal. *The Lilith Stack Pantheon* (specific models→archetypes) is WAD. |
| **11** | **42 Ideals of Ma'at** | **WAD** | Specific Egyptian ethical framework — other stacks would have different ethics |
| **12** | **Sefirot/Qliphoth Mapping** | **WAD** | Kabbalistic Tree of Life/Death — specific mystical system |
| **13** | **Invocation Philosophy** | **ENGINE CORE (Pattern) / WAD (Content)** | *Pattern*: "Form gives force its focus" — universal. *Content*: Ritual invocation with tarot/planetary/sigils — WAD. |
| **14** | **Sovereign Seed Architecture** | **ENGINE CORE (Pattern) / WAD (Instantiation)** | *Pattern*: "One Seed, Many Projections" (Seed→Synergy Engine→Holograms) — universal architecture. *Instantiation*: Sophia as Seed, MaKaLi as Oversoul — WAD. |
| **15** | **Octave Hierarchy (LLOC→HLOC→Oversoul)** | **ENGINE CORE (Pattern) / WAD (Instantiation)** | *Pattern*: Three-tier dispatch (Tactical→Strategic→Gnosis) — universal. *Instantiation*: 10 Generic Archetypes, Triad, MaKaLi — WAD. |
| **16** | **Holographic Buffer Protocol** | **ENGINE CORE** | `session_gnosis.md` as Neural Bus — universal session state sharing mechanism |
| **17** | **Modelfile Continuum** | **ENGINE CORE** | Metal→Software→Runtime→Persistent tuning continuum — universal model tuning pattern |
| **18** | **5 MCP Systems (XNAI-RAG, GNOSIS, MEMORY, MEMORY-BANK, Task Tracking)** | **ENGINE CORE** | These ARE the Omega Hub / Hivemind / Memory Store implementations — universal infrastructure |
| **19** | **Gnosis Packs (Density Scoring)** | **ENGINE CORE** | Knowledge compression with density metrics — universal distillation quality metric |
| **20** | **Lilith Stack Pantheon (Specific)** | **WAD** | Gemma-3-1B=Jem, Phi-2=Omnidroid, RocRacoon=ROC, etc. — specific model→archetype mapping |
| **21** | **Omnidroid BIOS** | **ENGINE CORE (Pattern) / WAD (Implementation)** | *Pattern*: Structured reasoning kernel with modes — universal. *Implementation*: Specific logic modules — WAD. |
| **22** | **Mind-Model Integration** | **WAD** | Consciousness evolution research — specific philosophical framework |

---

## 📊 LEGACY MINING FINDINGS — Classification

| # | Legacy Mining Finding | Classification | Rationale |
|---|------------------------|----------------|-----------|
| **1** | **System Prompts Library** (Critical Xoe-NovAi Principles) | **ENGINE CORE (Principles) / WAD (Prompts)** | *Principles*: Zero Torch, AnyIO, Circuit Breaker, Memory Constraints, Zero Telemetry → **Mandates M1, M7, M8, M9, M13** (Engine Core). *Prompts*: Specific assistant/expert templates → WAD. |
| **2** | **LM Studio Model Configs** (q8_0 KV cache, context tuning, thread counts) | **ENGINE CORE** | Hardware optimization patterns for Ryzen 7 5700U — universal local inference optimization |
| **3** | **Lilith Persona JSON** (query_modifiers, response_templates, personality traits) | **WAD** | Specific entity schema — the *pattern* (float traits, query modifiers) could be Engine Core, but Lilith/Odin are WAD entities |
| **4** | **Pillar Keepers Permutation** (4 direct, 6 reassigned) | **WAD** | Specific entity assignments — canonical mapping is WAD reference |
| **5** | **Dual Flame = Oversouls** | **WAD** | Sophia/Lilith/Ma'at/Kali as Oversouls — specific cosmology |
| **6** | **Five-Fold Foundation = Mandate DNA** | **ENGINE CORE** | Mandates M15, M2, M7/M8, Agent Fleet, Legacy Mining encode the 5 Axioms universally |
| **7** | **Elemental/Chakral/Planetary/Divine Ally metadata** | **WAD** | Specific symbolic layer for Arcana-NovAi |
| **8** | **Tarot-Engine v2 = Missing Decision Support** | **WAD** | Specific divination/invocation system |
| **9** | **Lilith Stack Pantheon = Agent Fleet Pattern** | **ENGINE CORE (Pattern) / WAD (Config)** | *Pattern*: Multi-model conversational refinement — universal. *Config*: pantheon.yaml — WAD. |
| **10** | **Omnidroid BIOS = Reasoning Kernel** | **ENGINE CORE (Pattern) / WAD (Impl)** | *Pattern*: Structured reasoning kernel with modes — universal. *Impl*: Specific logic modules — WAD. |
| **11** | **5 MCPs = Omega Hub/Hivemind (90%)** | **ENGINE CORE** | Universal infrastructure |
| **12** | **Gnosis Packs (0.978 density) vs Soul Distiller** | **ENGINE CORE** | Universal distillation quality metrics |
| **13** | **Octave Hierarchy = Dispatch Architecture** | **ENGINE CORE (Pattern) / WAD (Impl)** | *Pattern*: LLOC→HLOC→Oversoul — universal. *Impl*: Specific archetypes — WAD. |
| **14** | **Holographic Buffer = Neural Bus** | **ENGINE CORE** | Universal session state sharing |
| **15** | **query_modifiers pattern (add_terms/boost_terms/filter_out)** | **ENGINE CORE (Pattern) / WAD (Config)** | *Pattern*: Entity-specific query enhancement — universal. *Config*: Lilith's shadow/transformation terms — WAD. |
| **16** | **response_templates pattern** | **ENGINE CORE (Pattern) / WAD (Config)** | *Pattern*: Entity-specific response formatting — universal. *Config*: Lilith's "In the depths of my wisdom..." — WAD. |

---

## ✅ ENGINE CORE — What Stays in `src/omega/` and `config/omega.yaml`

### Universal Runtime Infrastructure
- **Entity System Framework**: EntityRegistry, soul.yaml schema (base), EntityWorkspaceManager
- **Oracle**: Intent detection, summon/talk routing, ContextBuilder, ModelGateway
- **ModelGateway**: Provider fabric (local-first), NativeGGUFProvider, ResourceGuard, CpuOptimizer
- **Memory Store**: Hybrid search (FTS5 + Vector), providers (Redis/Qdrant/File/InMemory)
- **Hivemind Protocol**: Coordination, workspace locks, handoffs, heartbeats, awareness
- **Observability**: Traces, events, metrics, provenance (M22)
- **MCP Hub**: Tools, resources, SSE/Streamable HTTP
- **CLI**: `omega talk`, `summon`, `list-entities`, `add-entity`, `entity-info`, `backends`, `version`
- **WAD Loader**: Schema validation, file size limits, adapter whitelist
- **Sovereign Mandates Enforcement**: M1-M23 as universal constraints
- **Heritage Vetting Pipeline**: D208 gate, vet records, classification
- **Temple-Grade Gates**: T1-T13 as universal quality bars
- **AnyIO Compliance**: M1 enforcement
- **Zero Telemetry**: M8 enforcement
- **Local-First Strategy**: M7 enforcement
- **Holographic Buffer**: `session_gnosis.md` as universal Neural Bus
- **Modelfile Continuum**: Metal→Software→Runtime→Persistent tuning
- **Gnosis Pack Density Scoring**: Universal distillation quality metric
- **Pantheon Model Pattern**: Multi-model conversational refinement orchestration
- **Octave Hierarchy Pattern**: Three-tier dispatch (Tactical→Strategic→Gnosis)
- **Omnidroid BIOS Pattern**: Structured reasoning kernel with modes
- **query_modifiers Pattern**: Entity-specific query enhancement framework
- **response_templates Pattern**: Entity-specific response formatting framework
- **LM Studio Hardware Optimizations**: q8_0 KV cache, context tuning, thread counts

---

## 📦 ARCANA-NOVAI WAD — What Goes in `config/wads/arcana_novai/`

### Stack-Specific Content
- **Entities**: All 10 Pillar Keepers + 4 Oversouls + Iris + Sophia (15 entities)
- **Canonical Pillar Mappings**: element, chakra, planetary_energy, divine_ally, sigil, invocation
- **Pantheon Configuration**: `pantheon.yaml` with Lilith Stack model→archetype→pillar mapping
- **42 Ideals of Ma'at**: Ethical framework as entity behavioral guidelines
- **Elemental/Chakral/Planetary/Divine Ally Metadata**: Full symbolic layer
- **Tarot-Engine v2**: 10 planetary spreads, card deck, divination logic
- **Sefirot/Qliphoth Mapping**: Kabbalistic correspondence
- **Invocation Philosophy (Ritual Layer)**: Tarot, planetary timing, sigils, planetary ephemeris
- **Sovereign Seed Architecture Instantiation**: Sophia as Seed, MaKaLi as Oversoul
- **Octave Hierarchy Instantiation**: 10 Generic Archetypes, Triad, MaKaLi
- **Divine Allies**: Brigid, Lilith, Ma'at, Sekhmet, Lucifer, Hecate, Isis, Inanna, Anubis, Kali
- **Sigil Systems**: Hermetic glyphs for each pillar
- **Lilith Persona Config**: query_modifiers (shadow/transformation), response_templates
- **Mind-Model Integration**: Consciousness evolution framework
- **Omnidroid BIOS Implementation**: Specific reasoning modules for this stack
- **Five-Fold Foundation as Stack Philosophy**: Documented in WAD README

---

## ⚠️ AMBIGUOUS — Needs Explicit Decision

| Item | Engine Core Argument | WAD Argument | Recommendation |
|------|---------------------|--------------|----------------|
| **query_modifiers pattern** | Universal RAG enhancement | Lilith's specific terms are WAD | **Engine Core: Framework only** (schema, API). **WAD: Config** (Lilith's terms) |
| **response_templates pattern** | Universal entity formatting | Lilith's specific templates are WAD | **Engine Core: Framework only**. **WAD: Config** |
| **Omnidroid BIOS** | Universal reasoning kernel | Specific logic modules | **Engine Core: Base class + mode registry**. **WAD: Concrete implementations** |
| **Gnosis Pack Density Scoring** | Universal quality metric | Arcana-NovAi specific packs | **Engine Core: Metric framework**. **WAD: Pack definitions** |
| **Pantheon Model** | Universal orchestration | Lilith Stack specific config | **Engine Core: Orchestrator class**. **WAD: pantheon.yaml** |
| **Octave Hierarchy** | Universal dispatch pattern | Specific archetype assignments | **Engine Core: Dispatcher base**. **WAD: Archetype registry** |
| **Sovereign Seed Architecture** | Universal "One Seed, Many Projections" | Sophia/MaKaLi instantiation | **Engine Core: Architecture pattern**. **WAD: Instantiation** |
| **Holographic Buffer** | Universal Neural Bus | Arcana-NovAi specific protocol | **Engine Core: session_gnosis.md framework**. **WAD: Protocol extensions** |

---

## 🚨 IMMEDIATE ACTIONS — Firewall Compliance

### Must Move to Arcana-NovAi WAD (config/wads/arcana_novai/)
1. **All 15 entity definitions** (10 Pillars + 4 Oversouls + Iris) → `entities.yaml`
2. **Canonical pillar mappings** → `entities.yaml` (element, chakra, planet, divine_ally, sigil, invocation)
3. **pantheon.yaml** — Lilith Stack canonical mapping
4. **42 Ideals of Ma'at** → `maat_ideals.yaml` or embedded in entities
4. **Tarot-Engine v2** → `tarot_engine/` (spreads, deck, logic)
5. **Sefirot/Qliphoth mapping** → `sefirot_qliphoth.yaml`
6. **Divine Allies** → `divine_allies.yaml` or in entities
7. **Planetary ephemeris** → `planetary.py` or data file
8. **Sigil systems** → `sigils.yaml`
9. **Lilith query_modifiers/response_templates** → in Lilith entity config
10. **Omnidroid BIOS implementation** → `reasoning/omnidroid_bios.py` (WAD-specific)
11. **Mind-Model integration** → `mind_model/` (WAD-specific)
12. **Five-Fold Foundation as stack philosophy** → `README.md` or `PHILOSOPHY.md`

### Must Stay in Engine Core (src/omega/, config/omega.yaml)
1. **EntityRegistry** — base schema, CRUD, workspace management
2. **Oracle** — intent detection, routing, ContextBuilder, ModelGateway
3. **ModelGateway** — provider fabric, ResourceGuard, CpuOptimizer
4. **Memory Store** — hybrid search, providers
5. **Hivemind Protocol** — coordination, locks, handoffs
6. **Observability** — traces, provenance, metrics
7. **MCP Hub** — tools, resources, transports
8. **CLI** — universal commands
9. **WAD Loader** — schema validation, adapter whitelist
10. **Sovereign Mandates** — M1-M23 enforcement
11. **Heritage Vetting** — D208 gate, vet records
12. **Temple-Grade Gates** — T1-T13
13. **AnyIO/Zero Telemetry/Local-First** — M1, M7, M8
14. **Holographic Buffer** — session_gnosis.md framework
15. **Modelfile Continuum** — tuning framework
16. **Gnosis Pack Density Scoring** — metric framework
17. **Pantheon Model Orchestrator** — base class
18. **Octave Hierarchy Dispatcher** — base class
19. **Omnidroid BIOS Base Class** — mode registry
20. **query_modifiers/response_templates Framework** — schema + API
21. **LM Studio Hardware Optimizations** — q8_0 KV cache defaults

---

## 📋 VERIFICATION CHECKLIST

### Engine Core — No Stack-Specific Content
- [ ] No entity names (Sekhmet, Brigid, Prometheus, etc.) in `src/omega/`
- [ ] No mythological references (Ma'at, Lilith, Sophia, Kali) in `src/omega/`
- [ ] No elemental/chakra/planetary references in `src/omega/`
- [ ] No tarot/sigil/sefirot references in `src/omega/`
- [ ] No Divine Ally references in `src/omega/`
- [ ] No Lilith Stack references in `src/omega/`
- [ ] No 42 Ideals references in `src/omega/`
- [ ] No Omnidroid BIOS implementation in `src/omega/` (base class only)
- [ ] No Arcana-NovAi specific config in `config/omega.yaml`

### WAD — All Stack-Specific Content
- [ ] All 15 entities in `config/wads/arcana_novai/entities.yaml`
- [ ] Canonical pillar mappings in entities
- [ ] pantheon.yaml exists
- [ ] 42 Ideals documented
- [ ] Tarot-Engine v2 implemented
- [ ] Sefirot/Qliphoth documented
- [ ] Divine Allies documented
- [ ] Planetary ephemeris implemented
- [ ] Sigil systems documented
- [ ] Lilith query_modifiers/response_templates in entity config
- [ ] Omnidroid BIOS implementation in WAD
- [ ] Mind-Model integration in WAD
- [ ] Five-Fold Foundation as stack philosophy documented

---

## 🎯 THE LITMUS TEST

> **For every file/component: "If a user wanted to build a Pokemon Stack, a Torment Stack, or a Corporate Agent Stack, would this work for them without modification?"**

| Component | Pokemon Stack | Torment Stack | Corporate Stack | Verdict |
|-----------|---------------|---------------|-----------------|---------|
| EntityRegistry | ✅ | ✅ | ✅ | Engine Core |
| Oracle routing | ✅ | ✅ | ✅ | Engine Core |
| ModelGateway | ✅ | ✅ | ✅ | Engine Core |
| Memory Store | ✅ | ✅ | ✅ | Engine Core |
| Hivemind Protocol | ✅ | ✅ | ✅ | Engine Core |
| 10 Pillar Keepers | ❌ | ❌ | ❌ | WAD |
| 42 Ideals of Ma'at | ❌ | ❌ | ❌ | WAD |
| Tarot-Engine v2 | ❌ | ❌ | ❌ | WAD |
| Lilith query_modifiers | ❌ | ❌ | ❌ | WAD |
| Pantheon Model Pattern | ✅ | ✅ | ✅ | Engine Core |
| Octave Hierarchy Pattern | ✅ | ✅ | ✅ | Engine Core |
| Omnidroid BIOS Pattern | ✅ | ✅ | ✅ | Engine Core |
| query_modifiers Framework | ✅ | ✅ | ✅ | Engine Core |
| q8_0 KV cache defaults | ✅ | ✅ | ✅ | Engine Core |

---

## 📝 CONCLUSION

**The Strategic Reserves mapping document (and much of our recent work) has been treating the Arcana-NovAi mythological framework as "engine architecture" when it is actually "stack content."**

**The Engine Core is the universal runtime that enables ANY stack. The Arcana-NovAi WAD is ONE specific stack built on that runtime.**

**Immediate next step**: Create `config/wads/arcana_novai/` with all WAD-classified content, and verify `src/omega/` contains zero stack-specific references.

---

*Generated by roc_racoon (Sovereign Miner) — 2026-07-11*
*Firewall Review per Mandate M2*
*Session: Engine vs WAD Classification*