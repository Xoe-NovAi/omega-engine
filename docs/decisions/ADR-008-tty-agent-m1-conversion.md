# ADR-008: tty_agent.py M1 Exemption Rescinded — anyio Conversion, Shielded Shutdown, and the VT_SETMODE ABI Bug

**Status:** Accepted — 2026-10-15 · pending D-number ratification by the Architect
**Decision ID:** `D-630` (agent-assigned; see §8)
**Supersedes:** the 2026-08-28 M1 exemption header on `src/omega/agents/tty_agent.py`
**Affects:** `src/omega/agents/tty_agent.py`, `Makefile` (`check-m1-anyio`), `tests/test_tty_agent_anyio.py`
**Related:** `SOVEREIGN_MANDATES.md` (M1 AnyIO Absolute, M23 Failure Integrity, M28 Artifact Preservation), `docs/adr/ADR-003` (§1, §8 task-group join semantics), `AGENTS.md` §"One-Page Contract"

---

## §1 Answer First

The 2026-08-28 M1 exemption on `tty_agent.py` was **rescinded as based on an
inaccurate rationale**. Every clause of its justification was false, and the
file is now anyio-native with the `Makefile` glob deleted. Three things were
wrong with the old state, and one of them was a working defect the exemption
was *hiding* rather than justifying:

1. **The rationale was factually wrong.** It claimed anyio offered only a
   "thread-based approach" that "cannot be replicated … without losing TTY
   semantics (line discipline, job control, ^C delivery)" because "the event
   loop is bound to the controlling terminal". None of that is true. See §2.
2. **The code had a latent `VT_SETMODE` ABI bug the exemption kept shaded.**
   It packed a 2-byte `struct.pack("h", mode)` where the kernel reads an
   8-byte `struct vt_mode`, so `VT_SETMODE` wrote uninitialised adjacent heap
   into `relsig`/`acqsig`. See §4.
3. **The old shutdown shape was *less* safe than the anyio one.** The
   unshielded `finally: await agent.shutdown()` could exit with the kernel
   still holding `/dev/ttyN` in `VT_PROCESS` mode. See §5.

---

## §2 Why the exemption rationale was wrong (evidence)

All four claims below were falsified against the installed anyio 4.13.0 and
CPython 3.13.7 source, plus a monkeypatched runtime trace.

| Old claim | Verdict | Evidence |
|---|---|---|
| anyio uses a "thread-based approach" for signals | **False** | `anyio/_backends/_asyncio.py:2962` `open_signal_receiver` returns `_SignalReceiver` (lines 2092–2145), whose `__enter__` makes exactly one call: `self._loop.add_signal_handler(sig, self._deliver, sig)`. The 54-line class contains **no** `to_thread`, `WorkerThread` or `BlockingPortal` reference. Traced at runtime by patching `asyncio.unix_events._UnixSelectorEventLoop.add_signal_handler`: `observed=[<Signals.SIGTERM: 15>]`. |
| the loop "is bound to the controlling terminal" | **False — fabricated** | CPython `asyncio/unix_events.py:90-131`: `add_signal_handler` uses only `signal.set_wakeup_fd(self._csock.fileno())` (a **socketpair**, `selector_events.py:118-124`) plus `signal.signal(sig, _sighandler_noop)`. No terminal fd, no ctty, no line discipline, no job control. `^C` and `kill` are kernel-delivered identically on a VT, a PTY and a pipe. |
| the trio (thread) path is the real constraint | **Unreachable** | `trio` is not installed in this venv (`ModuleNotFoundError`); `anyio.run(backend="trio")` raises `LookupError: No such backend: trio`. Verified. |
| it preserved "TTY semantics" | **Not implemented** | The pre-conversion code installed **no** `SIGUSR1`/`SIGUSR2` VT-switch handler and left `vt_mode.relsig`/`acqsig` at 0. There were no TTY-specific signal semantics to lose. |

