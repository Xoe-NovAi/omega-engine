# 🔱 Monitoring — Sovereign Hardware Telemetry
**AP Token**: `AP-MONITORING-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Reference documentation for the Monitoring package — always-available hardware telemetry (per-core CPU, memory pressure, thread contention, thermal, zRAM, disk I/O) for graceful degradation.
**Tags**: monitoring, hardware, telemetry, cpu, memory, thermal, zram, degradation
**Cross-references**: src/omega/monitoring/__init__.py, src/omega/hub.py, src/omega/oracle/resource_guard.py, SOVEREIGN_MANDATES.md

---

## Overview

The `monitoring` package provides **always-available hardware telemetry** for the Omega Engine. It captures per-core CPU utilization, memory pressure, thread contention, thermal/throttling data, zRAM compression statistics, and disk I/O — all with **zero external dependencies** (falls back to `/proc` when `psutil` unavailable).

This telemetry feeds the **ResourceGuard** and **Oracle.talk()** for graceful degradation under system pressure (M13 Temple-Grade).

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Monitoring Package                        │
├─────────────────────────────────────────────────────────────┤
│  __init__.py         │  HardwareMonitor — main class        │
│                      │  CpuSnapshot — delta calculation     │
│                      │  CLI entry point                     │
└─────────────────────────────────────────────────────────────┘
```

**Hardware Floor**: AMD Ryzen 7 5700U (Zen 2, 8C/16T, 14Gi RAM)
- L1: 64KB/core (32KB data + 32KB instruction)
- L2: 512KB/core
- L3: 8MB victim cache (2 instances × 4MB, NOT inclusive)
- CCX0: cores 0-3, CCX1: cores 4-7 (monolithic single-CCX die)
- TDP: 15W (thermal throttling is primary constraint)

---

## HardwareMonitor

### Constructor

```python
HardwareMonitor()
```

Captures initial baseline on instantiation.

### CPU Telemetry

#### `get_cpu_topology() -> Dict`
Returns static CPU topology information.

```python
topology = hm.get_cpu_topology()
# {
#   "model": "AMD Ryzen 7 5700U (Zen 2)",
#   "physical_cores": 8,
#   "logical_threads": 16,
#   "smt_enabled": True,
#   "l3_cache_mb": 8,
#   "l3_instances": 1,           # Monolithic die = single CCX
#   "l3_per_instance_mb": 8,
#   "l3_is_victim_cache": True,
#   "l3_shared_groups": ["0-7"],
#   "ccx0_cores": [0,1,2,3,4,5,6,7],
#   "ccx1_cores": []
# }
```

**Key Insight**: The 5700U is a **monolithic single-CCX die** — all 8 physical cores share one 8MB L3. Previous hardcoded 2-CCX model was factually wrong.

#### `get_per_core_utilization(interval: float = 0.5) -> Dict[str, float]`
Per-CPU utilization % over an interval.

```python
cpu = hm.get_per_core_utilization(interval=0.5)
# {"cpu0": 12.3, "cpu1": 8.7, ..., "cpu15": 5.2}
```

Uses `psutil.cpu_percent(percpu=True)` if available, else `/proc/stat` delta.

#### `get_load_avg() -> Dict`
Load averages and process counts from `/proc/loadavg`.

```python
load = hm.get_load_avg()
# {"load_1min": 1.23, "load_5min": 1.45, "load_15min": 1.38,
#  "running": 3, "total_processes": 247, "last_pid": 12345}
```

#### `get_context_switches() -> Dict`
Voluntary/involuntary context switch rates from `/proc/stat`.

#### `get_process_thread_count(pid: Optional[int] = None) -> Dict`
Thread count for specific PID or all Python processes.

```python
# All Python processes
threads = hm.get_process_thread_count()
# {"total_python_threads": 42, "processes": [{"pid": 123, "name": "python3", "threads": 12}, ...]}

# Specific PID
threads = hm.get_process_thread_count(pid=1234)
# {"pid": 1234, "name": "python3", "threads": 8}
```

---

## Memory Telemetry

#### `get_memory_status() -> Dict`
Comprehensive memory status with **OOM risk assessment**.

