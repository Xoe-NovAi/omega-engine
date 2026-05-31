---
name: "sovereign-search"
description: "Intelligent search orchestration across Exa, Tavily, and Serper.dev to optimize for depth and verification."
---

# Sovereign Search Fabric Skill

Use this skill when you need to perform high-quality web research. To ensure absolute resilience against API key expiration or MCP transport failures, the search fabric uses a **strict fallback hierarchy** prioritizing built-in, local-first, and highly stable tools.

## Search Provider Matrix (Hardened)

| Priority | Provider / Tool | Strength | Use Case | Strategy |
|---|---|---|---|---|
| **1 (Primary)** | **`websearch`** | Built-in, Zero-Config | Fast, general-purpose web search, recency, and broad discovery | **Default fallback** for all queries. Always try this first if specialized MCPs fail. |
| **2 (Primary)** | **`firecrawl`** | Full-Page Scrape/Crawl | Deep content extraction, sitemaps, and reading full pages | Use `firecrawl_scrape` or `firecrawl_search` for comprehensive page-level data. |
| **3 (Secondary)** | **Exa (MCP)** | Neural/Semantic Search | Technical papers, deep research, "similar to this" queries | **Currently Restricted (401)**. Use `websearch` $\rightarrow$ `firecrawl` as the primary path. |
| **4 (Secondary)** | **Tavily/Serper (MCP)** | AI-Optimized Retrieval | High-precision facts and curated summaries | **Disabled**. Do not attempt. |

## Workflow

### Step 1: Intent Analysis
Analyze the user's query to determine the optimal search focus:
- **General/Recency/Facts**: "What is the latest version of X?", "How do I fix Y?" $\rightarrow$ Use **`websearch`** immediately.
- **Deep Scrape/Crawl**: "Get the full content of X", "Crawl the docs of Y" $\rightarrow$ Use **`firecrawl`** immediately.
- **Academic/Technical**: "Find research papers on X" $\rightarrow$ Attempt **Exa**, fall back to **`websearch`** if 401 occurs.

### Step 2: Mandatory Execution Gate (No Lazy Responses)
- **The Mandate**: The agent **MUST** perform at least one active tool call (`websearch` or `firecrawl`) for any query requiring factual, technical, or recent information.
- **Anti-Laziness Rule**: Relying solely on internal parametric weights for research queries is a **violation of the Temple Grade standard**. If a tool fails, try another. Do not give up.

### Step 3: Fallback & Recovery
If a specialized MCP tool (like Exa or Tavily) returns a `401 Unauthorized`, `Connection Error`, or `Timeout`:
1.  **Do not crash or report failure.**
2.  Immediately fall back to the built-in **`websearch`** tool.
3.  Use **`firecrawl_scrape`** or **`webfetch`** to read the top URLs returned by `websearch`.

### Step 4: Synthesis & Output
Present the findings as a **Sovereign Search Report**:
- **Primary Finding**: Concise, direct answer.
- **Supporting Evidence**: Bullet points with citations (Tool $\rightarrow$ URL).
- **Fallback Log**: Note if any primary tools failed and how the fallback was handled.
