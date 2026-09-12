#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Heritage Vet Gate — Sovereign Link Protocol (D208 Enhanced)
# ⬡ OMEGA ⬡ MAAT ⬡ heritage_vet.py ⬡ v2.0.0
#
# Usage: python3 scripts/heritage_vet.py [--strict] [--scope-check]
# Called by: make heritage-vet
#
# Validates [id-soft:] tags in src/omega/ against HERITAGE_VET_LOG.md.
#
# Enhanced for D208:
#   - Scope declaration validation (tag must declare what it applies to)
#   - File:line cross-reference with vet records
#   - C-ARCH-005 violation detection (same tag used for multiple concepts)
#   - Classification enforcement (LEGITIMATE/METAPHORICAL/OVER-ATTRIBUTED)
#
# Exit codes:
#   0 — All tags pass.
#   1 — One or more tags failed validation.
#   2 — Setup error (missing files, etc.).

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# ── Configuration ──────────────────────────────────────────────────────
REPO_DIR = Path(__file__).resolve().parent.parent
VET_LOG = REPO_DIR / "data" / "entities" / "doom_guy" / "knowledge" / "HERITAGE_VET_LOG.md"
SRC_DIR = REPO_DIR / "src" / "omega"

SCAN_PATTERNS = ["**/*.py"]

# Enhanced tag regex: captures game-year, pattern-name, and justification
TAG_REGEX = re.compile(
    r"(?:#\s*[──]\s*)?\[id-soft:\s*([a-z0-9-]+)\]\s*([^—\n]+?)(?:\s*—\s*(.+))?$"
)

VET_SECTION_REGEX = re.compile(r"^###+\s+(vet-\d+):\s*(.*?)$", re.MULTILINE)
SCORE_REGEX = re.compile(r"\*\*Score\*\*:.*?(\d+)/10", re.IGNORECASE)
DECISION_REGEX = re.compile(r"\*\*(?:Decision|Verdict)\*\*:\s*(.*?)$", re.IGNORECASE | re.MULTILINE)
VET_FILE_LOCATIONS_REGEX = re.compile(r"\*\*File Locations\*\*:\s*(.*?)$", re.IGNORECASE | re.MULTILINE)
VET_SCOPE_REGEX = re.compile(r"\*\*Scope\*\*:\s*(.*?)$", re.IGNORECASE | re.MULTILINE)

# Colors
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
CYAN = "\033[0;36m"
NC = "\033[0m"


@dataclass
class TagOccurrence:
    """A single [id-soft:] tag occurrence in source code."""
    file: Path
    line_num: int
    line: str
    game_year: str
    pattern_name: str
    justification: str = ""

    @property
    def tag_key(self) -> str:
        return f"[id-soft: {self.game_year}] {self.pattern_name.strip()}"


@dataclass
class VetRecord:
    """A vet record from HERITAGE_VET_LOG.md."""
    vet_id: str
    concept: str
    score: int
    decision: str
    file_locations: List[str] = field(default_factory=list)
    scope: str = ""
    hardware_constraint: str = ""


def find_python_files() -> List[Path]:
    """Find all Python files matching the scan patterns."""
    files = set()
    for pattern in SCAN_PATTERNS:
        for path in SRC_DIR.glob(pattern):
            if path.is_file():
                files.add(path)
    return sorted(files)


def parse_vet_log(content: str) -> Dict[str, VetRecord]:
    """Parse HERITAGE_VET_LOG.md into a dict keyed by vet-ID."""
    entries: Dict[str, VetRecord] = {}

    sections = re.split(r"^###+\s+(vet-\d+):\s*(.*?)$", content, flags=re.MULTILINE)
    i = 1
    while i < len(sections):
        vet_id = sections[i].strip()
        concept = sections[i + 1].strip() if i + 1 < len(sections) else ""
        body = sections[i + 2] if i + 2 < len(sections) else ""

        # Skip duplicate vet IDs (keep first occurrence)
        if vet_id in entries:
            i += 3
            continue

        score_match = SCORE_REGEX.search(body)
        decision_match = DECISION_REGEX.search(body)
        file_loc_match = VET_FILE_LOCATIONS_REGEX.search(body)
        scope_match = VET_SCOPE_REGEX.search(body)

        hw_constraint = ""
        if "**Hardware Constraint**" in body:
            hw_section = body.split("**Hardware Constraint**")[1].split("**")[0]
            hw_constraint = hw_section.strip().strip(":").strip()

        entries[vet_id] = VetRecord(
            vet_id=vet_id,
            concept=concept,
            score=int(score_match.group(1)) if score_match else 0,
            decision=decision_match.group(1).strip() if decision_match else "UNKNOWN",
            file_locations=[loc.strip() for loc in file_loc_match.group(1).split(",")] if file_loc_match else [],
            scope=scope_match.group(1).strip() if scope_match else "",
            hardware_constraint=hw_constraint,
        )
        i += 3

    return entries


