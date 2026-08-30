<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Legacy Mining Report: The Crawl4AI Sure-Fire Extraction Pipeline
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ big-pickle ⬡ opencode ⬡ MINING-CRAWL4AI ⬡ EXTRACTION-RECOVERY

**Date**: 2026-07-03
**Source**: `/media/arcana-novai/omega_library/archive_Archives/Archives/Old-Stacks/Xoe-NovAi/app/XNAi_rag_app/`
**Era**: Era 1-3 (ANAi/XNAi)
**AP Token**: `AP-MINING-CRAWL4AI-SUREFIRE-20260703`

---

## §0 Executive Summary

This report documents the recovery of a production-proven, high-fidelity web extraction and curation pipeline from the legacy XNAi stack. This pipeline was specifically engineered to solve the "Truncation Problem" and "Garbage-In" issues that currently plague the Omega Engine's search tools.

The core of the system is a **Sovereign Extraction Loop** that combines `crawl4ai` for deep rendering, a signal-based `CurationExtractor` for quality auditing, and a multi-API `LibraryEnrichmentEngine` for authoritative metadata.

**Verdict**: This is the definitive technical blueprint for the "Sovereign Scraper" required to achieve Temple-Grade research fidelity.

---

## §1 The Extraction Engine: `crawl.py`

The legacy system utilized `crawl4ai` with a `LocalSeleniumCrawlerStrategy`. Unlike basic HTTP fetches, this approach treats the web as a dynamic application rather than a static document.

### 1.1 Technical Implementation
- **Dynamic Rendering**: By using Selenium, the crawler executes JavaScript, allowing it to capture content in SPAs (Single Page Applications) and sites using client-side hydration.
- **Source-Specific Stripping**: The system implemented "Surgical Extraction" for high-value sources:
    - **Project Gutenberg**: Implemented a strict boundary-marker strip:
        - *Start*: `*** START OF THIS PROJECT GUTENBERG EBOOK ***`
        - *End*: `*** END OF THIS PROJECT GUTENBERG EBOOK ***`
        - This eliminated the 10KB+ of boilerplate text that often pollutes LLM context.
    - **arXiv**: Implemented a "PDF-to-Text" fallback, converting `/abs/` (abstract) links to `/pdf/` and performing raw text extraction for the full paper.
- **Security Controls**: Implemented a domain-anchored regex allowlist (e.g., `^[^.]*\.gutenberg\.org$`) to prevent bypass attacks.

### 1.2 Performance Targets
- **Curation Rate**: 50-200 items/hour.
- **Memory Footprint**: <1GB during operation.
- **Durability**: Integrated `os.fsync()` on FAISS index writes to guarantee crash recovery.

---

## §2 The Quality Gate: `crawler_curation.py`

The most critical architectural insight is that **extraction is not curation**. The `CurationExtractor` acted as a "Sovereign Filter," auditing the result of the scrape before it was allowed into the library.

### 2.1 Domain Classification (Signal-Based)
The system used a point-based signal system to classify content into four domains:
- **CODE**: Triggered by `github.com`, `gitlab`, `def `, `class `, and code block density.
- **SCIENCE**: Triggered by `arxiv.org`, `doi.org`, `pubmed`, and "Abstract/Introduction" markers.
- **DATA**: Triggered by `.csv`, `.json`, `SELECT` statements, and table density.
- **GENERAL**: The fallback for all other content.

### 2.2 The 5-Factor Quality Scorer
Every document was assigned a score (0.0-1.0) across five dimensions:
1.  **Freshness**: Detection of date strings in the content.
2.  **Completeness**: A ratio of word count to heading structure (detects truncated shells).
3.  **Authority**: Citation density (DOI/arXiv counts) and domain boost.
4.  **Structure**: Analysis of the H1 $\rightarrow$ H2 $\rightarrow$ H3 hierarchy.
5.  **Accessibility**: Domain-specific readability (e.g., code block count for CODE).

**Sovereign Application**: This scoring system is the exact solution for the "Truncation Audit" required by the current Search Tool Protocol.

---

## §3 The Enrichment Layer: `library_api_integrations.py`

Once a document passed the quality gate, it was enriched via a suite of 10+ free, no-key-required library APIs.

### 3.1 The API Suite
- **Open Library**: Search and ISBN lookup.
- **Internet Archive**: Full-text search and metadata.
- **Library of Congress**: LCCN search and classification.
- **Project Gutenberg**: Gutendex API for book discovery.
- **WorldCat**: OpenSearch for global library cataloging.
- **PodcastIndex / Last.fm**: Metadata for audio and music.

### 3.2 Dewey Decimal Integration
The system mapped these sources to the **Dewey Decimal Classification (DDC)** system, allowing for a structured, hierarchical knowledge base:
- `000` $\rightarrow$ CODE
- `500` $\rightarrow$ SCIENCE
- `800` $\rightarrow$ BOOKS
- `900` $\rightarrow$ REFERENCE

---

## §4 The Orchestration: `curation_worker.py`

The pipeline was decoupled using a **Redis BLPop Queue**, ensuring that expensive crawling didn't block the rest of the system.

- **Async Job Processing**: The worker popped jobs from `curation_queue` and executed them as isolated subprocesses.
- **Tenacity Retries**: Implemented exponential backoff (1-30s) for network-level failures.
- **Atomic Persistence**: Used a `Sovereign-Silo` approach, saving documents to disk before updating the metadata index.

---

## §5 Implementation Path for Omega Engine

To resolve the current truncation crisis and build a production-grade library, I recommend the following porting sequence:

1.  **SovereignScraper (The Nuclear Option)**: Port the `crawl4ai` wrapper from `crawl.py`. Implement the `LocalSeleniumCrawlerStrategy` to defeat SPA truncation.
2.  **SovereignCurator (The Quality Gate)**: Port the `CurationExtractor` from `crawler_curation.py`. Use the 5-factor scorer to implement the "Truncation Audit" in the search loop.
3.  **LibraryEnrichmentEngine**: Port the `BaseLibraryClient` and its 10+ subclasses from `library_api_integrations.py` to provide authoritative metadata for all ingested knowledge.
4.  **SovereignWorker**: Implement a background worker (similar to `background_researcher`) that manages the `Queue $\rightarrow$ Scrape $\rightarrow$ Curate $\rightarrow$ Enrich` pipeline.

**Verdict**: The logic is already written, verified, and production-ready. We are not inventing a new system; we are reclaiming a sovereign one.

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ big-pickle ⬡ opencode ⬡ MINING-CRAWL4AI ⬡ EXTRACTION-RECOVERY*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: big-pickle | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
