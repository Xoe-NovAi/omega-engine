#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Sovereign Mandate CI Gate Checks — T3-3.

Automates verification of mandates that can be checked via static analysis.
Run via: make mandate-gates  OR  python scripts/mandate_gates.py

Exit code: 0 = all pass, 1 = violations found.

Mandates checked (NEW in T3-3):
  M3  Iris Constant — Iris not assigned a Pillar slot
  M6  Podman Sovereignty — no :U flags in Quadlet/container files
  M7  Local-First — providers.yaml strategy must be local_first
  M10 Fleet Integrity — agent file count <= 14
  M11 Soul Integrity — proposed_lessons.yaml has content
  M12 Queue Integrity — atomic write patterns present (extends T10)
  M15 Sovereign Continuity — session_gnosis.md exists for active agents
  M16 Modularization — no hardcoded absolute paths in src/omega/
  M20 SomaticState — llmama-cpp-python ctypes visible (best-effort)

Already enforced in temple-grade (DO NOT DUPLICATE):
  M1  AnyIO (T5 in temple-grade)
  M2  Firewall (verify-firewall target)
  M8  Zero Telemetry (T6 in temple-grade + github-audit)
  M9  Error Integrity (bare except grep)
  M13 Temple-Grade (the target itself)
  M14 Heritage Vetting (heritage-vet target)
  M21 Gate Integrity (test_contract_m21.py)
  M22 Response Provenance (test_contract_m21.py + oracle.py wiring)
