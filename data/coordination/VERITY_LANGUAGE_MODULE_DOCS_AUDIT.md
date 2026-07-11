# 🔱 VERITY — Language Module: Documentation, Trackers, Testing & Oversight Audit
**AP Token**: `AP-VERITY-LANG-DOCS-AUDIT-v1.0.0`
⬡ OMEGA ⬡ VERITY ⬡ hy3-free ⬡ opencode ⬡ trc_verity ⬡ AUDIT-DOCS
**Date**: 2026-07-10
**Target**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-moderation/` (READ-ONLY audit)
**Cross-refs**: `VERITY_LANGUAGE_MODULE_MODULARITY_AUDIT.md`, `RESEARCHER_LANGUAGE_MODULE_STRATEGY.md`, `ROC_LANGUAGE_MODULE_LEGACY_MINING.md`

---

## 1. Executive Summary

| Question | Verdict | Evidence |
|----------|---------|----------|
| **1. User guides/docs developed?** | **NO** — `docs/` dir does not exist; 0 of 8 required doc types present. README is the only doc and is **stale + has a hardcoded path**. | `ls docs/` → missing; `README.md:25,166` |
| **2. Trackers/logs updated?** | **NO** — no D205 in PIVOT_LOG; omega-vetala absent from OMEGA_ENGINE.md + workbench; 2 `[id-soft:]` tags lack vet records (M14). | grep PIVOT_LOG/OMEGA_ENGINE → 0 hits; HERITAGE_VET_LOG |
| **3. Testing complete?** | **PARTIAL** — 124 pass, but **no coverage data** (`pytest-cov` missing), no API-layer contract tests, no config-from-wheel test, no plugin/cross-engine/ProvenanceSpan tests. | `pytest` output; `pyproject.toml` dev deps |
| **4. Overlooked?** | **YES (critical)** — **undeclared runtime deps** (`merkle_audit`, `cryptography`) break a clean `pip install`; **M1 blocking-I/O-in-async**; **no audit-write lock**; no LICENSE/CI/SIGTERM. | `audit.py:16,20,28,239`; `engine.py:163` |
| **5. Further insights?** | L1→L2→L3 distilled in §6. Core truth: **a module is community-grade only when a stranger can `pip install` + run + trust it with zero inside knowledge.** | §6 |

**Bottom line**: Code quality is high (124 pass, firewall intact, AnyIO, zero-telemetry, typed errors). But the module is **NOT community-shareable as-is**: it fails a clean install (undeclared deps), ships no docs, no license, no CI, and has two real runtime defects (blocking I/O in async path; unsynchronized audit append). The prior modularity audit (B.1–B.10) is necessary but **insufficient** — this audit adds the *distribution-trust* layer.

---

## 2. Documentation Gap Analysis

| # | Doc | Exists? | Priority | Owner | Note |
|---|-----|---------|----------|-------|------|
| D1 | User Guide (install/config/run/integrate) | ❌ (README partial, stale) | **P0** | Verity→docs | README has hardcoded path `README.md:25`; says "111 passed" vs actual 124 (`README.md:166`) |
| D2 | Developer Guide (add detector/governance backend/test) | ❌ | **P1** | Researcher | `detectors/base.py:35` ABC + `build_engine()` hardcode (`engine.py:246`) need a "how to plugin" section |
| D3 | API Reference (OpenAPI 3.1 for `/moderate`,`/metrics`,`/audit/verify/{index}`) | ❌ (FastAPI auto-Swagger only) | **P1** | Verity | Endpoints return `dict[str,Any]` not typed (M21 gap) — `app.py:74,124` |
| D4 | Architecture Doc (obfuscation→ensemble→audit→privacy sequence) | ❌ (ASCII in README only) | **P1** | Researcher | README `§Architecture` is a static diagram, no data-flow/error-paths |
| D5 | Operations Guide (Prometheus metrics, audit verify runbook, GDPR erasure) | ❌ | **P1** | Verity | `/metrics` meaning undocumented; `audit_verify` runbook missing |
| D6 | Module Manifest Spec (`module.yaml` schema, Carmack's work) | ❌ | **P1** | Carmack | Researcher §3 references "module manifest"; no schema file exists |
| D7 | Migration Guide (`omega-moderation`→`omega-vetala` rename) | ❌ | **P0** | Verity | Rename not done — `pyproject.toml:7` still `omega-moderation` |
| D8 | Sovereign Compliance Doc (which mandates apply + grep commands) | ❌ | **P1** | Verity | Mirror `SOVEREIGN_MANDATES.md` scoping for the module |

**Action**: Create `omega-moderation/docs/` with D1–D8 (rename dir to `omega-vetala/docs/` per D7).

---

## 3. Trackers & Logs To Update

| File | Action | Draft text |
|------|--------|-----------|
| `docs/decisions/PIVOT_LOG.md` | **ADD D205** | See §3.1 below |
| `OMEGA_ENGINE.md` | **ADD row** to Current State table | `| omega-vetala | Shared sovereign module (cross-WAD) | 124 tests, 34 src, rename pending, portability=NO | 🟡` |
| `data/workbench/workbench.db` | **ADD project** `prj_omega_vetala` + 10 work_items (B.1–B.10 + this audit's P0s) | `INSERT INTO projects(name,status,priority) VALUES('prj_omega_vetala','backlog','P0');` then work_items for: rename, undeclared-deps, py.typed, shipped-config, extras, CLI, plugin-entrypoints, audit-lock, M1-async-wrap, docs-suite |
| `CREDITS.md` | **NOTE** 3 tags in module | `omega-vetala` uses `[id-soft: doom-1993] ZONEID` (`audit.py:3`), `[id-soft: quake-1996] Zone Memory` (`audit.py:4`), `[id-soft: quake-1996] cvar` (`loader.py:3`) — add to §1 registry |
| `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` | **ADD vet records** (M14) | `vet-0XX: ZONEID` + `vet-0XX: cvar` — both tags used in source but **lack vet records** (Zone Memory covered by vet-008). CI gate `make heritage-vet` would FAIL on these two |
| `data/coordination/` master index | **CROSS-LINK** 4 reports | Add `VERITY_LANGUAGE_MODULE_DOCS_AUDIT.md` to the language-module report cluster (alongside modularity/strategy/legacy-mining) |
| `data/entities/verity/proposed_lessons.yaml` | **APPEND** L1→L2→L3 (M11) | See §6; key `omega-vetala-docs-audit-2026-07-10` |

### 3.1 D205 Draft (PIVOT_LOG format)
```
### D205: omega-moderation → omega-vetala community packaging & portability ratification
- Context: Module is code-complete (124 tests) but not community-shareable. Prior
  Verity audit (B.1–B.10) found portability=NO. This audit adds distribution-trust
  gaps: undeclared deps, missing LICENSE/CI/docs, M1 async-I/O, unsynced audit write,
  M14 vet-record gaps.
