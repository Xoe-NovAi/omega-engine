<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔍 MaKaLi Council Audit — Accuracy, Depth & Big-Picture Fit
**Date**: 2026-08-19
**Auditor**: Kali (kali) · **Synthesizer**: Nemotron 3 Ultra
**Source**: Council verdict `MAKALI_COUNCIL_VERDICT_20260818.md` + codebase verification

---

## Executive Summary
The MaKaLi Cloud Council verdict is **directionally correct** but has **one critical blind spot** (Blocker D under-scoping) and **two sequencing tensions** resolved by Nemotron synthesis. Pre-debut scope is now locked.

---

## Fix-by-Fix Verification

### ✅ Verified Accurate (no changes needed)

| Fix | Evidence | Status |
|-----|----------|--------|
| **Blocker B** (dotenv M9) | Ran `scripts/m23_gate.py`: `oracle_cli.py: 8 → 10 (+2)` — **exact match**. Root cause: `oracle_cli.py:21-26` `try/except Exception/pass` → S110+BLE001. Gate is a ratchet; `make temple-grade` fails until fixed. | ✅ Accurate |
| **INST-1 Fix 4** (secrets) | `model_gateway.py:127` calls `_load_sovereign_secrets()` in `__init__`; `:316-341` dumps `.env`→`os.environ` (`:335`). N3 CLI-edge `load_dotenv()` covers CLI. | ✅ Accurate |
| **INST-1 Fix 5** (version) | `__init__.py:5` = `"1.0.0"` vs `pyproject.toml:7` = `"1.2.0"`. README badge = 1.2.0. | ✅ Accurate |
| **INST-1 Fix 6** (README) | `README.md:11` 1315 badge + `:65` "1315-test suite" + `:10` version badge. | ✅ Accurate |
| **Blocker C** (events) | `observability/__init__.py:160-187` EventType has **zero** `router.*`/`talk.latency` constants. | ✅ Accurate |

### ⚠️ Accurate but Under-Scoped (depth added)

**Blocker A (N9) — deadlock is real but only in the *future merge*.**  
Current code (`model_gateway.py:1230-1240` admission pre-check + `:1258` resource_guard lock, released `:1398-1401`) has **no deadlock** — sequential acquire, no nesting. Risk is in DEL-1 Week 2 merge.  
**Depth gap**: For LOCAL providers, `resource_guard.lock()` has `lock_timeout=None` (blocks forever). The admission pre-check provides C-10's "fail-fast to cloud on local contention." Naive merge → second concurrent local request **blocks instead of fail-fasts** → inverts M7. Fix must preserve fail-fast (thin pre-check OR short local lock timeout) + update `tests/contract/test_admission_control.py` (5 M21 tests) + `tests/conftest.py:158-159,195-196`.

**INST-1 Fix 2 (pyproject) — import-guard blast radius is bigger than stated.**  
Verified 4 files with **unguarded module-level imports** that break when deps move to extras:
- 🔴 **`memory/providers.py:22`** (`import redis.asyncio`) — **CRITICAL**: imported by 5 core files (`ics.py`, `ingestion/persistence.py`, `privacy/kernel.py`, `session_lifecycle.py`, `batch_writer.py`); `ics.py` is in CLI chain (`oracle_cli.py:45`). Breaks `omega talk` without redis.
- `youtube_worker.py:47`, `ingestion/worker.py:7` (redis), `proxy_pool.py:13` (warp_proxy_pool)
- Already safe: `vector_adapters.py:16-25` (lazy qdrant), `budget_guard.py:23-29` (guarded redis)
- Also: `.github/workflows/test.yml:43,77` uses `.[cli,dev]` — CI breaks unless guards land with Fix 2.

### 🔴 What Was Overlooked (the big one)

**Blocker D (N7) is under-scoped — the router collapse is FAR riskier than assessed.**  
N7 only checked ContextBuilder (correct: it depends on `SelectiveHydration`, wired `oracle.py:206-211`, not routers). But the routers **are** the resolution paths:
- `oracle.py:1133`: `await self.semantic_router.route(...)` — **SemanticRouter IS entity resolution** (`_route_by_domain`)
- `oracle.py:764`: `await self.triage_router.select_model(req)` — **TriageRouter IS model selection** (`_select_model`), called at `:1000, :1163`
- `ics.py:200,231` (TriageRouter last_selected_model cache), `health_monitor.py:631` (TriageRouter interface)

