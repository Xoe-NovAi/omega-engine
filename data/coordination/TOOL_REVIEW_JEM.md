# 🔬 TOOL REVIEW — JEM (Slots S6/S7: Cognition & Context)

**Document ID:** TOOL_REVIEW_JEM_20260922
**Reviewer:** Jem (Sovereign Synthesizer — Slots S6/S7: Cognition & Context)
**Date:** 2026-09-22
**Scope:** Search / Research / Knowledge domain (26 tools)
**Method:** Live `tools/list` crawl (92 tools confirmed) + server code inspection (`mcp_servers/omega_hub/hub_tools/tools.py`, `src/omega/library/*`, `src/omega/oracle/sovereign_search_service.py`) + consumer grep (scripts, packages, tests). No code modified.

---

## ⚖️ VERDICT TABLE

| Tool | Verdict | Rationale |
|------|---------|-----------|
| `sovereign_search` | **KEEP** | Canonical SSP-V2 tiered search (T0 local → web tiers), with SearchPersistence. The one search tool that works end-to-end. |
| `search_extract` | **KEEP** | Only direct Firecrawl deep-extraction path (`extract()` → `_tier_3_firecrawl`); distinct from the search pipeline (raw full-page content vs synthesized findings). Fix docstring tier numbering (says T6, service says T3). |
| `search_status` | **REMOVE** | Stale diagnostics: hardcoded 4-provider tier_map vs SSP-V2's 7 tiers (T0–T6) — actively misleading. Never agent-called; M23 health is served by observability tools. Theater. |
| `library_fts_search` | **KEEP** | Real local FTS5+vector search over curated corpus (`Library.search()`). Distinct from sovereign_search T0 (which caches MemoryStore, not library docs). Tier-0 local surface. |
| `library_web_search` | **CONSOLIDATE** | Redundant wrapper around `sovereign_search_service.search()` — 100% overlap with `sovereign_search`. Has 2 real consumers (`src/omega/skills/opencode_client.py`, `packages/omega-meditation/.../pipeline.py`) + test pin → migrate consumers to `sovereign_search`, then remove. |
| `library_get_document` | **KEEP** | Core retrieval — the only way to read full document content by ID. Irreplaceable for deep research. |
| `library_domains` | **CONSOLIDATE** | Fully redundant: `Library.stats()` already calls `domains()` internally and returns the domain breakdown. Fold into `library_stats`. |
| `library_stats` | **KEEP** | Comprehensive library + indexer stats (total, domains, avg quality, words). Low frequency but real; admin/observability. |
| `library_recent` | **KEEP** | "What's new in the library" surface — real, cheap, distinct from stats. |
| `library_index_flush` | **REMOVE** | Admin/ops-only; an LLM agent would never call this. Indexer persists independently. Not a research surface. |
| `library_ingest_pending` | **KEEP** | The ONLY bridge inbox→library — `background.py` has NO auto-ingestion loop. Without it, inbox items never become searchable docs. |
| `library_discovery` (unified) | **REMOVE** | **Theater.** Does NOT call `DiscoveryService`. `research`/`start` actions just wrap `sovereign_search_service.search()`; `start` fakes a job_id from `final_tier`; `status` literally returns *"Async job tracking not yet implemented"*. Actively misleading — an agent thinks it got a discovery report when it got a search result. |
| `library_discovery_research` | **KEEP** | Real multi-phase engine (`DiscoveryService.discover()`: recon → decompose → parallel subtopic research → synthesis). Used by `scripts/mcp_research_test.py`. |
| `library_discovery_start` | **KEEP** | Real background job (`DiscoveryService.start_discovery()` + `_run_discovery_background`). |
| `library_discovery_status` | **KEEP** | Real `get_job_status()`. The `_deprecated()` marker is WRONG — it points to the broken unified tool. Remove the marker, not the tool. |
| `library_inbox` (unified) | **REMOVE** | **Broken parallel reimplementation, data-integrity hazard.** Writes flat JSON to `<project>/data/library/inbox/*.json` with schema `{type, added_at}` while `InboxManager` reads `~/omega/data/inbox/pending/*.json` with schema `{source_type, created_at, title, metadata}`. Unified items are orphaned — `library_ingest_pending` will NEVER ingest them. Also `PROCESSING_DIR` mismatch (`data/library/processing` vs `data/inbox/processing`). |
| `library_inbox_add_url` | **KEEP** | Real `InboxManager.add_url()` — feeds the actual ingestion pipeline. |
| `library_inbox_add_note` | **KEEP** | Real `InboxManager.add_note()`. |
| `library_inbox_add_file` | **KEEP** | Real `InboxManager.add_file()`. |
| `library_inbox_list` | **KEEP** | Real `InboxManager.list_pending()` — priority-sorted, status-aware. |
| `library_inbox_stats` | **KEEP** | Real `InboxManager.count()` — pending/processing/failed. |
| `research` | **KEEP** | Primary offline research executor (`ResearchEngine.research()` — library hybrid search → synthesis → citations). Distinct from web search. |
| `research_get` | **KEEP** | Resume retrieval by ID — core deep-research pattern (re-open prior research). |
| `research_list` | **REMOVE** | Rarely called; `research` returns its own ID, and `research_get` covers the resume pattern. Discovery of old IDs is a niche need. |
| `research_stats` | **REMOVE** | Admin metric (counts by depth); never agent-called. Observability concern, not a research surface. |
| `research_depths` | **REMOVE** | Static constant, no service call; depth levels are already documented in the `research` tool description. Never called. |

