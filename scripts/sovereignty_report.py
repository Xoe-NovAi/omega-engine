#!/usr/bin/env python3
# 🔱 Omega Engine — Sovereignty Report Script (D203)
# ⬡ OMEGA ⬡ RESEARCHER ⬡ hy3-free ⬡ opencode ⬡ trc_research
#
# Prints a human-readable sovereignty report to stdout.
# Called by `make sovereignty`.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from omega.observability.sovereignty import get_sovereignty_ratio

CYAN = "\033[1;36m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_report():
    result = get_sovereignty_ratio()

    print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f" 🏛️  Sovereignty Report — Local/Cloud Inference Ratio")
    print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")

    total = result["total"]
    if total == 0:
        print(f"\n{YELLOW}No inference data found.{RESET}")
        print("Run some inferences first (e.g., 'omega talk \"hello\"')")
        print("Data is stored in data/observability/metrics.db")
        return

    local_count = result["local_count"]
    cloud_count = result["cloud_count"]
    ratio_local = result["ratio_local"] * 100
    ratio_cloud = result["ratio_cloud"] * 100

    # Color-code the ratio
    if ratio_local >= 80:
        ratio_color = GREEN
    elif ratio_local >= 50:
        ratio_color = YELLOW
    else:
        ratio_color = RED

    print(f"\n{BOLD}Total inferences:{RESET}      {total}")
    print(f"{BOLD}Local inferences:{RESET}      {local_count}  ({ratio_color}{ratio_local:.1f}%{RESET})")
    print(f"{BOLD}Cloud inferences:{RESET}      {cloud_count}  ({ratio_color}{ratio_cloud:.1f}%{RESET})")
    print(f"{BOLD}Period:{RESET}               {result['since'].replace('_', ' ')}")

    print(f"\n{BOLD}Provider Breakdown:{RESET}")
    print(f"  {'Provider':<25} {'Count':<8} {'Type':<10}")
    print(f"  {'─'*25} {'─'*8} {'─'*10}")
    for provider, info in sorted(
        result["provider_breakdown"].items(),
        key=lambda x: x[1]["count"],
        reverse=True,
    ):
        ptype = "🌩️  cloud" if info["is_cloud"] else "💻 local"
        print(f"  {provider:<25} {info['count']:<8} {ptype:<10}")

    print(f"\nGenerated: {result['generated_at']}")
    print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")

    # Target check
    if ratio_local >= 80:
        print(f"{GREEN}✅ SOVEREIGNTY TARGET MET (≥80% local){RESET}")
    else:
        print(f"{YELLOW}⚠️  BELOW SOVEREIGNTY TARGET (target: ≥80% local){RESET}")
        print(f"   See Mandate 7 (Local-First) — provider chain may need reconfiguration.")
        print(f"   Check config/providers.yaml fallback_chain ordering.")


if __name__ == "__main__":
    print_report()