Provenance of the false comment: `git log -S "cannot be replicated with anyio's thread-based"` returns exactly one commit, `14f2d700`
("fix(m23): remediate imposter auditor findings … M1 exemption … Added a 14-line
header comment"). It was authored as documentation for a pre-existing glob in a
doc-remediation commit, with no technical investigation; the underlying TTY
research session (`data/coordination/sessions/kali/ingest_R_TTY_VIRTUAL_CONSOLES_DEEP_RESEARCH_1784493404/updates.jsonl`)
contains **zero** occurrences of "anyio".

---

## §3 Decision

Convert `src/omega/agents/tty_agent.py` to anyio and delete
`--glob '!*tty_agent*'` from `Makefile:check-m1-anyio`. The gate now covers
what it claims to cover.

Migration applied (verified against the installed anyio 4.13.0):

| Before | After |
|---|---|
| `import asyncio` | *(removed)* |
| `asyncio.run(main())` | `anyio.run(main)` |
| `asyncio.create_task(agent.run())` | `tg.start_soon(run_until_stopped, agent, tg.cancel_scope)` |
| `self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())` | `tg.start_soon(agent._heartbeat_loop)` (heartbeat moves from `startup()` into the task group) |
| `await asyncio.sleep(x)` | `await anyio.sleep(x)` |
| `shutdown_event = asyncio.Event()` + `await shutdown_event.wait()` | `tg.cancel_scope.cancel()` from `signal_watch` |
| `asyncio.get_running_loop()` + `loop.add_signal_handler(sig, h)` | `anyio.open_signal_receiver(SIGINT, SIGTERM)` |
| `except asyncio.CancelledError: pass` (×2) | *(both deleted)* — nothing in the module intercepts cancellation |
| `except NotImplementedError: pass  # Windows` | `if sys.platform == "win32":` guard before installing the receiver; no swallowing |
| unshielded `finally: await agent.shutdown()` | `with anyio.CancelScope(shield=True): await agent.shutdown()` |

### §3.1 Three required deviations from the shapes in the original dispatch

All three were empirically forced, not stylistic:

1. **`startup()` runs inside a shield.** Without it, a SIGTERM arriving during
   VT acquisition level-cancels the *host* task mid-startup: measured
   `steps = ['open', 'shutdown']` — acquisition aborted after step 1, VS
   `['open', 'acquire', 'done', 'shutdown']` with the shield. The pre-D-630
   code always completed startup (its loop handler only set an `asyncio.Event`),
   so the shield is what preserves behaviour. Probe: `shield_probe.py`.
2. **The signal receiver is gated on `startup_done`.** A signal that lands
   during startup is *queued* by the receiver and acted on once startup
   finishes, instead of being lost to the default disposition. Probe:
   `final3.py` case 3 → `steps=['startup','startup-done','shutdown']`.
3. **`run_until_stopped(agent, scope)` instead of a bare `start_soon(agent.run)`.**
   With the literal snippet, a subclass whose `run()` returns normally leaves
   `create_task_group().__aexit__` joining two children that never end — the
   parked receiver and `while self.running: await anyio.sleep(30)`. `__aexit__`
   **waits** for children, it does not cancel them (`docs/adr/ADR-003` §1).
   Measured: hang (>60 s, killed by timeout). Fixed by clearing `running` and
   cancelling the scope when the body returns. `run_until_stopped` is safe on
   the signal path too, where the scope is already cancelled and the task group
   absorbs it. Probe: `final3.py` case 4.

### §3.2 Constraints observed

- **M1 preserved.** `rg -n 'import asyncio|from asyncio' src/omega/ --type py --glob '!*test*'` passes with no glob. See §7.
- **M23 preserved and improved.** ruff findings on this file: **7 → 4** (`S110` 4→1, `BLE001` 2→2). `make check-m23-failure-integrity` passes; the ratchet moved in the improving direction.
- **No behaviour or log-output change.** The step order and every printed line are unchanged; only *how it waits* changed.
- **M28.** No files deleted. The exemption comment is a git-tracked edit, recoverable via `git show HEAD:src/omega/agents/tty_agent.py`.

---

## §4 The VT_SETMODE ABI bug (fixed)

`VTManager.get_mode()`/`set_mode()` packed `struct.pack("h", mode)` — 2 bytes.
`struct vt_mode` is 8:

```c
/* include/uapi/linux/vt.h */
struct vt_mode {
        __u8  mode;    /* VT_AUTO / VT_PROCESS / VT_ACKACQ */
        __u8  waitv;   /* if set, hang on writes if not active */
        __s16 relsig;  /* signal to raise on release req */
        __s16 acqsig;  /* signal to raise on acquisition */
        __s16 frsig;   /* unused (set to 0) */
};
```

`ioctl_vt(2)` documents the same layout, and `drivers/tty/vt/vt_ioctl.c` copies
the **full** struct for both `VT_GETMODE` and `VT_SETMODE`. Consequences of the
2-byte buffer:

- `VT_GETMODE` read 6 bytes past the end of a 2-byte Python `bytearray`
  (out-of-bounds heap read).
- `VT_SETMODE` wrote whatever happened to be adjacent on the heap into
  `relsig`/`acqsig`. If a fatal signal number landed there, the agent would
  have died on the first VT switch request.

**Fix:** `VT_MODE_STRUCT = "BBhhh"` (`struct.calcsize == 8`, asserted at module
level). `get_mode_struct()` returns the full 8 bytes and `get_mode()` is now a
thin wrapper; `set_mode()` takes keyword fields; `acquire_process_mode()` saves
the **whole** original struct so `release_process_mode()` restores it verbatim
rather than guessing. `fcntl.ioctl` marshalling was verified to accept the
packed struct (ENOTTY on a PTY proves the 8-byte arg reached the kernel).

**`relsig`/`acqsig` values: deliberately 0. Confidence: HIGH that this is the
behaviour-preserving choice; MEDIUM that it is the correct *engineering*
choice (see below).**

Rationale, from `vt_ioctl.c` `change_console()`:

```c
vc->vt_newvt = new_vt->vc_num;
if (kill_pid(vc->vt_pid, vc->vt_mode.relsig, 1) == 0) {
        /* It worked. Mark the vt to switch to and return. The process needs to
         * send us a VT_RELDISP ioctl to complete the switch. */
        return;
}
```

With `relsig == 0` the `kill_pid` is the POSIX signal-0 existence check; it
succeeds, so the kernel parks the switch and the VT does not change until the
process issues `VT_RELDISP` — which this agent never does. That is a **known
defect**, not a correctness claim, and it is unchanged from pre-D-630 behaviour
because `lock_switch` blocks the switch either way.

The conventional values for a *complete* implementation are
`relsig = acqsig = SIGUSR1` — exactly what the Xorg server sets in
`hw/xfree86/os-support/linux/lnx_init.c`:

```c
signal(SIGUSR1, xf86VTRequest);
VT.mode = VT_PROCESS;
VT.relsig = SIGUSR1;
VT.acqsig = SIGUSR1;
```

Adopting them **requires** a real handler that answers with `VT_RELDISP`, or the
default SIGUSR1 action (terminate) kills the agent on the first VT switch — a
regression this ADR deliberately does not introduce under the "do not change
what it does" constraint. **Follow-up, out of scope here.**

---

## §5 Consequences

**Accepted**

- `src/omega/` is now uniformly free of raw `asyncio` imports. The M1 gate
  measures something real: future `asyncio` drift and `to_thread` misuse.
- A false claim in a permanent-looking header is gone. The file now documents
  *why* the old claim was wrong, so it cannot be re-asserted from memory.
- The `VT_SETMODE` buffer over-read and the uninitialised-`relsig` write are gone.
- `agent.shutdown()` is shielded and cannot be interrupted with the VT still in
  `VT_PROCESS` mode.

**Deferred / not decided here**

- **The VT_PROCESS switch handshake** (`relsig`/`acqsig` + `VT_RELDISP`), §4.
- **`VTManager.get_state()` has the same bug class.** It reads
  `struct vt_stat { unsigned short v_active; v_signal; v_state; }` through a
  `bytearray(16)` and reports `buf[0]`/`buf[1]` as bytes, which is only
  correct while the VT number and open-VT bitmask are both `< 256`. Left
  untouched because fixing it changes the *shape* of `get_state()`'s dict and
  therefore the dashboard output, which this ADR was constrained not to change.
- **`render_dashboard()` blocks the event loop** for ~100 ms every 2 s on
  `psutil.cpu_percent(interval=0.1)`, *inside* the loop thread. The conversion
  makes this visible to the M1 gate instead of hiding it. Correct remedy is
  `await anyio.to_thread.run_sync(self.vt.get_state)` — **not** a thread
  exemption.

**Not verified**

- Execution on a real Linux Virtual Console. `/dev/tty` returns ENXIO from a
  process with no controlling terminal and `/dev/tty3` returns EACCES without
  root in this environment. The VT ioctls were verified only against a PTY
  (which cleanly refuses with ENOTTY) and through `fcntl.ioctl` marshalling.
  See §7.3.

---

## §6 Mandate Traceability

| Mandate | How this ADR serves it |
|---|---|
| **M1** (AnyIO Absolute) | Exemption rescinded; `src/omega/` is uniformly asyncio-free and `make check-m1-anyio` passes with no glob. |
| **M23** (Failure Integrity) | `except NotImplementedError: pass` and both `except CancelledError: pass` deleted. ruff findings 7 → 4. Nothing is swallowed to make a signal path work. |
| **M28** (Artifact Preservation) | No deletion; the rescinded comment remains in git history and its full text is quoted in the module docstring so the correction is visible. |
| **M27** (Tracking Integrity) | A regression test file pins the anyio shape so the exemption cannot silently return. |
| **M13** (Temple-Grade) | `make lint` exit 0; the converted module compiles and its test suite passes 21/21. |

---

## §7 Verification Record

| # | Check | Command | Result |
|---|---|---|---|
| 7.1 | M1 gate, glob removed | `make check-m1-anyio` | **exit 0** — "M1 passed: No asyncio imports in core" |
| 7.2 | Compile | `.venv/bin/python -m py_compile src/omega/agents/tty_agent.py` | **exit 0** |
| 7.3 | Real module, external SIGTERM | `kill -TERM <pid>` to the converted module | **rc 0**; `frames=13`; VT order `open → acquire → lock_switch(True) → register → deregister → lock_switch(False) → release → close` |
| 7.4 | Real module, external SIGINT | `kill -INT <pid>` | **rc 0**, identical sequence |
| 7.5 | Real module, `run()` returns with no signal | | **rc 0**, no hang (pre-fix this hung >60 s) |
| 7.6 | Startup failure | | **rc 1**, no `shutdown()`, no hang |
| 7.7 | Regression suite | `.venv/bin/python -m pytest tests/test_tty_agent_anyio.py -v` | **21 passed** |
| 7.8 | M8 | `make check-m8-zero-telemetry` | **exit 0** |
| 7.9 | M23 ratchet | `make check-m23-failure-integrity` | **exit 0** — "No new soft-failure patterns" |
| 7.10 | Lint | `make lint` | **exit 0**; critical gate (`E9,F63,F7,F82`) count **0** |
| 7.11 | anyio task-group join semantics | 3 structural probes (`shield_probe.py`, `final3.py`, `shapes2.py`) | see §3.1 |
| 7.12 | `struct vt_mode` ABI | `struct.calcsize("BBhhh")`, kernel headers, `ioctl_vt(2)`, marshalling probe | 8 bytes; matches |

### 7.13 UNVERIFIED (do not cite as passing)

- **Live `/dev/tty3` / `/dev/tty4` execution.** `/dev/tty` → `ENXIO` (no
  controlling terminal in this process); `/dev/tty3` → `EACCES` (not root).
  Everything about the VT ioctls, `VT_PROCESS` acquisition and `VT_RELDISP`
  needs a root shell on a real VC before this ADR's M1 claim can be called
  *production*-verified. The M1 claim itself is fully verified; the VT claim is
  not.
- **`vt_get_state` byte-vs-short behaviour** (§5) — unchanged, untested.

---

## §8 D-number

The fleet's flat D-series is agent-assigned (D-617…D-628 appear in session
gnosis and operational docs, with no central assignment ledger). `D-629` is
**already taken** — it is used five times in `PUBLIC_ALLOWLIST.txt` for
"Research & Coordination — REMOVED from ALLOW". **`D-630` is free** (0
references repo-wide) and is the number used in this ADR and in the module
header.

**This is a request for ratification, not a claim of assignment.** The Architect
should renumber if convention says otherwise; the reference appears in exactly
two places (`src/omega/agents/tty_agent.py`, `Makefile:check-m1-anyio`).

---

## §9 The reusable lesson

A mandate exemption is a *claim about the runtime*, and it is written once, in
prose, and then never re-tested. This one survived eight weeks because the
comment was confident and specific — "line discipline, job control, ^C
delivery" — and because the file it described really was the only asyncio
import in `src/omega/`. Reading the actual backend source took about ten minutes
and disproved all four clauses.

The exemption also concealed two real defects (the ABI bug, §4, and the
unshielded shutdown, §5) precisely because the file was excluded from the gate
that would have forced someone to look. **A carve-out does not just excuse the
using the code is an exemption for.** When a rationale for an exemption cannot
be traced to a source, the burden is on the rationale.

*⬡ OMEGA ⬡ JEM ⬡ ADR-008 ⬡ AP-ADR-008-TTY-M1-CONVERSION-v1.0.0 ⬡ 2026-10-15*

<!-- Model provenance: step-5-preview-free (opencode) — session ses_ec0f2d295ffeKmFxfXkRci3NYt -->
