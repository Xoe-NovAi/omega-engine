# 🔱 Omega Engine — Search Tool Protocol & Agent Docket
# ⬡ OMEGA ⬡ researcher ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_search_protocol_v1
**AP Token**: `AP-SEARCH-PROTOCOL-v1.0.0`
**Date**: 2026-06-10
**Status**: FINAL — Approved by Kali (2026-06-12)
**Owners**: researcher / roc_racoon
**Overseer**: kali

---

## §0 Executive Summary

This document establishes the **Sovereign Search Protocol** — a mandatory multi-tier execution framework for all web research operations across the Omega Engine agent fleet. It replaces ad-hoc tool selection with a systematic, cost-aware, failure-resilient pipeline.

**Three Critical System States Discovered During Audit**:
1. **Firecrawl Credits ACTIVE (987 remaining)** — Credits restored. Ready for execution.
2. **Exa API ACTIVE (200 OK)** — `${EXA_API_KEY}` environment variable is set and valid.
3. **No centralized error-handling matrix** — Agents have no standard response to 401/402/429/500 errors from search tools.

**Five-Tier Protocol Defined**:
| Tier | Tool | Cost | Status |
|------|------|------|--------|
| 0 | Local Cache (`.firecrawl/` + MemoryStore) | Free | ✅ Functional |
| 1 | Built-in `websearch` | Free | ✅ Functional |
| 2 | SearXNG (Sovereign Metasearch) | Free | ✅ Active (Self-hosted) |
| 3 | Firecrawl / Hub (Deep Extraction / Gnosis) | Credits/Free | ✅ Active (987/1000) / Functional |
| 4 | Exa (Neural Search) | API Key | ✅ Functional |

---

## §1 Audit Findings — Current Tool Landscape

### 1.1 Firecrawl Fleet (28 skills in `~/.agents/skills/firecrawl-*`)

| Skill | Tool | Status | Notes |
|-------|------|--------|-------|
| `firecrawl_scrape` | `firecrawl_firecrawl_scrape` | ✅ Functional | Single-page extraction. Credits = 987 |
| `firecrawl_search` | `firecrawl_firecrawl_search` | ✅ Functional | Web search with optional scraping |
| `firecrawl_crawl` | `firecrawl_firecrawl_crawl` | ✅ Functional | Bulk site extraction |
| `firecrawl_agent` | `firecrawl_firecrawl_agent` | ✅ Functional | AI-powered structured extraction |
| `firecrawl_map` | `firecrawl_firecrawl_map` | ✅ Functional | URL discovery (uses minimal credits) |
| `firecrawl_interact` | `firecrawl_firecrawl_interact` | ✅ Functional | Browser interaction (scrape gated) |
| `firecrawl_parse` | `firecrawl_firecrawl_parse` | ✅ Functional | Local file parsing (no credits) |
| 21 other workflow skills | N/A | ❌ Gated | All depend on core tools |

**Credit Status**: Firecrawl CLI v1.18.0 installed, authenticated. 164 sites cached in `.firecrawl/`. Credits are active (987 remaining). Can use CLI directly via `bash` as MCP fallback (per Sovereign Web-Eye Mandate).

**Credit Reset**: Next cycle begins **June 19, 2026**.

### 1.2 Exa Search (`~/.agents/skills/sovereign-search/`)

| Tool | Endpoint | Status | Notes |
|------|----------|--------|-------|
| `exa_web_search_exa` | `https://mcp.exa.ai/mcp` | ✅ Functional | API key is valid |
| `exa_web_fetch_exa` | `https://mcp.exa.ai/mcp` | ✅ Functional | Same key dependency |

**Config** (opencode.json):
```json
"exa": {
  "type": "remote",
  "url": "https://mcp.exa.ai/mcp?tools=web_search_exa,web_fetch_exa",
  "headers": {
    "x-api-key": "${EXA_API_KEY}"
  },
  "enabled": true
}
```

**Root Cause**: `${EXA_API_KEY}` environment variable is set and valid. The sovereign-search skill is fully functional.

### 1.3 Sovereign Infrastructure
All external search dependencies (Tavily, Jina, Brave, Serper) have been purged in favor of self-hosted or neural-first sovereign alternatives.

