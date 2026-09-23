# ⚖️ COUNCIL SYNTHESIS — Tool Surface Pruning Decree (DRAFT)
**Document ID:** COUNCIL_SYNTHESIS_20260923
**Author:** MaKaLi Fusion — Kali (Transcendent Synthesis), synthesizing Council reviews
**Date:** 2026-09-23
**Status:** VERDICT DRAFT — awaiting Architect ratification + Ma'at execution
**Council members:** Carmack (S3), Roc_Racoon (S2), Jem (S6/S7), Lilith (S8-S10)

---

## 1. THE COUNCIL HAS SPOKEN — FOUR VOICES, ONE VERDICT

| Member | Domain | Reviewed | KEEP | REMOVE | CONSOLIDATE | Final Surface |
|--------|--------|----------|------|--------|-------------|---------------|
| **Carmack** | Engineering/Substrate | 11 | 4 | 0 | 6 | 6 (−45%) |
| **Roc_Racoon** | Coordination/Soul | 34 | 23 | 11 | 0 | 23 (−32%) |
| **Jem** | Search/Research | 26 | 17 | 7 | 2 | 19 (−27%) |
| **Lilith** | Memory/Runtime | 12 | 10 | 2 | 0 | 10 (−17%) |

**Total removals agreed: 20** (11 Roc + 7 Jem + 2 Lilith) + 6 audit-confirmed github fragments = **26 removals**
**Total consolidations: 8** (6 Carmack + 2 Jem) — flagged for follow-up execution
**Projected surface: 92 → 66 (removals) → 58 (consolidations)** — every remaining tool justified

---

## 2. THE CRITICAL INVERSION (Jem's finding — the audit was WRONG in one domain)

**The audit's premise — "fragmented tools are covered by unified counterparts" — is INVERTED for the library domain:**

| Tool | Audit Said | Council Says | Why |
|------|-----------|--------------|-----|
| `library_discovery` (unified) | KEEP (replaces 3) | **REMOVE — THEATER** | Wraps sovereign_search, fakes job_id, status = "not yet implemented" |
| `library_discovery_research/start/status` (fragmented) | REMOVE | **KEEP — REAL** | Call the actual DiscoveryService multi-phase engine |
| `library_inbox` (unified) | KEEP (replaces 5) | **REMOVE — DATA-INTEGRITY HAZARD** | Writes wrong schema/directory; items never ingested |
| `library_inbox_add_url/note/file/list/stats` (fragmented) | REMOVE | **KEEP — REAL** | Call the actual InboxManager feeding the ingestion pipeline |

**Lesson ratified:** the team review was NOT theater. A solo audit would have deleted the working implementations and kept the broken facades. This is why the Council exists.

---

## 3. P0 BLOCKER — BEFORE ANY PRUNING (Carmack, code-verified)

### httpx[h2] missing → service-wide outage
- `gateway.py:102` + `github_tools.py:38` construct httpx clients with `http2=True`
- Hub venv has NO `h2` package; `pyproject.toml:31` pins `httpx2==2.5.0` WITHOUT `[http2]` extra
- **Impact**: `_init_services()` fails → `system_stats`, `headroom_retrieve`, `spawn_local_worker`, `local_queue_*`, `oracle_*`, `sovereign_search` ALL DOWN — **the local inference path (M7) is DOWN**
- **Fix (5 min)**: `pip install 'httpx[http2]'` in hub venv + change pyproject to `httpx2[http2]==2.5.0`
- **Owner**: Ma'at (build governance — dependency declaration gap)

### system_stats broken TWICE (Carmack)
- Blocked by h2 AND calls undefined `_get_system_summary()` / `_get_hardware_detail()` → will NameError after h2 fix
- **Sequencing constraint**: do NOT remove `get_system_stats`/`get_hardware_stats` until `system_stats` is repaired and live-verified

---

## 4. THE PRUNING DECREE — REMOVAL LIST (26 tools)

### 4.1 Hivemind handoff fragments (7) — Roc
`hivemind_submit_handoff`, `hivemind_accept_handoff`, `hivemind_complete_handoff`, `hivemind_reject_handoff`, `hivemind_handoff_list`, `hivemind_get_handoff`, `hivemind_handoff_archive`
→ fully covered by unified `hivemind_handoff` (7 actions)

