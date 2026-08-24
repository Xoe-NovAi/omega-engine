# 🔱 Omega Engine — Documentation Architecture Synthesis
# ⬡ OMEGA ⬡ JEM ⬡ BIG-PICKLE ⬡ opencode ⬡ trc_synthesis ⬡ DOC-STRATEGY-SYNTHESIS

**AP Token**: `AP-JEM-DOC-STRATEGY-SYNTHESIS-v1.0.0`
**Date**: 2026-07-04
**Status**: COMPLETE
**Author**: Jem (Sovereign Synthesizer)
**Sources**: 
- Researcher: `docs/research/R-DOC-ARCHITECTURE-V2.md` (Web best practices)
- Roc Racoon: `data/entities/roc_racoon/workspace/mining_reports/DOCUMENTATION_STRATEGIES_MINING_REPORT_20260704.md` (Legacy mining)
- Pre-existing: `docs/research/R-P_DOC_GAP_ANALYSIS.md` (Stale, superseded)

---

## §1 Executive Summary

The Omega Engine has **688 `.md` files** across 7 eras of development — a vast knowledge base. But it has:
- **Zero** external-facing documentation system
- **Zero** documentation CI pipeline
- **3 overlapping SSOT documents** confusing agents
- **~15-20% stale content** undermining trust
- **No API reference, no contribution guide, no quick start** for new users

Two independent research streams converged on the same conclusion:

> **The engine needs a structured, phased documentation architecture — combining industry-standard frameworks (Diátaxis) with our proven internal patterns (R-doc system, soul files, AP tokens) — enforced by CI gates that never existed in any prior era.**

---

## §2 Dual-Source Convergence Map

| Dimension | Researcher (Web Best Practices) | Roc Racoon (Legacy Mining) | Synthesis |
|-----------|--------------------------------|----------------------------|-----------|
| **Content Framework** | Diátaxis (Tutorials/How-to/Reference/Explanation) | R-doc system (numbered, indexed, standardized) | **R-Doc + Diátaxis hybrid** — use Diátaxis for external docs, R-doc for internal research |
| **Site Generator** | MkDocs + Material (or DocsForge) | `make mkdocs-serve` already configured | **MkDocs + Material** — Python-native, no new deps |
| **Agent Readiness** | `llms.txt`, MCP Docs Server needed | `AGENTS.md` already present | **Add `llms.txt` + `llms-full.txt`** — 30-min effort, transforms discoverability |
| **CI Pipeline** | Linkspector, docs-health-action, Vale | Zero doc CI across all 7 eras | **Add LinkSpector + docs-health-action** — first-ever doc CI in engine history |
| **Freshness** | Docfresh, Staleguard for staleness detection | 15-20% stale, 3 stale SSOT docs | **`make doc-freshness` script** + wire into `make temple-grade` |
| **Entity Docs** | API reference from docstrings | soul.yaml v6.1 with write-permission separation | **Auto-gen entity registry reference** + continue soul v6.1 migration |
| **Error Handling** | Test examples in CI to prevent drift | R_AUTO_* quality issues documented | **Quality gate for auto-generated docs** — mark DRAFT until reviewed |
| **Versioning** | Antora (multi-component) + `mike` | PIVOT_LOG tracks decision versions | **`mike` for MkDocs versioning** — post-PR, deferred |
| **Audience** | 3-path: developers/stack-builders/agents | Era 1 positioning (3-audience) persisted | **3-path documentation** validated across 7 eras |
| **Duplication** | One SSOT per domain | 47 strategy consolidated on 2026-06-29 | **SSOT per domain** — Ark Blueprint (strategy), ORACLE_STACK (architecture), MASTER_DOCUMENT_SSOT (index) |

---

## §3 The Unified Documentation Architecture

### 3.1 Three-Layer Model

