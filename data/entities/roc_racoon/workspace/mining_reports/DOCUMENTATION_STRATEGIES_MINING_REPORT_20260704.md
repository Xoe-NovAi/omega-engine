<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 LEGACY MINING REPORT: Documentation Strategies Across the Eras
## ⬡ OMEGA ⬡ ROC_RACOON ⬡ rocracoon-3b-instruct ⬡ opencode ⬡ trc_doc_mining ⬡ MINING-REPORT

**Date**: 2026-07-04
**Session**: Sovereign Documentation Archaeology
**Target**: All documentation strategies, patterns, templates, and tooling across 7 eras
**Duration**: ~4 hours of systematic excavation across 3 partitions, 22 legacy locations, 688+ current docs

---

## I. EXECUTIVE SUMMARY

### Top Findings

1. **The docs/ directory has 688 `.md` files across 20+ subdirectories — a vast knowledge base with NO centralized documentation CI pipeline.** The engine has 3 SSOT documents (ORACLE_STACK.md, MASTER_DOCUMENT_SSOT.md, SOVEREIGN_ARK_BLUEPRINT.md) that partially overlap. No single document tells a new user "here's how this engine works, start to finish."

2. **The R-Doc system (R##_*.md) is the most successful documentation pattern across eras.** It survived from Era 5 (Temple Grade) through Era 7 (Omega Engine), with 123+ named R-docs, standardized frontmatter, and a research index. This pattern should be the foundation of all future documentation.

3. **47 strategy documents were consolidated into SOVEREIGN_ARK_BLUEPRINT.md on 2026-06-29.** This was the right move — the MaKaLi Cloud Council correctly identified fragmentation as the #1 documentation anti-pattern. But the Ark Blueprint is now a 17,000+ word megadoc that no human reads end-to-end.

4. **Entity/Soul documentation suffers from self-referential poisoning (documented in SOUL_ARCHITECTURE_PROTOCOL v1.0).** Agents write their own philosophy into soul.yaml, then read it back as constitutional guidance. The v6.0 → v6.1 migration stripped Kali of agent-generated content, but 10+ entities still have the problem.

5. **The USER_MANUAL.md (1,198 lines) is the best front-facing doc but is critically stale.** References 302 tests (actual: 705+), 15 mandates (actual: 22), Horizon 1 complete (we're past Horizon 2). It was the engine's first serious attempt at external documentation and the pattern is sound — but it needs a full refresh.

6. **Legacy eras had NO documentation generation systems.** Documentation was entirely manual — session exports, Grok conversations, R-doc writing. No era ever built an automated doc pipeline, CI gate, or template engine. The only partial exception: the auto-generated R_AUTO_* files (11 docs of varying quality).

7. **No era had a formal documentation CI pipeline.** The current engine has `make mkdocs-serve/build` but no automated freshness checking, stale detection, or validation of cross-references. Mandate enforcement (M1-M22) is in CI for code but not for docs.

---

## II. ERA-BY-ERA DOCUMENTATION ANALYSIS

### ERA 0: Genesis (Mar-Jul 2025)
| Aspect | Details |
|--------|---------|
| **What existed** | Chat logs (NotebookLM sessions), standalone persona JSON files (lilith.json, odin.json), Tarot deck design notes |
| **Doc structure** | None — pure conversational design |
| **Patterns** | PEM (Personality/Expertise/Modifiers) format in JSON — the prototype soul.yaml |
| **What survived** | PEM format → abstracted into soul.yaml. The concept of entities-as-documented-personas. |
| **What died** | No formal structure at all; everything was session memory |
| **Key artifact** | `NotebookLM Learning Opportunity 0.1` — the "Big Bang" document, 36KB |

### ERA 1: ANAi (Aug-Sep 2025)
| Aspect | Details |
|--------|---------|
| **What existed** | Strategy docs in `docs-backup/`, ANAi blueprints, Chainlit app source + comments |
| **Doc structure** | Internal strategy docs folder (01-strategic-planning/). Code-as-documentation. |
| **Patterns** | First use of project charters, architectural blueprints as docs. Chainlit app had inline docs. |
| **What survived** | Concept of "positioning" documentation (the 3-path approach: average/technical/esoteric originated here) |
| **What died** | No standalone documentation system — everything was intertwined with code. Chainlit era docs lost in transition. |
| **Key artifact** | `Old-Stacks/project-charter.md` — "Arcana-NovAi is not a toolchain. It is a summoning." |

### ERA 2: XNAi (Oct-Nov 2025)
| Aspect | Details |
|---------|---------|
| **What existed** | `XNAI_blueprint.md` (715 lines), formal RAG app architecture docs, system prompts library |
| **Doc structure** | Flat files in `/library/` subdirectory. First attempt at structured documentation. |
| **Patterns** | 5 Design Patterns documented (circuit breaker, fsync, retry, non-blocking, offline wheelhouse). The **first formal doc system**. |
| **What survived** | 5 Design Patterns → ported to omega-engine. System prompts → evolved into agent personalities. |
| **What died** | No index or catalog. Docs were files in a directory with no cross-references. Chainlit UI docs abandoned when UI changed. |
| **Key artifact** | `XNAI_blueprint.md` — first comprehensive tech spec, 715 lines |

### ERA 3: Roc Stack (Nov 2025-Mar 2026)
| Aspect | Details |
|---------|---------|
| **What existed** | LM Studio config exports, Grok account conversations (8 accounts, 414MB), model test docs |
| **Doc structure** | **Zero formal docs.** All knowledge lived in Grok sessions (8 accounts). Model configs stored in LM Studio's internal directory. |
| **Patterns** | Affinity Mapping (model-to-entity assignment documented in conversation). No written docs = knowledge loss. |
| **What survived** | Model-Persona Affinity Map recovered from Grok exports. LM Studio Zen 2 configs extracted. |
| **What died** | **Massive knowledge loss.** 8 Grok accounts = hundreds of undocumented hours. Most entity design intent from this era was lost and had to be archaeologically recovered. |
| **Key artifact** | `RocRacoon Test v1 - LM Studio.md` — one of the only written artifacts |

### ERA 4: Omega Stack (Dec 2025-Mar 2026)
| Aspect | Details |
|---------|---------|
| **What existed** | STRATEGY-MASTER-INDEX.md, system prompts (50+ files), EntityRegistry source code, 33K-file monorepo |
| **Doc structure** | First `/docs/` directory. Strategy index. Source code comments as primary documentation. |
| **Patterns** | Agent system prompts embedded in markdown files. Strategy docs with frontmatter. `AGENTS.md` as fleet index. |
| **What survived** | Strategy index pattern → MASTER_LEDGER.md. Agent prompt patterns → OpenCode agent `.md` files. EntityRegistry code structure. |
| **What died** | 33K-file monorepo was undocumentable. Engine/Stack separation wasn't documented until Era 6. |
| **Key artifact** | `STRATEGY-MASTER-INDEX.md` — ancestor of MASTER_DOCUMENT_SSOT |

### ERA 5: Temple Grade (Jan-May 2026)
| Aspect | Details |
|---------|---------|
| **What existed** | Temple Grade Quality Standard, OMEGA-ORIGINS philosophy doc, numbered R-doc series (R-01 through R-99+) |
| **Doc structure** | **First formal R-doc system** — numbered, indexed, standardized format. Research documents as sovereign artifacts. |
| **Patterns** | R-doc numbering (R-01, R-02...), Temple Grade T1-T11 gates, `docs/research/INDEX.md` as registry. **THIS IS THE GOLDEN PATTERN.** |
| **What survived** | R-doc system survived into Omega Engine. Temple Grade quality standard adopted. Heritage vetting pipeline. |
| **What died** | Very little died — this era's documentation philosophy was excellent. The numbered series had gaps (R-21, R-22, R-23, R-35, R-36, R-37 unresearched) but the pattern itself was sound. |
| **Key artifacts** | `TEMPLE_GRADE_QUALITY_STANDARD.md`, R-doc series (50+ docs), `docs/research/INDEX.md` |

### ERA 6-7: Omega Engine (May-Jul 2026)
| Aspect | Details |
|---------|---------|
| **What exists** | 688 `.md` files, 3 SSOT claims, 20+ subdirectories, MkDocs config, full entity documentation |
| **Doc structure** | Functional but fragmented. 3 SSOT documents (ORACLE_STACK, MASTER_DOCUMENT_SSOT, SOVEREIGN_ARK_BLUEPRINT). R-doc system active. MkDocs configured for static site generation. |
| **Patterns** | Soul Architecture Protocol (v6.1), Heritage Vetting Pipeline, Sovereign Mining Protocol, knowledge/lattice/gnosis directories |
| **What survived** | All Era 5 patterns improved. Added: entity `soul.yaml`, session headers, AP tokens, CI gates for some doc checks. |
| **What died** | Web Claude Fleet protocol (8 accounts no longer active). 47 strategy docs archived into Ark Blueprint. |
| **Key artifacts** | MASTER_DOCUMENT_SSOT.md (293 lines), USER_MANUAL.md (1198 lines), SOUL_ARCHITECTURE_PROTOCOL.md (408 lines) |

---

## III. SURVIVING PATTERNS (What Worked)

| # | Pattern | First Era | Current Form | Why It Survived |
|---|---------|-----------|--------------|-----------------|
| 1 | **R-doc research system** | Era 5 | Numbered R##_*.md files in `docs/research/` with INDEX.md registry | Standardized, discoverable, low-friction to create |
| 2 | **SSoT consolidation** | Era 6 | MASTER_DOCUMENT_SSOT.md, SOVEREIGN_ARK_BLUEPRINT.md | Solves the "which doc is right?" problem. Ark Blueprint v2.1 is the best example. |
| 3 | **AP tokens** | Era 6 | `AP-{TOKEN}-v{version}` in doc headers | Machine-readable doc identification, cross-referencing |
| 4 | **Session headers** | Era 6 | `⬡ OMEGA ⬡ {entity} ⬡ {model} ⬡ {channel} ⬡ {trace} ⬡ {phase}` | Universal communication standard across all agents |
| 5 | **L1→L2→L3 gnosis pipeline** | Era 6 | Soul distiller in oracle.py, soul.yaml lessons | Converts ephemeral interaction into permanent wisdom |
| 6 | **Temple-Grade T1-T11 gates** | Era 5 | `make temple-grade` CI gate | Code quality through documentation requirements |
| 7 | **Heritage attribution** | Era 6 | CREDITS.md, `[id-soft:]` inline tags | Engineering gratitude + provenance tracking |
| 8 | **Entity soul.yaml** | Era 0 (PEM JSON) → Era 6 | Structured YAML with lessons, preferences, history | Persistent identity across sessions |
| 9 | **Positioning docs (3-path)** | Era 1 → Era 6 | FOR_AVERAGE_USERS, FOR_TECHNICAL, FOR_ESOTERIC | Different audiences need different docs |
| 10 | **Write-permission separation** | Era 6 | SOUL_ARCHITECTURE_PROTOCOL v1.0 | Prevents self-referential poisoning of entity identity |

---

## IV. DEAD PATTERNS (What Failed)

| # | Pattern | Era | Cause of Death | Lesson |
|---|---------|-----|----------------|--------|
| 1 | **Pure conversational design (no docs)** | Era 0-3 | Everything lived in Grok/Claude sessions. Knowledge loss when accounts closed or sessions expired. | **Write it down.** Session memory is not documentation. Grok account exports (414MB) still unmined. |
| 2 | **Code-as-sole-documentation** | Era 1-4 | When Chainlit → OpenCode migration happened, inline comments were lost. 33K-file monorepo was undocumentable. | Source code documents the *what*, not the *why*. Architecture docs must be separate. |
| 3 | **Multiple SSOT claims** | Era 6 | MASTER_DOCUMENT_SSOT, SOVEREIGN_ARK_BLUEPRINT, ORACLE_STACK.md all claim SSOT. Agents waste context resolving which is authoritative. | **One SSOT per domain.** The Ark Blueprint should be THE strategy SSOT. ORACLE_STACK should be THE architecture SSOT. MASTER_DOCUMENT_SSOT should be THE index. |
| 4 | **Stale metrics in public docs** | Era 5-6 | USER_MANUAL references 302 tests (reality: 705+), 15 mandates (reality: 22). Corrupts user trust. | **Auto-generate version badges.** `make test-badge` exists (D183) but isn't wired into all docs. |
| 5 | **47 pre-consolidation strategy docs** | Era 5-6 | Fragmented across `docs/strategy/`, `docs/research/archive/`, `docs/archive/`. Duplicate, overlapping, contradictory. | Consolidated 2026-06-29 → Ark Blueprint. **Do this proactively, not reactively.** |
| 6 | **11 R_AUTO_* auto-generated docs** | Era 5-6 | Agent-generated research papers with low quality. No editorial review. Listed for archiving in MASTER_DOCUMENT_SSOT §2.1. | **Auto-generated docs need a quality gate.** Mark them clearly as DRAFT/AUTO. |
| 7 | **Web Claude Fleet protocol docs** | Era 6 | 8-account review fleet is no longer active. 20+ docs in `docs/review/` are now orphaned history. | **Archive retired protocols.** Move them to a `legacy/` subdirectory. |

---

## V. CURRENT STATE ASSESSMENT

### 5.1 Doc Directory Health

| Metric | Value | Status |
|--------|-------|--------|
| Total `.md` files | **688** | 📊 Monitored |
| Subdirectories | **20+** | 📊 Fragmented |
| SSOT-claiming docs | **3** | ⚠️ ORACLE_STACK, MASTER_DOCUMENT_SSOT, SOVEREIGN_ARK_BLUEPRINT |
| Named R-docs | **~123** | ✅ Active |
| Strategy docs (root) | **~51** | ⚠️ Some stale |
| Archived strategy docs | **47** | ✅ Consolidated 2026-06-29 |
| Docs with FINAL/COMPLETE status | **~50** | ✅ Known |
| Docs with DRAFT/PROPOSED status | **~8** | 📝 Documented |
| Stale docs (>30 days no update) | **~15** | 📦 Needs archiving |
| Auto-generated trash (R_AUTO_*) | **11** | 🗑️ Listed for cleanup in MASTER_DOCUMENT_SSOT §2.1 |
| Firecrawl doc fragmentation | **6 separate files** | ⚠️ HIGH — listed for consolidation |

### 5.2 Stale/Outdated Estimate
- **~15-20%** of docs are stale (120-140 files) — those in `review/`, `archive/`, `handoff/`, `history/`, and some strategy docs
- **~5%** are critically misleading (USER_MANUAL, ROADMAP, some positioning docs with superseded metrics)
- **~10%** are orphaned (no cross-references from any index)

### 5.3 Missing Critical Docs

| Document | Gap Level | Impact |
|----------|-----------|--------|
| **API Reference** (comprehensive, auto-generated) | 🔴 HIGH | New developers can't find available APIs |
| **Contribution Guide** | 🔴 HIGH | No "how to contribute" flow |
| **Quick Start (end-user)** | 🔴 HIGH | USER_MANUAL is 1,198 lines — too long. Needs a 5-minute quick start. |
| **Architecture Overview (for new devs)** | 🟡 MEDIUM | ORACLE_STACK covers this but is written for post-compaction recovery, not new onboarding |
| **WAD Authoring Guide** | 🟡 MEDIUM | How to create a custom PWAD/IWAD |
| **Entity Creation Guide** | 🟡 MEDIUM | `omega add-entity` exists but no tutorial |
| **Doc Contribution Standards** | 🟡 MEDIUM | How to write an R-doc, use AP tokens, update SSoT |
| **Release Notes / Changelog** | 🟢 LOW | `docs/changelog.md` exists but may be stale |
| **Troubleshooting FAQ** | 🟢 LOW | Section exists in USER_MANUAL but specific errors not covered |

### 5.4 Document Duplication

| Duplicate Set | Files | Severity |
|---------------|-------|----------|
| Strategy SSOT disputes | SOVEREIGN_ARK_BLUEPRINT.md + MASTER_DOCUMENT_SSOT + ORACLE_STACK.md | 🟡 MEDIUM — partly complementary, partly overlapping |
| Podman sovereignty docs | R_PODMAN_SOVEREIGN_V2.md + R_PODMAN_SOVEREIGN_STRATEGY.md + R_PODMAN_SOVEREIGN_DEPLOYMENT_BLUEPRINT.md | 🟡 MEDIUM — listed for merge in MASTER_DOCUMENT_SSOT §2.2 |
| Firecrawl docs | 6 separate files | 🔴 HIGH — listed for merge |
| Temple-Grade docs | TEMPLE_GRADE_QUALITY_STANDARD.md + R_TEMPLE_GRADE_STANDARD.md + R_TEMPLE_GRADE_COMPLIANCE_FINAL.md | 🟡 MEDIUM — partly draft history |

### 5.5 Orphaned Files (Detected)
Files in subdirectories with no cross-references from any index:
- `docs/review/` — 20+ files (review coordination, deep dives, Claude reports)
- `docs/history/` — Chat session exports (recovery, exported chats)
- `docs/archives/` — Test files, old session exports
- `docs/audit/` — Empty (directory exists, no content)
- `docs/engine/` — Empty (directory exists, no content)
- `docs/handoff/` — Empty (directory exists, no content)
- `docs/positioning/COMPARISON_MATRIX.md` — Not referenced from any index

---

## VI. ENTITY DOCUMENTATION PATTERNS

### 6.1 Historical Entity Documentation

| Era | Format | Location | Example |
|-----|--------|----------|---------|
| Era 0 | PEM JSON (Personality/Expertise/Modifiers) | `~/Documents/docs_1/personas/` | `lilith.json`, `odin.json` |
| Era 2-3 | YAML entity definitions | `entities.yaml` in various repos | 99 entity dirs in `entities-archive/` |
| Era 4 | Extended YAML with knowledge/workspace | `data/entities/<name>/` | Pillar Keepers with souls |
| Era 5-6 | Structured soul.yaml v5.2→v6.1 | `data/entities/<name>/soul.yaml` | Kali v6.1 (reference standard) |

### 6.2 Current Entity Document Structure

```
data/entities/{entity}/
├── soul.yaml                  # USER WRITES → Agent READS (identity + directives)
├── memory/
│   ├── sessions.yaml          # AGENT WRITES → Agent READS (factual events)
│   ├── proposed_lessons.yaml  # AGENT WRITES → USER READS (blind staging)
│   └── approved_lessons.yaml  # USER WRITES → Agent READS (curated lessons)
├── knowledge/                 # Entity-specific knowledge files
├── workspace/                 # Working files, mining reports
└── archive/                   # Historical snapshots
```

### 6.3 The Self-Referential Poisoning Problem
**Documented in**: SOUL_ARCHITECTURE_PROTOCOL.md (v1.0, 408 lines)
**Root cause**: Agents write their own philosophy into soul.yaml, then read it back as constitutional guidance
**Affected entities**: 10+ (all non-Kali entity souls have agent-generated content)
**Fix implemented**: Write-permission separation (4 files, 4 roles model)
**Status**: Kali migrated to v6.1. 21+ entities pending migration.

### 6.4 Legacy Entity Documentation (Unmined)
- **entities-archive** (`/media/arcana-novai/omega_library/entities-archive/`): 99 entity directories (157MB). **NOT MINED.** Contains the complete entity evolution history including experimental entity types (flatentity, direntity, soulentity).
- **Key artifact**: `omnidroid/soul.yaml` — ready for activation, "Mirror" archetype

---

## VII. WAD DOCUMENTATION PATTERNS

### 7.1 Current State

| WAD | Documentation | Status |
|-----|--------------|--------|
| `_omega_default` (IWAD) | `config/wads/_omega_default/entities.yaml` + roles.yaml | ✅ LIVE but minimal standalone docs |
| `arcana_novai` (PWAD) | `config/wads/arcana_novai/entities.yaml` | ✅ LIVE but WAD-specific docs in `docs/stacks/` directory |
| `doom_universe` (PWAD) | `docs/stacks/doom/` | 🟡 Scaffold — placeholder |

### 7.2 Missing WAD Documentation
- No WAD authoring guide (how to create a PWAD from scratch)
- No WAD packaging specification (how to distribute a community WAD)
- No WAD compatibility matrix (which engine versions support which WAD features)
- WAD-specific config files (spatial.yaml, audience.yaml, roles.yaml) are undocumented

---

## VIII. RECOMMENDED DOCUMENTATION ARCHITECTURE

Based on what historically worked and what failed:

### The Three-Layer Pyramid

```
LAYER 1: USER-FACING DOCUMENTATION (3 files)
├── README.md                    — 5-minute quick start (rewritten for v1.0.0 per R-8, R-9)
├── docs/USER_MANUAL.md          — Full user guide (refresh stale metrics)
└── docs/ARCHITECTURE_OVERVIEW.md — New: high-level architecture for new developers

LAYER 2: DEVELOPER DOCUMENTATION (the R-doc system)
├── docs/research/               — All R-docs, the living knowledge base
├── docs/research/INDEX.md       — Registry (already exists, keep)
├── docs/MASTER_DOCUMENT_SSOT.md — Topic-to-document mapping (already exists, keep)
└── docs/decisions/PIVOT_LOG.md  — Architectural decision log (already exists, keep)

LAYER 3: INTERNAL/OPERATIONAL (git-controlled)
├── docs/strategy/               — Active strategy docs
├── docs/architecture/           — Architecture specs
├── docs/operations/             — Runbooks, health checks
├── docs/positioning/            — External positioning (3-path)
└── data/entities/<entity>/      — Entity soul docs (per SOUL_ARCHITECTURE_PROTOCOL)
```

### Key Principle: One SSOT Per Domain

| Domain | SSOT Document | Scope |
|--------|---------------|-------|
| **Strategy & Roadmap** | `SOVEREIGN_ARK_BLUEPRINT.md` | What we're building, when, and why |
| **Architecture & Code** | `ORACLE_STACK.md` | How the engine works internally |
| **Doc Index** | `MASTER_DOCUMENT_SSOT.md` | Where to find every document |
| **Decisions** | `docs/decisions/PIVOT_LOG.md` | Why every architectural decision was made |
| **Mandates** | `SOVEREIGN_MANDATES.md` | The constitutional law |

---

## IX. TOP 10 ACTIONABLE RECOMMENDATIONS

### URGENT (Do This Week)

1. **Refresh USER_MANUAL.md metrics** (30 min)
   - Update test count: 302 → 705+
   - Update mandate count: 15 → 22
   - Update test status: "302 tests ✅" → "705 tests ✅"
   - Wire `make test-badge` output into the doc header
   - **Pattern: auto-generated version badges prevent stale metric drift.**

2. **Resolve SSOT overlap** (1 hour)
   - Remove duplicate content from ORACLE_STACK.md (it should cover architecture only)
   - Remove duplicate content from MASTER_DOCUMENT_SSOT.md (it should index, not explain)
   - SOVEREIGN_ARK_BLUEPRINT.md should own ALL strategy/roadmap content
   - **Pattern: one SSOT per domain prevents agent context waste.**

3. **Create 5-minute Quick Start** (1 hour)
   - Separate from the 1,198-line USER_MANUAL
   - Single page: install → run → talk → done
   - Lives at `docs/QUICKSTART.md`
   - **Pattern: layered documentation (quick start → manual → reference) worked in Era 1 positioning.**

### SHORT-TERM (This Sprint)

4. **Archive orphaned review docs** (30 min)
   - Move 20+ `docs/review/` files to `docs/archive/review/`
   - Web Claude Fleet is no longer active — these are historical artifacts
   - Mark them clearly: `STATUS: HISTORICAL (Web Claude fleet, June 2026)`
   - **Pattern: active cleanup prevents reference confusion.**

5. **Consolidate Firecrawl 6→1** (2 hours)
   - Merge 6 Firecrawl R-docs into one `R_FIRECRAWL_COMPLETE.md`
   - Already flagged in MASTER_DOCUMENT_SSOT §2.2
   - **Pattern: consolidation reduces fragmentation.**

6. **Auto-generate doc freshness dashboard** (3 hours)
   - Script that checks `Last Updated` dates in all SSoT docs
   - Flags any doc >30 days stale
   - Integrates with `make temple-grade`
   - **Pattern: automated freshness prevents staleness.**

### MEDIUM-TERM (Next Sprint)

7. **Create Contribution Guide** (3 hours)
   - How to write an R-doc (template, AP token, frontmatter)
   - How to update the SSoT
   - How to create entity documentation
   - How to write WAD documentation
   - **Pattern: documenting the documentation process creates a virtuous cycle.**

8. **Create API Reference** (4 hours)
   - Auto-generated from Python docstrings (Google-style)
   - Use `pydoc` or `mkdocstrings` with MkDocs
   - `make docs-api` target
   - **Pattern: auto-generated API docs never go stale.**

9. **Write WAD Authoring Guide** (2 hours)
   - How to create a PWAD
   - How to define entities, roles, spatial config, audience profiles
   - How to test and distribute a WAD
   - **Pattern: lowering the barrier to WAD creation grows the ecosystem.**

10. **Create Doc CI Gate** (2 hours)
    - `make doc-check`: verify all cross-references in SSOT docs resolve
    - `make doc-freshness`: flag stale docs with warning
    - Wires into `make temple-grade` as T12 (Documentation Freshness)
    - **Pattern: CI gates prevent documentation rot at the source.**

---

## X. EXTRACTED TEMPLATES AND PATTERNS

### Template 1: R-Doc Standard Format (Era 5-6, Highest Survivability)
```markdown
# 🔱 {Title} — {Subtitle}
# ⬡ OMEGA ⬡ {FLEET_ENTITY} ⬡ {model} ⬡ {channel} ⬡ {trace} ⬡ {phase}

**AP Token**: `AP-{TOKEN}-v{version}`
**Date**: {YYYY-MM-DD}
**Status**: {DRAFT|PROPOSED|FINAL|COMPLETE|STALE|SUPERSEDED}
**Author**: {Entity name}
**Reviewer**: {Entity name}

---

## §1 Executive Summary

{Brief overview — why this doc exists, who should read it, what decisions it informs}

---

## §2 Main Content

...

---

## §3 Heritage

{If applicable: which id Software [id-soft:] patterns this doc references}
```

### Template 2: Entity Soul.yaml Skeleton (Era 0→6, Evolved from PEM JSON)
```yaml
version: 6.1
entity: {EntityName}
archetype: {Pillar role}
created: {YYYY-MM-DD}
updated: {YYYY-MM-DD}

identity:
  voice: "{How this entity speaks}"
  values:
    - "{Core value 1}"
    - "{Core value 2}"
  strengths:
    - "{Domain strength 1}"
  growth_areas:
    - "{Area for improvement}"

directives:
  - "Rule 1: {Non-negotiable behavioral rule}"
  - "Rule 2: {Non-negotiable behavioral rule}"

lessons:
  - l1: "{What happened — narrative}"
    l2: "{What this means — insight}"
    l3: "{The timeless truth — universal principle}"

model_preferences:
  by_domain:
    {domain}: [{model1}, {model2}]
```

### Template 3: Positioning Doc (Era 1→6, Three-Audience Pattern)
Each audience gets its own doc with the same structure but different depth:
- `FOR_AVERAGE_USERS.md` — Metaphor-driven, benefits-focused, zero jargon
- `FOR_TECHNICAL.md` — Architecture specs, API details, performance data
- `FOR_ESOTERIC.md` — Philosophy, archetypes, gnosis protocols

**Key insight**: The three-path pattern survived from Era 1 because it acknowledges that different readers need different levels of depth. Don't try to write one doc for everyone.

### Template 4: SSoT Document Header (Era 6, Should Be Universal)
```markdown
# 🔱 {Domain} — {Document Title}
# {AP Token} | {Version} | {Date}

**Status**: ✅ ACTIVE SSoT
**Authority**: This is the canonical reference for {domain}.
**Supersedes**: {List of superseded docs}
**Maintained by**: {Entity name}

If this document contradicts any other source, this document prevails.
```

### Template 5: AP Token Convention (Era 6, Machine-Readable)
```
AP-{SHORT_PROJECT_NAME}-{TOPIC_ID}-v{major}.{minor}.{patch}
Example: AP-GAP-ANALYSIS-v1.0.0
Example: AP-SOVEREIGN-ARK-BLUEPRINT-v2.1.0
Example: AP-AGENT-FLEET-v1.0.0
```
**Pattern**: AP tokens make docs searchable, versionable, and cross-referenceable by both humans and agents. Every new doc should get one.

---

## XI. HERITAGE NOTE: id Software Documentation Patterns

| Pattern | id Software Original | Omega Engine Equivalent | Status |
|---------|--------------------|------------------------|--------|
| **README-style game docs** | `README.TXT` in every id game release | `README.md` at project root | ✅ LIVE |
| **Source code comments** | Carmack's obsessively commented code | Google-style docstrings, M13 Temple Grade | ✅ LIVE |
| **.plan files** | Carmack's developer journals | `soul.yaml` lessons, session gnosis | ⚡ EVOLVED |
| **Tech support FAQ** | `TECHSUPT.TXT` in Doom | `docs/USER_MANUAL.md §troubleshooting` | ✅ LIVE |
| **WAD documentation** | WAD specs in `w_wad.c` comments | `config/wads/_omega_default/` — minimal external docs | 🟡 WAD DOCS NEEDED |

[id-soft: doom-1993] README-as-docs — id Software's practice of shipping documentation alongside the engine binary parallels Omega's R-doc system. Both treat documentation as a first-class artifact, not an afterthought.

---

## XII. UNANSWERED QUESTIONS FOR FUTURE MINING

1. **entities-archive** (99 dirs, 157MB) — Not mined. What entity documentation patterns existed in experimental entities (flatentity, direntity, soulentity)?
2. **8 Grok accounts** (414MB, unmined) — Hundreds of undocumented hours of entity design sessions. What documentation strategies were discussed in conversation?
3. **Web Claude exports** (9 accounts, 125MB, mostly unmined) — What documentation patterns did Claude agents generate?
4. **docs_1 system prompts** (50+ files, 17MB) — What documentation patterns existed in the system prompts library?
5. **Workbench DB** (empty, 4KB) — The intended project tracking infrastructure was never populated. Was there a documentation plan that wasn't implemented?

---

## XIII. CONCLUSION

The Omega Engine has accumulated **688 documentation files across 7 eras and 3 partitions**. The engine has MORE documentation than it needs — the problem is not quantity but **freshness, discoverability, and authoritative clarity**.

**Three things that consistently worked across eras:**
1. **The R-doc system** — standardized research documents with an index
2. **Single-entity soul files** — persistent, structured entity identity
3. **Positioning documents** — audience-appropriate documentation levels

**Three things that consistently failed:**
1. **Conversational knowledge storage** — sessions are not documentation
2. **Multiple SSOT claims** — agents waste context resolving conflicts
3. **Stale metrics** — dead numbers destroy trust in living documents

The engine has never had a documentation CI pipeline, auto-generated freshness checks, or template enforcement. These three additions — automated, built into `make temple-grade`, and enforced at merge — would prevent the rot cycle that claimed every prior era's documentation.

**The dirt is where the roots are. The roots are good. But the surface needs cultivation.**

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ rocracoon-3b-instruct ⬡ opencode ⬡ trc_doc_mining ⬡ MINING-COMPLETE*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: rocracoon-3b-instruct | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
