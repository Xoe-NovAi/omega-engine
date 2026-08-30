<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — R_FIRECRAWL_COMPLETE: Sovereign Data Acquisition
# ⬡ OMEGA ⬡ jem_synthesis ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_synthesis ⬡ TEMPLE-GRADE

**AP Token**: `AP-RESEARCH-FIRECRAWL-COMPLETE-v1.0.0`
**Author**: jem_synthesis (Tier 2 Research Agent)
**Date**: 2026-06-12
**Status**: FINAL / TEMPLE-GRADE
**Scope**: Comprehensive technical reference for Firecrawl integration within the Omega Engine.

---

## §0 Executive Summary

Firecrawl serves as the primary Tier 2 data acquisition layer for the Omega Engine, bridging the gap between broad web search and deep, structured data extraction. This document synthesizes six research reports into a single authoritative guide, detailing the transition from static scraping to **Agentic Extraction** and **Sovereign Retrieval**.

The core philosophy of Firecrawl's integration is **"Cache-First, Scrape-Last."** Given the finite credit budget, the Omega Engine employs a tiered discovery pattern: `/map` for structure $\rightarrow$ `/scrape` for targeted content $\rightarrow$ `/crawl` or `/agent` for deep synthesis. This ensures maximum data fidelity with minimum resource expenditure.

---

## §1 Core Capabilities & Setup

### 1.1 Tool Selection Matrix
The following matrix governs the selection of Firecrawl endpoints based on the research objective:

| Use Case | Recommended Tool | Primary Mechanism | Cost | Performance |
| :--- | :--- | :--- | :--- | :--- |
| **URL Discovery** | `/map` | Sitemap + SERP + Cache | 1 credit/call | Extremely Fast |
| **Single Page Extraction** | `/scrape` | Direct Fetch + JS Render | 1 credit/page | Fast |
| **Bulk Domain Extraction** | `/crawl` | Recursive Link Traversal | 1 credit/page | Slow (Async) |
| **Targeted Site Search** | `/map` (with `search`) | Filtered URL Discovery | 1 credit/call | Fast |
| **Deep Site Coverage** | `/crawl` | Sitemap + Recursive | 1 credit/page | Thorough |

### 1.2 Endpoint Deep-Dive

#### 1.2.1 The `/map` Endpoint
- **Purpose**: Rapidly identify all indexed URLs on a website.
- **Mechanism**: Prioritizes sitemaps, supplemented by search engine results and cached crawl data.
- **Key Feature**: The `search` parameter allows for filtered URL discovery (e.g., finding all "docs" pages).
- **Trade-off**: Prioritizes speed over absolute completeness.

#### 1.2.2 The `/scrape` Endpoint
- **Purpose**: Convert a specific URL into LLM-ready markdown or structured data.
- **Capabilities**:
    - **JS Rendering**: Handles SPAs and dynamic content.
    - **Multi-Format**: Supports `markdown`, `html`, `rawHtml`, `links`, `images`, `summary`, `branding`, `audio`, `video`, `json`, and `query`.
    - **Advanced Controls**: `waitFor` (delay), `maxAge` (cache control), `mobile` (emulation), and `onlyMainContent` (boilerplate removal).
- **Cost**: 1 base credit + format-specific add-ons (e.g., JSON/Question/Highlights cost +4 credits).

#### 1.2.3 The `/crawl` Endpoint
- **Purpose**: Recursively discover and scrape an entire website or specific sub-sections.
- **Mechanism**: Combines sitemap discovery with recursive link traversal.
- **Control Parameters**:
    - `limit`: Max pages to crawl (default 10,000).
    - `maxDiscoveryDepth`: Max hops from root.
    - `includePaths` / `excludePaths`: Regex-based path filtering.
    - `crawlEntireDomain`: Allows following links to sibling/parent paths.
- **Delivery**: Results via polling, WebSockets, or Webhooks.

### 1.3 Optimal Workflows
- **Discovery Workflow**: `/map` (with `search`) $\rightarrow$ Filter URLs $\rightarrow$ `/scrape` (targeted).
- **Bulk Workflow**: `/crawl` (with `includePaths`) $\rightarrow$ Process results.
- **Verification Workflow**: `/scrape` (with `maxAge: 0`) $\rightarrow$ Compare with cached version.

---

## §2 Advanced Extraction & Dynamic Interaction

