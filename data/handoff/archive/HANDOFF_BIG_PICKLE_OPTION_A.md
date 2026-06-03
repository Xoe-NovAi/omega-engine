# 🔱 Omega Engine — Big Pickle Review & Option A Handoff
# ⬡ OMEGA ⬡ SOPHIA ⬡ opencode ⬡ trc_big_pickle_handoff ⬡ HANDOFF
**Date**: 2026-06-01
**Target Executor**: Antigravity/Sonnet-4.6 (or any agent picking up Horizon 1 work)
**Pre-flight Snapshot**: ✅ `9c91e97` — `git reset --hard HEAD` to roll back
**Test Baseline**: ✅ **292/292 passing** (was 276)
**Strategy Reference**: `docs/strategy/MASTER_SYNTHESIS_AND_ROADMAP.md`
**Est. Remaining Time**: ~4 hours (Option B)

---

## 🧭 How to Use This Handoff

This handoff documents the **Big Pickle Review** — a comprehensive audit of all Phases A-G execution that was handed off to Gemma 4 31B. The review uncovered **critical bugs** in the Phase C/E/F implementations, plus 17 Mandate 9 violations across 10 files.

**Always**: `source .venv/bin/activate && <command>`
**After every file change**: Run `python3 -m pytest tests/ -x --tb=short` (292 must pass)
**Before every commit**: Full suite — `make test`

---

## §0 SESSION SUMMARY — What Happened

### The Big Pickle Review

After Gemma 4 31B completed Phases A-G (Fleet Redesign, Request Queue, Knowledge Library, Benchmarks, Architecture Docs, CLI Commands), a comprehensive **post-execution audit** was performed. The audit found:

| Finding | Count | Severity |
|---------|-------|----------|
| Orphaned `entity_N` directories not cleaned | 50 | 🔴 Critical |
| Bare `except Exception:` without logging | 17 violations across 10 files | 🔴 Mandate 9 |
| `DATA_DIR` path resolution bugs (wrong parent count) | 3 files | 🔴 Blocking |
| `anyio.to_thread.run_sync` doesn't accept kwargs | 1 file | 🔴 Blocking |
| Falsy-trap (`x or DEFAULT` with `x=0`) | 1 (openai_compat.py) + 1 (request_queue.py) | 🟡 Medium |
| Hardcoded absolute paths | 3 (greek.py, cpu_optimizer.py) | 🟡 Medium |
| `asyncio` import in observability.py (detection only) | 1 | 🟢 Low |
| Source files with no test coverage | 21 | 🟢 Low |

### Phase A: Fleet Redesign (Gemma 4 31B — COMPLETE)
- 26→14 agents consolidated, `opencode.json` updated, 9 agents redesigned
- Quality/Pillar subagents created
- **Verified**: All 50 orphaned `entity_N` directories that Gemma missed were deleted by us

### Phase B: Entity Workspaces (Gemma 4 31B — COMPLETE)
- 25 entity workspaces with soul.yaml/knowledge/workspace created
- **Verified**: 50 orphan directories were NOT cleaned by Gemma — we did it in Option A

### Phase C: Request Queue (Gemma 4 31B — **BUGGY**)
- `src/omega/request_queue.py` created
- **Bugs found & fixed**:
  1. `DATA_DIR` path count: 4 parents for file 3 levels deep → 3 (🔴 path bug)
  2. `anyio.to_thread.run_sync(d.mkdir, parents=True, exist_ok=True)` — kwargs not supported → `lambda:` (🔴 crash)
  3. `days=0 or self.STALE_DAYS` → falsy trap, always becomes 7 (`0 or 7 = 7`) (🔴 logic bug)
  4. Tests used wrong method names (`enqueue` instead of `create_queued_request`)
- **ALL FIXED**. 5/5 request queue tests pass.

### Phase D: Knowledge Library (Gemma 4 31B — **BUGGY**)
- `src/omega/library/catalog.py` created
- **Bugs found & fixed**:
  1. `DATA_DIR` path count: 5 parents for file 4 levels deep → 4 (🔴 path bug)
