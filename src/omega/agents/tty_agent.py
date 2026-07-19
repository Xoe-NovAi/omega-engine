#!/usr/bin/env python3
"""
Omega Engine — TTY Agent Base Class
Runs agents on dedicated Linux Virtual Consoles (Ctrl+Alt+F3-F6)

Usage:
    python -m src.omega.agents.tty_agent --entity researcher --tty /dev/tty3
    python -m src.omega.agents.tty_agent --entity roc_racoon --tty /dev/tty4
"""

from __future__ import annotations

import argparse
import asyncio
import fcntl
import json
import os
import signal
import struct
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from omega.observability.observability_reader import SovereignReader


# ============================================================================
# VT IOCTL CONSTANTS (from linux/vt.h)
# ============================================================================

VT_OPENQRY   = 0x5600
VT_GETMODE   = 0x5601
VT_SETMODE   = 0x5602
VT_GETSTATE  = 0x5603
VT_SENDSIG   = 0x5604
VT_RELDISP   = 0x5605
VT_ACTIVATE  = 0x5606
VT_WAITACTIVE = 0x5607
VT_DISALLOCATE = 0x5608
VT_LOCKSWITCH = 0x5609
VT_UNLOCKSWITCH = 0x560A

VT_AUTO      = 0
VT_PROCESS   = 1
VT_ACKACQ    = 2


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
        """Get current VT mode."""
        if self.fd is None:
            return None
        try:
            buf = bytearray(2)
            fcntl.ioctl(self.fd, VT_GETMODE, buf)
            return struct.unpack("h", buf)[0]
        except OSError:
            return None
    
    def set_mode(self, mode: int) -> bool:
        """Set VT mode (VT_AUTO, VT_PROCESS, VT_ACKACQ)."""
        if self.fd is None:
            return False
        try:
            buf = struct.pack("h", mode)
            fcntl.ioctl(self.fd, VT_SETMODE, buf)
            return True
        except OSError as e:
            print(f"❌ VT_SETMODE failed: {e}", file=sys.stderr)
            return False
    
    def acquire_process_mode(self) -> bool:
        """Acquire VT_PROCESS mode — we own this VT."""
        # Save original mode first
        self._original_mode = struct.pack("h", self.get_mode() or VT_AUTO)
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
                "open_vts": [b for b in buf[2:] if b != 0]
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
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._reader: Optional[SovereignReader] = None
    
    async def startup(self) -> bool:
        """Initialize VT and agent."""
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
            crash_dir=self.config.data_dir / "crashes"
        )
        
        # 6. Register with Hivemind
        await self._register_hivemind()
        
        # 7. Start heartbeat
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        self.running = True
        self.start_time = datetime.now(timezone.utc)
        print(f"✅ {self.config.entity_name} ready on {self.config.tty_path}")
        return True
    
    async def shutdown(self):
        """Clean shutdown."""
        print(f"🛑 Shutting down {self.config.entity_name}...")
        self.running = False
        
        # Stop heartbeat
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
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
            "capabilities": self.get_capabilities()
        }
        reg_file.write_text(json.dumps(reg_data, indent=2))
    
    async def _deregister_hivemind(self):
        """Deregister agent from Hivemind."""
        reg_file = self.config.hivemind_dir / f"{self.config.entity_name}.json"
        if reg_file.exists():
            reg_file.unlink()
    
    async def _heartbeat_loop(self):
        """Periodic heartbeat to Hivemind."""
        while self.running:
            await asyncio.sleep(30)  # Every 30 seconds
            if not self.running:
                break
            
            reg_file = self.config.hivemind_dir / f"{self.config.entity_name}.json"
            if reg_file.exists():
                data = json.loads(reg_file.read_text())
                data["last_heartbeat"] = datetime.now(timezone.utc).isoformat()
                data["uptime_seconds"] = (datetime.now(timezone.utc) - self.start_time).total_seconds()
                reg_file.write_text(json.dumps(data, indent=2))
    
    def get_capabilities(self) -> list[str]:
        """Override in subclass to declare capabilities."""
        return ["tty_agent", "vt_process_mode"]
    
    def render_dashboard(self) -> Layout:
        """Override in subclass to provide custom dashboard."""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
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
            style="blue"
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
            style="dim"
        )
        layout["footer"].update(footer)
        
        return layout
    
    async def run_dashboard(self, refresh_rate: float = 2.0):
        """Run live dashboard on TTY."""
        if not self.console:
            return
        
        self._layout = self.render_dashboard()
        
        with Live(self._layout, console=self.console, refresh_per_second=1/refresh_rate, screen=True) as live:
            self._live = live
            while self.running:
                await asyncio.sleep(refresh_rate)
                if not self.running:
                    break
                self._layout = self.render_dashboard()
                live.update(self._layout)
    
    async def run(self):
        """Main run loop — override in subclass."""
        await self.run_dashboard()


# ============================================================================
# ENTITY-SPECIFIC AGENTS
# ============================================================================

