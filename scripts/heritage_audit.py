#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Heritage Audit — Classification & Remediation (D208)
# ⬡ OMEGA ⬡ MAAT ⬡ heritage_audit.py ⬡ v1.0.0
#
# Usage: python3 scripts/heritage_audit.py [--classify-all] [--output-report] [--output-credits]
# Called by: make heritage-audit
#
# Classifies all [id-soft:] tags as LEGITIMATE / METAPHORICAL / OVER-ATTRIBUTED
# Generates remediation report and corrected CREDITS.md registry.

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
CREDITS_FILE = REPO_DIR / "CREDITS.md"
REPORT_FILE = REPO_DIR / "data" / "coordination" / "HERITAGE_AUDIT_REPORT.md"
CORRECTED_CREDITS_FILE = REPO_DIR / "data" / "coordination" / "CREDITS_CORRECTED.md"

SCAN_PATTERNS = ["**/*.py"]

TAG_REGEX = re.compile(
    r"\[id-soft:\s*([a-z0-9-]+)\]\s*([^—\n]+?)(?:\s*—\s*(.+))?$"
)

VET_SECTION_REGEX = re.compile(r"^###+\s+(vet-\d+):\s*(.*?)$", re.MULTILINE)
SCORE_REGEX = re.compile(r"\*\*Score\*\*:.*?=\s*(\d+)/10", re.IGNORECASE)
DECISION_REGEX = re.compile(r"\*\*(?:Decision|Verdict)\*\*:\s*(.*?)$", re.IGNORECASE | re.MULTILINE)
VET_FILE_LOCATIONS_REGEX = re.compile(r"\*\*File Locations\*\*:\s*(.*?)$", re.IGNORECASE | re.MULTILINE)
VET_SCOPE_REGEX = re.compile(r"\*\*Scope\*\*:\s*(.*?)$", re.IGNORECASE | re.MULTILINE)

# Colors
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
CYAN = "\033[0;36m"
PURPLE = "\033[0;35m"
NC = "\033[0m"


@dataclass
class TagOccurrence:
    file: Path
    line_num: int
    line: str
    game_year: str
    pattern_name: str
    justification: str = ""

    @property
    def tag_key(self) -> str:
        return f"[id-soft: {self.game_year}] {self.pattern_name.strip()}"

    @property
    def full_tag(self) -> str:
        parts = [f"[id-soft: {self.game_year}] {self.pattern_name.strip()}"]
        if self.justification:
            parts.append(f"— {self.justification}")
        return " ".join(parts)


@dataclass
class VetRecord:
    vet_id: str
    concept: str
    score: int
    decision: str
    file_locations: List[str] = field(default_factory=list)
    scope: str = ""
    hardware_constraint: str = ""


@dataclass
class ClassificationResult:
    tag_key: str
    classification: str  # LEGITIMATE, METAPHORICAL, OVER-ATTRIBUTED
    reason: str
    occurrences: List[TagOccurrence] = field(default_factory=list)
    vet_record: Optional[VetRecord] = None
    remediation: str = ""


def find_python_files() -> List[Path]:
    files = set()
    for pattern in SCAN_PATTERNS:
        for path in SRC_DIR.glob(pattern):
            if path.is_file():
                files.add(path)
    return sorted(files)


def parse_vet_log(content: str) -> Dict[str, VetRecord]:
    entries: Dict[str, VetRecord] = {}
    sections = re.split(r"^###+\s+(vet-\d+):\s*(.*?)$", content, flags=re.MULTILINE)
    i = 1
    while i < len(sections):
        vet_id = sections[i].strip()
        concept = sections[i + 1].strip() if i + 1 < len(sections) else ""
        body = sections[i + 2] if i + 2 < len(sections) else ""

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
    occurrences: List[TagOccurrence] = []
    for py_file in find_python_files():
        try:
            content = py_file.read_text(encoding="utf-8")
        except Exception:
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


def find_matching_vet(occurrence: TagOccurrence, vet_records: Dict[str, VetRecord]) -> Optional[VetRecord]:
    for vet in vet_records.values():
        if occurrence.pattern_name.lower() in vet.concept.lower():
            return vet
    return None


