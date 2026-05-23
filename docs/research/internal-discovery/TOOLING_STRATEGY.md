# 🔱 Research Tooling & Data Management Strategy

**Discovery ID**: D-02  
**Status**: ✅ COMPLETE  
**Date**: 2026-05-14  
**System State**: MkDocs 1.6.1 installed, SQLite 3.46.1 available, Obsidian config present

---

## §1 Current State Assessment

### What We Have
| Tool | Version | Purpose | Status |
|------|---------|---------|--------|
| MkDocs | 1.6.1 | Static site generation for documentation | ✅ Installed |
| Material for MkDocs | 9.7.1 | Theme with search, navigation, code highlighting | ✅ Installed |
| SQLite | 3.46.1 | Structured metadata tracking | ✅ Available |
| Python sqlite3 | — | Bindings for schema management | ✅ Available |
| aiosqlite | 0.22.1 | Async SQLite for Python | ✅ Available |
| Obsidian | — | Graph-based markdown knowledge management | ✅ Config present |

### What We Lack
| Gap | Impact | Severity |
|-----|--------|----------|
| No mkdocs.yml config | Research docs are not searchable or navigable as a site | 🔴 High |
| No YAML frontmatter in research docs | No machine-readable metadata (tags, status, dates, links) | 🟡 Medium |
| No SQLite tracking DB | Cannot query "what research exists on topic X" or "which docs are stale" | 🟡 Medium |
| No Obsidian vault config | Cannot visualize knowledge graph or see document relationships | 🟢 Low |
| No automated snapshot archival | Research state disappears across sessions, no rollback | 🔴 High |
| No template standards | Each research doc uses different structure, no consistency | 🟡 Medium |

---

## §2 MkDocs Integration: Making Research Searchable

### Current Opportunity
MkDocs is installed and ready. The `docs/` directory already follows the MkDocs convention. We need a `mkdocs.yml` at the project root to activate it.

### Recommended Configuration
The config should:
- Use the Material theme (already installed)
- Enable search with indexing
- Set up navigation structure that mirrors the research directory
- Enable code highlighting for embedded snippets
- Add revision date display for freshness awareness

### Workflow
```bash
mkdocs serve    # Live preview at http://127.0.0.1:8000
mkdocs build    # Static site to site/
```

### Implementation Priority: 🔴 Immediate
A `mkdocs.yml` at project root will instantly make all 50+ research documents searchable and navigable.

---

## §3 YAML Frontmatter Standard: Making Research Machine-Readable

Every research document MUST include a standardized YAML frontmatter block. This enables:
- MkDocs metadata extraction and filtering
- SQLite automated ingestion
- Obsidian property-based queries
- Agent-based document discovery (the Hivemind MCP can filter by tags)

### Standard Template
```yaml
---
id: R-42
title: "Specific document title"
status: "✅ complete | 🔄 in_progress | 🔲 pending"
urgency: "🔴 critical | 🟡 high | 🟢 strategic"
domain: "infrastructure | memory | soul | providers | tooling"
tags: [podman, containers, rootless, systemd]
related: [R-13, R-PODMAN]
created: 2026-05-14
updated: 2026-05-14
author: "Sovereign Master Researcher"
sources:
  - "https://docs.podman.io/en/v5.0/markdown/podman-systemd.unit.5.html"
  - "https://github.com/containers/podman/blob/v5.0/RELEASE_NOTES.md"
---
```

### Implementation Priority: 🟡 Medium
Requires updating existing documents. Start with new documents only, backfill as resources allow.

---

## §4 SQLite Research Metadata Database: Making Research Queryable

### Architecture
A single SQLite database at `docs/research/internal-discovery/DB/research.db` tracking all research artifacts.

### Schema Design
```sql
-- Research documents registry
CREATE TABLE research_documents (
    id TEXT PRIMARY KEY,              -- R-42 or D-01
    title TEXT NOT NULL,
    status TEXT CHECK(status IN ('complete','in_progress','pending','blocked')),
    urgency TEXT CHECK(urgency IN ('critical','high','strategic')),
    domain TEXT,
    file_path TEXT UNIQUE NOT NULL,   -- Relative path from docs/research/
    created_at TEXT NOT NULL,
    updated_at TEXT,
    author TEXT
);

-- Tags for filtering
CREATE TABLE tags (
    document_id TEXT REFERENCES research_documents(id),
    tag TEXT NOT NULL,
    PRIMARY KEY (document_id, tag)
);

-- Cross-document links
CREATE TABLE related_documents (
    source_id TEXT REFERENCES research_documents(id),
    target_id TEXT REFERENCES research_documents(id),
    relationship TEXT DEFAULT 'related',
    PRIMARY KEY (source_id, target_id)
);

-- Source provenance tracking
CREATE TABLE sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id TEXT REFERENCES research_documents(id),
    url TEXT NOT NULL,
    accessed_at TEXT DEFAULT (datetime('now'))
);

-- Discovery tracking for internal projects
CREATE TABLE discoveries (
    id TEXT PRIMARY KEY,              -- D-01
    title TEXT NOT NULL,
    status TEXT CHECK(status IN ('complete','in_progress','pending')),
    lead TEXT,
    file_path TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT
);
```

