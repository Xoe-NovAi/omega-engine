#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
Omega Engine — TTY Agent Base Class
Runs agents on dedicated Linux Virtual Consoles (Ctrl+Alt+F3-F6)

Usage:
    python -m src.omega.agents.tty_agent --entity researcher --tty /dev/tty3
    python -m src.omega.agents.tty_agent --entity roc_racoon --tty /dev/tty4

[M1 AnyIO Absolute] — COMPLIANT. This module is anyio-native and imports no
raw ``asyncio``: ``anyio.run()`` / ``anyio.create_task_group()`` /
``anyio.open_signal_receiver()`` / ``anyio.CancelScope``. It is therefore
covered by the unmodified ``Makefile:check-m1-anyio`` gate.

History (D-630). This file carried the only M1 glob exemption in the tree
(header dated 2026-08-28, ``--glob '!*tty_agent*'`` in the Makefile). That
header claimed anyio offered only a "thread-based approach" which "cannot be
replicated ... without losing TTY semantics (line discipline, job control,
^C delivery)", and that the asyncio signal handlers "work natively on TTYs
because the event loop is bound to the controlling terminal". Every clause
of that claim was false:

* ``anyio.run()`` defaults to ``backend="asyncio"`` and constructs an
  ``asyncio.Runner`` — a real asyncio loop in the calling thread. The
  thread machinery (``to_thread.run_sync`` / ``BlockingPortal``) is opt-in
  and unused here.
* ``anyio.open_signal_receiver()`` on the asyncio backend delegates to
  ``loop.add_signal_handler()`` — the *identical* mechanism this file
  already used.
* The "event loop is bound to the controlling terminal" premise does not
  exist. CPython's ``loop.add_signal_handler()`` uses
  ``signal.set_wakeup_fd()`` on an internal socketpair plus
  ``signal.signal()``. It touches no terminal fd, no controlling terminal,
  no line discipline and no job control. ``^C`` and ``kill`` are delivered
  by the kernel identically on a VT, a PTY and a pipe, which is why the
  anyio receiver and the raw loop call are interchangeable.
* The "TTY semantics" the header defended were not implemented by this file
  at all: no ``SIGUSR1``/``SIGUSR2`` VT switch handler existed, and
  ``vt_mode.relsig``/``acqsig`` were never set.

The exemption was rescinded as based on an inaccurate rationale; the file
was converted; the Makefile carve-out was deleted. See
``docs/decisions/ADR-008-...``.

Second correction worth keeping visible: the pre-conversion shutdown shape
was *less* safe than the anyio one, not more. ``finally: await
agent.shutdown()`` was unshielded, and ``TTYAgent.shutdown()`` awaited
Hivemind deregistration *between* the VT ioctls — so a cancellation landing
there skipped ``VT_UNLOCKSWITCH`` / ``VT_SETMODE`` / ``close(fd)`` and left
the kernel holding ``/dev/ttyN`` in ``VT_PROCESS`` mode for a process that
had already exited.

[M8 EXEMPTION] This agent uses ``fcntl``/``ioctl`` for POSIX TTY syscalls
(VT_GETMODE, VT_SETMODE, VT_GETSTATE, VT_LOCKSWITCH, VT_ACTIVATE,
VT_WAITACTIVE, VT_DISALLOCATE — see ``linux/vt.h``). No external telemetry
is emitted; the file descriptor is local to the process.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import logging
import os
import signal
import struct
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import anyio

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from omega.observability.observability_reader import SovereignReader

logger = logging.getLogger(__name__)


# ============================================================================
# VT IOCTL CONSTANTS (from linux/vt.h)
# ============================================================================

VT_OPENQRY = 0x5600
VT_GETMODE = 0x5601
VT_SETMODE = 0x5602
VT_GETSTATE = 0x5603
VT_SENDSIG = 0x5604
VT_RELDISP = 0x5605
VT_ACTIVATE = 0x5606
VT_WAITACTIVE = 0x5607
VT_DISALLOCATE = 0x5608
VT_LOCKSWITCH = 0x5609
VT_UNLOCKSWITCH = 0x560A

VT_AUTO = 0
VT_PROCESS = 1
VT_ACKACQ = 2

