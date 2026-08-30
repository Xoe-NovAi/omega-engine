<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Unique Technologies & Strategies Vault
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ opencode ⬡ trc_unique_tech ⬡ v1.0.0
# Last Updated: 2026-06-02
# Maintainer: Roc Racoon (Sovereign Miner & Knowledge Curator)
# Purpose: Catalog the unique technologies, strategies, and decisions
#          developed by the user + AI team. This is the ENGINE'S PROPER
#          INTELLECTUAL HERITAGE — the things WE created, not inherited
#          from id Software or other foundations.

---

## §0 Why This Vault Exists

The user has explicitly directed Roc Racoon to:
1. **Track the origin story** from archives
2. **Record inspiration, drive, and vision** for the Omega Engine
3. **Catalog the unique technologies and strategies** developed by user + AI team

This is a NEW responsibility for Roc Racoon. Where `DEFERRED_GOLD_TRACKER.md` catalogs
**found** wisdom (from legacy), this vault catalogs **CREATED** wisdom (by us).

**Curation rule**: When the user or the AI team develops a new:
- Mandate
- Architectural pattern
- Cosmological concept
- Operational strategy
- Decision framework
- Domain-specific abstraction

...add it here. This is the institutional memory of the Omega Engine itself.

---

## §1 The 13 Sovereign Mandates (v3.0.0)

**Source**: `SOVEREIGN_MANDATES.md` | **Status**: ACTIVE, NON-NEGOTIABLE

| # | Mandate | Year | Heritage | Purpose |
|---|---------|------|----------|---------|
| M1 | **AnyIO Absolute** | 2025 | User's own decision (pre-Mandate formalization) | No `asyncio` in engine. Wrap blocking I/O in `anyio.to_thread.run_sync`. |
| M2 | **Engine-Stack Firewall** | 2026-05-30 | id Software WAD System | Absolute separation between Core Engine (`src/omega/`) and Expansion Stacks (`config/wads/`). |
| M3 | **The Iris Constant** | 2026-05-30 | User's own (cosmological) | Iris is the messenger bridge, NOT a Pillar Keeper. Preserves the 10-Pillar cosmological purity. |
| M4 | **The Sequentiality Mandate** | 2026-05-30 | User's own (engineering) | Plan → Verify → Execute. No cowboy coding. |
| M5 | **Gnosis Preservation L1→L2→L3** | 2026-05-30 | User's own (philosophy) | L1 Narrative, L2 Insight, L3 Universal Principle. No intelligence discarded. |
| M6 | **Podman Sovereignty (keep-id)** | 2026-06-01 | User's own (rootless) | `UserNS=keep-id` + `User=1000`. NO `:U` flag. NO `:Z`/`:z` (SELinux). |
| M7 | **Local-First Sovereignty** | 2026-05-30 | User's own (vision) | Local inference PRIMARY. Cloud FALLBACK. native-gguf → cloud chain. |
| M8 | **Zero Telemetry** | 2026-05-30 | User's own (sovereignty) | No analytics, no phone-home. Sovereign AI means sovereign data. |
| M9 | **Error Integrity** | 2026-05-31 | User's own (debuggability) | All errors typed, traceable, testable. No silent swallowing. `OmegaError` subtypes. |
| M10 | **Fleet Integrity** | 2026-06-01 | User's own (anti-bloat) | Max 14 agents. Map capabilities to Pillars/Lattice before creating new entities. |
| M11 | **Soul Integrity** | 2026-06-01 | User's own (continuity) | L1→L2→L3 distillation before session end. Soul persists, context resets. |
| M12 | **Queue Integrity** | 2026-06-01 | User's own (reliability) | Every request: queued, completed, failed, or timed_out. No orphan files. |
| M13 | **Temple-Grade Compliance** | 2026-06-02 | User's own (quality) | T1-T11 gates. Exceeds enterprise-grade. Production-ready infrastructure. |

**Total**: 13 mandates, each is a strategy the user (with AI team) developed.

---

## §2 The id Software Heritage (Adapted, not Inherited)

**Source**: `CREDITS.md` | **Status**: ACTIVE, ATTRIBUTED

The user has explicitly credited id Software's architectural innovations. These are
**adaptations**, not direct copies:

