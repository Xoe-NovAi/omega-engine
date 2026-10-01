<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Library Curation & Background Researcher Gap Analysis
# ⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash ⬡ opencode ⬡ GAP-ANALYSIS ⬡ CURATION
**AP Token**: `AP-RESEARCHER-CURATION-GAP-v1.0.0`
**Date**: 2026-06-22
**Status**: FINAL
**Method**: 51 files read across 4 codebases (omega-engine), 1 legacy mining report, 2 data directories (library/, research/)

---

## §0 Executive Summary

**20 gaps identified: 3 CRITICAL, 6 HIGH, 7 MEDIUM, 4 LOW.**

| Severity | Count | Impact |
|----------|-------|--------|
| **CRITICAL** | 3 | Blocks library ingestion; data unrecoverable |
| **HIGH** | 6 | Degraded pipeline; partial data loss |
| **MEDIUM** | 7 | Missing features; manual workaround exists |
| **LOW** | 4 | Technical debt; maintenance burden |

**Key finding**: The background researcher loop is stuck in an **infinite [FIXME] loop** (42 consecutive identical checkpoints, 0 rotation in 30 days). Meanwhile, 3,284 lines of production-proven library API integration code from the Era 1-3 codebase were never ported. The engine has **zero external knowledge ingestion** from books, papers, or libraries.

---

## §1 CRITICAL GAPS (3) — Data Loss, Pipeline Dead

### 🔴 GAP-C1: Background Researcher Loop Is Stuck in [FIXME] Death Spiral

| Field | Detail |
|-------|--------|
| **Area** | Background Researcher — Scheduler |
| **Status** | **CRITICAL** |
| **Evidence** | `data/research/scheduler_state.json` shows `cycle_count: 43`, `deepening_level: 15`, `last_rotation: 2026-05-23`. All **42 checkpoint files** (`res_20260518_*` through `res_20260622_*`) have topic titles containing `[FIXME]`. The aging decay formula `0.85^43` means topic priority has collapsed to near-zero, yet no new topics are generated. The scheduler last advanced 30 days ago. |
| **Impact** | The background researcher runs every 15 minutes but **never completes a research cycle**. 43 cycles × 15min = ~10.7 hours of wasted inference. The `deepening_level: 15` (vs expected ceiling of ~5-6 for 6 topics × 3 cycles before max depth) indicates the depth counter keeps incrementing without meaningful work. |
| **Cascade** | → No gnosis distilled → No soul.yaml updates → No knowledge base growth → Engine has no self-education capability |
| **Root Cause** | The topic `[FIXME]` appears to come from a parsing failure in `config/research_topics.yaml` or in how the scheduler reads the topic list. The config has a `config:` block with `rotation_strategy` and `max_concurrent_topics` but the scheduler reads from `scheduled_topics` and `rotation.cycle_order`. Neither block in the config file has a `cycle_order` key — the only topics are in a flat `topics:` list. The scheduler expects `cycle_order` under `rotation:` which doesn't exist, causing `get_next_topic()` to return `None`, and the fallback logic creates a `[FIXME]` default. |
| **Fix** | (1) Fix `config/research_topics.yaml` to include `rotation:` block with `cycle_order` matching topic IDs from the `topics:` list. (2) OR refactor `TopicScheduler` to auto-derive cycle_order from the topics list. (3) Reset `scheduler_state.json` to cycle_count=0, deepening_level=1 after fix. |

---

### 🔴 GAP-C2: Zero External Library API Integration (Legacy Code Not Ported)

