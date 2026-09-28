#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""M15 continuity tooling: turn per-entity gnosis prose into a fleet timeline.

The gnoses already contain dense session-history tables:

    | 2026-09-25 | maat_gates_20260925 | **Summary** ... |

Today that history is prose a human must read by hand across 40 files. This
tool extracts it, orders it fleet-wide newest-first, and adds two integrity
signals that are genuinely useful rather than decorative:

  * ORPHAN SESSION IDS — a session id cited in a gnosis that does not exist in
    the OpenCode session DB. That is a broken continuity reference: the record
    points at a session that was pruned, renamed, or never existed. It is the
    same class of defect as the import seam — a reference that resolves to
    nothing. The DB is opened READ-ONLY (`file:...?mode=ro`); a 45 GB file is
    never a thing to mutate by accident.

  * STALE ENTITIES — newest gnosis entry older than N days. This is the
    freshness signal the oversoul pulse needs.

M1: no `asyncio` import. M24: run under `.venv/bin/python`.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENTITIES_DIR = REPO_ROOT / "data" / "entities"
DB_PATH = Path.home() / ".local/share/opencode/opencode.db"

# | 2026-09-25 | maat_gates_20260925 | summary ... |
ROW_RE = re.compile(
    r"^\|\s*(?P<date>20\d\d-\d\d-\d\d)\s*\|\s*"
    r"(?P<sid>[A-Za-z0-9_.\-]+)\s*\|\s*(?P<summary>.*?)\s*\|\s*$",
    re.M,
)
# Dated headings, used only when a file yields no table rows.
HEAD_RE = re.compile(r"^#{1,6}\s*(?P<date>20\d\d-\d\d-\d\d)\b.*$", re.M)
SESSION_ID_RE = re.compile(r"\bses_[A-Za-z0-9]{8,}\b")


def gnosis_files(entity: str | None) -> list[tuple[str, Path]]:
    """(entity, path) for every gnosis: both the legacy and new locations."""
    out: list[tuple[str, Path]] = []
    ents = [entity] if entity else sorted(
        p.name for p in ENTITIES_DIR.iterdir() if p.is_dir()
    ) if ENTITIES_DIR.is_dir() else []
    for e in ents:
        for cand in (
            ENTITIES_DIR / e / "session_gnosis.md",
            ENTITIES_DIR / e / "gnosis" / "session_gnosis.md",
        ):
            if cand.is_file():
                out.append((e, cand))
    return out


