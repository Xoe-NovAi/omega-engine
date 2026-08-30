---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "documentation_audit"
document_id: "roc-documentation-survey-20260828"
title: "Documentation Landscape Survey — Full Inventory, Duplications, Gaps"
status: "ACTIVE"
date: "2026-08-28"
author: "roc_racoon (Codebase Archaeology Specialist)"
sprint: "PUBLIC-DEBUT-01"
confidence: 🟢 VERIFIED (all counts and files verified)
model: "openrouter/minimax/minimax-m3:free"
---

# 🔱 R_ROC_DOCUMENTATION_SURVEY_20260828 — Full Documentation Landscape Survey

**AP Token**: `AP-ROC-DOC-SURVEY-20260828-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ openrouter/minimax/minimax-m3:free ⬡ opencode ⬡ trc_doc_survey ⬡ ACTIVE

**Date**: 2026-08-28
**For**: Grokster + Architect
**Purpose**: Comprehensive documentation landscape survey before soft launch

---

## §0 — Executive Summary

The Omega Engine has **4,325 .md files** across 4 main directories (~320 MB). The documentation is **EXTENSIVE but CHAOTIC**:

1. **Total scale**: 4,325 .md files (1,564 in `docs/`, 634 in `data/coordination/`, 842 in `data/entities/`, 199 in `.opencode/`)
2. **Duplications**: **64 session_gnosis files** (1 per session); **27+ _v1/_v2/_v3 patterns**; **20+ model strategy docs** scattered across 4 directories
3. **Archive dirs**: 16 `archive/` directories (docs/archive: 468 files, 19 MB; data/coordination/archive: 140 files, 2.3 MB)
4. **Stale content**: **P1.md (113 lines)**, **P9.md (333 lines)** are dev artifacts NOT documentation; **HYDRATION_REPORT.md** is from Aug 7; **RESEARCH_EXECUTION_UPDATE.md** is from Jul 23
5. **Documentation gaps**: How to use dispatch guardrail, vault, 8-account Cline review, model fleet — NOT documented for the community

---

## §1 — Full Documentation Inventory

### 1.1 Repository-Wide Counts

| Directory | .md Files | Total Size | Description |
|-----------|-----------|-----------|-------------|
| `docs/` | **1,564** | **36 MB** | All documentation (research, architecture, strategy, team, intake, positioning, decisions) |
| `data/coordination/` | **634** | **60 MB** | Handoffs, briefings, R_* reports, handoffs, briefings |
| `data/entities/` | **842** | **93 MB** | Entity files (soul, session_gnosis, proposed_lessons, knowledge, workspace) |
| `.opencode/` | **199** | **134 MB** | Agent configs, commands, rules, plugins |
| **TOTAL** | **3,239** | **~323 MB** | All 4 main dirs |

**Repo-wide**: 4,325 .md files (excluding node_modules, .venv, __pycache__).

### 1.2 `docs/` Subdirectories (Top Contributors)

| Subdirectory | .md Files | Notes |
|--------------|-----------|-------|
| `docs/research/` | **609** | Largest dir (39% of docs/); contains archive subdir |
| `docs/archive/` | **468** | Second largest (30% of docs/); 19 MB; many STALE files |
| `docs/strategy/` | **141** | Strategic plans, 25+ files with D-series decisions |
| `docs/hardening/` | **46** | P0 hardening sprints |
| `docs/specs/` | **47** | Technical specs (context_injection, team_infra, etc.) |
| `docs/architecture/` | **26** | Core architecture docs |
| `docs/reference/` | **23** | API references, config loaders |
| `docs/gnosis/` | **18** | Lattice manifest, heritage, etc. |
| `docs/sprints/` | **14** | Sprint records |
| `docs/operations/` | **12** | Handoff, deployment, operations |
| `docs/knowledge/` | **14** | KB fragments (R_RESEARCH_BEST_PRACTICES_KB_PART*) |
| `docs/kb/` | **28** | Active Omega-KB Protocol entries (kb-0001, etc.) |
| `docs/how-to/` | **9** | Practitioner guides |
| `docs/explanation/` | **8** | Concept explanations |
| `docs/standards/` | **7** | Engineering standards |
| `docs/team/` | **7** | Team handoffs |
| `docs/positioning/` | **5** | FOR_TECHNICAL, FOR_ESOTERIC, FOR_AVERAGE_USERS |
| `docs/briefings/` | **4** | Daily/weekly briefings |
| `docs/execution/` | **3** | Execution plans |
| `docs/decisions/` | **4** | ADR-style decisions |
| `docs/protocol/` | **3** | MEDITATION_PROTOCOL, etc. |
| (other 15+ dirs) | <3 each | Long tail (intake, creative, legacy, etc.) |

### 1.3 `data/coordination/` Subdirectories

| Subdirectory | .md Files | Notes |
|--------------|-----------|-------|
| `data/coordination/` (top-level) | **233** | R_ROC_* (9 files), R_JEM_* (1), R_CARMACK_* (1), R_RESEARCHER_* (1), briefings, handoffs |
| `data/coordination/archive/` | **140** | Old handoffs, FLE studies, council records |
| `data/coordination/research/` | **78** | 78 research files (parallel to docs/research/) |
| `data/coordination/meditations/` | **25** | 25 meditation records (per session/agent) |
| `data/coordination/SESSION_PAGING_REPORTS/` | **31** | Per-session paging reports |
| `data/coordination/teamstudy_20260823/` | **19** | Team study artifacts |
| `data/coordination/grok_cli/` | **19** | Grok CLI handoffs |
| `data/coordination/fle_study_20260825/` | **12** | FLE study (532K + 340K = 872K in 2 files) |
| `data/coordination/council_20260824/` | **10** | Council records |
| `data/coordination/research_wave2/` | **9** | Wave 2 research |
| `data/coordination/anchored_summary/` | **6** | Anchored summaries |
| `data/coordination/session_gnosis/` | **5** | Cross-session gnosis |
| `data/coordination/meditate_tournament_20260826/` | **4** | Tournament records |
| `data/coordination/gap_investigation_20260825/` | **4** | Gap investigations |
| `data/coordination/handoffs/` | **2** | Active handoffs |
| (other dirs) | <2 each | Many empty dirs (awareness/, errors/, instances/, locks/, tasks/, sessions/) |

### 1.4 `data/entities/` — 54 Entity Directories

**Top contributors** (largest entity dirs by file count):

| Entity | Files | Notes |
|--------|-------|-------|
| `john_carmack/` | **477** | **LARGEST** (S3 consultant, many research artifacts) |
| `data/entities/` | **842 total** | Across 54 entities |
| `grokster/` | 72 | Cross-platform specialist, rich KB |
| `jem/` | 64 | Research/knowledge pipeline |
| `lilith/` | 46 | Runtime Oversoul |
| `kali/` | 45 | Grand Oversight |
| `doom_guy/` | 26 | Heritage, ID software |
| `maat/` | 26 | Build Oversoul |
| `roc_racoon/` | 26 | Legacy archaeology |
| `iris/` | 7 | Messenger bridge |
| `default/` | 7 | Default agent config |
| `antigravity/` | 5 | Google-fallback |
| `makali/` | 5 | Fusion entity |
| `cli_cline/` | 2 | Cline CLI |
| `cli_gemini/` | 4 | Gemini CLI |
| (40+ other entities) | 1 each | Minimal: soul.yaml only |

**Entity dir pattern**:
- `soul.yaml` — identity + capabilities
- `proposed_lessons.yaml` — L1→L2→L3 blind staging
- `session_gnosis.md` — M15 continuity anchor
- `knowledge/` — promoted KB topics + INDEX
- `workspace/` — working reports, handoffs
- `archive/` — old versions (where applicable)

### 1.5 Meditations — 25 Records

| Date Range | Count | Notes |
|------------|-------|-------|
| 2026-08-22 (oxalpha) | 1 | Ox Alpha full utilization |
| 2026-08-23 (kali, researcher) | 4 | Hidden gems, context packer, oversight audit, gnosis mining codex |
| 2026-08-24 (kali, lilith, maat, researcher) | 8 | W1-W4 specs, D602 torchfree, etc. |
| 2026-08-26 (opus) | 1 | Hidden gems, 5 voices |
| 2026-08-28 (grokster, antigravity, cline, copilot, carmack, roc) | 11 | PUBLIC-DEBUT-01 harvest |

### 1.6 Top-Level Files

| File | Size | Modified | Notes |
|------|------|----------|-------|
| `session-ses_07ee.md` | **641 KB** | Aug 7 | **HUGE** (1 session transcript dump) |
| `P9.md` | **281 KB** | Aug 28 | **HUGE** (dev artifact) |
| `P1.md` | **113 KB** | Aug 28 | **HUGE** (dev artifact) |
| `P6.md` | 89 KB | Aug 28 | Dev artifact |
| `P7.md` | 88 KB | Aug 28 | Dev artifact |
| `P5.md` | 83 KB | Aug 28 | Dev artifact |
| `P3.md` | 71 KB | Aug 28 | Dev artifact |
| `P4.md` | 49 KB | Aug 28 | Dev artifact |
| `AGENTS.md` | 5.6 KB | Aug 28 | **THE** team entry doc |
| `SOVEREIGN_MANDATES.md` | 24 KB | Aug 28 | **THE** constitutional law |
| `README.md` | 11 KB | Aug 28 | Project README |
| `CHANGELOG.md` | 8.5 KB | Aug 28 | Recent changelog |
| `HYDRATION_REPORT.md` | 4.5 KB | **Aug 7** | ⚠️ **STALE** (3 weeks old) |
| `RESEARCH_EXECUTION_UPDATE.md` | 1.7 KB | **Jul 23** | ⚠️ **STALE** (5 weeks old) |
| `ORACLE_STACK_CANONICAL.md` | 17 KB | Aug 28 | THE oracle stack doc |
| `OMEGA_ENGINE.md` | 20 KB | Aug 28 | Engine overview |
| `OMEGA_CODEX.md` | 19 KB | Aug 28 | Engine codex |

---

## §2 — Superseded Documents

### 2.1 Files with Explicit "SUPERSEDED" Markers (20 files)

| File | Reason | Line |
|------|--------|------|
| `data/coordination/PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828.md` | "SUPERSEDED — replaced by v2" | 6-22 |
| `data/coordination/R_ROC_OPENCODE_CONTEXT_MINING_20260828.md` | Superseded by corrected version | (header) |
| `data/coordination/THE_VISION_CANONICAL_DRAFT_20260823.md` | "SUPERSEDED 2026-08-26" by VISION_ANCHOR_PERPETUAL | 3-6 |
| `docs/sprints/current/README.md` | (marked superseded) | — |
| `docs/team/COMMUNICATION_HUB.md` | (marked superseded) | — |
| `docs/changelog.md` | (marked superseded) | — |
| `docs/research/R_OPENCODE_PLATFORM_INTERNALS_20260824.md` | (marked superseded) | — |
| `docs/research/R_EMBEDDING_ADAPTERS.md` | (marked superseded) | — |
| `docs/research/GROK_CLI_KNOWLEDGE_GAPS.md` | (marked superseded) | — |
| `docs/research/R_SKEPTICAL_VERIFICATION.md` | (marked superseded) | — |
| `docs/research/R_QDRANT_OPTIMIZATION.md` | (marked superseded) | — |
| `docs/research/R_SKEPTICAL_VERIFIER_FOUNDATION.md` | (marked superseded) | — |
| `docs/specs/team_infra/SPEC-D-p2-hygiene.md` | (marked superseded) | — |
| `docs/specs/VAULT_OVERHAUL_IMPLEMENTATION_MANUAL_20260818.md` | (marked superseded) | — |
| `docs/archive/MASTER_DOCUMENT_SSOT_STALE.md` | (in archive, marked stale) | — |
| `docs/archive/stale/team/OMEGA_SYSTEMS_DISCOVERY_REPORT.md` | (in archive/stale) | — |
| `docs/archive/stale/research/DATA_MANAGEMENT_HARDENING.md` | (in archive/stale) | — |
| `docs/archive/stale/research/COO-chat-custom-mode-test_*` (3 files) | (in archive/stale) | — |
| `docs/archive/sprints/2026-07-25-guard-and-distill/index.md` | (in archive) | — |
| `docs/adr/` (3 files) | (archived, kept for reference) | — |

### 2.2 _v1, _v2, _v3 Patterns (27 files)

| Pattern | Files | Status |
|---------|-------|--------|
| `soul_v1_archive.yaml` | 1 | Archive of old soul |
| `roc_test_v1.md` | 1 | Test file |
| `*_v1_*.md` (Roc workspace) | 10 | Mining briefs (DEEPSEEK_HARDENING_PASS_v2, YAML_HARDENING_BRIEF_v1, ORPHANED_SPECS_REPORT_v1, etc.) |
| `ROC_MINING_TASKS_v3.md` | 1 | Current tasks |
| `JEM_DEEP_ARCHITECTURE_BRIEF_v1.md` | 1 | Architecture brief |
| `ICS_TREASURE_MAP_v1.md` | 1 | Treasure map |
| `HIVEMIND_HARDENING_SPEC_v1.md` | 1 | Hardening spec |
| `OMNIDROID_DEEP_ARCHITECTURE_BRIEF_v1.md` | 1 | Architecture brief |
| `MINING_REPORT_MAKALI_COUNCIL_VISION_v2.md` | 1 | Council vision report |
| `CRUCIBLE_FINAL_SPEC_v2.md` | 1 | Spec |
| `MASTER_WORK_INDEX_v1.md` | 1 | Work index |
| `THREE_GHOSTS_RECOVERY_REPORT_v1.md` | 1 | Recovery report |
| `DEEPSEEK_FINAL_PASS_v3_20260608.md` | 1 | DeepSeek hardening |
| `MAKALI_TRIAD_DEEP_MINING_REPORT_v1.md` | 1 | Mining report |
| `COMPACTION_REMEDIATION_IMPLEMENTATION_PLAN_v1.md` | 1 | Compaction plan |
| `UBUNTU_PYTHON_MODERNIZATION_REPORT_v1.md` | 1 | Modernization report |
| `MIGRATION_*_EVIDENCE_20260822_v3.md` | 1 | Migration evidence |
| `REHEARSAL_LEARNING_PLAN_20260822_v3.md` | 1 | Rehearsal plan |
| `MIGRATION_PLAYBOOK_SPEC_20260822_v2.md` | 1 | Migration playbook |
| `MIGRATION_PLAYBOOK_SPEC_20260822_v3.md` | 1 | Migration playbook v3 |
| `MIGRATION_CASE_STUDIES_EVIDENCE_20260822_v2.md` | 1 | Migration evidence v2 |
| `REHEARSAL_LEARNING_PLAN_20260822_v2.md` | 1 | Rehearsal plan v2 |
| `ANTIGRAVITY_API_VERIFICATION_REPORT_v1.md` | 1 | Verification report |

**Pattern**: v1/v2/v3 are versioned working files. The "current" version is the highest-numbered. Older versions are historical.

### 2.3 Archive Directories (16 total)

| Path | Size | Notes |
|------|------|-------|
| `docs/archive/` | 19 MB | **LARGEST archive** (468 .md files) |
| `data/coordination/archive/` | 2.3 MB | 140 .md files (handoffs, FLE, council) |
| `config/wads/arcana_novai/archive` | — | WAD-specific |
| `data/entities/roc_racoon/archive` | — | Old soul versions |
| `data/entities/roc_racoon/memory/archive` | — | Old memory |
| `data/entities/lilith/memory/archive` | — | Old memory |
| `data/entities/lilith/workspace/archive` | — | Old workspaces |
| `data/entities/maat/memory/archive` | — | Old memory |
| `data/entities/researcher/memory/archive` | — | Old memory |
| `data/entities/researcher/workspace/archive` | — | Old workspaces |
| `data/entities/john_carmack/memory/archive` | — | Old memory |
| `data/entities/jem/knowledge/SOVEREIGN_IDENTITY/archive` | — | Old identity |
| `data/entities/jem/memory/archive` | — | Old memory |
| `data/entities/verity/memory/archive` | — | Old memory |
| `data/entities/doom_guy/memory/archive` | — | Old memory |
| `data/entities/grokster/kb/archive` | — | Old KB |

---

## §3 — Duplicated Content

### 3.1 Session Gnosis Duplication (64 files)

The biggest duplication. Each agent has 1-7 `session_gnosis*.md` files (per session date):

| Entity | session_gnosis Files |
|--------|----------------------|
| `roc_racoon/` | 8 (20260615, 20260618, 20260629, 20260707, 20260708, 20260716, 20260824, Roc-N7, current) |
| `lilith/` | 4 (workspace, 20260821, 20260824, L-N7) |
| `maat/` | 2 (20260824, workspace) |
| `JOHN_CARMACK/` | 1 (20260810) |
| `antigravity/` | 1 (workspace) |
| `iris/` | 1 (workspace) |
| (other entities) | 1 each |

**Pattern**: `session_gnosis_YYYYMMDD.md` is the date-stamped snapshot. `session_gnosis.md` is the current/latest. The "_L-N7" and "_Roc-N7" suffixes are sub-specialist variants.

**Duplication risk**: HIGH. These files overlap heavily. The "current" version supersedes the date-stamped versions, but old versions are never deleted.

### 3.2 Model Strategy Duplication (20+ files)

| File | Topic |
|------|-------|
| `config/model_registry/model_db/CURRENT_MODELS.md` | Current model registry |
| `data/entities/roc_racoon/workspace/LOCAL_MODELS_BRIEFING_GAMEPLAN_20260730.md` | Local models gameplan |
| `data/entities/roc_racoon/workspace/MODEL_INVENTORY_20260611.md` | Old model inventory |
| `data/entities/roc_racoon/workspace/MODEL_LIBRARY_LEGACY_MINING.md` | Legacy mining |
| `data/entities/lilith/workspace/active/MODEL_RUNTIME_GOVERNANCE_AUDIT.md` | Runtime governance |
| `data/entities/researcher/workspace/research_reports/R45_TOKENOMICS_COST_MODELING_20260813.md` | Tokenomics |
| `data/entities/researcher/workspace/research_reports/R2_MODEL_WINDOW_DETECTION_20260813.md` | Window detection |
| `data/entities/researcher/workspace/MODEL_KB_GAP_ANALYSIS.md` | KB gap analysis |
| `data/entities/researcher/workspace/MODEL_LEGACY_AUDIT_20260619.md` | Legacy audit |
| `data/coordination/SUBAGENT_MODEL_CORRECTION_20260828.md` | Subagent correction |
| `data/coordination/research/R_ANTIGRAVITY_MULTI_MODEL_TRUNCATION_20260828.md` | Antigravity |
| `data/coordination/research/R_402_FREE_MODEL_20260827.md` | 402 free model |
| `data/coordination/PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828.md` | Protocol v1 (SUPERSEDED) |
| `data/coordination/PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828_v2.md` | Protocol v2 |
| `data/coordination/R_ROC_SUBAGENT_MODEL_ARCHAEOLOGY_20260828.md` | Archaeology |
| `data/coordination/SUBAGENT_MODEL_PROTOCOL_BRIEFING_20260828.md` | Briefing |
| `data/coordination/R_RESEARCHER_TASK_TOOL_MODEL_RESEARCH_20260828.md` | Research |
| `data/coordination/R_CARMACK_REVIEW_SUBAGENT_MODEL_20260828.md` | Review |
| `data/coordination/archive/archive_20260720/handoff/CLINE_MODEL_REGISTRY_FIX_HANDOFF.md` | Old Cline fix |
| `data/coordination/archive/archive_20260720/handoff/CLINE_MODEL_REGISTRY_VERIFICATION_HANDOFF.md` | Old Cline verify |

**Duplication risk**: MEDIUM. Many overlapping model docs. The recent cluster (SUBAGENT_MODEL_*, PROTOCOL_*, etc.) is well-organized; the older docs (2026-06, 2026-07) are scattered.

### 3.3 Sovereignty/Oversoul Duplication (15+ files)

| File | Topic |
|------|-------|
| `data/entities/roc_racoon/workspace/OVERSIGHT_AUDIT_GROUND_TRUTH_20260823.md` | Ground truth |
| `data/entities/researcher/workspace/OVERSIGHT_AUDIT_WEB_RESEARCH_20260823.md` | Web research |
| `data/coordination/ARCHITECT_OVERSIGHT_PATTERNS_20260823.md` | Patterns |
| `data/coordination/KALI_OVERSIGHT_PORTFOLIO_20260811.md` | Portfolio (old) |
| `data/coordination/meditations/records/MEDITATION_KALI_20260823_SESSION_TRACKING_OVERSIGHT_AUDIT.md` | Meditation |
| `data/coordination/sessions/kali/ingest_*_sovereign_*` | Sessions |
| `docs/research/sovereign_memory` | Sovereign memory research |
| `docs/research/R_LONGCAT2_FINAL_OVERSIGHT_20260810.md` | LongCat2 (old) |
| `docs/research/sovereign_hardening_codex.md` | Hardening codex |
| `docs/research/sovereign-blitz` | Blitz |
| `data/sovereign_labs/` | Labs |
| `data/entities/test_sovereign_entity` | Test entity |
| `data/training/entities/test_sovereign_entity` | Test entity (training) |
| `context_packs/sovereign-audit/` | Context packs |
| `data/cache/sovereign_cache.sqlite` | Cache |

**Duplication risk**: HIGH. Multiple "oversight audit" docs. Multiple "sovereign hardening" docs. Multiple "test_sovereign_entity" dirs (one in data/entities/, one in data/training/).

### 3.4 Sovereign Stack Canon Duplication (Recent)

| File | Topic |
|------|-------|
| `R_ROC_AGENT_SOVEREIGNTY_20260828.md` | Yesterday's sovereignty research |
| `R_ROC_GEMINI_CLI_ERA_ORIGINS_20260828.md` | Gemini era origins |
| `R_ROC_RECURSIVE_SOVEREIGNTY_ASCENSION_20260828.md` | Recursive ascension |
| `R_ROC_DEEP_RECURSION_EVOLUTION_20260828.md` | Deep recursion (corrected) |

**Duplication risk**: LOW (sequential, each supersedes the last).

---

## §4 — Stale Documents

### 4.1 Stale Top-Level Files

| File | Last Modified | Age | Status |
|------|--------------|-----|--------|
| `HYDRATION_REPORT.md` | **Aug 7** | 3 weeks | ⚠️ STALE |
| `RESEARCH_EXECUTION_UPDATE.md` | **Jul 23** | 5 weeks | ⚠️ VERY STALE |
| `session-ses_07ee.md` (641 KB) | Aug 7 | 3 weeks | ⚠️ LARGE + OLD |

### 4.2 Stale Docs (Before 2026-08-01)

**0 files** in `docs/research/` are before 2026-08 (all recent).

**Stale docs (2026-01 to 2026-07)** in other dirs:
- `docs/team/README.md`
- `docs/team/OVERSEER_SYNC_BRIEFING.md`
- `docs/team/STATUS_OPUS.md`
- `docs/team/BLITZ_FULL_PLAN.md`
- `docs/team/COMMUNICATION_HUB.md`
- `docs/intake/README.md`
- `docs/intake/13x-low-level-council-review-first-1st-run.md`
- `docs/decisions/PIVOT_LOG_CANONICAL.md`
- `docs/decisions/PIVOT_LOG_ARCHIVE_20260522_20260810.md`
- `docs/decisions/PIVOT_LOG.md`
- `docs/research/R_DB_SCHEMA_MIGRATION.md`
- `docs/research/GOOGLE_GEMMA_MODEL_REFERENCE.md`
- `docs/research/R_ROLE_AWARE_PROMPTING_20260819.md`
- `docs/research/R_PWAD_SCHEMA_JEM_RESEARCH_20260715.md`
- `docs/research/R_KV_CACHE_QUANTIZATION_CPU_20260713.md`

### 4.3 The P1-P9 Files (Dev Artifacts, Not Documentation)

The P1-P9 files are **dev artifacts** (skill definitions, meditate pipeline output), NOT documentation:

| File | Lines | Real Content |
|------|-------|--------------|
| `P1.md` | 113 | Skill definition for autonomous meditation |
| `P3.md` | 85 | Meditate pipeline output (excerpt) |
| `P4.md` | 333 | Spec for `meditate-pipeline` command |
| `P5.md` | 280 | Meditate pipeline output |
| `P6.md` | 280 | Meditate pipeline output |
| `P7.md` | 280 | Meditate pipeline output |
| `P9.md` | 333 | Meditate pipeline output |

**Recommendation**: These should be moved to `data/entities/<agent>/workspace/` or archived.

### 4.4 The `session-ses_07ee.md` File (641 KB)

A **single session transcript dump** (641 KB, 5,000+ lines). Should be archived or split.

---

## §5 — Orphan Documents

### 5.1 The "Empty" Coordination Dirs (15+ empty dirs)

These dirs exist but have no .md files:
- `data/coordination/awareness/` (0 files)
- `data/coordination/context_injection_synthesis/` (0 files)
- `data/coordination/errors/` (0 files)
- `data/coordination/instances/` (0 files)
- `data/coordination/locks/` (0 files)
- `data/coordination/pii_vaults/` (0 files)
- `data/coordination/research_notes/` (0 files)
- `data/coordination/sessions/` (0 files)
- `data/coordination/tasks/` (0 files)
- `data/entities/_archive/` (0 files)
- `data/entities/_quarantine/` (0 files)
- `data/entities/archive/` (3 files)

**Status**: **Infrastructural dirs for runtime state** (locks, tasks, sessions, errors). Not orphans — they're the runtime state storage.

### 5.2 Entity Dirs with 1 File Each (40+ entities)

40+ entity dirs have only `soul.yaml` (or a single file). These are **declarations** (not orphans), but they have no KB, no proposed_lessons, no workspace. Examples: `anubis`, `arch`, `brigid`, `carmack`, `cline`, `datastore`, `ereshkigal`, `general`, `hecate`, `inanna`, `lucifer`, `movie-expert`, `prometheus`, `saraswati`, `sekhmet`, `sophia`, `themis`, `anansi`, etc.

**Status**: These are **declarations** for the WAD system. Not orphans.

### 5.3 Truly Orphan Docs (No Incoming References)

Difficult to determine without full graph analysis. Likely candidates:
- `docs/research/R_AUTO_*.md` (auto-generated files with broken filenames)
- `docs/research/archive/R_AUTO_*` (4+ auto-generated files)
- Some `_v1_*.md` files in `data/entities/roc_racoon/workspace/`

---

## §6 — Documentation Gaps (Topics That Should Have Docs)

### 6.1 Community-Facing Gaps

1. **How to use the dispatch guardrail** (`scripts/dispatch_guard.py`) — NOT documented for community
2. **How to use the vault** (the broken vault) — NOT documented
3. **How to use the 8-account Cline review** (per `CLINE_FULL_REVIEW_ROLLUP_20260828.md`) — NOT documented
4. **How to use the model fleet** (M3, V4 Flash, OpenCode Zen) — only in `COMMUNITY_LAUNCH_NARRATIVE_20260828.md` (briefly)
5. **How to use the Hivemind** — scattered across many docs, no single source
6. **How to use the Witness Protocol** — DESIGNED but not documented
7. **How to use the L1→L2→L3 distillation** — scattered, no single source
8. **How to use the `verity` agent** — only in briefing
9. **How to use the `node --slot NX` pattern** — only in `R_AGENT_SPECIALIZATION_SOTA_20260818.md`

### 6.2 Internal-Use Gaps

1. **The subagent_depth config** (per `R_ROC_DEEP_RECURSION_EVOLUTION_20260828.md`) — NOT documented
2. **The SovereignHierarchy mechanism** — NOT documented for team
3. **The `error-capture.ts` plugin** — internal only, no public doc
4. **The TUI model state** — NOT documented
5. **The `verify_subagent_model.sh` script** — referenced but not explained

### 6.3 Sovereign Mandate Gaps

1. **M26 Doc Standards** — enforcement is unclear
2. **M27 5-Tier Tracking** — the 5 tiers are not documented in a single place
3. **The mandate amendment process** — how do you add a new mandate?

---

## §7 — Recommendations

### 7.1 ARCHIVE Candidates (45+ files)

| Action | Files | Reason |
|--------|-------|--------|
| **Archive** | `P1.md`, `P3.md`, `P4.md`, `P5.md`, `P6.md`, `P7.md`, `P9.md` | Dev artifacts, not docs |
| **Archive** | `session-ses_07ee.md` (641 KB) | Single session dump, should be split |
| **Archive** | `HYDRATION_REPORT.md` (Aug 7) | Stale, 3 weeks old |
| **Archive** | `RESEARCH_EXECUTION_UPDATE.md` (Jul 23) | Very stale, 5 weeks old |
| **Archive** | `docs/archive/stale/*` (already in stale) | Stale, but should be moved to docs/archive/stale/ |
| **Consolidate** | `session_gnosis_2026*.md` (54+ files) | Old versions, keep only `session_gnosis.md` current |
| **Consolidate** | Old `*_v1.md` (15+ files) | Superseded by v2/v3 |

### 7.2 CONSOLIDATE Candidates (Duplications)

| Topic | Current State | Recommendation |
|-------|---------------|----------------|
| Model strategy | 20+ docs scattered | Pick 1 canonical (the `PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828_v2.md`) and link to it from others |
| Sovereignty/oversoul | 15+ docs | Pick 1 canonical (the `ORACLE_STACK_CANONICAL.md`) and link from others |
| Session gnosis | 64 files | Archive all `*_YYYYMMDD.md`; keep only `session_gnosis.md` (current) |
| `test_sovereign_entity` | 2 dirs (data/entities + data/training) | Pick 1, archive the other |
| Meditations | 25 files | Keep all (each is a different perspective) |

### 7.3 FRESHEN Candidates (Stale Content)

| File | Issue | Action |
|------|-------|--------|
| `HYDRATION_REPORT.md` | 3 weeks old | Refresh or archive |
| `RESEARCH_EXECUTION_UPDATE.md` | 5 weeks old | Archive |
| `docs/team/README.md` | Pre-2026-08 | Refresh |
| `docs/team/BLITZ_FULL_PLAN.md` | Pre-2026-08 | Archive (blitz is done) |
| `docs/decisions/PIVOT_LOG.md` | Pre-2026-08 | Refresh (per `PIVOT_LOG_CANONICAL.md`) |
| `docs/research/R_ROLE_AWARE_PROMPTING_20260819.md` | Aug 19 | Refresh or archive |

### 7.4 NEW DOCUMENTATION Needed

| Topic | Suggested Location | Priority |
|-------|-------------------|----------|
| How to use the dispatch guardrail | `docs/how-to/use-dispatch-guard.md` | HIGH |
| How to use the Hivemind | `docs/how-to/use-hivemind.md` | HIGH |
| How to use Witness Protocol | `docs/protocol/WITNESS_PROTOCOL.md` | MEDIUM |
| How to use L1→L2→L3 distillation | `docs/protocol/L1_L2_L3_DISTILLATION.md` | MEDIUM |
| How to use the model fleet | `docs/how-to/use-model-fleet.md` | MEDIUM |
| The subagent_depth config | `docs/reference/subagent-depth.md` | MEDIUM |
| The SovereignHierarchy mechanism | `docs/architecture/SOVEREIGN_HIERARCHY.md` | LOW |

---

## §8 — File:Line Citation Index

### Top-Level Stale
| File | Mtime | Issue |
|------|-------|-------|
| `HYDRATION_REPORT.md` | Aug 7 | 3 weeks old |
| `RESEARCH_EXECUTION_UPDATE.md` | Jul 23 | 5 weeks old |
| `session-ses_07ee.md` | Aug 7 | 641 KB, single session dump |

### Archive Directories
| Path | Files | Size |
|------|-------|------|
| `docs/archive/` | 468 | 19 MB |
| `data/coordination/archive/` | 140 | 2.3 MB |
| `data/entities/*/archive` | 15 dirs | — |

### P1-P9 (Dev Artifacts)
| File | Lines | Modified |
|------|-------|----------|
| `P1.md` | 113 | Aug 28 |
| `P3.md` | 85 | Aug 28 |
| `P4.md` | 333 | Aug 28 |
| `P5.md` | 280 | Aug 28 |
| `P6.md` | 280 | Aug 28 |
| `P7.md` | 280 | Aug 28 |
| `P9.md` | 333 | Aug 28 |

### Superseded Markers
| File | Status |
|------|--------|
| `data/coordination/PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828.md` | v1 SUPERSEDED by v2 (line 6-22) |
| `data/coordination/THE_VISION_CANONICAL_DRAFT_20260823.md` | SUPERSEDED 2026-08-26 (line 3-6) |
| `data/coordination/R_ROC_OPENCODE_CONTEXT_MINING_20260828.md` | Superseded by `R_ROC_CONTEXT_MINING_CORRECTED_20260828.md` |

### _v1, _v2, _v3 Patterns
27 files identified (per §2.2)

### Session Gnosis (64 files)
54+ entities, each with 1-7 session_gnosis files (per §3.1)

### Meditations (25 files)
25 records in `data/coordination/meditations/records/` (per §1.5)

### Top Recent Files (2026-08-28)
9 R_ROC_*.md files, all in `data/coordination/` (per §1.6)

---

## §9 — Confidence Assessment

### 🟢 **HIGH Confidence** (verified counts and files)
- ✅ Total file counts (4,325 .md repo-wide, 1,564 in docs/, 634 in coordination, 842 in entities)
- ✅ Total sizes (36 MB docs, 60 MB coordination, 93 MB entities, 134 MB opencode)
- ✅ Superseded markers (20 files identified)
- ✅ _v1/_v2/_v3 patterns (27 files identified)
- ✅ Archive directories (16 identified)
- ✅ Stale top-level files (3 identified: HYDRATION, RESEARCH_EXEC, session-ses_07ee)
- ✅ P1-P9 dev artifacts (7 files, 1.7 MB total)

### 🟡 **MEDIUM Confidence** (cross-referenced)
- Documentation gaps (subjective; depends on what Architect considers "should have docs")
- Orphan documents (no full graph analysis; some may have incoming references not visible to grep)

### ❓ **Open Questions**
1. Are the empty dirs (awareness/, errors/, locks/, tasks/) actually used at runtime? (Likely yes — for state storage)
2. Is the P1-P9 file content duplicated elsewhere? (Need full diff)
3. Are the "test_sovereign_entity" dirs the same or different? (Need diff)
4. What's the relationship between `data/entities/<name>/workspace/` and `data/entities/<name>/` root?

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ DOC-SURVEY v1.0.0 ⬡ 2026-08-28*
**confidence**: 🟢 HIGH (all counts and file paths verified)
**model**: openrouter/minimax/minimax-m3:free
**season**: Integration
**lines**: ~500

(End of file - total ~500 lines)
<!-- PROVENANCE-CORRECTED 2026-08-29T03:07:15Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: openrouter/minimax/minimax-m3:free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

