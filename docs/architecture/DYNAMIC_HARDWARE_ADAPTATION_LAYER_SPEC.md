<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🔱 OMEGA ENGINE — SPECIFICATION & IMPLEMENTATION MANUAL
## Dynamic Hardware Adaptation Layer (DHAL)

```
schema_version: "1.0.0"
document_type: "specification_manual"
document_id: "SPEC-DHAL-v1.0.0"
title: "Dynamic Hardware Adaptation Layer (DHAL) — Self-Discovering Heterogeneous Runtime"
status: "ACTIVE"
date: "2026-09-06"
author: "roc_racoon"
model: "google/gemini-3.8-flash"
channel: "opencode"
sprint: "PUBLIC-DEBUT-01"
governing_mandates: ["M1", "M2", "M7", "M13", "M14", "M22", "M23"]
```

---

### §1. EXECUTIVE SUMMARY & ARCHITECTURAL INTENT

Omega Engine operates across a heterogeneous multi-node fleet:
1. **Node 0 (HP Reference)**: AMD Ryzen 7 5700U (Zen 2 "Lucienne/Renoir", 8C/16T symmetric monolithic die, DDR4-3200, Radeon Vega 8 iGPU).
2. **Node 1 (ASUS ExpertBook P1 - P1503CVA)**: Intel Core i7-13620H (Raptor Lake-H, 10C/16T asymmetric hybrid [6 P-cores + 4 E-cores], DDR5-5200, Iris Xe 64EU iGPU).

Historically, the engine baked monolithic Zen 2 assumptions directly into core code (`src/omega/oracle/cpu_optimizer.py` hardcoded `ZEN2_COMPUTE_CORES = [0, 1, 2, 3, 4, 5, 6]` and `-march=znver2`), while `src/omega/council/hardware_detector.py` remained an unimplemented stub defaulting to `LOCAL_16GB`.

**The Objective of DHAL**:
Transform Omega Engine into an autonomous, self-discovering, polymorphic hardware runtime that:
- Inspects bare-metal silicon through Linux kernel sysfs/procfs interfaces at boot.
- Decouples hardware state into a node-local, git-ignored Single Source of Truth (`config/hardware_profile.yaml`).
- Dispatches execution to polymorphic architectural strategies (`Zen2Strategy`, `RaptorLakeStrategy`, `GenericFallbackStrategy`).
- Automatically isolates CPU-bound LLM inference (physical P-cores / high-bandwidth vector paths) from background agent tasks (E-cores, I/O threads).
- Automatically scales Council concurrency (`SERIAL_INDEPENDENT`, `BATCH_2`, `BATCH_4`, `BATCH_8`, `PARALLEL`) based on real memory channels and capacity.

---

### §1. EXECUTIVE SUMMARY & ARCHITECTURAL INTENT

Omega Engine operates across a heterogeneous multi-node fleet:
1. **Node 0 (HP Reference)**: AMD Ryzen 7 5700U (Zen 2 "Lucienne/Renoir", 8C/16T symmetric monolithic die, DDR4-3200, Radeon Vega 8 iGPU).
2. **Node 1 (ASUS ExpertBook P1 - P1503CVA)**: Intel Core i7-13620H (Raptor Lake-H, 10C/16T asymmetric hybrid [6 P-cores + 4 E-cores], DDR5-5200, Iris Xe 64EU iGPU).

Historically, the engine baked monolithic Zen 2 assumptions directly into core code (`src/omega/oracle/cpu_optimizer.py` hardcoded `ZEN2_COMPUTE_CORES = [0, 1, 2, 3, 4, 5, 6]` and `-march=znver2`), while `src/omega/council/hardware_detector.py` remained an unimplemented stub defaulting to `LOCAL_16GB`.

