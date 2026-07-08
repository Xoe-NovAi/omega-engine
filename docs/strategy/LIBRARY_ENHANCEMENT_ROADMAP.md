# 🔱 Sovereign Library Enhancement Roadmap
**AP Token**: `AP-LIBRARY-ROADMAP-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ deepseek-r1-qwen3-8b ⬡ opencode ⬡ trc_library_roadmap ⬡ STRATEGY

**Date**: 2026-07-08
**Purpose**: Comprehensive execution plan for upgrading the Omega Engine Library from a basic document store to a scholarly-grade, resilient knowledge platform. Based on legacy mining reports and Sovereign Ark Blueprint.

---

## 🎯 Executive Summary
Following the consolidation of the Library API Clients (v2.0), the foundation is solid. The next evolution requires porting high-value legacy scholarly enrichment systems, implementing robust circuit breakers, and wiring the library deeply into the Oracle's ingestion pipeline. 

This roadmap defines 4 sequential phases to achieve a **Sovereign Scholarly Archive**.

---

## 📦 Phase 1: Scholarly Enrichment & Resilience (Immediate)
**Goal**: Elevate metadata quality to academic standards and protect the engine from external API failures.

### 1.1 Port `MetadataEnricher` (Legacy: 869 lines)
*   **Target**: `src/omega/library/scholarly.py`
*   **Features**:
    *   ORCID integration for author identity resolution and disambiguation.
    *   OpenAlex / CrossRef integration for citation networks and venue metadata.
    *   Semantic Scholar integration for concept extraction.
*   **Value**: Transforms basic author strings into verifiable scholarly identities.

### 1.2 External API Resilience (Circuit Breakers)
*   **Target**: `src/omega/library/api_clients.py` & `src/omega/oracle/health_monitor.py`
*   **Features**:
    *   Implement `StochasticCircuitBreaker` for OpenLibrary, InternetArchive, LoC, and Gutenberg.
    *   Add exponential backoff and `Retry-After` header respect.
    *   Bulkhead isolation (separate AnyIO task groups/limits per provider).
*   **Value**: Prevents a downed external library API from hanging the Oracle ingestion pipeline.

### 1.3 Oracle Ingestion Wiring
*   **Target**: `src/omega/oracle/ingestion.py`
*   **Features**:
    *   Hook `enrich_document()` directly into the `SovereignIngestionPipeline`.
    *   Automatically attempt metadata enrichment when a new document is summoned or saved.
*   **Value**: Zero-touch curation. Documents become highly structured assets automatically.

---

## ⚖️ Phase 2: Quantitative Quality & Tiering (Near-Term)
**Goal**: Implement mathematical quality scoring and lifecycle management for stored knowledge.

### 2.1 Port `QualityMetricsService` (Legacy: 1120 lines)
*   **Target**: `src/omega/library/metrics.py`
*   **Features**:
    *   Calculate h-index and i10-index for authors.
    *   Journal impact factor and quartile rankings (Q1-Q4).
    *   Field-normalized citation impact scoring.
*   **Value**: Allows the engine to prioritize highly-cited, peer-reviewed knowledge over general web scrapes.

### 2.2 Implement `QualityTier` System (Legacy: 218 lines)
*   **Target**: `src/omega/library/tiering.py`
*   **Features**:
    *   Map the 5-dimensional CRACQ score to tiers: `GOLD`, `HIGH`, `GOOD`, `ACCEPTABLE`, `REJECTED`.
    *   Apply different retention policies (e.g., `REJECTED` purges after 7 days, `GOLD` is pinned to hot memory).
*   **Value**: Automated garbage collection of low-quality data; preservation of high-value assets.

### 2.3 Implement `EnrichmentHooks` (Legacy: 522 lines)
*   **Target**: `src/omega/library/hooks.py`
*   **Features**:
    *   Confidence-thresholded orchestration (only call paid/slow APIs if free APIs return confidence < 0.6).
    *   Staleness triggers (re-enrich documents older than 6 months).
*   **Value**: Optimizes API usage and token/time budgets.

---

## 🛡️ Phase 3: Advanced Ingestion & Compliance (Mid-Term)
**Goal**: High-throughput, parallelized ingestion with strict sovereign compliance gating.

### 3.1 Port `DaathIngestor` (Legacy: 163 lines)
*   **Target**: `src/omega/library/compliance.py`
*   **Features**:
    *   `MaatGuardrails` compliance checks at the boundary.
    *   Resonance tier assignment (does this document align with the user's sovereign values?).
*   **Value**: Prevents tainted, misaligned, or cognitively hazardous data from entering the permanent library.

### 3.2 `ContentSource` TaskGroup Pipeline (Legacy: 730 lines)
*   **Target**: `src/omega/library/pipeline.py`
*   **Features**:
    *   Parallel AnyIO processing of Web, RSS, PDF, and Code sources.
    *   Integration with `WorkerCoordinator` for RAM/CPU-aware pausing.
*   **Value**: Massive throughput increase for bulk library imports.

---

## 🔭 Phase 4: Observability & Performance (Ongoing)
**Goal**: Deep visibility into library health and lightning-fast retrieval.

### 4.1 Library Telemetry
*   **Target**: `src/omega/observability.py`
*   **Features**:
    *   Track API latency, hit/miss rates, and rate-limit events per provider.
    *   Monitor SQLite catalog fragmentation and vector index health.
*   **Value**: Data-driven optimization of the enrichment pipeline.

### 4.2 Smart Caching & FTS Optimization
*   **Target**: `src/omega/library/catalog.py`
*   **Features**:
    *   Faceted search capabilities (filter by author, year, Dewey Decimal).
    *   BM25 tuning for the SQLite FTS5 index.
*   **Value**: Instantaneous retrieval of exact knowledge blocks.

---

## 📜 Implementation Directives (The Carmack Standard)

1.  **Mandate 1 (AnyIO Absolute)**: No `asyncio`. All parallel enrichment must use `anyio.create_task_group()`.
2.  **Mandate 9 (Error Integrity)**: All new modules must define specific `OmegaError` subclasses (e.g., `ScholarlyAPIError`, `ComplianceGateError`). No bare exceptions.
3.  **Carmack's Law (Axiom 02)**: When porting legacy code, **do not copy blindly**. Strip redundant abstractions. If a legacy 800-line file can be a 150-line modern AnyIO module, rewrite it.
4.  **Test-Driven Porting**: No legacy module is considered "ported" until it has >90% test coverage with mocked external dependencies.

---
*End of Roadmap. Track progress in `OMEGA_ENGINE.md` and `PIVOT_LOG.md`.*