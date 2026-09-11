#!/usr/bin/env python3
"""P0.2 — migrate legacy gnosis packs to explicit reflection states.

Every manifest predating the pack state machine lacks `reflection_status`
(and `entity`/`phase`). The ledger (pause_ledger.py) falls back to an implicit
"captured" for missing statuses — the exact "no implicit states" violation
P0.2 exists to close.

This script rewrites each legacy manifest to carry an EXPLICIT state:

  - reflection_status: "superseded"  -> harness/test artifacts, no real
                                         session content (fake session ids,
                                         ritual self-testing). superseded_by
                                         names the reason class.
  - reflection_status: "captured"    -> real work sessions that were never
                                         reflected. Triage fields record the
                                         honest decision: they stay captured
                                         (un-ingested) until/unless reflected.

Idempotent: manifests that already have an explicit reflection_status are
touched only to add triage provenance if missing. Dry-run by default.

Usage:
  python3 scripts/compaction/migrate_legacy_packs.py [--apply]
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SESSIONS_DIR = Path(__file__).resolve().parent.parent.parent / "gnosis" / "sessions"

# Fake/placeholder session ids produced by hook or CLI misuse — pure test junk.
TEST_FIXTURE_IDS = {
    "--session-id",
    "test-session-002",
    "hook-test-002",
    "real-compact-test",
}

# Reasons that describe ritual self-verification rather than real work.
RITUAL_TEST_REASONS = re.compile(
    r"^(test|testing|verifying|verify|final check|final verification)"
    r"|test(ing)? (of|new|make|the)|from /tmp|make target",
    re.IGNORECASE,
)


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def classify(reason: str, session_id: str) -> tuple[str, str]:
    """Return (reflection_status, superseded_by or triage_note)."""
    if session_id in TEST_FIXTURE_IDS:
        return ("superseded", "harness-test-artifact: fake/placeholder session id")
    if RITUAL_TEST_REASONS.search(reason or ""):
        return ("superseded", "harness-test-artifact: ritual self-verification")
    return (
        "captured",
        "legacy: real session, never reflected; left honestly captured until ingested",
    )


def main() -> int:
    apply = "--apply" in sys.argv
    manifests = sorted(SESSIONS_DIR.glob("*_manifest.json"))
    changed: list[tuple[str, str, str]] = []  # (sid, status, note)
    skipped: int = 0

    for mf in manifests:
        data = json.loads(mf.read_text("utf-8"))
        sid = data.get("session_id", mf.stem.replace("_manifest", ""))
        reason = data.get("reason", "")

        # NEVER touch a manifest that already has an explicit reflection_status
        # (the 3 genuinely reflected packs, future rituals, prior migrations).
        # Only pure-legacy manifests (missing the field altogether) are migrated.
        if "reflection_status" in data:
            skipped += 1
            continue

        status, note = classify(reason, sid)

        data["reflection_status"] = status
        if status == "superseded":
            data["superseded_by"] = data.get("superseded_by", note)
            data.pop("reflected_at", None)
        else:
            data["triage_note"] = data.get("triage_note", note)
        data["triage_at"] = now_iso()
        data["triage_script"] = "migrate_legacy_packs.py"

        if apply:
            mf.write_text(json.dumps(data, indent=2) + "\n")
        changed.append((sid, status, note))

    print(f"Legacy pack migration — {'APPLIED' if apply else 'DRY-RUN'}   "
          f"(manifests: {len(manifests)}, already-triaged: {skipped})")
    print(f"{'session_id':<35} {'status':<11} note")
    print("-" * 110)
    for sid, status, note in changed:
        print(f"{sid:<35} {status:<11} {note}")

    n_sup = sum(1 for _, s, _ in changed if s == "superseded")
    n_cap = sum(1 for _, s, _ in changed if s == "captured")
    print("-" * 110)
    print(f"→ {n_sup} superseded (test junk), {n_cap} honestly captured (real sessions).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())