# ── Hardware Monitor ──
# ⬡ OMEGA ⬡ Sovereign Hardware Telemetry
# 
# Captures per-core CPU utilization, memory pressure, thread contention,
# and thermal/throttling data. Designed to be always-available to agents
# via MCP tools and CLI commands.
#
# Zero external deps beyond psutil (stdlib for procfs fallback).
# 
# Hardware floor: AMD Ryzen 7 5700U (Zen 2, 8C/16T, 14Gi RAM)
# [id-soft: quake-1996] Surface Cache — understand the physical fetch path
#   before optimizing the logical algorithm.
# [id-soft: doom3-2004] idHeap — know your memory topology before allocating.

from __future__ import annotations

import os
import time
import json
import struct
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Always-available fallback when psutil not installed
_PSUTIL_AVAILABLE = False
try:
    import psutil as _psutil
    _PSUTIL_AVAILABLE = True
except ImportError:
    _psutil = None  # type: ignore


# ── CPU Topology ────────────────────────────────────────────────────────────
# Ryzen 7 5700U:
#   - 8 physical cores, 16 SMT threads
#   - L1: 64KB/core (32KB data + 32KB instruction)
#   - L2: 512KB/core
#   - L3: 8MB victim cache (2 instances × 4MB, NOT inclusive)
#   - CCX0: cores 0-3 (L3: 4MB), CCX1: cores 4-7 (L3: 4MB)
#   - TDP: 15W (thermal throttling is primary constraint)


def _read_proc(path: str) -> str:
    """Read a /proc file, returning empty string on error."""
    try:
        with open(path) as f:
            return f.read()
    except (FileNotFoundError, PermissionError, OSError):
        return ""


def _parse_cpu_line(line: str) -> Dict[str, int]:
    """Parse a single /proc/stat CPU line into named fields."""
    parts = line.split()
    if len(parts) < 5:
        return {}
    return {
        "user": int(parts[1]),
        "nice": int(parts[2]),
        "system": int(parts[3]),
        "idle": int(parts[4]),
        "iowait": int(parts[5]) if len(parts) > 5 else 0,
        "irq": int(parts[6]) if len(parts) > 6 else 0,
        "softirq": int(parts[7]) if len(parts) > 7 else 0,
        "steal": int(parts[8]) if len(parts) > 8 else 0,
        "guest": int(parts[9]) if len(parts) > 9 else 0,
        "guest_nice": int(parts[10]) if len(parts) > 10 else 0,
    }


def _cpu_total(jiffies: Dict[str, int]) -> int:
    """Sum all jiffies from a parsed CPU line."""
    return sum(jiffies.values())


class CpuSnapshot:
    """Point-in-time CPU utilization snapshot.
    
    Stores /proc/stat jiffies for delta calculation.
    Lightweight — no psutil required.
    """
    def __init__(self, jiffies_per_core: Dict[str, Dict[str, int]]):
        self.jiffies_per_core = jiffies_per_core
        self.timestamp = time.monotonic()

    @classmethod
    def capture(cls) -> "CpuSnapshot":
        """Capture current CPU jiffies from /proc/stat."""
        data = _read_proc("/proc/stat")
        cores: Dict[str, Dict[str, int]] = {}
        for line in data.splitlines():
            if line.startswith("cpu"):
                name = line.split()[0]
                parsed = _parse_cpu_line(line)
                if parsed:
                    cores[name] = parsed
        return cls(cores)

    def utilization_vs(self, other: "CpuSnapshot", core: str = "cpu") -> float:
        """Calculate CPU utilization percentage between two snapshots."""
        if core not in self.jiffies_per_core or core not in other.jiffies_per_core:
            return 0.0
        delta = {}
        for key in self.jiffies_per_core[core]:
            delta[key] = self.jiffies_per_core[core][key] - other.jiffies_per_core[core].get(key, 0)
        total = _cpu_total(delta)
        if total == 0:
            return 0.0
        idle = delta.get("idle", 0) + delta.get("iowait", 0)
        return (1.0 - idle / total) * 100.0

    def per_core_utilization(self, other: "CpuSnapshot") -> Dict[str, float]:
        """Get utilization for every CPU core between two snapshots."""
        result: Dict[str, float] = {}
        for core_name in self.jiffies_per_core:
            if core_name.startswith("cpu") and core_name != "cpu":
                result[core_name] = self.utilization_vs(other, core_name)
        return result


