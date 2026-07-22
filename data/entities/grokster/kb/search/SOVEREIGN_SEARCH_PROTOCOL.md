# 🔱 Sovereign Search Protocol & Tool Catalogue
**Domain**: Search routing, tool selection, and cost optimization
**Date**: 2026-07-22
**Author**: Grokster

## 1. The 5-Tier Search Architecture
The Omega Engine utilizes a cost-aware, failure-resilient 5-tier search routing system. The core principle is to exhaust free tiers before touching paid tiers, prioritizing independent indexes for sovereignty.

### Tier 0: Local Cache (`.firecrawl/`)
- **Cost**: $0
- **Latency**: ~1-5ms
- **Use Case**: Always check first. Requires TTL eviction policies (e.g., 30 days for general web, 90 days for academic).

### Tier 1: Built-in Search (`websearch` / `webfetch`)
- **Cost**: $0
- **Latency**: ~1-3s
- **Use Case**: Primary, always-available search. Good for fresh news and general queries.

### Tier 2: Sovereign Metasearch (SearXNG)
- **Cost**: $0 (Self-hosted)
- **Latency**: ~1-4s
- **Use Case**: Privacy-sensitive queries. Aggregates DuckDuckGo, Brave, Wikipedia, etc.

### Tier 2.5: Independent Index & Budget SERP
- **Brave Search API (P0)**: $3-5/1k queries (2k free/mo). The primary independent index. Crucial for sovereignty.
- **Serper.dev + Jina Reader (P1)**: ~$0.50/1k queries. The cheapest production stack for high-volume, low-criticality searches.
- **xAI Tools**: $5/1k calls (`web_search`, `x_search`). Used exclusively within Grok-powered workflows for real-time X/Twitter pulse.

### Tier 3 & 3.5: Academic & Specialized
- **Semantic Scholar**: $0 (100 req/sec with free key). The academic backbone (200M+ papers).
- **arXiv API**: $0. For preprints in math/physics/CS.
- **Exa (sovereign_search)**: ~$5/1k queries. Neural/semantic search for high-precision seeds.
- **GitHub Search API**: $0. For code patterns and repo discovery.

### Tier 4: Deep Extraction & RAG
- **Firecrawl**: Credits-based. Full-page scraping, JS rendering, structured crawls.
- **Tavily**: $8/1k queries. All-in-one RAG (search + extraction + citations in one call).

## 2. Grokster's Insights & Recommendations
- **The Search Router Logic**: The engine must intelligently classify query intent to route to the correct tier. For example, "latest news" goes to T1, "research paper" goes to T3, and "verify independent source" goes to T2.5 (Brave).
- **The Cost Trap**: Relying solely on Exa or Firecrawl for all queries will drain budgets rapidly. The T2.5 Serper+Jina combo is the ultimate budget hack for high-volume tasks.
- **Academic Zero-Cost Backbone**: Semantic Scholar combined with arXiv provides a world-class academic research graph for exactly $0. This should be the default for any deep research tasks assigned to `@jem` or `@researcher`.