**The Objective of DHAL**:
Transform Omega Engine into an autonomous, self-discovering, polymorphic hardware runtime that:
- Inspects bare-metal silicon through Linux kernel sysfs/procfs interfaces at boot.
- Decouples hardware state into a node-local, git-ignored Single Source of Truth (`config/hardware_profile.yaml`).
- Dispatches execution to polymorphic architectural strategies (`Zen2Strategy`, `RaptorLakeStrategy`, `GenericFallbackStrategy`).
- Automatically isolates CPU-bound LLM inference (physical P-cores / high-bandwidth vector paths) from background agent tasks (E-cores, I/O threads).
- Automatically scales Council concurrency (`SERIAL_INDEPENDENT`, `BATCH_2`, `BATCH_4`, `BATCH_8`, `PARALLEL`) based on real memory channels and capacity.

---

### §1.1. Relationship to Archangel Architecture (Agent-Level Hardware Awareness)

**DHAL and Archangel are complementary, not redundant.**

| Layer | DHAL (Dynamic Hardware Adaptation Layer) | Archangel Architecture |
|-------|------------------------------------------|------------------------|
| **Scope** | System-level: compiler flags, core pinning, Council concurrency, ResourceGuard | Agent-level: prompt injection, hallucination prevention, write-tool gating |
| **Trigger** | Boot / hardware change | Every subagent dispatch |
| **Consumer** | `Zen2Optimizer`, `CouncilScheduler`, `ResourceGuard` | `SkepticalVerifier`, `M33Probe`, every subagent |
| **Artifact** | `config/hardware_profile.yaml` (git-ignored) | `[SYSTEM REGISTER: ...]` envelope (ephemeral, per-dispatch) |
| **Mandate** | M2, M7, M13, M14, M22, M23 | M1, M2, M7, M13, M14, M22, M23, M27 |

**DHAL adapts the *engine* to the hardware; Archangel adapts the *agent's mind* to the hardware.**

DHAL provides the authoritative hardware telemetry (`HardwareMonitor.collect_all()`) that Archangel's `SystemEnvelopeInjector` wraps and injects into every agent's context as the `[SYSTEM REGISTER: BARE-METAL PHYSICAL BOUNDARY]` envelope. The M33Probe's dynamic write-tool threshold (`calculate_dynamic_write_threshold()`) consumes the same `HardwareMonitor` metrics (memory pressure, thermal throttling, OOM risk) that DHAL exposes.

See **Archangel Architecture Specification** (`docs/architecture/ARCHANGEL_ARCHITECTURE.md`) for the agent-level injection pipeline, `RuntimeHardwareRegister` schema, and M33Probe integration.

---

### §2. CORE ARCHITECTURAL PRINCIPLES

```
┌────────────────────────────────────────────────────────────────────────┐
│                         LINUX KERNEL SYSFS / PROCFS                    │
│   /sys/devices/cpu_core     /sys/devices/cpu_atom     /proc/cpuinfo    │
│   /sys/class/drm/card0      /sys/class/powercap       /proc/meminfo    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
       [ scripts/detect_hardware_profile.py ] (Bare Metal Detection)
                                    │
                                    ▼
       [ config/hardware_profile.yaml ] (Node-Local SSOT - Git Ignored)
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│  CPU Optimizer   │      │ Council Scheduler│      │  ResourceGuard   │
│ (Strategy Model) │      │  (Concurrency)   │      │  (OOM & Power)   │
├──────────────────┤      ├──────────────────┤      ├──────────────────┤
│• P-Core Pinning  │      │• BATCH_2 (8GB)   │      │• VRAM+GTT Limit  │
│• E-Core I/O Set  │      │• BATCH_4 (16GB)  │      │• Thermal ceiling │
│• AVX-VNNI flags  │      │• BATCH_8 (32GB)  │      │• Swappiness/zswap│
└──────────────────┘      └──────────────────┘      └──────────────────┘
```

#### Principle 1: Machine-Local Truth (M2, M23)
Hardware configurations must **never be committed to git**. Committing one node's hardware profile breaks the other node upon `git pull`. `config/hardware_profile.yaml` is added to `.gitignore`. A tracked template is provided at `config/hardware_profile.example.yaml`.

#### Principle 2: Zero Heavy Dependencies at Detection
Detection must execute via Python standard library (`os`, `sys`, `platform`, `ctypes`, `subprocess`) without requiring PyTorch, CUDA, or heavy third-party packages. It must be executable in a minimal bootstrap venv or rescue shell.

