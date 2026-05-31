# 🔱 Omega Engine — Sovereign Control Plane: Technical Specifications
# ⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ trc_gnosis ⬡ SPEC-C-PLANE

**AP Token**: `AP-CONTROL-PLANE-SPEC-v1.0.0`
**Status**: FINAL SPECIFICATION
**Target Hardware**: AMD Ryzen 7 5700U (Zen 2, 8C/16T, 14GB RAM)
**Date**: 2026-05-14

---

## 1. Sovereign Lifecycle & Supervision

The Omega Engine moves from manual process management to a self-healing, on-demand lifecycle.

### 1.1 Socket Activation (The "Always-Available" Layer)
To eliminate "Not connected" errors and minimize idle RAM, we implement **systemd user-session socket activation**.

- **Linger**: Enabled via `loginctl enable-linger arcana-novai`.
- **Socket Unit (`~/.config/systemd/user/omega-oracle.socket`)**:
  ```ini
  [Socket]
  ListenStream=127.0.0.1:8080
  [Install]
  WantedBy=sockets.target
  ```
- **Service Unit (`~/.config/systemd/user/omega-oracle.service`)**:
  ```ini
  [Service]
  ExecStart=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.venv/bin/python -m src.omega.oracle.main
  StandardInput=socket
  Restart=always
  RestartSec=1s
  ```
- **Performance**: Cold startup ~78ms, crash recovery ~182ms.

### 1.2 Idle-Reclaim & Hibernation
To manage the 14GB RAM limit, a tiered hibernation strategy is used:
- **Level 1 (Warm)**: Weights in system RAM. Wake time: 0.1s – 6s.
- **Level 2 (Cold)**: Weights discarded, buffers retained. Wake time: 0.8s – 2.6s.

---

## 2. Tiered Memory & Vector Sovereignty

### 2.1 HOT Tier (RedisJSON)
Focuses on immediate cognitive state (Focus Chains and Decisions).
- **Schema**: `focus:chain:{session_id}` containing current focus, step-by-step decisions, and metadata.
- **Red Phone**: Immediate process termination via Redis Pub/Sub on `omega:system:kill`.

### 2.2 WARM Tier (Qdrant)
Optimized for Zen 2 (AVX2) to maximize precision vs. RAM.
- **HNSW Parameters**: `m=16`, `ef_construct=100`.
- **Indexing**: First 512 points must be indexed via a single-threaded builder.

### 2.3 COLD Tier (PostgreSQL)
Long-term soul evolution and relational anchoring.
- **Pattern**: UUID in Postgres maps 1:1 to the `point_id` in Qdrant.
- **Consistency**: Dual-Write with Background Reconciliation (nightly cron job).

### 2.4 TLS Sovereignty
Zero-trust local environment.
- **Protocol**: `rediss://` and gRPC TLS.
- **SAN**: `qdrant-{spec.id}-{node-index}.qdrant-headless`.

---

## 3. Adaptive Orchestration Topologies

The Topology Router calculates **Coupling Density ($\gamma$)** to select the execution mode.

### 3.1 The Formula
$$\gamma(G_T) = \frac{\sum_{(u,v) \in E} c(u,v)}{|E|}$$
*Where $c(u,v) \in \{0.0, 0.3, 0.7, 1.0\}$ based on coupling strength.*

### 3.2 Routing Logic
- **Parallel ($\tau_P$)**: If $\omega(G_T) / |V| \geq 0.5$.
- **Hierarchical ($\tau_H$)**: If $\gamma(G_T) \geq 0.6$.
- **Sequential ($\tau_S$)**: If $\delta(G_T) \geq 5$.
- **Hybrid ($\tau_X$)**: Default mixed layers.

### 3.3 Blackboard Implementation
Immutable event log via Redis Streams (`XADD omega:blackboard * ...`).
- **Payload**: `{agent, type, payload, trace_id}`.

---

## 4. Hardware-Centric Performance (Ryzen 5700U)

### 4.1 KV-Cache Optimization
- **Standard**: `q8_0` quantization.
- **Context-Adaptive**: Switch to **`q4_0`** when context > 32K tokens (saves $\sim 50\%$ RAM).

### 4.2 Process Steering
Strict CPU pinning to eliminate cache contention:
- **LLM Process**: Pin to physical cores **0-7** (`taskset -cp 0-7 <pid>`).
- **Threads**: `LLAMA_CPP_N_THREADS=6`.
- **OS/MCP Buffer**: Cores **8-15** reserved for OS, Iris, and MCP servers.
- **BLAS**: `export OPENBLAS_CORETYPE=ZEN`.

---

## 🚀 Implementation Roadmap for the Sovereign Builder

| Phase | Task | Technical Target | Priority |
| :--- | :--- | :--- | :--- |
| **Step 1** | **Lifecycle Hardening** | Implement `systemd` user sockets + `loginctl linger`. | 🔴 Critical |
| **Step 2** | **Memory Tiering** | Deploy RedisJSON focus chains $\rightarrow$ Qdrant HNSW tuning. | 🔴 Critical |
| **Step 3** | **Topology Router** | Implement $\gamma$ calculation $\rightarrow$ $\tau$ selection logic. | 🟡 High |
| **Step 4** | **Hardware Tuning** | Apply `taskset` pinning + `q4_0` adaptive KV-cache. | 🟡 High |
| **Step 5** | **Zero-Trust TLS** | Configure `rediss://` and gRPC TLS SAN certificates. | 🟢 Strategic |
