#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""WAD Validation Tool — pre-load structural validation for Omega Engine WADs.

Usage:
    python scripts/validate_wad.py <wad_dir>
    python scripts/validate_wad.py config/wads/arcana_novai
    python scripts/validate_wad.py config/wads/_omega_default

Exit codes:
    0 — valid WAD
    1 — validation errors found
"""

import sys
import os
import yaml
from pathlib import Path
from typing import List, Tuple

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

MAX_YAML_SIZE = 1 * 1024 * 1024  # 1 MB

MANIFEST_REQUIRED = ["name", "version", "entities"]
MANIFEST_KNOWN = {
    "name", "version", "entities", "author", "description", "license",
    "type", "mode", "requires_engine", "startup", "voices", "vr_scenes",
    "dependencies", "hierarchy", "adapters", "priority",
}
MANIFEST_TYPES = {
    "name": str, "version": str, "entities": (list, dict),
    "author": str, "description": str, "license": str,
    "type": str, "mode": str, "requires_engine": str,
    "startup": dict, "voices": (list, dict), "vr_scenes": (list, dict),
    "dependencies": (list, dict), "hierarchy": str, "adapters": (list, dict),
    "priority": int,
}
ENTITY_FIELDS = {
    "name": str, "domains": list, "model": str, "personality": str,
    "temperature": (int, float), "context_window": int, "slots": list,
    "role": str, "container": bool, "port": (int, type(None)),
    "nodes": list, "sovereignty": (str, dict, list, type(None)),
}
CORE_ENTITY_FIELDS = {
    "name", "domains", "model", "personality", "temperature",
    "context_window", "slots", "role", "container", "port",
    "wad_source", "priority", "nodes", "sovereignty", "metadata",
}


def validate_manifest(wad_path: Path) -> List[str]:
    errors = []
    manifest_path = wad_path / "manifest.yaml"
    if not manifest_path.exists():
        return ["manifest.yaml not found"]
    if manifest_path.stat().st_size > MAX_YAML_SIZE:
        return [f"manifest.yaml too large ({manifest_path.stat().st_size} bytes)"]
    try:
        data = yaml.safe_load(manifest_path.read_text())
    except yaml.YAMLError as e:
        return [f"manifest.yaml parse error: {e}"]
    if data is None:
        return ["manifest.yaml is empty"]
    if "wad" in data:
        data = data["wad"]
    for field in MANIFEST_REQUIRED:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    for field, expected in MANIFEST_TYPES.items():
        if field in data and not isinstance(data[field], expected):
            errors.append(f"Field '{field}' has wrong type: expected {expected}, got {type(data[field]).__name__}")
    unknown = set(data.keys()) - MANIFEST_KNOWN
    if unknown:
        errors.append(f"Unknown manifest fields: {sorted(unknown)}")
    if data.get("name", "").strip() == "":
        errors.append("Field 'name' is empty")
    if data.get("version", "").strip() == "":
        errors.append("Field 'version' is empty")
    # Check requires_engine
    if "requires_engine" in data:
        try:
            from packaging.specifiers import SpecifierSet
            SpecifierSet(data["requires_engine"])
        except Exception as e:
            errors.append(f"Invalid requires_engine: {e}")
    # Check voices reference
    if "voices" in data and isinstance(data["voices"], dict):
        primary = data["voices"].get("primary")
        if primary:
            voice_path = wad_path / "voices" / primary
            if not voice_path.exists():
                errors.append(f"Voice file not found: voices/{primary}")
    # Check hierarchy reference
    if "hierarchy" in data and isinstance(data["hierarchy"], str):
        h_path = wad_path / data["hierarchy"]
        if not h_path.exists():
            errors.append(f"Hierarchy file not found: {data['hierarchy']}")
    else:
        default_h = wad_path / "hierarchy.yaml"
        if default_h.exists():
            pass  # OK, default exists
    # Check dependencies
    deps = data.get("dependencies", [])
    if isinstance(deps, str):
        deps = [deps]
    for dep in deps:
        if not isinstance(dep, str):
            errors.append(f"Dependency must be a string, got {type(dep).__name__}")
            continue
        # Dependencies may live in other WAD directories — not a hard error
    return errors


def validate_entities(wad_path: Path) -> List[str]:
    errors = []
    entities_dir = wad_path / "entities"
    if not entities_dir.exists():
        return []  # No entities dir is OK
    for yaml_file in entities_dir.rglob("*.yaml"):
        if yaml_file.name == "soul.yaml":
            continue
        try:
            if yaml_file.stat().st_size > MAX_YAML_SIZE:
                errors.append(f"{yaml_file.relative_to(wad_path)}: too large ({yaml_file.stat().st_size} bytes)")
                continue
            data = yaml.safe_load(yaml_file.read_text())
        except yaml.YAMLError as e:
            errors.append(f"{yaml_file.relative_to(wad_path)}: parse error: {e}")
            continue
        if data is None:
            continue  # Empty file, skip
        # Check if it's an entity file (has entity: key) or dispatch/other
        if "entity" not in data:
            continue  # Not an entity file (could be dispatch.yaml, soul.yaml, etc.)
        ent = data["entity"]
        if not isinstance(ent, dict):
            errors.append(f"{yaml_file.relative_to(wad_path)}: 'entity' is not a dict")
            continue
        if "name" not in ent:
            errors.append(f"{yaml_file.relative_to(wad_path)}: missing 'name' field")
        if "domains" not in ent:
            errors.append(f"{yaml_file.relative_to(wad_path)}: missing 'domains' field")
        # Type validation
        for field, expected in ENTITY_FIELDS.items():
            if field in ent and not isinstance(ent[field], expected):
                errors.append(f"{yaml_file.relative_to(wad_path)}: field '{field}' has wrong type: expected {expected}, got {type(ent[field]).__name__}")
        # Range checks
        if "temperature" in ent:
            t = ent["temperature"]
            if not (0.0 <= t <= 2.0):
                errors.append(f"{yaml_file.relative_to(wad_path)}: temperature={t} out of range [0.0, 2.0]")
        if "context_window" in ent:
            c = ent["context_window"]
            if not (1 <= c <= 131072):
                errors.append(f"{yaml_file.relative_to(wad_path)}: context_window={c} out of range [1, 131072]")
        if "domains" in ent and len(ent["domains"]) > 20:
            errors.append(f"{yaml_file.relative_to(wad_path)}: too many domains ({len(ent['domains'])})")
        if "name" in ent and len(str(ent["name"])) > 128:
            errors.append(f"{yaml_file.relative_to(wad_path)}: name too long")
    return errors


def validate_voices(wad_path: Path) -> List[str]:
    errors = []
    voices_dir = wad_path / "voices"
    if not voices_dir.exists():
        return []
    for voice_file in voices_dir.glob("*.yaml"):
        try:
            data = yaml.safe_load(voice_file.read_text())
        except yaml.YAMLError as e:
            errors.append(f"voices/{voice_file.name}: parse error: {e}")
            continue
        if data is None:
            continue
        if "voice" not in data:
            errors.append(f"voices/{voice_file.name}: missing 'voice' key")
            continue
        v = data["voice"]
        if not isinstance(v, dict):
            errors.append(f"voices/{voice_file.name}: 'voice' is not a dict")
            continue
        if "name" not in v:
            errors.append(f"voices/{voice_file.name}: missing 'name'")
        if "personality" not in v:
            errors.append(f"voices/{voice_file.name}: missing 'personality'")
    return errors


def validate_hierarchy(wad_path: Path) -> List[str]:
    errors = []
    # Check manifest hierarchy reference or default
    manifest_path = wad_path / "manifest.yaml"
    if manifest_path.exists():
        data = yaml.safe_load(manifest_path.read_text())
        if data and "wad" in data:
            data = data["wad"]
        if data and "hierarchy" in data and isinstance(data["hierarchy"], str):
            h_path = wad_path / data["hierarchy"]
        else:
            h_path = wad_path / "hierarchy.yaml"
        if h_path.exists():
            try:
                h_data = yaml.safe_load(h_path.read_text())
                if h_data is None:
                    errors.append(f"hierarchy file is empty: {h_path.name}")
            except yaml.YAMLError as e:
                errors.append(f"hierarchy file parse error: {e}")
    return errors



def validate_souls(wad_path: Path) -> List[str]:
    errors = []
    for soul_file in wad_path.rglob("soul.yaml"):
        try:
            if soul_file.stat().st_size > MAX_YAML_SIZE:
                errors.append(f"{soul_file.relative_to(wad_path)}: too large")
                continue
            data = yaml.safe_load(soul_file.read_text())
        except yaml.YAMLError as e:
            errors.append(f"{soul_file.relative_to(wad_path)}: parse error: {e}")
            continue
        if data is None:
            continue
        # soul.yaml should have identity or entity section
        if "identity" in data:
            ident = data["identity"]
        elif "entity" in data:
            ident = data["entity"]
        else:
            errors.append(f"{soul_file.relative_to(wad_path)}: missing 'identity' or 'entity' section")
            continue
        if not isinstance(ident, dict):
            errors.append(f"{soul_file.relative_to(wad_path)}: 'identity' is not a dict")
            continue
        if "keeper" not in ident and "id" not in ident and "name" not in ident:
            errors.append(f"{soul_file.relative_to(wad_path)}: identity/entity missing 'keeper', 'id', or 'name'")
        # axioms should be a list if present
        if "axioms" in data and not isinstance(data["axioms"], list):
            errors.append(f"{soul_file.relative_to(wad_path)}: 'axioms' is not a list")
        # directives should be a list if present
        if "directives" in data and not isinstance(data["directives"], list):
            errors.append(f"{soul_file.relative_to(wad_path)}: 'directives' is not a list")
        # voice should be a dict if present
        if "voice" in data and not isinstance(data["voice"], dict):
            errors.append(f"{soul_file.relative_to(wad_path)}: 'voice' is not a dict")
    return errors


def validate_card_assignments(wad_path: Path) -> List[str]:
    errors = []
    for card_file in wad_path.rglob("card_assignment*.yaml"):
        try:
            data = yaml.safe_load(card_file.read_text())
        except yaml.YAMLError as e:
            errors.append(f"{card_file.relative_to(wad_path)}: parse error: {e}")
            continue
        if data is None:
            continue
        if "card" not in data:
            errors.append(f"{card_file.relative_to(wad_path)}: missing 'card' section")
            continue
        card = data["card"]
        if not isinstance(card, dict):
            errors.append(f"{card_file.relative_to(wad_path)}: 'card' is not a dict")
            continue
        for field in ["arcana", "key", "title", "keeper"]:
            if field not in card:
                errors.append(f"{card_file.relative_to(wad_path)}: card missing '{field}'")
    return errors



def validate_world(wad_path: Path) -> List[str]:
    errors = []
    world_dir = wad_path / "world"
    if not world_dir.exists():
        return []
    for lump_file in world_dir.rglob("*.yaml"):
        try:
            if lump_file.stat().st_size > MAX_YAML_SIZE:
                errors.append(f"{lump_file.relative_to(wad_path)}: too large ({lump_file.stat().st_size} bytes)")
                continue
            data = yaml.safe_load(lump_file.read_text())
        except yaml.YAMLError as e:
            errors.append(f"{lump_file.relative_to(wad_path)}: parse error: {e}")
            continue
        if data is None:
            continue
        # Check path traversal
        try:
            resolved = lump_file.resolve()
            if not str(resolved).startswith(str(wad_path.resolve())):
                errors.append(f"{lump_file.relative_to(wad_path)}: path traversal detected")
        except (OSError, RuntimeError):
            pass
    return errors


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/validate_wad.py <wad_dir>")
        sys.exit(1)
    wad_path = Path(sys.argv[1]).resolve()
    if not wad_path.is_dir():
        print(f"Error: {wad_path} is not a directory")
        sys.exit(1)

    print(f"Validating WAD: {wad_path.name}")
    print(f"Path: {wad_path}")
    print()

    all_errors = []
    all_errors.extend(validate_manifest(wad_path))
    all_errors.extend(validate_entities(wad_path))
    all_errors.extend(validate_voices(wad_path))
    all_errors.extend(validate_hierarchy(wad_path))
    all_errors.extend(validate_souls(wad_path))
    all_errors.extend(validate_world(wad_path))
    all_errors.extend(validate_card_assignments(wad_path))

    if all_errors:
        print(f"FAIL: {len(all_errors)} error(s) found:")
        for e in all_errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("PASS: WAD is valid")
        sys.exit(0)


if __name__ == "__main__":
    main()
PYEOF
