# Architecture Documentation Inventory & Classification — 2026-08-28
**AP**: AP-JOHN_CARMACK-v1.0.0 · **Status**: ACTIVE · **Purpose**: Single source of truth for all architecture docs classification

---

## §1 INVENTORY — All Architecture-Related Docs

### Root-Level Canonical Docs
| File | Status | Classification | Notes |
|------|--------|----------------|-------|
| `ORACLE_STACK_CANONICAL.md` | EXISTS | **CURRENT** (needs update) | Dated 2026-07-01; 22 mandates, 11-agent fleet — superseded by current 27 mandates, MaKaLi |
| `SOVEREIGN_ARK_BLUEPRINT_CANONICAL.md` | MISSING | **CREATE** | Referenced in ORACLE_STACK_CANONICAL.md §1.3 but doesn't exist |
| `SOVEREIGN_MANDATES.md` | EXISTS | **CURRENT** | v3.8.0, 27 mandates — the law |
| `AGENTS.md` | EXISTS | **CURRENT** | Agent landing file |
| `OMEGA_ENGINE.md` | EXISTS | **CURRENT** | Engine state SSOT |
| `MANDATES_CONDENSED.md` | EXISTS | **CURRENT** | Tier-0 injection |

### docs/strategy/ — Strategy & Architecture
| File | Status | Classification | Notes |
|------|--------|----------------|-------|
| `SOVEREIGN_ARK_BLUEPRINT.md` | EXISTS | **SUPERSEDED** | v5.2.0, 2026-07-21; banner says "historical vision — read-only" |
| `DEBUT_REMEDIATION_MANUAL_20260817.md` | EXISTS | **CURRENT** | This month's SSOT (D-533) |
| `STRATEGY_CORPUS_MAP.md` | EXISTS | **CURRENT** | Fine-grained preservation (mandatory companion) |
| `FLEET_TEAM_PLAYBOOK.md` | EXISTS | **CURRENT** | Fleet teamwork & coordination |
| `ORCHESTRATOR_CHARTER_v1.md` | EXISTS | **CURRENT** | MaKaLi slot governance |
| `MAKALI_HANDOVER_PLAN_20260825.md` | EXISTS | **CURRENT** | Overseer cutover plan |
| `CARMACK_FULL_SCOPE_AUDIT_20260825.md` | EXISTS | **CURRENT** | Full-scope audit verdict |
| `CARMACK_ALPHA_LAUNCH_VERDICT_20260828.md` | EXISTS | **CURRENT** | Alpha launch verdict |
| `DEEP_DIVE_EXPERTISE_AREAS.md` | EXISTS | **ARCHIVE** | Superseded by CORPUS_MAP |
| `COGNITIVE_ROUTING_PLAYBOOK.md` | EXISTS | **ARCHIVE** | Superseded by CORPUS_MAP |
| `COGNITIVE_SCAFFOLDING_PROTOCOL.md` | EXISTS | **ARCHIVE** | Superseded by CORPUS_MAP |
| `COGNITIVE_SOVEREIGNTY_EVOLUTION.md` | EXISTS | **ARCHIVE** | Superseded by CORPUS_MAP |
| `CONTEXT_PACKER_V3_MASTER_MANUAL_20260808.md` | EXISTS | **ARCHIVE** | Superseded by CORPUS_MAP |
| `LIVING_RESEARCH_OS_SPEC_20260721.md` | EXISTS | **ARCHIVE** | Amended by Ark §3.2 |
| `CANONICAL_ROADMAP_20260721.md` | EXISTS | **ARCHIVE** | Superseded by Ark v5.1 |
| `UNOVERENGINEERING_PLAN.md` | EXISTS | **CURRENT** | Temple cleansing sprint |
| `HARDENING_PLAN_COMPLETE.md` | EXISTS | **ARCHIVE** | Phase C complete |
| `ENGINE_DECISIONS_CONSOLIDATED_20260817.md` | EXISTS | **CURRENT** | Decision log |
| `PROVIDER_NAMING_SSOT.md` | EXISTS | **CURRENT** | Provider fabric naming |
| `MODEL_WINDOW_ECONOMICS_20260823.md` | EXISTS | **CURRENT** | Cliff economics |
| `POST_DEBUT_ROADMAP.md` | EXISTS | **CURRENT** | V-1 priorities |