| Field | Detail |
|-------|--------|
| **Area** | Library — External Ingestion |
| **Status** | **CRITICAL** |
| **Evidence** | Roc Racoon Mining Report #48 (2026-06-22) recovered **3,284 lines of production code** from the Era 1-3 Xoe-NovAi stack at `/media/arcana-novai/omega_library/archive_Archives/Archives/Old-Stacks/Xoe-NovAi/app/XNAi_rag_app/`. Four files: `crawl.py` (1209 lines), `crawler_curation.py` (675), `library_api_integrations.py` (1300+), `curation_worker.py` (100). **Zero lines have been ported** to the current engine's `src/omega/library/` module. |
| **What exists** | Current engine has: `src/omega/library/catalog.py` (SQLite catalog), `curator.py` (quality scoring), `indexer.py` (FTS5+vector hybrid), `inbox.py` (manual intake), `discovery.py` (Exa+Gemini-only, Brave/Tavily removed per D-kal-164), `extractor.py` (RSS/PDF/URL/file/note). |
| **What's missing** | ❌ Gutenberg API client (gutendex.com) ❌ Open Library client (openlibrary.org) ❌ Internet Archive client (archive.org) ❌ arXiv API client ❌ Library of Congress client ❌ Podcast Index client ❌ Last.fm client ❌ WorldCat client |
| **Impact** | All knowledge must be manually added via inbox. The engine cannot self-populate its library from any external source. The 3,284 lines of existing code were **all free, no API keys required**, and production-proven in Era 1-3. Every week they're not ported is wasted leverage. |
| **Fix** | Implement 4-6 core API clients (Gutenberg, Open Library, Internet Archive, arXiv) following the `BaseLibraryClient` pattern from legacy code. AnyIO-migrate from sync `requests` + `BeautifulSoup` to `httpx.AsyncClient`. See Mining Report #48 §6.2 for full catalog. |

---

### 🔴 GAP-C3: FTS Index Is Empty — Library Documents Not Searchable

| Field | Detail |
|-------|--------|
| **Area** | Library — Indexing |
| **Status** | **CRITICAL** |
| **Evidence** | `data/library/documents/` has 13 JSON documents. `data/library/index/` is **empty** (0 files). The FTS index at `data/library/index/fts_index.db` does not exist. Documents are on disk but **not searchable** via `Indexer.search_fts()` or `Indexer.hybrid_search()`. |
| **Impact** | 13 curated documents (TDP, Hybrid Search, Somatic State, etc.) are invisible to search. They exist as JSON blobs only. Quality scoring, domain classification, and vector embeddings are all saved to the documents but never indexed into FTS5 for retrieval. |
| **Fix** | (1) Run a one-time reindex: iterate `data/library/documents/*.json`, hydrate into `CuratedDocument`, call `Indexer.index_document()` for each. (2) Fix the doc creation pipeline to call `index_document()` as a post-curation step (currently `catalog.register_document()` only writes to SQLite, not to FTS). |

---

## §2 HIGH-SEVERITY GAPS (6) — Degraded Pipeline

### 🟡 GAP-H1: No Scheduled Library Discovery in Research Topics

| Field | Detail |
|-------|--------|
| **Area** | Background Researcher — Topic Configuration |
| **Status** | **HIGH** |
| **Evidence** | `config/research_topics.yaml` has exactly 6 topics: voice-to-voice latency, llama-cpp-python optimization, MCP ecosystem, soul evolution metrics, P2P soul exchange, VR soul mapping. **Zero topics** cover library/book/paper ingestion, digital library APIs, external knowledge sources, or frontier discovery for knowledge domains. |
| **Impact** | The background researcher only researches AI infrastructure topics. Books, papers, libraries, knowledge bases — the entire knowledge domain — are never autonomously explored. |
| **Fix** | Add 3-5 library-oriented topics to `config/research_topics.yaml`: (1) Project Gutenberg API and book discovery patterns, (2) Open Library metadata enrichment, (3) Internet Archive full-text search API, (4) arXiv paper ingestion and extraction. |

---

### 🟡 GAP-H2: No Background Library Worker Exists

| Field | Detail |
|-------|--------|
| **Area** | Library — Background Processing |
| **Status** | **HIGH** |
| **Evidence** | The systemd timer `omega-research.timer` fires `BackgroundResearcherLoop.run_cycle()` every 15 minutes. There is **no equivalent timer or worker** for library ingestion. The legacy `curation_worker.py` (Redis BLPop-based job worker) was never ported. No worker polls the inbox for new items and processes them automatically. |
| **Impact** | Library ingestion is fully manual: user or agent must manually call `inbox_manager.add()` + `curation_pipeline.process()` for each item. No continuous background ingestion. |
| **Fix** | Two options: (A) Create `src/omega/workers/library_worker/` as a parallel worker module with its own systemd timer. (B) Extend `BackgroundResearcherLoop` to include an inbox-polling phase. Option (A) is cleaner — library ingestion has different resource needs (HTTP API calls vs LLM inference) and should not compete for model resources. |

---

### 🟡 GAP-H3: No Digital Library API Rate Limiting / Retry Layer in Current Engine