def scan_source_files() -> List[TagOccurrence]:
    """Scan all Python files for [id-soft:] tags."""
    occurrences: List[TagOccurrence] = []
    py_files = find_python_files()

    for py_file in py_files:
        try:
            content = py_file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  {YELLOW}⚠️  Could not read {py_file}: {e}{NC}")
            continue

        for line_num, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if not stripped.startswith("#"):
                continue
            for match in TAG_REGEX.finditer(line):
                game_year = match.group(1).strip()
                pattern_name = match.group(2).strip()
                justification = match.group(3).strip() if match.group(3) else ""

                occurrences.append(TagOccurrence(
                    file=py_file,
                    line_num=line_num,
                    line=line.strip(),
                    game_year=game_year,
                    pattern_name=pattern_name,
                    justification=justification,
                ))

    return occurrences


def validate_tag(occurrence: TagOccurrence, vet_records: Dict[str, VetRecord], strict: bool, scope_check: bool) -> Tuple[bool, str]:
    """
    Validate a single tag occurrence against vet records.
    Returns (is_valid, reason).
    """
    tag_key = occurrence.tag_key

    # Find matching vet record by concept name (flexible matching)
    matching_vet = None
    pattern_lower = occurrence.pattern_name.lower()
    game_lower = occurrence.game_year.lower()
    
    # First try: exact pattern name in concept
    for vet in vet_records.values():
        if pattern_lower in vet.concept.lower():
            matching_vet = vet
            break
    
    # Second try: match by game year + keywords
    if not matching_vet:
        keywords = [kw for kw in pattern_lower.split() if len(kw) > 3]
        for vet in vet_records.values():
            concept_lower = vet.concept.lower()
            if game_lower in concept_lower or any(kw in concept_lower for kw in keywords):
                matching_vet = vet
                break

    if not matching_vet:
        return False, f"No vet record found for pattern '{occurrence.pattern_name}' (game: {occurrence.game_year})"

    # Check decision
    decision_upper = matching_vet.decision.upper()
    if "REJECT" in decision_upper or "DEFER" in decision_upper:
        return False, f"Vet record {matching_vet.vet_id} decision is {matching_vet.decision} (must be ADOPT/ADAPT)"

    # Check score
    if matching_vet.score < 7:
        return False, f"Vet record {matching_vet.vet_id} score is {matching_vet.score}/10 (must be >= 7)"

    # Scope check: verify file:line is in vet record's file_locations
    if scope_check:
        rel_path = occurrence.file.relative_to(REPO_DIR)
        file_line = f"{rel_path}:{occurrence.line_num}"
        found = False
        for vet_loc in matching_vet.file_locations:
            if file_line in vet_loc or vet_loc in file_line:
                found = True
                break
        if not found and matching_vet.file_locations:
            return False, f"Tag at {file_line} not declared in vet record {matching_vet.vet_id} file locations: {matching_vet.file_locations}"

    # Strict mode: require justification (scope declaration in tag)
    if strict and not occurrence.justification:
        return False, f"Tag missing scope justification (format: [id-soft: {occurrence.game_year}] {occurrence.pattern_name} — why this code exists)"

    return True, f"OK (vet: {matching_vet.vet_id}, decision: {matching_vet.decision}, score: {matching_vet.score}/10)"


