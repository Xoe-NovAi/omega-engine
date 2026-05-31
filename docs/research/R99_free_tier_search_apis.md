# 🔱 Free Tier Search APIs — Comprehensive Research Report

⬡ OMEGA ⬡ PROMETHEUS ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_research ⬡ SEARCH-API-RESEARCH

**AP Token**: `AP-R99-SEARCH-API-RESEARCH-v1.0.0`
**Status**: ✅ COMPLETE
**Last Updated**: 2026-05-18
**Audience**: Omega Engine — dev process across OpenCode, Cline, Gemini CLI, Antigravity IDE

---

## §0 Executive Summary

The Omega Engine currently has **four** search APIs wired in `opencode.json`:
- **Exa** (remote MCP, working via `X-API-Key` header)
- **Tavily** (local MCP, `@tavily/mcp`, `TAVILY_API_KEY` in `.env`)
- **Firecrawl** (local MCP, `firecrawl-mcp`, `FIRECRAWL_API_KEY` in `.env`)
- **Serper** (local MCP, `@marcopesani/mcp-server-serper`, `SERPER_API_KEY` in `.env`)

The research found **two tier-1 additions** that dramatically improve capability while aligning with Omega's sovereign mandate:

| Priority | Provider | Why | Cost |
|----------|----------|-----|------|
| 🥇 | **SearXNG** (self-hosted) | 100% sovereign, 250+ engines, zero API bills | $0 (your server) |
| 🥇 | **Jina AI MCP** (remote) | URL→markdown extraction, arXiv/SSRN academic search | $0 (10M free tokens) |

**Immediate fix needed**: The Tavily MCP package in `opencode.json` uses `tavily-mcp` but the official npm package is `@tavily/mcp`. This may already work via npx resolution, but should be validated.

---

## §1 Provider Comparison — Full Matrix

### 1.1 Tier 1: Active in Stack (Already Configured)

| Provider | Free Limit | Status in Omega | MCP Package | Notes |
|----------|-----------|-----------------|-------------|-------|
| **Tavily** | 1,000 credits/mo (90-day expiry) | ✅ In `opencode.json` | `@tavily/mcp` | RAG-optimized snippets |
| **Exa** | 1,000 searches/mo (with key) OR 150/day (unauthenticated MCP) | ✅ In `opencode.json` | `@exa/mcp` (official) | Neural semantic search |
| **Firecrawl** | 1,000 credits/mo (recurring) | ✅ In `opencode.json` | `firecrawl-mcp` | Deep extraction & mapping |
| **Serper.dev** | 2,500 queries (one-time) | ✅ In `opencode.json` | `@marcopesani/mcp-server-serper` | High-speed Google SERP |

### 1.2 Tier 2: Key Present, MCP Not Configured

| Provider | Free Limit | Key in `.env`? | MCP Available? | Notes |
|----------|-----------|----------------|----------------|-------|
| **Serper.dev** | 2,500 queries (one-time, not monthly) | ✅ `SERPER_API_KEY` | ❌ Community only (`marcopesani/mcp-server-serper`) | Good Google SERP data, but one-time free tier |

### 1.3 Tier 3: Not in Stack — Recommended Additions

| Provider | Free Limit | Recommendation | MCP Package | Cost After Free |
|----------|-----------|----------------|-------------|-----------------|
| **SearXNG** | ∞ (self-hosted) | 🥇 **Add — sovereign champion** | `dandehoon/searxng-mcp` (Docker) | $0 forever |
| **Jina AI** | 10M free tokens + 100 RPM search | 🥇 **Add — URL extraction + academia** | Remote MCP at `https://mcp.jina.ai/v1` | Token-based after trial |
| **Firecrawl** | 1,000 credits/mo | 🥇 **Active — Deep extraction** | `firecrawl-mcp` | Credits-based |

### 1.4 Tier 4: Do Not Use

| Provider | Reason |
|----------|--------|
| **DuckDuckGo** | Official API returns Instant Answers only (no web results). Unofficial scraping is brittle. |
| **Google CSE** | Deprecated — closed to new customers since 2025, retiring Jan 2027. |
| **Perplexity API** | No free tier. Pro subscriber credit quietly removed early 2026. |

