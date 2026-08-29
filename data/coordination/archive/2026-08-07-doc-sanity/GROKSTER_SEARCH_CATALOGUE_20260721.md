# 🔱 Sovereign Search Tool Catalogue — Paid vs Free
## ⬡ GROKSTER ⬡ SEARCH CATALOGUE ⬡ 2026-07-21
## Complete Separation + Retrieval Reference for Cross-Tool Efficiency

> **Purpose**: This catalogue separates every search tool option (current + candidate) 
> into **paid** and **free** tiers, with pricing, capabilities, latency profiles, 
> API key requirements, integration effort, and retrieval guidance for each.
> 
> **Use this to answer**: "Which tool do I use for X, and how much does it cost?"

---

## 📊 Quick Reference — At a Glance

### 🟢 FREE OPTIONS (Zero direct monetary cost)

| Tool | Tier | Limit | API Key? | Best For |
|------|------|-------|----------|----------|
| `.firecrawl/` cache | **T0** | Disk space only | ❌ | Re-use prior results; avoid re-fetch |
| `websearch`/`webfetch` | **T1** | Tool rate limit | ❌ | Primary always-available search |
| SearXNG | **T2** | Self-hosted infra | ❌ | Private metasearch; DuckDuckGo + Brave fallback |
| Semantic Scholar | **T3.5** | 100 req/sec (key) / 1/sec (no key) | Optional | Academic papers (200M+), citation graphs, TLDR |
| arXiv API | **T3.5** | 1 req/3 sec (no key) | ❌ | Preprint papers (2.2M+), math/physics/CS |
| OpenAlex API | **T3.5** | 100k req/day (no key) | ❌ | Open research graph; cross-publisher discovery |
| GitHub Search API | **T3.5** | 5,000 req/hr (auth) / 60/hr (no auth) | Optional | Code search, repo discovery, issue tracking |
| Jina Reader (`r.jina.ai`) | **T2.5** | Unclear (free tier) | ❌ | URL-to-Markdown extraction (15KB chars) |
| Web Grok Free Tier | **N/A** | ~10 queries/hr per account | ❌ | Casual open-ended questions via browser |
| **Proposed**: OSS crawler | **T0.5** | Bandwidth only | ❌ | Lightweight scrape; self-owned pipeline |

### 🔵 PAID OPTIONS (Per-query, per-token, or subscription costs)

| Tool | Tier | Pricing | Free Allowance | Best For |
|------|------|---------|----------------|----------|
| **xAI web_search** | **T2.5** | **$5/1k calls** | ❌ (API key) | Inside xAI Responses API; model-executed search |
| **xAI x_search** | **T2.5** | **$5/1k calls** | ❌ (API key) | X/Twitter social signals; real-time pulse |
| **xAI code_execution** | **T3** | **$5/1k calls** | ❌ (API key) | Sandboxed Python; in-model computation |
| **xAI collections_search** | **T3** | **$2.50/1k calls** | ❌ (API key) | RAG over uploaded documents; file-attachment search |
| **Exa (sovereign_search)** | **T3** | ~$5/1k queries | ~100 free queries | Neural/semantic search; high-precision seeds |
| **Firecrawl** | **T4** | Credits-based | Scalable crawl | Full-page scrape; structured crawl; JS rendering |
| **Tavily** | **T3.5** | $8/1k queries | 1,000 free/mo | **All-in-one RAG**: search + extraction + citations |
| **Perplexity Sonar** | **T3.5** | $1-5/1M tokens (per-token) | ~$5 free credit | Pre-synthesized answer; **no separate LLM call** |
| **CatchAll (Newscatcher)** | **T3.5** | Usage-based | Free tier avail | High-recall monitoring; entity scoring; compliance |
| **Twelve Labs** | **T4.5** | Cloud API | ~$50 free trial | Video-native search; scene detection; NLP in video |
| **Mixpeek** | **T4.5** | Cloud API (usage) | Limited free | Multimodal search (video, image, audio, docs) |

**FREE OPTIONS (Zero direct monetary cost)**

| Tool | Tier | Limit | API Key? | Best For |
|------|------|-------|----------|----------|
| `.firecrawl/` cache | **T0** | Disk space only | ❌ | Re-use prior results; avoid re-fetch |
| `websearch`/`webfetch` | **T1** | Tool rate limit | ❌ | Primary always-available search |
| SearXNG | **T2** | Self-hosted infra | ❌ | Private metasearch; DuckDuckGo + Brave fallback |
| **Semantic Scholar** | **T3.5** | 100 req/sec (key) / 1/sec (no key) | Optional | Academic papers (200M+), citation graphs, TLDR |
| arXiv API | **T3.5** | 1 req/3 sec (no key) | ❌ | Preprint papers (2.2M+), math/physics/CS |
| OpenAlex API | **T3.5** | 100k req/day (no key) | ❌ | Open research graph; cross-publisher discovery |
| GitHub Search API | **T3.5** | 5,000 req/hr (auth) / 60/hr (no auth) | Optional | Code search, repo discovery, issue tracking |
| Jina Reader (`r.jina.ai`) | **T2.5** | Unclear (free tier) | ❌ | URL-to-Markdown extraction (15KB chars) |
| Web Grok Free Tier | **N/A** | ~10 queries/hr per account | ❌ | Casual open-ended questions via browser |
| **Proposed**: OSS crawler | **T0.5** | Bandwidth only | ❌ | Lightweight scrape; self-owned pipeline |

**Brave Search API** has a free tier of 2,000 queries/month with a 1 query/second rate limit. The paid tier starts at $3-5/1k queries. Updated based on current information.

**Serper.dev** has a free tier of 2,500 queries on signup. The paid tier is $0.30-1/1k queries.