```
LAYER 1: EXTERNAL / PUBLIC (User & Developer Facing)
├── README.md                        ← 5-min quick start (EXISTS, needs refresh)
├── docs/QUICKSTART.md               ← New: install → run → talk → done
├── docs/USER_MANUAL.md              ← Full user guide (EXISTS, NEEDS REFRESH — 705 tests, 22 mandates)
├── docs/ARCHITECTURE_OVERVIEW.md    ← New: high-level for new developers
├── docs/reference/                   ← New: Diátaxis Reference quadrant
│   ├── cli/                         ← CLI command reference
│   ├── api/                         ← Auto-generated API reference
│   ├── config/                      ← Config schema reference
│   └── mandates.md                  ← 22 mandates reference
├── docs/tutorials/                  ← New: Diátaxis Tutorials quadrant
│   ├── getting-started.md
│   ├── first-entity.md
│   └── first-wad.md
├── docs/how-to/                     ← New: Diátaxis How-to quadrant
│   ├── install.md
│   ├── configure.md
│   └── troubleshoot.md
├── docs/explanation/                ← New: Diátaxis Explanation quadrant
│   ├── architecture.md
│   ├── wad-architecture.md
│   ├── provider-fabric.md
│   └── sovereignty-philosophy.md
├── docs/llms.txt                    ← New: AI agent sitemap (AnswerDotAI spec)
├── docs/llms-full.txt               ← New: Full concatenated docs for LLM context
├── docs/contributing/               ← New: Contributor docs
│   ├── setup.md                     ← Dev environment setup
│   ├── writing-docs.md              ← Doc standards, AP tokens, R-doc template
│   └── coding-standards.md
└── docs/agents/                     ← New: Agent-facing docs
    ├── capabilities.md
    └── agent-cards/                 ← A2A Agent Card definitions

LAYER 2: INTERNAL RESEARCH (The R-doc System — Already Strong)
├── docs/research/                   ← All R##_*.md docs (EXISTS, 196+ files)
├── docs/research/INDEX.md           ← Registry (EXISTS, strong)
├── docs/MASTER_DOCUMENT_SSOT.md     ← Topic-to-document mapping (EXISTS)
└── docs/decisions/PIVOT_LOG.md      ← Decision log (EXISTS, strong)

LAYER 3: OPERATIONAL (Git-Controlled, Agent-Facing)
├── docs/strategy/                   ← Active strategy docs (47 archived)
├── docs/architecture/               ← Architecture specs
├── docs/operations/                 ← Runbooks, health checks
├── SOVEREIGN_MANDATES.md            ← 22 mandates (EXISTS, strong)
├── OMEGA_ENGINE.md                  ← Engine SSOT (EXISTS)
├── ORACLE_STACK.md                  ← Post-compaction recovery (should narrow scope to architecture)
├── SOVEREIGN_ARK_BLUEPRINT.md       ← Strategy SSOT (should narrow scope to strategy/roadmap)
└── data/entities/<entity>/          ← Entity soul docs per SOUL_ARCHITECTURE_PROTOCOL
```

### 3.2 SSOT Domain Assignment (Resolving the 3-Way Overlap)

| Current Document | Problem | Resolution |
|-----------------|---------|------------|
| **ORACLE_STACK.md** | Claims SSOT, but overlaps with Ark Blueprint on strategy | **Narrow to architecture only**. Rename to `docs/ARCHITECTURE_SSOT.md` or keep as-is but remove strategy content. It should cover: what the code does, how to recover from compaction. |
| **SOVEREIGN_ARK_BLUEPRINT.md** | Claims SSOT, overlaps with ORACLE_STACK on architecture | **Own strategy/roadmap only**. Remove architecture deep-dives. Already the strongest SSOT after 2026-06-29 consolidation. |
| **MASTER_DOCUMENT_SSOT.md** | Claims SSOT but is an index, not a subject authority | **Own the index only**. Remove explanatory content. It should tell you WHERE to find things, not explain them. |
| **OMEGA_ENGINE.md** | Correctly scoped to engine state | **Keep as-is**. Already well-scoped. |

### 3.3 CI Pipeline (First-Ever Doc CI)