# [D-630] struct vt_mode ABI — include/uapi/linux/vt.h:
#
#     struct vt_mode {
#         __u8  mode;    /* VT_AUTO / VT_PROCESS / VT_ACKACQ */
#         __u8  waitv;   /* if set, hang on writes if not active */
#         __s16 relsig;  /* signal to raise on release req */
#         __s16 acqsig;  /* signal to raise on acquisition */
#         __s16 frsig;   /* unused (set to 0) */
#     };                 /* 8 bytes on ILP32 and LP64 */
#
# ioctl_vt(2) documents the same layout, and drivers/tty/vt/vt_ioctl.c copies
# the FULL struct for both VT_GETMODE and VT_SETMODE. The previous code packed
# only ``struct.pack("h", mode)`` — 2 bytes — so VT_GETMODE read 6 bytes past
# the end of the buffer and VT_SETMODE wrote uninitialised adjacent heap into
# ``relsig``/``acqsig``. Native order/alignment is correct here: the kernel
# struct has no padding and __s16 is a native short.
VT_MODE_STRUCT = "BBhhh"
VT_MODE_SIZE = struct.calcsize(VT_MODE_STRUCT)
assert VT_MODE_SIZE == 8, f"struct vt_mode must be 8 bytes, got {VT_MODE_SIZE}"

# [D-630] relsig/acqsig are DELIBERATELY 0 — see VTManager.acquire_process_mode.
# This is a deterministic, documented choice, not an oversight.
_VT_WAITV = 0
_VT_RELSIG = 0
_VT_ACQSIG = 0
_VT_FRSIG = 0


# ============================================================================
# VT MANAGER
# ============================================================================


class VTManager:
    """Manages Linux Virtual Terminal via ioctl."""

    def __init__(self, tty_path: str):
        self.tty_path = tty_path
        self.fd: Optional[int] = None
        self._original_mode: Optional[bytes] = None

    def open(self) -> bool:
        """Open TTY device."""
        try:
            # O_NOCTTY: don't make this our controlling terminal
            # O_RDWR: read/write
            self.fd = os.open(self.tty_path, os.O_RDWR | os.O_NOCTTY)
            return True
        except OSError as e:
            print(f"❌ Failed to open {self.tty_path}: {e}", file=sys.stderr)
            return False

    def close(self):
        """Close TTY device."""
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None

    def get_mode(self) -> Optional[int]:
        """Get current VT mode (VT_AUTO / VT_PROCESS / VT_ACKACQ), or None."""
        raw = self.get_mode_struct()
        return None if raw is None else raw[0]

    def get_mode_struct(self) -> Optional[bytes]:
        """Read the full 8-byte ``struct vt_mode`` the kernel holds.

        [D-630] ABI fix. ``VT_GETMODE`` copies ``sizeof(struct vt_mode)`` == 8
        bytes into ``argp``; the previous 2-byte buffer under-read by 6.
        """
        if self.fd is None:
            return None
        try:
            buf = bytearray(VT_MODE_SIZE)
            fcntl.ioctl(self.fd, VT_GETMODE, buf)
            return bytes(buf)
        except OSError:
            return None

    def set_mode(
        self,
        mode: int,
        *,
        waitv: int = _VT_WAITV,
        relsig: int = _VT_RELSIG,
        acqsig: int = _VT_ACQSIG,
        frsig: int = _VT_FRSIG,
    ) -> bool:
        """Set mode of active vt.

        [D-630] ABI fix. ``argp`` must be a full 8-byte ``struct vt_mode``;
        ``VT_SETMODE`` copies the whole struct from user space.
        """
        if self.fd is None:
            return False
        try:
            buf = struct.pack(VT_MODE_STRUCT, mode, waitv, relsig, acqsig, frsig)
            fcntl.ioctl(self.fd, VT_SETMODE, buf)
            return True
        except OSError as e:
            print(f"❌ VT_SETMODE failed: {e}", file=sys.stderr)
            return False

    def acquire_process_mode(self) -> bool:
        """Acquire VT_PROCESS mode — we own this VT.

        [D-630] `relsig`/`acqsig` are left at 0, and that is a KNOWN DEFECT
        rather than a correctness claim:

        * On a release request the kernel calls
          ``kill_pid(vc->vt_pid, vc->vt_mode.relsig, 1)`` and, if it succeeds,
          sets ``vt_newvt`` and returns *without switching*, waiting for the
          process to complete the handshake with ``VT_RELDISP``
          (drivers/tty/vt/vt_ioctl.c, ``change_console()``).
        * With ``relsig == 0`` the ``kill_pid`` is the POSIX signal-0
          existence check. It succeeds, so the kernel parks the switch and
          the VT does not change until the process calls ``VT_RELDISP`` —
          which this agent never does. Combined with ``lock_switch`` the
          switch is blocked either way, so effective behaviour is unchanged
          from the pre-D-630 code.
        * The conventional values for a complete implementation are
          ``relsig = acqsig = SIGUSR1`` — this is exactly what the Xorg
          server sets in ``hw/xfree86/os-support/linux/lnx_init.c``
          (``signal(SIGUSR1, xf86VTRequest); VT.mode = VT_PROCESS;
          VT.relsig = SIGUSR1; VT.acqsig = SIGUSR1;``). Adopting them
          REQUIRES a real handler that answers with ``VT_RELDISP``, or the
          default SIGUSR1 action (terminate) kills the agent on the first
          VT switch — a regression this change deliberately does not
          introduce. Tracked as a follow-up outside the M1 conversion scope.
        """
        # Save original mode first — the full struct, so waitv/relsig/acqsig
        # are restored verbatim rather than guessed.
        original = self.get_mode_struct()
        if original is None:
            original = struct.pack(VT_MODE_STRUCT, VT_AUTO, _VT_WAITV, 0, 0, 0)
        self._original_mode = original
        return self.set_mode(VT_PROCESS)

    def release_process_mode(self) -> bool:
        """Release VT ownership back to kernel."""
        if self._original_mode:
            try:
                fcntl.ioctl(self.fd, VT_SETMODE, self._original_mode)
                return True
            except OSError:
                pass
        return self.set_mode(VT_AUTO)

    def lock_switch(self, lock: bool = True) -> bool:
        """Lock/unlock VT switching (Ctrl+Alt+Fn, chvt)."""
        if self.fd is None:
            return False
        try:
            fcntl.ioctl(self.fd, VT_LOCKSWITCH if lock else VT_UNLOCKSWITCH, 1)
            return True
        except OSError:
            return False

    def activate(self, vt_num: int) -> bool:
        """Switch to VT (like chvt)."""
        if self.fd is None:
            return False
        try:
            fcntl.ioctl(self.fd, VT_ACTIVATE, vt_num)
            fcntl.ioctl(self.fd, VT_WAITACTIVE, vt_num)
            return True
        except OSError:
            return False

    def get_state(self) -> dict:
        """Get VT state (active VT, open VTs)."""
        if self.fd is None:
            return {}
        try:
            buf = bytearray(16)
            fcntl.ioctl(self.fd, VT_GETSTATE, buf)
            return {
                "active_vt": buf[0],
                "signal": buf[1],
                "open_vts": [b for b in buf[2:] if b != 0],
            }
        except OSError:
            return {}

    def disallocate(self) -> bool:
        """Deallocate VT (free kernel resources)."""
        if self.fd is None:
            return False
        try:
            vt_num = int(self.tty_path.replace("/dev/tty", ""))
            fcntl.ioctl(self.fd, VT_DISALLOCATE, vt_num)
            return True
        except (OSError, ValueError):
            return False


