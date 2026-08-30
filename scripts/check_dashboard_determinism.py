#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Determinism check for benchmark_dashboard --json output.

AP: AP-DASHBOARD-SHIP-R4-v1.0.0

Verifies that two consecutive renders of the dashboard (same input data
on disk, advancing wall-clock between runs) produce JSON with stable
SHAPE and SEMANTIC PAYLOAD — only the timestamp and freshness age fields
should differ.

Usage:
    python3 scripts/check_dashboard_determinism.py run1.json run2.json

Exit 0 = stable, 1 = drift detected.

Why not 100% byte-equal? Two fields are intentionally time-dependent:

  1. state["timestamp"]  -- the moment we rendered the dashboard
  2. freshness[*]["age_seconds"]  -- how old each input file is right now

If file mtimes stay constant and wall clock advances by N seconds, every
age_seconds increases by N. That is correct real-time behavior, not a
bug. What we DO verify is structural stability: same top-level keys,
same per-source freshness keys, same model fields. If a future change
adds a new top-level key or renames a field, this gate fails.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


# Fields that are allowed to differ between runs (time-dependent by design).
TIME_DEPENDENT = {
    ("timestamp",),  # state-level render timestamp
}


def is_time_dependent(path: tuple[str, ...]) -> bool:
    """Return True if the dotted path is one of the allowed time-varying fields.

    freshness[*].age_seconds is allowed to differ — files age in real time.
    Everything else must be byte-stable.
    """
    if path == ("timestamp",):
        return True
    # (freshness, <source>, age_seconds) — same logic
    if len(path) == 3 and path[0] == "freshness" and path[2] == "age_seconds":
        return True
    return False


def walk_diff(a: object, b: object, path: tuple[str, ...] = ()) -> list[str]:
    """Return a list of dotted paths where `a` and `b` differ."""
    diffs: list[str] = []
    if type(a) is not type(b):
        diffs.append(f"{'.'.join(path) or '<root>'}: type {type(a).__name__} vs {type(b).__name__}")
        return diffs
    if isinstance(a, dict):
        a_keys = sorted(a.keys())
        b_keys = sorted(b.keys())
        if a_keys != b_keys:
            missing_in_b = [k for k in a_keys if k not in b]
            missing_in_a = [k for k in b_keys if k not in a]
            if missing_in_b:
                diffs.append(f"{'.'.join(path) or '<root>'}: keys only in run1: {missing_in_b}")
            if missing_in_a:
                diffs.append(f"{'.'.join(path) or '<root>'}: keys only in run2: {missing_in_a}")
            return diffs
        for k in a_keys:
            diffs.extend(walk_diff(a[k], b[k], path + (str(k),)))
        return diffs
    if isinstance(a, list):
        if len(a) != len(b):
            diffs.append(f"{'.'.join(path) or '<root>'}: list length {len(a)} vs {len(b)}")
            return diffs
        for i, (ai, bi) in enumerate(zip(a, b)):
            diffs.extend(walk_diff(ai, bi, path + (f"[{i}]",)))
        return diffs
    if a != b:
        diffs.append(f"{'.'.join(path) or '<root>'}: {a!r} vs {b!r}")
    return diffs


def main() -> int:
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} run1.json run2.json", file=sys.stderr)
        return 2

    path_a = Path(sys.argv[1])
    path_b = Path(sys.argv[2])

    if not path_a.exists() or not path_b.exists():
        print(f"ERROR: missing input files: {path_a}, {path_b}", file=sys.stderr)
        return 2

    a = json.loads(path_a.read_text())
    b = json.loads(path_b.read_text())

    diffs = walk_diff(a, b)
    # Filter out the time-dependent fields (timestamp, freshness[*].age_seconds)
    semantic_diffs = [d for d in diffs if not is_time_dependent_from_str(d)]

    if semantic_diffs:
        print("❌ DETERMINISM DRIFT DETECTED:")
        for d in semantic_diffs[:20]:  # cap output to first 20
            print(f"  - {d}")
        if len(semantic_diffs) > 20:
            print(f"  ... and {len(semantic_diffs) - 20} more")
        return 1

    time_diffs = [d for d in diffs if is_time_dependent_from_str(d)]
    print(f"✅ Determinism OK: shape stable, {len(time_diffs)} time-dependent field(s) varied as expected")
    return 0


def is_time_dependent_from_str(dotted: str) -> bool:
    """Convert dotted path string to tuple and check if it's time-dependent."""
    if dotted.startswith("<root>"):
        return False
    parts = tuple(dotted.split(":")[0].split("."))
    if parts == ("timestamp",):
        return True
    if len(parts) == 3 and parts[0] == "freshness" and parts[2] == "age_seconds":
        return True
    return False


if __name__ == "__main__":
    sys.exit(main())