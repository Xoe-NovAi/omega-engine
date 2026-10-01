<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# How-To: Hardware Adaptation & CPU Profiling (DHAL)
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ dhal-docs ⬡ how-to ⬡ hardware-adaptation

This guide explains how to discover, configure, and exploit heterogeneous silicon architectures (Intel Raptor Lake-H, AMD Zen 2, and generic platforms) using the **Dynamic Hardware Adaptation Layer (DHAL)**.

---

## 1. Executive Summary

Omega Engine adapts dynamically to your machine's physical hardware. Instead of hardcoding core counts, compiler flags, or batching heuristics into engine binaries, DHAL discovers silicon truth at boot:

- **Intel Hybrid Architectures (e.g., Core i7-13620H)**: Isolates physical Performance Cores (P-cores) for compute-bound `llama.cpp` inference, while allocating Atom Efficient Cores (E-cores) for background agent tasks (vector search, SQLite synchronization, telemetry).
- **AMD Monolithic Architectures (e.g., Ryzen 7 5700U)**: Pins compute tasks to physical cores across CCXs, leaving dedicated headroom for OS and draft models.
- **Memory Bandwidth Scaling**: Automatically determines Council concurrency (`SERIAL_INDEPENDENT`, `BATCH_2`, `BATCH_4`, `BATCH_8`, `PARALLEL`) based on active memory channels and detected RAM bandwidth.

---

## 2. One-Touch Discovery: `make probe-hardware`

When deploying Omega Engine on a new machine or after a RAM/hardware upgrade, run:

```bash
make probe-hardware
```

This runs `scripts/detect_hardware_profile.py`, inspects Linux kernel `sysfs` (`/sys/devices/cpu_core/cpus`, `/sys/devices/cpu_atom/cpus`, `/sys/class/drm/`) and `procfs` (`/proc/cpuinfo`, `/proc/meminfo`), and generates a node-local profile:

```
config/hardware_profile.yaml
```

> 🔒 **Git Decoupling Note**: `config/hardware_profile.yaml` is ignored in `.gitignore`. It is your machine's local Single Source of Truth (SSOT) and is never committed to git, preventing merge conflicts across multi-node fleets.

---

## 3. Understanding Your Hardware Profile

Here is an example output generated for an asymmetric Intel hybrid processor:

```yaml
cpu:
  vendor: "intel"
  model: "13th Gen Intel(R) Core(TM) i7-13620H"
  microarch: "raptorlake"
  physical_cores: 10
  logical_threads: 16
  is_hybrid: true
  p_cores_physical: [0, 2, 4, 6, 8, 10]
  p_cores_logical: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
  e_cores_logical: [12, 13, 14, 15]
  compute_cores: [0, 2, 4, 6, 8, 10]
  io_threads: [12, 13, 14, 15]
  recommended_threads: 6
  has_avx2: true
  has_fma: true
  has_avx_vnni: true
  has_avx512: false
memory:
  total_mb: 31890
  available_mb: 28410
  type: "DDR5"
  channels: 2
  est_bandwidth_gbps: 83.2
gpu:
  vendor: "intel"
  model: "Iris Xe Graphics (64EU)"
  is_discrete: false
  vram_mb: 0
  gtt_mb: 15945
```

---

## 4. How the Engine Uses This Data

### A. Core Pinning & Thread Count (`src/omega/oracle/cpu_optimizer.py`)
`CpuOptimizerFactory.get_optimizer()` selects the appropriate strategy:
- **`RaptorLakeOptimizer`**: Pins LLM execution to physical P-cores `[0, 2, 4, 6, 8, 10]`. It restricts `llama.cpp` to `-t 6`. It explicitly avoids hyper-threaded siblings (which cause cache thrashing) and Atom E-cores (which cause thread synchronization lag).
- **`Zen2Optimizer`**: Pins LLM execution to physical cores `[0, 1, 2, 3, 4, 5, 6]`.
- **`GenericFallbackOptimizer`**: Allocates `os.cpu_count() - 1` cores with native compiler targets.

### B. Vector Neural Network Acceleration (AVX-VNNI)
If `has_avx_vnni: true`, the build instruction and runtime flags automatically inject `-mavxvnni -DLLAMA_AVX_VNNI=ON`, drastically speeding up INT8/INT4 quantized matrix multiplication.

### C. Council Concurrency Routing (`src/omega/council/execution_mode.py`)
Council concurrency scales directly with physical memory bandwidth:

| Profile | Memory & Hardware Setup | Concurrency Mode | Node Throughput |
| :--- | :--- | :--- | :--- |
| `CLOUD_EQUIVALENT` | 32GB+ RAM + Discrete GPU (NVIDIA/AMD) | `PARALLEL` | All nodes simultaneous |
| `LOCAL_32GB_DUAL` | 32GB+ RAM + Dual-Channel DDR5 (UMA) | `BATCH_8` | 8 nodes simultaneous |
| `LOCAL_16GB` | 14GB–30GB RAM | `BATCH_4` | 4 nodes simultaneous |
| `LOCAL_8GB` | 7GB–14GB RAM | `BATCH_2` | 2 nodes simultaneous |
| `LOCAL_4GB` | < 7GB RAM | `SERIAL_INDEPENDENT` | 1 node at a time |

---

## 5. Verification & Testing

To verify hardware adaptation and DHAL unit tests at any time, run:

```bash
# Run all DHAL hardware test suites
.venv/bin/python -m pytest tests/test_dhal_detector.py tests/test_cpu_optimizer.py tests/test_council_hardware.py tests/test_hardware.py -v
```

All tests should report `OK`.
<!-- PROVENANCE-CORRECTED 2026-09-07T03:03:09Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: dhal-docs | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

