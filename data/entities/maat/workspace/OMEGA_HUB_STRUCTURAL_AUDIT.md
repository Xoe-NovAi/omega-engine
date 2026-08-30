<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Hub Structural Audit — Ma'at (P1-P5 Governance)
# ⬡ OMEGA ⬡ MA'AT ⬡ deepseek-v4-flash ⬡ trc_maat ⬡ OMEGA-HUB-HARDENING

**Date**: 2026-06-09
**Scope**: Oracle, Library, Research, Discovery, ICS tool domains in `mcp_servers/omega_hub/server.py` (1448 lines)
**Baseline**: 320/320 tests passing
**Status**: 🟡 STRUCTURAL — 8 findings, 2 CRITICAL, 3 HIGH, 3 MED

---

## §0 — Tool Inventory Reconciliation

### Briefing says 47 tools across 6 domains. Actual count:

| Domain | Briefing Claims | Actual Count | Delta |
|--------|----------------|--------------|-------|
| Oracle | 7 | **8** | +1 (oracle_summon_local counted as separate) |
| Hivemind | 11 | **11** | ✅ Match |
| Library | 11 | **12** | +1 (library_index_flush exists but was omitted) |
| Discovery | (in Library) | **3** | Not counted separately in briefing |
| Research | 5 | **5** | ✅ Match |
| Observability | 2 | **2** | ✅ Match |
| Stats | 4 | **4** | ✅ Match |
| ICS | 1 | **1** | ✅ Match |
| Delegation | 1 | **1** | ✅ Match |
| **Total** | 47 | **47** | ✅ Match |

**Minor doc drift**: Section header at line 784 says `=== LIBRARY TOOLS (12) ===` — briefing says 11. Not a functional issue, but Lilith should note.

### Actual Tool Catalog (Oracle + Library + Research audited here)

**Oracle (8 tools)**: `oracle_talk`, `oracle_summon`, `oracle_summon_local`, `oracle_list_entities`, `oracle_list_pillar_keepers`, `oracle_entity_info`, `oracle_assess_intent`, `oracle_discover_entity`

**Library (12 tools)**: `library_inbox_add_url`, `library_inbox_add_note`, `library_inbox_add_file`, `library_inbox_list`, `library_inbox_stats`, `library_ingest_pending`, `library_search`, `library_get_document`, `library_domains`, `library_stats`, `library_recent`, `library_index_flush`

**Discovery (3 tools)**: `library_discovery_research`, `library_discovery_start`, `library_discovery_status`

**Research (5 tools)**: `research`, `research_get`, `research_list`, `research_depths`, `research_stats`

**ICS (1 tool)**: `ics_render`

---

## §1 — Finding M-A1 🔴 CRITICAL: Inconsistent Error Handling (M9 Violation)

### Location: All tool endpoints — `server.py:176-1269`

### Observation
Error handling is inconsistent across the 29 non-Hivemind tools:

| Pattern | Tools Using It | Count |
|---------|---------------|-------|
| **Has try/except → typed error dict** | `oracle_summon_local`, `delegate_task`, `observability_log_boundary_violation`, `get_omega_metrics`, `check_podman_storage` | 5 |
| **Has try/except internally (acceptably)** | `get_system_stats` (stats collector — all `except: pass`) | 1 |
| **NO try/except — relies on FastMCP** | **All remaining 23 tools** (all 8 Oracle except summon_local, all 12 Library, all 3 Discovery, all 5 Research, ics_render, check_models_directory, observability_check_recursion) | **23** |

### Impact
FastMCP will catch exceptions and return an MCP error to the client, but:
- Errors are **not typed** (no `OmegaError` subtypes per M9)
- Errors **don't carry trace_id** — debugging requires correlation from client logs
- Errors are **inconsistent** — some tools return structured `{"error": "..."}` dicts, others let raw exceptions propagate
- **Mandate 9** requires: *"Every public API boundary MUST catch and convert internal errors to OmegaError subtypes"*

### Example inconsistencies
```python
# oracle_summon_local (line 226): HAS try/except, returns structured error
try:
    response = await oracle.summon(entity_name, query, model_override=model)
except Exception as e:
    return json.dumps({"error": str(e), "entity": entity_name, ...})

# oracle_talk (line 177): NO try/except — raw exception to MCP layer
response = await oracle.talk(query)

# library_search (line 839): NO try/except — empty query crashes FTS5?
results = await indexer.hybrid_search(query, domain=domain_filter, limit=limit)
```

### Recommendation
Add `_safe_call()` wrapper pattern to all public MCP tools (both Oracle and Library domains):
```python
async def _safe_call(coro, tool_name, **context):
    try:
        result = await coro
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        trace_id = new_trace_id()
        logger.error(f"[{tool_name}] {trace_id}: {e}")
        return json.dumps({
            "error": str(e),
            "trace_id": trace_id,
            "tool": tool_name,
            **context
        }, indent=2)
```

Apply to all unguarded tools in a single pass. This is a uniform M9 compliance fix.

---

## §2 — Finding M-A2 🔴 CRITICAL: oracle_entity_info Has No Error Boundary Around Registry Calls

