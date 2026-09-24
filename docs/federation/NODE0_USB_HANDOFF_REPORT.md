# Node 1 → Node 0 USB Handoff Report

**Report ID:** `N1-N0-HANDOFF-20260924-01`  
**Date:** 2026-09-23/24 UTC  
**Source node:** Node 1 — ASUS ExpertBook P1503CVA / `xnai-n1-asus` / Compute Vanguard  
**Destination node:** Node 0 — HP Pavilion / `xnai-n0-hp` / Archival Bastion  
**Prepared by:** `researcher_humboldt` / Omega Engine Alpha  
**Transfer medium:** Physical USB pack; signed handoff should use an immutable release directory with a manifest and detached signature.

> **Scope:** This report describes what has actually been built and measured on Node 1, what remains unverified, and what Node 0 must provide or confirm before bilateral federation can proceed. It is not a declaration that every planned component is production-ready.

---

## 1. Executive handoff summary

Node 1 has built a substantial local sovereignty stack:

- a portable event-sourced continuity kernel;
- a SQLite authority adapter and crash-recovery test matrix;
- a one-way MemPalace projection boundary;
- an Arcana-NovAi WAD scaffold;
- local Ollama inference and performance instrumentation;
- Gnosis session-continuity infrastructure with a clean ledger;
- a hardened OpenCode/MCP configuration;
- a target design for Qwen3 768-D embeddings, spatial atlas, and federated Well synchronization.

The immediate federation blocker is not Node 1 compute capacity. It is **contract compatibility and trust**:

1. The Node 1 WAD manifest does not match the inspected Node 0 loader shape.
2. The Arcana WAD’s primary entity is Lilith, while the current continuity contract is for `researcher_humboldt`.
3. C6, sovereignty attestation, and WAD “signed” fields are currently policy labels/string fields, not mechanically verified cryptographic signatures.
4. Node 0’s exact Engine commit, loader source, trust roots, and current network/service state must be confirmed.
5. The current SQLite runtime is 3.46.1; production continuity requires a patched SQLite runtime (3.51.3+ or a documented fixed backport).
6. The 768-D embedding service and spatial atlas are target architecture, not live services.

No live SQLite authority should be placed on NFS. The recommended federation model is local SQLite authority on each node, plus signed event/artifact exchange.

---

## 2. Node 1 verified build state

### 2.1 Continuity kernel

Relevant files:

- `scripts/continuity_kernel.py`
- `scripts/continuity_files.py`
- `scripts/continuity_sqlite.py`
- `scripts/continuity_mempalace.py`
- `tests/test_continuity_kernel.py`
- `tests/test_continuity_sqlite.py`
- `tests/test_continuity_mempalace.py`
- `docs/CONTINUITY_KERNEL.md`

Implemented:

- portable `StateStore`, `ArtifactStore`, `EventBus`, `ModelRouter`, `Checkpoint`, and `Recovery` interfaces;
- event-sourced state authority;
- prepared-intent journal;
- POSIX single-writer lock;
- directory synchronization around atomic replacement;
- idempotency keys;
- event-ID deduplication;
- sequence collision detection;
- event-log state reconstruction;
- checkpoint rebuild;
- model/adapter provenance without changing entity identity;
- one-way MemPalace projection;
- injected `McpDrawerSink` boundary.

Crash recovery coverage includes:

- intent preparation;
- event insertion;
- state update;
- checkpoint insertion;
- post-apply journal cleanup.

The current full local test suite passes:

```text
88/88 tests
```

Important architectural invariant:

> SQLite continuity state is authoritative. MemPalace is a durable projection and retrieval surface, not the recovery source of truth.

### 2.2 SQLite adapter

The adapter uses:

- explicit transactions;
- `synchronous=FULL`;
- rollback journaling;
- deterministic event and idempotency keys;
- local POSIX storage assumptions;
- fail-closed production version policy.

