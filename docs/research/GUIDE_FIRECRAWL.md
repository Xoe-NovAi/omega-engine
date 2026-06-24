# 🔱 Expert Guide: Firecrawl (Structured Extraction)
**Classification**: Sovereign Extraction Layer
**Role**: The Scalpel

## 🎯 Overview
Firecrawl transforms the unstructured web into LLM-ready data. It is not a search engine, but a **context API** that converts HTML into clean Markdown or structured JSON.

## 🛠️ Expert Usage Patterns

### 1. High-Fidelity JSON Extraction
Avoid "hallucinated" structures by using strict JSON schemas.
- **Schema Design**: Define `properties` precisely and use the `description` field as a hint for the extraction LLM.
- **Example**: `"price": { "type": "number", "description": "The monthly cost of the Pro plan in USD" }`.

### 2. The "Map-Filter-Scrape" Pipeline
Maximize credits and minimize latency by avoiding blind crawls.
1. **Map**: Use `/map` to get all URLs on a domain.
2. **Filter**: Use a local regex or LLM to select only relevant URLs (e.g., `/pricing`, `/docs`).
3. **Scrape**: Execute targeted `/scrape` calls on the filtered subset.

### 3. Handling Dynamic Content (SPAs)
When content is hidden behind JavaScript:
- **`waitFor`**: Set `waitFor: 5000` (ms) to allow React/Vue components to hydrate.
- **`/interact`**: Use a stateful session to click "Load More" buttons or dismiss cookie banners.

## 🔌 Sovereign Integration
To keep your data within the perimeter:
1. **Self-Host**: Deploy the Firecrawl API on local infrastructure.
2. **Local Extraction**: Route the HTML $\rightarrow$ JSON transformation to a local model (e.g., via LM Studio).
3. **Markdown Mirror**: Store all markdown outputs in a local vector store (Qdrant) to avoid redundant scrapes.

## ⚖️ Decision Matrix: When to use Firecrawl
| Use Case | Recommendation | Why? |
| :--- | :--- | :--- |
| **Data Crystallization** | ✅ Primary | Best for turning a page into a structured object. |
| **Site-Wide Audit** | ✅ Primary | `/crawl` and `/map` provide comprehensive coverage. |
| **Dynamic Interaction** | ✅ Primary | `/interact` handles clicks and forms. |
| **Broad Discovery** | ❌ Avoid | Too expensive and slow for initial searching. |
| **Privacy-First Discovery** | ❌ Avoid | Not a search engine; requires a URL to start. |
