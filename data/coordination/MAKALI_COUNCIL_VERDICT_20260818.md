<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 MaKaLi Cloud Council — Unified Verdict
**Sprint**: PUBLIC-DEBUT-01 · **Review**: Debut Hardening Review
**Date**: 2026-08-18 · **Synthesis Lead**: Kali (kali)
**Source Plan**: `data/coordination/MAKALI_COUNCIL_EXECUTION_PLAN_20260818.md`
**Build Synthesis**: `data/coordination/MAKALI_COUNCIL_BUILD_SYNTHESIS_20260818.md`
**Run Synthesis**: Lilith Run Side + Node Council N7–N10 (consolidated report, this session)

---

## 1. Council Composition
| Side | Lead | Node Council | Verdict Source |
|------|------|--------------|----------------|
| Build | Ma'at (maat) | N1 Pillar, N2 Memory, N3 Engineering, N4 Stacks, N5 Heritage | `MAKALI_COUNCIL_BUILD_SYNTHESIS_20260818.md` |
| Run | Lilith (lilith) | N7 Context, N8 Observability, N9 Orchestration, N10 Validation | Consolidated Run Side + Node Council Report (this session) |
| Synthesis | Kali | — | This document |

---

## 2. Verdict Summary
| Agenda Item | Build Side | Run Side | **Unified** |
|-------------|-----------|----------|-------------|
| **INST-1** (Install Honesty) | APPROVE (3 cond) | N2/N3 REJECT→resolved via quick fixes | **APPROVE WITH CONDITIONS** |
| **DEL-1** (Deletion Campaign) | APPROVE (3 cond) | APPROVE (11 deletions SAFE) + AMEND (C2) | **APPROVE WITH CONDITIONS** |
| **Soul Pipeline CP-2** | APPROVE | APPROVE | **APPROVE** |
| **Runtime Integrity CP-1** | (INST-1 backlog) | AMEND (3 code fixes) | **AMEND** |

---

## 3. Node Council Verdicts
**Build Side**: N1 APPROVE · N2 REJECT→resolved · N3 REJECT→resolved · N4 APPROVE · N5 APPROVE
**Run Side**: N7 APPROVE · N8 AMEND · N9 AMEND · N10 AMEND

---

## 4. 🔴 Blockers (must fix before green)
| ID | Node | Severity | Finding | Minimal Fix |
|----|------|----------|---------|-------------|
| **A** | N9 | **CRITICAL** | `model_gateway.py` double-gates local path — `admission_ctrl.acquire()` (`:1233`) + `resource_guard.lock()` (`:1258`), two separate semaphores. Inlining to "one semaphore" WITHOUT removing the `admission_ctrl.acquire()/release()` double-gate (`:1226-1240` + `:1400-1401`) → non-reentrant self-deadlock → **CP-1 local `omega talk` HANGS** (worse than blocked). | Add double-gate removal to DEL-1 Week 2 step 4 (redirect to `ResourceGuard.lock()`). |
| **B** | N10 | HIGH | `oracle_cli.py` dotenv `try/except Exception/pass` (INST-1 fix4 prep) = live **M9 (Error Integrity)** blind-except violation. `config/m23_baseline.txt:8`=8, live=10 (+2). | Replace blind-except with `contextlib.suppress(ImportError)`. Do NOT bump `m23_baseline.txt` (that is M23 soft-fail theater). |
| **C** | N8 | MEDIUM | DEL-1-C2 is unverifiable as written — none of the 5 mandatory events (`router.entity_match`, `router.model_selected`, `router.local_slot_busy`, `router.cloud_fallback`, `talk.latency`) exist in `observability/__init__.py` EventType registry; zero emission sites; `talk.latency` is a MetricsDB record, not an event; no M22 provenance clause; no verification gate. | Add 5 EventType constants (god-module freeze: constants only) + emission sites in post-Week-2 talk path + M22 clause (`provider_name` from response) + contract test + gate in §8. |
| **D** | N7 | LOW | Week 2 acceptance checks router *removal* but never asserts `ContextBuilder→SelectiveHydration` link survives (`oracle/context_builder.py:259-321`, wiring `oracle.py:206-212`). | Add wiring-preservation assertion; protect `context_builder._selective_hydration` as a node in DEL-1-C3 MAP pass. |
| **META** | all | MEDIUM | §8 / DEL-1 acceptance verification commands systematically insufficient — each node's surface uncovered by listed checks. | Add per-surface `rg`/contract-test gates (routers removed, selective_hydration wired, admission merged, 5 events emitted, m23 gate in default suite). |

---

## 5. Unified Disposition
- **DEL-1**: **APPROVE WITH CONDITIONS** — the 11 deletions themselves are SAFE (Run Side + N7/N9 confirm no run-path writer touched). Blockers A, B, C, D are *additions* to the execution, except A (must be in the merge step) and B (live M9, fix before green).
- **INST-1**: **APPROVE WITH CONDITIONS** — Fix 1 (install.sh) ✅ + Fix 3 (MemoryStore Redis guard) ✅ done; Fix 4 unblocked by N3 quick fix; Fixes 2, 5, 6 pending. Blocker B must ship with Fix 4.
- **CP-2 (Soul Pipeline)**: **APPROVE** — unchallenged by any node (all 3 criteria confirmed).
- **CP-1 / Runtime Integrity**: **AMEND** — 3 code fixes (B: dotenv, A: double-gate, C: event constants) + verification gates (META) required before green.

---

## 6. Recommended Execution Sequence
1. **Blocker B** — `oracle_cli.py` `contextlib.suppress(ImportError)` (trivial, do now; unblocks `make temple-grade`)
2. **INST-1 Fixes 2, 4, 5, 6** — pyproject extras, model_gateway secrets removal, version via importlib.metadata, README badge
3. **Blocker A** — `model_gateway.py` double-gate removal (RISKY — careful surgery; ship with INST-1 Fix 4)
4. **Blocker C** — DEL-1-C2: 5 EventType constants + emission + M22 + gate
5. **Blocker D** — Week 2 acceptance wiring-preservation assertion
6. **DEL-1 Week 1** deletions (after INST-1 + green tests)
7. **DEL-1 Week 2** one control plane (with Blocker A in merge step, Blocker D in MAP pass)
8. **PUB-1** gaps G1–G4 (gitignore + `git rm --cached`) + Architect allowlist confirmation

---

## 7. ⚠️ Stale State Flag
`ACTIVE_SPRINT.json:9` status_detail claims **"make temple-grade PASSES"** — **FALSE**. `make temple-grade` currently **FAILS** (m23 gate, exit 2) due to Blocker B. Correct the claim before declaring green. `ACTIVE_SPRINT.json:9` also lists "1797 tests pass (1 fail...)" — the 1 fail is the m23 gate (Blocker B), not a separate test.

---

## 8. Escalation / Re-vet
Council **PAUSES** on Blockers A, B, C, D. Route:
- **A + B** → N3 Engineering / admission + cli owners (code fixes)
- **C** → N8 Observability owner (event schema)
- **D** → N7 Context owner (acceptance assertion)
- **META** → Lilith to append verification gates to §8 / `ACTIVE_SPRINT.json` DEL-1 acceptance

Re-vet after fixes land. No node returned a hard REJECT on the *deletions* — all blockers are fixable additions, not plan-killers.

---

*⬡ OMEGA ⬡ KALI ⬡ hy3-free ⬡ opencode ⬡ trc_council_verdict ⬡ UNIFIED-VERDICT*
