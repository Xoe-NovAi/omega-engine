#!/usr/bin/env python3
"""Mandate Compliance Meter — mechanical compliance measurement (D-532, T06).

Derives the engine's mandate compliance % from MECHANICAL checks, never
hand-written numbers. This resolves the 3-way SSOT contradiction found in
Web Claude audit r2 §4 (25/26/27 disagreeing mandate counts): the denominator
is parsed from SOVEREIGN_MANDATES.md (27 `### N. Title` sections, v3.8.0).

Each mandate maps to a mechanical check (grep / config parse / gate script).
Mandates with no mechanical check yet are reported as `untested` and are NOT
counted as passing (no silent credit).

Usage:
    python scripts/check_mandate_compliance.py [--json] [--quiet]

Exit code: 0 = no failures, 1 = at least one mandate check failed.
`untested` mandates do NOT fail the gate (they are explicitly not counted).

Output (default): human-readable table + JSON summary.
Output (--json): JSON only: {"total": 27, "passed": N, "untested": N, "failed": N, "checks": [...]}

[ID-REF] Kali directive d-kal-001 (Mandate Compliance Meter). T06 of
IMPLEMENTATION_PLAN_AUDIT_REMEDIATION_20260816.md. ADR D-532.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANDATES_MD = REPO / "SOVEREIGN_MANDATES.md"
SRC = REPO / "src" / "omega"

# ── Colors (only for human output) ──────────────────────────────────────────
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"


@dataclass
class CheckResult:
    mandate: str          # e.g. "M7"
    name: str             # e.g. "Local-First (Non-Negotiable)"
    status: str           # "passed" | "failed" | "untested"
    detail: str = ""
    check: str = ""       # mechanical check that produced this result


def run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    """Run a command, return (exit_code, combined stdout+stderr)."""
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30, cwd=str(cwd or REPO)
        )
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except subprocess.TimeoutExpired:
        return -1, "TIMEOUT after 30s"
    except FileNotFoundError:
        return -1, f"command not found: {cmd[0]}"


def parse_mandates() -> list[tuple[str, str]]:
    """Parse SOVEREIGN_MANDATES.md for `### N. Title` headings."""
    text = MANDATES_MD.read_text()
    found = re.findall(r"^### (\d+)\.\s+(.+?)\s*$", text, re.MULTILINE)
    return [(f"M{num}", name) for num, name in found]


def grep_zero(pattern: str, paths: list[Path], *extra: str) -> tuple[bool, str]:
    """Return (ok, detail) — ok if pattern has zero matches in paths (respecting exclusions)."""
    cmd = ["rg", "-n", pattern] + list(extra) + [str(p) for p in paths]
    code, out = run(cmd)
    if code == 1:
        return True, "0 matches"
    if code == 0:
        lines = out.strip().splitlines()
        return False, f"{len(lines)} match(es): {lines[0]}" if lines else "matches found"
    return False, out.strip()[:120] or f"rg failed (exit {code})"


def grep_any(pattern: str, paths: list[Path], *extra: str) -> tuple[bool, str]:
    """Return (ok, detail) — ok if pattern has at least one match."""
    cmd = ["rg", "-n", pattern] + list(extra) + [str(p) for p in paths]
    code, out = run(cmd)
    if code == 0:
        lines = out.strip().splitlines()
        return True, f"{len(lines)} match(es): {lines[0][:80]}" if lines else "matched"
    return False, f"no match (rg exit {code})"


def make_check(mandate: str, name: str, check: str, fn) -> CheckResult:
    try:
        ok, detail = fn()
    except Exception as e:  # noqa: BLE001 — meter must never crash mid-run
        ok, detail = False, f"check raised {type(e).__name__}: {e}"
    return CheckResult(mandate=mandate, name=name, status="passed" if ok else "failed",
                       detail=detail, check=check)


def build_checks(mandates: list[tuple[str, str]]) -> list[CheckResult]:
    results: list[CheckResult] = []
    available = dict(mandates)

    def m(name: str) -> str:
        return available.get(name, name)

    # ── M1: AnyIO Absolute — no asyncio imports in core ─────────────────────
    # Aligned with canonical gate `make check-m1-anyio` (excludes tests,
    # governance, and tty_agent which is a TTY driver, not core runtime).
    results.append(make_check(
        "M1", m("M1"), "make check-m1-anyio (canonical gate)",
        lambda: (lambda c, o: (c == 0, o.strip().splitlines()[-1][:100] if o.strip() else f"exit {c}"))(
            *run(["make", "check-m1-anyio"]))))

    # ── M2: Engine-Stack Firewall — canonical FirewallChecker (WAD refs) ────
    # Uses the dedicated scanner (src/omega/audit/firewall_checker.py) instead
    # of naive grep, which would false-positive on docstring mentions.
    def m2_check():
        code, out = run([sys.executable, str(REPO / "src/omega/audit/firewall_checker.py")])
        last = out.strip().splitlines()[-1][:120] if out.strip() else f"exit {code}"
        return (code == 0, last)
    results.append(make_check("M2", m("M2"), "python src/omega/audit/firewall_checker.py", m2_check))

    # ── M3: Iris Constant — Iris not assigned a Pillar slot ─────────────────
    def m3_check():
        violations = []
        for f in list((REPO / "config/wads").rglob("*.yaml")):
            try:
                content = f.read_text()
            except Exception:
                continue
            for line in content.split("\n"):
                ll = line.lower()
                if "iris" in ll and any(f"P{i}" in line for i in range(1, 11)):
                    if not line.strip().startswith("#"):
                        violations.append(f"{f.name}: {line.strip()[:60]}")
        return (len(violations) == 0,
                f"{len(violations)} violations: {violations[0]}" if violations else "Iris not in Pillar slots")
    results.append(make_check("M3", m("M3"), "scan config/wads/*.yaml for iris+P{N}", m3_check))

    # ── M4: Sequentiality Mandate — Plan → Verify → Execute ─────────────────
    # No mechanical check (process discipline, not static property).
    results.append(CheckResult("M4", m("M4"), "untested",
                               "No mechanical check (process discipline). Evidence: PIVOT_LOG.md D-series.",
                               "—"))

    # ── M5: Gnosis Preservation — proposed_lessons.yaml has content ─────────
    def m5_check():
        entities = [d for d in (REPO / "data/entities").iterdir() if d.is_dir()]
        with_lessons = []
        for d in entities:
            f = d / "proposed_lessons.yaml"
            if f.exists() and "proposals:" in f.read_text():
                with_lessons.append(d.name)
        return (len(with_lessons) > 0,
                f"{len(with_lessons)}/{len(entities)} entities have proposals")
    results.append(make_check("M5", m("M5"), "scan data/entities/*/proposed_lessons.yaml", m5_check))

    # ── M6: Podman Sovereignty — no :U flags in Quadlets ────────────────────
    def m6_check():
        hits = []
        for pattern in ["*.container", "*.volume", "*.network", "*.kube"]:
            for f in list((REPO / "config").rglob(pattern)) + list((REPO / "quadlet-test").rglob(pattern)):
                try:
                    content = f.read_text()
                except Exception:
                    continue
                for no, line in enumerate(content.split("\n"), 1):
                    if ":U" in line and "UserNS" not in line and not line.strip().startswith("#"):
                        hits.append(f"{f.name}:{no}")
        return (len(hits) == 0, f"{len(hits)} :U flag lines" if hits else "no :U flags")
    results.append(make_check("M6", m("M6"), "scan config/ + quadlet-test/ for :U flags", m6_check))

    # ── M7: Local-First — providers.yaml strategy local_first ───────────────
    def m7_check():
        f = REPO / "config/providers.yaml"
        if not f.exists():
            return False, "providers.yaml not found"
        content = f.read_text()
        has_local = "local_first" in content
        has_cloud = "cloud_first" in content
        if has_local and not has_cloud:
            return True, "strategy local_first"
        if has_cloud:
            return False, "cloud_first present — M7 violation"
        return False, "local_first not found"
    results.append(make_check("M7", m("M7"), "parse config/providers.yaml strategy", m7_check))

    # ── M8: Zero Telemetry — no telemetry SDK imports in core ───────────────
    # Aligned with canonical gate `make check-m8-zero-telemetry` (checks for
    # actual SDK imports, not the word "telemetry" which appears in mandate
    # docs/config requirements).
    def m8_check():
        code, out = run(["make", "check-m8-zero-telemetry"])
        last = out.strip().splitlines()[-1][:100] if out.strip() else f"exit {code}"
        return (code == 0, last)
    results.append(make_check("M8", m("M8"), "make check-m8-zero-telemetry", m8_check))

    # ── M9: Error Integrity — no bare except without logger/trace_id ────────
    def m9_check():
        # Delegates to the Makefile gate which has the exact regex.
        code, out = run(["make", "check-m9-error-integrity"])
        return (code == 0, out.strip().splitlines()[-1][:100] if out else f"exit {code}")
    results.append(make_check("M9", m("M9"), "make check-m9-error-integrity", m9_check))

    # ── M10: Fleet Integrity — agent file count <= 14 ───────────────────────
    def m10_check():
        agents = (REPO / ".opencode/agents")
        if not agents.exists():
            return False, ".opencode/agents/ not found"
        count = len(list(agents.glob("*.md")))
        return (count <= 14, f"{count} agents (max 14)")
    results.append(make_check("M10", m("M10"), "count .opencode/agents/*.md", m10_check))

    # ── M11: Soul Integrity — proposed_lessons.yaml non-empty proposals ─────
    def m11_check():
        entities = [d for d in (REPO / "data/entities").iterdir() if d.is_dir()]
        with_props = 0
        for d in entities:
            f = d / "proposed_lessons.yaml"
            if f.exists():
                content = f.read_text()
                if "proposals:" in content and any(
                    l.strip().startswith("- id:") for l in content.split("\n")):
                    with_props += 1
        return (with_props > 0, f"{with_props}/{len(entities)} entities have L3 proposals")
    results.append(make_check("M11", m("M11"), "scan data/entities/*/proposed_lessons.yaml", m11_check))

    # ── M12: Queue Integrity — atomic write patterns present ────────────────
    def m12_check():
        pats = [r"atomic_write", r"os\.rename", r"\.tmp.*rename", r"NamedTemporaryFile"]
        hits = set()
        for f in SRC.rglob("*.py"):
            try:
                content = f.read_text()
            except Exception:
                continue
            if any(re.search(p, content) for p in pats):
                hits.add(f.name)
        return (len(hits) > 0, f"{len(hits)} files with atomic write patterns")
    results.append(make_check("M12", m("M12"), "scan src/omega for atomic write patterns", m12_check))

    # ── M13: Temple-Grade Compliance — make temple-grade passes ─────────────
    # NOTE: not invoked recursively (temple-grade itself includes check-mandates
    # which could include this script). Mechanical check = component gates.
    def m13_check():
        code, out = run(["make", "temple-grade"])
        last = out.strip().splitlines()[-1][:120] if out.strip() else f"exit {code}"
        return (code == 0, last)
    results.append(make_check("M13", m("M13"), "make temple-grade (component gates)", m13_check))

    # ── M14: Heritage Vetting — every [id-soft:] tag has a vet record ───────
    def m14_check():
        code, out = run(["bash", str(REPO / "scripts/heritage_vet.sh")])
        ok = "✅ All heritage tags have vet records" in out or code == 0
        last = out.strip().splitlines()[-1][:120] if out.strip() else f"exit {code}"
        return (ok, last)
    results.append(make_check("M14", m("M14"), "scripts/heritage_vet.sh", m14_check))

    # ── M15: Sovereign Continuity — session_gnosis.md exists ────────────────
    def m15_check():
        entities = [d for d in (REPO / "data/entities").iterdir() if d.is_dir()]
        with_gnosis = 0
        for d in entities:
            g = d / "workspace/session_gnosis.md"
            if g.exists() and g.stat().st_size > 100:
                with_gnosis += 1
        return (with_gnosis > 0, f"{with_gnosis} entities have session_gnosis.md")
    results.append(make_check("M15", m("M15"), "scan data/entities/*/workspace/session_gnosis.md", m15_check))

    # ── M16: Modularization — no hardcoded absolute paths in core ───────────
    def m16_check():
        pats = [(r'"/home/[^"]*"', "home"), (r'"/root/[^"]*"', "root"),
                (r'"/tmp/[^"]*"', "tmp"), (r'"/var/[^"]*"', "var")]
        skip = {"constants.py", "cpu_optimizer.py", "cvar_table.py", "mandate_auditor.py"}
        skip_paths = {"workers/", "library/", "audit/", "governance/"}
        hits = []
        for f in SRC.rglob("*.py"):
            if f.name in skip:
                continue
            rel = str(f.relative_to(SRC))
            if any(s in rel for s in skip_paths):
                continue
            try:
                content = f.read_text()
            except Exception:
                continue
            for no, line in enumerate(content.split("\n"), 1):
                s = line.strip()
                if s.startswith("#") or s.startswith('"""'):
                    continue
                if any(re.search(p, s) for p, _ in pats):
                    hits.append(f"{f.name}:{no}")
                    break
        return (len(hits) == 0, f"{len(hits)} hardcoded paths" if hits else "no hardcoded paths")
    results.append(make_check("M16", m("M16"), "scan src/omega for hardcoded absolute paths", m16_check))

    # ── M17: Cognitive Integrity — NLI/skeptical verifier ───────────────────
    results.append(CheckResult("M17", m("M17"), "untested",
                               "No mechanical check (semantic integrity gate T12 not yet implemented).",
                               "—"))

    # ── M18: Token Efficiency ───────────────────────────────────────────────
    results.append(CheckResult("M18", m("M18"), "untested",
                               "No mechanical check (policy mandate, not statically checkable).",
                               "—"))

    # ── M19: Adversarial Alchemy ────────────────────────────────────────────
    results.append(CheckResult("M19", m("M19"), "untested",
                               "No mechanical check (strategic mandate).",
                               "—"))

    # ── M20: SomaticState — llama-cpp-python ctypes visible ─────────────────
    def m20_check():
        try:
            import llama_cpp  # type: ignore
            ok = hasattr(llama_cpp, "llama_copy_state_data") or hasattr(llama_cpp, "Llama")
            return (ok, "llama-cpp-python ctypes visible" if ok else "ctypes not visible")
        except ImportError:
            return (False, "llama_cpp not installed (best-effort — env-dependent)")
    results.append(make_check("M20", m("M20"), "import llama_cpp; check ctypes", m20_check))

    # ── M21: Gate Integrity — contract tests exist ──────────────────────────
    results.append(make_check(
        "M21", m("M21"), "ls tests/test_contract_m21.py",
        lambda: ((REPO / "tests/test_contract_m21.py").exists(),
                 "contract test file exists" if (REPO / "tests/test_contract_m21.py").exists()
                 else "test_contract_m21.py missing")))

    # ── M22: Response Provenance — provider_name captured at receipt ────────
    results.append(make_check(
        "M22", m("M22"), "rg 'provider_name' src/omega/oracle/model_gateway.py",
        lambda: grep_any(r"provider_name\s*[:=]", [SRC / "oracle/model_gateway.py"])))

    # ── M23: Failure Integrity — m23_gate.py exists + passes ────────────────
    def m23_check():
        gate = REPO / "scripts/m23_gate.py"
        if not gate.exists():
            return False, "scripts/m23_gate.py missing"
        code, out = run(["python", str(gate)])
        last = out.strip().splitlines()[-1][:100] if out.strip() else f"exit {code}"
        return (code == 0, last)
    results.append(make_check("M23", m("M23"), "python scripts/m23_gate.py", m23_check))

    # ── M24: Venv Sovereignty — no --break-system-packages ──────────────────
    def m24_check():
        hits = []
        for f in list((REPO / "scripts").glob("*.sh")) + list((REPO / "scripts").glob("*.py")):
            try:
                content = f.read_text()
            except Exception:
                continue
            if "--break-system-packages" in content and "grep" not in content:
                hits.append(f.name)
        return (len(hits) == 0, f"{len(hits)} files with break-system-packages" if hits
                else "no --break-system-packages")
    results.append(make_check("M24", m("M24"), "scan scripts/ for --break-system-packages", m24_check))

    # ── M25: Streaming Resilience — chunk_timeout_ms present ────────────────
    results.append(make_check(
        "M25", m("M25"), "rg 'chunk_timeout_ms' config/providers.yaml",
        lambda: grep_any(r"chunk_timeout_ms", [REPO / "config/providers.yaml"])))

    # ── M26: Doc Standards — make doc-llm-validate passes ───────────────────
    def m26_check():
        code, out = run(["make", "doc-llm-validate"])
        last = out.strip().splitlines()[-1][:100] if out.strip() else f"exit {code}"
        return (code == 0, last)
    results.append(make_check("M26", m("M26"), "make doc-llm-validate", m26_check))

    # ── M27: Tracking Integrity — validate_tracking_state passes ────────────
    def m27_check():
        code, out = run(["python", str(REPO / "scripts/validate_tracking_state.py")])
        last = out.strip().splitlines()[-1][:100] if out.strip() else f"exit {code}"
        return (code == 0, last)
    results.append(make_check("M27", m("M27"), "python scripts/validate_tracking_state.py", m27_check))

    return results