def classify_tag(occurrence: TagOccurrence, vet_records: Dict[str, VetRecord]) -> ClassificationResult:
    tag_key = occurrence.tag_key
    vet = find_matching_vet(occurrence, vet_records)

    if not vet:
        return ClassificationResult(
            tag_key=tag_key,
            classification="OVER-ATTRIBUTED",
            reason="No vet record found for this pattern",
            occurrences=[occurrence],
            remediation="Either create a vet record with score >= 7, or remove the tag",
        )

    decision_upper = vet.decision.upper()
    if "REJECT" in decision_upper or "DEFER" in decision_upper:
        return ClassificationResult(
            tag_key=tag_key,
            classification="OVER-ATTRIBUTED",
            reason=f"Vet record {vet.vet_id} decision: {vet.decision}",
            occurrences=[occurrence],
            vet_record=vet,
            remediation="Remove tag — concept was rejected/deferred in vetting",
        )

    if vet.score < 7:
        return ClassificationResult(
            tag_key=tag_key,
            classification="OVER-ATTRIBUTED",
            reason=f"Vet record {vet.vet_id} score: {vet.score}/10 (minimum 7)",
            occurrences=[occurrence],
            vet_record=vet,
            remediation="Remove tag or re-vet with stronger justification",
        )

    metaphorical_keywords = ["like", "similar to", "analogous", "metaphor", "inspired by", "reminiscent of", "evokes"]
    if occurrence.justification and any(kw in occurrence.justification.lower() for kw in metaphorical_keywords):
        return ClassificationResult(
            tag_key=tag_key,
            classification="METAPHORICAL",
            reason=f"Justification uses metaphorical language: '{occurrence.justification}'",
            occurrences=[occurrence],
            vet_record=vet,
            remediation="Convert to plain comment: remove [id-soft:] tag, keep explanation as regular comment",
        )

    if not vet.hardware_constraint:
        return ClassificationResult(
            tag_key=tag_key,
            classification="LEGITIMATE (needs hardware constraint in vet record)",
            reason=f"Vet approved but missing hardware constraint documentation",
            occurrences=[occurrence],
            vet_record=vet,
            remediation="Add **Hardware Constraint** section to vet record explaining original hardware necessity",
        )

    return ClassificationResult(
        tag_key=tag_key,
        classification="LEGITIMATE",
        reason=f"Vet {vet.vet_id}: {vet.decision}, {vet.score}/10, hardware constraint documented",
        occurrences=[occurrence],
        vet_record=vet,
        remediation="No action needed",
    )


def merge_classifications(results: List[ClassificationResult]) -> Dict[str, ClassificationResult]:
    merged: Dict[str, ClassificationResult] = {}
    for result in results:
        if result.tag_key not in merged:
            merged[result.tag_key] = result
        else:
            merged[result.tag_key].occurrences.extend(result.occurrences)
            severity = {"OVER-ATTRIBUTED": 3, "METAPHORICAL": 2, "LEGITIMATE": 1}
            current_sev = severity.get(merged[result.tag_key].classification.split()[0], 0)
            new_sev = severity.get(result.classification.split()[0], 0)
            if new_sev > current_sev:
                merged[result.tag_key] = result
    return merged