### Location: `oracle_entity_info` — `server.py:283-306`

### Observation
```python
def _get():
    return registry.get(name) or registry.find_by_name_fragment(name)
entity = await anyio.to_thread.run_sync(_get)
if not entity:
    return json.dumps({"error": f"Entity '{name}' not found"})
```

If `registry.get(name)` raises (e.g., connection issue reading YAML, corrupt entity data), the exception propagates uncaught. `find_by_name_fragment` (line 655-665) is a pure dict lookup and won't raise, but `registry.get()` could.

### Impact
A corrupt entity file in `data/entities/` would crash the MCP tool entirely — not just return a graceful error.

### Worse: `oracle_assess_intent` (line 310-327)
```python
def _assess():
    from omega.iris.matcher import IntentMatcher  # local import
    classification = IntentMatcher().classify(query)  # NEW IntentMatcher() every call
    domain_entity = registry.find_by_domain(query)
    iris_confidence = oracle._assess_iris_confidence(query)  # private method access
```

Three concerns:
1. **Fresh IntentMatcher** per call — no singleton, no warm start. Could be slow if IntentMatcher loads models/resources.
2. **Private method access** — `oracle._assess_iris_confidence` prefixed with `_` signals internal use. If the method signature changes, this breaks silently.
3. **No error handling** — if `IntentMatcher().classify()` fails, entire tool crashes.

### Recommendation
1. Add try/except to `oracle_entity_info` and `oracle_assess_intent`
2. Export `_assess_iris_confidence` as a public method or add a public wrapper
3. Cache IntentMatcher instance across calls (or lazy-init with warm state)

---

## §3 — Finding M-A3 🟡 HIGH: oracle_discover_entity Domain Matching Has No Empty-Input Guard

### Location: `oracle_discover_entity` — `server.py:330-346`

### Observation
```python
entity = registry.find_by_domain(query)
if not entity:
    return json.dumps({"error": "No matching entity found for this domain."})
```

`find_by_domain` at `entity_registry.py:613-652` does:
```python
words = set(text_lower.split())
for keyword in projected.domains:
    kw_lower = keyword.lower()
    if kw_lower in words or f" {kw_lower} " in f" {text_lower} ":
```

If `query` is empty string (`""`):
- `text_lower.split()` → `[]` (empty set)
- The space-bounded matching `` f" {kw_lower} " in f"  " `` → evaluates correctly (fails to match)
- Returns `None` → tool returns `{"error": "No matching entity found for this domain."}`
- **This works correctly** for empty input ✅

### However
If `projected.domains` contains an empty string (config error in entities.yaml):
- `kw_lower in words` → `"" in set()` → `False`
- `f"  " in f" {text_lower} "` → **this is `"  " in " something "` → evaluates to True** because the two-space string IS in the padded text
- Minor edge case, requires entity config with empty domain string

### Recommendation
Add `if not query.strip(): return json.dumps({"error": "Empty query."})` guard at top, and strip empty domains in entity_registry validation.

---

## §4 — Finding M-A4 🟡 HIGH: Library Search Passes Empty Query to FTS5

### Location: `library_search` — `server.py:838-843`

### Observation
```python
async def library_search(query: str, domain: str = "", limit: int = 20) -> str:
    domain_filter = domain if domain else None
    results = await indexer.hybrid_search(query, domain=domain_filter, limit=limit)
```

If `query=""` is passed:
- FTS5 empty string query behavior varies by tokenizer
- Worst case: returns all documents (exhaustive scan)
- Best case: returns empty results

**No input validation on `query`** — neither MCP tool layer nor `indexer.hybrid_search` checks for empty/whitespace-only queries.

### Similarly: `library_inbox_add_url(url, ...)` — no URL format validation
An empty or malformed URL goes directly to `inbox.add_url()` which may fail silently or crash later during curation.

### Recommendation
Add input guards:
```python
if not query.strip():
    return json.dumps({"error": "Search query cannot be empty", "count": 0, "results": []})
```
Apply similar guards to `library_inbox_add_url`, `library_inbox_add_file`.

---

## §5 — Finding M-A5 🟡 MED: Global `_current_entity` Is Ephemeral

### Location: `_current_entity` — `server.py:106`

### Observation
```python
_current_entity: Optional[str] = None  # Tracks the last entity used by oracle_talk/oracle_summon
```

This global is:
1. **In-memory only** — lost on server restart
2. **Race-prone** — two concurrent oracle_talk calls would overwrite each other's `_current_entity`
3. **Leaked abstraction** — the HTTP endpoint `/entity/current` serves this value, but it can be wrong under concurrent load

### Impact
Under concurrent access (e.g., two agents querying Orion simultaneously), `/entity/current` could return entity A's value while the actual last call was entity B.

