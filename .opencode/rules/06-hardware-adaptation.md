---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
rule_id: "RULE-06-HARDWARE-ADAPTATION"
authority: "M7 Local-First + M2 Engine-Stack Firewall + M23 Failure Integrity"
applies_to: "all-agents"
date: "2026-09-06"
status: "ACTIVE"
---

# Architecture Rule: Dynamic Hardware Adaptation Layer (DHAL)

> **The silicon is heterogeneous; the engine is polymorphic. Never hardcode CPU cores,
> thread counts, or architecture flags into core libraries.**

## The Core Rule

Omega Engine automatically adapts its execution topology, thread pinning, and Council concurrency to the host's physical silicon via the **Dynamic Hardware Adaptation Layer (DHAL)**.

| Component | Location | Role |
| :--- | :--- | :--- |
| **Bare-Metal Probe** | `scripts/detect_hardware_profile.py` | Inspects kernel sysfs/procfs directly; writes profile |
| **Host Profile (SSOT)** | `config/hardware_profile.yaml` | Node-local physical reality (**git-ignored**) |
| **Profile Template** | `config/hardware_profile.example.yaml` | Tracked reference schema |
| **CPU Optimizer** | `src/omega/oracle/cpu_optimizer.py` | Dispatches to `Zen2Optimizer`, `RaptorLakeOptimizer`, or `GenericFallbackOptimizer` |
| **Council Concurrency**| `src/omega/council/hardware_detector.py` | Maps memory bandwidth & GPU to Council concurrency |
| **Spec Manual** | `docs/architecture/DYNAMIC_HARDWARE_ADAPTATION_LAYER_SPEC.md` | Authoritative specification (`SPEC-DHAL-v1.0.0`) |
| **User Guide** | `docs/how-to/hardware-adaptation-dhal.md` | Human & operator runbook |

## Invariants for All Agents

1. **Never Commit `hardware_profile.yaml`**:
   `config/hardware_profile.yaml` is excluded in `.gitignore`. It represents the physical reality of the specific node running the code. Committing a profile breaks fleet peers upon pull.

2. **One-Touch Setup**:
   When onboarding any new node or after modifying RAM/drives, execute:
   ```bash
   make probe-hardware
   ```

3. **Hybrid Architecture Pinning (Intel Raptor Lake-H / Alder Lake)**:
   - **Performance Cores (P-cores)**: Dedicated exclusively to compute-bound LLM matrix multiplication (`llama.cpp`) at `-t [physical_P_count]`. Hyper-threading (SMT) siblings must **never** be used for inference.
   - **Efficient Cores (E-cores)**: Dedicated to asynchronous background work (vector search, SQLite synchronization, telemetry, Hub).

4. **Monolithic Architecture Pinning (AMD Zen 2 / Ryzen 5700U)**:
   - Compute is pinned to physical cores `[0, 1, 2, 3, 4, 5, 6]`.
   - Core `[7]` is reserved for OS and draft models.

5. **Memory Bandwidth Dictates Concurrency**:
   - Local LLM inference speed is strictly bounded by memory bandwidth ($TPS \propto BW / ModelSize$).
   - Council concurrency scales with memory channels:
     - `LOCAL_16GB` (Single/Dual DDR4) $\rightarrow$ `BATCH_4`
     - `LOCAL_32GB_DUAL` (Dual-Channel DDR5-5200) $\rightarrow$ `BATCH_8`
     - `CLOUD_EQUIVALENT` (Discrete GPU) $\rightarrow$ `PARALLEL`
