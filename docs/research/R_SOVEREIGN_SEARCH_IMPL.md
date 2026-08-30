<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Sovereign Search Architecture: 5-Tier Protocol Implementation
# ⬡ OMEGA ⬡ GROKSTER ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_search_impl ⬡ R34-COMPLETE

**AP Token**: `AP-SOVEREIGN-SEARCH-IMPL-v1.0.0`
**Date**: 2026-07-21
**Status**: COMPLETE
**Job ID**: R34 (Sovereign Search Architecture Implementation)
**Augments**: R_SEARCH_TOOL_PROTOCOL_V1.md, GROKSTER_SEARCH_CATALOGUE_20260721.md
**Owner**: grokster
**Decision Gate**: Implement 5-tier search router with cost/recall/relevance optimization

---

## §0 Executive Summary

This document specifies the complete implementation of the Omega Engine's **5-Tier Sovereign Search Protocol** — a cost-aware, failure-resilient, multi-provider search routing system. It synthesizes the existing search catalogue (17 tools catalogued), the existing search crawling protocol, and the search tool protocol v1 into a single implementation-ready specification.

**Key Design Decisions**:
1. **5-tier fallback chain**: Local Cache → Built-in → Sovereign → Academic → Deep Extraction
2. **Cost-first routing**: Free tiers exhausted before paid tiers
3. **Independent index priority**: Brave > SearXNG > websearch for sovereignty
4. **Academic tier as sovereign**: Semantic Scholar + arXiv + OpenAlex = zero-cost academic backbone
5. **Graceful degradation**: Every tier has a fallback; no single point of failure

---

## §1 Architecture Overview

### 1.1 The 5-Tier Protocol

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
│  Cost: $0 | Latency: ~1-4s | Self-hosted                   │
│  Provider: SearXNG MCP server (port 8017)                   │
└─────────────────────────────────────────────────────────────┘
         │ needs independent index or precision
         ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 2.5: Independent Index (Brave) + Budget SERP (Serper) │
│  Cost: $0.30-5/1k | Latency: ~0.5-0.8s | API key required  │
│  Providers: Brave Search API, Serper.dev, xAI tools         │
└─────────────────────────────────────────────────────────────┘
         │ needs academic depth
         ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 3: Academic Graph (Semantic Scholar + arXiv + OpenAlex)│
│  Cost: $0 | Latency: ~0.3-2s | Optional API key             │
│  Providers: Semantic Scholar, arXiv, OpenAlex, GitHub        │
└─────────────────────────────────────────────────────────────┘
         │ needs deep extraction or full-page scrape
         ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 4: Deep Extraction (Firecrawl + Exa + Tavily)         │
│  Cost: Credits/API key | Latency: ~2-10s                    │
│  Providers: Firecrawl, Exa, Tavily, Perplexity Sonar        │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Query Classification Rules

| Query Pattern | Tier Start | Reason |
|--------------|-----------|--------|
| "what is X", "define Y" | T0 | Likely cached or simple lookup |
| "latest on X", "news about Y" | T1 | Freshness needed, built-in sufficient |
| "private search", "sovereign query" | T2 | Privacy requirement |
| "independent source", "verify X" | T2.5 | Need independent index |
| "research paper on X", "academic Y" | T3 | Academic sources needed |
| "full text of X", "deep dive Y" | T4 | Full extraction needed |
| "code example X", "implementation Y" | T3.5 | GitHub Search API |
| "real-time X", "X on Twitter" | T2.5 | xAI x_search (paid) |

---

## §2 Tier Implementations

### 2.1 Tier 0 — Local Cache

**Provider**: `.firecrawl/` directory (filesystem cache)
**Status**: ✅ Already in stack

