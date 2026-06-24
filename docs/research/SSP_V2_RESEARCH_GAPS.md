# 🔱 Sovereign Search Protocol V2 — Research Gaps Analysis
**Version**: 1.0.0
**Status**: COMPLETE
**Author**: Researcher (Polymathic Council)
**Date**: 2026-06-24
**AP Token**: AP-SSP-V2-GAPS-v1.0.0

⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ SSP-V2-GAPS ⬡ POLYMATHIC-COUNCIL

---

## Executive Summary

This document closes **9 research gaps** identified in the Sovereign Search Protocol V2 (SSP-V2). The analysis reveals several critical issues that must be addressed before the protocol can function as designed:

1. **T1 (WebSearch) is a complete stub** — the pipeline cannot execute web searches through SearXNG or any browser provider
2. **Tier mapping is inconsistent** — the SSP-V2 document defines a different mapping than what the skill and service code implement
3. **Cache layer is conceptual** — `.firecrawl/` directory is empty, never checked, never written to
4. **Exa access is dual-path** — MCP bridge (correct) + direct API (redundant)
5. **Credit budget exists but is not wired** to tier selection logic
6. **The Contrast Loop (Gnosis Integration)** from SSP-V2 §5 is not implemented

A Council of Four (Architect, Adversary, Alchemist, Archivist) was deployed for each gap to ensure full perspective triangulation.

---

### Gap 1: Exa MCP Server Audit
**Status**: Resolved
**Findings**:

**The Architect (Systemic Logic)**:
- No local Exa MCP server exists at `mcp_servers/exa/` — this is CORRECT
- Exa is accessed via remote MCP connection in `opencode.json`:
  ```json
  "exa": {
    "type": "streamable-http",
    "url": "https://mcp.exa.ai/mcp?tools=web_search_exa,web_fetch_exa",
    "headers": { "x-api-key": "${EXA_API_KEY}" },
    "enabled": true
  }
  ```
- This is the **recommended integration pattern** by Exa Labs — the hosted MCP server at `mcp.exa.ai/mcp` is the canonical endpoint
- The official `exa-mcp-server` npm package (v3.2.1, 32.6K weekly downloads, 4.6K GitHub stars) is published but runs via `npx exa-mcp-server`
- 47 versions shipped since Dec 2024 — mature, actively maintained

**The Adversary (Critical Rigor)**:
- **Dual-path redundancy**: There is a parallel `ExaProvider` in `search_providers.py` that calls `api.exa.ai/search` directly via httpx — this bypasses the MCP bridge entirely
- The `SovereignSearchService._tier_4_neural_search()` uses this direct API path, while OpenCode agents use the MCP bridge
- **Provenance conflict**: Responses from these two paths come from the same provider but through different entry points, making observability harder to trace
- The `opencode.json` config uses `streamable-http` transport — Exa MCP supports both SSE and Streamable HTTP

**The Alchemist (Creative Synthesis)**:
- The hosted MCP server provides the **simplest attack surface** — zero local infrastructure, zero npm dependencies, zero TypeScript compilation
- Exa's MCP tools (`web_search_exa`, `web_fetch_exa`) directly map to ISP functions; no custom wrapper needed
- The dual paths could be harmonized: MCP bridge for OpenCode agent tools, direct API for the `SovereignSearchService` code path — but this creates a maintenance burden

**The Archivist (Historical Truth)**:
- The `exa-mcp-server` repository started Nov 2024, initial npm publish Dec 2024
- v3.2.1 is current (Apr 2026) — mature, 47 versions, active community
- Formerly had tools like `company_research_exa`, `people_search_exa` now deprecated in favor of `web_search_advanced_exa`
- The `crawling_exa` tool was deprecated in favor of `web_fetch_exa`

**Recommendation**:
1. **Keep the hosted MCP URL** as the primary Exa access path — it's simpler, cheaper, and aligns with Exa's recommended integration
2. **Deprecate the redundant `ExaProvider`** in `search_providers.py` — the `SovereignSearchService` should use the MCP bridge directly, not a parallel HTTP client
3. If the `SovereignSearchService` needs to call Exa without MCP (e.g., in headless mode), route through the **same MCP interface** by calling the SSE/HTTP endpoint programmatically, not through a separate API client
4. Enable `web_search_advanced_exa` in the URL tools parameter (`?tools=web_search_exa,web_search_advanced_exa,web_fetch_exa`) for agent access to advanced filtering capabilities