class ResearcherTTYAgent(TTYAgent):
    """Researcher agent on dedicated TTY."""
    
    def get_capabilities(self) -> list[str]:
        return super().get_capabilities() + [
            "deep_research", "web_scraping", "api_integration",
            "model_registry", "freshness_checking"
        ]
    
    def render_dashboard(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
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
            style="blue"
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
            except Exception:
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
            style="dim"
        )
        layout["footer"].update(footer)
        
        return layout


class RocRacoonTTYAgent(TTYAgent):
    """Roc Racoon miner agent on dedicated TTY."""
    
    def get_capabilities(self) -> list[str]:
        return super().get_capabilities() + [
            "legacy_mining", "pattern_extraction", "cross_partition_archaeology"
        ]
    
    def render_dashboard(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        uptime = ""
        if self.start_time:
            td = datetime.now(timezone.utc) - self.start_time
            uptime = f"Uptime: {int(td.total_seconds())}s"
        
        header = Panel(
            f"[bold magenta]🦝 ROC RACOON[/bold magenta] | "
            f"[green]{self.config.tty_path}[/green] | "
            f"[yellow]VT_PROCESS[/yellow] | {uptime}",
            style="magenta"
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
            style="dim"
        )
        layout["footer"].update(footer)
        
        return layout


class KaliTTYAgent(TTYAgent):
    """Kali oversight agent on dedicated TTY."""
    
    def get_capabilities(self) -> list[str]:
        return super().get_capabilities() + [
            "fleet_oversight", "drift_detection", "mandate_enforcement",
            "hivemind_coordination", "agent_delegation"
        ]
    
    def render_dashboard(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        uptime = ""
        if self.start_time:
            td = datetime.now(timezone.utc) - self.start_time
            uptime = f"Uptime: {int(td.total_seconds())}s"
        
        header = Panel(
            f"[bold red]⚖️ KALI[/bold red] | "
            f"[green]{self.config.tty_path}[/green] | "
            f"[yellow]VT_PROCESS[/yellow] | {uptime}",
            style="red"
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
            style="dim"
        )
        layout["footer"].update(footer)
        
        return layout


class ObservabilityTTYAgent(TTYAgent):
    """Observability dashboard on dedicated TTY (dmesg, journalctl, htop)."""
    
    def get_capabilities(self) -> list[str]:
        return super().get_capabilities() + [
            "kernel_log_stream", "journal_stream", "system_metrics", "crash_analysis"
        ]
    
    def render_dashboard(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        uptime = ""
        if self.start_time:
            td = datetime.now(timezone.utc) - self.start_time
            uptime = f"Uptime: {int(td.total_seconds())}s"
        
        header = Panel(
            f"[bold green]📊 OBSERVABILITY[/bold green] | "
            f"[green]{self.config.tty_path}[/green] | "
            f"[yellow]VT_PROCESS[/yellow] | {uptime}",
            style="green"
        )
        layout["header"].update(header)
        
        # Split body into kernel logs and metrics
        layout["body"].split_row(
            Layout(name="kernel", ratio=1),
            Layout(name="metrics", ratio=1)
        )
        
        # Kernel log panel (would stream dmesg -w)
        kernel_panel = Panel(
            "[dim]Kernel log stream (dmesg -w)[/dim]\n"
            "[dim]Connect: journalctl -k -f[/dim]",
            title="Kernel Ring Buffer",
            border_style="yellow"
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
            metrics_table.add_row("Memory", f"{mem.percent:.1f}% ({mem.used//1024**3}G/{mem.total//1024**3}G)")
            metrics_table.add_row("Swap", f"{psutil.swap_memory().percent:.1f}%")
        except Exception:
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
            style="dim"
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
    
    config = TTYAgentConfig(
        entity_name=entity,
        tty_path=tty_path,
        data_dir=data_dir
    )
    return agent_class(config)


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

async def main():
    parser = argparse.ArgumentParser(description="Omega Engine TTY Agent")
    parser.add_argument("--entity", "-e", required=True,
                        choices=list(AGENT_CLASSES.keys()),
                        help="Entity to run")
    parser.add_argument("--tty", "-t", required=True,
                        help="TTY device path (e.g., /dev/tty3)")
    parser.add_argument("--data-dir", "-d", default="data",
                        help="Omega data directory")
    parser.add_argument("--no-lock", action="store_true",
                        help="Don't lock VT switching")
    parser.add_argument("--refresh", type=float, default=2.0,
                        help="Dashboard refresh rate (seconds)")
    
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
    
    # Setup signal handlers
    loop = asyncio.get_running_loop()
    shutdown_event = asyncio.Event()
    
    def signal_handler():
        print("\n🛑 Signal received, shutting down...")
        shutdown_event.set()
    
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, signal_handler)
        except NotImplementedError:
            pass  # Windows
    
    # Startup
    if not await agent.startup():
        return 1
    
    # Run until shutdown
    try:
        run_task = asyncio.create_task(agent.run())
        await shutdown_event.wait()
        run_task.cancel()
        try:
            await run_task
        except asyncio.CancelledError:
            pass
    finally:
        await agent.shutdown()
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))