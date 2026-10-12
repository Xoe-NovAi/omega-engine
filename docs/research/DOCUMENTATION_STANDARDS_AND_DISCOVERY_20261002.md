# Documentation Standards & Discovery Report
**Date**: 2026-10-02
**Author**: Sovereign Researcher (Jem Analyst, L2)
**Status**: RESEARCH ONLY — no changes implemented

---

# PART 1: INDUSTRY DOCUMENTATION STANDARDS

## 1.1 Diátaxis Framework

**Verdict: YES — Omega should adopt Diátaxis as its primary information architecture.**

Diátaxis (diataxis.fr) identifies four distinct user needs and four corresponding documentation forms:

| Quadrant | User Need | Omega Equivalent |
|----------|-----------|------------------|
| **Tutorials** | Learning-oriented (study) | `docs/tutorials/` (1 file — severely underpopulated) |
| **How-to guides** | Task-oriented (work) | `docs/how-to/` (13 files — adequate) |
| **Reference** | Information-oriented (lookup) | `docs/reference/` (20+ files in `api/`) |
| **Explanation** | Understanding-oriented (context) | `docs/explanation/` (8 files — adequate) |

**Key finding**: Omega already has a *partial* Diátaxis structure, but it is incomplete and inconsistent. The `docs/tutorials/` directory has only 1 file. Many "explanation" docs are scattered in `docs/research/` and `docs/guides/`. The framework is proven at scale — adopted by Cloudflare, Gatsby, Vonage, and hundreds of other projects.

**Recommendation**: Formalize the existing `docs/tutorials/`, `docs/how-to/`, `docs/reference/`, `docs/explanation/` directories as the canonical Diátaxis quadrants. Move scattered docs into the correct quadrant. Add a `docs/index.md` that maps the four quadrants.

## 1.2 Google Developer Documentation Style Guide

**Key principles to adopt:**

1. **Clarity over cleverness** — write for the reader, not the writer
2. **Consistency** — same term, same meaning, same formatting throughout
3. **Sentence case headings** — not Title Case
4. **American English** — spelling, punctuation, capitalization
5. **Code formatting** — backticks for inline code, fenced blocks for code samples
6. **Inclusive language** — avoid gendered terms, ableist language
7. **Task-based headings** for tutorials/how-to, noun-phrase headings for concepts
8. **One H1 per page** — the page title, not repeated in headings

Omega already has `docs/standards/DOC_STYLE_GUIDE.md` (v1.0.0, 2026-07-06). It should be cross-referenced against the Google style guide and updated to align.

## 1.3 Best-Documented Open-Source Projects

| Project | Structure | Key Pattern |
|---------|-----------|-------------|
| **Kubernetes** | Concepts → Tutorials → Tasks → Reference → Contribute | Diátaxis-aligned, versioned docs, glossary |
| **Rust** | rustdoc (API) + mdBook (guide) + Reference | Auto-generated API docs from code, separate narrative guide |
| **Python** | Sphinx + PEP 8 + HOWTOs | Auto-generated API docs, how-to guides, FAQ |
| **Docker** | Tutorials → How-to → Reference → Concepts | Diátaxis-aligned, task-oriented |

**Common pattern**: All four use a Diátaxis-like structure with auto-generated API reference separated from narrative documentation. All version their docs. All have a glossary.

## 1.4 API Documentation Standards

