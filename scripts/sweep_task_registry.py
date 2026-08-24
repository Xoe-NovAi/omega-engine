#!/usr/bin/env python3
"""M27 Tier-3 zombie sweep — ACTIVE_SPRINT-aware (G5-1 amendment).

Finds TASK_REGISTRY.json tasks stuck `in_progress` past STALENESS_DAYS and:
  - dry-run (default): prints what WOULD change. Exit 0 clean / 2 offenders.
  - --apply: sets expired -> `failed` + reason string. NEVER touches
    superseded/completed. Atomic write (tmp->rename).
  - G5-1: if an expired task is referenced as a Tier-0 subtask in
    ACTIVE_SPRINT.json whose status is NOT blocked/superseded, the task is
    routed to a REVIEW LIST (`data/coordination/sweep_review_<date>.md`,
    exit 3) instead of being failed — blind auto-fail trips the M27
    cross-tier check and misclassifies delivered work.

Exit codes: 0 = nothing to do / applied cleanly · 1 = internal error ·
            2 = dry-run found offenders · 3 = review-list cases exist.

NEVER run this in pre-commit — manual (`make sweep-tasks`) or CI-only.
Timestamps parsed via shared _parse_ts() (validate_tracking_state).
"""
import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))
from validate_tracking_state import (  # noqa: E402
    DATA_DIR,
    ROOT_DIR,
    STALENESS_DAYS,
    TASK_REGISTRY_PATH,
    ACTIVE_SPRINT_PATH,
    _parse_ts,
)

REVIEW_PATH_FMT = str(DATA_DIR / "sweep_review_{date}.md")
FAIL_REASON = "auto-swept: in_progress exceeded {days}d staleness (last_checkpoint {ts}); no ACTIVE_SPRINT counterpart"


def build_sprint_subtask_map(sprint_path):
    """Map task_id -> tier-0 status for every subtask in ACTIVE_SPRINT.json."""
    mapping = {}
    if not sprint_path.exists():
        return mapping
    try:
        sprint = json.loads(sprint_path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"WARNING: cannot read {sprint_path.name}: {e}", file=sys.stderr)
        return mapping
    for ws in sprint.get("workstreams", {}).values():
        if not isinstance(ws, dict):
            continue
        for st in ws.get("subtasks", []):
            sid = st.get("id", "")
            if sid:
                mapping[sid] = st.get("status", "").lower()
    return mapping


def find_expired(tasks, now=None):
    """Return [(task, age_days)] for in_progress tasks past STALENESS_DAYS."""
    now = now or datetime.now(timezone.utc)
    expired = []
    for t in tasks:
        if t.get("status", "").lower() != "in_progress":
            continue
        ts = _parse_ts(t.get("last_checkpoint"))
        if ts is None:
            continue
        age = (now - ts).days
        if age > STALENESS_DAYS:
            expired.append((t, age))
    return expired


def classify(expired, sprint_map):
    """Split expired into (failable, review) per G5-1 rules."""
    failable, review = [], []
    for t, age in expired:
        tier0 = sprint_map.get(t.get("task_id", ""))
        # Route to review when an ACTIVE_SPRINT counterpart exists and is live.
        if tier0 is not None and tier0 not in {"blocked", "superseded"}:
            review.append((t, age, tier0))
        else:
            failable.append((t, age))
    return failable, review


def atomic_write_json(path, data):
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def apply_failures(failable):
    """Set status=failed + reason on failable tasks. Returns count."""
    registry = json.loads(TASK_REGISTRY_PATH.read_text())
    ids = {f.get("task_id") for f, _ in failable}
    n = 0
    for t in registry.get("tasks", []):
        if t.get("task_id") in ids:
            t["status"] = "failed"
            t["failure_reason"] = FAIL_REASON.format(
                days=STALENESS_DAYS, ts=t.get("last_checkpoint", "unknown"))
            n += 1
    atomic_write_json(TASK_REGISTRY_PATH, registry)
    return n


def write_review_list(review):
    path = Path(REVIEW_PATH_FMT.format(date=datetime.now(timezone.utc).strftime("%Y%m%d")))
    lines = [
        "# Sweep Review List — human classification required",
        "",
        f"Generated {datetime.now(timezone.utc).isoformat()} by sweep_task_registry.py.",
        "These expired in_progress tasks have LIVE ACTIVE_SPRINT counterparts",
        "(status not blocked/superseded) — auto-failing them would trip M27",
        "cross-tier validation and may misclassify delivered work (G5-1).",
        "",
        "| task_id | age_days | tier-0 status | last_checkpoint |",
        "|---|---|---|---|",
    ]
    for t, age, tier0 in review:
        lines.append(f"| `{t.get('task_id')}` | {age} | {tier0} | {t.get('last_checkpoint')} |")
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    with os.fdopen(fd, "w") as f:
        f.write("\n".join(lines) + "\n")
    os.replace(tmp, path)
    return path


