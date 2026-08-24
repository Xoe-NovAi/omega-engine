# 🔱 DIRECT API RESEARCH PROTOCOL
**AP Token**: `AP-DIRECT-API-RESEARCH-PROTOCOL-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_direct_api_research ⬡ ACTIVE

**Date**: 2026-07-18
**Status**: MANDATORY PROTOCOL — All technical research MUST follow this protocol
**Authority**: Sovereign Mandate M23 (Failure Integrity) + Search Crisis Remediation

---

## 📋 EXECUTIVE SUMMARY

The Omega Engine's search pipeline (omega-hub wrappers) has a **95% failure rate** on technical queries. This protocol establishes the **Direct API First** methodology — bypassing broken MCP wrappers entirely and using official APIs directly.

**THIS IS NOT OPTIONAL.** Any research session that relies solely on `omega-hub_library_web_search` or `omega-hub_sovereign_search` for technical queries is in violation of Mandate 23.

---

## 🎯 PRIORITY TOOL CHAIN (MANDATORY ORDER)

### Tier 1: Official APIs (Highest Reliability)
| API | Use Case | Auth | Rate Limit |
|-----|----------|------|------------|
| **HuggingFace Hub API** | Model cards, config.json, metadata, tags | HF_TOKEN | 1000/hr |
| **OpenCode Zen API** | Model specs, provider info, benchmarks | Zen auth | N/A |
| **GitHub API** | Repo metadata, releases, issues, code search | GH_TOKEN | 5000/hr |
| **arXiv API** | Paper metadata, abstracts, PDFs | None | 1 req/3s |
| **Artificial Analysis API** | Benchmark scores, capability rankings | API key | TBD |
| **Papers With Code API** | Benchmark leaderboards, model cards | None | N/A |

### Tier 2: Direct Firecrawl (High Fidelity Extraction)
| Tool | Use Case | Config |
|------|----------|--------|
| `firecrawl_firecrawl_search` | Find URLs for specific topics | `limit=10`, `origin=web` |
| `firecrawl_firecrawl_scrape` | **Full content extraction** | `max_chars=0` (NO LIMIT), `timeout=60` |
| `firecrawl_firecrawl_map` | Discover site structure | `limit=50` |
| `firecrawl_firecrawl_crawl` | Deep site crawling | `max_depth=2`, `max_pages=100` |

### Tier 3: Direct SearXNG (Broad Discovery)
| Tool | Use Case | Config |
|------|----------|--------|
| `searxng_search` (direct) | Privacy-first metasearch | `categories=general,science,it` |
| `searxng_health` | Instance health check | — |

### Tier 4: webfetch (Known Good URLs)
| Tool | Use Case |
|------|----------|
| `webfetch` | Fetch complete content from verified URLs (HF, arXiv, GitHub, official docs) |

### Tier 5: omega-hub Wrappers (LAST RESORT ONLY)
| Tool | Use Case | Warning |
|------|----------|---------|
| `omega-hub_library_web_search` | Broad, non-technical queries only | 95% failure on technical |
| `omega-hub_sovereign_search` | Broad, non-technical queries only | 95% failure on technical |

---

## 🔬 RESEARCH SESSION TEMPLATE

Every research session MUST follow this structure:

```markdown
## Research Session: {TOPIC}
**Date**: 2026-07-XX
**Agent**: Researcher
**Protocol**: Direct API Research Protocol v1.0

### Tools Used (in order):
1. [ ] Official API: {which} — {success/failure} — {details}
2. [ ] Firecrawl: {search/scrape/map/crawl} — {success/failure} — {details}
3. [ ] SearXNG: {direct} — {success/failure} — {details}
4. [ ] webfetch: {URL} — {success/failure} — {details}
5. [ ] omega-hub: {library_web_search/sovereign_search} — {success/failure} — {details}

### Sources Consulted:
- [ ] Official API responses (with URLs/endpoints)
- [ ] Firecrawl scraped content (with source URLs)
- [ ] SearXNG results (with engine attribution)
- [ ] webfetch content (with source URLs)
- [ ] omega-hub results (with tier attribution)

### Findings:
{Structured findings with citations}

