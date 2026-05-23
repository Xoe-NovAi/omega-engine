# 🔱 Omega Engine — Legacy Stack Discovery Report

**AP Token**: `AP-LEGACY-DISCOVERY-v1.0.0`
**Author**: Gemma 4‑31B Research Agent
**Date**: 2026‑05‑14
**Status**: COMPLETED

---

## 1️⃣ Executive Summary
A deep-dive audit of `xna-omega-legacy/` and `omega-stack-legacy/` was performed to reclaim architectural intelligence for the current Omega Engine. This report consolidates high-value findings that directly inform the remaining research queue (R‑11 through R‑15).

The legacy stacks were not merely "cruft" but contained a highly tuned operational environment for the Ryzen 5700U, a sophisticated provider-quota rotation system, and a robust Redis-based event fabric.

---

## 2️⃣ Hardware Tuning (Informs R‑13)
The legacy environment used a script `optimize_ryzen.sh` and specific environment variables to maximize Zen 2 performance.

### 🛠️ System-Level Optimizations
- **CPU Governor**: Set to `performance` to prevent frequency scaling latency.
- **Core Steering**: AI tasks pinned to physical cores 0‑7 using `taskset -cp 0-7` to avoid logical thread overhead.
- **Memory**: Transparent Hugepages (`THP`) enabled (`always`) to reduce TLB misses during large model loads.
- **Swap**: ZRAM used to mitigate OOM crashes on 16GB RAM.

### ⚙️ Inference Environment Variables
- `LLAMA_CPP_N_THREADS=6`: Optimal for 8C/16T Ryzen 5700U (leaving 2 cores for OS/Background).
- `OPENBLAS_CORETYPE=ZEN`: Forces optimized BLAS kernels for Zen 2 architecture.
- `MEMORY_LIMIT_GB=6.0`: Hard limit for local inference to prevent system freeze.

---

## 3️⃣ Orchestration & Event Fabric (Informs R‑12)
The legacy stacks relied heavily on **Redis 7.4.1** as a multi-purpose backbone, rendering RabbitMQ redundant for the current scope.

### 📡 Redis Usage Patterns
- **Event Bus**: Redis Streams used for the "Red Phone" kill-switch and agent-to-agent signaling.
- **Session State**: `session_manager` used Redis for ephemeral context and state persistence.
- **Vector Cache**: `vector_cache` used Redis to store frequent RAG embeddings.
- **Pub/Sub**: Used for real-time messaging between the Oracle and the voice interface.

**Recommendation**: Stick with Redis. It is already proven, lightweight, and supports all required patterns (Streams, Pub/Sub, Key-Value).

---

## 4️⃣ Health Monitoring & Observability (Informs R‑14)
A mature monitoring stack (Prometheus + Grafana + Consul) was used to ensure stability.

### 📈 Critical Redis Thresholds (Prometheus Rules)
| Metric | Threshold | Action |
|--------|-----------|--------|
| **Connected Clients** | `> 80%` of max | Alert: Connection saturation |
| **Memory Usage** | `> 85%` of max | Alert: Potential OOM / Eviction risk |
| **Cache Hit Rate** | `< 70%` | Alert: Inefficient indexing / Cold cache |
| **Eviction Rate** | `> 0.1/s` | Alert: Memory pressure / Too small cache |
| **Command Latency** | `p95 > 100ms` | Alert: Redis bottleneck |

### 🩺 Health Check Logic
- `healthcheck.py` implemented a tiered check: `Ping` $\rightarrow$ `Basic Op` $\rightarrow$ `Dependency Check`.
- Consul was used for service registration and automatic failover.

---

## 5️⃣ Quota & Cost Management (Informs R‑15)
The legacy `MultiProviderDispatcher` implemented a sophisticated account-rotation system.

### 💰 Quota Rotation Logic
- **Tracking**: `ACCOUNT-TRACKING-*.yaml` files stored daily usage per API key.
- **Rotation**: If a provider (e.g., Google AI Studio) returned a 429 (Rate Limit), the dispatcher automatically rotated to the next available account in the pool.
- **Auditing**: `xnai-quota-auditor.py` ran daily at 2 AM UTC to reset and sync quotas.

### 🎯 Dispatch Scoring Formula
Providers were selected based on a weighted score:
$$\text{Score} = (\text{QuotaScore} \times 0.4) + (\text{Latency} \times 0.3) + (\text{ContextFit} \times 0.3)$$

---

## 6️⃣ Context & Memory Management (Informs R‑11)
Findings from `COGNITIVE-ENHANCEMENTS.md` and `FINALIZED-STRATEGY-2026-02-22.md`.

- **Compaction Trigger**: OpenCode's internal compaction triggered at **~75%** of the model's context window, rather than a fixed token limit.
- **Contribution Analysis**: The system tracked which files/chunks contributed most to context consumption to optimize the "Invisible RAG" pipeline.

---

## 7️⃣ Conclusion
The legacy stacks provide a blueprint for a "Sovereign" setup. By porting the **Ryzen tuning**, **Redis-first orchestration**, and **Quota rotation** logic, the Omega Engine can achieve production-grade stability on consumer hardware.

**Next Action**: Integrate these findings into R‑11 through R‑15.
