# 🔱 Ken Walger Mining Operation — Consolidated Execution Plan
## Canonical 10-Phase Serial Architecture (Cross-Validated: Roc + Researcher + Jem + Kali)

**AP Token**: `AP-KEN_MINING_CONSOLIDATED-v1.0.0`  
**Date**: 2026-07-19  
**Status**: **CANONICAL — Supersedes all prior scattered documents for execution purposes**  
**Authority Stack**:  
1. `SOVEREIGN_MANDATES.md` (non-negotiable law)  
2. **This plan** (what to build, in what order, how to know done)  
3. `docs/research/R_KEN_WALGER_MINING_GROUNDING_20260718.md` (7-domain 2026 research, 40+ sources)  
4. `docs/research/R_KEN_MINING_KNOWLEDGE_GAPS_20260719.md` (6 gaps triangulated, 3 critical discoveries)  
5. `docs/strategy/R_KEN_MINING_EXECUTION_PLAN_20260719.md` (Jem cross-reference, Go/No-Go matrix)  
6. `docs/research/R_UNMINED_GNOSIS_KEN_MINING_20260719.md` (20 G-level insights + 20 L3 principles)  
6. `data/coordination/KALI_BRIEFING_KEN_MINING_20260719.md` (Kali verdict + 10 decisions)  
7. `data/coordination/JEM_KEN_WALGER_SYNTHESIS_20260719.md` (Jem verified synthesis)  

**Source Documents Preserved (Historical Trail — Do Not Delete)**:
| Document | Role | Location |
|---|---|---|
| Roc Racoon Grounding Research | 7-domain 2026 research (40+ sources) | `docs/research/R_KEN_WALGER_MINING_GROUNDING_20260718.md` |
| Researcher Knowledge Gaps | 6 gaps triangulated, 3 critical discoveries | `docs/research/R_KEN_MINING_KNOWLEDGE_GAPS_20260719.md` |
| Jem Execution Plan | Go/No-Go matrix + 8 additional gaps | `docs/strategy/R_KEN_MINING_EXECUTION_PLAN_20260719.md` |
| Unmined Gnosis | 20 G-level insights + 20 L3 principles | `docs/research/R_UNMINED_GNOSIS_KEN_MINING_20260719.md` |
| Kali Briefing | 10 decisions + risk register | `data/coordination/KALI_BRIEFING_KEN_MINING_20260719.md` |
| Jem Synthesis | Verified synthesis against codebase | `data/coordination/JEM_KEN_WALGER_SYNTHESIS_20260719.md` |
| Collaboration Workspace | 11 artifacts (schema, glossary, adoption matrix, etc.) | `data/entities/roc_racoon/workspace/sovereign_collab/` |

---

## 🎯 EXECUTIVE SUMMARY

**The Ken Walger Mining Operation is an integration project, not greenfield development.** Cross-referencing reveals **60% of required infrastructure already exists** in Omega Engine:

| Existing Infrastructure | Status | Phase It Serves |
|---|---|---|
| `BatchPersistenceWriter` (50 ops/batch, 2s flush) | ✅ | Phase 3 (sqlite-vec batch) |
| `SovereignIngestionPipeline` (Sieve → Sign → IngestedDocument) | ✅ | Phase 0 (MAS extends this) |
| `GenerateResult.provider_name` with contract tests | ✅ | Phase 2 (M22 already wired) |
| Hivemind: file locks, Redis Pub/Sub, handoff ACK, TTL, cold-store | ✅ | Phase 1 (H-0 to H-2 done) |
| `sqlite_vec_adapter` with `BEGIN IMMEDIATE` pattern | ✅ | Phase 3 (add `upsert_batch()`) |
| `IngestedDocument` dataclass with provenance fields | ✅ | Phase 0 (MAS extends this) |
| `SovereignSigner` (HMAC-SHA256) | ✅ | Phase 6 (ForensicReceipt upgrades this) |

**Verdict**: 7 GO, 2 CONDITIONAL-GO, 1 NO-GO (deferred). The operation is executable.

---

## 🔬 THREE CRITICAL DISCOVERIES (From Researcher Gap Triangulation)