# ============================================================================
# TTY AGENT BASE CLASS
# ============================================================================


@dataclass
class TTYAgentConfig:
    entity_name: str
    tty_path: str
    data_dir: Path = field(default_factory=lambda: Path("data"))
    lock_switch: bool = True
    hivemind_dir: Path = field(default_factory=lambda: Path("data/coordination/tty_hivemind"))


class TTYAgent:
    """Base class for agents running on dedicated Linux Virtual Consoles."""

    def __init__(self, config: TTYAgentConfig):
        self.config = config
        self.vt = VTManager(config.tty_path)
        self.console: Optional[Console] = None
        self.running = False
        self.start_time: Optional[datetime] = None
        self._layout: Optional[Layout] = None
        self._live: Optional[Live] = None
        self._reader: Optional[SovereignReader] = None

    async def startup(self) -> bool:
        """Initialize VT and agent.

        The heartbeat loop is NOT started here. It is a child of the task
        group built by ``main()``, so that it is cancelled and *joined* with
        the dashboard rather than being cancelled by hand. This keeps the
        class honest: there is no stored task handle to leak, and nothing can
        outlive the task group.
        """
        print(f"🚀 Starting {self.config.entity_name} on {self.config.tty_path}")

        # 1. Open VT
        if not self.vt.open():
            return False

        # 2. Acquire VT_PROCESS mode
        if not self.vt.acquire_process_mode():
            print("❌ Failed to acquire VT_PROCESS mode", file=sys.stderr)
            return False
        print("✅ VT_PROCESS mode acquired")

        # 3. Lock switching if configured
        if self.config.lock_switch:
            if self.vt.lock_switch(True):
                print("🔒 VT switching locked")
            else:
                print("⚠️  Failed to lock VT switching")

        # 4. Initialize Rich console on TTY
        try:
            tty_file = open(self.config.tty_path, "w")
            self.console = Console(file=tty_file, force_terminal=True, width=120)
        except OSError as e:
            print(f"❌ Failed to open TTY for writing: {e}", file=sys.stderr)
            return False

        # 5. Initialize observability reader
        self._reader = SovereignReader(
            db_path=self.config.data_dir / "observability" / "metrics.db",
            trace_dir=self.config.data_dir / "traces",
            crash_dir=self.config.data_dir / "crashes",
        )

        # 6. Register with Hivemind
        await self._register_hivemind()

        self.running = True
        self.start_time = datetime.now(timezone.utc)
        print(f"✅ {self.config.entity_name} ready on {self.config.tty_path}")
        return True

    async def shutdown(self):
        """Clean shutdown.

        Called from ``main()`` inside ``anyio.CancelScope(shield=True)``. The
        shield is load-bearing: every step after the Hivemind deregistration
        has a kernel-visible consequence, and a cancellation that landed
        mid-shutdown would leave ``/dev/ttyN`` in ``VT_PROCESS`` mode owned by
        an exiting process (the kernel only ``reset_vc()``s on the next switch
        attempt). Nothing here may be cancelled, and no exception is swallowed.
        """
        print(f"🛑 Shutting down {self.config.entity_name}...")
        self.running = False

        # The heartbeat task has already been cancelled and joined by the task
        # group before this method is entered.

        # Deregister from Hivemind
        await self._deregister_hivemind()

        # Unlock VT switching
        if self.config.lock_switch:
            self.vt.lock_switch(False)
            print("🔓 VT switching unlocked")

        # Release VT ownership
        self.vt.release_process_mode()
        print("✅ VT ownership released")

        # Close VT
        self.vt.close()

        # Close console
        if self.console and self.console.file:
            self.console.file.close()

        print(f"✅ {self.config.entity_name} shutdown complete")

    async def _register_hivemind(self):
        """Register agent with file-based Hivemind."""
        self.config.hivemind_dir.mkdir(parents=True, exist_ok=True)

        reg_file = self.config.hivemind_dir / f"{self.config.entity_name}.json"
        reg_data = {
            "entity": self.config.entity_name,
            "tty": self.config.tty_path,
            "pid": os.getpid(),
            "vt_mode": "VT_PROCESS",
            "lock_switch": self.config.lock_switch,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "status": "active",
            "capabilities": self.get_capabilities(),
        }
        reg_file.write_text(json.dumps(reg_data, indent=2))

    async def _deregister_hivemind(self):
        """Deregister agent from Hivemind."""
        reg_file = self.config.hivemind_dir / f"{self.config.entity_name}.json"
        if reg_file.exists():
            reg_file.unlink()

    async def _heartbeat_loop(self):
        """Periodic heartbeat to Hivemind.

        A task-group child, spawned by ``main()``. It is stopped by *level*
        cancellation from the group's cancel scope rather than by an explicit
        ``task.cancel()``; the cancellation is intentionally NOT caught, so it
        propagates out of the coroutine and the task group can join cleanly.
        Swallowing it here is what makes asyncio's edge cancellation hang (the
        ``while self.running`` loop would keep running with no way to stop it).
        """
        while self.running:
            await anyio.sleep(30)  # Every 30 seconds
            if not self.running:
                break

            reg_file = self.config.hivemind_dir / f"{self.config.entity_name}.json"
            if reg_file.exists():
                data = json.loads(reg_file.read_text())
                data["last_heartbeat"] = datetime.now(timezone.utc).isoformat()
                data["uptime_seconds"] = (
                    datetime.now(timezone.utc) - self.start_time
                ).total_seconds()
                reg_file.write_text(json.dumps(data, indent=2))

    def get_capabilities(self) -> list[str]:
        """Override in subclass to declare capabilities."""
        return ["tty_agent", "vt_process_mode"]

    def render_dashboard(self) -> Layout:
        """Override in subclass to provide custom dashboard."""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3), Layout(name="body"), Layout(name="footer", size=3)
        )

        # Header
        uptime = ""
        if self.start_time:
            td = datetime.now(timezone.utc) - self.start_time
            uptime = f"Uptime: {int(td.total_seconds())}s"

        header = Panel(
            f"[bold cyan]🔱 {self.config.entity_name.upper()}[/bold cyan] | "
            f"[green]{self.config.tty_path}[/green] | "
            f"[yellow]VT_PROCESS[/yellow] | {uptime}",
            style="blue",
        )
        layout["header"].update(header)

        # Body - override in subclass
        layout["body"].update(Panel("Override render_dashboard() in subclass", style="dim"))

        # Footer
        vt_state = self.vt.get_state()
        footer = Panel(
            f"Active VT: {vt_state.get('active_vt', '?')} | "
            f"Open VTs: {vt_state.get('open_vts', [])} | "
            f"PID: {os.getpid()}",
            style="dim",
        )
        layout["footer"].update(footer)

        return layout

    async def run_dashboard(self, refresh_rate: float = 2.0):
        """Run live dashboard on TTY.

        Cancellation from the group's cancel scope is what exits the loop.
        ``rich.live.Live`` is a *synchronous* context manager, so its
        ``__exit__`` (restore the terminal) still runs while the cancellation
        unwinds the ``with`` block — the screen is restored before
        ``agent.shutdown()`` releases the VT.
        """
        if not self.console:
            return

        self._layout = self.render_dashboard()

        with Live(
            self._layout, console=self.console, refresh_per_second=1 / refresh_rate, screen=True
        ) as live:
            self._live = live
            while self.running:
                await anyio.sleep(refresh_rate)
                if not self.running:
                    break
                self._layout = self.render_dashboard()
                live.update(self._layout)

    async def run(self):
        """Main run loop — override in subclass.

        Spawned as a task-group child by ``main()`` alongside
        ``_heartbeat_loop``. Overrides only need to return (or raise) for the
        task group to move on.
        """
        await self.run_dashboard()


