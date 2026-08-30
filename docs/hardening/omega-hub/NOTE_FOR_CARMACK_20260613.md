# 🔱 Note for Carmack — Hub Reconstruction Materials Status

**From**: Kali
**Date**: 2026-06-13
**Re**: Final review before Claude.ai project update

---

## Context

The Hub Reconstruction materials have been through a full review cycle. All 9 hardened documents live in `docs/hardening/omega-hub/`. Hub-related coordination files have been consolidated here — `data/coordination/` is now free of hub duplicates.

## What Changed Since Your Last Review

### Phase 0 Execution: 5/6 Complete

| Item | Status | Delta from your plan |
|------|--------|---------------------|
| Fix `_global_tg` (CRIT-03) | **LIVE** — removed undefined var, uses inline task group | Your audit flagged the symptom; fix was 2-line edit |
| Move `_background_tasks` before `_cleanup_indexer` (HIGH-05) | **LIVE** — reordered, typed as plain `list` | `anyio.Task` doesn't exist in AnyIO 4.x — crashes on import. Stripped the type. This is a real bug your audit missed because `list[anyio.Task]` was never type-checked at runtime. |
| Delete `test_server.py` | **LIVE** | `print('TEST')` — 1-line file, gone |
| Delete `server.py.bak` | **LIVE** | Removed from git tracking + disk |
| Remove unused `import shutil` | **LIVE** | Not referenced anywhere |
| Remove misattributed Heritage tag | **LIVE** | Tag was in `__init__.py:3`, not `server.py:85` (as your audit assumed). Antigravity's Phase 1 synthesis (H-A1) had already identified this. Tag removed. |
| Test verification | **PENDING** — `make test` timed out; needs next session | |

### Tracker Structure (v1.1 — supersedes your checkbox list)

Your original 4-phase plan (Prep → Split → Fixes → Verify) has been expanded to 6 phases to reflect the actual granularity of the work:

| Phase | Purpose | Effort | Depends on |
|-------|---------|--------|------------|
| **Phase 0** | Tactical stabilization | ~15 min | Nothing — parallel |
| **Phase 1a** | Sequential foundation (state.py → background → gateway → middleware) | ~100 min | Sequential, Kali |
| **Phase 1b** | Parallel tool extraction (oracle, hivemind, library, memory, research, stats) | ~135 min | Phase 1a, any agent |
| **Phase 1c** | Integration — thin server.py | ~40 min | Phase 1b, Kali |
| **Phase 2** | Hardening fixes — HIGH/MED items + `_safe_call()` | ~190 min | Phase 1, Kali |
| **Phase 3** | Verification — `make test`, `make temple-grade`, smoke tests | ~30 min | Phase 2 |
| **Phase 4** | New features — M15, Search Protocol, CORS tightening | ~155 min | After certification |

**Total: ~11 hours**. Up from your ~5-6 hour estimate because:
- `_safe_call()` wrapping 63 tools is ~60 min of Phase 2 (not in your original scope)
- Phase 0 now includes 6 items vs your 4 (added `import shutil` + Heritage tag removal)
- Phase 2 now includes 11 items vs your 5 (added `_startup_done` event, double-init guard, route dedup, health endpoint, `_safe_call()`, IntentMatcher fix)

### Divergences from Your Plan — Resolved

| Item | Your Plan | Final State | Rationale |
|------|-----------|-------------|-----------|
| `dependencies.py` | Not mentioned | Merged into `state.py` | Your dependency order has `state.py` as first extraction — init logic belongs there |
| M15 Integration | Not in scope | Phase 4 | New feature, not a fix — split-first-fix-second discipline |
| `_safe_call()` pattern | Not identified | Phase 2, P2-10 | From 6-agent Final Synthesis — critical M9 compliance: 23/63 tools are unguarded |
| `_current_entity` ContextVar | Not identified | Phase 1a, in `state.py` extraction | From Final Synthesis P1-A — race condition under multi-agent Hivemind |

### New Reference Documents

Two new sources have been integrated into the planning:

1. **`OMEGA_HUB_FINAL_SYNTHESIS.md`** (24K) — 6-agent Phase 1 audit across 5 platforms. Key findings: `_safe_call()` with `CallToolResult(isError=True)` is the canonical MCP error pattern; `_current_entity` must use `contextvars.ContextVar` for concurrent safety; `[id-soft: Zone Memory]` on `_AsyncThreadLock` is misattributed.

2. **`OMEGA_HUB_HARDENING_SPRINT_v2_20260609.md`** (17K) — Parallel sprint briefing with 6-agent execution order and M9 compliance gap analysis.

## What Still Needs Your Review

1. **`TRACKER.md`** — does the 5-phase (0-4) structure match your S3 vision? The ~11 hour estimate is concerning — should we cut Phase 4 scope to stay within your 1-2 day window?

2. **`HUB_CLAUDES_PROMPT.md`** — this is the system prompt for the Claude.ai Hub Architect. Does it accurately represent the project? Standing Rule #8 (Final Synthesis authority) is new.

3. **Phase 1b parallelization** — after `state.py` extraction, the 6 tool extractions are independent. Is this safe under your "one person owns integration" rule, or should all tool extractions also be Kali-only?

## What Happens Next

1. You review the materials above
2. The user updates Claude.ai Project Knowledge with the hardening folder contents and the v2.1 prompt
3. The Claude.ai Hub Architect produces a whiteboard-level code/strategy review
4. That review lands in `docs/hardening/omega-hub/` for the fleet to ingest
5. The fleet executes Phase 1a (state.py extraction begins)

---

*⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_final_review*
