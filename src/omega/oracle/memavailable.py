# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
MemAvailable Reader
Reads kernel's authoritative available memory estimate from /proc/meminfo

Kernel source: mm/page_alloc.c - si_mem_available()
- Accounts for free pages, page cache, reclaimable slab
- Subtracts watermark reserves (min/low/high)
- This is what the OOM killer uses (oom_badness in mm/oom_kill.c)
"""

from pathlib import Path
from typing import Optional

import anyio
import aiofiles


class MemAvailableReader:
    """
    Reads MemAvailable from /proc/meminfo.

    MemAvailable: 8123456 kB

    This is the kernel's estimate of memory available for new allocations
    without triggering reclaim. It accounts for:
    - NR_FREE_PAGES (truly free)
    - Page cache (active_file + inactive_file) minus watermark reserves
    - Reclaimable slab (SReclaimable) minus watermark reserves
    - Minus totalreserve_pages (min/low/high watermarks)

    This is the authoritative signal - userspace counters drift, kernel knows truth.
    """

    MEMINFO_PATH = Path("/proc/meminfo")

    def __init__(self, cache_ttl: float = 0.5):
        self._cache_gb: Optional[float] = None
        self._cache_kb: Optional[int] = None
        self._cache_time: float = 0.0
        self._cache_ttl = cache_ttl

    async def get_memavailable_gb(self) -> float:
        """
        Get MemAvailable in gigabytes.

        Returns:
            Available memory in GB (e.g., 8.12)
        """
        now = anyio.current_time()

        if self._cache_gb is not None and (now - self._cache_time) < self._cache_ttl:
            return self._cache_gb

        try:
            async with aiofiles.open(self.MEMINFO_PATH, "r") as f:
                content = await f.read()
        except (FileNotFoundError, PermissionError):
            return 0.0

        gb = self._parse_memavailable(content)
        self._cache_gb = gb
        self._cache_kb = int(gb * 1024 * 1024)
        self._cache_time = now
        return gb

    def _parse_memavailable(self, content: str) -> float:
        """Parse MemAvailable from /proc/meminfo content"""
        for line in content.splitlines():
            if line.startswith("MemAvailable:"):
                # Format: "MemAvailable:    8123456 kB"
                parts = line.split()
                if len(parts) >= 2:
                    kb = int(parts[1])
                    return kb / (1024 * 1024)  # kB -> GB
        return 0.0

    async def get_memavailable_kb(self) -> int:
        """Get MemAvailable in kilobytes (raw kernel value)"""
        await self.get_memavailable_gb()  # Populates cache
        return self._cache_kb or 0

    async def get_memavailable_mb(self) -> int:
        """Get MemAvailable in megabytes"""
        gb = await self.get_memavailable_gb()
        return int(gb * 1024)

    async def get_memavailable_bytes(self) -> int:
        """Get MemAvailable in bytes"""
        kb = await self.get_memavailable_kb()
        return kb * 1024

    def clear_cache(self) -> None:
        """Force cache invalidation on next read"""
        self._cache_gb = None
        self._cache_kb = None
        self._cache_time = 0.0


# Convenience functions (create new reader each call - stateless)


async def get_memavailable_gb() -> float:
    """Get MemAvailable in GB"""
    reader = MemAvailableReader()
    return await reader.get_memavailable_gb()


async def get_memavailable_mb() -> int:
    """Get MemAvailable in MB"""
    reader = MemAvailableReader()
    return await reader.get_memavailable_mb()


async def get_memavailable_kb() -> int:
    """Get MemAvailable in kB"""
    reader = MemAvailableReader()
    return await reader.get_memavailable_kb()


async def get_memavailable_bytes() -> int:
    """Get MemAvailable in bytes"""
    reader = MemAvailableReader()
    return await reader.get_memavailable_bytes()


# Synchronous versions for non-async contexts


def get_memavailable_gb_sync() -> float:
    """Synchronous MemAvailable read in GB"""
    try:
        with open("/proc/meminfo", "r") as f:
            content = f.read()
    except (FileNotFoundError, PermissionError):
        return 0.0

    for line in content.splitlines():
        if line.startswith("MemAvailable:"):
            parts = line.split()
            if len(parts) >= 2:
                kb = int(parts[1])
                return kb / (1024 * 1024)
    return 0.0


def get_memavailable_mb_sync() -> int:
    """Synchronous MemAvailable read in MB"""
    gb = get_memavailable_gb_sync()
    return int(gb * 1024)


def get_memavailable_kb_sync() -> int:
    """Synchronous MemAvailable read in kB"""
    try:
        with open("/proc/meminfo", "r") as f:
            content = f.read()
    except (FileNotFoundError, PermissionError):
        return 0

    for line in content.splitlines():
        if line.startswith("MemAvailable:"):
            parts = line.split()
            if len(parts) >= 2:
                return int(parts[1])
    return 0


def get_memavailable_bytes_sync() -> int:
    """Synchronous MemAvailable read in bytes"""
    return get_memavailable_kb_sync() * 1024


# Hardware floor reference (Ryzen 7 5700U)

HARDWARE_FLOOR = {
    "tdp_watts": 15,
    "l3_cache_mb": 8,  # Victim cache, not inclusive
    "ccx_count": 2,
    "cores_per_ccx": 4,
    "memory_bandwidth_gb_s": 51,  # DDR4-3200 dual channel
    "total_ram_gb": 16,
    "available_ram_idle_gb": 8,  # ~8GB at idle after kernel/page cache
}

MODEL_PROFILE = {
    "model_ram_gb": 1.7,  # GGUF weights (Qwen3-1.7B)
    "kv_cache_gb_per_8k": 0.5,  # 8K context
    "reserve_gb": 1.0,  # OS + page cache headroom
    "total_per_instance_gb": 3.2,
}

# Threshold calibration matrix (from R_CG02 research)

THRESHOLDS = {
    "memavailable": {
        "healthy_gb": 4.0,  # > 4GB = comfortable
        "warning_gb": 2.0,  # 2-4GB = throttle
        "critical_gb": 2.0,  # < 2GB = deny (below hard reserve)
    },
    "model_instance": {
        "min_headroom_gb": 3.2,  # One model instance + reserve
        "recommended_headroom_gb": 6.4,  # Two instances + reserve
    },
}


def check_memavailable_health() -> dict:
    """
    Quick health check using synchronous reads.

    Returns:
        Dict with available_gb, status, and recommendation
    """
    available_gb = get_memavailable_gb_sync()

    if available_gb >= THRESHOLDS["memavailable"]["healthy_gb"]:
        status = "healthy"
        recommendation = "allow"
    elif available_gb >= THRESHOLDS["memavailable"]["warning_gb"]:
        status = "warning"
        recommendation = "throttle"
    else:
        status = "critical"
        recommendation = "deny"

    return {
        "available_gb": round(available_gb, 2),
        "status": status,
        "recommendation": recommendation,
        "thresholds": THRESHOLDS["memavailable"],
    }


def can_load_model(
    model_gb: float = 1.7, kv_cache_gb: float = 0.5, reserve_gb: float = 1.0
) -> bool:
    """
    Check if we can load a model with given memory requirements.

    Args:
        model_gb: Model weights in GB
        kv_cache_gb: KV cache for context in GB
        reserve_gb: OS/page cache reserve in GB

    Returns:
        True if MemAvailable >= model + kv_cache + reserve
    """
    available_gb = get_memavailable_gb_sync()
    required_gb = model_gb + kv_cache_gb + reserve_gb
    return available_gb >= required_gb


def get_model_capacity(
    model_gb: float = 1.7, kv_cache_gb: float = 0.5, reserve_gb: float = 1.0
) -> int:
    """
    Calculate how many model instances can fit in available memory.

    Returns:
        Number of instances that can be loaded (0 = none)
    """
    available_gb = get_memavailable_gb_sync()
    required_per_instance = model_gb + kv_cache_gb + reserve_gb
    return max(0, int(available_gb / required_per_instance))
