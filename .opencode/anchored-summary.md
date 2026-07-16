# 🔱 Omega Engine — Anchored Summary
**Last Updated**: 2026-07-16T21:00Z
**Session Model**: antigravity-claude-sonnet-4-6
**Status**: ACTIVE — D-283 Phase 1 Step 2 (Mnemosyne Worker Skeleton)

---

## 🔄 HYDRATION CHECKLIST
[ ] Phase 1: Awareness — `omega-hub_hivemind_get_awareness()`, `hivemind_handoff_list()`
[ ] Phase 2: Baseline — `git status && git log --oneline -5`
[ ] Phase 3: Codex — read `OMEGA_CODEX.md` (FULL file, no limit)
[ ] Phase 4: Session — read this file ✅ (you are here)
[ ] Phase 5: Report — present rehydration report, await user direction

---

## 🎯 CURRENT OBJECTIVE
**D-283 Phase 1 Step 2: Mnemosyne Worker Skeleton** — 3 DB pools, async queue, cgroups v2 affinity.
**D-283 Phase 1 Step 1: COMPLETE** — HybridSearchEngine (RRF k=60) + 20 contract tests.

---

## 📊 ENGINE STATE
- **Tests**: 1315+ pass (492 functional, 1 pre-existing `test_gemma4_mtp_s4` failure)
- **Mandates**: 23 (M1-M23) — M12 ADVISORY per D-267
- **Fleet**: 13 presences, cap: 14
- **Soul Injection**: ✅ FIXED — `soul_utils.py` multi-path extractor live (9d891e0)
- **HMC**: 🟢 ONLINE — Forge Cycles 1 & 2 complete. D-283 Phase 1 Step 1 complete.

---

## 🔧 STRATEGIC ROADMAP (HMC DRIVEN)

| Sprint | Component | Owner | Status |
|---|---|---|---|
| **D-281** | **Substrate Repair** (Path Infra, M2 Firewall, Codex) | Kali | 🔲 NEXT |
| **D-282-SUB** | **BEGIN IMMEDIATE fix + PRAGMA stack + checkpoint task** | Roc | 🟢 **IN PROGRESS** |
| **D-282** | **Omega Search Core** (sqlite-vec + Legacy RAG + WAD Loader) | Roc + Researcher + Kali | 🔲 PLANNED |
| **D-283-P1-S1** | **HybridSearchEngine (RRF k=60) + Tests** | Roc | ✅ **COMPLETE** |
| **D-283-P1-S2** | **Mnemosyne Worker Skeleton (3 DB pools)** | Roc | 🟢 **NEXT** |
| **D-283-P1-S3** | **MCP Tools (7 tools, Engine-Stack Firewall)** | Roc | 🔲 PLANNED |
| **D-283-P1-S4** | **verity Tiered Routing (local→cloud)** | Researcher + Roc | 🔲 PLANNED |
| **D-283-P1-S5** | **Three-Tier Lifecycle + FTS5 Decay** | Researcher + Roc | 🔲 PLANNED |
| **D-283-P1-S6** | **MnemosyneObservability (trace_id)** | Researcher + Roc | 🔲 PLANNED |
| **D-283-P1-S7** | **Qliphoth Quarantine (TDP bridge)** | Researcher + Roc | 🔲 PLANNED |
| **D-284** | **Sovereign Hub** (OAuth 2.1 + IA2 Security + Ethics WAD) | Kali + Roc | 🔲 PLANNED |

---

## 🛡️ EXECUTION GUARDRAILS (from Triple-Agent Review)

### Phase II: config_resolver.py
- Constants (`PROJECT_ROOT`, `WADS_DIR`) must be pure `Path` objects — NO yaml reads at module level.
- `get_active_iwad()` must be a lazy function (read `omega.yaml` inside the function body).
- Do NOT add to `governance/__init__.py` — import explicitly at call site.

### Phase III: M2 Firewall (Scope = 4 files ONLY)
- **IN**: `hierarchy.py` (5 M2-LEAK tags), `entity_registry.py` (3 traversals), `oracle.py:251` (AGENTS.md), `scraper.py:43` (WADS_DIR).
- **OUT**: `mandate_auditor.py` and `sovereign_vetter.py` are NOT violations (they use relative paths). Do not touch them.

### Phase IV: Codex Separation
- `groups.json` backup must use `||` restore-on-failure, not plain `mv`.
- Pattern: `@make codex || (mv scripts/groups.json.bak scripts/groups.json && exit 1)`