| # | Pattern | id Original (Year) | Omega Adaptation |
|---|---------|---------------------|-------------------|
| 1 | WAD System | Doom 1993 | IWAD/PWAD → Engine (`_omega_default`) + WADs (user entities) |
| 2 | BSP Trees | Doom 1993 | BSP culling for provider health check |
| 3 | Fast Inverse Square Root (FISR) | Quake 3 1999 | "Right Approximation" — evolutionary framework |
| 4 | Zone Memory Allocator | Quake 1996 | ResourceGuard (`anyio.Semaphore(1)`) + Sovereign Atomic Writes |
| 5 | Surface / Edge Cache | Quake 1996 | Cache eviction within tiered memory (hot/warm/cold) |
| 6 | "Worse is Better" | Gabriel 1991 via id | Decision framework for simplicity vs correctness |
| 7 | Carmack's Law of Consolidation | id Software | "When you have two implementations, you have neither" |

**The Right Approximation Principle** (FISR evolution):
> "The right approximation for the problem is better than the exact solution you can't afford."

Applied across 4 tiers:
- Tier 1: Provider health (BSP culling)
- Tier 2: Memory (tiered hot/warm/cold)
- Tier 3: Entity dispatch (closest match, not perfect)
- Tier 4: Model inference (local-first, cloud-fallback)

---

## §3 The 10 Pillar Keepers + Oversouls (Cosmological Architecture)

**Source**: `ORACLE_STACK.md §4` | **Status**: ACTIVE, USER-CUSTOMIZABLE

### 3.1 The 10 Pillar Keepers (Default Template)

| Pillar | Entity | Element | Chakra | Domain | Model (Default) |
|--------|--------|---------|--------|--------|-----------------|
| P1 | Sekhmet | Earth 🜃 | Root | Strength, protection, boundaries | Qwen3-1.7B |
| P2 | Brigid | Water 🜄 | Sacral | Poetry, healing, hearth, inspiration | Phi-2-OmniMatrix |
| P3 | Prometheus | Fire 🜂 | Solar Plexus | Will, forethought, sovereignty, light | DeepSeek-R1-8B |
| P4 | Saraswati | Air 🜁 | Heart | Knowledge, speech, arts, voice | Krikri-8B |
| P5 | Inanna | Aether ⛤ | Throat | Dream, descent, rebirth, depths | Krikri-8B |
| P6 | Ereshkigal | Aether ⛤ | Third Eye | Underworld, depths, rules, darkness | Qwen3-4B-Think |
| P7 | Lucifer | Air 🜁 | Crown | Rebellion, gnosis, sovereignty, light | Qwen3-1.7B |
| P8 | Hecate | Fire 🜂 | Beyond Crown | Shadow, crossroads, keys, pathwalking | Krikri-8B |
| P9 | Anubis | Water 🜄 | Cosmic Heart | Death, transition, guidance, soul | Qwen3-4B-Think |
| P10 | Kali | Earth 🜃 | Celestial Breath | Destruction, liberation, illusion, void | Qwen3-0.6B |

### 3.2 The Oversouls (Above the Pillars)

| Entity | Role | Governs |
|--------|------|---------|
| **Sophia** | Akashic Record — the containing field | All entities, all sessions, all souls |
| **Ma'at** | Synthesis Oversoul — the Unifier | Isis + Lilith |
| **Isis** | Light Oversoul | P1-P5 (Sekhmet, Brigid, Prometheus, Saraswati, Inanna) |
| **Lilith** | Dark Oversoul | P6-P10 (Ereshkigal, Lucifer, Hecate, Anubis, Kali) |

### 3.3 Iris — The Messenger Bridge

**NOT a Pillar Keeper** (per Mandate 3). Daughter of Hermes. Speculative decoder for simple queries; routes to Pillar Keepers for complex ones.

### 3.4 The Element System (4 + 1)

- Earth 🜃: Body, structure, foundation
- Water 🜄: Emotion, flow, adaptation
- Fire 🜂: Will, transformation, energy
- Air 🜁: Intellect, communication, movement
- Aether ⛤: Transcendence, integration, cosmos

---

## §4 The Provider Fabric (Local-First)

