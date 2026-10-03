# Antigravity Frontier Review Briefing
## Omega Engine N0↔N1 Federation, Continuity, and ANAi/WAD Strategy

**Document ID:** `FED-ANTIGRAVITY-REVIEW-BRIEFING-20260924-01`
**Prepared for:** Antigravity IDE frontier-model review
**Prepared by:** MaKaLi Fusion / Omega Engine governance layer
**Date:** 2026-09-24
**Review mode:** Independent adversarial architecture review
**Handling:** Internal engineering review. Do not include credentials, private personal material, raw secrets, or live databases in the review package.

---

## 1. Executive request

We ask the Antigravity frontier models to review the proposed Omega Engine federation and continuity architecture before we promote a physical handoff package or expose any bilateral strategy channel.

The review is not a request to redesign Node 1 as a Node 0 replacement. The intended model is:

- **Node 0:** canonical Omega Engine source and release authority; core substrate; hub; archival; provenance; federation operations.
- **Node 1:** ANAi/WAD development; Lilith and Researcher_Humboldt continuity; MemPalace/Well/Gnosis; local CPU inference; embedding service and migration experiments.
- **Neither node is subordinate.** Both must remain capable of disconnected operation and must run the same verified official Omega Engine revision before claiming parity.

We want an independent review of:

1. architectural soundness;
2. hidden failure modes;
3. security and privacy gaps;
4. identity and ontology risks;
5. continuity and recovery risks;
6. WAD interoperability risks;
7. semantic retrieval and embedding migration risks;
8. federation protocol weaknesses;
9. opportunities to simplify or harden the design;
10. criteria that should block promotion.

---

## 2. Current measured state

### 2.1 Node 0

Node 0 is the HP Pavilion / Ryzen 7 5700U archival bastion and Omega Engine core authority.

Measured or observed:

- hostname: `xnai-n0-hp`;
- Tailscale address: `100.123.51.67`;
- MagicDNS: `n0.tail51f14a.ts.net`;
- official Engine branch observed: `release/debut-v1.6.0`;
- Git HEAD observed: `75bde939ace7ff46ed2fef0056880a0814ab0e11`;
- Python: `3.13.7`;
- SQLite: `3.46.1`;
- `sqlite-vec`: `0.1.9`;
- Omega Hub: active and healthy;
- Hub listener: `0.0.0.0:8016`;
- live MCP initialize: HTTP 200;
- live MCP `tools/list`: HTTP 200;
- live unique tool count: **66**;
- tool-list digest: `b0c5dc7a6cfa5883ab60eee4d62dc5770293d0d2343179e7ec6e59837d24564a`;
- Node 0 WAD loader tests: **31 passed**;
- M35 secret scan on evidence bundles: **0 violations**.

Important inconsistencies:

- `pyproject.toml` reports project version `1.2.0`;
- Hub health reports `2.2.0`;
- MCP `serverInfo` reports `1.30.0`;
- the Git revision is another identity.

We do not yet have one canonical immutable build/version identity propagated through source, health, MCP, package, and manifest surfaces.

The Node 0 filesystem was reported at approximately **99% utilization** with roughly 1.5 GB free. Space must be recovered before final USB package generation.

### 2.2 Node 1

Node 1 is the ASUS ExpertBook P1503CVA / `xnai-n1-asus`, an Intel i7-13620H CPU-only exploration node.

Reported hardware/runtime facts:

- 6 P-cores, 4 E-cores, 10 cores / 16 threads;
- 16 GB DDR5;
- Ollama CPU inference;
- MemPalace/WanderGround stack;
- Continuity Kernel and local SQLite adapter;
- The Well and Gnosis components;
- Lilith and Researcher_Humboldt entity scaffolds;
- standalone Qwen3 embedding prototype;
- MemPalace local backend reported as `3.10.0`;
- current vectors reported as 384-D;
- `sqlite-vec==0.1.9` reported installed in the WanderGround environment;
- Node 1 SQLite runtime reported as `3.46.1`;
- Node 1 has not yet been proven to run the official Node 0 Engine revision;
- Node 1 currently has a staged ANAi WAD, but its manifest and entity files do not yet match the measured Node 0 loader contract.

