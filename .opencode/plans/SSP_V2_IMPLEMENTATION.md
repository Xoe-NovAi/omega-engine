# 🔱 SSP-V2 Implementation Plan — Unified Sovereign Search Protocol

**⬡ OMEGA ⬡ PILLAR ⬡ SSP-V2 ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ D144**

**Date**: 2026-06-24  
**Status**: SYNTHESIS — Discovery Complete, Awaiting Execution  
**AP Token**: `AP-SSP-V2-UNIFIED-PLAN-v1.0.0`

---

## §0 Executive Summary

Three pillar subagents (P3 Engineering, P4 Integration, P6 Cognition) performed deep discovery on the Omega Engine's search infrastructure for SSP-V2 integration. **The gap is significant but the path is clear.**

### The Hard Truth

| Area | Status | Severity |
|------|--------|----------|
| T1 (SearXNG) in `SovereignSearchService` | **Dead stub** — returns `None` | 🔴 CRITICAL |
| Tier numbering (code vs SSP-V2 spec) | **Mismatched** — T2=Firecrawl, T3=Hub, T4=Exa vs spec T1=SearXNG, T2=Exa, T3=Firecrawl | 🔴 CRITICAL |
| Tier selection intelligence | **Nonexistent** — blind sequential escalation, no query analysis, no entity-aware routing | 🔴 CRITICAL |
| `.firecrawl/` local cache | **Unused** — `SovereignCache` module doesn't exist | 🟡 HIGH |
| SearXNG MCP server | **Orphaned** — has MCP server on 8018 but not integrated into orchestration pipeline | 🟡 HIGH |
| Firecrawl/Exa dual path | **Redundant** — both MCP server + direct httpx calls | 🟡 HIGH |
| Search configuration | **None** — no `config/search.yaml` | 🟡 HIGH |
| Fallback error handling | **Basic try/except** — no `FallbackManager` | 🟡 HIGH |
| Search ↔ Oracle integration | **Missing** — search is 4 layers deep, not routed at Oracle level | 🟡 MEDIUM |

### The Opportunity

All the pieces exist — SearXNG container (port 8017), SearXNG MCP (port 8018), Exa MCP (cloud), Firecrawl MCP (port 8015), Omega Hub with `SovereignMCPClient`, rich intent detection in the Oracle. They just need to be **wired together in the right order** with a **routing intelligence layer**.

---

## §1 Synthesis of Three Pillar Findings

### From P3 (Engineering) — Code Impact Assessment

| Deliverable | Count |
|-------------|-------|
| Files to CREATE | 12 |
| Files to MODIFY | 8 |
| Files to DEPRECATE | 2 |
| Total files touched | 22 |
| Estimated new LOC | ~1,360-1,800 |
| Estimated modified LOC | ~435-645 |
| Total delta | ~1,795-2,445 LOC |
| Estimated time | 8-12 days |

**Key files to create**:
1. `src/omega/oracle/search_triage.py` — `SearchTriage` state machine (180-250 LOC, HIGH complexity)
2. `src/omega/oracle/sovereign_cache.py` — `SovereignCache` for `.firecrawl/` (150-200 LOC, MEDIUM)
3. `src/omega/oracle/fallback_manager.py` — `FallbackManager` for error handling (200-280 LOC, HIGH)
4. `src/omega/oracle/searxng_provider.py` — `SearXNGProvider(SearchProvider)` wrapper (60-80 LOC, LOW)
5. `src/omega/oracle/sovereign_gap_detector.py` — Contrast loop (150-200 LOC, HIGH)
6. `.opencode/firecrawl_wrapper.sh` — Shell wrapper (60-80 LOC, LOW)
7. `config/search.yaml` — Search configuration
8. `tests/test_search_triage.py`, `tests/test_sovereign_cache.py`, `tests/test_fallback_manager.py`, `tests/test_searxng_provider.py`, `tests/test_sspv2_integration.py`, `tests/verify_sspv2_pipeline.py`