### Recommendation
Either:
- Remove `_current_entity` tracking from the MCP layer (let clients track their own last-entity)
- Or store it per-call in the response (it's already in `oracle_talk` and `oracle_summon` JSON output)

---

## §6 — Finding M-A6 🟡 MED: library_stats Calls indexer.stats() Which Could Raise

### Location: `library_stats` — `server.py:862-868`

### Observation
```python
async def library_stats() -> str:
    stats = await library.stats()
    idx_stats = indexer.stats()
    stats["index"] = idx_stats
    return json.dumps(stats, indent=2)
```

If `library.stats()` returns normally but `indexer.stats()` raises (e.g., SQLite connection issue), the exception propagates uncaught. The index stats enriching happens outside the library's error boundary.

### Recommendation
Wrap `indexer.stats()` in try/except or move the enrichment into `library.stats()` so it's atomically guarded.

---

## §7 — Finding M-A7 🟢 MED: Briefing Document Drift on Tool Counts

- Briefing says "Oracle (7 tools)" — actual: 8 (oracle_summon_local is an 8th Oracle tool)
- Briefing says "Library (11 tools)" — actual: 12 (library_index_flush is 12th)
- Doc at `server.py:784` says `=== LIBRARY TOOLS (12) ===` which is correct

This is a non-functional finding but affects the accuracy of sprint documentation.

---

## §8 — Finding M-A8 🟢 MED: library_discovery_research Docstring Says "blocking" But It's Async

### Location: `library_discovery_research` — `server.py:895-902`

```python
@mcp.tool()
async def library_discovery_research(query: str, depth: int = 2) -> str:
    """Execute the tiered external discovery pipeline (Gemini -> Exa -> Brave -> Tavily).

    Returns a consolidated discovery report. Note: This is synchronous/blocking.
    """
    report = await discovery.discover(query, depth=depth)
```

The docstring says "synchronous/blocking" but the function is `async` and uses `await`. The actual `discovery.discover()` call is awaited, so it's non-blocking. Docstring is misleading — agents may avoid calling it thinking it blocks.

### Recommendation
Remove "Note: This is synchronous/blocking" from docstring. Replace with "Async — non-blocking."

---

## §9 — Top 3 Findings to Seed Lilith

As the briefing instructs: *"Seed Lilith with your top 3 issues."*

### 🔴 #1 — M-A1: Inconsistent Error Handling (M9 Violation)
**23 of 29 tools lack try/except.** Error types, trace_ids, and messages are inconsistent. M9 mandates typed `OmegaError` subtypes at every public API boundary. FastMCP's default error handler is not enough — errors propagate without trace_ids, making debugging impossible across the fleet.

**Action for Lilith**: Check if Hivemind handoff tools follow the same pattern or if they have proper error boundaries. The handoff queue (`hivemind_submit_handoff`, `hivemind_accept_handoff`, `hivemind_complete_handoff`) uses `fcntl.flock` for atomicity but the MCP wrapper itself has no try/except. If a flock operation fails (e.g., NFS mount, permissions), the raw exception reaches the client.

### 🔴 #2 — M-A2: oracle_entity_info Has No Error Boundary
**Pure-dict-lookup-assuming code path.** If `registry.get()` raises or entity data is corrupt, the tool crashes. Requires only a 5-line fix (add try/except), but the impact is severe — agents depend on `oracle_entity_info` to discover council members.

**Action for Lilith**: Apply same error boundary analysis to `hivemind_get_session` and `hivemind_get_continuation` — these also do file I/O that could raise.

### 🟡 #3 — M-A5: `_current_entity` Global Is Ephemeral and Race-Prone
**In-memory global loses state on restart, overwrites under concurrency.** Not immediately blocking for single-agent use, but as the council scales to 6+ agents, concurrent MCP calls will corrupt this value. The HTTP endpoint `/entity/current` serves potentially wrong data.

**Action for Lilith**: Validate whether Hivemind's `_awareness` and `_hot_store` dicts have similar race/volatility concerns. They use `_AsyncThreadLock` (threading.Lock) for cross-event-loop safety, but the pattern isn't applied to `_current_entity`.

---

## §10 — Test Suite Confirmation

```
OMEGA_ENV=test PYTHONPATH=src python3 -m pytest tests/ -x -q
320 passed in 24.23s
```

No regressions. Baseline is clean.

---

## §11 — Summary

| # | Domain | Severity | Description |
|---|--------|----------|-------------|
| M-A1 | All | 🔴 CRITICAL | Inconsistent error handling — 23/29 tools lack try/except (M9 violation) |
| M-A2 | Oracle | 🔴 CRITICAL | oracle_entity_info / oracle_assess_intent have no error boundary |
| M-A3 | Oracle | 🟡 HIGH | discover_entity has no empty-input guard at MCP tool layer |
| M-A4 | Library | 🟡 HIGH | library_search passes empty query to FTS5 — no input validation |
| M-A5 | Global | 🟡 MED | _current_entity is ephemeral, race-prone, lost on restart |
| M-A6 | Library | 🟡 MED | library_stats calls indexer.stats() outside error boundary |
| M-A7 | Doc | 🟢 MED | Briefing tool count drift (Oracle 7→8, Library 11→12) |
| M-A8 | Discovery | 🟢 MED | library_discovery_research docstring says "blocking" but it's async |

---

⬡ **Ma'at** — Build Side Oversoul (P1-P5)
**Next**: Seed Lilith with the top 3 findings above.

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
