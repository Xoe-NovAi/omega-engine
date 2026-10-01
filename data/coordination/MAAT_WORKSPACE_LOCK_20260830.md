<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# MAAT Workspace Lock — 20260830

**Holder**: maat (Build Oversoul, channel=opencode)
**Domain**: scripts/benchmark_dashboard.py ship-readiness (Round 4)
**Acquired**: 2026-08-30
**TTL**: 4 hours (auto-expires)

## Scope (locked files)
- `scripts/benchmark_dashboard.py` (read-only analysis)
- `tests/unit/test_benchmark_dashboard.py` (NEW — Round 4 deliverable)
- `.github/workflows/dashboard-test.yml` (NEW)
- `Makefile` (dashboard-* targets)
- `docs/dashboards/BENCHMARK_DASHBOARD.md` (NEW)

## Out of scope (do NOT touch)
- `scripts/benchmark_dashboard_adversarial_test.py` (R3 jem artifact, frozen)
- Public API of the dashboard (do not break)
- Any feature additions (this is hardening, not enhancement)

## Coordination notes
- R1 (carmack): 22 bug fixes → commit 8a475d80
- R2 (researcher): v3.1 SOTA features → commit 0b864abe
- R3 (jem): v3.2 adversarial hardening → commit 2577e050 (HEAD)
- R4 (maat, this): ship-readiness gate (tests + docs + Makefile + CI + compliance)
- R5 (lilith, deferred): runtime hardening + observability