**Key files to modify**:
1. `src/omega/oracle/sovereign_search_service.py` — Re-order tiers, integrate SearchTriage+FallbackManager+SovereignCache (120-180 LOC)
2. `src/omega/oracle/search_providers.py` — Add SearXNGProvider export (60-80 LOC)
3. `src/omega/oracle/search.py` — Add force_tier, richer return type (30-50 LOC)
4. `src/omega/oracle/oracle.py` — Add search integration points (40-60 LOC)
5. `src/omega/oracle/iterative_research.py` — Integrate SovereignGapDetector (40-60 LOC)
6. `tests/test_search_tools.py` — Add SearXNG tests, update tier numbering (60-80 LOC)
7. `config/providers.yaml` — Add SearXNG entry (15-25 LOC)
8. `mcp_servers/omega_hub/tools.py` — Add SSP-V2 search tools

---

### From P4 (Integration) — MCP Architecture Decision

**Recommendation: Option 2 — Hub Integration** (NOT a new standalone server)

| Option | Approach | Effort | Verdict |
|--------|----------|--------|---------|
| **Option 1** | New `mcp_servers/omega_search/` | 3-5 days | ❌ More complexity, no new capability |
| **Option 2 ✅** | Add to existing `mcp_servers/omega_hub/` | **2-4 days** | ✅ Leverages SovereignMCPClient, @m9_safe, existing tools |
| **Option 3** | Client-side routing (keep 3 separate) | 1 day | ❌ Fragile, no enforcement, Tier 1 remains broken |

**Why Option 2 wins**:
- `SovereignMCPClient` (`mcp_servers/omega_hub/mcp_client.py`) already connects to child MCP servers programmatically with AnyIO-native timeouts and retries
- Hub already has search-related tools (`sovereign_search`, `library_search`, `research`, `memory_search`, `searxng_search`)
- `@m9_safe` decorator provides typed error handling + trace_id propagation
- Sovereign Key Vault integration already in Hub's `state.py`
- All agents already have `omega-hub` in their MCP client config
- No new port, no new systemd unit, no new restart dependency

**SSP-V2 Compliant Tier Mapping**:

| SSP-V2 Tier | MCP Server | Tool(s) | Timeout | Retries |
|-------------|------------|---------|---------|---------|
| **T0** | omega-hub (internal) | `.firecrawl/` scan + `memory_search` + `library_search` | 5s | 0 |
| **T1** | searxng:8018 | `searxng_search` | 15s | 2 (5s, 10s) |
| **T2** | exa (cloud MCP) | `web_search_exa` | 15s | 2 (5s, 10s) |
| **T3** | firecrawl:8015 | `firecrawl_search` → `firecrawl_scrape` | 30s | 1 (10s) |

**New MCP Tools to Add to Hub**:

| Tool | Purpose | Maps To |
|------|---------|---------|
| `search_tiered(query, tiers, force_tier, limit, entity_name)` | Unified SSP-V2 portal | SearchTriage state machine |
| `search_tier0_cache(query, entity_name, limit)` | Local cache check | SovereignCache + MemoryStore |
| `search_tier1_searxng(query, categories, engines, ...)` | Broad keyword discovery | SearXNG MCP via SovereignMCPClient |
| `search_tier2_exa(query, type, limit)` | Semantic/neural navigation | Exa cloud MCP via SovereignMCPClient |
| `search_tier3_firecrawl(query, url, limit, scrape)` | Deep extraction | Firecrawl MCP via SovereignMCPClient |

**Error Handling Strategy**:
```python
FALLBACK_CHAIN = {
    1: 2,   # SearXNG fails → try Exa
    2: 1,   # Exa fails → try SearXNG (broader keywords)
    3: 2,   # Firecrawl fails → try Exa for URL
}
```

---

### From P6 (Cognition) — Routing Intelligence Architecture

**Core Decision: Create `src/omega/oracle/search_router.py`** as a standalone module (NOT integrated into Oracle).

**The `SearchIntent` Dataclass** — contract between Oracle and search pipeline:

```python
@dataclass
class SearchIntent:
    primary_tier: int           # 0-4, recommended start tier
    max_tier: int = 4           # Maximum tier to escalate
    force_tier: Optional[int] = None  # Override
    query_category: str = "factual"   # factual|research|technical|academic|mining|casual
    search_depth: str = "standard"    # quick|standard|deep|exhaustive
    entity_name: Optional[str] = None
    domains: List[str] = field(default_factory=list)
    max_results: int = 10
    allow_cloud_search: bool = True
    credit_budget_firecrawl: int = 100
    signals_used: Dict[str, Any] = field(default_factory=dict)
    routing_reasoning: List[str] = field(default_factory=list)
```

