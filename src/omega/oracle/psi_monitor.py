# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
PSI (Pressure Stall Information) Monitor

Reads /proc/pressure/{memory,cpu,io} for kernel-authoritative stall metrics.
Values are percentages (0.00 = 0%, 100.00 = 100%) representing stall time
in exponentially weighted moving average windows.

Kernel 4.20+ (PSI merged), 5.15+ (triggers supported)
Kernel source: kernel/sched/psi.c -- psi_avgs_work updates EWMA every 2s
"""

import anyio
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

import aiofiles


Resource = Literal["memory", "cpu", "io"]
StallType = Literal["some", "full"]
Window = Literal["avg10", "avg60", "avg300"]


@dataclass(frozen=True)
class PSISnapshot:
    """Single PSI reading for a resource"""

    resource: Resource
    some_avg10: float
    some_avg60: float
    some_avg300: float
    some_total_us: int
    full_avg10: float
    full_avg60: float
    full_avg300: float
    full_total_us: int


class PSIMonitor:
    """
    Async PSI monitor with caching.

    Polls /proc/pressure/{resource} at configurable interval.
    Parses 'some' (at least one task stalled) and 'full' (all tasks stalled)
    for three EWMA windows: avg10 (10s), avg60 (60s), avg300 (300s).
    """

    def __init__(
        self,
        poll_interval: float = 1.0,
        resources: tuple[Resource, ...] = ("memory", "cpu", "io"),
    ):
        self.poll_interval = poll_interval
        self.resources = resources
        self._cache: dict[Resource, PSISnapshot] = {}
        self._task_group: Optional[anyio.abc.TaskGroup] = None
        self._running = False

    async def start(self) -> None:
        """Start background polling task"""
        if self._running:
            return
        self._running = True
        self._task_group = await anyio.create_task_group().__aenter__()
        self._task_group.start_soon(self._poll_loop)
        # Initial read
        await self._poll_once()

    async def stop(self) -> None:
        """Stop background polling"""
        self._running = False
        if self._task_group:
            tg = self._task_group
            self._task_group = None
            await tg.__aexit__(None, None, None)

    async def _poll_loop(self) -> None:
        """Background polling loop"""
        while self._running:
            await anyio.sleep(self.poll_interval)
            if self._running:
                await self._poll_once()

    async def _poll_once(self) -> None:
        """Poll all resources once"""
        for resource in self.resources:
            try:
                snapshot = await self._read_pressure(resource)
                self._cache[resource] = snapshot
            except (FileNotFoundError, PermissionError, OSError):
                # PSI not available (kernel < 4.20 or not mounted)
                pass

    async def _read_pressure(self, resource: Resource) -> PSISnapshot:
        """Read and parse /proc/pressure/{resource}"""
        path = Path(f"/proc/pressure/{resource}")
        async with aiofiles.open(path, "r") as f:
            content = await f.read()
        return self._parse_pressure(content, resource)

    def _parse_pressure(self, content: str, resource: Resource) -> PSISnapshot:
        """Parse PSI output format.

        Format example:
            some avg10=0.00 avg60=0.00 avg300=0.00 total=1234567
            full avg10=0.00 avg60=0.00 avg300=0.00 total=7654321
        """
        some_avg10 = some_avg60 = some_avg300 = 0.0
        some_total_us = 0
        full_avg10 = full_avg60 = full_avg300 = 0.0
        full_total_us = 0

        for line in content.strip().splitlines():
            parts = line.split()
            if not parts:
                continue

            stall_type = parts[0]  # "some" or "full"

            for part in parts[1:]:
                if "=" not in part:
                    continue
                key, value = part.split("=", 1)

                if stall_type == "some":
                    if key == "avg10":
                        some_avg10 = float(value)
                    elif key == "avg60":
                        some_avg60 = float(value)
                    elif key == "avg300":
                        some_avg300 = float(value)
                    elif key == "total":
                        some_total_us = int(value)
                elif stall_type == "full":
                    if key == "avg10":
                        full_avg10 = float(value)
                    elif key == "avg60":
                        full_avg60 = float(value)
                    elif key == "avg300":
                        full_avg300 = float(value)
                    elif key == "total":
                        full_total_us = int(value)

        return PSISnapshot(
            resource=resource,
            some_avg10=some_avg10,
            some_avg60=some_avg60,
            some_avg300=some_avg300,
            some_total_us=some_total_us,
            full_avg10=full_avg10,
            full_avg60=full_avg60,
            full_avg300=full_avg300,
            full_total_us=full_total_us,
        )

    def get_snapshot(self, resource: Resource = "memory") -> Optional[PSISnapshot]:
        """Get latest cached snapshot (non-blocking)"""
        return self._cache.get(resource)

    async def get_pressure(
        self,
        resource: Resource = "memory",
        stall_type: StallType = "some",
        window: Window = "avg60",
    ) -> float:
        """
        Get pressure value as fraction (0.0 to 1.0).

        Args:
            resource: "memory", "cpu", or "io"
            stall_type: "some" (at least one task stalled) or "full" (all tasks stalled)
            window: "avg10" (10s), "avg60" (60s), "avg300" (300s)

        Returns:
            Pressure as fraction (0.05 = 5% stall time)
        """
        snapshot = self._cache.get(resource)
        if not snapshot:
            # Try one-shot read
            try:
                snapshot = await self._read_pressure(resource)
                self._cache[resource] = snapshot
            except (FileNotFoundError, PermissionError, OSError):
                return 0.0

        if stall_type == "some":
            if window == "avg10":
                return snapshot.some_avg10 / 100.0
            elif window == "avg60":
                return snapshot.some_avg60 / 100.0
            else:  # avg300
                return snapshot.some_avg300 / 100.0
        else:  # full
            if window == "avg10":
                return snapshot.full_avg10 / 100.0
            elif window == "avg60":
                return snapshot.full_avg60 / 100.0
            else:  # avg300
                return snapshot.full_avg300 / 100.0

    async def get_all_metrics(self) -> PSISnapshot:
        """Get latest memory PSI metrics (blocking read if not cached)"""
        return await self._read_pressure("memory")

    async def get_memory_pressure(
        self,
        stall_type: StallType = "some",
        window: Window = "avg60",
    ) -> float:
        """Convenience: get memory pressure"""
        return await self.get_pressure("memory", stall_type, window)

    def is_available(self) -> bool:
        """Check if PSI is available on this system"""
        return Path("/proc/pressure/memory").exists()


# Convenience functions for one-shot reads


async def get_psi_some_avg60() -> float:
    """One-shot read of memory PSI some.avg60"""
    monitor = PSIMonitor()
    return await monitor.get_memory_pressure("some", "avg60")


async def get_psi_full_avg10() -> float:
    """One-shot read of memory PSI full.avg10"""
    monitor = PSIMonitor()
    return await monitor.get_memory_pressure("full", "avg10")


async def read_memory_pressure(
    stall_type: StallType = "some",
    window: Window = "avg60",
) -> float:
    """One-shot read of memory pressure"""
    monitor = PSIMonitor()
    return await monitor.get_memory_pressure(stall_type, window)


async def read_psi_snapshot(resource: Resource = "memory") -> Optional[PSISnapshot]:
    """One-shot full PSI snapshot"""
    monitor = PSIMonitor()
    try:
        return await monitor._read_pressure(resource)
    except (FileNotFoundError, PermissionError, OSError):
        return None


# Synchronous versions for non-async contexts


def read_memory_pressure_sync(
    stall_type: StallType = "some",
    window: Window = "avg60",
) -> float:
    """Synchronous one-shot memory pressure read"""
    try:
        with open("/proc/pressure/memory", "r") as f:
            content = f.read()
    except (FileNotFoundError, PermissionError, OSError):
        return 0.0

    monitor = PSIMonitor()
    snapshot = monitor._parse_pressure(content, "memory")

    if stall_type == "some":
        if window == "avg10":
            return snapshot.some_avg10 / 100.0
        elif window == "avg60":
            return snapshot.some_avg60 / 100.0
        else:
            return snapshot.some_avg300 / 100.0
    else:
        if window == "avg10":
            return snapshot.full_avg10 / 100.0
        elif window == "avg60":
            return snapshot.full_avg60 / 100.0
        else:
            return snapshot.full_avg300 / 100.0


def psi_available() -> bool:
    """Check if PSI is available"""
    return Path("/proc/pressure/memory").exists()