**Implementation**:
```python
import os
import time
from pathlib import Path

class LocalCache:
    """T0: Local filesystem cache with TTL eviction."""
    
    def __init__(self, cache_dir: str = ".firecrawl/", ttl_days: int = 30):
        self.cache_dir = Path(cache_dir)
        self.ttl_seconds = ttl_days * 86400
    
    def get(self, url: str) -> str | None:
        """Check cache for URL. Returns cached content or None."""
        cache_file = self._url_to_path(url)
        if not cache_file.exists():
            return None
        if time.time() - cache_file.stat().st_mtime > self.ttl_seconds:
            cache_file.unlink()  # TTL expired
            return None
        return cache_file.read_text(encoding="utf-8")
    
    def put(self, url: str, content: str) -> None:
        """Store content in cache."""
        cache_file = self._url_to_path(url)
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(content, encoding="utf-8")
    
    def _url_to_path(self, url: str) -> Path:
        """Convert URL to filesystem path."""
        import hashlib
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
        return self.cache_dir / f"{url_hash}.md"
    
    def evict_expired(self) -> int:
        """Remove all expired entries. Returns count removed."""
        removed = 0
        for f in self.cache_dir.glob("*.md"):
            if time.time() - f.stat().st_mtime > self.ttl_seconds:
                f.unlink()
                removed += 1
        return removed
```

**TTL Policy**:
| Source | TTL | Reason |
|--------|-----|--------|
| T1 websearch results | 30 days | General web content |
| T2 SearXNG results | 14 days | Metasearch results |
| T3 academic results | 90 days | Papers change rarely |
| T4 deep extractions | 7 days | Full pages change frequently |

---

### 2.2 Tier 1 — Built-in Search

**Providers**: `websearch` + `webfetch` (OpenCode built-in)
**Status**: ✅ Already in stack

**Implementation**: Already wired. No additional code needed.

**Usage Pattern**:
```python
# Primary search
result = websearch(query="latest AI developments 2026", numResults=8)

# Deep extraction of specific URL
content = webfetch(url="https://example.com/article", format="markdown")
```

**Limitations** (documented):
- Opaque ranking algorithm
- No independent index
- No citation shaping
- No academic-specific search

**When to Skip**: Need independent verification, academic sources, or full-page extraction.

---

### 2.3 Tier 2 — Sovereign Metasearch (SearXNG)

**Provider**: SearXNG (self-hosted, port 8017)
**Status**: ✅ Already in stack (MCP server connected)

**Implementation**:
```python
import httpx

class SearXNGClient:
    """T2: Sovereign metasearch via self-hosted SearXNG."""
    
    def __init__(self, base_url: str = "http://localhost:8017"):
        self.base_url = base_url
    
    async def search(
        self,
        query: str,
        categories: str = "general",
        engines: str = "duckduckgo,google,brave,wikipedia",
        language: str = "auto",
        time_range: str = "",
        pageno: int = 1,
        limit: int = 10,
    ) -> dict:
        """Execute sovereign metasearch."""
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{self.base_url}/search",
                data={
                    "q": query,
                    "format": "json",
                    "categories": categories,
                    "engines": engines,
                    "language": language,
                    "time_range": time_range,
                    "pageno": pageno,
                    "safesearch": 0,
                },
            )
            return response.json()
    
    async def health_check(self) -> bool:
        """Check SearXNG health."""
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{self.base_url}/healthz")
            return response.status_code == 200
```

**Category Routing**:
| Query Type | Category | Engines |
|-----------|----------|---------|
| General web | `general` | duckduckgo,google,brave |
| Academic | `science` | arxiv,semantic_scholar,google_scholar |
| Code/IT | `it` | github,duckduckgo,google |
| News | `news` | google_news,bing_news,duckduckgo |
| Videos | `videos` | youtube,invidious,duckduckgo |

---

### 2.4 Tier 2.5 — Independent Index + Budget SERP

#### Brave Search API (P0 — Highest Priority)

**Provider**: Brave Search API
**Status**: 🟡 Recommended next integration
**Pricing**: $3-5/1k queries; 2,000 free/month
**Latency**: ~0.8s (fastest AI-native tier)

