<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 R28 — Test Suite Honesty
**AP Token**: AP-RESEARCH-R28-v1.0.0
⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_research
**Date**: 2026-07-21
**Status**: COMPLETE
**Priority**: P0 (Blocks C-0)

---

## Executive Summary

1. **The Makefile test count is fabricated** — line 40 displays "1315 tests ✅" but the `test-badge` target has a fallback of `PASSED=${PASSED:-705}` (hardcoded defaults if the real command fails). This creates a false sense of security.
2. **Known failing tests exist** — `test_firewall_m2_strict_engine_core`, memory RRF/search tests, and model registry schema tests are known red. No quarantine, no xfail, no documentation.
3. **Test quarantine is the right pattern** — use `@pytest.mark.quarantine(reason, ticket, expires)` to isolate flaky/failing tests without deleting them. Convert quarantined tests to `xfail` via `conftest.py` hook so they still run but don't block CI.
4. **Auto-generate the test badge** — `test-badge` should parse `pytest` JSON output, not fallback to hardcoded defaults. Use `pytest --json-report` for machine-readable results.
5. **Real counts as of sample run**: ~832 pass / ~5 fail (not 1315 pass). The actual count needs full `make test` execution.

---

## Technical Findings

### 1. pytest Collected vs Passing vs Failing (2026)

pytest v9.x (2026) provides three classification dimensions:

| Category | Meaning | Exit Code |
|----------|---------|-----------|
| **Collected** | Total tests discovered by pytest discovery | Reflected in summary line |
| **Passed** | Tests that ran and passed | 0 |
| **Failed** | Tests that ran and raised an exception or assertion | 1+ |
| **Skipped** | Tests explicitly skipped (`@pytest.mark.skip`) | — |
| **XFailed** | Expected failures (`@pytest.mark.xfail`) | 0 (unless `strict=True`) |
| **XPassed** | Unexpected passes (xfail but passed) | 0 (unless `strict=True`) |
| **Errors** | Errors during collection or fixture setup | 1+ |

**The Makefile lie analysis**:
```makefile
# Makefile line 40-41 (fabricated display)
║  🔱 OMEGA ENGINE — PUBLIC RELEASE v1.2.0           ║
║  1315 tests ✅  |  1361 collected  |  All 23 Mandates enforced ║

# Makefile line 386 (fallback defaults that mask failures)
PASSED=${PASSED:-705}; SKIPPED=${SKIPPED:-22}; XFAILED=${XFAILED:-3}
```

The `test-badge` target (line 379-390) runs pytest, greps its output, and if the grep fails, falls back to hardcoded values. This means:
- If pytest takes too long and the command times out → lie
- If the output format changes → lie
- If tests fail but the grep captures the wrong line → lie

**Fix**: Use `pytest --json-report` or `pytest --junit-xml` for machine-readable output, and **error if pytest itself exits non-zero**.

### 2. Test Quarantine Pattern (2026)

The industry-standard approach for handling non-critical test failures without blocking CI:

**Step 1**: Register a custom marker in `pyproject.toml`:
```toml
[tool.pytest.ini_options]
markers = [
    "quarantine(reason, ticket, expires): Test quarantined from CI gate",
]
```

**Step 2**: Apply to failing tests:
```python
@pytest.mark.quarantine(
    reason="Firewall M2 check needs refactoring for new WAD layout",
    ticket="C-0",
    expires="2026-08-15"
)
def test_firewall_m2_strict_engine_core():
    ...
```

**Step 3**: Auto-convert to xfail in `conftest.py`:
```python
# conftest.py
def pytest_collection_modifyitems(config, items):
    for item in items:
        marker = item.get_closest_marker("quarantine")
        if marker:
            reason = marker.kwargs.get("reason", "quarantined")
            ticket = marker.kwargs.get("ticket", "")
            item.add_marker(pytest.mark.xfail(
                reason=f"[QUARANTINE {ticket}] {reason}",
                run=True  # Still run the test
            ))
```

