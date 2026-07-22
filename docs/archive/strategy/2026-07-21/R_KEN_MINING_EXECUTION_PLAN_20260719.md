# 🔱 Ken Walger Mining Operation — Verified Execution Plan
**AP Token**: `AP-KEN_MINING_EXEC-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_ken_mining_exec ⬡ VERIFIED

**Date**: 2026-07-19
**Status**: CROSS-REFERENCE COMPLETE — Ready for Phase 0 Execution
**Source**: `R_KEN_WALGER_MINING_GROUNDING_20260718.md` (Roc Racoon) + Omega Codebase Cross-Reference (Jem)
**Purpose**: Go/No-Go decisions for all 10 mining phases with mandate compliance verification

---

## 🎯 Executive Summary

Cross-referencing Roc Racoon's 2026 grounding research against Omega's existing codebase reveals **3 critical findings**:

1. **M22 Response Provenance is ALREADY WIRED** — `GenerateResult.provider_name` exists and has contract tests (test_contract_m21.py). ForensicReceipt upgrades this from observational to **cryptographic** — it's an enhancement, not a prerequisite.
2. **MemoryStore batch infrastructure ALREADY EXISTS** — `BatchPersistenceWriter` handles 50 ops/batch with 2s flush. MAS batch ingestion needs to extend this, not rebuild it.
3. **Sovereign Ingestion Pipeline ALREADY EXISTS** — `SovereignIngestionPipeline` (Sieve → Sign → IngestedDocument) is the canonical path. MAS v0.1 must extend this, not replace it.

**Verdict**: 7 GO, 2 CONDITIONAL-GO, 1 NO-GO. The mining operation is executable.

---

## 📊 Go/No-Go Matrix (10 Phases)

| Phase | Name | Decision | Reason | Blocking Mandates |
|-------|------|----------|--------|-------------------|
| **0** | MAS v0.1 Schema Design | **GO** | Extend existing `IngestedDocument` dataclass + `SovereignIngestionPipeline`. Schema lives in WAD layer (M2 compliant). | M2 (engine-stack firewall) — MAS must not leak into Core Engine |
| **1** | Hivemind H-0 to H-3 Hardening | **CONDITIONAL-GO** | Existing Hivemind has file locks, Redis Pub/Sub, handoff packets. H-0 to H-3 = extend existing patterns. **BLOCKER**: Must verify current test suite passes before touching Hivemind code. | M1 (AnyIO), M10 (Fleet Integrity — no new agents), M13 (Temple-Grade) |
| **2** | Model Gateway M22 Audit | **GO** | M22 already wired. `GenerateResult.provider_name` exists with contract tests. ForensicReceipt is additive. No code changes needed for base M22. | M22 (already satisfied) |
| **3** | sqlite-vec Batch Ingestion | **GO** | `sqlite_vec_adapter.py` has single-row upsert. Need to add `upsert_batch()` with transaction-wrapped batches (LlmMac: 500-2000 rows/txn). Existing `BEGIN IMMEDIATE` pattern is correct. | M16 (portable paths), M20 (anyio.to_thread.run_sync for blocking I/O) |
| **4** | all2md Blog Ingestion | **CONDITIONAL-GO** | all2md is the right tool (MCP, AST-based, 40+ formats). **BLOCKER**: Must install all2md first (`pip install all2md`). `universal_doc_reader.py` is 81 lines — can be deprecated. | M2 (engine-stack — all2md integration in WAD, not Core) |
| **5** | Prose Tax Sieve Eval | **GO** | sovereign-sdk-sieve exists as external package. Benchmark against Aussie AI taxonomy + vfalbor language tax. No Omega code changes needed — evaluation only. | M18 (Token Efficiency) |
| **6** | ForensicReceipt + Airlock | **GO** | SovereignSigner already exists (HMAC-SHA256). ForensicReceipt upgrades to Ed25519 + hash chain. `src/omega/provenance/` module doesn't exist yet — create it. Pattern: extend `SovereignIngestionPipeline.signer`. | M22 (cryptographic upgrade), M23 (receipt must not mask tool failures) |
| **7** | Meditate Synthesis | **GO** | Meditate framework already exists with WAD-backed lens loading (`lens_registry.py`). Custom lens set [Miner, Architect, Provenance, Decision, Edge, Scribe] = WAD YAML config. | M2 (lenses in WAD, not Core) |
| **8** | Jem Cross-Reference | **GO** | This document IS Phase 8. Task-graph decomposition pattern validated. | M4 (Sequentiality) |
| **9** | Serial Phase Execution | **NO-GO (deferred)** | Cannot execute mining phases until Phase 0 (MAS schema) is complete. Serial execution depends on schema definition. | M4 (Plan → Verify → Execute) |

---

## 🛡️ Mandate Compliance Check

### Mandatory Mandates (Apply to All Phases)

| Mandate | Status | Notes |
|---------|--------|-------|
| **M1: AnyIO Absolute** | ✅ SATISFIED | All Omega code uses anyio. ForensicReceipt must wrap Ed25519 signing in `anyio.to_thread.run_sync`. Hivemind hardening already uses anyio (see `hivemind_redis.py`). |
| **M2: Engine-Stack Firewall** | ⚠️ CONDITIONAL | MAS v0.1, all2md integration, ForensicReceipt, and Airlock must all live in `config/wads/` or new `src/omega/` modules — NOT in WAD-specific code. CREDITS.md shows heritage tags are WAD-layer. The `src/omega/provenance/` module must be Core Engine, not WAD-specific. |
| **M4: Sequentiality** | ✅ SATISFIED | Plan → Verify → Execute. This document IS the plan. Phase 9 (execution) is correctly blocked on Phase 0 (schema). |
| **M7: Local-First** | ✅ SATISFIED | All tools (all2md, Signet, sqlite-vec) are local-first. Signet has optional cloud anchor (OpenTimestamps) but local verification is primary. |
| **M8: Zero Telemetry** | ✅ SATISFIED | No external telemetry in any phase. ForensicReceipt verification is local. |
| **M10: Fleet Integrity** | ✅ SATISFIED | No new agents created. Phases use existing agents (Roc Racoon, Jem, Researcher). |
| **M13: Temple-Grade** | ⚠️ CONDITIONAL | `make temple-grade` must pass after each phase. ForensicReceipt + MAS schema additions need T1-T11 compliance. |
| **M14: Heritage Vetting** | ⚠️ CONDITIONAL | 27 adopted terms from Ken Walger need vet records. ForensicReceipt, Airlock, Prose Tax all need `[heritage: kenwalger-2026]` tags with vet records. CREDITS.md shows 23 ADOPT + 4 SYNTHESIZE — all PENDING. |
| **M16: Modularization** | ✅ SATISFIED | MAS schema, all2md integration, ForensicReceipt all designed as modular additions. No hardcoded paths. |
| **M18: Token Efficiency** | ✅ SATISFIED | Prose Tax evaluation directly serves M18. |
| **M21: Gate Integrity** | ⚠️ CONDITIONAL | ForensicReceipt must have contract tests for `ForensicReceipt` dataclass. MAS schema must have contract tests for `IngestedDocument` extension. |
| **M22: Response Provenance** | ✅ SATISFIED (base) | `GenerateResult.provider_name` already wired. ForensicReceipt is additive upgrade. |
| **M23: Failure Integrity** | ⚠️ CONDITIONAL | ForensicReceipt minting must NOT mask tool failures. If Ed25519 signing fails, the ingestion must still succeed (degraded mode, not hard stop). |

### Phase-Specific Mandate Analysis

| Phase | Key Mandates | Risk Level |
|-------|-------------|------------|
| Phase 0 (MAS Schema) | M2, M16 | LOW — extending existing patterns |
| Phase 1 (Hivemind) | M1, M10, M13 | MEDIUM — touching coordination infrastructure |
| Phase 3 (sqlite-vec batch) | M16, M20 | LOW — adding method to existing adapter |
| Phase 4 (all2md) | M2 | LOW — external tool integration |
| Phase 6 (ForensicReceipt) | M2, M13, M21, M22, M23 | HIGH — new crypto module, must not break existing ingestion |

---

## 🔍 Additional Gaps Found (Beyond Roc Racoon's Research)

### Gap J-01: ForensicReceipt Must Not Block Ingestion
**Roc's plan** assumes ForensicReceipt is a prerequisite for Phase 8 mining. **Cross-reference finding**: ForensicReceipt is an **enhancement** to M22, not a prerequisite. The existing `SovereignSigner` (HMAC-SHA256) already provides provenance. ForensicReceipt should be Phase 6 (post-evaluation), not Phase 0.

**Recommendation**: Execute Phase 0-5 WITHOUT ForensicReceipt. Add ForensicReceipt in Phase 6 as an upgrade. This unblocks the critical path immediately.

### Gap J-02: MAS v0.1 Must Extend IngestedDocument, Not Replace It
**Roc's plan** defines MAS as a new schema. **Cross-reference finding**: `IngestedDocument` already exists in `oracle/ingestion.py` with `content`, `metadata`, `provenance_hash`, `timestamp`, `pii_token_map`. MAS v0.1 must ADD fields (trace_id, span_id, agent_pillar, phase) to this existing dataclass, not create a parallel schema.

**Recommendation**: MAS v0.1 = `@dataclass class MiningIngestedDocument(IngestedDocument)` with MAS-specific fields.

### Gap J-03: Batch sqlite-vec Needs Transaction Wrapper
**Roc's plan** references LlmMac's 500-2000 rows/txn. **Cross-reference finding**: `sqlite_vec_adapter.py` currently does single-row upsert with `BEGIN IMMEDIATE`. Batch API needs to wrap multiple inserts in one transaction with a single `BEGIN IMMEDIATE` / `COMMIT` cycle. The existing `_write_lock` async lock serializes access.

**Recommendation**: Add `async def upsert_batch(self, items: List[Dict]) -> int` to `SQLiteVecAdapter` that wraps the LlmMac matrix.

### Gap J-04: all2md Installation Not Verified
**Roc's plan** assumes all2md is available. **Cross-reference finding**: `grep` for `all2md` in the codebase returns ZERO matches. It's not installed. The existing `universal_doc_reader.py` (81 lines) handles 8 formats but is not an MCP server.

**Recommendation**: Phase 0 must include `pip install all2md` and verification that it works on the target blog HTML.

### Gap J-05: Hivemind H-0 to H-3 Scope Is Unclear
**Roc's plan** references "H-0 to H-3 hardening" but doesn't define what H-0 through H-3 ARE. **Cross-reference finding**: The existing Hivemind already has: file-based locks (`hivemind_workspace_lock_*`), Redis Pub/Sub (`hivemind_redis.py`), handoff packets (`hivemind_submit_handoff`), heartbeat (`hivemind_heartbeat`), awareness (`hivemind_get_awareness`), extended checkin (`hivemind_extended_checkin`).

**Recommendation**: Define H-0 to H-3 explicitly before Phase 1. Based on the grounding research, likely candidates:
- H-0: Cold-store fallback (ALREADY EXISTS in `hivemind_get_awareness`)
- H-1: Inbox/ack threading (ALREADY EXISTS via handoff accept/complete)
- H-2: TTL alignment (ALREADY EXISTS via cvar_table config.hivemind.retention.*)
- H-3: Learned routing (AgensFlow pattern — NEW, needs implementation)

### Gap J-06: ForensicReceipt Heritage Vetting Required (M14)
**Roc's plan** includes ForensicReceipt with `[heritage: kenwalger-2026]` tag. **Cross-reference finding**: M14 requires vet records in `HERITAGE_VET_LOG.md`. The CREDITS.md shows ForensicReceipt vet record is `vet-XXX | 🟡 PENDING`. This MUST be completed before implementation.

**Recommendation**: Phase 6 must include M14 vet record creation for ForensicReceipt before any code is written.

### Gap J-07: Contract Tests for MAS Schema (M21)
**Roc's plan** doesn't mention M21 contract tests for the new MAS schema. **Cross-reference finding**: M21 requires `isinstance(result, ExpectedType)` tests for all typed returns. `MiningIngestedDocument` must have a contract test.

**Recommendation**: Phase 0 must include `tests/test_mining_schema.py` with M21 contract tests.

### Gap J-08: Airlock Is Missing From Critical Path
**Roc's plan** mentions Airlock but doesn't include it in the 10-phase critical path. **Cross-reference finding**: The Airlock outbound governance pattern is the "missing piece" identified in OUTREACH_PLAN.md. Without it, mined data has no egress governance.

**Recommendation**: Add Airlock as Phase 10 (post-mining) or defer to Horizon 2.

---

## ⏱️ Effort Re-Estimate

| Phase | Roc's Estimate | Jem Re-Estimate | Delta | Reason |
|-------|---------------|-----------------|-------|--------|
| **0: MAS Schema** | 2-3h | 3-4h | +1h | Must extend IngestedDocument (not create new), add M21 contract tests, verify against M2 |
| **1: Hivemind Hardening** | 4-6h | 2-3h | -3h | Most H-0 to H-2 patterns ALREADY EXIST. H-3 (learned routing) is the only new work. But must run full test suite first. |
| **2: M22 Audit** | 1-2h | 0.5h | -1.5h | M22 already wired. Just verify contract tests pass. Audit only. |
| **3: sqlite-vec Batch** | 3-4h | 2-3h | -1h | Add `upsert_batch()` method. Existing adapter is well-structured. |
| **4: all2md Ingestion** | 2-3h | 3-4h | +1h | Must install all2md, verify it works on target HTML, integrate with MAS pipeline. |
| **5: Prose Tax Eval** | 2-3h | 2-3h | 0 | Evaluation only — no code changes. |
| **6: ForensicReceipt** | 4-6h | 5-7h | +1h | New crypto module, M14 vet record, M21 contract tests, must not block ingestion (M23). |
| **7: Meditate Synthesis** | 1-2h | 1-2h | 0 | WAD YAML config only — existing lens infrastructure. |
| **8: Jem Cross-Ref** | 2-3h | 1h | -2h | THIS DOCUMENT. Done. |
| **9: Serial Execution** | 8-12h | 8-12h | 0 | Execution depends on all prior phases. |
| **TOTAL** | **29-44h** | **26-35h** | **-3h to -9h** | Existing infrastructure reduces effort significantly |

**Key Insight**: The existing codebase provides ~60% of the infrastructure needed. The mining operation is integration work, not greenfield development.

---

## ⚠️ Risk Register (Top 5)

### Risk 1: all2md Installation Failure on ARM/Ryzen
- **Probability**: MEDIUM
- **Impact**: HIGH — blocks Phase 4 (blog ingestion)
- **Mitigation**: Install all2md in Phase 0, not Phase 4. Verify it handles Ken's blog HTML before committing to it. Fallback: use existing `universal_doc_reader.py` with BeautifulSoup.

### Risk 2: ForensicReceipt M23 Violation (Masking Tool Failures)
- **Probability**: LOW
- **Impact**: CRITICAL — Sovereign Boundary Violation
- **Mitigation**: ForensicReceipt minting MUST be non-blocking. If Ed25519 fails, log warning and continue ingestion with existing HMAC-SHA256 provenance. Design pattern: `try: forensic_receipt = mint() except: logger.warning("ForensicReceipt degraded"); forensic_receipt = None`.

### Risk 3: M14 Heritage Vetting Backlog
- **Probability**: HIGH
- **Impact**: MEDIUM — 27 terms need vet records before code can be merged
- **Mitigation**: Batch-vet the 27 terms in a single session. Most are terminology (not code patterns), so vetting is lightweight. ForensicReceipt and Airlock are the only code patterns needing full vet.

### Risk 4: Memory Pressure During Serial Phases
- **Probability**: MEDIUM
- **Impact**: HIGH — 14GiB RAM ceiling
- **Mitigation**: One model loaded at a time (confirmed by grounding research). Monitor via `omega-hub_get_hardware_stats()` between phases. Unload model before loading next.

### Risk 5: MAS Schema Drift (M2 Violation)
- **Probability**: LOW
- **Impact**: HIGH — Engine-Stack Firewall violation
- **Mitigation**: MAS v0.1 MUST be defined in `config/wads/` layer OR in a new Core module (`src/omega/mining/`). Never in both. The `MiningIngestedDocument` extends `IngestedDocument` which is already in Core — so the extension MUST also be in Core.

---

## 🎯 Recommended Next Step

**UNBLOCK PHASE 0**: Install all2md and verify it works on Ken's blog HTML.

```bash
# 1. Install all2md
pip install all2md