#### Principle 3: Backward Compatibility Guarantee
Existing references to `Zen2Optimizer`, `get_recommended_threads()`, and `spec_decode` in `src/omega/oracle/model_gateway.py` and `src/omega/oracle/providers.py` must continue functioning without breaking changes.

---

### §3. DETAILED HARDWARE MATRIX & FLEET EXPLOITATION

| Dimension | Node 0: AMD Ryzen 7 5700U | Node 1: Intel Core i7-13620H | Engine Exploitation Strategy |
| :--- | :--- | :--- | :--- |
| **Microarch** | Zen 2 (Renoir / Lucienne) | Raptor Lake-H (RPL-H) | Specialized compiler flags & cache tuning |
| **Cores / Threads** | 8 Cores / 16 Threads (Symmetric) | 6 P-cores (12T) + 4 E-cores (4T) = 16T | Asymmetric task scheduling |
| **Compute Set** | Cores `[0, 1, 2, 3, 4, 5, 6]` | Cores `[0, 2, 4, 6, 8, 10]` (Physical P-cores) | Pin llama.cpp strictly to physical P-cores |
| **Background Set**| Core `[7]` (or SMT siblings) | Cores `[12, 13, 14, 15]` (Atom E-cores) | Pin vector indexing, SQLite sync, and Hub |
| **Vector Units** | AVX2, FMA3, F16C | AVX2, FMA3, **AVX-VNNI** | Enable VNNI INT8/INT4 kernels in llama.cpp |
| **Memory Bus** | DDR4-3200 (Dual Channel) | DDR5-5200 (1x16GB $\rightarrow$ 2x16GB) | Scale concurrent slots based on active channels |
| **Memory BW** | ~51.2 GB/s | ~41.6 GB/s (Single) $\rightarrow$ **~83.2 GB/s (Dual)** | Token gen speed scales linearly with dual-channel |
| **iGPU Silicon** | Radeon Vega 8 (GFX902) | Intel Iris Xe Graphics (64 EUs) | Vulkan (RADV) on AMD; Vulkan (ANV) on Intel |
| **iGPU Memory** | 512MB VRAM + Dynamic GTT via TTM | Shared system memory via Mesa / Level-Zero | Dynamic VRAM+GTT pooling for GGUF offload |

---

### §4. KERNEL TELEMETRY & DISCOVERY SPECIFICATION

To ensure deterministic detection without guessing, the detector interrogates standard Linux kernel sysfs paths:

#### 1. Intel Hybrid Core Detection (P vs. E Cores)
* **Kernel Path 1**: `/sys/devices/cpu_core/cpus` $\rightarrow$ Returns CPU mask string for Performance Cores (e.g. `0-11`).
* **Kernel Path 2**: `/sys/devices/cpu_atom/cpus` $\rightarrow$ Returns CPU mask string for Efficient Cores (e.g. `12-15`).
* **Physical P-Core Isolation**:
  For each CPU in `cpu_core`, inspect `/sys/devices/system/cpu/cpu{N}/topology/core_cpus_list` (or `thread_siblings_list`). Take the minimum thread index for each unique `core_id`.
  * *Result for i7-13620H*: `[0, 2, 4, 6, 8, 10]`.

#### 2. Vector Instruction Flags
Parse `/proc/cpuinfo` flags:
* Check for `avx2`, `fma`, `f16c`.
* Check for `avx_vnni` (Intel Raptor Lake vector neural network instructions).
* Check for `avx512f`, `avx512_vnni` (Server/HEDT).

#### 3. GPU & Memory Carve-Out (VRAM / GTT)
* **AMD APU**:
  * VRAM: `/sys/class/drm/card0/device/mem_info_vram_total`
  * GTT: `/sys/class/drm/card0/device/mem_info_gtt_total`
* **Intel iGPU**:
  * Inspect `/sys/class/drm/card0/device/drm/card0/` or query Mesa driver via `vulkaninfo --summary`.