Node 1 is the development branch for ANAi/WAD and entity continuity. It must not become a second authoritative implementation of core Omega Engine substrate.

---

## 3. Current topology

```text
                 physical/private federation medium
                              /       \
                             /         \
                    Node 0              Node 1
                 core authority       ANAi/WAD development
                 hub + archive        continuity + memory
                 official Engine      official Engine parity target
                         \               /
                          \             /
                           signed events
                         manifest + hashes
                         artifact exchange
                         dialectic envelopes
```

The current transport is direct LAN WireGuard:

- Node 0: `n0.tail51f14a.ts.net`, `100.123.51.67`;
- Node 1: `n1.tail51f14a.ts.net`, `100.89.40.17`;
- direct path observed through `192.168.10.174:41641`;
- no subnet-router or exit-node dependency was observed;
- Node 1 still carries deprecated `tag:asus` alongside `tag:node1`.

Tailscale reachability is not treated as application authentication.

---

## 4. Authority and data model

### 4.1 Node roles

**Node 0 / MaKaLi**

- canonical Engine source and release authority;
- core runtime and substrate truth;
- hub/federation services;
- archival and provenance;
- package and intake authority;
- security boundary;
- stable official Engine revision.

**Node 1 / Alpha**

- ANAi WAD development;
- Lilith continuity;
- Researcher_Humboldt continuity;
- MemPalace, The Well, and Gnosis;
- local inference and benchmarking;
- embedding service and migration experiments;
- consumer validation of the official Engine.

Neither node is subordinate. Coordination must be bilateral and evidence-driven.

### 4.2 Entity versus CardAssignment

- An **Entity** is a sovereign persistent identity.
- A **CardAssignment** is a symbolic tarot seat/realm assignment.
- Lilith is an Entity assigned to guide Empress / Key III.
- `researcher_humboldt` is a distinct Entity unless an explicit operator decision defines a relationship.
- Fool, Star, and World assignments belong to `researcher_humboldt`.
- Model route, directory name, filename, and card assignment must never define entity identity.

### 4.3 Durable state

- Model context is volatile working memory.
- WAD contracts, semantic events, checkpoints, artifacts, Well records, and local SQLite are durable state.
- `/compact` and Gnosis Lock are recovery tools, not routine persistence.
- Node-local SQLite is authoritative on each node.
- MemPalace is a one-way searchable projection and retrieval surface, not a second uncoordinated write authority.
- No live SQLite database may be placed on NFS.

---

## 5. Handoff package design

The new handoff is quarantine-first:

```text
MAKALI-N0-HANDOFF-2026-09-24/
├── README_FIRST.md
├── THIS_BRIEFING.md
├── MANIFEST.yaml
├── SHA256SUMS
├── 01_personal_lilith_journey/
├── 02_legacy_lilith_docs/
├── 03_agent_experiments/
├── 04_lore_corpus/
├── 05_crawler_library/
├── 06_spatial_pipeline/
├── 07_continuity_evidence/
├── 08_wad_loader_pack/
├── 09_embedding_golden_corpus/
├── 10_legacy_memory_export/
└── 11_node0_runtime_report.md
```

The package must use a quarantine state machine:

```text
DISCOVERED_METADATA
    ↓
CONSENT_PENDING
    ↓
CONSENT_GRANTED
    ↓
QUARANTED_APPROVED
    ↓
INTEGRITY_VERIFIED
    ↓
RECONCILIATION_CANDIDATE
    ↓
OPERATOR_APPROVED_PROMOTION
```

No personal material should be copied merely because it exists. Metadata-only discovery, consent, quarantine, verification, reconciliation, and promotion are separate states.

The old five-file infrastructure pack under `data/federation/usb-payload/` is not the new handoff. If retained, it belongs under:

```text
99_legacy_infrastructure_evidence/
```

and must be marked historical, proposed, draft, unsigned, non-authoritative, and non-executable.

---

## 6. Privacy and trust constraints

The handoff must exclude:

