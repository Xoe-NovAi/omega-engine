# API Reference: M36 Recursive Probe

> M36RecursiveProbe — recursive cross-validation probe with M23 honest stub behavior.

---

## Queue Isolation (2026-09-29)

Cross-validation packets are written to a **dedicated test queue**, never to live
Hivemind state.

**Root**: `data/handoff/m36-test/` — with its own `pending/ active/ completed/
stale/ archive/` subdirectories.

The live queue root is `state.HANDOFF_BASE`. The probe re-roots that for the
duration of the dispatch call and **restores it in a `finally` block**.

### Why this is structural, not a check

Before this change, the harness wrote `[M36 CROSS-VALIDATOR]` packets into the
**live** queue at `data/handoff/pending/`. It accumulated **42** of them, making
the live queue 64% test noise — which is why real packets went unread for hours.
39 pointed at `/tmp/`, 3 at `/nonexistent/deliverable.md`; none referenced a real
repo path, and none carried work product.

There are **two write sinks**, both in this file:

1. `hivemind_handoff(action="submit", ...)` called in-process
2. a direct `Path("data/handoff/pending")` write, taken when the tool call fails

Fixing only the tool call would have left the tap open. Both now target the test
root, so reaching live state is **impossible by construction** rather than
merely unlikely. A marker grep remains as belt-and-braces, but the separate
directory is the load-bearing part.

**Audit record** for the purge: `data/handoff/archive/M36-test-purge-20260929/PURGE_RECORD.md`

### The restore must be in `finally`

The restore originally sat *after* the outer `except` block. Any exception
outside the caught tuple (`AttributeError`, `RuntimeError`, `KeyboardInterrupt`,
`SystemExit`) exited the function without ever restoring the live root — leaving
the process **permanently** re-rooted at the test root, so every subsequent
handoff in that process wrote to a directory nobody watches.

That is a live-queue corruption path, not a test-hygiene path. The restore is now
in `finally` with pre-bound locals, so the import-failure path cannot itself
raise `UnboundLocalError`.

**Verified by sabotage**: removing the `finally` takes
`test_live_root_is_restored_after_dispatch` red.

### Known limitation

`HANDOFF_BASE` is a **process-global**. A concurrent handoff dispatched while an
M36 call is in flight will inherit the test root. There is no lock and no
`contextvars` isolation. This is a known residual risk, not a resolved issue —
the correct fix is to thread the queue root through as a parameter rather than
mutating a module global.

---

## Overview

**File**: `src/omega/oracle/m36_recursive_probe.py`

The M36 Recursive Probe performs recursive cross-validation of a deliverable against its specification. It is part of the M33/M34/M36 probe chain.

---

## M23 Honest Stub Behavior (2026-08-30)

The cross-validator dispatch via Hivemind is **not yet implemented** as real multi-agent dispatch. To comply with **M23 Failure Integrity** (no soft-failures, never synthesize a result), the stub now returns an **honest disclosure** instead of a fake success.

### Before (M23 Violation)

The stub previously returned `handoff_dispatched: True` without actually dispatching anything — a soft-failure pattern masquerading as a gate.

### After (M23 Compliant)

The stub now returns:

```python
{
    "status": "stub_bypass",              # explicit: this is a bypass, not a real dispatch
    "semantic_coverage_verified": False,  # NOT verified (no real cross-validator ran)
    "queued_findings_addressed": False,
    "deliverable_meets_purpose": False,
    "cross_validator_agent": agent,
    "cross_validator_timeout": False,
    "cross_validator_timeout_seconds": CROSS_VALIDATOR_TIMEOUT_SECONDS,
    "handoff_dispatched": False,          # M23: stub does NOT dispatch
    "handoff_packet_id": None,
    "priority": priority,
    "deliverable_path": deliverable_path,
    "verification_prompt": prompt,
    "_m23_honesty": "Stub bypass — real Hivemind dispatch not implemented. Cross-validation is P0-recommendation-only per 5-EIS consensus.",
}
```

### Key Changes

| Field | Old Value | New Value | Why |
|-------|-----------|-----------|-----|
| `status` | *(absent)* | `"stub_bypass"` | Explicit disclosure that this is a bypass |
| `handoff_dispatched` | `True` | `False` | M23: never claim a dispatch that didn't happen |
| `handoff_packet_id` | `handoff_packet_id` | `None` | No packet was created |
| `_m23_honesty` | *(absent)* | disclosure string | Machine-readable honesty marker |

---

## Status

- **Implementation**: Stub only. Real Hivemind dispatch is **not implemented**.
- **Decision pending**: Q3 in the Sonnet 5 audit — implement real dispatch (8-12h), delete entirely (saves 530 lines), or gate behind `OMEGA_M36_ENABLED=1` (hybrid, default OFF).
- **Current recommendation** (5-EIS consensus): P0-recommendation-only.

---

## Related

- `src/omega/oracle/m33_probe.py` — M33 write-tool probe (candidate to fold into dispatcher)
- `src/omega/oracle/m34_registry.py` — M34 session registry
- `SOVEREIGN_MANDATES.md` §M23 — Failure Integrity
