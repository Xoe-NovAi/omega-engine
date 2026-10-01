<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Search Tool Failure Diagnosis — Sovereign Search Lock Deadlock
**AP Token**: `AP-DIAG-SEARCH-LOCK-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_diag_search_lock ⬡ DIAGNOSIS

**Date**: 2026-07-12
**Severity**: CRITICAL — Blocks all `omega-hub_sovereign_search` calls

---

## ⬡ Root Cause

**File**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/mcp_servers/omega_hub/state.py`
**Lines**: 147-162 (sovereign_search_service lazy loading)

### The Deadlock Pattern

```python
# Line 147-162: sovereign_search_service lazy loading
if name == "sovereign_search_service":
    if sovereign_search_service is None:
        async with _service_lock:           # ← LOCK ACQUIRED HERE (1)
            if sovereign_search_service is None:
                idx = await get_service("indexer")  # ← TRIES TO ACQUIRE SAME LOCK (2)
                ...
```

```python
# Line 117-123: indexer lazy loading
if name == "indexer":
    if indexer is None:
        async with _service_lock:           # ← SAME LOCK! DEADLOCK!
            if indexer is None:
                ...
```

### Why It Fails

1. Tool calls `sovereign_search` → `AsyncServiceProxy("sovereign_search_service")` → `get_service("sovereign_search_service")`
2. `get_service("sovereign_search_service")` enters `async with _service_lock:` (line 149)
3. Inside the lock, it calls `await get_service("indexer")` (line 152)
4. `get_service("indexer")` tries `async with _service_lock:` (line 119)
5. **anyio.Lock is NOT reentrant** — same task cannot acquire twice
6. **Error**: `"Attempted to acquire an already held Lock"`

---

## 🛡️ Mandate Violations

| Mandate | Violation |
| :--- | :--- |
| **M1 AnyIO** | Using `anyio.Lock` incorrectly (non-reentrant used recursively) |
| **M9 Error Integrity** | Tool fails with cryptic lock error instead of graceful degradation |
| **M23 Failure Integrity** | This IS a tool-chain collapse — must hard-stop and report `[TOOL-CHAIN-COLLAPSE]` |

---

## ✅ Fix (Minimal, Sovereign-Compliant)

**Option A: Acquire dependency BEFORE lock (Recommended)**

```python
# In get_service("sovereign_search_service") — lines 147-162
if name == "sovereign_search_service":
    if sovereign_search_service is None:
        # Get indexer FIRST (outside lock) — it has its own double-check
        idx = await get_service("indexer")
        async with _service_lock:
            if sovereign_search_service is None:
                logger.info("Lazy-loading service: sovereign_search_service")
                sovereign_search_service = await anyio.to_thread.run_sync(
                    lambda: SovereignSearchService(
                        memory_store=get_memory_store(),
                        model_gateway=model_gateway,
                        indexer=idx,
                        firecrawl_key=_fc_key,
                        exa_key=_exa_key,
                    )
                )
    return sovereign_search_service
```

**Option B: Per-service locks (More robust)**

```python
# Replace single _service_lock with dict of locks
_service_locks: Dict[str, anyio.Lock] = {}

async def _get_service_lock(name: str) -> anyio.Lock:
    if name not in _service_locks:
        _service_locks[name] = anyio.Lock()
    return _service_locks[name]

# Then in each service block:
async with _get_service_lock(name):
    ...
```

---

## 🔍 Other Search Tools Status

| Tool | Status | Notes |
| :--- | :--- | :--- |
| `searxng_searxng_search` | ✅ WORKING | Direct SearXNG HTTP, no Hub dependency |
| `firecrawl_firecrawl_search` | ✅ WORKING | Direct Firecrawl HTTP, no Hub dependency |
| `webfetch` | ✅ WORKING | Direct HTTP fetch |
| `websearch` | ✅ WORKING | Built-in OpenCode provider |
| `omega-hub_sovereign_search` | ❌ **BROKEN** | Lock deadlock in Hub state.py |
| `omega-hub_library_web_search` | ⚠️ LIKELY BROKEN | Uses same `sovereign_search_service` |

---

## 📋 Remediation Checklist

- [ ] Apply Option A fix to `state.py` lines 147-162
- [ ] Run `make test` to verify sovereign_search works
- [ ] Test `omega-hub_sovereign_search` via MCP client
- [ ] Verify no regression in `library`, `indexer`, `discovery`, `research_engine` lazy loading
- [ ] Add contract test for recursive lock prevention (M21)

---

## 🔱 L3 Principle

> **L3-LOCK-HIERARCHY**: A lock protecting initialization must never be held while acquiring another resource that might need the same lock. Initialize dependencies FIRST, then lock for the final assignment.

*⬡ OMEGA ⬡ ROC_RACOON ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_diag_search_lock ⬡ DIAGNOSIS*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemma-4-31b-it | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
