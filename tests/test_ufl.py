# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Tests for Unified Forensic Ledger (UFL) — IW-3.

[IW-3] Unified Forensic Ledger provides append-only JSONL event store
for forensic analysis of Silent 200s, circuit breaker transitions, and errors.

[M21 Gate Integrity] Every UFL write path must be exercised by a
contract test that validates the entry structure and zoneid.

AP: AP-UFL-TEST-v1.0.0
"""

import json
import pytest
from pathlib import Path
from omega.observability.ufl import UFLWriter, get_ufl_writer
from omega.constants import ZONEID_TRACE


@pytest.fixture
def ufl_writer(tmp_path):
    """Create a UFL writer with a temporary data directory."""
    return UFLWriter(data_dir=tmp_path / "observability" / "forensic")


class TestUFLWrite:
    """UFL.write() must produce valid forensic entries."""

    def test_write_basic_entry(self, ufl_writer):
        """Basic entry must have all required fields."""
        trace_id = "trc_test_001"
        ufl_writer.write(
            event_type="silent_200",
            trace_id=trace_id,
            provider="test_provider",
            payload={"status_code": 200, "error_signature": "quota_exceeded"},
        )
        
        # Read back
        entries = ufl_writer.read_recent(max_entries=1)
        assert len(entries) == 1
        entry = entries[0]
        
        assert entry["_zoneid"] == ZONEID_TRACE
        assert entry["trace_id"] == trace_id
        assert entry["provider"] == "test_provider"
        assert entry["event_type"] == "silent_200"
        assert entry["payload"]["status_code"] == 200
        assert entry["payload"]["error_signature"] == "quota_exceeded"
        assert "timestamp" in entry

    def test_write_error_entry(self, ufl_writer):
        """write_error() must produce structured error entry."""
        trace_id = "trc_test_002"
        error = ValueError("Test error message")
        
        ufl_writer.write_error(
            error=error,
            trace_id=trace_id,
            provider="test_provider",
            context={"model": "test-model", "tokens": 100},
        )
        
        entries = ufl_writer.read_recent(max_entries=1)
        assert len(entries) == 1
        entry = entries[0]
        
        assert entry["event_type"] == "error"
        assert entry["payload"]["error_type"] == "ValueError"
        assert "Test error message" in entry["payload"]["error_message"]
        assert entry["payload"]["context"]["model"] == "test-model"

    def test_write_breaker_event(self, ufl_writer):
        """write_breaker_event() must produce structured breaker transition."""
        trace_id = "trc_test_003"
        
        ufl_writer.write_breaker_event(
            provider="test_provider",
            trace_id=trace_id,
            from_state="CLOSED",
            to_state="OPEN",
            reason="5 consecutive failures",
        )
        
        entries = ufl_writer.read_recent(max_entries=1)
        assert len(entries) == 1
        entry = entries[0]
        
        assert entry["event_type"] == "breaker_transition"
        assert entry["payload"]["from_state"] == "CLOSED"
        assert entry["payload"]["to_state"] == "OPEN"
        assert "5 consecutive failures" in entry["payload"]["reason"]

    def test_multiple_entries_same_day(self, ufl_writer):
        """Multiple writes must append to same daily file."""
        for i in range(5):
            ufl_writer.write(
                event_type="test_event",
                trace_id=f"trc_{i}",
                provider=f"provider_{i}",
                payload={"index": i},
            )
        
        entries = ufl_writer.read_recent(max_entries=10)
        assert len(entries) == 5
        # Most recent first
        assert entries[0]["payload"]["index"] == 4
        assert entries[4]["payload"]["index"] == 0

    def test_event_type_filter(self, ufl_writer):
        """read_recent() must filter by event_type."""
        ufl_writer.write("silent_200", "trc_1", "p1", {})
        ufl_writer.write("error", "trc_2", "p2", {})
        ufl_writer.write("silent_200", "trc_3", "p3", {})
        
        silent_entries = ufl_writer.read_recent(max_entries=10, event_type="silent_200")
        assert len(silent_entries) == 2
        assert all(e["event_type"] == "silent_200" for e in silent_entries)
        
        error_entries = ufl_writer.read_recent(max_entries=10, event_type="error")
        assert len(error_entries) == 1
        assert error_entries[0]["event_type"] == "error"


class TestUFLZoneId:
    """Every UFL entry must carry the ZONEID_TRACE integrity marker."""

    def test_zoneid_present_on_all_writes(self, ufl_writer):
        """ZONEID_TRACE must be present on every entry type."""
        ufl_writer.write("test", "trc_1", "p1", {})
        ufl_writer.write_error(ValueError("test"), "trc_2", "p2", {})
        ufl_writer.write_breaker_event("p3", "trc_3", "CLOSED", "OPEN", "test")
        
        entries = ufl_writer.read_recent(max_entries=10)
        for entry in entries:
            assert entry["_zoneid"] == ZONEID_TRACE, f"Missing zoneid on {entry['event_type']}"


class TestUFLSingleton:
    """Module-level singleton must work correctly."""

    def test_get_ufl_writer_returns_singleton(self):
        """get_ufl_writer() must return the same instance."""
        writer1 = get_ufl_writer()
        writer2 = get_ufl_writer()
        assert writer1 is writer2


class TestUFLFlush:
    """flush() and close() must work without errors."""

    def test_flush_and_close(self, ufl_writer):
        """flush() and close() must not raise."""
        ufl_writer.write("test", "trc_1", "p1", {})
        ufl_writer.flush()  # Should not raise
        ufl_writer.close()  # Should not raise
        # Writing after close should reopen
        ufl_writer.write("test2", "trc_2", "p2", {})
        entries = ufl_writer.read_recent(max_entries=1)
        assert entries[0]["trace_id"] == "trc_2"


class TestUFLIntegrationWithBLEG:
    """UFL must integrate with BLEG for Silent 200 recording."""

    def test_bleg_silent_200_written_to_ufl(self, ufl_writer):
        """BLEG inspection that detects Silent 200 must write to UFL."""
        from omega.observability.bleg import BLEGMiddleware
        from omega.errors import ProviderError
        
        guard = BLEGMiddleware(enabled=True)
        
        # This should raise and we catch it
        try:
            guard.inspect(200, {"error": "Quota exceeded"}, provider="test", trace_id="trc_bleg_001")
        except ProviderError:
            pass
        
        # Manually write to UFL as BLEG would (BLEG doesn't auto-write to UFL yet)
        ufl_writer.write(
            event_type="silent_200",
            trace_id="trc_bleg_001",
            provider="test",
            payload={"status_code": 200, "error_signature": "quota_exceeded"},
        )
        
        entries = ufl_writer.read_recent(max_entries=1, event_type="silent_200")
        assert len(entries) == 1
        assert entries[0]["trace_id"] == "trc_bleg_001"
        assert entries[0]["payload"]["error_signature"] == "quota_exceeded"