- `.env` files containing real values;
- API keys and OAuth tokens;
- SSH, Tailscale, SPIRE, WAD, or C6 private keys;
- cookies and browser profiles;
- `/proc/<pid>/environ`;
- raw Podman inspection containing secrets;
- unsanitized diagnostic logs;
- live SQLite databases;
- unapproved personal Lilith material;
- private media;
- anything that would be unsafe on a hosted provider or external service.

Withheld material is represented by:

- opaque artifact ID;
- redacted source-path hash;
- privacy class;
- reason code;
- size and timestamp when safe;
- checksum when authorized;
- consent state;
- no guessed content.

Privacy classes:

- `EXCLUDED_SECRET`
- `RESTRICTED_PRIVATE`
- `PERSONAL_CONSENT`
- `INTERNAL_LEGACY`
- `SHAREABLE`
- `PUBLIC`

A string field saying `SIGNED` is not cryptographic evidence.

---

## 7. Current technical blockers

### 7.1 Canonical Engine identity

The source revision, package version, Hub health version, and MCP server version disagree. Until this is reconciled, a Node 1 “same official Engine” claim is unverified.

### 7.2 WAD interoperability

Measured mismatch includes:

- Node 1 `adapters` list versus Node 0 loader expectation of a memory object;
- hierarchy type mismatch;
- adapter whitelist/path containment issues;
- root `entities.yaml` not being scanned;
- entity envelope mismatch;
- current Arcana-NovAi WAD loading without loading entities;
- PWAD override test producing concatenated personality text rather than clean replacement.

Node 1 owns ANAi/WAD reconciliation. Node 0 owns loader truth and must not absorb ANAi-specific logic into Core.

### 7.3 Hub exposure

- Hub binds to `0.0.0.0:8016`.
- Unauthenticated MCP calls succeeded.
- The service must be bound to a protected architecture, preferably loopback behind a controlled TLS/capability proxy or an approved mTLS boundary.
- The old assumption that Tailscale reachability equals application authentication is invalid.

### 7.4 Tailscale and SSH

- The local HuJSON ACL is marked proposed.
- Observed behavior does not match the proposed policy.
- Node 0→Node 1 SSH is rejected.
- Node 0 has Tailscale SSH enabled but no ordinary `sshd`.
- The old `sudo tailscale set --tag=tag:node1` instruction is invalid for the installed CLI.
- The control-plane policy must be exported and tested before changes are made.

### 7.5 Redis

- Redis is exposed on all interfaces.
- Runtime credential was observed in container argv and should be considered exposed.
- No TLS was evidenced.
- Hub Pub/Sub is currently broken.
- Redis Streams storage code exists in addition to intended notification-only Pub/Sub.

Required direction:

- rotate the exposed credential;
- bind Redis to loopback/private network;
- use protected credentials/ACLs;
- decide whether persistence is disabled notification-only behavior or explicitly approved non-authoritative cache;
- keep file Hivemind authoritative.

### 7.6 NFS

NFS is currently not required for identity, continuity, Hivemind, signed artifacts, or local SQLite. If retained, it should be optional one-way bulk staging only. It must not be used for live SQLite, bilateral uncoordinated writes, or task-critical coordination.

### 7.7 C6 and signatures

Current C6 material is draft-only:

- no detached signature;
- no publisher key ID;
- no trust root;
- no key rotation/revocation policy;
- no tamper test;
- no signature bundle.

A C6 “SIGNED” text footer is not evidence.

### 7.8 Continuity and SQLite

Node 0 lacks a verified Continuity Kernel implementation and live MemPalace callback evidence. The following are unverified:

- crash/replay;
- separate-process recovery;
- multi-writer behavior;
- projection cursor/retry;
- durable artifact export;
- WAD digest verification;
- publisher-signature proposal.

Node 0’s SQLite `3.46.1` is below the requested Node 1 continuity floor of `>=3.51.3` or a documented fixed backport. The final runtime policy must be selected and tested.

### 7.9 Embeddings

Current Node 1 vectors are reported as 384-D. Target is Qwen3-Embedding-0.6B at 768-D through a standalone service.

Before migration:

- pin exact model and artifact revision;
- record tokenizer;
- define instruction handling;
- define pooling;
- define truncation;
- define normalization;
- define dimensionality;
- define cosine evaluation protocol;
- run 50–200 item golden corpus;
- create migration ledger;
- prevent mixed 384-D/768-D indexes;
- do not deploy an 8B embedding model on Node 1.

