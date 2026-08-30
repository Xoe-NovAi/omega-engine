#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-MEMORY-FIREWALL-AUDITOR-CLI-v1.0.0
# 🔱 CLI entry point for Memory Firewall Audit

import sys
from omega.audit.memory_firewall_auditor import MemoryFirewallAuditor
from omega.oracle.entity_registry import EntityRegistry


def main() -> int:
    auditor = MemoryFirewallAuditor()
    registry = EntityRegistry()
    entities = list(registry.active_iter())
    
    if not entities:
        print("No entities loaded in registry")
        return 0
    
    reports = auditor.audit_all_tiers(entities)
    summary = auditor.get_summary([r for tier in reports.values() for r in tier])
    
    print(f"Total entities: {summary['total_entities']}")
    print(f"Clean entities: {summary['clean_entities']}")
    print(f"Violated entities: {summary['violated_entities']}")
    print(f"Total violations: {summary['total_violations']}")
    print(f"  Errors: {summary['error_violations']}")
    print(f"  Warnings: {summary['warning_violations']}")
    print(f"Compliance rate: {summary['compliance_rate']:.1%}")
    
    if summary['violated_entities'] > 0:
        print()
        for tier, tier_reports in reports.items():
            for r in tier_reports:
                if not r.clean:
                    print(f"  {tier.upper()}/{r.entity_name}:")
                    for v in r.violations:
                        print(f"    {v.severity.upper()}: {v.location} (trace={v.trace_id})")
        return 1
    else:
        print()
        print("✅ Memory Firewall Audit PASSED — No WAD leakage detected")
        return 0


if __name__ == "__main__":
    sys.exit(main())