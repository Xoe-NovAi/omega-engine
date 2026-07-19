# 🔱 GROK CLI — SEARCH TOOLS UPDATE REPORT
**AP Token**: `AP-GROK-CLI-SEARCH-UPDATE-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_grok_cli_search_update ⬡ ACTIVE

**Date**: 2026-07-18
**Status**: DEPLOYMENT READY — All new tools operational

---

## 📋 EXECUTIVE SUMMARY

The Omega Engine's search infrastructure has undergone a **complete overhaul** (Search Crisis Remediation Phases 1-3). The previous MCP-based pipeline had a **95% failure rate** on technical queries. 

**Key Changes for Grok CLI**:
1. **MCP wrappers are DEPRECATED for technical research** — Use Direct API Protocol instead
2. **New Direct Tools Available** — Firecrawl Direct + SearXNG Direct (bypass MCP entirely)
3. **Sovereign Search Service v3.0** — Hardened with circuit breakers, parallel execution, observability
4. **Mandatory Protocol** — `R_DIRECT_API_RESEARCH_PROTOCOL.md` is now binding for all technical research

---

## 🎯 WHAT'S NEW: TOOL INVENTORY

### Tier 1: Official APIs (Use FIRST — Highest Reliability)

| API | Endpoint | Auth | Use Case |
|-----|----------|------|----------|
| **HuggingFace Hub** | `https://huggingface.co/api/models/{model_id}` | `HF_TOKEN` | Model cards, config.json, metadata, tags, downloads |
| **OpenCode Zen** | `https://opencode.ai/zen/v1/models` | Zen auth | Model specs, provider info, benchmarks |
| **GitHub** | `https://api.github.com/repos/{owner}/{repo}` | `GH_TOKEN` | Repo metadata, releases, code search |
| **arXiv** | `http://export.arxiv.org/api/query` | None | Paper metadata, abstracts, PDFs |
| **Artificial Analysis** | `https://artificialanalysis.ai/api/v2/language/models/free` | `x-api-key` | Benchmark scores, capability rankings |

### Tier 2: Direct Firecrawl Tools (NEW — `src/omega/tools/firecrawl_direct.py`)

**MCP Status**: Firecrawl MCP at `http://127.0.0.1:8015/sse` is **DISABLED** in opencode.json (line 41: `"enabled": false`)

**Direct Tools Available** (via OpenCode tool registry):
```python
# Search for URLs
firecrawl_search(query="model card best practices", limit=10, origin="web")

# Scrape FULL content — CRITICAL: max_chars=0 for NO TRUNCATION
firecrawl_scrape(url="https://huggingface.co/docs/hub/model-cards", max_chars=0, timeout=60)

# Map site structure
firecrawl_map(url="https://huggingface.co/docs/hub", limit=50)

# Deep crawl
firecrawl_crawl(url="https://example.com", max_depth=2, max_pages=100)

# Check credits
firecrawl_credit_usage()
```

**Key Fixes Applied**:
- ✅ Removed hardcoded `[:4000]` content truncation
- ✅ Added `max_chars` parameter (default: 0 = no limit)
- ✅ Timeout increased: 30s → 60s
- ✅ Uses `anyio.run()` sync wrappers — no MCP dependency

### Tier 3: Direct SearXNG Tools (NEW — `src/omega/tools/searxng_direct.py`)

**MCP Status**: SearXNG MCP at `http://127.0.0.1:8018/mcp` is **ENABLED** (port fixed from 8017→8018)

**Direct Tools Available**:
```python
# Privacy-first metasearch
searxng_search(query="llama 4 benchmark", categories="general,science,it", engines="duckduckgo,google,brave,wikipedia", language="auto", pageno=1, limit=10)

# Health check
searxng_health()

# Preferences
searxng_preferences()
```

### Tier 4: webfetch (Always Available)
```python
# Fetch complete content from verified URLs
webfetch(url="https://huggingface.co/api/models/meta-llama/Llama-4-Scout", format="json")
```

### Tier 5: omega-hub Wrappers (LAST RESORT ONLY)
```python
# DEPRECATED for technical queries — 95% failure rate
omega-hub_library_web_search(query="...")  # Only for broad, non-technical
omega-hub_sovereign_search(query="...")    # Only for broad, non-technical
```