**Exa** has a free tier of ~100 queries. The paid tier is ~$5/1k queries.

**Firecrawl** has a free tier of 1,000 pages one-time. The paid tier is credits-based.

**Tavily** has a free tier of 1,000 searches/month. The paid tier is $8/1k queries.

**Perplexity Sonar** has a free tier of ~$5 free credit. The paid tier is $1-5/1M tokens.

**CatchAll (Newscatcher)** has a free tier available. The paid tier is usage-based.

**Twelve Labs** has a free trial of ~$50. The paid tier is cloud API.

**Mixpeek** has a limited free tier. The paid tier is cloud API (usage).

---

## 🧠 Deep Catalogue — Detailed Profiles

Each profile answers: *What is it? How fast? How much? What auth? How to integrate? When to use?*

---

### 🟢 FREE: `.firecrawl/` Local Cache

| Field | Value |
|-------|-------|
| **Current Tier** | **T0** — Always check first |
| **Status** | ✅ Already in stack (partial — `.firecrawl/` dir exists) |
| **What it is** | Local filesystem cache of previously fetched pages |
| **Pricing** | **$0** (disk space only) |
| **Latency** | ~1-5ms (local read) |
| **API Key Required** | ❌ |
| **Capabilities** | Content re-use; avoids duplicate network fetches |
| **Limitations** | No TTL-based eviction policy; no index beyond flat directory |
| **Integration** | Already wired. Needs: TTL eviction (30d T1, 14d T2, 7d T3) |
| **When to Use** | **Always first** — before any external call. Check cache → hit → done |
| **When to Skip** | Fresh content required; TTL has expired |

---

### 🟢 FREE: `websearch` / `webfetch` (Built-In)

| Field | Value |
|-------|-------|
| **Current Tier** | **T1** — Primary always-available search |
| **Status** | ✅ Already in stack |
| **What it is** | Built-in web search and fetch tools provided by the execution environment |
| **Pricing** | **$0** (included with model access) |
| **Latency** | ~1-3s search; ~3-8s fetch |
| **API Key Required** | ❌ |
| **Capabilities** | General web search; page content extraction |
| **Limitations** | Opaque ranking algorithm; no independent index; no citation shaping |
| **Integration** | Already wired. Default tool for all general queries |
| **When to Use** | **Default first step** for any query that needs fresh data |
| **When to Skip** | Need independent index; need academic results; need video/code search |

---

### 🟢 FREE: SearXNG (Self-Hosted Metasearch)

| Field | Value |
|-------|-------|
| **Current Tier** | **T2** — Sovereign metasearch |
| **Status** | ✅ Already in stack (MCP server connected) |
| **What it is** | Self-hosted privacy metasearch engine; aggregates DuckDuckGo, Google, Brave, Wikipedia, etc. |
| **Pricing** | **$0** (requires infrastructure — Podman container) |
| **Latency** | ~1-4s (aggregates multiple engines) |
| **API Key Required** | ❌ (self-hosted; no external API key) |
| **Capabilities** | 15+ engines; category filtering (general, science, videos, files, IT, news, images); language/region/time filters |
| **Limitations** | No JS rendering; no multimodal search; depends on upstream engine availability |
| **Integration** | Already wired via `searxng_searxng_search` tool. MCP server at `mcp_servers/searxng/` |
| **When to Use** | **Privacy-sensitive queries**; sovereign alternative to websearch; advanced filtering (date range, language, category) |
| **When to Skip** | Need JS rendering; single-category deep dive better via specialized API |

---

### 🟢 FREE: Semantic Scholar Academic Graph API

| Field | Value |
|-------|-------|
| **Current Tier** | **Proposed T3.5** — Academic/research search |
| **Status** | 🟡 Not integrated — **candidate** |
| **What it is** | Academic paper index covering 200M+ papers: arXiv, bioRxiv, PubMed, IEEE, ACM, Nature, etc. |
| **Pricing** | **$0** (rate-limited; free API key for higher limits) |
| **Latency** | ~0.3-1.5s per query |
| **API Key Required** | Optional (free; 100 req/sec with key vs 1/sec without) |
| **Capabilities** | Keyword search; citation traversal (forward/backward); TLDR summaries (AI-generated); recommendations by paper; author lookup; bulk search; SPECTER embeddings |
| **Limitations** | Academic focus only; no news/blogs/general web; rate limits without key |
| **Integration** | REST API: `https://api.semanticscholar.org/graph/v1/paper/search`. Use `?query=&year=&fieldsOfStudy=&fields=title,url,abstract,tldr,citationCount,publicationDate`. Auth via `x-api-key` header |
| **Retrieval Pattern** | `search?query=attention mechanism` → get paper IDs → TLDR summaries → LLM-ready abstracts |
| **When to Use** | **Any research question** that benefits from academic sources; citation chain analysis; literature reviews |
| **When to Skip** | Practical/general questions (use Brave or websearch); real-time news |

---

### 🟢 FREE: arXiv API

| Field | Value |
|-------|-------|
| **Current Tier** | **Proposed T3.5** — Preprint search |
| **Status** | 🟡 Not integrated — **candidate** |
| **What it is** | Preprint repository API covering 2.2M+ papers in physics, mathematics, computer science, biology, finance, statistics |
| **Pricing** | **$0** (no API key required; polite rate limit: 1 req / 3 sec) |
| **Latency** | ~0.5-2s |
| **API Key Required** | ❌ |
| **Capabilities** | Keyword search; author search; ID lookup; category filtering; atom/xml response |
| **Limitations** | Preprints only (not peer-reviewed); no citation graph; strict rate limit; XML response format |
| **Integration** | REST API: `http://export.arxiv.org/api/query?search_query=all:transformer&max_results=10&sortBy=submittedDate` |
| **When to Use** | **Latest preprints** before peer review; math/CS/physics research; complement to Semantic Scholar |
| **When to Skip** | Peer-reviewed sources needed; general web search |