### Gaps Identified:
{What couldn't be found, why, next steps}

### Tool Effectiveness Log:
| Tool | Query | Success | Latency | Notes |
|------|-------|---------|---------|-------|
```

---

## 🛠️ API USAGE PATTERNS

### HuggingFace Hub API
```python
# Model card metadata
GET https://huggingface.co/api/models/{model_id}

# Model card content (markdown)
GET https://huggingface.co/api/models/{model_id}/tree/main

# config.json (architecture, params)
GET https://huggingface.co/api/models/{model_id}/resolve/main/config.json

# Search models
GET https://huggingface.co/api/models?search={query}&filter={tags}&sort=downloads
```

**Key Fields to Extract**:
- `modelId`, `tags`, `pipeline_tag`, `library_name`
- `config.json`: `architectures`, `hidden_size`, `num_hidden_layers`, `num_attention_heads`, `num_key_value_heads`, `vocab_size`, `max_position_embeddings`, `torch_dtype`
- Model card: `model-index`, `metrics`, `datasets`, `license`

### OpenCode Zen API
```python
# List all available models
GET https://opencode.ai/zen/v1/models

# Model details
GET https://opencode.ai/zen/v1/models/{model_id}
```

### GitHub API
```python
# Repository info
GET https://api.github.com/repos/{owner}/{repo}

# Releases (for version tracking)
GET https://api.github.com/repos/{owner}/{repo}/releases

# Code search (for pattern mining)
GET https://api.github.com/search/code?q={query}+repo:{owner}/{repo}
```

### arXiv API
```python
# Search papers
GET http://export.arxiv.org/api/query?search_query={query}&start=0&max_results=10

# Paper details
GET http://export.arxiv.org/api/query?id_list={arxiv_id}
```

### Firecrawl Direct (via `firecrawl_firecrawl_*` tools)
```python
# Search for URLs
firecrawl_search(query="model card best practices", limit=10, origin="web")

# Scrape FULL content (critical: max_chars=0 for no truncation)
firecrawl_scrape(url="https://huggingface.co/docs/hub/model-cards", max_chars=0, timeout=60)

# Map site structure
firecrawl_map(url="https://huggingface.co/docs/hub", limit=50)
```

---

## 🚫 FORBIDDEN PATTERNS

| Pattern | Violation | Correct Alternative |
|---------|-----------|---------------------|
| Using only `omega-hub_library_web_search` for technical queries | M23 Failure Integrity | Start with Official APIs → Firecrawl → SearXNG |
| Not logging which tool succeeded/failed | M18 Token Efficiency | Mandatory tool effectiveness log |
| Accepting "No results" from omega-hub without trying direct tools | M23 Failure Integrity | Exhaust Tier 1-4 before Tier 5 |
| Truncating Firecrawl content (default 3000-4000 chars) | Data Loss | **ALWAYS** use `max_chars=0` |
| Not verifying API responses against source | M17 Cognitive Integrity | Cross-reference with official source |

---

## 📊 VALIDATION CHECKLIST

Before concluding any research session:

- [ ] At least **2 independent sources** for each key claim (Skeptical Verifier two-source rule)
- [ ] All technical specifications traced to **official documentation** (not blog posts)
- [ ] Firecrawl scrapes used `max_chars=0` for complete content
- [ ] Tool effectiveness log completed
- [ ] Gaps explicitly documented with "COULD NOT VERIFY" tags
- [ ] Research session template filled out completely
- [ ] Findings written to `docs/research/R_{TOPIC}_{DATE}.md`

---

## 🔗 INTEGRATION WITH SOVEREIGN SEARCH SERVICE

The `SovereignSearchService` (SSP-V2) is being hardened with:
- Circuit breakers per tier
- Parallel execution with race semantics
- Full observability (tracing, metrics)
- Health-aware routing

**Until Phase 2 of Search Crisis Remediation is complete**, the Direct API Protocol is the **only** reliable research method.

Once hardened, the service will automatically:
1. Check T0 local cache
2. Route to healthy tiers based on `SearchRouter` intent
3. Execute tiers in parallel with circuit breaker protection
4. Return first successful result with full trace

**But the Direct API Protocol remains the gold standard for verification.**

---

## 📝 HANDOFF NOTES

**Next Actions**:
1. Create `docs/research/R_DIRECT_API_RESEARCH_PROTOCOL.md` (this document)
2. Implement Firecrawl direct tools in `src/omega/tools/firecrawl_direct.py` ✅ DONE
3. Implement SearXNG direct tools in `src/omega/tools/searxng_direct.py` ✅ DONE
4. Update `SovereignSearchService` with circuit breakers ✅ DONE
5. Update `HealthMonitor` for search provider health ✅ DONE
6. Test end-to-end with Model Registry research gaps

**Blocking**: SearXNG MCP port fix (8017→8018) in opencode.json ✅ DONE
**Blocking**: Firecrawl timeout/truncation fixes ✅ DONE

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_direct_api_research ⬡ PROTOCOL ESTABLISHED*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
