# 🔱 Omega Engine — Sovereign Search & Crawling Protocol
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_research ⬡ SEARCH-PROTOCOL

**AP Token**: `AP-SEARCH-CRAWL-PROTOCOL-v1.0.0`
**Status**: ACTIVE
**Scope**: All agents performing web research / content extraction for the Omega Engine

---

## §0 Architecture Overview

```
                     ╔══════════════════════╗
                     ║  Sovereign Search    ║
                     ║       Fabric         ║
                     ╚══════════════════════╝
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  SearXNG     │    │  Cloud Fleet │    │  Extraction  │
│  Zero-cost   │    │  Quota-mgmt  │    │  Deep Read   │
│  port 8017   │    │  Fallback    │    │  Tiered      │
└──────────────┘    └──────────────┘    └──────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Local search │    │ Exa / Tavily │    │ Jina Reader  │
│ Wikipedia    │    │ Serper / Jina│    │ Firecrawl    │
│ ArXiv        │    │ Semantic     │    │ Exa contents │
└──────────────┘    └──────────────┘    └──────────────┘
```

### The Two Search Layers

| Layer | Provider | Cost | Always Available | Best For |
|-------|----------|------|-----------------|----------|
| **Sovereign** | SearXNG (self-hosted) | Zero | ✅ (when up) | General search, Wikipedia, ArXiv, news |
| **Cloud** | Exa, Tavily, Serper, Jina | API credits | ✅ | Semantic search, content extraction, academic |

---

## §1 Provider Reference

### 1.1 SearXNG (Sovereign Layer)

| Attribute | Value |
|-----------|-------|
| **URL** | `http://localhost:8017` |
| **API Format** | Form-encoded POST or GET with `?format=json` |
| **Auth** | None (local only, port 8017) |
| **JSON Search** | `POST /search` with `Content-Type: application/x-www-form-urlencoded`, body: `q=<query>&format=json` |
| **Health** | `GET /healthz` → `OK` |
| **Default Engines** | `brave`, `wikipedia`, `arxiv`, `semantischolar` |
| **Safesearch** | `0` (off) by default |
| **Max Results** | 10 per query |
| **Timeout** | 10s |

**Protocol**:
```bash
# Search
curl -s -X POST http://localhost:8017/search \
  -d "q=omega+engine+AI&format=json&safesearch=0"

# Health check
curl -sf http://localhost:8017/healthz
```

**Important**: SearXNG does NOT accept `Content-Type: application/json`. Use form-encoded data or query parameters with `format=json`.

**Stability**: The container may restart. Use `Restart=always` in Quadlet. Check with `systemctl --user status omega-searxng.service`.

### 1.2 Exa (Cloud — Semantic Search)

| Attribute | Value |
|-----------|-------|
| **API Key** | `EXA_API_KEY` in `.env` |
| **Endpoints** | Search: `https://api.exa.ai/search`, Contents: `https://api.exa.ai/contents` |
| **MCP** | `type: "remote"`, URL `https://mcp.exa.ai/mcp?tools=web_search_exa,web_fetch_exa` |
| **Monthly Quota** | 1000 queries (up to $20 credit) |
| **Reserved Emergency** | 100 queries |
| **Best For** | Semantic search, deep content extraction, high-relevance results |
| **Timeout** | 15s |

**Protocol**:
```python
# Search
resp = await client.post(
    "https://api.exa.ai/search",
    headers={"x-api-key": API_KEY},
    json={"query": query, "num_results": 10, "type": "high", "text": True}
)

# Content fetch
resp = await client.post(
    "https://api.exa.ai/contents",
    headers={"x-api-key": API_KEY},
    json={"urls": [url], "text": True}
)
```

### 1.3 Tavily (Cloud — RAG-Optimized)

| Attribute | Value |
|-----------|-------|
| **API Key** | `TAVILY_API_KEY` in `.env` |
| **Endpoint** | `https://api.tavily.com/search` |
| **MCP** | `type: "stdio"`, command `npx -y @tavily/mcp` |
| **Monthly Quota** | 1000 queries (free tier) |
| **Best For** | AI-optimized retrieval, structured results |
| **Timeout** | 15s |

**Important**: **Tavily API key was returning 401 Unauthorized.** It may be expired. Use sparingly. Prefer SearXNG or Exa.

**Protocol**:
```python
resp = await client.post(
    "https://api.tavily.com/search",
    json={
        "api_key": API_KEY,
        "query": query,
        "max_results": 8,
        "search_depth": "advanced",
    }
)
```

### 1.4 Serper.dev (Cloud — Google Search)

| Attribute | Value |
|-----------|-------|
| **API Key** | `SERPER_API_KEY` in `.env` |
| **MCP** | `type: "remote"`, URL `https://mcp.serper.dev/mcp` |
| **Monthly Quota** | 2500 queries (free tier) |
| **Best For** | Google-grade web search, SERP results |
| **Timeout** | 10s |