```python
mem = hm.get_memory_status()
# {
#   "total_mb": 13952.4,
#   "available_mb": 8234.1,
#   "used_mb": 5718.3,
#   "percent": 41.0,
#   "swap_total_mb": 16384.0,
#   "swap_used_mb": 1024.0,
#   "swap_percent": 6.2,
#   "process_rss_mb": 245.7,
#   "oom_risk": {
#     "model_gb": 1.7,
#     "kv_overhead_gb": 0.5,
#     "system_reserve_gb": 1.0,
#     "total_needed_gb": 3.2,
#     "surplus_deficit_mb": 5012,      # positive = surplus
#     "risk_level": "SAFE",            # SAFE | LOW | MODERATE | HIGH | CRITICAL
#     "deficit_mb": 0                  # positive = how much more needed
#   },
#   "zram": {...}  # See zRAM section
# }
```

**OOM Risk Calculation**:
- Assumes Qwen3-1.7B at Q6_K (~1.7GB)
- KV cache overhead: ~512MB for 4K context
- System reserve: ~1GB
- `risk_level` based on available vs. needed

#### `get_memory_pressure() -> float`
Memory pressure score **0.0 (safe) → 1.0 (critical)**.

```python
pressure = hm.get_memory_pressure()
# 0.12  (low pressure)
```

Formula: `avail_pressure * 0.7 + swap_pressure * 0.3`

#### `get_oom_risk_level() -> str`
Quick OOM risk check: `"SAFE" | "LOW" | "MODERATE" | "HIGH" | "CRITICAL"`

---

## zRAM Monitoring (OBS1)

#### `get_zram_stats() -> Dict`
Reads `/sys/block/zram*` for compression statistics.

```python
zram = hm.get_zram_stats()
# {
#   "available": True,
#   "devices": [
#     {
#       "device": "zram0",
#       "original_bytes": 2147483648,
#       "compressed_bytes": 536870912,
#       "mem_used_bytes": 536870912,
#       "compression_ratio": 4.0,
#       "reads": 12345,
#       "writes": 6789,
#       "read_failures": 0,
#       "write_failures": 0,
#       "disksize_bytes": 2147483648
#     }
#   ],
#   "total_original_mb": 2048.0,
#   "total_compressed_mb": 512.0,
#   "total_reads": 12345,
#   "total_writes": 6789,
#   "total_failures": 0,
#   "overall_compression_ratio": 4.0
# }
```

**Why zRAM matters**: On 5700U with 12GB RAM, zRAM provides 2-3x effective memory capacity through compression — critical for OOM protection.

#### `get_swap_zram_pressure() -> Dict`
Unified swap + zRAM pressure analysis.

```python
szp = hm.get_swap_zram_pressure()
# {
#   "swap_total_mb": 16384.0,
#   "swap_used_mb": 1024.0,
#   "swap_percent": 6.2,
#   "zram_available": True,
#   "zram_compressed_mb": 512.0,
#   "zram_original_mb": 2048.0,
#   "zram_compression_ratio": 4.0,
#   "zram_compression_savings_mb": 1536.0,
#   "effective_swap_total_mb": 18432.0,
#   "effective_swap_used_mb": 1536.0,
#   "effective_swap_percent": 8.3,
#   "pressure_score": 0.083,
#   "pressure_level": "SAFE"
# }
```

**Effective swap** = traditional swap + zRAM original capacity (what it can hold uncompressed).

---

## Thermal Telemetry

#### `get_temperatures() -> Dict`
CPU temperature from `k10temp` (AMD) or thermal zones fallback.

```python
temps = hm.get_temperatures()
# {
#   "available": True,
#   "celsius": [
#     {"label": "Tdie", "temp": 52.0},
#     {"label": "Tctl", "temp": 55.0}
#   ]
# }
```

#### `is_thermal_throttling() -> bool`
Returns `True` if any temperature > 85°C (Zen 2 Tjmax ~95°C, throttling starts ~85-90°C).

---

## Disk I/O

#### `get_disk_io() -> Dict`
NVMe stats from `/proc/diskstats`.

```python
dio = hm.get_disk_io()
# {"nvme0n1": {"reads_completed": 123456, "sectors_read": 987654321, ...}}
```

---

## Comprehensive Collection

#### `collect_all() -> Dict`
Single comprehensive snapshot of all hardware stats.