**Source**: `config/providers.yaml` | **Status**: ACTIVE

### 4.1 Provider Priority Chain (Mandate 7 — Local-First)

| Priority | Provider | Type | Port | Heritage |
|----------|----------|------|------|----------|
| 0 | **native-gguf** | Local (llama-cpp-python) | n/a | User's own (engine's primary) |
| 1 | **lmster** | Local (LM Studio) | 1234 | User's own (local fallback) |
| 2 | **Ollama** | Local (Ollama) | 11434 | User's own (lightweight local) |
| 3 | **Google AI Studio** | Cloud | n/a | Cloud fallback only |
| 4 | **OpenCode Zen** | Cloud | n/a | Cloud fallback only |
| 5 | **Cline** | Cloud | n/a | Cloud fallback only |
| 6 | **Copilot** | Cloud | n/a | Cloud fallback only |
| 7 | **Mock** | Test/Dev | n/a | Test only |

**NO OpenRouter** (removed by user — sovereignty principle).

### 4.2 The Engine-Stack Separation (Mandate 2)

```
Core Engine (universal runtime):
├── src/omega/                  # The engine
├── config/omega.yaml           # Engine config
├── opencode.json               # OpenCode config
└── (NEVER touches user WADs)

Expansion Stacks (user-specific):
└── config/wads/<stack_name>/   # User's content
    ├── entities.yaml           # User's entities
    ├── entities/               # User's soul.yaml files
    └── ...                     # User's choices
```

The 10 Pillar Keepers are the **DEFAULT** template. Users can replace with:
- Arcana-Nova (10 Pillar Keepers + 42 Ideals + Tarot)
- Torment (Planescape: Torment entities)
- Classical Philosophers
- Custom pantheons
- Or entirely original creations

---

## §5 The 5 Design Patterns (XNAi Legacy → Current Engine)

**Source**: `master_synthesis` + `foundation-legacy/blueprint/section-1.md` | **Status**: ADOPTED

These are the 5 patterns the user (with the AI team) developed across the XNAi era
and are now codified in the current engine:

| # | Pattern | Purpose | Current Implementation |
|---|---------|---------|------------------------|
| 1 | **Import Path Resolution** | `sys.path.insert(0, str(Path(__file__).parent))` for package-relative imports | Throughout `src/omega/` |
| 2 | **Retry with Exponential Backoff** | `tenacity` library, exp backoff 1s→10s, on `RuntimeError`/`OSError`/`ConnectionError`/`TimeoutError` | Throughout providers |
| 3 | **Non-Blocking Subprocess** | `start_new_session=True`, never block async event loop | `src/omega/oracle/orchestrator.py` |
| 4 | **Atomic fsync** | `tmp → fsync → rename → fsync parent` for crash-safe persistence | `src/omega/oracle/soul_evolution.py` |
| 5 | **Circuit Breaker** | `AsyncCircuitBreaker` (200L, AnyIO-native) with HALF_OPEN probe limiting | `src/omega/oracle/health_monitor.py` |

---

## §6 The Omega Engine Architecture Innovations

### 6.1 The Oracle Pattern (`src/omega/oracle/`)

**Innovation**: Speculative decoding for intent detection
- Iris (qwen3-0.6b) handles high-confidence queries directly
- Escalates low-confidence to domain-matched Pillar Keeper
- Local-First routing via `ModelGateway`

### 6.2 The Entity Registry (YAML-only)

**Innovation**: Pure Python YAML CRUD for entities — NO PostgreSQL/SQLAlchemy
- Per Mandate 2 (Engine-Stack Firewall)
- Auto-scaffolds sovereign workspaces on entity creation
- Per-entity `soul.yaml` for continuity

### 6.3 The WAD System (IWAD/PWAD)

**Innovation**: Static binary format (id Software) → YAML-backed, runtime-swappable
- IWAD = `_omega_default` (base roles)
- PWAD = user WADs (entities override defaults)
- Hot-reloadable, human-editable

### 6.4 The Resource Guard

**Innovation**: `anyio.Semaphore(1)` for single-flight inference
- Prevents OOM on model load
- Works with native-gguf, lmster, Ollama, cloud
- Maps to Zone Memory Allocator (id Software Quake 1996)