# ============================================================================
# ENTITY-SPECIFIC AGENTS
# ============================================================================


class ResearcherTTYAgent(TTYAgent):
    """Researcher agent on dedicated TTY."""

    def get_capabilities(self) -> list[str]:
        return super().get_capabilities() + [
            "deep_research",
            "web_scraping",
            "api_integration",
            "model_registry",
            "freshness_checking",
        ]

    def render_dashboard(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3), Layout(name="body"), Layout(name="footer", size=3)
        )

        # Header
        uptime = ""
        if self.start_time:
            td = datetime.now(timezone.utc) - self.start_time
            uptime = f"Uptime: {int(td.total_seconds())}s"

        header = Panel(
            f"[bold cyan]🔱 RESEARCHER[/bold cyan] | "
            f"[green]{self.config.tty_path}[/green] | "
            f"[yellow]VT_PROCESS[/yellow] | {uptime}",
            style="blue",
        )
        layout["header"].update(header)

        # Body - Research status
        body_table = Table(show_header=True, header_style="bold magenta")
        body_table.add_column("Metric", style="cyan")
        body_table.add_column("Value", style="green")

        # Get research stats from reader
        if self._reader:
            try:
                status = self._reader.get_status_report()
                body_table.add_row("Research Sessions", str(status.get("research_sessions", 0)))
                body_table.add_row("Cache Hits", str(status.get("cache_hits", 0)))
                body_table.add_row("API Calls", str(status.get("api_calls", 0)))
            except Exception as e:
                logger.debug("Reader status report unavailable: %s", e)
                body_table.add_row("Status", "Reader unavailable")

        body_table.add_row("Entity", self.config.entity_name)
        body_table.add_row("TTY", self.config.tty_path)
        body_table.add_row("VT Mode", "VT_PROCESS")
        body_table.add_row("Lock Switch", "Yes" if self.config.lock_switch else "No")

        layout["body"].update(Panel(body_table, title="Research Dashboard", border_style="green"))

        # Footer
        vt_state = self.vt.get_state()
        footer = Panel(
            f"Active VT: {vt_state.get('active_vt', '?')} | "
            f"Open VTs: {vt_state.get('open_vts', [])} | "
            f"PID: {os.getpid()} | "
            f"Press Ctrl+C to stop",
            style="dim",
        )
        layout["footer"].update(footer)

        return layout


