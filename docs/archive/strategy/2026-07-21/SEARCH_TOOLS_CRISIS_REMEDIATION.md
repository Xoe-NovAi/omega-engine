# 🔱 SEARCH TOOLS CRISIS REMEDIATION PLAN
**AP Token**: `AP-SEARCH-CRISIS-REMEDIATION-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_search_crisis ⬡ ACTIVE

**Date**: 2026-07-18
**Status**: EXECUTION PLAN — Ready for Implementation
**Handoff**: `ho_58791ace052f` (accepted by Researcher)

---

## 📋 EXECUTIVE SUMMARY

The Omega Engine's search pipeline has a **95% failure rate** on technical queries. The root causes are:

| Component | Status | Root Cause |
|-----------|--------|------------|
| **SearXNG MCP** | ❌ BROKEN | MCP server runs on port 8018, but opencode.json points to 8017; SearXNG instance has indexing issues |
| **Exa MCP** | ⚠️ REMOTE ONLY | No local MCP server; uses cloud API at mcp.exa.ai with API key dependency |
| **Firecrawl MCP** | ⚠️ PARTIAL | SSE transport crashes (ASGI race); content truncation at ~3000 chars; timeout defaults too low |
| **omega-hub wrappers** | ❌ 95% FAILURE | Both `library_web_search` and `sovereign_search` route through broken SearXNG → Exa → Firecrawl chain |
| **Direct tools** | ✅ WORKING | `firecrawl_firecrawl_*` and `webfetch` work for known URLs |

**Critical Insight**: The Sovereign Search Protocol (SSP-V2) 4-tier architecture (T0→T1→T2→T3) is **architecturally sound** but **operationally broken** because Tier 1 (SearXNG) fails silently, causing the entire pipeline to collapse.

---

## 🎯 REMEDIATION OBJECTIVES

### Phase 1: Immediate Stabilization (Week 1)
- [ ] Fix SearXNG MCP server port/config mismatch
- [ ] Fix Firecrawl MCP SSE transport stability
- [ ] Add Firecrawl content length parameter (remove 3000-char truncation)
- [ ] Increase Firecrawl default timeout to 60s
- [ ] Verify Exa API key resolution from KeyVault

### Phase 2: Pipeline Hardening (Week 2)
- [ ] Implement **true tier fallback** in `SovereignSearchService` (currently breaks on T1 failure)
- [ ] Add circuit breaker pattern for each tier
- [ ] Implement parallel tier execution with race semantics
- [ ] Add health checks for all providers before routing
- [ ] Fix `SearchRouter` to respect provider health

### Phase 3: Direct Tool Access (Week 2-3)
- [ ] Expose `firecrawl_firecrawl_search` and `firecrawl_firecrawl_scrape` as first-class OpenCode tools
- [ ] Add `webfetch` as primary T3 fallback
- [ ] Create `searxng_searxng_search` direct tool (bypass omega-hub)
- [ ] Document "Direct API First" research protocol

### Phase 4: Knowledge Base Integration (Week 3-4)
- [ ] Populate SovereignCache with successful research results
- [ ] Build curated URL registry per research domain
- [ ] Implement T0 local cache warming from successful T3 extractions
- [ ] Add automated freshness checks for cached results

---

## 🔧 PHASE 1: IMMEDIATE STABILIZATION (DETAILED)

### 1.1 Fix SearXNG MCP Server Configuration

**Problem**: 
- SearXNG MCP server runs on **port 8018** (see `mcp_servers/omega_hub/searxng/server.py`)
- opencode.json points to **port 8017** (the raw SearXNG instance, not the MCP wrapper)
- SearXNG instance itself has indexing/search quality issues

**Files to Fix**:
1. `opencode.json` line 35: Change URL from `http://127.0.0.1:8017/mcp` → `http://127.0.0.1:8018/mcp`
2. Verify SearXNG MCP server is actually running on 8018
3. Check SearXNG instance health at `http://127.0.0.1:8017/healthz`

**Code Location**: 
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/mcp_servers/omega_hub/searxng/server.py` (port 8018)
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json` line 35

### 1.2 Fix Firecrawl MCP SSE Transport Stability

