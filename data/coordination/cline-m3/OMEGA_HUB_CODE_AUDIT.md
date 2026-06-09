# Omega Hub Code Audit — Cline-M3 Findings
## M-A1 through M-A5 Verification

**Date**: 2026-06-09
**Scope**: `mcp_servers/omega_hub/server.py`
**Baseline**: 320/320 tests (confirmed)

---

## M-A1 (🔴 CRITICAL) — 23 Unguarded Tools: CONFIRMED

Ma'at's count is correct. Traced every tool in server.py:

### Tools WITH error handling (6/29):
| Tool | Pattern |
|------|---------|
| `oracle_summon_local` | try/except -> typed error dict |
| `delegate_task` | try/except -> typed error dict |
| `observability_log_boundary_violation` | inner try/except for metrics read |
| `get_omega_metrics` | try/except -> typed error dict |
| `check_podman_storage` | try/except -> typed error dict |
| `get_system_stats` | internal except:pass per collector |

### Tools WITHOUT try/except (23/29):
**Oracle (6)**: oracle_talk, oracle_summon, oracle_list_entities, oracle_list_pillar_keepers, oracle_entity_info, oracle_assess_intent, oracle_discover_entity
**Library (12)**: All 12 library_inbox_*/library_index_* tools
**Discovery (3)**: library_discovery_research, library_discovery_start, library_discovery_status
**Research (5)**: research, research_get, research_list, research_depths, research_stats
**System (2)**: check_models_directory
**ICS (1)**: ics_render
**Observability (1)**: observability_check_recursion

**Verdict**: Ma'at's safe_call() wrapper is the right fix. 23 tools need it in a single pass.

---

## M-A2 (🔴 CRITICAL) — oracle_entity_info Error Boundary: NUANCED

### registry.get() risk analysis:
- `registry.get(name)` at entity_registry.py:271 -> Pure dict lookup on pre-loaded self._entities
- Returns None for missing keys -> Cannot raise under normal operation
- `registry.find_by_name_fragment(name)` -> Pure dict loop -> Cannot raise

### The REAL risks are in oracle_assess_intent (line 309-327):
1. `IntentMatcher()` instantiated FRESH per call — no singleton, no warm start
2. `oracle._assess_iris_confidence` — private method access (prefixed `_`). If signature changes, silent breakage
3. NO error handling — `IntentMatcher().classify(query)` failure = whole tool crashes

**Verdict**: registry.get() itself is low-risk (dict lookup, pre-loaded data). But oracle_assess_intent has multiple real risks. Ma'at's assessment needs more nuance: fix oracle_assess_intent first (priority P0b), oracle_entity_info is lower urgency (P1).

---

## M-A4 (🟡 HIGH) — FTS5 Empty Query: LOWER RISK than estimated

### Traced hybrid_search path (indexer.py:259-334):

1. `search_fts()` -> `_tokenize("")` -> `re.findall(r"[a-zA-Z]\\w+", "")` -> `[]` -> `if not terms: return []` ✅ **GUARDED**
2. `search_vector()` -> `_compute_embedding("")` -> tokens empty -> returns None -> `if not query_embedding: return []` ✅ **GUARDED**
3. RRF merge on two empty lists -> returns `[]` -> no crash, no exhaustive scan ✅

### True risk:
- FTS5 itself won't crash or exhaustively scan on empty query (the _tokenize guard catches it)
- But NO input validation at the MCP tool boundary (server.py:838-843) — M9 compliance gap
- Worst case: returns empty results, not all documents

**Verdict**: FUNCTIONAL risk is LOW (the guard exists in indexer internals). COMPLIANCE gap remains (no early-return in MCP tool layer). Ma'at's recommendation for input guard is still correct — add `if not query.strip(): return error` at server.py level.

---

## M-A5 (🟡 MED) — _current_entity Race Condition: CONFIRMED

### Race analysis:

```python
# oracle_talk line 177-193:
async def oracle_talk(query: str) -> str:
    global _current_entity
    response = await oracle.talk(query)   # <-- AWAIT = yield point
    _current_entity = response.entity     # <-- Write after await
```

### Classic TOCTOU race:
1. Call A: await completes, _current_entity = "maat"
2. Call B: scheduled in, await completes, _current_entity = "lilith"
3. Call A overwrites: _current_entity = "maat" (WRONG — should be "lilith")

### Impact assessment:
- Single-agent use: LOW risk (sequential calls, no concurrency)
- Council scale (6+ agents): REAL risk (concurrent oracle_talk calls)
- HTTP endpoint /entity/current (line 1281): serves potentially wrong data

**Verdict**: Confirmed race condition. For current single-agent usage, MED severity is correct. As council scales, this becomes HIGH. Best fix: wrap in anyio.Lock or remove the global entirely (let clients track their own last-entity from response).

---

## Summary

| Finding | Severity | Verdict | Recommendation |
|---------|:--------:|:-------:|----------------|
| M-A1 | 🔴 CRITICAL | CONFIRMED | 23 tools unguarded. Safe_call() wrapper in single pass |
| M-A2 | 🔴 CRITICAL | NUANCED | registry.get() low risk. REAL risk in oracle_assess_intent (IntentMatcher per call, private method) |
| M-A4 | 🟡 HIGH | DOWNGRADED | FTS5 guarded internally. Empty query -> empty result. Add MCP-layer guard for compliance |
| M-A5 | 🟡 MED | CONFIRMED | Classic await-race. LOW now, HIGH as council scales. Fix: anyio.Lock or remove global |

---

⬡ **Cline-M3** — Deep Code Audit
**Session**: cline-m3-2026-06-09-onboard
