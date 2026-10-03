# ⬡ CONTROL PLANE — Four Production Control Planes

**Status**: ACTIVE (v1)
**Date**: 2026-10-03
**Ticket**: P1-1 (knowledge-gap report)
**Entity**: @doom_guy (Slot S1 Infrastructure Keeper)
**Frontier**: arXiv 2605.20173 (2026) — *"Build the dashboard before the agent. The trace is the contract."*

---

## L1 — Executive Summary

We had blockers and handoffs but no formal control plane. A runaway subagent could not be
halted. Destructive operations had no human gate. Token and tool spend was unbounded. A
blocker had no automatic route to a higher authority.

This document specifies four control planes and — more importantly — states plainly which
of them actually enforce anything today.

**One plane is fully enforced. One is partially enforced. One is a correct gate with
nothing calling it. One is advisory.** That distribution is not a hedge; it is the point.
A control plane believed to be enforcing when it is not produces confidence without a
control, which is strictly worse than having no plane, because the absence at least
looks like absence.

| # | Plane | Enforcement | One-line truth |
|---|-------|-------------|----------------|
| 1 | **Kill** | `PARTIAL` | Refuses to continue + durable marker. Does **not** interrupt an in-flight turn in another process. |
| 2 | **Escalate** | `ENFORCED` | Real mutation of `data/handoff/pending/`. You can watch it land. |
| 3 | **Approve** | `GATE_ENFORCED__CALLSITES_ADVISORY` | The gate is total and fail-closed. No destructive op calls it yet. |
| 4 | **Throttle** | `ADVISORY` | Registers limits and reports exceedance. Nothing counts spend yet. |

---

## L2 — Why This Order, and Not Another

The four planes are not a feature checklist. The deployment order is load-bearing, and
each position is a consequence of the one before it.

### 1. Kill switch — first, unconditionally

If you cannot stop the bleeding, every other control is theatre. A runaway agent burning
tokens, writing files, and ignoring its queue is not a problem that better routing or
approval semantics will address. Nothing below is worth deploying until you can halt.

### 2. Escalation — second, because stopping is not resolving

Once you can halt, the next question is who unblocks it. A kill with no route to a human
converts a runaway into a corpse. Escalation is what makes the kill productive rather than
merely decisive.

### 3. Approval — third, because gating an unroutable queue gates nothing

Human-in-the-loop only means something when the request actually reaches a human. If the
escalation path is broken, a pending approval is not a safety gate — it is a queue nobody
drains. Approve before escalate and you have built a lock on a door that does not connect
to anything.

### 4. Throttling — last, and this is the surprising one

Throttling is the only plane that **degrades throughput** rather than stopping work. Every
other plane is fail-safe under misconfiguration: a broken kill switch refuses to continue,
a broken approval gate denies. A broken throttle is not.

The failure mode is asymmetric and quiet. Set a limit too tight and real work silently
starves — no error, no alert, just an agent that appears lazy. Set it too loose and nothing
happens. There is no configuration of a throttle that fails loudly, which is exactly why it
belongs after the three planes that do.

---

## L3 — The Four Planes

### Plane 1 — KILL

```
control(action="kill", session_id=…, entity=…, reason=…)
control(action="release", session_id=…)
```

Halt a runaway session. **Idempotent by construction**: killing an already-dead session is
a no-op, *not an error*. In a fleet where several watchers watch the same runaway, a double
press is normal traffic, not a fault.

Idempotency means **state does not change**. The second call preserves the original
`reason` and `killed_at`. It does still append a `kill_noop` line to `kill_log.jsonl`,
because an operator pressing the button is evidence worth keeping — the *state* is
idempotent, the *audit trail* is not blind.

**Enforcement — `PARTIAL`.** Be precise about what this buys you:

- **ENFORCED:** `is_killed(session_id)` is consulted at hub-side advisory points; killed
  sessions are marked `🔴 KILLED` on the harvester radar and are excluded from
  `active_agents_count`.
- **NOT ENFORCED:** this does **not** interrupt an in-flight model turn inside an external
  OpenCode process. The dispatcher that would host that check lives under `src/omega/`,
  behind the M2 firewall, and no API exists to reach a running session from here.