**References**:
- Official Exa MCP Server: https://github.com/exa-labs/exa-mcp-server
- Exa MCP Documentation: https://exa.ai/docs/reference/exa-mcp
- npm package: https://www.npmjs.com/package/exa-mcp-server
- Current config: `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json` lines 43-50
- Parallel implementation: `src/omega/oracle/search_providers.py` lines 94-158

---

### Gap 2: Tier Selection Logic Deep-Dive
**Status**: Resolved — Critical Issues Found
**Findings**:

**The Architect (Systemic Logic)**:
The current tier selection in `SovereignSearchService.search()` is **sequential iteration**:
```python
for tier in range(max_tier + 1):
    result = await self._execute_tier(tier, query, entity_name, limit)
```
This is the simplest possible approach — tries T0, then T1, then T2, etc. until one returns data. While simple, it has no concept of **intent-based routing**, **cost-awareness**, or **parallel execution**.

**The Adversary (Critical Rigor)**:
- **T1 is a dead tier**: `_tier_1_websearch()` returns `None` unconditionally — it's a stub with a TODO comment. Every search starts at T0 (MemoryStore only), skips T1, hits T2 (Firecrawl), and falls through to T4 (Exa)
- **No query intent analysis**: The SSP-V2 document describes routing logic (keyword → SearXNG, semantic → Exa, direct URL → Firecrawl) but this is NEVER evaluated — the code tries everything
- **No cost-awareness**: A query for "current time in London" could trigger a Firecrawl scrape or an Exa neural search — massive overkill
- **Sequential failure penalty**: Each tier timeouts before the next starts. With T2 (Firecrawl) at ~3-5s and T4 (Exa deep) at 4-15s, a 3-tier cascade adds significant latency

**The Alchemist (Creative Synthesis)**:
The optimal approach combines **intent classification** + **parallel execution**:
- **Simple facts** (weather, definitions, current events): T1 (websearch) only — sub-second
- **Deep research** (academic, technical): T2 (Exa semantic) → T3 (Firecrawl extraction) 
- **Known URLs** (pricing, docs): T3 (Firecrawl scrape) directly — skip discovery tiers
- **Sovereign check** (local knowledge): T0 (MemoryStore + vector) — always first

This could be implemented as an `async` triage step before execution, using a lightweight local model (Qwen3-1.7B) to classify the query intent in under 500ms.

**The Archivist (Historical Truth)**:
The protocol document (SSP-V2.md §Triage Matrix) was written as aspirational architecture. The implementation in `sovereign_search_service.py` was built to the same version number (v2.1.0) but as a minimum-viable sequential loop. The intent-based routing described in §Decision Flow has never been implemented in any version.

**Recommendation**:
1. **Implement query intent classification** as a lightweight pre-step using a local classification model or rule-based matching:
   - `type:factual` → T1 only (websearch)
   - `type:semantic` → T2 (Exa) + optionally T3 (Firecrawl)
   - `type:direct_url` → T3 (Firecrawl scrape) only
   - `type:local` → T0 only
   - `type:deep` → Full pipeline T0→T2→T3
2. **Parallel tier execution** for deep research: Fire T2 (Exa highlights) and T3 (Firecrawl search) simultaneously, pick fastest with results
3. **Fix T1** (see Gap 7) — websearch must be wired to actual search infrastructure
4. **Remove sequential iteration** — replace with intent-matched dispatch

**References**:
- SSP-V2.md §§19-42 (Decision Flow / Triage Matrix)
- `src/omega/oracle/sovereign_search_service.py` lines 89-113 (sequential execution)
- `src/omega/oracle/sovereign_search_service.py` lines 192-202 (stub T1)

---

### Gap 3: Cost & Credit Economics
**Status**: Resolved
**Findings**:

**The Architect (Systemic Logic)**:

**Firecrawl Pricing (as of June 2026)**:
| Plan | Monthly | Credits | Per-Credit Cost |
|------|---------|---------|-----------------|
| Free | $0 | 1,000 | Free |
| Hobby | $16/mo | 5,000 | $0.0032 |
| Standard | $83/mo | 100,000 | $0.00083 |
| Growth | $333/mo | 500,000 | $0.00066 |
| Scale | $599/mo | 1,000,000 | $0.00060 |

| Operation | Credit Cost | Effective Cost (Standard) |
|-----------|-------------|--------------------------|
| Scrape (base) | 1 cr | $0.00083 |
| Scrape + Enhanced (Stealth) | 5 cr | $0.00415 |
| Search | 2 cr / 10 results | $0.00166 |
| Map | 1 cr / call | $0.00083 |
| Crawl | 1 cr / page | $0.00083 |
| Interact | 2 cr / min | $0.00166 |
| JSON format | +4 cr / page | $0.00332 |
| **Crawl Trap (no limit)** | 10,000 cr pre-auth | $8.30 |