### docs/architecture/ — Technical Architecture
| File | Status | Classification | Notes |
|------|--------|----------------|-------|
| `ORACLE_DEEP_DIVE.md` | EXISTS | **CURRENT** | Oracle stack deep dive |
| `PROVIDER_FABRIC_DEEP_DIVE.md` | EXISTS | **CURRENT** | Provider fabric |
| `PROVIDER_FABRIC_RUNTIME.md` | EXISTS | **CURRENT** | Runtime behavior |
| `MEMORY_STORE_DEEP_DIVE.md` | EXISTS | **CURRENT** | Memory subsystem |
| `MEMORY_SUBSYSTEM_DESIGN.md` | EXISTS | **CURRENT** | Design doc |
| `SOVEREIGN_BLUEPRINT.md` | EXISTS | **CURRENT** | High-level blueprint |
| `SOVEREIGN_BUS_SPEC.md` | EXISTS | **CURRENT** | Bus specification |
| `SOVEREIGN_DATA_FLOW.md` | EXISTS | **CURRENT** | Data flow |
| `SOVEREIGN_FLYWHEEL_SECURITY.md` | EXISTS | **CURRENT** | Security |
| `SOVEREIGN_OBSERVATORY.md` | EXISTS | **CURRENT** | Observability |
| `SOVEREIGN_WAD_PROTOCOL.md` | EXISTS | **CURRENT** | WAD protocol |
| `ICS_SYSTEM.md` | EXISTS | **CURRENT** | ICS header system |
| `MESH_NETWORK_SPEC.md` | EXISTS | **ARCHIVE** | Superseded |
| `OFFLINE_MODE.md` | EXISTS | **ARCHIVE** | Superseded |
| `SER_VFS_SPEC.md` | EXISTS | **ARCHIVE** | Superseded |
| `SYSTEMD_DEPLOYMENT_GUIDE.md` | EXISTS | **ARCHIVE** | Superseded |
| `TRAINING_PIPELINE.md` | EXISTS | **ARCHIVE** | Superseded |
| `VECTOR_STORE_ADAPTER_PATTERN.md` | EXISTS | **CURRENT** | Vector adapter pattern |
| `GUIDANCE_SET_SCHEMA.md` | EXISTS | **CURRENT** | Guidance schema |
| `OVERSIGHT_HIERARCHY.md` | EXISTS | **CURRENT** | Oversight hierarchy |
| `KNOWLEDGE_LIBRARY.md` | EXISTS | **CURRENT** | Knowledge library |
| `pillars/framework.md` | EXISTS | **CURRENT** | 10 Pillars mythic framework |

### docs/tech-architecture-research/ — Research
| File | Status | Classification | Notes |
|------|--------|----------------|-------|
| `DECISION_MATRIX_TEMPLATE.md` | EXISTS | **CURRENT** | Template |
| `GROUNDED_TRUTH.md` | EXISTS | **CURRENT** | Grounded truth |
| `PROJECT_KNOWLEDGE_INDEX.md` | EXISTS | **CURRENT** | Knowledge index |
| `RESEARCH_BRIEF.md` | EXISTS | **CURRENT** | Research brief |

