# 🚀 First-Run Experience (FRX) Specification
**Target**: Clean-room clone to interactive inference in under 10 minutes  
**Audience**: Developers deploying on x86-64 / ARM laptops

---

## 1. The 10-Minute Onboarding Contract

When a developer clones `omega-engine`, the setup experience must be deterministic, resilient to network drops, and self-diagnosing.

```
git clone https://github.com/xnai/omega-engine.git
cd omega-engine
make setup
```

The `make setup` command must execute the following five-phase automated pipeline:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ 1. DHAL PROBE   │───►│ 2. PREREQS      │───►│ 3. ENV TUNING   │
│  Detect CPU/RAM │    │ Check Ollama/   │    │ Write systemd   │
│  Channel config │    │ Docker/Python   │    │ thread overrides│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                       ┌─────────────────┐             │
                       │ 5. VERIFY BENCH │◄────────────┘
                       │ 1-second local  │     ┌─────────────────┐
                       │ token test      │◄───►│ 4. MODEL PULL   │
                       └─────────────────┘     │ Fetch tiny 3B   │
                                               │ validation card │
                                               └─────────────────┘
```

---

## 2. Phase Breakdown & Guardrails

### Phase 1: Dynamic Hardware Probe (DHAL)
*   **CPU Architecture**: Detects whether the processor is Intel Hybrid (P/E cores), AMD Zen, or Apple Silicon/ARM.
*   **The P-Core Trap Guard**: If Intel 12th/13th/14th Gen is detected, it enforces the hybrid mask rule: **Never narrow to physical cores only**. It pins `AllowedCPUs` to the full P-core range including HyperThreading siblings (e.g., `0-11` on a 6P+4E chip) to prevent spin-wait lock convoys.
*   **RAM Topology**: Probes single-channel vs. dual-channel memory bandwidth to set `OLLAMA_MAX_LOADED_MODELS` (1 for single-channel $\le$16GB; 2+ for dual-channel 32GB+).

### Phase 2: Dependency Verification & Graceful Fallback
*   Checks for Python 3.12+, `ollama`, `git`, `make`, `jq`, and Docker.
*   **Zero-Panic Principle**: If Docker is not found or the daemon is inactive, `make setup` must **not exit with a fatal error**. It prints:
    ```
    [INFO] Docker not detected. Skipping Open WebUI container.
    [OK] CLI Engine and HTTP server are fully functional via 'make python-chatbot'.
    ```

### Phase 3: Automated Environment Tuning
*   Generates `.env.ollama` and applies `/etc/systemd/system/ollama.service.d/override.conf`.
*   Applies KV-cache quantization (`q8_0`) and Flash Attention automatically.

### Phase 4: Verification Model Pull
*   Pulls a vetted, lightweight verification model (`phi4-mini` or `qwen2.5:3b`).
*   Uses resumable transfer strategies if running over unstable connections.

### Phase 5: The Dopamine Benchmark
*   Executes `make bench MODEL=phi4-mini`.
*   Prints expected vs. actual throughput table:
    *   *Low-tier (4-core/8GB)*: 4–7 t/s
    *   *Mid-tier (8-core/16GB DDR4/DDR5 single)*: 12–15 t/s
    *   *High-tier (16-core/32GB DDR5 dual)*: 22–30+ t/s

---

## 3. Post-Setup Next Steps Prompt

At the conclusion of `make setup`, the terminal displays three clear options:
1. `make python-chatbot` — Immediate interactive terminal dialogue.
2. `make python-serve` — Launch local HTTP API on `:8080` (OpenAPI Swagger UI).
3. `make gnosis-lock` — Review your local entity identity and evolution ledger.
