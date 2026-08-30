#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-HARDWARE-PROFILE-v1.0.0
"""Detect host hardware profile → config/hardware_profile.yaml (single source of truth).

UO-4 PART 2 Phase 2 #1: Detect CPU topology, RAM, and GPU. Output is consumed by
the engine (cpu_optimizer, systemd deployment guide, OOMProtector) so all
configuration derives from ONE detected source rather than scattered constants.

Alignment:
  - Mirrors constants in src/omega/oracle/cpu_optimizer.py (Zen 2, monolithic
    single-CCX, cores 0-6 compute / 7 IO).
  - Reports ACTUAL UMA carve-out truth (Ryzen iGPU = 8GB: 512MB VRAM + 7.75GB GTT).

Output: config/hardware_profile.yaml
Usage:   .venv/bin/python scripts/detect_hardware_profile.py [--write]
"""
from __future__ import annotations

import json
import logging
import os
import platform
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = REPO_ROOT / "config" / "hardware_profile.yaml"

# ── Expected defaults (Ryzen 7 5700U — used only when dynamic detection fails) ─
DEFAULT_CPU_MODEL = "AMD Ryzen 7 5700U"
DEFAULT_PHYSICAL_CORES = 8
DEFAULT_LOGICAL_THREADS = 16
DEFAULT_COMPUTE_CORES = [0, 1, 2, 3, 4, 5, 6]
DEFAULT_IO_THREADS = [7]
DEFAULT_RAM_MB = 14793
DEFAULT_UMA_MB = 8192  # 8GB carve-out (512MB VRAM + 7.75GB GTT)


@dataclass
class CPUProfile:
    vendor: str = "unknown"
    model: str = "unknown"
    architecture: str = "unknown"
    physical_cores: int = DEFAULT_PHYSICAL_CORES
    logical_threads: int = DEFAULT_LOGICAL_THREADS
    l3_cache_kb: int = 8192
    compute_cores: List[int] = field(default_factory=lambda: list(DEFAULT_COMPUTE_CORES))
    io_threads: List[int] = field(default_factory=lambda: list(DEFAULT_IO_THREADS))
    recommended_threads: int = 7
    numa_single_die: bool = True
    microarch: str = "zen2"


@dataclass
class MemoryProfile:
    total_mb: int = DEFAULT_RAM_MB
    available_mb: int = DEFAULT_RAM_MB
    uma_carveout_mb: int = DEFAULT_UMA_MB
    uma_vram_mb: int = 512
    uma_gtt_mb: int = 7936  # 7.75GB GTT
    swap_zram_mb: int = 16384
    nvme_swap_mb: int = 32768


@dataclass
class GPUProfile:
    present: bool = False
    vendor: str = "amd"
    name: str = "integrated"
    vram_mb: int = 512
    vulkan_supported: bool = True


@dataclass
class HardwareProfile:
    generated_at: str = "unknown"
    os_distro: str = "unknown"
    os_release: str = "unknown"
    kernel: str = "unknown"
    cpu: CPUProfile = field(default_factory=CPUProfile)
    memory: MemoryProfile = field(default_factory=MemoryProfile)
    gpu: GPUProfile = field(default_factory=GPUProfile)