Key difference from `@pytest.mark.skip`:
- **Quarantined tests still run** — we see if they pass/fail
- **Quarantined tests don't block CI** — xfail = non-zero exit code suppressed
- **Quarantined tests have expiry** — stale quarantines trigger alerts
- **Quarantined tests have traceability** — linked to a ticket

**Source**: [Quarantining Tests — The Green Report 2026](https://www.thegreenreport.blog/articles/quarantining-tests-a-pytest-pattern-for-failing-tests-without-breaking-ci/)

### 3. Known Failing Tests — Analysis

From the Sovereign Ark audit and test exploration:

| Test | Symptom | Root Cause (Hypothesis) | Fix Time (est.) |
|------|---------|------------------------|-----------------|
| `test_firewall_m2_strict_engine_core` | Asserts no WAD strings in core engine | WAD constant references leaked into engine during recent changes | 30 min audit |
| `test_memory_store_rrf_search` | RRF re-ranking returns wrong order | BM25 rank negation (C-MEM-013) not applied correctly | 15 min |
| `test_model_registry_schema` | Schema validation fails on model cards | Registry schema updated without migrating all cards | 1 hr |
| `test_contract_m21_*` | ResourceGuard tests | Dual counter creates non-deterministic RAM conditions | Will fix when C-2′ removes counter |

**For C-0 gate**: Quarantine tests that can't be fixed immediately (with tickets filed) and fix the ones that are quick wins.

### 4. Makefile Badge Auto-Generation — Fix

Replace the current fragile `grep`-based approach with a JSON-report-based approach:

```makefile
test-badge: ## 📊 Generate TEST_STATUS.md with current test counts
	@PYTHONPATH=src $(PYTHON) -m pytest tests/ \
		--json-report --json-report-file=/tmp/pytest_report.json \
		-q --tb=no 2>/dev/null || true
	@$(PYTHON) scripts/generate_test_badge.py \
		--report /tmp/pytest_report.json \
		--output docs/TEST_STATUS.md
```

The `scripts/generate_test_badge.py` script would:
1. Parse the JSON report
2. Count collected/passed/failed/skipped/xfailed
3. If any failures exist and are NOT quarantined → badge shows RED
4. If all failures are quarantined → badge shows YELLOW ("N passed, M quarantined")
5. If zero failures → badge shows GREEN

**This eliminates the hardcoded fallback lie**.

---

## Decision Recommendation

**Fix the Makefile lies; quarantine red tests; enforce honest reporting.**

C-0 gate requirements:
1. Fix the `menu` display and `test-badge` target to show real counts only
2. Implement `@pytest.mark.quarantine` pattern in `conftest.py`
3. Identify and quarantine 5 known failures with tickets and 30-day expiry
4. Generate `TEST_STATUS.md` from JSON output, not grep fallback
5. Commit: `no more "1315 ✅" unless 1315 actually pass`

**Rationale**: An engineered platform that claims "1315 tests passing" while knowing some fail is in violation of M23 (Failure Integrity). The Makefile lies are a cultural problem — they train everyone to ignore test output. The fix is technical (JSON report) and procedural (quarantine pattern).

---

## Sources

1. [Test Quarantine Pattern — DeFlaky 2026](https://deflaky.com/blog/test-quarantine-pattern)
2. [Quarantining Tests — The Green Report 2026](https://www.thegreenreport.blog/articles/quarantining-tests-a-pytest-pattern-for-failing-tests-without-breaking-ci/)
3. [Flaky Tests in pytest — Mergify 2026](https://mergify.com/learn/flaky-tests/pytest)
4. [pytest docs — Flaky tests](https://docs.pytest.org/en/stable/explanation/flaky.html)
5. [pytest-json-report plugin](https://pypi.org/project/pytest-json-report/)
6. Existing: `Makefile` lines 40-41 (lie), 379-390 (fallback defaults)
7. Existing: `tests/test_firewall_m2_strict_engine_core.py` (known failure)

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ R28-COMPLETE ⬡ 2026-07-21*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