### 1.5 Jina AI (Cloud — Content Extraction)

| Attribute | Value |
|-----------|-------|
| **API Key** | `JINA_API_KEY` in `.env` |
| **MCP** | `type: "remote"`, URL `https://mcp.jina.ai/v1` |
| **Search** | `https://s.jina.ai/<query>` (GET, returns markdown) |
| **Reader** | `https://r.jina.ai/<url>` (GET, returns clean content) |
| **Monthly Quota** | 10,000 tokens (very generous) |
| **Best For** | URL content extraction, academic search |
| **Timeout** | Search: 15s, Read: 30s |

**Protocol**:
```python
# Search
resp = await client.get(
    f"https://s.jina.ai/{query}",
    headers={"Authorization": f"Bearer {API_KEY}"}
)

# Read URL
resp = await client.get(
    f"https://r.jina.ai/{url}",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "X-Retain-Images": "none",
        "X-With-Links-Summary": "false",
    }
)
```

### 1.6 Firecrawl (Cloud — Deep Extraction)

| Attribute | Value |
|-----------|-------|
| **API Key** | `FIRECRAWL_API_KEY` in `.env` |
| **MCP** | `type: "stdio"`, command `npx -y firecrawl-mcp` |
| **Monthly Quota** | 1000 credits (free tier) |
| **Best For** | Deep content extraction, full page markdown |
| **Timeout** | 30s |

**Important**: Firecrawl credits are **limited and expensive** (1-2 credits per deep extract). Only use for final-stage deep reading, not for initial search.

---

## §2 Search Strategy — The Verification Cascade

### 2.1 Depth-Based Strategy

| Depth | Level | Search Providers | Extract Steps | Cycle Time |
|-------|-------|-----------------|---------------|------------|
| **1** | Light | SearXNG only | None | ~3s |
| **2** | Standard | SearXNG + 1 cloud (Tavily → Exa → Jina) | Jina Reader | ~15s |
| **3** | Deep | SearXNG + all cloud + fallback chain | Firecrawl deep | ~60s |

### 2.2 Provider Selection Priority

```
SEARCH:
  1. SearXNG (zero cost, always try first)
  2. Tavily (if quota remaining) → Exa → Jina → Serper

EXTRACT:
  1. Jina Reader (token-based, generous)
  2. Exa Contents (semantic, high quality)
  3. Direct HTTP fetch (no quota, unreliable)

DEEP EXTRACT:
  1. Firecrawl (deep, but expensive credits)
```

### 2.3 Verification Cascade

For claims that need verification:

```
Claim → SearXNG (3+ sources)
   ├── 3+ sources agree → VERIFIED ✓
   ├── Sources contradict → FLAG FOR HUMAN REVIEW ⚠️
   └── < 3 sources → Deepen with cloud fleet
         ├── Exa semantic search
         ├── Jina Reader for content extraction
         └── Firecrawl if still insufficient
```

### 2.4 Quota Management Rules

```yaml
# Default monthly budgets
exa:        total=1000, reserved_emergency=100
tavily:     total=1000, reserved_emergency=100
firecrawl:  total=1000, reserved_emergency=100
serper:     total=2500, reserved_emergency=500
jina:       total=10000, reserved_emergency=1000

# Daily limits
search_ops:      30/day
deep_extracts:    5/day
gemma_calls:     20/day
```

**Hard Rules**:
- Never consume reserved emergency credits unless no other source is available
- Daily limits reset at midnight UTC
- Budget state persists in `data/research/credit_budget.json`
- When quotas are exhausted, fall back entirely to SearXNG

---

## §3 Extraction Protocol

### 3.1 Content Extraction Priority

```
1. Jina Reader (r.jina.ai/<url>)
   - Fast, token-based, generous quota
   - Returns clean markdown
   - Best for most web content

2. Exa Contents (api.exa.ai/contents)
   - Semantic extraction, high quality
   - Better for technical/academic content
   - Limited by query quota

3. Direct HTTP (requests/httpx)
   - No quota cost
   - May get blocked by anti-bot measures
   - Unstructured HTML to parse
   - Timeout: 10s, max 8000 chars

4. Firecrawl Deep (api.firecrawl.dev/v1/scrape)
   - Most thorough extraction
   - Handles JS-rendered content
   - 1-2 credits per call — use sparingly
```

### 3.2 Content Truncation

| Provider | Max Chars | Strategy |
|----------|-----------|----------|
| Jina Reader | Full page | Use entire response |
| Exa Contents | 8000 | Truncate at 8000 |
| Direct HTTP | 8000 | Truncate at 8000 |
| Firecrawl | 8000 | Truncate at 8000 |

### 3.3 Distillation Pipeline