**Problem**: 
- SSE transport crashes with "ASGI race condition" (see server.py lines 248-265)
- Retry logic exists but is reactive, not preventive
- Content truncated at 4000 chars (line 137: `md = ...[:4000]`)
- Default timeout 30s too low for JS-heavy docs

**Files to Fix**:
1. `mcp_servers/firecrawl/server.py`:
   - Line 137: Remove hardcoded `[:4000]` truncation, add `max_chars` parameter
   - Line 112: Increase default timeout from 30 → 60 seconds
   - Lines 248-265: Improve SSE stability (consider streamable-http transport)
   - Add `max_tokens` or `max_chars` parameter to scrape tool

**New Tool Signature**:
```python
async def firecrawl_scrape(
    url: str,
    only_main: bool = False,
    formats: str = "markdown",
    include_tags: str = "",
    exclude_tags: str = "",
    wait_for: int = 0,
    timeout: int = 60,  # INCREASED from 30
    max_chars: int = 0,  # NEW: 0 = no limit
) -> str:
```

### 1.3 Verify Exa API Key Resolution

**Problem**: Exa provider in `search_providers.py` uses KeyVault fallback but may fail silently.

**Verification Steps**:
1. Check `omega.vault.KeyVault().resolve("exa")` returns valid key
2. Verify `EXA_API_KEY` environment variable as fallback
3. Test Exa MCP connection at `https://mcp.exa.ai/mcp`

**Code Location**: `src/omega/oracle/search_providers.py` lines 199-207

---

## 🔧 PHASE 2: PIPELINE HARDENING (DETAILED)

### 2.1 True Tier Fallback Implementation

**Current Broken Behavior** (in `sovereign_search_service.py` lines 185-228):
```python
for tier in range(effective_tier, effective_max + 1):
    try:
        result = await self._execute_tier(tier, query, entity_name, limit)
        if result:
            report["primary_finding"] = result
            report["final_tier"] = tier
            report["status"] = "success"
            break  # STOPS on first success, but if T1 fails with exception, it logs and CONTINUES
    except Exception as e:
        report["fallback_log"].append(...)
        # Continues to next tier - THIS PART WORKS
```

**Actual Issue**: The `SearchRouter` routes to T1 (SearXNG) by default, but when SearXNG returns empty results (not an exception), the pipeline treats it as "empty" and continues to T2. However, the router's `provider_health` check is **not wired correctly** — it checks `model_gateway.health_monitor` which tracks LLM providers, not search providers.

**Fix Required**:
1. Add search provider health monitoring to `HealthMonitor`
2. Make `SearchRouter.route()` respect `provider_health` for search tiers
3. Implement **parallel tier execution** with race semantics (first successful result wins)
4. Add circuit breaker per tier (fail fast after N consecutive failures)

### 2.2 Circuit Breaker Pattern for Search Tiers

**New File**: `src/omega/oracle/search_circuit_breaker.py`

```python
class SearchCircuitBreaker:
    """Circuit breaker for search provider tiers."""
    
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures: Dict[int, int] = defaultdict(int)
        self.last_failure: Dict[int, float] = {}
        self.state: Dict[int, str] = defaultdict(lambda: "closed")  # closed|open|half-open
    
    def record_success(self, tier: int):
        self.failures[tier] = 0
        self.state[tier] = "closed"
    
    def record_failure(self, tier: int):
        self.failures[tier] += 1
        self.last_failure[tier] = time.time()
        if self.failures[tier] >= self.failure_threshold:
            self.state[tier] = "open"
    
    def can_execute(self, tier: int) -> bool:
        if self.state[tier] == "closed":
            return True
        if self.state[tier] == "open":
            if time.time() - self.last_failure[tier] > self.recovery_timeout:
                self.state[tier] = "half-open"
                return True
            return False
        return True  # half-open allows one test request
```

### 2.3 Parallel Tier Execution with Race Semantics

**Modified `search()` method** in `SovereignSearchService`:

```python
async def search(self, query: str, entity_name: str, limit: int = 10, ...) -> Dict[str, Any]:
    # Get search intent (includes primary_tier, max_tier)
    search_intent = self.router.route(...)
    
    # Determine tiers to execute
    tiers = list(range(search_intent.primary_tier, search_intent.max_tier + 1))
    
    # Execute ALL tiers in parallel, return first successful result
    async def execute_tier_with_breaker(tier: int):
        if not self.circuit_breaker.can_execute(tier):
            return None
        try:
            result = await self._execute_tier(tier, query, entity_name, limit)
            if result:
                self.circuit_breaker.record_success(tier)
                return (tier, result)
            self.circuit_breaker.record_failure(tier)
            return None
        except Exception as e:
            self.circuit_breaker.record_failure(tier)
            return None
    
    # Race: first completed successful result wins
    tasks = [execute_tier_with_breaker(t) for t in tiers]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    
    for task in done:
        result = task.result()
        if result:
            tier, finding = result
            # Cancel remaining
            for p in pending:
                p.cancel()
            return self._build_report(tier, finding, query, entity_name)
    
    # All failed or empty
    return self._build_failed_report(query, entity_name)
```

---

## 🔧 PHASE 3: DIRECT TOOL ACCESS (DETAILED)

### 3.1 Expose Firecrawl Tools Directly in OpenCode

**Current State**: Firecrawl tools only available via MCP (`firecrawl_firecrawl_search`, etc.) which requires manual enable in OpenCode CLI.

**Solution**: Add native OpenCode tool wrappers that call Firecrawl HTTP API directly (bypassing MCP).

**New File**: `src/omega/tools/firecrawl_direct.py`

```python
"""Direct Firecrawl API tools — bypass MCP for reliability."""

import httpx
import os
from typing import Optional, List

FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY") or _resolve_from_vault()
BASE_URL = "https://api.firecrawl.dev/v1"

async def firecrawl_search_direct(query: str, limit: int = 10) -> str:
    """Direct Firecrawl search — no MCP dependency."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{BASE_URL}/search",
            headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}"},
            json={"query": query, "limit": limit}
        )
        resp.raise_for_status()
        data = resp.json()
        # Format results...
        return formatted_results

async def firecrawl_scrape_direct(url: str, max_chars: int = 0, timeout: int = 60) -> str:
    """Direct Firecrawl scrape with configurable content length."""
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(
            f"{BASE_URL}/scrape",
            headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}"},
            json={"url": url, "formats": ["markdown"]}
        )
        resp.raise_for_status()
        data = resp.json()
        md = data.get("data", {}).get("markdown", "")
        if max_chars > 0:
            md = md[:max_chars]
        return md
```

**Register in OpenCode**: Add to `opencode.json` as native tools (not MCP).

### 3.2 Add SearXNG Direct Tool

**New File**: `src/omega/tools/searxng_direct.py`

```python
"""Direct SearXNG search — bypass omega-hub wrapper."""

import httpx
import os

SEARXNG_URL = os.environ.get("SEARXNG_BASE_URL", "http://127.0.0.1:8017")

async def searxng_search_direct(query: str, limit: int = 10, categories: str = "general") -> str:
    """Direct SearXNG search via HTTP API."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            f"{SEARXNG_URL}/search",
            data={"q": query, "format": "json", "categories": categories, "pageno": "1"}
        )
        resp.raise_for_status()
        data = resp.json()
        # Format results...
        return formatted_results
```

### 3.3 Research Protocol: "Direct API First"

**Document**: `docs/research/R_DIRECT_API_RESEARCH_PROTOCOL.md`

```markdown
# Direct API Research Protocol (Mandatory for Technical Queries)

## Priority Order for Technical Research:
1. **Official APIs** (HuggingFace Hub API, OpenCode Zen API, GitHub API, arXiv API)
2. **Direct Firecrawl** (`firecrawl_firecrawl_search` + `firecrawl_firecrawl_scrape`)
3. **Direct SearXNG** (`searxng_searxng_search`)
4. **webfetch** for known good URLs
5. **omega-hub_sovereign_search** ONLY as last resort

## NEVER DO:
- Rely solely on omega-hub search tools for technical queries
- Assume tiered fallback works (it doesn't)
- Skip verification of search results
```

---

## 🔧 PHASE 4: KNOWLEDGE BASE INTEGRATION (DETAILED)

### 4.1 SovereignCache Population Strategy

**Current**: `SovereignCache` in `src/omega/oracle/search_cache.py` only caches T3 (Firecrawl) results.

**Enhancement**: Cache successful results from ALL tiers with metadata.

