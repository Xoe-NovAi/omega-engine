# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Control plane — four production control planes.

HERMETIC BY CONSTRUCTION. Every test redirects the module-level store paths at
`tmp_path` and, where time matters, monkeypatches `control_plane._now`. No test
reads or writes the live `data/coordination/control/` store, and none of them
sleep. The live queue cannot leak into a verdict, and a slow test suite cannot
become a flaky one.

WHAT IS ACTUALLY PROVEN HERE (and what is not)
----------------------------------------------
Proven: kill idempotency, approval fail-closed on unknown id AND on timeout,
throttle registration, status output shape, append-only preservation.

NOT proven: that any destructive operation consults `check()`. Nothing does
yet. See CONTROL_PLANE_20261003.md — the approval plane is a correct gate with
no doors wired to it in v1. A test asserting "the system is protected" would be
a lie, so there is not one.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from mcp_servers.omega_hub import control_plane as CP  # noqa: E402


@pytest.fixture
def store(tmp_path, monkeypatch):
    """Redirect every control-plane path at a tmp dir. Hermetic isolation."""
    cdir = tmp_path / "control"
    approvals = cdir / "approvals"
    monkeypatch.setattr(CP, "CONTROL_DIR", cdir)
    monkeypatch.setattr(CP, "CONTROL_STATE_PATH", cdir / "control.json")
    monkeypatch.setattr(CP, "KILL_LOG_PATH", cdir / "kill_log.jsonl")
    monkeypatch.setattr(CP, "DECISION_LOG_PATH", cdir / "decisions.jsonl")
    monkeypatch.setattr(CP, "APPROVALS_DIR", approvals)
    return cdir


@pytest.fixture
def clock(monkeypatch):
    """Controllable wall clock. Returns a setter; no test ever sleeps."""
    state = {"t": 1_000_000.0}
    monkeypatch.setattr(CP, "_now", lambda: state["t"])

    def _advance(seconds: float) -> None:
        state["t"] += seconds

    _advance.seconds = lambda s: _advance(s)  # type: ignore[attr-defined]
    return _advance


# ═══════════════════════════════════════════════════════════════════════════
# PLANE 1 — KILL: IDEMPOTENCY
# ═══════════════════════════════════════════════════════════════════════════


def test_kill_first_call_records(store):
    r = CP.kill(session_id="ses_runaway", entity="doom_guy", reason="spin loop")
    assert r["result"] == "killed", r
    assert r["already_killed"] is False
    assert CP.is_killed("ses_runaway") is True


def test_kill_is_idempotent_second_call_is_noop(store):
    """Killing an already-dead session is a NO-OP, NOT an error."""
    first = CP.kill(session_id="ses_runaway", reason="spin loop")
    second = CP.kill(session_id="ses_runaway", reason="different reason entirely")

    assert second["result"] == "noop", f"expected noop, got {second}"
    assert second["already_killed"] is True
    assert second["idempotent"] is True
    # Crucially: no exception, no error key.
    assert "error" not in second

    # STATE is unchanged — the original reason and timestamp survive.
    assert second["kill"]["reason"] == "spin loop", (
        f"second kill mutated the record: {second['kill']}"
    )
    assert second["kill"] == first["kill"]


def test_kill_n_times_stays_one_record(store):
    for _ in range(5):
        CP.kill(session_id="ses_x", reason="r")
    ids = CP.killed_session_ids()
    assert ids == {"ses_x"}
    assert len(CP.active_kills()) == 1


def test_kill_log_records_both_the_kill_and_the_noop(store):
    """M28: attempts are auditable. State is idempotent; the log is not blind."""
    CP.kill(session_id="ses_x", reason="r")
    CP.kill(session_id="ses_x", reason="r")
    events = [
        json.loads(line)["event"]
        for line in CP.KILL_LOG_PATH.read_text().strip().splitlines()
    ]
    assert events == ["kill", "kill_noop"], events


def test_kill_log_is_append_only_never_truncated(store):
    """Two kills, two kill events. The log grows; it is never rewritten."""
    CP.kill(session_id="ses_a")
    CP.kill(session_id="ses_b")
    body = CP.KILL_LOG_PATH.read_text()
    assert body.count('"event": "kill"') == 2, "kill log was rewritten, not appended"
    assert body.endswith("\n"), "last line is partial — write did not complete"


def test_is_killed_is_false_for_unknown_session(store):
    assert CP.is_killed("ses_never_seen") is False


def test_kill_empty_session_id_refuses(store):
    with pytest.raises(CP.ControlPlaneError) as exc:
        CP.kill(session_id="")
    assert exc.value.code == "missing_session_id"


