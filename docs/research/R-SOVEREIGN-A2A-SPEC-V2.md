# 🔱 R-SOVEREIGN-A2A-SPEC-V2: Hardened Sovereign Agent-to-Agent Communication Specification
**Document ID**: R-SOVEREIGN-A2A-SPEC-V2
**Status**: FINAL / TEMPLE-GRADE
**Date**: 2026-06-11
**Author**: Sovereign Architect
**AP Token**: `AP-SOVEREIGN-A2A-SPEC-V2.0.0`

---

## 📝 Executive Summary

The **Sovereign A2A (S-A2A) Specification v2** is a complete redesign of the agent coordination protocol, specifically engineered to eliminate the "Black Swan" failure modes identified in the **Sentinel Audit (R-A2A-SENTINEL-AUDIT)**. 

The core philosophy shifts from **Hub-centric reasoning** to **Hub-centric coordination**. The Hub is now a pure **Sovereignty Coordinator** managing atomic state and transport, while all cognitive verification, identity validation, and state hydration are moved to the agents. This architecture ensures zero reasoning bottlenecks in the Hub, cryptographically verified identity, and a deadlock-free state machine.

---

## 🔍 Research Log: External Synthesis

To ensure Temple-Grade resilience, the following external industry patterns were researched and integrated into this specification:

| Research Area | Source/Pattern | Key Technical Insight Extracted | Application in V2 |
| :--- | :--- | :--- | :--- |
| **State Recovery** | Helix Agents / Agent-Coherence | **Generation Fencing**: Use ownership epochs to reject "zombie" writers who wake up after their lock was reclaimed. | **Sovereign Epochs** in the lock-transfer sequence. |
| **Deadlock Prevention** | Redis Saga / Azure Saga | **Saga Compensations**: Define an explicit "Rollback" action for every state transition to ensure eventual consistency. | **Compensation Actions** for the `Transfer_Pending` state. |
| **Identity/PKI** | W3C DID / `did:agent` / AIP | **Deterministic AID**: Derive IDs from Ed25519 public keys using `hex(sha256(pubkey)[0..16])`. | **`did:agent`** implementation for all Sovereign IDs. |
| **Trust/Auth** | Verifiable Credentials (VC) | **Capability VCs**: Trust is not asserted; it is proven via signed credentials issued by an authority. | **Trust-Level VCs** replacing simple "Trusted" strings. |
| **Coordination** | Temporal / LangGraph | **Durable Checkpoints**: Persist execution state before external waits to survive infrastructure churn. | **Hydration Checkpoints** in `session_gnosis.md`. |
| **Latency/Tax** | PACT (arXiv:2606.05304v1) | **Action-State Communication**: Exchange compact records (Action, State, Result) instead of full transcripts. | **PACT-style Gnosis-Packets** to reduce hydration tax. |

---

## 🔐 1. The Identity Layer: Sovereign PKI

S-A2A v2 replaces "asserted trust" with **Cryptographic Provenance**.

### 1.1 Sovereign Agent Identity (`did:agent`)
Every agent is assigned a Decentralized Identifier (DID) derived from its Ed25519 keypair.
- **Derivation**: `DID = "did:agent:" + hex_lower(SHA-256(public_key_bytes)[0..16])`
- **Verification**: Possession of the private key is the sole proof of identity.
- **Registry**: Public keys are stored in the `SovereignKeyStore` (managed by the Hub), but resolution is deterministic.

### 1.2 Provenance and Signing
Every A2A message MUST be wrapped in a **Sovereign Envelope**:
```json
{
  "envelope": {
    "sender": "did:agent:...",
    "recipient": "did:agent:...",
    "epoch": 104,
    "timestamp": "iso8601",
    "signature": "ed25519_signature_of_payload"
  },
  "payload": { ... }
}
```

### 1.3 Trust via Verifiable Credentials (VC)
Trust levels are no longer strings; they are **Signed Capabilities**.
- **Trusted**: Agent presents a VC signed by the Oversoul/Hub.
- **Tainted**: Agent presents a VC (or no VC) and the payload is flagged by the recipient's `Skeptical Verifier`.
- **Taint-Tracking**: Taint is propagated via signed "Taint-Assertions" in the provenance chain.

---

## ⚙️ 2. Atomic Sovereignty Handshake v2

The state machine is redesigned to be **Deadlock-Free** and **Crash-Resilient**.

### 2.1 The Hardened State Machine
`Sovereign_Held` $\rightarrow$ `Transfer_Pending` $\rightarrow$ `Sovereign_Accepted`

### 2.2 Deadlock Prevention: TTLs and Epochs
To solve the "Orphan State" risk, the Hub implements **Lease-based Locking**:
1.  **Lock TTL**: When a resource enters `Transfer_Pending`, it is assigned a mandatory TTL (e.g., 300s).
2.  **Heartbeat**: The target agent MUST heartbeat the Hub to extend the lease if hydration is taking longer than expected.
3.  **Auto-Reversion**: If the TTL expires without an `accept_transfer` call, the Hub atomically reverts the state to `Sovereign_Held` and notifies the sender.
4.  **Generation Fencing (Epochs)**: Every time a lock is reclaimed or reverted, the **Sovereign Epoch** for that resource is incremented. Any late `accept_transfer` calls with a stale epoch are rejected.