- 3/3 library tests pass.

### Phase E: Model Tiers & Benchmarking (Gemma 4 31B — **BUGGY**)
- `src/omega/benchmarks/runner.py` + `src/omega/hardware.py` created
- **Bugs found & fixed**:
  1. `DATA_DIR` path count: 5 parents for file 4 levels deep → 4 (🔴 path bug)
  2. HardwareProfile field name mismatch in tests (`cpu_count` vs `num_cpus`)
- 3/3 benchmark + 2/2 hardware tests pass.

### Phase F: Architecture Docs (Gemma 4 31B — COMPLETE)
- 6 architecture docs created, all verified clean
- No bugs found.

### Phase G: CLI Commands (Gemma 4 31B — COMPLETE)
- `oracle_cli.py` extended with queue, library, bench commands
- Shebang in `.venv/bin/omega` fixed (stale path)
- Verifier files updated
- No major bugs found.

---

## §1 WHAT EXISTS NOW

### New Source Files (created during Phases C-E)
| File | Lines | Purpose |
|------|-------|---------|
| `src/omega/request_queue.py` | 294 | Async file-based queue with atomic writes, heartbeat, dead-letter |
| `src/omega/library/catalog.py` | 220 | SQLite-backed multi-dimensional document catalog |
| `src/omega/benchmarks/runner.py` | 180 | LLM benchmark runner with 3-point scale, per-criterion scoring |
| `src/omega/hardware.py` | 85 | CPU/RAM detection, Zen 2 optimization |

### New Test Files (created during Option A)
| File | Tests | Purpose |
|------|-------|---------|
| `tests/test_request_queue.py` | 5 | Queue enqueue/complete/stats/prune |
| `tests/test_library_catalog.py` | 3 | Catalog init/search/stats |
| `tests/test_benchmarks.py` | 3 | Benchmark run/list/import |
| `tests/test_hardware.py` | 2 | Hardware detection smoke tests |
| `tests/test_integration_new_systems.py` | 3 | End-to-end pipeline test |

### New CLI Commands (added to `oracle_cli.py`)
```bash
omega queue-status           # Queue statistics
omega process-queue          # Process pending requests
omega review-pending         # Show review queue
omega queue-prune            # Purge stale requests
omega library curate         # Register a document in the catalog
omega library status         # Library catalog stats
omega library search         # Search the catalog
omega bench run              # Run a benchmark
omega bench compare          # Compare benchmark results
omega bench rank             # Rank models by benchmark score
omega bench list             # List all benchmark runs
```

### Test Count Breakdown
| Area | Tests |
|------|-------|
| Original baseline | 276 |
| New queue tests | 5 |
| New library tests | 3 |
| New benchmark tests | 3 |
| New hardware tests | 2 |
| New integration tests | 3 |
| **Total** | **292** |

---

## §2 THE CRITICAL FINDINGS — Option B (MUST FIX)

After the deep code review, the following issues were identified across **69 source files**:

### 🔴 B1: 17 Bare `except Exception:` Without Logging (Mandate 9)

| # | File | Line | What Fails Silently |
|---|------|------|---------------------|
| 1 | `model_gateway.py` | 405 | Provider pre-check — returns False, no log |
| 2 | `model_gateway.py` | 422 | Observability event — `pass`, no log |
| 3 | `observability.py` | 193 | Provider counter collection |
| 4 | `observability.py` | 209 | `/proc/self/status` fallback |
| 5 | `providers.py` | 319 | Memory estimation → silent zeros |
| 6 | `cpu_optimizer.py` | 385 | `awk` subprocess → wrong RAM estimate |
| 7 | `memory/providers.py` | 135 | Redis `client.close()` |
| 8 | `memory/providers.py` | 256 | Lock file `unlink()` |
| 9 | `library/inbox.py` | 201 | JSON parse → silent default |
| 10 | `library/inbox.py` | 221 | Item fetch → silent None |
| 11 | `loop.py` (worker) | 212 | Lock dir rmdir |
| 12 | `loop.py` (worker) | 241 | File read failure |
| 13 | `loop.py` (worker) | 301 | URL fetch failure |
| 14 | `loop.py` (worker) | 440 | Cycle log append |
| 15 | `review_queue.py` | 121 | TTL sweep unlink |
| 16 | `soul_updater.py` | 86 | Soul YAML load → blank default |
| 17 | `cli/repl.py` | 100, 286 | State/WAD load → silent defaults |