---

### 🟢 FREE: OpenAlex API

| Field | Value |
|-------|-------|
| **Current Tier** | **Proposed T3.5** — Open research graph |
| **Status** | 🟡 Not integrated — **candidate** (bonus on Semantic Scholar) |
| **What it is** | Open catalog of global research: 250M+ works, 100M+ authors, institutions, publishers, concepts |
| **Pricing** | **$0** (100,000 req/day without key; higher with key; NO rate limit without email header) |
| **Latency** | ~0.3-1s |
| **API Key Required** | ❌ (recommend: add `mailto:` header for priority) |
| **Capabilities** | Cross-publisher discovery; concept tagging; author disambiguation; institution filtering; open access links |
| **Integration** | REST API: `https://api.openalex.org/works?search=attention%20is%20all%20you%20need` |
| **When to Use** | **Broad research graph discovery** — finding papers across publisher boundaries; affiliation-based search |
| **When to Skip** | Need paper PDFs or TLDR summaries (use Semantic Scholar instead) |

---

### 🟢 FREE: Jina Reader API

| Field | Value |
|-------|-------|
| **Current Tier** | **Proposed T2.5** — URL-to-Markdown extraction |
| **Status** | 🟡 Not integrated — **candidate** |
| **What it is** | Free URL-to-Markdown converter: prepend `r.jina.ai/` to any URL, get clean Markdown |
| **Pricing** | **$0** (~15K chars per request, no API key needed) |
| **Latency** | ~1-4s (depends on page complexity) |
| **API Key Required** | ❌ |
| **Capabilities** | Converts any public URL to clean Markdown; preserves structure; handles JavaScript |
| **Limitations** | May hit paywalls or JS-gated content; rate limits unclear on free tier |
| **Integration** | `webfetch { url: "https://r.jina.ai/https://example.com" }` — no API key needed |
| **When to Use** | **Quick Markdown extraction** from any web page; supplement to webfetch for JS-rendered pages |
| **When to Skip** | Already have the content via webfetch; high-volume extraction (get API key) |

---

### 🟢 FREE: GitHub Search API

| Field | Value |
|-------|-------|
| **Current Tier** | **Proposed T3.5** — Code/developer search |
| **Status** | 🟡 Not integrated — **candidate** |
| **What it is** | GitHub's search API: repositories, code, issues, users |
| **Pricing** | **$0** (5,000 req/hr authenticated; 60 req/hr unauthenticated) |
| **Latency** | ~0.5-2s |
| **API Key Required** | Recommended (free, higher rate limits) |
| **Capabilities** | Code search by language/repo/org; repository discovery by topic/stars; issue tracking; file content search |
| **Limitations** | Code search is limited to default branch; no semantic code understanding |
| **Integration** | REST API: `https://api.github.com/search/code?q=anyio+in:file+language:python` |
| **When to Use** | **Find code patterns** across open-source repos; check if a library is widely used; find examples |
| **When to Skip** | Need general web search; need documentation rather than source code |

---

### 🔵 PAID: Brave Search API

| Field | Value |
|-------|-------|
| **Current Tier** | **Proposed T2.5** — Independent index |
| **Priority** | **P0** — Highest priority integration |
| **Status** | 🟡 Not integrated — **recommended next** |
| **What it is** | Fully independent search index (30B+ pages, own crawler, not a Big Tech reseller). Official MCP server available. |
| **Pricing** | $3-5/1k queries; 2,000 queries **free/month** |
| **Latency** | ~0.8s (fastest AI-native tier) |
| **API Key Required** | ✅ (free tier: 2,000/mo; paid: $3-5/1k) |
| **API Key Location** | `config/providers.yaml` → `brave` section (proposed) |
| **Capabilities** | General web search; news search; video search; image search; **LLM Context API** (reshaped snippets ready for LLM consumption, Feb 2026); SOC 2 Type II; GDPR compliant; zero data retention option |
| **Limitations** | Smaller index than Google (30B vs 100B+); limited international coverage vs Google |
| **MCP** | **Official MCP server** (`@anthropic/brave-search`) — drops into Claude Code/Cursor in 3 config lines |
| **Integration** | **Option A (MCP)**: 3 lines in `opencode.json` → `mcpServers.brave.command: "npx -y @anthropic/brave-search"`
   **Option B (REST)**: `GET https://api.search.brave.com/res/v1/web/search?q=query` + `Accept: application/json` + `X-Subscription-Token: {key}`
   **Option C (Provider)**: Wire as new backend in `ModelGateway` → `providers.yaml` |
| **When to Use** | **Primary independent search** — sovereignty priority; LLM-aware context; privacy compliance needs |
| **When to Skip** | High-volume → use Serper (cheaper); need Google-specific results |
| **Clients Already Using** | Cohere, Mistral AI, AWS, Shopify, Snowflake |

---

### 🔵 PAID: Serper.dev + Jina Reader

| Field | Value |
|-------|-------|
| **Current Tier** | **Proposed T2.5** — Budget SERP |
| **Priority** | **P1** — Cheapest production search stack |
| **Status** | 🟡 Not integrated — **candidate** |
| **What it is** | Google SERP wrapper (search engine results page) + Jina Reader for free Markdown extraction |
| **Pricing** | **$0.30-1/1k queries** (Serper); Jina Reader is **$0** (free) |
| **Free Allowance** | 2,500 queries free on Serper signup |
| **Latency** | ~0.5s (fastest in class) |
| **API Key Required** | ✅ (Serper only; Jina is free) |
| **Capabilities** | Google search results (organic + ads + news + images + places); geo/location targeting; autocomplete |
| **Limitations** | Snippets only from Serper (no built-in extraction); need separate LLM call to summarize; Jina adds latency for extraction |
| **Integration** | REST: `POST https://google.serper.dev/search { "q": "query" }` with `X-API-KEY` header
   Jina: prepend `r.jina.ai/` to target URL |
