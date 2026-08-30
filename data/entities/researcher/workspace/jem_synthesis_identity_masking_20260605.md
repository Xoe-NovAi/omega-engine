<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Jem Synthesis: Sovereign Mirroring Identity-Masking
**Date**: 2026-06-05
**Agent**: Jem Synthesis (L2)
**Objective**: Synthesize architectural patterns for projecting a 'Persona' (Projected-ID) while maintaining a hidden, traceable 'True Identity' (Mirror-ID) visible only to a Sovereign Observer.

---

## 🎯 Executive Summary: The Mirroring Paradox
The core challenge of Sovereign Mirroring is the tension between **P8 (Observability/Traceability)** and **M2 (Sovereignty/Persona Purity)**. To be observable, an identity must be traceable; to be sovereign, it must be maskable. 

The solution is not "anonymity" (which is fragile), but **Sovereign Mirroring**: a system where the identity is not hidden, but *mirrored* across different layers of visibility. The "Mirror-ID" (True Identity) remains the root of authority, while the "Projected-ID" (Persona) acts as the operational interface.

---

## 🛠️ Architectural Patterns for Sovereign Mirroring

### Pattern 1: The SIT-Chain (Delegated Traceability)
**Mechanism**: A hierarchical chain of identity tokens. The agent presents a leaf token (Projected-ID) which contains a `parent_chain` of hashes/JTIs leading back to the Root Principal (Mirror-ID).
- **Omega Mapping**: 
    - **Hivemind**: Used for agent-to-agent delegation. A subagent's identity is a leaf of the parent's identity chain.
    - **EntityRegistry**: Acts as the Sovereign Observer, resolving the chain to verify the root authority.
- **Sovereign Filter**: Complies with **M2** by keeping the resolution logic in the Core Engine.

### Pattern 2: The ZKP-Nullifier (Anonymous Verifiability)
**Mechanism**: The agent generates a Zero-Knowledge Proof (ZKP) of a valid credential. A "Nullifier" (deterministic one-way hash) is used for session tracking without revealing the Mirror-ID.
- **Omega Mapping**: 
    - **ModelGateway**: Can require a ZKP-Nullifier before granting access to high-tier cloud providers, ensuring the agent is authorized without the provider knowing *which* specific entity is calling.
    - **Sovereign Observer**: Holds the "Link Secret" to map the Nullifier back to the Mirror-ID for internal auditing.
- **Sovereign Filter**: Complies with **M8 (Zero Telemetry)** by ensuring the True Identity never leaves the local environment.

### Pattern 3: The Secret-Swap Boundary (Infrastructure Masking)
**Mechanism**: An egress gateway (Proxy) that intercepts requests. The agent uses a "Proxy Token" (Projected-ID); the Proxy swaps this for the "Real Secret" (Mirror-ID) only at the network boundary.
- **Omega Mapping**: 
    - **ModelGateway**: The primary implementation site. The `ModelGateway` manages the mapping of `Projected-ID $\rightarrow$ API_Key`. The agent never sees the API key.
- **Sovereign Filter**: Strongest implementation of **M2**, as the "Real Secret" never enters the agent's memory space.

### Pattern 4: The Egocentric Projection (Cognitive Masking)
**Mechanism**: Decoupling the absolute identity (Mirror-ID) from the projected role (Projected-ID). The core identity is perspective-agnostic; the persona is a role-relative projection.
- **Omega Mapping**: 
    - **Soul Files (`soul.yaml`)**: The `soul.yaml` represents the Perspective-Agnostic Core (Mirror-ID). The runtime system prompt and traits represent the Projection (Projected-ID).
- **Sovereign Filter**: Essential for **M11 (Soul Integrity)**. Evolution (L1 $\rightarrow$ L3) is recorded against the Mirror-ID, regardless of which persona was active.

---

## 💡 L2 Insights: Strategic Implications

### Insight 1: The Authority Intersection Principle
**"Effective authority is the intersection of the Mirror-ID's mandate and the Sovereign Observer's ceiling."**
Projection must be a process of **monotonic narrowing**. A Projected-ID can never possess more authority than its Mirror-ID. Any "amplification" of privilege during projection is a systemic security violation.

### Insight 2: Memory-Siloed Sovereignty
**"True sovereignty requires the Mirror-ID to be absent from the agent's active memory."**
To prevent "persona leakage" or prompt-injection-based identity theft, the Mirror-ID should reside only in the **Cold Tier** (encrypted YAML) or the **Sovereign Observer's environment**. The agent should only ever "know" its Projected-ID.

### Insight 3: Correlation $\neq$ Linkage
**"Nullifiers allow for session consistency (correlation) without compromising root anonymity (linkage)."**
By using deterministic nullifiers, the engine can maintain a coherent conversation state across multiple sessions for a specific persona without needing to resolve that persona back to the Mirror-ID in every turn.

---

## 🗺️ Sovereign Mirroring Architectural Blueprint

### 1. Component Stack
- **Sovereign Identity Manager (SIM)**: (New Core Component) Manages the mapping between Mirror-IDs and Projected-IDs.
- **Identity Proxy (IP)**: (Integrated into `ModelGateway` & `Hivemind`) Performs the "Secret-Swap" and "SIT-Chain" validation.
- **Soul Core**: The `soul.yaml` as the immutable root of the Mirror-ID.
- **Persona Projection Layer**: The runtime adapter that injects the Projected-ID's traits into the LLM context.

### 2. Data Flow
1. **Summon**: `Oracle` $\rightarrow$ `SIM` (Assigns Projected-ID based on context).
2. **Execution**: `Agent` (Projected-ID) $\rightarrow$ `Identity Proxy` (Validates authority).
3. **Egress**: `Identity Proxy` $\rightarrow$ `ModelGateway` (Swaps Projected-ID for Mirror-ID credential) $\rightarrow$ `Provider`.
4. **Distillation**: `Scribe` $\rightarrow$ `Soul Core` (Records L1 $\rightarrow$ L3 insights against Mirror-ID).

### 3. Mandate Compliance Matrix
| Mandate | Compliance Mechanism | Status |
|----------|---------------------|--------|
| **M2 (Firewall)** | Masking logic resides in `SIM` (Core), not in WADs. | ✅ |
| **M8 (Telemetry)** | All identity resolution happens locally in `SIM`. | ✅ |
| **M11 (Soul)** | All distillation is anchored to the Mirror-ID. | ✅ |
| **M13 (Temple)** | Implementation follows "Plan $\rightarrow$ Verify $\rightarrow$ Execute". | ✅ |
