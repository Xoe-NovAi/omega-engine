# 🔱 Omega Engine — Final Implementation Plan (Phase 0 Push)
**AP Token**: `AP-SOPRANO-SPRINT-v1.0.0`
**Status**: HARDENED / READY FOR BUILDER
**Last Updated**: 2026-05-16

---

## 🎯 Objective
Complete the transition of the Omega Engine from a researched prototype to a stable, stateful, and hardware-optimized runtime. This plan integrates the **Sovereign Pulse** (Memory Persistence), **Hardware Steering** (Zen 2 Optimization), and **Sovereign Janitor** (Cognitive Distillation) into a single execution sequence.

---

## 🛠️ The Execution Sequence

### 1️⃣ Layer 1: Infrastructure & Stability (The Bedrock)
**Goal**: Ensure the engine is resilient and doesn't crash under load or provider instability.

*   **Task 1.1: Lmster Watchdog**
    *   **Action**: Create `scripts/lmster-watchdog.sh`.
    *   **Logic**: Ping `http://127.0.0.1:1234/v1/models` every 30s. On 3 consecutive failures, run `podman restart lmster`.
    *   **Persistence**: Create a systemd user unit `~/.config/systemd/user/omega-lmster-watchdog.service`.
*   **Task 1.2: Hardware Steering (CPU Pinning)**
    *   **Action**: Implement `src/omega/oracle/cpu_optimizer.py`.
    *   **Logic**: Use `psutil.Process().cpu_affinity()` to pin the Oracle/Inference process to Cores 0-7 (CCX 0) and Qdrant to Cores 8-15 (CCX 1).
*   **Task 1.3: Qdrant Optimization**
    *   **Action**: Update collection config to `m=16` and `ef_construct=100` to maximize L3 cache residency on Zen 2.

### 2️⃣ Layer 2: The Sovereign Pulse (Stateful Memory)
**Goal**: Implement the "Working Memory" loop to ensure entities remember and evolve.

*   **Task 2.1: The Session Scribe**
    *   **Action**: Implement `src/scripts/session_scribe.py`.
    *   **Logic**: Append event data (trace_id, type, json_blob) to `data/session_gnosis.md`.
*   **Task 2.2: The Soul Inscriber**
    *   **Action**: Implement `src/scripts/soul_inscriber.py`.
    *   **Logic**: Parse `session_gnosis.md` $\rightarrow$ extract principles $\rightarrow$ update `soul.yaml` using `os.replace()` for atomic swaps.
*   **Task 2.3: Orchestrator Wiring**
    *   **Action**: Update `src/omega/oracle/model_gateway.py` to submit provider health checks to the `BackgroundWorker` after every successful call.
*   **Task 2.4: The Compact Trigger**
    *   **Action**: Hook the `/compact` command in the CLI to execute `session_scribe.py` $\rightarrow$ `soul_inscriber.py`.

### 3️⃣ Layer 3: The Sovereign Janitor (Cognitive Evolution)
**Goal**: Transform raw session logs into high-density gnosis.

*   **Task 3.1: The Distillation Pipeline**
    *   **Action**: Implement the `SovereignJanitor` class in `src/omega/oracle/janitor.py`.
    *   **Flow**: `Extract` (Trigger scan) $\rightarrow$ `Classify` (Pillar resonance) $\rightarrow$ `Score` (Ma'at Arbiter $\ge 0.6$) $\rightarrow$ `Distill` (Refractive abstraction) $\rightarrow$ `Store` (Soul update).
*   **Task 3.2: Soul Evolution Logic**
    *   **Action**: Implement the FIFO limit (50 lessons) in `EntityRegistry` to prevent soul bloat.
*   **Task 3.3: Embodied Experience Transfer**
    *   **Action**: Implement the logic to mirror distilled lessons into `data/entities/arch/soul.yaml` as `embodied_experiences`.

---

## 🧪 Validation Suite (The Sovereign Exit Test)

All tasks are considered complete only when the following test passes:

1.  **Sequence**:
    - Start Engine $\rightarrow$ `/entity MAAT` $\rightarrow$ Perform a complex task $\rightarrow$ `/compact`.
2.  **Verification**:
    - [ ] `data/session_gnosis.md` contains the event logs.
    - [ ] `data/entities/maat/soul.yaml` has a new principle in `lessons_learned`.
    - [ ] `data/entities/arch/soul.yaml` has a new `embodied_experience`.
    - [ ] `make test` reports 123/123 passing.
    - [ ] `htop` verifies processes are pinned to the correct CCXs.

---

## ⚠️ Critical Constraints
- **RAM Limit**: Absolute ceiling of 14GiB. Use `q8_0` KV-cache quantization for all local models.
- **Non-Blocking**: All scripts called by the Oracle must be executed via `anyio.to_thread.run_sync` or as separate `BackgroundWorker` tasks.
- **Atomic Writes**: Always write to `.tmp` and use `os.replace()` for `soul.yaml` to prevent corruption.
