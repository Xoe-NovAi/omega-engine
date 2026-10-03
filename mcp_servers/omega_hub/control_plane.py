# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Omega Control Plane — the four production control planes.

WHY THIS EXISTS
---------------
The frontier finding (arXiv 2605.20173, 2026): a production agent system needs
four control planes, and the deployment ORDER is load-bearing — kill switch,
escalation, approval, throttling. Same paper: "Build the dashboard before the
agent. The trace is the contract."

We had blockers and handoffs but no formal control plane. Concretely: a runaway
subagent could not be halted; destructive operations had no human gate; token and
tool spend was unbounded; a blocker had no automatic escalation path.

DEPLOYMENT ORDER IS NOT ARBITRARY
---------------------------------
  1. kill      — you can always stop the bleeding. Nothing else matters if you
                 cannot halt a runaway.
  2. escalate  — once you can stop things, the next question is who unblocks
                 them. A blocker that cannot reach a human is a dead session.
  3. approve   — once routing exists, put a human in the path for the
                 destructive subset. Gating an unroutable queue gates nothing.
  4. throttle  — last, because it is the only plane that degrades throughput
                 rather than stopping it, and it is the one most likely to be
                 wired wrong (a too-tight limit silently starves real work).

THE FAIL-CLOSED PRINCIPLE (M23)
-------------------------------
Every approval path DENIES by default. Not "denies when it errors" — denies
when it is *missing*, *unknown*, *unanswered*, or *expired*. The dangerous
failure mode for a human gate is silence: nobody answered, so the operation
proceeded. That is the inverse of safety. `check()` returns DENY for an
operation_id nobody ever opened, because "unknown" and "safe" are not the same
claim and only one of them is provable here.

ENFORCEMENT STATUS — READ THIS BEFORE TRUSTING A PLANE
-----------------------------------------------------
`ENFORCEMENT` below is the honest per-plane status. Two planes are real
enforcement, one is a real gate whose call sites are not yet wired, and one is
advisory in v1. The distinction is load-bearing: an advisory plane that is
believed to be enforcing is worse than no plane, because it produces confidence
without a control.

APPEND-ONLY (M28)
-----------------
`kill_log.jsonl` and `decisions.jsonl` are append-only. They are opened with
mode "a", fsynced per record, and never rewritten or truncated. State files
(`control.json`, `approvals/*.json`) are atomically replaced via tmp + fsync +
os.replace, so a reader never observes a partial file. History is never
destroyed to make the current state smaller.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .federation_envelope import write_atomic

# ═══════════════════════════════════════════════════════════════════════════
# PATHS + SCHEMA
# ═══════════════════════════════════════════════════════════════════════════

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

CONTROL_DIR = PROJECT_ROOT / "data" / "coordination" / "control"
CONTROL_STATE_PATH = CONTROL_DIR / "control.json"
KILL_LOG_PATH = CONTROL_DIR / "kill_log.jsonl"
DECISION_LOG_PATH = CONTROL_DIR / "decisions.jsonl"
APPROVALS_DIR = CONTROL_DIR / "approvals"

CONTROL_SCHEMA = "control-plane/v1"

# ═══════════════════════════════════════════════════════════════════════════
# APPROVAL TIMEOUT — N, AND WHERE IT IS CONFIGURED
# ═══════════════════════════════════════════════════════════════════════════
#
# N = 900 seconds (15 minutes). Configured in three places, in precedence order:
#
#   1. per-request `timeout_s` argument on request_approval()  (highest)
#   2. environment variable OMEGA_APPROVAL_TIMEOUT_S           (medium)
#   3. DEFAULT_APPROVAL_TIMEOUT_S = 900                        (lowest, floor)
#
# UNANSWERED PAST N IS DENIED. There is no "extend", no "pending forever", and
# no default-allow path. An expired request is resolved to DENY and that
# resolution is written to decisions.jsonl so the denial is auditable rather
# than merely inferred.

DEFAULT_APPROVAL_TIMEOUT_S = 900
ENV_APPROVAL_TIMEOUT = "OMEGA_APPROVAL_TIMEOUT_S"

# Decisions
ALLOW = "ALLOW"
DENY = "DENY"

# Approval lifecycle states
PENDING = "pending"
APPROVED = "approved"
DENIED = "denied"


class ControlPlaneError(RuntimeError):
    """A control-plane operation could not be completed.

    Raised for genuine failures (corrupt state, unwritable store). NOT raised
    for a denial — a denial is a successful, honest ANSWER, and it is returned
    as data. Collapsing "denied" into "error" is how a human gate turns into a
    crash that gets caught and ignored.
    """

    def __init__(self, code: str, message: str, **detail: Any) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.detail = detail

    def as_dict(self) -> Dict[str, Any]:
        return {"error": {"code": self.code, "message": self.message, **self.detail}}


# ═══════════════════════════════════════════════════════════════════════════
# ENFORCEMENT MATRIX — the honest boundary
# ═══════════════════════════════════════════════════════════════════════════

