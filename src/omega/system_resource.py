import psutil
import anyio
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any

class ResourceZone(Enum):
    GREEN = "green"    # Optimal: < 14GB
    YELLOW = "yellow"  # Pressure: 14GB - 18GB (zRAM active)
    RED = "red"        # Critical: > 18GB (Force Cloud)

@dataclass
class ResourceSnapshot:
    physical_used_gb: float
    swap_used_gb: float
    total_pressure_gb: float
    cpu_load_percent: float
    zone: ResourceZone

class SystemResource:
    """
    Sovereign Resource Monitor for Ryzen 5700U (14GB RAM + 8GB zRAM).
    Ensures the Engine stays within hardware limits to prevent OOM and thrashing.
    """
    
    PHYSICAL_LIMIT_GB = 14.0
    ZRAM_LIMIT_GB = 8.0
    CRITICAL_LIMIT_GB = 18.0 # Physical + partial zRAM before severe thrashing

    @staticmethod
    async def get_snapshot() -> ResourceSnapshot:
        """
        Captures current system resource usage.
        Wrapped in to_thread.run_sync to ensure non-blocking I/O.
        """
        return await anyio.to_thread.run_sync(SystemResource._capture)

    @staticmethod
    def _capture() -> ResourceSnapshot:
        vm = psutil.virtual_memory()
        sm = psutil.swap_memory()
        
        physical_used = vm.used / (1024**3)
        swap_used = sm.used / (1024**3)
        total_pressure = physical_used + swap_used
        cpu_load = psutil.cpu_percent(interval=None)
        
        # Determine Zone
        if total_pressure < SystemResource.PHYSICAL_LIMIT_GB:
            zone = ResourceZone.GREEN
        elif total_pressure < SystemResource.CRITICAL_LIMIT_GB:
            zone = ResourceZone.YELLOW
        else:
            zone = ResourceZone.RED
            
        return ResourceSnapshot(
            physical_used_gb=round(physical_used, 2),
            swap_used_gb=round(swap_used, 2),
            total_pressure_gb=round(total_pressure, 2),
            cpu_load_percent=cpu_load,
            zone=zone
        )

    @classmethod
    async def get_zone(cls) -> ResourceZone:
        """Quick check for the current resource zone."""
        snapshot = await cls.get_snapshot()
        return snapshot.zone

    @classmethod
    async def is_local_inference_safe(cls) -> bool:
        """
        Returns True if the system is in the Green zone.
        Used by ModelGateway to decide between Local and Cloud.
        """
        return await cls.get_zone() == ResourceZone.GREEN