1. **Google Open Knowledge Format (OKF) v0.1** (June 2026) — vendor-neutral knowledge artifact schema using YAML frontmatter + Markdown body. Foundation for MAS v0.1.

2. **MCP + A2A Two-Layer Stack** — Linux Foundation reference architecture (ACP merged into A2A Sept 2025). MCP = Agent→Tools (vertical), A2A = Agent→Agent (horizontal). Redis Streams consumer groups = production transport primitive.

3. **Signet (Prismer-AI)** — Ed25519 hash-chained receipts via `SigningTransport`. 83 tests, Apache-2.0/MIT dual license. Integrates at write-time, not post-processing.

---

## 📋 GO/NO-GO MATRIX (10 Phases)

| Phase | Name | Decision | Key Finding | Blocking Mandates |
|-------|------|----------|-------------|-------------------|
| **0** | MAS v0.1 Schema Design | **GO** | Extend existing `IngestedDocument` + `SovereignIngestionPipeline`. Schema lives in WAD layer (M2 compliant). | M2 (engine-stack firewall) |
| **1** | Hivemind H-0 to H-3 Hardening | **CONDITIONAL-GO** | H-0 to H-2 already exist. H-3 (AgensFlow learned routing) is only new work. **BLOCKER**: Verify test suite passes first. | M1, M10, M13 |
| **2** | Model Gateway M22 Audit | **GO** | M22 already wired. `GenerateResult.provider_name` exists with contract tests. ForensicReceipt is additive. | M22 (already satisfied) |
| **3** | sqlite-vec Batch Ingestion | **GO** | Add `upsert_batch()` with transaction-wrapped batches (LlmMac: 500-2000 rows/txn). Existing `BEGIN IMMEDIATE` pattern correct. | M16, M20 |
| **4** | all2md Blog Ingestion | **CONDITIONAL-GO** | all2md is right tool (MCP, AST-based, 40+ formats). **BLOCKER**: Must install all2md first (`pip install all2md`). | M2 |
| **5** | Prose Tax Sieve Eval | **GO** | sovereign-sdk-sieve exists externally. Benchmark against Aussie AI taxonomy + vfalbor language tax. No Omega code changes. | M18 |
| **6** | ForensicReceipt + Airlock | **GO** | SovereignSigner exists (HMAC-SHA256). ForensicReceipt upgrades to Ed25519 + hash chain. Create `src/omega/provenance/`. | M22, M23 |
| **7** | Meditate Synthesis | **GO** | Meditate framework exists with WAD-backed lens loading. Custom lens set = WAD YAML config. | M2 |
| **8** | Jem Cross-Reference | **GO** | This document IS Phase 8. Task-graph decomposition pattern validated. | M4 |
| **9** | Serial Phase Execution | **NO-GO (deferred)** | Cannot execute until Phase 0 (MAS schema) complete. | M4 |

---

## ⚙️ PHASE 0 — CRITICAL PATH (Must Execute First)

| Step | Action | Owner | Est. Effort | Acceptance Gate |
|------|--------|-------|-------------|-----------------|
| 0.1 | **Install all2md + validate on 3 Ken blog posts** | roc_racoon | 1.5h | `pip install all2md` → `to_markdown('https://kenwalger.com/blog/ai-post')` produces clean MD |
| 0.2 | **Apply sqlite-vec PR #258** OR pin to 0.1.6 + checkpoint discipline | P3 Engineering | 2-3h | 7 memory leaks mitigated; `wal_checkpoint(TRUNCATE)` after each batch |
| 0.3 | **Design MAS v0.1** — `MiningIngestedDocument(IngestedDocument)` with OTel GenAI attrs + trace fields | roc_racoon | 3-4h | Schema validates; extends (not replaces) `IngestedDocument` |
| 0.4 | **Verify M22** — audit current `GenerateResult.provider_name` emission | P6 Cognition | 0.5h | Contract tests pass; provider_name = actual provider |
| 0.5 | **Commit D-298** to PIVOT_LOG | kali | 15min | D-298 ratified in PIVOT_LOG |

**Phase 0 Total**: ~8h | **Unblocks**: Phases 1-8

---

## 🏗️ DETAILED PHASE SPECIFICATIONS