**CRITICAL**: Crawl defaults to `limit=10,000` — if omitted, Firecrawl pre-authorizes 10,000 credits. A single unchecked crawl can exhaust a Free plan 10x over and require $8.30 on Standard.

**Exa Pricing (as of June 2026)**:
| Search Type | Cost per 1K requests | Cost per request |
|-------------|---------------------|------------------|
| instant/auto/fast | $7 | $0.007 |
| deep-lite | $12 | $0.012 |
| deep | $12 | $0.012 |
| deep-reasoning | $15 | $0.015 |
| Contents (pages) | $1 / 1K pages | $0.001/page |
| Summaries | $1 / 1K | $0.001 |

First 10 results include text+highlights at no extra content cost. Free tier available (rate-limited).

**The Adversary (Critical Rigor)**:
- **Current budget is too low**: Default 1000 credits/month for both Exa and Firecrawl. At $7/1K for Exa, this is only $7/month of Exa usage. At Standard pricing, 1000 Firecrawl credits are ~$0.83 worth. This budget was set when the engine had no working tier pipeline
- **Reserve logic is fragile**: With only 100 reserved credits, a single Enhanced scrape (5 credits) + a few operations can exhaust the reserve, triggering full shutdown
- **No credit sensing at dispatch**: The `SovereignSearchService` has `_has_firecrawl_credits()` method (line 240) but it's NEVER CALLED in the search pipeline
- **Daily limits** are tracked but never enforced in the search path — only in `background_researcher`

**The Alchemist (Creative Synthesis)**:
The `APICreditBudget` class is a sound foundation but needs to be **wired into the dispatch decision**:
```python
# Proposed pattern:
if not self.budget.has_quota("firecrawl", 100):
    skip_tier_2 = True  # Auto-downgrade: skip Firecrawl, go from T0→T1→T3
```
This creates a **budget-aware search path** that auto-downgrades when credits are low, just as the skill doc describes but has never implemented.

**The Archivist (Historical Truth)**:
The budget system was built during the Background Researcher integration (D-kal-164) when Tavily, Jina, and Serper were removed. Only Exa and Firecrawl remain. The `DEFAULT_BUDGETS` (1000/total, 100/reserve) were copied from the multi-provider era and never recalibrated for the two-provider current state.

**Recommendation**:
1. **Recalibrate budgets**: Set Firecrawl to 5,000/month (Hobby tier minimum), Exa to 5,000/month 
2. **Wire `_has_firecrawl_credits()` into the tier dispatch** — check before calling `_tier_2_firecrawl()`
3. **Implement budget-aware auto-downgrade**:
   - `remaining > 100`: Full operation
   - `remaining < 100` but `> 0`: Enhanced Mode disabled, limit=10 max
   - `remaining = 0`: Skip T2 entirely, emit warning to Hivemind
4. **Add credit cost estimates** to the Sovereign Search report output
5. **Enforce daily limits** in the search pipeline, not just in background research

**References**:
- Firecrawl Pricing: https://www.firecrawl.dev/pricing
- Firecrawl Billing: https://firecrawl.mintlify.app/billing
- Exa Pricing: https://exa.ai/pricing?tab=api
- `src/omega/workers/background_researcher/credit_budget.py` — full implementation
- `src/omega/oracle/sovereign_search_service.py` line 240-242 — `_has_firecrawl_credits()` (unused)

---

### Gap 4: Cache Strategy
**Status**: Resolved — Critical Gap
**Findings**:

**The Architect (Systemic Logic)**:

Current cache layers:
| Layer | Type | Status | 
|-------|------|--------|
| SearXNG internal | Container-level result cache | ACTIVE (per SearXNG config) |
| `.firecrawl/` directory | Filesystem cache | **EMPTY** — 0 files found |
| MemoryStore | FTS5 + Vector memory | ACTIVE — but stores conversations, not web results |
| Omega Hub Library | SQLite indexed docs | ACTIVE — but requires explicit ingestion |