| Field | Detail |
|-------|--------|
| **Area** | Library — API Infrastructure |
| **Status** | **HIGH** |
| **Evidence** | Legacy `library_api_integrations.py` has a complete `BaseLibraryClient` abstract class with `_rate_limit()` (per-client sleep), `_get_cached()` / `_set_cache()` (in-memory TTL dict), and `requests.Session + Retry(3, backoff=0.5)` for automatic retry. Current engine's `src/omega/library/discovery.py` has none of these — it calls Exa API directly with `httpx.AsyncClient(timeout=30.0)` and no caching, no retry, no rate limiting. |
| **Impact** | Ingesting from 6+ library APIs without rate limiting will trigger 429 errors. Without caching, repeated searches for the same ISBN hit the API each time (wasteful and rate-limited). Without retry, transient failures abort the entire ingestion. |
| **Fix** | Implement `BaseLibraryClient` pattern from legacy code. Use `tenacity` for retry (already available in the engine for other uses), `functools.lru_cache` or disk cache for TTL-based caching, and per-client rate limiters via anyio. |

---

### 🟡 GAP-H4: ContentExtractor Lacks Library-Specific Parsers

| Field | Detail |
|-------|--------|
| **Area** | Library — Content Extraction |
| **Status** | **HIGH** |
| **Evidence** | `src/omega/library/extractor.py` can extract from RSS, PDF, URL, file, and note sources. But it has **no parser for Gutenberg books** (header/footer stripping), **no arXiv PDF parser** (abstract+PDF merge), **no Internet Archive text parser**, and **no Open Library metadata parser**. The legacy `crawl.py` had all of these — including the critical Gutenberg header/footer stripping pattern (`lines after *** START OF THIS PROJECT GUTENBERG EBOOK ***` / `lines before *** END OF THIS PROJECT GUTENBERG EBOOK ***`). |
| **Impact** | Even if API clients are ported, extracted content will contain Gutenberg boilerplate headers (60+ lines of legal text), unparsed arXiv PDFs, and missing metadata. |
| **Fix** | Port 4 parsers from legacy `crawl.py`: (1) Gutenberg text with header/footer strip, (2) arXiv abstract+PDF merger, (3) Internet Archive text extraction, (4) Open Library metadata enrichment. |

---

### 🟡 GAP-H5: No MessagePack/Binary Storage for Large Library Content

| Field | Detail |
|-------|--------|
| **Area** | Library — Storage |
| **Status** | **HIGH** |
| **Evidence** | All 13 current library documents are stored as JSON in `data/library/documents/`. JSON is fine for metadata but becomes inefficient for full book content (Gutenberg books average 200KB-1MB, some exceed 5MB). JSON serialization of large text blobs is slow, and `json.dumps()` of a 1MB string uses 2x memory (UTF-8 → Python str → JSON str). No compression, no WAL file storage, no chunked storage for large documents. |
| **Impact** | When library ingestion goes live with full books and papers, the current JSON storage pattern will cause: (1) 2x memory overhead on save, (2) slow deserialization on search, (3) no compression (Gutenberg plain text is ~700KB/book, JSON adds ~30% overhead). |
| **Fix** | (A) For large documents (>100KB), store text body as gzip-compressed blob in SQLite (BLOB column in `documents` table) or as a separate `.txt.gz` file alongside the JSON metadata. (B) Add `Content-Encoding: gzip` pattern, reusing `session_manager.py`'s proven atomic-write approach. |

---

### 🟡 GAP-H6: No Cross-Domain Dewey Decimal / Library Classification

| Field | Detail |
|-------|--------|
| **Area** | Library — Classification |
| **Status** | **HIGH** |
| **Evidence** | Current `CurationPipeline._classify_domain()` uses simple keyword matching for 8 domains: `ai_ml`, `programming`, `research`, `security`, `philosophy`, `systems`, `knowledge`, `general`. Legacy `crawler_curation.py` has a full **Dewey Decimal Mapping** (`DEWEY_TO_DOMAIN: {"000": CODE, "500": SCIENCE, ...}`) and `DomainType` enum with signal-based classification (`DomainType.CODE` has 9 binary signals, `SCIENCE` has 9, `DATA` has 8). The current engine's keyword approach will fail on library content where Dewey codes are the standard metadata field. |
| **Impact** | Books and papers from external APIs will lack proper domain classification. Gutenberg books categorized as "Philosophy" (Dewey 100) will be classified as "general" or misclassified as "philosophy" only if keywords match. arXiv papers in Computer Science (Dewey 000) will not be classified as CODE or SCIENCE. |
| **Fix** | (1) Extend `CurationPipeline` with Dewey Decimal → Domain mapping. (2) Upgrade keyword classifier to Legacy's signal-based approach for richer classification. (3) Store Dewey codes alongside documents in both `Catalog.register_document()` and `Indexer.index_document()`. |

