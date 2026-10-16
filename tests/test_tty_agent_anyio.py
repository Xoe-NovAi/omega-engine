# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Regression tests for the D-630 anyio conversion of ``tty_agent.py``.

Scope. Every test targets the orchestration the conversion changed: task-group
shape, signal delivery as structured cancellation, shielded startup and
shutdown, cancellation joining, the ``struct vt_mode`` ABI, and the M1/M23
residue that the deleted exemption used to hide.

The VT ioctls themselves are exercised through ``fcntl.ioctl`` against a PTY or
a monkeypatched recorder, because a real Linux Virtual Console needs root and
be reached from a process with a controlling terminal (``/dev/tty`` raises
ENXIO here; ``/dev/tty3`` raises EACCES). UNVERIFIED items are named, not
asserted.

Run:  .venv/bin/python -m pytest tests/test_tty_agent_anyio.py -v
"""

from __future__ import annotations

import ast
import functools
import os
import signal
import struct
import sys
from pathlib import Path

import anyio
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from omega.agents import tty_agent as mod  # noqa: E402

SOURCE = Path(mod.__file__).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# VT recorder — stands in for VTManager, records the ioctl sequence
# ---------------------------------------------------------------------------
class RecordingVT:
    """Drop-in for VTManager that never touches the kernel."""

    def __init__(self, tty_path: str):
        self.tty_path = tty_path
        self.fd = 4242
        self.calls: list[str] = []
        self._original_mode: bytes | None = None
        self.last_packed: bytes | None = None

    def open(self) -> bool:
        self.calls.append("open")
        return True

    def close(self):
        self.calls.append("close")

    def get_mode_struct(self) -> bytes:
        self.calls.append("get_mode_struct")
        return struct.pack(mod.VT_MODE_STRUCT, mod.VT_AUTO, 0, 0, 0, 0)

    def get_mode(self) -> int:
        return mod.VT_AUTO

    def set_mode(self, mode: int, *, waitv=0, relsig=0, acqsig=0, frsig=0) -> bool:
        self.calls.append(f"set_mode({mode})")
        self.last_packed = struct.pack(mod.VT_MODE_STRUCT, mode, waitv, relsig, acqsig, frsig)
        return True

    def acquire_process_mode(self) -> bool:
        self.calls.append("acquire_process_mode")
        # mirrors the real implementation
        self._original_mode = self.get_mode_struct()
        self.set_mode(mod.VT_PROCESS)
        return True

    def release_process_mode(self) -> bool:
        self.calls.append("release_process_mode")
        return True

    def lock_switch(self, lock: bool = True) -> bool:
        self.calls.append(f"lock_switch({lock})")
        return True

    def activate(self, vt_num: int) -> bool:
        self.calls.append(f"activate({vt_num})")
        return True

    def get_state(self) -> dict:
        self.calls.append("get_state")
        return {"active_vt": 3, "signal": 0, "open_vts": [1, 2, 3]}

    def disallocate(self) -> bool:
        self.calls.append("disallocate")
        return True


class _FakeFile:
    def close(self):
        pass


class StubAgent(mod.TTYAgent):
    """TTYAgent with a recording VT and in-tmp Hivemind I/O."""

    def __init__(self, tmp_path, entity="observability", lock_switch=True):
        cfg = mod.TTYAgentConfig(
            entity_name=entity,
            tty_path="/dev/tty3",
            data_dir=tmp_path,
            lock_switch=lock_switch,
            hivemind_dir=tmp_path / "hivemind",
        )
        self.vt = RecordingVT(cfg.tty_path)
        self.config = cfg
        self.console = None
        self.running = False
        self.start_time = None
        self._layout = None
        self._live = None
        self._reader = None
        self.frames = 0
        self.deregistered = False
        self.registered = False

    async def startup(self) -> bool:
        """The real TTYAgent.startup step order, with the root-only console
        open and the SovereignReader construction stubbed."""
        from datetime import datetime, timezone
        self.startup_ran = True
        print(f"🚀 Starting {self.config.entity_name} on {self.config.tty_path}")
        if not self.vt.open():
            return False
        if not self.vt.acquire_process_mode():
            print("❌ Failed to acquire VT_PROCESS mode", file=sys.stderr)
            return False
        print("✅ VT_PROCESS mode acquired")
        if self.config.lock_switch:
            if self.vt.lock_switch(True):
                print("🔒 VT switching locked")
            else:
                print("⚠️  Failed to lock VT switching")
        class _F:
            def close(self): pass
        self.console = type("C", (), {"file": _F()})()  # stands in for Rich Console
        await self._register_hivemind()
        self.running = True
        self.start_time = datetime.now(timezone.utc)
        print(f"✅ {self.config.entity_name} ready on {self.config.tty_path}")
        return True

    async def _register_hivemind(self):
        self.registered = True

    async def _deregister_hivemind(self):
        self.deregistered = True

    async def run_dashboard(self, refresh_rate: float = 2.0):
        while self.running:
            await anyio.sleep(refresh_rate)
            self.frames += 1

    async def run(self):
        # the real default is 2.0s; a test needs a faster cadence
        await self.run_dashboard(refresh_rate=0.02)

    def render_dashboard(self):
        return None


def make_agent(tmp_path, **kw) -> StubAgent:
    agent = StubAgent(tmp_path, **kw)
    agent._tmp = tmp_path
    return agent


def run_main_body(agent, send=None, delay=0.12, startup_checkpoint=0.0):
    """Execute the exact orchestration body of the converted ``main()``."""

    async def body():
        started = False
        startup_done = anyio.Event()

        async def kick():
            await anyio.sleep(delay)
            os.kill(os.getpid(), send)

        async def shielded_startup():
            # optional checkpoint inside startup, to prove the shield holds
            if startup_checkpoint:
                await anyio.sleep(startup_checkpoint)
            return await agent.startup()

        async with anyio.create_task_group() as tg:
            if not mod._WINDOWS:
                tg.start_soon(mod.signal_watch, tg.cancel_scope, startup_done)
            if send is not None:
                tg.start_soon(kick)
            with anyio.CancelScope(shield=True):
                started = await shielded_startup()
            startup_done.set()
            if not started:
                tg.cancel_scope.cancel()
            else:
                tg.start_soon(mod.run_until_stopped, agent, tg.cancel_scope)
                tg.start_soon(agent._heartbeat_loop)

        if not started:
            return 1
        with anyio.CancelScope(shield=True):
            await agent.shutdown()
        return 0

    return body


# ===========================================================================
# §1 M1 / M23 residue
# ===========================================================================
def test_m1_gate_pattern_absent():
    """Exactly what ``rg -n 'import asyncio|from asyncio'`` matches."""
    import re

    hits = [
        (i + 1, line)
        for i, line in enumerate(SOURCE.splitlines())
        if re.search(r"\b(import\s+asyncio|from\s+asyncio)\b", line)
    ]
    assert not hits, f"M1 gate would FAIL: {hits}"
    assert not hasattr(mod, "asyncio")


def test_m23_no_not_implemented_error_swallow():
    """The deleted ``except NotImplementedError: pass  # Windows`` must stay gone.

    AST-based, so prose in the D-630 history block cannot false-positive.
    """
    tree = ast.parse(SOURCE)
    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for handler in node.handlers:
                names = []
                if isinstance(handler.type, ast.Name):
                    names = [handler.type.id]
                elif isinstance(handler.type, ast.Tuple):
                    names = [e.id for e in handler.type.elts if isinstance(e, ast.Name)]
                if "NotImplementedError" in names:
                    offenders.append(f"try/except at line {node.lineno}")
        if isinstance(node, ast.ExceptHandler) and isinstance(node.type, ast.Name):
            if node.type.id == "NotImplementedError":
                offenders.append(f"except at line {node.lineno}")
    assert not offenders, offenders


def test_no_cancelled_error_is_swallowed():
    """``except ... CancelledError`` must always re-raise.

    M1 conversion requirement: a swallowed cancellation is the edge-cancellation
    hang (asyncio keeps running the task because nothing cancels it again).
    """
    tree = ast.parse(SOURCE)
    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and isinstance(node.type, ast.Name):
            if node.type.id.endswith("CancelledError") or node.type.id == "BaseException":
                body = node.body
                reraises = any(isinstance(n, ast.Raise) for n in ast.walk(ast.Module(body=body)))
                if not reraises:
                    offenders.append(f"swallowed cancellation at line {node.lineno}")
    assert not offenders, offenders


def test_no_cancellation_handler_at_all():
    """The conversion deleted every ``except CancelledError`` clause.

    That is stronger than re-raising: nothing in this module intercepts
    cancellation, so the task group always gets to join its children.
    """
    tree = ast.parse(SOURCE)
    handlers = [
        n.lineno
        for n in ast.walk(tree)
        if isinstance(n, ast.ExceptHandler) and isinstance(n.type, ast.Name)
        and (n.type.id.endswith("CancelledError") or n.type.id == "BaseException")
    ]
    assert not handlers, f"cancellation intercepted at lines {handlers}"


# ===========================================================================
# §2 struct vt_mode ABI
# ===========================================================================
def test_vt_mode_struct_layout():
    """include/uapi/linux/vt.h: {__u8 mode; __u8 waitv; __s16 relsig/acqsig/frsig;}"""
    assert mod.VT_MODE_STRUCT == "BBhhh"
    assert struct.calcsize("BBhhh") == 8
    assert mod.VT_MODE_SIZE == 8
    packed = struct.pack(mod.VT_MODE_STRUCT, mod.VT_PROCESS, 0, signal.SIGUSR1, signal.SIGUSR2, 0)
    assert len(packed) == 8
    assert struct.unpack(mod.VT_MODE_STRUCT, packed) == (1, 0, signal.SIGUSR1, signal.SIGUSR2, 0)
    # the pre-D-630 layout, for contrast
    assert struct.calcsize("h") == 2


def test_get_mode_struct_passes_eight_byte_buffer(monkeypatch):
    seen = {}

    def fake_ioctl(fd, op, buf):
        seen["len"] = len(buf)
        return b"\x00" * len(buf)

    monkeypatch.setattr(mod.fcntl, "ioctl", fake_ioctl)
    vt = mod.VTManager("/dev/tty3")
    vt.fd = 99
    raw = vt.get_mode_struct()
    assert seen["len"] == 8, f"VT_GETMODE buffer was {seen['len']} bytes"
    assert raw == b"\x00" * 8


def test_set_mode_packs_full_struct(monkeypatch):
    seen = {}

    def fake_ioctl(fd, op, buf):
        seen["bytes"] = bytes(buf)
        return b"\x00" * len(buf)

    monkeypatch.setattr(mod.fcntl, "ioctl", fake_ioctl)
    vt = mod.VTManager("/dev/tty3")
    vt.fd = 99
    assert vt.set_mode(mod.VT_PROCESS, relsig=signal.SIGUSR1, acqsig=signal.SIGUSR1)
    assert len(seen["bytes"]) == 8
    assert seen["bytes"] == struct.pack("BBhhh", 1, 0, signal.SIGUSR1, signal.SIGUSR1, 0)


def test_ioctl_accepts_marshalled_struct():
    """fcntl.ioctl must accept the packed struct (bytes) and a bytearray."""
    master, slave = os.openpty()
    try:
        packed = struct.pack(mod.VT_MODE_STRUCT, mod.VT_PROCESS, 0, 0, 0, 0)
        for arg in (packed, bytearray(packed)):
            with pytest.raises(OSError):  # ENOTTY on a PTY — but the arg reached the kernel
                mod.fcntl.ioctl(slave, mod.VT_SETMODE, arg)
    finally:
        os.close(master)
        os.close(slave)


def test_acquire_saves_full_struct(tmp_path):
    agent = make_agent(tmp_path)
    assert agent.vt.acquire_process_mode() is True
    saved = agent.vt._original_mode
    assert saved is not None and len(saved) == 8, "saved original must be the whole struct"
    # restore path restores the saved bytes verbatim
    assert agent.vt.release_process_mode() is True
    assert "release_process_mode" in agent.vt.calls


def test_set_mode_defaults_to_zero_relsig(tmp_path):
    """D-630 decision: relsig/acqsig stay 0 (documented known defect)."""
    agent = make_agent(tmp_path)
    agent.vt.acquire_process_mode()
    mode, waitv, relsig, acqsig, frsig = struct.unpack(mod.VT_MODE_STRUCT, agent.vt.last_packed)
    assert mode == mod.VT_PROCESS
    assert (relsig, acqsig, frsig) == (0, 0, 0), (
        "relsig/acqsig non-zero without a VT_RELDISP handler would let the "
        "default SIGUSR1 action terminate the agent on VT switch"
    )


# ===========================================================================
# §3 anyio orchestration
# ===========================================================================
@pytest.mark.parametrize("sig", [signal.SIGTERM, signal.SIGINT])
def test_external_signal_graceful_shutdown(tmp_path, sig):
    agent = make_agent(tmp_path)
    assert anyio.run(run_main_body(agent, send=sig)) == 0

    assert agent.vt.calls[0] == "open"
    assert "acquire_process_mode" in agent.vt.calls
    assert agent.vt.calls[-1] == "close", "VT ioctls incomplete — VT would leak"
    assert "lock_switch(True)" in agent.vt.calls
    assert "lock_switch(False)" in agent.vt.calls
    assert "release_process_mode" in agent.vt.calls
    assert agent.frames >= 1, "the task group never actually ran the body"
    assert agent.deregistered
    # ordering: register during startup, deregister before the VT ioctls
    assert agent.vt.calls.index("lock_switch(False)") < agent.vt.calls.index("release_process_mode")


def test_shielded_startup_survives_signal_during_startup(tmp_path):
    """A signal landing mid-startup must not abort VT acquisition."""
    agent = make_agent(tmp_path)
    assert anyio.run(
        run_main_body(agent, send=signal.SIGTERM, delay=0.02, startup_checkpoint=0.08)
    ) == 0
    assert agent.startup_ran, "startup never ran"
    assert agent.vt.calls[-1] == "close", "shutdown incomplete after signal during startup"
    # startup finished: the console/Hivemind steps after the checkpoint all ran
    assert "lock_switch(True)" in agent.vt.calls
    assert agent.registered, "startup was interrupted before Hivemind registration"
    assert agent.vt.calls[-1] == "close"


def test_startup_failure_returns_one_without_hanging(tmp_path):
    """startup() False -> rc 1, and the group must not block on the receiver."""
    agent = make_agent(tmp_path)

    async def body():
        started = False
        startup_done = anyio.Event()
        async with anyio.create_task_group() as tg:
            tg.start_soon(mod.signal_watch, tg.cancel_scope, startup_done)
            started = await agent.startup()  # returns True normally
            startup_done.set()
            return 1 if not started else 0

        return 0

    async def failing():
        return False

    agent.startup = failing  # type: ignore[method-assign]

    async def body():
        started = False
        startup_done = anyio.Event()
        async with anyio.create_task_group() as tg:
            tg.start_soon(mod.signal_watch, tg.cancel_scope, startup_done)
            with anyio.CancelScope(shield=True):
                started = await agent.startup()
            startup_done.set()
            if not started:
                tg.cancel_scope.cancel()
        return 1 if not started else 0

    async def guarded():
        with anyio.fail_after(5):  # TimeoutError if the group blocked on the receiver
            return await body()

    assert anyio.run(guarded) == 1
    assert "acquire_process_mode" not in agent.vt.calls


def test_run_returning_stops_the_heartbeat_sibling(tmp_path):
    """A subclass whose run() returns must not force the group to join forever."""
    agent = make_agent(tmp_path)

    async def run_returns():
        return None

    agent.run = run_returns  # type: ignore[method-assign]
    assert anyio.run(run_main_body(agent, send=None, delay=0.05)) == 0
    assert agent.vt.calls[-1] == "close"


def test_cancellation_is_not_swallowed(tmp_path):
    """Level cancellation must propagate out of the loops, not be eaten."""
    seen: dict[str, object] = {}

    async def probe():
        try:
            await anyio.sleep(0.05)
        except anyio.get_cancelled_exc_class() as exc:
            seen["exc_class"] = type(exc)
            raise

    async def main():
        async with anyio.create_task_group() as tg:
            tg.start_soon(probe)
            await anyio.sleep(0.01)
            tg.cancel_scope.cancel()
        # resolve inside the running backend — get_cancelled_exc_class needs one
        seen["runtime_class"] = anyio.get_cancelled_exc_class()

    anyio.run(main)
    assert seen, "the task group never cancelled the child"
    assert seen["exc_class"] is seen["runtime_class"]


def test_shielded_cleanup_completes_under_outer_cancel(tmp_path):
    """The shield is what stops a mid-shutdown VT leak."""
    agent = make_agent(tmp_path)
    order: list[str] = []

    async def main():
        async with anyio.create_task_group() as tg:
            tg.start_soon(agent.run)
            tg.start_soon(agent._heartbeat_loop)
            await anyio.sleep(0.05)
            tg.cancel_scope.cancel()
        with anyio.CancelScope(shield=True):
            await agent.shutdown()
        order.append("cleanup-complete")

    anyio.run(main)
    assert "cleanup-complete" in order
    assert agent.vt.calls[-1] == "close"


def test_unshielded_cleanup_is_interrupted(tmp_path):
    """The bug the shield fixes — recorded so the fix's necessity stays visible.

    Configuration: an OUTER cancel scope is cancelled while the inner task
    group has already joined and cleanup is parked at a yield point. With level
    cancellation that yield point raises, and the VT ioctls after it never run.

    Sequenced with events, not wall-clock sleeps, so the cancellation lands
    exactly where the hazard is. Cancelling only the group's own scope is
    absorbed by ``__aexit__`` and is NOT enough to show the hazard — that
    negative result is why this test targets an outer scope.
    """
    agent = make_agent(tmp_path)
    order: list[str] = []
    reached = anyio.Event()
    release = anyio.Event()

    async def cleanup_body():
        agent.running = False
        order.append("deregister")
        reached.set()
        await release.wait()       # the outer cancel lands here
        await anyio.sleep(0)       # a yield point a future edit could add
        order.append("vt-ioctls")
        agent.vt.release_process_mode()
        agent.vt.close()

    async def host():
        try:
            async with anyio.create_task_group() as tg:
                tg.start_soon(agent.run)
                tg.start_soon(agent._heartbeat_loop)
                await anyio.sleep(0.02)
                tg.cancel_scope.cancel()
        finally:
            await cleanup_body()   # deliberately NOT shielded

    async def main():
        async with anyio.create_task_group() as outer:
            outer.start_soon(host)
            await reached.wait()
            outer.cancel_scope.cancel()
            release.set()

    anyio.run(main)
    assert "vt-ioctls" not in order, "unshielded cleanup unexpectedly completed"
    assert "close" not in agent.vt.calls, "VT was closed — shield hazard not shown"


def test_shielded_cleanup_survives_the_same_outer_cancel(tmp_path):
    """Same configuration, but shielded: cleanup completes and the VT closes."""
    agent = make_agent(tmp_path)
    order: list[str] = []
    reached = anyio.Event()
    release = anyio.Event()

    async def cleanup_body():
        agent.running = False
        order.append("deregister")
        reached.set()
        await release.wait()
        await anyio.sleep(0)
        order.append("vt-ioctls")
        agent.vt.release_process_mode()
        agent.vt.close()

    async def host():
        try:
            async with anyio.create_task_group() as tg:
                tg.start_soon(agent.run)
                tg.start_soon(agent._heartbeat_loop)
                await anyio.sleep(0.02)
                tg.cancel_scope.cancel()
        finally:
            with anyio.CancelScope(shield=True):
                await cleanup_body()

    async def main():
        async with anyio.create_task_group() as outer:
            outer.start_soon(host)
            await reached.wait()
            outer.cancel_scope.cancel()
            release.set()

    anyio.run(main)
    assert order[-1] == "vt-ioctls"
    assert agent.vt.calls[-1] == "close", "shielded cleanup was interrupted"

def test_open_signal_receiver_does_not_suppress_cancellation(tmp_path):
    """anyio's own contract (tests/test_signals.py::test_task_group_cancellation_open)."""

    async def parked():
        with anyio.open_signal_receiver(signal.SIGUSR1) as sigs:
            async for _ in sigs:  # pragma: no cover - never iterates
                pass

    async def main():
        async with anyio.create_task_group() as tg:
            tg.start_soon(parked)
            await anyio.sleep(0.05)
            tg.cancel_scope.cancel()

    anyio.run(main)  # a hang or suppression would fail here


def test_signal_watch_returns_after_first_signal(tmp_path):
    """One signal cancels the group; signal_watch must not stay a child."""
    agent = make_agent(tmp_path)
    assert anyio.run(run_main_body(agent, send=signal.SIGTERM, delay=0.05)) == 0
