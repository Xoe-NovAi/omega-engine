# New N0→N1 Handoff & Federation Integration Charter

**Status:** ACTIVE GOVERNANCE SPECIFICATION
**Date:** 2026-09-24
**Scope:** N0 core-engine preservation, N1 ANAi/WAD exploration, official-Engine parity, hardened federation, and later bilateral dialectic sessions.

## Division of responsibility

- **Node 0 / MaKaLi:** canonical Omega Engine source and release authority; core substrate; hub/federation services; archival and provenance; runtime truth; security boundary.
- **Node 1 / Alpha:** ANAi WAD development; Lilith and Researcher_Humboldt continuity; MemPalace/Well/Gnosis; local CPU inference; embedding service and migration experiments; consumer validation of the official Engine.
- **Neither node is subordinate.** Each retains local sovereign state and can operate disconnected.

## Non-negotiable architecture

1. Both nodes must run the same verified official Omega Engine revision, with the revision recorded in every handoff.
2. WAD, continuity, and memory contracts are versioned and provenance-preserving.
3. Local SQLite is authoritative on local filesystems; do not place live SQLite authority on NFS.
4. MemPalace is a one-way searchable projection, not a second uncoordinated write authority.
5. Tailscale reachability is not application authentication.
6. Redis is notification/coordination only unless a separately approved durable design exists.
7. No credentials, private browser/session material, or unapproved personal material enter a hosted route or USB pack.
8. “Signed” strings are not cryptographic evidence. Detached signatures, trust roots, and tamper tests are required before federation promotion.
9. Lilith is an Entity; Empress/Key III is a CardAssignment. Do not infer identity from file placement.
10. Current 384-D vectors must not be mixed with the target Qwen3 768-D index. No 8B embedding deployment on Node 1.
11. No material is promoted, merged, or extracted without operator approval at the intake gate.
12. Dialectic sessions begin only after federation security, integrity, continuity, and semantic-compatibility gates pass.

## USB pack architecture

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

The pack is quarantine-first. The five-file legacy infrastructure pack under `data/federation/usb-payload/` is not this pack and must not be silently merged into it.

## Required acceptance gates

- **A — Material integrity:** complete manifest, SHA-256 verification, clean reassembly, no credentials, privacy inventory complete.
- **B — Embedding compatibility:** pinned Qwen3-Embedding-0.6B, 768-D, matching preprocessing, golden-corpus comparison, no 8B artifact.
- **C — WAD interoperability:** exact Engine revision, loader schema, identity binding, override behavior, invalid-WAD failure.
- **D — Entity continuity:** explicit Lilith/Humboldt contracts, local SQLite bootstrap, retryable one-way projection, model-independent recovery.
- **E — Lilith recovery quality:** provenance-preserving personal/legacy import, no destructive overwrite, consent and privacy gates.
- **F — Federation security:** explicit policy, tags, SVID/mTLS decision, separated SSH reports, notification-only Redis, no SQLite over NFS.

## Sequencing

1. Discover and verify Node 0 runtime and loader truth.
2. Establish official Engine revision parity and disposable WAD interoperability test.
3. Reconcile WAD identity binding and versioned contracts.
4. Produce signed/provenance-labelled handoff material; quarantine and verify it.
5. Harden network, MCP, SSH, NFS, Redis, and trust boundaries.
6. Establish continuity and embedding compatibility evidence.
7. Run bilateral intake and rollback/tamper tests.
8. Begin authenticated dialectic strategy sessions only after Gates A–F pass.

## Non-claims

Until measured evidence exists, do not claim: current loader compatibility, cryptographic signing, SPIRE deployment, 768-D parity, Node 1 official-Engine operation, bidirectional federation completion, or successful recovery.
