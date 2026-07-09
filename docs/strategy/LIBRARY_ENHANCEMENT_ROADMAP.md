# 🔱 Sovereign Library Enhancement Roadmap
**AP Token**: `AP-LIBRARY-ROADMAP-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ deepseek-r1-qwen3-8b ⬡ opencode ⬡ trc_library_roadmap ⬡ STRATEGY

**Date**: 2026-07-08
**Purpose**: Comprehensive execution plan for upgrading the Omega Engine Library from a basic document store to a scholarly-grade, resilient knowledge platform. Based on legacy mining reports and Sovereign Ark Blueprint.
**Reviewed**: 2026-07-08 by Roc Racoon — R1–R12 insights from Carmack's Session 55 parallel architecture review incorporated (see handoff `ho_5b378d09a029`).

---

## 🎯 Executive Summary
Following the consolidation of the Library API Clients (v2.0), the foundation is solid. The next evolution requires porting high-value legacy scholarly enrichment systems, implementing robust circuit breakers, and wiring the library deeply into the Oracle's ingestion pipeline. 

This roadmap defines 4 sequential phases to achieve a **Sovereign Scholarly Archive**.

---

## 📦 Phase 1: Scholarly Enrichment & Resilience (Immediate)
**Goal**: Elevate metadata quality to academic standards and protect the engine from external API failures.
**Execution Order** (R2): 1.1 → 1.2 → 1.3 for quick wins — wire ingestion first (zero-dep), then resilience, then external enrichment.

### 1.1 Oracle Ingestion Wiring (Zero-Dep Win)
*   **Target**: `src/omega/oracle/ingestion.py`
*   **Features**:
    *   Hook `enrich_document()` directly into the `SovereignIngestionPipeline`.
    *   Automatically attempt metadata enrichment when a new document is summoned or saved.
*   **Value**: Zero-touch curation. Documents become highly structured assets automatically. No external API dependency — ships immediately.

### 1.2 External API Resilience (Circuit Breakers)
*   **Target**: `src/omega/library/api_clients.py` & `src/omega/oracle/health_monitor.py`
*   **Features**:
    *   Implement `StochasticCircuitBreaker` for OpenLibrary, InternetArchive, LoC, and Gutenberg.
    *   Add exponential backoff and `Retry-After` header respect.
    *   Bulkhead isolation (separate AnyIO task groups/limits per provider).
    *   **Persistent cache layer** (R3): SQLite/file-backed cache behind `api_clients.py` — current in-memory cache is lost on restart.
    *   **Global API budget** (R7): `max_calls_per_session` / `max_calls_per_day` in `LibraryAPIConfig` to enforce sovereignty cost caps.
*   **Value**: Prevents a downed external library API from hanging the Oracle ingestion pipeline. Graceful degradation (R4) — enrichment never blocks ingest.

### 1.3 Port `MetadataEnricher` (Legacy: 869 lines)
*   **Target**: `src/omega/library/scholarly.py`
*   **Features**:
    *   ORCID integration for author identity resolution and disambiguation.
    *   OpenAlex / CrossRef integration for citation networks and venue metadata.
    *   ~~~Semantic Scholar integration for concept extraction.~~~ **DROPPED (R8)**: requires API key; use OpenAlex concepts instead.
    *   **Per-field provenance** (R6): `field_provenance` dict in `LibraryMetadata` for M22 compliance.
    *   **Privacy gate** (R1): external enrichment MUST be opt-in per WAD with observability logging — never silent external calls.
*   **Value**: Transforms basic author strings into verifiable scholarly identities. Graceful degradation (R4) — if enrichment fails, document still ingests.

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
    *   **Explicit retention (R9)**: reconcile tier retention policy — make per-tier retention explicit in `catalog.py prune()` (currently implicit/undefined).
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
    *   **WorkerCoordinator exists (R11)**: wire `ContentSource` pipeline into the existing `COORDINATOR` singleton — do not re-implement coordination logic.
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
    *   **FTS5 Migration First (R5)**: `catalog.py` currently uses `LIKE` queries — no FTS5 virtual table exists yet. Phase 4.2 requires migrating to a real SQLite FTS5 virtual table before BM25 tuning.
    *   Faceted search capabilities (filter by author, year, Dewey Decimal).
    *   BM25 tuning for the SQLite FTS5 index (post-migration).
*   **Value**: Instantaneous retrieval of exact knowledge blocks.

---

## 🔍 Architecture Review Insights (R1–R12, Carmack Session 55)

Captured during parallel architecture review of this roadmap. Applied inline above; full list for traceability:

| # | Insight | Applied To |
|---|---------|-----------|
| R1 | External enrichment (ORCID/OpenAlex) is a privacy leak — opt-in per WAD + observability logging | §1.3 MetadataEnricher |
| R2 | Reorder phases: 1.3 → 1.2 → 1.1 for quick wins | Phase 1 execution order |
| R3 | Persistent cache layer (SQLite/file) behind `api_clients.py` — in-memory lost on restart | §1.2 Resilience |
| R4 | Enrichment must degrade gracefully — never block ingest | §1.2, §1.3 |
| R5 | FTS5 does not exist yet — `catalog.py` uses `LIKE`; migrate to FTS5 virtual table first | §4.2 |
| R6 | Per-field provenance (`field_provenance` dict) for M22 compliance | §1.3 MetadataEnricher |
| R7 | Global API budget (`max_calls_per_session/day`) in `LibraryAPIConfig` | §1.2 Resilience |
| R8 | Drop Semantic Scholar from Phase 1.1 — requires key; use OpenAlex concepts | §1.3 MetadataEnricher |
| R9 | Reconcile retention policy — explicit per-tier retention in `catalog.py prune()` | §2.2 Tiering |
| R10 | Add M21 contract tests for external APIs using frozen fixtures | Implementation Directives #5 |
| R11 | WorkerCoordinator already exists — wire into `COORDINATOR` singleton | §3.2 Pipeline |
| R12 | Right-Approximation on legacy ports: target ≤30% of legacy LOC for modern AnyIO | Implementation Directives #6 |

---

## 📜 Implementation Directives (The Carmack Standard)

1.  **Mandate 1 (AnyIO Absolute)**: No `asyncio`. All parallel enrichment must use `anyio.create_task_group()`.
2.  **Mandate 9 (Error Integrity)**: All new modules must define specific `OmegaError` subclasses (e.g., `ScholarlyAPIError`, `ComplianceGateError`). No bare exceptions.
3.  **Carmack's Law (Axiom 02)**: When porting legacy code, **do not copy blindly**. Strip redundant abstractions. If a legacy 800-line file can be a 150-line modern AnyIO module, rewrite it.
4.  **Test-Driven Porting**: No legacy module is considered "ported" until it has >90% test coverage with mocked external dependencies.
5.  **M21 Contract Tests (R10)**: External API integrations MUST have contract tests using frozen fixtures — no live API calls in CI.
6.  **Right-Approximation Port Budget (R12)**: Target ≤30% of legacy LOC for the modern AnyIO equivalent. If a legacy 869-line enricher needs >260 lines modern, revisit the design.

---

*End of Roadmap. Track progress in `OMEGA_ENGINE.md` and `PIVOT_LOG.md`. Reviewed 2026-07-08 (Roc Racoon) — R1–R12 from Carmack handoff `ho_5b378d09a029`.*