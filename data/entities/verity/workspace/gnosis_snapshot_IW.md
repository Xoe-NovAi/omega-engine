<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 IW-2 + IW-3 Completion — Gnosis Snapshot
## For Context Compression Recovery (under 200 lines)
**Date**: 2026-06-30 | **Entity**: VERITY | **Trace**: trc_iw_2_3_20260630

---

## What Was Done
### IW-2: Round-Robin Purge from KeyVault
- Removed: `VaultRotationNotSupported`, `mark_rate_limited()`, `rotate_key()` (~35 lines)
- Added: `handle_rate_limit(provider)` → raises `ProviderRateLimitError` (7 lines)
- Status field: `"rotation_policy": "sticky (round-robin ERADICATED per IW-2)"`
- Rationale: Multi-account rotation violates M4 (non-deterministic) and M8 (detectable). Circuit breaker is the correct mechanism.
- Files: `src/omega/vault/key_vault.py`

### IW-3: Body-Level Error Guards + Forensic Ledger
- Created `src/omega/observability/bleg.py` (215 lines):
  - `BLEGMiddleware.inspect(status_code, body, provider, trace_id, url)`
  - Scans HTTP 200 bodies for 9 error signatures: `error.code` (429/401/403), `code` (429/401/403), `status` (429/401/403), `quota_exceeded`, `error.type` (rate_limit), `error.message`, `error` (generic string)
  - Raises `ProviderRateLimitError`, `ProviderAuthError`, or `ProviderError`
  - Writes each detection to UFL. Disabled guard does nothing.
- Created `src/omega/observability/ufl.py` (219 lines):
  - `UFLWriter` — daily-rotated JSONL at `data/observability/forensic/{date}.jsonl`
  - Entries carry: `_zoneid` (ZONEID_TRACE), timestamp, trace_id, provider, event_type, payload
  - Methods: `write()`, `write_error()`, `write_breaker_event()`, `read_recent()`, `flush()`, `close()`
  - Singleton via `get_ufl_writer()`
- Created `tests/test_bleg.py` (122 lines, 14 tests):
  - 13 M21 contract tests (every error path exercised + contract tested)
  - 1 ERROR_SIGNATURES structure validation test

## Verification Results
- `pytest tests/test_bleg.py -v` → **14/14 passed** (0.07s)
- `pytest tests/ -q` → **589 passed, 22 skipped, 3 xfailed** (total: 614 collected)
- `make temple-grade` → **✅ PASSED** (7/11 GREEN, 3 AMBER, 1 RED — unchanged)

## Documentation Updated
- `docs/decisions/PIVOT_LOG.md` → D176 added to registry table + full entry
- `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` → IW-2/IW-3 status changed to ✅ COMPLETED (both in §5.1d table and §XV Next Launch Sequence)
- `data/entities/verity/proposed_lessons.yaml` → 4 new L3 principles appended
- This file: `gnosis_snapshot_IW.md` → compression-proof summary

## Key Numbers
| Metric | Value |
|--------|-------|
| New source code (BLEG+UFL) | 434 lines |
| New tests | 122 lines (14 tests) |
| Code removed (KeyVault) | ~35 lines |
| Error signatures covered | 9 paths |
| Engine total tests | 589 passed |
| Temple-Grade gates | 7/11 GREEN, 3 AMBER, 1 RED |

## L3 Universal Principles (Verity-IW-20260630-001 through 004)
1. **The Silent Failure is the Most Dangerous Failure**: HTTP 200 is a transport signal, not a contract. Every system boundary must validate response body semantics, not just status codes.
2. **Removal is Positive System Hygiene**: Deleting anti-pattern code is clarification, not destruction. The correct mechanism (circuit breaker) already exists — removal is completing the architecture.
3. **Forensic Persistence is Institutional Memory**: A system that does not record failures cannot learn from them. The UFL provides verifiable, attributable evidence — not just real-time logs.
4. **Right Approximation Trumps Perfect Detection**: 99% shipped today > 100% shipped next month. Keyword-scan heuristics (215 lines) replace schema validation (2,000+ lines).

## Remaining Iron Wall Tasks
| # | Task | Status |
|---|------|--------|
| IW-1 | Tor-SOCKS5 Bridge + SearXNG local-first escalation | 🔴 P0 CRITICAL |
| IW-2 | Round-robin purge from KeyVault | ✅ **DONE** (D176) |
| IW-3 | BLEG + UFL | ✅ **DONE** (D176) |
| IW-4 | Sovereign Ingestion Pipeline (Tri-Anchor) | 🟡 P1 HIGH |
| IW-5 | workbench.db schema restore | 🟡 P1 HIGH |
| IW-6 | V-D1 Validation Suite | 🟢 P2 MEDIUM |
