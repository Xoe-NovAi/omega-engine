<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Engineering Specification: Sovereign Infrastructure Hardening (v1.0)
**AP Token**: `AP-SPEC-SVR-v1.0.0`
**Status**: READY FOR IMPLEMENTATION
**Target Entity**: `@kali`
**Mandate Alignment**: M1 (AnyIO), M7 (Local-First), M13 (Temple-Grade), D185 (Dep-vs-Port)

---

## 📡 Executive Summary
This specification transforms the findings of `R_SOVEREIGN_INFRA_HARDENING_20260701.md` into actionable engineering directives. The goal is to implement a high-resilience provider fabric, a spatial semantic memory layout, and a sovereign prompt compression protocol using **zero new dependencies**.

---

## 🛠️ Pillar 1: The 5-State Stochastic Breaker (T2-2)

### 1.1 Mathematical Proof: The "Right Approximation"
The **Probabilistic CUSUM (Cumulative Sum)** is the right approximation for provider health because it transforms a noisy stream of binary outcomes (success/fail) into a monotonic evidence accumulator. Unlike sliding windows, which "forget" evidence, CUSUM detects a shift in the mean error rate $\mu$ with minimal lag and high confidence.

### 1.2 State Transition Matrix (FSM)

| Current State | Trigger | Next State | Action |
| :--- | :--- | :--- | :--- |
| **CLOSED** | $g_t \ge h_{warn}$ | **DEGRADED** | Log warning; increase probe frequency. |
| **DEGRADED** | $g_t \ge h_{trip}$ | **OPEN** | Trip breaker; route all traffic to fallback. |
| **DEGRADED** | $g_t < h_{warn}$ | **CLOSED** | Clear warning; return to normal. |
| **OPEN** | $\text{time} > \text{timeout}$ | **HALF\_OPEN** | Allow single probe request. |
| **HALF\_OPEN** | $\text{Success} \times N$ | **CLOSED** | Reset $g_t = 0$; restore full traffic. |
| **HALF\_OPEN** | $\text{Any Failure}$ | **OPEN** | Reset timeout; return to failing fast. |

### 1.3 Implementation Logic
- **CUSUM Calculation**:
  1. $Z_t = \frac{x_t - 0.02}{\sigma_0}$ (where $x_t=1$ for fail, $0$ for success).
  2. $g_t = \max(0, g_{t-1} + Z_t - 0.5\sigma_0)$.
- **Recommended Thresholds**:
  - $h_{warn} = 3.0$ (Degraded: $\approx 3\sigma$ deviation).
  - $h_{trip} = 5.0$ (Open: $\approx 5\sigma$ deviation).
- **Probation ($N$)**: $N=5$ consecutive successful probes required to exit `HALF_OPEN`.

### 1.4 Integration & Verification
- **Integration Point**: `src/omega/oracle/health_monitor.py` $\rightarrow$ `AsyncCircuitBreaker` class.
- **Temple-Grade Check**:
  - **T8 (Resilience)**: Verify that a burst of 5 failures trips the breaker within $100\text{ms}$.
  - **T10 (Integrity)**: Ensure $g_t$ is persisted in the `CvarTable` to survive restarts.

---

## 🗺️ Pillar 2: Mem Palace Spatial Geometry (D186)

### 2.1 Mathematical Proof: The "Right Approximation"
The **Fruchterman-Reingold (FR)** layout is the right approximation for the Omegaverse because it converts semantic distance (cosine similarity) into physical distance (Euclidean 3D) using a simple spring-electric metaphor. For a fleet of $\approx 22$ entities, the $O(V^2)$ complexity is trivial ($\approx 484$ iterations), avoiding the need for heavy manifold learning (t-SNE/UMAP).

