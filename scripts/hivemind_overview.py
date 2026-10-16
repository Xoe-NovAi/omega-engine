#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
# SPDX-License-Identifier: Apache-2.0

"""
CLI Reader for Hivemind Overview.
Usable by subagents and terminal operators without MCP access.
"""

import sys
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Read Hivemind Fleet Overview")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Output format")
    parser.add_argument("--radar-only", action="store_true", help="Print only top 3 radar lines")
    args = parser.parse_args()
    
    repo_root = Path(__file__).resolve().parent.parent
    overview_dir = repo_root / "data" / "coordination" / "hivemind_overview"
    target_file = overview_dir / ("latest.md" if args.format == "md" else "latest.json")
    
    if not target_file.exists():
        print("⚠️ Hivemind Overview not available yet. (latest file missing)")
        sys.exit(1)
        
    content = target_file.read_text(encoding="utf-8")
    
    if args.radar_only and args.format == "md":
        lines = content.strip().split("\n")
        print("\n".join(lines[:3]))
    else:
        print(content)
        
    sys.exit(0)


if __name__ == "__main__":
    main()