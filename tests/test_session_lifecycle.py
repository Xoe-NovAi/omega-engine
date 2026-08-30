# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Tests for Session Lifecycle Manager.
AP: AP-SESSION-LIFECYCLE-TESTS-v1.0.0

Coverage:
- SessionState enum values
- SessionLifecycleConfig defaults
- SessionLifecycleManager lifecycle sweep
- get_session_state (all 5 states)
- recall_from_external
- list_sessions_by_state
- get_config_summary
"""

import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from omega.oracle.session_lifecycle import (
    SessionState,
    SessionLifecycleConfig,
    SessionInfo,
    LifecycleStats,
    SessionLifecycleManager,
)


# ── SessionState Enum ────────────────────────────────────────────────────────

class TestSessionState:
    def test_enum_values(self):
        assert SessionState.ACTIVE.value == "active"
        assert SessionState.ARCHIVED.value == "archived"
        assert SessionState.EXTERNAL.value == "external"
        assert SessionState.DELETED.value == "deleted"

    def test_all_states(self):
        assert len(SessionState) == 4


# ── SessionLifecycleConfig ───────────────────────────────────────────────────

class TestSessionLifecycleConfig:
    def test_defaults(self):
        config = SessionLifecycleConfig()
        assert config.archive_after_days == 7
        assert config.compress_after_days == 30
        assert config.external_after_days == 90
        assert config.delete_after_days == 365
        assert config.enable_external_archive is True
        assert config.enable_deletion is False
        assert "archive/sessions" in str(config.external_storage_path)

    def test_custom_config(self):
        config = SessionLifecycleConfig(
            archive_after_days=3,
            external_after_days=60,
            enable_deletion=True,
        )
        assert config.archive_after_days == 3
        assert config.external_after_days == 60
        assert config.enable_deletion is True


# ── LifecycleStats ───────────────────────────────────────────────────────────

class TestLifecycleStats:
    def test_default_values(self):
        stats = LifecycleStats()
        assert stats.archived == 0
        assert stats.externalized == 0
        assert stats.deleted == 0
        assert stats.recalled == 0
        assert stats.errors == 0
        assert stats.duration_ms == 0.0

    def test_to_dict(self):
        stats = LifecycleStats(archived=5, externalized=2, duration_ms=123.45)
        d = stats.to_dict()
        assert d["archived"] == 5
        assert d["externalized"] == 2
        assert d["duration_ms"] == 123.45
        assert d["deleted"] == 0


# ── SessionInfo ──────────────────────────────────────────────────────────────

class TestSessionInfo:
    def test_session_info_creation(self):
        info = SessionInfo(
            entity_name="kali",
            session_id="ses_20260701_kali_001",
            state=SessionState.ACTIVE,
            age_days=2.5,
        )
        assert info.entity_name == "kali"
        assert info.state == SessionState.ACTIVE
        assert info.compressed is False


# ── SessionLifecycleManager ──────────────────────────────────────────────────

class TestSessionLifecycleManager:
    """Tests for SessionLifecycleManager using mock MemoryStore."""

    def _make_manager(self, config=None):
        """Create a manager with a mock MemoryStore."""
        mock_store = MagicMock()
        mock_store.archive_old_sessions = AsyncMock(return_value=3)
        mock_store._get_entity_dir = MagicMock(return_value=Path("/tmp/test_entities"))
        mock_store._get_archive_dir = MagicMock(return_value=Path("/tmp/test_archive"))
        mock_store._hot = {}
        mock_store.list_sessions = AsyncMock(return_value=[])

        return SessionLifecycleManager(mock_store, config), mock_store

    def test_init_defaults(self):
        manager, store = self._make_manager()
        assert manager.config.archive_after_days == 7
        assert manager._store is store

    def test_init_custom_config(self):
        config = SessionLifecycleConfig(archive_after_days=5)
        manager, _ = self._make_manager(config)
        assert manager.config.archive_after_days == 5

    @pytest.mark.anyio
    async def test_run_lifecycle_archives_old_sessions(self):
        manager, store = self._make_manager()
        stats = await manager.run_lifecycle()
        assert stats.archived == 3
        store.archive_old_sessions.assert_called_once_with(older_than_days=7)

    @pytest.mark.anyio
    async def test_run_lifecycle_external_disabled(self):
        config = SessionLifecycleConfig(enable_external_archive=False)
        manager, store = self._make_manager(config)
        # Patch _move_to_external to verify it's NOT called
        manager._move_to_external = AsyncMock(return_value=0)
        stats = await manager.run_lifecycle()
        manager._move_to_external.assert_not_called()

    @pytest.mark.anyio
    async def test_run_lifecycle_external_enabled(self):
        config = SessionLifecycleConfig(enable_external_archive=True)
        manager, store = self._make_manager(config)
        manager._move_to_external = AsyncMock(return_value=2)
        stats = await manager.run_lifecycle()
        assert stats.externalized == 2
        manager._move_to_external.assert_called_once()

    @pytest.mark.anyio
    async def test_run_lifecycle_deletion_disabled_by_default(self):
        manager, _ = self._make_manager()
        manager._delete_beyond_retention = AsyncMock(return_value=1)
        stats = await manager.run_lifecycle()
        manager._delete_beyond_retention.assert_not_called()

    @pytest.mark.anyio
    async def test_run_lifecycle_deletion_enabled(self):
        config = SessionLifecycleConfig(enable_deletion=True)
        manager, _ = self._make_manager(config)
        manager._delete_beyond_retention = AsyncMock(return_value=1)
        stats = await manager.run_lifecycle()
        assert stats.deleted == 1

    @pytest.mark.anyio
    async def test_run_lifecycle_handles_archive_error(self):
        manager, store = self._make_manager()
        store.archive_old_sessions = AsyncMock(side_effect=RuntimeError("disk full"))
        stats = await manager.run_lifecycle()
        assert stats.errors == 1
        assert stats.archived == 0

    @pytest.mark.anyio
    async def test_run_lifecycle_records_duration(self):
        manager, _ = self._make_manager()
        stats = await manager.run_lifecycle()
        assert stats.duration_ms >= 0

    @pytest.mark.anyio
    async def test_get_session_state_active_hot_cache(self):
        manager, store = self._make_manager()
        store._hot = {"kali:ses_001": MagicMock()}
        state = await manager.get_session_state("kali", "ses_001")
        assert state == SessionState.ACTIVE

    @pytest.mark.anyio
    async def test_get_session_state_deleted_not_found(self):
        manager, store = self._make_manager()
        store._hot = {}
        with patch("omega.oracle.session_lifecycle.anyio.Path") as mock_path:
            mock_path.return_value.exists = AsyncMock(return_value=False)
            state = await manager.get_session_state("kali", "ses_nonexistent")
            assert state == SessionState.DELETED

    @pytest.mark.anyio
    async def test_recall_from_external_not_found(self):
        manager, _ = self._make_manager()
        with patch("omega.oracle.session_lifecycle.anyio.Path") as mock_path:
            mock_path.return_value.exists = AsyncMock(return_value=False)
            result = await manager.recall_from_external("kali", "ses_001")
            assert result is False

    @pytest.mark.anyio
    async def test_recall_from_external_success(self):
        manager, _ = self._make_manager()
        with patch("omega.oracle.session_lifecycle.anyio.Path") as mock_path:
            mock_path.return_value.exists = AsyncMock(return_value=True)
            mock_path.return_value.parent = MagicMock()
            mock_path.return_value.mkdir = AsyncMock()
            with patch("shutil.copy2"):
                with patch("omega.oracle.session_lifecycle.anyio.to_thread") as mock_thread:
                    mock_thread.run_sync = AsyncMock()
                    result = await manager.recall_from_external("kali", "ses_001")
                    assert result is True

    @pytest.mark.anyio
    async def test_recall_from_external_handles_error(self):
        manager, _ = self._make_manager()
        with patch("omega.oracle.session_lifecycle.anyio.Path") as mock_path:
            mock_path.return_value.exists = AsyncMock(return_value=True)
            mock_path.return_value.parent = MagicMock()
            mock_path.return_value.copy = AsyncMock(side_effect=RuntimeError("IO error"))
            mock_path.return_value.mkdir = AsyncMock()
            
            result = await manager.recall_from_external("kali", "ses_001")
            assert result is False

    @pytest.mark.anyio
    async def test_list_sessions_by_state_empty(self):
        manager, store = self._make_manager()
        store.list_sessions = AsyncMock(return_value=[])
        results = await manager.list_sessions_by_state()
        assert results == []

    def test_get_config_summary(self):
        manager, _ = self._make_manager()
        summary = manager.get_config_summary()
        assert summary["archive_after_days"] == 7
        assert summary["external_after_days"] == 90
        assert summary["enable_external_archive"] is True
        assert summary["enable_deletion"] is False
        assert "external_storage_path" in summary

    def test_stats_starts_empty(self):
        manager, _ = self._make_manager()
        assert manager.stats.archived == 0
        assert manager.stats.errors == 0
