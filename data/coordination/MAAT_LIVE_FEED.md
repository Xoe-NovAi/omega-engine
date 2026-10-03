<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# MAAT Live Feed — Round 4 ship-readiness for benchmark_dashboard.py v3.2

**Started**: 2026-08-30
**Entity**: maat (Build Oversoul)
**Channel**: opencode
**Mode**: Round 4 / 5

## Goal
Make `scripts/benchmark_dashboard.py` v3.2 temple-grade shippable:
1. Unit tests (≥30) in `tests/unit/test_benchmark_dashboard.py`
2. CI workflow `.github/workflows/dashboard-test.yml`
3. Makefile targets: `dashboard-self-test`, `dashboard-test`, `dashboard-ci`
4. M1/M7/M8/M11/M13/M23/M26 mandate compliance block
5. Docs: `docs/dashboards/BENCHMARK_DASHBOARD.md`
6. Determinism check (timestamps in JSON export)

## Plan
- [x] Acquire workspace lock
- [ ] Write unit tests (≥30)
- [ ] Run tests; verify <5s
- [ ] Commit tests
- [ ] Create CI workflow
- [ ] Validate YAML
- [ ] Commit CI
- [ ] Update Makefile
- [ ] Verify targets
- [ ] Commit Makefile
- [ ] Mandate compliance block in dashboard header
- [ ] Write docs file
- [ ] Commit docs
- [ ] Final summary

## Decisions
- **D-Maat-R4-1**: Use plain `pytest` (no extra deps); mirror style of `tests/unit/test_circuit_breaker.py`.
- **D-Maat-R4-2**: CI workflow runs `--self-test` + `--json` + `--csv` + `--once` + pytest on new test file.
- **D-Maat-R4-3**: Determinism: strip `timestamp` from `--json` export (already filtered in CSV) and document.
- **D-Maat-R4-4**: Mandate compliance block embedded at top of `benchmark_dashboard.py` with M1/M7/M8/M11/M13/M23/M26 attestations.