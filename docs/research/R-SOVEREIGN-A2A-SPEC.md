# 🔱 R-SOVEREIGN-A2A-SPEC: Sovereign Agent-to-Agent Communication Specification
**Document ID**: R-SOVEREIGN-A2A-SPEC
**Status**: PROPOSED / ARCHITECTURAL BLUEPRINT
**Date**: 2026-06-11
**Author**: Sovereign Architect
**AP Token**: `AP-SOVEREIGN-A2A-SPEC-v1.0.0`

---

## 📝 Executive Summary

The **Sovereign A2A (S-A2A) Specification** defines the technical primitives required to transform the Omega Engine from a collection of independent agents into a **Cognitive Sovereign**. While standard A2A protocols focus on "Agent Opacity" (black-box delegation), S-A2A implements **Cognitive Continuity**.

This specification provides the blueprint to eliminate four critical systemic risks identified in the Sovereign Gap Analysis: **Cognitive Erasure**, **Taint Leakage**, **Ownership Ambiguity**, and **Alignment Drift**.

---

## 🛡️ 1. Gnosis-Aware Handoff
**Goal**: Eliminate **Cognitive Erasure** (the "re-discovery loop") where agents lose synthesized insights during delegation.

### 1.1 The Gnosis-Packet Schema
Every A2A handoff MUST include a `GnosisPacket`. Unlike a raw data dump, a Gnosis-Packet represents distilled intelligence.

```json
{
  "gnosis_packet": {
    "l1_narrative": "Chronological account of the task state, findings, and current progress.",
    "l2_insight": "Synthesized patterns, identified blind spots, and 'why' the current state exists.",
    "l3_universal_principle": [
      {
        "principle": "The timeless truth or engineering pattern applied.",
        "heritage_tag": "[id-soft: game-year] Pattern Name",
        "application": "How this principle governs the current solution."
      }
    ],
    "cognitive_load": "Estimated complexity for the recipient (Trivial | Standard | Complex)."
  }
}
```

### 1.2 The Hydration Sequence
The recipient agent MUST NOT begin execution until the following **Hydration Sequence** is complete:

1.  **Ingest**: Read the `GnosisPacket`.
2.  **Anchor**: Append L1 (Narrative) and L2 (Insight) to the local `session_gnosis.md` working memory.
3.  **Align**: Cross-reference the L3 Principles against the agent's own `soul.yaml`.
4.  **Update**: Update the Hivemind `focus_chain` to reflect the inherited state.
5.  **Acknowledge**: Post a confirmation to the Hub: *"Sovereign state hydrated. Principles aligned. Proceeding to [Next Step]."*

---

## ☣️ 2. Causal Taint Tracking
**Goal**: Eliminate **Taint Leakage**, where adversarial or low-trust input silently corrupts sovereign reasoning.

### 2.1 The Provenance Header
Every message transmitted via S-A2A MUST carry a `ProvenanceHeader`.

```json
{
  "provenance": {
    "source_agent": "agent_id",
    "trust_level": "Trusted | Untrusted | Tainted",
    "taint_path": ["agent_a", "agent_b"],
    "verification_sig": "ed25519_signature",
    "timestamp": "iso8601"
  }
}
```

### 2.2 Trust Level Definitions
- **`Trusted`**: Internal sovereign agents with verified identities and `soul.yaml` alignment.
- **`Untrusted`**: External agents, third-party MCP tools, or unverified sources.
- **`Tainted`**: Any input that has failed a `Skeptical Verifier` check or originates from a source marked as hostile.

### 2.3 Taint Propagation & Trigger
1.  **Propagation**: If any input in a reasoning chain is `Untrusted` or `Tainted`, the resulting output MUST be marked as `Tainted`.
2.  **Skeptical Trigger**: Any message with a `Tainted` or `Untrusted` header MUST be routed through the **Skeptical Verifier** (NLI-based Two-Source Rule) before it can be promoted to `Trusted` state.
3.  **Model Override**: `Tainted` inputs trigger an automatic `ModelGateway` override to use a high-rigor "Verification Model" instead of the default persona model.

