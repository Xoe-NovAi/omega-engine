# 🔱 OMEGA-HUB TOOL SURFACE AUDIT — Prioritized Removal Candidates
**Document ID:** TOOL_AUDIT_20260922
**Author:** Node 0 (MaKaLi Fusion)
**Date:** 2026-09-22
**Status:** FINDINGS ONLY — execution deferred post-compaction

---

## 📊 CURRENT STATE

- **Total tools exposed:** 92
- **Target:** ~50 (per Operator directive — "nearly a hundred tools is ridiculous")
- **Audit method:** Crawled full `tools/list` from live hub, cross-referenced unified-tool descriptions, deprecated markers, and usage patterns.

---

## 🎯 PRIORITIZED REMOVAL LIST

### P0 — REDUNDANT (26 tools) — replaced by unified tools

These tools are **fully replaced** by their unified counterparts. Keeping both doubles the surface for zero benefit.

| # | Tool to Remove | Replaced By |
|---|----------------|-------------|
| 1 | `github_add_entity_attribution` | `github` (action=add_entity_attribution) |
| 2 | `github_check_temple_grade` | `github` (action=check_temple_grade) |
| 3 | `github_create_pr_with_template` | `github` (action=create_pr) |
| 4 | `github_create_vet_issue` | `github` (action=create_vet_issue) |
| 5 | `github_get_repo_health` | `github` (action=get_repo_health) |
| 6 | `github_list_heritage_issues` | `github` (action=list_heritage_issues) |
| 7 | `hivemind_submit_handoff` | `hivemind_handoff` (action=submit) |
| 8 | `hivemind_accept_handoff` | `hivemind_handoff` (action=accept) |
| 9 | `hivemind_complete_handoff` | `hivemind_handoff` (action=complete) |
| 10 | `hivemind_reject_handoff` | `hivemind_handoff` (action=reject) |
| 11 | `hivemind_handoff_list` | `hivemind_handoff` (action=list) |
| 12 | `hivemind_get_handoff` | `hivemind_handoff` (action=get) |
| 13 | `hivemind_handoff_archive` | `hivemind_handoff` (action=archive) |
| 14 | `library_discovery_research` | `library_discovery` (action=research) |
| 15 | `library_discovery_start` | `library_discovery` (action=start) |
| 16 | `library_discovery_status` | `library_discovery` (action=status) |
| 17 | `library_inbox_add_url` | `library_inbox` (action=add_url) |
| 18 | `library_inbox_add_note` | `library_inbox` (action=add_note) |
| 19 | `library_inbox_add_file` | `library_inbox` (action=add_file) |
| 20 | `library_inbox_list` | `library_inbox` (action=list) |
| 21 | `library_inbox_stats` | `library_inbox` (action=stats) |
| 22 | `oracle_assess_intent` | `oracle_debug` (action=assess_intent) |
| 23 | `oracle_discover_entity` | `oracle_debug` (action=discover_entity) |
| 24 | `oracle_list_slot_keepers` | `oracle_debug` (action=list_slot_keepers) |
| 25 | `get_system_stats` | `system_stats` (detail=summary) |
| 26 | `get_hardware_stats` | `system_stats` (detail=hardware) |

**Impact:** 92 → 66

---

### P1 — DEPRECATED / LEGACY (3 tools)

| # | Tool to Remove | Reason |
|---|----------------|--------|
| 27 | `search_extract` | Legacy search tool, superseded by `library_web_search` / `sovereign_search` |
| 28 | `search_status` | Legacy search status, superseded |
| 29 | `memory_search` | Overlaps with `omega_memory_search` (hybrid RRF) — FTS5-only variant is redundant |

**Impact:** 66 → 63

---

### P2 — NICHE / CONSOLIDATABLE (23 tools) — evaluate for removal or consolidation