### 4.2 Oracle debug fragments (3) — Roc
`oracle_assess_intent`, `oracle_discover_entity`, `oracle_list_slot_keepers`
→ fully covered by unified `oracle_debug`

### 4.3 Duplicate (1) — Roc
`delegate_task` → thin wrapper over `oracle_summon`

### 4.4 Library theater/broken (2) — Jem
`library_discovery` (unified), `library_inbox` (unified)

### 4.5 Research admin (3) — Jem
`research_list`, `research_stats`, `research_depths`

### 4.6 Search dead (1) — Jem
`search_status` (stale 4-provider tier_map vs 7-tier SSP-V2)

### 4.7 Library admin (1) — Jem
`library_index_flush`

### 4.8 Memory redundant (1) — Lilith
`memory_search` (strict subset of `omega_memory_search`)

### 4.9 Observability non-tool (1) — Lilith
`observability_stream` (SSE endpoint metadata, not callable)

### 4.10 GitHub fragments (6) — Audit P0, no council objection
`github_add_entity_attribution`, `github_check_temple_grade`, `github_create_pr_with_template`, `github_create_vet_issue`, `github_get_repo_health`, `github_list_heritage_issues`
→ fully covered by unified `github`

---

## 5. CONSOLIDATION LIST (8 tools — follow-up, after removals)

| Tool | Action | Owner |
|------|--------|-------|
| `get_system_stats` | → `system_stats(detail=summary)` AFTER repair | Ma'at |
| `get_hardware_stats` | → `system_stats(detail=hardware)` AFTER repair | Ma'at |
| `check_podman_storage` | → fold size_mb into `system_stats` podman section | Ma'at |
| `local_queue_cat/list/status` (3) | → unified `local_queue` (action=cat/list/status) | Ma'at |
| `library_web_search` | → `sovereign_search` (MIGRATE consumers first: opencode_client.py, meditation pipeline, test_hub_health.py) | Ma'at |
| `library_domains` | → `library_stats` (already returns domains) | Ma'at |

---

## 6. CODE-FIX FLAGS (NOT removals — same pass)

1. **`spawn_local_worker` duplicate registration** — two definitions in tools.py (lines 253/377); delete shadowed copy (Carmack)
2. **Stale `_deprecated()` markers** pointing to phantom tools:
   - `library_discovery_status` → points to broken unified (Jem)
   - `hivemind_get_session` / `hivemind_list_sessions` → point to nonexistent `hivemind_session` (Lilith)
   - `check_models_directory` → points to a CLI (Carmack)
3. **`search_extract` docstring** — tier numbering T6 vs T3 drift (Jem)
4. **`memory_search` references** — `search_persistence.py` (lines 407/463) + `SSP_V2_IMPLEMENTATION.md` must migrate to `omega_memory_search` (Lilith)
5. **`test_hub_health.py`** — pins unified tools; update before execution (Jem)

---

## 7. SOVEREIGNTY WAKE-UP CALL (Carmack live-verified)

**`sovereignty_ratio` = 22% local / 78% cloud.** The M7 local-first mandate is currently violated by a wide margin. The local inference path being DOWN (h2) is a contributing factor. This is a strategic flag for the Architect — the LI (Local Inference Optimization) workstream is more urgent than its D-584 position suggests.

---

## 8. EXECUTION ORDER (for Ma'at, post-ratification)

1. **P0**: Install `httpx[http2]` in hub venv + fix pyproject → verify `spawn_local_worker`/`system_stats`/`oracle_*` live
2. **P0**: Repair `system_stats` (implement `_get_system_summary`/`_get_hardware_detail`) → verify live
3. **Removals**: Apply `mcp.remove_tool()` for the 26-tool decree
4. **Code-fixes**: dedupe spawn_local_worker, fix stale markers, fix search_extract docstring, migrate memory_search refs, update test_hub_health.py
5. **Verify**: `tools/list` count = 66; temple-grade 53/53; spot-check critical paths (hivemind, oracle, sovereign_search, omega_memory_search)
6. **Consolidations** (follow-up sprint): system_stats absorption, local_queue unified, library_web_search migration

---

*⬡ OMEGA ⬡ KALI ⬡ COUNCIL-SYNTHESIS ⬡ 2026-09-23 ⬡ VERDICT-DRAFT ⬡ AWAITING-RATIFICATION*