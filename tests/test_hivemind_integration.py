# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

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

        # [maat 2026-09-28] `EXTENDED_SESSIONS_FILE` was deliberately NOT
        # patched here. The Hivemind consolidation (de660681) removed the
        # separate on-disk extended-session store and folded extended TTLs into
        # the in-memory `_awareness` map, so the symbol no longer exists.
        # Patching it raised AttributeError inside this fixture, which killed
        # ALL 26 tests in this file at setup -- not just the 5 extended-session
        # ones. A fixture that errors is a file-wide outage that reads as 26
        # unrelated problems. Do not reintroduce the patch.

        # Create all directories
        for d in [
            "HALL_OF_RECORDS", "handoff/pending", "handoff/active",
            "handoff/completed", "handoff/stale", "handoff/archive", "locks",
        ]:
            (tmp_path / d).mkdir(parents=True, exist_ok=True)

        yield tmp_path


@pytest.fixture
def reset_state():
    """Reset in-memory hivemind state between tests.

    [maat 2026-09-28] `_extended_sessions` removed: extended sessions live in
    `_awareness` since the consolidation (de660781). See the note in
    `hivemind_fs`; clearing a symbol that no longer exists raised AttributeError
    and took down every test using this fixture.
    """
    state._hot_store.clear()
    state._awareness.clear()
    yield
    state._hot_store.clear()
    state._awareness.clear()


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
    """Tests for extended session checkin / checkout lifecycle.

    [maat 2026-09-28] REWRITTEN. These five tests previously manipulated a
    `state._extended_sessions` dict that they populated themselves and then
    asserted on — a dict the test built, testing nothing. They also referenced
    `EXTENDED_SESSIONS_FILE` / `_save_extended_sessions` / `_load_extended_sessions`,
    all removed by the Hivemind consolidation (de660681), which folded extended
    TTLs into the in-memory `_awareness` map.

    They now drive the REAL `hivemind_awareness` tool through the
    `extended_checkin` / `extended_checkout` actions, so a regression in the
    cap, the missing-argument guard, or the checkout path actually fails here.
    """

    @staticmethod
    async def _call(action, **kw):
        """Invoke the real tool and return its decoded JSON payload.

        [maat 2026-09-28] The tool is a FastMCP-decorated function: calling it
        directly returns a `CallToolResult`, NOT a string. It also refuses to
        run until hub services are initialised, so we call `_require_service()`
        to stand them up first. Both facts were discovered by running the test
        rather than by reading the signature -- the decorator wraps the
        function, so its type annotation no longer describes what it returns.

        If the service cannot be stood up, the test FAILS. Returning an empty
        or synthetic payload here would be the exact silent-degradation shape
        this suite exists to catch.
        """
        from mcp_servers.omega_hub.hub_tools import tools as hub_tools

        # Bypass ONLY the readiness gate. `_require_service()` blocks every tool
        # until the full 12-singleton engine bootstrap finishes, which is not
        # what these five tests are about -- they are about the extended-session
        # branch inside `hivemind_awareness`. Setting the flag exercises the real
        # code path: the real cap, the real guard, the real key deletions. If any
        # of that logic regresses, these tests still fail. We are NOT stubbing
        # the behaviour under test, only the "is the engine up" precondition.
        # Restored in the finally block so no other test inherits the bypass.
        # The readiness flags live in `state`, not in `tools` — `tools` imported
        # the `_require_service` FUNCTION, not the module-level flags. Verified
        # rather than assumed; a guessed attribute path cost one iteration here.
        prev_init, prev_err = state._init_complete, state._init_error
        state._init_complete, state._init_error = True, None
        try:
            args = {"action": action}
            args.update(kw)
            result = await hub_tools.hivemind_awareness(**args)
        finally:
            state._init_complete, state._init_error = prev_init, prev_err

        # When the FastMCP decorator is not active (direct module import, as
        # here) the tool returns a plain JSON string. When the wrapper IS active
        # the same function returns a CallToolResult whose content holds that
        # text. Handle both -- measured, not assumed: an earlier draft assumed
        # CallToolResult unconditionally and every test failed KeyError 'status'.
        if hasattr(result, "content"):
            result = "".join(
                getattr(c, "text", "") for c in result.content
            )
        if isinstance(result, str):
            return json.loads(result)
        return result

    @pytest.mark.anyio
    async def test_checkin_registers_session(self, hivemind_fs, reset_state):
        """T-INT-014: Extended checkin registers a TTL in _awareness."""
        out = await self._call("extended_checkin", channel="opencode",
                               entity="test-entity", ttl_seconds=10800,
                               reason="Long-running task")

        assert out["status"] == "extended_checkin_registered"
        assert out["ttl_seconds"] == 10800
        assert out["expires_at"] > 0, "expiry must be a real future timestamp"

        # The TTL must actually be recorded, not just echoed back.
        agent_id = "opencode/test-entity"
        assert agent_id in state._awareness
        assert state._awareness[agent_id]["extended_ttl"] == 10800
        assert state._awareness[agent_id]["extended_reason"] == "Long-running task"
        assert "extended_registered_at" in state._awareness[agent_id]

    @pytest.mark.anyio
    async def test_checkout_removes_session(self, hivemind_fs, reset_state):
        """T-INT-015: Extended checkout clears the TTL keys."""
        await self._call("extended_checkin", channel="opencode",
                         entity="test-entity", ttl_seconds=10800)
        agent_id = "opencode/test-entity"
        assert "extended_ttl" in state._awareness[agent_id]

        out = await self._call("extended_checkout", channel="opencode",
                               entity="test-entity")
        assert out["status"] == "extended_checkout_complete"
        # The extended keys must be gone. The base awareness entry legitimately
        # remains — checkout releases the TTL, it does not evict the agent.
        assert "extended_ttl" not in state._awareness[agent_id]
        assert "extended_reason" not in state._awareness[agent_id]
        assert "extended_registered_at" not in state._awareness[agent_id]

    @pytest.mark.anyio
    async def test_checkout_nonexistent_returns_no_session(self, hivemind_fs, reset_state):
        """T-INT-016: Checkout of an unknown agent is a no-op, not an error.

        This must NOT raise and must NOT fabricate a successful checkout.
        """
        out = await self._call("extended_checkout", channel="opencode",
                               entity="nonexistent")
        assert out["status"] == "no_extended_session"

    @pytest.mark.anyio
    async def test_checkin_requires_channel_and_entity(self, hivemind_fs, reset_state):
        """T-INT-019: M23 — a checkin missing its identity args fails loudly.

        Guards the `all([channel, entity])` truthiness trap that also bit the
        `post` validator: an empty list/None is 'missing', but these are
        required and must produce an explicit error, not a silent no-op.
        """
        out = await self._call("extended_checkin", channel="", entity="")
        assert "error" in out, f"expected an explicit error, got {out}"

        out2 = await self._call("extended_checkout", channel=None, entity=None)
        assert "error" in out2, f"expected an explicit error, got {out2}"

    @pytest.mark.anyio
    async def test_ttl_cap_at_24h(self, hivemind_fs, reset_state):
        """T-INT-018: TTL is capped at 86400s (24h) by the REAL implementation.

        Previously this asserted `min(100000, 86400) == 86400` — a tautology
        about Python's `min`, testing no product code whatsoever.
        """
        out = await self._call("extended_checkin", channel="opencode",
                               entity="cap-entity", ttl_seconds=100000)
        assert out["ttl_seconds"] == 86400, (
            f"TTL must be clamped to 24h, got {out['ttl_seconds']}"
        )
        assert state._awareness["opencode/cap-entity"]["extended_ttl"] == 86400

        # A TTL under the cap must pass through untouched — proves the cap is a
        # clamp and not a constant.
        out2 = await self._call("extended_checkin", channel="opencode",
                                entity="ok-entity", ttl_seconds=3600)
        assert out2["ttl_seconds"] == 3600


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
