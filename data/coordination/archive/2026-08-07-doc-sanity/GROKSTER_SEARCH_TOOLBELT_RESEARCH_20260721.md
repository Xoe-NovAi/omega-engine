# 🔱 Grokster — Advanced Search Toolbelt Research
## Gap Analysis & Integration Candidates for Omega Engine's Sovereign Search Protocol
## 2026-07-21

---

## §1 Current Stack Assessment

### Existing Tiers (As-Is)

| Tier | Tool | Type | Cost | Gap |
|------|------|------|------|-----|
| **T0** | `.firecrawl/` cache | Local cache | Free | No TTL-based eviction policy |
| **T1** | `websearch`/`webfetch` | Built-in, free | Free | No independent index; opaque ranking |
| **T2** | SearXNG | Self-hosted metasearch | Infra only | Good, but no JS rendering, no multimodal |
| **T3** | `sovereign_search` (Exa) | Neural/semantic API | ~$5/1k queries | Semantic excellence but expensive at scale |
| **T4** | Firecrawl | Crawl + extract + search | Credits | Already in use as T4 |

### Key Gaps Identified

1. **No independent search index** — Everything depends on resellers or Big Tech indices
2. **No citation-shaped RAG search** — We extract content manually after search
3. **No synthesized answer API** — We call LLM separately to summarize
4. **No academic/research search** — Semantic Scholar, arXiv, OpenAlex all free but unconnected
5. **No code search** — No GitHub/GitLab semantic search
6. **No video search** — Can't search inside video content
7. **No real-time news monitoring** — No event/firehose search
8. **No self-hosted AI search UI** — No Perplexity-style interface
9. **No EU/multilingual premium sources** — European market gap
10. **No spatial/local search** — No structured local/geographic search

---

## §2 Tier-by-Tier Integration Candidates

### Tier 2.5 — Independent Index (Between SearXNG and Exa)

**Candidate: Brave Search API**
| Metric | Value |
|--------|-------|
| Index | **Independent** — 30B+ pages, own crawler, not a reseller |
| Latency | ~0.8s (fastest AI-native tier) |
| Pricing | $3-5/1k queries; 2,000 free/month |
| MCP | **Official MCP server** — drops into Claude Code/Cursor in 3 lines |
| Special | LLM Context API endpoint (Feb 2026) returns ready-to-quote context |
| Clients | Cohere, Mistral AI, AWS, Shopify, Snowflake |
| SOC 2 | Type II certified, GDPR compliant |

**Why integrate**: Brave is the *only* major option backed by a fully independent index. It has official MCP support, meaning it's the smoothest integration path into Claude Code. The LLM Context API is Brave's answer to Tavily — reshaped snippets ready for LLM consumption. Privacy-first, no tracking, zero data retention option on enterprise.

**Integration cost**: ~2h (MCP server is already built; wire into provider fabric as a new backend)

---

### Tier 3.5 — Citation-Shaped RAG Search (Between Exa and Firecrawl)

**Candidate: Tavily**
| Metric | Value |
|--------|-------|
| Type | AI-native, keyword search + extraction + citation formatting |
| Latency | ~2.1s (bundled extraction adds latency) |
| Pricing | $8/1k queries; 1,000 free/month |
| Integrations | **LangChain native**, LlamaIndex, CrewAI, MCP (community) |
| Special | `search_depth: advanced` does full-page content extraction |

**Why integrate**: Tavily is the default search tool in LangChain for a reason. One call returns search results *plus* cleaned full-page text *plus* citation-shaped payload. For RAG pipelines, this replaces: websearch → webfetch → chunk → embed → search. Tavily does it in one call. The `include_raw_content=True` parameter gives us the full page text ready for the LLM.

**Trade-off**: ~2.1s is the slowest in the top tier, but you save the token round-trip. Total system cost (search + extraction + LLM) is only ~14% more than the cheapest stack, but vastly simpler code.

**Integration cost**: ~3h (new provider backend + LangChain integration if desired)

---

### Budget Tier — Serper + Jina Reader

