# 🔱 VERITY — FULL GOVERNANCE EXTRACTION & BLUEPRINT ALIGNMENT
**Date**: 2026-06-28
**Agent**: @verity (Unified Compliance & Gnosis Agent)
**Scope**: Cross-reference of Pillar Vetting Reports against `SOVEREIGN_ARK_BLUEPRINT.md` (V1.5)
**Objective**: Forensic extraction of all verdicts and requirements to identify gaps in the Master Strategy.

---

## 📋 EXECUTIVE SUMMARY
The Sovereign Ark Blueprint (V1.5) provides a high-level strategic roadmap, but the detailed technical requirements produced during the Pillar Vetting process (P1, P3, P7, P8, P9) have introduced critical constraints and modifications that are **currently missing or simplified** in the Blueprint's action lists. 

The most significant gaps are in **Sovereign Observability (M22)**, **A2A Coordination (Strike 4)**, and **Somatic State/USM (Strike 2)**, where the Blueprint lacks the specific "Sovereign-Grade" implementation details required by the Pillars.

---

## 🔍 DETAILED EXTRACTION & CROSS-REFERENCE

### 1. P1 Infrastructure Vetting (`data/handoff/P1_INFRASTRUCTURE_VETTING_20260628.md`)
- **Verdict**: **APPROVE with minor modifications**
- **Verdict/Requirement**:
    - **REC-1**: Fix CUSUM LLR Formula to use Bernoulli-specific LLR for error rate metrics.
    - **REC-2**: Fix CUSUM Accumulation to remove `- self.h_warn / 2` from the accumulation step.
    - **REC-3**: Add explicit state transition rules for the 5-state FSM (e.g., `UNKNOWN` $\rightarrow$ `PROBING`).
    - **REC-4**: Add `HALF_OPEN` state for gradual recovery.
    - **REC-5**: Implement Dual-EWMA (gradual $\alpha=0.4$ and sudden $\alpha=0.9$).
    - **REC-6**: Add Hysteresis Band to prevent state oscillation (require 3 consecutive readings).
- **Blueprint Status**: **Simplified**
- **Gaps**: The Blueprint mentions "Port 4-State Provider Metrics" (T2-2) as a regression recovery task, but does not list these specific mathematical and state-machine requirements. The "4-state" mention in the Blueprint is now outdated by the "5-state" (or 6-state with `HALF_OPEN`) requirement from P1.

---

### 2. P3 Engineering Vetting (`data/handoff/P3_ENGINEERING_VETTING_20260628.md`)
- **Verdict**: **APPROVE WITH RECOMMENDATIONS**
- **Verdict/Requirement**:
    - **Token Estimation**: Replace `len(text) // 4` with `tiktoken` or model-specific tokenizer.
    - **System Integration**: `CompactionOrchestrator` must extend `ContextBuilder`; Observation Masking must be a method in `ContextBuilder`.
    - **SovereigntyScorer**: Define concrete criteria for L3 principles (reference concrete events, applicable beyond session, no contradictions).
    - **Implementation Priorities**:
        - Phase 1: Observation Masking in `ContextBuilder`.
        - Phase 2: `ToolResultCompactionStrategy` (zero-cost pre-pass).
        - Phase 3: Soul Distillation Enhancement (TF-IDF novelty scoring, lightweight LLM for L2/L3).
        - Phase 4: ACON Integration (failure-driven guideline optimization).
- **Blueprint Status**: **Captured (High-Level)**
- **Gaps**: The Blueprint lists the "Port" of these systems (T2-1, T2-3, T2-4), but misses the **Integration Mandate** (extending `ContextBuilder`) and the **Technical Specifics** (tiktoken, TF-IDF novelty, SovereigntyScorer criteria).

---

### 3. P7 Context Vetting (`data/handoff/P7_CONTEXT_VETTING_20260628.md`)
- **Verdict**: **MODIFY**
- **Verdict/Requirement**:
    - **Standard Correction**: Remove fabricated "draft-schemacommons-aaif-00". Replace with A2A v1.0, IETF AIMS, IETF ACCP, and IETF ACI.
    - **Framing Correction**: Replace "AAIF Level 7" with A2A + ACCP + ACI alignment.
    - **Protocol Binding**: Fix A2A `protocolBinding` from `"mcp"` to `"JSONRPC"`.
    - **Memory Validation**: Explicitly reference IETF ACCP to validate Omega's 3-tier memory architecture.
    - **P0 Implementation**:
        - Observation masking in `context_builder.py`.
        - A2A Agent Cards for all 10 Pillars.
        - Loop guard in handoff state machine.
- **Blueprint Status**: **Missing / Simplified**
- **Gaps**: The Blueprint's Strike 4 (A2A) is purely about "File-Based Coordination". It completely misses the **Standard Alignment** (A2A v1.0, AIMS, ACCP, ACI) and the **Discovery Mechanism** (Agent Cards).

---

