---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

id: kg-queries-001
title: "Knowledge Graph — Canonical Queries"
generated_at: "2026-07-01T15:30:00Z"
pipeline_version: "1.0.0"
---

# 🔱 Knowledge Graph — Canonical Queries

## Purpose

Standard queries to extract structured knowledge from the Carmack conceptual graph. These queries ensure consistent retrieval patterns across agent sessions.

---

### Q1: Trace an axiom to its source examples

**Query**: Given L3 principle P, find all concrete examples Carmack used to demonstrate it.

```python
# Graph traversal:
#   principle_node ──informs──► example_node ──sourced_from──► source_file
```

**Use case**: When the entity needs to cite a real Carmack example for a principle.

---

### Q2: Find contradicting concepts

**Query**: Given concept C, find all concepts that contradict or constrain C.

```python
# Edge filter:
#   source: C, type: contradicts
```

**Use case**: When evaluating a proposal against Carmack's philosophy — find where his own ideas are in tension.

---

### Q3: Trace evolution of an idea

**Query**: Given concept C, find all `evolves_to` paths to understand how Carmack's thinking changed over time.

```python
# Path traversal:
#   C ──evolves_to──► C2 ──evolves_to──► C3
```

**Use case**: When the entity needs to understand not just what Carmack thought, but how it changed.

---

### Q4: Source attribution for any claim

**Query**: Given concept C, find all source files where Carmack discussed it.

```python
# Property filter:
#   node.sources contains [source_id]
```

**Use case**: Every generated Carmack statement should be traceable to a source.

---

### Q5: Interconnectedness score

**Query**: Find the most interconnected concepts (highest degree in the graph).

```python
# Graph metric:
#   degree = len(in_edges) + len(out_edges)
```

**Use case**: Identify the core concepts that Carmack returned to most often across his career.

---

## Query Execution

These queries are executed by the ingestion pipeline's knowledge graph module (`kg_incremental_build.py`). Each query produces a JSON result that can be injected into agent context.
