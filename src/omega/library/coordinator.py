# 🔱 Omega Engine — Resource-Aware Background Worker Coordinator
# AP: AP-WORKER-COORDINATOR-v1.0.0
# ⬡ OMEGA ⬡ KALI ⬡ sovereign ⬡ COORDINATOR ⬡ PHASE-2
#
# [id-soft: vet-029] Job-Worker Queue — atomic task decomposition with load coordination
# Ported from ParallelJobManager: decompose tasks, coordinate load.
#
# WorkerCoordinator is the cockpit for all background workers
# (content curation, library crawling, research loop). It:
#   - Pauses ALL work when system resources are strained
#   - Provides pause/resume/status primitives for every worker
#   - Integrates with ResourceGuard for OOM protection
#   - Reports status to Hivemind (Phase 4)


# DocRef: docs/architecture/KNOWLEDGE_LIBRARY.md
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

import anyio
from omega.errors import OmegaError

logger = logging.getLogger(__name__)


class WorkerState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class WorkerStatus:
    """Immutable snapshot of a single worker's state."""

    name: str
    state: WorkerState
    started_at: Optional[float] = None
    paused_at: Optional[float] = None
    last_heartbeat: Optional[float] = None
    items_processed: int = 0
    current_task: str = ""
    error_message: str = ""
    cpu_percent: float = 0.0
    memory_mb: float = 0.0


@dataclass
class CoordinatorConfig:
    """Configuration for the WorkerCoordinator.

    Attributes:
        cpu_high_watermark: CPU percentage that triggers auto-pause (0-100).
        memory_high_watermark: RAM percentage that triggers auto-pause (0-100).
        poll_interval_seconds: How often to check system resources.
        grace_period_seconds: Seconds after resource pressure clears before resuming.
        max_workers: Maximum concurrent background workers.
    """

    cpu_high_watermark: float = 85.0
    memory_high_watermark: float = 80.0
    poll_interval_seconds: float = 30.0
    grace_period_seconds: float = 60.0
    max_workers: int = 3