### Use Cases
```bash
# Find all documents about podman
sqlite3 DB/research.db "SELECT id, title FROM research_documents
    JOIN tags ON research_documents.id = tags.document_id
    WHERE tag = 'podman';"

# Find all documents related to R-13
sqlite3 DB/research.db "SELECT target_id, relationship FROM related_documents
    WHERE source_id = 'R-13';"

# Find stale documents (not updated in 30+ days)
sqlite3 DB/research.db "SELECT id, title FROM research_documents
    WHERE updated_at < date('now', '-30 days');"
```

### Implementation Priority: 🟡 Medium
Create the schema script and initialization script. Automate updates via git hooks.

---

## §5 Obsidian Integration: Visual Knowledge Graph

### How It Helps
Obsidian renders the same markdown files we already have but adds:
- **Graph View**: See how R-04 connects to R-01, R-02, R-03 visually
- **Backlinks**: See which documents reference a given doc
- **Local Graph**: Explore the neighborhood of a specific topic
- **Tag Pane**: Browse all documents by tag

### Setup
```bash
# Open the docs/ directory as an Obsidian vault
obsidian open /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/
```

### Recommended Plugins
| Plugin | Purpose |
|--------|---------|
| Core: Graph View | Knowledge graph visualization |
| Core: Backlinks | See reverse references |
| Core: Search | Full-text search across all research |
| Dataview (community) | SQL-like queries on YAML frontmatter |
| Periodic Notes (community) | Research session journaling |

### Best Practices
- Use `[[wiki-links]]` for cross-document references
- Use `#tags` for topic categorization
- Keep YAML frontmatter consistent for Dataview queries

### Implementation Priority: 🟢 Low
No code changes needed. Just configure the vault and optionally install plugins.

---

## §6 Automated Snapshot Archival: Preventing Intelligence Loss

### The Problem
Currently, the `docs/research/` directory has no versioned history mechanism beyond git. Git preserves history but requires manual commits and provides no summary of "what research state was the engine in at date X."

### The Solution: Weekly Research Snapshots
A systemd-triggered process (the "Sovereign Archivist") that:
1. Copies all of `docs/research/` to `docs/research/archives/<YYYY-MM-DD>/`
2. Generates a `manifest.json` with checksums and document counts
3. Generates a summary report of changes since last snapshot
4. Prunes snapshots older than 90 days

### Integration with Sovereign Janitor
This is a natural extension of the `R_SOVEREIGN_MAINTENANCE_STRATEGY.md` "Gardener" function. The Janitor's daily run would include:

```bash
# Pseudo-code for snapshot archival
if day_of_week == "Monday":
    snapshot_dir = f"docs/research/archives/{date}"
    cp -r docs/research/*.md $snapshot_dir/
    sha256sum > $snapshot_dir/manifest.sha256
    prune_archives(older_than_days=90)
```

### Implementation Priority: 🟡 Medium
Build this as a script within the Sovereign Janitor container.

---

## §7 The Unified Workflow

```
┌─────────────────────────────────────────────────────┐
│                Research Lifecycle                     │
├─────────────────────────────────────────────────────┤
│                                                       │
│  1. DISCOVER ───→ Legacy mining / web research        │
│       │              │                                 │
│       ▼              ▼                                 │
│  2. DOCUMENT ───→ Write to docs/research/R_*.md      │
│       │              │ (with YAML frontmatter)         │
│       ▼              ▼                                 │
│  3. REGISTER ────→ Update INDEX.md                   │
│       │              │ Insert into SQLite DB           │
│       ▼              ▼                                 │
│  4. PUBLISH ─────→ mkdocs serve / mkdocs build        │
│       │              │ Obsidian vault auto-refreshes   │
│       ▼              ▼                                 │
│  5. ARCHIVE ────→ Weekly snapshot (Sovereign Janitor) │
│       │              │ Git commit                      │
│       ▼              ▼                                 │
│  6. LINK ───────→ Update related_documents table      │
│                      Graph links in Obsidian           │
│                      Implementation notes in docs      │
│                                                       │
└─────────────────────────────────────────────────────┘
```

### Implementation Priority Summary

| Component | Priority | Effort | Dependencies |
|-----------|----------|--------|--------------|
| MkDocs config | 🔴 Immediate | 15 min | None |
| YAML frontmatter retro-fit | 🟡 Medium | 2-4 hours | None |
| SQLite schema + init script | 🟡 Medium | 1 hour | Python + sqlite3 |
| Obsidian vault setup | 🟢 Low | 5 min | Obsidian installed |
| Snapshot archival | 🟡 Medium | 2-3 hours | Sovereign Janitor container |
| Unified lifecycle enforcement | 🟢 Low | Ongoing | All above complete |

---

## §8 Implementation Note

**To the Sovereign Builder**: Start with the MkDocs config — it's the highest impact for the lowest effort. A single `mkdocs.yml` at the project root will unlock searchable, navigable, professional-looking research docs immediately. Then proceed to the SQLite schema for structured querying.

**Related Research**:
- [STACK_CAT_LINEAGE.md](./STACK_CAT_LINEAGE.md) — The evolutionary context for why this matters
- [DATA_MANAGEMENT_HARDENING.md](./DATA_MANAGEMENT_HARDENING.md) — The broader data governance strategy
- [R_SOVEREIGN_MAINTENANCE_STRATEGY.md](../R_SOVEREIGN_MAINTENANCE_STRATEGY.md) — The Janitor that will power archival
