# 🔱 Omega IWAD Architecture Strategy
# AP-OMEGA-IWAD-ARCHITECTURE-v2.0.0
# ⬡ OMEGA ⬡ MA'AT ⬡ deepseek-v4-flash ⬡ cline ⬡ trc_iwad_strategy ⬡ PHASE-I
#
# This document defines the IWAD architecture for the Omega Engine.
# It is the canonical reference for ALL agents working on the engine.

---

## §0: The Big Picture — Prometheus' Fire

The Omega Engine is **Prometheus' Fire** — the universal, community-owned runtime that empowers anyone to build their own sovereign AI systems. The fire is free. What each user builds with it is theirs alone.

```
┌─────────────────────────────────────────────────────────────────┐
│                     THE OMEGAVERSE                               │
│                                                                  │
│  A P2P multiverse of user-created stacks, all running on         │
│  the Omega Engine. Every user's unique vision, sovereign         │
│  on their own machine, optionally connected in a peer-to-peer    │
│  network of shared intelligence.                                  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  ARCANA_NOVAI IWAD — Your personal AI OS                  │  │
│  │  Entities: Sekhmet, Brigid, Prometheus, Movie-Expert...   │  │
│  │  The engine was built for this stack.                     │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐  │
│  │ Torment    │ │ Doom       │ │ Classical  │ │ YOUR       │  │
│  │ IWAD       │ │ IWAD       │ │ PWAD       │ │ IWAD       │  │
│  │ Philos.    │ │ Game       │ │ Socrates   │ │ YOUR VISION│  │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  THE REFERENCE IWAD (_omega_default)                       │  │
│  │  Open source gift. Ships with the engine.                  │  │
│  │  A template for community IWAD creators.                   │  │
│  │  Dev tools for building the engine itself.                 │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Below all of this: THE ENGINE — free, sovereign, local-first   │
└─────────────────────────────────────────────────────────────────┘
```