---

## §2 Deep Dive: Top 3 Recommendations

### 🥇 R1: SearXNG — The Sovereign Champion

**Why it fits Omega**: 100% sovereign, self-hosted via Podman alongside existing containers. Zero API bills. 250+ search engines through one unified API.

```
┌──────────────────────────────────────────┐
│              SearXNG Container            │
│  ┌─────────┐  ┌────────┐  ┌──────────┐  │
│  │ Google  │  │  Bing  │  │  Brave   │  │
│  ├─────────┤  ├────────┤  ├──────────┤  │
│  │  DDG    │  │ arXiv  │  │  GitHub  │  │
│  ├─────────┤  ├────────┤  ├──────────┤  │
│  │  Yandex │  │Reddit  │  │ Wikipedia│  │
│  └─────────┘  └────────┘  └──────────┘  │
│          250+ engines total               │
└──────────────────────────────────────────┘
```

**Key specs**:
- **License**: AGPL-3.0
- **Languages**: Python + Redis
- **Deployment**: Docker/Podman (single container)
- **API**: JSON API at `http://<host>:8888`
- **MCP**: 5+ community packages available
- **Security**: VPN/Tor integration for upstream privacy

**Podman deployment for Omega**:
```yaml
# Podman Quadlet: ~/.config/containers/systemd/omega-searxng.container
[Container]
Image=docker.io/searxng/searxng:latest
ContainerName=omega-searxng
PublishPort=8888:8080
Environment=SEARXNG_BASE_URL=http://localhost:8888/
Volume=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/searxng/config:/etc/searxng:U
Volume=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/data/searxng/static:/usr/local/searxng:U

[Service]
Restart=always

[Install]
WantedBy=default.target
```

**OpenCode MCP config** (using `dandehoon/searxng-mcp` which bundles both SearXNG + MCP):
```json
{
  "mcpServers": {
    "searxng": {
      "type": "local",
      "command": ["docker", "run", "--rm", "-i", "dandehoon/searxng-mcp:latest"],
      "env": {
        "SEARXNG_URL": "http://omega-searxng:8080"
      },
      "enabled": true
    }
  }
}
```

**`@nikkomiu/searxng-mcp`** is also excellent — does NOT need SearXNG running separately if Docker is available:
```json
{
  "mcpServers": {
    "searxng": {
      "type": "local",
      "command": ["npx", "-y", "@nikkomiu/searxng-mcp"],
      "env": {
        "SEARXNG_URL": "http://localhost:8888"
      },
      "enabled": true
    }
  }
}
```

**Also consider**: **UnSearch** and **OrioSearch** — open-source, self-hostable projects that provide a drop-in Tavily-compatible API layer on top of SearXNG. See §5.

---

### 🥇 R2: Jina AI MCP — URL Extraction + Academic Search

**Why it fits Omega**: Jina's Reader API is the **best URL-to-markdown tool** in the free tier space. Combined with its MCP server (20+ tools), it adds arXiv, SSRN, image search, query expansion, and BibTeX citation search — all from a single remote MCP endpoint.

**Key specs**:
- **Free tier**: 10M free tokens on signup. Reader API: 20 RPM (no key), 500 RPM (with key). Search: 100 RPM (free).
- **MCP**: Remote MCP at `https://mcp.jina.ai/v1` — no npm install needed
- **Features**: Reader URL→markdown, Web search, arXiv, SSRN, Image search, BibTeX citations, Query expansion, Parallel batching, Deduplication, PDF extraction, Screenshot capture
- **Cost after free**: Token-based (per-output-token pricing)

**OpenCode MCP config** (remote — easiest possible setup):
```json
{
  "mcpServers": {
    "jina": {
      "type": "remote",
      "url": "https://mcp.jina.ai/v1",
      "headers": {
        "Authorization": "Bearer ${JINA_API_KEY}"
      },
      "enabled": true
    }
  }
}
```