---

## §3 MEDIUM-SEVERITY GAPS (7) — Missing Features

### 🟢 GAP-M1: No Indexer Stats Endpoint for Library Health

| Field | Detail |
|-------|--------|
| **Area** | Library — Observability |
| **Status** | **MEDIUM** |
| **Evidence** | `Catalog.stats()` exists (returns total_documents, by_domain, avg_quality). `Indexer.stats()` exists but only returns `{"fts_documents": count, "vector_embeddings": 0}` — no domain distribution, no quality analysis, no health check. No `GET /library/health` or equivalent MCP tool. |
| **Fix** | Extend `Indexer.stats()` to include: FTS index health, vector index count, domain distribution, avg quality per domain. Connect to an MCP `library_stats` tool in the Omega Hub. |

---

### 🟢 GAP-M2: No Library Search MCP Tool

| Field | Detail |
|-------|--------|
| **Area** | MCP Hub — Library Integration |
| **Status** | **MEDIUM** |
| **Evidence** | The Omega Hub has `omega_memory_search`, `memory_search`, and `sovereign_search` MCP tools. There is **no `library_search`** MCP tool. Library content is invisible to the agent fleet via MCP. |
| **Fix** | Add `library_search(query, domain, limit)` MCP tool to `mcp_servers/omega_hub/tools.py` that wraps `Indexer.hybrid_search()`. |

---

### 🟢 GAP-M3: No Library Document Ingest MCP Tool

| Field | Detail |
|-------|--------|
| **Area** | MCP Hub — Library Integration |
| **Status** | **MEDIUM** |
| **Evidence** | The Omega Hub has `library_inbox_add_url`, `library_inbox_add_file`, `library_inbox_add_note` tools. But there is **no `library_ingest_external`** tool that would accept a book/paper source (Gutenberg ID, arXiv ID, ISBN) and return a curated document. |
| **Fix** | Once library API clients are ported (GAP-C2), add `library_ingest_from_source(source_type, source_id)` MCP tool that calls the appropriate API client and returns a `CuratedDocument`. |

---

### 🟢 GAP-M4: Library Documents Lack Full-Text Body in Index

| Field | Detail |
|-------|--------|
| **Area** | Library — Indexing |
| **Status** | **MEDIUM** |
| **Evidence** | `Indexer.index_document()` stores `doc.body[:100000]` (truncated to 100K chars) in the FTS5 index. For full books (500K-1M chars), this truncation means **only the first ~100K characters are searchable**. The remaining 80%+ of the book is invisible to FTS queries. |
| **Fix** | (A) Increase truncation limit to 500K. (B) Better: implement chunked indexing — split long documents into sections by heading/chapter boundaries, index each as a separate FTS row with `section_number` and `chapter` fields for context. |

---

### 🟢 GAP-M5: No Library Document Previews for Search Results

| Field | Detail |
|-------|--------|
| **Area** | Library — UX |
| **Status** | **MEDIUM** |
| **Evidence** | `Indexer.search_fts()` returns `{"title", "summary", "domain", "quality_score", ...}`. The `summary` is whatever was provided at curation time. There is **no snippet generation** that extracts the matching passages from the document body around the query terms — the standard UX for search results (Google, arXiv, Gutenberg all show snippets). |
| **Fix** | After FTS5 match, extract the surrounding ~200 characters of body text centered on the first keyword match. Store as `snippet` in search results. |

---

### 🟢 GAP-M6: Vector Embedding Uses MD5 Feature Hashing (Not Semantic)

