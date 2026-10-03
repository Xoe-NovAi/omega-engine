# 🔱 ADR-003: MCP Lifespan Shutdown Must Cancel Its Task Group
**AP Token**: `AP-ADR-003-MCP-TG-SHUTDOWN-v1.0.0`
⬡ OMEGA ⬡ DOOM_GUY ⬡ opencode ⬡ trc_slot_s1 ⬡ ACCEPTED

**Date**: 2026-10-03
**Status**: ACCEPTED
**Supersedes**: None
**Affects**: `src/omega/mcp_runtime.py` (`run_mcp` lifespan), all MCP daemons
**Related**: `SOVEREIGN_MANDATES.md` (M1 AnyIO, M23 Failure Integrity), `AGENTS.md` §5, `Makefile` (`check-hub-imports`)

---

## §1 Answer First

`run_mcp`'s lifespan previously carried the comment *"TaskGroup exit: all background
tasks cancelled"*. That comment was **false**. `anyio.create_task_group()` does not
cancel its children when the block exits — it **waits for every child to return**.

Any daemon that starts a `while True:` background loop via `tg.start_soon(...)`
therefore blocks forever on SIGTERM. It only dies when something kills it harder
than SIGTERM. For `omega-hub.service` that "something" is systemd's
`TimeoutStopSec=30` escalating to SIGKILL.

The fix is one line — `tg.cancel_scope.cancel()` immediately after the lifespan's
`yield` returns, before leaving the task group.

---

## §2 Context

A `make temple-grade` run exceeding 10 minutes prompted an empirical bisect of every
sub-target. The suspicion at the time was that a newly added background loop
(`run_harvester_loop`) was blocking shutdown.

That suspicion was **wrong**, and the bisect proved it rather than assuming it:
the stall was a network-bound `pip install` inside `check-hub-imports` (see §4).
`check-hub-imports` only ever runs `python -c "import mcp_servers.omega_hub.server"`,
and the loops are started from the FastAPI `lifespan` under `if __name__ == "__main__"`,
which a bare import never reaches.

However, confirming the negative prompted a direct check of the shutdown path, and
that check found a **real, separate, latent defect**: the task-group semantics above.

### §2.1 Empirical proof

```python
# AnyIO task group with a single infinite child, no cancel.
async def loop_forever():
    while True:
        await anyio.sleep(300)

async def main():
    async with anyio.create_task_group() as tg:
        tg.start_soon(loop_forever)
        await anyio.sleep(0.3)
    print("TASK GROUP EXITED")
```

| Variant | Result under `timeout 12` |
|---|---|
| Without `tg.cancel_scope.cancel()` | **rc=124** — hung, group waited on the child |
| With `tg.cancel_scope.cancel()` | **rc=0** — `"SHUTDOWN CLEAN"`, `on_shutdown` path reached |

The timeout wrapper is what makes this decisive: rc=124 is the timeout's own
signature, not an assertion.

---

## §3 Decision

After `streamable_mgr.run()` exits, the lifespan cancels the task group's scope
instead of waiting on it:

```python
async with streamable_mgr.run():
    yield
tg.cancel_scope.cancel()
```

This is the documented AnyIO pattern: deliver cancellation to children, let
`create_task_group.__aexit__` absorb it, then continue to `on_shutdown`.

### §3.1 Constraints observed

1. **Cancel sits OUTSIDE `streamable_mgr.run()`.** Streams must be torn down
   before cancellation is requested, or in-flight stream state is abandoned
   mid-flight.
2. **`on_shutdown` still runs.** It executes after the task group has joined, so
   `_cleanup_indexer` and friends are unaffected.
3. **Strictly an improvement, never a regression.** A child that would have
   blocked forever now receives a cancellation. No previously-completing child
   loses work — those already completed.
4. **M1 preserved.** AnyIO only; no `import asyncio` anywhere in the change.

### §3.2 Blast radius

