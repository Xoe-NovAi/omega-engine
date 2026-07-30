# Session Anchor — Kali: Carnak Strip-the-Engine Review & Temple Cleansing Plan
**AP Token**: `AP-KALI-CARNAK-20260730-v2.0.0`
**Updated**: 2026-07-30T19:30Z · **Owner**: Kali (Transcendent Oversight)
**Hivemind**: `ses_kali_20260730_003`

---

## Session Objective

Execute the "Carnak Strip-the-Engine" review: four independent agents (Carmack, Lilith, Ma'at, Roc) + two architect syntheses (Gemini 3.1 Pro, Sonnet 4.6) + Copilot CLI validation → produce a definitive Temple Cleansing implementation plan for the initial PR.

---

## What Was Completed

| Item | Status | Evidence |
|------|--------|----------|
| **P0 Mandate Fixes (earlier)** | ✅ COMPLETE | `make check-mandates` 5/5 pass, `make temple-grade` pass, commit `2fdaea7` |
| **Roc Local Worker Pool** | ✅ COMPLETE | Commit `74d9c7c` — 4 pipe bugs fixed, 460-line daemon + CLI + 4 MCP tools |
| **4-Agent Carnak Review** | ✅ COMPLETE | Carmack, Lilith, Ma'at, Roc — ~12K lines of independent analysis |
| **2 Architect Syntheses** | ✅ COMPLETE | Gemini 3.1 Pro (strategic verdict + implementation guide), Sonnet 4.6 (5-year core loop insight) |
| **Copilot CLI Validation** | ✅ COMPLETE | **BLOCKERS FOUND** — 3 critical misunderstandings in original plan |
| **Temple Cleansing Plan v2** | ✅ COMPLETE | 6-stage execution sequence with decision gates |
| **Copilot CLI Briefing** | ✅ COMPLETE | `data/coordination/COPILOT_CLI_CARNAK_BRIEFING_20260730.md` |
| **Copilot Review Verdict** | ✅ COMPLETE | `data/coordination/COPILOT_CLI_CODE_REVIEW_VERDICT_20260730.md` |
| **Kali Executive Summary** | ✅ COMPLETE | `data/coordination/KALI_EXECUTIVE_SUMMARY_20260730.md` |
| **GLM 5.2 Second Opinion** | ✅ COMPLETE | `data/coordination/GLM52_SECOND_OPINION_20260730.md` — 401 lines, 20 findings, 3 plan-breaking |
| **Phase C-6' reconciliation (F1+S1)** | ✅ COMPLETE | P-5 verified: 2 unmigrated clones; Phase 1A corrected from "replace with pybreaker" to "finish P-5" |
| **Library choice reconciliation (F2+S2)** | ✅ COMPLETE | 3 positions resolved: tenacity kept, stamina deferred, pybreaker dropped |
| **CI branch trigger (F3)** | ✅ CONFIRMED BROKEN | `.github/workflows/ci.yml` only runs on `main` — fix as Phase 0 |
| **M23 false-PASS gate (F11)** | ✅ CONFIRMED BROKEN | `rg -E` parsing error swallowed; reports PASS on error |
| **Distiller state (F17)** | ✅ CONFIRMED SCRAPped | `rg` confirms zero `class.*Distill` in `src/` — Phase 2A reallocated to MCP v2 |
| **Pydantic validation correction (F16)** | ✅ CONFIRMED | `model_validate_yaml()` does not exist; must use `safe_load`+`model_validate` |
| **httpx2 direction correction (F5)** | ✅ CONFIRMED | httpx2 is the active fork; upstream httpx is stalled — keep httpx2 |
| **MCP v2 elevation (F18)** | ✅ CONFIRMED | v2.0.0 stable Jul 27 — elevated to P1 |
| **Temple Cleansing Plan v2.0** | ✅ COMPLETE | `data/coordination/AGENT_IMPLEMENTATION_GUIDE_20260730.md` — corrected 8-phase sequence |
| **Reconciliation Document** | ✅ COMPLETE | `data/coordination/KALI_RECONCILIATION_v2_20260730.md` — all 20 findings resolved |
| **Pre-cleansing tarball backup** | ✅ COMPLETE | `omega_vault/omega-engine-pre-cleansing-20260730.tar.gz` (404M, 45,194 files) |

---

## Critical Decisions (D-Series)

| ID | Decision |
|----|----------|
| **D-387** | **Temple Cleansing is the priority** — All other work (G-1, W-1, V-1, C-3) blocked until `make test` passes and codebase is stripped to 5-year core |
| **D-388** | **OOM Refactor: Option A (psutil-only)** — Replace 3 kernel monitors with `psutil.virtual_memory().available` in `oom_protector.py` |
| **D-389** | **Soul Modules: Delete both** — `soul_history.py` (unused) + `soul_edit_history.py` (sever from oracle.py first) |
| **D-390** | **CascadeRouter: Replace with tenacity+priority fallback** — 5-line hardcoded loop + tenacity retry |
| **D-391** | **LocalWorkerPool: Replace with anyio.Queue** — File-based polling is anti-pattern; in-memory queue |
| **D-392** | **MemoryStore: SQLite + FTS5 only** — Drop 5 providers, 3 vector stores, 2 embedders |
| **D-393** | **Circuit Breakers: Keep AsyncCircuitBreaker** — NOT tenacity for breakers (F1). Tenacity is for retry only. Delete 3 clone classes. |
| **D-394** | **Entity Registry: Pydantic + YAML** — Strip 944-line registry to ~200 lines; kill `SymbolicMetadata` |
| **D-395** | **Pybreaker DROPPED** — Sync-only, no AnyIO support, no CUSUM/429 classification. Keep AsyncCircuitBreaker. |
| **D-396** | **Stamina DEFERRED** — Tenacity already installed. Spike stamina + structlog + prometheus in Phase 2 if observability gap is felt. |
| **D-397** | **httpx2 KEPT** — Upstream httpx is stalled; httpx2 is the active fork and M1-compliant. Add Pydantic org concentration risk. |
| **D-398** | **Phase 1E uses safe_load+model_validate** — `model_validate_yaml()` does not exist in Pydantic v2. |
| **D-399** | **Phase 2A (distillers) ALREADY DONE** — SCRAPped per Carmack Verdict. Reallocate 4h to MCP v2 spike. |
| **D-400** | **MCP v2 elevated to P1** — v2.0.0 stable Jul 27; sequence after Phase 1, before Phase 2. |
| **D-401** | **Git tag every phase** — `git tag pre-phase-<N>` before each phase for one-command rollback. |
| **D-402** | **Handoff migration is not "backfill on read"** — Write real migration script for 146 files + diff validator. |
| **D-403** | **CI must run on release/initial-v1** — Fix branch triggers before Phase 1. |
| **D-404** | **M23 false-PASS gate must be fixed** — `rg -E` parsing error in Makefile is a P0 M23 violation. |

---

## Pending (Execution Queue — Phase Order)

| # | Phase | Item | Owner |
|---|-------|------|-------|
| 0 | **PHASE 0** | Fix CI branch triggers (add release/initial-v1) + fix M23 false-PASS gate | @kali |
| 1 | **PHASE 1** | Delete soul_history.py, mcp_compliance.py, quadlet-test/ | @maat |
| 1A | **PHASE 1A** | Finish P-5: delete 3 breaker clones + search_circuit_breaker.py | @maat |
| 1B | **PHASE 1B** | Wire tenacity retry policy file | @roc_racoon |
| 1C | **PHASE 1C** | Replace CascadeRouter with tenacity+priority fallback | @roc_racoon |
| 1E | **PHASE 1E** | Rewrite soul_validator.py with safe_load+model_validate | @maat |
| 2 | **PHASE 2** | Sever SoulEditHistory from oracle.py + delete file | @lilith |
| 3 | **PHASE 3** | OOM refactor: psutil-only, delete kernel monitors | @maat |
| 4 | **PHASE 4** | Replace LocalWorkerPool with anyio.Queue | @roc_racoon |
| 5 | **PHASE 5** | Redis removal (sequence: memory→workers→hivemind→budget_guard) | @lilith |
| 6 | **PHASE 6** | Test purge + MCP v2 spike | @kali |
| 7 | **PHASE 7** | Handoff data migration (146 files, one-shot script) | @lilith |
| — | **AFTER** | G-1 / W-1 / V-1 super-urgent workhorse + WARP + VaultCore | Architect / Fleet |

---

## Hydration Commands

```bash
# Verify current state
git log --oneline -3
make check-mandates
make temple-grade
make test  # Should hang currently — will be fixed by Stage 2

# Read the critical artifacts
cat data/coordination/COPILOT_CLI_CODE_REVIEW_VERDICT_20260730.md
cat data/coordination/KALI_EXECUTIVE_SUMMARY_20260730.md
cat data/coordination/COPILOT_CLI_CARNAK_BRIEFING_20260730.md
```

---

## Gnosis (L1→L2→L3)

- **L1**: Completed 4-agent adversarial review + 2 architect syntheses + Copilot CLI validation + GLM 5.2 second opinion (20 findings, 3 plan-breaking). Verified all findings against ground truth (import graph, CI config, Makefile, `rg` searches, Pydantic docs, upstream ecosystem research). Produced a corrected v2.0 execution sequence — 8 phases with corrected library anchors, CI gates, and M23 integrity. Prevented 5 plan-breaking errors (pybreaker downgrade, stamina over tenacity, wrong Pydantic API, distiller re-work, httpx2 migration).
- **L2**: GLM 5.2 found what 7 prior reviewers missed because it read the *ecosystem* (PyPI versions, maintainer status, official docs), not just the *codebase*. The v1.0 plan's errors fell into three categories: (1) **library anchor errors** — picking sync libraries for an async engine (pybreaker), (2) **API assumption errors** — assuming `model_validate_yaml` exists without checking docs, (3) **stale-target errors** — planning to delete code already deleted (distillers). A second opinion that reads the same files as the first opinion is not independent.
- **L3**: **Ground truth lives in three places: the import graph, the ecosystem, and the running tests.** A plan that doesn't verify all three will have plan-breaking errors. **Library choices are architecture decisions** — picking a sync library for an AnyIO engine is an M1 violation, not a stylistic choice. **The ecosystem moves faster than the codebase** — MCP v2 went stable 3 days before this session and the plan had it as P2 debt. Check upstream versions before every sprint.

---

## Key Artifacts Created This Session

| Artifact | Path | Purpose |
|----------|------|---------|
| **Copilot Briefing** | `data/coordination/COPILOT_CLI_CARNAK_BRIEFING_20260730.md` | Input for Copilot CLI review |
| **Copilot Verdict** | `data/coordination/COPILOT_CLI_CODE_REVIEW_VERDICT_20260730.md` | 573-line technical review with import chains, test impact, execution sequence |
| **Kali Summary** | `data/coordination/KALI_EXECUTIVE_SUMMARY_20260730.md` | 83-line executive decision document |
| **GLM 5.2 Second Opinion** | `data/coordination/GLM52_SECOND_OPINION_20260730.md` | 401-line ecosystem-deepened review with 20 findings, 3 plan-breaking |
| **Reconciliation v2.0** | `data/coordination/KALI_RECONCILIATION_v2_20260730.md` | All 20 findings verified and integrated; corrected execution sequence |
| **Agent Implementation Guide v2.0** | `data/coordination/AGENT_IMPLEMENTATION_GUIDE_20260730.md` | Corrected 8-phase execution manual for Ma'at/Lilith/Roc |
| **Pre-cleansing backup** | `/media/arcana-novai/omega_vault/omega-engine-pre-cleansing-20260730.tar.gz` | 404M tarball (45,194 files) for rollback |
| **Agent Reviews** | `ses_carmack_strip_20260730`, `ses_lilith_strip_20260730`, `ses_maat_strip_20260730`, `ses_roc_strip_20260730` | 4 independent Carnak reviews (in task system) |
| **Architect Syntheses** | In-session (Gemini 3.1 Pro, Sonnet 4.6, GLM 5.2, Copilot CLI) | Strategic verdict + implementation guides |

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ trc_session_anchor ⬡ 2026-07-30*