Current host runtime:

```text
SQLite 3.46.1
```

Production requirement:

```text
SQLite >= 3.51.3
or documented fixed backport 3.50.7 / 3.44.6
```

The `sqlite-vec==0.1.9` extension is installed in the WanderGround venv and passes extension-load, `vec0`, insertion, and KNN smoke tests. It does not upgrade SQLite and is not a continuity authority by itself.

### 2.3 MemPalace

Current documented/measured state:

- MemPalace `3.10.0`;
- `sqlite_exact.sqlite3` backend;
- 5,047 documents;
- all current vectors measured at 384 dimensions;
- current state is local and healthy;
- the spatial atlas and 3D viewer are not live.

The current 384-D model provenance should be rechecked before a migration; repository documentation currently describes the legacy route as `nomic-embed-text` through Ollama, while the target route is Qwen3 768-D through a standalone ONNX process.

### 2.4 WAD scaffold

Relevant files:

- `wads/arcana_novai/manifest.yaml`
- `wads/arcana_novai/entities.yaml`
- `wads/arcana_novai/entities/lilith/soul.yaml`
- `wads/arcana_novai/entities/lilith/card_assignment_empress.yaml`
- `wads/arcana_novai/templates/card_entity_template.yaml`
- `wads/arcana_novai/ingestion/domains.yaml`
- `wads/arcana_novai/continuity.contract.json`
- `docs/federation/WAD_CONTRACT_BRIEF.md`

The scaffold includes:

- Arcana-NovAi WAD structure;
- Lilith entity material;
- Empress card assignment;
- a dual Entity + CardAssignment factory template;
- domain-to-wing ingestion mapping;
- a standalone continuity contract.

**Identity correction:** the Fool(0), Star(17), and World(21) assignments belong to `researcher_humboldt`; they must not be attributed to Lilith. Lilith’s current WAD assignment is Empress.

### 2.5 WAD compatibility status

The current manifest is **not proven loadable by Node 0**. The inspected loader evidence indicates the following mismatches:

- Node 1 manifest `adapters` is a list; the loader expects a mapping with a `memory` object;
- Node 1 manifest `hierarchy` is a mapping; the loader expects a string/path;
- adapter paths must conform to the Node 0 whitelist;
- the loader expects each `entities/**/*.yaml` file to expose a top-level `entity` object;
- the current `soul.yaml` and root `entities.yaml` do not prove that the Node 0 entity registry shape is satisfied.

The current WAD load test is therefore only a local contract test. It is not an Engine interoperability proof.

### 2.6 WAD integrity/provenance

Current continuity code calculates a canonical SHA-256 digest. It does **not** yet provide:

- publisher identity;
- public-key or key ID;
- signature algorithm;
- detached signature;
- trust-root distribution;
- whole-WAD tree digest;
- dependency digest;
- engine-version enforcement;
- tamper-rejection tests.

The digest proves content identity/integrity. It does not prove who published the WAD.

### 2.7 Spatial-memory target

Target architecture:

```text
Qwen3-Embedding-0.6B
→ standalone ONNX embedding service
→ 768-D vectors
→ versioned sqlite-vec atlas
→ UMAP/3D projection
```

Current status:

- `scripts/embedding_server.py` prototype exists in the working tree;
- it is not currently running;
- no production model revision/hash is pinned;
- no server test suite exists;
- the prototype needs anyio compliance review because it imports bare `asyncio`;
- no 384-D → 768-D migration ledger exists;
- no production atlas exists;
- no `make 3d-rebuild` target currently exists;
- no cross-node retrieval comparison exists.

Qwen3 supports user-defined/MRL dimensions, and an ONNX artifact is available, but the exact artifact, tokenizer, pooling, normalization, instruction handling, CPU footprint, and retrieval quality must be pinned and measured before cutover.

### 2.8 Node 1 local runtime

Current Node 1 facts:

