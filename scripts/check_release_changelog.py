#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""G8 — Fail-closed CHANGELOG section gate.

Extracts the CHANGELOG section for a given version and fails closed if:
- CHANGELOG file is missing
- No matching version heading is found
- The section body is empty/whitespace
- The output file (if requested) would be empty

This replaces the awk fallback in release.yml that permitted empty notes.

AP: AP-G8-CHGATE-v1.0.0
"""

import argparse
import re
import sys
from pathlib import Path


class ChangelogGateError(Exception):
    """Raised when the changelog gate fails (exit 1)."""
    pass


def normalize_version(version: str) -> str:
    """Normalize version for comparison: strip leading 'v' and whitespace."""
    return version.lstrip('v').strip()


def find_changelog_section(changelog_path: Path, target_version: str) -> tuple[str, int, int]:
    """
    Find the CHANGELOG section for target_version.

    Supports both bracketed headings (## [v1.6.0]) and unbracketed (## v1.6.0).
    Returns (section_text, start_line, end_line) where section_text includes
    the heading and all content until the next heading or EOF.
    """
    if not changelog_path.is_file():
        raise ChangelogGateError(f"CHANGELOG not found at {changelog_path}")

    content = changelog_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Pattern: ## [vX.Y.Z] or ## vX.Y.Z or ## X.Y.Z (with optional date suffix)
    # We match the version inside brackets or after ##, then normalize.
    # Must be exactly two hashes (## ) not three (###) to avoid subheadings.
    heading_pattern = re.compile(r'^## (?!\#)(?:\[(?P<bracketed>[^\]]+)\]|(?P<unbracketed>\S+))')

    target_norm = normalize_version(target_version)
    in_section = False
    section_lines = []
    start_line = -1
    end_line = -1

    for i, line in enumerate(lines):
        m = heading_pattern.match(line)
        if m:
            # Extract version from heading
            heading_version = m.group('bracketed') or m.group('unbracketed')
            heading_norm = normalize_version(heading_version)

            if in_section:
                # We were in a section and hit a new heading -> section ends
                end_line = i
                break

            if heading_norm == target_norm:
                # Found our section
                in_section = True
                start_line = i
                section_lines.append(line)
                continue

        if in_section:
            section_lines.append(line)

    if not in_section:
        raise ChangelogGateError(
            f"No CHANGELOG section found for version '{target_version}' "
            f"(normalized: '{target_norm}'). "
            f"Expected a heading like '## [{target_version}]' or '## {target_version}'."
        )

    # If we never hit a next heading, section goes to EOF
    if end_line == -1:
        end_line = len(lines)

    section_text = "\n".join(section_lines).rstrip() + "\n"

    # The section must have content beyond the heading line
    body = "\n".join(section_lines[1:]).strip()
    if not body:
        raise ChangelogGateError(
            f"CHANGELOG section for '{target_version}' exists but has no content "
            f"(only the heading). Release notes must not be empty."
        )

    return section_text, start_line + 1, end_line


def main() -> int:
    parser = argparse.ArgumentParser(
        description="G8 — Fail-closed CHANGELOG section extractor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exit codes:
  0  Success — section found and non-empty
  1  Gate failure — missing file, no section, or empty section
  2  Usage error
""",
    )
    parser.add_argument(
        "--tag",
        required=True,
        help="Git tag (e.g., v1.6.0-alpha). Leading 'v' is stripped for matching.",
    )
    parser.add_argument(
        "--changelog",
        default="CHANGELOG.md",
        help="Path to CHANGELOG.md (default: CHANGELOG.md)",
    )
    parser.add_argument(
        "--out",
        help="Optional output file to write the extracted section (release_notes.md)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0 (AP-G8-CHGATE-v1.0.0)",
    )

    args = parser.parse_args()

    try:
        section_text, start, end = find_changelog_section(
            Path(args.changelog), args.tag
        )

        if args.out:
            Path(args.out).write_text(section_text, encoding="utf-8")
            print(f"Wrote CHANGELOG section (lines {start}-{end}) to {args.out}")
        else:
            print(f"CHANGELOG section for {args.tag} found (lines {start}-{end}):")
            print(section_text)

        return 0

    except ChangelogGateError as e:
        print(f"G8 FAIL: {e}", file=sys.stderr)
        return 1
    except (OSError, ValueError, RuntimeError) as e:
        print(f"G8 ERROR: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())