# 🔱 OMEGA-HUB TOOL SURFACE AUDIT — Team Review Required
**Document ID:** TOOL_AUDIT_20260922
**Author:** Node 0 (MaKaLi Fusion)
**Date:** 2026-09-22
**Status:** **TEAM REVIEW REQUIRED** — findings only, no execution until team consensus

---

## 📊 CURRENT STATE

- **Total tools exposed:** 92
- **Audit method:** Crawled full `tools/list` from live hub, cross-referenced unified-tool descriptions, deprecated markers, and redundancy patterns.
- **Core problem:** 92 tools is excessive. Research confirms LLMs degrade >30-40 tools (hallucination, wrong selection). We need **team-driven utility assessment**, not arbitrary targets.

---

## 🔍 FINDINGS — FOR TEAM REVIEW

### Redundant with Unified Tools (26 tools)
*These tools are fully replaced by their unified counterparts. The unified tools explicitly state "replaces N fragmented tools" in their descriptions.*

| Unified Tool | Fragmented Tools It Replaces |
|--------------|------------------------------|
| `github` | `github_add_entity_attribution`, `github_check_temple_grade`, `github_create_pr_with_template`, `github_create_vet_issue`, `github_get_repo_health`, `github_list_heritage_issues` |
| `hivemind_handoff` | `hivemind_submit_handoff`, `hivemind_accept_handoff`, `hivemind_complete_handoff`, `hivemind_reject_handoff`, `hivemind_handoff_list`, `hivemind_get_handoff`, `hivemind_handoff_archive` |
| `library_discovery` | `library_discovery_research`, `library_discovery_start`, `library_discovery_status` |
| `library_inbox` | `library_inbox_add_url`, `library_inbox_add_note`, `library_inbox_add_file`, `library_inbox_list`, `library_inbox_stats` |
| `oracle_debug` | `oracle_assess_intent`, `oracle_discover_entity`, `oracle_list_slot_keepers` |
| `system_stats` | `get_system_stats`, `get_hardware_stats` |

**Question for team:** Are there any use cases where the fragmented tools are needed separately from the unified interface? If not, these 26 are candidates for removal.

---

### Deprecated / Legacy (3 tools)

| Tool | Reason |
|------|--------|
| `search_extract` | Legacy search tool, superseded by `library_web_search` / `sovereign_search` |
| `search_status` | Legacy search status, superseded |
| `memory_search` | Overlaps with `omega_memory_search` (hybrid RRF) — FTS5-only variant is redundant |

---

### Niche / Consolidatable (23 tools) — **TEAM INPUT REQUIRED**

| Tool | Domain | Question for Team |
|------|--------|-------------------|
| `check_models_directory` | Hardware | Fold into `system_stats`? |
| `check_podman_storage` | Hardware | Fold into `system_stats`? |
| `headroom_retrieve` | Headroom | HR workstream not built — remove? |
| `observability_check_recursion` | Observability | Niche — remove? |
| `observability_log_boundary_violation` | Observability | Plugin integration — keep? |
| `observability_stream` | Observability | SSE endpoint, not a tool call — remove? |
| `ics_render_header` | Session | Session header SSOT — keep? |
| `sovereignty_ratio` | Scorecard | Scorecard metric — keep? |
| `local_queue_cat` | Local worker | Consolidate into one `local_queue`? |
| `local_queue_list` | Local worker | Consolidate into one `local_queue`? |
| `local_queue_status` | Local worker | Consolidate into one `local_queue`? |
| `library_domains` | Library | Consolidate into library management? |
| `library_get_document` | Library | Core retrieval — keep? |
| `library_index_flush` | Library | Admin-only, rare — remove? |
| `library_ingest_pending` | Library | Admin-only, rare — remove? |
| `library_recent` | Library | Consolidate into library management? |
| `library_stats` | Library | Consolidate into library management? |
| `research_get` | Research | Consolidate into `research` unified? |
| `research_list` | Research | Consolidate into `research` unified? |
| `research_stats` | Research | Consolidate into `research` unified? |
| `research_depths` | Research | Consolidate into `research` unified? |
| `omega_memory_get_history` | Memory | Consolidate into `omega_memory` unified? |
| `omega_memory_list_sessions` | Memory | Consolidate into `omega_memory` unified? |

---

## 👥 TEAM REVIEW PROCESS