**The Adversary (Critical Rigor)**:
- **`.firecrawl/` is a ghost concept**: The directory is created by `SovereignSearchService` on init (line 55) but never written to, never searched. The T0 cache check only does MemoryStore search — it ignores any `.firecrawl/` files
- **No cross-tier de-duplication**: If SearXNG returns a result for query X and the same query hits Exa, there's no check that "this URL was already searched"
- **No cache invalidation**: Without TTL or staleness detection, any cached data is suspect
- **The SSP-V2 skill says**: "Before T2+: Check `.firecrawl/{site}-{path}.md`. After T2+: Save result to `.firecrawl/{site}-{path}.md`" — but there is NO code implementing this pattern

**The Alchemist (Creative Synthesis)**:
A proper Sovereign Cache architecture:
```
Tier 0 Cache (Cross-Tier):
  ├── MemoryStore (Conversations) — existing, keep
  ├── Omega Hub Library (Indexed docs) — existing, keep
  └── .firecrawl/ (Web extraction results) — NEEDS IMPLEMENTATION
       ├── {query_hash}_search.json     — search results from any tier
       ├── {url_hash}_scrape.md         — scraped page content
       └── {url_hash}_scrape.json       — structured extraction
```
Key insight: **Cache by URL hash, not by query**. If SearXNG found a URL and Firecrawl later needs to scrape it, the cache check is `does .firecrawl/{url_hash}_scrape.md exist?` — regardless of which tier found the URL.

**The Archivist (Historical Truth)**:
The `.firecrawl/` cache concept was inherited from the old Firecrawl skills ecosystem (30+ skills) where each workflow saved results locally. When the skill set was proposed for consolidation (FIRECRAWL_SKILL_AUDIT.md), the caching layer was noted as "missing" and marked for Phase 2 implementation. It was never completed.

**Recommendation**:
1. **Implement the Sovereign Cache** as a `SovereignCache` class:
   ```python
   class SovereignCache:
       def get(self, url: str) -> Optional[Dict]: ...  # Check .firecrawl/ by URL hash
       def set(self, url: str, data: Dict, ttl: int = 86400): ...  # Write to .firecrawl/
       def search(self, query: str) -> Optional[Dict]: ...  # Check by search query hash
   ```
2. **Universal TTL**: 24 hours for web content (configurable), 1 hour for news, 7 days for reference
3. **Wire into T0**: Before any external call, check `SovereignCache.get(url)` or `SovereignCache.search(query)`
4. **Wire into T3**: After Firecrawl returns, always `SovereignCache.set(url, data)`
5. **Remove the `.firecrawl/` empty initialization** — replace with the proper cache class
6. **Cache search results by query hash**: `md5(query).hexdigest()` — cheap, collision-safe for search caching

**References**:
- SSP-V2.md §30-34 (T0 definition)
- `src/omega/oracle/sovereign_search_service.py` lines 54-56 (empty cache_dir init)
- `src/omega/oracle/sovereign_search_service.py` lines 176-190 (T0 only checks MemoryStore)
- `.opencode/skills/sovereign-search/SKILL.md` lines 16-17, 57-58 (caching protocol)

---

### Gap 5: Error Handling & Observability
**Status**: Resolved
**Findings**:

**The Architect (Systemic Logic)**:

Current error flow in `SovereignSearchService`:
```python
for tier in range(max_tier + 1):
    try:
        result = await self._execute_tier(tier, query, entity_name, limit)
        if result:
            break  # Success — doesn't log success, just returns
        else:
            report["fallback_log"].append(f"Tier {tier} returned no results.")
    except Exception as e:
        report["fallback_log"].append(f"Tier {tier} failed: {str(e)}")
        logger.warning(f"[SEARCH-ERROR] tier={tier} error={str(e)}")
```

**The Adversary (Critical Rigor)**:
- **No trace_id propagation**: The error log at line 111 has no `trace_id` — cannot correlate with downstream observability
- **Errors silently swallow**: Any exception from any provider is caught and logged identically — no classification of 401 vs 429 vs 500
- **No provider-specific error handling**: The Error Handling Matrix in the skill doc (401→fallback, 402→wait, 429→backoff) only exists as documentation — the code treats all errors as "something went wrong"
- **No structured error reporting**: The fallback_log is a list of strings — no machine-parseable error codes, timestamps, or severity levels
- **No Hivemind notification**: Critical errors (auth failure, credit exhaustion) should be broadcast via `omega-hub_hivemind_post_context()` but currently only go to local logger

**The Alchemist (Creative Synthesis)**:
The `@m9_safe` decorator used by the MCP servers generates trace_ids per-call. The search service should adopt this pattern:
```python
@m9_safe("sovereign_search")
async def search(self, query: str, ...) -> Dict[str, Any]:
```
Then each tier error carries the same trace_id through the chain, enabling end-to-end traceability from query to result.