- **OpenAPI 3.x** — the industry standard for REST API documentation. Omega's MCP tools should have OpenAPI-equivalent specs (JSON Schema for tool inputs/outputs).
- **MCP tool docs** — each MCP tool should have: description, input schema, output schema, error codes, examples. Omega's `docs/reference/api/` has 20 files — this is the right location.
- **Self-describing APIs** — tools should expose their own documentation (like `openapi-mcp`'s `describe` tool).

## 1.5 Architecture Documentation Standards

- **C4 Model** (Simon Brown) — four levels: Context, Container, Component, Code. Omega has `docs/architecture/` with 49 files but no explicit C4 structure.
- **ADRs** (Architecture Decision Records) — Omega has `docs/adr/` with 3 files. This should be expanded. Each ADR should follow: Title, Status, Context, Decision, Consequences.
- **IEEE 42010** — the standard for architecture description. Omega's `docs/architecture/ARCHITECTURE_CANONICAL.md` is the closest equivalent.

---

# PART 2: DISCOVERY REPORT

## 2.1 File Counts by Directory (Top 30)

| Directory | .md Count |
|-----------|-----------|
| `docs/research/` | 461 |
| `data/coordination/` | 409 |
| `data/archive/coordination/2026-07-04-to-2026-07-14` | 151 |
| `docs/archive/strategy/2026-07-21` | 146 |
| `docs/strategy/` | 118 |
| `data/entities/roc_racoon/workspace/` | 112 |
| `data/entities/roc_racoon/workspace/mining_reports/` | 111 |
| `data/entities/researcher/workspace/` | 100 |
| `data/autonomous/` | 96 |
| `docs/archive/stale/research` | 77 |
| `data/coordination/research/` | 77 |
| `data/quarantine/legacy_layout_20260929/archive/` | 75 |
| `docs/research/archive/` | 74 |
| `docs/archive/coordination-2026-07` | 51 |
| `docs/archive/coordination-2026-08` | 50 |
| `docs/strategy/archive/` | 49 |
| `docs/architecture/` | 49 |
| `.` (top-level) | 48 |
| `data/entities/researcher/workspace/research_reports/` | 33 |
| `config/model_registry/models/cloud/` | 33 |
| `data/coordination/SESSION_PAGING_REPORTS/` | 31 |
| `data/entities/jem/workspace/` | 30 |
| `data/reviews/` | 29 |
| `data/coordination/meditations/records/` | 25 |
| `docs/federation/node1_received/federation/` | 24 |
| `docs/archive/review/` | 24 |
| `docs/federation/` | 23 |
| `data/knowledge/truth_alignment/gsca_study/` | 21 |
| `docs/reference/api/` | 20 |
| `docs/kb/` | 20 |

**Total `.md` files in `docs/`**: 1,785
**Total `.md` files in `docs/research/`**: 602

## 2.2 Top-Level Files That Should Be Archived

The following top-level `.md` files are session notes, reports, or transient artifacts that should be moved to `docs/archive/` or `data/archive/`:

| File | Classification |
|------|---------------|
| `Grokster-compaction-summary-09012026-11_19_AM.md` | Session note |
| `HYDRATION_REPORT.md` | Session report |
| `INTEGRATION_SUMMARY.md` | Session report |
| `PAGE-FROM-KALI-ses fdef2be4effe4pAaLXCTUx62GO.md` | Session note |
| `PILLAR_REFACTOR_WEB_EVIDENCE.md` | Research artifact |
| `PILLAR_RESEARCH_GAPS_20260822.md` | Research artifact |
| `PLUGIN_AUDIT_REPORT_20260925.md` | Audit report |
| `PRE_COMPACTION_NOTES.md` | Session note |
| `QUICK_WINS_FROM_GROK.md` | Session note |
| `RESEARCH_EXECUTION_UPDATE.md` | Session report |
| `ROC NEMOTRON3 WRITE FORENSICS.md` | Session note |
| `STATUS_REPORT.md` | Session report |
| `WAD_ANALYSIS.md` | Analysis artifact |
| `github-repos.md` | Reference note |
| `linux-tools.md` | Reference note |
| `old-claude-sys-prompt.md` | Legacy artifact |
| `quantum_error_correction_2026_article.md` | Research artifact |
| `session-ses_07ee.md` | Session note |
| `session-ses_f469.md` | Session note |
| `session-ses_fc75.md` | Session note |
| `P1.md`, `P3.md`, `P4.md`, `P5.md`, `P6.md`, `P7.md`, `P9.md` | Phase notes |
| `DOCUMENTATION_SPRINT_PLAN.md` | Sprint artifact |
| `GEMINI.md` | Agent config (may belong in `.opencode/`) |
| `CREDITS_CANONICAL.md` | Duplicate of `CREDITS.md` |
| `ORACLE_STACK_CANONICAL.md` | Duplicate of `ORACLE_STACK.md` |
| `SOVEREIGN_ARK_BLUEPRINT_CANONICAL.md` | Blueprint artifact |
| `OMEGA_CODEX.md` | May belong in `docs/` |
| `OMEGA_ENGINE.md` | May belong in `docs/` |
| `MANIFEST.md` | May belong in `docs/` |
| `DEPENDENCIES.md` | May belong in `docs/` |

**Count: ~38 files** that are session notes, reports, or duplicates.

## 2.3 Architecture Docs in `docs/research/` (Should Move to `docs/architecture/`)

**89 files** in `docs/research/` match `R_*ARCH*`, `R_*DESIGN*`, or `R_*SPEC*` patterns. Examples:

- `R_ADVANCED_SYSTEMS_ARCHITECTURE.md`
- `R_BACKGROUND_RESEARCHER_ARCHITECTURE.md`
- `R_C4A_MCP_AUDIT.md`
- `R_CG07_SOVEREIGN_SEARCH_5TIER.md`
- `R_CONTEXT_PACKER_ARCH_REVIEW_20260808.md`
- `R_DEEP_DIVE_RESEARCH_20260810.md`
- `R13_OPENCODE_PLUGIN_ARCHITECTURE_20260814.md`
- `R50_SOMATIC_STATE_DESIGN.md`
- `R51_FREEBUFF_ARCHITECTURE_STUDY.md`
- `AUTOMATED_MODEL_UPDATER_DESIGN.md`
- `GEMMA_MAINTENANCE_WORKER_DESIGN.md`
- `R-DOC-ARCHITECTURE-V2.md`
- `R-SOVEREIGN_ARCHEOLOGY_SOUL_INTEGRITY.md`

**Recommendation**: Move these to `docs/architecture/` or `docs/archive/stale/research/` depending on whether they are current or historical.

## 2.4 API Docs in `docs/research/` (Should Move to `docs/api/` or `docs/reference/api/`)

**17 files** in `docs/research/` match `R_*API*`, `R_*MCP*`, `R_*ENDPOINT*`, `R_*TOOL*` patterns:

- `R_ANTIGRAVITY_DIRECT_API_DEEP_MINE_20260826.md`
- `R_C4A_MCP_AUDIT.md`
- `R_CARMACK_CG-004_GEMMA4_API_SCHEMA_20260719.md`
- `R_CG01_MCP_STREAMABLE_HTTP_OAUTH.md`
- `R_CG01_MCP_STREAMABLE_HTTP_OAUTH_AUDIT.md`
- `R_CLINE_DIRECT_API_DEEP_MINE_20260826.md`
- `R_CONTEXT_PACKER_V3_LIBRARY_APIS_20260808.md`
- `R_COPILOT_DIRECT_API_DEEP_MINE_20260826.md`
- `R_DIRECT_API_RESEARCH_PROTOCOL.md`
- `R_LIBRARY_API_SPEC.md`
- `R_MCP_AUDIT_FINDINGS.md`
- `R_MCP_MIGRATION_AUDIT.md`
- `R_OPENCODE_MCP_HARDENING.md`
- `R_OPENC_MCP_CONFIG.md`
- `R_SEARCH_TOOL_PROTOCOL_V1.md`
- `R_SEARXNG_MCP_STREAMABLE_HTTP.md`
- `R_UBUNTU_2510_TOOLCHAIN_VERIFICATION_20260719.md`

**Recommendation**: Move current API specs to `docs/reference/api/` (where 20 API docs already live). Archive historical audits to `docs/archive/`.

## 2.5 `docs/reference/` — Current State

**Contents**:
- `CLAUDE_BEST_PRACTICES_GUIDE.md`
- `api/` (20 files: cas.md, config_loader.md, context_builder.md, entity_registry.md, ingestion.md, library_fts_search.md, local_inference.md, m36_recursive_probe.md, mcp_client.md, memory_store.md, metrics_db.md, model_gateway.md, observability.md, oracle.md, privacy_kernel.md, proxy_pool.md, selective_hydration.md, session_lifecycle.md, soul_loader.md, vault_core.md)
- `meditate-system-reference.md`
- `selective-hydration.md`
- `transformer_architecture_deep_dive.md`

**Gitignore status**: `docs/reference/**/*.md` is un-ignored (line 295) because the pre-commit docs gate requires a `docs/` change whenever `src/omega/` changes. However, the comment at line 308 notes this was previously a defect — the blanket `docs/reference/` ignore made the gate unsatisfiable.

## 2.6 `.gitignore` Defects

### Defect 1: Blanket `*.md` rule (line 270)
The blanket `*.md` rule silently swallows all Markdown files. This required 30+ un-ignore exceptions. The rule is a footgun — any new `.md` file is ignored by default unless explicitly un-ignored.

**Recommendation**: Replace the blanket `*.md` rule with targeted ignores for specific patterns (e.g., `session-*.md`, `*-Google-Search-Chat.md`, `OCCE-*.md`).

### Defect 2: `docs/reference/` blanket ignore (historical, now fixed)
Previously, `docs/reference/` was blanket-ignored, making the pre-commit docs gate unsatisfiable for any `src/omega/` change. This was fixed by adding `!docs/reference/**/*.md` (line 295).

### Defect 3: `data/coordination/sessions/` swept 637 transcripts
A blanket ignore on `data/coordination/sessions/` swept 637 transcripts, 2 with live tokens. This was a security incident.

### Defect 4: 81MB crash-looping error.log tracked under agent workspace
A large log file was tracked because the ignore rule didn't cover it.

### Defect 5: Frontier review package silently swallowed
The blanket `*.md` rule at line 270 silently swallowed the entire frontier review package (Antigravity IDE peer-review chain). This was reported as "committed" when git had never heard of it.

## 2.7 Missing Documentation (Features with No Docs)

Cross-referencing `src/omega/` modules against `docs/`:

| Module | Has Docs? | Location |
|--------|-----------|----------|
| `agents/` | Partial | `docs/agents/` |
| `audit/` | No | — |
| `benchmarks/` | Partial | `docs/benchmarks/` |
| `bridge/` | No | — |
| `cli/` | No | — |
| `config/` | Partial | `docs/reference/api/config_loader.md` |
| `council/` | No | — |
| `doc_reader/` | No | — |
| `eval/` | No | — |
| `experiments/` | No | — |
| `gateway/` | Partial | `docs/reference/api/model_gateway.md` |
| `governance/` | Partial | `docs/governance/` |
| `hardware.py` | Partial | `docs/how-to/hardware-adaptation-dhal.md` |
| `hub.py` | No | — |
| `ics.py` | Partial | `docs/architecture/ICS_SYSTEM.md` |
| `infra/` | No | — |
| `ingestion/` | Partial | `docs/reference/api/ingestion.md` |
| `integrations/` | No | — |
| `iris/` | No | — |
| `library/` | Partial | `docs/reference/api/library_fts_search.md` |
| `mcp_core/` | No | — |
| `mcp_runtime.py` | No | — |
| `meditate/` | Partial | `docs/guides/AUTONOMOUS_MEDITATION.md` |
| `memory/` | Partial | `docs/reference/api/memory_store.md` |
| `model_registry/` | No | — |
| `monitoring/` | No | — |
| `observability/` | Partial | `docs/reference/api/observability.md` |
| `oracle/` | Partial | `docs/reference/api/oracle.md` |
| `orchestration/` | No | — |
| `privacy/` | Partial | `docs/reference/api/privacy_kernel.md` |
| `proxy_pool.py` | Partial | `docs/reference/api/proxy_pool.md` |
| `rag/` | No | — |
| `request_queue.py` | No | — |
| `research/` | No | — |
| `search/` | No | — |
| `security/` | Partial | `docs/security/` |
| `skills/` | No | — |
| `soul/` | Partial | `docs/reference/api/soul_loader.md` |
| `state/` | No | — |
| `teachers/` | No | — |
| `tools/` | No | — |
| `training/` | No | — |
| `vault/` | Partial | `docs/reference/api/vault_core.md` |
| `workers/` | No | — |

**~25 modules have no dedicated documentation.** The most critical gaps: `mcp_core/`, `mcp_runtime.py`, `orchestration/`, `rag/`, `search/`, `workers/`, `council/`, `gateway/` (partial), `model_registry/`, `monitoring/`.

---

# RECOMMENDATIONS SUMMARY

1. **Adopt Diátaxis formally** — formalize `docs/tutorials/`, `docs/how-to/`, `docs/reference/`, `docs/explanation/` as the four quadrants. Populate `docs/tutorials/` (currently 1 file).
2. **Fix `.gitignore`** — replace blanket `*.md` with targeted ignores. Remove the need for 30+ un-ignore exceptions.
3. **Archive top-level session notes** — move ~38 session notes/reports/duplicates from top-level to `docs/archive/`.
4. **Move architecture docs** — move 89 `R_*ARCH*`/`R_*DESIGN*`/`R_*SPEC*` files from `docs/research/` to `docs/architecture/` or `docs/archive/`.
5. **Move API docs** — move 17 `R_*API*`/`R_*MCP*` files from `docs/research/` to `docs/reference/api/` or `docs/api/`.
6. **Document missing modules** — create docs for ~25 undocumented `src/omega/` modules, starting with `mcp_core/`, `orchestration/`, `rag/`, `search/`, `workers/`.
7. **Expand ADRs** — `docs/adr/` has only 3 files. Add ADRs for major architectural decisions.
8. **Align style guide** — cross-reference `docs/standards/DOC_STYLE_GUIDE.md` against Google Developer Documentation Style Guide.
9. **Create `docs/api/`** — the repo has no `docs/api/` directory. API docs should live there or in `docs/reference/api/`.
10. **Version docs** — like Kubernetes, version documentation alongside code releases.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ DOCUMENTATION_STANDARDS_AND_DISCOVERY_20261002 ⬡ 2026-10-02 ⬡*
