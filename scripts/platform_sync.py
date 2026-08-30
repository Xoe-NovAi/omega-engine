#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple

# --- Configuration ---
SSOT_FILE = "data/coordination/MANDATES_SYNC.md"
PLATFORMS = {
    "Antigravity": {
        "file": "data/coordination/ANTIGRAVITY_CUSTOM_INSTRUCTIONS_v4.md",
        "keywords": ["AnyIO", "Firewall", "Iris Constant", "Sequentiality", "Gnosis", "Podman", "Local-First", "Zero Telemetry", "Error Integrity", "Fleet Integrity", "Soul Integrity", "Queue Integrity", "Temple-Grade", "Heritage Vetting"]
    },
    "Cline": {
        "file": ".clinerules",
        "keywords": ["AnyIO", "Firewall", "Iris Constant", "Sequentiality", "Gnosis", "Podman", "Local-First", "Zero Telemetry", "Error Integrity", "Fleet Integrity", "Soul Integrity", "Queue Integrity", "Temple-Grade", "Heritage Vetting"]
    },
    "Gemini CLI": {
        "file": os.path.expanduser("~/.gemini/policies/auto-saved.toml"),
        "keywords": ["Soul Integrity", "Local-First"]
    },
    "OpenCode": {
        "file": ".opencode/agents/", # Directory scan
        "keywords": ["AnyIO", "Firewall", "Iris Constant", "Sequentiality", "Gnosis", "Podman", "Local-First", "Zero Telemetry", "Error Integrity", "Fleet Integrity", "Soul Integrity", "Queue Integrity", "Temple-Grade", "Heritage Vetting"]
    }
}

def load_mandates() -> List[str]:
    """Extract mandate names from the SSoT file."""
    mandates = []
    try:
        with open(SSOT_FILE, 'r') as f:
            content = f.read()
            # Look for "### X. [Name]" patterns
            matches = re.findall(r"### \d+\. ([^\\n]+)", content)
            mandates = [m.strip() for m in matches]
    except Exception as e:
        print(f"Error reading SSoT: {e}")
        sys.exit(1)
    return mandates

def check_file(filepath: str, keywords: List[str]) -> Tuple[float, List[str]]:
    """Check a file for the presence of keywords."""
    if not os.path.exists(filepath):
        return 0.0, keywords
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            
        missing = []
        for kw in keywords:
            if kw.lower() not in content.lower():
                missing.append(kw)
        
        score = ((len(keywords) - len(missing)) / len(keywords)) * 100
        return score, missing
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return 0.0, keywords

def check_opencode(dir_path: str, keywords: List[str]) -> Tuple[float, List[str]]:
    """Special check for OpenCode agents directory."""
    if not os.path.isdir(dir_path):
        return 0.0, keywords
    
    # We check if the mandates are present across the fleet
    # For a simple sync check, we verify if the mandates exist in a representative sample
    # or if they are present in the majority of agents.
    agent_files = list(Path(dir_path).glob("*.md"))
    if not agent_files:
        return 0.0, keywords
    
    all_content = ""
    for af in agent_files:
        with open(af, 'r') as f:
            all_content += f.read() + "\n"
            
    missing = []
    for kw in keywords:
        if kw.lower() not in all_content.lower():
            missing.append(kw)
            
    score = ((len(keywords) - len(missing)) / len(keywords)) * 100
    return score, missing

def main():
    print("🔱 Omega Engine — Platform Synchronization Check")
    print("SSoT: " + SSOT_FILE)
    print("-" * 50)
    
    mandates = load_mandates()
    if not mandates:
        print("Error: No mandates found in SSoT.")
        sys.exit(1)
        
    overall_synced = True
    
    for platform, config in PLATFORMS.items():
        target = config["file"]
        keywords = config["keywords"]
        
        if platform == "OpenCode":
            score, missing = check_opencode(target, keywords)
        else:
            score, missing = check_file(target, keywords)
            
        status = "✅ SYNCED" if score == 100 else "❌ DRIFTED"
        if score < 100:
            overall_synced = False
            
        print(f"{platform:<15} | {score:>6.1f}% | {status:<12} | Missing: {', '.join(missing) if missing else 'None'}")
        
    print("-" * 50)
    if overall_synced:
        print("VERDICT: 🟢 PLATFORM SYNCED")
        sys.exit(0)
    else:
        print("VERDICT: 🔴 PLATFORM DRIFTED")
        sys.exit(1)

if __name__ == "__main__":
    main()