### 1.4 Working Tools

| Tool | Type | Reliability | Notes |
|------|------|-------------|-------|
| `websearch` | Built-in | ✅ Always works | Zero-config, no API key, general purpose |
| `webfetch` | Built-in | ✅ Always works | Can read individual URLs |
| Omega Hub Research | MCP Hub | ✅ Functional | 4 depths (1-4), offline library search |
| Firecrawl CLI (bash) | CLI | ⚠️ Needs credits | `bash(firecrawl ...)` fallback works |

---

## §2 The 5-Tier Sovereign Search Protocol

### Protocol Rules
- **Always start at Tier 0**. Check local cache first.
- **Escalate sequentially**. Only move to a higher tier when all lower tiers are exhausted or inappropriate.
- **Never skip tiers**. Tier 2 (SearXNG) is NOT a replacement for Tier 1 (websearch) for simple queries.
- **Log every failure**. If a tool returns an error, document it and move to next tier.
- **The Sovereign Verification Mandate**: Search snippets (T1/T2) are indicators, NOT evidence. For any critical finding, a "Sovereign Verification Step" is mandatory: you MUST extract the full page using `firecrawl_scrape` or `webfetch`. Relying on truncated snippets is a violation of the Temple-Grade standard.
- **Truncation Awareness**: Be alert for truncated results. If a scraped page seems incomplete or ends abruptly, try an alternate tool (e.g., switch from `firecrawl_scrape` to `webfetch`).
- **The Sovereign Fallback Hierarchy**: If a result is flagged as truncated via a Truncation Audit, escalate as follows:
    `webfetch (T1)` $\rightarrow$ `firecrawl_scrape (T3)` $\rightarrow$ `firecrawl_actions (T3+ / Interactive)` $\rightarrow$ `Sovereign Playwright (Local)`

