import pytest
import anyio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from src.omega.orchestrator.hmc_watcher import HMCWatcher

@pytest.fixture
def mock_oracle():
    with patch("src.omega.orchestrator.hmc_watcher.Oracle", autospec=True) as mock:
        yield mock

@pytest.mark.anyio
async def test_hmc_watcher_triggers_carmack(mock_oracle):
    """Verify that a RESEARCHER_BRIEF file triggers a summon to @john_carmack."""
    coord_dir = Path("tests/tmp/coord")
    coord_dir.mkdir(parents=True, exist_ok=True)
    
    watcher = HMCWatcher(coordination_dir=str(coord_dir))
    instance = mock_oracle.return_value
    instance.summon = AsyncMock()
    
    # Simulate a file creation event
    from types import SimpleNamespace
    event = SimpleNamespace(type="created", path=coord_dir / "RESEARCHER_BRIEF_001.md")
    
    await watcher._handle_event(event.path)
    
    instance.summon.assert_called_once()
    args, _ = instance.summon.call_args
    assert args[0] == "john_carmack"
    assert "Sovereign Synthesis Request" in args[1]

@pytest.mark.anyio
async def test_hmc_watcher_triggers_roc(mock_oracle):
    """Verify that a S_SYNTHESIS file triggers a summon to @roc_racoon."""
    coord_dir = Path("tests/tmp/coord")
    coord_dir.mkdir(parents=True, exist_ok=True)
    
    watcher = HMCWatcher(coordination_dir=str(coord_dir))
    instance = mock_oracle.return_value
    instance.summon = AsyncMock()
    
    # Simulate a file creation event
    from types import SimpleNamespace
    event = SimpleNamespace(type="created", path=coord_dir / "S_SYNTHESIS_001.md")
    
    await watcher._handle_event(event.path)
    
    instance.summon.assert_called_once()
    args, _ = instance.summon.call_args
    assert args[0] == "roc_racoon"
    assert "Sovereign Coordination Request" in args[1]

@pytest.mark.anyio
async def test_hmc_watcher_ignores_irrelevant_files(mock_oracle):
    """Verify that irrelevant files do not trigger summons."""
    coord_dir = Path("tests/tmp/coord")
    coord_dir.mkdir(parents=True, exist_ok=True)
    
    watcher = HMCWatcher(coordination_dir=str(coord_dir))
    instance = mock_oracle.return_value
    instance.summon = AsyncMock()
    
    from types import SimpleNamespace
    event = SimpleNamespace(type="created", path=coord_dir / "random_file.txt")
    
    await watcher._handle_event(event.path)
    
    instance.summon.assert_not_called()
