<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Sovereign Search Intelligence: Firecrawl Technical Dossier
**Status**: VERIFIED
**Sovereignty Tier**: Tier 1 (High - Open Core / Self-Hostable)
**Protocol Alignment**: Deep Capture / Structured Extraction

## 1. Architecture & Core Mechanics
Firecrawl is a **web-to-LLM data pipeline**. Unlike a search engine, it is designed to turn the messy, dynamic web into clean, structured data that AI agents can consume without token waste.

### Core Workflow:
`URL/Query` $\to$ `Headless Browser (Puppeteer/Playwright)` $\to$ `JS Rendering` $\to$ `Smart Wait/Content Detection` $\to$ `Markdown/JSON Conversion` $\to$ `LLM-powered Extraction (Optional)` $\to$ `Sovereign Data`.

### Key Mechanical Features:
- **JS Rendering**: Handles SPAs (Single Page Applications) and dynamically loaded content by executing JavaScript in a headless browser.
- **Crawl & Map**:
    - `Map`: Discovers all URLs on a domain, creating a site-map for targeted scraping.
    - `Crawl`: Recursively follows links with configurable depth and path filters.
- **Interact**: Allows agents to perform actions (click, type, scroll) to reach data behind buttons or login walls.
- **Structured Extraction**: Uses LLMs to map raw page content to a provided JSON schema in a single pass.

## 2. Sovereignty Analysis
Firecrawl provides a strong path to sovereignty, though the "hosted" experience is significantly more polished than the "self-hosted" one.

- **Self-Hosting**: The core is open-source. Can be deployed via Docker.
- **Umbilical Cord Risk**: Moderate. While the core is open, the hosted "Fire-engine" manages complex proxy rotations and rendering clusters that are difficult to replicate locally at scale.
- **Data Privacy**: When self-hosted, data stays within the user's infrastructure.
- **Local-First Alignment**: High. It allows the Omega Engine to perform "Deep Capture" without relying on a third-party API for every page.

## 3. API Specification & Integration Patterns
Firecrawl uses a REST API designed for asynchronous, high-volume extraction.

### Primary Endpoints:
- `/scrape`: `URL` $\to$ `Markdown/JSON`. Best for single pages.
- `/crawl`: `URL` $\to$ `List of Pages`. Best for whole sites.
- `/map`: `URL` $\to$ `URL List`. Best for discovery.
- `/search`: `Query` $\to$ `Content`. Combined search and scrape.
- `/interact`: `scrapeId` $\to$ `Action`. Browser-level interaction.

### Key Request Patterns:
- **Schema Extraction**: Passing a `jsonOptions.schema` to `/scrape` triggers an LLM-based extraction loop.
- **Async Polling**: Crawls return a `jobId`, requiring polling of the status endpoint until completion.

## 4. Capability Mapping
- **Deep Extraction**: Absolute. The primary use case.
- **JS Support**: High. Handles almost all modern web frameworks.
- **Structure**: Superior. Converts HTML to LLM-optimized Markdown.
- **Interaction**: High. Can operate pages like a human.

## 5. Performance Benchmarks
- **Latency**: P95 ~3.4s for search/scrape. Crawling is asynchronous and can take minutes/hours depending on site size.
- **Accuracy**: High for structure; dependent on the LLM used for structured extraction.
- **Cost**: Credit-based (Hosted). Compute-based (Self-hosted).

## 6. Integration Gaps for Omega Engine
- **Proxy Management**: Self-hosted Firecrawl requires a separate proxy provider (e.g., Bright Data, Oxylabs) to avoid being blocked by Cloudflare/Akamai.
- **Resource Intensive**: Running headless browsers (Puppeteer) at scale requires significant RAM/CPU (unlike the lightweight SearXNG).
- **Token Cost**: While it reduces input tokens via Markdown, structured extraction still requires LLM calls.
