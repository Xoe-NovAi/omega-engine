# 🔱 Omega Engine — Web Research MCP Audit
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ R-27

**AP Token**: `AP-RESEARCH-R27-v1.0.0`
**Status**: ✅ COMPLETE
**Last Updated**: 2026-05-14

---

## 🎯 Executive Summary

This audit evaluates the most powerful web research MCP (Model Context Protocol) servers available for the OpenCode CLI and the Omega Engine. The goal is to identify a toolset that enables a "Sovereign Master Researcher" workflow: one that combines semantic discovery, high-density content retrieval, and synthesized reasoning.

**Key Finding**: No single tool is perfect for all research phases. The optimal strategy is a **Hybrid Research Stack** combining **Exa** for semantic discovery and high-density retrieval, **Brave Search** for broad web coverage and local data, and **Perplexity** for rapid synthesis of complex queries.

---

## 🔍 Provider Analysis

### 1. Exa (formerly Metaphor)
Exa is a search engine designed specifically for LLMs, utilizing a neural index to find links based on meaning rather than keywords.

- **MCP Implementation**: 
  - **Remote**: `https://mcp.exa.ai/mcp` (Zero-config)
  - **Local**: `npx -y exa-mcp-server`
- **Core Tools**:
  - `web_search_exa`: Semantic search for topics.
  - `web_fetch_exa`: Converts URLs to clean markdown.
  - `web_search_advanced_exa`: Category filters, domain restrictions, and subpage crawling.
- **Unique Capabilities**:
  - **Highlights**: Returns only the most relevant tokens from a page, reducing context window usage by ~10x.
  - **Structured Outputs**: Can return search results directly as JSON according to a schema.
  - **Category Search**: Dedicated indexes for people, companies, and research papers.
- **Verdict**: **Best for Deep Discovery & Token Efficiency.**

### 2. Brave Search
Brave provides a robust, independent search index with a strong focus on privacy and AI-readiness.

- **MCP Implementation**: 
  - **Local**: `npx -y @brave/brave-search-mcp-server`
- **Core Tools**:
  - `brave_web_search`: General web search.
  - `brave_llm_context`: Retrieves pre-extracted content optimized for RAG.
  - `brave_summarizer`: AI-powered summaries of search results.
  - Specialized tools for Local, Video, Image, News, and Place search.
- **Unique Capabilities**:
  - **Broadest Scope**: Excellent for local business data and diverse media types (video/image).
  - **LLM Context**: Specifically tuned snippets for grounding LLM responses.
- **Verdict**: **Best for General Purpose Web Coverage & Local Data.**

### 3. Tavily
Tavily is an AI-native search engine optimized for agents and RAG pipelines, focusing on returning clean, factual content.

- **MCP Implementation**: 
  - **Local**: `tavily-ai/tavily-mcp` (GitHub)
- **Core Tools**:
  - Real-time search, content extraction, and mapping.
- **Unique Capabilities**:
  - **RAG Optimization**: Specifically designed to remove "web noise" (headers, footers, ads) before the LLM sees the content.
  - **Agentic Focus**: Built to be called in loops by autonomous agents.
- **Verdict**: **Best for Pure RAG Pipelines & Factual Extraction.**

### 4. Perplexity
Perplexity is a "search-augmented" AI that synthesizes answers from multiple sources in real-time.

- **MCP Implementation**: 
  - **Local**: `perplexityai/modelcontextprotocol` (GitHub)
- **Core Tools**:
  - Search-augmented reasoning and research tools.
- **Unique Capabilities**:
  - **Synthesized Answers**: Instead of just links, it returns a reasoned answer with citations.
  - **Rapid Iteration**: Great for "getting the gist" of a complex topic before diving into raw sources.
- **Verdict**: **Best for Rapid Synthesis & Initial Reconnaissance.**

---

## 📊 Comparison Matrix