def test_release_lifts_the_kill_but_keeps_the_record(store):
    """A kill with no release is a one-way door; this is the door back."""
    CP.kill(session_id="ses_x", reason="mistake")
    r = CP.release(session_id="ses_x", reason="operator error")
    assert r["result"] == "released"
    assert CP.is_killed("ses_x") is False
    # M28: the kill record is marked, not deleted.
    assert "ses_x" in json.loads(CP.CONTROL_STATE_PATH.read_text())["killed"]


# ═══════════════════════════════════════════════════════════════════════════
# PLANE 3 — APPROVAL: FAIL-CLOSED
# ═══════════════════════════════════════════════════════════════════════════


def test_approve_unknown_operation_id_denies(store):
    """The core fail-closed guarantee: nobody opened it, so nobody cleared it."""
    r = CP.approve(operation_id="op_does_not_exist", approved=True)
    assert r["decision"] == CP.DENY, f"unknown id must DENY, got {r}"
    assert r["approved"] is False
    assert r["fail_closed"] is True
    assert r["reason"] == "unknown_operation_id"


def test_check_unknown_operation_id_denies(store):
    gate = CP.check(operation_id="op_does_not_exist")
    assert gate["decision"] == CP.DENY, gate
    assert gate["approved"] is False


def test_check_missing_operation_id_denies(store):
    for bad in (None, "", "   "):
        assert CP.check(operation_id=bad)["decision"] == CP.DENY, bad


def test_requested_but_unanswered_check_denies(store):
    """Pending is NOT approved. Absence of a decision is a denial."""
    req = CP.request_approval(operation="rm -rf /", entity="doom_guy")
    gate = CP.check(operation_id=req["operation_id"])
    assert gate["decision"] == CP.DENY, gate
    assert gate["reason"] == "awaiting_human_decision"


def test_approval_timeout_denies_fail_closed(store, clock):
    """THE FAIL-CLOSED PROOF.

    A request nobody answered, past its timeout, resolves DENY — even though the
    caller explicitly passed approved=True. Silence is not consent.
    """
    req = CP.request_approval(operation="drop_database", timeout_s=900)
    assert req["timeout_s"] == 900
    op = req["operation_id"]

    assert CP.check(operation_id=op)["decision"] == CP.DENY  # pending, in window

    clock(901)  # one second past expiry

    gate = CP.check(operation_id=op)
    assert gate["decision"] == CP.DENY, f"expired request must DENY: {gate}"
    assert gate["reason"] == "approval_timeout", gate
    assert gate["fail_closed"] is True

    # And the decisive call: an explicit approve=True CANNOT revive it.
    r = CP.approve(operation_id=op, approved=True)
    assert r["decision"] == CP.DENY, f"timeout must deny even approved=True: {r}"
    assert r["fail_closed"] is True
    assert r["reason"] == "approval_timeout"


def test_timeout_denial_is_written_to_the_audit_log(store, clock):
    req = CP.request_approval(operation="drop_database", timeout_s=10)
    clock(11)
    CP.approve(operation_id=req["operation_id"], approved=True)
    log = CP.DECISION_LOG_PATH.read_text()
    assert '"reason": "approval_timeout"' in log, log
    assert '"fail_closed": true' in log


def test_approve_within_window_allows(store, clock):
    req = CP.request_approval(operation="deploy", timeout_s=900)
    clock(10)
    r = CP.approve(operation_id=req["operation_id"], approved=True, decided_by="kali")
    assert r["decision"] == CP.ALLOW, r
    assert r["approved"] is True
    assert CP.check(operation_id=req["operation_id"])["decision"] == CP.ALLOW


def test_human_denial_is_a_denial(store):
    req = CP.request_approval(operation="deploy")
    r = CP.approve(operation_id=req["operation_id"], approved=False, reason="not now")
    assert r["decision"] == CP.DENY
    assert r["reason"] == "human_denied"


def test_decision_is_terminal_and_idempotent(store):
    req = CP.request_approval(operation="deploy")
    op = req["operation_id"]
    CP.approve(operation_id=op, approved=True, decided_by="kali")
    second = CP.approve(operation_id=op, approved=False, decided_by="attacker")
    assert second["decision"] == CP.ALLOW, "a second decision overwrote the first"
    assert second["idempotent"] is True
    assert CP.check(operation_id=op)["decision"] == CP.ALLOW


def test_non_positive_timeout_is_refused(store):
    with pytest.raises(CP.ControlPlaneError) as exc:
        CP.request_approval(operation="deploy", timeout_s=0)
    assert exc.value.code == "invalid_timeout"