def parse_gnosis(entity: str, path: Path) -> list[dict]:
    """Extract dated entries from one gnosis. Table rows win; headings fallback."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"warn: unreadable {path}: {exc}", file=sys.stderr)
        return []

    entries: list[dict] = []
    for m in ROW_RE.finditer(text):
        entries.append({
            "entity": entity,
            "date": m.group("date"),
            "session_id": m.group("sid"),
            "summary": re.sub(r"\s+", " ", m.group("summary"))[:300],
            "source": str(path.relative_to(REPO_ROOT)),
            "kind": "table-row",
        })

    if not entries:
        for m in HEAD_RE.finditer(text):
            d = m.group("date")
            # Associate any session id mentioned on the heading's own line.
            sid_match = SESSION_ID_RE.search(m.group(0))
            entries.append({
                "entity": entity,
                "date": d,
                "session_id": sid_match.group(0) if sid_match else None,
                "summary": m.group(0).lstrip("# ").strip()[:300],
                "source": str(path.relative_to(REPO_ROOT)),
                "kind": "heading",
            })
    return entries


def known_session_ids() -> set[str] | None:
    """All session ids in the OpenCode DB, opened READ-ONLY. None if unavailable."""
    if not DB_PATH.is_file():
        return None
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, timeout=5)
        try:
            return {r[0] for r in con.execute("SELECT id FROM session")}
        finally:
            con.close()
    except sqlite3.Error as exc:
        print(f"warn: cannot read session DB: {exc}", file=sys.stderr)
        return None


def newest_per_entity(entries: list[dict]) -> dict[str, str]:
    newest: dict[str, str] = {}
    for e in entries:
        d = e["date"]
        if e["entity"] not in newest or d > newest[e["entity"]]:
            newest[e["entity"]] = d
    return newest


def _parse_date(s: str) -> date | None:
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def render_md(entries: list[dict], orphan: dict[str, list[str]],
              stale: dict[str, int] | None) -> str:
    lines: list[str] = ["# Fleet Gnosis Timeline", ""]
    if not entries:
        lines.append("_No dated gnosis entries found._")
        return "\n".join(lines)

    by_date: dict[str, list[dict]] = {}
    for e in entries:
        by_date.setdefault(e["date"], []).append(e)

    lines.append("| Date | Entity | Session ID | Summary |")
    lines.append("|---|---|---|---|")
    for d in sorted(by_date, reverse=True):
        for e in sorted(by_date[d], key=lambda x: (x["entity"], x["session_id"] or "")):
            sid = e["session_id"] or "—"
            summary = e["summary"].replace("|", "\\|")
            lines.append(f"| {d} | {e['entity']} | `{sid}` | {summary} |")

    if orphan:
        lines += ["", "## Orphan Session IDs", "",
                  "Cited in a gnosis but absent from the OpenCode session DB —",
                  "broken continuity references.", "",
                  "| Entity | Session ID |", "|---|---|"]
        for ent in sorted(orphan):
            for sid in sorted(orphan[ent]):
                lines.append(f"| {ent} | `{sid}` |")

    if stale:
        lines += ["", f"## Stale Entities (no entry in > N days)", "",
                  "| Entity | Newest Entry | Age (days) |", "|---|---|---|"]
        for ent, age in sorted(stale.items(), key=lambda kv: -kv[1]):
            lines.append(f"| {ent} | {newest_per_entity(entries)[ent]} | {age} |")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Fleet gnosis timeline")
    ap.add_argument("--entity", help="filter to one entity")
    ap.add_argument("--since", help="YYYY-MM-DD (inclusive)")
    ap.add_argument("--until", help="YYYY-MM-DD (inclusive)")
    ap.add_argument("--format", choices=("md", "json"), default="md")
    ap.add_argument("--stale-days", type=int, default=None,
                    help="list entities whose newest entry is older than N days")
    ap.add_argument("--no-orphan-check", action="store_true",
                    help="skip the session-DB orphan check")
    args = ap.parse_args(argv)

    entries: list[dict] = []
    for ent, path in gnosis_files(args.entity):
        entries.extend(parse_gnosis(ent, path))

    since = _parse_date(args.since) if args.since else None
    until = _parse_date(args.until) if args.until else None
    if since or until:
        keep = []
        for e in entries:
            d = _parse_date(e["date"])
            if d is None:
                continue
            if since and d < since:
                continue
            if until and d > until:
                continue
            keep.append(e)
        entries = keep

    # Orphan check: any session-id-shaped token anywhere in the gnosis, not just
    # table cells, so ids mentioned in prose are caught too.
    orphan: dict[str, list[str]] = {}
    if not args.no_orphan_check:
        known = known_session_ids()
        if known is None:
            print("warn: session DB unavailable — orphan check skipped", file=sys.stderr)
        else:
            for ent, path in gnosis_files(args.entity):
                try:
                    text = path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                for sid in set(SESSION_ID_RE.findall(text)):
                    if sid not in known:
                        orphan.setdefault(ent, []).append(sid)

    # Newest first, for EVERY output format. Previously only the markdown
    # renderer sorted; JSON emitted file order, so `--format json` silently
    # disagreed with `--format md`. Caught by tests/test_gnosis_tools.py.
    entries.sort(key=lambda e: (e["date"], e["entity"], e["session_id"] or ""),
                 reverse=True)

    stale: dict[str, int] | None = None
    if args.stale_days is not None:
        today = date.today()
        stale = {}
        for ent, newest in newest_per_entity(entries).items():
            d = _parse_date(newest)
            if d is None:
                continue
            age = (today - d).days
            if age > args.stale_days:
                stale[ent] = age

    if args.format == "json":
        print(json.dumps({
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "entries": entries,
            "orphan_session_ids": orphan,
            "stale_entities": stale,
        }, indent=2))
    else:
        print(render_md(entries, orphan, stale))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