```python
# In _tier_1_searxng, _tier_2_exa, _tier_3_firecrawl:
if result:
    self.cache.set(
        query=query,
        entity="global",  # or entity_name
        result=result,
        metadata={
            "tier": tier,
            "provider": provider_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query_hash": hashlib.sha256(query.encode()).hexdigest()[:16]
        }
    )
```

### 4.2 Curated URL Registry

**New File**: `config/research/url_registry.yaml`

```yaml
# Curated reliable sources per domain
domains:
  model_cards:
    - "https://huggingface.co/docs/hub/model-cards"
    - "https://huggingface.co/docs/hub/model-card-annotated"
    - "https://huggingface.co/{model_id}"
  opencode:
    - "https://opencode.ai/docs/"
    - "https://opencode.ai/zen/v1/models"
    - "https://pi.dev/models/opencode/"
  benchmarks:
    - "https://artificialanalysis.ai/"
    - "https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard"
  papers:
    - "https://arxiv.org/abs/{arxiv_id}"
    - "https://arxiv.org/pdf/{arxiv_id}.pdf"
```

### 4.3 T0 Cache Warming

**Background Job**: `src/omega/workers/cache_warmer.py`

```python
async def warm_cache_from_successful_research():
    """Extract successful T3 results and populate T0 cache."""
    # Query HALL_OF_RECORDS for completed research sessions
    # Extract successful Firecrawl extractions
    # Write to SovereignCache with TTL = 7 days
    pass
```

---

## 📊 IMPLEMENTATION CHECKLIST

### Phase 1: Immediate (Days 1-3)
| Task | File | Status |
|------|------|--------|
| Fix SearXNG MCP port in opencode.json | `opencode.json:35` | ☐ |
| Verify SearXNG MCP running on 8018 | `mcp_servers/omega_hub/searxng/server.py` | ☐ |
| Remove Firecrawl 4000-char truncation | `mcp_servers/firecrawl/server.py:137` | ☐ |
| Increase Firecrawl default timeout to 60s | `mcp_servers/firecrawl/server.py:112` | ☐ |
| Add `max_chars` parameter to firecrawl_scrape | `mcp_servers/firecrawl/server.py` | ☐ |
| Test Exa API key resolution | `src/omega/oracle/search_providers.py:199-207` | ☐ |

### Phase 2: Pipeline Hardening (Days 4-10)
| Task | File | Status |
|------|------|--------|
| Add search provider health to HealthMonitor | `src/omega/oracle/health_monitor.py` | ☐ |
| Implement SearchCircuitBreaker | `src/omega/oracle/search_circuit_breaker.py` (NEW) | ☐ |
| Modify SearchRouter to respect search provider health | `src/omega/oracle/search_router.py` | ☐ |
| Implement parallel tier execution in SovereignSearchService | `src/omega/oracle/sovereign_search_service.py` | ☐ |
| Add circuit breaker integration | `src/omega/oracle/sovereign_search_service.py` | ☐ |

### Phase 3: Direct Tools (Days 8-14)
| Task | File | Status |
|------|------|--------|
| Create firecrawl_direct.py | `src/omega/tools/firecrawl_direct.py` (NEW) | ☐ |
| Create searxng_direct.py | `src/omega/tools/searxng_direct.py` (NEW) | ☐ |
| Register direct tools in OpenCode | `opencode.json` (tools section) | ☐ |
| Write Direct API Research Protocol | `docs/research/R_DIRECT_API_RESEARCH_PROTOCOL.md` (NEW) | ☐ |

### Phase 4: Knowledge Integration (Days 12-21)
| Task | File | Status |
|------|------|--------|
| Enhance SovereignCache with tier metadata | `src/omega/oracle/search_cache.py` | ☐ |
| Create URL registry | `config/research/url_registry.yaml` (NEW) | ☐ |
| Implement cache warmer background job | `src/omega/workers/cache_warmer.py` (NEW) | ☐ |
| Add freshness checks for cached results | `src/omega/oracle/search_cache.py` | ☐ |

---

## 🧪 VALIDATION TESTS

### Test 1: SearXNG MCP Connectivity
```bash
# Should return healthy
curl http://127.0.0.1:8018/health
# Should return search results
curl -X POST http://127.0.0.1:8018/mcp -d '{"method":"tools/call","params":{"name":"searxng_search","arguments":{"query":"python asyncio","limit":5}}}'
```