| Component | Current state |
|---|---|
| CPU | Intel i7-13620H, 6P+4E, 10C/16T |
| RAM | 16 GB DDR5-5600, single channel |
| GPU | Intel UHD Graphics 64EU, no discrete GPU |
| Ollama | 0.33.3 |
| CPU mask | `AllowedCPUs=0-11` |
| Threads | `OLLAMA_NUM_THREADS=8` |
| Loaded models | `OLLAMA_MAX_LOADED_MODELS=1` |
| Context | 8192 inherited server context |
| KV cache | `q8_0` |
| THP | `madvise` |
| Swap | zRAM active; NVMe `/swap.img` disabled and retained for rollback |
| zRAM | zstd, priority 100, approximately 7.4 GiB observed |
| Current governor | powersave with performance EPP profile |
| Measured inference | approximately 14.4 t/s for tested 3B–4B models |

These are Node 1 measurements, not Node 0 requirements.

### 2.9 Gnosis continuity

Current state after triage:

- pause ledger clean;
- no untriaged current captured packs;
- leash healthy/slack;
- reflection status is authoritative before narrative injection;
- malformed Well records produce diagnostics.

The roadmap still contains an older statement that the ledger is degraded. That statement should be corrected before the next handoff release.

### 2.10 OpenCode/MCP configuration

Current Node 1 inventory:

- `parallel-search`
- `mempalace`
- `firecrawl`
- `context7`
- `grep_app`

The hardened Node 1/Node 0 templates were regenerated to current schema:

- top-level MCP definitions;
- `prompt` field;
- no unsupported agent fields;
- `subagent_depth: 1`.

No private keys, OAuth tokens, or live credentials belong in the USB package.

---

## 3. What Node 0 must provide or confirm

These are requests to Node 0, ordered by dependency.

### Request N0-01 — Exact Engine source and loader contract — **BLOCKER**

Provide:

- exact Node 0 Engine commit hash;
- source or reproducible bundle for the WAD loader;
- loader version and supported manifest versions;
- exact `adapters` schema and allowed adapter paths;
- exact `hierarchy` type and accepted values;
- entity file envelope expected under `entities/**/*.yaml`;
- unknown-field behavior;
- dependency ordering and cycle behavior;
- engine-version enforcement;
- whether the Engine can run on Node 1 or only Node 0.

The inferred public repository URL `https://github.com/Xoe-NovAi/omega-engine` currently returns 404, so the local Node 0 source/bundle is the authoritative reference.

### Request N0-02 — WAD entity identity decision

Node 0 must help choose one of:

1. Lilith is the primary WAD/continuity identity; or
2. Humboldt is the primary continuity identity and is explicitly bound to a Lilith WAD entity; or
3. A formal parent/child or delegation relationship is introduced.

Node 0 must not infer this from filename placement. The identity binding must be machine-readable and tested.

### Request N0-03 — Current omega-hub inventory

Provide:

- current omega-hub version/build ID;
- current MCP initialize and tools/list result;
- current tool inventory;
- enabled/disabled tools;
- tool-level authorization policy;
- current listener bind address;
- whether Node 0 MCP is currently live or only staged;
- the exact service port and endpoint name.

The previously reported 93-tool count is a dated handshake, not a current capacity claim.

### Request N0-04 — Signed C6 and publisher material

Provide:

- ratified C6 contract version;
- public key or trust-root reference;
- signature algorithm;
- detached signature or signature bundle;
- key ID and rotation/revocation policy;
- C6 payload digest;
- exact Node 0 publisher identity;
- verification command and expected output.

Current Node 0 material containing string `SIGNED` fields is not sufficient cryptographic evidence.

### Request N0-05 — Payload manifest and bundle verification

Provide:

- `PAYLOAD_MANIFEST.md`;
- SHA-256 for every file;
- bundle SHA-256;
- Git bundle prerequisites;
- exact refs/branches/tags;
- bundle creation command;
- Node 0 expected commit;
- any signature over the manifest.