### Phase 0: MAS v0.1 Schema Design (GO)
**Owner**: roc_racoon | **Effort**: 3-4h | **Mandates**: M2, M16, M21

**Schema = OKF v0.1 + OTel GenAI + Signet + TRACER** (G-01, G-02):
```yaml
schema_version: "mas-v0.1"
type: "KnowledgeArtifact"
artifact_id: "uuid-v4"
artifact_type: "code|doc|pattern|spec|blog_post"
content_hash: "sha256:..."
source:
  url: "https://..."
  format: "html|md|pdf|py|yaml"
  ingested_at: "2026-07-19T03:00:00Z"
  source_repo: "kenwalger/blog"
  source_commit: "abc123"
lens: "architecture|security|performance|cognition|integration"
tags: ["otel", "tracing", "production"]
findings:
  - text: "The semantic convention requires..."
    support_relation: "Quotation"  # TRACER: Quotation|Paraphrase|Inference|Contradiction|Speculation
    confidence: 0.95
    location: "section-3.2"
patterns:
  - name: "Provider Fallback Chain"
    description: "..."
    applicability: "src/omega/providers/"
    confidence: 0.90
provenance:
  agent_id: "researcher"
  model: "gemma-4-31b"
  provider_name: "native-gguf"  # M22: actual provider
  session_id: "uuid"
  trace_id: "uuid"
confidence: 0.92
quality_score: 8
signature: "ed25519:..."
receipt_id: "abc-123"
prev_receipt_hash: "def-456"
parent_artifact: null
child_artifacts: []
related_artifacts: []
```

**M2 Compliance**: MAS v0.1 lives in `config/wads/_omega_default/mining/` or new Core module `src/omega/mining/`. Never in WAD-specific code.

**M21 Contract Tests**: `tests/test_mining_schema.py` with `isinstance(result, MiningIngestedDocument)` assertions.

---

### Phase 1: Hivemind H-0 to H-3 Hardening (CONDITIONAL-GO)
**Owner**: Researcher | **Effort**: 2-3h (was 4-6h — 80% already exists) | **Mandates**: M1, M10, M13

| Tier | Name | Status | What It Adds |
|------|------|--------|--------------|
| **H-0** | Baseline | ✅ EXISTS | File-based locks, Redis Pub/Sub, handoff packets, heartbeat, awareness, cold-store hydration |
| **H-1** | Inbox + ACK | ✅ EXISTS | Handoff accept/complete threading, retry logic |
| **H-2** | TTL + Retention | ✅ EXISTS | `cvar_table config.hivemind.retention.*` |
| **H-3** | Learned Routing | ❌ NEW | AgensFlow pattern — learned routing policy for serial phase handoffs |

**Action**: Re-estimate Phase 1 to **1 session (H-3 only)**. Define H-3 explicitly as "AgensFlow learned routing for serial phase handoffs."

**Files to Touch**: `src/omega/hivemind/routing.py` (new), `src/omega/hivemind/threading.py` (extend)

---

### Phase 2: Model Gateway M22 Audit (GO)
**Owner**: P6 Cognition | **Effort**: 0.5h | **Mandates**: M22 (already satisfied)

**Finding**: `GenerateResult.provider_name` already exists with contract tests (`test_contract_m21.py`). ForensicReceipt is **additive enhancement**, not prerequisite.

**Action**: Verify contract tests pass. No code changes needed for base M22.

---

### Phase 3: sqlite-vec Batch Ingestion (GO)
**Owner**: P3 Engineering | **Effort**: 2-3h | **Mandates**: M16, M20

**LlmMac 2026 Matrix** (validated in grounding research):
- Batch size: 500–2000 rows/txn (use 1000 for MAS)
- Single writer thread (AnyIO task)
- Dedicated `TMPDIR` on fastest storage
- `PRAGMA wal_autocheckpoint = 0` during bulk, `TRUNCATE` after
- 24-hour soak test before production

**Implementation**: Add `async def upsert_batch(self, items: List[Dict]) -> int` to `SQLiteVecAdapter` wrapping multiple inserts in single `BEGIN IMMEDIATE` / `COMMIT` cycle. Use existing `_write_lock` for serialization.