**Implementation**:
```python
import httpx

class BraveSearchClient:
    """T2.5: Independent index via Brave Search API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
    
    async def search(
        self,
        query: str,
        count: int = 10,
        offset: int = 0,
        country: str = "US",
        search_lang: str = "en",
        freshness: str = "pw",  # pw=past week, pm=past month, py=past year
    ) -> dict:
        """Execute Brave Search with LLM-optimized context."""
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(
                self.base_url,
                headers={
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip",
                    "X-Subscription-Token": self.api_key,
                },
                params={
                    "q": query,
                    "count": count,
                    "offset": offset,
                    "country": country,
                    "search_lang": search_lang,
                    "freshness": freshness,
                },
            )
            return response.json()
```

**MCP Integration** (3-line config):
```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@anthropic/brave-search"],
      "env": { "BRAVE_API_KEY": "${BRAVE_API_KEY}" }
    }
  }
}
```

#### Serper.dev (P1 — Budget Tier)

**Provider**: Serper.dev + Jina Reader
**Status**: 🟡 Candidate
**Pricing**: $0.30-1/1k queries; 2,500 free on signup
**Latency**: ~0.5s (fastest in class)

**Implementation**:
```python
class SerperClient:
    """T2.5: Budget SERP via Serper.dev + Jina Reader."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def search(self, query: str, num: int = 10) -> dict:
        """Execute Google SERP search."""
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": self.api_key},
                json={"q": query, "num": num},
            )
            return response.json()
    
    async def extract_url(self, url: str) -> str:
        """Extract full page content via Jina Reader (free)."""
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"https://r.jina.ai/{url}")
            return response.text
```

**Total Stack Cost**: ~$0.50/1k queries (Serper + Jina) — cheapest production stack.

---

### 2.5 Tier 3 — Academic Graph

#### Semantic Scholar (P0 — Academic Backbone)

**Provider**: Semantic Scholar Academic Graph API
**Status**: 🟡 Candidate (not yet integrated)
**Pricing**: $0 (100 req/sec with free API key; 1/sec without)
**Coverage**: 200M+ papers (arXiv, bioRxiv, PubMed, IEEE, ACM, Nature)

**Implementation**:
```python
class SemanticScholarClient:
    """T3: Academic paper search via Semantic Scholar."""
    
    def __init__(self, api_key: str | None = None):
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.headers = {}
        if api_key:
            self.headers["x-api-key"] = api_key
    
    async def search_papers(
        self,
        query: str,
        year: str = "",
        fields_of_study: str = "",
        limit: int = 10,
    ) -> list[dict]:
        """Search academic papers with TLDR summaries."""
        params = {
            "query": query,
            "limit": limit,
            "fields": "title,url,abstract,tldr,citationCount,publicationDate,authors",
        }
        if year:
            params["year"] = year
        if fields_of_study:
            params["fieldsOfStudy"] = fields_of_study
        
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(
                f"{self.base_url}/paper/search",
                headers=self.headers,
                params=params,
            )
            return response.json().get("data", [])
    
    async def get_citations(self, paper_id: str) -> list[dict]:
        """Get forward citations for a paper."""
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(
                f"{self.base_url}/paper/{paper_id}/citations",
                headers=self.headers,
                params={"fields": "title,url,citationCount"},
            )
            return response.json().get("data", [])
```

#### arXiv API (P1 — Preprint Search)

**Provider**: arXiv API
**Status**: 🟡 Candidate
**Pricing**: $0 (1 req/3 sec, no key needed)
**Coverage**: 2.2M+ preprints (physics, math, CS, biology)