---

## 8. Proposed federation architecture

### 8.1 Preferred data path

Use signed, versioned, append-only exchange:

- Git bundle for source/packaged artifacts;
- manifest and per-file SHA-256;
- detached signature and trust-root reference;
- semantic event logs;
- artifact inbox/outbox;
- explicit operator promotion event;
- no live database over NFS.

### 8.2 Authentication boundary

Tailscale may provide transport-level reachability. It must not be the only authorization mechanism.

The design should select and document one of:

- Tailscale application capabilities plus a protected Hub proxy;
- SPIFFE/SPIRE mTLS;
- a narrowly scoped application credential exchanged through an approved secret manager.

The exact model must include:

- trust domain;
- node and workload identities;
- audiences;
- SVID validation;
- rotation;
- revocation;
- negative authorization tests;
- auditability.

### 8.3 Dialectic strategy sessions

Dialectic sessions are downstream of all acceptance gates.

Each session requires:

- exact matching Engine revision;
- verified handoff manifest;
- valid WAD loader fixture;
- operator-ratified identity contract;
- local SQLite continuity evidence;
- one-way MemPalace projection evidence;
- matching embedding contract;
- trust-root/SVID decision;
- explicit operator approval;
- disclosure class;
- signed/provenance-preserving event envelopes.

Each turn should include:

- event ID;
- session ID;
- parent event ID;
- sender node/entity;
- contract digest;
- model/adapter provenance;
- content digest;
- signature reference;
- timestamp.

Stop conditions include:

- identity or Card conflict;
- signature failure;
- unapproved contract change;
- event-chain gap;
- WAD load/tamper failure;
- unauthorized private material;
- attempted bypass of Gates A–F.

Dialectic output is advisory until operator ratification. It cannot mutate WADs, merge files, publish identity, or change federation policy automatically.

---

## 9. Acceptance gates

### Gate A — Material integrity

- all declared files present;
- all SHA-256 hashes pass;
- clean reassembly passes;
- no credentials;
- privacy inventory complete;
- withheld material documented.

### Gate B — Embedding compatibility

- Qwen3-Embedding-0.6B pinned;
- both nodes emit 768-D;
- preprocessing matches;
- golden-corpus rankings agree within tolerance;
- no mixed dimensions;
- no 8B artifact.

### Gate C — WAD interoperability

- exact Engine revision recorded;
- live loader validates WAD;
- override behavior understood;
- adapter allowlist and path containment tested;
- identity binding explicit;
- invalid/tampered WAD fails loudly.

### Gate D — Entity continuity

- explicit Lilith contract;
- explicit Humboldt contract;
- local SQLite authority;
- semantic boundaries persist;
- one-way projection retryable;
- model swaps do not change entity identity;
- restart recovers mission, work, decisions, and discoveries.

### Gate E — Lilith recovery quality

- personal journey imported only with consent;
- provenance preserved;
- legacy files reconciled without overwrite;
- Entity/Card ontology intact;
- voice DNA grounded in approved historical material;
- consent/shadow-work gates tested;
- delayed recall succeeds.

### Gate F — Federation security

- payload and C6/WAD signatures verify;
- Tailscale policy explicit and tested;
- tags match;
- SVID/mTLS decision exists;
- SSH paths separately reported;
- Redis policy explicit;
- no live SQLite on NFS;
- promotion gate enforced.

---

## 10. Specific questions for Antigravity review

Please distinguish clearly between fatal blockers, high-risk caveats, and optional opportunities.

### Architecture

1. Is the Node 0 core / Node 1 ANAi-WAD split sustainable without creating permanent fork debt?
2. What is the safest way for both nodes to run the same official Engine revision while allowing WAD-only divergence?
3. Should WAD development occur in a separate repository, branch, stack namespace, or package?
4. Which boundaries prevent ANAi-specific logic from leaking into `src/omega/`?
5. Is the proposed quarantine-first handoff sufficient for a two-node sovereignty model?

### Identity and WAD