ENFORCEMENT: Dict[str, Dict[str, Any]] = {
    "kill": {
        "status": "PARTIAL",
        "enforced": True,
        "scope": "hub-side advisory points + harvester radar + durable record",
        "not_enforced": (
            "Does NOT interrupt an in-flight model turn inside an external "
            "OpenCode process. The dispatcher that would host that check lives "
            "under src/omega/ (out of this module's M2 firewall), and no API "
            "exists to reach a running session from here. A kill here is a "
            "refusal-to-continue plus a loud, durable marker — not SIGKILL."
        ),
        "predicate": "control_plane.is_killed(session_id)",
    },
    "escalate": {
        "status": "ENFORCED",
        "enforced": True,
        "scope": "real mutation of the handoff store (data/handoff/pending)",
        "not_enforced": (
            "Enforcement stops at the store. A higher-authority agent that does "
            "not drain its inbox still will not act — that is inbox liveness, "
            "not an escalation defect."
        ),
        "predicate": "n/a — observable directly in the handoff queue",
    },
    "approve": {
        "status": "GATE_ENFORCED__CALLSITES_ADVISORY",
        "enforced": False,
        "scope": "the decision function is total and fail-closed",
        "not_enforced": (
            "The gate DENIES correctly for every input, but no destructive "
            "operation calls check() yet. In v1 this is a correct gate with no "
            "doors wired to it — treat it as a primitive, not a control."
        ),
        "predicate": "control_plane.check(operation_id)",
    },
    "throttle": {
        "status": "ADVISORY",
        "enforced": False,
        "scope": "limit registration + an advisory comparison",
        "not_enforced": (
            "Nothing counts tokens or tool calls on the dispatch path yet, so "
            "check_throttle() compares a caller-supplied number against a "
            "stored limit. It reports; it does not stop."
        ),
        "predicate": "control_plane.check_throttle(entity, tokens, tool_calls)",
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# PRIMITIVES
# ═══════════════════════════════════════════════════════════════════════════


def _now() -> float:
    """Wall clock, injectable so timeout behaviour is testable without sleeping.

    Tests monkeypatch this. Production never does.
    """
    return time.time()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs() -> None:
    CONTROL_DIR.mkdir(parents=True, exist_ok=True)
    APPROVALS_DIR.mkdir(parents=True, exist_ok=True)


def approval_timeout_s() -> int:
    """Effective default approval timeout in seconds. Never <= 0.

    A malformed or non-positive override falls back to
    DEFAULT_APPROVAL_TIMEOUT_S and records why, rather than raising into a
    security gate or silently adopting an unbounded window.
    """
    raw = os.environ.get(ENV_APPROVAL_TIMEOUT)
    if raw is None or not raw.strip():
        return DEFAULT_APPROVAL_TIMEOUT_S
    try:
        value = int(raw.strip())
    except ValueError:
        return DEFAULT_APPROVAL_TIMEOUT_S
    if value <= 0:
        return DEFAULT_APPROVAL_TIMEOUT_S
    return value


def config() -> Dict[str, Any]:
    """Effective configuration plus the provenance of every value."""
    raw = os.environ.get(ENV_APPROVAL_TIMEOUT)
    anomaly: Optional[str] = None
    if raw is not None and raw.strip():
        try:
            if int(raw.strip()) <= 0:
                anomaly = f"{ENV_APPROVAL_TIMEOUT}={raw!r} is non-positive"
        except ValueError:
            anomaly = f"{ENV_APPROVAL_TIMEOUT}={raw!r} is not an integer"

    return {
        "approval_timeout_s": approval_timeout_s(),
        "approval_timeout_source": (
            f"env:{ENV_APPROVAL_TIMEOUT}"
            if raw and raw.strip() and not anomaly
            else "constant:DEFAULT_APPROVAL_TIMEOUT_S"
        ),
        "approval_timeout_env_var": ENV_APPROVAL_TIMEOUT,
        "approval_timeout_default_constant": DEFAULT_APPROVAL_TIMEOUT_S,
        "on_timeout": DENY,
        "config_anomaly": anomaly,
        "paths": {
            "control_dir": str(CONTROL_DIR),
            "state": str(CONTROL_STATE_PATH),
            "kill_log": str(KILL_LOG_PATH),
            "decision_log": str(DECISION_LOG_PATH),
            "approvals": str(APPROVALS_DIR),
        },
    }


def _append_jsonl(path: Path, record: Dict[str, Any]) -> None:
    """Append one JSON record. M28: append-only — open 'a', never truncate."""
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, sort_keys=True) + "\n"
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(line)
        fh.flush()
        os.fsync(fh.fileno())


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    """Read a JSON object, or None when absent/unreadable/corrupt."""
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, ValueError):
        return None
    if not raw.strip():
        return None
    try:
        data = json.loads(raw)
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