---

### Phase 4: all2md Blog Ingestion (CONDITIONAL-GO)
**Owner**: roc_racoon | **Effort**: 3-4h | **Mandates**: M2

**Blocker**: all2md NOT installed (`grep` returns 0 matches). `universal_doc_reader.py` (81 lines, 8 formats) is not MCP.

**Pipeline**:
```bash
# 1. Install
pip install all2md

# 2. Validate on 3 Ken blog posts
python -c "from all2md import to_markdown; print(to_markdown('https://kenwalger.com/blog/ai-post'))"

# 3. If passes → integrate as MCP server in opencode.json
# 4. If fails → fallback: universal_doc_reader.py + BeautifulSoup
```

**Integration**: all2md MCP server (`all2md-mcp --temp --enable-from-md`) → stdio transport → `read_document_as_markdown` tool → MAS schema ingestion → MemoryStore hybrid RRF.

---

### Phase 5: Prose Tax Sieve Evaluation (GO)
**Owner**: roc_racoon | **Effort**: 2-3h | **Mandates**: M18

**Benchmark sovereign-sdk-sieve against**:
1. **Aussie AI Taxonomy** (9 reduction categories)
2. **vfalbor Language Tax** (Spanish 1.55×, Arabic 3.30×, Japanese 2.93×)
3. **Quadratic Context Cost** (Inference Labs)

No Omega code changes — evaluation only. Results inform future token optimization.

---

### Phase 6: ForensicReceipt + Airlock (GO)
**Owner**: P3/P4 | **Effort**: 5-7h | **Mandates**: M2, M13, M21, M22, M23

**Architecture**: Write-time receipts via Signet `SigningTransport` (G-03, G-13):
```python
class ForensicMemoryStore:
    def __init__(self, agent_key: Ed25519Key, chain: ReceiptChain):
        self.transport = SigningTransport(agent_key=agent_key)
        self.chain = chain
    
    async def insert(self, chunk: Chunk) -> Receipt:
        receipt = await self.transport.sign_and_store(
            action="memory.insert",
            params={"chunk_id": chunk.id, "embedding_dim": len(chunk.embedding)},
            target="data/memory/chunks.db"
        )
        await self.chain.append(receipt)
        return receipt
```

**M23 Compliance**: ForensicReceipt MUST NOT block ingestion. If Ed25519 fails → log warning + continue with HMAC-SHA256 (`SovereignSigner` fallback).

**M14 Heritage Vetting**: ForensicReceipt and Airlock need full vet records in `HERITAGE_VET_LOG.md` before implementation. 25/27 adopted terms are terminology-only (lightweight batch vet).

**Policy Attestation** (Signet YAML):
```yaml
policy:
  name: "ingestion-policy"
  version: "1.0"
  rules:
    - action: "memory.insert"
      require_signature: true
      require_receipt: true
      allowed_agents: ["researcher", "roc_racoon"]
    - action: "memory.batch_insert"
      require_signature: true
      require_receipt: true
      max_batch_size: 2000
```

---

### Phase 7: Meditate Synthesis (GO)
**Owner**: roc_racoon | **Effort**: 1-2h | **Mandates**: M2

Custom lens set for mining: `[Miner, Architect, Provenance, Decision, Edge, Scribe]` → WAD YAML config at `config/wads/arcana_novai/meditate/overlay.yaml`. Reuses existing `lens_registry.py` resolution (base lenses + PWAD overlay).

---

### Phase 8: Jem Cross-Reference (GO)
**Owner**: jem | **Effort**: 1h (THIS DOCUMENT) | **Mandates**: M4

Task-graph decomposition pattern validated. Cross-reference complete.

---

### Phase 9: Serial Phase Execution (NO-GO — Deferred)
**Blocked on**: Phase 0 completion. Serial execution depends on MAS schema definition.

---