**Implementation**:
```python
class ArxivClient:
    """T3: Preprint search via arXiv API."""
    
    BASE_URL = "http://export.arxiv.org/api/query"
    
    async def search(
        self,
        query: str,
        max_results: int = 10,
        sort_by: str = "submittedDate",
        sort_order: str = "descending",
    ) -> list[dict]:
        """Search arXiv preprints. Rate limit: 1 req/3 sec."""
        params = {
            "search_query": f"all:{query}",
            "max_results": max_results,
            "sortBy": sort_by,
            "sortOrder": sort_order,
        }
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(self.BASE_URL, params=params)
            # Parse XML response
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.text)
            entries = []
            for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
                entries.append({
                    "title": entry.find("{http://www.w3.org/2005/Atom}title").text,
                    "url": entry.find("{http://www.w3.org/2005/Atom}id").text,
                    "abstract": entry.find("{http://www.w3.org/2005/Atom}summary").text,
                    "published": entry.find("{http://www.w3.org/2005/Atom}published").text,
                })
            return entries
```

#### OpenAlex API (P2 — Broad Research Graph)

**Provider**: OpenAlex API
**Status**: 🟡 Candidate
**Pricing**: $0 (100k req/day without key)
**Coverage**: 250M+ works, 100M+ authors

**Implementation**:
```python
class OpenAlexClient:
    """T3: Open research graph via OpenAlex API."""
    
    BASE_URL = "https://api.openalex.org"
    
    async def search_works(
        self,
        query: str,
        limit: int = 10,
       mailto: str = "xoe.nova.ai@gmail.com",
    ) -> list[dict]:
        """Search research works across publisher boundaries."""
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(
                f"{self.BASE_URL}/works",
                params={
                    "search": query,
                    "per_page": limit,
                    "mailto": mailto,  # Priority access
                },
            )
            return response.json().get("results", [])
```

#### GitHub Search API (P2 — Code Search)

**Provider**: GitHub Search API
**Status**: 🟡 Candidate
**Pricing**: $0 (5k req/hr authenticated; 60/hr unauthenticated)

**Implementation**:
```python
class GitHubSearchClient:
    """T3.5: Code/repo search via GitHub API."""
    
    BASE_URL = "https://api.github.com/search"
    
    async def search_code(
        self,
        query: str,
        language: str = "",
        limit: int = 10,
    ) -> list[dict]:
        """Search code across open-source repos."""
        params = {"q": query, "per_page": limit}
        if language:
            params["q"] += f" language:{language}"
        
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(
                f"{self.BASE_URL}/code",
                params=params,
            )
            return response.json().get("items", [])
```

---

### 2.6 Tier 4 — Deep Extraction

#### Firecrawl (P1 — Full Scrape)

**Provider**: Firecrawl
**Status**: ✅ Already in stack (credits: 987 remaining)
**Pricing**: Credits-based

**Implementation** (already wired):
```python
# Already integrated via firecrawl_firecrawl_scrape/search/crawl tools
# Use for: full-page extraction, JS rendering, structured crawl
```

#### Exa (P3 — Neural Search)

**Provider**: Exa (sovereign_search)
**Status**: ✅ Already in stack
**Pricing**: ~$5/1k queries (~100 free)

**Implementation** (already wired):
```python
# Already integrated via omega-hub_sovereign_search tool
# Use for: high-precision seeds, semantic/technical queries
```

#### Tavily (P2 — Citation-Shaped RAG)

**Provider**: Tavily
**Status**: 🟡 Candidate
**Pricing**: $8/1k queries; 1,000 free/month

**Implementation**:
```python
class TavilyClient:
    """T4: Citation-shaped RAG via Tavily."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def search(
        self,
        query: str,
        search_depth: str = "advanced",
        include_raw_content: bool = True,
    ) -> dict:
        """One-call RAG: search + extraction + citations."""
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "query": query,
                    "search_depth": search_depth,
                    "include_raw_content": include_raw_content,
                    "api_key": self.api_key,
                },
            )
            return response.json()
```

---

## §3 Search Router — Intelligent Routing

### 3.1 Router Implementation