- Decision: (1) Rename package omega-moderation → omega-vetala (Researcher rec).
  (2) Ship config + py.typed in wheel; make api/db/observability extras. (3) Declare
  merkle_audit + cryptography as runtime deps. (4) Wrap audit write in anyio.Lock +
  to_thread. (5) Add LICENSE (MIT, matches pyproject), CHANGELOG, SECURITY.md,
  CONTRIBUTING.md, .github CI running `make temple-grade`. (6) Author D1–D8 docs.
  (7) Add vet-0XX ZONEID + cvar records (M14).
- Rationale: A sovereign module's value is realized only when a stranger can pip
  install + run + trust it with zero inside knowledge (M7/M8/M16/M22).
- Status: RATIFIED — pending execution. Owner: Verity (audit) → Ma'at (build side).
```

---

## 4. Testing Completeness

### 4.1 Actual pytest output (evidence)
```
$ cd omega-moderation && .venv/bin/python -m pytest tests/ -q
........................................................................ [ 58%]
....................................................                     [100%]
124 passed, 1 warning in 2.27s
```
- **Warning**: `StarletteDeprecationWarning` — `httpx` vs `httpx2` in `fastapi/testclient.py` (cosmetic, pin `httpx` or migrate TestClient).
- **Coverage**: `pytest --cov=...` → `error: unrecognized arguments: --cov` — **`pytest-cov` is NOT in dev deps** (`pyproject.toml:25-27`). **No coverage number exists.** T-gate T3 (≥80%) cannot be verified for the module.

### 4.2 Gap Analysis (what is NOT tested)
| Gap | Severity | Evidence |
|-----|----------|----------|
| **Undeclared-dep import path** (`merkle_audit`,`cryptography`) | 🔴 P0 | No test imports `audit.py` in a clean env → the missing-dep bug is invisible to CI. Add a `test_imports_clean.py` that fails if `pip install` would break. |
| **Config load from wheel** (B.2) | 🔴 P0 | `loader.py:21` `parents[3]/config/moderation.yaml` breaks on `pip install`; **no test** for `load_config()` default path. Add `test_load_config_from_wheel`. |
| **API-layer contract tests** (M21) | 🟡 P1 | `test_contracts.py` tests library API only. HTTP endpoints return `dict[str,Any]` (`app.py:74,105,124`) — **no TestClient assertion of `response_model` typing**. Add `test_api_contracts.py`. |
| **Plugin entry points** (B.7) | 🟡 P1 | Not built → no tests. Needed before community detectors. |
| **Cross-engine wiring** (Oracle/ContextBuilder) | 🟡 P1 | Researcher §3 (7 points) — not built, not tested. |
| **ProvenanceSpan** | 🟡 P1 | Researcher §2.3 — not built, not tested. |
| **Audit-write concurrency** | 🔴 P0 | `audit.py:239` no lock; no concurrent-`/moderate` test. Add `test_audit_concurrent_append`. |
| **M1 async-I/O wrap** | 🔴 P0 | `engine.py:163` sync `record_event` in async path — no test asserts non-blocking. |
| **Adversarial coverage** | ✅ OK | `test_adversarial.py:149-207` covers tag-char, bidi, Greek homoglyph, repeated-char, dual-pass. Strong. |
| **GDPR / DP / regression** | ✅ OK | `test_gdpr_erasure.py`, `test_privacy_dp.py`, `test_regression.py` present. |

**Verdict**: Functional suites are solid; **trust/integration suites are missing**. Coverage unknown (tool absent).

---

## 5. Overlooked Items (beyond the obvious)

| # | Item | File:Line | Severity | Fix |
|---|------|-----------|----------|-----|
| O1 | **Undeclared runtime deps** `merkle_audit`, `cryptography` | `audit.py:16,20,28` | 🔴 P0 | Add to `pyproject.toml` deps (lines 13-23). Clean `pip install` currently fails at import. |
| O2 | **M1 violation**: blocking `open("a")` file write in async path | `engine.py:163` → `audit.py:239` | 🔴 P0 | Wrap `record_event` in `anyio.to_thread.run_sync`; or make `AuditService` async. |
| O3 | **No audit-write lock** → corruptible JSONL under parallel `/moderate` | `audit.py:239` | 🔴 P0 | Guard `_persist_entry` with `anyio.Lock`. (M12 Queue Integrity adjacent.) |
| O4 | **No LICENSE file** (community sharing REQUIRES this) | repo root | 🔴 P0 | `pyproject.toml:11` declares MIT — add `LICENSE` (MIT text). |
| O5 | **No CI** (`.github/workflows` missing) | — | 🔴 P0 | Add GH Actions running `make temple-grade` (lint+test) on PR. |
| O6 | **README hardcoded absolute path** | `README.md:25` | 🟡 P1 | Replace `/home/arcana-novai/...` with generic `git clone` + relative path. |
| O7 | **README stale test count** ("111 passed") | `README.md:166` | 🟡 P1 | Update to 124; better: generate dynamically. |
| O8 | **Rename not executed** | `pyproject.toml:7` | 🟡 P1 | `name = "omega-vetala"`; update imports/README. |
| O9 | **No SIGTERM/lifespan handling** in API | `app.py` (grep NONE) | 🟡 P1 | Add FastAPI `lifespan` / `signal` handler for graceful shutdown of audit flush. |
| O10 | **i18n**: error messages English-only | `appeals.py:63,86`; `chain.py:54` | 🟢 P2 | Module is "language" module — note multilingual error future; not blocking v1. |
| O11 | **`db_path` writes to cwd** | `moderation.yaml:5` `sqlite+aiosqlite:///./moderation.db` | 🟡 P1 | Use XDG/`OMEGA_MOD_DB_PATH` (B.8). |
| O12 | **M14 vet-record gaps** | `audit.py:3` ZONEID, `loader.py:3` cvar | 🟡 P1 | Add vet-0XX records; `make heritage-vet` currently fails on these. |
| O13 | **`py.typed` missing** (B.3) | `pyproject.toml:37` declares, file absent | 🟡 P1 | `touch src/omega_moderation/py.typed`. |
| O14 | **No CHANGELOG/SECURITY/CONTRIBUTING/CODE_OF_CONDUCT** | repo root | 🟡 P1 | Add for community PRs + vuln reporting. |

