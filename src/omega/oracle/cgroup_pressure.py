"""
cgroup v2 Memory Pressure Monitor

Reads memory.pressure from cgroup v2 filesystem for per-slice/container pressure.
Hierarchical: parent cgroup includes children's stall time.
Compatible with systemd-oomd pressure levels.

Kernel 5.2+ (memory.pressure), 5.15+ (memory.pressure_level)
Kernel source: kernel/cgroup/cgroup.c -- memory_pressure_read aggregates PSI per cgroup
"""
import anyio
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

import aiofiles


PressureLevel = Literal["low", "medium", "high", "critical"]
StallType = Literal["some", "full"]
Window = Literal["avg10", "avg60", "avg300"]


@dataclass(frozen=True)
class CgroupPressureSnapshot:
    """Parsed cgroup memory.pressure snapshot"""
    cgroup_path: str
    some_avg10: float
    some_avg60: float
    some_avg300: float
    some_total_us: int
    full_avg10: float
    full_avg60: float
    full_avg300: float
    full_total_us: int
    pressure_level: Optional[PressureLevel] = None


class CgroupPressureMonitor:
    """
    Monitor cgroup v2 memory.pressure for container-aware memory pressure.

    Reads from /sys/fs/cgroup/.../memory.pressure (or custom cgroup path).
    Parses same format as /proc/pressure/memory but per-cgroup.
    """

    def __init__(
        self,
        cgroup_path: str = "/sys/fs/cgroup",
        poll_interval: float = 2.0,
    ):
        self.cgroup_path = Path(cgroup_path)
        self.poll_interval = poll_interval
        self._cache: Optional[CgroupPressureSnapshot] = None
        self._task_group: Optional[anyio.abc.TaskGroup] = None
        self._running = False

    async def start(self) -> None:
        """Start background polling"""
        if self._running:
            return
        self._running = True
        self._task_group = await anyio.create_task_group().__aenter__()
        self._task_group.start_soon(self._poll_loop)
        await self._poll_once()

    async def stop(self) -> None:
        """Stop background polling"""
        self._running = False
        if self._task_group:
            tg = self._task_group
            self._task_group = None
            await tg.__aexit__(None, None, None)

    async def _poll_loop(self) -> None:
        while self._running:
            await anyio.sleep(self.poll_interval)
            if self._running:
                await self._poll_once()

    async def _poll_once(self) -> None:
        try:
            snapshot = await self._read_pressure()
            self._cache = snapshot
        except (FileNotFoundError, PermissionError, OSError):
            pass

    async def _read_pressure(self) -> CgroupPressureSnapshot:
        """Read and parse memory.pressure + memory.pressure_level"""
        pressure_file = self.cgroup_path / "memory.pressure"
        level_file = self.cgroup_path / "memory.pressure_level"

        async with aiofiles.open(pressure_file, "r") as f:
            content = await f.read()

        snapshot = self._parse_pressure(content)
        snapshot = CgroupPressureSnapshot(
            cgroup_path=str(self.cgroup_path),
            some_avg10=snapshot.some_avg10,
            some_avg60=snapshot.some_avg60,
            some_avg300=snapshot.some_avg300,
            some_total_us=snapshot.some_total_us,
            full_avg10=snapshot.full_avg10,
            full_avg60=snapshot.full_avg60,
            full_avg300=snapshot.full_avg300,
            full_total_us=snapshot.full_total_us,
        )

        # Read pressure level if available (systemd-oomd compatible)
        try:
            async with aiofiles.open(level_file, "r") as f:
                level_content = await f.read()
            level = level_content.strip()
            if level in ("low", "medium", "high", "critical"):
                snapshot = CgroupPressureSnapshot(
                    cgroup_path=str(self.cgroup_path),
                    some_avg10=snapshot.some_avg10,
                    some_avg60=snapshot.some_avg60,
                    some_avg300=snapshot.some_avg300,
                    some_total_us=snapshot.some_total_us,
                    full_avg10=snapshot.full_avg10,
                    full_avg60=snapshot.full_avg60,
                    full_avg300=snapshot.full_avg300,
                    full_total_us=snapshot.full_total_us,
                    pressure_level=level,
                )
        except (FileNotFoundError, PermissionError, OSError):
            pass

        return snapshot

    def _parse_pressure(self, content: str) -> CgroupPressureSnapshot:
        """Parse memory.pressure format (same as /proc/pressure/memory)"""
        some_avg10 = some_avg60 = some_avg300 = 0.0
        some_total_us = 0
        full_avg10 = full_avg60 = full_avg300 = 0.0
        full_total_us = 0

        for line in content.strip().splitlines():
            parts = line.split()
            if not parts:
                continue

            stall_type = parts[0]

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

        return CgroupPressureSnapshot(
            cgroup_path=str(self.cgroup_path),
            some_avg10=some_avg10,
            some_avg60=some_avg60,
            some_avg300=some_avg300,
            some_total_us=some_total_us,
            full_avg10=full_avg10,
            full_avg60=full_avg60,
            full_avg300=full_avg300,
            full_total_us=full_total_us,
        )

    def get_snapshot(self) -> Optional[CgroupPressureSnapshot]:
        """Get latest cached snapshot"""
        return self._cache

    async def get_pressure(
        self,
        stall_type: StallType = "some",
        window: Window = "avg60",
    ) -> float:
        """
        Get pressure as fraction (0.0 to 1.0).

        Returns 0.0 if cgroup pressure not available.
        """
        snapshot = self._cache
        if not snapshot:
            try:
                snapshot = await self._read_pressure()
                self._cache = snapshot
            except (FileNotFoundError, PermissionError, OSError):
                return 0.0

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

    def get_pressure_level(self) -> Optional[PressureLevel]:
        """Get systemd-oomd compatible pressure level"""
        return self._cache.pressure_level if self._cache else None

    def is_available(self) -> bool:
        """Check if cgroup v2 pressure is available"""
        return (self.cgroup_path / "memory.pressure").exists()