# ── Self-test (M13/M21): proves fail-closed behavior on synthetic fixtures ──

def self_test():
    """Exercise find_expired/classify against fixtures. Fail-closed asserts."""
    from validate_tracking_state import print_ok, print_error
    failures = []

    def check(name, cond):
        (print_ok if cond else (lambda m: failures.append(m)))(f"self-test: {name}")

    old = "2026-07-01T00:00:00Z"          # Z-suffix format (pre-3.11 landmine)
    fresh = "2026-08-23T00:00:00+00:00"   # offset format
    tasks = [
        {"task_id": "zombie-a", "status": "in_progress", "last_checkpoint": old},
        {"task_id": "fresh-b", "status": "in_progress", "last_checkpoint": fresh},
        {"task_id": "done-c", "status": "completed", "last_checkpoint": old},
        {"task_id": "superseded-d", "status": "superseded", "last_checkpoint": old},
        {"task_id": "bad-ts-e", "status": "in_progress", "last_checkpoint": "not-a-date"},
    ]
    expired = find_expired(tasks)
    check("only zombie-a detected expired", [t["task_id"] for t, _ in expired] == ["zombie-a"])
    check("Z-suffix timestamp parsed", expired and expired[0][1] > 30)

    # G5-1 classification
    failable, review = classify(expired, {"fresh-b": "in_progress"})
    check("no-sprint-counterpart zombie is failable", [t["task_id"] for t, _ in failable] == ["zombie-a"])
    failable, review = classify(expired, {"zombie-a": "in_progress"})
    check("live counterpart routes to review", len(review) == 1 and review[0][2] == "in_progress")
    failable, review = classify(expired, {"zombie-a": "blocked"})
    check("blocked counterpart stays failable", len(failable) == 1 and not review)
    failable, review = classify(expired, {"zombie-a": "superseded"})
    check("superseded counterpart stays failable", len(failable) == 1 and not review)

    # Never-touch guarantees
    statuses = {t["task_id"]: t["status"] for t in tasks}
    check("completed never swept", statuses["done-c"] == "completed")
    check("superseded never swept", statuses["superseded-d"] == "superseded")

    if failures:
        for f in failures:
            print_error(f)
        sys.exit(1)
    print("SELF-TEST PASSED (fail-closed behavior verified)")
    sys.exit(0)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--apply", action="store_true", help="apply failed transitions (default: dry-run)")
    ap.add_argument("--self-test", action="store_true", help="run fixture self-test and exit")
    args = ap.parse_args()

    if args.self_test:
        self_test()

    if not TASK_REGISTRY_PATH.exists():
        print(f"ERROR: {TASK_REGISTRY_PATH} not found", file=sys.stderr)
        sys.exit(1)

    registry = json.loads(TASK_REGISTRY_PATH.read_text())
    tasks = registry.get("tasks", [])
    expired = find_expired(tasks)
    if not expired:
        print(f"No expired in_progress tasks (> {STALENESS_DAYS}d). Registry is clean.")
        sys.exit(0)

    sprint_map = build_sprint_subtask_map(ACTIVE_SPRINT_PATH)
    failable, review = classify(expired, sprint_map)

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"=== sweep_task_registry ({mode}) — {len(expired)} expired > {STALENESS_DAYS}d ===")
    for t, age in failable:
        action = "WOULD FAIL" if not args.apply else "FAILED"
        print(f"  [{action}] {t['task_id']} ({age}d stale)")
    for t, age, tier0 in review:
        print(f"  [REVIEW] {t['task_id']} ({age}d stale) — ACTIVE_SPRINT counterpart is '{tier0}'")

    if args.apply:
        n = apply_failures(failable)
        print(f"Applied failed -> {n} task(s).")
    else:
        print("Dry-run only. Re-run with --apply to execute.")

    if review:
        path = write_review_list(review)
        print(f"{len(review)} task(s) routed to review list: {path}")
        sys.exit(3)
    sys.exit(0)


if __name__ == "__main__":
    main()
