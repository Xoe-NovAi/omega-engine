#!/usr/bin/env python3
# 🔱 soul_promote — Review-gated promotion of staged L3 lessons into soul.yaml
# AP: AP-SOUL-PROMOTE-v1.0.0
# ⬡ OMEGA ⬡ N2 ⬡ soul_promote ⬡ REVIEW-GATED
#
# [M11: Soul Integrity] Closes the one-way door: proposed_lessons.yaml → soul.yaml.
#   M11-class texts promise "promotion requires explicit soul_promote" — this IS it.
# [M13: Temple-Grade] T10 atomic writes; schema guard before replace.
# [C-1' pattern] Atomic write mirrors src/omega/soul_store.py SoulStore:
#   same-dir tempfile → fsync → os.replace → fsync parent dir.
#
# SAFETY MODEL (review-gated):
#   - DRY-RUN by default. Zero mutations without --apply --confirm.
#   - Diff-style preview printed BEFORE any write, in every mode.
#   - Snapshot soul.yaml → soul.yaml.bak.<ISO timestamp> before every apply.
#   - Schema guard: resulting YAML must parse AND contain merged lessons,
#     else abort + restore snapshot. Never leave a half-merged soul.
#
# Usage:
#   python scripts/soul_promote.py <entity> --all            # dry-run preview
#   python scripts/soul_promote.py <entity> --ids ID1,ID2    # dry-run preview
#   python scripts/soul_promote.py <entity> --indices 1,3    # dry-run preview
#   python scripts/soul_promote.py <entity> --all --apply --confirm   # real merge
#
# Exit codes: 0 ok · 1 usage/selection error · 2 merge aborted (schema guard)

