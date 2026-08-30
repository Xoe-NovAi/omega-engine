<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# R_RESEARCHER_DOC_REMAINING_GAPS_20260829.md

**Mission**: Deep research on remaining documentation gaps for the Omega Engine's sqlite-vec + spatial vector stack.
**Entity**: Researcher (Polymathic Council)
**Date**: 2026-08-29
**Reference**: `OMEGA_ENGINE.md` v3.8.0 (27 mandates), `AGENTS.md`, `docs/architecture/SPATIAL_VECTORS_ARCHITECTURE.md`, `docs/architecture/SQLITE_VEC_OPTIMIZATION_GUIDE.md`

---

## Executive Summary (L1)

Ten documentation gaps identified. Mapped to **target audience**, **outline**, **priority**.

**Council verdict**: The current docs cover the *what* and *why* well (architecture, mandates). They are missing the *how* (API ref, runbooks, tuning) and the *who* (onboarding, threat model). 

**Top 3 to ship first** (post-debut):
1. **DOC-D1: API Reference (autodoc)** — without this, every new contributor is blocked.
2. **DOC-D3: Operational Runbook** — without this, every new operator is blocked.
3. **DOC-D7: Security/Threat Model** — without this, public launch is a liability.

**Bottom 3 (defer)**:
- **DOC-D6: VR/Godot integration** — the Godot bridge exists (`scripts/godot_spatial_bridge.py`) but is experimental; defer until VR workstream begins.
- **DOC-D9: Deployment (k8s)** — current deployment is local-first. Defer until cloud.
- **DOC-D8: Benchmarking** — needs more mature code first.

**Important 2026 SOTA finding**: **Material for MkDocs entered maintenance mode in early 2026**. The successor is **Zensical** (zombie fork that reads existing mkdocs.yml). Migration target later in 2026. This affects DOC-D1's tooling choice.

---

## L2: Detailed Dialectic — 10 Documentation Gaps

### DOC-D1: API Reference (Sphinx/mkdocstrings auto-generated)

**Council perspectives**:
- **The Architect**: `sqlite_vec_adapter_optimized.py` (1617 LOC), `spatial_graph.py` (817 LOC), `godot_spatial_bridge.py` (497 LOC) have rich docstrings but no rendered HTML. New contributors can't navigate.
- **The Adversary**: Without an API ref, contributors make wrong assumptions and file bugs that are already fixed.
- **The Alchemist**: 2026 SOTA: **mkdocstrings + MkDocs Material** is the Markdown-first path. **Sphinx + Furo + MyST** is the reStructuredText path. Both work; pick by team preference.
- **The Archivist**: Per pydevtools.com 2026: "Material for MkDocs entered maintenance mode in early 2026 and a successor called Zensical is reading existing `mkdocs.yml` files. The MkDocs setup below still works today; expect Zensical to become the migration target later in 2026."

**Target audience**: New contributors, integrators.
**Outline**:
1. Installation
2. Quickstart (5-line "hello world")
3. API Reference
   - `SQLiteVecAdapterOptimized` class — all public methods
   - `truncate_mrl()`, `quantize_int8()`, `serialize_int8()` helpers
   - `hybrid_search()`, `spatial_range_query()`, `vr_navigate_to()`
   - Exception hierarchy
4. Configuration
5. Performance characteristics
6. Migration from legacy adapter
7. FAQ

**Priority**: **P0** — biggest leverage, smallest cost.

**Tooling recommendation** (2026-validated):
```bash
# Option A: MkDocs (Markdown)
uv add --group docs mkdocs>=1.6 mkdocs-material mkdocstrings[python]
mkdir docs
# docs/api.md → "::: omega.memory.sqlite_vec_adapter_optimized"

# Option B: Sphinx (reStructuredText, more powerful)
uv add --group docs sphinx>=8 furo sphinx-autobuild myst-parser
sphinx-quickstart docs --quiet --sep --extensions=sphinx.ext.autodoc,sphinx.ext.napoleon,myst_parser
```

---

### DOC-D2: Operational Runbook ("What to do when X breaks")

