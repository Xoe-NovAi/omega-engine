---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

id: kg-readme-001
title: "Knowledge Graph — Artifact Index"
generated_at: "2026-07-01T15:30:00Z"
system: "T3 - Entity Knowledge Graph"
---

# 🔱 Knowledge Graph — Carmack Conceptual Network

## Purpose

A persistent, incrementally-built knowledge graph of Carmack's conceptual universe. Nodes represent concepts (algorithms, principles, historical events); edges represent relationships (depends-on, informs, contradicts, refines, evolves-to). Built one source at a time with deduplication.

## Artifacts

| File | Type | Description | Generated |
|------|------|-------------|-----------|
| `kg_concept_nodes.json` | JSON | All concept nodes with definitions, source citations, and Carmack quotes | Incremental (per source) |
| `kg_relationships.json` | JSON | All relationship edges between concepts with strength and rationale | Incremental (per source) |
| `kg_incremental_build.py` | PY | Build script for adding one source at a time or full rebuild | One-time |
| `kg_queries.md` | MD | Canonical queries against the graph for common use cases | One-time |

## Relationship Types

| Type | Color | Description |
|------|-------|-------------|
| `depends_on` | #4A90D9 | A requires B to function correctly |
| `informs` | #50C878 | A provides foundational understanding for B |
| `contradicts` | #E74C3C | A and B are in tension |
| `refines` | #F39C12 | A makes B more precise or applicable |
| `evolves_to` | #9B59B6 | A was superseded by B over time |

## Schema Reference

See `INGESTION_PIPELINE_ARCHITECTURE.md §5.8-5.10` for node and edge JSON schemas.

## Incremental Build

```bash
# Add one source to the graph
python kg_incremental_build.py --source ../../../../knowledge/plans/plan_19961225_quake_gl.md

# Full rebuild from all ingested sources
python kg_incremental_build.py --rebuild
```
