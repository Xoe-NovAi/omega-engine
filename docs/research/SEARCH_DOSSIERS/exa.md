# 🔱 Sovereign Search Intelligence: Exa Technical Dossier
**Status**: VERIFIED
**Sovereignty Tier**: Tier 3 (Low - API Only / Cloud-Locked)
**Protocol Alignment**: Neural Retrieval / Semantic Intent

## 1. Architecture & Core Mechanics
Exa is a **neural search engine**. Unlike traditional engines (keyword-based) or metasearch (aggregators), Exa uses a custom-built index of the web where pages are represented as high-dimensional embeddings.

### Core Workflow:
`Semantic Query` $\to$ `Embedding Model` $\to$ `Neural Index Lookup` $\to$ `Sovereign Ranking` $\to$ `Synthesized Output/Highlights` $\to$ `User`.

### Key Mechanical Features:
- **Neural Search**: Searches for "meaning" and "intent" rather than keywords. It understands the *relationship* between the query and the destination page.
- **Link-Based Filtering**: Uses the graph structure of the web to prioritize high-quality, authoritative sources.
- **Highlights**: A specialized model that extracts only the most relevant excerpts from a page, reducing token waste by up to 90%.
- **Synthesis**: Can output results directly into a JSON schema via a synthesis layer, bypassing the need for a separate scrape/extract step.

## 2. Sovereignty Analysis
Exa provides the highest "Intelligence per Query" but the lowest "Sovereignty per Query."

- **Self-Hosting**: None. Exa is a proprietary cloud service.
- **Umbilical Cord Risk**: High. Total dependency on Exa's API and index. If the API goes down or pricing changes, the capability is lost.
- **Data Privacy**: Offers ZDR (Zero Data Retention) for enterprise users, ensuring queries aren't used for training.
- **Local-First Alignment**: Low. It is a purely external dependency.

## 3. API Specification & Integration Patterns
Exa's API is optimized for AI agents, focusing on "Grounding" and "Neural Retrieval."

### Primary Endpoints:
- `/search`: The main entry point. Supports neural search and synthesis.
- `/get-contents`: Fetches full text/markdown for specific IDs.

### Key Parameters:
| Parameter | Type | Description |
|-----------|------|------------------------------------------------------|
| `query` | String | The semantic query. |
| `type` | Enum | `instant` (low latency), `fast`, `auto`, `deep`, `deep-reasoning`. |
| `contents` | Object | Controls `text`, `highlights`, and `summary` extraction. |
| `outputSchema` | Object | A JSON schema for synthesized output. |
| `includeDomains` | Array | Restricts results to a specific whitelist. |

### Integration Pattern for Omega Engine:
Exa should be used as the **Neural Precision Layer (Tier 3)**.
`Complex Intent` $\to$ `Exa Neural Search` $\to$ `Synthesized Structured Data` $\to$ `Grounding`.

## 4. Capability Mapping
- **Semantic Intent**: Absolute. The best in class for "find me a page *like* this."
- **Latency**: Ultra-Low. "Instant" mode returns results in <180ms.
- **Synthesis**: High. Built-in structured output generation.
- **Sovereignty**: None.

## 5. Performance Benchmarks
- **Latency**: <180ms (Instant), 2-5s (Deep).
- **Accuracy**: Leading on retrieval benchmarks (FRAMES, Tip-of-Tongue).
- **Cost**: Per-request pricing (Neural search is more expensive than standard).

## 6. Integration Gaps for Omega Engine
- **Sovereignty Violation**: Being cloud-only, it violates the "Local-First" mandate if used as a primary search tool.
- **Black Box**: The indexing and ranking logic are proprietary and cannot be audited or tuned locally.
- **Price Scaling**: As the number of agents increases, the cost can scale linearly, unlike a self-hosted SearXNG.
