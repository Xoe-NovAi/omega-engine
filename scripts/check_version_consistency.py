#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""G9 — Version consistency gate (tag == pyproject == CHANGELOG).

Verifies that the git tag version, pyproject.toml version, and the CHANGELOG
heading for that version all agree after normalizing the leading 'v'.

Fails closed on any mismatch.

AP: AP-G9-VERGATE-v1.0.0
"""

import argparse
import re
import sys
import tomllib
from pathlib import Path


class VersionGateError(Exception):
    """Raised when version consistency check fails (exit 1)."""
    pass


def normalize_version(version: str) -> str:
    """Normalize version for comparison: strip leading 'v' and whitespace."""
    return version.lstrip('v').strip()


def get_pyproject_version(pyproject_path: Path) -> str:
    """Extract version from pyproject.toml."""
    if not pyproject_path.is_file():
        raise VersionGateError(f"pyproject.toml not found at {pyproject_path}")
    try:
        data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as e:
        raise VersionGateError(f"Failed to parse pyproject.toml: {e}")
    version = data.get("project", {}).get("version")
    if not version:
        raise VersionGateError("No 'project.version' key in pyproject.toml")
    return str(version).strip()


def get_changelog_heading_version(changelog_path: Path, target_version: str) -> str:
    """
    Find the CHANGELOG heading for target_version and return the version
    as it appears in the heading (with or without leading 'v').
    """
    if not changelog_path.is_file():
        raise VersionGateError(f"CHANGELOG not found at {changelog_path}")

    content = changelog_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Match exactly two hashes: ## [vX.Y.Z] or ## vX.Y.Z
    heading_pattern = re.compile(r'^## (?!\#)(?:\[(?P<bracketed>[^\]]+)\]|(?P<unbracketed>\S+))')

    target_norm = normalize_version(target_version)

    for line in lines:
        m = heading_pattern.match(line)
        if m:
            heading_version = m.group('bracketed') or m.group('unbracketed')
            heading_norm = normalize_version(heading_version)
            if heading_norm == target_norm:
                return heading_version.strip()

    raise VersionGateError(
        f"No CHANGELOG heading found matching version '{target_version}' "
        f"(normalized: '{target_norm}')."
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="G9 — Version consistency gate (tag == pyproject == CHANGELOG)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exit codes:
  0  All three versions agree
  1  Version mismatch or missing data
  2  Usage error
""",
    )
    parser.add_argument(
        "--tag",
        required=True,
        help="Git tag (e.g., v1.6.0-alpha). Leading 'v' is stripped for comparison.",
    )
    parser.add_argument(
        "--pyproject",
        default="pyproject.toml",
        help="Path to pyproject.toml (default: pyproject.toml)",
    )
    parser.add_argument(
        "--changelog",
        default="CHANGELOG.md",
        help="Path to CHANGELOG.md (default: CHANGELOG.md)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0 (AP-G9-VERGATE-v1.0.0)",
    )

    args = parser.parse_args()

    try:
        tag_version = args.tag
        tag_norm = normalize_version(tag_version)

        pyproject_version = get_pyproject_version(Path(args.pyproject))
        pyproject_norm = normalize_version(pyproject_version)

        changelog_version = get_changelog_heading_version(
            Path(args.changelog), tag_version
        )
        changelog_norm = normalize_version(changelog_version)

        # Compare all three
        mismatches = []
        if tag_norm != pyproject_norm:
            mismatches.append(f"tag ({tag_norm}) != pyproject ({pyproject_norm})")
        if tag_norm != changelog_norm:
            mismatches.append(f"tag ({tag_norm}) != CHANGELOG ({changelog_norm})")
        if pyproject_norm != changelog_norm:
            mismatches.append(f"pyproject ({pyproject_norm}) != CHANGELOG ({changelog_norm})")

        if mismatches:
            raise VersionGateError("Version mismatch: " + "; ".join(mismatches))

        print(f"G9 PASS: All versions agree on '{tag_norm}'")
        print(f"  tag:        {tag_version}")
        print(f"  pyproject:  {pyproject_version}")
        print(f"  CHANGELOG:  {changelog_version}")
        return 0

    except VersionGateError as e:
        print(f"G9 FAIL: {e}", file=sys.stderr)
        return 1
    except (OSError, ValueError, RuntimeError, tomllib.TOMLDecodeError) as e:
        print(f"G9 ERROR: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())