| Feature | Exa | Brave Search | Tavily | Perplexity |
| :--- | :--- | :--- | :--- | :--- |
| **Search Logic** | Semantic (Neural) | Keyword + Semantic | AI-Optimized | Synthesized AI |
| **Output Format** | Highlights / JSON | Rich Snippets / LLM Context | Clean Markdown | Synthesized Text |
| **Token Efficiency** | 🌟 Elite (Highlights) | High (LLM Context) | High (Cleaned) | Medium (Full Ans) |
| **Local/Media Data** | Low | 🌟 Elite | Medium | Medium |
| **Integration** | Remote / Local | Local | Local | Local |
| **Free Tier** | Generous | Good | Good | API-based |
| **Primary Strength** | Discovery | Coverage | RAG Purity | Synthesis |

---

## 🔱 Recommendation: The "Sovereign Master Researcher" Workflow

For the Omega Engine, I recommend a **Tiered Research Pipeline** rather than a single tool.

### The Pipeline
1. **Phase 1: Reconnaissance (Perplexity)**
   - Use Perplexity to generate a high-level synthesis of the query.
   - *Goal*: Identify key entities, dates, and technical terms.
2. **Phase 2: Semantic Discovery (Exa)**
   - Use Exa's semantic search to find "hidden" high-quality sources and research papers.
   - Use `highlights` to scan 20+ sources without blowing the context window.
   - *Goal*: Find the "Gold" sources.
3. **Phase 3: Broad Validation (Brave Search)**
   - Use Brave to verify facts across the general web and find local/current news.
   - *Goal*: Ensure no blind spots.
4. **Phase 4: Deep Extraction (Tavily / Exa Fetch)**
   - Use Tavily or Exa's `web_fetch` to extract the full, cleaned content of the top 3-5 sources for final analysis.
   - *Goal*: High-fidelity grounding for the final report.

### Recommended MCP Configuration
```json
{
  "mcpServers": {
    "exa": {
      "url": "https://mcp.exa.ai/mcp"
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@brave/brave-search-mcp-server"],
      "env": { "BRAVE_API_KEY": "..." }
    },
    "perplexity": {
      "command": "npx",
      "args": ["-y", "@perplexityai/mcp-server"],
      "env": { "PERPLEXITY_API_KEY": "..." }
    }
  }
}
```

---

## 🛠️ Implementation Notes for Builder Agents

- **Context Management**: When using Exa, always prefer `contents={"highlights": True}` to maximize the number of sources analyzed per turn.
- **Error Handling**: Implement a fallback chain: `Exa (Semantic) → Brave (General) → Tavily (RAG)`.
- **Rate Limiting**: Exa's remote MCP is highly stable; for local servers (Brave/Perplexity), ensure they are wrapped in the `ResourceGuard` to prevent OOM on the Ryzen 5700U.

---

## 🚨 Integration Diagnostics & v1.15.0 Analysis (May 15, 2026)

**Issue**: User reported that no MCP servers (Exa, Brave, Tavily) appear in the OpenCode `/status` output after upgrading to v1.15.0.

**Root Cause Analysis**:
1. **Orphaned Configs**: The `opencode.json` entries for `exa`, `brave-search`, and `tavily` are not consumed by the codebase. The discovery pipeline (`src/omega/library/discovery.py`) performs **direct HTTP calls** to the provider REST APIs using keys from `.env`, bypassing the MCP layer entirely.
2. **CLI Status Limitation**: The `oracle_cli.mcp_status` command only monitors core services listed in `Orchestrator.mcp_ports` (`omega-hub`, `omega-research`, `omega-stats`). Since the search providers are not registered as core services, they are never listed.
3. **Package Name Drift**: Original config referenced `@anthropic/brave-search-mcp-server` (404). The correct package is `@brave/brave-search-mcp-server` or `brave-search-mcp`. Similarly, `tavily-mcp-server` $\rightarrow$ `tavily-mcp`.

**Recommendations**:
- **Short-term**: Prune obsolete MCP entries from `opencode.json` to avoid confusion. Update `docs/README.md` to clarify that search providers are called via HTTP.
- **Long-term (Unified MCP Architecture)**:
  - Implement lightweight MCP wrappers in `src/omega/mcp/` that forward calls to the HTTP API.
  - Update `DiscoveryOrchestrator` to use the MCP client.
  - Add these services to `Orchestrator.mcp_ports` so they appear in `/status`.

**Current State**: The search pipeline is fully functional via HTTP, despite the MCP "disconnection" reported in the CLI.