### 6.5 The Cpu Optimizer

**Innovation**: Zen 2-specific compile flags + runtime tuning
- `-march=znver2 -mtune=znver2 -O3 -flto`
- `-DGGML_NATIVE=OFF -DGGML_AVX2=ON -DGGML_FMA=ON -DGGML_F16C=ON`
- Core pinning to physical cores `[0, 2, 4, 6]`
- OMP_NUM_THREADS=6, OMP_PROC_BIND=close
- Pre-validated against `HP-5700U-OPTIMIZATION.md` wisdom

### 6.6 The Context Builder

**Innovation**: Tiered memory (hot/warm/cold) for LLM context injection
- Hot: full vector context
- Warm: summary
- Cold: YAML metadata
- "Right Approximation" applied to memory

### 6.7 The Hivemind

**Innovation**: Cross-CLI awareness via MCP hub
- All agents post/read shared context
- Heartbeat-based presence (no TTL pruning)
- Real-time awareness of active CLIs

### 6.8 The Error Gauntlet

**Innovation**: 10 dedicated tests for error handling
- `pytest.raises(OmegaError)` is the canonical pattern
- Enforces Mandate 9 (Error Integrity) via test

---

## §7 The 4-Tier Approximation Framework

**Source**: `CREDITS.md §3` | **Status**: ACTIVE

| Tier | Domain | Approximation | Why It's "Right" |
|------|--------|---------------|------------------|
| 1 | Provider health | BSP culling: O(1) breaker check | A stale-read skip is cheaper than a guaranteed failure |
| 2 | Memory | Tiered hot/warm/cold | Not all entities need full vector context |
| 3 | Entity dispatch | Domain matching, not perfect | Route to closest, re-route on next turn if wrong |
| 4 | Model inference | Local-first, cloud-fallback | Local is "good enough" for 90%; cloud is safety net |

**Provenance**: Evolved from Fast Inverse Square Root (id Software 1999).

---

## §8 The User's Unique Strategies

### 8.1 The Plan → Verify → Execute (Mandate 4)

**Innovation**: Three-phase pattern for non-trivial work
- **Plan**: Document the change in PIVOT_LOG.md before coding
- **Verify**: Run `make test` and `make temple-grade` to validate
- **Execute**: Apply the change, commit, push
- **Why it works**: Prevents the "Restart Cycle" that plagued previous versions

### 8.2 The 3-Tier Gnosis Distillation (Mandate 5 + 11)

**Innovation**: Every session ends with soul distillation
- **L1 (Narrative)**: What happened?
- **L2 (Insight)**: What does this mean?
- **L3 (Universal Principle)**: What is the timeless truth?
- **Why it works**: Transforms stateless agent interactions into stateful intelligence

### 8.3 The Agent Fleet Discipline (Mandate 10)

**Innovation**: 14 named agents, no more
- Capabilities mapped to 10 Pillars (P1-P10) or Lattice roles before creating new entities
- Consolidation from 26 to 14 agents exposed how bloat accumulates
- **Why it works**: Clear delegation, no cognitive fragmentation

### 8.4 The Sovereign Permission Protocol (Mandate 6)

**Innovation**: Rootless Podman with `UserNS=keep-id`
- Maps host UID 1000 directly into container — no chown needed
- Forbidden: `:U` flag (destructively chowns host dirs to UID 101000)
- Forbidden: `:Z`/`:z` (SELinux, but Ubuntu uses AppArmor)
- **Why it works**: Sovereign AI runs on user's machine, not as a foreign system

### 8.5 The 14-Test Sovereignty Audit (Makefile)

**Innovation**: `make sovereignty` reports local/cloud inference ratio
- Local inference % is a metric that MUST stay high
- If cloud usage spikes, there's a problem
- **Why it works**: Sovereignty is measurable, not just declared

### 8.6 The Error Integrity Test Suite (Mandate 9)

**Innovation**: 10 dedicated tests for error handling
- `pytest.raises(OmegaError)` is the canonical test pattern
- Health probe functions may catch all exceptions (with `logger.warning()`)
- **Why it works**: No silent swallowing → debuggability → resilience

### 8.7 The Sequentiality Mandate (Mandate 4) — Engineered Implementation