| **When to Use** | **High-volume, low-criticality** searches; cost-optimized pipeline; budget tier |
| **When to Skip** | Need independent index (use Brave); need citation-shaped results (use Tavily) |
| **Total Stack Cost** | ~$0.50/1k queries (Serper + Jina) — **cheapest production stack** |

---

### 🔵 PAID: xAI API Server-Side Tools

| Field | Value |
|-------|-------|
| **Current Tier** | **Proposed T2.5-T3** — xAI-native tools |
| **Status** | 🟡 Not integrated (requires xAI API key + Responses API) |
| **What it is** | Tools executed by Grok models inside the Responses API: `web_search` (browse internet), `x_search` (X/Twitter firehose), `code_execution` (Python sandbox) |
| **Pricing** | **$5/1k calls** each (web_search, x_search, code_execution) — **not included in model token cost** |
| **Latency** | ~1-3s per tool call (model + execution) |
| **API Key Required** | ✅ (xAI API key — `config/providers.yaml` → `xai` section) |
| **Capabilities** | `web_search`: browse internet, real-time info, citation support
   `x_search`: X/Twitter firehose, social signals, real-time pulse
   `code_execution`: sandboxed Python with packages, file I/O, HTTP client
   `collections_search`: $2.50/1k RAG over uploaded documents |
