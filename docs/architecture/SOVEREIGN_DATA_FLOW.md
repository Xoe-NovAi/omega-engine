# 🔱 Sovereign Data Flow
**AP Token**: `AP-SOVEREIGN_DATA_FLOW-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_doc_deep ⬡ STANDARD

**Date**: 2026-07-06
**Purpose**: Architecture documentation for sovereign data flow.

---

# Sovereign Data Flow Architecture

**AP: AP-ARCH-SOVEREIGN-DATA-FLOW-v1.0.0**
**Date: 2026-06-09 | Sprint: S2-C Knowledge Sovereignty**

---

## Overview

This document describes the Sovereign Grade data flow for all content entering and exiting the Omega Engine's library and inference layers. It is the authoritative reference for how external data is tainted, isolated, indexed, searched, and returned to clients.

---

## §1 — Data Classification Boundary

All data entering the Omega Engine is classified at ingestion time:

| Source | Taint Level | Trust Level |
|--------|:-----------:|-------------|
| `oracle_talk` (internal inference) | None | **Trusted** — synthesized by the engine |
| `library_inbox_add_note` | 1 | External — user-provided text |
| `library_inbox_add_file` | 1 | External — local file content |
| `library_search` results | 1 | External — curated but unverified |
| `library_inbox_add_url` | 2 | **High-Risk** — arbitrary external URL |
| Detected injection pattern | 3 | **Malicious/Blocked** — quarantined |

---

## §2 — Full Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    EXTERNAL DATA SOURCES                      │
│                                                              │
│  User Note ──────┐                                           │
│  Local File ─────┼──→  library_inbox_add_*()                 │
│  External URL ───┘      MCP Tool Layer (47 tools)            │
│                                                              │
│  Web Search ─────────→  library_discovery_research()         │
└──────────────────────────────────┬───────────────────────────┘
                                   │
                          @tdp_wrap decorator
                     (source=..., taint_level=1|2)
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────┐
│                  TAINTED DATA BOUNDARY (TDP)                  │
│                                                              │
│  TaintedData(content, source, taint_level)                   │
│       │                                                      │
│       ├─ TDPGate.sanitize() — strip injection patterns       │
│       └─ TDPGate.isolate() — wrap in [EXTERNAL DATA] markers │
└──────────────────────────────────┬───────────────────────────┘
                                   │
              ┌────────────────────┴────────────────────┐
              │                                          │
              ▼                                          ▼
┌─────────────────────────┐              ┌───────────────────────────┐
│   FTS5 Index (BM25)     │              │  Vector Store             │
│   (SQLite aiosqlite)    │              │  (IVectorStoreAdapter)    │
│                         │              │                           │
│  documents_fts table    │              │  MemoryVectorAdapter      │
│  (doc_id, title, body,  │              │  (default, in-memory)     │
│   summary, domain, tags)│              │    or                     │
│                         │              │  QdrantAdapter            │
│  BM25 scoring via       │              │  (production, persistent) │
│  FTS5 rank column       │              │                           │
│                         │              │  MD5 feature-hash embed   │
│  Indexer.search_fts()   │              │  256-dim, L2-normalized   │
└─────────────┬───────────┘              └──────────────┬────────────┘
              │                                          │
              └──────────────────┬───────────────────────┘
                                 │
                         RRF Fusion (k=60)
                    score(d) = Σ 1 / (60 + rank_r(d))
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────┐
│                   SOVEREIGN SEARCH RESULT                     │
│                                                              │
│  • Hybrid-ranked (BM25 + cosine via RRF)                     │
│  • Taint level preserved in metadata                         │
│  • Isolated by TDPGate before MCP response                   │
│                                                              │
│  [EXTERNAL DATA START]                                       │
│  Source: library_search                                      │
│  Taint Level: 1                                              │
│  ---                                                         │
│  <result content>                                            │
│  [EXTERNAL DATA END]                                         │
└──────────────────────────────────┬───────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────┐
│                 CLIENT (via MCP Protocol)                     │
│                                                              │
│  Receives isolated, taint-marked results.                    │
│  Can choose to: render, quarantine, or strip markers.        │
└──────────────────────────────────────────────────────────────┘
```

