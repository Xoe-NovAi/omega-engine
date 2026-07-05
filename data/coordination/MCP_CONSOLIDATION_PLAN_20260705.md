# 🔱 MCP Tool Consolidation Plan
## 70 → ~39 Tools: Eliminating Bloat and Naming Confusion

**AP Token**: `AP-MCP-CONSOLIDATION-v1.0.0`
**Date**: 2026-07-05
**Author**: Sovereign Master Researcher
**Status**: PLAN (Awaiting Approval)

---

## Executive Summary

The Omega Hub has **70 MCP tools** — nearly double what's needed. The bloat comes from:
1. **Handoff CRUD**: 7 tools for file operations (submit/accept/complete/reject/list/get/archive)
2. **Inbox CRUD**: 5 tools for intake (add_url/add_note/add_file/list/stats)
3. **Discovery**: 3 tools for background jobs (research/start/status)
4. **Naming confusion**: `library_search` does **web search**, not library search

This plan consolidates 70 → ~39 tools by merging CRUD operations into action-based dispatchers.

---

## Critical Issue: `library_search` Naming

**Current behavior**: `library_search` calls `sovereign_search_service.search()` — the **web search** pipeline (SearXNG → Exa → Firecrawl). It does NOT search the local Library FTS5 index.

**Why this is dangerous**: An agent calling `library_search("circuit breaker")` expects local knowledge base results. It gets web search results instead. The agent thinks it searched the library but actually hit the internet.

**Fix**: Rename to `library_web_search` and clarify `library_fts_search` as the local search.

---

## Consolidation Plan

### 1. Handoff CRUD → `hivemind_handoff` (7 → 1 tool)

**Current** (7 tools):
```
hivemind_submit_handoff(target_channel, target_entity, source_channel, source_entity, task, context, priority)
hivemind_accept_handoff(packet_id, accepting_channel, accepting_entity)
hivemind_complete_handoff(packet_id, result)
hivemind_reject_handoff(packet_id, reason)
hivemind_handoff_list(status)
hivemind_get_handoff(packet_id)
hivemind_handoff_archive(packet_ids)
```

**Proposed** (1 tool):
```python
@mcp.tool()
async def hivemind_handoff(
    action: str,  # "submit" | "accept" | "complete" | "reject" | "list" | "get" | "archive"
    packet_id: str = "",
    # Submit params
    target_channel: str = "",
    target_entity: str = "",
    source_channel: str = "",
    source_entity: str = "",
    task: str = "",
    context: str = "",
    priority: int = 0,
    # Accept params
    accepting_channel: str = "",
    accepting_entity: str = "",
    # Complete/Reject params
    result: str = "",
    reason: str = "",
    # List params
    status: str = "",
    # Archive params
    packet_ids: List[str] = [],
) -> str:
```

**Dispatch logic**: Switch on `action` parameter, validate required params per action, delegate to existing internal functions.

**Savings**: -6 tools

### 2. Inbox CRUD → `library_inbox` (5 → 1 tool)

**Current** (5 tools):
```
library_inbox_add_url(url, tags, priority)
library_inbox_add_note(text, tags)
library_inbox_add_file(path, tags)
library_inbox_list(limit)
library_inbox_stats()
```

**Proposed** (1 tool):
```python
@mcp.tool()
async def library_inbox(
    action: str,  # "add_url" | "add_note" | "add_file" | "list" | "stats"
    url: str = "",
    text: str = "",
    path: str = "",
    tags: str = "",
    priority: int = 0,
    limit: int = 20,
) -> str:
```

**Savings**: -4 tools

### 3. Discovery → `library_discovery` (3 → 1 tool)

**Current** (3 tools):
```
library_discovery_research(query, depth)
library_discovery_start(query)
library_discovery_status(job_id)
```

**Proposed** (1 tool):
```python
@mcp.tool()
async def library_discovery(
    action: str,  # "research" | "start" | "status"
    query: str = "",
    depth: int = 2,
    job_id: str = "",
) -> str:
```

