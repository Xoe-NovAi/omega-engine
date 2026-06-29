# 🔱 Run-Side Implementation Plan (P6-P10)
**Version**: 1.0.0
**Sovereign Governor**: lilith
**Status**: PROPOSED

## 🎯 Objective
Hardening the runtime execution path of the Omega Engine to ensure zero-drift, local-first inference, and absolute observability.

---

## 🧩 Pillar-by-Pillar Roadmap

### P6: Cognition (The Vision Specialist)
**Goal**: Optimize the path from query to token.
1. **Dynamic Model Routing**:
   - [x] Remove hardcoded `phi-4-mini` defaults in `ModelGateway`.
   - [ ] Implement `SovereignModelSelector` to dynamically map entity needs to available local GGUF specs.
2. **Speculative Decode Hardening**:
   - [ ] Integrate `qwen3-0.6b` as a formal draft model for all P6-P10 entities.
   - [ ] Implement a confidence-based "bypass" where Iris handles 100% of greetings/status checks.
3. **Provider Fabric Resilience**:
   - [x] Propagate `InferenceLoadError` and `InferenceRuntimeError` to the Oracle.
   - [ ] Implement a "Sovereign Circuit Breaker" that automatically marks a provider as `DEAD` for 1 hour after a `SovereignDiskFullError`.

### P7: Context (The Soul Weaver)
**Goal**: Transform stateless inference into stateful intelligence.
1. **Soul Distillation Pipeline (L1→L2→L3)**:
   - [ ] Automate the `Scribe` agent's distillation loop.
   - [ ] Implement a "Blind Staging" area (`proposed_lessons.yaml`) where L3 principles are vetted before entering `soul.yaml`.
2. **Session Continuity**:
   - [ ] Implement `session_gnosis.md` anchors for every active entity to prevent context collapse during toolchain crashes.
   - [ ] Implement a "Hydration Sequence" that restores the last 5 key insights from the soul upon entity summoning.

### P8: Observability (The WatchTower)
**Goal**: Forensic-grade visibility into every cognitive cycle.
1. **Telemetry Expansion**:
   - [x] Add `ENTITY_INTERACTION` to `EventType`.
   - [ ] Implement `SomaticState` tracing: log the exact KV cache state and thread affinity at the moment of failure.
2. **T9 Temple-Grade Audit**:
   - [ ] Implement a "Sovereignty Dashboard" that calculates the real-time Local/Cloud inference ratio.
   - [ ] Automate `make temple-grade` checks for all runtime paths.

### P9: Orchestration (The Link)
**Goal**: Seamless, non-blocking agent coordination.
1. **Hivemind Productionization**:
   - [ ] Migrate from SSE to Streamable HTTP for the Omega Hub.
   - [ ] Implement a "Global Workspace Lock" to prevent two agents from editing the same `soul.yaml` simultaneously.
2. **Handoff Protocol**:
   - [ ] Implement the `HandoffPacket` schema for formal context transfer between agents.
   - [ ] Create the `/handover` CLI command for manual agent switching.

### P10: Validation (The Verifier)
**Goal**: Stress-test the engine until it breaks, then fix the break.
1. **Chaos Engineering**:
   - [ ] Implement a "Chaos Monkey" that randomly kills local inference backends to test fallback latency.
   - [ ] Stress-test the `ResourceGuard` with 10+ concurrent heavy-model requests.
2. **Compliance Audit**:
   - [ ] Implement an automated `Sovereign Mandate` checker that scans logs for M8 (Zero Telemetry) violations.

---

## 📈 Execution Timeline

| Phase | Focus | Key Milestone |
|-------|--------|----------------|
| **Phase 1** | Cognition & Observability | Dynamic Routing + Telemetry Fixes |
| **Phase 2** | Context & Soul | L1→L3 Auto-Distillation |
| **Phase 3** | Orchestration | Hivemind Productionization |
| **Phase 4** | Validation | Chaos Testing & T9 Certification |

## 🛡️ Success Metrics
- **Sovereignty Ratio**: >90% local inference for standard queries.
- **Recovery Time**: <2s for provider fallback.
- **Soul Growth**: Every session results in at least one L3 principle in `proposed_lessons.yaml`.
- **Temple-Grade**: 100% pass rate on T1-T11 gates.