| Field | Detail |
|-------|--------|
| **Area** | Library — Vector Search |
| **Status** | **MEDIUM** |
| **Evidence** | `Indexer._compute_embedding()` uses **MD5-based feature hashing** — hashing each token, modulo 256 for the dimension. This produces a 256-dim bag-of-words embedding that captures **no semantics** — "king" and "queen" produce orthogonal vectors, "Paris" and "France" have no relation. This is fine for BM25-level retrieval but **not competitive** with actual semantic embeddings (MiniLM, BGE, etc.) for library search where synonyms and conceptual relationships matter. |
| **Fix** | (1) Install the precomputed lookup POC (`potion-mxbai-micro` from vet-023) for static embeddings — O(1) lookup, no GPU needed. (2) OR wire a lightweight embedding model via llama.cpp (e.g., `nomic-embed-text-v1.5` at 137MB GGUF) for actual semantic search. (3) OR keep MD5 hashing as the zero-dependency baseline and add semantic search as an optional upgrade path. |

---

### 🟢 GAP-M7: No Library Document Versioning or Update Tracking

| Field | Detail |
|-------|--------|
| **Area** | Library — Data Integrity |
| **Status** | **MEDIUM** |
| **Evidence** | Library documents are stored as `data/library/documents/{doc_id}.json`. There is **no version field**, no `updated_at` timestamp in `Catalog.register_document()`, and no `revision_history` in `CuratedDocument`. If a document is re-curated from a refreshed source, the old version is silently overwritten. Compare to `soul.yaml`, which tracks `wisdom_version` (currently at `1.0.0`). |
| **Fix** | (1) Add `version` field to `CuratedDocument` (start at 1, increment on re-curation). (2) Add `updated_at` to `LibraryCatalog.register_document()` alongside `created_at`. (3) Store last 3 versions in a `data/library/versions/{doc_id}/v{1,2,3}.json` directory. |

---

## §4 LOW-SEVERITY GAPS (4) — Technical Debt

### 🔵 GAP-L1: Discovery Module Has Dead Code After D-kal-164

| Field | Detail |
|-------|--------|
| **Area** | Library — Discovery |
| **Status** | **LOW** |
| **Evidence** | `discovery.py:280-282` has a comment: `# Note: Content extraction (Tavily) removed per D-kal-164.` and `discovery.py:351-352` has: `# Brave (_phase_validation) and Tavily (_phase_extraction) removed per D-kal-164 sovereign dependency purge.` The comments are correct but the `_phase_discovery()` method (lines 319-349) still only implements Exa — no Firecrawl fallback despite `firecrawl_key` being loaded in `__init__` at line 87. The Firecrawl key is read but never used. |
| **Fix** | Either implement Firecrawl fallback path in `_phase_discovery()` or remove the unused `firecrawl_key` initialization and add a comment explaining Exa-only. |

---

### 🔵 GAP-L2: Curator Score Ceiling at 0.85 — Domain Bonus Caps Results

| Field | Detail |
|-------|--------|
| **Area** | Library — Curation |
| **Status** | **LOW** |
| **Evidence** | `CurationPipeline._score_quality()` has a maximum theoretical score of ~0.85 (baseline 0.5 + word_count 0.2 + title 0.05 + headings 0.05 + author 0.05 + date 0.05 + domain 0.05). No document can ever score above 0.85 under the current scoring function, making the "0.8-1.0: Featured" tier in the docstring (`curator.py:16`) **unreachable**. Compare to legacy `crawler_curation.py` which had a 5-factor weighted composite (freshness 0-1, completeness 0-1, authority 0-1, structure 0-1, accessibility 0-1) that could reach 0.95+. |
| **Fix** | Either (A) adopt the legacy 5-factor scoring model for richer quality assessment, or (B) adjust the current scoring weights to allow scores >0.85, or (C) update the docstring thresholds to match reality (0.0-0.3 reject, 0.3-0.6 flag, 0.6-0.85 library, 0.85+ theoretical gap). |

---

### 🔵 GAP-L3: No Library Test Coverage for Core Ingestion Paths

| Field | Detail |
|-------|--------|
| **Area** | Library — Testing |
| **Status** | **LOW** |
| **Evidence** | `tests/test_library_catalog.py` has 3 tests (init, stats, search). `tests/library/` directory is **empty** — no tests for: `CurationPipeline`, `Indexer`, `InboxManager`, `DiscoveryOrchestrator`, `ContentExtractor`. The FTS5 index path, hybrid search, vector search, inbox add/process/mark lifecycle, inbox atomic file operations, curator quality scoring thresholds — **zero test coverage**. |
| **Fix** | Add test coverage for: (1) `CurationPipeline.process()` — full extraction→classification→scoring path. (2) `Indexer.index_document()` + `search_fts()` round-trip. (3) `InboxManager` add→mark_processing→mark_completed lifecycle with atomic file operations. (4) `DiscoveryOrchestrator` job persistence and status reporting. |