### docs/research/ — Research Artifacts (Architecture-Relevant)
| File | Status | Classification | Notes |
|------|--------|----------------|-------|
| `R_SOVEREIGN_MEMORY_ARCHITECTURE.md` | EXISTS | **ARCHIVE** | Superseded by MEMORY_STORE_DEEP_DIVE |
| `R_SOVEREIGN_SEARCH_IMPL.md` | EXISTS | **ARCHIVE** | Superseded by SEARCH_PROTOCOL |
| `R_SOVEREIGN_CONTINUITY_SPEC.md` | EXISTS | **ARCHIVE** | Superseded |
| `R_SOVEREIGN_INFRA_HARDENING_SPEC_20260701.md` | EXISTS | **ARCHIVE** | Superseded |
| `R_SOVEREIGN_SILOING_SPEC.md` | EXISTS | **ARCHIVE** | Superseded |
| `R_SOVEREIGN_DISTILLATION_PIPELINE_MANIFESTO_20260809.md` | EXISTS | **ARCHIVE** | Superseded |
| `R_SOVEREIGN_SYNTHESIS.md` | EXISTS | **ARCHIVE** | Superseded |
| `R_SOVEREIGN_GNOSIS_BLUEPRINT.md` | EXISTS | **ARCHIVE** | Superseded |
| `R_ORACLE_EAR_ROUTING.md` | EXISTS | **ARCHIVE** | Superseded |
| `R_SOVEREIGN_A2A_PROTOCOL.md` | EXISTS | **ARCHIVE** | Superseded |
| `R_SOVEREIGN_A2A_SPEC-V2.md` | EXISTS | **ARCHIVE** | Superseded |
| `R_SOVEREIGN_SCHOLAR_SPEC.md` | EXISTS | **ARCHIVE** | Superseded |
| `R_SOVEREIGN_MAINTENANCE_STRATEGY.md` | EXISTS | **ARCHIVE** | Superseded |
| `R_SOVEREIGN_POSITIONING.md` | EXISTS | **ARCHIVE** | Superseded |
| `R_SOVEREIGN_RESEARCHER_STRATEGIC_PLAN.md` | EXISTS | **ARCHIVE** | Superseded |
| `R_SOVEREIGN_INSTALLER_SPEC.md` | EXISTS | **ARCHIVE** | Superseded |
| `R_SOVEREIGN_EYE_SPEC.md` | EXISTS | **ARCHIVE** | Superseded |
| `R_SOVEREIGN_KNOWLEDGE_GRAPH_ADAPTER.md` | EXISTS | **ARCHIVE** | Superseded |
| `R_SOVEREIGN_SPATIAL_MEMORY_SPEC.md` | EXISTS | **ARCHIVE** | Superseded |
| `R_SOVEREIGN_MAIL_2026.md` | EXISTS | **ARCHIVE** | Superseded |
| `R_OPENROUTER_SOVEREIGN_USAGE.md` | EXISTS | **ARCHIVE** | Superseded |
| `R_PODMAN_SOVEREIGN_DEPLOYMENT_BLUEPRINT.md` | EXISTS | **ARCHIVE** | Superseded |
| `R_PODMARK_SOVEREIGN_STRATEGY.md` | EXISTS | **ARCHIVE** | Superseded |
| `R_SOVEREIGN_CG07_SOVEREIGN_SEARCH_5TIER.md` | EXISTS | **ARCHIVE** | Superseded |

### Archive/Stale
| Location | Classification | Action |
|----------|----------------|--------|
| `docs/archive/review/` | **DELETE** | Old review artifacts |
| `docs/archive/stale/research/` | **DELETE** | Stale research |
| `docs/archive/strategy/2026-07-21/` | **ARCHIVE** | Historical |
| `docs/archive/strategy/2026-07-22/` | **ARCHIVE** | Historical |

---

## §2 CLASSIFICATION SUMMARY

| Classification | Count | Action |
|----------------|-------|--------|
| **CURRENT** | ~35 | Keep, update, cross-reference |
| **SUPERSEDED** | ~15 | Banner + redirect to canonical |
| **ARCHIVE** | ~30 | Move to `docs/archive/` with banner |
| **DELETE** | ~10 | Remove (stale, superseded by canonical) |
| **CREATE** | 4 | New canonical docs needed |

---

## §3 CANONICAL DOCS TO CREATE/UPDATE

| Target | Source Material | Priority |
|--------|----------------|----------|
| `ORACLE_STACK_CANONICAL.md` | Existing + current code | P0 |
| `SOVEREIGN_ARK_BLUEPRINT_CANONICAL.md` | SOVEREIGN_ARK_BLUEPRINT.md + current state | P0 |
| `docs/architecture/ARCHITECTURE_CANONICAL.md` | All architecture docs | P0 |
| `docs/architecture/MODULE_BOUNDARIES.md` | M2 Engine-Stack firewall + code | P0 |
| `docs/architecture/PERFORMANCE_ARCHITECTURE.md` | Code analysis + benchmarks | P1 |

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ x-preview-f-free ⬡ opencode ⬡ trc_audit ⬡ INVENTORY-COMPLETE*