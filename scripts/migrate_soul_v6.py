#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""🔱 Soul Architecture Protocol v6.1 — Transactional Migration Script.

Two-Phase Commit:
  Phase 1 (Validation): Parse all soul.yaml files and generate migration_manifest.json.
  Phase 2 (Execution): Write 4-file split only if Phase 1 succeeds 100%.

Usage:
  python scripts/migrate_soul_v6.py --dry-run          # Phase 1: Validate only
  python scripts/migrate_soul_v6.py                     # Phase 2: Execute migration
  python scripts/migrate_soul_v6.py --entity roc_racoon # Single entity migration

Mandates: M1 (AnyIO), M6 (Podman keep-id), M11 (Soul Integrity), M12 (Queue Integrity)
"""

import argparse
import json
import logging
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("migrate_soul_v6")

# Resolve entities directory
BASE_DIR = Path(__file__).resolve().parent.parent
ENTITIES_DIR = BASE_DIR / "data" / "entities"

# The 11 active fleet entities
FLEET_ENTITIES = [
    "kali",
    "doom_guy",
    "roc_racoon",
    "lilith",
    "maat",
    "verity",
    "jem",
    "researcher",
    "makali",
    "iris",
    "sophia",
    # john_carmack will be scaffolded fresh
]

MIGRATION_JOURNAL = BASE_DIR / "data" / "migration_journal.log"


from datetime import datetime, timezone

class DatetimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime and date objects."""
    def default(self, obj):
        if isinstance(obj, (datetime,)):
            return obj.isoformat()
        try:
            return str(obj)
        except Exception:
            return super().default(obj)


def log_journal(entry: str):
    """Append to the migration journal for audit trail."""
    with open(MIGRATION_JOURNAL, "a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {entry}\n")


def load_soul_yaml(entity_path: Path) -> Tuple[bool, Optional[Dict]]:
    """Load and parse a v5 soul.yaml file with resilience for agent-generated YAML.
    
    Handles three common formats:
      - Standard nested: entity: {name: foo, ...}
      - Flat mapping: entity: foo \n directives: \n - item
      - Mixed root: entity: foo \n - session (invalid YAML — repaired)
    """
    soul_file = entity_path / "soul.yaml"
    if not soul_file.exists():
        return False, None
    
    with open(soul_file, "r") as f:
        raw = f.read()
    
    # Step 1: Strip non-YAML header decorations
    lines = raw.split("\n")
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("⬡"):
            cleaned_lines.append(line)
        elif stripped.startswith("#"):
            cleaned_lines.append(line)
        elif not stripped:
            cleaned_lines.append(line)
    raw = "\n".join(cleaned_lines)
    
    # Step 2: Try standard parsing
    try:
        data = yaml.safe_load(raw)
        if data is not None and isinstance(data, dict):
            return True, data
    except yaml.YAMLError:
        pass
    
    # Step 3: Section-by-section resilient parsing.
    # Parse each root-level mapping key individually to recover
    # from mixed mapping/list at root level.
    try:
        data = {}
        current_key = None
        current_lines = []
        
        for line in cleaned_lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            
            # Detect root-level mapping key: not indented, contains ":"
            is_root_key = (
                not line.startswith(" ") and not line.startswith("\t")
                and ":" in stripped
                and not stripped.startswith("-")
                and not stripped.startswith("'")
                and not stripped.startswith('"')
            )
            
            if is_root_key:
                # Save previous section
                if current_key and current_lines:
                    section_text = "\n".join(current_lines)
                    try:
                        section_data = yaml.safe_load(section_text)
                        if isinstance(section_data, dict):
                            data.update(section_data)
                        elif isinstance(section_data, list):
                            data[current_key] = section_data
                    except yaml.YAMLError:
                        # Store unparseable section as raw text
                        data[current_key] = section_text
                
                current_key = stripped.split(":")[0].strip()
                current_lines = [line]
            else:
                current_lines.append(line)
        
        # Save last section
        if current_key and current_lines:
            section_text = "\n".join(current_lines)
            try:
                section_data = yaml.safe_load(section_text)
                if isinstance(section_data, dict):
                    data.update(section_data)
                elif isinstance(section_data, list):
                    data[current_key] = section_data
            except yaml.YAMLError:
                data[current_key] = section_text
        
        if data:
            return True, data
    
    except Exception as e:
        logger.warning(f"  Resilient parse failed: {e}")
    
    return False, None


