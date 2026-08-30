"""Omega Stats MCP Server — Ryzen 5700U system monitoring.

AP Token: AP-OMEGA-STATS-MCP-v1.1.0
ICS: [NODE: MAAT | ARCHETYPE: APOLLO | MODEL: DEEPSEEK-V4-FLASH | CONTEXT: STATS-MCP]

Monitors zRAM, CPU, disk, Vulkan iGPU, and Podman containers.
Now includes aggregated Omega Engine metrics (Inference, Research, Memory, and Errors).
Optimized for AMD Ryzen 7 5700U (Zen 2, 8C/16T, AVX2).

Usage:
    cd ~/omega && python mcp/omega-stats/server.py
"""

import json
import os
from datetime import datetime
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Omega Stats")

# Path to the shared metrics file produced by the Core Hub and Research MCP
METRICS_FILE = Path("data/logs/metrics.json")

@mcp.tool()
def get_system_stats() -> str:
    """Get comprehensive system stats: zRAM, CPU, disk, GPU, memory."""
    stats = {
        "timestamp": datetime.now().isoformat(),
        "cpu": {"available": False},
        "memory": {"available": False},
        "zram": {"available": False},
        "disk": {"available": False},
        "gpu": {"available": False},
        "podman": {"available": False},
        "ryzen_tuning": {"available": False},
    }

    # CPU
    try:
        with open("/proc/loadavg") as f:
            parts = f.read().strip().split()
            stats["cpu"] = {
                "available": True,
                "load_1min": float(parts[0]),
                "load_5min": float(parts[1]),
                "load_15min": float(parts[2]),
                "running_processes": int(parts[3].split("/")[0]),
                "total_processes": int(parts[3].split("/")[1]),
            }
    except Exception:
        pass

    # Memory
    try:
        with open("/proc/meminfo") as f:
            mem = {}
            for line in f:
                k, v = line.split(":", 1)
                mem[k.strip()] = int(v.strip().split()[0]) // 1024
            stats["memory"] = {
                "available": True,
                "total_mb": mem.get("MemTotal", 0),
                "free_mb": mem.get("MemFree", 0),
                "available_mb": mem.get("MemAvailable", 0),
                "used_mb": mem.get("MemTotal", 0) - mem.get("MemAvailable", 0),
            }
    except Exception:
        pass

    # zRAM
    zram_path = Path("/sys/block/zram0/mm_stat")
    if zram_path.exists():
        try:
            with open(zram_path) as f:
                mm = f.read().strip().split()
            stats["zram"] = {
                "available": True,
                "orig_data_mb": round(int(mm[0]) / 1048576, 1),
                "compressed_mb": round(int(mm[1]) / 1048576, 1),
                "mem_used_mb": round(int(mm[2]) / 1048576, 1),
                "ratio": round(int(mm[0]) / max(int(mm[1]), 1), 2),
            }
        except Exception:
            pass

    # Disk — omega_library partition
    try:
        statvfs = os.statvfs("/media/arcana-novai/omega_library")
        total = statvfs.f_frsize * statvfs.f_blocks // (1024**3)
        free = statvfs.f_frsize * statvfs.f_bfree // (1024**3)
        stats["disk"] = {
            "available": True,
            "mount": "/media/arcana-novai/omega_library",
            "total_gb": total,
            "free_gb": free,
            "used_gb": total - free,
            "used_pct": round((total - free) / total * 100, 1) if total > 0 else 0,
        }
    except Exception:
        pass

    # Vulkan iGPU
    gpu_path = Path("/sys/class/drm/card1/device/gpu_busy_percent")
    if gpu_path.exists():
        try:
            with open(gpu_path) as f:
                stats["gpu"] = {
                    "available": True,
                    "utilization_pct": int(f.read().strip()),
                }
        except Exception:
            pass

    # Podman
    try:
        result = os.popen("podman ps --format json 2>/dev/null").read()
        if result:
            containers = json.loads(result)
            stats["podman"] = {
                "available": True,
                "running": sum(1 for c in containers if c.get("State") == "running"),
                "total": len(containers),
                "names": [c.get("Names", [""])[0] for c in containers],
            }
    except Exception:
        pass

    # Ryzen tuning check
    try:
        with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor") as f:
            governor = f.read().strip()
        stats["ryzen_tuning"] = {
            "available": True,
            "governor": governor,
        }
    except Exception:
        pass

    return json.dumps(stats, indent=2)


@mcp.tool()
def get_omega_metrics() -> str:
    """Get aggregated Omega Engine metrics (Inference, Research, Memory, and Errors)."""
    if not METRICS_FILE.exists():
        return json.dumps({"error": "Metrics file not found. No metrics have been recorded yet."}, indent=2)
    
    try:
        with open(METRICS_FILE, "r") as f:
            metrics = json.load(f)
        return json.dumps(metrics, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to read metrics: {str(e)}"}, indent=2)


@mcp.tool()
def check_models_directory() -> str:
    """Check available GGUF models on omega_library partition."""
    models_dir = Path("/media/arcana-novai/omega_library/models/gguf")
    if not models_dir.exists():
        return json.dumps({"error": "Models directory not found"})
    
    models = []
    for f in sorted(models_dir.glob("*.gguf")):
        size_gb = round(f.stat().st_size / (1024**3), 2)
        models.append({"name": f.name, "size_gb": size_gb})
    
    return json.dumps({
        "path": str(models_dir),
        "total_models": len(models),
        "models": models,
    }, indent=2)


@mcp.tool()
def check_podman_storage() -> str:
    """Check Podman storage usage on omega_library."""
    storage_dir = Path("/media/arcana-novai/omega_library/podman-storage")
    if not storage_dir.exists():
        return json.dumps({"error": "Podman storage directory not found"})
    
    try:
        total_size = sum(f.stat().st_size for f in storage_dir.rglob("*") if f.is_file())
        size_mb = round(total_size / (1024**2), 1)
        return json.dumps({
            "path": str(storage_dir),
            "size_mb": size_mb,
            "exists": True,
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


from omega.mcp_runtime import run_mcp

if __name__ == "__main__":
    run_mcp(mcp)
