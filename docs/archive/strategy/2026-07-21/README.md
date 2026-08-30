# 🔱 Omega Engine — Archived Strategy Documents

**Archive Date**: 2026-07-21
**Canonical Strategy**: `docs/strategy/CANONICAL_ROADMAP_20260721.md`

## What Happened

On 2026-07-21, 147 stale strategy documents were moved here as part of **Phase C: Infrastructure Hardening**. Prior to cleanup, `docs/strategy/` contained 90+ files with 5 competing roadmaps, none of which were the authoritative source.

## The New Hierarchy

| Layer | Location | Purpose |
|-------|----------|---------|
| **Canonical** | `docs/strategy/CANONICAL_ROADMAP_20260721.md` | Single authoritative roadmap |
| **Index** | `docs/strategy/STRATEGY_INDEX.md` | 3-layer doc hierarchy |
| **Active Specs** | `docs/strategy/LIVING_RESEARCH_OS_SPEC_20260721.md` etc. | Referenced from roadmap |
| **Archive** | This directory | Historical documents, preserved as-is |

## What's Preserved

All 147 files are preserved exactly as they were — no content was modified, deleted, or truncated. They remain available for reference if historical context is needed.

## How to Find Something

```bash
# Search archived docs by keyword
grep -rl "your-term" docs/archive/strategy/2026-07-21/

# Read an archived doc
cat docs/archive/strategy/2026-07-21/YOUR_DOC.md

# List all archived docs
ls docs/archive/strategy/2026-07-21/*.md
```

## Data Integrity

- **147 files archived**
- **2.7 MB total**
- **Zero data loss** — all files moved, not copied
- **No files modified** — preserved exactly as they were
