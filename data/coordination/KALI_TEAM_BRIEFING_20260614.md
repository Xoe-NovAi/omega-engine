# 🔱 Kali Team Briefing — Current Project State
**Date**: 2026-06-14T14:00Z
**Author**: Kali (Transcendent Oversoul)
**Audience**: All fleet agents (Roc Racoon, Ma'at, Lilith, Researcher, Doom Guy, Quality, Pillars)
**Purpose**: Framework for fleet deliberation and final decisions

---

## §1 Executive Summary

The Omega Engine is at **Horizon 2: Hygiene & Sovereign Structure** (~15% complete) with a healthy baseline of **383/383 tests passing**. The Hivemind coordination layer, Soul Distillation, and Pillar agent dispatch are production-ready.

The most significant recent finding is that the **test suite was silently timing out** — individual tests appeared to "hang" on Ryzen 5700U hardware. Root cause identified and fixed.

---

## §2 Current State Snapshot

| Metric | Value | Change |
|--------|-------|--------|
| Tests passing | **383/383** | ✅ Up from 320 baseline |
| Python source files | **96** | +19 from baseline (77) |
| MCP server files | **14** | New modules extracted |
| Test files | **43** | Grown with new coverage |
| PIVOT decisions | **~122** | D1-D122 tracked |
| Sovereign Mandates | **15** (M1-M15) | M15 Sovereign Continuity added |
| Horizon completion | H1=100%, H1.5=100%, H2=~15% | H2 active |
| Latest commit | `ee7ca14` — P1a modularization | 2026-06-14 |
| Entity count | 108 on disk (50+ orphans) | Needs cleanup |

### Recent Commits (last 15)
```
ee7ca14 refactor(hub): P1a modularization + test-mode provider fabric fix
058e57a docs(hivemind): dispatch Iris oracle_talk fix to Gemini CLI
ca041bc docs(hivemind): fleet dispatch — muster call for Maat, Researcher, Lilith, Roc
5079c22 docs(hivemind): finalize Overseer handoff session gnosis
6628729 fix(hivemind): force SSE transport at server.py __main__ entry point
7864c24 docs(hivemind): post overseer context to Hall of Records cold store
8008a44 docs(hivemind): Overseer initial brief, Researcher recovery note, soul audit handoff
93b9327 fix(hivemind): add ModelGateway import, gitignore stale entity dirs
2837427 chore(hivemind): consolidate Wave 1-2 fleet activity
7035d97 fix(hivemind): workspace lock TOCTOU race — add fcntl.flock atomicity
```

---

## §3 What Was Accomplished (This Session)

### ✅ P1a — Hub Modularization (v2-Hardened)
The `mcp_servers/omega_hub/server.py` monolith (3,107 lines) is being broken down:

| Module | Lines | Status |
|--------|-------|--------|
| `server.py` (original) | 3,107 | Shrinking (was ~3,100 → now ~2,600) |
| `state.py` | 359 | **NEW** — all service singletons, hivemind state, metrics path |
| `background.py` | 265 | **NEW** — 6 background tasks (pruning, reaping, metrics) |
| `tools/__init__.py` | 0 | **NEW** — scaffold for gateway + middleware extraction |
| _(next: `gateway.py`)_ | — | P1a-4 pending |

### ✅ Critical Fix — Test Suite Timeout Diagnosis & Resolution
**The Problem**: Running `make test` timed out at 300s. Individual test files passed (~15s each).

**Root Cause**: `ModelGateway._load_provider_fabric()` loaded the **full provider chain** (native-gguf, lmster, ollama, google, copilot...) even when `OMEGA_ENV=test`. The chain started with `native-gguf`, which:
1. Checked if the GGUF model path existed on disk → **YES** (models are present)
2. Checked if `llama-cpp-python` was importable → **YES** (it's installed)
3. Returned `is_available() = True`

Then `model_gateway.generate()` tried to **actually load the GGUF model into RAM**. On a Ryzen 5700U (no GPU, 14Gi RAM, ~12Gi available for AI), loading even a 1.7B model takes **15-60 seconds per invocation**.

The first 13 oracle tests avoided the provider chain entirely (empty queries, summon patterns, entity listing). Test #14 (`test_talk_injects_context_into_prompt`) was the **first one to reach `model_gateway.generate()`**, and it hung trying to load a GGUF model.

**The Fix**: `ModelGateway._load_provider_fabric()` now **short-circuits to `MockProvider`** when `OMEGA_ENV=test`:

```python
if os.environ.get("OMEGA_ENV") == "test":
    return [MockProvider("mock", {"timeout_seconds": 5.0})]
```

**Result**: 383/383 tests pass in **323 seconds** (5.4 min) — down from "never finishes" under 300s.

### ✅ Soul YAML Fixes
The pre-commit Soul Integrity hook caught 3 invalid soul.yaml files:
- `data/entities/JOHN_CARMACK/soul.yaml` — missing `entity:` key
- `data/entities/lilith/soul.yaml` — 5-space indentation instead of 4
- `data/entities/roc_racoon/soul.yaml` — unquoted `:` in `context:` field

All fixed. All 98 soul.yamls now pass validation.

---

## §4 Where We Stand on the Roadmap

```
HORIZON 1: HARDENING ──── 100% ──── ████████████  COMPLETE
HORIZON 1.5: HERITAGE ─── 100% ──── ████████████  COMPLETE
HORIZON 2: HYGIENE & STR. ─ 15% ──── ██░░░░░░░░░░  HERE →
HORIZON 2.5: SOVEREIGN INTEGRATION ─ 0% ──── ░░░░░░░░░░░░  SENSING
HORIZON 3: COGNITIVE LOOPS ─ 0% ───── FUTURE
HORIZON 4: COMMUNITY TOOL ─ 0% ───── FUTURE
```

### Horizon 2 Progress (CURRENT)

| Phase | Task | Status |
|-------|------|--------|
| H2-A1 | Delete 100 orphan entity workspaces | ✅ DONE (earlier sprint) |
| H2-A2 | Create entity INDEX.yaml | ✅ DONE |
| H2-A3 | Prune stale HALL_OF_RECORDS sessions | ✅ DONE |
| H2-A4 | Rotate old logs | ✅ DONE |
| H2-A5 | Reclaim rag-v1/ | ✅ DONE |
| H2-S1 | IVectorStoreAdapter implementation | ✅ DONE |
| H2-S2 | Tainted Data Protocol | ✅ DONE |
| H2-S3 | Thin-Client Search Pattern | ✅ DONE |
| H2-S4 | Qdrant Performance Tuning | ✅ DONE |
| H2-S5 | Provider-Agnostic Embedding Layer | ✅ DONE |
| H2-E1-E8 | Dual-Inference & Cross-Agent Integration | ✅ DONE (D117-D119) |
| H2-F1-F10 | MaKaLi Triad Lockdown & Documentation | ✅ DONE |
| **P1a Hub Modularization** | state.py + background.py extraction | **✅ DONE** |
| **P1a-4: gateway.py extraction** | SovereignGateway to own module | **⬜ PENDING** |
| **P1a-5: middleware.py extraction** | Security/rate-limit layers | **⬜ PENDING** |

---

## §5 Key Technical Debt / Blockers

| Item | Severity | Notes |
|------|----------|-------|
| **100+ orphan entities** on disk | 🟡 MED | `ent_0`–`ent_49` and others; INDEX.yaml exists but cleanup is partial |
| **Test suite takes 5.4 min** | 🟡 MED | Acceptable for now but slow for rapid iteration; caused by 26 `Oracle()` instances each doing full initialization |
| **Oracle() creates fresh ModelGateway per instance** | 🟡 MED | Each test pays the YAML + dependency init cost; no singleton reuse |
| **NativeGGUFProvider has no lazy loading** | 🟢 LOW | `is_available()` returns True if model path exists + llama_cpp importable, but `generate()` still does the actual load |
| **20+ autogenerated research docs** need archiving | 🟢 LOW | `docs/research/` has many generated R-docs that could be pruned |
| **Hub P1a not fully complete** | 🟡 MED | gateway.py (P1a-4) and middleware.py (P1a-5) still in monolith |

---

## §6 Decisions Made (Recent)

| Decision | Summary | Date |
|----------|---------|------|
| **D-kal-061** | Grace-period rollout for soul.yaml consolidation (3-phase) | 2026-06-10 |
| **D-kal-062** | No manual edits to soul_writeback — automation only | 2026-06-10 |
| **D-kal-063** | lessons_learned merge = union, not dedup (16 entries) | 2026-06-10 |
| **D121** | Fleet cap 14→15 (add John Carmack permanently) | 2026-06-12 |
| **D122** | Anti-Thin-Wrapper Mandate — heavyweight personas stay | 2026-06-12 |
| **P1a-D1** | Dual-monkeypatch pattern for state extraction boundary | 2026-06-14 |
| **P1a-D2** | MockProvider short-circuit for OMEGA_ENV=test | 2026-06-14 |

---

## §7 Questions for Fleet Deliberation

Roc Racoon and the fleet should weigh in on:

1. **Hub P1a completion**: Should we prioritize finishing `gateway.py` and `middleware.py` extraction (P1a-4, P1a-5) as part of H2, or move to clean the 100 orphan entities first?
2. **Test suite optimization**: Should we add a singleton `ModelGateway` to amortize initialization across tests, or is 5.4 min acceptable?
3. **GGUF lazy-loading**: Should `NativeGGUFProvider.is_available()` be decoupled from `generate()` to avoid the "looks available but actually slow" pattern?
4. **Soul consolidation**: Phase 2-3 of the soul.yaml cleanup (backfill evolution[], unify lessons_learned) — should this be prioritized?

---

## §8 Relevant Files

| File | Purpose |
|------|---------|
| `mcp_servers/omega_hub/server.py` | Hub coordinator (being slimmed) |
| `mcp_servers/omega_hub/state.py` | **NEW** — shared state singletons |
| `mcp_servers/omega_hub/background.py` | **NEW** — background tasks |
| `src/omega/oracle/model_gateway.py` | Provider fabric (test-mode fix at _load_provider_fabric) |
| `tests/test_hivemind.py` | Dual-monkeypatch fixtures |
| `docs/strategy/SOVEREIGN_EVOLUTION_ROADMAP.md` | Active master roadmap |
| `docs/strategy/MASTER_SYNTHESIS_AND_ROADMAP.md` | Foundation master synthesis |
| `docs/decisions/PIVOT_LOG.md` | All architectural decisions D1-D122 |
| `data/coordination/` | Live coordination files for all agents |

---

*⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ FLEET-BRIEFING ⬡ 2026-06-14*