```python
from enum import Enum
from dataclasses import dataclass

class SearchTier(Enum):
    CACHE = 0
    BUILTIN = 1
    SOVEREIGN = 2
    INDEPENDENT = 2.5
    ACADEMIC = 3
    DEEP = 4

@dataclass
class SearchIntent:
    """Classified search intent."""
    query: str
    tier_start: SearchTier
    needs_freshness: bool
    needs_academic: bool
    needs_independent: bool
    needs_extraction: bool
    max_cost_per_query: float

class SearchRouter:
    """5-tier search router with cost/recall/relevance optimization."""
    
    def __init__(self, config: dict):
        self.cache = LocalCache(config.get("cache_dir", ".firecrawl/"))
        self.searxng = SearXNGClient(config.get("searxng_url", "http://localhost:8017"))
        self.brave = BraveSearchClient(config.get("brave_key", ""))
        self.serper = SerperClient(config.get("serper_key", ""))
        self.semantic = SemanticScholarClient(config.get("semantic_key"))
        self.arxiv = ArxivClient()
        self.openalex = OpenAlexClient()
        self.firecrawl = FirecrawlClient(config.get("firecrawl_key"))
    
    def classify_intent(self, query: str) -> SearchIntent:
        """Classify query intent to determine starting tier."""
        query_lower = query.lower()
        
        # Academic queries
        if any(kw in query_lower for kw in ["paper", "research", "study", "journal", "arxiv", "citation"]):
            return SearchIntent(
                query=query,
                tier_start=SearchTier.ACADEMIC,
                needs_freshness=False,
                needs_academic=True,
                needs_independent=False,
                needs_extraction=False,
                max_cost_per_query=0.0,
            )
        
        # Freshness queries
        if any(kw in query_lower for kw in ["latest", "news", "recent", "today", "2026", "breaking"]):
            return SearchIntent(
                query=query,
                tier_start=SearchTier.BUILTIN,
                needs_freshness=True,
                needs_academic=False,
                needs_independent=False,
                needs_extraction=False,
                max_cost_per_query=0.005,
            )
        
        # Code queries
        if any(kw in query_lower for kw in ["code", "implementation", "example", "github", "library"]):
            return SearchIntent(
                query=query,
                tier_start=SearchTier.ACADEMIC,
                needs_freshness=False,
                needs_academic=False,
                needs_independent=False,
                needs_extraction=False,
                max_cost_per_query=0.0,
            )
        
        # Verification queries
        if any(kw in query_lower for kw in ["verify", "independent", "confirm", "source", "original"]):
            return SearchIntent(
                query=query,
                tier_start=SearchTier.INDEPENDENT,
                needs_freshness=False,
                needs_academic=False,
                needs_independent=True,
                needs_extraction=False,
                max_cost_per_query=0.005,
            )
        
        # Deep extraction queries
        if any(kw in query_lower for kw in ["full text", "deep dive", "extract", "scrape", "crawl"]):
            return SearchIntent(
                query=query,
                tier_start=SearchTier.DEEP,
                needs_freshness=False,
                needs_academic=False,
                needs_independent=False,
                needs_extraction=True,
                max_cost_per_query=0.01,
            )
        
        # Default: start at cache, fallback to built-in
        return SearchIntent(
            query=query,
            tier_start=SearchTier.CACHE,
            needs_freshness=False,
            needs_academic=False,
            needs_independent=False,
            needs_extraction=False,
            max_cost_per_query=0.0,
        )
    
    async def search(self, query: str) -> dict:
        """Execute search with tier fallback."""
        intent = self.classify_intent(query)
        
        # T0: Check cache
        cached = self.cache.get(query)
        if cached:
            return {"tier": 0, "source": "cache", "content": cached, "cost": 0.0}
        
        # T1: Built-in search
        if intent.tier_start.value <= 1:
            try:
                result = await self._search_builtin(query)
                if result and not intent.needs_independent:
                    self.cache.put(query, result["content"])
                    return result
            except Exception:
                pass
        
        # T2: SearXNG
        try:
            result = await self.searxng.search(query)
            if result.get("results"):
                content = self._format_results(result["results"])
                self.cache.put(query, content)
                return {"tier": 2, "source": "searxng", "content": content, "cost": 0.0}
        except Exception:
            pass
        
        # T2.5: Independent index (Brave/Serper)
        if intent.tier_start.value <= 2.5:
            try:
                result = await self.brave.search(query)
                if result.get("web", {}).get("results"):
                    content = self._format_results(result["web"]["results"])
                    self.cache.put(query, content)
                    return {"tier": 2.5, "source": "brave", "content": content, "cost": 0.003}
            except Exception:
                pass
        
        # T3: Academic
        if intent.tier_start.value <= 3:
            try:
                papers = await self.semantic.search_papers(query, limit=5)
                if papers:
                    content = self._format_papers(papers)
                    self.cache.put(query, content)
                    return {"tier": 3, "source": "semantic_scholar", "content": content, "cost": 0.0}
            except Exception:
                pass
        
        # T4: Deep extraction
        if intent.tier_start.value <= 4:
            try:
                result = await self.firecrawl.search(query)
                if result:
                    content = self._format_results(result)
                    self.cache.put(query, content)
                    return {"tier": 4, "source": "firecrawl", "content": content, "cost": 0.01}
            except Exception:
                pass
        
        return {"tier": -1, "source": "none", "content": "No results found", "cost": 0.0}
```