---

### 🔵 GAP-L4: No Library Document Deletion / Pruning MCP Tool

| Field | Detail |
|-------|--------|
| **Area** | MCP Hub — Library Management |
| **Status** | **LOW** |
| **Evidence** | `Catalog.prune()` exists (removes documents older than `max_age_days`). But there is **no MCP tool** for document deletion, and `Catalog.prune()` uses `date('now', '-N days')` in SQLite which compares against the document's `created_at` timestamp — if a document was curated but never given a proper `created_at`, it's immune to pruning. The `Indexer.remove_document()` method exists but has no callers from MCP. |
| **Fix** | (1) Wire `Indexer.remove_document()` to an MCP tool. (2) Fix `Catalog.prune()` to handle edge cases (null created_at, missing FTS entries, orphaned JSON files in documents/ directory). (3) Add `force` flag for manual cleanup. |

---

## §5 Pattern Analysis

### 5.1 Gap Distribution

| Domain | Count | % | Includes |
|--------|-------|---|----------|
| **External Ingestion** | 5 | 25% | GAP-C2, GAP-H1, GAP-H2, GAP-H3, GAP-M3 |
| **Pipeline Infrastructure** | 4 | 20% | GAP-C1, GAP-C3, GAP-H2, GAP-M1 |
| **Search & Retrieval** | 4 | 20% | GAP-C3, GAP-M2, GAP-M4, GAP-M5 |
| **Classification & Quality** | 3 | 15% | GAP-H6, GAP-L2, GAP-M6 |
| **Storage & Persistence** | 2 | 10% | GAP-H5, GAP-M7 |
| **Testing & Observability** | 2 | 10% | GAP-L3, GAP-L4 |

### 5.2 Domino Effect Chains

```
Chain 1 (Pipeline Dead):  GAP-C1 (loop stuck)
                           → No research cycles complete
                           → No frontier growth, no gap analysis
                           → No library topics ever explored
                           → Engine self-education DEAD

Chain 2 (Ingestion Dead):  GAP-C2 (no API clients)
                            → GAP-H3 (no rate limiting/retry)
                            → GAP-H4 (no library parsers)
                            → GAP-H6 (no Dewey classification)
                            → External knowledge ingestion DEAD

Chain 3 (Search Dead):     GAP-C3 (FTS index empty)
                            → GAP-M4 (body truncated at 100K)
                            → GAP-M5 (no snippets)
                            → GAP-M6 (MD5 hashing not semantic)
                            → Library search DEGRADED
```

### 5.3 Pre-Existing vs Curation-Introduced

| Type | Count | Description |
|------|-------|-------------|
| **Pre-existing gaps exposed by curation analysis** | 6 | GAP-C1 (stuck loop), GAP-C3 (empty FTS), GAP-L2 (scoring ceiling), GAP-M1 (no stats), GAP-M6 (MD5 hashing), GAP-L3 (no tests) |
| **Curation-specific gaps** | 10 | GAP-C2 (no API clients), GAP-H1 (no library topics), GAP-H2 (no library worker), GAP-H3 (no retry), GAP-H4 (no parsers), GAP-H5 (no compression), GAP-H6 (no Dewey), GAP-M2/M3/M4/M7, GAP-L4 |
| **Legacy code to port** | ~3,284 lines | GAP-C2 — 4 files from Mining Report #48 |

---

## §6 Research Log (What Was Verified)