**The `SearchRouter` Class** — 15 signals fused into tier decisions:

| Priority | Signal | Source | Maps To |
|----------|--------|--------|---------|
| 🔴 High | `has_url` | Regex on query | Force T3 (Firecrawl scrape) |
| 🔴 High | `iris_confidence` | Oracle | <0.2 → deep; 0.2-0.5 → standard; >0.6 → minimal |
| 🔴 High | `entity_domain` | EntityRegistry | research→T2; legacy→T1; general→T1 |
| 🔴 High | `query_category` | New classifier | factual→T1; research→T2; academic→T2 |
| 🔴 High | `credit_status` | APICreditBudget | Low credits → skip T3 |
| 🔴 High | `provider_health` | Circuit breakers | Down provider → skip its tier |
| 🟡 Medium | `query_length` | len(query) | Long → deeper search |
| 🟡 Medium | `has_technical_keywords` | Keyword match | T1 (GitHub) or T4 (Omega Hub) |
| 🟡 Medium | `search_depth_mode` | Config/flag | Overrides all other signals |
| 🟡 Medium | `query_complexity` | Inferred | deep → escalate depth |
| 🟢 Low | `channel` | cvar config | OpenCode→full; Gemini→offline |
| 🟢 Low | `has_soul_gnosis` | soul.yaml | Try T4 before external |

**Decision Rules** (highest priority wins):

```
1. has_url = true           → FORCE T3 (Firecrawl scrape)
2. confidence < 0.2 AND research domain → PRIORITY T2 (Exa neural)
3. confidence < 0.2 AND legacy domain   → PRIORITY T1 (SearXNG arXiv/GitHub)
4. confidence > 0.6         → NO SEARCH or T1 only
5. credits < 100             → SKIP T3 (Firecrawl)
6. provider down             → SKIP that tier
```

**Confidence → Search Depth Mapping**:

| Confidence | Search Depth | Tier Chain |
|------------|-------------|-----------|
| 0.9 (Iris) | None or T1 only | Iris responds |
| 0.5 (General) | Standard | T0 → T1 → T4 |
| 0.2 (Technical) | Deep | T0 → T1 → T2 → T3 → T4 |
| 0.0 (Abstract) | Exhaustive | T0 → T2 → T3 → T1 → T4 |

---

## §2 Unified Implementation Plan

### Phase 0: Prerequisites (Day 0 — Already Done)

| Step | Status | Owner |
|------|--------|-------|
| SearXNG container running on :8017 | ✅ Done | Infrastructure |
| SearXNG MCP server on :8018 | ✅ Done | P4 Integration |
| Firecrawl MCP server on :8015 | ✅ Done | P4 Integration |
| Exa MCP registered in opencode.json | ✅ Done | P4 Integration |
| Omega Hub with SovereignMCPClient | ✅ Done | P4 Integration |
| Existing `SovereignSearchService` | ✅ Done | P3 Engineering |

### Phase 1: Core Routing Infrastructure (Days 1-2)

**Goal**: Build `SearchRouter` + `SearchIntent` + `config/search.yaml` + tier re-alignment.

| Step | Task | Files | Effort | Owner |
|------|------|-------|--------|-------|
| 1.1 | Create `config/search.yaml` | New file | 0.5d | P6 Cognition |
| 1.2 | Create `SearchIntent` dataclass | `search_router.py` | 0.25d | P6 Cognition |
| 1.3 | Create `SearchRouter` with signal analysis | `search_router.py` | 1.5d | P6 Cognition |
| 1.4 | Create `SovereignCache` for `.firecrawl/` | `sovereign_cache.py` | 1d | P3 Engineering |
| 1.5 | Re-order tiers in SovereignSearchService | `sovereign_search_service.py` | 0.5d | P3 Engineering |
| 1.6 | Create `tests/test_search_triage.py` | New test file | 1d | P3 Engineering |
| 1.7 | Create `tests/test_sovereign_cache.py` | New test file | 0.5d | P3 Engineering |

**Phase 1 effort**: ~3-4 days

---

### Phase 2: SearXNG Integration + MCP Tools (Days 3-4)

**Goal**: Wire SearXNG as T1, add Hub MCP tools.