#### 4. Memory Channels & Capacity
* Parse `/proc/meminfo` for `MemTotal` and `MemAvailable`.
* If permitted (root/sudo) or cached, check `dmidecode -t 17` for populated slots (detecting single vs dual channel). If unprivileged, fallback to heuristic based on total detected memory.

---

### §5. STEP-BY-STEP IMPLEMENTATION PLAN

```
================================================================================
PHASE 1: HARDWARE PROFILING SCRIPT EXPANSION (Immediate)
--------------------------------------------------------------------------------
1.1 Expand scripts/detect_hardware_profile.py to support hybrid Intel topologies,
    AVX-VNNI detection, memory channel detection, and GTT extraction.
1.2 Create config/hardware_profile.example.yaml with full schema documentation.
1.3 Ensure config/hardware_profile.yaml is ignored in .gitignore.
1.4 Add `make probe-hardware` target to Makefile.

================================================================================
PHASE 2: ORACLE CPU OPTIMIZER REFACTORING (Core Engine)
--------------------------------------------------------------------------------
2.1 Refactor src/omega/oracle/cpu_optimizer.py:
    - Define BaseCpuOptimizer interface.
    - Extract existing logic into Zen2Optimizer(BaseCpuOptimizer).
    - Implement RaptorLakeOptimizer(BaseCpuOptimizer) with P-core/E-core mapping.
    - Implement GenericFallbackOptimizer(BaseCpuOptimizer).
    - Implement CpuOptimizerFactory.get_optimizer().
2.2 Retain top-level exports and alias `Zen2Optimizer = CpuOptimizerFactory.get_optimizer()`
    to maintain strict 100% backward compatibility for existing callers.

================================================================================
PHASE 3: COUNCIL ENGINE DYNAMIC LINKING (Orchestration)
--------------------------------------------------------------------------------
3.1 Update src/omega/council/hardware_detector.py:
    - Read config/hardware_profile.yaml if present.
    - If absent, invoke detect_hardware_profile.py runtime collector.
    - Evaluate RAM + Channel count + Core count to map to:
      * LOCAL_4GB
      * LOCAL_8GB
      * LOCAL_16GB
      * LOCAL_32GB_DUAL
      * CLOUD_EQUIVALENT
3.2 Extend src/omega/council/models.py to add LOCAL_32GB_DUAL and BATCH_8 concurrency.

================================================================================
PHASE 4: VERIFICATION & BENCHMARKING (Acceptance Gate)
--------------------------------------------------------------------------------
4.1 Run test suite: `pytest tests/test_hardware_profile.py` and `pytest tests/test_cpu_optimizer.py`.
4.2 Benchmark generation on Node 0 (HP): Record baseline tokens/sec.
4.3 Onboard Node 1 (Asus): Run `make probe-hardware`, verify P-core pinning and AVX-VNNI.
================================================================================
```

---

### §6. CONCRETE CODE IMPLEMENTATIONS

#### Component 1: `scripts/detect_hardware_profile.py` (Excerpts & Key Logic)

