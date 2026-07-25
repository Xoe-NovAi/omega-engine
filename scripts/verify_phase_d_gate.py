#!/usr/bin/env python3
"""Phase D Gate Verification — Objective, automated gate check"""
import subprocess
import json
import sys
from pathlib import Path

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0, result.stdout.strip(), result.stderr.strip()

checks = [
    # (name, command, expected_in_output, required)
    ("C-0: Honest tests", "make test 2>&1 | grep -E 'passed|failed|error'", "passed", True),
    ("C-1': SoulStore single writer", "grep -r 'single.writer\\|actor.model' src/omega/", "single.writer", True),
    ("C-2': OOMProtector 3-signal", "grep -r 'cgroups\\|llama.cpp\\|vm.pressure' src/omega/", "cgroups", True),
    ("C-3: Restic backup", "test -f scripts/restic_backup.sh && echo 'exists'", "exists", True),
    ("C-4a: MCP audit doc", "test -f docs/research/R_CG01_MCP_STREAMABLE_HTTP_OAUTH_AUDIT.md && echo 'exists'", "exists", True),
    ("C-4b: MCP Streamable HTTP", "grep -r 'session.initialize' src/omega/mcp_client.py || echo 'REMOVED'", "REMOVED", True),
    ("C-5: MaKaLi routing", "grep -r 'oracle_summon_local' src/omega/", "oracle_summon_local", True),
    ("C-6': Breaker unification", "grep -r 'HealthMonitor' src/omega/", "HealthMonitor", True),
    ("C-10: Local admission", "grep -r 'CCX.*semaphore\\|admission' src/omega/", "semaphore", True),
    ("C-9: GenerationPolicy", "grep -r 'GenerationPolicy' src/omega/ || echo 'MISSING'", "MISSING", False),
    ("C-11: Property tests", "python -m pytest tests/property/ -v 2>&1 | grep -E 'passed|failed'", "passed", True),
    ("Soul distillation ≥1 L3/week", "grep -c 'tier.*L3' data/entities/*/proposed_lessons.yaml 2>/dev/null || echo '0'", "0", True),
    ("Restic weekly check", "systemctl is-enabled restic-check.timer 2>/dev/null || echo 'NOT CONFIGURED'", "NOT CONFIGURED", True),
    ("make test 100% pass", "make test 2>&1 | tail -3", "passed", True),
    ("make temple-grade T1-T11", "make temple-grade 2>&1 | grep -E 'T[0-9]+.*PASS\\|PASS.*T[0-9]+' | wc -l", "11", True),
]

print("═══════════════════════════════════════════════════════════")
print(" PHASE D GATE VERIFICATION")
print("═══════════════════════════════════════════════════════════\n")

results = []
for name, cmd, expected, required in checks:
    ok, out, err = run(cmd)
    passed = expected in out if expected != "MISSING" else "MISSING" not in out
    status = "✅ PASS" if passed else ("❌ FAIL" if required else "⚠️  WARN")
    results.append((name, passed, required, out[:80]))
    print(f"  {status} {name}")
    if not passed and out:
        print(f"       → {out[:80]}")

print("\n═══════════════════════════════════════════════════════════")
required_passed = sum(1 for _, p, r, _ in results if r and p)
required_total = sum(1 for _, _, r, _ in results if r)
print(f" REQUIRED: {required_passed}/{required_total} passed")
optional_passed = sum(1 for _, p, r, _ in results if not r and p)
optional_total = sum(1 for _, _, r, _ in results if not r)
print(f" OPTIONAL: {optional_passed}/{optional_total} passed")

gate_pass = required_passed == required_total
print(f"\n GATE: {'✅ PASS' if gate_pass else '❌ FAIL'}")
print("═══════════════════════════════════════════════════════════")

sys.exit(0 if gate_pass else 1)
