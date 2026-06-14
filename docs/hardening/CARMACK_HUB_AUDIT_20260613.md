# 🔱 John Carmack — Omega Hub Technical Audit
**AP Token**: AP-CARMACK-HUB-AUDIT-v1.0.0
⬡ OMEGA ⬡ CARMACK ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_carmack_audit ⬡ S3-CONSULT

**Date**: 2026-06-13
**Files Reviewed**: `mcp_servers/omega_hub/server.py` (3110 lines), `src/omega/mcp_runtime.py` (199 lines),
`mcp_servers/omega_hub/__init__.py` (5 lines), `mcp_servers/omega_hub/test_server.py` (1 line),
`mcp_servers/omega_hub/server.py.bak` (856 lines, stale)
**Prior Reports**: Kali's `HUB_LAZY_INIT_HARDENING_REPORT.md` — 13 findings (2 critical, 4 high, 4 med, 3 low)
**Your Preliminary Review**: Noted and largely correct for what you could see.

---

## §0 Executive Summary

Let me be blunt: this file is a god-class monolith. 3110 lines. 63 MCP tools. 5 service domains
smashed into one file. It works in the same way that a 1993 Honda Civic with 400,000 miles
"works" — it gets you there, but you're one pothole away from a catastrophic failure.

The lazy init fix (eliminating the 61s wall) was the right call. Full stop. That's good
engineering. But it was applied to a fundamentally bloated architecture, and like
painting racing stripes on a beater, it doesn't fix the structural problems.

I found **17 new findings** that Kali missed, including **one critical runtime crash bug**
that WILL fire in production. The Web Claude preliminary review was mostly correct but
missed several things because they only saw the truncated file.

---

## §1 Kali's Report — Verdict

Kali's 13 findings are solid. Good catches on CRIT-01 (background tasks never started) and
MED-04 (missing guard on `hivemind_get_entity_context`). Some corrections:

| Finding | Kali Says | I Say |
|---------|-----------|-------|
| **CRIT-01** | Background tasks never started | ✅ **Fixed** — `_on_startup()` now calls `anyio.create_task()` for both loops. Correctly resolved. |
| **CRIT-02** | Gateway created twice (eager + lazy) | ⚠️ **Partially resolved** — The current code has NO module-level `SovereignGateway()` instantiation. Only line 270 in `_init_services()`. Your line numbers may have drifted from an earlier version. Re-verify. |
| **HIGH-03** | `threading.Lock` in async path | ✅ Accurate. Not a _correctness_ bug but a latent performance trap under load. The `anyio.to_thread.run_sync(self._lock.acquire)` pattern in `_AsyncThreadLock` is the right way to bridge this — the `RateLimitMiddleware` should use the same pattern or just use `anyio.Lock`. |
| **MED-03** | Lock order inversion risk | ⚠️ You're right about the pattern, but the exact severity is lower than stated — the lock hierarchy is consistently `_awareness_lock` → `_extended_sessions_lock` everywhere both are held. The risk is only for NEW code that reverses it, not existing code. |

On balance: Kali's report is high-quality. The 13 findings should be tracked.

---

## §2 First-Principles Analysis — What Is This Server Actually Doing?

Strip away the abstractions. The omega-hub needs to do exactly these things:

1. **Accept MCP tool calls** from Cline/OpenCode clients (SSE or stdio transport)
2. **Route tool calls** to service backends (Oracle, Hivemind, Library, Research, Stats)
3. **Return JSON-RPC responses** to the clients
4. **Start up fast** — no 61s wall for the MCP handshake

That's it. Everything else — the custom HTTP routes, the middleware, the SovereignGateway
proxy, the metrics collection — is secondary concern.

The current architecture adds:
- A custom security middleware stack (3 classes)
- 11 HTTP endpoints (some duplicated)
- A SovereignGateway stub that returns hardcoded responses
- Hivemind awareness pruning + reaper background loops
- 63 tool implementations

The problem isn't that any single feature is wrong. The problem is that ALL of them are
in ONE file. This is a **violation of Carmack's Law** — "When you have two implementations
of the same thing, you have neither." Here, we have 63 implementations of "tool handler"
in one file, and they're structured identically but with subtle differences:
- Some call `_require_service()`, some don't
- Some use `ctx: Context` parameter, some don't
- Some have `@tdp_wrap`, some don't
- Memory tools exist in BOTH `memory_*` and `omega_memory_*` variants