**Candidate: Serper.dev + Jina Reader**
| Metric | Value |
|--------|-------|
| Type | Google SERP wrapper + URL-to-Markdown extraction |
| Latency | ~0.5s (fastest in class) |
| Pricing | $0.30-1/1k queries; 2,500 free on signup |
| Extraction | Jina Reader (`r.jina.ai`) — free, prepend URL to get Markdown |
| **Total cost** | ~$0.50/1k queries — this is the cheapest production stack |

**Why integrate**: Serper is the cheapest real Google results in the category. Combined with Jina Reader (free URL-to-Markdown), this is the *cheapest stack* with zero extraction cost. Use for high-volume, low-criticality searches where cost trumps quality.

**Trade-off**: Snippets only from Serper, no built-in extraction. You pay LLM tokens to summarize. Jina Reader is free but adds latency.

**Integration cost**: ~2h

---

### Tier — Synthesized Answer API (Replace separate LLM call)

**Candidate: Perplexity Sonar API**
| Metric | Value |
|--------|-------|
| Type | Pre-synthesized answer with inline citations |
| Pricing | ~$1-5/1M input tokens (no per-query fee, includes live web search) |
| Latency | ~2-3s (synthesis takes time) |
| Models | Sonar, Sonar Pro, Sonar Reasoning Pro, Sonar Deep Research |
| Special | **No separate LLM call needed** — citations baked in |

**Why integrate**: Sonar skips the search-then-LLM dance entirely. It returns a pre-synthesized answer with citations in one call. For user-facing Q&A, this eliminates the entire RAG pipeline. The Deep Research model ($2/$8 per 1M tokens) mirrors the Perplexity Deep Research product.

**Trade-off**: You don't get raw results. You can't control ranking, filtering, or follow-up retrieval. You're committed to Perplexity's model. Use for consumer-facing QA; avoid for agent stacks that need raw passages.

**Integration cost**: ~2h (REST API, OpenAI SDK compatible)

---

### Academic/Research Search (Free Tier — High Value)

**Candidate: Semantic Scholar Academic Graph API**
| Metric | Value |
|--------|-------|
| Index | 200M+ papers across arXiv, bioRxiv, PubMed, journals, conferences |
| Pricing | **Free** (rate-limited; API key for higher limits) |
| Capabilities | Keyword search, citation traversal, recommendations, author lookup |
| Special | TLDR summaries, SPECTER embeddings, citation graphs, bulk search |
| Format | JSON, BibTeX, Markdown |

**Why integrate**: **Free access to 200M+ research papers.** This is a no-brainer. Semantic Scholar is the most comprehensive academic search API available, and it's free. The TLDR summaries (AI-generated paper summaries) are LLM-ready. The citation graph API lets us do forward/backward citation traversal — "find papers that cite this paper" and "find papers this paper cites." This turns our research capability from general web search into targeted academic discovery.

**Bonus: arXiv API + OpenAlex API** — both free, both complementary. arXiv covers preprints (2.2M+), OpenAlex covers the broader research graph.

**Integration cost**: ~4h (3 APIs → unified academic search backend)

---

### Code Search (Critical for Developer Workflow)

**Candidate: GitHub Search API + Sourcegraph**
| Metric | Value |
|--------|-------|
| GitHub API | Free (5,000 req/hr authenticated) |
| Sourcegraph | Self-hostable, semantic code search |
| Special | Code intelligence (tree-sitter, SCIP), dependency graphs |
| Use case | "Find all repos that use this pattern" "Show me similar code" |

**Why integrate**: We have no code search capability at all. The GitHub Search API gives us repo/code/issue search. For deeper semantic code search, Sourcegraph (self-hosted) indexes entire codebases for symbol-level search. Combined with GitHub MCP Server (official), this becomes agent-native.

**Integration cost**: ~3h (GitHub API wrapper + optional Sourcegraph)

---

### High-Recall Search & Monitoring

**Candidate: CatchAll (Newscatcher)**
| Metric | Value |
|--------|-------|
| Type | Recall-first web index — scans 50,000+ pages per job |
| Pricing | Usage-based, pay per validated record, free tier available |
| Latency | Lite mode: ~seconds; Base mode: ~15 min (async) |
| Special | **Monitors**: scheduled re-runs; **Watchlists**: entity scoring |
| Output | Structured event records with source citations + extracted entities |