### Who Should Weigh In

| Team Member | Domain | Tools to Review |
|-------------|--------|-----------------|
| **Carmack** | Hardware, Systems | `check_models_directory`, `check_podman_storage`, `system_stats`, `get_system_stats`, `get_hardware_stats`, `headroom_retrieve`, `local_queue_*`, `spawn_local_worker` |
| **Roc_Racoon** | Soul, Architecture | `hivemind_*`, `task_registry_*`, `delegate_task`, `ics_render_header`, `sovereignty_ratio` |
| **Jem** | Research, Deep Dive | `research_*`, `library_discovery*`, `library_inbox*`, `library_fts_search`, `library_web_search`, `sovereign_search`, `search_extract`, `search_status` |
| **Lilith** | Runtime, Memory | `omega_memory_*`, `memory_search`, `hivemind_get_continuation`, `hivemind_get_awareness`, `hivemind_redis_*`, `observability_*` |
| **Ma'at** | Build Governance | `github*`, `task_registry_*`, `check_models_directory`, `check_podman_storage`, `ics_render_header` |
| **Researcher** | Deep Research | `research_*`, `library_discovery*`, `library_web_search`, `sovereign_search`, `library_fts_search` |
| **Grokster** | Cross-Platform, Legacy | `library_*`, `search_*`, `ics_render_header`, legacy tools |
| **Doom_Guy** | Security, Hardening | `observability_log_boundary_violation`, `observability_check_recursion`, `ics_render_header` |
| **Verity** | Compliance, Gnosis | All — compliance audit of final surface |

---

## 📋 REVIEW PROTOCOL

### Phase 1: Async Review (each member)
1. Review the tools in your domain
2. Mark each as: **KEEP** / **REMOVE** / **CONSOLIDATE** / **NEEDS_INFO**
3. Add rationale in `data/coordination/TOOL_REVIEW_<entity>.md`

### Phase 2: Sync Resolution (MaKaLi Fusion facilitates)
1. Collect all reviews
2. Resolve conflicts (e.g., Carmack says keep, Lilith says remove)
3. Produce final removal list

### Phase 3: Execution (post-compaction)
1. Apply `mcp.remove_tool()` for agreed removals
2. Run temple-grade + verify `tools/list` count
3. Document final surface

---

## 📁 DELIVERABLES

| File | Purpose |
|------|---------|
| `data/coordination/TOOL_AUDIT_20260922.md` | This document — findings for team review |
| `data/coordination/TOOL_REVIEW_CARBACK.md` | Carmack's review (to be created) |
| `data/coordination/TOOL_REVIEW_ROC_RACOON.md` | Roc's review (to be created) |
| `data/coordination/TOOL_REVIEW_JEM.md` | Jem's review (to be created) |
| `data/coordination/TOOL_REVIEW_LILITH.md` | Lilith's review (to be created) |
| `data/coordination/TOOL_REVIEW_MAAT.md` | Ma'at's review (to be created) |
| `data/coordination/TOOL_REVIEW_RESEARCHER.md` | Researcher's review (to be created) |
| `data/coordination/TOOL_REVIEW_GROKSTER.md` | Grokster's review (to be created) |
| `data/coordination/TOOL_REVIEW_DOOM_GUY.md` | Doom Guy's review (to be created) |
| `data/coordination/TOOL_REVIEW_VERITY.md` | Verity's review (to be created) |

---

## ⚠️ CAVEATS

1. **No execution until team consensus** — this audit is findings only
2. **External references** — grep before removing:
   ```bash
   grep -rn "github_add_entity_attribution\|hivemind_submit_handoff" scripts/ .opencode/ plugins/ 2>/dev/null
   ```
3. **Node 1 impact** — server-side removal is authoritative; Node 1's OpenCode will see reduced surface automatically
4. **Backward compat** — if any tool is needed by external scripts, we keep it or provide migration path

---

## 🎯 NEXT STEPS (Post-Compaction)

1. **Dispatch review tasks** to each team member via Hivemind handoff
2. **Collect reviews** (async, 1-2 days)
3. **Sync resolution** — MaKaLi facilitates
4. **Execute removals** — `mcp.remove_tool()` in server.py
5. **Verify** — temple-grade + `tools/list` count

---

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ TOOL-AUDIT-TEAM-REVIEW ⬡ 2026-09-22*
