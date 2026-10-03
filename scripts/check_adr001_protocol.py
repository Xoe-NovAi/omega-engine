# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""ADR-001 gate: the protocol is valid data, and the engine surface stays small.

Two properties, both falsifiable, both observed red before being trusted:

  1. The declared protocol file loads and satisfies its own invariants.
  2. The interpreter exposes exactly six verbs.

Property 2 is the load-bearing one. id unlocked thirty years of complexity
without changing its engine, because every verb added to an engine is a
future migration for every WAD in existence. This gate is what makes
"does this add to the surface?" a question with a mechanical answer.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from mcp_servers.omega_hub.federation_protocol import (  # noqa: E402
    ProtocolMalformed,
    load_protocol,
    receipt_fields,
    surface,
)

PROTOCOL = REPO_ROOT / "config/wads/_omega_default/protocol/hivemind.yaml"
EXPECTED_SURFACE = {
    "load",      # read a declared protocol
    "validate",  # check a message against the declared schema
    "persist",   # write it with a monotonic sequence number
    "read",      # the declared query path
    "transition",  # record a legal state change
    "receipt",   # the recorded outcome
}


def main() -> int:
    print("Checking ADR-001: communication protocol as data...")
    failures: list[str] = []

    # ── 1. the declared protocol must load ──
    try:
        proto = load_protocol(PROTOCOL)
        print(f"  protocol loads: {proto.name} v{proto.version}")
    except ProtocolMalformed as exc:
        print(f"  [1/3] FAIL: protocol does not load — {exc}")
        return 1

    # ── 2. invariants the data must satisfy ──
    print("  [1/3] Checking declared invariants...")
    if not proto.required:
        failures.append("schema.required is empty")
    for field in ("requested_target", "resolved_target"):
        if field not in proto.required:
            failures.append(
                f"{field} must be REQUIRED — without it the store cannot answer "
                "whether the sender omitted a suffix or the resolver stripped one"
            )
    if proto.initial_state not in proto.states:
        failures.append("lifecycle.initial is not a declared state")
    if proto.layout.get("inbox") != "pending":
        failures.append(
            f"layout.inbox is {proto.layout.get('inbox')!r}, expected 'pending'. "
            "The directory name is interface: it must tell an operator what the "
            "directory is for."
        )
    if proto.raw.get("retention", {}).get("auto_delete") is not False:
        failures.append("retention.auto_delete must be false (M29)")
    if proto.retention_days("retired") is not None:
        failures.append("retired must have no retention limit (M29)")

    # ── 3. the six-verb cap ──
    print("  [2/3] Checking the interpreter surface...")
    got = set(surface())
    if got != EXPECTED_SURFACE:
        failures.append(
            f"interpreter surface changed: expected {sorted(EXPECTED_SURFACE)}, "
            f"got {sorted(got)}. Adding a verb is allowed only if the complexity "
            "belongs in DATA instead. Update ADR-001 deliberately, do not drift."
        )

    # ── 4. node suffix must remain significant ──
    print("  [3/3] Checking the naming declaration...")
    if not proto.suffix_is_significant:
        failures.append(
            "naming.node_suffix_is_significant is false. makali-n0 and makali are "
            "distinct registered agents; folding them was the deployed heuristic "
            "GE-N0 measured and found wrong."
        )
    if not receipt_fields(proto):
        failures.append("delivery.receipt_fields must be declared")

    if failures:
        print(f"\n  FAIL: {len(failures)} ADR-001 violation(s):")
        for f in failures:
            print(f"    - {f}")
        return 1

    print(f"  ✓ protocol valid · surface = {len(got)} verbs · naming safe")
    print("  ADR-001 passed: the protocol is data, the engine is its interpreter.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
