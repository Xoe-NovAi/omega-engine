import os
import logging
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import tempfile
import yaml

from omega.memory_store import MemoryStore, reset_memory_store
from omega.oracle.context_builder import ContextBuilder
from omega.state import initialize_usm
from omega.observability import reset_observability

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
    from omega.state import reset_usm
    await reset_usm()
    await initialize_usm()
    
    def teardown():
        reset_memory_store()
        reset_observability()
    
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
    from omega.oracle.resource_guard import OOMProtector
    return OOMProtector


@pytest.fixture
def mock_admission_controller():
    """Fresh AdmissionController per test."""
    from omega.oracle.admission_controller import LocalInferenceAdmission
    return LocalInferenceAdmission()


@pytest.fixture
def soul_store(tmp_path):
    """SoulStore with temp entities dir."""
    from omega.oracle.soul_store import SoulStore
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
    """OOMProtector with mocked RAM."""
    from omega.oracle.resource_guard import OOMProtector
    return OOMProtector


@pytest.fixture
def admission_controller():
    """Fresh AdmissionController per test."""
    from omega.oracle.admission_controller import LocalInferenceAdmission
    return LocalInferenceAdmission()