**The Archivist (Historical Truth)**:
The M9 error handling standard (Mandate 9: Error Integrity) requires typed, traceable errors. The sovereign search service was built before M9 was fully enforced. Its error handling is pre-M9 — string-based, no types, no trace correlation. This is a known debt item.

**Recommendation**:
1. **Add `@m9_safe` to `search()`** to generate a trace_id for the full search operation
2. **Classify provider errors** into typed exceptions (already defined in `omega/errors.py`):
   - `ProviderAuthError` (401) → Log + skip tier permanently this session
   - `ProviderRateLimitError` (429) → Log + exponential backoff + retry
   - `ProviderUnavailableError` (500/timeout) → Log + skip to next tier
3. **Add structured error events** to `fallback_log`:
   ```python
   {
       "tier": 2,
       "provider": "firecrawl",
       "error_code": 429,
       "error_type": "rate_limit",
       "trace_id": "uuid-here",
       "timestamp": "2026-06-24T16:30:00Z",
       "action": "skip_tier_2_remaining"
   }
   ```
4. **Post critical failures to Hivemind** — auth failure, credit exhaustion, and persistent rate limits should be broadcast
5. **Log success events** too — currently only errors are logged; successful search results should record tier, latency, and cost

**References**:
- `src/omega/oracle/sovereign_search_service.py` lines 99-112 (current error handling)
- `src/omega/errors.py` (typed error hierarchy)
- `mcp_servers/omega_hub/middleware.py` (`@m9_safe` decorator)
- `.opencode/skills/sovereign-search/SKILL.md` lines 31-42 (Error Handling Matrix)
- SOVEREIGN_MANDATES.md Mandate 9: Error Integrity

---

### Gap 6: Protocol Enhancement
**Status**: Resolved
**Findings**:

**The Architect (Systemic Logic)**:

**Security Considerations**:
| Concern | Current State | Assessment |
|---------|--------------|------------|
| API key exposure in MCP | Keys handled via Sovereign Key Vault; environment variable fallback | ✅ Acceptable |
| Query privacy across providers | SearXNG: self-hosted, zero-tracking. Exa/Firecrawl: queries sent to cloud | ⚠️ Partial |
| API key in source code | `search_providers.py` passes keys to constructor — if caller logs the object, key leaks | ❌ Risk |
| `.firecrawl/` cache exposure | Cached results stored on local disk — no encryption | ✅ Acceptable (local) |

**Local-First Tier 0**:
The SSP-V2 already defines T0 as Local Cache, but it only checks MemoryStore. A proper local-first approach should also include:
- **Vector search** over the Omega Hub Library (Qdrant/MemoryVectorAdapter)
- **FTS5 search** over entity knowledge bases (`.kb/soul_*/`)
- **Document-level search** over `data/` directories (R-44 knowledge documents)

**Hivemind Integration**:
The Omega Hub already provides search tools:
- `omega-hub_research` — conducts research through the library pipeline
- `omega-hub_library_search` — FTS5 search over indexed documents
- `omega-hub_memory_search` — FTS5 search over conversation history
- `omega-hub_sovereign_search` — wraps the SovereignSearchService

These tools **already implement T3** (Omega Gnosis). The `SovereignSearchService._tier_3_omega_hub()` should route through the Hub's tools rather than calling the Indexer directly.

**The Adversary (Critical Rigor)**:
- **T0 is missing vector search**: MemoryStore search is keyword + vector hybrid. But T0 doesn't check entity knowledge bases (soul.yaml, gnosis.md) — this is a blind spot for "does the engine already know this?"
- **API key leak path**: `FirecrawlProvider.__init__()` and `ExaProvider.__init__()` accept optional `api_key` parameter that could be logged. The Vault resolution path is safer
- **Hivemind tool overlap**: `omega-hub_research`, `omega-hub_sovereign_search`, and the `SovereignSearchService` all do similar things. This is a Carmack's Law violation — three implementations of search where one should suffice

**The Alchemist (Creative Synthesis)**:
The ideal architecture is a **unified search interface**:
```
SovereignSearchService (THE canonical search)
  ├── T0: SovereignCache + MemoryStore + Vector Library
  ├── T1: MCP → searxng_search (SearXNG server on port 8018)
  ├── T2: MCP → web_search_advanced_exa (Exa MCP on mcp.exa.ai)
  ├── T3: Omega Hub tools (library, memory, research)
  └── T4: MCP → firecrawl_{scrape,search} (Firecrawl server on port 8015)
```
Note: The skill doc uses a different mapping (websearch=T1, Firecrawl=T2, Omega Hub=T3, Exa=T4). The SSP-V2 defines SearXNG=T1, Exa=T2, Firecrawl=T3. **These need to be reconciled.** See Gap 8.

