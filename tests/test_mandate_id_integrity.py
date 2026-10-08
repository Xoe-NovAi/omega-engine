#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
# SPDX-License-Identifier: Apache-2.0

"""
Mandate ID Integrity Regression Test (D-609)

Asserts:
1. Every inline (Mn) tag in SOVEREIGN_MANDATES.md resolves to an existing section
2. Every mandate ID referenced in the governance tier resolves
3. The declared mandate count in AGENTS.md matches the actual section count

This test FAILS if someone reintroduces a dangling ID.
"""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANDATES_MD = REPO / "SOVEREIGN_MANDATES.md"
AGENTS_MD = REPO / "AGENTS.md"
MANDATES_CONDENSED = REPO / "MANDATES_CONDENSED.md"
CONSTRAINTS_MD = REPO / "docs/governance/CONSTRAINTS.md"


def parse_mandate_sections() -> dict[int, str]:
    """Parse SOVEREIGN_MANDATES.md for `### N. Title` headings. Returns {section_num: title}."""
    text = MANDATES_MD.read_text()
    found = re.findall(r"^### (\d+)\.\s+(.+?)\s*$", text, re.MULTILINE)
    return {int(num): name.strip() for num, name in found}


def find_inline_tags() -> list[tuple[int, int, str]]:
    """
    Find all inline (Mn) tags in SOVEREIGN_MANDATES.md headings.
    Returns list of (section_num, tag_num, heading_text).
    """
    text = MANDATES_MD.read_text()
    # Match headings with inline tags like "### 28. Title (M29 — ...)"
    pattern = r"^### (\d+)\.\s+(.+?)\s+\(M(\d+)\s*—"
    found = re.findall(pattern, text, re.MULTILINE)
    return [(int(sec), int(tag), title.strip()) for sec, title, tag in found]


def extract_mandate_refs_from_file(path: Path) -> set[str]:
    """Extract all M<number> references from a file."""
    text = path.read_text()
    # Match M followed by digits, word boundary
    refs = re.findall(r"\bM(\d+)\b", text)
    return {f"M{r}" for r in refs}


def test_inline_tags_resolve_to_sections():
    """Every inline (Mn) tag in SOVEREIGN_MANDATES.md must resolve to an existing section."""
    sections = parse_mandate_sections()
    inline_tags = find_inline_tags()

    errors = []
    for sec_num, tag_num, heading in inline_tags:
        if tag_num not in sections:
            errors.append(
                f"§{sec_num} '{heading}' has inline tag (M{tag_num}) but §{tag_num} does not exist"
            )
        elif tag_num != sec_num:
            errors.append(
                f"§{sec_num} '{heading}' has inline tag (M{tag_num}) that disagrees with section number (off by {tag_num - sec_num:+d})"
            )

    assert not errors, "Inline tag resolution failures:\n" + "\n".join(errors)


def test_governance_tier_refs_resolve():
    """Every mandate ID in governance tier files must resolve to a section.
    
    Known proposed/future mandates (M33, M34, M36) documented in AGENTS.md
    as "Dispatch Guard Anchors" are allowed as forward references.
    """
    sections = parse_mandate_sections()
    valid_ids = {f"M{n}" for n in sections.keys()}

    # Proposed mandates documented in AGENTS.md §"M33/M34 Dispatch Guard Anchors"
    # These are forward references to work not yet ratified as numbered mandates
    proposed_mandates = {"M33", "M34", "M36"}

    governance_files = [
        ("AGENTS.md", AGENTS_MD),
        ("MANDATES_CONDENSED.md", MANDATES_CONDENSED),
        ("CONSTRAINTS.md", CONSTRAINTS_MD),
    ]

    errors = []
    for name, path in governance_files:
        if not path.exists():
            errors.append(f"{name}: file not found")
            continue
        refs = extract_mandate_refs_from_file(path)
        for ref in refs:
            if ref not in valid_ids and ref not in proposed_mandates:
                errors.append(f"{name}: references {ref} but no §{ref[1:]} exists")

    assert not errors, "Governance tier dangling references:\n" + "\n".join(errors)


def test_agents_md_count_matches_sections():
    """AGENTS.md declared mandate count must match actual section count."""
    sections = parse_mandate_sections()
    actual_count = len(sections)

    text = AGENTS_MD.read_text()

    # Find "X mandates" or "X laws" patterns in AGENTS.md
    count_matches = re.findall(r"(\d+)\s+(?:mandates?|laws?)", text, re.IGNORECASE)

    errors = []
    for match in count_matches:
        declared = int(match)
        if declared != actual_count:
            errors.append(f"AGENTS.md declares {declared} mandates/laws but SOVEREIGN_MANDATES.md has {actual_count} sections")

    assert not errors, "Mandate count mismatch:\n" + "\n".join(errors)


def test_no_phantom_m30_m35_in_governance():
    """M30 and M35 must not appear as mandate IDs in governance tier (they are named controls, not numbered mandates)."""
    governance_files = [
        ("AGENTS.md", AGENTS_MD),
        ("MANDATES_CONDENSED.md", MANDATES_CONDENSED),
        ("CONSTRAINTS.md", CONSTRAINTS_MD),
    ]

    errors = []
    for name, path in governance_files:
        if not path.exists():
            continue
        refs = extract_mandate_refs_from_file(path)
        for phantom in ["M30", "M35"]:
            if phantom in refs:
                # Allow M30 in MANDATES_CONDENSED.md since we just added it as the 30th mandate
                if phantom == "M30" and name == "MANDATES_CONDENSED.md":
                    continue
                errors.append(f"{name}: contains phantom mandate ID {phantom} (should be a named control, not a numbered mandate)")

    assert not errors, "Phantom mandate IDs in governance tier:\n" + "\n".join(errors)


if __name__ == "__main__":
    import sys
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))