# 🔱 Omega Engine — R-P005: Workbench Domain Migration Guide
# ⬡ OMEGA ⬡ MAAT ⬡ gemma-4-31b ⬡ opencode ⬡ trc_anchor ⬡ KNOWLEDGE-ANCHOR

**AP Token**: `AP-KNOWLEDGE-ANCHOR-v1.0.0`
**Status**: ✅ ACTIVE
**Last Updated**: 2026-05-15
**Target**: Database Schema Evolution

---

## 1. Overview
To support advanced routing and filtered project views, the Omega Workbench database (`data/workbench/workbench.db`) requires a schema migration to add a `domain` column to the `work_items` table. This allows tasks to be categorized by domain (e.g., `infrastructure`, `gnosis`, `soul-evolution`).

## 2. Migration Specification

### 2.1 SQL Migration Script
The following SQL should be executed against the SQLite database:

```sql
-- Start Transaction
BEGIN TRANSACTION;

-- 1. Add the domain column to work_items
ALTER TABLE work_items ADD COLUMN domain TEXT DEFAULT 'general';

-- 2. Update existing P0 items to a specific domain based on title keywords
UPDATE work_items 
SET domain = 'infrastructure' 
WHERE title LIKE '%container%' OR title LIKE '%podman%' OR title LIKE '%systemd%';

UPDATE work_items 
SET domain = 'gnosis' 
WHERE title LIKE '%research%' OR title LIKE '%soul%' OR title LIKE '%axiom%';

-- 3. Update the v_project_summary view to include the domain
-- Note: SQLite views must be dropped and recreated
DROP VIEW IF EXISTS v_project_summary;

CREATE VIEW v_project_summary AS 
SELECT id, title, priority, status, domain, workstream 
FROM work_items;

COMMIT;
```

### 2.2 Validation Procedure
After migration, run the following queries to verify the state:

```sql
-- Verify column existence
PRAGMA table_info(work_items);

-- Verify domain distribution
SELECT domain, COUNT(*) FROM work_items GROUP BY domain;

-- Verify view update
SELECT * FROM v_project_summary LIMIT 5;
```

### 2.3 Rollback Procedure
In case of failure, use the following script to revert the changes:

```sql
BEGIN TRANSACTION;

-- SQLite does not support DROP COLUMN in older versions.
-- For SQLite 3.35+, use:
ALTER TABLE work_items DROP COLUMN domain;

-- Recreate the original view
DROP VIEW IF EXISTS v_project_summary;
CREATE VIEW v_project_summary AS 
SELECT id, title, priority, status, workstream 
FROM work_items;

COMMIT;
```

---

## 3. Test Data for Verification
Use these entries to verify the migration's effectiveness:

| Title | Expected Domain |
| :--- | :--- |
| "Fix Podman network crash" | `infrastructure` |
| "Research Soul Abstraction" | `gnosis` |
| "Update README file" | `general` |

---

## 4. Cross-References
- **Database Path**: `data/workbench/workbench.db`
- **Project Management**: `AGENTS.md` §4 (Quick Start - Workbench)
- **Implementation**: `src/omega/oracle/orchestrator.py` (task dispatching)

---
**Implementation Note**: This migration should be wrapped in a Python script using `aiosqlite` to ensure it is executed as part of the engine's startup sequence if the schema version is outdated.