def test_timeout_precedence_and_default(store, monkeypatch):
    """argument > env > constant(900)."""
    assert CP.approval_timeout_s() == CP.DEFAULT_APPROVAL_TIMEOUT_S
    monkeypatch.setenv(CP.ENV_APPROVAL_TIMEOUT, "60")
    assert CP.approval_timeout_s() == 60
    req = CP.request_approval(operation="deploy")
    assert req["timeout_s"] == 60
    assert req["timeout_source"].startswith("env:")


def test_malformed_env_timeout_falls_back_to_safe_default(store, monkeypatch):
    """A broken override must not open an unbounded window, nor crash the gate."""
    monkeypatch.setenv(CP.ENV_APPROVAL_TIMEOUT, "not-a-number")
    assert CP.approval_timeout_s() == CP.DEFAULT_APPROVAL_TIMEOUT_S
    cfg = CP.config()
    assert cfg["config_anomaly"], "a malformed override must be reported, not hidden"


def test_config_states_the_timeout_and_that_timeout_denies(store):
    cfg = CP.config()
    assert cfg["approval_timeout_s"] == 900
    assert cfg["on_timeout"] == CP.DENY
    assert cfg["approval_timeout_env_var"] == CP.ENV_APPROVAL_TIMEOUT


# ═══════════════════════════════════════════════════════════════════════════
# PLANE 4 — THROTTLE
# ═══════════════════════════════════════════════════════════════════════════


def test_throttle_registration(store):
    r = CP.set_throttle(entity="doom_guy", max_tokens_per_hour=100_000,
                        max_tool_calls_per_hour=500)
    assert r["result"] == "throttled"
    listed = CP.list_throttles()
    assert len(listed) == 1
    assert listed[0]["entity"] == "doom_guy"
    assert listed[0]["max_tokens_per_hour"] == 100_000
    assert listed[0]["max_tool_calls_per_hour"] == 500
    assert listed[0]["window_s"] == 3600


def test_throttle_is_labelled_advisory_not_enforced(store):
    """An advisory plane that reads as enforcing is worse than no plane."""
    CP.set_throttle(entity="doom_guy", max_tokens_per_hour=1000)
    assert CP.ENFORCEMENT["throttle"]["enforced"] is False
    assert CP.ENFORCEMENT["throttle"]["status"] == "ADVISORY"
    assert CP.check_throttle(entity="doom_guy", tokens_used=10)["enforcement"] == "ADVISORY"


def test_throttle_check_reports_exceedance(store):
    CP.set_throttle(entity="doom_guy", max_tokens_per_hour=1000, max_tool_calls_per_hour=50)
    under = CP.check_throttle(entity="doom_guy", tokens_used=10, tool_calls_used=5)
    assert under["exceeded"] is False
    over = CP.check_throttle(entity="doom_guy", tokens_used=1001, tool_calls_used=51)
    assert over["exceeded"] is True
    assert set(over["exceeded_dimensions"]) == {"tokens", "tool_calls"}


def test_throttle_update_merges_and_preserves_the_other_limit(store):
    CP.set_throttle(entity="e", max_tokens_per_hour=1000, max_tool_calls_per_hour=50)
    CP.set_throttle(entity="e", max_tokens_per_hour=2000)
    limits = CP.list_throttles()[0]
    assert limits["max_tokens_per_hour"] == 2000
    assert limits["max_tool_calls_per_hour"] == 50, "update clobbered the other limit"


def test_throttle_requires_at_least_one_limit(store):
    with pytest.raises(CP.ControlPlaneError) as exc:
        CP.set_throttle(entity="e")
    assert exc.value.code == "missing_limits"


def test_clear_throttle_is_idempotent(store):
    CP.set_throttle(entity="e", max_tokens_per_hour=10)
    assert CP.clear_throttle(entity="e")["result"] == "cleared"
    assert CP.clear_throttle(entity="e")["result"] == "noop"


# ═══════════════════════════════════════════════════════════════════════════
# PLANE 2 — ESCALATION
# ═══════════════════════════════════════════════════════════════════════════


def _packet(tmp_path: Path, packet_id: str = "ho_abc") -> Path:
    pending = tmp_path / "handoff" / "pending"
    pending.mkdir(parents=True, exist_ok=True)
    p = pending / f"{packet_id}.json"
    p.write_text(json.dumps({
        "packet_id": packet_id,
        "task": "resolve the blocker",
        "target_agent_id": "opencode/lilith",
        "target_entity": "lilith",
        "priority": 0,
    }))
    return p


def test_escalate_retargets_the_real_packet(tmp_path, store):
    p = _packet(tmp_path)
    r = CP.escalate(packet_id="ho_abc", to_entity="makali",
                    pending_dir=tmp_path / "handoff" / "pending")
    assert r["result"] == "escalated"
    assert r["to_agent_id"] == "opencode/makali"
    updated = json.loads(p.read_text())
    assert updated["target_entity"] == "makali", "store was not mutated"
    assert updated["priority"] == 2, "an escalated blocker is not normal traffic"
    assert updated["escalation_history"][0]["from_agent_id"] == "opencode/lilith"