"""

import re
import sys
from pathlib import Path

# ── Colors ───────────────────────────────────────────────────────────────────
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

violations = 0


def check(name: str, condition: bool, detail: str = ""):
    global violations
    if condition:
        print(f"  {GREEN}✅ PASS{RESET} — {name}")
    else:
        violations += 1
        suffix = f" ({detail})" if detail else ""
        print(f"  {RED}❌ FAIL{RESET} — {name}{suffix}")


print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(f" 🛡️  Sovereign Mandate Gate Checks (T3-3)")
print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
print()

# ── M3: Iris Constant ────────────────────────────────────────────────────────
print(f"{YELLOW}[M3] Iris Constant — Iris not in Pillar slots{RESET}")
iris_in_pillar = False
wad_files = list(Path("config/wads").rglob("*.yaml"))
for f in wad_files:
    try:
        content = f.read_text()
    except Exception:
        continue
    if "iris" not in content.lower():
        continue
    # Check if iris appears on a line with a pillar slot assignment
    for line in content.split("\n"):
        line_lower = line.lower()
        if "iris" in line_lower and any(f"P{i}" in line for i in range(1, 11)):
            # Exclude comments
            if not line.strip().startswith("#"):
                iris_in_pillar = True
                print(f"    ⚠️  Found: {f}: {line.strip()[:80]}")
check("M3: Iris Constant", not iris_in_pillar)

# ── M6: Podman Sovereignty ───────────────────────────────────────────────────
print(f"{YELLOW}[M6] Podman Sovereignty — no :U flags in Quadlets{RESET}")
u_flag_files = []
for pattern in ["*.container", "*.volume", "*.network", "*.kube"]:
    for f in list(Path("config").rglob(pattern)) + list(Path("quadlet-test").rglob(pattern)):
        try:
            content = f.read_text()
        except Exception:
            continue
        for line_no, line in enumerate(content.split("\n"), 1):
            if ":U" in line and "UserNS" not in line and not line.strip().startswith("#"):
                u_flag_files.append(f"{f}:{line_no}")
check("M6: Podman Sovereignty", len(u_flag_files) == 0,
      f"{len(u_flag_files)} lines with :U flags")

# ── M7: Local-First ──────────────────────────────────────────────────────────
print(f"{YELLOW}[M7] Local-First — providers.yaml strategy must be local_first{RESET}")
providers_yaml = Path("config/providers.yaml")
if providers_yaml.exists():
    content = providers_yaml.read_text()
    # Check for strategy: local_first OR absence of strategy: cloud_first
    has_local_first = "local_first" in content
    has_cloud_first = "cloud_first" in content
    check("M7: Local-First strategy", has_local_first and not has_cloud_first,
          "cloud_first found" if has_cloud_first else "local_first not found")
else:
    check("M7: Local-First strategy", False, "providers.yaml not found")

# ── M10: Fleet Integrity ─────────────────────────────────────────────────────
print(f"{YELLOW}[M10] Fleet Integrity — agent file count <= 14{RESET}")
agents_dir = Path(".opencode/agents")
if agents_dir.exists():
    agent_files = list(agents_dir.glob("*.md"))
    agent_count = len(agent_files)
    agent_names = sorted([f.stem for f in agent_files])
    check("M10: Fleet Integrity", agent_count <= 14,
          f"{agent_count} agents (max 14): {', '.join(agent_names)}")
else:
    check("M10: Fleet Integrity", False, ".opencode/agents/ not found")

# ── M11: Soul Integrity ──────────────────────────────────────────────────────
print(f"{YELLOW}[M11] Soul Integrity — proposed_lessons.yaml has content{RESET}")
entities_dir = Path("data/entities")
if entities_dir.exists():
    entity_dirs = [d for d in entities_dir.iterdir() if d.is_dir()]
    entities_with_lessons = 0
    empty_entities = []
    for d in entity_dirs:
        lessons_file = d / "proposed_lessons.yaml"
        if lessons_file.exists():
            content = lessons_file.read_text()
            # Check if there are actual proposals (format: - id: proposal-...)
            if "proposals:" in content:
                lines = [l for l in content.split("\n")
                         if l.strip().startswith("- id:")]
                if len(lines) > 0:
                    entities_with_lessons += 1
                else:
                    empty_entities.append(d.name)
    check("M11: Soul Integrity", entities_with_lessons > 0,
          f"{entities_with_lessons}/{len(entity_dirs)} entities have L3 principles")
else:
    check("M11: Soul Integrity", False, "data/entities/ not found")

# ── M12: Queue Integrity (extends T10) ──────────────────────────────────────
print(f"{YELLOW}[M12] Queue Integrity — atomic write patterns{RESET}")
atomic_patterns = [
    r"\.tmp.*rename",
    r"atomic_write",
    r"atomic_writer",
    r"tempfile.*NamedTemporaryFile",
    r"os\.rename",
    r"anyio\.Path.*rename",
]
atomic_files = set()
core_files = list(Path("src/omega").rglob("*.py"))
for f in core_files:
    try:
        content = f.read_text()
    except Exception:
        continue
    for pat in atomic_patterns:
        if re.search(pat, content):
            atomic_files.add(str(f))
            break
check("M12: Queue Integrity", len(atomic_files) > 0,
      f"{len(atomic_files)} files with atomic patterns")

# ── M15: Sovereign Continuity ────────────────────────────────────────────────
print(f"{YELLOW}[M15] Sovereign Continuity — session_gnosis.md exists{RESET}")
if entities_dir.exists():
    entity_dirs = [d for d in entities_dir.iterdir() if d.is_dir()]
    agents_with_gnosis = 0
    for d in entity_dirs:
        workspace = d / "workspace"
        gnosis = workspace / "session_gnosis.md"
        if gnosis.exists() and gnosis.stat().st_size > 100:
            agents_with_gnosis += 1
    check("M15: Sovereign Continuity", agents_with_gnosis > 0,
          f"{agents_with_gnosis} entities have session_gnosis.md")
else:
    check("M15: Sovereign Continuity", False, "data/entities/ not found")

# ── M16: Modularization (hardcoded paths) ────────────────────────────────────
print(f"{YELLOW}[M16] Modularization — no hardcoded absolute paths in core{RESET}")
# Patterns that indicate hardcoded paths (excluding known exceptions)
path_patterns = [
    (r'"/home/[^"]*"', "home path"),
    (r'"/root/[^"]*"', "root path"),
    (r'"/tmp/[^"]*"', "tmp path"),
    (r'"/var/[^"]*"', "var path"),
]
hardcoded_violations = []
skip_files = {"constants.py", "cpu_optimizer.py", "cvar_table.py", "mandate_auditor.py"}
# These files legitimately use /tmp for temp files (not hardcoded config paths)
skip_paths = {"workers/", "library/", "audit/", "governance/"}
for f in core_files:
    if f.name in skip_files:
        continue
    rel_path = str(f.relative_to("src/omega"))
    if any(skip in rel_path for skip in skip_paths):
        continue
    try:
        content = f.read_text()
    except Exception:
        continue
    for line_no, line in enumerate(content.split("\n"), 1):
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith('"""'):
            continue
        for pat, desc in path_patterns:
            if re.search(pat, stripped):
                # Exclude test files and known exceptions
                if "test" not in str(f).lower():
                    hardcoded_violations.append(f"{f.relative_to('.')}:{line_no}")
                    break
check("M16: Modularization", len(hardcoded_violations) == 0,
      f"{len(hardcoded_violations)} hardcoded paths" if hardcoded_violations else "")

# ── M20: SomaticState — ctypes visibility ────────────────────────────────────
print(f"{YELLOW}[M20] SomaticState — llama-cpp-python ctypes visible (best-effort){RESET}")
try:
    import llama_cpp
    has_llama = hasattr(llama_cpp, "llama_copy_state_data") or hasattr(llama_cpp, "Llama")
    check("M20: SomaticState (llama-cpp-python)", has_llama,
          "llama_cpp not installed" if not has_llama else "")
except ImportError:
    # Not a hard failure — llama-cpp-python may not be installed in CI/test
    print(f"  {YELLOW}⚠️  WARN{RESET} — M20: SomaticState (llama_cpp not installed — best-effort check)")

# ── Summary ──────────────────────────────────────────────────────────────────
print()
if violations > 0:
    print(f"{RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f" ❌ {violations} mandate violation(s) detected")
    print(f"{RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    sys.exit(1)
else:
    print(f"{GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f" ✅ ALL MANDATE GATES PASSED")
    print(f"{GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    sys.exit(0)
