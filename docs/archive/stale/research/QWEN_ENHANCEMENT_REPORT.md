# 🔱 Qwen 3.6 Plus Enhancement Report: Research Infrastructure

**Date**: 2026-05-15  
**Model**: qwen3.6-plus-free  
**Scope**: Internal Discovery Hub, SQLite Schema, Makefile, Templates

---

## §1 Executive Summary

The previous assistant (DeepSeek V4 Flash) built a solid foundation for the Internal Discovery Hub. The MkDocs site, SQLite database, and documentation structure are all functional. However, several critical gaps existed that would cause friction as the research program scales. I have implemented surgical enhancements to address these gaps.

---

## §2 Enhancements Implemented

### 2.1 Omega-Enriched Discovery Template

**File**: `docs/research/internal-discovery/TEMPLATES/discovery_report.md`

**Before**: Generic template with basic YAML frontmatter.

**After**: Omega-specific template with:
- `confidence` score (1-10) for research claims
- `sovereignty_score` (1-10) for local-first compliance
- `hardware_impact` fields (RAM, CPU, latency estimates)
- `superseded_by` field for lifecycle management
- `word_count` for context window planning
- **Confidence Calibration section** (per Researcher's Protocol §VIII)
- **Uncertainty Log** (YAML format for known unknowns)
- **Hardware Impact Analysis table**
- **Sovereignty Assessment table**

**Impact**: Every new discovery document will now include the metadata needed for automated querying, confidence tracking, and hardware impact assessment.

### 2.2 SQLite Schema Upgrade with FTS5

**File**: `scripts/init-research-db.py`

**Before**: Basic schema with no full-text search, no schema versioning.

**After**: Enhanced schema with:
- **FTS5 virtual table** for full-text search across all research content
- **Schema version tracking** (`schema_version` table) for future migrations
- **New columns**: `confidence`, `sovereignty_score`, `ram_mb`, `cpu_cores`, `latency_ms`, `superseded_by`, `word_count`
- **New views**:
  - `v_low_confidence_documents` — Documents with confidence < 6
  - `v_research_velocity` — Documents per domain per month
  - `v_sovereignty_distribution` — Sovereignty score breakdown
- **New CLI commands**:
  - `--query <tag>` — Query documents by tag
  - `--stale` — List stale documents
  - `--stats` — Show database statistics
  - `--sync` — Sync existing DB with current docs

**Impact**: The database now supports full-text search, confidence tracking, and research velocity metrics.

### 2.3 `make validate-research` Target

**File**: `Makefile`

**Before**: No research validation.

**After**: Comprehensive validation target that checks:
1. ✅ All R-*.md files have YAML frontmatter
2. ✅ No broken internal links in research docs
3. ✅ SQLite DB sync status (document count match)
4. ✅ Stale document detection (90+ days)
5. ✅ MkDocs availability check

**Impact**: Automated integrity checks prevent silent corruption of the research graph.

### 2.4 MkDocs Serve & Build Targets

**File**: `Makefile`

**New targets**:
- `make mkdocs-serve` — Serve research documentation site
- `make mkdocs-build` — Build static research documentation site

**Impact**: One-command access to the searchable research site.

---

## §3 What Was NOT Changed (and Why)

| Component | Decision | Rationale |
|-----------|----------|-----------|
| **MkDocs navigation** | Kept static | Auto-discovery would require a plugin; static nav is more intentional for now |
| **Obsidian vault** | No changes needed | Obsidian works with existing markdown files; no code changes required |
| **Snapshot archival** | Deferred to Sovereign Janitor | This is a runtime concern, not a research infrastructure concern |
| **Git hooks** | Not implemented yet | Would require pre-commit setup; can be added later when needed |

---

## §4 Verification Results

```
$ make validate-research

🔍 Research Document Validation

  ✗ Missing YAML frontmatter: 45 documents (expected — legacy docs)
  ✓ No broken internal links
  ✓ SQLite DB in sync (45 documents)
  ✓ No stale documents
  ✓ MkDocs available

✅ Validation complete.
```

**Key findings**:
- All 45 existing documents are missing YAML frontmatter (expected — they predate the standard)
- No broken internal links (good — the research graph is intact)
- SQLite DB is in sync with the file system
- No stale documents (all docs are recent)
- MkDocs is available and functional

---

## §5 Next Steps for the Builder

1. **Retro-fit YAML frontmatter** on existing documents (2-4 hours of work)
2. **Implement the Sovereign Janitor** for automated snapshot archival
3. **Add pre-commit hooks** for automatic metadata extraction
4. **Create the MkDocs index page** for the research site
5. **Set up Obsidian vault** with Dataview plugin for SQL-like queries

---

## §6 Implementation Note

**To the Sovereign Builder**: The highest-leverage action is retro-fitting YAML frontmatter on the 45 existing documents. This will unlock the full power of the SQLite database and Obsidian Dataview queries. Start with the most critical documents (R-01 through R-18) and work outward.

The `make validate-research` target will guide you — run it after each batch of frontmatter additions to verify progress.

**Related Research**:
- [TOOLING_STRATEGY.md](./TOOLING_STRATEGY.md) — The original tooling blueprint
- [DATA_MANAGEMENT_HARDENING.md](./DATA_MANAGEMENT_HARDENING.md) — The broader data governance strategy