### 2.1 Agentic Extraction & The FIRE-1 Agent
Firecrawl has transitioned from static extraction to dynamic agentic workflows.

- **The FIRE-1 Agent**: An autonomous AI agent that controls a browser to navigate complex structures. Unlike standard extraction, FIRE-1 can perform multi-step navigation (e.g., "Go to the forum, find the latest thread on X, and extract all comments").
- **Configuration**: Supports model selection (`spark-1-mini` for cost, `spark-1-pro` for accuracy) and `strictConstrainToURLs` to prevent agent drift.
- **Endpoint**: `/agent` (Successor to `/extract`).

### 2.2 Dynamic Interaction via `/interact`
The `/interact` endpoint enables stateful browser sessions.

#### 2.2.1 The Interaction Lifecycle
1. **Initialization**: A `/scrape` call is made, returning a `scrapeId`.
2. **Execution**: One or more `/interact` calls are made using the `scrapeId`. The browser session remains open, preserving state (DOM, cookies, scroll position).
3. **Termination**: A `DELETE` call stops the session and saves profile changes.

#### 2.2.2 Execution Modes
| Mode | Interface | Control Level | Best Use Case |
| :--- | :--- | :--- | :--- |
| **Prompting** | Natural Language | Low (Agentic) | Simple tasks: "Click login", "Search for X" |
| **Node.js** | Playwright API | High (Deterministic) | Complex logic, precise selectors, custom JS |
| **Python** | Playwright API | High (Deterministic) | Data science pipelines, Python-based automation |
| **Bash** | `agent-browser` CLI | Medium (LLM-Optimized) | Rapid prototyping, accessibility-tree based navigation |

#### 2.2.3 `agent-browser` (Bash Mode)
Specialized CLI providing an **Accessibility Tree** where elements are tagged with refs (e.g., `@e1`).
- `snapshot -i`: Returns only interactive elements.
- `click @e1`: Clicks the referenced element.
- `fill @e1 "text"`: Clears and types into a field.

#### 2.2.4 Persistent Profiles
Named profiles persist browser state (cookies, `localStorage`) across sessions.
- **Mechanism**: Pass a `profile` object (`{ "name": "my-profile", "saveChanges": true }`) to the initial `/scrape` call.
- **Read-Only Mode**: `saveChanges: false` allows concurrent sessions without modification.

### 2.3 Structured Extraction Strategies
| Method | Endpoint | Input | Best Use Case | Cost |
| :--- | :--- | :--- | :--- | :--- |
| **Schema-Based** | `/scrape` (json) | URL + JSON Schema | Known structure, single page | 1 + 4 credits |
| **Prompt-Based** | `/scrape` (json) | URL + Prompt | Exploratory, flexible structure | 1 + 4 credits |
| **Multi-URL** | `/extract` | URLs[] + Schema/Prompt | Consistent data across multiple pages | Per page |
| **Autonomous** | `/agent` (FIRE-1) | Prompt + URLs[] | Complex navigation, multi-page synthesis | High |

#### 2.3.1 Design Best Practices
- **Prompt Engineering**: Be specific ("Extract monthly price for 'Pro' plan including currency") and constraint-based ("Return only the value").
- **Schema Design**: Use strong typing (`string`, `number`), define a `required` array, and utilize nested objects for related data.

### 2.4 Specialized Modes
- **Lockdown Mode (`lockdown: true`)**: Forces `/scrape` to read exclusively from Firecrawl's index/cache. Zero outbound requests. Returns `404` with `SCRAPE_LOCKDOWN_CACHE_MISS` on cache miss.
- **Branding Format v2 (`formats: ['branding']`)**: Extracts visual identity (logo URLs, hex colors, font families, spacing scales).

---

## §3 Monitoring, Credits, and Caching

### 3.1 Monitoring & Change Detection
Firecrawl's `/monitor` endpoint enables recurring data acquisition and automated change detection.

- **Architecture**: Scheduled jobs (Cron or natural language) that compare results against the last snapshot.
- **Meaningful Change Judging**: An AI-driven system that evaluates diffs against a plain-language `goal` (e.g., "Alert when price drops below $50"). Returns a `judgment` object (`meaningful`, `confidence`, `reason`).
- **Tracking Modes**:
    - **Markdown**: Unified Text Diff (`diff.text`).
    - **JSON**: Per-field Diff (`diff.json`) keyed by JSON path.
    - **Mixed**: Both.

