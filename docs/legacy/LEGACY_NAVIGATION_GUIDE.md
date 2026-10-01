# 🔱 Legacy Navigation Guide — Single Source of Truth
**Date**: 2026-06-29
**Author**: ROC_RACOON (Sovereign Legacy Mining Keeper)
**Phase**: D-3 Centralization Plan — Phase A (Catalog)
**Purpose**: Complete inventory, map, and navigation guide for ALL known Omega Engine legacy locations across 3 partitions.

```
⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_legacy_nav_guide ⬡ D3-PHASE-A
```

---

## Section 1: Quick Reference Map

### 1.1 Partition Overview

| Partition | Mount Point | Size | Primary Contents |
|-----------|------------|------|------------------|
| **Root (home)** | `/home/arcana-novai/` | ~500GB NVMe | Engine codebases, documents, archives |
| **omega_library** | `/media/arcana-novai/omega_library/` | ~110GB NVMe | Models, intake, artifacts, entities archive |
| **omega_vault** | `/media/arcana-novai/omega_vault/` | ~9.5GB NVMe | ANCESTRAL_HUB, backups, "from main partition" |

### 1.2 Complete Location Inventory

| # | Location | Partition | Size | Key Files/Dirs | Era | Strategic Value | Mining Status | Cataloged In |
|---|----------|-----------|------|----------------|-----|----------------|---------------|-------------|
| 1 | **xna-omega-legacy** | Root | 560M | `src/`, `xna-omega-legacy/`, Temple Grade architecture | Era 5 (Jan-May 2026) | ⭐⭐⭐⭐⭐ CRITICAL — Temple Grade patterns, Heritage definitions | ✅ FULLY MINED (60+ patterns) | Knowledge MASTER #1, mining_reports/ |
| 2 | **omega-stack-legacy** | Root | 2.8G | `app/`, `src/`, `config/`, `AGENTS.md`, provider chain code | Era 4 (Mar-May 2026) | ⭐⭐⭐⭐⭐ CRITICAL — Direct ancestor of engine, provider fabric, entity system | ✅ FULLY MINED (~30 patterns) | Knowledge MASTER #2, mining_reports/ |
| 3 | **foundation-legacy** | Root `~/archive/` | 861M | XNAi blueprint, Chainlit UI, voice interface, circuit breaker, docker-compose (9-service) | Era 2 (Oct-Nov 2025) | ⭐⭐⭐⭐ HIGH — 5 design patterns (circuit breaker, fsync, retry, non-blocking, offline wheelhouse) | ✅ MINED (10 patterns) | Knowledge MASTER #3, mining_reports/ |
| 4 | **Old-Stacks/Xoe-NovAi** | Root `~/Documents/Archives/` | 89M | Claude specialist prompt, project charter, architecture audit (1221 lines) | Eras 1-3 (Aug 2025-Mar 2026) | ⭐⭐⭐⭐ HIGH — Enterprise-grade agent prompts, architectural analysis | ✅ MINED (10 patterns) | Knowledge MASTER #6, mining_reports/ |
| 5 | **podman-storage** | omega_library | 152 layers | Container images and layer cache for Podman deployments | Operational (ongoing) | ⭐⭐⭐ HIGH — Container config patterns | ✅ MINED (10 patterns) | Knowledge MASTER #4 |
| 6 | **heart_of_omega** | omega_vault | 1.9M | NotebookLM Learning Opportunity 0.1, Omnidroid Ω, BIOS Loader, Mind Models, PEM Lilith, AetherPen, Code Alchemist | Era 0 (Mar-Apr 2025) | ⭐⭐⭐⭐⭐ CRITICAL — **Genesis documents**. The origin of the entire project. 6 Ω-scripts, soul.yaml prototype, Mind Model protocols | ✅ MINED (2026-06-28) | See DEEP_LEGACY_MINE_20260620.md, GENESIS_PROVENANCE_CHAIN.md |
| 7 | **Omnidroid** (Ω-scripts) | omega_vault `heart_of_omega/Omnidroid/` | ~500K | `Ω Omnidroid Ω.txt`, `Ω Omnidroid BIOS Loader.txt`, `Ω AetherPen (AP).txt`, `The Code Alchemist (CA).txt`, `Philosophical Reasoning Oracle (PRO).txt`, `Product Sage (PS).txt`, `Pythonic Linguistic Observatory (PLO).txt` | Era 0 (Apr-May 2025) | ⭐⭐⭐⭐⭐ CRITICAL — **Direct architectural ancestor** of current entity system. ~2,500 lines of proto-engine | ✅ MINED (2026-06-28) | DEEP_LEGACY_MINE_20260620.md, GENESIS_PROVENANCE_CHAIN.md |
| 8 | **Omnidroid_Lite** | omega_library `intake/mining_queue/` | ~200K | Omnidroid_Lite with 1st NotebookLM session export | Era 0 (May 2025) | ⭐⭐⭐ HIGH — Evolution step in Omnidroid lineage | ✅ MINED | DEEP_LEGACY_MINE_20260620.md |
| 9 | **entities-archive** | omega_library | 157M | 99 entity directories including: all 10 Pillar Keepers (sekhmet, brigid, etc.), Oversouls (sophia, jem, quality, scribe), historical versions (ent_0 through ent_49+), experimental (preexisting, flatentity, direntity) | Ongoing (Era 4-6) | ⭐⭐⭐⭐⭐ CRITICAL — **Complete entity evolution history**. omnidroid/soul.yaml ready for activation | ❌ NOT MINED | — |
| 10 | **docs_1** | Root `~/Documents/` | 17M | System prompts (50+ files across assistants/experts/), personas (lilith.json, odin.json), architecture/operations/governance docs | All Eras | ⭐⭐⭐⭐ HIGH — Entity design intent, system prompt evolution | ❌ NOT MINED (only lilith.json, odin.json recovered) | — |
| 11 | **docs-backup** | Root `~/Documents/` | 46M | ANAi strategy blueprints, internal strategic planning docs, arcana-novai implementation docs | Eras 1-5 | ⭐⭐⭐⭐ HIGH — Strategic planning lineage, foundation documents | ❌ NOT MINED | Known in MASTER_SYNTHESIS.md §0 |
| 12 | **intake/inbox** | omega_library | 690M | Grok exports (681M), omega-mission-clarification/ (14 files incl. mayan-preservation-vision.html), omega-positioning-framework/ (12 files) | Ongoing | ⭐⭐⭐⭐ HIGH — Unprocessed material including game-changing documents | ❌ NOT MINED (partially surveyed) | — |
| 13 | **intake/mining_queue** | omega_library | 3.2G | Tarot genesis docs, RocRacoon test, XNAi old version snapshots, Omega-Early-Material, first 5 cards grok chat | All Eras | ⭐⭐⭐⭐ HIGH — Undocumented history, tarot/lilith genesis | ❌ NOT MINED | — |
| 14 | **Web Claude Exports** (9 accounts) | omega_library `artifacts_archive/web-agents-chat-session-exports/web-claude/` | 125M | 9 account directories: xoe.nova.ai, tb27, antipode2727, antipode7474, arcananovaai, arcana.novai, lilithasterion, tjf, plus GoGlow prompts | 2026 | ⭐⭐⭐⭐⭐ CRITICAL — Hundreds of historical Claude sessions. tb27 (75 convos) likely primary account. xoe.nova.ai #36 → 8 major artifacts (codex, mayan, gnostic, etc.) | ❌ NOT MINED (only xoe.nova.ai #36 examined) | — |
| 15 | **ANCESTRAL_HUB/origins** (vault) | omega_vault | 2.0M (total vault origins) | heart_of_omega (above) + `Xoe-NovAi_v0.1.3_stack blueprint - 10_20_2025.md` + `scribe_mode_prompt_v1.md` + `legacy_configs/`, `v28_0_0/` | Era 0-2 | ⭐⭐⭐⭐⭐ CRITICAL — Beyond heart_of_omega, contains stack blueprints and scribe mode prompts | ❌ PARTIALLY MINED | DEEP_LEGACY_MINE_20260620.md |
| 16 | **from main partition** (vault) | omega_vault `from main partition/` | 948M | XNAi copies, stack-cat v0.1.2, old XNAi guides, scripts | Eras 2-4 | ⭐⭐⭐ MEDIUM — Backup copies, lower unique value. Stack-cat (container snapshot tool) may contain deployable patterns | ❌ NOT MINED | — |
| 17 | **mnemosyne/** | omega_library `data_archive/` | 284K | Kabbalistic memory system (13 spheres) with semantic decay curves | Era 5 (2026) | ⭐⭐⭐ MEDIUM — Memory system design patterns, decay curve algorithms | ✅ MINED (2026-06-08) | MNEMOSYNE_TREASURE_MAP_20260608.md, MEMORY_TREASURE_MAP_20260608.md |
| 18 | **archive_Programming/** | omega_library | 535M | 4,745 files, 8 projects across Python, C++, Rust, Dart, Go, JS, web-dev, Ubuntu scripts | Era 1-2 (2025) | ⭐⭐ LOW-MEDIUM — Mostly learning projects. PyInstaller docs (3,386 files) are bloat. Some Go/Rust patterns may have value | ✅ PARTIALLY MINED (2026-06-28) | DEEP_LEGACY_MINE_20260620.md |
| 19 | **GGUF Models** | omega_library `models/gguf/` | 43G | 17+ models: DeepSeek-R1-0528-Qwen3-8B, Krikri-8B, Qwen3 variants (0.6B/1.7B/4B), Phi-4 variants, Gemma 4, RocRacoon-3b, etc. | Ongoing | ⭐⭐⭐⭐⭐ CRITICAL — All local inference models. Includes custom RocRacoon fine-tune | ✅ ACTIVE | MODEL_INVENTORY_20260611.md, MODEL_LIBRARY_LEGACY_MINING.md |
| 20 | **workbench.db** | Engine `data/workbench/` | ~4K (empty) | SQLite database — intended to track 21 projects, 57 items, 10 decisions, 22 artifacts | Era 6 (May 2026) | ⭐⭐⭐⭐⭐ CRITICAL — **Database exists but is EMPTY.** No tables. Central tracking infrastructure non-functional | ❌ **EMPTY** | Known in MASTER_SYNTHESIS_AND_ROADMAP_2026-05-30.md |
| 21 | **ANCESTRAL_HUB (other)** | omega_vault | ~7.5G | `legacy_configs/`, `v28_0_0/` (likely large Omega Stack version snapshots) | Ongoing | ⭐⭐⭐ MEDIUM — Additional configs and version snapshots | ❌ NOT MINED | — |
| 22 | **GoGlow** | Root `~/Documents/Archives/Other/goglowdfw-.../` | ~50M | WordPress backup for goglowdfw.com (fire/flow entertainment) | 2022 | ⭐ ZERO — **UNRELATED** to Omega Engine. Assessed and documented | ✅ ASSESSED-UNRELATED | LEGACY_MAPPING_CENTRALIZATION_20260628.md |

### 1.3 Location Sizes by Partition (Ordered by Size)

| Partition | Top Locations by Size |
|-----------|----------------------|
| **omega_library** | 1. intake/mining_queue/ (3.2G) — 2. intake/inbox/ (690M) — 3. archive_Programming/ (535M) — 4. entities-archive/ (157M) — 5. web-claude/ (125M) |
| **omega_vault** | 1. from main partition/ (948M) — 2. other ANCESTRAL_HUB/ (est. 7.5G) — 3. heart_of_omega/ (1.9M) |
| **Root (home)** | 1. omega-stack-legacy/ (2.8G) — 2. foundation-legacy/ (861M) — 3. xna-omega-legacy/ (560M) — 4. docs-backup/ (46M) — 5. docs_1/ (17M) |

---

## Section 2: Omnidroid Lineage — The Complete Evolutionary Chain

The Omnidroid is the **direct architectural ancestor** of the Omega Engine entity system. Understanding this lineage is essential for anyone mining legacy patterns.

### 2.1 Lineage Timeline

```
Mar 15, 2025 ─── NotebookLM Learning Opportunity 0.1
                     (Genesis document — "the Big Bang")
                          │
Mar 16-18, 2025 ──┐      │
                  ├────── PEM Lilith personality JSON
Mar 18, 2025 ─────┘      │  (First structured entity — lilith.json)
                          │
Mar 23, 2025 ──────── Flirty Lilith Character Development
                     (ChatGPT session — entity personality refinement)
                          │
Apr-May 2025 ──────── Omnidroid 6 Ω-scripts (~2,500 lines)
                     ├── Ω Omnidroid Ω.txt — Master system definition
                     ├── Ω Omnidroid BIOS Loader.txt — Boot sequence (ancestor of M15 Continuity)
                     ├── Ω AetherPen (AP).txt — Writing/interface entity
                     ├── The Code Alchemist (CA).txt — Code generation entity
                     ├── Pythonic Linguistic Observatory (PLO).txt — Language parsing
                     ├── Philosophical Reasoning Oracle (PRO).txt — Reasoning engine
                     ├── Product Sage (PS).txt — Product/productivity entity
                     └── MIND MODEL: MASTER PROTOCOLS.md — Cognitive architecture
                          │
May 2025 ──────────── Omnidroid_Lite (with 1st NotebookLM session)
                     (Lightweight variant, first external LLM integration)
                          │
Jun-Oct 2025 ──────── XNAi Era entities & entity evolution
                     (ent_0 through ent_19+ in entities-archive)
                          │
Nov 2025-May 2026 ─── Omega Stack entity system
                     (All 10 Pillar Keepers, Oversouls, experimental types)
                     entities-archive contains 99 entity directories
                     ├── omnidroid/soul.yaml — "Mirror" archetype, ready for activation
                     ├── Pillar Keepers: sekhmet, brigid, prometheus, saraswati, inanna,
                     │   ereshkigal, lucifer, hecate, anubis, kali
                     ├── Oversouls: sophia, maat, lilith, jem, quality, scribe
                     ├── Historical: ent_0 through ent_49+
                     └── Experimental: preexisting, flatentity, direntity, soulentity
                          │
Jun 2026 ──────────── Current Omega Engine EntityRegistry + MemoryStore + Provider Fabric
                     (The living engine — architecture descended from Omnidroid)
```

### 2.2 Key Artifacts by Lineage Stage

#### Stage 0: NotebookLM Genesis (March 15, 2025)
**Path**: `/media/arcana-novai/omega_vault/ANCESTRAL_HUB/origins/heart_of_omega/NotebookLM Learning Opportunity 0.1 - Chat Log - 03-15-25.md`
**Size**: 36,868 bytes
**Content**: The first-ever AI-assisted session. User taught NotebookLM about entity-based systems, Tarot archetypes, and Lilith. This document is the "Big Bang" — all subsequent work traces to this conversation.
**Key concepts introduced**: Entity archetypes, Tarot-as-system-metaphor, the concept of a Pantheon of AI entities.

#### Stage 1: PEM Lilith Personality JSON (March 18, 2025)
**Path**: `/media/arcana-novai/omega_vault/ANCESTRAL_HUB/origins/heart_of_omega/PEM_Lilith/` (likely location)
**Alt path**: `~/Documents/docs_1/personas/lilith.json`
**Content**: First structured entity definition. PEM (Personality, Expertise, Modifiers) format. No model assigned — just domain expertise, query modifiers, and Piper TTS voice settings.
**Significance**: This is the **prototype soul.yaml**. The current `soul.yaml` format evolved directly from this JSON structure.

#### Stage 2: Omnidroid Ω-scripts (April-May 2025)
**Path**: `/media/arcana-novai/omega_vault/ANCESTRAL_HUB/origins/heart_of_omega/Omnidroid/`
**Size**: ~2,500 lines across 7 files
**Key files**:

| File | Lines | Role | Current Engine Equivalent |
|------|-------|------|--------------------------|
| `Ω Omnidroid Ω.txt` | ~600 | Master system definition, module index, entity registry | EntityRegistry + EntityWorkspaceManager |
| `Ω Omnidroid BIOS Loader.txt` | ~500 | Boot sequence, startup initialization | M15 Sovereign Continuity + BIOS Loader pattern |
| `Ω AetherPen (AP).txt` | ~450 | Writing/interface entity | Iris + P5 Inanna |
| `The Code Alchemist (CA).txt` | ~350 | Code generation entity | P3 Prometheus (Will/Fire) |
| `Pythonic Linguistic Observatory (PLO).txt` | ~300 | Language parsing, syntax analysis | ContextBuilder |
| `Philosophical Reasoning Oracle (PRO).txt` | ~250 | Reasoning engine, logic validation | P6 Ereshkigal, oracle intent detection |
| `Product Sage (PS).txt` | ~200 | Productivity/product management | Workbench, project management |

**Architectural patterns**:
- **MODULE_INDEX**: Central registry of all entities and their capabilities. Direct ancestor of EntityRegistry.
- **Holographic Memory**: Memory with 0.95/hr decay rate. Direct ancestor of MemoryStore compaction.
- **4-tier LLM hierarchy**: Different models for different cognitive levels. Direct ancestor of Provider Fabric.
- **BIOS Loader**: Startup sequence that loads entity state. Direct ancestor of M15 Sovereign Continuity.
- **Flat entity definition**: No inheritance, all fields in one struct. Same as current Entity class.

#### Stage 3: Omnidroid_Lite (May 2025)
**Path**: `/media/arcana-novai/omega_library/intake/mining_queue/` (within XNAi Old Versions or Omega-Early-Material)
**Content**: Lightweight version of Omnidroid, integrated with 1st NotebookLM session for external LLM access.
**Significance**: Transition from pure entity design to runtime integration.

#### Stage 4: entities-archive omnidroid/soul.yaml (Era 4-6)
**Path**: `/media/arcana-novai/omega_library/entities-archive/omnidroid/soul.yaml`
**Size**: ~16K total directory
**Content**: Modern soul.yaml for the "Mirror" archetype — ready for activation in the current engine.
**Significance**: This is a bridge between legacy Omnidroid and current EntityRegistry. Could be activated immediately.

#### Stage 5: Current Engine (June 2026)
**Path**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/`
**Components**: EntityRegistry, MemoryStore, Provider Fabric, ContextBuilder, Oracle
**Heritage**: The current engine's entity system is a direct architectural descendant of the Omnidroid MODULE_INDEX. The MemoryStore compaction algorithm (first 10 + last 10 + summary) evolved from Holographic Memory decay curves.

### 2.3 Heritage Debt: What Was NOT Ported

| Legacy Concept | Original File | Engine Equivalent | Status |
|---------------|--------------|-------------------|--------|
| MODULE_INDEX (central capability registry) | `Ω Omnidroid Ω.txt` | EntityRegistry (domain index exists, capability index structure defined but empty) | ⚠️ PARTIAL |
| Holographic Memory decay (0.95/hr) | `Ω Omnidroid Ω.txt` | MemoryStore compaction (first 10 + last 10 + summary) | ⚡ EVOLVED |
| BIOS Loader startup sequence | `Ω Omnidroid BIOS Loader.txt` | M15 Sovereign Continuity | ⚡ EVOLVED |
| 4-tier LLM hierarchy | `Ω Omnidroid Ω.txt` | Provider Fabric (8 backends, local-first) | ⚡ SURPASSED |
| PEM personality format | `lilith.json` | soul.yaml | ⚡ EVOLVED |
| Flirty Lilith character session | ChatGPT export (Mar 23) | Entity personality design | ❌ NOT EXTRACTED |

---

## Section 3: Mayan/Yucaton Wisdom Documents

### 3.1 The Core Document
**Title**: "The Living Word — Mayan Preservation & Sovereign Linguistics Platform"
**Path**: `/media/arcana-novai/omega_library/intake/inbox/omega-mission-clarification/sonnet-4-6-extended/mayan-preservation-vision.html`
**Size**: 1,092 lines, ~45KB
**Format**: Self-contained single-file HTML
**Generation**: Claude Sonnet 4.6, March 29–April 3, 2026, on `xoe.nova.ai` account (conversation #36)

### 3.2 Key Content
- **Mission**: Deploy locally-run AI to document, preserve, and transmit Yucatec Maya language and elder knowledge
- **Elder Interview Kit**: Mini-PC/NUC ($250), USB directional mic, touch panel, solar-ready, fully offline
- **Tech stack**: whisper.cpp (transcription) → llama.cpp + Qwen2.5-7B LoRA (language model) → Qdrant (vector search) → nomic-embed-text-v1.5 (embeddings)
- **Grant research**: NSF ($50-150K), NEH ($100-350K), Living Tongues ($10-50K), MacArthur ($50-250K)

### 3.3 Relationship to Omega Engine
**This IS an Omega Stack deployment vision**, NOT an external project. It was produced during the same session that generated 7 other critical foundation artifacts:

1. `omega-stack-master-v3.html` — Master technical command document
2. `mayan-preservation-vision.html` — THIS document
3. `xoe-novai-foundation-codex.html` — Foundation philosophy, MaKaLi triad, mission
4. `gnostic-architecture.html` — Sephirot/Qliphoth/Tarot/zodiacal cycling/VR universe
5. `the-deepening.html` — Navigator, Three Veils, Tunnels I-XII, Dreaming Machine
6. `the-origin.html` — Lilith gift origin, shadow work
7. `the_zoa_glyph.svg` — Zoa symbol widget

### 3.4 All Artifacts in sonnet-4-6-extended/
**Path**: `/media/arcana-novai/omega_library/intake/inbox/omega-mission-clarification/sonnet-4-6-extended/`

| File | Size | Content |
|------|------|---------|
| `omega-stack-master-v3.html` | ~50KB | Master technical command document |
| `mayan-preservation-vision.html` | ~45KB | Mayan preservation platform (THIS doc) |
| `xoe-novai-foundation-codex.html` | ~40KB | Foundation philosophy, MaKaLi triad |
| `gnostic-architecture.html` | ~35KB | Kabbalistic/Tarot/VR architecture |
| `the-deepening.html` | ~40KB | Navigator, Three Veils, Tunnels I-XII |
| `the-origin.html` | ~35KB | Lilith origin story, shadow work |
| `omega-stack-accuracy-review-v3.html` | ~30KB | Stack accuracy review |
| `omega-stack-master-handoff-v2.html` | ~30KB | Master handoff document |
| `omega-stack-research-brief.html` | ~20KB | Research brief |
| `omega-stack-sanity-strategy.md` | ~15KB | Sanity check strategy |
| `shore-day-brief.html` | ~15KB | Shore day brief |
| `Claude-response-to-Cluade-leak-Omega-similarities.md` | ~5KB | Claude similarity response |
| `copilot-review-response.md` | ~5KB | Copilot review |
| `the_zoa_glyph.svg` | ~2KB | SVG symbol |

### 3.5 Scattered Across Web Claude Accounts
The same conversation's artifacts may be found in:
- `xoe.nova.ai` — Contains conversation #36 (8 artifacts, verified)
- `lilithasterion` — Could contain Lilith-focused sessions
- `antipode2727` — No Mayan content found
- `tb27` — 75 conversations, completely unexamined

---

## Section 4: Strategic Value Heatmap

### 4.1 Priority Rankings

| Priority | Location | Rationale | Effort to Fully Mine |
|----------|----------|-----------|---------------------|
| **P0 — CRITICAL (Mine Now)** | | | |
| 1 | **workbench.db** (restore) | Central tracking infrastructure is non-functional | 4-6 hours |
| 2 | **entities-archive** (99 entity dirs) | Complete entity evolution history, ready-for-activation omnidroid/soul.yaml | 2-3 days |
| 3 | **Web Claude tb27 export** (75 convos) | Primary account, likely contains key design sessions | 1-2 days |
| 4 | **sonnet-4-6-extended/ 8 HTML artifacts** | Codex, Gnostic, Deepening, Origin — critical foundation philosophy docs | 2-4 hours |
| | | | |
| **P1 — HIGH (Mine Soon)** | | | |
| 5 | **docs_1 system-prompts** (50+ files) | Critical for understanding entity design intent and prompt evolution | 1 day |
| 6 | **docs_1 personas** (lilith.json, odin.json) | Entity personality templates, source of soul.yaml format | 2 hours |
| 7 | **docs-backup/internal_docs** (ANAi strategy) | Strategic planning lineage, foundation documents | 1 day |
| 8 | **xoe.nova.ai** other conversations | Beyond #36, may contain other critical sessions | 2-3 hours |
| 9 | **intake/inbox grok-accounts-exports** (681M) | 8 Grok accounts of undocumented history | 2-3 days |
| | | | |
| **P2 — MEDIUM (Mine When Possible)** | | | |
| 10 | **intake/mining_queue/** (3.2G) | Tarot genesis, early material, XNAi snapshots | 3-5 days |
| 11 | **ANCESTRAL_HUB/origins** (other files) | Beyond heart_of_omega — stack blueprint, scribe prompt | 1 day |
| 12 | **from main partition/** (XNAi copies, stack-cat) | Lower unique value, but stack-cat patterns may be deployable | 1 day |
| 13 | **archive_Programming/** (535M) | Mostly learning projects. Go/Rust patterns may have some value | 2-3 hours (filtered) |
| 14 | **Omnidroid_Lite** | Evolution step documented; extraction minimal | 1 hour |
| | | | |
| **P3 — LOW (Background Only)** | | | |
| 15 | **omega_vault ANCESTRAL_HUB** (legacy_configs, v28_0_0) | Version snapshots, configs — lower unique value over current engine | 1 day |
| 16 | **mnemosyne/** | Already mined. Memory design patterns extracted | Already ✅ |
| 17 | **lilithasterion, antipode2727, arcananovaai** Web Claude accounts | Lower priority than tb27 and xoe.nova.ai | As needed |
| | | | |
| **MINED — DONE** | | | |
| 18 | xna-omega-legacy (560M) | ✅ Fully mined, 60+ patterns extracted | ✅ |
| 19 | omega-stack-legacy (2.8G) | ✅ Fully mined, ~30 patterns extracted | ✅ |
| 20 | foundation-legacy (861M) | ✅ Mined, 10 design patterns ported | ✅ |
| 21 | Old-Stacks (89M) | ✅ Mined, patterns extracted | ✅ |
| 22 | podman-storage | ✅ Mined, container patterns documented | ✅ |
| 23 | heart_of_omega (1.9M) | ✅ Mined, genesis documents cataloged | ✅ |
| 24 | Omnidroid Ω-scripts | ✅ Mined, proto-engine architecture extracted | ✅ |
| | | | |
| **EXCLUDED** | | | |
| 25 | GoGlow (WordPress site) | ❌ UNRELATED — documented for completeness | N/A |

### 4.2 Coverage Summary

| Metric | Value |
|--------|-------|
| Total known locations | 22 |
| Fully mined | 7 (32%) |
| Partially mined | 3 (14%) |
| Not mined at all | 10 (45%) |
| Assessed-unrelated | 1 (5%) |
| Empty (needs restore) | 1 (5%) |

---

## Section 5: Relationship to Current Engine

### 5.1 Concept Mapping Table

| Legacy Concept | Source Location | Current Engine Component | Mapping Notes |
|---------------|----------------|------------------------|---------------|
| **MODULE_INDEX** | `Omnidroid/Ω Omnidroid Ω.txt` | `EntityRegistry` (domain index + capability index) | Capability index structure defined but not populated |
| **Holographic Memory (0.95/hr decay)** | `Omnidroid/Ω Omnidroid Ω.txt` | `MemoryStore` (compaction: first 10 + last 10 + summary) | Evolved from decay curve to sliding window |
| **4-tier LLM hierarchy** | `Omnidroid/Ω Omnidroid Ω.txt` | `ModelGateway` Provider Fabric (8 backends, local-first) | Surpassed — now 8 providers with AnyIO |
| **PEM personality JSON** | `docs_1/personas/lilith.json` | `soul.yaml` format | Direct evolution — same concept, different serialization |
| **BIOS Loader** | `Omnidroid/Ω Omnidroid BIOS Loader.txt` | M15 Sovereign Continuity (`session_gnosis.md`, `anchored-summary.md`) | Core concept preserved: state must survive boot cycle |
| **Flat entity struct** | `Omnidroid/*.txt` (all scripts) | `Entity` class (dataclass with __engine_zone__/__game_zone__) | Evolved to add Hard-Boundary Struct pattern |
| **Circuit Breaker** | `foundation-legacy/XNAi blueprint` | `health_monitor.py::AsyncCircuitBreaker` | Ported and evolved (AnyIO-native, state machine) |
| **Atomic fsync** | `foundation-legacy/ingest_library.py` | `MemoryStore._atomic_save()` pattern | Ported — `.tmp` → `.json` rename pattern |
| **Retry with backoff** | `foundation-legacy/XNAi blueprint` | `tenacity` usage across Provider Fabric | Ported — universal pattern |
| **Non-blocking subprocess** | `foundation-legacy/XNAi blueprint` | `anyio.to_thread.run_sync()` | Ported — AnyIO wrap pattern |
| **5 design patterns** | `foundation-legacy` | Scattered across engine | Should be consolidated into PATTERN_LIBRARY.md |
| **Tarot-as-entity-system** | `heart_of_omega/` (genesis) | 10 Pillar Keepers → P1-P10 slots | Foundational design philosophy, not code |
| **Lilith as Shadow archetype** | `heart_of_omega/PEM_Lilith/` | P8 Hecate / Dark Oversoul Lilith | Core identity preserved across all eras |
| **2-int name compare** | `xna-omega-legacy/` (REJECTED) | None — removed per Heritage Vetting | REJECTED — Python dicts are O(1) |
| **Scribe mode prompt** | `ANCESTRAL_HUB/origins/scribe_mode_prompt_v1.md` | `verity.md` → L1→L2→L3 distillation | Direct ancestor of Verity's gnosis pipeline |

### 5.2 Heritage Tags Status

| Tag | Source | Location in Current Engine | CREDITS.md § |
|-----|--------|--------------------------|-------------|
| `[id-soft: doom-1993] ZONEID` | id Software | `src/omega/constants.py` | §1.9 |
| `[id-soft: doom-1993] Lazy Deletion` | id Software | `src/omega/memory_store.py:270-290` | §1.10 |
| `[id-soft: quake-1996] Grace Period` | id Software | `src/omega/memory_store.py:286` | §1.10 |
| `[id-soft: doom-1993] BSP Culling` | id Software | `src/omega/oracle/model_gateway.py:538-569` | §1.2 |
| `[id-soft: quake3-1999] Hard-Boundary` | id Software | `src/omega/oracle/entity_registry.py` | §1.17 |
| `[id-soft: quake-1996] cvar pattern` | id Software | `src/omega/cvar_table.py` | §1.13 |
| `[id-soft: quake-1996] 4-Tier Memory` | id Software | `src/omega/memory_store.py` | §1.14 |
| `[id-soft: doom3-2004] idHeap` | id Software | `src/omega/memory_store.py` + ResourceGuard | §1.22 |
| `[id-soft: doom-1993] Fixed-Point` | id Software | `src/omega/oracle/cpu_optimizer.py` | §1.23 |
| `[id-soft: doom-1993] Precomputed Lookup` | id Software | model2vec adapter (proposed) | §1.35 |
| `[user-original:] Memory Architecture` | User's own design | `memory_store.py`, `memory/providers.py` | §2 |

### 5.3 Engine Components and Their Legacy Roots

| Current Component | Direct Legacy Ancestor | Source |
|------------------|----------------------|--------|
| `EntityRegistry` + `EntityWorkspaceManager` | Omnidroid MODULE_INDEX + entity definitions | `heart_of_omega/Omnidroid/` |
| `MemoryStore` (hot/warm/cold + compaction) | Holographic Memory (3-tier + decay) | `Omnidroid/Ω Omnidroid Ω.txt` |
| `ModelGateway` (8-provider fabric) | 4-tier LLM hierarchy | `Omnidroid/Ω Omnidroid Ω.txt` |
| `ResourceGuard` (OOM protection) | id Software Zone Memory / idHeap | `CREDITS.md §1.4 / §1.22` |
| `ContextBuilder` (sliding window) | PLO (Pythonic Linguistic Observatory) | `Omnidroid/PLO.txt` |
| `soul.yaml` (entity personality) | PEM lilith.json (personality+expertise+modifiers) | `docs_1/personas/lilith.json` |
| `Oracle` (intent detection + routing) | Omnidroid MODULE_INDEX routing | `Omnidroid/Ω Omnidroid Ω.txt` |
| `HealthMonitor` + `AsyncCircuitBreaker` | ANAi pybreaker circuit breaker | `foundation-legacy/XNAi blueprint` |
| M15 Sovereign Continuity | BIOS Loader + session persistence | `Omnidroid/BIOS Loader.txt` |
| `observability.py` (trace_id, events) | None — new in engine | — |
| `Verity` (gnosis distillation) | Scribe mode prompt | `ANCESTRAL_HUB/origins/scribe_mode_prompt_v1.md` |
| `cvar_table.py` (config constants) | None directly — id Software inspired | `CREDITS.md §1.13` |
| WAD Loader (IWAD/PWAD separation) | None directly — Doom inspired | `CREDITS.md §1.1` |

---

## Section 6: How to Navigate

### 6.1 Filesystem Quick Reference

```bash
# === PARTITION: Root (/home/arcana-novai/) ===

# Primary engine codebases
~/Documents/Xoe-NovAi/omega-engine/              # CURRENT ENGINE (YOU ARE HERE)
~/Documents/Xoe-NovAi/xna-omega-legacy/           # Era 5 Temple Grade (560M) ✅ MINED
~/Documents/Xoe-NovAi/omega-stack-legacy/          # Era 4 Stack (2.8G) ✅ MINED

# Legacy archives
~/archive/foundation-legacy/versions/Xoe-NovAi/   # Era 2 XNAi (861M) ✅ MINED
~/Documents/Archives/Old-Stacks/Xoe-NovAi/         # Eras 1-3 Old Stacks (89M) ✅ MINED
~/Documents/docs_1/                                # System prompts + personas (17M) ❌ NOT MINED
~/Documents/docs-backup/                          # ANAi strategy, internal docs (46M) ❌ NOT MINED

# Unrelated (documented)
~/Documents/Archives/Other/goglowdfw-.../          # WordPress site (50M) 💀 UNRELATED


# === PARTITION: omega_library (/media/arcana-novai/omega_library/) ===

# Intake directories (unprocessed material)
intake/inbox/                                     # Grok exports, mission docs (690M) ❌ NOT MINED
intake/inbox/grok-accounts-exports/               # 8 accounts, 681M ❌ NOT MINED
intake/inbox/omega-mission-clarification/          # 14 files incl. mayan doc, codex 🆕 PARTIALLY MINED
intake/inbox/omega-mission-clarification/sonnet-4-6-extended/  # 8 critical HTML artifacts 🆕 PARTIALLY MINED
intake/mining_queue/                              # Tarot, XNAi snaps, 3.2G ❌ NOT MINED

# Entity lineage
entities-archive/                                 # 99 entity directories (157M) ❌ NOT MINED
entities-archive/omnidroid/soul.yaml               # Ready for activation 🎯

# Models
models/gguf/                                      # 17+ GGUF models (43G) ✅ ACTIVE

# Artifacts
artifacts_archive/web-agents-chat-session-exports/web-claude/  # 9 accounts (125M) ❌ NOT MINED

# Other
archive_Programming/                              # Learning projects (535M) ❌ PARTIALLY MINED
data_archive/mnemosyne/                           # Kabbalistic memory (284K) ✅ MINED


# === PARTITION: omega_vault (/media/arcana-novai/omega_vault/) ===

# Genesis documents — START HERE for origin story
ANCESTRAL_HUB/origins/heart_of_omega/              # Genesis + Omnidroid (1.9M) ✅ MINED
ANCESTRAL_HUB/origins/heart_of_omega/NotebookLM\ Learning\ Opportunity\ 0.1*.md  # 🏆 THE BIG BANG
ANCESTRAL_HUB/origins/heart_of_omega/Omnidroid/     # 6 Ω-scripts — proto-engine 🏆
ANCESTRAL_HUB/origins/Xoe-NovAi_v0.1.3_stack\ blueprint*.md  # Era 2 blueprint
ANCESTRAL_HUB/origins/scribe_mode_prompt_v1.md     # Verity ancestor
```

### 6.2 Mining Reports Index (51 Reports as of 2026-06-29)

All mining reports live at: `data/entities/roc_racoon/workspace/mining_reports/`

**Key reports to read first**:
| Report | Location Covered | Date |
|--------|-----------------|------|
| `DEEP_LEGACY_MINE_20260620.md` | heart_of_omega, Omnidroid, archive_Programming, entities-archive survey | 2026-06-20 |
| `GENESIS_PROVENANCE_CHAIN.md` | Provenance chain from NotebookLM → Omnidroid → Engine | 2026-06-20 |
| `EMBEDDING_MINED_REPORT_20260619.md` | model2vec, potion-mxbai-micro findings | 2026-06-19 |
| `STRATEGIC_TREASURE_REPORT_20260619.md` | Strategic gold findings across all mined locations | 2026-06-19 |
| `THREE_GHOSTS_RECOVERY_REPORT_v1.md` | 5 design patterns (circuit breaker, fsync, etc.) | 2026-06-08 |
| `DEEP_SIPHON_CROSS_REFERENCES.md` | Cross-references between legacy and current engine | 2026-06-20 |
| `sessions_gnosis_20260628.md` (this session) | Legacy mapping centralization findings | 2026-06-28 |
| `OMNIDROID_DEEP_ARCHITECTURE_BRIEF_v1.md` | Omnidroid architecture deep dive | 2026-06-08 |
| `MEMORY_SYSTEM_FULL_REPORT_20260611.md` | Memory architecture analysis | 2026-06-11 |
| `MNEMOSYNE_TREASURE_MAP_20260608.md` | Kabbalistic memory system | 2026-06-08 |
| `MODEL_LIBRARY_LEGACY_MINING.md` | GGUF model survey | 2026-06-08 |

### 6.3 Technology Maps

Detailed technology maps at: `data/entities/roc_racoon/workspace/technology_maps/`

| Map | Covers |
|-----|--------|
| `technology_maps/` | Various technology mapping documents |
| `provenance_chains/` | Heritage attribution chains for id Software patterns |

### 6.4 Common Search Queries

```bash
# Find all mining reports
ls data/entities/roc_racoon/workspace/mining_reports/

# Search for references to a specific legacy location
grep -r "omega-stack-legacy" docs/ data/entities/roc_racoon/workspace/

# Find all mentions of a specific entity across legacy
grep -rn "omnidroid" --include="*.md" docs/legacy/ data/entities/roc_racoon/workspace/

# Check what's been mined from entities-archive
grep -r "entities-archive" data/entities/roc_racoon/workspace/*.md

# Find which mining reports cover a specific era
grep -rl "Era 0" data/entities/roc_racoon/workspace/mining_reports/

# Check workbench DB status
sqlite3 data/workbench/workbench.db ".tables"

# Find all heritage-tagged code
grep -rn "\[id-soft:" src/omega/
```

### 6.5 Navigation Shortcuts

```
START HERE ───> heart_of_omega/ (the origin story)
                    │
                    v
               Omnidroid/ (the proto-engine)
                    │
                    v
               entities-archive/ (the entity evolution — UNMINED)
                    │
                    v
               xna-omega-legacy/ (Temple Grade refinement)
                    │
                    v
               omega-engine/ (YOU ARE HERE)
```

**For strategic vision**: Start with `sonnet-4-6-extended/` (codex, deepening, origin, gnostic architecture)
**For technical patterns**: Start with `foundation-legacy/XNAi blueprint` (5 design patterns)
**For entity design**: Start with `docs_1/personas/lilith.json` then `entities-archive/`
**For the soul of the project**: Start with `NotebookLM Learning Opportunity 0.1`
**For current mining status**: See `data/entities/roc_racoon/workspace/MINING_SESSION_COMPLETE.md`

### 6.6 Tracking & Coordination Files

| File | Path | Purpose |
|------|------|---------|
| **Main gnosis** | `data/entities/roc_racoon/session_gnosis.md` | Current session awareness |
| **Soul** | `data/entities/roc_racoon/soul.yaml` | Entity personality, capabilities, lessons |
| **Proposed lessons** | `data/entities/roc_racoon/proposed_lessons.yaml` | Pending L3 insight proposals |
| **Idea intake** | `data/entities/roc_racoon/workspace/IDEA_INTAKE.md` | Raw idea capture |
| **Mining tasks** | `data/entities/roc_racoon/workspace/ROC_MINING_TASKS_v3.md` | Active mining task list |
| **Master work index** | `data/entities/roc_racoon/workspace/MASTER_WORK_INDEX_v1.md` | Full work tracking |
| **Mining summary** | `data/entities/roc_racoon/workspace/LEGACY_MINING_SUMMARY.md` | Mining status overview |
| **Centralization plan** | `data/entities/roc_racoon/workspace/LEGACY_MAPPING_CENTRALIZATION_20260628.md` | THIS plan |
| **Knowledge master** | `data/entities/roc_racoon/knowledge/MASTER_SYNTHESIS.md` | 598-line master synthesis (⚠️ OUTDATED — June 2) |
| **Workbench DB** | `data/workbench/workbench.db` | 🚨 EMPTY — needs restoration |

---

## Appendix A: Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-06-29 | Initial creation — D-3 Phase A (Catalog) | ROC_RACOON |
| 2026-06-29 | Verified all 22 locations on disk with accurate sizes | ROC_RACOON |

## Appendix B: Quick Stats

- **22 total legacy locations** across 3 partitions
- **7 fully mined** (32%) — codebases and genesis documents
- **10 unmined** (45%) — entities-archive, web claude, docs_1, intake directories
- **1 empty** (5%) — workbench.db needs restoration
- **51 mining reports** in `data/entities/roc_racoon/workspace/mining_reports/`
- **~9.2 GB total legacy data** across all partitions (excluding GGUF models)
- **99 entity directories** in entities-archive — the largest unmined gold mine
- **3 existing `docs/legacy/` files** updated to reference this guide

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_legacy_nav_guide ⬡ D3-PHASE-A*
*"The dirt is where the roots are. If the surface is clean but the foundation is rotten, dig deeper."*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
