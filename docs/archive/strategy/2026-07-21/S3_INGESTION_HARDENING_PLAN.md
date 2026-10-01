<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 S3 Ingestion Hardening Execution Plan (HARDENED v1.2)
**AP Token**: `AP-S3-INGESTION-HARDENING-v1.2.0`
**Status**: ACTIVE / IMPLEMENTATION-READY
**Date**: 2026-07-05
**Auditor**: John Carmack / Kali / Researcher

## 1. Executive Summary
This plan implements a resilient, CPU-optimized ingestion pipeline. It replaces the "process-per-job" model with a **Persistent Worker Pool** and implements a **Sovereign Proxy** to ensure M8 (Zero Telemetry) compliance.

---

## 2. Implementation Tickets

### T0: Sovereign Proxy MVP
**Priority**: P0 — Blocks all external API calls (T4)
**Effort**: 4h
**Implementation**:
- Deploy Nginx sidecar.
- Configure header stripping: `proxy_set_header User-Agent "Mozilla/5.0..."; proxy_set_header X-Forwarded-For "";`
- Route traffic through local Tor SOCKS5 (`127.0.0.1:9050`).
- **Verification**: `curl http://omega-sovereign-proxy/health` $\rightarrow$ `200 OK`.

### TICKET 1: Mount-Aware Double-Fsync
**Priority**: P0 — Blocks all ingestion integrity  
**Effort**: 2h  
**Legacy Source**: `crawl.py` (Lines 1052-1075)
**Implementation**:
- Implement `safe_fsync(fd)`: Detect mount type via `/proc/mounts`.
- If local (NVMe): `os.fsync(fd)` $\rightarrow$ `os.fsync(dir_fd)`.
- If network (NFS/FUSE): Best-effort write (skip `dir_fd` fsync to avoid hangs).
- **Test**: `test_atomic_write_survives_crash` on local vs network mounts.

### TICKET 2: Persistent IngestionWorker Pool
**Priority**: P0 — Pipeline efficiency and stability  
**Effort**: 4h  
**Legacy Source**: `curation_worker.py`
**Implementation**:
- Use `concurrent.futures.ProcessPoolExecutor` for a fixed-size worker pool.
- Wrap pool calls in `anyio.to_thread.run_sync`.
- Implement `SovereignWorker` as a persistent process that loads `CLTK` and `crawl4ai` as **Singletons**.
- Use `anyio.Semaphore(2)` to prevent CPU thrashing on Ryzen 5700U.
- **Test**: `test_job_execution_isolated` (verify no cold-start on 2nd job).

### TICKET 3: WebScraper with Context Recycling
**Priority**: P0 — Source material extraction  
**Effort**: 4h  
**Legacy Source**: `crawl.py`
**Implementation**:
- Implement `WebScraper` using `crawl4ai.AsyncWebCrawler`.
- **Somatic Reset**: Close and recreate `browser_context` every 50 pages to prevent memory leaks.
- **Surgical Tier**: Use `BM25ContentFilter` for query-driven extraction.
- **Sovereign Proxy**: Route all requests through `T0` proxy.
- **Test**: `test_deep_tier_spa` (verify memory stability over 100 pages).

### TICKET 4: TriangulationVerifier with Token Bucket
**Priority**: P1 — Data verification  
**Effort**: 6h  
**Legacy Source**: `library_api_integrations.py`
**Implementation**:
- Implement `TriangulationVerifier` using Open Library + Internet Archive.
- **Rate Limiting**: Implement a **Redis Token Bucket** (100 req/min) to prevent 429s.
- **Weighted Consensus**: Exact ID (1.0), Semantic Match (0.7), Edition (0.4).
- **Sovereign Proxy**: Route all requests through `T0` proxy.
- **Test**: `test_isbn_verification` (verify confidence score > 0.7).

### TICKET 5: QualityScorer — 5-Dimensional Scoring
**Priority**: P1 — Content filtering  
**Effort**: 3h  
**Legacy Source**: `crawler_curation.py`
**Implementation**:
- Implement `QualityScorer` with factors: Authority(0.3), Completeness(0.25), Freshness(0.2), Structure(0.15), Accessibility(0.1).
- Threshold: `passed = total > 0.6`.
- **Test**: `test_scoring_dimensions` (validate spam vs scholarly).

### TICKET 6: Greek Normalization (CLTK Singleton)
**Priority**: P2 — Classical processing  
**Effort**: 2h  
**Legacy Source**: `ingest_library.py`
**Implementation**:
- Integrate `cltk.nlp.NLP(language="grc")` as a **Singleton** within the worker process.
- Implement `normalize_greek(text)` using CLTK's NFC normalization.
- **Test**: `test_normalization` (verify `ἀνὴρ` $\rightarrow$ `ἀνὴρ`).

### TICKET 7: Branding Purge
**Priority**: P1 — Code hygiene  
**Effort**: 30m  
**Action**: Mechanical `sed` replace `Sovereign*` $\rightarrow$ `Ingestion*` / `Web*` in `src/omega/ingestion/`.

### TICKET 8: PLO Deferral Doc
**Priority**: P3 — Documentation  
**Effort**: 15m  
**File**: `docs/strategy/FUTURE_LINGUISTICS_SPIKE.md`

### TICKET 9: Blueprint Sync
**Priority**: P1 — Documentation  
**Effort**: 15m  
**File**: `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md`

---

## 3. Execution Order (Hard Sequence)

```
PRE-SPRINT (Day 0): Resolve B1 (Redis), B2 (CLTK Models), B3 (Sovereign Proxy), B4 (crawl4ai Deps)

WEEK 1:
├── Day 1-2: TICKET 1 (Double-Fsync) + TICKET 7 (Purge)
├── Day 3-5: TICKET 2 (Worker Pool) + TICKET 3 (WebScraper)
├── Day 6-8: TICKET 4 (Triangulation) + TICKET 5 (QualityScorer)
├── Day 9-10: TICKET 6 (Greek Normalize)
└── Day 10: TICKET 8 (Deferral) + TICKET 9 (Blueprint Sync)
```