# Convenience functions

async def read_cgroup_pressure(
    cgroup_path: str = "/sys/fs/cgroup",
    stall_type: StallType = "some",
    window: Window = "avg60",
) -> float:
    """One-shot read of cgroup memory pressure"""
    monitor = CgroupPressureMonitor(cgroup_path)
    return await monitor.get_pressure(stall_type, window)


async def read_cgroup_snapshot(cgroup_path: str = "/sys/fs/cgroup") -> Optional[CgroupPressureSnapshot]:
    """One-shot full cgroup pressure snapshot"""
    monitor = CgroupPressureMonitor(cgroup_path)
    try:
        return await monitor._read_pressure()
    except (FileNotFoundError, PermissionError, OSError):
        return None


def read_cgroup_pressure_sync(
    cgroup_path: str = "/sys/fs/cgroup",
    stall_type: StallType = "some",
    window: Window = "avg60",
) -> float:
    """Synchronous one-shot cgroup pressure read"""
    pressure_file = Path(cgroup_path) / "memory.pressure"
    try:
        with open(pressure_file, "r") as f:
            content = f.read()
    except (FileNotFoundError, PermissionError, OSError):
        return 0.0

    monitor = CgroupPressureMonitor(cgroup_path)
    snapshot = monitor._parse_pressure(content)

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


def cgroup_pressure_available(cgroup_path: str = "/sys/fs/cgroup") -> bool:
    """Check if cgroup v2 pressure is available"""
    return Path(cgroup_path, "memory.pressure").exists()


def get_current_cgroup_path() -> str:
    """Get current process's cgroup path from /proc/self/cgroup"""
    try:
        with open("/proc/self/cgroup", "r") as f:
            for line in f:
                # Format: 0::/user.slice/user-1000.slice/session-1.scope
                parts = line.strip().split(":")
                if len(parts) >= 3 and parts[1] == "":
                    # cgroup v2 unified hierarchy
                    cgroup_rel = parts[2]
                    return f"/sys/fs/cgroup{cgroup_rel}"
    except (FileNotFoundError, PermissionError, IndexError):
        pass
    return "/sys/fs/cgroup"