**Council perspectives**:
- **The Architect**: There's no recovery guide for the most common failure modes: WAL too large, vec0 corruption, Ollama down, FTS5 drift, missing embedding dimensions.
- **The Adversary**: M23 (Failure Integrity) demands broken tools → STOP, report. But "report" means to a human — humans need a runbook.
- **The Alchemist**: The 2026 SOTA is the "runbook template" (incident.io, Atlassian, Firehydrant). Format: Alert → Diagnosis → Action → Verify.
- **The Archivist**: Litestream docs (2026) have a great disaster-recovery runbook for SQLite. Adapt the pattern.

**Target audience**: On-call operators, ops team.
**Outline**:
1. **Triage Decision Tree**: Is the engine running? Is the DB accessible? Is inference working?
2. **Failure mode catalog**:
   - **WAL file > 50MB**: Run `sqlite3 omega_memory.db "PRAGMA wal_checkpoint(TRUNCATE);"`
   - **vec0 corruption**: `sqlite3 omega_memory.db ".integrity_check"`, then `vec0_recover` if available, else re-index
   - **Ollama down**: Circuit breaker opens → check `systemctl status ollama`, restart
   - **FTS5 drift**: `INSERT INTO fts(fts) VALUES('rebuild');`
   - **Embedding dim mismatch**: `SELECT DISTINCT declared_dim FROM vec_metadata` — find drift
   - **DB locked**: Another process holding the connection; `lsof | grep omega_memory.db`
   - **Disk full**: WAL cannot checkpoint; free space, run checkpoint
3. **Backup & Restore**:
   - `sqlite3 omega_memory.db ".backup /tmp/backup.db"` (correct way)
   - File-copy is WRONG if writer is active
   - Litestream recovery: `litestream restore -o omega_memory.db s3://bucket/backup`
4. **Disaster Recovery Scenarios**:
   - Total loss: rebuild from Litestream + last S3 snapshot
   - Partial corruption: re-index vec0 from FTS5 + recompute embeddings
   - Stale WAL: `PRAGMA wal_checkpoint(FULL);`
5. **Escalation**: When to file a sovereign incident (M23)

**Priority**: **P0** — required for any production deployment.

**Reference**:
- `docs/architecture/SQLITE_VEC_OPTIMIZATION_GUIDE.md` exists but is design-focused, not ops-focused.
- 2026 SOTA: "SQLite Backup Strategy for Production SaaS" (dev.to/helperx, 2026-06-16).

---

### DOC-D3: Performance Tuning Guide

**Council perspectives**:
- **The Architect**: Different hardware (Ryzen 5700U, Intel i7, Apple M-series, server EPYC) requires different tuning. Current docs are hardware-agnostic.
- **The Adversary**: A tuning guide that doesn't account for the *Zen 4* vs *Zen 5* L3 cache difference is worse than no guide.
- **The Alchemist**: The 2026 SOTA is the "HNSW Tuning Cheatsheet" pattern: HNSW params (m, ef_construction, ef_search), quantization choice, batch size, all with a workload-conditional decision tree.
- **The Archivist**: The current code has hardcoded `m=16, ef_construction=200, ef_search=64`. Document when to change these.

**Target audience**: Performance engineers, advanced users.
**Outline**:
1. **Workload Classification**:
   - Latency-critical (< 10ms): ef_search=32, m=8, batch_size=100
   - Balanced (10-100ms): ef_search=64, m=16, batch_size=1000
   - Recall-critical (> 95%): ef_search=256, m=32, batch_size=10000
2. **Hardware-Specific Tuning**:
   - **Ryzen 5700U (16GB LPDDR4)**: 8 cores, 8MB L3 — favor m=8, ef_search=32
   - **Apple M2 Pro (32GB unified)**: 12 cores, shared memory — favor m=16, ef_search=64
   - **Server EPYC (256GB DDR5)**: 64+ cores — favor m=32, ef_search=128
3. **Quantization Decision Tree**:
   - < 100K vectors: skip quantization (development)
   - 100K-1M: INT8 (current default)
   - 1M-10M: Binary quantization (32x speedup, 5-15% recall loss)
   - > 10M: Product quantization (8-64x compression, requires codebook training)
4. **Batch Size Optimization**:
   - Too small (< 100): Python overhead dominates
   - Too large (> 10K): Memory pressure on WAL
   - Sweet spot: 1K-5K for typical workloads