class HardwareMonitor:
    """Always-available hardware telemetry.
    
    Captures per-core CPU, memory pressure, thread contention, and OOM risk.
    Designed for zero-dependency operation — falls back to /proc when psutil
    is unavailable.
    
    Usage:
        hm = HardwareMonitor()
        report = hm.collect_all()  # single snapshot
        # Or for profiling benchmarks:
        before = hm.collect_all()
        ... do work ...
        after = hm.collect_all()
        delta = hm.diff(before, after)
    """

    def __init__(self):
        self._initial_collect = self.collect_all()

    # ── CPU ────────────────────────────────────────────────────────────────

    def get_cpu_topology(self) -> Dict:
        """Get CPU topology: cores, threads, L3 layout."""
        data = _read_proc("/proc/cpuinfo")
        phys_cores = set()
        siblings: Dict[int, List[int]] = {}
        current_proc = None
        
        for line in data.splitlines():
            if line.startswith("processor"):
                current_proc = int(line.split(":")[1].strip())
            elif line.startswith("core id") and current_proc is not None:
                core = int(line.split(":")[1].strip())
                phys_cores.add(core)
            elif line.startswith("cpu cores") and current_proc is not None:
                pass  # total = int(line.split(":")[1].strip())
            elif line.startswith("siblings") and current_proc is not None:
                pass  # sib = int(line.split(":")[1].strip())

        # Parse core siblings from topology
        topo = _read_proc("/sys/devices/system/cpu/cpu*/topology/core_siblings_list")
        # Use lscpu-style parsing
        total_cores = 8  # Ryzen 7 5700U fixed
        total_threads = 16

        # Parse L3 layout
        l3_indices = set()
        try:
            for cpu_dir in Path("/sys/devices/system/cpu").glob("cpu[0-9]*"):
                idx = int(cpu_dir.name[3:])
                l3_path = cpu_dir / "cache" / "index3" / "shared_cpu_list"
                if l3_path.exists():
                    l3_indices.add(l3_path.read_text().strip())
        except Exception:
            pass

        return {
            "model": "AMD Ryzen 7 5700U (Zen 2)",
            "physical_cores": total_cores,
            "logical_threads": total_threads,
            "smt_enabled": total_threads > total_cores,
            "l3_cache_mb": 8,
            "l3_instances": len(l3_indices) if l3_indices else 2,
            "l3_per_instance_mb": 8 // max(len(l3_indices), 1) if l3_indices else 4,
            "l3_is_victim_cache": True,
            "l3_shared_groups": sorted(l3_indices) if l3_indices else ["0-3", "8-11"],
            "ccx0_cores": [0, 1, 2, 3],
            "ccx1_cores": [4, 5, 6, 7],
        }

    def get_per_core_utilization(self, interval: float = 0.5) -> Dict[str, float]:
        """Get per-CPU utilization % over an interval."""
        if _PSUTIL_AVAILABLE and _psutil is not None:
            # psutil gives per-CPU percent directly
            per_cpu = _psutil.cpu_percent(interval=interval, percpu=True)
            return {f"cpu{i}": pct for i, pct in enumerate(per_cpu)}
        else:
            # /proc/stat delta approach
            before = CpuSnapshot.capture()
            time.sleep(interval)
            after = CpuSnapshot.capture()
            return after.per_core_utilization(before)

    def get_load_avg(self) -> Dict:
        """Get load averages and process counts."""
        data = _read_proc("/proc/loadavg")
        parts = data.strip().split()
        if len(parts) >= 4:
            proc_parts = parts[3].split("/")
            return {
                "load_1min": float(parts[0]),
                "load_5min": float(parts[1]),
                "load_15min": float(parts[2]),
                "running": int(proc_parts[0]),
                "total_processes": int(proc_parts[1]),
                "last_pid": int(parts[4]) if len(parts) > 4 else 0,
            }
        return {}

    def get_context_switches(self) -> Dict:
        """Get voluntary and involuntary context switch rates."""
        data = _read_proc("/proc/stat")
        result = {"voluntary": 0, "involuntary": 0}
        for line in data.splitlines():
            if line.startswith("ctxt "):
                result["total_ctxt"] = int(line.split()[1])
            elif line.startswith("processes "):
                result["processes"] = int(line.split()[1])
            elif line.startswith("procs_running "):
                result["procs_running"] = int(line.split()[1])
            elif line.startswith("procs_blocked "):
                result["procs_blocked"] = int(line.split()[1])
        return result

    def get_process_thread_count(self, pid: Optional[int] = None) -> Dict:
        """Count threads for a specific PID or all Python processes."""
        if pid is not None:
            try:
                proc = _psutil.Process(pid) if _PSUTIL_AVAILABLE else None
                if proc:
                    return {"pid": pid, "name": proc.name(), "threads": proc.num_threads()}
            except Exception:
                pass
            # Fallback to /proc
            data = _read_proc(f"/proc/{pid}/status")
            for line in data.splitlines():
                if line.startswith("Threads:"):
                    return {"pid": pid, "threads": int(line.split()[1])}
            return {"pid": pid, "threads": 0}

        # Count all python process threads
        if _PSUTIL_AVAILABLE:
            py_procs = []
            total_threads = 0
            for proc in _psutil.process_iter(["pid", "name", "num_threads"]):
                name = proc.info.get("name", "")
                if "python" in name.lower():
                    t = proc.info.get("num_threads", 0)
                    total_threads += t
                    py_procs.append({
                        "pid": proc.info["pid"],
                        "name": name,
                        "threads": t,
                    })
            return {"total_python_threads": total_threads, "processes": py_procs}
        return {"total_python_threads": 0, "processes": []}

    # ── Memory ──────────────────────────────────────────────────────────────

    def get_memory_status(self) -> Dict:
        """Get detailed memory status with pressure analysis."""
        if _PSUTIL_AVAILABLE:
            vm = _psutil.virtual_memory()
            swap = _psutil.swap_memory()
            result = {
                "total_mb": round(vm.total / 1048576, 1),
                "available_mb": round(vm.available / 1048576, 1),
                "used_mb": round(vm.used / 1048576, 1),
                "percent": vm.percent,
                "swap_total_mb": round(swap.total / 1048576, 1),
                "swap_used_mb": round(swap.used / 1048576, 1),
                "swap_percent": swap.percent,
            }
        else:
            data = _read_proc("/proc/meminfo")
            mem = {}
            for line in data.splitlines():
                k, v = line.split(":", 1)
                mem[k.strip()] = int(v.strip().split()[0]) // 1024
            result = {
                "total_mb": mem.get("MemTotal", 0),
                "available_mb": mem.get("MemAvailable", 0),
                "used_mb": mem.get("MemTotal", 0) - mem.get("MemAvailable", 0),
                "percent": round((1 - mem.get("MemAvailable", 0) / max(mem.get("MemTotal", 1), 1)) * 100, 1),
                "swap_total_mb": mem.get("SwapTotal", 0),
                "swap_used_mb": mem.get("SwapTotal", 0) - mem.get("SwapFree", 0),
                "swap_percent": round((mem.get("SwapTotal", 0) - mem.get("SwapFree", 0)) / max(mem.get("SwapTotal", 1), 1) * 100, 1) if mem.get("SwapTotal", 0) > 0 else 0,
            }

        # OOM risk assessment
        avail_mb = result.get("available_mb", 0)
        model_gb = 1.7  # Qwen3-1.7B approximate at Q6_K
        kv_overhead_gb = 0.5  # ~512MB for 4K context at q8_0/f16
        system_overhead = 1.0  # ~1GB for OS + services
        
        total_needed_for_inference = model_gb + kv_overhead_gb + system_overhead
        oom_risk_mb = total_needed_for_inference * 1024 - avail_mb

        # oom_risk_mb = needed - available. Positive = deficit (bad), negative = surplus (good)
        if oom_risk_mb > 1024:
            risk = "CRITICAL"
        elif oom_risk_mb > 512:
            risk = "HIGH"
        elif oom_risk_mb > 0:
            risk = "MODERATE"
        elif oom_risk_mb > -1024:
            risk = "LOW"
        else:
            risk = "SAFE"

        result["oom_risk"] = {
            "model_gb": model_gb,
            "kv_overhead_gb": kv_overhead_gb,
            "system_reserve_gb": system_overhead,
            "total_needed_gb": round(total_needed_for_inference, 1),
            "surplus_deficit_mb": round(-oom_risk_mb),  # positive = surplus
            "risk_level": risk,
            "deficit_mb": round(max(0, oom_risk_mb)),   # positive = how much more we need
        }
        return result

    def get_memory_pressure(self) -> float:
        """Return a memory pressure score 0.0 (safe) - 1.0 (critical)."""
        mem = self.get_memory_status()
        avail_mb = mem.get("available_mb", 0)
        total_mb = mem.get("total_mb", 1)
        swap_pct = mem.get("swap_percent", 0)
        
        # Available memory pressure (lower is worse)
        avail_pressure = max(0, 1.0 - avail_mb / (total_mb * 0.3))
        # Swap pressure
        swap_pressure = min(1.0, swap_pct / 50.0)
        
        return round(min(1.0, avail_pressure * 0.7 + swap_pressure * 0.3), 3)

    def get_oom_risk_level(self) -> str:
        """Quick OOM risk check: SAFE, LOW, MODERATE, HIGH, CRITICAL."""
        return self.get_memory_status()["oom_risk"]["risk_level"]

    # ── Thermal ─────────────────────────────────────────────────────────────

    def get_temperatures(self) -> Dict:
        """Get CPU temperature from thermal zone or k10temp."""
        result = {"available": False, "celsius": []}
        # Try k10temp (AMD) first
        k10_path = Path("/sys/class/hwmon")
        try:
            for hwmon in k10_path.iterdir():
                name_path = hwmon / "name"
                if name_path.exists() and "k10temp" in name_path.read_text():
                    for temp_input in hwmon.glob("temp*_input"):
                        idx = temp_input.name.replace("temp", "").replace("_input", "")
                        label_path = hwmon / f"temp{idx}_label"
                        label = label_path.read_text().strip() if label_path.exists() else f"T{idx}"
                        try:
                            temp = int(temp_input.read_text()) / 1000
                            result["celsius"].append({"label": label, "temp": temp})
                        except Exception:
                            pass
                    result["available"] = len(result["celsius"]) > 0
                    break
        except Exception:
            pass
        
        # Fallback to thermal zones
        if not result["available"]:
            try:
                for tz in Path("/sys/class/thermal").glob("thermal_zone*"):
                    try:
                        temp = int(tz.read_text()) / 1000
                        result["celsius"].append({"label": tz.name, "temp": temp})
                    except Exception:
                        pass
                result["available"] = len(result["celsius"]) > 0
            except Exception:
                pass
        
        return result

    def is_thermal_throttling(self) -> bool:
        """Check if CPU is currently thermal throttling."""
        temps = self.get_temperatures()
        if not temps.get("available"):
            return False
        max_temp = max((t["temp"] for t in temps["celsius"]), default=0)
        # Zen 2 Tjmax is ~95°C, throttling starts around 85-90°C
        return max_temp > 85

    # ── Disk I/O ────────────────────────────────────────────────────────────

    def get_disk_io(self) -> Dict:
        """Get disk I/O stats from /proc/diskstats."""
        result: Dict = {}
        data = _read_proc("/proc/diskstats")
        for line in data.splitlines():
            parts = line.strip().split()
            if len(parts) >= 14 and "nvme" in parts[2]:
                dev = parts[2]
                result[dev] = {
                    "reads_completed": int(parts[3]),
                    "reads_merged": int(parts[4]),
                    "sectors_read": int(parts[5]),
                    "read_time_ms": int(parts[6]),
                    "writes_completed": int(parts[7]),
                    "writes_merged": int(parts[8]),
                    "sectors_written": int(parts[9]),
                    "write_time_ms": int(parts[10]),
                    "io_in_progress": int(parts[11]),
                    "io_time_ms": int(parts[12]),
                    "weighted_io_time_ms": int(parts[13]),
                }
        return result

    # ── Comprehensive Collection ────────────────────────────────────────────

    def collect_all(self) -> Dict:
        """Collect a comprehensive snapshot of all hardware stats."""
        cpu = self.get_per_core_utilization(interval=0.2)
        mem = self.get_memory_status()
        temps = self.get_temperatures()
        load = self.get_load_avg()
        topo = self.get_cpu_topology()

        return {
            "timestamp": time.time(),
            "topology": topo,
            "cpu": {
                "per_core_percent": cpu,
                "avg_percent": round(sum(cpu.values()) / max(len(cpu), 1), 1) if cpu else 0,
                "load": load,
                "thermal_throttling": self.is_thermal_throttling(),
            },
            "memory": mem,
            "memory_pressure": self.get_memory_pressure(),
            "oom_risk": mem["oom_risk"]["risk_level"],
            "temperatures": temps,
            "threads": self.get_process_thread_count(),
            "disk_io": self.get_disk_io(),
        }

    @staticmethod
    def diff(before: Dict, after: Dict) -> Dict:
        """Compute diff between two collect_all snapshots for benchmark profiling."""
        return {
            "cpu_utilization_delta": round(
                after.get("cpu", {}).get("avg_percent", 0) - before.get("cpu", {}).get("avg_percent", 0), 1
            ),
            "memory_delta_mb": round(
                after.get("memory", {}).get("used_mb", 0) - before.get("memory", {}).get("used_mb", 0), 1
            ),
            "swap_delta_mb": round(
                after.get("memory", {}).get("swap_used_mb", 0) - before.get("memory", {}).get("swap_used_mb", 0), 1
            ),
            "temperature_delta": round(
                max((t["temp"] for t in after.get("temperatures", {}).get("celsius", [])), default=0)
                - max((t["temp"] for t in before.get("temperatures", {}).get("celsius", [])), default=0), 1
            ),
            "memory_pressure_delta": round(
                after.get("memory_pressure", 0) - before.get("memory_pressure", 0), 3
            ),
        }

    def to_json(self, **kwargs) -> str:
        """Serialize all stats to JSON string."""
        return json.dumps(self.collect_all(), **kwargs)


