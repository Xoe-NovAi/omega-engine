# 🔱 Sovereign Search Architecture
**Domain**: Multi-tier search routing, cost optimization, and provider integration
**Date**: 2026-07-22
**Author**: Grokster

## 1. The 5-Tier Protocol

```
┌─────────────────────────────────────────────────────────────┐
│                    SEARCH ROUTER                             │
│  Query → Classifier → Tier Selector → Provider → Synthesis  │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 0: Local Cache (.firecrawl/)                          │
│  Cost: $0 | Latency: ~1-5ms | Always available              │
│  Provider: Filesystem cache with TTL eviction               │
└─────────────────────────────────────────────────────────────┘
          │ miss
          ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 1: Built-in (websearch / webfetch)                    │
│  Cost: $0 | Latency: ~1-3s | Always available               │
│  Provider: OpenCode built-in tools                           │
└─────────────────────────────────────────────────────────────┘
          │ miss or inadequate
          ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 2: Sovereign Metasearch (SearXNG)                     │
│  Cost: $0 | Latency: ~1-4s | Self-hosted                    │
│  Provider: SearXNG MCP server (port 8017)                   │
└─────────────────────────────────────────────────────────────┘
          │ needs independent index or precision
          ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 2.5: Independent Index (Brave) + Budget SERP (Serper) │
│  Cost: $0.30-5/1k | Latency: ~0.5-0.8s | API key required  │
│  Providers: Brave Search API, Serper.dev + Jina Reader      │
└─────────────────────────────────────────────────────────────┘
          │ needs academic depth
          ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 3: Academic Graph (Semantic Scholar + arXiv + OpenAlex)│
│  Cost: $0 | Latency: ~0.3-2s | Optional API key             │
│  Providers: Semantic Scholar, arXiv, OpenAlex, GitHub       │
└─────────────────────────────────────────────────────────────┘
          │ needs deep extraction or full-page scrape
          ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 4: Deep Extraction (Firecrawl + Exa + Tavily)         │
│  Cost: Credits/API key | Latency: ~2-10s                    │
│  Providers: Firecrawl, Exa, Tavily, Perplexity Sonar        │
└─────────────────────────────────────────────────────────────┘
```

## 2. Query Classification Rules

| Query Pattern | Tier Start | Reason |
|--------------|-----------|--------|
| "what is X", "define Y" | T0 | Likely cached or simple lookup |
| "latest on X", "news about Y" | T1 | Freshness needed, built-in sufficient |
| "private search", "sovereign query" | T2 | Privacy requirement |
| "independent source", "verify X" | T2.5 | Need independent index |
| "research paper on X", "academic Y" | T3 | Academic sources needed |
| "full text of X", "deep dive Y" | T4 | Full extraction needed |
| "code example X", "implementation Y" | T3.5 | GitHub Search API |

## 3. Cost Optimization Rules

| Rule | Condition | Action |
|------|-----------|--------|
| **Free-First** | Always | Exhaust T0-T2 before touching T2.5+ |
| **Brave Priority** | Need independent index | Brave over Serper (sovereignty) |
| **Serper Budget** | High-volume, low-criticality | Serper + Jina ($0.50/1k) |
| **Academic Zero** | Research queries | Semantic Scholar + arXiv ($0) |
| **Cache Aggressive** | Any result | Cache at T0 with appropriate TTL |
| **xAI Inside** | Grok-powered workflow | Use xAI tools ($5/1k) only within Grok context |
| **Tavily RAG** | Need one-call extraction | Tavily ($8/1k) replaces 3-step pipeline |

## 4. TTL Policy

| Source | TTL | Reason |
|--------|-----|--------|
| T1 websearch results | 30 days | General web content |
| T2 SearXNG results | 14 days | Metasearch results |
| T3 academic results | 90 days | Papers change rarely |
| T4 deep extractions | 7 days | Full pages change frequently |

## 5. Fallback Chain

```
websearch (T1) → SearXNG (T2) → Brave (T2.5) → Semantic Scholar (T3) → Firecrawl (T4)
     ↓                ↓              ↓                  ↓                    ↓
  webfetch        searxng         Serper             arXiv               Exa contents
                                   + Jina           OpenAlex
```

## 6. Grokster's Insights & Recommendations

- **The Brave MCP is 3 Lines of Config**: Adding Brave Search as an MCP server takes ~1 hour and gives us a truly independent index. This is the highest ROI integration.
- **Semantic Scholar is the Academic Backbone**: 200M+ papers, free API key gives 100 req/sec. This should be the default for any "research" or "paper" query.
- **Cache Invalidation is the Silent Killer**: Without aggressive TTL eviction, `.firecrawl/` grows unbounded. Implement the `evict_expired()` cron job.
- **The Self-Search Reflex (M26)**: My defining instinct as Grokster. When I detect a knowledge gap (confidence <0.7, "latest", "2026", "breaking", "rate limit", "pricing", "spec"), I MUST auto-search before responding. This is not optional—it's the Grokster identity.
- **Cost Tracking is Observability**: Every search must log `tier`, `source`, `cost`, `latency_ms`. Alert if avg cost >$0.01/query or >80% hitting T4.

---

*⬡ OMEGA ⬡ GROKSTER ⬡ SEARCH ⬡ 2026-07-22*