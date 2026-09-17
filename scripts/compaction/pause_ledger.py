#!/usr/bin/env python3
"""pause_ledger.py — the Pause Ledger: visibility of every gnosis pack.

Each gnosis-lock creates a PACK (session artifacts + narrative + manifest) that
moves through a lifecycle:

    CAPTURED  →  REFLECTED  →  COMPACTED
    (ritual,     (skill fills   (plugin injects
     TODO by      narrative,     into a /compact)
     intent)      flips status)      )

This tool prints the full ledger: for every pack, its state, who locked it
(entity/channel/phase), when events happened, and whether the leash (pending
un-reflected pack) is currently slack or taut.

Exit codes: 0 = healthy, 1 = degraded (a pack is stuck CAPTURED or the leash
is taut with a pending pack that was never reflected before a later pack).

Pure stdlib, sync, no network.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HOME = Path(__file__).resolve().parents[2]
GNOSIS = HOME / "gnosis"
SESSIONS_DIR = GNOSIS / "sessions"
IDENTITY_FILE = GNOSIS / "identity" / "identity.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text("utf-8"))
    except Exception:
        return default


def main() -> int:
    problems: list[str] = []
    print(f"Pause Ledger @ {now_iso()}")
    print(f"{'PACK (session_id)':<38} {'STATE':<10} {'ENTITY':<12} {'PHASE':<10} {'CAPTURED':<21} {'REFLECTED':<21}")
    print("-" * 130)

    packs = []
    for manifest in sorted(SESSIONS_DIR.glob("*_manifest.json")):
        m = load_json(manifest, {})
        sid = m.get("session_id", manifest.stem.replace("_manifest", ""))
        packs.append(
            {
                "sid": sid,
                "status": m.get("reflection_status", "captured"),
                "entity": m.get("entity", "?"),
                "phase": m.get("phase", "unset"),
                "captured": m.get("timestamp", "?"),
                "reflected_at": m.get("reflected_at", "") or "",
                "triaged": "triage_at" in m,
            }
        )

    if not packs:
        print("  (no packs yet — run gnosis-lock to create the first)")
        return 0

    for p in packs:
        print(
            f"{p['sid']:<38} {p['status']:<10} {p['entity']:<12} {p['phase']:<10} "
            f"{p['captured']:<21} {p['reflected_at']:<21}"
        )
    print("-" * 130)

    # Lifecycle integrity checks
    # A CAPTURED pack is a problem ONLY if it is an implicit loose end. Legacy
    # packs triaged by migrate_legacy_packs.py carry `triage_at` — an explicit,
    # recorded decision to leave them captured (or superseded). Those resolve.
    # Untriaged captured packs are genuine loose ends; the leash governs them.
    loose_captured = [
        p for p in packs
        if p["status"] == "captured" and not p["triaged"]
    ]
    if loose_captured:
        oldest = min(loose_captured, key=lambda p: p["captured"])
        problems.append(
            f"{len(loose_captured)} untriaged pack(s) still CAPTURED — oldest: "
            f"{oldest['sid']} captured {oldest['captured']}. "
            f"Run /gnosis-lock to reflect it, or triage it explicitly "
            f"(migrate_legacy_packs.py for legacy, or set reflection_status)."
        )

    triaged_captured = sum(1 for p in packs if p["status"] == "captured" and p["triaged"])
    if triaged_captured:
        print(f"note     : {triaged_captured} legacy pack(s) explicitly triaged as captured "
              f"(triage_at set) — acknowledged, not loose ends.")

    # Leash check: pending_pack in identity must match a real, un-reflected pack
    identity = load_json(IDENTITY_FILE, {})
    pending = identity.get("pending_pack", "")
    if pending:
        m = SESSIONS_DIR / f"{pending}_manifest.json"
        status = load_json(m, {}).get("reflection_status", "captured") if m.is_file() else "missing"
        if status != "reflected":
            problems.append(
                f"LEASH TAUT — pending_pack {pending} is status={status}. "
                f"The ritual will refuse a new pack until this is reflected."
            )
        else:
            print(f"leash    : identity.pending_pack={pending} but that pack IS reflected — stale pointer")
    else:
        print("leash    : slack (no pending pack)")

    for p in problems:
        print(f"  ✗ {p}")
    print()
    if not problems:
        print("✅ PAUSE LEDGER CLEAN — every pack accounted for, leash slack.")
        return 0
    print("❌ PAUSE LEDGER DEGRADED — fix above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
