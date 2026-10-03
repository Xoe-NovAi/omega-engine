#!/usr/bin/env python3
"""M7 Sovereignty Gate — verifies sovereignty_policy + entity->tier mapping.

Spec: docs/architecture/SOVEREIGNTY_INVARIANT_SPEC.md
Ratified: 2026-09-16 — Synergy Model (Sovereignty is Policy Enforcement).
"""

import sys

import yaml


def main() -> int:
    try:
        with open("config/providers.yaml") as f:
            d = yaml.safe_load(f)
    except FileNotFoundError:
        print("FAIL: config/providers.yaml not found")
        return 1

    # sovereignty_policy must exist with valid mode + tiers
    sp = d.get("sovereignty_policy")
    if sp is None:
        print("FAIL: sovereignty_policy missing")
        return 1
    mode = sp.get("mode")
    if mode not in ("synergy", "local_first", "cloud_first"):
        print(f"FAIL: sovereignty_policy.mode invalid: {mode!r}")
        return 1
    tiers = sp.get("tiers")
    if not tiers:
        print("FAIL: sovereignty_policy.tiers missing")
        return 1

    # maakali_routing must exist and every entity must map to a valid tier
    routing = d.get("maakali_routing")
    if routing is None:
        print("FAIL: maakali_routing missing")
        return 1
    for ent, cfg in routing.items():
        tier = cfg.get("tier")
        if tier is None:
            print(f"FAIL: {ent} missing tier")
            return 1
        if tier not in tiers:
            print(f"FAIL: {ent} tier {tier!r} not in sovereignty_policy.tiers")
            return 1
        if "fallback_tier" not in cfg:
            print(f"FAIL: {ent} missing fallback_tier")
            return 1

    print(f"PASS: sovereignty_policy.mode={mode}, {len(tiers)} tiers, {len(routing)} entities mapped")
    return 0


if __name__ == "__main__":
    sys.exit(main())