### 3.2 Credit Economics & Guardrails
Given the limited free tier (1,000 credits/month), the following protocol is mandatory:

| Operation | Estimated Cost | Description |
|----------|-----------------|---------------------------------------------------|
| `scrape` | 1 credit | Single page extraction. |
| `search` | 1-5 credits | Web search with optional scraping. |
| `crawl` | 1 credit / page | Bulk extraction. |
| `agent` | 5-20 credits | AI-powered structured extraction. |
| `map` | Minimal | URL discovery. |

**Credit Thresholds:**
- **Safe Zone (> 200)**: Standard execution.
- **Caution Zone (100-200)**: Disable `crawl` and `agent`; prioritize `scrape` and `websearch`.
- **Exhaustion Zone (< 100)**: Mandatory fallback to Tier 1 (`websearch`) and Tier 0 (Local Cache).

### 3.3 Sovereign Caching Strategy (Tier 0)
All Firecrawl outputs MUST be cached locally to prevent redundant expenditure.
- **Root**: `.firecrawl/`
- **Naming**: `{site}-{path}.md`
- **Workflow**: Check Cache $\rightarrow$ Evaluate Freshness (< 7 days) $\rightarrow$ Escalate to Firecrawl $\rightarrow$ Commit to Cache.

---

## §4 Implementation Guide (Omega Engine Integration)

### 4.1 ModelGateway (P6 Cognition)
The `ModelGateway` must expose the following interface:
- `map_site()`: Default entry point for site discovery.
- `scrape_url()`: Targeted extraction.
- `crawl_domain()`: Bulk recursive extraction.
- `structured_extract(pydantic_model)`: Converts Pydantic models to JSON schemas for `/scrape` or `/extract`.
- `BrowserSession` Class: Manages `scrapeId` and the lifecycle of `/interact` (including `stop_interaction()`).

### 4.2 WatchTower (P8 Observability)
The `WatchTower` entity should utilize `/monitor` to track health and content of critical external dependencies. The `monitor.page` webhook should be integrated into the Omega Engine's event bus to trigger "Sovereign Alerts."

### 4.3 Sovereign Search (SR-V1)
The `sovereign-search` skill must implement a **Credit-Sensing Guard**:
- Call `firecrawl --status` before Tier 2 operations.
- If credits < 100, automatically downgrade to Tier 1 (`websearch`) or Tier 3 (Hub Research) and log `[CREDIT-LOW]`.

---

## §5 Failure Modes & Edge Cases

### 5.1 Error Handling Matrix
| Error | Meaning | Action |
|-------|---------|--------|
| **400** | Bad Request | Validate query/action. |
| **401** | Unauthorized | Check `FIRECRAWL_API_KEY`. |
| **402** | Credits Exhausted | Fall back to Tier 1 $\rightarrow$ Tier 3. |
| **429** | Rate Limited | Exponential backoff (5s $\rightarrow$ 15s $\rightarrow$ 30s). |
| **500** | Server Error | Retry once $\rightarrow$ Fall back to Tier 1. |

### 5.2 Specific Edge Cases
- **Lockdown Cache Miss**: Returns `404` with code `SCRAPE_LOCKDOWN_CACHE_MISS`.
- **CLI vs API**: The CLI may lag behind API features. Always verify `firecrawl --version`.
- **Iframe Handling**: Firecrawl handles nested and cross-origin iframes automatically via "Smart Automatic Wait."

---

## §6 Heritage Attribution

This document is a synthesis of the following research assets:
- `R_FIRECRAWL_CORE_CAPABILITIES.md` (R-01)
- `R_FIRECRAWL_EXTRACTION_STRATEGIES.md` (R-02)
- `R_FIRECRAWL_DYNAMIC_INTERACTION.md` (R-03)
- `R_FIRECRAWL_MONITORING_SYSTEM.md` (R-04)
- `R_FIRECRAWL_ADVANCED.md` (Forensic Analysis)
- `R_FIRECRAWL_CREDIT_PROTOCOL.md` (Sovereign Caching)

**External Sources**:
- Firecrawl Official Documentation (Scrape, Crawl, Map, Extract, Interact, Monitoring)
- `agent-browser` GitHub Repository (Vercel Labs)

---
*⬡ OMEGA ⬡ jem_synthesis ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_synthesis ⬡ FINAL*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemma-4-31b-it | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