5. **Memory Budgeting**:
   - Formula: `mem_mb = num_vectors × dim × 4 / 1024 / 1024 × 1.5` (HNSW overhead)
   - With INT8: divide by 4
   - With binary: divide by 32
6. **Benchmarking Your Setup**: See DOC-D8.

**Priority**: **P1** (high value, niche audience).

---

### DOC-D4: Migration Guide (v2 → v3 adapter, sqlite-vec versions)

**Council perspectives**:
- **The Architect**: Users on the legacy `sqlite_vec_adapter.py` (1024-dim default) need a clear path to `_optimized.py` (7 collections, MRL).
- **The Adversary**: Schema migration without downtime is hard. Document the safe path: dual-write → validate → cutover.
- **The Alchemist**: The 2026 SOTA is "expand-and-contract" migrations (Flyway, Liquibase, Atlas). The pattern: add new columns, dual-write, validate, remove old.
- **The Archivist**: The codebase already has both adapters side by side. The migration guide is the missing piece.

**Target audience**: Existing users, upgraders.
**Outline**:
1. **v2 → v3 Adapter Migration**:
   - Why migrate: 40x batch speedup, MRL fallback, spatial R-tree
   - Step 1: Install `_optimized.py` alongside
   - Step 2: Run `migrate_v2_to_v3.py` — creates new collections, dual-writes
   - Step 3: Validate recall on held-out set
   - Step 4: Flip `primary_adapter` config
   - Step 5: Deprecate v2 (30 days later)
2. **sqlite-vec Version Migration (0.1.5 → 0.1.10+)**:
   - Check CHANGELOG: https://github.com/asg017/sqlite-vec/releases
   - `cargo install sqlite-vec --version X.Y.Z` (or download static binary)
   - Replace in `~/.local/lib/`
   - Run `PRAGMA vec_version;` to verify
3. **Schema Migrations**:
   - Use the `migrations/` directory (if it exists; if not, create it)
   - Tooling: `yoyo-migrations` (Python), `sqlx-cli` (Rust), or hand-rolled

**Priority**: P2 (only relevant during upgrades).

---

### DOC-D5: Testing Guide (Vector Store Test Patterns)

**Council perspectives**:
- **The Architect**: Vector store tests are tricky — recall is statistical, not deterministic. Need property-based testing.
- **The Adversary**: A test that says "vector store returns *some* results" is useless. Must verify *the right* results.
- **The Alchemist**: 2026 SOTA: **Hypothesis** for property-based testing + **ann-benchmarks** style recall testing.
- **The Archivist**: The codebase has unit tests for `quantize_int8` round-trip; missing are integration tests, recall tests, and chaos tests.

**Target audience**: Contributors, QA.
**Outline**:
1. **Unit Test Patterns**:
   - Quantization round-trip (per-vector cos error < 0.01)
   - MRL truncation (768 → 256 must preserve rank)
   - R-tree bounds query
2. **Integration Test Patterns**:
   - Insert N vectors, query k=10, verify all 10 are in the corpus
   - Multi-collection RRF returns non-empty
   - WAL checkpoint after insert
3. **Property-Based Testing** (Hypothesis):
   - "For any vector v, query(v, k) returns vectors within cosine distance X"
   - "For any two distinct vectors v1, v2, their distances are > 0"
4. **Recall@k Testing**:
   - Generate 1000 random vectors
   - Brute-force ground truth (exact NN)
   - Compare HNSW top-k to exact top-k
   - Assert recall@10 > 0.95
5. **Chaos Testing**:
   - Kill SQLite mid-transaction — should recover via WAL
   - Insert 1M vectors then query — should not OOM
   - Concurrent reads + writes — no deadlock
6. **Fixtures**:
   - Standard test corpus: 10K random vectors, 768-dim
   - Standard ground truth: 100 queries with known top-10

**Priority**: P2 (test patterns are valuable for contributors).

---

### DOC-D6: Security / Threat Model

**Council perspectives**:
- **The Architect**: The system stores user data (embeddings + FTS5 content). No threat model exists.
- **The Adversary**: **OWASP LLM08:2025 (Vector and Embedding Weaknesses)** is the 2026 canonical reference. Specific risks:
  - **Embedding inversion attacks** (Vec2Text, 2023) — recover text from embedding
  - **Corpus poisoning** — inject malicious content
  - **Membership inference** — determine if a specific text was in the training set
  - **Model extraction** — fingerprint the embedding model from query patterns