```yaml
# Added to .github/workflows/test.yml
jobs:
  documentation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: LinkSpector (Dead Link Check)
        uses:俨然/linkspector@v1
      - name: Doc Freshness Check
        run: make doc-freshness
      - name: Prose Linting
        uses: errata-ai/vale-action@v2
```

Plus local targets:
```makefile
# Makefile additions
doc-check:           # Verify all cross-references resolve
doc-freshness:       # Flag docs >30 days stale
doc-serve:           # mkdocs serve
docs-api:            # Generate API reference from docstrings
llms-txt:            # Auto-generate llms.txt from doc tree
```

---

## §4 Prioritized Action Plan (3 Phases)

### Phase 1: Quick Wins (This Sprint — ~3 hours total)

| # | Action | Effort | Impact | Source | Done When |
|---|--------|--------|--------|--------|-----------|
| 1 | **Create `docs/llms.txt` & `docs/llms-full.txt`** | 30 min | 🔴 HIGH — enables AI agent discovery | Researcher §R1 | File exists, follows AnswerDotAI spec |
| 2 | **Add LinkSpector to CI** | 15 min | 🔴 HIGH — catches dead links on every PR | Researcher §R2 | `.github/workflows/test.yml` updated |
| 3 | **Add `docs-health-action` to CI** | 15 min | 🔴 HIGH — all-in-one health check | Researcher §R3 | `.github/workflows/test.yml` updated |
| 4 | **Refresh USER_MANUAL.md metrics** (302→705, 15→22) | 30 min | 🔴 HIGH — restores user trust | Roc §IX.1 | Test count and mandate count accurate |
| 5 | **Create `docs/QUICKSTART.md`** (install → run → talk → done) | 45 min | 🔴 HIGH — separates from 1198-line manual | Roc §IX.3 | File exists, standalone quick start |
| 6 | **Create `docs/contributing/setup.md`** | 30 min | 🟡 MEDIUM — enables new contributors | Researcher §R5 | File exists, covers venv/test/workflow |
| 7 | **Archive orphaned review docs** (move to `docs/archive/review/`) | 15 min | 🟡 MEDIUM — cleans up stale directory | Roc §IX.4 | `docs/review/` moved to archive |

### Phase 2: Structure (Next Sprint — ~8 hours total)

| # | Action | Effort | Impact | Source |
|---|--------|--------|--------|--------|
| 8 | **Set up MkDocs + Material theme** with `docs/` as content source | 2 hr | 🔴 HIGH — renders all docs as a site | Researcher §R6 |
| 9 | **Resolve SSOT overlap** — scope each SSOT to one domain | 1 hr | 🔴 HIGH — eliminates agent context waste | Roc §IX.2 |
| 10 | **Create Diátaxis directory structure** (tutorials/how-to/reference/explanation) | 1 hr | 🟡 MEDIUM — organizes all future docs | Researcher §10 |
| 11 | **Create `docs/tutorials/first-entity.md`** | 1 hr | 🟡 MEDIUM — lowers barrier to entity creation | Researcher §R7 |
| 12 | **Create `docs/tutorials/first-wad.md`** | 1 hr | 🟡 MEDIUM — lowers barrier to WAD creation | Researcher §R8 |
| 13 | **Generate API reference** from Python docstrings | 2 hr | 🔴 HIGH — auto-generated, never stale | Roc §IX.8 |

### Phase 3: Hardening (Post-PR — ~10 hours total)

| # | Action | Effort | Impact | Source |
|---|--------|--------|--------|--------|
| 14 | **Set up `mike` versioning** for MkDocs | 1 hr | 🟡 MEDIUM — versioned docs for releases | Researcher §R11 |
| 15 | **Add Vale prose linting** with Omega style rules | 1 hr | 🟡 MEDIUM — enforces writing standards | Researcher §R12 |
| 16 | **Create MCP Docs Server tool** — programmatic doc access | 3 hr | 🟡 MEDIUM — agents can query docs | Researcher §R13 |
| 17 | **Add Docfresh or Staleguard** to CI | 30 min | 🟡 MEDIUM — automated staleness tracking | Researcher §R15 |
| 18 | **Restructure 196 research docs** into Diátaxis quadrants | 8 hr | 🟢 LOW — strategic, not urgent | Researcher §R14 |
| 19 | **Wire `make doc-freshness` into `make temple-grade`** | 2 hr | 🔴 HIGH — prevents future staleness | Roc §IX.10 |

