
## [2026-06-06] P2 KB Schema Specification — COMPLETE

**Task**: Research and specify the Knowledge Base metadata architecture.

**Deliverable**: `data/kb/_staging/knowledge_systems/TD-P2-KNOWLEDGE-BASE-SCHEMA.md` (1024 lines)

**Key outputs**:
- §1: Frontmatter schema — 10 mandatory + 12 optional fields
- §2: Soul→KB Bridge — dual-write protocol mapping soul.yaml → KB artifacts
- §3: DOMAIN_INDEX.yaml + EDGE_INDEX.yaml design
- §4: Staleness metadata — TTL, supersession chains, git timestamps
- §5: Migration script — scripts/kb_migrate_frontmatter.py (full Python)
- §6: ZONEID_KNOWLEDGE_ARTIFACT = 0x1d4a21 registration

**Pending Phase 2**: Register ZONEID in cvar_table.py, implement kb_writer.py