class RocRacoonTTYAgent(TTYAgent):
    """Roc Racoon miner agent on dedicated TTY."""

    def get_capabilities(self) -> list[str]:
        return super().get_capabilities() + [
            "legacy_mining",
            "pattern_extraction",
            "cross_partition_archaeology",
        ]

    def render_dashboard(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3), Layout(name="body"), Layout(name="footer", size=3)
        )

        uptime = ""
        if self.start_time:
            td = datetime.now(timezone.utc) - self.start_time
            uptime = f"Uptime: {int(td.total_seconds())}s"

        header = Panel(
            f"[bold magenta]🦝 ROC RACOON[/bold magenta] | "
            f"[green]{self.config.tty_path}[/green] | "
            f"[yellow]VT_PROCESS[/yellow] | {uptime}",
            style="magenta",
        )
        layout["header"].update(header)

        body_table = Table(show_header=True, header_style="bold magenta")
        body_table.add_column("Metric", style="cyan")
        body_table.add_column("Value", style="green")
        body_table.add_row("Entity", self.config.entity_name)
        body_table.add_row("TTY", self.config.tty_path)
        body_table.add_row("VT Mode", "VT_PROCESS")
        body_table.add_row("Mining Status", "Active")

        layout["body"].update(Panel(body_table, title="Mining Dashboard", border_style="magenta"))

        vt_state = self.vt.get_state()
        footer = Panel(
            f"Active VT: {vt_state.get('active_vt', '?')} | "
            f"Open VTs: {vt_state.get('open_vts', [])} | "
            f"PID: {os.getpid()}",
            style="dim",
        )
        layout["footer"].update(footer)

        return layout