def test_escalate_unknown_packet_refuses_rather_than_inventing(tmp_path, store):
    with pytest.raises(CP.ControlPlaneError) as exc:
        CP.escalate(packet_id="ho_ghost", to_entity="makali",
                    pending_dir=tmp_path / "handoff" / "pending")
    assert exc.value.code == "unknown_packet"


def test_escalate_requires_a_destination(tmp_path, store):
    _packet(tmp_path)
    with pytest.raises(CP.ControlPlaneError) as exc:
        CP.escalate(packet_id="ho_abc", to_entity="",
                    pending_dir=tmp_path / "handoff" / "pending")
    assert exc.value.code == "missing_to_entity"


def test_escalate_is_idempotent_for_the_same_target(tmp_path, store):
    pending = tmp_path / "handoff" / "pending"
    _packet(tmp_path)
    CP.escalate(packet_id="ho_abc", to_entity="makali", pending_dir=pending)
    again = CP.escalate(packet_id="ho_abc", to_entity="makali", pending_dir=pending)
    assert again["result"] == "noop"
    assert again["already_escalated"] is True


# ═══════════════════════════════════════════════════════════════════════════
# STATUS SHAPE + RADAR
# ═══════════════════════════════════════════════════════════════════════════


def test_status_shape_is_total_even_when_empty(store):
    """An absent key and a zero count are different claims. Only one is true."""
    s = CP.status()
    for key in ("schema", "generated_at", "killed_count", "killed",
                "pending_approvals", "pending_approval_ids", "throttle_count",
                "throttles", "config", "enforcement", "paths"):
        assert key in s, f"status is missing {key!r}"
    assert s["killed_count"] == 0
    assert s["pending_approvals"] == 0
    assert s["throttle_count"] == 0


def test_status_counts_live_controls(store):
    CP.kill(session_id="ses_a")
    CP.set_throttle(entity="doom_guy", max_tokens_per_hour=1000)
    CP.request_approval(operation="deploy")
    s = CP.status()
    assert s["killed_count"] == 1
    assert s["throttle_count"] == 1
    assert s["pending_approvals"] == 1
    assert len(s["pending_approval_ids"]) == 1


def test_status_reports_enforcement_honestly(store):
    """The matrix must not claim enforcement it does not have."""
    e = CP.status()["enforcement"]
    assert e["escalate"]["enforced"] is True
    assert e["throttle"]["enforced"] is False
    assert e["approve"]["enforced"] is False
    assert e["kill"]["status"] == "PARTIAL"


def test_radar_block_shape(store):
    CP.kill(session_id="ses_a")
    CP.request_approval(operation="deploy")
    r = CP.radar_block()
    assert r["control_plane_ok"] is True
    assert r["killed_count"] == 1
    assert r["pending_approvals"] == 1
    assert "escalate" in r["enforced_planes"]
    assert "throttle" not in r["enforced_planes"]


def test_radar_reports_unreadable_store_as_null_not_zero(tmp_path, monkeypatch):
    """M23: an unreadable store is not an all-clear. null, never 0."""
    cdir = tmp_path / "broken"
    cdir.mkdir()
    (cdir / "control.json").write_text("{ this is not json")
    monkeypatch.setattr(CP, "CONTROL_DIR", cdir)
    monkeypatch.setattr(CP, "CONTROL_STATE_PATH", cdir / "control.json")
    monkeypatch.setattr(CP, "KILL_LOG_PATH", cdir / "kill_log.jsonl")
    monkeypatch.setattr(CP, "DECISION_LOG_PATH", cdir / "decisions.jsonl")
    monkeypatch.setattr(CP, "APPROVALS_DIR", cdir / "approvals")

    r = CP.radar_block()
    assert r["control_plane_ok"] is False
    assert r["killed_count"] is None, "a broken store reported zero kills"
    assert r["pending_approvals"] is None


def test_corrupt_state_raises_rather_than_reporting_all_clear(tmp_path, monkeypatch):
    """The same rule for the strict path: refuse, do not guess."""
    cdir = tmp_path / "broken"
    cdir.mkdir()
    (cdir / "control.json").write_text("not json at all")
    monkeypatch.setattr(CP, "CONTROL_DIR", cdir)
    monkeypatch.setattr(CP, "CONTROL_STATE_PATH", cdir / "control.json")
    with pytest.raises(CP.ControlPlaneError) as exc:
        CP.is_killed("ses_a")
    assert exc.value.code == "control_state_corrupt"