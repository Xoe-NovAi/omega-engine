"""Tests for Belial Legacy Deep Mining Keeper.

Uses temporary directories and mock file systems to avoid touching real partitions.
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, AsyncMock

import pytest

# Mock OMEGA_DATA_DIR to a temp dir before importing entity_belial
_omd = None


@pytest.fixture(autouse=True)
def mock_data_dir(monkeypatch, tmp_path):
    """Mock OMEGA_DATA_DIR to a temporary path for all tests."""
    data_dir = tmp_path / "omega" / "data"
    data_dir.mkdir(parents=True)
    monkeypatch.setenv("OMEGA_DATA_DIR", str(data_dir))
    # Re-import after setting env (monkeypatch auto-restores at teardown)
    return data_dir


@pytest.fixture
def belial(mock_data_dir):
    # Need to import after env is set
    from omega.entity_belial import BelialMiner
    with patch("omega.entity_belial.DATA_DIR", mock_data_dir):
        miner = BelialMiner()
        yield miner


@pytest.fixture
def temp_mine(tmp_path):
    """Create a temporary legacy mine directory with sample files."""
    mine = tmp_path / "test-omega-legacy"
    mine.mkdir(exist_ok=True)

    # Create sample files of different types
    (mine / "config.yaml").write_text("key: value\nsetting: true\n")
    (mine / "session_20260514.md").write_text("# Session Log\nImportant narrative data.\n")
    (mine / "orchestrator.py").write_text("import os\ndef run(): pass\n")
    (mine / "README.md").write_text("# Project\nDocumentation.\n")
    (mine / "data.json").write_text('{"key": "value"}')
    (mine / ".env.secret").write_text("API_KEY=test")
    (mine / "__pycache__").mkdir()
    (mine / "__pycache__" / "cache.pyc").write_text("binary")
    (mine / "node_modules").mkdir()
    (mine / "node_modules" / "dep.js").write_text("skip me")
    return mine


class TestBelialMinerInit:
    def test_init_loads_empty_history(self, belial):
        """BelialMiner initializes with an empty mining queue."""
        assert belial.mining_queue == []
        assert len(belial.mines) > 0

    def test_init_loads_existing_history(self, belial, mock_data_dir):
        """BelialMiner loads mining history JSON if it exists."""
        history_dir = mock_data_dir / "mining_queue"
        history_dir.mkdir(parents=True, exist_ok=True)
        history = [{"path": "test.yaml", "classification": "technical"}]
        (history_dir / "mining_history.json").write_text(json.dumps(history))

        from omega.entity_belial import BelialMiner
        miner = BelialMiner()
        assert len(miner.mining_queue) == 1
        assert miner.mining_queue[0]["path"] == "test.yaml"

    def test_init_invalid_history(self, belial, mock_data_dir):
        """BelialMiner handles corrupt history JSON gracefully."""
        history_dir = mock_data_dir / "mining_queue"
        history_dir.mkdir(parents=True, exist_ok=True)
        (history_dir / "mining_history.json").write_text("not valid json{{{")

        from omega.entity_belial import BelialMiner
        miner = BelialMiner()
        assert miner.mining_queue == []

    def test_legacy_mines_configured(self):
        """LEGACY_MINES should include expected mine locations."""
        from omega.entity_belial import LEGACY_MINES
        mine_names = [m[0] for m in LEGACY_MINES]
        assert "xna-omega-legacy" in mine_names
        assert "omega-stack-legacy" in mine_names
        assert "omega-original" in mine_names
        assert "docs_1-research" in mine_names
        assert "archive-backups" in mine_names


class TestScanMine:
    def test_scan_mine_finds_files(self, belial, temp_mine):
        """scan_mine should find .yaml, .md, .py, .json files."""
        artifacts = belial.scan_mine("test-mine", temp_mine)
        paths = [a["path"] for a in artifacts]
        # Should find our 5 sample files
        assert any("config.yaml" in p for p in paths)
        assert any("session_20260514.md" in p for p in paths)
        assert any("orchestrator.py" in p for p in paths)
        assert any("README.md" in p for p in paths)
        assert any("data.json" in p for p in paths)
        # Should NOT find pycache or node_modules files
        assert not any("__pycache__" in a["path"] or "node_modules" in a["path"] for a in artifacts)

    def test_scan_mine_nonexistent(self, belial):
        """scan_mine on nonexistent path returns empty list."""
        artifacts = belial.scan_mine("void", Path("/tmp/nonexistent_omega_mine_xyz"))
        assert artifacts == []

    def test_scan_mine_skips_large_files(self, belial, temp_mine):
        """scan_mine should skip files > 1MB."""
        large_file = temp_mine / "huge_data.bin"
        large_file.write_text("x" * 2_000_000)  # 2MB
        artifacts = belial.scan_mine("test-mine", temp_mine)
        assert not any("huge_data" in a["path"] for a in artifacts)

    def test_scan_mine_has_metadata(self, belial, temp_mine):
        """Each artifact should have source_mine, path, size_kb, suffix."""
        artifacts = belial.scan_mine("test-mine", temp_mine)
        assert len(artifacts) > 0
        for a in artifacts:
            assert "source_mine" in a
            assert "path" in a
            assert "size_kb" in a
            assert "suffix" in a
            assert "discovered_at" in a
            assert a["source_mine"] == "test-mine"


class TestClassifyArtifact:
    @pytest.fixture
    def belial_classify(self, belial):
        return belial

    def test_classify_config_yaml(self, belial):
        """Config .yaml files are 'technical'."""
        a = {"path": "project/config.yaml", "suffix": ".yaml"}
        assert belial.classify_artifact(a) == "technical"

    def test_classify_config_yml(self, belial):
        """Config .yml files are 'technical'."""
        a = {"path": "project/settings.yml", "suffix": ".yml"}
        assert belial.classify_artifact(a) == "technical"

    def test_classify_session(self, belial):
        """Session/chat files are 'strategic'."""
        a = {"path": "sessions/chat_export.md", "suffix": ".md"}
        assert belial.classify_artifact(a) == "strategic"

    def test_classify_python(self, belial):
        """Python source files are 'technical'."""
        a = {"path": "src/module.py", "suffix": ".py"}
        assert belial.classify_artifact(a) == "technical"

    def test_classify_markdown(self, belial):
        """Non-session markdown files are 'archival'."""
        a = {"path": "docs/notes.md", "suffix": ".md"}
        assert belial.classify_artifact(a) == "archival"

    def test_classify_noise(self, belial):
        """Unknown extensions are 'noise'."""
        a = {"path": "file.txt", "suffix": ".txt"}
        assert belial.classify_artifact(a) == "noise"

    def test_classify_json(self, belial):
        """Non-config .json files are 'archival'."""
        a = {"path": "data/dump.json", "suffix": ".json"}
        assert belial.classify_artifact(a) == "archival"


class TestSubmitToQueue:
    def test_submit_adds_artifacts(self, belial, temp_mine):
        """submit_to_queue should classify and add new artifacts."""
        artifacts = belial.scan_mine("test-mine", temp_mine)
        belial.submit_to_queue(artifacts)
        assert len(belial.mining_queue) == len(artifacts)
        # All should have classification assigned
        for a in belial.mining_queue:
            assert "classification" in a

    def test_submit_deduplicates(self, belial, temp_mine):
        """submit_to_queue should not add duplicate paths."""
        artifacts = belial.scan_mine("test-mine", temp_mine)
        belial.submit_to_queue(artifacts)
        assert len(belial.mining_queue) == len(artifacts)
        # Submit same artifacts again — should add none
        belial.submit_to_queue(artifacts)
        assert len(belial.mining_queue) == len(artifacts)

    def test_submit_persists_to_disk(self, belial, temp_mine, mock_data_dir):
        """submit_to_queue should save to mining_history.json."""
        artifacts = belial.scan_mine("test-mine", temp_mine)
        belial.submit_to_queue(artifacts)
        history_path = mock_data_dir / "mining_queue" / "mining_history.json"
        assert history_path.exists()
        with open(history_path) as f:
            saved = json.load(f)
        assert len(saved) == len(artifacts)


class TestGetPrioritizedQueue:
    def test_prioritizes_strategic(self, belial):
        """Strategic artifacts should come first."""
        belial.mining_queue = [
            {"path": "noise.txt", "classification": "noise"},
            {"path": "strategic.md", "classification": "strategic"},
            {"path": "tech.py", "classification": "technical"},
        ]
        prioritized = belial.get_prioritized_queue()
        assert prioritized[0]["classification"] == "strategic"
        assert prioritized[1]["classification"] == "technical"

    def test_empty_queue(self, belial):
        """Empty queue returns empty list."""
        assert belial.get_prioritized_queue() == []


class TestDiscoverOmegaFolders:
    def test_discover_omega_folders_nonexistent(self):
        """discover_omega_folders returns empty list when partitions don't exist."""
        from omega.entity_belial import discover_omega_folders, OMEGA_PARTITIONS
        with patch("omega.entity_belial.OMEGA_PARTITIONS", [Path("/nonexistent_omega_vault")]):
            found = discover_omega_folders()
            assert found == []

    def test_discover_omega_folders_full(self):
        """discover_omega_folders finds existing partitions and subfolders."""
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            # Create mock partition structure
            vault = td_path / "omega_vault"
            vault.mkdir()
            (vault / "projects").mkdir()
            (vault / "backups").mkdir()

            with patch("omega.entity_belial.OMEGA_PARTITIONS", [vault]):
                from omega.entity_belial import discover_omega_folders
                found = discover_omega_folders()
                assert vault in found
                assert len(found) >= 3  # vault + 2 subdirs


class TestDeepAnalyze:
    @pytest.mark.asyncio
    async def test_deep_analyze_empty_queue(self, belial):
        """deep_analyze with empty queue returns appropriate message."""
        result = await belial.deep_analyze(lambda x: "analysis")
        assert "No artifacts queued" in result

    @pytest.mark.asyncio
    async def test_deep_analyze_calls_gemma(self, belial, temp_mine):
        """deep_analyze should call the gemma_api_func with artifacts."""
        artifacts = belial.scan_mine("test-mine", temp_mine)
        belial.submit_to_queue(artifacts)

        mock_gemma = AsyncMock(return_value="Analysis complete")
        result = await belial.deep_analyze(mock_gemma)
        assert result == "Analysis complete"
        mock_gemma.assert_awaited_once()
        # The prompt should contain artifact summaries
        prompt_arg = mock_gemma.call_args[0][0]
        assert "Belial" in prompt_arg
        assert "P0 Legacy Deep Mining" in prompt_arg