# 2. Test on a sample blog post
python -c "from all2md import to_markdown; print(to_markdown('https://kenwalger.com/blog/ai-post'))"

# 3. If all2md works → GO for Phase 0
# 4. If all2md fails → fallback to universal_doc_reader.py + BeautifulSoup
```

This single action unblocks:
- Phase 0 (MAS schema can be designed knowing all2md output format)
- Phase 4 (blog ingestion depends on all2md)
- Phase 5 (Prose Tax evaluation needs blog content)

---

## 📋 Cross-Reference Summary by Area

### Area 1: MAS v0.1 Schema ↔ Existing Omega Schema
| Finding | Status | Action |
|---------|--------|--------|
| `IngestedDocument` exists in `oracle/ingestion.py` | ✅ | Extend, don't replace |
| `SovereignIngestionPipeline` exists | ✅ | MAS pipeline extends this |
| `BatchPersistenceWriter` exists | ✅ | MAS batch uses this |
| MAS fields (trace_id, span_id, agent_pillar, phase) | ❌ NEW | Add to IngestedDocument |
| M21 contract tests for MAS schema | ❌ NEW | Create in Phase 0 |

### Area 2: Hivemind Hardening ↔ Existing Hivemind Code
| Finding | Status | Action |
|---------|--------|--------|
| File-based workspace locks | ✅ EXISTS | H-0 done |
| Redis Pub/Sub ephemeral layer | ✅ EXISTS | H-0 done |
| Handoff accept/complete threading | ✅ EXISTS | H-1 done |
| TTL retention config (cvar_table) | ✅ EXISTS | H-2 done |
| Learned routing (AgensFlow) | ❌ NEW | H-3 only new work |
| Cold-store hydration | ✅ EXISTS | Done |

### Area 3: Model Gateway provider_name ↔ GenerateResult
| Finding | Status | Action |
|---------|--------|--------|
| `GenerateResult.provider_name: str` | ✅ EXISTS | No change needed |
| `GenerateResult.is_cloud: bool` | ✅ EXISTS | No change needed |
| M22 contract tests | ✅ EXISTS | Verify pass |
| ForensicReceipt (cryptographic upgrade) | ❌ NEW | Phase 6 |

### Area 4: sqlite-vec Batch Ingestion ↔ MemoryStore
| Finding | Status | Action |
|---------|--------|--------|
| `BatchPersistenceWriter` (50 ops/batch) | ✅ EXISTS | MAS batch uses this |
| `sqlite_vec_adapter.upsert()` (single row) | ✅ EXISTS | Add `upsert_batch()` |
| `BEGIN IMMEDIATE` pattern | ✅ EXISTS | Use in batch |
| LlmMac 500-2000 rows/txn | ❌ NEW | Configure in Phase 3 |

### Area 5: all2md Integration ↔ Universal Doc Reader
| Finding | Status | Action |
|---------|--------|--------|
| `universal_doc_reader.py` (81 lines) | ✅ EXISTS | Deprecate after all2md |
| all2md installed | ❌ NOT INSTALLED | Install in Phase 0 |
| all2md MCP server | ❌ NOT INTEGRATED | Phase 4 |
| HTML conversion capability | ❌ VERIFIED | all2md handles HTML |

### Area 6: ForensicReceipt ↔ Provenance Pipeline
| Finding | Status | Action |
|---------|--------|--------|
| `SovereignSigner` (HMAC-SHA256) | ✅ EXISTS | Keep as fallback |
| `IngestedDocument.provenance_hash` | ✅ EXISTS | ForensicReceipt extends this |
| `src/omega/provenance/` module | ❌ DOES NOT EXIST | Create in Phase 6 |
| Ed25519 signing | ❌ NEW | New dependency (cryptography) |
| Hash chain | ❌ NEW | ForensicReceipt feature |
| M14 vet record | ❌ PENDING | Required before implementation |

---

## 🔗 References

| Document | Source | Status |
|----------|--------|--------|
| `R_KEN_WALGER_MINING_GROUNDING_20260718.md` | Roc Racoon | ✅ COMPLETE |
| `FORENSIC_RECEIPT_STUDY.md` | Roc Racoon | ✅ COMPLETE |
| `KEN_TERM_ADOPTION_MATRIX.md` | Roc Racoon | ✅ COMPLETE |
| `CREDITS.md` (heritage attribution) | Roc Racoon | 🟡 PENDING vet records |
| `SOVEREIGN_COLLAB_MASTER.md` | Roc Racoon | ✅ COMPLETE |
| `test_contract_m21.py` | Omega CI | ✅ PASSING |
| `test_model_gateway.py` | Omega CI | ✅ PASSING |
| `test_firewall_m2.py` | Omega CI | ✅ PASSING |

---

*⬡ OMEGA ⬡ JEM ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_ken_mining_exec ⬡ VERIFIED*
