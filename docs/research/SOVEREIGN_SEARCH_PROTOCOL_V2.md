# 🔱 Sovereign Search Protocol V2 (SSP)
**Version**: 2.0.0
**Classification**: Engine-Level Search Standard
**Status**: ACTIVE

## 🎯 Vision
The Sovereign Search Protocol V2 (SSP) is the Omega Engine's standard for transforming the chaotic, tracked, and unstructured web into a structured, sovereign, and local knowledge base. It moves the agent from "searching for answers" to "orchestrating evidence."

## 🚀 The Sovereign Path (Routing Logic)
The SSP V2 implements a tiered pipeline that optimizes for **Privacy $\rightarrow$ Precision $\rightarrow$ Structure**.

**The Pipeline**:
`SearXNG (Discovery) $\rightarrow$ Exa (Neural Refinement) $\rightarrow$ Firecrawl (Sovereign Extraction) $\rightarrow$ Local Vector Store`

### Tier 1: The Wide-Angle Lens (SearXNG)
- **Goal**: Broad, private discovery.
- **Usage**: Keyword-exact matching, broad consensus gathering, and privacy-preserving initial probes.
- **Output**: A list of potential URLs and snippets.

### Tier 2: The Compass (Exa)
- **Goal**: Semantic navigation and high-precision seed generation.
- **Usage**: Finding "meaning" and "intent," discovering niche high-value sources, and refining the URL list via semantic similarity.
- **Output**: A refined set of high-precision seed URLs.

### Tier 3: The Scalpel (Firecrawl)
- **Goal**: High-fidelity data crystallization.
- **Usage**: Converting the refined URLs into clean Markdown or structured JSON using strict schemas.
- **Output**: LLM-ready structured data.

---

## 🛠️ Agent Decision Matrix
Agents must use the following matrix to determine the tool for the current query intent.

| Query Intent | Primary Tool | Secondary Tool | Logic |
| :--- | :--- | :--- | :--- |
| **Factual Lookup** (e.g., "What is the API limit for X?") | **SearXNG** | **Firecrawl** | Exact keyword match $\rightarrow$ Targeted scrape. |
| **Semantic Discovery** (e.g., "Find research arguing against X") | **Exa** | **SearXNG** | Intent-based search $\rightarrow$ Broad verification. |
| **Structured Extraction** (e.g., "Get the pricing tiers for X") | **Firecrawl** | **SearXNG** | Direct URL scrape $\rightarrow$ Map $\rightarrow$ Scrape. |
| **Niche/Obscure Research** (e.g., "Unconventional Zen 2 cooling") | **Exa** | **Firecrawl** | Neural discovery $\rightarrow$ Deep extraction. |
| **Broad Consensus** (e.g., "What are the top 5 LLMs for code?") | **SearXNG** | **Exa** | Aggregated view $\rightarrow$ Semantic refinement. |
| **Dynamic Interaction** (e.g., "Log in and get the user profile") | **Firecrawl** | N/A | `/interact` stateful session. |

---

## 🛡️ The Sovereign Search Standard
To maintain sovereignty, all search operations must adhere to these mandates:

1. **Local-First Discovery**: Always attempt a local SearXNG probe before escalating to cloud-based neural search.
2. **No Black-Box Reliance**: Never use a search engine's "AI Summary." Fetch the raw content and synthesize it using a local LLM.
3. **Sovereign Mirroring**: High-value clusters found via Exa/SearXNG must be scraped via Firecrawl and mirrored into the local vector store (Qdrant) to prevent future reliance on the provider.
4. **Privacy Shielding**: All discovery must be proxied. No agent shall query a search engine directly with the host's IP.
5. **Structure over Snippets**: A search is not complete until the result is converted from a "snippet" (SearXNG/Exa) into "structured data" (Firecrawl).

## 📈 Performance Metrics
- **Discovery Latency**: $\text{SearXNG} \approx 1\text{s}$
- **Neural Precision**: $\text{Exa} \approx \text{High}$
- **Extraction Fidelity**: $\text{Firecrawl} \approx \text{Perfect (Schema-driven)}$
