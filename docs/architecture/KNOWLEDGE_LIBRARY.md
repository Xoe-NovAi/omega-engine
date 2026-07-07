# 🔱 Knowledge Library Architecture
**AP Token**: `AP-KNOWLEDGE-LIB-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_doc_deep ⬡ STANDARD

**Date**: 2026-07-06
**Purpose**: Architecture of the knowledge library and memory management system.

---

# 🔱 Omega Engine — Knowledge Library Architecture
# AP: AP-LIBRARY-ARCH-v1.0.0
# ICS: [NODE: CORE | ARCHETYPE: LIBRARY | CONTEXT: SOVEREIGN-KNOWLEDGE]

The Knowledge Library is the sovereign memory of the Omega Engine, transforming transient research into a permanent, structured asset.

## 1. Core Philosophy: The Curated Archive
Unlike a raw RAG vector store, the Knowledge Library is a **curated archive**. It does not just store chunks; it stores **verified documents** with multi-dimensional quality metrics.

## 2. Structural Organization
The library is organized into 10 domain subdirectories mapping to the 10 Pillar slots:

`data/library/documents/`
├── `p1_sysadmin/` — Infrastructure, OS, Podman, Hardening
├── `p2_datastore/` — Vector DBs, SQLite, MemoryStore, Caching
├── `p3_buildmaster/` — CI/CD, Build tools, Architecture
├── `p4_bridge/` — APIs, MCP, Networking, Integration
├── `p5_sentinel/` — Security, Auditing, Mandates
├── `p6_modelgate/` — Inference, GGUF, Providers, Quantization
├── `p7_context/` — Sessions, Soul Evolution, Continuity
├── `p8_watchtower/` — Observability, Tracing, Forensics
├── `p9_link/` — Coordination, Handoff, Delegation
└── `p10_verifier/` — Testing, Chaos, Validation

## 3. The Catalog (SQLite)
The `library.db` tracks metadata for every document.

### 3.1 Schema
- `id`: Unique document ID
- `path`: Absolute path to the file
- `domain`: Pillar slot owner
- `title/author/source_url`: Provenance metadata
- `quality_vector`: JSON array `[integrity, coherence, completeness, structure, domain_fit]`
- `avg_quality`: Scalar average for fast ranking
- `created_at/indexed_at`: Temporal metadata

### 3.2 Multi-Dimensional Quality Scoring (CRACQ Pattern)
Every document is scored across 5 dimensions:
1. **Content Integrity**: Is the data accurate and verified?
2. **Coherence**: Is the document logically structured?
3. **Completeness**: Does it cover the topic exhaustively?
4. **Structure**: Is it formatted for AI consumption (markdown, lists)?
5. **Domain Fit**: How relevant is it to the assigned pillar?

## 4. The Curation Pipeline
Documents enter the library via the following pipeline:
`Discovery` $\rightarrow$ `Download` $\rightarrow$ `Process` $\rightarrow$ `Index` $\rightarrow$ `Catalog`

1. **Discovery**: `jem_discovery` identifies a high-value source.
2. **Download**: The source is saved to the domain directory.
3. **Process**: `jem_synthesis` cleans and formats the content.
4. **Index**: Vector embeddings are generated for RAG.
5. **Catalog**: `jem_verification` assigns the quality vector and registers the doc in `library.db`.

## 5. CLI Interface
- `omega library status`: Show overall catalog health and domain distribution.
- `omega library search <query>`: Find high-quality documents across domains.
- `omega library curate <domain>`: Trigger a curation cycle for a specific pillar.
