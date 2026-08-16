#!/usr/bin/env python3
import sys
import re

def check_commit_message(commit_msg_file):
    with open(commit_msg_file, 'r') as f:
        msg = f.read().strip()

    # Only trigger on bug fixes
    if not re.match(r'^(fix|bug|hotfix)(\(.*?\))?:', msg, re.IGNORECASE):
        return 0

    # Look for the Socratic markers
    has_root_cause = re.search(r'Root Cause:', msg, re.IGNORECASE)
    has_prevention = re.search(r'Prevention Gate:', msg, re.IGNORECASE)

    if not (has_root_cause and has_prevention):
        print("\n" + "="*60)
        print("🛡️  SOCRATIC COMMIT REJECTED (Cognitive Sovereignty Rule)")
        print("="*60)
        print("You are attempting to commit a bug fix without forensic analysis.")
        print("A fix without a prevention gate is a temporary patch.\n")
        print("Please append the following to your commit message:\n")
        print("Root Cause: <Explain WHY this bug occurred systemically>")
        print("Prevention Gate: <Explain WHAT prevents it from returning>")
        print("="*60 + "\n")
        return 1
        
    return 0

if __name__ == "__main__":
    if len(sys.argv) > 1:
        sys.exit(check_commit_message(sys.argv[1]))