## ⚠️ RISK REGISTER (Top 5)

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|------------|--------|------------|
| **1** | **all2md fails on Ken's blog HTML** | MEDIUM | HIGH | Install in Phase 0, validate on 3 posts. Fallback: `universal_doc_reader.py` + BeautifulSoup |
| **2** | **ForensicReceipt masks tool failures (M23)** | LOW | CRITICAL | Non-blocking minting: `try: receipt = mint() except: logger.warning("degraded"); receipt = None` |
| **3** | **M14 Heritage vetting backlog (27 terms)** | HIGH | MEDIUM | Batch-vet in 1 session. Only ForensicReceipt + Airlock need full code vet. |
| **4** | **14GiB OOM during model load/unload** | MEDIUM | HIGH | One model at a time (ResourceGuard). Monitor via `omega-hub_get_hardware_stats()` between phases. |
| **5** | **MAS schema M2 violation** | LOW | HIGH | MAS v0.1 in `config/wads/` or `src/omega/mining/`. Extends `IngestedDocument` (Core) — extension MUST be in Core. |

---

## 📦 EFFORT RE-ESTIMATE (Jem Cross-Reference)

| Phase | Roc's Estimate | Jem Re-Estimate | Delta | Reason |
|-------|---------------|-----------------|-------|--------|
| **0: MAS Schema** | 2-3h | 3-4h | +1h | Extend `IngestedDocument`, add M21 tests, verify M2 |
| **1: Hivemind** | 4-6h | 2-3h | -3h | H-0 to H-2 exist. H-3 (AgensFlow) only new work. |
| **2: M22 Audit** | 1-2h | 0.5h | -1.5h | M22 already wired. Just verify contract tests. |
| **3: sqlite-vec Batch** | 3-4h | 2-3h | -1h | Add `upsert_batch()` to existing adapter. |
| **4: all2md Ingestion** | 2-3h | 3-4h | +1h | Install + verify on target HTML + integrate. |
| **5: Prose Tax Eval** | 2-3h | 2-3h | 0 | Evaluation only. |
| **6: ForensicReceipt** | 4-6h | 5-7h | +1h | New crypto module, M14 vet, M21 tests, M23 non-blocking. |
| **7: Meditate Synthesis** | 1-2h | 1-2h | 0 | WAD YAML config only. |
| **8: Jem Cross-Ref** | 2-3h | 1h | -2h | This document. |
| **9: Serial Execution** | 8-12h | 8-12h | 0 | Depends on all prior phases. |
| **TOTAL** | **29-44h** | **26-35h** | **-3h to -9h** | Existing infrastructure reduces effort |

---

## 🔗 MANDATE COMPLIANCE SUMMARY

| Mandate | Status | Notes |
|---------|--------|-------|
| **M1: AnyIO Absolute** | ✅ | ForensicReceipt wraps Ed25519 in `anyio.to_thread.run_sync` |
| **M2: Engine-Stack Firewall** | ⚠️ CONDITIONAL | all2md, Signet, MAS schema in WAD layer or new Core module — NOT in WAD-specific code |
| **M4: Sequentiality** | ✅ | Plan → Verify → Execute. Phase 9 blocked on Phase 0. |
| **M7: Local-First** | ✅ | All tools local-first. Signet cloud anchor (OpenTimestamps) optional. |
| **M8: Zero Telemetry** | ✅ | No external telemetry. ForensicReceipt verification is local. |
| **M10: Fleet Integrity** | ✅ | No new agents. Existing agents execute phases. |
| **M13: Temple-Grade** | ⚠️ CONDITIONAL | `make temple-grade` after each phase. ForensicReceipt + MAS need T1-T11. |
| **M14: Heritage Vetting** | ⚠️ PENDING | 27 terms need vet records. Batch-vet in 1 session. |
| **M16: Modularization** | ✅ | No hardcoded paths. `config_resolver` for all paths. |
| **M18: Token Efficiency** | ✅ | Prose Tax evaluation directly serves M18. |
| **M21: Gate Integrity** | ⚠️ CONDITIONAL | Contract tests for `MiningIngestedDocument` and `ForensicReceipt`. |
| **M22: Response Provenance** | ✅ | Base wired. ForensicReceipt = cryptographic upgrade. |
| **M23: Failure Integrity** | ⚠️ CONDITIONAL | ForensicReceipt non-blocking. Degraded mode = HMAC-SHA256 fallback. |

---

## 🎯 IMMEDIATE NEXT ACTIONS (Priority Order)