```python
# scripts/detect_hardware_profile.py
from dataclasses import dataclass, field, asdict
from pathlib import Path
import os
import platform
from typing import List, Optional, Set

@dataclass
class CPUProfile:
    vendor: str = "unknown"
    model: str = "unknown"
    architecture: str = "unknown"
    microarch: str = "unknown"
    physical_cores: int = 0
    logical_threads: int = 0
    is_hybrid: bool = False
    p_cores_physical: List[int] = field(default_factory=list)
    p_cores_logical: List[int] = field(default_factory=list)
    e_cores_logical: List[int] = field(default_factory=list)
    compute_cores: List[int] = field(default_factory=list)
    io_threads: List[int] = field(default_factory=list)
    recommended_threads: int = 4
    has_avx2: bool = False
    has_fma: bool = False
    has_avx_vnni: bool = False
    has_avx512: bool = False

def _detect_hybrid_topology() -> tuple[bool, List[int], List[int], List[int]]:
    """Detect Intel hybrid P/E core layout via kernel sysfs PMU interfaces."""
    p_core_sysfs = Path("/sys/devices/cpu_core/cpus")
    e_core_sysfs = Path("/sys/devices/cpu_atom/cpus")
    
    if not p_core_sysfs.exists():
        return False, [], [], []

    def parse_cpu_list(content: str) -> List[int]:
        cpus = []
        for part in content.strip().split(","):
            if "-" in part:
                start, end = map(int, part.split("-"))
                cpus.extend(range(start, end + 1))
            elif part:
                cpus.append(int(part))
        return sorted(cpus)

    p_logical = parse_cpu_list(p_core_sysfs.read_text())
    e_logical = parse_cpu_list(e_core_sysfs.read_text()) if e_core_sysfs.exists() else []
    
    # Extract physical P-cores (first SMT thread of each physical core)
    p_physical = []
    seen_cores = set()
    for cpu in p_logical:
        topo_core = Path(f"/sys/devices/system/cpu/cpu{cpu}/topology/core_id")
        core_id = int(topo_core.read_text().strip()) if topo_core.exists() else cpu
        if core_id not in seen_cores:
            seen_cores.add(core_id)
            p_physical.append(cpu)

    return True, p_physical, p_logical, e_logical

def _detect_cpu_flags() -> dict:
    flags = {"avx2": False, "fma": False, "avx_vnni": False, "avx512": False}
    try:
        with open("/proc/cpuinfo", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("flags"):
                    fset = set(line.split(":")[1].strip().split())
                    flags["avx2"] = "avx2" in fset
                    flags["fma"] = "fma" in fset
                    flags["avx_vnni"] = "avx_vnni" in fset or "avx512_vnni" in fset
                    flags["avx512"] = "avx512f" in fset
                    break
    except OSError:
        pass
    return flags
```

---

#### Component 2: `src/omega/oracle/cpu_optimizer.py` (Polymorphic Factory)

```python
# src/omega/oracle/cpu_optimizer.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
import logging
import yaml
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class BaseCpuOptimizer(ABC):
    """Abstract contract for hardware-specific CPU/inference optimization."""
    
    @abstractmethod
    def get_recommended_threads(self, model_size_b: float = 7.0) -> int:
        """Returns optimal compute thread count for llama.cpp execution."""
        pass

    @abstractmethod
    def get_compute_affinity(self) -> List[int]:
        """Returns list of CPU thread IDs for taskset core pinning."""
        pass

    @abstractmethod
    def get_io_affinity(self) -> List[int]:
        """Returns list of CPU thread IDs for background/IO tasks."""
        pass

    @abstractmethod
    def get_cmake_flags(self) -> str:
        """Returns target-specific compiler flags for llama.cpp compilation."""
        pass


class Zen2Optimizer(BaseCpuOptimizer):
    """AMD Zen 2 (Renoir / Lucienne / Ryzen 5700U) Reference Strategy."""
    
    def get_recommended_threads(self, model_size_b: float = 7.0) -> int:
        return 7  # 7 physical compute cores, 1 core reserved for OS/IO

    def get_compute_affinity(self) -> List[int]:
        return [0, 1, 2, 3, 4, 5, 6]

    def get_io_affinity(self) -> List[int]:
        return [7]

    def get_cmake_flags(self) -> str:
        return "-march=znver2 -mavx2 -mfma -mf16c -DLLAMA_AVX2=ON"


class RaptorLakeOptimizer(BaseCpuOptimizer):
    """Intel Raptor Lake-H (i7-13620H) Asymmetric Hybrid Strategy."""
    
    def __init__(self, p_cores: List[int], e_cores: List[int]):
        self.p_cores = p_cores or [0, 2, 4, 6, 8, 10]
        self.e_cores = e_cores or [12, 13, 14, 15]

    def get_recommended_threads(self, model_size_b: float = 7.0) -> int:
        # Strictly pin to physical P-cores to eliminate SMT contention
        return len(self.p_cores)

    def get_compute_affinity(self) -> List[int]:
        return self.p_cores

    def get_io_affinity(self) -> List[int]:
        return self.e_cores

    def get_cmake_flags(self) -> str:
        return "-march=raptorlake -mavx2 -mfma -mavxvnni -DLLAMA_AVX2=ON -DLLAMA_AVX_VNNI=ON"


class GenericFallbackOptimizer(BaseCpuOptimizer):
    """Fallback strategy for unclassified platforms."""
    def get_recommended_threads(self, model_size_b: float = 7.0) -> int:
        import os
        return max(1, (os.cpu_count() or 4) - 1)

    def get_compute_affinity(self) -> List[int]:
        import os
        return list(range(max(1, (os.cpu_count() or 4) - 1)))

    def get_io_affinity(self) -> List[int]:
        import os
        return [max(0, (os.cpu_count() or 4) - 1)]

    def get_cmake_flags(self) -> str:
        return "-march=native -mavx2"


class CpuOptimizerFactory:
    """Factory creating optimal strategy from config/hardware_profile.yaml."""
    
    @classmethod
    def get_optimizer(cls) -> BaseCpuOptimizer:
        profile_path = Path(__file__).resolve().parent.parent.parent.parent / "config" / "hardware_profile.yaml"
        if not profile_path.exists():
            logger.warning("config/hardware_profile.yaml not found, falling back to Zen2 defaults")
            return Zen2Optimizer()
        
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            cpu = data.get("cpu", {})
            microarch = cpu.get("microarch", "").lower()
            is_hybrid = cpu.get("is_hybrid", False)

            if "raptorlake" in microarch or is_hybrid:
                return RaptorLakeOptimizer(
                    p_cores=cpu.get("p_cores_physical", []),
                    e_cores=cpu.get("e_cores_logical", [])
                )
            elif "zen2" in microarch or "5700u" in cpu.get("model", "").lower():
                return Zen2Optimizer()
            else:
                return GenericFallbackOptimizer()
        except Exception as err:
            logger.error(f"Failed to load hardware profile: {err}. Using Zen2 fallback.")
            return Zen2Optimizer()
```

