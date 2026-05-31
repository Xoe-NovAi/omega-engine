# 🔱 Omega Engine — Legacy Library & Curation Deep Dive
# ⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_research ⬡ R39-ANALYSIS

**AP Token**: `AP-R39-LEGACY-AUDIT-v1.0.0`
**Status**: ✅ COMPLETE
**Date**: 2026-05-14

## 1. Executive Summary
This report details the audit of legacy curation and library systems from `xna-omega-legacy` and `omega-stack-legacy`. The goal was to reclaim proven patterns for the implementation of **The Sentinel (R-34)** while avoiding previous architectural failures.

The legacy systems utilized a three-tier flow: **Watcher (Sentinel) $\rightarrow$ Processor (Digestor/Worker) $\rightarrow$ Storage (Library/Qdrant)**. The most critical reclaimed assets are the **LLM-based Quality Scoring (0.0-1.0)** and the **Resource-Aware Gating** mechanism.

---

## 2. Implementation Audit: Legacy Map

### 2.1 Component Mapping
| Component | Legacy File | Primary Role | Key Technology |
| :--- | :--- | :--- | :--- |
| **Intake Sentinel** | `xna-omega-legacy/scripts/intake_sentinel.py` | Portal monitoring & file routing | `anyio`, `hashlib` |
| **Intake Digestor** | `xna-omega-legacy/src/omega/services/intake_digestor.py` | Agent dispatch for file analysis | `AgentOrchestrator` |
| **Curation Pipeline** | `omega-stack-legacy/.../curation_pipeline.py` | Multi-source (Web/RSS/Doc) ingestion | `BeautifulSoup`, `feedparser` |
| **Curation Worker** | `omega-stack-legacy/_archive/scripts/curation_worker.py` | Agent-bus driven background processing | `AgentBusClient`, `ResourceHub` |
| **Web Scraper** | `omega-stack-legacy/scripts/scrapers/html_scraper.py` | Raw HTML extraction | `aiohttp`, `bs4` |

---

## 3. Strategy Extraction: "High-Gnosis" Filtering

### 3.1 The Quality Scoring Pattern
The legacy system avoided "data swamp" syndrome by implementing a quality gate.
- **Mechanism**: An LLM-based assessment performed after text extraction.
- **Metric**: A float score from `0.0` to `1.0`.
- **Prompt Logic**: The LLM evaluated content based on:
    - **Relevance**: Alignment with target categories.
    - **Depth**: Substance vs. surface-level summary.
    - **Originality**: Value-add vs. redundant information.
    - **Clarity**: Writing quality.
- **Threshold**: Content with a score $\ge 0.8$ was flagged as `HIGH-GNOSIS` for priority ingestion.

### 3.2 Noise Reduction Patterns
- **Structural Cleaning**: Blacklisting HTML elements (`script`, `style`, `nav`, `footer`, `header`).
- **Content Targeting**: Prioritizing specific CSS selectors (`article`, `main`, `.content`, `.post-content`, `.entry-content`, `.article-body`).
- **Extension Filtering**: Strict `IGNORE_EXTENSIONS` list to prevent processing of binary, temp, or system files.

---

## 4. Failure Analysis: Lessons Learned

| Failure Mode | Cause | Lesson for The Sentinel |
| :--- | :--- | :--- |
| **OOM Crashes** | Intensive PDF/OCR processing on the main thread. | **Sovereign Gate**: Implement `wait_for_resource_availability()` (zRAM/RAM check) before starting heavy ingestion. |
| **Dependency Bloat** | Core pipeline depended on `pdfminer`, `pytesseract`, `magic`, and `docx`. | **Modular Extraction**: Move heavy extractors into separate "Extractor Agents" or containers. The Sentinel should only handle routing. |
| **Loop Conflicts** | Mixing `asyncio.run` inside `anyio` contexts. | **Pure AnyIO**: Stick strictly to `anyio` for all concurrency to ensure stability. |
| **Redundant Processing** | Simple in-memory `known` sets for deduplication. | **Persistent Hashing**: Use SHA-256 file hashes stored in a lightweight DB to prevent re-processing after restarts. |

---

## 5. Proven Patterns for R-34 (The Sentinel)

The following patterns are cleared for integration into the new Sentinel architecture:

1.  **The Portal Model**: Maintain `inbox` $\rightarrow$ `mining_queue` $\rightarrow$ `research` directories. This allows the user to signal priority by file location.
2.  **Subprocess Decoupling**: The Sentinel remains a lightweight watcher. It spawns the `Digestor` as a separate process to ensure a single corrupted file cannot crash the system.
3.  **The Gnosis Score**: Implement the `0.0-1.0` quality score as a mandatory metadata field for every ingested document.
4.  **Resource-Aware Gating**: The Sentinel must query the `ResourceGuard` before triggering "Heavy Digests" (e.g., OCR).
5.  **Politeness Policy**: Maintain `politeness_delay` for web crawling to avoid IP bans.

---

## 🛠️ Implementation Note for the Builder Agent
Do not port `curation_pipeline.py` as a monolith. Implement the **Sentinel** as a pure `anyio` watcher that dispatches tasks to the **ModelGateway**. Use the `BeautifulSoup` selectors identified in this report as the default "cleaning" configuration for the web-intake module.
