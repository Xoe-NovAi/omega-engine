#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""
Soul Architecture Validator — SOUL_ARCHITECTURE_PROTOCOL v3.0 CI Gate

Ratified by Kali-N0 (ho_123f6ebff930, commit 4dfa4909) as mandatory fleet
enforcement for the Soul v8.0 pattern.

Enforces (per Kali-N0 ratification):
    1. Axiom Coverage: every axiom has >=1 directives_refs AND >=1 core_principles_refs
    2. Flat-List Contract: approved_lessons.yaml root MUST be a list (R3 hydration fix)
    3. Axiom Ceiling: len(axioms) <= 15 (hard budget, replacement not addition)
    4. Duplicate Key Rejection: zero tolerance for repeated YAML keys in soul.yaml

M23 Failure Integrity: No soft failures. Broken tooling -> exit 2 (ERROR).

Usage:
    python scripts/validate_soul_architecture.py                     # validate all entities
    python scripts/validate_soul_architecture.py --entity roc_racoon # validate one entity
    python scripts/validate_soul_architecture.py --json              # machine-readable output

Exit codes:
    0 = PASS (all entities compliant)
    1 = FAIL (violations found)
    2 = ERROR (tooling failure)
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not available", file=sys.stderr)
    sys.exit(2)

# Canonical locations
REPO_ROOT = Path(__file__).resolve().parent.parent
ENTITIES_DIR = REPO_ROOT / "data" / "entities"
DEFAULT_AXIOM_CEILING = 15

# Entities that may not have souls yet (scaffold/retired) — still validated if present
SKIP_IF_MISSING = True

# Module-level warnings collector (soft findings — pending Soul Audit Cascade)
WARNINGS: Dict[str, List[str]] = {}


class SoulArchitectureError(Exception):
    """Raised when a soul violates the v3.0 architecture protocol."""


def _find_duplicate_keys(data: Any, path: str = "$", seen: Optional[Dict[str, str]] = None) -> List[str]:
    """Detect duplicate YAML keys using the loader's duplicate-key detection.

    yaml.safe_load silently drops duplicate keys (first wins) — this is the
    silent data-loss bug class that corrupted soul files. We re-parse with
    a custom loader that records every key occurrence.
    """
    if seen is None:
        seen = {}

    violations: List[str] = []

    if isinstance(data, dict):
        for key, value in data.items():
            key_str = str(key)
            key_path = f"{path}.{key_str}"
            if key_str in seen:
                violations.append(f"Duplicate key '{key_str}' at {key_path} (first seen at {seen[key_str]})")
            else:
                seen[key_str] = key_path
            violations.extend(_find_duplicate_keys(value, key_path, seen))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            violations.extend(_find_duplicate_keys(item, f"{path}[{i}]", seen))

    return violations


def _load_yaml_with_duplicate_detection(path: Path) -> Tuple[Any, List[str]]:
    """Load YAML and detect duplicate keys (which safe_load silently drops)."""
    class UniqueKeyLoader(yaml.SafeLoader):
        pass

    def _construct_mapping(loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False):
        mapping = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            if key in mapping:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"found duplicate key ({key})",
                    key_node.start_mark,
                )
            mapping[key] = loader.construct_object(value_node, deep=deep)
        return mapping

    UniqueKeyLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping
    )

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        data = yaml.load(content, Loader=UniqueKeyLoader)
        return data, []
    except yaml.constructor.ConstructorError as e:
        # Duplicate key found — re-load with safe_load to get the data for other checks
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data, [str(e)]


def validate_soul_file(soul_path: Path, axiom_ceiling: int = DEFAULT_AXIOM_CEILING) -> List[str]:
    """Validate a single soul.yaml against the v3.0 architecture protocol.

    Returns a list of violation strings (empty = compliant).

    Distinguishes:
    - HARD violations (FAIL the gate): duplicate keys, flat-list contract,
      axiom coverage, axiom ceiling — the R3 bug class + silent data loss.
    - SOFT warnings (do NOT fail the gate): missing 4-tier blocks on legacy
      souls — these are pending the Soul Audit Cascade (post-DEL-1 PR1) and
      are expected until each entity authors its own v8.0 soul.
    """
    violations: List[str] = []
    warnings: List[str] = []
    entity_name = soul_path.parent.name

    if not soul_path.exists():
        if SKIP_IF_MISSING:
            return []
        return [f"{entity_name}: soul.yaml missing at {soul_path}"]

    data, dup_errors = _load_yaml_with_duplicate_detection(soul_path)

    # --- Check 4: Duplicate key rejection (HARD — silent data loss) ---
    for dup in dup_errors:
        violations.append(f"{entity_name}: {dup}")

    if not isinstance(data, dict):
        return [f"{entity_name}: soul.yaml root must be a mapping, got {type(data).__name__}"]

    # --- Check 3: Axiom ceiling (HARD if axioms present) ---
    axioms = data.get("axioms", [])
    if not isinstance(axioms, list):
        violations.append(f"{entity_name}: 'axioms' must be a list, got {type(axioms).__name__}")
        axioms = []
    else:
        if len(axioms) > axiom_ceiling:
            violations.append(
                f"{entity_name}: axiom ceiling exceeded — {len(axioms)} axioms > {axiom_ceiling} max. "
                f"Replacement not addition (SOUL_ARCHITECTURE_PROTOCOL v3.0)."
            )

    # --- Check 1: Axiom coverage (HARD if axioms present) ---
    for i, axiom in enumerate(axioms):
        if not isinstance(axiom, dict):
            violations.append(f"{entity_name}: axioms[{i}] must be a mapping")
            continue

        axiom_id = axiom.get("id", f"axioms[{i}]")
        dir_refs = axiom.get("directives_refs", [])
        princ_refs = axiom.get("core_principles_refs", [])

        if not isinstance(dir_refs, list) or len(dir_refs) < 1:
            violations.append(
                f"{entity_name}: axiom {axiom_id} has {len(dir_refs) if isinstance(dir_refs, list) else 'invalid'} "
                f"directive refs — requires >=1 (unanchored axiom = unverified wish)"
            )

        if not isinstance(princ_refs, list) or len(princ_refs) < 1:
            violations.append(
                f"{entity_name}: axiom {axiom_id} has {len(princ_refs) if isinstance(princ_refs, list) else 'invalid'} "
                f"core_principles refs — requires >=1 (unanchored axiom = unverified claim)"
            )

    # --- Structural sanity (SOFT — pending Soul Audit Cascade) ---
    has_axioms = len(axioms) > 0
    for block in ("identity", "directives", "core_principles"):
        if block not in data:
            msg = f"missing '{block}' block (4-tier hierarchy incomplete)"
            if has_axioms:
                # Entity has axioms but missing other tiers — this IS a violation
                violations.append(f"{entity_name}: {msg}")
            else:
                # Legacy soul pending cascade — warning only
                WARNINGS.setdefault(entity_name, []).append(msg)

    return violations