**Savings**: -2 tools

### 4. Rename `library_search` → `library_web_search`

**Current**: `library_search` — misleading name, does web search
**Proposed**: `library_web_search` — clear that it hits the internet

Keep `library_fts_search` as-is — it's the local knowledge search.

**Savings**: 0 tools (rename only, but eliminates confusion)

### 5. Merge Stats Tools (7 → 4)

**Current** (7 tools):
```
get_system_stats
get_hardware_stats
get_omega_metrics
check_models_directory
check_podman_storage
hivemind_get_metrics
observability_check_recursion
```

**Proposed** (4 tools):
```
get_system_stats(detail: str = "overview")  # "overview" | "hardware" | "full"
get_omega_metrics
hivemind_get_metrics
observability_check_recursion
```

Drop `check_models_directory` and `check_podman_storage` — these are one-off operational checks that belong in CLI, not MCP tools.

**Savings**: -3 tools

### 6. Merge Oracle Tools (9 → 6)

**Current** (9 tools):
```
oracle_talk
oracle_summon
oracle_summon_local
oracle_list_entities
oracle_list_pillar_keepers  ← redundant
oracle_entity_info
oracle_assess_intent        ← debug-only
oracle_discover_entity
headroom_retrieve
```

**Proposed** (6 tools):
```
oracle_talk
oracle_summon
oracle_summon_local
oracle_list_entities(filter: str = "")  # adds "pillars" filter
oracle_entity_info
oracle_debug(action: str)  # "assess_intent" | "discover_entity"
```

Drop `headroom_retrieve` — it's a compression utility, not an oracle tool. Merge `list_pillar_keepers` into `list_entities` with filter. Merge `assess_intent` + `discover_entity` into `oracle_debug`.

**Savings**: -3 tools

---

## Final Tool Count

| Category | Before | After | Savings |
|----------|:------:|:-----:|:-------:|
| Hivemind | 20 | 14 | -6 |
| Library | 15 | 7 | -8 |
| Oracle | 9 | 6 | -3 |
| Stats | 7 | 4 | -3 |
| Search | 3 | 3 | 0 |
| Memory | 4 | 3 | -1 |
| Research | 5 | 5 | 0 |
| Observability | 2 | 2 | 0 |
| ICS | 1 | 1 | 0 |
| Delegation | 1 | 1 | 0 |
| GitHub | 6 | 2 | -4 |
| **TOTAL** | **70** | **48** | **-22** |

Wait — that's 48, not 39. Let me recalculate with the GitHub consolidation.

Actually, let me recount. The hivemind consolidation saves 6 (20→14), not 12. Let me be more precise:

| Category | Before | After |
|----------|:------:|:-----:|
| Hivemind | 20 | 14 (6 core + 1 handoff + 8 lock/session) |
| Library | 15 | 7 |
| Oracle | 9 | 6 |
| Stats | 7 | 4 |
| Search | 3 | 3 |
| Memory | 4 | 3 |
| Research | 5 | 5 |
| Observability | 2 | 2 |
| ICS | 1 | 1 |
| Delegation | 1 | 1 |
| GitHub | 6 | 2 |
| **TOTAL** | **70** | **48** |

Hmm, still 48. Let me look at the hivemind tools more carefully — there might be more consolidation possible.

Actually, looking at the hivemind tools again:
- 6 core (post_context, heartbeat, get_awareness, get_continuation, get_entity_context, get_metrics)
- 1 handoff (consolidated from 7)
- 3 lock (acquire, release, check) → could be 1 with action param
- 2 extended (checkin, checkout) → could drop these
- 2 session (get_session, list_sessions) → could be 1 with action param

If I consolidate locks (3→1) and sessions (2→1), that's:
- 6 core + 1 handoff + 1 lock + 1 session = 9 hivemind tools (down from 20)

That gives us: 9 + 7 + 6 + 4 + 3 + 3 + 5 + 2 + 1 + 1 + 2 = 43

Let me refine this further. The user said "merge as you see fit" so I should be aggressive.