**Fix pattern for each**:
```python
# BEFORE:
except Exception:
    pass  # or return False, return {}
# AFTER:
except Exception as e:
    logger.warning("...: %s", e)
```

### 🟡 B2: Falsy-Trap in Provider Timeout
**File**: `src/omega/oracle/backends/openai_compat.py:102`
```python
config.timeout_seconds = config.timeout_seconds or 15.0
```
**Bug**: `timeout_seconds=0` (no timeout) silently becomes `15.0`.
**Fix**: `if config.timeout_seconds is not None: ...`

### 🟡 B3: Hardcoded Absolute Path in greek.py
**File**: `src/omega/library/greek.py:200`
```python
"path": "/media/arcana-novai/omega_library/models/gguf/Krikri-8b-Instruct-Q5_K_M.gguf",
```
**Bug**: Hardcoded developer machine path. Should reference `config/models.yaml`.

### 🟡 B4: Hardcoded HOME in cpu_optimizer.py
**File**: `src/omega/oracle/cpu_optimizer.py:185-186`
```python
"cp build/bin/llama-server /home/arcana-novai/.local/bin/\n"
```
**Bug**: Hardcoded home directory in build instructions. Use `$HOME`.

### 🟡 B5: Direct `asyncio` import
**File**: `src/omega/observability.py:235`
```python
import asyncio
asyncio.get_running_loop()
```
**Bug**: Mandate 1 minor violation (detection-only usage, last resort fallback).

---

## §3 ENGINE STATE AT HANDOFF

| Metric | Value |
|--------|-------|
| Test count | **292 passing, 0 failing** |
| Source files | ~69 .py files (added request_queue, catalog, runner, hardware) |
| New modules | request_queue, library.catalog, benchmarks.runner, hardware |
| Agents | 14 (fleet redesign complete) |
| Entity workspaces | 25 active |
| Circuit breaker | Consolidated into single AsyncCircuitBreaker (Doom Guy) |
| MCP Hub | Working (Artisan fix applied) |
| Queue system | File-based, atomic, with heartbeat/dead-letter |
| Library catalog | SQLite, 5-dimensional quality scoring |
| Bug count remaining | 17 bare except + 4 others (Option B) |

---

## §4 RECOMMENDED EXECUTION ORDER

### Priority: ESCALATION — Fix `asyncio` Event Loop Conflict
The `.venv` is now installing packages against Python 3.13's asyncio. The `observability.py:235` `import asyncio` call creates a second event loop reference that can cause `RuntimeError: Event loop is closed` on session teardown. **Fix this before anything else.**

### Step 1: Option B — Fix Mandate 9 Violations (~30 min)
1. Open each of the 10 files listed in B1 above
2. Add `logger.warning(...)` before each bare `except Exception:` block
3. Run `make test` after each file change
4. **Verification**: `grep -rn "except Exception:" src/omega/ | grep -v "logger.warning\|trace_id\|raise"` should show only legitimate health-probe exceptions

### Step 2: Option B — Fix Falsy-Trap & Paths (~10 min)
1. Fix `openai_compat.py:102` — `is not None` check
2. Fix `greek.py:200` — use `config/models.yaml` reference
3. Fix `cpu_optimizer.py:185-186` — use `$HOME`
4. Fix `observability.py:235` — `anyio` detection instead of `import asyncio`