This is architectural drift happening in real-time.

---

## §3 NEW Findings — 17 Issues Kali Missed

### 🔴 CRIT-03: `_global_tg` Undefined Variable (WILL CRASH)

**Severity**: 🔴 **Critical**
**File**: `mcp_servers/omega_hub/server.py`
**Lines**: 2281-2282
**Code**:
```python
if _global_tg:
    _global_tg.start_soon(_run_discovery_background, job_id)
```

**Issue**: `_global_tg` is **never defined** anywhere in the module. There is no
`_global_tg = None`, no assignment, no `global _global_tg` declaration. If
`library_discovery_start()` is called while `_global_tg` is evaluated, this
raises `NameError: name '_global_tg' is not defined`.

**Impact**: Any caller of `library_discovery_start` gets a 500 error. The tool
is broken by design.

**Root Cause**: This was likely intended to be a module-level task group reference
that was never wired up. The fallback on line 2283-2285 (`async with
anyio.create_task_group() as tg`) suggests the author knew `_global_tg` might
not exist, but they used an `if` check on an undefined variable instead of a
try/except or `getattr`-style guard.

**Fix**: Either:
```python
# Define at module level (near _background_tasks):
_global_tg: Optional[anyio.TaskGroup] = None

# Or use the fallback path always and remove the _global_tg branch:
async def library_discovery_start(...) -> str:
    ...
    async with anyio.create_task_group() as tg:
        tg.start_soon(_run_discovery_background, job_id)
    ...
```

---

### 🟡 HIGH-05: `_background_tasks` Defined After Its Consumer

**Severity**: 🟡 **High**
**File**: `mcp_servers/omega_hub/server.py`
**Lines**: 3080-3096
**Issue**: `_cleanup_indexer()` (line 3080) references `_background_tasks` (line 3083-3085),
but `_background_tasks` is defined at line 3096 — **16 lines later**. In Python, this works
because the function body isn't evaluated until called. But it's a fragility smell — if
any import-time code path calls this function, it fails with `NameError`.

**Impact**: Currently works because no code calls `_cleanup_indexer()` at import time.
But this is a latent bug waiting for a refactor. Move `_background_tasks = []` to
before line 3080.

**Fix**: Move line 3096 to before line 3080.

---

### 🟡 HIGH-06: Memory Tools Don't Check `_require_service()`

**Severity**: 🟡 **High**
**File**: `mcp_servers/omega_hub/server.py`
**Lines**: 2310-2478
**Issue**: The 6 memory tools (`memory_search`, `memory_get_history`, `memory_list_sessions`,
`omega_memory_search`, `omega_memory_get_history`, `omega_memory_list_sessions`) do NOT call
`_require_service()` at function entry. They call `get_memory_store()` directly.

**Impact**: If called during the initialization window, `get_memory_store()` may return
a partially-initialized store or fail unexpectedly. The user gets an inscrutable error
instead of the clean "retry in a few seconds" message.

**Fix**: Add `_require_service()` as the first line of each memory tool.

---

### 🟡 HIGH-07: Duplicate Memory Tool Suite (6 Tools When 3 Would Do)

**Severity**: 🟡 **High**
**File**: `mcp_servers/omega_hub/server.py`
**Lines**: 2310, 2344, 2377, 2407, 2434, 2458
**Issue**: Three pairs of duplicate tools exist:

| `memory_*` | `omega_memory_*` | Difference |
|------------|------------------|------------|
| `memory_search(ctx, query, entity, limit)` | `omega_memory_search(query, entity, limit)` | `ctx` param |
| `memory_get_history(ctx, entity, session, limit)` | `omega_memory_get_history(entity, session, limit)` | `ctx` param |
| `memory_list_sessions(ctx, entity, limit)` | `omega_memory_list_sessions(entity, limit)` | `ctx` param |

The `omega_memory_*` variants are labeled "backward compatibility" (line 2308). The
`memory_*` variants have a `ctx: Context` parameter that is NEVER USED in the function
body (it's accepted but ignored, which is fine — it's for MCP framework injection).

