#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
# SPDX-License-Identifier: Apache-2.0

"""
check_policy_constants.py — One constant for stale threshold [M29]

Enforces: handoff.stale_threshold_days == handoff.hot_storage_max_days

Coincidence is a bug waiting to drift. If two policies derive from separate
constants, they WILL drift silently — the same failure mode as
retention_expires_at being a stored field instead of a derived one.
"""

import sys
import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
POLICY_FILE = PROJECT_ROOT / "config" / "handoff_policy.yaml"

def main() -> int:
    print("=" * 70)
    print("Policy Constants Gate — Single Source of Truth [M29]")
    print("=" * 70)
    
    if not POLICY_FILE.exists():
        print(f"❌ FAIL: Policy file not found: {POLICY_FILE}")
        return 1
    
    try:
        with open(POLICY_FILE) as f:
            policy = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ FAIL: Could not parse {POLICY_FILE}: {e}")
        return 1
    
    handoff_policy = policy.get("handoff", {})
    stale_threshold = handoff_policy.get("stale_threshold_days")
    hot_storage_max = handoff_policy.get("hot_storage_max_days")
    
    print(f"\nPolicy file: {POLICY_FILE}")
    print(f"  handoff.stale_threshold_days: {stale_threshold}")
    print(f"  handoff.hot_storage_max_days: {hot_storage_max}")
    
    if stale_threshold is None:
        print("❌ FAIL: handoff.stale_threshold_days not defined")
        return 1
    
    if hot_storage_max is None:
        print("❌ FAIL: handoff.hot_storage_max_days not defined")
        return 1
    
    if stale_threshold != hot_storage_max:
        print(f"\n❌ FAIL: Constants diverge!")
        print(f"  stale_threshold_days ({stale_threshold}) != hot_storage_max_days ({hot_storage_max})")
        print(f"  This is the drift failure mode M29 prevents.")
        print(f"  They MUST be the same constant.")
        return 1
    
    print(f"\n✅ PASS: Single constant enforced ({stale_threshold} days)")
    print("=" * 70)
    return 0

if __name__ == "__main__":
    sys.exit(main())