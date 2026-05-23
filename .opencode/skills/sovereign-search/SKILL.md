---
name: "sovereign-search"
description: "Intelligent search orchestration across Exa, Tavily, and Serper.dev to optimize for depth and verification."
---

# Sovereign Search Fabric Skill

Use this skill when you need to perform high-quality web research that requires more than a single search engine's perspective.

## Search Provider Matrix

| Provider | Strength | Use Case | Strategy |
|---|---|---|---|
| **Exa** | Neural/Semantic Search | Deep research, finding patterns, academic/technical papers, "similar to this" queries | Use for `depth="deep"` or `focus="research"` |
| **Tavily** | AI-Optimized Retrieval | Fact-checking, curated summaries, high-precision data points | Use for `focus="facts"` or `focus="verified"` |
| **Serper.dev** | Fast Google-based Retrieval | Broad web search, recency, general-purpose queries | Use for `general` search or `recency` checks |

## Workflow

### Step 1: Intent Analysis
Analyze the user's query to determine the optimal search focus:
- **Research Focus**: "Find all papers on X", "What are the architectural patterns of Y?" $\rightarrow$ **Exa**
- **Verification Focus**: "Is X true?", "What is the official spec for Y?" $\rightarrow$ **Tavily**
- **General/Recency Focus**: "What's the latest news on X?", broad discovery queries $\rightarrow$ **Serper.dev**
- **Mixed**: Ambiguous or multi-faceted queries $\rightarrow$ **Fallback Chain (Serper $\rightarrow$ Exa $\rightarrow$ Tavily)**

### Step 2: Targeted Execution
Invoke the selected MCP tool:
- `exa_web_search_exa(...)` for semantic/deep research
- `tavily_tavily_search(...)` for AI-optimized fact retrieval
- `serper.dev(...)` for Google-powered general/recency queries (use `websearch` tool with Serper endpoint)

If the first provider returns no high-relevance results, automatically pivot to the next provider in the matrix.

### Step 3: Synthesis & Aggregation
Merge results from multiple providers:
1. **Deduplication**: Remove identical URLs.
2. **Cross-Referencing**: Identify where different providers agree or contradict.
3. **Relevance Scoring**: Rank results by snippet quality and source authority.

### Step 4: Output Generation
Present the findings as a **Sovereign Search Report**:
- **Primary Finding**: Concise answer to the query.
- **Supporting Evidence**: Bullet points with citations (Provider $\rightarrow$ URL).
- **Contradictions/Nuance**: Any conflicting information found across providers.
- **Next Steps**: Suggested follow-up queries for deeper dives.

## Example Usage

Query: "Latest developments in local LLM quantization for Ryzen 7 5700U"
1. **Analysis**: Mixed (Recency + Research + Verification).
2. **Execution**: 
   - Call `serper` for latest news/recency on Zen 2 quantization (General).
   - Call `exa` for technical papers/deep dives (Research).
   - Call `tavily` for fact-checking and verification of claims.
3. **Synthesis**: Combine recency from Serper, research from Exa, and verified facts from Tavily.
4. **Report**: "Latest developments show X (Serper), while technical analysis reveals Y (Exa), and verified benchmarks confirm Z (Tavily)."