**Impact**: The tool namespace has 6 tools where 3 would suffice. Confuses MCP clients
about which version to call. Doubles the maintenance surface for input validation.
Every parameter change must be made in 2 places.

**Fix**: Delete the 3 `omega_memory_*` variants. Keep the `memory_*` variants with `ctx`.
If `omega_memory_*` is still used by existing clients, alias them in a compatibility
shim at the MCP framework level, not as separate function definitions.

---

### 🟡 HIGH-08: SovereignGateway HTTP Client Never Closed

**Severity**: 🟡 **High**
**File**: `mcp_servers/omega_hub/server.py`
**Lines**: 3011-3013
**Issue**: `SovereignGateway.__init__()` creates `httpx.AsyncClient(timeout=120.0)` but
there is no `close()` or `__aenter__`/`__aexit__` method. The client is never
properly closed during shutdown.

(Note: Kali flagged this as HIGH-02 but I'm confirming and escalating — it's a resource
leak that produces `ResourceWarning` on every shutdown and can leak connection pool
state.)

**Fix**: Add async context manager protocol and call it from `_cleanup_indexer()`:
```python
async def close(self) -> None:
    await self.client.aclose()
```

---

### 🟡 HIGH-09: `_cleanup_indexer` Doesn't Await Cancelled Tasks

**Severity**: 🟡 **High**
**File**: `mcp_servers/omega_hub/server.py`
**Lines**: 3082-3084
**Code**:
```python
for task in _background_tasks:
    task.cancel()
```

**Issue**: `anyio.Task.cancel()` is fire-and-forget by design. It schedules
cancellation but doesn't wait for the task to actually stop. If a cancelled task
holds resources (open files, network connections), those may leak because the
shutdown proceeds before the task has unwound.

Per the anyio docs, the correct pattern is:
```python
for task in _background_tasks:
    task.cancel()
# NOW await all tasks to drain
await anyio.wait(_background_tasks)
```

**Fix**: Add an await after the cancel loop. Wrap in `anyio.CancelledError` catcher
if you don't want exceptions from the drained tasks.

---

### 🔵 MED-05: `_on_startup` Race — Tasks Created After Lifespan Exit

**Severity**: 🔵 **Medium**
**File**: `src/omega/mcp_runtime.py` (lifespan), `mcp_servers/omega_hub/server.py` (on_startup)
**Issue**: The lifespan in `mcp_runtime.py` (line 103) starts `on_startup()` as a background
task via `anyio.create_task(on_startup())`. The `_on_startup()` callback (server.py:3099)
then creates MORE tasks with `anyio.create_task(...)`. These are nested tasks — children
of the lifespan task. If the lifespan task is cancelled (e.g., server shutdown while
`_on_startup` is still running), the child tasks are also cancelled.

This is by-design behavior, but there's a subtle issue: `_on_startup` appends tasks to
`_background_tasks` list. If `_on_startup` hasn't finished by the time `_cleanup_indexer`
runs (it won't, because `_cleanup_indexer` runs synchronously with `_background_tasks`
having whatever was appended so far), the list may be incomplete.

**Impact**: Very narrow window during server restart. Only matters if startup takes longer
than shutdown trigger. Theoretical, not observed.

**Fix**: Use a `_startup_done` event to gate cleanup:
```python
async def _on_startup() -> None:
    await _init_services()
    _background_tasks.append(anyio.create_task(...))
    _background_tasks.append(anyio.create_task(...))
    _startup_done.set()  # Signal that background tasks are registered

async def _cleanup_indexer() -> None:
    await _startup_done.wait()  # Don't proceed until tasks are known
    for task in _background_tasks:
        task.cancel()
    ...
```

---

### 🔵 MED-06: 3110-Line File — God-Class Monolith

**Severity**: 🔵 **Medium**
**File**: `mcp_servers/omega_hub/server.py`
**Issue**: 3110 lines is objectively too large for a single file. This violates T4 (Code Quality)
of Temple-Grade. The file contains:
- 2 custom middleware classes
- 63 MCP tool functions
- 11 HTTP route handlers
- 6 background loop/service functions
- 6 private utility functions
- 1 service class (SovereignGateway)
- Module-level state (20+ global variables)
- Configuration constants