### 3.2 Cost Optimization Rules

| Rule | Condition | Action |
|------|-----------|--------|
| **Free-First** | Always | Exhaust T0-T2 before touching T2.5+ |
| **Brave Priority** | Need independent index | Brave over Serper (sovereignty) |
| **Serper Budget** | High-volume, low-criticality | Serper + Jina ($0.50/1k) |
| **Academic Zero** | Research queries | Semantic Scholar + arXiv ($0) |
| **Cache Aggressive** | Any result | Cache at T0 with appropriate TTL |
| **xAI Inside** | Grok-powered workflow | Use xAI tools ($5/1k) only within Grok context |
| **Tavily RAG** | Need one-call extraction | Tavily ($8/1k) replaces 3-step pipeline |

### 3.3 Fallback Chain

```
websearch (T1) → SearXNG (T2) → Brave (T2.5) → Semantic Scholar (T3) → Firecrawl (T4)
     ↓                ↓              ↓                  ↓                    ↓
  webfetch        searxng         Serper            arXiv              Exa contents
                                  + Jina           OpenAlex
```

---

## §4 Integration with Omega Engine

### 4.1 MCP Server Integration

```python
# mcp_servers/omega_search/router.py

from omega.search import SearchRouter

router = SearchRouter(config={
    "cache_dir": ".firecrawl/",
    "searxng_url": "http://localhost:8017",
    "brave_key": os.environ.get("BRAVE_API_KEY", ""),
    "serper_key": os.environ.get("SERPER_API_KEY", ""),
    "semantic_key": os.environ.get("SEMANTIC_SCHOLAR_KEY"),
    "firecrawl_key": os.environ.get("FIRECRAWL_API_KEY"),
})

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "sovereign_search":
        result = await router.search(arguments["query"])
        return [TextContent(type="text", text=result["content"])]
```

### 4.2 Agent Usage Pattern

```python
# In any agent's search workflow:
from omega.search import SearchRouter

router = SearchRouter(config)

# Automatic tier routing
result = await router.search("latest developments in local LLM inference 2026")

# Manual tier override
result = await router.search("quantum computing papers", tier_start=SearchTier.ACADEMIC)

# Cost-aware search
result = await router.search("news about AI regulation", max_cost=0.001)
```

---

## §5 Testing & Validation

### 5.1 Test Matrix

