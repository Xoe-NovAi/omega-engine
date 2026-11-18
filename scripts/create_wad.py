#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""WAD Scaffold CLI — create a compliant IWAD or PWAD skeleton (Phase 3.4).

Usage:
    python scripts/create_wad.py <name> [--type iwad|pwad] [--wads-dir <path>]

Creates:
    <wads_dir>/<name>/
      manifest.yaml
      entities/<sample_entity>.yaml
      entities/<sample_entity>/soul.yaml
      voices/<sample_voice>.yaml
      hierarchy.yaml
      dispatch.yaml
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from omega.governance.config_resolver import WADS_DIR  # noqa: E402

SAMPLE_ENTITY = "example"
SAMPLE_VOICE = "example_voice"
SAMPLE_WAD_NAME = "example_wad"
IWAD_DEFAULT = "_omega_default"


def _safe_name(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("'", "")


def scaffold(wad_name: str, wad_type: str, wads_dir: Path) -> Path:
    wad_name = _safe_name(wad_name)
    if not wad_name:
        raise SystemExit("wad name must be non-empty")
    if wad_type not in {"iwad", "pwad"}:
        raise SystemExit(f"invalid wad type: {wad_type}")

    target = wads_dir / wad_name
    if target.exists():
        raise SystemExit(f"WAD already exists: {target}")

    entities_dir = target / "entities" / SAMPLE_ENTITY
    voices_dir = target / "voices"
    entities_dir.mkdir(parents=True, exist_ok=True)
    voices_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "wad": {
            "name": wad_name,
            "version": "0.1.0",
            "author": "Your Name",
            "description": f"{wad_name} — custom Omega Engine WAD",
            "license": "Apache-2.0",
            "type": wad_type,
            "mode": "personal" if wad_type == "pwad" else "production",
            "priority": 1 if wad_type == "pwad" else 0,
            "requires_engine": ">=1.6.0",
            "startup": {"message": f"{wad_name} loaded."},
            "voices": {"primary": f"{SAMPLE_VOICE}.yaml", "secondary": []},
            "vr_scenes": [],
            "entities": [],
            "dependencies": [] if wad_type == "iwad" else [IWAD_DEFAULT],
        }
    }
    if wad_type == "pwad":
        manifest["wad"]["hierarchy"] = "hierarchy.yaml"

    import yaml

    (target / "manifest.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )

    (entities_dir / f"{SAMPLE_ENTITY}.yaml").write_text(
        "entity:\n"
        f"  name: {SAMPLE_ENTITY.title()}\n"
        "  domains:\n"
        "    - general\n"
        '  personality: "A sample entity for this WAD."\n'
        "  temperature: 0.7\n"
        "  context_window: 8192\n"
        "  slots: []\n"
        "  role: Sample Entity\n"
        "  container: false\n",
        encoding="utf-8",
    )

    (entities_dir / "soul.yaml").write_text(
        "identity:\n"
        f"  keeper: \"{SAMPLE_ENTITY}\"\n"
        '  epithet: "Sample Sovereign"\n'
        '  seat: "Sample Seat"\n'
        '  version: "0.1.0-draft"\n'
        '  status: "draft"\n'
        "\n"
        "axioms:\n"
        "  - id: \"EX-001\"\n"
        '    text: "This is a sample axiom. Replace with real axioms."\n'
        "\n"
        "directives:\n"
        "  - id: \"D-EX-001\"\n"
        '    rule: "This is a sample directive. Replace with real directives."\n'
        "\n"
        "principles: []\n"
        "\n"
        "voice:\n"
        "  dna_ref: \"voice_dna.md\"\n"
        '  default_preset: "default"\n'
        "  base_weights:\n"
        "    fierce: 0.5\n"
        "    tender: 0.5\n",
        encoding="utf-8",
    )

    (voices_dir / f"{SAMPLE_VOICE}.yaml").write_text(
        "voice:\n"
        f"  name: {SAMPLE_VOICE.replace('_', ' ').title()}\n"
        '  activation: "hey example"\n'
        '  personality: "A sample voice interface for this WAD."\n'
        "  temperature: 0.7\n"
        "  top_p: 0.9\n"
        '  model_recommendation: "opencode/big-pickle"\n'
        "  tags: [sample, wad]\n",
        encoding="utf-8",
    )

    (target / "hierarchy.yaml").write_text(
        "hierarchy:\n"
        f"  {SAMPLE_ENTITY}_root:\n"
        f"    name: {SAMPLE_ENTITY.title()}\n"
        '    title: "Sample Root"\n'
        '    role: "Top-level node for this WAD"\n'
        "    governs: []\n",
        encoding="utf-8",
    )

    (target / "dispatch.yaml").write_text(
        "entities:\n"
        "  - name: \"example\"\n"
        '    role: "SAMPLE_ENTITY"\n'
        '    mode: "primary"\n'
        '    purpose: "Sample entity dispatch entry"\n'
        "    capabilities: [\"sample\"]\n"
        "    domains: [\"general\"]\n"
        "    slot: null\n"
        '    task_tool_type: "general"\n'
        "    owned_files: []\n",
        encoding="utf-8",
    )

    return target


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Scaffold a compliant Omega Engine WAD.")
    parser.add_argument("name", help="WAD name (directory name)")
    parser.add_argument("--type", choices=["iwad", "pwad"], default="pwad", help="WAD type")
    parser.add_argument("--wads-dir", type=Path, default=None, help="Override WADS_DIR")
    args = parser.parse_args(argv)

    base = Path(args.wads_dir) if args.wads_dir is not None else WADS_DIR
    try:
        target = scaffold(args.name, args.type, base)
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Created WAD: {target}")
    print("Next: run `python scripts/validate_wad.py <path>` and `python scripts/lint_wad.py <path>`")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