Deleting them = rewriting `_route_by_domain` (keyword-only via `registry.find_by_domain` + default) **and** `_select_model` (ProviderSelector/entity affinity) — not a "wiring-preservation assertion." This is the single biggest gap in the council verdict.

---

## DEL-1 Week 1 — 3 Scope Corrections

1. **`record_first_breath` is called at `oracle.py:1211`** — deletion must include the call site (council didn't flag).
2. **"omega vault default CLI" conflicts with D-565** (zero vault changes during PUBLIC-DEBUT-01; vault deletion is post-debut). The `fleet_status` removal (N4) is done; the full vault CLI deletion should be **excluded** from Week 1.
3. **"Pantheon regexes"** — couldn't locate a concrete regex file; `entity_registry.py:163` is a comment. Target needs locating before deletion.

---

## Big-Picture Fit & Sequencing Decision

The fixes **do** fit the manual §5 sequence (`P0-1 → PUB-1 → INST-1 → DEL-1 → DOC-1 → P2 → P3/P4`), but there's a **sequencing tension**: `PLAN-DEBUT-CLEANSING` puts DEL-1 in **Phase B (post-debut)**, while the manual §5 lists it pre-debut.

**Nemotron Resolution**: The cleansing plan (D-532 ratified) is the operative sequence. DEL-1 Week 2 is post-debut.

### Corrected Pre-Debut Sequence

| Step | Action | Rationale |
|------|--------|-----------|
| **1** | **Blocker B** — `oracle_cli.py` `contextlib.suppress(ImportError)` | Unblocks `make temple-grade` (currently FAILS). 5-min fix. |
| **2** | **INST-1 Fix 2** — pyproject extras + **4 import guards** (`memory/providers.py`, `youtube_worker.py`, `ingestion/worker.py`, `proxy_pool.py`) | Install honesty. `memory/providers.py` is the blast radius — must land with Fix 2. |
| **3** | **INST-1 Fix 4** — remove `_load_sovereign_secrets()` from `model_gateway.py` | Removes `.env` dump; N3 CLI-edge `load_dotenv()` covers CLI. Document required env vars. |
| **4** | **INST-1 Fix 5** — `__init__.py` `importlib.metadata.version("omega")` with fallback | Single version source. |
| **5** | **INST-1 Fix 6** — README: remove 1315 badge, fix line 65 text, verify `make setup` target | Cosmetic but required for honest install. |
| **6** | **PUB-1 G1-G4** — gitignore + `git rm --cached` (tests/tmp/, .firecrawl/, config/github_accounts.yaml, birth_records.md) | Allowlist prep. |
| **7** | **Architect allowlist confirmation** + `release/debut` branch | Human gate — not automatable. |
| **8** | **DEL-1 Week 1** (minus vault CLI per D-565, minus record_first_breath call site at oracle.py:1211) | Dead code only. Low risk. |

**Post-debut (Phase B)**: DEL-1 Week 2 router collapse (with contract tests first), vault deletion, P2/P3/P4.

---

## Why This Sequence

1. **Blocker B is the gate** — `make temple-grade` fails NOW. Fix it first, everything else unblocks.
2. **INST-1 Fix 2 + guards are coupled** — moving deps to extras without guards breaks the CLI import chain. They are one atomic change.
3. **Fix 4 depends on N3 quick fix** (already done) — safe to execute.
4. **PUB-1 requires Architect** — don't execute G1-G4 until allowlist confirmed, but prep the gitignore now.
5. **DEL-1 Week 1 is safe** — dead code only, but exclude vault CLI (D-565) and include oracle.py:1211 call site.
6. **Week 2 is a Phase B project** — needs contract tests, careful rewrite of `_route_by_domain` + `_select_model`, update `ics.py`/`health_monitor.py`. Not a debut blocker.

---

## One-Line Verdict

> **Ship the install honesty fixes (Blocker B + INST-1 2/4/5/6), get the allowlist confirmed, tag v0.1.0. Everything else is post-debut cleanup.**

---

*⬡ OMEGA ⬡ KALI ⬡ hy3-free ⬡ opencode ⬡ trc_council_audit ⬡ AUDIT-RECORD*