#!/usr/bin/env python3
"""
Validate sote.yaml against JSON Schema.

Usage: python scripts/validate_sote_schema.py [week_folder]
"""

import sys
import json
import yaml
from pathlib import Path
from jsonschema import validate, ValidationError

SCHEMA_PATH = Path("schemas/sote/sote-schema.json")

def load_schema():
    """Load JSON Schema for sote.yaml."""
    if not SCHEMA_PATH.exists():
        print(f"Schema not found at {SCHEMA_PATH}")
        return None
    return json.loads(SCHEMA_PATH.read_text())

def validate_sote_yaml(week_folder: Path, schema: dict) -> bool:
    """Validate a single sote.yaml file."""
    sote_yaml = week_folder / "sote.yaml"
    if not sote_yaml.exists():
        print(f"sote.yaml not found in {week_folder}")
        return False
    
    try:
        data = yaml.safe_load(sote_yaml.read_text())
        validate(instance=data, schema=schema)
        print(f"✓ {week_folder.name}/sote.yaml valid")
        return True
    except ValidationError as e:
        print(f"✗ {week_folder.name}/sote.yaml INVALID: {e.message}")
        print(f"  Path: {' -> '.join(str(p) for p in e.path)}")
        return False
    except yaml.YAMLError as e:
        print(f"✗ {week_folder.name}/sote.yaml YAML ERROR: {e}")
        return False

def main():
    if len(sys.argv) > 1:
        week_folder = Path(sys.argv[1])
    else:
        # Default to current week
        week_folder = Path(f"docs/strategy/sote/{__import__('datetime').datetime.now().strftime('%Y-W%V')}")
    
    schema = load_schema()
    if schema is None:
        print("ERROR: Schema not found. Run 'make sote-schema' to generate.")
        sys.exit(1)
    
    if week_folder.is_dir():
        # Validate single week
        if not validate_sote_yaml(week_folder, schema):
            sys.exit(1)
    else:
        # Validate all weeks
        sote_root = Path("docs/strategy/sote")
        all_valid = True
        for week in sorted(sote_root.iterdir()):
            if week.is_dir() and week.name.startswith("20"):
                if not validate_sote_yaml(week, schema):
                    all_valid = False
        if not all_valid:
            sys.exit(1)
    
    print("All sote.yaml files valid")

if __name__ == "__main__":
    main()