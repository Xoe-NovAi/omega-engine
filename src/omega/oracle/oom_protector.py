"""
OOMProtector — Three-Signal Fusion for Admission Control

Fuses authoritative kernel memory pressure signals:
1. PSI (Pressure Stall Information) — /proc/pressure/memory
2. MemAvailable — /proc/meminfo (kernel's reclaimable estimate)
3. cgroup v2 memory.pressure — per-cgroup PSI (container-aware)

Kernel knows best — userspace counters drift; kernel signals are authoritative.

Decision: ALLOW | THROTTLE | DENY_OOM_RISK | DENY_THRASHING
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import anyio

from .psi_monitor import PSIMonitor, get_psi_some_avg60, get_psi_full_avg10
from .memavailable import MemAvailableReader, get_memavailable_gb
from .cgroup_pressure import CgroupPressureMonitor, read_cgroup_pressure, cgroup_pressure_available


class AdmissionResult(Enum):
    """Admission control decision"""
    ALLOW = "allow"                    # All signals healthy
    THROTTLE = "throttle"              # Pressure detected, reduce load
    DENY_OOM_RISK = "deny_oom_risk"    # MemAvailable below reserve
    DENY_THRASHING = "deny_thrashing"  # PSI full stall > 5%


@dataclass(frozen=True)
class PressureSnapshot:
    """Snapshot of all three pressure signals at decision time"""
    # PSI signals (system-wide)
    psi_some_avg60: float      # Fraction (0.0-1.0)
    psi_full_avg10: float      # Fraction (0.0-1.0)
    psi_some_avg10: float
    psi_some_avg300: float
    psi_full_avg60: float
    psi_full_avg300: float
    
    # MemAvailable (system-wide)
    memavailable_gb: float
    
    # cgroup pressure (container-aware, optional)
    cgroup_some_avg60: Optional[float] = None
    cgroup_full_avg10: Optional[float] = None
    cgroup_pressure_level: Optional[str] = None
    cgroup_available: bool = False


@dataclass(frozen=True)
class OOMProtectorConfig:
    """Configuration thresholds (calibrated for Ryzen 7 5700U)"""
    # MemAvailable thresholds (GB)
    min_reserve_gb: float = 2.0      # Hard floor: deny if below
    throttle_gb: float = 4.0         # Throttle if below
    
    # PSI thresholds (fractions)
    psi_full_critical: float = 0.05   # 5% full stall = thrashing
    psi_some_warning: float = 0.10    # 10% some stall = throttle
    psi_some_healthy: float = 0.05    # 5% some stall = healthy
    
    # cgroup thresholds (fractions)
    cgroup_some_warning: float = 0.15  # 15% cgroup some stall = throttle
    cgroup_full_critical: float = 0.05 # 5% cgroup full stall = deny
    
    # Model memory profile
    model_ram_gb: float = 1.7
    kv_cache_gb_per_8k: float = 0.5
    reserve_gb: float = 1.0


class OOMProtector:
    """
    Three-signal fusion admission controller.
    
    Decision logic (priority order):
    1. MemAvailable < min_reserve_gb → DENY_OOM_RISK (hard floor)
    2. PSI full.avg10 > 5% → DENY_THRASHING (system frozen)
    3. cgroup full.avg10 > 5% → DENY_THRASHING (container frozen)
    4. PSI some.avg60 > 10% → THROTTLE (sustained pressure)
    5. cgroup some.avg60 > 15% → THROTTLE (container pressure)
    6. MemAvailable < 4GB → THROTTLE (low headroom)
    7. Otherwise → ALLOW
    """
    
    def __init__(
        self,
        config: Optional[OOMProtectorConfig] = None,
        psi_poll_interval: float = 1.0,
        cgroup_path: str = "/sys/fs/cgroup",
    ):
        self.config = config or OOMProtectorConfig()
        self.psi = PSIMonitor(poll_interval=psi_poll_interval)
        self.memavailable = MemAvailableReader()
        self.cgroup = CgroupPressureMonitor(cgroup_path)
        self._cgroup_available = cgroup_pressure_available(cgroup_path)
    
    async def check(self) -> AdmissionResult:
        """
        Three-signal fusion check.
        
        Returns admission decision based on current pressure snapshot.
        """
        snapshot = await self._take_snapshot()
        return self._fuse_signals(snapshot)
    
    async def check_available(self, required_gb: float) -> bool:
        """
        Check if required memory is available with safety margin.
        
        Args:
            required_gb: Memory needed for new allocation (model + KV cache)
            
        Returns:
            True if MemAvailable >= required + reserve
        """
        available = await self.memavailable.get_memavailable_gb()
        reserve = self.config.reserve_gb
        return available >= required_gb + reserve
    
    async def get_snapshot(self) -> PressureSnapshot:
        """Get current pressure snapshot (for monitoring/debugging)"""
        return await self._take_snapshot()
    
    async def _take_snapshot(self) -> PressureSnapshot:
        """Capture all three signals concurrently using mutable container pattern"""
        results: dict = {}

        async def read_psi():
            results["psi"] = await self.psi.get_all_metrics()

        async def read_memavailable():
            results["mem"] = await self.memavailable.get_memavailable_gb()

        async def read_cgroup():
            if not self._cgroup_available:
                results["cgroup"] = None
                return
            try:
                results["cgroup"] = await self.cgroup._read_pressure()
            except (FileNotFoundError, PermissionError, OSError):
                results["cgroup"] = None

        # Run all three reads concurrently
        async with anyio.create_task_group() as tg:
            tg.start_soon(read_psi)
            tg.start_soon(read_memavailable)
            tg.start_soon(read_cgroup)

        psi_metrics = results.get("psi")
        memavailable_gb = results.get("mem", 0.0)
        cgroup_snapshot = results.get("cgroup")
        
        # Build snapshot — include cgroup data if available
        snapshot = PressureSnapshot(
            psi_some_avg10=psi_metrics.some_avg10 / 100.0,
            psi_some_avg60=psi_metrics.some_avg60 / 100.0,
            psi_some_avg300=psi_metrics.some_avg300 / 100.0,
            psi_full_avg10=psi_metrics.full_avg10 / 100.0,
            psi_full_avg60=psi_metrics.full_avg60 / 100.0,
            psi_full_avg300=psi_metrics.full_avg300 / 100.0,
            memavailable_gb=memavailable_gb,
            cgroup_some_avg60=(cgroup_snapshot.some_avg60 / 100.0) if cgroup_snapshot else None,
            cgroup_full_avg10=(cgroup_snapshot.full_avg10 / 100.0) if cgroup_snapshot else None,
            cgroup_pressure_level=cgroup_snapshot.pressure_level if cgroup_snapshot else None,
            cgroup_available=(cgroup_snapshot is not None),
        )
        
        return snapshot
    
    def _fuse_signals(self, snapshot: PressureSnapshot) -> AdmissionResult:
        """
        Fuse three signals into admission decision.
        
        Priority order (highest first):
        1. Hard OOM risk (MemAvailable below reserve)
        2. System thrashing (PSI full stall)
        3. Container thrashing (cgroup full stall)
        4. Sustained pressure (PSI some stall)
        5. Container pressure (cgroup some stall)
        6. Low headroom (MemAvailable 2-4GB)
        7. All clear
        """
        cfg = self.config
        
        # 1. HARD FLOOR: MemAvailable below absolute reserve
        if snapshot.memavailable_gb < cfg.min_reserve_gb:
            return AdmissionResult.DENY_OOM_RISK
        
        # 2. SYSTEM THRASHING: PSI full stall > 5%
        if snapshot.psi_full_avg10 > cfg.psi_full_critical:
            return AdmissionResult.DENY_THRASHING
        
        # 3. CONTAINER THRASHING: cgroup full stall > 5%
        if (snapshot.cgroup_available and 
            snapshot.cgroup_full_avg10 is not None and
            snapshot.cgroup_full_avg10 > cfg.cgroup_full_critical):
            return AdmissionResult.DENY_THRASHING
        
        # 4. SUSTAINED PRESSURE: PSI some stall > 10%
        if snapshot.psi_some_avg60 > cfg.psi_some_warning:
            return AdmissionResult.THROTTLE
        
        # 5. CONTAINER PRESSURE: cgroup some stall > 15%
        if (snapshot.cgroup_available and
            snapshot.cgroup_some_avg60 is not None and
            snapshot.cgroup_some_avg60 > cfg.cgroup_some_warning):
            return AdmissionResult.THROTTLE
        
        # 6. LOW HEADROOM: MemAvailable 2-4GB
        if snapshot.memavailable_gb < cfg.throttle_gb:
            return AdmissionResult.THROTTLE
        
        # 7. ALL CLEAR
        return AdmissionResult.ALLOW
    
    def get_decision_reason(self, result: AdmissionResult, snapshot: PressureSnapshot) -> str:
        """Human-readable reason for decision"""
        cfg = self.config
        
        if result == AdmissionResult.DENY_OOM_RISK:
            return f"MemAvailable {snapshot.memavailable_gb:.2f}GB < reserve {cfg.min_reserve_gb}GB"
        elif result == AdmissionResult.DENY_THRASHING:
            if snapshot.psi_full_avg10 > cfg.psi_full_critical:
                return f"PSI full.avg10 {snapshot.psi_full_avg10:.1%} > {cfg.psi_full_critical:.0%}"
            elif snapshot.cgroup_full_avg10 and snapshot.cgroup_full_avg10 > cfg.cgroup_full_critical:
                return f"cgroup full.avg10 {snapshot.cgroup_full_avg10:.1%} > {cfg.cgroup_full_critical:.0%}"
            return "Thrashing detected"
        elif result == AdmissionResult.THROTTLE:
            reasons = []
            if snapshot.psi_some_avg60 > cfg.psi_some_warning:
                reasons.append(f"PSI some.avg60 {snapshot.psi_some_avg60:.1%}")
            if snapshot.cgroup_some_avg60 and snapshot.cgroup_some_avg60 > cfg.cgroup_some_warning:
                reasons.append(f"cgroup some.avg60 {snapshot.cgroup_some_avg60:.1%}")
            if snapshot.memavailable_gb < cfg.throttle_gb:
                reasons.append(f"MemAvailable {snapshot.memavailable_gb:.2f}GB < {cfg.throttle_gb}GB")
            return "Throttle: " + "; ".join(reasons)
        else:
            return "All signals healthy"


# Convenience functions

async def create_oom_protector(
    min_reserve_gb: float = 2.0,
    throttle_gb: float = 4.0,
    cgroup_path: str = "/sys/fs/cgroup",
) -> OOMProtector:
    """Create OOMProtector with custom thresholds"""
    config = OOMProtectorConfig(
        min_reserve_gb=min_reserve_gb,
        throttle_gb=throttle_gb,
    )
    return OOMProtector(config=config, cgroup_path=cgroup_path)


async def quick_check() -> AdmissionResult:
    """One-shot admission check with defaults"""
    protector = await create_oom_protector()
    return await protector.check()


async def quick_check_available(required_gb: float) -> bool:
    """One-shot memory availability check"""
    protector = await create_oom_protector()
    return await protector.check_available(required_gb)


# Synchronous quick checks

def quick_check_sync() -> AdmissionResult:
    """Synchronous one-shot check (uses sync readers)"""
    from .psi_monitor import PSIMonitor
    from .memavailable import get_memavailable_gb_sync
    from .cgroup_pressure import read_cgroup_pressure_sync, cgroup_pressure_available
    
    cfg = OOMProtectorConfig()
    
    # PSI
    psi = PSIMonitor()
    psi_some_avg60 = 0.0
    psi_full_avg10 = 0.0
    try:
        psi_some_avg60 = anyio.run(psi.get_pressure("some", "avg60"))
        psi_full_avg10 = anyio.run(psi.get_pressure("full", "avg10"))
    except Exception:
        pass
    
    # MemAvailable
    memavailable_gb = get_memavailable_gb_sync()
    
    # cgroup
    cgroup_some_avg60 = None
    cgroup_full_avg10 = None
    if cgroup_pressure_available():
        cgroup_some_avg60 = read_cgroup_pressure_sync(stall_type="some", window="avg60")
        cgroup_full_avg10 = read_cgroup_pressure_sync(stall_type="full", window="avg10")
    
    # Fuse
    if memavailable_gb < cfg.min_reserve_gb:
        return AdmissionResult.DENY_OOM_RISK
    if psi_full_avg10 > cfg.psi_full_critical:
        return AdmissionResult.DENY_THRASHING
    if cgroup_full_avg10 and cgroup_full_avg10 > cfg.cgroup_full_critical:
        return AdmissionResult.DENY_THRASHING
    if psi_some_avg60 > cfg.psi_some_warning:
        return AdmissionResult.THROTTLE
    if cgroup_some_avg60 and cgroup_some_avg60 > cfg.cgroup_some_warning:
        return AdmissionResult.THROTTLE
    if memavailable_gb < cfg.throttle_gb:
        return AdmissionResult.THROTTLE
    
    return AdmissionResult.ALLOW


def quick_check_available_sync(required_gb: float) -> bool:
    """Synchronous memory availability check"""
    from .memavailable import get_memavailable_gb_sync
    available = get_memavailable_gb_sync()
    return available >= required_gb + 1.0  # reserve


# Health check for monitoring

async def get_health_status() -> dict:
    """Get detailed health status for monitoring endpoints"""
    protector = await create_oom_protector()
    snapshot = await protector.get_snapshot()
    decision = await protector.check()
    reason = protector.get_decision_reason(decision, snapshot)
    
    return {
        "decision": decision.value,
        "reason": reason,
        "signals": {
            "psi": {
                "some_avg10": f"{snapshot.psi_some_avg10:.2%}",
                "some_avg60": f"{snapshot.psi_some_avg60:.2%}",
                "some_avg300": f"{snapshot.psi_some_avg300:.2%}",
                "full_avg10": f"{snapshot.psi_full_avg10:.2%}",
                "full_avg60": f"{snapshot.psi_full_avg60:.2%}",
                "full_avg300": f"{snapshot.psi_full_avg300:.2%}",
            },
            "memavailable_gb": round(snapshot.memavailable_gb, 2),
            "cgroup": {
                "available": snapshot.cgroup_available,
                "some_avg60": f"{snapshot.cgroup_some_avg60:.2%}" if snapshot.cgroup_some_avg60 else None,
                "full_avg10": f"{snapshot.cgroup_full_avg10:.2%}" if snapshot.cgroup_full_avg10 else None,
                "pressure_level": snapshot.cgroup_pressure_level,
            } if snapshot.cgroup_available else None,
        },
        "thresholds": {
            "min_reserve_gb": protector.config.min_reserve_gb,
            "throttle_gb": protector.config.throttle_gb,
            "psi_full_critical": f"{protector.config.psi_full_critical:.0%}",
            "psi_some_warning": f"{protector.config.psi_some_warning:.0%}",
            "cgroup_some_warning": f"{protector.config.cgroup_some_warning:.0%}",
            "cgroup_full_critical": f"{protector.config.cgroup_full_critical:.0%}",
        },
    }