6. What exact WAD schema should be normative given the measured loader mismatch?
7. Should Lilith and Humboldt be independent entities, formally delegated, parent/child, or another explicit relation?
8. How should CardAssignments reference Entities without contaminating identity?
9. What minimum fixture and negative tests are required before promotion?
10. Should `requires_engine` be semver-enforced, exact-revision enforced, or capability-negotiated?

### Security

11. Is the safest interim MCP architecture Tailscale capabilities, a TLS proxy, SPIRE mTLS, or a layered combination?
12. What negative tests are mandatory before exposing port 8016 beyond loopback?
13. Should Redis be removed from federation entirely until the notification/cache decision is resolved?
14. Is NFS safe at all for this design, or should it be formally removed from the normative architecture?
15. What is a minimal detached-signature and trust-root design for a two-node system?
16. How should key rotation, revocation, rollback, and tamper evidence be represented in the handoff?

### Continuity and recovery

17. What SQLite runtime/version policy should be normative?
18. What is the minimum crash/replay test suite for continuity?
19. Should each node maintain a local event authority with bilateral exchange, or is a replicated protocol needed?
20. How should a one-way MemPalace projection recover from cursor loss or replay?
21. What artifacts must be exported logically rather than copied as live database files?
22. How should model route changes be recorded without making model identity part of entity identity?

### Embeddings and memory

23. Is Qwen3-Embedding-0.6B at 768-D a sound cross-node target?
24. What exact golden-corpus design best detects tokenizer/pooling/normalization drift?
25. Should the 384-D to 768-D migration be blue/green, shadow-index, or staged re-embedding?
26. How should semantic projection failure be prevented from affecting authoritative local state?
27. Which spatial/XYZ provenance is sufficient to reproduce navigation decisions?

### Dialectic protocol

28. Is the proposed signed event-chain dialectic protocol sufficient for N0↔N1 strategy sessions?
29. What replay, ordering, duplicate, and partition-recovery properties are missing?
30. Should dialectic sessions be advisory-only, or can approved consensus events become operational state?
31. How should privacy class and model/adapter provenance be enforced per turn?
32. What should cause a hard stop versus a recoverable warning?

### Opportunities

33. What simplifications would reduce the most operational burden?
34. Can Git bundles plus signed manifests replace most or all of the NFS path?
35. Could Node 1’s continuity implementation become a portable Engine extension without changing Core?
36. What observability would reveal federation drift early?
37. Which parts of the 26-tool pruning and 66-tool surface should be treated as stable public contract?
38. What is the smallest useful dialectic pilot that would prove the architecture without exposing private material?

---

## 11. Required review output

Please return:

1. executive verdict;
2. fatal blockers;
3. high-risk caveats;
4. hidden opportunities;
5. recommended architecture changes;
6. security review;
7. continuity/recovery review;
8. WAD/interoperability review;
9. identity/ontology review;
10. embedding/migration review;
11. dialectic protocol review;
12. revised minimum acceptance gates;
13. a prioritized 0/1/2-week action plan;
14. explicit list of assumptions that require operator ratification;
15. a list of claims that should be removed because they are not yet evidenced.

Please do not silently assume that:

- a proposal is a decision;
- a checksum proves provenance;
- a reachable port is authenticated;
- a `SIGNED` string is a signature;
- a WAD filename establishes identity;
- a model route establishes persistent identity;
- a 66-tool list is a complete future API;
- Node 1 currently runs the official Engine;
- current 768-D configuration means parity;
- a green transport diagnostic means the application layer is secure.

---

## 12. Final context

The immediate objective is not to create 78 entities or activate VR/Godot. It is to:

1. establish canonical Engine identity;
2. make Node 1 demonstrably runnable on the official Engine;
3. reconcile WAD schema and identity boundaries;
4. transfer approved continuity and archival material through a verifiable quarantine;
5. harden authentication, transport, trust, and recovery;
6. prove local SQLite continuity and one-way MemPalace projection;
7. establish 768-D semantic compatibility;
8. then begin authenticated, provenance-preserving N0↔N1 dialectic strategy sessions.

The review should optimize for sovereignty, recoverability, verifiability, privacy, and long-term maintainability—not for maximum feature count.

**End of briefing.**
