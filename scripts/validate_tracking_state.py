#!/usr/bin/env python3
import json
import sys
import re
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
        print_error(f"{TASK_REGISTRY_PATH.name} not found.")
        return False

    data = load_json(TASK_REGISTRY_PATH)
    errors = 0
    warnings = 0
    
    tasks = data.get("tasks", [])
    for t in tasks:
        status = t.get("status", "").lower()
        if status not in ALLOWED_EXECUTION_STATUSES:
            print_error(f"Task '{t.get('task_id')}' has invalid status: '{status}'. Allowed: {sorted(ALLOWED_EXECUTION_STATUSES)}")
            errors += 1

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