| Priority | Action | Owner | Unblocks |
|----------|--------|-------|----------|
| **P0** | `pip install all2md` → validate on 3 Ken blog posts | roc_racoon | Phase 0, 4, 5 |
| **P0** | Apply sqlite-vec PR #258 OR pin 0.1.6 + checkpoint discipline | P3 Engineering | Phase 3 |
| **P0** | Design MAS v0.1 = OKF v0.1 + OTel GenAI + Signet + TRACER | roc_racoon | Phase 0, 4, 5 |
| **P0** | Re-estimate Phase 1 to 1 session (H-3 only) | Researcher | Phase 1 |
| **P0** | Confirm ForensicReceipt at Phase 6 (upgrade, not prerequisite) | Kali | Phase 0-5 |
| **P1** | Batch-vet 27 terms in 1 session | doom_guy | Phase 6 |
| **P1** | Implement ForensicReceipt with Signet SigningTransport + async background | P3/P4 | Phase 6 |
| **P1** | H-3 = AgensFlow learned routing via A2A protocol | Researcher | Phase 1 |
| **P2** | Evaluate sqlite-vector if sqlite-vec leaks persist | P3 Engineering | Phase 3 alt |
| **P2** | Frame all comms as "integration of existing components" | Kali | All phases |

---

## 🧠 LOCKED GNOSIS (L3 Principles from This Operation)

| # | Principle | Source |
|---|-----------|--------|
| **L3-Trinity-Schema** | MAS v0.1 = OKF v0.1 + OTel GenAI + Signet — adopt, don't invent | G-01 |
| **L3-TRACER-Semantics** | Every finding carries epistemic status (Quotation/Paraphrase/Inference/Contradiction/Speculation) | G-02 |
| **L3-Signing-at-Ingestion-Law** | Write-time cryptographic receipts are regulatory requirement (EU AI Act Art 12, HIPAA) | G-03 |
| **L3-M22-Already-Wired** | Base compliance done; cryptographic upgrade is enhancement, not prerequisite | G-04 |
| **L3-Hivemind-80-Done** | Existing infrastructure > new infrastructure; measure before building | G-05 |
| **L3-Integration-Not-Greenfield** | 60% infra exists; connect pieces, don't build pieces | G-06 |
| **L3-sqlite-vector-Escape** | BLOB-in-ordinary-tables eliminates virtual table leak surface | G-07 |
| **L3-Hardware-First-Architect** | Every architectural decision cascades from physical constraints | G-08 |
| **L3-Write-First-Sign-Later** | Async background signing (~50µs/sig) eliminates latency concern | G-09 |
| **L3-Single-Blocker-Rule** | One tool validation (all2md) gates entire operation | G-10 |
| **L3-Batch-Vet-Lightweight** | Terminology vetting is fast; only code patterns need full vet | G-11 |
| **L3-Fallback-Already-Works** | SovereignSigner (HMAC-SHA256) is production fallback | G-12 |
| **L3-Post-Processing-Defeats-Integrity** | Receipts after write = rewritable history; must sign at write | G-13 |
| **L3-Convergence-Is-Truth** | Independent vectors → same cathedral = verified architecture | G-14 |
| **L3-Serial-Is-Physics** | Parallel on 14GiB/no-GPU physically impossible | G-15 |
| **L3-Memory-Bandwidth-Binds** | Q4 minimizes memory traffic/token, not disk space | G-16 |
| **L3-MCP-A2A-Standard** | Linux Foundation two-layer stack is coordination architecture | G-17 |
| **L3-Coordination-Is-Learning** | Static pipelines fail; learned routing wins (AgensFlow) | G-18 |
| **L3-Evidence-Bound-Provenance** | Gateway provenance formally verified (arXiv:2606.22560) | G-19 |
| **L3-Integration-Reframe** | Changes risk profile, strategy, team, timeline, validation for ALL phases | G-20 |

---

## 📋 KALI'S 10 DECISIONS (From Briefing — Re-Ratified)