| Step | Task | Files | Effort | Owner |
|------|------|-------|--------|-------|
| 2.1 | Update `search_providers.py` with SearXNGProvider | `search_providers.py` | 0.5d | P3 Engineering |
| 2.2 | Create `SearXNGProvider(SearchProvider)` wrapper | `searxng_provider.py` | 0.5d | P3 Engineering |
| 2.3 | Update SovereignSearchService T1 to use SearXNG | `sovereign_search_service.py` | 0.5d | P3 Engineering |
| 2.4 | Add `search_tiered`, `search_tier1_searxng` to Hub | `mcp_servers/omega_hub/tools.py` | 1d | P4 Integration |
| 2.5 | Verify SearXNG MCP connectivity via SovereignMCPClient | `mcp_servers/omega_hub/mcp_client.py` | 0.5d | P4 Integration |
| 2.6 | Create `tests/test_searxng_provider.py` | New test file | 0.5d | P3 Engineering |
| 2.7 | Update `tests/test_search_tools.py` | Modify existing | 0.5d | P3 Engineering |

**Phase 2 effort**: ~2-3 days

---

### Phase 3: Exa + Firecrawl Re-alignment (Days 4-5)

**Goal**: Complete tier re-ordering, add T2/T3 Hub tools, credit-aware dispatch.

| Step | Task | Files | Effort | Owner |
|------|------|-------|--------|-------|
| 3.1 | Move Exa T4→T2, Firecrawl T2→T3 | `sovereign_search_service.py` | 0.5d | P3 Engineering |
| 3.2 | Wire credit-aware dispatch (skip T3 if credits < 100) | `sovereign_search_service.py` | 0.5d | P3 Engineering |
| 3.3 | Add `search_tier2_exa`, `search_tier3_firecrawl` to Hub | `mcp_servers/omega_hub/tools.py` | 1d | P4 Integration |
| 3.4 | Cache-back protocol: write `.firecrawl/` after T2/T3 | `sovereign_search_service.py` + `sovereign_cache.py` | 0.5d | P3 Engineering |

**Phase 3 effort**: ~1.5-2 days

---

### Phase 4: Fallback Manager + Error Hardening (Days 5-7)

**Goal**: Implement comprehensive error handling.

| Step | Task | Files | Effort | Owner |
|------|------|-------|--------|-------|
| 4.1 | Create `FallbackManager` with full error matrix | `fallback_manager.py` | 2d | P3 Engineering |
| 4.2 | Wire FallbackManager into SovereignSearchService | `sovereign_search_service.py` | 0.5d | P3 Engineering |
| 4.3 | Create `.opencode/firecrawl_wrapper.sh` | New shell script | 0.5d | P4 Integration |
| 4.4 | Create `tests/test_fallback_manager.py` | New test file | 1d | P3 Engineering |

**Phase 4 effort**: ~3-4 days

---

### Phase 5: Oracle Integration + Sovereing Gap Detector (Days 7-9)

**Goal**: Wire SSP-V2 into Oracle's confidence escalation and entity routing.

| Step | Task | Files | Effort | Owner |
|------|------|-------|--------|-------|
| 5.1 | Wire SearchIntent into search.py | `search.py` | 0.5d | P3 Engineering |
| 5.2 | Add search() public method on Oracle | `oracle.py` | 0.5d | P6 Cognition |
| 5.3 | Integrate confidence → search depth mapping | `oracle.py` + `search_router.py` | 0.5d | P6 Cognition |
| 5.4 | Integrate entity domain → tier profile | `search_router.py` | 0.5d | P6 Cognition |
| 5.5 | Create `SovereignGapDetector` for contrast loop | `sovereign_gap_detector.py` | 1.5d | P6 Cognition + P3 |
| 5.6 | Integrate gap detector into iterative_research.py | `iterative_research.py` | 0.5d | P3 Engineering |
| 5.7 | Add user override support (env vars + flag) | `search_router.py` + `oracle_cli.py` | 0.5d | P6 Cognition |

**Phase 5 effort**: ~3-4 days

---

### Phase 6: Observability + Testing + Hardening (Days 9-11)

**Goal**: Full test coverage, observability, temple-grade compliance.

