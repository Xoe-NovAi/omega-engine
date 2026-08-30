<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Project: ken-walger-mining
## ONE-TURN HYDRATION BRIEF

### ONE-LINER
**10-Phase Serial Mining Operation** — Ken Walger's complete corpus (blog, GitHub, talks, papers) → structured knowledge base. 60% infra exists, 26-35h total, Phase 0 unblocks all.

### STATUS (2026-07-19)
- **Consolidated Plan**: ✅ `docs/strategy/KEN_WALGER_MINING_CONSOLIDATED_PLAN_20260719.md`
- **Grounding Research**: ✅ `docs/research/R_KEN_WALGER_MINING_GROUNDING_20260718.md` (7 domains, 40+ sources)
- **Knowledge Gaps**: ✅ `docs/research/R_KEN_MINING_KNOWLEDGE_GAPS_20260719.md` (6 gaps, 3 critical)
- **Execution Plan**: ✅ `docs/strategy/R_KEN_MINING_EXECUTION_PLAN_20260719.md` (Jem cross-ref, Go/No-Go matrix)
- **Unmined Gnosis**: ✅ `docs/research/R_UNMINED_GNOSIS_KEN_MINING_20260719.md` (20 G-level insights + 20 L3 principles)
- **Phase 0**: ⏳ PENDING — MAS v0.1 schema + all2md install + sqlite-vec fix

### KEY FILES
| Type | Path |
|------|------|
| Consolidated Plan | `docs/strategy/KEN_WALGER_MINING_CONSOLIDATED_PLAN_20260719.md` |
| Grounding | `docs/research/R_KEN_WALGER_MINING_GROUNDING_20260718.md` |
| Gaps | `docs/research/R_KEN_MINING_KNOWLEDGE_GAPS_20260719.md` |
| Execution | `docs/strategy/R_KEN_MINING_EXECUTION_PLAN_20260719.md` |
| Gnosis | `docs/research/R_UNMINED_GNOSIS_KEN_MINING_20260719.md` |

### 10-PHASE SERIAL ARCHITECTURE
| Phase | Name | Decision | Key Finding |
|-------|------|----------|-------------|
| **0** | MAS v0.1 Schema + all2md + sqlite-vec fix | **GO** | Extend `IngestedDocument`, install all2md first |
| **1** | Hivemind H-3 (AgensFlow) | **CONDITIONAL-GO** | H-0 to H-2 exist; only learned routing is new |
| **2** | M22 Audit | **GO** | Already wired — `GenerateResult.provider_name` with contract tests |
| **3** | sqlite-vec Batch Ingestion | **GO** | Add `upsert_batch()` with LlmMac 500-2000 rows/txn |
| **4** | all2md Blog Ingestion | **CONDITIONAL-GO** | **BLOCKER**: all2md not installed — Phase 0 step 1 |
| **5** | Prose Tax Sieve Eval | **GO** | Benchmark sovereign-sdk-sieve vs Aussie AI + vfalbor |
| **6** | ForensicReceipt (Signet) | **GO** | Write-time via `SigningTransport`; async background; M23 non-blocking |
| **7** | Meditate Synthesis | **GO** | Custom lens set [Miner, Architect, Provenance, Decision, Edge, Scribe] |
| **8** | Jem Cross-Ref | **GO** | This document |
| **9** | Serial Execution | **NO-GO (deferred)** | Blocked on Phase 0 |

### CRITICAL RISKS
| Risk | Severity | Mitigation |
|------|----------|------------|
| all2md install failure | **P0** | Phase 0 step 1 — verify before proceeding |
| sqlite-vec 7 memory leaks | **P0** | Batch ingestion with LlmMac, monitor RSS |
| M14 heritage vet backlog (27 terms) | **P1** | Parallel vet pipeline, don't block mining |

### INFRASTRUCTURE REUSE (60% Exists)
| Component | Status | Reuse For |
|-----------|--------|-----------|
| `IngestedDocument` model | ✅ Exists | Extend for MAS v0.1 |
| `sqlite-vec` adapter | ✅ Exists | Batch `upsert_batch()` |
| `omega-sieve` | ✅ v0.1.0 | T1→T2→T3 extraction pipeline |
| `omega-doc-reader` | ✅ v1.0.0 | Universal doc reading |
| Hivemind H-0 to H-2 | ✅ Exists | H-3 = learned routing only |
| M22 provider provenance | ✅ Wired | Audit only |
| Meditation pipeline | ✅ Delivered | Phase 7 lens set |

### DECISIONS LOG
- **D-298**: Ken Walger Mining Operation ratified
- **D-298a**: Serial execution (not parallel) — dependency chain
- **D-298b**: Phase 0 unblocks all — MAS schema + all2md + sqlite-vec fix
- **D-298c**: all2md install is hard blocker for Phase 4
- **D-298d**: sqlite-vec batch ingestion with LlmMac (500-2000 rows/txn)
- **D-298e**: ForensicReceipt = write-time signing + async background
- **D-298f**: Meditation lens set = [Miner, Architect, Provenance, Decision, Edge, Scribe]

### BLOCKERS
1. **all2md not installed** — Phase 0 step 1 (blocks Phase 4)
2. **sqlite-vec memory leaks (7 known)** — Phase 3 mitigation
3. **M14 heritage vet backlog (27 terms)** — parallel pipeline

---

*⬡ OMEGA ⬡ CPR ⬡ ken-walger-mining ⬡ 2026-07-19*