**Why integrate**: CatchAll is structured for *enumeration* — "find everything relevant on this topic" — rather than ranking. For compliance monitoring, competitive intelligence, and supply-chain tracking, this replaces a custom crawler. The event-oriented output (entities, clusters, citations) drops directly into a research pipeline.

**Trade-off**: Not a SERP replacement. Deep mode is async (~15 min). No MCP server yet.

---

### Video Search

**Candidate: Twelve Labs**
| Metric | Value |
|--------|-------|
| Type | Video-native foundation models (Marengo, Pegasus) |
| Capabilities | Natural language video search, scene detection, summarization |
| Special | Understands actions, events, and context across vision, audio, text |
| Indexing | ~60x real-time speed (index 1h video in 1 min) |
| Pricing | Cloud API; no self-hosting |

**Why integrate**: For any workflow involving video content (YouTube research, archival footage, training materials), Twelve Labs is the SOTA video understanding platform. Search inside videos using natural language. No manual tagging needed.

**Alternative**: **Mixpeek** — multimodal (video, image, audio, docs) in one API, self-hosted option available.

---

## §3 Integration Priority Matrix

| Priority | Tool | Cost Impact | Effort | Why Now |
|----------|------|-------------|--------|---------|
| **P0** | Brave Search API | Low ($3-5/1k) | 2h | Independent index + official MCP = biggest gap fill for lowest cost |
| **P1** | Semantic Scholar | Free | 4h | Free access to 200M+ papers; research capability multiplier |
| **P1** | Serper + Jina Reader | Very low ($0.50/1k) | 2h | Cheapest production search stack; budget tier |
| **P2** | Tavily | Medium ($8/1k) | 3h | Citation-shaped RAG; LangChain native |
| **P2** | Perplexity Sonar | Medium (per-token) | 2h | Eliminates separate LLM call for answer synthesis |
| **P3** | CatchAll | Usage-based | 4h | High-recall monitoring; compliance/competitive intel |
| **P3** | Twelve Labs/Mixpeek | Medium-high | 6h | Video search — specialized but high-value |
| **P4** | Sourcegraph/GitHub Code Search | Free-Low | 3h | Developer workflow enhancement |

---

## §4 Strategic Recommendations

### Immediate (0-2 sessions)
1. **Integrate Brave Search API as T2.5** — Independent index, official MCP, privacy-first. Biggest gap fill for lowest cost. Use the existing MCP server for instant integration with Claude Code.
2. **Add Semantic Scholar as dedicated research tier** — Free. 200M+ papers. TLDR summaries are LLM-ready. This turns our research pipeline from general web search into targeted academic discovery.

### Short-term (3-5 sessions)
3. **Add Serper + Jina Reader as Budget Tier** — Cheapest production stack at $0.50/1k queries. Use for high-volume, low-criticality searches. Pair with SearXNG fallback for sovereignty.
4. **Evaluate Tavily for citation-shaped RAG** — If we want to simplify our RAG pipeline from 5 steps to 1 call, this is the move. Default search tool in LangChain for a reason.

### Medium-term (6-10 sessions)
5. **Perplexity Sonar for user-facing Q&A** — Eliminates the separate LLM call for answer synthesis. Use for root access queries where raw results aren't needed.
6. **CatchAll for monitoring** — If we need continuous web monitoring for compliance, competitive intel, or breaking news tracking, this is purpose-built for it.

### Future (Post-C infrastructure)
7. **Video search (Twelve Labs/Mixpeek)** — Once the foundation is stable, video content search becomes a differentiator.
8. **Code search (Sourcegraph/GitHub)** — For the developer-facing workflows in the Community Tool phase.

---

## §5 Proposed L3 Principle

**L3-SearchTierSpecialization**: A sovereign search architecture is not defined by the most powerful single tool but by the smallest set of specialized tiers that cover the full recall-relevance-cost surface. No single search API wins on all dimensions: independent-index for sovereignty, neural for semantics, SERP for cost, academic for depth, synthesized for speed. The architecture that integrates each at its strength and falls through them gracefully defines the search frontier. Specialization is not fragmentation when the fallback chain is designed from the start.

---

*⬡ GROKSTER ⬡ SEARCH TOOLBELT RESEARCH ⬡ 2026-07-21*