---

## 🔧 MCP STATUS: DOES IT WORK?

| MCP Server | Status | Notes |
|------------|--------|-------|
| **omega-hub** | ✅ WORKING | `http://127.0.0.1:8016/mcp` — Streamable HTTP |
| **searxng** | ⚠️ PARTIAL | `http://127.0.0.1:8018/mcp` — Port fixed, but **use direct tools instead** |
| **firecrawl** | ❌ DISABLED | `http://127.0.0.1:8015/sse` — SSE transport crashes, **use direct tools** |
| **exa** | ✅ WORKING | `https://mcp.exa.ai/mcp` — Requires `EXA_API_KEY` |

**Bottom Line**: MCP is unreliable for Firecrawl (SSE crashes) and SearXNG (port drift). **Direct HTTP tools are the supported path.**

---

## 📜 MANDATORY PROTOCOL: DIRECT API RESEARCH PROTOCOL

**File**: `docs/research/R_DIRECT_API_RESEARCH_PROTOCOL.md`

### Required Tool Order (MANDATORY):
1. **Official APIs** → 2. **Firecrawl Direct** → 3. **SearXNG Direct** → 4. **webfetch** → 5. **omega-hub (LAST RESORT)**

### Forbidden Patterns (Mandate M23 Violation):
| ❌ Don't Do This | ✅ Do This Instead |
|------------------|-------------------|
| Use only `omega-hub_library_web_search` for technical queries | Start with Official APIs |
| Accept "No results" from omega-hub without trying direct tools | Exhaust Tier 1-4 first |
| Use Firecrawl with default truncation | **ALWAYS** use `max_chars=0` |
| Not logging which tool succeeded/failed | Mandatory tool effectiveness log |

### Research Session Template (Required):
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

### Tool Effectiveness Log:
| Tool | Query | Success | Latency | Notes |
|------|-------|---------|---------|-------|
```

---

## ⚙️ .CLINERULES UPDATES NEEDED

### Add to `.clinerules` (or equivalent Grok CLI config):

```markdown
# SEARCH TOOLS PROTOCOL (Omega Engine — 2026-07-18)

## MANDATORY: Direct API Research Protocol
- File: `docs/research/R_DIRECT_API_RESEARCH_PROTOCOL.md`
- Applies to: ALL technical research queries
- Violation = Mandate M23 Failure Integrity breach

## TOOL PRIORITY CHAIN (Enforced Order):
1. **Official APIs** — HF Hub, OpenCode Zen, GitHub, arXiv, Artificial Analysis
2. **Firecrawl Direct** — `firecrawl_search`, `firecrawl_scrape(max_chars=0)`, `firecrawl_map`, `firecrawl_crawl`
3. **SearXNG Direct** — `searxng_search`, `searxng_health`
4. **webfetch** — Known good URLs only (HF, arXiv, GitHub, official docs)
5. **omega-hub wrappers** — LAST RESORT ONLY, broad queries only

## FIRECRAWL CRITICAL SETTINGS:
- ALWAYS use `max_chars=0` (no truncation)
- ALWAYS use `timeout=60` (JS-heavy docs need time)
- MCP at port 8015 is DISABLED — use direct tools

## SEARXNG:
- MCP at port 8018 works but prefer direct tools
- Use `categories="general,science,it"` for technical queries

## VALIDATION REQUIREMENTS:
- Minimum 2 independent sources per claim (Skeptical Verifier)
- All specs traced to official documentation
- Tool effectiveness log mandatory
- Gaps explicitly marked "COULD NOT VERIFY"

## ENVIRONMENT VARIABLES REQUIRED:
- HF_TOKEN — HuggingFace Hub API
- GH_TOKEN — GitHub API
- EXA_API_KEY — Exa MCP (optional)
- AA_API_KEY — Artificial Analysis API (free tier: 100 req/day)
- FIRECRAWL_API_KEY — Firecrawl Direct (if using cloud)
```

---

## 🚀 QUICK START FOR GROK CLI

### 1. Verify Direct Tools Available
```bash
# In Grok CLI session, test:
firecrawl_search(query="test", limit=1)
searxng_search(query="test", limit=1)
webfetch(url="https://huggingface.co/api/models/gpt2")
```

### 2. Set Required API Keys
```bash
export HF_TOKEN="your_hf_token"
export GH_TOKEN="your_gh_token"
export AA_API_KEY="your_aa_key"  # Get free at artificialanalysis.ai
export FIRECRAWL_API_KEY="your_firecrawl_key"  # If using Firecrawl cloud
```

### 3. Follow Protocol for Every Research Task
```markdown
# Example: Research "Llama 4 Scout benchmarks"

