#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
Token counter for documentation files.
Checks token counts against budgets defined in token_budgets.yaml.
"""

import argparse
import sys
from pathlib import Path
import yaml
import tiktoken

# Use cl100k_base encoding (GPT-4, GPT-3.5, etc.)
ENCODING = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    """Count tokens in text using tiktoken."""
    return len(ENCODING.encode(text))

def load_budgets(budget_file: Path) -> dict:
    """Load token budgets from YAML."""
    with open(budget_file) as f:
        return yaml.safe_load(f)

def get_doc_type(filepath: Path) -> str:
    """Determine document type from path."""
    path_str = str(filepath)
    
    if "sprints" in path_str and "index.md" in path_str:
        return "sprint_plan"
    elif "sprints" in path_str and "tickets" in path_str:
        return "ticket_page"
    elif "research-index" in path_str:
        return "research_index"
    elif "architecture" in path_str or "deep-dive" in path_str:
        return "architecture_spec"
    elif "protocol" in path_str or "spec" in path_str:
        return "protocol_spec"
    elif "agent" in path_str or "skill" in path_str:
        return "agent_skill_def"
    else:
        return "reference_doc"

def check_file(filepath: Path, budgets: dict) -> tuple:
    """Check a single file against its budget."""
    content = filepath.read_text()
    tokens = count_tokens(content)
    doc_type = get_doc_type(filepath)
    
    budget = budgets.get("token_budgets", {}).get(doc_type, {})
    hard_limit = budget.get("hard_limit", 16000)
    soft_limit = budget.get("soft_limit", 12800)
    target = budget.get("target", 8000)
    
    status = "OK"
    if tokens > hard_limit:
        status = "HARD_LIMIT_EXCEEDED"
    elif tokens > soft_limit:
        status = "SOFT_LIMIT_EXCEEDED"
    elif tokens > target:
        status = "OVER_TARGET"
    
    return {
        "file": str(filepath),
        "doc_type": doc_type,
        "tokens": tokens,
        "target": target,
        "soft_limit": soft_limit,
        "hard_limit": hard_limit,
        "status": status
    }

def main():
    parser = argparse.ArgumentParser(description="Check documentation token budgets")
    parser.add_argument("--budget", required=True, help="Path to token_budgets.yaml")
    parser.add_argument("paths", nargs="+", help="Files or directories to check")
    
    args = parser.parse_args()
    
    budgets = load_budgets(Path(args.budget))
    
    all_results = []
    for path_str in args.paths:
        path = Path(path_str)
        if path.is_dir():
            for md_file in path.rglob("*.md"):
                if md_file.name in ["llms.txt", "llms-full.txt"]:
                    continue
                if md_file.is_file():  # Skip directories
                    all_results.append(check_file(md_file, budgets))
        else:
            all_results.append(check_file(path, budgets))
    
    # Print results
    print(f"{'FILE':<60} {'TYPE':<20} {'TOKENS':>8} {'TARGET':>8} {'SOFT':>8} {'HARD':>8} {'STATUS':<20}")
    print("-" * 140)
    
    has_errors = False
    for r in all_results:
        status_color = ""
        if r["status"] == "HARD_LIMIT_EXCEEDED":
            status_color = "\033[0;31m"  # Red
            has_errors = True
        elif r["status"] == "SOFT_LIMIT_EXCEEDED":
            status_color = "\033[1;33m"  # Yellow
        elif r["status"] == "OVER_TARGET":
            status_color = "\033[0;33m"  # Yellow
        else:
            status_color = "\033[0;32m"  # Green
        
        reset = "\033[0m"
        file_short = r["file"][-58:] if len(r["file"]) > 58 else r["file"]
        print(f"{file_short:<60} {r['doc_type']:<20} {r['tokens']:>8} {r['target']:>8} {r['soft_limit']:>8} {r['hard_limit']:>8} {status_color}{r['status']:<20}{reset}")
    
    print("-" * 140)
    
    if has_errors:
        print("\n❌ HARD LIMIT EXCEEDED - Some documents exceed hard token limits")
        return 1
    else:
        print("\n✅ All documents within token budgets")
        return 0

if __name__ == "__main__":
    sys.exit(main())