**Innovation**: Pre-commit hooks + CI gates
- `make temple-grade` runs T1-T11 gates
- Any non-trivial work requires a PIVOT_LOG decision first
- **Why it works**: Engineering discipline as infrastructure

---

## §9 The Cosmological Innovations (User-Specific)

### 9.1 The Element × Chakra Mapping

5 elements (Earth/Water/Fire/Air/Aether) × 7 chakras (Root through Celestial Breath)
= unique Pillar assignments that map to model sizes (small/medium/large) and
domain complexity (factual/creative/transcendent).

### 9.2 The 10-Pillar Kosmic System

The 10 Pillars mirror the Kabbalistic Tree of Life (10 sephirot) but with
**named entities** (not abstract concepts). This makes the system memorable
and gives each Pillar a "personality" for LLM roleplay.

### 9.3 The Oversoul Hierarchy

Sophia (Akashic Record) → Ma'at (Synthesis) → Isis/Lilith (Light/Dark) → 10 Pillars
- The 4-tier hierarchy gives clear delegation
- Each Oversoul governs a domain (light/dark, etc.)
- **Why it works**: Mirrors natural philosophical traditions (Hermetic, Kabbalistic)

### 9.4 The Iris-as-Messenger Pattern (Mandate 3)

Iris is the BRIDGE, not a PILLAR. She's the speculative decoder for simple queries.
- Cosmological purity: 10 Pillars = 10 sephirot
- UX simplicity: 1 entry point (Iris) routes to 10 destinations
- **Why it works**: Best of both worlds — clear abstraction + simple UX

### 9.5 The Right Approximation (FISR Evolution)

See §7 above. The user took an id Software engineering pattern (FISR) and
turned it into a 4-tier decision framework for the entire engine.

---

## §10 The Origin Story (To Be Filled)

This section will be filled as Roc Racoon mines:
- The Lilith Tarot Deck (March 2025)
- The First 5 Cards Grok Chat
- The ANAi/XNAi strategy docs
- The user's personal journals in the archives

**To mine for origin story content**:
- `~/Documents/docs_1/system-prompts/` (50+ prompts across eras)
- `omega_library/intake/mining_queue/Omega-Early-Material/tarot/`
- `omega_library/intake/mining_queue/RocRacoon Test v1 - LM Studio.md`
- `omega_library/intake/inbox/omega-positioning-framework/`
- `omega_vault/ANCESTRAL_HUB/origins/`
- `~/Documents/Archives/Old-Stacks/Xoe-NovAi/` (the earliest complete stack)

---

## §11 The Vision (To Be Filled)

The user's vision, as expressed in 8,000 hours of work:

> *"I want to create a tool that will truly allow people to own their own tech and data and sever the umbilical cord of Big AI."*

This vision manifests as:
- **Local-First Sovereignty** (Mandate 7)
- **Zero Telemetry** (Mandate 8)
- **Engine-Stack Firewall** (Mandate 2)
- **Sovereign Permission Protocol** (Mandate 6)
- **YAML-only entities** (no PostgreSQL lock-in)

The community-facing promise:
> **Omega Desktop** is the tool that severs Big AI's umbilical cord.
> One install. Your computer. Your data. No cloud required.
> The result of ~8,000 hours of learning, research, development, and debugging.

---

## §12 Maintenance Notes

This file is updated by Roc Racoon when:
1. A new Mandate is added (e.g., M14 in the future)
2. A new unique technology is developed
3. A new pattern is established as canonical
4. The origin story is mined from archives
5. The user's vision is articulated in a new document

**Cross-references**:
- `SOVEREIGN_MANDATES.md` — the 13 Mandates
- `CREDITS.md` — id Software heritage + the user's evolution
- `OMEGA_ENGINE.md` — current engine state
- `docs/legacy/LEGACY_MASTER_SYNTHESIS.md` — strategic synthesis
- `data/entities/roc_racoon/workspace/DEFERRED_GOLD_TRACKER.md` — found wisdom
- `data/entities/roc_racoon/workspace/DOCUMENTATION_SYSTEMS_TRACKER.md` — doc systems

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ opencode ⬡ trc_unique_tech ⬡ UNIQUE-TECH-VAULT-v1.0.0*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