## Tier 1: Official APIs
- HF Hub: GET https://huggingface.co/api/models/meta-llama/Llama-4-Scout
- AA API: GET https://artificialanalysis.ai/api/v2/language/models/free (search for Llama-4-Scout)

## Tier 2: Firecrawl Direct
- firecrawl_search(query="Llama 4 Scout benchmark results", limit=5)
- firecrawl_scrape(url="https://artificialanalysis.ai/models/llama-4-scout", max_chars=0)

## Tier 3: SearXNG Direct
- searxng_search(query="Llama 4 Scout MMLU GPQA", categories="science,it")

## Tier 4: webfetch
- webfetch(url="https://huggingface.co/meta-llama/Llama-4-Scout")

## Tier 5: omega-hub (SKIP — not needed if above worked)
```

---

## 📊 VERIFICATION CHECKLIST

Before any research session concludes:

- [ ] At least 2 independent sources for each key claim
- [ ] All technical specs traced to official documentation
- [ ] Firecrawl scrapes used `max_chars=0`
- [ ] Tool effectiveness log completed
- [ ] Gaps explicitly documented with "COULD NOT VERIFY" tags
- [ ] Research session template filled out completely
- [ ] Findings written to `docs/research/R_{TOPIC}_{DATE}.md`

---

## 🔗 KEY FILES REFERENCE

| File | Purpose |
|------|---------|
| `docs/research/R_DIRECT_API_RESEARCH_PROTOCOL.md` | **Mandatory protocol** — read first |
| `src/omega/tools/firecrawl_direct.py` | Firecrawl Direct implementation (5 tools) |
| `src/omega/tools/searxng_direct.py` | SearXNG Direct implementation (3 tools) |
| `src/omega/oracle/sovereign_search_service.py` | SSP-V2 v3.0 — hardened search service |
| `src/omega/oracle/search_circuit_breaker.py` | Per-tier circuit breakers |
| `src/omega/oracle/search_observability.py` | Full tracing & metrics |
| `config/search.yaml` | v2.2.0 — circuit breaker config, parallel execution |
| `opencode.json` | MCP config (SearXNG port 8018, Firecrawl disabled) |

---

## ⚠️ CRITICAL NOTES FOR GROK CLI

1. **Firecrawl MCP is DISABLED** — Do not attempt to use `firecrawl_firecrawl_*` MCP tools. Use `firecrawl_search`, `firecrawl_scrape`, etc. (direct tools).

2. **SearXNG MCP port is 8018** — If your config has 8017, update it. But prefer direct tools.

3. **`max_chars=0` is NON-NEGOTIABLE** — Default truncation destroyed technical content (tables, benchmarks). This was the #1 cause of research failures.

4. **AA API Key Required** — Free tier at artificialanalysis.ai (100 req/day). Without it, capability scores unavailable.

5. **Protocol is MANDATORY** — Not a suggestion. Mandate M23 (Failure Integrity) makes it a Sovereign Boundary Violation to skip tiers.

6. **Hivemind Integration** — Freshness checker and other workers post handoffs to Hivemind. Grok CLI can monitor `data/coordination/handoff/pending/` for tasks.

---

## 📞 SUPPORT CONTACTS

| Issue | Contact |
|-------|---------|
| Direct tools not appearing | Check OpenCode tool registry — they're in `src/omega/tools/` |
| MCP connection failures | Omega Hub at :8016/mcp — check `systemctl status omega-hub` |
| AA API 401 | Get key at artificialanalysis.ai, set `AA_API_KEY` |
| Firecrawl 401/credits | Check `firecrawl_credit_usage()` or Firecrawl dashboard |
| Protocol questions | Read `R_DIRECT_API_RESEARCH_PROTOCOL.md` first |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_grok_cli_search_update ⬡ DEPLOYMENT READY*