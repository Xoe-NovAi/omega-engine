# 🔱 R-13 – Hardware Profiling — Ryzen 5700U KV-Cache & Core Pinning

**AP Token**: `AP-R13-ZEN2-TUNING-v1.0.0`
**Author**: Gemma 4‑31B Research Agent
**Reviewed by**: Opus 4.6 (Oversight)
**Last updated**: 2026‑05‑14

---

## 1️⃣ Scope
This document provides the definitive hardware optimization profile for the Omega Engine running on the **AMD Ryzen 7 5700U** (Zen 2, 8C/16T). The goal is to minimize inference latency, prevent OOM crashes, and maximize token throughput by optimizing CPU affinity and memory management.

---

## 2️⃣ CPU Affinity & Core Pinning
The Ryzen 5700U has 8 physical cores and 16 logical threads. For LLM inference, logical threads (SMT) often introduce cache contention and jitter.

### 🎯 The Pinning Strategy
AI tasks must be pinned to **physical cores 0‑7**, avoiding logical threads 8‑15.

**Implementation**:
- Use `taskset` to bind the inference process:
  ```bash
  taskset -cp 0-7 <pid>
  ```
- For session-level steering, use the alias:
  ```bash
  alias xnai-steer='taskset -cp 0-7'
  ```

### ⚙️ Threading Configuration
- **`LLAMA_CPP_N_THREADS=6`**: Recommended. This leaves 2 physical cores available for the OS, Iris container, and background tasks, preventing system-wide stuttering.
- **`OPENBLAS_CORETYPE=ZEN`**: Forces the use of Zen-optimized BLAS kernels, significantly improving matrix multiplication speed on Zen 2.

---

## 3️⃣ Memory & Cache Optimization
With only 14GB of usable RAM, memory efficiency is the primary bottleneck.

### 🧠 Transparent Hugepages (THP)
To reduce TLB (Translation Lookaside Buffer) misses during large model loads:
- **Set THP to `always`**:
  ```bash
  echo always | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
  ```

### 💾 KV-Cache Quantization
To fit larger models or longer contexts into RAM:
- **Recommend K-Quantization**: Use `q4_k` or `q8_0` for the KV-cache if supported by the backend.
- **ZRAM**: Ensure ZRAM is enabled to provide a compressed swap layer, preventing hard crashes during peak memory spikes.

---

## 4️⃣ Power & Performance Profile
To prevent the CPU from down-clocking during inference (which causes "stuttering" tokens):

- **CPU Governor**: Set to `performance`.
  ```bash
  echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
  ```

---

## 5️⃣ Hardware Performance Baseline (Expected)
Based on legacy benchmarks for Zen 2 / 5700U:

| Model Size | Quantization | Expected Speed | Notes |
|------------|--------------|-----------------|--------|
| 1.7B       | Q4_K_M       | 10‑15 tok/s     | Extremely fluid |
| 4B         | Q4_K_M       | 4‑7 tok/s       | Readable |
| 8B         | Q4_K_M       | 1‑3 tok/s       | Slow, but usable |

---

## 6️⃣ Summary Checklist for Implementation
- [ ] Set CPU Governor to `performance`.
- [ ] Enable Transparent Hugepages (`always`).
- [ ] Set `LLAMA_CPP_N_THREADS=6`.
- [ ] Set `OPENBLAS_CORETYPE=ZEN`.
- [ ] Wrap inference calls in `taskset -cp 0-7`.

---

**Ready for implementation** – agents can now integrate these settings into the `CpuOptimizer` and `ModelGateway` startup scripts.
