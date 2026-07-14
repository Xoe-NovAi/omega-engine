"""Tests for somatic_state.py — Binary LLM State Serialization (M20)."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from pathlib import Path
from omega.oracle.somatic_state import SomaticStateManager


class TestSomaticStateManager:
    @pytest.fixture
    def state_dir(self, tmp_path):
        return tmp_path / "somatic_states"

    @pytest.fixture
    def manager(self, state_dir):
        return SomaticStateManager(state_dir)

    def test_init_creates_directory(self, tmp_path):
        new_dir = tmp_path / "new_somatic_dir"
        assert not new_dir.exists()
        manager = SomaticStateManager(new_dir)
        assert new_dir.exists()
        assert new_dir.is_dir()

    @pytest.mark.anyio
    async def test_capture_state_success(self, manager):
        mock_context_ptr = 0x12345678
        mock_state_bytes = b"fake_somatic_state_data"
        state_id = "test_state_001"

        with patch("omega.oracle.somatic_state.llama_cpp") as mock_llama:
            mock_llama.llama_copy_state_data = MagicMock(return_value=mock_state_bytes)

            with patch("omega.oracle.somatic_state.anyio.to_thread.run_sync") as mock_run_sync:
                # First call: llama_copy_state_data
                # Second call: open file (we need to mock the async context manager)
                mock_file = AsyncMock()
                mock_file.__aenter__ = AsyncMock(return_value=mock_file)
                mock_file.__aexit__ = AsyncMock(return_value=None)
                mock_file.write = AsyncMock()
                
                mock_run_sync.side_effect = [
                    mock_state_bytes,  # llama_copy_state_data result
                    mock_file,         # open file context manager
                ]

                result = await manager.capture_state(mock_context_ptr, state_id)

                assert result is True
                assert mock_run_sync.call_count == 2

    @pytest.mark.anyio
    async def test_capture_state_failure_no_data(self, manager):
        mock_context_ptr = 0x12345678
        state_id = "test_state_002"

        with patch("omega.oracle.somatic_state.llama_cpp") as mock_llama:
            mock_llama.llama_copy_state_data = MagicMock(return_value=None)

            result = await manager.capture_state(mock_context_ptr, state_id)

            assert result is False

    @pytest.mark.anyio
    async def test_capture_state_exception(self, manager):
        mock_context_ptr = 0x12345678
        state_id = "test_state_003"

        with patch("omega.oracle.somatic_state.anyio.to_thread.run_sync") as mock_run_sync:
            mock_run_sync.side_effect = RuntimeError("C-call failed")

            result = await manager.capture_state(mock_context_ptr, state_id)

            assert result is False

    @pytest.mark.anyio
    async def test_restore_state_success(self, manager):
        mock_context_ptr = 0x12345678
        state_id = "test_state_004"
        mock_state_bytes = b"restored_state_data"

        with patch("omega.oracle.somatic_state.anyio.to_thread.run_sync") as mock_run_sync:
            # First call: read_bytes
            # Second call: llama_set_state_data
            mock_run_sync.side_effect = [
                mock_state_bytes,  # file_path.read_bytes()
                None,              # llama_set_state_data returns None
            ]

            with patch("pathlib.Path.exists", return_value=True):
                result = await manager.restore_state(mock_context_ptr, state_id)

                assert result is True
                assert mock_run_sync.call_count == 2

    @pytest.mark.anyio
    async def test_restore_state_file_not_found(self, manager):
        mock_context_ptr = 0x12345678
        state_id = "nonexistent_state"

        with patch("pathlib.Path.exists", return_value=False):
            result = await manager.restore_state(mock_context_ptr, state_id)

            assert result is False

    @pytest.mark.anyio
    async def test_restore_state_exception(self, manager):
        mock_context_ptr = 0x12345678
        state_id = "test_state_005"

        with patch("omega.oracle.somatic_state.anyio.to_thread.run_sync") as mock_run_sync:
            mock_run_sync.side_effect = RuntimeError("C-call failed")

            with patch("pathlib.Path.exists", return_value=True):
                result = await manager.restore_state(mock_context_ptr, state_id)

                assert result is False

    @pytest.mark.anyio
    async def test_purge_state(self, manager):
        state_id = "test_state_006"

        with patch("pathlib.Path.exists", return_value=True):
            with patch("omega.oracle.somatic_state.anyio.to_thread.run_sync") as mock_run_sync:
                await manager.purge_state(state_id)
                mock_run_sync.assert_called_once()
                # Verify os.remove was called
                args, _ = mock_run_sync.call_args
                assert args[0].__name__ == "remove"

    @pytest.mark.anyio
    async def test_purge_state_not_exists(self, manager):
        state_id = "nonexistent_state"

        with patch("pathlib.Path.exists", return_value=False):
            with patch("omega.oracle.somatic_state.anyio.to_thread.run_sync") as mock_run_sync:
                await manager.purge_state(state_id)
                mock_run_sync.assert_not_called()

    def test_state_file_naming(self, manager):
        """Verify state files use .somatic extension."""
        state_id = "my_state"
        expected_path = manager.state_dir / f"{state_id}.somatic"
        # Just verify the path construction logic
        assert expected_path.suffix == ".somatic"
        assert expected_path.stem == state_id