Node 1 will verify before extraction:

```bash
git bundle verify <bundle>
```

A checksum ledger without signature verification proves integrity only.

### Request N0-06 — Tailscale current state

Provide:

- current tailnet policy: Grants or ACLs;
- current Node 0 tags;
- Node 0 Tailscale IP and hostname;
- advertised routes;
- `PeerExcludedByPolicy` result;
- Tailscale SSH state;
- ordinary `sshd` state;
- exact MCP/NFS/Redis reachability results.

Node 0 and Node 1 must use the canonical tags:

```text
tag:node0
tag:node1
```

Legacy tags must be removed or explicitly declared inert.

### Request N0-07 — SPIFFE/SPIRE deployment details

Provide:

- trust-domain name;
- SPIRE server/agent version;
- SPIFFE IDs and audiences for omega-hub, handoff, and publisher;
- attestation selectors;
- certificate rotation period;
- mTLS endpoint;
- expected SVID validation command;
- trust-bundle distribution method.

A single trust domain is probably sufficient for the two-node federation unless Node 0 requires independent administrative trust.

### Request N0-08 — Redis role and security

Clarify whether Redis is:

- ephemeral notification/heartbeat infrastructure only; or
- intended to carry durable events.

It must not be the durable event authority.

Provide:

- bind address;
- ACL/user policy;
- TLS/mTLS decision;
- channel names;
- message size/expiry policy;
- restart behavior;
- what happens when Redis is unavailable.

### Request N0-09 — Node 0 spatial/xyz materials

Provide or identify:

- current xyz pipeline;
- scraper and library;
- personal corpus location and consent status;
- coordinate semantics;
- embedding model/version;
- expected transfer format;
- any UMAP/3D projection code;
- current viewer status and port;
- whether Node 0 has an existing Qdrant/SQLite vector schema.

### Request N0-10 — Federation acceptance record

Provide a dated acceptance report containing:

- tags;
- ping;
- MCP initialize and real tool call;
- NFS read/write;
- Tailscale SSH versus host SSH distinction;
- `PeerExcludedByPolicy=[]` after Phase B;
- SPIRE SVID issuance;
- mTLS MCP call;
- Redis heartbeat/awareness/handoff tests;
- bundle verification;
- payload hash verification;
- C6 signature verification;
- rollback test.

---

## 4. What Node 0 is requested to receive from Node 1

The reciprocal Node 1 package is not yet a signed release. It should be assembled only after identity and loader reconciliation.

Planned Node 1 outbound contents:

1. WAD manifest after Node 0 loader reconciliation.
2. Lilith/Humboldt identity binding after decision.
3. Continuity contract aligned to the registered Entity.
4. CardAssignment files with correct entity ownership.
5. Continuity kernel source and tests.
6. SQLite adapter and fixed-runtime test evidence.
7. MemPalace projection boundary and callback contract.
8. Qwen3 ONNX model artifact, revision, checksum, and server tests.
9. 384-D → 768-D blue/green migration plan and quality report.
10. Node 1 Git bundle.
11. MemPalace/KG export with provenance.
12. Federation intake verification report.
13. Signed release envelope only after the signing mechanism is implemented.
14. Makali-N0 onboarding package (`docs/federation/makali_n0_onboarding/`, Document ID
    `FED-MAKALI-N0-ONBOARDING-20260925-01`) — the entity-practice briefing plus the
    engineering-strategy layer: `STRATEGY_AND_TECHNOLOGY_MAP.md` (comprehensive
    strategy/technology view with status, evidence, and honest gaps),
    inference-operations doctrine, model-evaluation lab with measured leaderboard,
    harness failure classes and quality gates, gnosis lifecycle and The Well,
    fast model-fetch layer, onboarding/MCP-parity checklists, and consented
    operator-vision resources.