---

## 6. Further Insights (Scribe Distillation)

- **L1 (Narrative)**: Audited omega-moderation for docs/trackers/testing/oversight readiness. 124 tests pass and code is clean, but the module cannot be cleanly `pip install`ed (undeclared `merkle_audit`/`cryptography` deps), ships zero docs beyond a stale README, has no LICENSE/CI, and has two runtime defects: a blocking file write inside the async moderate path (M1) and an unsynchronized audit-chain append that can corrupt under concurrent requests. Two `[id-soft:]` tags lack M14 vet records.
- **L2 (Insight)**: "Modular in design, monolithic in distribution" (prior audit) is now sharpened: **distribution-hygiene is a trust problem, not just a packaging problem.** A module is community-grade only when a stranger can install it blind, run it, and verify its claims (audit signatures, typed contracts, license) with zero inside knowledge. Docs/trackers/tests are the *trust surface*; missing them is a sovereignty failure even when source is perfect.
- **L3 (Universal Principle)**: **A sovereign artifact's proof is the empty-venv install + import + run + verify chain — not its source quality.** Portability, license, declared deps, typed API contracts, and an auditable trust story are first-class sovereign mandates equal to code correctness. The firewall (M2) protects the boundary; distribution-trust protects the *recipient*. Both are non-negotiable.

