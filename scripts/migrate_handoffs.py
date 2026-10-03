#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""Migrate the legacy handoff corpus into the four-directory contract.

Roc's ruling (`FEDERATION_CONTRACT_REFACTOR_20260928.md` §8, CHANGE 5):
the 1,214 legacy files migrate to `cold/legacy-*`, **NOT** to `retired/`.
`retired/` is a USER decision. *"Never infer retirement from age or from a
legacy directory name."* The existing `archive/` directory must not become
`retired/` by name equivalence — that is precisely the collision being fixed.

THE CENSUS IS NOT A REPORT
--------------------------
It is the reconciliation baseline. `pre_migration_ids` is taken from the census
and compared to `post_migration_ids` AFTERWARDS, exactly. Approximate equality
is not reconciliation.

IDEMPOTENCE
-----------
Keyed on `packet_id`. A second run finds everything already migrated and does
nothing. Re-running must never be a way to lose data.

ORDER PER PACKET
----------------
write temp -> fsync -> recompute SHA-256 and compare against the census ->
write receipt + provenance -> atomic rename -> update index -> only then
retire the source name.

NEVER DELETES
-------------
`retire the source name` means a rename into the destination tree, not an
unlink. Nothing here can remove a packet.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mcp_servers.omega_hub.federation_envelope import (  # noqa: E402
    LEGACY_CLASSIFICATION, HANDOFF_COLD, HANDOFF_HOT, HANDOFF_RETIRED,
    write_atomic,
)

REPO = Path(__file__).resolve().parent.parent
# The ruled-on layout lives INSIDE data/handoff/. An earlier version of this
# script targeted `data/handoffs/` — a different directory with an extra "s" —
# so its 1451 copies sit in a tree that is not the contract. Nothing was lost
# (the sources were copied, never moved), but that tree is superseded and must
# not be mistaken for the migration's output.
DEST_NAME = "handoff_migrated"
LEGACY_ROOT = REPO / "data" / "handoff"
DEST = REPO / "data" / "handoff"          # hot/ cold/ envelopes/ retired/ land here
CENSUS_PATH = LEGACY_ROOT / "MIGRATION_CENSUS_20260929.json"
RECEIPTS = LEGACY_ROOT / ".receipts"
INDEX_PATH = REPO / "data" / "handoff_index.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _load_index() -> dict:
    """Existing handoff index, if any. Recorded per packet as `index_entry`."""
    if not INDEX_PATH.is_file():
        return {}
    try:
        data = json.loads(INDEX_PATH.read_text())
    except (OSError, ValueError):
        return {}
    if isinstance(data, dict):
        return {k: v for k, v in data.items() if not k.startswith("_")}
    if isinstance(data, list):
        out = {}
        for row in data:
            if isinstance(row, dict) and row.get("packet_id"):
                out[row["packet_id"]] = row
        return out
    return {}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def classify(src_dir_name: str, packet: dict) -> str:
    """Destination, per Roc's ruling. NEVER inferred from a name at runtime.

    The legacy `archive/` directory maps to `cold/legacy-archive`. It does NOT
    map to `retired/` — that is the whole point of the ruling.
    """
    status = str(packet.get("status") or "").lower()
    # An EXPLICIT user-retirement flag is the only thing that reaches retired/.
    if packet.get("retired_by_user") is True:
        return HANDOFF_RETIRED
    key = src_dir_name.lower()
    if key in LEGACY_CLASSIFICATION:
        return LEGACY_CLASSIFICATION[key]
    if status in LEGACY_CLASSIFICATION:
        return LEGACY_CLASSIFICATION[status]
    return LEGACY_CLASSIFICATION["unknown"]


def census() -> dict:
    """Baseline: id, dir, status, size, SHA-256, timestamp, index entry, target.

    [maat 2026-09-29] RECURSIVE, and the fix is load-bearing. The first version
    globbed only the top level of each queue, so it silently missed
    `archive/M36-test-spam-20260928/` (757 packets that Kali archived under the
    M36 ruling). A census that under-counts is worse than no census: it becomes
    the reconciliation baseline, and anything it does not name is invisible to
    the "no unclassified file outside the census" check — the one check that
    would have caught it.

    `classify()` keys on the TOP-LEVEL queue name, never the nested subdirectory,
    so Kali's M36 archive classifies as `cold/legacy-archive` — which is right:
    it IS in `archive/`, and per Roc's ruling a legacy directory name never
    reaches `retired/`.
    """
    rows = []
    index = _load_index()
    if not LEGACY_ROOT.is_dir():
        return {"created_at_utc": _now(), "count": 0, "pre_migration_ids": [], "rows": []}
    for src in sorted(p for p in LEGACY_ROOT.iterdir() if p.is_dir()):
        if src.name in (DEST_NAME, ".receipts"):
            continue
        for f in sorted(src.rglob("*.json")):
            if DEST_NAME in f.relative_to(LEGACY_ROOT).parts:
                continue  # never re-ingest our own destination tree
            if f.name.upper().startswith(("MANIFEST", "MIGRATION_", "README", "INDEX")):
                continue  # a manifest is not a packet
            try:
                packet = json.loads(f.read_text())
            except (OSError, ValueError):
                packet = {}
            pid = packet.get("packet_id") or f.stem
            rows.append({
                "packet_id": pid,
                "source": str(f.relative_to(REPO)),
                "src_dir": src.name,
                "src_subdir": str(f.parent.relative_to(src)) if f.parent != src else "",
                "status": packet.get("status"),
                "size": f.stat().st_size,
                "sha256": _sha256(f),
                "mtime_utc": datetime.fromtimestamp(
                    f.stat().st_mtime, tz=timezone.utc).isoformat(timespec="seconds"),
                "index_entry": index.get(pid) is not None,
                "target": classify(src.name, packet),
            })
    return {
        "created_at_utc": _now(),
        "count": len(rows),
        "pre_migration_ids": sorted({r["packet_id"] for r in rows}),
        "rows": rows,
    }