def _empty_state() -> Dict[str, Any]:
    return {"schema": CONTROL_SCHEMA, "killed": {}, "throttles": {}}


def _load_state() -> Dict[str, Any]:
    """Load control.json, tolerating absence but NOT corruption.

    A corrupt state file means we do not know which sessions are killed or
    which limits are in force. Returning an empty state would silently report
    "nothing is killed, no throttles exist" — a confident false all-clear. It
    raises instead so the caller reports the failure (M23).
    """
    if not CONTROL_STATE_PATH.exists():
        return _empty_state()
    data = _read_json(CONTROL_STATE_PATH)
    if data is None:
        raise ControlPlaneError(
            "control_state_corrupt",
            f"{CONTROL_STATE_PATH} exists but is not readable JSON. Refusing to "
            "report an empty control state — an unreadable store is not an "
            "all-clear. Do not delete the file to 'fix' it (M28: append-only "
            "preservation); restore it from backup or archive it aside and "
            "reconcile against kill_log.jsonl.",
            path=str(CONTROL_STATE_PATH),
        )
    data.setdefault("schema", CONTROL_SCHEMA)
    data.setdefault("killed", {})
    data.setdefault("throttles", {})
    return data


def _save_state(state: Dict[str, Any]) -> None:
    """Atomically persist control.json (tmp + fsync + os.replace)."""
    ensure_dirs()
    state["schema"] = CONTROL_SCHEMA
    state["updated_at"] = _now_iso()
    write_atomic(CONTROL_STATE_PATH, json.dumps(state, indent=2, sort_keys=True))


# ═══════════════════════════════════════════════════════════════════════════
# PLANE 1 — KILL SWITCH
# ═══════════════════════════════════════════════════════════════════════════


def kill(
    session_id: str,
    entity: Optional[str] = None,
    reason: Optional[str] = None,
    requested_by: Optional[str] = None,
) -> Dict[str, Any]:
    """Halt a runaway session. IDEMPOTENT.

    Killing an already-dead session is a NO-OP, not an error: the operator
    pressed the button twice, or a retry crossed the original. Both are normal
    in a fleet where several watchers watch the same runaway.

    Idempotency means the STATE does not change. The second call still appends
    a `kill_noop` line to kill_log.jsonl, because an operator pressing the
    button is evidence worth preserving (M28) — but it does not re-write the
    kill record, does not reset the timestamp, and does not change the reason.
    """
    if not session_id or not str(session_id).strip():
        raise ControlPlaneError(
            "missing_session_id",
            "kill requires a non-empty session_id. Refusing to kill '*'.",
        )
    session_id = str(session_id).strip()
    ensure_dirs()
    state = _load_state()
    killed = state.setdefault("killed", {})

    existing = killed.get(session_id)
    if existing is not None:
        _append_jsonl(
            KILL_LOG_PATH,
            {
                "ts": _now_iso(),
                "event": "kill_noop",
                "session_id": session_id,
                "requested_by": requested_by,
                "note": "already killed; state unchanged",
            },
        )
        return {
            "result": "noop",
            "already_killed": True,
            "idempotent": True,
            "session_id": session_id,
            "kill": existing,
            "note": (
                "Session was already killed. No state change. This is the "
                "correct answer, not an error."
            ),
        }

    record = {
        "session_id": session_id,
        "entity": entity,
        "reason": reason,
        "requested_by": requested_by,
        "killed_at": _now_iso(),
        "enforcement": ENFORCEMENT["kill"]["status"],
        "scope_note": ENFORCEMENT["kill"]["not_enforced"],
    }
    killed[session_id] = record
    _save_state(state)
    _append_jsonl(
        KILL_LOG_PATH,
        {
            "ts": _now_iso(),
            "event": "kill",
            "session_id": session_id,
            "entity": entity,
            "reason": reason,
            "requested_by": requested_by,
        },
    )
    return {
        "result": "killed",
        "already_killed": False,
        "idempotent": True,
        "session_id": session_id,
        "kill": record,
        "enforcement": ENFORCEMENT["kill"]["status"],
        "note": ENFORCEMENT["kill"]["not_enforced"],
    }


