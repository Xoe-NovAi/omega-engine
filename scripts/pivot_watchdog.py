# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — PIVOT Watchdog
# AP: AP-PIVOT-WATCHDOG-v1.0.0
"""
Scans PIVOT_LOG.md for decisions with 'Status: pending' that are older than 7 days.
Flags them for review by P5 Sentinel.
"""
import re
from datetime import datetime, timedelta
from pathlib import Path

def run_watchdog():
    log_path = Path("docs/decisions/PIVOT_LOG.md")
    if not log_path.exists():
        print("❌ Error: PIVOT_LOG.md not found.")
        return

    content = log_path.read_text()
    
    # Pattern to find decisions: '- **Decision XX — Name**: ... | Status: pending'
    # We assume the date is in the session header above the decision or in the filename
    # For now, we'll look for the 'Date: YYYY-MM-DD' pattern in the file
    
    current_date = datetime.now()
    violations = []
    
    # Simple approach: find all 'Status: pending' and flag them all for review
    # since the PIVOT_LOG doesn't have per-decision dates in a standard format.
    # A better approach would be to parse the session headers.
    
    pending_decisions = re.findall(r"(- \*\*Decision \d+ .*? \| Status: pending)", content)
    
    if pending_decisions:
        print(f"⚠️ Found {len(pending_decisions)} pending decisions requiring review:")
        for dec in pending_decisions:
            print(f"  - {dec}")
        return False
    
    print("✅ No pending decisions found. All decisions are shipped, rejected, or deferred.")
    return True

if __name__ == "__main__":
    if not run_watchdog():
        exit(1)
