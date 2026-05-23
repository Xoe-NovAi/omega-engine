# 🔱 Xoe-NovAi Internal Discovery Project

**Project Root**: `docs/research/internal-discovery/`  
**Established**: 2026-05-14  
**Status**: 🟢 ACTIVE  
**AP Token**: `AP-INTERNAL-DISCOVERY-v1.0.0`

---

## §1 Purpose

This project is the **sovereign knowledge engine** for all internal discovery and research initiatives within the Xoe-NovAi ecosystem. It exists to:

1. **Preserve** the evolutionary lineage of our tools, architectures, and decisions.
2. **Track** all research initiatives, their status, and their interconnections.
3. **Harden** our data management so that no intelligence evaporates across sessions.
4. **Enable** graph-based navigation (Obsidian) and searchable publication (MkDocs).

---

## §2 Project Structure

```
internal-discovery/
├── INDEX.md                    ← This file — the project hub
├── STACK_CAT_LINEAGE.md        ← The context-aggregation evolution lineage
├── TOOLING_STRATEGY.md         ← Obsidian, MkDocs, SQLite integration blueprint
├── DATA_MANAGEMENT_HARDENING.md ← Lifecycle, metadata standards, archival
├── DB/                         ← SQLite schema and migration scripts
│   └── research_metadata.sql   ← The canonical schema
├── DOCUMENTS/                  ← Preserved legacy documents (referenced, not duplicated)
│   └── INDEX.md                ← Index of externally-referenced documents
├── MAPS/                       ← Knowledge graph maps and relationship diagrams
│   └── INDEX.md                ← Index of available maps
└── TEMPLATES/                  ← Reusable templates for research documents
    └── discovery_report.md     ← Standard template for new discoveries
```

---

## §3 Active Discovery Registry

| ID | Title | Status | Lead | Started | Documents |
|----|-------|--------|------|---------|-----------|
| D-01 | Context Aggregation Lineage | ✅ COMPLETE | Researcher | 2026-05-14 | [STACK_CAT_LINEAGE.md](./STACK_CAT_LINEAGE.md) |
| D-02 | Tooling & Data Management Strategy | ✅ COMPLETE | Researcher | 2026-05-14 | [TOOLING_STRATEGY.md](./TOOLING_STRATEGY.md), [DATA_MANAGEMENT_HARDENING.md](./DATA_MANAGEMENT_HARDENING.md) |
| D-03 | *(Next)* | 🔲 PENDING | — | — | — |

---

## §4 Interconnection Map

```
docs/research/ (Omega Research Index)
    │
    ├── R_*.md (Provider Fabric, Soul, Memory specs)
    │
    └── internal-discovery/ (THIS PROJECT)
            │
            ├── INDEX.md ───────────────────────────────→ docs/operations/RESEARCH_QUEUE.md
            │
            ├── STACK_CAT_LINEAGE.md ───────────────────→ ../R_HOLOGRAPHIC_MEMORY_LATTICE.md
            │                                           → ../../gnosis/ARCHITECT.md
            │
            ├── TOOLING_STRATEGY.md ────────────────────→ (Configures: mkdocs.yml, obsidian vault)
            │                                           → (Feeds: DB/research_metadata.sql)
            │
            └── DATA_MANAGEMENT_HARDENING.md ───────────→ ../../operations/RESEARCH_QUEUE.md
                                                        → ../CORRECTIONS.md
```

---

## §5 Tools & Integration

| Tool | Purpose | Status | Config Location |
|------|---------|--------|-----------------|
| **MkDocs** | Render research as searchable HTML site | ✅ Installed (v1.6.1, Material theme) | `mkdocs.yml` (project root) |
| **Obsidian** | Graph-based knowledge navigation | ✅ Installed | `~/.config/obsidian/` |
| **SQLite** | Structured metadata querying | ✅ Available (v3.46.1) | `DB/research_metadata.sql` |
| **Hivemind MCP** | Cross-agent context sharing | 🟢 ACTIVE | `mcp/omega-hivemind/` |

---

## §6 Quick Start

```bash
# 1. View the full research site (MkDocs)
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
mkdocs serve          # Live preview at http://127.0.0.1:8000

# 2. Initialize the research metadata database
python3 scripts/init-research-db.py          # Create DB
python3 scripts/init-research-db.py --seed   # Seed from existing docs

# 3. Query the database
sqlite3 docs/research/internal-discovery/DB/research.db \
  "SELECT * FROM v_stale_documents;"         # Find stale docs
sqlite3 docs/research/internal-discovery/DB/research.db \
  "SELECT * FROM v_document_tags WHERE tags LIKE '%podman%';"  # Filter by tag

# 4. Open in Obsidian (add docs/ as a vault folder)
obsidian open docs/

# 5. Use a discovery template for new findings
cp TEMPLATES/discovery_report.md ../R-NEW_document.md
```