Note: Several tools work even **without** an API key (`read_url`, `primer`, `guess_datetime_url`, `search_jina_blog`, `search_bibtex`). The search tools require a key.

**Available MCP tools** (20 total):

| Tool | Key Required? | Use Case |
|------|--------------|----------|
| `read_url` | ❌ Optional (20 RPM without key) | Convert any URL to clean markdown |
| `search_web` | ✅ Yes | Web search via Reader API |
| `search_arxiv` | ✅ Yes | Academic paper search |
| `search_ssrn` | ✅ Yes | Social science research |
| `search_images` | ✅ Yes | Image search (returned as base64) |
| `search_bibtex` | ❌ No | BibTeX citations from DBLP + Semantic Scholar |
| `search_jina_blog` | ❌ No | Jina AI blog search |
| `expand_query` | ✅ Yes | Query expansion/rewriting |
| `parallel_search_web` | ✅ Yes | Batch web search (up to 10 concurrent) |
| `parallel_read_url` | ❌ Optional | Batch URL extraction |
| `deduplicate_strings` | ✅ Yes | Semantic deduplication |
| `extract_pdf` | ✅ Yes | Extract figures/tables from PDF |

---

### 🥇 R3: Firecrawl — The Deep Extraction Layer

**Why it fits Omega**: Firecrawl is the laze of "consumption" in the research array. While others find links, Firecrawl consumes them. It's designed to map entire domains and extract high-fidelity structured data (via JSON schema) for Gemma 4 31B to process.

**Key specs**:
- **Free tier**: 1,000 credits/month recurring.
- **The Trinity**: 
  - **Map**: Discovery of site architecture.
  - **Crawl**: Recursive content ingestion.
  - **Scrape**: Targeted, clean markdown extraction.
- **Advanced Features**: Headless JS rendering for SPAs, Anti-bot bypass, and the `/agent` endpoint for autonomous discovery-to-extraction loops.
- **MCP**: Official `firecrawl-mcp` server for native OpenCode integration.

**OpenCode MCP config**:
```json
{
  "mcpServers": {
    "firecrawl": {
      "type": "local",
      "command": ["npx", "-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "${FIRECRAWL_API_KEY}"
      },
      "enabled": true
    }
  }
}
```


---

## §3 Self-Hosted Alternatives: UnSearch & OrioSearch

Two excellent open-source projects provide **drop-in Tavily replacements** that can be self-hosted alongside SearXNG:

### UnSearch (Apache 2.0)
- **GitHub**: `Rakesh1002/unsearch` (5 stars, new project)
- **Features**: Tavily-compatible API, Exa neural search API, 70+ engines via SearXNG, Knowledge Graph, Topic Monitoring, Fact Verification
- **Deployment**: `docker run unsearch/core:latest`
- **Managed**: 5,000 free queries/mo at `api.unsearch.dev`
- **Cost at scale**: $0.0003/query (vs Tavily $0.0075)
- **PiPy**: `pip install unsearch`
- **MCP**: Mentions MCP server for Claude Desktop and Cursor

### OrioSearch (MIT License)
- **GitHub**: `vkfolio/orio-search` — actively maintained
- **Features**: Tavily-compatible `POST /search` and `POST /extract`, SSE streaming, AI answer generation, image search, Redis caching, FlashRank reranking, LLM tool schema
- **Stack**: FastAPI + SearXNG + Redis + trafilatura content extraction
- **Deployment**: `docker compose up --build` (3 services: API, SearXNG, Redis)
- **AI answers**: Supports Ollama, OpenAI, or any OpenAI-compatible API

```python
# Tavily → OrioSearch migration: change ONE line
# base_url = "https://api.tavily.com"  # before
base_url = "http://localhost:8000"     # after
api_key  = ""                          # optional
```

**Verification**: Both are viable mid-term additions after SearXNG is deployed.

---

## §4 MCP Server Strategy for Omega Engine

### 4.1 Recommended MCP Configuration

