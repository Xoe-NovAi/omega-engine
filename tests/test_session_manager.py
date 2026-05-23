"""Tests for SessionManager — entity-scoped rolling sessions.

AP: AP-SESSION-MANAGER-TESTS-v1.0.0
Covers: R51 Phase 0d — SessionManager test contract (15 tests)
"""

import json
import pytest
from datetime import datetime, timezone

from omega.oracle.session_manager import SessionManager


@pytest.fixture
def session_dir(tmp_path, monkeypatch):
    """Create isolated session directory."""
    monkeypatch.setenv("OMEGA_DATA_DIR", str(tmp_path))
    sd = tmp_path / "sessions"
    sd.mkdir(parents=True, exist_ok=True)
    return sd


@pytest.fixture
def manager(session_dir):
    """SessionManager with isolated temp directory."""
    return SessionManager(session_dir=session_dir)


class TestNewSession:
    """Test new session creation."""

    @pytest.mark.anyio
    async def test_get_session_id_creates_new_session(self, manager, session_dir):
        """First call creates a new session file."""
        session_id = await manager.get_session_id("sophia")
        assert session_id is not None
        assert (session_dir / "sophia.active").exists()

    @pytest.mark.anyio
    async def test_session_id_format(self, manager):
        """Session ID follows ses_{YYYYMMDD}_{entity_slug}_{counter}."""
        session_id = await manager.get_session_id("sophia")
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        assert session_id == f"ses_{today}_sophia_001"

    @pytest.mark.anyio
    async def test_session_id_format_with_spaces(self, manager):
        """Entity names with spaces are slugified."""
        session_id = await manager.get_session_id("The Architect")
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        assert session_id == f"ses_{today}_the_architect_001"

    @pytest.mark.anyio
    async def test_session_file_content(self, manager, session_dir):
        """Active file contains date, counter, session_id, entity, created_at."""
        await manager.get_session_id("sophia")
        active_file = session_dir / "sophia.active"
        data = json.loads(active_file.read_text())
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        assert data["date"] == today
        assert data["counter"] == 1
        assert data["entity"] == "sophia"
        assert "created_at" in data
        assert "session_id" in data


class TestSessionReuse:
    """Test same-day session reuse."""

    @pytest.mark.anyio
    async def test_same_day_returns_existing_session(self, manager):
        """Second call on same day returns the same session ID."""
        first = await manager.get_session_id("sophia")
        second = await manager.get_session_id("sophia")
        assert first == second

    @pytest.mark.anyio
    async def test_different_entities_get_different_sessions(self, manager):
        """Different entities have separate session files."""
        sophia_id = await manager.get_session_id("sophia")
        maat_id = await manager.get_session_id("maat")
        assert sophia_id != maat_id
        assert "sophia" in sophia_id
        assert "maat" in maat_id


class TestRollover:
    """Test daily counter rollover."""

    @pytest.mark.anyio
    async def test_rollover_new_day_new_session(self, manager):
        """When date changes, a new session is created with incremented counter."""
        today = datetime.now(timezone.utc).strftime("%Y%m%d")

        # First session for today
        first = await manager.get_session_id("sophia")
        assert today in first

        # Simulate tomorrow by writing a fake active file with yesterday's date
        active_file = manager.session_dir / "sophia.active"
        fake_data = {
            "date": "20260101",  # Old date
            "counter": 5,
            "session_id": "ses_20260101_sophia_005",
            "entity": "sophia",
        }
        active_file.write_text(json.dumps(fake_data))

        # Next call should create new session with counter=6
        new_id = await manager.get_session_id("sophia")
        assert today in new_id
        assert "sophia_006" in new_id


class TestCorruption:
    """Test corrupted session file recovery."""

    @pytest.mark.anyio
    async def test_corrupted_session_file_resets(self, manager, session_dir):
        """Invalid JSON in active file is handled gracefully — new session created."""
        active_file = session_dir / "sophia.active"
        active_file.write_text("not valid json {{{")

        session_id = await manager.get_session_id("sophia")
        assert session_id is not None
        assert "sophia_001" in session_id

    @pytest.mark.anyio
    async def test_empty_session_file_resets(self, manager, session_dir):
        """Empty active file is handled gracefully."""
        active_file = session_dir / "sophia.active"
        active_file.write_text("")

        session_id = await manager.get_session_id("sophia")
        assert session_id is not None

    @pytest.mark.anyio
    async def test_missing_keys_in_session_file(self, manager, session_dir):
        """Session file with missing keys creates new session."""
        active_file = session_dir / "sophia.active"
        active_file.write_text(json.dumps({"foo": "bar"}))

        session_id = await manager.get_session_id("sophia")
        assert session_id is not None


class TestTransient:
    """Test transient mode."""

    def test_transient_returns_trace_id(self, manager):
        """Transient mode returns the trace_id as session_id."""
        trace_id = "trc_abc123"
        session_id = manager.get_session_id_transient(trace_id)
        assert session_id == trace_id

    def test_transient_no_file_created(self, manager, session_dir):
        """Transient mode does not create any session file."""
        manager.get_session_id_transient("trc_test_001")
        assert not (session_dir / "trc_test_001.active").exists()


class TestEnvironment:
    """Test environment-specific behavior."""

    def test_omega_env_test_skips_mkdir(self, tmp_path, monkeypatch):
        """When OMEGA_ENV=test, session_dir is not auto-created."""
        monkeypatch.setenv("OMEGA_ENV", "test")
        test_dir = tmp_path / "no_auto_create" / "sessions"
        SessionManager(session_dir=test_dir)
        # Directory should NOT exist
        assert not test_dir.exists()

    def test_omega_env_production_creates_dir(self, tmp_path, monkeypatch):
        """When OMEGA_ENV is not test, session_dir is created."""
        monkeypatch.setenv("OMEGA_ENV", "production")
        test_dir = tmp_path / "auto_create" / "sessions"
        SessionManager(session_dir=test_dir)
        # Directory SHOULD exist
        assert test_dir.exists()
