# 🔱 Roc Racoon — Session Gnosis (2026-07-12)
**AP Token**: `AP-ROC_RACOON-GNOSIS-20260712`
⬡ OMEGA ⬡ ROC_RACOON ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_search_fixes ⬡ GNOSIS

---

## 🗃️ RAW INTAKE LOG

### [ARCH] Search Tool Deadlock Diagnosis
**Timestamp**: 2026-07-12 16:00
**Context**: User reported `omega-hub_sovereign_search` failing with "Attempted to acquire an already held Lock"
**Investigation**: Traced through `mcp_servers/omega_hub/state.py` lazy-loading chain
**Finding**: Recursive `anyio.Lock` acquisition — `sovereign_search_service` held lock while calling `get_service("indexer")` which also needed the same lock

### [ARCH] Fix Implementation
**Timestamp**: 2026-07-12 16:15-17:30
**Actions**: 
1. Moved dependency resolution outside locks in `state.py` (2 services)
2. Added module-level globals for API keys
3. Added `health_monitor` property to ModelGateway
4. Added gateway to lazy-loader
5. Fixed `search_status` tool attribute access

### [ARCH] Verification
**Timestamp**: 2026-07-12 17:30
**Result**: MCP client calls to `sovereign_search` and `library_web_search` return successful SearXNG (T1) results
**Evidence**: `trace_id: srch_398c9a19068c` with 10 results, status=success

### [BURN] SSE Transport Issue
**Timestamp**: 2026-07-12 17:45
**Issue**: Server process runs but doesn't bind to port 8016
**Status**: Deferred — separate from search tool fixes

---

## 🧠 L1 → L2 → L3 DISTILLATION

### L1 (Narrative)
Fixed a recursive lock deadlock in the Omega Hub's service lazy-loader that prevented all search tools from working. The deadlock occurred because `anyio.Lock` is not reentrant, and the `sovereign_search_service` initialization tried to acquire the same lock twice (once directly, once via `get_service("indexer")`). Applied minimal fixes to 3 files, verified search works via MCP client.

### L2 (Insight)
The lazy-loading pattern in `state.py` uses a single global `_service_lock` for all services, but some services have dependencies on other lazy-loaded services. This creates a classic lock ordering problem. The fix is to resolve dependencies BEFORE acquiring the lock, not inside it. This pattern appears in at least 2 services (`sovereign_search_service` and `research_engine`).

### L3 (Universal Principle)
**L3-LOCK-HIERARCHY**: A lock protecting initialization must never be held while acquiring another resource that might need the same lock. Initialize dependencies FIRST, then lock for the final assignment.

**L3-SEARCH-RESILIENCE**: Search pipeline must degrade gracefully — T1 (SearXNG) works without any API keys; T2/T3 are optional enhancements. The system correctly falls back to available tiers.

**L3-MCP-TRANSPORT-SEPARATION**: MCP server transport (SSE/Streamable HTTP) is orthogonal to tool logic. Tools work in-process; transport issues are a separate configuration layer.

---

## 📋 PROPOSED LESSONS (for soul.yaml)

```yaml
proposals:
  - L1: "Fixed recursive anyio.Lock deadlock in Hub service lazy-loader by moving dependency resolution outside lock scope"
    L2: "Single global lock for all lazy-loaded services creates lock ordering problems when services depend on each other"
    L3: "L3-LOCK-HIERARCHY: Initialize dependencies BEFORE acquiring initialization lock; never hold lock while acquiring dependent resources"
    tags: [arch, concurrency, deadlock, anyio]
    confidence: 0.95
    
  - L1: "Sovereign Search (SSP-V2) works with T1 (SearXNG) alone — no API keys required for basic operation"
    L2: "Tiered search protocol correctly degrades: T0 local cache → T1 SearXNG (free) → T2 Exa (paid) → T3 Firecrawl (paid)"
    L3: "L3-SEARCH-RESILIENCE: Design systems to work at minimum viable tier; paid tiers are enhancements, not requirements"
    tags: [search, resilience, sovereignty, tiered-architecture]
    confidence: 0.9
    
  - L1: "MCP tool logic and transport are separable — tools tested in-process before SSE server was running"
    L2: "FastMCP tool decorators (`@mcp.tool()`) execute in-process; transport (SSE/Streamable HTTP) is just the wire protocol"
    L3: "L3-MCP-TRANSPORT-SEPARATION: Test tool logic independently of transport; transport issues don't invalidate tool correctness"
    tags: [mcp, testing, architecture, transport]
    confidence: 0.85
```

---

## 🔗 CROSS-REFERENCES

- **Diagnosis Doc**: `docs/diagnostics/DIAG_SEARCH_LOCK_DEADLOCK_20260712.md`
- **Anchored Summary**: `.opencode/anchored-summary.md`
- **Modified Files**: 
  - `mcp_servers/omega_hub/state.py` (lock fix, globals, gateway loader)
  - `src/omega/oracle/model_gateway.py` (health_monitor property)
  - `mcp_servers/omega_hub/tools.py` (search_status fix)
- **Related Work**: 
  - Sovereign Search Protocol v2 (SSP-V2) in `src/omega/oracle/sovereign_search_service.py`
  - MCP Hub modularization in `mcp_servers/omega_hub/`
  - ModelGateway provider fabric in `src/omega/oracle/model_gateway.py`

---

## 🎯 NEXT SESSION PRIORITIES

1. **Debug SSE Transport**: `src/omega/mcp_runtime.py` `run_mcp()` not binding to port 8016
2. **Fix Provider Errors**: Ollama 404, RemoteProvider `session_id` TypeError
3. **Add API Keys**: Firecrawl/Exa for T2/T3 search tiers
4. **Run Full Test Suite**: `make test` to verify no regressions

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_search_fixes ⬡ GNOSIS*