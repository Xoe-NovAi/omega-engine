#!/usr/bin/env python3
"""End-to-end recall stack verification. Runs in CI."""

import subprocess
import json
import sys

def run_cmd(cmd: str) -> dict:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return {"stdout": result.stdout, "stderr": result.stderr, "rc": result.returncode}

def test_recall_stack():
    failures = []
    
    # 1. /recall via ochist (search term extraction)
    r = run_cmd('ochist grep "pin trap" --global --limit 3')
    if r["rc"] != 0 or "pin trap" not in r["stdout"]:
        failures.append("recall: ochist grep failed")
    
    # 2. /db via ocdb-ro (read-only SQL)
    r = run_cmd('ocdb-ro --search "gnosis" --limit 2')
    if r["rc"] != 0 or "gnosis" not in r["stdout"]:
        failures.append("db: ocdb-ro search failed")
    
    # 3. Session cost aggregate
    r = run_cmd('ocdb-ro "SELECT ROUND(SUM(cost),2) AS usd, COUNT(*) AS sessions FROM session"')
    if r["rc"] != 0:
        failures.append("db: cost aggregate failed")
    
    # 4. Schema lookup
    r = run_cmd('ocdb-ro --schema part')
    if r["rc"] != 0 or "CREATE TABLE" not in r["stdout"]:
        failures.append("db: schema lookup failed")
    
    # 5. Safety: ocdb-ro blocks DDL
    r = run_cmd('ocdb-ro "CREATE TABLE evil(x)"')
    if r["rc"] == 0:
        failures.append("SAFETY: ocdb-ro allowed DDL (should reject)")
    
    if failures:
        print("FAILURES:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("✅ All recall stack checks passed")

if __name__ == "__main__":
    test_recall_stack()