| Test | Tier | Expected | Pass Criteria |
|------|------|----------|---------------|
| Cache hit | T0 | Cached content | Latency <10ms |
| Cache miss → websearch | T1 | Search results | 3+ results |
| SearXNG privacy search | T2 | Metasearch results | 5+ results |
| Brave independent index | T2.5 | Brave results | 3+ results |
| Semantic Scholar papers | T3 | Academic papers | 3+ papers with TLDR |
| arXiv preprints | T3 | Preprint results | 3+ preprints |
| Firecrawl deep extraction | T4 | Full page content | Content >1000 chars |
| Fallback chain | T1→T2→T2.5 | Progressive fallback | Final result non-empty |
| Cost tracking | All | Cost per query | Total cost logged |

### 5.2 Validation Commands

```bash
# Test each tier independently
source .venv/bin/activate && python -c "
import asyncio
from omega.search import SearchRouter

async def test():
    router = SearchRouter({})
    
    # T0: Cache test
    result = await router.search('test query')
    print(f'T0: {result[\"source\"]} - cost: {result[\"cost\"]}')
    
    # T2: SearXNG test
    result = await router.search('privacy search')
    print(f'T2: {result[\"source\"]} - cost: {result[\"cost\"]}')
    
    # T3: Academic test
    result = await router.search('research paper on transformers')
    print(f'T3: {result[\"source\"]} - cost: {result[\"cost\"]}')

asyncio.run(test())
"
```

---

## §6 Monitoring & Observability

### 6.1 Metrics to Track

| Metric | Source | Alert Threshold |
|--------|--------|-----------------|
| **Cost per query** | Router logs | >$0.01/query average |
| **Cache hit rate** | LocalCache stats | <50% (TTL too short) |
| **Tier distribution** | Router logs | >80% hitting T4 (routing issue) |
| **Provider latency** | HTTP client | >5s average |
| **Provider errors** | HTTP client | >5% error rate |
| **Credit balance** | Firecrawl/Exa APIs | <100 credits remaining |

### 6.2 Observability Integration

```python
# Log search routing decisions
logger.info(
    "search_completed",
    query=query[:50],
    tier=result["tier"],
    source=result["source"],
    cost=result["cost"],
    latency_ms=elapsed_ms,
)
```

---

## §7 Deployment & Operations

### 7.1 Prerequisites

| Component | Status | Action Required |
|-----------|--------|-----------------|
| `.firecrawl/` cache | ✅ Exists | Enable TTL eviction |
| SearXNG | ✅ Running | No action |
| Brave API key | 🟡 Not configured | Get free key (2k/mo) |
| Semantic Scholar key | 🟡 Not configured | Get free key (optional) |
| Firecrawl credits | ✅ 987 remaining | Monitor balance |

### 7.2 Implementation Phases

| Phase | Duration | Scope | Dependencies |
|-------|----------|-------|--------------|
| **Phase 1** | 2 days | T0-T2 (cache, websearch, SearXNG) | None |
| **Phase 2** | 1 day | T2.5 (Brave integration) | Brave API key |
| **Phase 3** | 2 days | T3 (Semantic Scholar + arXiv) | Semantic Scholar key (optional) |
| **Phase 4** | 1 day | Router + cost tracking | Phases 1-3 |
| **Phase 5** | 1 day | Testing + monitoring | Phase 4 |

**Total**: ~7 days for complete implementation

---

## §8 Future Enhancements

| Enhancement | Priority | Effort | Impact |
|-------------|----------|--------|--------|
| **Brave MCP integration** | P0 | 1h | Independent index in 3 config lines |
| **Semantic Scholar MCP** | P1 | 4h | Academic backbone wired |
| **Perplexity Sonar** | P2 | 2h | Pre-synthesized answers |
| **Search result reranking** | P2 | 1d | Better relevance scoring |
| **Multi-query fusion** | P3 | 2d | Parallel tier search + RRF |
| **Search analytics dashboard** | P3 | 1d | Cost/tier/latency visualization |

---

*⬡ OMEGA ⬡ GROKSTER ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_search_impl ⬡ R34-COMPLETE*
*Decision Gate PASSED: 5-tier search router with cost/recall/relevance optimization specified*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
