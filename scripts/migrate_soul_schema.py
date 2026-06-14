#!/usr/bin/env python3
"""Migrate soul.yaml files to canonical schema.
AP: AP-MIGRATE-SOUL-v1.0.0
Closes G-10: unify `lessons:` / `lessons_learned:` to `soul_evolution.lessons_learned`.

Canonical path: soul_evolution.lessons_learned (used by oracle.py:376)
Drift patterns detected:
  - Top-level `lessons:` (wrong field name + wrong nesting)
  - Top-level `lessons_learned:` (wrong nesting)
  - `soul_evolution.lessons:` (wrong field name, right nesting)
"""

import os
import sys
import yaml
from pathlib import Path

ENTITIES_DIR = Path(__file__).resolve().parent.parent / "data" / "entities"

# Files that should be migrated
DRIFT_FILES = [
    # Top-level `lessons:` -> soul_evolution.lessons_learned
    "context", "jem_discovery", "jem_synthesis", "jem_verification",
    "makali", "quality", "roc_racoon", "scribe",
    # Top-level `lessons_learned:` -> soul_evolution.lessons_learned
    "antigravity", "cli_cline", "cli_gemini", "kali", "maat",
    # `soul_evolution.lessons:` -> soul_evolution.lessons_learned
    "link", "sentinel",
]


def normalize_soul(data: dict) -> dict:
    """Normalize a soul.yaml dict to canonical schema."""
    changed = False

    # Detect and migrate top-level `lessons:` -> soul_evolution.lessons_learned
    if "lessons" in data and isinstance(data["lessons"], list):
        lessons = data.pop("lessons")
        changed = True
        if "soul_evolution" not in data:
            data["soul_evolution"] = {}
        if "lessons_learned" not in data["soul_evolution"]:
            data["soul_evolution"]["lessons_learned"] = []
        # Merge, avoiding duplicates
        existing_ids = {l.get("source") for l in data["soul_evolution"]["lessons_learned"] if isinstance(l, dict)}
        for l in lessons:
            if isinstance(l, dict) and l.get("source") not in existing_ids:
                data["soul_evolution"]["lessons_learned"].append(l)
                existing_ids.add(l.get("source"))

    # Detect and migrate top-level `lessons_learned:` -> soul_evolution.lessons_learned
    if "lessons_learned" in data and isinstance(data["lessons_learned"], list):
        # This is at top level, not under soul_evolution
        if "soul_evolution" not in data or "lessons_learned" not in data.get("soul_evolution", {}):
            lessons = data.pop("lessons_learned")
            changed = True
            if "soul_evolution" not in data:
                data["soul_evolution"] = {}
            if "lessons_learned" not in data["soul_evolution"]:
                data["soul_evolution"]["lessons_learned"] = []
            existing_ids = {l.get("source") for l in data["soul_evolution"]["lessons_learned"] if isinstance(l, dict)}
            for l in lessons:
                if isinstance(l, dict) and l.get("source") not in existing_ids:
                    data["soul_evolution"]["lessons_learned"].append(l)
                    existing_ids.add(l.get("source"))

    # Detect and migrate `soul_evolution.lessons:` -> soul_evolution.lessons_learned
    if "soul_evolution" in data and isinstance(data["soul_evolution"], dict):
        se = data["soul_evolution"]
        if "lessons" in se and isinstance(se["lessons"], list):
            se["lessons_learned"] = se.pop("lessons")
            changed = True

    return data, changed


def main():
    migrated = 0
    errors = 0

    for name in DRIFT_FILES:
        path = ENTITIES_DIR / name / "soul.yaml"
        if not path.exists():
            # Try under entities directly
            path = ENTITIES_DIR / name / "soul.yaml"
            if not path.exists():
                print(f"  ⚠️  {name}: soul.yaml not found, skipping")
                continue

        try:
            with open(path) as f:
                data = yaml.safe_load(f)
            if not isinstance(data, dict):
                print(f"  ⚠️  {name}: not a dict, skipping")
                continue

            new_data, changed = normalize_soul(data)
            if changed:
                # Backup original
                bak_path = path.with_suffix(".yaml.bak")
                if not bak_path.exists():
                    os.rename(path, bak_path)
                    print(f"  💾 {name}: backup created at {bak_path.name}")

                with open(path, "w") as f:
                    yaml.dump(new_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                migrated += 1
                print(f"  ✅ {name}: migrated to canonical schema")
            else:
                print(f"  ➖ {name}: already canonical, no change")
        except Exception as e:
            print(f"  ❌ {name}: error — {e}")
            errors += 1

    print(f"\nSummary: {migrated} migrated, {errors} errors")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
