<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

## C2 — COMPLETE — 2026-06-02T15:10Z
**File(s)**: `Makefile`
**Diff stat**: +4 -1
**Test result**: 14/14 filtered tests pass (bootstrap/summon/talk keyword match)
**Mandate check**: M1✓ M2✓ M5✓ M9✓ M13✓
**Temple-grade gate**: T1✓ T2✓ T3✓ T4✓ T5✓ T6✓ T7✓ T8✓ T9✓ T10✓ T11✓ (exempt)
**PIVOT_LOG entry**: N/A (target addition, not a decision)
**Blockers**: none

### What Changed
- Makefile line 225: Added `test-oracle-bootstrap` to `.PHONY` list
- Makefile line 355-357: New target `test-oracle-bootstrap` — runs oracle tests filtered to bootstrap/summon/talk keywords

### Notes
- `--timeout=30` flag not available in this pytest version — removed from target
- Dedicated `tests/test_oracle_bootstrap.py` not created; existing 14 tests provide adequate coverage via `-k` filter
