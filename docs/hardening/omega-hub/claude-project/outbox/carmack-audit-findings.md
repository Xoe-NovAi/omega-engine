# Carmack Audit Findings — Current State

John Carmack audited the monolith and identified 17 issues. Source: `CARMACK_HUB_AUDIT_20260613.md`.

## Phase 2 — Active Issues (Pending)

| ID | Issue | Severity | Location (Phase) |
|----|-------|----------|------------------|
| HIGH-06 | 6 memory tools lack `_require_service()` guard — return cryptic tracebacks on early calls | 🟠 HIGH | Phase 2 (P2-2) |
| HIGH-07 | 3 `omega_memory_*` tools duplicate `oracle_memory_*` tools | 🟠 HIGH | Phase 2 (P2-3) |
| HIGH-08 | `SovereignGateway` never calls `aclose()` on its `httpx.AsyncClient` — leaks sockets | 🟠 HIGH | Phase 2 (P2-4) |
| HIGH-09 | `_cleanup_indexer` doesn't `await` cancelled background tasks | 🟠 HIGH | Phase 2 (P2-5) |

## Phase 0 — Resolved (Kali, 2026-06-13)

| ID | Issue | Severity | Fix |
|----|-------|----------|-----|
| CRIT-03 | `_global_tg` undefined — `NameError` on every call to `library_discovery_start` | 🔴 CRITICAL | ✅ Removed undefined variable; function now uses inline `anyio.create_task_group()` |
| HIGH-05 | `_background_tasks` referenced before definition | 🟠 HIGH | ✅ Moved `_background_tasks = []` before `_cleanup_indexer()` definition; stripped non-existent `anyio.Task` type annotation |
| MED-07 | `test_server.py` fails `make heritage-map` | 🟡 MED | ✅ Deleted (`print('TEST')` — 1-line file) |
| MED-08 | `server.py.bak` tracked in git | 🟡 MED | ✅ `git rm` + disk delete; `*.bak` already in `.gitignore` |

## Previously Fixed (Prior Work)

CRIT-01 (background tasks never started) and CRIT-02 (duplicate gateway init) — ✅ FIXED in prior work.