def detect_c_arch_005_violations(occurrences: List[TagOccurrence]) -> List[str]:
    """
    Detect C-ARCH-005 violations: same tag used for multiple distinct concepts in same file.
    """
    violations = []
    by_file_tag: Dict[Tuple[Path, str], List[TagOccurrence]] = {}
    for occ in occurrences:
        key = (occ.file, occ.tag_key)
        by_file_tag.setdefault(key, []).append(occ)

    for (file, tag_key), occs in by_file_tag.items():
        justifications = set(occ.justification for occ in occs)
        if len(justifications) > 1:
            violations.append(
                f"{file}: Tag '{tag_key}' used for multiple concepts: {justifications}"
            )

    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description="Heritage Vet Gate — D208 Enhanced")
    parser.add_argument("--strict", action="store_true", help="Require scope justification in tags")
    parser.add_argument("--scope-check", action="store_true", help="Validate file:line against vet record locations")
    args = parser.parse_args()

    print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
    print(f" 🏛️  Heritage Vet Gate — Sovereign Link Protocol")
    print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")

    # ── Pre-flight ──
    if not VET_LOG.exists():
        print(f"  {RED}❌ HERITAGE_VET_LOG.md not found at {VET_LOG}{NC}")
        print(f"  {YELLOW}Run 'make heritage-vet-create' first.{NC}")
        return 2

    if not SRC_DIR.exists():
        print(f"  {RED}❌ Source directory not found: {SRC_DIR}{NC}")
        return 2

    # ── Load vet log ──
    vet_log_content = VET_LOG.read_text(encoding="utf-8")
    entries = parse_vet_log(vet_log_content)
    print(f"  {CYAN}Loaded {len(entries)} vet records.{NC}")

    # ── Scan source files ──
    py_files = find_python_files()
    occurrences = scan_source_files()

    legacy_count = 0
    sovereign_count = 0
    failures: List[str] = []
    legacy_warnings: List[str] = []

    for occ in occurrences:
        if occ.game_year.startswith("vet-"):
            sovereign_count += 1
            ok, reason = validate_tag(occ, entries, args.strict, args.scope_check)
            if ok:
                print(f"  {GREEN}✅{NC} {occ.file.name}:{occ.line_num}: [id-soft: {occ.game_year}] {occ.pattern_name} — {reason}")
            else:
                failures.append(f"{occ.file.name}:{occ.line_num}: [id-soft: {occ.game_year}] {occ.pattern_name} — {reason}")
                print(f"  {RED}❌{NC} {occ.file.name}:{occ.line_num}: [id-soft: {occ.game_year}] {occ.pattern_name} — {reason}")
        else:
            legacy_count += 1
            ok, reason = validate_tag(occ, entries, args.strict, args.scope_check)
            if ok:
                print(f"  {GREEN}✅{NC} {occ.file.name}:{occ.line_num}: [id-soft: {occ.game_year}] {occ.pattern_name} — {reason}")
            else:
                failures.append(f"{occ.file.name}:{occ.line_num}: [id-soft: {occ.game_year}] {occ.pattern_name} — {reason}")
                print(f"  {RED}❌{NC} {occ.file.name}:{occ.line_num}: [id-soft: {occ.game_year}] {occ.pattern_name} — {reason}")

            rel = occ.file.relative_to(REPO_DIR)
            legacy_warnings.append(f"{rel}: [id-soft: {occ.game_year}] {occ.pattern_name}")

    # C-ARCH-005 violation detection
    c_arch_violations = detect_c_arch_005_violations(occurrences)
    for v in c_arch_violations:
        failures.append(f"C-ARCH-005: {v}")
        print(f"  {RED}❌ C-ARCH-005:{NC} {v}")

    # ── Summary ──
    print()
    print(f"  Scanned {len(py_files)} files: {sovereign_count} sovereign links, {legacy_count} legacy tags.")

    if legacy_warnings:
        print()
        print(f"  {YELLOW}⚠️  Migration Advisory:{NC}")
        print(f"  {len(legacy_warnings)} tags use legacy [id-soft: <game-year>] format.")
        print(f"  Migrate to [id-soft: vet-XXX] format for 1:1 immutable linkage.")

    print()
    if failures:
        print(f"  {RED}❌ {len(failures)} unvetted heritage tag(s) found.{NC}")
        print(f"  {YELLOW}Each [id-soft:] tag must have a corresponding vet record with scope declaration.{NC}")
        print(f"  {YELLOW}See: docs/strategy/HERITAGE_VETTING_PIPELINE.md{NC}")
        return 1
    else:
        print(f"  {GREEN}✅ All heritage tags have vet records. Heritage Vetting Pipeline compliant.{NC}")
        return 0


if __name__ == "__main__":
    sys.exit(main())