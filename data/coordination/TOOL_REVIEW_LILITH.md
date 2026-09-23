# 🌊 TOOL REVIEW — LILITH (Slots S8-S10: Runtime)

**Reviewer:** Lilith — Runtime Oversoul (S8 Observability, S9 Orchestration, S10 Validation)
**Date:** 2026-09-22
**Source audit:** `TOOL_AUDIT_20260922.md` (92 tools)
**Scope:** Memory / Runtime / Telemetry — 12 tools assigned + 2 audit-assigned extras
**Method:** Live `tools/list` crawl (92 confirmed) + source inspection of `mcp_servers/omega_hub/hub_tools/tools.py` + `src/omega/memory_store.py` + caller grep across scripts/, .opencode/, plugins/, ~/.config/opencode/plugin/
**Mode:** REVIEW ONLY — no server code modified.

---

## Verdict Table

| Tool | Verdict | Rationale |
|------|---------|-----------|
| `omega_memory_search` | **KEEP** | Canonical sovereign memory retrieval — hybrid RRF (FTS5+Vector) is the single search entry. Core of knowledge metabolism (M11). |
| `omega_memory_get_history` | **KEEP** | Distinct operation (session history read); no unified `omega_memory` tool exists — this IS the surface. Needed for continuity (M15). |
| `omega_memory_list_sessions` | **KEEP** | Distinct operation (session enumeration); required to locate resumable sessions (M15 continuity). |
| `memory_search` | **REMOVE** | FTS5-only is a strict subset of `omega_memory_search` — hybrid RRF internally calls `search_fts` (verified `memory_store.py:323-361`). Redundant; audit already marks deprecated. |
| `hivemind_redis_publish` | **KEEP** | Ephemeral awareness layer (heartbeats, live-feed deltas); M23-degradable to file-based Hivemind; federation playbook depends on it. NOTE: currently degraded — Redis auth-gated (`NOAUTH`) and `OMEGA_REDIS_HOST` unset. |
| `hivemind_redis_subscribe` | **KEEP** | Matched read-side of the ephemeral bus; bounded listen (M23-compliant, never blocks). Same degraded-state note as publish. |
| `hivemind_get_metrics` | **KEEP** | S8 observability core — coordination health (awareness, handoffs, locks, sessions); generates on the fly if metrics.json absent. |
| `hivemind_get_session` | **KEEP** | Only path to session snapshots (hot store + HALL_OF_RECORDS cold fallback). FLAG: `_deprecated()` marker points to `hivemind_session(action='get')` which **does not exist** — stale marker, fix the deprecation string, do not remove the tool. |
| `hivemind_list_sessions` | **KEEP** | Only Hivemind session enumeration (channel/entity filters). FLAG: same phantom `hivemind_session` deprecation marker — stale, fix string only. |
| `observability_check_recursion` | **KEEP** | Heritage-tagged (M14, doom_guy HERITAGE_VET_LOG), canonical MCP exposure of `SovereignHierarchy.check_recursion()` (hierarchy.py:129-153), cited in CANONICAL_KNOWLEDGE_BASE. S9 orchestration guard for M17 cognitive integrity. No live callers today — wire into `subagent_dispatcher` flow or revisit. |
| `observability_log_boundary_violation` | **KEEP** | Design-correct M8 zero-telemetry channel for Engine-Stack Firewall (M1/M2) violation logging → `data/logs/metrics.json`. Plugin does NOT currently call it (grep verified) — the tool is the contract; wire the plugin or it stays dormant. |
| `observability_stream` | **REMOVE** | Confirmed: returns a static SSE endpoint URL (`/obs/stream`) — discovery metadata, not a callable operation. LLM agents cannot consume SSE push streams via MCP request/response. Keep the endpoint; move discovery to docs. |

### Supplementary (audit-assigned to Lilith, outside the 12-task scope)

| Tool | Verdict | Rationale |
|------|---------|-----------|
| `hivemind_get_awareness` | **KEEP** | Step 1 of the coordination protocol (verify target availability); cold-store hydration on restart. Core hivemind function. |
| `hivemind_get_continuation` | **KEEP** | M15 sovereign continuity — the continuation-note read path; cold-store fallback (D-kal-051). Core. |