A kill here is a refusal-to-continue plus a loud durable marker. It is not SIGKILL.

`release` is **not** in the frontier spec. It is here because a kill with no release is a
one-way door, and a one-way door wired into a fleet is an outage waiting for a typo. The
kill record is never deleted — it is marked released (M28).

### Plane 2 — ESCALATE

```
control(action="escalate", packet_id=…, to_entity=…)
```

Promote a blocker/handoff to a higher authority. Reuses the real handoff store: the packet
is re-targeted, priority raised to `2` (critical — an escalated blocker is not normal
traffic), and the move appended to the packet's own `escalation_history`.

**Enforcement — `ENFORCED`.** The packet lands in `data/handoff/pending/` where the
target's `hivemind_handoff(action="inbox")` will see it. This is the one plane whose effect
you can observe without trusting a flag.

Two fail-loud refusals:

- Unknown `packet_id` → `unknown_packet`. An escalation of a packet that does not exist is
  a **fabricated blocker**, which is worse than no escalation at all.
- Missing `to_entity` → `missing_to_entity`. An escalation with no destination is a blocker
  written into the void.

### Plane 3 — APPROVE  *(the fail-closed plane)*

```
control(action="request_approval", operation=…, entity=…, timeout_s=…)
control(action="approve", operation_id=…, approved=bool, decided_by=…)
control(action="check", operation_id=…)
```

Human-in-the-loop gate for destructive operations.

**Resolution table — there is no fifth row:**

| Condition | Decision | `fail_closed` |
|-----------|----------|---------------|
| Unknown `operation_id` | **DENY** | `true` |
| Missing/blank `operation_id` | **DENY** | `true` |
| Pending, past `expires_at` | **DENY** | `true` |
| Pending, unanswered, in window | **DENY** (gate) | `false` |
| Pending, `approved=True`, in window | ALLOW | `false` |
| Pending, `approved=False` | DENY | `false` |
| Already decided | the recorded decision | `false` |

Every row denies except one. That is the design.

**The dangerous failure mode for a human gate is silence.** Nobody answered, so the
operation proceeded — the exact inverse of safety. Therefore *unanswered is not approved*.
A pending request checks DENY until a human explicitly clears it.

**Enforcement — `GATE_ENFORCED__CALLSITES_ADVISORY`.** The decision function is total,
deterministic, and fail-closed on every unresolved path. **No destructive operation calls
`check()` yet.** In v1 this is a correct gate with no doors wired to it. Treat it as a
primitive, not a control.

### Plane 4 — THROTTLE

```
control(action="throttle", entity=…, max_tokens_per_hour=…, max_tool_calls_per_hour=…)
control(action="throttle_check", entity=…, tokens_used=…, tool_calls_used=…)
```

Per-entity hourly rate limits. `set_throttle` merges: passing one limit leaves the other
untouched. Passing neither is rejected — use `unthrottle` to remove a limit rather than
silently clearing both.

**Enforcement — `ADVISORY`.** Nothing counts tokens or tool calls on the dispatch path in
v1, so `tokens_used` / `tool_calls_used` are supplied by the caller. `throttle_check`
compares a number against a stored limit and reports. **It does not stop anything.**

---

## The Approval Timeout — N, and where it lives

**N = 900 seconds (15 minutes).**

Precedence, highest first:

| Priority | Source | Purpose |
|----------|--------|---------|
| 1 | `timeout_s` argument on `request_approval()` | per-request override |
| 2 | `OMEGA_APPROVAL_TIMEOUT_S` env var | deployment-wide override |
| 3 | `DEFAULT_APPROVAL_TIMEOUT_S = 900` | compiled-in floor |

**Unanswered past N is DENIED.** There is no extend, no "pending forever", and no
default-allow path. An expired request is resolved to DENY and written to
`decisions.jsonl`, so the denial is auditable rather than merely inferred.

A malformed or non-positive override (`"abc"`, `"0"`, `"-5"`) falls back to 900 and
records a `config_anomaly` in `config()`. It does **not** open an unbounded window and it
does **not** crash the gate.

### The fail-closed proof