Do not describe the current WAD as a signed, Engine-loadable package. It is currently a scaffold with unresolved loader and signature gates.

Item 14 (onboarding package) ships as a **separate unsigned documentation bundle**
alongside — not inside — the signed release envelope: it is a living working
snapshot, not a release artifact. Its operator-vision and Lilith-identity material
is **personal/proprietary** per the pack's own privacy table — physical-USB
carriage only, never a hosted provider.

---

## 5. Node 0 intake procedure for the USB pack

Node 0 should treat the USB pack as untrusted input until all checks pass.

### 5.1 Quarantine

Copy into a quarantine directory, not the production tree:

```text
node0-quarantine/
└── n1-handoff/
```

Do not extract directly into:

- `gnosis/`
- `wads/`
- `.git/`
- `data/production/`
- Node 0’s live Omega Engine configuration.

### 5.2 Verify the outer manifest

Before extraction, verify:

- file inventory;
- SHA-256 values;
- media type;
- file size;
- release ID;
- source commit;
- signature;
- signing key;
- dependency manifest;
- expiry or revocation metadata.

### 5.3 Verify the Git bundle

```bash
git bundle verify /path/to/node1.bundle
git fetch /path/to/node1.bundle <ref>:refs/remotes/node1/<ref>
```

Do not merge, checkout, or run code from the bundle during verification.

### 5.4 Verify the WAD

After loader reconciliation:

- place the WAD under a test Engine path;
- run `load_all_wads()` or the exact Node 0 equivalent;
- assert no schema/type/path/adapter errors;
- assert the expected Entity appears in the registry;
- assert the expected continuity contract is bound;
- run signed-manifest tamper tests;
- test a failed load and rollback.

### 5.5 Verify semantic artifacts

For MemPalace and embedding exports:

- verify stable source IDs;
- verify provenance and source paths;
- verify model revision and tokenizer;
- verify vector dimensions;
- verify checksums;
- verify no credentials or private keys are present.

---

## 6. Acceptance criteria for the bilateral handoff

The handoff is complete only when all applicable criteria pass.

### WAD

- [ ] Exact Node 0 Engine commit recorded.
- [ ] WAD manifest loads without type/adapter/hierarchy errors.
- [ ] Entity registration is proven by the Node 0 loader.
- [ ] Entity and continuity identity binding is explicit.
- [ ] Dependency and load order are deterministic.
- [ ] Malformed manifests fail loudly.
- [ ] Tampered files fail signature/digest checks.
- [ ] Rollback to the previous WAD succeeds.

### Continuity

- [ ] Fixed SQLite runtime is selected and recorded.
- [ ] SQLite source ID and build provenance are recorded.
- [ ] Event/state/checkpoint/intent transaction survives the crash matrix.
- [ ] Local SQLite authority is not placed on NFS.
- [ ] MemPalace projection uses the one-way boundary.
- [ ] Projection cursor/retry state is durable.
- [ ] A non-OpenCode process can recover identity, mission, todos, decisions, and artifacts.
- [ ] Model/provider swap changes provenance but not identity.

### Spatial memory

- [ ] Exact ONNX artifact revision and checksum pinned.
- [ ] Embedding server passes unit, health, and cosine tests.
- [ ] 768-D output is finite, normalized, and reproducible.
- [ ] Existing 384-D corpus is exported without mutating the live palace.
- [ ] Shadow 768-D index is built separately.
- [ ] Retrieval parity/quality thresholds are recorded.
- [ ] Deletes, updates, and KG supersession are projected correctly.
- [ ] Rollback to the 384-D index remains available.

### Federation

