#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""M15 continuity tooling: archive-before-overwrite + provenance stamping.

THE PROBLEM THIS SOLVES
-----------------------
Every entity's `session_gnosis.md` was being overwritten wholesale each
session, so the prior state was unrecoverable. A gnosis is the M15 continuity
anchor: it is the only record of what a session knew before compaction. Losing
it silently means the next session inherits an assertion it cannot check.

THE RULE
--------
Any agent about to write a gnosis runs this FIRST:

    .venv/bin/python scripts/gnosis_archive.py archive --entity maat

That copies the current file into `data/entities/<entity>/gnosis/archive/`
BEFORE the overwrite. Then write the new gnosis, then:

    .venv/bin/python scripts/gnosis_archive.py stamp --entity maat

`stamp` inserts a machine-readable provenance header recording what it
superseded, so a reader can always walk back through the chain.

M23 — NEVER CLOBBER. If the archive target already exists the tool refuses to
overwrite it and appends a seconds-precision suffix instead, reporting the
name it actually used. Losing a continuity record to a name collision is the
exact failure this tool exists to prevent.

HEADER FORMAT — why an HTML comment
----------------------------------
The header is an HTML comment block placed immediately AFTER the existing SPDX
comment. Chosen after verifying what the gates actually read:

  * `make doc-llm-validate` runs `validate_llm_docs.py` against
    `docs/sprints/current/` ONLY — it never reads `data/entities/`. So a
    frontmatter block here would not be validated, and adding real YAML
    frontmatter would risk confusing generic YAML tooling for no benefit.
  * `scripts/validate_soul.py` does not reference session_gnosis.
  * `scripts/validate_tracking_state.py` (make check-tracking-state) does not
    read gnoses either.
  * REUSE compliance is driven by REUSE.toml plus the in-file SPDX comment,
    which we preserve in place at the top.

An HTML comment is invisible to every markdown renderer, survives all three
gates untouched, and is trivial for a model to read. Real YAML frontmatter was
the alternative and was rejected on those grounds.

MODES
-----
  archive  copy the current gnosis into the archive (no-clobber)
  stamp    insert/refresh the provenance header on the current gnosis
  verify   fleet-wide audit; exit non-zero if any gnosis is unstamped
