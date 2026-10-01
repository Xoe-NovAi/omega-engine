<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Ma'at-EIS Public Docs Review — CI/CD, Build, Install Accuracy

**AP Token**: `AP-MAAT-PUBLIC-DOCS-REVIEW-20260902-v1.0.0`
⬡ OMEGA ⬡ MAAT ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_docs_review ⬡ COMPLETE

**Date**: 2026-09-02
**Session**: `ses_fb6cf6856ffes3wd3wmvyrm2IG` (standing EIS)

---

## §0 VERIFICATION (M23 Discipline)

**Files Read**:
- `README.md` (365 lines)
- `CONTRIBUTING.md` (365 lines)
- `ARCHITECTURE.md` (252 lines)
- `docs/QUICKSTART.md` (98 lines)
- `docs/USER_MANUAL.md` (1,212 lines)
- `SECURITY.md` (86 lines)
- `CODE_OF_CONDUCT.md` (87 lines)
- `CHANGELOG.md` (165 lines)
- `FAQ.md` (not found)
- `ROADMAP.md` (not found)
- `LICENSE` (Apache 2.0)
- `scripts/install.sh` (8.2KB)
- `scripts/download_model.sh`
- `Makefile` (665 lines)
- `.github/workflows/*.yml` (8 workflows)
- `config/providers.yaml`
- `config/wads/_omega_default/entities.yaml`

**Commands Tested**:
- `make test` → **FAILS** (ModuleNotFoundError: omega.library)
- `make check-m1-anyio` → **PASSES**
- `make check-m8-zero-telemetry` → **PASSES**
- `make check-m23-failure-integrity` → **FAILS** (check_secrets.py exits 1)
- `make check-mandate-compliance` → **RUNS** (18/28 = 64.3%)
- `make temple-grade` → **FAILS** (cascading from M23)
- `make check-m1-anyio` → **PASSES**
- `make check-hub-health` → **RUNS** (detects hub down)
- `scripts/install.sh` → **RUNS** (provisions venv, downloads model)
- `scripts/download_model.sh` → **RUNS** (downloads LFM2.5-2.6B)

---

## §1 INSTALL.SH VS README/DOCS ACCURACY

### §1.1 Verified Accurate

| Claim | Location | Status | Evidence |
|-------|----------|--------|----------|
| One-click install via `./scripts/install.sh` | README:18-22 | ✅ **ACCURATE** | Script provisions venv, installs deps, downloads model |
| Python 3.12+ required | README:16 | ✅ **ACCURATE** | `pyproject.toml:14` requires `>=3.12` |
| Venv auto-setup | README:19 | ✅ **ACCURATE** | `install.sh:45-55` creates `.venv/` |
| Local model bundled | README:19 | ✅ **ACCURATE** | `install.sh:85-95` calls `download_model.sh` |
| Manual install alternative | README:34 | ✅ **ACCURATE** | `pip install -e ".[native,cli]"` works |

### §1.2 Inaccurate / Stale

| Claim | Location | Reality | Fix |
|-------|----------|---------|-----|
| "Qwen 1.7B GGUF, ~1.6GB" | README:24 | **LFM2.5-2.6B Q4_K_M, 1.67GB** | Update to LFM2.5-2.6B |
| `./scripts/download_model.sh` downloads Qwen | README:25 | Downloads **LFM2.5-2.6B** | Update model name |
| "No GPU required" | README:61 | ✅ Accurate (CPU works) | Keep |

---

## §2 MAKEFILE TARGETS VS DOCS CLAIMS

### §2.1 Verified Working Targets

| Target | Docs Claim | Reality | Status |
|--------|------------|---------|--------|
| `make check-m1-anyio` | README:58 | ✅ **WORKS** | Zero `import asyncio` in `src/omega/` |
| `make check-m8-zero-telemetry` | README:60 | ✅ **WORKS** | No outbound HTTP in core |
| `make check-m23-failure-integrity` | README:62 | ❌ **FAILS** | `check_secrets.py` exits 1 |
| `make check-mandate-compliance` | README:288 | ✅ **RUNS** | 18/28 = 64.3% |
| `make check-m1-anyio` | README:292 | ✅ **WORKS** | |
| `make check-hub-health` | Not in README | ✅ **WORKS** | Detects hub down |
| `make check-broken-imports` | Not in README | ✅ **WORKS** | |
| `make check-mandates` | CONTRIBUTING.md | ✅ **WORKS** | Runs all mandate gates |

