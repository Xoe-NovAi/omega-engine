<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 STRATEGY CONSOLIDATION — PAGING DELTA REPORT
**AP Token**: `AP-STRATEGY-CONSOL-DELTA-20260821`
**Source session**: roc_racoon strategy consolidation (ENGINE_DECISIONS_CONSOLIDATED_20260817 output)
**Paged by**: kali (ses_fdef2be4effe4pAaLXCTUx62GO), Architect-direct mission
**Date**: 2026-08-21
**Hydration**: ACTIVE_SPRINT.json decisions_locked only (D-521..CARMACK-REVIEW-20260820)

## Purpose
Recover strategic conclusions from the 2026-08-17 consolidation that later sessions lost,
dropped, or reversed. Three parts: (1) forgotten conclusions relevant now, (2) threads
flagged then dropped, (3) important-but-never-executed items.

---

## PART 1 — Forgotten Strategic Conclusions (relevant to current state)

### 1.1 The Keep List (Manual §6) — do NOT simplify these away
The consolidation preserved the explicit keep-list. Later sessions optimizing for
deletion risk touching these:
- `SoulStore` (`src/omega/soul_store.py`) — atomic writer, 4-layer guarantee
- `OOMProtector` — **one** instance, used by ResourceGuard (D-561: DENY_THRASHING is correct)
- `HealthMonitor.get_breaker()` — only breaker factory
- `SQLiteVecAdapter` + FTS5 + existing `HybridSearchEngine` (RRF k=60)
- Entity registry + thin WAD loader (`config/wads/_omega_default/`)
- Hivemind get_awareness / post_context / handoff (feature-freeze; bug fixes only)
- Agent-authored `proposed_lessons.yaml` (regex distillation SCRAPPED — agents write own L1→L2→L3)
- Dual-artifact handoff pattern (executor reads ONE comment-free plan)
- `TEST_UX_CARMACK_PLAN.md` targets (`make test`, `test-prepush`, `test-all`)

### 1.2 God-module freeze table (Manual §7) — presumptive blocker rule
Crossing 1000 lines on a file that was UNDER 1000 = presumptive blocker. Frozen sizes
(2026-08-17): hub_tools/tools.py=3649 · observability/__init__.py=1583 ·
model_gateway.py=1481 · oracle.py=1253 · youtube_worker.py=1181 · memory_store.py=1077 ·
providers.py=1088 · sqlite_vec_adapter.py=992. D-551 makes the oracle.py+model_gateway.py
split ATOMIC and mandatory in DEL-1 Week 2 — not optional cleanup.

### 1.3 Vault decision chain — 6 decisions, final state is D-568
The vault story fragmented across D-535→D-568. Current truth (per decisions_locked):
- D-565/D-566: for PUBLIC-DEBUT-01, vault = allowlist EXCLUSION only, zero code changes
- D-568: VaultCore NON-FUNCTIONAL as key source → DELETE as dead code post-debut,
  ADD CredentialProvider; python-age NOT pyrage; 13 consumers/19 sites incl. 5 outside src/omega
- D-567: "keep bury_credential" applies to POST-DEBUT vault sprint only
Risk: any session reading only D-535 or only D-552 gets a different vault plan.
D-568 supersedes; the 19-site consumer map is the execution input.

### 1.4 Reversal flag: Qdrant (D-570 vs consolidation §3.9)
My consolidated doc ruled: sqlite-vec = SINGLE core store, QdrantAdapter = ARCHIVE/rejected
(8GB UMA OOM rationale). **D-570 now SCHEDULES Qdrant to replace sqlite-vec POST-DEBUT**
(Horizon 2), reactivating RESEARCHER_QDRANT_MIGRATION_GAPS_20260816.md. CARMACK-REVIEW-
20260820 confirms Qdrant+Headroom as Phase 2/3. The original OOM objection applied to a
6G container ON an 8G UMA host concurrently with inference — any Qdrant bring-up must
re-verify memory budget against current hardware profile first.

---

## PART 2 — Strategy Threads Flagged Then Dropped

