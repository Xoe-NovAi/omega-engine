# 🦝 Roc Racoon — Kali Report: Repo Readiness Audit for Public Debut

**AP Token**: `AP-ROC_RACOON-KALI-REPORT-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_readiness_audit ⬡ ACTIVE

**Date**: 2026-08-16
**Hivemind Session**: `ses_20260816_roc_racoon_readiness_audit`
**Purpose**: Full-session accomplishments + deep repo readiness audit + remediation plan for public debut.

---

## §1 Session Accomplishments (What We Did)

### 1.1 C-6' Circuit-Breaker Migration — COMPLETE ✅
Migrated `src/omega/ingestion/pipeline.py` off the custom `pybreaker` API to the canonical `AsyncCircuitBreaker` (per finalized C-6' plan, D-376b):
- **Removed** `import pybreaker` (line 12) — was an **undeclared dependency** (Temple-Grade T1/T5/M24 violation)
- **Removed** deprecated `record_failure(SchemaError("Extraction empty"))` (was line 271) — validation gate kept as business check
- **Removed** deprecated `record_success()` (was line 297) — redundant since `call()` records success internally
- **Removed** `SchemaError` from `.ingestion_types` import (became unused, F401)
- **Added** `AsyncCircuitBreaker.can_proceed()` in `src/omega/oracle/health_monitor.py` (~line 468) — legitimate non-raising admission check (resilience4j `isCallPermitted()` / pybreaker `can_execute()` pattern), used by `pre_flight_check()` and `run_batch()`
- **Verified**: `tests/test_sovereign_ingestion.py` (incl. `test_omnidroid_promotion`) + `tests/test_health_monitor.py` = **26 tests OK**; `test_providers.py::test_generate_missing_candidates` OK

### 1.2 Prior Session Fixes (carried forward, verified)
- Observability `log_event_sync` NoEventLoopError fallback
- Context packer `profile.exclude` via GitIgnoreSpec (10 contract tests pass)
- `test_model_updater.py` 13/13; `TierExecutionRecord.start_time: Optional[float] = None`
- sqlite_vec_adapter NULL-distance skip + `omega_vec_static_64` table name
- `providers.py` canonical `ProviderAuthError` (shadow removed) + `_resolve_google_api_key` env fallback
- ResourceGuard xdist xfail; VaultCoreRateLimit; fts_memory awaits; conftest autouse resets; F821 remediation

---

## §2 Deep Discovery — Repo Readiness Audit (THE LARGER ISSUE)

### 2.1 🔴 P0-CRITICAL: Real API Keys Tracked in Git History
| File | Keys Found | Status |
|------|-----------|--------|
| `docs/archive/stale/migrate_keys_full.py` | **8 real `sk-...` keys** (OpenAI-style) | 🔴 TRACKED IN GIT |
| `docs/guides/PROVIDER_FREE_TIER_GUIDE.md` | **4+ real keys** (`csk-...` Cerebras, `sk-...` SiliconFlow) | 🔴 TRACKED IN GIT |
| `tests/test_failure_registry.py` | `sk-1234567890...` | ✅ Test fixtures (safe) |

**Impact**: Any public push exposes live credentials. Keys must be **rotated** (they're compromised) AND scrubbed from history (`git filter-repo`). This is a **hard blocker** for public debut.

### 2.2 🔴 P0-CRITICAL: 63 Test Failures (47 errors + 13 failures + 60 skipped)
Full serial suite: **1825 tests, 63 failing**. CI runs `pytest tests/ -x` → **CI is RED**. Root-cause taxonomy:

| # | Root Cause | Count | Affected Files | Fix Pattern |
|---|-----------|-------|---------------|-------------|
| 1 | **Async/sync mismatch** — tests call `async` methods without `await` (`coroutine not subscriptable`, `no len()`, `not JSON serializable`, `detect_regression` coroutine asserts) | ~20 | `test_metrics_db.py` (12), `test_contract_m21.py` (3), `test_fts_memory.py` (1), `test_search_tools.py` (2), `test_hub_health.py` (1) | Add `await` in tests (M1 AnyIO migration debt — implementations correctly async) |
| 2 | **VaultCore API drift** — implementation refactored, tests not updated: `store_credential`→`bury_credential`, `verify_integrity`/`_loaded` removed, `encrypted_blob` now requires **age-armored ciphertext** (pydantic ValidationError ×12), `initialize_fleet_vault`/`ProviderName` moved | ~18 | `test_vault_core.py` (18), `test_contract_m21.py` (2) | Align tests to new API; encrypt blobs via age; update imports |
| 3 | **ImportError** — `cannot import name 'tools' from 'mcp_servers.omega_hub'` (module restructured) | 9 | `test_library_fts_search.py` | Fix import path to restructured module |
| 4 | **Mock signature mismatch** — `MockVectorAdapter.query() got unexpected keyword 'collection'` | 1 | `test_qdrant_index.py` | Align mock signature with `indexer.py:226` call |
| 5 | **Individual logic failures** — `assert 0 == 1`, `assert 13 == 14`, `assert 0 == 2`, dispatch template missing `[id-soft:` heritage tag, `int()` on empty string | ~5 | scattered | Per-test diagnosis |

**Systemic insight**: The implementation has evolved (async migration per M1, vault refactor, mcp restructure) but **tests lag behind** — classic test-debt. This is the single largest quality signal for debut.

### 2.3 🟠 HIGH: 11,400 flake8 Violations in `src/omega/`
| Violation | Count | Notes |
|-----------|-------|-------|
| E501 line too long | 4,859 | >79 chars |
| W293 blank line whitespace | 4,444 | |
| F401 unused imports | 929 | |
| E302 expected 2 blank lines | 308 | |
| W291 trailing whitespace | 319 | |
| E402 module import not at top | 66 | |
| F811 redefinition of unused | 67 | |
| + 8 more types | ~400 | |

**CI blind spot**: `ci.yml` flake8 uses `--select=E9,F63,F7,F82` + `--exit-zero` → **lint debt invisible to CI**. Public debut with 11K violations is a maintenance + credibility problem.

### 2.4 🟠 HIGH: CI Pipeline Status
- `test.yml`: `pytest tests/ -v --tb=short -x` → **fails on first of 63 failures** → RED
- `ci.yml`: `pytest tests/ -v` → RED; flake8 critical-only + exit-zero → lint passes silently
- `make test`: `pytest -x --tb=short -m "not integration" tests/` → RED on first failure
- `make temple-grade` = `check-codex-stale doc-llm-validate check-mandates check-tracking-state` → **doc-llm-validate PASSES** ✅ (verified this session)
- `make heritage-map` → **target does not exist** (minor: AGENTS.md references it)

### 2.5 🟡 MEDIUM: Repo Hygiene
- **81 uncommitted files** (modified + untracked) — dirty working tree; includes `config/model_registry/index.sqlite` (binary), test artifacts, session files
- `.git` = 108M / 90MiB pack — large but manageable
- `scripts/rotate_test_log.py` deleted (uncommitted)

### 2.6 🟢 GOOD — Already in Place (do not regress)
- `.env` / `.env.*` **NOT tracked** — `.gitignore` covers them (verified: `git ls-files | grep .env` → only `.env.example` files)
- `README.md` + `LICENSE` exist
- CI workflows exist (`ci.yml`, `test.yml`)
- Heritage registry (`CREDITS.md`) + vet pipeline documented
- Sovereign Mandates (M1–M27) documented + `m23_baseline.txt`
- `doc-llm-validate` passes
- Hivemind coordination live (awareness: roc_racoon + SOPHIA/github-bridge active)

---

## §3 Remediation Plan — Path to Public Debut

### Phase 0 — Security (BLOCKER, do first, ~2h)
- [ ] **P0-1a**: Rotate all exposed keys (OpenAI-style in migrate_keys_full.py; Cerebras/SiliconFlow in PROVIDER_FREE_TIER_GUIDE.md)
- [ ] **P0-1b**: `git filter-repo` scrub both files from ALL history (or `git filter-branch` fallback)
- [ ] **P0-1c**: Add **gitleaks** (or trufflehog) secret scan to CI pre-commit + workflow
- [ ] **P0-1d**: Verify no other secrets: `git grep` for `sk-`, `csk-`, `AIza`, `ghp_`, `xai-` patterns

### Phase 1 — Test Suite Green (P0-2, ~1-2 days)
- [ ] **P1-1**: Fix async/sync cluster (~20 tests): add `await` to `MetricsDB` calls (get_stats, record_event, record_error, set_baseline, get_breaker_history, get_error_summary, get_performance_trend, detect_regression, get_baseline), `BudgetGate.check_budget`, fts_memory, search_tools, hub_health
- [ ] **P1-2**: Fix VaultCore cluster (~18 tests): align to `bury_credential` API, age-armor `encrypted_blob` in fixtures, update `initialize_fleet_vault`/`ProviderName` imports, restore/rename `verify_integrity`/`_loaded` or update tests
- [ ] **P1-3**: Fix `mcp_servers.omega_hub.tools` import (9 tests): update to restructured module path
- [ ] **P1-4**: Fix qdrant mock signature (1 test)
- [ ] **P1-5**: Fix individual logic failures (~5 tests)
- [ ] **P1-6**: Verify `make test` + full serial suite GREEN; remove `-x` from CI test.yml (or keep for speed after green)

### Phase 2 — Lint Debt (P1-3, ~1-2 days)
- [ ] **P2-1**: Auto-fix mechanical violations: W293 (blank whitespace), W291 (trailing), E302/E303/E305 (blank lines) — `autopep8` or `ruff --fix`
- [ ] **P2-2**: F401 unused imports (929) — `ruff check --select F401 --fix` + manual review of 929
- [ ] **P2-3**: E501 line-too-long (4,859) — `ruff format` or targeted refactor; consider raising max-line-length to 100/120 with documented decision
- [ ] **P2-4**: Tighten CI lint gate: remove `--exit-zero`, gate on `E9,F63,F7,F82` + F401 at minimum
- [ ] **P2-5**: Add `make heritage-map` target (referenced in AGENTS.md but missing)

### Phase 3 — CI & Hygiene (P1-4/P2-5, ~half day)
- [ ] **P3-1**: Update `test.yml`/`ci.yml`: full suite without `-x`, real pass/fail counts, no vanity gates
- [ ] **P3-2**: Commit hygiene: review 81 uncommitted files; commit session artifacts to `data/` (or gitignore test artifacts); remove `config/model_registry/index.sqlite` binary from tracking if not needed
- [ ] **P3-3**: Verify `make temple-grade` green end-to-end (add lint + test gates if appropriate)
- [ ] **P3-4**: Final secret re-scan + `git log` review before first public push

### Phase 4 — Debut Polish (optional, ~1 day)
- [ ] **P4-1**: README refresh (install, quickstart, architecture diagram)
- [ ] **P4-2**: CONTRIBUTING.md + issue/PR templates
- [ ] **P4-3**: Release tag `v0.1.0` + CHANGELOG
- [ ] **P4-4**: Verify `pip install -e .` from clean checkout works (CI does this — confirm)

---

## §4 Recommendations for Kali

1. **Ratify the remediation plan** (or amend priorities) — Phase 0 security is the hard blocker; nothing else matters until keys are scrubbed + rotated.
2. **Assign owners**: Roc (test clusters P1-1..P1-5 — already has full context), Ma'at/N3 (lint P2), Verity (CI gate verification P3), Kali (Phase 0 security coordination with Architect for key rotation).
3. **Decision needed**: max-line-length policy for E501 (79 vs 100/120) — affects 4,859 violations; recommend 100 with `ruff format` as canonical formatter.
4. **Decision needed**: VaultCore API — confirm `bury_credential` rename is intentional (tests were never updated); if so, tests align to it; if not, restore `store_credential` alias.
5. **CI philosophy**: recommend CI gate on `make test` (full suite, no `-x`) + `make lint` (strict) + `make temple-grade` — single command = single truth.

---

## §5 Evidence

- Full suite output: `/tmp/full_suite_output.txt` (1825 tests, 63 failing)
- Error taxonomy: 18 TypeError / 13 AssertionError / 12 pydantic ValidationError / 11 ImportError / 5 AttributeError / 1 ValueError
- flake8 statistics: 11,400 total violations in `src/omega/`
- Secret scan: `git grep` matches in `docs/archive/stale/migrate_keys_full.py` (8 keys) + `docs/guides/PROVIDER_FREE_TIER_GUIDE.md` (4+ keys)
- CI workflows: `.github/workflows/ci.yml`, `.github/workflows/test.yml`
- Hivemind post: `ses_20260816_roc_racoon_readiness_audit`

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_readiness_audit ⬡ ACTIVE*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
