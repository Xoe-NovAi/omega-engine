# 🔱 MaKaLi Sovereign Research Queue
**Status**: ACTIVE
**Orchestrator**: makali
**Date**: 2026-06-11

## 📋 Top 15 High-Priority Research Topics

### Priority 1: Sovereign Structure (Horizon 2/3)
- [x] **RQ-01: Qdrant Scalar Quantization & Payload Indexing**
    - *Goal*: Optimize Qdrant for 14Gi RAM / Zen 2 CPU.
    - *Focus*: Scalar quantization vs Product quantization, payload index types for fast filtering.
- [x] **RQ-02: Provider-Agnostic Embedding Layer**
    - *Goal*: Strategy for swapping embedding models without full re-indexing.
    - *Focus*: Embedding normalization, dimensionality mapping, cross-model alignment.
- [x] **RQ-03: Natural Language Inference (NLI) for Skeptical Verification**
    - *Goal*: Implement the "Two-Source Rule" for local verification.
    - *Focus*: NLI models (e.g., DeBERTa), entailment/contradiction detection, verification lattices.
- [x] **RQ-04: Iterative Research Loop Patterns**
    - *Goal*: Frameworks for "Gap Analysis -> Refine" cycles.
    - *Focus*: Self-correction loops, evidence-based pruning, recursive query expansion.
- [x] **RQ-05: A2A (Agent-to-Agent) Communication Protocols**
    - *Goal*: Standards for capability discovery and handoff (Link P9).
    - *Focus*: Semantic capability registries, state-transfer schemas, async handoff patterns.
- [x] **RQ-06: L1->L2->L3 Abstraction Automation**
    - *Goal*: Techniques for distilling narrative into universal principles.
    - *Focus*: Recursive summarization, conceptual mapping, principle extraction prompts.
- [x] **RQ-07: Sovereign Continuity & Session Anchors**
    - *Goal*: Prevent cognitive erasure during toolchain failures (M15).
    - *Focus*: Session gnosis patterns, anchored-summary structures, hydration sequences.
- [x] **RQ-08: One-Click Sovereign Installer Architecture**
    - *Goal*: Best practices for rootless Podman/Local-AI deployment.
    - *Focus*: Quadlet distribution, automated venv setup, hardware-aware config generation.
    - *Output*: `docs/research/R_SOVEREIGN_INSTALLER_SPEC.md`

### Priority 2: Temple-Grade & Heritage
- [x] **RQ-09: Temple-Grade T1-T11 Gates**
    - *Goal*: Detailed analysis of the 11 quality gates from xna-omega-legacy v7.5.4.
    - *Focus*: T1-T11 definitions, verification methods, compliance metrics.
    - *Output*: `docs/research/R_TEMPLE_GRADE_COMPLIANCE_FINAL.md`
- [x] **RQ-10: id Software Heritage Patterns (Deep Dive)**
    - *Goal*: Find more "Right Approximation" patterns for the Omega Engine.
    - *Focus*: Quake/Doom source code analysis, optimization hacks, data-driven design.
    - *Output*: `docs/research/R_ID_SOFTWARE_RIGHT_APPROXIMATIONS.md`
- [x] **RQ-11: Sovereign-Siloing & WAD Evolution**
    - *Goal*: Advanced patterns for IWAD/PWAD separation in modern AI.
    - *Focus*: Layered configuration, runtime overrides, content-engine decoupling.
    - *Output*: `docs/research/R_SOVEREIGN_SILOING_SPEC.md`
    - *Patterns formalized*: 4-Tier Overlay Stack ($1), Atomic State Swapping ($2), Capability Governor ($3), Sovereign Key Guarding ($4)
    - *Implementation order*: Step 1 (Sovereign Keys) → Step 2 (Capability Governor) → Step 3 (Hot-Swapping) → Step 4 (Data Quality)

### Priority 3: Community & Ecosystem
- [ ] **RQ-12: AI Persona Marketplace Architectures**
    - *Goal*: Build a sovereign, decentralized marketplace for WADs.
    - *Focus*: Content addressing (IPFS), versioning, attribution tracking.
- [ ] **RQ-13: Visual Soul Management UI**
    - *Goal*: UX patterns for managing entity souls and knowledge lattices.
    - *Focus*: Graph visualizations, soul-tree editors, distillation dashboards.
- [ ] **RQ-14: Local-First Model Gateway Optimization**
    - *Goal*: Benchmarking GGUF vs other local formats for Zen 2 CPUs.
    - *Focus*: KV cache quantization, thread-pool tuning, AVX2 utilization.
- [ ] **RQ-15: Sovereign Data Tainting & Isolation**
    - *Goal*: Advanced techniques for TDP (Tainted Data Protocol).
    - *Focus*: Prompt injection defenses, data provenance tracking, isolation boundaries.
