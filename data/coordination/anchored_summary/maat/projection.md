<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 MA'AT PROJECTION — 2026-09-28 (SEAM ARC)

## Status: PUBLIC · temple-grade 53/53 · two dead daemons recovered

### Executive Summary
Build-side governance held while **two MCP daemons were crash-looping in production** and temple-grade reported 53/53 the entire time. Both are now repaired, and the gates that would have caught them are landed and proven. The commit is **`de660681` on `release/debut-v1.6.0`**; working tree clean.

**The lesson that matters more than the fixes:** a green gate is a claim about the system, not a measurement of it. Every gate in the temple-grade chain was static or artifact-level; none executed an import. The fleet was blind for 36+ hours because "53/53 PASS" and "the daemon is dead" were both true at the same time.

### Key State
| Gate | Status |
|------|--------|
| **Temple-Grade** | 53/53 PASS — now **leads with** `check-hub-imports` (6 modules, clean venv) |
| **Tier A import gate** | `tests/test_hub_import_smoke.py` — 6 modules + 3 structural guards, 10/10 |
| **Tier B import gate** | `make check-hub-imports` — HEAD + tracked-diff overlay, ~30–45 s |
| **Hub health gate** | 5 conditions + dwell + `uptime_s`; **4 negative paths proven failing** |
| **Hub systemd unit** | `ExecStartPre` import check; `StartLimit*` moved to `[Unit]` (was inert) |
| **Legacy shim** | 12 of 28 dead → **28/28 resolve** |
| **omega-hub** | NRestarts 34 → **0**, active/running, `:8016/health` 200 |
| **omega-searxng-mcp** | NRestarts **6991** → **0**, active/running, `:8018/health` 200 |

### What Was Actually Broken
| # | Defect | Symptom | Root cause |
|---|--------|---------|------------|
| 1 | `omega_hub/server.py:85` imported 3 deleted symbols | crash-loop | Hivemind consolidation deleted them; `__getattr__` shim masked it at import |
| 2 | `searxng/server.py:29` imported uninstalled `fastmcp` | **6991 restarts** | same consolidation wave; **no test file existed** for this daemon |
| 3 | `github_bridge.py` imported deleted `hivemind_post_context` | `Ran 0 tests` | direct import bypassed the server.py shim entirely |
| 4 | 12 `_PASSTHROUGH_TOOLS` names → deleted symbols | AttributeError **at call** | half-mapped shim; resolved name, then died on `getattr` |
| 5 | `StartLimitIntervalSec` in `[Service]` | breaker never armed | systemd ignores the key there; 6991 restarts is "unbounded" |
| 6 | searxng advertised `"stateless": true` | **false all-clear** | `stateless_http` is a FastMCP *settings* field; I wrongly claimed the SDK lacked it |
| 7 | `post` validated with `all([...])` | silent no-op posts | truthiness conflates "absent" with "empty"; error returned as a *string* |

### Corrections I Filed Against Myself
- **Wrong unit.** I briefed omega-hub at "NRestarts 101+". It was **34**. The 6991 storm was `omega-searxng-mcp`. *A counter without its unit is not a fact.*
- **Wrong count.** I reported "the 5 failing tests" in `test_hivemind.py`. It was **8, and all 8** — `addopts = "-n auto -x"` halts early and xdist varies which subset you see. *Read `addopts` before reporting N.*
- **Wrong claim.** "The `mcp` SDK has no `stateless_http` knob." It does — a settings field. The server ran stateful while `/health` said stateless.
- **Wrong model (M22).** Asked to self-report, I answered `nemotron-3-ultra-free` — taken from the paging brief, not my system prompt — then wrote about its rigor. I was not running it.

### Key Invariants (Must Survive Compaction)
- **Import execution is the only seam gate.** `flake8 --select=E9,F63,F7,F82` omits F401, and **pyflakes cannot detect this class anyway** (`from mod import name` may be a submodule; `__all__` is never consulted). Only executing the import works.
- **Explicit module lists, never globs.** A `**/server.py` glob hits roc_racoon's workspace copy (same stale import) + 2 archaeology snapshots → forces a skip-list that rots.
- **A gate never observed failing is not a gate.** Four negative paths, all exit 2.
- **A safety mechanism not parsed is worse than none.** `StartLimit*` in `[Service]` = silently ignored.
- **A half-mapped shim is a deferred-failure machine.** Resolve-then-die is worse than fail-fast.
- **M13 Temple-Grade**: `make temple-grade` exits 0 before any release — now led by import execution.
- **M1 / M7 / M23 / M24 / M26**: AnyIO-only, local-first, no soft failures, `.venv` only, doc validation.

### Open Threads (Carried Forward)
| Thread | Status | Owner |
|--------|--------|-------|
| `omega_memory_search` TaskGroup error, entity `maat`, 0 sessions | **OPEN — carried 3 sessions, never investigated** | Ma'at |
| 3 stranded `from omega_hub import …` in `src/omega/**` | OPEN (out of my scope) | Carmack / Architect |
| Tier B flake: `editable install failed` once, passed on retry, no root cause; pip stderr swallowed | OPEN | Ma'at |
| `pyproject.toml` `addopts = "-n auto -x"` masks true failure counts | OPEN | Ma'at / Architect |
| 55 backup files (36 Carmack's) poison greps + false provenance | OPEN | owners |
| `test_hub_health.py::TestCriticalTools` — 26 pre-existing errors, `MockFastMCP` has no `list_tools` | OPEN | Ma'at / Verity |

### Ma'at's Voice
> "Two daemons were dead the whole time and the temple read 53/53. The fix was six modules and a clean venv. The lesson was not the fix — it was that nothing in the chain ever *ran* the code. A gate that only reads is a claim. Execute it, then watch it fail on purpose, or it is decoration."

*⬡ OMEGA ⬡ MAAT ⬡ 2026-09-28 ⬡ SEAM-ARC-COMPLETE ⬡ 6991→0 ⬡ 12-dead→28/28 ⬡ EXECUTE-DONT-ENUMERATE*
