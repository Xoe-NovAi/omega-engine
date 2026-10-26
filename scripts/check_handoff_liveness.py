#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
# SPDX-License-Identifier: Apache-2.0
"""Handoff plane liveness check (SLO).

Reports whether the handoff plane is alive. A plane with zero pending AND
zero active packets for longer than STALE_HOURS is considered dead — not
"all clear". This is the check that would have caught the 6-day silence
(2026-10-20 → 2026-10-26) that went unnoticed because the watchdog was
also dead.

Exit codes:
  0 — plane is alive (pending or active packets exist, or last activity
      within STALE_HOURS)
  1 — plane is dead (no pending/active AND last activity older than
      STALE_HOURS)
  2 — store unreachable (error, not empty)
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HANDOFF_ROOT = REPO / "data" / "handoff"
STALE_HOURS = 24  # SLO: plane must show activity within this window


def _parse_ts(s: str | None) -> float | None:
    if not s:
        return None
    try:
        # Handle ISO 8601 with or without Z
        s = s.replace("Z", "+00:00")
        return datetime.fromisoformat(s).timestamp()
    except (ValueError, TypeError):
        return None


def main() -> int:
    if not HANDOFF_ROOT.is_dir():
        print(f"ERROR: handoff root not found: {HANDOFF_ROOT}", file=sys.stderr)
        return 2

    pending_dir = HANDOFF_ROOT / "pending"
    stale_dir = HANDOFF_ROOT / "stale"

    pending_count = 0
    active_count = 0
    newest_ts = None

    # Count pending
    if pending_dir.is_dir():
        for f in pending_dir.glob("*.json"):
            try:
                env = json.loads(f.read_text())
                pending_count += 1
                for key in ("created_at_utc", "submitted_at", "last_event_at_utc"):
                    t = _parse_ts(env.get(key))
                    if t and (newest_ts is None or t > newest_ts):
                        newest_ts = t
            except (OSError, ValueError):
                continue

    # Count active (hot/)
    hot_dir = HANDOFF_ROOT / "hot"
    if hot_dir.is_dir():
        for f in hot_dir.glob("*.json"):
            try:
                env = json.loads(f.read_text())
                active_count += 1
                for key in ("created_at_utc", "submitted_at", "last_event_at_utc"):
                    t = _parse_ts(env.get(key))
                    if t and (newest_ts is None or t > newest_ts):
                        newest_ts = t
            except (OSError, ValueError):
                continue

    # Also check stale for newest activity
    if stale_dir.is_dir():
        for f in stale_dir.glob("*.json"):
            try:
                env = json.loads(f.read_text())
                for key in ("created_at_utc", "submitted_at", "last_event_at_utc", "reaped_at"):
                    t = _parse_ts(env.get(key))
                    if t and (newest_ts is None or t > newest_ts):
                        newest_ts = t
            except (OSError, ValueError):
                continue

    now = time.time()
    age_hours = (now - newest_ts) / 3600 if newest_ts else float("inf")

    print(f"Handoff plane liveness:")
    print(f"  pending:  {pending_count}")
    print(f"  active:   {active_count}")
    print(f"  newest activity: {datetime.fromtimestamp(newest_ts, tz=timezone.utc).isoformat() if newest_ts else 'NONE'}")
    print(f"  age: {age_hours:.1f} hours (SLO: {STALE_HOURS}h)")

    if pending_count == 0 and active_count == 0:
        if age_hours > STALE_HOURS:
            print(f"  STATUS: DEAD — no pending/active packets, last activity {age_hours:.1f}h ago (>{STALE_HOURS}h)")
            return 1
        else:
            print(f"  STATUS: IDLE — no pending/active but recent activity ({age_hours:.1f}h ago)")
            return 0
    else:
        print(f"  STATUS: ALIVE — {pending_count} pending, {active_count} active")
        return 0


if __name__ == "__main__":
    sys.exit(main())