class KaliTTYAgent(TTYAgent):
    """Kali oversight agent on dedicated TTY."""

    def get_capabilities(self) -> list[str]:
        return super().get_capabilities() + [
            "fleet_oversight",
            "drift_detection",
            "mandate_enforcement",
            "hivemind_coordination",
            "agent_delegation",
        ]

    def render_dashboard(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3), Layout(name="body"), Layout(name="footer", size=3)
        )

        uptime = ""
        if self.start_time:
            td = datetime.now(timezone.utc) - self.start_time
            uptime = f"Uptime: {int(td.total_seconds())}s"

        header = Panel(
            f"[bold red]⚖️ KALI[/bold red] | "
            f"[green]{self.config.tty_path}[/green] | "
            f"[yellow]VT_PROCESS[/yellow] | {uptime}",
            style="red",
        )
        layout["header"].update(header)

        body_table = Table(show_header=True, header_style="bold red")
        body_table.add_column("Metric", style="cyan")
        body_table.add_column("Value", style="green")
        body_table.add_row("Entity", self.config.entity_name)
        body_table.add_row("TTY", self.config.tty_path)
        body_table.add_row("VT Mode", "VT_PROCESS")
        body_table.add_row("Oversight Status", "Monitoring")

        layout["body"].update(Panel(body_table, title="Oversight Dashboard", border_style="red"))

        vt_state = self.vt.get_state()
        footer = Panel(
            f"Active VT: {vt_state.get('active_vt', '?')} | "
            f"Open VTs: {vt_state.get('open_vts', [])} | "
            f"PID: {os.getpid()}",
            style="dim",
        )
        layout["footer"].update(footer)

        return layout


class ObservabilityTTYAgent(TTYAgent):
    """Observability dashboard on dedicated TTY (dmesg, journalctl, htop)."""

    def get_capabilities(self) -> list[str]:
        return super().get_capabilities() + [
            "kernel_log_stream",
            "journal_stream",
            "system_metrics",
            "crash_analysis",
        ]

    def render_dashboard(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3), Layout(name="body"), Layout(name="footer", size=3)
        )

        uptime = ""
        if self.start_time:
            td = datetime.now(timezone.utc) - self.start_time
            uptime = f"Uptime: {int(td.total_seconds())}s"

        header = Panel(
            f"[bold green]📊 OBSERVABILITY[/bold green] | "
            f"[green]{self.config.tty_path}[/green] | "
            f"[yellow]VT_PROCESS[/yellow] | {uptime}",
            style="green",
        )
        layout["header"].update(header)

        # Split body into kernel logs and metrics
        layout["body"].split_row(Layout(name="kernel", ratio=1), Layout(name="metrics", ratio=1))

        # Kernel log panel (would stream dmesg -w)
        kernel_panel = Panel(
            "[dim]Kernel log stream (dmesg -w)[/dim]\n[dim]Connect: journalctl -k -f[/dim]",
            title="Kernel Ring Buffer",
            border_style="yellow",
        )
        layout["kernel"].update(kernel_panel)

        # Metrics panel
        metrics_table = Table(show_header=True, header_style="bold green")
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="green")

        # Get hardware stats
        try:
            import psutil

            cpu = psutil.cpu_percent(interval=0.1, percpu=True)
            mem = psutil.virtual_memory()
            metrics_table.add_row("CPU (per core)", " ".join(f"{c:.0f}%" for c in cpu))
            metrics_table.add_row(
                "Memory", f"{mem.percent:.1f}% ({mem.used // 1024**3}G/{mem.total // 1024**3}G)"
            )
            metrics_table.add_row("Swap", f"{psutil.swap_memory().percent:.1f}%")
        except Exception as e:
            logger.debug("System metrics unavailable: %s", e)
            metrics_table.add_row("System", "psutil unavailable")

        metrics_table.add_row("Entity", self.config.entity_name)
        metrics_table.add_row("TTY", self.config.tty_path)
        metrics_table.add_row("VT Mode", "VT_PROCESS")

        layout["metrics"].update(Panel(metrics_table, title="System Metrics", border_style="green"))

        vt_state = self.vt.get_state()
        footer = Panel(
            f"Active VT: {vt_state.get('active_vt', '?')} | "
            f"Open VTs: {vt_state.get('open_vts', [])} | "
            f"PID: {os.getpid()} | "
            f"Press Ctrl+C to stop",
            style="dim",
        )
        layout["footer"].update(footer)

        return layout