Actually, let me just write the plan as-is and present it to the user. The key consolidations are:
1. Handoff 7→1
2. Inbox 5→1
3. Discovery 3→1
4. library_search → library_web_search (rename)
5. Stats 7→4
6. Oracle 9→6
7. Lock 3→1
8. Session 2→1

That should get us to ~43 tools. Let me write the final plan.</think><tool_call>
<function=write>
<parameter=content># 🔱 MCP Tool Consolidation Plan
## 70 → ~43 Tools: Eliminating Bloat and Naming Confusion

**AP Token**: `AP-MCP-CONSOLIDATION-v1.0.0`
**Date**: 2026-07-05
**Author**: Sovereign Master Researcher
**Status**: PLAN — Awaiting User Approval Before Execution

---

## Problem Statement

The Omega Hub has **70 MCP tools**. This is excessive because:
1. **Handoff CRUD**: 7 separate tools for file operations (submit/accept/complete/reject/list/get/archive)
2. **Inbox CRUD**: 5 separate tools for intake (add_url/add_note/add_file/list/stats)
3. **Discovery**: 3 separate tools for background jobs (research/start/status)
4. **Lock CRUD**: 3 separate tools (acquire/release/check)
5. **Session CRUD**: 2 separate tools (get/list)
6. **Naming confusion**: `library_search` does **web search**, not library search — this is a trap

---

## Critical Fix: `library_search` Naming

**Current**: `library_search` calls `sovereign_search_service.search()` — the **web search** pipeline (SearXNG → Exa → Firecrawl). It does NOT search the local Library FTS5 index.

**Danger**: An agent calling `library_search("circuit breaker")` expects local knowledge base results. It gets web search results instead. The agent thinks it searched the library but actually hit the internet.

**Fix**: Rename to `library_web_search`. Keep `library_fts_search` as the local knowledge search.

---

## Consolidation Details

### 1. Handoff CRUD → `hivemind_handoff` (7 → 1)

Merge 7 handoff tools into one action-based dispatcher:

```python
@mcp.tool()
async def hivemind_handoff(
    action: str,          # "submit" | "accept" | "complete" | "reject" | "list" | "get" | "archive"
    packet_id: str = "",  # required for accept/complete/reject/get
    # Submit params
    target_channel: str = "",
    target_entity: str = "",
    source_channel: str = "",
    source_entity: str = "",
    task: str = "",
    context: str = "",
    priority: int = 0,
    # Accept params
    accepting_channel: str = "",
    accepting_entity: str = "",
    # Complete/Reject params
    result: str = "",
    reason: str = "",
    # List params
    status: str = "",
    # Archive params
    packet_ids: List[str] = [],
) -> str:
```

Internal dispatch: `if action == "submit": ...` delegates to existing `_submit_handoff()` logic.

**Eliminated tools**: `hivemind_submit_handoff`, `hivemind_accept_handoff`, `hivemind_complete_handoff`, `hivemind_reject_handoff`, `hivemind_handoff_list`, `hivemind_get_handoff`, `hivemind_handoff_archive`

### 2. Inbox CRUD → `library_inbox` (5 → 1)

```python
@mcp.tool()
async def library_inbox(
    action: str,          # "add_url" | "add_note" | "add_file" | "list" | "stats"
    url: str = "",
    text: str = "",
    path: str = "",
    tags: str = "",
    priority: int = 0,
    limit: int = 20,
) -> str:
```

**Eliminated tools**: `library_inbox_add_url`, `library_inbox_add_note`, `library_inbox_add_file`, `library_inbox_list`, `library_inbox_stats`

### 3. Discovery → `library_discovery` (3 → 1)

```python
@mcp.tool()
async def library_discovery(
    action: str,          # "research" | "start" | "status"
    query: str = "",
    depth: int = 2,
    job_id: str = "",
) -> str:
```

**Eliminated tools**: `library_discovery_research`, `library_discovery_start`, `library_discovery_status`

### 4. Lock CRUD → `hivemind_workspace_lock` (3 → 1)