| **Limitations** | **Expensive at scale** ($5/1k per tool); tied to xAI model; only via Responses API |
| **Integration** | `POST /v1/responses { "model": "grok-4.5", "tools": [{"type": "web_search"}], "input": "what's the latest on AI?" }` |
| **When to Use** | **Inside Grok-powered workflows**; real-time X pulse; sandboxed code execution that feeds back into model |
| **When to Skip** | Using non-xAI models (can't use these tools); high-volume web search (cheaper via Brave/Serper) |

---

### 🔵 PAID: Exa (sovereign_search)

| Field | Value |
|-------|-------|
| **Current Tier** | **T3** — Neural/semantic search |
| **Status** | ✅ Already in stack (via `omega-hub_sovereign_search`) |
| **What it is** | Neural search engine designed for LLMs — embeddings-based semantic retrieval. "Google for AI" |
| **Pricing** | ~$5/1k queries (~100 free queries) |
| **Latency** | ~1-3s |
| **API Key Required** | ✅ (Exa API key — stored in Omega-Vault prototype) |
| **Capabilities** | Semantic similarity search; keyword + neural hybrid; date filtering; domain filtering; content extraction |
| **Limitations** | Expensive at scale; smaller index than Google; not great for real-time news |
| **When to Use** | **High-precision seeds**; academic/technical queries where semantic understanding matters |
| **When to Skip** | Broad queries; high-volume; real-time needs |

---

### 🔵 PAID: Firecrawl

| Field | Value |
|-------|-------|
| **Current Tier** | **T4** — Full scrape + crawl |
| **Status** | ✅ Already in stack (credits-based) |
| **What it is** | Full-page scraping and structured crawling engine. JS rendering, PDF extraction, sitemap crawl |
| **Pricing** | Credits-based (usage-dependent) |
| **Latency** | ~2-10s per page; slower for full crawls |
| **API Key Required** | ✅ (Firecrawl API key) |
| **Capabilities** | Full-page scrape; recursive crawl; sitemap-based crawl; JS rendering; PDF/doc extraction; screenshot |
| **When to Use** | **Deep page extraction**; JS-heavy sites; full site mapping; structured crawl |
| **When to Skip** | Quick search (use Brave or websearch); simple URL fetch (use webfetch or Jina) |

---

### 🔵 PAID: Tavily

| Field | Value |
|-------|-------|
| **Current Tier** | **Proposed T3.5** — Citation-shaped RAG |
| **Priority** | **P2** — When RAG pipeline simplification matters |
| **Status** | 🟡 Not integrated — **candidate** |
| **What it is** | AI-native search engine that returns search results + cleaned full-page text + citation-shaped payload in one call |
| **Pricing** | **$8/1k queries**; 1,000 queries free/month |
| **Latency** | ~2.1s (slowest in top tier — bundled extraction adds latency) |
| **API Key Required** | ✅ |
| **Capabilities** | `search_depth: advanced` → full-page content extraction + cleaning; `include_raw_content=True` → full page text for LLM; citation formatting; LangChain native |
| **Limitations** | 2.1s latency is slowest premium tier; expensive at $8/1k; smaller index |
| **Integration** | `POST https://api.tavily.com/search { "query": "...", "search_depth": "advanced", "include_raw_content": true }`
   **LangChain**: `TavilySearchAPIWrapper()` — packaged |
| **When to Use** | **RAG pipeline in one call** — replaces (websearch → webfetch → chunk → embed → search); saves token round-trips |
| **When to Skip** | Low-volume or cost-sensitive (cheaper options exist); need raw results control (use Brave) |
| **Total System Cost** | Only ~14% more than cheapest stack, but **vastly simpler code** |

---

### 🔵 PAID: Perplexity Sonar API

| Field | Value |
|-------|-------|
| **Current Tier** | **Proposed T3.5** — Synthesized answer |
| **Priority** | **P2** — When separate LLM call is the bottleneck |
| **Status** | 🟡 Not integrated — **candidate** |
| **What it is** | Pre-synthesized answer with inline citations. Models: Sonar, Sonar Pro, Sonar Reasoning Pro, Sonar Deep Research |
| **Pricing** | **$1-5/1M tokens** (input/output combined, includes live web search cost in token price — NO separate per-query fee) |
| **Latency** | ~2-3s (synthesis takes time) |
| **API Key Required** | ✅ |
| **Capabilities** | Pre-synthesized answers with inline citations; `previous_query_id` for follow-ups; live web search included in token cost; OpenAI SDK compatible |
| **Limitations** | No raw results to control ranking/filtering; committed to Perplexity's model; not for agent stacks needing raw passages |
| **Integration** | OpenAI-compatible: `client.chat.completions.create(model="sonar-pro", messages=[...])` with `extra_body={"search_domain_filter": [...]}` |
| **When to Use** | **User-facing Q&A** where you want a polished answer with citations; **replace separate LLM call** for answer synthesis |
| **When to Skip** | Agent stacks that need raw passages for RAG/computation; need to control ranking |
| **Models** | Sonar ($1/$1 per 1M), Sonar Pro ($3/$5), Sonar Reasoning Pro ($2/$8), Sonar Deep Research ($2/$8) |

---

### 🔵 PAID: CatchAll (Newscatcher)

| Field | Value |
|-------|-------|
| **Current Tier** | **Proposed T3.5** — High-recall monitoring |
| **Priority** | **P3** — Specialized, not immediate |
| **Status** | 🟡 Not integrated — **candidate** |
| **What it is** | Recall-first web monitoring index — scans 50,000+ pages per job; structured event records with entity extraction |
| **Pricing** | Usage-based (pay per validated record); free tier available |
| **Latency** | Lite: ~seconds; Base: ~15 min (async processing) |
| **API Key Required** | ✅ |
| **Capabilities** | **Monitors** (scheduled re-runs); **Watchlists** (entity scoring + sentiment); structured event records with source citations + extracted entities; competitive intelligence; compliance monitoring |
| **Limitations** | Not a SERP replacement; deep mode is async (15 min); no MCP server yet |
| **When to Use** | **Continuous topic monitoring**; compliance scanning; competitive intelligence; supply-chain tracking |
| **When to Skip** | One-off searches; need real-time results |

---

### 🔵 PAID: Twelve Labs / Mixpeek

| Field | Value |
|-------|-------|
| **Current Tier** | **Proposed T4.5** — Video/multimodal search |
| **Priority** | **P3-P4** — Specialized, future |
| **Status** | 🟡 Not integrated — **candidate** |
| **What it is** | Video-native AI search. Marengo (scene understanding) + Pegasus (text/video search). Mixpeek = multimodal (video, image, audio, docs) in one API |
| **Pricing** | Cloud API (~$50 free trial for Twelve Labs); Mixpeek usage-based |
| **Latency** | Indexing: ~60x real-time speed (1h video in 1 min) |
| **API Key Required** | ✅ |
| **Capabilities** | Natural language video search; scene detection; summarization; action/event understanding across vision+audio+text |
| **When to Use** | **Video content analysis**; YouTube research; archival footage; training materials |
| **When to Skip** | Text-only workflows |

---

## 🧭 Retrieval Decision Tree — Which Tool to Use

```
START: I need to find information
│
├─ Is it something I've fetched before?
│   └─ ✅ → T0: .firecrawl/ cache (instant, $0)
│
├─ Is it a general web question?
│   ├─ Need independent/sovereign index?
│   │   ├─ ✅ → Brave Search API ($3-5/1k, T2.5) — first choice
│   │   └─ ❌ → websearch ($0, T1) — always available
│   ├─ Need CHEAPEST option?
│   │   └─ → Serper + Jina ($0.50/1k, T2.5) — budget tier
│   └─ Need privacy?
│       └─ → SearXNG ($0, T2) — self-hosted metasearch
│
├─ Is it an academic or research question?
│   ├─ Need peer-reviewed papers?
│   │   └─ → Semantic Scholar ($0, T3.5) — 200M papers, TLDR summaries
│   ├─ Need latest preprints?
│   │   └─ → arXiv API ($0, T3.5) — 2.2M preprints
│   └─ Need broad cross-publisher discovery?
│       └─ → OpenAlex ($0, T3.5) — 250M works
│
├─ Is it a code/developer question?
│   └─ → GitHub Search API ($0, T3.5) — 5,000 req/hr
│
├─ Is it about real-time X/Twitter pulse?
│   ├─ Via Grok model → xAI x_search ($5/1k, T2.5)
│   └─ Via general → websearch ($0, T1)
│
├─ Is it a RAG pipeline question?
│   ├─ Want one-call solution?
│   │   └─ → Tavily ($8/1k, T3.5) — search + extraction + citation in 1 call
│   └─ Want separate control?
│       └─ → Brave ($3-5/1k, T2.5) + webfetch ($0, T1)
│
├─ Is it a user-facing Q&A that needs polished answer?
│   └─ → Perplexity Sonar ($1-5/1M tokens, T3.5) — no separate LLM call
│
├─ Is it high-recall monitoring?
│   └─ → CatchAll ($?, T3.5) — scheduled re-runs, entity scoring
│
├─ Is it deep page extraction or full crawl?
│   ├─ Simple → webfetch ($0, T1)
│   ├─ JS-heavy → Firecrawl (credits, T4)
│   └─ Quick Markdown → Jina Reader ($0, T2.5)
│
├─ Is it video content search?
│   └─ → Twelve Labs ($?, T4.5) — video-native AI
│
└─ Is it semantic/nearest-neighbor search?
    └─ → Exa ($5/1k, T3) — neural embeddings search
```

---

## 🗺️ Tier Mapping — Where Each Tool Fits

| Tier | Current | Proposed Addition | Gap Filled |
|------|---------|-------------------|------------|
| **T0** Local cache | `.firecrawl/` | + TTL eviction policy | Content freshness |
| **T0.5** Lightweight scrape | ❌ | OSS crawler (proposed) | Self-owned crawl pipeline |
| **T1** Free web search | `websearch`/`webfetch` | — | — |
| **T2** Sovereign metasearch | SearXNG | — | — |
| **T2.5** Independent/Budget API | ❌ | **Brave** (P0) · **Serper** (P1) · xAI tools (when on Grok) | Independent index; cheapest SERP; xAI-native |
| **T3** Neural/semantic | Exa | — | — |
| **T3.5** Specialized search | ❌ | **Semantic Scholar** (P1) · **Tavily** (P2) · **Sonar** (P2) | Academic; RAG-in-one; synthesized answers |
| **T4** Full crawl/scrape | Firecrawl | — | — |
| **T4.5** Multimodal | ❌ | Twelve Labs (P3) | Video search |

---

## 💰 Cost Comparison — At Various Usage Levels

| Scenario | Monthly Volume | Cheapest Stack | Monthly Cost |
|----------|---------------|----------------|-------------|
| Light research | 500 queries | websearch + SearXNG + Semantic Scholar | **$0** |
| Active development | 5,000 queries | Brave ($3/1k) + Semantic Scholar ($0) | **$15** |
| Heavy research | 20,000 queries | Serper ($0.50/1k) + Semantic Scholar ($0) | **$10** |
| Production RAG | 50,000 queries | Brave ($3/1k) + Tavily ($8/1k, 20%) | **$150-230** |
| Enterprise scale | 200,000 queries | Serper ($0.30/1k) + Firecrawl (bulk) | **$60-100** |
| Video analysis | Variable | Twelve Labs ($50 trial → usage) | **$50-500** |

---

## 🎯 Integration Roadmap (Priority Order)

### Step 1 (Now — 2h) — Brave Search API as T2.5
- **Why**: Independent index = sovereignty priority. Official MCP = trivial integration.
- **Integration path**:
  ```json
  // opencode.json
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@anthropic/brave-search"],
      "env": { "BRAVE_API_KEY": "${BRAVE_API_KEY}" }
    }
  }
  ```
- **Or**: Wire as a provider in `config/providers.yaml` for programmatic access via ModelGateway
- **Cost**: $0 (2,000 free/mo covers light usage)

### Step 2 (Now — 4h) — Semantic Scholar as Academic T3.5
- **Why**: Free. 200M papers. TLDR summaries are LLM-ready. Instant capability multiplier.
- **Integration path**: REST API wrapper → `src/omega/search/semantic_scholar.py` → MCP tool `omega-hub_academic_search`
- **Cost**: $0

### Step 3 (Short-term — 2h) — Serper + Jina as Budget T2.5
- **Why**: Cheapest production stack at $0.50/1k. Use for high-volume search.
- **Integration path**: REST API wrapper → `providers.yaml` → `serper` backend
- **Cost**: $0 (2,500 free queries on signup)

### Step 4 (Medium-term — 3h) — Tavily for RAG Simplification
- **Why**: Replaces 5-step RAG pipeline with 1 call. LangChain native.
- **Integration path**: Provider backend → LangChain integration
- **Cost**: $8/1k (use sparingly; 1K free/mo)

### Step 5 (Medium-term — 2h) — Perplexity Sonar for User-Facing QA
- **Why**: Eliminates separate LLM call for answer synthesis.
- **Integration path**: OpenAI-compatible SDK → existing provider fabric
- **Cost**: $1-5/1M tokens (use for answer synthesis, not raw search)

### Step 6 (Future) — CatchAll, Twelve Labs, Code Search
- **Why**: Specialized needs; wait for foundation stability
- **Cost**: Variable

---

## 🔑 API Key Requirements — Quick Reference

| Tool | Key Required? | Key Source | Current Status |
|------|---------------|------------|----------------|
| `.firecrawl/` cache | ❌ | — | ✅ Already stored |
| `websearch`/`webfetch` | ❌ | — | ✅ Already available |
| SearXNG | ❌ | Self-hosted | ✅ Already running |
| Semantic Scholar | Optional (free key) | `api.semanticscholar.org` | 🟡 Needs key registration |
| arXiv API | ❌ | — | 🟡 No key needed |
| OpenAlex | ❌ | — | 🟡 No key needed |
| GitHub Search | Optional (free key) | GitHub PAT | 🟡 Needs PAT setup |
| Jina Reader | ❌ | — | 🟡 No key needed |
| Brave Search | ✅ (free tier) | `api.search.brave.com` | ❌ Needs key + integration |
| Serper.dev | ✅ (free signup) | `serper.dev` | ❌ Needs key + integration |
| xAI server tools | ✅ (paid key) | xAI API console | ❌ Needs key + Responses API setup |
| Exa | ✅ (paid key) | Exa dashboard | ✅ Already wired in sovereign_search |
| Firecrawl | ✅ (credits) | Firecrawl dashboard | ✅ Already wired |
| Tavily | ✅ (free tier) | Tavily dashboard | ❌ Needs key + integration |
| Perplexity Sonar | ✅ (paid key) | Perplexity API | ❌ Needs key + integration |
| CatchAll | ✅ (usage-based) | Newscatcher | ❌ Needs evaluation |
| Twelve Labs | ✅ (free trial) | Twelve Labs | ❌ Needs evaluation |

---

## 📐 Architecture: Unified Search Router (Proposed)

```
                ┌──────────────────────┐
                │   SEARCH ROUTER       │
                │  (Omega Hub: T0-T5)  │
                └──────┬───────┬───────┘
                       │       │
                ┌──────┘       └──────┐
                ▼                     ▼
        ┌───────────────┐   ┌───────────────┐
        │  FREE POOL    │   │  PAID POOL     │
        │  (Always try  │   │  (Fall through │
        │   first)      │   │   by config)   │
        └───────┬───────┘   └───────┬───────┘
                │                   │
     ┌──────────┼──────────┐  ┌────┼────┐
     ▼          ▼          ▼  ▼    ▼    ▼
 ┌──────┐ ┌────────┐ ┌──────┐ ┌──┐ ┌──┐ ┌────┐
 │Cache │ │web-    │ │SearXNG│ │B │ │S │ │Exa │
 │T0    │ │search  │ │T2    │ │r │ │e │ │T3  │
 │      │ │T1      │ │      │ │a │ │m │ │    │
 │      │ │        │ │      │ │v │ │a │ │    │
 │      │ │        │ │      │ │e │ │n │ │    │
 └──────┘ └────────┘ └──────┘ │T │ │t │ └────┘
                              │2 │ │i │
                              │. │ │c │
                              │5 │ │  │
                              └──┘ │T │
                                   │3 │
                                   │. │
                                   │5 │
                                   └──┘
```

**Fallback Chain**: T0 (cache) → T1 (websearch) → T2 (SearXNG) → T2.5 (Brave/Serper) → T3 (Exa) → T3.5 (Semantic Scholar/Tavily/Sonar) → T4 (Firecrawl) → T4.5 (Twelve Labs)

**Cost optimization**: Route by query type:
- General web → T1 or T2.5 Brave ($3-5/1k)
- Academic → T3.5 Semantic Scholar ($0)
- High volume → T2.5 Serper ($0.30-1/1k)
- RAG pipeline → T3.5 Tavily ($8/1k)
- Deep crawl → T4 Firecrawl (credits)
- Video → T4.5 Twelve Labs ($)

---

*⬡ GROKSTER ⬡ SEARCH CATALOGUE ⬡ 2026-07-21 ⬡ 17 FREE/PAID TOOLS CATALOGUED*

---

# 🔍 DEEP WEB RESEARCH: Search API Ecosystem Trends 2026

## Executive Summary

The search API ecosystem in 2026 is undergoing a significant transformation, characterized by **fragmentation, specialization, and strategic positioning**. The market has evolved from a simple Google-centric landscape to a sophisticated multi-tier ecosystem where different providers serve distinct use cases and price points.

**Key Market Dynamics:**
- **Hyper-specialization**: Search APIs now serve specific niches (academic research, real-time X/Twitter, semantic search, video, etc.)
- **Pricing polarization**: From free tiers ($0) to enterprise pricing ($50+/1M tokens)
- **Technology divergence**: Different architectures for different use cases (REST, GraphQL, streaming)
- **Regional considerations**: Compliance, data sovereignty, and localization requirements

---

## 📊 Market Landscape: 17 Major Players

### **FREE TIER OPTIONS (Zero Direct Cost)**

| Tool | Tier | Limit | API Key? | Best For |
|------|------|-------|----------|----------|
| `websearch`/`webfetch` | T1 | Tool rate limit | ❌ | Primary always-available search |
| SearXNG | T2 | Self-hosted infra | ❌ | Private metasearch; DuckDuckGo + Brave fallback |
| Semantic Scholar | T3.5 | 100 req/sec (key) / 1/sec (no key) | Optional | Academic papers (200M+), citation graphs, TLDR |
| arXiv API | T3.5 | 1 req/3 sec (no key) | ❌ | Preprint papers (2.2M+), math/physics/CS |
| OpenAlex API | T3.5 | 100k req/day (no key) | ❌ | Open research graph; cross-publisher discovery |
| GitHub Search API | T3.5 | 5,000 req/hr (auth) / 60/hr (no auth) | Optional | Code search, repo discovery, issue tracking |
| Jina Reader (`r.jina.ai`) | T2.5 | Unclear (free tier) | ❌ | URL-to-Markdown extraction (15KB chars) |
| Web Grok Free Tier | N/A | ~10 queries/hr per account | ❌ | Casual open-ended questions via browser |

### **PAID OPTIONS (Per-query, per-token, or subscription costs)**

| Tool | Tier | Pricing | Free Allowance | Best For |
|------|------|---------|----------------|----------|
| **xAI web_search** | **T2.5** | **$5/1k calls** | ❌ (API key) | Inside xAI Responses API; model-executed search |
| **xAI x_search** | **T2.5** | **$5/1k calls** | ❌ (API key) | X/Twitter social signals; real-time pulse |
| **xAI code_execution** | **T3** | **$5/1k calls** | ❌ (API key) | Sandboxed Python; in-model computation |
| **xAI collections_search** | **T3** | **$2.50/1k calls** | ❌ (API key) | RAG over uploaded documents; file-attachment search |
| **Exa (sovereign_search)** | **T3** | ~$5/1k queries | ~100 free queries | Neural/semantic search; high-precision seeds |
| **Firecrawl** | **T4** | Credits-based | Scalable crawl | Full-page scrape; structured crawl; JS rendering |
| **Tavily** | **T3.5** | $8/1k queries | 1,000 free/mo | **All-in-one RAG**: search + extraction + citations |
| **Perplexity Sonar** | **T3.5** | $1-5/1M tokens | ~$5 free credit | Pre-synthesized answer; **no separate LLM call** |
| **CatchAll (Newscatcher)** | **T3.5** | Usage-based | Free tier avail | High-recall monitoring; entity scoring; compliance |
| **Twelve Labs** | **T4.5** | Cloud API | ~$50 free trial | Video-native search; scene detection; NLP in video |
| **Mixpeek** | **T4.5** | Cloud API (usage) | Limited free | Multimodal search (video, image, audio, docs) |

---

## 🎯 Strategic Positioning & Use Cases

### **Tier 1: Sovereign Search (P0-P1)**
**Purpose**: Independence, privacy, compliance
**Tools**: Brave Search API, SearXNG
**Best for**: Privacy-sensitive queries, sovereign alternatives to Big Tech

### **Tier 2: Budget Search (P2-P3)**
**Purpose**: Cost-effective general search
**Tools**: Serper.dev + Jina Reader, xAI tools (when on Grok)
**Best for**: High-volume, cost-optimized pipelines

### **Tier 3: Specialized Search (P4-P5)**
**Purpose**: Domain-specific capabilities
**Tools**: Semantic Scholar, arXiv, GitHub Search, Jina Reader
**Best for**: Academic research, code search, URL extraction

### **Tier 4: VIP Search (P6-P7)**
**Purpose**: Advanced capabilities, enterprise needs
**Tools**: Exa, Firecrawl, Tavily, Perplexity Sonar
**Best for**: RAG pipelines, synthesized answers, video search

---

## 💰 Pricing Models Analysis

### **Usage-Based Pricing (Most Common)**
- **Per-query pricing**: $0.30-$5/1k queries
- **Per-token pricing**: $0.075-$15/1M tokens
- **Hybrid models**: Freemium + usage (Tavily, Perplexity)

### **Subscription Models**
- **Fixed monthly credits**: $16-$599/month
- **Enterprise custom**: Custom pricing, volume discounts

### **Freemium Models**
- **Free tier**: 1,000-5,000 queries/month
- **Conversion funnel**: Free → Pro → Enterprise

---

## 📈 Market Trends & Projections

### **Technology Trends**
1. **AI-native search**: Neural embeddings, semantic understanding
2. **Real-time capabilities**: X/Twitter, live data feeds
3. **Multimodal search**: Video, image, audio processing
4. **Specialized verticals**: Industry-specific search solutions

### **Business Model Evolution**
1. **From product to platform**: APIs becoming ecosystems
2. **Data as a service**: Premium datasets and analytics
3. **Managed services**: Full-stack search solutions
4. **Edge computing**: Distributed search capabilities

### **Pricing Disruption**
1. **Pay-per-use**: Eliminates upfront costs
2. **Usage-based scaling**: Costs align with value
3. **Enterprise customization**: Tailored pricing for large organizations
4. **Community pricing**: Open-source alternatives

---

## 🏢 Key Players Analysis

### **Established Players**
- **Google**: Search, Gemini API
- **Microsoft**: Bing Search API, Azure AI
- **OpenAI**: GPT API, Search API

### **Specialized Players**
- **Brave**: Independent search index, privacy-focused
- **Semantic Scholar**: Academic research, citation graphs
- **Exa**: Neural search, semantic understanding
- **Tavily**: All-in-one RAG, search + extraction

### **Emerging Players**
- **xAI**: Grok ecosystem, integrated search capabilities
- **Firecrawl**: Full-page scraping, structured crawl
- **CatchAll**: High-recall, compliance-focused search

---

## 🔮 Future Outlook (2026-2028)

### **Technology Convergence**
1. **AI-first search**: Neural networks driving relevance
2. **Cross-platform integration**: Unified search across domains
3. **Edge search**: Distributed search capabilities
4. **Privacy-preserving search**: Federated learning, differential privacy

### **Market Consolidation**
1. **Vertical integration**: Search providers expanding into adjacent services
2. **Platform ecosystems**: Search APIs becoming core infrastructure
3. **Standardization**: Industry standards for search interoperability

### **Pricing Evolution**
1. **Outcome-based pricing**: Pay for results, not queries
2. **Predictable pricing**: Subscription models with usage caps
3. **Dynamic pricing**: Real-time rate adjustments based on demand

---

## 📋 Strategic Recommendations

### **For Users**
1. **Assess requirements**: Define specific use cases and requirements
2. **Evaluate total cost of ownership**: Include implementation, maintenance, and usage costs
3. **Consider long-term needs**: Plan for growth and changing requirements
4. **Test multiple providers**: Evaluate different solutions before committing

### **For Providers**
1. **Differentiate on value**: Focus on specific niches and capabilities
2. **Build ecosystems**: Create partner programs and integrations
3. **Invest in AI**: Leverage machine learning for better relevance
4. **Offer flexible pricing**: Multiple pricing models for different segments

---

## 🎯 Conclusion

The search API ecosystem in 2026 represents a **mature but evolving market** with clear **specialization patterns** and **strategic positioning**. The key to success lies in:

1. **Understanding specific requirements**: Different use cases demand different solutions
2. **Balancing cost and capability**: Find the optimal trade-off between price and features
3. **Future-proofing investments**: Choose solutions that can scale with changing needs
4. **Leveraging ecosystem partnerships**: Integrate with complementary services

The market is moving toward **specialization** rather than **consolidation**, with providers focusing on specific niches and capabilities. This creates opportunities for both **specialized players** and **generalists** with unique value propositions.

**The search API landscape in 2026 is characterized by diversity, competition, and continuous innovation — making it an exciting time for developers and organizations looking to leverage search capabilities in their applications.**

---

*⬡ GROKSTER ⬡ SEARCH CATALOGUE ⬡ 2026-07-21 ⬡ 17 FREE/PAID TOOLS CATALOGUED ⬡ DEEP RESEARCH COMPLETE*