"""Review-gated promotion of proposed_lessons.yaml entries into soul.yaml."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

BACKUPS_TO_KEEP = 5
CONTENT_KEYS = ("principle", "insight", "narrative")  # lesson body keys, priority order


class PromotionError(Exception):
    """Fatal promotion failure (selection error, IO error)."""


# ────────────────────────── Loading ──────────────────────────

def entity_paths(entity: str, repo_root: Path | None = None) -> tuple[Path, Path]:
    """Resolve proposed_lessons.yaml and soul.yaml paths for an entity."""
    root = repo_root or Path(__file__).resolve().parent.parent
    base = root / "data" / "entities" / entity
    return base / "proposed_lessons.yaml", base / "soul.yaml"


def load_proposals(path: Path) -> list[dict[str, Any]]:
    """Load the proposals list from a proposed_lessons.yaml file."""
    if not path.exists():
        raise PromotionError(f"No proposal staging file found: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        raise PromotionError(f"Unparseable proposals file {path}: {e}") from e
    proposals = data.get("proposals", [])
    if not isinstance(proposals, list):
        raise PromotionError(f"'proposals' is not a list in {path}")
    return proposals


def select_proposals(
    proposals: list[dict[str, Any]], all_flag: bool, ids: list[str], indices: list[int]
) -> tuple[list[tuple[int, dict[str, Any]]], list[str]]:
    """Select proposals by --all / --ids / --indices.

    Returns (selected as (original_index, proposal) pairs, skip_reports).
    """
    if not all_flag and not ids and not indices:
        raise PromotionError("Nothing selected: pass --all, --ids, or --indices")
    if sum(bool(x) for x in (all_flag, ids, indices)) > 1:
        raise PromotionError("--all, --ids, and --indices are mutually exclusive")

    selected: list[tuple[int, dict[str, Any]]] = []
    skips: list[str] = []

    if all_flag:
        for i, p in enumerate(proposals):
            selected.append((i, p))
    elif ids:
        by_id = {}
        for i, p in enumerate(proposals):
            pid = p.get("id") if isinstance(p, dict) else None
            if isinstance(pid, str):
                by_id[pid] = i
        for want in ids:
            if want in by_id:
                selected.append((by_id[want], proposals[by_id[want]]))
            else:
                skips.append(f"id '{want}' not found in proposals")
    else:  # indices are 1-based positions in the proposals list
        n = len(proposals)
        for idx in indices:
            if 1 <= idx <= n:
                selected.append((idx - 1, proposals[idx - 1]))
            else:
                skips.append(f"index {idx} out of range (1..{n})")

    return selected, skips


# ─────────────────────── Validation & dedupe ───────────────────────

def lesson_body(lesson: dict[str, Any]) -> str | None:
    """Return the first non-empty body text of a lesson, or None."""
    for key in CONTENT_KEYS:
        val = lesson.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return None


def content_hash(text: str) -> str:
    """Stable content hash for dedupe (whitespace-normalized)."""
    normalized = " ".join(text.split()).lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def validate_proposal(p: Any) -> dict[str, Any]:
    """Validate one proposal dict; raise ValueError if malformed."""
    if not isinstance(p, dict):
        raise ValueError("proposal is not a mapping")
    pid = p.get("id")
    if not isinstance(pid, str) or not pid.strip():
        raise ValueError("missing or empty 'id'")
    if lesson_body(p) is None:
        raise ValueError("missing lesson body (need non-empty principle/insight/narrative)")
    return p


def existing_dedupe_keys(soul_data: dict[str, Any]) -> tuple[set[str], set[str]]:
    """Extract dedupe key sets (ids, content hashes) from parsed soul.yaml."""
    ids: set[str] = set()
    hashes: set[str] = set()
    lessons = soul_data.get("lessons")
    if not isinstance(lessons, list):
        return ids, hashes
    for lesson in lessons:
        if not isinstance(lesson, dict):
            continue
        lid = lesson.get("id")
        if isinstance(lid, str):
            ids.add(lid)
        body = lesson_body(lesson)
        if body:
            hashes.add(content_hash(body))
    return ids, hashes


def build_lesson_entry(proposal: dict[str, Any]) -> dict[str, Any]:
    """Build the soul.yaml lesson entry from a validated proposal."""
    tags = proposal.get("tags") or []
    category = tags[0] if isinstance(tags, list) and tags and isinstance(tags[0], str) else "general"
    entry: dict[str, Any] = {
        "id": proposal["id"].strip(),
        "tier": proposal.get("tier", "L3"),
        "category": category,
        "promoted_from": "proposed_lessons.yaml",
        "promoted_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }
    # Body under its original key (principle preferred, then insight/narrative)
    for key in CONTENT_KEYS:
        val = proposal.get(key)
        if isinstance(val, str) and val.strip():
            entry[key] = val.strip()
            break
    # Preserve useful provenance fields when present
    for key in ("mandates", "confidence", "source_session", "directive_provenance"):
        if proposal.get(key) is not None:
            entry[key] = proposal[key]
    return entry


# ─────────────────────── Text-preserving splice ───────────────────────

def dump_lesson_block(entries: list[dict[str, Any]]) -> str:
    """Serialize new lesson entries as an indented YAML list block."""
    block = yaml.safe_dump(entries, default_flow_style=False, allow_unicode=True, width=100)
    return "\n".join("  " + line if line.strip() else line for line in block.rstrip("\n").split("\n"))


def splice_lessons(soul_text: str, block: str) -> str:
    """Insert serialized lessons into the top-level `lessons:` section.

    Preserves all comments/formatting elsewhere in the file. If no top-level
    `lessons:` key exists, appends a new section at end of file.
    """
    lines = soul_text.split("\n")
    insert_at: int | None = None
    for i, line in enumerate(lines):
        if line == "lessons:" or line.startswith("lessons:"):
            insert_at = i
            break

    if insert_at is None:
        # No lessons section yet — append one.
        sep = "" if soul_text.endswith("\n") else "\n"
        return f"{soul_text}{sep}\nlessons:\n{block}\n"

    # Find end of the lessons block: next line starting at column 0 (non-empty),
    # scanning past the optional inline value on the `lessons:` line itself.
    j = insert_at + 1
    while j < len(lines) and (lines[j].startswith((" ", "\t")) or not lines[j].strip()):
        j += 1
    new_lines = lines[:j] + block.split("\n") + lines[j:]
    return "\n".join(new_lines)


# ─────────────────────── Atomic write (SoulStore pattern) ───────────────────────

def atomic_write(path: Path, content: str) -> None:
    """Same-dir tempfile → fsync → os.replace → fsync parent dir.

    Mirrors src/omega/soul_store.py SoulStore.write_atomic (sync variant).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        data = content.encode("utf-8")
        os.write(fd, data)
        try:
            os.fsync(fd)
        except OSError as e:
            raise PromotionError(f"fsync failed on tempfile {tmp_path}: {e} — do NOT retry") from e
        finally:
            os.close(fd)
        os.replace(tmp_path, str(path))
        try:
            parent_fd = os.open(str(path.parent), os.O_RDONLY)
            try:
                os.fsync(parent_fd)
            finally:
                os.close(parent_fd)
        except OSError as e:
            print(f"WARN: parent dir fsync failed for {path}: {e} (data safe)", file=sys.stderr)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