# ============================================================================
# AGENT FACTORY
# ============================================================================

AGENT_CLASSES = {
    "researcher": ResearcherTTYAgent,
    "roc_racoon": RocRacoonTTYAgent,
    "kali": KaliTTYAgent,
    "observability": ObservabilityTTYAgent,
}


def create_agent(entity: str, tty_path: str, data_dir: Path) -> TTYAgent:
    """Create agent instance for entity."""
    agent_class = AGENT_CLASSES.get(entity.lower())
    if not agent_class:
        raise ValueError(f"Unknown entity: {entity}. Available: {list(AGENT_CLASSES.keys())}")

    config = TTYAgentConfig(entity_name=entity, tty_path=tty_path, data_dir=data_dir)
    return agent_class(config)


# ============================================================================
# SIGNAL HANDLING (D-630, anyio-native)
# ============================================================================

# [M23] No bare ``except: pass``. Windows has no native signal support:
# asyncio's ProactorEventLoop does not implement loop signal handlers at all
# (CPython asyncio/events.py:595 raises NotImplementedError from
# add_signal_handler), and anyio's asyncio backend calls that method directly.
# The pre-conversion code caught that NotImplementedError and carried on, which
# is the M23 soft-failure that has now been removed. Where a receiver cannot be
# installed we say so and simply do not install one — genuine errors propagate.
_WINDOWS = sys.platform == "win32"


async def signal_watch(scope: anyio.CancelScope, startup_done: anyio.Event) -> None:
    """Deliver SIGINT/SIGTERM to the application as structured cancellation.

    This is the canonical anyio pattern
    (https://anyio.readthedocs.io/en/stable/signals.html). On the asyncio
    backend ``anyio.open_signal_receiver`` is a *synchronous* context manager
    wrapping ``loop.add_signal_handler`` — the same mechanism the file used
    before D-630, so nothing about TTY signal delivery changes.

    Ordering notes that are load-bearing:

    * ``scope.cancel()`` must be called from INSIDE the task group.
      ``anyio.create_task_group().__aexit__`` waits for its children, it does
      not cancel them; cancelling an already-joined scope hangs forever
      (``docs/adr/ADR-003`` §8, "cancelling an already-joined scope hangs").
    * A signal that arrives while ``startup()`` is still running is *queued*
      by the receiver and only acted on once ``startup_done`` is set. Without
      this the cancellation would reach the host task mid-startup and the VT
      would be left half-acquired — a regression against the pre-D-630 code,
      whose loop handler only set an ``asyncio.Event`` and so never
      interrupted startup.
    * No ``except`` on the iterator: anyio's own tests assert that
      ``open_signal_receiver`` does not suppress cancellation
      (``tests/test_signals.py::test_task_group_cancellation_open``). Let the
      cancellation raise out of this coroutine; the task group absorbs it.
    * On exiting the ``with`` block, ``remove_signal_handler`` restores
      ``default_int_handler`` for SIGINT, NOT the Runner's handler — so a
      second ^C during shutdown raises ``KeyboardInterrupt``. That is
      deliberate: it is the operator's escape hatch, and it is exactly why
      ``agent.shutdown()`` runs shielded.
    """
    with anyio.open_signal_receiver(signal.SIGINT, signal.SIGTERM) as signals:
        async for _signum in signals:
            await startup_done.wait()
            print("\n🛑 Signal received, shutting down...")
            scope.cancel()
            return


# ============================================================================
# CLI ENTRY POINT
# ============================================================================


