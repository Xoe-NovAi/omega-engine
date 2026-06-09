# R-doc: Firecrawl Gotchas & Advanced Tips
**Version**: 1.0.0
**Status**: FINAL
**Date**: 2026-06-09
**Author**: researcher

## Executive Summary
This document provides a forensic analysis of the Firecrawl API and CLI, focusing on recent deprecations, advanced interaction patterns, and specialized modes (`lockdown`, `branding`). The primary shift in the Firecrawl ecosystem is the move toward **Agentic Extraction** (replacing `/extract` with `/agent`) and **Sovereign Retrieval** (via `lockdown` mode).

## 1. API Evolution & Deprecations
Firecrawl has transitioned from static extraction to dynamic agentic workflows.

### 1.1 Deprecated Endpoints
| Deprecated Endpoint | Successor | Note |
| :--- | :--- | :--- |
| `/v1/extract` / `/v2/extract` | `/agent` | Move from schema-based extraction to prompt-based agentic extraction. |
| `/v1/deep-research` | `/v2/search` | Deep research is now integrated into the enhanced Search API. |
| `/v1/llmstxt` | `llmstxt.new/` | Transitioned to a prefix-based utility for LLM-ready text. |

### 1.2 New High-Value Endpoints
- **`/parse`**: High-performance Rust-based engine for PDFs, Word, and spreadsheets (up to 50MB).
- **`/monitor`**: Webhook-driven change tracking with plain-English goal setting.
- **`/v2/search`**: Combines web search with full-page scraping in a single call.

## 2. Advanced Interaction & Edge Cases
The `/interact` endpoint transforms a scrape into a stateful browser session.

### 2.1 Iframe & Shadow DOM Handling
- **Automatic Traversal**: Firecrawl now handles nested iframes, cross-origin frames, and dynamically injected iframes automatically. No special configuration is required for basic iframe content extraction.
- **Wait Logic**: The system implements "Smart Automatic Wait," ensuring iframe content is fully loaded before extraction.
- **State Persistence**: Sessions persist across multiple `/interact` calls, allowing for complex multi-step workflows (e.g., Login $\rightarrow$ Navigate $\rightarrow$ Extract).

### 2.2 Interaction Patterns
- **Natural Language**: Use `prompt` for high-level actions ("Click the login button and enter credentials").
- **Code Mode**: Use Playwright (Node/Python) or Bash (`agent-browser`) for precision control.
- **Profiles**: Use named profiles to persist cookies and `localStorage` across different sessions.

## 3. Specialized Modes: Lockdown & Branding

### 3.1 Lockdown Mode (`lockdown: true`)
Designed for compliance-constrained and air-gapped environments.
- **Mechanism**: Forces the `/scrape` endpoint to read exclusively from Firecrawl's index/cache.
- **Security**: Zero outbound requests. No HTTP fetches, no `robots.txt` checks.
- **Data Retention**: Zero Data Retention (ZDR) by default.
- **Failure Mode**: Returns `404` with code `SCRAPE_LOCKDOWN_CACHE_MISS` if the URL is not cached.
- **Billing**: Cache hit (5 credits), Cache miss (1 credit).

### 3.2 Branding Format v2 (`formats: ['branding']`)
Extracts a site's visual identity into a structured format.
- **Capabilities**: Captures logo URLs, primary/secondary hex colors, font families, spacing scales, and UI component styles.
- **Improvements**: Now handles logos embedded in background images and sites built with modern builders (Wix, Framer).
- **Use Case**: Ideal for generating on-brand assets or personalized onboarding environments.

## 4. Troubleshooting & Gotchas

### 4.1 Common Error Codes
- **401 (Unauthorized)**: API key missing or invalid. Check `FIRECRAWL_API_KEY`.
- **429 (Too Many Requests)**: Rate limit exceeded. Check concurrency settings.
- **400 (Bad Request)**: Invalid query or unsupported action.

### 4.2 CLI vs API Discrepancies
- **Version Lag**: The CLI may occasionally lag behind the latest API features. Always check `firecrawl --version`.
- **Environment**: CLI relies on local `.env` or shell exports; API calls are direct.
- **Output**: CLI defaults to file-based output (`-o`), while API returns JSON.

## 5. Summary Table: Optimal Settings
| Goal | Recommended Setting | Format/Flag |
| :--- | :--- | :--- |
| **Air-gapped/Secure** | `lockdown: true` | `/scrape` |
| **Visual Identity** | `formats: ['branding']` | `/scrape` |
| **Fast Q&A** | `formats: ['question']` | `/scrape` |
| **Precise Snippets** | `formats: ['highlights']` | `/scrape` |
| **Document Parsing** | `/parse` | Multipart Upload |
| **Dynamic Flow** | `/interact` | `prompt` or `code` |