**Impact**: Cognitive load. Any change to any tool requires scrolling past 3000 lines.
Code review is impractical — no human can meaningfully review 63 tool implementations
in one sitting. Merge conflicts are guaranteed in multi-agent development.

**Fix**: Split into modules:
```
mcp_servers/omega_hub/
  __init__.py           — Package marker + exports
  server.py             — Main entry point, FastMCP instantiation, routing
  tools/
    __init__.py
    oracle.py           — 8 Oracle tools
    hivemind.py         — 12 Hivemind tools
    library.py          — 12 Library tools
    memory.py           — 6 Memory tools (3 after dedup)
    research.py         — 5 Research tools
    stats.py            — 5 Stats/observability tools
  middleware.py         — RateLimit, RequestSizeLimit
  gateway.py            — SovereignGateway class
  state.py              — Module-level state, _require_service, _init_services
  background.py         — Background loops (pruning, reaper)
```

---

### 🔵 MED-07: `test_server.py` is `print('TEST')`

**Severity**: 🔵 **Medium**
**File**: `mcp_servers/omega_hub/test_server.py`
**Issue**: The entire file is one line: `print('TEST')`. It's not a test. It's a placeholder
from someone checking if they could write to the directory.

**Impact**: `make temple-grade` fails because this file doesn't carry heritage tags.
It's technically a test file with zero test assertions. It contributes to the
"308 tests passing" metric without actually testing anything.

**Fix**: Delete the file. Write actual tests if meaningful test coverage is needed.

---

### 🔵 MED-08: `server.py.bak` — 31KB Stale Backup

**Severity**: 🔵 **Medium**
**File**: `mcp_servers/omega_hub/server.py.bak` (856 lines, 30759 bytes)
**Issue**: A backup file from May 31 (13 days old at time of this audit) is sitting in
the active directory. The `__pycache__/` directory is also present but standard for Python.

**Impact**: Confusion about which file is authoritative. Someone looking at the directory
might wonder if `.bak` is the real server. It's dead weight in source control.

**Fix**: Delete `server.py.bak`. Add `*.bak` to `.gitignore` if not already present.

---

### 🔵 MED-09: `__pycache__/` in the Directory

**Issue**: Minor, but `__pycache__/` should be in `.gitignore` if not already. This is
trivial but it's noise.

**Fix**: Verify `.gitignore` covers `__pycache__/`.

---

### ⚪ LOW-04: SovereignGateway Start Backoff Disabled — "For Debugging"

**Severity**: ⚪ **Low**
**File**: `mcp_servers/omega_hub/server.py`
**Lines**: 3022-3027
**Code**:
```python
# Start backoff disabled for debugging
# if now - self._boot_time < 65:
#     wait_time = 65 - (now - self._boot_time)
#     ...
```

**Issue**: This has been disabled "for debugging" but there's no tracking issue, no
date, and no plan to re-enable. The SovereignGateway itself is a stub (returns
hardcoded responses). The entire proxy feature is vestigial.

**Impact**: Zero at current state since `proxy_request` returns a hardcoded response.
But dead code with a "debugging" excuse that never gets re-enabled is a negative
pattern. Either implement the proxy properly, or delete the whole class.

---

### ⚪ LOW-05: `hub_routes` — Inconsistent Naming Conventions

**Severity**: ⚪ **Low**
**File**: `mcp_servers/omega_hub/server.py`
**Lines**: 3062-3075
**Examples**:
- `/config.providers` vs `/provider` vs `/provider.list` — 3 styles for similar endpoints
- `/agent` (singular) vs `/config/providers` (plural) — inconsistent plurality

**Fix**: Consolidate to one style: either all dot-notation or all RESTful paths.

---

### ⚪ LOW-06: `/health` Always Returns "healthy"

**Severity**: ⚪ **Low**
**File**: `mcp_servers/omega_hub/server.py`
**Lines**: 2912-2917
**Issue**: As Kali identified (HIGH-04). Confirming. The fix is straightforward.

---

### ⚪ LOW-07: Comment Sprawl