### Test 2: Firecrawl Scrape Full Content
```python
# Should return >10000 chars for documentation pages
result = await firecrawl_scrape_direct("https://opencode.ai/docs/zen/", max_chars=0)
assert len(result) > 10000
```

### Test 3: Pipeline Fallback Works
```python
# Mock SearXNG to fail, verify Exa/Firecrawl still execute
service = SovereignSearchService(...)
with patch.object(service.searxng, 'search', side_effect=Exception("SearXNG down")):
    result = await service.search("test query", "RESEARCHER")
    assert result["status"] == "success"
    assert result["final_tier"] in [2, 3]  # Exa or Firecrawl
```

### Test 4: Circuit Breaker Opens
```python
breaker = SearchCircuitBreaker(failure_threshold=3)
for _ in range(3):
    breaker.record_failure(1)
assert breaker.can_execute(1) == False  # Circuit open
```

---

## 📁 DELIVERABLES

| Document | Path | Status |
|----------|------|--------|
| This Remediation Plan | `docs/strategy/SEARCH_TOOLS_CRISIS_REMEDIATION.md` | ✅ CREATED |
| Direct API Research Protocol | `docs/research/R_DIRECT_API_RESEARCH_PROTOCOL.md` | ☐ PENDING |
| Circuit Breaker Implementation | `src/omega/oracle/search_circuit_breaker.py` | ☐ PENDING |
| Firecrawl Direct Tool | `src/omega/tools/firecrawl_direct.py` | ☐ PENDING |
| SearXNG Direct Tool | `src/omega/tools/searxng_direct.py` | ☐ PENDING |
| URL Registry | `config/research/url_registry.yaml` | ☐ PENDING |
| Cache Warmer | `src/omega/workers/cache_warmer.py` | ☐ PENDING |

---

## 🎯 SUCCESS CRITERIA

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Technical query success rate | ~5% | >80% | 20 test queries across domains |
| Firecrawl content completeness | ~3000 chars | Full content | Compare with known-good pages |
| Pipeline fallback reliability | Broken | 100% | Mock each tier failure |
| SearXNG MCP availability | 0% (wrong port) | 99.9% | Health check endpoint |
| Research session tool diversity | 1-2 tools | 4+ tools | Tool usage logs |

---

## ⚠️ RISKS & MITIGATIONS

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| SearXNG instance fundamentally broken (indexing) | High | High | Direct API fallback; curated URL registry |
| Firecrawl API credits exhausted | Medium | High | Credit monitoring; local cache warming |
| Exa API key rotation | Low | Medium | KeyVault rotation; env var fallback |
| MCP transport instability (SSE) | High | Medium | Migrate to streamable-http; direct HTTP tools |
| OpenCode tool registration changes | Low | Medium | Version-pinned tool definitions |

---

## 🔗 RELATED DOCUMENTS

- `docs/strategy/TOOL_ISSUES_REPORT_20260718.md` — Original issue documentation
- `docs/strategy/RESEARCH_COMPREHENSIVE_REPORT_20260718.md` — Research findings despite broken tools
- `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` — Current sprint context (HMC Quad-Forge)
- `src/omega/oracle/sovereign_search_service.py` — SSP-V2 implementation
- `src/omega/oracle/search_router.py` — Intent-based routing
- `config/search.yaml` — SSP-V2 configuration

---

## 📝 HANDOFF NOTES

**Next Agent**: Researcher (this agent) — Execute Phase 1 immediately
**Dependencies**: 
- SearXNG MCP server must be running on port 8018
- Firecrawl API key must be in KeyVault or ENV
- Exa API key must be in KeyVault or ENV

**Blocking Issues**:
1. SearXNG MCP port mismatch in opencode.json (5-min fix)
2. Firecrawl content truncation (10-min fix)
3. No direct tool access for Firecrawl/SearXNG (requires new tool files)

**Immediate Next Steps**:
1. Fix `opencode.json` line 35 (port 8017 → 8018)
2. Edit `mcp_servers/firecrawl/server.py` line 137 (remove `[:4000]`)
3. Create `src/omega/tools/firecrawl_direct.py` and `searxng_direct.py`
4. Test end-to-end with a technical query

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_search_crisis ⬡ PLAN COMMITTED*