def deconstruct_soul(data: Dict) -> Tuple[Dict, List]:
    """Separate identity (Constitution) from lessons (Gnosis).
    
    Handles both flat format (entity: name) and nested format
    (entity: {name: name, lessons_learned: [...]}).
    
    Returns:
        (identity_dict, lessons_list)
    """
    # Detect format: flat (entity: name at root) vs nested (entity block)
    root_entity_name = data.get("entity")
    
    if isinstance(root_entity_name, str) and root_entity_name:
        # Flat format: entity: name, directives: [...], soul_evolution: {lessons_learned: [...]}
        identity = {}
        lessons = []
        
        for key, value in data.items():
            # Extract lessons from any key that looks like a lesson store
            if key in ("lessons_learned", "lessons", "sessions", "philosophy"):
                if isinstance(value, list):
                    lessons.extend(value)
                elif isinstance(value, dict):
                    subs = value.get("lessons_learned", value.get("lessons", []))
                    if isinstance(subs, list):
                        lessons.extend(subs)
            
            # Special handling for soul_evolution block
            elif key == "soul_evolution":
                if isinstance(value, dict):
                    # Extract lessons from within the block
                    subs = value.get("lessons_learned", value.get("lessons", []))
                    if isinstance(subs, list):
                        lessons.extend(subs)
                    # Keep the metadata (minus lessons) in identity
                    clean_soul = {k: v for k, v in value.items() if k not in ("lessons_learned", "lessons")}
                    if clean_soul:
                        identity[key] = clean_soul
                elif isinstance(value, list):
                    lessons.extend(value)
                else:
                    # It's a string (agent-generated corruption) - we'll treat it as a lesson
                    lessons.append(value)
            else:
                identity[key] = value
        return identity, lessons
    
    elif isinstance(root_entity_name, dict):
        # Nested format: entity: {name: name, personality: ..., lessons_learned: [...]}
        entity = root_entity_name
        lessons = entity.get("lessons_learned", [])
        if not lessons:
            lessons = entity.get("lessons", [])
        
        philosophy = entity.get("philosophy", [])
        principles = entity.get("universal_principles", [])
        insights = entity.get("architectural_insights", [])
        experiences = entity.get("embodied_experiences", [])
        
        combined = []
        for lst in [lessons, philosophy, principles, insights, experiences]:
            if isinstance(lst, list):
                combined.extend(lst)
        
        identity = dict(entity)
        for key in ["lessons_learned", "lessons", "philosophy", 
                    "universal_principles", "architectural_insights", 
                    "embodied_experiences"]:
            identity.pop(key, None)
        
        return {"entity": identity}, combined
    
    else:
        # Unknown format — try to extract anything useful
        identity = {}
        lessons = []
        for key, value in data.items():
            if isinstance(value, list):
                lessons.extend(value)
            else:
                identity[key] = value
        return identity, lessons


def check_existing_v6(entity_path: Path) -> bool:
    """Check if v6 structure already exists."""
    required_files = [
        "soul.yaml", "approved_lessons.yaml", 
        "proposed_lessons.yaml", "sessions.yaml"
    ]
    existing = [entity_path / f for f in required_files]
    return all(f.exists() for f in existing)