### 2.3 Crash Recovery (The Hub-Crash Gap)
Locks are persisted in `data/coordination/locks/{resource}.lock` (disk-backed). Upon Hub reboot:
1.  The Hub scans the lock directory.
2.  It reconciles disk locks with current timestamps.
3.  Expired locks are reaped immediately.
4.  Active locks are re-hydrated into the `_hot_store`.

---

## 🧠 3. Cognitive Continuity & Hydration

S-A2A v2 optimizes for **Information Gain** while minimizing the **Hydration Tax**.

### 3.1 PACT-style Gnosis-Packets
Instead of raw history, agents exchange **Action-State Records**:
```json
{
  "gnosis_packet": {
    "action": "The specific action taken (e.g., 'Deep Research on X')",
    "state": "The evidence/grounding for the action (L2 Insights)",
    "result": "The final output/answer passed downstream",
    "l3_principles": [ { "principle": "...", "heritage": "..." } ],
    "cognitive_load": "Trivial | Standard | Complex"
  }
}
```

### 3.2 Tiered Hydration (The Fast-Path)
The mandatory 5-step hydration is now **dynamic** based on load and trust:

| Path | Condition | Sequence |
| :--- | :--- | :--- |
| **Fast-Path** | `cognitive_load == "Trivial"` AND `Trust == "Trusted"` | 1. Ingest $\rightarrow$ 2. Acknowledge (Direct Execution) |
| **Standard-Path** | `cognitive_load == "Standard"` | 1. Ingest $\rightarrow$ 2. Anchor $\rightarrow$ 3. Align $\rightarrow$ 4. Acknowledge |
| **Deep-Path** | `cognitive_load == "Complex"` OR `Trust == "Untrusted"` | 1. Ingest $\rightarrow$ 2. Anchor $\rightarrow$ 3. Align $\rightarrow$ 4. Skeptical Verify $\rightarrow$ 5. Acknowledge |

---

## ☣️ 4. Decoupled Verification & Taint Tracking

To prevent **Hub Bloat**, all reasoning is moved to the agents.

### 4.1 Client-Side Skeptical Verification
The Hub no longer runs NLI checks. It only transports the `Tainted` flag in the `ProvenanceHeader`.
- **The Rule**: If a recipient receives a `Tainted` or `Untrusted` payload, it **MUST** invoke its own local `Skeptical Verifier` (Two-Source Rule) before promoting the data to `Trusted` state in its `session_gnosis.md`.
- **Model Override**: If the agent detects `Tainted` data, it internally requests a `ModelGateway` override to use a high-rigor verification model for that specific turn.

---

## 🏛️ Audit Response: Remediation Matrix

| Sentinel Finding | Root Cause | S-A2A v2 Solution | Verification Method |
| :--- | :--- | :--- | :--- |
| **Orphan State Risk** | No timeout for `Transfer_Pending`. | **TTL-based Leases** + **Auto-Reversion** to `Sovereign_Held`. | Simulate target crash $\rightarrow$ verify lock release after TTL. |
| **Signature Void** | No defined PKI for signatures. | **`did:agent`** + **Ed25519** + **SovereignKeyStore**. | Attempt to spoof signature $\rightarrow$ verify rejection. |
| **Hub Bloat** | Reasoning logic in the Hub. | **Client-Side Verification**. Hub is now pure transport/state. | Measure Hub latency during Tainted-payload transfer. |
| **Hydration Tax** | Mandatory sequence for all tasks. | **Fast-Path** for trivial/trusted tasks + **PACT records**. | Compare execution time of `Trivial` vs `Complex` handoffs. |
| **Hub-Crash Gap** | State lost on reboot. | **Disk-backed Lock Persistence** + **Epoch Fencing**. | Force Hub restart during transfer $\rightarrow$ verify recovery. |

---

## 🛠️ Implementation Roadmap (Sovereign Architect)

1.  **Phase 1 (Identity)**: Implement `did:agent` derivation and `SovereignKeyStore` in `src/omega/oracle/security.py`.
2.  **Phase 2 (Coordination)**: Update `mcp_servers/omega_hub/server.py` with TTL locks, Epochs, and disk-persistence.
3.  **Phase 3 (Continuity)**: Implement PACT Gnosis-Packets and the Tiered Hydration logic in agent system prompts.
4.  **Phase 4 (Verification)**: Integrate the `Skeptical Verifier` into the agent's local execution loop.

**Temple-Grade Compliance**:
- **M1 AnyIO**: All lease/lock operations use `anyio.Lock` and `anyio.to_thread.run_sync`.
- **M12 Queue Integrity**: All state transitions are atomic and terminal.
- **M13 Temple-Grade**: Explicit error states defined: `StaleEpochError`, `LeaseExpiredError`, `TaintLeakageError`.