def generate_remediation_report(classifications: Dict[str, ClassificationResult]) -> str:
    from datetime import datetime
    lines = [
        "# 🔱 Heritage Audit Remediation Report",
        f"**Generated**: {datetime.now().isoformat()}",
        f"**Total Tags Analyzed**: {len(classifications)}",
        "",
        "## Summary",
        "",
    ]

    counts = {"LEGITIMATE": 0, "METAPHORICAL": 0, "OVER-ATTRIBUTED": 0}
    for c in classifications.values():
        key = c.classification.split()[0]
        counts[key] = counts.get(key, 0) + 1

    lines.append(f"- **LEGITIMATE**: {counts.get('LEGITIMATE', 0)}")
    lines.append(f"- **METAPHORICAL**: {counts.get('METAPHORICAL', 0)}")
    lines.append(f"- **OVER-ATTRIBUTED**: {counts.get('OVER-ATTRIBUTED', 0)}")
    lines.append("")

    for cat in ["OVER-ATTRIBUTED", "METAPHORICAL", "LEGITIMATE"]:
        cat_results = [c for c in classifications.values() if c.classification.startswith(cat)]
        if not cat_results:
            continue
        lines.append(f"## {cat} ({len(cat_results)})")
        lines.append("")
        for result in sorted(cat_results, key=lambda x: x.tag_key):
            lines.append(f"### {result.tag_key}")
            lines.append(f"- **Classification**: {result.classification}")
            lines.append(f"- **Reason**: {result.reason}")
            lines.append(f"- **Remediation**: {result.remediation}")
            lines.append(f"- **Occurrences**:")
            for occ in result.occurrences:
                rel = occ.file.relative_to(REPO_DIR)
                lines.append(f"  - `{rel}:{occ.line_num}` — `{occ.line}`")
            if result.vet_record:
                lines.append(f"- **Vet Record**: {result.vet_record.vet_id} ({result.vet_record.decision}, {result.vet_record.score}/10)")
                if result.vet_record.scope:
                    lines.append(f"- **Scope**: {result.vet_record.scope}")
            lines.append("")
    return "\n".join(lines)


