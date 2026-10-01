<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Technical Extraction Report: Sector A (Library & Ingestion)
**Sovereign Miner**: Roc Racoon
**Date**: 2026-07-02
**Source Partition**: `/home/arcana-novai/archive/foundation-legacy/versions/Xoe-NovAi/`
**Target Sector**: Library API Integrations & Ingestion Pipelines

---

## 1. API Integration Logic (High-Value)
Extracted from `library_api_integrations.py`. These patterns provide the foundation for an automated, local-first enrichment engine.

### 🌐 Core API endpoints
| Source | Search Endpoint | Detail/Metadata Endpoint | Key Requirement |
|--------|------------------|--------------------------|------------------|
| **Open Library** | `/search.json` | `/api/books` (`jscmd=details`) | `User-Agent` header |
| **Internet Archive** | `/advancedsearch.php` | `/metadata/{identifier}` | `mediatype:texts` filter |
| **Library of Congress** | `/books/services/web/search.json` | (Combined in search) | `fo=json` parameter |
| **Project Gutenberg** | `gutendex.com/books/search` | `gutendex.com/books/{id}` | Public domain focus |

### 🛠️ Implementation Patterns
- **Client Abstraction**: `BaseLibraryClient` provides a unified interface for `search()` and `get_by_identifier()`.
- **Resilience**: Uses `requests.Session` with a `urllib3.util.retry.Retry` strategy (backoff factor 0.5, retries on 500, 502, 504).
- **Efficiency**: 
    - **TTL-based Caching**: Local dictionary cache for API responses to minimize redundant network calls.
    - **Rate Limiting**: Explicit `_rate_limit()` method enforcing calls-per-period window.
- **Schema**: `LibraryMetadata` dataclass provides a unified structure for books, podcasts, and music, ensuring consistency across diverse providers.

---

## 2. Crawling & Curation Patterns
Extracted from `crawl.py`. These patterns are critical for expanding the engine's internal knowledge base.

### 🕷️ Source-Specific Extraction Logic
- **Project Gutenberg**: 
    - Workflow: Search $\rightarrow$ Link Extraction $\rightarrow$ Find `.txt` / `.txt.utf-8` $\rightarrow$ Content Cleaning.
    - **Header/Footer Stripping**: Uses markers (`*** START OF THIS PROJECT GUTENBERG EBOOK ***`) to isolate the actual book text from the wrapper.
- **arXiv**:
    - Workflow: Search $\rightarrow$ `/abs/` page parsing $\rightarrow$ PDF link generation (`/pdf/`).
    - **PDF Extraction**: Basic text extraction from PDF binaries via regex-based cleaning of non-printable characters.
- **PubMed**:
    - Workflow: Search $\rightarrow$ `/pubmed/` link extraction $\rightarrow$ Abstract/Journal extraction.
- **YouTube**:
    - Workflow: Search $\rightarrow$ `/watch?v=` link extraction $\rightarrow$ Metadata/Description extraction.

### 🛡️ Security & Sanitization (Sovereign-Grade)
- **Domain-Anchored Allowlist**: Implements a strict URL validation system that converts glob patterns (e.g., `*.gutenberg.org`) into anchored regexes (`^[^.]*\\.gutenberg\\.org$`) to prevent domain-bypass attacks.
- **Input Hardening**: 
    - `validate_safe_input()`: Whitelist regex for user queries to prevent command injection.
    - `sanitize_id()`: Strips non-alphanumeric characters from IDs to prevent path traversal.
- **Content Cleaning**: `sanitize_content()` removes `<script>` and `<style>` tags using `re.DOTALL` and collapses whitespace for cleaner LLM consumption.

---

## 3. Ingestion Pipeline & Scholarly Curation
Extracted from `ingest_library.py`. This represents the most advanced "Enterprise" logic in the legacy stack.

### ⛓️ The Ingestion Chain
`Source (API/RSS/Local)` $\rightarrow$ `SHA256 Deduplication` $\rightarrow$ `Quality Assessment` $\rightarrow$ `Library Enrichment` $\rightarrow$ `Scholarly Enhancement` $\rightarrow$ `FAISS Vectorstore`.

### 🎓 Scholarly Enhancement Logic
- **Language Detection**: Regex-based identification of Classical Greek (`\u0370-\u03FF`), Latin (common function words), and Hebrew (`\u0590-\u05FF`).
- **Historical Era Classification**: Hybrid approach using keywords (e.g., "Hellenistic", "Byzantine") and a known author-to-era mapping.
- **Citation Network Extraction**: Regex-based extraction of academic references using patterns like `cf.`, `see`, and `compare`.
- **Authority Scoring**: Publisher-based weightings (e.g., Oxford = 0.95, Cambridge = 0.94) to determine the "truth-weight" of a source.

### 🏗️ Infrastructure & Durability
- **Deduplication**: Uses a Redis-backed checksum store (30-day TTL) to prevent re-ingesting the same content across sessions.
- **Atomic Durability**: Implements `os.fsync` on the FAISS index and its parent directory to guarantee that index updates are written to physical disk, preventing corruption during crashes (Pattern 4).
- **Domain KBs**: `DomainKnowledgeBaseConstructor` builds specialized ontologies and "Expert Profiles" (e.g., "Plato Scholar") based on the ingested content.

---

## 🚀 Mapping to Omega Engine Needs

| Legacy Finding | Omega Engine Application | Priority | Dedup Status |
|----------------|--------------------------|----------|-------------|
| **Library Clients** | Implement in `src/omega/oracle/providers/` for autonomous research. | High | **NOVEL** — No equivalent in omega-engine. High-priority port. |
| **Domain-Anchored Allowlist** | Integrate into `TDP` (Tainted Data Protocol) for web security. | Critical | **UNCERTAIN** — `sanitize_content()` ported to pii_masker.py (Phase 3.3) but exact scope vs. legacy `crawl.py` allowlist unclear. |
| **Scholarly Curator** | Wire into `Verity` for high-fidelity academic auditing. | Medium | **NOVEL** — Skeptical Verifier does cross-referencing but not citation extraction or publisher authority scoring. |
| **Atomic fsync** | Apply to all `data/` writes to ensure sovereign state durability. | High | **PORTED** — `memory_store.py` already uses atomic writes (`os.fsync` on directory). |
| **Dewey Mapping** | Use in `EntityRegistry` for automatic domain routing. | Low | **NOVEL** — EntityRegistry uses keyword matching, not Dewey Decimal classification. |
| **Citation Networking** | Use in `Skeptical Verifier` to cross-reference claims across sources. | Medium | **EVOLVED** — Skeptical Verifier provides similar source cross-referencing via NLI-based Two-Source Rule, not regex citation patterns. |
