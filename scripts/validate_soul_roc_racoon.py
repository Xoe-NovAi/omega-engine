#!/usr/bin/env python3
"""
Validate Kali's soul files against the v6.0 lean architecture.

Architecture (v6.0):
  soul.yaml              — USER content only (identity, directives, team, trajectory)
  memory/sessions.yaml   — AGENT content (factual events only)
  memory/proposed_lessons.yaml — AGENT proposals (staged, NOT read by agent)
  memory/approved_lessons.yaml — USER approved content (read by agent)
  archive/               — Moved/archived old versions

Rules:
  - soul.yaml must NOT contain soul_axioms or wisdom_text (agent-generated artifacts)
  - soul.yaml must have entity.name and directives
  - proposed_lessons.yaml must have proposals list
  - approved_lessons.yaml must have approved list
  - All files must be valid YAML
  - Archive files must be valid YAML (but not checked for structure)
"""
import yaml
import sys
from pathlib import Path

BASE = Path("data/entities/roc_racoon")


def validate_all():
    errors = []

    # ── 1. soul.yaml ──
    soul_path = BASE / "soul.yaml"
    if not soul_path.exists():
        errors.append(f"MISSING: {soul_path}")
    else:
        try:
            with open(soul_path) as f:
                soul = yaml.safe_load(f)
            if not soul:
                errors.append(f"EMPTY: {soul_path}")
            else:
                # Must have entity
                if "entity" not in soul:
                    errors.append(f"{soul_path}: missing 'entity' key")
                elif "name" not in soul.get("entity", {}):
                    errors.append(f"{soul_path}: entity missing 'name'")

                # Must have directives
                if "directives" not in soul:
                    errors.append(f"{soul_path}: missing 'directives' key")

                # Must NOT have agent-generated content
                if "soul_axioms" in soul:
                    errors.append(f"{soul_path}: contains 'soul_axioms' — must be archived")
                if "wisdom_text" in soul:
                    errors.append(f"{soul_path}: contains 'wisdom_text' — must be archived")
                if "trajectory" in soul:
                    errors.append(f"{soul_path}: contains 'trajectory' — agent-generated operational drift, must be archived")

                # Check duplicate directive IDs
                directives = soul.get("directives", [])
                d_ids = [d.get("id") for d in directives if isinstance(d, dict)]
                if len(d_ids) != len(set(d_ids)):
                    errors.append(f"{soul_path}: duplicate directive IDs found: "
                                  f"{[id for id in d_ids if d_ids.count(id) > 1]}")

        except yaml.YAMLError as e:
            errors.append(f"{soul_path}: YAML error: {e}")

    # ── 2. memory/sessions.yaml ──
    sessions_path = BASE / "memory" / "sessions.yaml"
    if not sessions_path.exists():
        errors.append(f"MISSING: {sessions_path}")
    else:
        try:
            with open(sessions_path) as f:
                sessions = yaml.safe_load(f)
            if not sessions:
                errors.append(f"EMPTY: {sessions_path}")
        except yaml.YAMLError as e:
            errors.append(f"{sessions_path}: YAML error: {e}")

    # ── 3. memory/proposed_lessons.yaml ──
    proposals_path = BASE / "memory" / "proposed_lessons.yaml"
    if not proposals_path.exists():
        errors.append(f"MISSING: {proposals_path}")
    else:
        try:
            with open(proposals_path) as f:
                proposals = yaml.safe_load(f)
            if proposals is None:
                errors.append(f"EMPTY: {proposals_path}")
            elif "proposals" not in proposals:
                errors.append(f"{proposals_path}: missing 'proposals' key")
        except yaml.YAMLError as e:
            errors.append(f"{proposals_path}: YAML error: {e}")

    # ── 4. memory/approved_lessons.yaml ──
    approved_path = BASE / "memory" / "approved_lessons.yaml"
    if not approved_path.exists():
        errors.append(f"MISSING: {approved_path}")
    else:
        try:
            with open(approved_path) as f:
                approved = yaml.safe_load(f)
            if approved is None:
                errors.append(f"EMPTY: {approved_path}")
            elif "approved" not in approved:
                errors.append(f"{approved_path}: missing 'approved' key")
        except yaml.YAMLError as e:
            errors.append(f"{approved_path}: YAML error: {e}")

    # ── 5. archive/ — validate YAML (no structural checks) ──
    archive_dir = BASE / "archive"
    if archive_dir.exists():
        for fpath in sorted(archive_dir.iterdir()):
            if fpath.suffix in (".yaml", ".yml"):
                try:
                    with open(fpath) as f:
                        yaml.safe_load(f)
                except yaml.YAMLError as e:
                    errors.append(f"{fpath}: YAML error: {e}")
    else:
        errors.append(f"MISSING: {archive_dir}/ (archive directory should exist)")

    return errors


if __name__ == "__main__":
    # Support optional path override for pre-commit
    target = sys.argv[1] if len(sys.argv) > 1 else None
    if target:
        # Legacy mode: validate a single file
        try:
            with open(target) as f:
                data = yaml.safe_load(f)
            if not data:
                print(f"❌ {target} is empty")
                sys.exit(1)
            print(f"✅ {target} is valid")
            sys.exit(0)
        except yaml.YAMLError as e:
            print(f"❌ {target}: {e}")
            sys.exit(1)
    else:
        errors = validate_all()
        if errors:
            print("❌ Soul validation FAILED:")
            for e in errors:
                print(f"  • {e}")
            sys.exit(1)
        else:
            print("✅ Soul validation PASSED — v6.0 lean architecture intact")
            sys.exit(0)