---

#### Component 3: `src/omega/council/hardware_detector.py` (Dynamic Council Sizing)

```python
# src/omega/council/hardware_detector.py
from pathlib import Path
import logging
import yaml
from .models import HardwareProfile

logger = logging.getLogger(__name__)

def detect_hardware_profile() -> HardwareProfile:
    """Auto-detect hardware profile for optimal Council concurrency."""
    profile_path = Path(__file__).resolve().parents[3] / "config" / "hardware_profile.yaml"
    
    total_ram_mb = 16384  # Default fallback
    has_discrete_gpu = False
    
    if profile_path.exists():
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            total_ram_mb = data.get("memory", {}).get("total_mb", 16384)
            has_discrete_gpu = data.get("gpu", {}).get("vendor") == "nvidia"
        except Exception as err:
            logger.warning(f"Error reading hardware profile: {err}")
    else:
        # Fallback reading /proc/meminfo directly
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        total_ram_mb = int(line.split()[1]) // 1024
                        break
        except Exception:
            pass

    # Dynamic classification thresholds
    if total_ram_mb >= 32000:
        return HardwareProfile.CLOUD_EQUIVALENT if has_discrete_gpu else HardwareProfile.LOCAL_32GB_DUAL
    elif total_ram_mb >= 14000:
        return HardwareProfile.LOCAL_16GB
    elif total_ram_mb >= 7000:
        return HardwareProfile.LOCAL_8GB
    else:
        return HardwareProfile.LOCAL_4GB
```

---

### §7. CRITICAL CALLOUTS, CAVEATS & TRENCH TRAPS

> ⚠️ **CAVEAT 1: The SMT "Hyper-Threading Trap" on P-Cores**  
> On Intel Raptor Lake, the 6 P-cores have Hyper-Threading (SMT) enabled by default, presenting 12 virtual threads (`cpu0` through `cpu11`).  
> **Never set `llama.cpp` `-t 12`!**  
> Hyper-threaded sibling pairs share L1/L2 caches and execution ports. Under matrix multiplication, two threads running on the same physical core fight over vector registers, creating thermal throttling and a ~20% net drop in throughput.  
> **Always use `-t 6` pinned strictly to physical P-cores (`0, 2, 4, 6, 8, 10`).**

