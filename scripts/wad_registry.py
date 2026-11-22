#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""WAD Registry — local marketplace for discovering, installing, and managing WADs (Phase 4.6).

Usage:
    python scripts/wad_registry.py list [--registry <path>]
    python scripts/wad_registry.py search <query> [--registry <path>]
    python scripts/wad_registry.py install <wad_name> [--registry <path>] [--wads-dir <path>]
    python scripts/wad_registry.py info <wad_name> [--registry <path>]
    python scripts/wad_registry.py remove <wad_name> [--wads-dir <path>]
    python scripts/wad_registry.py publish <wad_dir> [--registry <path>]

Registry format (JSON):
{
  "version": "1.0",
  "wads": [
    {
      "name": "arcana_novai",
      "version": "1.0.0",
      "description": "...",
      "author": "...",
      "type": "pwad",
      "tags": ["arcana", "tarot", "sovereign"],
      "path": "config/wads/arcana_novai",
      "dependencies": ["_omega_default"],
      "checksum": "sha256:..."
    }
  ]
}
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import yaml

DEFAULT_REGISTRY = REPO_ROOT / "config" / "wad_registry.json"
DEFAULT_WADS_DIR = REPO_ROOT / "config" / "wads"


def _sha256_dir(directory: Path) -> str:
    """Compute a composite SHA-256 of all files in a directory."""
    h = hashlib.sha256()
    for f in sorted(directory.rglob("*")):
        if f.is_file():
            h.update(f.relative_to(directory).as_posix().encode())
            h.update(f.read_bytes())
    return f"sha256:{h.hexdigest()}"


def _load_registry(registry_path: Path) -> dict:
    """Load the registry JSON file."""
    if not registry_path.exists():
        return {"version": "1.0", "wads": []}
    try:
        return json.loads(registry_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"version": "1.0", "wads": []}


def _save_registry(registry_path: Path, data: dict) -> None:
    """Save the registry JSON file."""
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _wad_info(wad_dir: Path) -> dict | None:
    """Extract WAD metadata from a WAD directory."""
    manifest_path = wad_dir / "manifest.yaml"
    if not manifest_path.exists():
        return None
    try:
        raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        manifest = raw.get("wad", raw) if isinstance(raw, dict) else {}
    except yaml.YAMLError:
        return None

    if not isinstance(manifest, dict):
        return None

    return {
        "name": manifest.get("name", wad_dir.name),
        "version": manifest.get("version", "0.0.0"),
        "description": manifest.get("description", ""),
        "author": manifest.get("author", ""),
        "type": manifest.get("type", "pwad"),
        "tags": manifest.get("tags", []),
        "dependencies": manifest.get("dependencies", []),
        "path": str(wad_dir.relative_to(REPO_ROOT)) if wad_dir.is_relative_to(REPO_ROOT) else str(wad_dir),
        "checksum": _sha256_dir(wad_dir),
    }


def cmd_list(args) -> int:
    """List all WADs in the registry."""
    registry = _load_registry(Path(args.registry))
    wads = registry.get("wads", [])
    if not wads:
        print("No WADs in registry.")
        return 0
    print(f"{'Name':<20} {'Version':<10} {'Type':<6} {'Description'}")
    print("-" * 80)
    for w in wads:
        desc = (w.get("description", "") or "")[:40]
        print(f"{w['name']:<20} {w.get('version', '?'):<10} {w.get('type', '?'):<6} {desc}")
    print(f"\nTotal: {len(wads)} WADs")
    return 0


def cmd_search(args) -> int:
    """Search WADs by name, description, or tags."""
    registry = _load_registry(Path(args.registry))
    query = args.query.lower()
    results = []
    for w in registry.get("wads", []):
        if (
            query in w.get("name", "").lower()
            or query in (w.get("description", "") or "").lower()
            or any(query in t.lower() for t in w.get("tags", []))
        ):
            results.append(w)
    if not results:
        print(f"No WADs matching '{args.query}'.")
        return 0
    print(f"Found {len(results)} WAD(s) matching '{args.query}':")
    for w in results:
        print(f"  {w['name']} v{w.get('version', '?')} — {w.get('description', '')[:60]}")
    return 0


