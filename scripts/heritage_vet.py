#!/usr/bin/env python3
# 🔱 Heritage Vet Gate — Sovereign Link Protocol
# ⬡ OMEGA ⬡ KALI ⬡ heritage_vet.py ⬡ v1.0.0
#
# Usage: python3 scripts/heritage_vet.py
# Called by: make heritage-vet
#
# Validates [id-soft:] tags in src/omega/ against HERITAGE_VET_LOG.md.
#
# Two tag formats are supported:
#   1. Legacy: [id-soft: doom-1993]  — matches if the pattern appears
#      anywhere in the vet log.
#   2. Sovereign Link: [id-soft: vet-002] — strict check:
#      - The vet-002 section must exist.
#      - The decision must be ADOPT or ADAPT.
#      - The total_score must be >= 7.
#
# Exit codes:
#   0 — All tags pass.
#   1 — One or more tags failed validation.
#   2 — Setup error (missing files, etc.).

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ── Configuration ──────────────────────────────────────────────────────
REPO_DIR = Path(__file__).resolve().parent.parent
VET_LOG = REPO_DIR / "data" / "entities" / "doom_guy" / "knowledge" / "HERITAGE_VET_LOG.md"
SRC_DIR = REPO_DIR / "src" / "omega"

# Files to scan (mirrors the bash version's find expression)
SCAN_PATTERNS = [
    "*/oracle/*.py",
    "*/omega/constants.py",
    "*/omega/cvar_table.py",
    "*/omega/observability.py",
]

TAG_REGEX = re.compile(r"\[id-soft:\s*([^\]]+)\]")
VET_SECTION_REGEX = re.compile(r"^##\s+(vet-\d+):", re.MULTILINE)
SCORE_REGEX = re.compile(r"\*\*Score\*\*:.*?=\s*(\d+)/10", re.IGNORECASE)
DECISION_REGEX = re.compile(r"\*\*Decision\*\*:\s*(.*?)$", re.IGNORECASE | re.MULTILINE)

# Colors
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
CYAN = "\033[0;36m"
NC = "\033[0m"


def find_python_files() -> List[Path]:
    """Find all Python files matching the scan patterns."""
    files = set()
    for pattern in SCAN_PATTERNS:
        # Patterns are relative to SRC_DIR (src/omega).
        # E.g., "*/oracle/*.py" matches "oracle/*.py" inside src/omega.
        relative_pattern = pattern.lstrip("*/")
        for path in (SRC_DIR / "").glob(relative_pattern):
            if path.is_file():
                files.add(path)
    return sorted(files)


def parse_vet_log(content: str) -> Dict[str, Dict]:
    """Parse HERITAGE_VET_LOG.md into a dict keyed by vet-ID.

    Each entry contains:
      - concept: str
      - decision: str (raw, including emoji/markdown)
      - score: int (0-10)
    """
    entries: Dict[str, Dict] = {}

    # Split on section headers
    sections = re.split(r"^##\s+(vet-\d+):\s*(.*?)$", content, flags=re.MULTILINE)
    # sections[0] is preamble, then groups of (vet_id, concept, body)
    i = 1
    while i < len(sections):
        vet_id = sections[i].strip()
        concept = sections[i + 1].strip() if i + 1 < len(sections) else ""
        body = sections[i + 2] if i + 2 < len(sections) else ""

        score_match = SCORE_REGEX.search(body)
        decision_match = DECISION_REGEX.search(body)

        entries[vet_id] = {
            "concept": concept,
            "score": int(score_match.group(1)) if score_match else 0,
            "decision": decision_match.group(1).strip() if decision_match else "UNKNOWN",
        }
        i += 3

    return entries


def validate_legacy_tag(pattern: str, vet_log_content: str) -> Tuple[bool, str]:
    """Validate a legacy tag (e.g., doom-1993).

    Pass if the pattern appears anywhere in the vet log.
    """
    if pattern.lower() in vet_log_content.lower():
        return True, "legacy pattern found in log"
    return False, "pattern not found in log"


def validate_sovereign_link(vet_id: str, entries: Dict[str, Dict]) -> Tuple[bool, str]:
    """Strict validation for a vet-ID tag (e.g., vet-002).

    Checks:
      1. The vet-ID section exists in the log.
      2. The decision is ADOPT or ADAPT.
      3. The score is >= 7/10.
    """
    if vet_id not in entries:
        return False, f"vet record '{vet_id}' not found in HERITAGE_VET_LOG.md"

    entry = entries[vet_id]
    decision_upper = entry["decision"].upper()

    if "REJECT" in decision_upper or "DEFER" in decision_upper:
        return False, f"decision is {entry['decision']} (must be ADOPT/ADAPT)"

    if entry["score"] < 7:
        return False, f"score is {entry['score']}/10 (must be >= 7)"

    return True, f"sovereign link OK ({entry['decision']}, {entry['score']}/10)"


def main() -> int:
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
    legacy_count = 0
    sovereign_count = 0
    failures: List[str] = []
    legacy_warnings: List[str] = []

    for py_file in py_files:
        try:
            content = py_file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  {YELLOW}⚠️  Could not read {py_file}: {e}{NC}")
            continue

        for match in TAG_REGEX.finditer(content):
            pattern = match.group(1).strip()

            if pattern.startswith("vet-"):
                # Sovereign Link format
                sovereign_count += 1
                ok, reason = validate_sovereign_link(pattern, entries)
                if ok:
                    print(f"  {GREEN}✅{NC} {py_file.name}: [id-soft: {pattern}] — {reason}")
                else:
                    failures.append(f"{py_file.name}: [id-soft: {pattern}] — {reason}")
                    print(f"  {RED}❌{NC} {py_file.name}: [id-soft: {pattern}] — {reason}")
            else:
                # Legacy format
                legacy_count += 1
                ok, reason = validate_legacy_tag(pattern, vet_log_content)
                if ok:
                    pass  # Silent OK for legacy to reduce noise
                else:
                    failures.append(
                        f"{py_file.name}: [id-soft: {pattern}] — {reason}"
                    )
                    print(f"  {RED}❌{NC} {py_file.name}: [id-soft: {pattern}] — {reason}")

                # Warn about legacy format usage
                rel = py_file.relative_to(REPO_DIR)
                legacy_warnings.append(
                    f"{rel}: [id-soft: {pattern}]"
                )

    # ── Summary ──
    print()
    print(f"  Scanned {len(py_files)} files: "
          f"{sovereign_count} sovereign links, {legacy_count} legacy tags.")

    if legacy_warnings:
        print()
        print(f"  {YELLOW}⚠️  Migration Advisory:{NC}")
        print(f"  {len(legacy_warnings)} tags use the legacy [id-soft: <game-year>] format.")
        print(f"  Sovereign Mandate 14 recommends migrating to [id-soft: vet-XXX] format")
        print(f"  for 1:1 immutable linkage. Legacy format is still accepted but discouraged.")

    print()
    if failures:
        print(f"  {RED}❌ {len(failures)} unvetted heritage tag(s) found.{NC}")
        print(f"  {YELLOW}Each [id-soft:] tag must have a corresponding vet record.{NC}")
        print(f"  {YELLOW}See: docs/strategy/HERITAGE_VETTING_PIPELINE.md{NC}")
        return 1
    else:
        print(f"  {GREEN}✅ All heritage tags have vet records. "
              f"Heritage Vetting Pipeline compliant.{NC}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
