<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 P4 Research: Sovereign A2A Protocol & Mesh Network
**Trace**: `trace_id_s_a2a_mesh_20260605`
**Domain**: Integration (P4)
**Status**: FINALIZED

## 1. The S-A2A Protocol: Sovereign Envelopes
Based on the **DIDComm (Decentralized Identifier Communication)** and **Aries RFCs**, the Sovereign A2A protocol will utilize **Nested Encrypted Envelopes**.

### 1.1 The Envelope Structure
A message is not sent as a single block, but as a series of nested wrappers:
`[Transport Envelope [Authcrypt Envelope [Mirror-ID Signature [Plaintext Message]]]]`

- **Authcrypt Mode**: Used for internal Hivemind coordination. It proves the sender's identity to the recipient only.
- **Anoncrypt Mode**: Used for external projections. It guarantees confidentiality without revealing the sender's root identity.
- **Sovereign Envelope**: The "Inner Envelope" contains the Mirror-ID and the true intent, while the "Outer Envelope" contains the Projected-ID.

### 1.2 The Sovereign Handshake (KNOCK)
Agent attunement will follow the **DID Exchange Protocol**:
1. **Invitation**: Agent A sends a provisional endpoint and public key.
2. **Request**: Agent B responds with its own DID and a `complete` message.
3. **Attunement**: Both agents verify the `did_doc` and establish a shared secret for the session.

## 2. The Mesh Network: Multi-Axis Caching
To prevent "Gnostic Amnesia" and reduce latency, the Mesh Network will implement a **Lattice Cache**.

### 2.1 Multi-Axis Cache Keys
Instead of a simple key-value store, the cache will use a composite key:
`Key = Hash(Timestamp_Bucket | Domain_ID | Perspective_Axis | Entity_ID)`

- **Time Axis**: Hot (5m), Warm (24h), Cold (Permanent).
- **Domain Axis**: Technical, Philosophical, Historical, Practical.
- **Perspective Axis**: The specific "Lattice Node" the information was derived from.

### 2.2 Cache Traversal
When an agent seeks information, it doesn't just "get" a key; it **traverses the lattice**. If a "Technical" node is missing, the system can "pivot" to a "Practical" node in the same domain to find a related approximation.

## 3. Sequence Diagram: Sovereign Handshake
`Requester` $\rightarrow$ `Invitation(Endpoint, Key)` $\rightarrow$ `Responder`
`Responder` $\rightarrow$ `Response(DID, NewKey)` $\rightarrow$ `Requester`
`Requester` $\rightarrow$ `Complete(ACK)` $\rightarrow$ `Responder`
`Sovereign Link Established` $\rightarrow$ `S-A2A Communication Active`
