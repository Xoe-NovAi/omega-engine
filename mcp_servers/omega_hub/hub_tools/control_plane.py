# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Omega Control Plane — MCP tool surface.

Thin async adapter over `mcp_servers.omega_hub.control_plane`. Every call is
blocking filesystem I/O, so each action runs in an AnyIO worker thread (M1).
There is no `asyncio` import in this module, and there never will be.

DELIBERATE CONVENTION DEVIATION: NO `_require_service()`
--------------------------------------------------------
Every other tool on this hub calls `_require_service()` first. The control
plane does not, and that is intentional.

A kill switch that is unavailable while the hub's services are still
initializing, or degraded, or wedged, is not a kill switch — it is a switch
that works exactly when it is not needed. The control plane is pure filesystem
state with no service dependency, so requiring services would buy nothing and
cost availability at the one moment availability matters.

The flip side, stated plainly: `control` is reachable while the rest of the hub
is unhealthy. It is a small, read-mostly, append-only surface, and that is the
intended blast radius.

ERROR CONTRACT (load-bearing)
-----------------------------
A control-plane FAILURE is an ERROR PAYLOAD, never an empty success:

    {"error": {"code": "unknown_packet", "message": "...", ...}}

Branch on `error.code`, NOT on emptiness. `if not result: pass` passes equally
on a denial and a dead store, and a denial is a real answer that must not be
swallowed.

A DENIAL is not an error. `approve` and `check` return DENY as ordinary data
with `"fail_closed": true`. Collapsing "denied" into "error" would let a
caller's `except` branch turn a safety refusal into a retry.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

import anyio

from mcp_servers.omega_hub.middleware import m9_safe
from mcp_servers.omega_hub.server import mcp
from mcp_servers.omega_hub import control_plane as cp

logger = logging.getLogger("omega.hub.control")

VALID_ACTIONS = {
    "kill", "release", "escalate",
    "request_approval", "approve", "check",
    "throttle", "unthrottle", "throttle_check",
    "status", "radar", "config",
}


def _fail(exc: Exception) -> str:
    """Render an exception as the documented error payload (M23: no synthesis)."""
    if isinstance(exc, cp.ControlPlaneError):
        return json.dumps(exc.as_dict())
    return json.dumps({
        "error": {
            "code": "control_plane_failure",
            "message": str(exc),
            "type": type(exc).__name__,
            "note": "Control-plane operation failed. No synthetic result returned.",
        }
    })


