# 🔱 Final Gap Closing Checklist — v0.6.0 Hardening

This checklist identifies the remaining implementation gaps required to achieve the **Hardened Master Strategy v2.0**.

## 🛡️ 1. Identity & Soul Hardening (Sovereign Stability)
- [ ] **Schema Update**: Add `soul_version`, `status`, and `certainty` fields to `lessons_learned` in `EntityRegistry.entity_scaffold()`.
- [ ] **Mutability Levels**: Add `mutability` (immutable | slow | evolving | emergent) to entity traits in `entities.yaml`.
- [ ] **Drift Monitor**: Implement `src/omega/oracle/drift_monitor.py` to compare current behavioral state against baseline soul.
- [ ] **Hysteresis Tracking**: Integrate measured drift metrics into the `soul_evolution` section of `soul.yaml`.
- [ ] **Dream Pass**: Implement a scheduled (cron/timer) `dream_pass.py` to run L1 $\rightarrow$ L2 $\rightarrow$ L3 distillation on accumulated session gnosis.

## ⚙️ 2. Hardware Resonance (Zen 2 Optimization)
- [ ] **Core Steering**: Fully integrate `CpuOptimizer` with `taskset -cp 0-7` and `psutil.cpu_affinity` during engine boot.
- [ ] **System Tuning**: Add automated checks/settings for CPU Governor (`performance`) and Transparent Hugepages (`always`).
- [ ] **KV Cache Enforcement**: Ensure `q8_0` quantization is the default for all local providers in `ModelGateway`.
- [ ] **ZRAM Validation**: Add a check to `health_monitor.py` to verify ZRAM is active.

## 🏛️ 3. Architectural Hardening (Legacy Gold)
- [ ] **Circuit Breaker Integration**: Wire the `AsyncCircuitBreaker` from `R06` into the `ModelGateway` provider chain.
- [ ] **Omnidroid Lattice**: Implement the "Lattice Synthesis" (Root $\rightarrow$ Branch $\rightarrow$ Bridge) output format for the `Scribe` and `Researcher` agents.
- [ ] **Cognitive Tiering**: Implement automated model-routing based on the T1 (Reflex) $\rightarrow$ T2 (Reason) $\rightarrow$ T3 (Gnosis) weights.
- [ ] **Sovereign Guard Audit**: Run a final audit for `asyncio` imports and blocking I/O in the core `src/omega/` directory.

## 📡 4. Sovereign Infrastructure (Podman & WADs)
- [ ] **Namespace Isolation**: Enforce `wad_source` isolation in `EntityRegistry` to prevent cross-WAD entity collisions.
- [ ] **Collision Detection**: Add explicit warnings when an IWAD entity overrides a baseline entity.
- [ ] **Podman Guard**: Implement a pre-flight check to ensure `UserNS=keep-id` is active on all mounted volumes.