> ⚠️ **CAVEAT 2: The E-Core Latency Drag**  
> If an inference thread gets scheduled on an Atom E-core (`cpu12`–`cpu15`), the entire synchronous token generation barrier waits for that single slowest core.  
> **Never allow the OS scheduler to freely migrate llama.cpp worker threads across the hybrid boundary.** Enforce thread affinity with `taskset` or `pthread_setaffinity_np`.  
> *Note (D-426, 2026-09-06): E-cores (Gracemont) DO support AVX2 + AVX-VNNI (256-bit) — verified by researcher report `hw-research-gaps-20260906-01`. AVX-VNNI INT8/INT4 kernels are safe on ALL 10 cores; no SIGILL risk. AVX-512 is fused off on all consumer Alder/Raptor Lake — do NOT enable AVX-512 paths.*

> ⚠️ **CAVEAT 3: AMD GTT Page Limits vs BIOS Carve-Out**  
> On your HP laptop (Ryzen 5700U), the BIOS VRAM is only 512MB. If you try to run an 8B model on Vulkan without adjusting kernel TTM limits, `llama-server` may crash with `vk::DeviceLostError`.  
> To unlock system RAM for Vulkan iGPU inference, ensure your kernel boot parameter in `/etc/default/grub` contains:  
> `ttm.pages_limit=3670016` (maps ~14GB of system RAM to GTT).  
> *Note: Use `ttm.pages_limit`, NOT `amdttm.` (which is silently ignored on consumer Ryzen APUs).*

> ⚠️ **CAVEAT 4: Memory Rank and Bandwidth Realities on ASUS P1**  
> With the factory single 16GB stick, your memory bandwidth is locked to **Single-Channel (~41.6 GB/s)**.  
> Upgrading to 2×16GB DDR5-5200 unlocks **Dual-Channel (~83.2 GB/s)**.  
> Because local LLM generation is completely memory-bandwidth bound, this hardware upgrade will produce an immediate **~1.8x to 2x speedup in tokens/second** without changing a single line of software.

---

### §8. VERIFICATION GATES & ACCEPTANCE CRITERIA

Before merging and deploying DHAL across the fleet, the following gates must exit 0:

- [ ] **Gate 1: Silicon Discovery Determinism**  
  `python3 scripts/detect_hardware_profile.py` correctly detects:
  - On HP: `vendor: amd`, `microarch: zen2`, `is_hybrid: false`, `compute_cores: [0..6]`.
  - On Asus: `vendor: intel`, `microarch: raptorlake`, `is_hybrid: true`, `p_cores_physical: [0, 2, 4, 6, 8, 10]`, `e_cores_logical: [12, 13, 14, 15]`, `has_avx_vnni: true`.
- [ ] **Gate 2: Non-Destructive Git Status**  
  `config/hardware_profile.yaml` is properly ignored by git. Running `git status` on either machine shows no untracked configuration changes.
- [ ] **Gate 3: Backward Compatibility**  
  Existing calls to `Zen2Optimizer` in `src/omega/oracle/model_gateway.py` continue to pass all unit and integration tests.
- [ ] **Gate 4: Council Concurrency Scaling**  
  `detect_hardware_profile()` returns `LOCAL_16GB` on 16GB machines and transitions to `LOCAL_32GB_DUAL` / `BATCH_8` when memory >= 32GB **and** dual-channel memory is present (channels >= 2). Single-channel 32GB+ machines remain at `LOCAL_16GB` / `BATCH_4`.
- [ ] **Gate 5: Mandate M1 (AnyIO) & M2 (Firewall)**  
  Zero `asyncio` imports in core; zero stack logic leaking into hardware detection.

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ SPEC-DHAL-v1.0.0 ⬡ TRC-HARDWARE-MASTERY ⬡ 2026-09-06*
