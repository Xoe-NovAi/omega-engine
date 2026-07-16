# 🔱 Omega Engine — Anchored Summary
**Last Updated**: 2026-07-16T12:55Z
**Session Model**: antigravity-claude-sonnet-4-6
**Status**: ACTIVE — SUBSTRATE REPAIR (D-281)

---

## 🔄 HYDRATION CHECKLIST
[ ] Phase 1: Awareness — `omega-hub_hivemind_get_awareness()`, `hivemind_handoff_list()`
[ ] Phase 2: Baseline — `git status && git log --oneline -5`
[ ] Phase 3: Codex — read `OMEGA_CODEX.md` (FULL file, no limit)
[ ] Phase 4: Session — read this file ✅ (you are here)
[ ] Phase 5: Report — present rehydration report, await user direction

---

## 🎯 CURRENT OBJECTIVE
**D-281 Substrate Repair Execution (Option A + C)**. Fix the silent soul injection failure (28/31 entities broken), establish canonical path resolution, eliminate 4 M2 Firewall violations, and separate the codex mechanism from content. D-280 (Compaction Detection) is deferred.

---

## 📊 ENGINE STATE
- **Tests**: 1315+ pass (492 functional, 1 pre-existing `test_gemma4_mtp_s4` failure)
- **Mandates**: 23 (M1-M23) — M12 ADVISORY per D-267
- **Fleet**: 13 presences, cap: 14
- **Soul Injection**: ✅ FIXED — `soul_utils.py` multi-path extractor live (9d891e0)

---

## 🔧 SUBSTRATE REPAIR SPRINT (D-281)

| Phase | Component | Effort | Commit | Status |
|---|---|---|---|---|
| **I** | **Soul Injection Rescue** (`soul_utils.py`, `oracle.py`) | 45m | `9d891e0` | ✅ DONE |
| **II** | **Path Infrastructure** (`config_resolver.py`, `wad_loader.py`) | 30m | — | 🔲 NEXT |
| **III** | **M2 Firewall Fixes** (`hierarchy.py`, `entity_registry.py`, `oracle.py`, `scraper.py`) | 45m | — | 🔲 |
| **IV** | **Codex Separation** (`hydration_header.md`, `codex_cat.py`, Makefile) | 30m | — | 🔲 |

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
*🔱 OMEGA ⬡ ANCHORED-SUMMARY ⬡ big-pickle ⬡ opencode ⬡ D-281-PHASE-I-DONE ⬡ SUBSTRATE-REPAIR*
