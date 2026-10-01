<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Search Dossier: Firecrawl (Structured Extraction)
**Version**: 1.0.0
**Classification**: Sovereign Extraction Layer
**Role in SSP V2**: The Scalpel (High-Fidelity Data Crystallization)

---

## ⚙️ Technical Architecture

Firecrawl is designed to turn the unstructured web into LLM-ready data. Unlike a search engine, it is a **context API** focused on the transformation of HTML into Markdown or structured JSON.

### Core Modalities
1. **`/scrape` (Single Page)**:
   - Fetches a URL and converts it to clean Markdown.
   - Supports **JSON Extraction** via LLM-guided schema mapping.
   - Handles JS-rendered pages via headless browser orchestration.
2. **`/crawl` (Site-Wide)**:
   - Recursively discovers and scrapes pages.
   - Implements depth limits and path filtering (e.g., `/blog/*`).
   - Manages concurrency to avoid being blocked by target servers.
3. **`/map` (Discovery)**:
   - Generates a complete list of indexed URLs on a domain.
   - Essential for "targeted crawling" to avoid wasted credits.
4. **`/interact` (Live Session)**:
   - Provides a stateful browser session.
   - Allows agents to click buttons, fill forms, and navigate dynamic flows.

---

## 🛠️ Expert Patterns for Structured Extraction

### 1. Schema-Driven JSON Design
To get high-fidelity data, avoid natural language prompts alone. Use **strict JSON schemas**.
- **Pattern**: Define the `properties` of the object precisely.
- **Guidance**: Use `description` fields within the schema to act as "hints" for the extraction LLM (e.g., `"price": { "type": "number", "description": "The monthly cost of the Pro plan in USD" }`).

### 2. Handling JS-Heavy SPAs
Dynamic content often fails in simple scrapes.
- **`waitFor` Strategy**: Use the `waitFor` parameter (e.g., `5000ms`) to ensure React/Vue components have hydrated before extraction.
- **Interaction Flow**: Use `/interact` to trigger a "Load More" button or handle a cookie banner that blocks the main content.

### 3. The "Map-Filter-Scrape" Pipeline
To optimize cost and latency:
1. **Map**: Get all URLs on `example.com`.
2. **Filter**: Use a local regex or LLM to select only URLs matching `/pricing` or `/docs`.
3. **Scrape**: Execute targeted scrapes on the filtered subset.

---

## ⚖️ Strengths & Weaknesses

| Strength | Description | Weakness | Description |
| :--- | :--- | :--- | :--- |
| **Structure** | Turns HTML into perfect JSON. | **Cost** | Credit-based pricing can be expensive. |
| **Automation** | Headless browser handles JS. | **Latency** | Crawling takes minutes, not seconds. |
| **LLM-Native** | Markdown is optimal for RAG. | **Dependency** | Relying on a cloud API for core data. |
| **Interaction** | Can handle logins and clicks. | **Fragility** | DOM changes can break complex interactions. |

---

## 🛡️ Sovereign Usage

To maximize sovereignty and minimize reliance on centralized providers:
1. **Self-Host the API**: Deploy Firecrawl on local infrastructure to keep scraped content within the perimeter.
2. **Local LLM Extraction**: Configure the extraction pipeline to use a local model (e.g., via LM Studio) to perform the HTML $\rightarrow$ JSON transformation, ensuring the content never leaves the host.
3. **Local Markdown Cache**: Store all `markdown` outputs in a local vector store (Qdrant) to avoid re-scraping the same pages.
4. **Sovereign Map**: Use `/map` to create a local index of target sites, treating the web as a remote database that is mirrored locally.
