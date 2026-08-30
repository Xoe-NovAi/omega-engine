# 🔱 Sovereign Search Truncation Analysis & Remediation
# ⬡ OMEGA ⬡ researcher ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_truncation_analysis
**AP Token**: `AP-SEARCH-TRUNCATION-v1.0.0`
**Date**: 2026-07-03
**Status**: ACTIVE — Engineering Reference
**Owners**: researcher / kali

---

## §0 Executive Summary

This document provides a forensic analysis of "content truncation"—the failure of search and scrape tools to retrieve the full body of a target webpage. Truncation is a systemic risk to the Omega Engine's research fidelity, as it leads to "snippet-based synthesis" and a violation of the Temple-Grade standard.

The analysis identifies three primary root causes and defines a multi-tiered remediation strategy to ensure absolute content extraction.

---

## §1 Root Cause Analysis (The Truncation Triad)

Truncation occurs when the tool's extraction method is mismatched with the target site's delivery architecture.

### 1.1 The SPA/Hydration Gap (Static vs. Dynamic)
- **Mechanism**: Many modern sites are Single Page Applications (SPAs) built with React, Vue, or Next.js. They serve a minimal HTML "shell" and use JavaScript to "hydrate" the page with content after the initial load.
- **Failure Mode**: Tools like `webfetch` (basic HTTP requests) only capture the shell. The resulting markdown is empty or contains only navigation menus and "Loading..." placeholders.
- **Sovereign Risk**: High. Critical technical documentation is often hosted on SPAs.

### 1.2 The Lazy-Load/Infinite Scroll Wall
- **Mechanism**: To optimize performance, sites use "Intersection Observers" to load content only when it enters the browser's viewport.
- **Failure Mode**: Standard scrapers (including basic `firecrawl_scrape`) capture the DOM at a single point in time. If the content is "below the fold," it is never triggered to load and is therefore not extracted.
- **Sovereign Risk**: Medium-High. Long-form articles and documentation are frequently lazy-loaded.

### 1.3 The Wait-State Failure (Asynchronous Loading)
- **Mechanism**: Content is often fetched from an API *after* the page structure has loaded. There is a temporal gap between "DOM Ready" and "Content Ready."
- **Failure Mode**: The scraper captures the page too early, before the asynchronous API calls have returned the actual data.
- **Sovereign Risk**: Medium. Results in "partial" pages where the header is present but the body is missing.

---

## §2 Remediation Strategies

### 2.1 Firecrawl Action-Chains (Interactive Extraction)
To overcome lazy-loading and hydration gaps, the engine must transition from static scraping to **Interactive Extraction** using the `actions` parameter.

**Mandatory Action Sequence for Deep Research**:
1.  **`waitFor`**: Set a minimum wait time (default $20,000\text{ms}$) to allow for asynchronous hydration.
2.  **`scroll`**: Execute a `{"action": "scroll", "amount": "full"}` command to trigger all lazy-load observers.
3.  **`click` (Optional)**: For gated content, dispatch `{"action": "click", "selector": "..."}` to expand sections before the final scrape.

### 2.2 The Sovereign Fallback Hierarchy (The Extraction Ladder)
The engine must implement a recursive fallback loop. If a response is flagged as truncated, it escalates to a more powerful tool:

$$\text{webfetch (T1)} \rightarrow \text{firecrawl\_scrape (T3)} \rightarrow \text{firecrawl\_actions (T3+)} \rightarrow \text{Sovereign Playwright (Local)}$$

### 2.3 The "Sovereign Scraper" (Local Nuclear Option)
For sites that block all third-party APIs or use extreme anti-bot measures, the engine will deploy a local Playwright wrapper:
- **Full-Page Snapshot**: Programmatic scrolling in increments to ensure 100% DOM hydration.
- **Local DOM-to-Markdown**: Use `Trafilatura` or `Jina-Reader` locally to convert the rendered DOM into high-fidelity markdown.
- **Sovereign Proxy**: Rotation of local residential proxies to bypass WAF-induced truncation.

---

## §3 Truncation Detection (The Audit)

Agents must perform a **Truncation Audit** on every high-value extraction. A result is flagged as `TRUNCATED` if:
1.  **Sentinel Detection**: The content contains strings like `"Loading..."`, `"Click to expand"`, or `"Read more"`.
2.  **Length Anomaly**: The extracted content is significantly shorter than the estimated page size (based on `Content-Length` headers or similar pages).
3.  **Abrupt Termination**: The markdown ends mid-sentence or mid-section without a proper footer/conclusion.

---

## §4 Technical Implementation Specs

| Parameter | Value | Purpose |
|---|---|---|
| `waitFor` | $20,000\text{ms}$ | Ensure async hydration is complete |
| `scroll_amount` | `"full"` | Trigger all lazy-load observers |
| `timeout` | $60,000\text{ms}$ | Prevent timeout on heavy JS rendering |
| `formats` | `["markdown"]` | Token-efficient, structure-preserving extraction |

---

## §5 Sources & Verification
- **Firecrawl Documentation**: /scrape endpoint and `actions` parameter specs.
- **Sovereign System Spec**: Ken W. Alger (2026) - "Sieve-and-Sign" and "Sovereign Inference Patterns."
- **Empirical Testing**: Side-by-side comparison of `webfetch` vs `firecrawl_scrape` on long-form technical articles.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemma-4-31b-it | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