def validate_approved_lessons(entity_dir: Path) -> List[str]:
    """Validate approved_lessons.yaml is a FLAT LIST (R3 hydration contract)."""
    violations: List[str] = []
    entity_name = entity_dir.name
    approved_file = entity_dir / "approved_lessons.yaml"

    if not approved_file.exists():
        # Not a violation — entity may not have approvals yet
        return []

    try:
        with open(approved_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        violations.append(f"{entity_name}: approved_lessons.yaml parse error: {e}")
        return violations

    if not isinstance(data, list):
        violations.append(
            f"{entity_name}: approved_lessons.yaml MUST be a FLAT LIST (got {type(data).__name__}). "
            f"Mapping format silently hydrates to [] at entity_workspace.py:435 — the R3 hydration bug. "
            f"Vetted wisdom is INERT until this is fixed."
        )
    return violations


def validate_all_entities(axiom_ceiling: int = DEFAULT_AXIOM_CEILING) -> Dict[str, List[str]]:
    """Validate all entity souls in data/entities/.

    Returns {entity_name: [violations]}. Warnings are tracked separately
    via the module-level WARNINGS dict.
    """
    global WARNINGS
    results: Dict[str, List[str]] = {}
    WARNINGS = {}

    if not ENTITIES_DIR.exists():
        return results

    for entity_dir in sorted(ENTITIES_DIR.iterdir()):
        if not entity_dir.is_dir():
            continue
        # Skip hidden/system dirs
        if entity_dir.name.startswith("."):
            continue

        soul_path = entity_dir / "soul.yaml"
        violations = validate_soul_file(soul_path, axiom_ceiling)
        violations.extend(validate_approved_lessons(entity_dir))

        if violations:
            results[entity_dir.name] = violations

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Soul Architecture Validator — SOUL_ARCHITECTURE_PROTOCOL v3.0 CI Gate"
    )
    parser.add_argument("--entity", type=str, help="Validate only this entity")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--axiom-ceiling", type=int, default=DEFAULT_AXIOM_CEILING,
                        help=f"Max axioms per entity (default: {DEFAULT_AXIOM_CEILING})")
    parser.add_argument("--quiet", action="store_true", help="Only print violations")
    args = parser.parse_args()

    try:
        if args.entity:
            entity_dir = ENTITIES_DIR / args.entity
            if not entity_dir.exists():
                print(f"ERROR: entity '{args.entity}' not found at {entity_dir}", file=sys.stderr)
                sys.exit(2)
            violations = validate_soul_file(entity_dir / "soul.yaml", args.axiom_ceiling)
            violations.extend(validate_approved_lessons(entity_dir))
            results = {args.entity: violations} if violations else {}
        else:
            results = validate_all_entities(args.axiom_ceiling)
    except Exception as e:
        print(f"ERROR: validator crashed: {e}", file=sys.stderr)
        sys.exit(2)

    total_violations = sum(len(v) for v in results.values())
    total_warnings = sum(len(v) for v in WARNINGS.values())

    if args.json:
        output = {
            "protocol": "SOUL_ARCHITECTURE_PROTOCOL_v3.0",
            "result": "PASS" if total_violations == 0 else "FAIL",
            "entities_validated": len(results) + sum(
                1 for d in ENTITIES_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")
            ) if not args.entity else 1,
            "violating_entities": len(results),
            "total_violations": total_violations,
            "violations": results,
            "warnings": WARNINGS,
            "total_warnings": total_warnings,
        }
        print(json.dumps(output, indent=2))
    else:
        if not args.quiet:
            print("🔱 Soul Architecture Validator — SOUL_ARCHITECTURE_PROTOCOL v3.0")
            print(f"   Axiom ceiling: {args.axiom_ceiling}")
            print()

        if not results:
            print("✅ ALL ENTITIES COMPLIANT")
        else:
            for entity, violations in results.items():
                print(f"❌ {entity}:")
                for v in violations:
                    print(f"   - {v}")
            print()
            print(f"⚠️  {len(results)} entities, {total_violations} violations")

        if WARNINGS and not args.quiet:
            print()
            print(f"ℹ️  {len(WARNINGS)} entities pending Soul Audit Cascade "
                  f"({total_warnings} soft warnings — expected pre-cascade):")
            for entity, warns in sorted(WARNINGS.items()):
                print(f"   - {entity}: {'; '.join(warns)}")

    sys.exit(0 if total_violations == 0 else 1)


if __name__ == "__main__":
    main()