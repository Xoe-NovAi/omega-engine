# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-TEST-COMPACTION-CAPTURE-v1.0.0
# Tests for CompactionCaptureService — Snapshot-Before-Compaction Sidecar
#
# M21: Gate Integrity — contract tests verify return types
# M9: Error Integrity — tests for error paths
# M23: Failure Integrity — no soft-failures in tests

import json
import sqlite3
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from scripts.compaction_capture import (
    CompactionCaptureService,
    CompactionSummary,
    get_capture,
    reset_capture,
)


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def tmp_db(tmp_path: Path) -> Path:
    """Create a temporary OpenCode DB with the expected schema."""
    db_path = tmp_path / "opencode.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """
        CREATE TABLE message (
            id INTEGER PRIMARY KEY,
            session_id TEXT NOT NULL,
            data TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE part (
            id INTEGER PRIMARY KEY,
            message_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            time_created INTEGER NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def tmp_entity_dir(tmp_path: Path) -> Path:
    """Create a temporary entity data directory."""
    return tmp_path / "entities"


@pytest.fixture
def tmp_session_map(tmp_path: Path) -> Path:
    """Create a temporary session-entity map."""
    return tmp_path / "SESSION_ENTITY_MAP.yaml"


@pytest.fixture
def capture_service(
    tmp_db: Path, tmp_entity_dir: Path, tmp_session_map: Path
) -> CompactionCaptureService:
    """Create a CompactionCaptureService with temporary paths."""
    return CompactionCaptureService(
        opencode_db=tmp_db,
        entity_data_dir=tmp_entity_dir,
        session_map_path=tmp_session_map,
    )


def _insert_compaction_message(
    db_path: Path,
    message_id: int,
    session_id: str,
    summary_text: str,
    agent: str = "test_agent",
    model_id: str = "test_model",
) -> None:
    """Insert a compaction message into the test DB."""
    msg_data = json.dumps({
        "role": "assistant",
        "summary": True,
        "agent": agent,
        "modelID": model_id,
    })
    part_data = json.dumps({"type": "text", "text": summary_text})
    import time

    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "INSERT INTO message (id, session_id, data) VALUES (?, ?, ?)",
        (message_id, session_id, msg_data),
    )
    conn.execute(
        "INSERT INTO part (message_id, data, time_created) VALUES (?, ?, ?)",
        (message_id, part_data, int(time.time() * 1000)),
    )
    conn.commit()
    conn.close()


# ── Dataclass Contract Tests ──────────────────────────────────────────


class TestCompactionSummary:
    """Contract tests for CompactionSummary dataclass."""

    def test_summary_is_dataclass(self) -> None:
        """M21: Contract test — CompactionSummary is a dataclass."""
        summary = CompactionSummary(
            session_id="ses_001",
            message_id="1",
            part_id="1",
            summary_text="test summary",
            timestamp=1000.0,
        )
        assert isinstance(summary, CompactionSummary)
        assert isinstance(summary.session_id, str)
        assert isinstance(summary.message_id, str)
        assert isinstance(summary.part_id, str)
        assert isinstance(summary.summary_text, str)
        assert isinstance(summary.timestamp, float)
        assert isinstance(summary.agent, str)
        assert isinstance(summary.model_id, str)

    def test_char_count(self) -> None:
        """char_count returns the length of the summary text."""
        summary = CompactionSummary(
            session_id="ses_001",
            message_id="1",
            part_id="1",
            summary_text="hello world",
            timestamp=1000.0,
        )
        assert summary.char_count == 11

    def test_char_count_empty(self) -> None:
        """char_count returns 0 for empty summary."""
        summary = CompactionSummary(
            session_id="ses_001",
            message_id="1",
            part_id="1",
            summary_text="",
            timestamp=1000.0,
        )
        assert summary.char_count == 0

    def test_default_values(self) -> None:
        """Default values for optional fields."""
        summary = CompactionSummary(
            session_id="ses_001",
            message_id="1",
            part_id="1",
            summary_text="test",
            timestamp=1000.0,
        )
        assert summary.reason == "unknown"
        assert summary.agent == "unknown"
        assert summary.model_id == "unknown"
        assert summary.raw_data == {}


# ── CompactionCaptureService Tests ────────────────────────────────────


class TestCompactionCaptureService:
    """Tests for the CompactionCaptureService class."""

    def test_default_config(self) -> None:
        """Default config uses standard paths."""
        svc = CompactionCaptureService()
        assert svc._opencode_db == Path.home() / ".local" / "share" / "opencode" / "opencode.db"
        assert svc._poll_interval == 5.0

    def test_custom_config(self, tmp_path: Path) -> None:
        """Custom config overrides defaults."""
        svc = CompactionCaptureService(
            opencode_db=tmp_path / "custom.db",
            poll_interval=10.0,
        )
        assert svc._opencode_db == tmp_path / "custom.db"
        assert svc._poll_interval == 10.0

    def test_initial_status(self, capture_service: CompactionCaptureService) -> None:
        """Initial status reflects clean state."""
        status = capture_service.get_status()
        assert isinstance(status, dict)
        assert status["running"] is False
        assert status["last_seen_message_id"] == 0
        assert status["stats"]["total_scanned"] == 0
        assert status["stats"]["total_captured"] == 0
        assert status["stats"]["total_errors"] == 0

    def test_scan_empty_db(self, capture_service: CompactionCaptureService) -> None:
        """Scanning an empty DB returns no results."""
        captured = capture_service.scan_for_summaries()
        assert isinstance(captured, list)
        assert len(captured) == 0

    def test_scan_missing_db(self, tmp_entity_dir: Path, tmp_session_map: Path) -> None:
        """Scanning with missing DB returns empty list (M23 compliant)."""
        svc = CompactionCaptureService(
            opencode_db=Path("/nonexistent/opencode.db"),
            entity_data_dir=tmp_entity_dir,
            session_map_path=tmp_session_map,
        )
        captured = svc.scan_for_summaries()
        assert captured == []

    def test_scan_captures_summary(
        self,
        capture_service: CompactionCaptureService,
        tmp_db: Path,
    ) -> None:
        """Scan captures a compaction summary from the DB."""
        _insert_compaction_message(
            tmp_db,
            message_id=100,
            session_id="ses_test_001",
            summary_text="This is a compaction summary.",
            agent="kali",
            model_id="gpt-4",
        )

        captured = capture_service.scan_for_summaries()
        assert len(captured) == 1
        assert captured[0].session_id == "ses_test_001"
        assert captured[0].message_id == "100"
        assert captured[0].summary_text == "This is a compaction summary."
        assert captured[0].agent == "kali"
        assert captured[0].model_id == "gpt-4"

    def test_scan_monotonic_idempotency(
        self,
        capture_service: CompactionCaptureService,
        tmp_db: Path,
    ) -> None:
        """Scanning twice with the same data captures only once."""
        _insert_compaction_message(
            tmp_db, message_id=100, session_id="ses_001", summary_text="summary 1"
        )

        captured1 = capture_service.scan_for_summaries()
        assert len(captured1) == 1

        captured2 = capture_service.scan_for_summaries()
        assert len(captured2) == 0  # Already seen

    def test_scan_captures_multiple(
        self,
        capture_service: CompactionCaptureService,
        tmp_db: Path,
    ) -> None:
        """Scan captures multiple new summaries."""
        for i in range(3):
            _insert_compaction_message(
                tmp_db,
                message_id=100 + i,
                session_id=f"ses_{i:03d}",
                summary_text=f"summary {i}",
            )

        captured = capture_service.scan_for_summaries()
        assert len(captured) == 3
        # Monotonically ordered
        assert captured[0].message_id == "100"
        assert captured[2].message_id == "102"

    def test_scan_routes_to_entity_workspace(
        self,
        capture_service: CompactionCaptureService,
        tmp_db: Path,
        tmp_entity_dir: Path,
    ) -> None:
        """Scanned summaries are routed to entity workspace as markdown."""
        _insert_compaction_message(
            tmp_db,
            message_id=100,
            session_id="ses_test_001",
            summary_text="Test compaction content.",
        )

        capture_service.scan_for_summaries()

        # Default entity since no session map
        workspace = tmp_entity_dir / "default" / "compactions"
        assert workspace.exists()
        files = list(workspace.glob("*.md"))
        assert len(files) == 1

        content = files[0].read_text()
        assert "Test compaction content." in content
        assert "ses_test_001" in content
        assert "**Entity**: default" in content

    def test_scan_empty_text_skipped(
        self,
        capture_service: CompactionCaptureService,
        tmp_db: Path,
    ) -> None:
        """Messages with empty summary text are skipped."""
        msg_data = json.dumps({
            "role": "assistant",
            "summary": True,
            "agent": "test",
            "modelID": "model",
        })
        part_data = json.dumps({"type": "text", "text": ""})
        import time

        conn = sqlite3.connect(str(tmp_db))
        conn.execute(
            "INSERT INTO message (id, session_id, data) VALUES (?, ?, ?)",
            (100, "ses_001", msg_data),
        )
        conn.execute(
            "INSERT INTO part (message_id, data, time_created) VALUES (?, ?, ?)",
            (100, part_data, int(time.time() * 1000)),
        )
        conn.commit()
        conn.close()

        captured = capture_service.scan_for_summaries()
        assert len(captured) == 0

    def test_scan_non_summary_skipped(
        self,
        capture_service: CompactionCaptureService,
        tmp_db: Path,
    ) -> None:
        """Non-summary messages are not captured."""
        msg_data = json.dumps({
            "role": "assistant",
            "summary": False,
            "agent": "test",
            "modelID": "model",
        })
        part_data = json.dumps({"type": "text", "text": "not a summary"})
        import time

        conn = sqlite3.connect(str(tmp_db))
        conn.execute(
            "INSERT INTO message (id, session_id, data) VALUES (?, ?, ?)",
            (100, "ses_001", msg_data),
        )
        conn.execute(
            "INSERT INTO part (message_id, data, time_created) VALUES (?, ?, ?)",
            (100, part_data, int(time.time() * 1000)),
        )
        conn.commit()
        conn.close()

        captured = capture_service.scan_for_summaries()
        assert len(captured) == 0

    def test_get_current_max_id(
        self,
        capture_service: CompactionCaptureService,
        tmp_db: Path,
    ) -> None:
        """_get_current_max_id returns the highest message ID."""
        import time

        conn = sqlite3.connect(str(tmp_db))
        for i in range(1, 6):
            conn.execute(
                "INSERT INTO message (id, session_id, data) VALUES (?, ?, ?)",
                (i * 100, "ses_001", json.dumps({"role": "user"})),
            )
        conn.commit()
        conn.close()

        max_id = capture_service._get_current_max_id()
        assert max_id == 500


# ── Session Map Tests ─────────────────────────────────────────────────


class TestSessionMap:
    """Tests for session-to-entity mapping."""

    def test_load_session_map(
        self, capture_service: CompactionCaptureService, tmp_session_map: Path
    ) -> None:
        """Session map is loaded from YAML file."""
        tmp_session_map.write_text(
            """
session_mappings:
  - opencode_session: "ses_alpha"
    omega_entity: "kali"
  - opencode_session: "ses_beta"
    omega_entity: "lilith"
default_entity: "default"
"""
        )
        mapping = capture_service._load_session_map()
        assert mapping == {"ses_alpha": "kali", "ses_beta": "lilith"}

    def test_load_missing_map(
        self, capture_service: CompactionCaptureService
    ) -> None:
        """Missing session map returns empty dict."""
        mapping = capture_service._load_session_map()
        assert mapping == {}

    def test_resolve_entity_mapped(
        self, capture_service: CompactionCaptureService, tmp_session_map: Path
    ) -> None:
        """Mapped session ID resolves to correct entity."""
        tmp_session_map.write_text(
            """
session_mappings:
  - opencode_session: "ses_alpha"
    omega_entity: "kali"
"""
        )
        capture_service._session_map = capture_service._load_session_map()
        entity = capture_service._resolve_entity("ses_alpha")
        assert entity == "kali"

    def test_resolve_entity_unmapped(
        self, capture_service: CompactionCaptureService
    ) -> None:
        """Unmapped session ID resolves to 'default'."""
        entity = capture_service._resolve_entity("ses_unknown")
        assert entity == "default"


# ── Markdown Formatting Tests ─────────────────────────────────────────


class TestMarkdownFormatting:
    """Tests for markdown output format."""

    def test_format_markdown(
        self, capture_service: CompactionCaptureService
    ) -> None:
        """Markdown includes all required metadata fields."""
        summary = CompactionSummary(
            session_id="ses_abc123",
            message_id="42",
            part_id="99",
            summary_text="Test content here.",
            timestamp=1700000000.0,
            agent="doom_guy",
            model_id="llama-3-70b",
        )
        md = capture_service._format_markdown(summary, "doom_guy")
        assert "**Entity**: doom_guy" in md
        assert "**Session**: ses_abc123" in md
        assert "**Message ID**: 42" in md
        assert "**Part ID**: 99" in md
        assert "**Agent**: doom_guy" in md
        assert "**Model**: llama-3-70b" in md
        assert "Test content here." in md


# ── Singleton Tests ──────────────────────────────────────────────────


class TestSingleton:
    def teardown_method(self) -> None:
        reset_capture()

    def test_get_capture_singleton(self) -> None:
        """get_capture always returns the same instance."""
        c1 = get_capture()
        c2 = get_capture()
        assert c1 is c2

    def test_reset_capture(self) -> None:
        """reset_capture creates a new instance on next access."""
        c1 = get_capture()
        reset_capture()
        c2 = get_capture()
        assert c1 is not c2


# ── Stats Tests ──────────────────────────────────────────────────────


class TestStats:
    """Tests for statistics tracking."""

    def test_stats_after_scan(
        self,
        capture_service: CompactionCaptureService,
        tmp_db: Path,
    ) -> None:
        """Stats are updated after scanning."""
        _insert_compaction_message(
            tmp_db, message_id=100, session_id="ses_001", summary_text="summary"
        )
        capture_service.scan_for_summaries()

        stats = capture_service._stats
        assert stats["total_scanned"] == 1
        assert stats["total_captured"] == 0  # Captured count is incremented in loop
        assert stats["total_errors"] == 0