```json
{
  "mcpServers": {
    "searxng": {
      "type": "local",
      "command": ["docker", "run", "--rm", "-i", "dandehoon/searxng-mcp:latest"],
      "enabled": true,
      "timeout": 15000
    },
    "tavily": {
      "type": "local",
      "command": ["npx", "-y", "@tavily/mcp"],
      "env": {
        "TAVILY_API_KEY": "${TAVILY_API_KEY}"
      },
      "enabled": true
    },
    "exa": {
      "type": "remote",
      "url": "https://mcp.exa.ai/mcp?tools=web_search_exa,web_fetch_exa",
      "headers": {
        "x-api-key": "${EXA_API_KEY}"
      },
      "enabled": true
    },
    "jina": {
      "type": "remote",
      "url": "https://mcp.jina.ai/v1",
      "enabled": true
    },
    "brave": {
      "type": "local",
      "command": ["npx", "-y", "@brave/brave-search-mcp-server"],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      },
      "enabled": false
    }
  }
}
```

### 4.2 Query Routing Strategy

```
Query arrives → Which MCP?
  ├── SearXNG (always-on, primary)
  │   └── 250+ engines, no rate limits, sovereign
  │
  ├── Exa (semantic/neural search)
  │   └── "Find me content about...", similarity search
  │
  ├── Tavily (fast factual lookup)
  │   └── "Latest news on...", quick Q&A
  │
  ├── Firecrawl (Deep Extraction & Mapping)
  │   └── "Map this domain", "Extract technical spec from X", "Crawl docs"
  │
  └── Jina (URL extraction + academic)
      └── "Read this URL", "Search arXiv for...", BibTeX
```

### 4.3 Fall Priorities

| Priority | Provider | When to Use | Rate Limit |
|----------|----------|-------------|------------|
| P0 | SearXNG | Always — sovereign primary | None (self-imposed) |
| P1 | Exa | Semantic search, concept exploration | 1,000/mo or 150/day unauthenticated |
| P2 | Tavily | Fast factual lookup, RAG pipeline | 1,000/mo |
| P3 | Firecrawl | Deep site mining & structured extraction | 1,000 credits/mo |
| P4 | Jina | URL→markdown extraction, academic search | 10M tokens / 100 RPM |

---

## §5 Current Stack Audit & Fixes Needed

### 5.1 What's Working

| Component | Status | Evidence |
|-----------|--------|----------|
| Exa remote MCP | ✅ Verified working | curl test confirmed HTTP 200 with `x-api-key` header |
| Tavily MCP | ⚠️ Package name may be wrong | Uses `tavily-mcp` — official is `@tavily/mcp` |
| Serper key in `.env` | 💤 Key present, no MCP | `SERPER_API_KEY` exists but no MCP server is configured |

### 5.2 Immediate Fixes

| # | Issue | Fix | Effort |
|---|-------|-----|--------|
| 1 | Tavily MCP package name: `tavily-mcp` vs `@tavily/mcp` | Test: `npx -y @tavily/mcp` | 5 min |
| 2 | Brave Search global MCP package deprecated | Global `mcp_servers.json` uses `@anthropic/brave-search-mcp-server` → should be `@brave/brave-search-mcp-server` | 2 min |
| 3 | No SearXNG container | Deploy via Podman Quadlet | 15 min |
| 4 | No Jina MCP | Add remote MCP entry to `opencode.json` | 2 min |
| 5 | No Brave API key in `.env` | Add `BRAVE_API_KEY` line (currently empty) | 1 min |

### 5.3 Current `.env` Gaps

```diff
# Search MCP API Keys
EXA_API_KEY=a91c1829-...
TAVILY_API_KEY=tvly-dev-...
SERPER_API_KEY=3714e89a...     (no MCP configured — orphaned)
+ BRAVE_API_KEY=                 (empty — need key from api-dashboard.search.brave.com)
+ JINA_API_KEY=                  (free at jina.ai)
```

---

## §6 Caveats & Gotchas