---

## §3 — Knowledge Discovery Layer

The entity knowledge layer adds a second data flow for entity-specific topics:

```
data/entities/{entity}/workspace/    ← Agent writes research here
         │
         │  Topic Promotion Gate (T1→T2)
         │  • Quality gate check
         │  • Vector embedding generated
         │  • INDEX.yaml updated
         │
         ▼
data/entities/{entity}/knowledge/    ← Promoted, indexed topics
         │
         │  CrossRefEngine.find_related()
         │  • PATH A: FTS5 keyword match (tags + title)
         │  • PATH B: Cosine similarity (MD5 feature vectors)
         │  • RRF merge (k=60)
         │
         ▼
data/entities/{entity}/knowledge/INDEX.yaml   ← Discovery manifest
         │
         ▼
KNOWLEDGE_MANIFEST.yaml                        ← Global catalog
```

---

## §4 — CrossRef Engine (src/omega/library/crossref.py)

The `CrossRefEngine` implements dual-path cross-referencing between library documents:

```
CrossRefEngine.find_related(doc_id)
    │
    ├── PATH A: _keyword_related()
    │     • Extract tags + title tokens from source doc
    │     • FTS5 MATCH query against all other docs
    │     • Returns: ranked list by BM25
    │
    ├── PATH B: _vector_related()
    │     • Load all doc vectors (lazy, cached)
    │     • Cosine similarity: source vec vs all others
    │     • Returns: ranked list by similarity score
    │
    └── MERGE: RRF(k=60)
          • Union of both result sets
          • score(d) = Σ 1/(60 + rank_r(d))
          • Sort descending → top-k results
          • Each result tagged with _paths: ["keyword"|"vector"|both]
```

---

## §5 — Component Responsibility Map

| Component | File | Responsibility |
|-----------|------|----------------|
| `TaintedData` | `oracle/security.py` | Data classification wrapper |
| `TDPGate` | `oracle/security.py` | Isolation + sanitization |
| `@tdp_wrap` | `oracle/security.py` | MCP tool decorator |
| `Indexer` | `library/indexer.py` | FTS5 + vector indexing & hybrid search |
| `CrossRefEngine` | `library/crossref.py` | Dual-path cross-reference (NEW) |
| `Library` | `library/library.py` | Document storage + curator |
| `LibraryCatalog` | `library/catalog.py` | SQLite metadata catalog |
| `QdrantAdapter` | `memory/vector_adapters.py` | Production vector store |
| `MemoryVectorAdapter` | `memory/vector_adapters.py` | Test/dev vector store |
| Omega Hub | `mcp_servers/omega_hub/server.py` | 47 MCP tools + lifespan |

---

## §6 — Sovereign Grade Gate Criteria

The knowledge layer is **Sovereign Grade** when:

- [x] `doc_security_R_tainted_data_protocol.json` exists and is FTS-indexed
- [x] `doc_datastore_R_hybrid_search_rrf.json` exists and is FTS-indexed
- [x] `doc_watchtower_R_aiosqlite_teardown_hardening.json` exists and is FTS-indexed
- [x] `src/omega/library/crossref.py` implements dual-path RRF cross-referencing
- [ ] Vector embeddings present for all 3 gap docs (requires ingest step)
- [ ] `@tdp_wrap` applied to all 5 MCP tool endpoints (S2-A pending)
- [ ] `Indexer.close()` wired into MCP server lifespan (SD-010 fix pending)
- [ ] SD-001 (auth) and SD-002 (CORS) resolved (Sentinel sprint)

**Verification**: `python scripts/verify_knowledge_sovereign.py`

---

*⬡ OMEGA ⬡ ANTIGRAVITY-IDE ⬡ S2-C Knowledge Sovereignty ⬡ 2026-06-09*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
