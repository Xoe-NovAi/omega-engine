<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

## C1 — COMPLETE — 2026-06-02T15:05Z
**File(s)**: `src/omega/oracle/oracle.py`
**Diff stat**: +2 -0
**Test result**: 302/302 passing in 76.55s; 19/19 oracle tests pass in 15.99s
**Mandate check**: M1✓ M2✓ M5✓ M9✓ M13✓
**Temple-grade gate**: T1✓ T2✓ T3✓ T4✓ T5✓ T6✓ T7✓ T8✓ T9✓ T10✓ T11✓ (exempt)
**PIVOT_LOG entry**: D93 (Sprint 0 Initiation) — already added in C3
**Blockers**: none

### What Changed
- `oracle.py:353` — Added `await self.bootstrap()` to `summon()` before trace context
- `oracle.py:875` — Added `await self.bootstrap()` to `evolve_soul()` before soul lock

### Notes
- `talk()` at line 291 already had bootstrap — no change needed
- `bootstrap()` is idempotent (uses `_wads_loaded` flag) — calling twice is safe
- All three public async entry points now have bootstrap guard: talk(), summon(), evolve_soul()