```
User Query

```
User Query

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ Tier 0: LOCAL CACHE CHECK                           │
│ • .firecrawl/ directory (164 cached sites)          │
│ • MemoryStore hybrid search                         │
│                                                      │
│ If cached hit → return result                        │
│ If miss → escalate to Tier 1                         │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ Tier 1: BUILT-IN WEBSEARCH                          │
│ • websearch(query) - general purpose                 │
│ • webfetch(url) - read specific page                 │
│                                                      │
│ Cost: Free. Always works. No API key needed.          │
│ Result: Snippets + URLs                              │
│                                                      │
│ If sufficient → return and cite                      │
│ If need deep extraction → escalate to Tier 2          │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ Tier 2: SEARXNG (SOVEREIGN METASEARCH)              │
│ • curl 'http://localhost:8018/sse'                  │
│ • Provides aggregated results from multiple engines   │
│                                                      │
│ Cost: Free. Self-hosted.                              │
│ Result: Cleaned, privacy-preserving search results    │
│                                                      │
│ If sufficient → return and cite                      │
│ If need deep extraction → escalate to Tier 3          │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ Tier 3: FIRECRAWL / HUB (DEEP EXTRACTION / GNOSIS)  │
│ • firecrawl_scrape(url) - full page extraction       │
│ • library_search(query) - offline library            │
│                                                      │
│ Cost: Credits (Firecrawl) / Free (Hub)               │
│ ✅ ACTIVE (987 credits)                               │
│                                                      │
│ If 402 → log and escalate to Tier 4                  │
│ If success → cache to .firecrawl/ for Tier 0 reuse   │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ Tier 4: EXA (NEURAL SEARCH)                          │
│ • exa_web_search_exa(query) - neural/web search      │
│ • exa_web_fetch_exa(url) - full page fetch           │
│                                                      │
│ Cost: API Key. ✅ Functional.                        │
│ ✅ EXA IS ACTIVE - Tier 4 = reachable                │
│                                                      │
│ If 401 → log and escalate to Kali for resolution     │
└─────────────────────────────────────────────────────┘
```

---

## §3 Error Handling Matrix

Every agent MUST follow this matrix when a search tool returns an error.

| Error Code | Meaning | Likely Tool | Immediate Action | Escalation Path |
|------------|---------|-------------|------------------|-----------------|
| **401** | Unauthorized / Invalid API Key | Exa | Fall back to Tier 1 (websearch). Log to Hivemind. | Kali to fix API key |
| **402** | Payment Required / Credits Exhausted | Firecrawl (all 28 skills) | Fall back to Tier 1 (websearch). Use cached `.firecrawl/` data. | Wait until Jun 19 or upgrade plan |
| **403** | Forbidden | Any | Fall back to Tier 1. Check if IP-blocked. | Kali escalation |
| **404** | Not Found | webfetch, Exa fetch | Verify URL. Try alternate URL. | User report |
| **429** | Rate Limited | Any | Execute exponential backoff: wait 5s → 15s → 30s → 60s. If all fail, fall back. | Track in observability |
| **500** | Server Error | Any | Retry once after 2s timeout. On second failure, fall back to Tier 1. | Log trace in Hivemind |
| **502/503** | Bad Gateway / Service Unavailable | Firecrawl/MCP | Wait 10s, retry once. If still failing, fall back. | Monitor status page |
| **Timeout** | Tool did not respond within limit | Any MCP tool | Set timeout=30s default. On timeout, retry with timeout=60s. On second timeout, fall back. | Log to Hivemind |
| **Connection Refused** | MCP server not running | Omega Hub, Exa MCP | Check `firecrawl --status` / `systemctl --user status omega-hub`. Try restart. | Kali escalation |

### Mandatory Error Logging Format

When ANY search tool fails, the agent MUST log to Hivemind:
```
[SEARCH-ERROR] tool={tool_name} error={error_code} tier={0-4} fallback={fallback_tool} timestamp={ISO8601}
```

---

## §4 The Researcher + Roc Racoon Docket

This docket defines the parallel execution plan for the Researcher-Roc partnership.

### 🔴 4.1 Immediate — Fix Critical Search Gaps (Sprint Priority)

| ID | Task | Owner | Effort | Dependencies |
|----|------|-------|--------|-------------|
| **SR-1** | **Firecrawl Credit Protocol**: Document credit usage patterns, caching strategy, and CLI fallback patterns. Create `make firecrawl-status` target. | Researcher | 2h | None |
| **SR-2** | **Exa Key Verification**: Roc audits `.env` files, env vars, and opencode.json to verify why Exa is now working and ensure stability. | Roc Racoon | 1h | None |
| **SR-3** | **`.firecrawl/` Cache Analysis**: Catalog all 164 cached sites. Determine which are reusable and which are stale. Build a quick-reference for Tier 0 hits. | Roc Racoon | 3h | SR-2 |
| **SR-4** | **Search Protocol CI Gate**: Add `make verify-search-tools` target that checks Firecrawl status, Exa connectivity, and reports results summary. | Researcher w/ Roc review | 2h | SR-1, SR-2 |

### 🟡 4.2 Medium — Refine & Harden

| ID | Task | Owner | Effort | Dependencies |
|----|------|-------|--------|-------------|
| **SR-5** | **Embed Protocol into sovereign-search skill**: Rewrite `sovereign-search/SKILL.md` with the 5-tier protocol, error matrix, and the new caching patterns. | Researcher | 2h | SR-1, SR-4 |
| **SR-6** | **Agent audit for search compliance**: Update all 14 agent files with the standard search protocol instructions. Ensure every agent's instructions reference the protocol. | Roc Racoon | 3h | SR-5 |
| **SR-7** | **Hub research tool hardening**: Audit Omega Hub's research tools for search completeness (library_discovery_research, library_search). Add any missing error handling. | Roc Racoon | 2h | None |

### 🟢 4.3 Strategic — Long-Term Evolution

| ID | Task | Owner | Effort | Notes |
|----|------|-------|--------|-------|
| **SR-8** | **Exa alternative evaluation**: If Exa key cannot be recovered, evaluate Tavily vs Serper vs Jina as replacement. Test with free tiers. | Researcher | 4h | After SR-2 |
| **SR-9** | **AI-powered research pipeline**: Integrate the 5-tier protocol with Jem-2.0 discovery pipeline so L1/L2/L3 research knows which tier to use for each phase. | Researcher + Roc | 6h | Blocked on SR-5 |
| **SR-10** | **Credit budget automation**: Script to track Firecrawl credit usage per-agent, per-session, with alerts when approaching 80% exhaustion. | Roc Racoon | 4h | Future sprint |

---

## §5 Implementation Guide for Agents

### 5.1 Quick Reference: When to Use What

| Situation | Tool | Tier | Why |
|-----------|------|------|-----|
| "What is the latest version of X?" | `websearch` | T1 | Fast, free, perfect for factual lookups |
| "Find the documentation for Y" | `websearch` → `webfetch` | T1 | Search + read specific page |
| "Sovereign, aggregated search" | SearXNG | T2 | Metasearch without tracking |
| "Get the full content of this page" | `firecrawl_scrape(url)` | T3 | Full markdown extraction |
| (Firecrawl 402) "Get the full content" | `webfetch(url)` | T1 fallback | May miss JS content, but works |
| "Crawl all docs for this tool" | `firecrawl_crawl(url)` | T3 | Multi-page extraction |
| "Research this academic topic" | `websearch` first → Local Library | T1+T0 | Library may have indexed papers |
| "I have a PDF/DOCX on my machine" | `firecrawl_parse(path)` | T3 | Local file parsing (no credits) |
| "Compare prices across 10 sites" | `firecrawl_agent(prompt)` | T3 | AI-powered extraction |
| "Is this page different from last week?" | `firecrawl_monitor_create(url)` | T3 | Change tracking |
| "Find similar research to this paper" | Exa `web_search_exa(similar=...)` | T4 | Exa's neural search (Sovereign) |

### 5.2 The "No Lazy Response" Mandate

Per Temple-Grade standard: **agents MUST perform at least one active tool call** for any query requiring factual, technical, or recent information. Relying solely on internal parametric weights for research queries is a violation.

**Sovereign Verification Requirement**:
1.  **No Snippet-Only Research**: Using search result descriptions as the sole source for a finding is forbidden.
2.  **Full-Page Extraction**: Every critical finding must be verified by reading the full source page.
3.  **Verification Evidence**: Citations must include the full URL and a confirmation that the full page was analyzed (e.g., "Verified via full-page scrape of [URL]").
4.  **Truncation Check**: If the extracted content appears truncated, the agent must attempt a second extraction method (e.g., `webfetch` as fallback for `firecrawl_scrape`) before declaring the source unavailable.

**Truncation Audit Criteria**:
A result is flagged as `TRUNCATED` if:
-   It contains sentinel strings like `"Loading..."`, `"Click to expand"`, or `"Read more"`.
-   The markdown ends abruptly (mid-sentence or mid-section) without a proper footer.
-   The content length is an anomaly compared to the expected page size.

If all tools fail:
1. Try `websearch` (Tier 1) — it almost never fails
2. If `websearch` also fails, log the failure chain to Hivemind
3. Then and only then, respond with parametric knowledge, clearly labeled as "based on training data, not verified from live sources"

### 5.3 Caching Protocol (Mandatory from Sprint 2026-06-10)

```
BEFORE any Tier 2+ tool call:
  1. Check .firecrawl/ for existing data on the URL/query
  2. Naming convention: .firecrawl/{site}-{path}.md
  3. grep/head the cached file — don't read it whole