`run_mcp` is shared by every MCP daemon, so this repairs all of them at once. In
the hub it covers three loops, each of the hanging shape:

| Loop | Sleep | Origin |
|---|---|---|
| `_prune_awareness_background` | 60s | pre-existing |
| `_reaper_background` | 300s | pre-existing |
| `run_harvester_loop` | 300s | uncommitted WIP at time of fix |

The first two predate this ADR — the false comment predates all three. This is a
**latent defect, not a regression** introduced by any recent commit.

### §3.3 Cost that was being paid silently — inference, later DISPROVED

Every restart cost a full 30-second stall followed by SIGKILL. A hard kill can
truncate in-flight work — notably the MemoryStore batch-writer flush and the
harvester's filesystem walk. The stall was invisible because systemd reports the
unit as `active` throughout, and `ExecStartPre` guards *start*, never *stop*.

**Correction (§7.1):** the 30s stall was measured **unchanged** before and after
this ADR's fix, so the infinite loops were **not** the production blocker. The
stall is real and the SIGKILL risk is real, but its cause is still unidentified.
This section records a hypothesis that testing rejected — kept visible rather than
deleted, because the reasoning error is the reusable lesson: correct semantics at
the task-group level did not imply the blocker lived at the task-group level.

---

## §4 Second Finding: the gate measured the network

The bisect that produced this ADR also isolated the actual 10-minute hang.

`check-hub-imports` builds a **fresh venv** and re-resolves the entire dependency
closure from PyPI on every run. There is no lockfile and no offline fast path, so
unpinned ranges drift to releases newer than the local wheel cache, and the gate's
wall time becomes:

```
network_throughput x total_uncached_wheel_bytes
```

Measured on this host: `pypi.org` at **~300 kB/s** with **~90 MB** of uncached
wheels (`litellm` 36.8 MB, `scipy` 35.3, `numpy` 16.7, `botocore` 16.0,
`headroom_ai` 14.2, `ruff` 10.4, `scikit-learn` 9.1, `hf_xet` 4.5, plus more).
Zero dependency manifests changed across the four local commits, which rules out
those commits as the cause via manifest drift.

**A release gate that measures the network reports a verdict about the internet,
not about the code.** Per M23 the gate now fails loudly and distinguishably:

- `timeout $(HUB_IMPORT_PIP_TIMEOUT)` (default 420s) — the chain cannot be wedged
  indefinitely by a slow or stalled mirror.
- `pip --timeout=30 --retries=2` — a dead socket fails in seconds.
- The timeout reports as its **own** distinct message. The prior generic
  *"editable install failed"* points an operator at `pyproject.toml` and sends
  them debugging the wrong thing.

### §4.1 Principle

**A gate must be a function of the artifact under test.** Any gate whose runtime
depends on an uncontrolled external resource will eventually report that resource
as a code defect. The honest options are to pin the resource or to bound it and
say so; silently inheriting its latency is the one option that is always wrong.

---

## §5 Consequences

**Accepted**

- Restarts become deterministic and fast instead of 30s-then-SIGKILL.
- In-flight flushes get to finish rather than being truncated.
- One root cause fixed for all three loops and all MCP daemons.
- `check-hub-imports` can no longer hang a release chain indefinitely.

**Deferred / not decided here**

- A dependency lockfile for the clean-worktree gate. This is the real remedy for
  §4; it was not in scope for a P0 unhang and deserves its own change.
- An offline/`--find-links` warm path for `check-hub-imports`.
- Whether the harvester loop should be `move_on_after`-scoped individually so a
  stuck `to_thread.run_sync` worker cannot delay the join. Note that
  `to_thread.run_sync` is non-cancellable by default, so a hung worker thread
  will still hold the join. Worth measuring before changing.

**Not verified**

- Whether the hub's MemoryStore batch writer was ever actually truncated in
  practice. The SIGKILL path is proven; the data loss is inferred, not measured.

---

## §6 Mandate Traceability