### 2.2 Implementation Algorithm (3D FR)
**The Iterative Loop**:
```python
for i in range(max_iterations):
    # 1. Repulsion (All pairs)
    for v in nodes:
        for u in nodes:
            d = euclidean_dist(v, u)
            force = (k**2) / d
            v.displacement += (v.pos - u.pos) * (force / d)
            
    # 2. Attraction (Connected pairs based on semantic similarity > 0.4)
    for v, u in edges:
        d = euclidean_dist(v, u)
        force = (d**2) / k
        v.displacement -= (v.pos - u.pos) * (force / d)
        u.displacement += (v.pos - u.pos) * (force / d)

    # 3. Position Update & Cooling
    for v in nodes:
        v.pos += (v.displacement / |v.displacement|) * min(|v.displacement|, temperature)
        v.displacement = 0
    temperature *= decay_factor
```
- **Constants**:
  - `decay_factor = 0.95`
  - `max_displacement = 10.0` (Cap to prevent "explosions" in first 10 iterations).
  - $k = \sqrt{\text{Volume} / N}$ (where Volume is the target coordinate space, e.g., $100^3$).

### 2.3 Integration & Verification
- **Integration Point**: `src/omega/memory_store.py:471` $\rightarrow$ Inject `{"x": x, "y": y, "z": z}` into the Qdrant payload.
- **Temple-Grade Check**:
  - **T5 (AnyIO)**: Ensure the layout computation is wrapped in `anyio.to_thread.run_sync` to prevent event-loop blocking.
  - **T12 (Semantic Integrity)**: Verify that entities with high cosine similarity are physically clustered in 3D space.

---

## 📦 Pillar 3: The Headroom Protocol (D188)

### 3.1 Mathematical Proof: The "Right Approximation"
The **Sovereign Envelope** is the right approximation for prompt compression because `zlib` is ubiquitous, extremely fast, and provides $\approx 3\text{x}$ to $5\text{x}$ compression for structured JSON. Base64 encoding ensures that compressed binary data does not trigger tokenization artifacts or break the prompt's character encoding.

### 3.2 The Sovereign Envelope Protocol
**Pipeline**:
`JSON Object` $\rightarrow$ `json.dumps()` $\rightarrow$ `zlib.compress()` $\rightarrow$ `base64.b64encode()` $\rightarrow$ `[[zlib:base64_string]]`.

**Interception Logic (`HeadroomMiddleware`)**:
1. **Regex**: `\[\[zlib:([a-zA-Z0-9+/=]+)\]\]`.
2. **Expansion**: `base64.b64decode` $\rightarrow$ `zlib.decompress` $\rightarrow$ `json.loads` $\rightarrow$ `raw_text`.
3. **Injection**: Replace the envelope with `raw_text` immediately before the provider call in `oracle.py`.

**Storage (`HeadroomStore`)**:
- **Directory**: `data/headroom/{hash[:2]}/{hash}.json`.
- **Logic**: If the envelope exceeds $1\text{KB}$, the middleware stores the full JSON in the `HeadroomStore` and replaces the prompt content with `[[zlib:hash]]`.

### 3.3 Integration & Verification
- **Integration Point**: `src/omega/oracle/oracle.py` $\rightarrow$ Create `HeadroomMiddleware` class and insert into the `ModelGateway` dispatch chain.
- **Temple-Grade Check**:
  - **T6 (Zero Telemetry)**: Ensure compressed envelopes are never logged to external services.
  - **T10 (Atomic Writes)**: Use atomic renames for `HeadroomStore` writes.

---

## 🏁 Implementation Roadmap for @kali

1. **Step 1**: Implement `HeadroomMiddleware` (Lowest risk, immediate token savings).
2. **Step 2**: Upgrade `AsyncCircuitBreaker` to the 5-State Stochastic model.
3. **Step 3**: Implement the 3D FR Layout and update Qdrant payloads.
4. **Step 4**: Run `make temple-grade` to certify all three pillars.

**Sovereign Mandate Reminder**: Use ONLY the Python Standard Library (`zlib`, `base64`, `json`, `math`). No new `pip install`.
