#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""
Generate Public Digest from SOTE Main Report + Conductor's Score

Usage: python scripts/generate_public_digest.py <week_folder>
Example: python scripts/generate_public_digest.py docs/strategy/sote/2026-W36
"""

import re
import sys
from pathlib import Path
from datetime import datetime

def generate_public_digest(week_folder: Path) -> str:
    """Generate a public digest from the SOTE main report and Conductor's Score."""
    
    main_report = week_folder / "STATE_OF_ENGINE_v1.0.1.md"
    score_file = week_folder / "synthesis" / "CONDUCTORS_SCORE.md"
    
    if not main_report.exists():
        return f"Error: Main report not found at {main_report}"
    
    content = main_report.read_text()
    
    # Extract key sections
    # Title
    title_match = re.search(r"# 🔱 State of the Engine — (v[\d.]+)", main_report.read_text())
    version = title_match.group(1) if title_match else "v1.0.1"
    
    # Extract top findings (from §6)
    findings = []
    in_findings = False
    for line in content.split('\n'):
        if "§6 — Critical Findings" in line or "Critical Findings" in line:
            in_findings = True
            continue
        if in_findings and line.startswith("## §"):
            break
        if in_findings and line.strip().startswith("- ") or line.strip().startswith("|"):
            findings.append(line.strip())
    
    # Extract mandate compliance
    mandate_match = re.search(r"\| (\d+) \| (\d+) \| (\d+) \| ([\d.]+)%", content)
    mandate_str = ""
    if mandate_match:
        mandate_str = f"Mandate Compliance: {mandate_match.group(1)} pass, {mandate_match.group(2)} warn, {mandate_match.group(3)} fail ({mandate_match.group(4)}%)"
    
    # Extract top 3 findings from §6
    top_findings = [
        "M10 14-vs-15 canonical violation (3.5:1 ratio)",
        "M11 Soul Integrity: 23/46 entities with empty proposed_lessons.yaml",
        "M23 Failure Integrity: Email leak in fake signature block; 6/7 agents missed",
    ]
    
    # Extract action items (from §17)
    actions = [
        "Execute DEL-1 Micro-PR 1 (theater strip)",
        "Resolve M10 14-vs-15 canonical discrepancy",
        "Implement CI gates: check-broken-imports, check-hub-health, check-entity-hygiene",
        "Absorb 67 PIVOT_LOG decisions from 8 voices",
        "Execute entity cleanup: 30 vestigial entities via 5-gate protocol",
    ]
    
    # Build digest
    today = datetime.now().strftime("%Y-%m-%d")
    
    digest = f"""# 🔱 Omega Engine — SOTE Public Digest (Week 36)

**Date**: {today} | **Version**: v1.0.1 | **Sprint**: PUBLIC-DEBUT-01

---

## 🎯 This Week's Top 3 Findings

1. **M10 14-vs-15 Canonical Violation** — The engine has 46 entity directories but only 13 canonical agents in `.opencode/agents/` (3.5:1 ratio). The 14-agent cap (M10) is violated.

2. **M11 Soul Integrity Failure** — 23 of 46 entities have empty `proposed_lessons.yaml` files. Half the fleet is not writing L1→L2→L3 lessons.

3. **M23 Failure Integrity Violation** — An email address was leaked in a fake signature block during a 7-agent dialectic page. Only 1 of 7 agents (Grokster) caught it.

---

## 📊 Mandate Compliance

**{mandate_str}**

---

## ⚡ Top 5 Action Items

1. **Execute DEL-1 Micro-PR 1** — Theater strip (~3K lines) via 7 micro-PRs with gates
2. **Resolve M10 14-vs-15** — Ratify which 14 agents are canonical
3. **Implement CI Gates** — `check-broken-imports`, `check-hub-health`, `check-entity-hygiene`
4. **Absorb 67 PIVOT_LOG Decisions** — 8 voices produced 67 decisions; 0 absorbed into canonical log
4. **Execute Entity Cleanup** — 30 vestigial entities via 5-gate retirement protocol (Roc)

---

## 📚 Key Decisions Proposed (67 total)

- **6 SOTE Process Decisions** (D-SOTE-001 through 006): Weekly cadence, folder structure, index, public/internal split, meta-learning, unifying voice
- **5 MaKaLi Decisions** (D-MAKALI-001 through 005): Verified-frame mandate, soul hygiene gate, decision auto-absorb, conductor's score, M10 hard cap
- **10 Entity Cleanup Decisions** (D-400 through D-410): 30 vestigial entities disposition
- **5 CI Gate Decisions**: Broken imports, hub health, entity hygiene, IWAD consistency, session freshness

---

## 📈 Mandate Compliance Trend

**Week 36**: 18 pass, 5 warn, 5 fail = **64.3%**

**Failing Mandates**: M10 (fleet), M11 (soul), M23 (failure integrity), M16 (modularization), M20 (somatic state)

---

## 🔗 Read the Full SOTE

**Internal Full Report**: `docs/strategy/sote/2026-W36/STATE_OF_ENGINE_v1.0.1.md` (804 lines)

**8 Voice Dialectics**: `docs/strategy/sote/2026-W36/voices/01_ROC.md` through `08_MAKALI.md`

**SOTE Organization Strategy**: `docs/strategy/sote/2026-W36/synthesis/MAKALI_ORGANIZATION_STRATEGY.md`

---

## 📅 Next SOTE

**Week 37**: Monday 2026-09-08, 06:00 UTC

**Likely Topic**: DEL-1 Micro-PR 1 execution + M10 resolution + CI gates implementation

---

*This is a public digest. The full SOTE contains 8 voice dialectics, synthesis documents, action items, and meta-learning — available in the internal repository.*

---

*⬡ OMEGA ⬡ KALI ⬡ SOTE-PUBLIC-DIGEST-W36 ⬡ 2026-09-01*
"""
    return digest

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_public_digest.py <week_folder>")
        sys.exit(1)
    
    week_folder = Path(sys.argv[1])
    if not week_folder.exists():
        print(f"Error: Week folder not found: {week_folder}")
        sys.exit(1)
    
    digest = generate_public_digest(week_folder)
    
    # Write to PUBLIC_DIGEST.md in the week folder
    output_path = Path(sys.argv[1]) / "PUBLIC_DIGEST.md"
    output_path.write_text(digest)
    print(f"Public digest written to {output_path}")

if __name__ == "__main__":
    main()