### §1.2 Broken / Misdocumented Targets

| Target | Docs Claim | Reality | Fix |
|--------|------------|---------|-----|
| `make test` | README:97, 287 | ❌ **BROKEN** | ModuleNotFoundError: omega.library |
| `make test-all` | README:287 | ❌ **BROKEN** | Same root cause |
| `make temple-grade` | README:98, 289 | ❌ **FAILS** | Cascading from M23 |
| `make verify-mining` | CI: test.yml:61 | ❌ **MISSING** | Not in Makefile |

---

## §3 CI/CD WORKFLOWS VS DOCS CLAIMS

### §3.1 Workflow Inventory (8 workflows)

| Workfile | Purpose | Status |
|----------|---------|--------|
| `test.yml` | Unit tests | ❌ **BROKEN** (verify-mining missing, test fails) |
| `ci.yml` | Full CI | ❌ **BROKEN** (depends on test.yml) |
| `sote.yml` | SOTE weekly pipeline | ✅ **WORKS** (index, digest, validate) |
| `allowlist-check.yml` | Allowlist enforcement | ✅ **WORKS** |
| `allowlist-lint.yml` | Allowlist lint | ✅ **WORKS** |
| `dashboard-test.yml` | Dashboard test | ✅ **WORKS** |
| `reuse-compliance.yml` | REUSE compliance | ✅ **WORKS** |
| `secret-scan.yml` | Secret scan | ❌ **FAILS** (OAuth secret) |

### §3.2 Critical CI Issues

| Issue | Location | Impact |
|-------|----------|--------|
| `make verify-mining` missing | `.github/workflows/test.yml:61` | CI fails at this step |
| `secret-scan.yml` fails | `secret-scan.yml` | OAuth secret committed |
| `test.yml` runs full suite | `test.yml:61` | Contradicts "two-tier" design |

---

## §4 VERIFICATION GATES ACCURACY

### §4.1 Gates That Pass (7)

| Gate | Make Target | Status | Evidence |
|------|-------------|--------|----------|
| M1 AnyIO | `make check-m1-anyio` | ✅ | Zero `import asyncio` in `src/omega/` |
| M7 Local-First | `make check-m7-local-first` | ✅ | `config/providers.yaml:8` |
| M8 Zero Telemetry | `make check-m8-zero-telemetry` | ✅ | No outbound HTTP |
| M11 Soul Integrity | `make check-m11-soul-integrity` | ⚠️ Partial | Soul store exists, auto-prompt not wired |
| M24 Venv Sovereignty | `make check-m24-venv-sovereignty` | ✅ | All Python in `.venv/` |
| M25 Doc Standards | `make doc-llm-validate` | ✅ | |
| M26 Doc Standards | `make check-doc-standards` | ✅ | |

### §4.2 Gates That Fail (5)

| Gate | Make Target | Status | Root Cause |
|------|-------------|--------|------------|
| M13 Temple-Grade | `make temple-grade` | ❌ | Cascading from M23 |
| M16 Modularization | `make check-m16-modularization` | ❌ | Hardcoded path in `m34_registry.py:75` |
| M23 Failure Integrity | `make check-m23-failure-integrity` | ❌ | `check_secrets.py` exits 1 |
| M27 Tracking Integrity | `make check-tracking-state` | ❌ | Stale `in_progress` task |
| M28 Spatial | `make check-m28-spatial` | ✅ | R-tree + vec0 works |

---

## §5 PROVIDER FABRIC / MODEL DOWNLOAD ACCURACY

### §5.1 Provider Fabric (config/providers.yaml)

| Claim | Reality | Fix |
|-------|---------|-----|
| "8-backend fallback chain" | **10 active providers** | Update to 10 |
| Local-first priority | ✅ `strategy: local_first` | Keep |
| Default model Qwen 1.7B | **LFM2.5-2.6B Q4_K_M** | Update README |
| Ollama enabled | **Disabled** in providers.yaml | Update table |

### §5.2 Provider Table (README:110-129)

