<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Search Persistence Pipeline — Deep Research
**AP Token**: `AP-SEARCH-PERSISTENCE-v1.0.0`
**Date**: 2026-07-26 | **Priority**: P0 — Carmack #1 Constraint
**Researcher**: Sovereign Researcher (Council of Four)

---

## Executive Summary

Carmack's #1 constraint confirmed. Websearch/webfetch results vanish when session ends. The engine has **three disjointed persistence mechanisms** that fail to compose into usable research memory.

## Current State

| Mechanism | What It Stores | What It Loses |
|-----------|---------------|---------------|
| `search_persistence.py` | Metadata only (query, tier, latency) | Content in unsearchable JSON blob |
| `SovereignCache` (.firecrawl/) | T3 Firecrawl results only | T0-T2 results, no dedup, 33 stale items |
| `CASArchiver` | Content-addressed blobs | Exists but unwired to search |
| `search_history.db` | 47 records (mostly test queries) | No FTS5, no content search |

**Critical flaw**: `results_json` is stored as opaque TEXT — you cannot search "which previous search found content about X?"

## Recommended Architecture: ResearchArtifactStore

### Schema (SQLite FTS5)

```sql
CREATE TABLE artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_hash TEXT UNIQUE NOT NULL,      -- SHA-256 (CAS key)
    url TEXT,
    title TEXT,
    source_type TEXT NOT NULL,              -- 'websearch', 'firecrawl', 'exa', etc.
    source_tier INTEGER NOT NULL,           -- SSP tier (0-6)
    entity_name TEXT,
    content_preview TEXT,                   -- First 500 chars
    authority_score REAL DEFAULT 0.5,
    freshness_score REAL DEFAULT 1.0,
    access_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_verified INTEGER DEFAULT 0,
    shared INTEGER DEFAULT 1
);

CREATE VIRTUAL TABLE artifacts_fts USING fts5(
    title, content_preview, url,
    content='artifacts', content_rowid='id',
    tokenize='porter unicode61'
);
```

### TTL Policy

| Source Type | TTL | Rationale |
|-------------|-----|-----------|
| SearXNG / websearch (T1) | 24h | Discovery results change frequently |
| webfetch / exa (T2) | 72h | Fetched pages more stable |
| Firecrawl (T3) | 7d | Deep extraction expensive, stable |
| manual | 30d | Human-curated |
| verified (any) | 30d | SkepticalVerifier passed |

### Integration Points

1. **T0 (check cache)**: Before any external search, check `artifacts_fts`
2. **Post-tier (persist)**: After each tier executes, persist results to store
3. **CAS wiring**: Metadata in SQLite, content blobs in CASArchiver

## Migration Path

| Phase | Task | Effort |
|-------|------|--------|
| 1 | Create ResearchArtifactStore module | 4h |
| 2 | Wire into SSP-V2 pipeline (T0 check + post-tier persist) | 8h |
| 3 | Connect CASArchiver for content blobs | 4h |
| 4 | Eviction (LRU 10K entries) + observability | 4h |
| 5 | Migrate .firecrawl/ + search_history.db | 2h |
| **Total** | | **~22h** |

## Key Insight

Without this, ALL research is disposable. R18 should be Sprint 0, not Sprint 18.