def release(
    session_id: str,
    entity: Optional[str] = None,
    reason: Optional[str] = None,
    released_by: Optional[str] = None,
) -> Dict[str, Any]:
    """Lift a kill. Idempotent — releasing a non-killed session is a no-op.

    NOT part of the four-plane frontier spec. Included because a kill with no
    release is a one-way door, and a one-way door wired into a fleet is a
    mistake waiting to become an outage. The kill record itself is never
    deleted — it is marked released, and kill_log.jsonl keeps the original.
    """
    if not session_id or not str(session_id).strip():
        raise ControlPlaneError("missing_session_id", "release requires session_id")
    session_id = str(session_id).strip()
    ensure_dirs()
    state = _load_state()
    killed = state.setdefault("killed", {})

    existing = killed.get(session_id)
    if existing is None:
        _append_jsonl(
            KILL_LOG_PATH,
            {"ts": _now_iso(), "event": "release_noop", "session_id": session_id,
             "released_by": released_by, "note": "not killed; state unchanged"},
        )
        return {
            "result": "noop",
            "already_released": True,
            "idempotent": True,
            "session_id": session_id,
            "note": "Session was not killed. No state change.",
        }

    existing["released_at"] = _now_iso()
    existing["released_by"] = released_by
    existing["release_reason"] = reason
    existing["active"] = False
    _save_state(state)
    _append_jsonl(
        KILL_LOG_PATH,
        {"ts": _now_iso(), "event": "release", "session_id": session_id,
         "entity": entity, "reason": reason, "released_by": released_by},
    )
    return {
        "result": "released",
        "already_released": False,
        "idempotent": True,
        "session_id": session_id,
        "kill": existing,
    }


def is_killed(session_id: str) -> bool:
    """The enforcement predicate. True only for an ACTIVE (unreleased) kill.

    This is the call every hub-side advisory point makes. It is a pure
    filesystem read — cheap enough to call in a loop, and it fails TOWARD
    safety: if the store is unreadable it raises rather than returning False.
    A predicate that returns False when it cannot tell is a predicate that
    silently lets a runaway through.
    """
    state = _load_state()
    record = state.get("killed", {}).get(session_id)
    return bool(record) and record.get("active", True) is not False


def active_kills() -> List[Dict[str, Any]]:
    state = _load_state()
    return [r for r in state.get("killed", {}).values() if r.get("active", True) is not False]


def killed_session_ids() -> set:
    """Set of ACTIVE killed session ids — used by the harvester radar."""
    return {r["session_id"] for r in active_kills() if r.get("session_id")}


# ═══════════════════════════════════════════════════════════════════════════
# PLANE 2 — ESCALATION
# ═══════════════════════════════════════════════════════════════════════════


def _handoff_dirs(pending_dir: Optional[Path] = None) -> Dict[str, Path]:
    """Resolve the handoff queues. Lazy so this module imports standalone."""
    if pending_dir is not None:
        root = Path(pending_dir).parent
        return {
            "pending": Path(pending_dir),
            "active": root / "active",
            "completed": root / "completed",
            "stale": root / "stale",
            "archive": root / "archive",
        }
    from . import state as _state  # local import: state pulls in omega services

    return {
        "pending": _state.HANDOFF_PENDING,
        "active": _state.HANDOFF_ACTIVE,
        "completed": _state.HANDOFF_COMPLETED,
        "stale": _state.HANDOFF_STALE,
        "archive": _state.HANDOFF_ARCHIVE,
    }


def _find_packet(packet_id: str, dirs: Dict[str, Path]) -> Optional[Path]:
    for name in ("pending", "active", "completed", "stale", "archive"):
        candidate = dirs[name] / f"{packet_id}.json"
        if candidate.exists():
            return candidate
    return None