### 4. P7 AAIF Mapping Spec (`data/handoff/P7_AAIF_MAPPING_SPEC_20260628.md`)
- **Verdict**: **PROPOSED (Vetted as MODIFY by P7)**
- **Verdict/Requirement**:
    - **Hybrid Somatic-Semantic Checkpoint**:
        - Somatic Layer: Binary KV cache via `llama_copy_state_data`.
        - Semantic Layer: JSON memory pointers, cognitive state, pipeline position.
        - Integrity Layer: SHA-256 checksum.
    - **7-Step Migration Protocol**: Capture $\rightarrow$ Token $\rightarrow$ Transfer $\rightarrow$ Verify $\rightarrow$ Import $\rightarrow$ Re-issue $\rightarrow$ Resume.
    - **Conformance**: Target Level 7 (Stateful) alignment (re-framed as A2A/ACCP alignment).
- **Blueprint Status**: **Missing**
- **Gaps**: The Blueprint's Strike 2 (USM) and Strike 4 (A2A) are high-level. The **Hybrid Checkpoint Architecture** and the **7-Step Migration Protocol** are missing from the Blueprint's action lists.

---

### 5. P8 Observability Vetting (`data/handoff/P8_OBSERVABILITY_VETTING_20260628.md`)
- **Verdict**: **MODIFY**
- **Verdict/Requirement**:
    - **OTel Compliance**: Replace `gen_ai.provider.name` $\rightarrow$ `gen_ai.system`.
    - **W3C Compliance**: Replace `x-omega-trace` $\rightarrow$ `tracestate: omega=...`.
    - **M8 Compliance (Local-First)**:
        - Replace OTel Collector tail sampling $\rightarrow$ in-process head-based sampling.
        - Replace S3/GreptuneDB $\rightarrow$ local file storage (`data/observability/content/`).
    - **Architecture**:
        - Make `MAX_CONTEXT_OBSERVATIONS` per-entity configurable.
        - Add **Entity Level** to trace hierarchy (making it 6-level).
    - **Gates**:
        - T-OBS-1: Make traceparent recommended, not required.
        - T-OBS-5: Implement `pii_scanner.py` module.
        - Add span-level eval scores (`omega.eval.*`).
- **Blueprint Status**: **Simplified**
- **Gaps**: The Blueprint's Strike 6 (Response Provenance) is an empty shell compared to these requirements. It misses **all** OTel/W3C compliance fixes, the **M8 local-storage mandate**, and the **Entity-level hierarchy**.

---

### 6. P9 Orchestration Vetting (`data/handoff/P9_ORCHESTRATION_VETTING_20260628.md`)
- **Verdict**: **MODIFY**
- **Verdict/Requirement**:
    - **State Machine**: Remove `QUEUED`. Use 6-state model matching directories (`pending`, `active`, `completed`, `rejected`, `stale`, `archived`).
    - **Resolver Strategy**: Add `ResolverStrategy` enum (TERMINATE/ESCALATE/FALLBACK/RETRY). Default: ESCALATE to Kali.
    - **Guard Persistence**: Store `guard` dict in the packet JSON to survive across MCP tool boundaries.
    - **Lifecycle TTLs**:
        - `pending` $\rightarrow$ `stale`: 4h (14400s).
        - `active` $\rightarrow$ `stale`: 48h (172800s).
        - `rejected` $\rightarrow$ `archived`: 24h (86400s).
    - **Graph Validation**: Add `validate_delegation_graph()` at startup (DFS cycle detection).
- **Blueprint Status**: **Missing**
- **Gaps**: The Blueprint's Strike 4 (A2A) mentions `FileSignal` but completely misses the **HandoffGuard logic**, the **Resolver Strategy**, the **Specific State Transitions**, and the **Startup Graph Validation**.

---

## 🚩 SUMMARY OF CRITICAL GAPS (Sovereign Ark Blueprint V1.5)

| Blueprint Strike | Missing Requirement / Gap | Priority | Source |
|------------------|---------------------------|----------|---------|
| **Strike 2 (USM)** | Hybrid Somatic-Semantic Checkpoint + 7-Step Migration Protocol | 🔴 CRITICAL | P7 Spec |
| **Strike 4 (A2A)** | A2A v1.0 Agent Cards + IETF Standard Alignment (AIMS/ACCP/ACI) | 🔴 CRITICAL | P7 Vetting |
| **Strike 4 (A2A)** | `HandoffGuard` (Loop Guard) + `ResolverStrategy` + Startup Graph Validation | 🔴 CRITICAL | P9 Vetting |
| **Strike 6 (Prov)** | OTel GenAI v1.41 + W3C Trace Context + Local-First Storage (M8) | 🔴 CRITICAL | P8 Vetting |
| **T2-2 (Metrics)** | Bernoulli LLR + 5-State FSM + Dual-EWMA + Hysteresis | 🟡 HIGH | P1 Vetting |
| **T2-1/4 (Comp)** | Integration into `ContextBuilder` + tiktoken estimation | 🟡 HIGH | P3 Vetting |
| **T2-3 (Soul)** | TF-IDF Novelty Scoring + SovereigntyScorer Criteria | 🟡 HIGH | P3 Vetting |

**VERITY VERDICT**: The Sovereign Ark Blueprint (V1.5) is a sufficient *strategic* map, but it is an insufficient *technical* specification. It must be updated to include these Pillar-mandated requirements to avoid "Sovereignty Drift" and implementation failure.