- [ ] Bundle prerequisites verify.
- [ ] Payload manifest hashes match.
- [ ] C6 and WAD signatures verify cryptographically.
- [ ] Tailscale Grants/ACLs are explicit and deny-by-default after lockdown.
- [ ] Live tags match policy tags.
- [ ] MCP application authorization succeeds.
- [ ] SPIRE SVIDs issue and mTLS succeeds.
- [ ] Tailscale SSH and host SSH are separately reported.
- [ ] Redis is proven to be notification-only unless a durability design is approved.
- [ ] `well-import` and deduplication pass across nodes.
- [ ] Explicit publish/approval gate prevents automatic merge.
- [ ] Cross-node WAD and semantic compatibility tests pass.

---

## 7. Security and privacy constraints

- Do not include private keys, OAuth tokens, API keys, SSH keys, or live credentials.
- Do not treat string `SIGNED` fields as cryptographic verification.
- Do not treat tailnet reachability as authentication.
- Do not treat mTLS as replay protection; handoff events still need ID, cursor, expiry, and conflict rules.
- Do not make Redis the durable event store.
- Do not mount one live SQLite continuity database from two hosts over NFS.
- Do not use uncoordinated dual writes to MemPalace, Qdrant, and sqlite-vec.
- Use one source event authority and idempotent projections.
- Keep the 384-D index until the 768-D migration acceptance gate passes.
- Keep all historical claims dated and labeled; do not convert historical handshakes into current capacity claims.

---

## 8. Recommended first action after delivery

1. Node 0 provides the exact Engine commit and WAD loader source.
2. Node 0 and Node 1 reconcile the manifest shape in a test fixture.
3. Node 0 confirms the EntityRegistry behavior with a minimal WAD.
4. Both nodes decide and record the Lilith/Humboldt identity binding.
5. Node 0 provides the C6/publisher trust material.
6. Node 1 produces a corrected, signed WAD release candidate.
7. Both nodes run the WAD acceptance test.
8. Only then proceed to continuity runtime and spatial migration work.

The USB report is a handoff and alignment instrument. It does not authorize production merge, remote execution, or trust of unsigned payloads.

---

## 9. Local provenance and source references

### Repository state

At report preparation time:

```text
branch: node1/all-5-mcp-green
working tree: dirty
```

Important uncommitted/current-working-tree materials are not automatically release artifacts. Before packaging, review and stage only intended files. In particular, review:

- `scripts/continuity_mempalace.py`
- `tests/test_continuity_mempalace.py`
- `scripts/embedding_server.py`
- `scripts/check_docs.py`
- current WAD/entity additions
- model artifacts
- documentation changes

### Key local references

- `docs/federation/INTAKE_MANUAL.md`
- `docs/federation/ACL_POLICY.md`
- `docs/federation/WAD_CONTRACT_BRIEF.md`
- `docs/federation/NODE0_NEEDS_LILITH.md`
- `docs/federation/node0_received/PAYLOAD_MANIFEST.md`
- `docs/federation/node0_received/INGESTION_REPORT.md`
- `scripts/federation/intake_node0.py`
- `docs/research/KNOWLEDGE_GAPS_IMPLEMENTATION_GUIDE.md`
- `docs/research/EMBEDDING_MODEL_DECISION.md`
- `wads/arcana_novai/continuity.contract.json`

### External references used for the research

- SQLite WAL and WAL-reset defect: https://sqlite.org/wal.html
- SQLite 3.51.3 release: https://sqlite.org/releaselog/3_51_3.html
- SQLite atomic commit: https://sqlite.org/atomiccommit.html
- Git bundle verification: https://git-scm.com/docs/git-bundle
- Tailscale ACL examples: https://tailscale.com/docs/reference/examples/acls
- Tailscale Grants versus ACLs: https://tailscale.com/docs/reference/grants-vs-acls
- Qwen3 Embedding model card: https://huggingface.co/Qwen/Qwen3-Embedding-0.6B
- Qwen3 ONNX community artifact: https://huggingface.co/onnx-community/Qwen3-Embedding-0.6B-ONNX
- SPIFFE overview: https://spiffe.io/docs/

---

**End of report.**