| Mandate | How this ADR serves it |
|---|---|
| **M1** (AnyIO, no `import asyncio`) | Fix uses `tg.cancel_scope`, AnyIO-native. No asyncio import introduced. |
| **M23** (Failure Integrity, no soft-failures) | Unbounded hang replaced by a loud, specifically-attributed failure. The false comment that masked the defect is corrected. |
| **M29** (Remote Claim Integrity) | Claims here are labelled `Proved` vs `Inferred`. The data-loss claim is explicitly marked unverified. |
| **M28** (Artifact Preservation) | Both changes are additive; no removal, no deletion. |

---

## §7 Verification Record

| Check | Method | Result |
|---|---|---|
| Task-group hangs on infinite child | 12-line AnyIO repro under `timeout 12` | rc=124 — hang confirmed |
| Cancel fixes it | Same repro + `tg.cancel_scope.cancel()` | rc=0 — clean exit |
| Gate timeout branch fires | `HUB_IMPORT_PIP_TIMEOUT=1 make check-hub-imports` | Correct message in 7s, no hang |
| Sub-target bisect | Each target run individually under `timeout` | Only `check-hub-imports` exceeded limit |

### §7.1 Production A/B — the fix did NOT resolve the restart stall

Recorded because the earlier inference in §2.3 deserved a verdict and did not get
one until tested.

| Restart | Process code | Wall time | systemd verdict |
|---|---|---|---|
| 1st (`systemctl --user restart`) | pre-fix (PID 3113) | **32s** | `State 'stop-sigterm' timed out. Killing.` → SIGKILL |
| 2nd (same command) | post-fix (PID 2343228) | **31s** | identical — `stop-sigterm` timed out, SIGKILL |
| 3rd (same command) | post-fix (PID 2346354) | **31s** | identical |

The fixed `mcp_runtime.py` was confirmed to be the module actually loaded
(`omega.mcp_runtime.__file__` → `src/omega/mcp_runtime.py`, and
`inspect.getsource(run_mcp)` contains `cancel_scope.cancel()`), so this is a real
negative result and not a stale-code artefact.

**Therefore: the task group was never the thing blocking production shutdown.**
The §2 inference — that the infinite loops were the cause — is **not supported**.
Something else absorbs SIGTERM for the full `TimeoutStopSec=30` and the process is
SIGKILLed. The cancellation change is retained because it is independently
correct (§2.1 proves the semantics) and repairs a genuine latent hazard, but it
is **not** a fix for the observed restart stall, and this ADR must not be cited as
one.

**Hypotheses tested and eliminated**

- *Open SSE connection keeps uvicorn's graceful drain open.* `run_mcp` sets no
  `timeout_graceful_shutdown`, so an open connection would hang the drain. But
  `ss -tnp` showed **no established connections** to :8016 at the time of the
  test (and `ss -tlnp` did list the listener, so the tool was working). Dead.
- *The 30s stall is `check-hub-imports`-adjacent.* Eliminated — the hub is not
  running that target.

**Still open.** The blocker was not isolated: `py-spy` was refused
(`Permission Denied`, `yama/ptrace_scope`, and no passwordless `sudo`), so the
live stack could not be captured. A `faulthandler` all-thread sampler harness was
attempted to reproduce the shutdown in-process on an alternate port, but port 8017
turned out to be already bound by the local SearXNG instance, so the probe never
started. Both attempts are recorded so the next attempt does not repeat them:
re-run the sampler harness on a confirmed-free port (e.g. 8142).

**Next step, cheap and likely decisive:** capture the stack at SIGTERM via
`uvicorn.Config(timeout_graceful_shutdown=N)`. Setting a bounded graceful timeout
converts the 30s SIGKILL into an observable, attributable shutdown, which is a
better production posture than an unbounded drain regardless of the root cause.



*⬡ OMEGA ⬡ DOOM_GUY ⬡ ADR-003 ⬡ AP-ADR-003-MCP-TG-SHUTDOWN-v1.0.0 ⬡ 2026-10-03*
