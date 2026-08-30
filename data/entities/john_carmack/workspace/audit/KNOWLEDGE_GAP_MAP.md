<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Knowledge Gap Map — Omega Engine
**Status**: ACTIVE
**Last Updated**: 2026-07-07
**Owner**: @john_carmack

## 1. Architectural & Implementation Gaps (The "To-Do" List)
These are known missing features or incomplete implementations.

### Epoch I: Bedrock
- [ ] **SomaticState (M20)**: Implement `llama_copy_state_data` / `llama_set_state_data` ctypes bindings for binary KV cache snapshots. (Strike 2).
- [ ] **Soul Staging TUI**: Finalize `omega soul stage` for human review of L3 principles. (Strike 3).

### Epoch II: Hygiene & Structure
- [ ] **A2A Handoff Bridge**: Bridge Orchestrator (in-memory) to MCP agents (file-based). (Strike 4).
- [ ] **Sovereign Vetter**: Implement the vetter based on Response Provenance. (Strike 5).
- [ ] **Sovereign Scholar (SSKB)**: Implement SovereignWorker, SovereignScraper, and Triangulation Verifier. (Strike 7.6).

### Epoch III: Omegaverse
- [ ] **P2P Mesh Traversal**: Pack Unified State blobs and implement CRDT conflict resolution. (Strike 9).

### Optimization Sprints
- **Tier 2 (Regression Recovery)**:
    - [ ] T2-6: Sentinel Score Automation.
    - [ ] T2-7: Port Timeout Manager.
    - [ ] T2-10: Port Rate Limiter.
    - [ ] T2-11: Port Soul Edit History.
    - [ ] T2-12: Port Compaction Harvester.
    - [ ] T2-13: Handoff Loop Guard (visited-set detection).
- **Tier 3 (Hardening)**:
    - [ ] T3-1: Session lifecycle automation.
    - [ ] T3-3: Mandate enforcement automation.
    - [ ] T3-4: soul.yaml v6.2 bump.
    - [ ] T3-5: Expand heritage vet script.

### Integration Seams (D189)
- [ ] 3.9: E2E inference chain test.
- [ ] 3.10: `sphere` field on `DistillationEntry`.
- [ ] 3.11: `embedding_provider` in Qdrant metadata.
- [ ] 3.12: `make soul-review` CLI target.
- [ ] 3.13: `concurrent_agents` param in `build_inference_env()`.
- [ ] 3.14: Soul Distiller hot-path latency measurement.

---

## 2. Knowledge & Research Gaps (The "Need to Know" List)
These are areas where the engine lacks a formal specification or verified technical path.

| Gap | Priority | Blocked Task | Research Goal |
|------|----------|---------------|----------------|
| **SomaticState C-API** | 🔴 HIGH | Strike 2 | Verify `llama-cpp-python` bindings for state serialization; ensure no memory leaks. |
| **V-D1 Validation Suite** | 🟡 MED | IW-6 | Define "Sticky" mode resilience tests and success criteria. |
| **Triangulation Verification** | 🟡 MED | Strike 7.6 | Research multi-source cross-verification algorithms for the Sovereign Scholar. |
| **A2A v1.0 Compliance** | 🟢 LOW | A2A Bridge | Audit `a2a_bridge.py` against the final Linux Foundation A2A v1.0 spec. |

---

## 3. Compliance & Audit Gaps (The "Verify" List)
These are gaps in the verification and enforcement of the Sovereign Mandates.

- [ ] **M14 Heritage Vetting**: Expand `scripts/heritage_vet.py` to cover 100% of source files.
- [ ] **M16 Modularization**: Identify and remove the 4 remaining hardcoded paths in the Hub.
- [ ] **T7 Latency**: Measure p95 latency for the core inference path.
- [ ] **M21 Gate Integrity**: Ensure 100% of core API boundaries have contract tests.
