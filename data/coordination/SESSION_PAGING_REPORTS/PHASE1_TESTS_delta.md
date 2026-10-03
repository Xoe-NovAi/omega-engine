<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# PHASE1_TESTS_delta — Roc Racoon Paging Report
**From**: roc_racoon (ses_ff325ba36ffeaVrPdakPq31mqn lineage)
**To**: kali (ses_fdef2be4effe4pAaLXCTUx62GO)
**Date**: 2026-08-21
**Scope**: Phase 1 Test Suite Green (P1-1..P1-5) — forgotten findings, CI insights, unexecuted items

---
## 1. Forgotten Findings — What Broke, Why, Never Root-Caused

### P1-1 async/sync (~20 tests) — FIXED, but root cause never documented
- **Pattern**: Tests called async methods without `await` → coroutine returned instead of result.
- **Hidden bug found**: `test_search_tools.py` JSON serialization failure was NOT a missing await.
  Root cause: `AsyncMock` gateway leaked coroutines into trace records via
  `model_gateway.health_monitor.is_available()` — mock returned coroutine, stored in
  `TierExecutionRecord.provider_health`, then `json.dumps(log_data)` in
  `search_observability.complete_trace` blew up with "Object of type coroutine is not
  JSON serializable". Fix: `MagicMock` for sync `is_available`. **Insight: AsyncMock
  auto-children poison any dict they touch — audit ALL attribute access on mocked gateways.**

### P1-2 VaultCore API drift (~18 tests) — FIXED to 20/20, with source-code changes
- D-532 honored: tests aligned to `bury_credential`/`create_credential`; no alias restored.
- **Source bugs fixed during test alignment** (tests were the canary):
  - `_save_data`/`_atomic_write` used `anyio.run()` inside running loop → RuntimeError.
    Made async; all 12 call sites awaited.
  - Credentials stored under `key_id` but looked up under `provider:key_id` — key mismatch
    across create/get/update/lease-release paths. Unified on `credential_ref`.
  - Duplicate check tested `key_id in self.credentials` (wrong key format) → duplicates
    silently accepted. Fixed to check full ref.
  - `increment_usage` never set status=EXHAUSTED; `reset_daily_quota` never reset it back.
  - Audit file written as JSON array, loaded as JSONL → round-trip crash. Now writes JSONL,
    loader accepts both formats.
  - `VaultAuditEntry.action` Literal rejected `credential_retrieved`/`credential_updated`
    that the code itself emitted.
- **THE BIG ONE**: `credential_ref` was a plain `@property` → absent from `model_dump()`.
  Persistence round-trip broke (save keyed by ref, load crashed reconstructing). Fixed with
  Pydantic v2 `@computed_field(return_type=str) @property`. **This is the L3 lesson:
  computed properties serving as identity keys must be serialized or reconstructed at load.**
### Never root-caused / left dangling
- **P1-3 incomplete**: Updated 7 of 9 `from mcp_servers.omega_hub import tools` imports in
  `test_library_fts_search.py` to `hub_tools.tools`. Lines ~236 and ~246 (signature tests)
  still had old import when session hit step limit. **Tests NEVER re-run after edits —
  unverified.** Also `test_hub_health.py` had same path drift (`tools.py` →
  `hub_tools/tools.py`) — fixed via grep path, verified passing.
- **P1-4 never started**: `MockVectorAdapter.query()` in `tests/test_qdrant_index.py:45`
  needs `collection` kwarg — indexer at `src/omega/library/indexer.py:226` passes it.
  One-line fix, never executed.
- **P1-5 partially diagnosed, not fixed**:
  - `test_contract_m21.py::test_talk_*` failures = missing `sqlite_vec` dependency,
    NOT logic bugs. Integration tests need the dep or a skip marker.
  - Failure-analysis doc claims "dispatch template missing [id-soft: tag" test exists in
    test_contract_m21.py — IT DOES NOT. Doc reference is stale; don't chase it.
  - int()-on-empty-string was the hub_health grep path issue (already fixed).
- **Full-suite green NEVER achieved or verified.** Verified green only per-file:
  vault 20/20, metrics_db 32/32, fts/search_tools/hub_health targeted runs.
  Acceptance criterion #2 (full serial pytest = 0 failures) remains OPEN.

### Production fragility left in place (test fixed, prod not)
- `search_observability.complete_trace` does bare `json.dumps(log_data)` with no
  `default=str` guard. Any non-serializable value in trace records crashes the pipeline
  AFTER results are computed. Recommend `json.dumps(..., default=str)` + typed
  provider_health field.
## 2. Test Infrastructure Insights for CI-0..CI-5 Verification

1. **Always run with `-o addopts=""`** — pyproject injects `-x -n auto`; without the
   override you get early-exit + parallel flakiness that masks real counts.
2. **Truth-anchor discipline (re: sibling's finding)**: paste actual pytest summary lines
   into reports. I claimed "~20 tests" early on before exact verification; later claims
   used real output ("20 passed, 172 warnings"). Counts from memory drift.
3. **AsyncMock auto-children are a silent poison** — any `mock.attr.method()` returns a
   coroutine unless explicitly MagicMock'd. In CI verification, grep new tests for
   AsyncMock objects whose nested attrs feed non-await paths.
4. **Pydantic v2 gotchas that cost me hours**: computed properties excluded from
   model_dump() by default (use @computed_field); Literal enums reject values the code
   itself emits; validator on encrypted_blob blocks naive test fixtures (mock age-armored
   prefix works: "age-encryption.org/v1->...").
5. **anyio.run() inside a running loop = RuntimeError** — audit for sync persistence
   helpers calling anyio.run; convert to async + await all call sites (12 in vault_core).
6. **Format migrations need dual-format loaders**: JSON array → JSONL switch broke
   round-trip until loader accepted both. Any CI gate touching persisted state should
   test save→load→save equality.

## 3. Flagged Important, Never Executed
- Full serial suite verification (`pytest tests/ -o addopts=""` → 0 failures) — OPEN.
- P1-3 lines ~236/~246 import fix + re-run of test_library_fts_search.py — OPEN.
- P1-4 Qdrant mock one-liner — OPEN.
- sqlite_vec dependency for contract_m21 talk tests (install or skipif) — OPEN.
- Prod hardening: default=str in complete_trace json.dumps — OPEN, recommend P2 ticket.
- Vault audit.json other-consumer audit (did my JSONL switch break anything else?) —
  never grepped. One `grep -rn "audit.json" src/ scripts/` would close it.
