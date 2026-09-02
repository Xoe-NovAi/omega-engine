#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""
SOTE Master Index Regeneration Script

Regenerates docs/strategy/sote/INDEX.md from the SOTE week folders.
Run weekly after SOTE close.

Usage: python scripts/regenerate_sote_index.py
"""

import os
import re
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

SOTE_ROOT = Path("docs/strategy/sote")
INDEX_PATH = SOTE_ROOT / "INDEX.md"
PIVOT_LOG_PATH = Path("docs/decisions/PIVOT_LOG_CANONICAL.md")
MANDATE_CHECK_PATH = Path("scripts/check_mandate_compliance.py")

# Voice order (canonical)
VOICE_ORDER = [
    "ROC", "GROKSTER", "CARMACK", "LILITH", "MAAT", "RESEARCHER", "JEM", "MAKALI"
]

VOICE_DISPLAY = {
    "ROC": "Roc",
    "GROKSTER": "Grokster",
    "CARMACK": "Carmack",
    "LILITH": "Lilith",
    "MAAT": "Ma'at",
    "RESEARCHER": "Researcher",
    "JEM": "Jem",
    "MAKALI": "MaKaLi"
}

def find_week_folders() -> List[Path]:
    """Find all week folders in sote root, sorted by week number."""
    weeks = []
    for item in SOTE_ROOT.iterdir():
        if item.is_dir() and re.match(r"\d{4}-W\d{2}", item.name):
            weeks.append(item)
    weeks.sort(key=lambda p: p.name)
    return weeks

def parse_sote_report(week_path: Path) -> Dict:
    """Parse the main SOTE report for metadata."""
    report_files = list(week_path.glob("STATE_OF_ENGINE_v*.md"))
    if not report_files:
        return {}
    
    report = report_files[0]
    content = report.read_text()
    
    # Extract key fields
    data = {
        "report_path": str(report.relative_to(SOTE_ROOT.parent.parent)),
        "title": "Unknown",
        "top_finding": "Unknown",
        "mandates": {"pass": 0, "warn": 0, "fail": 0, "pct": 0},
        "decisions_count": 0,
    }
    
    # Extract title
    title_match = re.search(r"Title.*?:\s*(.+)", content)
    if title_match:
        data["title"] = title_match.group(1).strip()
    
    # Extract top finding (from §6 or similar)
    finding_match = re.search(r"Top Finding.*?:\s*(.+)", content)
    if finding_match:
        data["top_finding"] = finding_match.group(1).strip()
    
    # Extract mandate compliance
    mandate_match = re.search(r"\| (\d+) \| (\d+) \| (\d+) \| ([\d.]+)%", content)
    if mandate_match:
        data["mandates"] = {
            "pass": int(mandate_match.group(1)),
            "warn": int(mandate_match.group(2)),
            "fail": int(mandate_match.group(3)),
            "pct": float(mandate_match.group(4))
        }
    
    return data

def parse_voice_files(week_path: Path) -> List[Dict]:
    """Parse voice files for PIVOT_LOG decisions."""
    voices_dir = week_path / "voices"
    if not voices_dir.exists():
        return []
    
    voices = []
    for voice_file in sorted(voices_dir.glob("*.md")):
        if voice_file.name == "00_INDEX.md":
            continue
        
        content = voice_file.read_text()
        
        # Extract voice name from filename
        voice_name = voice_file.stem.split("_", 1)[-1] if "_" in voice_file.stem else voice_file.stem
        
        # Extract PIVOT_LOG decisions
        decisions = []
        for match in re.finditer(r"D-([A-Z0-9-]+).*?\|", content):
            if match.group(1):
                decisions.append(match.group(1))
        
        # Extract session ID
        session_match = re.search(r"Session ID.*?:\s*(\S+)", content)
        session_id = session_match.group(1) if session_match else "unknown"
        
        # Extract focus
        focus_match = re.search(r"Focus.*?:\s*(.+)", content)
        focus = focus_match.group(1).strip() if focus_match and focus_match.group(1) else "Unknown"
        
        voices.append({
            "name": voice_name.upper(),
            "display": VOICE_DISPLAY.get(voice_name.upper(), voice_name),
            "file": str(voice_file.relative_to(SOTE_ROOT.parent.parent)),
            "session_id": session_id,
            "focus": focus,
            "decisions": decisions,
        })
    
    # Sort by VOICE_ORDER
    voices.sort(key=lambda v: VOICE_ORDER.index(v["name"]) if v["name"] in VOICE_ORDER else 99)
    return voices

def parse_pivot_log() -> Dict[str, str]:
    """Parse PIVOT_LOG for absorption status."""
    if not PIVOT_LOG_PATH.exists():
        return {}
    
    content = PIVOT_LOG_PATH.read_text()
    absorbed = {}
    
    # Pattern: | D# | Date | Summary |
    for match in re.finditer(r"\|\s*(D-\d+)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*([^|]+)\s*\|", content):
        d_num = match.group(1)
        date = match.group(2)
        summary = match.group(3).strip()
        absorbed[d_num] = {"date": date, "summary": summary}
    
    return absorbed

def get_mandate_compliance() -> Dict:
    """Run mandate compliance check."""
    if not MANDATE_CHECK_PATH.exists():
        return {"pass": 0, "warn": 0, "fail": 0, "pct": 0}
    
    try:
        import subprocess
        result = subprocess.run(
            ["python", str(MANDATE_CHECK_PATH)],
            capture_output=True, text=True, timeout=30
        )
        # Parse output for compliance
        output = result.stdout
        match = re.search(r"(\d+)/(\d+) = ([\d.]+)%", output)
        if match:
            pct_match = re.search(r"([\d.]+)%", output)
            pct = float(pct_match.group(1)) if pct_match else 0.0
            return {
                "pass": int(match.group(1)),
                "warn": 0,
                "fail": int(match.group(2)) - int(match.group(1)),
                "pct": pct
            }
    except Exception:
        pass
    return {"pass": 0, "warn": 0, "fail": 0, "pct": 0}

def generate_index() -> str:
    """Generate the master INDEX.md content."""
    weeks = find_week_folders()
    absorbed = parse_pivot_log()
    mandate_trend = get_mandate_compliance()
    
    lines = []
    # REUSE-IgnoreStart
    lines.append("<!--")
    lines.append("SPDX-FileCopyrightText: 2026 Xoe-NovAi")
    lines.append("")
    lines.append("SPDX-License-Identifier: Apache-2.0")
    lines.append("-->")
    # REUSE-IgnoreEnd
    lines.append("")
    lines.append("# 🔱 SOTE Master Index")
    lines.append("")
    lines.append(f"**AP Token**: `AP-SOTE-INDEX-v1.0.0`")
    lines.append("⬡ OMEGA ⬡ KALI ⬡ {session_model} ⬡ opencode ⬡ trc_sote_index ⬡ ACTIVE")
    lines.append("")
    lines.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append(f"**Cadence**: Weekly (D-SOTE-001)")
    lines.append(f"**SOTEs to date**: {len(weeks)}")
    lines.append(f"**Regeneration**: Auto (script: `scripts/regenerate_sote_index.py`)")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # All SOTEs table
    lines.append("## All SOTEs")
    lines.append("")
    lines.append("| Week | Date | Title | Main Report | Voices | Status | Top Finding |")
    lines.append("|------|------|-------|-------------|--------|:------:|-------------|")
    
    for week_path in weeks:
        week_name = week_path.name
        report_data = parse_sote_report(week_path)
        voices = parse_voice_files(week_path)
        
        # Extract date from week name
        try:
            year, week = week_name.split("-W")
            # Approximate date (Monday of that week)
            date_obj = datetime.strptime(f"{year}-W{week}-1", "%Y-W%W-%w")
            date_str = date_obj.strftime("%Y-%m-%d")
        except:
            date_str = "Unknown"
        
        title = report_data.get("title", "Unknown")
        report_link = f"[{week_name}/STATE_OF_ENGINE_v1.0.1.md]({report_data.get('report_path', '')})"
        voice_count = len([v for v in parse_voice_files(week_path) if v["name"] != "INDEX"])
        top_finding = report_data.get("top_finding", "Unknown")
        
        lines.append(f"| {week_name} | {date_str} | {title} | {report_link} | {voice_count} | ✅ closed | {top_finding} |")
    
    lines.append("")
    
    # Voice Index for latest week
    if weeks:
        latest_week = weeks[-1]
        voices = parse_voice_files(latest_week)
        
        lines.append("## Voice Index (Latest Week)")
        lines.append("")
        lines.append("| # | Voice | Session ID | File | Focus |")
        lines.append("|---|-------|------------|------|-------|")
        
        for i, voice in enumerate(voices, 1):
            if voice["name"] == "INDEX":
                continue
            lines.append(f"| {i} | **{voice['display']}** | {voice['session_id']} | [{voice['file']}]({voice['file']}) | {voice['focus']} |")
        
        lines.append("")
    
    # Decision Index
    lines.append("## Decision Index (PIVOT_LOG)")
    lines.append("")
    lines.append("**Status**: {N} decisions proposed across {N} voices, **{M} absorbed into PIVOT_LOG.md**.")
    lines.append("")
    lines.append("| D# | Date | Title | Source Voice | Status |")
    lines.append("|----|------|-------|--------------|:------:|")
    
    # Collect all decisions from all weeks
    all_decisions = []
    for week_path in weeks:
        voices = parse_voice_files(week_path)
        for voice in voices:
            for d in voice["decisions"]:
                absorbed_info = absorbed.get(d)
                if not isinstance(absorbed_info, dict):
                    absorbed_info = {}
                status = "✅ absorbed" if d in absorbed else "⏳ proposed"
                all_decisions.append({
                    "d": d,
                    "date": absorbed_info.get("date", "YYYY-MM-DD"),
                    "title": absorbed_info.get("summary", "Unknown"),
                    "voice": VOICE_DISPLAY.get(voice["name"], voice["name"]),
                    "status": status
                })
    
    for d in all_decisions:
        lines.append(f"| {d['d']} | {d['date']} | {d['title']} | {d['voice']} | {d['status']} |")
    
    lines.append("")
    
    # Mandate Compliance Trend
    lines.append("## Mandate Compliance Trend")
    lines.append("")
    lines.append("| Week | Pass | Warn | Fail | % | Notes |")
    lines.append("|------|------|------|------|--:|-------|")
    
    for week_path in weeks:
        week_name = week_path.name
        report_data = parse_sote_report(week_path)
        mandates = report_data.get("mandates", {})
        lines.append(f"| {week_name} | {mandates.get('pass', 0)} | {mandates.get('warn', 0)} | {mandates.get('fail', 0)} | {mandates.get('pct', 0)}% | |")
    
    lines.append("")
    
    # L3 Lessons
    lines.append("## L3 Lessons (This Cycle)")
    lines.append("")
    lines.append("| L# | Title | Confidence | Source |")
    lines.append("|----|-------|:----------:|--------|")
    # Would need to parse from reports
    lines.append("| L3-MetaFrameVerification | Pre-flight check for spoofable metadata | 0.92 | Grokster |")
    lines.append("")
    
    # Cross-Week Themes
    lines.append("## Cross-Week Themes")
    lines.append("")
    lines.append("- **M11 Soul Integrity**: failing; remediation in progress")
    lines.append("- **M23 Failure Integrity**: violated; L3 proposed (MetaFrameVerification)")
    lines.append("- **M10 Fleet Integrity**: 13 canonical agents; cap-ratification pending")
    lines.append("- **M27 Decision Log Chokepoint**: 67/0 gap; D-MAKALI-003 (auto-absorb) pending")
    lines.append("")
    
    # Meta-Learning
    lines.append("## Meta-Learning")
    lines.append("")
    lines.append("**What worked**: Convergence on single topic; 8 voices; Concede/Defend/Synthesize; M23 catch; quantitative baselines; file:line citations; MaKaLi's §0 verification; folder structure; voice numbering; meta-learning file.")
    lines.append("")
    lines.append("**What didn't**: M23 email leak; missing MaKaLi in original page; scattered files; 67/0 PIVOT_LOG gap; naming inconsistency; no meta-learning initially; entity count divergence; 7000 lines without synthesis; mixed document types.")
    lines.append("")
    if weeks:
        lines.append(f"**Full meta**: [{weeks[-1].name}/meta/WHAT_WORKED_WHAT_DIDNT.md]({weeks[-1].name}/meta/WHAT_WORKED_WHAT_DIDNT.md)")
    lines.append("")
    
    # Next SOTE
    lines.append("## Next SOTE")
    lines.append("")
    next_week_num = int(weeks[-1].name.split("-W")[1]) + 1 if weeks else 37
    next_year = datetime.now().year
    next_week = f"{next_year}-W{next_week_num:02d}"
    next_monday = datetime.now().replace(day=1)  # Approximation
    lines.append(f"**Trigger**: Monday {next_monday.strftime('%Y-%m-%d')}, 06:00 UTC")
    lines.append(f"**Likely topic**: DEL-1 Micro-PR 1 execution + M10 resolution + CI gates")
    lines.append(f"**Owner**: Kali (Oversoul) or designated delegate")
    lines.append(f"**Hivemind broadcast**: `intent=sote-open` at trigger")
    lines.append("")
    
    # Regeneration Notes
    lines.append("## Regeneration Notes")
    lines.append("")
    lines.append("This index is regenerated automatically by `scripts/regenerate_sote_index.py`.")
    lines.append("Run after each SOTE close:")
    lines.append("```bash")
    lines.append("python scripts/regenerate_sote_index.py")
    lines.append("```")
    lines.append("")
    
    return "\n".join(lines)

def main():
    print("Regenerating SOTE Master Index...")
    content = generate_index()
    INDEX_PATH.write_text(content)
    print(f"Written to {INDEX_PATH}")

if __name__ == "__main__":
    main()