# ─────────────────────── Snapshot management ───────────────────────

def snapshot_soul(soul_path: Path, keep: int = BACKUPS_TO_KEEP) -> Path:
    """Copy soul.yaml → soul.yaml.bak.<ISO timestamp>; prune older, keep last N."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bak = soul_path.with_name(f"{soul_path.name}.bak.{ts}")
    shutil.copy2(str(soul_path), str(bak))
    prune_snapshots(soul_path, keep)
    return bak


def snapshot_backups(soul_path: Path) -> list[Path]:
    """All snapshot backups for this soul.yaml, oldest first."""
    parent = soul_path.parent
    prefix = f"{soul_path.name}.bak."
    baks = sorted(parent.glob(prefix + "*"), key=lambda p: p.name)
    return baks


def prune_snapshots(soul_path: Path, keep: int) -> int:
    """Delete oldest snapshots beyond `keep`. Returns count pruned."""
    baks = snapshot_backups(soul_path)
    pruned = 0
    for old in baks[:-keep] if keep > 0 else baks:
        old.unlink()
        pruned += 1
    return pruned


# ─────────────────────── Merge core ───────────────────────

def plan_merge(
    soul_text: str, selected: list[tuple[int, dict[str, Any]]]
) -> tuple[list[dict[str, Any]], list[str]]:
    """Compute the new lesson entries to append + per-proposal reports.

    Malformed proposals are skipped and reported, never crash the merge.
    """
    try:
        soul_data = yaml.safe_load(soul_text) or {}
        if not isinstance(soul_data, dict):
            raise PromotionError(f"soul.yaml root is not a mapping")
    except yaml.YAMLError as e:
        raise PromotionError(f"Existing soul.yaml does not parse: {e}") from e

    known_ids, known_hashes = existing_dedupe_keys(soul_data)
    new_entries: list[dict[str, Any]] = []
    reports: list[str] = []

    for orig_idx, proposal in selected:
        label = f"[{orig_idx + 1}]"
        try:
            validate_proposal(proposal)
        except ValueError as e:
            reports.append(f"SKIP {label} malformed proposal: {e}")
            continue
        pid = proposal["id"].strip()
        body = lesson_body(proposal) or ""
        chash = content_hash(body)
        if pid in known_ids:
            reports.append(f"DUP  {label} id already in soul.yaml: {pid}")
            continue
        if chash in known_hashes:
            reports.append(f"DUP  {label} identical content already in soul.yaml: {pid}")
            continue
        entry = build_lesson_entry(proposal)
        new_entries.append(entry)
        known_ids.add(pid)
        known_hashes.add(chash)
        preview = body[:80] + ("…" if len(body) > 80 else "")
        reports.append(f"ADD  {label} {pid} [{entry['tier']}/{entry['category']}] {preview}")

    return new_entries, reports


def render_preview(
    entity: str, soul_path: Path, reports: list[str], new_entries: list[dict[str, Any]], apply: bool = False
) -> None:
    """Print diff-style preview of exactly what will merge."""
    print("=" * 72)
    print(f"soul_promote — {'APPLY' if apply else 'PLAN'} for entity '{entity}'")
    print(f"target: {soul_path}")
    print("=" * 72)
    print("\n--- selection report ---")
    for r in reports:
        print(r)
    if new_entries:
        print("\n--- diff (lessons appended to soul.yaml) ---")
        for e in new_entries:
            body_key = next(k for k in CONTENT_KEYS if k in e)
            print(f"+ id: {e['id']}")
            print(f"  tier: {e['tier']}  category: {e['category']}  date: {e['promoted_date']}")
            print(f"  {body_key}: {e[body_key][:120]}{'…' if len(e[body_key]) > 120 else ''}")
    else:
        print("\n(no new lessons to merge)")
    print()


def verify_result(old_text: str, new_text: str, expected_entries: list[dict[str, Any]]) -> None:
    """Schema guard: new soul.yaml must parse and contain exactly the merge.

    Raises PromotionError on any violation (caller restores backup).
    """
    old_data = yaml.safe_load(old_text) or {}
    new_data = yaml.safe_load(new_text)
    if not isinstance(new_data, dict):
        raise PromotionError("Schema guard: merged soul.yaml root is not a mapping")

    # Everything except `lessons` must be byte-for-byte semantically unchanged.
    check_old = {k: v for k, v in old_data.items() if k != "lessons"}
    check_new = {k: v for k, v in new_data.items() if k != "lessons"}
    if check_old != check_new:
        raise PromotionError("Schema guard: non-lessons content changed unexpectedly")

    old_lessons = old_data.get("lessons") or []
    new_lessons = new_data.get("lessons") or []
    if not isinstance(new_lessons, list):
        raise PromotionError("Schema guard: 'lessons' is not a list after merge")
    if len(new_lessons) != len(old_lessons) + len(expected_entries):
        raise PromotionError(
            f"Schema guard: lesson count mismatch "
            f"(expected {len(old_lessons) + len(expected_entries)}, got {len(new_lessons)})"
        )
    new_ids = {l.get("id") for l in new_lessons if isinstance(l, dict)}
    for e in expected_entries:
        if e["id"] not in new_ids:
            raise PromotionError(f"Schema guard: promoted lesson missing after merge: {e['id']}")


def promote(
    entity: str,
    all_flag: bool = False,
    ids: list[str] | None = None,
    indices: list[int] | None = None,
    apply: bool = False,
    confirm: bool = False,
    keep_backups: int = BACKUPS_TO_KEEP,
    repo_root: Path | None = None,
) -> int:
    """Main entry point. Returns process exit code."""
    ids = ids or []
    indices = indices or []
    proposals_path, soul_path = entity_paths(entity, repo_root)

    if not soul_path.exists():
        raise PromotionError(f"soul.yaml not found: {soul_path}")

    proposals = load_proposals(proposals_path)
    selected, sel_skips = select_proposals(proposals, all_flag, ids, indices)

    soul_text = soul_path.read_text(encoding="utf-8")
    new_entries, reports = plan_merge(soul_text, selected)
    reports = sel_skips + reports

    render_preview(entity, soul_path, reports, new_entries, apply=apply)

    if not new_entries:
        print("Nothing to promote. No changes made.")
        return 0

    if not apply:
        print("DRY-RUN complete — zero mutations. Re-run with --apply --confirm to promote.")
        return 0

    if not confirm:
        print("REFUSED: --apply requires explicit --confirm (review gate). No changes made.")
        return 1

    # ── Gated write path ──
    merged_text = splice_lessons(soul_text, dump_lesson_block(new_entries))

    # Schema guard BEFORE touching disk
    try:
        verify_result(soul_text, merged_text, new_entries)
    except PromotionError:
        print("ABORTED: schema guard failed pre-write. soul.yaml untouched.", file=sys.stderr)
        raise

    bak = snapshot_soul(soul_path, keep_backups)
    print(f"snapshot: {bak}")

    atomic_write(soul_path, merged_text)

    # Post-write re-verification; restore snapshot on any failure.
    try:
        written = soul_path.read_text(encoding="utf-8")
        verify_result(soul_text, written, new_entries)
    except Exception as e:
        shutil.copy2(str(bak), str(soul_path))
        print(f"RESTORED from {bak}: post-write verification failed: {e}", file=sys.stderr)
        raise PromotionError(f"Post-write verification failed, soul.yaml restored: {e}") from e

    print(f"PROMOTED {len(new_entries)} lesson(s) into {soul_path}")
    return 0


# ─────────────────────── CLI ───────────────────────

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="soul_promote",
        description="Review-gated promotion of proposed_lessons.yaml → soul.yaml (dry-run default).",
    )
    parser.add_argument("entity", help="Entity name (data/entities/<entity>/)")
    sel = parser.add_mutually_exclusive_group(required=True)
    sel.add_argument("--all", action="store_true", help="Select all staged proposals")
    sel.add_argument("--ids", help="Comma-separated proposal IDs to select")
    sel.add_argument("--indices", help="Comma-separated 1-based proposal positions to select")
    parser.add_argument("--apply", action="store_true", help="Perform the merge (default: dry-run)")
    parser.add_argument("--confirm", action="store_true", help="Explicit review confirmation required by --apply")
    parser.add_argument("--keep-backups", type=int, default=BACKUPS_TO_KEEP, help="Snapshots to retain (default 5)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    ids = [s.strip() for s in args.ids.split(",") if s.strip()] if args.ids else []
    indices = [int(s) for s in args.indices.split(",") if s.strip()] if args.indices else []
    try:
        return promote(
            entity=args.entity,
            all_flag=args.all,
            ids=ids,
            indices=indices,
            apply=args.apply,
            confirm=args.confirm,
            keep_backups=args.keep_backups,
        )
    except PromotionError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2 if "guard" in str(e).lower() or "restored" in str(e).lower() else 1


if __name__ == "__main__":
    sys.exit(main())
