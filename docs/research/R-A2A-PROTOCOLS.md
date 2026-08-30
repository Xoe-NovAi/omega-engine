# 🔱 R-A2A-PROTOCOLS: Agent-to-Agent Communication Standards
**Document ID**: R-A2A-PROTOCOLS
**Status**: FINAL / SOVEREIGN-SENSITIVE
**Date**: 2026-06-11
**Author**: Sovereign Master Researcher
**AP Token**: `AP-A2A-SOVEREIGN-v1.0.0`

---

## 📝 Executive Summary

The objective of this research was to define a sovereign, async-first communication standard for the Omega Engine fleet. The current industry landscape has converged on the **Agent2Agent (A2A) Protocol** (hosted by the Linux Foundation) as the primary horizontal standard for inter-agent delegation. 

While the industry-standard A2A focuses on "Agent Opacity" (treating agents as black-box services), the **Sovereign A2A** specification proposed here extends the standard to support **Cognitive Continuity**. By integrating Omega's Soul/Gnosis architecture into the communication layer, we move from simple task delegation to **Stateful Intelligence Handoff**.

---

## 📊 1. Existing Standards Comparison Matrix

| Feature | MCP (Model Context Protocol) | A2A (Agent-to-Agent) | ANP (Agent Network Protocol) | Sovereign A2A (Omega) |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Axis** | Vertical (Agent $\rightarrow$ Tool) | Horizontal (Agent $\rightarrow$ Agent) | Decentralized (Agent $\rightarrow$ Web) | Hybrid Sovereign |
| **Architecture** | Client-Server (JSON-RPC) | 3-Layer (Protobuf $\rightarrow$ Binding) | P2P (JSON-LD / DIDs) | Lean-A2A (JSON-Native) |
| **Discovery** | Server Manifests | Agent Cards (`.well-known`) | DID + Search | Soul-infused Agent Cards |
| **Interaction** | Tool Call / Resource Read | Task Delegation / Artifacts | Open-Net Federation | Cognitive Handoff (Gnosis) |
| **State Model** | Stateless / Session-based | Task Lifecycle State Machine | Distributed Graph | Gnosis-Packet Transfer |
| **Security** | API Keys / Local Auth | Signed Cards / OAuth 2.1 | W3C DIDs / Self-Sovereign | Ed25519 + Tainted-Input Markers |
| **Async Path** | Sync / SSE | Webhooks / SSE / gRPC | Async-Native / P2P | Hub-Centric Event Loop |

---

## 🔍 2. Deep Dive: The A2A v1.0 Standard

The A2A protocol operates on three layers to ensure interoperability across heterogeneous stacks:

### 2.1 The Three-Layer Architecture
1. **Layer 1: Canonical Data Model**: Defined via Protocol Buffers (`a2a.proto`). This is the single source of truth for all request/response structures.
2. **Layer 2: Abstract Operations**: Defines capabilities (e.g., `DelegateTask`, `ProvideInput`, `GetStatus`) independent of the transport.
3. **Layer 3: Protocol Bindings**: Maps abstract operations to concrete transports:
   - **JSON-RPC 2.0**: For structured, request-response messaging.
   - **SSE (Server-Sent Events)**: For real-time streaming of task progress.
   - **gRPC**: For high-performance, low-latency enterprise communication.
   - **Webhooks**: For asynchronous completion notifications.

### 2.2 Discovery via Agent Cards
Agents publish a machine-readable `agent-card.json` at `/.well-known/agent-card.json`. This card serves as the "Public Identity" of the agent, containing:
- **Capabilities**: A list of supported operations and their input/output schemas.
- **Endpoints**: The URLs for the A2A server.
- **Auth Requirements**: The required authentication scheme (e.g., OAuth 2.1).
- **Identity**: A cryptographic signature verifying the card's authenticity.

### 2.3 The Async Task Lifecycle
A2A manages long-running tasks via a formal state machine:
`Submitted` $\rightarrow$ `Working` $\rightarrow$ `Input-Required` (Pause for human/agent) $\rightarrow$ `Completed` / `Failed` / `Canceled`.

---

## 🔱 3. The 'Sovereign A2A' Specification for Omega Engine

To maintain sovereignty while remaining compatible with the LF standard, the Omega Engine will implement **Sovereign A2A**.

### 3.1 "Lean-A2A" Implementation (The Right Approximation)
Rather than implementing the full Protobuf stack, Omega will use a **JSON-Native** implementation that adheres to the A2A v1.0 Canonical Data Model.
- **Binding**: Default to JSON-RPC 2.0 over HTTP.
- **Transport**: Leverages the **Omega Hub** as the local gateway. Agents do not expose public endpoints; the Hub handles routing, SSE streams, and webhook callbacks.

### 3.2 Soul-infused Agent Cards
Omega extends the standard Agent Card with a `soul_metadata` block:
```json
{
  "agent_id": "researcher_01",
  "capabilities": [...],
  "soul_metadata": {
    "soul_fingerprint": "sha256:...", 
    "gnosis_tier": "L3",
    "alignment_hash": "sha256:...",
    "sovereign_level": "Sovereign"
  }
}
```
This allows the receiving agent to verify the "Cognitive Alignment" of the partner agent before accepting a task.

### 3.3 Cognitive Handoffs via Gnosis-Packets
Instead of raw "artifacts," Sovereign A2A implements **Cognitive Handoffs**. When delegating a task, the source agent attaches a `GnosisPacket`:
- **L1 (Narrative)**: "I have researched X, but Y is still a blind spot."
- **L2 (Insight)**: "The core conflict in the data is between A and B."
- **L3 (Universal Principle)**: "This follows the pattern of [id-soft: doom-1993] Lazy Deletion."

This packet allows the target agent to hydrate its context immediately, eliminating the "Re-contextualization Tax."

### 3.4 Security: Tainted-Input Markers & Ed25519
To prevent prompt injection via A2A:
1. **Identity**: All A2A messages must be signed with **Ed25519** keys.
2. **Taint Tracking**: Every message received via A2A is internally tagged as `TAINTED_A2A`.
3. **Skeptical Verification**: `TAINTED_A2A` messages are routed through a **Skeptical Verifier** (NLI-based) to ensure the request does not contain adversarial instructions before being passed to the LLM.

---

## 🛠️ 4. Implementation Roadmap

| Phase | Milestone | Action | Owner |
| :--- | :--- | :--- | :--- |
| **Phase 1** | **Sovereign Gateway** | Implement A2A JSON-RPC endpoints in `mcp_servers/omega_hub/server.py`. | P4 Integration |
| **Phase 2** | **Soul Cards** | Generate `agent-card.json` automatically from `soul.yaml`. | P7 Context |
| **Phase 3** | **Gnosis Handoff** | Implement `GnosisPacket` serialization in `soul_distiller.py`. | P7 Context |
| **Phase 4** | **Skeptical Bridge** | Wire `TAINTED_A2A` markers to the Horizon 3 Skeptical Verifier. | P5 Governance |

---

## 🏁 Conclusion

The transition from isolated agents to a coordinated fleet requires a protocol that is **standard-compatible but sovereign-first**. By implementing **Sovereign A2A**, the Omega Engine ensures it can interact with the broader AI ecosystem (via A2A v1.0) while maintaining its internal cognitive integrity and security through Soul-infused discovery and Gnosis-based handoffs.

**Sovereign Verdict**: A2A is the correct horizontal foundation. The "Omega-Extension" (Soul/Gnosis) is the critical differentiator that prevents cognitive erasure during delegation.