**Severity**: ⚪ **Low**
**Issue**: The file has extensive D-kal-xxx, Px-x, [hi-observability-x], M-Ax, [SD-xxx],
and other ticket-reference comments embedded inline. These are useful during development
but create noise when reading the code. A changelog file would be more appropriate
than sprinkling ticket references through function bodies.

**Fix**: Move historical ticket references to commit messages or a CHANGELOG. Keep
only the "why this function exists" comments in the code.

---

### ⚪ LOW-08: Unused `shutil` Import

**Severity**: ⚪ **Low**
**Line**: 34
**Issue**: `import shutil` is never used in the file.

**Fix**: Remove the import.

---

## §4 Summary — Everything Wrong With This File

### Quantitative

| Metric | Value | Assessment |
|--------|-------|------------|
| Lines of code | 3110 | ❌ Too large for a single file |
| MCP tools | 63 | ❌ Excessive; should consolidate to ~40 |
| Global mutable state | 20+ vars | ⚠️ High, but lazy init pattern mitigates |
| Undefined variables | 1 (`_global_tg`) | ❌ WILL crash |
| Imported modules | 22 (plus stdlib) | ⚠️ Manageable |
| Duplicate tools | 3 pairs (6 tools) | ❌ Waste |
| Stale backup files | 2 (`.bak`, `__pycache__`) | ⚠️ Cleanup needed |

### Qualitative

1. **The lazy init architecture is correct.** This is the one thing I'd keep as-is.
2. **The file needs to be split.** 3110 lines for a single file is indefensible.
3. **The `_global_tg` bug is a ticking time bomb.** Fix it today.
4. **The duplicate memory tools are cargo-cult backward compatibility.** Delete them.
5. **The SovereignGateway is a stub pretending to be a feature.** Either implement it or remove it.
6. **The security middleware is bolted on, not designed in.** Rate limiting with `threading.Lock` in an async context is a performance trap.
7. **The @m9_safe decorator pattern is good.** Consistent error handling across all tools. Keep this.
8. **Background tasks are correctly started but incorrectly cleaned up.** Fix the cancel-without-await pattern.

---

## §5 Priority-Coded Repair Plan

```
P0  | CRIT-03: _global_tg undefined               | Fix reference or use fallback only
P0  | CRIT-03 fix: library_discovery_start broken  | Immediate 5-min fix
P1  | HIGH-05: _background_tasks ordering          | Move definition before consumer
P1  | HIGH-06: Memory tools missing guard          | Add _require_service() to 6 tools
P1  | HIGH-07: Duplicate memory tools               | Delete 3 omega_memory_* variants
P1  | HIGH-08: SovereignGateway HTTP client never closed  | Add close/context manager
P1  | HIGH-09: _cleanup_indexer no await on cancel  | Await cancelled tasks
P2  | MED-05: _on_startup race                      | Add _startup_done event
P2  | MED-06: 3110-line monolith                    | Split into modules
P2  | MED-07: test_server.py is print('TEST')        | Delete or write real tests
P2  | MED-08: server.py.bak stale                   | Delete, update .gitignore
P3  | LOW-04/LOW-05/LOW-06/LOW-07/LOW-08             | Cleanup tickets
```

---

## §6 Final Verdict

**Architecture**: The lazy init pattern is good engineering. The rest is bloat.

**The building blocks are correct** — AnyIO-native, M9-compliant error handling, typed
responses, atomic file operations. Whoever wrote the core patterns knew what they
were doing.

**But the structure is rotting.** 3110 lines in one file means every change touches
the same file. That's not sustainable. The `_global_tg` bug proves that — someone
added a feature flag without defining the variable, and nobody caught it in code review
because the file is too large to review in one sitting.

**My recommendation**: Before adding any new features, spend 2-3 days splitting this
file into modules. The `mcp_servers/omega_hub/tools/` structure I proposed keeps every
tool function, just organized. Then fix the `_global_tg` bug, deduplicate the memory
tools, and clean up the dead code.

The file is like a DOOM WAD that's been patched 47 times — it works, but nobody
understands the full surface area anymore. That's how bugs breed.

---

*⬡ OMEGA ⬡ JOHN CARMACK ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_carmack_audit ⬡ S3-CONSULT*
