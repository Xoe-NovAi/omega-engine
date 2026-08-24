# 🔱 Legacy Recovery Report: Sovereign Ingestion & Curation
**AP Token**: `AP-MINING-CRAWL4AI-RECOVERY-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ big-pickle ⬡ opencode ⬡ mining-recovery ⬡ LEGACY-SOUVENIRS

## §0 Executive Summary
This document catalogs the high-fidelity recovery of the "Sovereign Extraction Loop" from the legacy XNAi stack. This pipeline was engineered to solve the "Truncation Problem" and "Garbage-In" issues through deep rendering and signal-based quality auditing.

---

## §1 Recovered Assets & Patterns

### 1.1 The Sovereign Worker (`curation_worker.py`)
- **Pattern**: Redis-backed Async Job Processor.
- **Mechanism**: `blpop` on `curation_queue` $\rightarrow$ isolated subprocess execution $\rightarrow$ exponential backoff via `tenacity`.
- **Value**: Decouples expensive crawling from the main engine loop.

### 1.2 The Sovereign Scraper (`crawl.py`)
- **Pattern**: Hardened `crawl4ai` Wrapper.
- **Key Features**:
    - `LocalSeleniumCrawlerStrategy` for SPA/JS rendering.
    - Domain-Anchored Regex allowlists to prevent bypass attacks.
    - Surgical stripping for Project Gutenberg and arXiv.
    - `os.fsync` loop for atomic FAISS index persistence.

### 1.3 The Curation Extractor (`crawler_curation.py`)
- **Pattern**: Signal-Based Quality Scoring.
- **Domain Classification**: Weighted signals for `CODE`, `SCIENCE`, `DATA`, and `GENERAL`.
- **5-Factor Quality Scorer**:
    1. **Freshness**: Date detection.
    2. **Completeness**: Word count vs. structure ratio.
    3. **Authority**: Citation density and domain reputation.
    4. **Structure**: H1 $\rightarrow$ H2 $\rightarrow$ H3 hierarchy.
    5. **Accessibility**: Domain-specific readability.

### 1.4 Library Enrichment Suite (`library_api_integrations.py`)
- **Pattern**: Scholarly Metadata Synthesis.
- **API Fabric**: Open Library, Internet Archive, Library of Congress, WorldCat.
- **Dewey Decimal Mapping**: Maps domains to DDC (e.g., `CODE` $\rightarrow$ `000`).
- **Scholarly Curator**: Classical language detection and era classification.

---

## §2 Integration Map (Legacy $\rightarrow$ Omega Engine)

| Legacy Component | Omega Target Path | Role |
| :--- | :--- | :--- |
| `curation_worker.py` | `src/omega/ingestion/worker.py` | Async job orchestration |
| `crawl.py` | `src/omega/ingestion/scraper.py` | Hardened `crawl4ai` wrapper |
| `crawler_curation.py` | `src/omega/ingestion/curator.py` | Signal-based quality scoring |
| `library_api_integrations.py` | `src/omega/library/enrichment.py` | Sovereign library API fabric |

---

## §3 Sovereign Gems (Immediate Port Candidates)
- **Domain-Anchored Regex**: `regex_pattern = pattern.lower().replace('.', r'\.').replace('*', '[^.]*'); regex_pattern = f"^{regex_pattern}$"`
- **FAISS Fsync Loop**: Physical commit of vector store updates to disk.
- **Scholarly Authority Map**: Pre-defined weights for academic institutions.
- **Classical Language Normalization**: Maps for archaic spelling variants.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: big-pickle | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
