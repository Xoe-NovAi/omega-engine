#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""WAD Linter — automated structural checks for Omega Engine WADs (Phase 3.4).

Usage:
    python scripts/lint_wad.py <wad_dir> [--fix]

Exit codes:
    0 — no errors (warnings allowed)
    1 — lint errors found
    2 — usage/invocation error
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import yaml  # noqa: E402

MAX_YAML_SIZE = 1 * 1024 * 1024
AXIOM_CEILING = 20


def _file_hashes(directory: Path) -> dict:
    hashes = {}
    for f in sorted(directory.rglob("*")):
        if f.is_file():
            rel = str(f.relative_to(directory))
            hashes[rel] = hashlib.sha256(f.read_bytes()).hexdigest()
    return hashes


def _check_duplicate_keys(path: Path) -> list[str]:
    """Use UniqueKeyLoader to detect duplicate YAML keys (silent data loss)."""
    errors: list[str] = []
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{path.name}: unreadable ({exc})"]

    class UniqueKeyLoader(yaml.SafeLoader):
        pass

    def construct_mapping(loader, node, deep=False):
        mapping = {}
        for key_node, value_node in node.value:
            try:
                key = loader.construct_object(key_node, deep=deep)
            except Exception:
                # Unhashable key (e.g. nested mapping) — delegate to safe loader
                return yaml.SafeLoader.construct_mapping(loader, node, deep=deep)
            if not isinstance(key, (str, int, float, bool, tuple, frozenset, bytes)):
                # Unhashable or complex key — delegate to safe loader
                return yaml.SafeLoader.construct_mapping(loader, node, deep=deep)
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
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping
    )
    try:
        yaml.load(content, Loader=UniqueKeyLoader)
    except yaml.constructor.ConstructorError as exc:
        errors.append(f"{path.name}: duplicate key — {exc}")
    except yaml.YAMLError as exc:
        errors.append(f"{path.name}: parse error — {exc}")
    return errors