def escalate(
    packet_id: str,
    to_entity: str,
    to_channel: str = "opencode",
    reason: Optional[str] = None,
    requested_by: Optional[str] = None,
    pending_dir: Optional[Path] = None,
    from_entity: Optional[str] = None,
) -> Dict[str, Any]:
    """Promote a blocker/handoff to a higher authority. Reuses the handoff store.

    An escalation is a REAL mutation: the packet is re-targeted, its priority is
    raised, and the escalation is appended to the packet's own history. It lands
    in `data/handoff/pending/` where the target's `hivemind_handoff(action="inbox")`
    will actually see it. This is the one plane that is fully ENFORCED — you can
    observe the effect without trusting a flag.

    IDEMPOTENT: re-escalating the same packet to the same target records the
    attempt and changes nothing.
    """
    if not packet_id or not str(packet_id).strip():
        raise ControlPlaneError("missing_packet_id", "escalate requires packet_id")
    if not to_entity or not str(to_entity).strip():
        raise ControlPlaneError(
            "missing_to_entity",
            "escalate requires to_entity. An escalation with no destination is a "
            "blocker written into the void — refusing rather than filing it "
            "nowhere.",
        )
    packet_id = str(packet_id).strip()
    to_entity = str(to_entity).strip()

    dirs = _handoff_dirs(pending_dir)
    path = _find_packet(packet_id, dirs)
    if path is None:
        raise ControlPlaneError(
            "unknown_packet",
            f"No handoff packet {packet_id!r} in any queue. Refusing to invent "
            "one — an escalation of a packet that does not exist is a fabricated "
            "blocker, which is worse than no escalation.",
            packet_id=packet_id,
            searched=[str(d) for d in dirs.values()],
        )

    packet = _read_json(path)
    if packet is None:
        raise ControlPlaneError(
            "unreadable_packet",
            f"Packet {packet_id!r} at {path} is unreadable or not a JSON object.",
            packet_id=packet_id,
            path=str(path),
        )

    previous_target = packet.get("target_agent_id") or packet.get("target_entity")
    new_agent_id = f"{to_channel}/{to_entity}"
    history = packet.setdefault("escalation_history", [])
    already = any(
        h.get("to_agent_id") == new_agent_id for h in history if isinstance(h, dict)
    )

    if already and previous_target == new_agent_id:
        return {
            "result": "noop",
            "already_escalated": True,
            "idempotent": True,
            "packet_id": packet_id,
            "to_agent_id": new_agent_id,
            "note": "Packet is already escalated to this target. No state change.",
        }

    entry = {
        "escalated_at": _now_iso(),
        "from_agent_id": previous_target,
        "to_agent_id": new_agent_id,
        "to_entity": to_entity,
        "to_channel": to_channel,
        "reason": reason,
        "requested_by": requested_by,
        "from_entity": from_entity,
    }
    history.append(entry)

    packet["target_agent_id"] = new_agent_id
    packet["target_entity"] = to_entity
    packet["target_channel"] = to_channel
    packet["priority"] = 2  # critical — an escalated blocker is not normal traffic
    packet["escalated"] = True
    packet["escalated_at"] = entry["escalated_at"]
    if not packet.get("packet_id"):
        packet["packet_id"] = packet_id

    write_atomic(path, json.dumps(packet, indent=2, sort_keys=True))
    _append_jsonl(
        DECISION_LOG_PATH,
        {"ts": entry["escalated_at"], "event": "escalate", "packet_id": packet_id, **entry},
    )

    return {
        "result": "escalated",
        "already_escalated": False,
        "idempotent": True,
        "packet_id": packet_id,
        "from_agent_id": previous_target,
        "to_agent_id": new_agent_id,
        "priority": 2,
        "path": str(path),
        "enforcement": ENFORCEMENT["escalate"]["status"],
        "note": (
            "Packet written to the handoff store. Observable via "
            "hivemind_handoff(action='inbox') at the target."
        ),
    }


# ═══════════════════════════════════════════════════════════════════════════
# PLANE 3 — APPROVAL (human-in-the-loop gate, FAIL-CLOSED)
# ═══════════════════════════════════════════════════════════════════════════


def _approval_path(operation_id: str) -> Path:
    safe = "".join(c for c in operation_id if c.isalnum() or c in "-_")
    if not safe:
        raise ControlPlaneError(
            "invalid_operation_id",
            f"operation_id {operation_id!r} contains no usable characters.",
        )
    return APPROVALS_DIR / f"{safe}.json"


def request_approval(
    operation: str,
    entity: Optional[str] = None,
    detail: str = "",
    timeout_s: Optional[int] = None,
    requested_by: Optional[str] = None,
) -> Dict[str, Any]:
    """OPEN an approval request. `approve()` needs something to resolve.

    timeout_s precedence: explicit argument > OMEGA_APPROVAL_TIMEOUT_S >
    DEFAULT_APPROVAL_TIMEOUT_S (900). The effective value is stamped on the
    request AND echoed in the response, so a reader never has to guess which N
    applied.
    """
    if not operation or not str(operation).strip():
        raise ControlPlaneError("missing_operation", "request_approval requires operation")
    if timeout_s is not None and timeout_s <= 0:
        raise ControlPlaneError(
            "invalid_timeout",
            f"timeout_s must be positive; got {timeout_s}. An unbounded or "
            "non-positive approval window is not a gate.",
        )

    ensure_dirs()
    effective = int(timeout_s) if timeout_s is not None else approval_timeout_s()
    operation_id = f"op_{uuid.uuid4().hex[:16]}"
    created = _now()
    record = {
        "operation_id": operation_id,
        "operation": str(operation).strip(),
        "entity": entity,
        "detail": detail,
        "requested_by": requested_by,
        "requested_at": _now_iso(),
        "requested_at_epoch": created,
        "timeout_s": effective,
        "timeout_source": (
            "argument"
            if timeout_s is not None
            else config()["approval_timeout_source"]
        ),
        "expires_at_epoch": created + effective,
        "expires_at": datetime.fromtimestamp(
            created + effective, tz=timezone.utc
        ).isoformat(),
        "state": PENDING,
        "decided_at": None,
        "decided_by": None,
        "decision_reason": None,
    }
    write_atomic(_approval_path(operation_id), json.dumps(record, indent=2, sort_keys=True))
    _append_jsonl(
        DECISION_LOG_PATH,
        {"ts": record["requested_at"], "event": "approval_requested",
         "operation_id": operation_id, "operation": record["operation"],
         "entity": entity, "timeout_s": effective},
    )
    return {
        "result": "requested",
        "operation_id": operation_id,
        "operation": record["operation"],
        "state": PENDING,
        "timeout_s": effective,
        "timeout_source": record["timeout_source"],
        "expires_at": record["expires_at"],
        "on_timeout": DENY,
        "note": (
            f"Unanswered after {effective}s this request is DENIED. There is no "
            "extend and no default-allow."
        ),
    }