| Step | Task | Files | Effort | Owner |
|------|------|-------|--------|-------|
| 6.1 | Add trace_id propagation + timing metrics per tier | `sovereign_search_service.py` | 0.5d | P3 Engineering |
| 6.2 | Add search latency to observability traces | `oracle.py`, `observability.py` | 0.5d | P6 Cognition |
| 6.3 | Create `tests/test_sspv2_integration.py` | New test file | 1d | P3 Engineering |
| 6.4 | Create `tests/verify_sspv2_pipeline.py` | Manual verification script | 0.5d | P3 Engineering |
| 6.5 | Run `make temple-grade` — fix any regressions | All | 1d | All |
| 6.6 | Update `SOVEREIGN_SEARCH_PROTOCOL_V2.md` | Documentation | 0.5d | P6 Cognition |

**Phase 6 effort**: ~2-3 days

---

### Total Effort

| Phase | Description | Effort | Dependencies |
|-------|-------------|--------|-------------|
| P1 | Core routing infrastructure | 3-4 days | None |
| P2 | SearXNG integration + MCP tools | 2-3 days | P1 |
| P3 | Exa/Firecrawl re-alignment | 1.5-2 days | P2 |
| P4 | Fallback + error hardening | 3-4 days | P3 |
| P5 | Oracle integration + Gap Detector | 3-4 days | P4 |
| P6 | Observability + testing + hardening | 2-3 days | P5 |
| **Total** | **Full SSP-V2** | **~11-15 days** | — |

---

## §3 File Manifest (Complete)

### 3.1 Files to Create (12)

```
src/omega/oracle/
├── search_router.py           # NEW: SearchRouter + SearchIntent (P6)
├── search_triage.py           # NEW: SearchTriage state machine (P3)
├── sovereign_cache.py         # NEW: .firecrawl/ cache manager (P3)
├── fallback_manager.py        # NEW: Error handling matrix (P3)
├── searxng_provider.py        # NEW: SearXNGProvider(SearchProvider) (P3)
├── sovereign_gap_detector.py  # NEW: L3 contrast loop (P6+P3)

config/
├── search.yaml                # NEW: SSP-V2 configuration (P6)

.opencode/
├── firecrawl_wrapper.sh       # NEW: Shell wrapper for key+limit mgmt (P4)

tests/
├── test_search_router.py      # NEW: SearchRouter signal tests (P6)
├── test_search_triage.py      # NEW: State machine transition tests (P3)
├── test_sovereign_cache.py    # NEW: Cache read/write/eviction tests (P3)
├── test_fallback_manager.py   # NEW: Error handler tests (P3)
├── test_searxng_provider.py   # NEW: SearXNG integration tests (P3)
├── test_sspv2_integration.py  # NEW: End-to-end SSP-V2 tests (P3)
├── verify_sspv2_pipeline.py   # NEW: Manual verification script (P3)
```

**Total create**: 7 Python + 1 YAML + 1 Shell + 7 Tests = **16 files**

### 3.2 Files to Modify (9)

```
src/omega/oracle/
├── sovereign_search_service.py # MODIFY: Tier re-order, integrate new modules
├── search_providers.py         # MODIFY: Add SearXNGProvider export
├── search.py                   # MODIFY: force_tier passthrough, richer return
├── oracle.py                   # MODIFY: SearchIntent integration
├── iterative_research.py       # MODIFY: Gap detector integration

mcp_servers/omega_hub/
├── tools.py                    # MODIFY: Add search_tiered + tier tools
├── mcp_client.py               # MODIFY: Verify Exa streamable-http support

tests/
├── test_search_tools.py        # MODIFY: Add SearXNG, update tier numbers

config/
├── providers.yaml              # MODIFY: Add SearXNG provider entry
```

### 3.3 Files to Deprecate (1-2)

```
tests/verify_sovereign_search.py  # Old tier numbering — replace with verify_sspv2_pipeline.py
```

---