**Code path** (`mcp_servers/omega_hub/control_plane.py`, `approve()`):

```
approve(op, approved=True)
  └─ record = _read_json(_approval_path(op))
       ├─ record is None ──────────────────► return DENY, fail_closed=True,
       │                                      reason="unknown_operation_id"
       └─ record["state"] in (approved, denied) ──► return recorded decision
                                                 (terminal, never overwritten)
  └─ expires_at = record["expires_at_epoch"]; now = _now()
       └─ now > expires_at ─────────────────► _resolve_terminal(DENY,
                                          reason="approval_timeout",
                                          fail_closed=True)
       └─ approved  ────────────────────────► _resolve_terminal(APPROVED)
       └─ not approved ─────────────────────► _resolve_terminal(DENIED,
                                          reason="human_denied")
```

The load-bearing detail: **the expiry check runs BEFORE the `approved` branch.** An explicit
`approved=True` cannot revive an expired request. Silence is not consent.

**Test assertion** — `tests/test_control_plane.py::test_approval_timeout_denies_fail_closed`:

```python
req = CP.request_approval(operation="drop_database", timeout_s=900)
assert CP.check(operation_id=op)["decision"] == CP.DENY   # pending, in window

clock(901)                                                # one second past expiry

gate = CP.check(operation_id=op)
assert gate["decision"] == CP.DENY
assert gate["reason"] == "approval_timeout"
assert gate["fail_closed"] is True

r = CP.approve(operation_id=op, approved=True)            # ← the decisive call
assert r["decision"] == CP.DENY                           # explicit approve LOSES
assert r["fail_closed"] is True
assert r["reason"] == "approval_timeout"
```

No test sleeps: `_now()` is monkeypatched, so the suite is hermetic and instant.

---

## Persistence

```
data/coordination/control/
├── control.json          state: killed set + throttles   (atomic replace)
├── kill_log.jsonl        append-only kill audit trail    (M28)
├── decisions.jsonl       append-only decision audit      (M28)
└── approvals/
    └── op_<id>.json      one file per request            (atomic replace)
```

- **Append-only logs** (`kill_log.jsonl`, `decisions.jsonl`): opened `"a"`, fsynced per
  record, **never rewritten or truncated**.
- **State files**: tmp + `fsync` + `os.replace` via the canonical
  `federation_envelope.write_atomic`, so a reader never observes a partial file.
- **Corrupt state fails loud.** `_load_state()` raises `control_state_corrupt` rather than
  returning empty. Returning empty would report "nothing is killed, no throttles exist" —
  a confident false all-clear.

---

## Harvester Radar Integration

`scripts/hivemind_harvest.py` calls `control_plane.radar_block()` each 300s cycle.

`latest.json` → `radar`:

```json
{
  "blocker_count": 0,
  "pending_handoff_count": 62,
  "active_agents_count": 2,
  "killed_count": 1,
  "pending_approvals": 1,
  "throttled_entities": 1,
  "control_plane_ok": true,
  "enforced_planes": ["escalate", "kill"]
}
```

`latest.md` → the 3-line triage radar gains a fourth line:

```
# ⬡ HIVEMIND FLEET RADAR — 2026-10-03T22:39:14.021785+00:00 [FRESH]
🔴 0 BLOCKERS | ⚡ 62 PENDING HANDOFFS | 🟢 2 AGENTS ACTIVE
☠️ 1 KILLED | ⏳ 1 PENDING APPROVALS
```

A killed session renders as `🔴 KILLED` in its fleet row and is **excluded from
`active_agents_count`** — a halted agent must never read as merely idle:

```
- **🔴 KILLED** `@testkilledagent` (`ses_RUNAWAY_`) — DOING spin · NEXT none
```

### Degradation (M23)

If the control plane is missing or corrupt, the harvester still publishes — a dead radar is
worse than one that admits it is blind. But it reports `null`, **never `0`**:

```json
"killed_count": null, "pending_approvals": null,
"control_plane_ok": false
```

```
☠️ ? KILLED | ⏳ ? PENDING APPROVALS | ⚠️ CONTROL PLANE UNREADABLE
```