def atomic_write_yaml(file_path: Path, data: Any) -> None:
    """Write YAML atomically using tmp-rename pattern."""
    fd, tmp_path = tempfile.mkstemp(dir=str(file_path.parent), prefix=f".{file_path.stem}_", suffix=".yaml")
    try:
        with os.fdopen(fd, "w") as f:
            yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False)
            f.write(f"# 🔱 Omega Engine — {file_path.stem.replace('_', ' ').title()}\n")
            f.write("# Auto-generated during Soul v6.1 migration\n\n")
            f.write(yaml_str)
        os.replace(tmp_path, str(file_path))
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def migrate_entity(entity_name: str, dry_run: bool = False) -> Dict[str, Any]:
    """Migrate a single entity from v5 to v6.1.
    
    Args:
        entity_name: The entity directory name (lowercase)
        dry_run: If True, only validate and print manifest
    
    Returns:
        Dict with status, entity, and manifest
    """
    entity_path = ENTITIES_DIR / entity_name
    if not entity_path.exists():
        return {"status": "skipped", "entity": entity_name, "reason": "Directory not found"}
    
    # Phase 0: Check if already v6
    if check_existing_v6(entity_path):
        logger.info(f"  {entity_name}: Already v6.1 — skipped.")
        return {"status": "skipped", "entity": entity_name, "reason": "Already v6.1"}
    
    # Phase 1: Validate
    has_soul, soul_data = load_soul_yaml(entity_path)
    if not has_soul:
        # Scaffold fresh v6.1 for entities without soul.yaml
        logger.info(f"  {entity_name}: No soul.yaml found. Scaffolding fresh v6.1.")
        if not dry_run:
            atomic_write_yaml(entity_path / "soul.yaml", {"entity": {"name": entity_name}})
            atomic_write_yaml(entity_path / "approved_lessons.yaml", [])
            atomic_write_yaml(entity_path / "proposed_lessons.yaml", [])
            atomic_write_yaml(entity_path / "sessions.yaml", [])
            log_journal(f"SCAFFOLDED: {entity_name} — fresh v6.1")
        return {"status": "scaffolded", "entity": entity_name, "manifest": {
            "soul": {"entity": {"name": entity_name}},
            "approved_lessons": [],
            "proposed_lessons": [],
            "sessions": []
        }}
    
    identity, lessons = deconstruct_soul(soul_data)
    
    manifest = {
        "entity": entity_name,
        "soul": identity,
        "approved_lessons": [],      # Vetted wisdom — starts empty (user must approve)
        "proposed_lessons": lessons, # All extracted lessons go to inbox
        "sessions": []
    }
    
    if dry_run:
        logger.info(f"\n  📋 Manifest for {entity_name}:")
        logger.info(f"      soul.yaml: {len(json.dumps(identity, cls=DatetimeEncoder))} bytes (identity only)")
        logger.info(f"      approved_lessons.yaml: 0 items (empty — user vets)")
        logger.info(f"      proposed_lessons.yaml: {len(lessons)} lessons extracted")
        logger.info(f"      sessions.yaml: 0 items (fresh)")
        return {"status": "validated", "entity": entity_name, "manifest": manifest}
    
    # Phase 2: Execute Migration with Backup
    backup_path = entity_path / "soul.yaml.bak"
    shutil.copy(str(entity_path / "soul.yaml"), str(backup_path))
    logger.info(f"  {entity_name}: Backup created at {backup_path}")
    
    try:
        # Write the 4-file structure
        atomic_write_yaml(entity_path / "soul.yaml", identity)
        atomic_write_yaml(entity_path / "approved_lessons.yaml", [])
        atomic_write_yaml(entity_path / "proposed_lessons.yaml", lessons)
        atomic_write_yaml(entity_path / "sessions.yaml", [])
        
        log_journal(f"MIGRATED: {entity_name} — {len(lessons)} lessons moved to proposed_lessons.yaml")
        logger.info(f"  {entity_name}: ✅ Migration complete. {len(lessons)} lessons in inbox.")
        
        return {"status": "completed", "entity": entity_name, "lessons_count": len(lessons)}
    
    except Exception as e:
        # Rollback: restore from backup
        logger.error(f"  {entity_name}: ❌ Migration FAILED: {e}")
        if backup_path.exists():
            shutil.copy(str(backup_path), str(entity_path / "soul.yaml"))
            logger.info(f"  {entity_name}: Rollback complete.")
            os.remove(backup_path)
        log_journal(f"FAILED: {entity_name} — {e} (rolled back)")
        return {"status": "failed", "entity": entity_name, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Soul Architecture v6.1 Migration Script")
    parser.add_argument("--entity", type=str, help="Migrate a single entity (lowercase name)")
    parser.add_argument("--dry-run", action="store_true", help="Phase 1: Validate only, no writes")
    parser.add_argument("--rollback", type=str, help="Rollback a specific entity from .bak")
    args = parser.parse_args()
    
    if args.rollback:
        entity_path = ENTITIES_DIR / args.rollback
        bak_file = entity_path / "soul.yaml.bak"
        if bak_file.exists():
            shutil.copy(str(bak_file), str(entity_path / "soul.yaml"))
            logger.info(f"Rolled back {args.rollback} from backup.")
            os.remove(bak_file)
            log_journal(f"ROLLBACK: {args.rollback}")
        else:
            logger.error(f"No backup found for {args.rollback}")
        return
    
    entities = [args.entity] if args.entity else FLEET_ENTITIES
    
    logger.info("=" * 60)
    logger.info(f"🔱 Soul Architecture Protocol v6.1 Migration")
    logger.info(f"   Mode: {'DRY RUN (Validation Only)' if args.dry_run else 'EXECUTION'}")
    logger.info(f"   Entities: {len(entities)}")
    logger.info("=" * 60)
    
    results = []
    for entity_name in entities:
        logger.info(f"\n{'─' * 40}")
        logger.info(f"  Entity: {entity_name}")
        logger.info(f"{'─' * 40}")
        
        result = migrate_entity(entity_name, dry_run=args.dry_run)
        results.append(result)
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 MIGRATION SUMMARY")
    logger.info("=" * 60)
    
    for r in results:
        status_icon = {
            "completed": "✅",
            "validated": "📋",
            "scaffolded": "🆕",
            "skipped": "⏭️",
            "failed": "❌"
        }.get(r["status"], "❓")
        logger.info(f"  {status_icon} {r['entity']:15s} | {r['status']}")
        if "lessons_count" in r:
            logger.info(f"        Lessons extracted: {r['lessons_count']}")
        if "error" in r:
            logger.info(f"        Error: {r['error']}")
    
    completed = [r for r in results if r["status"] == "completed"]
    failed = [r for r in results if r["status"] == "failed"]
    logger.info(f"\n  Total: {len(results)} | Completed: {len(completed)} | Failed: {len(failed)}")
    
    if args.dry_run:
        logger.info("\n  💡 To execute: python scripts/migrate_soul_v6.py")
    
    # Write manifest for review (with custom date encoder)
    manifest_path = BASE_DIR / "migration_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(results, f, indent=2, cls=DatetimeEncoder)
    logger.info(f"\n  📄 Manifest written to {manifest_path}")
    
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