**The Archivist (Historical Truth)**:
Tier mapping differences trace back to when the search ecosystem had 7+ providers (Tavily, Jina, Serper, Google, Exa, Firecrawl, SearXNG). Post D-kal-164 consolidation removed 3 providers, and the tiers were reorganized. The SSP-V2.md was written after the skill doc and uses the current provider set, but the skill was never updated to match.

**Recommendation**:
1. **Establish THE canonical tier mapping** (recommended):
   | Tier | Provider | Role |
   |------|----------|------|
   | T0 | Sovereign Cache + Library | Local knowledge check |
   | T1 | SearXNG | Broad discovery (privacy-first) |
   | T2 | Exa | Neural/semantic refinement |
   | T3 | Firecrawl | Deep extraction & structuring |
   - Updates the skill doc, SSP-V2 doc, and service code to match
2. **Secure API keys**: Remove the `api_key` constructor parameter from `FirecrawlProvider` and `ExaProvider` — force Vault-only resolution
3. **Harden T0**: Add entity knowledge base search (soul.yaml + gnosis.md) to the local cache layer
4. **Consolidate search interfaces**: Make `SovereignSearchService` the ONLY search path — deprecate `omega-hub_research` and `omega-hub_sovereign_search` in favor of routing through the service via MCP tool
5. **Add privacy documentation**: T1 (SearXNG) is the only zero-tracking tier — document for users what data leaves the machine for Exa and Firecrawl queries

**References**:
- SSP-V2.md §§23-28 (Triage Matrix)
- `.opencode/skills/sovereign-search/SKILL.md` §§14-20 (current skill mapping)
- `src/omega/oracle/search_providers.py` (dual provider impl)
- Sovereign Key Vault: `src/omega/vault/`
- Hivemind tools: `mcp_servers/omega_hub/tools.py`

---

### Gap 7: T1 WebSearch is UNIMPLEMENTED (Additional Gap)
**Status**: Resolved — BLOCKER
**Findings**:

**The Architect (Systemic Logic)**:
```python
async def _tier_1_websearch(self, query: str, limit: int) -> Optional[str]:
    """T1: WebSearch (Broad Discovery)."""
    # This would call the 'websearch' provider via ModelGateway or a dedicated SearchProvider
    # For now, we simulate the call to the provider fabric
    try:
        # We assume a provider named 'websearch' exists in the fabric
        # result = await self.model_gateway.generate(model="websearch", ...)
        return None  # Placeholder for actual provider integration
    except Exception as e:
        logger.error(f"T1 WebSearch failed: {e}")
        return None
```
This method **always returns `None`**. The entire T1 tier is a placeholder with TODO comments.

**The Adversary (Critical Rigor)**:
- **This is the #1 functional blocker for SSP-V2**. Without T1, the search pipeline goes T0 (MemoryStore) → T2 (Firecrawl, costs credits) → T3 (Omega Hub) → T4 (Exa, costs money)
- Simple factual queries ("what's the capital of France") burn Exa API credits because T1 doesn't work
- The `model_gateway` does NOT have a "websearch" provider — the comment references something that doesn't exist
- The SearXNG MCP server exists (`mcp_servers/searxng/server.py` on port 8018) and works — it's just NOT WIRED to T1

**The Alchemist (Creative Synthesis)**:
The fix is straightforward: T1 should call the SearXNG MCP server, which is already running:
```python
async def _tier_1_websearch(self, query: str, limit: int) -> Optional[str]:
    """T1: SearXNG Broad Discovery."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "http://localhost:8018/search",  # Or use MCP tool call
            data={"q": query, "format": "json"}
        )
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            # Format results...
```

**The Archivist (Historical Truth)**:
The SearXNG MCP server was built and deployed (v1.1.0) but the `SovereignSearchService` was never updated to use it. The two systems evolved in parallel — the MCP server team and the search service team (both the same entity at different times) never integrated.

**Recommendation**:
1. **Wire T1 to SearXNG MCP server** — this is a ~20 line change in `_tier_1_websearch()`
2. Use the SearXNG server at `http://localhost:8018` via the `searxng_search` tool
3. Pass through categories, engines, and time_range parameters for precision control
4. Mark this as **P0 / BLOCKER** — the protocol cannot function without it