def cmd_info(args) -> int:
    """Show detailed info about a WAD."""
    registry = _load_registry(Path(args.registry))
    for w in registry.get("wads", []):
        if w.get("name") == args.wad_name:
            print(json.dumps(w, indent=2))
            return 0
    print(f"WAD '{args.wad_name}' not found in registry.")
    return 1


def cmd_install(args) -> int:
    """Install a WAD from the registry into the WADS_DIR."""
    registry = _load_registry(Path(args.registry))
    wad_entry = None
    for w in registry.get("wads", []):
        if w.get("name") == args.wad_name:
            wad_entry = w
            break
    if not wad_entry:
        print(f"WAD '{args.wad_name}' not found in registry.")
        return 1

    wads_dir = Path(args.wads_dir)
    source_path = Path(wad_entry.get("path", ""))
    if not source_path.is_absolute():
        source_path = REPO_ROOT / source_path

    target_dir = wads_dir / args.wad_name
    if target_dir.exists():
        print(f"WAD '{args.wad_name}' already installed at {target_dir}.")
        print("Use 'wad_registry.py remove' first, or use 'wad_upgrade' for version updates.")
        return 1

    if not source_path.is_dir():
        print(f"Source WAD directory not found: {source_path}")
        return 1

    # Validate before installing
    try:
        from scripts.validate_wad import validate_wad
        errors = validate_wad(source_path)
        if errors:
            print(f"WAD validation failed: {errors}")
            return 1
    except ImportError:
        pass  # validate_wad module not importable — skip

    shutil.copytree(source_path, target_dir)
    print(f"Installed WAD '{args.wad_name}' v{wad_entry.get('version', '?')} to {target_dir}")
    return 0


def cmd_remove(args) -> int:
    """Remove an installed WAD."""
    wads_dir = Path(args.wads_dir)
    target_dir = wads_dir / args.wad_name
    if not target_dir.exists():
        print(f"WAD '{args.wad_name}' not installed.")
        return 1
    shutil.rmtree(target_dir)
    print(f"Removed WAD '{args.wad_name}' from {target_dir}")
    return 0


def cmd_publish(args) -> int:
    """Publish a WAD directory to the registry."""
    wad_dir = Path(args.wad_dir)
    if not wad_dir.is_dir():
        print(f"Not a directory: {wad_dir}")
        return 1

    info = _wad_info(wad_dir)
    if info is None:
        print(f"Cannot extract WAD info from {wad_dir} (missing or invalid manifest.yaml)")
        return 1

    registry_path = Path(args.registry)
    registry = _load_registry(registry_path)

    # Update or add
    existing_idx = None
    for i, w in enumerate(registry.get("wads", [])):
        if w.get("name") == info["name"]:
            existing_idx = i
            break

    if existing_idx is not None:
        registry["wads"][existing_idx] = info
        print(f"Updated WAD '{info['name']}' in registry.")
    else:
        registry.setdefault("wads", []).append(info)
        print(f"Published WAD '{info['name']}' to registry.")

    _save_registry(registry_path, registry)
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="WAD Registry — local marketplace.")
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY), help="Registry JSON path")
    parser.add_argument("--wads-dir", default=str(DEFAULT_WADS_DIR), help="WADs install directory")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List all WADs in registry")

    p_search = sub.add_parser("search", help="Search WADs")
    p_search.add_argument("query", help="Search query")

    p_info = sub.add_parser("info", help="Show WAD details")
    p_info.add_argument("wad_name", help="WAD name")

    p_install = sub.add_parser("install", help="Install a WAD")
    p_install.add_argument("wad_name", help="WAD name")

    p_remove = sub.add_parser("remove", help="Remove a WAD")
    p_remove.add_argument("wad_name", help="WAD name")

    p_publish = sub.add_parser("publish", help="Publish a WAD to registry")
    p_publish.add_argument("wad_dir", help="WAD directory path")

    args = parser.parse_args(argv)

    # Set defaults for registry and wads_dir on args
    if not hasattr(args, "registry"):
        args.registry = str(DEFAULT_REGISTRY)
    if not hasattr(args, "wads_dir"):
        args.wads_dir = str(DEFAULT_WADS_DIR)

    commands = {
        "list": cmd_list,
        "search": cmd_search,
        "info": cmd_info,
        "install": cmd_install,
        "remove": cmd_remove,
        "publish": cmd_publish,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
