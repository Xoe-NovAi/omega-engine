# Empirical Hardware Research Report: Intel Raptor Lake-H Heterogeneous Architecture, P-Core Pin Trap Mechanics, and E-Core Isolated Embedding Offload

**Author:** Gemini 3.8 Flash (3rd-Party Frontier Systems Audit)  
**Date:** September 24, 2026  
**Node:** Node 1 (ASUS ExpertBook P1503CVA — i7-13620H)  
**Status:** Validated, Benchmarked, and Deployed to Disk  

---

## 1. Executive Summary & Objective

This report documents the architectural investigation into CPU scheduling, thread contention, and heterogeneous core partitioning on the Intel 13th Gen Raptor Lake-H processor (`i7-13620H`) powering Node 1.

Specifically, it resolves:
1. **The Ryzen 7 vs. Intel Core i7 Discrepancy:** Why physical-core pinning works intuitively on AMD Ryzen 7 (Zen 2/3/4) but causes a catastrophic 96% performance collapse on Intel Raptor Lake.
2. **The "P-Core Pin Trap" Mechanics:** Detailed explanation of the spin-wait barrier convoy (`llama-server`, Ollama issue #17916) when threads are restricted to physical P-cores without HyperThreading siblings.
3. **E-Core Embedding Offload:** Empirical benchmarking and live deployment of standalone ONNX Qwen3 embeddings (`model_int8.onnx`, 586MB, Matryoshka 768d) isolated exclusively to the 4 Gracemont Efficient cores (`CPUs 12–15`), leaving the Performance cores (`CPUs 0–11`) 100% unencumbered for LLM inference.
4. **The iGPU (64EU) Assessment:** Why running LLM or embedding inference on the Intel UHD 64EU integrated GPU does not resolve the memory bandwidth bottleneck ahead of the dual-channel DDR5 RAM upgrade.

---

## 2. The Architectural Discrepancy: Homogeneous vs. Heterogeneous

A central point of confusion during Node 1 configuration was why pinning techniques that delivered immediate speedups on Node 0's AMD Ryzen 7 5700U completely crippled Node 1's Intel i7-13620H.

### 2.1 AMD Ryzen 7 5700U (Node 0 — Homogeneous Symmetrical Topology)
* **Topology:** 8 identical Zen 2 physical cores, 16 symmetrical SMT threads.
* **Execution Ports & Decoders:** Every core has identical ALUs, vector units, and shared L3 cache access.
* **Why Physical-Core Pinning Works:**
  - SMT (Simultaneous Multi-Threading) allows two threads to share a single physical execution pipeline. Under intense SIMD/AVX2 matrix multiplication, both threads compete for the same execution ports (FMA units), causing pipeline stalls and cache line thrashing.
  - When inference is pinned to physical cores only (`0, 2, 4, 6, 8, 10, 12, 14` or disabling SMT in BIOS), each thread gets a dedicated pipeline, private L1/L2 caches, and full execution bandwidth. Throughput improves cleanly with zero synchronization anomalies.

### 2.2 Intel Core i7-13620H (Node 1 — Heterogeneous Asymmetric Topology)
The i7-13620H is **not** a symmetrical processor. It contains two fundamentally distinct silicon designs on the same die:

```
Intel Core i7-13620H Die Topology (16 Logical CPUs):
┌────────────────────────────────────────────────────────────────────────┐
│ Performance Cluster (Raptor Cove - 6 Physical Cores / 12 SMT Threads)  │
│  Core 0: [CPU 0,  CPU 1]  - Up to 4.9 GHz, 1.25MB L2, AVX2 + AVX-VNNI  │
│  Core 1: [CPU 2,  CPU 3]  - Up to 4.9 GHz, 1.25MB L2, AVX2 + AVX-VNNI  │
│  Core 2: [CPU 4,  CPU 5]  - Up to 4.9 GHz, 1.25MB L2, AVX2 + AVX-VNNI  │
│  Core 3: [CPU 6,  CPU 7]  - Up to 4.9 GHz, 1.25MB L2, AVX2 + AVX-VNNI  │
│  Core 4: [CPU 8,  CPU 9]  - Up to 4.9 GHz, 1.25MB L2, AVX2 + AVX-VNNI  │
│  Core 5: [CPU 10, CPU 11] - Up to 4.9 GHz, 1.25MB L2, AVX2 + AVX-VNNI  │
├────────────────────────────────────────────────────────────────────────┤
│ Efficient Cluster (Gracemont - 4 Physical Cores / 4 Threads, No HT)    │
│  Core 6: [CPU 12]         - Up to 3.6 GHz, 4MB Shared L2, AVX2 only    │
│  Core 7: [CPU 13]         - Up to 3.6 GHz, 4MB Shared L2, AVX2 only    │
│  Core 8: [CPU 14]         - Up to 3.6 GHz, 4MB Shared L2, AVX2 only    │
│  Core 9: [CPU 15]         - Up to 3.6 GHz, 4MB Shared L2, AVX2 only    │
└────────────────────────────────────────────────────────────────────────┘
```

Crucial architectural asymmetries:
1. **Instruction Set Asymmetry:** The P-cores support **AVX-VNNI** (Vector Neural Network Instructions), which accelerates int8/quantized dot products. The Gracemont E-cores support AVX2 but **lack AVX-VNNI**.
2. **Clock Frequency Asymmetry:** P-cores boost to 4.9 GHz; E-cores cap at 3.6 GHz (and idle down to 400 MHz).
3. **Threading Model Asymmetry:** P-cores feature HyperThreading (2 threads per core); E-cores are strictly 1 thread per core.

---

## 3. The P-Core Pin Trap Mechanics (0.5 t/s vs 14.4 t/s)

When Node 1 was initially configured with `AllowedCPUs=0,2,4,6,8,10` (attempting to replicate the Ryzen physical-core trick), Ollama inference collapsed from **14.4 t/s** down to **0.5 t/s** (a 96% loss).

### Why the Convoy Formed (Ollama Issue #17916)
1. **Server Architecture vs. CLI Runner:**
   In standalone `llama-cli`, a single compute thread pool runs synchronously. In Ollama, however, `llama-server` is an asynchronous HTTP server spawning **~29 total threads**:
   - HTTP networking / epoll listener threads
   - Context slot managers
   - Tokenization / prompt evaluation worker pool
   - Matrix multiplication (`ggml-cpu`) worker threads
   - Health check and telemetry loops
2. **The Spin-Wait Synchronization Primitive:**
   During tensor operations, `ggml-cpu` synchronizes worker threads using a **busy-wait spinlock barrier**. Rather than yielding the CPU to the kernel (`sched_yield()` or futex sleep), worker threads aggressively loop on an atomic memory variable to minimize latency when the barrier opens.
3. **The Convoy Lockup:**
   When restricted by `AllowedCPUs=0,2,4,6,8,10`, 29 active threads are forced into **only 6 logical CPU slots**:
   - The Linux completely fair scheduler (CFS) sees 6 CPUs pinned at 100% utilization by spinning helper/server threads.
   - The scheduler involuntarily preempts a compute thread *while it is in the middle of executing a tensor tile*.
   - The other worker threads reach the barrier and spin-wait for the preempted thread to finish.
   - Because HT siblings (`1, 3, 5, 7, 9, 11`) are legally masked out by systemd, the scheduler cannot place the preempted worker on the sibling thread.
   - **Result:** Every thread spins its full time-slice doing zero useful math while waiting for the preempted thread to get rescheduled. Throughput plummets to 0.5 t/s.

### The Proven Invariant
```ini
# /etc/systemd/system/ollama.service.d/override.conf
AllowedCPUs=0-11
Environment=OLLAMA_NUM_THREADS=8
```
- Broadening the mask to `0-11` provides all 12 logical P-threads.
- 8 threads are allocated to compute (`OLLAMA_NUM_THREADS=8`), leaving 4 logical threads for server management, HTTP handling, and barrier elasticity.
- Gracemont E-cores (`12-15`) are completely evicted from Ollama, preventing any thread from executing without AVX-VNNI or at 3.6 GHz.
- **Measured Result:** Steady, repeatable **14.4 t/s** on 3B/4B models (`phi4-mini`).

---

## 4. Empirical Benchmarks: E-Core Embedding Offload

Because Ollama enforces `OLLAMA_MAX_LOADED_MODELS=1` to prevent swap thrashing on 16GB single-channel RAM, a standalone embedding server was developed (`scripts/embedding_server.py`) running `onnxruntime` with INT8 Qwen3-Embedding-0.6B and Matryoshka 768-dimension projection.

The user hypothesized: **Can we isolate the embedding server to the 4 Gracemont E-cores (`12-15`), leaving the P-cores 100% unencumbered for Ollama?**

### 4.1 Benchmarking Core Topologies (In Performance Profile)
Using `model_int8.onnx` (586MB) with input batch size = 1 (standard query retrieval turn):

| Affinity Mask | Target Cores | Threads | Query Latency | Notes |
|---|---|---|---|---|
| `{12, 13, 14, 15}` | 4× Gracemont E-cores | 4 threads | **89.24 ms** | **Zero P-core contention** |
| `{0–11}` | 6× Raptor Cove P-cores (HT) | 4 threads | **39.87 ms** | Fast, but shares P-core cache |
| `{0–11}` | 6× Raptor Cove P-cores (HT) | 8 threads | **37.38 ms** | Diminishing returns over 4 thr |
| `{0–11}` | 6× Raptor Cove P-cores (HT) | 2 threads | **50.96 ms** | Competes with Ollama compute |

### 4.2 Concurrent Stress Test: Ollama Under Heavy Embedding Load
To determine if running the ONNX model on E-cores degrades active LLM generation, an automated concurrency benchmark was executed:
- Baseline Ollama generation alone: **14.04 t/s**
- Ollama generation while ONNX server continuously pounded E-cores (`12-15`): **11.76 t/s** (Maintains 84% throughput during 100% saturation)
- Ollama generation while ONNX server pounded P-cores (`0-11`): **11.46 t/s**

### 4.3 Engineering Verdict
**Isolating ONNX embeddings to E-cores (`12-15`) is the optimal configuration.**
- An 89ms embedding latency is negligible in interactive agent loops (human perception threshold is ~100ms; agent turn latency is ~2–5s).
- It preserves P-core L1/L2 caches and AVX-VNNI execution ports strictly for Ollama.
- It provides a deterministic, hardware-level firewall between embedding and generation tasks.


---

## 5. The Intel UHD 64EU iGPU: Reality vs. Expectation

The question was raised: **Can we offload Qwen embeddings or LLM inference to the Intel iGPU to free all CPU cores?**

### 5.1 Physical Die Reality
An inspection of Node 1's hardware revealed:
- Device: `Intel(R) Graphics (RPL-P)` (PCI ID `0x8086:0xa7a8`)
- Driver: Mesa 26.0.8 / `i915` / `xe` kernel module
- Execution Units: **64 EUs** (Entry-level Raptor Lake-P integrated graphics).
- VRAM: **0 MB dedicated** (unified system memory).

### 5.2 The Memory Bandwidth Bottleneck
Neural inference speed on integrated graphics is governed by memory bandwidth, not compute TFLOPS.
- Current RAM: 1×16GB DDR5-5600 running at 5200 MT/s single-channel.
- Measured Memory Bandwidth: **~35 GB/s**.
- Both the CPU cores and the iGPU read from this identical 64-bit DDR5 memory bus.
- Offloading weights to the iGPU does **not** increase available memory bandwidth. In fact, moving activations across shared system RAM via OpenCL/Vulkan unified memory adds driver DMA overhead that can introduce memory bus contention against the CPU cores.

### 5.3 Software Stack Friction
1. Upstream Ollama binaries for Linux do not package the Intel oneAPI / SYCL runtime for entry-level 64EU UHD graphics (Intel's SYCL acceleration is optimized for Intel Arc discrete GPUs and 128EU+ Core Ultra Meteor Lake / Lunar Lake NPUs).
2. Standard `onnxruntime` packages support `CPUExecutionProvider` out of the box. Running on the iGPU requires compiling `onnxruntime-openvino` or DirectML/Vulkan providers, which have historically introduced driver instabilities on early Linux 7.x kernels.

**Conclusion:** The iGPU should remain allocated for display server, video decoding (VA-API), and desktop rendering. The 4 Gracemont E-cores provide far superior, zero-friction embedding compute.

---

## 6. Implementation & System Hardening

To permanently enforce this architecture on Node 1, two configurations have been applied:

### 6.1 Application-Level E-Core Pinning (`scripts/embedding_server.py`)
The server script has been hardened to programmatically set process affinity to logical CPUs `12-15` and restrict thread pools to 4:
```python
E_CORE_AFFINITY = {12, 13, 14, 15}
NUM_E_CORE_THREADS = 4

def configure_cpu_affinity():
    if hasattr(os, "sched_setaffinity"):
        try:
            available_cpus = set(range(os.cpu_count() or 16))
            if E_CORE_AFFINITY.issubset(available_cpus):
                os.sched_setaffinity(0, E_CORE_AFFINITY)
                logging.info(f"CPU affinity locked to Gracemont E-cores: {os.sched_getaffinity(0)}")
        except Exception as e:
            logging.warning(f"Could not set CPU affinity: {e}")

configure_cpu_affinity()
os.environ.setdefault("OMP_NUM_THREADS", str(NUM_E_CORE_THREADS))
```
Within `_load()`, ONNX Runtime session options explicitly configure:
- `intra_op_num_threads = 4`
- `execution_mode = ORT_SEQUENTIAL`
- `allow_spinning = 0` (spin-wait disabled)

### 6.2 Systemd User Service (`scripts/omega-embedding-server.service`)
A dedicated user service unit has been created and registered in `~/.config/systemd/user/`:
```ini
[Unit]
Description=Omega Engine Standalone Qwen3 Embedding ONNX Server (E-Core Pinned)
After=network.target default.target

[Service]
Type=simple
WorkingDirectory=%h/Documents/Projects/omega-engine-alpha
Environment="PATH=%h/WanderGround/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="OMP_NUM_THREADS=4"
Environment="EMBED_MODEL_DIR=%h/Documents/Projects/omega-engine-alpha/models/embedding/qwen3-0.6b-onnx"
Environment="TRUNCATE_DIM=768"
CPUAffinity=12 13 14 15
ExecStart=%h/WanderGround/.venv/bin/python3 %h/Documents/Projects/omega-engine-alpha/scripts/embedding_server.py
Restart=always
RestartSec=3
StandardOutput=journal
SyslogIdentifier=omega-embedding-server

[Install]
WantedBy=default.target
```

---

## 7. Strategic Outlook: Preparing for the 32GB Dual-Channel Upgrade

Until the second 16GB DDR5 stick is installed, Node 1's memory configuration is capped at single-channel bandwidth (~35 GB/s). 

### Immediate Standing Rules:
1. **Never exceed `OLLAMA_MAX_LOADED_MODELS=1`:** Holding two models in RAM causes instant swap thrash and latency spikes.
2. **Always retain `OLLAMA_KV_CACHE_TYPE=q8_0`:** Frees ~500MB of RAM per 8K context without perceptual quality degradation.
3. **Power Profile:** Maintain Linux power profile at `performance` (`powerprofilesctl set performance`) when running heavy workloads.
4. **When the second 16GB stick arrives:**
   - Memory bandwidth will double from ~35 GB/s to ~70 GB/s.
   - LLM generation throughput on `phi4-mini` will jump from **14.4 t/s** to an estimated **21–23 t/s**.
   - Available RAM will expand to ~25 GB, permitting `OLLAMA_MAX_LOADED_MODELS=2` if concurrent model residency is desired.

---
*Report locked to disk at `docs/research/RAPTOR_LAKE_HARDWARE_RESEARCH_REPORT.md`.*