# ── Simple CLI Entry Point ───────────────────────────────────────────────────

def main_cli():
    """Print hardware stats to stdout (for `omega hardware-stats` or direct use)."""
    import argparse
    parser = argparse.ArgumentParser(description="Omega Hardware Monitor")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--watch", type=float, default=0, help="Continuous monitoring interval (seconds)")
    parser.add_argument("--oom", action="store_true", help="Quick OOM risk check only")
    args = parser.parse_args()

    hm = HardwareMonitor()

    if args.oom:
        status = hm.get_oom_risk_level()
        mem = hm.get_memory_status()
        print(f"OOM Risk: {status}")
        print(f"Memory: {mem['used_mb']}/{mem['total_mb']}MB used ({mem['percent']}%)")
        print(f"Available: {mem['available_mb']}MB")
        print(f"Swap: {mem['swap_used_mb']}/{mem['swap_total_mb']}MB ({mem['swap_percent']}%)")
        return

    if args.watch:
        try:
            while True:
                stats = hm.collect_all()
                if args.json:
                    print(json.dumps(stats))
                else:
                    _print_terminal(stats)
                time.sleep(args.watch)
        except KeyboardInterrupt:
            print("\nStopped.")
        return

    stats = hm.collect_all()
    if args.json:
        print(json.dumps(stats, indent=2))
    else:
        _print_terminal(stats)


