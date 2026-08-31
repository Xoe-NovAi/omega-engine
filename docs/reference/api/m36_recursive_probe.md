# API Reference: M36 Recursive Probe

> M36RecursiveProbe — recursive cross-validation probe with M23 honest stub behavior.

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
