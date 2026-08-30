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
    tr = terminalreporter._tw
    tr.sep_title = None
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

# Ensure AnyIO handles async fixtures in conftest
pytestmark = pytest.mark.anyio

# Fix AnyIO backend to asyncio only (removes [asyncio] suffix from test names)
@ pytest.fixture
def anyio_backend():
    return "asyncio"


@ pytest.fixture(autouse=True)
async def _set_test_env(tmp_path, monkeypatch, request, anyio_backend):
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
    from omega.state import reset_usm
    await reset_usm()
    await initialize_usm()
    
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