def lint_wad(wad_path: Path) -> list[str]:
    """Run all lint checks on a WAD directory. Returns list of error strings."""
    errors: list[str] = []
    warnings: list[str] = []

    if not wad_path.is_dir():
        return [f"{wad_path} is not a directory"]

    # 1. Manifest checks
    manifest_path = wad_path / "manifest.yaml"
    if not manifest_path.exists():
        errors.append("manifest.yaml missing")
    else:
        try:
            raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            manifest = raw.get("wad", raw) if isinstance(raw, dict) else raw
            if not isinstance(manifest, dict):
                errors.append("manifest.yaml root must be a mapping")
            else:
                for field in ("name", "version", "entities"):
                    if field not in manifest:
                        errors.append(f"manifest missing required field: {field}")
                if manifest.get("type") == "pwad" and "dependencies" in manifest:
                    deps = manifest.get("dependencies", [])
                    if isinstance(deps, list) and IWAD_DEFAULT not in deps and deps:
                        pass  # PWADs may declare no IWAD dep (optional)
        except yaml.YAMLError as exc:
            errors.append(f"manifest.yaml parse error: {exc}")

    # 2. Duplicate-key checks across all YAML files
    for yaml_file in wad_path.rglob("*.yaml"):
        # Skip template files (Jinja placeholders)
        try:
            content = yaml_file.read_text(encoding="utf-8")
            if "{{" in content:
                continue
        except OSError:
            continue
        errors.extend(
            f"{yaml_file.relative_to(wad_path)}: {e}"
            for e in _check_duplicate_keys(yaml_file)
        )

    # 3. Soul schema + axiom ceiling
    for soul_file in wad_path.rglob("soul.yaml"):
        rel = soul_file.relative_to(wad_path)
        try:
            data = yaml.safe_load(soul_file.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"{rel}: parse error: {exc}")
            continue
        if not isinstance(data, dict):
            errors.append(f"{rel}: root must be a mapping")
            continue
        if "identity" not in data and "entity" not in data:
            errors.append(f"{rel}: missing 'identity' or 'entity' section")
            continue
        axioms = data.get("axioms", [])
        if isinstance(axioms, list) and len(axioms) > AXIOM_CEILING:
            errors.append(
                f"{rel}: axiom count {len(axioms)} exceeds ceiling {AXIOM_CEILING}"
            )
        for ax in axioms if isinstance(axioms, list) else []:
            if isinstance(ax, dict) and "text" not in ax and "id" not in ax:
                errors.append(f"{rel}: axiom missing 'id' and 'text'")

    # 4. Voice references + missing voice_dna.md
    voices_dir = wad_path / "voices"
    if voices_dir.exists():
        for voice_file in voices_dir.glob("*.yaml"):
            try:
                data = yaml.safe_load(voice_file.read_text(encoding="utf-8"))
            except yaml.YAMLError as exc:
                errors.append(f"voices/{voice_file.name}: parse error: {exc}")
                continue
            if not isinstance(data, dict) or "voice" not in data:
                errors.append(f"voices/{voice_file.name}: missing 'voice' key")
                continue
            v = data["voice"]
            if not isinstance(v, dict):
                errors.append(f"voices/{voice_file.name}: 'voice' is not a dict")
                continue
            if "name" not in v or "personality" not in v:
                errors.append(f"voices/{voice_file.name}: missing 'name' or 'personality'")
            dna_ref = v.get("dna_ref")
            if dna_ref:
                dna_path = wad_path / "entities" / voice_file.stem / dna_ref
                if not dna_path.exists():
                    # dna_ref is relative to entity dir; check common locations
                    alt = wad_path / dna_ref
                    if not alt.exists():
                        warnings.append(
                            f"voices/{voice_file.name}: dna_ref '{dna_ref}' not found"
                        )

    # 5. Missing voice_dna.md referenced by soul.yaml
    for soul_file in wad_path.rglob("soul.yaml"):
        rel = soul_file.relative_to(wad_path)
        try:
            data = yaml.safe_load(soul_file.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        if not isinstance(data, dict):
            continue
        voice = data.get("voice")
        if isinstance(voice, dict):
            dna_ref = voice.get("dna_ref")
            if dna_ref:
                dna_path = soul_file.parent / dna_ref
                if not dna_path.exists():
                    warnings.append(f"{rel}: voice.dna_ref '{dna_ref}' not found")

    # 6. Hierarchy reference integrity
    manifest_path = wad_path / "manifest.yaml"
    if manifest_path.exists():
        try:
            raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            manifest = raw.get("wad", raw) if isinstance(raw, dict) else raw
            if isinstance(manifest, dict):
                if "hierarchy" in manifest and isinstance(manifest["hierarchy"], str):
                    h_path = wad_path / manifest["hierarchy"]
                else:
                    h_path = wad_path / "hierarchy.yaml"
                if h_path.exists():
                    h_data = yaml.safe_load(h_path.read_text(encoding="utf-8"))
                    if not isinstance(h_data, dict) or "hierarchy" not in h_data:
                        errors.append(f"{h_path.name}: missing 'hierarchy' root key")
        except yaml.YAMLError:
            pass

    # 7. Card assignment references
    for card_file in wad_path.rglob("card_assignment*.yaml"):
        rel = card_file.relative_to(wad_path)
        try:
            data = yaml.safe_load(card_file.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"{rel}: parse error: {exc}")
            continue
        if not isinstance(data, dict) or "card" not in data:
            errors.append(f"{rel}: missing 'card' section")
            continue
        card = data["card"]
        if not isinstance(card, dict):
            errors.append(f"{rel}: 'card' is not a dict")
            continue
        for field in ("arcana", "key", "title", "keeper"):
            if field not in card:
                errors.append(f"{rel}: card missing '{field}'")

    # 8. Entity name / domain sanity
    for entity_file in wad_path.rglob("*.yaml"):
        if entity_file.name in {"manifest.yaml", "dispatch.yaml", "hierarchy.yaml"}:
            continue
        if "soul.yaml" in str(entity_file):
            continue
        try:
            data = yaml.safe_load(entity_file.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        if not isinstance(data, dict) or "entity" not in data:
            continue
        ent = data["entity"]
        if not isinstance(ent, dict):
            errors.append(f"{entity_file.relative_to(wad_path)}: 'entity' is not a dict")
            continue
        if "name" not in ent:
            errors.append(f"{entity_file.relative_to(wad_path)}: entity missing 'name'")
        if "domains" not in ent:
            errors.append(f"{entity_file.relative_to(wad_path)}: entity missing 'domains'")
        if isinstance(ent.get("domains"), list) and len(ent["domains"]) > 20:
            errors.append(
                f"{entity_file.relative_to(wad_path)}: too many domains ({len(ent['domains'])})"
            )

    # 9. Dual-tree sync drift (only when running inside the repo)
    config_wads = REPO_ROOT / "config" / "wads"
    packaged_wads = REPO_ROOT / "src" / "omega" / "config_data" / "wads"
    if config_wads.is_dir() and packaged_wads.is_dir() and wad_path.is_relative_to(config_wads):
        config_hashes = _file_hashes(config_wads)
        packaged_hashes = _file_hashes(packaged_wads)
        if config_hashes != packaged_hashes:
            errors.append(
                "Dual-tree drift: config/wads/ != src/omega/config_data/wads/. "
                "Run `python scripts/lint_wad.py <wad_dir> --fix` to sync."
            )

    return errors


def fix_dual_tree() -> None:
    """Copy config/wads/ → src/omega/config_data/wads/ to resolve drift."""
    config_wads = REPO_ROOT / "config" / "wads"
    packaged_wads = REPO_ROOT / "src" / "omega" / "config_data" / "wads"
    if not config_wads.is_dir():
        print("No config/wads/ directory found", file=sys.stderr)
        return
    if packaged_wads.exists():
        shutil.rmtree(packaged_wads)
    shutil.copytree(config_wads, packaged_wads)
    print(f"Synced {config_wads} → {packaged_wads}")


IWAD_DEFAULT = "_omega_default"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Lint an Omega Engine WAD.")
    parser.add_argument("wad_dir", help="Path to the WAD directory")
    parser.add_argument("--fix", action="store_true", help="Auto-fix dual-tree drift")
    args = parser.parse_args(argv)

    wad_path = Path(args.wad_dir).resolve()
    if args.fix:
        fix_dual_tree()

    errors = lint_wad(wad_path)
    if errors:
        print(f"FAIL: {len(errors)} lint error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"PASS: {wad_path.name} lint clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
