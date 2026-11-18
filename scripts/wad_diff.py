#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""WAD Diff Tool — structural comparison between two WAD directories (Phase 4.3).

Usage:
    python scripts/wad_diff.py <wad_a> <wad_b> [--json]

Exit codes:
    0 — identical
    1 — differences found
    2 — usage error
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import yaml


def _collect_files(wad_path: Path) -> dict[str, str]:
    """Return {relative_path: sha256} for all files in a WAD."""
    hashes = {}
    for f in sorted(wad_path.rglob("*")):
        if f.is_file():
            rel = str(f.relative_to(wad_path))
            hashes[rel] = hashlib.sha256(f.read_bytes()).hexdigest()
    return hashes


def _collect_entities(wad_path: Path) -> dict[str, dict]:
    """Return {entity_name: entity_dict} for all entities in a WAD."""
    entities = {}
    entities_dir = wad_path / "entities"
    if not entities_dir.exists():
        return entities
    for yaml_file in entities_dir.rglob("*.yaml"):
        try:
            data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        if not isinstance(data, dict) or "entity" not in data:
            continue
        ent = data["entity"]
        if isinstance(ent, dict) and "name" in ent:
            entities[ent["name"]] = ent
    return entities


def diff_wads(wad_a: Path, wad_b: Path) -> dict:
    """Compute structural diff between two WADs."""
    files_a = _collect_files(wad_a)
    files_b = _collect_files(wad_b)

    files_only_a = sorted(set(files_a) - set(files_b))
    files_only_b = sorted(set(files_b) - set(files_a))
    files_changed = sorted(
        k for k in (set(files_a) & set(files_b)) if files_a[k] != files_b[k]
    )

    entities_a = _collect_entities(wad_a)
    entities_b = _collect_entities(wad_b)

    entities_only_a = sorted(set(entities_a) - set(entities_b))
    entities_only_b = sorted(set(entities_b) - set(entities_a))
    entities_changed = []
    for name in sorted(set(entities_a) & set(entities_b)):
        if entities_a[name] != entities_b[name]:
            changed_fields = [
                k for k in set(entities_a[name]) | set(entities_b[name])
                if entities_a[name].get(k) != entities_b[name].get(k)
            ]
            entities_changed.append({"name": name, "changed_fields": changed_fields})

    # Manifest comparison
    manifest_a = {}
    manifest_b = {}
    for wad, manifest in ((wad_a, manifest_a), (wad_b, manifest_b)):
        mp = wad / "manifest.yaml"
        if mp.exists():
            try:
                raw = yaml.safe_load(mp.read_text(encoding="utf-8"))
                manifest.update(raw.get("wad", raw) if isinstance(raw, dict) else {})
            except yaml.YAMLError:
                pass

    manifest_diff = {}
    for key in sorted(set(manifest_a) | set(manifest_b)):
        if manifest_a.get(key) != manifest_b.get(key):
            manifest_diff[key] = {
                "a": manifest_a.get(key),
                "b": manifest_b.get(key),
            }

    return {
        "wad_a": str(wad_a),
        "wad_b": str(wad_b),
        "files": {
            "only_in_a": files_only_a,
            "only_in_b": files_only_b,
            "changed": files_changed,
        },
        "entities": {
            "only_in_a": entities_only_a,
            "only_in_b": entities_only_b,
            "changed": entities_changed,
        },
        "manifest": manifest_diff,
        "identical": (
            not files_only_a
            and not files_only_b
            and not files_changed
            and not entities_only_a
            and not entities_only_b
            and not entities_changed
            and not manifest_diff
        ),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Diff two Omega Engine WADs.")
    parser.add_argument("wad_a", help="First WAD directory")
    parser.add_argument("wad_b", help="Second WAD directory")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args(argv)

    wad_a = Path(args.wad_a).resolve()
    wad_b = Path(args.wad_b).resolve()

    if not wad_a.is_dir():
        print(f"Error: {wad_a} is not a directory", file=sys.stderr)
        return 2
    if not wad_b.is_dir():
        print(f"Error: {wad_b} is not a directory", file=sys.stderr)
        return 2

    result = diff_wads(wad_a, wad_b)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        if result["identical"]:
            print(f"IDENTICAL: {wad_a.name} == {wad_b.name}")
        else:
            print(f"DIFF: {wad_a.name} vs {wad_b.name}")
            if result["files"]["only_in_a"]:
                print(f"  Files only in {wad_a.name}: {result['files']['only_in_a']}")
            if result["files"]["only_in_b"]:
                print(f"  Files only in {wad_b.name}: {result['files']['only_in_b']}")
            if result["files"]["changed"]:
                print(f"  Changed files: {result['files']['changed']}")
            if result["entities"]["only_in_a"]:
                print(f"  Entities only in {wad_a.name}: {result['entities']['only_in_a']}")
            if result["entities"]["only_in_b"]:
                print(f"  Entities only in {wad_b.name}: {result['entities']['only_in_b']}")
            if result["entities"]["changed"]:
                for ec in result["entities"]["changed"]:
                    print(f"  Changed entity '{ec['name']}': {ec['changed_fields']}")
            if result["manifest"]:
                print(f"  Manifest differences: {list(result['manifest'].keys())}")

    return 0 if result["identical"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
PYEOF