### Step 3: Horizon 1 Completion Check
After Option B:
- `make test` = 292 passing
- `grep -rn "except Exception:" src/omega/ | grep -v "logger.warning\|trace_id\|raise"` = zero harmful matches
- All hardcoded paths → config/constants references

---

## §5 COORDINATION NOTES

### For the Next Agent Executing Option B
- There is NO `setup.cfg`. Dependencies are in `pyproject.toml`.
- `errors.py` (at `src/omega/errors.py`) defines `OmegaError` — use it for all typed errors.
- The `.venv` at `.venv/` was created with Python 3.13.
- Some tests use `OMEGA_ENV=test` to switch to mock mode. Always set this for test runs.
- The `tests/` directory uses `pytest` with `anyio` plugin for async tests.

### Files You Will Modify
| File | Change | Lines |
|------|--------|-------|
| `model_gateway.py` | Add logging to 2 bare excepts | ~4 |
| `observability.py` | Add logging to 2 bare excepts + fix asyncio import | ~10 |
| `providers.py` | Add logging to memory estimation except | ~3 |
| `cpu_optimizer.py` | Add logging + fix hardcoded path | ~4 |
| `memory/providers.py` | Add logging to 2 bare excepts | ~4 |
| `library/inbox.py` | Add logging to 2 bare excepts | ~4 |
| `workers/.../loop.py` | Add logging to 4 bare excepts | ~8 |
| `workers/.../review_queue.py` | Add logging to 1 bare except | ~2 |
| `workers/.../soul_updater.py` | Add logging to 1 bare except | ~2 |
| `cli/repl.py` | Add logging to 2 bare excepts | ~4 |
| `openai_compat.py` | Fix falsy-trap | ~1 |
| `greek.py` | Fix hardcoded path | ~1 |

### What NOT to Touch
- `health_monitor.py` — the 2 bare excepts (lines 140, 165) are documented as health probe exceptions per Mandate 9's explicit carve-out. Leave them.
- `oracle.py:873` — has `except Exception:` with `raise` (correctly propagates). Leave it.
- `searxng_client.py:92` — health check returning False. Covered by health probe exception.

---

## §6 ROLLBACK PLAN

```bash
# Full rollback to pre-Big-Pickle state
git reset --hard 9c91e97

# Or partial rollback: revert specific files
git checkout 9c91e97 -- src/omega/request_queue.py
git checkout 9c91e97 -- src/omega/benchmarks/runner.py
git checkout 9c91e97 -- src/omega/library/catalog.py
git checkout 9c91e97 -- src/omega/hardware.py
```

---

## §7 GNOSIS LOG (L1→L2→L3)

**L1 — Narrative**: Gemma 4 31B executed Phases A-G of the fleet redesign. A post-execution audit (Big Pickle Review) found critical bugs in 3 of 7 phases: 50 orphan entity directories not cleaned, 3 path resolution bugs, 1 runtime crash (run_sync kwargs), 1 falsy-trap logic bug. Option A execution fixed all of these + created 16 new tests. The remaining Option B covers 17 Mandate 9 violations + 4 hardened issues.

**L2 — Insight**: Gemma 4 31B was given detailed handoffs with exact file paths and commands. Despite this, the code had systematic errors: every single new file had the DATA_DIR parent count wrong. This is not a random mistake — it's a pattern. The model produced structurally correct code but systematically mis-estimated file-system path depth. Future handoffs should include `Path(__file__).resolve().parent` depth diagrams for each file.

**L3 — Universal Principle**: "Code that looks right but has the wrong constants is invisible." The Gemma-generated code would pass a cursory review — the imports are correct, the async patterns are right, the error types exist. But the DATA_DIR paths resolve one directory too high. This is the engineering equivalent of a perfectly spelled sentence that says the wrong thing. Review must verify **constants and paths** specifically, not just structure and style.

---

*⬡ OMEGA ⬡ SOPHIA ⬡ opencode ⬡ trc_big_pickle_handoff ⬡ HANDOFF*
*Big Pickle Review complete. Option B ready for execution.*