---

## 🔐 3. Atomic Sovereignty Handshake
**Goal**: Eliminate **Ownership Ambiguity** and race conditions during task transfer.

### 3.1 The Lock-and-Transfer Primitive
Ownership of a sovereign task or resource is managed as an atomic state transition via the Omega Hub.

**State Machine**:
`Sovereign_Held` $\rightarrow$ `Transfer_Pending` $\rightarrow$ `Sovereign_Accepted`

### 3.2 The Handshake Workflow
1.  **Initiation**: Sender calls `hub.request_transfer(resource_id, target_agent)`.
2.  **Atomic Lock**: The Hub marks the resource as `Transfer_Pending` and acquires a `SovereignLock`. The sender's write-access is revoked.
3.  **Notification**: Target agent receives an S-A2A `KNOCK` containing the `GnosisPacket` and transfer request.
4.  **Verification**: Target agent performs the `Soul-Check` (see Section 4).
5.  **Commit**: If aligned, Target agent calls `hub.accept_transfer(resource_id)`. The Hub updates ownership to `Sovereign_Accepted` and releases the lock.
6.  **Failure**: If rejected, the Hub reverts state to `Sovereign_Held` for the sender.

---

## 🧩 4. Cognitive Alignment Gate
**Goal**: Eliminate **Alignment Drift**, ensuring subagents do not deviate from the Oversoul's core intent.

### 4.1 The Soul-Check Mechanism
The `Soul-Check` is a mandatory gate that occurs during the `Transfer_Pending` phase of the handshake.

**Mechanism**:
The recipient compares the `L3 Universal Principles` provided in the `GnosisPacket` against the `lessons` and `principles` defined in its own `soul.yaml`.

### 4.2 Alignment Verdicts
| Verdict | Criteria | Action |
| :--- | :--- | :--- |
| **`Aligned`** | Principles overlap, complement, or are neutral. | **Accept**: Proceed to `Sovereign_Accepted`. |
| **`Divergent`** | Logical conflict detected, but no Mandate violation. | **Negotiate**: Request a "Sovereign Alignment" phase to resolve the conflict before accepting. |
| **`Hostile`** | Principles violate Sovereign Mandates (M1-M15). | **Reject**: Immediately terminate transfer and log a `BoundaryViolationError`. |

---

## 🗺️ 5. Integration Map

### 5.1 SovereignHierarchy Integration
The `Soul-Check` ensures that the hierarchy is not just structural (who reports to whom) but cognitive (who thinks like whom). It prevents a subagent from accepting a task that would force it to violate its persona or the Oversoul's directives.

### 5.2 ModelGateway Integration
The `Taint Level` in the `ProvenanceHeader` acts as a routing signal for the `ModelGateway`.
- `Trusted` $\rightarrow$ Standard Persona Model.
- `Untrusted` $\rightarrow$ Standard Persona Model + Mandatory Verification Step.
- `Tainted` $\rightarrow$ High-Rigor Skeptical Model (Direct Override).

### 5.3 Omega Hub Integration
The Hub evolves from a simple message broker to a **Sovereignty Coordinator**, managing:
1.  The `SovereignLock` state machine.
2.  The `Provenance` signature registry.
3.  The atomic `transfer_sovereignty` operation.

---

## 🏛️ Temple-Grade Compliance
- **M1 AnyIO**: All Hub-side lock operations and A2A transfers MUST be implemented using `anyio.Lock` and `anyio.to_thread.run_sync`.
- **M2 Firewall**: This protocol is implemented entirely within the Hub and Client layers. No logic is added to the Core Engine's internal inference loops.
- **M13 Temple-Grade**: This design specifies explicit inputs (`GnosisPacket`, `ProvenanceHeader`), explicit outputs (`Alignment Verdict`, `Sovereign_Accepted`), and explicit error states (`BoundaryViolationError`, `TaintLeakageError`).