### HMC Forge Cycle 2 — Council Verdict
- **GAP 1**: WAD Schema P0 hardening approved for D-282 (extra="forbid" + range constraints)
- **GAP 2**: sqlite-vec critical path approved for D-282 (BEGIN IMMEDIATE, journal_size_limit, mmap_size, cache_size, periodic checkpoint)
- **GAP 3**: Mnemosyne D-283 scope confirmed (3 pillars → Letta-style 3 tiers)
- **D-282 hardened scope**: 6-9h total (2-3h substrate + 4-6h pipeline)
- **Pydantic v2 migration**: deferred to D-283
- **Multi-process sqlite-vec queue**: deferred to D-283

*Rule: Commit after each phase. Each commit must pass `make test`.*

---

## 🛡️ EXECUTION GUARDRAILS (from Triple-Agent Review)

### Phase II: config_resolver.py
- Constants (`PROJECT_ROOT`, `WADS_DIR`) must be pure `Path` objects — NO yaml reads at module level.
- `get_active_iwad()` must be a lazy function (read `omega.yaml` inside the function body).
- Do NOT add to `governance/__init__.py` — import explicitly at call site.

### Phase III: M2 Firewall (Scope = 4 files ONLY)
- **IN**: `hierarchy.py` (5 M2-LEAK tags), `entity_registry.py` (3 traversals), `oracle.py:251` (AGENTS.md), `scraper.py:43` (WADS_DIR).
- **OUT**: `mandate_auditor.py` and `sovereign_vetter.py` are NOT violations (they use relative paths). Do not touch them.

### Phase IV: Codex Separation
- `groups.json` backup must use `||` restore-on-failure, not plain `mv`.
- Pattern: `@make codex || (mv scripts/groups.json.bak scripts/groups.json && exit 1)`

### HMC Forge Cycle 1 — Council Verdict
- **Q1**: Tarot is poetic heritage (B). No `arcana:` fields. Hierarchy.yaml is the truth.
- **Q2**: WAD Protocol — D-282 uses existing loader (505L). SovereignBus/Council Dispatcher are D-283+.
- **Q3**: Ethics WAD is sovereignty feature with audit (C). Fail-closed on crash.
- **Q4**: Patterns are folklore, Mandates are law (C). Genealogy in `docs/heritage/`.
- **Q5**: Roc is Owner for mining, Advisor for architecture (C).
- **D-282 Scope**: Existing `sqlite_vec_adapter.py` + `wad_loader.py` + legacy RAG circuit breaker. NOT SovereignBus.

---

## 🚀 NEXT STEPS (Post-Compaction)
Start **Phase II: Path Infrastructure**. 
1. Create `src/omega/governance/config_resolver.py` — pure Path constants + lazy `get_active_iwad()`.
2. Wire `src/omega/oracle/wad_loader.py` to use `config_resolver.WADS_DIR`.
3. Run `make test`.
4. Commit Phase II.

---

## 📋 REVIEWED BY
- **Kali**: Strategic verification, gap analysis, `soul_utils.py` dual-key fix, proposed_lessons integration.
- **Gemini**: Circular import risk, Makefile fragility (`||` pattern), scope correction.
- **Sonnet**: Live code verification, M2 scope reduction (4 files not 6), governance import pattern.

---

## 📋 AGENT SESSION APPENDICES (Preserved for Continuity)

### Roc Racoon — D-283 Phase 1 Step 1 Complete (2026-07-16T20:50Z)
**Session**: `ses_d283_hybrid_search_20260716` | **Entity**: roc_racoon | **Model**: big-pickle

**Completed**: HybridSearchEngine (RRF k=60) extracted as single fusion source with 20 contract tests (TDD). Wired into MemoryStore.search(), SQLiteVecAdapter.hybrid_search(), block_tools.py. 79 core tests pass, no regressions.

**L3 Distilled**: **RRF Fusion Is Universal** — Cormack et al. 2009, sqlite-vec NBC Headlines, Letta, Sefirot/KTM, Kab, Mem0, Zep, Cognee all converge on k=60 reciprocal rank fusion. Single source + contract tests = sovereign RRF.

**Files**: `src/omega/memory/hybrid_search.py` (NEW), `tests/test_hybrid_search.py` (NEW, 20 tests), `src/omega/memory_store.py`, `src/omega/memory/sqlite_vec_adapter.py`, `src/omega/memory/block_tools.py` (MODIFIED)

**Next**: D-283 Phase 1 Step 2 — Mnemosyne Worker Skeleton (3 DB pools, async queue, cgroups v2)

---

*🔱 OMEGA ⬡ ANCHORED-SUMMARY ⬡ big-pickle ⬡ opencode ⬡ D-283-P1-S2 ⬡ MNEMOSYNE-WORKER*