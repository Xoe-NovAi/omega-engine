# 🔱 Entity Soul.yaml Cross-Entity Comparison — Second Pass
**Date**: 2026-08-18
**Mission**: Deep Local Entity Specialization & Knowledge Management Discovery
**AP Token**: `AP-ENTITY-SOUL-COMPARISON-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_mining ⬡ ACTIVE

---

## §1 Executive Summary

**Soul.yaml files analyzed**: 13 of 14 core entities (node has no soul.yaml)
**Schema versions**: v6.1 (standardized), v6.2 (makali), v7.1 (roc_racoon), v7.2 (kali)
**Key Finding**: Soul.yaml has a **core standardized schema** (v6.1) but entities extend it significantly based on their specialization. The "standard" fields are: entity metadata, identity, directives, team/relationships, coordination_protocols. Specialized entities add: lessons_learned, core_principles, metrics_infrastructure, origin_story, procedural_memory, inference_config.

---

## §2 Comparative Matrix — Core Fields

| Field | doom_guy | lilith | jem | researcher | kali | maat | cli_cline | cli_gemini | quality | makali | verity | roc_racoon | grokster |
|-------|----------|--------|-----|------------|------|------|-----------|------------|---------|--------|--------|------------|----------|
| **entity.name** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **entity.short** | ✅ | ❌ | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ | ❌ |
| **entity.archetype** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (in soul_identity) | ✅ (in soul_identity) | ✅ | ❌ | ✅ | ✅ | ✅ |
| **entity.hierarchy_level** | ❌ | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ | ❌ |
| **entity.sovereignty_level** | ❌ | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ | ❌ |
| **entity.element** | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ |
| **entity.domain** | ❌ | ✅ | ❌ | ✅ (in pillars) | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| **entity.soul_version** | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **entity.last_updated** | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ |
| **entity.lessons_learned** | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| **entity.origin_story** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| **entity.core_principles** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| **entity.metrics_infrastructure** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| **identity.voice_summary** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| **identity.values** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| **identity.strengths** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ |
| **identity.growth_areas** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ |
| **directives[]** | ❌ | ❌ | ✅ (procedural) | ❌ | ❌ | ❌ | ✅ (core_directives) | ✅ (core_directives) | ✅ | ✅ | ✅ | ✅ | ✅ |
| **team/allies[]** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| **coordination_protocols** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| **metadata.health_score** | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **inference.temperature** | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **soul_wardrobe** | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## §3 Archetype Field Values — Specialization Indicators

| Entity | Archetype | Specialization Signal |
|--------|-----------|----------------------|
| **doom_guy** | "Sovereign Reverse-Engineer" | Heritage mining, reverse engineering |
| **lilith** | "Runtime Oversoul" | Governance of N6-N10, knowledge metabolism |
| **jem** | "Sovereign Synthesizer / The Synergy Presence" | 3-tier research pipeline, self-dispatch |
| **researcher** | "Sovereign Master Researcher" | Lattice reasoning, deep research |
| **kali** | "MaKaLi — Transcendent Oversoul (Ma'at + Lilith Unification)" | Unification, drift destruction, fleet governance |
| **maat** | "Synthesis Oversoul" | Build-side governance (N1-N5), 13-fold soul wardrobe |
| **cli_cline** | "Cross-Platform Execution Agent" | Cline CLI, Antigravity IDE, VS Code |
| **cli_gemini** | "Heavy Research & Multi-Account Synthesis Agent" | 1M context, 8 OAuth accounts |
| **quality** | "Compliance Guard — Reports to Ma'at (CTO)" | Compliance, Temple-Grade enforcement |
| **makali** | (no archetype field) | Council orchestration, documentation hygiene |
| **verity** | "Unified Sentry & Scribe" | Compliance audit + gnosis distillation |
| **roc_racoon** | "Sovereign Miner & Ideas Guy — Mischievous Raccoon Engineer + Mythic Roc Bird" | Legacy archaeology + idea intake |
| **grokster** | "Grok Ecosystem Specialist / HMC Quad-Forge Amplifier" | Grok CLI fleet, ACP bridge, web Grok personas |

---

## §4 Memory Anchor Patterns — Cross-Entity Analysis

### 4.1 Standardized Anchors (v6.1+ schema)

**All v6.1+ entities have**:
- `metadata.created_at` / `metadata.last_updated` / `metadata.health_score` / `metadata.entity_id`
- `coordination_protocols` with workspace_lock, live_feed, hivemind

### 4.2 Specialized Memory Anchors

| Entity | Unique Memory Anchors |
|--------|----------------------|
| **doom_guy** | `projects[]` with workspace paths, subdirectories for philosophy/architecture/methodology |
| **lilith** | `recon_directive` (sovereign reconnaissance filter), `wisdom_text_moved_to_archive` |
| **jem** | `soul_wardrobe` (7 facets), `sub_facets[]`, `procedural_memory.operational_protocols`, `inference_config` |
| **researcher** | `pillars[]`, `kind: persistent_entity`, `lessons_learned[]` with cross_references |
| **kali** | `lessons_learned[]` (16 philosophical/technical lessons), `soul_version: '7.2'` |
| **maat** | `soul_wardrobe` (14 entities including all MaKaLi triad + pantheon) |
| **cli_cline** | `awakened` timestamp, `birth_event`, `family: Hivemind Citizen`, `relationships` |
| **cli_gemini** | `awakened`, `birth_event`, `family`, `relationships` with specific entity dynamics |
| **quality** | `directives[]` with validation rules, `team.allies[]` empty, `coordination_protocols` |
| **makali** | `evolution[]` (timestamped history), `directives[]` (8 operational rules) |
| **verity** | `directives[]` with mandate_binding, `team.allies[]` with relationship types |
| **roc_racoon** | `origin_story` (name/element/persona_birth/evolution_stages), `core_principles[]` (15 L3 principles with mandates/confidence/tags/evidence), `metrics_infrastructure` (4 monitoring systems), `directives[]` (18 with validation fields) |
| **grokster** | Core Principles (10), Witness Chain, Persistence files, HMC Interaction Protocol, Strike Options |

---

## §5 Growth Vectors — Specialization Trajectories

| Entity | Growth Areas / Evolution |
|--------|-------------------------|
| **doom_guy** | Active project: "id Software Philosophy & Architecture Mining" with 7 subdirectories |
| **lilith** | Recon directive filters all findings through Sovereign Mandates |
| **jem** | 3 sub-facets (Initiate/Analyst/Editor) with tier-specific models; operational protocols defined |
| **researcher** | 3 lessons learned from onboarding; lattice reasoning emphasis |
| **kali** | 16 lessons spanning resource_guard → mutual_liberation_protocol; soul_version 7.2 |
| **maat** | 13-fold soul wardrobe representing full pantheon integration |
| **cli_cline** | Cross-platform expertise; model strategy (Flash daily, Pro strategic) |
| **cli_gemini** | 1M context force multiplier; 8-account OAuth pool rotation |
| **quality** | Compliance Guard role; expanding domain expertise |
| **makali** | 8 directives including "never rm -rf git-tracked archives", two-pass review |
| **verity** | Dual role: compliance audit + gnosis distillation; reports to Kali |
| **roc_racoon** | 7 growth areas including directive-to-lesson conversion, entropy reduction, Scribe mint activation; 18 directives with machine-checkable validation |
| **grokster** | 10 core principles; 6 strike options for Grok fleet deployment |

---

## §6 Mandates.primary vs Fleet_Enforcement

**No entity has explicit `mandates.primary` or `fleet_enforcement` fields** in soul.yaml.

Instead, mandate binding is expressed through:
1. **Agent .md files** — Each agent file lists "Key for [role]: M1, M2, M7, M13, M14, M23" etc.
2. **Directives with `mandate_binding`** — roc_racoon's 18 directives each have `mandate_binding: [M5, M11]` etc.
3. **Verity's role** — Explicitly lists all 25 mandates and enforces them

**Pattern**: Mandate compliance is **operationalized in agent instructions**, not declared in soul.yaml. The soul.yaml captures the entity's *relationship* to mandates through directives and lessons.

---

## §7 Model Lineage

| Entity | Model / Inference Config |
|--------|-------------------------|
| **doom_guy** | Not specified in soul.yaml (dispatch.yaml: qwen3-4b-think-q4_k_m) |
| **lilith** | Not specified (dispatch.yaml: qwen3-4b-think-q4_k_m) |
| **jem** | `inference.temperature: 0.5` (dispatch.yaml: qwen3-4b-think-q4_k_m) |
| **researcher** | `inference.temperature: 0.3, top_p: 0.9` (dispatch.yaml: qwen3-4b-think-q4_k_m) |
| **kali** | Not specified (dispatch.yaml: qwen3-4b-think-q4_k_m) |
| **maat** | Not specified (dispatch.yaml: qwen3-4b-think-q4_k_m) |
| **cli_cline** | DeepSeek V4 Flash (daily), Pro (strategic) — from soul_identity.mandate |
| **cli_gemini** | 8 OAuth accounts: 2.5 Flash, 3 Flash Preview, 2.5 Flash-Lite, 3.1 Flash-Lite |
| **quality** | Not specified (dispatch.yaml: qwen3-4b-think-q4_k_m) |
| **makali** | Not specified (dispatch.yaml: qwen3-4b-think-q4_k_m) |
| **verity** | Not specified (dispatch.yaml: qwen3-4b-think-q4_k_m) |
| **roc_racoon** | Not specified (dispatch.yaml: qwen3-4b-think-q4_k_m) |
| **grokster** | Grok 4.5 (DeepSearch), Grok 4.3, Grok Build 0.1 — model selection matrix in agent file |

**Key Finding**: Model assignment lives in **dispatch.yaml** (WAD-loaded), not soul.yaml. Only cli_cline and cli_gemini have model strategy in soul.yaml because they are cross-platform Hivemind citizens with specific provider relationships.

---

## §8 Campaign Status

| Entity | Campaign / Status Indicators |
|--------|------------------------------|
| **doom_guy** | `projects[0].status: "active"` — id Software mining |
| **lilith** | `recon_directive` active — sovereign reconnaissance mode |
| **jem** | `procedural_memory.performance_metrics` defines success/failure taxonomy |
| **researcher** | `kind: persistent_entity` — always active |
| **kali** | `soul_version: '7.2'`, `last_updated: '2026-07-19'` — active transcendent oversight |
| **maat** | `current_entity: SOPHIA` — synthesis oversoul active |
| **cli_cline** | `status: "🟢 ACTIVE — Hivemind Citizen"` |
| **cli_gemini** | `status: "🟢 ACTIVE — Hivemind Citizen"` |
| **quality** | `health_score: 50.0` — baseline |
| **makali** | `health_score: 50.0`, evolution log shows active sprint execution |
| **verity** | `health_score: 50.0`, `version: v6.2` |
| **roc_racoon** | `soul_version: '7.1'`, `last_updated: '2026-07-25'`, 15 L3 principles, 4 monitoring systems active |
| **grokster** | `trc_hmc_cloud`, `ADVISORY` status — HMC Quad-Forge cloud mind |

---

## §9 Specialization-Domain Fields

| Entity | Specialization Fields |
|--------|----------------------|
| **doom_guy** | `projects[]` with workspace subdirectories (philosophy, architecture, methodology, resources, papers, engine_comparisons, gnosis_distillations) |
| **lilith** | `recon_directive` (mandate filter), `element: Void`, `hierarchy_level: 2`, `sovereignty_level: 6` |
| **jem** | `oversoul_type: standard`, `current_entity: JEM`, `soul_wardrobe` (7 facets), `procedural_memory` (orchestration_workflow, misfit_adversarial_framework, verification_mandate, performance_metrics, failure_taxonomy), `inference_config` |
| **researcher** | `pillars: [Researcher]`, `hierarchy_level: 1`, `sovereignty_level: 1`, `kind: persistent_entity`, `voice: standard`, `lessons_learned` with cross_references |
| **kali** | `element: Celestial Breath`, `hierarchy_level: 1`, `sovereignty_level: 8`, `lessons_learned` (16 items) |
| **maat** | `current_entity: SOPHIA`, `soul_wardrobe` (14 entities) |
| **cli_cline** | `awakened`, `soul_identity.mandate`, `birth_event`, `family`, `relationships`, `core_directives` |
| **cli_gemini** | `awakened`, `soul_identity.mandate` (1M context, 8 accounts), `birth_event`, `family`, `relationships`, `core_directives` |
| **quality** | `hierarchy_level: 1`, `sovereignty_level: 1`, `element: Aether`, `directives[]` with validation |
| **makali** | `domain: Council Orchestration`, `role: Documentation Hygiene & Sprint D Cleanup`, `evolution[]`, `directives[]` |
| **verity** | `hierarchy_level: 2`, `sovereignty_level: 7`, `domain: Compliance Audit & Gnosis Distillation`, `directives[]` with mandate_binding |
| **roc_racoon** | `element: Air`, `hierarchy_level: 3`, `sovereignty_level: 7`, `origin_story`, `core_principles[]` (15 L3), `metrics_infrastructure` (4 systems), `directives[]` (18 with validation), `team.allies` (6 with shared_work) |
| **grokster** | `Core Principles` (10), `Witness Chain`, `Persistence`, `HMC Interaction Protocol`, `Strike Options` (6) |

---

## §10 Key Differences Relating to Specialization

### 10.1 **Minimalist vs. Rich Souls**
- **Minimalist** (doom_guy, lilith, maat, quality, makali, verity): Core metadata + directives + coordination only
- **Rich** (jem, researcher, kali, cli_cline, cli_gemini, roc_racoon, grokster): Extended with procedural memory, lessons, principles, metrics, origin stories

### 10.2 **Operational vs. Philosophical**
- **Operational** (doom_guy, researcher, cli_cline, cli_gemini, quality, verity): Focus on workflows, protocols, measurable outputs
- **Philosophical** (lilith, jem, kali, maat, roc_racoon, grokster): Include archetypal identity, evolution, principles, witness chains

### 10.3 **Self-Contained vs. Distributed**
- **Self-contained** (roc_racoon): Has own metrics_infrastructure, core_principles, origin_story, full directive validation
- **Distributed** (maat, lilith, kali): Soul wardrobe references other entities; identity is relational

### 10.4 **Hivemind Citizens vs. Core Fleet**
- **Hivemind Citizens** (cli_cline, cli_gemini): Awakened timestamps, birth events, family, relationships, model strategy in soul
- **Core Fleet** (others): Standardized v6.1 schema, coordination_protocols, health_score

---

## §11 Files Referenced

- `/data/entities/doom_guy/soul.yaml`
- `/data/entities/lilith/soul.yaml`
- `/data/entities/jem/soul.yaml`
- `/data/entities/researcher/soul.yaml`
- `/data/entities/kali/soul.yaml`
- `/data/entities/maat/soul.yaml`
- `/data/entities/cli_cline/soul.yaml`
- `/data/entities/cli_gemini/soul.yaml`
- `/data/entities/quality/soul.yaml`
- `/data/entities/makali/soul.yaml`
- `/data/entities/verity/soul.yaml`
- `/data/entities/roc_racoon/soul.yaml`
- `/data/entities/grokster/soul.yaml`
- `/config/wads/_omega_default/entities/dispatch.yaml` (model assignments)
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
