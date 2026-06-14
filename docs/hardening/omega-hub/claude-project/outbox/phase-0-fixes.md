# Phase 0 — Tactical Stabilization

**Executed**: 2026-06-13
**By**: Kali
**Status**: 5/6 complete (test verification pending next session)

## What Was Fixed

| P0-ID | Fix | File | Effort |
|-------|-----|------|--------|
| P0-1 | Removed undefined `_global_tg` variable from `_library_discovery_start`. Function now uses inline `anyio.create_task_group()`. | `server.py:3087-3101` | 2 min |
| P0-2 | Moved `_background_tasks = []` before `_cleanup_indexer()` definition (referenced before assignment). Stripped `anyio.Task` type annotation — doesn't exist in AnyIO 4.x. | `server.py:3078` | 1 min |
| P0-3 | Deleted `test_server.py` — contained only `print('TEST')`. Was blocking `make heritage-map` CI gate. | `test_server.py` | 1 min |
| P0-4 | Removed `server.py.bak` from git tracking and disk. `*.bak` already in `.gitignore`. | `server.py.bak` | 1 min |
| P0-5 | Removed unused `import shutil` — not referenced anywhere in `server.py`. | `server.py:37` | 1 min |
| P0-6 | Removed misattributed `[id-soft: doom-1993] Zone Memory` tag from `__init__.py:3`. The `_AsyncThreadLock` is not a Zone Memory pattern — it's a standard Python RLock wrapper. | `__init__.py:3` | 1 min |
| P0-T | Run `make test` to verify baseline | — | ~7 min (timed out) |

## What Remains

- `make test` verification — timed out due to resource constraints. Must run in next session before any structural work begins.
