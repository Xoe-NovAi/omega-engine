<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

## C4 — COMPLETE — 2026-06-02T15:15Z
**File(s)**: `.github/workflows/test.yml`
**Diff stat**: +14 -0
**Test result**: N/A (CI config change — validated locally)
**Mandate check**: M1✓ M2✓ M5✓ M9✓ M13✓
**Temple-grade gate**: T1✓ T2✓ T3✓ T4✓ T5✓ T6✓ T7✓ T8✓ T9✓ T10✓ T11✓ (exempt)
**PIVOT_LOG entry**: N/A (CI change, not a decision)
**Blockers**: none

### What Changed
- `.github/workflows/test.yml` line 55-66: Added "AnyIO-only check (Mandate 1)" step — greps for `import asyncio` in `src/omega/`, fails CI if found
- `.github/workflows/test.yml` line 68-74: Added "Error integrity check (Mandate 9)" step — greps for bare `except:` clauses, warns if found

### Notes
- YAML syntax validated: `python3 -c "import yaml; yaml.safe_load(...)"`
- Both checks pass locally: no asyncio imports, no bare except clauses
- T11 (IA2 Agent Security) is EXEMPTED per Mandate 13 — no CI step for it