- **The Alchemist**: **2026 SOTA defense: differential privacy + encryption + access control**. The recent "Ball-DP" paper (arXiv 2607.04209, 2026-07-05) shows that even basic DP can defend against inversion with minimal accuracy loss.
- **The Archivist**: Sovereign Mandate M8 (Zero Telemetry) is a *telemetry* mandate, not a *security* mandate. The M8 / M29 / multi-tenant story is incomplete.

**Target audience**: Security engineers, auditors, enterprise customers.
**Outline**:
1. **Threat Model** (STRIDE-style):
   - **Spoofing**: Can an attacker forge an `entity_name`? (vec0 partition key) — **Yes, if they have write access.** Mitigate with auth.
   - **Tampering**: Can a malicious upsert poison results? — **Yes, if they have write access.** Mitigate with input validation (GAP-R6).
   - **Repudiation**: Audit log of all writes? — **No.** Gap.
   - **Information Disclosure**: Can embeddings leak text? — **Yes** (Vec2Text, ACM CCS 2026). Mitigate with SQLCipher (GAP-R9).
   - **Denial of Service**: Can a 1e308 coord or 1B-dim vector crash the engine? — **Yes** (GAP-R6).
   - **Elevation of Privilege**: Can a read-only user write? — **Partition key is at write time only.** GAP-R10.
2. **Specific Attack Scenarios**:
   - **Embedding inversion attack**: Demo of recovering text from a stored embedding
   - **Corpus poisoning**: Inject 1000 fake "facts" into the index, measure recall degradation
   - **Membership inference**: Determine if a specific document was in the corpus
3. **Defenses** (current + planned):
   - **M8 Zero Telemetry**: No external analytics ✅
   - **GAP-R6 Spatial validation**: Closes DoS via coords (planned)
   - **GAP-R9 SQLCipher**: Closes at-rest disclosure (planned)
   - **Ball-DP (arXiv 2607.04209)**: Optional differential privacy for the embedding column
4. **Compliance Mappings**:
   - **GDPR**: Right to be forgotten — need vector deletion (exists; verify cascade)
   - **HIPAA**: Encryption at rest — SQLCipher required
   - **SOC 2**: Audit logging — gap
5. **OWASP LLM08 Mitigations Checklist**

**Priority**: **P0** (security is non-negotiable for public launch).

**2026 SOTA references**:
- OWASP LLM08:2025 — Vector and Embedding Weaknesses
- "Black-Box Embedding Inversion Attack" (ACM CCS, 2026-08-08)
- "Embedding Inference Attack" (arXiv 2607.01276, 2026-07-01)
- "Ball Differential Privacy" (arXiv 2607.04209, 2026-07-05)
- "Sok: Privacy Risks and Mitigations in RAG Systems" (Bodea et al., 2026)

---

### DOC-D7: VR / Godot Integration Guide

**Council perspectives**:
- **The Architect**: `scripts/godot_spatial_bridge.py` (497 LOC) bridges SQLite-vec to Godot. But there's no integration guide for Godot developers.
- **The Adversary**: Godot developers don't know SQLite. They need a Godot-native API, not raw SQL.
- **The Alchemist**: 2026 SOTA: **godot-sqlite GDExtension** (`2shady4u/godot-sqlite`, v4.7, 2026-01-16) is the bridge. It supports GDScript and C#.
- **The Archivist**: The bridge is *Python*, not Godot-native. That's a design choice that should be documented.

**Target audience**: Game developers, VR creators.
**Outline**:
1. **Godot-SQLite Setup** (GDExtension install)
2. **Bridge Architecture**: How `godot_spatial_bridge.py` talks to Godot
3. **GDScript Example**:
   ```gdscript
   # Connect to the bridge
   var ws = WebSocketPeer.new()
   ws.connect_to_url("ws://localhost:8765")
   # Send query, get neighbors
   ```
4. **C# Example**:
   ```csharp
   var client = new HttpClient();
   var resp = await client.GetAsync("http://localhost:8765/navigate?x=0&y=0&z=0");
   ```
