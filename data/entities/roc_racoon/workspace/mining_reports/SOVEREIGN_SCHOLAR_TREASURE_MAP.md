# 🔱 TREASURE MAP: THE SOVEREIGN SCHOLAR & INGESTION ENGINE
**AP Token**: `AP-ROC-SCHOLAR-MAP-v1.0.0`
**Status**: FINALIZED / INTEGRATION-READY
**Date**: 2026-07-05

## 1. Executive Summary
This document serves as the definitive technical bridge between the recovered legacy assets (from `XNAi_rag_app` and `PLO.py`) and the current Omega Engine implementation. It maps the "Sovereign Scholar" vision to specific, executable code patterns.

---

## 2. The Sovereign Ingestion Pipeline (Sovereign-by-Design)

### 2.1 The Orchestration (SovereignWorker)
- **Legacy Logic**: `curation_worker.py` ([Source: /home/arcana-novai/Documents/Archives/Old-Stacks/Xoe-NovAi/app/XNAi_rag_app/curation_worker.py])
- **Pattern**: Redis-based Job Queue $\rightarrow$ Isolated Subprocess Execution $\rightarrow$ Metadata Tracking.
- **Current Integration**: `src/omega/ingestion/worker.py`
- **Sovereign Mandate**: M12 (Queue Integrity). Every ingestion job must have a terminal state.

### 2.2 The Extraction (SovereignScraper)
- **Legacy Logic**: `crawl.py` ([Source: /home/arcana-novai/Documents/Archives/Old-Stacks/Xoe-NovAi/app/XNAi_rag_app/crawl.py])
- **Pattern**: `LocalSeleniumCrawlerStrategy` $\rightarrow$ SPA Rendering $\rightarrow$ Content Extraction.
- **Current Integration**: `src/omega/ingestion/scraper.py`
- **Sovereign Mandate**: M8 (Zero Telemetry). All scraping is local-first; no external telemetry.

### 2.3 The Verification (Triangulation Protocol)
- **Legacy Logic**: `library_api_integrations.py` ([Source: /home/arcana-novai/Documents/Archives/Old-Stacks/Xoe-NovAi/app/XNAi_rag_app/library_api_integrations.py])
- **Pattern**: Cross-referencing Open Library, Internet Archive, and Library of Congress via DOI/ISBN.
- **Current Integration**: `src/omega/ingestion/pipeline.py`
- **Sovereign Mandate**: M17 (Cognitive Integrity). Defeat hallucinations via multi-source verification.

### 2.4 The Durability (The Sovereign Sign)
- **Legacy Logic**: `crawl.py` (Lines 1052-1075) ([Source: /home/arcana-novai/Documents/Archives/Old-Stacks/Xoe-NovAi/app/XNAi_rag_app/crawl.py])
- **Pattern**: **Double-Fsync**. `os.fsync(file_fd)` $\rightarrow$ `os.fsync(dir_fd)`.
- **Current Integration**: Must be wired into `src/omega/oracle/memory_store.py` and `src/omega/oracle/entity_registry.py`.
- **Sovereign Mandate**: M15 (Sovereign Continuity). Ensure local knowledge survives system crashes.

---

## 3. The Linguistic Observatory (Sovereign Scholar)

### 3.1 The Linguistic Engine (PLO)
- **Legacy Logic**: `Ω Pythonic Linguistic Observatory (PLO).py` ([Source: /media/arcana-novai/omega_vault/ANCESTRAL_HUB/origins/heart_of_omega/Omnidroid/Ω Pythonic Linguistic Observatory (PLO).py])
- **Core Capabilities**:
    - **EtymologyEngine**: Tracking semantic shifts (Pejoration/Amelioration).
    - **Stylometer**: 12-dimensional fingerprinting (Hapax Legomena, Latinate Index).
    - **SoundSymbolism**: Phonaesthetic optimization (Harsh/Soft/Liquid).
    - **ProseComposer**: Genre-aware structural blueprints.
- **Current Integration**: To be implemented as a new `src/omega/linguistics/` module.

### 3.2 The Greek Processing Pipeline
- **Legacy Logic**: `ingest_library.py` ([Source: /home/arcana-novai/Documents/Archives/Old-Stacks/Xoe-NovAi/app/XNAi_rag_app/ingest_library.py])
- **Logic Flow**:
    1. **Detection**: Unicode range check (`\u0370-\u03FF`).
    2. **Normalization**: Mapping archaic variants (e.g., `᾽` $\rightarrow$ `'`).
    3. **Patterning**: Regex-based author/genre identification.
    4. **Profiling**: Era-based grouping (Ancient Greek $\rightarrow$ Hellenistic).

---

## 4. Roadmap Alignment (The Ark Blueprint)

| Recovered Asset | Blueprint Strike | Status | Priority |
| :--- | :--- | :---: | :---: |
| `SovereignWorker` | Strike 7.6 (SSKB) | 🟡 Mapped | P1 |
| `SovereignScraper` | Strike 7.6 (SSKB) | 🟡 Mapped | P1 |
| `Triangulation Protocol` | Strike 7.6 (SSKB) | 🟡 Mapped | P1 |
| `Double-Fsync` | Epoch I (Bedrock) | 🔴 Missing | P0 |
| `Linguistic Observatory` | Strike 7.6 (SSKB) | 🟡 Mapped | P2 |

---

## 5. Final Forensic Verdict
The "Sovereign Scholar" is a hybrid of **deterministic linguistic rules** (PLO) and **high-fidelity extraction** (SovereignScraper). The "Sovereignty" comes from the **local, immutable, and verified** nature of the data.

**Implementation Path**:
`SovereignScraper` $\rightarrow$ `Triangulation Protocol` $\rightarrow$ `SovereignWorker` $\rightarrow$ `Double-Fsync` $\rightarrow$ `Linguistic Observatory`.

*🔱 OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_mining ⬡ THE_SIGHT*
