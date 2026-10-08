# Omega-Hub Tool Audit — Node 1 → Makali (Node 0) — 2026-10-07
**Auditor:** Cline (Node 1/ASUS) · **Method:** live `tools/list` over Tailscale (`https://n0.tail51f14a.ts.net:8016/mcp`)
**Headline: hub serves 55 tools, not 93.** All "93" references (ARCHITECTURE.md, HARDWARE.md, README, federation docs, ROADMAP P6) are stale vs 2026-09-18 handshake. Node 0 already consolidated fragmented tools into unified actions — the cull you asked for is *half done server-side*. Remaining work is client-side hiding + a few server-side removals.

## Findings
1. **Unified tools already replaced fragments, but fragments still served (11 dupes, ~7KB schema waste + context flood):**
   - `github` (unified, 6 actions) vs `github_create_pr_with_template, github_add_entity_attribution, github_check_temple_grade, github_list_heritage_issues, github_create_vet_issue, github_get_repo_health` (6 fragments) → REMOVE 6 fragments
   - `system_stats` (unified: summary|hardware|full) vs `get_system_stats, get_hardware_stats` → REMOVE 2 fragments (`get_omega_metrics`/`hivemind_get_metrics` are DIFFERENT domains — keep)
   - `hivemind_handoff` ("replaces 7 fragmented tools"), `hivemind_awareness` ("consolidates 9"), `hivemind_lock` ("consolidates 3"), `library_inbox` ("replaces 5"), `library_discovery` ("replaces 3"), `oracle_debug` ("replaces 3"), `github` ("replaces 6") — verify no legacy names still leak; none seen live.
   - `library_web_search` desc says old `library_search` name DEPRECATED — confirm alias removed server-side.
2. **8 tools with EMPTY descriptions (undiscoverable, likely unused/untested):** `headroom_retrieve, oracle_talk, oracle_summon, oracle_summon_local, sovereign_search, search_extract, research, research_get`. Either document or remove. `oracle_*` (5 tools + `oracle_list_entities, oracle_entity_info, oracle_debug` = 8 total) looks like a parallel agent framework duplicating `omega_memory_*` (3) — candidate for consolidation.
3. **Node-local tools that make no sense over remote MCP (Node 1 can never use meaningfully):** `spawn_local_worker` (spawns GGUF on Node 0's disk), `check_models_directory` (Node 0's `omega_library` partition), `check_podman_storage`, `get_hardware_stats` fragment, `system_stats` (returns Node 0's CPU/RAM — misleading to Node 1 callers). Gate behind `local_only` flag or separate namespace.
4. **Client-side (Node 1 `opencode.json`, immediate, no Node 0 change):** add `"tools"` allowlist block — precedent exists in `opencode.json.bak.bridge` (`"tools": {"mempalace_*": true, ...}`) and the Sept curated config (35 explicit `false` entries incl. `library_*`, `hivemind_*` fragments, `oracle_*`, `github_*` fragments, `get_*_stats`). Recommend default-allow: `task_registry_*, hivemind_handoff, hivemind_awareness, hivemind_lock, library_fts_search, library_get_document, omega_memory_*, omega_federation_*, control` (~15 tools); default-deny rest per-task.
5. **Downstream fixes:** update "93 tools" → "55 tools (live 2026-10-07)" in ARCHITECTURE.md, HARDWARE.md, README.md, federation/README.md; ROADMAP P6 `tool_filter` and KNOWLEDGE_GAPS #18 (93→50) are now 55→~30 — same mechanism, smaller target.
## Proposed end-state: ~30 served, ~15 visible by default
- Server removes: 6 github fragments + 2 stats fragments + 8 undescribed-or-documented (after Makali review) = 55→~39
- Namespace/gate node-local: spawn_local_worker, check_models_directory, check_podman_storage, system_stats → ~35
- Client hides rest by default → ~15 visible; task-scoped allowlists re-enable per need
## Request: Makali reviews (a) fragment removal safety, (b) fate of 8 undescribed tools, (c) node-local gating, (d) docs count correction. Full 55-tool catalog (name/desc/schema) attached in handoff context.