@m9_safe("control")
@mcp.tool()
async def control(
    action: str,
    session_id: Optional[str] = None,
    entity: Optional[str] = None,
    packet_id: Optional[str] = None,
    to_entity: Optional[str] = None,
    to_channel: str = "opencode",
    reason: Optional[str] = None,
    requested_by: Optional[str] = None,
    released_by: Optional[str] = None,
    decided_by: Optional[str] = None,
    approved: Optional[bool] = None,
    operation_id: Optional[str] = None,
    operation: Optional[str] = None,
    detail: str = "",
    timeout_s: Optional[int] = None,
    max_tokens_per_hour: Optional[int] = None,
    max_tool_calls_per_hour: Optional[int] = None,
    tokens_used: int = 0,
    tool_calls_used: int = 0,
) -> str:
    """Four production control planes — kill, escalate, approve, throttle.

    DEPLOYMENT ORDER IS LOAD-BEARING: kill, escalate, approve, throttle. Kill
    first because nothing else matters if you cannot stop the bleeding.
    Escalate second so a halt is followed by a route to authority. Approve
    third because gating an unroutable queue gates nothing. Throttle last
    because it is the only plane that degrades throughput instead of stopping
    work, and so the easiest to wire wrong.

    Actions:
        kill              Halt a runaway session. IDEMPOTENT — killing an
                          already-dead session is a no-op, not an error.
        release           Lift a kill (operator escape hatch; the kill record is
                          kept, marked released).
        escalate          Promote a blocker/handoff to a higher authority.
                          Requires packet_id + to_entity. Writes to the real
                          handoff store.
        request_approval  OPEN an approval request. Returns operation_id.
        approve           Resolve one. FAIL-CLOSED: unknown id, or unanswered
                          past its timeout, both DENY.
        check             The gate: "may this operation proceed?" DENY unless an
                          explicit human ALLOW exists.
        throttle          Register/update a per-entity hourly limit.
        unthrottle        Remove a limit.
        throttle_check    Compare observed usage to a limit. ADVISORY in v1.
        status            All active controls. Feeds the harvester radar.
        radar             Compact radar block only.
        config            Effective config + timeout provenance.

    ENFORCEMENT — read before trusting a plane:
        kill      PARTIAL  (hub-side refusal + durable marker; does NOT
                            interrupt an in-flight turn in another process)
        escalate  ENFORCED (real mutation of data/handoff/pending)
        approve   GATE IS CORRECT, CALL SITES NOT WIRED (no destructive op
                  calls check() yet — a correct gate with no doors on it)
        throttle  ADVISORY (nothing counts spend on the dispatch path yet)

    Args:
        action: One of the actions listed above.
        session_id: Target session for kill/release.
        entity: Entity for throttle registration, or context on a kill.
        packet_id: Handoff packet to escalate.
        to_entity: Escalation destination.
        to_channel: Escalation destination channel (default opencode).
        reason: Free-text justification recorded with the action.
        requested_by: Who asked.
        released_by: Who lifted the kill.
        decided_by: Who decided the approval.
        approved: True/False for the approve action. Required there.
        operation_id: Target approval request for approve/check.
        operation: Short operation name for request_approval (e.g. "rm -rf /").
        detail: Human-readable detail shown to the approver.
        timeout_s: Per-request approval timeout. Falls back to
                   OMEGA_APPROVAL_TIMEOUT_S, then to 900.
        max_tokens_per_hour: Token ceiling for throttle.
        max_tool_calls_per_hour: Tool-call ceiling for throttle.
        tokens_used: Observed tokens for throttle_check (ADVISORY).
        tool_calls_used: Observed tool calls for throttle_check (ADVISORY).

    Returns:
        JSON string. On failure: {"error": {"code", "message"}}. A DENIAL is
        returned as data with "decision": "DENY" and "fail_closed": true.
    """
    if action not in VALID_ACTIONS:
        return json.dumps({
            "error": {
                "code": "invalid_action",
                "message": f"Invalid action {action!r}.",
                "valid": sorted(VALID_ACTIONS),
            }
        })

    try:
        def _work() -> Dict[str, Any]:
            if action == "kill":
                return cp.kill(session_id=session_id, entity=entity, reason=reason,
                               requested_by=requested_by)

            if action == "release":
                return cp.release(session_id=session_id, entity=entity, reason=reason,
                                  released_by=released_by)

            if action == "escalate":
                return cp.escalate(packet_id=packet_id, to_entity=to_entity,
                                   to_channel=to_channel, reason=reason,
                                   requested_by=requested_by, from_entity=entity)

            if action == "request_approval":
                return cp.request_approval(
                    operation=operation or "unspecified", entity=entity,
                    detail=detail, timeout_s=timeout_s, requested_by=requested_by,
                )

            if action == "approve":
                if approved is None:
                    return {"error": {
                        "code": "missing_approved",
                        "message": "approve requires approved=True or approved=False.",
                        "note": "Defaulting either way would make the gate a coin flip.",
                    }}
                return cp.approve(operation_id=operation_id, approved=approved,
                                  decided_by=decided_by, reason=reason)

            if action == "check":
                return cp.check(operation_id=operation_id)

            if action == "throttle":
                return cp.set_throttle(
                    entity=entity, max_tokens_per_hour=max_tokens_per_hour,
                    max_tool_calls_per_hour=max_tool_calls_per_hour,
                    set_by=requested_by,
                )

            if action == "unthrottle":
                return cp.clear_throttle(entity=entity, cleared_by=requested_by)

            if action == "throttle_check":
                return cp.check_throttle(entity=entity, tokens_used=tokens_used,
                                         tool_calls_used=tool_calls_used)

            if action == "status":
                return cp.status()

            if action == "radar":
                return cp.radar_block()

            return cp.config()  # action == "config"

        # Every action is blocking filesystem I/O (M1).
        return json.dumps(await anyio.to_thread.run_sync(_work))
    except Exception as exc:  # noqa: BLE001 — surfaced as an error payload, not synthesized
        logger.warning("control action=%s failed: %s", action, exc)
        return _fail(exc)


__all__ = ["control", "VALID_ACTIONS"]