```
Raw Content → Chunk (max 12k chars) → Gemma 4-31B → 3-Tier Distillation
                                                           ├── L1 (Narrative)
                                                           ├── L2 (Insight)
                                                           └── L3 (Universal Principle → soul.yaml)
```

---

## §4 OpenCode MCP Integration

### 4.1 MCP Server Configuration

All MCP servers are defined in `opencode.json` under the `mcp` key:

```json
{
  "mcp": {
    "firecrawl": {
      "type": "stdio",
      "command": ["npx", "-y", "firecrawl-mcp"],
      "env": { "FIRECRAWL_API_KEY": "${FIRECRAWL_API_KEY}" }
    },
    "exa": {
      "type": "remote",
      "url": "https://mcp.exa.ai/mcp?tools=web_search_exa,web_fetch_exa",
      "headers": { "x-api-key": "${EXA_API_KEY}" }
    },
    "serper": {
      "type": "remote",
      "url": "https://mcp.serper.dev/mcp",
      "headers": { "x-api-key": "${SERPER_API_KEY}" }
    },
    "jina": {
      "type": "remote",
      "url": "https://mcp.jina.ai/v1",
      "headers": { "Authorization": "Bearer ${JINA_API_KEY}" }
    }
  }
}
```

**Important**: OpenCode MCP types must be one of `stdio`, `sse`, or `remote`. The type `local` is NOT valid and will cause the MCP server to be silently ignored.

### 4.2 MCP Type Reference

| Type | Use Case | Example |
|------|----------|---------|
| `stdio` | Local processes (npx, pip, uvx) | `firecrawl-mcp`, `@tavily/mcp` |
| `sse` | Local network services with streamed events | `omega-hub`, `omega-research` |
| `remote` | Cloud HTTP services | Exa, Serper, Jina |

### 4.3 Config Merge Behavior

OpenCode merges `~/.config/opencode/mcp_servers.json` (global) with `opencode.json` (project):

```
Global Config (~/.config/opencode/mcp_servers.json)
└── Project Config (opencode.json) ← OVERRIDES for duplicate names
```

The project config overrides the global config for servers with the same name.

---

## §5 Best Practices

### 5.1 Searching

1. **Start with SearXNG** — zero cost, always available when running
2. **Formulate specific queries** — "describe the ideal page" not keywords
3. **Validate SearXNG health first** — `curl -sf http://localhost:8017/healthz`
4. **Escalate depth progressively** — start at depth 1, only go deeper if needed
5. **Prefer Tavily/Exa for semantic search**, Jina for content extraction

### 5.2 Extracting

1. **Jina Reader is the default extractor** — most efficient for content extraction
2. **Exa for high-quality technical content** — 1 query per extraction
3. **Firecrawl for last resort** — expensive credits, JS-rendered pages only
4. **Never exceed 12k chars per distillation batch** — Gemma context window limit
5. **Always collect source URLs** metadata for verification

### 5.3 Quota Conservation

1. Let SearXNG handle 80%+ of search volume
2. Reserve cloud APIs for cases where SearXNG returns insufficient results
3. Use depth=1 for routine verification, depth=3 only for critical deep research
4. Set `reserved_emergency` as a hard floor — never go below

### 5.4 Stability

1. SearXNG may restart unexpectedly — wrap searches in retry logic
2. All cloud APIs may return 401/429 — implement fallback chains
3. Always have a graceful fallback for every query
4. Log all API failures for budget forensic analysis

---

## §6 Error Handling Matrix

| Error | Likely Cause | Action |
|-------|-------------|--------|
| SearXNG connection refused | Container down | `systemctl --user restart omega-searxng.service` |
| SearXNG returns HTML | Wrong content-type | Use form-encoded not JSON body |
| Exa 401 | EXA_API_KEY missing/expired | Check `.env` |
| Tavily 401 | TAVILY_API_KEY expired | Replace key at tavily.com |
| Jina 401 | JINA_API_KEY missing | Check `.env` |
| Firecrawl 402 | Credits exhausted | Wait for next billing cycle |
| All providers fail | No network | Fall back to offline mock |
| Quota exhausted | Monthly budget depleted | Wait for month reset, or use SearXNG only |

---

## §7 Quick Reference — One-Liner Commands

```bash
# SearXNG health
curl -sf http://localhost:8017/healthz

# SearXNG search (JSON)
curl -s "http://localhost:8017/search?q=<query>&format=json" | jq .

# Budget status
python3 -m omega.workers.background_researcher.run --status

# Run one research cycle
python3 -m omega.workers.background_researcher.run --topic "<topic>" --depth 2 --once

# Install systemd timer
cp config/systemd/omega-research.* ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable omega-research.timer
systemctl --user start omega-research.timer

# View research history
ls -la data/research/checkpoints/
cat data/research/pending_review.md
```

---

*This protocol is maintained by the Omega Background Researcher. Report discrepancies to the Research Queue.*
