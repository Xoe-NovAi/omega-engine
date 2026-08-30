# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Error Gauntlet — Integration tests that provoke every error path.

Each scenario provokes a specific error condition and verifies:
1. Graceful degradation (no crash)
2. Error is logged (structured or via logger)
3. System continues operating after the error

Run with: PYTHONPATH=src python3 -m pytest tests/test_error_gauntlet.py -v
"""

import json
import logging
import os
from pathlib import Path
from unittest.mock import patch

import anyio
import pytest

from omega.observability import (
    ForensicsManager,
    ObservabilityEngine,
    JsonFormatter,
    setup_json_logging,
    EventType,
    CRASH_DIR,
    DATA_DIR,
)


# ── Fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture
def temp_crash_dir(tmp_path: Path) -> Path:
    """Isolated crash directory for testing."""
    d = tmp_path / "crashes"
    d.mkdir(parents=True, exist_ok=True)
    return d


@pytest.fixture
def forensics(temp_crash_dir: Path) -> ForensicsManager:
    return ForensicsManager(crash_dir=temp_crash_dir)


# ── Scenario 1: ForensicsManager crash dump ──────────────────────────────

@pytest.mark.anyio
async def test_scenario_crash_dump_creation_and_recovery(forensics: ForensicsManager):
    """Provoke a crash dump and verify it can be recovered."""
    error = ValueError("test crash: provider timeout")
    path = await forensics.snapshot(
        reason="test",
        error=error,
        trace_id="trc_gauntlet_001",
        extra_context={"provider": "ollama", "model": "qwen3"},
    )
    assert path.exists()
    assert "crash_" in path.name
    assert "trc_gauntlet_001" in path.name

    dump = forensics.check_recovery()
    assert dump is not None
    assert dump["reason"] == "test"
    assert dump["error"]["type"] == "ValueError"
    assert "provider timeout" in dump["error"]["message"]


# ── Scenario 2: ForensicsManager replay ──────────────────────────────────

@pytest.mark.anyio
async def test_scenario_replay_reconstructs_timeline(forensics: ForensicsManager):
    """Record an error, create a crash dump, then replay to see the timeline."""
    forensics.record_error(
        ValueError("disk full"),
        trace_id="trc_gauntlet_002",
        context={"operation": "write", "path": "/tmp/test"},
    )
    await forensics.snapshot(
        reason="disk_full",
        error=ValueError("disk full"),
        trace_id="trc_gauntlet_002",
    )

    result = await forensics.replay("trc_gauntlet_002")
    assert result is not None
    assert result["crash_dump"]["reason"] == "disk_full"
    assert result["crash_dump"]["error"]["type"] == "ValueError"


# ── Scenario 3: ForensicsManager learn ───────────────────────────────────

@pytest.mark.anyio
async def test_scenario_learn_returns_lesson(forensics: ForensicsManager):
    """After a crash, learn() extracts a lesson string."""
    await forensics.snapshot(
        reason="provider_unavailable",
        error=ConnectionError("ollama refused connection"),
        trace_id="trc_gauntlet_003",
    )

    lesson = await forensics.learn("trc_gauntlet_003", entity_name="SOPHIA")
    assert lesson is not None
    assert "ConnectionError" in lesson
    assert "ollama" in lesson


# ── Scenario 4: ObservabilityEngine error recording ──────────────────────

@pytest.mark.anyio
async def test_scenario_engine_records_and_logs_errors(forensics: ForensicsManager):
    """ObservabilityEngine.record_error() stores error + logs event."""
    engine = ObservabilityEngine(
        enable_dataset_collection=False,
        forensics_manager=forensics,
    )
    engine.record_error(
        RuntimeError("model inference failed"),
        trace_id="trc_gauntlet_004",
        context={"model": "qwen3", "prompt_tokens": 512},
    )

    assert len(forensics.recent_errors) == 1
    assert forensics.recent_errors[0]["error_type"] == "RuntimeError"

    recent = engine.recent_events(10)
    error_events = [e for e in recent if e["event"] == EventType.ERROR]
    assert len(error_events) >= 1
    assert error_events[0]["data"]["error_type"] == "RuntimeError"


# ── Scenario 5: Crash dump with engine state ─────────────────────────────

@pytest.mark.anyio
async def test_scenario_crash_dump_includes_engine_state(forensics: ForensicsManager):
    """Crash dump includes _collect_engine_state() and _collect_system_info()."""
    engine = ObservabilityEngine(
        enable_dataset_collection=False,
        forensics_manager=forensics,
    )
    engine.log_event(EventType.QUERY_RECEIVED, "trc_gauntlet_005", {"query": "hello"})

    path = await engine.snapshot(
        reason="test_with_state",
        error=Exception("engine state test"),
        trace_id="trc_gauntlet_005",
    )
    assert path.exists()

    with open(str(path)) as f:
        dump = json.load(f)

    assert "engine_state" in dump
    assert "system_info" in dump
    assert dump["engine_state"]["has_crashed"] is True
    assert dump["system_info"]["timestamp"] > 0
    assert "anyio_backend" in dump["system_info"]


# ── Scenario 6: JsonFormatter produces valid structured JSON ──────────────

def test_scenario_json_formatter_output():
    """JsonFormatter produces valid JSON with all required fields."""
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="omega.test",
        level=logging.WARNING,
        pathname="test.py",
        lineno=42,
        msg="provider %s failed",
        args=("ollama",),
        exc_info=None,
    )
    record.trace_id = "trc_gauntlet_006"
    output = formatter.format(record)
    parsed = json.loads(output)
    assert parsed["level"] == "WARNING"
    assert parsed["logger"] == "omega.test"
    assert parsed["message"] == "provider ollama failed"
    assert parsed["trace_id"] == "trc_gauntlet_006"
    assert "timestamp" in parsed


# ── Scenario 7: setup_json_logging applies to logger tree ────────────────

def test_scenario_json_logging_setup():
    """setup_json_logging replaces handler on target logger."""
    logger = logging.getLogger("omega.gauntlet")
    logger.info("plain text before setup")

    setup_json_logging("omega.gauntlet")

    with patch.object(logger, "handlers", logger.handlers):
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0].formatter, JsonFormatter)


# ── Scenario 8: Snapshot survives ForensicsManager reconstruction ────────

@pytest.mark.anyio
async def test_scenario_forensics_persistence_across_instances(temp_crash_dir: Path):
    """Crash dump written by one ForensicsManager is readable by another."""
    fm1 = ForensicsManager(crash_dir=temp_crash_dir)
    await fm1.snapshot(
        reason="cross_instance",
        error=OSError("file locked"),
        trace_id="trc_gauntlet_008",
    )

    fm2 = ForensicsManager(crash_dir=temp_crash_dir)
    dump = fm2.check_recovery()
    assert dump is not None
    assert dump["reason"] == "cross_instance"
    assert dump["error"]["type"] == "OSError"


# ── Scenario 9: Error ring buffer is bounded ─────────────────────────────

def test_scenario_error_ring_buffer_bounded(temp_crash_dir: Path):
    """ForensicsManager error ring buffer never exceeds maxlen."""
    fm = ForensicsManager(crash_dir=temp_crash_dir, max_recent_errors=5)
    for i in range(20):
        fm.record_error(
            ValueError(f"error {i}"),
            trace_id=f"trc_{i}",
        )
    assert len(fm.recent_errors) == 5
    assert fm.recent_errors[0]["error_message"] == "error 15"


# ── Scenario 10: Replay returns None for unknown trace_id ────────────────

@pytest.mark.anyio
async def test_scenario_replay_unknown_trace(forensics: ForensicsManager):
    """Replay with a trace_id that doesn't exist returns None."""
    result = await forensics.replay("trc_nonexistent")
    assert result is None