```python
stats = hm.collect_all()
# {
#   "timestamp": 1727890123.456,
#   "topology": {...},
#   "cpu": {"per_core_percent": {...}, "avg_percent": 12.3, "load": {...}, "thermal_throttling": False},
#   "memory": {...},
#   "memory_pressure": 0.12,
#   "oom_risk": "SAFE",
#   "zram": {...},
#   "swap_zram_pressure": {...},
#   "temperatures": {...},
#   "threads": {"total_python_threads": 42, "processes": [...]},
#   "disk_io": {...}
# }
```

#### `diff(before: Dict, after: Dict) -> Dict`
Compute delta between two snapshots for benchmark profiling.

```python
before = hm.collect_all()
# ... run workload ...
after = hm.collect_all()
delta = hm.diff(before, after)
# {
#   "cpu_utilization_delta": 15.2,
#   "memory_delta_mb": 1024.5,
#   "swap_delta_mb": 512.0,
#   "zram_compressed_delta_mb": 256.0,
#   "temperature_delta": 3.0,
#   "memory_pressure_delta": 0.045
# }
```

#### `to_json(**kwargs) -> str`
Serialize all stats to JSON.

---

## CLI Interface

```bash
# Full stats as JSON
python -m omega.monitoring --json

# Pretty terminal output
python -m omega.monitoring

# Watch mode (continuous)
python -m omega.monitoring --watch 2

# Quick OOM risk check only
python -m omega.monitoring --oom
```

**Terminal Output Example**:
```
============================================================
  OMEGA HARDWARE MONITOR
============================================================

📦 Topology: 8C/16T
   L3: 8MB (1 instances × 8MB)

🔥 CPU: 12.3% avg
  CPU0:  12.3% ████░░░░░░  CPU1:   8.7% ███░░░░░░  ...
   Load: 1.23 / 1.45 / 1.38

🧠 Memory: 5718/13952MB (41.0%)
   Available: 8234MB
   Swap: 1024/16384MB (6.2%)
   OOM Risk: SAFE
   Memory Pressure: 0.120
   zRAM: 512MB compressed / 2048MB original (ratio: 4.0x)
   Swap+zRAM Pressure: SAFE (score: 0.083)

🧵 Threads: Python processes total threads: 42
============================================================
```

---

## Integration: hub.py

The `hub.py` module provides a simplified async interface for the Oracle:

```python
from omega.hub import get_hardware_stats

stats = await get_hardware_stats()
# {"cpu_usage": 12.3, "memory_available_mb": 8234, "memory_total_mb": 13952, "temperature_c": 52.0}
```

**Fallback**: Returns safe defaults on any error (`cpu_usage=0.0`, `memory_available_mb=1024`).

---

## Usage Example

```python
from omega.monitoring import HardwareMonitor
from omega.oracle import ResourceGuard

hm = HardwareMonitor()

# Check if safe to run large model
mem = hm.get_memory_status()
if mem["oom_risk"]["risk_level"] in ("HIGH", "CRITICAL"):
    print("⚠️  Insufficient memory for large model")
    # Route to smaller model or cloud

# Pre/post benchmark profiling
before = hm.collect_all()
result = await run_inference()
after = hm.collect_all()
delta = hm.diff(before, after)
print(f"Memory delta: {delta['memory_delta_mb']:.1f}MB")
print(f"zRAM delta: {delta['zram_compressed_delta_mb']:.1f}MB")

# ResourceGuard integration
guard = ResourceGuard(max_ram_mb=2048)
async with guard:
    # Guard checks memory_pressure before allowing inference
    result = await model_gateway.generate(...)
```

---

## Mandate Compliance

| Mandate | Compliance |
|---------|------------|
| **M1 AnyIO** | Blocking `/proc` reads wrapped in `anyio.to_thread` |
| **M7 Local-First** | All telemetry local; no cloud dependencies |
| **M13 Temple-Grade** | OOM risk assessment enables graceful degradation |
| **M23 Failure Integrity** | Graceful fallback to `/proc` when `psutil` unavailable; safe defaults on error |

---

## Heritage

- [id-soft: vet-038] Surface Cache — understand the physical fetch path before optimizing the logical algorithm
- [id-soft: vet-039] idHeap — know your memory topology before allocating

---

## Testing

```bash
pytest tests/test_hardware_monitor.py -v
```

Key test scenarios:
- CPU topology detection (monolithic vs chiplet)
- Memory pressure calculation
- zRAM stats parsing
- Thermal throttling detection
- Diff calculation
- CLI output formats
- Fallback when psutil unavailable

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ MONITORING-v1.0.0 ⬡ 2026-10-02 ⬡*