```python
@mcp.tool()
async def hivemind_workspace_lock(
    action: str,          # "acquire" | "release" | "check"
    domain: str = "",
    holder: str = "",
) -> str:
```

**Eliminated tools**: `hivemind_workspace_lock_acquire`, `hivemind_workspace_lock_release`, `hivemind_workspace_lock_check`

### 5. Session CRUD → `hivemind_session` (2 → 1)

```python
@mcp.tool()
async def hivemind_session(
    action: str,          # "get" | "list"
    session_id: str = "",
    channel: str = "",
    entity: str = "",
    limit: int = 20,
) -> str:
```

**Eliminated tools**: `hivemind_get_session`, `hivemind_list_sessions`

### 6. Rename `library_search` → `library_web_search`

Rename only. No logic change. Eliminates the naming trap.

### 7. Merge Stats → `get_system_stats` (7 → 4)

```python
@mcp.tool()
async def get_system_stats(
    detail: str = "overview",  # "overview" | "hardware" | "full"
) -> str:
```

Merge `get_system_stats` + `get_hardware_stats` into one with `detail` param. Drop `check_models_directory` and `check_podman_storage` (one-off CLI checks, not MCP tools).

**Eliminated tools**: `get_hardware_stats`, `check_models_directory`, `check_podman_storage`

### 8. Merge Oracle → (9 → 6)

- Merge `oracle_list_pillar_keepers` into `oracle_list_entities` (add `filter="pillars"` param)
- Merge `oracle_assess_intent` + `oracle_discover_entity` into `oracle_debug(action="assess_intent"|"discover_entity")`
- Drop `headroom_retrieve` from oracle category (it's a compression utility, belongs elsewhere)

---

## Final Count

| Category | Before | After | Saved |
|----------|:------:|:-----:|:-----:|
| Hivemind | 20 | 12 | -8 |
| Library | 15 | 7 | -8 |
| Oracle | 9 | 6 | -3 |
| Stats | 7 | 4 | -3 |
| Search | 3 | 3 | 0 |
| Memory | 4 | 3 | -1 |
| Research | 5 | 5 | 0 |
| Observability | 2 | 2 | 0 |
| ICS | 1 | 1 | 0 |
| Delegation | 1 | 1 | 0 |
| GitHub | 6 | 2 | -4 |
| **TOTAL** | **70** | **46** | **-24** |

---

## Backward Compatibility

The old tool names will NOT be removed immediately. Instead:

1. **Phase 1**: Add new consolidated tools (`hivemind_handoff`, `library_inbox`, etc.)
2. **Phase 2**: Add deprecation warnings to old tools (log a warning when called)
3. **Phase 3**: After 2 sprint cycles, remove deprecated tools

This prevents breaking any existing agent code that references old tool names.

---

## Files to Modify

| File | Changes |
|------|---------|
| `mcp_servers/omega_hub/tools.py` | Add 8 new consolidated tools, add deprecation to 24 old tools, rename `library_search` |
| `tests/test_hub_health.py` | Update tool count assertion (70 → 46+) |
| `tests/test_hivemind_integration.py` | Add tests for consolidated handoff/lock/session tools |
| `tests/test_library_fts_search.py` | No changes needed |
| `docs/reference/api/library_fts_search.md` | Update tool names |
| `docs/llms-full.txt` | Update tool names |

---

## Execution Order

1. Write the 8 new consolidated tools
2. Add deprecation warnings to old tools
3. Rename `library_search` → `library_web_search`
4. Update tests
5. Run full test suite
6. Update documentation

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Breaking existing agent code | Backward-compatible: old tools still work, just warn |
| Action param typo | Validate action param against allowed values, return clear error |
| Test regression | Run full suite after each change |
| Documentation drift | Update docs in same PR |

---

*🔱 OMEGA ⬡ RESEARCHER ⬡ MCP-CONSOLIDATION-PLAN ⬡ v1.0.0 ⬡ AWAITING-APPROVAL*