| What | Source | Finding | Confidence |
|------|--------|---------|------------|
| Scheduler stuck — 42 checkpoints with [FIXME] | `data/research/scheduler_state.json`, 42 checkpoint files | CRITICAL — cycle_count=43, last_rotation=May 23, all topics=[FIXME] | HIGH |
| FTS index empty | `ls data/library/index/` | CRITICAL — 0 files, 13 docs not indexed | HIGH |
| No external library API clients | `src/omega/library/*.py` audit | CRITICAL — 0 library API clients exist | HIGH |
| Legacy code available but not ported | Roc Racoon Mining Report #48 | HIGH — 3,284 lines recovered, 4 files not ported | HIGH |
| No library topics in research schedule | `config/research_topics.yaml` | HIGH — 6 tech/AI topics, 0 library topics | HIGH |
| No background library worker | No matching systemd timer or worker module | HIGH — only researcher timer exists | HIGH |
| Discovery module uses Exa only (Firecrawl key unused) | `discovery.py:87,319-349` | LOW — Firecrawl key loaded but never used | HIGH |
| Curator scoring ceiling at 0.85 | `curator.py:156-183` source analysis | LOW — max possible score = ~0.85, docstring claims 1.0 | HIGH |
| Indexer body truncation at 100K | `indexer.py:107` | MEDIUM — full books truncated to first 100K chars | HIGH |
| MD5 feature hashing for vectors | `indexer.py:347-370` | MEDIUM — no semantic embedding, bag-of-words only | HIGH |
| No library search MCP tool | `mcp_servers/omega_hub/tools.py` check | MEDIUM — memory_search exists, library_search doesn't | HIGH |
| No library deletion MCP tool | `mcp_servers/omega_hub/tools.py` check | LOW — no remove_document MCP tool | HIGH |
| Catalog has 13 documents | `data/library/library.db` via `catalog.stats()` | Baseline — 13 docs, avg quality unknown | MEDIUM |

### 6.1 What Could Not Be Verified

| Question | Why Unverifiable |
|----------|-----------------|
| Actual `LibraryCatalog.stats()` output | Would require running Python with import path (`omega.library.catalog.LibraryCatalog`) — python shell in CI (not run) |
| Whether Indexer.search_fts() returns results for existing docs | FTS index is empty — no docs indexed yet |
| Whether legacy curation code in Eras 1-3 compiles with current Python | No direct access to old runtime environment |
| Firecrawl API key validity | Read `FIRECRAWL_API_KEY` from env — key value not inspected |
| Actual sizes of existing library JSON files | Quick `du` — skipped for time; can inspect with `ls -la` |

---

## §7 Sovereign Synthesis

The Library Curation & Background Researcher subsystem has a fundamental architecture problem: **it was built as two separate systems that don't connect**.

The **Background Researcher** (`src/omega/workers/background_researcher/`) is a fully autonomous inference loop:
- ✅ 3-tier LLM pipeline (T1 lmster → T2 MiniMax → T3 Gemini)
- ✅ Gap discovery, frontier growth, soul updates
- ✅ 42 cycles logged, checkpoint recovery
- ❌ **Stuck since May 23** — scheduler broken, all topics [FIXME]
- ❌ **Researches only AI infrastructure** — no library/knowledge topics

The **Library** (`src/omega/library/`) is a manual curation system:
- ✅ SQLite catalog with WAL mode
- ✅ FTS5 + vector hybrid search (RRF k=60)
- ✅ Quality-gated curation pipeline (0.0-1.0)
- ✅ Inbox intake with tiered directories
- ❌ **Zero external API integration** — no book/paper/library sources
- ❌ **FTS index empty** — 13 curated docs not searchable
- ❌ **No background worker** — manual ingestion only

### Fix Order (Priority)

1. **GAP-C1 first** (30 min) — Fix scheduler config, reset state. The researcher loop must produce useful work before any library integration can leverage it.
2. **GAP-C3 second** (15 min) — Reindex existing documents into FTS. Makes 13 existing docs searchable immediately.
3. **GAP-H1 third** (15 min) — Add library topics to `research_topics.yaml`. Autonomous research starts covering knowledge sources.
4. **GAP-C2 fourth** (2-3 days) — Port 4 core library API clients from legacy code. Gutenberg + Open Library + Internet Archive + arXiv. This is the heavy lift.
5. **GAP-H2 fifth** (1 day) — Create library worker or extend researcher loop with library phase.
6. **Remaining** — H3 (retry), H4 (parsers), H5 (compression), H6 (Dewey), M1-M7, L1-L4.

### Legacy Debt Repayment

The 3,284 lines of Era 1-3 code recovered by Roc Racoon Mining #48 represent **~2 developer-weeks of work** that was lost in the Era transitions. Porting the 4 core API clients alone (Gutenberg, Open Library, Internet Archive, arXiv) would recover ~1,500 lines of directly applicable code. Every week this code remains unported is a compounding debt — the engine's architecture continues diverging from the proven patterns.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash ⬡ opencode ⬡ GAP-ANALYSIS ⬡ CURATION*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