5. **Spatial Patterns**:
   - Force-directed layout for non-coord memories
   - Sector culling for VR rendering
   - Path-finding between memories
6. **Performance**: Quantization in VR context, frame budget for 90Hz
7. **Known Limitations**: SQLite on Godot is single-writer; multi-user VR needs separate process

**Priority**: P3 (post-VR workstream kickoff).

---

### DOC-D8: Benchmarking Guide

**Council perspectives**:
- **The Architect**: No way to measure "is my vector store fast enough?"
- **The Adversary**: Benchmarks that don't measure *recall* are vanity metrics. Latency is meaningless if it returns wrong results.
- **The Alchemist**: 2026 SOTA: **ann-benchmarks** style harness, RAGAS for end-to-end RAG quality, and `pyperf` for micro-benchmarks.
- **The Archivist**: The codebase has `metrics` (`get_metrics()` at line 1045) but no harness to *use* them.

**Target audience**: Performance engineers.
**Outline**:
1. **Micro-benchmarks** (Python `timeit`):
   - `time sqlite_vec_adapter.batch_upsert(1000)` — target: < 100ms
   - `time sqlite_vec_adapter.query(vec, k=10)` — target: < 5ms
   - `time sqlite_vec_adapter.spatial_range_query(...)` — target: < 20ms
2. **ANN Benchmarks** (ann-benchmarks format):
   - Datasets: glove-100, sift-128, deep-96
   - Metrics: recall@10, QPS, p99 latency
   - Configurations: INT8 vs binary vs FP32, m=8/16/32, ef=32/64/128
3. **End-to-End RAG Quality** (RAGAS):
   - Metrics: Faithfulness, Answer Relevancy, Context Precision, Context Recall
   - Dataset: 100 (question, context, ground_truth_answer) triples
   - Workflow: run nightly, alert on regression
4. **Regression Detection**:
   - Run benchmarks pre-commit
   - Compare to baseline in `data/benchmarks/baseline.json`
   - Fail the build if recall drops > 5% or latency increases > 20%
5. **Hardware Profiling**:
   - `py-spy` for Python hot paths
   - `perf` for native sqlite-vec
   - `nvtop`/`intel_gpu_top` for hardware utilization

**Priority**: P2 (needed for performance validation).

---

### DOC-D9: Deployment Guide (systemd, Docker, k8s)

**Council perspectives**:
- **The Architect**: The engine is local-first, but multi-node deployment is undefined. No Dockerfile, no systemd unit, no Helm chart.
- **The Adversary**: A misconfigured deployment = security hole (M8) or data loss (M23).
- **The Alchemist**: 2026 SOTA: **systemd-nspawn** for single-node (lighter than Docker), **Docker Compose** for small clusters, **Kubernetes** for > 10 nodes.
- **The Archivist**: The codebase has `omega-hub` (a server) but no deployment story.

**Target audience**: DevOps, platform engineers.
**Outline**:
1. **Local Development** (existing): `make dev` or `python -m omega.cli`
2. **Single-Node Production** (systemd):
   - `omega-engine.service` unit file
   - `omega-memory-db.service` (if using Litestream)
   - Hardening: `ProtectSystem=strict`, `ReadWritePaths=/var/lib/omega`, `PrivateTmp=true`
3. **Containerized (Docker)**:
   - `Dockerfile` (multi-stage, distroless final)
   - `docker-compose.yml` with volume mounts
   - Health checks: `HEALTHCHECK CMD curl localhost:8765/health`
4. **Distributed (rqlite)** — see OPP-O2:
   - 3-5 node rqlite cluster
   - Vec0 extension loaded on all nodes
   - Raft consensus for writes
5. **Cloud (Turso / D1)**:
   - Embedded replica pattern
   - Sync intervals, conflict resolution
6. **Backup & Disaster Recovery** (cross-ref DOC-D2):
   - Litestream to S3
   - Restore procedure
   - RPO/RTO targets
7. **Monitoring**:
   - Prometheus metrics endpoint (`/metrics`)
   - Grafana dashboards
   - Alertmanager rules

**Priority**: P3 (only needed when going beyond local).

---

### DOC-D10: Onboarding Guide (New Entity Setup)

