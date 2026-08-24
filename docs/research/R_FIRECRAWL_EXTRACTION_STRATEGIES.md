# 🔱 Omega Engine — R-02 Firecrawl Extraction Strategies
# ⬡ OMEGA ⬡ researcher ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_research ⬡ R02

**AP Token**: `AP-RESEARCH-R02-v1.0.0`
**Author**: researcher (Sovereign Master Researcher)
**Date**: 2026-06-09
**Status**: READY

---

## Summary
This document analyzes Firecrawl's structured data extraction capabilities, contrasting the `/scrape (json)` and `/extract` endpoints with the autonomous `FIRE-1` agent. It provides a framework for designing high-fidelity JSON schemas and prompts to ensure consistent, machine-readable output for the Omega Engine.

## Findings

### 1. Extraction Modalities

| Method | Endpoint | Input | Best Use Case | Cost |
| :--- | :--- | :--- | :--- | :--- |
| **Schema-Based** | `/scrape` (json) | URL + JSON Schema | Known structure, single page | 1 + 4 credits |
| **Prompt-Based** | `/scrape` (json) | URL + Prompt | Exploratory, flexible structure | 1 + 4 credits |
| **Multi-URL** | `/extract` | URLs[] + Schema/Prompt | Consistent data across multiple pages | Per page |
| **Autonomous** | `/agent` (FIRE-1) | Prompt + URLs[] | Complex navigation, multi-page synthesis | High (Agentic) |

### 2. The `/extract` Endpoint
- **Capabilities**: Simplifies collecting structured data from multiple URLs or entire domains (using `/*` wildcards).
- **Web Search Integration**: The `enableWebSearch: true` parameter allows the extractor to follow links outside the provided domain to enrich the result (e.g., finding reviews on third-party sites for a product page).
- **URL-less Extraction**: Supports extracting data based on a prompt alone (Alpha), where Firecrawl finds the relevant URLs autonomously.

### 3. The FIRE-1 Agent
- **Nature**: An autonomous AI agent that controls a browser to navigate complex structures.
- **Advantage**: Unlike standard extraction, FIRE-1 can perform multi-step navigation (e.g., "Go to the forum, find the latest thread on X, and extract all comments").
- **Configuration**: Supports model selection (`spark-1-mini` for cost, `spark-1-pro` for accuracy) and `strictConstrainToURLs` to prevent agent drift.

### 4. Prompt Engineering for Extraction

To maximize fidelity, prompts should follow these principles:
- **Specificity**: Instead of "Extract pricing," use "Extract the monthly price for the 'Pro' plan, including the currency symbol."
- **Constraint-Based**: "Return only the value; do not include explanatory text."
- **Structural Guidance**: When using prompts without schemas, specify the desired keys (e.g., "Return a JSON object with keys 'price' and 'features'").

### 5. Schema Design Best Practices
- **Strong Typing**: Use explicit types (`string`, `number`, `boolean`, `array`).
- **Required Fields**: Always define a `required` array to prevent the LLM from omitting critical data.
- **Nested Objects**: Use nested objects for related data (e.g., a `dimensions` object containing `width`, `height`, `depth`).

## Recommendations

1. **Prefer Schemas over Prompts**: For production pipelines, always use a JSON Schema to ensure downstream parser stability.
2. **Use FIRE-1 for "Deep" Extraction**: If the data is hidden behind interactions or spread across multiple non-linear pages, escalate from `/extract` to `/agent`.
3. **Enable Web Search for Competitive Intel**: When performing market research, set `enableWebSearch: true` to capture external validation and reviews.

## Sources
- [Firecrawl Extract Docs](https://docs.firecrawl.dev/features/extract) — accessed 2026-06-09
- [Firecrawl Agent Docs](https://docs.firecrawl.dev/features/agent) — accessed 2026-06-09
- File: `.firecrawl/feature-extract.md`

## Implementation Note
_For: P6 Cognition / ModelGateway_
The `ModelGateway` should implement a `structured_extract()` method that accepts a Pydantic model. This model should be converted to a JSON schema and passed to the `/scrape` or `/extract` endpoint. For complex tasks, the gateway should route the request to the `FIRE-1` agent via the `/agent` endpoint.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemma-4-31b-it | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