def generate_corrected_credits(classifications: Dict[str, ClassificationResult]) -> str:
    """Generate corrected CREDITS.md registry with only LEGITIMATE tags."""
    legitimate = [c for c in classifications.values() if c.classification.startswith("LEGITIMATE")]

    lines = [
        "# 🔱 id Software Architectural Heritage — Attribution Framework (CORRECTED)",
        "# ⬡ OMEGA ⬡ CREDITS ⬡ v2.0.0-CORRECTED ⬡ D208 Heritage Remediation",
        "",
        "## Mandate: Full Attribution Required",
        "",
        "Every Omega Engine pattern derived from id Software's innovations MUST credit the original source.",
        "> *\"A people that no longer remembers has lost its soul.\"*",
        "",
        "---",
        "",
        "## §1 Heritage Registry (Corrected — D208)",
        "",
        "| # | Pattern | Source | Status | Tag |",
        "|---|---------|--------|--------|-----|",
    ]

    for i, c in enumerate(sorted(legitimate, key=lambda x: x.tag_key), 1):
        vet = c.vet_record
        if vet:
            # Extract game/year from vet_id or concept
            source = "id Software"
            if "doom-1993" in c.tag_key or "doom-1993" in (vet.concept or "").lower():
                source = "Doom 1993"
            elif "quake-1996" in c.tag_key or "quake-1996" in (vet.concept or "").lower():
                source = "Quake 1996"
            elif "quake3-1999" in c.tag_key or "quake3-1999" in (vet.concept or "").lower():
                source = "Quake 1999"
            elif "doom3-2004" in c.tag_key or "doom3-2004" in (vet.concept or "").lower():
                source = "DOOM 3 2004"
            elif "doom3bfg-2012" in c.tag_key or "doom3bfg-2012" in (vet.concept or "").lower():
                source = "DOOM 3 BFG 2012"

            status = "✅ PROMOTED" if vet.decision.upper() in ("ADOPT", "ADAPT") else "⚠️ NEEDS REVIEW"
            lines.append(f"| {i} | {c.tag_key.split('] ')[1] if '] ' in c.tag_key else c.tag_key} | {source} | {status} | `{c.tag_key}` |")

    lines.extend([
        "",
        f"**Total**: {len(legitimate)} LEGITIMATE mappings",
        "",
        "---",
        "",
        "## §2 Removed Tags (METAPHORICAL / OVER-ATTRIBUTED)",
        "",
        "The following tags were classified as non-legitimate and should be removed from source code:",
        "",
    ])

    for cat in ["METAPHORICAL", "OVER-ATTRIBUTED"]:
        cat_results = [c for c in classifications.values() if c.classification.startswith(cat)]
        if not cat_results:
            continue
        lines.append(f"### {cat} ({len(cat_results)})")
        lines.append("")
        for c in sorted(cat_results, key=lambda x: x.tag_key):
            lines.append(f"- `{c.tag_key}` — {c.reason}")
            lines.append(f"  - **Remediation**: {c.remediation}")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## §3 Attribution Enforcement Rules (Unchanged)",
        "",
        "### Rule 1: R-docs Must Have Heritage Section",
        "```markdown",
        "### Heritage",
        "This pattern derives from: [id Software Concept: Year]",
        "```",
        "",
        "### Rule 2: Code Must Credit in Comments",
        "```python",
        "# ── BSP-style provider culling [BSP Culling: id Software 1993] ──",
        "```",
        "",
        "### Rule 2a: Inline `[id-soft:]` Tag Protocol (D208 Enhanced)",
        "**Format**: `# [id-soft: GAME YEAR] Pattern Name — why this code exists`",
        "",
        "**Game codes**: `doom-1993`, `quake-1996`, `quake2-1997`, `quake3-1999`, `doom3-2004`, `doom3bfg-2012`, `wolf3d-2012`",
        "",
        "**Enforcement**: `grep -rn \"\\[id-soft:\" src/omega/` — CI gate via `make heritage-vet`",
        "",
        "### Rule 3: Decisions Must Cite Source",
        "```markdown",
        "- **Decision XX**: Chose X per [Carmack's Law: id Software].",
        "```",
        "",
        "### Rule 4: Evolution Must Be Explicit",
        "Show: (1) original (2) what changed (3) why",
        "",
        "### Rule 5: No Erasure",
        "Credit stays even if pattern is refactored. Heritage is gratitude, not IP.",
        "",
        "---",
        "",
        "## §4 The \"Right Approximation\" Principle",
        "",
        "> **\"The right approximation for the problem is better than the exact solution you can't afford.\"**",
        "",
        "| Tier | Domain | Approximation | Why |",
        "|------|--------|---------------|-----|",
        "| 1 | Provider health | BSP culling: O(1) breaker check | Stale-read skip cheaper than guaranteed failure |",
        "| 2 | Memory | Tiered hot/warm/cold | Not all entities need full vector context |",
        "| 3 | Entity dispatch | Domain matching, not perfect | Route to closest, re-route if wrong |",
        "| 4 | Model inference | Local-first, cloud-fallback | Local \"good enough\" for 90% of queries |",
        "",
        "---",
        "",
        "## §5 User's Own Technology (No Attribution Required)",
        "",
        "These patterns are the user's OWN IP — evolved through ANAi → XNAi → omega-stack → omega-engine:",
        "",
        "| Pattern | First Appearance | Current Location |",
        "|---------|-----------------|------------------|",
        "| 3-Tier Memory (Hot/Warm/Cold) | ANAi Aug 2025 | `memory_store.py` |",
        "| Provider Chain (Redis→File→InMemory) | ANAi Sep 2025 | `memory/providers.py` |",
        "| Intent Detection | ANAi Aug 2025 | `oracle.py` |",
        "| Entity Registry (YAML CRUD) | ANAi Oct 2025 | `entity_registry.py` |",
        "| ResourceGuard (OOM protection) | omega-stack May 2026 | `resource_guard.py` |",
        "| MCP Hub (47 tools) | omega-stack May 2026 | `omega_hub/server.py` |",
        "| Hivemind Protocol | omega-engine Jun 2026 | `omega_hub/server.py` |",
        "| Soul Distiller (L1→L2→L3) | omega-engine Jun 2026 | `soul_distiller.py` |",
        "| MaKaLi Triad | omega-engine Jun 2026 | `makali.md` |",
        "| Sovereign Mandates | omega-engine Jun 2026 | `SOVEREIGN_MANDATES.md` |",
        "| Engine-Stack Firewall | omega-engine Jun 2026 | `SOVEREIGN_MANDATES.md` (M2) |",
        "| Circuit Breaker Consolidation | omega-engine Jun 2026 | `model_gateway.py` |",
        "| PEM (Personality Enhancement Module) | Lilith Deck Mar 2025 | `entity_registry.py` |",
        "",
        "---",
        "",
        "## §6 How to Add New Mapping",
        "",
        "```markdown",
        "### N.x [Concept Name] (Game, Year)",
        "| Aspect | id Software Original | Omega Engine Adaptation |",
        "|--------|--------------------|------------------------|",
        "| **Origin** | Creator — description | Omega implementation |",
        "| **Core idea** | What it did | What we do |",
        "| **Omega evolution** | How we changed it | Why we changed it |",
        "",
        "**Attribution format**: `[Tag: source]`",
        "```",
        "",
        "---",
        "",
        f"**Full detailed tables**: `docs/archive/coordination/CREDITS-full-20260708.md`",
        "",
        f"*Last Updated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')} | {len(legitimate)} Heritage Mappings | D208 Heritage Remediation Complete*",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Heritage Audit — D208 Classification")
    parser.add_argument("--classify-all", action="store_true", help="Classify all tags")
    parser.add_argument("--output-report", action="store_true", help="Write remediation report to file")
    parser.add_argument("--output-credits", action="store_true", help="Write corrected CREDITS.md to file")
    args = parser.parse_args()

    if not args.classify_all and not args.output_report and not args.output_credits:
        args.classify_all = True
        args.output_report = True
        args.output_credits = True

    print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
    print(f" 🏛️  Heritage Audit — D208 Classification & Remediation")
    print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")

    if not VET_LOG.exists():
        print(f"  {RED}❌ HERITAGE_VET_LOG.md not found{NC}")
        return 2

    vet_log_content = VET_LOG.read_text(encoding="utf-8")
    vet_records = parse_vet_log(vet_log_content)
    print(f"  {CYAN}Loaded {len(vet_records)} vet records.{NC}")

    occurrences = scan_source_files()
    print(f"  {CYAN}Found {len(occurrences)} tag occurrences in source.{NC}")

    # Classify each occurrence
    results: List[ClassificationResult] = []
    for occ in occurrences:
        result = classify_tag(occ, vet_records)
        results.append(result)

    # Merge by tag_key
    classifications = merge_classifications(results)

    # Print summary
    counts = {"LEGITIMATE": 0, "METAPHORICAL": 0, "OVER-ATTRIBUTED": 0}
    for c in classifications.values():
        key = c.classification.split()[0]
        counts[key] = counts.get(key, 0) + 1

    print(f"\n  {GREEN}LEGITIMATE:{NC} {counts.get('LEGITIMATE', 0)}")
    print(f"  {YELLOW}METAPHORICAL:{NC} {counts.get('METAPHORICAL', 0)}")
    print(f"  {RED}OVER-ATTRIBUTED:{NC} {counts.get('OVER-ATTRIBUTED', 0)}")

    # Output report
    if args.output_report:
        REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
        report = generate_remediation_report(classifications)
        REPORT_FILE.write_text(report, encoding="utf-8")
        print(f"\n  {GREEN}✅ Remediation report written to {REPORT_FILE}{NC}")

    # Output corrected credits
    if args.output_credits:
        corrected = generate_corrected_credits(classifications)
        CORRECTED_CREDITS_FILE.parent.mkdir(parents=True, exist_ok=True)
        CORRECTED_CREDITS_FILE.write_text(corrected, encoding="utf-8")
        print(f"  {GREEN}✅ Corrected CREDITS.md written to {CORRECTED_CREDITS_FILE}{NC}")

    # Print detailed results
    print(f"\n{CYAN}━━━ Detailed Classification ━━━{NC}")
    for cat in ["OVER-ATTRIBUTED", "METAPHORICAL", "LEGITIMATE"]:
        cat_results = [c for c in classifications.values() if c.classification.startswith(cat)]
        if not cat_results:
            continue
        color = RED if cat == "OVER-ATTRIBUTED" else (YELLOW if cat == "METAPHORICAL" else GREEN)
        print(f"\n  {color}{cat} ({len(cat_results)}){NC}")
        for c in sorted(cat_results, key=lambda x: x.tag_key):
            print(f"    {color}→{NC} {c.tag_key}")
            for occ in c.occurrences:
                rel = occ.file.relative_to(REPO_DIR)
                print(f"      {rel}:{occ.line_num}")

    return 0


if __name__ == "__main__":
    import re
    sys.exit(main())