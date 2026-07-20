#!/usr/bin/env python3
# 🔱 MandateAuditor — M1-M23 Compliance Verification
# ⬡ OMEGA ⬡ PILLAR-P10 ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_mandate_auditor ⬡ ACTIVE
# AP: AP-MANDATE-AUDITOR-v1.0.0
"""Sovereign Mandate Auditor — Core Engine Module.

This module provides programmatic access to Sovereign Mandate verification.
Used by:
- `make mandate-audit` CLI target
- `make temple-grade` (T13 gate)
- Contract tests in tests/contracts/test_mandate_auditor.py

Mandates checked (subset enforceable via static analysis):
- M3: Iris Constant — Iris not assigned a Pillar slot
- M6: Podman Sovereignty — No :U flags in Quadlet/container files
- M7: Local-First — providers.yaml strategy must be local_first
- M10: Fleet Integrity — Agent file count <= 14
- M11: Soul Integrity — proposed_lessons.yaml has content
- M12: Queue Integrity — Atomic write patterns present
- M15: Sovereign Continuity — session_gnosis.md exists for active agents
- M16: Modularization — No hardcoded absolute paths in src/omega/
- M20: SomaticState — llama-cpp-python ctypes visible (best-effort)

Mandates enforced elsewhere (do not duplicate):
- M1: AnyIO (T5 in temple-grade)
- M2: Firewall (verify-firewall target)
- M8: Zero Telemetry (T6 in temple-grade + github-audit)
- M9: Error Integrity (bare except grep in temple-grade)
- M13: Temple-Grade (the target itself)
- M14: Heritage Vetting (heritage-vet target)
- M21: Gate Integrity (test_contract_m21.py)
- M22: Response Provenance (test_contract_m21.py + oracle.py wiring)
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class MandateResult:
    """Result of a single mandate check."""
    mandate_id: str
    name: str
    passed: bool
    detail: str = ""
    severity: str = "error"  # "error" | "warning" | "info"


@dataclass(frozen=True)
class AuditReport:
    """Complete audit report for all checked mandates."""
    results: tuple[MandateResult, ...]
    passed: int
    failed: int
    warnings: int

    @property
    def all_passed(self) -> bool:
        return self.failed == 0


class MandateAuditor:
    """Audits the codebase for Sovereign Mandate compliance."""

    def __init__(self, root: Path | str = "."):
        self.root = Path(root).resolve()
        self.results: list[MandateResult] = []

    def _check(self, mandate_id: str, name: str, condition: bool, detail: str = "", severity: str = "error") -> None:
        """Record a mandate check result."""
        self.results.append(MandateResult(
            mandate_id=mandate_id,
            name=name,
            passed=condition,
            detail=detail,
            severity=severity
        ))

    def check_m3_iris_constant(self) -> None:
        """M3: MESSENGER_BRIDGE Constant — MESSENGER_BRIDGE not assigned a Pillar slot (P1-P10)."""
        from omega.governance.config_resolver import WADS_DIR
        from omega.ics import ROLE_CONSTANTS
        import yaml
        
        iris_in_pillar = False
        violations: list[str] = []

        # M2 Firewall: Load entity definitions from WAD config (no hardcoded entity names)
        # Use auditor's root to find WAD config (supports test temp dirs)
        try:
            # Try to find dispatch.yaml in the auditor's root
            wad_dir = self.root / "config" / "wads"
            if wad_dir.exists():
                # Look for any IWAD with entities/dispatch.yaml
                for iwad_dir in wad_dir.iterdir():
                    if iwad_dir.is_dir():
                        dispatch_path = iwad_dir / "entities" / "dispatch.yaml"
                        if dispatch_path.exists():
                            config = yaml.safe_load(dispatch_path.read_text(encoding="utf-8")) or {}
                            entities = config.get("entities", [])
                            break
                else:
                    entities = []
            else:
                entities = []
        except Exception:
            # Fallback to original scan if WAD config unavailable
            wad_glob = str(Path("config") / "wads" / "**" / "*.yaml")
            wad_files = list(self.root.glob(wad_glob))
            for f in wad_files:
                try:
                    content = f.read_text()
                except Exception:
                    continue
                # Search for MESSENGER_BRIDGE role entity in Pillar slots
                # Use case-insensitive search for the role name
                if "messenger_bridge" not in content.lower():
                    continue
                for line_no, line in enumerate(content.split("\n"), 1):
                    line_lower = line.lower()
                    if "messenger_bridge" in line_lower and any(f"P{i}" in line for i in range(1, 11)):
                        if not line.strip().startswith("#"):
                            iris_in_pillar = True
                            violations.append(f"{f.relative_to(self.root)}:{line_no}: {line.strip()[:80]}")
            self._check(
                "M3",
                "MESSENGER_BRIDGE Constant — MESSENGER_BRIDGE not in Pillar slots",
                not iris_in_pillar,
                f"{len(violations)} violations" if violations else ""
            )
            return

        # Check WAD entities for Iris in Pillar slots
        for ent in entities:
            role = ent.get("role")
            if role == ROLE_CONSTANTS["MESSENGER_BRIDGE"]:
                # This is the Iris entity - check if it has a Pillar slot
                pillar_slot = ent.get("pillar_slot")
                if pillar_slot is not None and str(pillar_slot).startswith("P"):
                    iris_in_pillar = True
                    violations.append(f"WAD entity '{ent.get('name')}' has Pillar slot: {pillar_slot}")

        self._check(
            "M3",
            "MESSENGER_BRIDGE Constant — MESSENGER_BRIDGE not in Pillar slots",
            not iris_in_pillar,
            f"{len(violations)} violations" if violations else ""
        )

    def check_m6_podman_sovereignty(self) -> None:
        """M6: Podman Sovereignty — No :U flags in Quadlet/container files."""
        u_flag_violations: list[str] = []

        patterns = ["*.container", "*.volume", "*.network", "*.kube"]
        search_dirs = [
            self.root / "config",
            self.root / "quadlet-test",
        ]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            for pattern in patterns:
                for f in search_dir.rglob(pattern):
                    try:
                        content = f.read_text()
                    except Exception:
                        continue
                    for line_no, line in enumerate(content.split("\n"), 1):
                        if ":U" in line and "UserNS" not in line and not line.strip().startswith("#"):
                            u_flag_violations.append(f"{f.relative_to(self.root)}:{line_no}")

        self._check(
            "M6",
            "Podman Sovereignty — no :U flags in Quadlets",
            len(u_flag_violations) == 0,
            f"{len(u_flag_violations)} lines with :U flags" if u_flag_violations else ""
        )

    def check_m7_local_first(self) -> None:
        """M7: Local-First — providers.yaml strategy must be local_first."""
        providers_yaml = self.root / "config" / "providers.yaml"
        if not providers_yaml.exists():
            self._check("M7", "Local-First strategy", False, "providers.yaml not found")
            return

        content = providers_yaml.read_text()
        has_local_first = "local_first" in content
        has_cloud_first = "cloud_first" in content

        self._check(
            "M7",
            "Local-First — providers.yaml strategy is local_first",
            has_local_first and not has_cloud_first,
            "cloud_first found" if has_cloud_first else "local_first not found"
        )

    def check_m10_fleet_integrity(self) -> None:
        """M10: Fleet Integrity — Agent file count <= 14."""
        agents_dir = self.root / ".opencode" / "agents"
        if not agents_dir.exists():
            self._check("M10", "Fleet Integrity — agent count <= 14", False, ".opencode/agents/ not found")
            return

        agent_files = list(agents_dir.glob("*.md"))
        agent_count = len(agent_files)
        agent_names = sorted([f.stem for f in agent_files])

        self._check(
            "M10",
            "Fleet Integrity — agent count <= 14",
            agent_count <= 14,
            f"{agent_count} agents (max 14): {', '.join(agent_names)}"
        )

    def check_m11_soul_integrity(self) -> None:
        """M11: Soul Integrity — proposed_lessons.yaml has content."""
        entities_dir = self.root / "data" / "entities"
        if not entities_dir.exists():
            self._check("M11", "Soul Integrity — proposed_lessons.yaml has content", False, "data/entities/ not found")
            return

        entity_dirs = [d for d in entities_dir.iterdir() if d.is_dir()]
        entities_with_lessons = 0
        empty_entities: list[str] = []

        for d in entity_dirs:
            lessons_file = d / "proposed_lessons.yaml"
            if lessons_file.exists():
                content = lessons_file.read_text()
                if "proposals:" in content:
                    lines = [l for l in content.split("\n") if l.strip().startswith("- id:")]
                    if len(lines) > 0:
                        entities_with_lessons += 1
                    else:
                        empty_entities.append(d.name)

        self._check(
            "M11",
            "Soul Integrity — proposed_lessons.yaml has L3 principles",
            entities_with_lessons > 0,
            f"{entities_with_lessons}/{len(entity_dirs)} entities have L3 principles"
        )

    def check_m12_queue_integrity(self) -> None:
        """M12: Queue Integrity — Atomic write patterns present in core."""
        atomic_patterns = [
            r"\.tmp.*rename",
            r"atomic_write",
            r"atomic_writer",
            r"tempfile.*NamedTemporaryFile",
            r"os\.rename",
            r"anyio\.Path.*rename",
        ]

        atomic_files = set()
        core_files = list((self.root / "src" / "omega").rglob("*.py"))

        for f in core_files:
            try:
                content = f.read_text()
            except Exception:
                continue
            for pat in atomic_patterns:
                if re.search(pat, content):
                    atomic_files.add(str(f.relative_to(self.root)))
                    break

        self._check(
            "M12",
            "Queue Integrity — atomic write patterns in core",
            len(atomic_files) > 0,
            f"{len(atomic_files)} files with atomic patterns"
        )

    def check_m15_sovereign_continuity(self) -> None:
        """M15: Sovereign Continuity — session_gnosis.md exists for active agents."""
        entities_dir = self.root / "data" / "entities"
        if not entities_dir.exists():
            self._check("M15", "Sovereign Continuity — session_gnosis.md exists", False, "data/entities/ not found")
            return

        entity_dirs = [d for d in entities_dir.iterdir() if d.is_dir()]
        agents_with_gnosis = 0

        for d in entity_dirs:
            workspace = d / "workspace"
            gnosis = workspace / "session_gnosis.md"
            if gnosis.exists() and gnosis.stat().st_size > 100:
                agents_with_gnosis += 1

        self._check(
            "M15",
            "Sovereign Continuity — session_gnosis.md exists",
            agents_with_gnosis > 0,
            f"{agents_with_gnosis} entities have session_gnosis.md"
        )

    def check_m16_modularization(self) -> None:
        """M16: Modularization — No hardcoded absolute paths in src/omega/."""
        path_patterns = [
            (r'"/home/[^"]*"', "home path"),
            (r'"/root/[^"]*"', "root path"),
            (r'"/tmp/[^"]*"', "tmp path"),
            (r'"/var/[^"]*"', "var path"),
        ]

        skip_files = {"constants.py", "cpu_optimizer.py", "cvar_table.py", "mandate_auditor.py"}
        skip_paths = {"workers/", "library/", "audit/", "governance/"}

        hardcoded_violations: list[str] = []
        core_files = list((self.root / "src" / "omega").rglob("*.py"))

        for f in core_files:
            if f.name in skip_files:
                continue
            rel_path = str(f.relative_to(self.root / "src" / "omega"))
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
                        if "test" not in str(f).lower():
                            hardcoded_violations.append(f"{f.relative_to(self.root)}:{line_no}")
                        break

        self._check(
            "M16",
            "Modularization — no hardcoded absolute paths in core",
            len(hardcoded_violations) == 0,
            f"{len(hardcoded_violations)} hardcoded paths" if hardcoded_violations else ""
        )

    def check_m20_somatic_state(self) -> None:
        """M20: SomaticState — llama-cpp-python ctypes visible (best-effort)."""
        try:
            import llama_cpp
            has_llama = hasattr(llama_cpp, "llama_copy_state_data") or hasattr(llama_cpp, "Llama")
            self._check(
                "M20",
                "SomaticState — llama-cpp-python ctypes visible",
                has_llama,
                "llama_cpp not installed" if not has_llama else "",
                severity="warning"  # Best-effort, not a hard failure
            )
        except ImportError:
            # Not a hard failure — llama-cpp-python may not be installed in CI/test
            self._check(
                "M20",
                "SomaticState — llama-cpp-python ctypes visible",
                True,  # Pass with warning
                "llama_cpp not installed — best-effort check",
                severity="warning"
            )

    def run_all(self) -> AuditReport:
        """Execute all checks, return aggregate report."""
        self.results.clear()

        # Run all mandate checks
        self.check_m3_iris_constant()
        self.check_m6_podman_sovereignty()
        self.check_m7_local_first()
        self.check_m10_fleet_integrity()
        self.check_m11_soul_integrity()
        self.check_m12_queue_integrity()
        self.check_m15_sovereign_continuity()
        self.check_m16_modularization()
        self.check_m20_somatic_state()

        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed and r.severity == "error")
        warnings = sum(1 for r in self.results if not r.passed and r.severity == "warning")

        return AuditReport(
            results=tuple(self.results),
            passed=passed,
            failed=failed,
            warnings=warnings
        )

    def print_report(self, report: AuditReport) -> None:
        """Print formatted audit report to stdout."""
        GREEN = "\033[92m"
        RED = "\033[91m"
        YELLOW = "\033[93m"
        CYAN = "\033[96m"
        RESET = "\033[0m"

        print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f" 🛡️  Sovereign Mandate Audit Report")
        print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        print()

        for result in report.results:
            if result.passed:
                print(f"  {GREEN}✅ PASS{RESET} — [{result.mandate_id}] {result.name}")
            else:
                if result.severity == "warning":
                    print(f"  {YELLOW}⚠️  WARN{RESET} — [{result.mandate_id}] {result.name}")
                else:
                    print(f"  {RED}❌ FAIL{RESET} — [{result.mandate_id}] {result.name}")
                if result.detail:
                    print(f"       {result.detail}")

        print()
        if report.failed > 0:
            print(f"{RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f" ❌ {report.failed} mandate violation(s) detected")
            print(f"{RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        elif report.warnings > 0:
            print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f" ⚠️  {report.warnings} warning(s), {report.passed} passed")
            print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        else:
            print(f"{GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f" ✅ ALL MANDATE GATES PASSED ({report.passed} checks)")
            print(f"{GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")


def main() -> int:
    """CLI entry point for `make mandate-audit`."""
    auditor = MandateAuditor(".")
    report = auditor.run_all()
    auditor.print_report(report)
    return 0 if report.all_passed else 1


if __name__ == "__main__":
    sys.exit(main())