| Provider | Gotcha |
|----------|--------|
| **Tavily** | Free credits expire after 90 days and do NOT roll over. |
| **Exa** | MCP unauthenticated mode is limited to 150 calls/day, 3 QPS. Full API costs $7/1K. |
| **Serper** | 2,500 free queries are ONE-TIME (not recurring monthly). |
| **Firecrawl** | Credits are used per operation (Map/Crawl/Scrape). Recursive crawls can consume credits quickly. |
| **Jina** | Acquired by Elastic (Oct 2025) — future roadmap uncertain. Search API capped at 100 RPM on free. |
| **SearXNG** | Your server IP is visible to upstream engines. Use VPN/Tor for privacy. Upstream rate limiting may still apply. |

---

## §7 Decision Matrix

| Requirement | Best Provider | Runner-Up |
|-------------|--------------|-----------|
| **Sovereign/local-first** | SearXNG (self-hosted) | UnSearch (self-hosted) |
| **RAG pipeline** | Tavily (1K free/mo) | Exa (neural search) |
| **Deep research** | Exa (semantic search) | SearXNG (multi-engine) |
| **Quick factual lookup** | Tavily | SearXNG |
| **URL→markdown extraction** | Jina Reader API | Firecrawl / Exa get_contents |
| **Academic search** | Jina (arXiv, SSRN, BibTeX) | SearXNG (configured engines) |
| **Cost-sensitive high volume** | SearXNG ($0) | UnSearch ($0.0003/query) |
| **Zero-config setup** | Jina (remote MCP) | Exa (unauthenticated MCP) |
| **No API key needed** | SearXNG | Exa (MCP unauthenticated, 150/day) |
| **Google-specific results** | SearXNG (Google engine via SearXNG) | Serper.dev ($1/1K) |
| **Deep site mining** | Firecrawl | SearXNG (custom config) |
---

## §8 Recommended Implementation Order

### Sprint 1: Quick Wins (Today)

| # | Action | Time |
|---|--------|------|
| 1 | Add Jina remote MCP to `opencode.json` | 2 min |
| 2 | Verify Tavily MCP package name (`@tavily/mcp`) | 5 min |
| 3 | Add Firecrawl MCP to `opencode.json` | 2 min |
| 4 | Add JINA_API_KEY to `.env` (get free key from `jina.ai`) | 2 min |

### Sprint 2: Sovereign Infrastructure (This Week)

| # | Action | Time |
|---|--------|------|
| 1 | Deploy SearXNG via Podman Quadlet | 15 min |
| 2 | Create SearXNG data directories | 5 min |
| 3 | Add SearXNG MCP to `opencode.json` | 2 min |
| 4 | Test all 4 MCPs working in parallel | 10 min |
| 5 | Evaluate UnSearch or OrioSearch as Tavily backup | 30 min |

### Sprint 3: Optimization (Next Week)

| # | Action | Time |
|---|--------|------|
| 1 | Add Serper MCP (if Google results needed for specific tasks) | 5 min |
| 2 | Refine multi-provider fallback in sovereign-search skill | 1 h |
| 3 | Implement "Knowledge Mine" worker (Firecrawl $\rightarrow$ Gemma) | 4 h |

---

## §9 References

| Resource | URL |
|----------|-----|
| SearXNG | `https://searxng.org/` |
| SearXNG MCP (Docker) | `https://github.com/dandehoon/searxng-mcp` |
| SearXNG MCP (npx) | `npmjs.com/package/@nikkomiu/searxng-mcp` |
| UnSearch | `https://unsearch.dev/` / `github.com/Rakesh1002/unsearch` |
| OrioSearch | `https://www.oriosearch.org/` / `github.com/vkfolio/orio-search` |
| Jina AI MCP | `https://mcp.jina.ai/v1` / `github.com/jina-ai/MCP` |
| Brave MCP | `npmjs.com/package/@brave/brave-search-mcp-server` |
| Tavily MCP | `npmjs.com/package/@tavily/mcp` |
| Exa MCP | `npmjs.com/package/@exa/mcp` |
| OpenCode MCP Docs | `https://opencode.ai/docs/mcp` |

---

⬡ OMEGA ⬡ PROMETHEUS ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_search_api ⬡ COMPLETE