---

## Memory architecture

**Current surface (6 tools → 4):** `omega_memory_search`, `omega_memory_get_history`, `omega_memory_list_sessions`, `memory_search` (+ `omega_memory_list_sessions`/`get_history` are not duplicated anywhere).

**Recommended memory surface — exactly 3 tools:**

1. `omega_memory_search` — the **single search entry**. Hybrid RRF (BM25 + vector) subsumes FTS5; verified at `memory_store.py:323-361` that the hybrid path internally calls `search_fts` as one leg. One search tool, one mental model.
2. `omega_memory_get_history` — session history read (per entity + session_id).
3. `omega_memory_list_sessions` — session enumeration for continuity/resume.

**Why NOT a unified `omega_memory` action-param tool:** the audit floats "consolidate into `omega_memory` unified?" — but no such unified tool exists, and these three are already the minimal coherent surface (search / read / enumerate). Folding them into one action-param tool would save 2 slots at the cost of discoverability and would break the established per-operation naming that matches the MemoryStore API 1:1. The 3-tool surface is the right size.

**`memory_search` verdict rationale (REMOVE):**
- Strict functional subset: `omega_memory_search` = RRF(FTS5, Vector); `memory_search` = FTS5 only. Every result `memory_search` can return, `omega_memory_search` can return with equal-or-better ranking.
- The "no vector overhead" argument is negligible at this scale and the wrong trade for an LLM agent — hybrid recall is strictly more useful for knowledge metabolism.
- **Grep-before-removal caveat (audit §Caveats 2):** `memory_search` is referenced in `src/omega/search/search_persistence.py` (tier mapping, lines 407/463) and `.opencode/plans/SSP_V2_IMPLEMENTATION.md` — these references must be updated to `omega_memory_search` when the tool is removed.

**Continuity note (M15):** `hivemind_get_session` / `hivemind_list_sessions` are the only Hivemind snapshot accessors. Their `_deprecated()` markers reference a **nonexistent** `hivemind_session` unified tool — this is a stale marker bug, not a replacement. Fix the deprecation strings (or drop the markers) in the same pass that removes other tools; do NOT remove the tools themselves.

**Ephemeral bus note:** `hivemind_redis_publish/subscribe` are currently degraded — local Redis answers `NOAUTH Authentication required` and `OMEGA_REDIS_HOST` is unset. They degrade gracefully to `status="unavailable"` (M23-compliant), so they are safe to keep; validate the pair once federation Redis auth is configured (see `data/federation/usb-payload/redis/REDIS_FED_CONFIG_20260922.md`).

---

## Summary

**Counts (12 assigned tools):**
- **KEEP: 10** — `omega_memory_search`, `omega_memory_get_history`, `omega_memory_list_sessions`, `hivemind_redis_publish`, `hivemind_redis_subscribe`, `hivemind_get_metrics`, `hivemind_get_session`, `hivemind_list_sessions`, `observability_check_recursion`, `observability_log_boundary_violation`
- **REMOVE: 2** — `memory_search`, `observability_stream`
- **CONSOLIDATE: 0**
- **NEEDS_INFO: 0**

**Recommended final surface for Lilith's domain: 10 tools** (12 − 2 removed).

**Code-fix flags (not removals):**
1. `hivemind_get_session` / `hivemind_list_sessions` — stale `_deprecated()` markers pointing to phantom `hivemind_session` tool.
2. `observability_check_recursion` / `observability_log_boundary_violation` — zero live callers; wire into `subagent_dispatcher` / OpenCode plugin respectively, or revisit in a later pass.
3. `memory_search` references in `search_persistence.py` + `SSP_V2_IMPLEMENTATION.md` must be migrated to `omega_memory_search` at removal time.

**Net effect on the 92-tool surface:** Lilith's domain contributes 2 removals. Combined with the audit's 26 redundant + 3 deprecated + other members' reviews, the surface should land well under the 40-tool degradation threshold.

---

*⬡ OMEGA ⬡ LILITH ⬡ TOOL-REVIEW-S8-S10 ⬡ 2026-09-22*