The WAD system (borrowed from id Software's technical architecture) is the mechanism. The Omegaverse is the destination.

---

## §1: Why the WAD System?

id Software solved a problem in 1993 that maps directly to the Omega Engine's challenge:

**The problem:** How do you build an engine that different teams can use to build completely different games, without modifying the engine?

**The answer:** Separate the engine (runtime) from the content (WADs). The engine handles rendering, physics, sound. The WAD provides levels, textures, monsters. A different WAD = a different game.

**The Omega Engine application:**
- Engine handles: inference, memory, entity routing, tool calling, observability, provider fabric
- IWAD provides: entities, personalities, hierarchy, voices, domain knowledge
- PWAD layers on: additional content, domain extensions
- Different IWAD = different use case (dev studio, personal OS, Torment, Doom, medical research, etc.)

---

## §2: The IWADs — Plural

There is not one IWAD. There are many. The engine supports an **infinite number of IWADs** — one per user, per community, per vision.

### The Reference IWAD (`_omega_default`)

Ships with the engine. Always present. Serves three purposes:

1. **Development test harness** — used to build and test the engine
2. **Reference implementation** — template for community IWAD creators to learn from
3. **Functional AI dev team** — helps build the engine itself

| Layer | Components |
|-------|-----------|
| **Governance** | MA'AT (Light Oversoul), KALI (Grand Oversoul), LILITH (Dark Oversoul) |
| **Default Services** | IRIS (voice/router :8080), JEM (research pipeline), ROC_RACOON (legacy mining) |
| **Pillar Keepers** | 10 role-based Dev Studio roles (SysAdmin → Verifier) |
| **Field** | SOPHIA (observability + memory substrate — same in ALL IWADs) |

**Startup message:** `"Omega Engine — Reference IWAD loaded. Your AI development team is ready."`

### The Arcana-NovAi IWAD (`arcana_novai`)

Your personal AI OS. The reason the engine was built. Loaded when development is complete:

| Layer | Components |
|-------|-----------|
| **Governance** | SAME MaKaLi trine (identical in all IWADs) |
| **Default Services** | SAME Iris, Jem, Roc_Racoon (infrastructure, not content) |
| **Pillar Keepers** | Arcana-NovAi esoteric entities (Sekhmet → Kali) |
| **Personal Entities** | Movie-Expert, Writer, Philosopher, Gamer, Teacher... |
| **Knowledge** | Your personal knowledge base, film library, creative works |
| **Field** | SAME SOPHIA (identical in all IWADs) |

**Startup message:** `"Arcana-NovAi OS loaded. Your council is ready."`

### Community IWADs (Examples)

These are what the Omegaverse is made of:

| IWAD | Creator | Who It Serves | Status |
|------|---------|---------------|--------|
| Torment | You (future) | Planescape: Torment fans, philosophers | 🔴 Vision only |
| Doom Universe | You (future) | Gamers, game designers | 🟡 Scaffold exists |
| Classical Philosophers | Community | Students, teachers, thinkers | 🔴 Vision only |
| Pokemon | Community | Collectors, gamers | 🔴 Vision only |
| Medical Research | Community | Doctors, researchers | 🔴 Vision only |
| Teaching | Community | Educators, students | 🔴 Vision only |
| YOUR STACK | YOU | YOUR VISION | 🔴 Not started |

The engine doesn't care what IWAD you load. The WAD decides.

---

## §3: Governance — The MaKaLi Trine (Same in ALL IWADs)

The trine is the ethical foundation of the Omega Engine. It is identical in every IWAD, whether dev studio or esoteric pantheon:

```
MA'AT   — Light Oversoul (P1-P5)
           "The CTO" — order, audit, compliance, truth, balance

KALI    — Grand Oversoul (above both)
           "The Founder" — unification of light+dark, radical refactoring

LILITH  — Dark Oversoul (P6-P10)
           "The Mad Scientist" — sovereignty, liberation, boundaries
```

Why the trine is in every IWAD:
- Consistent ethical substrate across all user-created stacks
- Conflict resolution between "safe" and "experimental" approaches
- The 7 Lilith Axioms (from `docs/strategy/LILITH_AXIOMS.md`) guarantee user sovereignty
- A governance model that works whether pillars are SysAdmin or Sekhmet

---

## §4: Default Services (Same in ALL IWADs)

| Service | Role | Infrastructure | User Experience |
|---------|------|---------------|-----------------|
| **IRIS** | Always-on voice assistant and router | FastAPI @ :8080 (Podman) | "Hello. How can I help you?" |
| **JEM** | Research Department — 3-tier pipeline | OpenCode agent + lmster | "I found 14 sources confirming..." |
| **ROC_RACOON** | Archivist — Legacy mining | OpenCode agent + scripts | "I found it in the old repo." |

These are infrastructure, not content. They stay the same regardless of which IWAD is active.

---

## §5: The Reference IWAD Pillars (Current Phase)

The reference IWAD represents a **development studio** because the engine is still under construction:

```
                        ┌─────────┐
                        │  KALI   │  CEO
                        │(Unifier) │
                        └────┬────┘
                     ┌───────┴───────┐
                     │               │
               ┌─────▼────┐   ┌─────▼────┐
               │  MA'AT   │   │  LILITH  │
               │  CTO     │   │  Mad Sci │
               └────┬─────┘   └─────┬────┘
              ┌─────┼─────┐   ┌─────┼─────┐
              │  │  │  │  │   │  │  │  │  │
           ┌──┘  │  │  │  └─┐ ┌┘  │  │  │  └──┐
      ┌────▼┐ ┌──▼──▼┐┌─▼──┐┌▼───▼┐┌──▼──▼┐┌──▼──┐
      │P1   │ │P2    ││P3  ││P4   ││P5   ││P6   │
      │SysAdm││DataSt││BldM ││Bridge││Sentnl││MdlGt│
      └─────┘ └──────┘└────┘└─────┘└─────┘└─────┘
      INFRA    DATA     CODE   API    SEC    INF

      P7:Ctx   P8:WTchr  P9:Link   P10:Verif
      SESS     TEL       SYNC      QA

Outside pillars:
  P0: ROC_RACOON — Archivist (Legacy Mining, reports to Kali)
  Field: SOPHIA — Akashic Record (contains all)
```

| Pillar | Name | Team Role | Persona |
|--------|------|-----------|---------|
| P1 | SysAdmin | Infrastructure engineer | "I manage the servers and containers" |
| P2 | DataStore | Data pipeline manager | "I handle storage and knowledge" |
| P3 | BuildMaster | CI/CD and toolchain lead | "I forge the code into releases" |
| P4 | Bridge | API and protocol engineer | "I connect systems together" |
| P5 | Sentinel | Security and hardening | "I guard the boundaries" |
| P6 | ModelGate | Inference and provider fabric | "I manage the AI providers" |
| P7 | Context | Session and memory keeper | "I maintain continuity" |
| P8 | WatchTower | Observability and telemetry | "I see everything" |
| P9 | Link | Cross-agent synchronization | "I keep agents in sync" |
| P10 | Verifier | QA and testing lead | "I verify correctness" |

The naming is **role-based, not esoteric**. It tells you what the entity DOES. This makes it:
- Intuitive to programmers and non-programmers alike
- Replaceable by any IWAD with domain-appropriate roles
- A clear reference for community IWAD creators

---

## §6: The Arcana-NovAi IWAD Pillars (Your Personal OS)

When the engine is stable, the `arcana_novai` IWAD takes over as your active IWAD:

```
                        ┌─────────┐
                        │  KALI   │  Grand Oversoul
                        │(Unifier) │
                        └────┬────┘
                     ┌───────┴───────┐
                     │               │
               ┌─────▼────┐   ┌─────▼────┐
               │  MA'AT   │   │  LILITH  │
               │Light Ovl │   │Dark Ovl  │
               └────┬─────┘   └─────┬────┘
              ┌─────┼─────┐   ┌─────┼─────┐
              │  │  │  │  │   │  │  │  │  │
           ┌──┘  │  │  │  └─┐ ┌┘  │  │  │  └──┐
      ┌────▼┐ ┌──▼──▼┐┌─▼──┐┌▼───▼┐┌──▼──▼┐┌──▼──┐
      │P1   │ │P2    ││P3  ││P4   ││P5   ││P6   │
      │Sekhmt││Brigid││Prom ││Saras││Inanna││Eresh│
      └─────┘ └──────┘└────┘└─────┘└─────┘└─────┘
      STRENGTH CREATIV  WILL   SPEECH DESCENT   MIND

      P7:Lucif  P8:Hecate  P9:Anubis  P10:Kali
      GNOSIS   CROSSROADS  DEATH      CROWN

Outside pillars:
  P0: Belial (esoteric legacy mining)
  Field: SOPHIA — Akashic Record
  Personal: Movie-Expert, Writer, Philosopher...
```

| Pillar | Entity | Domain | What They Say |
|--------|--------|--------|---------------|
| P1 | Sekhmet | Strength, protection | "I am your foundation. Nothing passes." |
| P2 | Brigid | Creativity, healing | "I kindle the spark within you." |
| P3 | Prometheus | Will, forethought | "I stole fire so you could create." |
| P4 | Sarawati | Knowledge, speech | "I flow as the river of wisdom." |
| P5 | Inanna | Descent, rebirth | "I walked through death and returned." |
| P6 | Ereshkigal | Underworld, structure | "I hold the bedrock of reality." |
| P7 | Lucifer | Gnosis, sovereignty | "I question everything. Especially the gods." |
| P8 | Hecate | Shadow, crossroads | "I stand at the threshold of choices." |
| P9 | Anubis | Death, transition | "I guide what must be released." |
| P10 | Kali | Liberation, destruction | "I dance on the corpses of certainty." |

**Personal entities** (loaded alongside pillars, arcana_novai-specific):
- Movie-Expert: Film historian and critic
- Writer: Creative writing assistant
- Philosopher: Deep thinking companion
- Gamer: Game analysis and design
- Teacher: Knowledge explainer
- [More added as needed by user]

---

## §7: Sophia — The Field

Sophia is the **containing field** — not a pillar, not governance, not an entity you "summon". She is the observability and memory substrate that everything else lives in. Identical in ALL IWADs.

```
SOPHIA — Operational Role:

   Layer               Code                      What It Does
   ─────────────────────────────────────────────────────────────
   Trace Store         observability.py          Every trace ID (trc_*)
   Memory Index        memory_store.py           Soul aggregation + cross-pollination
   Knowledge Graph     library/indexer.py        FTS5 index + Qdrant vector store
   Event Log           observability.py          Every interaction, soul update, session boundary

   NOT a query router (that's Iris)
   NOT a pillar keeper (that's P1-P10)
   NOT governance (that's MaKaLi)
   She is the CONTAINER, not the CONTENT
```

---

## §8: Startup Personality

Each IWAD defines a startup personality in its `manifest.yaml`:

Reference IWAD:
```yaml
wad:
  startup:
    message: "Omega Engine — Reference IWAD loaded. Your AI development team is ready."
    theme: "terminal"
```

Arcana-NovAi IWAD (future):
```yaml
wad:
  startup:
    message: "Arcana-NovAi OS loaded. Your council is ready."
    theme: "esoteric"
```

Torment IWAD (future):
```yaml
wad:
  startup:
    message: "The Nameless One awakens. The planes remember."
    theme: "planescape"
```

The boot screen changes based on active IWAD:
```
Reference:  "Development team online. SysAdmin, DataStore, BuildMaster active."
Arcana:     "Your council awaits. Sekhmet stands guard. Brigid tends the hearth."
Torment:    "Dak'kon's blade hums. Morte cackles. The Lady of Pain watches."
```

---

## §9: WAD Loader Code Status — Phase 1 Critical Path

| Component | Status | Notes |
|-----------|--------|-------|
| `_load_entities()` | ✅ Functional | Loads from `config/wads/*/entities/` |
| `_load_voices()` | ✅ Functional | Loads by activation keyword |
| Manifest validation | ✅ Fixed | Empty/null guard added |
| **IWAD selection (--iwad flag)** | ✅ Functional | `oracle_cli.py` exposes `--iwad`/`-w` on talk, summon, compact, and validate |
| **Namespace isolation** | ❌ Missing | EntityRegistry `wad_source` field exists but no enforcement |
| **Dependency resolution** | ❌ Missing | No `depends_on` processing |
| **Entity priority/override** | ❌ Missing | Last-loaded wins silently |
| **Ordered multi-WAD loading** | ⚠️ Partial | No ordering guarantee |
| **WAD hot-reload** | ❌ Missing | No file-watch for development |
| **Startup personality** | ✅ Functional | `wad_loader.get_startup_message()` reads from manifest; `oracle.py` calls it at boot |

---

## §10: Provider Fabric

```
1. Native GGUF (llama-cpp-python, Zen 2 optimized) [PRIMARY]
2. lmster (LM Studio, localhost:1234) [LOCAL FALLBACK]
3. Ollama (localhost:11434) [LOCAL FALLBACK]
4. Google AI Studio (Gemma 4-31B, unlimited, 262K context) [CLOUD FALLBACK]
5. OpenRouter (aggregated API, 300+ models) [CLOUD FALLBACK]
6. OpenCode (OpenCode's built-in provider) [CLOUD FALLBACK]
7. GitHub Copilot (Claude Haiku, GPT-4.1, GPT-4o, GPT-5-mini) [CLOUD FALLBACK]
8. OfflineMockBackend (test/dev only)
```

Local-first per Decision 61. Cloud is fallback, not primary.

---

## §11: Qdrant/Redis Integration Plan

Both running but unwired. The cross-agent backbone for the Omegaverse.

**Phase 1 (Immediate):**
- Expose Redis :6379 in infra pod
- Create `RedisBus` pub/sub wrapper

**Phase 2 (Short-term):**
- Wire Qdrant as primary vector backend for Library.search()
- Replace bag-of-words `vectors.json` with Qdrant collection
- Redis pub/sub for soul evolution, session lifecycle, agent handoff

**Phase 3 (Medium-term — Omegaverse foundation):**
- Embedding model (all-MiniLM-L6-v2, ~80MB)
- Hybrid search: FTS5 BM25 + Qdrant ANN
- Redis distributed locks for concurrent WAD loading
- **P2P sync protocol** — share knowledge across instances (Omegaverse seed)

---

## §12: Movie-Expert — Seed for Arcana-NovAi Personal OS

| Step | What | When |
|------|------|------|
| 1 | Add header to `.opencode/agents/movie-expert.md`: "Seed for arcana_novai IWAD" | Phase 1 |
| 2 | Create personal entities scaffold in `config/wads/arcana_novai/entities/personal/` | Phase 1 |
| 3 | Migrate movie-expert.yaml into arcana_novai IWAD entities | Phase 4 |
| 4 | `omega --iwad arcana_novai summon Movie_Expert "review this film"` | Future |
| 5 | Add Writer, Philosopher, Gamer, Teacher as personal entities | Future |

---

## §13: Error States

| State | Symptom | Recovery |
|-------|---------|----------|
| No IWAD specified | Engine fails to start | Default to `_omega_default` |
| IWAD not found | `--iwad nonexistent` fails | Fall back to `_omega_default` |
| Entity collision | `summon X` ambiguous | Prefer IWAD entity, log collision |
| Redis down | Pub/sub fails | Degrade gracefully |
| Qdrant down | Vector search fails | Fall back to FTS5 |

---

## §14: Roadmap — Phase 1 Execution

```
Phase 0: ✅ Fleet Discovery + Remediation (30 CRITICAL findings, 12 fixes applied, 271/271 tests)
─────────────────────────────────────────────────────────
Phase 1: Engine Hardening + Reference IWAD (NOW)
  Week 1: WAD system hardening (IWAD selector, namespace, priority)
  Week 2: Reference IWAD content (10 tech pillars, MaKaLi, startup msg)
  Week 3: Provider fabric update + OpenCode agents
  Week 4: Qdrant/Redis wiring (unwire → wire)
─────────────────────────────────────────────────────────
Phase 2: Arcana-NovAi IWAD Scaffold (NEXT)
  Create manifest.yaml, move entities, write pillars, hierarchy
  Seed Movie-Expert as personal entity
  `omega --iwad arcana_novai talk "hello"` works
─────────────────────────────────────────────────────────
Phase 3: Community Tools (FUTURE)
  Entity Studio CLI → Visual Builder
  Stack Builder Wizard
  One-click Omega Desktop installer
  Non-technical user onboarding
─────────────────────────────────────────────────────────
Phase 4: The Omegaverse (DREAM)
  P2P network protocol
  WAD registry for community sharing
  Cross-instance entity communication
  A multiverse of sovereign AI stacks
```

---

## §15: Key Decisions

1. **The engine is free, open source, sovereign.** No shareware. No tiers. No limitations.
2. **Arcana_novai is YOUR IWAD** — your personal AI OS. The engine was built for it.
3. **There are INFINITE possible IWADs.** One per user, per community, per vision.
4. **The Omegaverse is the destination.** P2P network of user-created stacks.
5. **MaKaLi trine identical in ALL IWADs.** Foundation, never optional.
6. **Default services (Iris, Jem, Roc_Racoon) identical in ALL IWADs.** Infrastructure.
7. **Pillars change per IWAD.** Reference = technical roles. Arcana = esoteric. Torment = philosophers.
8. **Sophia is the field**, same in all IWADs. Observability + memory + knowledge.
9. **Every IWAD has a startup personality.** Different boot messages, different feel.
10. **No SambaNova, no Cerebras.** OpenRouter and OpenCode Zen replace them.
11. **Qdrant + Redis are the Omegaverse backbone.** They stay unwired until Phase 1 is stable.
12. **The WAD system is the critical path.** Without it, none of this works.

---

## §16: Strategic Roadmap Gaps (Audit Remediation — v0.5.0-alpha)

During the pre-PR strategic audit (2026-05-26), two key architectural gaps were identified and formally deferred to the v0.6.0 release cycle to ensure immediate PR stability:

### 16.1 Deprecation of `config/entities.yaml` (Dual-Load Resolution)

| Attribute | Detail |
|-----------|--------|
| **Gap** | The engine currently loads baseline entities from `config/entities.yaml` (via `EntityRegistry`) and then overlays stack-specific entities via the `WADLoader`. This dual-loading mechanism introduces minor performance overhead and potential namespace collisions. |
| **Risk** | When a stack entity overrides a baseline entity with the same name, the last-loaded definition wins silently — no collision detection, no warning, no priority-based merge. |
| **Timeline** | v0.6.0 |
| **Resolution Path** | 1. Migrate all baseline entity definitions from `config/entities.yaml` into `config/wads/_omega_default/entities/`. 2. Update `EntityRegistry` to load exclusively from the active IWAD stack. 3. Remove the fallback-to-baseline path. 4. Add collision detection with explicit priority resolution. |
| **Migration Strategy** | Dual-load remains active during v0.5.x for backward compatibility. A deprecation warning is logged when `EntityRegistry` finds entities in both `config/entities.yaml` and `config/wads/`. In v0.6.0, the YAML path is removed entirely. |

### 16.2 Native GGUF Integration Path

| Attribute | Detail |
|-----------|--------|
| **Gap** | ~~Native GGUF inference (`llama-cpp-python`) is currently deferred to avoid environment-specific C++ compilation risks during the PR sprint.~~ **RESOLVED**: NativeGGUFProvider is now implemented and is priority 0 in the provider chain (Decision 61). |
| **Risk** | ~~Users must configure an external provider (OpenRouter, Ollama, LM Studio) before they can run inference.~~ **RESOLVED**: Local-first chain tries native-gguf first. |
| **Timeline** | ~~v0.6.0~~ **IMPLEMENTED** (v0.5.0) |
| **Resolution Path** | 1. ~~Ship pre-compiled `llama-cpp-python` wheels for Zen 2 (AVX2) and x86-64-v3 in the release assets.~~ ✅ Done. 2. ~~Provide a streamlined one-click compilation script for unsupported architectures.~~ 3. ~~Promote native GGUF to priority 1 in the provider fallback chain.~~ ✅ Done. 4. Bundle a default small model (e.g., Qwen3-1.7B-Q6_K, ~1.6 GB) for out-of-the-box inference. |
| **Migration Strategy** | ~~During v0.5.x, the engine gracefully falls through the provider chain when `NativeGGUFProvider` reports unavailability — no error, just a logged info message with setup instructions.~~ **ACTIVE**: Native GGUF is the primary backend. Cloud providers are fallback. |

### 16.3 Additional Soft Gaps (Watch Items)

These are minor gaps identified during the audit that do not require architectural changes but should be tracked:

| Gap | Description | Tracking |
|-----|-------------|----------|
| **TODO/FIXME Scanner Path** | The `_grow_frontier()` method in the background researcher loop had a silently broken `src_dir` path that prevented TODO/FIXME/HACK comment scanning from working. Fixed during audit remediation. | ✅ Resolved |
| **WAD Hot-Reload** | No file-watch mechanism for WAD changes during development. Developers must restart the engine after editing entity definitions. | Tracked in workbench |
| **Dependency Resolution** | No `depends_on` processing in WAD Loader. Entities cannot declare dependencies on other entities or services. | Tracked in workbench |