## §4 Architecture Diagram (ASCII)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          OPENGODE MCP CLIENT                              │
│                    (discovers: omega-hub on :8016)                         │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                    OMEGA HUB MCP SERVER (:8016)                            │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │                      SSP-V2 Tools (NEW)                              │ │
│  │                                                                      │ │
│  │  search_tiered(query, tiers, force_tier, ...)                        │ │
│  │    ├── search_tier0_cache(query, entity, limit)                       │ │
│  │    ├── search_tier1_searxng(query, categories, ...)                   │ │
│  │    ├── search_tier2_exa(query, type, limit)                           │ │
│  │    └── search_tier3_firecrawl(query, url, limit)                      │ │
│  │                                                                      │ │
│  │  ┌──────────────────────────────────────────────────────────────┐   │ │
│  │  │  SearchRouter │ SearchIntent │ FallbackManager                │   │ │
│  │  │  • Signal fusion (15 signals)                                 │   │ │
│  │  │  • Entity domain profiles                                     │   │ │
│  │  │  • Confidence → depth mapping                                 │   │ │
│  │  │  • Credit-aware dispatch                                      │   │ │
│  │  └──────────────────────────────────────────────────────────────┘   │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │          SovereignMCPClient (EXISTING — AnyIO-native)                │ │
│  │                                                                      │ │
│  │  Tier 1: ────→  SearXNG MCP server (:8018) ───→ SearXNG (:8017)     │ │
│  │  Tier 2: ────→  Exa Cloud MCP (streamable-http)                      │ │
│  │  Tier 3: ────→  Firecrawl MCP server (:8015) ───→ Firecrawl API     │ │
│  │                                                                      │ │
│  │  T0: Local SovereignCache (.firecrawl/) + MemoryStore                │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │          Hivemind Communication (EXISTING)                            │ │
│  │  • [SEARCH-ERROR] format for tier failures                           │ │
│  │  • [CREDIT-LOW] format for credit exhaustion                         │ │
│  │  • trace_id propagation through entire search chain                  │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## §5 Verification Gates

| Gate | What to Check | How |
|------|---------------|-----|
| **T1 Success** | `search_tiered("python 3.13", force_tier=1)` returns SearXNG results | `verify_sspv2_pipeline.py --tier 1` |
| **T2 Success** | `search_tiered("neural network", force_tier=2)` returns Exa results | `verify_sspv2_pipeline.py --tier 2` |
| **T3 Success** | `search_tiered("https://example.com", force_tier=3)` returns Firecrawl scrape | `verify_sspv2_pipeline.py --tier 3` |
| **Failover** | SearXNG down → auto-fall back to Exa | `tests/test_fallback_manager.py` |
| **Credit Skip** | Firecrawl credits < 100 → auto-skip T3 | `pytest -k credit` |
| **Cache-back** | T2/T3 success → `.firecrawl/` populated | `pytest -k cache_back` |
| **Temple-Grade** | All T1-T11 gates pass | `make temple-grade` |
| **Test Suite** | All 440+ tests pass | `make test` |
| **Observability** | Search trace_id + tier log in observability events | Check event log |
| **M14 Heritage** | Any new heritage patterns carry `[id-soft:]` tags | `make heritage-map` |

---

## §6 Owner Assignment

| Module | Primary Owner | Review By |
|--------|--------------|-----------|
| `search_router.py` + `SearchIntent` | **P6 Cognition** | P3 Engineering |
| `sovereign_cache.py` | **P3 Engineering** | P4 Integration |
| `search_triage.py` | **P3 Engineering** | P6 Cognition |
| `fallback_manager.py` | **P3 Engineering** | P4 Integration |
| `searxng_provider.py` | **P3 Engineering** | P4 Integration |
| `sovereign_gap_detector.py` | **P6 Cognition + P3** | Kali Oversight |
| `firecrawl_wrapper.sh` | **P4 Integration** | P3 Engineering |
| `config/search.yaml` | **P6 Cognition** | P4 Integration |
| Hub MCP tools (`tools.py`) | **P4 Integration** | P3 Engineering |
| Oracle integration (`oracle.py`) | **P6 Cognition** | Kali Oversight |
| Tests + verification | **P3 Engineering** | Verity |
| Temple-grade enforcement | **Verity** | Kali Oversight |

---

## §7 Key Architectural Decisions

### Decision 1: Hub Integration over New Server
**Adopt Option 2** — add SSP-V2 tools to existing `mcp_servers/omega_hub/`. SovereignMCPClient + @m9_safe + existing tools make this the sovereign path. No new ports, no new systemd units.

### Decision 2: Retain SearXNGClient, Add Wrapper
Keep existing `SearXNGClient` in `workers/background_researcher/` for backward compatibility. Create `SearXNGProvider(SearchProvider)` wrapper that delegates to it.

