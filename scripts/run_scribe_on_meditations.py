#!/usr/bin/env python3
"""
Scribe Pipeline: Process Autonomous Meditations → Approved Lessons
AP: AP-SCRIBE-MEDITATION-20260911-v1.0.0
⬡ OMEGA ⬡ GROKSTER ⬡ SCRIBE-PIPELINE ⬡ 2026-09-11
"""

import sys
import yaml
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUTONOMOUS_DIR = PROJECT_ROOT / "data" / "autonomous"

# M28 (2026-10-09): this was hardcoded to `grokster`, which was PRUNED at
# 27dd54b5 — `grokster` is not in the IWAD core-14 roster. The next run would
# have RECREATED a pruned entity directory via mkdir-on-write, which is the
# exact resurrection defect M28 exists to prevent. Fail closed instead, and
# require the caller to name the entity explicitly.
SCRIBE_ENTITY = os.environ.get("OMEGA_SCRIBE_ENTITY", "").strip()
if not SCRIBE_ENTITY:
    raise SystemExit(
        "OMEGA_SCRIBE_ENTITY is required. The previous default (`grokster`) was "
        "pruned at 27dd54b5 and writing to it would resurrect a retired entity "
        "(M28). Set OMEGA_SCRIBE_ENTITY to a current IWAD core entity."
    )

_ENTITY_DIR = PROJECT_ROOT / "data" / "entities" / SCRIBE_ENTITY
if not _ENTITY_DIR.is_dir():
    raise SystemExit(
        f"Entity directory does not exist: {_ENTITY_DIR}. "
        f"'{SCRIBE_ENTITY}' is not a current IWAD core entity."
    )

APPROVED_LESSONS = _ENTITY_DIR / "approved_lessons.yaml"
PROPOSED_LESSONS = _ENTITY_DIR / "proposed_lessons.yaml"

def load_yaml_first_doc(path: Path) -> Dict:
    """Load only the first YAML document (handles multi-doc files)."""
    if path.exists():
        with open(path) as f:
            docs = list(yaml.safe_load_all(f))
            if docs:
                return docs[0] or {"proposals": []}
    return {"proposals": []}

def save_yaml(path: Path, data: Dict):
    with open(path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

def extract_meditation_content(md_path: Path) -> Dict[str, Any]:
    """Extract structured content from meditation raw markdown."""
    content = md_path.read_text()
    lines = content.split('\n')
    
    prompt = ""
    for line in lines:
        if line.startswith("**Prompt**:"):
            prompt = line.replace("**Prompt**:", "").strip()
            break
    
    lesson_id = f"L3-MEDITATION-{md_path.stem}"
    
    return {
        "id": lesson_id,
        "date": datetime.now().isoformat()[:10],
        "level": "L3",
        "narrative": f"Autonomous meditation: {prompt[:100]}..." if prompt else "Autonomous meditation session",
        "insight": content[:500] + "..." if len(content) > 500 else content,
        "principle": f"Meditation on {prompt.split('--lenses')[0].strip() if '--lenses' in prompt else 'autonomous topic'} yielded structural insights",
        "tags": ["meditation", "autonomous", "L3"],
        "status": "approved",
        "evidence": [
            {"artifact": str(md_path.relative_to(PROJECT_ROOT)), "quote": content[:200]}
        ]
    }

def main():
    print("⬡ SCRIBE PIPELINE: MEDITATIONS → APPROVED LESSONS ⬡")
    
    meditation_files = sorted(AUTONOMOUS_DIR.glob("*meditation_raw.md"))
    print(f"Found {len(meditation_files)} meditation files")
    
    # Load existing approved lessons
    approved = load_yaml_first_doc(APPROVED_LESSONS)
    if "proposals" not in approved:
        approved["proposals"] = []
    
    existing_ids = {p.get("id") for p in approved["proposals"]}
    
    new_lessons = 0
    for md_file in meditation_files:
        lesson = extract_meditation_content(md_file)
        if lesson["id"] not in existing_ids:
            approved["proposals"].append(lesson)
            new_lessons += 1
            print(f"  + {lesson['id']}")
        else:
            print(f"  = {lesson['id']} (already exists)")
    
    if new_lessons > 0:
        save_yaml(APPROVED_LESSONS, approved)
        print(f"\n✓ Promoted {new_lessons} meditations to approved_lessons.yaml")
    else:
        print("\n= No new meditations to promote")
    
    # Update proposed_lessons.yaml (first document only)
    try:
        proposed = load_yaml_first_doc(PROPOSED_LESSONS)
        if "proposals" in proposed:
            for p in proposed["proposals"]:
                if p.get("id", "").startswith("L3-MEDITATION-"):
                    p["status"] = "promoted"
            save_yaml(PROPOSED_LESSONS, proposed)
            print("✓ Updated proposed_lessons.yaml (first doc) with promotion status")
    except Exception as e:
        print(f"⚠ Could not update proposed_lessons.yaml: {e}")
    
    print(f"\n✓ Scribe pipeline complete. Total approved lessons: {len(approved.get('proposals', []))}")

if __name__ == "__main__":
    main()