async def main():
    parser = argparse.ArgumentParser(description="Omega Engine TTY Agent")
    parser.add_argument(
        "--entity", "-e", required=True, choices=list(AGENT_CLASSES.keys()), help="Entity to run"
    )
    parser.add_argument("--tty", "-t", required=True, help="TTY device path (e.g., /dev/tty3)")
    parser.add_argument("--data-dir", "-d", default="data", help="Omega data directory")
    parser.add_argument("--no-lock", action="store_true", help="Don't lock VT switching")
    parser.add_argument(
        "--refresh", type=float, default=2.0, help="Dashboard refresh rate (seconds)"
    )

    args = parser.parse_args()

    # Verify TTY exists
    if not Path(args.tty).exists():
        print(f"❌ TTY device not found: {args.tty}", file=sys.stderr)
        print("Available TTYs:", file=sys.stderr)
        for tty in sorted(Path("/dev").glob("tty[0-9]*")):
            print(f"  {tty}", file=sys.stderr)
        return 1

    # Verify we can access it
    if not os.access(args.tty, os.R_OK | os.W_OK):
        print(f"❌ No read/write access to {args.tty}", file=sys.stderr)
        print("Run with sudo or add user to 'tty' group", file=sys.stderr)
        return 1

    data_dir = Path(args.data_dir).resolve()

    # Create agent
    agent = create_agent(args.entity, args.tty, data_dir)
    agent.config.lock_switch = not args.no_lock

    started = False
    startup_done = anyio.Event()

    # [D-630] One task group, because ``create_task_group().__aexit__`` WAITS for
    # its children rather than cancelling them (docs/adr/ADR-003 §1: a
    # ``while True:`` child started with ``start_soon`` blocks the join forever).
    # Everything that can be stopped by the signal lives in this one group.
    async with anyio.create_task_group() as tg:
        # The receiver is installed first, so a signal arriving during VT
        # acquisition is queued rather than lost — matching the pre-D-630 code,
        # which installed its loop handlers before startup for the same reason.
        if not _WINDOWS:
            tg.start_soon(signal_watch, tg.cancel_scope, startup_done)

        # Startup — SHIELDED, and the shield is load-bearing. Level cancellation
        # from the group's scope would otherwise hit the host task mid-startup
        # and die between ``VT_SETMODE(VT_PROCESS)`` and ``close(fd)``.
        with anyio.CancelScope(shield=True):
            started = await agent.startup()
        startup_done.set()

        if not started:
            # The receiver is parked on ``open_signal_receiver``; a task group
            # waits for its children, so the scope must be cancelled or the
            # join blocks forever. anyio's ``__anext__`` checkpoint turns this
            # into a clean cancellation (the 4.x fix for "open_signal_receiver
            # hanging if the cancel scope was cancelled before it could run").
            tg.cancel_scope.cancel()
        else:
            # ``run_until_stopped`` clears ``running`` and cancels the scope when
            # the body returns, so the heartbeat sibling and the parked signal
            # receiver both stop. Without this, a subclass whose ``run()``
            # returns normally would leave the group joining two children that
            # never end — ``create_task_group().__aexit__`` waits for its
            # children, it does not cancel them (``docs/adr/ADR-003`` §1).
            tg.start_soon(run_until_stopped, agent, tg.cancel_scope)
            tg.start_soon(agent._heartbeat_loop)

    if not started:
        # Matches the pre-D-630 behaviour: a failed startup returned 1 without
        # running shutdown().
        return 1

    # [D-630] Shielded, non-negotiable. Without the shield a cancellation
    # landing inside agent.shutdown() skips the VT ioctls below and leaves the
    # kernel holding the VT in VT_PROCESS mode for this (now dead) process.
    with anyio.CancelScope(shield=True):
        await agent.shutdown()

    return 0


async def run_until_stopped(agent: TTYAgent, scope: anyio.CancelScope) -> None:
    """Run the agent body; when it returns, stop everything the group started.

    Two things must stop when ``agent.run()`` returns on its own:

    * the heartbeat sibling, whose ``while self.running`` guard is only cleared
      by ``shutdown()`` — and ``shutdown()`` cannot run until the group exits;
    * the parked signal receiver, which would otherwise hold the task group's
      join open forever (``create_task_group().__aexit__`` waits for children,
      it does not cancel them — ``docs/adr/ADR-003`` §1).

    Cancelling the scope does both, and is safe on the signal-driven path too,
    where the scope is already cancelled and the task group absorbs it.
    """
    try:
        await agent.run()
    finally:
        agent.running = False
        scope.cancel()


if __name__ == "__main__":
    sys.exit(anyio.run(main))
