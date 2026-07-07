# AP: AP-PR-READINESS-v1.0.0
# 🔱 Omega Engine — Hardware Detection
# Detects RAM at startup for model tier recommendations.


# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
import os
import psutil
from dataclasses import dataclass

@dataclass
class HardwareProfile:
    total_ram_gb: float
    available_ram_gb: float
    cpu_count: int
    is_zen2: bool = False

    @property
    def ai_ram_gb(self) -> float:
        """RAM available for AI workloads (~2GB reserved for OS)."""
        return max(0, self.available_ram_gb - 2.0)


def detect_hardware() -> HardwareProfile:
    """Detect current hardware capabilities."""
    mem = psutil.virtual_memory()
    total_gb = mem.total / (1024 ** 3)
    avail_gb = mem.available / (1024 ** 3)

    # Simple Zen 2 detection via /proc/cpuinfo
    is_zen2 = False
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if "model name" in line and "Ryzen 7" in line:
                    is_zen2 = True
                    break
    except FileNotFoundError:
        pass

    return HardwareProfile(
        total_ram_gb=round(total_gb, 1),
        available_ram_gb=round(avail_gb, 1),
        cpu_count=os.cpu_count() or 8,
        is_zen2=is_zen2,
    )