| # | Tool | Recommendation |
|---|------|----------------|
| 30 | `check_models_directory` | **Fold into** `system_stats` — hardware check |
| 31 | `check_podman_storage` | **Fold into** `system_stats` — hardware check |
| 32 | `headroom_retrieve` | **Remove** — niche, HR workstream not yet built |
| 33 | `observability_check_recursion` | **Remove** — niche, rarely used |
| 34 | `observability_log_boundary_violation` | **Keep** — plugin integration |
| 35 | `observability_stream` | **Remove** — SSE endpoint, not a tool call |
| 36 | `ics_render_header` | **Keep** — session header SSOT |
| 37 | `sovereignty_ratio` | **Keep** — scorecard metric |
| 38 | `local_queue_cat` | **Consolidate** into one `local_queue` tool |
| 39 | `local_queue_list` | **Consolidate** into one `local_queue` tool |
| 40 | `local_queue_status` | **Consolidate** into one `local_queue` tool |
| 41 | `library_domains` | **Consolidate** into `library` management |
| 42 | `library_get_document` | **Keep** — core retrieval |
| 43 | `library_index_flush` | **Remove** — admin-only, rare |
| 44 | `library_ingest_pending` | **Remove** — admin-only, rare |
| 45 | `library_recent` | **Consolidate** into `library` management |
| 46 | `library_stats` | **Consolidate** into `library` management |
| 47 | `research_get` | **Consolidate** into `research` unified |
| 48 | `research_list` | **Consolidate** into `research` unified |
| 49 | `research_stats` | **Consolidate** into `research` unified |
| 50 | `research_depths` | **Consolidate** into `research` unified |
| 51 | `omega_memory_get_history` | **Consolidate** into `omega_memory` unified |
| 52 | `omega_memory_list_sessions` | **Consolidate** into `omega_memory` unified |

**P2 removal (not consolidation): 8 tools** → 63 → 55
**P2 consolidation (fold into unified): 15 tools** → 55 → 40 (if all consolidated)

---

## ✅ CORE KEEP (39 tools)

| Group | Tools |
|-------|-------|
| **Hivemind core** | `hivemind_post_context`, `hivemind_heartbeat`, `hivemind_get_awareness`, `hivemind_get_continuation`, `hivemind_get_entity_context`, `hivemind_get_metrics`, `hivemind_get_session`, `hivemind_list_sessions`, `hivemind_extended_checkin`, `hivemind_extended_checkout`, `hivemind_redis_publish`, `hivemind_redis_subscribe`, `hivemind_workspace_lock_acquire`, `hivemind_workspace_lock_check`, `hivemind_workspace_lock_release`, `hivemind_handoff` |
| **Library** | `library_discovery`, `library_inbox`, `library_fts_search`, `library_web_search` |
| **Oracle** | `oracle_debug`, `oracle_list_entities`, `oracle_entity_info`, `oracle_talk`, `oracle_summon`, `oracle_summon_local` |
| **Federation** | `omega_federation_status`, `omega_federation_diagnose` |
| **Memory** | `omega_memory_search` |
| **Research** | `research`, `sovereign_search` |
| **System** | `system_stats`, `spawn_local_worker`, `delegate_task` |
| **GitHub** | `github` |
| **Task Registry** | `task_registry_register`, `task_registry_query`, `task_registry_update`, `task_registry_get` |

---

## 📈 PROJECTED SURFACE

| Scenario | Tool Count |
|----------|-----------|
| Current | 92 |
| After P0 (redundant removed) | 66 |
| After P0+P1 (deprecated removed) | 63 |
| After P0+P1+P2-removal (niche removed) | **55** |
| After full P2 consolidation | **40** |

**Recommended target: 55** (remove 37 tools) — aggressive but safe. Full consolidation to 40 can follow in a later sprint.

---

## 🛠️ IMPLEMENTATION NOTES (for post-compaction execution)

### Removal mechanism
The official `mcp` SDK FastMCP exposes `remove_tool(name)`. Pattern already proven with `library_search`:
```python
# In mcp_servers/omega_hub/server.py, after tool registration:
for _tool in [
    "github_add_entity_attribution", "github_check_temple_grade", ...
]:
    try:
        mcp.remove_tool(_tool)
    except Exception:
        logger.warning("remove_tool(%s) failed (non-fatal)", _tool)
```

### Consolidation mechanism
For P2 consolidations, keep the unified tool and remove the fragments (same as P0 pattern).

### Verification
```bash
# After restart:
curl -s -X POST http://127.0.0.1:8016/mcp -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | jq '.result.tools | length'
# Expect: 55
```

---

## ⚠️ CAVEATS

1. **Backward compat:** Some tools may be referenced by external scripts/plugins. Grep before removing:
   ```bash
   grep -rn "github_add_entity_attribution\|hivemind_submit_handoff" scripts/ .opencode/ plugins/ 2>/dev/null
   ```
2. **Node 1 impact:** Node 1's OpenCode will see the reduced surface automatically after restart (no client-side filtering needed — server-side removal is authoritative).
3. **MCP tool count vs LLM quality:** Research confirms LLMs degrade >30-40 tools (hallucination, wrong selection). 55 is still above ideal; 40 is the long-term target.

---

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ TOOL-AUDIT ⬡ 2026-09-22 ⬡ FINDINGS-ONLY*