def reconcile(cen: dict) -> dict:
    """Exact equality, plus per-packet integrity. Never approximate."""
    pre = set(cen["pre_migration_ids"])
    post, problems = set(), []

    dest_root = DEST
    for r in cen["rows"]:
        target = dest_root / r["target"] / Path(r["source"]).name
        if not target.is_file():
            problems.append(f"missing destination: {r['target']}/{Path(r['source']).name}")
            continue
        post.add(r["packet_id"])
        got = _sha256(target)
        if got != r["sha256"]:
            problems.append(f"sha mismatch for {r['packet_id']}")
        if not (RECEIPTS / f"{r['packet_id']}.receipt.json").is_file():
            problems.append(f"no receipt for {r['packet_id']}")

    missing = pre - post
    extra = post - pre
    for p in sorted(missing):
        problems.append(f"PRE but not POST: {p}")
    for p in sorted(extra):
        problems.append(f"POST but not PRE (unreferenced): {p}")

    return {
        "pre_count": len(pre),
        "post_count": len(post),
        "pre_equals_post": pre == post,
        "missing": sorted(missing),
        "extra": sorted(extra),
        "problems": problems,
        "ok": pre == post and not problems,
    }


def migrate(cen: dict, apply: bool) -> dict:
    moved = skipped = 0
    receipts = {}
    for r in cen["rows"]:
        src = REPO / r["source"]
        dst = DEST / r["target"] / src.name
        if dst.is_file():
            skipped += 1  # idempotent: already migrated
            continue
        if not apply:
            moved += 1
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        tmp = dst.with_name(dst.name + ".mig.tmp")
        shutil.copy2(src, tmp)          # copy, never move: source stays until verified
        with open(tmp, "rb+") as fh:    # fsync before the rename
            os.fsync(fh.fileno())
        if _sha256(tmp) != r["sha256"]:
            tmp.unlink()
            raise SystemExit(f"FATAL: sha mismatch during copy of {r['packet_id']}")
        os.replace(tmp, dst)            # atomic rename into place
        write_atomic(RECEIPTS / f"{r['packet_id']}.receipt.json", json.dumps({
            "packet_id": r["packet_id"],
            "from": r["source"],
            "to": str(dst.relative_to(REPO)),
            "sha256": r["sha256"],
            "migrated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "provenance": "migrate_handoffs",
            "classification_basis": "Roc ruling: legacy name -> cold/legacy-*, "
                                   "never retired/ by name equivalence",
        }, indent=2, sort_keys=True))
        receipts[r["packet_id"]] = str(dst.relative_to(REPO))
        moved += 1
    return {"moved": moved, "skipped_already_migrated": skipped, "receipts": len(receipts)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Legacy handoff migration (Roc ruling)")
    ap.add_argument("--census", action="store_true", help="census only, write baseline")
    ap.add_argument("--apply", action="store_true", help="perform the migration")
    ap.add_argument("--reconcile", action="store_true", help="compare pre vs post exactly")
    ap.add_argument("--root", default=None)
    a = ap.parse_args(argv)

    global DEST
    if a.root:
        DEST = Path(a.root).resolve()

    if a.census or (not a.apply and not a.reconcile):
        cen = census()
        DEST.mkdir(parents=True, exist_ok=True)
        write_atomic(CENSUS_PATH, json.dumps(cen, indent=2, sort_keys=True))
        print(f"census: {cen['count']} packets, {len(cen['pre_migration_ids'])} unique ids")
        from collections import Counter
        for t, n in sorted(Counter(r["target"] for r in cen["rows"]).items()):
            print(f"  {t:34} {n}")
        print(f"  baseline -> {CENSUS_PATH.relative_to(REPO)}")
        return 0

    if a.apply:
        if not CENSUS_PATH.is_file():
            print("FAIL: no census. Run --census first; migration is baseline-driven.")
            return 1
        cen = json.loads(CENSUS_PATH.read_text())
        res = migrate(cen, apply=True)
        print(f"migrated: {res['moved']}  already-migrated(skipped): "
              f"{res['skipped_already_migrated']}  receipts: {res['receipts']}")
        return 0

    if a.reconcile:
        if not CENSUS_PATH.is_file():
            print("FAIL: no census to reconcile against")
            return 1
        cen = json.loads(CENSUS_PATH.read_text())
        res = reconcile(cen)
        print(f"reconcile: pre={res['pre_count']} post={res['post_count']} "
              f"pre_equals_post={res['pre_equals_post']} ok={res['ok']}")
        for p in res["problems"][:10]:
            print(f"  PROBLEM: {p}")
        return 0 if res["ok"] else 2

    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
