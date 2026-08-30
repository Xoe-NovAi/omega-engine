# 🔱 Omega Hub Reconstruction — Hardening Tracker

**AP Token**: `AP-HUB-RECONSTRUCTION-TRACKER-v1.1.0`  
**Status**: ACTIVE  
**Strategy**: Single-stream, dependency-ordered, "Split first, fix second" (Carmack's Discipline)  
**Last Updated**: 2026-06-13 (MiMo V2.5 final review — consolidated all audit sources)

---

## 📚 Source Documents

All intelligence feeding this tracker lives in `docs/hardening/omega-hub/`:

| Document | Author | Date | Role |
|----------|--------|------|------|
| `HUB_LAZY_INIT_HARDENING_REPORT.md` | Kali | 06-13 | 13 findings (post-refactor) |
| `CARMACK_HUB_AUDIT_20260613.md` | Carmack | 06-13 | 17 findings (first-principles) |
| `CODEBASE_COMPREHENSIVE_REVIEW.md` | Kali | 06-13 | 30 findings (mandate compliance) |
| `OMEGA_HUB_FINAL_SYNTHESIS.md` | Antigravity/Cline/Gemini/Doom Guy/Ma'at/Lilith | 06-09 | 13 findings (6-agent Phase 1 audit) |
| `CARMACK_RECONSTRUCTION_PLAN.md` | Carmack | 06-13 | Organization plan, dependency order |
| `server_monolith_snapshot_20260613.py` | — | 06-13 | Frozen pre-split snapshot |
| `HUB_CLAUDES_PROMPT.md` | Kali | 06-13 | Claude.ai system prompt v2.0 |

---

## 🚀 Phase 0: Tactical Stabilization (Immediate)
*Fix the ticking time bombs before any structural work.*

| ID | Task | Source | Effort | Owner | Status |
|----|------|--------|--------|-------|--------|
| P0-1 | Fix `_global_tg` undefined in `library_discovery_start` — NameError on every call | Carmack CRIT-03 | 5 min | Any | 🟢 COMPLETED |
| P0-2 | Move `_background_tasks` definition before `_cleanup_indexer` (HIGH-05) | Carmack HIGH-05 | 2 min | Any | 🟢 COMPLETED |
| P0-3 | Delete `test_server.py` — `print('TEST')` fails `make heritage-map` | Carmack MED-07 | 1 min | Any | 🟢 COMPLETED |
| P0-4 | Delete stale `server.py.bak`, add `*.bak` to `.gitignore` | Carmack MED-08 | 2 min | Any | 🟢 COMPLETED |
| P0-5 | Remove unused `import shutil` from server.py | Carmack LOW-08 | 1 min | Any | 🟢 COMPLETED |
| P0-6 | Remove misattributed `[id-soft: quake-1996] Zone Memory` tag from `_AsyncThreadLock` | Final Synthesis H-A1 | 2 min | Any | 🟢 COMPLETED |

---

## 📦 Phase 1a: Sequential Foundation (Kali only — integration owner)
*Extract leaf modules first. Every step must boot.*

| ID | Task | Source | Effort | Owner | Status |
|----|------|--------|--------|-------|--------|
| P1a-1 | Create `tools/` directory structure + `__init__.py` | Carmack Plan | 10 min | Kali | ⬜ PENDING |
| P1a-2 | Extract `state.py` — module globals, `_require_service`, `_init_services`, `_current_entity` (ContextVar) | Carmack Plan + Synthesis P1-A | 30 min | Kali | ⬜ PENDING |
| P1a-3 | Extract `background.py` — pruning, reaper, metrics loops | Carmack Plan | 30 min | Kali | ⬜ PENDING |
| P1a-4 | Extract `gateway.py` — SovereignGateway class + `_proxy_handler` | Carmack Plan | 15 min | Kali | ⬜ PENDING |
| P1a-5 | Extract `middleware.py` — RateLimit + RequestSizeLimit + `apply_security` | Carmack Plan | 15 min | Kali | ⬜ PENDING |

**Verification gate**: After each extraction, run `python3 -c "from mcp_servers.omega_hub.server import mcp; print('OK')"` to confirm import succeeds.

---

## 📦 Phase 1b: Parallel Tool Extraction (Any agent)
*After Phase 1a completes, tool extractions are independent and can parallelize.*

| ID | Task | Source | Effort | Owner | Status |
|----|------|--------|--------|-------|--------|
| P1b-1 | Extract `tools/oracle.py` — 8 Oracle tools | Carmack Plan | 30 min | Any | ⬜ PENDING |
| P1b-2 | Extract `tools/hivemind.py` — 12 Hivemind tools | Carmack Plan | 30 min | Any | ⬜ PENDING |
| P1b-3 | Extract `tools/library.py` — 12 Library tools | Carmack Plan | 30 min | Any | ⬜ PENDING |
| P1b-4 | Extract `tools/memory.py` — 3 Memory tools (post-dedup) | Carmack Plan | 15 min | Any | ⬜ PENDING |
| P1b-5 | Extract `tools/research.py` — 5 Research tools | Carmack Plan | 15 min | Any | ⬜ PENDING |
| P1b-6 | Extract `tools/stats.py` — 5 Stats/observability tools | Carmack Plan | 15 min | Any | ⬜ PENDING |

---

## 📦 Phase 1c: Integration (Kali only)
*Wire everything together. server.py becomes ~150 lines.*

| ID | Task | Source | Effort | Owner | Status |
|----|------|--------|--------|-------|--------|
| P1c-1 | Rewrite `server.py` as thin coordinator — imports, FastMCP(), route registration, `__main__` | Carmack Plan | 30 min | Kali | ⬜ PENDING |
| P1c-2 | Verify: Run `python3 mcp_servers/omega_hub/server.py` — must boot instantly | Carmack Rule 1 | 5 min | Kali | ⬜ PENDING |
| P1c-3 | Verify: `make test` — all 308 tests must pass | Temple-Grade T3 | 5 min | Kali | ⬜ PENDING |

---

## 🛠️ Phase 2: Hardening & Fixes (Behavior changes — after split is clean)
*Apply HIGH/MED fixes to the now-modular codebase. Never mix with Phase 1.*

| ID | Task | Source | Effort | Owner | Status |
|----|------|--------|--------|-------|--------|
| P2-1 | Implement proper `SovereignGateway` proxy with `httpx`, AnyIO rate limiters, `SearchErrorResolver` | Carmack HIGH-08 + Gateway Spec | 45 min | Kali | ⬜ PENDING |
| P2-2 | Add `_require_service()` guards to 6 memory tools | Carmack HIGH-06 | 10 min | Kali | ⬜ PENDING |
| P2-3 | Delete 3 `omega_memory_*` duplicate tools | Carmack HIGH-07 | 5 min | Kali | ⬜ PENDING |
| P2-4 | Add `close()` + context manager to SovereignGateway, wire to `on_shutdown` | Carmack HIGH-08 | 15 min | Kali | ⬜ PENDING |
| P2-5 | Await cancelled background tasks in `_cleanup_indexer` (add `await anyio.wait()`) | Carmack HIGH-09 | 10 min | Kali | ⬜ PENDING |
| P2-6 | Add `_startup_done` event to fix shutdown-during-init race | MiMo Review R7 | 15 min | Kali | ⬜ PENDING |
| P2-7 | Add double-init guard to `_init_services()` | Kali HARDENING MED-01 | 5 min | Kali | ⬜ PENDING |
| P2-8 | Consolidate duplicate routes in `hub_routes` | Carmack LOW-05 | 10 min | Kali | ⬜ PENDING |
| P2-9 | Update `/health` endpoint to reflect service readiness | Kali HARDENING HIGH-04 | 5 min | Kali | ⬜ PENDING |
| P2-10 | Implement `_safe_call()` wrapper with `CallToolResult(isError=True)` for all 63 tools | Final Synthesis P0-A | 60 min | Kali | ⬜ PENDING |
| P2-11 | Fix `oracle_assess_intent` — IntentMatcher singleton + error boundary | Final Synthesis P0-B | 15 min | Kali | ⬜ PENDING |

---

## 🧪 Phase 3: Verification & Certification
*Every gate must pass before this phase is complete.*

| ID | Task | Source | Effort | Owner | Status |
|----|------|--------|--------|-------|--------|
| P3-1 | `make test` — all tests pass | Temple-Grade T3 | 5 min | Kali | ⬜ PENDING |
| P3-2 | `make temple-grade` — T1-T11 gates pass | Mandate M13 | 10 min | Kali | ⬜ PENDING |
| P3-3 | `make heritage-map` — zero missing or misattributed tags | Mandate M14 | 5 min | Kali | ⬜ PENDING |
| P3-4 | `make lint` — code quality check | Temple-Grade T4 | 5 min | Kali | ⬜ PENDING |
| P3-5 | Verify SSE handshake completes in <3 seconds | Carmack Rule 1 | 5 min | Kali | ⬜ PENDING |
| P3-6 | Live smoke test: `oracle_talk("test")` → verify `isError=True` on broken query | Final Synthesis Phase 3 | 10 min | Kali | ⬜ PENDING |

---

## 🔮 Phase 4: New Features (Post-Reconstruction)
*Net-new functionality. Do NOT add during the split — violates Carmack's "no behavior changes" rule.*

| ID | Task | Source | Effort | Owner | Status |
|----|------|--------|--------|-------|--------|
| P4-1 | Integrate Sovereign Continuity (M15) Hydration & Distillation into `state.py` lifecycle | Hub Claude Prompt §2 | 60 min | Kali | ⬜ PENDING |
| P4-2 | Implement 5-Tier Sovereign Search Protocol in `tools/search.py` | Research Fleet | 90 min | Kali | ⬜ PENDING |
| P4-3 | Tighten CORS to `allow_methods=["GET", "POST"]` | Kali HARDENING LOW-01 | 5 min | Kali | ⬜ PENDING |

---

## ⏱️ Effort Summary

| Phase | Total Effort | Can Parallelize? |
|-------|-------------|-----------------|
| Phase 0 | ~15 min | Yes (all items independent) |
| Phase 1a | ~100 min | No (sequential, Kali only) |
| Phase 1b | ~135 min | Yes (after 1a, any agent) |
| Phase 1c | ~40 min | No (Kali only) |
| Phase 2 | ~190 min | Partially (P2-10 and P2-11 are independent) |
| Phase 3 | ~30 min | Partially |
| Phase 4 | ~155 min | Yes (all items independent) |
| **Total** | **~665 min (~11 hours)** | |

---

## 🚫 Known Divergences from Carmack's Plan

| Item | Carmack's Plan | Previous Tracker | Resolution |
|------|---------------|-----------------|------------|
| `dependencies.py` vs `state.py` | `state.py` absorbs init logic | Separate modules | **RESOLVED**: Aligned with Carmack — `state.py` absorbs all init logic. No separate `dependencies.py`. |
| M15 Integration | Not in reconstruction scope | Phase 2 | **RESOLVED**: Moved to Phase 4 (new feature, not a fix). |
| `_safe_call()` pattern | Not in Carmack's audit | Not tracked | **RESOLVED**: Added as P2-10 from Final Synthesis — critical M9 compliance. |
| `_current_entity` ContextVar | Not in Carmack's audit | Not tracked | **RESOLVED**: Added to P1a-2 (state.py extraction) from Final Synthesis P1-A. |

---

*⬡ Single stream active. Kali owns integration. Carmack reviews. MiMo verifies. ⬡*