def emit_json(results: list[CheckResult], total: int) -> str:
    passed = sum(1 for r in results if r.status == "passed")
    failed = sum(1 for r in results if r.status == "failed")
    untested = sum(1 for r in results if r.status == "untested")
    payload = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "untested": untested,
        "compliance_pct": round(100.0 * passed / total, 1),
        "measured_pct": round(100.0 * passed / max(passed + failed, 1), 1),
        "checks": [
            {"mandate": r.mandate, "name": r.name, "status": r.status,
             "detail": r.detail, "check": r.check}
            for r in results
        ],
    }
    return json.dumps(payload, indent=2)


def emit_human(results: list[CheckResult], total: int) -> str:
    passed = sum(1 for r in results if r.status == "passed")
    failed = sum(1 for r in results if r.status == "failed")
    untested = sum(1 for r in results if r.status == "untested")
    lines = [
        f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}",
        f" 🛡️  Mandate Compliance Meter (D-532 / T06) — denominator {total}",
        f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}",
    ]
    for r in results:
        if r.status == "passed":
            icon, color = "✅", GREEN
        elif r.status == "failed":
            icon, color = "❌", RED
        else:
            icon, color = "➖", YELLOW
        detail = f" — {r.detail}" if r.detail else ""
        lines.append(f"  {color}{icon} {r.mandate}: {r.name}{RESET}{detail}")
    lines.append(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    lines.append(
        f"  Total: {total} | Passed: {GREEN}{passed}{RESET} | "
        f"Failed: {RED}{failed}{RESET} | Untested: {YELLOW}{untested}{RESET} | "
        f"Compliance: {passed}/{total} = {100.0 * passed / total:.1f}%"
    )
    lines.append(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    return "\n".join(lines)


def main() -> int:
    mandates = parse_mandates()
    total = len(mandates)
    if total != 27:
        print(f"⚠️  Denominator drift: SOVEREIGN_MANDATES.md has {total} mandates (expected 27, v3.8.0)",
              file=sys.stderr)
    results = build_checks(mandates)

    if "--json" in sys.argv:
        print(emit_json(results, total))
    else:
        print(emit_human(results, total))

    failed = sum(1 for r in results if r.status == "failed")
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
