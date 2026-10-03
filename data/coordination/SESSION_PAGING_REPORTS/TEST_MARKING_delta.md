<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# TEST_MARKING_delta.md — Session Paging Report (Batch 2)

**From**: researcher (paged from ses_fdef2be4effe4pAaLXCTUx62GO lineage — test-marking/gate-verification research)
**To**: kali (Architect-direct mission)
**Date**: 2026-08-21
**Scope**: Forgotten findings mapped to CI-0..CI-5 verification, C-0 test honesty (false-count ban), M21 contract mandates
**Method**: Read-only forensics (grep, pytest --collect-only, targeted runs). Original session wrote no files; this report is the sole artifact.
**Status**: IN_PROGRESS → COMPLETE (see footer)

---

## §1 Forgotten Findings — Directly Applicable to CI-0..CI-5 Verification

**F1 — Real test volume vs vanity counts (C-0 CRITICAL).**
Empirically collected: **1824 unit-tier tests** across 108 `test_*.py` files
(`pytest -o addopts="" -m "not integration" --co -q` → "1824 tests collected").
Any hardcoded count in prompts/code (sibling's "308/308 Tests Passing" find) is a
false-count violation under C-0: the real number is 6x that and changes daily.
CI verification must derive counts from pytest, never from literals.

**F2 — Inverted skipif = silent-fail theater.**
`tests/test_hub_health.py` has `pytestmark = pytest.mark.skipif(
not pytest.importorskip("httpx"), ...)`. `importorskip` returns a truthy module,
so `not module` is always False → **never skips**. Confirmed offline: 1 failed
(hub at 127.0.0.1:8016 unreachable). This is the same *silent* failure class as
the sibling's "Fourteen Laws" regex drift: a check that looks like protection
but verifies nothing.

**F3 — addopts `-m "not integration"` scope leak (false-scope reporting).**
Because pyproject `addopts` carries `-m "not integration"`, every Makefile target
WITHOUT an explicit CLI `-m` silently excludes the integration tier:
`test-all`, `test-cov`, `test-random`, `test-flake-hunt`, `test-summary`,
`test-json`, `test-pick`, `test-debug`. A gate named "all" that runs a subset
is a C-0 honesty violation at the gate level, not just the metric level.

**F4 — tldr plugin suppresses `--collect-only` (broken pick gates).**
Verified: with pytest-tldr active, `pytest --collect-only -q` emits **zero** test
IDs ("Ran 0 tests"); with `-p no:tldr`, "1824 tests collected". Therefore
`make test-pick` / `test-pick-skim` pipe empty input into fzf/sk. Any CI step
built on `--collect-only` inherits this void silently.

**F5 — temple-grade does NOT enforce T3 (testing/coverage).**
`make temple-grade` = `check-codex-stale + doc-llm-validate + check-mandates +
check-tracking-state`. Line 233 is a literal placeholder: "# Existing
temple-grade checks would go here". No `[tool.coverage.report] fail_under`
exists anywhere in pyproject.toml → coverage ≥80% (T3) is enforced **nowhere**.
"temple-grade passed" therefore conveys false confidence about test health —
same class as the mandate-regex drift the sibling found.

**F6 — Global testmon makes later runs shrink silently.**
`testmon = true` in global config means EVERY run is incremental: first run
executes all and builds `.testmondata`; subsequent runs execute only
changed-affected tests while still reporting green. Under C-0's false-count ban,
a shrinking pass-count reported as stable is a subtle vanity vector.
Also: `testmon_store = ".testmondata"` is an invalid option →
`PytestConfigWarning` on every invocation (config hygiene noise).

**F7 — Only TWO files are genuinely real-network.**
Full-suite forensics (grep for QdrantClient/redis.Redis/httpx.Client without
transport/localhost/subprocess/socket) found exactly:
- `tests/test_hub_health.py` — live hub 127.0.0.1:8016 (+1 subprocess grep)
- `tests/test_search_tools.py` — 4 network tests: firecrawl CLI, curl
  api.exa.ai, curl google.com (`test_websearch_baseline`, `test_search_summary`
  have NO skip guard), plus offline tests (cache-growth, 2 mocked)
Everything else is mocked/in-process — **including every file named
`*_integration.py`** (hivemind/metrics_db/world_state/integration_new_systems/
e2e_*): all use monkeypatched temp dirs, MagicMock, ASGITransport,
Starlette TestClient, or local sqlite.

**F8 — verify_qdrant_parity.py is invisible to pytest.**
Hits real Qdrant localhost:6333 but contains 0 `test_` functions → never
collected, never counted in any honest tally, yet mutates a live service if run
manually. Same for `verify_sovereign_search.py`, `verify_new_tech.py`.

**F9 — xdist safety is real but fixture-dependent.**
`-n auto` is safe ONLY because conftest's autouse `_set_test_env` resets
MemoryStore/USM/OMEGA_DATA_DIR per test and workers are process-isolated.
Any future test mutating an un-reset global reintroduces flake risk silently.

---

## §2 Quarantine / Marking Patterns — Adopted vs Dropped

### ADOPTED (ratified into design, keep)
- **2-tier markers only** (`unit`/`integration`) — Carmack minimalism held; do
  not add a third tier.
- Default tier = `"not integration"` filter; the `unit` marker is defined but
  intentionally unused (decorative). Acceptable.
- **Mocked-client discipline**: MagicMock/AsyncMock clients, `httpx.MockTransport`,
  `ASGITransport`, Starlette `TestClient`, local sqlite via tmp_path — this is
  what keeps 1800+ tests offline. Preserve as house style.
- xdist `-n auto` default parallelism (safe per F9 fixture contract).
- M21 isinstance-gate contract tests already present in file headers
  (e.g., test_qdrant_payload_index.py) — pattern matches new M21 mandate.

### DROPPED / CORRECTED (preliminary list was 50% wrong)
- `test_qdrant_payload_index.py` → NOT integration (client = MagicMock;
  source comment says "no network call occurs").
- `test_qdrant_index.py` → NOT integration (MockVectorAdapter).
- `test_storage_providers.py` → NOT integration (AsyncMock client;
  `test_fallback_flow` uses unroutable 10.255.255.1, benign ~1s fallback).
- `verify_qdrant_parity.py` → standalone script, not a test; relocation, not a marker.

### ANTI-PATTERNS FLAGGED FOR QUARANTINE (C-0 relevance)
- Inverted/no-op skipif conditions (F2) — protection theater.
- Hardcoded pass-counts in prompts/code (sibling's 308/308) — violates
  false-count ban; derive from pytest at runtime.
- Gate targets whose name promises broader scope than their flags deliver (F3).
- Shrinking incremental runs reported as stable green (F6).

---

## §3 Flagged Important — NEVER Executed

Original session was research-only (write ban). **None** of the consolidated
recommendations were applied. Outstanding work items, in priority order:

1. **test_hub_health.py**: replace inverted skipif with a single combined
   assignment (two `pytestmark =` lines override each other):
   ```python
   def _hub_reachable():
       try:
           with socket.create_connection(("127.0.0.1", 8016), timeout=1.0):
               return True
       except OSError:
           return False
   pytestmark = [pytest.mark.integration,
                 pytest.mark.skipif(not _hub_reachable(),
                                    reason="omega-hub not running")]
   ```
2. **test_search_tools.py**: module-level `pytestmark = pytest.mark.integration`
   (or mark only the 4 network tests to keep cache-growth/mocked tests in unit).
3. **pyproject.toml**: remove `-m "not integration"` from `addopts` (fast targets
   already carry it on CLI); delete `testmon = true` + `testmon_store`;
   add `[tool.coverage.report] fail_under = 80` (makes T3 enforceable).
4. **Makefile**: add `-p no:tldr` to test-pick/test-pick-skim collect step;
   OSC 9 fallback (`notify-send`) for notify-test; correct the false
   "<10s" help text (real: minutes for 1824 tests).
5. Do NOT mark qdrant/storage files (mocked) — prevents unit-tier bloat.
6. Optional: relocate `verify_*.py` scripts out of `tests/`.

### Also never executed
- **Full offline green-run confirmation**: the 1824-test run exceeded the shell
  120s cap mid-flight; end-to-end pass state of the offline suite is UNVERIFIED.
  CI-0 verification should complete one full `-m "not integration"` run with
  generous timeout before trusting any count.
- M21 note: existing contract tests under `tests/contract/` (e.g.,
  provider_classification) are local-sqlite, unit-safe — no marking needed.

---

**FILE COMPLETE** — 3 sections delivered (§1 findings/F1-F9, §2 adopted-vs-dropped,
§3 unexecuted items). No other files written.
*⬡ OMEGA ⬡ RESEARCHER ⬡ TEST_MARKING_delta ⬡ COMPLETE ⬡ 2026-08-21*
