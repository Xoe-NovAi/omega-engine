#!/usr/bin/env python3
"""Tag stale R-docs with STALE header annotation.
AP: AP-TAG-STALE-v1.0.0
Criteria: last-modified > 14 days ago OR content is from legacy-era bulk dump.
"""

import os
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta

RESEARCH_DIR = Path(__file__).resolve().parent.parent / "docs" / "research"
STALE_CUTOFF = datetime.now(timezone.utc) - timedelta(days=14)

# Always-keep files regardless of date
KEEP_LIST = {
    "INDEX.md", "_TEMPLATE.md",
}

def is_stale_by_date(path: Path) -> bool:
    """Check if file was last modified before the 14-day cutoff."""
    mtime = os.path.getmtime(path)
    mtime_dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
    return mtime_dt < STALE_CUTOFF

def has_stale_tag(content: str) -> bool:
    """Check if file already has a STALE tag."""
    return "**Status**: STALE" in content or "**Status**: 🔴 STALE" in content

def tag_stale(path: Path) -> bool:
    """Add STALE status tag to a stale R-doc."""
    with open(path) as f:
        content = f.read()
    
    if has_stale_tag(content):
        return False  # Already tagged
    
    # Find the header section (between first # line and first ## or content gap)
    lines = content.split("\n")
    
    # Find where to insert the status line — after the first line starting with #
    # and before the next ## or blank line gap
    insert_pos = None
    for i, line in enumerate(lines):
        if line.startswith("# ") and not line.startswith("## "):
            continue  # Skip header line itself
        if insert_pos is None:
            # Find end of header block (blank line after metadata)
            if line.strip() == "" and i > 0 and (lines[i-1].strip() == "" or lines[i-1].startswith("#")):
                insert_pos = i
                break
            if line.startswith("##"):
                insert_pos = i
                break
    
    if insert_pos is None:
        # Fallback: insert after first line
        insert_pos = 1
    
    # Insert STALE tag
    stale_line = "\n**Status**: 🔴 STALE — Legacy document from pre-June 2026. Contents may be outdated.\n"
    lines.insert(insert_pos, stale_line)
    
    with open(path, "w") as f:
        f.write("\n".join(lines))
    
    return True

def main():
    stale_count = 0
    tagged_count = 0
    already_tagged = 0
    
    for path in sorted(RESEARCH_DIR.iterdir()):
        if not path.is_file() or not path.name.endswith(".md"):
            continue
        if path.name in KEEP_LIST:
            continue
        
        content = path.read_text()
        
        # Check if it's a legacy-era file (May 23 or earlier)
        if "May 23" in content or "May 2026" in path.name:
            if not has_stale_tag(content):
                if tag_stale(path):
                    tagged_count += 1
                    print(f"  🏷️  {path.name}")
            else:
                already_tagged += 1
            stale_count += 1
            continue
        
        # Check by date
        if is_stale_by_date(path):
            stale_count += 1
            if not has_stale_tag(content):
                if tag_stale(path):
                    tagged_count += 1
                    print(f"  🏷️  {path.name}")
            else:
                already_tagged += 1
    
    print(f"\nSummary: {stale_count} stale, {tagged_count} newly tagged, {already_tagged} already tagged")
    return 0

if __name__ == "__main__":
    main()