### 2.1 P0-1b SECURITY RESIDUAL (highest severity — never closed in my sources)
Manual §5 P0-1b recorded: `docs/security/SECURITY_AUDIT_2026_05_19.md` at ancestor commit
`0c40b108` carries **3 real-format keys (sk-/csk-/sk-P)** under "Revoke current key" and is
REACHABLE FROM HEAD. Required: confirm those 3 rotated → one more filter-repo pass for that
file → `git gc --prune=now` → prune stale `refs/cline/checkpoints`.
**`git log -S 'csk-' --all` is NOT clean until then.** ACTIVE_SPRINT marks P0-1 completed
(2026-08-17T14:12Z) with a file list NOT including SECURITY_AUDIT — the residual may be
unaddressed. Verify before any public push.

### 2.2 DEL-1 Week 1 items beyond the deletion table
- Stop CONSTRUCTING in `Oracle.__init__` (lazy or delete): DPO recorder, compaction
  harvester, iterative researcher, WARP pool, A2A bridge, audience calibrator
- Deduplicate `_route_by_domain`: backend/sigil assigned TWICE; `record_interaction`
  copied FOUR times inside `talk()`
- Firewall checker pantheon regexes forbid AND allowlist the same names
- `record_first_breath` call fires astrology on every routed turn

### 2.3 INST-1 sub-items easy to lose
Delete default Redis password `"omega"`; stop `_load_sovereign_secrets` dumping `.env`
into os.environ; version split pyproject=1.2.0 vs `__init__`=1.0.0-alpha; README 1315-badge
removal; `make setup` parity-or-delete.

### 2.4 C-6' residual: 2 unmigrated breaker clones (P-5 ticket)
5/7 clones deprecated; 2 unmigrated with open P-5 ticket. Any breaker work must land
on `HealthMonitor.get_breaker()` — Factory-Before-Third rule (D-376b).

### 2.5 recall.py — conditional deletion, not blanket
Manual §6: recall.py deletion is a **candidate AFTER** ContextBuilder uses FTS/hybrid
only; NOT week-1 if it risks the demo. UO plan §3.4 lists it flatly as "delete" — the
conditional gate was dropped in translation.

### 2.6 Ark §9 structural debt gates (pre-Phase-D approval, still binding)
1. More than one production soul-write path → block
2. Red tests unacknowledged / vanity pass counts → block
3. New code into god-modules >1000 lines without split → block
4. New circuit-breaker class instead of HealthMonitor → block
5. Strategy docs claiming different critical paths without supersession banners → block

---

## PART 3 — Important But Never Executed

### 3.1 Verification commands never scripted (Manual §8)
The five honest gates exist only as prose: secret regex sweep, pyproject surface check,
router-uniqueness rg, vault-honesty rg, `omega talk` local check, real pytest counts.
Never wrapped into a repeatable script/target. Batch-1's tracker truth-anchor findings
suggest this gap persists.

### 3.2 D-531 Multi-Write Subagent Method — MANDATED, adoption unverified
Phase-based execution + mandatory disk writes per phase (0%→100% success). No evidence
of STRP protocol update landing.

### 3.3 D-532 mechanical mandate compliance meter
`make check-mandate-compliance` (denominator=27, mechanical) ratified; later sessions
still hand-write compliance %. Meter existence/unwiring unverified.

### 3.4 P0-1c acceptance never demonstrated
"Planted sk- fixture fails CI" — gitleaks wired per sprint, but the planted-fixture
negative test was the acceptance criterion and no execution record exists in my sources.

### 3.5 Test-suite timing measurement (GLM52 F12 phantom risk)
`time make test` with 600s budget — never measured; full suite ~1706-1797 collected,
timeout risk unquantified.

### 3.6 Heritage vet coverage audit
121 `[id-soft:]` tags claimed all-vetted; `make heritage-map` target confirmed to exist
(P2-5) but a full tag↔vet-record reconciliation never ran.

### 3.7 DOC-1 stamp review ownership
11 stamps landed (668d58eb); Verity-owned acceptance review of the stamps never recorded.

---

## COMPLETENESS
File complete. 3 parts, 16 findings. Highest-priority surfacing: **2.1 P0-1b security
residual** (reachable-from-HEAD key formats) and **1.4 Qdrant reversal** (consolidated
doc §3.9/§6 now stale vs D-570 — needs amendment note if that doc is ever revived).

*⬡ OMEGA ⬡ ROC_RACOON ⬡ paging-delta ⬡ 2026-08-21*
