import os
import logging
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from omega.memory_store import MemoryStore, reset_memory_store
from omega.oracle.context_builder import ContextBuilder
from omega.state import initialize_usm
from omega.observability import reset_observability

logger = logging.getLogger(__name__)


logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
async def _set_test_env(tmp_path, monkeypatch):
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
    yield
    reset_memory_store()
    reset_observability()


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