"""

from __future__ import annotations

import argparse
import getpass
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENTITIES_DIR = REPO_ROOT / "data" / "entities"
SCHEMA_VERSION = "1.0.0"

# Header markers. BEGIN/END let `stamp` be idempotent: re-stamping replaces the
# existing block in place rather than stacking a second one.
BEGIN = "<!-- GNOSIS-META:BEGIN"
END = "<!-- GNOSIS-META:END -->"

META_RE = re.compile(
    re.escape(BEGIN) + r".*?" + re.escape(END), re.S
)

# ── adoption (2026-09-28) ────────────────────────────────────────────────────
# The archive regime did not exist before 2026-09-28. Gnoses written before
# then were overwritten wholesale and their prior states are gone. Rather than
# leave 38 gnoses silently unstamped (a gate that is red for no legible reason)
# or back-date headers to fake a history that never existed (a fabricated audit
# record), we stamp FORWARD with the truth:
#
#     supersedes: adoption-2026-09-28
#
# which is explicitly NOT a filename. It states that no prior archive exists
# because the archive regime did not exist. Entities that had already lost
# history get an additional `history_lost` line naming that fact, so the loss
# is visible in the record instead of merely absent from it.
ADOPTION_ID = "adoption-2026-09-28"
HISTORY_LOST_NOTE = (
    "pre-regime; prior states were overwritten before versioning began"
)
# An entity is "at risk" when its gnosis already documents multiple sessions
# yet retains no archive — i.e. earlier states demonstrably existed and are gone.
AT_RISK_MIN_SESSION_ROWS = 2

# Dated session-history table rows, used to detect that multi-session history exists.
SESSION_ROW_RE = re.compile(r"^\|\s*20\d\d-\d\d-\d\d\s*\|", re.M)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def entity_dir(entity: str) -> Path:
    return ENTITIES_DIR / entity


def gnosis_path(entity: str) -> Path:
    return entity_dir(entity) / "session_gnosis.md"


def archive_dir(entity: str) -> Path:
    return entity_dir(entity) / "gnosis" / "archive"


def _stamp_now() -> str:
    return utc_now().isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_meta(text: str) -> dict[str, str] | None:
    """Return the parsed GNOSIS-META block, or None if absent.

    Keys are emitted as `key: value` so a model can read them directly and a
    regex can recover them without a YAML dependency.
    """
    m = META_RE.search(text)
    if not m:
        return None
    meta: dict[str, str] = {}
    for line in m.group(0).splitlines():
        kv = re.match(r"\s*(?:#\s*)?([a-z_]+):\s*(.+?)\s*$", line)
        if kv and kv.group(1) != "GNOSIS-META":
            meta[kv.group(1)] = kv.group(2)
    return meta


def latest_archive(entity: str) -> str | None:
    """Newest archive filename for this entity, or None."""
    d = archive_dir(entity)
    if not d.is_dir():
        return None
    cands = sorted(p.name for p in d.glob("session_gnosis_*.md"))
    return cands[-1] if cands else None


def count_archives(entity: str) -> int:
    d = archive_dir(entity)
    if not d.is_dir():
        return 0
    return len(list(d.glob("session_gnosis_*.md")))


# ── mode: archive ────────────────────────────────────────────────────────────

def do_archive(entity: str, dry_run: bool) -> int:
    src = gnosis_path(entity)
    if not src.is_file():
        print(f"FAIL: no gnosis at {src} — nothing to archive", file=sys.stderr)
        return 1

    dest_dir = archive_dir(entity)
    now = utc_now()
    base = now.strftime("session_gnosis_%Y%m%d-%H%M.md")

    dest = dest_dir / base
    if dest.exists():
        # M23: never clobber. Seconds precision, then a counter if still taken.
        stamped = now.strftime("session_gnosis_%Y%m%d-%H%M%S.md")
        dest = dest_dir / stamped
        n = 1
        while dest.exists():
            dest = dest_dir / f"session_gnosis_{now.strftime('%Y%m%d-%H%M%S')}_{n}.md"
            n += 1
        print(f"  note: {base} already exists — using {dest.name} (no clobber)")

    if dry_run:
        print(f"DRY-RUN archive: {src} -> {dest}")
        return 0

    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    print(f"archived: {src.relative_to(REPO_ROOT)} -> {dest.relative_to(REPO_ROOT)}")
    return 0


# ── mode: stamp ──────────────────────────────────────────────────────────────

def build_block(entity: str, stamped_by: str, supersedes: str,
                history_lost: str | None = None) -> str:
    lines = [
        BEGIN,
        f"  entity: {entity}",
        f"  stamped_at: {_stamp_now()}",
        f"  stamped_by: {stamped_by}",
        f"  supersedes: {supersedes}",
        f"  schema_version: {SCHEMA_VERSION}",
    ]
    if history_lost:
        lines.append(f"  history_lost: {history_lost}")
    lines.append(END)
    return "\n".join(lines)


def insert_block(text: str, block: str) -> str:
    """Insert `block` after the leading SPDX comment, or refresh it in place."""
    if META_RE.search(text):
        return META_RE.sub(block, text, count=1)
    lines = text.split("\n")
    insert_at = 0
    if lines and lines[0].lstrip().startswith("<!--"):
        for i, ln in enumerate(lines):
            if "-->" in ln:
                insert_at = i + 1
                break
    while insert_at < len(lines) and lines[insert_at].strip() == "":
        insert_at += 1
    return "\n".join(lines[:insert_at] + block.split("\n") + [""] + lines[insert_at:])


def do_stamp(entity: str, stamped_by: str, supersedes: str | None, dry_run: bool) -> int:
    p = gnosis_path(entity)
    if not p.is_file():
        print(f"FAIL: no gnosis at {p} to stamp", file=sys.stderr)
        return 1

    text = p.read_text(encoding="utf-8")
    existing = parse_meta(text)
    if supersedes is None:
        # Default: whatever archive exists right now; 'none' for a first write.
        arch = latest_archive(entity)
        supersedes = arch if arch else "none"

    block = build_block(entity, stamped_by, supersedes)

    # Preserve an existing `history_lost` line across refreshes. The pre-regime
    # loss is a permanent property of an entity's history: once an entity has
    # ONE archive it stops appearing in at_risk_entities(), so a later `stamp`
    # would otherwise silently erase the only record that earlier states were
    # lost. That is precisely the silent-data-loss failure this tooling exists
    # to prevent, and it would have recurred on the very next session.
    #
    # Two sources, in order of authority:
    #   1. the current file's own header (already there -> just carry it)
    #   2. the newest archived copy, which is immutable and retains the line
    # Note we must NOT gate the archive scan on the current file having the
    # line: that is circular, because the current file is precisely what lost
    # it. (First draft of this bug did exactly that and silently no-opped.)
    prior = parse_meta(text) or {}
    history_lost = prior.get("history_lost")
    if not history_lost:
        ad = archive_dir(entity)
        if ad.is_dir():
            for cand in sorted(ad.glob("session_gnosis_*.md"), reverse=True):
                try:
                    pm = parse_meta(cand.read_text(encoding="utf-8"))
                except OSError:
                    continue
                if pm and pm.get("history_lost"):
                    history_lost = pm["history_lost"]
                    break
    if history_lost:
        block = build_block(entity, stamped_by, supersedes, history_lost)

    if META_RE.search(text):
        new_text = META_RE.sub(block, text, count=1)
        action = "refreshed"
    else:
        new_text = insert_block(text, block)
        action = "inserted"

    if dry_run:
        print(f"DRY-RUN stamp: would {action} header in {p.relative_to(REPO_ROOT)}")
        print("--- would write ---")
        print(block)
        return 0

    p.write_text(new_text, encoding="utf-8")
    print(f"{action} stamp: {p.relative_to(REPO_ROOT)} (supersedes={supersedes})")
    return 0


# ── mode: adopt ──────────────────────────────────────────────────────────────

def at_risk_entities() -> dict[str, int]:
    """Entities whose gnosis shows multi-session history but retains no archive.

    That combination is proof that earlier states existed and are gone — the
    exact loss the `history_lost` line is meant to make visible.
    """
    out: dict[str, int] = {}
    for e in all_entities():
        p = gnosis_path(e)
        if not p.is_file():
            continue
        if count_archives(e) > 0:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        n = len(SESSION_ROW_RE.findall(text))
        if n >= AT_RISK_MIN_SESSION_ROWS:
            out[e] = n
    return out


def do_adopt(stamped_by: str, dry_run: bool) -> int:
    """Stamp every UNSTAMPED gnosis forward, truthfully.

    Idempotent: only unstamped files are touched, so a second run finds nothing
    to do and exits 0. Archives nothing — there is nothing to archive for a
    first write, and archiving now would fabricate a pre-regime history.
    Header insert only; gnosis content is never rewritten.
    """
    risk = at_risk_entities()
    targets: list[Path] = []
    for e in all_entities():
        p = gnosis_path(e)
        if not p.is_file():
            continue
        try:
            if parse_meta(p.read_text(encoding="utf-8")) is None:
                targets.append(p)
        except OSError:
            print(f"  warn: unreadable {p} — skipped", file=sys.stderr)

    at_risk_here = [p for p in targets if p.parent.name in risk]
    normal_here = [p for p in targets if p.parent.name not in risk]

    print(f"adoption stamp: {ADOPTION_ID}  by={stamped_by}  dry_run={dry_run}")
    print(f"  unstamped gnoses to adopt : {len(targets)}")
    print(f"    of which at-risk        : {len(at_risk_here)} "
          f"({', '.join(sorted(p.parent.name for p in at_risk_here)) or 'none'})")
    print(f"    normal (no lost history): {len(normal_here)}")

    if not targets:
        print("  nothing to adopt (already idempotent — no unstamped gnoses)")
        return 0

    for label, sample in (("AT-RISK", at_risk_here[:1]), ("NORMAL", normal_here[:1])):
        if not sample:
            continue
        p = sample[0]
        note = HISTORY_LOST_NOTE if label == "AT-RISK" else None
        block = build_block(p.parent.name, stamped_by, ADOPTION_ID, note)
        print(f"\n  --- example header for a {label} entity "
              f"({p.parent.name}) ---")
        print("  " + block.replace("\n", "\n  "))

    if dry_run:
        print(f"\nDRY-RUN: no files written. Would adopt {len(targets)} gnosis file(s).")
        return 0

    written = 0
    for p in targets:
        ent = p.parent.name
        note = HISTORY_LOST_NOTE if ent in risk else None
        text = p.read_text(encoding="utf-8")
        block = build_block(ent, stamped_by, ADOPTION_ID, note)
        p.write_text(insert_block(text, block), encoding="utf-8")
        written += 1
        if note:
            print(f"  adopted (history_lost recorded): {ent}")
    print(f"\nadopted {written} gnosis file(s); "
          f"{len(at_risk_here)} carry an explicit history_lost line.")
    return 0


# ── mode: verify ─────────────────────────────────────────────────────────────

def all_entities() -> list[str]:
    if not ENTITIES_DIR.is_dir():
        return []
    return sorted(p.name for p in ENTITIES_DIR.iterdir() if p.is_dir())


def do_verify() -> int:
    entities = all_entities()
    unstamped: list[str] = []
    no_archive: list[str] = []
    unparseable: list[str] = []

    print(f"Verifying {len(entities)} entity gnoses...\n")

    for e in entities:
        p = gnosis_path(e)
        if not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except OSError as exc:
            unparseable.append(f"{e}: unreadable ({exc})")
            continue

        meta = parse_meta(text)
        if meta is None:
            unstamped.append(e)
        else:
            missing = [k for k in ("entity", "stamped_at", "schema_version") if k not in meta]
            if missing:
                unparseable.append(f"{e}: header missing {','.join(missing)}")

        # Modified more than once but no archive retained => history was lost.
        if count_archives(e) == 0:
            n_entries = len(re.findall(r"^\|\s*20\d\d-\d\d-\d\d\s*\|", text, re.M))
            if n_entries >= 2:
                no_archive.append(f"{e}: {n_entries} session rows, 0 archives")

    print(f"  unstamped            : {len(unstamped)}")
    print(f"  unparseable header   : {len(unparseable)}")
    print(f"  history at risk      : {len(no_archive)}")

    for e in unstamped:
        print(f"    UNSTAMPED          {e}")
    for e in unparseable:
        print(f"    UNPARSEABLE        {e}")
    for e in no_archive:
        print(f"    AT-RISK            {e}")

    # M23: a gnosis with no provenance header cannot be audited, so this fails.
    if unstamped:
        print(f"\nFAIL: {len(unstamped)} unstamped gnosis file(s).", file=sys.stderr)
        return 1
    print("\nOK: all gnoses stamped.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="M15 gnosis archive/stamp/verify")
    ap.add_argument("mode", choices=("archive", "stamp", "verify", "adopt"))
    ap.add_argument("--entity", help="entity name (not used by verify/adopt)")
    ap.add_argument("--by", dest="stamped_by",
                    default=None, help="stamped_by; defaults to $USER")
    ap.add_argument("--supersedes", default=None,
                    help="archive filename this replaces (default: newest archive)")
    ap.add_argument("--dry-run", action="store_true",
                    help="show what would happen; mutate nothing")
    args = ap.parse_args(argv)

    if args.mode == "verify":
        return do_verify()

    who = args.stamped_by or os.environ.get("USER") or getpass.getuser()

    if args.mode == "adopt":
        if args.entity:
            ap.error("--entity is not used by adopt (it is fleet-wide)")
        return do_adopt(who, args.dry_run)

    if not args.entity:
        ap.error(f"--entity is required for {args.mode}")

    if args.mode == "archive":
        return do_archive(args.entity, args.dry_run)

    return do_stamp(args.entity, who, args.supersedes, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