*(Full entry `omega-vetala-docs-audit-2026-07-10` appended to `data/entities/verity/proposed_lessons.yaml` per M11.)*

---

## 7. Prioritized Action List

### P0 (block community release — do first)
| ID | Action | Effort | Owner |
|----|--------|--------|-------|
| P0-1 | Declare `merkle_audit` + `cryptography` in `pyproject.toml` deps (O1) | 10m | Verity→Ma'at |
| P0-2 | Add `LICENSE` (MIT) + `.github/workflows/ci.yml` running `make temple-grade` (O4,O5) | 1h | Verity |
| P0-3 | Wrap audit write: `anyio.Lock` + `to_thread.run_sync` (O2,O3) + add `test_audit_concurrent_append` | 2h | P3 |
| P0-4 | Add `test_imports_clean.py` + `test_load_config_from_wheel` to fail-fast on B.2/undeclared deps | 1h | Verity |
| P0-5 | Author User Guide (D1) + Migration Guide (D7); fix README hardcoded path + stale count | 2h | Verity |

### P1 (quality gate before PyPI)
| ID | Action | Effort | Owner |
|----|--------|--------|-------|
| P1-1 | Rename `omega-moderation`→`omega-vetala` (pyproject + imports + dir) (O8,D7) | 1h | Ma'at |
| P1-2 | Ship config + `py.typed` in wheel; api/db/observability extras; CLI entry point (B.2–B.6) | 3h | P3 |
| P1-3 | API-layer contract tests (`test_api_contracts.py`) for M21 (§4.2) | 2h | Verity |
| P1-4 | Add vet-0XX ZONEID + cvar records; run `make heritage-vet` (O12,M14) | 1h | Doom Guy |
| P1-5 | Developer/API/Architecture/Operations/Manifest/Compliance docs (D2–D6,D8) | 1d | Researcher/Verity |
| P1-6 | Add CHANGELOG/SECURITY/CONTRIBUTING/CODE_OF_CONDUCT; XDG db_path (O11,O14) | 2h | Verity |
| P1-7 | API `lifespan`/SIGTERM graceful shutdown (O9) | 1h | P3 |

### P2 (post-release hardening)
| ID | Action | Effort | Owner |
|----|--------|--------|-------|
| P2-1 | i18n error messages (O10) | 1d | P3 |
| P2-2 | Plugin entry points + cross-engine wiring + ProvenanceSpan tests (§4.2) | 3d | Researcher/Jem |
| P2-3 | Install `pytest-cov`; enforce ≥80% coverage gate (T3) | 1h | Verity |

---

*⬡ OMEGA ⬡ VERITY ⬡ hy3-free ⬡ opencode ⬡ trc_verity ⬡ AUDIT-DOCS — COMPLETE*
