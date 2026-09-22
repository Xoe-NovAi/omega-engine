#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""M27 Tracking Integrity validator (Cognitive State Validator).

M1 (2026-08-23): staleness rule — `in_progress` tasks with `last_checkpoint`
older than STALENESS_DAYS are errors. Shared `_parse_ts()` helper handles the
three coexisting ISO-8601 formats in TASK_REGISTRY.json (`Z` suffix,
`+00:00` offset, microsecond variants) per G5-2 of
RESEARCHER_SESSION_TRACKING_GAPS_20260823.md.
M3 (2026-08-23): warn-only schema checks for optional `superseded_by` and
`artifact_path` fields (legacy records grandfathered, never errored).
"""
import json
import subprocess
import sys
import re
from datetime import datetime, timezone
from pathlib import Path

# Configuration
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data" / "coordination"

ACTIVE_SPRINT_PATH = DATA_DIR / "ACTIVE_SPRINT.json"
TASK_REGISTRY_PATH = DATA_DIR / "TASK_REGISTRY.json"
GAP_REGISTRY_PATH = DATA_DIR / "GAP_REGISTRY.json"

# Unified Taxonomy per TRACKING_ARCHITECTURE.md
ALLOWED_STATUSES = {"backlog", "ready", "in_progress", "blocked", "completed", "superseded"}
# Tier-0 (planning) uses the 6-status taxonomy above.
# Tier-3 (TASK_REGISTRY execution records) may also use `failed` — a subagent run can
# legitimately fail, which is distinct from `blocked` (waiting on dep) or `superseded`
# (replaced by newer plan). Per Carmack review (2026-08-14): collapsing failed→blocked
# destroys a real signal. `failed` is the ONLY addition to Tier-3.
ALLOWED_EXECUTION_STATUSES = ALLOWED_STATUSES.union({"failed"})

# GAP_REGISTRY allowed statuses
ALLOWED_GAP_STATUSES = {"resolved", "outstanding", "partial", "lost"}

# M1: staleness threshold (days). `in_progress` tasks whose last_checkpoint is
# older than this are errors. 7d sits in the empirical gap of the age
# distribution (legitimate work clusters <=6d, zombies >=8d) — Researcher
# Ruling 1, RESEARCHER_SESSION_TRACKING_GAPS_20260823.md.
STALENESS_DAYS = 7


def _parse_ts(value):
    """Parse an ISO-8601 timestamp tolerating format heterogeneity (G5-2).

    Normalizes the `Z` suffix (rejected by fromisoformat pre-3.11), assumes
    UTC when naive. Returns a timezone-aware datetime or None on failure.
    Shared by validate_tracking_state.py, sweep_task_registry.py, and
    generate_session_registry.py — do NOT duplicate parsing logic elsewhere.
    """
    if not value or not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _resolve_pointer(pointer: object, task_ids: set) -> bool:
    """Resolve a superseded_by pointer per G3 priority order.

    1. task_id present in the registry
    2. git commit hash (verified via `git rev-parse --verify`)
    3. repo-relative doc/file path existing on disk

    Returns True if the pointer resolves under any strategy.
    """
    pointer = str(pointer or "").strip()
    # Strip scheme prefixes used by convention (commit:<sha>, task:<id>, doc:<path>)
    # and trailing prose annotations ("docs/x.md Phase 1 (replaced ...)").
    pointer = re.sub(r"^(commit|task|doc|file|path):", "", pointer)
    candidates = [pointer] + pointer.split()[:2]
    for cand in candidates:
        if not cand:
            continue
        if cand in task_ids:
            return True
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--verify", "--quiet", f"{cand}^{{commit}}"],
                cwd=ROOT_DIR, capture_output=True, timeout=10,
            )
            if result.returncode == 0:
                return True
        except (OSError, subprocess.SubprocessError):
            pass
        if (ROOT_DIR / cand).exists():
            return True
    return False

def print_error(msg):
    print(f"��� ERROR: {msg}", file=sys.stderr)

def print_warn(msg):
    print(f"������ WARNING: {msg}")

def print_ok(msg):
    print(f"��� OK: {msg}")

def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print_error(f"Failed to load {path.name}: {e}")
        sys.exit(1)

def extract_gap_ids(text):
    """Extract R-ID patterns (R + digits) from text."""
    if not text:
        return set()
    return set(re.findall(r'\bR\d+\b', text.upper()))

def validate_gap_registry():
    print(f"\n���� Validating {GAP_REGISTRY_PATH.name}...")
    if not GAP_REGISTRY_PATH.exists():
        print_warn(f"{GAP_REGISTRY_PATH.name} not found. Skipping.")
        return True

    data = load_json(GAP_REGISTRY_PATH)
    gaps = data.get("gaps", {})
    
    errors = 0
    topics = set()
    
    for gap_id, details in gaps.items():
        topic = details.get("topic", "").lower()
        if topic in topics:
            print_error(f"Duplicate topic found in gaps: '{topic}' (Gap ID: {gap_id})")
            errors += 1
        topics.add(topic)
        
        status = details.get("status", "").lower()
        if status not in ALLOWED_GAP_STATUSES:
            print_error(f"Gap {gap_id} has invalid status: '{status}'. Allowed: {sorted(ALLOWED_GAP_STATUSES)}")
            errors += 1

    if errors == 0:
        print_ok(f"GAP_REGISTRY is healthy ({len(gaps)} gaps registered).")
    return errors == 0

def validate_active_sprint():
    print(f"\n���� Validating {ACTIVE_SPRINT_PATH.name}...")
    if not ACTIVE_SPRINT_PATH.exists():
        print_error(f"{ACTIVE_SPRINT_PATH.name} not found.")
        return False

    data = load_json(ACTIVE_SPRINT_PATH)
    errors = 0

    # Load GAP_REGISTRY for R-ID cross-check
    gap_ids = set()
    if GAP_REGISTRY_PATH.exists():
        gap_data = load_json(GAP_REGISTRY_PATH)
        gap_ids = set(gap_data.get("gaps", {}).keys())

    # Check workstreams/phases
    workstreams = data.get("workstreams", {})
    for ws_name, ws_data in workstreams.items():
        if isinstance(ws_data, dict):
            status = ws_data.get("status", "").lower()
            if status and status not in ALLOWED_STATUSES:
                print_error(f"Workstream '{ws_name}' has invalid status: '{status}'. Allowed: {ALLOWED_STATUSES}")
                errors += 1

            for st in ws_data.get("subtasks", []):
                st_status = st.get("status", "").lower()
                if st_status and st_status not in ALLOWED_STATUSES:
                    print_error(f"Subtask '{st.get('id', 'unknown')}' in '{ws_name}' has invalid status: '{st_status}'")
                    errors += 1

                # FIX 3: R-ID cross-check — scan tags + description for R\d+ patterns
                st_id = st.get("id", "")
                referenced_gaps = set()
                
                # Check tags array
                tags = st.get("tags", [])
                if isinstance(tags, list):
                    for tag in tags:
                        referenced_gaps.update(extract_gap_ids(str(tag)))
                
                # Check description
                desc = st.get("description", "")
                referenced_gaps.update(extract_gap_ids(desc))
                
                # Check ssots array
                ssots = st.get("ssots", [])
                if isinstance(ssots, list):
                    for ssot in ssots:
                        referenced_gaps.update(extract_gap_ids(str(ssot)))
                
                # Validate each referenced gap exists in registry
                for gap_key in referenced_gaps:
                    if gap_ids and gap_key not in gap_ids:
                        print_error(f"Subtask '{st_id}' references gap '{gap_key}' which is NOT in GAP_REGISTRY. Must register the gap first.")
                        errors += 1

    if errors == 0:
        print_ok("ACTIVE_SPRINT statuses are compliant.")
    return errors == 0

def validate_task_registry():
    print(f"\n���� Validating {TASK_REGISTRY_PATH.name}...")
    if not TASK_REGISTRY_PATH.exists():
        # TASK_REGISTRY.json is a runtime artifact (gitignored) — absent in a
        # fresh CI checkout. Skip gracefully instead of failing the gate.
        print_warn(f"{TASK_REGISTRY_PATH.name} absent (runtime artifact) — skipped.")
        return True

    data = load_json(TASK_REGISTRY_PATH)
    errors = 0
    warnings = 0
    
    tasks = data.get("tasks", [])
    task_ids = {t.get("task_id", "") for t in tasks}
    for t in tasks:
        status = t.get("status", "").lower()
        if status not in ALLOWED_EXECUTION_STATUSES:
            print_error(f"Task '{t.get('task_id')}' has invalid status: '{status}'. Allowed: {sorted(ALLOWED_EXECUTION_STATUSES)}")
            errors += 1

    # M1: Staleness rule — `in_progress` with stale last_checkpoint is an error.
    now = datetime.now(timezone.utc)
    stale_offenders = []
    for t in tasks:
        if t.get("status", "").lower() != "in_progress":
            continue
        ts = _parse_ts(t.get("last_checkpoint"))
        if ts is None:
            print_warn(f"Task '{t.get('task_id')}' is in_progress but has missing/unparseable last_checkpoint. Cannot assess staleness.")
            warnings += 1
            continue
        age_days = (now - ts).days
        if age_days > STALENESS_DAYS:
            stale_offenders.append((t.get("task_id"), age_days))
    if stale_offenders:
        for task_id, age_days in stale_offenders:
            print_error(f"Stale in_progress task: '{task_id}' — last_checkpoint {age_days}d ago (threshold: {STALENESS_DAYS}d). Sweep it (`make sweep-tasks`) or close it out.")
            errors += 1

    # G5-2 drift item 2: inverted clocks — checkpoint must not precede creation.
    for t in tasks:
        created = _parse_ts(t.get("created_at"))
        checked = _parse_ts(t.get("last_checkpoint"))
        if created and checked and checked < created:
            print_warn(f"Task '{t.get('task_id')}' has last_checkpoint earlier than created_at (inverted clock). Fix the timestamps.")
            warnings += 1

    # M3: optional schema fields — warn-only, never error (legacy grandfathering).
    for t in tasks:
        task_id = t.get("task_id", "")
        status = t.get("status", "").lower()
        if status == "superseded":
            pointer = t.get("superseded_by")
            if not pointer or not str(pointer).strip():
                print_warn(f"Superseded task '{task_id}' lacks a non-empty superseded_by pointer (successor task_id, commit hash, or repo-relative doc path). Legacy records are grandfathered; new records MUST set it.")
                warnings += 1
            elif not _resolve_pointer(pointer, task_ids):
                print_warn(f"Superseded task '{task_id}' has superseded_by '{pointer}' which does NOT resolve (no such task_id / commit / path).")
                warnings += 1
        artifact = t.get("artifact_path")
        if artifact:
            artifact_path = ROOT_DIR / artifact
            if not artifact_path.exists():
                print_warn(f"Task '{task_id}' cites artifact_path '{artifact}' which does not exist on disk.")
                warnings += 1

    # FIX 1: Cross-tier validation — Tier-3 `failed` must sync to Tier-0 `blocked`/`superseded`
    if ACTIVE_SPRINT_PATH.exists():
        sprint_data = load_json(ACTIVE_SPRINT_PATH)
        # Build a map of subtask_id -> (workstream, subtask_status)
        subtask_status_map = {}
        workstreams = sprint_data.get("workstreams", {})
        for ws_name, ws_data in workstreams.items():
            if isinstance(ws_data, dict):
                for st in ws_data.get("subtasks", []):
                    st_id = st.get("id", "")
                    st_status = st.get("status", "").lower()
                    if st_id:
                        subtask_status_map[st_id] = (ws_name, st_status)

        for t in tasks:
            task_id = t.get("task_id", "")
            status = t.get("status", "").lower()
            if status == "failed":
                # Check if this task_id corresponds to a Tier-0 subtask
                if task_id in subtask_status_map:
                    ws_name, st_status = subtask_status_map[task_id]
                    if st_status not in {"blocked", "superseded"}:
                        print_error(f"Cross-tier violation: Task '{task_id}' is 'failed' in TASK_REGISTRY but Tier-0 subtask in '{ws_name}' is '{st_status}'. Must be 'blocked' or 'superseded'.")
                        errors += 1
                else:
                    # Task doesn't map to a Tier-0 subtask — warn but don't error (could be standalone)
                    print_warn(f"Task '{task_id}' is 'failed' but has no corresponding Tier-0 subtask. Consider adding to ACTIVE_SPRINT for traceability.")

    if errors == 0:
        print_ok(f"TASK_REGISTRY is healthy ({len(tasks)} tasks).")
    return errors == 0

def main():
    print("==================================================")
    print("�������  OMEGA ENGINE: COGNITIVE STATE VALIDATOR")
    print("==================================================")
    
    success = True
    success &= validate_gap_registry()
    success &= validate_active_sprint()
    success &= validate_task_registry()
    
    print("\n==================================================")
    if success:
        print("��� ALL TRACKING STATE CHECKS PASSED")
        sys.exit(0)
    else:
        print("��� TRACKING STATE CHECKS FAILED. Please fix the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()