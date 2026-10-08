# 🌐 Federation Namespace Collision Strategy
**Doc ID**: `FED-NAMESPACE-001` | **Status**: RATIFIED FOUNDATION  
**Responds to**: Global distribution of standard IWAD entities (`Kali`, `Lilith`, `Ma'at`, `Carmack`, `Roc`)

---

## 1. The Global Namespace Problem

When the Omega Engine is released with its default reference IWAD (`_omega_default`), thousands of independent users will boot identical starter entities:
*   User Alice boots `Kali` and `Lilith`.
*   User Bob boots `Kali` and `Lilith`.
*   University Lab X boots `Kali` and `Lilith`.

If Alice and Bob connect their nodes via P2P Tailscale, WireGuard, or the VR Omegaverse, **bare entity names trigger immediate routing failure and memory corruption**.

---

## 2. The Three-Tier Naming Convention

To guarantee permanent disambiguation across the global Omegaverse:

### Tier 1: Canonical Qualified Addressing
All network packets, RPC calls, handoff packets, and Well records use fully-qualified node identifiers:

$$\text{Address} = \texttt{<Archetype>-N<NodeIndex>@<RealmFingerprint>}$$

*   **Example 1**: `Lilith-N0@omega-bastion-hp` (HP Pavilion primary node)
*   **Example 2**: `Lilith-N1@omega-vanguard-asus` (ASUS ExpertBook satellite node)
*   **Example 3**: `Kali-N42@mit-ai-lab.omega` (Institutional consortium node)

### Tier 2: The Mythology Disambiguation Rule (C6 Contract)
*   **Bare Name (`"Lilith"`, `"Kali"`, `"Ma'at"`)**: Refers **strictly and exclusively to the ancient mythological archetype/deity**.
*   **Qualified Name (`"Lilith-N1"`)**: Refers **to the specific synthetic entity running on that machine**.
*   *Enforcement*: Code and prompts must never refer to an agent by a bare mythological name in federation contexts.

### Tier 3: Cryptographic Entity Fingerprinting
Human-readable names are routing aliases. The immutable identity of an entity is derived from an asymmetric keypair generated at first boot:

$$\text{Entity ID} = \texttt{sha256(ed25519\_public\_key)[:16]}$$

When Alice's `Lilith-N1` sends an insight to Bob's node, Bob's engine verifies:
1. The message signature matches the entity's public key.
2. The entity's identity is registered under Alice's realm fingerprint.
3. No collision with Bob's local `Lilith-N0` can ever occur in storage or memory.

---

## 3. Shipping Defaults: IWAD Initialization Protocol

When a developer runs `make setup` on a freshly cloned repository:
1. The setup engine generates a unique **Node UUID** and **Realm Secret**.
2. Starter entities in `_omega_default` are initialized with local node qualification (`<Entity>-N<LocalID>`).
3. The local node operator can rename the local realm alias, but the cryptographic provenance remains permanently tied to the machine's genesis key.