### Decision 3: Re-number Tiers, Don't Re-key
Update `_execute_tier()` dispatch mapping. Old numeric tier references must have runtime translation with deprecation warnings.

### Decision 4: Remove Omega Hub from Search Chain
SSP-V2 doesn't include Omega Hub (Indexer) as a search tier. Keep it as a separate research tool (via IterativeResearcher) but remove from live SSP-V2 pipeline.

### Decision 5: SearchRouter Standalone (Not in Oracle)
The Oracle (780 lines) shouldn't absorb search routing. `SearchRouter` is a separate module with clear single responsibility, independently testable, usable by both Hub and Oracle.

### Decision 6: Credit-Aware Dispatch
Before T3 (Firecrawl), check `_has_firecrawl_credits(100)`. If below threshold, skip T3 and log `[CREDIT-LOW]` to Hivemind.

---

## §8 Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Tier re-ordering breaks existing callers | HIGH | Critical | Deprecation shim: log warnings for old tier numbers, map to correct tiers |
| SearXNG container not running | MEDIUM | High | Graceful connection error → cross-tier failover to Exa |
| Background researcher dependency on SearXNG | LOW | Low | Wrapping rather than replacing avoids conflicts |
| SearchRouter state machine complexity | MEDIUM | Medium | Use transitions table (not nested if/elif); write tests first |
| SovereignGapDetector LLM cost | LOW | Low | 1 call per search; batched or throttled |
| Hivemind noise from tier failure logs | MEDIUM | Medium | Aggregate logs per session, not per tier failure |

---

## §9 Current State (Before) vs Target State (After)

### Before SSP-V2
```
Oracle talks to Entity
  → Entity may or may not call IterativeResearcher
    → SovereignSearchService.search()
      → T0: MemoryStore (works)
      → T1: None (DEAD STUB)
      → T2: Firecrawl direct HTTP (wrong tier)
      → T3: Omega Hub Indexer (not a search tier)
      → T4: Exa direct HTTP (wrong tier)
    No query analysis, no tier intelligence, no credit awareness
```

### After SSP-V2
```
Oracle detects low confidence or research intent
  → SearchRouter analyzes 15 signals
    → SearchIntent produced (primary_tier, max_tier, search_depth)
    → SovereignSearchService.search(search_intent=intent)
      → T0: .firecrawl/ cache + MemoryStore + Qdrant (ENRICHED)
      → T1: SearXNG via MCP (FIXED)
      → T2: Exa via cloud MCP (RE-ORDERED)
      → T3: Firecrawl via MCP (RE-ORDERED, CREDIT-AWARE)
      → FallbackManager handles errors (NEW)
      → SovereignCache writes back after success (NEW)
    → Resuold returned with tier_used + fallback_log + evidence[]
    → Optionally passed to SovereignGapDetector for L3 contrast
```

---

## §10 Conclusion

SSP-V2 is **feasible and well-scoped**. The existing infrastructure (SearXNG container, MCP servers, SovereignSearchService, Oracle intent detection) provides a solid foundation. The gaps are:

1. **T1 dead stub** — needs SearXNG wiring (2-3 days)
2. **Tier numbering wrong** — needs re-alignment (1-2 days)
3. **No routing intelligence** — needs SearchRouter + SearchIntent (3-4 days)
4. **No cache layer** — needs SovereignCache (1-2 days)
5. **Weak error handling** — needs FallbackManager (2-3 days)
6. **No oracle integration** — needs confidence→search depth wiring (2-3 days)

**Total estimated effort**: 11-15 days across P3 (Engineering), P4 (Integration), and P6 (Cognition), with oversight from Kali and quality enforcement from Verity.

**The engine already has all the pieces. SSP-V2 is about wiring them together in the right order with the right intelligence.**

---

*⬡ OMEGA ⬡ PILLAR ⬡ SSP-V2 ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ SYNTHESIS-COMPLETE*

**Pillar Reports Referenced**:
- P3 Engineering: Code impact, file-by-file assessment, tier re-alignment
- P4 Integration: MCP architecture, Hub integration, SovereignMCPClient
- P6 Cognition: SearchRouter, SearchIntent, signal fusion, confidence→depth mapping