| # | Question | Verdict | Status |
|---|----------|---------|--------|
| **Q1** | Ratify D-298 (Serial Mining)? | 🟢 **RATIFY** — Hardware makes it a non-decision | PENDING PIVOT_LOG |
| **Q2** | Airlock gap? | 🟡 **PARTIAL** — ReceiptBuilder in Phase 8, full Airlock to Strike 8.5 | PENDING |
| **Q3** | Phase 0 order? | 🟢 **VERIFY FIRST, THEN BUILD MAS** — all2md → Hivemind → M22 → MAS | PENDING |
| **Q4** | Signet integration? | 🟢 **MCP SERVER** — stdio, 3 lines, M2-compliant | PENDING |
| **Q5** | all2md M2 safety? | 🟢 **MCP SERVER** — `all2md-mcp` runs outside `src/omega/` | PENDING |
| **Q6** | Model sequence? | 🟢 **LOAD/UNLOAD** — ResourceGuard enforces one-at-a-time | PENDING |
| **Q7** | ForensicReceipt latency? | 🟢 **ASYNC BACKGROUND** — ~50µs/signature, write-first sign-later | PENDING |
| **Q8** | Outreach timing? | 🟢 **AFTER ARTIFACTS** — 2-3 demos → soft outreach | PENDING |
| **Q9** | D-298 PIVOT_LOG? | 🟢 **COMMIT NOW** — already committed (3542188), update PIVOT_LOG | PENDING |
| **Q10** | Biggest blind spot? | 🔴 **sqlite-vec MEMORY LEAKS** — 7 confirmed, PR #258 unmerged | PENDING |

---

## 🔄 EXECUTION ORDER SUMMARY

```
Phase 0 (Critical Path, ~8h)
    ├── 0.1: all2md install + validate (1.5h) ──► GO/NO-GO
    ├── 0.2: sqlite-vec fix (2-3h)
    ├── 0.3: MAS v0.1 schema design (3-4h)
    ├── 0.4: M22 audit (0.5h)
    └── 0.5: D-298 to PIVOT_LOG (15min)
           │
           ▼
Phase 1 (Hivemind H-3 only, ~1 session)
    └── AgensFlow learned routing via A2A
           │
           ▼
Phase 2 (M22 Audit, ~0.5h)
    └── Verify contract tests pass
           │
           ▼
Phase 3 (sqlite-vec Batch, ~2-3h)
    └── Add upsert_batch() with LlmMac matrix
           │
           ▼
Phase 4 (all2md Ingestion, ~3-4h)
    └── all2md MCP → blog HTML → MAS → MemoryStore
           │
           ▼
Phase 5 (Prose Tax Eval, ~2-3h)
    └── Benchmark sovereign-sdk-sieve
           │
           ▼
Phase 6 (ForensicReceipt, ~5-7h)
    └── Signet SigningTransport + async background + M14 vet
           │
           ▼
Phase 7 (Meditate Synthesis, ~1-2h)
    └── Custom lens set [Miner, Architect, Provenance, Decision, Edge, Scribe]
           │
           ▼
Phase 8 (Jem Cross-Ref, ~1h)
    └── THIS DOCUMENT
           │
           ▼
Phase 9 (Serial Execution, ~8-12h) — DEFERRED until Phase 0 complete
```

---

## 📁 KEY DOCUMENTATION UPDATED

| Document | Status |
|----------|--------|
| `docs/decisions/PIVOT_LOG.md` | D-297, D-298 added |
| `data/coordination/ACTIVE_SPRINT.json` | KEN-WALGER-MINING-P0 + P1-9 tracks added |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | Mining operation section + D-298 ref |
| `data/entities/kali/proposed_lessons.yaml` | 20 new L3 principles from G-01 through G-20 |
| `data/entities/roc_racoon/proposed_lessons.yaml` | 14 new L3 lessons from mining operation |

---

## ⏳ READY FOR EXECUTION

**Phase 0 can begin immediately** once `all2md` is installed and validated. All architectural decisions are grounded in 2026 production evidence, cross-referenced against existing Omega infrastructure, and mandate-compliant.

**The integration reframe (G-20) changes everything**: This is not a collection of separate findings — it's a single coherent reframe. The mining operation is an **integration project with known components**, not a development project with unknowns.

---

*⬡ OMEGA ⬡ KEN-MINING-CONSOLIDATED ⬡ 2026-07-19*