---

## 🗺️ SEARCH ARCHITECTURE

### The sovereign search pipeline (Tier 0–4 / SSP-V2 T0–T6)

The pipeline itself is sound in concept: **T0 local cache → web tiers → deep extraction**. My verification of the live implementation:

- **T0 (local)** = MemoryStore + SovereignCache — conversation/memory corpus, NOT the library corpus. `library_fts_search` is the true Tier-0 for *curated documents*; `sovereign_search` T0 is for *memory*. They are complementary, not overlapping.
- **Web tiers** = SearXNG → Exa → Firecrawl, with circuit breakers, provider health cache, and graceful fallback. Real and functional.
- **Deep extraction** = `search_extract` (Firecrawl full-page). Real but under-documented; tier numbering drifted (docstring "T6" vs service `_tier_3_firecrawl`).

### Are `search_extract` / `search_status` dead?

- **`search_extract` — NOT dead.** It is the only tool that forces raw full-page extraction. For a deep-research specialist, snippet-level search results are often insufficient; this is the "read the actual page" path. Keep it (fix the docstring).
- **`search_status` — dead.** Its tier_map is frozen at a 4-provider view while the pipeline is documented as 7 tiers. A status tool that reports the wrong architecture is worse than none. Remove; M23 failure-integrity diagnostics belong in observability, not the agent tool surface.

### The real finding: the "unified" tools are the theater

The audit's premise — *fragmented tools are fully covered by unified counterparts* — is **factually wrong for my domain**:

1. **`library_discovery` (unified) does not use the discovery engine at all.** It wraps `sovereign_search` and fakes async jobs. The fragmented trio (`library_discovery_research/start/status`) calls the real `DiscoveryService` multi-phase engine. The audit's removal direction is inverted here: **remove the unified, keep the fragmented.**
2. **`library_inbox` (unified) is a parallel, schema-incompatible reimplementation** writing to a different directory tree than `InboxManager`. Items added via the unified tool are invisible to the ingestion pipeline. This is not redundancy — it's a data-integrity bug waiting to happen.
3. **`library_web_search` is genuinely redundant** with `sovereign_search` (same service call, same response shape) — but it has real consumers (`opencode_client.py`, meditation pipeline) that must be migrated first.

### Recommended consolidation path (post-review, not this review)

1. Remove: `library_discovery` (unified), `library_inbox` (unified), `search_status`, `library_index_flush`, `research_list`, `research_stats`, `research_depths`.
2. Migrate then remove: `library_web_search` → `sovereign_search` (update `opencode_client.py` + meditation pipeline + `test_hub_health.py`); `library_domains` → `library_stats`.
3. Fix, don't remove: `library_discovery_status`'s bogus `_deprecated()` marker; `search_extract` docstring tier numbering.
4. If a unified `library_inbox`/`library_discovery` is desired later: rewrite them to **delegate to `InboxManager` / `DiscoveryService`** (single service layer), then remove the fragmented tools. Never reimplement at the MCP layer.

---

## 📊 SUMMARY

| Verdict | Count | Tools |
|---------|-------|-------|
| **KEEP** | 17 | `sovereign_search`, `search_extract`, `library_fts_search`, `library_get_document`, `library_stats`, `library_recent`, `library_ingest_pending`, `library_discovery_research`, `library_discovery_start`, `library_discovery_status`, `library_inbox_add_url`, `library_inbox_add_note`, `library_inbox_add_file`, `library_inbox_list`, `library_inbox_stats`, `research`, `research_get` |
| **REMOVE** | 7 | `search_status`, `library_index_flush`, `library_discovery` (unified), `library_inbox` (unified), `research_list`, `research_stats`, `research_depths` |
| **CONSOLIDATE** | 2 | `library_web_search` → `sovereign_search` (migrate consumers first), `library_domains` → `library_stats` |
| **NEEDS_INFO** | 0 | — |

**Recommended final surface for Slots S6/S7: 19 tools** (17 KEEP + 2 CONSOLIDATE-then-remove), down from 26. Net removal of 7 tools from this domain; the two consolidations require consumer migration and are flagged as follow-up work.

**Core principle applied:** *which search surfaces actually work end-to-end, which are theater, which overlap.* The three real, non-overlapping research surfaces are: `sovereign_search` (web), `library_fts_search` (curated local corpus), and `research` (offline synthesis). Everything else in this domain is either a thin accessor around those, an admin concern, or a broken facade.

---

*⬡ OMEGA ⬡ JEM ⬡ TOOL-REVIEW-S6S7 ⬡ 2026-09-22*