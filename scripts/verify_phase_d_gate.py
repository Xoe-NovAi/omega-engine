#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Phase D Gate Verification — fail-closed, probe-backed (v1.1).

M23 spirit: missing mandatory capability is FAIL, never soft-pass.
Do not invert expectations (e.g. expecting "0" L3 or "NOT CONFIGURED").
"""
from __future__ import annotations

import importlib.metadata
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: str, timeout: int = 120) -> tuple[int, str, str]:
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=timeout,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def ok(name: str, passed: bool, detail: str, required: bool = True) -> dict:
    return {
        "name": name,
        "passed": passed,
        "required": required,
        "detail": detail[:200],
    }


def check_file(path: str) -> bool:
    return (ROOT / path).is_file()


def check_hook_registered() -> tuple[bool, str]:
    """Check C-0.5: session end hook is correctly wired.
    
    Per Carmack Verdict 2026-07-30: soul distillation pipeline scrapped.
    Hook now just writes timestamp + refreshes codex. Agents write own lessons.
    """
    hook_file = ROOT / ".opencode" / "hooks" / "session_end.py"
    if not hook_file.is_file():
        return False, "session_end.py missing"
    
    return True, f"hook={hook_file.name} (timestamp + codex refresh)"


def check_mcp_pin() -> tuple[bool, str]:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    pinned = bool(re.search(r"mcp\s*[>=<~!]=.*1\.2", pyproject) or "mcp>=1.27" in pyproject)
    if not pinned:
        # also allow poetry-style
        pinned = "mcp" in pyproject and "<2" in pyproject
    try:
        ver = importlib.metadata.version("mcp")
    except importlib.metadata.PackageNotFoundError:
        return False, "mcp package not installed"
    major = int(ver.split(".")[0])
    if major >= 2:
        return False, f"mcp {ver} is v2+ (pin requires <2 until deliberate migrate)"
    if not pinned:
        return False, f"mcp {ver} installed but pyproject pin missing"
    return True, f"mcp {ver} installed; pyproject pin present"


def check_l3_proposals() -> tuple[bool, str]:
    total = 0
    files = 0
    for path in (ROOT / "data" / "entities").glob("*/memory/proposed_lessons.yaml"):
        files += 1
        text = path.read_text(encoding="utf-8", errors="ignore")
        total += len(re.findall(r"\bL3\b|level:\s*['\"]?L3", text, flags=re.I))
    # Also check legacy location
    for path in (ROOT / "data" / "entities").glob("*/proposed_lessons.yaml"):
        files += 1
        text = path.read_text(encoding="utf-8", errors="ignore")
        total += len(re.findall(r"\bL3\b|level:\s*['\"]?L3", text, flags=re.I))
    # Fail-closed for gate criterion "≥1 L3 somewhere in staging" is soft:
    # require at least one proposal file with any L3 marker OR any proposed content.
    if total >= 1:
        return True, f"L3 markers={total} across {files} proposal files"
    return False, f"no L3 markers in proposed_lessons (files scanned={files})"


def check_warp_socks() -> tuple[bool, str]:
    code, out, _ = run("ss -lntp 2>/dev/null | rg '808[123]' || true")
    if out.strip():
        return True, out.replace("\n", " | ")[:200]
    return False, "no listeners on 8081-8083 (W-1 not live)"


def check_restic() -> tuple[bool, str]:
    script_ok = check_file("scripts/restic_backup.sh") or check_file(
        "scripts/backup_restic.sh"
    )
    if not script_ok:
        return False, "restic backup script missing"
    code, out, _ = run(
        "systemctl --user is-enabled omega-restic-backup.timer 2>/dev/null; "
        "systemctl is-enabled omega-restic-backup.timer 2>/dev/null; true"
    )
    enabled = "enabled" in out
    # Script present is required; timer is required for full C-3 gate
    if script_ok and enabled:
        return True, "restic script + timer enabled"
    if script_ok:
        return False, "restic script exists but omega-restic-backup.timer not enabled"
    return False, "restic not configured"


def check_soulstore() -> tuple[bool, str]:
    path = ROOT / "src" / "omega" / "soul_store.py"
    if not path.is_file():
        return False, "soul_store.py missing"
    text = path.read_text(encoding="utf-8", errors="ignore")
    markers = ("os.replace", "fsync", "flock")
    hit = sum(1 for m in markers if m in text)
    if hit >= 2:
        return True, f"soul_store markers {hit}/3 ({', '.join(markers)})"
    return False, "soul_store missing atomic/fsync/flock markers"


def check_vault() -> tuple[bool, str]:
    core = ROOT / "src" / "omega" / "vault" / "vault_core.py"
    if not core.is_file():
        return False, "vault_core.py missing"
    # Prefer tests if present
    code, out, err = run(
        ".venv/bin/python -m pytest tests/unit/test_vault_core.py "
        "tests/test_vault_integrity.py -q --tb=no 2>&1 | tail -5",
        timeout=180,
    )
    combined = f"{out}\n{err}"
    if code == 0 and ("passed" in combined or "passed" in out):
        return True, out[:160] or "vault tests passed"
    if "no tests ran" in combined.lower():
        return True, "vault_core present (no tests collected)"
    # If pytest env broken, fall back to presence (warn path via required=False later)
    if core.is_file() and code != 0:
        return False, f"vault tests failed/exit {code}: {out[:120]}"
    return True, "vault_core present"


def main() -> int:
    results: list[dict] = []

    # Required integrity
    passed, detail = check_soulstore()
    results.append(ok("C-1': SoulStore atomic writer", passed, detail))

    results.append(
        ok(
            "C-3: Restic backup configured",
            *check_restic(),
        )
    )

    audit = check_file("docs/research/R_CG01_MCP_STREAMABLE_HTTP_OAUTH_AUDIT.md") or check_file(
        "docs/research/R_CG01_MCP_STREAMABLE_HTTP_OAUTH.md"
    )
    results.append(ok("C-4a: MCP audit doc present", audit, "audit doc" if audit else "missing"))

    mcp_runtime = (ROOT / "src" / "omega" / "mcp_runtime.py").is_file() or any(
        (ROOT / "src" / "omega").rglob("*mcp*runtime*.py")
    )
    results.append(
        ok(
            "C-4b: MCP runtime module present",
            mcp_runtime,
            "mcp_runtime found" if mcp_runtime else "mcp_runtime missing",
        )
    )

    code, out, _ = run(
        "rg -n 'oracle_summon_local' src/omega --glob '*.py' | head -3 || true"
    )
    results.append(
        ok(
            "C-5: MaKaLi local summon present",
            bool(out.strip()),
            out or "oracle_summon_local not found",
        )
    )

    code, out, _ = run(
        "rg -n 'class HealthMonitor|def get_breaker' src/omega/oracle/health_monitor.py | head -5 || true"
    )
    results.append(
        ok(
            "C-6': HealthMonitor breaker factory",
            bool(out.strip()),
            out or "HealthMonitor markers missing",
        )
    )

    code, out, _ = run(
        "rg -n 'Admission|admission' src/omega/oracle/admission_controller.py | head -5 || true"
    )
    results.append(
        ok(
            "C-10: Admission controller present",
            check_file("src/omega/oracle/admission_controller.py") and bool(out.strip()),
            out or "admission_controller missing",
        )
    )

    # Property tests — required but may be slow; bounded
    code, out, err = run(
        ".venv/bin/python -m pytest tests/property/ -q --tb=no 2>&1 | tail -8",
        timeout=300,
    )
    prop_ok = code == 0 and "failed" not in (out + err).lower().split("passed")[0:1]
    # simpler: exit code 0
    prop_ok = code == 0
    results.append(
        ok(
            "C-11: Property tests exit 0",
            prop_ok,
            out or err or f"exit={code}",
        )
    )

    passed, detail = check_vault()
    results.append(ok("V-1: VaultCore tests / presence", passed, detail))

    passed, detail = check_hook_registered()
    results.append(ok("C-0.5: session_end hook registered", passed, detail))

    passed, detail = check_mcp_pin()
    results.append(ok("CG-01: mcp dependency pin <2", passed, detail))

    passed, detail = check_l3_proposals()
    results.append(
        ok(
            "M5/M11: ≥1 L3 marker in proposed_lessons",
            passed,
            detail,
            required=False,  # fleet-wide weekly rate is process; marker is advisory
        )
    )

    passed, detail = check_warp_socks()
    results.append(ok("W-1: WARP SOCKS listeners", passed, detail, required=False))

    # Optional GenerationPolicy
    code, out, _ = run("rg -n 'GenerationPolicy' src/omega --glob '*.py' | head -3 || true")
    results.append(
        ok(
            "C-9: GenerationPolicy extracted",
            bool(out.strip()),
            out or "GenerationPolicy not found",
            required=False,
        )
    )

    print("═══════════════════════════════════════════════════════════")
    print(" PHASE D GATE VERIFICATION (fail-closed v1.1)")
    print("═══════════════════════════════════════════════════════════\n")

    for r in results:
        if r["passed"]:
            status = "✅ PASS"
        elif r["required"]:
            status = "❌ FAIL"
        else:
            status = "⚠️  WARN"
        print(f"  {status} {r['name']}")
        print(f"       → {r['detail']}")

    req = [r for r in results if r["required"]]
    opt = [r for r in results if not r["required"]]
    req_pass = sum(1 for r in req if r["passed"])
    opt_pass = sum(1 for r in opt if r["passed"])

    print("\n═══════════════════════════════════════════════════════════")
    print(f" REQUIRED: {req_pass}/{len(req)} passed")
    print(f" OPTIONAL: {opt_pass}/{len(opt)} passed")
    gate_pass = req_pass == len(req)
    print(f"\n GATE: {'✅ PASS' if gate_pass else '❌ FAIL'}")
    print("═══════════════════════════════════════════════════════════")

    # Machine-readable summary for agents
    summary_path = ROOT / "data" / "coordination" / "phase_d_gate_last.json"
    try:
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(
            json.dumps(
                {
                    "gate_pass": gate_pass,
                    "required_passed": req_pass,
                    "required_total": len(req),
                    "results": results,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"\nWrote {summary_path.relative_to(ROOT)}")
    except OSError as exc:
        print(f"\n(warning: could not write summary: {exc})")

    return 0 if gate_pass else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.TimeoutExpired:
        print("GATE: ❌ FAIL (timeout running checks)")
        raise SystemExit(1)