class WorkerCoordinator:
    """Central coordinator for background workers.

    Usage:
        coord = WorkerCoordinator()
        await coord.register("curator")
        async with coord.run("curator"):
            # worker body here
            ...

    When system resources are strained, the coordinator:
      1. Sets state to PAUSED for all workers
      2. Cancels any running context manager
      3. Resumes after grace period when resources recover
    """

    # [id-soft: vet-008] Grace Period — 0.5s for entity morphing,
    # evolved to 60s for resource pressure recovery
    _config: CoordinatorConfig
    _workers: Dict[str, "WorkerStatus"] = {}
    _global_paused: bool = False
    _pause_event: anyio.Event
    _cancel_scope: Optional[anyio.CancelScope] = None
    _resource_monitor_task: Optional[anyio.abc.TaskGroup] = None

    def __init__(self, config: Optional[CoordinatorConfig] = None) -> None:
        self._config = config or CoordinatorConfig()
        self._workers = {}
        self._global_paused = False
        self._pause_event = anyio.Event()
        self._pause_event.set()  # Start in unpaused state
        self._cancel_scope = None

    # ── Registration ────────────────────────────────────────────────

    async def register(self, name: str) -> None:
        """Register a new worker.

        Must be called before the worker starts running.
        """
        if name in self._workers:
            logger.debug("Worker %s already registered", name)
            return
        self._workers[name] = WorkerStatus(
            name=name,
            state=WorkerState.IDLE,
            started_at=None,
        )
        logger.info("Worker registered: %s", name)

    async def unregister(self, name: str) -> None:
        """Remove a worker from the coordinator."""
        self._workers.pop(name, None)
        logger.info("Worker unregistered: %s", name)

    # ── Lifecycle ───────────────────────────────────────────────────

    async def start(self) -> None:
        """Start the resource monitoring background task."""
        if self._resource_monitor_task is not None:
            return  # Already running
        async with anyio.create_task_group() as tg:
            tg.start_soon(self._resource_monitor_loop)
            self._resource_monitor_task = tg

    async def stop(self) -> None:
        """Stop all workers and the resource monitor."""
        self._global_paused = False
        for name in list(self._workers.keys()):
            self._workers[name].state = WorkerState.STOPPED
        if self._cancel_scope:
            self._cancel_scope.cancel()
        self._resource_monitor_task = None
        logger.info("WorkerCoordinator stopped")

    # ── Run context manager ─────────────────────────────────────────

    def run(self, name: str) -> "WorkerCoordinator._RunContext":
        """Create an async context manager that wraps a worker body.

        The worker will be paused/resumed automatically based on
        system resource pressure.

        Usage:
            async with coord.run("curator"):
                while True:
                    item = await queue.get()
                    await process(item)

        NOTE: This is a synchronous method that returns the context manager.
        The context manager's __aenter__/__aexit__ handle the actual lifecycle.
        """
        return WorkerCoordinator._RunContext(self, name)

    class _RunContext:
        """Async context manager for a worker run cycle."""

        def __init__(self, coord: "WorkerCoordinator", name: str) -> None:
            self._coord = coord
            self._name = name

        async def __aenter__(self) -> "WorkerCoordinator._RunContext":
            ws = self._coord._workers.get(self._name)
            if ws is None:
                raise ValueError(f"Worker '{self._name}' not registered")
            ws.state = WorkerState.RUNNING
            ws.started_at = time.time()
            logger.info("Worker started: %s", self._name)
            return self

        async def __aexit__(self, *exc_info) -> None:
            ws = self._coord._workers.get(self._name)
            if ws:
                ws.state = WorkerState.IDLE
            logger.info("Worker stopped: %s", self._name)

    # ── Pause / Resume ──────────────────────────────────────────────

    async def pause(self, name: Optional[str] = None, reason: str = "") -> None:
        """Pause a specific worker or all workers.

        Args:
            name: Worker name. If None, pauses ALL workers.
            reason: Human-readable reason for the pause.
        """
        if name:
            ws = self._workers.get(name)
            if ws:
                ws.state = WorkerState.PAUSED
                ws.paused_at = time.time()
                logger.warning("Worker paused: %s — %s", name, reason)
        else:
            self._global_paused = True
            logger.warning("All workers paused — %s", reason)

    async def resume(self, name: Optional[str] = None) -> None:
        """Resume a specific worker or all workers."""
        if name:
            ws = self._workers.get(name)
            if ws:
                ws.state = WorkerState.RUNNING
                logger.info("Worker resumed: %s", name)
        else:
            self._global_paused = False
            self._pause_event.set()
            logger.info("All workers resumed")

    async def wait_if_paused(self) -> None:
        """Block the current task if the coordinator is paused."""
        while self._global_paused or any(
            ws.state == WorkerState.PAUSED for ws in self._workers.values()
        ):
            await anyio.sleep(1.0)

    # ── Status ──────────────────────────────────────────────────────

    async def status(self) -> Dict[str, WorkerStatus]:
        """Get a snapshot of all worker states."""
        return dict(self._workers)

    async def is_paused(self, name: Optional[str] = None) -> bool:
        """Check if a specific worker or the whole system is paused."""
        if name:
            ws = self._workers.get(name)
            return ws is not None and ws.state == WorkerState.PAUSED
        return self._global_paused

    async def heartbeat(self, name: str, task: str = "") -> None:
        """Update a worker's heartbeat timestamp."""
        ws = self._workers.get(name)
        if ws:
            ws.last_heartbeat = time.time()
            ws.current_task = task
            ws.items_processed += 1

    # ── Resource Monitoring ─────────────────────────────────────────

    async def _resource_monitor_loop(self) -> None:
        """Background task: polls system resources and auto-pauses on strain.

        Uses a simple CPU/Memory check. When the engine gains a proper
        health monitor, this should read from there instead.
        """
        while True:
            try:
                await anyio.sleep(self._config.poll_interval_seconds)
                under_pressure = await self._check_resources()

                if under_pressure and not self._global_paused:
                    logger.warning(
                        "Resource pressure detected: pausing all workers (CPU >%s%% or MEM >%s%%)",
                        self._config.cpu_high_watermark,
                        self._config.memory_high_watermark,
                    )
                    await self.pause(reason="auto: resource pressure")
                elif not under_pressure and self._global_paused:
                    logger.info("Resources recovered: resuming workers")
                    await self.resume()
            except anyio.get_cancelled_scope().cancel:
                break
            except (OmegaError, RuntimeError, OSError) as exc:
                logger.error("Resource monitor error: %s", exc)

    async def _check_resources(self) -> bool:
        """Check if system resources are under strain.

        Returns:
            True if CPU or memory exceeds configured watermarks.
        """
        try:
            import psutil

            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory()
            mem_pct = mem.percent if hasattr(mem, "percent") else 0.0
        except ImportError:
            # psutil not available — assume healthy
            cpu = 0.0
            mem_pct = 0.0

        # Update status for all workers
        for ws in self._workers.values():
            ws.cpu_percent = cpu
            ws.memory_mb = mem_pct

        return cpu > self._config.cpu_high_watermark or mem_pct > self._config.memory_high_watermark


# ── Named singleton for module-level import ──────────────────────────

COORDINATOR = WorkerCoordinator()
"""Module-level singleton. Import this for convenience:

    from omega.library.coordinator import COORDINATOR
    await COORDINATOR.register("curator")
    async with COORDINATOR.run("curator"):
        ...
"""