Status degrades to `STALE_PARTIAL` with a `control_plane` gap entry. An unreadable store is
not an all-clear.

---

## How To Use Them

### Halt a runaway

```jsonc
control(action="kill", session_id="ses_abc", entity="roc_racoon",
        reason="token spin, ignored 3 interrupts", requested_by="doom_guy")
// → {"result": "killed", "already_killed": false, ...}

control(action="kill", session_id="ses_abc")
// → {"result": "noop", "already_killed": true, "idempotent": true}
//   A second press is a no-op, NOT an error.
```

### Gate a destructive operation

```jsonc
control(action="request_approval", operation="rm -rf data/knowledge",
        entity="doom_guy", detail="P1-2 cleanup", timeout_s=900)
// → {"result": "requested", "operation_id": "op_…", "timeout_s": 900,
//
//    "on_timeout": "DENY"}

control(action="check", operation_id="op_…")
// → {"decision": "DENY", "reason": "awaiting_human_decision"}
//    DENY until a human acts. Not a pending "maybe".

control(action="approve", operation_id="op_…", approved=true, decided_by="kali")
// → {"decision": "ALLOW", "approved": true}
```

### Escalate a blocker

```jsonc
control(action="escalate", packet_id="ho_abc", to_entity="makali",
        reason="blocked 3h, needs sovereign decision")
// → {"result": "escalated", "to_agent_id": "opencode/makali", "priority": 2}
```

### Inspect the fleet

```jsonc
control(action="status")
// → full state + config + the enforcement matrix
control(action="radar")
// → compact block only, for embedding
```

---

## Known Gaps (v1)

Stated plainly rather than discovered later:

1. **No destructive operation calls `check()` yet.** The approval plane is a primitive
   awaiting doors. Highest-value next wiring: destructive filesystem ops, dispatch,
   `git push --force`, and vault exports.
2. **Kill cannot interrupt an external process.** Reaching a running OpenCode turn needs a
   dispatcher hook under `src/omega/` (M2 firewall) and an API that does not yet exist.
3. **Nothing counts spend.** Throttle needs a counter feeding it from the dispatch path.
4. **Escalation is manual.** No automatic escalation on repeated blockers or on a blocked
   queue age — the plane exists, the trigger does not.
5. **Single-node.** Kills and approvals are local filesystem state. A node that cannot see
   `data/coordination/control/` cannot honour a kill issued elsewhere.

---

## Mandate Compliance

| Mandate | Compliance |
|---------|-----------|
| **M1 AnyIO** | Zero `import asyncio`. Every tool action runs via `anyio.to_thread.run_sync`. `make check-m1-anyio` passes. |
| **M2 Firewall** | All control-plane code in `mcp_servers/omega_hub/`. **Zero** changes under `src/omega/`. |
| **M7 Local-First** | Filesystem only. Zero inference, zero network. |
| **M8 Zero Telemetry** | No egress. |
| **M23 Failure Integrity** | Fail-CLOSED on approval timeout/unknown. Corrupt state raises rather than reporting an empty store. Degraded radar reports `null`, never `0`. |
| **M28 Preservation** | `kill_log.jsonl` + `decisions.jsonl` append-only, never truncated. State files atomically replaced. |

---

## Verification

```
tests/test_control_plane.py                    37 passed, 0 failed
  make check-m1-anyio                          PASS
  end-to-end via MCP tool surface              kill idempotency, fail-closed,
                                               error codes, status shape — all correct
  harvester end-to-end                         radar block + 🔴 KILLED row +
                                               ACTIVE exclusion confirmed
  degraded path                                corrupt store → null + STALE_PARTIAL
```

**Deployment note:** the `control` tool is registered in code but the hub process running
on this node (PID 3113, started 14:18) predates this change and still serves 54 tools. It
must be **restarted** before `control` is reachable over MCP. Until then,
`tests/test_hub_health.py::test_registered_surface_is_complete` fails with
`55 != 54` — verified to be exactly this delta by unregistering `control` (54 == 54, PASS).

*⬡ OMEGA ⬡ DOOM_GUY ⬡ SLOT-S1 ⬡ CONTROL-PLANE-v1 ⬡ 2026-10-03*