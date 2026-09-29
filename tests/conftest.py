# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

import os
import logging
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import tempfile
import yaml


def pytest_xdist_auto_num_workers(config):
    """Memory-aware -n auto (2026-08-24 OOM root-cause fix, v2 — MEASURED).

    Field data from the second OOM: full-suite COLLECTION alone (zero tests
    executed) holds ~683MB RSS per process — every xdist worker pays that
    toll because collection imports every test module. v1 assumed 350MB and
    still OOM'd the box. Numbers below are measured, not guessed.
    """
    per_worker_mb = 750   # measured: 683MB collection floor + execution margin
    reserve_mb = 4000     # opencode agent session(s) + desktop + qdrant + headroom
    try:
        info = {}
        with open("/proc/meminfo") as fh:
            for line in fh:
                if ":" in line:
                    key, val = line.split(":", 1)
                    info[key.strip()] = int(val.split()[0])
        avail_mb = info.get("MemAvailable", 4_000_000) // 1024
    except OSError:
        return 4  # non-Linux fallback: conservative default
    by_mem = max(1, (avail_mb - reserve_mb) // per_worker_mb)
    return max(1, min(os.cpu_count() or 4, by_mem))


# ── Per-worker peak-RSS visibility [Architect demand: 2026-08-24] ─────────
# Each process (controller + workers) records its kernel-maintained high-water
# mark (VmHWM — monotonic, zero sampling cost); workers ship it back via
# workeroutput; the controller prints a per-worker table at session end.
# Every test run now ANSWERS "how much memory did we actually use?"

def _vmhwm_mb():
    try:
        with open("/proc/self/status") as fh:
            for line in fh:
                if line.startswith("VmHWM:"):
                    return int(line.split()[1]) // 1024
    except OSError:
        pass
    return -1


_PEAK_ATTR = "_omega_peak_rss_mb"


def pytest_configure(config):
    setattr(config, _PEAK_ATTR, _vmhwm_mb())


def pytest_sessionfinish(session, exitstatus):
    peak = getattr(session.config, _PEAK_ATTR, -1)
    if hasattr(session.config, "workeroutput"):
        session.config.workeroutput["peak_rss_mb"] = peak


_nodes = []


def pytest_testnodedown(node, error):
    _nodes.append(getattr(node, "workeroutput", {}).get("peak_rss_mb", -1))


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    own = getattr(config, _PEAK_ATTR, -1)
    worker_peaks = [p for p in _nodes if p and p > 0]
    lines = [f"┬─ resource report ─ controller peak: {own}MB"]
    if worker_peaks:
        lines.append(
            f"   ├─ {len(worker_peaks)} xdist workers · peaks {min(worker_peaks)}"
            f"-{max(worker_peaks)}MB · aggregate ~{sum(worker_peaks)}MB"
        )
    lines.append("   └─ budget: 750MB/worker + 4GB system reserve (memory-aware -n auto)")

    # ── [doom_guy 2026-09-28] NEVER hide the result ──────────────────────────
    # This hook previously did `tr.sep_title = None`, which stripped pytest's
    # "=== short test summary info ===" section. That is the SAME defect class
    # as the phantom `--ignore` (a green build over a suite that never ran) and
    # as `is-active` returning true during an auto-restart: a reporting surface
    # that cannot go red. With the title suppressed, `pytest --collect-only -q`
    # printed NO test count at all — 2410 tests collected and the terminal said
    # nothing about it, so a human could not tell 0 from 2410.
    #
    # Fix: leave pytest's own summary intact, and print an explicit machine-
    # checkable count line FIRST so the number is visible even when the terminal
    # is being scrolled, piped, or truncated. The counts are read from pytest's
    # own stats object, not recomputed, so they cannot drift from reality.
    stats = terminalreporter.stats
    # ── Count sources, in priority order ───────────────────────────────────
    # This hook receives DIFFERENT reporter objects depending on who is
    # driving the terminal:
    #   * pytest-tldr (installed, and it hijacks the reporter) passes its OWN
    #     object as `terminalreporter`. It keys results as "x"/"f"/"E" and keeps
    #     its own `_n_tests`, and it prints a bare "OK" instead of a count — so
    #     reading only `stats["passed"]` under tldr yields zeros, which is how a
    #     2410-test run renders as "collected=0".
    #   * plain pytest passes the real TerminalReporter, where
    #     `stats["passed"]` and `session.testscollected` are populated.
    # Read all of them, prefer whichever is non-zero, and never report a count
    # of 0 when tests demonstrably ran.
    def _count(*keys) -> int:
        total = 0
        for k in keys:
            try:
                v = stats.get(k, [])  # type: ignore[union-attr]
            except Exception:
                v = []
            if v is None:
                continue
            try:
                total += len(v)
            except TypeError:
                total += int(v)
        return total

    # [maat 2026-09-28] Prefer the session's own count over the reporter's.
    # Measured on a real full-suite run: JSON reported collected=2435 while this
    # line printed 2396 — a 39-test understatement, because pytest-tldr's
    # `_n_tests` is stale under `-n auto` (it does not see every worker's share).
    # `session.testscollected` is the authoritative figure and is what the JSON
    # report agrees with, so it is now consulted FIRST. `_n_tests` remains only
    # as a last resort, for reporters that expose no session object.
    sess = getattr(terminalreporter, "_session", None)
    collected = int(getattr(sess, "testscollected", 0) or 0)
    if not collected:
        collected = int(getattr(terminalreporter, "_n_tests", 0) or 0)
    if not collected:
        collected = _count("collected")


    passed = _count("passed", "P")
    failed = _count("failed", "f")
    errored = _count("error", "E")
    skipped = _count("skipped", "s")
    xfailed = _count("xfailed")
    xpassed = _count("xpassed", "X")

    # [maat 2026-09-28] Last-resort tally for a reporter that keeps NO
    # reliable per-outcome keys. Measured on pytest-tldr 0.2.6, installed and
    # DEFAULT here: its stats dict is literally {'.': [TestReport, ...]} in a
    # single-process run, and under `-n auto` it carries a PARTIAL key set
    # (observed: 'error' present, 'passed' absent). So an "all keys are zero"
    # trigger is not sufficient — it produced `passed=0` for a 2373-test run in
    # which ~2340 passed. Detecting the reporter BY CLASS and then tallying the
    # reports directly is deterministic; guessing from the keys was not.
    #
    # The entries ARE TestReport objects carrying `.outcome`, so the tally is
    # recoverable. Only engaged for TLDR reporters, so the real
    # TerminalReporter path is provably untouched. Visibility only: it reads
    # reports that already exist and writes no test state.
    _tldr = "TLDR" in type(terminalreporter).__name__.upper()
    if _tldr or not (passed or failed or errored or skipped or xfailed or xpassed):
        from collections import Counter as _Counter

        # A nodeid can appear up to three times (setup/call/teardown). Keep the
        # LAST report per nodeid so a setup error is not masked by, or double
        # counted with, its own teardown entry.
        _last: dict = {}
        try:
            for _v in stats.values():
                for _r in _v or []:
                    _nid = getattr(_r, "nodeid", None)
                    if _nid is not None:
                        _last[_nid] = getattr(_r, "outcome", "?")
        except Exception:  # pragma: no cover - never let reporting break the run
            _last = {}
        _t = _Counter(_last.values())
        passed = _t.get("passed", 0)
        failed = _t.get("failed", 0)
        errored = _t.get("error", 0)
        skipped = _t.get("skipped", 0)
        xfailed = _t.get("xfailed", 0)
        xpassed = _t.get("xpassed", 0)

    # If passed+failed+error+skipped+xfailed is non-zero but collected is 0,
    # the run really did execute tests; derive rather than print a false zero.
    executed = passed + failed + errored + skipped + xfailed + xpassed
    if not collected and executed:
        collected = executed

    # ── Authoritative counts ──────────────────────────────────────────────
    # Under pytest-tldr the per-category stats above are unreliable (it keys
    # outcomes "x"/"f"/"E" and folds passes away), so they under-report: a run
    # that really passed 2301 showed passed=0. That is the same lie in a new
    # place, so when pytest-json-report is available we take its counts as
    # authoritative. It is a declared test dependency and reads the same
    # in-process results — it does not re-run anything.
    if config.pluginmanager.hasplugin("jsonreport"):
        try:
            import json as _json
            from pathlib import Path as _Path

            rep_path = getattr(config, "json_report_file", None)
            if rep_path is None:
                rep_path = getattr(config.option, "json_report_file", None)
            if rep_path and _Path(rep_path).exists():
                with open(rep_path, encoding="utf-8") as fh:
                    _s = _json.load(fh).get("summary", {})
                if _s:
                    collected = int(_s.get("collected", collected) or collected)
                    passed = int(_s.get("passed", passed) or passed)
                    failed = int(_s.get("failed", failed) or failed)
                    errored = int(_s.get("error", errored) or errored)
                    skipped = int(_s.get("skipped", skipped) or skipped)
                    xfailed = int(_s.get("xfailed", xfailed) or xfailed)
                    xpassed = int(_s.get("xpassed", xpassed) or xpassed)
        except Exception:
            pass  # never let reporting break the test run

    verdict = "PASS" if (failed == 0 and errored == 0) else "FAIL"
    terminalreporter.write_line(
        f"═══ OMEGA TEST RESULT: {verdict} | collected={collected} "
        f"passed={passed} failed={failed} errors={errored} "
        f"skipped={skipped} xfailed={xfailed} ═══"
    )
    for ln in lines:
        terminalreporter.write_line(ln)


from omega.memory_store import MemoryStore, reset_memory_store
from omega.oracle.context_builder import ContextBuilder
from omega.oracle.world_state import world_state
from omega.state import initialize_usm
from omega.observability import reset_observability
from omega.oracle.provider_registry import reset_provider_registry
from omega.oracle.resource_guard import reset_resource_guard

logger = logging.getLogger(__name__)

# NOTE: No global pytestmark = pytest.mark.anyio here. A global anyio mark
# forces EVERY test (including sync `def test_` functions) to run inside an
# async event loop — which breaks any sync code that calls anyio.run()
# internally ("Already running asyncio in this thread"). Tests that need
# async use explicit @pytest.mark.anyio (469 marks across 63 files).

# Fix AnyIO backend to asyncio only (removes [asyncio] suffix from test names)
@ pytest.fixture
def anyio_backend():
    return "asyncio"


@ pytest.fixture(autouse=True)
def _set_test_env(tmp_path, monkeypatch, request, anyio_backend):
    """Ensure OMEGA_ENV=test and isolated temp data dir for all tests.
    
    OMEGA_DATA_DIR is set to an autouse temp directory to prevent entity workspace
    scaffolding (EntityRegistry.add() → EntityWorkspaceManager.scaffold_workspace)
    from leaking test entities into the production data/entities/ directory.
    Previously, tests like test_wad_loader.py created direntity/, duplicate, etc.
    in the live data/entities/ tree.
    
    Teardown: reset_memory_store() closes the FTS5 SQLite connection on the
    MemoryStore singleton, preventing ResourceWarning: unclosed database.
    """
    monkeypatch.setenv("OMEGA_ENV", "test")
    monkeypatch.setenv("OMEGA_DATA_DIR", str(tmp_path))
    reset_memory_store()
    reset_observability()
    reset_provider_registry()
    reset_resource_guard()
    world_state.reset()
    import anyio
    from omega.state import reset_usm, initialize_usm
    # reset_usm is async — it MUST be awaited via anyio.run, or the USM
    # singleton is never cleared and state leaks between tests (e.g. the
    # session counter in session_manager tests kept incrementing).
    anyio.run(reset_usm)
    anyio.run(initialize_usm)
    
    def teardown():
        reset_memory_store()
        reset_observability()
        reset_provider_registry()
        reset_resource_guard()
        world_state.reset()
    
    request.addfinalizer(teardown)


@pytest.fixture
def temp_data_dir(tmp_path, monkeypatch):
    """Create isolated temp data directory for tests.
    
    This fixture exists for tests that need explicit access to the temp data path.
    The autouse _set_test_env already ensures OMEGA_DATA_DIR is isolated.
    """
    logger.debug("temp_data_dir: OMEGA_DATA_DIR=%s, OMEGA_ENV=%s", tmp_path, os.environ.get("OMEGA_ENV"))
    reset_memory_store()
    yield tmp_path
    reset_memory_store()


@pytest.fixture
def mock_memory_store():
    """Mock MemoryStore with configurable get_history return value."""
    store = MagicMock(spec=MemoryStore)
    store.get_history = AsyncMock(return_value=[])
    store.add_exchange = AsyncMock()
    return store


@pytest.fixture
def context_builder(mock_memory_store):
    """ContextBuilder with injected mock MemoryStore."""
    return ContextBuilder(memory_store=mock_memory_store)


@pytest.fixture
def sample_exchanges():
    """Standard test fixture: 2 conversation exchanges."""
    return [
        {
            "timestamp": "2026-05-16T10:00:00+00:00",
            "user": "What is strength?",
            "assistant": "Strength is the will to endure.",
            "metadata": {},
        },
        {
            "timestamp": "2026-05-16T10:01:00+00:00",
            "user": "And what is courage?",
            "assistant": "Courage is strength in the face of fear.",
            "metadata": {},
        },
    ]

# ============================================================================
# C-11 Test Infrastructure Fixtures
# ============================================================================

@pytest.fixture
def temp_entity_dir(tmp_path):
    """Create a temporary entity directory with minimal soul.yaml."""
    entities = tmp_path / "entities"
    entities.mkdir()
    entity = entities / "test_entity"
    entity.mkdir()
    soul = {"entity": {"name": "test_entity", "lessons_learned": []}}
    (entity / "soul.yaml").write_text(yaml.dump(soul))
    return entities


@pytest.fixture
def mock_soul_store(temp_entity_dir):
    """SoulStore with temp entities dir."""
    from omega.oracle.soul_store import SoulStore
    return SoulStore(temp_entity_dir)


@pytest.fixture
def mock_provider():
    """Mock provider config."""
    return {
        "name": "mock_provider",
        "type": "openai",
        "api_key": "test-key",
        "model": "test-model",
        "priority": 0,
        "enabled": True,
    }


# ── Shared-resource isolation: the OOM RAM sensor ─────────────────────────
# [carmack-20260928] FLAKY-POOL ROOT CAUSE, proven by execution.
#
# `ResourceGuard.lock()` calls `OOMProtector.check_available(required_gb)`,
# which reads the REAL host via `psutil.virtual_memory().available` (or
# /proc/meminfo). `Orchestrator.dispatch_agent` acquires that lock BEFORE it
# reaches `anyio.run_process`, so on a memory-pressured box the dispatch raises
# `InferenceOOMError` and the test's expected `{"status": "timeout"}` never
# arrives.
#
# Proof (both directions, same test, no skip/retry involved):
#   control  (normal box)                        -> 1 passed
#   OOMProtector.check_available forced to False -> 1 FAILED,
#       omega.errors.InferenceOOMError: Refusing model load: available RAM
#       below 1.0 GB safety threshold
#
# That is why the flaky pool was load-dependent rather than random: it fails
# when other agents are resident, passes when the box is quiet. A skip, a
# retry, or `-p no:randomly` would have hidden a real environmental coupling.
#
# The fix is isolation of the shared resource, not suppression: a test's
# outcome must not depend on how much RAM the host happens to have free.
# Tests that genuinely exercise the OOM sensor opt out via the
# `real_oom_sensor` marker so their subject is not stubbed away.
#
# DERIVED, NOT CURATED. The first two versions of this list were hand-written
# and both were wrong: v1 missed two files (broke the tests it was meant to
# protect), and v2 was silently swallowed by a concurrent edit that truncated
# the enclosing `mock_provider` function — the hook never ran, so the
# exemption was dead code and the tests failed again. Both failure modes are
# removed by construction below: the list is computed from the filesystem, and
# a self-check asserts the hook is reachable as a module-level pytest hook.
_OOM_SUBJECT_MARKERS = ("oom_protector", "check_available", "memavailable")


def _derive_real_oom_sensor_files() -> set:
    """Every test FILE whose source mentions the OOM sensor, derived not guessed.

    A curated list is a hole with a comment on it. Deriving it means a new
    OOM test file is exempt by construction, and a renamed/moved file cannot
    silently lose its exemption.
    """
    derived = set()
    for path in Path(__file__).parent.rglob("test_*.py"):
        if "__pycache__" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if any(tok in text for tok in _OOM_SUBJECT_MARKERS):
            derived.add(path.name)
    return derived


_REAL_OOM_SENSOR_FILES = _derive_real_oom_sensor_files()


def pytest_collection_modifyitems(config, items):
    """Tag tests whose subject IS the OOM sensor so they keep the real one."""
    for item in items:
        if item.path.name in _REAL_OOM_SENSOR_FILES:
            item.add_marker(pytest.mark.real_oom_sensor)


# [carmack-20260928] Structural self-check. A hook that is accidentally nested
# inside another function is silently dead — that is exactly what happened, and
# it cost a full green->red cycle on the PR gate. This asserts the hook is
# reachable, so the same mistake cannot pass silently a second time.
assert (
    "pytest_collection_modifyitems" in dir()
    or "pytest_collection_modifyitems" in globals()
), "pytest_collection_modifyitems must be module-level to be a hook"


@pytest.fixture(autouse=True)
def _isolate_oom_ram_sensor(request):
    """Neutralise the real-RAM sensor for tests that are not ABOUT it.

    Scoped per test via monkeypatch, so it cannot leak into a test that does
    want the real sensor, and cannot leak between tests.
    """
    if "real_oom_sensor" in request.keywords:
        return
    try:
        from omega.oracle.resource_guard import OOMProtector
    except ImportError:
        return
    if not hasattr(OOMProtector, "check_available"):
        return

    async def _always_available(self, required_gb):
        return True

    request.node.addfinalizer(lambda: None)
    m = request.getfixturevalue("monkeypatch")
    m.setattr(OOMProtector, "check_available", _always_available, raising=True)


@pytest.fixture
def mock_oom_protector():
    """OOMProtector with mocked RAM."""
    try:
        from omega.oracle.resource_guard import OOMProtector
        return OOMProtector
    except ImportError:
        pytest.skip("OOMProtector not yet implemented")


@pytest.fixture
def mock_admission_controller():
    """Fresh AdmissionController per test."""
    try:
        from omega.oracle.admission_controller import LocalInferenceAdmission
        return LocalInferenceAdmission()
    except ImportError:
        pytest.skip("AdmissionController not yet implemented")


@pytest.fixture
def soul_store(tmp_path):
    """SoulStore with temp entities dir."""
    try:
        from omega.oracle.soul_store import SoulStore
    except ImportError:
        pytest.skip("SoulStore not yet implemented")
    entities = tmp_path / "entities"
    entities.mkdir()
    (entities / "test_entity").mkdir()
    import yaml
    (entities / "test_entity" / "soul.yaml").write_text(
        yaml.dump({"entity": {"name": "test_entity", "lessons_learned": []}})
    )
    return SoulStore(entities)


@pytest.fixture
def oom_protector():
    """OOMProtector instance — return class from old resource_guard for backwards compat."""
    try:
        from omega.oracle.oom_protector import OOMProtector
        return OOMProtector()
    except ImportError:
        pytest.skip("OOMProtector not yet implemented")


@pytest.fixture
def admission_controller():
    """Fresh AdmissionController per test."""
    try:
        from omega.oracle.admission_controller import LocalInferenceAdmission
        return LocalInferenceAdmission()
    except ImportError:
        pytest.skip("AdmissionController not yet implemented")
