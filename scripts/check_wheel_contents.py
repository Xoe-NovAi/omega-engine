#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""G10 — Wheel content gate.

Inspects the BUILT wheel artifact and fails closed if it contains:
- Any path under 'arcana_novai'
- Any '*.local.yaml'
- Any 'github_accounts.yaml'
- Any 'keys/' directory
- Any absolute local machine path in YAML contents
- Any file under 'config_data/' not in the explicit allowlist

The allowlist is deliberate: adding a packaged file requires editing this script.

AP: AP-G10-WHEELGATE-v1.0.0
"""

import argparse
import sys
import zipfile
from pathlib import Path


class WheelGateError(Exception):
    """Raised when wheel content gate fails (exit 1)."""
    pass


# Explicit allowlist — MUST be updated when adding new packaged files.
# Top-level runtime YAMLs (5 files):
ALLOWLIST_TOPLEVEL = frozenset({
    "omega/config_data/embedding_strategy.yaml",
    "omega/config_data/models.yaml",
    "omega/config_data/omega.yaml",
    "omega/config_data/provider_capabilities.yaml",
    "omega/config_data/providers.yaml",
})

# IWAD prefix — all files under this prefix are allowed if they exist in source
ALLOWLIST_IWAD_PREFIX = "omega/config_data/wads/_omega_default/"


def is_allowed_config_data(path: str) -> bool:
    """Check if a config_data path is in the allowlist."""
    if path in ALLOWLIST_TOPLEVEL:
        return True
    if path.startswith(ALLOWLIST_IWAD_PREFIX):
        return True
    return False


def check_absolute_paths_in_yaml(content: bytes) -> list[str]:
    """Scan YAML content for absolute local machine paths."""
    violations = []
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return violations

    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        # Unix absolute paths
        if stripped.startswith("/home/") or stripped.startswith("/Users/") or stripped.startswith("/root/"):
            violations.append(f"line {i}: absolute path '{stripped[:80]}'")
        # Windows absolute paths (drive letter)
        if len(stripped) >= 3 and stripped[1] == ":" and stripped[2] in ("\\", "/"):
            violations.append(f"line {i}: windows absolute path '{stripped[:80]}'")
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(
        description="G10 — Wheel content gate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exit codes:
  0  Wheel content is clean
  1  Forbidden content found
  2  Usage error or wheel read error
""",
    )
    parser.add_argument(
        "--wheel",
        required=True,
        help="Path to the built wheel (.whl file)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0 (AP-G10-WHEELGATE-v1.0.0)",
    )

    args = parser.parse_args()

    wheel_path = Path(args.wheel)
    if not wheel_path.is_file():
        print(f"G10 ERROR: Wheel not found at {wheel_path}", file=sys.stderr)
        return 2

    violations = []

    try:
        with zipfile.ZipFile(wheel_path, "r") as z:
            names = z.namelist()

            for name in names:
                # 1. arcana_novai anywhere in path
                if "arcana_novai" in name:
                    violations.append(f"Forbidden path segment 'arcana_novai': {name}")

                # 2. *.local.yaml
                if name.endswith(".local.yaml"):
                    violations.append(f"Forbidden *.local.yaml: {name}")

                # 3. github_accounts.yaml (anywhere)
                if name.endswith("github_accounts.yaml"):
                    violations.append(f"Forbidden github_accounts.yaml: {name}")

                # 4. keys/ directory
                if "keys/" in name or name.endswith("/keys") or name == "keys":
                    violations.append(f"Forbidden keys/ directory: {name}")

                # 5. config_data/ not in allowlist
                if name.startswith("omega/config_data/") and not is_allowed_config_data(name):
                    violations.append(f"Unexpected config_data file (not in allowlist): {name}")

                # 6. Absolute paths in YAML content
                if name.endswith(".yaml"):
                    abs_violations = check_absolute_paths_in_yaml(z.read(name))
                    for v in abs_violations:
                        violations.append(f"Absolute path in {name}: {v}")

    except zipfile.BadZipFile as e:
        print(f"G10 ERROR: Invalid wheel file: {e}", file=sys.stderr)
        return 2
    except (OSError, ValueError, RuntimeError) as e:
        print(f"G10 ERROR: {e}", file=sys.stderr)
        return 2

    if violations:
        print("G10 FAIL: Wheel content violations:", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        return 1

    print("G10 PASS: Wheel content is clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())