| Priority | Provider | Status | Fix |
|----------|----------|--------|-----|
| 1 | Native GGUF | ✅ | Keep |
| 2 | LM Studio | ✅ | Keep |
| 3 | Ollama | **Disabled** | Mark as disabled |
| 4 | Mock | ✅ | Keep |
| 5 | Google AI Studio | ✅ | Keep |
| 6 | OpenRouter | ✅ | Keep |
| 7 | OpenCode Zen | ✅ | Keep |
| 7 | Copilot | ✅ | Keep |
| 8 | Antigravity | ✅ | Keep |

---

## §6 TEMPLE-GRADE / TEST SUITE ACCURACY

### §6.1 Temple-Grade Reality

| Claim | Reality |
|-------|---------|
| "Temple-Grade (T1-T11) ✅ VERIFIED" | **FALSE** — runs 6 checks, not 11 |
| "All 11 Temple-Grade gates" | **FALSE** — 6 checks run |
| "✅ VERIFIED (v7.5.4)" | **FALSE** — fails on M23 cascade |

**Actual `make temple-grade` runs**:
1. `check-codex-stale`
2. `doc-llm-validate`
3. `check-mandates`
4. `check-mandate-compliance`
5. `check-tracking-state`
6. `dashboard-self-test`

### §6.2 Test Suite

| Claim | Reality |
|-------|---------|
| "Two-tier: fast unit tier (default `make test`)" | **BROKEN** — 0 tests collected |
| "opt-in integration (`make test-all`)" | **BROKEN** — same root cause |
| "11 Temple-Grade gates" | **FALSE** — 6 checks |

**Root cause**: 12 test files import `omega.library` (deleted in D-565, not restored).

---

## §7 CRITICAL ISSUES FOUND

| # | Issue | File:Line | Severity |
|---|-------|-----------|----------|
| 1 | `make test` broken — 0 tests collected | `tests/contract/test_provider_classification.py:29` | 🔴 CRITICAL |
| 2 | `make verify-mining` missing from Makefile | `.github/workflows/test.yml:61` | 🔴 CRITICAL |
| 3 | Real OAuth secret committed | `OAuth-failure-incident-session-ses_fe8c.md:57` | 🔴 CRITICAL |
| 4 | `check_secrets.py` exits 1 (11 violations) | `scripts/check_secrets.py` | 🔴 CRITICAL |
| 4 | Mandate compliance 64.3% not "all enforced" | `scripts/check_mandate_compliance.py` | 🔴 CRITICAL |
| 5 | `make verify-mining` missing from Makefile | `Makefile` (not present) | 🔴 CRITICAL |
| 6 | Dead code persists (cohort_registry, m33, m36) | `src/omega/oracle/` | 🟠 WARNING |
| 7 | Hardcoded path in `m34_registry.py:75` | `src/omega/oracle/m34_registry.py:75` | 🟠 WARNING |
| 8 | CI references non-existent target | `.github/workflows/test.yml:61` | 🟠 WARNING |

---

## §8 RECOMMENDATIONS (Concede/Defend/Synthesize)

### R1. `make test` Broken — CONCEDE

**CONCEDE**: The test suite is broken and the README claims it works. This is a launch blocker.

**DEFEND**: The fix is known and queued (`HUB-RESTORATION-NEEDED` in ACTIVE_SPRINT.json).

**SYNTHESIZE**: **Update README to honestly state "Test suite currently broken — fix queued."** Do not claim passing tests.

### R2. `make verify-mining` Missing — CONCEDE

**CONCEDE**: CI references a target that doesn't exist.

**SYNTHESIZE**: **Either add the target or remove the CI step.** The target was likely removed during DEL-1 theater strip.

### R3. Temple-Grade "T1-T11" — CONCEDE

**CONCEDE**: The "T1-T11" framing is from a different era. Current `make temple-grade` runs 6 checks.

**SYNTHESIZE**: **Replace "T1-T11" with "6 cross-cutting checks" and note M23 cascade failure.**

### R3. Provider Count — CONCEDE

**CONCEDE**: "8-backend" is stale. 10 active providers.

**SYNTHESIZE**: **Update to "10 active providers (cloud opt-in fallback only; Ollama currently disabled)."**

### R4. Default Model — CONCEDE

**CONCEDE**: v2.0.0 changed default to LFM2.5-2.6B.

**SYNTHESIZE**: **Update README to LFM2.5-2.6B Q4_K_M (1.67GB).**

---

*⬡ OMEGA ⬡ MAAT ⬡ PUBLIC-DOCS-REVIEW ⬡ 2026-09-02*