def approve(
    operation_id: str,
    approved: bool,
    decided_by: Optional[str] = None,
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    """Resolve an approval request. FAIL-CLOSED on every unresolved path.

    Resolution table — there is no fifth row:

      unknown operation_id   -> DENY  (fail_closed=True, reason=unknown_operation_id)
      pending, past expires_at-> DENY  (fail_closed=True, reason=approval_timeout)
      pending, approved=True  -> ALLOW (the only path that yields ALLOW)
      pending, approved=False -> DENY  (reason=human_denied)
      already decided         -> the recorded decision, unchanged (idempotent)

    The first two rows are the point. An operation nobody registered and an
    operation nobody answered both produce DENY, so a caller that asks "may I?"
    about something that does not exist is told no.
    """
    if not operation_id or not str(operation_id).strip():
        # No id at all is the most likely form of "unknown" — DENY, not raise.
        return {
            "operation_id": operation_id,
            "decision": DENY,
            "approved": False,
            "fail_closed": True,
            "reason": "unknown_operation_id",
            "detail": "approve called without an operation_id",
        }
    operation_id = str(operation_id).strip()
    ensure_dirs()
    path = _approval_path(operation_id)
    record = _read_json(path)

    if record is None:
        return {
            "operation_id": operation_id,
            "decision": DENY,
            "approved": False,
            "fail_closed": True,
            "reason": "unknown_operation_id",
            "detail": (
                f"No approval request {operation_id!r} exists. Denying: an "
                "operation nobody opened is not one that was cleared."
            ),
        }

    if record.get("state") in (APPROVED, DENIED):
        # Idempotent: a second decision never overwrites the first.
        return {
            "operation_id": operation_id,
            "decision": ALLOW if record["state"] == APPROVED else DENY,
            "approved": record["state"] == APPROVED,
            "state": record["state"],
            "fail_closed": False,
            "reason": "already_decided",
            "idempotent": True,
            "decided_at": record.get("decided_at"),
            "decided_by": record.get("decided_by"),
            "note": "A decision is terminal and was not overwritten.",
        }

    expires_at = record.get("expires_at_epoch")
    now = _now()
    if expires_at is not None and now > float(expires_at):
        return _resolve_terminal(
            record,
            path,
            DENY,
            decided_by=decided_by,
            reason="approval_timeout",
            note=(
                f"Request expired at {record.get('expires_at')} "
                f"(timeout_s={record.get('timeout_s')}); resolved DENY without a "
                "human answer. Fail-closed is the default."
            ),
            fail_closed=True,
        )

    if approved:
        return _resolve_terminal(
            record, path, APPROVED, decided_by=decided_by, reason=reason,
            note="Human approved within the window.", fail_closed=False,
        )
    return _resolve_terminal(
        record, path, DENIED, decided_by=decided_by, reason="human_denied",
        note=reason or "Human denied.", fail_closed=False,
    )


def _resolve_terminal(
    record: Dict[str, Any],
    path: Path,
    state: str,
    decided_by: Optional[str],
    reason: Optional[str],
    note: str,
    fail_closed: bool,
) -> Dict[str, Any]:
    """Write the terminal decision. State file + append-only audit record."""
    decided_at = _now_iso()
    record["state"] = state
    record["decided_at"] = decided_at
    record["decided_by"] = decided_by
    record["decision_reason"] = reason
    record["decision_note"] = note
    record["fail_closed"] = fail_closed
    write_atomic(path, json.dumps(record, indent=2, sort_keys=True))
    _append_jsonl(
        DECISION_LOG_PATH,
        {
            "ts": decided_at,
            "event": "approval_decided",
            "operation_id": record["operation_id"],
            "operation": record.get("operation"),
            "entity": record.get("entity"),
            "decision": state.upper(),
            "reason": reason,
            "decided_by": decided_by,
            "fail_closed": fail_closed,
            "note": note,
        },
    )
    return {
        "operation_id": record["operation_id"],
        # The STORED state is approved/denied; the DECISION handed to a caller
        # is ALLOW/DENY. Conflating the two vocabularies produced "DENIED" as a
        # decision, which no caller branches on correctly.
        "decision": ALLOW if state == APPROVED else DENY,
        "state": state,
        "approved": state == APPROVED,
        "fail_closed": fail_closed,
        "reason": reason,
        "decided_at": decided_at,
        "decided_by": decided_by,
        "note": note,
    }


def check(operation_id: Optional[str]) -> Dict[str, Any]:
    """The gate a destructive operation consults. DENY is the default answer.

    check() and approve() share one rule: no explicit human ALLOW means DENY.
    So a pending request checks DENY (not yet cleared), an expired one checks
    DENY (nobody answered), and an unknown one checks DENY (never opened).
    """
    if not operation_id or not str(operation_id).strip():
        return {"operation_id": operation_id, "decision": DENY, "approved": False,
                "fail_closed": True, "reason": "unknown_operation_id"}
    operation_id = str(operation_id).strip()
    record = _read_json(_approval_path(operation_id))
    if record is None:
        return {
            "operation_id": operation_id, "decision": DENY, "approved": False,
            "fail_closed": True, "reason": "unknown_operation_id",
            "detail": "No such approval request. Absence of approval is denial.",
        }
    if record.get("state") == APPROVED:
        return {"operation_id": operation_id, "decision": ALLOW, "approved": True,
                "fail_closed": False, "reason": "approved",
                "decided_at": record.get("decided_at")}
    if record.get("state") == DENIED:
        return {"operation_id": operation_id, "decision": DENY, "approved": False,
                "fail_closed": bool(record.get("fail_closed")),
                "reason": record.get("decision_reason") or "human_denied"}
    expires_at = record.get("expires_at_epoch")
    if expires_at is not None and _now() > float(expires_at):
        return {"operation_id": operation_id, "decision": DENY, "approved": False,
                "fail_closed": True, "reason": "approval_timeout",
                "expires_at": record.get("expires_at")}
    return {
        "operation_id": operation_id, "decision": DENY, "approved": False,
        "fail_closed": False, "reason": "awaiting_human_decision",
        "expires_at": record.get("expires_at"),
        "note": "Still inside the window, but nobody has approved. DENY until they do.",
    }


def list_approvals(state: Optional[str] = None) -> List[Dict[str, Any]]:
    """All approval requests, optionally filtered by state.

    Expired-but-unresolved requests are reported as PENDING with an
    `expired` flag. They are DENIED on the next check() or approve() call; this
    function reports the stored state rather than performing the transition, so
    that reading the queue is not itself a mutation.
    """
    ensure_dirs()
    out: List[Dict[str, Any]] = []
    now = _now()
    for f in sorted(APPROVALS_DIR.glob("*.json")):
        record = _read_json(f)
        if record is None:
            continue
        if record.get("state") == PENDING:
            expires_at = record.get("expires_at_epoch")
            record["expired"] = (
                expires_at is not None and now > float(expires_at)
            )
        if state and record.get("state") != state:
            continue
        out.append(record)
    return out


def pending_approvals() -> List[Dict[str, Any]]:
    return [r for r in list_approvals(PENDING)]


# ═══════════════════════════════════════════════════════════════════════════
# PLANE 4 — THROTTLING  (ADVISORY in v1)
# ═══════════════════════════════════════════════════════════════════════════


def set_throttle(
    entity: str,
    max_tokens_per_hour: Optional[int] = None,
    max_tool_calls_per_hour: Optional[int] = None,
    set_by: Optional[str] = None,
) -> Dict[str, Any]:
    """Register or update a per-entity hourly rate limit.

    Either limit may be None to leave it unchanged; passing None for both is
    rejected rather than silently clearing every limit.
    """
    if not entity or not str(entity).strip():
        raise ControlPlaneError("missing_entity", "throttle requires entity")
    if max_tokens_per_hour is None and max_tool_calls_per_hour is None:
        raise ControlPlaneError(
            "missing_limits",
            "set_throttle requires at least one of max_tokens_per_hour or "
            "max_tool_calls_per_hour. Use clear_throttle() to remove a limit.",
        )
    for label, value in (("max_tokens_per_hour", max_tokens_per_hour),
                         ("max_tool_calls_per_hour", max_tool_calls_per_hour)):
        if value is not None and value <= 0:
            raise ControlPlaneError(
                "invalid_limit", f"{label} must be positive; got {value}"
            )
    entity = str(entity).strip()
    ensure_dirs()
    state = _load_state()
    throttles = state.setdefault("throttles", {})
    current = throttles.get(entity, {})
    merged = dict(current)
    if max_tokens_per_hour is not None:
        merged["max_tokens_per_hour"] = int(max_tokens_per_hour)
    if max_tool_calls_per_hour is not None:
        merged["max_tool_calls_per_hour"] = int(max_tool_calls_per_hour)
    merged.update({
        "entity": entity,
        "set_at": _now_iso(),
        "set_by": set_by,
        "window_s": 3600,
        "enforcement": ENFORCEMENT["throttle"]["status"],
    })
    throttles[entity] = merged
    _save_state(state)
    return {"result": "throttled", "entity": entity, "limits": merged,
            "enforcement": ENFORCEMENT["throttle"]["status"]}


def clear_throttle(entity: str, cleared_by: Optional[str] = None) -> Dict[str, Any]:
    entity = str(entity).strip()
    ensure_dirs()
    state = _load_state()
    existed = state.setdefault("throttles", {}).pop(entity, None)
    _save_state(state)
    return {"result": "cleared" if existed else "noop", "entity": entity,
            "was_throttled": existed is not None, "idempotent": True,
            "cleared_by": cleared_by}


def list_throttles() -> List[Dict[str, Any]]:
    state = _load_state()
    return sorted(state.get("throttles", {}).values(), key=lambda t: t.get("entity", ""))


def check_throttle(
    entity: str,
    tokens_used: int = 0,
    tool_calls_used: int = 0,
) -> Dict[str, Any]:
    """Compare observed usage against a registered limit. ADVISORY.

    Nothing counts tokens or tool calls on the dispatch path in v1, so
    `tokens_used` / `tool_calls_used` are supplied by the caller. This function
    reports whether those numbers are over the line; it does not stop anything.
    Treating an ADVISORY result as enforcement is the specific failure this
    status label exists to prevent.
    """
    state = _load_state()
    limits = state.get("throttles", {}).get(str(entity).strip())
    if not limits:
        return {"entity": entity, "throttled": False, "exceeded": False,
                "enforcement": ENFORCEMENT["throttle"]["status"],
                "note": "No throttle registered for this entity."}
    exceeded: List[str] = []
    if limits.get("max_tokens_per_hour") is not None and \
            tokens_used > int(limits["max_tokens_per_hour"]):
        exceeded.append("tokens")
    if limits.get("max_tool_calls_per_hour") is not None and \
            tool_calls_used > int(limits["max_tool_calls_per_hour"]):
        exceeded.append("tool_calls")
    return {
        "entity": entity,
        "throttled": True,
        "exceeded": bool(exceeded),
        "exceeded_dimensions": exceeded,
        "limits": limits,
        "observed": {"tokens_used": tokens_used, "tool_calls_used": tool_calls_used,
                     "window_s": limits.get("window_s", 3600)},
        "enforcement": ENFORCEMENT["throttle"]["status"],
        "note": ENFORCEMENT["throttle"]["not_enforced"],
    }


# ═══════════════════════════════════════════════════════════════════════════
# STATUS + RADAR
# ═══════════════════════════════════════════════════════════════════════════


def status() -> Dict[str, Any]:
    """All active controls. Feeds the harvester radar.

    Shape is stable: kills / approvals / throttles / config / enforcement are
    always present, even when empty. An absent key and a zero count are
    different claims, and only one of them is true.
    """
    kills = active_kills()
    pending = pending_approvals()
    throttles = list_throttles()
    return {
        "schema": CONTROL_SCHEMA,
        "generated_at": _now_iso(),
        "killed_count": len(kills),
        "killed": kills,
        "pending_approvals": len(pending),
        "pending_approval_ids": [p.get("operation_id") for p in pending],
        "expired_pending": [p.get("operation_id") for p in pending if p.get("expired")],
        "throttle_count": len(throttles),
        "throttles": throttles,
        "config": config(),
        "enforcement": ENFORCEMENT,
        "paths": {
            "control_dir": str(CONTROL_DIR),
            "kill_log": str(KILL_LOG_PATH),
            "decision_log": str(DECISION_LOG_PATH),
            "approvals": str(APPROVALS_DIR),
        },
    }


def radar_block() -> Dict[str, Any]:
    """Compact control-plane summary for the harvester's `radar` object.

    Deliberately small and total. The harvester runs every 300s and must not
    fail because the control plane is missing or corrupt — but it must also not
    silently report zeros it did not verify. On an unreadable store this
    returns `control_plane_ok: false` with the reason, which is a visible gap
    rather than a false all-clear (M23).
    """
    try:
        kills = active_kills()
        pending = pending_approvals()
        throttles = list_throttles()
        return {
            "control_plane_ok": True,
            "killed_count": len(kills),
            "pending_approvals": len(pending),
            "throttled_entities": len(throttles),
            "approval_timeout_s": approval_timeout_s(),
            "enforced_planes": sorted(
                k for k, v in ENFORCEMENT.items() if v.get("enforced")
            ),
        }
    except ControlPlaneError as exc:
        return {
            "control_plane_ok": False,
            "control_plane_error": exc.code,
            "killed_count": None,
            "pending_approvals": None,
            "note": (
                "Control-plane state unreadable. Counts are null, not zero — an "
                "unreadable store is not an all-clear (M23)."
            ),
        }


__all__ = [
    "CONTROL_DIR", "CONTROL_STATE_PATH", "KILL_LOG_PATH", "DECISION_LOG_PATH",
    "APPROVALS_DIR", "CONTROL_SCHEMA", "ALLOW", "DENY", "PENDING", "APPROVED",
    "DEFAULT_APPROVAL_TIMEOUT_S", "ENV_APPROVAL_TIMEOUT", "ENFORCEMENT",
    "ControlPlaneError",
    "approval_timeout_s", "config", "ensure_dirs",
    "kill", "release", "is_killed", "active_kills", "killed_session_ids",
    "escalate",
    "request_approval", "approve", "check", "list_approvals", "pending_approvals",
    "set_throttle", "clear_throttle", "list_throttles", "check_throttle",
    "status", "radar_block",
]