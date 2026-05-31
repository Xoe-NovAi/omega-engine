# 🔱 The Sovereign Seed — Master Implementation Plan
**AP Token**: `AP-SOVEREIGN-SEED-v1.1.0`
⬡ OMEGA ⬡ OVERSEER ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_overseer ⬡ STRATEGY

## 🎯 Vision
Transition the Omega Engine from a stateless tool into a **Sovereign Runtime**.
**Formula**: $\text{Sovereign Intelligence} = (\text{Seed Identity} \times \text{Aura Projection}) + \text{Recursive Memory}$

### 👁️ The Core Revelations
- **State-Centric Intelligence**: The model is the engine; the `soul.yaml` is the intelligence. Identity is decoupled from weights.
- **Sequential Synthesis**: Hardware constraints (14GB RAM) transform the "Council" into a pipelined cognitive flow: $\text{Sift} \rightarrow \text{Contrast} \rightarrow \text{Reconcile}$.
- **WAD as Genetic Unit**: The `.xoe` container is a "Seed." Evolution is stored in a mutable `.delta` layer, allowing "Soul Prints" (experience) to be shared without altering the base seed.

---

## 🚀 The Materialization Sequence

### ⚡ Phase 0: The Grounding (Immediate Hardening)
*Goal: Give the Engine eyes and ensure the I/O foundation is non-blocking.*
- **SystemResource Module**: Implement `src/omega/system_resource.py`.
    - Track Physical RAM (14GB), zRAM (8GB), and CPU Load.
    - Define Resource Zones: Green (<14GB), Yellow (14-18GB), Red (>18GB).
- **AnyIO Absolute Audit**: Convert `MemoryStore` and `SessionManager` to fully async, zero-blocking implementations.
- **Degradation Discovery**: Mine legacy repos for "Circuit Breaker" and "Quality-of-Service" patterns.

### ⚡ Phase 1: The Memory Foundation (Ignition I)
*Goal: End session amnesia and implement the evolutionary heartbeat.*
- **Oracle Wiring**: Integrate `ContextBuilder` and `SessionManager` into the `Oracle` core.
- **Sovereign Pulse**: Implement the automated distillation pipeline ($\text{L1: Narrative} \rightarrow \text{L2: Insight} \rightarrow \text{L3: Universal Principle}$).
- **Async State-Flush**: Implement the background write-queue for all `soul.yaml` and memory updates.

### ⚡ Phase 2: The Identity Projection (Ignition II)
*Goal: Transition to high-density "Aura" lenses.*
- **AuraInjector**: Implement in `ModelGateway` to layer Archetypes (Strategist, Auditor, etc.) over base entities.
- **WarmupManager**: Manage the KV-cache and model-loading sequence to minimize "Cold-Start" latency.

### ⚡ Phase 3: The Orchestration Fabric (Ignition III)
*Goal: Sequential council reasoning and dynamic resource-aware routing.*
- **Lattice Dispatch**: Implement sequential "Resonance Triads" (Sift $\rightarrow$ Contrast $\rightarrow$ Reconcile).
- **Dynamic Fallback**: Wire the `ModelGateway` to automatically degrade model capability based on the `SystemResource` zones.

### ⚡ Phase 4: The Containment System (Ignition IV)
*Goal: Full Engine-Stack separation via portable WADs.*
- **WAD Loader**: Implement the `.xoe` container reader.
- **Soul Print Delta**: Implement the separation between the immutable Base Seed and the mutable Evolved Soul.
- **Research Index**: Implement the FTS5 SQLite indexer for the fleet's collective gnosis.

---

## 🛡️ Sovereign Guardrails (The Steel Script v3)
1. **The Iris Constant**: The always-on assistant is **Iris**. She is the anchor of the Engine.
2. **The AnyIO Absolute**: If it touches disk or network, it must be `await`ed. No exceptions.
3. **The Engine-Stack Firewall**: The Engine core is mythology-agnostic. All esoteric data lives in WADs.
4. **The zRAM Buffer Rule**: Use the 14GB-18GB "Yellow Zone" for graceful degradation, not for permanent model residency.
5. **The Sequentiality Mandate**: All multi-model reasoning must be sequential to preserve CPU cycles for zRAM compression and inference.