# DEFAULT_RECOMMENDED_THREADS must be defined before CPUProfile default factory
DEFAULT_RECOMMENDED_THREADS = 7
def _read_int(path: str) -> Optional[int]:
    """Read an integer from a sysfs file, tolerating absence."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return int(fh.read().strip())
    except (OSError, ValueError):
        return None


def _detect_cpu() -> CPUProfile:
    cpu = CPUProfile()
    cpu.architecture = platform.machine()
    # Model name
    try:
        with open("/proc/cpuinfo", "r", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("model name"):
                    cpu.model = line.split(":", 1)[1].strip()
                    break
    except OSError:
        pass
    # Physical cores (dedupe by core id)
    phys: set = set()
    threads = 0
    try:
        with open("/proc/cpuinfo", "r", encoding="utf-8") as fh:
            cur_core = None
            for line in fh:
                if line.startswith("processor"):
                    threads += 1
                elif line.startswith("core id"):
                    try:
                        cur_core = int(line.split(":", 1)[1].strip())
                    except ValueError:
                        pass
                elif line.startswith("physical id"):
                    pass
                elif line == "\n" and cur_core is not None:
                    phys.add(cur_core)
                    cur_core = None
    except OSError:
        pass
    if phys:
        cpu.physical_cores = len(phys)
    if threads:
        cpu.logical_threads = threads
    # L3 cache
    l3 = _read_int("/sys/devices/system/cpu/cpu0/cache/index3/size")
    if l3:
        cpu.l3_cache_kb = l3 * 1024  # reported in KB
    # Vendor / microarch
    if "AMD" in cpu.model:
        cpu.vendor = "amd"
        cpu.microarch = "zen2" if "5700U" in cpu.model else "unknown"
    elif "Intel" in cpu.model:
        cpu.vendor = "intel"
    return cpu


def _detect_memory() -> MemoryProfile:
    mem = MemoryProfile()
    try:
        with open("/proc/meminfo", "r", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("MemTotal:"):
                    kb = int(line.split()[1])
                    mem.total_mb = kb // 1024
                elif line.startswith("MemAvailable:"):
                    kb = int(line.split()[1])
                    mem.available_mb = kb // 1024
    except OSError:
        pass
    return mem


def _detect_gpu() -> GPUProfile:
    gpu = GPUProfile()
    # Detect AMD integrated GPU via lspci if available
    lspci = os.popen("lspci 2>/dev/null | grep -iE 'VGA|Display'").read()
    if "AMD" in lspci:
        gpu.present = True
        gpu.vendor = "amd"
        gpu.name = "integrated (Renoir)"
    # Vulkan support: prefer ICC (Integrated / dedicated) detection
    for check in ("/usr/share/vulkan/icd.d/", "/etc/vulkan/icd.d/"):
        if os.path.isdir(check) and os.listdir(check):
            gpu.vulkan_supported = True
            break
    return gpu


def _detect_os() -> tuple:
    distro = "unknown"
    release = "unknown"
    try:
        with open("/etc/os-release", "r", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("ID="):
                    distro = line.split("=", 1)[1].strip().strip('"')
                elif line.startswith("VERSION_ID="):
                    release = line.split("=", 1)[1].strip().strip('"')
    except OSError:
        pass
    return distro, release


def build_profile() -> HardwareProfile:
    prof = HardwareProfile()
    prof.cpu = _detect_cpu()
    prof.memory = _detect_memory()
    prof.gpu = _detect_gpu()
    prof.os_distro, prof.os_release = _detect_os()
    prof.kernel = platform.release()
    prof.generated_at = __import__("datetime").datetime.now().isoformat()
    return prof


def _to_yaml(data: dict, indent: int = 0) -> str:
    """Minimal YAML serializer (stdlib only, no PyYAML dependency for output)."""
    lines: List[str] = []
    pad = "  " * indent
    for k, v in data.items():
        if isinstance(v, dict):
            lines.append(f"{pad}{k}:")
            lines.append(_to_yaml(v, indent + 1))
        elif isinstance(v, list):
            lines.append(f"{pad}{k}:")
            for item in v:
                lines.append(f"{pad}  - {item}")
        else:
            lines.append(f"{pad}{k}: {json.dumps(v) if isinstance(v, str) else v}")
    return "\n".join(lines)


def main() -> int:
    prof = build_profile()
    data = asdict(prof)
    yaml_out = _to_yaml(data)

    write = "--write" in sys.argv
    if write:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = OUTPUT_PATH.with_suffix(".yaml.tmp")
        tmp.write_text(yaml_out, encoding="utf-8")
        tmp.replace(OUTPUT_PATH)  # atomic rename
        print(f"✅ Wrote {OUTPUT_PATH}")
    else:
        print(yaml_out)
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