---

## §5 The Documentation Maturity Ladder

```
Level 0: None
    Current state of auto-generated API reference, contribution guide, quick start

Level 1: Discoverable
    └── llms.txt + AGENTS.md + LinkSpector CI
    → Agents can find docs; broken links caught on PR

Level 2: Navigable
    └── Diátaxis directory structure + MkDocs site + QUICKSTART.md
    → Humans can navigate by task type; quick start exists

Level 3: Reliable
    └── Freshness CI + refreshed metrics + SSOT domains resolved
    → Users trust the numbers; agents trust the SSOT

Level 4: Verifiable
    └── Vale prose linting + API auto-generation + Docfresh
    → Style is consistent; API reference never stale

Level 5: Generative
    └── MCP Docs Server + versioned docs + community contributions
    → Agents query docs programmatically; community contributes

Current: Level 0 (auto-gen API missing, CI missing, quick start missing)
Phase 1 target: Level 1-2
Phase 2 target: Level 2-3
Phase 3 target: Level 3-4
```

---

## §6 Key Tensions & Tradeoffs

| Tension | Choice | Rationale |
|---------|--------|-----------|
| **R-doc system vs Diátaxis** | Both — R-doc is INTERNAL, Diátaxis is EXTERNAL | R-docs are research artifacts for developers. Diátaxis organizes user-facing content. Different audiences, different formats. |
| **MkDocs vs DocsForge** | MkDocs + Material | Already configured (`make mkdocs-serve`). Python-native. Minimal new dependencies. DocsForze can be evaluated later for zero-CDN needs. |
| **Antora vs mike** | `mike` for now | Antora is more powerful for multi-component (IWAD/PWAD versioning) but adds complexity. `mike` is simpler and sufficient for Phase 3. |
| **One big manual vs many small docs** | Small, task-oriented docs (Diátaxis) | The 1198-line USER_MANUAL proves the monolith doesn't work for new users. QUICKSTART.md should be the entry point. |
| **Auto-generated vs hand-written** | Auto-generate API reference + llms.txt; hand-write tutorials + explanations | Auto-generation prevents staleness for reference material. Hand-written docs are essential for learning-oriented content. |
| **CI for docs vs not** | Add CI in Phase 1 | Every prior era failed at doc maintenance because there was no automated enforcement. CI is the only prevention. |

---

## §7 Heritage

This documentation strategy bridges two traditions:
- **[id-soft: doom-1993] README-as-docs**: id Software shipped `README.TXT` alongside every game binary. Our R-doc system and Diátaxis external docs continue this tradition of documentation as a first-class artifact.
- **[id-soft: quake-1996] Carmack's .plan files**: Carmack's developer journals are the spiritual ancestor of `soul.yaml` lessons and session gnosis documentation.
- **Omega Engine evolution**: The 3-path positioning documentation (average/technical/esoteric) survived from Era 1 because it correctly identifies that different readers need different documentation depth. This synthesis validates that pattern against modern industry standards.

---

## §8 Ratification

- [ ] **Kali** — Grand Oversight
- [ ] **Ma'at** — Build Side (Phase 1 implementation owner)
- [ ] **Verity** — Compliance audit (doc CI enforcement)
- [ ] **Doom Guy** — Heritage attribution review
- [ ] **Roc Racoon** — Legacy mining validation

---

*⬡ OMEGA ⬡ JEM ⬡ BIG-PICKLE ⬡ opencode ⬡ trc_synthesis ⬡ DOC-STRATEGY-SYNTHESIS*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: BIG-PICKLE | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