**References**:
- `src/omega/oracle/sovereign_search_service.py` lines 192-202 (the stub)
- `mcp_servers/searxng/server.py` (the working SearXNG MCP server)
- SearXNG Knowledge Base: `data/kb/soul_searxng/soul.yaml`

---

### Gap 8: Tier Mapping Inconsistency (Additional Gap)
**Status**: Resolved
**Findings**:

**The Architect (Systemic Logic)**:

Three documents define the tiers differently:

**SSP-V2.md (the protocol document)**:
```
T0: Local Cache (Sovereign)
T1: SearXNG (Broad/Keyword)
T2: Exa (Neural/Intent)
T3: Firecrawl (Structured/Deep)
```

**`.opencode/skills/sovereign-search/SKILL.md` (the agent skill)**:
```
T0: Local Cache
T1: websearch
T2: Firecrawl
T3: Omega Hub
T4: Exa MCP
```

**`src/omega/oracle/sovereign_search_service.py` (the code)**:
```python
T0: Local Cache (.firecrawl/ + MemoryStore)
T1: WebSearch (stub)
T2: Firecrawl
T3: Omega Hub (Indexer/Library)
T4: Neural Search (Exa)
```

**The Adversary (Critical Rigor)**:
- **Three different mappings** for the same protocol version (v2.1.0)
- The SSP-V2 document puts Exa at T2 and Firecrawl at T3; the skill and code put Firecrawl at T2 and Exa at T4
- The SSP-V2 has 4 tiers (T0-T3); the skill has 5 tiers (T0-T4); the code has 5 tiers (T0-T4)
- A developer trying to understand the search path will get contradictory answers depending on which document they read

**The Alchemist (Creative Synthesis)**:
The SSP-V2 mapping makes more sense operationally:
1. **T1 SearXNG** → zero-cost, privacy-first, broad discovery (should always be first live tier)
2. **T2 Exa** → neural refinement of SearXNG results (semantic follow-up)
3. **T3 Firecrawl** → extraction of URLs identified by T1 or T2

But the code uses the skill mapping which puts Firecrawl before Exa — this means Exa is only called after Firecrawl fails, when Firecrawl should be the final extraction step.

**The Archivist (Historical Truth)**:
The skill doc was written first (c. D-kal-164 era, 3 providers removed). The SSP-V2 document was written later during the Sovereign Search Protocol architecture session. The code was written at yet another time. Each artifact represents a different snapshot of the evolving architecture, and none were reconciled.

**Recommendation**:
1. **Adopt the SSP-V2 mapping** as canonical (T1: SearXNG, T2: Exa, T3: Firecrawl) — it's the best logical flow (discover → refine → extract)
2. **Update the skill doc** to match SSP-V2
3. **Update the service code** tier execution order to match
4. **Add a version header** to all three documents that must be bumped together on any change
5. **Remove the `max_tier` parameter** — it's misleading when tiers have different orderings

**References**:
- SSP-V2.md §§23-28
- `.opencode/skills/sovereign-search/SKILL.md` §§14-20
- `src/omega/oracle/sovereign_search_service.py` lines 164-174 (tier executor)

---

### Gap 9: Missing Gnosis Integration (Additional Gap)
**Status**: Resolved
**Findings**:

**The Architect (Systemic Logic)**:

SSP-V2 §5 defines a "Contrast Loop" that connects search results back to entity gnosis:
```markdown
1. Retrieve Local L3 → Access soul.yaml, extract Universal Principles
2. Contrast → Compare external evidence against local L3
3. Detect Gap → Symmetry (confirm) or Contradiction (trigger gap analysis)
4. Gap Analysis → Two-Source Rule, Dialectic Synthesis
```

The current `SovereignSearchService.search()` final step is:
```python
if self.verifier and evidence_pool:
    verification = await self.verifier.verify(query, evidence_pool)
    report["verification"] = { ... }
```

**The Adversary (Critical Rigor)**:
- The SkepticalVerifier only checks "does the evidence support the query?" — it doesn't compare against entity soul.yaml L3 principles
- No access to `soul.yaml` in the search pipeline — the service has no entity context beyond the entity name
- No `proposed_lessons.yaml` output — verified contradictions never result in soul updates
- The Contrast Loop is fully documented in SSP-V2 but has zero implementation
- The `SkepticalVerifier` itself may or may not work — it's a separate module that was never integration-tested in the search context