AFTER any Tier 2+ tool call:
  1. Save result to .firecrawl/ with proper naming
  2. If it's a manual ingestion, save to data/kb/manuals/<tool>/
```

---

## §5.4 Sovereign Key Vault Integration (D-kal-169)

To secure API credentials and decouple the engine from platform-specific config files (like `opencode.json`), the **Sovereign Key Vault** was implemented at `src/omega/vault/`.

*   **Encryption**: AES-256-GCM authenticated encryption with a random 12-byte nonce.
*   **Storage**: Encrypted payload saved at `data/vault/keys.json.enc`.
*   **Resolution**: Providers resolve keys dynamically via `KeyVault().resolve("exa"/"firecrawl")` with a graceful fallback to environment variables (`os.getenv()`).
*   **MCP Hub**: `state.py` initializes search keys by querying the `KeyVault` singleton, eliminating raw file parses of `opencode.json`.

## §5.5 Search System Bug Fixes (Sprint C Unification)

During the June 23, 2026 Sovereign Audit, five critical bugs in the search infrastructure were identified and remediated:

1.  **Missing `os` Import**: `search_providers.py` was calling `os.environ.get()` inside `_resolve_from_vault()` without importing `os`, causing runtime `NameError` crashes on vault fallback. **Fixed** by adding `import os`.
2.  **AttributeError in Iterative Research**: `iterative_research.py` was calling `self.searcher.search(...)` instead of the correct `self.searcher.search_knowledge(...)` method on `SovereignSearcher`, causing immediate runtime crashes. **Fixed** by correcting the method call and parameter order.
3.  **KeyVault Singleton Initialization Bug**: `KeyVault.__init__` was setting `self._initialized = True` before running initialization code. If initialization failed, subsequent calls would return a broken, uninitialized vault. **Fixed** by moving the initialization flag to the end of `__init__()`.
4.  **Exa MCP Config Merge Conflict**: Three separate files defined Exa with conflicting transport protocols (`http` vs `streamable-http`). **Fixed** by consolidating to a single project-level `opencode.json` with `streamable-http` and removing stale entries from `config/mcp_servers.json`.
5.  **Broken T1 Websearch Stub**: `sovereign_search_service.py` had a dead `None` placeholder for Tier 1 websearch. **Fixed** by wiring a direct httpx provider.

---

## §6 Contrarian Views & Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Firecrawl credits never reset (plan change) | Low | High | Upgrade to self-hosted Firecrawl or migrate to pure websearch |
| Exa API key unrecoverable | Medium | Medium | Evaluate sovereign alternatives |
| Agent forgets protocol under pressure | High | Medium | Embed protocol in every agent's instructions file |
| `.firecrawl/` cache grows unbounded | High | Low | Add monthly cleanup to `make hygiene` |
| SearXNG instance offline | Low | Medium | `systemctl --user restart searxng` |

---

## §7 Open Questions

1. **Firecrawl plan upgrade**: Should we upgrade from the free 1,000-credit plan to a paid tier? Cost-benefit analysis needed.
2. **Exa key recovery**: Is the key in `.env`? Has it expired? Can we regenerate it from the Exa dashboard?
3. **Self-hosted Firecrawl**: Firecrawl offers a self-hosted option (open-source). Would this eliminate credit concerns entirely?
4. **SearXNG Optimization**: Should we add specific engine filters to SearXNG to prioritize technical/academic sources?

---

## §8 Sources

| Source | Tool | Type | Quality |
|--------|------|------|---------|
| `opencode.json` (line 42-92) | MCP Config | Primary | ⭐⭐⭐⭐⭐ |
| `~/.agents/skills/firecrawl/SKILL.md` | Firecrawl Skill | Primary | ⭐⭐⭐⭐⭐ |
| `~/.agents/skills/firecrawl-*/SKILL.md` | 28 Firecrawl Skills | Primary | ⭐⭐⭐⭐⭐ |
| `.opencode/skills/sovereign-search/SKILL.md` | Exa/Tavily/Serper | Primary | ⭐⭐⭐⭐⭐ |
| `firecrawl --status` (CLI) | Live CLI Status | Primary | ⭐⭐⭐⭐⭐ |
| `firecrawl credit-usage` (CLI) | Credit Metrics | Primary | ⭐⭐⭐⭐⭐ |
| `mcp_servers/omega_hub/server.py` | Hub Server | Primary | ⭐⭐⭐⭐ |
| Exa MCP Endpoint (401 response) | Live Test | Primary | ⭐⭐⭐⭐⭐ |

---

## §9 Document Sign-Off

| Role | Status | Date |
|------|--------|------|
| **researcher** — Author | ✅ Draft Complete | 2026-06-10 |
| **roc_racoon** — Code Audit Review | ✅ Complete | 2026-06-10 |
| **kali** — Oversight & Approval | ⏳ Pending | TBD |

---

*⬡ OMEGA ⬡ researcher ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_search_protocol_v1 ⬡ DRAFT*
