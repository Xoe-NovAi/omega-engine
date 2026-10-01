<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — R-01 Firecrawl Core Capabilities
# ⬡ OMEGA ⬡ researcher ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_research ⬡ R01

**AP Token**: `AP-RESEARCH-R01-v1.0.0`
**Author**: researcher (Sovereign Master Researcher)
**Date**: 2026-06-09
**Status**: READY

---

## Summary
This document provides a comprehensive architectural audit of Firecrawl's core data acquisition endpoints: `/map`, `/scrape`, and `/crawl`. It establishes a decision matrix for tool selection based on the required scope, speed, and depth of data extraction, and documents the cost-performance trade-offs of each method.

## Findings

### 1. Tool Selection Matrix (Capability Matrix)

| Use Case | Recommended Tool | Primary Mechanism | Cost | Performance |
| :--- | :--- | :--- | :--- | :--- |
| **URL Discovery** | `/map` | Sitemap + SERP + Cache | 1 credit/call | Extremely Fast |
| **Single Page Extraction** | `/scrape` | Direct Fetch + JS Render | 1 credit/page | Fast |
| **Bulk Domain Extraction** | `/crawl` | Recursive Link Traversal | 1 credit/page | Slow (Async) |
| **Targeted Site Search** | `/map` (with `search`) | Filtered URL Discovery | 1 credit/call | Fast |
| **Deep Site Coverage** | `/crawl` | Sitemap + Recursive | 1 credit/page | Thorough |

### 2. Endpoint Deep-Dive

#### 2.1 The `/map` Endpoint
- **Purpose**: Rapidly identify all indexed URLs on a website.
- **Mechanism**: Prioritizes sitemaps, supplemented by search engine results and cached crawl data.
- **Key Feature**: The `search` parameter allows for filtered URL discovery (e.g., finding all "docs" pages).
- **Trade-off**: Prioritizes speed over absolute completeness. For 100% coverage, `/crawl` is required.

#### 2.2 The `/scrape` Endpoint
- **Purpose**: Convert a specific URL into LLM-ready markdown or structured data.
- **Capabilities**:
    - **JS Rendering**: Handles SPAs and dynamic content.
    - **Multi-Format**: Supports `markdown`, `html`, `rawHtml`, `links`, `images`, `summary`, `branding`, `audio`, `video`, `json`, and `query`.
    - **Advanced Controls**: `waitFor` (delay), `maxAge` (cache control), `mobile` (emulation), and `onlyMainContent` (boilerplate removal).
- **Cost**: 1 base credit + format-specific add-ons (e.g., JSON/Question/Highlights cost +4 credits).

#### 2.3 The `/crawl` Endpoint
- **Purpose**: Recursively discover and scrape an entire website or specific sub-sections.
- **Mechanism**: Combines sitemap discovery with recursive link traversal.
- **Control Parameters**:
    - `limit`: Max pages to crawl (default 10,000).
    - `maxDiscoveryDepth`: Max hops from root.
    - `includePaths` / `excludePaths`: Regex-based path filtering.
    - `crawlEntireDomain`: Allows following links to sibling/parent paths.
- **Delivery**: Results via polling, WebSockets, or Webhooks.

### 3. Optimal Workflows

- **Discovery Workflow**: `/map` (with `search`) $\rightarrow$ Filter URLs $\rightarrow$ `/scrape` (targeted).
- **Bulk Workflow**: `/crawl` (with `includePaths`) $\rightarrow$ Process results.
- **Verification Workflow**: `/scrape` (with `maxAge: 0`) $\rightarrow$ Compare with cached version.

## Recommendations

1. **Implement a "Discovery-First" Pattern**: For any research task, the agent should first call `/map` to understand the site structure before committing credits to a full `/crawl`.
2. **Use `maxAge` for Performance**: Set `maxAge` to a non-zero value (e.g., 1 hour) for non-critical data to increase speed by up to 5x.
3. **Leverage `onlyMainContent`**: Always default to `true` for LLM context to minimize token noise.

## Sources
- [Firecrawl Scrape Docs](https://docs.firecrawl.dev/features/scrape) — accessed 2026-06-09
- [Firecrawl Crawl Docs](https://docs.firecrawl.dev/features/crawl) — accessed 2026-06-09
- [Firecrawl Map Docs](https://docs.firecrawl.dev/features/map) — accessed 2026-06-09
- File: `.firecrawl/feature-scrape.md`
- File: `.firecrawl/feature-crawl.md`
- File: `.firecrawl/feature-map.md`

## Implementation Note
_For: P6 Cognition / ModelGateway_
When implementing the Firecrawl provider, the `ModelGateway` should expose three distinct methods: `map_site()`, `scrape_url()`, and `crawl_domain()`. The `map_site` method should be the default entry point for any "find information on site X" query to optimize credit usage and latency.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemma-4-31b-it | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