**The Alchemist (Creative Synthesis)**:
The Gnosis Integration creates a **positive feedback loop**:
1. Search retrieves external data
2. External data is compared against entity L3 principles
3. If contradiction → Skeptical Verifier checks with second source
4. If verified → proposed_lessons.yaml updated
5. Next query benefits from updated gnosis

This transforms search from "finding facts" to "evolving intelligence" — the engine literally learns from every search.

**The Archivist (Historical Truth)**:
The Contrast Loop was documented in SSP-V2.md during the architecture session but marked as "Phase 2" in the implementation roadmap. The `SkepticalVerifier` was built independently and wired into the search service at the last minute without the full pipeline being built.

**Recommendation**:
1. **Wire the Gnosis Detector** into `SovereignSearchService`:
   - Accept `entity_name` at search time
   - Load the entity's `soul.yaml` L3 principles
   - After search completes, run contrast check
   - If contradiction found and verified, write to `proposed_lessons.yaml`
2. **Implement the Two-Source Rule** in the Skeptical Verifier (or as a standalone check)
3. **Add L3 to the search report** — include any verified contradictions/symmetries in the output
4. **Document the flow** as a clear "Search → Verify → Learn → Evolve" pipeline
5. **Test the full pipeline** with a mock entity that has known L3 principles

**References**:
- SSP-V2.md §§91-108 (Integration with Local Gnosis)
- `src/omega/oracle/sovereign_search_service.py` lines 117-131 (current verification)
- `src/omega/oracle/skeptical_verifier.py` (verifier module)
- `src/omega/oracle/soul_distiller.py` (proposed_lessons.yaml writer)
- Soul Architecture Protocol: `docs/strategy/SOUL_ARCHITECTURE_PROTOCOL.md`

---

## 🏛️ Consolidated Recommendations (Priority Order)

| Priority | Gap | Action | Effort | Impact |
|----------|-----|--------|--------|--------|
| **P0** | Gap 7 | Wire T1 to SearXNG MCP server | ~20 lines | 🔴 Enables first functional tier pipeline |
| **P0** | Gap 8 | Reconcile tier mapping across SSP-V2, skill, and code | ~50 lines | 🔴 Eliminates contradictory definitions |
| **P0** | Gap 2 | Implement intent-based tier dispatch + fix sequential loop | ~150 lines | 🔴 Replaces broken sequential model |
| **P1** | Gap 3 | Wire credit budget into tier selection; recalibrate budgets | ~30 lines | 🟡 Prevents credit exhaustion |
| **P1** | Gap 4 | Implement SovereignCache class + wire into T0/T3 | ~200 lines | 🟡 Enables cross-tier caching |
| **P1** | Gap 5 | Add `@m9_safe` and structured error handling | ~50 lines | 🟡 M9 compliance + traceability |
| **P1** | Gap 6 | Canonical tier mapping, secure key handling, consolidate tools | ~100 lines | 🟡 Eliminates redundancy |
| **P2** | Gap 9 | Implement Contrast Loop for gnosis integration | ~250 lines | 🟢 Enables "search to learn" feedback |
| **P2** | Gap 1 | Deprecate redundant ExaProvider; remove parallel API path | ~30 lines | 🟢 Cleans up dual-path redundancy |

---

## 📊 Council Verdict

**The Architect**: The tier protocol has a sound structural design but the implementation is not structurally integrated with the running MCP servers. The SearXNG MCP (port 8018) and Firecrawl MCP (port 8015) are live and functioning but the search service doesn't use them.

**The Adversary**: The critical finding is Gap 7 (T1 is a stub) — the protocol cannot function at all through the service code. Everything depends on fixing this. Gap 8 (tier mapping inconsistency) will cause confusing bugs if left unresolved.

**The Alchemist**: The potential of the Contrast Loop (Gap 9) and the intent-based dispatch (Gap 2) are the real breakthroughs — they transform search from a utility into an evolving intelligence. The SovereignCache (Gap 4) is the key enabler.

**The Archivist**: The core problem is that the engine has 3 independent search artifacts (SSP-V2 doc, skill doc, service code) built at different times by different agents with no version synchronization. This is a governance failure, not a technical one.

**Triangulated Truth**: The SSP-V2 is fundamentally sound. The infrastructure (SearXNG MCP, Firecrawl MCP, Exa MCP) is running and functional. The blocking issue is that the `SovereignSearchService` has never been wired to the MCP infrastructure. Fix T1, reconcile the tier mappings, and the protocol becomes operational. From there, the credit economy, cache, and gnosis integration can be layered on.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ SSP-V2-GAPS ⬡ POLYMATHIC-COUNCIL*