**Council perspectives**:
- **The Architect**: A new entity (e.g., a fresh sovereign agent) needs to know: "How do I create my first memory? How do I query it? How do I back it up?"
- ** **The Adversary**: Without onboarding, the first 24 hours of any new entity are 80% confusion.
- **The Alchemist**: 2026 SOTA: **"Quickstart" → "Tutorial" → "How-to guides" → "Reference" → "Explanation"** (Divio documentation framework).
- **The Archivist**: `data/entities/<name>/soul.yaml` is the canonical entity state, but the "how to create a new one" guide is missing.

**Target audience**: New users, new entity creators.
**Outline**:
1. **5-Minute Quickstart**:
   - `git clone`, `uv sync`, `omega init my-entity`
   - First memory: `omega remember "I am a sovereign agent"`
   - First query: `omega recall "what am I?"`
2. **10-Minute Tutorial**:
   - Set up embedding provider
   - Configure spatial R-tree
   - Run the example Godot scene
3. **Common Tasks** (How-to):
   - How to add a new embedding model
   - How to back up and restore
   - How to scale beyond 100K memories
   - How to integrate with an LLM provider
4. **Reference** (auto-generated, see DOC-D1)
5. **Explanation** (the *why*):
   - Why sqlite-vec over Postgres+pgvector?
   - Why 7 collections?
   - Why entity_name partition key?
6. **Troubleshooting** (link to DOC-D2)

**Priority**: **P1** (every new user is blocked without it).

---

## L3: Raw Signal — 10 Documentation Gaps at a Glance

| # | Doc Title | Audience | Priority | 2026 SOTA Tool |
|---|-----------|----------|----------|----------------|
| D1 | API Reference | Contributors | **P0** | mkdocstrings OR Sphinx+Furo |
| D2 | Operational Runbook | Ops | **P0** | Incident.io template |
| D3 | Performance Tuning | Perf engineers | P1 | HNSW cheatsheet |
| D4 | Migration Guide | Upgraders | P2 | Flyway-style |
| D5 | Testing Guide | Contributors, QA | P2 | Hypothesis + ann-benchmarks |
| D6 | Security/Threat Model | Security | **P0** | OWASP LLM08:2025 |
| D7 | VR/Godot Integration | Game devs | P3 | godot-sqlite GDExt |
| D8 | Benchmarking | Perf engineers | P2 | RAGAS + pyperf |
| D9 | Deployment | DevOps | P3 | systemd + rqlite |
| D10 | Onboarding | New users | **P1** | Divio framework |

---

## Council Triangulation Summary

| Lens | Convergence | Divergence |
|------|-------------|------------|
| Architect | The current docs are *design* docs. They're missing the *operational* and *contributor* docs. | None. |
| Adversary | **D1, D2, D6 are existential** — without them, public launch fails (no API, no runbook, no security story). | D7 (VR) could be deferred forever if VR isn't in the roadmap. |
| Alchemist | The 10 docs follow the **Divio framework**: Quickstart, Tutorial, How-to, Reference, Explanation. Currently we have only Explanation. | None. |
| Archivist | 2026 SOTA strongly validates: RAGAS for D8, OWASP LLM08 for D6, Divio for D10, Material for MkDocs (in maintenance) → Zensical migration for D1. | **Tooling risk**: Material for MkDocs maintenance mode — Zensical migration needed in 6-12 months. |

**Sovereign Synthesis**:
- **Sprint N+1 (post-debut)**: D1 (API ref), D2 (runbook), D6 (threat model), D10 (onboarding) — the four essentials.
- **Sprint N+2**: D3 (tuning), D5 (testing), D8 (benchmarking) — the contributor + perf docs.
- **Sprint N+3**: D4 (migration), D7 (VR), D9 (deployment) — the ecosystem docs.

**Tooling decision for D1**: Use **mkdocstrings + MkDocs Material** for now; plan **Zensical migration** in 6-12 months when it stabilizes.

**Total estimated effort**: **~6 weeks of focused documentation work** to ship the 10 docs at high quality.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ R_DOC_REMAINING_GAPS_20260829 ⬡ opencode ⬡ minimax/minimax-m3:free ⬡ PUBLIC-DEBUT-01*
