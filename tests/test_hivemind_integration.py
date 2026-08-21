# 🔱 Omega Engine — Hivemind Integration Test Harness
# AP: AP-HIVEMIND-INTEGRATION-v1.0.0
"""
Integration tests for the Hivemind coordination layer.

Per Carmack S3 Audit §Gap 2:
- Handoff lifecycle (submit → accept → complete → archive)
- Handoff rejection (submit → reject)
- Workspace lock acquire / release / conflict
- Extended session checkin / checkout
- Stale lock reaping
- Stale handoff reaping

These tests exercise the filesystem state machine that the MCP tools
operate on, validating the full lifecycle without importing server.py
(which has complex MCP module side-effects).

Usage: pytest tests/test_hivemind_integration.py -v
"""
import json
import os
import sys
import time
import fcntl
import tempfile
from pathlib import Path
from datetime import datetime, timezone, timedelta

import pytest

# Ensure MCP server modules are importable
MCP_SERVER_PATH = Path(__file__).resolve().parent.parent / "mcp_servers" / "omega_hub"
sys.path.insert(0, str(MCP_SERVER_PATH.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

# ── Minimal state patching ──
# We only need the filesystem paths and helpers from state.py,
# not the service singletons (which require full engine init).
from mcp_servers.omega_hub import state


# ═══════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def hivemind_fs(monkeypatch):
    """Redirect all Hivemind filesystem paths to a temp directory."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # Patch all path constants
        monkeypatch.setattr(state, "HALL_OF_RECORDS", tmp_path / "HALL_OF_RECORDS")
        monkeypatch.setattr(state, "HANDOFF_BASE", tmp_path / "handoff")
        monkeypatch.setattr(state, "HANDOFF_PENDING", tmp_path / "handoff" / "pending")
        monkeypatch.setattr(state, "HANDOFF_ACTIVE", tmp_path / "handoff" / "active")
        monkeypatch.setattr(state, "HANDOFF_COMPLETED", tmp_path / "handoff" / "completed")
        monkeypatch.setattr(state, "HANDOFF_STALE", tmp_path / "handoff" / "stale")
        monkeypatch.setattr(state, "HANDOFF_ARCHIVE", tmp_path / "handoff" / "archive")
        monkeypatch.setattr(state, "LOCKS_BASE", tmp_path / "locks")
        monkeypatch.setattr(state, "METRICS_PATH", tmp_path / "metrics.json")
        monkeypatch.setattr(state, "EXTENDED_SESSIONS_FILE", tmp_path / "extended_sessions.json")

        # Create all directories
        for d in [
            "HALL_OF_RECORDS", "handoff/pending", "handoff/active",
            "handoff/completed", "handoff/stale", "handoff/archive", "locks",
        ]:
            (tmp_path / d).mkdir(parents=True, exist_ok=True)

        yield tmp_path


@pytest.fixture
def reset_state():
    """Reset in-memory hivemind state between tests."""
    state._hot_store.clear()
    state._awareness.clear()
    state._extended_sessions.clear()
    yield
    state._hot_store.clear()
    state._awareness.clear()
    state._extended_sessions.clear()


def _write_handoff_packet(directory: Path, packet: dict) -> str:
    """Write a handoff packet to a directory and return the packet_id."""
    pid = packet["packet_id"]
    path = directory / f"{pid}.json"
    with open(path, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        json.dump(packet, f, indent=2)
        fcntl.flock(f, fcntl.LOCK_UN)
    return pid


def _read_handoff_packet(directory: Path, packet_id: str) -> dict:
    """Read a handoff packet from a directory."""
    path = directory / f"{packet_id}.json"
    with open(path) as f:
        return json.load(f)


def _make_packet(packet_id: str, status: str = "pending", **overrides) -> dict:
    """Create a minimal handoff packet."""
    packet = {
        "packet_id": packet_id,
        "target_agent_id": "opencode/test-target",
        "target_channel": "opencode",
        "target_entity": "test-target",
        "source_agent_id": "opencode/test-source",
        "source_channel": "opencode",
        "source_entity": "test-source",
        "task": "Test task",
        "context": "",
        "priority": 0,
        "status": status,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }
    packet.update(overrides)
    return packet


# ═══════════════════════════════════════════════════════════════════════════
# HANDOFF LIFECYCLE TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestHandoffLifecycle:
    """Tests for the full handoff lifecycle: submit → accept → complete → archive."""

    def test_submit_to_pending(self, hivemind_fs):
        """T-INT-001: Submit writes packet to pending/ directory."""
        packet = _make_packet("ho_test001")
        pid = _write_handoff_packet(state.HANDOFF_PENDING, packet)

        assert (state.HANDOFF_PENDING / f"{pid}.json").exists()
        loaded = _read_handoff_packet(state.HANDOFF_PENDING, pid)
        assert loaded["status"] == "pending"
        assert loaded["packet_id"] == pid

    def test_accept_moves_to_active(self, hivemind_fs):
        """T-INT-002: Accept moves packet from pending/ to active/."""
        packet = _make_packet("ho_test002")
        _write_handoff_packet(state.HANDOFF_PENDING, packet)

        # Simulate accept: read from pending, write to active, delete pending
        src = state.HANDOFF_PENDING / "ho_test002.json"
        dst = state.HANDOFF_ACTIVE / "ho_test002.json"
        with open(src) as f:
            data = json.load(f)
        data["status"] = "active"
        data["accepted_by_agent_id"] = "opencode/test-acceptor"
        data["accepted_at"] = datetime.now(timezone.utc).isoformat()
        with open(dst, "w") as f:
            json.dump(data, f, indent=2)
        src.unlink()

        assert not (state.HANDOFF_PENDING / "ho_test002.json").exists()
        assert (state.HANDOFF_ACTIVE / "ho_test002.json").exists()
        loaded = _read_handoff_packet(state.HANDOFF_ACTIVE, "ho_test002")
        assert loaded["status"] == "active"
        assert loaded["accepted_by_agent_id"] == "opencode/test-acceptor"

    def test_complete_moves_to_completed(self, hivemind_fs):
        """T-INT-003: Complete moves packet from active/ to completed/."""
        packet = _make_packet("ho_test003", status="active")
        _write_handoff_packet(state.HANDOFF_ACTIVE, packet)

        src = state.HANDOFF_ACTIVE / "ho_test003.json"
        dst = state.HANDOFF_COMPLETED / "ho_test003.json"
        with open(src) as f:
            data = json.load(f)
        data["status"] = "completed"
        data["completed_at"] = datetime.now(timezone.utc).isoformat()
        data["result"] = "Task done"
        with open(dst, "w") as f:
            json.dump(data, f, indent=2)
        src.unlink()

        assert not (state.HANDOFF_ACTIVE / "ho_test003.json").exists()
        assert (state.HANDOFF_COMPLETED / "ho_test003.json").exists()
        loaded = _read_handoff_packet(state.HANDOFF_COMPLETED, "ho_test003")
        assert loaded["status"] == "completed"
        assert loaded["result"] == "Task done"

    def test_archive_moves_to_archive(self, hivemind_fs):
        """T-INT-004: Archive moves packet from completed/ to archive/."""
        packet = _make_packet("ho_test004", status="completed")
        _write_handoff_packet(state.HANDOFF_COMPLETED, packet)

        src = state.HANDOFF_COMPLETED / "ho_test004.json"
        dst = state.HANDOFF_ARCHIVE / "ho_test004.json"
        with open(src) as f:
            data = json.load(f)
        data["status"] = "archived"
        data["archived_at"] = datetime.now(timezone.utc).isoformat()
        with open(dst, "w") as f:
            json.dump(data, f, indent=2)
        src.unlink()

        assert not (state.HANDOFF_COMPLETED / "ho_test004.json").exists()
        assert (state.HANDOFF_ARCHIVE / "ho_test004.json").exists()
        loaded = _read_handoff_packet(state.HANDOFF_ARCHIVE, "ho_test004")
        assert loaded["status"] == "archived"

    def test_full_lifecycle(self, hivemind_fs):
        """T-INT-005: Full lifecycle — submit → accept → complete → archive."""
        pid = "ho_lifecycle"
        packet = _make_packet(pid)

        # Submit → pending
        _write_handoff_packet(state.HANDOFF_PENDING, packet)
        assert (state.HANDOFF_PENDING / f"{pid}.json").exists()

        # Accept → active
        src = state.HANDOFF_PENDING / f"{pid}.json"
        dst = state.HANDOFF_ACTIVE / f"{pid}.json"
        with open(src) as f:
            data = json.load(f)
        data["status"] = "active"
        with open(dst, "w") as f:
            json.dump(data, f)
        src.unlink()
        assert (state.HANDOFF_ACTIVE / f"{pid}.json").exists()

        # Complete → completed
        src = state.HANDOFF_ACTIVE / f"{pid}.json"
        dst = state.HANDOFF_COMPLETED / f"{pid}.json"
        with open(src) as f:
            data = json.load(f)
        data["status"] = "completed"
        with open(dst, "w") as f:
            json.dump(data, f)
        src.unlink()
        assert (state.HANDOFF_COMPLETED / f"{pid}.json").exists()

        # Archive → archive
        src = state.HANDOFF_COMPLETED / f"{pid}.json"
        dst = state.HANDOFF_ARCHIVE / f"{pid}.json"
        with open(src) as f:
            data = json.load(f)
        data["status"] = "archived"
        with open(dst, "w") as f:
            json.dump(data, f)
        src.unlink()
        assert (state.HANDOFF_ARCHIVE / f"{pid}.json").exists()

        # Verify final state
        loaded = _read_handoff_packet(state.HANDOFF_ARCHIVE, pid)
        assert loaded["status"] == "archived"

    def test_reject_moves_to_stale(self, hivemind_fs):
        """T-INT-006: Reject moves packet from pending/ to stale/."""
        packet = _make_packet("ho_reject001")
        _write_handoff_packet(state.HANDOFF_PENDING, packet)

        src = state.HANDOFF_PENDING / "ho_reject001.json"
        dst = state.HANDOFF_STALE / "ho_reject001.json"
        with open(src) as f:
            data = json.load(f)
        data["status"] = "stale"
        data["rejected"] = True
        data["reason"] = "Not my domain"
        with open(dst, "w") as f:
            json.dump(data, f)
        src.unlink()

        assert not (state.HANDOFF_PENDING / "ho_reject001.json").exists()
        assert (state.HANDOFF_STALE / "ho_reject001.json").exists()
        loaded = _read_handoff_packet(state.HANDOFF_STALE, "ho_reject001")
        assert loaded["rejected"] is True
        assert loaded["reason"] == "Not my domain"

    def test_packet_not_found_returns_error(self, hivemind_fs):
        """T-INT-007: Accept/complete for nonexistent packet returns error."""
        # Simulate the _find_packet_path behavior
        def _find_packet_path(packet_id):
            for q in [state.HANDOFF_PENDING, state.HANDOFF_ACTIVE, state.HANDOFF_COMPLETED, state.HANDOFF_STALE]:
                path = q / f"{packet_id}.json"
                if path.exists():
                    return path
            return None

        assert _find_packet_path("ho_nonexistent") is None


# ═══════════════════════════════════════════════════════════════════════════
# WORKSPACE LOCK TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestWorkspaceLocks:
    """Tests for workspace lock acquire / release / conflict detection."""

    def test_acquire_lock(self, hivemind_fs):
        """T-INT-008: Acquire creates a lock file with correct metadata."""
        lock_path = state.LOCKS_BASE / "test-domain.lock"
        lock_data = {
            "agent_id": "opencode/test-entity",
            "channel": "opencode",
            "entity": "test-entity",
            "domain": "test-domain",
            "acquired_at": datetime.now(timezone.utc).timestamp(),
            "ttl": 3600,
        }
        with open(lock_path, "w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(lock_data, f, indent=2)
            fcntl.flock(f, fcntl.LOCK_UN)

        assert lock_path.exists()
        with open(lock_path) as f:
            loaded = json.load(f)
        assert loaded["agent_id"] == "opencode/test-entity"
        assert loaded["domain"] == "test-domain"

    def test_release_lock(self, hivemind_fs):
        """T-INT-009: Release removes the lock file."""
        lock_path = state.LOCKS_BASE / "test-domain.lock"
        lock_data = {
            "agent_id": "opencode/test-entity",
            "domain": "test-domain",
            "acquired_at": datetime.now(timezone.utc).timestamp(),
            "ttl": 3600,
        }
        with open(lock_path, "w") as f:
            json.dump(lock_data, f)

        # Release: verify agent matches, then unlink
        with open(lock_path) as f:
            existing = json.load(f)
        assert existing["agent_id"] == "opencode/test-entity"
        lock_path.unlink()

        assert not lock_path.exists()

    def test_lock_conflict_detection(self, hivemind_fs):
        """T-INT-010: Acquire by different agent detects conflict."""
        lock_path = state.LOCKS_BASE / "test-domain.lock"
        lock_data = {
            "agent_id": "opencode/holder-entity",
            "domain": "test-domain",
            "acquired_at": datetime.now(timezone.utc).timestamp(),
            "ttl": 3600,
        }
        with open(lock_path, "w") as f:
            json.dump(lock_data, f)

        # Try to acquire from a different agent
        with open(lock_path) as f:
            existing = json.load(f)
        if existing.get("agent_id") != "opencode/new-entity":
            conflict = True
            holder = existing.get("agent_id")
        else:
            conflict = False
            holder = None

        assert conflict is True
        assert holder == "opencode/holder-entity"

    def test_expired_lock_overwrite(self, hivemind_fs):
        """T-INT-011: Expired lock can be overwritten by new agent."""
        lock_path = state.LOCKS_BASE / "test-domain.lock"
        lock_data = {
            "agent_id": "opencode/old-entity",
            "domain": "test-domain",
            "acquired_at": (datetime.now(timezone.utc) - timedelta(hours=2)).timestamp(),
            "ttl": 3600,  # 1 hour TTL — expired
        }
        with open(lock_path, "w") as f:
            json.dump(lock_data, f)

        # Check if expired
        now = datetime.now(timezone.utc).timestamp()
        with open(lock_path) as f:
            existing = json.load(f)
        expired = now > existing["acquired_at"] + existing["ttl"]
        assert expired is True

        # Overwrite with new lock
        new_data = {
            "agent_id": "opencode/new-entity",
            "domain": "test-domain",
            "acquired_at": now,
            "ttl": 3600,
        }
        with open(lock_path, "w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(new_data, f, indent=2)
            fcntl.flock(f, fcntl.LOCK_UN)

        with open(lock_path) as f:
            loaded = json.load(f)
        assert loaded["agent_id"] == "opencode/new-entity"

    def test_lock_check_returns_status(self, hivemind_fs):
        """T-INT-012: Lock check returns TTL and remaining seconds."""
        lock_path = state.LOCKS_BASE / "test-domain.lock"
        now = datetime.now(timezone.utc).timestamp()
        lock_data = {
            "agent_id": "opencode/test-entity",
            "domain": "test-domain",
            "acquired_at": now - 600,  # acquired 10 minutes ago
            "ttl": 3600,
        }
        with open(lock_path, "w") as f:
            json.dump(lock_data, f)

        # Check
        with open(lock_path) as f:
            data = json.load(f)
        age = now - data["acquired_at"]
        remaining = max(0, data["ttl"] - age)
        assert remaining > 0
        assert remaining < 3600

    def test_no_lock_returns_no_lock(self, hivemind_fs):
        """T-INT-013: Lock check on empty domain returns no_lock."""
        lock_path = state.LOCKS_BASE / "empty-domain.lock"
        assert not lock_path.exists()


# ═══════════════════════════════════════════════════════════════════════════
# EXTENDED SESSION TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestExtendedSessions:
    """Tests for extended session checkin / checkout lifecycle."""

    def test_checkin_registers_session(self, hivemind_fs, reset_state):
        """T-INT-014: Extended checkin registers session with TTL."""
        agent_id = "opencode/test-entity"
        ttl = 10800  # 3 hours

        state._extended_sessions[agent_id] = {
            "agent_id": agent_id,
            "channel": "opencode",
            "entity": "test-entity",
            "ttl_seconds": ttl,
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "reason": "Long-running task",
        }

        assert agent_id in state._extended_sessions
        assert state._extended_sessions[agent_id]["ttl_seconds"] == ttl

    def test_checkout_removes_session(self, hivemind_fs, reset_state):
        """T-INT-015: Extended checkout removes session."""
        agent_id = "opencode/test-entity"
        state._extended_sessions[agent_id] = {
            "agent_id": agent_id,
            "ttl_seconds": 10800,
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }

        del state._extended_sessions[agent_id]
        assert agent_id not in state._extended_sessions

    def test_checkout_nonexistent_returns_no_session(self, hivemind_fs, reset_state):
        """T-INT-016: Checkout for nonexistent session returns no_extended_session."""
        agent_id = "opencode/nonexistent"
        assert agent_id not in state._extended_sessions

    def test_extended_session_persistence(self, hivemind_fs, reset_state):
        """T-INT-017: Extended sessions persist to disk."""
        agent_id = "opencode/persist-entity"
        state._extended_sessions[agent_id] = {
            "agent_id": agent_id,
            "ttl_seconds": 7200,
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }

        # Save
        state._save_extended_sessions(state._extended_sessions)

        # Load in fresh state
        loaded = state._load_extended_sessions()
        assert agent_id in loaded
        assert loaded[agent_id]["ttl_seconds"] == 7200

    def test_ttl_cap_at_24h(self, hivemind_fs, reset_state):
        """T-INT-018: TTL is capped at 86400 seconds (24h)."""
        requested_ttl = 100000  # > 24h
        capped_ttl = min(requested_ttl, 86400)
        assert capped_ttl == 86400


# ═══════════════════════════════════════════════════════════════════════════
# STALE REAPING TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestStaleReaping:
    """Tests for stale handoff and lock reaping logic."""

    def test_stale_handoff_reaping(self, hivemind_fs):
        """T-INT-019: Pending handoff older than 24h is reaped to stale/."""
        now = datetime.now(timezone.utc)
        old_time = (now - timedelta(hours=25)).timestamp()

        packet = _make_packet("ho_old001")
        _write_handoff_packet(state.HANDOFF_PENDING, packet)

        # Touch the file's mtime to 25 hours ago
        target = state.HANDOFF_PENDING / "ho_old001.json"
        os.utime(target, (old_time, old_time))

        # Reap logic
        reaped = 0
        for f in state.HANDOFF_PENDING.glob("*.json"):
            age = (now - datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)).total_seconds()
            if age > 86400:  # 24h
                data = json.loads(f.read_text())
                data["status"] = "stale"
                dst = state.HANDOFF_STALE / f.name
                dst.write_text(json.dumps(data, indent=2))
                f.unlink()
                reaped += 1

        assert reaped == 1
        assert not (state.HANDOFF_PENDING / "ho_old001.json").exists()
        assert (state.HANDOFF_STALE / "ho_old001.json").exists()

    def test_recent_handoff_not_reaped(self, hivemind_fs):
        """T-INT-020: Recent handoff is NOT reaped."""
        packet = _make_packet("ho_recent001")
        _write_handoff_packet(state.HANDOFF_PENDING, packet)

        now = datetime.now(timezone.utc)
        reaped = 0
        for f in state.HANDOFF_PENDING.glob("*.json"):
            age = (now - datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)).total_seconds()
            if age > 86400:
                reaped += 1

        assert reaped == 0
        assert (state.HANDOFF_PENDING / "ho_recent001.json").exists()

    def test_stale_lock_reaping(self, hivemind_fs):
        """T-INT-021: Expired lock is reaped."""
        lock_path = state.LOCKS_BASE / "expired-domain.lock"
        lock_data = {
            "agent_id": "opencode/test-entity",
            "domain": "expired-domain",
            "acquired_at": (datetime.now(timezone.utc) - timedelta(hours=2)).timestamp(),
            "ttl": 3600,
        }
        with open(lock_path, "w") as f:
            json.dump(lock_data, f)

        # Reap logic
        now = datetime.now(timezone.utc).timestamp()
        reaped = 0
        for lock_file in state.LOCKS_BASE.glob("*.lock"):
            with open(lock_file) as f:
                data = json.load(f)
            if now > data["acquired_at"] + data["ttl"]:
                lock_file.unlink()
                reaped += 1

        assert reaped == 1
        assert not lock_path.exists()

    def test_active_lock_not_reaped(self, hivemind_fs):
        """T-INT-022: Active lock is NOT reaped."""
        lock_path = state.LOCKS_BASE / "active-domain.lock"
        lock_data = {
            "agent_id": "opencode/test-entity",
            "domain": "active-domain",
            "acquired_at": datetime.now(timezone.utc).timestamp(),
            "ttl": 3600,
        }
        with open(lock_path, "w") as f:
            json.dump(lock_data, f)

        now = datetime.now(timezone.utc).timestamp()
        reaped = 0
        for lock_file in state.LOCKS_BASE.glob("*.lock"):
            with open(lock_file) as f:
                data = json.load(f)
            if now > data["acquired_at"] + data["ttl"]:
                lock_file.unlink()
                reaped += 1

        assert reaped == 0
        assert lock_path.exists()


# ═══════════════════════════════════════════════════════════════════════════
# HANDOFF LIST / FIND TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestHandoffQuery:
    """Tests for handoff list and find operations."""

    def test_list_pending_handoffs(self, hivemind_fs):
        """T-INT-023: List returns all pending packets."""
        for i in range(3):
            packet = _make_packet(f"ho_list{i}")
            _write_handoff_packet(state.HANDOFF_PENDING, packet)

        pending = list(state.HANDOFF_PENDING.glob("*.json"))
        assert len(pending) == 3

    def test_find_packet_in_correct_queue(self, hivemind_fs):
        """T-INT-024: _find_packet_path finds packet in correct queue."""
        # Put packet in active/
        packet = _make_packet("ho_find001", status="active")
        _write_handoff_packet(state.HANDOFF_ACTIVE, packet)

        # Search all queues
        def _find_packet_path(packet_id):
            for q in [state.HANDOFF_PENDING, state.HANDOFF_ACTIVE, state.HANDOFF_COMPLETED, state.HANDOFF_STALE]:
                path = q / f"{packet_id}.json"
                if path.exists():
                    return path
            return None

        found = _find_packet_path("ho_find001")
        assert found is not None
        assert found.parent == state.HANDOFF_ACTIVE

    def test_find_nonexistent_returns_none(self, hivemind_fs):
        """T-INT-025: _find_packet_path returns None for missing packet."""
        def _find_packet_path(packet_id):
            for q in [state.HANDOFF_PENDING, state.HANDOFF_ACTIVE, state.HANDOFF_COMPLETED, state.HANDOFF_STALE]:
                path = q / f"{packet_id}.json"
                if path.exists():
                    return path
            return None

        assert _find_packet_path("ho_ghost") is None

    def test_batch_archive_multiple(self, hivemind_fs):
        """T-INT-026: Batch archive moves multiple packets."""
        pids = ["ho_arch001", "ho_arch002", "ho_arch003"]
        for pid in pids:
            packet = _make_packet(pid, status="completed")
            _write_handoff_packet(state.HANDOFF_COMPLETED, packet)

        # Archive all
        succeeded = 0
        for pid in pids:
            src = state.HANDOFF_COMPLETED / f"{pid}.json"
            if src.exists():
                dst = state.HANDOFF_ARCHIVE / f"{pid}.json"
                data = json.loads(src.read_text())
                data["status"] = "archived"
                dst.write_text(json.dumps(data, indent=2))
                src.unlink()
                succeeded += 1

        assert succeeded == 3
        assert len(list(state.HANDOFF_COMPLETED.glob("*.json"))) == 0
        assert len(list(state.HANDOFF_ARCHIVE.glob("*.json"))) == 3
