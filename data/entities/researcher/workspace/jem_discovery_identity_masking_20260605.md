<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Jem Discovery: Sovereign Mirroring Identity-Masking Research
**Date**: 2026-06-05
**Agent**: Jem Discovery (L1)
**Objective**: Identify technical patterns for projecting a 'Persona' (Projected-ID) while maintaining a hidden, traceable 'True Identity' (Mirror-ID) visible only to a Sovereign Observer.

---

## 📑 Evidence Log

### Vector 1: Cryptographic Identity Masking & Proxying
- **Aries RFCs (Indirect Identity Control)**:
    - **Concept**: Delegation, Guardianship, and Controllership.
    - **Mechanism**: Use of "Proxy Trust Frameworks" and "Proxy Credentials" to bind a holder to a proxied identity.
    - **Key Signal**: "Proxy Challenges" allow a verifier to evaluate the legitimacy of indirect control without necessarily exposing the root identity.
    - **Source**: [Aries RFCs 0103](https://aries-rfcs.readthedocs.io/en/latest/concepts/0103-indirect-identity-control/)

- **Gordian Envelope (draft-mcnally-envelope-02)**:
    - **Concept**: Hierarchical binary data with selective elision.
    - **Mechanism**: Merkle-like digest trees allow a holder to encrypt or elide specific parts of a document (e.g., the True Identity) without invalidating the overall signature.
    - **Key Signal**: "Progressive Trust" — disclosure can be increased over time.
    - **Source**: [IETF draft-mcnally-envelope-02](https://datatracker.ietf.org/doc/html/draft-mcnally-envelope-02)

- **CapiscIO Authority Envelopes**:
    - **Concept**: Monotonic narrowing of authority.
    - **Mechanism**: Verifiable delegation chains where each link (`parent_authority_hash`) narrows the scope.
    - **Key Signal**: The "Authority Envelope" separates *identity* (who is this?) from *authority* (what may this agent do?).
    - **Source**: [CapiscIO RFC-008](https://github.com/capiscio/capiscio-rfcs/blob/main/docs/008-delegated-authority-envelopes.md)

- **ZeroID (RFC 8693)**:
    - **Concept**: On-Behalf-Of (OBO) delegation.
    - **Mechanism**: Uses the `act` claim in JWTs to carry the full delegation chain.
    - **Key Signal**: The `act` claim allows a service to see the actor (Projected-ID) and the original authorizer (Mirror-ID).
    - **Source**: [ZeroID GitHub](https://github.com/highflame-ai/zeroid)

- **PEDIGREE (SIT Tokens)**:
    - **Concept**: Dual-layer authority enforcement.
    - **Mechanism**: "SIT" (Suradar Identity Token) contains a `parent_chain` of JTIs.
    - **Key Signal**: "Ceiling" (Operator-level policy) vs "Mandate" (Parent-level policy). The Sovereign Observer (Operator) defines the Ceiling.
    - **Source**: [IETF draft-rampalli-pedigree-00](https://www.ietf.org/archive/id/draft-rampalli-pedigree-00.html)

### Vector 2: Zero-Knowledge Proofs (ZKPs)
- **AnonCreds**:
    - **Concept**: Unlinkable credentials.
    - **Mechanism**: Use of "Link Secrets" to bind credentials to a holder without revealing a unique identifier to the verifier.
    - **Key Signal**: "Predicate Proofs" (e.g., proving age > 18) allow verification of a property without revealing the underlying attribute.
    - **Source**: [AnonCreds Spec](https://anoncreds.github.io/anoncreds-spec/)

- **zkMe**:
    - **Concept**: Selective Disclosure (SD).
    - **Mechanism**: ZK circuits extract specific fields into a public output (`operatorOutput`) while keeping the rest of the credential hidden.
    - **Key Signal**: "Nullifiers" provide a deterministic, one-way hash for anti-Sybil/session-tracking without revealing the True Identity.
    - **Source**: [zkMe Docs](https://docs.zk.me/hub/how-built/credential-sys/selective-disclosure)

- **zk-creds**:
    - **Concept**: General-purpose ZKPs for existing docs.
    - **Mechanism**: Converts non-anonymous docs (e.g., passports) into anonymous credentials using zk-SNARKs.
    - **Key Signal**: "Hidden Issuer" property — can hide where a credential came from by concatenating lists from different issuers.
    - **Source**: [IACR 2022/878](https://eprint.iacr.org/2022/878)

- **ZkVCT (ShareRing)**:
    - **Concept**: Merkle-anchored ZK tokens.
    - **Mechanism**: Attributes hashed into a Sparse Merkle Tree (SMT). Proofs are validated against a signed Merkle Root.
    - **Key Signal**: Nullifiers = `Poseidon([UserPrivateKey, CredentialID, ContextID])`.
    - **Source**: [ZkVCT Spec](https://sharering.network/did-and-zkp-specifications/zkvct-spec/)

### Vector 3: Self-Sovereign Identity (SSI) for AI
- **AIP (Agent Identity Protocol)**:
    - **Concept**: Layered agent identity.
    - **Mechanism**: `did:aip` identifiers. Layers: Core Identity $\rightarrow$ Principal Chain $\rightarrow$ Capabilities $\rightarrow$ Credential Token.
    - **Key Signal**: "Principal Chain" establishes who authorized the agent, creating a traceable path back to a human/org.
    - **Source**: [IETF draft-singla-agent-identity-protocol](https://datatracker.ietf.org/doc/draft-singla-agent-identity-protocol/)

- **APS (Agent Passport System)**:
    - **Concept**: Faceted Authority Attenuation.
    - **Mechanism**: Authority modeled as a product lattice (Scope, Spend, Depth, Time, Reputation, Values, Reversibility).
    - **Key Signal**: Monotonic narrowing ensures a delegated persona can never exceed the authority of the Mirror-ID.
    - **Source**: [IETF draft-pidlisnyi-aps](https://datatracker.ietf.org/doc/draft-pidlisnyi-aps/)

- **Agent-ID (p-vbordei)**:
    - **Concept**: Capability VC profile.
    - **Mechanism**: Principal signs a Capability VC for an agent.
    - **Key Signal**: "Machine-first identity" — focuses on what the agent can do, not who it is.
    - **Source**: [GitHub p-vbordei/agent-id](https://github.com/p-vbordei/agent-id)

### Vector 4: High-Security Proxy Patterns
- **Google "Safe Proxies"**:
    - **Concept**: Tool Proxy for administrative actions.
    - **Mechanism**: Intercepts CLI commands, enforces Multi-Party Authorization (MPA), and logs all actions.
    - **Key Signal**: The proxy is the only entity with the "Real" credentials; the user only has "Proxy" access.
    - **Source**: [Google SRE Book Ch 3](https://google.github.io/building-secure-and-reliable-systems/raw/ch03.html)

- **Gatekeeper Pattern**:
    - **Concept**: Single enforcement point.
    - **Mechanism**: Hardened intermediary in a DMZ. Validates requests and injects validated identity headers for backends.
    - **Key Signal**: "Minimal Privilege" — the gatekeeper knows only enough to make security decisions, not the full business logic.
    - **Source**: [Layrs Gatekeeper](https://layrs.me/course/hld/12-reliability-patterns/gatekeeper/)

- **Iron-Proxy**:
    - **Concept**: Boundary-level secret injection.
    - **Mechanism**: Workloads use "Proxy Tokens"; the proxy swaps these for "Real Secrets" at the egress boundary.
    - **Key Signal**: "Secret-Swap" — the True Identity (Real Secret) never enters the untrusted sandbox.
    - **Source**: [GitHub ironsh/iron-proxy](http://github.com/ironsh/iron-proxy)

- **Scoped Credentials Proxy**:
    - **Concept**: External credential attachment.
    - **Mechanism**: Proxy validates request against allowlist and attaches a narrowly scoped token (e.g., one repo).
    - **Key Signal**: OS-level process isolation ensures the agent cannot read the proxy's environment variables.
    - **Source**: [AgentPatterns.ai](https://agentpatterns.ai/security/scoped-credentials-proxy/)

### Vector 5: Persona Projection in MAS
- **SPASM**:
    - **Concept**: Egocentric Context Projection (ECP).
    - **Mechanism**: Stores history in perspective-agnostic form; projects it into agent-specific views (SELF vs PARTNER).
    - **Key Signal**: Prevents "echoing" and persona drift by decoupling the absolute identity from the projected role.
    - **Source**: [arXiv 2604.09212](https://arxiv.org/html/2604.09212)

- **Persona Object Protocol (POP)**:
    - **Concept**: Portable persona objects.
    - **Mechanism**: Separation of persona definition (canonical object) from runtime projection (adapter).
    - **Key Signal**: Persona is a "standalone object" that can be referenced and projected into different runtimes.
    - **Source**: [GitHub joy7758/persona-object-protocol](https://github.com/joy7758/persona-object-protocol)

---

## 🛠️ Technical Patterns for Sovereign Mirroring

Based on the evidence, I propose the following four patterns for implementing **Sovereign Mirroring Identity-Masking**:

### Pattern A: The "SIT-Chain" (Delegated Traceability)
- **Mechanism**: Use a structure similar to **PEDIGREE** or **AIP**. The agent presents a leaf token (Projected-ID). This token contains a `parent_chain` of hashes/JTIs.
- **Mirroring**: The full chain leads back to the Root Principal (Mirror-ID).
- **Sovereign Observer**: The Registry or a privileged PEP (Policy Enforcement Point) resolves the chain to reveal the Mirror-ID. The recipient only sees the leaf.
- **Citation**: [PEDIGREE SIT Tokens], [AIP Principal Chain].

### Pattern B: The "ZKP-Nullifier" (Anonymous Verifiability)
- **Mechanism**: Use **AnonCreds** or **ZkVCT**. The agent generates a ZKP that they possess a valid credential from a trusted issuer.
- **Mirroring**: The agent uses a "Link Secret" to bind the credential to their True Identity (Mirror-ID) without revealing it.
- **Sovereign Observer**: The Observer holds the "Link Secret" or the "Master Key" used in the ZK-circuit, allowing them to link the Projected-ID (Nullifier) back to the Mirror-ID.
- **Citation**: [AnonCreds Link Secrets], [ZkVCT Nullifiers].

### Pattern C: The "Secret-Swap Boundary" (Infrastructure Masking)
- **Mechanism**: Use an **Iron-Proxy** style egress gateway. The agent operates using a "Proxy Token" (Projected-ID).
- **Mirroring**: The Proxy maintains a mapping of `Proxy-Token $\rightarrow$ Real-Credential`.
- **Sovereign Observer**: The Proxy is the Sovereign Observer. It swaps the Projected-ID for the Mirror-ID only at the network boundary and logs the mapping.
- **Citation**: [Iron-Proxy Secret Injection], [Scoped Credentials Proxy].

### Pattern D: The "Egocentric Projection" (Cognitive Masking)
- **Mechanism**: Use **SPASM's ECP** or **POP's Projection**. Maintain a "Perspective-Agnostic" core identity (Mirror-ID).
- **Mirroring**: Project this core into a "Role-Relative" persona (Projected-ID) for the specific interaction.
- **Sovereign Observer**: The Orchestrator/Runtime that manages the projection mapping.
- **Citation**: [SPASM ECP], [POP Projection Model].

---

## 📡 Raw Signals for L2 Synthesis

- **Signal 1 (Monotonic Narrowing)**: Authority must only shrink as it moves from Mirror-ID $\rightarrow$ Projected-ID. Any "amplification" is a security violation.
- **Signal 2 (Dual Enforcement)**: Use a "Ceiling" (Global/Observer limit) and a "Mandate" (Parent/Mirror limit). The effective authority is the intersection of both.
- **Signal 3 (Linkage vs. Correlation)**: Use "Nullifiers" to allow session-tracking (correlation) without revealing the True Identity (linkage).
- **Signal 4 (Boundary Isolation)**: The most secure Mirror-IDs are those that never enter the agent's memory space, existing only in the Sovereign Observer's environment.
- **Signal 5 (Perspective Agnosticism)**: True identity should be stored in a form that is independent of the role it is currently projecting.