def _print_terminal(stats: Dict):
    """Pretty-print hardware stats to terminal."""
    cpu = stats.get("cpu", {})
    mem = stats.get("memory", {})
    temps = stats.get("temperatures", {})
    topo = stats.get("topology", {})

    print("=" * 60)
    print("  OMEGA HARDWARE MONITOR")
    print("=" * 60)

    print(f"\n📦 Topology: {topo.get('physical_cores', '?')}C/{topo.get('logical_threads', '?')}T")
    print(f"   L3: {topo.get('l3_cache_mb', '?')}MB ({topo.get('l3_instances', '?')} instances × {topo.get('l3_per_instance_mb', '?')}MB)")

    print(f"\n🔥 CPU: {cpu.get('avg_percent', 0):.1f}% avg")
    per_core = cpu.get("per_core_percent", {})
    for i in range(0, 16, 4):
        row = "  "
        for j in range(i, min(i + 4, 16)):
            key = f"cpu{j}"
            val = per_core.get(key, 0)
            bar = "█" * int(val / 10) + "░" * (10 - int(val / 10))
            row += f"CPU{j}: {val:5.1f}% {bar}  "
        print(row)

    load = cpu.get("load", {})
    print(f"   Load: {load.get('load_1min', 0):.2f} / {load.get('load_5min', 0):.2f} / {load.get('load_15min', 0):.2f}")
    
    if cpu.get("thermal_throttling"):
        print("   ⚠️  THERMAL THROTTLING ACTIVE")

    if temps.get("available"):
        temp_str = " | ".join(f"{t['label']}: {t['temp']:.0f}°C" for t in temps["celsius"])
        print(f"   Temp: {temp_str}")

    print(f"\n🧠 Memory: {mem.get('used_mb', 0):.0f}/{mem.get('total_mb', 0):.0f}MB ({mem.get('percent', 0):.1f}%)")
    print(f"   Available: {mem.get('available_mb', 0):.0f}MB")
    print(f"   Swap: {mem.get('swap_used_mb', 0):.0f}/{mem.get('swap_total_mb', 0):.0f}MB ({mem.get('swap_percent', 0):.1f}%)")
    print(f"   OOM Risk: {stats.get('oom_risk', 'UNKNOWN')}")
    print(f"   Memory Pressure: {stats.get('memory_pressure', 0):.3f}")

    print(f"\n🧵 Threads: Python processes total threads: {stats.get('threads', {}).get('total_python_threads', 0)}")

    print("=" * 60)


if __name__ == "__main__":
    main_cli()
